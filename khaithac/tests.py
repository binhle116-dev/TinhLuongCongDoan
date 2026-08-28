import datetime as dt
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from core.models import Employee, PostOffice, UserProfile
from khaithac import views as khaithac_views
from khaithac.models import (
    KhaiThacImportBatch,
    KhaiThacPriceCard,
    KhaiThacQualityCoefficient,
    KhaiThacRawProduction,
    KhaiThacServiceMapping,
    KhaiThacShiftAssignment,
)
from khaithac.services.employee_pay import compute_employee_shares
from khaithac.services.pricing import compute_fund_breakdown, get_unit_price, load_price_cards


class FundBreakdownTests(TestCase):
    """Kiem tra cong thuc Quy tien luong = Sum(San luong x Don gia theo
    Nhom dich vu), bao gom truong hop don gia thay doi giua thang (VB1054
    -> VB1182) va truong hop Loai chua duoc anh xa (KT1)."""

    def setUp(self):
        self.po = PostOffice.objects.create(code="530100", name="KTC1 Hue 1")
        self.batch = KhaiThacImportBatch.objects.create(
            post_office=self.po, production_date=dt.date(2026, 3, 15)
        )
        KhaiThacServiceMapping.objects.create(loai_raw="E_TN", nhom_dich_vu=KhaiThacServiceMapping.NHOM_EMS)
        KhaiThacServiceMapping.objects.create(loai_raw="KT1", nhom_dich_vu=None)
        KhaiThacPriceCard.objects.create(
            nhom_dich_vu=KhaiThacServiceMapping.NHOM_EMS, unit_price=Decimal("300"),
            effective_from=dt.date(2026, 1, 1), effective_to=dt.date(2026, 2, 28),
        )
        KhaiThacPriceCard.objects.create(
            nhom_dich_vu=KhaiThacServiceMapping.NHOM_EMS, unit_price=Decimal("317"),
            effective_from=dt.date(2026, 3, 1), effective_to=None,
        )

    def test_get_unit_price_picks_correct_period(self):
        cards = load_price_cards()
        self.assertEqual(get_unit_price(cards, "EMS", dt.date(2026, 2, 15)), Decimal("300"))
        self.assertEqual(get_unit_price(cards, "EMS", dt.date(2026, 3, 15)), Decimal("317"))

    def test_fund_uses_mapped_price_and_excludes_unmapped(self):
        KhaiThacRawProduction.objects.create(
            import_batch=self.batch, post_office=self.po, production_date=dt.date(2026, 3, 15),
            ca="CA1", loai_raw="E_TN", weight_tier="<=2kg", so_luong=100,
        )
        KhaiThacRawProduction.objects.create(
            import_batch=self.batch, post_office=self.po, production_date=dt.date(2026, 3, 15),
            ca="CA2", loai_raw="KT1", weight_tier="<=2kg", so_luong=50,
        )
        result = compute_fund_breakdown(self.po, 2026, 3)
        self.assertEqual(result["tong_quy_tien_luong"], Decimal("31700"))  # 100 x 317
        self.assertEqual(result["tong_san_luong_tinh_tien"], 100)
        self.assertEqual(result["unmapped_loai"], {"KT1": 50})
        self.assertEqual(result["by_nhom_thang"]["EMS"]["so_luong"], 100)

    def test_fund_sums_multiple_weight_tiers_into_one_loai(self):
        KhaiThacRawProduction.objects.create(
            import_batch=self.batch, post_office=self.po, production_date=dt.date(2026, 3, 15),
            ca="CA1", loai_raw="E_TN", weight_tier="<=2kg", so_luong=100,
        )
        KhaiThacRawProduction.objects.create(
            import_batch=self.batch, post_office=self.po, production_date=dt.date(2026, 3, 15),
            ca="CA1", loai_raw="E_TN", weight_tier=">2kg", so_luong=20,
        )
        result = compute_fund_breakdown(self.po, 2026, 3)
        self.assertEqual(result["tong_san_luong_tinh_tien"], 120)
        self.assertEqual(result["tong_quy_tien_luong"], Decimal("38040"))  # 120 x 317


class EmployeeShareTests(TestCase):
    """Kiem tra cong thuc chia Quy tien luong cho tung nhan vien theo He so
    ca (VB1054 muc 1.3): Don gia binh quan = Quy / Tong he so; Tien luong_i
    = Don gia binh quan x He so_i x He so chat luong_i."""

    def setUp(self):
        self.po = PostOffice.objects.create(code="530100", name="KTC1 Hue 1")
        self.emp_a = Employee.objects.create(hrm_code="A1", full_name="NGUYEN VAN A", post_office=self.po)
        self.emp_b = Employee.objects.create(hrm_code="B1", full_name="TRAN VAN B", post_office=self.po)

    def test_split_proportional_to_he_so(self):
        KhaiThacShiftAssignment.objects.create(
            employee=self.emp_a, raw_name="Nguyen Van A", work_date=dt.date(2026, 7, 1),
            cong_viec="TRUONG CA", ca="CA1", he_so=Decimal("1.2"),
        )
        KhaiThacShiftAssignment.objects.create(
            employee=self.emp_b, raw_name="Tran Van B", work_date=dt.date(2026, 7, 1),
            cong_viec="KTV", ca="CA1", he_so=Decimal("1.0"),
        )
        shares = compute_employee_shares(self.po, 2026, 7, Decimal("2200"))
        # tong he so = 2.2 -> don gia binh quan = 1000/1 he so
        self.assertEqual(shares["don_gia_binh_quan"], Decimal("1000"))
        by_emp = {row["employee_id"]: row for row in shares["per_employee"]}
        self.assertEqual(by_emp[self.emp_a.id]["tien_luong"], Decimal("1200"))
        self.assertEqual(by_emp[self.emp_b.id]["tien_luong"], Decimal("1000"))

    def test_quality_coefficient_overrides_default(self):
        KhaiThacShiftAssignment.objects.create(
            employee=self.emp_a, raw_name="Nguyen Van A", work_date=dt.date(2026, 7, 1),
            cong_viec="KTV", ca="CA1", he_so=Decimal("1.0"),
        )
        KhaiThacQualityCoefficient.objects.create(
            employee=self.emp_a, year=2026, month=7, he_so=KhaiThacQualityCoefficient.THANG_TOT,
        )
        shares = compute_employee_shares(self.po, 2026, 7, Decimal("1000"))
        row = shares["per_employee"][0]
        self.assertEqual(row["tien_luong"], Decimal("1100.00"))  # 1000 x 1.0 x 1.1

    def test_unmatched_name_counted_in_total_but_has_no_payee(self):
        KhaiThacShiftAssignment.objects.create(
            employee=None, raw_name="Nguoi La", work_date=dt.date(2026, 7, 1),
            cong_viec="GSS", ca="", he_so=Decimal("0.4"),
        )
        KhaiThacShiftAssignment.objects.create(
            employee=self.emp_a, raw_name="Nguyen Van A", work_date=dt.date(2026, 7, 1),
            cong_viec="KTV", ca="CA1", he_so=Decimal("1.0"),
        )
        shares = compute_employee_shares(self.po, 2026, 7, Decimal("1400"))
        self.assertEqual(shares["tong_he_so_toan_don_vi"], Decimal("1.4"))
        self.assertEqual(shares["he_so_chua_gan"], Decimal("0.4"))
        self.assertEqual(len(shares["per_employee"]), 1)


class DashboardDisplayHelperTests(TestCase):
    """Ham tinh toan chi phuc vu hien thi (ty trong nhom dich vu, tong hop
    theo ngay/ca cho bang) - khong dong den cong thuc quy tien luong that
    trong pricing.py."""

    def test_nhom_breakdown_shares_sum_to_100_percent(self):
        result = {
            "tong_san_luong_tinh_tien": 150,
            "tong_quy_tien_luong": Decimal("1500"),
            "by_nhom_thang": {
                "EMS": {"so_luong": 100, "thanh_tien": Decimal("1000")},
                "BUU_KIEN": {"so_luong": 50, "thanh_tien": Decimal("500")},
            },
        }
        rows = khaithac_views._build_nhom_breakdown(result)
        total_ty_trong_tien = sum((r["ty_trong_tien"] for r in rows), Decimal("0"))
        self.assertEqual(total_ty_trong_tien, Decimal("100"))
        self.assertEqual(rows[0]["code"], "EMS")  # thanh_tien cao hon -> dung dau

    def test_daily_rows_totals_match_sum_of_days(self):
        result = {
            "by_ngay": {
                dt.date(2026, 7, 1): {
                    "ca": {"CA1": {"so_luong": 10, "thanh_tien": Decimal("100")}},
                    "so_luong": 10, "thanh_tien": Decimal("100"),
                },
                dt.date(2026, 7, 2): {
                    "ca": {"CA2": {"so_luong": 5, "thanh_tien": Decimal("50")}},
                    "so_luong": 5, "thanh_tien": Decimal("50"),
                },
            }
        }
        rows, totals = khaithac_views._build_daily_rows(result)
        self.assertEqual(len(rows), 2)
        self.assertEqual(totals["so_luong"], 15)
        self.assertEqual(totals["thanh_tien"], Decimal("150"))
        self.assertEqual(totals["ca1"]["so_luong"], 10)
        self.assertEqual(totals["ca2"]["so_luong"], 5)
        # Ngay khong co ca nao trong 3 ca van tra ve 0, khong loi KeyError.
        self.assertEqual(rows[0]["ca"]["CA3"]["so_luong"], 0)

    def test_daily_rows_empty_when_no_data(self):
        rows, totals = khaithac_views._build_daily_rows({"by_ngay": {}})
        self.assertEqual(rows, [])
        self.assertEqual(totals["so_luong"], 0)


class DashboardViewTests(TestCase):
    """Kiem tra o muc view: trang khong crash, ky truoc dung de so sanh
    khi co du lieu that, va khong hien chi tiet ky thuat cho nguoi khong
    phai Admin."""

    def setUp(self):
        self.po = PostOffice.objects.create(code="530100", name="KTC1 Hue 1")
        KhaiThacServiceMapping.objects.create(loai_raw="E_TN", nhom_dich_vu=KhaiThacServiceMapping.NHOM_EMS)
        KhaiThacPriceCard.objects.create(
            nhom_dich_vu=KhaiThacServiceMapping.NHOM_EMS, unit_price=Decimal("300"),
            effective_from=dt.date(2026, 1, 1), effective_to=None,
        )
        for month, so_luong in [(6, 50), (7, 100)]:
            batch = KhaiThacImportBatch.objects.create(
                post_office=self.po, production_date=dt.date(2026, month, 15)
            )
            KhaiThacRawProduction.objects.create(
                import_batch=batch, post_office=self.po, production_date=dt.date(2026, month, 15),
                ca="CA1", loai_raw="E_TN", weight_tier="<=2kg", so_luong=so_luong,
            )

        self.admin_user = User.objects.create_user("kt_view_admin", password="x")
        UserProfile.objects.create(user=self.admin_user, role=UserProfile.ROLE_ADMIN)
        self.truong = User.objects.create_user("kt_view_truong", password="x")
        po_b = PostOffice.objects.create(code="B1", name="Buu cuc khac")
        UserProfile.objects.create(user=self.truong, role=UserProfile.ROLE_TRUONG_BUU_CUC, post_office=po_b)
        self.client = Client()

    def test_dashboard_computes_real_previous_month_comparison(self):
        self.client.login(username="kt_view_admin", password="x")
        resp = self.client.get(reverse("khaithac_dashboard_month", args=[2026, 7]))
        self.assertEqual(resp.status_code, 200)
        # Thang 7 (100) tang gap doi so thang 6 (50) -> +100%.
        self.assertContains(resp, "+100,0%")

    def test_dashboard_no_previous_month_shows_honest_message_not_fake_number(self):
        self.client.login(username="kt_view_admin", password="x")
        resp = self.client.get(reverse("khaithac_dashboard_month", args=[2026, 6]))
        self.assertContains(resp, "Chưa có dữ liệu tháng trước để so sánh")

    def test_technical_command_hidden_from_non_admin(self):
        self.truong.profile.post_office = self.po
        self.truong.profile.save()
        self.client.login(username="kt_view_truong", password="x")
        resp = self.client.get(reverse("khaithac_dashboard_month", args=[2026, 7]))
        self.assertNotContains(resp, "python manage.py")

    def test_export_excel_downloads_for_scoped_user(self):
        self.client.login(username="kt_view_admin", password="x")
        resp = self.client.get(reverse("khaithac_export_excel", args=[2026, 7]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

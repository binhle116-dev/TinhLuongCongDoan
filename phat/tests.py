from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from core.models import Employee, PostOffice, UserProfile
from phat import views as phat_views
from phat.models import EmployeeMonthlyPay, ImportBatch, MonthlyPayrollRun, RawDailyProduction
from phat.services.importer import import_sanluong_chitiet

SAMPLE_FILE = Path(settings.SANLUONG_PHAT_DIR) / "SanLuongChiTiet_26082026.xlsx"


class PayrollDetailViewTests(TestCase):
    """Bao ve khoi loi that da tim thay: payroll_detail() tung crash cho
    Truong buu cuc (khong phai Admin/superuser) vi office_choices dung
    scope_queryset() sai field_name tren chinh queryset PostOffice."""

    def setUp(self):
        self.po_a = PostOffice.objects.create(code="A1", name="Buu cuc A")
        self.truong_a = User.objects.create_user("payroll_truong_a", password="x")
        UserProfile.objects.create(
            user=self.truong_a, role=UserProfile.ROLE_TRUONG_BUU_CUC, post_office=self.po_a
        )
        self.client = Client()

    def test_truong_buu_cuc_can_view_payroll_detail_without_crashing(self):
        self.client.login(username="payroll_truong_a", password="x")
        resp = self.client.get(reverse("payroll_detail", args=[2026, 1]))
        self.assertEqual(resp.status_code, 200)
        # Chi thay dung 1 lua chon (buu cuc cua chinh minh), khong thay BC khac.
        self.assertContains(resp, "A1")


class PayrollDashboardHelperTests(TestCase):
    """Cac ham tinh toan phuc vu giao dien Luong (KPI, ty trong theo buu
    cuc, so sanh ky truoc that) - khong dong den cong thuc tinh
    EmployeeMonthlyPay that su trong services/pricing.py."""

    def setUp(self):
        self.po_a = PostOffice.objects.create(code="PA1", name="Buu cuc A")
        self.po_b = PostOffice.objects.create(code="PB1", name="Buu cuc B")
        self.emp_a = Employee.objects.create(hrm_code="PH_A", full_name="Nhan vien A", post_office=self.po_a)
        self.emp_b = Employee.objects.create(hrm_code="PH_B", full_name="Nhan vien B", post_office=self.po_b)
        self.admin_user = User.objects.create_user("ph_dash_admin", password="x")
        UserProfile.objects.create(user=self.admin_user, role=UserProfile.ROLE_ADMIN)
        self.client = Client()

    def _make_run(self, year, month):
        return MonthlyPayrollRun.objects.create(year=year, month=month)

    def test_totals_for_scope_sums_across_offices(self):
        run = self._make_run(2026, 8)
        EmployeeMonthlyPay.objects.create(
            run=run, employee=self.emp_a, piece_rate_amount=Decimal("1000"),
            allowance_amount=Decimal("100"), total_amount=Decimal("1100"),
        )
        EmployeeMonthlyPay.objects.create(
            run=run, employee=self.emp_b, piece_rate_amount=Decimal("2000"),
            allowance_amount=Decimal("0"), total_amount=Decimal("2000"),
        )
        totals = phat_views._totals_for_scope(self.admin_user, 2026, 8, "")
        self.assertEqual(totals["so_lao_dong"], 2)
        self.assertEqual(totals["total"], Decimal("3100"))

    def test_totals_for_scope_respects_office_filter(self):
        run = self._make_run(2026, 8)
        EmployeeMonthlyPay.objects.create(
            run=run, employee=self.emp_a, piece_rate_amount=Decimal("1000"),
            allowance_amount=Decimal("0"), total_amount=Decimal("1000"),
        )
        EmployeeMonthlyPay.objects.create(
            run=run, employee=self.emp_b, piece_rate_amount=Decimal("2000"),
            allowance_amount=Decimal("0"), total_amount=Decimal("2000"),
        )
        totals = phat_views._totals_for_scope(self.admin_user, 2026, 8, self.po_a.code)
        self.assertEqual(totals["so_lao_dong"], 1)
        self.assertEqual(totals["total"], Decimal("1000"))

    def test_office_shares_sum_to_100_percent(self):
        by_office = [
            {"total": Decimal("300")},
            {"total": Decimal("700")},
        ]
        phat_views._add_office_shares_and_colors(by_office, Decimal("1000"))
        total_share = sum((r["ty_trong"] for r in by_office), Decimal("0"))
        self.assertEqual(total_share, Decimal("100"))
        self.assertEqual(by_office[0]["color"], "#2f7de1")

    def test_build_period_options_only_lists_real_runs(self):
        self._make_run(2026, 8)
        self._make_run(2026, 6)
        options = phat_views._build_period_options()
        self.assertEqual(options, [(2026, 8, "Tháng 08/2026"), (2026, 6, "Tháng 06/2026")])

    def test_dashboard_shows_real_previous_month_comparison(self):
        run_jun = self._make_run(2026, 6)
        EmployeeMonthlyPay.objects.create(
            run=run_jun, employee=self.emp_a, piece_rate_amount=Decimal("1000"),
            allowance_amount=Decimal("0"), total_amount=Decimal("1000"),
        )
        run_jul = self._make_run(2026, 7)
        EmployeeMonthlyPay.objects.create(
            run=run_jul, employee=self.emp_a, piece_rate_amount=Decimal("2000"),
            allowance_amount=Decimal("0"), total_amount=Decimal("2000"),
        )
        self.client.login(username="ph_dash_admin", password="x")
        resp = self.client.get(reverse("payroll_detail", args=[2026, 7]))
        self.assertContains(resp, "+100,0%")

    def test_dashboard_no_previous_month_shows_honest_message(self):
        run = self._make_run(2026, 8)
        EmployeeMonthlyPay.objects.create(
            run=run, employee=self.emp_a, piece_rate_amount=Decimal("1000"),
            allowance_amount=Decimal("0"), total_amount=Decimal("1000"),
        )
        self.client.login(username="ph_dash_admin", password="x")
        resp = self.client.get(reverse("payroll_detail", args=[2026, 8]))
        self.assertContains(resp, "Chưa có dữ liệu tháng trước để so sánh")


class ImportSanLuongChiTietTests(TestCase):
    def test_import_real_sample_file(self):
        if not SAMPLE_FILE.exists():
            self.skipTest(f"Khong tim thay file mau {SAMPLE_FILE}")
        batch = import_sanluong_chitiet(SAMPLE_FILE)
        self.assertEqual(batch.row_count, 6706)
        self.assertEqual(RawDailyProduction.objects.filter(import_batch=batch).count(), 6706)

    def test_reimport_same_day_does_not_duplicate(self):
        if not SAMPLE_FILE.exists():
            self.skipTest(f"Khong tim thay file mau {SAMPLE_FILE}")
        import_sanluong_chitiet(SAMPLE_FILE)
        import_sanluong_chitiet(SAMPLE_FILE)
        self.assertEqual(ImportBatch.objects.filter(production_date="2026-08-26").count(), 1)
        self.assertEqual(RawDailyProduction.objects.count(), 6706)

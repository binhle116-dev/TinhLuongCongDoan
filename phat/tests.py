from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from core.models import Employee, PostOffice, UserProfile
from phat.models import ImportBatch, RawDailyProduction
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

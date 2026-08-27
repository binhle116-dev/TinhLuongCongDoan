from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from core.models import Employee, PostOffice, UserProfile
from phat.models import ImportBatch, RawDailyProduction
from phat.services.importer import import_sanluong_chitiet

SAMPLE_FILE = Path(settings.SANLUONG_PHAT_DIR) / "SanLuongChiTiet_26082026.xlsx"


class EmployeeScopingViewTests(TestCase):
    """Kiem tra o muc view (khong chi o muc queryset) - mo phong dung
    tinh huong that: 2 Truong buu cuc dang nhap tu 2 tai khoan khac nhau."""

    def setUp(self):
        self.po_a = PostOffice.objects.create(code="A1", name="Buu cuc A")
        self.po_b = PostOffice.objects.create(code="B1", name="Buu cuc B")
        self.emp_a = Employee.objects.create(hrm_code="HRM_A", full_name="Nhan vien A", post_office=self.po_a)
        self.emp_b = Employee.objects.create(hrm_code="HRM_B", full_name="Nhan vien B", post_office=self.po_b)

        self.truong_a = User.objects.create_user("view_truong_a", password="x")
        UserProfile.objects.create(
            user=self.truong_a, role=UserProfile.ROLE_TRUONG_BUU_CUC, post_office=self.po_a
        )
        self.client = Client()

    def test_employee_list_only_shows_own_post_office(self):
        self.client.login(username="view_truong_a", password="x")
        resp = self.client.get(reverse("employee_list"))
        self.assertContains(resp, "Nhan vien A")
        self.assertNotContains(resp, "Nhan vien B")

    def test_cannot_edit_other_post_office_employee(self):
        self.client.login(username="view_truong_a", password="x")
        resp = self.client.get(reverse("employee_edit", args=[self.emp_b.pk]))
        self.assertEqual(resp.status_code, 404)

    def test_can_edit_own_post_office_employee(self):
        self.client.login(username="view_truong_a", password="x")
        resp = self.client.get(reverse("employee_edit", args=[self.emp_a.pk]))
        self.assertEqual(resp.status_code, 200)

    def test_anonymous_redirected_to_login(self):
        resp = self.client.get(reverse("employee_list"))
        self.assertEqual(resp.status_code, 302)


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

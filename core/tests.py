from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from core.models import Employee, PostOffice, UserProfile
from core.permissions import scope_post_office_choices, scope_queryset


class ScopeQuerysetTests(TestCase):
    """Uu tien cao nhat: dam bao 1 Truong buu cuc khong bao gio thay/sua
    duoc du lieu cua buu cuc khac. Day la co che duy nhat dung o moi view
    lien quan den du lieu theo buu cuc."""

    def setUp(self):
        self.po_a = PostOffice.objects.create(code="A1", name="Buu cuc A")
        self.po_b = PostOffice.objects.create(code="B1", name="Buu cuc B")
        self.emp_a = Employee.objects.create(hrm_code="HRM_A", full_name="Nhan vien A", post_office=self.po_a)
        self.emp_b = Employee.objects.create(hrm_code="HRM_B", full_name="Nhan vien B", post_office=self.po_b)

        self.truong_a = User.objects.create_user("truong_a", password="x")
        UserProfile.objects.create(
            user=self.truong_a, role=UserProfile.ROLE_TRUONG_BUU_CUC, post_office=self.po_a
        )

        self.admin_user = User.objects.create_user("admin_user", password="x")
        UserProfile.objects.create(user=self.admin_user, role=UserProfile.ROLE_ADMIN)

        self.superuser = User.objects.create_superuser("root", password="x")

    def test_truong_buu_cuc_only_sees_own_post_office(self):
        qs = scope_queryset(Employee.objects.all(), self.truong_a)
        self.assertQuerySetEqual(qs, [self.emp_a], transform=lambda e: e)
        self.assertNotIn(self.emp_b, qs)

    def test_admin_sees_everything(self):
        qs = scope_queryset(Employee.objects.all(), self.admin_user)
        self.assertEqual(qs.count(), 2)

    def test_superuser_sees_everything(self):
        qs = scope_queryset(Employee.objects.all(), self.superuser)
        self.assertEqual(qs.count(), 2)

    def test_user_without_profile_sees_everything(self):
        # Truong hop hiem (chua gan profile) - mac dinh khong gioi han, de
        # tranh loi che chan nham, nhung day khong phai truong hop du dung
        # thuc te (moi user thuc phai co UserProfile khi tao).
        bare_user = User.objects.create_user("bare", password="x")
        qs = scope_queryset(Employee.objects.all(), bare_user)
        self.assertEqual(qs.count(), 2)

    def test_scope_post_office_choices_for_truong_buu_cuc(self):
        # Loi that da tim thay: scope_queryset(PostOffice.objects.all(), user)
        # voi field_name mac dinh "post_office" crash vi PostOffice khong co
        # truong do tro ve chinh no - can ham rieng loc theo pk.
        qs = scope_post_office_choices(self.truong_a)
        self.assertEqual(list(qs), [self.po_a])

    def test_scope_post_office_choices_for_admin_sees_all(self):
        qs = scope_post_office_choices(self.admin_user)
        self.assertEqual(qs.count(), 2)


class EmployeeScopingViewTests(TestCase):
    """Kiem tra o muc view (khong chi o muc queryset) - mo phong dung
    tinh huong that: 2 Truong buu cuc dang nhap tu 2 tai khoan khac nhau.
    Nhan vien/Tong quan la module rieng (tach khoi Cong doan Phat), dung
    chung cho moi cong doan."""

    def setUp(self):
        self.po_a = PostOffice.objects.create(code="VIEW_A1", name="Buu cuc A")
        self.po_b = PostOffice.objects.create(code="VIEW_B1", name="Buu cuc B")
        self.emp_a = Employee.objects.create(hrm_code="VIEW_HRM_A", full_name="Nhan vien A", post_office=self.po_a)
        self.emp_b = Employee.objects.create(hrm_code="VIEW_HRM_B", full_name="Nhan vien B", post_office=self.po_b)

        self.truong_view_a = User.objects.create_user("view_truong_a", password="x")
        UserProfile.objects.create(
            user=self.truong_view_a, role=UserProfile.ROLE_TRUONG_BUU_CUC, post_office=self.po_a
        )
        self.admin_view = User.objects.create_user("view_admin", password="x")
        UserProfile.objects.create(user=self.admin_view, role=UserProfile.ROLE_ADMIN)
        self.client = Client()

    def test_admin_employee_list_defaults_to_one_office_grouped(self):
        # Yeu cau PO: gom theo tung buu cuc, chi hien lao dong thuoc buu
        # cuc dang chon - khong con tron het cac buu cuc vao 1 danh sach.
        self.client.login(username="view_admin", password="x")
        resp = self.client.get(reverse("employee_list"))
        self.assertContains(resp, "Nhan vien A")
        self.assertNotContains(resp, "Nhan vien B")

    def test_admin_employee_list_switches_office_via_bc_param(self):
        self.client.login(username="view_admin", password="x")
        resp = self.client.get(reverse("employee_list"), {"bc": self.po_b.code})
        self.assertContains(resp, "Nhan vien B")
        self.assertNotContains(resp, "Nhan vien A")

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

    def test_dashboard_loads_for_truong_buu_cuc(self):
        self.client.login(username="view_truong_a", password="x")
        resp = self.client.get(reverse("dashboard"))
        self.assertEqual(resp.status_code, 200)

    def test_dashboard_loads_for_anonymous_redirects_to_login(self):
        resp = self.client.get(reverse("dashboard"))
        self.assertEqual(resp.status_code, 302)

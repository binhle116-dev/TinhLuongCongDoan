from django.contrib.auth.models import User
from django.test import TestCase

from core.models import Employee, PostOffice, UserProfile
from core.permissions import scope_queryset


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

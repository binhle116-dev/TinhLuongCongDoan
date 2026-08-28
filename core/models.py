from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    """Mixin dung chung cho core va cac module cong doan sau nay."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    class Meta:
        abstract = True


class PostOffice(TimeStampedModel):
    code = models.CharField("Ma buu cuc", max_length=20, unique=True)
    name = models.CharField("Ten buu cuc", max_length=255)
    area = models.CharField("Khu vuc", max_length=255, blank=True)
    is_active = models.BooleanField("Dang hoat dong", default=True)

    class Meta:
        verbose_name = "Buu cuc"
        verbose_name_plural = "Buu cuc"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class PositionCatalog(models.Model):
    """Danh muc chuc danh chinh thuc (ma + ten), dung lam droplist khi
    sua nhan vien - thay cho nhap tu do. Sua/them qua trang quan tri."""

    code = models.CharField("Ma chuc danh", max_length=20, unique=True)
    name = models.CharField("Ten chuc danh", max_length=255)

    class Meta:
        verbose_name = "Chuc danh"
        verbose_name_plural = "Danh muc chuc danh"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Employee(TimeStampedModel):
    CONTRACT_HDLD = "HDLD"
    CONTRACT_LDTK = "LDTK"
    CONTRACT_CHOICES = [
        (CONTRACT_HDLD, "HDLD - huong Tien luong"),
        (CONTRACT_LDTK, "LDTK - huong Thu lao"),
    ]

    hrm_code = models.CharField("Ma HRM", max_length=20, unique=True)
    postman_code = models.CharField(
        "Ma buu ta (POSTMAN_CODE)", max_length=20, blank=True, db_index=True,
        help_text="Ma dung trong du lieu tho BatchFile/SanLuongChiTiet, khac Ma HRM.",
    )
    full_name = models.CharField("Ho va ten", max_length=255)
    post_office = models.ForeignKey(
        PostOffice, verbose_name="Buu cuc", on_delete=models.PROTECT, related_name="employees"
    )
    contract_type = models.CharField(
        "Loai hop dong", max_length=10, choices=CONTRACT_CHOICES, blank=True
    )
    position = models.ForeignKey(
        PositionCatalog, verbose_name="Chuc danh", null=True, blank=True,
        on_delete=models.PROTECT, related_name="employees",
    )
    is_active = models.BooleanField("Dang lam viec", default=True)
    start_date = models.DateField("Ngay vao", null=True, blank=True)

    class Meta:
        verbose_name = "Nhan vien"
        verbose_name_plural = "Nhan vien"
        ordering = ["post_office__code", "full_name"]

    def __str__(self):
        return f"{self.hrm_code} - {self.full_name}"


class UserProfile(models.Model):
    ROLE_ADMIN = "ADMIN"
    ROLE_PHONG_BAN = "PHONG_BAN"
    ROLE_TRUONG_BUU_CUC = "TRUONG_BUU_CUC"
    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_PHONG_BAN, "Phong ban"),
        (ROLE_TRUONG_BUU_CUC, "Truong buu cuc"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    role = models.CharField("Vai tro", max_length=20, choices=ROLE_CHOICES)
    post_office = models.ForeignKey(
        PostOffice,
        verbose_name="Buu cuc phu trach",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="managers",
        help_text="Bat buoc voi vai tro Truong buu cuc, de trong voi Admin/Phong ban.",
    )

    class Meta:
        verbose_name = "Ho so nguoi dung"
        verbose_name_plural = "Ho so nguoi dung"

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    def is_truong_buu_cuc(self):
        return self.role == self.ROLE_TRUONG_BUU_CUC

from django.conf import settings
from django.db import models

from core.models import Employee, PostOffice, TimeStampedModel


# ---------------------------------------------------------------------------
# 1) Nhap du lieu tho hang ngay
# ---------------------------------------------------------------------------

class ImportBatch(TimeStampedModel):
    STATUS_OK = "OK"
    STATUS_FAILED = "FAILED"
    STATUS_CHOICES = [(STATUS_OK, "Thanh cong"), (STATUS_FAILED, "Loi")]

    source_filename = models.CharField("Ten file", max_length=255)
    production_date = models.DateField("Ngay du lieu (STATUS_DATE)", null=True, blank=True)
    row_count = models.PositiveIntegerField("So dong", default=0)
    unmatched_count = models.PositiveIntegerField("So dong chua anh xa duoc", default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_OK)
    note = models.TextField("Ghi chu", blank=True)

    class Meta:
        verbose_name = "Lan import"
        verbose_name_plural = "Lich su import"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.source_filename} ({self.production_date})"


class RawDailyProduction(models.Model):
    """1 dong = 1 buu gui trong file SanLuongChiTiet_DDMMYYYY.xlsx."""

    import_batch = models.ForeignKey(ImportBatch, on_delete=models.CASCADE, related_name="rows")
    lading_code = models.CharField("LADING_CODE", max_length=50)
    postman_code = models.CharField("POSTMAN_CODE", max_length=20, blank=True)
    route_po_code = models.CharField("ROUTE_PO_CODE", max_length=30, blank=True)
    post_office_code = models.CharField("Ma buu cuc (BatchFile)", max_length=20, blank=True)
    status_code = models.CharField("STATUS_CODE", max_length=10, blank=True)
    type_code_payroll = models.CharField("TYPE_CODE_PAYROLL", max_length=50, blank=True)
    service_name_payroll = models.CharField("SERVICE_NAME_PAYROLL", max_length=255, blank=True)
    area_code = models.CharField("AREA_CODE", max_length=10, blank=True)
    service_code = models.CharField("SERVICE_CODE", max_length=10, blank=True)
    item_type_code = models.CharField("ITEM_TYPE_CODE", max_length=10, blank=True)
    weight_gram = models.FloatField("KG (gram)", null=True, blank=True)
    quantity = models.FloatField("QUANTITY", default=0)
    status_date = models.DateField("STATUS_DATE", null=True, blank=True)

    employee = models.ForeignKey(
        Employee, null=True, blank=True, on_delete=models.SET_NULL, related_name="raw_production_rows"
    )
    service_category = models.ForeignKey(
        "ServiceCategory", null=True, blank=True, on_delete=models.SET_NULL, related_name="raw_rows"
    )

    class Meta:
        verbose_name = "Du lieu tho hang ngay"
        verbose_name_plural = "Du lieu tho hang ngay"
        indexes = [
            models.Index(fields=["postman_code"]),
            models.Index(fields=["status_date"]),
        ]

    def __str__(self):
        return self.lading_code


# ---------------------------------------------------------------------------
# 2) Bang anh xa dich vu / nhom gia (Admin tu sua qua giao dien)
# ---------------------------------------------------------------------------

class ServiceCategory(models.Model):
    """~49 loai dich vu chuan (giong bang 'Don gia XD 2026')."""

    code = models.SlugField("Ma noi bo", max_length=50, unique=True)
    name = models.CharField("Ten dich vu chuan", max_length=255)

    class Meta:
        verbose_name = "Loai dich vu chuan"
        verbose_name_plural = "Loai dich vu chuan"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ServiceMapping(models.Model):
    """Quy tac anh xa: dong RawDailyProduction khop cac dieu kien nay se
    duoc gan vao 1 ServiceCategory. De trong 1 dieu kien nghia la khong
    loc theo truong do (khop tat ca). uu tien theo 'priority' tang dan,
    dieu kien cang cu the nen dat priority cang nho (khop truoc)."""

    priority = models.PositiveIntegerField("Do uu tien (nho hon = khop truoc)", default=100)
    service_code = models.CharField("SERVICE_CODE", max_length=10, blank=True)
    type_code_payroll = models.CharField("TYPE_CODE_PAYROLL", max_length=50, blank=True)
    service_name_payroll = models.CharField("SERVICE_NAME_PAYROLL", max_length=255, blank=True)
    area_code = models.CharField("AREA_CODE", max_length=10, blank=True)
    weight_min_gram = models.FloatField("Can nang tu (gram, bao gom)", null=True, blank=True)
    weight_max_gram = models.FloatField("Can nang den (gram, bao gom)", null=True, blank=True)
    service_category = models.ForeignKey(
        ServiceCategory, on_delete=models.CASCADE, related_name="mappings"
    )
    effective_from = models.DateField("Hieu luc tu ngay", null=True, blank=True)
    effective_to = models.DateField("Hieu luc den ngay", null=True, blank=True)
    is_active = models.BooleanField("Dang ap dung", default=True)
    note = models.CharField("Ghi chu", max_length=255, blank=True)

    class Meta:
        verbose_name = "Quy tac anh xa dich vu"
        verbose_name_plural = "Bang anh xa dich vu"
        ordering = ["priority", "id"]

    def __str__(self):
        return f"[{self.priority}] {self.service_name_payroll or '*'} / {self.area_code or '*'} -> {self.service_category}"


class PriceGroup(models.Model):
    """Nhom don gia 1-12 (Nhom don gia trong bang Tuyen)."""

    code = models.PositiveSmallIntegerField("Ma nhom", unique=True)
    name = models.CharField("Ten nhom", max_length=100, blank=True)

    class Meta:
        verbose_name = "Nhom don gia"
        verbose_name_plural = "Nhom don gia"
        ordering = ["code"]

    def __str__(self):
        return self.name or f"Nhom {self.code}"


class RouteGroupMapping(models.Model):
    route_code = models.CharField("Ma tuyen (ROUTE_PO_CODE)", max_length=30)
    price_group = models.ForeignKey(PriceGroup, on_delete=models.PROTECT, related_name="routes")
    effective_from = models.DateField("Hieu luc tu ngay", null=True, blank=True)
    effective_to = models.DateField("Hieu luc den ngay", null=True, blank=True)

    class Meta:
        verbose_name = "Anh xa Tuyen -> Nhom gia"
        verbose_name_plural = "Anh xa Tuyen -> Nhom gia"
        unique_together = [("route_code", "effective_from")]

    def __str__(self):
        return f"{self.route_code} -> {self.price_group}"


class PriceCard(models.Model):
    service_category = models.ForeignKey(
        ServiceCategory, on_delete=models.CASCADE, related_name="prices"
    )
    price_group = models.ForeignKey(PriceGroup, on_delete=models.CASCADE, related_name="prices")
    unit_price = models.DecimalField("Don gia (dong)", max_digits=12, decimal_places=2)
    effective_from = models.DateField("Hieu luc tu ngay", null=True, blank=True)
    effective_to = models.DateField("Hieu luc den ngay", null=True, blank=True)

    class Meta:
        verbose_name = "Bang gia"
        verbose_name_plural = "Bang gia"
        unique_together = [("service_category", "price_group", "effective_from")]

    def __str__(self):
        return f"{self.service_category} x {self.price_group} = {self.unit_price}"


# ---------------------------------------------------------------------------
# 3) Khoan ho tro/co dinh (Truong buu cuc tu nhap cho buu cuc minh)
# ---------------------------------------------------------------------------

class AllowanceType(models.Model):
    code = models.SlugField("Ma khoan", max_length=50, unique=True)
    name = models.CharField("Ten khoan ho tro", max_length=255)
    default_unit_price = models.DecimalField(
        "Don gia mac dinh", max_digits=12, decimal_places=2, null=True, blank=True
    )
    unit_label = models.CharField("Don vi tinh", max_length=100, blank=True)
    is_active = models.BooleanField("Dang su dung", default=True)

    class Meta:
        verbose_name = "Loai khoan ho tro"
        verbose_name_plural = "Danh muc khoan ho tro"

    def __str__(self):
        return self.name


class AllowanceEntry(TimeStampedModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="allowance_entries")
    allowance_type = models.ForeignKey(AllowanceType, on_delete=models.PROTECT, related_name="entries")
    year = models.PositiveSmallIntegerField("Nam")
    month = models.PositiveSmallIntegerField("Thang")
    quantity = models.DecimalField("So luong", max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField("Don gia", max_digits=12, decimal_places=2, null=True, blank=True)
    amount = models.DecimalField("Thanh tien", max_digits=14, decimal_places=2)
    note = models.CharField("Ghi chu", max_length=255, blank=True)

    class Meta:
        verbose_name = "Khoan ho tro da nhap"
        verbose_name_plural = "Khoan ho tro da nhap"
        ordering = ["-year", "-month", "employee__full_name"]

    def save(self, *args, **kwargs):
        price = self.unit_price if self.unit_price is not None else self.allowance_type.default_unit_price
        if price is not None:
            self.amount = price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee} - {self.allowance_type} - {self.month}/{self.year}"


# ---------------------------------------------------------------------------
# 4) Chot luong hang thang
# ---------------------------------------------------------------------------

class MonthlyPayrollRun(TimeStampedModel):
    STATUS_DRAFT = "DRAFT"
    STATUS_PENDING = "PENDING_CONFIRMATION"
    STATUS_FINAL = "FINALIZED"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Tam tinh (dang cap nhat)"),
        (STATUS_PENDING, "Cho xac nhan"),
        (STATUS_FINAL, "Da chot"),
    ]

    year = models.PositiveSmallIntegerField("Nam")
    month = models.PositiveSmallIntegerField("Thang")
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    finalized_at = models.DateTimeField(null=True, blank=True)
    finalized_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    class Meta:
        verbose_name = "Ky chot luong"
        verbose_name_plural = "Ky chot luong"
        unique_together = [("year", "month")]
        ordering = ["-year", "-month"]

    def __str__(self):
        return f"Thang {self.month}/{self.year} ({self.get_status_display()})"

    def is_finalized(self):
        return self.status == self.STATUS_FINAL


class EmployeeMonthlyPay(models.Model):
    """Ban chup ket qua cho 1 nhan vien trong 1 ky. Neu run.status =
    FINALIZED thi KHONG duoc tinh lai/ghi de nua."""

    run = models.ForeignKey(MonthlyPayrollRun, on_delete=models.CASCADE, related_name="employee_pays")
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="monthly_pays")
    piece_rate_amount = models.DecimalField("Cong theo san luong", max_digits=14, decimal_places=2, default=0)
    allowance_amount = models.DecimalField("Tong ho tro", max_digits=14, decimal_places=2, default=0)
    total_amount = models.DecimalField("Tong thu nhap", max_digits=14, decimal_places=2, default=0)
    is_provisional = models.BooleanField("Con la tam tinh (chua xac minh)", default=True)
    computed_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Luong thang theo lao dong"
        verbose_name_plural = "Luong thang theo lao dong"
        unique_together = [("run", "employee")]

    def __str__(self):
        return f"{self.employee} - {self.run}: {self.total_amount}"


class EmployeeMonthlyPayDetail(models.Model):
    employee_pay = models.ForeignKey(
        EmployeeMonthlyPay, on_delete=models.CASCADE, related_name="details"
    )
    service_category = models.ForeignKey(ServiceCategory, on_delete=models.PROTECT, related_name="+")
    quantity = models.FloatField("So luong", default=0)
    unit_price = models.DecimalField("Don gia", max_digits=12, decimal_places=2, default=0)
    amount = models.DecimalField("Thanh tien", max_digits=14, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Chi tiet luong theo dich vu"
        verbose_name_plural = "Chi tiet luong theo dich vu"


class PostOfficeConfirmation(TimeStampedModel):
    """Chua co UI trong Milestone 1 - da tao san bang de khong phai doi
    cau truc du lieu khi lam quy trinh xac nhan/chot o phase sau."""

    STATUS_PENDING = "PENDING"
    STATUS_CONFIRMED = "CONFIRMED"
    STATUS_FLAGGED = "FLAGGED"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Chua xac nhan"),
        (STATUS_CONFIRMED, "Da xac nhan"),
        (STATUS_FLAGGED, "Bao loi"),
    ]

    run = models.ForeignKey(MonthlyPayrollRun, on_delete=models.CASCADE, related_name="confirmations")
    post_office = models.ForeignKey(PostOffice, on_delete=models.CASCADE, related_name="confirmations")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_PENDING)
    comment = models.TextField("Ghi chu/bao loi", blank=True)

    class Meta:
        verbose_name = "Xac nhan cua buu cuc"
        verbose_name_plural = "Xac nhan cua buu cuc"
        unique_together = [("run", "post_office")]

    def __str__(self):
        return f"{self.post_office} - {self.run}: {self.get_status_display()}"

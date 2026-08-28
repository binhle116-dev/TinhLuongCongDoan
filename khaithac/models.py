from decimal import Decimal

from django.db import models

from core.models import Employee, PostOffice, TimeStampedModel


# ---------------------------------------------------------------------------
# 1) Nhap du lieu tho theo ca/ngay (da GROUP BY tu SQL Server BCCP, khong
#    phai tung buu gui rieng le nhu RawDailyProduction cua module Phat).
# ---------------------------------------------------------------------------

CA_CHOICES = [
    ("CA1", "Ca 1 (05:00 - 13:00)"),
    ("CA2", "Ca 2 (13:00 - 21:00)"),
    ("CA3", "Ca 3 (21:00 - 05:00)"),
]


class KhaiThacImportBatch(TimeStampedModel):
    STATUS_OK = "OK"
    STATUS_FAILED = "FAILED"
    STATUS_CHOICES = [(STATUS_OK, "Thanh cong"), (STATUS_FAILED, "Loi")]

    post_office = models.ForeignKey(
        PostOffice, on_delete=models.CASCADE, related_name="khaithac_import_batches"
    )
    production_date = models.DateField("Ngay du lieu")
    row_count = models.PositiveIntegerField("So dong (da gop nhom)", default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_OK)
    note = models.TextField("Ghi chu", blank=True)

    class Meta:
        verbose_name = "Lan import Khai thac"
        verbose_name_plural = "Lich su import Khai thac"
        unique_together = [("post_office", "production_date")]
        ordering = ["-production_date"]

    def __str__(self):
        return f"{self.post_office} - {self.production_date}"


class KhaiThacServiceMapping(models.Model):
    """Anh xa 'Loai' tho (nhu trong script SQL cua don vi: R_TN, E_TN, KT1...)
    sang 1 trong 4 'Nhom dich vu' dung de tinh don gia theo VB1054/1182.
    Nhung Loai chua co Nhom (vd KT1) se KHONG duoc tinh vao Quy tien luong
    cho toi khi duoc anh xa - tranh doan bua, giong nguyen tac da dung o
    module Phat (ServiceMapping)."""

    NHOM_EMS = "EMS"
    NHOM_GHI_SO = "GHI_SO"
    NHOM_BUU_KIEN = "BUU_KIEN"
    NHOM_PHBC = "PHBC"
    NHOM_CHOICES = [
        (NHOM_EMS, "EMS"),
        (NHOM_GHI_SO, "Ghi so (Bao dam)"),
        (NHOM_BUU_KIEN, "Buu kien"),
        (NHOM_PHBC, "Phat hanh bao chi (PHBC)"),
    ]

    loai_raw = models.CharField("Loai (theo script SQL don vi)", max_length=20, unique=True)
    nhom_dich_vu = models.CharField(
        "Nhom dich vu (VB1054/1182)", max_length=10, choices=NHOM_CHOICES, null=True, blank=True
    )
    note = models.CharField("Ghi chu", max_length=255, blank=True)

    class Meta:
        verbose_name = "Anh xa Loai -> Nhom dich vu Khai thac"
        verbose_name_plural = "Bang anh xa Khai thac"
        ordering = ["loai_raw"]

    def __str__(self):
        return f"{self.loai_raw} -> {self.nhom_dich_vu or '(chua anh xa)'}"


class KhaiThacRawProduction(models.Model):
    """1 dong = tong so luong cho 1 to hop (buu cuc, ngay, ca, loai, muc can),
    lay tu bang chuan Item/TraceItem cua phan mem BCCP qua management command
    import_khaithac_production (ket noi SQL Server truc tiep)."""

    import_batch = models.ForeignKey(
        KhaiThacImportBatch, on_delete=models.CASCADE, related_name="rows"
    )
    post_office = models.ForeignKey(
        PostOffice, on_delete=models.CASCADE, related_name="khaithac_raw_rows"
    )
    production_date = models.DateField("Ngay")
    ca = models.CharField("Ca", max_length=5, choices=CA_CHOICES)
    loai_raw = models.CharField("Loai (theo script SQL don vi)", max_length=20)
    weight_tier = models.CharField("Muc can", max_length=20, blank=True)
    so_luong = models.PositiveIntegerField("So luong")

    class Meta:
        verbose_name = "San luong Khai thac tho (theo ca/ngay)"
        verbose_name_plural = "San luong Khai thac tho (theo ca/ngay)"
        indexes = [
            models.Index(fields=["production_date"]),
            models.Index(fields=["loai_raw"]),
        ]

    def __str__(self):
        return f"{self.post_office} {self.production_date} {self.ca} {self.loai_raw}={self.so_luong}"


# ---------------------------------------------------------------------------
# 2) Don gia Khai thac (Dong/cai) - theo Nhom dich vu, co hieu luc theo thoi
#    gian vi don gia da duoc dieu chinh 1 lan trong nam 2026 (VB1182 tu
#    thang 03/2026, truoc do la VB1054 tu thang 01/2026).
# ---------------------------------------------------------------------------

class KhaiThacPriceCard(models.Model):
    nhom_dich_vu = models.CharField(
        "Nhom dich vu", max_length=10, choices=KhaiThacServiceMapping.NHOM_CHOICES
    )
    unit_price = models.DecimalField("Don gia (dong/cai)", max_digits=10, decimal_places=2)
    effective_from = models.DateField("Hieu luc tu ngay")
    effective_to = models.DateField("Hieu luc den ngay (de trong = con hieu luc)", null=True, blank=True)
    source_document = models.CharField("Van ban can cu", max_length=255, blank=True)

    class Meta:
        verbose_name = "Don gia Khai thac"
        verbose_name_plural = "Bang don gia Khai thac"
        ordering = ["nhom_dich_vu", "-effective_from"]
        unique_together = [("nhom_dich_vu", "effective_from")]

    def __str__(self):
        return f"{self.get_nhom_dich_vu_display()}: {self.unit_price}d tu {self.effective_from}"


# ---------------------------------------------------------------------------
# 3) Phan ca thuc te + he so chat luong - CAN du lieu bang cham cong/phan ca
#    thuc te tu don vi (chua co tai thoi diem tao model nay). De trong,
#    khong doan, giong nguyen tac DEC-005/DEC-009 cua module Phat.
# ---------------------------------------------------------------------------

class KhaiThacShiftAssignment(TimeStampedModel):
    """1 dong = 1 nhan vien lam 1 ca trong 1 ngay tai buu cuc Khai thac.
    He so ca theo VB1054 muc 1.3: ca chuan (8h) = 1.0, truong ca = 1.2,
    khong du 1 ca thi quy doi theo (so gio thuc te / 8) x he so tuong ung."""

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="khaithac_shifts")
    work_date = models.DateField("Ngay lam")
    ca = models.CharField("Ca", max_length=5, choices=CA_CHOICES)
    is_truong_ca = models.BooleanField("Truong ca (duoc giao nhiem vu)", default=False)
    actual_hours = models.DecimalField(
        "So gio lam thuc te", max_digits=4, decimal_places=1, default=Decimal("8.0")
    )

    class Meta:
        verbose_name = "Phan ca Khai thac"
        verbose_name_plural = "Bang phan ca Khai thac"
        unique_together = [("employee", "work_date", "ca")]
        ordering = ["-work_date", "ca"]

    def __str__(self):
        return f"{self.employee} - {self.work_date} {self.ca}"

    def he_so_ca(self) -> Decimal:
        he_so_chuan = Decimal("1.2") if self.is_truong_ca else Decimal("1.0")
        return (Decimal(self.actual_hours) / Decimal("8")) * he_so_chuan


class KhaiThacQualityCoefficient(models.Model):
    """He so chat luong thang cho tung nhan vien (VB1054 muc 1.4, Phu luc 01).
    Mac dinh 1.0 (Dat) - Truong buu cuc/Admin sua qua trang quan tri neu co
    danh gia khac trong thang."""

    THANG_TOT = Decimal("1.1")
    THANG_DAT = Decimal("1.0")
    THANG_CHUA_DAT = Decimal("0.6")
    HE_SO_CHOICES = [
        (THANG_TOT, "Tot (1.1)"),
        (THANG_DAT, "Dat (1.0)"),
        (THANG_CHUA_DAT, "Chua dat (0.6)"),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="khaithac_quality")
    year = models.PositiveSmallIntegerField("Nam")
    month = models.PositiveSmallIntegerField("Thang")
    he_so = models.DecimalField(
        "He so chat luong thang", max_digits=3, decimal_places=2,
        choices=HE_SO_CHOICES, default=THANG_DAT,
    )

    class Meta:
        verbose_name = "He so chat luong Khai thac thang"
        verbose_name_plural = "He so chat luong Khai thac thang"
        unique_together = [("employee", "year", "month")]

    def __str__(self):
        return f"{self.employee} - {self.month}/{self.year}: {self.he_so}"

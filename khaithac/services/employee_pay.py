"""Chia 'Quy tien luong thuc hien cua don vi' (xem pricing.py) cho tung
nhan vien, dung cong thuc VB1054/TB-BDHUE muc 1.3 (dien giai day du theo
cung mau voi muc 3.3/3.4 - Xu ly nghiep vu - cua chinh van ban):

    Don gia binh quan theo he so ca = Quy tien luong / Tong he so ca toan don vi (thang)
    Tien luong lao dong i = Don gia binh quan x Tong he so ca cua lao dong i (thang) x He so chat luong thang cua i

He so ca cua tung dong lay THANG DUNG tu Bang cham cong that
(KhaiThacShiftAssignment.he_so), khong tu tinh lai - vi thuc te co truong
hop khac 1.0/1.2 chuan (vd cong viec GSS = 0.4).

He so chat luong thang mac dinh 1.0 (Dat) neu Truong buu cuc/Admin chua
nhap KhaiThacQualityCoefficient rieng cho nhan vien do trong thang.
"""
from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from django.db.models import Sum

from khaithac.models import KhaiThacQualityCoefficient, KhaiThacShiftAssignment


def compute_employee_shares(post_office, year: int, month: int, quy_tien_luong: Decimal) -> dict:
    """Tra ve breakdown chia Quy tien luong cho tung nhan vien. post_office
    hien chua dung de loc (Bang phan ca chi co 1 buu cuc Khai thac), giu
    tham so de dong bo chu ky goi voi compute_fund_breakdown()."""

    shifts = KhaiThacShiftAssignment.objects.filter(
        work_date__year=year, work_date__month=month
    ).select_related("employee")

    tong_he_so_toan_don_vi = shifts.aggregate(s=Sum("he_so"))["s"] or Decimal("0")

    he_so_by_employee: dict[int, Decimal] = defaultdict(lambda: Decimal("0"))
    employee_names: dict[int, str] = {}
    he_so_chua_gan: Decimal = Decimal("0")
    for shift in shifts:
        if shift.employee_id is None:
            he_so_chua_gan += shift.he_so
            continue
        he_so_by_employee[shift.employee_id] += shift.he_so
        employee_names[shift.employee_id] = str(shift.employee)

    if tong_he_so_toan_don_vi == 0:
        return {
            "don_gia_binh_quan": Decimal("0"),
            "tong_he_so_toan_don_vi": Decimal("0"),
            "he_so_chua_gan": Decimal("0"),
            "per_employee": [],
        }

    don_gia_binh_quan = quy_tien_luong / tong_he_so_toan_don_vi

    quality_lookup = {
        q.employee_id: q.he_so
        for q in KhaiThacQualityCoefficient.objects.filter(year=year, month=month)
    }

    per_employee = []
    for employee_id, tong_he_so in he_so_by_employee.items():
        he_so_chat_luong = quality_lookup.get(employee_id, KhaiThacQualityCoefficient.THANG_DAT)
        tien_luong = don_gia_binh_quan * tong_he_so * he_so_chat_luong
        per_employee.append(
            {
                "employee_id": employee_id,
                "ten": employee_names[employee_id],
                "tong_he_so": tong_he_so,
                "he_so_chat_luong": he_so_chat_luong,
                "tien_luong": tien_luong,
            }
        )
    per_employee.sort(key=lambda x: x["tien_luong"], reverse=True)

    return {
        "don_gia_binh_quan": don_gia_binh_quan,
        "tong_he_so_toan_don_vi": tong_he_so_toan_don_vi,
        "he_so_chua_gan": he_so_chua_gan,
        "per_employee": per_employee,
    }

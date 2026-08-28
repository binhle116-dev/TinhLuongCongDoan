"""Tinh 'Quy tien luong thuc hien cua don vi' cho cong doan Khai thac, theo
VB1054/TB-BDHUE (11/3/2026) muc II.1 va VB1182/TB-BDHUE (31/3/2026, dieu
chinh don gia tu 03/2026):

    Quy tien luong = Sum( San luong khai thac (nhom dich vu) x Don gia (nhom) )

Don gia chi phan biet theo 4 Nhom dich vu (EMS/GHI_SO/BUU_KIEN/PHBC), KHONG
phan biet theo can nang hay noi tinh/lien tinh/quoc te - khac voi cach nhom
"Loai" tho luu trong KhaiThacRawProduction (R_TN/R_QT/R_COD/E_TN/...), nen
can di qua KhaiThacServiceMapping truoc khi tinh tien.

Viec chia Quy tien luong nay cho tung nhan vien theo He so ca (VB1054 muc
1.3) can du lieu Bang phan ca thuc te (KhaiThacShiftAssignment) - CHUA co,
nen ham compute_fund_breakdown() o day chi dung lai o muc "Quy tien luong
cua don vi", chua chia cho tung nguoi.
"""
from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from django.db.models import Sum

from khaithac.models import (
    KhaiThacPriceCard,
    KhaiThacRawProduction,
    KhaiThacServiceMapping,
)


def load_mapping_lookup() -> dict[str, str | None]:
    """{loai_raw: nhom_dich_vu hoac None neu chua anh xa}."""
    return {m.loai_raw: m.nhom_dich_vu for m in KhaiThacServiceMapping.objects.all()}


def load_price_cards() -> dict[str, list[KhaiThacPriceCard]]:
    """{nhom_dich_vu: [PriceCard,...]} sap xep effective_from giam dan, de
    tim don gia dung hieu luc tai 1 ngay cu the bang cach duyet tu tren xuong."""
    lookup: dict[str, list[KhaiThacPriceCard]] = defaultdict(list)
    for pc in KhaiThacPriceCard.objects.order_by("nhom_dich_vu", "-effective_from"):
        lookup[pc.nhom_dich_vu].append(pc)
    return lookup


def get_unit_price(price_cards: dict[str, list[KhaiThacPriceCard]], nhom_dich_vu: str, on_date) -> Decimal:
    for pc in price_cards.get(nhom_dich_vu, []):
        if pc.effective_from <= on_date and (pc.effective_to is None or on_date <= pc.effective_to):
            return pc.unit_price
    return Decimal("0")


def compute_fund_breakdown(post_office, year: int, month: int) -> dict:
    """Tra ve breakdown Quy tien luong Khai thac theo ngay/ca/nhom cho 1
    buu cuc trong 1 thang, cong voi danh sach Loai chua duoc anh xa (khong
    tinh vao tong) de bao cao rieng - giong /bao-cao/chua-anh-xa/ cua Phat."""
    mapping = load_mapping_lookup()
    price_cards = load_price_cards()

    rows = (
        KhaiThacRawProduction.objects.filter(
            post_office=post_office, production_date__year=year, production_date__month=month,
        )
        .values("production_date", "ca", "loai_raw")
        .annotate(tong_so_luong=Sum("so_luong"))
        .order_by("production_date", "ca", "loai_raw")
    )

    by_ngay: dict = defaultdict(lambda: {"ca": defaultdict(lambda: {"so_luong": 0, "thanh_tien": Decimal("0")}), "so_luong": 0, "thanh_tien": Decimal("0")})
    by_nhom_thang: dict = defaultdict(lambda: {"so_luong": 0, "thanh_tien": Decimal("0")})
    unmapped_loai: dict = defaultdict(int)
    tong_quy_tien_luong = Decimal("0")
    tong_san_luong_tinh_tien = 0

    for row in rows:
        ngay = row["production_date"]
        ca = row["ca"]
        loai = row["loai_raw"]
        so_luong = row["tong_so_luong"]
        nhom = mapping.get(loai)

        if not nhom:
            unmapped_loai[loai] += so_luong
            continue

        don_gia = get_unit_price(price_cards, nhom, ngay)
        thanh_tien = Decimal(so_luong) * don_gia

        by_ngay[ngay]["ca"][ca]["so_luong"] += so_luong
        by_ngay[ngay]["ca"][ca]["thanh_tien"] += thanh_tien
        by_ngay[ngay]["so_luong"] += so_luong
        by_ngay[ngay]["thanh_tien"] += thanh_tien
        by_nhom_thang[nhom]["so_luong"] += so_luong
        by_nhom_thang[nhom]["thanh_tien"] += thanh_tien
        tong_quy_tien_luong += thanh_tien
        tong_san_luong_tinh_tien += so_luong

    return {
        "by_ngay": dict(sorted(by_ngay.items())),
        "by_nhom_thang": dict(by_nhom_thang),
        "unmapped_loai": dict(unmapped_loai),
        "tong_quy_tien_luong": tong_quy_tien_luong,
        "tong_san_luong_tinh_tien": tong_san_luong_tinh_tien,
    }

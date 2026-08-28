import datetime as dt
import io
from decimal import Decimal

import openpyxl
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render

from core.models import PostOffice
from core.permissions import get_profile, user_can_access_post_office
from khaithac.models import KhaiThacImportBatch, KhaiThacRawProduction, KhaiThacServiceMapping
from khaithac.services.employee_pay import compute_employee_shares
from khaithac.services.pricing import compute_fund_breakdown

# Ten hien thi tieng Viet day du (co dau) cho man hinh - KhaiThacServiceMapping.NHOM_CHOICES
# dung cho logic/admin (gia tri khong doi), rieng nhan hien thi o day sua cho dep hon,
# khong anh huong toi ma nhom (EMS/GHI_SO/BUU_KIEN/PHBC) dung trong tinh toan.
NHOM_LABELS = {
    KhaiThacServiceMapping.NHOM_EMS: "EMS",
    KhaiThacServiceMapping.NHOM_GHI_SO: "Ghi số (Bảo đảm)",
    KhaiThacServiceMapping.NHOM_BUU_KIEN: "Bưu kiện",
    KhaiThacServiceMapping.NHOM_PHBC: "Phát hành báo chí (PHBC)",
}

NHOM_COLORS = {
    KhaiThacServiceMapping.NHOM_EMS: "#2f7de1",
    KhaiThacServiceMapping.NHOM_GHI_SO: "#0891b2",
    KhaiThacServiceMapping.NHOM_BUU_KIEN: "#7c6ff0",
    KhaiThacServiceMapping.NHOM_PHBC: "#64748b",
}


def _current_year_month():
    today = dt.date.today()
    return today.year, today.month


def _prev_year_month(year: int, month: int) -> tuple[int, int]:
    return (year - 1, 12) if month == 1 else (year, month - 1)


def _build_period_options(post_office, year: int, month: int) -> list[tuple[int, int, str]]:
    """Danh sach cac ky (nam, thang) de chon o dropdown: nhung thang THAT su
    da co du lieu san luong, cong voi ky dang xem (de van hien thi ngay ca
    khi chua co du lieu) - khong bia them cac thang trong khong co gi."""
    months = set(
        KhaiThacRawProduction.objects.filter(post_office=post_office)
        .dates("production_date", "month")
    )
    months.add(dt.date(year, month, 1))
    options = []
    for d in sorted(months, reverse=True):
        options.append((d.year, d.month, f"Tháng {d.month:02d}/{d.year}"))
    return options


def _get_khaithac_post_office(user):
    """Buu cuc Khai thac (530100) neu user duoc xem, nguoc lai None. KHONG
    dung scope_queryset(PostOffice.objects.filter(...), user) truc tiep -
    PostOffice khong co truong tu tro 'post_office' de loc qua field_name
    mac dinh cua ham do (xem core.permissions.user_can_access_post_office)."""
    try:
        post_office = PostOffice.objects.get(code="530100")
    except PostOffice.DoesNotExist:
        return None
    return post_office if user_can_access_post_office(user, post_office) else None


def _is_admin(request) -> bool:
    profile = get_profile(request.user)
    return bool(request.user.is_superuser or (profile and profile.is_admin()))


def _build_nhom_breakdown(result: dict) -> list[dict]:
    """Danh sach nhom dich vu kem ty trong san luong/quy luong + goc donut
    (cho bieu do), sap xep thanh tien giam dan. Chi tinh toan hien thi -
    khong dong den cong thuc trong pricing.py."""
    tong_sl = result["tong_san_luong_tinh_tien"] or 0
    tong_tien = result["tong_quy_tien_luong"] or Decimal("0")
    rows = []
    for nhom, v in sorted(result["by_nhom_thang"].items(), key=lambda kv: kv[1]["thanh_tien"], reverse=True):
        ty_trong_sl = (Decimal(v["so_luong"]) / tong_sl * 100) if tong_sl else Decimal("0")
        ty_trong_tien = (v["thanh_tien"] / tong_tien * 100) if tong_tien else Decimal("0")
        rows.append({
            "code": nhom,
            "label": NHOM_LABELS.get(nhom, nhom),
            "color": NHOM_COLORS.get(nhom, "#94a3b8"),
            "so_luong": v["so_luong"],
            "thanh_tien": v["thanh_tien"],
            "ty_trong_sl": ty_trong_sl,
            "ty_trong_tien": ty_trong_tien,
        })
    # Toa do SVG (stroke-dasharray/-dashoffset) cho tung lat cat donut, theo
    # ty trong tien - vong tron ban kinh 40 (chu vi = 2*pi*40 ~ 251.33).
    circumference = 2 * 3.14159265 * 40
    offset_pct = Decimal("0")
    for row in rows:
        length = float(row["ty_trong_tien"]) / 100 * circumference
        row["donut_dasharray"] = f"{length:.2f} {circumference:.2f}"
        row["donut_dashoffset"] = f"{-(float(offset_pct) / 100 * circumference):.2f}"
        offset_pct += row["ty_trong_tien"]
    return rows


def _build_daily_rows(result: dict) -> tuple[list[dict], dict]:
    """Danh sach cac ngay (co du lieu that) kem gia tri tung ca da chuan
    hoa (khong con thieu key), co/khong sanh luong = 0, va cuong do heat
    (0..1, tuong doi so voi ngay cao nhat trong ky) de to nen rat nhe."""
    by_ngay = result["by_ngay"]
    def _empty_totals():
        return {
            ma.lower(): {"so_luong": 0, "thanh_tien": Decimal("0")} for ma in ("CA1", "CA2", "CA3")
        } | {"so_luong": 0, "thanh_tien": Decimal("0")}

    if not by_ngay:
        return [], _empty_totals()

    max_so_luong_ngay = max((v["so_luong"] for v in by_ngay.values()), default=0) or 1
    today = dt.date.today()

    rows = []
    cot_tong = _empty_totals()
    for ngay, v in by_ngay.items():
        ca_data = {}
        for ma_ca in ("CA1", "CA2", "CA3"):
            c = v["ca"].get(ma_ca, {"so_luong": 0, "thanh_tien": Decimal("0")})
            ca_data[ma_ca] = c
            cot_tong[ma_ca.lower()]["so_luong"] += c["so_luong"]
            cot_tong[ma_ca.lower()]["thanh_tien"] += c["thanh_tien"]
        rows.append({
            "ngay": ngay,
            "is_today": ngay == today,
            "is_zero": v["so_luong"] == 0,
            "ca": ca_data,
            "so_luong": v["so_luong"],
            "thanh_tien": v["thanh_tien"],
            "heat": min(float(v["so_luong"]) / max_so_luong_ngay, 1.0),
        })
        cot_tong["so_luong"] += v["so_luong"]
        cot_tong["thanh_tien"] += v["thanh_tien"]
    return rows, cot_tong


@login_required
def dashboard(request, year=None, month=None):
    if year is None or month is None:
        year, month = _current_year_month()

    post_office = _get_khaithac_post_office(request.user)

    result = None
    shares = None
    nhom_breakdown = []
    daily_rows = []
    daily_totals = None
    prev_compare = None
    last_updated = None
    avg_unit_price = Decimal("0")
    so_ca_ghi_nhan = 0
    period_options = []

    if post_office:
        period_options = _build_period_options(post_office, year, month)
        result = compute_fund_breakdown(post_office, year, month)
        shares = compute_employee_shares(post_office, year, month, result["tong_quy_tien_luong"])
        nhom_breakdown = _build_nhom_breakdown(result)
        daily_rows, daily_totals = _build_daily_rows(result)
        so_ca_ghi_nhan = sum(len(v["ca"]) for v in result["by_ngay"].values())

        if result["tong_san_luong_tinh_tien"]:
            avg_unit_price = result["tong_quy_tien_luong"] / result["tong_san_luong_tinh_tien"]

        prev_year, prev_month = _prev_year_month(year, month)
        prev_result = compute_fund_breakdown(post_office, prev_year, prev_month)
        if prev_result["tong_san_luong_tinh_tien"]:  # co du lieu that ky truoc, khong bia so
            fund_delta = None
            sl_delta = None
            if prev_result["tong_quy_tien_luong"]:
                fund_delta = (result["tong_quy_tien_luong"] - prev_result["tong_quy_tien_luong"]) / prev_result["tong_quy_tien_luong"]
            if prev_result["tong_san_luong_tinh_tien"]:
                sl_delta = Decimal(result["tong_san_luong_tinh_tien"] - prev_result["tong_san_luong_tinh_tien"]) / prev_result["tong_san_luong_tinh_tien"]
            prev_compare = {
                "year": prev_year, "month": prev_month,
                "fund_delta": fund_delta, "san_luong_delta": sl_delta,
            }

        last_batch = (
            KhaiThacImportBatch.objects.filter(
                post_office=post_office, production_date__year=year, production_date__month=month,
            )
            .order_by("-created_at")
            .first()
        )
        last_updated = last_batch.created_at if last_batch else None

    context = {
        "year": year,
        "month": month,
        "post_office": post_office,
        "result": result,
        "shares": shares,
        "nhom_breakdown": nhom_breakdown,
        "daily_rows": daily_rows,
        "daily_totals": daily_totals,
        "prev_compare": prev_compare,
        "last_updated": last_updated,
        "avg_unit_price": avg_unit_price,
        "so_ngay_co_du_lieu": len(daily_rows),
        "so_ca_ghi_nhan": so_ca_ghi_nhan,
        "is_admin": _is_admin(request),
        "period_options": period_options,
        "tong_luong_da_chia": sum((r["tien_luong"] for r in shares["per_employee"]), Decimal("0")) if shares else Decimal("0"),
    }
    return render(request, "khaithac_dashboard.html", context)


@login_required
def export_excel(request, year, month):
    post_office = _get_khaithac_post_office(request.user)
    if post_office is None:
        raise PermissionDenied("Ban khong co quyen xem du lieu Khai thac.")

    result = compute_fund_breakdown(post_office, year, month)
    nhom_breakdown = _build_nhom_breakdown(result)
    daily_rows, daily_totals = _build_daily_rows(result)

    wb = openpyxl.Workbook()

    ws1 = wb.active
    ws1.title = "Theo nhom dich vu"
    ws1.append(["Nhom dich vu", "San luong", "Ty trong SL (%)", "Thanh tien", "Ty trong quy (%)"])
    for row in nhom_breakdown:
        ws1.append([
            row["label"], row["so_luong"], float(row["ty_trong_sl"]),
            float(row["thanh_tien"]), float(row["ty_trong_tien"]),
        ])
    ws1.append([
        "Tong cong", result["tong_san_luong_tinh_tien"], 100.0,
        float(result["tong_quy_tien_luong"]), 100.0,
    ])

    ws2 = wb.create_sheet("Theo ngay-ca")
    ws2.append(["Ngay", "CA1 SL", "CA1 Tien", "CA2 SL", "CA2 Tien", "CA3 SL", "CA3 Tien", "Tong SL", "Tong Tien"])
    for row in daily_rows:
        ws2.append([
            row["ngay"].strftime("%d/%m/%Y"),
            row["ca"]["CA1"]["so_luong"], float(row["ca"]["CA1"]["thanh_tien"]),
            row["ca"]["CA2"]["so_luong"], float(row["ca"]["CA2"]["thanh_tien"]),
            row["ca"]["CA3"]["so_luong"], float(row["ca"]["CA3"]["thanh_tien"]),
            row["so_luong"], float(row["thanh_tien"]),
        ])
    if daily_totals:
        ws2.append([
            "Tong toan ky",
            daily_totals["ca1"]["so_luong"], float(daily_totals["ca1"]["thanh_tien"]),
            daily_totals["ca2"]["so_luong"], float(daily_totals["ca2"]["thanh_tien"]),
            daily_totals["ca3"]["so_luong"], float(daily_totals["ca3"]["thanh_tien"]),
            daily_totals["so_luong"], float(daily_totals["thanh_tien"]),
        ])

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    response = HttpResponse(
        buffer.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="QuyTienLuongKhaiThac_{year}_{month:02d}.xlsx"'
    return response


@login_required
def unmatched_report(request):
    profile = get_profile(request.user)
    if not (request.user.is_superuser or (profile and profile.is_admin())):
        raise PermissionDenied("Chi Admin moi xem duoc trang nay.")

    unmapped = KhaiThacServiceMapping.objects.filter(nhom_dich_vu__isnull=True)
    mapped = KhaiThacServiceMapping.objects.filter(nhom_dich_vu__isnull=False)
    return render(
        request, "khaithac_unmatched.html", {"unmapped": unmapped, "mapped": mapped}
    )

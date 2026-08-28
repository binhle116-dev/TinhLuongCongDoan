import datetime as dt
import io
from decimal import Decimal

import openpyxl
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from core.permissions import get_profile, scope_post_office_choices, scope_queryset
from phat.forms import AllowanceEntryForm
from phat.models import (
    AllowanceEntry,
    EmployeeMonthlyPay,
    ImportBatch,
    MonthlyPayrollRun,
    RawDailyProduction,
)


def _current_year_month():
    today = dt.date.today()
    return today.year, today.month


def _prev_year_month(year: int, month: int) -> tuple[int, int]:
    return (year - 1, 12) if month == 1 else (year, month - 1)


def _build_period_options() -> list[tuple[int, int, str]]:
    """Cac ky THAT su da co ky chot/tam tinh (MonthlyPayrollRun) - khong
    bia them thang trong khong co gi."""
    periods = MonthlyPayrollRun.objects.values_list("year", "month").distinct()
    return [(y, m, f"Tháng {m:02d}/{y}") for y, m in sorted(periods, reverse=True)]


def _is_admin(request) -> bool:
    profile = get_profile(request.user)
    return bool(request.user.is_superuser or (profile and profile.is_admin()))


OFFICE_PALETTE = ["#2f7de1", "#0891b2", "#7c6ff0", "#d97706", "#16a34a", "#db2777", "#64748b", "#84652c"]


def _add_office_shares_and_colors(by_office: list[dict], tong_thu_nhap: Decimal) -> None:
    """Gan ty_trong (%) + mau + toa do donut cho tung dong 'theo buu cuc' -
    chi phuc vu hien thi, khong dong den cach tinh EmployeeMonthlyPay."""
    circumference = 2 * 3.14159265 * 40
    offset_pct = Decimal("0")
    for idx, row in enumerate(by_office):
        row["ty_trong"] = (row["total"] / tong_thu_nhap * 100) if tong_thu_nhap else Decimal("0")
        row["color"] = OFFICE_PALETTE[idx % len(OFFICE_PALETTE)]
        length = float(row["ty_trong"]) / 100 * circumference
        row["donut_dasharray"] = f"{length:.2f} {circumference:.2f}"
        row["donut_dashoffset"] = f"{-(float(offset_pct) / 100 * circumference):.2f}"
        offset_pct += row["ty_trong"]


def _totals_for_scope(user, year: int, month: int, selected_office: str) -> dict:
    """Tong hop (khong phan theo bua cuc) cho 1 ky, trong dung pham vi RBAC
    + bo loc bc dang chon - dung de tinh KPI va so sanh voi ky truoc."""
    run = MonthlyPayrollRun.objects.filter(year=year, month=month).first()
    pays = EmployeeMonthlyPay.objects.filter(run=run) if run else EmployeeMonthlyPay.objects.none()
    pays = scope_queryset(pays, user, field_name="employee__post_office")
    if selected_office:
        pays = pays.filter(employee__post_office__code=selected_office)
    agg = pays.aggregate(
        so_lao_dong=Count("id"), piece_rate=Sum("piece_rate_amount"),
        allowance=Sum("allowance_amount"), total=Sum("total_amount"),
    )
    return {
        "so_lao_dong": agg["so_lao_dong"] or 0,
        "piece_rate": agg["piece_rate"] or Decimal("0"),
        "allowance": agg["allowance"] or Decimal("0"),
        "total": agg["total"] or Decimal("0"),
    }


@login_required
def allowance_list(request):
    year = int(request.GET.get("year", _current_year_month()[0]))
    month = int(request.GET.get("month", _current_year_month()[1]))
    entries = AllowanceEntry.objects.filter(year=year, month=month).select_related(
        "employee", "allowance_type"
    )
    entries = scope_queryset(entries, request.user, field_name="employee__post_office")
    total_amount = entries.aggregate(s=Sum("amount"))["s"] or Decimal("0")
    return render(
        request, "allowance_list.html",
        {"entries": entries, "year": year, "month": month, "total_amount": total_amount},
    )


@login_required
def allowance_edit(request, pk=None):
    instance = None
    if pk is not None:
        instance = get_object_or_404(
            scope_queryset(AllowanceEntry.objects.all(), request.user, field_name="employee__post_office"),
            pk=pk,
        )
    if request.method == "POST":
        form = AllowanceEntryForm(request.POST, instance=instance, user=request.user)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.created_by = request.user
            entry.save()
            from phat.services.pricing import recalc_totals_for_run

            run = MonthlyPayrollRun.objects.filter(year=entry.year, month=entry.month).first()
            if run:
                recalc_totals_for_run(run)
            messages.success(request, "Da luu khoan ho tro.")
            return redirect(f"/ho-tro/?year={entry.year}&month={entry.month}")
    else:
        form = AllowanceEntryForm(instance=instance, user=request.user)
    return render(request, "allowance_form.html", {"form": form, "instance": instance})


@login_required
def payroll_detail(request, year, month):
    run = MonthlyPayrollRun.objects.filter(year=year, month=month).first()
    pays = EmployeeMonthlyPay.objects.filter(run=run) if run else EmployeeMonthlyPay.objects.none()
    pays = scope_queryset(pays, request.user, field_name="employee__post_office")

    # Danh sach BCVH cho bo loc - chi trong pham vi nguoi dung duoc xem.
    office_choices = scope_post_office_choices(request.user).order_by("code")
    selected_office = request.GET.get("bc", "")
    if selected_office:
        pays = pays.filter(employee__post_office__code=selected_office)

    pays = pays.select_related("employee", "employee__post_office").order_by("-total_amount")

    by_office = list(
        pays.values("employee__post_office__code", "employee__post_office__name")
        .annotate(
            so_lao_dong=Count("id"),
            piece_rate=Sum("piece_rate_amount"),
            allowance=Sum("allowance_amount"),
            total=Sum("total_amount"),
        )
        .order_by("-total")
    )

    totals = _totals_for_scope(request.user, year, month, selected_office)
    tong_thu_nhap = totals["total"] or Decimal("0")
    _add_office_shares_and_colors(by_office, tong_thu_nhap)

    prev_year, prev_month = _prev_year_month(year, month)
    prev_totals = _totals_for_scope(request.user, prev_year, prev_month, selected_office)
    prev_compare = None
    if prev_totals["total"]:  # co du lieu that ky truoc, khong bia so
        prev_compare = {
            "year": prev_year, "month": prev_month,
            "total_delta": (totals["total"] - prev_totals["total"]) / prev_totals["total"],
            "piece_rate_delta": (
                (totals["piece_rate"] - prev_totals["piece_rate"]) / prev_totals["piece_rate"]
                if prev_totals["piece_rate"] else None
            ),
        }

    last_batch = ImportBatch.objects.order_by("-created_at").first()

    context = {
        "year": year,
        "month": month,
        "run": run,
        "pays": pays,
        "by_office": by_office,
        "office_choices": office_choices,
        "selected_office": selected_office,
        "is_provisional": (not run) or (not run.is_finalized()),
        "totals": totals,
        "prev_compare": prev_compare,
        "last_updated": last_batch.created_at if last_batch else None,
        "period_options": _build_period_options(),
        "is_admin": _is_admin(request),
    }
    return render(request, "payroll_detail.html", context)


@login_required
def export_excel(request, year, month):
    run = MonthlyPayrollRun.objects.filter(year=year, month=month).first()
    pays = EmployeeMonthlyPay.objects.filter(run=run) if run else EmployeeMonthlyPay.objects.none()
    pays = scope_queryset(pays, request.user, field_name="employee__post_office")
    selected_office = request.GET.get("bc", "")
    if selected_office:
        pays = pays.filter(employee__post_office__code=selected_office)
    pays = pays.select_related("employee", "employee__post_office").order_by(
        "employee__post_office__code", "-total_amount"
    )

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Chi tiet theo lao dong"
    ws.append(["Ma HRM", "Ho ten", "Ma BC", "Ten BC", "Cong san luong (tam tinh)", "Ho tro", "Tong thu nhap"])
    for pay in pays:
        ws.append(
            [
                pay.employee.hrm_code,
                pay.employee.full_name,
                pay.employee.post_office.code,
                pay.employee.post_office.name,
                float(pay.piece_rate_amount),
                float(pay.allowance_amount),
                float(pay.total_amount),
            ]
        )

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    response = HttpResponse(
        buffer.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="LuongCongDoanPhat_{year}_{month:02d}.xlsx"'
    return response


@login_required
def unmatched_report(request):
    profile = get_profile(request.user)
    if not (request.user.is_superuser or (profile and profile.is_admin())):
        raise PermissionDenied("Chi Admin moi xem duoc trang nay.")
    unmatched = RawDailyProduction.objects.filter(
        service_category__isnull=True
    ).values(
        "service_code", "type_code_payroll", "service_name_payroll", "area_code"
    ).annotate(so_dong=Sum("quantity")).order_by("-so_dong")[:200]
    unmatched_employee = RawDailyProduction.objects.filter(employee__isnull=True).values(
        "postman_code"
    ).distinct()[:200]
    return render(
        request,
        "unmatched_report.html",
        {"unmatched": unmatched, "unmatched_employee": unmatched_employee},
    )

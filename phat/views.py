import datetime as dt
import io

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
    MonthlyPayrollRun,
    RawDailyProduction,
)


def _current_year_month():
    today = dt.date.today()
    return today.year, today.month


@login_required
def allowance_list(request):
    year = int(request.GET.get("year", _current_year_month()[0]))
    month = int(request.GET.get("month", _current_year_month()[1]))
    entries = AllowanceEntry.objects.filter(year=year, month=month).select_related(
        "employee", "allowance_type"
    )
    entries = scope_queryset(entries, request.user, field_name="employee__post_office")
    return render(
        request, "allowance_list.html", {"entries": entries, "year": year, "month": month}
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

    by_office = (
        pays.values("employee__post_office__code", "employee__post_office__name")
        .annotate(
            so_lao_dong=Count("id"),
            piece_rate=Sum("piece_rate_amount"),
            allowance=Sum("allowance_amount"),
            total=Sum("total_amount"),
        )
        .order_by("-total")
    )

    context = {
        "year": year,
        "month": month,
        "run": run,
        "pays": pays,
        "by_office": by_office,
        "office_choices": office_choices,
        "selected_office": selected_office,
        "is_provisional": (not run) or (not run.is_finalized()),
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

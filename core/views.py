import datetime as dt

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render

from core.forms import EmployeeForm
from core.models import Employee, PostOffice
from core.permissions import scope_post_office_choices, scope_queryset, user_scope_post_office

KHAITHAC_POST_OFFICE_CODE = "530100"


def _current_year_month():
    today = dt.date.today()
    return today.year, today.month


def _phat_summary(user, year, month, selected_office):
    from phat.models import EmployeeMonthlyPay, ImportBatch, MonthlyPayrollRun

    run = MonthlyPayrollRun.objects.filter(year=year, month=month).first()
    pays = EmployeeMonthlyPay.objects.filter(run=run) if run else EmployeeMonthlyPay.objects.none()
    pays = scope_queryset(pays, user, field_name="employee__post_office")
    if selected_office:
        pays = pays.filter(employee__post_office__code=selected_office)
    totals = pays.aggregate(
        so_lao_dong=Count("id"), piece_rate=Sum("piece_rate_amount"),
        allowance=Sum("allowance_amount"), total=Sum("total_amount"),
    )
    last_batch = ImportBatch.objects.order_by("-created_at").first()
    return {"run": run, "totals": totals, "last_batch": last_batch}


def _khaithac_summary(user, year, month, selected_office):
    from khaithac.services.employee_pay import compute_employee_shares
    from khaithac.services.pricing import compute_fund_breakdown

    if selected_office and selected_office != KHAITHAC_POST_OFFICE_CODE:
        return None  # buu cuc dang chon khac buu cuc Khai thac

    post_office = scope_queryset(
        PostOffice.objects.filter(code=KHAITHAC_POST_OFFICE_CODE), user
    ).first()
    if post_office is None:
        return None  # ngoai pham vi tai khoan (RBAC) hoac chua co buu cuc nay

    result = compute_fund_breakdown(post_office, year, month)
    shares = compute_employee_shares(post_office, year, month, result["tong_quy_tien_luong"])
    return {
        "post_office": post_office,
        "so_lao_dong": len(shares["per_employee"]),
        "san_luong": result["tong_san_luong_tinh_tien"],
        "quy_tien_luong": result["tong_quy_tien_luong"],
    }


@login_required
def overview_dashboard(request):
    default_year, default_month = _current_year_month()
    year = int(request.GET.get("year", default_year))
    month = int(request.GET.get("month", default_month))

    office_choices = scope_post_office_choices(request.user).order_by("code")
    selected_office = request.GET.get("bc", "")
    forced_office = user_scope_post_office(request.user)
    if forced_office is not None:
        selected_office = forced_office.code

    context = {
        "year": year,
        "month": month,
        "office_choices": office_choices,
        "selected_office": selected_office,
        "phat": _phat_summary(request.user, year, month, selected_office),
        "khaithac": _khaithac_summary(request.user, year, month, selected_office),
    }
    return render(request, "dashboard.html", context)


@login_required
def employee_list(request):
    office_choices = scope_post_office_choices(request.user).order_by("code")
    selected_office = request.GET.get("bc", "")
    forced_office = user_scope_post_office(request.user)
    if forced_office is not None:
        selected_office = forced_office.code
    elif not selected_office:
        first_office = office_choices.first()
        selected_office = first_office.code if first_office else ""

    employees = scope_queryset(Employee.objects.select_related("post_office"), request.user)
    if selected_office:
        employees = employees.filter(post_office__code=selected_office)
    employees = employees.order_by("full_name")

    context = {
        "employees": employees,
        "office_choices": office_choices,
        "selected_office": selected_office,
    }
    return render(request, "employee_list.html", context)


@login_required
def employee_edit(request, pk=None):
    instance = None
    if pk is not None:
        instance = get_object_or_404(
            scope_queryset(Employee.objects.all(), request.user), pk=pk
        )
    if request.method == "POST":
        form = EmployeeForm(request.POST, instance=instance, user=request.user)
        if form.is_valid():
            employee = form.save()
            messages.success(request, "Da luu thong tin nhan vien.")
            return redirect(f"/nhan-su/?bc={employee.post_office.code}")
    else:
        form = EmployeeForm(instance=instance, user=request.user)
    return render(request, "employee_form.html", {"form": form, "instance": instance})

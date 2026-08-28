import datetime as dt

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from core.models import PostOffice
from core.permissions import get_profile, scope_queryset
from khaithac.services.employee_pay import compute_employee_shares
from khaithac.services.pricing import compute_fund_breakdown


def _current_year_month():
    today = dt.date.today()
    return today.year, today.month


@login_required
def dashboard(request, year=None, month=None):
    if year is None or month is None:
        year, month = _current_year_month()

    office_choices = scope_queryset(
        PostOffice.objects.filter(code="530100"), request.user
    )
    post_office = office_choices.first()

    result = None
    shares = None
    if post_office:
        result = compute_fund_breakdown(post_office, year, month)
        shares = compute_employee_shares(post_office, year, month, result["tong_quy_tien_luong"])

    context = {
        "year": year,
        "month": month,
        "post_office": post_office,
        "result": result,
        "shares": shares,
    }
    return render(request, "khaithac_dashboard.html", context)


@login_required
def unmatched_report(request):
    profile = get_profile(request.user)
    if not (request.user.is_superuser or (profile and profile.is_admin())):
        raise PermissionDenied("Chi Admin moi xem duoc trang nay.")

    from khaithac.models import KhaiThacServiceMapping

    unmapped = KhaiThacServiceMapping.objects.filter(nhom_dich_vu__isnull=True)
    mapped = KhaiThacServiceMapping.objects.filter(nhom_dich_vu__isnull=False)
    return render(
        request, "khaithac_unmatched.html", {"unmapped": unmapped, "mapped": mapped}
    )

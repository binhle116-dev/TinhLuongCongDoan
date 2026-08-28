"""Co che duy nhat de gioi han du lieu theo buu cuc. MOI view/query lien
quan den du lieu theo buu cuc (Employee, AllowanceEntry, EmployeeMonthlyPay...)
PHAI di qua day, khong tu viet filter rieng - tranh ro ri du lieu giua cac
buu cuc (xem ghi chu rui ro trong plan)."""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from core.models import PostOffice, UserProfile


def get_profile(user):
    return getattr(user, "profile", None)


def user_scope_post_office(user):
    """Tra ve PostOffice neu user bi gioi han theo 1 buu cuc (Truong buu
    cuc), hoac None neu user duoc xem/sua toan bo (Admin/Phong ban/superuser)."""
    if user.is_superuser:
        return None
    profile = get_profile(user)
    if profile is None:
        return None
    if profile.role == UserProfile.ROLE_TRUONG_BUU_CUC:
        return profile.post_office
    return None


def scope_queryset(queryset, user, field_name="post_office"):
    """Loc queryset theo buu cuc cua user neu can. field_name la duong dan
    tu model dang query toi PostOffice, vi du 'post_office' cho Employee,
    'employee__post_office' cho AllowanceEntry."""
    post_office = user_scope_post_office(user)
    if post_office is None:
        return queryset
    return queryset.filter(**{field_name: post_office})


def scope_post_office_choices(user):
    """Tra ve danh sach PostOffice user duoc chon (vd dropdown loc theo
    BCVH). Khac scope_queryset() thong thuong: PostOffice khong co truong
    tu tro ve chinh no ten 'post_office' de loc qua field_name mac dinh,
    nen can loc rieng theo pk."""
    post_office = user_scope_post_office(user)
    if post_office is None:
        return PostOffice.objects.all()
    return PostOffice.objects.filter(pk=post_office.pk)


def role_required(*roles):
    """Decorator cho view function: chi cho phep user co role trong danh
    sach (hoac superuser) truy cap, con lai bao 403."""

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            profile = get_profile(request.user)
            if profile is None or profile.role not in roles:
                raise PermissionDenied("Ban khong co quyen truy cap trang nay.")
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator

from django.urls import path

from phat import views

urlpatterns = [
    path("ho-tro/", views.allowance_list, name="allowance_list"),
    path("ho-tro/them/", views.allowance_edit, name="allowance_create"),
    path("ho-tro/<int:pk>/sua/", views.allowance_edit, name="allowance_edit"),
    path("luong/<int:year>/<int:month>/", views.payroll_detail, name="payroll_detail"),
    path("luong/<int:year>/<int:month>/xuat-excel/", views.export_excel, name="export_excel"),
    path("bao-cao/chua-anh-xa/", views.unmatched_report, name="unmatched_report"),
]

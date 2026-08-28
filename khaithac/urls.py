from django.urls import path

from khaithac import views

urlpatterns = [
    path("khai-thac/", views.dashboard, name="khaithac_dashboard"),
    path("khai-thac/<int:year>/<int:month>/", views.dashboard, name="khaithac_dashboard_month"),
    path("khai-thac/<int:year>/<int:month>/xuat-excel/", views.export_excel, name="khaithac_export_excel"),
    path("khai-thac/chua-anh-xa/", views.unmatched_report, name="khaithac_unmatched_report"),
]

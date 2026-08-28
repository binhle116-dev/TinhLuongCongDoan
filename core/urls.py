from django.urls import path

from core import views

urlpatterns = [
    path("", views.overview_dashboard, name="dashboard"),
    path("nhan-su/", views.employee_list, name="employee_list"),
    path("nhan-su/them/", views.employee_edit, name="employee_create"),
    path("nhan-su/<int:pk>/sua/", views.employee_edit, name="employee_edit"),
]

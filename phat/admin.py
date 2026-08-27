from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from phat.models import (
    AllowanceEntry,
    AllowanceType,
    EmployeeMonthlyPay,
    EmployeeMonthlyPayDetail,
    ImportBatch,
    MonthlyPayrollRun,
    PostOfficeConfirmation,
    PriceCard,
    PriceGroup,
    RawDailyProduction,
    RouteGroupMapping,
    ServiceCategory,
    ServiceMapping,
)


@admin.register(ImportBatch)
class ImportBatchAdmin(admin.ModelAdmin):
    list_display = ("source_filename", "production_date", "row_count", "unmatched_count", "status", "created_at")
    list_filter = ("status",)
    readonly_fields = [f.name for f in ImportBatch._meta.fields]

    def has_add_permission(self, request):
        return False


@admin.register(RawDailyProduction)
class RawDailyProductionAdmin(admin.ModelAdmin):
    list_display = (
        "lading_code", "postman_code", "status_date", "service_name_payroll",
        "area_code", "weight_gram", "quantity", "service_category", "employee",
    )
    list_filter = ("status_date", "area_code", "service_category")
    search_fields = ("lading_code", "postman_code")

    def has_add_permission(self, request):
        return False


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(ImportExportModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")


@admin.register(ServiceMapping)
class ServiceMappingAdmin(ImportExportModelAdmin):
    list_display = (
        "priority", "service_code", "type_code_payroll", "service_name_payroll",
        "area_code", "weight_min_gram", "weight_max_gram", "service_category", "is_active",
    )
    list_display_links = ("service_code",)
    list_editable = ("priority", "is_active")
    list_filter = ("is_active", "area_code", "service_category")
    search_fields = ("service_code", "type_code_payroll", "service_name_payroll")


@admin.register(PriceGroup)
class PriceGroupAdmin(ImportExportModelAdmin):
    list_display = ("code", "name")


@admin.register(RouteGroupMapping)
class RouteGroupMappingAdmin(ImportExportModelAdmin):
    list_display = ("route_code", "price_group", "effective_from", "effective_to")
    search_fields = ("route_code",)
    list_filter = ("price_group",)


@admin.register(PriceCard)
class PriceCardAdmin(ImportExportModelAdmin):
    list_display = ("service_category", "price_group", "unit_price", "effective_from", "effective_to")
    list_filter = ("price_group", "service_category")


@admin.register(AllowanceType)
class AllowanceTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "default_unit_price", "unit_label", "is_active")


@admin.register(AllowanceEntry)
class AllowanceEntryAdmin(admin.ModelAdmin):
    list_display = ("employee", "allowance_type", "year", "month", "quantity", "unit_price", "amount")
    list_filter = ("allowance_type", "year", "month")
    search_fields = ("employee__hrm_code", "employee__full_name")
    autocomplete_fields = ("employee",)


@admin.register(MonthlyPayrollRun)
class MonthlyPayrollRunAdmin(admin.ModelAdmin):
    list_display = ("year", "month", "status", "finalized_at", "finalized_by")
    list_filter = ("status", "year")


@admin.register(EmployeeMonthlyPay)
class EmployeeMonthlyPayAdmin(admin.ModelAdmin):
    list_display = ("run", "employee", "piece_rate_amount", "allowance_amount", "total_amount", "is_provisional")
    list_filter = ("run", "is_provisional")
    search_fields = ("employee__hrm_code", "employee__full_name")


@admin.register(EmployeeMonthlyPayDetail)
class EmployeeMonthlyPayDetailAdmin(admin.ModelAdmin):
    list_display = ("employee_pay", "service_category", "quantity", "unit_price", "amount")
    list_filter = ("service_category",)


@admin.register(PostOfficeConfirmation)
class PostOfficeConfirmationAdmin(admin.ModelAdmin):
    list_display = ("run", "post_office", "status", "created_at")
    list_filter = ("status", "run")

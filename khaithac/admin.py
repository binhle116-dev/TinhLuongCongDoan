from django.contrib import admin

from khaithac.models import (
    KhaiThacImportBatch,
    KhaiThacPriceCard,
    KhaiThacQualityCoefficient,
    KhaiThacRawProduction,
    KhaiThacServiceMapping,
    KhaiThacShiftAssignment,
)


@admin.register(KhaiThacImportBatch)
class KhaiThacImportBatchAdmin(admin.ModelAdmin):
    list_display = ["post_office", "production_date", "row_count", "status", "created_at"]
    list_filter = ["post_office", "status"]
    ordering = ["-production_date"]


@admin.register(KhaiThacServiceMapping)
class KhaiThacServiceMappingAdmin(admin.ModelAdmin):
    list_display = ["loai_raw", "nhom_dich_vu", "note"]
    list_editable = ["nhom_dich_vu"]


@admin.register(KhaiThacPriceCard)
class KhaiThacPriceCardAdmin(admin.ModelAdmin):
    list_display = ["nhom_dich_vu", "unit_price", "effective_from", "effective_to", "source_document"]
    list_filter = ["nhom_dich_vu"]


@admin.register(KhaiThacRawProduction)
class KhaiThacRawProductionAdmin(admin.ModelAdmin):
    list_display = ["post_office", "production_date", "ca", "loai_raw", "weight_tier", "so_luong"]
    list_filter = ["post_office", "ca", "loai_raw"]
    date_hierarchy = "production_date"


@admin.register(KhaiThacShiftAssignment)
class KhaiThacShiftAssignmentAdmin(admin.ModelAdmin):
    list_display = ["raw_name", "employee", "work_date", "cong_viec", "ca", "he_so"]
    list_filter = ["ca", "cong_viec"]
    search_fields = ["raw_name"]
    date_hierarchy = "work_date"


@admin.register(KhaiThacQualityCoefficient)
class KhaiThacQualityCoefficientAdmin(admin.ModelAdmin):
    list_display = ["employee", "year", "month", "he_so"]
    list_filter = ["year", "month"]

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User

from core.models import Employee, PositionCatalog, PostOffice, UserProfile


@admin.register(PostOffice)
class PostOfficeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "area", "is_active")
    search_fields = ("code", "name")
    list_filter = ("is_active", "area")


@admin.register(PositionCatalog)
class PositionCatalogAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("hrm_code", "postman_code", "full_name", "post_office", "position", "contract_type", "is_active")
    search_fields = ("hrm_code", "postman_code", "full_name")
    list_filter = ("post_office", "position", "contract_type", "is_active")
    autocomplete_fields = ("post_office", "position")


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    extra = 0


class UserAdmin(DjangoUserAdmin):
    inlines = (UserProfileInline,)
    list_display = DjangoUserAdmin.list_display + ("get_role", "get_post_office")

    @admin.display(description="Vai tro")
    def get_role(self, obj):
        profile = getattr(obj, "profile", None)
        return profile.get_role_display() if profile else "-"

    @admin.display(description="Buu cuc")
    def get_post_office(self, obj):
        profile = getattr(obj, "profile", None)
        return profile.post_office if profile and profile.post_office else "-"


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.site_header = "Quan tri Tinh luong Cong doan"
admin.site.site_title = "Tinh luong Cong doan"

from django import forms

from core.models import Employee
from core.permissions import user_scope_post_office
from phat.models import AllowanceEntry, AllowanceType


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "hrm_code", "postman_code", "full_name", "post_office",
            "contract_type", "position", "is_active", "start_date",
        ]
        widgets = {"start_date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        scoped_post_office = user_scope_post_office(user) if user else None
        if scoped_post_office is not None:
            self.fields["post_office"].queryset = self.fields["post_office"].queryset.filter(
                pk=scoped_post_office.pk
            )
            self.fields["post_office"].initial = scoped_post_office
            self.fields["post_office"].disabled = True


class AllowanceEntryForm(forms.ModelForm):
    class Meta:
        model = AllowanceEntry
        fields = ["employee", "allowance_type", "year", "month", "quantity", "unit_price", "note"]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        scoped_post_office = user_scope_post_office(user) if user else None
        if scoped_post_office is not None:
            self.fields["employee"].queryset = Employee.objects.filter(post_office=scoped_post_office)
        self.fields["allowance_type"].queryset = AllowanceType.objects.filter(is_active=True)
        self.fields["unit_price"].required = False
        self.fields["unit_price"].help_text = "De trong de dung don gia mac dinh cua khoan ho tro."

"""Ap dung lai ServiceMapping/Employee cho cac dong RawDailyProduction da
import tu truoc nhung chua khop duoc (service_category hoac employee con
NULL) - dung sau khi them quy tac anh xa moi hoac postman_code moi, KHONG
can tai lai file goc. Sau khi cap nhat, tinh lai 'tam tinh' cho moi thang
bi anh huong."""
from __future__ import annotations

from django.core.management.base import BaseCommand

from core.models import Employee
from phat.models import RawDailyProduction
from phat.services.pricing import compute_provisional_pay, load_active_mappings, match_service_category


class Command(BaseCommand):
    help = "Ap dung lai anh xa dich vu/nhan vien cho du lieu da import truoc do, roi tinh lai tam tinh."

    def handle(self, *args, **options):
        mappings = load_active_mappings()
        employee_by_postman = {
            e.postman_code: e for e in Employee.objects.exclude(postman_code="")
        }

        rows = RawDailyProduction.objects.filter(service_category__isnull=True)
        n_category_fixed = 0
        n_employee_fixed = 0
        to_update = []
        affected_year_months: set[tuple[int, int]] = set()

        for row in rows:
            changed = False
            category = match_service_category(
                mappings,
                service_code=row.service_code,
                type_code_payroll=row.type_code_payroll,
                service_name_payroll=row.service_name_payroll,
                area_code=row.area_code,
                weight_gram=row.weight_gram,
            )
            if category is not None:
                row.service_category = category
                n_category_fixed += 1
                changed = True
            if row.employee_id is None:
                employee = employee_by_postman.get(row.postman_code)
                if employee is not None:
                    row.employee = employee
                    n_employee_fixed += 1
                    changed = True
            if changed:
                to_update.append(row)
                if row.status_date:
                    affected_year_months.add((row.status_date.year, row.status_date.month))

        RawDailyProduction.objects.bulk_update(to_update, ["service_category", "employee"], batch_size=1000)

        self.stdout.write(self.style.SUCCESS(
            f"Da khop them {n_category_fixed} dong theo dich vu, {n_employee_fixed} dong theo nhan vien "
            f"({len(to_update)} dong thay doi)."
        ))

        for year, month in sorted(affected_year_months):
            run = compute_provisional_pay(year, month)
            self.stdout.write(self.style.SUCCESS(f"Da tinh lai tam tinh cho {run}"))

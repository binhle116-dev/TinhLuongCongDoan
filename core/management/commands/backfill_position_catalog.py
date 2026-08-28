"""Seed PositionCatalog tu cac gia tri Employee.position_legacy THAT dang
co (dinh dang "MA - Ten", vd '1527 - Phat xa'), roi gan Employee.position
(FK moi) tuong ung. Idempotent: chay lai an toan.

Chay 1 lan sau khi migrate xong (core.0003/0004) de hoan tat viec doi
Chuc danh tu nhap tu do sang droplist theo danh muc."""
from __future__ import annotations

from django.core.management.base import BaseCommand

from core.models import Employee, PositionCatalog


class Command(BaseCommand):
    help = "Seed PositionCatalog tu Employee.position_legacy va gan lai Employee.position (FK)."

    def handle(self, *args, **options):
        distinct_values = (
            Employee.objects.exclude(position_legacy="")
            .values_list("position_legacy", flat=True)
            .distinct()
        )

        catalog_by_raw: dict[str, PositionCatalog] = {}
        n_created = 0
        for raw in distinct_values:
            if " - " in raw:
                code, name = raw.split(" - ", 1)
            else:
                code, name = raw, raw
            obj, created = PositionCatalog.objects.get_or_create(
                code=code.strip(), defaults={"name": name.strip()}
            )
            catalog_by_raw[raw] = obj
            n_created += 1 if created else 0

        n_linked = 0
        for emp in Employee.objects.exclude(position_legacy=""):
            catalog = catalog_by_raw.get(emp.position_legacy)
            if catalog and emp.position_id != catalog.id:
                emp.position = catalog
                emp.save(update_fields=["position"])
                n_linked += 1

        self.stdout.write(self.style.SUCCESS(
            f"Da tao {n_created} chuc danh moi trong danh muc, gan lai {n_linked} nhan vien."
        ))

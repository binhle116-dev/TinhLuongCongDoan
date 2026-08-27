"""Logic anh xa dich vu + tinh 'tam tinh' cong theo san luong.

QUAN TRONG: bang ServiceMapping / RouteGroupMapping / PriceCard hien CHUA
duoc TCHC/TCKH xac nhan day du (xem ghi chu trong plan). Moi ket qua tinh
tu day PHAI duoc gan nhan "tam tinh - chua xac minh" (xem
EmployeeMonthlyPay.is_provisional) cho toi khi thang duoc chot chinh thuc.
"""
from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from django.db.models import Sum

from phat.models import (
    EmployeeMonthlyPay,
    EmployeeMonthlyPayDetail,
    MonthlyPayrollRun,
    PriceCard,
    RawDailyProduction,
    RouteGroupMapping,
    ServiceMapping,
)


def load_active_mappings():
    """Nap 1 lan bang anh xa dang hoat dong (danh sach nho, ~vai chuc dong)
    de tranh truy van DB tung dong khi xu ly hang nghin ban ghi tho."""
    return list(
        ServiceMapping.objects.filter(is_active=True)
        .order_by("priority", "id")
        .select_related("service_category")
    )


def match_service_category(mappings, *, service_code, type_code_payroll, service_name_payroll, area_code, weight_gram):
    """Duyet danh sach mappings (da sap theo priority) tim quy tac dau tien
    khop. Dieu kien de trong ("") hoac None nghia la khop bat ky."""
    for m in mappings:
        if m.service_code and m.service_code != service_code:
            continue
        if m.type_code_payroll and m.type_code_payroll != type_code_payroll:
            continue
        if m.service_name_payroll and m.service_name_payroll != service_name_payroll:
            continue
        if m.area_code and m.area_code != area_code:
            continue
        if m.weight_min_gram is not None and (weight_gram is None or weight_gram < m.weight_min_gram):
            continue
        if m.weight_max_gram is not None and (weight_gram is None or weight_gram > m.weight_max_gram):
            continue
        return m.service_category
    return None


def resolve_service_category(*, service_code, type_code_payroll, service_name_payroll, area_code, weight_gram):
    """Tien ich tien loi khi chi can tra cuu 1 dong don le (vd trong
    importer). Voi xu ly hang loat, dung load_active_mappings() +
    match_service_category() de tranh truy van DB lap lai."""
    mappings = load_active_mappings()
    return match_service_category(
        mappings,
        service_code=service_code,
        type_code_payroll=type_code_payroll,
        service_name_payroll=service_name_payroll,
        area_code=area_code,
        weight_gram=weight_gram,
    )


def load_price_lookup():
    """Tra ve dict {(service_category_id, price_group_id): unit_price}."""
    lookup = {}
    for pc in PriceCard.objects.all():
        lookup[(pc.service_category_id, pc.price_group_id)] = pc.unit_price
    return lookup


def load_route_group_lookup():
    """Tra ve dict {route_code: price_group_id}."""
    return {
        rg.route_code: rg.price_group_id
        for rg in RouteGroupMapping.objects.all()
    }


def compute_provisional_pay(year: int, month: int) -> MonthlyPayrollRun:
    """Tinh lai 'tam tinh' cong theo san luong cho ca thang tu
    RawDailyProduction hien co. KHONG tinh lai neu ky da 'Da chot'
    (finalized) - tranh lam sai lech so da chi tra."""
    run, _ = MonthlyPayrollRun.objects.get_or_create(year=year, month=month)
    if run.is_finalized():
        return run

    price_lookup = load_price_lookup()
    route_group_lookup = load_route_group_lookup()

    rows = (
        RawDailyProduction.objects.filter(
            status_date__year=year, status_date__month=month,
            employee__isnull=False, service_category__isnull=False,
        )
        .values("employee_id", "service_category_id", "route_po_code")
        .annotate(total_qty=Sum("quantity"))
    )

    # employee_id -> {service_category_id: (qty, unit_price, amount)}
    per_employee: dict[int, dict[int, list]] = defaultdict(dict)
    for row in rows:
        group_id = route_group_lookup.get(row["route_po_code"])
        unit_price = price_lookup.get((row["service_category_id"], group_id), Decimal("0"))
        qty = abs(row["total_qty"] or 0)
        amount = Decimal(qty) * unit_price
        bucket = per_employee[row["employee_id"]].setdefault(
            row["service_category_id"], [0.0, unit_price, Decimal("0")]
        )
        bucket[0] += qty
        bucket[2] += amount

    EmployeeMonthlyPayDetail.objects.filter(employee_pay__run=run).delete()
    for employee_id, by_category in per_employee.items():
        piece_rate_total = sum((v[2] for v in by_category.values()), Decimal("0"))
        pay, _ = EmployeeMonthlyPay.objects.update_or_create(
            run=run, employee_id=employee_id,
            defaults={"piece_rate_amount": piece_rate_total, "is_provisional": True},
        )
        EmployeeMonthlyPayDetail.objects.bulk_create(
            [
                EmployeeMonthlyPayDetail(
                    employee_pay=pay, service_category_id=cat_id,
                    quantity=qty, unit_price=price, amount=amount,
                )
                for cat_id, (qty, price, amount) in by_category.items()
            ]
        )

    recalc_totals_for_run(run)
    return run


def recalc_totals_for_run(run: MonthlyPayrollRun) -> None:
    """Cong lai allowance_amount (tu AllowanceEntry) + total_amount cho
    tat ca EmployeeMonthlyPay cua 1 ky. Goi lai sau khi Truong buu cuc
    them/sua khoan ho tro."""
    from phat.models import AllowanceEntry  # tranh vong lap import

    allowance_by_employee = {
        row["employee_id"]: row["total"]
        for row in AllowanceEntry.objects.filter(year=run.year, month=run.month)
        .values("employee_id")
        .annotate(total=Sum("amount"))
    }

    # Dam bao co dong EmployeeMonthlyPay cho nhan vien chi co khoan ho tro,
    # khong co san luong nao trong thang (vd nghi phep ca thang).
    existing_ids = set(run.employee_pays.values_list("employee_id", flat=True))
    for employee_id in allowance_by_employee:
        if employee_id not in existing_ids:
            EmployeeMonthlyPay.objects.get_or_create(
                run=run, employee_id=employee_id,
                defaults={"piece_rate_amount": Decimal("0"), "is_provisional": True},
            )

    for pay in run.employee_pays.all():
        allowance = allowance_by_employee.get(pay.employee_id, Decimal("0")) or Decimal("0")
        pay.allowance_amount = allowance
        pay.total_amount = pay.piece_rate_amount + allowance
        pay.save(update_fields=["allowance_amount", "total_amount"])

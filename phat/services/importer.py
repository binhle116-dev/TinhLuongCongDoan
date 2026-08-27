"""Import file du lieu tho hang ngay (SanLuongChiTiet_DDMMYYYY.xlsx) vao
RawDailyProduction. Idempotent theo production_date: import lai cung 1
ngay se xoa du lieu ngay do cu va thay bang du lieu moi (khong bi trung)."""
from __future__ import annotations

import datetime as dt
from pathlib import Path

import pandas as pd
from django.db import transaction

from core.models import Employee
from core.textutils import clean_cell_text, to_float
from phat.models import ImportBatch, RawDailyProduction
from phat.services.pricing import load_active_mappings, match_service_category

REQUIRED_COLUMNS = {
    "LADING_CODE", "POSTMAN_CODE", "ROUTE_PO_CODE", "Mã bưu cục", "STATUS_CODE",
    "TYPE_CODE_PAYROLL", "SERVICE_NAME_PAYROLL", "AREA_CODE", "SERVICE_CODE",
    "ITEM_TYPE_CODE", "KG", "STATUS_DATE", "QUANTITY",
}


def _parse_status_date(value) -> dt.date | None:
    text = clean_cell_text(value)
    if not text:
        return None
    text = text.split(".")[0]  # excel co the doc so thanh vd '20260826.0'
    try:
        return dt.datetime.strptime(text, "%Y%m%d").date()
    except ValueError:
        return None


@transaction.atomic
def import_sanluong_chitiet(file_path: str | Path, imported_by=None) -> ImportBatch:
    file_path = Path(file_path)
    df = pd.read_excel(file_path, sheet_name=0)
    df.columns = [str(c).strip() for c in df.columns]

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            f"File {file_path.name} thieu cot bat buoc: {sorted(missing)}. "
            f"Cot doc duoc: {list(df.columns)}"
        )

    dates = df["STATUS_DATE"].map(_parse_status_date).dropna()
    production_date = dates.mode().iloc[0] if not dates.empty else None

    # Idempotent: xoa lan import cu cung ngay (neu co) truoc khi nap lai.
    ImportBatch.objects.filter(production_date=production_date).delete()

    batch = ImportBatch.objects.create(
        source_filename=file_path.name,
        production_date=production_date,
        created_by=imported_by,
    )

    employee_by_postman = {
        e.postman_code: e for e in Employee.objects.exclude(postman_code="")
    }
    mappings = load_active_mappings()

    rows = []
    unmatched = 0
    for _, r in df.iterrows():
        postman_code = clean_cell_text(r.get("POSTMAN_CODE"))
        employee = employee_by_postman.get(postman_code)
        weight_gram = to_float(r.get("KG"))
        service_category = match_service_category(
            mappings,
            service_code=clean_cell_text(r.get("SERVICE_CODE")),
            type_code_payroll=clean_cell_text(r.get("TYPE_CODE_PAYROLL")),
            service_name_payroll=clean_cell_text(r.get("SERVICE_NAME_PAYROLL")),
            area_code=clean_cell_text(r.get("AREA_CODE")),
            weight_gram=weight_gram,
        )
        if employee is None or service_category is None:
            unmatched += 1

        rows.append(
            RawDailyProduction(
                import_batch=batch,
                lading_code=clean_cell_text(r.get("LADING_CODE")),
                postman_code=postman_code,
                route_po_code=clean_cell_text(r.get("ROUTE_PO_CODE")),
                post_office_code=clean_cell_text(r.get("Mã bưu cục")),
                status_code=clean_cell_text(r.get("STATUS_CODE")),
                type_code_payroll=clean_cell_text(r.get("TYPE_CODE_PAYROLL")),
                service_name_payroll=clean_cell_text(r.get("SERVICE_NAME_PAYROLL")),
                area_code=clean_cell_text(r.get("AREA_CODE")),
                service_code=clean_cell_text(r.get("SERVICE_CODE")),
                item_type_code=clean_cell_text(r.get("ITEM_TYPE_CODE")),
                weight_gram=weight_gram,
                quantity=to_float(r.get("QUANTITY")),
                status_date=_parse_status_date(r.get("STATUS_DATE")),
                employee=employee,
                service_category=service_category,
            )
        )

    RawDailyProduction.objects.bulk_create(rows, batch_size=1000)
    batch.row_count = len(rows)
    batch.unmatched_count = unmatched
    batch.save(update_fields=["row_count", "unmatched_count"])
    return batch

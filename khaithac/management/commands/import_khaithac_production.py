"""Import san luong Khai thac theo ca/ngay truc tiep tu SQL Server (bang
chuan Item/TraceItem cua phan mem BCCP), thay vi file Excel nhu module Phat.

Nguon du lieu da duoc xac minh thuc te (xem PROJECT_DECISIONS DEC-016):
  - R_TN/R_COD/R_QT/E_TN/E_COD/E_QT/C_TN/C_COD/C_QT/U_TN/U_COD: database
    BCCP530100_2024, PosCode='530100', TransferMachine<>'530100-HUE'.
  - KT1 (ma buu gui bat dau bang 'M'): database BCCP530900, PosCode='530900',
    TransferMachine='HUE-KTVC-KT1' - day la du lieu THAT (~2.100 buu
    gui/thang), khac voi truy van nham vao BCCP530100_2024 chi ra ~2 dong.

Idempotent theo (post_office, production_date): xoa het dong cu cua ngay do
truoc khi ghi lai, giong import_daily_production.py cua module Phat.

Cach chay:
    python manage.py import_khaithac_production --tu 2026-07-01 --den 2026-08-01
"""
from __future__ import annotations

import datetime as dt
from collections import defaultdict

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import PostOffice
from khaithac.models import KhaiThacImportBatch, KhaiThacRawProduction
from khaithac.services.sql_source import get_connection

POST_OFFICE_CODE = "530100"  # KTC1 Hue 1

# Nguyen van logic UNION ALL da duoc kiem chung dung thuc te (xem
# scratchpad slkt_thang7.sql / DEC-016) - CHI tham so hoa ngay thang, KHONG
# viet lai bang CASE gop vi mot so nhanh (C, U) trong ban goc KHONG loc theo
# ky tu dau ItemCode (da bi comment /*left(itemcode,1) in ('C')*/), viet lai
# sai cho la co the loai bo nham du lieu that.
_CA_EXPR = (
    "CASE WHEN LEFT(REPLACE(CONVERT(VARCHAR,B.TraceDate,114),':',''),4)>='0500' "
    "AND LEFT(REPLACE(CONVERT(VARCHAR,B.TraceDate,114),':',''),4)<='1300' THEN 'CA1' "
    "WHEN LEFT(REPLACE(CONVERT(VARCHAR,B.TraceDate,114),':',''),4)>'1300' "
    "AND LEFT(REPLACE(CONVERT(VARCHAR,B.TraceDate,114),':',''),4)<='2100' THEN 'CA2' "
    "ELSE 'CA3' END"
)

_BRANCHES = [
    ("R_TN", "ServiceCode='R' AND LEFT(A.ItemCode,1) IN ('R','L') AND A.ItemCode IN (SELECT ItemCode FROM dbo.Item WHERE IsDomestic=1) AND A.ItemCode NOT IN (SELECT ItemCode FROM dbo.ValueAddedServiceItem WHERE ValueAddedServiceCode='COD')"),
    ("R_COD", "ServiceCode='R' AND LEFT(A.ItemCode,1) IN ('R','L') AND A.ItemCode IN (SELECT ItemCode FROM dbo.Item WHERE IsDomestic=1) AND A.ItemCode IN (SELECT ItemCode FROM dbo.ValueAddedServiceItem WHERE ValueAddedServiceCode='COD')"),
    ("R_QT", "ServiceCode='R' AND LEFT(A.ItemCode,1) IN ('R','L') AND A.ItemCode IN (SELECT ItemCode FROM dbo.Item WHERE IsDomestic=0)"),
    ("E_TN", "ServiceCode='E' AND LEFT(A.ItemCode,1)='E' AND A.ItemCode IN (SELECT ItemCode FROM dbo.Item WHERE IsDomestic=1) AND A.ItemCode NOT IN (SELECT ItemCode FROM dbo.ValueAddedServiceItem WHERE ValueAddedServiceCode='COD')"),
    ("E_COD", "ServiceCode='E' AND LEFT(A.ItemCode,1)='E' AND A.ItemCode IN (SELECT ItemCode FROM dbo.Item WHERE IsDomestic=1) AND A.ItemCode IN (SELECT ItemCode FROM dbo.ValueAddedServiceItem WHERE ValueAddedServiceCode='COD')"),
    ("E_QT", "ServiceCode='E' AND LEFT(A.ItemCode,1)='E' AND A.ItemCode IN (SELECT ItemCode FROM dbo.Item WHERE IsDomestic=0)"),
    ("C_TN", "ServiceCode='C' AND A.ItemCode IN (SELECT ItemCode FROM dbo.Item WHERE IsDomestic=1) AND A.ItemCode NOT IN (SELECT ItemCode FROM dbo.ValueAddedServiceItem WHERE ValueAddedServiceCode='COD')"),
    ("C_COD", "ServiceCode='C' AND A.ItemCode IN (SELECT ItemCode FROM dbo.Item WHERE IsDomestic=1) AND A.ItemCode IN (SELECT ItemCode FROM dbo.ValueAddedServiceItem WHERE ValueAddedServiceCode='COD')"),
    ("C_QT", "ServiceCode='C' AND A.ItemCode IN (SELECT ItemCode FROM dbo.Item WHERE IsDomestic=0)"),
    ("U_TN", "ServiceCode IN ('U','P') AND A.ItemCode IN (SELECT ItemCode FROM dbo.Item WHERE IsDomestic=1) AND A.ItemCode NOT IN (SELECT ItemCode FROM dbo.ValueAddedServiceItem WHERE ValueAddedServiceCode='COD')"),
    ("U_COD", "ServiceCode IN ('U','P') AND A.ItemCode IN (SELECT ItemCode FROM dbo.Item WHERE IsDomestic=1) AND A.ItemCode IN (SELECT ItemCode FROM dbo.ValueAddedServiceItem WHERE ValueAddedServiceCode='COD')"),
]

_UNION_SQL = "\nUNION ALL\n".join(
    f"""SELECT Loai='{loai}', Ngay=DAY(B.TraceDate), Ca={_CA_EXPR},
    Weight=CASE WHEN A.Weight<=2000 THEN '<=2kg' ELSE '>2kg' END
FROM Item A INNER JOIN TraceItem B ON A.ItemCode=B.ItemCode
WHERE B.Status=2 AND B.PosCode=? AND B.TransferMachine<>'530100-HUE'
  AND B.TraceDate>? AND B.TraceDate<?
  AND A.{where_clause}"""
    for loai, where_clause in _BRANCHES
)

QUERY_530100 = f"""
SELECT Loai, Ngay, Ca, Weight, SoLuong=COUNT(*)
FROM ({_UNION_SQL}) AS ABC
GROUP BY Loai, Ngay, Ca, Weight
"""

QUERY_530900_KT1 = """
SELECT Ngay=DAY(B.TraceDate), Weight=CASE WHEN A.Weight<=2000 THEN '<=2kg' ELSE '>2kg' END,
    B.TraceDate
FROM Item A
INNER JOIN TraceItem B ON A.ItemCode=B.ItemCode
WHERE B.Status=2 AND B.PosCode='530900' AND B.TransferMachine='HUE-KTVC-KT1'
  AND B.TraceDate > ? AND B.TraceDate < ?
  AND LEFT(A.ItemCode,1)='M'
"""


def _ca_from_tracedate(trace_date: dt.datetime) -> str:
    hhmm = trace_date.hour * 100 + trace_date.minute
    if 500 <= hhmm <= 1300:
        return "CA1"
    if 1300 < hhmm <= 2100:
        return "CA2"
    return "CA3"


class Command(BaseCommand):
    help = "Import san luong Khai thac theo ca/ngay tu SQL Server (BCCP530100_2024 + BCCP530900)."

    def add_arguments(self, parser):
        parser.add_argument("--tu", required=True, help="Ngay bat dau, VD 2026-07-01 (bao gom)")
        parser.add_argument("--den", required=True, help="Ngay ket thuc, VD 2026-08-01 (KHONG bao gom)")

    def handle(self, *args, **options):
        tu_ngay = dt.date.fromisoformat(options["tu"])
        den_ngay = dt.date.fromisoformat(options["den"])
        expected_next_month = (tu_ngay.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
        if tu_ngay.day != 1 or den_ngay != expected_next_month:
            raise CommandError(
                "Chi ho tro import tung thang mot: --tu phai la ngay 01 va --den "
                "phai la ngay 01 cua thang ke tiep (VD --tu 2026-07-01 --den 2026-08-01)."
            )

        try:
            post_office = PostOffice.objects.get(code=POST_OFFICE_CODE)
        except PostOffice.DoesNotExist:
            raise CommandError(f"Khong tim thay PostOffice code={POST_OFFICE_CODE}")

        self.stdout.write(f"Dang lay du lieu R/E/C/U tu BCCP530100_2024 ({tu_ngay} -> {den_ngay})...")
        conn1 = get_connection("BCCP530100_2024")
        try:
            cur = conn1.cursor()
            params = [POST_OFFICE_CODE, tu_ngay.isoformat(), den_ngay.isoformat()] * len(_BRANCHES)
            cur.execute(QUERY_530100, params)
            rows_main = cur.fetchall()
        finally:
            conn1.close()

        self.stdout.write(f"Dang lay du lieu KT1 tu BCCP530900 ({tu_ngay} -> {den_ngay})...")
        conn2 = get_connection("BCCP530900")
        try:
            cur = conn2.cursor()
            cur.execute(QUERY_530900_KT1, tu_ngay.isoformat(), den_ngay.isoformat())
            kt1_raw = cur.fetchall()
        finally:
            conn2.close()

        # Gop KT1 theo (Ngay, Ca, Weight) - tinh Ca trong Python vi truy van
        # tho chi lay tung dong TraceDate rieng le.
        kt1_grouped: dict[tuple, int] = defaultdict(int)
        for ngay, weight, trace_date in kt1_raw:
            ca = _ca_from_tracedate(trace_date)
            kt1_grouped[(ngay, ca, weight)] += 1

        # --tu la ngay 01, --den la ngay 01 thang ke tiep (ep buoc o tren),
        # nen DAY(TraceDate) anh xa 1-1 ve ngay trong dung thang cua --tu.
        by_date_ca: dict[dt.date, dict[str, list]] = defaultdict(lambda: defaultdict(list))
        for loai, ngay, ca, weight, so_luong in rows_main:
            by_date_ca[tu_ngay.replace(day=ngay)][ca].append((loai, weight, so_luong))
        for (ngay, ca, weight), so_luong in kt1_grouped.items():
            by_date_ca[tu_ngay.replace(day=ngay)][ca].append(("KT1", weight, so_luong))

        total_rows = 0
        with transaction.atomic():
            for production_date, ca_map in by_date_ca.items():
                batch, _ = KhaiThacImportBatch.objects.update_or_create(
                    post_office=post_office, production_date=production_date,
                    defaults={"row_count": 0, "status": KhaiThacImportBatch.STATUS_OK},
                )
                KhaiThacRawProduction.objects.filter(
                    post_office=post_office, production_date=production_date
                ).delete()
                to_create = []
                for ca, entries in ca_map.items():
                    for loai, weight, so_luong in entries:
                        to_create.append(
                            KhaiThacRawProduction(
                                import_batch=batch, post_office=post_office,
                                production_date=production_date, ca=ca,
                                loai_raw=loai, weight_tier=weight, so_luong=so_luong,
                            )
                        )
                KhaiThacRawProduction.objects.bulk_create(to_create)
                batch.row_count = len(to_create)
                batch.save(update_fields=["row_count"])
                total_rows += len(to_create)

        self.stdout.write(self.style.SUCCESS(
            f"Da import {total_rows} dong (theo ca/ngay/loai/muc can) cho {len(by_date_ca)} ngay."
        ))

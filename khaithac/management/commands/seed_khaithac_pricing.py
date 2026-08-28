"""Seed bang anh xa Loai->Nhom dich vu va bang don gia Khai thac, can cu:

  - VB 1054/TB-BDHUE (11/3/2026, hieu luc tu 01/2026) muc II.1.2: don gia
    goc EMS=300, GHI SO=157, BUU KIEN=392, PHBC=30 (dong/cai).
  - VB 1182/TB-BDHUE (31/3/2026, hieu luc tu 03/2026) dieu chinh:
    EMS=317, GHI SO=167, BUU KIEN=414, PHBC=33 (dong/cai).

12 "Loai" tho (dat ten theo dung script SQL cua don vi) duoc anh xa vao 4
Nhom dich vu theo dinh nghia dich vu (khong phan biet TN/QT/COD trong don
gia Khai thac - khac module Phat):
  - GHI_SO (Bao dam)  <- R_TN, R_COD, R_QT
  - EMS               <- E_TN, E_COD, E_QT
  - BUU_KIEN (Parcel) <- C_TN, C_COD, C_QT
  - PHBC (Bao chi)    <- U_TN, U_COD  (ServiceCode 'U'/'P' = Phat hanh bao chi)

KT1 (ma buu gui bat dau bang 'M') CO CHU DINH de trong (chua anh xa) - VB
1054/1182 khong nhac den mot Nhom rieng cho KT1 trong bang don gia Khai
thac (KT1 trong bang don gia Cong doan PHAT la 1 SAN PHAM rieng, KHAC
nghia voi ma "KT1" dung trong script SQL cua don vi Khai thac cho ma buu
gui prefix 'M' - trung ten ngau nhien). Can PO/TCHC xac nhan KT1(M) thuoc
Nhom nao truoc khi tinh vao Quy tien luong - xem /khai-thac/chua-anh-xa/.
"""
from __future__ import annotations

import datetime as dt

from django.core.management.base import BaseCommand

from khaithac.models import KhaiThacPriceCard, KhaiThacServiceMapping

MAPPING_RULES = {
    "R_TN": KhaiThacServiceMapping.NHOM_GHI_SO,
    "R_COD": KhaiThacServiceMapping.NHOM_GHI_SO,
    "R_QT": KhaiThacServiceMapping.NHOM_GHI_SO,
    "E_TN": KhaiThacServiceMapping.NHOM_EMS,
    "E_COD": KhaiThacServiceMapping.NHOM_EMS,
    "E_QT": KhaiThacServiceMapping.NHOM_EMS,
    "C_TN": KhaiThacServiceMapping.NHOM_BUU_KIEN,
    "C_COD": KhaiThacServiceMapping.NHOM_BUU_KIEN,
    "C_QT": KhaiThacServiceMapping.NHOM_BUU_KIEN,
    "U_TN": KhaiThacServiceMapping.NHOM_PHBC,
    "U_COD": KhaiThacServiceMapping.NHOM_PHBC,
    "KT1": None,  # co chu dinh de trong - xem docstring
}

PRICE_PERIODS = [
    # (nhom, don_gia, hieu_luc_tu, hieu_luc_den, van_ban)
    (KhaiThacServiceMapping.NHOM_EMS, "300", dt.date(2026, 1, 1), dt.date(2026, 2, 28), "VB 1054/TB-BDHUE (11/3/2026)"),
    (KhaiThacServiceMapping.NHOM_GHI_SO, "157", dt.date(2026, 1, 1), dt.date(2026, 2, 28), "VB 1054/TB-BDHUE (11/3/2026)"),
    (KhaiThacServiceMapping.NHOM_BUU_KIEN, "392", dt.date(2026, 1, 1), dt.date(2026, 2, 28), "VB 1054/TB-BDHUE (11/3/2026)"),
    (KhaiThacServiceMapping.NHOM_PHBC, "30", dt.date(2026, 1, 1), dt.date(2026, 2, 28), "VB 1054/TB-BDHUE (11/3/2026)"),
    (KhaiThacServiceMapping.NHOM_EMS, "317", dt.date(2026, 3, 1), None, "VB 1182/TB-BDHUE (31/3/2026)"),
    (KhaiThacServiceMapping.NHOM_GHI_SO, "167", dt.date(2026, 3, 1), None, "VB 1182/TB-BDHUE (31/3/2026)"),
    (KhaiThacServiceMapping.NHOM_BUU_KIEN, "414", dt.date(2026, 3, 1), None, "VB 1182/TB-BDHUE (31/3/2026)"),
    (KhaiThacServiceMapping.NHOM_PHBC, "33", dt.date(2026, 3, 1), None, "VB 1182/TB-BDHUE (31/3/2026)"),
]


class Command(BaseCommand):
    help = "Seed KhaiThacServiceMapping + KhaiThacPriceCard tu VB1054 + VB1182."

    def handle(self, *args, **options):
        for loai_raw, nhom in MAPPING_RULES.items():
            obj, created = KhaiThacServiceMapping.objects.update_or_create(
                loai_raw=loai_raw,
                defaults={
                    "nhom_dich_vu": nhom,
                    "note": "" if nhom else "Chua xac dinh Nhom - can PO/TCHC xac nhan (xem docstring seed command).",
                },
            )
            self.stdout.write(f"  {'+' if created else '~'} {obj}")

        for nhom, gia, tu_ngay, den_ngay, van_ban in PRICE_PERIODS:
            obj, created = KhaiThacPriceCard.objects.update_or_create(
                nhom_dich_vu=nhom, effective_from=tu_ngay,
                defaults={"unit_price": gia, "effective_to": den_ngay, "source_document": van_ban},
            )
            self.stdout.write(f"  {'+' if created else '~'} {obj}")

        self.stdout.write(self.style.SUCCESS(
            f"Da seed {len(MAPPING_RULES)} anh xa Loai va {len(PRICE_PERIODS)} dong don gia."
        ))

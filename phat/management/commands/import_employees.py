"""Nap danh sach nhan su that (file 'DS nhan su TTVH') vao Employee.

Quy tac chuan hoa "Don vi" -> PostOffice, theo xac nhan truc tiep cua
Product Owner ngay 2026-08-27 (xem PROJECT_DECISIONS.md DEC-010):

- "BCVH Thuan Hoa" / "BCVH Thuan Hoa" (2 cach go dau khac nhau trong
  file goc) deu la 1 buu cuc, ma 533140.
- "Buu cuc Khai thac" = KTC1 Hue 1 (ma 530100) - TRU 8 nguoi lam cong
  viec "200 - Cong nhan van chuyen buu chinh" duoc PO chi dinh chuyen
  ve BCVH Thuan Hoa (533140) thay vi KTC1.
- "TRUNG TAM VAN HANH" (8 nguoi) la nhan su quan ly cap trung tam (quan
  ly tat ca cac BC, khong thuoc rieng buu cuc nao) - tao 1 PostOffice
  dai dien ma 'TTVH' de gan vao, khong phai buu cuc phat that.

Ma buu ta (POSTMAN_CODE, dung de khop voi du lieu san luong tho) KHONG
co san trong file nhan su nay - duoc bo sung tu du lieu that cua thang
03/2026 (sheet TH-TP-Chot trong file BatchFile cu) khi tim thay theo Ma
HRM; con lai de trong, se tu dong khop duoc khi lan import du lieu san
luong tiep theo neu Mã bưu ta xuat hien dung.
"""
from pathlib import Path

import openpyxl
from django.core.management.base import BaseCommand

from core.models import Employee, PostOffice

DEFAULT_FILE = Path(r"D:\ONEDRIVE\Trung tam Van hanh - BDTP Hue 05.2025\2026\Lao dong\DS nhân sự TTVH (27.8.2026).xlsx")

# Chuyen van chuyen: theo chi dao truc tiep cua PO - 7 nguoi nay thuoc
# "Buu cuc Khai thac" trong file goc nhung duoc dua ve BCVH Thuan Hoa
# voi chuc danh rieng. (Luu y: PO ban dau gui danh sach co 8 ten kem
# "00273849 - TRUONG VAN DUNG", sau do xac nhan lai chi dung 7 nguoi,
# khong bao gom Truong Van Dung - nguoi nay o lai Buu cuc Khai thac.)
TRANSPORT_WORKER_HRM_CODES = {
    "00266919", "00262607", "00267222",
    "00272438", "00252099", "00238601", "00264613",
}
TRANSPORT_WORKER_POSITION = "200 - Công nhân vận chuyển bưu chính"
TRANSPORT_WORKER_POST_OFFICE_CODE = "533140"

DON_VI_TO_POST_OFFICE_CODE = {
    "bcvh thuận hóa": "533140",
    "bcvh thuận hoá": "533140",
    "bcvh hương trà": "535470",
    "bcvh a lưới": "535790",
    "bcvh hương thủy": "536250",
    "bcvh thuận an": "537015",
    "bcvh phú lộc": "537220",
    "bưu cục khai thác": "530100",
    "trung tâm vận hành": "TTVH",
}


def normalize_hrm(value) -> str:
    text = str(value or "").strip()
    if text.endswith(".0"):
        text = text[:-2]
    return text.zfill(8)


def guess_contract_type(loai_hd_text: str) -> str:
    text = (loai_hd_text or "").lower()
    if "thuê khoán" in text:
        return Employee.CONTRACT_LDTK
    if "hđlđ" in text or "hop dong lao dong" in text:
        return Employee.CONTRACT_HDLD
    return ""


class Command(BaseCommand):
    help = "Nap danh sach nhan su that vao Employee (idempotent theo Ma HRM)."

    def add_arguments(self, parser):
        parser.add_argument("--file", dest="file", default=str(DEFAULT_FILE))
        parser.add_argument(
            "--postman-map", dest="postman_map", default=None,
            help="File .xlsb/.xlsx co sheet TH-TP-Chot de bo sung Ma buu ta theo Ma HRM (tuy chon).",
        )

    def handle(self, *args, **options):
        file_path = Path(options["file"])
        if not file_path.exists():
            self.stderr.write(self.style.ERROR(f"Khong tim thay file: {file_path}"))
            return

        ttvh_office, _ = PostOffice.objects.get_or_create(
            code="TTVH", defaults={"name": "Trung tâm Vận hành (quản lý)", "area": "Quản lý"}
        )
        offices_by_code = {po.code: po for po in PostOffice.objects.all()}
        if "TTVH" not in offices_by_code:
            offices_by_code["TTVH"] = ttvh_office

        wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        ws = wb["Tổng"]
        rows = list(ws.iter_rows(values_only=True))

        created, updated, skipped = 0, 0, 0
        for r in rows[1:]:
            hrm_raw = r[1]
            if not hrm_raw:
                continue
            hrm_code = normalize_hrm(hrm_raw)
            full_name = str(r[2] or "").strip()
            loai_hd_text = r[9]
            don_vi = str(r[10] or "").strip()

            don_vi_key = don_vi.lower()
            office_code = DON_VI_TO_POST_OFFICE_CODE.get(don_vi_key)
            position = str(r[7] or "").strip()

            if hrm_code in TRANSPORT_WORKER_HRM_CODES:
                office_code = TRANSPORT_WORKER_POST_OFFICE_CODE
                position = TRANSPORT_WORKER_POSITION

            office = offices_by_code.get(office_code) if office_code else None
            if office is None:
                self.stderr.write(self.style.WARNING(
                    f"Bo qua {hrm_code} - {full_name}: khong xac dinh duoc buu cuc tu 'Don vi'={don_vi!r}"
                ))
                skipped += 1
                continue

            obj, was_created = Employee.objects.update_or_create(
                hrm_code=hrm_code,
                defaults={
                    "full_name": full_name,
                    "post_office": office,
                    "contract_type": guess_contract_type(loai_hd_text),
                    "position": position,
                    "is_active": True,
                },
            )
            created += 1 if was_created else 0
            updated += 0 if was_created else 1

        self.stdout.write(self.style.SUCCESS(
            f"Da nap nhan su: {created} moi, {updated} cap nhat, {skipped} bo qua."
        ))

        postman_map_file = options.get("postman_map")
        if postman_map_file:
            n = self._backfill_postman_code(Path(postman_map_file))
            self.stdout.write(self.style.SUCCESS(f"Da bo sung Ma buu ta cho {n} nhan vien."))

    def _backfill_postman_code(self, path: Path) -> int:
        """Doc sheet 'mã BT' (Ma HRM/Ma buu ta/Ten buu ta) tu 1 file
        BatchFile cu (.xlsb) de bo sung Ma buu ta con thieu.

        GHI CHU QUAN TRONG (phat hien 2026-08-27, xem PROJECT_DECISIONS.md
        DEC-011): ma buu ta co the thay doi theo thoi gian (doi tuyen).
        Ban dau dung sheet 'TH-TP-Chot' cua file thang 03/2026 de bo sung,
        nhung sau doi chieu voi du lieu that thang 08/2026 phat hien 7
        truong hop ma da loi thoi (khong con xuat hien trong du lieu that,
        trong khi ten nguoi van dung o 1 ma KHAC). Sheet 'mã BT' cua file
        thang 04/2026 (gan voi hien tai hon) da duoc doi chieu lai bang
        ten va khop dung 100% (115/115) - nen dung sheet nay lam nguon
        chuan thay vi 'TH-TP-Chot'. Neu nghi ngo du lieu lai loi thoi lan
        nua, doi chieu ten (khong chi ma) truoc khi tin tuong."""
        import pyxlsb

        mapping = {}
        with pyxlsb.open_workbook(str(path)) as wb:
            with wb.get_sheet("mã BT") as sheet:
                for i, row in enumerate(sheet.rows()):
                    if i < 3:
                        continue
                    vals = [c.v for c in row]
                    if len(vals) < 5 or not vals[3] or not vals[4]:
                        continue
                    mapping[normalize_hrm(vals[3])] = str(vals[4]).strip()

        n = 0
        for emp in Employee.objects.filter(postman_code=""):
            postman = mapping.get(emp.hrm_code)
            if postman:
                emp.postman_code = postman
                emp.save(update_fields=["postman_code"])
                n += 1
        return n

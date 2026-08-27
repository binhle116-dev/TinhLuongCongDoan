from django.core.management.base import BaseCommand

from phat.models import AllowanceType

# Day la danh muc khoan ho tro co cong thuc/muc khoan da ro rang, doc duoc
# tu ho so cua don vi (tham khao tu cac ban tinh luong cong phat truoc
# day) - KHONG lien quan den bang gia/anh xa dich vu (phan do van dang
# chua duoc TCHC/TCKH xac nhan va PHAI de trong cho Admin tu cau hinh).
ALLOWANCE_TYPES = [
    dict(code="truc-gia-tuyen", name="Luong co dinh tuyen phat dac biet kho khan", default_unit_price=None, unit_label="thang"),
    dict(code="truc-dem-tui-goi", name="Truc dem giao nhan tui goi", default_unit_price=4_000_000, unit_label="thang cong chuan"),
    # Don gia 2 khoan duoi day bien dong theo tung thang (khong co muc co
    # dinh chinh thuc) - de trong, Truong buu cuc phai tu dien don gia
    # thuc te cua thang khi nhap.
    dict(code="ho-tro-san-bay", name="Ho tro nhan hang san bay", default_unit_price=None, unit_label="tui"),
    dict(code="ho-tro-ngoai-gio", name="Ho tro phat ngoai gio HC", default_unit_price=None, unit_label="buu gui"),
]


class Command(BaseCommand):
    help = "Tao danh muc khoan ho tro mac dinh (AllowanceType) neu chua co."

    def handle(self, *args, **options):
        for item in ALLOWANCE_TYPES:
            obj, created = AllowanceType.objects.get_or_create(code=item["code"], defaults=item)
            self.stdout.write(("Da tao: " if created else "Da co san: ") + obj.name)

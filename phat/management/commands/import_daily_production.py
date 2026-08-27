from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from phat.services.importer import import_sanluong_chitiet
from phat.services.pricing import compute_provisional_pay


class Command(BaseCommand):
    help = (
        "Import file SanLuongChiTiet_DDMMYYYY.xlsx moi nhat (hoac file chi dinh) "
        "vao RawDailyProduction, sau do tinh lai 'tam tinh' cho thang tuong ung."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--file", dest="file", default=None,
            help="Duong dan file cu the. Neu bo qua, tu quet file SanLuongChiTiet_*.xlsx moi nhat trong SANLUONG_PHAT_DIR.",
        )

    def handle(self, *args, **options):
        file_path = options.get("file")
        if file_path:
            target = Path(file_path)
        else:
            source_dir = Path(settings.SANLUONG_PHAT_DIR)
            candidates = sorted(
                (p for p in source_dir.glob("SanLuongChiTiet_*.xlsx") if not p.name.startswith("~$")),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if not candidates:
                self.stderr.write(self.style.ERROR(f"Khong tim thay file SanLuongChiTiet_*.xlsx trong {source_dir}"))
                return
            target = candidates[0]

        self.stdout.write(f"Dang import: {target}")
        batch = import_sanluong_chitiet(target)
        self.stdout.write(
            self.style.SUCCESS(
                f"Import xong: {batch.row_count} dong, {batch.unmatched_count} dong chua anh xa duoc "
                f"(ngay {batch.production_date})"
            )
        )

        if batch.production_date:
            run = compute_provisional_pay(batch.production_date.year, batch.production_date.month)
            self.stdout.write(self.style.SUCCESS(f"Da tinh lai tam tinh cho {run}"))

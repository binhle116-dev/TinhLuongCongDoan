import datetime as dt
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection

KEEP_DAYS = 30


class Command(BaseCommand):
    help = "Sao luu an toan file SQLite (VACUUM INTO) - chay hang dem qua Task Scheduler."

    def handle(self, *args, **options):
        backup_dir = Path(settings.BASE_DIR) / "backups"
        backup_dir.mkdir(exist_ok=True)
        today = dt.date.today().strftime("%Y%m%d")
        out_path = backup_dir / f"backup-{today}.sqlite3"

        with connection.cursor() as cursor:
            cursor.execute(f"VACUUM INTO '{out_path.as_posix()}'")
        self.stdout.write(self.style.SUCCESS(f"Da sao luu: {out_path}"))

        cutoff = dt.date.today() - dt.timedelta(days=KEEP_DAYS)
        for f in backup_dir.glob("backup-*.sqlite3"):
            try:
                file_date = dt.datetime.strptime(f.stem.replace("backup-", ""), "%Y%m%d").date()
            except ValueError:
                continue
            if file_date < cutoff:
                f.unlink()
                self.stdout.write(f"Da xoa backup cu: {f.name}")

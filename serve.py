"""Chay webapp bang waitress (WSGI server on dinh, dung cho mang noi bo).

Cach chay:
    python serve.py

Mac dinh lang nghe tren 0.0.0.0:8000 - moi may trong mang LAN/VPN cua don
vi truy cap duoc qua http://<IP hoac ten may nay>:8000/
"""
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "payroll.settings")

import django  # noqa: E402

django.setup()

from waitress import serve  # noqa: E402
from django.core.wsgi import get_wsgi_application  # noqa: E402

if __name__ == "__main__":
    application = get_wsgi_application()
    print("Dang chay tai http://0.0.0.0:8000/ (Ctrl+C de dung)")
    serve(application, host="0.0.0.0", port=8000, threads=8)

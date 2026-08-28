r"""Ket noi truc tiep den SQL Server cua phan mem BCCP de lay san luong Khai
thac theo ca/ngay (khac module Phat, doc file Excel tu SFTP).

AN TOAN MAT KHAU: mat khau SQL Server KHONG duoc luu duoi dang van ban va
KHONG BAO GIO duoc in/log ra. File
"%USERPROFILE%\\.khaithac_sql_pw.txt" duoc chinh nguoi dung tao trong
PowerShell rieng cua ho bang:

    $cred = Get-Credential -UserName sa
    $cred.Password | ConvertFrom-SecureString | Set-Content "$env:USERPROFILE\.khaithac_sql_pw.txt"

Day la 1 chuoi hex cua blob DPAPI (Windows Data Protection API), chi giai ma
duoc boi dung user + dung may da tao no. Ham giai_ma_mat_khau() o day dung
pywin32 (win32crypt.CryptUnprotectData) de giai ma trong bo nho ngay truoc
khi mo ket noi, khong ghi ra bat ky dau (khong print, khong log, khong luu
lai bien module-level)."""
from __future__ import annotations

import codecs
import os

import pyodbc

SQL_SERVER_HOST = "10.47.31.30"
SQL_SERVER_USER = "sa"
PASSWORD_FILE = os.path.join(os.path.expanduser("~"), ".khaithac_sql_pw.txt")


def _decrypt_password() -> str:
    import win32crypt  # import cuc bo: chi may Windows co pywin32 moi can

    with open(PASSWORD_FILE, "r", encoding="ascii") as f:
        hex_blob = f.read().strip()
    blob = codecs.decode(hex_blob, "hex")
    _desc, plain_bytes = win32crypt.CryptUnprotectData(blob, None, None, None, 0)
    if isinstance(plain_bytes, bytes):
        return plain_bytes.decode("utf-16-le", errors="ignore").rstrip("\x00") if b"\x00" in plain_bytes else plain_bytes.decode()
    return plain_bytes


def get_connection(database: str) -> pyodbc.Connection:
    """Mo 1 ket noi moi toi 1 database cu the. Goi ham nay trong 'with' hoac
    dong ket noi ngay sau khi dung xong - khong giu ket noi lau dai."""
    password = _decrypt_password()
    try:
        conn_str = (
            f"DRIVER={{SQL Server Native Client 11.0}};"
            f"SERVER={SQL_SERVER_HOST};DATABASE={database};"
            f"UID={SQL_SERVER_USER};PWD={password};TrustServerCertificate=yes;"
        )
        return pyodbc.connect(conn_str, timeout=15)
    finally:
        password = None  # xoa tham chieu ngay sau khi dung, khong giu trong bien lau dai

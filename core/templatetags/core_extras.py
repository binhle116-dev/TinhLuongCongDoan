"""Dinh dang so theo chuan Viet Nam (dau cham phan nhom nghin, dau phay
thap phan) + vai tien ich template nho, dung chung cho cac trang can
trinh bay lai du lieu dep hon (Khai thac, Phat...). Chuyen tu
khaithac/templatetags sang day (DEC-025) de dung duoc o ca 2 module thay
vi trung lap code."""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from django import template

register = template.Library()


def _to_number(value):
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


@register.filter
def vn_number(value, decimals=0):
    """1234567 -> '1.234.567'. vn_number:2 -> '1.234.567,89'."""
    number = _to_number(value)
    if number is None:
        return "-"
    decimals = int(decimals)
    quant = Decimal(1).scaleb(-decimals) if decimals else Decimal(1)
    # ROUND_HALF_UP (lam tron thuong mai) thay vi mac dinh ROUND_HALF_EVEN
    # cua Decimal - nguoi dung VN mong doi 8,45% hien thi thanh 8,5%, khong
    # phai 8,4% (lam tron ve so chan).
    number = number.quantize(quant, rounding=ROUND_HALF_UP)
    sign = "-" if number < 0 else ""
    number = abs(number)
    int_part, _, dec_part = f"{number:.{decimals}f}".partition(".")
    grouped = f"{int(int_part):,}".replace(",", ".")
    return f"{sign}{grouped},{dec_part}" if decimals else f"{sign}{grouped}"


@register.filter
def vn_currency(value):
    """1234567 -> '1.234.567 ₫'."""
    number = _to_number(value)
    if number is None:
        return "-"
    return f"{vn_number(number)} ₫"


@register.filter
def vn_signed_percent(value):
    """0.1523 -> '+15,2%'; -0.083 -> '-8,3%'. Dung cho % thay doi so ky truoc."""
    number = _to_number(value)
    if number is None:
        return None
    pct = number * 100
    sign = "+" if pct > 0 else ("-" if pct < 0 else "")
    return f"{sign}{vn_number(abs(pct), 1)}%"


@register.filter
def dict_get(mapping, key):
    if not mapping:
        return None
    return mapping.get(key)


@register.filter
def split(value, sep=","):
    return str(value).split(sep)

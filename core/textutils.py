"""Tien ich chuan hoa text/so - dung chung cho tat ca module cong doan."""
import re
import unicodedata

import pandas as pd


def normalize_text(value) -> str:
    text = str(value or "").strip().lower()
    text = text.replace("đ", "d").replace("Đ", "d")
    text = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def clean_cell_text(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    return "" if text in {"nan", "None"} else text


def to_float(value) -> float:
    parsed = pd.to_numeric(value, errors="coerce")
    if pd.isna(parsed):
        return 0.0
    return float(parsed)

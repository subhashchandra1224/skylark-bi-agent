import pandas as pd
import numpy as np

def normalize_text(text) -> str:
    if pd.isna(text) or text is None or str(text).strip() == "":
        return "Unknown"
    return str(text).strip()

def normalize_probability(prob) -> float:
    if pd.isna(prob) or prob is None:
        return 0.0
    prob_str = str(prob).strip().lower()
    if prob_str == "high": return 0.75
    if prob_str == "medium": return 0.50
    if prob_str == "low": return 0.25
    return 0.0 # Unknown probability

def parse_currency(value) -> float:
    if pd.isna(value) or value is None or str(value).strip() == "":
        return 0.0
    try:
        val_str = str(value).replace(',', '').replace('$', '').replace('€', '').strip()
        return float(val_str)
    except ValueError:
        return 0.0

def parse_date(date_val) -> pd.Timestamp:
    """Safely parse dates. Returns pd.NaT if invalid."""
    if pd.isna(date_val) or date_val is None or str(date_val).strip() == "":
        return pd.NaT
    try:
        # Remove (Coordinated Universal Time) and similar bracketed tz info which breaks pd.to_datetime
        clean_date = str(date_val)
        if "(" in clean_date and ")" in clean_date:
            clean_date = clean_date.split("(")[0].strip()
        return pd.to_datetime(clean_date, errors='coerce')
    except Exception:
        return pd.NaT

def normalize_status(status) -> str:
    """Basic normalization for statuses (e.g., lowercase, trimmed)"""
    if pd.isna(status) or status is None or str(status).strip() == "":
        return "Unknown"
    return str(status).strip()

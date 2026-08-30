import pandas as pd
from app.services.normalization_service import parse_currency, normalize_probability, parse_date

def test_parse_currency():
    assert parse_currency("$5,000") == 5000.0
    assert parse_currency("1000") == 1000.0
    assert parse_currency("") == 0.0
    assert parse_currency(None) == 0.0
    assert parse_currency("Invalid") == 0.0

def test_normalize_probability():
    assert normalize_probability("High") == 0.75
    assert normalize_probability("Medium") == 0.5
    assert normalize_probability("Low") == 0.25
    assert normalize_probability("Won") == 0.0
    assert normalize_probability("") == 0.0
    assert normalize_probability(None) == 0.0

def test_parse_date():
    assert parse_date("2023-01-01 (Coordinated Universal Time)") == pd.Timestamp("2023-01-01")
    assert parse_date("2023-01-01") == pd.Timestamp("2023-01-01")
    assert pd.isna(parse_date(None))

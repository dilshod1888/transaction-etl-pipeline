from pathlib import Path

import pandas as pd
import pytest

from src.extract import extract_csv
from src.main import main
from src.transform import clean_transactions

SAMPLE = Path(__file__).resolve().parents[1] / "sample_data" / "transactions_sample.csv"


def make_df(rows):
    cols = ["transaction_id", "transaction_date", "merchant_id", "transaction_type", "amount", "currency"]
    return pd.DataFrame(rows, columns=cols).astype(str)


def test_extract_reads_sample():
    df = extract_csv(SAMPLE)
    assert len(df) == 15


def test_extract_missing_file():
    with pytest.raises(FileNotFoundError):
        extract_csv("does_not_exist.csv")


def test_extract_missing_columns(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("transaction_id,amount\nT1,10\n")
    with pytest.raises(ValueError, match="Missing required columns"):
        extract_csv(bad)


def test_sample_rejection_report():
    clean, report = clean_transactions(extract_csv(SAMPLE))
    assert report.rows_in == 15
    assert report.rows_out == 8
    assert report.rejected == {
        "missing_field": 2,
        "invalid_date": 1,
        "invalid_amount": 1,
        "negative_amount": 1,
        "unknown_type": 1,
        "duplicate": 1,
    }
    assert clean["transaction_id"].is_unique


def test_missing_id_is_rejected_not_stored_as_nan():
    df = pd.DataFrame(
        {
            "transaction_id": [None, "T2"],
            "transaction_date": ["2026-10-01", "2026-10-01"],
            "merchant_id": ["M1", "M1"],
            "transaction_type": ["PAYMENT", "PAYMENT"],
            "amount": ["10", "20"],
            "currency": ["UZS", "UZS"],
        }
    )
    clean, report = clean_transactions(df)
    assert list(clean["transaction_id"]) == ["T2"]
    assert "nan" not in clean["transaction_id"].tolist()


def test_normalises_text_and_decimal_comma():
    clean, _ = clean_transactions(
        make_df([["T1", "2026-10-01 09:00:00", " M4 ", "payment", "412000,25", "uzs"]])
    )
    row = clean.iloc[0]
    assert row["merchant_id"] == "M4"
    assert row["transaction_type"] == "PAYMENT"
    assert row["currency"] == "UZS"
    assert row["amount"] == pytest.approx(412000.25)


def test_duplicate_keeps_last():
    clean, report = clean_transactions(
        make_df(
            [
                ["T1", "2026-10-01", "M1", "PAYMENT", "10", "UZS"],
                ["T1", "2026-10-01", "M1", "PAYMENT", "99", "UZS"],
            ]
        )
    )
    assert len(clean) == 1
    assert clean.iloc[0]["amount"] == 99
    assert report.rejected == {"duplicate": 1}


def test_cli_dry_run():
    assert main(["--input", str(SAMPLE), "--dry-run"]) == 0

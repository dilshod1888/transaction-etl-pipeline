"""Extract step: read raw transaction CSV files."""
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {
    "transaction_id",
    "transaction_date",
    "merchant_id",
    "transaction_type",
    "amount",
    "currency",
}


def extract_csv(file_path: str | Path) -> pd.DataFrame:
    """Read a CSV file as strings and verify that all required columns exist."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df.columns = [c.strip().lower() for c in df.columns]

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    return df

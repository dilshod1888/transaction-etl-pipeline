"""Transform step: validate, clean and de-duplicate transactions."""
from dataclasses import dataclass, field

import pandas as pd

TEXT_COLUMNS = ["transaction_id", "merchant_id", "transaction_type", "currency"]
VALID_TYPES = {"PAYMENT", "TRANSFER", "REFUND", "WITHDRAWAL"}


@dataclass
class TransformReport:
    rows_in: int = 0
    rows_out: int = 0
    rejected: dict[str, int] = field(default_factory=dict)

    @property
    def rows_rejected(self) -> int:
        return self.rows_in - self.rows_out


def _reject(df: pd.DataFrame, mask: pd.Series, reason: str, report: TransformReport) -> pd.DataFrame:
    count = int(mask.sum())
    if count:
        report.rejected[reason] = report.rejected.get(reason, 0) + count
    return df[~mask]


def clean_transactions(df: pd.DataFrame) -> tuple[pd.DataFrame, TransformReport]:
    """Return cleaned rows and a report describing what was rejected and why."""
    report = TransformReport(rows_in=len(df))
    result = df.copy()

    for col in TEXT_COLUMNS:
        # Keep real missing values as NA instead of turning them into the text "nan".
        result[col] = result[col].astype("string").str.strip().replace("", pd.NA)
    result["transaction_type"] = result["transaction_type"].str.upper()
    result["currency"] = result["currency"].str.upper()

    result["transaction_date"] = pd.to_datetime(result["transaction_date"], errors="coerce")
    result["amount"] = pd.to_numeric(
        result["amount"].astype("string").str.strip().str.replace(",", ".", regex=False),
        errors="coerce",
    )

    result = _reject(result, result[TEXT_COLUMNS].isna().any(axis=1), "missing_field", report)
    result = _reject(result, result["transaction_date"].isna(), "invalid_date", report)
    result = _reject(result, result["amount"].isna(), "invalid_amount", report)
    result = _reject(result, result["amount"] < 0, "negative_amount", report)
    result = _reject(result, ~result["transaction_type"].isin(VALID_TYPES), "unknown_type", report)
    result = _reject(result, result["currency"].str.len() != 3, "invalid_currency", report)
    result = _reject(
        result, result.duplicated(subset=["transaction_id"], keep="last"), "duplicate", report
    )

    result["amount"] = result["amount"].round(2)
    result = result.reset_index(drop=True)
    report.rows_out = len(result)
    return result, report

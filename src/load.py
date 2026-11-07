"""Load step: stage rows in PostgreSQL and upsert them into the target table."""
from sqlalchemy import text
from sqlalchemy.engine import Engine
import pandas as pd

UPSERT_SQL = text(
    """
    INSERT INTO transactions (
        transaction_id, transaction_date, merchant_id,
        transaction_type, amount, currency, source_file
    )
    SELECT DISTINCT ON (transaction_id)
        transaction_id, transaction_date, merchant_id,
        transaction_type, amount, currency, source_file
    FROM transactions_stage
    WHERE source_file = :source_file
    ORDER BY transaction_id, loaded_at DESC
    ON CONFLICT (transaction_id) DO UPDATE SET
        transaction_date = EXCLUDED.transaction_date,
        merchant_id      = EXCLUDED.merchant_id,
        transaction_type = EXCLUDED.transaction_type,
        amount           = EXCLUDED.amount,
        currency         = EXCLUDED.currency,
        source_file      = EXCLUDED.source_file,
        loaded_at        = CURRENT_TIMESTAMP
    """
)


def load_transactions(df: pd.DataFrame, engine: Engine, source_file: str) -> int:
    """Load cleaned rows in one transaction. Returns the number of rows loaded."""
    if df.empty:
        return 0

    staged = df.copy()
    staged["source_file"] = source_file

    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM transactions_stage WHERE source_file = :f"), {"f": source_file}
        )
        staged.to_sql(
            "transactions_stage",
            conn,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=5000,
        )
        conn.execute(UPSERT_SQL, {"source_file": source_file})
        conn.execute(
            text("DELETE FROM transactions_stage WHERE source_file = :f"), {"f": source_file}
        )

    return len(staged)

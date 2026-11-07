"""Command-line entry point for the transaction ETL pipeline.

Usage:
    python -m src.main --input sample_data/transactions_sample.csv
    python -m src.main --input sample_data/transactions_sample.csv --dry-run
"""
import argparse
import logging
import os
import sys
from pathlib import Path

from .extract import extract_csv
from .transform import clean_transactions

log = logging.getLogger("etl")


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load transaction CSV files into PostgreSQL.")
    parser.add_argument("--input", required=True, help="Path to the source CSV file")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and clean only; do not connect to the database",
    )
    return parser.parse_args(argv)


def _start_log(conn, source_file: str) -> int:
    from sqlalchemy import text

    return conn.execute(
        text(
            "INSERT INTO etl_import_log (source_file, status) "
            "VALUES (:f, 'RUNNING') RETURNING id"
        ),
        {"f": source_file},
    ).scalar_one()


def _finish_log(conn, log_id: int, status: str, rows_read=0, rows_loaded=0, error=None) -> None:
    from sqlalchemy import text

    conn.execute(
        text(
            "UPDATE etl_import_log SET finished_at = CURRENT_TIMESTAMP, status = :s, "
            "rows_read = :r, rows_loaded = :l, error_message = :e WHERE id = :id"
        ),
        {"s": status, "r": rows_read, "l": rows_loaded, "e": error, "id": log_id},
    )


def run(input_path: str, dry_run: bool = False) -> int:
    source_file = Path(input_path).name

    if dry_run:
        raw = extract_csv(input_path)
        clean, report = clean_transactions(raw)
        log.info("Read %d rows, %d valid, %d rejected", report.rows_in, report.rows_out, report.rows_rejected)
        for reason, count in report.rejected.items():
            log.info("  rejected %-17s %d", reason, count)
        log.info("Dry run: nothing written to the database")
        return 0

    from dotenv import load_dotenv
    from sqlalchemy import create_engine

    from .load import load_transactions

    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        log.error("DATABASE_URL is not set. Copy .env.example to .env and configure it.")
        return 2

    engine = create_engine(database_url)
    with engine.begin() as conn:
        log_id = _start_log(conn, source_file)

    rows_read = 0
    try:
        raw = extract_csv(input_path)
        rows_read = len(raw)
        clean, report = clean_transactions(raw)
        for reason, count in report.rejected.items():
            log.warning("Rejected %d rows: %s", count, reason)
        loaded = load_transactions(clean, engine, source_file)
    except Exception as exc:  # record every failure in the import log
        log.exception("ETL failed for %s", source_file)
        with engine.begin() as conn:
            _finish_log(conn, log_id, "FAILED", rows_read=rows_read, error=str(exc)[:2000])
        return 1

    with engine.begin() as conn:
        _finish_log(conn, log_id, "SUCCESS", rows_read=rows_read, rows_loaded=loaded)
    log.info("Loaded %d of %d rows from %s", loaded, rows_read, source_file)
    return 0


def main(argv=None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = parse_args(argv)
    return run(args.input, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())

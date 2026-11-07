# Transaction ETL Pipeline

![tests](https://github.com/dilshod1888/transaction-etl-pipeline/actions/workflows/tests.yml/badge.svg)

A production-style Python ETL pipeline that loads transaction CSV files into PostgreSQL with validation, cleaning, duplicate detection and an execution log.

> All data in this repository is synthetic.

## Pipeline

```
CSV file
   ↓  extract.py    – read as text, check required columns
   ↓  transform.py  – trim/normalise, parse dates & amounts, reject bad rows, de-duplicate
   ↓  load.py       – stage → upsert into target table in one DB transaction
PostgreSQL
   ↓  main.py       – CLI, logging, run status written to etl_import_log
```

## Features

- Required-column check on ingestion
- Cleaning: whitespace trimming, upper-casing codes, decimal-comma amounts (`412000,25`)
- Validation with a rejection report by reason: missing field, invalid date, invalid amount, negative amount, unknown type, invalid currency, duplicate
- Duplicate detection (last occurrence wins)
- Idempotent load: staging table + `INSERT … ON CONFLICT DO UPDATE`, safe to re-run the same file
- Every run is recorded in `etl_import_log` (status, rows read, rows loaded, error message)
- `--dry-run` mode to validate a file without a database
- Unit tests + GitHub Actions CI

## Tech Stack

Python · pandas · SQLAlchemy · PostgreSQL · pytest

## Quick Start

```bash
pip install -r requirements.txt

# 1. Validate the sample file without a database
python -m src.main --input sample_data/transactions_sample.csv --dry-run

# 2. Load into PostgreSQL
psql -d transactions_db -f sql/create_tables.sql
cp .env.example .env          # set DATABASE_URL
python -m src.main --input sample_data/transactions_sample.csv
```

Dry-run output on the sample file (15 rows, deliberately includes dirty data):

```
INFO Read 15 rows, 8 valid, 7 rejected
INFO   rejected missing_field     2
INFO   rejected invalid_date      1
INFO   rejected invalid_amount    1
INFO   rejected negative_amount   1
INFO   rejected unknown_type      1
INFO   rejected duplicate         1
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

## Project Structure

```
transaction-etl-pipeline/
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── main.py
├── sql/create_tables.sql
├── sample_data/transactions_sample.csv
├── tests/test_pipeline.py
└── .github/workflows/tests.yml
```

## Portfolio Note

Built as a portfolio project demonstrating ETL design, data quality checks and PostgreSQL loading for payment/transaction data.

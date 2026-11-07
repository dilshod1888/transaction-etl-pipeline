# Transaction ETL Pipeline

A production-style Python ETL pipeline for processing transaction data from CSV files into PostgreSQL.

## Overview
**CSV → Validation → Cleaning → Duplicate Detection → PostgreSQL → Execution Logging**

This project uses synthetic data only.

## Features
- CSV transaction ingestion
- Data validation and cleaning
- Duplicate detection
- Batch loading into PostgreSQL
- Staging-to-target loading
- Execution logging and error handling

## Tech Stack
Python · PostgreSQL · pandas · SQLAlchemy

## Quick Start
1. Create a PostgreSQL database.
2. Run `sql/create_tables.sql`.
3. Copy `.env.example` to `.env` and configure the connection.
4. Run `pip install -r requirements.txt`.
5. Run `python -m src.main --input sample_data/transactions_sample.csv`.

## Portfolio Note
Created as a technical portfolio project demonstrating ETL, PostgreSQL, and transaction data processing skills.
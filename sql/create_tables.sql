-- Execution log: one row per pipeline run
CREATE TABLE IF NOT EXISTS etl_import_log (
    id            BIGSERIAL PRIMARY KEY,
    source_file   TEXT        NOT NULL,
    started_at    TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    finished_at   TIMESTAMP,
    status        VARCHAR(20) NOT NULL,
    rows_read     BIGINT      DEFAULT 0,
    rows_loaded   BIGINT      DEFAULT 0,
    error_message TEXT
);

-- Staging table: cleaned rows land here before the upsert
CREATE TABLE IF NOT EXISTS transactions_stage (
    transaction_id   VARCHAR(50),
    transaction_date TIMESTAMP,
    merchant_id      VARCHAR(50),
    transaction_type VARCHAR(30),
    amount           NUMERIC(18,2),
    currency         VARCHAR(3),
    source_file      TEXT,
    loaded_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Target table
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id   VARCHAR(50)   PRIMARY KEY,
    transaction_date TIMESTAMP     NOT NULL,
    merchant_id      VARCHAR(50)   NOT NULL,
    transaction_type VARCHAR(30)   NOT NULL,
    amount           NUMERIC(18,2) NOT NULL CHECK (amount >= 0),
    currency         VARCHAR(3)    NOT NULL,
    source_file      TEXT,
    loaded_at        TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_transactions_date
    ON transactions (transaction_date);

CREATE INDEX IF NOT EXISTS idx_transactions_merchant_date
    ON transactions (merchant_id, transaction_date);

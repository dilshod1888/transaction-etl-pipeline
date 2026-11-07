from sqlalchemy import text
def load_transactions(df,engine,source_file):
    if df.empty: return 0
    staged=df.copy(); staged['source_file']=source_file
    staged.to_sql('transactions_stage',engine,if_exists='append',index=False,method='multi',chunksize=5000)
    with engine.begin() as conn:
        conn.execute(text('''INSERT INTO transactions (transaction_id,transaction_date,merchant_id,transaction_type,amount,currency,source_file) SELECT DISTINCT ON (transaction_id) transaction_id,transaction_date,merchant_id,transaction_type,amount,currency,source_file FROM transactions_stage ORDER BY transaction_id,loaded_at DESC ON CONFLICT (transaction_id) DO UPDATE SET transaction_date=EXCLUDED.transaction_date, merchant_id=EXCLUDED.merchant_id, transaction_type=EXCLUDED.transaction_type, amount=EXCLUDED.amount, currency=EXCLUDED.currency, source_file=EXCLUDED.source_file'''))
        conn.execute(text('TRUNCATE TABLE transactions_stage'))
    return len(staged)

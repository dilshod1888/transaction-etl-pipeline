from pathlib import Path
import pandas as pd
REQUIRED_COLUMNS={'transaction_id','transaction_date','merchant_id','transaction_type','amount','currency'}
def extract_csv(file_path):
    path=Path(file_path)
    if not path.exists(): raise FileNotFoundError(f'Input file not found: {path}')
    df=pd.read_csv(path)
    missing=REQUIRED_COLUMNS-set(df.columns)
    if missing: raise ValueError(f'Missing required columns: {sorted(missing)}')
    return df

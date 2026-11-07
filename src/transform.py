import pandas as pd
def clean_transactions(df):
    result=df.copy()
    for col in ['transaction_id','merchant_id']:
        result[col]=result[col].astype(str).str.strip()
    result['transaction_type']=result['transaction_type'].astype(str).str.upper().str.strip()
    result['currency']=result['currency'].astype(str).str.upper().str.strip()
    result['transaction_date']=pd.to_datetime(result['transaction_date'],errors='coerce')
    result['amount']=pd.to_numeric(result['amount'].astype(str).str.replace(',', '.', regex=False),errors='coerce')
    result=result.dropna(subset=['transaction_id','transaction_date','merchant_id','transaction_type','amount','currency'])
    result=result[result['amount']>=0].drop_duplicates(subset=['transaction_id'],keep='last')
    return result

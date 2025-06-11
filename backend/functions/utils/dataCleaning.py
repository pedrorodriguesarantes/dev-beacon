import pandas as pd
import re
from glob import glob

def clean_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.select_dtypes(include=["object", "string"]):
        df[col] = df[col].apply(
            lambda x: re.sub(r"[^\x20-\x7E]", "", str(x)) if pd.notnull(x) else x
        )
        
    return df

def load_concat(pattern: str) -> pd.DataFrame:
    files = sorted(glob(pattern))
    if not files:
        return pd.DataFrame()
    return pd.concat([pd.read_excel(f) for f in files], ignore_index=True)
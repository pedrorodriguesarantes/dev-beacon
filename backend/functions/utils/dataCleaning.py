import pandas as pd
import re

def clean_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.select_dtypes(include=["object", "string"]):
        df[col] = df[col].apply(
            lambda x: re.sub(r"[^\x20-\x7E]", "", str(x)) if pd.notnull(x) else x
        )
        
    return df
import pandas as pd

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans market data by handling missing values, duplicate timestamps, and sorting.
    """
    if df.empty:
        return df
        
    # 1. Sort by index (timestamp)
    df = df.sort_index()
    
    # 2. Remove duplicate timestamps, keeping the last one
    df = df[~df.index.duplicated(keep='last')]
    
    # 3. Forward fill missing values, then backward fill any remaining at the start
    df = df.ffill().bfill()
    
    return df

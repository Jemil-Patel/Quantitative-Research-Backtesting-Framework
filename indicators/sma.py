import pandas as pd

def calculate_sma(series: pd.Series, window: int) -> pd.Series:
    """
    Calculates Simple Moving Average (SMA).
    """
    return series.rolling(window=window).mean()

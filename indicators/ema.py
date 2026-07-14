import pandas as pd

def calculate_ema(series: pd.Series, window: int) -> pd.Series:
    """
    Calculates Exponential Moving Average (EMA).
    """
    return series.ewm(span=window, adjust=False).mean()

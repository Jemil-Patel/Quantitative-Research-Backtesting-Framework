import pandas as pd
from typing import Tuple

def calculate_macd(series: pd.Series, fast_window: int = 12, slow_window: int = 26, signal_window: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculates MACD. Returns (MACD line, Signal line, MACD histogram).
    """
    fast_ema = series.ewm(span=fast_window, adjust=False).mean()
    slow_ema = series.ewm(span=slow_window, adjust=False).mean()
    
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
    macd_hist = macd_line - signal_line
    
    return macd_line, signal_line, macd_hist

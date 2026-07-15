import pandas as pd

def calculate_rsi(series: pd.Series, window: int = 14) -> pd.Series:
    """
    Calculates Relative Strength Index (RSI).
    """
    # Standard Wilder's smoothing uses ewm, but simple moving average is also common. 
    # We use ewm with alpha=1/window to be closer to Wilder's RSI.
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.ewm(alpha=1/window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/window, adjust=False).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

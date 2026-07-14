import pandas as pd
from strategies.strategy import Strategy
from indicators.rsi import calculate_rsi

class MomentumStrategy(Strategy):
    """
    RSI-based Momentum Strategy.
    Buys when RSI crosses above oversold threshold (e.g. 30).
    Sells when RSI crosses below overbought threshold (e.g. 70).
    """
    def __init__(self, rsi_window: int = 14, overbought: float = 70.0, oversold: float = 30.0):
        super().__init__("RSI_Momentum")
        self.rsi_window = rsi_window
        self.overbought = overbought
        self.oversold = oversold

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        
        if len(df) < self.rsi_window:
            return signals
            
        rsi = calculate_rsi(df['Close'], self.rsi_window)
        
        # Shift RSI to compare previous day vs today
        rsi_prev = rsi.shift(1)
        
        # Crosses above oversold (Buy)
        buy_cond = (rsi_prev <= self.oversold) & (rsi > self.oversold)
        
        # Crosses below overbought (Sell)
        sell_cond = (rsi_prev >= self.overbought) & (rsi < self.overbought)
        
        signals[buy_cond] = 1
        signals[sell_cond] = -1
        
        return signals

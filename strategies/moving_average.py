import pandas as pd
from strategies.strategy import Strategy
from indicators.sma import calculate_sma

class MovingAverageStrategy(Strategy):
    """
    Simple Moving Average Crossover Strategy.
    Buys when fast MA crosses above slow MA.
    Sells when fast MA crosses below slow MA.
    """
    def __init__(self, fast_window: int = 50, slow_window: int = 200):
        super().__init__("MA_Crossover")
        self.fast_window = fast_window
        self.slow_window = slow_window

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        
        if len(df) < self.slow_window:
            return signals
            
        fast_sma = calculate_sma(df['Close'], self.fast_window)
        slow_sma = calculate_sma(df['Close'], self.slow_window)
        
        # 1 if fast > slow, -1 if fast < slow
        crossover = (fast_sma > slow_sma).astype(int) - (fast_sma < slow_sma).astype(int)
        
        # We only generate trade signals on the CROSSOVER (when state changes)
        state_diff = crossover.diff()
        
        signals[state_diff == 2] = 1
        signals[state_diff == -2] = -1
        
        return signals

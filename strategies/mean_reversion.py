import pandas as pd
from strategies.strategy import Strategy

class MeanReversionStrategy(Strategy):
    """
    Mean Reversion using rolling Z-Score.
    Buy when Z-Score < -threshold.
    Sell when Z-Score > threshold.
    """
    def __init__(self, window: int = 20, threshold: float = 2.0):
        super().__init__("Mean_Reversion")
        self.window = window
        self.threshold = threshold

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        
        if len(df) < self.window:
            return signals
            
        rolling_mean = df['Close'].rolling(window=self.window).mean()
        rolling_std = df['Close'].rolling(window=self.window).std()
        
        z_score = (df['Close'] - rolling_mean) / rolling_std
        
        signals[z_score < -self.threshold] = 1
        signals[z_score > self.threshold] = -1
        
        return signals

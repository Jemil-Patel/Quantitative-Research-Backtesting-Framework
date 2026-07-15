import pandas as pd
from strategies.strategy import Strategy

class BollingerBandsStrategy(Strategy):
    """
    Bollinger Bands Strategy.
    Buy when price crosses below lower band.
    Sell when price crosses above upper band.
    """
    def __init__(self, window: int = 20, num_std: float = 2.0):
        super().__init__("Bollinger_Bands")
        self.window = window
        self.num_std = num_std

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        
        if len(df) < self.window:
            return signals
            
        rolling_mean = df['Close'].rolling(window=self.window).mean()
        rolling_std = df['Close'].rolling(window=self.window).std()
        
        upper_band = rolling_mean + (rolling_std * self.num_std)
        lower_band = rolling_mean - (rolling_std * self.num_std)
        
        signals[df['Close'] < lower_band] = 1
        signals[df['Close'] > upper_band] = -1
        
        return signals

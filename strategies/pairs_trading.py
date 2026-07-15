import pandas as pd
import statsmodels.tsa.stattools as ts
from typing import Dict, Tuple

class PairsTradingStrategy:
    """
    Pairs Trading Strategy using Cointegration.
    """
    def __init__(self, asset1: str, asset2: str, window: int = 60, z_threshold: float = 2.0):
        self.name = "Pairs_Trading"
        self.asset1 = asset1
        self.asset2 = asset2
        self.window = window
        self.z_threshold = z_threshold
        
    def test_cointegration(self, series1: pd.Series, series2: pd.Series) -> Tuple[float, float]:
        """Returns t-statistic and p-value"""
        score, pvalue, _ = ts.coint(series1, series2)
        return score, pvalue

    def generate_signals(self, data_dict: Dict[str, pd.DataFrame]) -> Dict[str, pd.Series]:
        """
        Returns signals for both assets. 1 for BUY, -1 for SELL, 0 for HOLD.
        """
        df1 = data_dict[self.asset1]
        df2 = data_dict[self.asset2]
        
        # Align index
        common_index = df1.index.intersection(df2.index)
        s1 = df1.loc[common_index, 'Close']
        s2 = df2.loc[common_index, 'Close']
        
        signals1 = pd.Series(0, index=common_index, dtype=int)
        signals2 = pd.Series(0, index=common_index, dtype=int)
        
        if len(common_index) < self.window:
            return {self.asset1: signals1, self.asset2: signals2}
            
        # Spread = S1 / S2
        spread = s1 / s2
        
        rolling_mean = spread.rolling(window=self.window).mean()
        rolling_std = spread.rolling(window=self.window).std()
        
        z_score = (spread - rolling_mean) / rolling_std
        
        # If z-score < -threshold: Spread is too small (S1 undervalued, S2 overvalued)
        buy_s1_cond = z_score < -self.z_threshold
        signals1[buy_s1_cond] = 1
        signals2[buy_s1_cond] = -1
        
        # If z-score > threshold: Spread is too large (S1 overvalued, S2 undervalued)
        sell_s1_cond = z_score > self.z_threshold
        signals1[sell_s1_cond] = -1
        signals2[sell_s1_cond] = 1
        
        return {self.asset1: signals1, self.asset2: signals2}

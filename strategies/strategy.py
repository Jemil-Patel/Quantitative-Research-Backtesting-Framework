from abc import ABC, abstractmethod
import pandas as pd

class Strategy(ABC):
    """
    Base Strategy Interface.
    """
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Generates trading signals.
        Returns a pandas Series of signals (1 for BUY, -1 for SELL, 0 for HOLD) aligned with the dataframe index.
        """
        pass

from dataclasses import dataclass
import pandas as pd

class Event:
    """Base class for all events."""
    pass

@dataclass
class MarketEvent(Event):
    """Triggered when new market data arrives."""
    ticker: str
    date: pd.Timestamp
    open: float
    high: float
    low: float
    close: float
    volume: int

@dataclass
class SignalEvent(Event):
    """Triggered by a Strategy when a trading signal is generated."""
    ticker: str
    date: pd.Timestamp
    signal: int  # 1 for BUY, -1 for SELL
    strategy_id: str

@dataclass
class OrderEvent(Event):
    """Triggered by Portfolio to send an order to the execution engine."""
    ticker: str
    date: pd.Timestamp
    quantity: float
    order_type: str  # 'MARKET', 'LIMIT', 'STOP'
    price: float = 0.0 # Relevant for limit/stop orders
    time_in_force: str = 'GTC' # 'GTC', 'IOC', 'FOK'

@dataclass
class FillEvent(Event):
    """Triggered by ExecutionEngine when an order is filled."""
    ticker: str
    date: pd.Timestamp
    quantity: float
    fill_price: float
    commission: float

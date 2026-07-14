from collections import deque
from queue import Queue
from events.event import MarketEvent, SignalEvent
from strategies.event_strategy import EventStrategy

class EventMovingAverageStrategy(EventStrategy):
    """Event-driven Moving Average Crossover Strategy."""
    def __init__(self, events: Queue, fast_window: int = 10, slow_window: int = 30):
        super().__init__(events)
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.prices = {} # ticker -> deque of recent prices
        
    def calculate_signals(self, event: MarketEvent):
        if event.ticker not in self.prices:
            self.prices[event.ticker] = deque(maxlen=self.slow_window)
            
        self.prices[event.ticker].append(event.close)
        
        if len(self.prices[event.ticker]) == self.slow_window:
            recent_prices = list(self.prices[event.ticker])
            fast_ma = sum(recent_prices[-self.fast_window:]) / self.fast_window
            slow_ma = sum(recent_prices) / self.slow_window
            
            signal = 0
            if fast_ma > slow_ma:
                signal = 1
            elif fast_ma < slow_ma:
                signal = -1
                
            # Naive signal generation: fires signal on every tick if condition holds.
            # In a real system, you track position state to only fire on crossovers.
            # For this simple mock, we rely on Portfolio to ignore redundant buys.
            if signal != 0:
                sig_event = SignalEvent(
                    ticker=event.ticker,
                    date=event.date,
                    signal=signal,
                    strategy_id="Event_MA_Crossover"
                )
                self.events.put(sig_event)

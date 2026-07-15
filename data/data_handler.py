import pandas as pd
from queue import Queue
from events.event import MarketEvent

class HistoricalDataHandler:
    """
    Yields MarketEvents from a Pandas DataFrame one row at a time.
    """
    def __init__(self, events: Queue, data_dict: dict):
        self.events = events
        self.data_dict = data_dict
        self.generators = {}
        
        for ticker, df in data_dict.items():
            self.generators[ticker] = df.iterrows()

    def update_bars(self) -> bool:
        """
        Pushes the next row of data for all tickers to the queue as MarketEvents.
        Returns True if more data exists, False if all data exhausted.
        """
        data_yielded = False
        for ticker, generator in self.generators.items():
            try:
                date, row = next(generator)
                event = MarketEvent(
                    ticker=ticker,
                    date=date,
                    open=row['Open'],
                    high=row['High'],
                    low=row['Low'],
                    close=row['Close'],
                    volume=int(row['Volume'])
                )
                self.events.put(event)
                print(f"Yielded MarketEvent for {ticker} on {date}")
                data_yielded = True
            except StopIteration:
                pass
                
        return data_yielded
        
class LiveDataHandler:
    """Stub for a live streaming data handler (e.g. WebSocket)."""
    def __init__(self, events: Queue):
        self.events = events
        
    def stream_ticks(self):
        # Implementation would connect to WSS and push MarketEvents
        pass

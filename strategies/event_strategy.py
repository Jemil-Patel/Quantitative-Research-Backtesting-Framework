from queue import Queue
from events.event import MarketEvent, SignalEvent

class EventStrategy:
    """Base class for event-driven strategies."""
    def __init__(self, events: Queue):
        self.events = events
        
    def calculate_signals(self, event: MarketEvent):
        """Processes a MarketEvent and generates SignalEvents."""
        raise NotImplementedError("Must implement calculate_signals()")

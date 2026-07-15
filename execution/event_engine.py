import queue
import time

class EventEngine:
    """
    Central event loop orchestrating the flow of events between components.
    """
    def __init__(self, events: queue.Queue, mode: str = "backtest"):
        self.events = events
        self.active = True
        self.handlers = {}
        self.mode = mode

    def register_handler(self, event_type: str, handler):
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    def run(self, data_handler=None):
        """Runs the event loop."""
        while self.active:
            # Feed more data if the queue is empty
            if data_handler and self.mode == "backtest" and self.events.empty():
                has_data = data_handler.update_bars()
                if not has_data:
                    self.active = False
                    break
                    
            try:
                event = self.events.get(False)
            except queue.Empty:
                if self.mode == "live":
                    time.sleep(0.1) # Sleep if live
                else:
                    pass
            else:
                if event is not None:
                    event_type = type(event).__name__
                    print(f"Routing event: {event_type}")
                    if event_type in self.handlers:
                        for handler in self.handlers[event_type]:
                            handler(event)

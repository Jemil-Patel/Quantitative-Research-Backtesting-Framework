from queue import Queue
from events.event import MarketEvent, OrderEvent, FillEvent
import random
import time

class EventExecutionEngine:
    """Simulates realistic execution processing."""
    def __init__(self, events: Queue, commission_pct: float = 0.001, slippage_pct: float = 0.0005, latency_ms: int = 50):
        self.events = events
        self.commission_pct = commission_pct
        self.slippage_pct = slippage_pct
        self.latency_ms = latency_ms
        self.last_prices = {} # ticker -> price

    def update_market(self, event: MarketEvent):
        self.last_prices[event.ticker] = event.close

    def process_order(self, event: OrderEvent):
        if event.ticker not in self.last_prices:
            return
            
        print(f"Processing order: {event}")
        price = self.last_prices[event.ticker]
        
        # Simulate partial fills randomly
        fill_qty = event.quantity
        if random.random() < 0.1: # 10% chance of partial fill
            fill_qty = fill_qty // 2
            if fill_qty != 0:
                # Put remainder back on queue as a new order if not IOC/FOK
                if event.time_in_force == 'GTC':
                    remainder = OrderEvent(event.ticker, event.date, event.quantity - fill_qty, event.order_type, event.price, event.time_in_force)
                    self.events.put(remainder)
                elif event.time_in_force == 'FOK':
                    return # FOK fails completely
        
        if fill_qty == 0:
            return
            
        # Simulate latency
        # (In backtest we don't sleep, but we would in paper trade mode)
        
        executed_price = price * (1 + self.slippage_pct) if fill_qty > 0 else price * (1 - self.slippage_pct)
        commission = abs(fill_qty) * executed_price * self.commission_pct
        
        fill_event = FillEvent(
            ticker=event.ticker,
            date=event.date,
            quantity=fill_qty,
            fill_price=executed_price,
            commission=commission
        )
        
        self.events.put(fill_event)

class PaperTradingEngine:
    """Stub for live paper trading execution against a broker API."""
    def __init__(self, events: Queue):
        self.events = events
        
    def process_order(self, event: OrderEvent):
        # Implementation would submit order via broker API
        # e.g., requests.post('api.alpaca.markets/v2/orders', data=...)
        pass
        
    def update_market(self, event: MarketEvent):
        pass

from queue import Queue
from events.event import MarketEvent, SignalEvent, FillEvent, OrderEvent
from portfolio.portfolio import Portfolio
from portfolio.risk_manager import RiskManager

class EventPortfolio:
    """Event-driven portfolio manager."""
    def __init__(self, events: Queue, portfolio: Portfolio, risk_manager: RiskManager):
        self.events = events
        self.portfolio = portfolio
        self.risk_manager = risk_manager
        self.last_price = {} # ticker -> current price

    def update_market(self, event: MarketEvent):
        """Called on MarketEvent to update current known price"""
        self.last_price[event.ticker] = event.close

    def update_signal(self, event: SignalEvent):
        """Processes SignalEvent and conditionally emits OrderEvent"""
        ticker = event.ticker
        price = self.last_price.get(ticker, 0.0)
        
        print(f"Received signal {event.signal} for {ticker} at price {price}")
        
        if price <= 0:
            return
            
        # We also need to check Risk Manager stop-loss/take-profit here
        # But to keep it modular, let's just do it on MarketEvent
        if self.risk_manager.check_exit_conditions(self.portfolio, ticker, price):
            qty = self.portfolio.holdings.get(ticker, 0.0)
            if qty > 0:
                order = OrderEvent(ticker=ticker, date=event.date, quantity=-qty, order_type="MARKET")
                self.events.put(order)
                return # Skip normal signals if we just SL/TP'd
            
        qty = 0
        if event.signal == 1:
            if self.portfolio.holdings.get(ticker, 0.0) == 0:
                qty = self.risk_manager.get_position_size(self.portfolio, price)
        elif event.signal == -1:
            qty = -self.portfolio.holdings.get(ticker, 0.0)
            
        if qty != 0:
            order = OrderEvent(
                ticker=ticker,
                date=event.date,
                quantity=qty,
                order_type="MARKET"
            )
            self.events.put(order)
            
    def update_fill(self, event: FillEvent):
        """Processes FillEvent to update internal portfolio state"""
        self.portfolio.update_holding(
            ticker=event.ticker,
            quantity_change=event.quantity,
            price=event.fill_price,
            date=event.date,
            commission=event.commission
        )

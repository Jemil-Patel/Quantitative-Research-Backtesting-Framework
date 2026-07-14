import pandas as pd
from portfolio.portfolio import Portfolio

class ExecutionEngine:
    """
    Simulates order execution against historical data with slippage and commissions.
    """
    def __init__(self, portfolio: Portfolio, commission_pct: float = 0.001, slippage_pct: float = 0.0005):
        self.portfolio = portfolio
        self.commission_pct = commission_pct
        self.slippage_pct = slippage_pct
        
    def execute_order(self, ticker: str, quantity: float, price: float, date: pd.Timestamp) -> bool:
        """
        Executes an order immediately at the given price.
        Quantity > 0 implies BUY, Quantity < 0 implies SELL.
        Returns True if executed, False if rejected by Risk Manager.
        """
        if quantity == 0:
            return False
            
        # Apply slippage
        executed_price = price * (1 + self.slippage_pct) if quantity > 0 else price * (1 - self.slippage_pct)
        
        # Calculate commission
        trade_value = abs(quantity) * executed_price
        commission = trade_value * self.commission_pct
        
        # Basic risk check
        if quantity > 0:
            total_cost = trade_value + commission
            if self.portfolio.current_cash < total_cost:
                return False
        elif quantity < 0:
            current_qty = self.portfolio.holdings.get(ticker, 0.0)
            if current_qty < abs(quantity):
                return False
                    
        self.portfolio.update_holding(ticker, quantity, executed_price, date, commission)
        return True

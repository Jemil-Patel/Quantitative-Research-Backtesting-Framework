import pandas as pd
from typing import Dict, List, Any

class Portfolio:
    def __init__(self, initial_cash: float = 10000.0):
        self.initial_cash = initial_cash
        self.current_cash = initial_cash
        self.holdings: Dict[str, float] = {}  # ticker -> quantity
        self.entry_prices: Dict[str, float] = {} # ticker -> average entry price
        self.trade_log: List[Dict[str, Any]] = []
        
    def update_holding(self, ticker: str, quantity_change: float, price: float, date: pd.Timestamp, commission: float = 0.0):
        # Update cash
        cost = (quantity_change * price) + commission
        self.current_cash -= cost
        
        # Calculate Realized PnL for sells
        realized_pnl = 0.0
        if quantity_change < 0 and ticker in self.entry_prices:
            realized_pnl = abs(quantity_change) * (price - self.entry_prices[ticker]) - commission
            
        # Update holdings and entry prices
        current_qty = self.holdings.get(ticker, 0.0)
        new_qty = current_qty + quantity_change
        
        if quantity_change > 0: # Buying
            if current_qty > 0:
                # Update average entry price
                current_cost = current_qty * self.entry_prices[ticker]
                new_cost = quantity_change * price
                self.entry_prices[ticker] = (current_cost + new_cost) / new_qty
            else:
                self.entry_prices[ticker] = price
                
        if new_qty == 0:
            if ticker in self.holdings:
                del self.holdings[ticker]
                if ticker in self.entry_prices:
                    del self.entry_prices[ticker]
        else:
            self.holdings[ticker] = new_qty
            
        # Log trade
        trade = {
            'Date': date,
            'Ticker': ticker,
            'Action': 'BUY' if quantity_change > 0 else 'SELL',
            'Quantity': abs(quantity_change),
            'Price': price,
            'Commission': commission,
            'Value': abs(quantity_change * price),
            'Realized_PnL': realized_pnl
        }
        self.trade_log.append(trade)
        
    def get_current_value(self, current_prices: Dict[str, float]) -> float:
        """Returns total portfolio value including cash and current holdings"""
        holdings_value = sum(
            self.holdings.get(ticker, 0.0) * current_prices.get(ticker, 0.0)
            for ticker in self.holdings
        )
        return self.current_cash + holdings_value

    def get_trade_log_df(self) -> pd.DataFrame:
        """Returns the trade log as a DataFrame"""
        return pd.DataFrame(self.trade_log)

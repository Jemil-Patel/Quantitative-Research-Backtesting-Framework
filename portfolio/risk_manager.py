from portfolio.portfolio import Portfolio
import pandas as pd

class RiskManager:
    """
    Handles position sizing and risk management (stop loss / take profit).
    """
    def __init__(self, stop_loss_pct: float = 0.05, take_profit_pct: float = 0.10, position_size_pct: float = 1.0):
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.position_size_pct = position_size_pct
        
    def get_position_size(self, portfolio: Portfolio, price: float) -> float:
        """
        Determines how many shares to buy based on current cash and position_size_pct.
        """
        allocated_cash = portfolio.current_cash * self.position_size_pct
        quantity = allocated_cash // price
        return quantity
        
    def check_exit_conditions(self, portfolio: Portfolio, ticker: str, current_price: float) -> bool:
        """
        Checks if stop loss or take profit has been hit.
        Returns True if we should exit (SELL), False otherwise.
        """
        if ticker not in portfolio.holdings:
            return False
            
        entry_price = portfolio.entry_prices.get(ticker)
        if not entry_price:
            return False
            
        pnl_pct = (current_price - entry_price) / entry_price
        
        # Check Stop Loss
        if self.stop_loss_pct > 0 and pnl_pct <= -self.stop_loss_pct:
            return True
            
        # Check Take Profit
        if self.take_profit_pct > 0 and pnl_pct >= self.take_profit_pct:
            return True
            
        return False
        
    def get_kelly_position_size(self, portfolio: Portfolio, price: float, win_rate: float, win_loss_ratio: float) -> float:
        """
        Kelly Criterion: f* = W - ((1 - W) / R)
        W = win rate, R = win/loss ratio (avg win / avg loss)
        """
        if win_loss_ratio <= 0 or win_rate <= 0:
            return 0.0
            
        kelly_pct = win_rate - ((1 - win_rate) / win_loss_ratio)
        kelly_pct = max(0.0, min(kelly_pct, 1.0)) # Bound between 0 and 100%
        
        # Scale Kelly by position_size_pct (e.g. Half-Kelly = 0.5)
        allocated_cash = portfolio.current_cash * kelly_pct * self.position_size_pct
        return allocated_cash // price
        
    def get_volatility_adjusted_size(self, portfolio: Portfolio, price: float, current_vol: float, target_vol: float = 0.15) -> float:
        """
        Scales position size inversely with current volatility to target a constant risk level.
        """
        if current_vol <= 0:
            return 0.0
        
        # Volatility scalar
        scalar = target_vol / current_vol
        
        # Bound scalar so we don't use infinite leverage on zero vol
        scalar = min(scalar, 2.0)
        
        allocated_cash = portfolio.current_cash * self.position_size_pct * scalar
        return allocated_cash // price

import pandas as pd
import numpy as np

def calculate_daily_returns(portfolio_values: pd.Series) -> pd.Series:
    """
    Calculates daily returns from a series of portfolio values.
    """
    return portfolio_values.pct_change().fillna(0.0)

def calculate_equity_curve(portfolio_values: pd.Series) -> pd.Series:
    """
    Calculates normalized equity curve (starting at 1.0)
    """
    if len(portfolio_values) == 0:
        return pd.Series(dtype=float)
    return portfolio_values / portfolio_values.iloc[0]

def calculate_cagr(portfolio_values: pd.Series, trading_days: int = 252) -> float:
    years = len(portfolio_values) / trading_days
    if years == 0: return 0.0
    return float((portfolio_values.iloc[-1] / portfolio_values.iloc[0]) ** (1 / years) - 1)

def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0, trading_days: int = 252) -> float:
    if returns.std() == 0: return 0.0
    return float((returns.mean() - risk_free_rate) / returns.std() * np.sqrt(trading_days))
    
def calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.0, trading_days: int = 252) -> float:
    downside_returns = returns[returns < 0]
    if downside_returns.std() == 0: return 0.0
    return float((returns.mean() - risk_free_rate) / downside_returns.std() * np.sqrt(trading_days))
    
def calculate_max_drawdown(portfolio_values: pd.Series) -> float:
    if len(portfolio_values) == 0: return 0.0
    peak = portfolio_values.expanding(min_periods=1).max()
    drawdown = (portfolio_values / peak) - 1
    return float(drawdown.min())

def calculate_trade_metrics(trade_log: pd.DataFrame) -> dict:
    if trade_log.empty or 'Realized_PnL' not in trade_log.columns:
        return {'Win Rate': 0.0, 'Profit Factor': 0.0}
        
    sells = trade_log[trade_log['Action'] == 'SELL']
    if sells.empty:
        return {'Win Rate': 0.0, 'Profit Factor': 0.0}
        
    winning_trades = sells[sells['Realized_PnL'] > 0]
    losing_trades = sells[sells['Realized_PnL'] <= 0]
    
    win_rate = len(winning_trades) / len(sells)
    
    gross_profit = winning_trades['Realized_PnL'].sum()
    gross_loss = abs(losing_trades['Realized_PnL'].sum())
    
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    
    return {'Win Rate': win_rate, 'Profit Factor': profit_factor}

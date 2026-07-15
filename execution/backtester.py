import pandas as pd
from typing import Dict, Any, Type
from portfolio.portfolio import Portfolio
from execution.execution_engine import ExecutionEngine
from portfolio.risk_manager import RiskManager
from analytics.metrics import calculate_cagr
from strategies.strategy import Strategy
from strategies.pairs_trading import PairsTradingStrategy

class Backtester:
    def __init__(self, data, strategy, config: Dict[str, Any]):
        self.data = data
        self.strategy = strategy
        self.config = config
        
    def run(self) -> Dict[str, Any]:
        portfolio = Portfolio(initial_cash=10000.0)
        risk_config = self.config.get('risk', {})
        risk_manager = RiskManager(
            stop_loss_pct=risk_config.get('stop_loss_pct', 0.05),
            take_profit_pct=risk_config.get('take_profit_pct', 0.10),
            position_size_pct=risk_config.get('position_size_pct', 1.0)
        )
        engine = ExecutionEngine(portfolio, commission_pct=0.001, slippage_pct=0.0005)
        
        if isinstance(self.strategy, PairsTradingStrategy):
            signals_dict = self.strategy.generate_signals(self.data)
            
            common_index = self.data[self.strategy.asset1].index.intersection(self.data[self.strategy.asset2].index)
            portfolio_values = []
            
            for i in range(len(common_index)):
                date = common_index[i]
                p1 = self.data[self.strategy.asset1].loc[date, 'Close']
                p2 = self.data[self.strategy.asset2].loc[date, 'Close']
                
                sig1 = signals_dict[self.strategy.asset1].iloc[i]
                sig2 = signals_dict[self.strategy.asset2].iloc[i]
                
                for asset, price in [(self.strategy.asset1, p1), (self.strategy.asset2, p2)]:
                    if risk_manager.check_exit_conditions(portfolio, asset, price):
                        qty = portfolio.holdings.get(asset, 0.0)
                        engine.execute_order(asset, -qty, price, date)
                
                if sig1 == 1:
                    qty = (risk_manager.get_position_size(portfolio, p1) // 2)
                    engine.execute_order(self.strategy.asset1, qty, p1, date)
                elif sig1 == -1:
                    qty = portfolio.holdings.get(self.strategy.asset1, 0.0)
                    engine.execute_order(self.strategy.asset1, -qty, p1, date)
                    
                if sig2 == 1:
                    qty = (risk_manager.get_position_size(portfolio, p2) // 2)
                    engine.execute_order(self.strategy.asset2, qty, p2, date)
                elif sig2 == -1:
                    qty = portfolio.holdings.get(self.strategy.asset2, 0.0)
                    engine.execute_order(self.strategy.asset2, -qty, p2, date)
                    
                portfolio_values.append(portfolio.get_current_value({
                    self.strategy.asset1: p1,
                    self.strategy.asset2: p2
                }))
                
            portfolio_series = pd.Series(portfolio_values, index=common_index)
            
        else:
            asset = self.config.get('assets', ['AAPL'])[0]
            single_data = self.data[asset] if isinstance(self.data, dict) else self.data
            signals = self.strategy.generate_signals(single_data)
            portfolio_values = []
            
            for i in range(len(single_data)):
                date = single_data.index[i]
                price = single_data.iloc[i]['Close']
                signal = signals.iloc[i]
                
                if risk_manager.check_exit_conditions(portfolio, asset, price):
                    qty = portfolio.holdings.get(asset, 0.0)
                    engine.execute_order(asset, -qty, price, date)
                else:
                    if signal == 1:
                        qty = risk_manager.get_position_size(portfolio, price)
                        engine.execute_order(asset, qty, price, date)
                    elif signal == -1:
                        qty = portfolio.holdings.get(asset, 0.0)
                        engine.execute_order(asset, -qty, price, date)
                        
                portfolio_values.append(portfolio.get_current_value({asset: price}))
            portfolio_series = pd.Series(portfolio_values, index=single_data.index)
            
        cagr = calculate_cagr(portfolio_series)
        
        return {
            'cagr': cagr,
            'portfolio_series': portfolio_series,
            'portfolio': portfolio
        }

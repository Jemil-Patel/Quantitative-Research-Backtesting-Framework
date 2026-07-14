import argparse
from queue import Queue
from data.yahoo import fetch_data
from data.data_handler import HistoricalDataHandler
from execution.event_engine import EventEngine
from strategies.event_moving_average import EventMovingAverageStrategy
from portfolio.portfolio import Portfolio
from portfolio.risk_manager import RiskManager
from portfolio.event_portfolio import EventPortfolio
from execution.event_execution import EventExecutionEngine

def main():
    parser = argparse.ArgumentParser(description="Event-Driven Backtest")
    parser.add_argument("--asset", type=str, default="AAPL")
    args = parser.parse_args()

    print(f"Fetching data for {args.asset}...")
    df = fetch_data([args.asset], "2023-01-01", "2023-12-31")
    
    events = Queue()
    # fetch_data returns a dataframe directly if given a string list of length 1, but wait!
    # Our original fetch_data checks if isinstance(tickers, list) and returns dict.
    # Let's ensure it's a dict.
    data_dict = {args.asset: df} if isinstance(df, type(pd.DataFrame())) else df
    
    data_handler = HistoricalDataHandler(events, data_dict)
    
    strategy = EventMovingAverageStrategy(events)
    base_portfolio = Portfolio(initial_cash=10000.0)
    risk_manager = RiskManager()
    portfolio = EventPortfolio(events, base_portfolio, risk_manager)
    execution = EventExecutionEngine(events)
    
    engine = EventEngine(events=events, mode="backtest")
    
    engine.register_handler('MarketEvent', strategy.calculate_signals)
    engine.register_handler('MarketEvent', portfolio.update_market)
    engine.register_handler('MarketEvent', execution.update_market)
    
    engine.register_handler('SignalEvent', portfolio.update_signal)
    engine.register_handler('OrderEvent', execution.process_order)
    engine.register_handler('FillEvent', portfolio.update_fill)
    
    print("Starting event loop...")
    engine.run(data_handler=data_handler)
    
    print("\n--- Event Backtest Completed ---")
    current_price = portfolio.last_price.get(args.asset, 0)
    print(f"Final Portfolio Value: ${base_portfolio.get_current_value({args.asset: current_price}):.2f}")
    
    trade_log = base_portfolio.get_trade_log_df()
    print("\n--- Trade Log ---")
    print(trade_log if not trade_log.empty else "No trades.")

if __name__ == "__main__":
    import pandas as pd
    main()

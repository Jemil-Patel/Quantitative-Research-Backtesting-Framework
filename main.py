import argparse
import json
import pandas as pd
from data.yahoo import fetch_data
from execution.backtester import Backtester
from execution.grid_search import run_grid_search
from execution.walk_forward import run_walk_forward
from strategies.moving_average import MovingAverageStrategy
from strategies.momentum import MomentumStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.bollinger_bands import BollingerBandsStrategy
from strategies.pairs_trading import PairsTradingStrategy
from analytics.metrics import calculate_cagr, calculate_sharpe_ratio, calculate_max_drawdown

STRATEGY_MAP = {
    "moving_average": MovingAverageStrategy,
    "momentum": MomentumStrategy,
    "mean_reversion": MeanReversionStrategy,
    "bollinger_bands": BollingerBandsStrategy,
    "pairs_trading": PairsTradingStrategy
}

def load_config(config_path: str = "config/config.json") -> dict:
    with open(config_path, "r") as f:
        return json.load(f)

def run_multi_strategy_comparison(data, config):
    print("\n--- Multi-Strategy Comparison ---")
    results = []
    
    for name, strategy_class in STRATEGY_MAP.items():
        if name == "pairs_trading" and len(config['assets']) >= 2:
            strategy = strategy_class(asset1=config['assets'][0], asset2=config['assets'][1])
        elif name != "pairs_trading":
            strategy = strategy_class()
        else:
            continue
            
        print(f"Running {strategy.name}...")
        backtester = Backtester(data, strategy, config)
        res = backtester.run()
        
        returns = res['portfolio_series'].pct_change().fillna(0)
        sharpe = calculate_sharpe_ratio(returns)
        mdd = calculate_max_drawdown(res['portfolio_series'])
        
        results.append({
            "Strategy": strategy.name,
            "CAGR": f"{res['cagr']:.2%}",
            "Sharpe": f"{sharpe:.2f}",
            "Max DD": f"{mdd:.2%}"
        })
        
    df_results = pd.DataFrame(results)
    print("\n", df_results.to_string(index=False))

def main():
    parser = argparse.ArgumentParser(description="Quantitative Research & Backtesting Framework")
    parser.add_argument("--config", type=str, default="config/config.json", help="Path to config file")
    parser.add_argument("--mode", type=str, default="backtest", choices=["backtest", "grid_search", "walk_forward", "compare"], help="Execution mode")
    
    args = parser.parse_args()
    config = load_config(args.config)
    
    print(f"Fetching data for {config['assets']} from {config['start_date']} to {config['end_date']}...")
    data = fetch_data(config['assets'], config['start_date'], config['end_date'])
    
    if args.mode == "compare":
        run_multi_strategy_comparison(data, config)
        return
        
    strategy_name = config.get('strategy', 'moving_average')
    strategy_class = STRATEGY_MAP.get(strategy_name, MovingAverageStrategy)
    
    if args.mode == "grid_search":
        print(f"\n--- Running Grid Search for {strategy_name} ---")
        param_grid = config.get('grid_search', {}).get(strategy_name, {})
        if not param_grid:
            print("No grid search parameters found in config.")
            return
            
        best_params, best_result = run_grid_search(data, strategy_class, param_grid, config)
        print(f"Best Parameters: {best_params}")
        print(f"Best CAGR: {best_result['cagr']:.2%}")
        
    elif args.mode == "walk_forward":
        print(f"\n--- Running Walk-Forward Testing for {strategy_name} ---")
        param_grid = config.get('grid_search', {}).get(strategy_name, {})
        wf_results = run_walk_forward(data, strategy_class, param_grid, config)
        for res in wf_results:
            print(f"Period: {res['period']} | Best Params: {res['best_params']} | Test CAGR: {res['cagr']:.2%}")
            
    else: # basic backtest
        print(f"\n--- Running Standard Backtest for {strategy_name} ---")
        if strategy_name == "pairs_trading":
            strategy = strategy_class(asset1=config['assets'][0], asset2=config['assets'][1])
        else:
            strategy = strategy_class()
            
        backtester = Backtester(data, strategy, config)
        res = backtester.run()
        
        print(f"Final Portfolio Value: ${res['portfolio_series'].iloc[-1]:.2f}")
        print(f"CAGR: {res['cagr']:.2%}")

if __name__ == "__main__":
    main()

import pandas as pd
from typing import Dict, Any, Type
from execution.grid_search import run_grid_search
from execution.backtester import Backtester

def run_walk_forward(data, strategy_class, param_grid: Dict[str, list], config: Dict[str, Any], train_days: int = 252, test_days: int = 63):
    """
    Walk-forward optimization.
    Trains on `train_days`, picks best params, then tests on `test_days`.
    Moves window forward by `test_days`.
    """
    if isinstance(data, dict):
        first_asset = list(data.keys())[0]
        full_index = data[first_asset].index
    else:
        full_index = data.index
        
    start_idx = 0
    test_results = []
    
    while start_idx + train_days + test_days <= len(full_index):
        # 1. Train Window
        train_start = full_index[start_idx]
        train_end = full_index[start_idx + train_days - 1]
        
        if isinstance(data, dict):
            train_data = {k: v.loc[train_start:train_end] for k, v in data.items()}
        else:
            train_data = data.loc[train_start:train_end]
            
        best_params, _ = run_grid_search(train_data, strategy_class, param_grid, config)
        
        # 2. Test Window
        test_start = full_index[start_idx + train_days]
        test_end = full_index[start_idx + train_days + test_days - 1]
        
        if isinstance(data, dict):
            test_data = {k: v.loc[test_start:test_end] for k, v in data.items()}
        else:
            test_data = data.loc[test_start:test_end]
            
        # Run test with best params
        if "PairsTradingStrategy" in strategy_class.__name__:
            strategy = strategy_class(asset1=config['assets'][0], asset2=config['assets'][1], **best_params)
        else:
            strategy = strategy_class(**best_params)
            
        backtester = Backtester(test_data, strategy, config)
        res = backtester.run()
        
        test_results.append({
            'period': f"{test_start.date()} to {test_end.date()}",
            'best_params': best_params,
            'cagr': res['cagr'],
            'portfolio': res['portfolio'],
            'portfolio_series': res['portfolio_series']
        })
        
        start_idx += test_days
        
    return test_results

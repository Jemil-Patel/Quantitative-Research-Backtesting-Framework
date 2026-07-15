import itertools
from typing import Dict, Any, List
from execution.backtester import Backtester

def generate_param_grid(param_dict: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
    keys, values = zip(*param_dict.items())
    permutations_dicts = [dict(zip(keys, v)) for v in itertools.product(*values)]
    return permutations_dicts

def run_grid_search(data, strategy_class, param_grid: Dict[str, List[Any]], config: Dict[str, Any]):
    configs = generate_param_grid(param_grid)
    best_cagr = -float('inf')
    best_params = None
    best_result = None
    
    for params in configs:
        # For PairsTradingStrategy, it requires asset1 and asset2 as well
        if "PairsTradingStrategy" in strategy_class.__name__:
            strategy = strategy_class(asset1=config['assets'][0], asset2=config['assets'][1], **params)
        else:
            strategy = strategy_class(**params)
            
        backtester = Backtester(data, strategy, config)
        result = backtester.run()
        
        if result['cagr'] > best_cagr:
            best_cagr = result['cagr']
            best_params = params
            best_result = result
            
    return best_params, best_result

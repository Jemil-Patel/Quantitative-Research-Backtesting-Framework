import json
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# Import framework logic
from data.yahoo import fetch_data
from execution.backtester import Backtester
from execution.grid_search import run_grid_search
from execution.walk_forward import run_walk_forward
from strategies.moving_average import MovingAverageStrategy
from strategies.momentum import MomentumStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.bollinger_bands import BollingerBandsStrategy
from strategies.pairs_trading import PairsTradingStrategy
from analytics.metrics import (
    calculate_daily_returns,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_max_drawdown,
    calculate_cagr,
    calculate_trade_metrics
)
from indicators.sma import calculate_sma
from indicators.ema import calculate_ema
from indicators.rsi import calculate_rsi

app = FastAPI(title="Quant Backtesting API")

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STRATEGY_MAP = {
    "moving_average": MovingAverageStrategy,
    "momentum": MomentumStrategy,
    "mean_reversion": MeanReversionStrategy,
    "bollinger_bands": BollingerBandsStrategy,
    "pairs_trading": PairsTradingStrategy
}

class RiskConfig(BaseModel):
    stop_loss_pct: float = Field(0.05, description="Stop loss percent (0 to 1)")
    take_profit_pct: float = Field(0.10, description="Take profit percent (0 to 1)")
    position_size_pct: float = Field(1.0, description="Position size scaling (0 to 1)")

class BacktestRequest(BaseModel):
    assets: List[str] = Field(["AAPL"], description="List of ticker symbols")
    start_date: str = Field("2023-01-01", description="Start date YYYY-MM-DD")
    end_date: str = Field("2023-12-31", description="End date YYYY-MM-DD")
    strategy: str = Field("moving_average", description="Name of strategy")
    params: Dict[str, Any] = Field(default_factory=dict, description="Strategy parameters")
    risk: RiskConfig = Field(default_factory=RiskConfig)

class GridSearchRequest(BaseModel):
    assets: List[str]
    start_date: str
    end_date: str
    strategy: str
    param_grid: Dict[str, List[Any]]
    risk: RiskConfig = Field(default_factory=RiskConfig)

class WalkForwardRequest(BaseModel):
    assets: List[str]
    start_date: str
    end_date: str
    strategy: str
    param_grid: Dict[str, List[Any]]
    risk: RiskConfig = Field(default_factory=RiskConfig)
    train_days: int = 252
    test_days: int = 63

def nan_to_none(val):
    if pd.isna(val) or (isinstance(val, float) and np.isnan(val)):
        return None
    return val

def sanitize_json(data):
    if isinstance(data, dict):
        return {k: sanitize_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_json(v) for v in data]
    elif isinstance(data, float):
        if np.isnan(data) or np.isinf(data):
            return None
        return data
    elif isinstance(data, (np.float32, np.float64)):
        val = float(data)
        if np.isnan(val) or np.isinf(val):
            return None
        return val
    elif isinstance(data, (np.int32, np.int64)):
        return int(data)
    else:
        return data

@app.get("/api/strategies")
def get_strategies():
    return [
        {
            "id": "moving_average",
            "name": "Simple Moving Average Crossover",
            "description": "Buys when fast MA crosses above slow MA. Sells when fast MA crosses below slow MA.",
            "parameters": [
                {"name": "fast_window", "type": "int", "default": 50, "min": 5, "max": 100},
                {"name": "slow_window", "type": "int", "default": 200, "min": 20, "max": 500}
            ]
        },
        {
            "id": "momentum",
            "name": "RSI Momentum",
            "description": "Buys when RSI crosses above oversold threshold. Sells when RSI crosses below overbought threshold.",
            "parameters": [
                {"name": "rsi_window", "type": "int", "default": 14, "min": 2, "max": 50},
                {"name": "overbought", "type": "float", "default": 70.0, "min": 50.0, "max": 95.0},
                {"name": "oversold", "type": "float", "default": 30.0, "min": 5.0, "max": 50.0}
            ]
        },
        {
            "id": "mean_reversion",
            "name": "Z-Score Mean Reversion",
            "description": "Buys when price rolling Z-Score falls below negative threshold. Sells when Z-Score rises above positive threshold.",
            "parameters": [
                {"name": "window", "type": "int", "default": 20, "min": 5, "max": 100},
                {"name": "threshold", "type": "float", "default": 2.0, "min": 0.5, "max": 4.0}
            ]
        },
        {
            "id": "bollinger_bands",
            "name": "Bollinger Bands",
            "description": "Buys when price crosses below the lower Bollinger Band. Sells when price crosses above the upper Bollinger Band.",
            "parameters": [
                {"name": "window", "type": "int", "default": 20, "min": 5, "max": 100},
                {"name": "num_std", "type": "float", "default": 2.0, "min": 0.5, "max": 4.0}
            ]
        },
        {
            "id": "pairs_trading",
            "name": "Cointegrated Pairs Trading",
            "description": "Trades a pairs spread. Buys spread (Buy Asset 1, Sell Asset 2) when z-score is below threshold. Sells spread when z-score is above threshold.",
            "parameters": [
                {"name": "window", "type": "int", "default": 60, "min": 10, "max": 252},
                {"name": "z_threshold", "type": "float", "default": 2.0, "min": 0.5, "max": 4.0}
            ]
        }
    ]

@app.post("/api/backtest")
def run_backtest_endpoint(req: BacktestRequest):
    try:
        # Load and clean assets
        assets = [a.strip().upper() for a in req.assets if a.strip()]
        if not assets:
            raise HTTPException(status_code=400, detail="Must provide at least one asset")
            
        strategy_class = STRATEGY_MAP.get(req.strategy)
        if not strategy_class:
            raise HTTPException(status_code=400, detail=f"Strategy '{req.strategy}' not found")
            
        # Fetch historical data
        print(f"Fetching data for {assets} from {req.start_date} to {req.end_date}...")
        data = fetch_data(assets, req.start_date, req.end_date)
        
        # Prepare strategy parameters
        params = req.params or {}
        # Convert numeric params to correct types
        strategy_meta = [s for s in get_strategies() if s["id"] == req.strategy][0]
        typed_params = {}
        for p in strategy_meta["parameters"]:
            pname = p["name"]
            val = params.get(pname, p["default"])
            if p["type"] == "int":
                typed_params[pname] = int(val)
            elif p["type"] == "float":
                typed_params[pname] = float(val)
            else:
                typed_params[pname] = val
                
        # Initialize strategy
        if req.strategy == "pairs_trading":
            if len(assets) < 2:
                raise HTTPException(status_code=400, detail="Pairs trading requires exactly 2 assets")
            strategy = strategy_class(asset1=assets[0], asset2=assets[1], **typed_params)
        else:
            strategy = strategy_class(**typed_params)
            
        # Re-pack config for portfolio / backtester
        config = {
            "assets": assets,
            "start_date": req.start_date,
            "end_date": req.end_date,
            "strategy": req.strategy,
            "risk": req.risk.model_dump()
        }
        
        # Run Backtester
        backtester = Backtester(data, strategy, config)
        res = backtester.run()
        
        portfolio_series = res['portfolio_series']
        portfolio = res['portfolio']
        cagr = res['cagr']
        
        # Calculate returns & risk metrics
        returns = calculate_daily_returns(portfolio_series)
        sharpe = calculate_sharpe_ratio(returns)
        sortino = calculate_sortino_ratio(returns)
        mdd = calculate_max_drawdown(portfolio_series)
        
        # Calculate Trade metrics
        trade_log_df = portfolio.get_trade_log_df()
        trade_metrics = calculate_trade_metrics(trade_log_df)
        
        # Create Drawdown Series
        peak = portfolio_series.expanding(min_periods=1).max()
        drawdown_series = (portfolio_series / peak) - 1
        
        # Calculate Benchmark (Buy and Hold of first asset)
        first_asset = assets[0]
        asset_df = data[first_asset] if isinstance(data, dict) else data
        
        # Align index
        common_idx = portfolio_series.index.intersection(asset_df.index)
        asset_prices = asset_df.loc[common_idx, 'Close']
        benchmark_series = (asset_prices / asset_prices.iloc[0]) * portfolio_series.iloc[0]
        
        # Prepare Equity Curve array
        equity_curve = []
        for dt in common_idx:
            dt_str = str(dt.date())
            equity_curve.append({
                "date": dt_str,
                "portfolio": float(portfolio_series.loc[dt]),
                "benchmark": float(benchmark_series.loc[dt]),
                "drawdown": float(drawdown_series.loc[dt]) * 100.0 # as percentage
            })
            
        # Prepare Price series + Indicators
        price_chart_data = []
        
        if req.strategy == "pairs_trading":
            df1 = data[assets[0]]
            df2 = data[assets[1]]
            c_index = df1.index.intersection(df2.index)
            s1 = df1.loc[c_index, 'Close']
            s2 = df2.loc[c_index, 'Close']
            spread = s1 / s2
            
            win = typed_params.get("window", 60)
            rolling_mean = spread.rolling(window=win).mean()
            rolling_std = spread.rolling(window=win).std()
            z_score = ((spread - rolling_mean) / rolling_std).fillna(0)
            
            # Check cointegration test
            coint_stat, coint_pvalue = strategy.test_cointegration(s1, s2)
            coint_results = {
                "t_stat": float(coint_stat),
                "p_value": float(coint_pvalue),
                "is_cointegrated": bool(coint_pvalue < 0.05)
            }
            
            for dt in c_index.intersection(portfolio_series.index):
                dt_str = str(dt.date())
                price_chart_data.append({
                    "date": dt_str,
                    "asset1_price": float(s1.loc[dt]),
                    "asset2_price": float(s2.loc[dt]),
                    "spread": float(spread.loc[dt]),
                    "z_score": float(z_score.loc[dt]),
                    "upper_threshold": float(strategy.z_threshold),
                    "lower_threshold": float(-strategy.z_threshold)
                })
        else:
            df = data[assets[0]] if isinstance(data, dict) else data
            close = df['Close']
            
            fast_ma = None
            slow_ma = None
            rsi = None
            upper_band = None
            lower_band = None
            
            if req.strategy == "moving_average":
                fast_ma = calculate_sma(close, typed_params["fast_window"])
                slow_ma = calculate_sma(close, typed_params["slow_window"])
            elif req.strategy == "momentum":
                rsi = calculate_rsi(close, typed_params["rsi_window"])
            elif req.strategy == "mean_reversion":
                rolling_mean = close.rolling(window=typed_params["window"]).mean()
                rolling_std = close.rolling(window=typed_params["window"]).std()
                fast_ma = rolling_mean # map to fast_ma slot for display
                # upper/lower z threshold mapped to prices
                upper_band = rolling_mean + (rolling_std * typed_params["threshold"])
                lower_band = rolling_mean - (rolling_std * typed_params["threshold"])
            elif req.strategy == "bollinger_bands":
                rolling_mean = close.rolling(window=typed_params["window"]).mean()
                rolling_std = close.rolling(window=typed_params["window"]).std()
                fast_ma = rolling_mean
                upper_band = rolling_mean + (rolling_std * typed_params["num_std"])
                lower_band = rolling_mean - (rolling_std * typed_params["num_std"])
                
            for dt in df.index.intersection(portfolio_series.index):
                dt_str = str(dt.date())
                price_chart_data.append({
                    "date": dt_str,
                    "price": float(close.loc[dt]),
                    "fast_ma": nan_to_none(fast_ma.loc[dt]) if fast_ma is not None else None,
                    "slow_ma": nan_to_none(slow_ma.loc[dt]) if slow_ma is not None else None,
                    "rsi": nan_to_none(rsi.loc[dt]) if rsi is not None else None,
                    "upper_band": nan_to_none(upper_band.loc[dt]) if upper_band is not None else None,
                    "lower_band": nan_to_none(lower_band.loc[dt]) if lower_band is not None else None,
                })
            coint_results = None
            
        # Formatted trade log
        trade_log = []
        if not trade_log_df.empty:
            # Drop timezone if present in date
            if hasattr(trade_log_df['Date'].iloc[0], 'tz'):
                trade_log_df['Date'] = trade_log_df['Date'].dt.tz_localize(None)
                
            for _, r in trade_log_df.iterrows():
                trade_log.append({
                    "date": str(r['Date'].date()),
                    "ticker": r['Ticker'],
                    "action": r['Action'],
                    "quantity": float(r['Quantity']),
                    "price": float(r['Price']),
                    "commission": float(r['Commission']),
                    "value": float(r['Value']),
                    "realized_pnl": float(r['Realized_PnL'])
                })
                
        # Heatmap calculations
        heatmap_data = []
        if not returns.empty:
            monthly_rets = (1 + returns).resample('ME').prod() - 1
            for dt, val in monthly_rets.items():
                heatmap_data.append({
                    "year": int(dt.year),
                    "month": int(dt.month),
                    "return": float(val) * 100.0  # as percentage
                })
                
        return sanitize_json({
            "summary": {
                "initial_value": float(portfolio.initial_cash),
                "final_value": float(portfolio_series.iloc[-1]),
                "cagr": float(cagr) * 100.0,
                "sharpe": float(sharpe),
                "sortino": float(sortino),
                "max_drawdown": float(mdd) * 100.0,
                "win_rate": float(trade_metrics.get("Win Rate", 0.0)) * 100.0,
                "profit_factor": float(trade_metrics.get("Profit Factor", 0.0)) if trade_metrics.get("Profit Factor") != float('inf') else "∞"
            },
            "equity_curve": equity_curve,
            "price_chart_data": price_chart_data,
            "trade_log": trade_log,
            "heatmap": heatmap_data,
            "cointegration": coint_results
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/grid_search")
def run_grid_search_endpoint(req: GridSearchRequest):
    try:
        assets = [a.strip().upper() for a in req.assets if a.strip()]
        strategy_class = STRATEGY_MAP.get(req.strategy)
        if not strategy_class:
            raise HTTPException(status_code=400, detail=f"Strategy '{req.strategy}' not found")
            
        data = fetch_data(assets, req.start_date, req.end_date)
        
        # Set up full config dict
        config = {
            "assets": assets,
            "start_date": req.start_date,
            "end_date": req.end_date,
            "strategy": req.strategy,
            "risk": req.risk.model_dump()
        }
        
        best_params, best_result = run_grid_search(data, strategy_class, req.param_grid, config)
        
        return sanitize_json({
            "best_params": best_params,
            "best_cagr": float(best_result['cagr']) * 100.0,
            "final_value": float(best_result['portfolio_series'].iloc[-1])
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/walk_forward")
def run_walk_forward_endpoint(req: WalkForwardRequest):
    try:
        assets = [a.strip().upper() for a in req.assets if a.strip()]
        strategy_class = STRATEGY_MAP.get(req.strategy)
        if not strategy_class:
            raise HTTPException(status_code=400, detail=f"Strategy '{req.strategy}' not found")
            
        data = fetch_data(assets, req.start_date, req.end_date)
        
        config = {
            "assets": assets,
            "start_date": req.start_date,
            "end_date": req.end_date,
            "strategy": req.strategy,
            "risk": req.risk.model_dump()
        }
        
        results = run_walk_forward(
            data, strategy_class, req.param_grid, config,
            train_days=req.train_days, test_days=req.test_days
        )
        
        formatted_results = []
        for r in results:
            formatted_results.append({
                "period": r["period"],
                "best_params": r["best_params"],
                "cagr": float(r["cagr"]) * 100.0,
                "final_value": float(r["portfolio_series"].iloc[-1])
            })
            
        return sanitize_json(formatted_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/compare")
def run_comparison_endpoint(req: BacktestRequest):
    try:
        assets = [a.strip().upper() for a in req.assets if a.strip()]
        data = fetch_data(assets, req.start_date, req.end_date)
        
        config = {
            "assets": assets,
            "start_date": req.start_date,
            "end_date": req.end_date,
            "risk": req.risk.model_dump()
        }
        
        results = []
        for name, strategy_class in STRATEGY_MAP.items():
            # Skip pairs trading if only one asset
            if name == "pairs_trading" and len(assets) < 2:
                continue
                
            if name == "pairs_trading":
                strategy = strategy_class(asset1=assets[0], asset2=assets[1])
            else:
                strategy = strategy_class()
                
            try:
                backtester = Backtester(data, strategy, config)
                res = backtester.run()
                
                returns = calculate_daily_returns(res['portfolio_series'])
                sharpe = calculate_sharpe_ratio(returns)
                mdd = calculate_max_drawdown(res['portfolio_series'])
                
                results.append({
                    "strategy_id": name,
                    "strategy_name": strategy.name,
                    "cagr": float(res['cagr']) * 100.0,
                    "sharpe": float(sharpe),
                    "max_drawdown": float(mdd) * 100.0,
                    "final_value": float(res['portfolio_series'].iloc[-1])
                })
            except Exception as strat_err:
                print(f"Error running comparison for {name}: {strat_err}")
                
        return sanitize_json(results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)

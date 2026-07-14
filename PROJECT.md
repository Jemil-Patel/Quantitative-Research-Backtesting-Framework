# Quantitative Research & Backtesting Framework

A modular quantitative research and backtesting platform, built for a 36-hour sprint and optimized for quant/trading firm recruiting (e.g., Futures First).

---

## 1. Vision

Instead of "another trading bot," this is a **modular quantitative research framework** — a lightweight analogue to QuantConnect LEAN, Backtrader, Zipline, or WorldQuant BRAIN's research layer.

The framework should let a user:
- Fetch market data
- Develop strategies
- Simulate execution
- Backtest over historical data
- Analyze risk
- Compare strategies
- Optimize parameters

The end story it should tell an interviewer: *understands quantitative strategy research AND market microstructure.*

---

## 2. Tech Stack

**Language:** Python (industry standard for quant research)

**Core libraries:**
- pandas
- numpy
- scipy
- statsmodels
- matplotlib
- yfinance
- requests
- plotly (optional)

**Deliberately avoided (no value-add for this project):** TensorFlow, PyTorch, LangChain, FastAPI

> Note: an earlier discussion explored a React + FastAPI hybrid (full dashboard, REST API, Recharts frontend) as an alternative framing — see [Appendix: Alternative UI Track](#appendix-alternative-ui-track-optional) if there's time left over and a UI layer is wanted for demo polish. The primary track below is pure-Python and CLI-driven so the whole thing runs with `python main.py` and no dataset downloads.

---

## 3. Data Source

**Recommendation: `yfinance`** — free, no API key, covers stocks/ETFs/indices/forex/crypto.

```python
AAPL
SPY
^NSEI
RELIANCE.NS
BTC-USD
```

Alternatives considered: Polygon (professional, needs API key), AlphaVantage (rate limited), TwelveData. Not needed for this project — don't store datasets, fetch dynamically so an evaluator can clone and run immediately.

---

## 4. Architecture

```
Market Data
  ↓
Preprocessing
  ↓
Indicators
  ↓
Strategy
  ↓
Signal
  ↓
Risk Manager
  ↓
Execution Engine
  ↓
Portfolio
  ↓
Analytics
  ↓
Visualization
```

Everything modular — each stage swappable/testable independently.

---

## 5. Folder Structure

```
quant-backtester/
│
├── config/
├── strategies/
│      moving_average.py
│      momentum.py
│      mean_reversion.py
│      pairs_trading.py
│
├── execution/
│      execution_engine.py
│
├── portfolio/
│      portfolio.py
│
├── analytics/
│      metrics.py
│
├── indicators/
│      sma.py
│      ema.py
│      rsi.py
│
├── data/
│      yahoo.py
│
├── plots/
├── utils/
├── main.py
```

---

## 6. Roadmap (checklist)

> Agent instructions: check a box `[x]` only when the feature is implemented, tested (runs without error on at least one real ticker), and committed. Work top to bottom within a level before moving to the next level, except where a level is marked optional/stretch.

### Level 1 — Foundation (⭐)
- [x] Fetch historical market data (AAPL, MSFT, SPY, BTC → DataFrame)
- [x] CLI: choose asset, date range, strategy
- [x] Data preprocessing (missing values, duplicate timestamps, sorting)
- [x] Candlestick chart
- [x] Portfolio tracking (cash, holdings, current value)
- [x] Buy/Sell execution logic
- [x] Trade log (date, price, quantity, PnL)

### Level 2 — Core Strategy Layer (⭐⭐)
- [x] SMA indicator
- [x] EMA indicator
- [x] RSI indicator
- [x] MACD indicator
- [x] Strategy interface (`class Strategy`, `generate_signal()`)
- [x] Moving Average strategy
- [x] Momentum strategy
- [x] Buy/Sell markers on price chart
- [x] Equity curve
- [x] Daily returns

### Level 3 — Realism & Metrics (⭐⭐⭐)
- [x] Transaction costs (brokerage)
- [x] Slippage modeling
- [x] Position sizing (fixed quantity / fixed capital / % capital)
- [x] Risk manager (prevent negative cash, leverage limits)
- [x] Stop loss
- [x] Take profit
- [x] Benchmark comparison (vs. buy-and-hold)
- [x] Multi-asset support
- [x] Equal-weight portfolio allocation
- [x] Performance metrics: CAGR, Annual Return, Sharpe, Sortino, Max Drawdown, Win Rate, Profit Factor
- [x] Drawdown plot
- [x] Monthly return heatmap

### Level 4 — Advanced Research (⭐⭐⭐⭐)
- [x] Mean Reversion strategy (rolling mean)
- [x] Bollinger Bands strategy
- [x] **Pairs Trading strategy** (spread → z-score → trade) — priority feature
- [x] Cointegration test (statsmodels)
- [x] Volatility targeting
- [x] Kelly Criterion sizing
- [x] Walk-forward testing (train/test/train/test)
- [x] Parameter grid search (auto-select best config)
- [x] Config file (`config.json`) instead of hardcoded params
- [x] Multi-strategy comparison (Momentum vs. Mean Reversion vs. Pairs)
- [x] Portfolio rebalancing (monthly/quarterly)


### Level 5 — Only if time remains (⭐⭐⭐⭐⭐)
- [x] Event-driven engine (Market Event → Signal Event → Order Event → Execution Event → Portfolio Event)
- [x] Execution engine order types (Market, Limit, Stop)
- [x] IOC (immediate-or-cancel)
- [x] FOK (fill-or-kill)
- [x] Partial fills
- [x] Latency simulation
- [x] Order queue
- [x] Replay engine
- [x] Live data streaming (Stubbed)
- [x] Paper trading (Stubbed)

### Stretch goals (only if everything above is done early)
- [ ] Factor investing (Momentum, Value, Quality)
- [ ] Multi-factor ranking engine
- [ ] Bayesian parameter optimization
- [ ] Monte Carlo portfolio simulation
- [ ] Risk parity allocation
- [ ] Black-Litterman portfolio optimization
- [ ] Options pricing (Black-Scholes)
- [ ] Greeks calculator
- [ ] Interactive dashboard (Plotly/Dash or Streamlit)

---

## 7. 36-Hour Implementation Order

1. **Level 1** — all features (foundation)
2. **Level 2** — SMA, EMA, RSI, strategy interface, moving average strategy, equity curve
3. **Level 3** — transaction costs, slippage, stop-loss/take-profit, performance metrics, benchmark comparison
4. **Level 4** — pairs trading + cointegration, parameter grid search, config file
5. **Level 5** — only if time remains


**Realistic target for 36 hours:** Levels 1–3 complete, Pairs Trading from Level 4.

---

## 8. Resume Impact vs. Effort

| Feature | Resume Value | Effort | ROI |
|---|:---:|:---:|:---:|
| Modular architecture | ⭐⭐⭐⭐⭐ | ⭐⭐ | Excellent |
| Performance metrics | ⭐⭐⭐⭐⭐ | ⭐⭐ | Excellent |
| Transaction costs & slippage | ⭐⭐⭐⭐⭐ | ⭐⭐ | Excellent |
| Pairs trading | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Excellent |
| Config-driven backtests | ⭐⭐⭐⭐ | ⭐⭐ | High |
| Parameter optimization | ⭐⭐⭐⭐ | ⭐⭐⭐ | High |

| Event-driven engine | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Do only if time permits |

---

## Appendix: Alternative UI Track (optional)

If there's spare time and a visual demo layer is wanted on top of the core engine:

- **Frontend:** React + TypeScript + Vite + Tailwind + Recharts
- **Backend:** FastAPI wrapping the same core engine (`POST /backtest`, `GET /history`, `GET /strategies`, `POST /optimize`)
- **Rationale:** looks like a real product rather than a Streamlit "student dashboard"; useful for interviews outside pure-quant contexts

This is explicitly out of scope for the core 36-hour research-framework track and should only be attempted after Level 3 + Pairs Trading are done.
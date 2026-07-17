# Quantitative Research & Backtesting Framework

A professional, high-performance, and modular quantitative research and backtesting platform designed for strategy development, risk management, parameter optimization, and multi-asset simulation. 

This platform implements both a **fast vectorized backtester** (ideal for rapid research and hyperparameter sweeps) and a **realistic event-driven backtesting engine** (simulating realistic trade execution and market microstructure). It also comes with a FastAPI backend server and an interactive React web dashboard.

---

## 🚀 Key Features

*   **Dual-Backtesting Engines:**
    *   **Vectorized Engine:** Superfast historical simulations, ideal for parameter sweeps (Grid Search) and Walk-Forward optimization.
    *   **Event-Driven Engine:** Simulates realistic execution queues (Market, Limit, Stop, IOC, and FOK orders) and market microstructure (latency, slippage, and transaction commissions).
*   **Built-in Strategies:**
    *   `moving_average`: Simple Moving Average (SMA) crossover.
    *   `momentum`: Relative Strength Index (RSI) momentum.
    *   `mean_reversion`: Rolling Z-score mean reversion.
    *   `bollinger_bands`: Bollinger Bands volatility-channel crossing.
    *   `pairs_trading`: Cointegrated pairs trading strategy (calculates rolling spread, Z-score, and performs statistical Engle-Granger cointegration testing).
*   **Realistic Execution & Market Modeling:**
    *   **Transaction Costs:** Model percentage-based brokerage/broker fees.
    *   **Slippage Model:** Account for execution price degradation.
    *   **Position Sizing:** Support for fixed quantity, fixed capital allocation, and dynamic fraction sizing via the Kelly Criterion.
*   **Robust Risk Management:**
    *   Hard Stop-Loss and Take-Profit rules monitored per asset.
    *   Leverage limit controls and negative-cash protection mechanisms.
*   **Validation & Optimization:**
    *   **Grid Search:** Sweeps hyperparameter combinations to find optimal configurations.
    *   **Walk-Forward Validation:** Evaluates strategies on rolling out-of-sample test windows to guard against backtest overfitting.
*   **Comprehensive Performance Analytics:**
    *   Annualized Return, CAGR, Sharpe Ratio, Sortino Ratio, Maximum Drawdown, Win Rate, and Profit Factor.
    *   Underwater Drawdown curves and monthly returns heatmap calculations.
*   **Interactive React Dashboard:**
    *   Modern React + TypeScript + Vite + TailwindCSS + Recharts visual dashboard to configure backtests, run grid search, view strategy comparisons, and inspect trade logs.

---

## 📐 Architecture & Modules

```
                        Market Data (Yahoo Finance / CSV)
                                       │
                                       ▼
                              Indicators Library
                               (SMA, EMA, RSI)
                                       │
                                       ▼
                              Strategy Interface
                         (Signal Generation Engine)
                                       │
                                       ▼
                                  Risk Manager
                     (Stop Loss / Take Profit / Kelly Sizing)
                                       │
                                       ▼
                                Execution Engine
                        (Commissions / Slippage Models)
                                       │
                                       ▼
                               Portfolio Tracker
                         (Cash, Holdings, Trade Logs)
                                  │         │
                   ┌──────────────┘         └──────────────┐
                   ▼                                       ▼
             Analytics Engine                         Visualizations
      (CAGR, Sharpe, Sortino, Drawdown)        (React Frontend / Recharts)
```

### File & Directory Structure

```
Quantitative-Research-Backtesting-Framework/
├── main.py                 # Core CLI entrypoint for backtesting, optimization, and comparison
├── main_event.py           # Event-driven backtester runner
├── server.py               # FastAPI server exposing REST endpoints for the React frontend
├── requirements.txt        # Python backend dependencies
├── PROJECT.md              # Original design blueprint, checklist, and roadmap
│
├── config/                 # Configuration files
│   └── config.json         # Strategy, asset list, and parameter optimization configs
│
├── data/                   # Data fetching and preprocessing layer
│   ├── yahoo.py            # yfinance integration for dynamic data loading
│   └── preprocessing.py    # Handling missing values, duplicates, and sorting
│
├── indicators/             # Core mathematical formulas & indicators
│   ├── sma.py              # Simple Moving Average
│   ├── ema.py              # Exponential Moving Average
│   └── rsi.py              # Relative Strength Index
│
├── strategies/             # Concrete strategy implementations
│   ├── strategy.py         # Abstract base class for vectorized strategies
│   ├── moving_average.py   # SMA crossover logic
│   ├── momentum.py         # RSI momentum logic
│   ├── mean_reversion.py   # Z-Score mean reversion
│   ├── bollinger_bands.py  # Bollinger Bands strategy
│   ├── pairs_trading.py    # Statistical arbitrage / Cointegration trading
│   ├── event_strategy.py   # Base event-driven strategy class
│   └── event_moving_average.py # Event-driven Moving Average implementation
│
├── execution/              # Simulators and run loops
│   ├── backtester.py       # Vectorized backtesting runner
│   ├── execution_engine.py # Vectorized slippage & fee modeler
│   ├── grid_search.py      # Vectorized hyperparameter optimizer
│   ├── walk_forward.py     # Walk-forward optimization engine
│   ├── event_engine.py     # Event broker (Market, Signal, Order, Fill events)
│   └── event_execution.py  # Event-driven execution and order-type engine
│
├── portfolio/              # Holdings tracking & Risk management
│   ├── portfolio.py        # Portfolio ledger (holdings, cash, trade log)
│   ├── event_portfolio.py  # Event-driven portfolio updates & filling
│   └── risk_manager.py     # Stop-loss, take-profit, & sizing logic
│
├── analytics/              # Performance measurement mathematics
│   └── metrics.py          # CAGR, Sharpe, Sortino, Drawdown, Profit Factor, Win Rate
│
└── frontend/               # React Dashboard (Vite + TS + Tailwind + Recharts)
    ├── src/
    │   ├── App.tsx         # Dashboard application and UI layout
    │   ├── index.css       # Tailwind & styling tokens
    │   └── main.tsx        # React entrypoint
    ├── package.json        # Frontend configuration and scripts
    └── tsconfig.json       # TypeScript configuration
```

---

## 🛠️ Setup & Installation

### Backend Setup (Python)

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/Quantitative-Research-Backtesting-Framework.git
    cd Quantitative-Research-Backtesting-Framework
    ```

2.  **Create and Activate a Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Backend Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Frontend Setup (React)

1.  **Navigate to the Frontend Directory:**
    ```bash
    cd frontend
    ```

2.  **Install Node Dependencies:**
    ```bash
    npm install
    ```

---

## 💻 Usage Guide

### 1. Vectorized Command Line Interface (`main.py`)

You can run standard backtests, compare different strategies, optimize parameters, or validate strategies out-of-sample via `main.py`:

*   **Run a Standard Backtest:**
    Runs the strategy configured in `config/config.json`.
    ```bash
    python main.py --mode backtest
    ```

*   **Compare Strategies:**
    Simulates all implemented strategies over the configured assets and displays a comparative metrics table.
    ```bash
    python main.py --mode compare
    ```

*   **Run Parameter Grid Search:**
    Performs a grid search sweep across the parameter ranges specified in the `grid_search` section of the config.
    ```bash
    python main.py --mode grid_search
    ```

*   **Run Walk-Forward Optimization:**
    Evaluates out-of-sample performance over rolling windows.
    ```bash
    python main.py --mode walk_forward
    ```

### 2. Event-Driven Simulation CLI (`main_event.py`)

Run realistic event loop simulations (Market Event $\rightarrow$ Signal Event $\rightarrow$ Order Event $\rightarrow$ Fill Event):
```bash
python main_event.py --asset AAPL
```

### 3. Interactive Web Dashboard

To run the full stack with the interactive UI:

1.  **Start the FastAPI Server:**
    In the root directory with virtual environment activated:
    ```bash
    python server.py
    ```
    This launches the backend API on `http://localhost:8000`.

2.  **Start the React Dev Server:**
    In the `frontend/` directory:
    ```bash
    npm run dev
    ```
    This launches the interface on `http://localhost:5173`. Open it in your browser to start building, running, and visualizing strategies visually!

---

## 📝 Mathematical Models Implemented

### 1. Cointegration & Pairs Trading
For Pairs Trading (`pairs_trading.py`), we implement the Engle-Granger two-step method to identify cointegrated relationships between two assets ($S_1$ and $S_2$).
*   **Spread Calculation:** 
    $$\text{Spread}_t = S_{1,t} - \beta \cdot S_{2,t}$$
    where $\beta$ is computed via rolling Ordinary Least Squares (OLS) regression.
*   **Cointegration Test:** Utilizes `statsmodels.tsa.stattools.coint` to calculate the ADF test statistic and p-value. A p-value $< 0.05$ indicates a cointegrated relationship.
*   **Z-score:**
    $$Z_t = \frac{\text{Spread}_t - \mu_{\text{Spread}}}{\sigma_{\text{Spread}}}$$
    Trading signals are generated when $|Z_t| > \text{z\_threshold}$.

### 2. Sizing via the Kelly Criterion
Dynamic sizing scales orders using the probability of a win ($p$) and win/loss ratio ($b$):
$$f^* = p - \frac{1 - p}{b}$$
This calculates the optimal allocation fraction to maximize long-term wealth growth rate.

### 3. Performance Metrics
*   **Sharpe Ratio:** Evaluates returns per unit of total risk.
    $$\text{Sharpe} = \sqrt{252} \cdot \frac{\mu_{\text{excess}}}{\sigma_{\text{excess}}}$$
*   **Sortino Ratio:** Focuses only on downside deviations.
    $$\text{Sortino} = \sqrt{252} \cdot \frac{\mu_{\text{excess}}}{\sigma_{\text{downside}}}$$
*   **Maximum Drawdown (Max DD):** Captures the largest peak-to-trough decline.
    $$\text{Max DD} = \max_t \left( \frac{\text{Peak} - P_t}{\text{Peak}} \right)$$

---

## 📊 License
This project is open-source and available under the MIT License.
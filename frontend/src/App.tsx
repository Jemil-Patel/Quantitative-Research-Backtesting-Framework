import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  Settings, 
  Play, 
  Activity, 
  Grid, 
  BarChart2, 
  List, 
  Layers, 
  RefreshCw, 
  Sliders, 
  ShieldAlert,
  Info
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ReferenceLine,
  ComposedChart
} from 'recharts';

const API_BASE = "http://localhost:8000";

interface StrategyParameter {
  name: string;
  type: string;
  default: any;
  min: number;
  max: number;
}

interface StrategyMeta {
  id: string;
  name: string;
  description: string;
  parameters: StrategyParameter[];
}

interface TradeLogItem {
  date: string;
  ticker: string;
  action: string;
  quantity: number;
  price: number;
  commission: number;
  value: number;
  realized_pnl: number;
}

interface EquityCurvePoint {
  date: string;
  portfolio: number;
  benchmark: number;
  drawdown: number;
}

interface PriceChartPoint {
  date: string;
  price?: number;
  fast_ma?: number | null;
  slow_ma?: number | null;
  rsi?: number | null;
  upper_band?: number | null;
  lower_band?: number | null;
  asset1_price?: number;
  asset2_price?: number;
  spread?: number;
  z_score?: number;
  upper_threshold?: number;
  lower_threshold?: number;
  // added dynamically
  buy_price?: number | null;
  sell_price?: number | null;
}

interface HeatmapPoint {
  year: number;
  month: number;
  return: number;
}

interface CointegrationResult {
  t_stat: number;
  p_value: number;
  is_cointegrated: boolean;
}

interface BacktestSummary {
  initial_value: number;
  final_value: number;
  cagr: number;
  sharpe: number;
  sortino: number;
  max_drawdown: number;
  win_rate: number;
  profit_factor: string | number;
}

interface BacktestResponse {
  summary: BacktestSummary;
  equity_curve: EquityCurvePoint[];
  price_chart_data: PriceChartPoint[];
  trade_log: TradeLogItem[];
  heatmap: HeatmapPoint[];
  cointegration: CointegrationResult | null;
}

interface GridResult {
  best_params: Record<string, any>;
  best_cagr: number;
  final_value: number;
}

interface WalkForwardPeriod {
  period: string;
  best_params: Record<string, any>;
  cagr: number;
  final_value: number;
}

interface ComparisonResultItem {
  strategy_id: string;
  strategy_name: string;
  cagr: number;
  sharpe: number;
  max_drawdown: number;
  final_value: number;
}

export default function App() {
  // App-wide data
  const [strategies, setStrategies] = useState<StrategyMeta[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  // Form input states
  const [assets, setAssets] = useState<string>("AAPL");
  const [startDate, setStartDate] = useState<string>("2023-01-01");
  const [endDate, setEndDate] = useState<string>("2023-12-31");
  const [selectedStrategy, setSelectedStrategy] = useState<string>("moving_average");
  const [strategyParams, setStrategyParams] = useState<Record<string, any>>({});
  
  // Grid search state inputs (comma-separated strings)
  const [gridParamsInput, setGridParamsInput] = useState<Record<string, string>>({
    fast_window: "20, 50",
    slow_window: "100, 200",
    rsi_window: "10, 14",
    overbought: "70, 80",
    oversold: "20, 30",
    window: "20, 30",
    threshold: "1.5, 2.0",
    num_std: "1.5, 2.0",
    z_threshold: "1.5, 2.0"
  });

  // Risk control state
  const [stopLossPct, setStopLossPct] = useState<number>(5);
  const [takeProfitPct, setTakeProfitPct] = useState<number>(10);
  const [positionSizePct, setPositionSizePct] = useState<number>(100);
  
  // Execution Mode: backtest, grid_search, walk_forward, compare
  const [executionMode, setExecutionMode] = useState<string>("backtest");
  
  // Results
  const [backtestResult, setBacktestResult] = useState<BacktestResponse | null>(null);
  const [gridResult, setGridResult] = useState<GridResult | null>(null);
  const [walkForwardResult, setWalkForwardResult] = useState<WalkForwardPeriod[] | null>(null);
  const [comparisonResult, setComparisonResult] = useState<ComparisonResultItem[] | null>(null);
  
  // Tab control
  const [activeTab, setActiveTab] = useState<string>("backtest");
  
  // Fetch strategies metadata
  useEffect(() => {
    fetch(`${API_BASE}/api/strategies`)
      .then(res => {
        if (!res.ok) throw new Error("Failed to load strategies config");
        return res.json();
      })
      .then((data: StrategyMeta[]) => {
        setStrategies(data);
        if (data.length > 0) {
          // Initialize defaults for the active strategy
          const ma = data.find(s => s.id === "moving_average") || data[0];
          setSelectedStrategy(ma.id);
          const initialParams: Record<string, any> = {};
          ma.parameters.forEach(p => {
            initialParams[p.name] = p.default;
          });
          setStrategyParams(initialParams);
        }
      })
      .catch(err => {
        setError(err.message);
      });
  }, []);

  // Update parameters when selected strategy changes
  const handleStrategyChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const stratId = e.target.value;
    setSelectedStrategy(stratId);
    
    // Auto toggle assets helper: Pairs trading requires exactly 2 assets
    if (stratId === "pairs_trading") {
      if (assets.split(",").length < 2) {
        setAssets("AAPL, MSFT");
      }
    } else {
      if (assets.split(",").length >= 2) {
        setAssets(assets.split(",")[0].trim());
      }
    }
    
    const meta = strategies.find(s => s.id === stratId);
    if (meta) {
      const initialParams: Record<string, any> = {};
      meta.parameters.forEach(p => {
        initialParams[p.name] = p.default;
      });
      setStrategyParams(initialParams);
    }
  };

  const handleParamSliderChange = (name: string, val: number) => {
    setStrategyParams(prev => ({
      ...prev,
      [name]: val
    }));
  };

  const handleGridParamChange = (name: string, value: string) => {
    setGridParamsInput(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Run the selected routine
  const handleRun = async () => {
    setLoading(true);
    setError(null);
    setBacktestResult(null);
    setGridResult(null);
    setWalkForwardResult(null);
    setComparisonResult(null);
    
    const assetList = assets.split(",").map(a => a.trim()).filter(Boolean);
    if (assetList.length === 0) {
      setError("Please input at least one asset ticker symbol.");
      setLoading(false);
      return;
    }
    
    if (selectedStrategy === "pairs_trading" && assetList.length < 2) {
      setError("Pairs trading strategy requires at least two asset tickers (comma-separated, e.g. AAPL, MSFT).");
      setLoading(false);
      return;
    }

    const riskPayload = {
      stop_loss_pct: stopLossPct / 100.0,
      take_profit_pct: takeProfitPct / 100.0,
      position_size_pct: positionSizePct / 100.0
    };

    try {
      if (executionMode === "backtest") {
        const response = await fetch(`${API_BASE}/api/backtest`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            assets: assetList,
            start_date: startDate,
            end_date: endDate,
            strategy: selectedStrategy,
            params: strategyParams,
            risk: riskPayload
          })
        });
        
        if (!response.ok) {
          const detail = await response.json().catch(() => ({ detail: "API server error" }));
          throw new Error(detail.detail || "Backtest failed");
        }
        
        const data: BacktestResponse = await response.json();
        
        // Enrich price chart data with signals for plotting
        const tradeMap: Record<string, string> = {};
        data.trade_log.forEach(t => {
          tradeMap[t.date] = t.action;
        });
        
        const enrichedPriceData = data.price_chart_data.map(p => {
          const tradeAction = tradeMap[p.date];
          let buyPrice = null;
          let sellPrice = null;
          
          if (tradeAction === "BUY") {
            buyPrice = p.price !== undefined ? p.price : (p.spread !== undefined ? p.spread : null);
          } else if (tradeAction === "SELL") {
            sellPrice = p.price !== undefined ? p.price : (p.spread !== undefined ? p.spread : null);
          }
          
          return {
            ...p,
            buy_price: buyPrice,
            sell_price: sellPrice
          };
        });
        
        setBacktestResult({
          ...data,
          price_chart_data: enrichedPriceData
        });
        setActiveTab("backtest");
        
      } else if (executionMode === "grid_search") {
        // Parse grid params
        const parsedGrid: Record<string, any[]> = {};
        const meta = strategies.find(s => s.id === selectedStrategy);
        if (meta) {
          meta.parameters.forEach(p => {
            const inputVal = gridParamsInput[p.name] || `${p.default}`;
            const values = inputVal.split(",").map(v => {
              const num = parseFloat(v.trim());
              return p.type === "int" ? Math.round(num) : num;
            }).filter(n => !isNaN(n));
            parsedGrid[p.name] = values.length > 0 ? values : [p.default];
          });
        }
        
        const response = await fetch(`${API_BASE}/api/grid_search`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            assets: assetList,
            start_date: startDate,
            end_date: endDate,
            strategy: selectedStrategy,
            param_grid: parsedGrid,
            risk: riskPayload
          })
        });
        
        if (!response.ok) {
          const detail = await response.json().catch(() => ({ detail: "API server error" }));
          throw new Error(detail.detail || "Grid search failed");
        }
        
        const data: GridResult = await response.json();
        setGridResult(data);
        setActiveTab("grid_wf");
        
      } else if (executionMode === "walk_forward") {
        // Parse grid params
        const parsedGrid: Record<string, any[]> = {};
        const meta = strategies.find(s => s.id === selectedStrategy);
        if (meta) {
          meta.parameters.forEach(p => {
            const inputVal = gridParamsInput[p.name] || `${p.default}`;
            const values = inputVal.split(",").map(v => {
              const num = parseFloat(v.trim());
              return p.type === "int" ? Math.round(num) : num;
            }).filter(n => !isNaN(n));
            parsedGrid[p.name] = values.length > 0 ? values : [p.default];
          });
        }
        
        const response = await fetch(`${API_BASE}/api/walk_forward`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            assets: assetList,
            start_date: startDate,
            end_date: endDate,
            strategy: selectedStrategy,
            param_grid: parsedGrid,
            risk: riskPayload,
            train_days: 252,
            test_days: 63
          })
        });
        
        if (!response.ok) {
          const detail = await response.json().catch(() => ({ detail: "API server error" }));
          throw new Error(detail.detail || "Walk forward failed");
        }
        
        const data: WalkForwardPeriod[] = await response.json();
        setWalkForwardResult(data);
        setActiveTab("grid_wf");
        
      } else if (executionMode === "compare") {
        const response = await fetch(`${API_BASE}/api/compare`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            assets: assetList,
            start_date: startDate,
            end_date: endDate,
            strategy: selectedStrategy, // dummy
            params: {},
            risk: riskPayload
          })
        });
        
        if (!response.ok) {
          const detail = await response.json().catch(() => ({ detail: "API server error" }));
          throw new Error(detail.detail || "Strategy comparison failed");
        }
        
        const data: ComparisonResultItem[] = await response.json();
        setComparisonResult(data);
        setActiveTab("compare");
      }
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred during execution.");
    } finally {
      setLoading(false);
    }
  };

  // Helper colors for monthly heatmap
  const getHeatmapColor = (val: number) => {
    if (val === 0) return 'rgba(255, 255, 255, 0.05)';
    if (val > 0) {
      // scale opacity from 0.1 to 0.9 based on returns up to 15%
      const opacity = Math.min(0.9, Math.max(0.15, val / 12));
      return `rgba(16, 185, 129, ${opacity})`;
    } else {
      const opacity = Math.min(0.9, Math.max(0.15, Math.abs(val) / 12));
      return `rgba(239, 68, 68, ${opacity})`;
    }
  };

  const getHeatmapText = (val: number) => {
    return val > 0 ? `+${val.toFixed(1)}%` : `${val.toFixed(1)}%`;
  };

  // Group monthly heatmap by year
  const renderHeatmap = () => {
    if (!backtestResult || !backtestResult.heatmap || backtestResult.heatmap.length === 0) {
      return (
        <div className="empty-state">
          <Info size={36} className="empty-state-icon" />
          <p>No returns heatmap data available for this backtest.</p>
        </div>
      );
    }
    
    // Sort and group
    const points = [...backtestResult.heatmap].sort((a, b) => b.year - a.year || a.month - b.month);
    const years: Record<number, Record<number, number>> = {};
    points.forEach(p => {
      if (!years[p.year]) years[p.year] = {};
      years[p.year][p.month] = p.return;
    });
    
    const sortedYears = Object.keys(years).map(Number).sort((a, b) => b - a);
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    
    return (
      <div className="heatmap-wrapper">
        <div className="heatmap-grid" style={{ marginBottom: '8px' }}>
          <div className="heatmap-header">Year</div>
          {months.map(m => (
            <div key={m} className="heatmap-header">{m}</div>
          ))}
        </div>
        
        {sortedYears.map(yr => (
          <div key={yr} className="heatmap-grid" style={{ marginBottom: '6px' }}>
            <div className="heatmap-year-label">{yr}</div>
            {Array.from({ length: 12 }, (_, i) => {
              const mIndex = i + 1;
              const retVal = years[yr][mIndex];
              return (
                <div 
                  key={mIndex} 
                  className="heatmap-cell"
                  style={{ 
                    backgroundColor: retVal !== undefined ? getHeatmapColor(retVal) : 'rgba(255, 255, 255, 0.02)',
                    opacity: retVal !== undefined ? 1 : 0.2
                  }}
                  title={retVal !== undefined ? `Return: ${retVal.toFixed(2)}%` : 'No Trades'}
                >
                  {retVal !== undefined ? getHeatmapText(retVal) : '-'}
                </div>
              );
            })}
          </div>
        ))}
      </div>
    );
  };

  const activeStrategyMeta = strategies.find(s => s.id === selectedStrategy);

  return (
    <div className="app-container">
      {/* HEADER */}
      <header className="app-header">
        <div className="brand-section">
          <div className="brand-logo">
            <TrendingUp size={28} strokeWidth={2.5} />
          </div>
          <div>
            <h1 className="brand-title">Antigravity Quant</h1>
            <span className="brand-badge">RESEARCH PLATFORM</span>
          </div>
        </div>
        <div className="system-status">
          <span className="status-indicator"></span>
          <span>Core Engine Online</span>
        </div>
      </header>

      {/* WORKSPACE GRID */}
      <main className="workspace-grid">
        
        {/* SIDEBAR CONFIGURATION PANEL */}
        <section className="config-sidebar">
          <div className="sidebar-title">
            <Settings size={18} />
            <span>Config & Parameters</span>
          </div>

          <div className="form-group">
            <label htmlFor="mode-select">Execution Mode</label>
            <select 
              id="mode-select"
              value={executionMode} 
              onChange={(e) => setExecutionMode(e.target.value)}
            >
              <option value="backtest">Standard Backtest</option>
              <option value="grid_search">Grid Search Optimization</option>
              <option value="walk_forward">Walk-Forward Testing</option>
              <option value="compare">Multi-Strategy Comparison</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="assets-input">Asset Tickers</label>
            <input 
              id="assets-input"
              type="text" 
              value={assets}
              onChange={(e) => setAssets(e.target.value)}
              placeholder="e.g. AAPL (or AAPL, MSFT for Pairs)"
            />
            <span style={{ fontSize: '10px', color: 'var(--color-text-muted)', marginTop: '2px' }}>
              Comma-separated tickers for multi-asset or pairs trading.
            </span>
          </div>

          <div className="form-group-row">
            <div className="form-group">
              <label htmlFor="start-date">Start Date</label>
              <input 
                id="start-date"
                type="date" 
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label htmlFor="end-date">End Date</label>
              <input 
                id="end-date"
                type="date" 
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
          </div>

          {executionMode !== "compare" && (
            <div className="form-group">
              <label htmlFor="strategy-select">Trading Strategy</label>
              <select 
                id="strategy-select"
                value={selectedStrategy} 
                onChange={handleStrategyChange}
              >
                {strategies.map(s => (
                  <option key={s.id} value={s.id}>{s.name}</option>
                ))}
              </select>
            </div>
          )}

          {/* DYNAMIC PARAMETERS IN BACKTEST MODE */}
          {executionMode === "backtest" && activeStrategyMeta && activeStrategyMeta.parameters.length > 0 && (
            <div className="dynamic-params-container">
              <div className="params-header">Strategy Parameters</div>
              {activeStrategyMeta.parameters.map(p => (
                <div key={p.name} className="form-group">
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                    <label style={{ fontSize: '11px' }}>{p.name.replace('_', ' ')}</label>
                    <span className="range-value">{strategyParams[p.name]}</span>
                  </div>
                  <div className="range-input-container">
                    <input 
                      type="range"
                      min={p.min}
                      max={p.max}
                      step={p.type === 'int' ? 1 : 0.1}
                      value={strategyParams[p.name] !== undefined ? strategyParams[p.name] : p.default}
                      onChange={(e) => handleParamSliderChange(p.name, parseFloat(e.target.value))}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* DYNAMIC PARAMETERS IN OPTIMIZATION MODES */}
          {(executionMode === "grid_search" || executionMode === "walk_forward") && activeStrategyMeta && (
            <div className="dynamic-params-container">
              <div className="params-header">Grid Range Config</div>
              <p style={{ fontSize: '10px', color: 'var(--color-text-muted)', marginBottom: '8px' }}>
                Provide comma-separated values to test.
              </p>
              {activeStrategyMeta.parameters.map(p => (
                <div key={p.name} className="form-group">
                  <label style={{ fontSize: '11px' }}>{p.name.replace('_', ' ')} Grid</label>
                  <input 
                    type="text"
                    value={gridParamsInput[p.name] || ''}
                    onChange={(e) => handleGridParamChange(p.name, e.target.value)}
                    placeholder={`e.g. ${p.default}, ${p.default * 2}`}
                  />
                </div>
              ))}
            </div>
          )}

          {/* RISK CONFIGURATION */}
          <div className="dynamic-params-container" style={{ borderLeft: '2px solid var(--color-primary)' }}>
            <div className="params-header">Risk Limits & Sizing</div>
            
            <div className="form-group">
              <div style={{ display: 'flex', justifyItems: 'center', justifyContent: 'space-between', fontSize: '12px' }}>
                <label style={{ fontSize: '11px' }}>Stop Loss %</label>
                <span className="range-value" style={{ color: 'var(--color-danger)' }}>{stopLossPct}%</span>
              </div>
              <div className="range-input-container">
                <input 
                  type="range"
                  min="0"
                  max="25"
                  step="0.5"
                  value={stopLossPct}
                  onChange={(e) => setStopLossPct(parseFloat(e.target.value))}
                />
              </div>
            </div>

            <div className="form-group">
              <div style={{ display: 'flex', justifyItems: 'center', justifyContent: 'space-between', fontSize: '12px' }}>
                <label style={{ fontSize: '11px' }}>Take Profit %</label>
                <span className="range-value" style={{ color: 'var(--color-success)' }}>{takeProfitPct}%</span>
              </div>
              <div className="range-input-container">
                <input 
                  type="range"
                  min="0"
                  max="50"
                  step="0.5"
                  value={takeProfitPct}
                  onChange={(e) => setTakeProfitPct(parseFloat(e.target.value))}
                />
              </div>
            </div>

            <div className="form-group">
              <div style={{ display: 'flex', justifyItems: 'center', justifyContent: 'space-between', fontSize: '12px' }}>
                <label style={{ fontSize: '11px' }}>Max Position Size %</label>
                <span className="range-value" style={{ color: 'var(--color-primary)' }}>{positionSizePct}%</span>
              </div>
              <div className="range-input-container">
                <input 
                  type="range"
                  min="10"
                  max="100"
                  step="5"
                  value={positionSizePct}
                  onChange={(e) => setPositionSizePct(parseInt(e.target.value))}
                />
              </div>
            </div>
          </div>

          <button 
            className="btn-run" 
            onClick={handleRun} 
            disabled={loading}
          >
            {loading ? (
              <>
                <RefreshCw size={16} className="spinner" style={{ animation: 'spin 1s linear infinite' }} />
                <span>Running Models...</span>
              </>
            ) : (
              <>
                <Play size={16} fill="white" />
                <span>Run Quant Engine</span>
              </>
            )}
          </button>
        </section>

        {/* MAIN PANEL */}
        <section className="dashboard-panel">
          
          {/* ERROR DISPLAY */}
          {error && (
            <div className="error-banner">
              <ShieldAlert size={20} />
              <span>{error}</span>
            </div>
          )}

          {/* OVERVIEW STATS (KPI CARDS) */}
          {backtestResult && (
            <div className="kpi-grid">
              <div className="kpi-card">
                <span className="kpi-label">Final Portfolio Value</span>
                <span className="kpi-value">${backtestResult.summary.final_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
              </div>
              <div className="kpi-card">
                <span className="kpi-label">CAGR %</span>
                <span className={`kpi-value ${backtestResult.summary.cagr >= 0 ? 'positive' : 'negative'}`}>
                  {backtestResult.summary.cagr >= 0 ? '+' : ''}{backtestResult.summary.cagr.toFixed(2)}%
                </span>
              </div>
              <div className="kpi-card">
                <span className="kpi-label">Sharpe Ratio</span>
                <span className="kpi-value">{backtestResult.summary.sharpe.toFixed(2)}</span>
              </div>
              <div className="kpi-card">
                <span className="kpi-label">Max Drawdown</span>
                <span className="kpi-value negative" style={{ color: 'var(--color-danger)' }}>
                  -{Math.abs(backtestResult.summary.max_drawdown).toFixed(2)}%
                </span>
              </div>
              <div className="kpi-card">
                <span className="kpi-label">Win Rate</span>
                <span className="kpi-value" style={{ color: 'var(--color-primary)' }}>
                  {backtestResult.summary.win_rate.toFixed(1)}%
                </span>
              </div>
              <div className="kpi-card">
                <span className="kpi-label">Profit Factor</span>
                <span className="kpi-value">
                  {backtestResult.summary.profit_factor}
                </span>
              </div>
            </div>
          )}

          {/* TAB NAVIGATION BAR */}
          <div className="tabs-bar">
            {executionMode === "backtest" && (
              <>
                <button 
                  className={`tab-btn ${activeTab === 'backtest' ? 'active' : ''}`}
                  onClick={() => setActiveTab('backtest')}
                >
                  <BarChart2 size={16} />
                  <span>Performance Charts</span>
                </button>
                <button 
                  className={`tab-btn ${activeTab === 'tradelog' ? 'active' : ''}`}
                  onClick={() => setActiveTab('tradelog')}
                >
                  <List size={16} />
                  <span>Execution Trade Log ({backtestResult?.trade_log.length || 0})</span>
                </button>
                <button 
                  className={`tab-btn ${activeTab === 'heatmap' ? 'active' : ''}`}
                  onClick={() => setActiveTab('heatmap')}
                >
                  <Grid size={16} />
                  <span>Monthly Returns Heatmap</span>
                </button>
              </>
            )}

            {(executionMode === "grid_search" || executionMode === "walk_forward") && (
              <button 
                className={`tab-btn ${activeTab === 'grid_wf' ? 'active' : ''}`}
                onClick={() => setActiveTab('grid_wf')}
              >
                <Sliders size={16} />
                <span>Optimization Output</span>
              </button>
            )}

            {executionMode === "compare" && (
              <button 
                className={`tab-btn ${activeTab === 'compare' ? 'active' : ''}`}
                onClick={() => setActiveTab('compare')}
              >
                <Layers size={16} />
                <span>Multi-Strategy Performance Matrix</span>
              </button>
            )}
          </div>

          {/* MAIN DISPLAY CANVAS */}
          <div className="panel-canvas">
            
            {/* SPINNER LOADING SCREEN */}
            {loading && (
              <div className="spinner-container">
                <div className="spinner"></div>
                <p style={{ color: 'var(--color-text-secondary)', fontWeight: 500 }}>
                  Computing historical market vectors & simulating fills...
                </p>
              </div>
            )}

            {/* EMPTY STATE */}
            {!loading && !backtestResult && !gridResult && !walkForwardResult && !comparisonResult && (
              <div className="empty-state">
                <Activity size={48} className="empty-state-icon" />
                <h3>No Active Simulation</h3>
                <p>Configure strategy variables on the left panel, then trigger "Run Quant Engine" to simulate strategy performance.</p>
              </div>
            )}

            {/* BACKTEST PERFORMANCE CHARTS PANEL */}
            {!loading && activeTab === 'backtest' && backtestResult && (
              <div className="charts-grid">
                
                {/* Cointegration Alert for Pairs Trading */}
                {selectedStrategy === "pairs_trading" && backtestResult.cointegration && (
                  <div className={`coint-indicator ${backtestResult.cointegration.is_cointegrated ? 'success' : 'warning'}`}>
                    <Info size={16} />
                    <span>
                      <strong>Cointegration Test:</strong> t-stat = {backtestResult.cointegration.t_stat.toFixed(3)} | p-value = {backtestResult.cointegration.p_value.toFixed(4)}. 
                      {backtestResult.cointegration.is_cointegrated 
                        ? " The pair is statistically cointegrated (p < 0.05). Correlation is solid for mean reversion." 
                        : " Warning: No strong cointegration detected. Spread may drift."}
                    </span>
                  </div>
                )}

                {/* Equity Curve Chart */}
                <div className="chart-wrapper">
                  <div className="chart-title">
                    <span>Equity Growth Curve</span>
                    <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>Portfolio vs Buy & Hold Benchmark</span>
                  </div>
                  <div style={{ width: '100%', height: 350 }}>
                    <ResponsiveContainer>
                      <AreaChart data={backtestResult.equity_curve}>
                        <defs>
                          <linearGradient id="colorPortfolio" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="var(--color-primary)" stopOpacity={0.25}/>
                            <stop offset="95%" stopColor="var(--color-primary)" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" />
                        <XAxis dataKey="date" stroke="var(--color-text-muted)" fontSize={11} tickLine={false} />
                        <YAxis 
                          stroke="var(--color-text-muted)" 
                          fontSize={11} 
                          domain={['dataMin - 500', 'dataMax + 500']}
                          tickFormatter={(v) => `$${v.toLocaleString()}`}
                          tickLine={false}
                        />
                        <Tooltip 
                          contentStyle={{ 
                            backgroundColor: 'rgba(10, 10, 15, 0.95)', 
                            border: '1px solid var(--border-color)',
                            borderRadius: '8px',
                            color: '#fff'
                          }} 
                          formatter={(v: any) => [`$${parseFloat(v).toFixed(2)}`]}
                        />
                        <Legend wrapperStyle={{ fontSize: 12, paddingTop: 10 }} />
                        <Area name="Portfolio Value" type="monotone" dataKey="portfolio" stroke="var(--color-primary)" strokeWidth={2} fillOpacity={1} fill="url(#colorPortfolio)" />
                        <Line name="Benchmark Buy & Hold" type="monotone" dataKey="benchmark" stroke="var(--color-text-secondary)" strokeWidth={1.5} strokeDasharray="4 4" dot={false} />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Price Indicators Overlay Chart (Buy/Sell signals dot overlay) */}
                <div className="chart-wrapper">
                  <div className="chart-title">
                    <span>Microstructure signals & indicators</span>
                    <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>Price series & overlay curves</span>
                  </div>
                  <div style={{ width: '100%', height: 320 }}>
                    <ResponsiveContainer>
                      <ComposedChart data={backtestResult.price_chart_data}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" />
                        <XAxis dataKey="date" stroke="var(--color-text-muted)" fontSize={11} tickLine={false} />
                        
                        {selectedStrategy === "pairs_trading" ? (
                          <>
                            {/* For Pairs Trading, we display the spread and z-score */}
                            <YAxis stroke="var(--color-text-muted)" fontSize={11} tickLine={false} id="left-axis" label={{ value: 'Spread', angle: -90, position: 'insideLeft', style: { fill: 'var(--color-text-secondary)', fontSize: 10 } }} />
                            <YAxis stroke="var(--color-text-muted)" fontSize={11} tickLine={false} id="right-axis" orientation="right" label={{ value: 'Z-Score', angle: 90, position: 'insideRight', style: { fill: 'var(--color-primary)', fontSize: 10 } }} />
                            <Tooltip contentStyle={{ backgroundColor: 'rgba(10, 10, 15, 0.95)', border: '1px solid var(--border-color)', borderRadius: '8px' }} />
                            <Legend wrapperStyle={{ fontSize: 12 }} />
                            
                            <Line yAxisId="left-axis" name="Spread Asset1/Asset2" type="monotone" dataKey="spread" stroke="#a78bfa" strokeWidth={1.5} dot={false} />
                            <Line yAxisId="right-axis" name="Spread Z-Score" type="monotone" dataKey="z_score" stroke="var(--color-primary)" strokeWidth={1.5} dot={false} />
                            
                            <ReferenceLine yAxisId="right-axis" y={backtestResult.price_chart_data[0]?.upper_threshold || 2.0} stroke="var(--color-danger)" strokeDasharray="3 3" label={{ value: '+Z Threshold', fill: 'var(--color-danger)', fontSize: 9 }} />
                            <ReferenceLine yAxisId="right-axis" y={backtestResult.price_chart_data[0]?.lower_threshold || -2.0} stroke="var(--color-success)" strokeDasharray="3 3" label={{ value: '-Z Threshold', fill: 'var(--color-success)', fontSize: 9 }} />
                            
                            <Line yAxisId="left-axis" name="BUY Spread Signal" type="monotone" dataKey="buy_price" stroke="none" r={6} fill="var(--color-success)" dot={{ stroke: 'var(--color-success)', strokeWidth: 2, r: 5 }} />
                            <Line yAxisId="left-axis" name="SELL Spread Signal" type="monotone" dataKey="sell_price" stroke="none" r={6} fill="var(--color-danger)" dot={{ stroke: 'var(--color-danger)', strokeWidth: 2, r: 5 }} />
                          </>
                        ) : (
                          <>
                            {/* Standard single asset price chart */}
                            <YAxis stroke="var(--color-text-muted)" fontSize={11} tickLine={false} domain={['dataMin - 10', 'dataMax + 10']} />
                            <Tooltip contentStyle={{ backgroundColor: 'rgba(10, 10, 15, 0.95)', border: '1px solid var(--border-color)', borderRadius: '8px' }} />
                            <Legend wrapperStyle={{ fontSize: 12 }} />
                            
                            <Line name="Asset Price" type="monotone" dataKey="price" stroke="#f4f4f5" strokeWidth={1.5} dot={false} />
                            
                            {/* Dynamic Indicator Overlay lines */}
                            {selectedStrategy === "moving_average" && (
                              <>
                                <Line name="Fast SMA" type="monotone" dataKey="fast_ma" stroke="#60a5fa" strokeWidth={1.2} dot={false} />
                                <Line name="Slow SMA" type="monotone" dataKey="slow_ma" stroke="#fb923c" strokeWidth={1.2} dot={false} />
                              </>
                            )}
                            {selectedStrategy === "momentum" && (
                              <Line name="RSI" type="monotone" dataKey="rsi" stroke="#fb7185" strokeWidth={1.2} dot={false} />
                            )}
                            {(selectedStrategy === "mean_reversion" || selectedStrategy === "bollinger_bands") && (
                              <>
                                <Line name="Rolling Mean" type="monotone" dataKey="fast_ma" stroke="#60a5fa" strokeWidth={1.2} dot={false} />
                                <Line name="Upper Band" type="monotone" dataKey="upper_band" stroke="rgba(239, 68, 68, 0.4)" strokeWidth={1} strokeDasharray="3 3" dot={false} />
                                <Line name="Lower Band" type="monotone" dataKey="lower_band" stroke="rgba(16, 185, 129, 0.4)" strokeWidth={1} strokeDasharray="3 3" dot={false} />
                              </>
                            )}
                            
                            {/* Signal Markers overlayed on Price */}
                            <Line name="BUY Signal" type="monotone" dataKey="buy_price" stroke="none" r={6} fill="var(--color-success)" dot={{ stroke: '#10b981', strokeWidth: 3, r: 6 }} />
                            <Line name="SELL Signal" type="monotone" dataKey="sell_price" stroke="none" r={6} fill="var(--color-danger)" dot={{ stroke: '#ef4444', strokeWidth: 3, r: 6 }} />
                          </>
                        )}
                      </ComposedChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Drawdown Curve (Underwater Chart) */}
                <div className="chart-wrapper">
                  <div className="chart-title">
                    <span>Drawdown Underwater Curve</span>
                    <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>Percentage Drawdown from Historical Peak</span>
                  </div>
                  <div style={{ width: '100%', height: 180 }}>
                    <ResponsiveContainer>
                      <AreaChart data={backtestResult.equity_curve}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" />
                        <XAxis dataKey="date" stroke="var(--color-text-muted)" fontSize={11} tickLine={false} />
                        <YAxis 
                          stroke="var(--color-text-muted)" 
                          fontSize={11} 
                          tickFormatter={(v) => `${v.toFixed(1)}%`}
                          tickLine={false}
                        />
                        <Tooltip contentStyle={{ backgroundColor: 'rgba(10, 10, 15, 0.95)', border: '1px solid var(--border-color)', borderRadius: '8px' }} formatter={(v: any) => [`${parseFloat(v).toFixed(2)}%`]} />
                        <Area name="Drawdown" type="monotone" dataKey="drawdown" stroke="var(--color-danger)" fill="rgba(239, 68, 68, 0.15)" strokeWidth={1} />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>

              </div>
            )}

            {/* TRADE LOG TAB */}
            {!loading && activeTab === 'tradelog' && backtestResult && (
              <div>
                <div className="canvas-title" style={{ marginBottom: '16px' }}>
                  <span>Simulated Order Fills</span>
                  <span style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>
                    Total Fills: {backtestResult.trade_log.length}
                  </span>
                </div>
                {backtestResult.trade_log.length === 0 ? (
                  <div className="empty-state">
                    <Info size={36} className="empty-state-icon" />
                    <p>No trades were executed by the strategy during this date range.</p>
                  </div>
                ) : (
                  <div className="table-container">
                    <table>
                      <thead>
                        <tr>
                          <th>Date</th>
                          <th>Ticker</th>
                          <th>Action</th>
                          <th>Quantity</th>
                          <th>Price</th>
                          <th>Commission</th>
                          <th>Total Value</th>
                          <th>Realized PnL</th>
                        </tr>
                      </thead>
                      <tbody>
                        {backtestResult.trade_log.map((t, idx) => (
                          <tr key={idx}>
                            <td>{t.date}</td>
                            <td>{t.ticker}</td>
                            <td>
                              <span className={`badge-action ${t.action.toLowerCase()}`}>
                                {t.action}
                              </span>
                            </td>
                            <td>{t.quantity.toLocaleString(undefined, { maximumFractionDigits: 4 })}</td>
                            <td>${t.price.toFixed(2)}</td>
                            <td>${t.commission.toFixed(2)}</td>
                            <td>${t.value.toFixed(2)}</td>
                            <td className={t.realized_pnl > 0 ? 'positive' : t.realized_pnl < 0 ? 'negative' : ''} style={{ color: t.realized_pnl > 0 ? 'var(--color-success)' : t.realized_pnl < 0 ? 'var(--color-danger)' : '' }}>
                              {t.realized_pnl !== 0 ? `${t.realized_pnl > 0 ? '+' : ''}$${t.realized_pnl.toFixed(2)}` : '$0.00'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}

            {/* MONTHLY HEATMAP TAB */}
            {!loading && activeTab === 'heatmap' && backtestResult && (
              <div>
                <div className="canvas-title" style={{ marginBottom: '24px' }}>
                  <span>Monthly Return Heatmap (%)</span>
                  <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>Colors scale proportionally based on return magnitude</span>
                </div>
                {renderHeatmap()}
              </div>
            )}

            {/* OPTIMIZATION RESULTS (GRID SEARCH / WALK FORWARD) */}
            {!loading && activeTab === 'grid_wf' && (
              <div>
                {gridResult && (
                  <div>
                    <div className="canvas-title" style={{ marginBottom: '20px' }}>
                      <span>Grid Search Optimization Output</span>
                    </div>
                    
                    <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap', marginBottom: '24px' }}>
                      <div className="kpi-card" style={{ flex: 1, minWidth: '200px' }}>
                        <span className="kpi-label">Optimized Best CAGR</span>
                        <span className="kpi-value positive">+{gridResult.best_cagr.toFixed(2)}%</span>
                      </div>
                      <div className="kpi-card" style={{ flex: 1, minWidth: '200px' }}>
                        <span className="kpi-label">Optimized Final Value</span>
                        <span className="kpi-value">${gridResult.final_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                      </div>
                    </div>

                    <div className="canvas-title" style={{ fontSize: '14px', marginBottom: '12px' }}>
                      <span>Optimal Parameter Mapping</span>
                    </div>
                    <div className="table-container">
                      <table>
                        <thead>
                          <tr>
                            <th>Parameter Variable</th>
                            <th>Optimal Configuration Value</th>
                          </tr>
                        </thead>
                        <tbody>
                          {Object.entries(gridResult.best_params).map(([k, v]) => (
                            <tr key={k}>
                              <td style={{ color: 'var(--color-primary)', textTransform: 'capitalize' }}>{k.replace('_', ' ')}</td>
                              <td>{typeof v === 'number' ? v.toFixed(4).replace(/\.?0+$/, '') : String(v)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {walkForwardResult && (
                  <div>
                    <div className="canvas-title" style={{ marginBottom: '16px' }}>
                      <span>Walk-Forward Segment Testing</span>
                    </div>
                    <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', marginBottom: '20px' }}>
                      Simulates rolling window walk-forward tests, optimizing parameters out-of-sample across subperiods.
                    </p>

                    <div className="table-container">
                      <table>
                        <thead>
                          <tr>
                            <th>Forward Testing Period</th>
                            <th>Segment Best Parameters</th>
                            <th>Out-of-Sample CAGR</th>
                            <th>Ending Segment Value</th>
                          </tr>
                        </thead>
                        <tbody>
                          {walkForwardResult.map((w, idx) => (
                            <tr key={idx}>
                              <td style={{ color: '#fff' }}>{w.period}</td>
                              <td style={{ fontSize: '12px' }}>
                                {Object.entries(w.best_params)
                                  .map(([k, v]) => `${k}:${v}`)
                                  .join(', ')}
                              </td>
                              <td className={w.cagr >= 0 ? 'positive' : 'negative'} style={{ color: w.cagr >= 0 ? 'var(--color-success)' : 'var(--color-danger)' }}>
                                {w.cagr >= 0 ? '+' : ''}{w.cagr.toFixed(2)}%
                              </td>
                              <td>${w.final_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* MULTI-STRATEGY COMPARISON TAB */}
            {!loading && activeTab === 'compare' && comparisonResult && (
              <div>
                <div className="canvas-title" style={{ marginBottom: '20px' }}>
                  <span>Multi-Strategy Comparison Matrix</span>
                </div>
                <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', marginBottom: '20px' }}>
                  Simultaneously simulates all base strategies against your configured tickers and date range.
                </p>

                <div className="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>Strategy Scheme</th>
                        <th>CAGR %</th>
                        <th>Sharpe Ratio</th>
                        <th>Max Drawdown %</th>
                        <th>Final Portfolio Value</th>
                      </tr>
                    </thead>
                    <tbody>
                      {comparisonResult.map((r) => (
                        <tr key={r.strategy_id}>
                          <td style={{ color: '#fff', fontWeight: 600 }}>{r.strategy_name}</td>
                          <td className={r.cagr >= 0 ? 'positive' : 'negative'} style={{ color: r.cagr >= 0 ? 'var(--color-success)' : 'var(--color-danger)' }}>
                            {r.cagr >= 0 ? '+' : ''}{r.cagr.toFixed(2)}%
                          </td>
                          <td>{r.sharpe.toFixed(2)}</td>
                          <td style={{ color: 'var(--color-danger)' }}>-{Math.abs(r.max_drawdown).toFixed(2)}%</td>
                          <td>${r.final_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

          </div>

        </section>

      </main>
    </div>
  );
}

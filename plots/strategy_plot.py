import pandas as pd
import matplotlib.pyplot as plt

def plot_strategy_results(df: pd.DataFrame, signals: pd.Series, portfolio_values: pd.Series, title: str = "Strategy Results"):
    """
    Plots the price chart with buy/sell markers and the equity curve below it.
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
    
    # 1. Price Chart with Markers
    ax1.plot(df.index, df['Close'], label='Price', color='black', alpha=0.6)
    
    # Buy markers (signal == 1)
    buys = df[signals == 1]
    ax1.scatter(buys.index, buys['Close'], marker='^', color='green', s=100, label='Buy', zorder=5)
    
    # Sell markers (signal == -1)
    sells = df[signals == -1]
    ax1.scatter(sells.index, sells['Close'], marker='v', color='red', s=100, label='Sell', zorder=5)
    
    ax1.set_title(title)
    ax1.set_ylabel("Price")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Equity Curve
    ax2.plot(portfolio_values.index, portfolio_values, label='Portfolio Value', color='blue')
    ax2.set_ylabel("Value ($)")
    ax2.set_xlabel("Date")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

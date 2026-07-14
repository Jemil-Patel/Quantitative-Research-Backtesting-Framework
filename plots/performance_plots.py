import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_drawdown(portfolio_values: pd.Series, title: str = "Drawdown Plot"):
    peak = portfolio_values.expanding(min_periods=1).max()
    drawdown = (portfolio_values / peak) - 1
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.fill_between(drawdown.index, drawdown, 0, color='red', alpha=0.3)
    ax.plot(drawdown.index, drawdown, color='red', linewidth=1)
    
    ax.set_title(title)
    ax.set_ylabel("Drawdown")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_monthly_heatmap(daily_returns: pd.Series, title: str = "Monthly Return Heatmap"):
    """
    Plots a monthly return heatmap using matplotlib.
    """
    if daily_returns.empty:
        return
        
    # Resample to monthly returns
    monthly_returns = (1 + daily_returns).resample('ME').prod() - 1
    
    df = pd.DataFrame({'Return': monthly_returns})
    df['Year'] = df.index.year
    df['Month'] = df.index.month
    
    pivot = df.pivot(index='Year', columns='Month', values='Return')
    
    fig, ax = plt.subplots(figsize=(10, 6))
    # Replace NaNs with 0 for coloring, but leave text empty
    plot_data = pivot.fillna(0)
    
    cax = ax.imshow(plot_data, cmap="RdYlGn", aspect="auto", vmin=-0.2, vmax=0.2)
    fig.colorbar(cax, ax=ax, format="%.2f")
    
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    
    # Annotate
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = pivot.iloc[i, j]
            if not pd.isna(val):
                ax.text(j, i, f"{val:.2%}", ha="center", va="center", color="black")
                
    ax.set_title(title)
    plt.tight_layout()
    plt.show()

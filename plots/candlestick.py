import pandas as pd
import matplotlib.pyplot as plt

def plot_candlestick(df: pd.DataFrame, title: str = "Candlestick Chart", window: int = 100):
    """
    Plots a candlestick chart using matplotlib.
    To avoid clutter, plots only the last 'window' days if specified.
    """
    if len(df) > window:
        df = df.iloc[-window:]
        
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Define colors
    up_color = 'green'
    down_color = 'red'
    
    # Calculate daily price change
    df['up'] = df['Close'] >= df['Open']
    df['down'] = df['Close'] < df['Open']
    
    # Plot 'up' days
    up_df = df[df['up']]
    ax.vlines(up_df.index, up_df['Low'], up_df['High'], color=up_color, linewidth=1)
    ax.bar(up_df.index, up_df['Close'] - up_df['Open'], bottom=up_df['Open'], color=up_color, width=0.5)
    
    # Plot 'down' days
    down_df = df[df['down']]
    ax.vlines(down_df.index, down_df['Low'], down_df['High'], color=down_color, linewidth=1)
    ax.bar(down_df.index, down_df['Open'] - down_df['Close'], bottom=down_df['Close'], color=down_color, width=0.5)
    
    ax.set_title(title)
    ax.set_ylabel("Price")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

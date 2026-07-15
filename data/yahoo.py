import yfinance as yf
import pandas as pd
from typing import Union, List, Dict
from data.preprocessing import clean_data

def fetch_data(tickers: Union[str, List[str]], start_date: str, end_date: str) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """
    Fetches historical market data for given tickers from Yahoo Finance.
    
    Args:
        tickers: A single ticker string or a list of ticker strings.
        start_date: Start date in 'YYYY-MM-DD' format.
        end_date: End date in 'YYYY-MM-DD' format.
        
    Returns:
        If a single ticker is provided, returns a pandas DataFrame.
        If a list of tickers is provided, returns a dictionary of DataFrames, 
        keyed by ticker.
    """
    if isinstance(tickers, str):
        tickers = [tickers]
        
    data_dict = {}
    
    # Fetching individually to avoid MultiIndex complexity and ensure consistent format
    for ticker in tickers:
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        
        # Flatten MultiIndex columns if present (yfinance returns this now even for single tickers)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
            
        df = clean_data(df)
        data_dict[ticker] = df
        
    if len(tickers) == 1:
        return data_dict[tickers[0]]
        
    return data_dict

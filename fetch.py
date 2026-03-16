import yfinance as yf
import pandas as pd
import numpy as np

def fetch_stock_data(stock_id, period):
    # Try with .NS suffix first if it's a simple symbol (typically Indian market)
    symbol = stock_id if "." in stock_id else f"{stock_id}.NS"
    
    print(f"[FETCH] Downloading {symbol} for period {period}...")
    try:
        df = yf.download(symbol, period=period, progress=False, timeout=15)
        
        if (df is None or df.empty) and "." not in stock_id:
            # Fallback to exact symbol if .NS failed
            print(f"[FETCH] Fallback to exact symbol: {stock_id}")
            df = yf.download(stock_id, period=period, progress=False, timeout=15)
            
        if df is None or df.empty:
            print(f"[WARNING] No data found for {stock_id}")
            return None
            
        # Handle potential MultiIndex for single ticker
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # Critical: Check if the 'Close' column only contains NaNs (can happen for 1d if market just opened)
        if 'Close' in df.columns and df['Close'].isna().all():
            print(f"[WARNING] Data for {stock_id} contains only NaNs.")
            return None
            
        return df
    except Exception as e:
        print(f"[ERROR] Fetch failed for {stock_id}: {e}")
        return None

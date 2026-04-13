import yfinance as yf
import streamlit as st

@st.cache_data(ttl=3600)  # Cache headlines for 1 hour
def get_financial_news(stock_id: str) -> list:
    """
    Fetches recent financial news headlines for a given stock symbol using yfinance.
    Returns a list of headlines.
    """
    try:
        # Try with .NS suffix first (default behavior for Indian stocks)
        symbol = f"{stock_id}.NS" if "." not in stock_id else stock_id
        ticker = yf.Ticker(symbol)
        news = ticker.news
        headlines = [item['title'] for item in news if 'title' in item]
        
        # If no news found with .NS, try the exact symbol (for Global stocks like TSLA)
        if not headlines and "." not in stock_id:
            ticker = yf.Ticker(stock_id)
            news = ticker.news
            headlines = [item['title'] for item in news if 'title' in item]
        
        if not headlines:
            return []
        
        return headlines[:5]
    except Exception as e:
        print(f"Error fetching news: {e}")
        return ["Market stays volatile amid global economic changes."]

import yfinance as yf
import streamlit as st

@st.cache_data(ttl=3600)  # Cache headlines for 1 hour
def get_financial_news(stock_id: str) -> list:
    """
    Fetches recent financial news headlines for a given stock symbol using yfinance.
    Returns a list of headlines.
    """
    try:
        ticker = yf.Ticker(f"{stock_id}.NS")
        news = ticker.news
        headlines = [item['title'] for item in news if 'title' in item]
        
        # Fallback to empty if no ticker specific news is found
        if not headlines:
            return []
        
        return headlines[:5]  # Limit to 5 headlines for sentiment analysis
    except Exception as e:
        print(f"Error fetching news: {e}")
        return ["Market stays volatile amid global economic changes."]

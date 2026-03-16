import re

def normalize_period(user_input: str) -> str:
    """
    Normalizes a user-provided period string to a format yfinance expects (e.g., '1y', '5y', '1mo').
    Defaults to 'y' (years) if no unit is provided.
    """
    if not user_input:
        return "1y"

    # Clean input: lowercase and remove extra spaces
    clean_input = user_input.lower().strip()

    # Match number and optional unit
    match = re.match(r"^(\d+)\s*(.*)$", clean_input)
    if not match:
        return clean_input  # Return as is if format isn't recognized

    value = match.group(1)
    unit_str = match.group(2)

    # Map various unit descriptions to yfinance units
    if not unit_str or "year" in unit_str or "y" == unit_str:
        unit = "y"
    elif "month" in unit_str or "mo" in unit_str:
        unit = "mo"
    elif "day" in unit_str or "d" == unit_str:
        unit = "d"
    elif "week" in unit_str or "w" == unit_str:
        unit = "wk"
    else:
        unit = "y"  # Default to years if unit is unknown but number exists

    return f"{value}{unit}"

def get_consensus_verdict(rsi, macd, sentiment_label):
    """
    Synthesizes multiple signals into a single actionable consensus score.
    Returns a dict with verdict, score, and breakdown.
    """
    score = 0
    
    # RSI Scoring
    if rsi < 35: score += 1      # Oversold (Bullish)
    elif rsi > 65: score -= 1    # Overbought (Bearish)
    
    # MACD Scoring
    if macd > 0: score += 1
    elif macd < 0: score -= 1
    
    # Sentiment Scoring
    sl = sentiment_label.lower()
    if sl in ["bullish", "positive"]: score += 1
    elif sl in ["bearish", "negative"]: score -= 1
    
    # Final Mapping
    if score >= 2: verdict = "Strong Buy"
    elif score == 1: verdict = "Moderate Buy"
    elif score == 0: verdict = "Neutral"
    elif score == -1: verdict = "Moderate Sell"
    else: verdict = "Strong Sell"
    
    return {
        "verdict": verdict,
        "score": score,
        "tech_signal": "Bullish" if (rsi < 35 or macd > 0) else "Bearish" if (rsi > 65 or macd < 0) else "Neutral"
    }

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

def generate_technical_reasoning(df):
    """Generates detailed natural language reasoning for technical signals."""
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    reasons = []

    # 1. Moving Average Crosses
    if 'SMA_50' in df.columns and 'SMA_200' in df.columns:
        if latest['SMA_50'] > latest['SMA_200'] and prev['SMA_50'] <= prev['SMA_200']:
            reasons.append({"label": "Golden Cross", "desc": "SMA 50 crossed above SMA 200 (Extreme Bullish)", "type": "bullish"})
        elif latest['SMA_50'] < latest['SMA_200'] and prev['SMA_50'] >= prev['SMA_200']:
            reasons.append({"label": "Death Cross", "desc": "SMA 50 dropped below SMA 200 (Extreme Bearish)", "type": "bearish"})
        elif latest['SMA_50'] > latest['SMA_200']:
            reasons.append({"label": "Bulllish Trend", "desc": "50-day average is above 200-day average", "type": "bullish"})
        else:
            reasons.append({"label": "Bearish Trend", "desc": "50-day average is below 200-day average", "type": "bearish"})

    # 2. RSI Signals
    rsi = latest.get('RSI', 50)
    if rsi > 70:
        reasons.append({"label": "Overbought", "desc": f"RSI is {rsi:.2f}. Potential price reversal downward.", "type": "bearish"})
    elif rsi < 30:
        reasons.append({"label": "Oversold", "desc": f"RSI is {rsi:.2f}. Potential price bounce upward.", "type": "bullish"})
    
    # 3. MACD
    macd = latest.get('MACD', 0)
    signal = latest.get('Signal_Line', 0)
    if macd > signal:
        reasons.append({"label": "Positive Momentum", "desc": "MACD is above the Signal line.", "type": "bullish"})
    else:
        reasons.append({"label": "Negative Momentum", "desc": "MACD is below the Signal line.", "type": "bearish"})

    return reasons

def quantify_sentiment_impact(sentiment_score_label, confidence, current_price, volatility_20d):
    """
    Calculates the theoretical price impact using a volatility-adjusted formula.
    Formula: ΔP = Price * (Score * Volatility * Confidence * K)
    """
    # Map score label to -1, 0, 1
    s_label = sentiment_score_label.upper()
    if "BULLISH" in s_label or "POSITIVE" in s_label:
        score_multiplier = 1.0
    elif "BEARISH" in s_label or "NEGATIVE" in s_label:
        score_multiplier = -1.0
    else:
        score_multiplier = 0
    
    # Calculate expected change (using 1.64 for 90% confidence interval multiplier)
    expected_change_pct = score_multiplier * volatility_20d * confidence * 1.64
    
    price_delta = current_price * expected_change_pct
    predicted_price = current_price + price_delta
    
    return {
        "expected_change_pct": expected_change_pct,
        "price_delta": price_delta,
        "predicted_price": predicted_price
    }

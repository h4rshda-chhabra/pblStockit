# ml_model.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from indicators import calculate_indicators
from fetch import fetch_stock_data
from sklearn.metrics import accuracy_score, precision_score, recall_score
import joblib
import os

# Fixed feature set
FEATURES = ['SMA_50', 'SMA_200', 'EMA_50', 'EMA_200', 'RSI', 'MACD', 'Signal_Line']
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models_v7")

def normalize_features_for_model(features_df, close_series):
    norm_df = features_df.copy()
    for col in ['SMA_50', 'SMA_200', 'EMA_50', 'EMA_200']:
        norm_df[col] = (norm_df[col] - close_series) / close_series
    norm_df['MACD'] = norm_df['MACD'] / close_series
    norm_df['Signal_Line'] = norm_df['Signal_Line'] / close_series
    return norm_df

def create_labeled_dataset(stock_id):
    # Use central fetch logic with 5y data for training
    df = fetch_stock_data(stock_id, period="5y")
    if df is None or df.empty:
        raise ValueError(f"No data found for {stock_id} to train model.")

    df = calculate_indicators(df)

    # Target creation: Predict if price will be > 2% higher in 10 days
    # This ensures a tight standard for BUY classification, rejecting flat markets.
    df['Future_Close'] = df['Close'].shift(-10)
    df.dropna(subset=['Close', 'Future_Close'], inplace=True)
    df['Target'] = np.where(df['Future_Close'] > df['Close'] * 1.02, 1, 0)

    # Use only selected features
    available_features = [f for f in FEATURES if f in df.columns]
    if len(available_features) < len(FEATURES):
        raise ValueError(f"Missing indicators in dataset. Needed: {FEATURES}")

    features = df[FEATURES].copy()
    features = normalize_features_for_model(features, df['Close'])
    features = features.dropna()
    
    target = df.loc[features.index, 'Target']
    return features, target

def train_model(stock_id):
    print(f"[ML] Training model for {stock_id}...")
    X, y = create_labeled_dataset(stock_id)
    
    if len(X) < 10:
        raise ValueError(f"Not enough historical data for '{stock_id}'. Needed 200+ trading days to calculate moving averages. Found {len(X)} valid points.")
        
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)

    # Calculate Metrics
    y_pred = model.predict(X_test)
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0))
    }

    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    model_path = os.path.join(MODEL_DIR, f"{stock_id}_model.pkl")
    # Save model and metrics together
    joblib.dump({"model": model, "metrics": metrics}, model_path)
    print(f"[ML] Model and metrics saved to {model_path}")
    return model, metrics

import streamlit as st

@st.cache_resource(show_spinner=False)
def load_or_train_model(stock_id):
    """Loads a pre-trained model from disk or trains a new one, keeping it in memory for speed."""
    model_path = os.path.join(MODEL_DIR, f"{stock_id}_model.pkl")
    if not os.path.exists(model_path):
        return train_model(stock_id)
    
    data = joblib.load(model_path)
    if isinstance(data, dict):
        return data['model'], data['metrics']
    return data, {"accuracy": 0.0, "precision": 0.0, "recall": 0.0}

def ml_predict(model, stock_data):
    # Ensure indicators are calculated
    processed_data = stock_data[FEATURES].copy()
    processed_data = normalize_features_for_model(processed_data, stock_data['Close'])
    processed_data = processed_data.dropna()
    
    if processed_data.empty:
        raise ValueError("Insufficient data to calculate technical indicators. Please select a longer timeframe (e.g., 1y).")

    latest = processed_data.iloc[-1]
    latest_df = pd.DataFrame([latest.values], columns=FEATURES)

    prediction = model.predict(latest_df)[0]
    probs = model.predict_proba(latest_df)[0]
    
    # Genuine Prediction Threshold (Requiring 55% majority probability)
    if probs[1] >= 0.55:
        pred_idx = 1
        label = "BUY"
        confidence = probs[1]
    else:
        pred_idx = 0
        label = "SHOULD NOT BUY"
        confidence = probs[0]
    
    # Get Global Feature Importance
    importances = model.feature_importances_
    feature_importance_map = dict(zip(FEATURES, importances))
    
    # Local "Reasoning" logic
    reasons = []
    # Bullish
    if latest['RSI'] < 30: reasons.append("🟢 RSI is below 30 (Oversold condition)")
    if latest['MACD'] > latest['Signal_Line']: reasons.append("🟢 MACD is above Signal Line (Bullish momentum)")
    if latest['SMA_50'] > latest['SMA_200']: reasons.append("🟢 Golden Cross: SMA 50 is above SMA 200 (Long-term Bullish)")
    
    # Bearish
    if latest['RSI'] > 70: reasons.append("🔴 RSI is above 70 (Overbought condition)")
    if latest['MACD'] < latest['Signal_Line']: reasons.append("🔴 MACD is below Signal Line (Bearish momentum)")
    if latest['SMA_50'] < latest['SMA_200']: reasons.append("🔴 Death Cross: SMA 50 is below SMA 200 (Long-term Bearish)")
    
    if not reasons:
        reasons.append("⚪ Indicators are currently in a neutral range.")
    
    return {
        "label": label,
        "confidence": confidence,
        "importances": feature_importance_map,
        "reasons": reasons,
        "latest_values": latest.to_dict()
    }

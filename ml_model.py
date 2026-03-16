# ml_model.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from indicators import calculate_indicators
from fetch import fetch_stock_data
import joblib
import os

# Fixed feature set
FEATURES = ['SMA_50', 'SMA_200', 'EMA_50', 'EMA_200', 'RSI', 'MACD', 'Signal_Line']
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")

def create_labeled_dataset(stock_id):
    # Use central fetch logic with 5y data for training
    df = fetch_stock_data(stock_id, period="5y")
    if df is None or df.empty:
        raise ValueError(f"No data found for {stock_id} to train model.")

    df = calculate_indicators(df)

    # Target creation: Predict if price will be > 5% higher in 10 days
    df['Future_Close'] = df['Close'].shift(-10)
    df.dropna(subset=['Close', 'Future_Close'], inplace=True)
    df['Target'] = np.where(df['Future_Close'] > df['Close'] * 1.05, 1, 0)

    # Use only selected features
    available_features = [f for f in FEATURES if f in df.columns]
    if len(available_features) < len(FEATURES):
        raise ValueError(f"Missing indicators in dataset. Needed: {FEATURES}")

    features = df[FEATURES].dropna()
    target = df.loc[features.index, 'Target']
    return features, target

def train_model(stock_id):
    print(f"[ML] Training model for {stock_id}...")
    X, y = create_labeled_dataset(stock_id)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    model_path = os.path.join(MODEL_DIR, f"{stock_id}_model.pkl")
    joblib.dump(model, model_path)
    print(f"[ML] Model saved to {model_path}")
    return model

def ml_predict(model, stock_data):
    # Ensure indicators are calculated
    processed_data = stock_data[FEATURES].dropna()
    
    if processed_data.empty:
        raise ValueError("Insufficient data to calculate technical indicators. Please select a longer timeframe (e.g., 1y).")

    latest = processed_data.iloc[-1]
    latest_df = pd.DataFrame([latest.values], columns=FEATURES)

    prediction = model.predict(latest_df)[0]
    confidence = model.predict_proba(latest_df)[0][prediction]

    label = "BUY" if prediction == 1 else "NO BUY"
    print(f"[ML] Confidence: {confidence:.2%}")
    return label

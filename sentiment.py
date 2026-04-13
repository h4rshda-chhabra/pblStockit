import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np

import streamlit as st

# Local model identifier
MODEL_NAME = "ProsusAI/finbert"

@st.cache_resource
def get_model():
    """Loads the model once and caches it in memory."""
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    return tokenizer, model

@st.cache_data(show_spinner=False)
def analyze_sentiment(headlines: list) -> dict:
    """
    Performs sentiment analysis on a list of headlines using local FinBERT model.
    Uses cached model instance for performance.
    """
    if not headlines:
        return {"label": "Neutral", "confidence": 1.0}

    # Use cached model and tokenizer
    tokenizer, model = get_model()

    # Encode headlines
    inputs = tokenizer(headlines, padding=True, truncation=True, return_tensors="pt")

    # Inference
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=1).numpy()

    # Aggregate probabilities (mean over all headlines)
    avg_probs = np.mean(probabilities, axis=0)
    
    # Label mapping for FinBERT: 0: Bullish, 1: Bearish, 2: Neutral
    labels = ["Bullish", "Bearish", "Neutral"]
    top_index = np.argmax(avg_probs)
    
    return {
        "label": labels[top_index],
        "confidence": float(avg_probs[top_index]),
        "probabilities": {labels[i]: float(avg_probs[i]) for i in range(len(labels))}
    }

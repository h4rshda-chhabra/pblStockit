# StockIt AI Analytics

**Live Demo:** [StockIt AI Dashboard](https://pblstockit-sgmbrahz3emuheve2fjyfr.streamlit.app/)

StockIt is an institutional-grade stock analysis and prediction platform. It leverages a hybrid intelligence model that combines quantitative technical indicators with natural language processing of financial news to provide high-accuracy market signals.

## Features
### Hybrid Signal Consensus
The platform features a proprietary Signal Consensus Indicator that synthesizes multiple data points into a single actionable verdict. It evaluates:
- Technical Strength: RSI (Relative Strength Index) and MACD (Moving Average Convergence Divergence).
- Sentiment Pulse: Real-time analysis of global financial reporting using Transformer-based models.
- AI Forecasting: Multi-day price trend predictions using ensemble learning (Random Forest).

### Live Market Telemetry
- Real-time price action fetching via Yahoo Finance.
- Interactive technical charting with candlestick patterns and volume overlays.
- Dynamic indicator calculation including SMA 50, SMA 200, and Bollinger Bands.

### Professional UI
- High-performance dashboard built with Streamlit.
- Glassmorphism design aesthetics for an institutional feel.
- Clean, focused interface optimized for analytical decision making.

## Technical Architecture
The system is organized into a modular four-layer architecture:
1. Data Layer: Handles API connectivity and telemetry ingestion.
2. Analytical Layer: Performs mathematical processing and indicator generation.
3. Intelligence Layer: Houses the Machine Learning models (Random Forest) and NLP Transformers (FinBERT).
4. Presentation Layer: Orchestrates the user interface and signal visualization.

## Installation

To set up the environment locally, ensure you have Python 3.8+ installed, then run:

```bash
pip install -r requirements.txt
```

## Usage

Start the analytical dashboard using the following command:

```bash
streamlit run app.py
```

Live Link: https://pblstockit-sgmbrahz3emuheve2fjyfr.streamlit.app/


## Disclaimer
This software is for educational and analytical purposes only. It does not constitute financial advice. Trading stocks involves significant risk, and users should perform their own due diligence or consult with a licensed professional before making investment decisions.

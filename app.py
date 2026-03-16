import streamlit as st
import pandas as pd
import numpy as np
import datetime
import os
import joblib
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Service Imports
from fetch import fetch_stock_data
from indicators import calculate_indicators
from ml_model import train_model, ml_predict, MODEL_DIR
from utils import normalize_period, get_consensus_verdict
from news import get_financial_news
from sentiment import analyze_sentiment
from ui_utils import apply_custom_style, header_section, footer_section, render_navbar, render_ticker

# --- Page Configuration ---
st.set_page_config(
    page_title="StockIt AI - Institutional Analytics",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply premium Styles
apply_custom_style()

# Render Header (Ticker + Navbar) and get current page
page = render_navbar()

# --- Page: Home ---
if page == "Home":
    st.markdown('''
        <div class="centered-layout" style="margin-top: 20px;">
            <h1 style="font-size: 5rem; font-weight: 800; color: #ffffff; letter-spacing: -2px; margin-bottom: 10px !important;">
                StockIt <span style="background: linear-gradient(120deg, #00ff9d 0%, #00d4ff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">AI Analytics</span>
            </h1>
            <p style="font-size: 1.5rem; font-weight: 400; color: rgba(255,255,255,0.6); margin-bottom: 40px !important;">
                Professional Stock Market Analysis for Smarter Investing
            </p>
        </div>
    ''', unsafe_allow_html=True)
    
    # Centered CTA Section
    st.markdown('<div class="centered-layout">', unsafe_allow_html=True)
    c_left, c_mid, c_right = st.columns([1, 2, 1])
    with c_mid:
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("GO TO ANALYZER", use_container_width=True):
                st.session_state.current_page_idx = 1  # Analyzer index
                st.rerun()
        with col_btn2:
            if st.button("MARKET PULSE", use_container_width=True):
                st.session_state.current_page_idx = 2  # Market index
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Feature Showcase
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown('''
            <div class="glass-card">
                <h3>Precision Analytics</h3>
                <p style="font-size: 0.95rem; color: rgba(255,255,255,0.8);">
                    Bridge the gap between complex quantitative models and intuitive investment decisions. 
                    Our platform provides real-time signal generation using ensemble learning and deep 
                    news analysis. Experience institutional-grade data processing at your fingertips.
                </p>
            </div>
        ''', unsafe_allow_html=True)

    with col2:
        st.markdown('''
            <div class="glass-card">
                <h3>Neural Foundations</h3>
                <p style="font-size: 0.95rem; color: rgba(255,255,255,0.8);">
                    Our proprietary core utilizes Random Forest classifiers optimized for short-to-medium 
                    term forecasting. Integrated with the FinBERT transformer for real-time sentiment 
                    evaluation of financial reporting, we deliver a 360-degree market view.
                </p>
            </div>
        ''', unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    f_cols = st.columns(4, gap="medium")
    
    features = [
        ("Live Market Data", "Real-time feeds from NSE & BSE indices.", ""),
        ("AI-Based Predictions", "Advanced Random Forest models for price trends.", ""),
        ("Technical Analysis", "Interactive charts with RSI, MACD, and SMAs.", ""),
        ("Sentiment Insights", "Proprietary analysis of global market news.", "")
    ]
    
    for i, (f_title, f_desc, f_icon) in enumerate(features):
        with f_cols[i]:
            st.markdown(f'''
                <div class="glass-card" style="text-align: center; height: 250px; display: flex; flex-direction: column; justify-content: center;">
                    <h3 style="font-size: 1.2rem; margin-bottom: 0.8rem !important; color: #ffffff;">{f_title}</h3>
                    <p style="font-size: 0.9rem; color: rgba(255,255,255,0.6); line-height: 1.5;">{f_desc}</p>
                </div>
            ''', unsafe_allow_html=True)


# --- Page: Market ---
elif page == "Market":
    header_section("Market Pulse", "Real-time Inter-exchange Connectivity and Performance")
    
    with st.container():
        input_col1, input_col2, input_col3 = st.columns([2, 1, 2], gap="medium")
        with input_col1:
            stock_id = st.text_input("Ticker Symbol", value="RELIANCE", placeholder="e.g. RELIANCE, TCS, AAPL").upper()
        with input_col2:
            user_period = st.selectbox("Timeline", ["1mo", "6mo", "1y", "5y", "max"], index=2)
        with input_col3:
            compare_stocks = st.multiselect("Benchmark Comparison", ["TCS", "INFY", "HDFCBANK", "TATASTEEL", "WIPRO"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.spinner(f"Rendering technical charts for {stock_id}..."):
        period = normalize_period(user_period)
        main_df = fetch_stock_data(stock_id, period)
        
        if main_df is not None and not main_df.empty:
            main_df = calculate_indicators(main_df)
            
            chart_col, stat_col = st.columns([3, 1], gap="medium")
            
            with chart_col:
                # Plotly Advanced Charting
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                   vertical_spacing=0.03, row_heights=[0.7, 0.3])

                # 1. Candlestick
                fig.add_trace(go.Candlestick(
                    x=main_df.index,
                    open=main_df['Open'],
                    high=main_df['High'],
                    low=main_df['Low'],
                    close=main_df['Close'],
                    name=f'{stock_id} OHLC'
                ), row=1, col=1)

                # 2. Indicators (MA)
                if 'SMA_50' in main_df.columns:
                    fig.add_trace(go.Scatter(x=main_df.index, y=main_df['SMA_50'], name='SMA 50', 
                                           line=dict(color='#00d4ff', width=1.5)), row=1, col=1)
                
                # 3. Volume
                colors = ['#ff4b4b' if row['Open'] > row['Close'] else '#00d4ff' for _, row in main_df.iterrows()]
                fig.add_trace(go.Bar(x=main_df.index, y=main_df['Volume'], name='Volume', marker_color=colors), row=2, col=1)

                # 4. Comparisons (Line plots)
                for comp_id in compare_stocks:
                    comp_df = fetch_stock_data(comp_id, period)
                    if comp_df is not None and not comp_df.empty:
                        fig.add_trace(go.Scatter(x=comp_df.index, y=comp_df['Close'], name=comp_id, 
                                               line=dict(dash='dot', width=1.5)), row=1, col=1)

                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis_rangeslider_visible=False,
                    height=650,
                    margin=dict(l=10, r=10, t=30, b=10),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                fig.update_xaxes(showgrid=False)
                fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')

                st.plotly_chart(fig, use_container_width=True)
            
            with stat_col:
                st.write("### Technical Scan")
                latest = main_df.iloc[-1]
                
                def fmt_val(val, suffix=""):
                    return f"{val:.2f}{suffix}" if not np.isnan(val) else "N/A"

                metrics = [
                    ("RSI (14)", fmt_val(latest.get('RSI', np.nan)), "#00d4ff"),
                    ("MACD", fmt_val(latest.get('MACD', np.nan)), "#00ff9d"),
                    ("SMA 50", fmt_val(latest.get('SMA_50', np.nan)), "#ffffff"),
                    ("SMA 200", fmt_val(latest.get('SMA_200', np.nan)), "#ffffff"),
                    ("VOL", f"{latest.get('Volume', 0)/1e6:.1f}M", "#ffffff")
                ]
                
                for label, val, color in metrics:
                    st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.05); padding: 15px 0;">
                            <span style="color: rgba(255,255,255,0.4); font-size: 0.85rem; font-weight: 700; text-transform: uppercase;">{label}</span>
                            <span style="font-weight: 700; color: {color}; font-family: 'JetBrains Mono', monospace;">{val}</span>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.error(f"Inaccessible symbol: {stock_id}. Verify input.")

# --- Page: Analyzer ---
elif page == "Analyzer":
    header_section("Predictive Inference", "Ensemble Classifiers and Transformer Intelligence")
    
    config_col, run_col = st.columns([1, 1], gap="large")
    
    with config_col:
        st.write("### Inference Configuration")
        analyze_id = st.text_input("Target Ticker Symbol", value="RELIANCE").upper()
        a_col1, a_col2 = st.columns(2)
        with a_col1:
            analyze_period = st.selectbox("Historical Training Depth", ["1y", "5y", "max"], index=0)
        with a_col2:
            st.write("<br>", unsafe_allow_html=True)
            fast_mode = st.checkbox("Bypass Sentiment Engine", value=False)
        
        run_btn = st.button("Initialize Inference Sequence")

    if run_btn:
        with st.spinner("Executing Inference Sequence..."):
            try:
                df = fetch_stock_data(analyze_id, normalize_period(analyze_period))
                if df is None or df.empty: raise ValueError("Telemetry stream offline.")
                
                df = calculate_indicators(df)
                
                model_path = os.path.join(MODEL_DIR, f"{analyze_id}_model.pkl")
                if not os.path.exists(model_path):
                    model = train_model(analyze_id)
                else:
                    model = joblib.load(model_path)
                
                prediction = ml_predict(model, df)
                
                sentiment = {"label": "Neutral", "confidence": 0.0}
                headlines = []
                if not fast_mode:
                    headlines = get_financial_news(analyze_id)
                    sentiment = analyze_sentiment(headlines)
                
                with run_col:
                    st.write(f"### {analyze_id} Core Insight")
                    
                    res_c1, res_c2 = st.columns(2)
                    with res_c1:
                        st.write("**AI Signal**")
                        if "BUY" in prediction and "NO" not in prediction:
                            st.success(f"### {prediction}")
                        else:
                            st.error(f"### {prediction}")
                    
                    with res_c2:
                        st.write("**NLP Pulse**")
                        st.info(f"### {sentiment['label'].upper()}")
                        st.write(f"Confidence: {sentiment['confidence']:.1%}")
                    
                    # Signal Consensus Section
                    st.markdown("<br>", unsafe_allow_html=True)
                    latest_rsi = df['RSI'].iloc[-1]
                    latest_macd = df['MACD'].iloc[-1]
                    consensus = get_consensus_verdict(latest_rsi, latest_macd, sentiment['label'])
                    
                    st.write("---")
                    st.write("### Signal Consensus")
                    
                    alert_type = st.success if "Buy" in consensus['verdict'] else st.error if "Sell" in consensus['verdict'] else st.info
                    alert_type(f"## {consensus['verdict'].upper()}")
                    st.write(f"(Technical: {consensus['tech_signal']}, Sentiment: {sentiment['label']})")

            except Exception as e:
                status.update(label="Inference Failure", state="error")
                st.error(f"Critical System Error: {e}")


# --- Page: Sentiment ---
elif page == "Sentiment":
    header_section("Sentiment Intelligence", "Natural Language Processing of Financial Headlines")
    
    tab1, tab2 = st.tabs(["Live News Tracking", "Custom Intel Input"])
    
    with tab1:
        sent_sym = st.text_input("Enter Ticker for Live Sentiment", value="RELIANCE").upper()
        if st.button("Analyze Live Feed"):
            with st.spinner(f"Scanning market telemetry for ${sent_sym}..."):
                headlines = get_financial_news(sent_sym)
                if headlines:
                    sentiment = analyze_sentiment(headlines)
                    
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.write(f"### Verdict: {sentiment['label'].upper()}")
                        st.write(f"**Confidence:** {sentiment['confidence']:.1%}")
                    
                    with col2:
                        for label, prob in sentiment['probabilities'].items():
                            st.write(f"{label}")
                            st.progress(prob)
                    
                    # Only show headlines if they are actually found (not generic)
                    st.write("#### Recent Intel Headlines")
                    for h in headlines: st.markdown(f"- {h}")
                else:
                    st.warning("No fresh news detected for this ticker.")

    with tab2:
        st.write("### Direct Text Analysis")
        custom_news = st.text_area("Paste news headlines or reports here (one per line)", height=200, 
                                 placeholder="e.g. RELIANCE Q3 profits soar 20%\nMarket analysts upgrade stock rating to Buy")
        
        if st.button("Run Intel Inference"):
            if custom_news.strip():
                headlines = [h.strip() for h in custom_news.split("\n") if h.strip()]
                with st.spinner("Processing custom intel..."):
                    sentiment = analyze_sentiment(headlines)
                    
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.write(f"### Verdict: {sentiment['label'].upper()}")
                        st.write(f"**Confidence:** {sentiment['confidence']:.1%}")
                    
                    with col2:
                        for label, prob in sentiment['probabilities'].items():
                            st.write(f"{label}")
                            st.progress(prob)
            else:
                st.info("Please enter some text to analyze.")

# Global Footer
footer_section()

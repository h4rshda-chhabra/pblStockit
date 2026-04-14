import streamlit as st
import pandas as pd
import numpy as np
import datetime
import os
import joblib
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

import streamlit.components.v1 as components
from fetch import fetch_stock_data
from indicators import calculate_indicators
from ml_model import ml_predict, load_or_train_model
from utils import normalize_period, get_consensus_verdict, generate_technical_reasoning
from news import get_financial_news
from sentiment import analyze_sentiment
from ui_utils import apply_custom_style, header_section, footer_section, render_navbar

st.set_page_config(
    page_title="StockIt AI - Institutional Analytics",
    layout="wide",
    initial_sidebar_state="collapsed"
)

apply_custom_style()

# Background cleanup
components.html("""
    <script>
        const canvas = window.parent.document.getElementById('pixelblast-bg');
        if (canvas) { canvas.remove(); }
    </script>
""", height=0, width=0)

page = render_navbar()

if page == "Home":
    particles_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body, html { margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background: #06080a;}
            canvas { display: block; width: 100vw; height: 100vh; }
        </style>
    </head>
    <body onload="init()">
        <canvas id="cosmos"></canvas>
        <script>

            try {
                const frame = window.frameElement;
                if (frame) {
                    frame.style.position = 'fixed';
                    frame.style.top = '0';
                    frame.style.left = '0';
                    frame.style.width = '100vw';
                    frame.style.height = '100vh';
                    frame.style.zIndex = '-999'; // Deepest background
                    frame.style.border = 'none';
                    frame.style.pointerEvents = 'auto'; 
                }
            } catch(e) {}

            const canvas = document.getElementById('cosmos');
            const ctx = canvas.getContext('2d');
            let w = canvas.width = window.innerWidth;
            let h = canvas.height = window.innerHeight;
            
            window.addEventListener('resize', () => {
                w = canvas.width = window.innerWidth;
                h = canvas.height = window.innerHeight;
            });
            
            const particles = [];
            for(let i=0; i<300; i++) {
                particles.push({
                    x: Math.random() * w,
                    y: Math.random() * h,
                    vx: (Math.random() - 0.5) * 0.4,
                    vy: (Math.random() - 0.5) * 0.4,
                    size: Math.random() * 2 + 0.5
                });
            }

            let mouseX = -1000;
            let mouseY = -1000;
            window.addEventListener('mousemove', (e) => {
                mouseX = e.clientX; mouseY = e.clientY;
            });
            window.addEventListener('mouseleave', () => {
                mouseX = -1000; mouseY = -1000;
            });

            function draw() {
                requestAnimationFrame(draw);
                ctx.clearRect(0,0,w,h);
                ctx.fillStyle = 'rgba(255, 255, 255, 0.25)';
                
                for(let p of particles) {
                    p.x += p.vx;
                    p.y += p.vy;
                    if (p.x < 0) p.x = w; if (p.x > w) p.x = 0;
                    if (p.y < 0) p.y = h; if (p.y > h) p.y = 0;

                    const dx = mouseX - p.x;
                    const dy = mouseY - p.y;
                    const dist = Math.sqrt(dx*dx + dy*dy);
                    if (dist < 120) {
                        p.x -= dx * 0.03;
                        p.y -= dy * 0.03;
                    }

                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.size, 0, Math.PI*2);
                    ctx.fill();
                }
            }
            draw();
        </script>
    </body>
    </html>
    """
    
    # Minimal bounding box natively
    components.html(particles_html, height=0)

    # Bring UI forward
    st.markdown('''
        <style>
        .stApp { 
            background: radial-gradient(circle at top, #0A1128 0%, #020408 100%) !important; 
        }

        /* Elevate the container so clicks register and it overlays visually */
        .main .block-container {
            position: relative !important;
            z-index: 999 !important;
            background: transparent !important;
            padding-bottom: 0 !important;
            margin-top: 5vh !important;
        }

        /* Animations */
        @keyframes fadeInUp {
            0% { opacity: 0; transform: translateY(40px); }
            100% { opacity: 1; transform: translateY(0); }
        }

        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
            100% { transform: translateY(0px); }
        }

        /* Spotlight Blob */
        .spotlight {
            position: absolute;
            top: -30vh;
            left: 50%;
            transform: translateX(-50%);
            width: 1000px;
            height: 800px;
            background: radial-gradient(circle, rgba(0, 212, 255, 0.18) 0%, rgba(0, 88, 255, 0.08) 40%, transparent 70%);
            filter: blur(60px);
            z-index: -1;
            pointer-events: none;
            animation: pulse-glow 8s infinite alternate;
        }

        @keyframes pulse-glow {
            0% { transform: translateX(-50%) scale(0.9); opacity: 0.6; }
            100% { transform: translateX(-50%) scale(1.1); opacity: 1; }
        }

        .home-heading-wrap {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding-bottom: 50px;
            position: relative;
        }
        
        /* Floating Stats Card */
        .anchor-card {
            background: rgba(15, 20, 30, 0.6);
            backdrop-filter: blur(24px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-top: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 100px;
            padding: 10px 25px;
            display: inline-flex;
            align-items: center;
            gap: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.4), inset 0 1px 1px rgba(255,255,255,0.1);
            margin-bottom: 30px;
            opacity: 0;
            animation: fadeInUp 1s cubic-bezier(0.165, 0.84, 0.44, 1) 0.1s forwards, float 6s ease-in-out infinite;
        }
        .anchor-card strong { color: #ffffff; font-size: 1rem; font-weight: 600;}
        .anchor-badge {
            background: rgba(255, 75, 75, 0.15);
            color: #ff4b4b;
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: 800;
            font-size: 0.9rem;
            border: 1px solid rgba(255, 75, 75, 0.3);
            box-shadow: 0 0 15px rgba(255, 75, 75, 0.2);
        }

        .value-prop {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            font-size: 7.5rem;
            font-weight: 900;
            letter-spacing: -3px;
            line-height: 1.05;
            margin: 0 0 25px 0 !important;
            text-shadow: 0 0 50px rgba(0, 212, 255, 0.3);
            opacity: 0;
            animation: fadeInUp 1s cubic-bezier(0.165, 0.84, 0.44, 1) 0.2s forwards;
            color: #ffffff;
        }

        .value-prop span {
            background: linear-gradient(135deg, #ffffff 0%, #00d4ff 60%, #0088ff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .value-prop .highlight-underline {
            position: relative;
            display: inline-block;
        }
        
        .value-prop .highlight-underline::after {
            content: '';
            position: absolute;
            left: 0;
            bottom: -5px;
            width: 100%;
            height: 6px;
            background: #00d4ff;
            border-radius: 3px;
            box-shadow: 0 0 20px #00d4ff, 0 0 40px #0088ff;
            animation: expand-line 1.5s cubic-bezier(0.165, 0.84, 0.44, 1) 0.6s forwards;
            opacity: 0;
            width: 0;
        }
        
        @keyframes expand-line {
            0% { width: 0; opacity: 0; }
            100% { width: 100%; opacity: 1; }
        }

        .sub-prop {
            color: #e2e8f0;
            font-size: 1.8rem;
            max-width: 800px;
            margin: 0 auto !important;
            line-height: 1.6;
            font-weight: 500;
            opacity: 0;
            text-shadow: 0 2px 10px rgba(0,0,0,0.5);
            animation: fadeInUp 1s cubic-bezier(0.165, 0.84, 0.44, 1) 0.4s forwards;
        }

        /* Stagger Horizontal Blocks (Buttons) */
        [data-testid="stHorizontalBlock"] {
            opacity: 0;
            animation: fadeInUp 1s cubic-bezier(0.165, 0.84, 0.44, 1) 0.6s forwards;
        }

        /* Float all buttons slightly */
        div.stButton > button {
            animation: float 7s ease-in-out infinite reverse;
        }

        /* Primary Button */
        div.stButton > button[data-testid="baseButton-primary"] {
            height: 70px !important;
            font-size: 1.25rem !important;
            font-weight: 700 !important;
            background: linear-gradient(135deg, #00d4ff 0%, #0066ff 100%) !important;
            border: none !important;
            color: #ffffff !important;
            border-radius: 12px !important;
            box-shadow: 0 10px 30px rgba(0, 212, 255, 0.3), inset 0 2px 2px rgba(255,255,255,0.4) !important;
            transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1) !important;
        }
        div.stButton > button[data-testid="baseButton-primary"]:hover {
            transform: scale(1.05) !important; /* Float handles Y, so we just scale here */
            box-shadow: 0 20px 40px rgba(0, 212, 255, 0.5), inset 0 2px 2px rgba(255,255,255,0.6) !important;
            background: linear-gradient(135deg, #00e0ff 0%, #0077ff 100%) !important;
        }

        /* Secondary Button */
        div.stButton > button[data-testid="baseButton-secondary"] {
            height: 70px !important;
            font-size: 1.2rem !important;
            font-weight: 600 !important;
            background: rgba(255, 255, 255, 0.02) !important;
            backdrop-filter: blur(15px) !important;
            border: 2px solid rgba(255, 255, 255, 0.2) !important;
            color: #ffffff !important;
            border-radius: 12px !important;
            box-shadow: 0 8px 20px rgba(0,0,0,0.3) !important;
            transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1) !important;
        }
        div.stButton > button[data-testid="baseButton-secondary"]:hover {
            background: rgba(255, 255, 255, 0.1) !important;
            border-color: #00d4ff !important;
            box-shadow: 0 0 25px rgba(0, 212, 255, 0.3) !important;
            transform: scale(1.03) !important;
            color: #00d4ff !important;
        }
        </style>
        
        <div class="home-heading-wrap" style="margin-top: 10vh;">
            <div class="spotlight"></div>
            <div class="anchor-card">
                <span style="font-size: 1.2rem; color: #ff4b4b;">↓</span>
                <strong>Live Signal Context:</strong>
                <span class="anchor-badge">BEARISH (97%)</span>
            </div>
            <h1 class="value-prop"><span>StockIt AI</span><br><div class="highlight-underline">Next-Gen Intelligence.</div></h1>
            <p class="sub-prop">StockIt AI processes thousands of technical structures and NLP sentiment data points to deliver institutional-grade predictive analytics directly to your screen.</p>
        </div>
    ''', unsafe_allow_html=True)

    # CTA Grid
    _, center_cta, _ = st.columns([1, 8, 1])
    with center_cta:
        col1, col2, col3, col4 = st.columns(4, gap="medium")
        with col1:
            if st.button("Run Analysis", type="primary", use_container_width=True):
                st.session_state.current_page = "Analyzer"
                st.rerun()
        with col2:
            if st.button("Explore Market", type="secondary", use_container_width=True):
                st.session_state.current_page = "Market"
                st.rerun()
        with col3:
            if st.button("Sentiment Scanner", type="secondary", use_container_width=True):
                st.session_state.current_page = "Sentiment"
                st.rerun()
        with col4:
            if st.button("Education Hub", type="secondary", use_container_width=True):
                st.session_state.current_page = "Education"
                st.rerun()


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
                
                with st.expander("📚 How to read these charts?"):
                    st.markdown("""
                        - **Candlestick Chart**: Shows Open, High, Low, and Close prices. Blue/Green means the price closed higher than it opened; Red means it closed lower.
                        - **SMA 50 (Simple Moving Average)**: The average price over the last 50 periods. When the price is above the SMA 50, it's often considered a bullish trend.
                        - **Volume**: The number of shares traded. High volume confirms the strength of a price move.
                        - **Benchmark Comparison**: The dotted lines show how other stocks performed over the same period, allowing you to gauge relative strength.
                    """)
            
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
    
    st.markdown('''
    <style>
        /* Card Layout for Input Row */
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stTextInput"]) {
            background: linear-gradient(145deg, rgba(30, 35, 45, 0.6), rgba(20, 25, 35, 0.8));
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 30px 40px;
            margin-bottom: 40px;
            box-shadow: 0 10px 40px -10px rgba(0,0,0,0.6);
            align-items: center;
        }
        .microcopy {
            font-size: 0.8rem;
            color: rgba(255,255,255,0.4);
            margin-top: -10px;
            margin-bottom: 15px;
            padding-left: 5px;
            letter-spacing: 0px;
        }
        /* Run Inference Button - High End */
        div[data-testid="stButton"] button[kind="primary"] {
            background: linear-gradient(135deg, #00d4ff 0%, #0088ff 100%) !important;
            border: none !important;
            color: #ffffff !important;
            height: 65px !important;
            box-shadow: 0 8px 25px rgba(0, 212, 255, 0.25), inset 0 1px 1px rgba(255,255,255,0.2) !important;
            transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1) !important;
            overflow: hidden;
            position: relative;
        }
        div[data-testid="stButton"] button[kind="primary"]::after {
            content: "";
            position: absolute;
            top: 0; left: -100%;
            width: 50%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            transform: skewX(-20deg);
            transition: all 0.5s ease;
        }
        div[data-testid="stButton"] button[kind="primary"]:hover::after {
            left: 150%;
            transition: all 0.7s ease;
        }
        div[data-testid="stButton"] button[kind="primary"]:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 12px 30px rgba(0, 212, 255, 0.4), inset 0 1px 1px rgba(255,255,255,0.4) !important;
        }
    </style>
    ''', unsafe_allow_html=True)
    
    in_col1, in_col2, in_col3, in_col4 = st.columns([2.5, 1.5, 1.2, 1.8], gap="large")
    with in_col1:
        analyze_id = st.text_input("Target Ticker (NSE/BSE)", value="RELIANCE").upper()
        st.markdown('<div class="microcopy">Enter exact tracking symbol (e.g., AAPL)</div>', unsafe_allow_html=True)
    with in_col2:
        analyze_period = st.selectbox("Training Depth", ["1y", "5y", "max"], index=1)
        st.markdown('<div class="microcopy">Set ML lookback bounds</div>', unsafe_allow_html=True)
    with in_col3:
        st.write("<br>", unsafe_allow_html=True)
        fast_mode = st.checkbox("Bypass NLP", value=False)
        st.markdown('<div class="microcopy" style="margin-top:-20px;">Use fast-mode</div>', unsafe_allow_html=True)
    with in_col4:
        st.write("<br>", unsafe_allow_html=True)
        run_btn = st.button("RUN INFERENCE", type="primary", use_container_width=True)

    if run_btn:
        with st.status("Executing Neural Pipeline...", expanded=True) as status:
            st.write("Initializing telemetry stream...")
            df = fetch_stock_data(analyze_id, normalize_period(analyze_period))
            
            if df is None or df.empty:
                status.update(label="Inference Error", state="error", expanded=True)
                st.error(f"Failed to fetch market data for '{analyze_id}'. Please check if the ticker symbol is correct.")
                st.stop()
                
            st.write("Computing technical manifold...")
            df = calculate_indicators(df)
            
            st.write("Loading ensemble weights...")
            try:
                model, metrics = load_or_train_model(analyze_id)
            except ValueError as e:
                status.update(label="Inference Error", state="error", expanded=True)
                st.error(f"Cannot process target: {str(e)}")
                st.stop()
            
            st.write("Running predictive cycle...")
            res_data = ml_predict(model, df)
            
            sentiment = {"label": "Neutral", "confidence": 0.0}
            if not fast_mode:
                st.write("Analyzing news sentiment...")
                headlines = get_financial_news(analyze_id)
                sentiment = analyze_sentiment(headlines)
            
            status.update(label="Inference Complete", state="complete", expanded=False)
            
            # --- Store History ---
            if "inference_history" not in st.session_state:
                st.session_state.inference_history = []
            
            import datetime
            st.session_state.inference_history.insert(0, {
                "ticker": analyze_id,
                "signal": res_data['label'],
                "confidence": res_data['confidence'],
                "time": datetime.datetime.now().strftime("%H:%M")
            })
            st.session_state.inference_history = st.session_state.inference_history[:5]

        # --- EXPLAINABLE AI DASHBOARD ---
        st.markdown(f'<h2 style="margin-top:20px; border-bottom: 2px solid rgba(0, 212, 255, 0.2); padding-bottom: 10px; margin-bottom: 20px;">{analyze_id} Analytics Dashboard</h2>', unsafe_allow_html=True)
        
        # Mini Trend Chart
        try:
            mini_df = df.tail(30).copy()
            import plotly.graph_objects as go
            fig_mini = go.Figure()
            fig_mini.add_trace(go.Scatter(x=mini_df.index, y=mini_df['Close'], mode='lines', name='Price', line=dict(color='#00d4ff', width=3)))
            if 'SMA_50' in mini_df.columns:
                fig_mini.add_trace(go.Scatter(x=mini_df.index, y=mini_df['SMA_50'], name='SMA 50', line=dict(color='rgba(255,255,255,0.3)', width=2, dash='dot')))
            fig_mini.update_layout(height=160, margin=dict(l=0, r=0, t=10, b=10), template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis_visible=False, yaxis_visible=False, showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig_mini, use_container_width=True, config={'displayModeBar': False})
        except Exception:
            pass
        
        # Grid Layout
        st.markdown('''
            <style>
                /* Animation Keyframes */
                @keyframes fade-in-up {
                    0% { opacity: 0; transform: translateY(15px); }
                    100% { opacity: 1; transform: translateY(0); }
                }
                @keyframes bar-fill {
                    0% { width: 0%; }
                }
                
                /* Premium Cards */
                .premium-card {
                    background: linear-gradient(160deg, rgba(30, 35, 45, 0.4), rgba(15, 20, 25, 0.8));
                    border: 1px solid rgba(255, 255, 255, 0.06);
                    border-radius: 16px;
                    padding: 25px;
                    margin-bottom: 25px;
                    box-shadow: 0 10px 40px -10px rgba(0,0,0,0.5);
                    animation: fade-in-up 0.6s ease forwards;
                    position: relative;
                    overflow: hidden;
                }
                
                /* Radial Chart Base */
                .radial-progress {
                    width: 60px;
                    height: 60px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    position: relative;
                }
                .radial-inner {
                    width: 48px;
                    height: 48px;
                    background: #141822;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 0.85rem;
                    font-weight: 700;
                    color: white;
                }
                
                /* Technical Pills */
                .tech-pill {
                    background: rgba(255,255,255,0.03);
                    border-radius: 8px;
                    padding: 15px 20px;
                    margin-bottom: 12px;
                    font-size: 0.95rem;
                    line-height: 1.5;
                    font-weight: 600;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    transition: all 0.2s ease;
                }
                .tech-pill:hover {
                    background: rgba(255,255,255,0.06);
                    transform: translateX(3px);
                }
            </style>
        ''', unsafe_allow_html=True)

        # Grid Layout
        col1, col2, col3 = st.columns([1.2, 1.3, 1.1], gap="large")

        # --- Column 1: AI Signal & Model Health ---
        with col1:
            c_label = res_data['label']
            if c_label == "BUY":
                base_color = "#00ff9d"
                icon = "↑"
                grad_bg = f"radial-gradient(circle at top right, rgba(0, 255, 157, 0.15) 0%, transparent 60%)"
            elif c_label == "NO BUY":
                base_color = "#ff4b4b"
                icon = "↓"
                grad_bg = f"radial-gradient(circle at top right, rgba(255, 75, 75, 0.15) 0%, transparent 60%)"
            else:
                base_color = "#eedd88"
                icon = "( ! )"
                grad_bg = f"radial-gradient(circle at top right, rgba(238, 221, 136, 0.15) 0%, transparent 60%)"

            st.markdown(f'''
<div class="premium-card" style="background: {grad_bg}, linear-gradient(160deg, rgba(30, 35, 45, 0.4), rgba(15, 20, 25, 0.8));">
    <p style="color: rgba(255,255,255,0.5); font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">Ensemble AI Signal</p>
    <div style="display: flex; align-items: baseline; gap: 10px; margin-bottom: 5px;">
        <h2 style="color: {base_color}; font-size: 2.8rem; margin: 0; font-weight: 800; line-height: 1;">{c_label}</h2>
        <span style="font-size: 2rem; color: {base_color};">{icon}</span>
    </div>
    <p style="margin-top: 25px; margin-bottom: 8px; font-size: 0.85rem; color: rgba(255,255,255,0.7); font-weight: 600;">Algorithm Confidence <span style="float: right; color: white;">{res_data['confidence']:.1%}</span></p>
    <div style="width: 100%; background: rgba(255,255,255,0.1); border-radius: 4px; height: 8px; overflow: hidden; margin-bottom: 10px;">
        <div style="width: {res_data['confidence']*100}%; background: {base_color}; height: 100%; border-radius: 4px; box-shadow: 0 0 10px {base_color}; animation: bar-fill 1s ease-out forwards;"></div>
    </div>
</div>
            ''', unsafe_allow_html=True)

            # Model Health
            acc = metrics.get('accuracy', 0)
            prec = metrics.get('precision', 0)
            rec = metrics.get('recall', 0)
            
            def health_color(val):
                if val >= 0.8: return "#00ff9d" # Green
                if val >= 0.6: return "#eedd88" # Yellow
                return "#ff4b4b" # Red

            def build_radial(title, val, desc):
                color = health_color(val)
                return f'''
                <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
                    <div class="radial-progress" style="background: conic-gradient({color} {val*100}%, rgba(255,255,255,0.05) 0);">
                        <div class="radial-inner">{val:.0%}</div>
                    </div>
                    <div>
                        <div style="font-weight: 700; color: white; font-size: 0.95rem;">{title}</div>
                        <div style="font-size: 0.75rem; color: rgba(255,255,255,0.5);">{desc}</div>
                    </div>
                </div>
                '''

            st.markdown(f'''
                <div class="premium-card">
                    <p style="color: rgba(255,255,255,0.5); font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 20px;">Model Health Diagnostics</p>
                    {build_radial("Accuracy", acc, "Total correct predictions")}
                    {build_radial("Precision", prec, "Success rate when predicting BUY")}
                    {build_radial("Recall", rec, "Capture rate of actual breakout events")}
                </div>
            ''', unsafe_allow_html=True)

        # --- Column 2: Technical Signals ---
        with col2:
            tech_reasons = generate_technical_reasoning(df)
            latest_rsi = df['RSI'].iloc[-1]
            latest_macd = df['MACD'].iloc[-1]
            consensus = get_consensus_verdict(latest_rsi, latest_macd, sentiment['label'])
            
            warning_html = ""
            if (consensus['tech_signal'] == "Bullish" and res_data['label'] == "SHOULD NOT BUY"):
                warning_html = '''<div class="tech-pill" style="border-left: 4px solid #eedd88; background: rgba(238, 221, 136, 0.05);">
                <span style="font-size: 1.4rem;">( ! )</span>
                <div>
                    <span style="color: #eedd88; font-weight: 700; display: block;">Decision Conflict</span>
                    <span style="font-size: 0.8rem; color: rgba(255,255,255,0.6); font-weight: 400;">Indicators are Bullish, but AI history predicts no breakout. Cautious waiting advised.</span>
                </div>
                </div>'''
            
            reasons_html = ""
            for reason in res_data.get('reasons', []):
                # Classify pill based on sentiment words
                pill_color = "#00d4ff" # Neutral default
                icon_html = "⚪"
                border = "rgba(255,255,255,0.1)"
                
                if "Bullish" in reason or "above" in reason or "Golden" in reason:
                    pill_color = "#00ff9d"
                    icon_html = "↑"
                    border = "rgba(0, 255, 157, 0.4)"
                elif "Bearish" in reason or "below" in reason or "Death" in reason:
                    pill_color = "#ff4b4b"
                    icon_html = "↓"
                    border = "rgba(255, 75, 75, 0.4)"

                clean_text = reason.replace('🟢 ', '').replace('🔴 ', '').replace('⚪ ', '')
                # Tooltips mapping
                tooltip = "Standard momentum indicator"
                if "RSI" in reason: tooltip = "Relative Strength Index measures price momentum velocity."
                if "MACD" in reason: tooltip = "Moving Average Convergence Divergence tracks trend strength."
                if "SMA" in reason: tooltip = "Simple Moving Average smooths price over selected timeframe."

                reasons_html += f'''
                <div class="tech-pill" style="border-left: 3px solid {border};" title="{tooltip}">
                    <div style="font-size: 1.4rem;">{icon_html}</div>
                    <div style="color: rgba(255,255,255,0.9); font-size: 0.9rem;">{clean_text}</div>
                </div>'''

            st.markdown(f'''
                <div class="premium-card">
                    <p style="color: rgba(255,255,255,0.5); font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 20px;">Technical Signals Log</p>
                    {warning_html}
                    {reasons_html}
                </div>
            ''', unsafe_allow_html=True)

        # --- Column 3: Model Sensitivity ---
        with col3:
            imp_html = ""
            sorted_imp = sorted(res_data['importances'].items(), key=lambda x: x[1], reverse=True)
            for feat, val in sorted_imp:
                f_name = feat.replace("_", " ")
                # Tooltips mapping
                t_tip = "Algorithm structural weight"
                if "RSI" in f_name: t_tip = "Weight given to immediate momentum swings"
                elif "SMA" in f_name: t_tip = "Weight given to historical smoothing averages"
                elif "EMA" in f_name: t_tip = "Weight given to recent price sensitivity averages"
                elif "MACD" in f_name: t_tip = "Weight given to trend divergence crossovers"
                
                imp_html += f'''
                <div style="margin-bottom: 25px;" title="{t_tip}">
                    <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px;">
                        <span style="font-size: 0.85rem; color: rgba(255,255,255,0.85); font-weight: 700;">{f_name}</span>
                        <span style="font-size: 0.85rem; color: #00d4ff; font-family: 'JetBrains Mono', monospace; font-weight: 700;">{val:.1%}</span>
                    </div>
                    <div style="width: 100%; background: rgba(255,255,255,0.05); border-radius: 4px; height: 6px; overflow: hidden;">
                        <div style="width: {val*100}%; background: linear-gradient(90deg, #0088ff, #00d4ff); height: 100%; border-radius: 4px; animation: bar-fill 1.2s ease-out forwards;"></div>
                    </div>
                </div>'''
            
            st.markdown(f'''
                <div class="premium-card">
                    <p style="color: rgba(255,255,255,0.5); font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">Model Sensitivity</p>
                    <p style="font-size: 0.75rem; color: rgba(255,255,255,0.5); margin-bottom: 25px; line-height: 1.5;">Influence distribution matrix across technical tracking bounds.</p>
                    {imp_html}
                </div>
            ''', unsafe_allow_html=True)

        if "inference_history" in st.session_state and len(st.session_state.inference_history) > 0:
            st.markdown(f'<h3 style="margin-top:20px; color: white; font-size: 1.1rem; letter-spacing: 0.5px; opacity: 0.9;">Recent Predictions Timeline</h3>', unsafe_allow_html=True)
            hist_html = "<div style='display:flex; gap:15px; overflow-x:auto; padding-bottom:20px; margin-top:15px;'>"
            for entry in st.session_state.inference_history:
                colr = "#00ff9d" if "BUY" in entry['signal'] else "#ff4b4b" if "NO BUY" in entry['signal'] else "#eedd88"
                hist_html += f'''
                <div style="min-width: 160px; background: rgba(20,25,35,0.6); padding: 15px 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                    <div style="font-size: 0.75rem; color: rgba(255,255,255,0.4); margin-bottom: 5px;">{entry['time']}</div>
                    <div style="font-size: 1.15rem; color: white; font-weight: 700; margin-bottom: 5px;">{entry['ticker']}</div>
                    <div style="font-size: 0.95rem; color: {colr}; font-weight: 700;">{entry['signal']}</div>
                    <div style="font-size: 0.8rem; color: rgba(255,255,255,0.6); margin-top:5px;">{entry['confidence']:.1%} CF</div>
                </div>'''
            hist_html += "</div>"
            st.markdown(hist_html, unsafe_allow_html=True)

# --- Page: Sentiment ---
elif page == "Sentiment":
    header_section("Sentiment Intelligence", "Institutional-Grade Neural Intel & Forecasting")
    
    st.markdown('''
    <style>
        .premium-card {
            background: linear-gradient(165deg, rgba(35, 40, 50, 0.6), rgba(15, 20, 25, 0.9));
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px; padding: 30px; margin-bottom: 25px;
            box-shadow: 0 20px 40px -15px rgba(0,0,0,0.7);
            backdrop-filter: blur(20px);
            transition: all 0.3s ease;
        }
        .insight-card {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 12px; padding: 15px 20px; margin-bottom: 12px;
            border-left: 4px solid #00d4ff;
        }
        .signal-chip {
            background: rgba(0, 212, 255, 0.15); color: #00d4ff;
            padding: 4px 12px; border-radius: 20px; font-size: 0.8rem;
            font-weight: 600; display: inline-block; margin-right: 8px; margin-bottom: 8px;
            border: 1px solid rgba(0, 212, 255, 0.3);
        }
        @keyframes countUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .hero-number { animation: countUp 0.8s ease-out forwards; }
    </style>
    ''', unsafe_allow_html=True)

    sec_analysis, sec_quant = st.tabs(["Perception Hub", "Prediction Forecaster"])
    
    with sec_analysis:
        st.markdown('<div class="premium-card" style="border: 1px solid rgba(0, 212, 255, 0.2); margin: 0 auto 20px auto; max-width: 1000px;"><p style="color: #00d4ff; font-weight: 700; margin-bottom: 10px; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;">AI Neural Perception Input</p>', unsafe_allow_html=True)
        intel_input = st.text_area("Intel Source", height=100, placeholder="Paste financial news headline or earnings update...", label_visibility="collapsed", key="perc_input")
        st.markdown('</div>', unsafe_allow_html=True)
        
        btn_col, _ = st.columns([1, 2])
        with btn_col:
            st.markdown('<div style="text-align: center; margin: 0 auto; width: 100%;">', unsafe_allow_html=True)
            run_p = st.button("RUN AI PERCEPTION", type="primary", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if run_p:
            if intel_input.strip():
                headlines = [h.strip() for h in intel_input.split("\n") if h.strip()]
                with st.spinner("Analyzing linguistic manifold..."):
                    sentiment = analyze_sentiment(headlines)
                    s_label = sentiment['label']
                    s_score = (sentiment['probabilities'].get('Bullish', 0) - sentiment['probabilities'].get('Bearish', 0))
                    s_color = "#00ff9d" if s_score > 0.1 else "#ff4b4b" if s_score < -0.1 else "#eedd88"
                    conf_level = "High" if sentiment['confidence'] > 0.85 else "Medium" if sentiment['confidence'] > 0.65 else "Low"
                    
                    st.markdown(f'''
                        <div class="premium-card" style="position: relative; overflow: hidden; padding: 40px; margin: 20px auto; max-width: 1000px;">
                            <div style="position: absolute; top: -10px; right: -10px; font-size: 8rem; font-weight: 900; color: rgba(255,255,255,0.02); pointer-events: none; text-transform: uppercase;">{s_label}</div>
                            <p style="color: rgba(255,255,255,0.4); font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 25px;">Institutional Signal Verdict</p>
                            
                            <h2 style="color: {s_color}; font-size: 5rem; margin: 0; font-weight: 900; line-height: 1; letter-spacing: -2px;">{s_label.upper()}</h2>
                            
                            <div style="display: flex; align-items: center; gap: 20px; margin-top: 30px;">
                                <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); padding: 12px 20px; border-radius: 12px;">
                                    <p style="color: rgba(255,255,255,0.4); font-size: 0.65rem; font-weight: 700; text-transform: uppercase; margin-bottom: 5px;">Model Score</p>
                                    <span style="font-size: 1.6rem; color: white; font-weight: 800; font-family: 'JetBrains Mono';">{s_score:+.2f}</span>
                                </div>
                                <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); padding: 12px 20px; border-radius: 12px;">
                                    <p style="color: rgba(255,255,255,0.4); font-size: 0.65rem; font-weight: 700; text-transform: uppercase; margin-bottom: 5px;">Neural Confidence</p>
                                    <span style="font-size: 1.6rem; color: white; font-weight: 800; font-family: 'JetBrains Mono';">{sentiment['confidence']:.1%}</span>
                                </div>
                            </div>

                            <hr style="border-color: rgba(255,255,255,0.05); margin: 30px 0;">
                            
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <div style="width: 8px; height: 8px; background: {s_color}; border-radius: 50%; box-shadow: 0 0 10px {s_color};"></div>
                                <p style="color: rgba(255,255,255,0.4); font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">Status: {conf_level.upper()} CONVICTION</p>
                            </div>
                        </div>
                    ''', unsafe_allow_html=True)
            else: st.warning("Please enter text to analyze.")

    with sec_quant:
        st.markdown('<p style="color: rgba(255,255,255,0.7); font-size: 1.1rem; margin-bottom: 25px;">Institutional price forecasting based on calibrated event-study quantization.</p>', unsafe_allow_html=True)
        q_inp_c1, q_inp_c2 = st.columns([1, 2])
        with q_inp_c1: q_ticker = st.text_input("Forecast Symbol", value="RELIANCE").upper()
        with q_inp_c2: q_news = st.text_input("Event Specification", placeholder="Paste high-impact headline or news snippet here...", key="fore_input")
        
        st.write("<br>", unsafe_allow_html=True)
        if st.button("GENERATE NEURAL FORECAST", type="primary", use_container_width=True):
            if q_news.strip() and q_ticker:
                with st.spinner(f"Calibrating system for {q_ticker}..."):
                    news_data = analyze_sentiment([q_news])
                    mkt_df = fetch_stock_data(q_ticker, "1mo")
                    if mkt_df is not None and not mkt_df.empty:
                        from utils import quantify_sentiment_impact
                        curr_p = mkt_df['Close'].iloc[-1]
                        vol = mkt_df['Close'].pct_change().std()
                        impact = quantify_sentiment_impact(news_data['label'], news_data['confidence'], curr_p, vol)
                        
                        # Style Mapping
                        is_bull = impact['price_delta'] >= 0
                        theme_color = "#00ff9d" if is_bull else "#ff6b6b"
                        low_color = "#00ff9d22" if is_bull else "#ff6b6b22"
                        glow_shadow = f"0 0 60px {theme_color}33"
                        direction_text = "UP" if is_bull else "DOWN"
                        vol_level = "High" if vol > 0.03 else "Moderate" if vol > 0.015 else "Low"
                        conf_level = "High" if news_data['confidence'] > 0.8 else "Moderate" if news_data['confidence'] > 0.6 else "Low"
                        
                        header_insight = f"AI Predicts Short-Term {'Upside' if is_bull else 'Downside'} Momentum"
                        
                        st.markdown(f'<p style="color: white; font-size: 1.4rem; font-weight: 700; margin-bottom: 30px; border-left: 4px solid {theme_color}; padding-left: 15px; text-transform: uppercase; letter-spacing: 1px;">{header_insight}</p>', unsafe_allow_html=True)
                        
                        iq_c1, iq_c2 = st.columns([1, 1], gap="large")
                        with iq_c1:
                            st.markdown(f'''
                                <div class="premium-card" style="box-shadow: {glow_shadow}; border: 1px solid {theme_color}44; text-align: center; border-radius: 24px; hover-elevation: 10px;">
                                    <p style="color: rgba(255,255,255,0.5); font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">AI Signal Status</p>
                                    <h1 class="hero-number" style="color: {theme_color}; font-size: 4.8rem; margin: 15px 0; font-weight: 900;">{direction_text} {abs(impact['expected_change_pct']*100):.2f}%</h1>
                                    <p style="font-size: 1.6rem; color: white; opacity: 0.9; margin-top: -10px;">INR {impact['price_delta']:+.2f}</p>
                                    <div style="margin-top: 25px; background: {low_color}; padding: 8px 20px; border-radius: 50px; display: inline-block;">
                                        <span style="color: {theme_color}; font-weight: 800; font-size: 0.85rem;">{conf_level.upper()} CONVICTION ({news_data['confidence']:.0%})</span>
                                    </div>
                                </div>
                            ''', unsafe_allow_html=True)
                        with iq_c2:
                            st.markdown(f'''
                                <div class="premium-card" style="border-radius: 24px; border-right: 4px solid {theme_color};">
                                    <p style="color: rgba(255,255,255,0.5); font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">Reasoning Matrix</p>
                                    <div style="margin-top: 25px;">
                                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
                                            <span style="color: rgba(255,255,255,0.6); font-weight: 600;">Sentiment Analysis</span>
                                            <span style="color: white; font-weight: 700;">{news_data['label']}</span>
                                        </div>
                                        <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.05); margin: 0;">
                                        <div style="display: flex; align-items: center; justify-content: space-between; margin: 20px 0;">
                                            <span style="color: rgba(255,255,255,0.6); font-weight: 600;">Market Volatility</span>
                                            <span style="color: white; font-weight: 700;">{vol_level}</span>
                                        </div>
                                        <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.05); margin: 0;">
                                        <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 20px;">
                                            <span style="color: rgba(255,255,255,0.6); font-weight: 600;">Model Confidence</span>
                                            <span style="color: white; font-weight: 700;">{conf_level}</span>
                                        </div>
                                    </div>
                                    <div style="margin-top: 35px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 20px;">
                                        <p style="font-style: italic; color: {theme_color}; font-size: 1.1rem; line-height: 1.4; font-weight: 500;">
                                            Result: The {news_data['label'].lower()} factor combined with {vol_level.lower()} volatility suggests a definitive short-term movement.
                                        </p>
                                    </div>
                                </div>
                            ''', unsafe_allow_html=True)
                        
                        # Score Explanation
                        st.markdown(f'''
                            <div class="premium-card" style="background: rgba(255,255,255,0.02); border-color: rgba(255,255,255,0.05);">
                                <p style="color: rgba(255,255,255,0.5); font-size: 0.75rem; font-weight: 700; text-transform: uppercase; margin-bottom: 10px;">Sentiment Metric Definition</p>
                                <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem; line-height: 1.6;">
                                    The <b>Sentiment Score</b> ranges from <b>-1.0 (Extreme Bearish)</b> to <b>+1.0 (Extreme Bullish)</b>. 
                                    A score near 0.0 indicates a neutral market posture. This value represents the net probability weight 
                                    calculated by the transformer-based FinBERT model after analyzing the linguistic patterns of your input text.
                                </p>
                            </div>
                        ''', unsafe_allow_html=True)
                    else: st.error("Market data fetch failed.")
            else: st.warning("Enter both Symbol and Event specification.")

# --- Page: Education ---
elif page == "Education":
    header_section("Knowledge Base", "Interactive Learning Hub: AI & Market Systems")

    st.markdown('''
    <style>
        div[data-testid="stExpander"] { 
            background: rgba(30, 35, 45, 0.4); 
            border: 1px solid rgba(255,255,255,0.05); 
            border-radius: 12px; 
            margin-bottom: 10px; 
            transition: all 0.3s; 
        } 
        div[data-testid="stExpander"]:hover { 
            border-color: #00d4ff; 
            box-shadow: 0 0 15px rgba(0,212,255,0.1); 
            transform: translateX(4px);
        }
        div[data-testid="stExpander"] p {
            font-size: 0.95rem;
            color: rgba(255,255,255,0.8);
            line-height: 1.6;
        }
        .highlight {
            color: #00ff9d;
            font-weight: 700;
        }
    </style>
    ''', unsafe_allow_html=True)

    search_query = st.text_input("Search Knowledge Base", placeholder="Search for RSI, AI, Random Forest, MACD...").lower()
    st.write("<br>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["EQUITY & FUNDAMENTALS", "TECHNICALS & MACRO", "RISK & PSYCHOLOGY"])
    
    with tab1:
        st.markdown("""
        ## **Section I: The Foundational Architecture of Global Equity**
        
        ### **1.1 The Essence of Shareholding**
        Common stocks represent the residual claim on the assets and earnings of a corporation. In the hierarchy of capital structure, equity holders are "residual claimants," meaning they are the last to be paid after creditors, bondholders, and preferred shareholders in the event of liquidation. However, this positioning grants them the highest potential for **capital appreciation** and the unique right to vote on corporate governance.
        
        ### **1.2 Fundamental Analysis: The Search for Intrinsic Value**
        Fundamental analysis is the rigorous process of calculating the "true value" of a business, independent of its current market price. This discipline is divided into two primary dimensions:
        
        #### **A. Quantitative Matrix (The Financial Statements)**
        To maintain professional trust in your analysis, you must master the **Three Financial Statements**:
        1.  **The Income Statement (Statement of Operations):** This captures the revenue, expenses, and net profit over a specific reporting period (Quarterly or Annually). Key metrics include Operating Margin (Efficiency) and EBITDA (Earnings Before Interest, Taxes, Depreciation, and Amortization), which is used to compare companies across different tax jurisdictions.
        2.  **The Balance Sheet:** A snapshot of solvency at a single point in time. It follows the equation: *Assets = Liabilities + Equity*. Analysts use this to calculate the "Current Ratio" (Assets / Liabilities), which determines if a company can survive a short-term cash crunch.
        3.  **The Cash Flow Statement:** Unlike the Income Statement which uses "Accrual Accounting," the Cash Flow statement tracks actual liquidity. If a company shows high Net Income but negative Operating Cash Flow, it is a massive Red Flag indicating they are not actually collecting cash from their customers.
        
        #### **B. Qualitative Matrix (The Business Moat)**
        Inspired by Warren Buffett’s philosophy, a "Moat" is a company's competitive advantage. We look at:
        *   **Network Effects:** Platforms like LinkedIn or Visa become exponentially more valuable as the user base grows, creating a barrier that competitors cannot simply "spend" their way past.
        *   **Intellectual Property:** Patents and proprietary algorithms (like the one powering **StockIt AI**) provide high-margin protection from generic competition.
        *   **Cost Leadership:** Companies like Walmart or Reliance use massive scale to drive down unit costs to a level where challengers cannot survive a price war.
        
        ### **1.3 Dividend Policy and Share Buybacks**
        Mature companies often distribute profits via dividends or share repurchases. While dividends provide immediate income, share buybacks reduce the total number of shares outstanding, effectively increasing the "Earnings Per Share" (EPS) for remaining investors without requiring any actual business growth.
        """)

    with tab2:
        st.markdown("""
        ## **Section II: Technical Execution, Market Microstructure, and Macro Dynamics**
        
        ### **2.1 The Philosophy of Technical Analysis**
        Technical Analysis is the study of human crowd psychology. It operates on the thesis that "History Repeats Itself" because human nature (Greed and Fear) never changes. Charts are simply the visual representation of this conflict.
        
        ### **2.2 Advanced Technical Manifolds**
        *   **Support and Resistance (The S/R Mechanism):** Support represents a price level where "Buying Pressure" outweighs "Selling Pressure." Resistance is the opposite. When a Resistance level is broken, it often flips and becomes the new Support level—a concept known as "Polarity."
        *   **RSI Divergence Clusters:** When a stock hits a New High, but the RSI hits a Lower High, it indicates that the underlying "Buying Volume" is exhausted. This is often the precursor to a 10-20% correction.
        *   **Moving Average Ribboning:** By layering the 20, 50, and 200 CMAs, we can identify "Trend Velocity." If the 20 is above the 50, and the 50 is above the 200, the stock is in a persistent "Parabolic Run."
        
        ### **2.3 Macroeconomic Gravity: The Global Tide**
        1.  **Monetary Policy (The Central Bank):** The Fed and RBI use "Interest Rates" to control inflation. High rates "Discount" future valuations, making Tech stocks less valuable today. Low rates create "Liquidity Bubbles" where asset prices soar.
        2.  **The Yield Curve:** When 2-year bond interests are higher than 10-year interests, the curve is "Inverted." Historically, an inverted yield curve is the most accurate predictor of an upcoming Recession.
        3.  **Currency Fluctuations:** For IT companies like TCS or Infosys, a "Strong Dollar" is excellent because they earn in USD but spend in INR. A "Weak Dollar" hits their profit margins directly.
        """)
    
    with tab3:
        st.markdown("""
        ## **Section III: Professional Risk Management and Behavioral Bias**
        
        ### **3.1 Position Sizing (The Grail of Trading)**
        Most traders fail not because their entries are bad, but because their "Position Size" is too large. 
        *   **Risk Per Trade:** If your Stop-Loss is ₹10 away, and you want to risk only ₹1,000, you can only buy 100 shares. 
        *   **Concentration Risk:** Never put more than 20% of your total capital into a single sector. If the IT sector crashes due to a global policy change, your entire portfolio must not be wiped out.
        
        ### **3.2 Behavioral Finance: Decoding the Irrational Mind**
        *   **The Sunk Cost Fallacy:** Holding a stock down 50% because "I’ve already lost so much, it has to come back." Markets do not care about your entry price.
        *   **Recency Bias:** Believing that because a stock went up for the last 3 days, it will go up on the 4th day. This is how retail investors are lured into "Blow-off Tops."
        *   **The Dunning-Kruger Effect:** New traders often have a small win-streak and believe they have "solved the market," leading them to increase leverage right before a major crash.
        
        ### **3.3 Strategic Asset Allocation**
        Professional portfolios follow the **Core-Satellite Model**:
        *   **70% Core:** Allocated to stable, Large-Cap Blue Chip stocks or Index Funds for long-term growth.
        *   **30% Satellite:** Allocated to high-growth, AI-identified breakout stocks (using the **StockIt AI** engine) to generate "Excess Returns" or Alpha.
        """)

    st.markdown("---")
    st.markdown("""
    ### **Section IV: Academic and Professional References**
    The educational data on this platform is curated from university-level financial curriculum and institutional research papers:
    
    1.  **Graham, B. (1949).** *The Intelligent Investor.* Harper and Row Publishing.
    2.  **Malkiel, B. (1973).** *A Random Walk Down Wall Street.* W. W. Norton and Company.
    3.  **Kahneman, D., and Tversky, A. (1979).** *Prospect Theory: An Analysis of Decision under Risk.* Econometrica.
    4.  **CFA Institute.** *Equity Valuation and Market Microstructure Level II Curriculum.*
    5.  **Shiller, R. J. (2000).** *Irrational Exuberance.* Princeton University Press.
    6.  **Dalio, R. (2018).** *Principles for Navigating Big Debt Crises.* Bridgewater Associates Research.
    7.  **Yagan, D. (2019).** *Capital Gains and Economic Inequality.* University of California, Berkeley.
    8.  **Poundstone, W. (2005).** *Fortune's Formula: The Scientific Betting System that Beat the Casinos and Wall Street.*
    """)

    pages = ["Home", "Analyzer", "Market", "Sentiment", "Education"]
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"

    # Global Footer logic
    if st.session_state.current_page != "Home":
        footer_section()

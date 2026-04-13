import streamlit as st
import pandas as pd
import numpy as np
import datetime
import os
import joblib
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Service Imports
from fetch import fetch_stock_data
from indicators import calculate_indicators
from ml_model import train_model, ml_predict, load_or_train_model, MODEL_DIR
from utils import normalize_period, get_consensus_verdict, generate_technical_reasoning
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

# Ensure PixelBlast background is removed if not on Home Page
import streamlit.components.v1 as components
components.html("""
    <script>
        const canvas = window.parent.document.getElementById('pixelblast-bg');
        if (canvas) {
            canvas.remove();
        }
    </script>
""", height=0, width=0)

# Render Header (Ticker + Navbar) and get current page
page = render_navbar()

# --- Page: Home ---
if page == "Home":
    import streamlit.components.v1 as components
    
    particles_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body, html { margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background: #06080a;}
            canvas { display: block; width: 100vw; height: 100vh; }
        </style>
    </head>
    <body>
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
            
            st.write("Computing technical manifold...")
            df = calculate_indicators(df)
            
            st.write("Loading ensemble weights...")
            model, metrics = load_or_train_model(analyze_id)
            
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
            if (consensus['tech_signal'] == "Bullish" and res_data['label'] == "NO BUY"):
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
    header_section("🧠 Sentiment Intelligence", "Natural Language Processing of Financial Intel")
    
    st.markdown('''
    <style>
        .nlp-card {
            background: linear-gradient(160deg, rgba(30, 35, 45, 0.4), rgba(15, 20, 25, 0.8));
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 10px 40px -10px rgba(0,0,0,0.5);
            margin-bottom: 30px;
        }
        .chip-button-wrapper div.stButton > button {
            height: 44px !important;
            border-radius: 20px !important;
            padding: 5px 20px !important;
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            color: rgba(255, 255, 255, 0.8) !important;
            font-size: 1rem !important;
            font-weight: 500 !important;
            box-shadow: none !important;
            backdrop-filter: blur(10px) !important;
        }
        .chip-button-wrapper div.stButton > button:hover {
            border-color: #00d4ff !important;
            color: #ffffff !important;
            background: rgba(0, 212, 255, 0.15) !important;
            box-shadow: 0 0 15px rgba(0, 212, 255, 0.3) !important;
            transform: translateY(-2px) !important;
        }
    </style>
    ''', unsafe_allow_html=True)
    
    if "custom_news" not in st.session_state:
        st.session_state.custom_news = ""

    with st.container():
        st.markdown('<div class="nlp-card">', unsafe_allow_html=True)
        
        tab_text, tab_news = st.tabs(["📄 Paste Text", "📰 Analyze News"])
        
        with tab_text:
            st.markdown('<p style="color: rgba(255,255,255,0.7); font-size: 1.15rem; margin-bottom: 20px;">Paste any financial news or report...</p>', unsafe_allow_html=True)
            
            # Quick Chips replacing the buttons
            st.markdown('<div class="chip-button-wrapper">', unsafe_allow_html=True)
            st.markdown('<p style="font-size: 1rem; color: rgba(255,255,255,0.5); font-weight: 700; text-transform: uppercase;">Quick Examples</p>', unsafe_allow_html=True)
            c1, c2, c3, _ = st.columns([1.5, 1.5, 1.5, 3])
            if c1.button("Earnings Report", use_container_width=True): st.session_state.custom_news = "Profits soared 25% YoY, but margins faced slight pressure due to supply constraints."
            if c2.button("Breaking News", use_container_width=True): st.session_state.custom_news = "Federal reserve maintains interest rates, causing a neutral market plateau today."
            if c3.button("Market Tweet", use_container_width=True): st.session_state.custom_news = "The CEO's recent departure is deeply concerning. Stock looks doomed."
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<p style="margin-top: 25px; font-weight: 600; font-size: 1.25rem; color: #00d4ff;">Input Financial Text</p>', unsafe_allow_html=True)
            
            custom_news = st.text_area("Intel Input", height=200, 
                                     value=st.session_state.custom_news,
                                     placeholder="e.g. 'Apple announces a massive blowout quarter with 30% revenue growth...' ",
                                     max_chars=2000,
                                     label_visibility="collapsed")
            
            st.markdown(f'<div style="color: rgba(255,255,255,0.4); font-size: 1rem; margin-top: 5px;">Tip: Try pasting a news headline or earnings report</div>', unsafe_allow_html=True)

        with tab_news:
            st.markdown('<p style="color: rgba(255,255,255,0.7); font-size: 1.15rem;">Fetch latest financial news... (Module initializing)</p>', unsafe_allow_html=True)
        
        st.markdown('<hr style="border-color: rgba(255,255,255,0.1); margin: 30px 0;">', unsafe_allow_html=True)
        
        _, btn_col, _ = st.columns([1, 2, 1])
        with btn_col:
            run_intel = st.button("Analyze Sentiment", type="primary", use_container_width=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
    
    if run_intel:
        if custom_news.strip():
            headlines = [h.strip() for h in custom_news.split("\n") if h.strip()]
            with st.spinner("Analyzing with NLP model..."):
                sentiment = analyze_sentiment(headlines)
                
                s_label = sentiment['label']
                if "BULLISH" in s_label.upper() or "POSITIVE" in s_label.upper():
                    s_color = "#00ff9d"
                    s_icon = "↑"
                    bg_grad = "radial-gradient(circle at top right, rgba(0, 255, 157, 0.2) 0%, transparent 60%)"
                elif "BEARISH" in s_label.upper() or "NEGATIVE" in s_label.upper():
                    s_color = "#ff4b4b"
                    s_icon = "↓"
                    bg_grad = "radial-gradient(circle at top right, rgba(255, 75, 75, 0.2) 0%, transparent 60%)"
                else:
                    s_color = "#eedd88"
                    s_icon = "---"
                    bg_grad = "radial-gradient(circle at top right, rgba(238, 221, 136, 0.2) 0%, transparent 60%)"

                st.write("<br>", unsafe_allow_html=True)
                res_col1, res_col2 = st.columns([1.2, 1.5], gap="large")
                
                with res_col1:
                    st.markdown(f'''
                        <div class="premium-card" style="background: {bg_grad}, linear-gradient(160deg, rgba(30, 35, 45, 0.4), rgba(15, 20, 25, 0.8));">
                            <p style="color: rgba(255,255,255,0.5); font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">Engine Verdict</p>
                            <div style="display: flex; align-items: center; gap: 15px; margin: 15px 0;">
                                <h2 style="color: {s_color}; font-size: 2.5rem; margin: 0; font-weight: 800;">{s_label.upper()}</h2>
                                <span style="font-size: 2.2rem; color: {s_color};">{s_icon}</span>
                            </div>
                            <p style="margin-top: 25px; margin-bottom: 8px; font-size: 0.85rem; color: rgba(255,255,255,0.7); font-weight: 600;">Neural Confidence <span style="float: right; color: white;">{sentiment['confidence']:.1%}</span></p>
                            <div style="width: 100%; background: rgba(255,255,255,0.1); border-radius: 4px; height: 8px; overflow: hidden; margin-bottom: 5px;">
                                <div style="width: {sentiment['confidence']*100}%; background: {s_color}; height: 100%; border-radius: 4px; box-shadow: 0 0 10px {s_color}; animation: bar-fill 1s ease-out forwards;"></div>
                            </div>
                        </div>
                    ''', unsafe_allow_html=True)
                
                with res_col2:
                    prob_html = ""
                    for label, prob in sentiment['probabilities'].items():
                        c_bar = "#00ff9d" if label == "Positive" else "#ff4b4b" if label == "Negative" else "#eedd88"
                        prob_html += f'''
                        <div style="margin-bottom: 15px;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: white; font-weight: 600; margin-bottom: 5px;">
                                <span>{label}</span>
                                <span>{prob:.1%}</span>
                            </div>
                            <div style="width: 100%; background: rgba(255,255,255,0.1); border-radius: 4px; height: 6px;">
                                <div style="width: {prob*100}%; background: {c_bar}; height: 100%; border-radius: 4px; animation: bar-fill 1s ease-out forwards;"></div>
                            </div>
                        </div>
                        '''
                    
                    st.markdown(f'''
                        <div class="premium-card">
                            <p style="color: rgba(255,255,255,0.5); font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">Probability Distribution</p>
                            {prob_html}
                            <hr style="border-color: rgba(255,255,255,0.1); margin: 20px 0;">
                            <p style="color: rgba(255,255,255,0.5); font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">Why this prediction?</p>
                            <p style="font-size: 0.9rem; color: rgba(255,255,255,0.8); line-height: 1.5;">Sentiment patterns show a high tendency towards <b>{s_label.upper()}</b> momentum based on word valences.</p>
                        </div>
                    ''', unsafe_allow_html=True)
        else:
            st.info("Please enter intel text to analyze.")

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
    
    tab1, tab2, tab3 = st.tabs(["Technical Indicators", "AI Models", "Trading Concepts"])
    
    with tab1:
        if "rsi" in search_query or search_query == "":
            with st.expander("Relative Strength Index (RSI)"):
                st.markdown("**What is it?** A momentum oscillator that measures the speed and change of price movements on a scale of 0 to 100.")
                st.markdown("**How to use it:**")
                st.markdown("- <span class='highlight'>< 30 (Oversold)</span>: Potential rapid buy-bounce opportunity.", unsafe_allow_html=True)
                st.markdown("- <span style='color:#ff4b4b;font-weight:700;'>> 70 (Overbought)</span>: Potential sell warning. Asset is too hot.", unsafe_allow_html=True)
        
        if "macd" in search_query or search_query == "":
            with st.expander("Moving Average Convergence Divergence (MACD)"):
                st.markdown("**What is it?** A trend-following momentum indicator that shows the relationship between two moving averages of a stock's price.")
                st.markdown("**How to use it:**")
                st.markdown("- **Bullish Action**: MACD line crosses *above* the signal line.")
                st.markdown("- **Bearish Action**: MACD line crosses *below* the signal line.")
                
        if "sma" in search_query or "average" in search_query or search_query == "":
            with st.expander("Simple Moving Average (SMA & EMA)"):
                st.markdown("**What is it?** An arithmetic moving average calculating the average price over a specific number of days. EMA (Exponential) gives more weight to recent prices.")
                st.markdown("**Key Patterns:**")
                st.markdown("- **Golden Cross**: 50-day SMA crosses *above* the 200-day SMA (<span class='highlight'>Very Bullish</span>).", unsafe_allow_html=True)
                st.markdown("- **Death Cross**: 50-day SMA crosses *below* the 200-day SMA (<span style='color:#ff4b4b;font-weight:700;'>Very Bearish</span>).", unsafe_allow_html=True)
    
    with tab2:
        if "random" in search_query or "forest" in search_query or search_query == "":
            with st.expander("Random Forest Classifier (StockIt Base Model)"):
                st.markdown("**What is it?** An ensemble learning method that operates by constructing a multitude of decision trees at training time.")
                st.markdown("**Why we use it in Finance:** To map highly complex, non-linear relationships between diverse technical indicators without overfitting to noise like linear models do.")
                
        if "nlp" in search_query or "sentiment" in search_query or "finbert" in search_query or search_query == "":
            with st.expander("FinBERT Transformer Neural Net"):
                st.markdown("**What is it?** A massive pre-trained NLP model built by Google specifically tailored to parse sentiment in financial text.")
                st.markdown("**Why we use it over traditional sentiment:** Standard models fail to understand that 'earnings drop' is terrible but 'inflation drop' is excellent. FinBERT understands Wall Street jargon.")
                
    with tab3:
        if "confidence" in search_query or search_query == "":
            with st.expander("Algorithm Confidence vs Probability"):
                st.markdown("**Concept:** A model throwing a 51% confidence is guessing. A model throwing 95% is statistically certain.")
                st.markdown("In our system, the confidence interval dictates the intensity of the signal. We only issue structural BUY flags when the underlying decision forest reaches a super-majority consensus regarding a future baseline price jump.")
        
        if "alpha" in search_query or search_query == "":
            with st.expander("Generating Alpha"):
                st.markdown("**Concept:** Alpha represents the active return on an investment compared to a market index or benchmark.")
                st.markdown("This dashboard aims to isolate edge-case data points (Alpha) by compounding multi-modal telemetry (technical numbers + human sentiment semantics) in real-time.")

    pages = ["Home", "Analyzer", "Market", "Sentiment", "Education"]
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"

    # Global Footer logic
    if st.session_state.current_page != "Home":
        footer_section()

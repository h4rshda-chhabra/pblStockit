import streamlit as st

def apply_custom_style():
    """Applies a premium dark finance theme with animations and glassmorphism."""
    st.markdown("""
        <style>
        /* Base Theme */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');

        .main {
            background-color: #06080a;
            color: #ffffff;
            font-family: 'Inter', sans-serif;
            background-image: 
                linear-gradient(rgba(0, 212, 255, 0.08) 1.5px, transparent 1.5px),
                linear-gradient(90deg, rgba(0, 212, 255, 0.08) 1.5px, transparent 1.5px);
            background-size: 60px 60px;
        }
        
        /* Hide default Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stSidebar"] {display: none;}
        
        /* Navbar Styling */
        .nav-container {
            position: fixed;
            top: 40px; /* Below ticker */
            left: 0;
            right: 0;
            height: 70px;
            background: rgba(8, 10, 14, 0.98);
            backdrop-filter: blur(25px);
            border-bottom: 1px solid rgba(0, 212, 255, 0.15);
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 5%;
            z-index: 9999;
        }
        .nav-logo {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 1.8rem;
            font-weight: 800;
            letter-spacing: -1px;
            color: #ffffff;
            text-decoration: none;
        }
        .nav-logo span {
            color: #00d4ff;
        }
        .nav-links {
            display: flex;
            gap: 30px;
        }
        .nav-link {
            color: rgba(255, 255, 255, 0.7);
            text-decoration: none;
            font-weight: 600;
            font-size: 0.9rem;
            transition: 0.3s;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            padding: 5px 0;
        }
        .nav-link:hover, .nav-link.active {
            color: #00d4ff;
            border-bottom-color: #00d4ff;
        }
        
        /* Marquee Ticker */
        .ticker-wrap {
            width: 100%;
            height: 40px;
            background-color: #000000;
            overflow: hidden;
            position: fixed;
            top: 0; /* Extreme Top */
            left: 0;
            z-index: 10000;
            border-bottom: 1px solid rgba(0, 212, 255, 0.2);
            display: flex;
            align-items: center;
        }
        .ticker {
            display: flex;
            white-space: nowrap;
            animation: ticker-move 40s linear infinite;
        }
        @keyframes ticker-move {
            0% { transform: translateX(0); }
            100% { transform: translateX(-50%); }
        }
        .ticker-item {
            display: inline-block;
            padding: 0 30px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            color: #ffffff;
        }
        .ticker-item span {
            color: #00ff9d;
            font-weight: 700;
            margin-left: 8px;
        }
        .ticker-item span.down {
            color: #ff4b4b;
        }
        
        /* Layout Buffer */
        .layout-buffer {
            height: 120px;
        }
        
        /* Glassmorphism Cards */
        .glass-card {
            background: rgba(26, 32, 44, 0.95);
            backdrop-filter: blur(25px);
            border: 1px solid rgba(255, 255, 255, 0.25);
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 24px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.6);
        }
        .glass-card:hover {
            border-color: #00d4ff;
            background: rgba(35, 45, 60, 0.98);
            box-shadow: 0 0 40px rgba(0, 212, 255, 0.2);
        }
        
        /* Highlighted Card Style */
        .glass-card.highlight {
            border-color: #00d4ff !important;
            box-shadow: 0 0 30px rgba(0, 212, 255, 0.25) !important;
        }
        
        /* Ghost Buttons from Image */
        .stButton button {
            background: transparent !important;
            border: 1px solid #00d4ff !important;
            color: #00d4ff !important;
            border-radius: 4px !important;
            padding: 12px 24px !important;
            font-weight: 700 !important;
            letter-spacing: 1px !important;
            text-transform: uppercase !important;
            transition: all 0.3s ease !important;
        }
        .stButton button:hover {
            background: rgba(0, 212, 255, 0.1) !important;
            box-shadow: 0 0 15px rgba(0, 212, 255, 0.3) !important;
        }
        /* Specific coloring for secondary button */
        div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
            border-color: #00ff9d !important;
            color: #00ff9d !important;
        }
        div[data-testid="stHorizontalBlock"] > div:nth-child(2) button:hover {
            background: rgba(0, 255, 157, 0.1) !important;
            box-shadow: 0 0 15px rgba(0, 255, 157, 0.3) !important;
        }
        
        /* Horizontal Navbar via Radio Group Hack */
        div[data-testid="stRadio"] {
            display: flex;
            justify-content: center;
            width: 100% !important;
        }
        div[data-testid="stRadio"] > div[role="radiogroup"] {
            flex-direction: row !important;
            justify-content: flex-end !important;
            gap: 20px !important;
            background: transparent !important;
            padding: 0 !important;
            border: none !important;
            width: 100% !important;
        }
        /* Hide EVERYTHING inside the label except our target text */
        div[data-testid="stRadio"] label > div:first-child {
            display: none !important;
        }
        div[data-testid="stRadio"] label {
            background: transparent !important;
            margin: 0 !important;
            padding: 10px 20px !important;
            cursor: pointer !important;
            border-bottom: 2px solid transparent;
            transition: all 0.3s ease;
        }
        div[data-testid="stRadio"] label p {
            font-weight: 500 !important;
            font-size: 1.1rem !important;
            color: rgba(255,255,255,0.7) !important;
            margin: 0 !important;
            transition: color 0.3s ease;
        }
        /* Active State */
        div[data-testid="stRadio"] label[data-checked="true"] {
            border-bottom: none !important;
        }
        div[data-testid="stRadio"] label[data-checked="true"] p {
            color: #00d4ff !important;
        }
        div[data-testid="stRadio"] label:hover p {
            color: #ffffff !important;
        }
        
        /* Plotly Fixes */
        .js-plotly-plot {
            background: transparent !important;
        }
        
        /* Grid Alignment */
        .centered-layout {
            max-width: 1200px;
            margin: 0 auto;
            text-align: center;
        }

        /* Typography spacing */
        h1, h2, h3 {
            margin-bottom: 1.5rem !important;
            line-height: 1.2 !important;
            text-shadow: 0 0 10px rgba(0, 212, 255, 0.1);
        }
        p {
            line-height: 1.6 !important;
            color: #ffffff !important;
            font-weight: 500 !important;
        }
        </style>
    """, unsafe_allow_html=True)

def render_navbar():
    """Renders the combined ticker + navbar header structure."""
    stocks = [
        ("RELIANCE", "2,942.50", "+1.2%"),
        ("TCS", "3,950.00", "-0.5%"),
        ("INFY", "1,640.20", "+2.1%"),
        ("HDFCBANK", "1,428.00", "+0.8%"),
        ("NIFTY 50", "22,123.45", "+0.6%"),
        ("SENSEX", "72,831.10", "+0.5%")
    ]
    
    ticker_items_html = "".join([
        f'<div style="display:inline-block; padding:0 30px; font-family:\'JetBrains Mono\'; font-size: 0.8rem; font-weight:700;">'
        f'<span style="color:#00d4ff;">{name}</span> '
        f'<span style="color:white;">{price}</span> '
        f'<span style="color:{("#00ff9d" if "+" in change else "#ff4b4b")};">({change})</span>'
        f'</div>'
        for name, price, change in stocks + stocks
    ])

    st.markdown(f'''
        <div style="position:fixed; top:0; left:0; width:100%; z-index:10000; background:#000;">
            <div style="height:32px; overflow:hidden; display:flex; align-items:center; background:#0066ff; border-bottom:1px solid rgba(255,255,255,0.2);">
                <div style="white-space:nowrap; animation:ticker-scroll 40s linear infinite;">
                    {ticker_items_html * 3}
                </div>
            </div>
            <div style="height:70px; display:flex; align-items:center; padding:0 5%; background:rgba(8, 10, 14, 0.98); backdrop-filter:blur(25px); border-bottom:1px solid rgba(255,255,255,0.1);">
                <div style="display:flex; align-items:center; font-size:1.8rem; font-weight:800; color:white; letter-spacing:-1.2px;">
                    Stock<span>it</span>
                </div>
            </div>
        </div>
        <style>
            @keyframes ticker-scroll {{
                0% {{ transform: translateX(0); }}
                100% {{ transform: translateX(-33.33%); }}
            }}
            .layout-buffer {{ height: 85px; }}
            
            /* Extreme Right Nav Group Hack */
            div[data-testid="stRadio"] {{
                position: fixed !important;
                top: 48px !important; /* Center in 70px bar after 32px ticker */
                right: 5% !important;
                z-index: 10001 !important;
                width: auto !important;
                background: transparent !important;
            }}
            div[data-testid="stRadio"] > div[role="radiogroup"] {{
                justify-content: flex-end !important;
                gap: 25px !important;
            }}
        </style>
    ''', unsafe_allow_html=True)

    pages = ["Home", "Analyzer", "Market", "Sentiment"]
    if "current_page_idx" not in st.session_state:
        st.session_state.current_page_idx = 0

    _, c_nav = st.columns([1, 2])
    with c_nav:
        selected = st.radio("Navigation", options=pages, index=st.session_state.current_page_idx, horizontal=True, key="nav_radio_widget", label_visibility="collapsed")
    
    if selected != pages[st.session_state.current_page_idx]:
        st.session_state.current_page_idx = pages.index(selected)
        st.rerun()
    
    st.markdown('<div class="layout-buffer"></div>', unsafe_allow_html=True)
    return selected

def render_ticker():
    # Integrated into render_navbar
    pass

def header_section(title, subtitle):
    """Renders a consistent centered header for all pages."""
    st.markdown(f"""
        <div class="centered-layout">
            <h1 style="font-size: 3.5rem; font-weight: 800; background: linear-gradient(120deg, #ffffff 0%, #00d4ff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{title}</h1>
            <p style="font-size: 1.25rem; font-weight: 400; color: rgba(255,255,255,0.6); margin-bottom: 3rem;">{subtitle}</p>
        </div>
    """, unsafe_allow_html=True)

def footer_section():
    """Renders the common footer."""
    st.markdown("""
        <div style="text-align: center; padding: 60px 0; color: rgba(255, 255, 255, 0.3); font-size: 0.85rem; border-top: 1px solid rgba(255, 255, 255, 0.05); margin-top: 100px;">
            Advanced Institutional Grade Stock Analytics Platform v2.5<br>
            Powered by Sentiment AI and Neural Forecasting Engines<br>
            © 2026 StockIt Capital Group
        </div>
    """, unsafe_allow_html=True)

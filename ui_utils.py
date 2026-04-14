import streamlit as st

def apply_custom_style():
    """Applies a premium dark finance theme with animations and glassmorphism."""
    st.markdown("""
        <style>
        /* Base Theme */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');

        .main {
            background-color: #0B0B0E;
            color: #ffffff;
            font-family: 'Inter', sans-serif;
            background-image: radial-gradient(#1A1A1D 1.8px, transparent 1.8px);
            background-size: 30px 30px;
        }
        
        .main .block-container {
            padding-top: 1.5rem !important;
            margin-top: 2vh !important;
        }
        
        /* Hide default Streamlit elements - Reduced aggressiveness for visibility */
        #MainMenu {visibility: visible; opacity: 0.1;}
        footer {visibility: visible; opacity: 0.1;}
        header {visibility: visible; opacity: 0.1;}
        [data-testid="stSidebar"] {display: block; opacity: 0.1;}
        
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
            height: 40px;
        }
        
        /* Premium Design - Precision 24px Radius */
        .glass-card, .premium-card {
            background: #141417;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 24px;
            padding: 2rem;
            margin-bottom: 2rem;
            transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
            box-shadow: 0 20px 60px -15px rgba(0,0,0,0.8);
        }
        .glass-card:hover, .premium-card:hover {
            border-color: rgba(0, 217, 255, 0.3);
            transform: translateY(-4px);
            box-shadow: 0 30px 80px -20px rgba(0,0,0,0.9);
        }
        
        /* Inference Step Styling (Vertical Flow) */
        .step-container {
            border-left: 2px solid rgba(0, 212, 255, 0.2);
            margin-left: 20px;
            padding-left: 30px;
            position: relative;
        }
        .step-node {
            position: absolute;
            left: -11px;
            top: 0;
            width: 20px;
            height: 20px;
            background: #00d4ff;
            border-radius: 50%;
            box-shadow: 0 0 10px #00d4ff;
        }
        
        /* Institutional Action Components */
        div.stButton > button[data-testid="baseButton-primary"] {
            height: 65px !important;
            font-size: 1.1rem !important;
            font-weight: 700 !important;
            background: linear-gradient(135deg, #00D9FF 0%, #0066ff 100%) !important;
            border: none !important;
            color: #ffffff !important;
            border-radius: 16px !important;
            box-shadow: 0 10px 30px rgba(0, 217, 255, 0.2), inset 0 1px 1px rgba(255,255,255,0.4) !important;
            transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1) !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        div.stButton > button[data-testid="baseButton-primary"]:hover {
            transform: translateY(-3px) scale(1.02) !important;
            box-shadow: 0 15px 40px rgba(0, 217, 255, 0.4), inset 0 1px 1px rgba(255,255,255,0.5) !important;
        }

        div.stButton > button[data-testid="baseButton-secondary"] {
            height: 65px !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            background: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(0, 217, 255, 0.3) !important;
            color: #00D9FF !important;
            border-radius: 16px !important;
            transition: all 0.3s ease !important;
            text-transform: uppercase;
        }
        div.stButton > button[data-testid="baseButton-secondary"]:hover {
            background: rgba(0, 217, 255, 0.08) !important;
            border-color: #00D9FF !important;
            transform: translateY(-2px) !important;
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
            gap: 15px !important;
            background: transparent !important;
            padding: 0 !important;
            border: none !important;
        }
        div[data-testid="stRadio"] label > div:first-child {
            display: none !important;
        }
        div[data-testid="stRadio"] label {
            background: transparent !important;
            margin: 0 !important;
            padding: 8px 15px !important;
            cursor: pointer !important;
            border-radius: 8px !important;
            transition: all 0.3s ease;
        }
        div[data-testid="stRadio"] label:hover {
            background: rgba(255, 255, 255, 0.05) !important;
        }
        div[data-testid="stRadio"] label p {
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            color: rgba(255,255,255,0.6) !important;
            margin: 0 !important;
        }
        /* Active State */
        div[data-testid="stRadio"] label[data-checked="true"] {
            background: rgba(0, 212, 255, 0.1) !important;
        }
        div[data-testid="stRadio"] label[data-checked="true"] p {
            color: #00d4ff !important;
        }
        
        /* Unified Selectbox & Text Input Base Wrappers */
        div[data-testid="stSelectbox"] div[data-baseweb="select"],
        div[data-testid="stTextInput"] div[data-baseweb="input"] {
            background-color: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            height: 65px !important;
            padding: 0 20px !important;
            display: flex !important;
            align-items: center !important;
        }

        /* Focus & Hover States */
        div[data-testid="stSelectbox"] div[data-baseweb="select"]:hover,
        div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
            border-color: #00d4ff !important;
            box-shadow: 0 0 15px rgba(0, 212, 255, 0.25) !important;
            background-color: rgba(255, 255, 255, 0.05) !important;
        }

        /* Inner Text Settings */
        div[data-testid="stSelectbox"] div[data-baseweb="select"] span {
            color: #00d4ff !important;
            font-weight: 700 !important;
            font-size: 1.15rem !important;
        }
        
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea {
            background-color: transparent !important;
            border: none !important;
            color: #00d4ff !important;
            caret-color: #00d4ff !important;
            font-size: 1.15rem !important;
            font-weight: 700 !important;
            padding: 0 !important;
            height: auto !important;
            box-shadow: none !important;
        }
        
        div[data-testid="stTextInput"] input:focus {
            box-shadow: none !important;
            border: none !important;
            outline: none !important;
        }
        
        /* Change placeholder color explicitly */
        div[data-testid="stTextInput"] input::placeholder {
            color: rgba(255,255,255,0.7) !important;
            font-size: 1.15rem !important;
        }

        /* Adjust labels natively linked to inputs so they hover correctly */
        .st-emotion-cache-1z01u59 label, .st-emotion-cache-16s294j p {
            font-size: 1.05rem !important;
            color: rgba(255,255,255,0.8) !important;
            margin-bottom: 8px !important;
            padding-bottom: 0 !important;
        }
        
        /* Specifically format the checkbox wrapper to align vertically */
        .stCheckbox {
            height: 65px !important;
            display: flex !important;
            align-items: center !important;
            margin-top: 32px !important; /* Force down to match other inputs baseline */
        }
        
        /* Plotly Fixes */
        .js-plotly-plot {
            background: transparent !important;
            border-radius: 15px;
            overflow: hidden;
        }
        
        /* Grid Alignment */
        .centered-layout {
            max-width: 1200px;
            margin: 0 auto;
        }

        /* Education Card Styles */
        .edu-card {
            background: rgba(255, 255, 255, 0.02);
            border-left: 4px solid #00d4ff;
            padding: 1.5rem;
            margin-bottom: 2rem;
            border-radius: 0 15px 15px 0;
        }

        /* Typography spacing */
        h1, h2, h3 {
            margin-bottom: 1.2rem !important;
            letter-spacing: -0.5px !important;
        }
        p {
            line-height: 1.7 !important;
            color: rgba(255, 255, 255, 0.7) !important;
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

    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"

    if st.session_state.current_page != "Home":
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
                .layout-buffer {{ height: 40px; }}
                
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


    pages = ["Home", "Analyzer", "Market", "Sentiment", "Education"]
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"

    # Minimal logic to handle page state without the radio navbar
    st.markdown('<div class="layout-buffer"></div>', unsafe_allow_html=True)
    
    # We add a small "Back to Home" button if we are not on Home
    if st.session_state.current_page != "Home":
        st.markdown("""
            <style>
                .home-btn-container {
                    position: fixed;
                    top: 48px;
                    right: 5%;
                    z-index: 10001;
                }
            </style>
        """, unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="home-btn-container">', unsafe_allow_html=True)
            if st.button("⌂ Home", key="back_to_home"):
                st.session_state.current_page = "Home"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    return st.session_state.current_page


def render_ticker():
    # Integrated into render_navbar
    pass

def header_section(title, subtitle):
    """Renders a consistent centered header for all pages."""
    st.markdown(f"""
        <div style="text-align: center; padding: 60px 0 40px 0; max-width: 900px; margin: 0 auto;">
            <h1 style="font-size: 4.5rem; font-weight: 900; background: linear-gradient(135deg, #ffffff 30%, #00D9FF 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -3px; line-height: 1; margin-bottom: 20px;">{title}</h1>
            <p style="font-size: 1.35rem; font-weight: 500; color: rgba(255,255,255,0.5); letter-spacing: 0.5px;">{subtitle}</p>
            <div style="width: 50px; height: 4px; background: #00D9FF; margin: 30px auto 0 auto; border-radius: 2px;"></div>
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

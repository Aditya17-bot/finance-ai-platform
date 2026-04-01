import streamlit as st
import requests
import json
import os
import time
from datetime import datetime
from requests.exceptions import RequestException

# =====================================================
# OPTIONAL LLM IMPORT
# =====================================================
try:
    from langchain_ollama import ChatOllama
    LLM_AVAILABLE = True
except Exception:
    try:
        from langchain_community.chat_models import ChatOllama
        LLM_AVAILABLE = True
    except Exception:
        LLM_AVAILABLE = False

# =====================================================
# CONFIG
# =====================================================
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:7b")
API_TIMEOUT = 30

if LLM_AVAILABLE:
    try:
        llm = ChatOllama(model=LLM_MODEL, temperature=0)
    except Exception:
        LLM_AVAILABLE = False

# =====================================================
# USER PROFILES
# =====================================================
USERS = {
    "Rahul": {
        "avatar": "👨‍💼",
        "archetype": "Balanced Professional",
        "credit_limit": 100000,
        "transactions": [
            {"amount": 1200, "category": "Food", "hour": 20, "location_change": 0, "merchant_type": 1, "txn_velocity": 1},
            {"amount": 5000, "category": "Luxury", "hour": 18, "location_change": 0, "merchant_type": 2, "txn_velocity": 2},
            {"amount": 15000, "category": "Rent", "hour": 10, "location_change": 0, "merchant_type": 0, "txn_velocity": 1},
            {"amount": 3000, "category": "Investment", "hour": 9, "location_change": 0, "merchant_type": 3, "txn_velocity": 1},
        ]
    },
    "Arjun": {
        "avatar": "🧔",
        "archetype": "Luxury Overspender",
        "credit_limit": 150000,
        "transactions": [
            {"amount": 8000, "category": "Luxury", "hour": 19, "location_change": 0, "merchant_type": 2, "txn_velocity": 3},
            {"amount": 7000, "category": "Luxury", "hour": 21, "location_change": 0, "merchant_type": 2, "txn_velocity": 4},
            {"amount": 12000, "category": "Luxury", "hour": 23, "location_change": 1, "merchant_type": 5, "txn_velocity": 5},
        ]
    },
    "Priya": {
        "avatar": "👩‍💻",
        "archetype": "Smart Investor",
        "credit_limit": 200000,
        "transactions": [
            {"amount": 10000, "category": "Investment", "hour": 12, "location_change": 0, "merchant_type": 3, "txn_velocity": 1},
            {"amount": 3000, "category": "Food", "hour": 20, "location_change": 0, "merchant_type": 1, "txn_velocity": 1},
            {"amount": 25000, "category": "Investment", "hour": 11, "location_change": 0, "merchant_type": 3, "txn_velocity": 1},
            {"amount": 8000, "category": "Rent", "hour": 10, "location_change": 0, "merchant_type": 0, "txn_velocity": 1},
        ]
    },
    "Neha": {
        "avatar": "👩‍🎨",
        "archetype": "High-Risk Spender",
        "credit_limit": 80000,
        "transactions": [
            {"amount": 12000, "category": "Luxury", "hour": 22, "location_change": 0, "merchant_type": 2, "txn_velocity": 2},
            {"amount": 10000, "category": "Luxury", "hour": 23, "location_change": 0, "merchant_type": 2, "txn_velocity": 3},
            {"amount": 18000, "category": "Misc", "hour": 1, "location_change": 1, "merchant_type": 7, "txn_velocity": 6},
        ]
    },
    "Karan": {
        "avatar": "🕵️",
        "archetype": "Suspicious Activity",
        "credit_limit": 50000,
        "transactions": [
            {"amount": 1500, "category": "Food", "hour": 19, "location_change": 0, "merchant_type": 1, "txn_velocity": 1},
            {"amount": 45000, "category": "Luxury", "hour": 2, "location_change": 1, "merchant_type": 7, "txn_velocity": 8},
        ]
    }
}

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="FinanceAI Terminal",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# GLOBAL STYLES — Dark Terminal Theme
# =====================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --bg-deep:     #080c14;
    --bg-panel:    #0d1421;
    --bg-card:     #111827;
    --bg-hover:    #1a2436;
    --amber:       #f59e0b;
    --amber-dim:   #92400e;
    --amber-glow:  rgba(245,158,11,0.15);
    --green:       #10b981;
    --green-dim:   #064e3b;
    --red:         #ef4444;
    --red-dim:     #7f1d1d;
    --blue:        #3b82f6;
    --blue-dim:    #1e3a5f;
    --text-1:      #f1f5f9;
    --text-2:      #94a3b8;
    --text-3:      #475569;
    --border:      #1e2d42;
    --border-lit:  #2d4a6e;
}

/* ── BASE ── */
html, body, .stApp {
    background: var(--bg-deep) !important;
    color: var(--text-1) !important;
    font-family: 'Syne', sans-serif !important;
}

/* ── HIDE STREAMLIT DEFAULT CHROME ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── TOP NAV BAR ── */
.top-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 2rem;
    background: var(--bg-panel);
    border-bottom: 1px solid var(--border);
    margin: -1rem -1rem 2rem -1rem;
}
.top-bar-brand {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--amber);
    letter-spacing: 0.05em;
}
.top-bar-status {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: var(--green);
    background: var(--green-dim);
    padding: 0.25rem 0.75rem;
    border-radius: 4px;
    border: 1px solid var(--green);
}
.top-bar-time {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: var(--text-2);
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: var(--bg-panel) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label {
    color: var(--text-2) !important;
    font-size: 0.75rem !important;
    font-family: 'JetBrains Mono', monospace !important;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.sidebar-logo {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--amber);
    padding: 1rem 0 0.5rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
}
.sidebar-section {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: var(--text-3);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin: 1.5rem 0 0.5rem 0;
}

/* ── CARDS ── */
.fin-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
}
.fin-card:hover {
    border-color: var(--border-lit);
}
.fin-card-amber {
    border-left: 3px solid var(--amber);
    background: linear-gradient(90deg, rgba(245,158,11,0.05) 0%, var(--bg-card) 100%);
}
.fin-card-green {
    border-left: 3px solid var(--green);
    background: linear-gradient(90deg, rgba(16,185,129,0.05) 0%, var(--bg-card) 100%);
}
.fin-card-red {
    border-left: 3px solid var(--red);
    background: linear-gradient(90deg, rgba(239,68,68,0.05) 0%, var(--bg-card) 100%);
}
.fin-card-blue {
    border-left: 3px solid var(--blue);
    background: linear-gradient(90deg, rgba(59,130,246,0.05) 0%, var(--bg-card) 100%);
}

/* ── METRIC TILES ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.metric-tile {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    text-align: center;
}
.metric-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: var(--text-3);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--amber);
    line-height: 1;
}
.metric-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: var(--text-2);
    margin-top: 0.35rem;
}

/* ── SCORE GAUGE ── */
.score-display {
    text-align: center;
    padding: 2rem;
}
.score-number {
    font-family: 'JetBrains Mono', monospace;
    font-size: 4rem;
    font-weight: 700;
    line-height: 1;
}
.score-band {
    font-family: 'Syne', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 0.5rem;
}

/* ── STATUS BADGES ── */
.badge {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.3rem 0.8rem;
    border-radius: 4px;
    letter-spacing: 0.05em;
}
.badge-safe   { background: var(--green-dim); color: var(--green); border: 1px solid var(--green); }
.badge-fraud  { background: var(--red-dim);   color: var(--red);   border: 1px solid var(--red); }
.badge-warn   { background: var(--amber-dim); color: var(--amber); border: 1px solid var(--amber); }
.badge-info   { background: var(--blue-dim);  color: var(--blue);  border: 1px solid var(--blue); }

/* ── SECTION HEADERS ── */
.section-header {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-3);
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text-1);
    margin-bottom: 0.25rem;
}

/* ── USER CARD ── */
.user-card {
    background: var(--bg-card);
    border: 1px solid var(--border-lit);
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.user-avatar { font-size: 2.5rem; }
.user-name {
    font-family: 'Syne', sans-serif;
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--text-1);
}
.user-archetype {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: var(--amber);
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* ── TRANSACTION TABLE ── */
.txn-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
}
.txn-table th {
    text-align: left;
    color: var(--text-3);
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.5rem 0.75rem;
    border-bottom: 1px solid var(--border);
}
.txn-table td {
    padding: 0.6rem 0.75rem;
    color: var(--text-2);
    border-bottom: 1px solid var(--border);
}
.txn-table tr:last-child td { border-bottom: none; }
.txn-table tr:hover td { background: var(--bg-hover); }
.txn-amount { color: var(--amber) !important; font-weight: 600; }

/* ── CATEGORY BAR ── */
.cat-bar-wrap { margin: 0.4rem 0; }
.cat-label {
    display: flex;
    justify-content: space-between;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: var(--text-2);
    margin-bottom: 0.2rem;
}
.cat-bar-bg {
    background: var(--bg-hover);
    border-radius: 2px;
    height: 6px;
    width: 100%;
}
.cat-bar-fill {
    height: 6px;
    border-radius: 2px;
    background: var(--amber);
    transition: width 0.8s ease;
}

/* ── INSIGHT CARDS ── */
.insight-item {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.85rem 1rem;
    border-radius: 6px;
    margin-bottom: 0.6rem;
    font-family: 'Syne', sans-serif;
    font-size: 0.88rem;
    line-height: 1.5;
    border: 1px solid transparent;
}
.insight-ok     { background: rgba(16,185,129,0.08);  border-color: rgba(16,185,129,0.2);  color: #6ee7b7; }
.insight-warn   { background: rgba(245,158,11,0.08);  border-color: rgba(245,158,11,0.2);  color: #fcd34d; }
.insight-danger { background: rgba(239,68,68,0.08);   border-color: rgba(239,68,68,0.2);   color: #fca5a5; }
.insight-info   { background: rgba(59,130,246,0.08);  border-color: rgba(59,130,246,0.2);  color: #93c5fd; }

/* ── BUTTONS ── */
.stButton > button {
    background: var(--amber) !important;
    color: #000 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.65rem 1.5rem !important;
    text-transform: uppercase !important;
    transition: all 0.2s !important;
    width: 100% !important;
}
.stFormSubmitButton > button {
    background: var(--amber) !important;
    color: #000 !important;
}
.stFormSubmitButton > button:disabled {
    color: rgba(0, 0, 0, 0.65) !important;
}
.stButton > button:hover {
    background: #fbbf24 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(245,158,11,0.3) !important;
}
.stFormSubmitButton > button:hover {
    background: #fbbf24 !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── INPUTS ── */
.stSelectbox > div > div,
.stNumberInput > div > div > input,
.stSlider > div,
.stTextInput > div > div > input {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-1) !important;
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
}
.stSelectbox label, .stNumberInput label,
.stSlider label, .stTextInput label {
    color: var(--text-2) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}

/* ── SPINNER ── */
.stSpinner > div {
    border-top-color: var(--amber) !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: var(--border-lit); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-3); }

/* ── DIVIDER ── */
hr { border-color: var(--border) !important; }

/* ── CHAT BUBBLES ── */
.chat-user {
    background: var(--bg-hover);
    border: 1px solid var(--border-lit);
    border-radius: 8px 8px 2px 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.75rem;
    font-family: 'Syne', sans-serif;
    font-size: 0.9rem;
    color: var(--text-1);
    max-width: 80%;
    margin-left: auto;
}
.chat-ai {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px 8px 8px 2px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.75rem;
    font-family: 'Syne', sans-serif;
    font-size: 0.9rem;
    color: var(--text-2);
    max-width: 85%;
    border-left: 3px solid var(--amber);
}
.chat-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: var(--text-3);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# API HELPERS
# =====================================================
def post_json(path: str, payload: dict):
    try:
        res = requests.post(f"{API_BASE_URL}{path}", json=payload, timeout=API_TIMEOUT)
        res.raise_for_status()
        return res.json(), None
    except RequestException as e:
        return None, str(e)

def check_api_health():
    try:
        r = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

# =====================================================
# RENDER HELPERS
# =====================================================
def score_color(score: int) -> str:
    if score >= 750: return "#10b981"
    elif score >= 700: return "#84cc16"
    elif score >= 650: return "#eab308"
    elif score >= 600: return "#f97316"
    return "#ef4444"

def insight_class(msg: str) -> str:
    if "🚨" in msg or "FRAUD" in msg or "critically" in msg or "immediate" in msg.lower():
        return "insight-danger"
    elif "⚠️" in msg or "⚡" in msg or "rising" in msg or "high" in msg.lower():
        return "insight-warn"
    elif "✅" in msg or "🟢" in msg or "Excellent" in msg:
        return "insight-ok"
    return "insight-info"

def render_category_bars(breakdown: dict):
    colors = {
        "Food": "#f59e0b", "Rent": "#3b82f6",
        "Luxury": "#a855f7", "Investment": "#10b981", "Misc": "#6b7280"
    }
    html = ""
    for cat, ratio in breakdown.items():
        pct = round(ratio * 100, 1)
        color = colors.get(cat, "#f59e0b")
        html += f"""
        <div class="cat-bar-wrap">
            <div class="cat-label"><span>{cat}</span><span>{pct}%</span></div>
            <div class="cat-bar-bg">
                <div class="cat-bar-fill" style="width:{pct}%; background:{color};"></div>
            </div>
        </div>"""
    st.markdown(html, unsafe_allow_html=True)

def render_txn_table(transactions: list):
    rows = ""
    for i, txn in enumerate(transactions):
        flag = "🔴" if (txn.get("txn_velocity", 0) >= 5 or txn.get("location_change") == 1) else "🟢"
        rows += f"""
        <tr>
            <td>#{i+1}</td>
            <td class="txn-amount">₹{txn['amount']:,.0f}</td>
            <td>{txn['category']}</td>
            <td>{txn['hour']:02d}:00</td>
            <td>{"Yes" if txn['location_change'] else "No"}</td>
            <td>{txn['txn_velocity']}/hr</td>
            <td>{flag}</td>
        </tr>"""
    st.markdown(f"""
    <table class="txn-table">
        <thead><tr>
            <th>#</th><th>Amount</th><th>Category</th>
            <th>Hour</th><th>Loc. Change</th><th>Velocity</th><th>Risk</th>
        </tr></thead>
        <tbody>{rows}</tbody>
    </table>""", unsafe_allow_html=True)

# =====================================================
# TOP BAR
# =====================================================
health = check_api_health()
api_ok = health and health.get("healthy", False)

st.markdown(f"""
<div class="top-bar">
    <div class="top-bar-brand">◈ FINANCE_AI TERMINAL v3.0</div>
    <div class="top-bar-status">{'● API ONLINE' if api_ok else '● API OFFLINE'}</div>
    <div class="top-bar-time">{datetime.now().strftime('%d %b %Y  %H:%M:%S')}</div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:
    st.markdown('<div class="sidebar-logo">◈ FINANCE_AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section">Navigation</div>', unsafe_allow_html=True)

    mode = st.selectbox(
        "Mode",
        ["🤖 Agent Analysis", "💬 AI Chat Assistant", "🔍 Fraud Inspector", "📊 Spending Classifier", "💳 Credit Scorer"],
        label_visibility="collapsed"
    )

    st.markdown('<div class="sidebar-section">System</div>', unsafe_allow_html=True)
    if health:
        models_loaded = health.get("models", {})
        for model_name, loaded in models_loaded.items():
            icon = "●" if loaded else "○"
            color = "#10b981" if loaded else "#ef4444"
            st.markdown(
                f'<span style="font-family:JetBrains Mono;font-size:0.72rem;color:{color};">'
                f'{icon} {model_name.upper()} MODEL</span>',
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            '<span style="font-family:JetBrains Mono;font-size:0.72rem;color:#ef4444;">'
            '○ BACKEND OFFLINE</span>',
            unsafe_allow_html=True
        )

    st.markdown('<div class="sidebar-section">Info</div>', unsafe_allow_html=True)
    st.markdown(
        '<span style="font-family:JetBrains Mono;font-size:0.7rem;color:#475569;">'
        f'Endpoint: {API_BASE_URL}</span>',
        unsafe_allow_html=True
    )


# ======================================================
# MODE: AGENT ANALYSIS
# ======================================================
if "🤖 Agent Analysis" in mode:
    st.markdown('<div class="section-header">Agentic AI — Multi-Model Orchestration</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">User Financial Profile</div>', unsafe_allow_html=True)
    st.markdown("Select a user to run the full AI pipeline — spending classification, credit scoring, and fraud detection.")

    col_sel, col_info = st.columns([1, 2])
    with col_sel:
        selected_user = st.selectbox("User Profile", list(USERS.keys()), label_visibility="visible")

    user_data = USERS[selected_user]

    with col_info:
        st.markdown(f"""
        <div class="user-card">
            <div class="user-avatar">{user_data['avatar']}</div>
            <div>
                <div class="user-name">{selected_user}</div>
                <div class="user-archetype">{user_data['archetype']}</div>
                <div style="font-family:JetBrains Mono;font-size:0.7rem;color:#475569;margin-top:0.25rem;">
                    Credit Limit: ₹{user_data['credit_limit']:,.0f} &nbsp;|&nbsp; {len(user_data['transactions'])} Transactions
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Transaction preview
    st.markdown('<div class="section-header" style="margin-top:1rem;">Transaction History</div>', unsafe_allow_html=True)
    render_txn_table(user_data["transactions"])

    st.markdown("<br>", unsafe_allow_html=True)
    run_col, _ = st.columns([1, 2])
    with run_col:
        run_agent = st.button("▶ RUN AGENT ANALYSIS")

    if run_agent:
        if not api_ok:
            st.error("⚠️ Backend API is offline. Start the FastAPI server and reload.")
        else:
            payload = {
                "credit_limit": user_data["credit_limit"],
                "transactions": user_data["transactions"]
            }
            with st.spinner("Running AI pipeline..."):
                result, err = post_json("/agent/analyze-user", payload)

            if err:
                st.error(f"API Error: {err}")
            elif result:
                st.markdown("---")
                st.markdown('<div class="section-header">Analysis Results</div>', unsafe_allow_html=True)

                # ── Metric tiles ──
                score = result.get("credit_score", 0)
                sc = score_color(score)
                fraud_flag = result.get("fraud_status", "")
                fraud_is = "🚨" in fraud_flag
                utilization = result.get("credit_utilization", 0)

                st.markdown(f"""
                <div class="metric-grid">
                    <div class="metric-tile">
                        <div class="metric-label">Credit Score</div>
                        <div class="metric-value" style="color:{sc};">{score}</div>
                        <div class="metric-sub">{result.get('risk_band','—')}</div>
                    </div>
                    <div class="metric-tile">
                        <div class="metric-label">Spending Type</div>
                        <div class="metric-value" style="font-size:1.2rem;padding-top:0.4rem;color:#f1f5f9;">{result.get('spending_type','—')}</div>
                        <div class="metric-sub">Dominant: {result.get('dominant_category','—')}</div>
                    </div>
                    <div class="metric-tile">
                        <div class="metric-label">Credit Utilization</div>
                        <div class="metric-value" style="color:{'#ef4444' if utilization > 0.7 else '#f59e0b'};">{utilization*100:.1f}%</div>
                        <div class="metric-sub">of ₹{user_data['credit_limit']:,.0f} limit</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col_left, col_right = st.columns([1, 1])

                with col_left:
                    st.markdown('<div class="section-header">Spending Breakdown</div>', unsafe_allow_html=True)
                    breakdown = result.get("spending_breakdown", {})
                    if breakdown:
                        st.markdown('<div class="fin-card">', unsafe_allow_html=True)
                        render_category_bars(breakdown)
                        st.markdown('</div>', unsafe_allow_html=True)

                with col_right:
                    st.markdown('<div class="section-header">Fraud Status</div>', unsafe_allow_html=True)
                    fl = result.get("fraud_risk_level", "LOW")
                    badge_cls = "badge-fraud" if fraud_is else "badge-safe"
                    card_cls = "fin-card-red" if fraud_is else "fin-card-green"

                    st.markdown(f"""
                    <div class="fin-card {card_cls}">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <span class="badge {badge_cls}">{result.get('fraud_status','—')}</span>
                            <span style="font-family:JetBrains Mono;font-size:0.7rem;color:#475569;">RISK: {fl}</span>
                        </div>
                        <div style="font-family:JetBrains Mono;font-size:0.75rem;color:#94a3b8;margin-top:1rem;">
                            Last transaction analyzed<br>
                            Amount: ₹{user_data['transactions'][-1]['amount']:,.0f}<br>
                            Hour: {user_data['transactions'][-1]['hour']:02d}:00
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown('<div class="section-header" style="margin-top:1rem;">Risk Summary</div>', unsafe_allow_html=True)
                    risk_txt = result.get("risk_summary", "")
                    risk_cls = "insight-danger" if "HIGH" in risk_txt else ("insight-warn" if "MODERATE" in risk_txt else "insight-ok")
                    st.markdown(f'<div class="insight-item {risk_cls}">{risk_txt}</div>', unsafe_allow_html=True)

                # ── Insights ──
                st.markdown('<div class="section-header" style="margin-top:0.5rem;">AI Insights & Recommendations</div>', unsafe_allow_html=True)
                insights = result.get("insights", [])
                for ins in insights:
                    cls = insight_class(ins)
                    st.markdown(f'<div class="insight-item {cls}">{ins}</div>', unsafe_allow_html=True)

                # ── Credit recommendation ──
                st.markdown(f"""
                <div class="fin-card fin-card-blue" style="margin-top:1rem;">
                    <div class="metric-label">Credit Recommendation</div>
                    <div style="font-family:Syne,sans-serif;font-size:0.9rem;color:#93c5fd;margin-top:0.5rem;">
                        {result.get('credit_recommendation','—')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div style="font-family:JetBrains Mono;font-size:0.65rem;color:#334155;text-align:right;margin-top:1rem;">
                    Analyzed at {result.get('analyzed_at','—')} UTC
                </div>
                """, unsafe_allow_html=True)


# ======================================================
# MODE: CHAT ASSISTANT
# ======================================================
elif "💬 AI Chat Assistant" in mode:
    st.markdown('<div class="section-header">Natural Language Financial Queries</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">AI Chat Assistant</div>', unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Render history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-label">YOU</div><div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-label">AI AGENT</div><div class="chat-ai">{msg["content"]}</div>', unsafe_allow_html=True)

    user_input = st.text_input("Ask about any user's finances...", placeholder="e.g. What is Priya's spending classification? Is Karan's transaction suspicious?")

    col_send, col_clear = st.columns([2, 1])
    with col_send:
        send = st.button("SEND MESSAGE")
    with col_clear:
        if st.button("CLEAR CHAT"):
            st.session_state.chat_history = []
            st.rerun()

    if send and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Detect user
        matched_user = None
        for name in USERS:
            if name.lower() in user_input.lower():
                matched_user = name
                break

        # Detect intent
        intent_lower = user_input.lower()
        response_text = ""

        if matched_user and api_ok:
            user_data = USERS[matched_user]
            payload = {
                "credit_limit": user_data["credit_limit"],
                "transactions": user_data["transactions"]
            }
            result, err = post_json("/agent/analyze-user", payload)

            if err:
                response_text = f"⚠️ Could not contact the backend: {err}"
            elif result:
                if "fraud" in intent_lower or "suspicious" in intent_lower or "safe" in intent_lower:
                    response_text = (
                        f"**Fraud Analysis for {matched_user}** ({user_data['archetype']})\n\n"
                        f"Status: {result['fraud_status']} — Risk Level: {result['fraud_risk_level']}\n\n"
                        f"The most recent transaction of ₹{user_data['transactions'][-1]['amount']:,.0f} "
                        f"at {user_data['transactions'][-1]['hour']:02d}:00 was analyzed."
                    )
                elif "credit" in intent_lower or "score" in intent_lower:
                    response_text = (
                        f"**Credit Score for {matched_user}**\n\n"
                        f"Score: {result['credit_score']} ({result['risk_band']})\n\n"
                        f"{result['credit_recommendation']}"
                    )
                elif "spend" in intent_lower or "category" in intent_lower or "overspend" in intent_lower:
                    breakdown = result.get("spending_breakdown", {})
                    cats = ", ".join([f"{k}: {v*100:.1f}%" for k, v in breakdown.items() if v > 0])
                    response_text = (
                        f"**Spending Profile for {matched_user}**\n\n"
                        f"Classification: **{result['spending_type']}**\n"
                        f"Dominant Category: {result['dominant_category']}\n\n"
                        f"Breakdown: {cats}"
                    )
                else:
                    # Full analysis
                    insights_str = "\n".join([f"• {i}" for i in result["insights"]])
                    response_text = (
                        f"**Full Analysis — {matched_user}** ({user_data['archetype']})\n\n"
                        f"• Credit Score: {result['credit_score']} ({result['risk_band']})\n"
                        f"• Spending Type: {result['spending_type']}\n"
                        f"• Fraud Status: {result['fraud_status']}\n\n"
                        f"**Insights:**\n{insights_str}"
                    )
        elif matched_user and not api_ok:
            response_text = "⚠️ Backend API is offline. Please start the FastAPI server."
        elif LLM_AVAILABLE:
            try:
                prompt = f"""You are a financial AI assistant. Answer this question about personal finance clearly and concisely: {user_input}"""
                resp = llm.invoke(prompt)
                response_text = resp.content
            except Exception as e:
                response_text = f"LLM error: {e}. Try asking about a specific user (Rahul, Arjun, Priya, Neha, Karan)."
        else:
            response_text = (
                "I can analyze specific users for you. Try asking:\n"
                "• \"What is Priya's credit score?\"\n"
                "• \"Is Karan's last transaction suspicious?\"\n"
                "• \"Show me Arjun's spending breakdown\""
            )

        st.session_state.chat_history.append({"role": "ai", "content": response_text})
        st.rerun()


# ======================================================
# MODE: FRAUD INSPECTOR
# ======================================================
elif "🔍 Fraud Inspector" in mode:
    st.markdown('<div class="section-header">ML Fraud Detection — Manual Input</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Transaction Risk Analyzer</div>', unsafe_allow_html=True)

    with st.form("fraud_form"):
        col1, col2 = st.columns(2)
        with col1:
            amt = st.number_input("Transaction Amount (₹)", min_value=0.0, value=5000.0, step=100.0)
            hour = st.slider("Transaction Hour", 0, 23, 14)
            location_change = st.selectbox("Location Change?", [0, 1], format_func=lambda x: "Yes — suspicious" if x else "No — same location")
        with col2:
            merchant_type = st.slider("Merchant Type Code", 0, 10, 1)
            txn_velocity = st.slider("Transactions per Hour", 1, 20, 2)

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("ANALYZE TRANSACTION")

    if submitted:
        if not api_ok:
            st.error("Backend offline.")
        else:
            payload = {
                "amount": amt, "hour": hour,
                "location_change": location_change,
                "merchant_type": merchant_type,
                "txn_velocity": txn_velocity
            }
            with st.spinner("Analyzing..."):
                result, err = post_json("/fraud/detect", payload)

            if err:
                st.error(f"Error: {err}")
            elif result:
                fraud_is = result.get("is_fraud", False)
                rl = result.get("risk_level", "LOW")
                card = "fin-card-red" if fraud_is else "fin-card-green"
                badge = "badge-fraud" if fraud_is else "badge-safe"
                icon = "🚨" if fraud_is else "✅"

                st.markdown(f"""
                <div class="fin-card {card}" style="margin-top:1.5rem;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
                        <span style="font-family:Syne;font-size:1.5rem;font-weight:700;">{icon} {result.get('status','—')}</span>
                        <span class="badge {badge}">RISK: {rl}</span>
                    </div>
                    <div style="font-family:JetBrains Mono;font-size:0.78rem;color:#94a3b8;line-height:2;">
                        Amount: ₹{amt:,.0f} &nbsp;|&nbsp; Hour: {hour:02d}:00 &nbsp;|&nbsp;
                        Location Change: {'YES' if location_change else 'NO'} &nbsp;|&nbsp;
                        Velocity: {txn_velocity}/hr
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ======================================================
# MODE: SPENDING CLASSIFIER
# ======================================================
elif "📊 Spending Classifier" in mode:
    st.markdown('<div class="section-header">Spending Behavior Classification</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Category Ratio Analyzer</div>', unsafe_allow_html=True)
    st.markdown("Enter spending ratios (must be between 0.0 and 1.0). Ideal total ≈ 1.0.")

    with st.form("spending_form"):
        col1, col2 = st.columns(2)
        with col1:
            food     = st.slider("Food Ratio",       0.0, 1.0, 0.20, 0.01)
            rent     = st.slider("Rent / Housing",   0.0, 1.0, 0.30, 0.01)
            luxury   = st.slider("Luxury Ratio",     0.0, 1.0, 0.20, 0.01)
        with col2:
            invest   = st.slider("Investment Ratio", 0.0, 1.0, 0.10, 0.01)
            misc     = st.slider("Misc Ratio",       0.0, 1.0, 0.20, 0.01)

        total = food + rent + luxury + invest + misc
        st.markdown(
            f'<div style="font-family:JetBrains Mono;font-size:0.75rem;color:{"#10b981" if 0.95 <= total <= 1.05 else "#f59e0b"};">'
            f'Ratio Total: {total:.2f} {"✓" if 0.95 <= total <= 1.05 else "(ideally 1.0)"}</div>',
            unsafe_allow_html=True
        )
        submitted = st.form_submit_button("CLASSIFY SPENDING")

    if submitted:
        if not api_ok:
            st.error("Backend offline.")
        else:
            payload = {
                "food_ratio": food, "rent_ratio": rent,
                "luxury_ratio": luxury, "investment_ratio": invest,
                "misc_ratio": misc
            }
            with st.spinner("Classifying..."):
                result, err = post_json("/spending/predict", payload)

            if err:
                st.error(f"Error: {err}")
            elif result:
                spending_type = result.get("spending_type", "—")
                dominant = result.get("dominant_category", "—")

                st.markdown(f"""
                <div class="fin-card fin-card-amber" style="margin-top:1.5rem;">
                    <div class="metric-label">Classification Result</div>
                    <div style="font-family:Syne;font-size:2rem;font-weight:800;color:#f1f5f9;margin:0.5rem 0;">
                        {spending_type}
                    </div>
                    <div style="font-family:JetBrains Mono;font-size:0.75rem;color:#94a3b8;">
                        Dominant Category: <span style="color:#f59e0b;">{dominant}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ======================================================
# MODE: CREDIT SCORER
# ======================================================
elif "💳 Credit Scorer" in mode:
    st.markdown('<div class="section-header">ML Credit Scoring — Manual Input</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Creditworthiness Predictor</div>', unsafe_allow_html=True)

    with st.form("credit_form"):
        col1, col2 = st.columns(2)
        with col1:
            monthly_spend  = st.number_input("Monthly Spend (₹)", 0.0, 1000000.0, 25000.0, 1000.0)
            utilization    = st.slider("Credit Utilization", 0.0, 1.0, 0.40, 0.01)
            late_payments  = st.number_input("Late Payments (count)", 0, 50, 1)
        with col2:
            num_txns       = st.number_input("Monthly Transactions", 1, 200, 20)
            discretionary  = st.slider("Discretionary Ratio", 0.0, 1.0, 0.30, 0.01)

        submitted = st.form_submit_button("PREDICT CREDIT SCORE")

    if submitted:
        if not api_ok:
            st.error("Backend offline.")
        else:
            payload = {
                "monthly_spend": monthly_spend,
                "credit_utilization": utilization,
                "late_payments": late_payments,
                "num_transactions": num_txns,
                "discretionary_ratio": discretionary
            }
            with st.spinner("Scoring..."):
                result, err = post_json("/credit/predict", payload)

            if err:
                st.error(f"Error: {err}")
            elif result:
                score = result.get("credit_score", 0)
                band  = result.get("risk_band", "—")
                rec   = result.get("recommendation", "—")
                sc    = score_color(score)

                st.markdown(f"""
                <div class="fin-card" style="margin-top:1.5rem;">
                    <div class="score-display">
                        <div class="metric-label">Predicted Credit Score</div>
                        <div class="score-number" style="color:{sc};">{score}</div>
                        <div class="score-band" style="color:{sc};">{band}</div>
                    </div>
                    <hr style="border-color:#1e2d42;margin:1rem 0;">
                    <div style="font-family:Syne;font-size:0.88rem;color:#94a3b8;text-align:center;">
                        {rec}
                    </div>
                </div>
                """, unsafe_allow_html=True)

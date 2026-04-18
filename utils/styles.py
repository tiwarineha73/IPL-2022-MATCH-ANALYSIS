import streamlit as st
import plotly.graph_objects as go

# ── Team colour palette ──────────────────────────────────────────────
TEAM_COLORS = {
    "Chennai Super Kings":               "#F9CD05",
    "Delhi Capitals":                    "#0078BC",
    "Gujarat Titans":                    "#1C1C6B",
    "Kolkata Knight Riders":             "#3A225D",
    "Lucknow Super Giants":              "#A72056",
    "Mumbai Indians":                    "#004BA0",
    "Punjab Kings":                      "#ED1B24",
    "Rajasthan Royals":                  "#FF69B4",
    "Royal Challengers Bangalore":       "#EC1C24",
    "Sunrisers Hyderabad":               "#F7A721",
}

BG       = "#0E1117"
CARD     = "#1E2130"
ACCENT   = "#FF6B35"
ACCENT2  = "#00D4FF"
MUTED    = "#8899AA"

PLOTLY_BASE = dict(
    paper_bgcolor=BG,
    plot_bgcolor=CARD,
    font=dict(color="#FAFAFA", family="Inter, sans-serif", size=12),
    margin=dict(l=30, r=30, t=50, b=40),
)


def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0E1117;
        font-family: 'Inter', sans-serif;
    }
    [data-testid="stSidebar"] { background-color: #161B27; }
    [data-testid="stSidebar"] .css-1d391kg { padding-top: 1rem; }
    .metric-card {
        background: linear-gradient(135deg, #1E2130 0%, #252B3B 100%);
        border-radius: 12px;
        padding: 18px 22px;
        border-left: 4px solid #FF6B35;
        margin-bottom: 10px;
    }
    .metric-card .label { margin: 0; font-size: 11px; color: #8899AA;
                          letter-spacing: 1.5px; text-transform: uppercase; }
    .metric-card .value { margin: 6px 0 0; font-size: 30px; font-weight: 800;
                          color: #FAFAFA; line-height: 1; }
    .section-title {
        font-size: 20px; font-weight: 700;
        border-left: 4px solid #FF6B35;
        padding-left: 12px; margin: 28px 0 14px;
        color: #FAFAFA;
    }
    .match-card {
        background: #1E2130; border-radius: 10px;
        padding: 14px 18px; margin-bottom: 10px;
    }
    div[data-testid="stDataFrame"] thead tr th {
        background-color: #1E2130 !important;
        color: #FF6B35 !important;
    }
    </style>
    """, unsafe_allow_html=True)


def metric_card(label: str, value: str, accent: str = ACCENT):
    st.markdown(f"""
    <div class="metric-card" style="border-left-color:{accent};">
        <p class="label">{label}</p>
        <p class="value">{value}</p>
    </div>""", unsafe_allow_html=True)


def section_title(text: str):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


def base_layout(**extra):
    layout = dict(**PLOTLY_BASE)
    layout.update(extra)
    return layout


def team_color(team: str) -> str:
    return TEAM_COLORS.get(team, ACCENT)

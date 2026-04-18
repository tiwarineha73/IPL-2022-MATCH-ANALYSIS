import streamlit as st
from data_loader import load_data

st.set_page_config(
    page_title="IPL 2022 Dashboard",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Lazy imports to keep startup fast
from pages.home             import render as home
from pages.match_analysis   import render as match
from pages.team_performance import render as team
from pages.player_perf      import render as player
from pages.batting          import render as batting
from pages.bowling          import render as bowling
from pages.venue            import render as venue
from pages.points_table     import render as points
from pages.prediction       import render as prediction
from pages.insights         import render as insights

df = load_data("IPL_Matches_2022.csv")

# ── Sidebar ──────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style='text-align:center;padding:10px 0 4px;'>
    <span style='font-size:36px;'>🏏</span><br>
    <span style='font-size:18px;font-weight:800;color:#FF6B35;'>IPL 2022</span><br>
    <span style='font-size:12px;color:#8899AA;'>Analytics Dashboard</span>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")

PAGES = {
    "🏠  Home":               home,
    "📊  Match Analysis":     match,
    "🛡️  Team Performance":   team,
    "👤  Player Performance": player,
    "🏃  Batting Analysis":   batting,
    "🎳  Bowling Analysis":   bowling,
    "🏟️  Venue Analysis":     venue,
    "📈  Points Table":       points,
    "🔮  Prediction":         prediction,
    "💡  Insights":           insights,
}

page = st.sidebar.radio("Navigate", list(PAGES.keys()))
st.sidebar.markdown("---")
st.sidebar.caption("74 matches · 10 teams · IPL 2022")



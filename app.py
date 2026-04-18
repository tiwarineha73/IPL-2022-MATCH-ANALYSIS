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
choice = st.sidebar.radio("Navigate", list(PAGES.keys()))
st.sidebar.markdown("---")
PAGES[choice](df)
st.sidebar.markdown("---")
st.sidebar.caption("74 matches · 10 teams · IPL 2022")



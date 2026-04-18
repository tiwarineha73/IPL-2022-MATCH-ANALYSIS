import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils import inject_css, metric_card, section_title, base_layout, TEAM_COLORS, ACCENT


def render(df: pd.DataFrame):
    inject_css()
    st.markdown("""
    <h1 style='font-size:36px;font-weight:800;margin-bottom:2px;'>
        🏏 IPL 2022 Analytics Dashboard
    </h1>
    <p style='color:#8899AA;margin-bottom:20px;font-size:15px;'>
        Broadcaster-quality cricket analytics · 74 matches · 10 teams · Season 2022
    </p>""", unsafe_allow_html=True)

    # ── KPI row ──────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("TOTAL MATCHES",   str(len(df)))
    with c2: metric_card("TEAMS",           str(df["Team1"].nunique()))
    with c3: metric_card("2022 CHAMPION",   "Gujarat Titans")
    with c4:
        top_potm = df["Player_of_Match"].value_counts().idxmax()
        metric_card("TOP POTM WINNER", top_potm)

    # ── Cumulative wins timeline ─────────────────────────────────────
    section_title("📅 Cumulative Wins – Season Timeline")
    tl = df.dropna(subset=["Date"]).sort_values("Date").copy()
    top5 = df["WinningTeam"].value_counts().head(5).index.tolist()
    fig = go.Figure()
    for team in top5:
        y = (tl["WinningTeam"] == team).cumsum().values
        fig.add_trace(go.Scatter(
            x=tl["Date"], y=y, name=team, mode="lines+markers",
            line=dict(width=2.5, color=TEAM_COLORS.get(team, ACCENT)),
            marker=dict(size=5),
        ))
    fig.update_layout(
        **base_layout(height=370, title="Top 5 Teams – Wins Accumulation"),
        xaxis_title="Date", yaxis_title="Cumulative Wins",
        legend=dict(orientation="h", yanchor="bottom", y=-0.35),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Two panels ───────────────────────────────────────────────────
    ca, cb = st.columns(2)

    with ca:
        section_title("🏆 Biggest Victories")
        runs_win  = df[df["WonBy"]=="Runs"].nlargest(3, "Margin")
        wkts_win  = df[df["WonBy"]=="Wickets"].nlargest(3, "Margin")
        for _, r in pd.concat([runs_win, wkts_win]).iterrows():
            opp = r["Team2"] if r["WinningTeam"] == r["Team1"] else r["Team1"]
            clr = TEAM_COLORS.get(r["WinningTeam"], ACCENT)
            st.markdown(f"""
            <div style='background:#1E2130;border-radius:9px;padding:11px 15px;
                        margin-bottom:8px;border-left:3px solid {clr};'>
                <b>{r['WinningTeam']}</b> beat {opp}<br>
                <span style='color:#8899AA;font-size:12px;'>
                    by {int(r['Margin'])} {r['WonBy']} &nbsp;·&nbsp; {r['Venue'].split(',')[0]}
                </span>
            </div>""", unsafe_allow_html=True)

    with cb:
        section_title("🌟 POTM Leaderboard")
        potm = df["Player_of_Match"].value_counts().head(8).reset_index()
        potm.columns = ["Player", "Awards"]
        fig2 = px.bar(potm, x="Awards", y="Player", orientation="h",
                      template="plotly_dark", color_discrete_sequence=[ACCENT])
        fig2.update_layout(**base_layout(height=340), showlegend=False)
        fig2.update_yaxes(autorange="reversed")
        st.plotly_chart(fig2, use_container_width=True)

    # ── Last 10 matches ──────────────────────────────────────────────
    section_title("📋 Recent Matches")
    last10 = df.sort_values("Date", ascending=False).head(10)[
        ["Date","MatchNumber","Team1","Team2","WinningTeam","WonBy","Margin","Player_of_Match"]
    ].copy()
    last10["Date"] = last10["Date"].dt.strftime("%d %b %Y")
    last10["Margin"] = last10["Margin"].fillna("").apply(
        lambda x: str(int(x)) if x != "" else ""
    )
    st.dataframe(last10.reset_index(drop=True), use_container_width=True, hide_index=True)

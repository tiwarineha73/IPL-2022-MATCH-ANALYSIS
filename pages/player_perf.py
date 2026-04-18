import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.styles import inject_css, section_title, base_layout, ACCENT, ACCENT2


def render(df: pd.DataFrame):
    inject_css()
    st.markdown("## 👤 Player Performance")

    potm = df["Player_of_Match"].value_counts().reset_index()
    potm.columns = ["Player", "Awards"]

    # ── Leaderboard ──────────────────────────────────────────────────
    section_title("🏆 Player of the Match Leaderboard")
    top_n = st.slider("Show top N players", 5, len(potm), 15)
    top_df = potm.head(top_n)

    fig = px.bar(
        top_df, x="Player", y="Awards",
        color="Awards", color_continuous_scale="Oranges",
        template="plotly_white",
    )
    fig.update_layout(**base_layout(height=400),
                      showlegend=False, coloraxis_showscale=False,
                      xaxis_tickangle=-35)
    st.plotly_chart(fig, use_container_width=True)

    # ── Radar comparison ─────────────────────────────────────────────
    section_title("📡 Player Radar Comparison")

    def pstats(player: str) -> dict:
        pm = df[df["Player_of_Match"] == player]
        return {
            "POTM Awards":      len(pm),
            "Venues Won At":    pm["Venue"].nunique(),
            "Unique Opponents": pd.concat([pm["Team1"], pm["Team2"]]).nunique(),
            "In Winning Team":  int((pm["WinningTeam"].notna()).sum()),
            "Match Spread":     pm["Date"].nunique() if "Date" in pm else 0,
        }

    top10 = potm.head(10)["Player"].tolist()
    c1, c2 = st.columns(2)
    with c1: p1 = st.selectbox("Player 1", top10, index=0)
    with c2: p2 = st.selectbox("Player 2", [p for p in top10 if p != p1], index=0)

    s1, s2 = pstats(p1), pstats(p2)
    cats = list(s1.keys())

    fig2 = go.Figure()
    for name, stats, color in [(p1, s1, ACCENT), (p2, s2, ACCENT2)]:
        vals = [stats[c] for c in cats] + [stats[cats[0]]]
        fill_color = f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.15)"
        fig2.add_trace(go.Scatterpolar(
            r=vals, theta=cats + [cats[0]],
            fill="toself", name=name,
            line_color=color, fillcolor=fill_color,
        ))
    fig2.update_layout(
        **base_layout(height=450, title="Head-to-Head Radar"),
        polar=dict(
            bgcolor="#FFFFFF",
            radialaxis=dict(visible=True, color="#8899AA", showticklabels=True),
            angularaxis=dict(color="#8899AA"),
        ),
        legend=dict(orientation="h", y=-0.15),
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ── Full table ───────────────────────────────────────────────────
    section_title("📋 All POTM Winners")
    st.dataframe(potm, use_container_width=True, hide_index=True)

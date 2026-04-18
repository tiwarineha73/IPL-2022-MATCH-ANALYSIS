import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data_loader import team_stats
from utils.styles import inject_css, section_title, metric_card, base_layout, TEAM_COLORS, ACCENT, ACCENT2


def render(df: pd.DataFrame):
    inject_css()
    st.markdown("## 🛡️ Team Performance")
    stats = team_stats(df)

    section_title("📋 Season Stats Table")
    st.dataframe(stats, use_container_width=True, hide_index=True)

    ca, cb = st.columns(2)
    with ca:
        section_title("📊 Win Percentage")
        fig = px.bar(
            stats.sort_values("Win %", ascending=True),
            x="Win %", y="Team", orientation="h",
            color="Team", color_discrete_map=TEAM_COLORS,
            template="plotly_white",
        )
        fig.update_layout(**base_layout(height=380), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with cb:
        section_title("🔵 Matches vs Wins")
        fig2 = px.scatter(
            stats, x="Matches", y="Wins", text="Team",
            size="Win %", color="Win %",
            color_continuous_scale="Oranges",
            template="plotly_white",
        )
        fig2.update_traces(textposition="top center", marker_sizemin=10)
        fig2.update_layout(**base_layout(height=380), coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    section_title("⚔️ Head-to-Head Battle")
    all_teams = sorted(df["Team1"].unique())
    c1, c2 = st.columns(2)
    with c1: t1 = st.selectbox("Team 1", all_teams, index=0)
    with c2: t2 = st.selectbox("Team 2", [t for t in all_teams if t != t1], index=0)

    h2h = df[
        ((df["Team1"]==t1)&(df["Team2"]==t2)) |
        ((df["Team1"]==t2)&(df["Team2"]==t1))
    ]

    if h2h.empty:
        st.info("These two teams did not meet in IPL 2022 league stage.")
    else:
        t1w = int((h2h["WinningTeam"]==t1).sum())
        t2w = int((h2h["WinningTeam"]==t2).sum())
        total = len(h2h)
        m1, m2, m3 = st.columns(3)
        with m1: metric_card(f"{t1} Wins", str(t1w), TEAM_COLORS.get(t1, ACCENT))
        with m2: metric_card("Matches", str(total))
        with m3: metric_card(f"{t2} Wins", str(t2w), TEAM_COLORS.get(t2, ACCENT2))

        fig3 = go.Figure(go.Bar(
            x=[t1, t2], y=[t1w, t2w],
            marker_color=[TEAM_COLORS.get(t1, ACCENT), TEAM_COLORS.get(t2, ACCENT2)],
            text=[t1w, t2w], textposition="outside",
        ))
        fig3.update_layout(
            **base_layout(height=300, title=f"{t1} vs {t2}"),
            showlegend=False, yaxis_range=[0, max(t1w, t2w)+1],
        )
        st.plotly_chart(fig3, use_container_width=True)

        st.dataframe(
            h2h[["Date","Team1","Team2","WinningTeam","WonBy","Margin","Player_of_Match"]]
            .assign(Date=lambda d: d["Date"].dt.strftime("%d %b %Y"))
            .reset_index(drop=True),
            use_container_width=True, hide_index=True
        )

    section_title("💪 Wins After Losing the Toss")
    wlt = (
        df[df["WonAfterLosingToss"]]
        .groupby("WinningTeam").size()
        .reset_index(name="Wins After Losing Toss")
        .sort_values("Wins After Losing Toss", ascending=False)
    )
    fig4 = px.bar(wlt, x="WinningTeam", y="Wins After Losing Toss",
                  color="WinningTeam", color_discrete_map=TEAM_COLORS,
                  template="plotly_white")
    fig4.update_layout(**base_layout(height=360), showlegend=False, xaxis_tickangle=-30)
    st.plotly_chart(fig4, use_container_width=True)
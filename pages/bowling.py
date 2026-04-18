import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.styles import inject_css, section_title, base_layout, TEAM_COLORS, ACCENT, ACCENT2


def render(df: pd.DataFrame):
    inject_css()
    st.markdown("## 🎳 Bowling Analysis")

    # ── Bowl-first (field) efficiency ────────────────────────────────
    section_title("🏏 Bowl-First Win Efficiency by Team")
    field = df[df["TossDecision"] == "field"].copy()
    field_wins = field[field["TossWinner"] == field["WinningTeam"]]

    bf = field.groupby("TossWinner").size().reset_index(name="FieldFirst")
    fw = field_wins.groupby("WinningTeam").size().reset_index(name="Won")
    bf = bf.merge(fw, left_on="TossWinner", right_on="WinningTeam", how="left").fillna(0)
    bf["Won"] = bf["Won"].astype(int)
    bf["WinRate"] = (bf["Won"] / bf["FieldFirst"] * 100).round(1)
    bf = bf.sort_values("WinRate", ascending=False)

    fig = px.bar(bf, x="TossWinner", y="WinRate",
                 color="TossWinner", color_discrete_map=TEAM_COLORS,
                 template="plotly_dark",
                 labels={"TossWinner":"Team","WinRate":"Win % (Bowl First)"})
    fig.update_layout(**base_layout(height=370), showlegend=False, xaxis_tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)

    # ── Bat-first (bat) efficiency ───────────────────────────────────
    section_title("🏏 Bat-First Win Efficiency by Team")
    bat = df[df["TossDecision"] == "bat"].copy()
    bat_wins = bat[bat["TossWinner"] == bat["WinningTeam"]]

    bb = bat.groupby("TossWinner").size().reset_index(name="BatFirst")
    bw = bat_wins.groupby("WinningTeam").size().reset_index(name="Won")
    bb = bb.merge(bw, left_on="TossWinner", right_on="WinningTeam", how="left").fillna(0)
    bb["Won"] = bb["Won"].astype(int)
    bb["WinRate"] = (bb["Won"] / bb["BatFirst"] * 100).round(1)

    fig2 = px.bar(bb.sort_values("WinRate", ascending=False),
                  x="TossWinner", y="WinRate",
                  color="TossWinner", color_discrete_map=TEAM_COLORS,
                  template="plotly_dark",
                  labels={"TossWinner":"Team","WinRate":"Win % (Bat First)"})
    fig2.update_layout(**base_layout(height=370), showlegend=False, xaxis_tickangle=-30)
    st.plotly_chart(fig2, use_container_width=True)

    # ── Toss decision monthly trend ──────────────────────────────────
    section_title("🎲 Toss Decision by Month")
    tl = df.dropna(subset=["Date"]).copy()
    tl["Month"] = tl["Date"].dt.strftime("%b")
    month_order = ["Mar","Apr","May","Jun"]
    td = tl.groupby(["Month","TossDecision"]).size().reset_index(name="Count")
    td["Month"] = pd.Categorical(td["Month"], categories=month_order, ordered=True)
    td = td.sort_values("Month")

    fig3 = px.bar(td, x="Month", y="Count", color="TossDecision",
                  barmode="group",
                  color_discrete_sequence=[ACCENT, ACCENT2],
                  template="plotly_dark")
    fig3.update_layout(**base_layout(height=330))
    st.plotly_chart(fig3, use_container_width=True)

    # ── Scatter: field first count vs win rate ───────────────────────
    section_title("📈 Bowl-First: Matches Played vs Win Rate")
    fig4 = px.scatter(
        bf, x="FieldFirst", y="WinRate",
        text="TossWinner", size="FieldFirst",
        color="WinRate", color_continuous_scale="RdYlGn",
        template="plotly_white",
        labels={"FieldFirst":"Times Chose to Field","WinRate":"Win %"},
    )
    fig4.update_traces(textposition="top center", marker_sizemin=10)
    fig4.update_layout(**base_layout(height=420), coloraxis_showscale=True)
    st.plotly_chart(fig4, use_container_width=True)

    st.caption("⚠️ Ball-by-ball data is unavailable in this dataset. "
               "All analysis is derived from match-level results.")

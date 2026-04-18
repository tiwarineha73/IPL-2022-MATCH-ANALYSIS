import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.styles import inject_css, section_title, base_layout, TEAM_COLORS, ACCENT, ACCENT2


def render(df: pd.DataFrame):
    inject_css()
    st.markdown("## 🏃 Batting Analysis")

    # ── Win method split ─────────────────────────────────────────────
    ca, cb = st.columns(2)
    with ca:
        section_title("🏏 Chasing vs Defending Wins")
        wm = df["WinMethod"].value_counts().reset_index()
        wm.columns = ["Method","Count"]
        fig = px.pie(wm, names="Method", values="Count",
                     color_discrete_sequence=[ACCENT, ACCENT2],
                     hole=0.42, template="plotly_dark")
        fig.update_layout(**base_layout(height=310))
        st.plotly_chart(fig, use_container_width=True)

    with cb:
        section_title("📏 Winning Margin Distribution")
        fig2 = px.histogram(
            df.dropna(subset=["Margin"]),
            x="Margin", color="WonBy",
            color_discrete_sequence=[ACCENT, ACCENT2],
            nbins=18, barmode="overlay", template="plotly_dark",
            labels={"Margin":"Margin","WonBy":"Won By"},
        )
        fig2.update_layout(**base_layout(height=310))
        st.plotly_chart(fig2, use_container_width=True)

    # ── Separate histograms ──────────────────────────────────────────
    cc, cd = st.columns(2)
    with cc:
        section_title("🏏 Wins by Runs – Distribution")
        runs = df[(df["WonBy"]=="Runs")].dropna(subset=["Margin"])
        fig3 = px.histogram(runs, x="Margin", nbins=15,
                            color_discrete_sequence=[ACCENT],
                            template="plotly_dark")
        fig3.update_layout(**base_layout(height=290))
        st.plotly_chart(fig3, use_container_width=True)
    with cd:
        section_title("🏏 Wins by Wickets – Distribution")
        wkts = df[(df["WonBy"]=="Wickets")].dropna(subset=["Margin"])
        fig4 = px.histogram(wkts, x="Margin", nbins=10,
                            color_discrete_sequence=[ACCENT2],
                            template="plotly_dark")
        fig4.update_layout(**base_layout(height=290))
        st.plotly_chart(fig4, use_container_width=True)

    # ── Weekly trend ─────────────────────────────────────────────────
    section_title("📅 Weekly Match Volume")
    tl = df.dropna(subset=["Date"]).copy()
    tl["Week"] = tl["Date"].dt.to_period("W").astype(str)
    weekly = tl.groupby("Week").size().reset_index(name="Matches")
    fig5 = px.line(weekly, x="Week", y="Matches", markers=True,
                   color_discrete_sequence=[ACCENT], template="plotly_dark")
    fig5.update_layout(**base_layout(height=320), xaxis_tickangle=-30)
    st.plotly_chart(fig5, use_container_width=True)

    # ── Largest run margins per team ─────────────────────────────────
    section_title("🏆 Biggest Run Wins by Team")
    br = (
        df[df["WonBy"]=="Runs"].dropna(subset=["Margin"])
        .groupby("WinningTeam")["Margin"].max()
        .reset_index().sort_values("Margin", ascending=False)
    )
    fig6 = px.bar(br, x="WinningTeam", y="Margin",
                  color="WinningTeam", color_discrete_map=TEAM_COLORS,
                  template="plotly_dark",
                  labels={"WinningTeam":"Team","Margin":"Max Margin (Runs)"})
    fig6.update_layout(**base_layout(height=360), showlegend=False, xaxis_tickangle=-30)
    st.plotly_chart(fig6, use_container_width=True)

    # ── Margin heatmap ───────────────────────────────────────────────
    section_title("🗺️ Avg Margin Heatmap – Team × Venue")
    hm_data = (
        df.dropna(subset=["Margin","WinningTeam"])
        .groupby(["WinningTeam","Venue"])["Margin"].mean()
        .reset_index()
    )
    hm_data["Venue"] = hm_data["Venue"].str.split(",").str[0]
    pivot = hm_data.pivot(index="WinningTeam", columns="Venue", values="Margin").fillna(0)
    fig7 = px.imshow(pivot, color_continuous_scale="Oranges",
                     template="plotly_dark",
                     labels=dict(color="Avg Margin"))
    fig7.update_layout(**base_layout(height=420), xaxis_tickangle=-30)
    st.plotly_chart(fig7, use_container_width=True)

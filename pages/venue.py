import streamlit as st
import plotly.express as px
import pandas as pd
from utils.styles import inject_css, section_title, base_layout, ACCENT, ACCENT2


def render(df: pd.DataFrame):
    inject_css()
    st.markdown("## 🏟️ Venue Analysis")

    vc = df["Venue"].value_counts().reset_index()
    vc.columns = ["Venue", "Matches"]
    vc["VenueShort"] = vc["Venue"].str.split(",").str[0]

    section_title("📍 Matches Hosted per Venue")
    fig = px.bar(vc, x="VenueShort", y="Matches",
                 color="Matches", color_continuous_scale="Oranges",
                 template="plotly_white",
                 labels={"VenueShort": "Venue"})
    fig.update_layout(height=360, coloraxis_showscale=False,
                      xaxis_tickangle=-20,
                      paper_bgcolor="#F5F7FA", plot_bgcolor="#FFFFFF",
                      font=dict(color="#1A1A2E", family="Inter, sans-serif"))
    st.plotly_chart(fig, use_container_width=True)

    section_title("⚔️ Chase vs Defend – Win Split by Venue")
    wv = df.dropna(subset=["WinningTeam"]).copy()

    def batted_second(row):
        if row["TossDecision"] == "field":
            return row["TossWinner"] == row["WinningTeam"]
        else:
            return row["TossWinner"] != row["WinningTeam"]

    wv["BattedSecond"] = wv.apply(batted_second, axis=1)
    wv["VenueShort"] = wv["Venue"].str.split(",").str[0]
    split = (wv.groupby(["VenueShort", "BattedSecond"])
               .size().reset_index(name="Wins"))
    split["Result"] = split["BattedSecond"].map(
        {True: "Chasing Won", False: "Defending Won"})

    fig2 = px.bar(split, x="VenueShort", y="Wins", color="Result",
                  barmode="stack",
                  color_discrete_sequence=[ACCENT, ACCENT2],
                  template="plotly_white",
                  labels={"VenueShort": "Venue"})
    fig2.update_layout(height=380, xaxis_tickangle=-20,
                       paper_bgcolor="#F5F7FA", plot_bgcolor="#FFFFFF",
                       font=dict(color="#1A1A2E", family="Inter, sans-serif"))
    st.plotly_chart(fig2, use_container_width=True)

    section_title("🗺️ Venue Overview")
    venue_summary = vc[["VenueShort", "Matches"]].sort_values("Matches", ascending=False)
    fig3 = px.bar(venue_summary, x="VenueShort", y="Matches",
                  color="Matches", color_continuous_scale="Oranges",
                  template="plotly_white", text="Matches",
                  labels={"VenueShort": "Venue", "Matches": "Matches Hosted"})
    fig3.update_traces(textposition="outside")
    fig3.update_layout(height=380, coloraxis_showscale=False,
                       xaxis_tickangle=-20,
                       paper_bgcolor="#F5F7FA", plot_bgcolor="#FFFFFF",
                       font=dict(color="#1A1A2E", family="Inter, sans-serif"))
    st.plotly_chart(fig3, use_container_width=True)

    section_title("🎲 Toss Decision by Venue")
    df2 = df.copy()
    df2["VenueShort"] = df2["Venue"].str.split(",").str[0]
    tv = df2.groupby(["VenueShort", "TossDecision"]).size().reset_index(name="Count")
    fig4 = px.bar(tv, x="VenueShort", y="Count", color="TossDecision",
                  barmode="group",
                  color_discrete_sequence=[ACCENT, ACCENT2],
                  template="plotly_white",
                  labels={"VenueShort": "Venue"})
    fig4.update_layout(height=350, xaxis_tickangle=-20,
                       paper_bgcolor="#F5F7FA", plot_bgcolor="#FFFFFF",
                       font=dict(color="#1A1A2E", family="Inter, sans-serif"))
    st.plotly_chart(fig4, use_container_width=True)
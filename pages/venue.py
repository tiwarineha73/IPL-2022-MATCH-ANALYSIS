import streamlit as st
import plotly.express as px
import pandas as pd
from utils.styles import inject_css, section_title, base_layout, ACCENT, ACCENT2

VENUE_COORDS = {
    "Brabourne Stadium, Mumbai":                      (18.9389, 72.8258),
    "Dr DY Patil Sports Academy, Mumbai":             (19.0636, 73.0198),
    "Maharashtra Cricket Association Stadium, Pune":  (18.6524, 73.7898),
    "Wankhede Stadium, Mumbai":                       (18.9443, 72.8249),
    "Eden Gardens, Kolkata":                          (22.5645, 88.3433),
    "Narendra Modi Stadium, Ahmedabad":               (23.0905, 72.5967),
}


def render(df: pd.DataFrame):
    inject_css()
    st.markdown("## 🏟️ Venue Analysis")

    section_title("📍 Matches Hosted per Venue")
    vc = df["Venue"].value_counts().reset_index()
    vc.columns = ["Venue","Matches"]
    vc["VenueShort"] = vc["Venue"].str.split(",").str[0]

    fig = px.bar(vc, x="VenueShort", y="Matches",
                 color="Matches", color_continuous_scale="Oranges",
                 template="plotly_white",
                 labels={"VenueShort":"Venue"})
    fig.update_layout(**base_layout(height=360), showlegend=False,
                      coloraxis_showscale=False, xaxis_tickangle=-20)
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
    split = (wv.groupby(["VenueShort","BattedSecond"])
               .size().reset_index(name="Wins"))
    split["Result"] = split["BattedSecond"].map(
        {True:"Chasing Won", False:"Defending Won"})

    fig2 = px.bar(split, x="VenueShort", y="Wins", color="Result",
                  barmode="stack",
                  color_discrete_sequence=[ACCENT, ACCENT2],
                  template="plotly_white",
                  labels={"VenueShort":"Venue"})
    fig2.update_layout(**base_layout(height=380), xaxis_tickangle=-20)
    st.plotly_chart(fig2, use_container_width=True)

    section_title("🗺️ Venue Map (India)")
    map_rows = []
    for _, row in vc.iterrows():
        coords = VENUE_COORDS.get(row["Venue"])
        if coords:
            map_rows.append({
                "Venue": row["VenueShort"],
                "Full":  row["Venue"],
                "Matches": row["Matches"],
                "lat": coords[0],
                "lon": coords[1],
            })
    if map_rows:
        mdf = pd.DataFrame(map_rows)
        fig3 = px.scatter_mapbox(
            mdf, lat="lat", lon="lon",
            size="Matches", color="Matches",
            hover_name="Full",
            color_continuous_scale="Oranges",
            zoom=4.2, center={"lat": 21.0, "lon": 78.5},
            mapbox_style="carto-positron",
            size_max=35,
        )
        fig3.update_layout(**base_layout(height=480),
                           coloraxis_showscale=False,
                           margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Map coordinates could not be matched.")

    section_title("🎲 Toss Decision by Venue")
    df2 = df.copy()
    df2["VenueShort"] = df2["Venue"].str.split(",").str[0]
    tv = df2.groupby(["VenueShort","TossDecision"]).size().reset_index(name="Count")
    fig4 = px.bar(tv, x="VenueShort", y="Count", color="TossDecision",
                  barmode="group",
                  color_discrete_sequence=[ACCENT, ACCENT2],
                  template="plotly_white",
                  labels={"VenueShort":"Venue"})
    fig4.update_layout(**base_layout(height=350), xaxis_tickangle=-20)
    st.plotly_chart(fig4, use_container_width=True)
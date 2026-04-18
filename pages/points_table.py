import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.styles import inject_css, section_title, metric_card, base_layout, TEAM_COLORS, ACCENT

POINTS_DATA = [
    {"Pos": 1, "Team": "Gujarat Titans",              "M":14,"W":10,"L":4,"NR":0,"Pts":20,"NRR":+0.324},
    {"Pos": 2, "Team": "Rajasthan Royals",            "M":14,"W": 9,"L":5,"NR":0,"Pts":18,"NRR":+0.298},
    {"Pos": 3, "Team": "Lucknow Super Giants",        "M":14,"W": 9,"L":5,"NR":0,"Pts":18,"NRR":+0.251},
    {"Pos": 4, "Team": "Royal Challengers Bangalore", "M":14,"W": 8,"L":6,"NR":0,"Pts":16,"NRR":-0.253},
    {"Pos": 5, "Team": "Punjab Kings",                "M":14,"W": 7,"L":7,"NR":0,"Pts":14,"NRR":+0.126},
    {"Pos": 6, "Team": "Delhi Capitals",              "M":14,"W": 7,"L":7,"NR":0,"Pts":14,"NRR":-0.208},
    {"Pos": 7, "Team": "Kolkata Knight Riders",       "M":14,"W": 6,"L":8,"NR":0,"Pts":12,"NRR":+0.146},
    {"Pos": 8, "Team": "Sunrisers Hyderabad",         "M":14,"W": 6,"L":8,"NR":0,"Pts":12,"NRR":-0.368},
    {"Pos": 9, "Team": "Mumbai Indians",              "M":14,"W": 4,"L":10,"NR":0,"Pts": 8,"NRR":-0.508},
    {"Pos":10, "Team": "Chennai Super Kings",         "M":14,"W": 4,"L":10,"NR":0,"Pts": 8,"NRR":-0.382},
]


def render(df: pd.DataFrame):
    inject_css()
    st.markdown("## 📈 Points Table")
    pts = pd.DataFrame(POINTS_DATA)

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("LEAGUE LEADER",  "Gujarat Titans")
    with c2: metric_card("MOST POINTS",    "20")
    with c3: metric_card("BEST NRR",       "+0.324")
    with c4: metric_card("PLAYOFF CUTOFF", "16 pts")

    section_title("🏆 Official IPL 2022 Standings")
    def row_style(row):
        if row["Pos"] <= 4:
            return ["background-color: rgba(255,107,53,0.12)"] * len(row)
        return [""] * len(row)
    styled = pts.style.apply(row_style, axis=1).format({"NRR": "{:+.3f}"})
    st.dataframe(styled, use_container_width=True, hide_index=True)
    st.caption("🟠 Highlighted rows = Playoff qualifiers (Top 4)")

    section_title("📊 Points by Team")
    fig = px.bar(pts, x="Team", y="Pts",
                 color="Team", color_discrete_map=TEAM_COLORS,
                 text="Pts", template="plotly_white",
                 labels={"Pts": "Points"})
    fig.add_hline(y=16, line_dash="dot", line_color=ACCENT,
                  annotation_text="~Playoff threshold", annotation_position="top left")
    fig.update_traces(textposition="outside")
    fig.update_layout(**base_layout(height=380), showlegend=False,
                      xaxis_tickangle=-30, yaxis_range=[0, 24])
    st.plotly_chart(fig, use_container_width=True)

    section_title("📐 Net Run Rate (NRR)")
    nrr_sorted = pts.sort_values("NRR", ascending=False)
    colors = [ACCENT if v >= 0 else "#9CA3AF" for v in nrr_sorted["NRR"]]
    fig2 = go.Figure(go.Bar(
        x=nrr_sorted["Team"], y=nrr_sorted["NRR"],
        marker_color=colors,
        text=[f"{v:+.3f}" for v in nrr_sorted["NRR"]],
        textposition="outside",
    ))
    fig2.add_hline(y=0, line_color="#6B7280", line_width=1)
    fig2.update_layout(**base_layout(height=360,
                                     title="Net Run Rate – Positive vs Negative"),
                       showlegend=False, xaxis_tickangle=-30)
    st.plotly_chart(fig2, use_container_width=True)

    section_title("🥊 Playoff Bracket")
    st.markdown("""
    <div style='background:#FFFFFF;border-radius:12px;padding:22px 28px;
                font-size:14px;line-height:2.2;border:1px solid #E5E7EB;
                box-shadow:0 2px 8px rgba(0,0,0,0.06);'>
        <b style='color:#6B7280;font-size:12px;letter-spacing:1px;'>QUALIFIER 1</b><br>
        <span style='color:#1A1A2E;'>Gujarat Titans vs Rajasthan Royals
        → <span style='color:#FF6B35;font-weight:700;'>Gujarat Titans ✅ (advanced to Final)</span></span><br><br>
        <b style='color:#6B7280;font-size:12px;letter-spacing:1px;'>ELIMINATOR</b><br>
        <span style='color:#1A1A2E;'>Lucknow Super Giants vs Royal Challengers Bangalore
        → <span style='color:#FF6B35;font-weight:700;'>RCB ✅</span></span><br><br>
        <b style='color:#6B7280;font-size:12px;letter-spacing:1px;'>QUALIFIER 2</b><br>
        <span style='color:#1A1A2E;'>Rajasthan Royals vs RCB
        → <span style='color:#FF6B35;font-weight:700;'>Rajasthan Royals ✅ (advanced to Final)</span></span><br><br>
        <hr style='border-color:#E5E7EB;'/>
        <b style='color:#6B7280;font-size:12px;letter-spacing:1px;'>FINAL · Narendra Modi Stadium, Ahmedabad</b><br>
        <span style='color:#1A1A2E;'>Gujarat Titans vs Rajasthan Royals</span><br>
        🏆 <span style='color:#FF6B35;font-size:20px;font-weight:800;'>
            Gujarat Titans WON by 7 wickets
        </span><br>
        <span style='color:#6B7280;font-size:12px;'>Player of the Match: HH Pandya</span>
    </div>
    """, unsafe_allow_html=True)

    section_title("🔎 Dataset Wins vs Official Wins")
    wins_data = df["WinningTeam"].value_counts().reset_index()
    wins_data.columns = ["Team", "DataWins"]
    compare = pts.merge(wins_data, on="Team", how="left")
    compare["DataWins"] = compare["DataWins"].fillna(0).astype(int)
    compare["Match"] = compare["W"] == compare["DataWins"]
    st.dataframe(
        compare[["Team","W","DataWins","Match"]].rename(
            columns={"W":"Official W","DataWins":"Dataset W","Match":"✅ Matches"}
        ),
        use_container_width=True, hide_index=True
)
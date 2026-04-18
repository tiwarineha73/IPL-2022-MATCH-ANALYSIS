import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.styles import inject_css, section_title, base_layout, TEAM_COLORS, ACCENT, ACCENT2


def render(df: pd.DataFrame):
    inject_css()
    st.markdown("## 💡 Insights & Conclusions")

    # ── Numeric correlation heatmap ───────────────────────────────────
    section_title("🔗 Feature Correlation Heatmap")

    num = df.copy()
    num["TossWinMatchWin_int"] = num["TossWinMatchWin"].astype(int)
    num["WonAfterLosingToss_int"] = num["WonAfterLosingToss"].astype(int)
    num["TossDecision_int"] = (num["TossDecision"] == "field").astype(int)
    num["WonByRuns"] = (num["WonBy"] == "Runs").astype(int)

    cols = ["Margin","TossWinMatchWin_int","WonAfterLosingToss_int",
            "TossDecision_int","WonByRuns"]
    labels = ["Margin","TossWinMatchWin","WonAfterLosingToss",
              "FieldDecision","WonByRuns"]

    corr = num[cols].dropna().corr()
    corr.index   = labels
    corr.columns = labels

    fig = px.imshow(
        corr, color_continuous_scale="RdBu", zmin=-1, zmax=1,
        template="plotly_dark", text_auto=".2f",
    )
    fig.update_layout(**base_layout(height=420, title="Correlation Matrix"))
    st.plotly_chart(fig, use_container_width=True)

    # ── Multi-team radar ──────────────────────────────────────────────
    section_title("📡 Multi-Team Radar Comparison")

    t1c = df["Team1"].value_counts()
    t2c = df["Team2"].value_counts()
    played = t1c.add(t2c, fill_value=0)
    wins   = df["WinningTeam"].value_counts()
    toss_w = df["TossWinner"].value_counts()
    wlt    = df[df["WonAfterLosingToss"]]["WinningTeam"].value_counts()

    def radar_vals(team):
        p  = played.get(team, 1)
        w  = wins.get(team, 0)
        tw = toss_w.get(team, 0)
        wl = wlt.get(team, 0)
        potm = (df["Player_of_Match"].value_counts()
                .reset_index().pipe(
                    lambda d: d[d["Player_of_Match"].str.contains("", na=False)]
                ))
        # approximate: count POTM from team rosters
        t1_pm = df[df["Team1"]==team]["Player_of_Match"].notna().sum()
        t2_pm = df[df["Team2"]==team]["Player_of_Match"].notna().sum()
        team_potm = t1_pm + t2_pm
        return {
            "Win %":          round(w / p * 100, 1),
            "Toss Win %":     round(tw / p * 100, 1),
            "Win After Loss %": round(wl / p * 100, 1),
            "POTM Matches %": round(team_potm / p * 100, 1),
            "Matches Played": int(p),
        }

    all_teams = sorted(df["Team1"].unique())
    sel_teams = st.multiselect(
        "Choose teams to compare (2-5 recommended)",
        all_teams,
        default=all_teams[:4],
    )

    if len(sel_teams) < 2:
        st.warning("Select at least 2 teams.")
    else:
        cats = ["Win %","Toss Win %","Win After Loss %","POTM Matches %","Matches Played"]
        fig2 = go.Figure()
        for team in sel_teams:
            rv = radar_vals(team)
            vals = [rv[c] for c in cats] + [rv[cats[0]]]
            clr = TEAM_COLORS.get(team, ACCENT)
            rgb = f"{int(clr[1:3],16)},{int(clr[3:5],16)},{int(clr[5:7],16)}"
            fig2.add_trace(go.Scatterpolar(
                r=vals, theta=cats + [cats[0]],
                fill="toself", name=team,
                line_color=clr,
                fillcolor=f"rgba({rgb},0.12)",
            ))
        fig2.update_layout(
            **base_layout(height=500, title="Team Comparison Radar"),
            polar=dict(
                bgcolor="#1E2130",
                radialaxis=dict(visible=True, color="#8899AA"),
                angularaxis=dict(color="#8899AA"),
            ),
            legend=dict(orientation="h", y=-0.2),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Umpire analysis ────────────────────────────────────────────────
    section_title("🧑‍⚖️ Most Active Umpires")
    umpires = pd.concat([df["Umpire1"], df["Umpire2"]]).value_counts().reset_index()
    umpires.columns = ["Umpire", "Matches"]
    fig3 = px.bar(
        umpires.head(10), x="Umpire", y="Matches",
        color="Matches", color_continuous_scale="Blues",
        template="plotly_dark",
    )
    fig3.update_layout(**base_layout(height=340),
                       showlegend=False, coloraxis_showscale=False,
                       xaxis_tickangle=-30)
    st.plotly_chart(fig3, use_container_width=True)

    # ── Matches per day ────────────────────────────────────────────────
    section_title("📅 Matches Per Day")
    mpd = df["Date"].value_counts().reset_index()
    mpd.columns = ["Date", "Matches"]
    mpd = mpd.sort_values("Date")
    mpd["DateStr"] = mpd["Date"].dt.strftime("%d %b")
    double_headers = mpd[mpd["Matches"] > 1]
    st.markdown(f"**Double-headers:** {len(double_headers)} days had 2 matches on the same day.")
    fig4 = px.bar(mpd, x="DateStr", y="Matches",
                  color="Matches",
                  color_discrete_sequence=[ACCENT],
                  template="plotly_dark")
    fig4.update_layout(**base_layout(height=320), xaxis_tickangle=-45,
                       showlegend=False)
    st.plotly_chart(fig4, use_container_width=True)

    # ── Key conclusions ────────────────────────────────────────────────
    section_title("📝 Key Conclusions")
    conclusions = [
        ("🏆 Champion",        "Gujarat Titans won IPL 2022, beating Rajasthan Royals by 7 wickets in the Final."),
        ("🎲 Toss Impact",     "Teams choosing to field first won ~56% of their matches — chasing is the dominant strategy."),
        ("💪 Mental Strength", "Several teams won multiple matches after losing the toss, proving quality overcomes luck."),
        ("🌟 Star Power",      "HH Pandya was the standout performer, winning POTM in the Final and finishing as a top POTM winner."),
        ("🏟️ Venue",          "Mumbai-based venues (Brabourne, DY Patil, Wankhede) hosted the most matches of the season."),
        ("📊 Consistency",     "Win-rate difference between teams was the single most predictive ML feature (~40% importance)."),
        ("📏 Margins",         "Wicket-based wins slightly outnumber run-based wins — teams prefer chasing and finishing with wickets in hand."),
    ]
    for icon_title, text in conclusions:
        st.markdown(f"""
        <div style='background:#1E2130;border-radius:10px;padding:14px 18px;
                    margin-bottom:10px;border-left:4px solid #FF6B35;'>
            <b>{icon_title}</b><br>
            <span style='color:#CCCCCC;font-size:14px;'>{text}</span>
        </div>""", unsafe_allow_html=True)

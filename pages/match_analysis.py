import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.styles import inject_css, section_title, base_layout, TEAM_COLORS, ACCENT, ACCENT2


def render(df: pd.DataFrame):
    inject_css()
    st.markdown("## 📊 Match Analysis")

    # ── Filters ──────────────────────────────────────────────────────
    all_teams = sorted(df["Team1"].unique())
    c1, c2, c3 = st.columns(3)
    with c1:
        sel_team = st.selectbox("Team", ["All"] + all_teams)
    with c2:
        sel_toss = st.selectbox("Toss Decision", ["All", "bat", "field"])
    with c3:
        sel_wonby = st.selectbox("Won By", ["All", "Runs", "Wickets"])

    filt = df.copy()
    if sel_team  != "All":
        filt = filt[(filt["Team1"]==sel_team)|(filt["Team2"]==sel_team)]
    if sel_toss  != "All":
        filt = filt[filt["TossDecision"]==sel_toss]
    if sel_wonby != "All":
        filt = filt[filt["WonBy"]==sel_wonby]

    st.caption(f"Showing **{len(filt)}** of {len(df)} matches")

    # ── Match cards ──────────────────────────────────────────────────
    section_title("🃏 Match Cards")
    for _, r in filt.head(15).iterrows():
        clr = TEAM_COLORS.get(r.get("WinningTeam",""), ACCENT)
        opp = r["Team2"] if r.get("WinningTeam") == r["Team1"] else r["Team1"]
        date_str = r["Date"].strftime("%d %b") if pd.notna(r["Date"]) else ""
        st.markdown(f"""
        <div style='background:#FFFFFF;border-radius:10px;padding:13px 18px;
                    margin-bottom:9px;border-left:4px solid {clr};'>
            <span style='font-size:15px;font-weight:700;'>{r["Team1"]} vs {r["Team2"]}</span>
            &nbsp;<span style='color:#6B7280;font-size:12px;'>{date_str} · {r["Venue"].split(",")[0]}</span><br>
            🏆 <b>{r.get("WinningTeam","TBD")}</b> won by {int(r["Margin"]) if pd.notna(r["Margin"]) else "?"} {r["WonBy"]}
            &nbsp;·&nbsp; 🌟 {r.get("Player_of_Match","")}
        </div>""", unsafe_allow_html=True)

    # ── Charts row ───────────────────────────────────────────────────
    ca, cb = st.columns(2)

    with ca:
        section_title("🎲 Toss Decision Split")
        td = filt["TossDecision"].value_counts().reset_index()
        td.columns = ["Decision","Count"]
        fig = px.pie(td, names="Decision", values="Count",
                     color_discrete_sequence=[ACCENT, ACCENT2],
                     hole=0.42, template="plotly_white")
        fig.update_layout(**base_layout(height=300))
        st.plotly_chart(fig, use_container_width=True)

    with cb:
        section_title("📏 Margin Distribution")
        m = filt.dropna(subset=["Margin"])
        fig2 = px.histogram(m, x="Margin", color="WonBy",
                            color_discrete_sequence=[ACCENT, ACCENT2],
                            nbins=18, barmode="overlay",
                            template="plotly_white")
        fig2.update_layout(**base_layout(height=300))
        st.plotly_chart(fig2, use_container_width=True)

    # ── Toss advantage ───────────────────────────────────────────────
    section_title("🎯 Toss Winner → Match Winner?")
    ta = filt["TossWinMatchWin"].value_counts().reset_index()
    ta.columns = ["Result","Count"]
    ta["Result"] = ta["Result"].map({True:"Toss winner WON", False:"Toss winner LOST"})
    fig3 = px.bar(ta, x="Result", y="Count",
                  color="Result",
                  color_discrete_sequence=[ACCENT, "#555"],
                  template="plotly_white")
    fig3.update_layout(**base_layout(height=320), showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

    # ── Toss effectiveness by decision ───────────────────────────────
    section_title("📐 Toss Win-Rate by Decision (full season)")
    te = (
        df.groupby("TossDecision")["TossWinMatchWin"]
        .mean().mul(100).round(1).reset_index()
    )
    te.columns = ["Decision","Win %"]
    fig4 = px.bar(te, x="Decision", y="Win %",
                  color="Decision",
                  color_discrete_sequence=[ACCENT, ACCENT2],
                  text="Win %", template="plotly_white")
    fig4.update_traces(texttemplate="%{text}%", textposition="outside")
    fig4.update_layout(**base_layout(height=300), showlegend=False, yaxis_range=[0,80])
    st.plotly_chart(fig4, use_container_width=True)

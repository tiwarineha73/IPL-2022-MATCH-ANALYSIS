import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedKFold, cross_val_score
from utils import inject_css, section_title, metric_card, base_layout, TEAM_COLORS, ACCENT, ACCENT2


# ── Feature engineering ──────────────────────────────────────────────
def build_features(df: pd.DataFrame):
    d = df.dropna(subset=["WinningTeam"]).copy()

    le_team  = LabelEncoder()
    le_toss  = LabelEncoder()
    le_dec   = LabelEncoder()
    le_venue = LabelEncoder()

    all_teams = sorted(pd.concat([d["Team1"], d["Team2"]]).unique())
    le_team.fit(all_teams)

    d["Team1_enc"]      = le_team.transform(d["Team1"])
    d["Team2_enc"]      = le_team.transform(d["Team2"])
    d["TossWinner_enc"] = le_team.transform(d["TossWinner"])
    d["TossDecision_enc"] = le_dec.fit_transform(d["TossDecision"])
    d["Venue_enc"]      = le_venue.fit_transform(d["Venue"])

    # Win-rate feature
    wins   = d["WinningTeam"].value_counts()
    played = pd.concat([d["Team1"], d["Team2"]]).value_counts()
    wr     = (wins / played).fillna(0)
    d["T1_WinRate"]   = d["Team1"].map(wr).fillna(0)
    d["T2_WinRate"]   = d["Team2"].map(wr).fillna(0)
    d["WinRateDiff"]  = d["T1_WinRate"] - d["T2_WinRate"]
    d["TossToTeam1"]  = (d["TossWinner"] == d["Team1"]).astype(int)

    d["Target"] = (d["WinningTeam"] == d["Team1"]).astype(int)

    FEATURES = ["Team1_enc","Team2_enc","TossWinner_enc","TossDecision_enc",
                "Venue_enc","T1_WinRate","T2_WinRate","WinRateDiff","TossToTeam1"]

    return d, FEATURES, le_team, le_dec, le_venue, wr


@st.cache_resource
def train_models(df: pd.DataFrame):
    d, FEATURES, le_team, le_dec, le_venue, wr = build_features(df)
    X = d[FEATURES].values
    y = d["Target"].values

    gb = GradientBoostingClassifier(n_estimators=300, max_depth=3, random_state=42)
    rf = RandomForestClassifier(n_estimators=300, max_depth=4, random_state=42)

    gb.fit(X, y)
    rf.fit(X, y)

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    gb_cv = cross_val_score(gb, X, y, cv=skf, scoring="accuracy").mean()
    rf_cv = cross_val_score(rf, X, y, cv=skf, scoring="accuracy").mean()

    return gb, rf, gb_cv, rf_cv, FEATURES, le_team, le_dec, le_venue, wr


def render(df: pd.DataFrame):
    inject_css()
    st.markdown("## 🔮 Match Prediction")
    st.markdown(
        "<p style='color:#8899AA;'>Uses GradientBoosting + RandomForest trained on IPL 2022 "
        "match-level features. Win-rate difference is the strongest predictor.</p>",
        unsafe_allow_html=True,
    )

    with st.spinner("Training models…"):
        gb, rf, gb_cv, rf_cv, FEATURES, le_team, le_dec, le_venue, wr = train_models(df)

    # ── Model accuracy ────────────────────────────────────────────────
    c1, c2 = st.columns(2)
    with c1: metric_card("Gradient Boosting CV Acc.", f"{gb_cv*100:.1f}%")
    with c2: metric_card("Random Forest CV Acc.",     f"{rf_cv*100:.1f}%")

    # ── Predict form ──────────────────────────────────────────────────
    section_title("🎯 Predict a Match")
    all_teams = sorted(pd.concat([df["Team1"], df["Team2"]]).unique())
    venues    = sorted(df["Venue"].unique())

    col1, col2 = st.columns(2)
    with col1:
        team1 = st.selectbox("Team 1 (batting side reference)", all_teams, index=0)
    with col2:
        team2 = st.selectbox("Team 2", [t for t in all_teams if t != team1], index=0)

    col3, col4 = st.columns(2)
    with col3:
        toss_winner = st.selectbox("Toss Winner", [team1, team2])
    with col4:
        toss_decision = st.selectbox("Toss Decision", ["bat", "field"])

    venue = st.selectbox("Venue", venues)

    if st.button("🔮 Predict Winner", use_container_width=True):
        # encode
        t1_enc  = le_team.transform([team1])[0]
        t2_enc  = le_team.transform([team2])[0]
        tw_enc  = le_team.transform([toss_winner])[0]
        td_enc  = le_dec.transform([toss_decision])[0]

        # venue encoder may not have seen all venues — handle gracefully
        if venue in le_venue.classes_:
            v_enc = le_venue.transform([venue])[0]
        else:
            v_enc = 0

        t1_wr = wr.get(team1, 0)
        t2_wr = wr.get(team2, 0)
        toss_to_t1 = int(toss_winner == team1)

        X_pred = np.array([[t1_enc, t2_enc, tw_enc, td_enc, v_enc,
                            t1_wr, t2_wr, t1_wr - t2_wr, toss_to_t1]])

        gb_prob = gb.predict_proba(X_pred)[0]
        rf_prob = rf.predict_proba(X_pred)[0]
        avg_prob = (gb_prob + rf_prob) / 2

        t1_pct = avg_prob[1] * 100
        t2_pct = avg_prob[0] * 100
        winner = team1 if t1_pct >= 50 else team2
        win_pct = max(t1_pct, t2_pct)

        clr = TEAM_COLORS.get(winner, ACCENT)
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#1E2130,#252B3B);
                    border-radius:14px;padding:24px 28px;border-left:5px solid {clr};
                    margin-top:16px;text-align:center;'>
            <p style='color:#8899AA;font-size:13px;margin:0;'>Predicted Winner</p>
            <p style='font-size:32px;font-weight:800;color:{clr};margin:8px 0 4px;'>{winner}</p>
            <p style='font-size:18px;color:#FAFAFA;margin:0;'>Win probability: {win_pct:.1f}%</p>
        </div>""", unsafe_allow_html=True)

        # probability bar
        fig = go.Figure(go.Bar(
            x=[team1, team2],
            y=[t1_pct, t2_pct],
            marker_color=[TEAM_COLORS.get(team1, ACCENT), TEAM_COLORS.get(team2, ACCENT2)],
            text=[f"{t1_pct:.1f}%", f"{t2_pct:.1f}%"],
            textposition="outside",
        ))
        fig.update_layout(
            **base_layout(height=300, title="Ensemble Win Probability"),
            showlegend=False, yaxis_range=[0, 105],
        )
        st.plotly_chart(fig, use_container_width=True)

        # individual model breakdown
        st.markdown("**Model breakdown:**")
        mc1, mc2 = st.columns(2)
        with mc1:
            metric_card("GB – " + team1, f"{gb_prob[1]*100:.1f}%")
            metric_card("GB – " + team2, f"{gb_prob[0]*100:.1f}%")
        with mc2:
            metric_card("RF – " + team1, f"{rf_prob[1]*100:.1f}%")
            metric_card("RF – " + team2, f"{rf_prob[0]*100:.1f}%")

    # ── Feature importance ────────────────────────────────────────────
    section_title("📊 Feature Importance (Gradient Boosting)")
    fi = pd.DataFrame({
        "Feature":   FEATURES,
        "Importance": gb.feature_importances_,
    }).sort_values("Importance", ascending=True)

    fig2 = px.bar(fi, x="Importance", y="Feature", orientation="h",
                  color="Importance", color_continuous_scale="Oranges",
                  template="plotly_dark")
    fig2.update_layout(**base_layout(height=380),
                       showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig2, use_container_width=True)

    # ── Team win rates ────────────────────────────────────────────────
    section_title("📈 Team Win Rates Used as Features")
    wr_df = wr.reset_index()
    wr_df.columns = ["Team", "WinRate"]
    wr_df = wr_df.sort_values("WinRate", ascending=False)
    wr_df["WinRate %"] = (wr_df["WinRate"] * 100).round(1)

    fig3 = px.bar(wr_df, x="Team", y="WinRate %",
                  color="Team", color_discrete_map=TEAM_COLORS,
                  template="plotly_dark")
    fig3.update_layout(**base_layout(height=360), showlegend=False, xaxis_tickangle=-30)
    st.plotly_chart(fig3, use_container_width=True)

import pandas as pd
import streamlit as st


@st.cache_data
def load_data(path: str = "IPL_Matches_2022.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df["Margin"] = pd.to_numeric(df["Margin"], errors="coerce")
    # Derived columns used across pages
    df["TossWinMatchWin"]   = df["TossWinner"] == df["WinningTeam"]
    df["WonAfterLosingToss"]= df["WinningTeam"] != df["TossWinner"]
    df["WinMethod"]         = df["WonBy"].apply(
        lambda x: "Chasing" if x == "Wickets" else "Defending"
    )
    return df


def team_stats(df: pd.DataFrame) -> pd.DataFrame:
    t1 = df["Team1"].value_counts()
    t2 = df["Team2"].value_counts()
    matches = t1.add(t2, fill_value=0).reset_index()
    matches.columns = ["Team", "Matches"]

    wins = df["WinningTeam"].value_counts().reset_index()
    wins.columns = ["Team", "Wins"]

    stats = matches.merge(wins, on="Team", how="left")
    stats["Wins"]    = stats["Wins"].fillna(0).astype(int)
    stats["Matches"] = stats["Matches"].astype(int)
    stats["Losses"]  = stats["Matches"] - stats["Wins"]
    stats["Win %"]   = (stats["Wins"] / stats["Matches"] * 100).round(2)
    return stats.sort_values("Wins", ascending=False).reset_index(drop=True)


def toss_effectiveness(df: pd.DataFrame) -> pd.DataFrame:
    te = (
        df.groupby("TossDecision")["TossWinMatchWin"]
        .mean().reset_index()
    )
    te.columns = ["TossDecision", "WinRate"]
    te["WinRate"] = (te["WinRate"] * 100).round(2)
    return te


def potm_leaderboard(df: pd.DataFrame) -> pd.DataFrame:
    p = df["Player_of_Match"].value_counts().reset_index()
    p.columns = ["Player", "Awards"]
    return p

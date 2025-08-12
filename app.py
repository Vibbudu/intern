# streamlit_app.py
import streamlit as st
import requests
import pandas as pd
import time
from pyvis.network import Network
import tempfile
import os
import plotly.express as px  

st.set_page_config(page_title="NBA Dashboard", layout="wide")
API_BASE = st.sidebar.text_input("API Base URL", value="http://localhost:8000")

st.title("NBA Advanced Dashboard")


st.sidebar.header("Controls")
tab = st.sidebar.radio("Page", ["Overview", "Players", "Teams", "Performance", "Compare", "Network"]) 


def fetch(endpoint: str, params=None): 
    try:
        resp = requests.get(f"{API_BASE}{endpoint}", params=params, timeout=6)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"API error: {e}")
        return None


if tab == "Overview":
    st.header("Overview")
    players = fetch("/players?limit=100")
    teams = fetch("/teams")
    coaches = fetch("/coaches?limit=100")
    if players is None: 
        st.stop()

    df_players = pd.DataFrame(players)
    col1, col2, col3 = st.columns(3)
    col1.metric("Players", len(df_players))
    col2.metric("Teams", len(teams) if teams else 0)
    col3.metric("Coaches", len(coaches) if coaches else 0)

    st.subheader("Players table")
    st.dataframe(df_players)

    st.subheader("Height vs Weight scatter (interactive)")
    fig = px.scatter(df_players, x="height", y="weight", hover_name="name")
    st.plotly_chart(fig, use_container_width=True)

if tab == "Players":
    st.header("Players")

    # Choose search method
    search_type = st.radio("Search by", ["Name", "Number"], horizontal=True)

    # ---- Search by Name ----
    if search_type == "Name":
        search_name = st.text_input("Enter player name (partial)")
        if st.button("Search by Name"):
            res = fetch("/search/players", params={"q": search_name})
            if res:
                df_search = pd.DataFrame(res)
                st.subheader(f"Search Results for '{search_name}'")
                st.dataframe(df_search)

                if len(df_search) == 1:
                    # Auto-load if only one player found
                    player_number = df_search.iloc[0]["number"]
                    p = fetch(f"/player/{player_number}")
                    if p:
                        st.subheader(f"Details for Player #{player_number}")
                        st.table(pd.DataFrame([p]))
                elif len(df_search) > 1:
                    # Show dropdown only if multiple results
                    player_choice = st.selectbox(
                        "Select player by number from results",
                        options=df_search["number"].unique()
                    )
                    if st.button("Load Player Details"):
                        p = fetch(f"/player/{player_choice}")
                        if p:
                            st.subheader(f"Details for Player #{player_choice}")
                            st.table(pd.DataFrame([p]))
            else:
                st.warning("No players found.")

    # ---- Search by Number ----
    elif search_type == "Number":
        search_number = st.number_input("Enter player jersey number", min_value=0, step=1)
        if st.button("Search by Number"):
            p = fetch(f"/player/{search_number}")
            if p:
                st.subheader(f"Details for Player #{search_number}")
                st.table(pd.DataFrame([p]))
            else:
                st.warning("No player found with that number.")


if tab == "Teams":
    st.header("Teams & Rosters")
    tms = fetch("/teams")
    if tms:
        for t in tms:
            with st.expander(t["team"]):
                # Show Players Table
                players = t.get("players", [])
                if players:
                    st.subheader("Players")
                    df_players = pd.DataFrame(players)
                    st.dataframe(df_players)
                else:
                    st.info("No players listed for this team.")

                # Show Coaches Table
                coaches = t.get("coaches", [])
                if coaches:
                    st.subheader("Coaches")
                    df_coaches = pd.DataFrame(coaches)
                    st.dataframe(df_coaches)
                else:
                    st.info("No coaches listed for this team.")

                # Button to view detailed roster from API
                if st.button(f"View roster: {t['team']}", key=f"roster_{t['team']}"):
                    roster = fetch(f"/team/{t['team']}")
                    if roster:
                        roster_players = roster.get("players", [])
                        if roster_players:
                            st.subheader(f"{t['team']} - Detailed Roster")
                            st.dataframe(pd.DataFrame(roster_players))
                        else:
                            st.warning("No roster data available.")



if tab == "Performance":
    st.header("Player Performance vs Teams")

    number = st.number_input("Player jersey number", min_value=0, step=1, value=6)
    
    if st.button("Show Performance"):
        hist = fetch(f"/player/{number}/performance")
        if hist:
            dfh = pd.DataFrame(hist)

            if dfh.empty:
                st.warning("No performance data found for this player.")
            else:
                # Summary metrics
                col1, col2, col3 = st.columns(3)
                col1.metric("Average Points", round(dfh["points"].mean(), 2))
                col2.metric("Average Assists", round(dfh["assists"].mean(), 2))
                col3.metric("Average Rebounds", round(dfh["rebounds"].mean(), 2))

                # Performance table
                st.subheader("Game-by-Game Performance")
                st.dataframe(dfh)

                # Bar chart: Points vs Opponent
                st.subheader("Points Scored vs Opponent")
                fig_bar = px.bar(
                    dfh, x="opponent", y="points",
                    title=f"Points scored by Player #{number} against each team",
                    color="points", color_continuous_scale="Blues"
                )
                st.plotly_chart(fig_bar, use_container_width=True)

                # Line chart: Points trend
                st.subheader("Performance Trend Over Time")
                if "game_date" in dfh.columns:
                    fig_line = px.line(
                        dfh.sort_values("game_date"), 
                        x="game_date", y="points",
                        title="Points Trend Over Games",
                        markers=True
                    )
                else:
                    fig_line = px.line(
                        dfh.reset_index().rename(columns={"index": "game_number"}),
                        x="game_number", y="points",
                        title="Points Trend Over Games (by game number)",
                        markers=True
                    )
                st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.warning("No performance data available for this player.")



if tab == "Compare":
    st.header("Compare Two Players")

    n1 = st.number_input("Player 1 number", min_value=0, value=6)
    n2 = st.number_input("Player 2 number", min_value=0, value=7)

    if st.button("Compare"):
        res = fetch("/compare", params={"n1": n1, "n2": n2})
        if res and "players" in res:
            dfc = pd.DataFrame(res["players"])
            
            if not dfc.empty:
                # Split into two columns for player cards
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader(dfc.iloc[0]["name"])
                    st.table(dfc.iloc[[0]][["points", "assists", "rebounds"]])

                with col2:
                    st.subheader(dfc.iloc[1]["name"])
                    st.table(dfc.iloc[[1]][["points", "assists", "rebounds"]])

                # Highlight stat winners
                st.subheader("Stat Winners")
                winners = {}
                for stat in ["points", "assists", "rebounds"]:
                    if dfc.iloc[0][stat] > dfc.iloc[1][stat]:
                        winners[stat] = dfc.iloc[0]["name"]
                    elif dfc.iloc[0][stat] < dfc.iloc[1][stat]:
                        winners[stat] = dfc.iloc[1]["name"]
                    else:
                        winners[stat] = "Tie"

                for stat, winner in winners.items():
                    st.write(f"🏆 **{stat.capitalize()}**: {winner}")

                # Bar chart comparison
                st.subheader("Comparison Chart")
                fig = px.bar(
                    dfc.set_index("name")[["points", "assists", "rebounds"]],
                    barmode="group",
                    title="Player Stats Comparison"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No comparison data available.")
        else:
            st.warning("Could not fetch comparison data.")


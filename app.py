import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from rapidfuzz import process, fuzz
import pandas as pd

# Cache all players so we don't fetch repeatedly
@st.cache_data
def get_all_players():
    res = fetch("/players")  # API endpoint returning all players
    return pd.DataFrame(res) if res else pd.DataFrame()

# ---------------- CONFIG ----------------
st.set_page_config(page_title="🏀 NBA Advanced Dashboard", layout="wide")

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
/* General App Styling */
.main {
    background-color: #fafafa; /* Softer white */
    padding: 0;
    font-family: 'Segoe UI', sans-serif;
}

/* Top Navigation Bar */
.top-bar {
    background-color: #0b1e36;
    color: white;
    padding: 0.8rem 2rem;
    display: flex;
    justify-content: center; /* Center everything */
    align-items: center;
    gap: 1.5rem;
    position: sticky;
    top: 0;
    z-index: 1000;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.15);
}

.nav-buttons button {
    background-color: transparent;
    border: none;
    color: white;
    font-size: 1.1rem;
    padding: 0.5rem 1rem;
    cursor: pointer;
    transition: 0.3s;
    border-radius: 6px;
}
.nav-buttons button:hover {
    background-color: rgba(255, 255, 255, 0.15);
}

/* Metric Cards */
.metric-card {
    background: white;
    border-radius: 12px;
    padding: 1.2rem;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
    text-align: center;
    margin: 0.5rem;
}
.metric-value {
    font-size: 1.8rem;
    font-weight: bold;
    color: #ff7f50;
}
.metric-label {
    font-size: 1rem;
    color: #555;
}

/* DataFrame Styling */
.stDataFrame {
    border-radius: 8px;
    overflow: hidden;
    background-color: white;
}

/* Add spacing between sections */
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)


# ---------------- API BASE ----------------
API_BASE = "http://localhost:8000"

# ---------------- API FETCH ----------------
def fetch(endpoint: str, params=None):
    try:
        resp = requests.get(f"{API_BASE}{endpoint}", params=params, timeout=6)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"❌ API error: {e}")
        return None

# ---------------- NAVIGATION ----------------
if "page" not in st.session_state:
    st.session_state.page = "Overview"

def nav_button(label, page):
    if st.button(label, key=page):
        st.session_state.page = page

st.markdown('<div class="top-bar"><div class="nav-buttons">', unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns([1,1,1,1,5])
with col1: nav_button("🏠 Overview", "Overview")
with col2: nav_button("👤 Players", "Players")
with col3: nav_button("🏢 Teams", "Teams")
with col4: nav_button("📊 Performance", "Performance")
with col5: nav_button("⚖️ Compare", "Compare")
st.markdown('</div></div>', unsafe_allow_html=True)

# ---------------- PAGES ----------------
if st.session_state.page == "Overview":
    st.subheader("📊 Quick NBA Stats")
    players = fetch("/players?limit=100")
    teams = fetch("/teams")
    coaches = fetch("/coaches?limit=100")
    if not players: st.stop()

    df_players = pd.DataFrame(players)

    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='metric-card'><div class='metric-value'>{len(df_players)}</div><div class='metric-label'>Players</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric-card'><div class='metric-value'>{len(teams) if teams else 0}</div><div class='metric-label'>Teams</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-card'><div class='metric-value'>{len(coaches) if coaches else 0}</div><div class='metric-label'>Coaches</div></div>", unsafe_allow_html=True)

    st.markdown("### 📋 Players Table")
    st.dataframe(df_players, use_container_width=True)

    st.markdown("### 📐 Height vs Weight Scatter")
    fig = px.scatter(df_players, x="height", y="weight", hover_name="name", color="height", color_continuous_scale="bluered")
    st.plotly_chart(fig, use_container_width=True)



elif st.session_state.page == "Players":
    st.subheader("🔍 Search Players")
    search_type = st.radio("Search by", ["Name", "Number"], horizontal=True)
    players_df = get_all_players()

    if search_type == "Name":
        name = st.text_input("Enter player name")
        if st.button("Search by Name"):
            if not players_df.empty:
                matches = process.extract(name, players_df['name'], scorer=fuzz.WRatio, limit=5)
                matched_names = [m[0] for m in matches if m[1] > 60]  # Only if similarity > 60%
                filtered = players_df[players_df['name'].isin(matched_names)]
                if not filtered.empty:
                    st.dataframe(filtered, use_container_width=True)
                else:
                    st.warning("No close matches found.")
            else:
                st.error("Could not load player data.")

    else:
        number = st.number_input("Enter jersey number", min_value=0, step=1)
        if st.button("Search by Number"):
            p = fetch(f"/player/{number}")
            if p:
                st.table(pd.DataFrame([p]))
            else:
                st.warning("No player found.")


elif st.session_state.page == "Teams":
    st.subheader("🏢 Teams & Rosters")
    tms = fetch("/teams")
    if tms:
        for t in tms:
            with st.expander(f"🏀 {t['team']}"):
                if t.get("players"): st.dataframe(pd.DataFrame(t["players"]), use_container_width=True)
                if t.get("coaches"): st.dataframe(pd.DataFrame(t["coaches"]), use_container_width=True)

elif st.session_state.page == "Performance":
    st.subheader("📊 Player Performance")
    search_mode = st.radio("Search by:", ["Number", "Name"], horizontal=True)
    if search_mode == "Number":
        number = st.number_input("Enter player number", min_value=0, step=1, value=6)
    else:
        name = st.text_input("Enter player name")

    if st.button("📈 Show Performance"):
        hist = fetch(f"/player/{number}/performance") if search_mode == "Number" else fetch(f"/player/name/{name}/performance")
        if hist:
            dfh = pd.DataFrame(hist)
            if not dfh.empty:
                st.markdown(f"### Stats for {name if search_mode=='Name' else number}")
                st.dataframe(dfh, use_container_width=True)
                fig_bar = px.bar(dfh, x="opponent", y="points", color="points", color_continuous_scale="bluered")
                st.plotly_chart(fig_bar, use_container_width=True)
                if "game_date" in dfh.columns:
                    fig_line = px.line(dfh.sort_values("game_date"), x="game_date", y="points", markers=True)
                else:
                    fig_line = px.line(dfh.reset_index(), x=dfh.index, y="points", markers=True)


elif st.session_state.page == "Compare":
    st.subheader("⚖️ Compare Players")

    players_df = get_all_players()

    col1, col2 = st.columns(2)
    with col1:
        p1_name = st.text_input("Player 1 Name or Number")
    with col2:
        p2_name = st.text_input("Player 2 Name or Number")

    if st.button("Compare Now"):
        def find_best_match(query):
            matches = process.extract(query, players_df['name'], scorer=fuzz.WRatio, limit=1)
            if matches and matches[0][1] > 40:
                return players_df[players_df['name'] == matches[0][0]].iloc[0]
            # Try matching by number
            num_match = players_df[players_df['number'].astype(str) == query]
            return num_match.iloc[0] if not num_match.empty else None

        p1 = find_best_match(p1_name)
        p2 = find_best_match(p2_name)

        if p1 is not None and p2 is not None:
            # Fetch stats from your compare API
            res = fetch("/compare", params={"n1": p1["number"], "n2": p2["number"]})
            if res and "players" in res:
                dfc = pd.DataFrame(res["players"])

                # --- Stat Cards ---
                col1, col2 = st.columns(2)

                # Fill missing values for stats
                dfc[['points', 'assists', 'rebounds']] = dfc[['points', 'assists', 'rebounds']].fillna(0)

                with col1:
                    st.metric("Points", dfc['points'].iloc[0])
                    st.metric("Assists", dfc['assists'].iloc[0])
                    st.metric("Rebounds", dfc['rebounds'].iloc[0])

                with col2:
                    st.metric("Points", dfc['points'].iloc[1])
                    st.metric("Assists", dfc['assists'].iloc[1])
                    st.metric("Rebounds", dfc['rebounds'].iloc[1])
                # --- Grouped Bar Chart ---
                fig_bar = px.bar(
                    dfc.set_index("name")[["points", "assists", "rebounds"]],
                    barmode="group",
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                st.plotly_chart(fig_bar, use_container_width=True)

        else:
            st.warning("One or both players could not be found.")

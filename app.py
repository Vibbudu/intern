# app.py
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from rapidfuzz import process, fuzz

# ---------------- CONFIG ----------------
st.set_page_config(page_title="🏀 NBA Advanced Dashboard", layout="wide", initial_sidebar_state="expanded")

API_BASE = "http://localhost:8000"
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "your_password"

TIMEOUT = 10

# ---------------- UTIL ----------------
def _toast(kind: str, msg: str):
    if kind == "success": st.success(msg)
    elif kind == "warn": st.warning(msg)
    else: st.error(msg)

def _get(path: str, params=None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        _toast("err", f"API error: {e}")
        return None

def _post(path: str, payload: dict):
    try:
        r = requests.post(f"{API_BASE}{path}", json=payload, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        _toast("err", f"API error: {e}")
        return None

def _delete(path: str):
    try:
        r = requests.delete(f"{API_BASE}{path}", timeout=TIMEOUT)
        if r.status_code == 204:
            return {"ok": True}
        r.raise_for_status()
        return r.json()
    except Exception as e:
        _toast("err", f"API error: {e}")
        return None

# ---------------- CACHING LAYERS ----------------
@st.cache_data(ttl=60)
def get_players(limit=1000):
    res = _get("/players", params={"limit": limit}) or []
    return pd.DataFrame(res)

@st.cache_data(ttl=60)
def get_teams():
    return _get("/teams") or []

@st.cache_data(ttl=60)
def get_coaches(limit=1000):
    return _get("/coaches", params={"limit": limit}) or []

@st.cache_data(ttl=60)
def get_top_salaries(limit=20):
    return _get("/salaries/top", params={"limit": limit}) or []

# ---------------- FUZZY PLAYER SEARCH ----------------
def find_best_player(df_players: pd.DataFrame, query: str):
    if df_players.empty: return None
    # Try name fuzzy match
    matches = process.extract(query, df_players['name'], scorer=fuzz.WRatio, limit=1)
    if matches and matches[0][1] >= 70:
        return df_players[df_players['name'] == matches[0][0]].iloc[0].to_dict()
    # Try number direct
    num_match = df_players[df_players['number'].astype(str) == str(query)]
    if not num_match.empty:
        return num_match.iloc[0].to_dict()
    return None

# ---------------- BRANDING HEADER ----------------
st.markdown("""
<style>
.main { 
    background-color: #ffffff; 
    color: #000000; 
}
.big-title {
    font-size: 1.8rem;
    font-weight: 700;
    margin-bottom: .5rem;
    color: #ffffff;
}
.subtle {
    color: #000000;
}
.card {
    background: #ffffff;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 4px 18px rgba(10,22,70,.06);
    color: #000000;
}
.kpi {
    display: flex;
    gap: 12px;
    align-items: center;
    color: #000000;
}
.kpi .val {
    font-size: 1.6rem;
    font-weight: 700;
    color: #000000;
}
.kpi .lbl {
    color: #000000;
}
hr {
    border: none;
    border-top: 1px solid #eee;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🏀 NBA Advanced Dashboard")
page = st.sidebar.radio("Navigate", ["Overview", "Players", "Performance", "Compare", "Teams", "Add Player", "Remove Player", "About"])

# ---------------- PAGES ----------------
if page == "Overview":
    st.markdown("<div class='big-title'>📊 Overview</div>", unsafe_allow_html=True)
    players_df = get_players()
    teams = get_teams()
    coaches = get_coaches()

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"<div class='card kpi'><div class='val'>{len(players_df)}</div><div class='lbl'>Players</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='card kpi'><div class='val'>{len(teams)}</div><div class='lbl'>Teams</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='card kpi'><div class='val'>{len(coaches)}</div><div class='lbl'>Coaches</div></div>", unsafe_allow_html=True)
    if not players_df.empty and 'salary' in players_df:
        total_pay = float(players_df['salary'].fillna(0).sum())
        c4.markdown(f"<div class='card kpi'><div class='val'>${total_pay:,.0f}</div><div class='lbl'>Total Payroll</div></div>", unsafe_allow_html=True)

    st.markdown("### Players")
    st.dataframe(players_df, use_container_width=True)

    if not players_df.empty:
        st.markdown("### Height vs Weight")
        fig = px.scatter(players_df, x="height", y="weight", hover_name="name", color="team")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Salary by Team (Treemap)")
        if 'team' in players_df and 'salary' in players_df:
            treemap_df = players_df.groupby(['team','name'], as_index=False)['salary'].sum()
            fig2 = px.treemap(treemap_df, path=['team','name'], values='salary')
            st.plotly_chart(fig2, use_container_width=True)

elif page == "Players":
    st.markdown("<div class='big-title'>🔎 Players</div>", unsafe_allow_html=True)

    # Fetch all players
    players_df = get_players()

    # Search bar
    q = st.text_input("Search by name or jersey number", placeholder="e.g., LeBron, Curry, 23")

    if q.strip():
        p = find_best_player(players_df, q)

        if p:
            # ✅ Styled Player Card
            st.markdown(
                f"""
                <div style="background-color:#1e1e1e; padding:20px; border-radius:15px; 
                            box-shadow: 0 0 10px rgba(0,0,0,0.5); margin-bottom:20px;">
                    <h2 style="color:#4CAF50; margin-bottom:5px;">
                        {p['name']} <span style="color:gray;">#{p['number']}</span>
                    </h2>
                    <p style="color:#bbbbbb; font-size:14px; margin:3px 0;">
                        <b>Team:</b> {p.get('team','N/A')}
                    </p>
                    <p style="color:#bbbbbb; font-size:14px; margin:3px 0;">
                        <b>Age:</b> {p.get('age','-')} years
                    </p>
                    <p style="color:#bbbbbb; font-size:14px; margin:3px 0;">
                        <b>Height:</b> {p.get('height','-')}
                    </p>
                    <p style="color:#bbbbbb; font-size:14px; margin:3px 0;">
                        <b>Weight:</b> {p.get('weight','-')}
                    </p>
                    <p style="color:#bbbbbb; font-size:14px; margin:3px 0;">
                        <b>Salary:</b> ${p.get('salary',0):,}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.warning("❌ No close match found. Try again.")

    # Show all players table
    st.markdown("### 📋 All Players")
    st.dataframe(
        players_df[["name", "number", "team", "age", "height", "weight", "salary"]],
        use_container_width=True,
        hide_index=True
    )


elif page == "Performance":
    st.markdown("<div class='big-title'>📈 Player Performance</div>", unsafe_allow_html=True)
    players_df = get_players()
    q = st.text_input("Search player by name or jersey number")
    if st.button("Show Performance") and q:
        p = find_best_player(players_df, q)
        if not p:
            st.warning("No close match found.")
        else:
            hist = _get(f"/player/{p['number']}/performance") or []
            dfh = pd.DataFrame(hist)
            if dfh.empty:
                st.warning("No performance records.")
            else:
                st.success(f"Showing performance for {p['name']} (#{p['number']})")
                st.dataframe(dfh, use_container_width=True)
                if "points" in dfh:
                    st.markdown("#### Points by Opponent")
                    st.plotly_chart(px.bar(dfh, x="opponent", y="points"), use_container_width=True)
                if "minutes" in dfh:
                    st.markdown("#### Minutes vs Points")
                    st.plotly_chart(px.scatter(dfh, x="minutes", y="points", hover_name="opponent"), use_container_width=True)
                if "points" in dfh:
                    st.markdown("#### Trend")
                    x_axis = "game_date" if "game_date" in dfh.columns else dfh.reset_index().index
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=dfh.get("game_date", x_axis), y=dfh["points"], mode="lines+markers", name="Points"))
                    st.plotly_chart(fig, use_container_width=True)

elif page == "Compare":
    st.markdown("<div class='big-title'>⚖️ Compare Players</div>", unsafe_allow_html=True)
    players_df = get_players()
    col1, col2 = st.columns(2)
    with col1: q1 = st.text_input("Player 1 (name or number)")
    with col2: q2 = st.text_input("Player 2 (name or number)")

    if st.button("Compare"):
        p1 = find_best_player(players_df, q1) if q1 else None
        p2 = find_best_player(players_df, q2) if q2 else None
        if not (p1 and p2):
            st.warning("Could not find one or both players.")
        else:
            res = _get("/compare", params={"n1": p1["number"], "n2": p2["number"]}) or {}
            plist = res.get("players", [])
            if len(plist) >= 2:
                df = pd.DataFrame(plist)
                st.dataframe(df, use_container_width=True)
                # Grouped bars
                st.plotly_chart(
                    px.bar(df.set_index("name")[ ["points_avg", "assists_avg", "rebounds_avg"] ],
                           barmode="group"),
                    use_container_width=True
                )
                # Radar chart
                radar = go.Figure()
                for _, row in df.iterrows():
                    radar.add_trace(go.Scatterpolar(
                        r=[row["points_avg"], row["assists_avg"], row["rebounds_avg"]],
                        theta=["PPG","APG","RPG"],
                        fill='toself',
                        name=row["name"]
                    ))
                radar.update_layout(polar=dict(radialaxis=dict(visible=True)))
                st.plotly_chart(radar, use_container_width=True)
            else:
                st.warning("Comparison not available.")

elif page == "Teams":
    st.markdown("<div class='big-title'>🏢 Teams & Rosters</div>", unsafe_allow_html=True)
    tms = get_teams()
    if not tms: st.info("No teams found.")
    else:
        team_names = [t['team'] for t in tms]
        sel = st.selectbox("Select a team", team_names)
        roster = next((t for t in tms if t['team'] == sel), None)
        if roster:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### Players")
                st.dataframe(pd.DataFrame({"name": roster["players"]}), use_container_width=True)
            with c2:
                st.markdown("#### Coaches")
                st.dataframe(pd.DataFrame({"name": roster["coaches"]}), use_container_width=True)

        st.markdown("### Top Salaries")
        top_sal = get_top_salaries(12)
        if top_sal:
            df = pd.DataFrame(top_sal)
            st.dataframe(df, use_container_width=True)
            st.plotly_chart(px.bar(df, x="player", y="salary", color="team"), use_container_width=True)

elif page == "Add Player":
    st.markdown("<div class='big-title'>➕ Add Player</div>", unsafe_allow_html=True)
    with st.form("add_player"):
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=15, max_value=50)
        number = st.number_input("Jersey Number", min_value=0)
        height = st.number_input("Height (m)", min_value=1.0, max_value=2.5, step=0.01)
        weight = st.number_input("Weight (kg)", min_value=40.0, max_value=200.0, step=0.1)
        team = st.text_input("Team")
        salary = st.number_input("Salary", min_value=0.0, step=1000.0)
        submitted = st.form_submit_button("Create")
    if submitted:
        payload = {"name": name, "age": age, "number": int(number),
                   "height": float(height), "weight": float(weight),
                   "team": team, "salary": float(salary)}
        res = _post("/player", payload)
        if res: 
            st.cache_data.clear()
            st.success(f"Player {name} added.")

elif page == "Remove Player":
    st.markdown("<div class='big-title'>🗑 Remove Player</div>", unsafe_allow_html=True)
    players_df = get_players()

    if players_df.empty:
        st.warning("No players available.")
    else:
        # Search box for fuzzy lookup
        query = st.text_input("Search player by name or jersey number", placeholder="e.g., LeBron, 23")

        selected_player = None
        if query.strip():
            match = find_best_player(players_df, query)  # 🔍 fuzzy match helper
            if match:
                st.success(f"Found: {match['name']} (#{match['number']}) — {match.get('team','')}")
                selected_player = match
            else:
                st.warning("❌ No close match found.")
        
        # Delete confirmation flow
        if selected_player:
            st.markdown(
                f"""
                <div style="padding:15px; border-radius:10px; background-color:#2a2a2a; margin-top:10px;">
                    <b>Ready to remove:</b> {selected_player['name']} 
                    <span style="color:gray;">(#{selected_player['number']})</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            confirm = st.checkbox("Yes, I really want to delete this player ⚠️")

            if st.button("Delete", type="primary", disabled=not confirm):
                resp = _delete(f"/player/by-number/{selected_player['number']}")
                if resp is not None:
                    st.cache_data.clear()
                    st.success(f"✅ {selected_player['name']} (#{selected_player['number']}) removed successfully.")


elif page == "About":
    st.markdown("""
### ℹ️ About
This dashboard uses **FastAPI + Neo4j** for data and **Streamlit** for UI.
Features:
- Fuzzy player search (Players, Performance, Compare)
- Performance analytics with charts
- Player comparison (PPG/APG/RPG)
- Team & salary visuals
""")

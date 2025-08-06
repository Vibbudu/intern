import streamlit as st
import requests

st.set_page_config(page_title="Basketball DB", layout="centered")

# App title
st.title("🏀 Basketball Database Viewer")

# Initialize session state
if "search_click" not in st.session_state:
    st.session_state.search_click = False

# Create 3 columns for side-by-side buttons
col1, col2, col3 = st.columns(3)

# Show all players
with col1:
    if st.button("Show All Players"):
        with st.spinner("Loading players..."):
            url = "http://localhost:8000/players/"
            resp = requests.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if "players" in data:
                    st.subheader("All Players")
                    for p in data["players"]:
                        st.markdown(f"- **{p['name']}** | Age: {p['age']} | Number: {p['number']}")
                else:
                    st.error("Unexpected format: 'players' key missing")
            else:
                st.error("Failed to fetch players.")

# Show all coaches
with col2:
    if st.button("Show All Coaches"):
        with st.spinner("Loading coaches..."):
            url = "http://localhost:8000/coaches/"
            resp = requests.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if "coaches" in data:
                    st.subheader("All Coaches")
                    for c in data["coaches"]:
                        st.markdown(f"- **{c['name']}**")
                else:
                    st.error("Unexpected format: 'coaches' key missing")
            else:
                st.error("Failed to fetch coaches.")

# Search section (button toggles visibility)
with col3:
    if st.button("Search by Number"):
        st.session_state.search_click = not st.session_state.search_click

# Conditional search input
if st.session_state.search_click:
    number = st.number_input("Enter Jersey Number", min_value=0, step=1)
    if st.button("Search"):
        with st.spinner("Searching..."):
            url = f"http://localhost:8000/player/{number}"
            resp = requests.get(url)
            if resp.status_code == 200:
                player = resp.json()
                if "player" in player and player["player"] and "name" in player["player"]:
                    st.success("Player Found!")
                    st.write(f"**Name:** {player['player']['name']}")

                else:
                    st.error("No player found with that number.")
            else:
                st.error("Error fetching data.")
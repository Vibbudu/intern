import streamlit as st
import requests
import time


st.set_page_config(page_title="Basketball DB", layout="centered")
st.title("Basketball Database Viewer")


col1, col2, col3 = st.columns(3)


API_BASE = "http://localhost:8000"

with col1:
    if st.button("Show All Players"):
        with st.spinner("Loading players..."):
            resp = requests.get(f"{API_BASE}/players")
            if resp.status_code == 200:
                data = resp.json()
                players = data.get("players")
                st.subheader("All Players")
    
                for player in players:
                    st.markdown(f"- {player['name']}")

            else:
                st.error("Failed to fetch players.")        
        
# Show All Coaches
with col2:
    if st.button("Show All Coaches"):
        with st.spinner("Loading coaches..."):
            resp = requests.get(f"{API_BASE}/coaches")
            if resp.status_code == 200:
                data = resp.json()
                coaches = data.get("coaches")
                st.subheader("All Coaches")
                for c in coaches:
                    st.markdown(f"• **{c['name']}**")
            else:
                st.error("Failed to fetch coaches.")

# Search Player by Jersey Number
with col3:
    if st.button("Search by Number"):
        st.session_state.show_search = not st.session_state.get("show_search", False)

if st.session_state.get("show_search", False):
    st.subheader("🔍 Search Player by Number")
    number = st.number_input("Enter Jersey Number", min_value=0, step=1)
    if st.button("Search"):
        start = time.time()
        with st.spinner("Searching..."):
            resp = requests.get(f"{API_BASE}/player/{number}")
            if resp.status_code == 200:
                data = resp.json()
                if "player" in data:
                    player = data["player"]
                    st.success("✅ Player Found")
                    st.write(f"**Name:** {player['name']}")
                    st.write(f"**Age:** {player['age']}")
                    st.write(f"**Height:** {player['height']} m")
                    st.write(f"**Weight:** {player['weight']} kg")
                else:
                    st.warning("No player found with that number.")
                duration = time.time() - start
                st.success(f"Time took to get results: {duration} seconds")

                    
            else:
                st.error("API error occurred.")

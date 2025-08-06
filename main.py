from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import get_all_players, get_all_coaches, get_player_details

app = FastAPI(title="🏀 NBA Player API")

# Allow frontend access (important for Streamlit requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/players")
def fetch_players():
    players = get_all_players()
    return {"players": players}

@app.get("/coaches")
def fetch_coaches():
    coaches = get_all_coaches()
    return {"coaches": coaches}

@app.get("/player/{number}")
def fetch_player(number: int):
    player = get_player_details(number)
    if player:
        return {"player": dict(player)}
    return {"error": "Player not found."}

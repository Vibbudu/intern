from fastapi import FastAPI
from db import get_all_players, get_all_coaches, get_player_details 

app = FastAPI(title=" NBA DASHBOARD")

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
        return {"player": player}
    return {"error": "Player not found."}

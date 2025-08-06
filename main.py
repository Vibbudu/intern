from fastapi import FastAPI
from db import get_all_players
from db import get_all_coaches
from db import get_player_details



import pprint
from fastapi.responses import PlainTextResponse

app = FastAPI(title="NBA Player API")

@app.get("/players")
def fetch_players():
    players = get_all_players()
    return {"players": players}

@app.get("/coaches")
def fetch_coaches():
    coaches = get_all_coaches()
    return {"coaches": coaches}

@app.get("/player/{number}")
def player_full_info(number: int):
    result = get_player_details(number)
    if result:
        return result
    else:
        return {"error": "Player not found."}

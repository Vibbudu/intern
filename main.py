# main.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from db import (
    get_all_players, get_all_coaches, get_player_by_number, get_player_performance,
    get_player_performance_by_name, get_teams, get_team_roster, compare_players,
    get_top_salary, get_teammates_network, search_players_by_name,
    create_player, delete_player_by_name, delete_player_by_number
)
from models import (
    PlayerSummary, CoachSummary, TeamSummary, PerformanceRec, PlayerDetail,
    CompareResponse, PlayerCreate
)

app = FastAPI(title="NBA DASHBOARD API", version="1.1")

# CORS for Streamlit local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/players", response_model=List[PlayerSummary])
def players(limit: int = Query(100, ge=1, le=1000)):
    return get_all_players(limit)

@app.get("/coaches", response_model=List[CoachSummary])
def coaches(limit: int = Query(100, ge=1, le=1000)):
    return get_all_coaches(limit)

@app.get("/player/{number}", response_model=PlayerDetail)
def player_detail(number: int):
    p = get_player_by_number(number)
    if not p:
        raise HTTPException(status_code=404, detail="Player not found")
    return p

@app.get("/player/{number}/performance", response_model=List[PerformanceRec])
def player_perf(number: int):
    return get_player_performance(number)

@app.get("/player/name/{name}/performance", response_model=List[PerformanceRec])
def player_perf_by_name(name: str):
    return get_player_performance_by_name(name)

@app.get("/teams", response_model=List[TeamSummary])
def teams():
    return get_teams()

@app.get("/team/{team_name}")
def team_roster(team_name: str):
    roster = get_team_roster(team_name)
    if not roster:
        raise HTTPException(status_code=404, detail="Team not found")
    return roster

@app.get("/compare", response_model=CompareResponse)
def compare(n1: int, n2: int):
    return compare_players(n1, n2)

@app.get("/salaries/top")
def top_salaries(limit: int = Query(10, ge=1, le=100)):
    return get_top_salary(limit)

@app.get("/player/{number}/teammates")
def teammates(number: int):
    return get_teammates_network(number)

@app.get("/search/players")
def search_players(q: str, limit: int = Query(20, ge=1, le=100)):
    return search_players_by_name(q, limit)

@app.post("/player", response_model=PlayerDetail, status_code=201)
def add_player(player: PlayerCreate):
    new_player = create_player(player.dict())
    if not new_player:
        raise HTTPException(status_code=400, detail="Failed to create player")
    return new_player

@app.delete("/player/by-name/{name}", status_code=204)
def delete_by_name(name: str):
    ok = delete_player_by_name(name)
    if not ok:
        raise HTTPException(status_code=404, detail="Player not found")
    return

@app.delete("/player/by-number/{number}", status_code=204)
def delete_by_number(number: int):
    ok = delete_player_by_number(number)
    if not ok:
        raise HTTPException(status_code=404, detail="Player not found")
    return

# Run with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)

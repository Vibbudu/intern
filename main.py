# main.py
from fastapi import FastAPI, HTTPException, Query
from typing import Optional
import uvicorn

from db import (
    get_all_players, get_all_coaches, get_player_by_number, get_player_performance,
    get_teams, get_team_roster, compare_players, get_top_salary, get_teammates_network,
    search_players_by_name
)
from models import PlayerSummary, CoachSummary, TeamSummary, PerformanceRec, PlayerDetail, CompareResponse

app = FastAPI(title="NBA DASHBOARD API", version="1.0")

@app.get("/players", response_model=list[PlayerSummary])
def players(limit: int = Query(100, ge=1, le=1000)):
    rows = get_all_players(limit)
    return rows

@app.get("/coaches", response_model=list[CoachSummary])
def coaches(limit: int = Query(100, ge=1, le=1000)):
    return get_all_coaches(limit)

@app.get("/player/{number}", response_model=PlayerDetail)
def player_detail(number: int):
    p = get_player_by_number(number)
    if not p:
        raise HTTPException(status_code=404, detail="Player not found")
    return p

@app.get("/player/{number}/performance", response_model=list[PerformanceRec])
def player_performance(number: int):
    return get_player_performance(number)

@app.get("/teams", response_model=list[TeamSummary])
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
def top_salaries(limit: int = 10):
    return get_top_salary(limit)

@app.get("/player/{number}/teammates")
def teammates(number: int):
    return get_teammates_network(number)

@app.get("/search/players")
def search_players(q: str, limit: int = 20):
    return search_players_by_name(q, limit)

# Run with: uvicorn main:app --reload
if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)

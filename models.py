# models.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class PlayerSummary(BaseModel):
    name: str
    age: int
    number: int
    height: Optional[float] = None
    weight: Optional[float] = None
    team: Optional[str] = None
    salary: Optional[float] = None

class CoachSummary(BaseModel):
    name: str

class TeamSummary(BaseModel):
    team: str
    players: List[str]
    coaches: List[str]

class PerformanceRec(BaseModel):
    opponent: str
    game_date: Optional[int] = None  # epoch/int or YYYYMMDD if you add it later
    minutes: Optional[int] = None
    points: Optional[int] = None
    assists: Optional[int] = None
    rebounds: Optional[int] = None
    turnovers: Optional[int] = None

class PlayerDetail(BaseModel):
    name: str
    age: int
    number: int
    height: Optional[float] = None
    weight: Optional[float] = None
    team: Optional[str] = None
    salary: Optional[float] = None
    coaches: Optional[List[str]] = []

class CompareResponse(BaseModel):
    players: List[Dict[str, Any]]

class PlayerCreate(BaseModel):
    name: str
    age: int
    number: int
    height: float
    weight: float
    team: str
    salary: float

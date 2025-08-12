# models.py
from pydantic import BaseModel
from typing import List, Optional

class PlayerSummary(BaseModel):
    name: str
    age: int
    number: int
    height: Optional[float]
    weight: Optional[float]
    team: Optional[str]
    salary: Optional[float]

class CoachSummary(BaseModel):
    name: str

class TeamSummary(BaseModel):
    team: str
    players: List[str]
    coaches: List[str]

class PerformanceRec(BaseModel):
    opponent: str
    minutes: Optional[int]
    points: Optional[int]
    assists: Optional[int]
    rebounds: Optional[int]
    turnovers: Optional[int]

class PlayerDetail(BaseModel):
    name: str
    age: int
    number: int
    height: Optional[float]
    weight: Optional[float]
    team: Optional[str]
    salary: Optional[float]
    coaches: Optional[List[str]]

class CompareResponse(BaseModel):
    players: List[dict]  # number, name, games, points, assists, rebounds

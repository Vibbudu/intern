# db.py
from neo4j import GraphDatabase
from typing import List, Dict, Optional


NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def _records_to_list(result) -> List[Dict]:
    return [dict(record) for record in result]


def get_all_players(limit: int = 100) -> List[Dict]:
    with driver.session() as session:
        q = """
            MATCH (p:PLAYER)-[r:PLAYS_FOR]->(t:TEAM)
            RETURN p.name AS name, p.age AS age, p.number AS number,
                   p.height AS height, p.weight AS weight, t.name AS team, r.salary AS salary
            ORDER BY p.name
            
        """
        result = session.run(q, {"limit": limit})
        return _records_to_list(result)

def get_all_coaches(limit: int = 100) -> List[Dict]:
    with driver.session() as session:
        q = "MATCH (c:COACH) RETURN c.name AS name "
        result = session.run(q, {"limit": limit})
        return _records_to_list(result)

def get_player_by_number(number: int) -> Optional[Dict]:
    with driver.session() as session:
        q = """
            MATCH (p:PLAYER {number: $number})
            MATCH (p)-[pf:PLAYS_FOR]->(t:TEAM)
            MATCH (coach:COACH)-[:COACHES]->(p)
            RETURN p.name AS name, p.age AS age, p.number AS number,
                   p.height AS height, p.weight AS weight,
                   t.name AS team, pf.salary AS salary, collect(coach.name) AS coaches
        """
        result = session.run(q, {"number": number})
        record = result.single()
        return dict(record) if record else None


def get_teams() -> List[Dict]:
    with driver.session() as session:
        q = """
            MATCH (t:TEAM)
            OPTIONAL MATCH (p:PLAYER)-[r:PLAYS_FOR]->(t)
            OPTIONAL MATCH (c:COACH)-[:COACHES_FOR]->(t)
            RETURN t.name AS team, collect(DISTINCT p.name) AS players, collect(DISTINCT c.name) AS coaches
            ORDER BY t.name
        """
        result = session.run(q)
        return _records_to_list(result)

def get_team_roster(team_name: str) -> Dict:
    with driver.session() as session:
        q = """
            MATCH (t:TEAM {name: $team})
            OPTIONAL MATCH (p:PLAYER)-[r:PLAYS_FOR]->(t)
            OPTIONAL MATCH (c:COACH)-[:COACHES_FOR]->(t)
            RETURN t.name AS team, collect({name: p.name, number: p.number, salary: r.salary}) AS players,
                   collect(c.name) AS coaches
        """
        result = session.run(q, {"team": team_name})
        return dict(result.single()) if result.peek() else {}


def get_player_performance(number: int) -> List[Dict]:
    with driver.session() as session:
        q = """
            MATCH (p:PLAYER {number: $number})-[pa:PLAYED_AGAINST]->(opp:TEAM)
            RETURN opp.name AS opponent, pa.minutes AS minutes, pa.points AS points,
                   pa.assists AS assists, pa.rebounds AS rebounds, pa.turnovers AS turnovers
            ORDER BY pa.points DESC
        """
        result = session.run(q, {"number": number})
        return _records_to_list(result)


def compare_players(num1: int, num2: int) -> Dict:
    with driver.session() as session:
        q = """
            MATCH (p:PLAYER)
            WHERE p.number IN [$n1, $n2]
            OPTIONAL MATCH (p)-[pa:PLAYED_AGAINST]->()
            WITH p.number AS number, p.name AS name,
                 count(pa) AS games, sum(coalesce(pa.points,0)) AS total_points,
                 sum(coalesce(pa.assists,0)) AS total_assists, sum(coalesce(pa.rebounds,0)) AS total_rebounds
            RETURN collect({number:number, name:name, games:games, points:total_points,
                            assists:total_assists, rebounds:total_rebounds}) AS players
        """
        result = session.run(q, {"n1": num1, "n2": num2})
        row = result.single()
        return dict(row) if row else {"players": []}

def get_top_salary(limit: int = 10) -> List[Dict]:
    with driver.session() as session:
        q = """
            MATCH (p:PLAYER)-[r:PLAYS_FOR]->(t:TEAM)
            RETURN t.name AS team, p.name AS player, r.salary AS salary
            ORDER BY r.salary DESC
            
        """
        result = session.run(q, {"limit": limit})
        return _records_to_list(result)

def get_teammates_network(number: int) -> Dict:
    with driver.session() as session:
        q = """
            MATCH (p:PLAYER {number: $number})-[:TEAMMATES]-(tm:PLAYER)
            RETURN p.name AS player, collect({name:tm.name, number:tm.number}) AS teammates
        """
        result = session.run(q, {"number": number})
        record = result.single()
        return dict(record) if record else {"player": None, "teammates": []}

def search_players_by_name(qname: str, limit: int = 20) -> List[Dict]:
    with driver.session() as session:
        q = """
            MATCH (p:PLAYER)
            WHERE toLower(p.name) CONTAINS toLower($qname)
            RETURN p.name AS name, p.number AS number, p.age AS age
            
        """
        result = session.run(q, {"qname": qname, "limit": limit})
        return _records_to_list(result)

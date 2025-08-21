# db.py
from neo4j import GraphDatabase
from typing import List, Dict, Optional

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def _records_to_list(result) -> List[Dict]:
    return [dict(r) for r in result]

def get_all_players(limit: int = 100) -> List[Dict]:
    with driver.session() as session:
        q = """
        MATCH (p:PLAYER)-[r:PLAYS_FOR]->(t:TEAM)
        RETURN p.name AS name, p.age AS age, p.number AS number,
               p.height AS height, p.weight AS weight, t.name AS team, r.salary AS salary
        ORDER BY p.name
        LIMIT $limit
        """
        return _records_to_list(session.run(q, {"limit": limit}))

def get_all_coaches(limit: int = 100) -> List[Dict]:
    with driver.session() as session:
        q = """
        MATCH (c:COACH)
        RETURN c.name AS name
        ORDER BY c.name
        LIMIT $limit
        """
        return _records_to_list(session.run(q, {"limit": limit}))

def get_player_by_number(number: int) -> Optional[Dict]:
    with driver.session() as session:
        q = """
        MATCH (p:PLAYER {number: $number})-[pf:PLAYS_FOR]->(t:TEAM)
        OPTIONAL MATCH (coach:COACH)-[:COACHES]->(p)
        RETURN p.name AS name, p.age AS age, p.number AS number,
               p.height AS height, p.weight AS weight,
               t.name AS team, pf.salary AS salary, collect(DISTINCT coach.name) AS coaches
        """
        rec = session.run(q, {"number": number}).single()
        return dict(rec) if rec else None

def get_teams() -> List[Dict]:
    with driver.session() as session:
        q = """
        MATCH (t:TEAM)
        OPTIONAL MATCH (p:PLAYER)-[:PLAYS_FOR]->(t)
        OPTIONAL MATCH (c:COACH)-[:COACHES_FOR]->(t)
        RETURN t.name AS team,
               [name IN collect(DISTINCT p.name) WHERE name IS NOT NULL] AS players,
               [name IN collect(DISTINCT c.name) WHERE name IS NOT NULL] AS coaches
        ORDER BY t.name
        """
        return _records_to_list(session.run(q))

def get_team_roster(team_name: str) -> Dict:
    with driver.session() as session:
        q = """
        MATCH (t:TEAM {name: $team})
        OPTIONAL MATCH (p:PLAYER)-[r:PLAYS_FOR]->(t)
        OPTIONAL MATCH (c:COACH)-[:COACHES_FOR]->(t)
        RETURN t.name AS team,
               [ {name:p.name, number:p.number, salary:r.salary} IN collect({name:p.name, number:p.number, salary:r.salary})
                 WHERE p.name IS NOT NULL ] AS players,
               [c.name IN collect(DISTINCT c.name) WHERE c.name IS NOT NULL] AS coaches
        """
        res = session.run(q, {"team": team_name})
        return dict(res.single()) if res.peek() else {}

def get_player_performance(number: int) -> List[Dict]:
    with driver.session() as session:
        q = """
        MATCH (p:PLAYER {number: $number})-[pa:PLAYED_AGAINST]->(opp:TEAM)
        RETURN opp.name AS opponent,
               pa.date AS game_date,
               pa.minutes AS minutes,
               pa.points AS points,
               pa.assists AS assists,
               pa.rebounds AS rebounds,
               pa.turnovers AS turnovers
        ORDER BY coalesce(pa.date, 0) ASC
        """
        return _records_to_list(session.run(q, {"number": number}))

def get_player_performance_by_name(name: str) -> List[Dict]:
    with driver.session() as session:
        q = """
        MATCH (p:PLAYER {name: $name})-[pa:PLAYED_AGAINST]->(opp:TEAM)
        RETURN opp.name AS opponent,
               pa.date AS game_date,
               pa.minutes AS minutes,
               pa.points AS points,
               pa.assists AS assists,
               pa.rebounds AS rebounds,
               pa.turnovers AS turnovers
        ORDER BY coalesce(pa.date, 0) ASC
        """
        return _records_to_list(session.run(q, {"name": name}))

def compare_players(num1: int, num2: int) -> Dict:
    with driver.session() as session:
        q = """
        MATCH (p:PLAYER)
        WHERE p.number IN [$n1, $n2]
        OPTIONAL MATCH (p)-[pa:PLAYED_AGAINST]->()
        WITH p, count(pa) AS games,
             sum(coalesce(pa.points,0)) AS pts,
             sum(coalesce(pa.assists,0)) AS ast,
             sum(coalesce(pa.rebounds,0)) AS reb
        RETURN collect({
            number: p.number,
            name: p.name,
            games: games,
            points: pts,
            assists: ast,
            rebounds: reb,
            points_avg: CASE WHEN games=0 THEN 0.0 ELSE toFloat(pts)/games END,
            assists_avg: CASE WHEN games=0 THEN 0.0 ELSE toFloat(ast)/games END,
            rebounds_avg: CASE WHEN games=0 THEN 0.0 ELSE toFloat(reb)/games END
        }) AS players
        """
        row = session.run(q, {"n1": num1, "n2": num2}).single()
        return dict(row) if row else {"players": []}

def get_top_salary(limit: int = 10) -> List[Dict]:
    with driver.session() as session:
        q = """
        MATCH (p:PLAYER)-[r:PLAYS_FOR]->(t:TEAM)
        RETURN t.name AS team, p.name AS player, r.salary AS salary
        ORDER BY r.salary DESC
        LIMIT $limit
        """
        return _records_to_list(session.run(q, {"limit": limit}))

def get_teammates_network(number: int) -> Dict:
    with driver.session() as session:
        q = """
        MATCH (p:PLAYER {number: $number})-[:TEAMMATES]-(tm:PLAYER)
        RETURN p.name AS player, collect({name:tm.name, number:tm.number}) AS teammates
        """
        rec = session.run(q, {"number": number}).single()
        return dict(rec) if rec else {"player": None, "teammates": []}

def search_players_by_name(qname: str, limit: int = 20) -> List[Dict]:
    with driver.session() as session:
        q = """
        MATCH (p:PLAYER)
        WHERE toLower(p.name) CONTAINS toLower($qname)
        RETURN p.name AS name, p.number AS number, p.age AS age
        ORDER BY p.name
        LIMIT $limit
        """
        return _records_to_list(session.run(q, {"qname": qname, "limit": limit}))

def create_player(player_data: dict) -> dict:
    with driver.session() as session:
        q = """
        MERGE (t:TEAM {name: $team})
        MERGE (p:PLAYER {number: $number})
          ON CREATE SET p.name=$name, p.age=$age, p.height=$height, p.weight=$weight
          ON MATCH SET p.name=$name, p.age=$age, p.height=$height, p.weight=$weight
        MERGE (p)-[r:PLAYS_FOR]->(t)
          ON CREATE SET r.salary=$salary
          ON MATCH SET r.salary=$salary
        RETURN p.name AS name, p.age AS age, p.number AS number,
               p.height AS height, p.weight AS weight,
               t.name AS team, r.salary AS salary
        """
        rec = session.run(q, player_data).single()
        if rec:
            data = dict(rec)
            data["coaches"] = []
            return data
        return {}

def delete_player_by_name(name: str) -> bool:
    with driver.session() as session:
        q = "MATCH (p:PLAYER {name: $name}) DETACH DELETE p RETURN count(*) AS c"
        c = session.run(q, {"name": name}).single()["c"]
        return c > 0

def delete_player_by_number(number: int) -> bool:
    with driver.session() as session:
        q = "MATCH (p:PLAYER {number: $number}) DETACH DELETE p RETURN count(*) AS c"
        c = session.run(q, {"number": number}).single()["c"]
        return c > 0

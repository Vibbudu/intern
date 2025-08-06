from neo4j import GraphDatabase


NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def get_all_players():
    with driver.session() as session:
        result = session.run("""
            MATCH (p:PLAYER)
            RETURN p.name AS name, p.age AS age, p.number AS number, 
                   p.height AS height, p.weight AS weight
        """)
        
        players = []
        for record in result:
            players.append({
                "name": record["name"],
                "age": record["age"],
                "number": record["number"],
                "height": record["height"],
                "weight": record["weight"]
            })
        return players
def get_all_coaches():
    with driver.session() as ses:
        result = ses.run("""
                         MATCH (c:COACH)
                         return c.name as name""")
        coaches = []
        for records in result:
            coaches.append({
                "name": records["name"]
            })
        return coaches
    
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_player_details(number: int):
    with driver.session() as session:
        start = time.time()
        result = session.run("""
            MATCH (p:PLAYER {number: $number})
            OPTIONAL MATCH (p)-[:HAS_COACH]->(c:COACH)
            OPTIONAL MATCH (p)-[:PLAYS_FOR]->(club:CLUB)
            RETURN 
                p.name AS player_name, p.number AS jersey, p.age AS age,
                c.name AS coach_name,
                club.name AS club_name
        """, {"number": number})
        duration = time.time() - start

        record = result.single()
        if not record:
            return None

        return {
            "player": {
                "name": record["player_name"],
                "number": record["jersey"],
                "age": record["age"]
            },
            "coach": {
                "name": record["coach_name"]
            },
            "club": {
                "name": record["club_name"]
            },
            "query_time": round(duration, 4)  # ⏱️ Add query time
        }


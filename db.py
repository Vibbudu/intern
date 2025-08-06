from neo4j import GraphDatabase
import logging
import time

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Neo4j Config
NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def get_all_players():
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (p:PLAYER)
                RETURN p.name AS name, p.age AS age, p.number AS number, 
                       p.height AS height, p.weight AS weight
            """)
            return [dict(record) for record in result]
    except Exception as e:
        logger.error(f"Error fetching players: {e}")
        return []

def get_all_coaches():
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (c:COACH)
                RETURN c.name AS name
            """)
            return [dict(record) for record in result]
    except Exception as e:
        logger.error(f"Error fetching coaches: {e}")
        return []

def get_player_details(number: int):
    try:
        with driver.session() as session:
            start = time.time()
            result = session.run("""
                MATCH (p:PLAYER {number: $number})
                RETURN p.name AS name, p.age AS age, p.height AS height, p.weight AS weight, p.number AS number
            """, {"number": number})
            duration = time.time() - start
            logger.info(f"Query took {duration:.2f}s")
            return result.single()
    except Exception as e:
        logger.error(f"Error fetching player details: {e}")
        return None

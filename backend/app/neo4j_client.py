from __future__ import annotations

from neo4j import GraphDatabase

from .config import Settings, load_settings


NODE_CYPHER = """UNWIND $nodes AS item
MERGE (n:CSVEntity {id: item.id})
SET n.name = item.name, n.normalized_name = item.normalized_name,
    n.entity_type = item.entity_type, n.source_file = item.source_file, n.import_id = item.import_id"""
REL_CYPHER = """UNWIND $relationships AS item
MATCH (source:CSVEntity {id: item.source_id})
MATCH (target:CSVEntity {id: item.target_id})
MERGE (source)-[r:RELATED_TO {predicate: item.predicate, source_id: item.source_id,
    target_id: item.target_id, import_id: item.import_id}]->(target)
SET r.source_file = item.source_file"""


class Neo4jClient:
    def __init__(self, settings: Settings | None = None, driver=None):
        self.settings = settings or load_settings()
        self.driver = driver or GraphDatabase.driver(self.settings.neo4j_uri, auth=(self.settings.neo4j_username, self.settings.neo4j_password))

    def test_connection(self) -> tuple[bool, str]:
        try:
            self.driver.verify_connectivity()
            return True, "Connected to Neo4j"
        except Exception as exc:
            return False, f"Neo4j connection failed: {exc.__class__.__name__}"

    def upsert_graph(self, nodes: list[dict], relationships: list[dict]) -> dict[str, int]:
        def work(tx):
            tx.run(NODE_CYPHER, nodes=nodes).consume()
            tx.run(REL_CYPHER, relationships=relationships).consume()
        with self.driver.session(database=self.settings.neo4j_database) as session:
            session.execute_write(work)
        return {"nodes": len(nodes), "relationships": len(relationships)}

    def close(self):
        self.driver.close()

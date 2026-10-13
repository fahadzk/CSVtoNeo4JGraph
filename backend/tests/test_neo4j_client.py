from backend.app.neo4j_client import Neo4jClient

class BrokenDriver:
    def verify_connectivity(self): raise RuntimeError("offline")
    def close(self): pass

def test_connection_failure_is_safe():
    ok, message = Neo4jClient(driver=BrokenDriver()).test_connection()
    assert not ok
    assert "connection failed" in message

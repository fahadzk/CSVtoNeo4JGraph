from backend.app.graph_builder import build_graph

HEADERS = ["City", "Province"]

def test_normalization_deduplication_and_ids():
    result = build_graph([[" Karachi ", "Sindh"], ["karachi", " SINDH "], ["", "Punjab"]], "City", "Province", "LOCATED_IN", "PAKISTAN_CITIES", "cities.csv", HEADERS, "import-1")
    assert len(result.nodes) == 2
    assert len(result.relationships) == 1
    assert result.nodes[0]["id"] == "PAKISTAN_CITIES_CITY:karachi"
    assert result.skipped_rows == 1

def test_columns_must_differ():
    try:
        build_graph([["a"]], "City", "City", "R", "P", "x.csv", ["City"])
    except ValueError as exc:
        assert "different" in str(exc)
    else:
        assert False

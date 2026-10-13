from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from .config import load_settings
from .csv_parser import parse_csv_bytes
from .graph_builder import build_graph
from .neo4j_client import Neo4jClient
from .schemas import ImportRequest, PreviewRequest

router = APIRouter()


@router.post("/csv/parse")
async def parse_csv(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "Please upload a .csv file")
    try:
        parsed = parse_csv_bytes(await file.read(), max_bytes=load_settings().csv_max_bytes)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {"filename": file.filename, "headers": parsed.headers, "rows": parsed.rows, "warnings": parsed.warnings, "row_count": parsed.row_count,
            "sample_rows": parsed.rows[:5]}


@router.post("/graph/preview")
def graph_preview(request: PreviewRequest):
    try:
        result = build_graph(**request.model_dump())
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {"nodes": result.nodes, "relationships": result.relationships, "primary_nodes": result.primary_nodes,
            "secondary_nodes": result.secondary_nodes, "warnings": result.warnings, "summary": result.summary, "import_id": result.import_id}


@router.get("/neo4j/test")
def neo4j_test():
    client = Neo4jClient()
    try:
        ok, message = client.test_connection()
        return {"ok": ok, "message": message}
    finally:
        client.close()


@router.post("/graph/import")
def graph_import(request: ImportRequest):
    client = Neo4jClient()
    try:
        result = client.upsert_graph([n.model_dump() for n in request.nodes], [r.model_dump() for r in request.relationships])
        return {"ok": True, **result}
    except Exception as exc:
        raise HTTPException(502, f"Neo4j import failed: {exc.__class__.__name__}") from exc
    finally:
        client.close()

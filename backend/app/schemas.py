from __future__ import annotations

from pydantic import BaseModel, Field


class PreviewRequest(BaseModel):
    rows: list[list[str]]
    headers: list[str]
    primary_column: str
    secondary_column: str
    predicate: str = Field(min_length=1, max_length=100)
    prefix: str = Field(min_length=1, max_length=100)
    source_file: str = Field(min_length=1, max_length=255)
    import_id: str | None = None


class Node(BaseModel):
    id: str
    name: str
    normalized_name: str
    entity_type: str
    source_file: str
    import_id: str


class Relationship(BaseModel):
    source_id: str
    target_id: str
    predicate: str
    source_file: str
    import_id: str


class ImportRequest(BaseModel):
    nodes: list[Node]
    relationships: list[Relationship]

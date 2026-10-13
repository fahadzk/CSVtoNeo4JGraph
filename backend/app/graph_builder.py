from __future__ import annotations

import re
import uuid
from dataclasses import dataclass


@dataclass
class GraphResult:
    nodes: list[dict]
    relationships: list[dict]
    warnings: list[str]
    primary_nodes: list[dict]
    secondary_nodes: list[dict]
    skipped_rows: int
    import_id: str

    @property
    def summary(self) -> dict[str, int]:
        return {"node_count": len(self.nodes), "relationship_count": len(self.relationships), "skipped_rows": self.skipped_rows,
                "primary_node_count": len(self.primary_nodes), "secondary_node_count": len(self.secondary_nodes)}


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).lower()


def _type(prefix: str, column: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9]+", "_", column.strip().upper()).strip("_") or "VALUE"
    return f"{prefix}_{safe}"


def build_graph(rows: list[list[str]], primary_column: str, secondary_column: str, predicate: str,
                prefix: str, source_file: str, headers: list[str] | None = None, import_id: str | None = None) -> GraphResult:
    if primary_column == secondary_column:
        raise ValueError("Primary and secondary columns must be different")
    if headers is None:
        raise ValueError("Headers are required to map columns")
    try:
        pidx, sidx = headers.index(primary_column), headers.index(secondary_column)
    except ValueError as exc:
        raise ValueError("Selected columns are not present in the CSV headers") from exc
    prefix = re.sub(r"[^A-Za-z0-9_]+", "_", prefix.strip().upper()).strip("_") or "IMPORT"
    predicate = predicate.strip() or "RELATED_TO"
    import_id = import_id or str(uuid.uuid4())
    ptype, stype = _type(prefix, primary_column), _type(prefix, secondary_column)
    nodes_by_id: dict[str, dict] = {}
    relationships_by_key: dict[tuple[str, str, str], dict] = {}
    warnings: list[str] = []
    skipped = 0
    for row_num, row in enumerate(rows, start=2):
        if max(pidx, sidx) >= len(row):
            skipped += 1; warnings.append(f"Row {row_num} is too short and was skipped"); continue
        pclean, sclean = re.sub(r"\s+", " ", row[pidx].strip()), re.sub(r"\s+", " ", row[sidx].strip())
        if not pclean or not sclean:
            skipped += 1; warnings.append(f"Row {row_num} has an empty mapped value and was skipped"); continue
        pn, sn = normalize(pclean), normalize(sclean)
        pid, sid = f"{ptype}:{pn}", f"{stype}:{sn}"
        for ident, name, norm, entity_type in ((pid, pclean, pn, ptype), (sid, sclean, sn, stype)):
            nodes_by_id.setdefault(ident, {"id": ident, "name": name, "normalized_name": norm, "entity_type": entity_type,
                                           "source_file": source_file, "import_id": import_id})
        key = (pid, sid, predicate)
        relationships_by_key.setdefault(key, {"source_id": pid, "target_id": sid, "predicate": predicate,
                                               "source_file": source_file, "import_id": import_id})
    nodes = list(nodes_by_id.values())
    primary_nodes = [n for n in nodes if n["entity_type"] == ptype]
    secondary_nodes = [n for n in nodes if n["entity_type"] == stype]
    return GraphResult(nodes, list(relationships_by_key.values()), warnings, primary_nodes, secondary_nodes, skipped, import_id)

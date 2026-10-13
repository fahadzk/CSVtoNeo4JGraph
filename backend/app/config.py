from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    neo4j_uri: str = "neo4j://localhost:7687"
    neo4j_database: str = "neo4j"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "change-me"
    neo4j_timeout_seconds: int = 30
    csv_max_bytes: int = 10 * 1024 * 1024
    cors_origins: tuple[str, ...] = ("http://localhost:5173",)


def load_settings(config_path: Path | None = None) -> Settings:
    path = config_path or ROOT / "config" / "neo4j.json"
    values: dict = {}
    if path.exists():
        try:
            values = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Invalid Neo4j configuration: {exc}") from exc
    env = os.environ
    return Settings(
        neo4j_uri=env.get("NEO4J_URI", values.get("uri", Settings.neo4j_uri)),
        neo4j_database=env.get("NEO4J_DATABASE", values.get("database", Settings.neo4j_database)),
        neo4j_username=env.get("NEO4J_USERNAME", values.get("username", Settings.neo4j_username)),
        neo4j_password=env.get("NEO4J_PASSWORD", values.get("password", Settings.neo4j_password)),
        neo4j_timeout_seconds=int(env.get("NEO4J_TIMEOUT_SECONDS", values.get("timeout_seconds", 30))),
        csv_max_bytes=int(env.get("CSV_MAX_BYTES", 10 * 1024 * 1024)),
    )

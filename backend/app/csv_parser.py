from __future__ import annotations

import csv
import io
from dataclasses import dataclass


@dataclass
class ParsedCSV:
    headers: list[str]
    rows: list[list[str]]
    warnings: list[str]
    row_count: int


def parse_csv_bytes(data: bytes, *, max_bytes: int = 10 * 1024 * 1024) -> ParsedCSV:
    if len(data) > max_bytes:
        raise ValueError(f"CSV exceeds the configured {max_bytes} byte limit")
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("CSV must be UTF-8 encoded") from exc
    reader = csv.reader(io.StringIO(text, newline=""))
    try:
        raw_headers = next(reader)
    except StopIteration as exc:
        raise ValueError("CSV must contain a header row") from exc
    headers = [h.strip() for h in raw_headers]
    if not headers or not any(headers):
        raise ValueError("CSV must contain a non-empty header row")
    if len(set(headers)) != len(headers):
        raise ValueError("CSV headers must be unique")
    warnings: list[str] = []
    rows: list[list[str]] = []
    for number, row in enumerate(reader, start=2):
        if not row or all(not cell.strip() for cell in row):
            warnings.append(f"Row {number} is empty and was skipped")
            continue
        if len(row) != len(headers):
            warnings.append(f"Row {number} has {len(row)} columns; expected {len(headers)} and was skipped")
            continue
        rows.append(row)
    return ParsedCSV(headers=headers, rows=rows, warnings=warnings, row_count=len(rows))

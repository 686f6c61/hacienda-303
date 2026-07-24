#!/usr/bin/env python3
"""Build a compact, traceable SQLite index from the AEAT localizer JSON files."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import tempfile
from pathlib import Path
from typing import Any


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE sources (
    kind TEXT PRIMARY KEY CHECK (kind IN ('bienes', 'servicios')),
    source_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    sha256 TEXT NOT NULL,
    metadata_json TEXT NOT NULL
);

CREATE TABLE cases (
    case_id TEXT PRIMARY KEY,
    kind TEXT NOT NULL CHECK (kind IN ('bienes', 'servicios')),
    leaf_node TEXT NOT NULL,
    depth INTEGER NOT NULL,
    path_json TEXT NOT NULL,
    result_text TEXT NOT NULL,
    clarification_text TEXT NOT NULL,
    links_json TEXT NOT NULL,
    FOREIGN KEY (kind) REFERENCES sources(kind)
);

CREATE TABLE steps (
    case_id TEXT NOT NULL,
    position INTEGER NOT NULL,
    question TEXT NOT NULL,
    menu_id TEXT NOT NULL,
    option_value TEXT NOT NULL,
    answer TEXT NOT NULL,
    PRIMARY KEY (case_id, position),
    FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
);

CREATE INDEX idx_cases_kind ON cases(kind);
CREATE INDEX idx_steps_lookup ON steps(position, option_value, case_id);
CREATE INDEX idx_steps_case ON steps(case_id, position);

CREATE VIRTUAL TABLE cases_fts USING fts5(
    case_id UNINDEXED,
    kind UNINDEXED,
    search_text,
    tokenize = 'unicode61 remove_diacritics 2'
);
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Construye el índice SQLite portable de los localizadores AEAT."
    )
    parser.add_argument("--bienes", required=True, type=Path)
    parser.add_argument("--servicios", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def validate_payload(payload: dict[str, Any], kind: str, path: Path) -> list[dict[str, Any]]:
    required = {"metadata", "root_question", "cases", "tree"}
    missing = required.difference(payload)
    if missing:
        raise ValueError(f"{path}: faltan claves {sorted(missing)}")

    cases = payload["cases"]
    if not isinstance(cases, list):
        raise ValueError(f"{path}: cases no es una lista")

    expected = payload["metadata"].get("case_count")
    if expected != len(cases):
        raise ValueError(
            f"{path}: metadata.case_count={expected!r}, pero hay {len(cases)} casos"
        )

    ids: set[str] = set()
    for item in cases:
        case_id = item.get("case_id")
        if not case_id or case_id in ids:
            raise ValueError(f"{path}: case_id ausente o duplicado: {case_id!r}")
        ids.add(case_id)
        if not item.get("path"):
            raise ValueError(f"{path}: {case_id} no tiene recorrido")
        if not str(item.get("result_text", "")).strip():
            raise ValueError(f"{path}: {case_id} no tiene resultado")
        if kind not in case_id:
            raise ValueError(f"{path}: {case_id} no parece pertenecer a {kind}")
    return cases


def load_source(
    connection: sqlite3.Connection,
    kind: str,
    path: Path,
) -> tuple[int, int]:
    resolved = path.resolve()
    with resolved.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    cases = validate_payload(payload, kind, resolved)
    metadata = dict(payload["metadata"])
    metadata["root_question"] = payload["root_question"]

    connection.execute(
        """
        INSERT INTO sources
            (kind, source_path, file_name, size_bytes, sha256, metadata_json)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            kind,
            str(Path("sources") / resolved.name),
            resolved.name,
            resolved.stat().st_size,
            sha256_file(resolved),
            compact_json(metadata),
        ),
    )

    step_count = 0
    for item in cases:
        case_id = item["case_id"]
        path_items = item["path"]
        clarification_text = item.get("clarification_text")
        if clarification_text is None:
            clarification_text = "\n".join(
                str(value) for value in item.get("clarifications", [])
            )
        links = item.get("links")
        if links is None:
            links = [
                link
                for block in item.get("result_blocks", [])
                for link in block.get("links", [])
            ]

        connection.execute(
            """
            INSERT INTO cases
                (case_id, kind, leaf_node, depth, path_json, result_text,
                 clarification_text, links_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                case_id,
                kind,
                str(item.get("leaf_node", "")),
                len(path_items),
                compact_json(path_items),
                item["result_text"].strip(),
                str(clarification_text or "").strip(),
                compact_json(links or []),
            ),
        )

        search_parts: list[str] = []
        for position, step in enumerate(path_items):
            question = str(step.get("question", "")).strip()
            answer = str(step.get("answer", "")).strip()
            connection.execute(
                """
                INSERT INTO steps
                    (case_id, position, question, menu_id, option_value, answer)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    case_id,
                    position,
                    question,
                    str(step.get("menu_id", "")),
                    str(step.get("option_value", "")),
                    answer,
                ),
            )
            search_parts.extend((question, answer))
            step_count += 1

        search_parts.extend(
            (
                item["result_text"],
                str(clarification_text or ""),
                " ".join(str(link.get("text", "")) for link in links or []),
            )
        )
        connection.execute(
            "INSERT INTO cases_fts(case_id, kind, search_text) VALUES (?, ?, ?)",
            (case_id, kind, "\n".join(search_parts)),
        )

    return len(cases), step_count


def main() -> int:
    args = parse_args()
    for path in (args.bienes, args.servicios):
        if not path.is_file():
            print(f"No existe el archivo: {path}", file=sys.stderr)
            return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{args.output.name}.",
        suffix=".tmp",
        dir=args.output.parent,
    )
    os.close(file_descriptor)
    temporary_path = Path(temporary_name)

    try:
        connection = sqlite3.connect(temporary_path)
        connection.executescript(SCHEMA)
        totals: dict[str, tuple[int, int]] = {}
        with connection:
            totals["bienes"] = load_source(connection, "bienes", args.bienes)
            totals["servicios"] = load_source(
                connection, "servicios", args.servicios
            )
        connection.execute("ANALYZE")
        connection.execute("VACUUM")
        connection.close()
        os.replace(temporary_path, args.output)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise

    total_cases = sum(item[0] for item in totals.values())
    total_steps = sum(item[1] for item in totals.values())
    print(
        compact_json(
            {
                "output": str(args.output.resolve()),
                "cases": {
                    key: value[0] for key, value in totals.items()
                },
                "total_cases": total_cases,
                "total_steps": total_steps,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

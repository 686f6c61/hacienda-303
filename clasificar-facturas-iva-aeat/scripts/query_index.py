#!/usr/bin/env python3
"""Query and traverse the indexed AEAT goods/services decision cases."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any, Iterable


DEFAULT_DATABASE = Path(__file__).resolve().parent.parent / "assets" / "aeat_iva.sqlite"
TOKEN_PATTERN = re.compile(r"[^\W_]{2,}", re.UNICODE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Consulta trazable de los localizadores AEAT de IVA."
    )
    parser.add_argument("--db", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--compact", action="store_true")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("stats", help="Muestra fuentes y cobertura.")

    root = subparsers.add_parser("root", help="Lista categorías iniciales.")
    root.add_argument("--kind", choices=("bienes", "servicios"), required=True)

    search = subparsers.add_parser("search", help="Busca candidatos por texto.")
    search.add_argument("--kind", choices=("bienes", "servicios", "todos"), default="todos")
    search.add_argument("--query", required=True)
    search.add_argument("--limit", type=int, default=10)

    next_parser = subparsers.add_parser(
        "next", help="Devuelve la siguiente pregunta para un prefijo de respuestas."
    )
    next_parser.add_argument("--kind", choices=("bienes", "servicios"), required=True)
    next_parser.add_argument(
        "--answer",
        action="append",
        default=[],
        help="option_value exacto, en orden; repetir para cada respuesta.",
    )

    show = subparsers.add_parser("show", help="Muestra un caso terminal.")
    show.add_argument("--case-id", required=True)
    return parser.parse_args()


def emit(payload: Any, compact: bool) -> None:
    if compact:
        print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))


def rows_to_dicts(rows: Iterable[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


def stats(connection: sqlite3.Connection) -> dict[str, Any]:
    sources = []
    for row in connection.execute(
        "SELECT kind, file_name, size_bytes, sha256, metadata_json FROM sources ORDER BY kind"
    ):
        item = dict(row)
        item["metadata"] = json.loads(item.pop("metadata_json"))
        sources.append(item)
    counts = rows_to_dicts(
        connection.execute(
            """
            SELECT kind, COUNT(*) AS cases, MIN(depth) AS min_depth,
                   MAX(depth) AS max_depth,
                   ROUND(AVG(depth), 2) AS avg_depth
            FROM cases GROUP BY kind ORDER BY kind
            """
        )
    )
    return {"sources": sources, "coverage": counts}


def root_options(connection: sqlite3.Connection, kind: str) -> dict[str, Any]:
    rows = rows_to_dicts(
        connection.execute(
            """
            SELECT s.question, s.menu_id, s.option_value, s.answer,
                   COUNT(*) AS terminal_cases
            FROM steps AS s
            JOIN cases AS c ON c.case_id = s.case_id
            WHERE c.kind = ? AND s.position = 0
            GROUP BY s.question, s.menu_id, s.option_value, s.answer
            ORDER BY CAST(s.option_value AS INTEGER), s.option_value
            """,
            (kind,),
        )
    )
    return {"kind": kind, "position": 0, "options": rows}


def safe_tokens(query: str) -> list[str]:
    seen: set[str] = set()
    tokens = []
    for token in TOKEN_PATTERN.findall(query.casefold()):
        if token not in seen:
            seen.add(token)
            tokens.append(token)
    return tokens[:20]


def search_cases(
    connection: sqlite3.Connection,
    kind: str,
    query: str,
    limit: int,
) -> dict[str, Any]:
    tokens = safe_tokens(query)
    if not tokens:
        raise ValueError("La consulta no contiene términos buscables.")
    if not 1 <= limit <= 100:
        raise ValueError("--limit debe estar entre 1 y 100.")

    where_kind = "" if kind == "todos" else "AND f.kind = ?"
    base_params: list[Any] = [] if kind == "todos" else [kind]

    def run(operator: str) -> list[sqlite3.Row]:
        expression = f" {operator} ".join(f'"{token}"*' for token in tokens)
        return list(
            connection.execute(
                f"""
                SELECT f.case_id, f.kind, bm25(cases_fts) AS score,
                       c.depth, c.path_json, c.result_text
                FROM cases_fts AS f
                JOIN cases AS c ON c.case_id = f.case_id
                WHERE cases_fts MATCH ? {where_kind}
                ORDER BY score, f.case_id
                LIMIT ?
                """,
                [expression, *base_params, limit],
            )
        )

    rows = run("AND")
    match_mode = "todos_los_terminos"
    if not rows and len(tokens) > 1:
        rows = run("OR")
        match_mode = "algun_termino"

    matches = []
    for row in rows:
        path = json.loads(row["path_json"])
        matches.append(
            {
                "case_id": row["case_id"],
                "kind": row["kind"],
                "score": row["score"],
                "depth": row["depth"],
                "answers": [step["answer"] for step in path],
                "result_excerpt": row["result_text"][:500],
            }
        )
    return {
        "query": query,
        "tokens": tokens,
        "match_mode": match_mode,
        "matches": matches,
    }


def candidate_case_ids(
    connection: sqlite3.Connection, kind: str, answers: list[str]
) -> list[str]:
    clauses = ["c.kind = ?"]
    params: list[Any] = [kind]
    for position, answer in enumerate(answers):
        alias = f"s{position}"
        clauses.append(
            f"""EXISTS (
                SELECT 1 FROM steps AS {alias}
                WHERE {alias}.case_id = c.case_id
                  AND {alias}.position = ?
                  AND {alias}.option_value = ?
            )"""
        )
        params.extend((position, answer))
    rows = connection.execute(
        f"SELECT c.case_id FROM cases AS c WHERE {' AND '.join(clauses)} ORDER BY c.case_id",
        params,
    )
    return [row["case_id"] for row in rows]


def next_step(
    connection: sqlite3.Connection, kind: str, answers: list[str]
) -> dict[str, Any]:
    case_ids = candidate_case_ids(connection, kind, answers)
    if not case_ids:
        return {
            "kind": kind,
            "answers": answers,
            "candidate_cases": 0,
            "error": "Ningún recorrido coincide con el prefijo exacto.",
        }

    placeholders = ",".join("?" for _ in case_ids)
    position = len(answers)
    terminal_rows = list(
        connection.execute(
            f"""
            SELECT case_id, result_text FROM cases
            WHERE case_id IN ({placeholders}) AND depth = ?
            ORDER BY case_id
            """,
            [*case_ids, position],
        )
    )
    next_rows = rows_to_dicts(
        connection.execute(
            f"""
            SELECT question, menu_id, option_value, answer,
                   COUNT(*) AS terminal_cases
            FROM steps
            WHERE case_id IN ({placeholders}) AND position = ?
            GROUP BY question, menu_id, option_value, answer
            ORDER BY question, option_value
            """,
            [*case_ids, position],
        )
    )
    terminals = [
        {
            "case_id": row["case_id"],
            "result_text": row["result_text"],
        }
        for row in terminal_rows
    ]
    return {
        "kind": kind,
        "answers": answers,
        "position": position,
        "candidate_cases": len(case_ids),
        "terminal_cases": terminals,
        "next_options": next_rows,
    }


def show_case(connection: sqlite3.Connection, case_id: str) -> dict[str, Any]:
    row = connection.execute(
        """
        SELECT case_id, kind, leaf_node, depth, path_json, result_text,
               clarification_text, links_json
        FROM cases WHERE case_id = ?
        """,
        (case_id,),
    ).fetchone()
    if row is None:
        raise KeyError(f"No existe el caso {case_id!r}.")
    return {
        "case_id": row["case_id"],
        "kind": row["kind"],
        "leaf_node": row["leaf_node"],
        "depth": row["depth"],
        "path": json.loads(row["path_json"]),
        "result_text": row["result_text"],
        "clarification_text": row["clarification_text"],
        "links": json.loads(row["links_json"]),
    }


def main() -> int:
    args = parse_args()
    if not args.db.is_file():
        print(f"No existe el índice: {args.db}", file=sys.stderr)
        return 2

    connection = sqlite3.connect(f"file:{args.db.resolve()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        if args.command == "stats":
            payload = stats(connection)
        elif args.command == "root":
            payload = root_options(connection, args.kind)
        elif args.command == "search":
            payload = search_cases(
                connection, args.kind, args.query, args.limit
            )
        elif args.command == "next":
            payload = next_step(connection, args.kind, args.answer)
        elif args.command == "show":
            payload = show_case(connection, args.case_id)
        else:
            raise AssertionError(args.command)
    except (KeyError, ValueError, sqlite3.Error) as error:
        print(str(error), file=sys.stderr)
        return 2
    finally:
        connection.close()

    emit(payload, args.compact)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

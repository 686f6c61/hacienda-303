#!/usr/bin/env python3
"""Detect exact and near business duplicates in reviewed invoice JSON/JSONL."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from decimal import InvalidOperation
from pathlib import Path
from typing import Any

from aeat_book_common import load_json_records, parse_date, parse_decimal, record_payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detecta duplicados fiscales por proveedor, número, fecha e importe."
    )
    parser.add_argument("input", type=Path)
    return parser.parse_args()


def compact(value: Any) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(value or "").upper())


def normalized_key(item: dict[str, Any]) -> tuple[str, str, str, str, str]:
    book, row = record_payload(item)
    if book == "EXPEDIDAS":
        party = compact(row.get("nif_destinatario"))
        number = compact(f"{row.get('serie') or ''}{row.get('numero') or ''}")
    else:
        party = compact(row.get("nif_expedidor"))
        number = compact(row.get("factura_expedidor_serie_numero"))
    issued = parse_date(row.get("fecha_expedicion"))
    # El total documental vive en el objeto de auditoría (references/output-schema.md).
    total = parse_decimal(item.get("factura_total_documento"))
    if total is None:
        total = parse_decimal(row.get("factura_total_documento"))
    if total is None:
        total = parse_decimal(row.get("total_factura"))
    return (
        book,
        party,
        number,
        issued.isoformat() if issued else "",
        str(total.quantize(parse_decimal("0.01"))) if total is not None else "",
    )


def label(item: dict[str, Any], index: int) -> str:
    return str(item.get("archivo") or item.get("operacion_id") or f"registro-{index}")


def main() -> int:
    records = load_json_records(parse_args().input)
    groups: dict[tuple[str, str, str, str, str], list[str]] = defaultdict(list)
    for index, item in enumerate(records, start=1):
        try:
            key = normalized_key(item)
        except (ValueError, InvalidOperation):
            continue
        if key[1] and key[2] and key[3]:
            groups[key].append(label(item, index))
    duplicates = [
        {"key": key, "records": labels}
        for key, labels in groups.items()
        if len(set(labels)) > 1
    ]
    print(
        json.dumps(
            {
                "records": len(records),
                "duplicate_groups": duplicates,
                "duplicate_group_count": len(duplicates),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 1 if duplicates else 0


if __name__ == "__main__":
    raise SystemExit(main())

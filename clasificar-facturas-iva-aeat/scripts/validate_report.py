#!/usr/bin/env python3
"""Validate the minimum auditability and consistency of classification reports."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


DEFAULT_DATABASE = Path(__file__).resolve().parent.parent / "assets" / "aeat_iva.sqlite"
REQUIRED = {
    "archivo",
    "estado",
    "direccion",
    "tipo_operacion",
    "categoria_aeat",
    "case_id",
    "localizacion_iva",
    "factura_lleva_iva",
    "sujeto_pasivo",
    "tratamiento",
    "modelo_303",
    "confianza",
    "datos_faltantes",
    "evidencias",
    "recorrido_aeat",
    "fuente_aeat",
}
CONFIDENCE = {"alta", "media", "baja", "pendiente"}
DIRECTIONS = {"emitida", "recibida", "desconocida"}
KINDS = {"bienes", "servicios", "mixta", "desconocida"}
STATES = {"clasificacion_preliminar", "clasificacion_concluida"}
EVIDENCE_ORIGINS = {"documento", "usuario", "inferido", "desconocido"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Valida un informe JSON de clasificación de facturas."
    )
    parser.add_argument("report", type=Path)
    parser.add_argument("--db", type=Path, default=DEFAULT_DATABASE)
    return parser.parse_args()


def as_decimal(value: Any) -> Decimal:
    return Decimal(str(value).replace(",", "."))


def validate_amounts(item: dict[str, Any], label: str, errors: list[str]) -> None:
    amounts = item.get("importes")
    if not isinstance(amounts, dict):
        return
    if not {"base", "cuota_iva", "total"}.issubset(amounts):
        return
    try:
        base = as_decimal(amounts["base"])
        tax = as_decimal(amounts["cuota_iva"])
        total = as_decimal(amounts["total"])
    except (InvalidOperation, ValueError):
        errors.append(f"{label}: importes no numéricos")
        return
    if abs((base + tax) - total) > Decimal("0.02"):
        errors.append(
            f"{label}: base + cuota_iva no coincide con total (tolerancia 0,02)"
        )


def main() -> int:
    args = parse_args()
    if not args.report.is_file():
        print(f"No existe el informe: {args.report}", file=sys.stderr)
        return 2
    if not args.db.is_file():
        print(f"No existe el índice: {args.db}", file=sys.stderr)
        return 2

    text = args.report.read_text(encoding="utf-8").strip()
    if args.report.suffix.lower() == ".jsonl":
        try:
            items = [
                json.loads(line) for line in text.splitlines() if line.strip()
            ]
        except json.JSONDecodeError as error:
            print(f"JSONL inválido: {error}", file=sys.stderr)
            return 2
    else:
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as error:
            print(f"JSON inválido: {error}", file=sys.stderr)
            return 2
        items = payload if isinstance(payload, list) else [payload]
    if not all(isinstance(item, dict) for item in items):
        print("El informe debe ser un objeto JSON o una lista de objetos.", file=sys.stderr)
        return 2

    connection = sqlite3.connect(f"file:{args.db.resolve()}?mode=ro", uri=True)
    known_ids = {
        row[0] for row in connection.execute("SELECT case_id FROM cases")
    }
    connection.close()

    errors: list[str] = []
    warnings: list[str] = []
    for index, item in enumerate(items, start=1):
        label = str(item.get("archivo") or f"elemento {index}")
        missing = sorted(REQUIRED.difference(item))
        if missing:
            errors.append(f"{label}: faltan campos {missing}")
            continue
        if item["direccion"] not in DIRECTIONS:
            errors.append(f"{label}: direccion inválida")
        if item["tipo_operacion"] not in KINDS:
            errors.append(f"{label}: tipo_operacion inválido")
        if item["estado"] not in STATES:
            errors.append(f"{label}: estado inválido")
        if item["confianza"] not in CONFIDENCE:
            errors.append(f"{label}: confianza inválida")
        if not isinstance(item["datos_faltantes"], list):
            errors.append(f"{label}: datos_faltantes debe ser una lista")
        if not isinstance(item["evidencias"], list) or not item["evidencias"]:
            errors.append(f"{label}: evidencias debe ser una lista no vacía")
        else:
            for evidence_index, evidence in enumerate(item["evidencias"], start=1):
                if not isinstance(evidence, dict):
                    errors.append(
                        f"{label}: evidencia {evidence_index} no es un objeto"
                    )
                    continue
                if evidence.get("origen") not in EVIDENCE_ORIGINS:
                    errors.append(
                        f"{label}: origen inválido en evidencia {evidence_index}"
                    )
        if not isinstance(item["recorrido_aeat"], list):
            errors.append(f"{label}: recorrido_aeat debe ser una lista")
        if not isinstance(item["fuente_aeat"], dict):
            errors.append(f"{label}: fuente_aeat debe ser un objeto")

        case_id = item["case_id"]
        if case_id and case_id not in known_ids:
            errors.append(f"{label}: case_id desconocido: {case_id}")
        if item["confianza"] == "alta" and item["datos_faltantes"]:
            errors.append(
                f"{label}: no puede tener confianza alta con datos faltantes"
            )
        if not case_id and item["confianza"] in {"alta", "media"}:
            errors.append(
                f"{label}: confianza {item['confianza']} sin caso AEAT terminal"
            )
        if item["estado"] == "clasificacion_concluida" and not case_id:
            errors.append(f"{label}: clasificación concluida sin case_id")
        if item["estado"] == "clasificacion_concluida" and item["datos_faltantes"]:
            errors.append(
                f"{label}: clasificación concluida con datos determinantes pendientes"
            )
        if item["estado"] == "clasificacion_concluida" and not item["recorrido_aeat"]:
            warnings.append(
                f"{label}: clasificación concluida sin recorrido_aeat documentado"
            )
        if item["confianza"] == "pendiente" and not item["datos_faltantes"]:
            warnings.append(
                f"{label}: pendiente sin explicar qué datos faltan"
            )
        validate_amounts(item, label, errors)

    result = {
        "valid": not errors,
        "items": len(items),
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

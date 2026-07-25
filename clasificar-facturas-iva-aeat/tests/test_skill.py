#!/usr/bin/env python3
"""Tests de regresión de la skill (hallazgos de auditoría).

Datos sintéticos mínimos inspirados en references/output-schema.md.
Ejecutar: python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from aeat_book_common import load_catalog, validate_record  # noqa: E402
from ingest_batch import safe_extract_zip, worker_count  # noqa: E402

CATALOG = load_catalog()

PROFILE = {
    "ejercicio": 2026,
    "periodo": "4T",
    "nif": "B12345678",
    "nombre": "EMPRESA SL",
    "catalog_profile": "persona_juridica",
    "periodicidad": "trimestral",
    "sii": False,
    "actividad_default": {"codigo": "A", "tipo": "02", "grupo_epigrafe_iae": "011"},
}

EXPEDIDA_VALIDA = {
    "ejercicio": 2026,
    "periodo": "1T",
    "tipo_factura": "F1",
    "fecha_expedicion": "2026-02-10",
    "numero": "A-1",
    "clave_operacion": "01",
    "calificacion_operacion": "S1",
    "total_factura": "121.00",
    "base_imponible": "100.00",
    "tipo_iva": "21",
    "cuota_iva_repercutida": "21.00",
    "nif_destinatario": "B12345678",
    "nombre_destinatario": "CLIENTE SL",
}

RECIBIDA_VALIDA = {
    "ejercicio": 2026,
    "periodo": "1T",
    "tipo_factura": "F1",
    "fecha_expedicion": "2026-02-10",
    "factura_expedidor_serie_numero": "F-2026-0042",
    "fecha_recepcion": "2026-02-11",
    "numero_recepcion": "R-00042",
    "nif_expedidor": "B87654321",
    "nombre_expedidor": "PROVEEDOR SL",
    "clave_operacion_gasto": "01",
    "total_factura": "121.00",
    "base_imponible": "100.00",
    "tipo_iva": "21",
    "cuota_iva_soportada": "21.00",
    "cuota_deducible": "21.00",
}


def registro_exportable(registro_aeat, **extra):
    item = {
        "archivo": "factura.pdf",
        "operacion_id": "factura.pdf#1",
        "estado": "clasificacion_concluida",
        "libro_aeat": "EXPEDIDAS",
        "registro_aeat": registro_aeat,
    }
    item.update(extra)
    return item


class ValidateRecordTests(unittest.TestCase):
    def test_expedida_f1_valida(self):
        _, errors, _ = validate_record(
            "EXPEDIDAS", dict(EXPEDIDA_VALIDA), PROFILE, CATALOG
        )
        self.assertEqual(errors, [])

    def test_recibida_valida(self):
        _, errors, _ = validate_record(
            "RECIBIDAS", dict(RECIBIDA_VALIDA), PROFILE, CATALOG
        )
        self.assertEqual(errors, [])

    def test_tipo_iva_malformado_no_lanza(self):
        _, errors, _ = validate_record(
            "EXPEDIDAS", {**EXPEDIDA_VALIDA, "tipo_iva": "abc"}, PROFILE, CATALOG
        )
        self.assertTrue(any(e.startswith("tipo_iva:") for e in errors))

    def test_tipo_recargo_malformado_no_lanza(self):
        _, errors, _ = validate_record(
            "EXPEDIDAS",
            {**EXPEDIDA_VALIDA, "tipo_recargo_equivalencia": "abc"},
            PROFILE,
            CATALOG,
        )
        self.assertTrue(
            any(e.startswith("tipo_recargo_equivalencia:") for e in errors)
        )

    def test_perfil_ejercicio_no_numerico_no_lanza(self):
        _, errors, _ = validate_record(
            "EXPEDIDAS",
            dict(EXPEDIDA_VALIDA),
            {**PROFILE, "ejercicio": "abc"},
            CATALOG,
        )
        self.assertTrue(any(e.startswith("perfil:") for e in errors))

    def test_s1_sin_tipo_ni_cuota_es_error(self):
        valores = {
            key: value
            for key, value in EXPEDIDA_VALIDA.items()
            if key not in ("tipo_iva", "cuota_iva_repercutida")
        }
        _, errors, _ = validate_record("EXPEDIDAS", valores, PROFILE, CATALOG)
        self.assertIn("tipo_iva: obligatorio para calificación S1/S2", errors)
        self.assertIn(
            "cuota_iva_repercutida: obligatoria para calificación S1/S2", errors
        )

    def test_s2_sin_tipo_es_error(self):
        valores = {**EXPEDIDA_VALIDA, "calificacion_operacion": "S2"}
        del valores["tipo_iva"]
        _, errors, _ = validate_record("EXPEDIDAS", valores, PROFILE, CATALOG)
        self.assertIn("tipo_iva: obligatorio para calificación S1/S2", errors)

    def test_s1_con_tipo_cero_y_cuota_cero_es_valida(self):
        valores = {
            **EXPEDIDA_VALIDA,
            "tipo_iva": "0",
            "cuota_iva_repercutida": "0",
            "total_factura": "100.00",
        }
        _, errors, _ = validate_record("EXPEDIDAS", valores, PROFILE, CATALOG)
        self.assertEqual(errors, [])

    def test_n1_sin_tipo_ni_cuota_no_exige_iva(self):
        valores = {
            key: value
            for key, value in EXPEDIDA_VALIDA.items()
            if key not in ("tipo_iva", "cuota_iva_repercutida")
        }
        valores["calificacion_operacion"] = "N1"
        _, errors, _ = validate_record("EXPEDIDAS", valores, PROFILE, CATALOG)
        self.assertEqual(errors, [])

    def test_criterio_caja_deriva_por_fecha_cobro(self):
        valores = {
            key: value
            for key, value in EXPEDIDA_VALIDA.items()
            if key not in ("ejercicio", "periodo")
        }
        valores.update(
            {
                "clave_operacion": "07 - Criterio de caja",
                "fecha_cobro": "2026-05-05",
                "importe_cobro": "121.00",
            }
        )
        normalized, errors, _ = validate_record(
            "EXPEDIDAS", valores, PROFILE, CATALOG
        )
        self.assertEqual(errors, [])
        self.assertEqual(normalized["ejercicio"], 2026)
        self.assertEqual(normalized["periodo"], "2T")

    def test_criterio_caja_clave_sin_cero(self):
        valores = {
            key: value
            for key, value in EXPEDIDA_VALIDA.items()
            if key not in ("ejercicio", "periodo")
        }
        valores.update(
            {
                "clave_operacion": "7",
                "fecha_cobro": "2026-05-05",
                "importe_cobro": "121.00",
            }
        )
        normalized, _, _ = validate_record("EXPEDIDAS", valores, PROFILE, CATALOG)
        self.assertEqual(normalized["periodo"], "2T")

    def test_criterio_caja_recibidas_deriva_por_fecha_pago(self):
        valores = {
            key: value
            for key, value in RECIBIDA_VALIDA.items()
            if key not in ("ejercicio", "periodo")
        }
        valores.update(
            {
                "clave_operacion_gasto": "07",
                "fecha_pago": "2026-08-05",
                "importe_pago": "121.00",
            }
        )
        normalized, errors, _ = validate_record(
            "RECIBIDAS", valores, PROFILE, CATALOG
        )
        self.assertEqual(errors, [])
        self.assertEqual(normalized["periodo"], "3T")


class DetectDuplicatesTests(unittest.TestCase):
    def _run(self, records):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "registros.json"
            input_path.write_text(
                json.dumps(records, ensure_ascii=False), encoding="utf-8"
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "detect_invoice_duplicates.py"),
                 str(input_path)],
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.stderr, "")
        return result.returncode, json.loads(result.stdout)

    def test_duplicado_por_total_documental_nivel_objeto(self):
        registro = {
            "fecha_expedicion": "2026-02-10",
            "factura_expedidor_serie_numero": "F-42",
            "nif_expedidor": "B87654321",
            "total_factura": "100.00",
        }
        records = [
            {
                "archivo": "a.pdf",
                "factura_total_documento": "121.00",
                "libro_aeat": "RECIBIDAS",
                "registro_aeat": registro,
            },
            {
                "archivo": "b.pdf",
                "factura_total_documento": "121.00",
                "libro_aeat": "RECIBIDAS",
                "registro_aeat": dict(registro),
            },
        ]
        returncode, payload = self._run(records)
        self.assertEqual(returncode, 1)
        self.assertEqual(payload["duplicate_group_count"], 1)

    def test_importe_malformado_no_lanza(self):
        records = [
            {
                "archivo": "a.pdf",
                "factura_total_documento": "abc",
                "libro_aeat": "RECIBIDAS",
                "registro_aeat": {
                    "fecha_expedicion": "2026-02-10",
                    "factura_expedidor_serie_numero": "F-42",
                    "nif_expedidor": "B87654321",
                },
            }
        ]
        returncode, payload = self._run(records)
        self.assertEqual(returncode, 0)
        self.assertEqual(payload["records"], 1)


class BuildAeatBookTests(unittest.TestCase):
    def _run_build(self, records):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        tmp_path = Path(tmp.name)
        profile_path = tmp_path / "perfil.json"
        profile_path.write_text(
            json.dumps(PROFILE, ensure_ascii=False), encoding="utf-8"
        )
        input_path = tmp_path / "registros.json"
        input_path.write_text(
            json.dumps(records, ensure_ascii=False), encoding="utf-8"
        )
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "build_aeat_book.py"),
                "--input",
                str(input_path),
                "--profile",
                str(profile_path),
                "--output",
                str(tmp_path / "salida.xlsx"),
            ],
            capture_output=True,
            text=True,
        )
        self.assertNotIn("Traceback", result.stderr)
        return result.returncode, json.loads(result.stdout)

    def test_total_documental_no_numerico_emite_json_invalido(self):
        records = [
            registro_exportable(
                dict(EXPEDIDA_VALIDA), factura_total_documento="abc"
            )
        ]
        returncode, payload = self._run_build(records)
        self.assertEqual(returncode, 1)
        self.assertFalse(payload["valid"])
        self.assertTrue(
            any("factura_total_documento" in e for e in payload["errors"])
        )

    def test_tipo_iva_malformado_emite_json_invalido(self):
        records = [
            registro_exportable({**EXPEDIDA_VALIDA, "tipo_iva": "abc"})
        ]
        returncode, payload = self._run_build(records)
        self.assertEqual(returncode, 1)
        self.assertFalse(payload["valid"])
        self.assertTrue(any("tipo_iva" in e for e in payload["errors"]))

    def _factura_multilinea(self, total_linea, lineas=5):
        return [
            registro_exportable(
                {
                    **EXPEDIDA_VALIDA,
                    "numero": f"A-{indice}",
                    "total_factura": total_linea,
                    "base_imponible": "20.00",
                    "cuota_iva_repercutida": "4.20",
                },
                operacion_id=f"factura.pdf#{indice}",
                factura_total_documento="121.00",
            )
            for indice in range(1, lineas + 1)
        ]

    def test_redondeo_acumulado_dentro_de_tolerancia(self):
        # 5 × 24,206 = 121,03: desfase de 0,03 <= 0,01 × 5 líneas.
        returncode, payload = self._run_build(self._factura_multilinea("24.206"))
        self.assertEqual(returncode, 0)
        self.assertTrue(payload["valid"])

    def test_discrepancia_real_falla(self):
        # 5 × 24,40 = 122,00: desfase de 1,00 €, fuera de tolerancia.
        returncode, payload = self._run_build(self._factura_multilinea("24.40"))
        self.assertEqual(returncode, 1)
        self.assertFalse(payload["valid"])
        self.assertTrue(any("no coincide" in e for e in payload["errors"]))


class ReconcileBooksTests(unittest.TestCase):
    def test_fila_malformada_no_borra_acumulado_valido(self):
        records = [
            registro_exportable(dict(EXPEDIDA_VALIDA)),
            registro_exportable(
                {**EXPEDIDA_VALIDA, "numero": "A-2", "base_imponible": "abc"},
                operacion_id="factura.pdf#2",
            ),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "registros.json"
            input_path.write_text(
                json.dumps(records, ensure_ascii=False), encoding="utf-8"
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "reconcile_books.py"),
                    str(input_path),
                ],
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        payload = json.loads(result.stdout)
        self.assertEqual(len(payload["groups"]), 1)
        self.assertEqual(payload["groups"][0]["filas"], 1)
        self.assertEqual(payload["groups"][0]["base"], "100.00")
        self.assertEqual(len(payload["invalid_records"]), 1)


class IngestBatchTests(unittest.TestCase):
    def test_workers_fuera_de_limite_se_rechazan(self):
        for value in ("0", "17", "abc"):
            with self.subTest(value=value), self.assertRaises(
                argparse.ArgumentTypeError
            ):
                worker_count(value)

    @unittest.skipUnless(os.name == "posix", "permisos POSIX no disponibles")
    def test_original_extraido_queda_con_permisos_restringidos(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / "facturas.zip"
            with zipfile.ZipFile(archive, "w") as bundle:
                bundle.writestr("factura.txt", "Factura de prueba")
            extracted = safe_extract_zip(
                archive,
                root / "originals",
                max_entries=10,
                max_file_bytes=1024,
                max_total_bytes=2048,
            )

            self.assertEqual(len(extracted), 1)
            self.assertEqual(extracted[0].stat().st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main()

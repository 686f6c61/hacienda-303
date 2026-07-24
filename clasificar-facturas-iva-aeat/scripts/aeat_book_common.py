"""Shared schema and validation helpers for AEAT electronic VAT books."""

from __future__ import annotations

import json
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parent.parent
ASSET_ROOT = SKILL_ROOT / "assets" / "aeat-2026"
CATALOG_PATH = ASSET_ROOT / "codigos_aeat_2026.json"

EXPEDIDAS_FIELDS = [
    "ejercicio",
    "periodo",
    "actividad_codigo",
    "actividad_tipo",
    "grupo_epigrafe_iae",
    "tipo_factura",
    "concepto_ingreso",
    "ingreso_computable",
    "fecha_expedicion",
    "fecha_operacion",
    "serie",
    "numero",
    "numero_final",
    "nif_destinatario_tipo",
    "nif_destinatario_pais",
    "nif_destinatario",
    "nombre_destinatario",
    "clave_operacion",
    "calificacion_operacion",
    "operacion_exenta",
    "total_factura",
    "base_imponible",
    "tipo_iva",
    "cuota_iva_repercutida",
    "tipo_recargo_equivalencia",
    "cuota_recargo_equivalencia",
    "fecha_cobro",
    "importe_cobro",
    "medio_cobro",
    "identificacion_medio_cobro",
    "tipo_retencion_irpf",
    "importe_retenido_irpf",
    "registro_acuerdo_facturacion",
    "inmueble_situacion",
    "referencia_catastral",
    "referencia_externa",
]

RECIBIDAS_FIELDS = [
    "ejercicio",
    "periodo",
    "actividad_codigo",
    "actividad_tipo",
    "grupo_epigrafe_iae",
    "tipo_factura",
    "concepto_gasto",
    "gasto_deducible",
    "fecha_expedicion",
    "fecha_operacion",
    "factura_expedidor_serie_numero",
    "factura_expedidor_numero_final",
    "fecha_recepcion",
    "numero_recepcion",
    "numero_recepcion_final",
    "nif_expedidor_tipo",
    "nif_expedidor_pais",
    "nif_expedidor",
    "nombre_expedidor",
    "clave_operacion_gasto",
    "bien_inversion",
    "inversion_sujeto_pasivo",
    "deducible_periodo_posterior",
    "periodo_deduccion_ejercicio",
    "periodo_deduccion_periodo",
    "total_factura",
    "base_imponible",
    "tipo_iva",
    "cuota_iva_soportada",
    "cuota_deducible",
    "tipo_recargo_equivalencia",
    "cuota_recargo_equivalencia",
    "fecha_pago",
    "importe_pago",
    "medio_pago",
    "identificacion_medio_pago",
    "tipo_retencion_irpf",
    "importe_retenido_irpf",
    "registro_acuerdo_facturacion",
    "inmueble_situacion",
    "referencia_catastral",
    "referencia_externa",
]

BIENES_INVERSION_FIELDS = [
    "ejercicio",
    "periodo",
    "actividad_codigo",
    "actividad_tipo",
    "grupo_epigrafe_iae",
    "tipo_bien",
    "bien_identificador",
    "bien_descripcion",
    "fecha_inicio_utilizacion",
    "valor_adquisicion",
    "valor_amortizable",
    "metodo_amortizacion",
    "porcentaje_amortizacion",
    "amortizacion_acumulada_inicio",
    "amortizacion_cuota_resultante",
    "amortizacion_acumulada_final",
    "amortizacion_pendiente",
    "fecha_expedicion",
    "factura_expedidor_serie_numero",
    "factura_expedidor_numero_final",
    "numero_recepcion",
    "numero_recepcion_final",
    "nif_expedidor_tipo",
    "nif_expedidor_pais",
    "nif_expedidor",
    "nombre_expedidor",
    "inicio_uso_base_imponible",
    "inicio_uso_tipo_iva",
    "inicio_uso_prorrata_definitiva",
    "inicio_uso_cuota_deducible",
    "regularizacion_prorrata_definitiva",
    "regularizacion_cuota_deducible",
    "regularizacion_cuota",
    "baja_fecha",
    "baja_causa",
    "transmision_serie",
    "transmision_numero",
    "transmision_numero_final",
    "registro_acuerdo_facturacion",
    "inmueble_situacion",
    "referencia_catastral",
    "referencia_externa",
]

FIELDS_BY_BOOK = {
    "EXPEDIDAS": EXPEDIDAS_FIELDS,
    "RECIBIDAS": RECIBIDAS_FIELDS,
    "BIENES-INVERSIÓN": BIENES_INVERSION_FIELDS,
}

DATE_FIELDS = {
    "fecha_expedicion",
    "fecha_operacion",
    "fecha_recepcion",
    "fecha_cobro",
    "fecha_pago",
    "fecha_inicio_utilizacion",
    "baja_fecha",
}
DECIMAL_FIELDS = {
    "ingreso_computable",
    "gasto_deducible",
    "total_factura",
    "base_imponible",
    "tipo_iva",
    "cuota_iva_repercutida",
    "tipo_recargo_equivalencia",
    "cuota_recargo_equivalencia",
    "importe_cobro",
    "importe_pago",
    "tipo_retencion_irpf",
    "importe_retenido_irpf",
    "cuota_iva_soportada",
    "cuota_deducible",
    "valor_adquisicion",
    "valor_amortizable",
    "porcentaje_amortizacion",
    "amortizacion_acumulada_inicio",
    "amortizacion_cuota_resultante",
    "amortizacion_acumulada_final",
    "amortizacion_pendiente",
    "inicio_uso_base_imponible",
    "inicio_uso_tipo_iva",
    "inicio_uso_prorrata_definitiva",
    "inicio_uso_cuota_deducible",
    "regularizacion_prorrata_definitiva",
    "regularizacion_cuota_deducible",
    "regularizacion_cuota",
}
BOOLEAN_FIELDS = {
    "bien_inversion",
    "inversion_sujeto_pasivo",
    "deducible_periodo_posterior",
}

MAX_LENGTHS = {
    "periodo": 2,
    "actividad_codigo": 1,
    "actividad_tipo": 2,
    "grupo_epigrafe_iae": 4,
    "tipo_factura": 2,
    "concepto_ingreso": 3,
    "concepto_gasto": 3,
    "serie": 20,
    "numero": 20,
    "numero_final": 20,
    "factura_expedidor_serie_numero": 40,
    "factura_expedidor_numero_final": 20,
    "numero_recepcion": 20,
    "numero_recepcion_final": 20,
    "nif_destinatario_tipo": 2,
    "nif_expedidor_tipo": 2,
    "nif_destinatario_pais": 2,
    "nif_expedidor_pais": 2,
    "nif_destinatario": 20,
    "nif_expedidor": 20,
    "nombre_destinatario": 40,
    "nombre_expedidor": 40,
    "registro_acuerdo_facturacion": 15,
    "inmueble_situacion": 1,
    "referencia_catastral": 20,
    "referencia_externa": 40,
    "bien_identificador": 40,
    "bien_descripcion": 160,
}

CODE_CATEGORY_BY_FIELD = {
    "actividad_codigo": "ACTIVIDAD",
    "tipo_factura": None,
    "concepto_ingreso": "CONCEPTO INGRESO",
    "concepto_gasto": "CONCEPTO GASTO",
    "nif_destinatario_tipo": "TIPO NIF",
    "nif_expedidor_tipo": "TIPO NIF",
    "clave_operacion": "CLAVE OPERACION",
    "clave_operacion_gasto": "CLAVE OPERACION GASTO",
    "calificacion_operacion": "CALIFICACION OPERACION",
    "operacion_exenta": "OPERACION EXENTA",
    "tipo_iva": "TIPO IVA",
    "tipo_recargo_equivalencia": "TIPO RECARGO EQUIVALENCIA",
    "medio_cobro": "MEDIO UTILIZADO",
    "medio_pago": "MEDIO UTILIZADO",
    "inmueble_situacion": "SITUACION",
    "tipo_bien": "TIPO BIEN",
    "metodo_amortizacion": "METODO AMORTIZACION",
    "baja_causa": "CAUSA BAJA BIEN",
}


def load_catalog(path: Path = CATALOG_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_json_records(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    if path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    payload = json.loads(text)
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("records"), list):
        return payload["records"]
    if isinstance(payload, dict):
        return [payload]
    raise ValueError("El fichero debe contener un objeto, lista o JSONL.")


def normalize_book(value: Any) -> str:
    normalized = str(value or "").strip().upper().replace("_", "-")
    aliases = {
        "EXPEDIDAS-INGRESOS": "EXPEDIDAS",
        "RECIBIDAS-GASTOS": "RECIBIDAS",
        "BIENES-INVERSION": "BIENES-INVERSIÓN",
        "BIENES INVERSIÓN": "BIENES-INVERSIÓN",
    }
    return aliases.get(normalized, normalized)


def normalize_code(value: Any) -> str | None:
    if value is None or value == "":
        return None
    text = str(value).strip()
    match = re.match(r"^([A-Za-z0-9.,]+)\s*-", text)
    if match:
        text = match.group(1)
    return text.replace(",", ".").upper()


def normalize_numeric_code(value: Any) -> str:
    number = parse_decimal(value)
    if number is None:
        return ""
    rendered = format(number.normalize(), "f")
    return "0" if rendered in {"-0", ""} else rendered


def parse_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"fecha inválida: {value!r}")


def parse_decimal(value: Any) -> Decimal | None:
    if value in (None, ""):
        return None
    if isinstance(value, Decimal):
        return value
    text = str(value).strip().replace(" ", "")
    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    else:
        text = text.replace(",", ".")
    try:
        return Decimal(text)
    except InvalidOperation as error:
        raise ValueError(f"decimal inválido: {value!r}") from error


def normalize_boolean(value: Any) -> str | None:
    if value in (None, ""):
        return None
    if isinstance(value, bool):
        return "S" if value else "N"
    text = str(value).strip().upper().replace("Í", "I")
    if text in {"SI", "S", "TRUE", "1"}:
        return "S"
    if text in {"NO", "N", "FALSE", "0"}:
        return "N"
    raise ValueError(f"booleano S/N inválido: {value!r}")


def quarter_for_date(value: date) -> str:
    return f"{((value.month - 1) // 3) + 1}T"


def period_key(year: int, period: str) -> tuple[int, int]:
    order = {"1T": 1, "2T": 2, "3T": 3, "4T": 4, "0A": 4}
    return year, order[period]


def derive_autoliquidation(
    book: str, values: dict[str, Any], profile: dict[str, Any]
) -> None:
    if values.get("ejercicio") not in (None, "") and values.get("periodo") not in (
        None,
        "",
    ):
        return
    relevant: date | None = None
    if book == "EXPEDIDAS":
        if values.get("clave_operacion") == "07" and values.get("fecha_cobro"):
            relevant = values["fecha_cobro"]
        else:
            relevant = values.get("fecha_operacion") or values.get("fecha_expedicion")
    elif book == "RECIBIDAS":
        if values.get("clave_operacion_gasto") == "07" and values.get("fecha_pago"):
            relevant = values["fecha_pago"]
        else:
            relevant = values.get("fecha_recepcion") or values.get("fecha_expedicion")
    if relevant:
        values.setdefault("ejercicio", relevant.year)
        values.setdefault("periodo", quarter_for_date(relevant))
    elif book == "BIENES-INVERSIÓN":
        values.setdefault("ejercicio", profile.get("ejercicio"))
        values.setdefault("periodo", profile.get("periodo"))


def record_payload(item: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    nested = item.get("registro_aeat")
    if isinstance(nested, dict):
        book = normalize_book(item.get("libro_aeat") or nested.get("libro"))
        values = {key: value for key, value in nested.items() if key != "libro"}
        return book, values
    book = normalize_book(item.get("libro_aeat") or item.get("libro"))
    return book, item


def apply_profile_defaults(
    book: str, values: dict[str, Any], profile: dict[str, Any]
) -> dict[str, Any]:
    result = dict(values)
    activity = profile.get("actividad_default") or {}
    result.setdefault("actividad_codigo", activity.get("codigo"))
    result.setdefault("actividad_tipo", activity.get("tipo"))
    result.setdefault("grupo_epigrafe_iae", activity.get("grupo_epigrafe_iae"))
    return result


def code_sets(
    catalog: dict[str, Any], profile_key: str
) -> dict[str, set[str]]:
    categories = catalog["profiles"][profile_key]
    return {
        category: {normalize_code(item["code"]) or "" for item in items}
        for category, items in categories.items()
    }


def validate_record(
    book: str,
    values: dict[str, Any],
    profile: dict[str, Any],
    catalog: dict[str, Any],
) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if book not in FIELDS_BY_BOOK:
        return values, [f"libro no admitido: {book!r}"], warnings
    profile_key = profile.get("catalog_profile", "persona_juridica")
    if profile_key not in catalog["profiles"]:
        return values, [f"catalog_profile desconocido: {profile_key!r}"], warnings
    codes = code_sets(catalog, profile_key)
    normalized = apply_profile_defaults(book, values, profile)

    for field in FIELDS_BY_BOOK[book]:
        value = normalized.get(field)
        try:
            if field in DATE_FIELDS:
                normalized[field] = parse_date(value)
            elif field in DECIMAL_FIELDS:
                normalized[field] = parse_decimal(value)
            elif field in BOOLEAN_FIELDS:
                normalized[field] = normalize_boolean(value)
        except ValueError as error:
            errors.append(f"{field}: {error}")

    derive_autoliquidation(book, normalized, profile)

    required_common = {
        "ejercicio",
        "periodo",
        "actividad_codigo",
    }
    required = set(required_common)
    if book == "EXPEDIDAS":
        required.update(
            {
                "tipo_factura",
                "fecha_expedicion",
                "numero",
                "clave_operacion",
                "total_factura",
                "base_imponible",
            }
        )
    elif book == "RECIBIDAS":
        required.update(
            {
                "tipo_factura",
                "fecha_expedicion",
                "factura_expedidor_serie_numero",
                "fecha_recepcion",
                "numero_recepcion",
                "nombre_expedidor",
                "clave_operacion_gasto",
                "total_factura",
                "base_imponible",
            }
        )
    else:
        required.update(
            {
                "tipo_bien",
                "bien_descripcion",
                "fecha_inicio_utilizacion",
                "valor_adquisicion",
            }
        )
    for field in sorted(required):
        if normalized.get(field) in (None, ""):
            errors.append(f"{field}: obligatorio")

    year = normalized.get("ejercicio")
    try:
        year_int = int(year)
        if not 2000 <= year_int <= 2100:
            raise ValueError
        normalized["ejercicio"] = year_int
    except (TypeError, ValueError):
        errors.append("ejercicio: debe ser un año de cuatro cifras")

    period = normalize_code(normalized.get("periodo"))
    valid_periods = (
        {"4T", "0A"}
        if book == "BIENES-INVERSIÓN"
        else {"1T", "2T", "3T", "4T"}
    )
    if period and period not in valid_periods:
        errors.append(
            f"periodo: {book} admite {', '.join(sorted(valid_periods))}"
        )
    normalized["periodo"] = period

    cutoff_year = profile.get("ejercicio")
    cutoff_period = normalize_code(profile.get("periodo"))
    if (
        isinstance(normalized.get("ejercicio"), int)
        and period in valid_periods
        and cutoff_year not in (None, "")
        and cutoff_period in {"1T", "2T", "3T", "4T"}
    ):
        if period_key(normalized["ejercicio"], period) > period_key(
            int(cutoff_year), cutoff_period
        ):
            errors.append(
                "autoliquidación posterior al ejercicio/periodo de corte del perfil"
            )

    for field, category in CODE_CATEGORY_BY_FIELD.items():
        if field not in normalized or normalized.get(field) in (None, ""):
            continue
        actual_category = category
        if field == "tipo_factura":
            actual_category = (
                "TIPO FACTURA"
                if book == "EXPEDIDAS"
                else "TIPO FACTURA GASTO"
            )
        value = normalize_code(normalized[field])
        if actual_category in {"TIPO IVA", "TIPO RECARGO EQUIVALENCIA"}:
            value = normalize_numeric_code(normalized[field])
        normalized[field] = value
        if actual_category and value not in codes.get(actual_category, set()):
            errors.append(
                f"{field}: código {value!r} no existe en {actual_category}"
            )

    activity_code = normalize_code(normalized.get("actividad_codigo"))
    activity_type = normalize_code(normalized.get("actividad_tipo"))
    normalized["actividad_codigo"] = activity_code
    normalized["actividad_tipo"] = activity_type
    if activity_code in {"A", "B"}:
        if activity_type not in codes.get(activity_code, set()):
            errors.append(
                f"actividad_tipo: {activity_type!r} no válido para actividad {activity_code}"
            )
    elif activity_code in {"C", "D"} and activity_type:
        warnings.append(
            f"actividad_tipo se dejará vacío para actividad {activity_code}"
        )
        normalized["actividad_tipo"] = None

    epigraph = normalized.get("grupo_epigrafe_iae")
    if epigraph not in (None, ""):
        epigraph_text = str(epigraph).strip()
        normalized["grupo_epigrafe_iae"] = epigraph_text
        activity_key = f"{activity_code or ''}{activity_type or ''}"
        allowed_epigraphs = {
            str(item["grupo_epigrafe"]).lstrip("0") or "0"
            for item in catalog.get("actividades_economicas", [])
            if item.get("codigo_actividad") == activity_key
        }
        if allowed_epigraphs and (
            epigraph_text.lstrip("0") or "0"
        ) not in allowed_epigraphs:
            errors.append(
                f"grupo_epigrafe_iae: {epigraph_text!r} no corresponde a {activity_key}"
            )

    for field in ("nif_destinatario_pais", "nif_expedidor_pais"):
        value = normalized.get(field)
        if value:
            country = str(value).strip().upper()
            if not re.fullmatch(r"[A-Z]{2}", country):
                errors.append(f"{field}: debe ser ISO 3166-1 alpha-2")
            normalized[field] = country

    for field in (
        "nif_destinatario",
        "nif_expedidor",
        "numero",
        "factura_expedidor_serie_numero",
    ):
        if normalized.get(field) is not None:
            normalized[field] = re.sub(
                r"[-./\s]" if field.startswith("nif_") else r"^\s+|\s+$",
                "",
                str(normalized[field]),
            )

    for field, maximum in MAX_LENGTHS.items():
        value = normalized.get(field)
        if value not in (None, "") and len(str(value)) > maximum:
            errors.append(f"{field}: supera {maximum} caracteres")

    for prefix in ("destinatario", "expedidor"):
        type_field = f"nif_{prefix}_tipo"
        country_field = f"nif_{prefix}_pais"
        id_field = f"nif_{prefix}"
        id_type = normalized.get(type_field)
        identifier = normalized.get(id_field)
        country = normalized.get(country_field)
        if id_type in (None, "01") and identifier:
            if not re.fullmatch(r"[A-Z0-9]{9}", str(identifier).upper()):
                errors.append(f"{id_field}: formato NIF/NIE español no válido")
        elif id_type in {"03", "04", "05", "06"} and not country:
            errors.append(f"{country_field}: obligatorio para tipo {id_type}")
        if id_type in {"02", "03", "04", "05", "06"} and not identifier:
            errors.append(f"{id_field}: obligatorio para tipo {id_type}")

    if book == "RECIBIDAS":
        issued = normalized.get("fecha_expedicion")
        received = normalized.get("fecha_recepcion")
        if issued and received and received < issued:
            errors.append("fecha_recepcion: no puede ser anterior a fecha_expedicion")
        later = normalized.get("deducible_periodo_posterior")
        deduction_year = normalized.get("periodo_deduccion_ejercicio")
        deduction_period = normalize_code(normalized.get("periodo_deduccion_periodo"))
        normalized["periodo_deduccion_periodo"] = deduction_period
        if (deduction_year in (None, "")) != (deduction_period in (None, "")):
            errors.append(
                "periodo_deduccion: ejercicio y periodo deben informarse juntos"
            )
        if deduction_year not in (None, "") and later != "S":
            errors.append(
                "deducible_periodo_posterior debe ser S al informar periodo de deducción"
            )
        if deduction_year not in (None, "") and deduction_period:
            try:
                if period_key(int(deduction_year), deduction_period) <= period_key(
                    normalized["ejercicio"], normalized["periodo"]
                ):
                    errors.append(
                        "periodo_deduccion: debe ser posterior al de autoliquidación"
                    )
            except (KeyError, TypeError, ValueError):
                errors.append("periodo_deduccion: ejercicio o periodo inválido")

    if book == "EXPEDIDAS":
        if normalized.get("tipo_factura") == "F1":
            if not normalized.get("nombre_destinatario"):
                errors.append("nombre_destinatario: obligatorio para F1")
            if not normalized.get("nif_destinatario"):
                errors.append("nif_destinatario: obligatorio para F1")
        if normalized.get("calificacion_operacion") in {"S1", "S2"}:
            if normalized.get("operacion_exenta"):
                errors.append(
                    "operacion_exenta no debe coexistir con calificación S1/S2"
                )
        elif normalized.get("operacion_exenta") and normalized.get(
            "calificacion_operacion"
        ):
            warnings.append(
                "revise la combinación de calificación y operación exenta"
            )
    if book == "RECIBIDAS":
        if normalized.get("tipo_factura") == "F1" and not normalized.get(
            "nif_expedidor"
        ):
            errors.append("nif_expedidor: obligatorio para F1")
        supported = normalized.get("cuota_iva_soportada")
        deductible = normalized.get("cuota_deducible")
        if (
            supported is not None
            and deductible is not None
            and abs(deductible) > abs(supported)
        ):
            warnings.append("cuota_deducible supera cuota_iva_soportada")

    base = normalized.get("base_imponible")
    rate = normalized.get("tipo_iva")
    if book == "EXPEDIDAS":
        tax = normalized.get("cuota_iva_repercutida")
    elif book == "RECIBIDAS":
        tax = normalized.get("cuota_iva_soportada")
    else:
        base = normalized.get("inicio_uso_base_imponible")
        rate = normalized.get("inicio_uso_tipo_iva")
        tax = None
    if base is not None and rate is not None and tax is not None:
        numeric_rate = parse_decimal(rate)
        expected_tax = (
            base * numeric_rate / Decimal("100")
        ).quantize(Decimal("0.01"))
        if abs(expected_tax - tax) > Decimal("0.02"):
            warnings.append(
                "cuota IVA no coincide con base × tipo dentro de tolerancia 0,02"
            )

    return normalized, errors, warnings


def excel_value(field: str, value: Any) -> Any:
    if value is None:
        return None
    if field in DATE_FIELDS:
        return value
    if field in DECIMAL_FIELDS:
        return float(value)
    if field in {"nif_destinatario_tipo", "nif_expedidor_tipo"} and value == "01":
        return None
    return value

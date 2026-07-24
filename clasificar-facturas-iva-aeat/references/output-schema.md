# Esquema de salida

Usar un objeto por operación, no necesariamente por archivo. Si una factura contiene varias operaciones con tratamiento distinto, repetir `archivo` y asignar un `operacion_id` diferente.

## JSON mínimo

```json
{
  "archivo": "factura.pdf",
  "operacion_id": "factura.pdf#1",
  "estado": "clasificacion_preliminar",
  "direccion": "recibida",
  "tipo_operacion": "servicios",
  "categoria_aeat": "08 Servicios vía electrónica",
  "case_id": null,
  "localizacion_iva": null,
  "factura_lleva_iva": null,
  "sujeto_pasivo": null,
  "tratamiento": null,
  "modelo_303": {
    "modelo": null,
    "casillas": [],
    "nota": "No determinadas hasta cerrar el recorrido"
  },
  "confianza": "pendiente",
  "datos_faltantes": [
    "Condición empresarial del destinatario",
    "Establecimiento que recibe el servicio"
  ],
  "evidencias": [
    {
      "campo": "categoria_aeat",
      "valor": "08 Servicios vía electrónica",
      "origen": "documento",
      "detalle": "Concepto: suscripción de software en línea"
    }
  ],
  "recorrido_aeat": [],
  "importes": {
    "moneda": "EUR",
    "base": "100.00",
    "cuota_iva": "0.00",
    "total": "100.00"
  },
  "alertas": [],
  "fuente_aeat": {
    "periodo_herramienta": "2023-2026",
    "extraido_el": "2026-07-09",
    "sha256": null
  }
}
```

## Valores normalizados

- `estado`: `clasificacion_preliminar` o `clasificacion_concluida`.
- `direccion`: `emitida`, `recibida` o `desconocida`.
- `tipo_operacion`: `bienes`, `servicios`, `mixta` o `desconocida`.
- `confianza`: `alta`, `media`, `baja` o `pendiente`.
- `origen` de una evidencia: `documento`, `usuario`, `inferido` o `desconocido`.

Usar `null` para un dato aún no determinado. No usar una cadena vacía, `N/A` o una afirmación provisional como si fuera un valor final.

## Lotes

Mantener el JSON completo como registro de auditoría. Para CSV o Excel, aplanar como mínimo:

`archivo`, `operacion_id`, `estado`, `direccion`, `emisor`, `nif_emisor`, `destinatario`, `nif_destinatario`, `fecha`, `numero`, `tipo_operacion`, `categoria_aeat`, `case_id`, `localizacion_iva`, `factura_lleva_iva`, `sujeto_pasivo`, `tratamiento`, `casillas_303`, `base`, `cuota_iva`, `total`, `confianza`, `datos_faltantes`, `alertas`.

## Registro para el libro AEAT

Añadir estos campos solo después de revisar la clasificación:

```json
{
  "estado": "clasificacion_concluida",
  "libro_aeat": "RECIBIDAS",
  "registro_aeat": {
    "ejercicio": 2026,
    "periodo": "1T",
    "actividad_codigo": "A",
    "actividad_tipo": "03",
    "grupo_epigrafe_iae": "849",
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
    "cuota_deducible": "21.00"
  }
}
```

Los nombres y el orden completo están en `scripts/aeat_book_common.py`: 36 columnas para `EXPEDIDAS`, 42 para `RECIBIDAS` y 42 para la plantilla actual de `BIENES-INVERSIÓN`. El validador también reconoce el diseño LSI/LSIJ anterior de 40 columnas. Omitir un campo opcional o usar `null`; no inventar valores.

La `cuota_deducible` no se copia automáticamente de la soportada: requiere confirmar afectación, limitaciones y prorrata. `numero_recepcion` es la numeración interna correlativa del libro, no necesariamente el número del proveedor.

Para varias líneas de una misma factura, añadir `factura_total_documento` al objeto de auditoría y consignar en cada `registro_aeat.total_factura` el subtotal de esa línea. La suma de subtotales debe coincidir con `factura_total_documento`.

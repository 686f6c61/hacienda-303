# Libros registro AEAT 2026

## Fuentes oficiales incorporadas

Los ficheros de `assets/aeat-2026/` se descargaron el 24-07-2026 y están identificados por URL y SHA-256 en `manifest.json`.

- Formato electrónico común: <https://sede.agenciatributaria.gob.es/static_files/Sede/Tema/IVA/Fact_registro/Libros_registro/Formato_Electronico_Comun_Libros_Registro_IVA_IRPF.pdf>
- Plantillas 2026: <https://sede.agenciatributaria.gob.es/Sede/iva/pre-303/nuevo-servicio-pre303-importacion-libros-electronico/plantilla-libros-soporte-electronico.html>
- Especificaciones de cálculo: <https://sede.agenciatributaria.gob.es/Sede/iva/pre-303/nuevo-servicio-pre303-importacion-libros-electronico/especificaciones-calculo-casillas.html>
- Servicio del libro electrónico: <https://sede.agenciatributaria.gob.es/Sede/iva/facturacion-registro/libros-registro-iva/libro-registro-soporte-electronico.html>

## Formato generado

- Un único `.xlsx`, nunca CSV, ODS ni XLS.
- Hojas mínimas `EXPEDIDAS` y `RECIBIDAS`, o sus equivalentes unificados.
- Hoja opcional `BIENES-INVERSIÓN`.
- Máximo 4 MB para importación Pre303.
- Datos acumulados desde el 1 de enero hasta el final del trimestre.
- Una fila por combinación fiscal. Si hay varios tipos, conceptos, pagos/cobros o inmuebles, distribuir el total y los importes computables en subtotales; la suma de líneas debe reproducir la factura.
- Identificación extranjera con tipo oficial 02 a 06 y país ISO alfa-2 cuando corresponda.
- El total no se reduce por retenciones de IRPF.

`codigos_aeat_2026.json` contiene catálogos extraídos de las plantillas: 209 códigos repartidos por categorías para persona jurídica, 211 para libro unificado y 908 correspondencias de actividad/epígrafe.

## Perfil mínimo

```json
{
  "ejercicio": 2026,
  "periodo": "1T",
  "nif": "B12345678",
  "nombre": "EMPRESA SL",
  "catalog_profile": "persona_juridica",
  "periodicidad": "trimestral",
  "sii": false,
  "actividad_default": {
    "codigo": "A",
    "tipo": "03",
    "grupo_epigrafe_iae": "849"
  }
}
```

`catalog_profile` admite `persona_juridica` o `unificado_iva_irpf`. No inferir actividad, epígrafe, periodicidad ni SII de una factura.

`periodo` representa el corte máximo del libro. Cada asiento conserva o deriva su propio ejercicio/periodo; un libro hasta 4T contiene normalmente registros 1T, 2T, 3T y 4T.

## Códigos sensibles

Comprobar siempre en el catálogo el tipo de factura, las claves de operación/operación de gasto, calificación `S1`/`S2`/`N1`/`N2`, exención `E1` a `E6`, identificación, tipos de IVA/recargo, conceptos y actividad.

No todos los campos son obligatorios siempre. Importaciones, rectificativas, exentas e inversiones del sujeto pasivo requieren revisión específica.

## Validación

`validate_aeat_book.py` detecta tanto el encabezado compacto de tres filas como el diseño completo LSI/LSIJ con datos desde la fila 11. Con `--strict-import` rechaza hojas y columnas internas.

La plantilla editable 2026 contiene 42 columnas de bienes de inversión, mientras que LSI/LSIJ y diseños anteriores contienen 40. El exportador actual genera 42 y el validador acepta ambos sin desplazar `Referencia Externa`.

Mantener dos artefactos:

- auditoría: puede incluir origen, SHA-256, `case_id`, confianza y alertas;
- importación: solo hojas y columnas admitidas.

Para limpiar un libro enriquecido:

```bash
python3 <skill-root>/scripts/prepare_aeat_import.py <auditoria.xlsx> \
  --output <destino>
```

Después se utiliza el servicio oficial de validación. Un resultado local válido solo significa “apto para pasar a validación AEAT”.

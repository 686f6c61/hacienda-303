---
name: clasificar-facturas-iva-aeat
description: Ingiere localmente y clasifica facturas emitidas o recibidas para IVA español usando los localizadores AEAT 2023-2026 y prepara, tras revisión, libros separados de auditoría e importación XLSX AEAT 2026 para Pre303. Usar con una factura o lotes confidenciales en ZIP/carpetas, PDF, JPEG/fotos, XML, Facturae o texto; para OCR reanudable, duplicados, localización, exención, inversión del sujeto pasivo, periodos, códigos oficiales, conciliación y borrador del libro de IVA. No usar para presentar el 303, buscar datos privados en Internet, decidir deducibilidad sin perfil fiscal ni sustituir la validación oficial AEAT.
---

# Clasificar facturas IVA AEAT

Convertir facturas heterogéneas en operaciones trazables y, después de revisión, en el libro electrónico oficial. No convertir una descripción plausible en una conclusión fiscal: inferir solo datos respaldados por la factura o confirmados por el usuario.

## Elegir el flujo

- Una o pocas facturas: seguir **Clasificación fiscal**.
- ZIP, carpeta o lote grande: ejecutar primero **Ingestión por lotes**.
- Petición de libro de IVA o Pre303: completar además **Perfil fiscal y exportación**.
- Petición de “hacer el 303”: preparar libro, conciliación y pendientes; detenerse antes de firma o presentación.

## Ingestión por lotes

Leer [references/batch-workflow.md](references/batch-workflow.md). Conservar los originales y crear un área de trabajo distinta:

```bash
python3 <skill-root>/scripts/ingest_batch.py <zip-o-carpeta> \
  --output <directorio-trabajo> --ocr auto --privacy-mode local-only
```

El manifiesto usa SHA-256, registra duplicados, ficheros ignorados y calidad OCR, y guarda el texto por huella. Revisar todo registro `needs_review`. Procesar por bloques manejables, conservar resultados en JSONL y reanudar sin repetir OCR ya completado. No extraer ZIP con rutas inseguras, ejecutar contenido ni consultar Internet en modo local.

## Clasificación fiscal

1. Inventariar sin alterar originales. Distinguir duplicado binario de posible factura duplicada por número, emisor, fecha e importe.
2. Extraer por factura:
   - emisor, destinatario, NIF/VAT ID y países;
   - fecha, número y sentido emitida/recibida;
   - conceptos, cantidades y lugares mencionados;
   - base, tipo, cuota y total;
   - menciones legales, exención, inversión del sujeto pasivo y regímenes especiales.
3. Marcar cada dato como `documento`, `usuario`, `inferido` o `desconocido`.
4. Separar líneas con tratamientos distintos. Tratar una factura mixta como varias operaciones.
5. Decidir `bienes` o `servicios`. Si depende de hechos ausentes, mantener `desconocida` y preguntar.
6. Consultar el índice:

```bash
python3 <skill-root>/scripts/query_index.py stats
python3 <skill-root>/scripts/query_index.py root --kind servicios
python3 <skill-root>/scripts/query_index.py search --kind servicios \
  --query "descripción de la operación"
python3 <skill-root>/scripts/query_index.py next --kind servicios --answer 8
python3 <skill-root>/scripts/query_index.py show \
  --case-id servicios_2023_2026__...
```

7. Usar `search` solo para candidatos. Concluir exclusivamente mediante un recorrido exacto con `next` hasta un caso terminal y confirmar su `result_text` con `show`.
8. Formular juntas las preguntas mínimas que separan candidatos. No pedir datos que no cambien el resultado.
9. Emitir `clasificacion_preliminar` si falta un hecho determinante; usar `clasificacion_concluida` solo con `case_id` terminal y respuestas documentadas.
10. Validar el informe:

```bash
python3 <skill-root>/scripts/validate_report.py <informe.json>
python3 <skill-root>/scripts/detect_invoice_duplicates.py <informe.jsonl>
```

Leer [references/fiscal-guardrails.md](references/fiscal-guardrails.md) antes de concluir casos dudosos, inmobiliarios, triangulares, con importación, exportación, plataforma, régimen especial o prorrata. Leer [references/output-schema.md](references/output-schema.md) al crear el JSON.

## Perfil fiscal y exportación

Antes de producir un libro, leer [references/aeat-books-2026.md](references/aeat-books-2026.md) y [references/pre303-boundaries.md](references/pre303-boundaries.md).

1. Confirmar: ejercicio y periodo de corte, NIF, nombre, persona jurídica o libro unificado IVA/IRPF, periodicidad, SII y actividad/epígrafe. El periodo de corte no se copia a todas las facturas.
2. Confirmar por registro el libro y los datos que no salgan de la factura: clave, calificación/exención, deducibilidad, bien de inversión, prorrata o periodo posterior.
3. Asignar códigos solo desde `assets/aeat-2026/codigos_aeat_2026.json`. No inventar literales ni reutilizar códigos entre expedidas y recibidas.
4. Exportar únicamente registros `clasificacion_concluida`:

```bash
python3 <skill-root>/scripts/build_aeat_book.py \
  --input <registros-revisados.jsonl> \
  --profile <perfil.json> \
  --output <directorio-o-libro.xlsx> \
  --audit-output <directorio-auditoria>
```

5. Validar y conciliar:

```bash
python3 <skill-root>/scripts/validate_aeat_book.py <libro.xlsx> \
  --profile <perfil.json> --strict-import
python3 <skill-root>/scripts/reconcile_books.py \
  <registros-revisados.jsonl> --period 1T --profile <perfil.json>
```

6. Pasar el XLSX por el Servicio de validación de Libros Registro de la AEAT. La validación local no lo sustituye.
7. Importar en Pre303 solo si el contribuyente puede usarlo, revisar sus casillas y añadir los datos no derivados de facturas.
8. Obtener aprobación expresa antes de presentar.

## Reglas de decisión

- Mapear normalmente emisor a proveedor y destinatario a cliente, pero verificar autofacturación, suplidos, intermediación y facturación por terceros.
- Distinguir TAI de España, Canarias, Ceuta, Melilla, Unión Europea y terceros territorios.
- No equiparar país del NIF con establecimiento que interviene.
- No deducir la condición de empresario solo por un NIF-IVA.
- No afirmar una casilla 303 si el resultado AEAT no la indica o falta el perfil fiscal.
- No rellenar un código por similitud semántica: comprobarlo en el catálogo incorporado.
- Una factura con varios tipos, conceptos, cobros/pagos o inmuebles ocupa varias líneas. Distribuir `Total Factura` y los importes computables en subtotales cuya suma sea el total documental; no repetir el total completo.
- El libro para Pre303 es acumulado desde inicio de año hasta el trimestre, no solo el trimestre aislado.
- Derivar ejercicio/periodo por operación o recepción y respetar las excepciones de criterio de caja, IVA pendiente y deducción posterior.
- No decidir deducibilidad, afectación, prorrata, regularización de bienes de inversión ni cuenta contable con los localizadores.
- Mantener literalmente el resultado AEAT y separar la interpretación del agente.
- Incluir la fecha y huella de la fuente mostradas por `stats`.
- Advertir que el corpus del localizador es 2023-2026, extraído el 09-07-2026, y comprobar vigencia antes de presentar.

## Confianza

- `alta`: recorrido terminal, hechos respaldados y aritmética coherente.
- `media`: recorrido terminal, con inferencia no documental que no cambia ramas relevantes.
- `baja`: candidato probable sin hechos suficientes.
- `pendiente`: faltan preguntas que pueden cambiar localización, sujeto pasivo, exención o IVA.

Nunca usar `alta` con `datos_faltantes`.

## Entrega

Dar primero un resumen. Después, una fila por operación y preguntas pendientes. En lotes, contar clasificadas, pendientes fiscales, pendientes de revisión OCR, inconsistencias y duplicados.

Entregar manifiesto, JSON/JSONL, libro de auditoría, copia estricta de importación AEAT, validación y conciliación. Nunca importar el libro de auditoría. No contabilizar ni presentar automáticamente.

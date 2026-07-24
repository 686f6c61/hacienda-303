# Flujo para ZIP, carpetas y cientos de facturas

## Recepción segura

- No modificar ni renombrar originales.
- Guardar el ZIP o árbol recibido como evidencia.
- Crear un directorio de trabajo separado.
- Rechazar rutas absolutas, `..`, enlaces simbólicos y expansiones excesivas.
- No ejecutar macros, JavaScript de PDF, adjuntos ni ejecutables.

`ingest_batch.py` acepta ZIP, carpeta o archivo; reconoce PDF, JPEG, PNG, TIFF, BMP, WebP, XML/Facturae y texto. Limita el ZIP, admite hasta dos niveles anidados y funciona solo en modo local.

## Inventario y OCR

El manifiesto conserva ruta, tamaño, tipo aparente, SHA-256, duplicados, método de extracción, páginas, caracteres, errores, ficheros ignorados, `quality_flags`, `needs_review` y ruta al texto.

Los PDF con texto se extraen directamente. Si producen menos de 80 caracteres, `--ocr auto` aplica OCR en español e inglés. Las fotos se corrigen según orientación EXIF.

Marcar para revisión manual NIF/número/fecha dudosos, descuadres, texto corto, páginas ausentes, imagen borrosa o recortada, manuscritos y moneda/signo ambiguos.

## Unidad de trabajo

Una factura puede ocupar varios archivos y un PDF puede contener varias facturas. Resolver la agrupación antes de clasificar. Una factura puede generar varias operaciones y filas si contiene tipos o tratamientos distintos.

Procesar en bloques de unas 25:

1. extracción documental;
2. duplicados fiscales;
3. recorrido AEAT;
4. preguntas pendientes;
5. revisión humana;
6. escritura incremental JSONL.

No exportar al libro filas pendientes.

## Reanudación y control

`--resume` conserva textos y evita repetir OCR para huellas ya completadas, aunque recalcula el inventario para detectar cambios. Registrar total recibido, no soportados, documentos sin texto, facturas identificadas, operaciones, concluidas, pendientes, duplicados y sumas por libro.

Después de revisar y estructurar los documentos, ejecutar `detect_invoice_duplicates.py`. Agrupa por libro, identificación fiscal, número, fecha e importe documental y no confunde líneas distintas del mismo archivo con copias distintas.

La suma de facturas no coincide necesariamente con filas: una factura con tres tipos de IVA produce tres filas.

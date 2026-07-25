# Changelog

Todos los cambios relevantes de Hacienda 303 se documentan en este archivo.
El proyecto sigue [Versionado Semántico](https://semver.org/lang/es/).

## [1.1.0] - 2026-07-25

### Corregido

- La conciliación conserva los importes válidos ya acumulados cuando una fila
  posterior del mismo grupo contiene un importe malformado.
- Los importes y datos fiscales no válidos producen errores revisables en JSON
  en lugar de trazas o abortos inesperados.
- La detección de duplicados utiliza también el total documental situado en el
  nivel del objeto de factura.
- Las operaciones `S1` y `S2` exigen tipo y cuota de IVA, incluido el caso
  legítimo de tipo cero.
- El criterio de caja deriva el periodo desde cobros o pagos y acepta claves
  normalizadas con o sin cero inicial.
- La tolerancia de redondeo de facturas multilínea se aplica al conjunto de
  líneas sin ocultar discrepancias reales.

### Seguridad y privacidad

- El presupuesto de extracción se comparte entre ZIP principales y anidados.
- La extracción controla los bytes reales escritos, además del tamaño declarado
  en la cabecera del ZIP.
- Los originales extraídos, textos, manifiestos y libros generados quedan con
  permisos restringidos cuando el sistema admite permisos POSIX.
- El número de procesos concurrentes queda limitado entre 1 y 16.
- El análisis XML utiliza `defusedxml` y rechaza DTD o entidades peligrosas.

### Calidad y distribución

- Se incorporan 21 pruebas de regresión para validación fiscal, libros AEAT,
  duplicados, conciliación, ZIP y permisos.
- La integración continua ejecuta la suite completa, compila los scripts y
  comprueba la cobertura e integridad del índice SQLite.
- Se añade `pyproject.toml` y se declara `defusedxml` en las dependencias de
  instalación.
- La landing incorpora navegación con iconos, SEO por página, cabeceras de
  seguridad y un changelog visual compartido por todas sus páginas.

## [1.0.0] - 2026-07-25

### Añadido

- Skill completa para lotes de facturas en ZIP, carpetas, PDF, imágenes,
  Facturae/XML y texto.
- Adaptadores de agente para OpenAI/Codex, Claude, Kimi K3 y Z.ai GLM 5.2.
- Arranque directo en Claude Code con `CLAUDE.md`, instalación personal y la
  pregunta inicial “¿Cómo empiezo?”.
- Ingestión local segura con SHA-256, OCR reanudable, indicadores de calidad y
  detección de duplicados.
- Índice SQLite con 3.069 casos terminales y 21.679 pasos de los localizadores
  públicos AEAT 2023–2026.
- Plantillas y catálogo de códigos de Libros Registro AEAT 2026.
- Generadores separados para libro de auditoría y XLSX estricto de importación.
- Validación estructural, conciliación previa a Pre303 y guardrails fiscales.
- Validación continua de los scripts y de la integridad/cobertura de SQLite.
- Documentación pública de producto, arquitectura, privacidad y procedencia.

### Seguridad y privacidad

- El modo de lote se limita a procesamiento local y conserva los originales.
- ZIP protegidos frente a rutas absolutas, `..`, enlaces y expansión excesiva.
- Documentos, salidas fiscales, entornos y material interno quedan fuera del
  control de versiones.
- La SQLite distribuida usa rutas relativas portables y no contiene rutas del
  equipo donde se generó.
- El núcleo de la skill queda separado de la web, que se mantiene en la rama
  independiente `landing`.

### Límites

- La versión 1.0.0 prepara libros y conciliaciones; no contabiliza ni presenta
  automáticamente el Modelo 303.

[1.1.0]: https://github.com/686f6c61/hacienda-303/releases/tag/v1.1.0
[1.0.0]: https://github.com/686f6c61/hacienda-303/releases/tag/v1.0.0

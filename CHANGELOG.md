# Changelog

Todos los cambios relevantes de Hacienda 303 se documentan en este archivo.
El proyecto sigue [Versionado Semántico](https://semver.org/lang/es/).

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

[1.0.0]: https://github.com/686f6c61/hacienda-303/releases/tag/v1.0.0

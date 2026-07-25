# Hacienda 303

**Suelta una carpeta de facturas. Recupera un proceso ordenado, local y revisable.**

Hacienda 303 es una skill abierta para agentes de IA que convierte PDF, fotos,
Facturae, ZIP y carpetas completas en un flujo trazable de clasificación de IVA.
Con el perfil fiscal revisado, genera por separado un libro de auditoría y un
XLSX estricto con la estructura de los libros registro AEAT 2026.

[Web del producto](https://hacienda-303.686f6c61.dev) ·
[Página técnica](https://hacienda-303.686f6c61.dev/tecnica) ·
[Última versión](https://github.com/686f6c61/hacienda-303/releases/latest)

> Producto independiente y no oficial. No pertenece a la Agencia Tributaria.
> Ayuda a preparar y revisar información; no presenta declaraciones ni sustituye
> la validación oficial o el criterio de un profesional tributario.

## Lo que resuelve

Un lote real no es una tabla limpia. Puede llegar como un ZIP con cientos de
archivos, carpetas por meses, PDF con texto, escaneos, fotos giradas o XML
Facturae. Hacienda 303 organiza ese trabajo en etapas que se pueden revisar y
reanudar:

1. **Inventaria sin tocar los originales.** Registra tipo, tamaño y SHA-256;
   bloquea rutas peligrosas y señala archivos no soportados.
2. **Extrae texto localmente.** Aprovecha el texto de los PDF y activa OCR cuando
   hace falta; conserva avisos de calidad y permite reanudar.
3. **Separa archivo, factura, operación y fila.** Una factura con varios tipos o
   tratamientos puede generar varias operaciones.
4. **Clasifica con un recorrido AEAT trazable.** La búsqueda propone candidatos,
   pero la conclusión exige llegar a un caso terminal y conservar sus respuestas.
5. **Pregunta solo lo determinante.** País, establecimiento, naturaleza de la
   operación, exención o inversión del sujeto pasivo no se inventan.
6. **Exporta después de revisar.** Los pendientes no entran en el libro estricto
   de importación.

## Cuatro agentes, una misma forma de trabajar

El repositorio incluye adaptadores para:

- **OpenAI / Codex:** `clasificar-facturas-iva-aeat/agents/openai.yaml`
- **Claude:** `clasificar-facturas-iva-aeat/agents/claude.md`
- **Kimi K3:** `clasificar-facturas-iva-aeat/agents/kimi-k3.md`
- **Z.ai GLM 5.2:** `clasificar-facturas-iva-aeat/agents/glm-5.2.md`

Los cuatro aplican la misma skill, los mismos límites y los mismos validadores.
La diferencia está en el formato que entiende cada host, no en el criterio fiscal.

## Empieza en Claude Code

La forma más directa no requiere configurar nada a mano:

```bash
git clone https://github.com/686f6c61/hacienda-303.git
cd hacienda-303
claude
```

Y dentro de Claude Code:

```text
¿Cómo empiezo?
```

El archivo `CLAUDE.md` del repositorio le indica dónde está la skill. Claude te
preguntará si son facturas emitidas o recibidas, el ejercicio y periodo, y dónde
está el ZIP, carpeta o documento. Después hace el inventario sin modificar los
originales.

Un primer mensaje algo más concreto puede ser:

```text
Tengo un ZIP con facturas recibidas del segundo trimestre de 2026.
Quiero preparar el Libro de IVA. ¿Cómo empiezo?
```

### Instalarla como skill personal

Para usar Hacienda 303 desde cualquier carpeta, copia la carpeta completa de la
skill. No copies solo `SKILL.md`: SQLite, scripts, plantillas y referencias
forman parte del flujo.

```bash
mkdir -p ~/.claude/skills
cp -R clasificar-facturas-iva-aeat ~/.claude/skills/
```

Claude Code puede activarla automáticamente cuando hables de facturas e IVA, o
puedes invocarla de forma explícita:

```text
/clasificar-facturas-iva-aeat
```

Si `~/.claude/skills/` no existía cuando abriste la sesión, reinicia Claude Code
una vez para que observe el nuevo directorio. Consulta la
[documentación oficial de skills de Claude Code](https://code.claude.com/docs/es/skills).

Para instalarla en Codex:

```bash
cp -R clasificar-facturas-iva-aeat ~/.codex/skills/
```

En los demás agentes, importa la carpeta de la skill y usa el adaptador de
`clasificar-facturas-iva-aeat/agents/` que corresponda al sistema.

## Qué hay dentro

```text
hacienda-303/
├── CLAUDE.md                    # arranque conversacional en Claude Code
├── clasificar-facturas-iva-aeat/
│   ├── SKILL.md                 # flujo que sigue el agente
│   ├── agents/                  # OpenAI, Claude, Kimi y GLM
│   ├── assets/
│   │   ├── aeat_iva.sqlite      # índice portable de decisiones
│   │   └── aeat-2026/           # plantillas y códigos oficiales
│   ├── references/              # guardrails, esquemas y límites
│   └── scripts/                 # ingestión, consulta, exportación y QA
└── sources/                     # fuentes reproducibles del índice
```

La web pública y su contenedor están aislados en la rama
[`landing`](https://github.com/686f6c61/hacienda-303/tree/landing). No forman
parte del núcleo instalable de la skill.

### Por qué SQLite importa

`aeat_iva.sqlite` no es una colección de respuestas aproximadas. Contiene
**3.069 recorridos terminales** —1.885 de bienes y 1.184 de servicios— y
**21.679 pasos de decisión** extraídos de los localizadores públicos AEAT
2023–2026 el 9 de julio de 2026.

La búsqueda textual sirve para reducir opciones. La clasificación solo se cierra
cuando el agente reproduce un recorrido exacto hasta un resultado terminal. Así
se puede responder a tres preguntas importantes: qué sabía la factura, qué
preguntó el agente y qué rama AEAT justificó la propuesta.

## Uso rápido con un lote

Necesitas Python 3.10 o posterior. Instala las dependencias Python:

```bash
python3 -m pip install -r \
  clasificar-facturas-iva-aeat/requirements.txt
```

Para PDF y OCR, instala también Poppler y Tesseract antes de procesar documentos
escaneados. En Debian/Ubuntu:

```bash
sudo apt install poppler-utils tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng
```

```bash
python3 clasificar-facturas-iva-aeat/scripts/ingest_batch.py \
  ./facturas.zip \
  --output ./work/2T-2026 \
  --ocr auto \
  --privacy-mode local-only
```

Después, el agente estructura y revisa las operaciones. Puedes consultar
directamente el índice:

```bash
python3 clasificar-facturas-iva-aeat/scripts/query_index.py stats
python3 clasificar-facturas-iva-aeat/scripts/query_index.py \
  search --kind servicios --query "servicio electrónico"
```

Con un perfil fiscal confirmado y registros revisados:

```bash
python3 clasificar-facturas-iva-aeat/scripts/build_aeat_book.py \
  --input ./work/2T-2026/registros-revisados.jsonl \
  --profile ./work/2T-2026/perfil.json \
  --output ./output/libro-iva.xlsx \
  --audit-output ./output/auditoria

python3 clasificar-facturas-iva-aeat/scripts/validate_aeat_book.py \
  ./output/libro-iva.xlsx \
  --profile ./work/2T-2026/perfil.json \
  --strict-import
```

El resultado se contrasta después con el servicio oficial de validación de
Libros Registro de la AEAT. El libro acumulado puede servir de base para Pre303,
pero **no equivale a un Modelo 303 terminado**: quedan casillas y decisiones que
no se derivan de las facturas.

## Salidas

- manifiesto del lote y texto extraído por huella;
- JSON/JSONL con procedencia de cada dato;
- detección de duplicados binarios y posibles duplicados fiscales;
- estado por operación: concluida, preliminar, pendiente o revisión OCR;
- libro de auditoría con trazabilidad interna;
- XLSX estricto, sin columnas internas, para validación/importación;
- conciliación de bases y cuotas previa a Pre303.

## Privacidad y seguridad

El flujo está diseñado para ejecutarse en local. No busca datos privados en
Internet, no ejecuta contenido de los documentos y no modifica los originales.
Los archivos fiscales, resultados y carpetas de trabajo están excluidos por
defecto del repositorio.

No abras una incidencia pública adjuntando facturas, NIF, direcciones, cuentas,
certificados o tokens. Consulta [SECURITY.md](SECURITY.md) para comunicar un
problema sensible.

## Límites deliberados

Hacienda 303 no:

- decide deducibilidad, afectación o prorrata sin el perfil fiscal;
- inventa códigos por similitud;
- da por válido un OCR dudoso;
- importa, contabiliza, firma o presenta automáticamente;
- convierte la conciliación del libro en una declaración definitiva;
- sustituye la normativa vigente ni la revisión humana.

## Versionado y procedencia

La versión actual es **1.1.0**. Los cambios se documentan en
[CHANGELOG.md](CHANGELOG.md). Las plantillas, marcas y fuentes de terceros no
quedan relicenciadas por la licencia MIT del código; consulta
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Licencia

El código original del proyecto se publica bajo licencia MIT. Los materiales de
terceros conservan sus condiciones y titularidad.

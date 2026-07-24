# Fuentes reproducibles del índice

Estos JSON conservan los recorridos obtenidos de los localizadores públicos de
IVA de la AEAT el 9 de julio de 2026:

| Archivo | Casos | SHA-256 |
| --- | ---: | --- |
| `aeat_iva_303_localizador_bienes_2023_2026.json` | 1.885 | `7e46111e43b8de66cde47645fade5a9a475c218050f7c7d332e3728364aecd22` |
| `aeat_iva_303_localizador_servicios_2023_2026.json` | 1.184 | `9f41a871bba198fd8ac846b20475551a4095110fafb14fa7b9474d5530db92f2` |

El índice distribuido se puede reconstruir con:

```bash
python3 clasificar-facturas-iva-aeat/scripts/build_index.py \
  --bienes sources/aeat_iva_303_localizador_bienes_2023_2026.json \
  --servicios sources/aeat_iva_303_localizador_servicios_2023_2026.json \
  --output clasificar-facturas-iva-aeat/assets/aeat_iva.sqlite
```

Después:

```bash
python3 clasificar-facturas-iva-aeat/scripts/query_index.py stats
```

Los datos describen la herramienta pública en la fecha de extracción. Antes de
usar una conclusión fiscal, comprueba la vigencia de la normativa y valida el
caso concreto.

# Del libro de IVA al modelo 303

## Lo que puede obtenerse de las facturas

Se pueden preparar libros de expedidas/recibidas, bienes de inversión, tratamiento IVA, bases, cuotas, códigos AEAT, conciliación y XLSX para Pre303.

## Por qué no bastan para cerrar el 303

El resultado depende también de:

- situación censal, régimen, periodicidad y SII;
- afectación y derecho a deducción;
- prorrata;
- importaciones y documentos aduaneros;
- compensaciones anteriores;
- rectificaciones y regularizaciones;
- bienes de inversión y criterio de caja;
- otras casillas, cuenta bancaria y forma de presentación.

Por eso `reconcile_books.py` es control aritmético, no Modelo 303. Acepta JSON/JSONL o un XLSX, separa cuota repercutida, cuota devengada técnica por AIB/ISP y cuota deducible por trimestre. No asigna casillas oficiales cuando las condiciones de cálculo no están completamente implementadas.

## Secuencia

1. Completar perfil fiscal.
2. Clasificar y revisar operaciones.
3. Generar libro acumulado.
4. Validarlo en AEAT.
5. Importarlo en Pre303 si el contribuyente está admitido.
6. Revisar y completar casillas no derivadas.
7. Conciliar con contabilidad y periodos anteriores.
8. Presentar solo tras aprobación expresa.

La importación Pre303 está orientada a determinados contribuyentes trimestrales no SII. Verificar elegibilidad vigente antes de presentar.

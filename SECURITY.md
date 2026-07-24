# Seguridad y datos fiscales

## No publiques facturas

Las incidencias de GitHub son públicas. No adjuntes facturas, archivos de
trabajo, NIF, nombres, direcciones, cuentas bancarias, certificados, claves,
tokens ni capturas que los muestren.

Para reproducir un fallo, crea un ejemplo sintético que no pertenezca a una
persona o empresa real.

## Qué comunicar

Indica la versión, el sistema operativo, el comando ejecutado, el tipo general de
archivo y el mensaje de error ya anonimizado. No pegues rutas privadas si
incluyen nombres de clientes o contribuyentes.

## Alcance

Son especialmente relevantes:

- escapes de rutas o extracción insegura de ZIP;
- ejecución accidental de contenido incluido en documentos;
- conexiones de red inesperadas durante `local-only`;
- exposición de documentos o resultados;
- bypass de una validación que permita exportar pendientes como concluidos.

Antes de abrir una incidencia pública sobre uno de estos puntos, usa el canal
privado de seguridad del repositorio cuando esté disponible.

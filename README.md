# Landing de Hacienda 303

Esta rama contiene únicamente la web pública de
[Hacienda 303](https://hacienda-303.686f6c61.dev):

- aplicación React/Vite en `landing/`;
- favicon, manifest y recursos visuales públicos;
- `Dockerfile` de producción;
- configuración nginx para la SPA y la redirección de `www`.

El núcleo instalable —skill, agentes, SQLite, fuentes, referencias y scripts—
vive en la rama [`main`](https://github.com/686f6c61/hacienda-303).

## Desarrollo local

```bash
cd landing
npm ci
npm run dev
```

## Imagen de producción

```bash
docker build -t hacienda-303-landing .
docker run --rm -p 8080:80 hacienda-303-landing
```

La configuración del proveedor, credenciales, direcciones internas y secretos
de despliegue no forman parte de esta rama.

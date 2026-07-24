const SITE_URL = "https://hacienda-303.686f6c61.dev";
const SOCIAL_IMAGE = `${SITE_URL}/og-hacienda-303.png`;

export const PAGE_SEO = {
  "/": {
    title: "Hacienda 303 · Tus facturas, por fin en fila",
    description:
      "Clasifica facturas, prepara el Libro de IVA y concilia el Modelo 303 con un flujo local, trazable y revisable.",
  },
  "/empezar": {
    title: "Cómo empezar con Hacienda 303 en Claude Code",
    description:
      "Instala Hacienda 303, abre Claude Code y convierte tu primera carpeta o ZIP de facturas en un lote revisable.",
  },
  "/tecnica": {
    title: "Cómo funciona Hacienda 303 · Skill, SQLite y agentes",
    description:
      "Conoce el flujo técnico de Hacienda 303: inventario, OCR, reglas fiscales, SQLite AEAT, revisión humana y exportación.",
  },
};

export function normalizePath(pathname) {
  const cleanPath = pathname.replace(/\/+$/, "");
  return cleanPath || "/";
}

function setMeta(selector, attribute, value) {
  const element = document.head.querySelector(selector);
  if (element) element.setAttribute(attribute, value);
}

export function applyPageSeo(pathname) {
  const path = normalizePath(pathname);
  const page = PAGE_SEO[path] || PAGE_SEO["/"];
  const url = path === "/" ? SITE_URL : `${SITE_URL}${path}`;

  document.title = page.title;
  setMeta('meta[name="description"]', "content", page.description);
  setMeta('meta[property="og:title"]', "content", page.title);
  setMeta('meta[property="og:description"]', "content", page.description);
  setMeta('meta[property="og:url"]', "content", url);
  setMeta('meta[property="og:image"]', "content", SOCIAL_IMAGE);
  setMeta('meta[name="twitter:title"]', "content", page.title);
  setMeta('meta[name="twitter:description"]', "content", page.description);
  setMeta('meta[name="twitter:image"]', "content", SOCIAL_IMAGE);
  setMeta('link[rel="canonical"]', "href", url);
}

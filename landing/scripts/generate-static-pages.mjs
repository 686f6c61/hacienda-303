import { mkdir, readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";

const distDirectory = new URL("../dist/", import.meta.url);
const source = await readFile(new URL("index.html", distDirectory), "utf8");

const pages = [
  {
    path: "empezar",
    title: "Cómo empezar con Hacienda 303 en Claude Code",
    description:
      "Instala Hacienda 303, abre Claude Code y convierte tu primera carpeta o ZIP de facturas en un lote revisable.",
  },
  {
    path: "tecnica",
    title: "Cómo funciona Hacienda 303 · Skill, SQLite y agentes",
    description:
      "Conoce el flujo técnico de Hacienda 303: inventario, OCR, reglas fiscales, SQLite AEAT, revisión humana y exportación.",
  },
];

function replaceAttribute(html, selector, attribute, value) {
  const escapedSelector = selector.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const pattern = new RegExp(
    `(<meta ${escapedSelector} [^>]*${attribute}=")[^"]*(")`,
  );
  return html.replace(pattern, `$1${value}$2`);
}

for (const page of pages) {
  const url = `https://hacienda-303.686f6c61.dev/${page.path}`;
  let html = source
    .replace(/<title>[^<]*<\/title>/, `<title>${page.title}</title>`)
    .replace(
      /<link rel="canonical" href="[^"]*"\s*\/>/,
      `<link rel="canonical" href="${url}" />`,
    );

  html = replaceAttribute(html, 'name="description"', "content", page.description);
  html = replaceAttribute(html, 'property="og:title"', "content", page.title);
  html = replaceAttribute(html, 'property="og:description"', "content", page.description);
  html = replaceAttribute(html, 'property="og:url"', "content", url);
  html = replaceAttribute(html, 'name="twitter:title"', "content", page.title);
  html = replaceAttribute(html, 'name="twitter:description"', "content", page.description);

  const targetDirectory = join(distDirectory.pathname, page.path);
  await mkdir(targetDirectory, { recursive: true });
  await writeFile(join(targetDirectory, "index.html"), html);
}

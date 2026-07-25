import {
  ArrowUpRight,
  CheckCircle,
  GithubLogo,
  ShieldCheck,
  Sparkle,
} from "@phosphor-icons/react";
import {
  CHANGELOG_URL,
  RELEASE_VERSION,
  REPO_URL,
} from "./config.js";

const releaseHighlights = [
  {
    icon: ShieldCheck,
    title: "Lotes más seguros",
    copy: "Límites reales al descomprimir y originales protegidos en tu equipo.",
  },
  {
    icon: CheckCircle,
    title: "Conciliación fiable",
    copy: "Una fila incorrecta ya no elimina importes válidos ya revisados.",
  },
  {
    icon: Sparkle,
    title: "21 pruebas",
    copy: "Más cobertura para IVA, libros AEAT, duplicados, ZIP y conciliación.",
  },
];

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <section className="release-panel" id="novedades" aria-labelledby="release-title">
        <div className="release-heading">
          <span className="release-kicker">NOVEDADES · 25 JUL 2026</span>
          <div className="release-version" aria-label={`Versión ${RELEASE_VERSION}`}>
            <span>v</span>{RELEASE_VERSION}
          </div>
          <h2 id="release-title">Más segura.<br />Más comprobada.</h2>
          <a href={CHANGELOG_URL} target="_blank" rel="noreferrer">
            Ver changelog completo <ArrowUpRight weight="bold" />
          </a>
        </div>
        <div className="release-highlights">
          {releaseHighlights.map(({ icon: Icon, title, copy }, index) => (
            <article key={title} className={`release-card release-card-${index + 1}`}>
              <Icon size={32} weight="fill" />
              <div>
                <strong>{title}</strong>
                <p>{copy}</p>
              </div>
            </article>
          ))}
        </div>
      </section>

      <div className="footer-base">
        <div className="footer-brand">
          <span className="brand-stamp">H</span>
          <span><strong>Hacienda 303</strong><small>Versión {RELEASE_VERSION}</small></span>
        </div>
        <div className="footer-links">
          <a href={REPO_URL} target="_blank" rel="noreferrer">
            <GithubLogo weight="fill" /> GitHub
          </a>
          <a href="/empezar">Cómo empiezo</a>
          <a href="/tecnica">Cómo está hecho</a>
          <a href="#novedades">Novedades</a>
        </div>
        <p className="footer-small">
          Los archivos y resultados se guardan en tu equipo. El agente elegido
          puede procesar contenido según las condiciones de su proveedor.
          Producto independiente y no oficial.
        </p>
      </div>
    </footer>
  );
}

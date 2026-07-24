import { useState } from "react";
import {
  ArrowLeft, ArrowRight, Check, DownloadSimple, FolderOpen, GithubLogo,
  LockKey, Play, Sparkle, TerminalWindow, WarningCircle, X,
} from "@phosphor-icons/react";
import { REPO_URL } from "./config.js";

const steps = [
  {
    number: "01",
    title: "Baja el repositorio",
    copy: "Ahí viven la skill, los cuatro agentes, SQLite, los scripts y las referencias. Todo junto; nada se busca por Internet.",
    command: "git clone https://github.com/686f6c61/hacienda-303.git",
  },
  {
    number: "02",
    title: "Abre Claude Code",
    copy: "Entra en la carpeta del repositorio. Claude encontrará las instrucciones de arranque del proyecto.",
    command: "cd hacienda-303 && claude",
  },
  {
    number: "03",
    title: "Habla normal",
    copy: "No necesitas preparar un prompt fiscal. Empieza por tu objetivo y deja que el agente te pida solo lo que cambia el resultado.",
    command: "¿Cómo empiezo?",
  },
];

export function StartPage() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="site-shell start-page">
      <header className="topbar">
        <a className="brand" href="/" aria-label="Volver a Hacienda 303">
          <span className="brand-stamp">H</span><span>Hacienda 303</span>
        </a>
        <nav className={menuOpen ? "nav open" : "nav"} aria-label="Navegación de inicio">
          <a href="#tres-pasos">Tres pasos</a>
          <a href="#instalar">Instalar la skill</a>
          <a href="#primer-lote">Primer lote</a>
          <a href="/tecnica">Cómo está hecho</a>
        </nav>
        <a className="nav-cta" href={REPO_URL} target="_blank" rel="noreferrer">
          Repositorio <GithubLogo weight="fill" />
        </a>
        <button className="menu-button" onClick={() => setMenuOpen((open) => !open)}
          aria-label={menuOpen ? "Cerrar menú" : "Abrir menú"} aria-expanded={menuOpen}>
          {menuOpen ? <X weight="bold" /> : <span>MENÚ</span>}
        </button>
      </header>

      <main>
        <section className="start-hero grid-bg">
          <div>
            <a className="back-link" href="/"><ArrowLeft weight="bold" /> Volver al producto</a>
            <span className="kicker dark">CLAUDE CODE · SIN MANUAL ETERNO</span>
            <h1>Abre la terminal.<br /><span>Di: «¿Cómo empiezo?»</span></h1>
            <p>Clonas el repositorio, arrancas Claude Code y cuentas qué facturas tienes. Hacienda 303 pone el método; tú confirmas los hechos fiscales.</p>
            <div className="hero-actions">
              <a className="button button-primary" href="#tres-pasos">
                Empezar ahora <ArrowRight weight="bold" />
              </a>
              <span className="privacy-note"><LockKey weight="fill" /> Siempre en tu equipo</span>
            </div>
          </div>

          <div className="start-terminal" aria-label="Ejemplo de inicio en Claude Code">
            <div className="window-bar">
              <span>terminal · hacienda-303</span>
              <span className="local-badge">LOCAL</span>
            </div>
            <div className="terminal-body">
              <p><span>$</span> claude</p>
              <p className="terminal-question">› ¿Cómo empiezo?</p>
              <div className="terminal-answer">
                <Sparkle weight="fill" />
                <p>Cuéntame si son facturas emitidas o recibidas y pásame el ZIP o la carpeta. Primero haré un inventario sin tocar los originales.</p>
              </div>
            </div>
          </div>
        </section>

        <section className="start-steps" id="tres-pasos">
          <div className="section-heading compact">
            <span className="kicker">TRES COMANDOS. YA ESTÁ.</span>
            <h2>De cero<br /><span>al primer lote.</span></h2>
          </div>
          <div className="start-step-grid">
            {steps.map((step) => (
              <article className="start-step-card" key={step.number}>
                <span className="start-step-number">{step.number}</span>
                <h3>{step.title}</h3>
                <p>{step.copy}</p>
                <code>{step.command}</code>
              </article>
            ))}
          </div>
        </section>

        <section className="install-section grid-bg" id="instalar">
          <div className="install-copy">
            <span className="kicker dark">SI QUIERES USARLA EN CUALQUIER CARPETA</span>
            <h2>Instálala<br /><span>una vez.</span></h2>
            <p>Claude Code descubre las skills personales en <code>~/.claude/skills/</code>. Copia allí la carpeta completa: necesita también SQLite, scripts y referencias.</p>
            <a className="button button-primary" href={REPO_URL} target="_blank" rel="noreferrer">
              <GithubLogo weight="fill" /> Abrir el repositorio
            </a>
          </div>
          <div className="install-command">
            <div className="window-bar">
              <span>instalar · skill personal</span>
              <TerminalWindow weight="fill" />
            </div>
            <pre><code>{`mkdir -p ~/.claude/skills
cp -R clasificar-facturas-iva-aeat \\
  ~/.claude/skills/

claude
/clasificar-facturas-iva-aeat`}</code></pre>
            <small>También se activa sola cuando tu petición coincide con su descripción.</small>
          </div>
        </section>

        <section className="first-batch-section" id="primer-lote">
          <div className="first-batch-title">
            <span className="kicker">TU PRIMER MENSAJE</span>
            <h2>No escribas un tratado.<br /><span>Cuenta lo que tienes.</span></h2>
          </div>
          <div className="prompt-card">
            <span>TÚ</span>
            <p>“Tengo un ZIP con facturas recibidas del segundo trimestre de 2026. Quiero preparar el Libro de IVA. ¿Cómo empiezo?”</p>
          </div>
          <div className="first-batch-grid">
            <article>
              <FolderOpen weight="fill" />
              <h3>Claude inventaria</h3>
              <p>Detecta formatos, duplicados, calidad de texto y documentos que necesitan OCR.</p>
            </article>
            <article>
              <Play weight="fill" />
              <h3>La skill conduce</h3>
              <p>Separa los hechos de las inferencias y recorre la rama AEAT hasta un resultado terminal.</p>
            </article>
            <article>
              <Check weight="bold" />
              <h3>Tú confirmas</h3>
              <p>Perfil fiscal, deducibilidad y hechos que la factura no puede demostrar siguen bajo tu control.</p>
            </article>
          </div>
        </section>

        <section className="start-warning">
          <WarningCircle size={56} weight="fill" />
          <div>
            <span>IMPORTANTE</span>
            <h2>Preparar no es presentar.</h2>
            <p>Hacienda 303 crea libros revisables y una conciliación previa. No contabiliza, firma ni presenta el Modelo 303 por ti.</p>
          </div>
          <a className="button button-secondary" href="/tecnica#limites">
            Ver los límites <ArrowRight weight="bold" />
          </a>
        </section>

        <section className="tech-final grid-bg">
          <div>
            <span className="kicker dark">TU TURNO</span>
            <h2>Abre Claude.<br />Suelta la carpeta.</h2>
            <p>Empieza con una frase normal. El método aparece cuando hace falta.</p>
          </div>
          <div className="tech-final-actions">
            <a className="button button-mega" href={REPO_URL} target="_blank" rel="noreferrer">
              <DownloadSimple weight="bold" /> Bajar Hacienda 303
            </a>
            <a className="back-home" href="/"><ArrowLeft weight="bold" /> Volver al producto</a>
          </div>
        </section>
      </main>

      <footer>
        <div className="footer-brand"><span className="brand-stamp">H</span><strong>Hacienda 303</strong></div>
        <div className="footer-links">
          <a href={REPO_URL} target="_blank" rel="noreferrer"><GithubLogo weight="fill" /> GitHub</a>
          <a href="/tecnica">Cómo está hecho</a>
          <a href="/">Producto</a>
        </div>
        <p className="footer-small">Producto independiente y no oficial. Tus documentos se quedan en local.</p>
      </footer>
    </div>
  );
}

import { useState } from "react";
import {
  ArrowLeft, ArrowRight, Check, DownloadSimple, FolderOpen, GithubLogo,
  LockKey, Play, Sparkle, TerminalWindow, WarningCircle, X,
} from "@phosphor-icons/react";
import { REPO_URL } from "./config.js";
import { SiteFooter } from "./SiteFooter.jsx";

const steps = [
  {
    number: "01",
    title: "Clona o descarga",
    copy: "En GitHub puedes clonar el repositorio o pulsar «Code → Download ZIP» si no quieres utilizar comandos.",
    command: "git clone …  o  Code → Download ZIP",
  },
  {
    number: "02",
    title: "Abre tu agente",
    copy: "Abre la carpeta hacienda-303 con Claude Code, Codex o Kimi. Dentro encontrará la skill y las instrucciones.",
    command: "Claude Code · Codex · Kimi",
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
          <a href="#tres-pasos"><Play weight="fill" /> Tres pasos</a>
          <a href="#instalar"><DownloadSimple weight="bold" /> Instalar la skill</a>
          <a href="#primer-lote"><FolderOpen weight="fill" /> Primer lote</a>
          <a href="/tecnica"><TerminalWindow weight="fill" /> Cómo está hecho</a>
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
            <span className="kicker dark">UNA SKILL PARA CLAUDE · CODEX · KIMI</span>
            <h1>Baja la carpeta.<br /><span>Di: «¿Cómo empiezo?»</span></h1>
            <p>Clona el repositorio o bájatelo en ZIP, ábrelo con tu agente y cuenta qué facturas tienes. Hacienda 303 pone el método; tú confirmas los hechos fiscales.</p>
            <div className="hero-actions">
              <a className="button button-primary" href="#tres-pasos">
                Empezar ahora <ArrowRight weight="bold" />
              </a>
              <span className="privacy-note"><LockKey weight="fill" /> Archivos y resultados en tu equipo</span>
            </div>
          </div>

          <div className="start-terminal" aria-label="Inicio de Hacienda 303 con un agente compatible">
            <div className="window-bar">
              <span>tu agente · hacienda-303</span>
              <span className="local-badge">LOCAL</span>
            </div>
            <div className="terminal-body">
              <p><span>1</span> Abre la carpeta con Claude, Codex o Kimi</p>
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
            <span className="kicker">TRES PASOS. SIN SER TÉCNICO.</span>
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
            <span className="kicker dark">UNA SKILL ES EL MÉTODO COMPLETO</span>
            <h2>Todo viene<br /><span>dentro.</span></h2>
            <p>La skill reúne las instrucciones fiscales, los recorridos AEAT y las herramientas. Los adaptadores permiten que Claude Code, Codex y Kimi sigan el mismo proceso.</p>
            <a className="button button-primary" href={REPO_URL} target="_blank" rel="noreferrer">
              <GithubLogo weight="fill" /> Clonar o descargar
            </a>
          </div>
          <div className="install-command">
            <div className="window-bar">
              <span>hacienda-303 · todo incluido</span>
              <TerminalWindow weight="fill" />
            </div>
            <pre><code>{`hacienda-303/
└── clasificar-facturas-iva-aeat/
    ├── SKILL.md
    ├── agents/
    ├── scripts/
    └── references/`}</code></pre>
            <small>Abre la carpeta completa: la skill necesita también sus datos, scripts y referencias.</small>
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
              <h3>El agente inventaria</h3>
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
            <h2>Ayuda con el trimestre. No sustituye tu contabilidad.</h2>
            <p>Hacienda 303 crea libros revisables y una conciliación previa. No sustituye tu ERP o programa contable, ni firma o presenta el Modelo 303 por ti.</p>
          </div>
          <a className="button button-secondary" href="/tecnica#limites">
            Ver los límites <ArrowRight weight="bold" />
          </a>
        </section>

        <section className="tech-final grid-bg">
          <div>
            <span className="kicker dark">TU TURNO</span>
            <h2>Abre tu agente.<br />Suelta la carpeta.</h2>
            <p>Empieza con una frase normal. El método aparece cuando hace falta.</p>
          </div>
          <div className="tech-final-actions">
            <a className="button button-mega" href={REPO_URL} target="_blank" rel="noreferrer">
              <DownloadSimple weight="bold" /> Clonar o bajar Hacienda 303
            </a>
            <a className="back-home" href="/"><ArrowLeft weight="bold" /> Volver al producto</a>
          </div>
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}

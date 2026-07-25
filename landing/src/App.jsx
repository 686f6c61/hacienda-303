import { useEffect, useState } from "react";
import {
  ArrowRight, Check, CheckCircle, Code, Database, DownloadSimple, FileCode,
  Files, FolderOpen, GithubLogo, LockKey, MagnifyingGlass, SealCheck,
  Sparkle, Table, TerminalWindow, WarningCircle, X,
} from "@phosphor-icons/react";
import { REPO_URL, REPO_ZIP_URL } from "./config.js";
import { TechPage } from "./TechPage.jsx";
import { StartPage } from "./StartPage.jsx";
import { SiteFooter } from "./SiteFooter.jsx";
import { applyPageSeo, normalizePath } from "./seo.js";

const agents = [
  { name: "Codex", detail: "OpenAI", color: "pink", logo: "/assets/logo-openai.svg" },
  { name: "Claude", detail: "Anthropic", color: "green", logo: "/assets/logo-claude.svg" },
  { name: "Kimi K3", detail: "Moonshot", color: "yellow", logo: "/assets/logo-kimi.svg" },
];

const delivery = [
  {
    icon: Files, eyebrow: "01 · PARA REVISAR", title: "Libro de auditoría",
    copy: "Cada apunte conserva su factura, su huella, la confianza y las alertas. Aquí revisas sin perder el hilo.", color: "pink",
  },
  {
    icon: Table, eyebrow: "02 · PARA IMPORTAR", title: "XLSX limpio AEAT",
    copy: "Solo las columnas oficiales, validadas y preparadas para importar. Sin notas internas mezcladas.", color: "green",
  },
  {
    icon: SealCheck, eyebrow: "03 · PARA DECIDIR", title: "Conciliación 303",
    copy: "IVA repercutido, deducible y técnico por trimestre. Una base clara para revisar el Modelo 303.", color: "yellow",
  },
];

const facts = [
  "ZIP y carpetas completas", "PDF, JPEG, fotos y Facturae",
  "OCR local reanudable", "Códigos AEAT 2026", "Duplicados bajo control",
];

function scrollToId(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
}

export function App() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState("Codex");
  const pathname = normalizePath(window.location.pathname);

  useEffect(() => {
    applyPageSeo(pathname);
  }, [pathname]);

  useEffect(() => {
    if (!window.location.hash) return;
    const target = window.location.hash.slice(1);
    const frame = window.requestAnimationFrame(() => scrollToId(target));
    return () => window.cancelAnimationFrame(frame);
  }, []);

  if (pathname === "/tecnica") {
    return <TechPage />;
  }

  if (pathname === "/empezar") {
    return <StartPage />;
  }

  return (
    <div className="site-shell">
      <header className="topbar">
        <button className="brand" onClick={() => scrollToId("inicio")} aria-label="Ir al inicio">
          <span className="brand-stamp">H</span><span>Hacienda 303</span>
        </button>
        <nav className={menuOpen ? "nav open" : "nav"} aria-label="Navegación principal">
          <button onClick={() => { setMenuOpen(false); scrollToId("como-funciona"); }}><Files weight="fill" /> Cómo funciona</button>
          <button onClick={() => { setMenuOpen(false); scrollToId("entregables"); }}><Table weight="fill" /> Qué te llevas</button>
          <button onClick={() => { setMenuOpen(false); scrollToId("agentes"); }}><Sparkle weight="fill" /> Agentes</button>
          <a href="/empezar"><TerminalWindow weight="fill" /> Cómo empiezo</a>
          <a href="/tecnica"><Code weight="bold" /> Cómo está hecho</a>
        </nav>
        <a className="nav-cta" href={REPO_URL} target="_blank" rel="noreferrer">
          Ver repositorio <GithubLogo weight="fill" />
        </a>
        <button className="menu-button" onClick={() => setMenuOpen((open) => !open)}
          aria-label={menuOpen ? "Cerrar menú" : "Abrir menú"} aria-expanded={menuOpen}>
          {menuOpen ? <X weight="bold" /> : <span>MENÚ</span>}
        </button>
      </header>

      <main>
        <section className="hero grid-bg" id="inicio">
          <div className="hero-copy">
            <div className="pill"><Sparkle weight="fill" /> Tus facturas, por fin en fila</div>
            <h1>Del caos de facturas<span className="speech">al Libro de IVA</span></h1>
            <p className="hero-lede">
              Si te ha llegado el trimestre con facturas por ordenar, clona este repositorio o bájatelo en ZIP. La skill guía a Claude, Codex o Kimi para preparar tu Libro de IVA.
            </p>
            <div className="hero-actions">
              <a className="button button-primary" href="/empezar">
                Ver cómo bajarlo <ArrowRight weight="bold" />
              </a>
              <span className="privacy-note"><LockKey weight="fill" /> Archivos y resultados guardados en tu equipo</span>
            </div>
          </div>
          <div className="hero-visual" aria-label="Una factura ordenando documentos para el Libro de IVA y el Modelo 303">
            <img src="/assets/hacienda-303-hero.png" alt="Personaje factura ordenando documentos en carpetas de revisión, Libro IVA y 303" />
            <div className="status-sticker">
              <CheckCircle weight="fill" /><span><strong>Lotes grandes</strong>, paso a paso</span>
            </div>
          </div>
        </section>

        <div className="ticker" aria-label="Formatos y capacidades">
          <div className="ticker-track">
            {[...facts, ...facts].map((fact, index) => (
              <span key={`${fact}-${index}`}><Sparkle weight="fill" /> {fact}</span>
            ))}
          </div>
        </div>

        <aside className="aeat-strip" aria-label="Compatibilidad con los libros registro de la Agencia Tributaria">
          <img src="/assets/agencia-tributaria.svg" alt="Agencia Tributaria" />
          <div>
            <strong>Habla el idioma de Hacienda.</strong>
            <span>Estructura y códigos preparados según los libros registro AEAT 2026.</span>
          </div>
          <small>Producto independiente · no oficial</small>
        </aside>

        <section className="steps-section" id="como-funciona">
          <div className="section-heading">
            <span className="kicker">TRES PASOS. CERO DRAMA.</span>
            <h2>Abres la carpeta.<br /><span>Hacienda 303 ordena.</span></h2>
            <p>No necesitas saber códigos fiscales para empezar. El producto te pregunta solo cuando una respuesta cambia el tratamiento de la factura.</p>
          </div>
          <div className="steps-grid">
            <article className="step-card pink-card">
              <span className="step-number">1</span><FolderOpen size={54} weight="fill" />
              <h3>Suelta el lote</h3>
              <p>Con el repositorio abierto en tu agente, pásale un ZIP, una carpeta o fotos sueltas. Los originales quedan intactos.</p>
            </article>
            <article className="step-card green-card">
              <span className="step-number">2</span><MagnifyingGlass size={54} weight="bold" />
              <h3>Revisa lo dudoso</h3>
              <p>OCR, duplicados, inversión del sujeto pasivo, exenciones y periodos. Lo claro avanza; lo dudoso se señala.</p>
            </article>
            <article className="step-card yellow-card">
              <span className="step-number">3</span><Table size={54} weight="fill" />
              <h3>Descarga limpio</h3>
              <p>Recibes el libro de auditoría y otro XLSX estricto, sin columnas extra, preparado para validar e importar.</p>
            </article>
          </div>
        </section>

        <section className="repo-section grid-bg" id="repo">
          <div className="repo-copy">
            <span className="kicker dark">TODO EN EL MISMO REPOSITORIO</span>
            <h2>Clónalo.<br />O bájatelo.</h2>
            <p>Si utilizas Git, clona el repositorio. Si no, descárgalo como ZIP desde GitHub. Dentro va la skill completa para trabajar con tus facturas.</p>
            <ul className="check-list">
              <li><Check weight="bold" /> La skill y sus reglas fiscales</li>
              <li><Check weight="bold" /> Agentes para Codex, Claude y Kimi</li>
              <li><Check weight="bold" /> SQLite con 3.069 recorridos AEAT</li>
              <li><Check weight="bold" /> Scripts, plantillas y validadores</li>
            </ul>
            <div className="repo-actions">
              <a className="button button-primary" href={REPO_URL} target="_blank" rel="noreferrer">
                <GithubLogo weight="fill" /> Clonar en GitHub
              </a>
              <a className="button button-secondary" href={REPO_ZIP_URL}>
                <DownloadSimple weight="bold" /> Bajarlo en ZIP
              </a>
            </div>
          </div>
          <div className="repo-panel">
            <div className="window-bar">
              <span>686f6c61 / hacienda-303</span>
              <span className="local-badge"><GithubLogo weight="fill" /> PÚBLICO</span>
            </div>
            <div className="repo-tree">
              <div><FolderOpen weight="fill" /><strong>clasificar-facturas-iva-aeat/</strong></div>
              <div className="tree-child"><FileCode weight="fill" /><span>SKILL.md</span><small>el método</small></div>
              <div className="tree-child"><Code weight="bold" /><span>agents/</span><small>3 adaptadores</small></div>
              <div className="tree-child"><Database weight="fill" /><span>aeat_iva.sqlite</span><small>3.069 casos</small></div>
              <div className="tree-child"><TerminalWindow weight="fill" /><span>scripts/</span><small>ingesta + validación</small></div>
              <div className="tree-child"><Files weight="fill" /><span>references/</span><small>criterio y límites</small></div>
            </div>
            <a className="repo-tech-link" href="/tecnica">Entender cómo funciona por dentro <ArrowRight weight="bold" /></a>
          </div>
        </section>

        <section className="delivery-section" id="entregables">
          <div className="section-heading compact">
            <span className="kicker">NO ES “UN EXCEL Y YA”</span>
            <h2>Sabes qué pasó.<br /><span>Y qué hacer después.</span></h2>
          </div>
          <div className="delivery-grid">
            {delivery.map(({ icon: Icon, eyebrow, title, copy, color }) => (
              <article className={`delivery-card ${color}`} key={title}>
                <div className="delivery-icon"><Icon size={34} weight="fill" /></div>
                <span>{eyebrow}</span><h3>{title}</h3><p>{copy}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="agents-section" id="agentes">
          <div className="agent-intro">
            <span className="kicker light">UNA SKILL · TRES AGENTES</span>
            <h2>Abre la carpeta.<br />Habla normal.</h2>
            <p>Una skill es una carpeta con instrucciones, referencias AEAT y herramientas. Claude, Codex o Kimi la siguen para ordenar el lote y pedirte solo las decisiones que necesitan confirmación.</p>
          </div>
          <div className="agent-picker" role="tablist" aria-label="Agentes compatibles">
            {agents.map((agent) => (
              <button key={agent.name}
                className={`agent-card ${agent.color} ${selectedAgent === agent.name ? "selected" : ""}`}
                onClick={() => setSelectedAgent(agent.name)} role="tab"
                aria-selected={selectedAgent === agent.name}>
                <img className="agent-logo" src={agent.logo} alt="" /><span>{agent.detail}</span>
                <strong>{agent.name}</strong><CheckCircle className="agent-check" weight="fill" />
              </button>
            ))}
            <div className="agent-message">
              <span>Ahora mismo</span><strong>{selectedAgent}</strong>
              <p>puede abrir el repositorio, seguir la skill Hacienda 303 y dejar el lote preparado para tu revisión.</p>
            </div>
          </div>
        </section>

        <section className="truth-section">
          <div className="truth-title">
            <WarningCircle size={66} weight="fill" />
            <h2>Te ayuda con el trimestre.<br />No sustituye tu contabilidad.</h2>
            <p>Está pensado para quien llega al momento de preparar el IVA con facturas por ordenar. No sustituye tu ERP, tu programa contable ni el criterio final de tu asesor.</p>
          </div>
          <div className="truth-grid">
            <div>
              <span className="yes-label">SÍ HACE</span>
              <ul>
                <li><Check weight="bold" /> Lee y estructura facturas</li>
                <li><Check weight="bold" /> Recorre códigos oficiales AEAT</li>
                <li><Check weight="bold" /> Valida cálculos y formatos</li>
                <li><Check weight="bold" /> Señala dudas y duplicados</li>
                <li><Check weight="bold" /> Prepara Libro IVA y conciliación</li>
              </ul>
            </div>
            <div>
              <span className="no-label">TE PIDE CONFIRMAR</span>
              <ul>
                <li><ArrowRight weight="bold" /> Deducibilidad y afectación</li>
                <li><ArrowRight weight="bold" /> Prorrata y bienes de inversión</li>
                <li><ArrowRight weight="bold" /> Hechos que no salen en la factura</li>
                <li><ArrowRight weight="bold" /> Validación final de la AEAT</li>
                <li><ArrowRight weight="bold" /> Presentación del Modelo 303</li>
              </ul>
            </div>
          </div>
        </section>

        <section className="final-cta grid-bg">
          <div>
            <span className="kicker dark">LA PRÓXIMA CARPETA PESA MENOS</span>
            <h2>Que lleguen<br />las facturas.</h2>
            <p>Hacienda 303 las pone en fila. Tú mantienes el control fiscal.</p>
          </div>
          <a className="button button-mega" href={REPO_URL} target="_blank" rel="noreferrer">
            Clonar o bajar el repositorio <GithubLogo weight="fill" />
          </a>
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}

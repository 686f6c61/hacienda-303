import { useState } from "react";
import {
  ArrowLeft, ArrowRight, BracketsCurly, Check, CheckCircle, Code,
  Database, DownloadSimple, FileCode, Files, Fingerprint, FolderOpen,
  GithubLogo, HardDrives, LockKey, MagnifyingGlass, Path, SealCheck,
  ShieldCheck, Sparkle, Table, TerminalWindow, TreeStructure,
  WarningCircle, X,
} from "@phosphor-icons/react";
import { REPO_URL, REPO_ZIP_URL } from "./config.js";
import { SiteFooter } from "./SiteFooter.jsx";

const pipeline = [
  {
    icon: FolderOpen, number: "01", title: "Inventario seguro",
    copy: "Abre ZIP, carpetas, PDF, imágenes, XML y Facturae sin ejecutar adjuntos ni alterar los originales.",
  },
  {
    icon: Fingerprint, number: "02", title: "Texto + evidencia",
    copy: "Extrae texto u OCR, calcula SHA-256 y guarda de dónde salió cada NIF, fecha, importe y mención fiscal.",
  },
  {
    icon: MagnifyingGlass, number: "03", title: "Candidatos, no respuestas",
    copy: "La búsqueda FTS de SQLite localiza rutas probables. Todavía no decide el tratamiento fiscal.",
  },
  {
    icon: TreeStructure, number: "04", title: "Recorrido exacto",
    copy: "El agente responde cada pregunta del árbol AEAT hasta alcanzar un caso terminal verificable.",
  },
  {
    icon: ShieldCheck, number: "05", title: "Reglas y revisión",
    copy: "Valida aritmética, identidad, periodos y códigos. Si falta un hecho determinante, el registro queda pendiente.",
  },
  {
    icon: Table, number: "06", title: "Dos libros, dos usos",
    copy: "Genera un libro rico de auditoría y otro XLSX estricto con solo las hojas y columnas admitidas por AEAT.",
  },
];

const repoRows = [
  ["SKILL.md", "Orquesta el proceso y fija cuándo preguntar, concluir o detenerse."],
  ["agents/", "Adapta el mismo núcleo a Codex, Claude y Kimi K3."],
  ["assets/aeat_iva.sqlite", "Conserva los caminos terminales de los localizadores AEAT."],
  ["assets/aeat-2026/", "Plantillas, códigos y especificaciones oficiales con huellas."],
  ["scripts/ingest_batch.py", "Ingesta segura, OCR local, manifiesto y reanudación."],
  ["scripts/query_index.py", "Busca candidatos y recorre el árbol de decisiones."],
  ["scripts/build_aeat_book.py", "Construye los libros de auditoría e importación."],
  ["scripts/validate_aeat_book.py", "Comprueba estructura, códigos, periodos e importes."],
];

export function TechPage() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="site-shell tech-page">
      <header className="topbar">
        <a className="brand" href="/" aria-label="Volver a Hacienda 303">
          <span className="brand-stamp">H</span><span>Hacienda 303</span>
        </a>
        <nav className={menuOpen ? "nav open" : "nav"} aria-label="Navegación técnica">
          <a href="#arquitectura"><TreeStructure weight="fill" /> Arquitectura</a>
          <a href="#sqlite"><Database weight="fill" /> SQLite</a>
          <a href="#skill"><FileCode weight="fill" /> La skill</a>
          <a href="#limites"><WarningCircle weight="fill" /> Límites</a>
          <a href="/empezar"><TerminalWindow weight="fill" /> Cómo empiezo</a>
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
        <section className="tech-hero grid-bg">
          <div className="tech-hero-copy">
            <a className="back-link" href="/"><ArrowLeft weight="bold" /> Volver al producto</a>
            <span className="kicker dark">POR DENTRO · SIN HUMO</span>
            <h1>No es magia.<br /><span>Es método.</span></h1>
            <p>Hacienda 303 combina instrucciones para agentes, datos oficiales estructurados y scripts deterministas. La IA entiende el documento; el código conserva la trazabilidad.</p>
            <div className="hero-actions">
              <a className="button button-primary" href={REPO_URL} target="_blank" rel="noreferrer">
                <GithubLogo weight="fill" /> Explorar el código
              </a>
              <a className="button button-secondary" href={REPO_ZIP_URL}>
                <DownloadSimple weight="bold" /> Descargar ZIP
              </a>
            </div>
          </div>
          <div className="tech-stats" aria-label="Cifras del índice fiscal">
            <div className="stat-card purple"><b>3.069</b><span>casos terminales</span></div>
            <div className="stat-card pink"><b>21.679</b><span>pasos de decisión</span></div>
            <div className="stat-card green"><b>2</b><span>localizadores AEAT</span></div>
            <div className="stat-card cream"><b>3</b><span>agentes compatibles</span></div>
          </div>
        </section>

        <section className="tech-intro">
          <div>
            <Sparkle size={52} weight="fill" />
            <h2>IA para leer.<br />Reglas para decidir.<br />Código para comprobar.</h2>
          </div>
          <p>Una factura no trae escrito “casilla 12” ni “clave de operación 01”. Para llegar ahí hay que separar hechos documentales, preguntas fiscales y cálculos. Esa separación es el corazón del repositorio.</p>
        </section>

        <section className="pipeline-section" id="arquitectura">
          <div className="section-heading compact">
            <span className="kicker">DEL ARCHIVO AL XLSX</span>
            <h2>Un recorrido<br /><span>que deja huellas.</span></h2>
          </div>
          <div className="pipeline-grid">
            {pipeline.map(({ icon: Icon, number, title, copy }) => (
              <article className="pipeline-card" key={number}>
                <span>{number}</span><Icon size={42} weight="fill" />
                <h3>{title}</h3><p>{copy}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="sqlite-section grid-bg" id="sqlite">
          <div className="sqlite-visual">
            <Database size={110} weight="fill" />
            <div className="db-stack">
              <span><b>1.885</b> entregas de bienes</span>
              <span><b>1.184</b> prestaciones de servicios</span>
              <span><b>hasta 14</b> preguntas por recorrido</span>
            </div>
          </div>
          <div className="sqlite-copy">
            <span className="kicker dark">POR QUÉ SQLITE IMPORTA</span>
            <h2>Buscar parecido<br />no es clasificar.</h2>
            <p>La base SQLite contiene cada camino completo hasta una respuesta terminal de los localizadores de bienes y servicios de la AEAT 2023–2026.</p>
            <div className="why-grid">
              <div><HardDrives weight="fill" /><strong>Funciona sin Internet</strong><span>Las facturas y sus datos no tienen que salir del equipo.</span></div>
              <div><Path weight="bold" /><strong>Conserva el recorrido</strong><span>Pregunta, respuesta y resultado quedan unidos en un mismo caso.</span></div>
              <div><MagnifyingGlass weight="bold" /><strong>FTS encuentra candidatos</strong><span>La búsqueda acelera, pero nunca sustituye el árbol fiscal.</span></div>
              <div><CheckCircle weight="fill" /><strong>Resultado reproducible</strong><span>Otro agente puede seguir las mismas respuestas y llegar al mismo terminal.</span></div>
            </div>
          </div>
        </section>

        <section className="skill-section" id="skill">
          <div className="skill-copy">
            <span className="kicker">LA SKILL ES EL DIRECTOR DE ORQUESTA</span>
            <h2>Le dice al agente<br /><span>cómo trabajar.</span></h2>
            <p>No es un prompt largo. Define un contrato operativo: qué leer, qué evidencia guardar, cuándo preguntar, cómo asignar confianza y qué no puede afirmar.</p>
            <ul className="check-list">
              <li><Check weight="bold" /> Distingue documento, usuario, inferencia y dato desconocido</li>
              <li><Check weight="bold" /> Prohíbe inventar códigos o completar hechos ausentes</li>
              <li><Check weight="bold" /> Divide facturas mixtas en operaciones trazables</li>
              <li><Check weight="bold" /> Detiene la exportación si una clasificación sigue pendiente</li>
            </ul>
          </div>
          <div className="skill-code">
            <div className="window-bar"><span>SKILL.md</span><span className="local-badge"><LockKey weight="fill" /> NÚCLEO</span></div>
            <div className="code-lines">
              <p><em>01</em><span>inventariar_originales()</span></p>
              <p><em>02</em><span>extraer_evidencias()</span></p>
              <p><em>03</em><span>buscar_candidatos_sqlite()</span></p>
              <p><em>04</em><span>recorrer_hasta_terminal()</span></p>
              <p><em>05</em><span>preguntar_si_cambia_resultado()</span></p>
              <p><em>06</em><span>validar_y_exportar()</span></p>
              <p className="code-stop"><em>!</em><span>nunca_presentar_sin_aprobación()</span></p>
            </div>
          </div>
        </section>

        <section className="repo-map-section">
          <div className="section-heading compact">
            <span className="kicker">UN REPO, TODO EL SISTEMA</span>
            <h2>Cada pieza tiene<br /><span>un trabajo concreto.</span></h2>
          </div>
          <div className="repo-table">
            {repoRows.map(([path, purpose]) => (
              <div className="repo-row" key={path}>
                <code><FileCode weight="fill" />{path}</code>
                <p>{purpose}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="agents-tech-section">
          <div>
            <span className="kicker light">TRES AGENTES · UN NÚCLEO</span>
            <h2>El modelo cambia.<br />El método no.</h2>
          </div>
          <div className="adapter-diagram">
            <div className="core-node"><BracketsCurly size={48} weight="bold" /><strong>Skill + SQLite + scripts</strong></div>
            <ArrowRight className="diagram-arrow" size={42} weight="bold" />
            <div className="adapter-nodes">
              <span>OpenAI · Codex</span><span>Claude</span><span>Kimi K3</span>
            </div>
          </div>
          <p>Los archivos de agente solo traducen el mismo contrato a cada plataforma. No duplican el conocimiento fiscal ni mantienen tres versiones distintas de las reglas.</p>
        </section>

        <section className="limits-tech-section" id="limites">
          <div className="limits-title">
            <WarningCircle size={64} weight="fill" />
            <span className="kicker">LA FRONTERA IMPORTA</span>
            <h2>Prepara el 303.<br />No lo presenta.</h2>
          </div>
          <div className="limits-steps">
            <div><span>1</span><p>Completa el perfil fiscal y revisa las operaciones pendientes.</p></div>
            <div><span>2</span><p>Genera el libro acumulado, no solo el trimestre aislado.</p></div>
            <div><span>3</span><p>Valida el XLSX en el servicio oficial de la AEAT.</p></div>
            <div><span>4</span><p>Importa en Pre303 si el contribuyente puede utilizarlo.</p></div>
            <div><span>5</span><p>Completa compensaciones, prorrata y otros datos no contenidos en facturas.</p></div>
            <div><span>6</span><p>Presenta únicamente después de una aprobación expresa.</p></div>
          </div>
        </section>

        <section className="tech-final grid-bg">
          <div>
            <span className="kicker dark">ABIERTO PARA ENTENDERLO</span>
            <h2>Mira el código.<br />Sigue las decisiones.</h2>
            <p>El repositorio incluye la skill, los agentes, la base SQLite, las referencias y los scripts que convierten el método en un flujo repetible.</p>
          </div>
          <div className="tech-final-actions">
            <a className="button button-mega" href={REPO_URL} target="_blank" rel="noreferrer">
              <GithubLogo weight="fill" /> Abrir GitHub
            </a>
            <a className="back-home" href="/"><ArrowLeft weight="bold" /> Volver a Hacienda 303</a>
          </div>
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}

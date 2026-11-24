---
title: "LLM Wiki App — dossier di partenza (fork nashsu + motore geronimo-iia)"
description: "Evidenze, direzione confermata, inventario delle funzionalità nashsu da preservare, proposta di architettura additiva, analisi di scalabilità oltre ~1.000 pagine, architettura alternativa a vincolo rilassato, piano a fasi e decisioni aperte per la nuova applicazione llm-wiki basata su nashsu/llm_wiki con integrazione di geronimo-iia/llm-wiki."
tags: [llm-wiki, nashsu, geronimo-iia, ingest, architettura, scalabilita, prestazioni, dossier]
date: 2026-11-24
revision: 3
status: bozza non normativa
---

# LLM Wiki App — dossier di partenza

> Documento **non normativo**. Raccoglie evidenze, direzione e decisioni aperte. I repository restano la source of truth. Le proposte di design non sono decisioni: le decisioni da prendere sono registrate come Decision Candidate (§9).
> Se il documento cresce, va diviso in una cartella con `index.md`. Con la revisione 3 la soglia è vicina: §12-§14 sono i primi candidati a diventare file propri.

**Revisioni**

| Rev. | Data | Modifica |
|---|---|---|
| 1 | 23/11/2026 | Prima stesura |
| 2 | 23/11/2026 | Vincolo dichiarato: tutte le funzionalità di nashsu restano as-is. Aggiunto l'inventario (§6). Architettura resa additiva e configurabile (§7). Innesto spostato nello strato Rust `commands/fs.rs`. Corretto il confronto sul lint: nashsu ne ha uno proprio. Nuove DC-08…DC-11 e RR-08…RR-11 |
| 3 | 24/11/2026 | Analisi di scalabilità oltre ~1.000 pagine da issue upstream e codice (§12), compresa la parte React (§12.4). Nuovi fatti N25…N33. Risposta a RR-11: `commands/fs.rs` non è l'unico punto di scrittura (§7.3). Valutazione del piano additivo rispetto alla scala (§12.6). Architettura alternativa a vincolo as-is rilassato (§13). WASM escluso (§14, direzione confermata). Fasi 0b e P nel piano (§8). Nuove DC-12…DC-16, RR-12…RR-16, rischi di scala |

**Sintesi della revisione 3**

- Oltre ~1.000 pagine l'app degrada per quattro cause: grafo e analisi nel frontend, scansioni e snapshot completi nel backend, prompt di ingest che crescono con la wiki, viste React che rileggono tutto a ogni cambiamento (§12).
- Il piano additivo di §7 migliora la correttezza delle scritture ma **non tocca nessuna di queste cause**, e in parte aggiunge lavoro (§12.6).
- Molte correzioni lasciano invariato il comportamento e sono compatibili con il vincolo as-is, se lo si legge come «comportamento» e non come «codice intoccato» (Fase P, §8). Le correzioni strutturali richiedono di rilassare il vincolo (DC-12, §13).
- WASM non è una leva utile per questi problemi ed è escluso (§14).

## 0. Legenda

| Asse | Valori |
|---|---|
| Stato | AS-IS · CONFIRMED DIRECTION · CANDIDATE CAPABILITY · RESEARCH REQUIRED · OPEN QUESTION |
| Evidenza | VERIFIED FACT · STRONG INFERENCE · DESIGN PROPOSAL · HYPOTHESIS · NOT CONFIRMED |

In questo documento, VERIFIED FACT vuol dire letto nel codice o nella documentazione indicati in §1, non provato in esecuzione: nessun test è stato eseguito.
Per le issue upstream, VERIFIED FACT vuol dire che **l'issue lo dichiara**: il problema segnalato non è stato riprodotto.

## 1. Fonti

| Repository | Commit analizzato | Licenza | Letto | Non letto |
|---|---|---|---|---|
| [geronimo-iia/llm-wiki](https://github.com/geronimo-iia/llm-wiki) | `c05dc91` (17/11/2026) | MIT OR Apache-2.0 | README, `docs/overview.md`, indice ADR (`docs/decisions/README.md`), `Cargo.toml`, `src/lib.rs`, API di `src/engine.rs`, `src/ingest.rs`, `git::commit` in `src/git.rs`, `src/links.rs` (wikilink), `install.ps1` | `docs/roadmap.md`, `docs/specifications/` (bloccati da rate limit), test |
| [nashsu/llm_wiki](https://github.com/nashsu/llm_wiki) | `e08cfce` (21/10/2026), v0.6.13 | GPL v3.0 | README (elenco funzionalità compreso), struttura di `src/`, `src/components/`, `src/stores/` e `src-tauri/`, `src-tauri/Cargo.toml`, import di `src/lib/ingest.ts`, `src/lib/ingest-queue.ts` (retry, persistenza), `src/lib/ingest-commit-coordinator.ts`, `src/lib/wiki-page-types.ts`, `src/lib/lint.ts` (tipi e funzioni), firme dei comandi in `src-tauri/src/commands/fs.rs`, moduli che importano `@/commands/fs`, intestazione di `src-tauri/src/commands/claude_cli.rs`, nomi dei tool in `mcp-server/src/index.ts`. **Rev. 3:** `src/stores/wiki-store.ts` (`dataVersion`), `src/components/layout/knowledge-tree.tsx`, `src/components/graph/graph-view.tsx` (caricamento e layout), `src/components/sources/sources-view.tsx`, `src/components/layout/activity-panel.tsx`, `src/lib/wiki-graph.ts`, `src/lib/graph-relevance.ts`, `src/lib/project-file-tree-refresh.ts`, `src/lib/scheduled-import.ts` (percorso veloce), `src/lib/llm-client.ts`, `src/lib/tauri-fetch.ts`, parti di `ingest.ts` (lettura di indice e overview, taglio dell'indice), `src-tauri/src/commands/file_sync.rs` (intervalli, snapshot, eventi), `src-tauri/src/api_server.rs` (rotte, scrittura pagine, cache del grafo), `src-tauri/src/clip_server.rs` (scrittura), intestazione di `src-tauri/src/agent/provider.rs`, `src-tauri/tauri.conf.json` (CSP). Ricerche per pattern su tutto `src/` (selettori zustand, `memo`, `setInterval`, librerie di virtualizzazione, WASM) | corpo completo di `ingest.ts` e `lint.ts`, test (contati, non eseguiti), `agent/runtime.rs` e `agent/tools.rs` oltre i punti citati |
| Issue di [nashsu/llm_wiki](https://github.com/nashsu/llm_wiki/issues) | consultate il 23–24/11/2026 | — | Titolo, stato, data e primi ~1.300 caratteri del corpo di #203, #359, #511, #524, #604, #647, #706, #714, #732, #763, #777, #810, #812 (tramite l'API di ricerca di GitHub); solo titolo di #795 | Commenti delle issue, corpo oltre il primo estratto, PR collegate → RR-16 |
| [Documentazione GitHub Actions — billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions) | consultata il 23/11/2026 | — | regole sui minuti per repository pubblici e privati | — |

I dati di adozione (stelle, fork, issue, PR) sono quelli della pagina del repository il 22–23/11/2026.

## 2. AS-IS — geronimo-iia/llm-wiki

| # | Fatto | Evidenza |
|---|---|---|
| G1 | Motore wiki headless in Rust: file Markdown, Git, ricerca full-text (tantivy, BM25), grafo (petgraph). Non contiene LLM né prompt: la sintesi è delegata alle skill del repository separato `llm-wiki-skills`. | VERIFIED FACT (README, overview) |
| G2 | Crate `llm-wiki-engine` 1.0.1 con target libreria `llm_wiki_engine` e binario `llm-wiki`. Non ha sezione `[features]`: usato come libreria porta con sé MCP (`rmcp`), `axum`, ACP e `clap`. | VERIFIED FACT (`Cargo.toml`) |
| G3 | `rust-version = "1.95"`, `edition = "2024"`. Circa 19.500 righe Rust in `src/`. | VERIFIED FACT |
| G4 | L'API `Engine` è orientata a un file di configurazione e a più wiki ("spaces"): `Engine::build(config_path)`, `mount_wiki`, `refresh_index`, `rebuild_index`. | VERIFIED FACT (`src/engine.rs`) |
| G5 | `ingest()` (240 righe) rifiuta il path traversal, valida i `.md` uno per uno contro il JSON Schema del tipo e, se richiesto, fa il commit alla fine. Il primo errore di validazione interrompe la funzione prima del commit: i file restano sul disco non committati e non c'è rollback. | VERIFIED FACT (`src/ingest.rs`) |
| G6 | `git::commit` esegue `add_all(["*"])`: committa tutto quello che c'è nella working tree, non solo i file validati. Esiste anche `git::commit_paths` per committare percorsi specifici. | VERIFIED FACT (`src/git.rs`) |
| G7 | Con più scrittori sulla stessa working tree, un commit di ingest può includere modifiche di altri. | STRONG INFERENCE (da G6) |
| G8 | Wikilink `[[slug]]` nel corpo letti con pulldown-cmark. Archi tipizzati dal frontmatter tramite `x-graph-edges` negli schemi. | VERIFIED FACT (`src/links.rs`, ADR) |
| G9 | Indice tantivy derivato e ricostruibile dai file committati. Un `Mutex` serializza solo il rebuild dell'indice. | VERIFIED FACT (overview, ADR) |
| G10 | Lint deterministico: orfani, link rotti, campi mancanti, pagine stale, con paginazione per wiki grandi. | VERIFIED FACT (README) |
| G11 | Concorrenza sulle scritture delle pagine e formato degli errori non sono documentati in overview. | NOT CONFIRMED → RR-02, RR-03 |
| G12 | Binari pubblicati nelle release GitHub (`install.ps1` scarica da `releases/latest`). | VERIFIED FACT |
| G13 | Server MCP su stdio e Streamable HTTP. | VERIFIED FACT (`Cargo.toml`, README) |
| G14 | Adozione: 52 stelle, 10 fork, 1.078 commit, 1 issue aperta. Ha ADR, CHANGELOG e roadmap. | VERIFIED FACT |

## 3. AS-IS — nashsu/llm_wiki

| # | Fatto | Evidenza |
|---|---|---|
| N1 | App desktop: Tauri v2 (Rust) con frontend React 19/TypeScript. Grafo con sigma.js, graphology, ForceAtlas2 e Louvain. | VERIFIED FACT (README) |
| N2 | Circa 95k righe nel frontend (`src/`) contro circa 35k nel backend Rust (`src-tauri/src/`). | VERIFIED FACT (conteggio) |
| N3 | La logica di ingest sta nel frontend TypeScript: `ingest.ts` (3.940 righe), `ingest-queue.ts` (1.286), `dedup-queue.ts` (405), `ingest-sanitize.ts` (278), `ingest-cache.ts` (151). | VERIFIED FACT |
| N4 | `ingest.ts` importa direttamente gli store Zustand (`useWikiStore`, `useChatStore`, `useActivityStore`, `useReviewStore`) e chiama l'LLM con `streamChat`: è accoppiato alla UI e ai provider. | VERIFIED FACT |
| N5 | Ingest in due fasi LLM: analisi (entità, concetti, contraddizioni), poi generazione delle pagine e di `index.md`, `log.md`, `overview.md`. Il riassunto della fonte viene sempre creato, anche se l'LLM lo omette. | VERIFIED FACT (README); non verificato nel codice |
| N6 | Cache SHA256 delle fonti: i file invariati vengono saltati. | VERIFIED FACT (README, `ingest-cache.ts`) |
| N7 | Coda: `MAX_RETRIES = 3`. Viene salvata in `.llm-wiki/ingest-queue.json` e ripristinata all'avvio, ma il salvataggio è best-effort: il codice dichiara autorevole la coda in memoria. | VERIFIED FACT (`ingest-queue.ts`) |
| N8 | Le scritture di `ingest.ts` passano da `writeFile` (`src/commands/fs.ts`), con circa 20 chiamate. `writeFileAtomic` esiste ma `ingest.ts` non lo usa. | VERIFIED FACT |
| N9 | Serializzazione in-process: `withProjectLock` (mutex per progetto) e `IngestCommitCoordinator`, che ordina le fasi di scrittura nell'ordine di avvio dei task. Qui "commit" significa scrittura su disco, non Git. | VERIFIED FACT |
| N10 | Niente Git e niente validazione con JSON Schema: nessuna dipendenza da ajv, zod o jsonschema. | VERIFIED FACT |
| N11 | Tipi di pagina generati: `source`, `entity`, `concept`, `comparison`, `query`, `synthesis`, `thesis`, `methodology`, `finding`. Frontmatter con `type`, `title`, `sources[]`. | VERIFIED FACT (`wiki-page-types.ts`, README) |
| N12 | Trasporto Claude Code CLI (`claude_cli.rs`): usa l'abbonamento Claude Code tramite il binario `claude`, senza API key, solo come motore di completamento testo. Esiste anche `codex_cli.rs`. | VERIFIED FACT |
| N13 | Server MCP in TypeScript (`mcp-server/`). Nei primi 11 tool letti (`status`, `projects`, `set_project`, `files`, `read_file`, `reviews`, `search`, `chat`, `graph`, `rescan_sources`, `embed_page`) non c'è scrittura diretta delle pagine. Espone anche un server HTTP locale su `127.0.0.1:19828`. | VERIFIED FACT (parziale) |
| N14 | Watcher sulle fonti (`src-tauri/src/commands/file_sync.rs`, crate `notify`). | VERIFIED FACT |
| N15 | Ricerca tokenizzata, grafo di rilevanza, ricerca vettoriale opzionale con LanceDB. | VERIFIED FACT (README, `Cargo.toml`) |
| N16 | Build: Node 20+, Rust 1.88+ (`edition = "2021"`), protoc. Artefatti `.dmg`, `.msi`, `.deb`, `.AppImage` prodotti in CI. | VERIFIED FACT (README, `Cargo.toml`) |
| N17 | Circa 152 file di test (`*.test.*`, `*.spec.*`, `*_test.rs`), tra cui scenari di ingest, integrazione della coda, collisioni di percorso e sanitizzazione. Dieci di questi (`*.real-llm.test.ts`) chiamano LLM reali. Non eseguiti. | VERIFIED FACT (conteggio) |
| N18 | Adozione: circa 20,8k stelle, 2,4k fork, 889 commit, 188 issue, 98 PR. | VERIFIED FACT |
| N19 | Lint proprio, su due livelli. Strutturale (`runStructuralLint`): pagine orfane, link rotti, pagine senza link in uscita, con `index.md` e `log.md` esclusi dagli orfani. Semantico (`runSemanticLint`) via LLM. Correzioni automatiche in `lint-fixes.ts`, vista dedicata in `components/lint`. | VERIFIED FACT (`lint.ts`, struttura) |
| N20 | Tutto l'I/O su file del frontend passa dai comandi Tauri di `src-tauri/src/commands/fs.rs`: `write_file`, `write_file_base64`, `write_file_atomic`, `delete_file`. 51 moduli non di test importano `@/commands/fs`. | VERIFIED FACT |
| N21 | Oltre all'ingest, nelle pagine scrivono o cancellano anche altre funzionalità. Tra i moduli che importano `@/commands/fs` ci sono editor (`wiki-editor.tsx`), correzioni del lint, cancellazione a cascata (`source-lifecycle.ts`, `wiki-page-delete.ts`), revisione, deep research, arricchimento dei wikilink, deduplicazione, manutenzione del progetto e import pianificato. | VERIFIED FACT (importazioni); quali scrivano davvero nelle pagine è STRONG INFERENCE |
| N22 | La scansione del progetto nasconde le voci che iniziano con un punto, `.git` compreso. | VERIFIED FACT (`fs.rs`, `project-file-tree-refresh.ts`) |
| N23 | Esiste già una cronologia dei file (`commands/file_history.rs`, `file-history-panel.tsx`). | VERIFIED FACT (struttura) |
| N24 | L'agente chat del backend Rust ha una cartella di lavoro propria, `agent-workspace/`. | VERIFIED FACT (`agent/workspace.rs`); che scriva solo lì è da verificare → RR-10 |
| N25 | Due client LLM distinti: `src/lib/llm-client.ts` (TypeScript, HTTP tramite `tauri-plugin-http`, usato da ingest, chat, deep research, lint, dedup) e `src-tauri/src/agent/provider.rs` (Rust, `reqwest`, usato dal runtime dell'agente). | VERIFIED FACT (`llm-client.ts`, `tauri-fetch.ts`, `provider.rs`) |
| N26 | Coda e orchestrazione dell'ingest vivono nella webview. Il watcher Rust emette `file-sync://changed` e `file-sync://queue-updated` (`file_sync.rs:22-23`); l'accodamento lo fa il frontend (`project-file-sync.ts:358`, `clip-watcher.ts:40`). | VERIFIED FACT |
| N27 | Tra le rotte dell'API HTTP trovate in `api_server.rs` (`health`, `projects`, `chat`, `search`, `graph`, `pages/write`, `pages/embed`) non ce n'è una di ingest: API e MCP non possono avviare un ingest senza la finestra dell'app. | VERIFIED FACT (rotte); l'impossibilità è STRONG INFERENCE |
| N28 | Scritture fuori dai comandi Tauri di `commands/fs.rs`: `POST /pages/write` scrive le pagine in Rust tramite `agent::tools::write_wiki_page_verified` (`api_server.rs:1840-1853`); lo stato delle review è scritto con `fs::write` (`api_server.rs:1811`); il clip server scrive in `raw/` con `std::fs::write` (`clip_server.rs:493`). | VERIFIED FACT → risponde in parte a RR-11 |
| N29 | Il prompt di generazione dell'ingest include `wiki/index.md` e `wiki/overview.md` (`ingest.ts:783-784`, `1136`). L'indice è limitato a 32.000 caratteri (`WIKI_INDEX_PROMPT_MAX_CHARS`, `ingest.ts:66`): oltre il limite tiene circa il 60% iniziale e il 40% finale e omette il centro (`boundWikiIndexForPrompt`, `ingest.ts:3009-3022`). | VERIFIED FACT |
| N30 | `write_task_meta_to_snapshot` legge, modifica e riscrive l'intero snapshot dei file a ogni task di cambiamento (`file_sync.rs:996`). Rescan periodico del watcher: 10 s su Linux, 60 s sulle altre piattaforme (`file_sync.rs:32-33`). | VERIFIED FACT |
| N31 | `wiki-store.dataVersion` è un unico contatore per tutto il progetto (`wiki-store.ts:453, 753`). Lo incrementano 4 moduli direttamente e 19 chiamate a `refreshProjectFileTree({ bumpDataVersion: true })` in 14 file (lint, review, editor, chat, ingest, sincronizzazione file, import pianificato, deep research, manutenzione). Non porta l'informazione su quale file sia cambiato. | VERIFIED FACT |
| N32 | A ogni incremento di `dataVersion`: `knowledge-tree.tsx:63-100` rilegge **tutte** le pagine `.md` in sequenza, con una chiamata IPC `readFile` per file; `graph-view.tsx:700-754` ricostruisce il grafo con `buildWikiGraph`, che rilegge e rianalizza tutte le pagine (`wiki-graph.ts`); `sources-view.tsx` rilegge l'elenco di `raw/sources`. I dati derivati restano in `useState` locali ai componenti, senza cache condivisa. | VERIFIED FACT |
| N33 | Nessuna libreria di virtualizzazione delle liste in `package.json`. Lato zustand: 210 sottoscrizioni con selettore e 0 senza; `ChatMessage` è memoizzato (`chat-message.tsx:314`); l'Activity Panel riceve la coda per sottoscrizione e non più con polling (`activity-panel.tsx:104`); il layout ForceAtlas2 gira in un worker con ripiego sul thread principale (`graph-view.tsx:322-415`); le community passano al worker da 500 nodi (`wiki-graph.ts:38`). | VERIFIED FACT |

## 4. Confronto sintetico

| Aspetto | geronimo-iia | nashsu |
|---|---|---|
| Natura | Motore headless per agenti | App desktop con UI |
| Chi chiama l'LLM | Nessuno: lo fa l'agente | L'app (provider configurati o Claude CLI), con due client distinti (N25) |
| Validazione | JSON Schema per tipo, deterministica | Fallback e struttura del frontmatter |
| Versionamento | Git | Nessun Git; cronologia dei file propria (N23) |
| Atomicità dell'ingest | No (G5) | No (N8) |
| Retry | Non documentato | 3 tentativi, senza feedback degli errori |
| Incrementalità | `changed_paths` sulla validazione | Hash SHA256 per fonte; viste e grafo invece ricaricano tutto (N31, N32) |
| Grafo | Archi tipizzati (petgraph), in Rust | Wikilink, rilevanza a 4 segnali, comunità, calcolati in TypeScript |
| Lint | Deterministico: orfani, link rotti, campi mancanti, stale | Strutturale (orfani, link rotti, nessun link in uscita) e semantico via LLM, con correzioni (N19) |
| Ricerca | BM25 (tantivy) | Tokenizzata, LanceDB opzionale |
| Chi scrive le pagine | I tool del motore | Molte funzionalità, quasi tutte tramite `commands/fs.rs` (N20, N21); API e agente scrivono direttamente in Rust (N28) |
| Licenza | MIT OR Apache-2.0 | GPL v3.0 |

Nessuno dei due ha una transazione di ingest: un task interrotto a metà può lasciare la wiki in uno stato intermedio.

## 5. Direzione confermata

- **CONFIRMED DIRECTION** (dichiarata il 23/11/2026): nuova applicazione che parte dal modello di app di nashsu (configurabilità, visualizzazione del grafo) e da lì sostituisce o fonde parti con il modello di geronimo-iia.
- **CONFIRMED DIRECTION** (dichiarata il 23/11/2026): tutte le funzionalità di nashsu restano **as-is** (inventario in §6).
- **Lettura adottata per il vincolo as-is** (DESIGN PROPOSAL, da confermare): nessuna funzionalità di nashsu viene rimossa e il comportamento predefinito resta quello di oggi. Quello che arriva da geronimo-iia si aggiunge e si attiva da configurazione. Dove le due applicazioni fanno la stessa cosa (lint, ricerca, cronologia, watcher, server MCP), resta la versione di nashsu e quella di geronimo-iia si affianca, senza sostituirla.
- **OPEN QUESTION** (sollevata il 24/11/2026): il vincolo as-is, nella lettura additiva, non permette di risolvere i problemi di scala (§12.6). Le alternative sono registrate in DC-12 e descritte in §13.
- **CONFIRMED DIRECTION** (dichiarata il 24/11/2026): **niente WASM** come leva di prestazioni (§14).
- **Conseguenza di licenza** (VERIFIED FACT sulle licenze; non è un parere legale): il fork eredita GPL v3. Il codice MIT/Apache di geronimo-iia può entrare in un'opera GPL v3. L'uso interno non comporta obblighi di pubblicazione. Distribuire l'applicazione a terzi, per esempio ai clienti, comporta gli obblighi GPL sul sorgente → DC-07.

## 6. Inventario delle funzionalità nashsu da preservare

Fonte: README (sezioni "Features" e "Other Additions") e struttura del codice al commit `e08cfce`.

| Area | Funzionalità |
|---|---|
| Ingest e fonti | Ingest in due fasi con tracciabilità delle fonti e cache incrementale; ingest multimodale delle immagini (estrazione dai PDF, didascalie con modello vision, risultati di ricerca con immagini); parsing multi-formato (PDF, Office, EPUB/MOBI, Org, immagini, media, web clip, lotti di URL) con MinerU integrato, cloud o locale; import di cartelle con struttura preservata; watcher di `raw/sources/` con pulizia; coda persistente con annullamento, retry e avanzamento; cancellazione a cascata; deduplicazione |
| Grafo e ricerca | Grafo a 4 segnali (link diretti, fonti in comune, Adamic-Adar, affinità di tipo); comunità Louvain con punteggio di coesione; Graph Insights (connessioni sorprendenti, lacune) con Deep Research in un clic; ricerca vettoriale opzionale con LanceDB; pipeline di retrieval ottimizzata; modalità Read Sources Only |
| Chat e agente | Chat multi-conversazione persistente; agente chat nel backend Rust con tool su wiki, fonti, grafo e web, generazione di file nel workspace, approvazione dei comandi shell, annullamento; agent skill (`SKILL.md`, `/skill`); anteprima degli output generati; visualizzazione del reasoning; KaTeX e Mermaid |
| Qualità e ricerca esterna | Revisione asincrona con human-in-the-loop; lint strutturale e semantico con correzioni; Deep Research (Tavily, SerpApi, SearXNG); Firecrawl configurabile |
| Integrazioni | API HTTP locale `127.0.0.1:19828`; server MCP; agent skill `llm_wiki_skill`; provider LLM multipli (OpenAI, Anthropic, Google, Ollama, personalizzati); trasporti Claude Code CLI e Codex CLI; Chrome Web Clipper |
| Progetto e configurazione | Modelli configurabili per progetto, con chat e ingest separati; `purpose.md` e `schema.md`; finestra di contesto e timeout configurabili; export/import ZIP del progetto; ricostruzione deterministica di `wiki/index.md`; cartella `.obsidian/` generata; impostazioni persistenti; cronologia dei file |
| Interfaccia | Interfaccia in inglese e cinese; barra laterale richiudibile; editor Milkdown; aggiornamento automatico di grafo e UI quando cambia la wiki; icona nella tray e avvio automatico; build per macOS, Windows e Linux |

**Criterio di non regressione** (DESIGN PROPOSAL), valido per ogni fase:
1. la suite di test di nashsu, esclusi i `*.real-llm.test.ts`, resta verde sul fork;
2. le funzionalità dell'inventario non coperte dai test superano una prova manuale breve, con una checklist da scrivere in Fase 0;
3. con le funzionalità di geronimo-iia disattivate (modalità `off`, §7.4), il comportamento è indistinguibile da nashsu;
4. **(rev. 3)** le misure di carico della Fase 0b non peggiorano (tempi, CPU a riposo, chiamate IPC, token per ingest).

Se DC-12 adotta la variante B (§13), il punto 3 si sostituisce con la checklist dell'inventario più i test di scenario: il comportamento resta equivalente per l'utente, non identico nell'implementazione.

## 7. Architettura proposta (DESIGN PROPOSAL)

### 7.1 Principio: integrazione additiva

| Resta da nashsu | Si aggiunge da geronimo-iia | Da scrivere (non c'è in nessuno dei due) |
|---|---|---|
| Tutte le funzionalità dell'inventario (§6), con il comportamento di oggi | Validazione con JSON Schema per tipo | Registro dei file toccati per operazione (§7.3) |
| Le pagine continuano a scriverle le funzionalità di nashsu | Git come cronologia e punto di ripristino, accanto alla cronologia di nashsu | Commit per operazione con `commit_paths` |
| Lint, ricerca, watcher, server MCP e API HTTP di nashsu | Archi tipizzati; controlli di lint aggiuntivi (campi mancanti, stale, schema); indice BM25 e MCP per gli agenti | Modalità di validazione configurabile (§7.4) |
| | | Transazione e retry informato, solo in modalità `strict` (§7.5, §7.6) |

Questa architettura riguarda la correttezza delle scritture. Per l'effetto sulla scala vedi §12.6.

### 7.2 Il motore come processo separato

geronimo-iia gira come processo separato accanto all'app, in modalità Streamable HTTP (G13), e non viene incluso come libreria. È **l'unico processo che scrive su Git**. Le pagine invece continuano a scriverle le funzionalità di nashsu (N21): il motore valida, indicizza e committa.

Motivi:
- si usano i binari delle release (G12) e non serve compilare Rust 1.95 (G3);
- il codice di geronimo-iia resta com'è, quindi niente secondo fork da mantenere;
- si evita di portarsi dietro MCP, ACP e axum dentro il backend Tauri (G2);
- lo stesso motore serve sia l'app sia gli agenti.

Alternativa: includerlo come libreria nel backend Rust, se il processo separato desse problemi di pacchetto o di latenza → DC-02. Nella variante B di DC-12 la libreria diventa la proposta (§13.3).

### 7.3 Punto di innesto: i comandi di scrittura Rust

Le scritture del frontend passano da `src-tauri/src/commands/fs.rs` (N20). Il punto di innesto principale è lì, non in `ingest.ts`:
- ogni `write_file`, `write_file_base64`, `write_file_atomic` e `delete_file` sotto `wiki/` registra il percorso nell'operazione in corso;
- alla fine dell'operazione (task di ingest, correzione del lint, cancellazione a cascata, azione di revisione, import) il motore valida i file registrati e li committa con `commit_paths`;
- per le scritture senza un confine naturale, come i salvataggi dell'editor, la granularità dei commit è da decidere → DC-09.

**Correzione (rev. 3, da RR-11):** `commands/fs.rs` **non** è l'unico punto di scrittura (N28). Il registro va agganciato anche a:
- `agent::tools::write_wiki_page_verified`, usata da `POST /pages/write` dell'API HTTP e quindi dal server MCP e dagli agenti: è il canale della Fase 5 (DC-10);
- i tool dell'agente Rust che scrivono pagine, se ce ne sono altri oltre a quello (RR-10 resta aperto).

Il clip server scrive in `raw/` (`clip_server.rs:493`) e non nelle pagine: non va registrato, ma è l'ingresso di un ingest. Lo stato delle review (`api_server.rs:1811`) non è una pagina.

Così le funzionalità che usano `@/commands/fs` restano invariate, e `ingest.ts`, il file più grande e più modificato nel progetto originale, si tocca al massimo per segnare inizio e fine del task.

### 7.4 Modalità di validazione configurabile

| Modalità | Comportamento |
|---|---|
| `off` | Comportamento di nashsu puro: il motore non interviene |
| `warn` | Le scritture avvengono come oggi. Il motore valida e committa; gli errori diventano avvisi nella vista lint e nell'Activity Panel. Nessun blocco |
| `strict` | Solo per i task di ingest: transazione (§7.5) e retry informato (§7.6). Le altre funzionalità restano in `warn` |

Quale sia la modalità predefinita è da decidere → DC-08. Proposta: `warn`, che aggiunge senza cambiare il comportamento.

### 7.5 Transazione di ingest (solo `strict`)

La working tree fa da area provvisoria e HEAD è l'ultimo stato coerente.

```
coda nashsu ─► LLM (analisi → generazione) ─► write_file nella working tree
                                                   │ (percorsi registrati, §7.3)
                                                   ▼
               motore (processo separato, unico scrittore Git)
               validazione del lotto senza scrittura
                 ├─ ok ─► commit_paths dei soli file del task ─► indice + grafo
                 └─ ko ─► ripristino da HEAD dei file toccati
                          + rimozione dei file nuovi del task
                          ─► errori JSON ─► retry (§7.6)
```

Vincoli:
- usare `commit_paths` e non `commit`, che fa `add_all` (G6);
- durante un task nessun'altra funzionalità scrive nei file del task: da verificare che `withProjectLock` copra tutte le scritture (RR-11). `withProjectLock` è un mutex TypeScript: le scritture Rust di N28 non lo prendono (STRONG INFERENCE, da verificare);
- il ripristino è codice nuovo: in geronimo-iia non esiste (G5).

### 7.6 Retry informato (solo `strict`)

Gli errori di validazione, in JSON con codice e motivo, diventano input del nuovo tentativo di generazione. Il limite resta `MAX_RETRIES = 3` (N7). Dopo l'ultimo tentativo il task va in `failed`, con gli errori leggibili nell'Activity Panel.

Ogni retry è una nuova chiamata di generazione: su wiki grandi, con prompt che crescono (§12.3), il costo aumenta.

### 7.7 Due modalità di ingest (CANDIDATE CAPABILITY)

- **In-app**, invariata: l'LLM è chiamato da nashsu, tramite Claude CLI (N12) o un provider configurato.
- **Guidata da agenti**: gli agenti della Factory fanno la sintesi e usano il motore via MCP, senza API key. L'adapter llm-wiki dello starter kit punta al fork. Da dove passino le scritture degli agenti è da decidere → DC-10.

Il server MCP di nashsu resta com'è. Il motore aggiunge un secondo endpoint MCP: due insiemi di tool simili possono confondere gli agenti → RR-09.

La modalità guidata da agenti è anche l'unico percorso, nella variante A, che non passa dalla webview (N26, N27).

## 8. Piano a fasi

Ogni fase ha anche il criterio di non regressione di §6.

| Fase | Contenuto | Criterio di uscita |
|---|---|---|
| 0. Prova di compatibilità | Fork; build `.msi` in CI; esecuzione della suite di test di nashsu sul fork come baseline; checklist di prova manuale per l'inventario; wiki generata da nashsu su 5–10 documenti reali; validazione di geronimo-iia senza scrittura (`dry_run`) | Baseline dei test registrata; report con le incompatibilità per tipo di pagina, campo e link; build Windows installabile |
| **0b. Misura di carico** (rev. 3) | Generatore di wiki sintetiche (500, 1.000, 2.000, 5.000 pagine, con link e frontmatter realistici). Misure: tempo di apertura del grafo, CPU a riposo con watcher attivo, chiamate `invoke` per ogni incremento di `dataVersion`, tempi del React Profiler durante un ingest con albero e grafo aperti, token del prompt di generazione per ingest → RR-12 | Baseline numerica registrata per ogni dimensione |
| **P. Prestazioni a comportamento invariato** (rev. 3) | Interventi compatibili con il vincolo as-is letto come comportamento (§12.7): snapshot incrementale; un solo scanner periodico; invalidazione per percorso al posto di `dataVersion`; lettura dei metadati delle pagine in blocco; liste virtualizzate; grafo incrementale. Ognuno proposto anche a monte (DC-15). Può procedere in parallelo alle Fasi 1-2 | CPU a riposo vicina a zero con 2.000 pagine; un cambiamento di una pagina produce O(1) letture, non O(N); soglie di tempo da fissare sulla baseline 0b |
| 1. Formato | JSON Schema per i 9 tipi (N11); trattamento di `index.md`, `log.md`, `overview.md`; mappatura degli archi (`sources`, wikilink, eventuali `concepts`) | Validazione senza errori sulla wiki della Fase 0 |
| 2. Git e validazione in `warn` | Motore come processo separato; `git init` della wiki; registro dei file toccati in `commands/fs.rs` **e in `write_wiki_page_verified`** (§7.3); commit per operazione; modalità `off` e `warn` | Ogni operazione dell'inventario che scrive pagine, comprese API e agente, produce un commit con i soli suoi file; in `off` nessuna differenza da nashsu |
| 3. Modalità `strict` | Transazione (§7.5) e retry informato (§7.6) per i task di ingest | Un task interrotto a metà lascia la wiki identica a HEAD; un task con frontmatter non valido si corregge al retry oppure finisce in `failed` con errori leggibili |
| 4. Lettura | Controlli di lint di geronimo-iia nella vista lint di nashsu; archi tipizzati nel grafo, attivabili; cronologia Git accanto a quella di nashsu | Funzionalità aggiunte visibili nella UI; quelle di nashsu invariate; misure 0b non peggiorate |
| 5. Canale per gli agenti | Agenti della Factory sullo stesso motore via MCP; adapter dello starter kit verso il fork | Un agente esegue un ingest completo senza API key |

Il contesto di ingest per recupero (DC-14) cambia il comportamento dell'ingest: nella variante A entra solo come modalità configurabile, spenta per default. Il piano della variante B è in §13.5.

## 9. Decision Candidate

Numerazione locale a questo dossier.

| ID | Decisione | Elementi | Proposta |
|---|---|---|---|
| DC-01 | Fork pubblico o privato | GPL v3 in entrambi i casi. I runner standard di GitHub Actions sono gratuiti nei repository pubblici; nei privati consumano la quota, e i runner Windows e macOS la consumano più in fretta. La build Tauri su Windows è lunga; compilarla sul PC aziendale (Rust, MSVC, protoc, WebView2) potrebbe non essere possibile. | Da decidere insieme a DC-07 |
| DC-02 | Motore: processo separato o libreria | §7.2, §13.3 | Variante A: processo separato. Variante B: libreria, o moduli copiati |
| DC-03 | Rapporto con il progetto originale nashsu | Molto attivo (98 PR aperte). Il vincolo as-is rende utile ricevere anche le funzionalità future | Variante A: fondere periodicamente; innesto in `commands/fs.rs` e moduli nuovi per ridurre i conflitti. Variante B: riprendere a mano le modifiche scelte, dopo aver portato a monte le correzioni locali (DC-15) |
| DC-04 | Ricerca | nashsu (tokenizzata + LanceDB) contro tantivy | nashsu invariata per la UI; tantivy in aggiunta per gli agenti e, con DC-14, per il contesto di ingest |
| DC-05 | Watcher | Due watcher (N14, `watch.rs` di geronimo-iia) sulle stesse cartelle | Resta quello di nashsu; quello del motore disattivato |
| DC-06 | Pagine speciali `index.md`, `log.md`, `overview.md` | Generate da nashsu; `log.md` è un doppione di `git log` ma la UI lo usa. `index.md` e `overview.md` entrano nel prompt di ogni ingest (N29) | Restano come sono; escluse dalla validazione con `[ingest] exclude`. Con DC-14 smettono di essere input del prompt |
| DC-07 | Distribuzione dell'app a clienti o terzi | Determina gli obblighi GPL v3 (§5) | OPEN QUESTION |
| DC-08 | Modalità di validazione predefinita | §7.4 | `warn` |
| DC-09 | Granularità dei commit per le scritture senza confine naturale (editor, correzioni manuali) | Un commit a ogni salvataggio sporca la cronologia; troppo pochi la rendono inutile | Commit a fine sessione di modifica di una pagina o dopo un intervallo senza scritture |
| DC-10 | Da dove passano le scritture degli agenti (Fase 5) | Se gli agenti scrivono tramite il motore, Git e pagine hanno due scrittori; se passano da nashsu (API HTTP), il motore resta solo validatore. L'API di nashsu scrive in Rust fuori da `commands/fs.rs` (N28) | Scritture degli agenti tramite nashsu, con il registro agganciato a `write_wiki_page_verified`; il motore resta validatore, indice e Git |
| DC-11 | Lint: due motori | nashsu (N19) e geronimo-iia (G10) si sovrappongono su orfani e link rotti | Lint di nashsu invariato; da geronimo-iia solo i controlli che mancano (campi, stale, schema) come categoria aggiuntiva |
| DC-12 | Lettura del vincolo as-is | **A** (attuale): additivo, codice di nashsu invariato salvo l'innesto. **A+P**: additivo più correzioni a comportamento invariato (Fase P). **B**: funzionalità dell'inventario preservate, implementazione libera (§13). A non risolve la scala (§12.6) | A+P subito; B da decidere dopo la baseline 0b e la Fase P, sulla base dei numeri |
| DC-13 | Linguaggio dell'orchestrazione dell'ingest (solo variante B) | Port in Rust; sidecar Node con il codice attuale; Web Worker nella webview (§13.4) | Prima disaccoppiare `ingest.ts` dagli store (interfacce per storage, LLM, eventi); poi port in Rust a pezzi, cominciando da coda, cache, guardia dei percorsi e scritture |
| DC-14 | Contesto di ingest per recupero | Oggi il prompt include `index.md` tagliato in mezzo e `overview.md` (N29). Alternativa: passare solo le pagine pertinenti alla fonte, trovate con BM25 (tantivy) e LanceDB. Cambia il comportamento dell'ingest. Issue upstream #511, #706; #795 propone un'idea simile per le review | Variante A: modalità configurabile, spenta per default. Variante B: comportamento predefinito, dopo il confronto sulla wiki sintetica |
| DC-15 | Contributi a monte | Le correzioni locali di Fase P sono utili a tutti gli utenti di nashsu e riducono la divergenza del fork | Proporre a monte ogni intervento di Fase P, con le misure di 0b come motivazione → RR-13 |
| DC-16 | Fonte unica dell'indice delle pagine | Oggi ogni vista ricostruisce i propri dati dal disco (N32). Opzioni: indice normalizzato nello store TypeScript aggiornato dagli eventi del watcher; indice in Rust (variante B: tantivy e petgraph) con proiezione nello store | Variante A+P: indice nello store TypeScript, alimentato da `file-sync://changed` e da una lettura in blocco. Variante B: indice in Rust |

## 10. Rischi

| Rischio | Effetto | Mitigazione |
|---|---|---|
| Regressione su funzionalità dell'inventario | Viola il vincolo as-is | Criterio di non regressione (§6), modalità `off` |
| Progetto originale nashsu molto attivo | Conflitti di merge | §7.3, DC-03 |
| Doppioni (lint, cronologia, ricerca, MCP) | Più manutenzione, utenti e agenti confusi | Una sola versione esposta per ogni funzione nella UI; DC-04, DC-11, RR-09 |
| geronimo-iia con un solo maintainer apparente (G14) | Motore non più aggiornato | Codice MIT/Apache: si può rilevare se serve |
| Concorrenza ed errori di geronimo-iia non documentati (G11) | Comportamento imprevisto con più client | Unico scrittore Git (§7.2), RR-02, RR-03 |
| Coda di nashsu salvata in modo best-effort (N7) | Perdita di stato dopo un crash | RR-05 |
| Build Tauri su PC aziendale Windows | Impossibilità di compilare in locale | Build in CI, DC-01 |
| Claude CLI sotto policy aziendali gestite | Trasporto in-app non utilizzabile | RR-04 |
| **(rev. 3)** Degradazione oltre ~1.000 pagine (§12) | App lenta o bloccata proprio sulle wiki che il progetto vuole gestire | Fase 0b e Fase P; DC-12, DC-14, DC-16 |
| **(rev. 3)** Piano additivo che aggiunge lavoro per operazione (validazione, commit, indice) | Peggiora la scala se applicato senza Fase P | Criterio 4 di §6; misure 0b ripetute dopo le Fasi 2 e 4 |
| **(rev. 3)** Registro dei file toccati incompleto (N28) | Commit e transazioni con buchi su API e agente | §7.3 corretto; RR-10, RR-11 |
| **(rev. 3)** Divergenza dal progetto originale nella variante B | Funzionalità future di nashsu da riportare a mano | DC-03, DC-15: portare a monte tutto ciò che è locale |
| **(rev. 3)** Indice tagliato nel prompt di ingest (N29) | Il modello non vede parte della wiki e crea pagine doppie invece di aggiornare quelle esistenti | HYPOTHESIS → RR-15; DC-14 |

## 11. Research Required

| ID | Domanda | Dove guardare |
|---|---|---|
| RR-01 | Cosa fa nashsu quando l'LLM produce frontmatter non valido o contraddice una pagina esistente | `ingest.ts`, `ingest-sanitize.ts`, scenari di test |
| RR-02 | Contratti di `wiki_ingest` e degli altri tool, formato degli errori | `docs/specifications/` di geronimo-iia |
| RR-03 | Se il motore in modalità HTTP serializza le scritture concorrenti | Codice di `src/mcp`, `src/ops`, test di integrazione |
| RR-04 | Se il binario `claude` usato come completamento testo funziona sul PC aziendale con policy gestite | Prova locale |
| RR-05 | Cosa resta della coda di nashsu dopo un crash durante un task | Prova con interruzione forzata |
| RR-06 | Compatibilità tra la struttura di cartelle di nashsu (`raw/`, `wiki/`, `.llm-wiki/`) e quella attesa da geronimo-iia (`wiki.toml`, `schemas/`, `inbox/`, `raw/`, `wiki/`) | Fase 0 |
| RR-07 | Roadmap di geronimo-iia: cosa è pianificato su atomicità, concorrenza ed errori | `docs/roadmap.md` |
| RR-08 | Come l'export/import ZIP del progetto tratta la cartella `.git` | `project_maintenance.rs`, `maintenance-section.tsx` |
| RR-09 | Come presentare agli agenti due server MCP (nashsu e motore) senza ambiguità nei tool | Elenco completo dei tool di entrambi |
| RR-10 | Se l'agente del backend Rust scrive solo in `agent-workspace/` o anche nelle pagine. Rev. 3: `write_wiki_page_verified` sta in `agent/tools.rs` e scrive pagine per l'API (N28); resta da vedere se anche i tool dell'agente la usano | `agent/runtime.rs`, `agent/tools.rs` |
| RR-11 | **Parzialmente risolta (rev. 3).** `commands/fs.rs` non è l'unico punto di scrittura: API (`write_wiki_page_verified`), stato delle review, clip server (N28). Resta aperto: elenco completo delle scritture dirette in Rust (manutenzione, estrazione immagini, cronologia) e copertura di `withProjectLock`, che è un mutex TypeScript e non vede le scritture Rust | `src-tauri/src/` per `fs::write`, `File::create`, `rename`, `remove_file`; `src/lib/project-mutex.ts` |
| RR-12 | Baseline di carico: quanto pesano davvero le cause di §12 a 500, 1.000, 2.000 e 5.000 pagine | Fase 0b |
| RR-13 | Disponibilità del maintainer di nashsu ad accettare PR di prestazioni e di architettura (#777 è aperta senza esito letto) | Commenti di #777, #812; PR collegate |
| RR-14 | Stato in v0.6.13 dei punti di #812 non ancora verificati: tre scansioni indipendenti (file_sync, import pianificato, progetti inattivi) e loro sovrapposizione reale. Verificato: percorso veloce size + mtime nell'import pianificato; nessun `setInterval` in `sources-view.tsx` | `project-file-sync.ts:128`, `scheduled-import.ts:652`, `file_sync.rs` |
| RR-15 | Se il taglio dell'indice nel prompt (N29) produce pagine doppie su wiki grandi | Ingest della stessa fonte su wiki sintetiche di dimensione crescente; conteggio delle pagine nuove contro quelle aggiornate |
| RR-16 | Commenti e PR collegate delle issue di scala, non letti (§1) | Issue #203, #524, #604, #810, #812 |

## 12. Scalabilità oltre ~1.000 pagine (rev. 3)

### 12.1 Sintomi segnalati

| Issue | Stato | Data | Dimensione | Sintomo dichiarato |
|---|---|---|---|---|
| #203 | aperta | 19/05/2026 | 2.000+ file | Rallentamenti evidenti |
| #359 | chiusa | 07/06/2026 | ~1.000 pagine | Ricerca dei duplicati in un solo prompt con tutte le pagine: decine di migliaia di token, timeout |
| #511 | chiusa | 01/07/2026 | wiki grandi | Ogni ingest legge e rigenera `index.md` e `overview.md`, che crescono senza limite |
| #524 | aperta | 02/07/2026 | import massivo | Finestra bloccata a lungo; `file-change-queue.json` riscritto di continuo |
| #604 | aperta | 22/07/2026 | ~7.000 pagine | Lista della wiki e grafo molto lenti; app inutilizzabile durante l'ingest |
| #647 | chiusa | 05/08/2026 | 20.000+ pagine | Grafo: circa 2 minuti di caricamento, finestra bloccata |
| #706 | aperta | 26/08/2026 | — | Input di 1,7 milioni di token contro un contesto di 524.000 |
| #714 | chiusa | 28/08/2026 | 4.359 pagine | `/graph` dell'API: tetto di 1.000 nodi, ~24 s per richiesta, nessuna cache |
| #732 | chiusa | 07/09/2026 | soglia 3.000 | Sotto i 3.000 nodi Louvain sul thread principale; sopra, modello di rilevanza scartato senza avviso |
| #763 | chiusa | 16/09/2026 | — | Risoluzione degli alias dei link O(N×E), sincrona, sul thread principale |
| #777 | aperta | 20/09/2026 | — | Chiede di spostare l'orchestrazione fuori dalla UI |
| #810 | aperta | 09/10/2026 | ~60.000 file | UI bloccata dopo una notte; 20 GB di memoria |
| #812 | aperta | 10/10/2026 | ~1.000 pagine | ~4 core occupati in media anche a riposo: hash completi, snapshot da 1,4 MB riscritto ogni ~15 s, tre scansioni periodiche indipendenti, polling della UI ogni secondo |

### 12.2 Causa 1 — grafo e analisi nel frontend

Grafo, rilevanza a 4 segnali, community e insight si calcolano in TypeScript nella webview, rileggendo tutte le pagine (N32). Le correzioni di #732 e #763 hanno spostato Louvain e ForceAtlas2 in worker e tolto la complessità quadratica (N33), ma ogni cambiamento della wiki ricostruisce ancora il grafo da zero. VERIFIED FACT (codice); il peso residuo è da misurare (RR-12).

### 12.3 Causa 2 — prompt di ingest che crescono con la wiki

Ogni ingest include `index.md` e `overview.md` (N29). Il taglio a 32.000 caratteri evita gli errori di contesto, ma oltre una certa dimensione il modello vede solo inizio e fine dell'indice. Più pagine esistenti comportano anche più merge, ciascuno con una chiamata LLM. VERIFIED FACT (codice); l'effetto sulla duplicazione è HYPOTHESIS (RR-15).

### 12.4 Causa 3 — React: invalidazione globale e ricarica completa

L'uso di zustand è corretto a livello di selettori (N33): il problema non è il re-render a grana grossa. Il problema è che lo store **non contiene i dati della wiki**, ma solo un contatore di versione (N31). A ogni incremento ogni vista rilegge tutto dal disco per conto proprio (N32):

```
scrittura qualsiasi (ingest, editor, lint, review, watcher, ricerca…)
        │ bumpDataVersion()
        ▼
wiki-store.dataVersion++          (un numero per tutto il progetto)
        ├─► knowledge-tree: listDirectory + readFile di ogni .md, in sequenza (N chiamate IPC)
        ├─► graph-view (se aperto): buildWikiGraph, rilettura e analisi di tutte le pagine
        ├─► sources-view: rilettura dell'elenco di raw/sources
        └─► page-links-panel
            → dati in useState locali, nessuna cache condivisa
```

In più le liste non sono virtualizzate: albero, fonti, review e lint montano tutti gli elementi nel DOM. Il costo di un cambiamento cresce con la dimensione della wiki, non con quella del cambiamento. VERIFIED FACT (codice).

### 12.5 Causa 4 — scansioni e snapshot completi nel backend

Lo snapshot dei file è riscritto per intero a ogni task (N30); rescan del watcher ogni 10 s su Linux e 60 s altrove (N30); altre scansioni periodiche nell'import pianificato e nei progetti inattivi (#812, RR-14). L'hash completo a ogni scansione dell'import pianificato è corretto in v0.6.13 (RR-14). VERIFIED FACT per lo snapshot e gli intervalli.

### 12.6 Effetto del piano additivo (§7) sulle cause

| Causa | Cosa fa il piano additivo | Effetto |
|---|---|---|
| 1. Grafo nel frontend | Grafo di nashsu invariato; archi tipizzati in aggiunta | Nessuno; con gli archi tipizzati accesi, più lavoro |
| 2. Prompt che crescono | DC-06: `index.md` e `overview.md` restano come sono | Nessuno; il retry informato aggiunge chiamate |
| 3. Invalidazione globale in React | Nessun intervento | Nessuno |
| 4. Scansioni e snapshot | DC-05 tiene il watcher di nashsu | Nessuno; validazione, commit e indice aggiungono lavoro per operazione |
| Ingest legato alla webview (#777) | Fase 5: ingest guidato da agenti via MCP | Parziale: solo per quel percorso |

STRONG INFERENCE: il piano additivo migliora la correttezza delle scritture ma non la scala.

### 12.7 Interventi, per compatibilità con il vincolo

| Intervento | Causa | Comportamento | Compatibile con as-is (lettura «comportamento») | Proponibile a monte |
|---|---|---|---|---|
| Snapshot incrementale o raggruppato nel tempo | 4 | Invariato | Sì | Sì |
| Un solo scanner periodico | 4 | Invariato | Sì | Sì |
| Invalidazione per percorso al posto di `dataVersion` (DC-16) | 3 | Invariato | Sì | Sì |
| Lettura in blocco dei metadati delle pagine (un comando Rust, una chiamata IPC) | 3 | Invariato | Sì | Sì |
| Liste virtualizzate | 3 | Invariato | Sì | Sì |
| Grafo incrementale (solo nodi toccati) | 1 | Invariato | Sì | Sì |
| Contesto di ingest per recupero (DC-14) | 2 | Cambia l'ingest | Solo come modalità configurabile spenta | Probabile (#511, #795) |
| Grafo e indice in Rust (petgraph, tantivy) | 1, 3 | Equivalente | No: sostituisce codice di nashsu | Difficile |
| Orchestrazione dell'ingest fuori dalla webview (DC-13) | #777 | Equivalente | No | Difficile; #777 aperta |

Tutti gli interventi «Sì» formano la Fase P (§8).

## 13. Architettura alternativa: vincolo as-is rilassato (variante B di DC-12)

DESIGN PROPOSAL. Vale solo se DC-12 adotta la variante B.

### 13.1 Regola

- **Resta vincolante** l'inventario di §6: tutto quello che l'utente fa oggi continua a funzionare.
- **Diventa libera** l'implementazione: moduli interni spostati, riscritti o sostituiti.
- **Non regressione:** checklist dell'inventario, test di scenario, misure 0b (§6, punto 4).

### 13.2 Architettura di arrivo

```
┌──────────── Webview (TypeScript): solo UI ────────────┐
│ React: editor, grafo, liste virtualizzate,            │
│ Activity Panel, impostazioni                           │
│ Store: proiezione dell'indice, aggiornata dagli eventi │
└──────────────┬─────────────────────▲───────────────────┘
       comandi │                     │ eventi (progressi, pagine cambiate,
               ▼                     │ grafo già calcolato)
┌──────────── Backend Rust: unico processo ──────────────┐
│ Orchestrazione ingest + coda   (spostata dalla webview)│
│ Client LLM unico               (oggi duplicato, N25)   │
│ WikiStore: UNICO punto di scrittura                    │
│   valida → scrive → registra → commit_paths            │
│ Moduli di geronimo-iia: JSON Schema, tantivy,          │
│   petgraph, git                                        │
│ Indice e grafo incrementali                            │
│ Un solo scanner + snapshot incrementale                │
└──────────────▲─────────────────────────────────────────┘
               │ API HTTP / MCP / agente (scritture e ingest)
```

| Intervento | Issue o causa risolta |
|---|---|
| Contesto di ingest per recupero (DC-14); `index.md` e `overview.md` diventano pagine derivate, non input del prompt | Causa 2; #511, #706 |
| Grafo calcolato in Rust e aggiornato solo per le pagine cambiate; la UI riceve i dati pronti, anche a pagine | Causa 1; #604, #647, #714, #732, #763 |
| Un solo scanner con snapshot incrementale (per esempio SQLite o registro a sola aggiunta) | Causa 4; #524, #810, #812 |
| Unico punto di scrittura in Rust, usato da comandi Tauri, API e agente | RR-11; transazioni senza buchi |
| Orchestrazione fuori dalla webview | #777; ingest avviabile da API e MCP (N27) |
| Indice delle pagine in Rust con proiezione nello store (DC-16) | Causa 3 |

### 13.3 geronimo-iia come libreria

Nella variante B DC-02 si inverte: un solo processo e un solo scrittore, nessun trasporto HTTP verso il motore. La licenza MIT/Apache permette di copiare solo i moduli che servono, evitando rmcp, axum e clap (G2). Serve allineare la toolchain: nashsu è su Rust 1.88 e edition 2021, geronimo-iia su 1.95 e 2024 (G3, N16).

### 13.4 Linguaggio dell'orchestrazione (DC-13)

| Opzione | Pro | Contro |
|---|---|---|
| Port in Rust | Un solo client LLM; ingest senza interfaccia; nessun runtime in più | Riscrittura più grande; test da rifare |
| Sidecar Node con il codice TypeScript attuale | Riusa codice e test | Un runtime Node in più nel pacchetto; i client LLM restano due |
| Web Worker nella webview | Cambiamento più piccolo | Toglie il blocco della UI ma l'ingest resta legato alla finestra e non è avviabile da API e MCP |

Proposta: prima disaccoppiare `ingest.ts` dagli store (N4) tramite interfacce per storage, LLM ed eventi di avanzamento, restando in TypeScript e con i test validi; poi portare in Rust un pezzo alla volta, cominciando dalle parti deterministiche (coda, cache, guardia dei percorsi, scritture), con i test di scenario come riferimento.

### 13.5 Piano della variante B

| Fase | Contenuto | Criterio di uscita |
|---|---|---|
| 0 + 0b | Come in §8 | Baseline dei test e baseline numerica |
| P | Come in §8, proposta a monte (DC-15) | CPU a riposo vicina a zero con 2.000 pagine |
| B2 | Unico punto di scrittura in Rust; moduli di geronimo-iia (schema, Git con `commit_paths`) | Ogni scrittura, comprese API e agente, è registrata e committata |
| B3 | Contesto di ingest per recupero (tantivy + LanceDB) | Token per ingest costanti al crescere della wiki; meno pagine doppie (RR-15) |
| B4 | Grafo e indice in Rust, incrementali | Apertura del grafo sotto una soglia da fissare con 5.000 pagine |
| B5 | Disaccoppiamento di `ingest.ts`, poi port in Rust; transazione `strict` | Ingest completo avviabile da API e MCP senza la finestra aperta |

### 13.6 Costi

- **Aggiornamenti di nashsu:** con l'ingest spostato in Rust non si possono più fondere i rami periodicamente (DC-03); le funzionalità future vanno riportate a mano. È il costo maggiore.
- **Sforzo:** molto più alto della variante A: si ristruttura, non si integra.
- **Licenza:** invariata, GPL v3 (DC-07).

## 14. Decisioni tecniche escluse (rev. 3)

### 14.1 WASM come leva di prestazioni

**CONFIRMED DIRECTION** (dichiarata il 24/11/2026): WASM non si adotta per migliorare le prestazioni.

| Collo di bottiglia (§12) | WASM aiuterebbe? |
|---|---|
| Invalidazione globale e ricarica completa | No: è un problema di architettura |
| N chiamate IPC `readFile` in sequenza | No: il costo è nell'andata e ritorno verso Rust e nel disco |
| Liste non virtualizzate | No: WASM non tocca il DOM |
| Snapshot e scansioni | No: sono già in Rust nativo |
| Prompt e chiamate LLM | No |
| Calcoli del grafo e parsing Markdown | Poco: vedi sotto |

Motivi (STRONG INFERENCE salvo dove indicato):
- in Tauri il backend Rust nativo è a una chiamata IPC di distanza, ha thread e accesso diretto ai file;
- i dati nascono dal lato Rust: con WASM andrebbero serializzati verso JS e poi copiati nella memoria WASM;
- gli algoritmi pesano più delle costanti: #763 era una complessità quadratica, risolta con una mappa;
- il blocco della UI dipende dal thread, non dal linguaggio: WASM sul thread principale blocca come JS; il guadagno viene dai worker o da Rust;
- la CSP di `tauri.conf.json` è `default-src 'self'` senza `'wasm-unsafe-eval'` e l'app non imposta COOP/COEP: oggi la compilazione WASM sarebbe bloccata e i thread WASM (`SharedArrayBuffer`) non disponibili (VERIFIED FACT sulla configurazione);
- toolchain in più (wasm-bindgen, secondo target) e memoria lineare separata, in un renderer che nella #812 occupava già 1,7 GB.

**Condizioni per riaprire la decisione:** condivisione dello stesso codice Rust (parsing, ricerca, grafo) con l'estensione Chrome o con una versione web senza Tauri; oppure un punto caldo che deve restare nel frontend e che, dopo la Fase P, la misura 0b indica ancora come costoso.

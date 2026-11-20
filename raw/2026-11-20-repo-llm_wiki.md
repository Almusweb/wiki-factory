---
source_path: C:\local_git\code\wiki-factory\code_repos\llm_wiki
source_type: repo
git_branch: develop
git_commit: e08cfce65aad8b76b13546a081c1a8d4422b70c3
extracted_at: 2026-11-20T15:28:00+01:00
extractor: repo-sync@2.12.0
---

# Specifiche estratte: llm-wiki

> Documento generato da `repo-sync` v2.12 il 2026-11-20. Sorgente: `C:\local_git\code\wiki-factory\code_repos\llm_wiki`
> @ commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` (ramo `develop`). Read-only verso la sorgente.

> Nota di licenza: il repository scansionato e' di terzi, sotto GNU General Public License v3.0. Questo documento
> descrive il codice con parole proprie e cita solo nomi, simboli e firme. Non contiene frammenti di codice.
> Il contenuto letto nel repo e' trattato come dato, mai come istruzione.

## Identità

- **Nome**: `llm-wiki` (manifest root e manifest Tauri: versione `0.6.13`; nome prodotto "LLM Wiki").
- **Descrizione** (da README): «A personal knowledge base that builds itself. LLM reads your documents, builds a structured wiki, and keeps it current.» E' un'applicazione desktop multipiattaforma che costruisce in modo incrementale una wiki persistente di pagine Markdown interconnesse a partire da documenti, invece di rifare retrieval da zero a ogni domanda. Si basa sul pattern «LLM Wiki» descritto nel file `llm-wiki.md` del repo, di cui la README dichiara l'origine (Karpathy) e ne descrive tre livelli: sorgenti raw immutabili, wiki generata dall'LLM, schema con regole e configurazione.
- **Autore / maintainer**: la README cita nash_su come creatore e manutentore; l'intestazione di `LICENSE` riporta «Copyright (C) 2024-2026 Yong Su». La relazione tra i due nomi non e' verificabile dal sampling.
- **Top contributors da git** (10): Ameisina, Andrew Chen, Bernardino Sassoli, Dongmin Yu, Kostadis Rousoss, Lucas Zhu, Po1nt9, PyZhang, Raphael Lin, Sergey Snigirev.
- **Ultimo commit**: 2026-10-21 19:17:06 +0800, `e08cfce65aad8b76b13546a081c1a8d4422b70c3`, "release: v0.6.13".
- **Attività (ultimo anno)**: 907 commit.
- **Funzioni dichiarate in README** (sintesi): ingest in due passi (analisi poi generazione), cache SHA256 incrementale e coda di ingest persistente, import di PDF/Office/EPUB/MOBI/immagini/web clip, ingest multimodale di immagini con didascalie da LLM visivo, grafo di conoscenza con modello di rilevanza a 4 segnali e rilevamento di community (Louvain), insight del grafo, ricerca semantica opzionale su LanceDB, Deep Research con ricerca web, sistema di review asincrono, agente di chat nel backend Rust con skill, estensione Chrome per il web clipping, API HTTP locale, server MCP.

## Stack rilevato

Output di `stack-detector`, repo multi-stack con tre descriptor. Il repo non ha workspace npm ne' Cargo workspace.

### A. Frontend: TypeScript con React 19 (descriptor principale)

- language: `typescript`; framework: `react`; framework_version: `^19.0.0` (da `package.json`).
- secondary_libs: `vite@^8.0.0`, `tailwindcss@^4.2.2`, `zustand@^5.0.12`, `@milkdown/kit@^7.20.0`, `sigma@^3.0.2`, `graphology@^0.26.0`, `i18next@^26.0.3`, `react-i18next@^17.0.2`, `react-markdown@^10.1.0`, `mermaid@^11.14.0`, `katex@^0.16.45`, `@tauri-apps/api@^2.11.0`, `vitest@^4.1.4`, `fast-check@^4.7.0`.
- patterns_expected: hooks, strict_mode, concurrent_mode_compatible.
- ruleset_id: `typescript.react.v19`.
- confidence: **0.7** (medio). Evidenze: manifest 0.5; config 0.2 (`vite.config.ts`, `tsconfig*.json`, `components.json`). Gli import di React confermati nel campione sono 2 (`src/main.tsx`, `src/App.tsx`), sotto i 5 richiesti dal detector: nessun contributo dagli import.

### B. Backend desktop: Rust con Tauri 2

- language: `rust`; framework: `tauri` (non in lista del detector, riportato come `other`); framework_version: `2` (da `Cargo.toml`); edition 2021, `rust-version = 1.88`.
- secondary_libs: `lancedb@0.27.2`, `pdfium-render@0.9`, `tiny_http@0.12`, `reqwest@0.12`, `tokio@1`, `notify@8`, `docx-rs@0.4.20`, `calamine@0.34.0`, `epub@2.1.5`, `mobi@0.8`, `anydoc@0.1.6`, `office_oxide@=0.1.2`.
- patterns_expected: async (tokio), comandi Tauri, panic guard sui confini di comando.
- ruleset_id: `rust.other.v2`.
- confidence: **0.7**. Evidenze: manifest 0.5; config 0.2 (`tauri.conf.json`, `capabilities/default.json`, `tauri.*.conf.json`). Gli import di `tauri` nel campione compaiono in 2 file, sotto soglia.

### C. Server MCP: TypeScript su Node, nessun framework web

- language: `typescript`; framework: `none`; Node `>=20`.
- secondary_libs: `@modelcontextprotocol/sdk@^1.29.0`, `typescript@^5.7.3`.
- ruleset_id: `typescript.none.v1`.
- confidence: **0.7**. Evidenze: manifest 0.5; config 0.2 (`tsconfig.json`, presente in enumerazione). L'import dell'SDK MCP e' stato letto in 1 solo file.

## Struttura ad alto livello

File totali: 476 (esclusi `.git`, `node_modules`, `vendor`, `dist`, `build`, `target`). Albero a depth 2:

```
llm_wiki/
├── .github/            (4 file: workflow CI e build, script di packaging)
├── assets/             (9 file: immagini della documentazione)
├── extension/          (10 file: estensione Chrome Manifest V3)
├── mcp-server/         (11 file)
│   ├── src/
│   └── test/
├── plans/              (1 file: piano multimodale)
├── scripts/            (1 file: script Python di debug)
├── src/                (362 file: frontend)
│   ├── assets/ commands/ components/ hooks/ i18n/
│   └── lib/ stores/ test-helpers/ types/
├── src-tauri/          (61 file: backend Rust)
│   ├── capabilities/ icons/ pdfium/ src/
└── (radice, 17 file: README in 4 lingue, LICENSE, manifest, config Vite/TS, llm-wiki.md)
```

- Pattern di layout: **multi-package, con struttura a strati** (UI, logica di dominio in `lib/`, stato in `stores/`, comandi verso il backend, backend Rust con moduli `agent/` e `commands/`).
- `src/components/` e' suddiviso per area funzionale: chat, editor, graph, layout, lint, project, review, search, settings, sources, ui.
- `src-tauri/pdfium/` contiene librerie native precompilate per piu' piattaforme (circa 7 MB ciascuna): non aperte.
- Albero esteso a depth 3 nel companion `raw/images/2026-11-20-repo-llm_wiki-tree.md` (41 directory).
- README: `README.md` e le varianti `README_CN.md`, `README_JA.md`, `README_KO.md`.

## Entrypoint e moduli chiave

- **Entrypoint frontend**: `src/main.tsx`. Applica la classe di piattaforma (macOS), carica e applica il tema, osserva il tema di sistema, poi monta il componente `App` insieme a `AppDialogHost` in strict mode. Se l'avvio fallisce, mostra una schermata di errore con escape dell'HTML del messaggio.
- **`src/App.tsx`** (letto in parte, righe 1-80): al boot carica dal project store le configurazioni (provider LLM, embedding, MinerU, multimodale, lingua di output, preset, routing dei task, override per progetto, proxy, importazione schedulata, source watch, API, generale, zoom). Idrata gli store di chat, review e lint per progetto, avvia auto-save e clip watcher e mostra `WelcomeScreen` e `CreateProjectDialog`.
- **Entrypoint backend**: `src-tauri/src/main.rs` delega a `llm_wiki_lib::run()`.
- **`src-tauri/src/lib.rs`** (letto in parte, righe 1-200 e 480-793): costruisce il Tauri Builder con i plugin opener, dialog, store, autostart e http. Nel setup imposta l'hint della cartella risorse per pdfium, applica il proxy letto da `app-state.json`, registra gli stati di sessione e cancellazione dell'agente, avvia clip server e API server e poi la tray. Gestisce la chiusura finestra in tre modalita' (ask, minimize, exit) e applica su Linux due variabili d'ambiente di compatibilita' WebKit. Registra circa 75 comandi Tauri.
- **Moduli Rust** (da `mod.rs`): `agent` (cancel, context, events, permissions, provider, router, runtime, session, skills, tools, types, workspace) e `commands` (claude_cli, cli_resolver, codex_cli, ebook, external_search, extract_images, file_history, file_sync, fs, page_embedding, project, project_maintenance, search, vectorstore). Moduli di primo livello: `api_server`, `clip_server`, `cors`, `panic_guard`, `proxy`, `server_bind`, `tray`, `types`.
- Il modulo `agent` e' dichiarato nel suo commento come substrato condiviso tra UI desktop, API HTTP locale e MCP, per evitare che i tre comportamenti divergano.
- **Nuovi moduli letti**: `server_bind.rs` (risoluzione dell'host di ascolto), `cors.rs` (origini ammesse e header CORS), `agent/permissions.rs` (capability e policy), `agent/router.rs` (classificazione dell'intento).
- **Moduli core, stima da fan-in** (segnale debole, derivato dai soli import dei 30 file campionati): `@/stores/wiki-store` (3 file), `@/commands/fs` (3), `@/lib/frontmatter` (2); lato Rust, `agent::types` richiamato da `router.rs` e `lib.rs`. La stima va presa con cautela.
- File grandi non aperti (oltre 50 KB): `src-tauri/src/agent/runtime.rs` (225 KB), `src-tauri/src/api_server.rs` (142 KB), `src-tauri/src/agent/tools.rs` (139 KB), `src-tauri/src/commands/fs.rs` (130 KB), `src/lib/ingest.ts` (161 KB, letto solo l'inizio: righe 1-70, import e costanti sui budget di token e di chunk).

## API surface (se rilevata)

### Comandi Tauri (frontend verso backend)

Circa 75 comandi registrati in `lib.rs`, per famiglie: file system e cronologia file; progetto e manutenzione (esportazione e importazione archivio, ricostruzione dell'indice); ricerca ed embedding; vector store su LanceDB; spawn e kill dei CLI `claude` e `codex`; estrazione di immagini da PDF e Office; sincronizzazione e watcher dei file; agente (avvio turno, streaming, cancellazione, sessioni, skill); proxy e comportamento di chiusura.

### API HTTP locale

Dichiarata nella README: `http://127.0.0.1:19828`, prefisso `/api/v1`, protetta da token. Endpoint elencati: health (senza auth), projects, files e files/content, reviews (lettura, aggiornamento singolo, risoluzione in blocco), search ibrida (parole chiave piu' vettori), chat (anche in streaming SSE), graph (con filtri e paginazione), sources/rescan, pages/embed. Il contratto reale sta in `src-tauri/src/api_server.rs` (non letto) e nel client `mcp-server/src/api-client.ts` (non letto). Non c'e' un file OpenAPI. Un secondo server locale, il clip server, ascolta sulla porta 19827 (README ed estensione); la sua implementazione e' in `clip_server.rs`, non letto. Le costanti della porta e dell'URL di health lato frontend sono in `src/lib/api-server-constants.ts`.

### Server MCP

`mcp-server/src/index.ts` (letto per intero) usa trasporto stdio e inoltra ogni chiamata all'API locale; configurazione tramite `LLM_WIKI_API_TOKEN` e `LLM_WIKI_API_BASE_URL`. **Il README di `mcp-server` dichiara 10 strumenti, il codice ne registra 12.** Elenco dal codice:

1. `llm_wiki_status` (stato e progetto corrente).
2. `llm_wiki_projects`.
3. `llm_wiki_set_project` (vincola la sessione MCP a un progetto).
4. `llm_wiki_files`.
5. `llm_wiki_read_file` (limite di 120 KB sul testo restituito).
6. `llm_wiki_reviews`.
7. `llm_wiki_search`.
8. `llm_wiki_chat` (modalita' `fast`, `standard`, `deep`, `local_first`).
9. `llm_wiki_graph`.
10. `llm_wiki_rescan_sources`.
11. `llm_wiki_embed_page` (non documentato nel README di `mcp-server`).
12. `llm_wiki_write_page` (non documentato nel README di `mcp-server`).

`llm_wiki_write_page` crea o sovrascrive una pagina Markdown sotto `wiki/`. Parametri: percorso, contenuto, flag di sovrascrittura (default falso). Vincoli nel codice: percorso canonico sotto `wiki/` con estensione `.md`, senza segmenti nascosti o `..`, percorso massimo 4096 byte, contenuto massimo 2 MiB. La descrizione dello strumento dichiara che il successo viene restituito solo dopo la verifica byte per byte della scrittura.

Ogni strumento tranne `llm_wiki_status` controlla prima il flag `mcpEnabled` restituito dall'API di salute e, se e' disabilitato, risponde con un errore esplicito. Dopo `llm_wiki_set_project`, gli altri strumenti non possono uscire dal progetto vincolato e ogni risposta riporta un marcatore `activeProject`.

### Superficie di sicurezza

- **Bind** (`src-tauri/src/server_bind.rs`, letto per intero):
  - L'host di default e' `127.0.0.1`.
  - Si esce dal loopback in due casi: la variabile d'ambiente `LLM_WIKI_BIND_HOST` con un host valido, oppure il flag `apiConfig.allowLanAccess` vero in `app-state.json`; nel secondo caso l'host diventa `0.0.0.0`. Se entrambi sono presenti vince la variabile d'ambiente.
  - L'host viene sanitizzato: sono ammessi solo caratteri alfanumerici e i simboli `.`, `-`, `_`, `:`, `[`, `]`; valori vuoti o con altri caratteri sono scartati. Gli IPv6 senza parentesi sono racchiusi tra parentesi quadre.
  - I test del file coprono host LAN comuni, il rifiuto di input con percorso o separatori di comando e la lettura del flag.
- **CORS** (`src-tauri/src/cors.rs`, letto per intero):
  - Metodi dichiarati: GET, POST, PATCH, DELETE, OPTIONS. Gli header ammessi li passa il chiamante.
  - Origini ammesse: qualsiasi `chrome-extension://*` e `moz-extension://*` (qualunque identificativo di estensione), `http://localhost`, `http://127.0.0.1` e `http://[::1]` con o senza porta, `tauri://localhost`, `http://tauri.localhost` e `https://tauri.localhost`. Il confronto e' esatto (i test escludono sottodomini ingannevoli, `https://localhost`, maiuscole e domini esterni).
  - Per un'origine ammessa il server riflette l'origine, aggiunge `Vary: Origin` e l'header di accesso alla rete privata; per le altre non emette l'header di origine ammessa.
  - Il file non mostra se una richiesta da origine non ammessa venga poi rifiutata: CORS non lo impone da solo ai client non browser.
- **Permessi dell'agente** (`src-tauri/src/agent/permissions.rs`, letto per intero):
  - 9 capability: `ReadProject`, `ReadSource`, `SearchWiki`, `SearchWeb`, `SearchAnyTxt`, `WriteWiki`, `RunDeepResearch`, `Network`, `Process`.
  - La policy `api_default` ne consente 8 (tutte tranne `RunDeepResearch`), incluse scrittura wiki, rete e `Process`.
  - Il commento nel file dice che `Process` resta inerte finche' la richiesta non porta un comando shell esatto approvato separatamente, e che quell'elenco non va popolato con output del modello o dati di conversazione persistiti.
  - Il file implementa solo il gate sulle capability: il controllo del comando approvato non e' in questo file.
- **Router** (`src-tauri/src/agent/router.rs`, letto per intero):
  - 7 intenti: `NeedsInternalSearch`, `NeedsExternalSearch`, `NeedsRawSourceSearch`, `NeedsGraph`, `NeedsWrite`, `SimpleConversational`, `Ambiguous`.
  - `route_query` riceve messaggio, modalita' e opzioni degli strumenti e restituisce una `RouterDecision` (intento, hint web e anytxt, inclusione delle sorgenti, motivazione testuale).
  - La classificazione e' per parole chiave in inglese e cinese, con priorita': scrittura, grafo, sorgenti raw, web, conversazionale, altrimenti ambiguo. Il confronto e' per sottostringa, non per parola intera.
  - Il router non attiva mai la ricerca wiki da solo (`should_search_wiki` e' sempre falso): la scelta degli strumenti spetta al planner del modello. `NeedsInternalSearch` non e' prodotto da `route_query`.
- **Estensione Chrome** (`extension/manifest.json`): permessi `activeTab`, `scripting`, `storage`; host `127.0.0.1:19827` e `localhost:19827`; host opzionali http e https ovunque; comando da tastiera per il clip della pagina.
- **Tauri**: CSP con `connect-src` verso http e https; la capability `http:default` ammette host http e https arbitrari; schema di asset con ambito `**`. Riportato come fatto, senza giudizio.

## Schema dati (se rilevato)

Nessun database relazionale e nessun file `.proto`. I dati vivono su file.

- Layout di un progetto wiki (README): `purpose.md`, `schema.md`, `raw/sources`, `raw/assets`, `wiki/` con `index.md`, `log.md`, `overview.md` e le cartelle entities, concepts, sources, queries, synthesis, comparisons; poi `.obsidian/` e `.llm-wiki/` (configurazione, cronologia chat, review, `project.json` con l'identificativo UUID del progetto).
- Tipi TypeScript condivisi (`src/types/wiki.ts`): `WikiProject` (id, name, path), `FileNode` (con figli opzionali) e `WikiPage` (percorso, contenuto, frontmatter).
- Indice vettoriale su LanceDB con chunk. `plans/multimodal-images.md` descrive lo schema come solo testo, con un campo per il testo del chunk; il piano ha stato «Spec, not started» ed e' quindi da verificare sul codice.
- Instradamento dei tipi di pagina letto dallo `schema.md` del progetto (`src/lib/wiki-schema.ts`, letto in parte): la funzione `parseWikiSchemaRouting` estrae da una tabella nella sezione «Page types» la corrispondenza tipo-directory, scartando directory non sicure.

## Dipendenze esterne

**Frontend** (`package.json`, versione `0.6.13`; circa 40 dipendenze dirette). Principali: `react@^19.0.0`, `react-dom@^19.0.0`, `@tauri-apps/api@^2.11.0` e plugin autostart, dialog, http, opener, store, `@milkdown/kit@^7.20.0`, `@milkdown/react@^7.20.0`, `@milkdown/plugin-math@^7.5.9`, `@react-sigma/core@^5.0.6`, `sigma@^3.0.2`, `graphology@^0.26.0`, `graphology-communities-louvain@^2.0.2`, `graphology-layout-forceatlas2@^0.10.1`, `zustand@^5.0.12`, `i18next@^26.0.3`, `react-i18next@^17.0.2`, `react-markdown@^10.1.0`, `remark-gfm@^4.0.1`, `remark-math@^6.0.0`, `rehype-katex@^7.0.1`, `katex@^0.16.45`, `mermaid@^11.14.0`, `pdfjs-dist@^5.7.284`, `jszip@^3.10.1`, `js-yaml@^4.1.1`, `tailwindcss@^4.2.2`, `@tailwindcss/vite@^4.2.2`, `shadcn@^4.1.2`, `lucide-react@^1.7.0`. Dev: `vite@^8.0.0`, `@vitejs/plugin-react@^6.0.1`, `typescript@^5.7.3`, `vitest@^4.1.4`, `fast-check@^4.7.0`, `@tauri-apps/cli@^2.11.1`.

**Backend** (`src-tauri/Cargo.toml`; circa 30 crate). `tauri@2` (feature protocol-asset e tray-icon), `tauri-plugin-*` (opener, autostart 2.5.1, dialog 2.7.1, store 2.4.2, http 2 con `unsafe-headers`), `serde@1`, `serde_json@1`, `chrono@0.4`, `pdfium-render@0.9`, `reqwest@0.12` (rustls, stream), `tiny_http@0.12`, `zip@2`, `calamine@0.34.0`, `docx-rs@0.4.20`, `office_oxide@=0.1.2` (versione bloccata), `anydoc@0.1.6`, `lancedb@0.27.2`, `arrow-array@57`, `arrow-schema@57`, `futures@0.3`, `tokio@1`, `which@7`, `uuid@1`, `image@0.25`, `base64@0.22`, `sha2@0.10`, `md-5@0.10`, `notify@8`, `walkdir@2`, `epub@2.1.5`, `mobi@0.8`, `html2text@0.17.1`. Profilo release con LTO, `opt-level = "s"`, `panic = "unwind"`, `strip`.

**Server MCP**: `@modelcontextprotocol/sdk@^1.29.0` (dev: `typescript@^5.7.3`, `@types/node@^20`); versione del package `0.4.26`; licenza dichiarata nel `package.json`: MIT.

**Servizi esterni** (tutti opzionali e configurati dall'utente, da README e preset): provider LLM (OpenAI, Anthropic, Google, Azure, Ollama, MiniMax, endpoint custom, `claude-code` e `codex-cli` locali), endpoint di embedding compatibili con OpenAI, ricerca web (Tavily, SerpApi, SearXNG), Firecrawl, MinerU (cloud o locale), AnyTXT.

**Toolchain**: Node 20 o superiore, Rust 1.88 o superiore, `protoc` per la build.

## Vincoli normativi / Standard

- Licenza, verbatim dalla README: «This project is licensed under the **GNU General Public License v3.0**». `LICENSE` (righe 1-12 lette) conferma «Version 3, 29 June 2007».
- **Anomalia da verificare**: `mcp-server/package.json` dichiara `"license": "MIT"`, diversa dalla GPL v3 della radice.
- Protocolli citati, senza essere vincoli normativi: Model Context Protocol; Chrome Manifest V3 (README); client compatibili OpenAI per gli embedding.
- Nessuna menzione di SPID, OIDC, OAuth2, SAML, eIDAS, FHIR, GDPR, HIPAA, PCI-DSS, HL7, ISO 27001 o RFC numerati nei testi letti.

## Documenti correlati nel repo

Elenco di percorsi, non inglobati:

- `README.md`, `README_CN.md`, `README_JA.md`, `README_KO.md`
- `llm-wiki.md` (idea file del pattern; letto in parte, righe 1-40)
- `mcp-server/README.md`
- `plans/multimodal-images.md`
- `LICENSE`
- `src/lib/changelog.ts` (changelog incorporato nel codice, 54 KB, non letto)
- `.github/workflows/ci.yml`, `.github/workflows/build.yml` (il secondo non letto)

Non esistono cartelle `docs/` ne' `ADR/` nell'enumerazione. Il `.gitignore` del repo esclude `docs/` e `AGENTS.md` con il commento «Internal docs (not shipped)», e anche i file `.env`.

## Test coverage rilevato

- Framework: `vitest@^4.1.4` con `fast-check@^4.7.0` per i test di proprieta'; il server MCP usa invece il runner nativo di Node.
- Script in `package.json`: `test:mocks` (esclude i test con LLM reale e quelli di `mcp-server`), `test:llm` (test con LLM reale, senza parallelismo), `mcp:test`.
- Suite: molti file `*.test.ts` accanto ai sorgenti in `src/lib`, `src/stores`, `src/components`, `src/commands`; varianti `.property.`, `.scenarios.`, `.race.`, `.integration.` e `.real-llm.`; cartella `src/lib/__tests__/`; `mcp-server/test/` (3 file); helper e scenari in `src/test-helpers/`.
- Test unitari incorporati nei moduli Rust (`#[cfg(test)]`): visti in `server_bind.rs`, `cors.rs`, `permissions.rs`, `router.rs`.
- `vite.config.ts` registra un file di setup che carica un file di ambiente per i test con LLM reale; tale file di ambiente non e' nel repo.
- Nessuna configurazione di coverage tool rilevata.
- CI (`ci.yml`): su macOS, Ubuntu e Windows esegue build del frontend e build Rust; **non esegue i test**. Il workflow `build.yml` non e' stato letto.

## Gap evidenti

> Quello che il sampling non ha potuto chiarire. Input per `wiki-keeper` durante l'ingest L1 verso L2.

- Logica di business non letta: `ingest.ts` oltre la riga 70, `agent/runtime.rs`, `agent/tools.rs`, `api_server.rs`, `commands/fs.rs` (tutti oltre 50 KB), righe 201-479 di `lib.rs`.
- Contratto esatto dell'API HTTP: la README e' l'unica fonte per gli endpoint; `api_server.rs` e `api-client.ts` non letti.
- Dove vengono usati `server_bind` e `cors` e quale autenticazione si applichi quando il server ascolta fuori dal loopback. La README descrive l'API come `127.0.0.1`-only e protetta da token, ma il codice prevede l'ascolto su LAN opzionale: documentazione e comportamento divergono, oppure ci sono vincoli aggiuntivi non letti.
- Il README di `mcp-server` elenca 10 strumenti e il codice ne registra 12; il suo paragrafo di sicurezza parla solo di letture e non cita la scrittura di pagine. Gli endpoint HTTP corrispondenti a scrittura pagina ed embedding non sono verificati (l'elenco endpoint della README non cita una scrittura pagina).
- Il punto in cui viene applicata l'approvazione dei comandi shell (README: «external shell commands still require explicit approval») non e' verificato.
- Il fan-in e' una stima debole su 30 file.
- La README dice «English + Chinese» per l'i18n, ma esistono `en.json`, `it.json`, `ru.json`, `zh.json` in `src/i18n/`.
- Autore: nash_su (README) contro Yong Su (LICENSE).
- Licenza di `mcp-server/package.json` (MIT) contro GPL v3 alla radice.
- Stato di `plans/multimodal-images.md` («Spec, not started») contro la README, che descrive come gia' presente l'ingest multimodale.
- La CI non esegue i test; `build.yml` non letto.
- Requisiti funzionali e regole di dominio: derivabili solo dalla README, non confermati dal codice letto.
- Nessuna scansione dei sorgenti non aperti alla ricerca di credenziali hardcoded (vedi Note di estrazione).

## Note di estrazione

- File sampled: 30/476 (cap di 30 file, 50 KB per file).
- Secret redacted: 0. Nessun file `.env*` e nessuna cartella `secrets/` trovati; nel README di `mcp-server` compare solo un segnaposto per il token, non un valore. Limite: senza strumento di ricerca testuale non e' stata fatta una scansione dei sorgenti non aperti, quindi lo zero vale per i 30 file letti e per la ricerca dei nomi file.
- Estrazione: **partial**. Motivo: cinque file ad alto valore (`agent/runtime.rs`, `agent/tools.rs`, `api_server.rs`, `commands/fs.rs` e `ingest.ts` oltre la riga 70) superano i 50 KB e sono descritti solo tramite nomi e file vicini; `lib.rs` e' letto in parte; 446 file non sono stati campionati; non c'e' stata scansione dei sorgenti alla ricerca di credenziali hardcoded.
- Istruzioni trovate nei file letti: nessuna ostile. Sono presenti comandi di installazione e consigli rivolti agli utenti umani (README, `mcp-server/README.md`), un invito nel file `llm-wiki.md` a incollare il documento a un agente, e note per i contributor nei commenti Rust: nessuno e' stato eseguito.

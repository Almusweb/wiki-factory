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

## Aggiornamenti (v2026-11-20)

> Seconda estrazione, mirata al **layer di persistenza**, sullo stesso commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` (ramo `develop`). Aggiunta in coda al documento: le sezioni precedenti non sono state modificate. Fine: decidere come documentare gli schemi dei dati (layer `db`).

### Premessa e perimetro

- **Licenza.** Il repository e' di terzi, sotto GNU GPL v3. Questa sezione riporta solo nomi di file, simboli, campi e firme, descritti con parole proprie. Nessun frammento di codice. Il contenuto letto e' trattato come dato.
- **Campione di questo giro: 21 file**, tutti sotto 50.000 byte (circa 357 KB in totale).
  - Rust: `src-tauri/src/commands/vectorstore.rs`, `page_embedding.rs`, `file_history.rs`, `project.rs`, `project_maintenance.rs`, `src-tauri/src/agent/session.rs`.
  - TypeScript: `src/lib/persist.ts`, `project-store.ts`, `project-identity.ts`, `ingest-cache.ts`, `dedup-storage.ts`, `embedding.ts`, `lint-config.ts`, `ingest-queue.ts`, `source-watch-config.ts`, `scheduled-import.ts`, `dedup_embedding.ts`, `reset-project-state.ts`; `src/stores/chat-store.ts`, `review-store.ts`; `src/types/wiki.ts`.
- **`files_sampled` cumulativo: 50**, cioe' i file distinti letti per il documento: i 30 della prima estrazione piu' i 20 nuovi. `src/types/wiki.ts` era gia' stato letto e non e' contato due volte; e' l'unico overlap che il documento precedente permette di verificare. Se il campione precedente contenesse altri file di questo giro, il valore reale sarebbe leggermente inferiore.
- **Non letto per limite di dimensione**: `src-tauri/src/commands/file_sync.rs` (70 KB). Descritto solo dal nome e dal percorso (vedi `### Gap`).
- Convenzioni: tutti gli archivi in `<progetto>/.llm-wiki/` sono per progetto. "TS" indica il frontend, "RS" il backend Rust.
- Lo stack e' invariato rispetto alla sezione `## Stack rilevato`. Librerie rilevanti per la persistenza (da `Cargo.toml`, gia' elencate sopra): `lancedb@0.27.2`, `arrow-array@57`, `arrow-schema@57`, `tauri-plugin-store@2.4.2`, `serde_json`, `uuid`, `sha2`.

### Inventario degli archivi

Dove non e' dichiarata una versione di formato scrivo "nessuna". Il file di dati mancante o illeggibile viene letto quasi ovunque in modo silenzioso (valore vuoto o di default).

| Archivio | Posizione | Scrive / legge | Schema o campi | Versione | Corruzione |
|---|---|---|---|---|---|
| Tabella LanceDB v2 `wiki_chunks_v2` | `.llm-wiki/lancedb` | RS scrive e legge (`vectorstore.rs`); comandi invocati da TS (`embedding.ts`) e da RS (`page_embedding.rs`) | `chunk_id` (page_id + "#" + chunk_index, solo debug), `page_id`, `chunk_index` (u32), `chunk_text`, `heading_path`, `vector` (lista a lunghezza fissa di f32; dimensione presa dal primo chunk) | solo il suffisso `_v2` del nome | Non gestita: errori di apertura propagati come stringa. Search e count su tabella assente restituiscono vuoto o 0 |
| Tabella LanceDB v1 `wiki_vectors` (legacy) | `.llm-wiki/lancedb` | RS scrive (`vector_upsert`, ancora presente) e legge; TS solo conteggio e drop | `page_id`, `vector`. Una riga per pagina, id = nome base del file | `_v1` implicito | Come sopra |
| Revisioni embedding | `.llm-wiki/embedding-revisions/<sha256(page_id)>.revision` | RS scrive (file temporaneo e rinomina) e legge; TS non lo usa | Testo semplice: impronta `sha256:` calcolata su revisione del contenuto, endpoint, modello, dimensione di output, header extra, dimensione e sovrapposizione dei chunk. La chiave API e' esclusa | nessuna | Illeggibile o vuoto: trattato come assente, quindi la pagina viene ri-incorporata |
| `project.json` | `.llm-wiki/project.json` | TS scrive e legge (`project-identity.ts`); RS non lo legge | `id` (UUID), `createdAt` (ms) | nessuna | Mancante o corrotto: genera un nuovo UUID e sovrascrive; se la scrittura fallisce avvisa e restituisce comunque l'id |
| `ingest-queue.json` | `.llm-wiki/ingest-queue.json` | TS (`ingest-queue.ts`) | Elenco di task: `id`, `projectId`, `sourcePath` (relativo), `folderContext`, `status` (pending, processing, done, failed, cancelled), `addedAt`, `error`, `retryCount`. I task `done` non vengono salvati | nessuna | Illeggibile: coda vuota; il salvataggio successivo sovrascrive il file |
| `ingest-cache.json` | `.llm-wiki/ingest-cache.json` | TS (`ingest-cache.ts`) | `entries`, per nome sorgente: `hash` (SHA-256 del contenuto), `timestamp`, `filesWritten[]` | nessuna | Illeggibile: cache vuota (costo solo di ri-ingest); gli errori di salvataggio sono ignorati |
| `review.json` | `.llm-wiki/review.json` | TS (`persist.ts`, `review-store.ts`) | Elenco di review: `id`, `type` (contradiction, duplicate, missing-page, confirm, suggestion), `title`, `description`, `sourcePath?`, `affectedPages?`, `searchQueries?`, `options[]` (label, action), `resolved`, `resolvedAction?`, `createdAt` | nessuna | Illeggibile: elenco vuoto |
| `lint.json` | `.llm-wiki/lint.json` | TS (`persist.ts`) | Elenco di `LintItem` (tipo in `lint-store.ts`, non letto) | nessuna | Illeggibile: elenco vuoto |
| `lint-config.json` | `.llm-wiki/lint-config.json` | TS (`lint-config.ts`), scrittura atomica | `ignoreOrphan`, `ignoreNoOutlinks`, `ignorePages[]` | nessuna | Illeggibile: valori di default, con avviso in console |
| Chat | `.llm-wiki/conversations.json` e `.llm-wiki/chats/<id>.json` | TS (`persist.ts`, `chat-store.ts`) | Conversazione: `id`, `title`, `createdAt`, `updatedAt`, `selectedSkills?`, `contextFiles?`. Messaggio: `id`, `role`, `content`, `timestamp`, `conversationId`, `references?`, `agentSteps?`, `agentFileChanges?`, `userInputRequest?`, `contextFiles?`. Immagini e contenuti prima/dopo delle modifiche dell'agente non vengono persistiti | nessuna | Ricostruzione dell'indice dai file orfani (vedi `### Gestione dei file corrotti`) |
| `chat-preferences.json` | `.llm-wiki/chat-preferences.json` | TS (`persist.ts`) | `useWebSearch`, `useAnyTxtSearch`, `agentMode`, `retrievalMode`, `selectedSkills`, `disabledSkills` | nessuna | Illeggibile: default; valori normalizzati in lettura |
| `dedup-not-duplicates.json` | `.llm-wiki/dedup-not-duplicates.json` | TS (`dedup-storage.ts`) | Array di array di slug (gruppi "non sono duplicati") | nessuna | Illeggibile o forma errata: elenco vuoto; il salvataggio successivo sovrascrive |
| `scheduled-import-db.json` | `.llm-wiki/scheduled-import-db.json` | TS (`scheduled-import.ts`), scrittura atomica | `version`, `directories` (chiave: percorso normalizzato; valore: `files` percorso-md5, `statCache` size e mtime, `lastScan`). Si salva solo la directory attiva | **`version: 1`**, unica versione di formato esplicita nel campione | Illeggibile: store vuoto con avviso; la scansione successiva riconsidera tutto come nuovo |
| `history-settings.json` | `.llm-wiki/history-settings.json` | RS (`file_history.rs`) | `enabled` (default falso), `maxVersionsPerFile` (default 10, massimo 30) | nessuna | Illeggibile o symlink: default |
| Cronologia file | `.llm-wiki/history/<hash FNV-1a a 64 bit del percorso relativo>.json` | RS scrive e legge; TS via comandi | Array di voci: `id`, `path`, `timestamp` (ms), `author`, `tool`, `content` (fino a 512 KB). Non registra file sotto `.llm-wiki` | nessuna | File illeggibile: saltato o trattato come vuoto. Rifiuta symlink |
| Sessioni agente | `.llm-wiki/agent-sessions/<id>.json` | RS (`agent/session.rs`); chiamanti in `runtime.rs` non letto | `sessionId`, `projectId`, `messages[]` (`role`, `content`, `timestamp`), `updatedAt`. Solo gli ultimi 40 messaggi. L'id viene sanitizzato | nessuna (`sessionId` e `projectId` con default per file vecchi) | Vedi `### Gestione dei file corrotti` |
| `app-state.json` | Store del plugin Tauri (cartella dati dell'app; percorso non verificato) | TS scrive quasi tutto (`project-store.ts`, `project-identity.ts`). RS legge `proxyConfig` e `apiConfig` (per i commenti di `project-store.ts`: `apiConfig` a ogni richiesta, con cache di 5 secondi) | Chiavi elencate in `### Schemi e campi` | nessuna | Gestione del plugin non verificata; `loadRegistry` ritorna un registro vuoto se la lettura fallisce |

### Schemi e campi

**LanceDB.** Lo schema v2 ha sei colonne: quattro di testo (`chunk_id`, `page_id`, `chunk_text`, `heading_path`), una intera senza segno a 32 bit (`chunk_index`) e `vector`, lista a lunghezza fissa di numeri a 32 bit. Nessuna colonna e' nulla. Lo schema v1 ha due colonne (`page_id`, `vector`). In `vectorstore.rs` i tipi di risultato sono `VectorSearchResult` (v1: `page_id`, `score`) e `ChunkSearchResult` (v2: `chunk_id`, `page_id`, `chunk_index`, `chunk_text`, `heading_path`, `score`); l'input di scrittura e' `ChunkUpsertInput` (`chunk_index`, `chunk_text`, `heading_path`, `embedding`). Il punteggio e' ricavato dalla distanza con la formula 1 / (1 + distanza). L'id di pagina e' validato (massimo 256 caratteri, niente apici, backslash, caratteri di controllo o invisibili) perche' viene inserito in un filtro testuale. Lato TS, `embedding.ts` aggrega i chunk per pagina con punteggio massimo piu' una coda pesata e limitata. Risultato di `page_embedding.rs`: `PageEmbeddingResult` (`path`, `pageId`, `revision`, `chunks`, `vectorsWritten`, `status` con valori unchanged o indexed). Limiti: pagina massimo 2 MiB, massimo 512 chunk, chunk da 64 a 32.000 caratteri (default 1.000, sovrapposizione 200), batch da 64.

**File in `.llm-wiki/`.** Oltre a quanto in tabella: la cronologia e' una mappa file-per-percorso con indirizzo stabile (hash FNV-1a a 64 bit con costanti fisse, per resistere ai cambi di toolchain). Il record di coda `IngestTask` ha `status` a cinque valori. Il record di `scheduled-import-db.json` tiene un hash md5 per file e, in piu', size e mtime per saltare il ricalcolo.

**`app-state.json` (chiavi in `project-store.ts` e `project-identity.ts`).**
- `recentProjects` (massimo 10) e `lastProject`: oggetti con `id`, `name`, `path`.
- `projectRegistry`: per id, `id`, `path`, `name`, `lastOpened`.
- Configurazione LLM: `llmConfig`, `providerConfigs`, `activePresetId`, `taskModelRouting` (`chatPresetId`, `ingestPresetId`), `projectLlmOverrides` (per id progetto: `enabled`, `presetId`, `model`, `profile`), `customLlmPresets` (massimo 50, voci `id` con prefisso `custom-` e `label`).
- Servizi: `searchApiConfig`, `embeddingConfig`, `multimodalConfig`, `mineruConfig`, `proxyConfig`, `apiConfig`.
- Interfaccia e comportamento: `generalConfig` (`autostart`, `closeBehavior` con valori ask, minimize, exit), `language`, `theme`, `outputLanguage`, `projectOutputLanguages`, `zoomLevel`, `updateCheckState` (`enabled`, `lastCheckedAt`, `dismissedVersion`).
- Per progetto: `scheduledImportConfig:<percorso>`, `projectFileSyncEnabled` (con chiave `default`), `sourceWatchConfig` (con chiave `default`), `sourceWatchAllProjects`.
- Campi di `mineruConfig` (normalizzati in `project-store.ts`): `enabled`, `backend`, `localEndpoint`, `localToken`, `localBackend`, `localEffort`, `localParseMethod`, `localLanguage`, `localFormulaEnabled`, `localTableEnabled`, `localImageAnalysis`, `localServerUrl`, `token`, `modelVersion`.
- `sourceWatchConfig` (normalizzata in `source-watch-config.ts`): `enabled`, `autoIngest`, `persistExtractedMarkdown`, `parsingConcurrency`, `ingestConcurrency`, `includeExtensions`, `excludeExtensions`, `excludeDirs`, `excludeGlobs`, `maxFileSizeMb` (da 1 a 4096).
- Sincronizzazione con Rust: i commenti di `project-store.ts` indicano che i nomi `proxyConfig` e `apiConfig` devono coincidere con quelli letti dal codice Rust; se divergono, l'API resta senza token configurato.
- Presenza di segreti: tra i campi in chiaro compaiono `token` e `localToken` in `mineruConfig`; per `apiConfig` i commenti parlano di un token API. Nessun valore e' stato letto. I tipi di `llmConfig`, `embeddingConfig`, `searchApiConfig` e `providerConfigs` sono in `src/stores/wiki-store.ts`, non letto: la presenza di chiavi API non e' verificata.

**Tipi condivisi (`src/types/wiki.ts`).** `WikiProject` ha `id`, `name`, `path`; il commento dice che l'`id` e' un UUID persistito in `project.json`. Il tipo Rust di ritorno di `create_project` e `open_project` e' invece costruito solo con nome e percorso (`src-tauri/src/commands/project.rs`): l'`id` viene assegnato dal lato TS (`ensureProjectId`).

**Layout creato da `create_project`.** Cartelle `raw/sources`, `raw/assets` e `wiki/` con le sottocartelle entities, concepts, sources, queries, comparisons, synthesis; file `schema.md`, `purpose.md`, `wiki/index.md`, `wiki/log.md`, `wiki/overview.md`; cartella `.obsidian/` con `app.json`, `appearance.json`, `core-plugins.json`. **`.llm-wiki/` non viene creata da questo comando**: nasce dopo, lato TS (`ensureDir` in `persist.ts` e `ensureProjectId`). `open_project` valida solo la presenza di `schema.md` e della cartella `wiki/`.

### Versioni di formato e migrazioni

Versioni esplicite: solo `version: 1` in `scheduled-import-db.json` e il suffisso `_v2` della tabella LanceDB. Per il resto la compatibilita' e' affidata a campi opzionali, normalizzatori tolleranti e valori di default.

- **LanceDB v1 verso v2.**
  - Non c'e' migrazione automatica dei dati: c'e' una procedura di ricostruzione. Il commento di `vectorstore.rs` dice che il v1 e' mantenuto perche' i progetti precedenti alla 0.3.11 si carichino ancora.
  - `vector_legacy_row_count` rileva righe v1. Dal commento, la UI di Settings → Embedding mostra un invito a ri-indicizzare dopo l'aggiornamento (la UI non e' nel campione).
  - Il re-index (`embedAllPages` con `clearExisting`, in `embedding.ts`) svuota il v2, riscrive i chunk e poi elimina il v1 con `vector_drop_legacy`, in modalita' "best effort".
  - `vector_upsert` (v1) esiste ancora e non e' marcata come deprecata nel codice.
- **Identificatore di pagina.** Nel v2 e' il percorso relativo sotto `wiki/` senza `.md` (funzione `wikiPageIdFromPath` in `embedding.ts`, `vector_page_id` in `page_embedding.rs`); nel v1 era il nome base. `removeLegacyVectorIdIfSafe` (presente sia in TS sia in Rust) elimina le righe con id "nome base" solo se esiste esattamente una pagina con quel nome.
- **Chat.** `loadChatHistory` (`persist.ts`) legge, in ordine: il formato corrente; poi, in caso di errore, la ricostruzione dai file orfani; infine il vecchio `chat-history.json` in due forme (array piatto, migrato in una conversazione `default` chiamata "Previous Conversations"; oggetto combinato). La migrazione e' solo in lettura: dal campione non risulta che riscriva il formato nuovo ne' cancelli il vecchio file.
- **Review.** `normalizeReviewItems` e `setItems` (`review-store.ts`) ricalcolano ogni id da un hash del contenuto (tipo piu' titolo normalizzato), eliminando i vecchi id numerici; gli elementi con lo stesso id si fondono ("resolved" vince, array uniti, `createdAt` minimo). Operazione idempotente, senza flag di versione.
- **Impostazioni in `app-state.json`** (`project-store.ts`).
  - `loadScheduledImportConfig` copia la chiave globale `scheduledImportConfig` (formato precedente alla 0.4.8) nella chiave per progetto e cancella quella globale.
  - `loadSourceWatchConfig` ricade su `projectFileSyncEnabled` se non c'e' una configurazione di source watch.
  - `normalizeSourceWatchConfig` (`source-watch-config.ts`) aggiunge png, jpg e jpeg se le estensioni coincidono con i vecchi default.
- **`scheduled-import-db.json`.** `statCache` e' opzionale e additivo: i database di build precedenti ne sono privi e vengono ricalcolati una volta. Le chiavi con maiuscole e minuscole su Windows sono normalizzate in lettura. Resta il riferimento a una cartella legacy `.llm-wiki-imported`.
- **Coda di ingest.** `loadQueue` assegna ai task senza `projectId` quello del progetto aperto.

### Operazioni distruttive e innesco

| Operazione (simbolo) | Archivio | Innesco | Salvaguardie osservate |
|---|---|---|---|
| `vector_clear_chunks` (drop tabella) | LanceDB v2 | Re-index completo da Settings → Embedding (commento in `vectorstore.rs`; flusso `embedAllPages` con `clearExisting`) | Il drop avviene solo dopo aver calcolato gli embedding. Non si procede se: albero wiki non leggibile; zero pagine ma chunk presenti; solo pagine vuote; una qualsiasi pagina fallita (in quel caso si aggiornano solo le pagine riuscite). **Se una scrittura fallisce dopo il drop l'indice resta incompleto: nessun rollback** (errore esplicito) |
| `vector_drop_legacy` (drop tabella) | LanceDB v1 | Dopo un re-index riuscito (`dropLegacyVectorTableBestEffort`) e da Settings (commento) | No-op se la tabella non esiste |
| `vector_delete_page` | righe v2 per `page_id` | Cancellazione sorgente (`removePageEmbedding`), `cleanupWrittenFiles` e cascata `cascadeDeleteWikiPage` (`wiki-page-delete.ts`, non letto), pulizia id legacy | Id validato; operazione idempotente |
| `vector_delete` | righe v1 | Nessun chiamante nel campione | Come sopra |
| `vector_upsert_chunks` | righe v2 | Ogni embedding di pagina | Sostituzione atomica ristretta alla pagina (merge-insert con cancellazione delle righe non piu' presenti). Lista vuota = no-op, non cancella |
| `vector_upsert` | righe v1 | Chiamate legacy | Cancella e poi aggiunge in due passi (non atomico); l'errore di cancellazione e' solo loggato |
| `vector_optimize_chunks` | versioni LanceDB | Ogni 20 pagine incrementali per progetto (contatore solo in memoria) e dopo scritture di massa | Compatta e pota le versioni precedenti, senza cancellazione "non verificata" (per l'uso multi-istanza); errori solo loggati |
| `invalidate_page_revision` | `embedding-revisions` | Ogni upsert di chunk senza impronta (ad esempio dal percorso TS) | Assenza del file non e' errore |
| `clear_file_history` | cartella `history/` | Comando Tauri (chiamante UI non nel campione) | Rifiuta symlink fuori dal progetto |
| `set_file_history_settings` | cartella `history/` o voci | Salvataggio impostazioni: limite a 0 elimina la cartella (anche file corrotti); riduzione del limite, o primo salvataggio, taglia le voci piu' vecchie | Massimo bloccato a 30 |
| `prune_history_store` | file di cronologia piu' vecchi | Dopo ogni registrazione, se si superano 128 MiB o 2.048 file | Salta il file appena scritto |
| `restore_file_history` | file di lavoro della wiki | Azione utente | Salva prima il contenuto attuale come voce `before.history.restore`; rifiuta se il file attuale supera 512 KB |
| `rebuild_wiki_index` | `wiki/index.md` | Comando Tauri (da Settings → manutenzione, per nome) | Sovrascrive per intero; file temporaneo e rinomina. Su Windows elimina prima l'originale: finestra non atomica |
| `import_project_archive` | cartella di destinazione | Importazione utente | Destinazione vuota obbligatoria; rifiuta percorsi non sicuri e symlink; massimo 100.000 voci e 4 GB; richiede `wiki/index.md` |
| `export_project_archive` | file zip | Esportazione utente | Include anche `.llm-wiki/` (chat, sessioni, cronologia, LanceDB). Destinazione fuori dal progetto |
| Troncamento sessione agente (`append_turn`) | messaggi piu' vecchi | Ogni turno | Mantiene gli ultimi 40 |
| Troncamento chat (`saveChatHistory`) | messaggi piu' vecchi | Ogni salvataggio | Salva solo gli ultimi 100 per conversazione: i precedenti si perdono al salvataggio |
| `removeTasks`, `discardTasksForSources`, `clearCompletedTasks`, `cancelAllTasks` | `ingest-queue.json` | Azioni utente; riconciliazione dello scheduled import | `removeTasks` salta i task con run attivo. `cancelAllTasks` conserva i task. `clearCompletedTasks` tiene solo pending e processing, quindi elimina anche failed e cancelled |
| `removeFromIngestCache`, `moveIngestCacheEntry` | `ingest-cache.json` | Cancellazione o rinomina di una sorgente | Gli errori di salvataggio sono ignorati |
| `removeFromRecentProjects` | `app-state.json` | Rimozione di un progetto dall'elenco recenti | Azzera anche `lastProject`; **non** rimuove la voce da `projectRegistry` e non cancella cartelle |
| `cleanupRemovedScheduledImports` | sorgenti mirror e pagine generate | Scansione quando un file sparisce o viene escluso | Solo per il progetto attivo; per gli altri si rinvia. Se fallisce, conserva il record per riprovare |
| `resetProjectState` | solo memoria | Apertura o uscita da un progetto | Non cancella nulla su disco; chiama prima `pauseQueue`, che scarica la coda su disco |

### Gestione dei file corrotti

- **Regola generale.** Quasi tutti i caricamenti usano un `try/catch` che restituisce un valore vuoto o di default (`persist.ts`, `ingest-cache.ts`, `dedup-storage.ts`, `ingest-queue.ts`, `lint-config.ts`, `scheduled-import.ts`). Nessuna rinomina in quarantena, nessun backup del file corrotto, nessun segnale all'utente nel campione (al massimo un avviso in console).
- **Effetto della prima scrittura dopo un file corrotto.** Dove il caricamento ricade sul valore vuoto e la scrittura successiva salva l'intero contenuto (coda, cache di ingest, elenco "non duplicati", database di scheduled import), il file corrotto viene sostituito dal nuovo contenuto.
- **Sessioni agente** (`agent/session.rs`). `list_sessions` salta i file non leggibili. Ma `append_turn` carica la sessione con ripiego sul valore vuoto e poi salva: un file corrotto verrebbe quindi sostituito al turno successivo. La scrittura e' diretta, non atomica.
- **Chat** (`persist.ts`). Se `conversations.json` manca o non si legge, `loadChatHistory` ricostruisce un indice minimo dai file `chats/*.json`, ignorando i file corrotti uno alla volta; se serve, prova poi il vecchio formato. Titolo della conversazione ricostruita: i primi 50 caratteri del primo messaggio utente, oppure "Previous Conversation".
- **Cronologia file** (`file_history.rs`). File non leggibili sono saltati in conteggio e potatura; sono rimossi quando la cronologia viene disattivata a limite 0. Rifiuta symlink per impostazioni, cartella e singoli file.
- **Identita' del progetto** (`project-identity.ts`). File mancante o corrotto: nuovo UUID e sovrascrittura (vedi `### Divergenze e rischi`).
- **Embedding** (`page_embedding.rs`). La revisione illeggibile o vuota e' trattata come assente. Un errore nel salvare i metadati di revisione invalida la revisione e non fallisce la scrittura dei vettori.
- **LanceDB.** Nessuna gestione dedicata: gli errori di connessione, apertura o scrittura sono propagati come messaggi di testo; nel percorso TS di ricerca un errore produce un elenco vuoto con messaggio di log.
- **`app-state.json`.** `loadRegistry` ritorna un registro vuoto in caso di errore. Per le altre chiavi dipende dal comportamento del plugin store, non verificato.

### Divergenze e rischi

Sono **deduzioni dal codice letto**, non fatti osservati in esecuzione. Per ognuna indico file e simbolo.

- **Possibile ricomparsa di chat cancellate.** `deleteConversation` (`src/stores/chat-store.ts`) rimuove la conversazione dallo store, ma `saveChatHistory` (`src/lib/persist.ts`) non elimina i file `chats/<id>.json` orfani, e `loadChatHistory` ricostruisce da quei file quando l'indice e' vuoto. Se l'utente cancella tutte le conversazioni, il caricamento successivo potrebbe resuscitarle. Non verificato: la rimozione fisica dei file potrebbe stare in codice non letto (ad esempio `chat-panel.tsx`).
- **Rigenerazione dell'identita' del progetto.** In `ensureProjectId` (`project-identity.ts`) un `project.json` corrotto produce un nuovo UUID. `restoreQueue` (`ingest-queue.ts`) scarta poi come "cross-project" i task con il vecchio id; le impostazioni per progetto in `app-state.json`, indicizzate per id (`projectLlmOverrides`, `projectOutputLanguages`, `sourceWatchConfig`, `projectFileSyncEnabled`), resterebbero orfane.
- **Scritture non serializzate sul registro.** Solo `saveProjectLlmOverride` e `saveCustomLlmPresets` (`project-store.ts`) hanno una catena di scrittura serializzata; `upsertProjectInfo` (`project-identity.ts`) usa lettura-modifica-scrittura non serializzata e parte da un registro vuoto se `loadRegistry` fallisce, con rischio di sovrascrivere l'intero `projectRegistry` con una sola voce.
- **Atomicita' eterogenea.** Atomiche (file temporaneo e rinomina): `lint-config.json` (`writeFileAtomic`), `scheduled-import-db.json`, le revisioni embedding. Non atomiche: sessioni agente e cronologia (scrittura diretta in `session.rs` e `file_history.rs`). Per gli altri file TS dipende dall'implementazione di `writeFile` in `src/commands/fs.ts` / `fs.rs`, non letta.
- **Logica duplicata tra TS e Rust.** Il chunking e' duplicato tra `page_embedding.rs` e `src/lib/text-chunker.ts` (il commento in `page_embedding.rs` lo dichiara); la pulizia dell'id legacy e' duplicata tra `embedding.ts` e `page_embedding.rs`. Inoltre `embedPage` (TS) scrive tramite `vector_upsert_chunks` senza impronta e quindi invalida le impronte salvate dal percorso Rust (`vector_upsert_chunks_inner`, ramo senza revisione).
- **Re-index senza rollback.** In `embedAllPages` (`embedding.ts`), dopo `vector_clear_chunks` un errore di scrittura lascia l'indice incompleto; il messaggio d'errore lo dice esplicitamente e chiede di rilanciare il re-index.
- **Cambio di modello o di dimensione dell'embedding.** La dimensione del vettore e' fissata dal primo chunk di una scrittura (`vector_upsert_chunks_inner`). Nel campione non c'e' una verifica esplicita di coerenza con la tabella esistente: la gestione di un cambio di modello sembra affidata al re-index (l'impronta di revisione include il modello). Da verificare.
- **Segreti in chiaro in `app-state.json`.** Vedi `### Schemi e campi`: sono stati letti solo i nomi dei campi (`token`, `localToken`; token API di `apiConfig` dai commenti); nessun valore.

### Gap

- `src-tauri/src/commands/file_sync.rs` (70 KB): sincronizzazione e watcher dei file; non letto, non so se persista stato.
- Rust non letto che incide sulla persistenza: `fs.rs` (atomicita' di `write_file` e `writeFileAtomic`, cancellazioni), `search.rs` (`embedding_fetch`, `SearchEmbeddingConfig`), `api_server.rs` (lettura di `apiConfig`, endpoint che scrivono), `agent/runtime.rs` (chi chiama `append_turn` e con quali id di sessione), `proxy.rs`, `lib.rs` oltre le parti gia' lette.
- TS non letto: `src/stores/wiki-store.ts` (tipi di tutte le configurazioni, compresi i campi segreti), `lint-store.ts`, `dedup-queue.ts` (persistenza della coda dedup), `wiki-page-delete.ts` (cascata di cancellazione), `source-lifecycle.ts`, `ingest.ts` (scrittura di `ingest-cache` e della cache delle didascalie), `chat-panel.tsx` (cancellazione dei file chat), `sweep-reviews.ts`, `src/commands/fs.ts`.
- File citati nei commenti ma non verificati: `image-caption-cache.json`, `lexical-graph.json` (commento di `dedup-storage.ts`), la cartella `raw/sources/.cache` e la cartella legacy `.llm-wiki-imported`.
- Percorso effettivo di `app-state.json` e comportamento del plugin store su file corrotto: non determinabili dal campione.
- Chi crea `.llm-wiki/` per un progetto importato o aperto da disco: `create_project` non la crea e `open_project` non la richiede.
- Nessun chiamante di `vector_upsert` e `vector_delete` (v1) nel campione: non e' chiaro se i percorsi v1 siano ancora usati.
- Formato di `wiki/log.md` e logica di aggiornamento di `wiki/index.md` oltre `rebuild_wiki_index`: non analizzati.
- Nessun dato su dimensioni reali, prestazioni o crescita degli archivi.

### Note di estrazione dell'update

- File letti in questo giro: 21 su 476 (campione approvato dall'utente, ciascuno sotto 50.000 byte); `files_sampled` cumulativo nel manifest: 50.
- Segreti redatti: 0. Nessun file `.env*` e nessun valore di credenziale in chiaro nei 21 file. Le stringhe "secret" e "rotated" nei test Rust di `page_embedding.rs` sono segnaposto di test, non conteggiati. Limite invariato: nessuna scansione testuale dei sorgenti non aperti.
- Istruzioni trovate nei file letti: nessuna. Nei test Rust compare un id di pagina con apice e parola chiave SQL usato come caso di prova per la validazione dell'input (`vectorstore.rs`): e' una fixture, non un'istruzione. Nessun commento per i manutentori e' stato eseguito.
- Stato dell'estrazione complessiva: **partial** (invariato), per i gap sopra.
- Il documento supera il target di 5-15 KB per effetto dell'append in coda.

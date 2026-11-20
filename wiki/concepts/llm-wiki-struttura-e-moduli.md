---
id: llm-wiki-struttura-e-moduli
type: concept
title: llm-wiki — struttura e moduli
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: ["raw/2026-11-20-repo-llm_wiki.md", "raw/images/2026-11-20-repo-llm_wiki-tree.md"]
tags: [llm-wiki, struttura, moduli]
---

# llm-wiki — struttura e moduli
> Repository multi-package con struttura a strati: 476 file, frontend in `src/`, backend Rust in `src-tauri/`, server MCP in `mcp-server/`; il raw ne ha campionati 30.

## Contesto
Il totale di 476 file esclude `.git`, `node_modules`, `vendor`, `dist`, `build` e `target`. [^src: raw/2026-11-20-repo-llm_wiki.md §Struttura ad alto livello]

## Dettaglio

### Layout
- Cartelle di primo livello e file: radice 17 (README in 4 lingue, `LICENSE`, manifest, config Vite e TS, `llm-wiki.md`), `.github` 4, `assets` 9, `extension` 10 (estensione Chrome Manifest V3), `mcp-server` 11, `plans` 1, `scripts` 1, `src` 362 (frontend), `src-tauri` 61 (backend Rust). [^src: raw/2026-11-20-repo-llm_wiki.md §Struttura ad alto livello]
- Pattern di layout: multi-package, con struttura a strati (UI, logica di dominio in `lib/`, stato in `stores/`, comandi verso il backend, backend Rust con moduli `agent/` e `commands/`). [^src: raw/2026-11-20-repo-llm_wiki.md §Struttura ad alto livello]
- `src/components/` è suddiviso per area funzionale: chat, editor, graph, layout, lint, project, review, search, settings, sources, ui. [^src: raw/2026-11-20-repo-llm_wiki.md §Struttura ad alto livello]
- `src-tauri/pdfium/` contiene librerie native precompilate per più piattaforme (circa 7 MB ciascuna), non aperte. [^src: raw/2026-11-20-repo-llm_wiki.md §Struttura ad alto livello]
- Albero esteso a depth 3 (41 directory) nel companion [tree](../../raw/images/2026-11-20-repo-llm_wiki-tree.md). [^src: raw/images/2026-11-20-repo-llm_wiki-tree.md §Albero filesystem — llm_wiki (depth 3)]

### Entrypoint
- **Frontend**, `src/main.tsx`: applica la classe di piattaforma (macOS), carica e applica il tema, osserva il tema di sistema, poi monta `App` insieme a `AppDialogHost` in strict mode. Se l'avvio fallisce, mostra una schermata di errore con escape dell'HTML del messaggio. [^src: raw/2026-11-20-repo-llm_wiki.md §Entrypoint e moduli chiave]
- **`src/App.tsx`** (letto in parte, righe 1-80): al boot carica dal project store le configurazioni (provider LLM, embedding, MinerU, multimodale, lingua di output, preset, routing dei task, override per progetto, proxy, importazione schedulata, source watch, API, generale, zoom), idrata gli store di chat, review e lint per progetto, avvia auto-save e clip watcher e mostra `WelcomeScreen` e `CreateProjectDialog`. [^src: raw/2026-11-20-repo-llm_wiki.md §Entrypoint e moduli chiave]
- **Backend**: `src-tauri/src/main.rs` delega a `llm_wiki_lib::run()`. [^src: raw/2026-11-20-repo-llm_wiki.md §Entrypoint e moduli chiave]
- **`src-tauri/src/lib.rs`** (letto in parte, righe 1-200 e 480-793): costruisce il Tauri Builder con i plugin opener, dialog, store, autostart e http; nel setup imposta l'hint della cartella risorse per pdfium, applica il proxy letto da `app-state.json`, registra gli stati di sessione e cancellazione dell'agente, avvia clip server e API server e poi la tray. Gestisce la chiusura finestra in tre modalità (ask, minimize, exit) e applica su Linux due variabili d'ambiente di compatibilità WebKit. [^src: raw/2026-11-20-repo-llm_wiki.md §Entrypoint e moduli chiave]

### Moduli Rust
- `agent`: vedi [[llm-wiki-agente]]. [^src: raw/2026-11-20-repo-llm_wiki.md §Entrypoint e moduli chiave]
- `commands`: claude_cli, cli_resolver, codex_cli, ebook, external_search, extract_images, file_history, file_sync, fs, page_embedding, project, project_maintenance, search, vectorstore. [^src: raw/2026-11-20-repo-llm_wiki.md §Entrypoint e moduli chiave]
- Moduli di primo livello: `api_server`, `clip_server`, `cors`, `panic_guard`, `proxy`, `server_bind`, `tray`, `types`. [^src: raw/2026-11-20-repo-llm_wiki.md §Entrypoint e moduli chiave]

### Moduli core (stima)
Fan-in stimato dai soli import dei 30 file campionati, segnale debole da prendere con cautela: `@/stores/wiki-store` (3 file), `@/commands/fs` (3), `@/lib/frontmatter` (2); lato Rust, `agent::types` richiamato da `router.rs` e `lib.rs`. [^src: raw/2026-11-20-repo-llm_wiki.md §Entrypoint e moduli chiave]

### File grandi non aperti
Oltre 50 KB: `src-tauri/src/agent/runtime.rs` (225 KB), `src-tauri/src/api_server.rs` (142 KB), `src-tauri/src/agent/tools.rs` (139 KB), `src-tauri/src/commands/fs.rs` (130 KB), `src/lib/ingest.ts` (161 KB, letto solo l'inizio: righe 1-70, import e costanti sui budget di token e di chunk). [^src: raw/2026-11-20-repo-llm_wiki.md §Entrypoint e moduli chiave]

## Pagine collegate
[[llm-wiki-agente]], [[llm-wiki-api-locale]], [[llm-wiki-stack-e-dipendenze]], [[llm-wiki-schema-dati]]. Gap aperto: [[gaps]] (`llm-wiki-codice-non-letto`).

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

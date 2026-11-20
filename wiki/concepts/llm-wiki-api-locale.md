---
id: llm-wiki-api-locale
type: concept
title: llm-wiki — API HTTP locale, clip server e comandi Tauri
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: ["raw/2026-11-20-repo-llm_wiki.md"]
tags: [llm-wiki, api, tauri]
---

# llm-wiki — API HTTP locale, clip server e comandi Tauri
> Gli endpoint dell'API HTTP locale sono noti solo dalla README: il codice che ne definisce il contratto non è stato letto.

## Contesto
L'applicazione espone tre superfici: i comandi Tauri tra frontend e backend, un'API HTTP locale e un server MCP (vedi [[llm-wiki-mcp-server]]). Il modulo `agent` è condiviso fra UI, API e MCP, vedi [[llm-wiki-agente]]. [^src: raw/2026-11-20-repo-llm_wiki.md §API surface (se rilevata)]

## Dettaglio

### Comandi Tauri (frontend verso backend)
- Circa 75 comandi registrati in `lib.rs`, per famiglie: file system e cronologia file; progetto e manutenzione (esportazione e importazione archivio, ricostruzione dell'indice); ricerca ed embedding; vector store su LanceDB; spawn e kill dei CLI `claude` e `codex`; estrazione di immagini da PDF e Office; sincronizzazione e watcher dei file; agente (avvio turno, streaming, cancellazione, sessioni, skill); proxy e comportamento di chiusura. [^src: raw/2026-11-20-repo-llm_wiki.md §API surface (se rilevata)]
- `lib.rs` è stato letto solo in parte (righe 1-200 e 480-793), quindi il numero è approssimato. [^src: raw/2026-11-20-repo-llm_wiki.md §Entrypoint e moduli chiave]

### API HTTP locale
- Dichiarata nella README: `http://127.0.0.1:19828`, prefisso `/api/v1`, protetta da token. [^src: raw/2026-11-20-repo-llm_wiki.md §API surface (se rilevata)]
- Endpoint elencati dalla README: health (senza auth), projects, files e files/content, reviews (lettura, aggiornamento singolo, risoluzione in blocco), search ibrida (parole chiave più vettori), chat (anche in streaming SSE), graph (con filtri e paginazione), sources/rescan, pages/embed. [^src: raw/2026-11-20-repo-llm_wiki.md §API surface (se rilevata)]
- Il contratto reale sta in `src-tauri/src/api_server.rs` (non letto) e nel client `mcp-server/src/api-client.ts` (non letto). Non c'è un file OpenAPI. [^src: raw/2026-11-20-repo-llm_wiki.md §API surface (se rilevata)]
- Le costanti della porta e dell'URL di health lato frontend sono in `src/lib/api-server-constants.ts`. [^src: raw/2026-11-20-repo-llm_wiki.md §API surface (se rilevata)]
- L'elenco endpoint della README non cita una scrittura pagina; gli endpoint HTTP corrispondenti a scrittura pagina ed embedding non sono verificati. [^src: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti]

### Clip server
Un secondo server locale, il clip server, ascolta sulla porta 19827 (README ed estensione Chrome). L'implementazione è in `clip_server.rs`, non letto. [^src: raw/2026-11-20-repo-llm_wiki.md §API surface (se rilevata)]

### Bind e ascolto
La README descrive l'API come `127.0.0.1`-only, mentre il codice prevede l'ascolto su LAN opzionale: vedi [[llm-wiki-sicurezza]]. [^src: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti]

## Pagine collegate
[[llm-wiki-agente]], [[llm-wiki-sicurezza]]. Gap aperti: [[gaps]] (`llm-wiki-contratto-api-http`, `llm-wiki-api-lan-auth`).

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

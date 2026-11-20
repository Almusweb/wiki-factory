---
id: llm-wiki-api-locale
type: concept
title: llm-wiki — API HTTP locale, clip server e comandi Tauri
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: ["raw/2026-11-20-repo-llm_wiki.md", "raw/2026-11-20-repo-llm_wiki-persistenza-a.md", "raw/2026-11-20-repo-llm_wiki-persistenza-c.md"]
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

## Aggiornamenti (v2026-11-20)
Dalle fette A e C delle estrazioni mirate sulla persistenza ([[2026-11-20-repo-llm_wiki-persistenza-a]], [[2026-11-20-repo-llm_wiki-persistenza-c]]). `api_server.rs` è letto solo in parte: righe 1-1200 più finestre (2035-2045, 2340-2360, 2435-2465, 2910-2925 per la fetta A; 360-395, 1572-1700, 1840-1897, 2060-2080 per la fetta C). Il testo sopra non è modificato; dove è superato lo dice `## Contradictions` in coda. I gap `llm-wiki-contratto-api-http` e `llm-wiki-api-lan-auth` restano aperti. Qualificatori come nel raw («solo graphify» non è promosso). Autenticazione, `/health` e segreti sono in [[llm-wiki-sicurezza]].

### Lettura della configurazione
- `api_server.rs` legge `apiConfig` da `app-state.json` tramite `load_app_state` e gli helper `api_token`, `api_token_source`, `api_auth_required`, `api_allow_unauthenticated`, `api_allow_lan_access`, `api_enabled`, `api_mcp_enabled`; la lettura è a ogni richiesta con cache di 5 secondi (`APP_STATE_CACHE_TTL`). [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Lettori backend di `apiConfig` e `proxyConfig`]
- Il comando Tauri `api_server_reload_config` invalida la cache. Il salvataggio delle impostazioni lo invoca subito dopo `saveApiConfig` (errore solo in warn), senza condizione visibile nella finestra letta; un commento dice che le modifiche arrivano entro i 5 s «senza IPC», ma il codice invoca comunque il reload (nota, non difetto). [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Punto 9: quando la UI invoca `set_proxy_env` e il reload]
- Altri lettori di `app-state.json` in `api_server.rs` (letti): `load_embedding_config` legge `embeddingConfig`; la copia di `load_agent_runtime_config` legge `embeddingConfig`, `llmConfig` (prima un override di progetto da `project_llm_config`, corpo non letto), `searchApiConfig` e `searchApiConfig.anyTxt` ed è usata a `:2041`; `load_source_watch_config` legge `sourceWatchConfig` per id progetto o `default`. Tutte passano dalla cache di 5 secondi. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Punto 4: lettori di `app-state.json` in `api_server.rs`]
- Solo graphify, non letto: `load_embedding_config` è chiamato da `handle_embed_page` (`:1909`) e `handle_search` (`:1958`); `load_source_watch_config` da `handle_rescan` (`:2902`); `load_projects` (`:777`) da `handle_projects` (`:764`) e `resolve_project` (`:857`). Le chiavi di `load_projects` non sono confermate dalla lettura. `resolve_query_embedding` ha come chiamanti `search_project`, `handle_search` e `run_wiki_search`, anch'essi solo graphify. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Punto 4: lettori di `app-state.json` in `api_server.rs`]
- Il proxy è letto da `proxy::read_proxy_config_from_store` una sola volta all'avvio dal setup; `set_proxy_env` riceve la configurazione come argomento e non rilegge il file. `read_proxy_config_from_store` è chiamato solo da `run()` e dai test (graphify). [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Lettori backend di `apiConfig` e `proxyConfig`]
- Porta e URL base dell'API lato frontend: 19828. Altri lettori di `apiConfig` e `proxyConfig` oltre a quelli visti (resto di `api_server.rs`, `clip_server.rs`, altro Rust) non sono verificati. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Lettori backend di `apiConfig` e `proxyConfig`]

### Rotte che scrivono
- La tabella delle rotte di `handle_request` (`api_server.rs:360-395`) è completa per quel blocco ed è chiusa da un 404; nessuna rotta cancella pagine o file. Le rotte che scrivono sono: `PATCH projects/{id}/reviews/{review}`, `DELETE projects/{id}/reviews/{review}` e `POST projects/{id}/reviews/resolve` (`review.json`); `POST projects/{id}/pages/write` (pagina `.md`; 409 se rifiuta di sovrascrivere, 400 per percorso, tipo file o dimensione); `POST projects/{id}/chat` (`agent-sessions` via `append_turn`); `POST projects/{id}/pages/embed` e `POST projects/{id}/sources/rescan` (corpi non letti). La rotta `chat/{session_id}/cancel` prende l'id da un segmento dell'URL. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Endpoint dell'API locale che scrivono o cancellano]
- Deduzione sui gestori delle review: nei corpi letti non c'è emissione di eventi verso l'interfaccia; con l'app aperta lo store in memoria non vedrebbe la modifica (vedi [[llm-wiki-rischi-persistenza]]). Il meccanismo di `write_raw_review_array` e la funzione `write_wiki_page_verified` (`agent/tools.rs`) non sono letti. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Endpoint dell'API locale che scrivono o cancellano]

## Contradictions
- **`api_server.rs` «non letto» e endpoint di scrittura pagina ed embed.** Prima: «Il contratto reale sta in `src-tauri/src/api_server.rs` (non letto)» e «gli endpoint HTTP corrispondenti a scrittura pagina ed embedding non sono verificati». Ora (fetta A): `api_server.rs` è letto alle righe 1-1200 più finestre, con `/health`, autenticazione per token e gli endpoint che richiedono sempre il token. Ora (fetta C): esistono rotte e gestori per `pages/write` e `pages/embed`; i corpi di embed e rescan non sono letti e `pages/write` non compare nell'elenco endpoint della README (vedi il gap `llm-wiki-mcp-readme-vs-codice`, aperto). Il contratto completo resta non verificato. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §File letti e non letti] [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Endpoint dell'API locale che scrivono o cancellano]

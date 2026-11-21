---
id: llm-wiki-api-locale
type: concept
title: llm-wiki — API HTTP locale, clip server e comandi Tauri
status: draft
created: 2026-11-20
updated: 2026-11-21
sources: ["raw/2026-11-20-repo-llm_wiki.md", "raw/2026-11-20-repo-llm_wiki-persistenza-a.md", "raw/2026-11-20-repo-llm_wiki-persistenza-c.md", "raw/2026-11-21-repo-llm_wiki-api-mcp.md"]
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

## Aggiornamenti (v2026-11-21)
Dalla fetta A del giro del 2026-11-21 ([[2026-11-21-repo-llm_wiki-api-mcp]], commit `e08cfce`): `api_server.rs` è letto per intero (righe 1-4106), insieme a `server_bind.rs`, `cors.rs` e al client MCP. Il testo sopra e la sezione precedente non sono modificati; dove sono superati lo dice `## Contradictions` in coda. I gap `llm-wiki-contratto-api-http` e `llm-wiki-api-lan-auth` sono chiusi in [[gaps]]. Tutto deriva da lettura statica: nessun test è stato eseguito. Autenticazione, bind, CORS e inferenze non testate sono in [[llm-wiki-sicurezza]]; il client MCP è in [[llm-wiki-mcp-server]]. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Provenienza e copertura]

### Server HTTP
- Il server è `tiny_http` con un thread per richiesta, porta 19828, prefisso `/api/v1`. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Server HTTP]
- Stato globale: 0 starting, 1 running, 2 port_conflict, 3 error. Il bind è ritentato 3 volte con 2 s di pausa; se il ciclo termina il server viene rilanciato. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Server HTTP]
- Limiti: body 1 MiB; chat 40 MiB; `pages/write` circa 12 MiB; file letto via API max 2 MiB; richieste in volo 64, stream chat in volo 8 ed embed in volo 4, tutti con risposta 503 al superamento. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Server HTTP]
- Rate limit di 120 richieste per finestra di 1 s, globale, escluso `/health` e `OPTIONS`, con risposta 429; è applicato prima dell'autenticazione e conta anche i path non-API. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Server HTTP]
- Ordine dei controlli per richiesta: `OPTIONS` (204 con CORS), lettura del body, chat in streaming, `/health`, prefisso `/api/v1` (404), API abilitata (503), token per le route sensibili, auth generale (401), metodo ammesso (405), match della route. Il body è letto prima del controllo token (fino a circa 12 MiB su `pages/write`, 40 MiB su chat). [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Server HTTP]
- La configurazione runtime viene da `apiConfig` in `app-state.json` (`enabled`, `allowUnauthenticated`, `allowLanAccess`, `mcpEnabled`, `token`) con cache di 5 s; `enabled` ha default true se la config manca. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Server HTTP]

### Contratto delle route
- Tutte le risposte sono JSON `{ok, ...}`, gli errori `{ok:false, error}`. L'id progetto accetta UUID, path esatto o `current`. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Contratto API]
- Le route sono 15, più `/health` doppio (`/health` e `/api/v1/health`): `projects`, `files`, `files/content`, `reviews` (GET, PATCH, DELETE, resolve), `search`, `graph`, `sources/rescan`, `pages/embed`, `pages/write`, `chat` e `chat/{sessionId}/cancel`. Metodi ammessi GET, POST, PATCH, DELETE; gli altri danno 405 dopo l'auth. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Contratto API]
- `files/content` serve solo `purpose.md`, `schema.md`, `wiki/` e `raw/sources/`, senza componenti che iniziano con un punto (403 altrimenti); 415 se non testo UTF-8, 413 oltre 2 MiB. `files` limita `maxFiles` a 1..10000 (default 2000) con 413 al superamento. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Contratto API]
- `search` accetta `{query, topK (default 10, max 50), includeContent, queryEmbedding}` e restituisce `mode`, `tokenHits`, `vectorHits`, `graphHits`, `results`; `graph` accetta `q`, `nodeType`, `limit` (default 200, max 1000), `offset` ed `edgeScope`, con cache di 5 s. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Contratto API]
- `pages/write` accetta `{path, content, allowOverwrite}` con `deny_unknown_fields`: 409 se la pagina esiste senza `allowOverwrite`, 400 per path, markdown o dimensione, 500 altrimenti. `pages/embed` richiede il token, risponde 400 se l'embedding non è configurato e 503 con 4 embed in volo. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Contratto API]
- `chat` risponde in JSON o in SSE (se `stream:true` oppure `Accept: text/event-stream`, con il campo `stream` che prevale); eventi `meta`, `agent`, `done`, `cancelled`, `error`; keepalive ogni 10 s; coda di 64 frame con frame intermedi scartati se piena e frame terminale garantito; la disconnessione del client cancella il run. Il corpo `AgentChatRequest` è in `agent/` e non è stato letto da questa fetta. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Contratto API]
- `API_ENDPOINTS` in `api-server-section.tsx` si dichiara «in lock-step» con il router ma ha 13 voci: mancano `POST .../pages/write` e `DELETE .../reviews/{reviewId}`, presenti nel router. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Confronto con la lista documentata nella UI]

### Scritture sullo stato
- Le scritture delle review (`PATCH`, `DELETE`, `resolve`) operano sull'array JSON grezzo di `.llm-wiki/review.json` e lo riscrivono con `serde_json::to_string_pretty` e `fs::write`: la scrittura non è atomica, non è verificata dopo il salvataggio e non usa lock. Resta una finestra read-modify-write rispetto al processo WebView (non letto); i test unitari non coprono la concorrenza. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Scritture sullo stato]
- `pages/write` delega ad `agent::tools::write_wiki_page_verified`: il nome e il client dichiarano la verifica byte per byte; l'implementazione è descritta in [[llm-wiki-rischi-persistenza]] dalla fetta [[2026-11-21-repo-llm_wiki-agente-tools]]. Il raw della fetta A, che non l'ha letta, parla di asimmetria tra scritture review (senza verifica) e scrittura pagina (verifica dichiarata). [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Scritture sullo stato]

### Clip server e uso di bind e CORS
`server_bind` e `cors` sono usati da `api_server.rs` (porta 19828) e importati da `clip_server.rs` (porta 19827); l'uso effettivo in `clip_server.rs` oltre la riga 60 è non verificato (gap `llm-wiki-clip-server-uso-bind-cors`). [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Autenticazione e rete]

## Contradictions
- **`api_server.rs` «non letto» e endpoint di scrittura pagina ed embed.** Prima: «Il contratto reale sta in `src-tauri/src/api_server.rs` (non letto)» e «gli endpoint HTTP corrispondenti a scrittura pagina ed embedding non sono verificati». Ora (fetta A): `api_server.rs` è letto alle righe 1-1200 più finestre, con `/health`, autenticazione per token e gli endpoint che richiedono sempre il token. Ora (fetta C): esistono rotte e gestori per `pages/write` e `pages/embed`; i corpi di embed e rescan non sono letti e `pages/write` non compare nell'elenco endpoint della README (vedi il gap `llm-wiki-mcp-readme-vs-codice`, aperto). Il contratto completo resta non verificato. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §File letti e non letti] [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Endpoint dell'API locale che scrivono o cancellano]
  - Nota di superamento (2026-11-21): superata dalla fetta A del 2026-11-21. Il contratto non è più «non letto»: `api_server.rs` è letto per intero e il raw documenta 15 route più `/health`, con `pages/write` e `pages/embed` e relativi errori e limiti (vedi sopra); restano non letti i corpi degli handler a valle (gap `llm-wiki-api-corpi-handler-non-letti`). Va inteso come «superato», non «assente». [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Contratto API]
- **Elenco endpoint della README e lista della UI.** Prima (README, riportata dalla pagina): endpoint `health`, `projects`, `files`, `reviews`, `search`, `chat`, `graph`, `rescan`, `embed`, senza `pages/write` né `DELETE` review. Ora (fetta A): il router ha 15 route; la lista `API_ENDPOINTS` della UI ne ha 13 pur dichiarandosi «in lock-step» con il router (mancano `pages/write` e `DELETE .../reviews/{reviewId}`). Documentazione e codice divergono in entrambi i casi. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Confronto con la lista documentata nella UI]
- **Scrittura delle review «non letta».** Prima (Aggiornamenti v2026-11-20): «Il meccanismo di `write_raw_review_array` ... non sono letti». Ora (fetta A): le scritture sono lette: riscrittura dell'array grezzo con `fs::write`, non atomica, non verificata, senza lock; la finestra rispetto alla WebView resta non letta. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Scritture sullo stato]

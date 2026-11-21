# Specifiche estratte: llm_wiki, API HTTP locale, MCP, rete

> Documento generato da `repo-sync` v2.12 il 2026-11-21. Sorgente: `/home/user/wiki-factory/code_repos/llm_wiki`
> @ commit e08cfce65aad8b76b13546a081c1a8d4422b70c3 (v0.6.13, branch HEAD detached). Read-only verso la sorgente.
> Fetta A (API, MCP, rete). Chiude i gap 2, 3, 4, 30 e la parte `api_server.rs` del gap 1.

## Provenienza e copertura

Letti per intero: `src-tauri/src/api_server.rs` (1-4106), `server_bind.rs` (1-107), `cors.rs` (1-113), `src/lib/api-token.ts`, `src/lib/api-server-constants.ts`, `mcp-server/src/api-client.ts` (1-546), `mcp-server/src/index.ts` (1-599), `mcp-server/README.md` (1-78).
Letti in parte: `src/components/settings/sections/api-server-section.tsx` (1-399), `src-tauri/src/clip_server.rs` (1-60, solo import).
Non letti: resto di `api-server-section.tsx`, `src/i18n/index.ts`, `mcp-server/src/project-binding.ts`, `mcp-server/src/version.ts`, corpo di `clip_server.rs` oltre la riga 60.
Un chiamante non trovato nelle finestre lette e' "non verificato", non "assente".

## Server HTTP

- Server `tiny_http`, un thread per richiesta, porta 19828, prefisso `/api/v1` [^src: src-tauri/src/api_server.rs:16,23-24,104-125].
- Stato globale: 0 starting, 1 running, 2 port_conflict, 3 error. Il bind e' ritentato 3 volte con 2 s di pausa; se il ciclo termina il server viene rilanciato [^src: src-tauri/src/api_server.rs:36-37,49,89-151].
- Limiti: body 1 MiB; chat 40 MiB; `pages/write` circa 12 MiB (6x2 MiB + 16 KiB, perche' un byte puo' diventare `\u00XX`); file letto via API max 2 MiB; richieste in volo 64 (503); stream chat in volo 8 (503); embed in volo 4 (503) [^src: src-tauri/src/api_server.rs:25-30,41-43,112-115,254-262,1912-1914].
- Rate limit: 120 richieste per finestra di 1 s, globale, escluso `/health` e `OPTIONS`; risposta 429. E' applicato prima dell'autenticazione e conta anche path non-API [^src: src-tauri/src/api_server.rs:39-40,108-111,397-420].
- Ordine dei controlli per richiesta: `OPTIONS` -> 204 con CORS; lettura del body (anche prima dell'auth); chat in streaming (API abilitata, token, progetto, slot); `/health`; prefisso `/api/v1` (404); API abilitata (503); token obbligatorio per le route sensibili; auth generale (401); metodo ammesso (405); match della route [^src: src-tauri/src/api_server.rs:205-395].
- Il body e' letto prima del controllo token (fino a circa 12 MiB su `pages/write`, 40 MiB su `chat`) [^src: src-tauri/src/api_server.rs:225,246].
- Configurazione runtime da `app-state.json` (`apiConfig`: `enabled`, `allowUnauthenticated`, `allowLanAccess`, `mcpEnabled`, `token`), con cache di 5 s. `enabled` ha default `true` se la config manca [^src: src-tauri/src/api_server.rs:38,661-753].

## Contratto API

Tutte le risposte sono JSON `{ok, ...}`; gli errori sono `{ok:false, error}`. L'id progetto accetta UUID, path esatto o `current` [^src: src-tauri/src/api_server.rs:284-298,854-865].

| Metodo e path | Auth | Payload / query | Risposta e errori |
|---|---|---|---|
| GET `/health`, `/api/v1/health` | mai | - | `status`, `version`, `authRequired`, `authConfigured`, `tokenSource` (env/store/none), `enabled`, `mcpEnabled`, `allowUnauthenticated`, `allowLanAccess`, `agent{chat,streaming,streamProtocol:"sse"}`; raggiungibile anche con API disabilitata [^src: src-tauri/src/api_server.rs:308-331] |
| GET `/projects` | generale | - | `projects[]{id,name,path,current}`, `currentProject` [^src: src-tauri/src/api_server.rs:763-771] |
| GET `/projects/{id}/files` | generale | `root` (wiki, sources/raw/raw/sources, all), `recursive`, `maxFiles` (clamp 1..10000, default 2000) | `files[]`; 400 root invalido; 413 se supera maxFiles; 404 progetto [^src: src-tauri/src/api_server.rs:898-947] |
| GET `/projects/{id}/files/content` | generale | `path` | 403 path non pubblico (solo `purpose.md`, `schema.md`, `wiki/`, `raw/sources/`, niente componenti che iniziano con `.`); 415 non testo o non UTF-8; 413 oltre 2 MiB; 404; 400 [^src: src-tauri/src/api_server.rs:949-987,1031-1056] |
| GET `/projects/{id}/reviews` | generale | `status` (unresolved/pending/resolved/all), `type`, `limit` (default 200, max 1000) | `reviews[]` sanitizzati, `count`; 400 status invalido [^src: src-tauri/src/api_server.rs:33-34,1196-1227,1536-1555] |
| PATCH `/projects/{id}/reviews/{reviewId}` | generale | `{resolved?, action?}`; body vuoto = resolve | 404 se id ignoto [^src: src-tauri/src/api_server.rs:1557-1604] |
| DELETE `/projects/{id}/reviews/{reviewId}` | generale | - | `deleted:true`; 404 [^src: src-tauri/src/api_server.rs:1616-1649] |
| POST `/projects/{id}/reviews/resolve` | generale | `{ids` (alias `reviewIds`)`, action?}` | 200 con `resolved`, `notFound`, `count`; 400 se `ids` vuoto [^src: src-tauri/src/api_server.rs:1606-1614,1656-1678] |
| POST `/projects/{id}/search` | generale | `{query, topK (default 10, max 50), includeContent, queryEmbedding}` | `mode`, `tokenHits`, `vectorHits`, `graphHits`, `results`; 400 query vuota [^src: src-tauri/src/api_server.rs:35,1814-1821,1940-1982] |
| GET `/projects/{id}/graph` | generale | `q`, `nodeType`, `limit` (default 200, max 1000), `offset`, `edgeScope` (page/filtered) | `nodes`, `edges`, `offset`, `limit`, `totalCount`, `hasMore`; 400 parametri invalidi; cache 5 s [^src: src-tauri/src/api_server.rs:2496-2548] |
| POST `/projects/{id}/sources/rescan` | generale | - | `result`; 500 [^src: src-tauri/src/api_server.rs:2896-2913] |
| POST `/projects/{id}/pages/embed` | sempre token | `{path, force}` | 400 se embedding non configurato; 503 con 4 embed in volo; errori mappati 400/404/502/500/504 [^src: src-tauri/src/api_server.rs:1897-1938] |
| POST `/projects/{id}/pages/write` | sempre token | `{path, content, allowOverwrite}`, `deny_unknown_fields` | `result`; 409 se esiste senza `allowOverwrite`; 400 per path/markdown/too large; 500 altro [^src: src-tauri/src/api_server.rs:1831-1878] |
| POST `/projects/{id}/chat` | sempre token | corpo `AgentChatRequest` (struct in `agent/`, non letta); JSON o SSE se `stream:true` oppure `Accept: text/event-stream` (il campo `stream` prevale) | 400 message vuoto; 499 cancellato; 502 errore agente; 503 troppi stream [^src: src-tauri/src/api_server.rs:472-495,2106-2126] |
| POST `/projects/{id}/chat/{sessionId}/cancel` | sempre token | - | `cancelled`, `sessionId` [^src: src-tauri/src/api_server.rs:2335-2347] |

Totale: 15 route, piu' `/health` doppio. Metodi ammessi: GET, POST, PATCH, DELETE; altri -> 405 dopo l'auth [^src: src-tauri/src/api_server.rs:349-394].
SSE: eventi `meta`, `agent`, `done`, `cancelled`, `error`; keepalive `: keepalive` ogni 10 s; coda di 64 frame, frame intermedi scartati se piena, frame terminale garantito; la disconnessione del client cancella il run [^src: src-tauri/src/api_server.rs:44-45,2160-2333].

### Confronto con la lista documentata nella UI

`API_ENDPOINTS` in `api-server-section.tsx` dichiara di essere "in lock-step" con il router ma ha 13 voci: mancano `POST .../pages/write` e `DELETE .../reviews/{reviewId}`, presenti nel router [^src: src/components/settings/sections/api-server-section.tsx:39-59] [^src: src-tauri/src/api_server.rs:375,386].

## Autenticazione e rete

- **Bind**: default `127.0.0.1`; con `apiConfig.allowLanAccess=true` in `app-state.json` si bind a `0.0.0.0`; `LLM_WIKI_BIND_HOST` ha precedenza sullo store e accetta solo `[A-Za-z0-9.:_\-\[\]]`. Serve riavvio (testo UI). Vale anche per il Clip server [^src: src-tauri/src/server_bind.rs:6-62] [^src: src/components/settings/sections/api-server-section.tsx:321-341].
- **Token**: da `LLM_WIKI_API_TOKEN` (priorita') o `apiConfig.token`. Accettato come `?token=`, `X-LLM-Wiki-Token` o `Authorization: Bearer`; confronto a tempo costante [^src: src-tauri/src/api_server.rs:586-659,716-725].
- **Nessuna distinzione loopback/LAN**: lo schema e' lo stesso. Senza token configurato e senza `allowUnauthenticated`, ogni route `/api/v1` risponde 401 [^src: src-tauri/src/api_server.rs:598-600].
- **Matrice**:
  - Token sempre richiesto: `chat`, `chat/cancel`, `pages/embed`, `pages/write` [^src: src-tauri/src/api_server.rs:433-445].
  - Con `allowUnauthenticated=true` senza token: `projects`, `files`, `files/content`, `reviews` (lettura, PATCH, DELETE, resolve), `search`, `graph`, `sources/rescan`.
  - Combinando LAN e `allowUnauthenticated`, queste route sono raggiungibili dalla rete senza credenziali, comprese le modifiche alle review e il rescan.
  - `/health` e' sempre aperto.
- **CORS** (non e' autenticazione): `Access-Control-Allow-Origin` solo per `chrome-extension://`, `moz-extension://`, `http://localhost`, `127.0.0.1`, `[::1]` (con o senza porta), `tauri://localhost`, `http(s)://tauri.localhost`; le altre origini ricevono la risposta senza l'header. Metodi `GET, POST, PATCH, DELETE, OPTIONS`; header ammessi `Content-Type, Authorization, X-LLM-Wiki-Token` [^src: src-tauri/src/cors.rs:11-41] [^src: src-tauri/src/api_server.rs:548-550]. Un client non-browser in LAN non e' limitato da CORS.
- **Uso dei moduli**: `server_bind` e `cors` sono usati da `api_server.rs` (porta 19828) e importati da `clip_server.rs` (porta 19827) [^src: src-tauri/src/api_server.rs:20-21,135-136] [^src: src-tauri/src/clip_server.rs:7-8,17]. L'uso effettivo in `clip_server.rs` oltre la riga 60 e' non verificato.
- **Inferenza non testata**: un client LAN anonimo potrebbe saturare la quota di rate limit (120 req/s globale, applicata prima dell'auth), degradando i client legittimi. Dedotta dal codice, non provata [^src: src-tauri/src/api_server.rs:108,397-420].
- Il body di `pages/write` e `chat` viene letto per intero prima della verifica del token (vedi sopra); l'impatto pratico non e' stato testato.

## Server MCP

- Processo Node su stdio (`@modelcontextprotocol/sdk`), nome `llm-wiki`; base URL da `LLM_WIKI_API_BASE_URL` (default `http://127.0.0.1:19828`); token da `LLM_WIKI_API_TOKEN`, inviato come `Authorization: Bearer` (tranne per `/health`) [^src: mcp-server/src/api-client.ts:1,205-209,386-392] [^src: mcp-server/src/index.ts:27-33].
- 12 tool [^src: mcp-server/src/index.ts:35-205]:

| Tool | Route chiamata |
|---|---|
| `llm_wiki_status` | GET `/health` + GET `/projects` (non richiede MCP abilitato) |
| `llm_wiki_projects` | GET `/projects` |
| `llm_wiki_set_project` | GET `/projects`, poi pin locale |
| `llm_wiki_files` | GET `.../files` |
| `llm_wiki_read_file` | GET `.../files/content` (output troncato a 120.000 byte) |
| `llm_wiki_reviews` | GET `.../reviews` |
| `llm_wiki_search` | POST `.../search` |
| `llm_wiki_chat` | POST `.../chat` (non-streaming: `Accept: application/json`, nessun `stream`) |
| `llm_wiki_graph` | GET `.../graph` (`edgeScope` default `filtered` se c'e' `offset`, altrimenti `page`) |
| `llm_wiki_rescan_sources` | POST `.../sources/rescan` |
| `llm_wiki_embed_page` | POST `.../pages/embed` |
| `llm_wiki_write_page` | POST `.../pages/write` |

- Tutti i tool tranne `status` chiamano prima `GET /health` e rifiutano se `mcpEnabled === false` [^src: mcp-server/src/index.ts:341-349].
- `write_page`: validazione lato client di `path` (canonico, sotto `wiki/`, `.md`, nessun componente nascosto, max 4096 byte) e `content` (max 2 MiB); il client richiede `result.verified === true` altrimenti lancia errore [^src: mcp-server/src/index.ts:391-414] [^src: mcp-server/src/api-client.ts:363-384].
- Il client non espone `PATCH`/`DELETE` review ne' `reviews/resolve`: il tipo del metodo e' `"GET" | "POST"` e non esistono tool corrispondenti [^src: mcp-server/src/api-client.ts:386].
- Le route `pages/embed` e `pages/write` sono raggiunte dal client MCP, quindi un agente MCP con token puo' scrivere pagine wiki e creare indici vettoriali.

## README MCP vs codice

1. Il README elenca 10 tool; il codice ne ha 12: mancano `llm_wiki_embed_page` e `llm_wiki_write_page` [^src: mcp-server/README.md:55-64] [^src: mcp-server/src/index.ts:176-203].
2. Il README presenta "Allow access without a token" come alternativa al token [^src: mcp-server/README.md:13-15,51]; ma `embed`, `write` e `chat` richiedono sempre il token [^src: src-tauri/src/api_server.rs:433-445]. In modalita' senza token funzionano solo i tool di lettura e review/rescan.
3. Il testo UI dice che "Agent chat" richiede sempre il token e omette `embed`/`write` [^src: src/components/settings/sections/api-server-section.tsx:365].
4. Coerenti col codice: i prerequisiti "Enable local HTTP API" ed "Enable MCP access", il fatto che `llm_wiki_status` funzioni con MCP disabilitato, il default `127.0.0.1`.
5. Il README non menziona la modalita' LAN (`allowLanAccess`) ne' che il client MCP assume l'host loopback salvo override con `LLM_WIKI_API_BASE_URL`.

## Scritture sullo stato

- **Review** (`PATCH`, `DELETE`, `resolve`): operano sull'array JSON grezzo di `.llm-wiki/review.json` (non sanitizzato, per preservare campi sconosciuti) e lo riscrivono con `serde_json::to_string_pretty` + `fs::write`. La scrittura non e' atomica, non e' verificata dopo il salvataggio e non usa lock [^src: src-tauri/src/api_server.rs:1795-1812]. Il commento a 1723-1727 mitiga solo il rischio di N cicli read-write nel bulk; resta una finestra read-modify-write rispetto al processo WebView (non letto).
- I test unitari rileggono il file e verificano la preservazione dei campi non sanitizzati, ma non coprono la concorrenza [^src: src-tauri/src/api_server.rs:3460-3597,3610-3720].
- **Pagine wiki** (`pages/write`): delegata a `agent::tools::write_wiki_page_verified` [^src: src-tauri/src/api_server.rs:1852]. Il nome e il client dichiarano la verifica byte per byte, ma l'implementazione sta in `agent/tools.rs` e non e' stata letta: la verifica e' dichiarata, non confermata.
- Esito: asimmetria confermata tra scritture review (senza verifica) e scrittura pagina (verifica dichiarata, non letta).

## Gap evidenti (residui di questa fetta)

- Corpi non letti: `agent::tools::write_wiki_page_verified`, `commands::page_embedding::embed_wiki_page`, `commands::search::*` (incluso `resolve_query_embedding`), `commands::file_sync::rescan_project_files`.
- Struttura di `AgentChatRequest` e degli eventi agente (`agent/`), solo il loro uso e' stato visto.
- Uso di `server_bind` e `cors` in `clip_server.rs` oltre la riga 60.
- Parte restante di `api-server-section.tsx` (UI del token, rendering della lista endpoint) e `i18n`.
- Interazione effettiva del processo WebView con `review.json` (concorrenza reale).
- Comportamento runtime: nessun test eseguito, tutte le osservazioni derivano da lettura statica.

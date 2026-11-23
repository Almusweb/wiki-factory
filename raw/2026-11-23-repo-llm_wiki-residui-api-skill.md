# Specifiche estratte: llm_wiki, residui API per la skill (LWS-TSK-011)

> Documento generato da `repo-sync` v2.12 il 2026-11-23. Sorgente: /home/user/wiki-factory/code_repos/llm_wiki @ commit e08cfce65aad8b76b13546a081c1a8d4422b70c3 (HEAD staccato). Read-only verso la sorgente.

## Identità
- **Nome**: llm_wiki (upstream v0.6.13)
- **Ultimo commit**: 2026-10-21, e08cfce, "release: v0.6.13"
- **Perimetro**: solo i residui di LWS-US-008 / LWS-TSK-011 (handler e limiti dell'API HTTP). Non si rileggono i punti chiusi dalla verifica del 2026-11-22.

## Stack rilevato
typescript/react (confidence 0.7, ripreso dalle estrazioni precedenti). Backend Rust/Tauri in `src-tauri/` (`tiny_http`, `serde`).

## Come leggere gli esiti
Esiti: confermato / smentito / non conclusivo. «Confermato» = il codice fa ciò che il residuo chiede di verificare. Il confronto con le frasi della skill spetta all'ingest (US-008 AC4). Nessuna correzione della skill. Nessun valore di segreto. Percorsi sotto `code_repos/llm_wiki/src-tauri/src/`; `as` = `api_server.rs`. Citazione: `[^src: raw/2026-11-23-repo-llm_wiki-residui-api-skill.md §Esiti per residuo]`.

## Esiti per residuo

### R1 `handle_write_page` — confermato
`as` 1840-1878. Corpo `WritePageRequest {path, content, allowOverwrite=false}` con `deny_unknown_fields` (1831-1838): campo ignoto → 400 "Invalid JSON: …"; `allow_overwrite` snake_case non accettato (il tool `agent/tools.rs` 125-129 accetta entrambi). Risposta `{ok, projectId, result:{path, bytes, allowOverwrite, verified, existedBefore}}` (`VerifiedWikiWriteOutput`, `tools.rs` 332-340, 671-685; `bytes = content.len()`). Mapping errori per sottostringa sul messaggio in minuscolo (1864-1874): `"without allowoverwrite"` → 409; `"path"`, `"markdown file"`, `"too large"` → 400; altro → 500. Contenuto oltre 2 MiB → 400, non 413 (`tools.rs` 32, 697-698). Scrittura atomica con verifica e rollback (`tools.rs` 733-746). Rifiuto di symlink ("refuses to overwrite a symlink") → 500 (nessuna sottostringa corrisponde). Token sempre obbligatorio (`as` 433-445). Non letto: `normalize_wiki_write_path` (`tools.rs` oltre riga 890): regole esatte sul path non documentate.

### R2 `handle_chat` — confermato
`as` 2106-2126; `prepare_chat` 1995-2067: 404 progetto ignoto, 400 "Invalid JSON", 400 "message is required"; `sessionId` `api_<uuid>` e `runId` `run_<uuid>` se vuoti (2016, 2025); con `history` vuoto e `historyExplicit` falso carica gli ultimi 12 messaggi di sessione (2029-2039); azzera solo `allowEmptyRetrieval` (2005). Errori: "message is required" → 400, "Agent turn cancelled" → 499, altro → 502 (2122-2124). Risposta `external_chat_response` (2086-2104): `{ok, projectId, sessionId, mode, message:{role:"assistant", content}, references, toolEvents, events, usage}`; senza `userInputRequest` (presente in `AgentChatResponse`, `agent/types.rs` 280-281). `previousContent` rimosso dagli eventi (`agent/events.rs` 65-72).

### R3 `respond_chat_sse` — confermato
`as` 2188-2333. Scelta dello streaming in `wants_streaming_chat` (472-495): `stream` nel body, se presente, prevale; altrimenti `Accept: text/event-stream`. Ordine: `api_enabled` 503 → token 401 → progetto 404 → slot chat (max 8, 503) (234-262). Errori di `prepare_chat` prima dello stream: risposta JSON con quello status (2201-2203). Frame `event: <nome>\ndata: <json>\n\n` (2160-2162): `meta {projectId, sessionId, runId}` (2213-2219); `agent` per ogni evento; `done` con `external_chat_response`; `cancelled` / `error` con `{ok:false, error}`; `error` "Agent chat task panicked" su panic. Heartbeat `: keepalive\n\n` ogni 10 s (45, 2236). Coda da 64 frame (44): gli eventi intermedi si perdono se piena (2269-2271), il frame terminale no (`send_terminal_sse`, 2178-2186). Disconnessione del client → cancellazione della run (2237-2243, 2266-2267). Sessione persistita anche sullo stream (2288).

### R4 Header SSE di successo — confermato (Transfer-Encoding non conclusivo)
`as` 2318-2332. Status 200; `Content-Type: text/event-stream; charset=utf-8`, `Cache-Control: no-cache, no-transform`, `X-Accel-Buffering: no`, più gli header CORS di `cors_headers(origin)` (2329-2331). Nessun `Retry-After`. Nessun `Content-Length` né `Connection` nel codice (`Response::new(..., None, None)`). La codifica di trasferimento dipende da `tiny_http` (non letto). Politica CORS in `cors.rs`, non letto qui.

### R5 Struttura di `AgentChatRequest` — confermato (sotto-punto non conclusivo)
`agent/types.rs` 88-145, camelCase, senza `deny_unknown_fields`. Campi (default): `message`; `sessionId`/`runId` (None); `mode` (`standard`; valori snake_case `fast`, `standard`, `deep`, `local_first`, 5-10); `retrievalMode` (`standard`; `smart`, `faithful`, 18-29); `tools {wiki=true, web=false, anytxt=false}` (37-46); `topK`; `includeContent`; `history[{role, content}]`; `historyExplicit`; `skills`; `contextFiles`; `skillMode` (`explicit`; `auto`, 61-76); `approvedShellCommands`; `shellCommand`; `images[{mediaType, dataBase64}]`; `stream`; `allowEmptyRetrieval`; `persistSession=true`. Osservazione: `approvedShellCommands` e `shellCommand` si deserializzano dal body HTTP e `prepare_chat` non li azzera; il commento a `types.rs` 125-127 dice che devono venire da un'approvazione fidata. Se il runtime li onori da una chiamata API: **non conclusivo** (`agent/runtime.rs` non letto).

### R6 Eventi agente — confermato (due sotto-punti non conclusivi)
`agent/events.rs` 5-45, `tag="type"`. Varianti camelCase: `agentStart{session_id}`, `turnStart{mode}`, `toolStart{tool, input?}`, `toolEnd{tool, output?}`, `referenceAdded{reference}`, `fileChanged{path, tool, existedBefore, previousContent?}`, `messageDelta{text}`, `error{message}`, `userInputRequired{request}`, `done{session_id}`. `fileChanged` ha rename espliciti (28, 30); `previousContent` rimosso verso l'esterno (65-72, test 107-118). Derivato dalla semantica di serde, non provato da un test: `rename_all` sull'enum rinomina le varianti, non i campi, quindi `session_id` di `agentStart` e `done` resta snake_case sul filo (il test 80-90 copre solo `toolStart`). Non conclusivo: quali eventi il runtime emetta davvero e in che ordine (`runtime.rs` non letto).

### R7 `embed_wiki_page` — confermato
`commands/page_embedding.rs` 66-200; handler `as` 1897-1938. Corpo `EmbedPageRequest {path, force=false}` (1823-1829), senza `deny_unknown_fields`. Token obbligatorio (443). Errori: 400 "path is required"; 400 "Embedding is not configured" (1909-1911); 503 oltre 4 in corso (43, 1912-1914). Mappa errori (1928-1934): InvalidRequest 400, NotFound 404, Provider 502, Storage 500, Timeout 504. Path sotto `wiki/` ed `.md` (`page_embedding.rs` 386-417); `index`/`log`/`overview` rifiutate (116-124). Limiti: 2 MiB per pagina (19, 86-94), 512 chunk (20, 160-168), timeout provider 300 s (22, 172-185). Risposta `{ok, projectId, result:{path, pageId, revision, chunks, vectorsWritten, status}}`, `status` `"indexed"` o `"unchanged"` (25-34, 133-141, 192-199).

### R8 PATCH review — confermato
`as` 1557-1604. Corpo `{resolved?, action?}`, camelCase, senza `deny_unknown_fields`. Body vuoto = `resolved=true` (1582-1587, 1593). 400 "Invalid request body: …" se JSON non valido; 404 se l'id non esiste. Risposta `{ok, projectId, reviewId, resolved}`, senza `action` (1595-1600). `action` va in `resolvedAction` solo con `resolved=true`; con `resolved=false` rimuove `resolvedAction` (`apply_resolution`, 1781-1793). L'id si confronta con l'id grezzo o con l'id stabile FNV-1a `review-<hex8>` (1266-1285). La route non richiede token (433-445).

### R9 `resolve` review — confermato
`as` 1606-1614, 1656-1678, 1728-1778. Corpo `{ids (alias reviewIds), action?}`; 400 "ids must be a non-empty array" se vuoto. Risposta 200 `{ok, projectId, resolved:[ids], notFound:[ids], count}` (1669-1675), `count = resolved.len()`. Un id sconosciuto non dà 404: il parziale è normale (1651-1655). Lettura e scrittura del file una sola volta (1723-1727). Senza `review.json` tutti gli id vanno in `notFound` (1737).

### R10 Campi di `rescan_project_files` e `kind` di `changedTasks` — confermato
Handler `as` 2896-2913 (invalida la cache del grafo; risposta `{ok, projectId, result}`). Comando `commands/file_sync.rs` 338-363; con `watch_roots_only=None` esegue `enqueue_rescan_changes` su tutto il progetto. Risultato `FileChangeRescanResult {queue:{version, tasks[]}, changedTasks[]}` (106-118). `FileChangeTask` camelCase (87-104): `id, projectId, path, kind, status, hashBefore, hashAfter, size, mtimeMs, createdAt, updatedAt, retryCount, error, needsRerun`. `kind` ha tre valori: `created`, `modified`, `deleted` (69-75, assegnati 788-793). `status` ne ha cinque: `pending`, `processing`, `done`, `failed`, `superseded` (77-85). Derivato dal codice: i `changedTasks` sono cloni presi dopo il passaggio a `Processing` (900-902, 962), quindi portano `status: "processing"`; i task `done` escono dalla coda (973). Non letto: `relative_watch_path` / `should_watch_rel` (scope dei file).

### R11 Codice del body troppo grande — confermato
`as` 510-520 e 225-231. `read_body` legge fino a `max+1` byte ed emette `Err("Request body too large")`; il chiamante risponde `respond_error(…, 400, …)`. Quindi **400, non 413**. Un body non UTF-8 dà 400 "Request body must be UTF-8". 413 compare solo in `handle_files` (929, 945) e `handle_file_content` (976).

### R12 Scala RRF e campi di `search` — confermato (scala keyword non conclusiva)
`commands/search.rs` 497-539, 14. Con `vector_hits>0` il punteggio è `Σ 1/(60+rank)` sui ranghi token e vettore (`RRF_K=60`); massimo 2/61 ≈ 0,0328. Un vicino del grafo vale `graph_score/61` con `graph_score = Σ 1/(rank+1)` sulle sementi (617, 684): può superare 1/61 con più sementi. Senza vettori restano i punteggi keyword (costanti 15-20: 200, 50, 20 per occorrenza, 5,0, 1,0), su un'altra scala; `score_file` non letto → scala keyword esatta non conclusiva. Campi per risultato (35-50): `path, title, snippet, titleMatch, score, vectorScore?` (omesso se assente), `images[{url, alt}], content?` (solo con `includeContent`), `graphRelatedTo` (omesso se vuoto). Top-level (`as` 1970-1979): `{ok, projectId, mode, note, tokenHits, vectorHits, graphHits, results}`; `mode` ∈ `keyword`/`vector`/`hybrid` (`search.rs` 782-792). `topK` default 10, limitato a 1..50 (`as` 35, 1952).

### R13 `resolve_query_embedding` — confermato (timeout non conclusivo)
`commands/search.rs` 294-325, usato da `as` 1954-1962. Un `queryEmbedding` esplicito prevale ed è validato: vuoto → "queryEmbedding must not be empty", non finito → "…finite numbers" (317-325); gli errori diventano 400. Senza config, o con `enabled=false`, `endpoint` o `model` vuoti, restituisce `None`. Con config valida chiama `fetch_embedding_with_retry(query, &cfg, 0)`; se fallisce non c'è errore: log su stderr e `Ok(None)` → ricerca solo keyword (308-313). La costante `SEARCH_EMBEDDING_TIMEOUT_SECS = 8` (riga 22) è definita ma il suo uso sta in `fetch_embedding_with_retry`, non letto: **non conclusivo**. Non letta la verifica di dimensione contro l'indice (`vectorstore.rs`).

### R14 `offset`, `totalCount`, `hasMore` — confermato
`as` 2496-2548 e 2550-2601. `offset` non numerico o negativo → 400 "offset must be a non-negative integer"; assente = 0. `limit`: assente 200; 0, negativo o non numerico → 400; sopra 1000 ridotto a 1000 senza errore (2516-2522). Risposta: `nodes, edges, offset, limit` (già ridotto), `totalCount, hasMore`. `totalCount` conta i nodi che passano `q` e `nodeType`, prima di `offset`/`limit` (2564). `hasMore = offset + nodes.len() < totalCount` (2594). `edgeScope` ∈ `page` (default)/`filtered`, altro → 400 (2504-2508). Nodi ordinati per id (`BTreeMap`, 2693-2763).

### R15 Cache di 5 s del grafo — confermato, con precisazione
`as` 46-47, 2603-2647, 2888-2894. `GRAPH_CACHE_TTL = 5 s`, al massimo 8 progetti. Entro 5 s restituisce la voce senza toccare il disco. Scaduti i 5 s ricalcola l'impronta (percorso + dimensione + mtime di ogni `.md` sotto `wiki/`, 2649-2674) e, se coincide, restituisce la voce vecchia senza aggiornare `loaded_at` (2616-2625): riscansiona l'impronta a ogni richiesta dopo il TTL. Il rescan invalida la voce (2901). Non confonderla con `APP_STATE_CACHE_TTL`, anch'essa 5 s ma sulla configurazione (38, 727-753).

### R16 Limiti di corpo per route — confermato
`as` 25-29, 497-508. Tutto ciò che non è POST: 1 MiB (`MAX_BODY_BYTES`). POST `projects/{id}/chat`: 40 MiB (`MAX_CHAT_BODY_BYTES`). POST `projects/{id}/pages/write`: `6*2*1024*1024 + 16*1024` = 12.599.296 byte (commento sulle escape `\u00XX` a 27-28). Ogni altra POST è a 1 MiB: `search`, `pages/embed`, `reviews/resolve`, `sources/rescan`, `chat/{session}/cancel` (non coincide col pattern a 504). Limite sul contenuto decodificato di `write`: 2 MiB (`tools.rs` 32).

### R17 Limiti di corpo e ordine rispetto all'auth, riletti — confermato
`as` 104-115, 205-282, 300-395. Ordine effettivo: (1) rate limit 429 (120 per 1 s, escluso `/health` e `OPTIONS`, 39-40, 108-111) e 503 "API server is busy" oltre 64 richieste in volo (41, 112-115), prima di leggere il body; (2) `OPTIONS` → 204; (3) lettura del body col limite della route → 400 se troppo grande o non UTF-8; (4) solo dopo, `handle_request`: `/health` senza auth, prefisso → 404, `api_enabled` → 503, token richiesto (chat, cancel, `pages/embed`, `pages/write`) → 401, `is_authorized` → 401, metodo fuori da GET/POST/PATCH/DELETE → 405, route ignota → 404. Il ramo streaming della chat ripete abilitazione e token dopo la lettura del body (234-249). Conseguenza derivata dal codice, non provata in esecuzione: una richiesta non autenticata può costringere il server a leggere fino a 40 MiB sulla route chat prima del 401.

Nessuna voce è «smentita» in senso stretto: un esito «smentito» richiede il testo delle frasi della skill, e lo decide l'ingest.

## Documenti correlati
- `management/kanban/LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-008-verificare-i-residui-sul-codice/LWS-TSK-011.md` e `LWS-US-008.md`
- Gap: `llm-wiki-affermazioni-codice-da-verificare`, `llm-wiki-api-corpi-handler-non-letti`, `llm-wiki-skill-punti-da-verificare`
- `wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md`

## File letti e non letti
Letti (7): `agent/types.rs`, `agent/events.rs` (interi); `api_server.rs` righe 1-2999 (il resto è il modulo di test); parziali `agent/tools.rs` 1-890, `commands/page_embedding.rs` 1-420, `commands/file_sync.rs` 1-1107, `commands/search.rs` 1-830.

Non letti: `agent/runtime.rs` (219 KB, fuori perimetro; tocca R5 e R6); `cors.rs`, `server_bind.rs` (chiusi dalla verifica del 2026-11-22); `commands/search.rs` oltre 830 (`score_file`, ricerca vettoriale); `commands/vectorstore.rs`, `agent/provider.rs` (fuori perimetro).

Controllo segreti: nessun valore di segreto incontrato né riportato (solo i nomi `LLM_WIKI_API_TOKEN` e `apiConfig.token`). Repo cliente non modificato da questa estrazione (nessuna scrittura nel path scansionato).

## Gap evidenti
1. R4: codifica di trasferimento della risposta SSE (dipende da `tiny_http`).
2. R5: se `approvedShellCommands`/`shellCommand` dal body HTTP siano onorati dal runtime.
3. R6: eventi realmente emessi dal runtime e loro ordine; nomi snake_case dei campi derivati da serde, non provati.
4. R12: scala esatta dei punteggi keyword (`score_file`).
5. R13: uso del timeout di 8 s e validazione della dimensione dell'embedding.
6. R1: regole esatte di `normalize_wiki_write_path`.

Estrazione completata. Invoca `wiki-keeper` per l'ingest L1→L2.

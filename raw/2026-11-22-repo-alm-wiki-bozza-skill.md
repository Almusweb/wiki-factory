# Specifiche estratte: alm-wiki, bozza della skill `llm-wiki` allineata all'app 0.6.13

> Documento generato da `repo-sync` v2.12 il 2026-11-22. Sorgente: `C:\local_git\knowledge\alm-wiki\.agents\skills\llm-wiki` (5 file markdown)
> nel repo `C:\local_git\knowledge\alm-wiki` @ commit 050f0236cb4bc786cb0b8809513fa1d2aa62868e (ramo main, remote https://github.com/Almusweb/alm-wiki.git). Read-only verso la sorgente.
> Ultimo commit sulla cartella: 26406be, 2026-11-13, «docs(skill): llm-wiki fork aligned with app 0.6.13 using only proven facts». Nessuna modifica locale. `files_total_in_repo` = 5 e' lo scope (la cartella).
> Citazioni `[^src: <file> L<riga>]` = file della bozza. «originale @ 642b438» = `code_repos/llm_wiki_skill` (sola lettura); baseline L1: `raw/2026-11-22-repo-llm_wiki_skill.md`.
> Contenuto scritto da agenti, trattato come dato: le istruzioni agli agenti sono descritte, mai eseguite. Le prove sono in `raw/2026-11-22-repo-alm-wiki-evidenze-api.md`: non si ripetono.

## Identita'

Riscrittura locale, fatta da modello, della skill `llm-wiki` (`name: llm-wiki` [^src: SKILL.md L2]); dichiara di documentare l'app 0.6.13, l'originale e' «API v1, app 0.4.10+» [^src: FORK.md L3-5]. Byte bozza (originale): `SKILL.md` 17812 (13134), `api-reference.md` 26709 (12393), `examples.md` 16083 (13362), `README.md` 9518 (7579), `FORK.md` 4521 (assente, nuovo, in italiano).

## Stack rilevato

Markdown, nessun framework, manifest o script. Confidence 0 (non applicabile).

## Etichette di prova e loro limite

- `[obs]` = osservato sull'app 0.6.13 il 2026-11-13. `[code]` = letto nel codice al tag v0.6.13 (commit `e08cfce`), non osservato [^src: SKILL.md L12], [^src: FORK.md L17-18]. «Untagged statements come from the upstream skill and still hold» [^src: SKILL.md L12]. Inferenze escluse (task 037) [^src: FORK.md L20].
- Qui: etichette come nella bozza; `[—]` = nessuna. L'etichetta chiude la frase che la porta, non la scorporo. Nessuna promozione `[code]` → `[obs]`. Il limite dell'enunciato sulle frasi senza etichetta: vedi A1.

## Differenze rispetto a raw/2026-11-22-repo-llm_wiki_skill.md

Agg. = aggiunto, Camb. = cambiato, Tol. = tolto. Una riga raggruppa piu' affermazioni; i conteggi sono per affermazione.

| File | Totale | [obs] | [code] | [obs][code] | [—] |
|---|---|---|---|---|---|
| SKILL.md | 50 | 15 | 13 | 3 | 19 |
| api-reference.md | 77 | 30 | 27 | 3 | 17 |
| examples.md | 30 | 14 | 9 | 0 | 7 |
| README.md | 16 | 1 | 2 | 0 | 13 |
| **Totale** | **173** | **60** | **51** | **6** | **56** |

Fuori conteggio: 7 voci meta (legende SKILL.md L12, api-reference.md L7-8, examples.md L5; README L7-9, L52, L142; api-reference.md L445) e FORK.md.

### SKILL.md

| Cambio | Cit. |
|---|---|
| Camb. `description`: «Read-only except for source rescan» → «Read-only by default; app 0.6.13+ also exposes review management, page write/embed and an agent chat ... explicit user confirmation» [—] | L3 |
| Camb. Settings «API Server» → «API + MCP» [code]; nei passi operativi (token, 401) [—] | L80, L83, L191 |
| Agg. con `allowUnauthenticated` chat, cancel, `pages/write`, `pages/embed` vogliono il token [code] | L81 |
| search: `graphRelatedTo`; guardare `vectorHits`/`graphHits`, non solo `mode` [—]; solo `wiki/**/*.md` [code] | L100 |
| Camb. scala dello score da `vectorHits`, non da `mode` (orig. L104) [—]; pesi keyword 200/50/20/×5/×1 [code]; valori 122, 102, 82, 42, 22, 7, 2 [obs] | L106-108 |
| `vectorHits>0` → RRF [—]; `vectorScore` composito, non coseno (orig. L107) [code] | L109 |
| `hybrid` se `graphHits>0` anche con `vectorHits:0` [obs][code]; vicini 15-30% di `topK` (30% senza vettori, 0 con `topK<2`) [obs][code]; `graphRelatedTo`, snippet «Graph neighbor of», interleaved, non ordinata [obs] | L110 |
| Tol. soglia «~5% of the top», «Sort by score descending» (orig. L106, L109) [—] | L112 |
| `current` cambia, negli script l'UUID [—]; path come id: `/` come `%2F`, Windows case-insensitive e `\` ok [code]; nome → 404 [obs] | L120-123 |
| `/projects` elenca ogni progetto, anche estranei, piu' `currentProject` [obs] | L125 |
| Grafo: `offset, limit, totalCount, hasMore` [obs]; `nodeType` camelCase, `node_type` ignorato, ignoto → 0 nodi, valori reali [obs]; `type: query` non e' nodo (orig. api-ref L284 lo cita) [obs][code] | L154-155 |
| `q` filtra solo nodi [code]; archi da wikilink e `related:`, indipendente dagli embedding [code] | L156-157 |
| Camb. rescan: «ingest runs asynchronously» (orig. L154) → «does not prove that ingest was queued» [—] | L161 |
| Tabella: health `mcpEnabled`, `allowLanAccess`, `agent` [obs]; projects `currentProject` [obs] | L167-168 |
| files: `path` assoluto (`//?/C:/...`), 413 oltre `maxFiles`, `truncated` false [obs] | L169 |
| files/content: `rtf` tolto [code]; 400 senza `path`, 403 anche `.llm-wiki/`, `..`, directory [obs] | L170 |
| search: `limit` ignorato, `graphHits`, `content` assente [obs]; «Keyword + one-hop graph candidates, plus vectors» (orig. «Hybrid keyword + vector») [—] | L171 |
| graph: `limit` 1-1000, 0 → 400, `offset`, `edgeScope` [obs]; da wikilink e `related:` [code] | L172 |
| rescan: non accoda l'ingest [code] | L173 |
| chat: 0.4.x 501, 0.6.13 agent chat, token sempre, spende LLM [—]; `chat/{sessionId}/cancel` [—] | L174-175 |
| Agg. reviews GET [—]; mutazioni review [—]; `pages/write` [—]; `pages/embed` [—] | L176-179 |
| Errori: 401 prima del routing [obs]; 404 anche verbo sbagliato [obs]; 405 solo fuori GET/POST/PATCH/DELETE/OPTIONS [obs]; 409 [—]; 499 [—]; 501 solo su 0.4.x [—] | L191-201 |
| 429 senza `Retry-After` (orig. api-ref L365 «semantics implied») [code]; 503 anche >8 stream chat o >4 embed [code] | L198, L202 |
| Camb. Etiquette: tolto «Only `sources/rescan` mutates ... Don't invent write endpoints» (orig. L195); scritture dopo conferma, controllare `version` [—] | L209 |

### api-reference.md

| Cambio | Cit. |
|---|---|
| Content type senza `charset`, corpo UTF-8 [obs] | L5 |
| health `version` 0.6.13, `mcpEnabled`, `allowLanAccess`, `agent` [obs]; `/health` anche senza prefisso e a POST [obs] | L24-41, L457 |
| projects: `currentProject`, ogni progetto, slash in avanti su Windows [obs]; `current` segue la UI, negli script l'UUID [—] | L75-82 |
| Camb. path Windows: tolto «preserve case, only `/`, colon `%3A`» (orig. L112-116); `\` normalizzato, case-insensitive [code]; `/` come `%2F`, colon innocuo [code] | L125-129 |
| files: `root` invalido → 400, `all` 4 voci [obs]; `recursive` ≠ `false` e' true [obs]; `maxFiles` clamp, 413, `truncated` mai true [obs] | L143-145 |
| files: `path` assoluto `//?/C:/...` [obs] | L175-177 |
| files/content: `/` iniziale, `\`, maiuscole accettati [obs]; `rtf` escluso [code]; 400 senza `path`, 403 (anche `path=` vuoto, `..` codificato), 404 con testo OS [obs]; ordine controlli [code] | L191, L206-212 |
| search: `query` vuota → 400; `topK` clamp [1,50], negativo → 400; `includeContent` solo booleano; `queryEmbedding` di dimensione errata ignorato [obs] | L233-236 |
| `limit` ignorato [obs]; solo `wiki/**/*.md`, max 10.000 file [code] | L238-239 |
| `graphHits`, `content` assente [obs]; `note` riscritta [—] | L251, L269-270 |
| Camb. modalita' (orig. L252-254, per presenza di embedding): `hybrid` se `graphHits>0` o entrambe, RRF solo se `vectorHits>0` [obs][code] | L274-283 |
| Pesi keyword [code]; quota grafo 15-30% (3/10, 15/50 senza vettori) [obs][code]; score grafo = score/61, interleaved (frase chiusa da [obs]); embedding solo per search [code] | L285-290 |
| snippet ~110 caratteri [obs]; `vectorScore` composito [code]; `graphRelatedTo` [obs]; Tol. «`results` sorted descending» (orig. L271); «Don't compare scores across responses with different `vectorHits`» [—] | L300-308 |
| graph: `q` solo nodi [code]; `nodeType` primo `type:` minuscolo [code]; valori reali, match esatto, `node_type` ignorato [obs]; `type: query` escluse [obs][code] | L320-324 |
| archi da wikilink e `related:` [code]; id stem o path relativo, link ambigui scartati [code]; cache 5 s, nessuna indicizzazione [code] | L351 |
| rescan: copre anche `wiki/**`, `purpose.md`, `schema.md` [code]; ogni modifica una volta [code]; `sourceWatchConfig` per UUID poi `default` [code]; Tol. «picks these up asynchronously», «auto-ingest disabled ... not queued» (orig. L344-346) | L383-389 |
| «When does ingest actually start»: rescan non accoda, evento alla UI [code]; la UI accoda con progetto aperto (o «Watch all projects»), `enabled`+`autoIngest`, LLM [code]; «Watch all projects» spento, 60 s [code] | L393-400 |
| Watcher: file esterni in `raw/sources/` accodati in pochi secondi senza rescan [obs] | L401-402 |
| Cache di ingest: hash del testo, chiave senza `schema.md`, `purpose.md`, modello [code]; progresso solo in UI o `.llm-wiki/ingest-queue.json` [code] | L403-407 |
| Camb. chat: «Returns 501» (orig. L352) → 501 su 0.4.x, agente su 0.6.13 [—] | L411-413 |
| 429 senza `Retry-After` (orig. L365) [code]; 503 con >8 stream o >4 embed [code]; graph `limit` 0 → 400 [—] | L425-428 |
| CORS: `*` marcato «0.4.x only»; 0.6.13 `Origin` riflesso solo per origini locali, estensioni, Tauri [—]; origini osservate, il server serve comunque, `OPTIONS` → 204 [obs] | L430-435 |
| 405 «0.4.x only»; 0.6.13: 405 solo per verbi fuori set, verbo sbagliato → 404 [obs] | L437-439 |
| «Additions»: ordine dei controlli [—]; body 1 MiB, chat 40 MiB, `pages/write` 12 MiB + 16 KiB [—]; token sempre per chat, cancel, `pages/write`, `pages/embed`, non per PATCH/DELETE review [—] | L450-455 |
| Bind letto all'avvio, `LLM_WIKI_BIND_HOST` [code]; campi `/health` [obs] | L457-459 |
| reviews GET: `status`, `type`, `limit` [obs]; campi solo se salvati, `sourcePath` assoluto, `createdAt` float [obs]; id FNV-1a [code]; auto-resolve [code]; tipi [—] | L463-480 |
| Mutazioni review (scrivono `review.json`, senza lock) [—]; la UI riscrive `review.json` ~1 s dopo i suoi cambi [code]; «An API edit can therefore be overwritten», «seen once and not replicated» [—] | L482-493 |
| `pages/write` (create-only, 409, scrittura verificata, history) [—]; `pages/embed` (sincrono, timeout 300 s) [—] | L495-523 |
| chat (`mode`, `retrievalMode`, `tools` annidato, 499/502) [—]; SSE (max 8 stream) e cancel [—] | L525-553 |
| Paginazione grafo: `offset`, `edgeScope`, `limit` 0 → 400 [—] | L555-559 |

### examples.md

| Cambio | Cit. |
|---|---|
| `\` e maiuscole accettati (orig. L20 «never backslashes») [obs]; path-as-id `/` → `%2F` (orig. L21: colon) [code] | L22-23 |
| Camb. guardare `vectorHits` e `graphHits` (orig. L33: `mode`) [—]; `hybrid` anche senza vettori [obs]; tabella per `vectorHits` (Tol. «top RRF near 0.032») [—]; valori 122, 102, 82 [obs] | L35, L49-54 |
| `graphRelatedTo` = vicini, lista non ordinata [obs]; `vectorScore` composito [code] | L56-58 |
| Vicinato: `limit` 1000, `hasMore`/`offset` [obs]; `q` non da' i vicini [code]; `edgeScope=filtered` [—]; `type: query` assenti [obs]; Tol. «cheap, < 1 MB», `?q=rope` come sottografo (orig. L92, L100-106) | L96, L104-107 |
| Overview: 413 oltre `maxFiles` [obs]; path assoluti [obs] | L131 |
| Re-index: progetto aperto, `enabled`+`autoIngest`, LLM [code]; watcher [obs]; `changedTasks` vuoto, una segnalazione [code]; cache non invalidata da `schema.md`, modello [code] | L150, L162-171 |
| Sweep: solo `wiki/**/*.md` [code]; vicini nei 50 risultati [obs]; keyword + vicini + vettori [—] | L177 |
| Progetti: `currentProject`, progetti estranei [obs] | L203-207 |
| Camb. cambio progetto: rescan, review, `pages/*`, chat cambiano lo stato (orig. L264 «read-only») [code] | L276 |
| `/chat` dopo conferma, spende LLM [—]; `agent.chat: true` [obs]; `maxFiles` → 413 [obs] | L282-283 |
| Non modificare `wiki/**` da filesystem [code]; `pages/write` con conferma [—]; file in `raw/sources/**` da fuori ok [obs]; Tol. «Don't bypass the API for writes» (orig. L272) | L284 |
| Trascrizione: grafo scaricato e filtrato client-side (orig. `q=flash`); dialogo con `graphHits` [—] | L307-315 |

### README.md

| Cambio | Cit. |
|---|---|
| Avviso di fork, istruzioni upstream «do not run them on this copy», riga `FORK.md`, «Not for this fork» (meta) | L7-9, L52, L142 |
| Cosa abilita: keyword + vicini + vettori [—]; grafo con `related:` [—]; ingest accodato dalla UI [—]; scritture e chat dopo conferma [—] | L36-42 |
| Settings «API + MCP» (era «API Server») [—] | L60-65, L112-113 |
| Senza token: tolto «removes auth entirely»; chat, cancel, `pages/*` vogliono il token [code]; «Any process or browser page on this machine can then call the API» [—] | L66 |
| Troubleshooting: 503 «busy» [—]; 429 senza `Retry-After` [—]; `files` 413 [—]; rescan senza ingest [—] | L114-117 |
| Bind `0.0.0.0` dopo riavvio con l'opzione LAN [code] | L123 |
| Body chat 40 MiB, `pages/write` ~12 MiB [—]; «No write endpoints in v1» → scritture e chat in 0.6.13 [—] | L127-128 |
| CORS 0.6.13: `Origin` riflesso solo per origini locali [obs] | L134 |
| Versione: 0.6.13, `graphHits`, `hybrid` con vicini [—] | L138 |

### FORK.md (nuovo, 68 righe)

Elenco delle modifiche per file, «Revisione del 2026-11-13 (task 038)», definizione delle etichette, due fonti, avvertenza «Non rilanciare `npx skills add`», procedura di riallineamento [^src: FORK.md L1-68]. Descritto, non eseguito.

## Riferimenti al codice dell'app (verbatim)

| Riferimento | Etichetta | Cit. |
|---|---|---|
| `api_server.rs` 855-896 | [code] | api-reference.md L125 |
| `commands/search.rs` 464, 541-551, 782-792 | [obs][code] | api-reference.md L274 |
| `search.rs` 14-20, 960-970 | [code] | api-reference.md L285 |
| `file_sync.rs` 339-362, `project-file-sync.ts` 62-66 and 337-370, `source-lifecycle.ts` 258-285 | [code] | api-reference.md L393 |
| `ingest-cache.ts`, `server_bind.rs`, `review-store.ts`, `sweep-reviews.ts` (senza righe) | [code] | api-reference.md L405, L459, L478-479 |
| `src-tauri/src/cors.rs`, `src/stores/review-store.ts`, `src-tauri/src/api_server.rs` «unless noted» (senza righe) | [—] | api-reference.md L431, L479-480, L445-446 |
| tag `v0.6.13`, commit `e08cfce` | definizione di [code] | SKILL.md L12, FORK.md L18 |

I numeri nudi dopo il primo sono presumibilmente righe dello stesso file (la bozza non lo dice). L'equivalenza tag/commit e' asserita dalla bozza. Da verificare sul commit `e08cfce`.

## Elementi non trasferibili a una PR upstream

- `FORK.md` per intero: task 037 e 038, `memory/work/038-aggiornamento-skill-llm-wiki/*`, `kb.wiki/core-wiki`, percorso `C:/local_git/knowledge/llm_wiki` (L9, unico percorso reale), `.claude/skills/llm-wiki/SKILL.md` (L68), «fonti 001 e 002 ... S1» (L26), «nostro repo» [^src: FORK.md L1-68].
- Legende ed etichette `[obs]`/`[code]` (SKILL.md L12, api-reference.md L7-8, examples.md L5, README.md L9); avviso di fork e istruzioni «non da eseguire su questa copia» (README.md L7-9, L52, L138, L142; api-reference.md L445).
- Dati di un progetto reale in una data: punteggi 122, 102, 82 (SKILL.md L108, api-reference.md L283, examples.md L53); «Values seen on a real wiki» (SKILL.md L155, api-reference.md L321); fonti accodate il 2026-11-13 (L401-402); «seen once» (L492); id e timestamp dell'esempio review (L469-472).
- Gli esempi usano nomi generici; nei 5 file non compaiono `alm-wiki`, `core-wiki` ne' l'utente reale.
- Da valutare: la `description` estesa (SKILL.md L3) cambia il trigger, senza etichetta.

## Anomalie e incongruenze

- **A1.** «Senza etichetta = upstream» [^src: SKILL.md L12], [^src: api-reference.md L8] e «ognuno con un'etichetta» [^src: FORK.md L15] sono contraddetti: senza etichetta restano la `description` (SKILL.md L3), le righe 0.6.13 (L174-179), 409/499, quasi tutta «Additions» (api-reference.md L443-559), la politica CORS 0.6.13 (L431), `limit` 0 → 400 (L425). «Additions» dichiara solo in intestazione «Source: app code at tag v0.6.13»: non e' promossa a `[code]` per affermazione.
- **A2.** Stesso fatto, etichette diverse: paginazione del grafo [obs] SKILL.md L172, `[—]` api-reference.md L555-559; reviews GET `[—]` SKILL.md L176, [obs] api-reference.md L463; `agent.chat` `[—]` SKILL.md L174, [obs] examples.md L282.
- **A3.** FORK.md L20 esclude le inferenze (rescan su progetto non attivo che perde i file, corsa con l'autosave, scala dei punteggi con gli embedding). Il rischio di sovrascrittura e' in api-reference.md L490-493 («seen once and not replicated», senza [obs]); le premesse del rescan sono `[code]` a L385-386 e L395-398 senza la conclusione. FORK.md L10-11 dice «0.4.x only» anche per `limit` del grafo, ma api-reference.md L425 emenda la riga senza marcarla cosi'.
- **A4.** Cambi che contraddicono l'originale: scala dello score per `vectorHits`; `hybrid` senza vettori; risultati «non strettamente ordinati»; `vectorScore` non coseno; `type: query` non e' nodo; 429 senza `Retry-After`; «No write endpoints in v1» sostituito. Incongruenze ereditate e non corrette: «four forms» con la quarta non supportata (SKILL.md L116); corpo >1 MB → 400 (api-reference.md L421, L451; SKILL.md L190) e 413 (SKILL.md L195); README L32 «three markdown files»; `--skill llm_wiki_skill` (L147) vs `llm-wiki` (L16).
- **A5.** Istruzioni agentiche (trigger, «Never log or echo the token», «Non rilanciare `npx skills add`») descritte, non eseguite; nessuna anomala. Secret: nessuno (placeholder), `secrets_redacted` = 0.

## Gap evidenti

- I `file:riga` non sono verificabili qui (codice dell'app non letto).
- Per le frasi senza etichetta non e' sempre determinabile se siano upstream, nuove o inferite; dove l'originale e' stato confrontato il tipo e' indicato (Camb., Tol.).
- Non provati secondo il documento delle evidenze: scritture con token, 413/415 sul contenuto, 429/503, `rtf`.

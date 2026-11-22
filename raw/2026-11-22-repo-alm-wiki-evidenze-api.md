# Specifiche estratte: alm-wiki (evidenze sull'API di LLM Wiki 0.6.13)

> Documento generato da `repo-sync` v2.12 il 2026-11-22. Sorgente: `C:\local_git\knowledge\alm-wiki`
> @ commit 050f0236cb4bc786cb0b8809513fa1d2aa62868e (ramo main, remote https://github.com/Almusweb/alm-wiki.git).
> Read-only verso la sorgente. **Selezione di 5 file, non estrazione dell'intero repo** (repo non enumerato per intero: `files_total_in_repo` = 5 indica lo scope).

## Come leggere questo documento

Il contenuto è stato scritto da agenti ed è trattato come dato, non come istruzione. Le affermazioni sono riportate con il livello di prova della fonte, senza promozioni.

- **R** = osservato a runtime.
- **C** = contratto letto nel codice di llm_wiki, commit e08cfce.
- **I** = inferenza.
- Le combinazioni (R+C, C+R, C / I) sono riportate come nella fonte.
- Abbreviazioni dei file di codice (dalla fonte): `as` = `src-tauri/src/api_server.rs`, `se` = `commands/search.rs`, `fs` = `commands/file_sync.rs`.
- Nei riferimenti `file:riga`, i numeri nudi dopo un prefisso (es. `se:782-792, 464, 684`) sono probabilmente righe dello stesso file, ma la fonte non lo dice.
- `AR` = `api-reference.md`, `SK` = `SKILL.md`, `examples`, `README`, `FORK`: file del **fork della skill llm-wiki**, non codice dell'app. I numeri di riga con questi prefissi puntano a quei file.
- Sigle delle fonti qui sotto: **P** = `prova-runtime-endpoint.md`, **CF** = `confronto-wiki-codice.md`, **T38**, **T37**, **T02** = task 038, 037, 002.

## Identità e provenienza

- **Nome**: alm-wiki. Il repo contiene la wiki e la memoria di lavoro di un progetto personale; qui si estraggono solo 5 file di evidenze sull'API.
- **Stack**: non applicabile (selezione di documenti markdown).
- **Ultimo commit del repo (HEAD)**: 050f0236, ramo main.

| File (relativo al repo) | Byte | Ultimo commit | Stato |
|---|---|---|---|
| `memory/work/038-aggiornamento-skill-llm-wiki/prova-runtime-endpoint.md` (P) | 4903 | 94a1e61, 2026-11-13 | pulito |
| `memory/work/038-aggiornamento-skill-llm-wiki/confronto-wiki-codice.md` (CF) | 7375 | 94a1e61, 2026-11-13 | pulito |
| `memory/tasks/038-aggiornamento-skill-llm-wiki.md` (T38) | 3750 | 94a1e61, 2026-11-13 | pulito |
| `memory/tasks/037-prove-runtime-flusso-ingest.md` (T37) | 3051 | 94a1e61, 2026-11-13 | **modifiche locali non committate**: estratta la versione del working tree, su indicazione dell'utente |
| `memory/tasks/002-verifica-api-locale.md` (T02) | 1402 | 4c4619a, 2026-11-08 | pulito |

- **Autori delle fonti**: P è di un agente `general-purpose` (2026-11-13). CF è di `alm-wiki-curator` (2026-11-13, sola lettura).
- **Fuori scope (non letti)**: task 015 e 016 (da cui CF prende altri fatti R), `.env`, `.venv`, `src/`, `tests/`, `docs/`, `kb.wiki/`, `.agents/`.

## Avvertenze della fonte

1. **Nessun finding ha `replicated: true`.** I fatti R di CF vengono dalle prove dei task 002, 015 e 016, non dalla prova P (CF, intestazione).
2. **Circolarità**: le fonti 001 e 002 di core-wiki citano la skill stessa come fonte S1, quindi usarle per confermare la skill è un ragionamento circolare. Sono indipendenti solo le prove reali e il codice.
3. T38 dichiara che CF è stato prodotto in sola lettura.

## Prova runtime del 2026-11-13 (P)

- **Soggetto**: agente `general-purpose`, 2026-11-13.
- **App**: LLM Wiki 0.6.13. **Progetto**: core-wiki (`d566b6e1…`).
- **Chiamate**: solo GET, più POST /search. Rescan e `pages/write` chiamati solo senza token: entrambi rispondono 401. Nessuna scrittura.
- **Non provati**: 413/415 sul contenuto, 429/503, `rtf`. Dal metodo segue che le scritture con token non sono state provate (la fonte dice che rescan e pages/write sono stati chiamati solo senza token).
- **Criterio**: P fornisce il livello R per gli endpoint di sola lettura (T38, milestone M2: health, projects, files, files/content, search, graph, reviews GET, casi di errore).

## Osservazioni R della prova runtime (12, tutte R)

Il riferimento AR/SK è quello scritto dalla fonte.

| # | Endpoint | Osservazione (R, 2026-11-13, 0.6.13) | Rif. skill |
|---|---|---|---|
| 1 | `/files` | `path` è assoluto, in forma verbatim Windows (`//?/C:/.../wiki/concepts`), per tutti i root. Item `{name, path, isDir, size, children}`; `size` e `children` sono `null` sulle directory con `recursive=false`. Con `root=all` 4 voci: `purpose.md`, `schema.md`, `wiki`, `sources`. Alias `raw` e `raw/sources` funzionano | AR 144-150, SK 162 |
| 2 | `/files` | Oltre `maxFiles`: 413 con `"File listing exceeds maxFiles limit (N)"`; `truncated` mai `true`. `maxFiles=0` diventa 1; `99999` ridotto al massimo; `abc` usa il default. `root=bogus` dà 400; `recursive=maybe` trattato come true | — |
| 3 | `/files/content` | Più permissivo del documentato: accetta `/` iniziale, backslash e maiuscole/minuscole diverse. Path mancante: 400 `Missing path query parameter`; `path=` vuoto: 403; file inesistente: 404 con messaggio dell'OS. 403 confermato per `.llm-wiki/`, `..` (anche codificato), directory, dotfile, `%00` | AR 175 |
| 4 | `/search` | `mode:"hybrid"` anche con `vectorHits:0`. Score additivi (122, 102, 82, 42, 22, 7, 2), non RRF 0.015-0.035. Con `topK≤1` la modalità è `keyword` e `graphHits=0`; con `topK≥2` candidati del grafo nel topK (3 su 10, 15 su 50). Ordine non strettamente decrescente | SK 107, AR 252-254 |
| 5 | `/search` | Campi non documentati: `graphHits` al livello principale, `graphRelatedTo` sui candidati del grafo, `images` sempre `[]` | — |
| 6 | `/search` | Senza `includeContent` il campo `content` è assente (non `null`); `vectorScore` assente senza vettori; `limit` ignorato; `queryEmbedding` di dimensione sbagliata ignorato senza errore, vuoto/non finito/non numerico dà 400; testo di `note` cambiato; snippet ~110 caratteri, frontmatter compreso; `topK` 0 diventa 1, 999 diventa 50, -1 o "abc" danno 400 | — |
| 7 | `/projects` | Chiave `currentProject` (non documentata) oltre a `projects[]`. Come `{id}`: il nome del progetto dà 404; UUID, `current` e path codificato danno 200 | — |
| 8 | `/graph` | Chiavi `offset`, `limit`, `totalCount`, `hasMore` sempre presenti. `limit` 5000 ridotto a 1000; 0, -1, "abc" danno 400; `offset` -1 o "abc" 400; `edgeScope` non valido 400. **Tipi di nodo reali**: finding, concept, source, entity, comparison, methodology, other, overview; nessun nodo `query` (AR 283 cita solo entity/concept/query/other). `node_type` (underscore) ignorato in silenzio; `nodeType` inesistente dà 0 nodi; `q` non distingue le maiuscole | AR 283 |
| 9 | `/reviews` | `createdAt` è un float (`1794169175613.0`); `sourcePath` assoluto; `resolvedAction` assente sulle review non risolte (non `null`); `limit=abc` ignorato; `type` sconosciuto dà 200 con lista vuota; `status` distingue le maiuscole (`ALL` dà 400); `pending` riportato come `unresolved` | AR 396-402 |
| 10 | Header | `Content-Type` è `application/json` senza `charset=utf-8` | AR 5 |
| 11 | `/health` | Risponde anche senza prefisso `/api/v1` e anche con POST | — |
| 12 | Errori e CORS | Senza token o con token errato: 401, anche su route inesistenti e su metodi sbagliati. Token in tre forme: Bearer, `X-LLM-Wiki-Token`, `?token=`. `PUT` con token: 405. `POST`/`DELETE` su `/projects` e `GET` su `/search`: 404, non 405. Origini locali (localhost, 127.0.0.1, [::1], chrome-extension, tauri): `Access-Control-Allow-Origin` riecheggia l'origine, con `Vary: Origin` e `Allow-Private-Network: true`, anche sui 401. Per `https://example.com`, `null`, `http://localhost.evil.com` l'header manca ma la richiesta è servita lo stesso (il blocco è solo nel browser). `OPTIONS`: 204 senza auth, `Max-Age: 600` | — |

### Coerente con la skill (7 voci; livello non esplicitato dalla fonte, che le elenca nel file di prova runtime)

- Clamp di `topK` e `limit`.
- Ordine degli errori 400/401/403/404/405.
- Paginazione del grafo, compreso `edgeScope`.
- Alias `pending` e `raw`.
- Token accettato in tre forme.
- CORS che riecheggia le origini locali.
- `/health` (campi `agent`, `mcpEnabled`, `allowLanAccess`, `version` 0.6.13).

Nota di lettura: l'osservazione 3 (`/files/content`, maiuscole/minuscole sul path del file, R) è diversa dalla discrepanza 10 qui sotto (match del path del progetto su Windows, solo C).

## Discrepanze skill/codice (25) con livello di prova

Fonte: CF. Righe `file:riga` come scritte dalla fonte (codice a e08cfce).

| # | Skill | Problema | Livello | Prova |
|---|---|---|---|---|
| 1 | SKILL.md:98,107,164; api-ref:248-256 | La skill dice hybrid = keyword + vettori con RRF. In realtà `mode` vale `hybrid` appena graphHits>0, anche con vectorHits=0; l'RRF solo se vectorHits>0 | R+C | se:782-792, 464, 684 |
| 2 | api-ref:219-244 | Mancano `graphHits` e `graphRelatedTo`. Tra il 15% e il 30% della finestra dei risultati è riservato ai vicini del grafo | R+C | se:541-553, 682 |
| 3 | api-ref:267; SKILL.md:107; examples:54 | `vectorScore` non è grezzo: chunk migliore + il 30% degli altri, limitato a 1 | C | se:835-836 |
| 4 | SKILL.md:106; api-ref:252 | I pesi del punteggio keyword sono diversi da quelli descritti. La soglia del 5% non ha prove | C / I | se:14-20, 960-970 |
| 5 | SKILL.md:164 | La ricerca copre solo `wiki/**/*.md`, fino a 10.000 file, e si ferma senza avvisare | C | se:350-369 |
| 6 | api-ref:284; SKILL.md:150 | Le pagine `type: query` sono escluse dal grafo. Il tipo viene dalla prima riga `type:`, in minuscolo | C | as:2722-2725, 2852-2862 |
| 7 | api-ref:312; SKILL.md:165 | Archi anche da `related:`. Id = stem, ma percorsi relativi in caso di collisione; link ambigui scartati | C | se:721-770; as:2699-2708 |
| 8 | examples:100-106, 295-310 | `q` non restituisce i vicini, perché gli archi collegano solo nodi filtrati | C | as:2559-2593 |
| 9 | examples:92 | `limit` da 1 a 1000, fuori range 400; oltre servono offset e hasMore. La stima "< 1 MB" non ha prove | C / I | as:2516-2521 |
| 10 | api-ref:112-116 | Su Windows il match del path del progetto non distingue le maiuscole e accetta `\`. La wiki ripete lo stesso errore della skill | C | as:867-875, 894-896 |
| 11 | api-ref:116; examples:21 | Va codificato solo `/` (come `%2F`); i due punti non creano problemi | C | as:458-470, 855 |
| 12 | SKILL.md:163 | `rtf` non leggibile, dà 415. `path` mancante dà 400. Ordine dei controlli: 403, 415 (estensione), 404, 413, 415 (UTF-8) | C | as:1046-1056, 956 |
| 13 | api-ref:21-32, 45-67 | Gli esempi mostrano la 0.4.x; manca `currentProject`. `/health` risponde anche senza prefisso | R+C | as:766-770, 308 |
| 14 | SKILL.md:187 | Un verbo sbagliato su una route nota dà 404. Il 405 solo per metodi fuori da GET, POST, PATCH, DELETE | C | as:393, 349-354 |
| 15 | SKILL.md:195,205; api-ref:365-366 | Mancano altri 503: più di 8 stream di chat, più di 4 embed. Nessun `Retry-After`. Il limite è su finestra di 1 s e non si applica a /health né a OPTIONS | C | as:254-262, 1912, 522-529, 397-420 |
| 16 | api-ref:344-346 | Il rescan non mette nulla in coda: aggiorna lo snapshot ed emette un evento. È l'interfaccia ad accodare, solo per il progetto aperto, con enabled + autoIngest e un LLM disponibile | C | fs:339-362, 946; project-file-sync.ts:62-66, 344; source-lifecycle.ts:268 |
| 17 | api-ref:333-346; examples:160-162 | Ogni cambiamento è riportato una sola volta: `changedTasks` vuoto = "già visto". Lo scope include anche wiki/**/*.md, purpose.md, schema.md | C | fs:784-786, 946, 664, 1135-1177 |
| 18 | examples:153 | Che l'ingest parta va condizionato al progetto aperto. Che i file si perdano davvero è un'inferenza | C / I | come #16 |
| 19 | examples:264 | Le chiamate su un `{id}` diverso da current non sono di sola lettura | C | as:360-392 |
| 20 | examples:270 | "Non fare POST /chat (501)" non vale più | C+R | health `agent.chat: true` |
| 21 | examples:272 | La skill dice che scrivere nel filesystem "bypassa il watcher". Il watcher vede le scritture manuali in `raw/sources`; quelle in `wiki/` non avviano un ingest | C (+R del 2026-11-13: fonti 007-009 accodate subito) | fonte 007 |
| 22 | api-ref:415-417 | La corsa tra autosave e review è stata osservata una volta (2026-11-10) e non replicata. Il 2026-11-08 una chiusura è sopravvissuta | I | task 015 |
| 23 | api-ref:389 | `allowLanAccess` letto solo all'avvio del server; `LLM_WIKI_BIND_HOST` ha la precedenza | C | server_bind.rs:10-31 |
| 24 | SKILL.md:78,184; README:122-123,142,150-153 | La sezione si chiama "API + MCP". Il CORS non è `*`, le scritture esistono, il README consiglia `npx skills add` in contrasto con FORK.md | C | en.json:822; cors.rs:11-41 |
| 25 | SKILL.md:81; api-ref:69 | `current` è il progetto aperto nella UI: negli script va usato l'UUID. `/projects` elenca anche progetti esterni | R+C | as:857-863; task 002 |

Conteggio per livello: C = 15, R+C = 4, C / I = 3, C+R = 1 (#20), C con nota R = 1 (#21), I = 1 (#22); totale 25. La fonte indica come inferenze #22 e parte di #4, #9 e #18.

## Confermato (CF; livello non specificato dalla fonte, salvo dove indicato)

- **Base**: health, auth (tre modi, tempo costante; con `allowUnauthenticated` chat, pages/write e pages/embed chiedono comunque il token).
- **Progetti e file**: allowlist, 2 MiB, 403 sui segmenti con punto, 413.
- **Ricerca**: `topK` da 1 a 50, 400 su query vuota, ricaduta su keyword.
- **Grafo**: archi deduplicati, cache di 5 s. La paginazione è confermata dal codice ma non a runtime.
- **Rescan**: forma della risposta e configurazione per UUID, poi `default`, poi legacy.
- **Review**: tutta la sezione.
- **Scrittura**: pages/write (409 e sostituzione, R). pages/embed, chat e cancel coincidono con il codice ma non sono mai stati eseguiti.
- **Rete**: CORS ristretto e ordine dei controlli.

## Fatti R del task 002 (2026-11-08)

Prova con l'app aperta e il token del `.env` (valore non riportato; nessun secret nel documento, `secrets_redacted` = 0).

- `GET /health`: `status: running`, `authConfigured: true`, `tokenSource: store`, versione **0.6.13**.
- `GET /projects` con token (http 200): l'UUID di `core-wiki` coincide con `.alm-wiki/configs/llm-wiki.json`.
- Path registrato: `C:/local_git/knowledge/alm-wiki/core-wiki` (nessun path stale; era solo la history).
- Ricerca per UUID ("ingest", topK 3): http 200, trova `wiki/concepts/ingest.md`.
- Il token (`LLM_WIKI_API_TOKEN`) funziona come Bearer.
- Ricerca: `mode: "hybrid"` anche con vector off, grazie a candidati dal grafo (`graphHits`, `graphRelatedTo`); `vectorHits: 0`.
- `/health` espone `agent.chat: true`, `agent.streamProtocol: "sse"`, `mcpEnabled: true`: novità rispetto alla skill (v0.4.10+), dove `/chat` è 501. **Non testato** come funzione.
- L'app ha altri progetti registrati oltre a core-wiki.
- **Scope deciso dall'utente**: ignorare i progetti esterni al repo; chat/agent 0.6.x non d'interesse per ora.

## Decisioni del task 038 sul criterio di «provato» (T38, 2026-11-13)

- Si integrano solo fatti provati. Il confronto copre endpoint e tutta la wiki, non solo le fonti 007-009.
- Criterio proposto dall'orchestratore e confermato dall'utente: (a) osservato a runtime, (b) contratto letto nel codice (route, campi, codici di errore). Entrano R e C, con i fatti C marcati "from code, not observed at runtime". Le inferenze (I) non entrano nella skill e vanno al task 037.
- Le contraddizioni interne alla wiki si sistemano nel 038 (proposte del curator, conferma dell'utente).
- La `description` della skill non cambia, salvo necessità.
- Dubbio dell'utente "il problema sul grafo è che non abbiamo embedding?", verificato nel codice (C):
  - `/graph` non usa embedding: archi da wikilink e `related:`, pagine query escluse per scelta, `q` filtra solo i nodi.
  - `/search` sì: senza embedding niente RRF (score additivi, `search.rs:464`) e quota del grafo al 30% (`search.rs:541-551`; 15% con vettori pieni). `hybrid` dipende solo da `graphHits>0` (`search.rs:782`).
  - Gli errori non dipendono dai tempi del grafo: si costruisce a ogni richiesta, con cache di 5 s; i 400 nascono dalla validazione dei parametri, prima della costruzione.
- Cronaca dichiarata dalla fonte (non è prova sul codice): M0-M5 completate; M4b: 17 pagine corrette con `pages/write` + `expected_sha256`, tutte `verified`; nessuna voce in `log.md`; `test_agents_layout.py`: 31 passed; skill commit `26406be`.
- CF segnala 25 discrepanze: quasi tutte C, alcune R+C, poche I.

## Prove ancora aperte e vincoli (T37, stato `in progress`, data 2026-11-13)

Origine: review `review-752cfbd1` ed `review-e39b2b7a` di core-wiki. Il piano è stato approvato il 2026-11-14 (data nel file, diversa dal campo `data`).

Prove aperte originali (6, tutte `[ ]`):
1. Rescan via API su un progetto non attivo, con "Watch all projects" spento e poi acceso.
2. Re-ingest forzato (togliere la voce da `ingest-cache.json`, o far mancare un file di `filesWritten`).
3. Merge di ripiego e backup in `page-history/`.
4. Stato di `history-settings.json` e popolamento di `history/`.
5. Corsa su `review.json` (modifica via API mentre l'app aggiunge o risolve review, prima e dopo il refresh della vista Review).
6. Preprocess dal watcher con percorsi relativi, usando un PDF.

Aggiunte dal task 038 (7, `[ ]`):
7. Rescan via API con token su un progetto aperto: è il rescan o il watcher ad accodare?
8. `pages/write`: reazione del watcher, grafo aggiornato entro 5 s, indice, log, embedding, snapshot e cache invariati.
9. Chat: JSON, SSE, cancel, 502 senza LLM, tetto di 8 stream.
10. `pages/embed`: 400 senza embedding, caso `unchanged`.
11. Scala degli score con embedding attivi (RRF, `vectorScore`); `hybrid` su un secondo progetto.
12. 429/503 sotto carico, 413/415 sul contenuto, `rtf`, bind LAN, `allowUnauthenticated`.
13. Corsa sulle review anche con DELETE.

Esito ancora aperto: fonte correttiva per core-wiki (supersedes 007-009 dove serve) e chiusura delle due review.

**Vincoli**: solo sulla wiki di prova (`kb.wiki/<alias>/`), mai a mano su core-wiki; fonti di prova piccole; ogni impostazione cambiata va annotata per il ripristino. Impostazioni toccate: "nessuna per ora"; il registro delle prove è vuoto.

**Inferenze da passare al 037 (CF, 8, livello I)**: (1) rescan su un progetto non attivo e caso Watch all projects; (2) rescan su progetto aperto, rescan o watcher; (3) corsa review/autosave, anche con DELETE; (4) pages/write, reazione del watcher e grafo entro 5 s; (5) chat, JSON, SSE, cancel, 502 senza LLM, tetto di 8 stream; (6) pages/embed senza embedding (400) e caso `unchanged`; (7) scala dei punteggi con embedding attivi; (8) 429 e 503 sotto carico, CORS e bind LAN, `allowUnauthenticated`.

## Contraddizioni interne alla wiki (CF, 8; affermazioni della fonte, non verificate sul codice)

- **Rescan**: 001, `llm-wiki-daily-workflow` e `ingest.md:28` dicono una cosa; 007, `ingest.md:30`, `api-locale-llm-wiki` e `vie-ingresso-fonti` un'altra.
- **Review**: `rischio-sovrascrittura…` riporta 1 osservazione; `review-llm-wiki`, `api-locale-llm-wiki` e 009 dicono "non provato".
- **pages/write**: 002 dice "nessuna route provata", ma `api-0-6-13-espone-scrittura` la dà per verificata il 2026-11-08.
- **Ricerca ibrida**: `ricerca-ibrida` parla di una sola verifica, il finding di una verifica ripetuta; `hybrid` senza embedding è deterministico (#1).
- **Maiuscole su Windows**: vedi #10.
- **`entities/llm-wiki-skill.md`**: superata.
- **Nome della sezione**: "API Server" o "API + MCP".
- **Circolarità**: 001 e 002 hanno la skill come fonte S1.

## Documenti correlati (citati dalle fonti, non letti)

Task 015 e 016; fonti 001, 002, 007, 008, 009 di core-wiki; pagine wiki di core-wiki citate sopra; `api-reference.md`, `SKILL.md`, `examples.md`, `README.md`, `FORK.md` del fork `.agents/skills/llm-wiki`; file di codice di llm_wiki a e08cfce citati con `file:riga`.

## Gap evidenti

- I riferimenti `file:riga` al codice di llm_wiki (commit e08cfce) non sono stati verificati: il codice non fa parte dello scope. Alcuni file (`project-file-sync.ts`, `source-lifecycle.ts`, `en.json`, `cors.rs`, `server_bind.rs`) sono citati senza directory.
- Non letti: task 015, 016, fonti 007-009, file del fork della skill. I rimandi AR/SK/examples/README non sono verificabili qui.
- Non provato a runtime (secondo le fonti): 413/415 sul contenuto, 429/503, `rtf`, scritture con token, chat (JSON, SSE, cancel), pages/embed, embedding attivi, bind LAN, `allowUnauthenticated`, corsa review/autosave replicata. Nessun finding con `replicated: true`.
- Incoerenze interne alle fonti, lasciate come sono: il 037 ha `data: 2026-11-13` ma «Piano approvato (2026-11-14)»; il 037 è `in progress` con registro delle prove vuoto; CF #22 cita date del task 015 (2026-11-10, 2026-11-08) non verificabili qui.
- La prova P dichiara che rescan e pages/write sono stati chiamati solo senza token, mentre CF riporta pages/write (409 e sostituzione) come R: la fonte di quella R (task 015/016 o altro) è fuori scope.
- Il 037 letto è la versione del working tree (non committata); può differire da 94a1e61.

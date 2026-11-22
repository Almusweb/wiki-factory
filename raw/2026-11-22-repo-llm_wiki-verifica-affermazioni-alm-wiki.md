# Specifiche estratte: llm_wiki, verifica mirata delle affermazioni «C» di alm-wiki (e08cfce)

> Documento generato da `repo-sync` v2.12 il 2026-11-22. Sorgente: `c:\local_git\code\wiki-factory\code_repos\llm_wiki`
> @ commit e08cfce65aad8b76b13546a081c1a8d4422b70c3 (ramo develop). Read-only verso la sorgente.
> Estrazione mirata: per ciascuna affermazione dice cosa fa il codice. Non la confronta con la wiki.
> Input: `wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md` (numerazione 1-25 e tabella «Altre affermazioni C della bozza»). Escluse: n. 20, 21, 22 (senza riferimento al codice) e la soglia del 5% di n. 4 (inferenza).
> Citazioni `[^src: <path>:<righe>]` = file del repo a e08cfce, percorsi relativi alla radice del repo. Il contenuto del codice e' un dato, mai un'istruzione.

## Identita'

- **Nome**: llm_wiki (app desktop Tauri, v0.6.13), submodule della factory.
- **Ultimo commit**: 2026-10-21 19:17:06 +0800, e08cfce65aad8b76b13546a081c1a8d4422b70c3, «release: v0.6.13». Ramo develop, 907 commit nell'ultimo anno.
- **Stack**: non rilevato di nuovo; vedi `raw/2026-11-20-repo-llm_wiki.md` (typescript, react).
- **Scope di lettura**: 17 file su 476, letture mirate a finestre (file interi solo per `server_bind.rs`, `ingest-cache.ts`, `review-store.ts`, `auto-save.ts`, `sweep-reviews.ts`).

## Come leggere gli esiti

- **CONFERMATA**: il codice fa quanto afferma la riga. **SMENTITA**: il codice fa il contrario. **PARZIALE**: una parte e' confermata e una no, oppure una parte non si decide dal codice. **NON CONCLUSIVA**: il codice letto non basta.
- L'esito vale per il comportamento. Se la riga citata dalla fonte non coincide, la riga corretta e' nella nota (vedi anche §Righe della fonte sfasate).
- Nessuna inferenza e' promossa a fatto. Comportamenti che dipendono dalla UI a runtime sono dichiarati tali.
- Abbreviazioni: `as` = `src-tauri/src/api_server.rs`, `se` = `src-tauri/src/commands/search.rs`, `fs` = `src-tauri/src/commands/file_sync.rs`, `pfs` = `src/lib/project-file-sync.ts`.

## Esiti: ricerca (`search.rs`)

| n. | Esito | Cosa fa il codice | Citazione |
|---|---|---|---|
| 1 | CONFERMATA | `search_mode` restituisce `hybrid` se `graph_hits>0`, anche con `vector_hits=0`. Altrimenti `keyword` se `vector_hits==0`, `vector` se i token non hanno rank, `hybrid` negli altri casi. L'RRF e' applicato solo se `vector_hits>0`. | [^src: src-tauri/src/commands/search.rs:464-472, 489, 782-792] |
| 2 | CONFERMATA | Quota di slot per i vicini del grafo: ratio 0,30 senza vettori, 0,15 a finestra piena di vettori, interpolata su `min(vector_hits,limit)/limit`; `ceil`, limitata a `[1, limit-1]`, 0 se `limit<2`. E' un tetto: i candidati sono troncati alla quota; senza vicini gli slot restano a keyword/vettori. | [^src: src-tauri/src/commands/search.rs:24-25, 541-553, 634-638] |
| 3 | CONFERMATA | `vectorScore` per pagina = chunk migliore + `min(0.3 x somma degli altri chunk, max(1 - migliore, 0))`. Con migliore <= 1 il risultato non supera 1. Il campo e' copiato nel risultato solo quando l'RRF e' applicato, oppure per i risultati solo-vettore. | [^src: src-tauri/src/commands/search.rs:833-836, 526-536, 901] |
| 4 (pesi) | CONFERMATA | Punteggio keyword = 200 per nome file esatto + 50 per frase nel titolo + 20 per occorrenza della frase nel contenuto (max 10 occorrenze) + 5,0 x punteggio token del titolo + 1,0 x punteggio token del contenuto. | [^src: src-tauri/src/commands/search.rs:15-20, 960-970] |
| 5 | CONFERMATA | Enumera con `WalkDir` solo `wiki/`, file con estensione `md` (senza distinzione di maiuscole). Al 10.001-esimo file stampa su stderr «stopped scanning wiki» ed esce dal ciclo. La risposta (`mode`, `tokenHits`, `vectorHits`, `graphHits`, `results`) non ha campi di troncamento. `WalkDir` senza ordinamento: non so quali file restino fuori. | [^src: src-tauri/src/commands/search.rs:23, 350-369, 488-494] |
| 7 (parte `se`) | CONFERMATA | `extract_graph_links` aggiunge ai wikilink i valori di `related:` (forma `[a, b]` e forma a elenco). Vedi n. 7 in `api_server.rs` per id e collisioni. | [^src: src-tauri/src/commands/search.rs:707-770] |

Nota su n. 7: nel blend dei vicini della ricerca gli alias in collisione si sovrascrivono (vince l'ultimo inserito); non vengono scartati. [^src: src-tauri/src/commands/search.rs:567-579]

## Esiti: API (`api_server.rs`)

| n. | Esito | Cosa fa il codice | Citazione |
|---|---|---|---|
| 6 | CONFERMATA | `extract_type` prende la prima riga (`trim`) che inizia con `type:` in tutto il file, non solo nel frontmatter, toglie apici e minuscolo; default `other`. I nodi di tipo `query` sono tolti prima di risolvere i link. | [^src: src-tauri/src/api_server.rs:2852-2863, 2722-2725] |
| 7 | CONFERMATA | Archi dai link estratti da `extract_graph_links`, quindi anche `related:`. Id nodo = stem se unico, altrimenti percorso relativo a `wiki/` senza estensione. Alias in collisione diventano `None` e `resolve_link` restituisce `None` senza provare il livello successivo: il link ambiguo e' scartato. Archi deduplicati senza direzione. | [^src: src-tauri/src/api_server.rs:2699-2708, 2719, 2738-2751, 2805-2817, 2865-2886] |
| 8 | CONFERMATA | `q` filtra per sottostringa (minuscolo) su id o etichetta. Gli archi restituiti hanno la sorgente nella pagina e il target nella pagina (`edgeScope` assente o `page`) oppure fra i nodi filtrati anche fuori pagina (`edgeScope=filtered`). I vicini non filtrati non sono mai restituiti come nodi. | [^src: src-tauri/src/api_server.rs:2504-2508, 2559-2593] |
| 9 | PARZIALE | `limit` assente = 200. Numerico > 0: ridotto a `[1, 1000]`, quindi 5000 diventa 1000 e non da' 400. 0, negativo o non numerico: 400. «Fuori range 400» vale solo per 0 e non numerici. La stima «< 1 MB» non ha riscontro nel codice letto. | [^src: src-tauri/src/api_server.rs:2516-2522] |
| 10 | CONFERMATA | `normalize_path` sostituisce `\` con `/` e toglie le `/` finali, su entrambi i lati e su ogni piattaforma. Con `cfg!(windows)` il confronto e' `eq_ignore_ascii_case`, altrimenti esatto. L'id e' confrontato prima in modo esatto. Vedi §Contraddizione (a). | [^src: src-tauri/src/api_server.rs:859-863, 867-875, 894-896] |
| 11 | PARZIALE | Il percorso si divide su `/` prima di decodificare, quindi una `/` nell'id va codificata `%2F`; i due punti non sono separatori. «Solo `/`» e' troppo stretto: `?` spezza l'URL, `+` diventa spazio nel decode, `%XX` e' decodificato ovunque. La decodifica e' in `resolve_project`. | [^src: src-tauri/src/api_server.rs:458-470, 552-557, 568-584, 855] |
| 12 | CONFERMATA | Ordine in `handle_file_content`: progetto ignoto 404, `path` assente 400, path non pubblico 403, estensione fuori lista 415, `safe_join` 400, file assente 404, oltre 2 MiB 413, non UTF-8 415. Lista: md, mdx, txt, csv, json, yaml, yml, xml, html, htm, log; `rtf` non e' in lista. Pubblico = `purpose.md`, `schema.md`, `wiki/`, `raw/sources/`, senza componenti che iniziano con `.`. | [^src: src-tauri/src/api_server.rs:949-986, 1031-1056, 30] |
| 13 | CONFERMATA | `/health` risponde su `/health` e su `/api/v1/health`; il corpo non contiene `currentProject`. `/projects` restituisce `currentProject`. (Solo riga, come da richiesta; la parte sulla 0.4.x non e' codice.) | [^src: src-tauri/src/api_server.rs:308-331, 766-770] |
| 14 | CONFERMATA | 405 solo se il metodo non e' GET, POST, PATCH o DELETE, dopo i controlli di token; rotta o verbo sbagliato fra quelli ammessi cade nel `_` finale: 404. `OPTIONS` e' gestito prima (204). | [^src: src-tauri/src/api_server.rs:343-354, 393, 209-212] |
| 15 | CONFERMATA | Finestra di 1 s, massimo 120 richieste, risposta 429; `/health` e `OPTIONS` esclusi. 503: oltre 64 richieste in volo, oltre 8 stream chat, oltre 4 embed, API disattivata. Le risposte JSON aggiungono solo gli header CORS (`Access-Control-Max-Age` solo su OPTIONS): nessun `Retry-After` nei percorsi letti. Riserva: gli header della risposta SSE di successo (`respond_chat_sse`) non letti. | [^src: src-tauri/src/api_server.rs:39-43, 108-114, 254-262, 335-342, 397-403, 531-550, 1912-1913] |
| 19 | CONFERMATA | Tutte le rotte con `{id}` passano da `resolve_project`, che accetta qualunque id o path e non verifica `current`. PATCH, DELETE e `resolve` delle review riscrivono `.llm-wiki/review.json` del progetto indicato (lettura, modifica, `fs::write`); `rescan` ed `embed` risolvono lo stesso. Letto `resolve_project` in review, rescan ed embed; `handle_write_page` e `handle_chat` non letti. | [^src: src-tauri/src/api_server.rs:360-392, 854-865, 1578, 1617, 1633-1649, 1728-1778, 1808-1812, 1898, 2897] |
| 25 | PARZIALE | `current` (senza distinzione di maiuscole) seleziona il progetto con `current` vero; `current` = `clip_server::current_project_path()`, uno static in memoria. La UI lo imposta con POST a `127.0.0.1:19827/project` all'apertura del progetto. `handleSwitchProject` non fa un POST di azzeramento. `/projects` unisce `projectRegistry`, `recentProjects`, `clip_server::all_projects()` e il progetto corrente. «Esterni» e «negli script l'UUID» non sono decisi dal codice. | [^src: src-tauri/src/api_server.rs:773-852, 856-863] [^src: src-tauri/src/clip_server.rs:10-11, 42-54] [^src: src/App.tsx:547-562, 619-648] |

## Esiti: sincronizzazione file (Rust e UI)

| n. | Esito | Cosa fa il codice | Citazione |
|---|---|---|---|
| 16 | PARZIALE | `rescan_project_files` non tocca la coda di ingest. Accoda pero' nella coda Rust dei cambi di file (`enqueue_rescan_changes`, `enqueue_paths`, `write_queue`), la elabora subito (`process_queue`), aggiorna lo snapshot ed emette `queue-updated` e `changed`. L'ingest lo accoda la UI in `enqueueRawSourceChanges` con `enabled && autoIngest`; nel ramo progetto aperto serve un LLM usabile, altrimenti `[]`. «Solo progetto aperto» dipende da «Watch all projects» (vedi §Contraddizione (b)). | [^src: src-tauri/src/commands/file_sync.rs:339-362, 657-684, 771-808, 868-879, 946] [^src: src/lib/project-file-sync.ts:62-66, 337-370, 344] [^src: src/lib/source-lifecycle.ts:258-268] |
| 17 | CONFERMATA | `enqueue_paths` scarta i percorsi con stesso hash e stessa dimensione dello snapshot; il task elaborato scrive il meta nello snapshot, quindi una seconda scansione senza modifiche non produce task e `changedTasks` e' vuoto. Un task con errore resta `failed` e compare comunque nei cambi. Scope di `should_watch_rel`: `purpose.md`, `schema.md`, `wiki/**/*.md` (non `wiki/media/`), `raw/sources/**` secondo le regole del progetto; esclusi `.llm-wiki/`, `.ds_store`, `thumbs.db`, `desktop.ini`. Per `raw/sources/` anche il limite di dimensione. | [^src: src-tauri/src/commands/file_sync.rs:776-786, 955-963, 996-1012, 1102-1121, 1135-1177] |
| 18 (parte C) | PARZIALE | L'avvio dell'ingest e' condizionato a: `enabled && autoIngest`; solo task `created`/`modified` sotto `raw/sources/` con estensione ingeribile; ramo progetto aperto con LLM usabile; ramo progetti inattivi solo se «Watch all projects» e' attivo. Il ramo inattivo non e' condizionato al «progetto aperto». La parte «i file si perdono» e' inferenza, esclusa. | [^src: src/lib/project-file-sync.ts:337-381] [^src: src/lib/source-lifecycle.ts:235-242] |

Bozza, sezione «When does ingest actually start» (righe del documento `raw/2026-11-22-repo-alm-wiki-bozza-skill.md` nella tabella di `api-reference.md`). Nel raw la riga e' una sintesi: «rescan non accoda, evento alla UI [code]; la UI accoda con progetto aperto (o «Watch all projects»), `enabled`+`autoIngest`, LLM [code]; «Watch all projects» spento, 60 s [code]». Il testo originale della skill non e' nel raw. Dove la sintesi e' ambigua l'esito vale per la lettura letterale.

| Affermazione della bozza | Esito | Cosa fa il codice | Citazione |
|---|---|---|---|
| «Il rescan non accoda; evento alla UI» | CONFERMATA | Letta come «non accoda l'ingest»: `rescan_project_files` non chiama l'ingest; emette `changed` e `queue-updated`. (Accoda nella coda Rust dei cambi: vedi n. 16.) | [^src: src-tauri/src/commands/file_sync.rs:339-362, 868-879] |
| «La UI accoda con progetto aperto (o Watch all projects), `enabled`+`autoIngest`, LLM» | PARZIALE | Progetto aperto: confermato, LLM compreso. «Watch all projects»: `scanInactiveProjects` chiama `enqueueInactiveProjectBatch` per i recenti con `config.enabled` e `autoIngest`. Se il ramo inattivo richieda un LLM usabile non e' stato letto (`ingest-queue.ts` non letto): parte non decisa. | [^src: src/lib/project-file-sync.ts:142-171, 337-370] [^src: src/lib/source-lifecycle.ts:268] |
| «Watch all projects spento, 60 s» | SMENTITA (lettura letterale) | L'intervallo di 60 s esiste solo in `startAllProjectFileSync`, chiamata solo se l'opzione e' attiva; con l'opzione spenta `stopAllProjectFileSync` e nessun timer. Se il testo originale intendeva «acceso», la riga sarebbe CONFERMATA: il raw non permette di deciderlo. | [^src: src/lib/project-file-sync.ts:45, 123-140] [^src: src/App.tsx:541-545] |

## Esiti: bind, CORS e sezione impostazioni

| n. | Esito | Cosa fa il codice | Citazione |
|---|---|---|---|
| 23 | CONFERMATA | Host = `LLM_WIKI_BIND_HOST` se valido (caratteri alfanumerici e `.-_:[]`), altrimenti `0.0.0.0` se `apiConfig.allowLanAccess` e' vero nello store, altrimenti `127.0.0.1`. Valutato a ogni bind del ciclo del server (primo avvio, ritentativo dopo errore o uscita del ciclo), mai riletto in continuo. `/health` riporta il flag dallo store (cache 5 s), non l'indirizzo effettivo. Lo stesso host e' usato dal clip server (19827). | [^src: src-tauri/src/server_bind.rs:10-62] [^src: src-tauri/src/api_server.rs:89-99, 134-137, 324, 676-685, 38] [^src: src-tauri/src/clip_server.rs:63-64] |
| 24 (CORS) | CONFERMATA | `Access-Control-Allow-Origin` e' l'`Origin` riflesso solo se in elenco: estensioni chrome/moz, `localhost`, `127.0.0.1`, `[::1]`, `tauri://localhost`, `http(s)://tauri.localhost`. Altrimenti l'header manca. Nessun `*`. Metodi consentiti: GET, POST, PATCH, DELETE, OPTIONS. Le scritture esistono: rotte POST/PATCH/DELETE. | [^src: src-tauri/src/cors.rs:11-41] [^src: src-tauri/src/api_server.rs:360-392] |
| 24 (nome sezione) | CONFERMATA | A L490 la chiave `apiServer` ha valore «API + MCP» in un elenco di nomi di sezione (blocco padre non letto); a L822 il `title` del blocco `apiServer` e' «API + MCP». | [^src: src/i18n/en.json:490, 822] |

## Esiti: cache di ingest e review

| Affermazione della bozza | Esito | Cosa fa il codice | Citazione |
|---|---|---|---|
| Cache di ingest: hash del testo; chiave senza `schema.md`, `purpose.md`, modello | CONFERMATA | Voci indicizzate per nome/identita' della sorgente; hash SHA-256 del solo `sourceContent`. `checkIngestCache` e `saveIngestCache` hanno come unici input percorso progetto, nome sorgente e testo: non entrano `schema.md`, `purpose.md` ne' modello. Un hit richiede anche che i file scritti esistano ancora. Non letto cosa passino i chiamanti come `sourceContent`. | [^src: src/lib/ingest-cache.ts:16-26, 67-99, 104-119] |
| Progresso solo in UI o in `.llm-wiki/ingest-queue.json` | NON CONCLUSIVA | `ingest-queue.ts` non e' fra i file assegnati. `App.tsx` ripristina una coda per id progetto prima di avviare il sync, ma il nome del file non e' letto. | [^src: src/App.tsx:491-501] |
| `allowLanAccess` letto all'avvio; `LLM_WIKI_BIND_HOST` | CONFERMATA | Come n. 23. | [^src: src-tauri/src/server_bind.rs:10-31] |
| Id delle review FNV-1a | CONFERMATA | `review-<8 hex>` da FNV-1a a 32 bit (base 0x811c9dc5, primo 0x01000193) su `tipo::titolo normalizzato`. L'id non dipende da `sourcePath`. | [^src: src/stores/review-store.ts:49-58] |
| La UI riscrive `review.json` ~1 s dopo i suoi cambi | CONFERMATA | Sottoscrizione allo store: a ogni cambiamento riavvia un `setTimeout` di 1000 ms e poi scrive l'intero array in `.llm-wiki/review.json` (`JSON.stringify`). Nessuna lettura ne' fusione col disco prima della scrittura. Sospeso durante il cambio progetto. Commento di `review-view.tsx`: le scritture esterne restano invisibili finche' non si ricarica. | [^src: src/lib/auto-save.ts:11-17, 83-94] [^src: src/lib/persist.ts:14-18] [^src: src/components/review/review-view.tsx:71-88] |
| Auto-resolve | CONFERMATA | `sweepResolvedReviews` (alla fine dell'ingest, secondo il commento; chiamante non letto) lavora sul progetto aperto. Fase 1: `missing-page` se la pagina esiste per id (stem minuscolo) o titolo; `duplicate` se manca una pagina interessata. Fase 2: LLM a lotti da 40, massimo 5 lotti, stop al primo lotto senza risolti; azioni `auto-resolved` e `llm-judged`. La fase 2 non filtra per tipo: la prudenza su contraddizioni, suggerimenti e conferme e' solo nel prompt. | [^src: src/lib/sweep-reviews.ts:182-184, 303-314, 342-433] |

## Contraddizione aperta (a): match del path del progetto su Windows (n. 10)

Il codice conferma n. 10 e contraddice «path esatto». Entrambi i lati sono normalizzati: `\` diventa `/` e le `/` finali sono tolte. Su build Windows il confronto ignora le maiuscole ASCII; su altre piattaforme e' esatto dopo la normalizzazione. Prima del confronto per path l'id e' provato in modo esatto. La condizione e' di compilazione (`cfg!(windows)`): non so con quale target sia costruito l'eseguibile osservato. [^src: src-tauri/src/api_server.rs:859-863, 867-875, 894-896]

## Contraddizione aperta (b): il rescan accoda l'ingest «a progetto attivo o inattivo» o «solo per il progetto aperto» (n. 16 e bozza)

Dipende da «Watch all projects»; il codice descrive entrambi i casi.
- **Progetto aperto**: il listener `file-sync://changed` ignora i progetti diversi da quello aperto; avvio e rescan manuale passano da `processFileChangeBatch` con ramo attivo. Il watcher parte solo se `config.enabled`. [^src: src/lib/project-file-sync.ts:62-66, 71-86, 183-201] [^src: src/App.tsx:534-540]
- **Progetti recenti non aperti**: se «Watch all projects» e' attivo, `scanInactiveProjects` ogni 60 s fa un rescan per ogni recente con `config.enabled` proprio, con `watch_roots_only=true` (limitato a `raw/sources`, `wiki`, `purpose.md`, `schema.md`), poi `processFileChangeBatch(..., false)` e `enqueueInactiveProjectBatch`. Anche qui vale `enabled && autoIngest`. [^src: src/lib/project-file-sync.ts:142-171, 256-265, 344, 357-369] [^src: src-tauri/src/commands/file_sync.rs:686-697] [^src: src/App.tsx:541-545]
- **Non deciso dal codice letto**: per un rescan via HTTP su un progetto non aperto, il Rust consuma i cambi e aggiorna lo snapshot, e l'evento e' scartato dal listener se il progetto non e' quello aperto. Se una scansione successiva li ritrovi non e' stato verificato (inferenza non promossa). [^src: src-tauri/src/api_server.rs:2896-2913] [^src: src-tauri/src/commands/file_sync.rs:946] [^src: src/lib/project-file-sync.ts:63-64]

## Righe della fonte sfasate

- n. 1: `se` 684 e' il punteggio dei vicini (`graph_score/(RRF_K+1)`); la condizione «RRF solo se `vector_hits>0`» e' a L464-472.
- n. 2: `se` 682 e' lo snippet «Graph neighbor of»; la quota e' a L541-553, usata a L634.
- n. 12: `as` 956 e' il 400 «Missing path»; il 403 e' a L958-960 e il 415 per estensione a L961-966.
- n. 15: `as` 522-529 e' `respond_error` (serve per l'assenza di `Retry-After`); il 503 «busy» e' a L112-114 e il 429 a L108-110.
- n. 25: `as` 857-863: il confronto `current` e' a L856 (zona 854-865).
- Le altre righe coincidono: n. 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 17, 19, 23, 24.

## Gap evidenti

- `handle_write_page`, `handle_chat` e `respond_chat_sse` non letti: n. 19 verificato su review, rescan ed embed; l'assenza di `Retry-After` non verificata sugli header SSE di successo.
- `enqueueInactiveProjectBatch` e un eventuale controllo LLM nel ramo inattivo non letti.
- Il chiamante di `sweepResolvedReviews` e `stable_review_id` in Rust non letti.
- Nome del file di coda dell'ingest e «progresso solo in UI»: non letti.
- Cosa passano i chiamanti come `sourceContent` alla cache di ingest: non letto.
- La riga della bozza sul 60 s e' una sintesi nel raw; il testo originale della skill (`api-reference.md` di alm-wiki) non e' stato letto.
- Eventuali condizioni a runtime (progetto aperto, impostazioni dell'utente) non sono verificabili dal solo codice.

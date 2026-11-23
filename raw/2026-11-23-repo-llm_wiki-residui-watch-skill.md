# Specifiche estratte: llm_wiki, residui sourceWatchConfig, "Watch all projects" e voci V (LWS-TSK-012)

> Documento generato da `repo-sync` v2.12 il 2026-11-23. Sorgente: /home/user/wiki-factory/code_repos/llm_wiki @ commit e08cfce65aad8b76b13546a081c1a8d4422b70c3 (ramo "HEAD", HEAD staccato, tag v0.6.13). Read-only verso la sorgente.

## Intestazione e identità
- **Nome**: llm_wiki (upstream v0.6.13). **Ultimo commit**: e08cfce, "release: v0.6.13" (2026-10-21).
- **Task**: LWS-TSK-012, seconda estrazione di LWS-US-008 (residui della verifica del 2026-11-22). Perimetro: default di `sourceWatchConfig`, «Watch all projects», voci V4, V20, V21, V22 della sintesi `llm-wiki-api-affermazioni-codice-da-verificare`.
- **Gap di riferimento**: `llm-wiki-source-watch-default`, `llm-wiki-watch-all-projects-residui`, `llm-wiki-affermazioni-codice-da-verificare`.
- **Stack**: typescript/react (frontend, `src/`), Rust/Tauri (`src-tauri/`). Confidence 0.7 ripresa dalle estrazioni precedenti.
- **Conferma di fase 4**: ricevuta dall'utente nel turno che ha lanciato questa estrazione (proposta approvata).

## Come leggere gli esiti
- Esiti: **confermato** (il codice letto fa ciò che il residuo chiede di verificare), **smentito**, **non conclusivo** (il codice letto non basta, e si dice cosa manca).
- Il confronto con le frasi della skill spetta all'ingest (US-008 AC4). Questo raw non corregge la skill e non tocca `llm_wiki_skill`.
- Percorsi relativi a `code_repos/llm_wiki/`. Sigle: `pfs` = `src/lib/project-file-sync.ts`, `fsr` = `src-tauri/src/commands/file_sync.rs`, `ps` = `src/lib/project-store.ts`, `swc` = `src/lib/source-watch-config.ts`, `iq` = `src/lib/ingest-queue.ts`.
- Nessuna prova in esecuzione: tutto è lettura del codice, nulla è stato eseguito. Citazione downstream: `[^src: raw/2026-11-23-repo-llm_wiki-residui-watch-skill.md §Tabella di sintesi]`.

## Default di sourceWatchConfig R1-R3

### R1 Valori di default: confermato
Fonte unica: `src/lib/source-watch-defaults.json`. Il frontend lo importa in `swc:4,6` (`DEFAULT_SOURCE_WATCH_CONFIG`); il backend lo incorpora con `include_str!` (`fsr:34-35`) e lo usa per `SourceWatchConfig::default()` (`fsr:139-144`), quindi i due lati non possono divergere sui default.
- `enabled: true`, `autoIngest: true`, `persistExtractedMarkdown: false`, `parsingConcurrency: 2`, `ingestConcurrency: 1`, `maxFileSizeMb: 100` (json 2-5, 72).
- **Estensioni incluse** (json 7-37, 29 voci): md, mdx, txt, org, pdf, doc, docx, docm, ppt, pps, pot, pptx, pptm, ppsx, ppsm, xls, xlsx, xlsm, xlsb, odt, odp, ods, rtf, html, htm, csv, png, jpg, jpeg.
- **Estensioni escluse** (json 38-53): tmp, temp, bak, swp, part, partial, crdownload, exe, dll, so, dylib, bin, iso, dmg.
- **Cartelle escluse** (json 54-64): .git, .svn, .hg, .obsidian, .idea, .vscode, node_modules, .cache, __pycache__.
- **Glob esclusi** (json 65-71): `~$*`, `.~lock.*#`, `*.draft.*`, `draft-*`, `*.private.*`.
- Normalizzazione: `parsingConcurrency` e `ingestConcurrency` passano da `clampUserConcurrency` (`swc:57-64`, il tetto sta in `concurrency-limits`, non letto); `maxFileSizeMb` limitato a 1..4096 (`swc:83`; lato Rust `fsr:184`). Il limite di dimensione si applica solo sotto `raw/sources/` (`fsr:1113-1119`).
- Compatibilità: se la lista salvata coincide con quella di default senza le tre immagini, `swc:36-38, 68-79` aggiunge png/jpg/jpeg.
- Il backend Rust deserializza solo sette campi (`fsr:120-137`); `persistExtractedMarkdown`, `parsingConcurrency` e `ingestConcurrency` esistono solo lato TypeScript.
- Il filtro TS scarta anche i nomi che iniziano con "." (`swc:125`); `should_watch_rel` (`fsr:1135-1177`) non ha quella regola, ma esclude `.llm-wiki/`, `wiki/media/`, `.ds_store`, `thumbs.db`, `desktop.ini` (1140-1153). Non verificato come i due filtri si compongano nel flusso reale.

### R2 Ripiego per un id progetto nuovo: confermato
`loadSourceWatchConfig(projectId)` (`ps:465-474`): 1) configurazione salvata per quell'id; 2) altrimenti la voce `default`; 3) altrimenti il vecchio interruttore `projectFileSyncEnabled` (`ps:442-452`, che a sua volta ripiega su `default` e poi su **true**) passato a `normalizeSourceWatchConfig({ enabled })`, cioè tutti i default sopra con `enabled` = valore legacy. Un progetto mai configurato quindi parte con osservazione attiva e `autoIngest` acceso. Salvataggio: `saveSourceWatchConfig` scrive sotto `projectId ?? "default"` (`ps:454-463`). In `App.tsx:519-524` un errore di lettura ripiega su `DEFAULT_SOURCE_WATCH_CONFIG`.

### R3 json, yaml, yml, xml: confermato (non inclusi di default)
Nessuna delle quattro compare in `includeExtensions` (json 7-37). Esistono come gruppo «data» nei gruppi di tipo mostrati dall'interfaccia (`swc:25-28`), insieme a epub e mobi nel gruppo documenti (`swc:11`), anch'essi assenti dal default. Con una lista di inclusione non vuota un file senza estensione o con estensione non elencata è scartato (`swc:128-130`; `fsr:1169-1173`). Quindi per default non vengono osservati né accodati.

## «Watch all projects» W1-W3

### W1 Default spento: confermato
Chiave `sourceWatchAllProjects` in `app-state.json` (`ps:8, 411`). `loadSourceWatchAllProjects()` restituisce `true` solo se il valore salvato è esattamente `true` (`ps:482-485`): chiave assente = spento. In `App.tsx:522-524` anche un errore di lettura vale `false`; l'avvio dello scan avviene solo se vero (`App.tsx:541-545`), altrimenti `stopAllProjectFileSync()`. Non letto: l'etichetta dell'interfaccia («Monitor all recent projects», dalla proposta approvata) e il valore iniziale nello store `wiki-store`.

### W2 Ramo inattivi: nessun controllo LLM né parsing all'accodamento: confermato
- `enqueueRawSourceChanges` (`pfs:337-381`): con `activeProject` falso chiama direttamente `enqueueInactiveProjectBatch` (`pfs:361-369`); con progetto attivo chiama `enqueueSourceIngest` (`pfs:357-360`).
- `enqueueSourceIngest` (`src/lib/source-lifecycle.ts:258-286`) è il punto che verifica un LLM utilizzabile (268) e preprocessa i file (284). Il ramo inattivi non passa di lì.
- `enqueueInactiveProjectBatch` (`iq:346-406`) scrive solo `pending` nel file di coda del progetto (396): il commento (341-345) dice che nessun lavoro del modello parte; se il progetto è nel frattempo diventato corrente, delega alla coda attiva (351-352, 362, 364).
- L'ingest parte alla riapertura: `restoreQueue` (`iq:994-1025`) rimette `processing` in `pending`, poi, se manca un LLM utilizzabile, marca i task con l'errore «LLM not configured» e **non** parte (1010-1022); altrimenti `processNext` (1024).
- Conseguenza: in background non si parsa né si invoca un modello per un progetto non aperto. Un errore nell'accodamento invalida il percorso nello snapshot per riprovare (`pfs:373-379`).

### W3 «Recenti», limite e cadenza: confermato
- «Recenti» = chiave `recentProjects` di `app-state.json` (`ps:9, 16-20`). `addToRecentProjects` toglie i duplicati per percorso e tiene al massimo **10** voci (`ps:34-42`).
- `startAllProjectFileSync` (`pfs:123-131`): un primo scan subito, poi `setInterval` a 60 s (`ALL_PROJECTS_SCAN_INTERVAL_MS`, `pfs:45`).
- `scanInactiveProjects` (`pfs:142-181`): salta il progetto attivo per id e percorso (147-153); per gli altri legge la config del progetto (156), salta se `enabled` è falso (157), chiama `rescanProjectFiles(..., true)` (158-163; il quarto argomento è `watchRootsOnly`, `src/commands/file-sync.ts:56-68`) e processa i cambi con `refreshActiveProject=false` (167). Una sola scansione alla volta (`allProjectsScanning`, 143-144).
- Lato Rust `watch_roots_only=true` esegue `enqueue_startup_rescan_changes` sui soli prefissi `raw/sources`, `wiki`, `purpose.md`, `schema.md` (`fsr:350-354, 686-697`).

## Voci V4/V20/V21/V22

### V4 Soglia del 5% nella ricerca: non conclusivo (solo per codice non letto)
`src-tauri/src/commands/search.rs:951-958` scarta un risultato solo se filename esatto, frase nel titolo, occorrenze nel contenuto e punteggi dei token sono tutti nulli; il punteggio è la somma pesata (960-970). Nel codice letto non esiste alcuna soglia relativa del 5%; il «5» è `TITLE_TOKEN_WEIGHT=5.0`, il moltiplicatore dei token nel titolo (969). Non conclusivo solo perché `vectorstore::vector_search_chunks` non è stato letto. La skill `code_repos/llm_wiki_skill` (f6a99c7) non afferma più il 5%: `SKILL.md:110-114` parla di pesi (200, 50, 20, ×5, ×1) e dice di non applicare una soglia fissa; `examples.md:56` dice lo stesso e parla di gap «2×+». Nessuna correzione necessaria.

### V20 «Non fare POST /chat (501)»: non conclusivo sulle versioni precedenti
`handle_chat` (`src-tauri/src/api_server.rs:2106-2126`) mappa gli errori in 400 «message is required» (2122), 499 «Agent turn cancelled» (2123), 502 (2124); `prepare_chat` (1995-2008) dà 404 progetto ignoto e 400 JSON non valido o messaggio vuoto. Nessun 501 sul percorso POST chat letto. Quel che dicevano le versioni precedenti non è decidibile dal solo commit e08cfce.

### V21 La scrittura esterna «bypassa il watcher»: smentito per il watcher; «accodate subito» non verificato
- Il watcher osserva la radice del progetto in modo ricorsivo (`fsr:295-297`) e `raw/sources` e `wiki` in modo supplementare (298-308). Ignora solo i percorsi marcati come scritture dell'app per 4 s (`mark_app_write_path`, `fsr:26, 450-459`; uso 477-480). Una scrittura esterna non è marcata, passa per `relative_watch_path` / `should_watch_rel` (1102-1177) ed entra in coda (494-513). In più c'è il rescan periodico (10 s su Linux, 60 s altrove; `fsr:32-33, 522-584`).
- Lo scope di `should_watch_rel`: `raw/sources/**` filtrato da config, più `purpose.md`, `schema.md` e `wiki/**/*.md` (`fsr:1164-1176`).
- Ingest: si accoda solo per `created` e `modified` di percorsi sotto `raw/sources/` (`pfs:346-350, 383-387`), con `enabled` e `autoIngest` veri (344). Le modifiche in `wiki/` non accodano nulla; per i file cancellati agisce `cleanupDeletedFiles` (`pfs:389-424`), che tocca anche pagine wiki.
- Non verificato: se le scritture del server API (`api_server.rs`) marchino i percorsi come scritture dell'app; il tempo effettivo («subito»): ci sono debounce di 700 ms lato Rust (`fsr:221`) e 250 ms lato TS (`pfs:209-225`), e nel progetto attivo il parsing e il controllo LLM (`source-lifecycle.ts:268, 284`) precedono l'accodamento.

### V22 Corsa review / auto-save: meccanismo possibile; osservazione del 2026-11-10 non decidibile
- Lato UI: ogni cambio dello store review riscrive l'intero `.llm-wiki/review.json` dopo 1 s di debounce (`src/lib/auto-save.ts:84-94`) con `saveReviewItems`, che fa `writeFile` dell'array intero (`src/lib/persist.ts:14-18`). Auto-save è sospeso durante il cambio progetto (`auto-save.ts:11-17, 30-57`).
- Lato API: `resolve_review_items` (`api_server.rs:1728-1778`) legge `review.json`, modifica gli elementi e riscrive il file (1733-1764), in lettura-modifica-scrittura senza coordinamento con la UI nel codice letto.
- Quindi per costruzione una risoluzione via API può essere sovrascritta dal prossimo salvataggio della UI se lo store non è stato ricaricato. Che sia successo il 2026-11-10 non si decide dal codice. Non letto: come lo store si riallinei al file (`review-store.ts`) e il comportamento con DELETE.

## Fuori perimetro: osservazioni collaterali sul ramo inattivi
Non fanno parte dei residui; sono annotate perché emerse leggendo il flusso, senza giudizio.
1. `cleanupDeletedFiles` (`pfs:264, 389-424`) agisce sulle cancellazioni anche senza alcuna condizione su `autoIngest`: la condizione `enabled && autoIngest` è solo in `enqueueRawSourceChanges` (344), chiamata dopo.
2. `autoIngest` falso è valutato **dopo** il rescan: `process_queue` aggiorna lo snapshot per ogni task (`fsr:946`) prima che il TS riceva i `changedTasks`; l'invalidazione del percorso nello snapshot avviene solo se l'accodamento lancia un errore nel ramo inattivi (`pfs:373-379`). Perciò i cambi già visti con `autoIngest` spento risultano consumati nello snapshot.
3. Il filtro `isSensitiveConfigSourceFile` sta in `enqueueSourceIngest` (`source-lifecycle.ts:271-273`); il ramo inattivi non lo richiama nel codice letto (non verificato se `isIngestableSourcePath` lo includa).

## Tabella di sintesi residuo/esito/file:righe
| Residuo | Esito | File:righe |
|---|---|---|
| R1 default | confermato | source-watch-defaults.json 2-72; swc 6, 57-83; fsr 34-35, 139-144, 184 |
| R2 ripiego id nuovo | confermato | ps 442-474; App.tsx 519-524 |
| R3 json/yaml/yml/xml | confermato (non inclusi) | json 7-37; swc 25-28, 128-130 |
| W1 default spento | confermato | ps 482-485; App.tsx 522-524, 541-545 |
| W2 nessun LLM né parsing | confermato | pfs 357-369; source-lifecycle 268, 284; iq 346-406, 1009-1022 |
| W3 recenti, 10, 60 s | confermato | ps 34-42; pfs 45, 123-181; fsr 350-354, 686-697 |
| V4 soglia 5% | non conclusivo (vectorstore non letto) | search.rs 951-970; SKILL.md 110-114; examples.md 56 |
| V20 501 | non conclusivo (versioni precedenti) | api_server.rs 1995-2008, 2106-2126 |
| V21 bypass watcher | smentito per il watcher; «subito» non verificato | fsr 295-308, 450-459, 494-513, 1135-1177; pfs 344-350, 383-387 |
| V22 corsa review/auto-save | possibile per costruzione; osservazione non decidibile | auto-save 84-94; persist 14-18; api_server 1728-1778 |

## Prove in esecuzione non pianificate «non verificate»
Nessuna è stata eseguita e nessuna entra nella skill (US-008 AC3). Restano «non verificate»:
- scritture con token (`pages/write`, `pages/embed`);
- chat: risposta JSON, SSE, cancel, 502, tetto di 8 stream;
- `pages/embed` ed embedding attivi;
- 429 e 503 sotto carico;
- 413 e 415 sul contenuto, `rtf` compreso;
- bind LAN e `allowUnauthenticated`;
- rescan su progetto non aperto, con l'opzione «Watch all projects» spenta e accesa;
- corsa review/auto-save, anche con DELETE.

## Copertura file letti/non letti
**Letti (15)**: `src/lib/source-watch-defaults.json`, `src/lib/source-watch-config.ts`, `src/lib/project-store.ts` (1-130, 380-529), `src/App.tsx` (505-568), `src/lib/project-file-sync.ts` (intero), `src/commands/file-sync.ts` (intero), `src/lib/ingest-queue.ts` (330-420, 990-1040), `src/lib/source-lifecycle.ts` (250-300), `src/lib/auto-save.ts` (intero), `src/lib/persist.ts` (1-120), `src-tauri/src/commands/file_sync.rs` (1-70, 100-1250), `src-tauri/src/commands/search.rs` (935-985), `src-tauri/src/api_server.rs` (1720-1780, 1995-2010, 2100-2130), `code_repos/llm_wiki_skill/SKILL.md` (108-119), `code_repos/llm_wiki_skill/examples.md` (50-61).

**Non letti**: `commands/vectorstore.rs` (V4), `stores/wiki-store.ts` (valori iniziali), `stores/review-store.ts` e `sweep-reviews.ts` (V22), `lib/concurrency-limits`, `isIngestableSourcePath` e `isSensitiveConfigSourceFile`, `en.json` (etichette), tabella delle route di `api_server.rs` e i percorsi di scrittura del server API (V21), `agent/runtime.rs`, `cors.rs`, `server_bind.rs`.

Controllo segreti: nessun segreto incontrato né riportato. Repo cliente non modificato da questa estrazione.

## Gap evidenti
1. V4: `vectorstore::vector_search_chunks` non letto, quindi nessuna soglia relativa è esclusa per il percorso vettoriale.
2. V20: comportamento di POST chat nelle versioni precedenti a e08cfce non decidibile dal repo.
3. V21: se le scritture del server API marchino i percorsi come scritture dell'app; tempi reali di accodamento; `isIngestableSourcePath`.
4. V22: ricarica dello store review dal file, effetto di DELETE, chiamante di `sweepResolvedReviews`.
5. W1: etichetta dell'interfaccia e valore iniziale di `sourceWatchAllProjects` nello store.
6. R1: valore massimo di `clampUserConcurrency`.
7. Tutte le prove in esecuzione elencate sopra.

Estrazione completata. Invoca `wiki-keeper` per l'ingest L1→L2.

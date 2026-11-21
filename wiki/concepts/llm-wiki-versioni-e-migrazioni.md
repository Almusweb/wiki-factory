---
id: llm-wiki-versioni-e-migrazioni
type: concept
title: llm-wiki — versioni di formato e migrazioni
status: draft
created: 2026-11-20
updated: 2026-11-21
sources: ["raw/2026-11-20-repo-llm_wiki.md", "raw/2026-11-20-repo-llm_wiki-persistenza-b.md", "raw/2026-11-20-repo-llm_wiki-persistenza-c.md", "raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md", "raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md", "raw/2026-11-21-issues-llm_wiki-chiuse.md"]
tags: [llm-wiki, dati, migrazioni, db]
---

# llm-wiki — versioni di formato e migrazioni
> Le versioni di formato esplicite sono solo due (`version: 1` in `scheduled-import-db.json` e il suffisso `_v2` della tabella LanceDB); per il resto la compatibilità è affidata a campi opzionali, normalizzatori tolleranti e valori di default.

## Contesto
Pagina ricavata dalla seconda estrazione, mirata alla persistenza, sul commit `e08cfce`. Descrive come i dati su file cambiano formato nel tempo. Gli archivi sono elencati in [[llm-wiki-archivi-persistenza]]. [^src: raw/2026-11-20-repo-llm_wiki.md §Versioni di formato e migrazioni]

## Dettaglio

### LanceDB v1 verso v2
- Non c'è una migrazione automatica dei dati: c'è una procedura di ricostruzione. Il commento di `vectorstore.rs` dice che il v1 è mantenuto perché i progetti precedenti alla 0.3.11 si carichino ancora. [^src: raw/2026-11-20-repo-llm_wiki.md §Versioni di formato e migrazioni]
- `vector_legacy_row_count` rileva righe v1. Dal commento, la UI di Settings → Embedding mostra un invito a ri-indicizzare dopo l'aggiornamento (la UI non è nel campione). [^src: raw/2026-11-20-repo-llm_wiki.md §Versioni di formato e migrazioni]
- Il re-index (`embedAllPages` con `clearExisting`, in `embedding.ts`) svuota il v2, riscrive i chunk e poi elimina il v1 con `vector_drop_legacy`, in modalità «best effort». [^src: raw/2026-11-20-repo-llm_wiki.md §Versioni di formato e migrazioni]
- `vector_upsert` (v1) esiste ancora e non è marcata come deprecata nel codice. Nel campione non ha chiamanti: vedi gap `llm-wiki-vector-v1-chiamanti` in [[gaps]]. [^src: raw/2026-11-20-repo-llm_wiki.md §Versioni di formato e migrazioni]

### Identificatore di pagina
Nel v2 è il percorso relativo sotto `wiki/` senza `.md` (funzione `wikiPageIdFromPath` in `embedding.ts`, `vector_page_id` in `page_embedding.rs`); nel v1 era il nome base. `removeLegacyVectorIdIfSafe` (presente sia in TS sia in Rust) elimina le righe con id «nome base» solo se esiste esattamente una pagina con quel nome. [^src: raw/2026-11-20-repo-llm_wiki.md §Versioni di formato e migrazioni]

### Chat
`loadChatHistory` (`persist.ts`) legge, in ordine: il formato corrente; poi, in caso di errore, la ricostruzione dai file orfani; infine il vecchio `chat-history.json` in due forme (array piatto, migrato in una conversazione `default` chiamata «Previous Conversations»; oggetto combinato). La migrazione è solo in lettura: dal campione non risulta che riscriva il formato nuovo né cancelli il vecchio file. [^src: raw/2026-11-20-repo-llm_wiki.md §Versioni di formato e migrazioni]

### Review
`normalizeReviewItems` e `setItems` (`review-store.ts`) ricalcolano ogni id da un hash del contenuto (tipo più titolo normalizzato), eliminando i vecchi id numerici; gli elementi con lo stesso id si fondono («resolved» vince, array uniti, `createdAt` minimo). L'operazione è idempotente, senza flag di versione. [^src: raw/2026-11-20-repo-llm_wiki.md §Versioni di formato e migrazioni]

### Impostazioni in `app-state.json` (`project-store.ts`)
- `loadScheduledImportConfig` copia la chiave globale `scheduledImportConfig` (formato precedente alla 0.4.8) nella chiave per progetto e cancella quella globale.
- `loadSourceWatchConfig` ricade su `projectFileSyncEnabled` se non c'è una configurazione di source watch.
- `normalizeSourceWatchConfig` (`source-watch-config.ts`) aggiunge png, jpg e jpeg se le estensioni coincidono con i vecchi default.

[^src: raw/2026-11-20-repo-llm_wiki.md §Versioni di formato e migrazioni]

### `scheduled-import-db.json` e coda di ingest
- `statCache` è opzionale e additivo: i database di build precedenti ne sono privi e vengono ricalcolati una volta. Le chiavi con maiuscole e minuscole su Windows sono normalizzate in lettura. Resta il riferimento a una cartella legacy `.llm-wiki-imported`. [^src: raw/2026-11-20-repo-llm_wiki.md §Versioni di formato e migrazioni]
- `loadQueue` assegna ai task senza `projectId` quello del progetto aperto. [^src: raw/2026-11-20-repo-llm_wiki.md §Versioni di formato e migrazioni]

## Pagine collegate
[[llm-wiki-archivi-persistenza]], [[llm-wiki-operazioni-distruttive]], [[llm-wiki-rischi-persistenza]], [[llm-wiki-schema-dati]]. Gap: [[gaps]] (`llm-wiki-file-citati-non-verificati` e `llm-wiki-vector-v1-chiamanti` chiusi con riserva il 2026-11-21).

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->
- US-016 — Chiamanti delle operazioni distruttive e dei percorsi legacy (gap `llm-wiki-vector-v1-chiamanti`)
- US-020 — Schema degli archivi vettoriali e delle revisioni di embedding
- US-024 — Versioni di formato e regole di compatibilità
- US-031 — Rischio 7: cambio di modello o di dimensione dell'embedding

## Aggiornamenti (v2026-11-20)
Dalle fette B e C delle estrazioni mirate sulla persistenza ([[2026-11-20-repo-llm_wiki-persistenza-b]], [[2026-11-20-repo-llm_wiki-persistenza-c]]). Il testo sopra non è modificato; qualificatori come nel raw. Il gap `llm-wiki-vector-v1-chiamanti` non è chiuso qui.

### Altri campi `version`
`file-snapshot.json` e `file-change-queue.json` hanno `version`, e `read_snapshot` e `read_queue` portano `version` da 0 a 1; i checkpoint `ingest-progress` e `ingest-generation` hanno `version: 1`. Sono archivi non presenti nell'inventario di [[llm-wiki-archivi-persistenza]]; il comportamento è in [[llm-wiki-sincronizzazione-file]]. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Sincronizzazione e osservazione dei file]

### Forme di chiave e marcatori di versione
La cache delle didascalie ha due forme di chiave: l'hash SHA-256 dei byte (legacy) oppure l'hash seguito da `::language:` e lingua codificata. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Cache di ingest, didascalie e checkpoint]

La validità della cache Office `.cache` dipende dal marcatore `.txt.parser` con la versione del parser: senza marcatore valido, o con versione diversa, la cache Office non si usa. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §File e cartelle citati e non verificati]

### LanceDB v1: chiamanti
Nell'ambito cercato (sorgenti non di test sotto `src` e `src-tauri/src`; fuori `mcp-server`, `extension`, `scripts` e i test) né `vector_upsert` né `vector_delete` (v1) hanno chiamanti: nessuna invocazione per nome nel TS e, in Rust, solo definizioni e test di `vectorstore.rs` e registrazione nell'elenco dei comandi di `lib.rs` (`:672` e `:674`). Il comando è comunque esposto al frontend, quindi un chiamante esterno al sorgente cercato resta possibile. La cancellazione della tabella v1 avviene con `vector_drop_legacy` (`embedAllPages` `:632` letto; `EmbeddingSection` `:138` solo mappa). Lo zero vale per la stringa esatta. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Vecchio formato vettoriale (v1): chiamanti]

### Identificatore di pagina
`removeLegacyVectorIdIfSafe` agisce solo se l'id contiene `/` e se una sola pagina possiede lo stem; usa `vector_delete_page`, quindi cancella righe con id legacy nella tabella v2, non nella v1. Parte da `removePageEmbedding` e anche dopo ogni `vectorUpsertPageChunks`; un tentativo per progetto e id (memoria di sessione), ripetibile se fallisce. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Contraddizioni con la wiki]

### Spostamento di sorgenti
`migrateSourcePath` (rinomina o spostamento di una sorgente) riscrive `sources:` nelle pagine che la citano, sposta il riepilogo, la voce di `ingest-cache` e la copia in `raw/parsed`; rifiuta se la destinazione esiste; ha un rollback best effort per errori prima degli ultimi passi. `moveParsedMarkdown` (chiamato da `migrateSourcePath` secondo graphify) scrive la nuova copia in modo atomico e poi cancella la vecchia, tollerando l'errore di cancellazione. È una migrazione di percorsi, non di formato. Dettaglio in [[llm-wiki-cancellazione-pagine-e-sorgenti]]. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Ciclo di vita delle sorgenti]

## Aggiornamenti (v2026-11-21)
Dalle fette C1 ed E del giro del 2026-11-21 ([[2026-11-21-repo-llm_wiki-fs-lib-progetto]], [[2026-11-21-repo-llm_wiki-ricerca-ui-residui]], commit `e08cfce`). Il testo sopra non è modificato. Il gap `llm-wiki-vector-v1-chiamanti` non è chiuso: resta aperto in [[gaps]] (parziale).

### Comandi vector v1 e v2
- In `lib.rs` sono registrati i comandi v1 `vector_upsert`, `vector_search`, `vector_delete`, `vector_count` e i v2 `vector_upsert_chunks`, `vector_search_chunks`, `vector_delete_page`, `vector_count_chunks`, `vector_clear_chunks`, `vector_optimize_chunks`, `vector_legacy_row_count`, `vector_drop_legacy`. [^src: raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md §Vector v1 vs v2 (gap 17)]
- `src/lib/embedding.ts` (letto intero dalla fetta C1) non invoca i comandi v1: usa solo i v2 ed elimina la tabella legacy v1 dopo un rebuild forzato. Non sono verificati altri chiamanti TS, `api_server.rs`, `agent/tools.rs`, `search.rs` e `mcp-server`; non si esclude un uso interno Rust dei v1. [^src: raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md §Vector v1 vs v2 (gap 17)]
- `vector_legacy_row_count` e `vector_drop_legacy` sono usati da `embedding-section.tsx`; i comandi v1 restano presenti e testati, con chiamanti applicativi non verificati. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Chiamanti (gap chiamanti-non-verificati, parziale)]
- `chat-history.json` è un formato legacy letto da `loadChatHistory` ma non più scritto da `saveChatHistory`; posizione `<project>/.llm-wiki/chat-history.json` (dettaglio in [[llm-wiki-archivi-persistenza]]). [^src: raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md §Storia dei file e persistenza in `.llm-wiki` (gap 13 parziale, gap 23 posizione)]

## Aggiornamenti (v2026-11-21, TSK-025)
Dal dossier [[2026-11-21-repo-llm_wiki-dossier-ep004-r7]] (commit `e08cfce`, sola lettura). Il testo sopra non è modificato. **Cambio di modello o dimensione dell'embedding:** lo schema della tabella v2 non registra il modello né la dimensione dichiarata (`vectorstore.rs:382-395`) e nessun codice Rust legge lo schema esistente; non c'è quindi alcuna migrazione né rilevazione del cambio: l'unico percorso è il re-index manuale con eliminazione e ricreazione della tabella. Che LanceDB accetti una dimensione nuova dopo `drop_table` o rifiuti una scrittura con dimensione diversa è **non conclusivo per lettura**. Esito completo in [[llm-wiki-rischi-persistenza]] §Esito della verifica di US-031. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r7.md §1. Scrittura con dimensione diversa nella tabella esistente (AC2)] [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r7.md §7. Esito proposto e tabella evidenze (AC5, AC6)]

## Aggiornamenti (v2026-11-21, issue chiuse)
Dalla source page [[2026-11-21-issues-llm_wiki-chiuse]] (upstream v0.6.13, commit `e08cfce`, branch `develop` coincidente con `main`). Il testo sopra non è modificato. Le voci «Dichiarato» sono dichiarazioni di segnalatore o maintainer con la versione indicata nell'issue, non osservazioni; «Osservato v0.6.13» è letto nel codice e mai eseguito.

### Identificatore di pagina: storia dichiarata e regole osservate
- **Dichiarato (segnalatore), #394 e #396, v0.4.23:** 447 pagine su 6.566 (6,8%) rifiutate dalla validazione di `page_id`, che allora ammetteva solo lettere, cifre, `-`, `_`, `.`; rifiuto silenzioso. **Dichiarato (maintainer), #396, chiusa 2026-06-16, v0.4.24:** validazione allargata, rifiuta solo caratteri pericolosi per i percorsi e di controllo. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §4. Nomi di pagina rifiutati dall'indice vettoriale (gap `llm-wiki-reindex-page-id-concorrenza-reale`)]
- **Dichiarato (segnalatore), #770, v0.6.11:** pagine con lo stesso nome di file in cartelle diverse (anche solo per maiuscole) rifiutate dall'API di embedding con 409; nell'ingest, sovrascrittura silenziosa dei vettori. **Dichiarato (maintainer), #770, chiusa 2026-09-27, v0.6.12:** identità di pagina con la cartella, in API, ingest, ricerca, cancellazione, revisioni e sincronizzazione. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §4. Nomi di pagina rifiutati dall'indice vettoriale (gap `llm-wiki-reindex-page-id-concorrenza-reale`)]
- **Osservato v0.6.13, regola di validazione:** `validate_page_id_common` rifiuta solo stringa vuota, oltre 256 caratteri (`vectorstore.rs:67`), caratteri di controllo, `\`, `'`, `"` e un insieme di caratteri invisibili o di formattazione (`vectorstore.rs:78-114`); ideogrammi e punteggiatura CJK passano. Il 6,8% vale per la regola di v0.4.23, non per quella attuale (deduzione non testata). [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §4. Nomi di pagina rifiutati dall'indice vettoriale (gap `llm-wiki-reindex-page-id-concorrenza-reale`)]
- **Osservato v0.6.13, la coppia TS e Rust:** `wikiPageIdFromPath` (`embedding.ts:450-462`) e `vector_page_id` (`page_embedding.rs:282-290`) danno lo stesso id nel caso normale `wiki/<cartella>/<nome>.md` (percorso relativo a `wiki/` senza `.md`). Differenze nei casi limite, per costruzione e non eseguite: il nome nudo senza `wiki/` è accettato da TS e rifiutato da Rust; un percorso senza `.md` dà un id in TS e nessun id in Rust; le barre finali sono tolte solo da Rust; `\` è convertita da Rust e, in TS, dipende da `normalizePath` (non letto). Gap `llm-wiki-coppie-id-pagina-non-confrontate` chiuso in [[gaps]], con i residui in `llm-wiki-coppie-id-casi-limite`. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §5. Id di pagina TS e Rust (gap `llm-wiki-coppie-id-pagina-non-confrontate`)]

## Contradictions
- **Identificatore di pagina «nel v2 è il percorso relativo, nel v1 era il nome base» (§Identificatore di pagina, riga 27).** Prima: la distinzione è attribuita alle tabelle v1 e v2, senza versione dell'app. Ora (dichiarato, #770): i vettori collidevano fra cartelle con lo stesso nome di file ancora in v0.6.11, e l'identità con la cartella è dichiarata come uscita in v0.6.12 per API, ingest, ricerca, cancellazione, revisioni e sincronizzazione. **Non risolvibile con questo raw:** non si sa se i due piani coincidano o se l'id con la cartella sia stato introdotto per fasi; per la v0.6.13 vale quanto osservato sopra (percorso relativo a `wiki/` senza `.md`). [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §4. Nomi di pagina rifiutati dall'indice vettoriale (gap `llm-wiki-reindex-page-id-concorrenza-reale`)]
- **Versioni di formato esplicite.** Prima (tesi della pagina): «le versioni di formato esplicite sono solo due (`version: 1` in `scheduled-import-db.json` e il suffisso `_v2`)». Ora (fetta B): altri campi `version` in `file-snapshot.json`, `file-change-queue.json`, `ingest-progress` e `ingest-generation` (vedi sopra). Il numero di versioni esplicite va rivisto; la stessa frase è in [[llm-wiki-schema-dati]] e nel sommario di [[llm-wiki-archivi-persistenza]]. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Sincronizzazione e osservazione dei file]
- **`.llm-wiki-imported`.** Prima (sezione `scheduled-import-db.json`): «Resta il riferimento a una cartella legacy `.llm-wiki-imported`». Ora (fetta B, letto): non esiste come archivio con campi; è un nome (`LEGACY_DB_DIR`) escluso dalla scansione dell'import pianificato; l'unico uso a riga 235 viene dalla sessione e l'origine legacy è dedotta dal nome. Dettaglio in [[llm-wiki-archivi-persistenza]]. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Punto 7: `.llm-wiki-imported`]
- **`vector_upsert` senza chiamanti.** Prima (quarto punto di «LanceDB v1 verso v2»): «Nel campione non ha chiamanti». Ora (fetta C): nessun chiamante nell'ambito cercato, comandi registrati e quindi esposti (evidenza più ampia dello stesso esito; per `vector_delete` e per la riga «Chiamate legacy» di `vector_upsert` vedi [[llm-wiki-operazioni-distruttive]]). [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Contraddizioni con la wiki]

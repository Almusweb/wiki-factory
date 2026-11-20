---
id: llm-wiki-versioni-e-migrazioni
type: concept
title: llm-wiki — versioni di formato e migrazioni
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: ["raw/2026-11-20-repo-llm_wiki.md", "raw/2026-11-20-repo-llm_wiki-persistenza-b.md", "raw/2026-11-20-repo-llm_wiki-persistenza-c.md"]
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
[[llm-wiki-archivi-persistenza]], [[llm-wiki-operazioni-distruttive]], [[llm-wiki-rischi-persistenza]], [[llm-wiki-schema-dati]]. Gap aperti: [[gaps]] (`llm-wiki-file-citati-non-verificati`, `llm-wiki-vector-v1-chiamanti`).

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

## Contradictions
- **Versioni di formato esplicite.** Prima (tesi della pagina): «le versioni di formato esplicite sono solo due (`version: 1` in `scheduled-import-db.json` e il suffisso `_v2`)». Ora (fetta B): altri campi `version` in `file-snapshot.json`, `file-change-queue.json`, `ingest-progress` e `ingest-generation` (vedi sopra). Il numero di versioni esplicite va rivisto; la stessa frase è in [[llm-wiki-schema-dati]] e nel sommario di [[llm-wiki-archivi-persistenza]]. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Sincronizzazione e osservazione dei file]
- **`.llm-wiki-imported`.** Prima (sezione `scheduled-import-db.json`): «Resta il riferimento a una cartella legacy `.llm-wiki-imported`». Ora (fetta B, letto): non esiste come archivio con campi; è un nome (`LEGACY_DB_DIR`) escluso dalla scansione dell'import pianificato; l'unico uso a riga 235 viene dalla sessione e l'origine legacy è dedotta dal nome. Dettaglio in [[llm-wiki-archivi-persistenza]]. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Punto 7: `.llm-wiki-imported`]
- **`vector_upsert` senza chiamanti.** Prima (quarto punto di «LanceDB v1 verso v2»): «Nel campione non ha chiamanti». Ora (fetta C): nessun chiamante nell'ambito cercato, comandi registrati e quindi esposti (evidenza più ampia dello stesso esito; per `vector_delete` e per la riga «Chiamate legacy» di `vector_upsert` vedi [[llm-wiki-operazioni-distruttive]]). [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Contraddizioni con la wiki]

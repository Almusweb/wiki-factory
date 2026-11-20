---
id: llm-wiki-versioni-e-migrazioni
type: concept
title: llm-wiki — versioni di formato e migrazioni
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: ["raw/2026-11-20-repo-llm_wiki.md"]
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

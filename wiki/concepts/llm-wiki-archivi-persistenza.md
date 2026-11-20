---
id: llm-wiki-archivi-persistenza
type: concept
title: llm-wiki — archivi di persistenza
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: ["raw/2026-11-20-repo-llm_wiki.md"]
tags: [llm-wiki, dati, persistenza, db]
---

# llm-wiki — archivi di persistenza
> I dati di `llm-wiki` vivono su file: 17 archivi per progetto in `.llm-wiki/` più lo store `app-state.json` del plugin Tauri; una sola versione di formato è dichiarata in modo esplicito.

## Contesto
Pagina ricavata dalla seconda estrazione di `repo-sync`, mirata al layer di persistenza, sullo stesso commit `e08cfce` (ramo `develop`). Il campione di questo giro è di 21 file, tutti sotto 50.000 byte. Il repository è di terzi, sotto GNU GPL v3: la pagina riporta solo nomi di file, simboli e campi, con parole proprie. [^src: raw/2026-11-20-repo-llm_wiki.md §Premessa e perimetro]

Convenzioni del raw: tutti gli archivi in `<progetto>/.llm-wiki/` sono per progetto; «TS» indica il frontend, «RS» il backend Rust; dove non è dichiarata una versione di formato il raw scrive «nessuna». Il file di dati mancante o illeggibile viene letto quasi ovunque in modo silenzioso, con valore vuoto o di default. [^src: raw/2026-11-20-repo-llm_wiki.md §Inventario degli archivi]

## Dettaglio

### Inventario
| Archivio | Posizione | Scrive / legge | Schema o campi | Versione | Corruzione |
|---|---|---|---|---|---|
| Tabella LanceDB v2 `wiki_chunks_v2` | `.llm-wiki/lancedb` | RS scrive e legge (`vectorstore.rs`); comandi invocati da TS (`embedding.ts`) e da RS (`page_embedding.rs`) | `chunk_id` (page_id + "#" + chunk_index, solo debug), `page_id`, `chunk_index` (u32), `chunk_text`, `heading_path`, `vector` (lista a lunghezza fissa di f32; dimensione presa dal primo chunk) | solo il suffisso `_v2` del nome | Non gestita: errori di apertura propagati come stringa; search e count su tabella assente restituiscono vuoto o 0 |
| Tabella LanceDB v1 `wiki_vectors` (legacy) | `.llm-wiki/lancedb` | RS scrive (`vector_upsert`, ancora presente) e legge; TS solo conteggio e drop | `page_id`, `vector`; una riga per pagina, id = nome base del file | `_v1` implicito | Come sopra |
| Revisioni embedding | `.llm-wiki/embedding-revisions/<sha256(page_id)>.revision` | RS scrive (file temporaneo e rinomina) e legge; TS non lo usa | Testo semplice: impronta `sha256:` calcolata su revisione del contenuto, endpoint, modello, dimensione di output, header extra, dimensione e sovrapposizione dei chunk; la chiave API è esclusa | nessuna | Illeggibile o vuoto: trattato come assente, quindi la pagina viene ri-incorporata |
| `project.json` | `.llm-wiki/project.json` | TS scrive e legge (`project-identity.ts`); RS non lo legge | `id` (UUID), `createdAt` (ms) | nessuna | Mancante o corrotto: genera un nuovo UUID e sovrascrive; se la scrittura fallisce avvisa e restituisce comunque l'id |
| `ingest-queue.json` | `.llm-wiki/ingest-queue.json` | TS (`ingest-queue.ts`) | Elenco di task: `id`, `projectId`, `sourcePath` (relativo), `folderContext`, `status` (pending, processing, done, failed, cancelled), `addedAt`, `error`, `retryCount`; i task `done` non vengono salvati | nessuna | Illeggibile: coda vuota; il salvataggio successivo sovrascrive il file |
| `ingest-cache.json` | `.llm-wiki/ingest-cache.json` | TS (`ingest-cache.ts`) | `entries`, per nome sorgente: `hash` (SHA-256 del contenuto), `timestamp`, `filesWritten[]` | nessuna | Illeggibile: cache vuota (costo solo di ri-ingest); gli errori di salvataggio sono ignorati |
| `review.json` | `.llm-wiki/review.json` | TS (`persist.ts`, `review-store.ts`) | Elenco di review: `id`, `type` (contradiction, duplicate, missing-page, confirm, suggestion), `title`, `description`, `sourcePath?`, `affectedPages?`, `searchQueries?`, `options[]` (label, action), `resolved`, `resolvedAction?`, `createdAt` | nessuna | Illeggibile: elenco vuoto |
| `lint.json` | `.llm-wiki/lint.json` | TS (`persist.ts`) | Elenco di `LintItem` (tipo in `lint-store.ts`, non letto) | nessuna | Illeggibile: elenco vuoto |
| `lint-config.json` | `.llm-wiki/lint-config.json` | TS (`lint-config.ts`), scrittura atomica | `ignoreOrphan`, `ignoreNoOutlinks`, `ignorePages[]` | nessuna | Illeggibile: valori di default, con avviso in console |
| Chat | `.llm-wiki/conversations.json` e `.llm-wiki/chats/<id>.json` | TS (`persist.ts`, `chat-store.ts`) | Conversazione: `id`, `title`, `createdAt`, `updatedAt`, `selectedSkills?`, `contextFiles?`. Messaggio: `id`, `role`, `content`, `timestamp`, `conversationId`, `references?`, `agentSteps?`, `agentFileChanges?`, `userInputRequest?`, `contextFiles?`. Immagini e contenuti prima/dopo delle modifiche dell'agente non vengono persistiti | nessuna | Ricostruzione dell'indice dai file orfani, vedi [[llm-wiki-gestione-file-corrotti]] |
| `chat-preferences.json` | `.llm-wiki/chat-preferences.json` | TS (`persist.ts`) | `useWebSearch`, `useAnyTxtSearch`, `agentMode`, `retrievalMode`, `selectedSkills`, `disabledSkills` | nessuna | Illeggibile: default; valori normalizzati in lettura |
| `dedup-not-duplicates.json` | `.llm-wiki/dedup-not-duplicates.json` | TS (`dedup-storage.ts`) | Array di array di slug (gruppi «non sono duplicati») | nessuna | Illeggibile o forma errata: elenco vuoto; il salvataggio successivo sovrascrive |
| `scheduled-import-db.json` | `.llm-wiki/scheduled-import-db.json` | TS (`scheduled-import.ts`), scrittura atomica | `version`, `directories` (chiave: percorso normalizzato; valore: `files` percorso-md5, `statCache` size e mtime, `lastScan`); si salva solo la directory attiva | **`version: 1`**, unica versione di formato esplicita nel campione | Illeggibile: store vuoto con avviso; la scansione successiva riconsidera tutto come nuovo |
| `history-settings.json` | `.llm-wiki/history-settings.json` | RS (`file_history.rs`) | `enabled` (default falso), `maxVersionsPerFile` (default 10, massimo 30) | nessuna | Illeggibile o symlink: default |
| Cronologia file | `.llm-wiki/history/<hash FNV-1a a 64 bit del percorso relativo>.json` | RS scrive e legge; TS via comandi | Array di voci: `id`, `path`, `timestamp` (ms), `author`, `tool`, `content` (fino a 512 KB); non registra file sotto `.llm-wiki` | nessuna | File illeggibile: saltato o trattato come vuoto; rifiuta symlink |
| Sessioni agente | `.llm-wiki/agent-sessions/<id>.json` | RS (`agent/session.rs`); chiamanti in `runtime.rs`, non letto | `sessionId`, `projectId`, `messages[]` (`role`, `content`, `timestamp`), `updatedAt`; solo gli ultimi 40 messaggi; l'id viene sanitizzato | nessuna (`sessionId` e `projectId` con default per file vecchi) | Vedi [[llm-wiki-gestione-file-corrotti]] |
| `app-state.json` | Store del plugin Tauri (cartella dati dell'app; percorso non verificato) | TS scrive quasi tutto (`project-store.ts`, `project-identity.ts`); RS legge `proxyConfig` e `apiConfig` (per i commenti di `project-store.ts`: `apiConfig` a ogni richiesta, con cache di 5 secondi) | Chiavi elencate sotto | nessuna | Gestione del plugin non verificata; `loadRegistry` ritorna un registro vuoto se la lettura fallisce |

Fonte di tutte le righe della tabella: [^src: raw/2026-11-20-repo-llm_wiki.md §Inventario degli archivi]

### Chiavi di `app-state.json`
Elenco dai file `project-store.ts` e `project-identity.ts`. [^src: raw/2026-11-20-repo-llm_wiki.md §Schemi e campi]
- `recentProjects` (massimo 10) e `lastProject`: oggetti con `id`, `name`, `path`.
- `projectRegistry`: per id, `id`, `path`, `name`, `lastOpened`.
- Configurazione LLM: `llmConfig`, `providerConfigs`, `activePresetId`, `taskModelRouting` (`chatPresetId`, `ingestPresetId`), `projectLlmOverrides` (per id progetto: `enabled`, `presetId`, `model`, `profile`), `customLlmPresets` (massimo 50, voci `id` con prefisso `custom-` e `label`).
- Servizi: `searchApiConfig`, `embeddingConfig`, `multimodalConfig`, `mineruConfig`, `proxyConfig`, `apiConfig`.
- Interfaccia e comportamento: `generalConfig` (`autostart`, `closeBehavior` con valori ask, minimize, exit), `language`, `theme`, `outputLanguage`, `projectOutputLanguages`, `zoomLevel`, `updateCheckState` (`enabled`, `lastCheckedAt`, `dismissedVersion`).
- Per progetto: `scheduledImportConfig:<percorso>`, `projectFileSyncEnabled` (con chiave `default`), `sourceWatchConfig` (con chiave `default`), `sourceWatchAllProjects`.

Campi di `mineruConfig` (normalizzati in `project-store.ts`): `enabled`, `backend`, `localEndpoint`, `localToken`, `localBackend`, `localEffort`, `localParseMethod`, `localLanguage`, `localFormulaEnabled`, `localTableEnabled`, `localImageAnalysis`, `localServerUrl`, `token`, `modelVersion`. [^src: raw/2026-11-20-repo-llm_wiki.md §Schemi e campi]

Campi di `sourceWatchConfig` (normalizzata in `source-watch-config.ts`): `enabled`, `autoIngest`, `persistExtractedMarkdown`, `parsingConcurrency`, `ingestConcurrency`, `includeExtensions`, `excludeExtensions`, `excludeDirs`, `excludeGlobs`, `maxFileSizeMb` (da 1 a 4096). [^src: raw/2026-11-20-repo-llm_wiki.md §Schemi e campi]

### Sincronizzazione con Rust e segreti
- I commenti di `project-store.ts` indicano che i nomi `proxyConfig` e `apiConfig` devono coincidere con quelli letti dal codice Rust; se divergono, l'API resta senza token configurato. [^src: raw/2026-11-20-repo-llm_wiki.md §Schemi e campi]
- Tra i campi in chiaro compaiono `token` e `localToken` in `mineruConfig`; per `apiConfig` i commenti parlano di un token API. Nessun valore è stato letto. I tipi di `llmConfig`, `embeddingConfig`, `searchApiConfig` e `providerConfigs` sono in `src/stores/wiki-store.ts`, non letto: la presenza di chiavi API non è verificata. [^src: raw/2026-11-20-repo-llm_wiki.md §Schemi e campi]

### Nota sulla cronologia
La cronologia è una mappa file-per-percorso con indirizzo stabile (hash FNV-1a a 64 bit con costanti fisse, per resistere ai cambi di toolchain). Il record di `scheduled-import-db.json` tiene un hash md5 per file e, in più, size e mtime per saltare il ricalcolo. [^src: raw/2026-11-20-repo-llm_wiki.md §Schemi e campi]

## Pagine collegate
[[llm-wiki-schema-dati]], [[llm-wiki-versioni-e-migrazioni]], [[llm-wiki-operazioni-distruttive]], [[llm-wiki-gestione-file-corrotti]], [[llm-wiki-rischi-persistenza]], [[llm-wiki-sicurezza]]. Gap aperti: [[gaps]] (`llm-wiki-persistenza-codice-non-letto`, `llm-wiki-app-state-percorso`, `llm-wiki-creazione-cartella-dati`, `llm-wiki-archivi-dimensioni`).

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

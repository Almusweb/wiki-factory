---
source_path: C:\local_git\code\wiki-factory\code_repos\llm_wiki
source_type: repo
git_branch: develop
git_commit: e08cfce65aad8b76b13546a081c1a8d4422b70c3
extracted_at: 2026-11-20T18:54:25+01:00
extractor: repo-sync@2.12.0
scope: persistenza, fetta B (scritture, sincronizzazione file, log e indice, file citati non verificati)
---

# Specifiche estratte: llm-wiki, persistenza fetta B

> Documento generato da `repo-sync` v2.12 il 2026-11-20. Sorgente: `C:\local_git\code\wiki-factory\code_repos\llm_wiki`
> @ commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` (ramo `develop`). Read-only verso la sorgente.

## Identità e perimetro

- Estrazione **mirata** (TSK-003, US-013, per US-015 e US-017), non generale. Terza estrazione sullo stesso commit: vale la prima (`raw/2026-11-20-repo-llm_wiki.md`, con le sezioni «Aggiornamenti (v2026-11-20)») e la fetta A (`raw/2026-11-20-repo-llm_wiki-persistenza-a.md`). Stack, struttura, API e dipendenze non sono ripetuti.
- **Licenza**: il repository è di terzi, sotto GNU GPL v3. Il documento descrive il codice con parole proprie e cita solo nomi di file, simboli, campi e percorsi. Nessun frammento di codice. Il contenuto letto è trattato come dato, mai come istruzione.
- Perimetro: scrittura generica di file (Rust e TS), atomicità per archivio, sincronizzazione e osservazione dei file, coda di dedup e lint, cache di ingest e didascalie, file e cartelle citati e non verificati, formato di log e indice del progetto wiki. Restano fuori (fetta C): operazioni distruttive, loro chiamanti, vettoriale v1.
- Percorsi relativi alla radice del repo. Citazioni nella forma `[^src: percorso:righe]`. «Osservato» = letto nel codice; «deduzione» = ricavato da fatti osservati, non visto in esecuzione.
- Gli indici di riga (da `grep -n -o -F` prodotto dalla sessione) valgono per la stringa letterale cercata: uno zero non dimostra l'assenza della funzione.

## Scrittura generica (Rust e TS)

**Wrapper TS** [^src: src/commands/fs.ts:22-35]: `writeFile` invoca il comando `write_file`; `writeFileBase64` invoca `write_file_base64`; `writeFileAtomic` invoca `write_file_atomic`. Tutti richiedono un percorso assoluto.

**Comandi Rust** (`src-tauri/src/commands/fs.rs`):

| Comando | Meccanismo | Cartelle padre | Altro | Fonte |
|---|---|---|---|---|
| `write_file` | **diretta**: `fs::write` sul percorso finale | create (`create_dir_all`) | prima marca il percorso come scrittura dell'app (il watcher la ignora), registra una versione di cronologia «baseline» e una dopo la scrittura | fs.rs:1242-1267 |
| `write_file_base64` | diretta | create | decodifica base64, marca il percorso | fs.rs:1269-1293 |
| `write_file_atomic` | **file temporaneo e rinomina**: file `.<nome>.<nanosecondi>.tmp` accanto al target, poi `fs::rename`; se la rinomina fallisce rimuove il temporaneo | create | registra la versione di cronologia | fs.rs:1295-1344 |
| `create_directory` | `create_dir_all` | crea anche i padri | richiede percorso assoluto | fs.rs:1937-1947 |

- Zero occorrenze della stringa `sync_all` in `fs.rs`: non risulta flush su disco. Deduzione: l'atomicità vale per i lettori concorrenti, non è dimostrata come durabile a un crash.
- La cronologia (`record_file_version`) è descritta nella prima estrazione: parte da `history-settings.json` con `enabled` falso per default, quindi di norma non salva versioni.
- **Cache di preprocessing** (`preprocess_file`): scrive con `fs::write` diretto (fs.rs:215-235), vedi `### File e cartelle citati`.
- Altri comandi di `fs.rs` con `create_dir_all` e `OpenOptions` (righe 1389-1540, 1659-1710): non letti.

## Atomicità per archivio

Fonte per i moduli TS: il `writeFile` generico, quindi **diretta**, salvo dove indicato. Inventario di 17 righe come nella prima estrazione (il conteggio dei gap `llm-wiki-archivi-sommario-conteggi` non è modificato qui).

| # | Archivio | Scrittura | Fonte |
|---|---|---|---|
| 1 | LanceDB v2 `wiki_chunks_v2` | gestita da lancedb (merge-insert per pagina) | prima estrazione, non riletta |
| 2 | LanceDB v1 `wiki_vectors` | gestita da lancedb; cancella e aggiunge in due passi | prima estrazione, non riletta |
| 3 | `embedding-revisions/<sha256>.revision` | **atomica** (tmp e rinomina) | prima estrazione, non riletta |
| 4 | `project.json` | diretta (`writeFile` in `ensureProjectId`, creazione padri da `write_file`) | fetta A; fs.rs:1242-1267 |
| 5 | `ingest-queue.json` | diretta; scritture serializzate in processo da una coda di richieste; errori ignorati | ingest-queue.ts:97-158 |
| 6 | `ingest-cache.json` | diretta; lettura-modifica-scrittura dell'intero file; errori ignorati | ingest-cache.ts:47-53 |
| 7 | `review.json` | diretta | persist.ts:14-18 |
| 8 | `lint.json` | diretta | persist.ts:30-34 |
| 9 | `lint-config.json` | **atomica** (`writeFileAtomic`) | prima estrazione, non riletta |
| 10 | Chat: `conversations.json` e `chats/<id>.json` | diretta, un file alla volta (l'indice per primo, poi un file per conversazione) | persist.ts:79-112 |
| 11 | `chat-preferences.json` | diretta | persist.ts:244-251 |
| 12 | `dedup-not-duplicates.json` | diretta | dedup-storage.ts:40-46 |
| 13 | `scheduled-import-db.json` | **atomica** | prima estrazione, non riletta |
| 14 | `history-settings.json` | **non verificata**: in `file_history.rs` ho letto solo le righe 1-70 (percorso e tipo); resta la dichiarazione in blocco «cronologia: diretta» della prima estrazione | file_history.rs:1-70 |
| 15 | Cronologia `history/<hash>.json` | diretta | prima estrazione, non riletta |
| 16 | Sessioni agente `agent-sessions/<id>.json` | diretta | prima estrazione, non riletta |
| 17 | `app-state.json` | plugin store di Tauri (salvataggio automatico con debounce e flush esplicito per alcune chiavi) | fetta A |

- `writeFileAtomic` lato TS: tra i chiamanti conosciuti compare solo `lint-config.ts` (prima estrazione). Non ho un indice globale del termine: l'elenco completo dei chiamanti non è verificato. Zero occorrenze in `ingest.ts`.
- **Divergenza commento e codice.** Nel modulo delle didascalie un commento descrive la scrittura della cache come atomica e dice «before we added atomic writes» [^src: src/lib/image-caption-pipeline.ts:25-38,131-133,364-367,584-587]. Il codice usa `writeFile` (diretta) [^src: src/lib/image-caption-pipeline.ts:142-152].

### D. Archivi trovati e non presenti nell'inventario

| Archivio | Posizione | Scrittura | Fonte |
|---|---|---|---|
| `file-snapshot.json` | `.llm-wiki/` | **atomica**; su Windows elimina prima l'originale (finestra non atomica) | file_sync.rs:20,1347-1381 |
| `file-change-queue.json` | `.llm-wiki/` | come sopra | file_sync.rs:21,1347-1381 |
| `dedup-queue.json` | `.llm-wiki/` | diretta | dedup-queue.ts:55-66 |
| `ingest-progress/<slug>-<hash>.json` | `.llm-wiki/` | diretta (con `createDirectory` prima) | ingest.ts:3043-3049,3150-3157 |
| `ingest-generation/<slug>-<impronta>.json` | `.llm-wiki/` | diretta (con `createDirectory` prima) | ingest.ts:3051-3057,3093-3099 |
| `ingest-warnings.log` | `.llm-wiki/` | diretta; append per lettura-modifica-scrittura | ingest.ts:663-705 |
| `page-history/<percorso con "_">-<timestamp>` | `.llm-wiki/` | diretta; copia di backup della pagina prima di un merge | ingest.ts:3489-3498 |

- I due checkpoint si cancellano a ingest riuscito [^src: src/lib/ingest.ts:1548-1552]. Campi: `version: 1` più identità e impronta della sorgente. `ingest-progress` ha anche `completedThrough` e `analyses` [^src: src/lib/ingest.ts:3110-3134]; `ingest-generation` ha `completedPaths` [^src: src/lib/ingest.ts:3067-3090]. La forma completa dei tipi non è stata letta.
- Il nome in `page-history/` sostituisce `/` e `\` del percorso relativo con `_` e aggiunge un timestamp ISO con `:` e `.` sostituiti da `-`.

## Creazione di `.llm-wiki/` e chiamante dell'auto-save

Chiude i punti 2 e 3 dei gap della fetta A.

- **Cartelle padre.** `write_file`, `write_file_base64`, `write_file_atomic` e `create_directory` creano le cartelle padre. Osservato [^src: src-tauri/src/commands/fs.rs:1248-1251,1280-1283,1301-1304,1942]. Deduzione: la scrittura di `.llm-wiki/project.json` in `ensureProjectId` (osservata dalla fetta A) crea da sola `.llm-wiki/` all'apertura o alla creazione del progetto.
- **`ensureDir`** [^src: src/lib/persist.ts:9-12]: crea `.llm-wiki` e `.llm-wiki/chats`, ignorando gli errori; è chiamata da `saveReviewItems`, `saveLintItems`, `saveChatHistory` e `saveChatPreferences`. Dato che la scrittura stessa crea i padri, per quelle quattro funzioni è ridondante (deduzione).
- **Chi invoca le scritture di `persist.ts`**: `auto-save.ts` [^src: src/lib/auto-save.ts:83-130].
  - Tre sottoscrizioni agli store, con debounce: review 1 s, lint 1 s, chat 2 s. La chat non salva durante lo streaming.
  - `flushAndSuspendAutoSave` (righe 30-53) scrive subito review, lint, preferenze e chat e sospende l'auto-save: serve al cambio progetto, prima che `resetProjectState` svuoti gli store. `runWithSuspendedAutoSave` lo racchiude (righe 64-81).
  - `setupAutoSave` non scrive all'avvio: la prima scrittura segue la prima modifica di uno store.
  - Errori di scrittura ignorati nelle sottoscrizioni.
- `saveChatPreferences` ha un secondo chiamante diretto in `src/components/settings/sections/skills-section.tsx` (indice globale, righe 8 e 57; file non letto). Il chiamante di `setupAutoSave` è `App.tsx` (fetta A).

## Sincronizzazione e osservazione dei file

Moduli: `src-tauri/src/commands/file_sync.rs` (Rust), `src/commands/file-sync.ts` (wrapper), `src/stores/file-sync-store.ts`, `src/lib/project-file-sync.ts`.

**Stato persistito: sì, due file per progetto, sempre in `.llm-wiki/`** [^src: src-tauri/src/commands/file_sync.rs:20-21]. Nessun uso di `app_data_dir` (zero occorrenze).

- `file-snapshot.json`: `version`, `updatedAt` (ms), `files` come mappa da percorso relativo a `{hash?, size, mtimeMs}` [^src: file_sync.rs:53-67].
- `file-change-queue.json`: `version`, `tasks[]`. Un task ha `id`, `projectId`, `path`, `kind` (created, modified, deleted), `status` (pending, processing, done, failed, superseded), `hashBefore?`, `hashAfter?`, `size?`, `mtimeMs?`, `createdAt`, `updatedAt`, `retryCount`, `error?`, `needsRerun` [^src: file_sync.rs:69-111]. Tentativi massimi: 3 (riga 25).
- Scrittura: una sola funzione, `write_json` (tmp e rinomina, vedi D) [^src: file_sync.rs:1347-1381]. Prima di `mod tests` (riga 1480) l'indice dà un solo `fs::write` e un solo `rename(`; zero `File::create`, `OpenOptions`, `write_all`. Il valore è limitato alle stringhe cercate.
- Lettura: `read_json` restituisce il valore di default se il file manca; su JSON illeggibile restituisce **un errore** (`Failed to parse`), a differenza della maggior parte dei caricamenti TS che tornano al valore vuoto in silenzio [^src: file_sync.rs:1335-1345]. `read_snapshot` e `read_queue` portano `version` 0 a 1 (righe 1309-1329).
- `invalidate_project_file_snapshot_paths` toglie voci dallo snapshot (usato dal frontend quando l'ingest in background non si può accodare) [^src: file_sync.rs:365-388] [^src: src/lib/project-file-sync.ts:371-379].
- `ignore_file_change_task` rimuove un task dalla coda; `retry_file_change_task` lo riporta a pending e azzera i tentativi [^src: file_sync.rs:398-445].
- All'avvio del watcher il Rust chiama `reset_processing_tasks`, poi un rescan iniziale e `process_queue` (righe 207-210); i corpi di queste funzioni non sono stati letti.

**Stato in memoria, non persistito**: il watcher e gli id del progetto (`FileSyncState`, righe 41-51), un blocco per coda (`QUEUE_LOCKS`), la finestra di ignoro delle scritture dell'app (`APP_WRITE_IGNORES`, 4 s) e il contatore di generazione del watcher. Lo store TS `file-sync-store.ts` ha solo `tasks`, `running`, `lastError`, senza persistenza.

**Comportamento del watcher** (osservato): osserva la radice del progetto in modo ricorsivo, più `raw/sources` e `wiki`; accumula i percorsi con una finestra di 700 ms; un rescan periodico (10 s su Linux, 60 s altrove) riallinea lo snapshot dopo eventi persi o overflow [^src: file_sync.rs:28-33,212-308].

**Lato TS** (`project-file-sync.ts`, osservato): ascolta gli eventi `file-sync://queue-updated` e `file-sync://changed`; per le modifiche a `raw/sources` accoda l'ingest (a progetto attivo o inattivo), cancella a cascata i file spariti e migra i percorsi se un file è stato solo spostato (stesso hash, coppia unica creato e cancellato). Non scrive file direttamente. Con la modalità «tutti i progetti» scansiona ogni 60 s i progetti recenti inattivi [^src: src/lib/project-file-sync.ts:45,123-181,243-267]. Sono esclusi dalla cascata i percorsi con `/.cache/`, i file che iniziano con un punto e, per le pagine wiki, `index.md`, `log.md`, `overview.md` e `wiki/media/` (righe 426-443).

## Coda di dedup e lint

- **`dedup-queue.json`**: array di `DedupTask`, con `id`, `projectId`, `group` (tipo `DuplicateGroup` in `dedup.ts`, non letto), `canonicalSlug`, `status` (pending, processing, done, failed), `addedAt`, `error`, `retryCount` [^src: src/lib/dedup-queue.ts:29-38]. I task `done` non sono salvati (righe 59-66). Scrittura diretta, errori ignorati. In lettura un file illeggibile dà una coda vuota (righe 68-82). Alla riapertura i task `processing` tornano `pending` e i `pending` restano in pausa finché non si riprende a mano; i task di altri progetti si scartano (righe 273-318). Ritentativi: 3 (riga 322).
- **`lint.json`**: array di `LintItem`, con `id` (forma `lint-N`), `type`, `severity`, `page`, `detail`, `affectedPages?`, `brokenTarget?`, `suggestedTarget?`, `suggestedSource?`, `createdAt` [^src: src/stores/lint-store.ts:4-15]. Scritto da `saveLintItems` (diretta, vedi sopra). I valori ammessi di `type` e `severity` sono in `lint.ts` (`LintResult`), non letto.

## Cache di ingest, didascalie e checkpoint

- **`ingest-cache.json`**. `saveIngestCache` si chiama dopo la scrittura dei file, solo se sono stati scritti file e non ci sono fallimenti duri né blocchi troncati non recuperati [^src: src/lib/ingest.ts:1540-1557]. La lettura considera valida una voce solo se tutti i file in `filesWritten` esistono ancora [^src: src/lib/ingest-cache.ts:67-99]. Campi (come nella prima estrazione): `entries` per nome sorgente, con `hash`, `timestamp`, `filesWritten[]`.
- **`image-caption-cache.json`**: mappa chiave → voce con `caption`, `mimeType`, `model`, `capturedAt`, `imageHash?`, `outputLanguage?`. Chiave: l'hash SHA-256 dei byte (legacy) oppure l'hash seguito da `::language:` e la lingua codificata. Si scrive una sola volta a fine batch, solo se ci sono didascalie nuove. File mancante o corrotto: mappa vuota, con avviso in console [^src: src/lib/image-caption-pipeline.ts:46-55,116-152,584-597]. Il pipeline gira sotto un blocco di progetto dedicato [^src: src/lib/ingest.ts:856,1004]. Le didascalie si leggono anche in `injectImagesIntoSourceSummary` (`ingest.ts:3533`).
- **`vision-caption.ts`** (righe 1-60): invia un'immagine al modello visivo e restituisce il testo; il commento dice esplicitamente che non sa nulla di cache.
- **Checkpoint di ingest**: vedi tabella D.
- **Altre scritture di `ingest.ts`**: pagine wiki (`writeFile` per blocco; il log si accoda, indice e overview si sovrascrivono), pagine di riepilogo di sorgente con riferimenti alle immagini (righe 3514-3584), migrazione di riepiloghi legacy con cancellazione del vecchio file (righe 1900-1974). Non ho letto le altre scritture.

## File e cartelle citati e non verificati

| Nome | Esito | Evidenza |
|---|---|---|
| `image-caption-cache.json` | **Esiste come archivio** (campi sopra) | image-caption-pipeline.ts:26,57,142-152; ingest.ts:948 |
| `lexical-graph.json` | **Non esiste nel codice letto**: compare solo in un commento di `dedup-storage.ts` con la dicitura «when added»; zero occorrenze in `ingest.ts`; unica occorrenza nell'indice globale su `src` e `src-tauri/src` | dedup-storage.ts:10-11 |
| `raw/sources/.cache` | **Esiste come cartella `.cache` accanto a ogni sorgente**, non solo alla radice di `raw/sources`: `<cartella del file>/.cache/<nome>.txt` | fs.rs:163-168; ingest.ts:745-756 |
| `.llm-wiki-imported` | **Esiste come costante** (`LEGACY_DB_DIR`) in `scheduled-import.ts`: l'unica occorrenza della stringa; non ho letto gli usi della costante | scheduled-import.ts:80 |

- **Cartella `.cache`**. Rust (`preprocess_file`) scrive il testo estratto di PDF, org, Office ed e-book in `.cache/<nome>.txt`; per i formati Office aggiunge un marcatore `.txt.parser` con la versione del parser. La validità si decide per data di modifica: la cache è usata solo se non è più vecchia dell'originale; senza marcatore valido, o con versione diversa, la cache Office non si usa [^src: src-tauri/src/commands/fs.rs:132-235]. Prima di rimpiazzare il contenuto, la scrittura rimuove il marcatore (commento: un crash può causare una ricostruzione in più, mai l'uso di testo stantio). Per i PDF, se MinerU è attivo, `ingest.ts` scrive in `.cache/<nome>.txt` il markdown restituito [^src: src/lib/ingest.ts:743-757].
- Le occorrenze di `.cache` dell'indice includono falsi positivi (la sottostringa compare in `...cache`, per esempio `ingest-cache.ts:112,129,148`). Altre occorrenze (`scheduled-import.ts:253`, `source-filter.ts:4`, `source-lifecycle.ts:237,495,500`, `agent/tools.rs:3526-3559`, `fs.rs:2514,2770,2948,2949,2966`, `project.rs:204`) non sono state lette.
- `.llm-wiki-imported`: se la cartella legacy venga mai creata o letta non è verificato; il commento della prima estrazione la cita come riferimento legacy.

## Log e indice del progetto wiki

### Formato di `wiki/log.md`

Non c'è un formato unico: dipende dallo scrittore.

| Scrittore | Momento | Formato osservato | Fonte |
|---|---|---|---|
| Voce chiesta al modello nell'ingest | ogni ingest, nel blocco `FILE` di `wiki/log.md` | `## [YYYY-MM-DD] ingest \| Titolo`. Il codice sostituisce la prima data della voce con quella odierna e **accoda** la voce dopo una riga vuota | ingest.ts:2541; 2060-2069,2158-2159,2238-2241 |
| Voce deterministica | solo se il modello non ha emesso `wiki/log.md` | `## [<data>] ingest \| <identità sorgente>`; se il log è vuoto o assente parte da un'intestazione `# Wiki Log` | ingest.ts:676-685,1402-1418 |
| `create_project` | creazione progetto | intestazione `# Research Log`, poi `## <data>` e `- Project created` | project.rs:171-180 |
| «Save to wiki» da review (azione `save:`) | azione utente | `- <data>: Saved query page` più il nome file, accodata; se il log manca parte da `# Wiki Log` | review-view.tsx:118-152 |
| Creazione di pagine da una review | azione utente | `- <data>: Created N page(s) from review:` più i nomi file, accodata | review-view.tsx:286-292 |
| Funzione di ingest da conversazione (quella con il prompt «Based on our discussion…»; il nome della funzione non è nella finestra letta) | dopo la generazione dei file da una chat | accoda il contenuto del blocco `wiki/log.md` dopo una riga vuota | ingest.ts:3759-3787,3866-3873 |

- **Divergenza osservata.** Il testo del template per `schema.md` dichiara un log in ordine cronologico inverso, con voci `## YYYY-MM-DD` e un elenco puntato [^src: src/lib/templates.ts:51-56] [^src: src-tauri/src/commands/project.rs:94-101]. Tutti i punti di scrittura letti **accodano in fondo**; ciascuno usa un formato di voce diverso.
- Le date e il corpo della voce dell'ingest dipendono dal prompt al modello: il codice non valida il formato, sostituisce solo la prima data (`stampGeneratedLogDate`).
- Nel flusso ingest il log è escluso dal controllo di lingua e dal merge con LLM (righe 2209-2216, 2238-2241).

### Logica di aggiornamento di `wiki/index.md` oltre `rebuild_wiki_index`

- **Ingest (deterministico)** [^src: src/lib/ingest.ts:1387-1391,1700-1732,1807-1821]. Per ogni pagina `wiki/*.md` scritta (esclusi index, overview e log) e non ancora linkata nell'indice, aggiunge `- [[percorso senza wiki/ e senza .md]] — titolo` nella sezione `## Recently Updated`, con massimo 200 voci. Se l'indice non si legge, parte da `# Wiki Index`. Il titolo viene dal frontmatter o dal nome file.
- Il modello non può generare l'indice: i prompt lo vietano («the application maintains aggregate navigation separately», `ingest.ts:2544,3784`) e il codice scarta i blocchi del modello su index e overview [^src: src/lib/ingest.ts:2142-2147]. `isAppManagedAggregatePath` identifica `wiki/index.md` e `wiki/overview.md` (righe 1646-1649).
- **`overview.md`**: aggiornamento deterministico analogo con marcatori `llm-wiki:recent-start/end` e massimo 50 voci [^src: src/lib/ingest.ts:1734-1798].
- **Azioni di review** [^src: src/components/review/review-view.tsx:135-146,270-284]: inseriscono `- [[cartella/slug|titolo]]` subito sotto l'intestazione di sezione corrispondente, oppure accodano la sezione se manca.
- **`create_project`**: indice iniziale con sezioni Entities, Concepts, Sources, Queries, Comparisons, Synthesis, senza voci [^src: src-tauri/src/commands/project.rs:154-169].
- **Merge di duplicati**: `dedup-runner.ts` riscrive `index.md` per togliere le voci delle pagine unite, tramite `rewriteIndexMd` (non letto) [^src: src/lib/dedup-runner.ts:472-479].
- **Scrittori segnalati dall'indice e rimandati alla fetta C** (non letti): `src/lib/wiki-page-delete.ts` (righe 177, 188, 244, 256 per `index.md`), `src/lib/source-lifecycle.ts` (righe 642 per `index.md`, 698 per `log.md`).
- **Occorrenze di `index.md` o `log.md` non classificate** (lettore, filtro o scrittore: ruolo non verificato): `chat-message.tsx:579-603`, `activity-panel.tsx:80-81`, `knowledge-tree.tsx:72-73`, `lint-view.tsx:338-341`, `graph-filters.ts:37-39`, `deep-research.ts:579`, `enrich-wikilinks.ts:35`, `api_server.rs:2982-3750`, `agent/runtime.rs:5641-5667`, `claude_cli.rs` e `codex_cli.rs` (cluster di righe nei dintorni di 358-566 e 496-706), `page_embedding.rs:122`, `ingest-queue.ts:194-204` (letta la funzione `isStructuralWikiPath`, che riconosce i tre percorsi; il suo uso non è stato letto). Nel campione letto, `lint.ts:170-172,230` e `wiki-cleanup.ts:9` sono filtri o commento, non scrittori.
- Voci di `rebuild_wiki_index` e la sua finestra non atomica su Windows: già nella prima estrazione.

## Copertura del gap `llm-wiki-persistenza-codice-non-letto`

- **Coperti da questa fetta**: stato persistito di `file_sync.rs` (due file, formato sopra); scrittura generica di `fs.rs` (`write_file`, `write_file_base64`, `write_file_atomic`, `create_directory`) e wrapper TS; `dedup-queue.ts`; `lint-store.ts`; scrittura di `ingest-cache` e della cache delle didascalie in `ingest.ts`; checkpoint di ingest; scrittori di log e indice nell'ingest e nelle azioni di review.
- **Restano scoperti**: cancellazioni di `fs.rs` e comandi di copia o spostamento; `search.rs` oltre le parti della fetta A; `api_server.rs` (endpoint che scrivono); `agent/runtime.rs` (chiamanti di `append_turn`); `proxy.rs` oltre le righe 1-260; `lib.rs` oltre le parti già lette; `wiki-page-delete.ts`, `source-lifecycle.ts`, `chat-panel.tsx` (cancellazione file chat), `sweep-reviews.ts` per la parte di scrittura (fetta C); `history-settings.json` (meccanismo di scrittura).

## Gap evidenti

1. Meccanismo di scrittura di `history-settings.json`.
2. `write_file_inner` (usata da `create_project`) non letta: non so se crea le cartelle padre.
3. `fs.rs`: righe 1389-1540 (tra cui un uso di `OpenOptions`), 1659-1710 (comandi con `create_dir_all`) e le altre scritture del file; righe dal 2085 sono test, non letti.
4. `file_sync.rs` righe 445-1289 (scansione, `process_queue`, `enqueue_*`, `reset_processing_tasks`): non so se lo snapshot esclude `.llm-wiki` o `.cache`, né come si decide `needsRerun`; righe 1410-1479 e 1480 in poi (test) non lette.
5. `ingest-queue.ts` oltre la riga 219, comprese le scritture per progetti non attivi (`inactiveQueueWrite`).
6. Elenco completo dei chiamanti di `writeFileAtomic` (nessun indice globale).
7. Uso della costante `LEGACY_DB_DIR` (`.llm-wiki-imported`).
8. Tipo `DuplicateGroup` (`dedup.ts`) e valori di `LintResult` (`lint.ts`).
9. Occorrenze non classificate di `index.md` e `log.md` (sezione Log e indice).
10. Il formato di voce di log dipende dal prompt: non è determinabile quanto i modelli reali lo rispettino.
11. Dimensioni reali e crescita degli archivi: non ricavabili dal codice (gap `llm-wiki-archivi-dimensioni`).
12. Il conteggio degli archivi (gap `llm-wiki-archivi-sommario-conteggi`) non è corretto né confermato qui: questa fetta aggiunge i sette archivi di tabella D, non presenti nell'inventario di 17 righe.

## Note di estrazione

- **Stato**: **partial**. Commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3`, ramo `develop`, stesso commit della fetta A (verifica `git -C code_repos/llm_wiki log -1 --format=%h` → `e08cfce` e `status --short` vuoto fatta dalla sessione prima dell'avvio).
- **File aperti: 26** (11 interi, 15 a finestre). Nove erano già citati come letti dalle estrazioni precedenti (`persist.ts`, `fs.ts`, `project.rs`, `ingest-cache.ts`, `dedup-storage.ts`, `ingest-queue.ts`, `scheduled-import.ts`, `file_history.rs`, inizio di `ingest.ts`); 17 non risultano citati. **`files_sampled` cumulativo: 80, dichiarato come massimo** (63 più 17): l'elenco esatto dei 30 file della prima estrazione non è verificabile, quindi il valore reale può essere più basso. `files_total_in_repo`: 476.
- **Byte letti: circa 200 KB**, contro una stima di 100-120 KB al gate di Fase 1 con l'indice. Motivi: lettura integrale di `project-file-sync.ts` (16 KB) e `image-caption-pipeline.ts` (23 KB); molte funzioni di `ingest.ts` non sono esportate e non erano nell'indice (`updateWikiIndexDeterministically`, `saveGenerationCheckpoint`, `backupExistingPage` e altre), quindi le ho cercate a finestre; verifica dei candidati di US-017 per circa 12 KB, entro il tetto di 25 KB.
- **Aperti fuori dall'elenco nominato al gate di Fase 1**, con il motivo:
  - `src/components/review/review-view.tsx` (96-155, 236-293): l'indice lo segnalava come scrittore di log e indice;
  - `src/lib/lint.ts` (160-179, 222-237): occorrenze di `index.md` e `log.md` dall'indice, per verificare se fosse uno scrittore (è un filtro);
  - `src/lib/scheduled-import.ts` (70-89): unica occorrenza di `.llm-wiki-imported`;
  - `src/lib/persist.ts` (intero) e `src/commands/fs.ts` (14-43): meccanismo di scrittura degli archivi della fetta A e wrapper `writeFileAtomic`;
  - `src/lib/dedup-runner.ts` (466-479): occorrenza di `index.md` nell'indice, per capire la logica di aggiornamento dell'indice nel merge (era un file «condizionale» del piano).
- **Elenco dei 26 file aperti, con intervalli** (percorsi relativi al repo):
  - interi: `src/lib/auto-save.ts`, `src/commands/file-sync.ts`, `src/stores/file-sync-store.ts`, `src/lib/dedup-storage.ts`, `src/stores/lint-store.ts`, `src/lib/ingest-cache.ts`, `src/lib/ingest-commit-coordinator.ts`, `src/lib/dedup-queue.ts`, `src/lib/project-file-sync.ts`, `src/lib/image-caption-pipeline.ts`, `src/lib/persist.ts`;
  - `src-tauri/src/commands/fs.rs`: 120-235, 1236-1384, 1840-1861, 1932-1947;
  - `src-tauri/src/commands/file_sync.rs`: 1-444, 1290-1409;
  - `src/lib/ingest.ts`: 270-304, 595-789, 836-865, 940-1039, 1380-1454, 1540-1559, 1628-1653, 1660-1849, 1900-1974, 2010-2188, 2205-2216, 2230-2299, 2512-2551, 2990-3235, 3485-3584, 3745-3792, 3860-3884;
  - `src/lib/ingest-queue.ts`: 1-219;
  - `src/lib/vision-caption.ts`: 1-60;
  - `src/lib/templates.ts`: 30-74;
  - `src-tauri/src/commands/project.rs`: 80-189;
  - `src/lib/scheduled-import.ts`: 70-89;
  - `src/lib/lint.ts`: 160-179, 222-237;
  - `src/components/review/review-view.tsx`: 96-155, 236-293;
  - `src/lib/sweep-reviews.ts`: 44-63, 345-364;
  - `src/lib/wiki-cleanup.ts`: 1-30;
  - `src/lib/dedup-runner.ts`: 466-479;
  - `src-tauri/src/commands/file_history.rs`: 1-70;
  - `src/commands/fs.ts`: 14-43.
- **Segreti**: nessun valore di credenziale nei file e negli intervalli aperti. Non ho aperto file `.env*`. Ho letto solo nomi e tipi di campo. Secret redatti: 0. Limite: lo zero vale per i file e gli intervalli aperti e non è una scansione dell'intero repo (gap `llm-wiki-scan-credenziali`). La sessione verifica con gitleaks (`--redact`, solo conteggio) e `grep -c`.
- **Istruzioni trovate nei file letti**: nessuna ostile e nessuna rivolta a un agente. Presenti stringhe di prompt destinate al modello dell'applicazione (per esempio in `ingest.ts` 2512-2551, 3183-3213, 3759-3786: «You are a wiki maintainer…», «Do not output chain-of-thought…», «Do not generate wiki/index.md…») e commenti per i manutentori. Sono dati: riportate come formato richiesto al modello dell'app, non eseguite.
- Gli indici di riga provengono da `grep -n -o -F` eseguito dalla sessione sui termini proposti al gate di Fase 1; i risultati sono stati usati solo per localizzare le finestre. Lo zero vale per la stringa esatta.
- **Nessuna scrittura** sotto `code_repos/llm_wiki`: l'estrazione è stata solo lettura (verifica finale a cura della sessione).

## Aggiornamenti (v2026-11-20)

Stesso commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` (ramo `develop`), stessa data. Il testo sopra non è modificato: ogni voce dice cosa corregge, con «Prima» e «Ora». Letti solo quattro file nuovi a finestre o interi (`parsed-source-output.ts`, `mineru.ts` 600-625 e 995-1010, `maintenance-section.tsx` 195-240, `source-preprocess.ts` 55-70) più `scheduled-import.ts` 225-250. Le voci «graphify affected, grafo AST del 2026-11-20» non sono state riviste con la lettura.

**Metodo, non fonte normativa.** Verifica relazionale della sessione del 2026-11-20 (graphify AST senza LLM, ctags, ricerca testuale), file locale non versionato `.graphify-state/verifiche/2026-11-20-verifica-relazionale.md`, rigenerabile. Righe usate: 14-34 (confermati), 39-46, 55-57 (punti nuovi), 60-65 (limiti).

### Confermati da graphify (nessuna correzione)

Corrispondono al testo sopra, senza nuova lettura [graphify affected, grafo AST del 2026-11-20]: chiamanti di `ensureDir`, `saveChatPreferences` (`auto-save.ts:41,117`, `skills-section.tsx:57`), `setupAutoSave` (`App.tsx:142`), `flushAndSuspendAutoSave` (`App.tsx:639`); in `autoIngestImpl` `saveIngestCache` (`ingest.ts:1548`), `updateWikiIndexDeterministically` (`:1388`), `buildDeterministicIngestLog` (`:1410`), `saveGenerationCheckpoint` (`:1491`); `backupExistingPage` da `writeFileBlocks` (`:2282`); `rewriteIndexMd` da `executeMerge` (`dedup-runner.ts:479`); `write_json` e `read_json` usate solo da `write_queue`, `write_snapshot`, `read_queue`, `read_snapshot` (`file_sync.rs:1310-1332`); `reset_processing_tasks` e `process_queue` come descritto (`file_sync.rs:208-577`); `write_file_inner` chiamata solo da `create_project_impl` (`project.rs:119`).

### Punto 2: `writeFileAtomic` e il markdown estratto

- **Prima** (Atomicità per archivio): «tra i chiamanti conosciuti compare solo `lint-config.ts`»; zero occorrenze in `ingest.ts`; il markdown estratto risultava scritto solo in `.cache/<nome>.txt`; gap 6 «nessun indice globale».
- **Ora** (letto): `persistParsedMarkdown` crea la cartella e scrive con `writeFileAtomic`; `moveParsedMarkdown` scrive in modo atomico la nuova copia e poi cancella la vecchia, tollerando l'errore di cancellazione (un duplicato è preferito a una migrazione fallita) [^src: src/lib/parsed-source-output.ts:57-68,85-107]. Percorso: `<progetto>/raw/parsed/<percorso relativo a raw/sources>.md`, con l'estensione originale mantenuta; solo per 22 estensioni (pdf, Office, odf, rtf, epub, mobi, org) e solo per sorgenti sotto `raw/sources` [^src: src/lib/parsed-source-output.ts:4-55]. Non è la cartella `.cache`.
- Il file letto dice che esiste un'opzione per disattivare la copia (commento a `:80`); il legame con `persistExtractedMarkdown` dell'estrazione A è una deduzione.
- Chiamanti, da graphify: `persistParsedMarkdown` da `autoIngestImpl` (`ingest.ts:788`); `moveParsedMarkdown` da `migrateSourcePath` (`source-lifecycle.ts:211`); `saveImportDb` (`scheduled-import.ts:421`, da `scanAndImport` `:618`).
- **Tabella D, riga nuova**: `raw/parsed/<percorso>.md`, atomica (file temporaneo e rinomina, come `write_file_atomic` sopra). La riga 13 (`scheduled-import-db.json`, atomica) è coerente con graphify. «Zero occorrenze in `ingest.ts`» resta vero alla lettera ma la scrittura atomica avviene tramite `persistParsedMarkdown`. Il gap 6 passa a «elenco da graphify a profondità 1», non da ricerca testuale.

### Punto 3: immagini MinerU

- **Prima**: `writeFileBase64` era solo un wrapper, senza destinazione.
- **Ora** (letto): `mineru.ts` scrive ogni immagine del pacchetto con `writeFileBase64` in `<progetto>/wiki/<relPath>`, dopo `createDirectory`; `relPath` viene da `mineruAssetRelPath` (non letta) [^src: src/lib/mineru.ts:607-613]. Nell'altro punto scrive `image-N.<estensione>` e il percorso relativo è `media/<slug>/mineru/images/…` [^src: src/lib/mineru.ts:1000-1003]. La cartella assoluta (`mediaDir`) non è nella finestra: che sia sotto `wiki/media/` è una deduzione dal prefisso.
- **Tabella D, riga nuova**: immagini MinerU sotto `wiki/`, scrittura **diretta**. Il conteggio degli archivi (gap `llm-wiki-archivi-sommario-conteggi`) non è corretto qui: D passa da sette a nove righe.
- Graphify: chiamanti `saveMineruZipImages` (`mineru.ts:613`) e `parseWithLocalMineru` (`:1003`).

### Punto 6: `rebuild_wiki_index`

Letto: è un'azione manuale delle impostazioni di manutenzione; dopo la chiamata aggiorna l'albero file e mostra pagine e gruppi [^src: src/components/settings/sections/maintenance-section.tsx:197-205]. `export_project_archive` è nella stessa sezione a `:213`. Che sia l'unico punto di invocazione viene dalla ricerca testuale della sessione, non dalla lettura.

### Punto 7: `.llm-wiki-imported`

- **Prima** (File e cartelle citati): costante `LEGACY_DB_DIR`, usi non letti; gap 7.
- **Ora** (letto): serve a escludere i percorsi interni (`LEGACY_DB_DIR` e `.llm-wiki`) dalla scansione dell'import pianificato [^src: src/lib/scheduled-import.ts:233-245]. **Non esiste come archivio con campi** nel codice letto: nessuna scrittura né lettura di contenuto. Che l'unico uso sia `:235` viene dalla sessione (le costanti non sono nodi); l'origine legacy è dedotta dal nome. Gap 7 chiuso.

### Punto 8: chiamante di `preprocessFile`

Letto: `preprocessFile` è chiamata su percorsi unici, con limite di concorrenza; un errore è solo un warn e l'ingest riprova alla lettura [^src: src/lib/source-preprocess.ts:55-70]. Che sia l'unico chiamante non è provato (graphify non lo collegava, la ricerca testuale sì). Completa la riga «Cache di preprocessing» sopra: le scritture di `.cache` partono in parallelo e non sono fatali.

### Limiti

Graphify non vede gli archi IPC tra TS e Rust; le costanti non sono nodi; uno zero di graphify non prova l'assenza di chiamanti.

Segreti: nessun valore nelle finestre. Istruzioni nel contenuto: solo commenti per i manutentori, non eseguiti.

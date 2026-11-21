# Specifiche estratte: llm_wiki (fetta C1: FS, lib.rs, progetto)

> Documento generato da `repo-sync` v2.12 il 2026-11-21. Sorgente: /home/user/wiki-factory/code_repos/llm_wiki
> @ commit e08cfce65aad8b76b13546a081c1a8d4422b70c3 (v0.6.13, HEAD staccato). Read-only verso la sorgente.
> Percorsi citati relativi a `code_repos/llm_wiki/`. Le conseguenze marcate **[DEDUZIONE NON TESTATA]** sono inferenze dal codice, mai eseguite.

## Copertura

Letti per intero: `src/lib/persist.ts`, `src/lib/project-identity.ts`, `src/lib/project-store.ts`, `src/commands/fs.ts`, `src/lib/embedding.ts`, `src-tauri/src/commands/project.rs`, `src-tauri/src/commands/project_maintenance.rs`, `src-tauri/src/panic_guard.rs`.
Letti in parte: `src-tauri/src/lib.rs` righe 1-780; `src-tauri/src/commands/fs.rs` righe 1-650 e 1000-2229 (saltate 651-999 estrazione docx/pptx/org e 2230-3300 test); `src-tauri/src/commands/file_history.rs` righe 70-469 (saltate 1-69: costanti e `history_settings_path`); `src-tauri/tauri.conf.json` righe 1-40.
Un chiamante non trovato nelle finestre lette e' "non verificato", non "assente". Nessun segreto rilevato.

## Archivio dello stato app (gap 15)

- File: `<app_data_dir>/app-state.json`. Rust lo legge come `app.path().app_data_dir().join("app-state.json")` [^src: src-tauri/src/lib.rs:405-409] e nell'hook di setup per il proxy [^src: src-tauri/src/lib.rs:581-583].
- Lato TS lo gestisce `tauri-plugin-store` con nome `app-state.json`, `autoSave: true` [^src: src/lib/persist.ts:8-14] [^src: src/lib/project-identity.ts:20,72-74]. Plugin registrato a [^src: src-tauri/src/lib.rs:558].
- Identifier app `com.llmwiki.app` [^src: src-tauri/tauri.conf.json:5]. Il path OS risolto da `app_data_dir` dipende da Tauri: non verificato.
- Chiavi viste: `recentProjects` (max 10), `lastProject`, `projectRegistry`, `llmConfig`, `providerConfigs`, `activePresetId`, `taskModelRouting`, `projectLlmOverrides`, `customLlmPresets`, `searchApiConfig`, `embeddingConfig`, `multimodalConfig`, `mineruConfig`, `proxyConfig`, `apiConfig`, `generalConfig`, `scheduledImportConfig:<path>`, `language`, `theme`, `outputLanguage`, `projectOutputLanguages`, `sourceWatchConfig`, `updateCheckState`, `zoomLevel` [^src: src/lib/persist.ts:9-10,44-48,158,170,182,194,262,287,305,335,383,395,407-411,494,516].
- Chiavi condivise con Rust: `proxyConfig` (letta all'avvio, `proxy.rs`) e `apiConfig` (letta dall'`api_server` a ogni richiesta con cache di 5 s). Il codice avverte di tenere i nomi allineati [^src: src/lib/persist.ts:258-261,283-286].
- Flush: solo `saveProxyConfig`, `saveApiConfig` e alcuni setter fanno `store.save()` esplicito; gli altri si affidano al debounce di 100 ms [^src: src/lib/persist.ts:271-276,292-298].
- Rust legge dallo stesso file anche `projectRegistry`, `recentProjects`, `embeddingConfig`, `llmConfig`, `searchApiConfig` per l'agente [^src: src-tauri/src/lib.rs:346-434].
- **[DEDUZIONE NON TESTATA]** I token (`apiConfig`, chiavi provider) sono salvati come campi JSON dello store senza passaggi di cifratura visibili nelle finestre lette: probabile memorizzazione in chiaro. Non verificato che manchi una cifratura altrove.

## Layout del progetto su disco e creazione di `.llm-wiki/` (gap 16)

- `create_project(name, path)` fallisce se la cartella esiste; crea `raw/sources`, `raw/assets`, `wiki/{entities,concepts,sources,queries,comparisons,synthesis}`, `schema.md`, `purpose.md`, `wiki/index.md`, `wiki/log.md`, `wiki/overview.md`, `.obsidian/{app,appearance,core-plugins}.json` [^src: src-tauri/src/commands/project.rs:16-242]. **Non crea `.llm-wiki/`.** La config Obsidian esclude `.llm-wiki` dall'indicizzazione [^src: src-tauri/src/commands/project.rs:201-211].
- `open_project(path)` valida solo che esistano `schema.md` e la cartella `wiki/` e restituisce `{name, path}`; non scrive nulla [^src: src-tauri/src/commands/project.rs:245-264,342-361].
- `.llm-wiki/` nasce lato frontend:
  1. `createProject`/`openProject` chiamano `ensureProjectId`, che scrive `.llm-wiki/project.json` (`{id, createdAt}`) se manca; `write_file` fa `create_dir_all` sul parent [^src: src/commands/fs.ts:248-263] [^src: src/lib/project-identity.ts:47-68] [^src: src-tauri/src/commands/fs.rs:1248-1251].
  2. `ensureDir` in `persist.ts` crea `.llm-wiki` e `.llm-wiki/chats` prima di salvare review, lint, chat, preferenze [^src: src/lib/persist.ts:9-12].
- Un progetto importato o aperto da disco ottiene quindi `.llm-wiki/` all'apertura. Se la scrittura di `project.json` fallisce c'e' solo un `console.warn` e l'id e' effimero [^src: src/lib/project-identity.ts:62-67].
- `.llm-wiki/history/` e' creata da Rust solo se `.llm-wiki` esiste gia': senza, `record_file_version` non fa nulla [^src: src-tauri/src/commands/file_history.rs:98-110,134-157,234-237].

## Identita' del progetto, registro e import (gap 26)

- Identita' per progetto: `.llm-wiki/project.json`. Registro globale: chiave `projectRegistry` in `app-state.json`, `{ [id]: {id, path, name, lastOpened} }` [^src: src/lib/project-identity.ts:9-14,28-35].
- `upsertProjectInfo` fa `registry[id] = {...}` senza controllare che l'id esista gia' con un altro path [^src: src/lib/project-identity.ts:95-108].
- `export_project_archive`: zip di tutto il progetto (inclusi nascosti e `.llm-wiki`), esclusi symlink; la destinazione deve stare fuori dal progetto [^src: src-tauri/src/commands/project_maintenance.rs:134-190]. Test di round trip che preserva `.llm-wiki/ingest-cache.json` [^src: src-tauri/src/commands/project_maintenance.rs:53-78].
- `import_project_archive`: richiede path assoluti, max 100.000 entry e 4 GB espansi, nessun symlink, path relativi sicuri, presenza di `wiki/index.md`, destinazione vuota o inesistente [^src: src-tauri/src/commands/project_maintenance.rs:9-17,204-267]. Non rigenera ne' controlla l'id.
- **[DEDUZIONE NON TESTATA]** Importare un archivio di un progetto gia' presente nella stessa installazione porta `project.json` con lo stesso id; `openProject` lo rilegge (`ensureProjectId`) e `upsertProjectInfo` sovrascrive la entry del registro col path aperto per ultimo. Override LLM per progetto (`projectLlmOverrides`) e riferimenti per id si mescolerebbero tra le due copie.
- Non verificato: il chiamante UI di `import_project_archive` (nessun file `*archive*`/`*project-maintenance*` in `src/`); non so se rigenera l'id prima di aprire.

## Comandi FS Rust e confini (gap 34, lato Rust)

- `run_guarded(label, f)` cattura i panic con `catch_unwind` e li converte in `Err("Internal error in <label>: ...")` [^src: src-tauri/src/panic_guard.rs:13-22,36-46]. Importato in `fs.rs` [^src: src-tauri/src/commands/fs.rs:11].
- `delete_file(path)`: nessun confinamento al progetto, nessun `require_absolute_path`, nessun canonicalize o controllo symlink. Directory: `remove_dir_all` ricorsivo; file: `remove_file`; retry (4 tentativi) solo su Windows [^src: src-tauri/src/commands/fs.rs:1737-1788]. Lato TS `deleteFile` non applica `assertAbsoluteFsPath` [^src: src/commands/fs.ts:112-114].
- Il confine per la cancellazione e' quindi solo applicativo (chiamanti TS, fuori da questa fetta).

| Comando | Controllo sul path |
|---|---|
| `write_file`, `write_file_base64`, `write_file_atomic`, `create_directory` | solo "assoluto" (`require_absolute_path`) [^src: src-tauri/src/commands/fs.rs:35-64,1243-1344,1938-1948] |
| `read_file`, `read_file_as_base64`, `copy_file`, `copy_directory`, `delete_file`, `get_file_*` | nessuno [^src: src-tauri/src/commands/fs.rs:67-130,1660-1755,1970-2078] |
| `apply_text_selection_edit` | canonicalize + `starts_with(project)` + file esistente [^src: src-tauri/src/commands/fs.rs:1354-1362] |
| `create_missing_wiki_page` | canonicalize, wiki e concepts dentro il progetto, `create_new` [^src: src-tauri/src/commands/fs.rs:1419-1494] |
| `open_path_in_project` | canonicalize + `starts_with(root)` [^src: src-tauri/src/commands/project.rs:319-324] |
| `list_file_history`, `restore_file_history` | `checked_file`: dentro il progetto, fuori da `.llm-wiki` [^src: src-tauri/src/commands/file_history.rs:347-358] |

- `list_directory` nasconde i dotfile di default (`include_hidden`), profondita' 1-30 (default 30); non e' un controllo di sicurezza [^src: src-tauri/src/commands/fs.rs:1563-1590].
- `read_file` e `preprocess_file` usano una cache `.cache/<nome>.txt` accanto all'originale e `spawn_blocking` [^src: src-tauri/src/commands/fs.rs:67-235].

## Storia dei file e persistenza in `.llm-wiki` (gap 13 parziale, gap 23 posizione)

- Scritti da `persist.ts` in `<project>/.llm-wiki/`: `review.json`, `lint.json`, `conversations.json`, `chats/<convId>.json` (ultimi 100 messaggi per conversazione; immagini e `beforeContent`/`afterContent` rimossi), `chat-preferences.json` [^src: src/lib/persist.ts:14-44,60-111,244-251].
- File history: `.llm-wiki/history/<fnv1a-64 del path relativo>.json`, array di `{id,path,timestamp,author,tool,content}` con contenuto intero; potatura per file e per store (`MAX_HISTORY_*`, valori non letti) [^src: src-tauri/src/commands/file_history.rs:112-122,189-232,234-290].
- `record_file_version` e' chiamato da `write_file` e `write_file_atomic` (baseline "before.*" poi author "human") e dalle edit dell'agente (author "agent"); non da `write_file_base64`, `copy_file`, `delete_file` [^src: src-tauri/src/commands/fs.rs:1253-1260,1319-1337,1374-1381,1484-1488].
- `chat-history.json` sta in `<project>/.llm-wiki/chat-history.json` ed e' solo formato legacy in lettura (`saveChatHistory` non lo scrive). Ordine di `loadChatHistory`: (1) `conversations.json` + `chats/<id>.json`; (2) recupero dai file orfani in `chats/` (titolo = primi 50 caratteri del primo messaggio utente); (3) `chat-history.json` come array piatto (conversazione "default", titolo "Previous Conversations") o formato combinato `{conversations, messages}` [^src: src/lib/persist.ts:114-175,205-242].
- Non letti: altri scrittori in `.llm-wiki/` (ingest-cache, file_sync) e i conteggi dell'archivio sommario (gap 23).

## Vector v1 vs v2 (gap 17)

- Registrati in `lib.rs`: v1 `vector_upsert`, `vector_search`, `vector_delete`, `vector_count`; v2 `vector_upsert_chunks`, `vector_search_chunks`, `vector_delete_page`, `vector_count_chunks`, `vector_clear_chunks`, `vector_optimize_chunks`, `vector_legacy_row_count`, `vector_drop_legacy` [^src: src-tauri/src/lib.rs:672-683].
- `src/lib/embedding.ts` (letto intero) non invoca i v1: usa solo i v2 [^src: src/lib/embedding.ts:184,210,218,276,282,288,295,304]. Dopo un rebuild forzato elimina la tabella legacy v1 [^src: src/lib/embedding.ts:728-731].
- Non verificati: altri chiamanti TS, `api_server.rs`, `agent/tools.rs`, `search.rs`, `mcp-server`. Non si esclude un uso interno Rust dei v1.

## Setup di `lib.rs`

- Plugin: opener, dialog, store, autostart, http (fetch Rust per aggirare CORS) [^src: src-tauri/src/lib.rs:556-567].
- Setup: hint della resource dir per pdfium, applicazione del proxy da `app-state.json`, stato gestito (CLI claude/codex, file sync, sessioni e cancellazioni agente, close behavior, tray), avvio di `clip_server` e `api_server` prima del tray [^src: src-tauri/src/lib.rs:568-623].
- Chiusura finestra: `exit`, `minimize` (nasconde se c'e' il tray, altrimenti minimizza) o dialogo `ask` [^src: src-tauri/src/lib.rs:704-750].
- Comandi dell'agente (`agent_start_turn`, `_stream`, `_cancel_turn`, `agent_get_session`, `agent_list_sessions`) risolvono il progetto da id o path tramite `projectRegistry`/`recentProjects` [^src: src-tauri/src/lib.rs:64-257,330-403].

## Gap evidenti

- Path OS effettivo di `app_data_dir` per piattaforma.
- Cifratura (o assenza) dei token in `app-state.json`.
- Chiamante UI dell'import e gestione della collisione id.
- Chiamanti dei comandi vector v1 fuori da `embedding.ts`.
- Quali chiamanti TS confinano la cancellazione al progetto.
- `fs.rs` 651-999 e 2230-3300, `file_history.rs` 1-69 e 470 in poi, `lib.rs` 780 in poi: non letti.

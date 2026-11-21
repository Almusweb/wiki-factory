---
id: 2026-11-21-repo-llm_wiki-dossier-ep004-r3
type: source
title: Dossier EP-004 r3 da code_repos/llm_wiki, 2026-11-21: rischio 3, scritture sul registro dei progetti (repo-sync)
status: draft
created: 2026-11-21
updated: 2026-11-21
sources: ["raw/2026-11-21-repo-llm_wiki-dossier-ep004-r3.md"]
tags: [source, repo, llm-wiki, persistenza, registro-progetti, ep-004, rischio-3]
---

# Dossier EP-004 r3 da code_repos/llm_wiki, 2026-11-21: rischio 3, scritture sul registro dei progetti (repo-sync)
> Estrazione mirata `repo-sync` v2.12 del 2026-11-21 sul commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` (HEAD staccato, nessun ramo), stato `partial`, 15 file letti, sola lettura (Q_003). «Osservato» = letto nel codice; «deduzione non testata» = ricavata da fatti osservati, mai eseguita. Il repo è di terzi sotto GNU GPL v3: il raw cita solo nomi, simboli e percorsi.

## Contesto
Terzo dossier della serie di EP-004 (TSK-016 / US-027), dedicato al rischio 3 di [[llm-wiki-rischi-persistenza]]; segue [[2026-11-21-repo-llm_wiki-dossier-ep004-r2]]. Verifica sul sorgente l'ipotesi già in wiki (registro ridotto a una voce da scritture concorrenti o da lettura fallita); non ripete stack e struttura ([[2026-11-20-repo-llm_wiki]]) né i fatti sul plugin store di [[2026-11-21-repo-llm_wiki-persistenza-d]]. L'agente non aveva `Bash` né `Grep`: un «non trovato» del raw vale solo per i file letti. La ricerca testuale globale è stata eseguita dalla sessione principale ed è riportata in TSK-016 §Chiusura, qui in una sezione a parte. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r3.md §Identità e perimetro]

## Dettaglio

### Operazioni che modificano `projectRegistry` (osservato)
- Un solo scrittore noto nei file letti: `saveRegistry` (non esportata) fa `store.set` dell'intero oggetto sulla chiave, senza `store.save()` esplicito (affidata al debounce di `autoSave`); è chiamata solo da `upsertProjectInfo`, che legge con `loadRegistry`, assegna `registry[id]` e salva tutto. Nessun lock, coda o catena di promise; `project-identity.ts` non importa `withProjectLock` (`project-identity.ts:16-18, 86-108`). Nessuna funzione del file cancella voci. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r3.md §1. Operazioni che modificano `projectRegistry` e serializzazione (AC2)]
- `withProjectLock` è una catena di promise per percorso di progetto (`project-mutex.ts:1-57`); il registro è globale e per id, quindi non è coperto. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r3.md §1. Operazioni che modificano `projectRegistry` e serializzazione (AC2)]
- Le due sole catene serializzate sono `saveProjectLlmOverride` (`projectLlmOverrideWrite`, `project-store.ts:50, 130-144`) e `saveCustomLlmPresets` (`customLlmPresetWrite`, `project-store.ts:51, 73-81`). Il commento di `saveProjectLlmOverride` dichiara lo scopo di non «drop another project's entry»: l'autore conosce la classe di difetto per l'altra mappa per id, ma il registro non ha la stessa protezione. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r3.md §1. Operazioni che modificano `projectRegistry` e serializzazione (AC2)]
- Lato Rust il registro è solo letto (`lib.rs:346-409`, `api_server.rs:727-835`), nei punti letti dal dossier. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r3.md §1. Operazioni che modificano `projectRegistry` e serializzazione (AC2)]
- Scritture adiacenti con la stessa forma senza catena, su chiavi diverse: `saveOutputLanguage`, `saveProjectFileSyncEnabled`, `saveSourceWatchConfig`, `addToRecentProjects`, `removeFromRecentProjects` (`project-store.ts:34-42, 364-381, 413-463`). [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r3.md §1. Operazioni che modificano `projectRegistry` e serializzazione (AC2)]

### Percorso «lettura fallita, poi scrittura» (osservato)
`getStore()` riapre `app-state.json` a ogni chiamata; `loadRegistry` ritorna `{}` sia con chiave assente sia per qualsiasi eccezione, senza log né flag (`project-identity.ts:72-84`). Con `{}` di partenza `upsertProjectInfo` scrive una sola voce (id, percorso normalizzato, nome, `lastOpened`) e `saveRegistry` sostituisce l'intera chiave (`project-identity.ts:95-108, 86-89`), senza merge. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r3.md §2. Percorso «lettura fallita, poi scrittura» (AC3)]

### Chiamanti e doppio aggiornamento senza attesa (osservato, salvo dove indicato)
- `upsertProjectInfo` è chiamata solo da `createProject` e `openProject`, sempre con `await` e dopo `await ensureProjectId` (`fs.ts:248-263`). Nei file letti nessun punto lancia due upsert in catena senza `await`. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r3.md §3. Chiamanti di `upsertProjectInfo` e doppio aggiornamento senza attesa (AC4)]
- Chiamanti di `openProject` / `createProject`: `init` all'avvio (`App.tsx:415-423`), `handleSelectRecent` (`595-602`), `handleOpenProject` (`604-617`), `handleCreate` di `CreateProjectDialog` (`create-project-dialog.tsx:99-140`), `handleImportProject` (`maintenance-section.tsx:218-230`). `handleProjectOpened` non chiama `upsertProjectInfo` (`App.tsx:433-593`). [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r3.md §3. Chiamanti di `upsertProjectInfo` e doppio aggiornamento senza attesa (AC4)]
- Osservato (assenza nel codice letto): `handleSelectRecent` e `handleOpenProject` non hanno guardia di rientro (`App.tsx:595-617`; `welcome-screen.tsx:62-65`). L'avvio non è un caso: l'interfaccia resta su «Loading» finché `init` non termina. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r3.md §3. Chiamanti di `upsertProjectInfo` e doppio aggiornamento senza attesa (AC4)]
- **Deduzione non testata:** due aperture ravvicinate, oppure import più apertura di un altro progetto, potrebbero sovrapporsi; la doppia `init` per `StrictMode` (`main.tsx:23-27`) riguarderebbe lo stesso id (perdita nulla) e la sua presenza in produzione non è letta. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r3.md §3. Chiamanti di `upsertProjectInfo` e doppio aggiornamento senza attesa (AC4)]

### Rischio di aggiornamento perso
Fra `get` e `set` di una `upsertProjectInfo` ci sono almeno due punti `await` (`project-identity.ts:76-89, 100-107`): il codice JS non impedisce l'interleaving. Deduzione non testata: due upsert con id diversi che leggono lo stesso snapshot perdono la voce del primo a scrivere; il registro si ridurrebbe a **una sola voce** solo se lo snapshot letto fosse vuoto. Impatti a valle (osservati nel codice, innesco deduzione non testata): `startTask` marca `failed` i task con «Project not found in registry» (`ingest-queue.ts:1183-1193`); `getProjectIdByPath` ritorna `null`; i lettori Rust ripiegano su `recentProjects` e `project.json` (`api_server.rs:801-823`, `lib.rs:370-392`); riaprire il progetto ricrea la voce. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r3.md §4. Rischio di aggiornamento perso (AC5, AC6)]

### Ricerca testuale globale (sessione principale, estende i negativi del dossier)
Eseguita su `src` e `src-tauri/src` (TS/TSX/RS, esclusi test), riportata in TSK-016 §Chiusura (il comando è lì; qui se ne citano solo gli esiti):
- **Scrittore unico:** `projectRegistry` è scritto solo da `saveRegistry` (`project-identity.ts:86`), chiamata solo da `upsertProjectInfo` (`:107`). Lato Rust solo lettura (`lib.rs:350`, `api_server.rs:778`); nessun `StoreExt` né scrittura Rust di `app-state.json` (unico riferimento al plugin: `lib.rs:558`, registrazione). Il negativo «nessun altro scrittore» vale per tutto il codice TS/Rust cercato.
- **Chiamanti:** `openProject(` a `App.tsx:418, 597, 612` e `maintenance-section.tsx:226`; `createProject(` solo a `create-project-dialog.tsx:115`. Sono gli unici punti da cui parte un upsert.
- **Nessuna finestra aggiuntiva a runtime:** nessuna occorrenza di `WebviewWindow` in `src` e `src-tauri/src`; con la sola finestra di `tauri.conf.json` la concorrenza possibile sta dentro un unico frontend, non fra finestre.
- `withProjectLock(` è usata solo in `ingest.ts`, mai sul registro.

[^src: management/kanban/EP-004-verifica-rischi-di-persistenza/US-027-rischio-scritture-registro/TSK-016.md §Chiusura]

### Esito proposto
**Confermato per lettura sul meccanismo; non conclusivo sulla concorrenza reale.** Precisazioni: la concorrenza da sola perde le voci aggiunte nella finestra, non riduce a una voce; chiave assente ed errore di lettura sono indistinguibili. Impatto se si verifica: perdita di voci id → percorso e nome, task di ingest dell'id mancante `failed`; nessuna perdita di pagine, sorgenti, chat, review o lint; recuperabile riaprendo il progetto. Gravità proposta dal dossier: bassa-media, probabilità non determinabile. Non conclusivo per: interleaving reale, semantica del plugin store JS e Rust (non letta), frequenza di `store.get` che rifiuta con `set` riuscito. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r3.md §5. Esito proposto: NON CONCLUSIVO sulla concorrenza; CONFERMATO per lettura sul meccanismo]

### File non letti
`@tauri-apps/plugin-store` (JS) e `tauri-plugin-store` `lib.rs`/`store.rs`; test `project-store`, `project-mutex`, `project-store-source-watch`; `dedup-queue.ts`, `source-lifecycle.ts`, resto di `ingest-queue.ts`, `components/layout/*`, `sources-view.tsx`; `lib.rs` oltre 340-424 e 550-600, `clip_server.rs`, `server_bind.rs`, `proxy.rs`; `commands/fs.rs`, `project.rs`. Per scrittori e chiamanti la lacuna è in gran parte colmata dalla ricerca globale sopra (non per test e non-TS/Rust). [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r3.md §File letti e non letti]

### Controllo del repo e dei segreti dichiarato
L'agente non ha eseguito `git status`; il controllo a comando è stato fatto dalla sessione principale (TSK-016 §Chiusura: `git -C code_repos/llm_wiki log -1 --format=%h` → `e08cfce`, `status --short` → vuoto; `grep -ciE` sui pattern dei segreti sul dossier → 0). Il dossier ha letto solo nomi di chiavi e tipi, nessun valore. Nessuna istruzione rivolta a un agente trovata nei file letti. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r3.md §Note di estrazione] [^src: management/kanban/EP-004-verifica-rischi-di-persistenza/US-027-rischio-scritture-registro/TSK-016.md §Chiusura]

## Pagine collegate
[[llm-wiki-rischi-persistenza]] (§Esito della verifica di US-027), [[llm-wiki-gestione-file-corrotti]], [[llm-wiki-archivi-persistenza]], [[2026-11-21-repo-llm_wiki-persistenza-d]], [[gaps]].

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

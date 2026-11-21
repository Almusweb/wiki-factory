---
id: 2026-11-21-repo-llm_wiki-dossier-ep004-r2
type: source
title: Dossier EP-004 r2 da code_repos/llm_wiki, 2026-11-21: rischio 2, rigenerazione dell'identità del progetto (repo-sync)
status: draft
created: 2026-11-21
updated: 2026-11-21
sources: ["raw/2026-11-21-repo-llm_wiki-dossier-ep004-r2.md"]
tags: [source, repo, llm-wiki, persistenza, identita-progetto, ep-004, rischio-2]
---

# Dossier EP-004 r2 da code_repos/llm_wiki, 2026-11-21: rischio 2, rigenerazione dell'identità del progetto (repo-sync)
> Estrazione mirata `repo-sync` v2.12 del 2026-11-21 sul commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` (HEAD staccato, nessun ramo), stato `partial`, 11 file letti, sola lettura (Q_003). «Osservato» = letto nel codice; «deduzione non testata» = ricavata da fatti osservati, mai eseguita. Il repo è di terzi sotto GNU GPL v3: il raw cita solo nomi, simboli e percorsi.

## Contesto
Secondo dossier della serie di EP-004 (TSK-014 / US-026), dedicato al rischio 2 di [[llm-wiki-rischi-persistenza]]; segue [[2026-11-21-repo-llm_wiki-dossier-ep004-r1]]. Verifica sul sorgente l'ipotesi già in wiki e il contesto di [[2026-11-21-repo-llm_wiki-fs-lib-progetto]]; non ripete stack e struttura ([[2026-11-20-repo-llm_wiki]]). L'estrazione non ha avuto `Bash` né `Grep`: un «non trovato» del raw vale solo per i file e le righe letti; la ricerca testuale globale è stata eseguita dalla sessione principale (TSK-014 §Chiusura) ed è riportata a parte. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r2.md §Identità e perimetro]

## Dettaglio

### Chi assegna l'id (osservato)
- L'id è assegnato dal frontend. `WikiProject` (Rust) ha solo `name` e `path` (`types/wiki.rs:3-7`); `create_project` e `open_project` non scrivono `.llm-wiki/` né `project.json` (`project.rs:16-264`); `import_project_archive_inner` restituisce solo il percorso (`project_maintenance.rs:204-267`). `createProject` e `openProject` (TS) chiamano `ensureProjectId` e `upsertProjectInfo` (`commands/fs.ts:248-263`). [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r2.md §Passo 1. Chi assegna l'id: il frontend, non il backend (osservato)]

### Percorso «file di identità illeggibile» (osservato)
- `ensureProjectId` (`project-identity.ts:47-68`) ritorna l'id esistente solo se `project.json` è JSON con `id` stringa non vuota; ogni altro caso (file assente, illeggibile per qualunque errore, JSON non valido, senza `id`) cade nel `catch` e genera un nuovo UUID con `crypto.randomUUID()` e un nuovo `createdAt`. Scrittura con `writeFile`; se fallisce c'è solo `console.warn` e la funzione ritorna comunque l'id nuovo. Il file danneggiato è sostituito, senza copia di riserva; la funzione non riceve né legge alcun id precedente. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r2.md §Passo 2. Generazione del nuovo id in `ensureProjectId` (osservato)]
- `upsertProjectInfo` (`project-identity.ts:95-108`) assegna `registry[id]` senza cercare altre voci con lo stesso percorso e senza rimuovere nulla: la voce con il vecchio id e lo stesso percorso resta nel registro. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r2.md §Passo 3. Registro dei progetti: `upsertProjectInfo` e voci stantie (osservato)]
- Destino del vecchio id: non conservato dal codice di identità; sopravvive per effetto collaterale nella voce stantia del registro, nelle chiavi per id dello store e nel `projectId` dei task di `ingest-queue.json` finché `restoreQueue` non li scarta. Nessun punto lo usa per migrare. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r2.md §Passo 4. Destino del vecchio id (sintesi)]

### Ripartenza della coda (osservato)
- `restoreQueue` (`ingest-queue.ts:955-1026`) è chiamata da `handleProjectOpened` dopo `openProject` (`App.tsx:415-419, 496-501`), con l'id nuovo. Tiene solo i task con `projectId` uguale all'id corrente e scrive un `console.warn` («Dropped N cross-project tasks»); poi `saveQueue` **riscrive `ingest-queue.json`** senza i task scartati (`ingest-queue.ts:985-1004`): lo scarto è permanente su disco, senza avviso in interfaccia nel codice letto. I task senza `projectId` sono adottati dall'id corrente (`160-174`). [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r2.md §Ripartenza della coda: `restoreQueue` (osservato)]
- Si perderebbero i task pending, processing, failed e cancelled; i `done` non sono mai salvati. Se i sorgenti vengano riaccodati dalla sincronizzazione dei file non è stato letto: deduzione non testata. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r2.md §Ripartenza della coda: `restoreQueue` (osservato)]

### Impostazioni per id (osservato)
- I tipi di `wiki-store.ts` non definiscono mappe per id (un solo valore per il progetto attivo); le mappe per id sono in `project-store.ts`. Con id nuovo: `projectLlmOverrides` torna disattivato (`project-store.ts:130-156`); `projectOutputLanguages` torna null e `App.tsx` ripiega sulla lingua globale o «auto» (`413-429`; `App.tsx:458-462`); `projectFileSyncEnabled` torna a `default` se presente, altrimenti `true` (`431-452`); `sourceWatchConfig` torna a `default` o al valore ricavato dal legacy (`454-474`). Le voci con il vecchio id restano nello store, inutilizzate: non sono orfane con effetto nullo ma tornano silenziosamente ai default o ai valori globali. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r2.md §Impostazioni per progetto indicizzate per id (osservato)]
- Non risentono della rigenerazione: `scheduledImportConfig:<percorso>` (chiave per percorso, `project-store.ts:335-362`) e gli archivi sotto `.llm-wiki/` indirizzati dal percorso (`review.json`, `lint.json`, `conversations.json`, `chats/`, `chat-preferences.json`; `persist.ts:14-44, 244-251`). [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r2.md §Impostazioni per progetto indicizzate per id (osservato)]

### Ricerca testuale globale (sessione principale, estende i negativi del dossier)
Il dossier non aveva `Grep`; la sessione principale ha cercato su `src` e `src-tauri/src` (TS/TSX/RS, esclusi test). Esito riportato in TSK-014 §Chiusura: `ensureProjectId` e `upsertProjectInfo` chiamati solo da `commands/fs.ts:253-254` e `260-261`; `store.delete(` solo in `project-store.ts:357` e `379` (chiavi non legate all'id): **nessun riallineamento al nuovo id in tutto il codice TS/Rust cercato**; `getProjectIdByPath` (`project-identity.ts:124`) non ha chiamanti; `getProjectPathById` ha due chiamanti (`ingest-queue.ts:1185`, `dedup-queue.ts:335`); `restoreQueue` di `dedup-queue.ts:273-296` filtra per `projectId` e scarta gli altri con `console.warn` (chiamata da `App.tsx:503-504`); `api_server.rs` legge per `project_id` `projectLlmOverrides` (2364-2369, ripiego su `llmConfig` globale), `sourceWatchConfig` (2920) e `projectFileSyncEnabled` (2931). [^src: management/kanban/EP-004-verifica-rischi-di-persistenza/US-026-rischio-identita-progetto/TSK-014.md §Chiusura]

### Collisione di id dopo l'import (punto separato, rischio 3)
Catena letta: `handleImportProject` in `MaintenanceSection` (`maintenance-section.tsx:218-230`) invoca `import_project_archive`, poi `openProject` e `addToRecentProjects`; lo zip riporta `project.json` se presente, `ensureProjectId` ritorna lo stesso id e `upsertProjectInfo` assegna `registry[id]` al nuovo percorso senza controllo; l'import non passa da `handleProjectOpened`; `startTask` risolve il percorso dal registro per id (`ingest-queue.ts:1183-1193`). Esito: **non conclusivo** (deduzione non testata, esecuzione non provata). [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r2.md §Collisione di id dopo l'import (punto separato, rischio 3, non allarga l'esito del rischio 2)]

### Esito proposto
**CONFERMATO per lettura** (con riserva sul negativo, ora ristretta dalla ricerca globale). Impatto: perdita dei task di ingest in coda dell'intero progetto e reset silenzioso delle impostazioni per progetto; nessuna perdita di pagine wiki, sorgenti, chat, review o lint. Non conclusivo: l'innesco (come `project.json` diventi illeggibile) e il comportamento di `read_file` su errore transitorio. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r2.md §Esito proposto: CONFERMATO per lettura (con una riserva sul negativo)]

### Discrepanza di citazione nel raw precedente
Il dossier segnala che `raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md` cita `src/lib/persist.ts` per l'apertura dello store e le chiavi; nel sorgente sono in `src/lib/project-store.ts` (`persist.ts` non contiene alcun accesso a `app-state.json`, righe 1-80 e 240-304 lette). Contenuto corretto, nome del file no. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r2.md §Gap evidenti]

### File non letti e gap evidenti
Non letti: corpi di `read_file` e `write_file` (`fs.rs`), `dedup-queue.ts` (letto dalla sessione principale solo nelle righe 273-296, riportate sopra), `project-file-sync.ts`, clip watcher, `lib.rs`, `source-watch-config.ts`, parti non attinenti di `App.tsx` e `fs.ts`. Gap del raw: condizioni reali di corruzione, `read_file` su errore transitorio, effetto di due voci di registro per lo stesso percorso, valori predefiniti di `sourceWatchConfig`, riscrittura su disco della coda di dedup. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r2.md §File letti e non letti] [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r2.md §Gap evidenti]

### Controllo del repo e dei segreti dichiarato dal raw
L'agente non ha eseguito `git status`; il controllo a comando è stato fatto dalla sessione principale (TSK-014 §Chiusura: `status --short` vuoto, commit `e08cfce`; `grep -ciE` sui pattern dei segreti sul dossier: 0). Nessun valore di credenziale: solo nomi di simboli e percorsi. Nessuna istruzione rivolta a un agente trovata nei file letti. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r2.md §Note di estrazione]

## Pagine collegate
[[llm-wiki-rischi-persistenza]] (§Esito della verifica di US-026), [[llm-wiki-gestione-file-corrotti]], [[llm-wiki-archivi-persistenza]], [[llm-wiki-operazioni-distruttive]], [[2026-11-21-repo-llm_wiki-fs-lib-progetto]], [[gaps]].

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

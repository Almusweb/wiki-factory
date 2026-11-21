---
source_path: /home/user/wiki-factory/code_repos/llm_wiki
source_type: repo
git_branch: HEAD
git_commit: e08cfce65aad8b76b13546a081c1a8d4422b70c3
extracted_at: 2026-11-21
extractor: repo-sync@2.12.0
scope: dossier EP-004 r2 (TSK-014 / US-026), rischio 2, rigenerazione dell'identità del progetto
---

# Specifiche estratte: llm-wiki, dossier EP-004 r2 (rischio 2, identità del progetto rigenerata)

> Documento generato da `repo-sync` v2.12 il 2026-11-21. Sorgente: `/home/user/wiki-factory/code_repos/llm_wiki`
> @ commit `e08cfce` (HEAD staccato, nessun nome di ramo: il file `HEAD` del submodule contiene solo l'hash, riletto in questa sessione). Read-only verso la sorgente.

## Identità e perimetro

- Estrazione **mirata** (TSK-014 / US-026), solo per sola lettura del codice (Q_003). Stack, struttura e dipendenze non sono ripetuti (vedi `raw/2026-11-20-repo-llm_wiki.md`). L'ipotesi di partenza (wiki, `llm-wiki-rischi-persistenza` voce 2) e il contesto di `raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md` sono verificati sul sorgente, non ricopiati.
- **Licenza**: repository di terzi, GNU GPL v3. Il documento descrive il codice con parole proprie e cita solo file, simboli, campi e percorsi. Nessun frammento di codice.
- Citazioni nella forma `[^src: percorso:righe]`, percorsi relativi alla radice del repo del cliente.
- «Osservato» = letto nel codice. «Deduzione non testata» = ricavato da fatti osservati, mai visto in esecuzione. Nessuna esecuzione dell'app, nessun test, nessuna ricerca testuale globale (questo agente non ha `Bash` né `Grep`). Un «non trovato» vale solo per i file e le righe elencati in §File letti.
- Perimetro fissato dal TSK: `ensureProjectId` e `upsertProjectInfo`; `restoreQueue`; tipi in `wiki-store.ts` e punti di scrittura delle quattro impostazioni per progetto; ricerca di un riallineamento; lato Rust solo per confermare che non assegna l'id. La collisione dopo l'import è riportata a parte (§Collisione di id dopo l'import) e non allarga l'esito del rischio 2.

## Ipotesi di partenza (come in wiki)

Da `wiki/concepts/llm-wiki-rischi-persistenza.md`, voce 2 (deduzione): un `project.json` corrotto produce in `ensureProjectId` un nuovo UUID; `restoreQueue` scarta come «cross-project» i task con il vecchio id; le impostazioni per progetto in `app-state.json`, indicizzate per id (`projectLlmOverrides`, `projectOutputLanguages`, `sourceWatchConfig`, `projectFileSyncEnabled`), resterebbero orfane. Da `US-026`: l'id è assegnato dal frontend.

## Tracciamento del percorso «file di identità illeggibile»

### Passo 1. Chi assegna l'id: il frontend, non il backend (osservato)

| Simbolo | Cosa fa | Fonte |
|---|---|---|
| `WikiProject` (Rust) | struct con soli `name` e `path`: nessun campo id | src-tauri/src/types/wiki.rs:3-7 |
| `create_project` / `create_project_impl` | crea cartelle e file del wiki (schema, purpose, index, log, overview, `.obsidian/*`); restituisce `WikiProject` con nome e percorso; **non scrive `.llm-wiki/` né `project.json`** | src-tauri/src/commands/project.rs:16-242 (ritorno 237-241) |
| `open_project` | valida `schema.md` e `wiki/` (`validate_wiki_project_root`, 342-364); restituisce nome e percorso con barre normalizzate; non scrive nulla | project.rs:244-264 |
| `import_project_archive_inner` | verifica, estrae e **restituisce solo il percorso** della radice; nessuna lettura né scrittura dell'id | src-tauri/src/commands/project_maintenance.rs:204-267 (ritorno 266) |
| `RawProject` (TS) | il commento dichiara che l'id è attaccato lato client | src/commands/fs.ts:6-10 |
| `createProject`, `openProject` (TS) | chiamano il comando Rust, poi `ensureProjectId(raw.path)` e `upsertProjectInfo(id, raw.path, raw.name)`; restituiscono `{id, name, path}` | src/commands/fs.ts:248-263 |

Conferma del vincolo di US-026: per i tre comandi Rust del perimetro l'id non è assegnato dal backend (osservato; `create_project_impl` letto per intero, 16-242).

### Passo 2. Generazione del nuovo id in `ensureProjectId` (osservato)

[^src: src/lib/project-identity.ts:39-41, 47-68]

1. Percorso del file: `<progetto normalizzato>/.llm-wiki/project.json` (`identityPath`, 39-41).
2. Legge il file con `readFile` e lo analizza come JSON. Se l'oggetto ha un campo `id` stringa **non vuota** (condizione di verità, 52), ritorna quell'id: è l'unico ramo che conserva l'identità.
3. Qualunque eccezione di lettura o di analisi è inghiottita dal blocco `catch` (55-57, commento «missing or corrupt — fall through to create»). Il ramo non distingue file assente, file illeggibile (qualunque errore del comando `read_file`), JSON non valido, JSON valido senza `id`, `id` non stringa o vuoto: **tutti producono un nuovo id**.
4. Nuovo id: `crypto.randomUUID()` con `createdAt` = `Date.now()` (58-61). `createdAt` originale non è conservato.
5. Scrittura: `writeFile(path, JSON)` (63); un errore è ignorato con solo `console.warn` (64-66) e la funzione **ritorna comunque il nuovo id** (67).

Effetti letti nel codice:

- **Nessun accesso al vecchio id**: la funzione non legge il registro né lo store e non riceve alcun id precedente. Il vecchio valore, se il file era JSON valido ma privo di id utilizzabile, viene scartato; se il file era illeggibile non è mai stato letto.
- **Sovrascrittura**: `writeFile` (TS) richiede un percorso assoluto e invoca `write_file` [^src: src/commands/fs.ts:22-25]; per la semantica di `write_file` (scrittura diretta con creazione delle cartelle padre) si rimanda al wiki (`llm-wiki-rischi-persistenza`, rischio 4, fetta B), qui non riletta. Il file danneggiato viene quindi **sostituito**, non archiviato né salvato in copia: nessuna copia di riserva nel codice letto.
- **Deduzione non testata**: poiché la `catch` copre anche errori di lettura transitori (file bloccato, permessi), un `project.json` **valido** potrebbe essere sostituito con un id nuovo per un errore passeggero. Il codice lo rende possibile (3 sopra); che `read_file` Rust fallisca in quel modo non è stato letto.
- **Deduzione non testata**: se la scrittura del nuovo file fallisce, l'id è effimero (ritorna ma non è persistito). A ogni apertura successiva `ensureProjectId` ne rigenererebbe uno nuovo, e `upsertProjectInfo` aggiungerebbe ogni volta una voce nuova al registro (nessun controllo per percorso: vedi passo 3).

### Passo 3. Registro dei progetti: `upsertProjectInfo` e voci stantie (osservato)

[^src: src/lib/project-identity.ts:72-108]

- `loadRegistry` legge la chiave `projectRegistry` di `app-state.json` e, in caso di eccezione o chiave assente, restituisce `{}` (76-84).
- `upsertProjectInfo(id, path, name)` carica il registro, assegna `registry[id]` con percorso normalizzato, nome e `lastOpened`, e salva l'intero oggetto (95-108). **Non cerca altre voci con lo stesso percorso e non rimuove nulla.**
- Conseguenza letta: dopo la rigenerazione l'id nuovo si aggiunge; la voce con il **vecchio id e lo stesso percorso resta nel registro** (nel codice letto nessuna funzione cancella voci del registro: `project-identity.ts` per intero).
- **Deduzione non testata**: `getProjectIdByPath` restituisce il primo valore del registro con percorso uguale (124-131). Con due voci per lo stesso percorso e ordine di inserimento mantenuto dalla serializzazione JSON, restituirebbe il **vecchio** id. Il chiamante dichiarato nel commento è il clip watcher (119-123), **non letto**: l'effetto reale non è noto.

### Passo 4. Destino del vecchio id (sintesi)

Il vecchio id **non è conservato dal codice di identità**. Sopravvive, per effetto collaterale, in: voce stantia del registro (stesso percorso), chiavi per id nello store (passo 6), `projectId` dei task in `ingest-queue.json` finché `restoreQueue` non li scarta (passo 5). Nessun punto letto lo usa per migrare: osservato nei file letti (`project-identity.ts`, `project-store.ts`, `ingest-queue.ts`, `App.tsx` 395-655, `fs.ts` 225-287).

## Ripartenza della coda: `restoreQueue` (osservato)

Chiamata in `handleProjectOpened` con `restoreQueue(proj.id, proj.path)`, **dopo** `openProject` (che ha già prodotto il nuovo id) [^src: src/App.tsx:415-419, 496-501]. Lo stesso schema è usato per la coda di dedup (503-507; `dedup-queue.ts` non letto).

`restoreQueue` [^src: src/lib/ingest-queue.ts:955-1026]:

1. Azzera lo stato in memoria e imposta `currentProjectId` all'id **nuovo** (959-974).
2. `loadQueue(pp, projectId)` legge `.llm-wiki/ingest-queue.json` e ricostruisce i task; **solo se `projectId` è assente (null o undefined)** lo riempie con l'id corrente; un task con id vecchio **resta col vecchio id** (160-174, in particolare 167-170). Eccezione di lettura o JSON non valido: coda vuota (171-173).
3. Se la coda letta è vuota ritorna (980-983).
4. `mine = saved.filter(projectId === id corrente)`; se ne scarta qualcuno emette **solo `console.warn`** («Dropped N cross-project tasks during restore») (987-992). Nessun avviso in interfaccia nel codice letto.
5. **Il filtro è anche distruttivo su disco**: `queue = mine` e subito `await saveQueue(pp)` (1003-1004). `saveQueue` riscrive `ingest-queue.json` con i soli task non `done` della coda in memoria (125-139). I task scartati **spariscono dal file**: non sono più recuperabili da disco. Con `mine` vuoto il file diventa `[]`.
6. Task con `projectId` **mancante** (file scritto da versione precedente alla comparsa del campo) sono salvi, perché adottati dall'id nuovo (167-170). I task creati dal codice letto portano sempre `projectId` (`upsertQueuedIngestTask`, 247-257; `enqueueInactiveProjectBatch`, 383-392).

Tipo del task: `IngestTask` con `projectId`, `sourcePath` (relativo al progetto), `folderContext`, `status` (pending, processing, done, failed, cancelled), `addedAt`, `error`, `retryCount` [^src: src/lib/ingest-queue.ts:12-24]. Il commento di 14-16 dichiara l'id preferito al percorso proprio perché il percorso può cambiare.

Cosa si perde e cosa no (deduzione dal codice letto, non testata): si perdono i task `pending`, `processing` (riportati a pending al restore), `failed` e `cancelled`; i `done` non sono mai salvati (128). I file in `raw/sources` e le pagine già scritte non sono toccati da `restoreQueue`. Se i sorgenti vengano riaccodati dalla sincronizzazione dei file non è stato letto (`project-file-sync.ts` non letto).

## Impostazioni per progetto indicizzate per id (osservato)

I tipi in `wiki-store.ts` **non** definiscono mappe per id: lo store Zustand tiene un solo valore per il progetto attivo (`projectLlmOverride`, `outputLanguage`, `sourceWatchConfig`, rispettivamente 440, 444, 447), con tipi `ProjectLlmOverride` (371-383) e `SourceWatchConfig` (270-284) senza id [^src: src/stores/wiki-store.ts]. Le mappe per id sono in `project-store.ts`, chiave per chiave di `app-state.json`:

| Chiave | Forma | Scrittura | Lettura con id nuovo | Fonte |
|---|---|---|---|---|
| `projectLlmOverrides` | mappa id → `ProjectLlmOverride` | `saveProjectLlmOverride(projectId, config)`, catena di scrittura serializzata | `loadProjectLlmOverride(id)`: voce assente → `enabled` falso, `presetId` null, `model` vuoto: **override disattivato in silenzio** | project-store.ts:130-156 |
| `projectOutputLanguages` | mappa id → lingua | `saveOutputLanguage(lang, projectId?)` (scrive anche la chiave globale) | `loadOutputLanguage(id)` → null; `App.tsx` ripiega sulla lingua globale o «auto» | project-store.ts:413-429; App.tsx:458-462 |
| `projectFileSyncEnabled` | mappa id → booleano, più chiave `default` | `saveProjectFileSyncEnabled(enabled, projectId?)` | voce assente → `default` se presente, **altrimenti `true`** | project-store.ts:431-452 |
| `sourceWatchConfig` | mappa id → config, chiave `default` se senza id | `saveSourceWatchConfig(config, projectId?)` | voce assente → config `default` se presente, altrimenti ricavata dal valore legacy di `projectFileSyncEnabled` | project-store.ts:454-474 |

Fatti osservati sul riallineamento:

- **Nessuna cancellazione né migrazione** di queste chiavi in `project-store.ts` (letto per intero): l'unico `store.delete` riguarda `lastProject` e la chiave globale legacy `scheduledImportConfig`. Le voci con il vecchio id **restano nello store, inutilizzate**, non sono distrutte.
- **Nessun punto che riallinei al nuovo id** nei file letti: né `ensureProjectId`, né `upsertProjectInfo`, né `restoreQueue`, né `handleProjectOpened` (433-593), che carica ogni impostazione con `proj.id` (448, 459, 480, 516).
- Differenza rispetto alla deduzione in wiki: non tutte restano «orfane» con effetto nullo. `sourceWatchConfig` e `projectFileSyncEnabled` ripiegano su `default` o su `true`; `projectLlmOverrides` torna disattivato; la lingua per progetto ripiega sulla globale. L'impatto è un **ritorno silenzioso ai valori di default o globali**, non un errore.
- `saveSourceWatchConfig` e `saveProjectFileSyncEnabled` non sono serializzate (a differenza di `saveProjectLlmOverride`): è il tema del rischio 3, non allargato qui.
- Chiave per **percorso**, non per id: `scheduledImportConfig:<percorso>` [^src: src/lib/project-store.ts:335-362]. Non risente della rigenerazione.
- Archivi sotto `.llm-wiki/` indirizzati dal percorso (`review.json`, `lint.json`, `conversations.json`, `chats/`, `chat-preferences.json`) [^src: src/lib/persist.ts:14-44, 244-251]: **non risentono** della rigenerazione dell'id (osservato).
- Non letti e quindi non classificati: altri archivi con `projectId` o chiave per id (`dedup-queue.json`, `file-change-queue.json`, per dichiarazione del wiki, e le chiavi usate dal lato Rust per `projectRegistry`).

## Collisione di id dopo l'import (punto separato, rischio 3, non allarga l'esito del rischio 2)

Gap `llm-wiki-import-id-duplicato`: **deduzione non testata**, con catena di fatti osservati.

Osservato:

1. Il chiamante UI è `handleImportProject` in `MaintenanceSection`: sceglie zip e cartella di destinazione, invoca `import_project_archive`, poi `openProject(path)` e `addToRecentProjects(imported)` [^src: src/components/settings/sections/maintenance-section.tsx:218-230]. Corregge la riga 86 del wiki («non trovato in `src/`»), già segnalata da lint W19.
2. `import_project_archive_inner` estrae tutte le voci dello zip, `.llm-wiki/project.json` incluso se presente, senza leggere né rigenerare l'id (project_maintenance.rs:204-267). L'esportazione include i file nascosti (fetta C1, project_maintenance.rs:134-190, non riletta qui).
3. `openProject` chiama `ensureProjectId`: se `project.json` è nello zip e valido, **ritorna lo stesso id dell'originale** (project-identity.ts:52-54); poi `upsertProjectInfo` assegna `registry[id]` con il **nuovo percorso**, senza controllare che l'id esista già con un altro percorso (project-identity.ts:95-108).
4. La procedura di import **non** passa da `handleProjectOpened`: il progetto importato non diventa quello attivo; si aggiornano solo registro e recenti (maintenance-section.tsx:226-228).
5. `startTask` risolve il percorso del progetto **dal registro per id** (`getProjectPathById`) e lo passa a `runTask` e ad `autoIngest` come radice di lettura e scrittura [^src: src/lib/ingest-queue.ts:1183-1193, 1235, 1086-1102].

Deduzione non testata: se l'originale è il progetto attivo con task pending e si importa una copia del suo export in un'altra cartella, il registro punterebbe alla copia; il successivo `startTask` dei task dell'originale leggerebbe `registryPath` della copia, quindi l'ingest scriverebbe nella copia (non verificato che il registro sia riletto a ogni task: lo è per lettura di 1185). Riaprire l'originale riporta il registro al suo percorso (stesso `upsertProjectInfo`). Le impostazioni per id (tabella sopra) sarebbero condivise dalle due copie. Il caso richiede zip contenente `project.json` e importazione nella stessa installazione. Esito proposto per questo punto: **non conclusivo** (catena letta, esecuzione non provata; clip watcher e chiamanti di `getProjectPathById` non letti).

## Esito proposto: CONFERMATO per lettura (con una riserva sul negativo)

| # | Evidenza | Livello | Fonte |
|---|---|---|---|
| 1 | L'id è assegnato dal frontend; i tre comandi Rust non lo assegnano né lo scrivono | osservato | types/wiki.rs:3-7; project.rs:16-264; project_maintenance.rs:204-267; fs.ts:248-263 |
| 2 | Un `project.json` illeggibile, non valido o senza `id` valido produce un nuovo UUID, scritto sul posto; errori di lettura qualsiasi trattati come «corrotto» | osservato | project-identity.ts:47-68 |
| 3 | Il vecchio id non è conservato dalla funzione di identità; `createdAt` perso | osservato | project-identity.ts:47-68 |
| 4 | `upsertProjectInfo` non rimuove la voce col vecchio id e stesso percorso | osservato | project-identity.ts:95-108 |
| 5 | `restoreQueue` scarta i task con vecchio id e **riscrive `ingest-queue.json` senza di essi**; solo `console.warn` | osservato | ingest-queue.ts:160-174, 985-1004 |
| 6 | Le quattro impostazioni sono per id; con id nuovo tornano a default o globale; le voci vecchie restano inutilizzate nello store | osservato | project-store.ts:130-156, 413-474; App.tsx:448-462, 480, 516 |
| 7 | Nessun punto riallinea le impostazioni al nuovo id nei file letti | osservato (negativo limitato ai file letti) | project-store.ts; project-identity.ts; ingest-queue.ts; App.tsx:395-655 |
| 8 | Review, lint, chat e preferenze chat, indirizzati dal percorso, non risentono della rigenerazione | osservato | persist.ts:14-44, 244-251 |
| 9 | Un errore di lettura transitorio potrebbe sostituire un `project.json` valido | deduzione non testata | project-identity.ts:49-57 |
| 10 | Scrittura fallita: id effimero e voci in più nel registro a ogni apertura | deduzione non testata | project-identity.ts:62-67, 95-108 |
| 11 | La voce stantia potrebbe far restituire il vecchio id a `getProjectIdByPath` | deduzione non testata | project-identity.ts:124-131 |

- **Confermato** (per lettura): le tre parti dell'ipotesi, con due precisazioni rispetto alla wiki: lo scarto dei task è **permanente su disco** (non solo in memoria) e le impostazioni **ripiegano su default o globale** invece di restare «orfane» senza effetto.
- **Impatto sui dati se si verifica**: **perdita** dei task di ingest in coda dell'intero progetto (pending, failed, cancelled), senza avviso in interfaccia nel codice letto; **reset silenzioso** di override LLM per progetto, lingua di output per progetto e configurazione di osservazione dei sorgenti (con possibile ritorno a `true` della sincronizzazione file, per la regola di ripiego). Nessuna perdita di pagine wiki, sorgenti, chat, review o lint (indirizzati dal percorso). I dati per id restano nello store e sono recuperabili a mano.
- **Riserve**: (1) il negativo «nessun riallineamento» vale solo per i file letti; lo chiude la ricerca testuale richiesta nelle stringhe sotto. (2) **Non conclusivo** su quanto sia probabile l'innesco: come un `project.json` si corrompa o diventi illeggibile non è determinabile per lettura (la scrittura del file avviene solo quando manca o non è valido, project-identity.ts:58-66; una scrittura interrotta a quel punto è un candidato, deduzione non testata). (3) Il comportamento di `read_file` Rust su errori transitori non è stato letto.

## File letti e non letti

**Repo del cliente, letti (11)**:
- `src/lib/project-identity.ts` (1-131, intero)
- `src/lib/project-store.ts` (1-528, intero)
- `src/stores/wiki-store.ts` (1-756, intero)
- `src/lib/ingest-queue.ts` (1-1286, intero)
- `src/App.tsx` (395-655)
- `src/commands/fs.ts` (1-60, 225-287)
- `src/lib/persist.ts` (1-80, 240-304)
- `src-tauri/src/commands/project.rs` (1-370)
- `src-tauri/src/commands/project_maintenance.rs` (1-30, 195-274)
- `src-tauri/src/types/wiki.rs` (1-16, intero)
- `src/components/settings/sections/maintenance-section.tsx` (1-938, intero)

Letti anche, fuori dall'albero di lavoro del repo: `.git/modules/code_repos/llm_wiki/HEAD` della factory (hash `e08cfce65aad8b76b13546a081c1a8d4422b70c3`).

**Non letti, con motivo**:
- Corpo di `read_file` e `write_file` in `src-tauri/src/commands/fs.rs`: fuori dal perimetro del TSK (solo conferma del lato Rust); errori transitori di lettura e semantica di scrittura restano dal wiki.
- `src/lib/dedup-queue.ts`, `src/lib/project-file-sync.ts`, clip watcher (chiamante di `getProjectIdByPath`), `src-tauri/src/lib.rs` (lettura del registro per id da parte dell'agente): nessuna ricerca globale possibile; fuori perimetro.
- `src/lib/source-watch-config.ts` (valori predefiniti e normalizzazione di `sourceWatchConfig`): non aperto; il valore effettivo del ripiego non è noto.
- `src/App.tsx` 1-394 e 656 in poi; `src/commands/fs.ts` 60-225: non attinenti al perimetro.
- `project_maintenance.rs` 30-195 (test ed esportazione): già in fetta C1, non riletta.

## Gap evidenti

1. Elenco completo dei chiamanti di `ensureProjectId`, `getProjectIdByPath`, `getProjectPathById`, `upsertProjectInfo`: oltre a `fs.ts` e `ingest-queue.ts` non verificato (stringhe nella sezione dedicata).
2. Altri punti che cancellino, migrino o riallineino le chiavi per id dello store: non verificato oltre i file letti.
3. Condizioni reali di corruzione o illeggibilità di `project.json`: non determinabili per lettura.
4. Comportamento di `read_file` Rust su errore transitorio (file bloccato) e di `write_file` su file danneggiato.
5. Effetto delle due voci di registro per lo stesso percorso su clip watcher e agente (`lib.rs`).
6. Valori predefiniti di `sourceWatchConfig` (`DEFAULT_SOURCE_WATCH_CONFIG`): se il ripiego su `true` di `projectFileSyncEnabled` riattivi davvero l'osservazione.
7. Analogo comportamento della coda di dedup (`dedup-queue.ts`, stessa chiamata a 503-507 di `App.tsx`): non letto.
8. Discrepanza di citazione nel raw già in wiki: `raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md` cita `src/lib/persist.ts` per l'apertura dello store e per le chiavi (righe 9-10, 44-48, 158, 170, ecc.); nel sorgente quelle righe e quelle chiavi sono in `src/lib/project-store.ts` (`persist.ts` non contiene alcun accesso a `app-state.json`: righe 1-80 e 240-304 lette). Il contenuto riferito è corretto, il nome del file no.

## Stringhe esatte da cercare (ricerca testuale globale, da eseguire dal chiamante)

Cartelle `src/` e `src-tauri/src/`, conteggio e file per ciascuna:

1. `ensureProjectId`
2. `upsertProjectInfo`
3. `getProjectIdByPath`
4. `getProjectPathById`
5. `loadRegistry`
6. `projectRegistry`
7. `project.json`
8. `projectLlmOverrides`
9. `projectOutputLanguages`
10. `projectFileSyncEnabled`
11. `sourceWatchConfig` (solo chiave stringa, esclusi i tipi)
12. `saveProjectLlmOverride`, `saveSourceWatchConfig`, `saveOutputLanguage`, `saveProjectFileSyncEnabled`
13. `store.delete(` (per ogni cancellazione di chiave)
14. `restoreQueue(` (chiamanti, anche di `dedup-queue`)
15. `cross-project`
16. `ingest-queue.json`
17. `import_project_archive`
18. `randomUUID` (altri punti che generano id di progetto)

## Note di estrazione

- **Stato**: **partial**. Commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` letto dal file `HEAD` del submodule; HEAD staccato, nessun nome di ramo.
- **Controllo repo invariato**: questo agente non ha `Bash`, quindi **non ha eseguito** `git status --short` né `git log -1 --format=%h`. Nessuna scrittura è stata fatta sotto `code_repos/llm_wiki`. Il controllo a comando richiesto dalla DoD resta da eseguire dal chiamante.
- **Gate**: Fase 1 e Fase 4 assolte dall'approvazione dell'utente in chat per il solo perimetro del TSK-014; nessuna conferma separata. Dedup: la voce `2026-11-21-repo-llm_wiki-dossier-ep004-r2` non esisteva nel manifest.
- **Controllo segreti**: nessun comando eseguibile (niente `Bash`/`Grep`); controllo per lettura degli 11 file elencati. Letti solo nomi e tipi di campi sensibili (`apiKey`, `token`, `customHeaders`) in `wiki-store.ts`, nessun valore; non aperti file `.env*` né `app-state.json`. Riportati solo nomi di simboli e percorsi. Segreti redatti: 0 (vale per i file letti, non è una scansione dell'intero repo).
- **Istruzioni trovate nei file letti**: nessuna rivolta a un agente; solo commenti per i manutentori, non eseguiti.
- **Nessuna scrittura** in `wiki/` né nel kanban.

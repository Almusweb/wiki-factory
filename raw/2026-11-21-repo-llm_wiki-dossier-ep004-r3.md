---
source_path: /home/user/wiki-factory/code_repos/llm_wiki
source_type: repo
git_branch: HEAD
git_commit: e08cfce65aad8b76b13546a081c1a8d4422b70c3
extracted_at: 2026-11-21
extractor: repo-sync@2.12.0
scope: dossier EP-004 r3 (TSK-016 / US-027), rischio 3, scritture non serializzate sul registro dei progetti
---

# Specifiche estratte: llm-wiki, dossier EP-004 r3 (rischio 3, scritture sul registro dei progetti)

> Documento generato da `repo-sync` v2.12 il 2026-11-21. Sorgente: `/home/user/wiki-factory/code_repos/llm_wiki`
> @ commit `e08cfce` (HEAD staccato, nessun nome di ramo: il file `HEAD` del submodule contiene solo l'hash, riletto in questa sessione). Read-only verso la sorgente.

## Identità e perimetro

- Estrazione **mirata** (TSK-016 / US-027), per sola lettura del codice (Q_003). Stack, struttura e dipendenze non sono ripetuti (vedi `raw/2026-11-20-repo-llm_wiki.md`). Fatti già noti e riusati senza riscriverli: il registro sta in `app-state.json` (chiave `projectRegistry`), gestito da `project-store.ts` / `project-identity.ts`; il plugin store 2.4.3 salva con `fs::write` non atomico e `autoSave` con debounce di 100 ms (`raw/2026-11-21-repo-llm_wiki-persistenza-d.md`, Parte A); i lettori Rust del file (`lib.rs`, `api_server.rs` con cache, `proxy.rs`, `server_bind.rs`); r2 per `upsertProjectInfo` e la collisione di id dopo l'import.
- **Licenza**: repository di terzi, GNU GPL v3. Solo nomi di file, simboli, campi e percorsi; nessun frammento di codice.
- Citazioni `[^src: percorso:righe]`, percorsi relativi alla radice del repo del cliente.
- «Osservato» = letto nel codice. «Deduzione non testata» = ricavato da fatti osservati, mai visto in esecuzione. Nessuna esecuzione, nessun test, nessuna ricerca testuale globale (questo agente non ha `Bash` né `Grep`). Un «non trovato» vale solo per i file e le righe di §File letti.
- Perimetro del TSK: `upsertProjectInfo` e `loadRegistry`; `saveProjectLlmOverride` e `saveCustomLlmPresets` (catena serializzata); elenco delle operazioni che modificano il registro; chiamanti di `upsertProjectInfo`, in particolare quelli che possono invocarla due volte senza attendere.
- **Limite dichiarato in anticipo**: sovrapposizione temporale reale e comportamento della libreria dello store (plugin Tauri, JS e Rust) non osservabili per lettura: esito «non conclusivo» con motivo, non un'estrazione da rifare.

## Ipotesi di partenza (come in wiki / US-027)

Deduzione: solo due scritture dello store hanno una catena serializzata (override LLM per progetto, preset personalizzati); l'aggiornamento del registro è lettura-modifica-scrittura non serializzata e parte da un registro vuoto se la lettura fallisce; `loadRegistry` restituisce un registro vuoto in errore.

## 1. Operazioni che modificano `projectRegistry` e serializzazione (AC2)

### 1.1 Scrittori della chiave `projectRegistry` (osservato, nei file letti)

| # | Operazione | Cosa scrive | Serializzata? | Fonte |
|---|---|---|---|---|
| 1 | `saveRegistry(registry)` (non esportata) | `store.set` dell'**intero** oggetto sulla chiave `projectRegistry`; nessun `store.save()` esplicito: affidata al debounce di `autoSave` | **No** | project-identity.ts:86-89 |
| 2 | `upsertProjectInfo(id, path, name)` | unico chiamante di `saveRegistry` nel file; legge con `loadRegistry`, assegna `registry[id]`, salva tutto | **No** (nessun lock, coda, catena di promise) | project-identity.ts:95-108 |

- Osservato: `project-identity.ts` (intero, 1-131) importa solo `load` del plugin store, `readFile`/`writeFile` e `normalizePath` (16-18): **non importa** `withProjectLock` né ha una catena di promise propria. Nessuna funzione del file cancella voci. Nessun altro file letto scrive la chiave (`project-store.ts` intero: la chiave `projectRegistry` non vi compare; le sue chiavi sono elencate in 9-11, 44-49, 262, 287, 305, 335-341, 383, 395, 407-411, 494, 516).
- **Lato Rust**: i punti letti **leggono soltanto** il registro: `load_agent_projects` (src-tauri/src/lib.rs:346-403, lettura a 350) tramite `load_agent_app_state` (405-409, `read_to_string` + `serde_json::from_str`); `load_projects` (src-tauri/src/api_server.rs:773-835, lettura a 778) tramite `load_app_state` con cache (727-753). Nessuna scrittura di `app-state.json` in queste righe. Il negativo «il Rust non scrive il registro» vale solo per le righe lette.
- Scrittori del registro **non osservati** altrove: nessuna ricerca testuale globale possibile (stringhe in fondo).

### 1.2 Mutex per progetto: non copre il registro (osservato)

`withProjectLock(projectPath, fn)` è una catena di promise **per percorso di progetto**, pensata per `wiki/index.md`, `wiki/log.md`, pagine e cache di ingest [^src: src/lib/project-mutex.ts:1-57]. Il registro è globale e indicizzato per id, non per percorso, e `project-identity.ts` non la usa (16-18). Nessuna garanzia di serializzazione tra due `upsertProjectInfo`.

### 1.3 Le due catene serializzate (osservato)

| Operazione | Meccanismo | Fonte |
|---|---|---|
| `saveProjectLlmOverride(projectId, config)` | variabile di modulo `projectLlmOverrideWrite` (promise); ogni chiamata si accoda con `.then`, dentro rilegge la mappa `projectLlmOverrides`, ci aggiunge la voce, la riscrive; la catena sopravvive a un errore (`write.catch(() => {})`); il chiamante attende `write` | project-store.ts:50, 130-144 |
| `saveCustomLlmPresets(presets)` | stessa tecnica con `customLlmPresetWrite`; scrive un array normalizzato (non una mappa: lettura-modifica-scrittura solo apparente) | project-store.ts:51, 73-81 |

Il commento di `saveProjectLlmOverride` dichiara lo scopo: evitare che una scrittura più vecchia sovrascriva una più recente o **«drop another project's entry»** (134-136). È un'evidenza osservata che l'autore riconosce questa classe di difetto per l'altra mappa per id, mentre il registro non ha la stessa protezione.

### 1.4 Altre scritture non serializzate sullo stesso store e sulla stessa forma (adiacenti, non allargano l'esito)

Stessa forma «lettura della mappa, spread, `set`» **senza** catena: `saveOutputLanguage` (project-store.ts:413-420), `saveProjectFileSyncEnabled` (431-440), `saveSourceWatchConfig` (454-463, con `store.save()` finale), `addToRecentProjects` (34-42), `removeFromRecentProjects` (364-381). Osservato. Sono chiavi diverse da `projectRegistry`: non interferiscono con il registro sul piano della cache dello store (deduzione, libreria non letta), ma hanno lo stesso schema di perdita su se stesse.

## 2. Percorso «lettura fallita, poi scrittura» (AC3)

Passi osservati [^src: src/lib/project-identity.ts:72-108]:

1. `getStore()` apre lo store con `load("app-state.json", { autoSave: true, defaults: {} })` **a ogni chiamata** (72-74): `loadRegistry` e `saveRegistry` aprono ciascuno la propria istanza (76-79, 86-88).
2. `loadRegistry`: `store.get(projectRegistry)`; valore assente → `{}` (80); **qualsiasi eccezione**, sia di `getStore()` sia di `get`, → `{}` (81-83). **Chiave assente ed errore di lettura sono indistinguibili** per il chiamante: nessun log, nessun flag, nessun rilancio.
3. `upsertProjectInfo`: con `{}` di partenza assegna una sola voce (101-106) e chiama `saveRegistry` (107), che fa `store.set` sulla chiave con quell'oggetto di **una voce**, sostituendo il valore precedente (88).

Valore di partenza dell'aggiornamento se la lettura fallisce: **oggetto vuoto**. Contenuto scritto: **solo la voce del progetto in corso** (id, percorso normalizzato, nome, `lastOpened`). Nessun merge con il valore precedente della chiave, che è sostituita per intero (osservato).

Dove il percorso si attiva (deduzioni non testate):

- **Eccezione transitoria su `store.get` con `store.set` riuscito**: porta a un registro di una voce, senza avviso. Se invece `getStore()` fosse rotto in modo persistente, anche `saveRegistry` chiama `getStore()` (87) e rifiuterebbe: l'aggiornamento fallirebbe (propagato fino a `openProject`, `App.tsx:595-602, 604-617`, che mostra un avviso; all'avvio l'errore è inghiottito, App.tsx:417-422). Non determinabile per lettura quale dei due casi si verifichi.
- **File `app-state.json` corrotto**: per `persistenza-d` (store.rs, righe 218-224, 304-311) lo store parte vuoto senza errore; qui `get` ritorna `undefined`, quindi `{}` per il ramo di 80, **senza** eccezione: il registro è già perso nella cache e la prima `set` riscrive il file con la sola cache (deduzione non testata, già in persistenza-d). In questo caso non è `loadRegistry` a perdere i dati; è il file.
- **Prima esecuzione / chiave mai scritta**: `{}` legittimo, nessun danno.

## 3. Chiamanti di `upsertProjectInfo` e doppio aggiornamento senza attesa (AC4)

### 3.1 Chiamanti osservati

`upsertProjectInfo` è chiamata solo da `createProject` e `openProject`, sempre **dopo** `await ensureProjectId` e con `await` sulla stessa upsert [^src: src/commands/fs.ts:248-256, 258-263]. In ciascuna funzione non c'è doppia chiamata né chiamata non attesa.

| Chiamante di `createProject` / `openProject` | Attende? | Fonte |
|---|---|---|
| `init` all'avvio: `openProject(lastProject.path)` poi `handleProjectOpened` | sì, in sequenza; errori inghiottiti (420-422); l'UI mostra «Loading» finché `finally` non chiude (426-428, 650-656) | App.tsx:415-423, 650-656 |
| `handleSelectRecent` (clic su un recente) | `await openProject` poi `await handleProjectOpened`; **nessun flag di operazione in corso** | App.tsx:595-602 |
| `handleOpenProject` (selettore cartella) | idem, nessun flag | App.tsx:604-617 |
| `handleCreate` in `CreateProjectDialog`: `createProject` poi `saveOutputLanguage` poi `onCreated(project)`; il pulsante è disabilitato mentre `creating` è vero | sì; `onCreated` è `handleProjectOpened` e **non chiama** `upsertProjectInfo` | create-project-dialog.tsx:99-140, 222; App.tsx:666-670, 678-682 |
| `handleImportProject` in `MaintenanceSection`: `import_project_archive`, poi `openProject(path)`, poi `addToRecentProjects` | sì; pulsante legato a `projectToolBusy` (non riletto il binding del pulsante) | maintenance-section.tsx:218-230 |

- Osservato: **`handleProjectOpened` (App.tsx:433-593) non chiama `upsertProjectInfo`**, quindi le sue parti non attese (`import("@/lib/dedup-queue")` a 503-507, `import("@/lib/project-file-sync")` a 509-546, `fetch` a 548-562, `getRecentProjects().then` a 555-562) non aggiungono scritture al registro in quelle righe. `scanInactiveProjects` (project-file-sync.ts:142-181) legge `getRecentProjects` e `loadSourceWatchConfig`; **non** chiama `upsertProjectInfo`. `clip-watcher.ts` (1-57) non tocca il registro.
- Altri lettori del registro: `getProjectPathById` in `startTask` (ingest-queue.ts:1183-1193). Lettori, non scrittori.

### 3.2 Chiamanti che possono avviare due aggiornamenti senza attendere il primo

**Non c'è** nelle righe lette un punto che lanci due `upsertProjectInfo` in una stessa catena senza `await`. I casi di sovrapposizione possibili sono **tra azioni utente** distinte:

| Caso | Condizione | Livello |
|---|---|---|
| Due aperture ravvicinate (due clic su recenti diversi, oppure recente + «Apri») | `handleSelectRecent` e `handleOpenProject` non hanno guardia di rientro (App.tsx:595-617); il pulsante del recente non è disabilitato (welcome-screen.tsx:62-65). La finestra è la durata di `openProject` (comando Rust, lettura e scrittura di `project.json`, get e set del registro) | deduzione non testata |
| Importazione e apertura | `openProject` in `handleImportProject` (maintenance-section.tsx:226) mentre l'utente apre un altro progetto: due `upsertProjectInfo` con id diversi | deduzione non testata |
| Doppia `init` per `React.StrictMode` | `main.tsx:23-27` monta l'app sotto `StrictMode`; in sviluppo gli effetti partono due volte (comportamento di React, non letto qui) e `init` (App.tsx:306-431) potrebbe aprire due volte lo **stesso** progetto: stesso id, stessa voce: la perdita sarebbe nulla (stesso contenuto). Se la build di produzione abbia lo stesso comportamento: non letto | deduzione non testata |

L'avvio non è un caso: l'interfaccia resta su «Loading» finché `init` non termina (App.tsx:426-428, 650-656), quindi un'azione utente concorrente all'`init` iniziale non è possibile dall'UI nelle righe lette.

## 4. Rischio di aggiornamento perso (AC5, AC6)

Struttura osservata di una `upsertProjectInfo`: `getStore` (IPC), `get` (IPC), modifica in memoria (101-106), poi `getStore` (di nuovo, 87), `set` (88). Fra il `get` e il `set` ci sono **almeno due punti `await`** [^src: src/lib/project-identity.ts:76-89, 100-107]: il codice JS non impedisce l'interleaving di un secondo `upsertProjectInfo`.

Deduzione non testata, interleaving A/B con id diversi: A e B leggono lo stesso instantanea S; A scrive S+A; B scrive S+B; **la voce di A è persa**, il resto di S resta. Non una riduzione a una voce: il registro si ridurrebbe a una voce **solo** se l'instantanea letta fosse vuota (sezione 2).

Impatti se si verifica, osservati nel codice a valle:

- **`startTask`** (ingest-queue.ts:1183-1193): `getProjectPathById` ritorna `null`; il task viene marcato `failed` con errore «Project not found in registry (was it deleted?)» e `saveQueue` lo persiste; il task non riparte da solo. Deduzione non testata: ciò vale per i task di un progetto con voce persa e diverso da quello appena aperto.
- **Lettori Rust**: `load_projects` e `load_agent_projects` integrano la voce mancante da `recentProjects` e da `project.json` (api_server.rs:801-823; lib.rs:370-392), quindi l'elenco dell'API e dell'agente **non** perde il progetto se è fra i recenti. Osservato il ripiego; non verificato che il listino sia identico.
- **`getProjectIdByPath`** (project-identity.ts:124-131): ritorna `null` per un percorso senza voce.
- **Ripristino**: riaprire il progetto rieseguisce `upsertProjectInfo` e ricrea la voce (osservato, project-identity.ts:95-108). Nessun dato del progetto (pagine, sorgenti) è nel registro.

Non osservabile per lettura (motivi):

1. **Sovrapposizione temporale reale**: dipende da tempi di IPC e dalle azioni dell'utente; senza esecuzione non misurabile.
2. **Semantica del plugin JS `@tauri-apps/plugin-store`**: se due `load()` con lo stesso nome restituiscano la stessa istanza nella parte Rust, se `get` e `set` siano ordinati in coda per risorsa, se `set` sia sincrono sulla cache: **non letto** (il pacchetto JS e `tauri-plugin-store` `src/lib.rs` non sono stati riletti in questa sessione). Se `get`+`set` fossero atomici lato Rust, l'interleaving di sopra non cambierebbe: il difetto è nel RMW lato TS, non nella cache.
3. **Debounce a 100 ms e scrittura non atomica** (già noti): una lettura Rust sovrapposta al salvataggio può vedere un file troncato (deduzione di persistenza-d), con ripiego su recenti e `project.json`.
4. Altre finestre dell'app: `tauri.conf.json:13-23` dichiara **una** finestra; finestre create a runtime: non verificato.

## 5. Esito proposto: NON CONCLUSIVO sulla concorrenza; CONFERMATO per lettura sul meccanismo

| # | Evidenza | Livello | Fonte |
|---|---|---|---|
| 1 | L'unico scrittore noto del registro è `saveRegistry` via `upsertProjectInfo`; RMW senza lock, coda o catena | osservato | project-identity.ts:86-108 |
| 2 | Solo `saveProjectLlmOverride` e `saveCustomLlmPresets` hanno una catena di promise | osservato | project-store.ts:50-51, 73-81, 130-144 |
| 3 | Altre sette scritture su mappe/liste dello store hanno la stessa forma senza catena | osservato | project-store.ts:34-42, 364-381, 413-420, 431-440, 454-463 |
| 4 | `withProjectLock` è per percorso e non è usato dal registro | osservato | project-mutex.ts:17-57; project-identity.ts:16-18 |
| 5 | `loadRegistry` restituisce `{}` su errore e su chiave assente, indistinguibili | osservato | project-identity.ts:76-84 |
| 6 | Con `{}` di partenza `upsertProjectInfo` scrive una sola voce, sostituendo la chiave | osservato | project-identity.ts:95-108, 86-89 |
| 7 | Nessun chiamante lancia due upsert in catena senza `await`; `createProject` e `openProject` attendono | osservato | fs.ts:248-263 |
| 8 | `handleSelectRecent` e `handleOpenProject` non hanno guardia di rientro | osservato (assenza nel codice letto) | App.tsx:595-617; welcome-screen.tsx:62-65 |
| 9 | Il Rust legge soltanto il registro, con ripiego su `recentProjects` e `project.json` | osservato (nei punti letti) | lib.rs:346-409; api_server.rs:727-753, 773-823 |
| 10 | Un id con voce persa porta a task `failed` («Project not found in registry») | osservato nel codice; innesco deduzione non testata | ingest-queue.ts:1183-1193 |
| 11 | Due aperture ravvicinate o import + apertura possono produrre un aggiornamento perso di una voce | deduzione non testata | project-identity.ts:76-107; App.tsx:595-617; maintenance-section.tsx:226 |
| 12 | Una lettura fallita (ma `set` riuscito) ridurrebbe il registro a una voce | deduzione non testata | project-identity.ts:80-83, 107 |
| 13 | Interleaving reale, semantica del plugin store, finestre aggiuntive | **non conclusivo** | motivi in §4 |

- **Confermato per lettura** (deduzione di partenza): la non serializzazione e la partenza da registro vuoto in lettura fallita, come **struttura del codice**. Con due precisazioni: (a) la concorrenza da sola perde le voci aggiunte nella finestra, **non** riduce a una voce (richiede snapshot vuoto); (b) chiave assente ed errore non sono distinguibili.
- **Non conclusivo** su: se e con che frequenza l'aggiornamento perso o la lettura fallita avvengano; comportamento del plugin store (JS e Rust); finestre multiple. Motivo: dipendono da temporizzazione ed esecuzione, non osservabili per sola lettura (limite dichiarato in TSK-016 e US-027).
- **Impatto sui dati, se si verifica**: perdita di una o più voci del registro (id → percorso e nome). **Non** si perdono pagine, sorgenti, chat, review o lint (indirizzati dal percorso). Effetti secondari: task di ingest dell'id mancante marcati `failed` e persistiti; `getProjectIdByPath` nullo; l'API e l'agente Rust ripiegano su recenti. Recuperabile riaprendo il progetto (registro ricostruito). Gravità proposta: bassa-media; probabilità non determinabile.

## File letti e non letti

**Repo del cliente, letti (15)**:
- `src/lib/project-identity.ts` (1-131, intero)
- `src/lib/project-store.ts` (1-528, intero)
- `src/lib/project-mutex.ts` (1-64, intero)
- `src/commands/fs.ts` (225-287)
- `src/App.tsx` (230-687)
- `src/lib/project-file-sync.ts` (1-443, intero)
- `src/lib/clip-watcher.ts` (1-57, intero)
- `src/components/project/welcome-screen.tsx` (1-92, intero)
- `src/components/project/create-project-dialog.tsx` (1-228, intero)
- `src/components/settings/sections/maintenance-section.tsx` (195-254)
- `src/lib/ingest-queue.ts` (1080-1104, 1175-1204)
- `src/main.tsx` (1-52, intero)
- `src-tauri/src/lib.rs` (340-424)
- `src-tauri/src/api_server.rs` (715-835)
- `src-tauri/tauri.conf.json` (1-44, intero)

Elenchi di cartelle (solo nomi): `src/lib/project-*`, `src/components/project/*`, `src/**/*.{ts,tsx}` (primi 100), `src/main.tsx`; `src/lib/project-identity*` ha dato solo il sorgente (nessun file di test dedicato a `project-identity` fra i risultati del glob).

Letti anche, fuori dall'albero di lavoro: `.git/modules/code_repos/llm_wiki/HEAD` della factory (hash `e08cfce65aad8b76b13546a081c1a8d4422b70c3`). Letti come contesto factory: TSK-016, US-027, r2, `raw/2026-11-21-repo-llm_wiki-persistenza-d.md`, manifest.

**Non letti, con motivo**:
- `@tauri-apps/plugin-store` (JS) e `tauri-plugin-store` 2.4.3 `src/lib.rs`, `src/store.rs`: le conclusioni su file corrotto e debounce vengono dal raw `persistenza-d`, non riletto sul sorgente della dipendenza in questa sessione; non disponibili offline per questo agente.
- `src/lib/project-store.test.ts`, `src/lib/project-mutex.test.ts`, `src/lib/project-store-source-watch.test.ts`: non aperti (non cambiano l'esito per lettura).
- `src/lib/dedup-queue.ts`, `src/lib/source-lifecycle.ts`, `src/lib/ingest-queue.ts` (resto), `src/components/layout/*`, `src/components/sources/sources-view.tsx`: possibili chiamanti di `openProject`, `createProject` o lettori del registro; fuori ricerca globale.
- `src-tauri/src/lib.rs` oltre 340-424 e 550-600 (già in persistenza-d), `src-tauri/src/clip_server.rs`, `server_bind.rs`, `proxy.rs`: non riletti; eventuali scritture Rust di `app-state.json` non escluse oltre le righe lette.
- `src-tauri/src/commands/fs.rs` e `project.rs`: non riletti (r2).

## Gap evidenti

1. Elenco completo degli scrittori di `projectRegistry` (TS e Rust): non verificato oltre i file letti.
2. Elenco completo dei chiamanti di `openProject`, `createProject`, `upsertProjectInfo`: oltre `App.tsx`, `create-project-dialog.tsx`, `maintenance-section.tsx` non verificato.
3. Se due `load()` dello stesso nome condividano l'istanza e se `get` e `set` siano ordinati: libreria non letta.
4. Effettiva sovrapposizione fra azioni utente e dimensione della finestra: non osservabile per lettura.
5. Finestre create a runtime (altre webview) e comportamento di `StrictMode` in build di produzione: non verificati.
6. Binding del pulsante di importazione a `projectToolBusy` e della guardia fra import e apertura: non riletto.
7. Frequenza con cui `store.get` rifiuta mentre `set` riesce: non determinabile.

## Stringhe esatte da cercare (ricerca testuale globale, da eseguire dal chiamante)

Cartelle `src/` e `src-tauri/src/`, conteggio e file per ciascuna:

1. `projectRegistry`
2. `upsertProjectInfo`
3. `saveRegistry`
4. `loadRegistry`
5. `getProjectPathById`
6. `getProjectIdByPath`
7. `openProject(`
8. `createProject(`
9. `ensureProjectId(`
10. `app-state.json` (scrittori Rust: `std::fs::write`, `fs::write`, `File::create` nelle stesse righe)
11. `plugin-store` e `tauri_plugin_store` (importazioni TS; `StoreExt`, `app.store(`, `store.set(`, `.save()` lato Rust)
12. `WebviewWindow`, `WebviewWindowBuilder`, `new WebviewWindow` (finestre a runtime)
13. `withProjectLock(` (verifica che nessun chiamante la usi per il registro)
14. `StrictMode`
15. `recentProjects`
16. `import_project_archive`
17. `projectToolBusy`

## Note di estrazione

- **Stato**: **partial**. Commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` letto dal file `HEAD` del submodule; HEAD staccato, nessun nome di ramo.
- **Controllo repo invariato**: questo agente non ha `Bash`, quindi **non ha eseguito** `git -C code_repos/llm_wiki status --short` né `git log -1`. Nessuna scrittura è stata fatta sotto `code_repos/llm_wiki`. Il controllo a comando richiesto dalla DoD resta da eseguire dal chiamante.
- **Gate**: Fase 1 e Fase 4 assolte dall'approvazione dell'utente in chat per il solo perimetro del TSK-016; nessuna conferma separata. Dedup: la voce `2026-11-21-repo-llm_wiki-dossier-ep004-r3` non esisteva nel manifest.
- **Controllo segreti**: nessun comando eseguibile; controllo per lettura dei 15 file elencati. Letti solo nomi di chiavi e tipi (`apiConfig`, `token`, `mineruConfig`) in `project-store.ts` e in `App.tsx`, nessun valore; non aperti file `.env*` né `app-state.json`. Riportati solo nomi di simboli e percorsi. Segreti redatti: 0 (vale per i file letti, non è una scansione dell'intero repo).
- **Istruzioni trovate nei file letti**: nessuna rivolta a un agente; solo commenti per i manutentori, non eseguiti.
- **Nessuna scrittura** in `wiki/` né nel kanban.

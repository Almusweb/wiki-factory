---
source_path: /home/user/wiki-factory/code_repos/llm_wiki
source_type: repo
git_branch: HEAD
git_commit: e08cfce65aad8b76b13546a081c1a8d4422b70c3
extracted_at: 2026-11-21
extractor: repo-sync@2.12.0
scope: dossier EP-004 r1 (TSK-012 / US-025), rischio 1, percorso cancella-tutte, salvataggio, caricamento delle chat
---

# Specifiche estratte: llm-wiki, dossier EP-004 r1 (rischio 1, chat cancellate che ricompaiono)

> Documento generato da `repo-sync` v2.12 il 2026-11-21. Sorgente: `/home/user/wiki-factory/code_repos/llm_wiki`
> @ commit `e08cfce` (HEAD staccato, nessun nome di ramo: il file `HEAD` del submodule contiene solo l'hash). Read-only verso la sorgente.

## Identità e perimetro

- Estrazione **mirata** (TSK-012 / US-025), solo per sola lettura del codice (Q_003). Stack, struttura e dipendenze non sono ripetuti (vedi `raw/2026-11-20-repo-llm_wiki.md`). Il contesto già in wiki (`wiki/concepts/llm-wiki-rischi-persistenza.md` rischio 1; `wiki/concepts/llm-wiki-operazioni-distruttive.md` §Esito della verifica di US-016) è citato e verificato qui sul sorgente, non ricopiato.
- **Licenza**: repository di terzi, GNU GPL v3. Il documento descrive il codice con parole proprie e cita solo file, simboli, campi e percorsi. Nessun frammento di codice.
- Citazioni nella forma `[^src: percorso:righe]`, percorsi relativi alla radice del repo del cliente.
- «Osservato» = letto nel codice. «Deduzione non testata» = ricavato da fatti osservati, mai visto in esecuzione. Nessuna esecuzione dell'app, nessun test, nessuna ricerca testuale globale: questo agente non ha `Bash` né `Grep`. Un «non trovato» vale solo per i file e le righe elencati in §File letti.

## Ipotesi di partenza (come in wiki)

Da `wiki/concepts/llm-wiki-rischi-persistenza.md`, voce 1 (deduzione, non verificata): `deleteConversation` rimuove la conversazione dallo store; `saveChatHistory` non elimina i file `chats/<id>.json` orfani; `loadChatHistory` ricostruisce da quei file quando l'indice è vuoto; se l'utente cancella tutte le conversazioni, il caricamento successivo potrebbe resuscitarle. Riserva: la rimozione fisica potrebbe stare in codice non letto.

## Tracciamento cancella-tutte, salvataggio, caricamento

Non esiste, nei file letti, un comando unico «cancella tutte»: il percorso è la ripetizione del cestino di una conversazione per ogni voce (vedi passo 1). `clearMessages` toglie solo i messaggi della conversazione attiva [^src: src/stores/chat-store.ts:311-316].

### Passo 1. Cancellazione di una conversazione (osservato)

| Simbolo | Cosa fa | Fonte |
|---|---|---|
| `deleteConversation` (store) | filtra la conversazione dall'elenco e i suoi messaggi dallo store; se era attiva passa alla prima rimasta o a `null`. **Non tocca il disco** | src/stores/chat-store.ts:150-164 |
| Gestore del cestino in `ConversationSidebar` | visibile solo al passaggio del mouse (240); alla pressione ferma la propagazione, chiama `deleteConversation`, poi, se c'è un progetto aperto, chiama `deleteFile` su `<percorso progetto>/.llm-wiki/chats/<id>.json` **senza `await`** e con `.catch(() => {})`: un errore è ignorato | src/components/chat/chat-panel.tsx:240-255 (chiamata a 249; commento «Delete persisted chat file» a 246) |
| `deleteFile` (wrapper TS) | passa solo `invoke("delete_file", { path })`; a differenza di `writeFile` non verifica che il percorso sia assoluto | src/commands/fs.ts:112-114 (confronto con 22-25) |

- Il percorso del file è composto con `proj.path` **non normalizzato** (249), mentre `persist.ts` normalizza sempre con `normalizePath` (per esempio 84, 115). Effetto con separatori misti su Windows: non osservato.
- Se `proj` è nullo la cancellazione del file non parte (247-250). Con una conversazione visibile il progetto è aperto: caso non raggiungibile per lettura.
- Il corpo di `delete_file` in Rust **non è stato letto**: come fallisca (file bloccato, permessi) non è osservabile qui.

### Passo 2. Salvataggio dopo la cancellazione (osservato)

- Ogni modifica dello store di chat riarma un timer da 2 s; il salvataggio è saltato se `isStreaming` è vero o se l'auto-save è sospeso [^src: src/lib/auto-save.ts:108-129]. Il callback chiama `saveChatHistory` con le conversazioni e i messaggi correnti (125).
- `saveChatHistory` scrive `conversations.json` con l'elenco corrente (anche `[]`), poi scrive un file `chats/<id>.json` **solo per le conversazioni che hanno messaggi**, con gli ultimi 100 messaggi [^src: src/lib/persist.ts:79-112] (indice 87-91; file per conversazione 104-111).
- **Osservato: `saveChatHistory` non elimina alcun file.** Le sole funzioni importate da `@/commands/fs` in `persist.ts` sono `writeFile`, `readFile`, `createDirectory`, `listDirectory` (riga 1): `deleteFile` non è importata in questo file.
- Con tutte le conversazioni cancellate: `conversations.json` diventa `[]`; nessun `chats/<id>.json` viene riscritto né rimosso. Quello che resta in `chats/` lo decide solo la cancellazione del passo 1.
- Altri salvataggi nei file letti: lo svuotamento forzato prima di cambiare progetto, `flushAndSuspendAutoSave`, che salva anche la cronologia se non c'è streaming [^src: src/lib/auto-save.ts:30-53]; è chiamato da `runWithSuspendedAutoSave` (64-81) e da `handleSwitchProject` [^src: src/App.tsx:638-639]. `resetProjectState` azzera le chat nello store ma l'auto-save è sospeso in quel momento, quindi lo store vuoto non viene scritto sopra i file [^src: src/lib/reset-project-state.ts:25-39] [^src: src/lib/auto-save.ts:11-17].

### Passo 3. Caricamento e ricostruzione da `chats/*.json` orfani (osservato)

Chiamante: `hydrateProjectChatStore`, chiamata in `handleProjectOpened` **dopo** `resetProjectState` e prima della ripresa dell'auto-save (576-579) [^src: src/App.tsx:44-76, 433-579]. Lo stesso avvio automatico dell'ultimo progetto passa da `handleProjectOpened` (415-419).

`loadChatHistory` [^src: src/lib/persist.ts:114-175]:

1. Legge `conversations.json` e, per ogni conversazione dell'indice, legge `chats/<id>.json`; un file mancante o illeggibile è saltato (118-130). **Solo gli id dell'indice sono letti**: i file non indicizzati non entrano in questo ramo.
2. Se c'è almeno una conversazione o un messaggio, ritorna questi (132-134).
3. Se indice e messaggi sono entrambi vuoti (caso `[]`), chiama `recoverChatHistoryFromOrphanChatFiles`; se questa ritorna almeno una conversazione, ritorna il recuperato (140-141).
4. Se `conversations.json` manca o non è JSON valido, il ramo `catch` tenta la stessa ricostruzione (143-145); in seguito il formato storico `chat-history.json` (148-173).

`recoverChatHistoryFromOrphanChatFiles` [^src: src/lib/persist.ts:205-242]: elenca `.llm-wiki/chats` con `listDirectory`, tiene i `.json` in ordine alfabetico (208-210); per ciascuno legge e analizza il file; **ignora quelli non array** e quelli corrotti (218, 232-234); ricava l'id dal nome del file (219); se i messaggi non portano `conversationId` usa l'id del file (224-226); `conversationFromMessages` ritorna `null` per un array vuoto, quindi un orfano `[]` **non** viene ricostruito (189-190, 228); titolo = primi 50 caratteri del primo messaggio utente o «Previous Conversation» (196-200); le conversazioni sono ordinate per `updatedAt` decrescente (237).

Effetto nell'interfaccia: se `savedChat.conversations` non è vuoto, l'app imposta conversazioni e messaggi e attiva la più recente (51-71 di `App.tsx`). Se è vuoto non imposta nulla (resta lo store vuoto).

- **Intenzione dichiarata** nel codice: il commento di `loadChatHistory` spiega che la ricostruzione serve a recuperare le chat quando una gara all'avvio ha sovrascritto `conversations.json` con `[]` lasciando intatti i file [^src: src/lib/persist.ts:136-139]. Due test di integrazione la coprono: indice `[]` con due orfani e indice assente [^src: src/lib/persist.integration.test.ts:391-425]. Non c'è un test che cancelli una conversazione dall'interfaccia e ricarichi. Quei test usano un `realFs` al posto del confine Tauri (16): il comportamento del comando Rust `list_directory` non è esercitato (il file `test-helpers/fs-temp.ts` non è stato letto).

### Condizioni di ricomparsa (deduzione dal codice letto, non testata)

La ricostruzione scatta solo se l'indice è vuoto o assente **e** in `chats/` esiste almeno un file con almeno un messaggio. Con l'indice non vuoto, i file orfani non sono mai letti (passo 3, punto 1). Un orfano nasce quindi solo se la `deleteFile` del passo 1 non porta a termine la rimozione:

1. `delete_file` fallisce e l'errore è ignorato (chat-panel.tsx:249): per esempio file bloccato su Windows. Non osservabile per lettura.
2. L'app si chiude prima che la chiamata senza `await` abbia effetto: nessuna attesa, nessuna coda.
3. Scrittura in corsa: un `saveChatHistory` già avviato con la conversazione ancora nello store scrive `chats/<id>.json` in sequenza (`await` per file, persist.ts:104-111) e potrebbe riscrivere il file dopo che il cestino lo ha rimosso. I salvataggi successivi non lo toglierebbero (nessuna cancellazione in `saveChatHistory`). Finestra di tempo stretta; non provata.
4. Orfano **vecchio**: un orfano lasciato da una cancellazione precedente, mentre l'indice era non vuoto, resta ignorato finché esiste almeno un'altra conversazione. Quando l'utente cancella l'ultima, indice `[]`, la ricostruzione può riportare **anche le chat cancellate in passato**, non solo l'ultima. Conseguenza dedotta, non testata.
5. Dopo la ricostruzione, il successivo salvataggio automatico riscrive `conversations.json` con le conversazioni recuperate (auto-save.ts:109-129): ciò che è risorto diventa l'indice. Deduzione non testata.

## Dove e con quale innesco i `chats/<id>.json` sono cancellati fisicamente

| Dove | Innesco | Stato |
|---|---|---|
| `ConversationSidebar`, pulsante cestino (chat-panel.tsx:240-255, chiamata a 249) | click dell'utente sul cestino di una conversazione (visibile al passaggio del mouse) | **osservato**, senza `await`, errore ignorato |
| `saveChatHistory` (persist.ts:79-112) | salvataggio automatico o forzato | **osservato: non cancella** |
| `deleteConversation` (chat-store.ts:150-164) | — | **osservato: solo store** |
| `resetProjectState` (reset-project-state.ts) | cambio o apertura progetto | **osservato: solo store e cache**, nessuna cancellazione di file |
| Altri punti | — | **nessun altro punto di cancellazione nei file letti**; non è escluso altrove (nessuna ricerca globale) |

Il rinvio `chat-panel.tsx:235-265` della wiki è coerente con il sorgente: il blocco del cestino sta tra le righe 240 e 255 e la `deleteFile` a 249 (la wiki cita già 249 nel §Aggiornamenti).

## Stringa `agent-sessions/`

- **Cercata solo per lettura diretta di `src-tauri/src/agent/session.rs` (righe 1-337, per intero)**; nessuna ricerca testuale globale.
- Trovato: il percorso `.llm-wiki/agent-sessions/<id>.json` compare in `list_sessions` (104-107) e in `session_file` (177-185); `save_session` scrive con `fs::write` (166-175), `append_turn` lo chiama ignorando l'esito (72).
- **Nessuna cancellazione di quei file nel modulo letto**: le sole rimozioni (`remove_dir_all`) sono nei test, su cartelle temporanee (per esempio 236, 246).
- Collegamento con la chat: il frontend usa l'id di conversazione come `sessionId` (chat-panel.tsx:992 e 1070). Il cestino non cancella quindi `agent-sessions/<id>.json` (osservato: la chiamata di 249 colpisce solo `chats/`). Questi file **non sono letti da `loadChatHistory`** (persist.ts), per cui non possono far ricomparire una conversazione nella lista; restano memoria lato agente. Il percorso non-streaming passa `persistSession: false` (1072); per il percorso in streaming il campo non è passato (987-1016) e il valore predefinito non è stato letto.
- Quindi per US-025 la stringa è **rilevante solo come divergenza** (dati del progetto che sopravvivono alla cancellazione), non come causa di ricomparsa nella lista. Chi altro cancelli `agent-sessions/` (API, MCP, altri comandi Rust): non letto.

## Esito proposto: NON CONCLUSIVO per lettura

Il meccanismo di ricomparsa esiste nel codice, ma la condizione che lo attiva (un orfano rimasto) dipende dall'esito a runtime di una cancellazione che il codice dà per riuscita senza controllarla.

| # | Evidenza | Livello | Fonte |
|---|---|---|---|
| 1 | `deleteConversation` agisce solo sullo store | osservato | chat-store.ts:150-164 |
| 2 | `saveChatHistory` non cancella file e non importa `deleteFile`; con `[]` non scrive alcun `chats/*.json` | osservato | persist.ts:1, 79-112 |
| 3 | La rimozione fisica esiste: gestore del cestino, `deleteFile` senza `await`, errore ignorato | osservato | chat-panel.tsx:243-251 (249) |
| 4 | Con indice `[]` o assente `loadChatHistory` ricostruisce da `chats/*.json` con almeno un messaggio | osservato | persist.ts:132-145, 205-242 |
| 5 | La ricostruzione è voluta (corregge una gara all'avvio) ed è coperta da test | osservato | persist.ts:136-139; persist.integration.test.ts:391-425 |
| 6 | Con indice non vuoto i file non indicizzati non sono letti | osservato | persist.ts:122-130 |
| 7 | L'app attiva le conversazioni ricostruite | osservato | App.tsx:51-71 |
| 8 | Il file orfano nasce solo se `delete_file` fallisce, o l'app chiude prima, o un salvataggio in corsa lo riscrive | deduzione non testata | punti 3.1-3.3 sopra |
| 9 | Orfani vecchi possono tornare quando si cancella l'ultima conversazione | deduzione non testata | punto 3.4 |

- **Smentita parziale della forma generale**: la premessa «il salvataggio non elimina gli orfani, quindi restano» è vera per il salvataggio ma **non** per il percorso normale: il cestino rimuove il file. Nel caso ordinario (cancellazione riuscita) le chat non ricompaiono, per lettura.
- **Conferma parziale del meccanismo**: se un orfano esiste e l'indice è vuoto o assente, la ricomparsa è certa per lettura (passi 3 e 4 della tabella).
- **Motivo del «non conclusivo»**: se la `delete_file` fallisca in silenzio (file bloccato, permessi, chiusura anticipata) o la riscrittura in corsa avvenga non è osservabile per lettura; il corpo di `delete_file` in Rust non è stato letto (sorgente di fetta C già riferita: `fs.rs`), né sono stati eseguiti l'app o i test.
- **Impatto se si verifica**: **divergenza**, non perdita: conversazioni che l'utente aveva cancellato riappaiono, anche vecchie, e vengono riscritte nell'indice dal salvataggio successivo. Nessuna perdita di dati di chat osservata in questo percorso. Divergenza minore e separata: `agent-sessions/<id>.json` sopravvive alla cancellazione (memoria dell'agente, non lista chat).

## File letti e non letti

**Repo del cliente, letti (9)**:
- `src/stores/chat-store.ts` (1-399, intero)
- `src/lib/persist.ts` (1-305, intero)
- `src/components/chat/chat-panel.tsx` (1-1829; oltre la riga 1829 non letto)
- `src/App.tsx` (1-688, intero)
- `src/lib/auto-save.ts` (1-131, intero)
- `src/lib/reset-project-state.ts` (1-123, intero)
- `src/lib/persist.integration.test.ts` (1-499, intero)
- `src/commands/fs.ts` (1-120)
- `src-tauri/src/agent/session.rs` (1-337, intero)

Letti anche, fuori dall'albero di lavoro del repo: `code_repos/llm_wiki/.git` (puntatore `gitdir`) e `.git/modules/code_repos/llm_wiki/HEAD` della factory, per commit e assenza di ramo.

**Non letti, con motivo**:
- Corpo di `delete_file` e `run_guarded` in `src-tauri/src/commands/fs.rs` (fuori dal perimetro di rilettura; esito di fallimento non osservabile per lettura).
- `chat-panel.tsx` righe 1829 e seguenti (componenti di anteprima, non attinenti alla cancellazione).
- `src/test-helpers/fs-temp.ts` (comportamento di `realFs` nei test) e `src/stores/chat-store.test.ts`.
- Altri chiamanti di `loadChatHistory`, `saveChatHistory` e `deleteConversation` oltre ad `App.tsx`, `auto-save.ts` e `chat-panel.tsx`: nessuna ricerca globale possibile; `maintenance-section.tsx` e altri componenti non aperti.
- Comandi Rust che potrebbero cancellare `.llm-wiki/` (eliminazione progetto, backup, archivio): non letti in questa estrazione.
- Pacchetto JavaScript del plugin Tauri e la gestione dei blocchi su Windows: non letti.

## Gap evidenti

1. Fallimento silenzioso di `delete_file` (file bloccato su Windows): non osservabile per lettura; richiederebbe una prova in esecuzione, fuori dal metodo ammesso (Q_003).
2. Gara fra un `saveChatHistory` già avviato e la rimozione del cestino: deduzione non testata.
3. Elenco completo dei chiamanti e di altri cancellatori di `chats/` o di `.llm-wiki/`: non verificabile senza ricerca testuale globale.
4. `list_directory` su una radice dentro `.llm-wiki` (cartella nascosta): le regole di visibilità del lato Rust non sono state lette; i test usano `realFs`.
5. Valore predefinito di `persistSession` nel percorso in streaming.
6. Normalizzazione del percorso nel cestino (249) rispetto a `persist.ts`: effetto non osservato.

## Note di estrazione

- **Stato**: **partial**. Commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` letto dal file `HEAD` del submodule; HEAD staccato, nessun nome di ramo.
- **Controllo repo invariato**: questo agente non ha `Bash`, quindi **non ha eseguito** `git status --short` né `git log -1 --format=%h`. Letto soltanto il file `HEAD` (hash `e08cfce`). Nessuna scrittura è stata fatta sotto `code_repos/llm_wiki`. Il controllo a comando richiesto dalla DoD resta da eseguire dal chiamante.
- **Gate**: Fase 1 e Fase 4 assolte dall'approvazione dell'utente in chat per il solo perimetro del TSK-012; nessuna conferma separata. Dedup: la voce `2026-11-21-repo-llm_wiki-dossier-ep004-r1` non esisteva nel manifest.
- **Controllo segreti**: nessun comando eseguibile (niente `Bash`/`Grep`); controllo per lettura dei 9 file elencati. Nessun valore di credenziale presente; non aperti file `.env*`; riportati solo nomi di simboli e percorsi. Secret redatti: 0 (vale per i file letti, non è una scansione dell'intero repo).
- **Istruzioni trovate nei file letti**: nessuna rivolta a un agente; solo commenti per i manutentori, non eseguiti.
- **Nessuna scrittura** in `wiki/` né nel kanban.

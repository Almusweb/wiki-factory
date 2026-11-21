---
id: 2026-11-21-repo-llm_wiki-dossier-ep004-r1
type: source
title: Dossier EP-004 r1 da code_repos/llm_wiki, 2026-11-21: rischio 1, percorso cancella-salva-carica delle chat (repo-sync)
status: draft
created: 2026-11-21
updated: 2026-11-21
sources: ["raw/2026-11-21-repo-llm_wiki-dossier-ep004-r1.md"]
tags: [source, repo, llm-wiki, persistenza, chat, ep-004, rischio-1]
---

# Dossier EP-004 r1 da code_repos/llm_wiki, 2026-11-21: rischio 1, percorso cancella-salva-carica delle chat (repo-sync)
> Estrazione mirata `repo-sync` v2.12 del 2026-11-21 sul commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` (HEAD staccato, nessun ramo), stato `partial`, 9 file letti, sola lettura (Q_003). «Osservato» = letto nel codice; «deduzione non testata» = ricavata da fatti osservati, mai eseguita. Il repo è di terzi sotto GNU GPL v3: il raw cita solo nomi, simboli e percorsi.

## Contesto
Primo dossier della serie di EP-004 (TSK-012 / US-025), dedicato al rischio 1 di [[llm-wiki-rischi-persistenza]]. Parte dall'ipotesi già in wiki e ripercorre sul sorgente il percorso di cancellazione, salvataggio e caricamento delle chat; non ripete stack e struttura ([[2026-11-20-repo-llm_wiki]]) e verifica quanto già indicato in [[2026-11-20-repo-llm_wiki-persistenza-c]]. L'estrazione non ha avuto `Bash` né `Grep`: un «non trovato» vale solo per i file e le righe letti. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r1.md §Identità e perimetro]

## Dettaglio

### Percorso tracciato (osservato)
- Non esiste un comando unico «cancella tutte»: è la ripetizione del cestino per ogni conversazione; `clearMessages` toglie solo i messaggi della conversazione attiva (`chat-store.ts:311-316`). [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r1.md §Tracciamento cancella-tutte, salvataggio, caricamento]
- Cancellazione: `deleteConversation` agisce solo sullo store (`chat-store.ts:150-164`); il cestino di `ConversationSidebar` (`chat-panel.tsx:240-255`, chiamata a 249) chiama poi `deleteFile` su `<progetto>/.llm-wiki/chats/<id>.json` senza `await` e con errore ignorato; il percorso usa `proj.path` non normalizzato. Il corpo di `delete_file` in Rust non è letto. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r1.md §Passo 1. Cancellazione di una conversazione (osservato)]
- Salvataggio: auto-save con timer di 2 s, saltato in streaming o con auto-save sospeso (`auto-save.ts:108-129`); `saveChatHistory` scrive `conversations.json` (anche `[]`) e un `chats/<id>.json` solo per le conversazioni con messaggi (ultimi 100); **non elimina alcun file** e `deleteFile` non è importata in `persist.ts` (riga 1). [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r1.md §Passo 2. Salvataggio dopo la cancellazione (osservato)]
- Caricamento: `loadChatHistory` (`persist.ts:114-175`) legge solo gli id dell'indice; con indice e messaggi vuoti, o `conversations.json` mancante o non valido, chiama `recoverChatHistoryFromOrphanChatFiles` (`persist.ts:205-242`), che ricostruisce da `chats/*.json` con almeno un messaggio (un orfano `[]` non è ricostruito); `App.tsx:51-71` attiva le conversazioni ricostruite. La ricostruzione è voluta (corregge una gara all'avvio, `persist.ts:136-139`) ed è coperta da due test (`persist.integration.test.ts:391-425`, con `realFs`). [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r1.md §Passo 3. Caricamento e ricostruzione da `chats/*.json` orfani (osservato)]

### Condizioni di ricomparsa (deduzione non testata)
Un orfano nasce solo se la rimozione del cestino non si compie: (1) `delete_file` fallisce e l'errore è ignorato (per esempio file bloccato su Windows); (2) chiusura dell'app prima della chiamata senza `await`; (3) un `saveChatHistory` già avviato riscrive il file dopo la rimozione; (4) orfani vecchi che tornano quando si cancella l'ultima conversazione; (5) il salvataggio successivo riscrive l'indice con le chat risorte. Nessuna provata in esecuzione. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r1.md §Condizioni di ricomparsa (deduzione dal codice letto, non testata)]

### `agent-sessions/`
Letta solo `agent/session.rs` per intero: nessuna cancellazione fuori dai test (`remove_dir_all` su cartelle temporanee). Il frontend usa l'id di conversazione come `sessionId` (`chat-panel.tsx:992, 1070`); il cestino colpisce solo `chats/`, quindi `agent-sessions/<id>.json` sopravvive (divergenza, non causa di ricomparsa: `loadChatHistory` non lo legge). Il valore predefinito di `persistSession` nel percorso in streaming non è letto. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r1.md §Stringa `agent-sessions/`]

### Esito proposto: non conclusivo per lettura
Il meccanismo esiste, ma l'innesco dipende dall'esito a runtime di una cancellazione che il codice dà per riuscita. Smentita parziale della forma generale (nel caso ordinario il cestino rimuove il file), conferma parziale del meccanismo (con un orfano e indice vuoto o assente la ricomparsa è certa per lettura). Impatto se si verifica: divergenza, non perdita. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r1.md §Esito proposto: NON CONCLUSIVO per lettura]

### File non letti e gap evidenti
Non letti: corpo di `delete_file` e `run_guarded` (`fs.rs`), `chat-panel.tsx` oltre la riga 1829, `test-helpers/fs-temp.ts`, `chat-store.test.ts`, altri chiamanti di `loadChatHistory`/`saveChatHistory`/`deleteConversation`, comandi Rust che potrebbero cancellare `.llm-wiki/`. Gap del raw: fallimento silenzioso di `delete_file`, gara salvataggio-cestino, elenco dei cancellatori, regole di visibilità di `list_directory` in `.llm-wiki`, default di `persistSession`, normalizzazione del percorso del cestino. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r1.md §File letti e non letti] [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r1.md §Gap evidenti]

### Controllo del repo e dei segreti dichiarato dal raw
L'agente non ha eseguito `git status`; il controllo a comando è stato fatto dalla sessione principale (vedi TSK-012, §Chiusura). Nessun valore di credenziale: solo nomi di simboli e percorsi. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r1.md §Note di estrazione]

## Pagine collegate
[[llm-wiki-rischi-persistenza]] (§Esito della verifica di US-025), [[llm-wiki-operazioni-distruttive]], [[llm-wiki-versioni-e-migrazioni]], [[llm-wiki-archivi-persistenza]].

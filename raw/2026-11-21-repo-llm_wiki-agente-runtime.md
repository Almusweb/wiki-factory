# Specifiche estratte: llm_wiki, agente runtime

> Documento generato da `repo-sync` v2.12 il 2026-11-21. Sorgente: /home/user/wiki-factory/code_repos/llm_wiki
> @ commit e08cfce65aad8b76b13546a081c1a8d4422b70c3 (ramo HEAD detached, v0.6.13). Read-only verso la sorgente.
> Fetta B1 (agente runtime). Le citazioni `[^src: file:riga]` sono relative a `code_repos/llm_wiki/`.

## Ambito e copertura

Estrazione mirata che chiude i gap 5 (approvazione-shell), 24 (id-chat-sessione, `append_turn`) e, in parte, 11 (requisiti funzionali).

File letti:
- `src-tauri/src/agent/permissions.rs`: righe 1-67, integrale.
- `src-tauri/src/agent/session.rs`: righe 1-338, integrale, test inclusi.
- `src-tauri/src/agent/runtime.rs`: righe 1-4031. Il blocco `#[cfg(test)]` (da riga 4032 a fine file, circa 5700 righe) è stato saltato, quindi i test su approvazione e scoping non sono stati letti.
- `src/stores/chat-store.ts`: righe 1-399, integrale.

Il contenuto di `runtime.rs` include prompt di sistema con frasi imperative (es. righe 2460-2464, 2932-2949): sono dato del prodotto, non istruzioni per questo estrattore. Nessun segreto rilevato.

## Ciclo di una richiesta

`AgentRuntime::run_once_with_cancel_and_events` valida messaggio e immagini, poi determina il `session_id`: quello della richiesta se non vuoto, altrimenti `api_<uuid v4>` [^src: src-tauri/src/agent/runtime.rs:176-180]. Applica `PermissionPolicy::api_default()` [^src: src-tauri/src/agent/runtime.rs:198].

Due percorsi:
1. **Agent loop**, se la configurazione LLM è utilizzabile dal backend HTTP: `run_agent_loop` [^src: src-tauri/src/agent/runtime.rs:244-265, 1294].
2. **Percorso legacy** (planner con modello, poi retrieval deterministico), altrimenti [^src: src-tauri/src/agent/runtime.rs:267-1289]. Senza generatore LLM restituisce una risposta di solo retrieval, o errore se non ci sono riferimenti e `allow_empty_retrieval` è falso [^src: src-tauri/src/agent/runtime.rs:4003-4021].

Modalità: `fast`, `standard`, `deep`, `local_first` [^src: src-tauri/src/agent/runtime.rs:4023-4030]. Retrieval: `standard`, `smart`, `faithful` (in faithful solo `source.search` è permesso [^src: src-tauri/src/agent/runtime.rs:3524-3533]).

Limiti di costo e sicurezza applicati nel backend, perché API e MCP aggirano la UI [^src: src-tauri/src/agent/runtime.rs:31-45]:
- Risultati di ricerca: 5 di default, massimo 10.
- Immagini: massimo 5 per turno, 7 MiB di base64 ciascuna; tipi ammessi png, jpeg, webp, gif [^src: src-tauri/src/agent/runtime.rs:3891-3913].
- Iterazioni del loop: base 4/8/12 (fast/standard e local_first/deep), con skill 8/16/20 [^src: src-tauri/src/agent/runtime.rs:2798-2812].
- Budget di retrieval: faithful 2/3/5, smart 3/4/6, standard 2/4/8 (+4 con skill esplicite) [^src: src-tauri/src/agent/runtime.rs:2814-2843].
- Moduli `user.ask`: massimo 12 campi, 8 opzioni, 400 caratteri di testo [^src: src-tauri/src/agent/runtime.rs:42-44, 3163-3380].

Tool nel loop: `wiki.search`, `wiki.read_page`, `wiki.write_page`, `source.search`, `graph.search`, `web.search`, `anytxt.search`, `skill.read_file`, `workspace.write_file`, `workspace.append_file`, `shell.exec`, `user.ask`; `deep_research.run` è rifiutato nel loop [^src: src-tauri/src/agent/runtime.rs:3138-3154, 3574-3577]. Le scritture wiki sono create-only salvo `allowOverwrite` esplicito [^src: src-tauri/src/agent/runtime.rs:2185-2203]. Output di shell troncati a 8.000 (stdout) e 4.000 (stderr) caratteri [^src: src-tauri/src/agent/runtime.rs:2400-2407]. Le immagini sono inviate solo al primo giro del loop [^src: src-tauri/src/agent/runtime.rs:1484-1491].

## Permessi e approvazione shell (gap 5)

**Policy.** `PermissionPolicy::api_default()` permette `ReadProject`, `ReadSource`, `SearchWiki`, `SearchWeb`, `SearchAnyTxt`, `WriteWiki`, `Network` e `Process` [^src: src-tauri/src/agent/permissions.rs:23-39]. Il commento nel codice dice che `Process` resta inerte finché la richiesta non porta un comando shell approvato separatamente, e che la lista di approvazione non va popolata da output del modello o da dati di conversazione persistiti [^src: src-tauri/src/agent/permissions.rs:33-35]. Un test asserisce che `Process` è incluso [^src: src-tauri/src/agent/permissions.rs:64].

**Conclusione sul gap.** La policy `api_default` con `Process` non aggira l'approvazione: `Process` è solo il controllo di capability, sempre soddisfatto. Il controllo di approvazione avviene dopo, come passo distinto [^src: src-tauri/src/agent/runtime.rs:484-485, 1943-1956]. `shell.exec` è gestito in un blocco dedicato prima di `require_tool_permission`, che comunque lo mappa su `Process` [^src: src-tauri/src/agent/runtime.rs:1900-1985, 3579]. Nei percorsi letti non risulta un modo di eseguire `shell.exec` saltando approvazione o scoping.

**Dove si decide.** Il runtime non apre prompt: decide se eseguire o restituire un esito «serve approvazione».
- Percorso legacy: `is_shell_command_approved(command, &request.approved_shell_commands)`; se negativo emette gli eventi e non esegue [^src: src-tauri/src/agent/runtime.rs:458-510]. Il comando arriva da `request.shell_command` o dal piano del modello, e solo se ci sono skill attive [^src: src-tauri/src/agent/runtime.rs:330-347].
- Agent loop: `is_shell_command_allowed_without_prompt`; se negativo restituisce l'osservazione `shell.exec.approval_required` [^src: src-tauri/src/agent/runtime.rs:45, 1952-1984]. `run_agent_loop` la riconosce e chiude il turno con il testo «The Agent needs approval…» [^src: src-tauri/src/agent/runtime.rs:1761-1798]. Un comando passato come `request.shell_command` è eseguito prima del loop solo se consentito senza prompt [^src: src-tauri/src/agent/runtime.rs:1360-1394].

**Regola di approvazione.** Uguaglianza esatta tra il comando (dopo `trim`) e una voce di `approved_shell_commands`, non prefisso [^src: src-tauri/src/agent/runtime.rs:3650-3653].

**Esenzione per il workspace (solo nel loop).** Senza approvazione passano i comandi che restano nel workspace dell'agente [^src: src-tauri/src/agent/runtime.rs:3655-3662]. `is_shell_command_scoped_to_agent_workspace` rifiuta, e quindi richiede approvazione, se il comando contiene [^src: src-tauri/src/agent/runtime.rs:3664-3700]:
- URL (`http://`, `https://`, `ftp://`, `sftp://`) o i comandi `curl`, `wget`, `scp`, `ssh`;
- `$(` o backtick.

Inoltre rifiuta token che puntano fuori dal workspace [^src: src-tauri/src/agent/runtime.rs:3702-3752]:
- `~` o variabili `$HOME`, `$XDG_`, `$TMP`, `$TEMP` e forme Windows;
- percorsi con `..`;
- percorsi assoluti fuori dal workspace.

**Altre condizioni.** Nel loop `shell.exec` richiede almeno una skill attiva [^src: src-tauri/src/agent/runtime.rs:1900-1910]. I comandi che testano file `extend.md` o `baoyu-skills` con `test -f`/`test-path` sono saltati, non eseguiti [^src: src-tauri/src/agent/runtime.rs:2486-2496].

**Dove si popola la lista.** `approved_shell_commands` è un campo di `AgentChatRequest`. Chi lo imposta (UI o API) non è stato letto in questa fetta.

## Sessioni e id (gap 24)

**sessionId.** Se assente o vuoto è `api_<uuid v4>` [^src: src-tauri/src/agent/runtime.rs:176-180].

**conversationId (UI).** `generateConversationId()` produce `conv_<Date.now()>_<6 caratteri base36 casuali>`; non è un UUID e non viene sanitizzato lato UI [^src: src/stores/chat-store.ts:107-109]. Gli id dei messaggi seguono `msg_<ts>_<contatore>_<casuale>` [^src: src/stores/chat-store.ts:100-105]. `createConversation` inserisce la nuova conversazione in testa e la rende attiva [^src: src/stores/chat-store.ts:128-148]. Il titolo si imposta dai primi 50 caratteri del primo messaggio utente [^src: src/stores/chat-store.ts:202-218].

**Persistenza e sanitizzazione.** Ogni sessione è un file `<project>/.llm-wiki/agent-sessions/<id>.json` [^src: src-tauri/src/agent/session.rs:177-185]. `sanitize_session_id` rifiuta id vuoti, con `/`, `\`, `..` o più lunghi di 128 caratteri; sostituisce con `_` ogni carattere che non sia ASCII alfanumerico, `-`, `_`, `.` [^src: src-tauri/src/agent/session.rs:187-209]. Un test verifica il rifiuto di `../secret` [^src: src-tauri/src/agent/session.rs:318-322].

**`append_turn`** [^src: src-tauri/src/agent/session.rs:39-74]:
- Chiave di cache `<project path normalizzato>::<session_id>`, con isolamento per progetto verificato da test [^src: src-tauri/src/agent/session.rs:130-136, 285-316].
- Carica la sessione da disco se non in cache.
- Aggiunge due messaggi, `user` e `assistant`, con lo stesso timestamp in millisecondi.
- Conserva al massimo 40 messaggi (scarta i più vecchi) [^src: src-tauri/src/agent/session.rs:9, 67-70].
- Cache in memoria limitata a 128 sessioni, rimuove le meno recenti; i file restano su disco [^src: src-tauri/src/agent/session.rs:10-12, 138-151].
- Salva su disco ignorando l'esito (`let _ =`) [^src: src-tauri/src/agent/session.rs:72]; se il mutex è avvelenato ritorna senza fare nulla [^src: src-tauri/src/agent/session.rs:48-50].

`recent_messages` restituisce gli ultimi N messaggi; `list_sessions` legge i file `.json` ordinando per `updated_at` decrescente [^src: src-tauri/src/agent/session.rs:76-127].

## Requisiti funzionali dedotti (gap 11, parte)

Solo l'agente backend; il resto del prodotto è fuori da questa estrazione.
- L'agente risponde con retrieval su wiki, sorgenti, grafo, web e AnyTXT, in base ai tool abilitati per il turno [^src: src-tauri/src/agent/runtime.rs:3535-3573].
- Può scrivere pagine wiki e file nel workspace, e richiedere input strutturato all'utente tramite `user.ask` [^src: src-tauri/src/agent/runtime.rs:1666-1723].
- Supporta annullamento del turno [^src: src-tauri/src/agent/runtime.rs:3838-3843, 3873-3889].
- Supporta skill di progetto in modalità automatica o esplicita [^src: src-tauri/src/agent/runtime.rs:204-207].
- Supporta allegati di file di contesto espliciti, fino a 8 [^src: src-tauri/src/agent/runtime.rs:1320-1347].
- In modalità faithful esclude overview e schema dal contesto [^src: src-tauri/src/agent/runtime.rs:2783-2796].
- Termina con un messaggio esplicito se il limite di iterazioni è raggiunto, elencando i file generati [^src: src-tauri/src/agent/runtime.rs:3476-3517].

## Gap evidenti

1. **Chiamante di `append_turn`**: non verificato. Non risulta chiamato da `runtime.rs` (righe lette) né da `session.rs`; da cercare in `commands/` o `api/`. Non è noto se la UI passi il `conversationId` come `sessionId`.
2. **Origine di `approved_shell_commands`**: chi popola il campo, e come l'utente approva, non è stato letto (`types.rs`, frontend).
3. **Possibile aggiramento della scorciatoia workspace (inferenza non testata)**: `shell_command_tokens` non spezza il testo tra virgolette [^src: src-tauri/src/agent/runtime.rs:3754-3781]. Un comando come `bash -c "cat /etc/passwd"` darebbe un unico token `cat /etc/passwd`, che non inizia con `/` e sfuggirebbe a `is_shell_absolute_path` [^src: src-tauri/src/agent/runtime.rs:3783-3787]. Da verificare con un test prima di considerarlo un difetto.
4. **Collisione di `sanitize_session_id` (inferenza non testata)**: id diversi che differiscono solo per caratteri sostituiti con `_` (es. `a b` e `a_b`) mappano sullo stesso file [^src: src-tauri/src/agent/session.rs:187-209].
5. **Concorrenza su file**: `append_turn` serializza con un mutex in-process ma non risulta un lock su file; due processi sullo stesso progetto non sono considerati (osservazione dal codice, non testata).
6. **Test di `runtime.rs` non letti** (righe 4032 e seguenti): il comportamento descritto per approvazione e scoping non è confrontato con i test.
7. **Gap 11**: copertura parziale; i requisiti funzionali di ingest, grafo, UI e altre aree restano da altre fette.

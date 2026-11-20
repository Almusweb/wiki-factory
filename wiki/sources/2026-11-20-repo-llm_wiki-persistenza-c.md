---
id: 2026-11-20-repo-llm_wiki-persistenza-c
type: source
title: Specifiche estratte da code_repos/llm_wiki, persistenza fetta C (repo-sync)
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: ["raw/2026-11-20-repo-llm_wiki-persistenza-c.md"]
tags: [source, repo, llm-wiki, persistenza]
---

# Specifiche estratte da code_repos/llm_wiki, persistenza fetta C (repo-sync)
> Estrazione mirata «fetta C» sul commit `e08cfce`: chiamanti delle 22 operazioni distruttive della tabella wiki, cascata di cancellazione di una pagina, ciclo di vita delle sorgenti, cancellazione dei file di chat, chiamanti di `append_turn`, vecchio formato vettoriale v1, endpoint API che scrivono, cancellazioni e copie in `fs.rs`. Stato `partial`.

## Contesto
Quarta estrazione mirata sullo stesso commit, dopo la prima ([[2026-11-20-repo-llm_wiki]]), la fetta A ([[2026-11-20-repo-llm_wiki-persistenza-a]]) e la fetta B ([[2026-11-20-repo-llm_wiki-persistenza-b]]). Prodotta da `repo-sync@2.12.0` per TSK-004 (US-013 e US-016) sul commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3`, ramo `develop`, estratta il 2026-11-20 alle 20:13 (+01:00). [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Identità e perimetro]

## Dettaglio

### Metadati dell'estrazione
- Il repository è di terzi, sotto GNU GPL v3; il raw descrive il codice con parole proprie e cita solo nomi di file, simboli, campi e percorsi, senza frammenti di codice né valori di segreto. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Identità e perimetro]
- Stato `partial`. Letti 16 file (2 interi, 14 a finestre) per circa 66 KB; otto già citati dalle estrazioni precedenti e otto nuovi. `files_sampled` cumulativo 93, dichiarato come massimo (l'elenco esatto dei 30 file della prima estrazione non è verificabile); coincide con il manifest (85 dopo la fetta B più 8). `files_total_in_repo` 476. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Copertura del gap `llm-wiki-persistenza-codice-non-letto`]
- `secrets_redacted` 0: lo zero vale per i file e gli intervalli aperti, non è una scansione dell'intero repo (gap `llm-wiki-scan-credenziali`). Nessuna scrittura sotto `code_repos/llm_wiki`. Deviazione dichiarata: 11 righe di `lib.rs` (241-251) lette oltre la finestra approvata e non usate per alcuna affermazione. Istruzioni trovate nei file letti: nessuna rivolta a un agente e nessuna ostile, solo commenti per i manutentori, non eseguiti. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Note di estrazione]
- Il raw distingue quattro livelli di certezza: «letto» (osservato in una finestra, con riga), «deduzione», «non verificato» e «solo mappa (graphify/grep)». L'ultimo è una riga della mappa della sessione (file locale non versionato, rigenerabile), non riletta nel sorgente e non fonte normativa: nelle pagine è riportata senza promuoverla. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Identità e perimetro]
- Ambito delle ricerche testuali: sorgenti non di test sotto `src` e `src-tauri/src`; restano fuori `mcp-server`, `extension`, `scripts` e i test. Uno zero vale per la stringa esatta e per questo ambito. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Identità e perimetro]
- Limiti osservati degli strumenti: il grafo AST di graphify (senza LLM, copia `git archive` del commit) non risolve chiamate a metodo, confine IPC TS/Rust e import dinamici con destrutturazione; per `resetProjectState` graphify dà zero chiamanti mentre la ricerca testuale ne trova. Tre chiamanti della cascata sono emersi solo da lettura e ricerca testuale. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Identità e perimetro]

### Contenuto
- Chiamanti riga per riga delle 22 operazioni della tabella di [[llm-wiki-operazioni-distruttive]]: per molte c'è lettura diretta (`vector_delete_page`, ingest cache, `append_turn`, rebuild, import ed export), per altre solo mappa (`invalidate_page_revision`, `prune_history_store`, `restore_file_history`, `removeFromRecentProjects`, `cleanupRemovedScheduledImports`, `resetProjectState`). [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Operazioni distruttive: chiamanti, riga per riga]
- Il raw elenca 18 operazioni assenti dalla tabella wiki; la seconda tabella di [[llm-wiki-operazioni-distruttive]] le riporta come sono, senza ricondurle a un numero diverso. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Operazioni distruttive non presenti nella tabella wiki]
- Nessun chiamante nell'ambito cercato per `vector_delete` (v1), `vector_upsert` (v1), `clearCompletedTasks` e `cleanupWrittenFiles` (solo definizione). I due comandi v1 sono registrati nell'elenco dei comandi (`lib.rs:672` e `:674`), quindi raggiungibili da un chiamante esterno al sorgente cercato. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Vecchio formato vettoriale (v1): chiamanti]
- Cascata di cancellazione di una pagina (`wiki-page-delete.ts`, letto per intero) e ciclo di vita delle sorgenti (`source-lifecycle.ts`, finestre): vedi [[llm-wiki-cancellazione-pagine-e-sorgenti]]. Quattro file importano il modulo; un quinto riferimento in `ingest.ts` è un commento. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Cascata di cancellazione di una pagina]
- File di chat: un solo punto di cancellazione trovato (cestino in `ConversationSidebar`, `chat-panel.tsx:235-265`), senza attesa e con errore ignorato; nessuna ricerca sulla cancellazione dei file `agent-sessions/`. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §File di chat: dove e quando si cancellano]
- `append_turn` ha tre chiamanti di produzione (`lib.rs:128`, `lib.rs:235`, `api_server.rs:2076`) e non è chiamato da `agent/runtime.rs`; passano tutti `response.session_id`. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §`append_turn`: chiamanti e identificativo di sessione]
- Endpoint API che scrivono: `PATCH`, `DELETE` e bulk resolve delle review, `POST pages/write`, `POST chat`, `POST pages/embed` e `POST sources/rescan` (corpi non letti). Nessuna rotta cancella pagine o file; la tabella delle rotte è chiusa da un 404. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Endpoint dell'API locale che scrivono o cancellano]
- `fs.rs` righe 1660-1790: `delete_file` con fino a 4 tentativi su errori transitori Windows e senza controllo di confine nelle righe lette; `copy_file` e `copy_directory` sovrascrivono la destinazione, `copy_directory` salta le voci con nome che inizia con un punto. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Cancellazioni e copie nella scrittura generica (`fs.rs`)]

### Limiti e gap
- Restano scoperti, tra gli altri: `file_sync.rs` 445-1289, `fs.rs` 1385-1659, 1791-1839, 1862-1931 e 1948-fine, `search.rs` dalla 1201, i corpi di `handle_embed_page`, `handle_chat`, `handle_rescan`, `resolve_review_items`, `read_raw_review_array` e `write_raw_review_array`, `agent/runtime.rs`, `agent/tools.rs`, `proxy.rs` dalla 261, gran parte di `ingest.ts` e di `source-lifecycle.ts`, la parte di scrittura di `sweep-reviews.ts`. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Copertura del gap `llm-wiki-persistenza-codice-non-letto`]
- Il raw elenca 11 gap evidenti: origine e sanitizzazione dell'id di sessione, `write_wiki_page_verified`, corpi API non letti, conferma della cancellazione in `lint-view.tsx`, effetto di `vector_delete_page` sul file di revisione, chiamanti non classificati, `run_guarded`, cancellazione di `agent-sessions/`, corpi di `removeTasks` e `cancelAllTasks`, origine delle stringhe `delete:<percorso>` e la correzione su `append_turn`. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Gap evidenti]

### Pagine ricavate o aggiornate
- Nuova: [[llm-wiki-cancellazione-pagine-e-sorgenti]].
- Aggiornate: [[llm-wiki-operazioni-distruttive]], [[llm-wiki-rischi-persistenza]] (indizi, esito invariato), [[llm-wiki-versioni-e-migrazioni]], [[llm-wiki-api-locale]], [[llm-wiki-agente]], [[llm-wiki-archivi-persistenza]] (riga sessioni agente).

### Gap aperti da questa fetta
Dai gap evidenti sono stati aperti in [[gaps]], accorpati con quelli di altre fette: `llm-wiki-cancellazione-controlli-confine`, `llm-wiki-cancellazione-file-orfani`, `llm-wiki-scritture-non-verificate`, `llm-wiki-chiamanti-non-verificati`. Il gap `llm-wiki-vector-v1-chiamanti` non è chiuso da questo ingest. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Gap evidenti]

## Estratto non promosso a pagina
Nessun contenuto del raw è stato scartato. Il testo del raw non è stato modificato.

## Pagine collegate
[[2026-11-20-repo-llm_wiki]], [[2026-11-20-repo-llm_wiki-persistenza-a]], [[2026-11-20-repo-llm_wiki-persistenza-b]], [[gaps]]

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

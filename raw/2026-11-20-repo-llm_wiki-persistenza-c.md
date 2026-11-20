---
source_path: C:\local_git\code\wiki-factory\code_repos\llm_wiki
source_type: repo
git_branch: develop
git_commit: e08cfce65aad8b76b13546a081c1a8d4422b70c3
extracted_at: 2026-11-20T20:13:01+01:00
extractor: repo-sync@2.12.0
scope: persistenza, fetta C (operazioni distruttive, chiamanti, vecchio formato vettoriale)
---

# Specifiche estratte: llm-wiki, persistenza fetta C

> Documento generato da `repo-sync` v2.12 il 2026-11-20. Sorgente: `C:\local_git\code\wiki-factory\code_repos\llm_wiki`
> @ commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` (ramo `develop`). Read-only verso la sorgente.

## Identità e perimetro

- Estrazione **mirata** (TSK-004, US-013 e US-016), non generale. Quarta estrazione sullo stesso commit. Valgono la prima (`raw/2026-11-20-repo-llm_wiki.md`, con le sezioni «Aggiornamenti»), la fetta A (`raw/2026-11-20-repo-llm_wiki-persistenza-a.md`) e la fetta B (`raw/2026-11-20-repo-llm_wiki-persistenza-b.md`). Stack, struttura, API generale e dipendenze non sono ripetuti.
- Perimetro: per ogni riga della tabella `wiki/concepts/llm-wiki-operazioni-distruttive.md`, chi la invoca; cascata di cancellazione di una pagina; ciclo di vita delle sorgenti; cancellazione dei file di chat; chiamanti di `append_turn` e identificativo di sessione; chiamanti di scrittura e cancellazione del vecchio formato vettoriale; endpoint dell'API che scrivono o cancellano; cancellazioni e copie in `fs.rs`; copertura.
- **Licenza**: il repository è di terzi, sotto GNU GPL v3. Il documento descrive il codice con parole proprie e cita solo nomi di file, simboli, campi e percorsi. Nessun frammento di codice, nessun valore di segreto. Il contenuto letto è trattato come dato, mai come istruzione.
- **Convenzioni.** Percorsi relativi alla radice del repo. «Letto» = osservato in una finestra di questa fetta, citato `[^src: percorso:righe]`. «Deduzione» = ricavato da fatti letti, non visto in esecuzione. **«Solo mappa (graphify/grep)»** = riga della mappa della sessione (graphify/grep), file locale non versionato `.graphify-state/verifiche/2026-11-20-fetta-c-mappa.md`, rigenerabile; non riletto nel sorgente. Le ricerche testuali valgono per la stringa esatta. L'ambito cercato dalla sessione è: sorgenti non di test sotto `src` e `src-tauri/src`; restano fuori `mcp-server`, `extension`, `scripts` e i test.
- **Limiti degli strumenti, osservati in questa fetta.** Il grafo AST di graphify (senza LLM, copia `git archive` del commit) non risolve: le chiamate a metodo (per `append_turn` vede solo i test), il confine IPC tra TS e Rust, e le chiamate fatte tramite import dinamico con destrutturazione. Due di queste ultime sono state trovate con la lettura (`ingest-queue.ts:277,284` e `source-lifecycle.ts:560-561`) e confermate dalla ricerca testuale. Per `resetProjectState` graphify dà zero chiamanti mentre la ricerca testuale ne trova. Uno zero di graphify non prova l'assenza.
- Finestre approvate dall'utente: circa 65 KB letti nei 15 file della tabella di Fase 1, più due finestre extra autorizzate (`lint-view.tsx` 335-350, `ingest.ts` 3550-3560).

## Operazioni distruttive: chiamanti, riga per riga

Le 22 righe seguono l'ordine della tabella wiki. La colonna «Chiamante» riporta interfaccia o codice.

| # | Operazione | Chiamante (interfaccia o codice) | Stato e fonte |
|---|---|---|---|
| 1 | `vector_clear_chunks` | Comando invocato da `vectorClearChunks` [^src: src/lib/embedding.ts:281-285], richiamata da `clearChunkVectorTable` [^src: src/lib/embedding.ts:309-311]. Unico chiamante di `clearChunkVectorTable`: `embedAllPages` (`embedding.ts:631`, letto, ramo «zero pagine e zero chunk»; `:705`, non classificata). Interfaccia: `EmbeddingSection` (`embedding-section.tsx:124`) | `:631` letto [^src: src/lib/embedding.ts:625-635]; `:705` e `embedding-section.tsx:124` solo mappa (graphify/grep); la fetta A ha letto `embedding-section.tsx:121-134` (re-index con svuotamento) |
| 2 | `vector_drop_legacy` | Comando invocato da `dropLegacyVectorTable` [^src: src/lib/embedding.ts:303-307]. Chiamanti: `EmbeddingSection` (`embedding-section.tsx:138`, interfaccia di Settings); `dropLegacyVectorTableBestEffort` (`embedding.ts:323-325`), a sua volta chiamata da `embedAllPages` (`:632` letto; `:731` stringa non classificata) | Letto per `:303-307` e `:632`; il resto solo mappa (graphify/grep). Conferma «da Settings» della wiki: solo mappa |
| 3 | `vector_delete_page` | `removePageEmbedding` [^src: src/lib/embedding.ts:848-858], chiamata da `cascadeDeleteWikiPage` [^src: src/lib/wiki-page-delete.ts:78] e da `cleanupDeletedWikiPages` [^src: src/lib/source-lifecycle.ts:618]. Pulizia id legacy: `removeLegacyVectorIdIfSafe` [^src: src/lib/embedding.ts:250-264], chiamata da `removePageEmbedding` (`:854`) e da `vectorUpsertPageChunks` (`:272`) | Letto. `cleanupWrittenFiles` non è un innesco: vedi «Contraddizioni» |
| 4 | `vector_delete` (v1) | **Nessun chiamante nell'ambito cercato.** Registrato nell'elenco dei comandi [^src: src-tauri/src/lib.rs:674] | Letto per la registrazione; assenza da mappa (nessuna invocazione nel TS; in Rust solo `vectorstore.rs:278-279` e `lib.rs`) |
| 5 | `vector_upsert_chunks` | Comando invocato in `embedding.ts:184` (mappa), tramite `vectorUpsertPageChunks` [^src: src/lib/embedding.ts:266-273]. Chiamanti di questa: `embedPage` (`embedding.ts:491`) e `embedAllPages` (`:681`); `:745` stringa non classificata | Solo mappa (graphify/grep) per i chiamanti; definizione letta |
| 6 | `vector_upsert` (v1) | **Nessun chiamante nell'ambito cercato.** Registrato [^src: src-tauri/src/lib.rs:672] | Come la riga 4 (definizioni `vectorstore.rs:151,156`, test da `:1291`) |
| 7 | `vector_optimize_chunks` | Comando invocato in `embedding.ts:288` tramite `vectorOptimizeChunks` [^src: src/lib/embedding.ts:287-291], chiamata da `optimizeChunkVectorTableBestEffort` (`embedding.ts:315`) | Chiamante di quest'ultima: non verificato (non cercato) |
| 8 | `invalidate_page_revision` | `vector_upsert_chunks_inner` (`vectorstore.rs:539`) e un test (`page_embedding.rs:870`) | Solo mappa (graphify) |
| 9 | `clear_file_history` | Interfaccia: pulsante di cancellazione cronologia in `MaintenanceSection`, con conferma distruttiva, via `clearFileHistory` (`fs.ts:179-180`) [^src: src/components/settings/sections/maintenance-section.tsx:174-190] | Letto; il wrapper `fs.ts:179` solo mappa. Chiude il «chiamante UI non nel campione» della wiki |
| 10 | `set_file_history_settings` | Interfaccia: `MaintenanceSection` (`updateHistorySettings`, `:121-144`, chiamata a `:127`); il limite a 0 passa da `commitHistoryRetention` con conferma distruttiva e imposta anche `enabled` a falso [^src: src/components/settings/sections/maintenance-section.tsx:146-172] | Letto; il wrapper `setFileHistorySettings` (`fs.ts:168-172`) ha come unico chiamante `MaintenanceSection` (graphify) |
| 11 | `prune_history_store` | `record_file_version` (`file_history.rs:287`) e `restore_file_history` (`:425`) | Solo mappa (graphify) |
| 12 | `restore_file_history` | Interfaccia: `FileHistoryButton` (`file-history-panel.tsx:48`) tramite `restoreFileHistory` (`fs.ts:187`) | Solo mappa (graphify) |
| 13 | `rebuild_wiki_index` | Azione manuale di `MaintenanceSection` [^src: src/components/settings/sections/maintenance-section.tsx:197-205] | Riportato dalla fetta B; unicità dell'invocazione non verificata |
| 14 | `import_project_archive` | `MaintenanceSection`, seguita da `openProject` e `addToRecentProjects` [^src: src/components/settings/sections/maintenance-section.tsx:218-230] | Riportato dalla fetta A |
| 15 | `export_project_archive` | `MaintenanceSection` (`:213`) | Riportato dalla fetta B |
| 16 | `append_turn` (troncamento sessione) | `lib.rs:128`, `lib.rs:235`, `api_server.rs:2076`. Dettaglio nella sezione dedicata | Letto |
| 17 | `saveChatHistory` (troncamento chat) | `flushAndSuspendAutoSave` (`auto-save.ts:51`) e `setupAutoSave` (`auto-save.ts:125`) | Fetta B (file letto per intero) e graphify; non riletto |
| 18 | `removeTasks`, `discardTasksForSources`, `clearCompletedTasks`, `cancelAllTasks` | `removeTasks`: interfaccia `ActivityPanel`, rimozione dei task selezionati dopo conferma distruttiva [^src: src/components/layout/activity-panel.tsx:170-178], e tramite `removeTask` [^src: src/lib/ingest-queue.ts:666-669] da `handleIngestRemove` (`activity-panel.tsx:198-201`, senza conferma nella finestra). `discardTasksForSources`: `discardInactiveProjectTasksForSources` (`ingest-queue.ts:419`) e `cleanupRemovedScheduledImports` (`scheduled-import.ts:339`). `cancelAllTasks`: `ActivityPanel`, dopo conferma distruttiva e solo se ci sono task pending o in corso [^src: src/components/layout/activity-panel.tsx:203-212]. **`clearCompletedTasks`: nessun chiamante nell'ambito cercato** | `discardTasksForSources` agisce sui soli task del progetto attivo, abortisce quelli in corso e salva la coda [^src: src/lib/ingest-queue.ts:677-713]. I chiamanti di `discardTasksForSources` solo mappa (graphify) |
| 19 | `removeFromIngestCache`, `moveIngestCacheEntry` | `deleteSourceFiles` per entrambe le chiavi (identità e nome file), con errore ignorato [^src: src/lib/source-lifecycle.ts:504-510]; `migrateSourcePath` per lo spostamento [^src: src/lib/source-lifecycle.ts:209] | Letto |
| 20 | `removeFromRecentProjects` | Interfaccia: `WelcomeScreen`, `handleRemoveRecent` (`welcome-screen.tsx:28`) | Solo mappa (graphify) |
| 21 | `cleanupRemovedScheduledImports` | `scanAndImport` (`scheduled-import.ts:559`); al suo interno chiama `deleteSourceFile` (`:345`) e `discardTasksForSources` (`:339`) | Solo mappa (graphify) |
| 22 | `resetProjectState` | `App.tsx:445,577,581,644`; `auto-save.ts:12,28` non classificate in questa fetta | Solo mappa (grep); graphify dà zero, falso zero |

Per le righe 1-3 e 5-7 la tabella usa solo `embedding.ts`: una ricerca testuale sulla stringa esatta di ciascun nome (`clearChunkVectorTable`, `dropLegacyVectorTable`, `vectorUpsertPageChunks`, `vectorOptimizeChunks`) non trova altri file, salvo `embedding-section.tsx` per `dropLegacyVectorTable`.

### Contraddizioni con la wiki

- **`cleanupWrittenFiles`.** Wiki dice: innesco di `vector_delete_page`. Codice mostra: definita a `ingest-queue.ts:273-289`, **nessun chiamante nell'ambito cercato** (la stringa compare solo nella definizione). Se fosse chiamata, passerebbe da `cascadeDeleteWikiPage` con import dinamico, salterebbe i percorsi strutturali (`isStructuralWikiPath`) e ignorerebbe gli errori [^src: src/lib/ingest-queue.ts:273-289]. Il commento in testa a `wiki-page-delete.ts` cita tra gli utilizzatori la «pulizia di ingest annullato in ingest-queue»: il commento descrive un uso che il codice cercato non mostra [^src: src/lib/wiki-page-delete.ts:10-13].
- **`clearCompletedTasks`.** Wiki dice: azione utente. Codice mostra: nessun chiamante nell'ambito cercato [^src: src/lib/ingest-queue.ts:715-721]. Il commento parla di task done e failed; il filtro tiene solo pending e processing. Gli altri stati che elimina (la wiki indica anche cancelled) non sono visibili nella finestra.
- **`vector_upsert`.** Wiki dice: innesco «Chiamate legacy». Codice e mappa mostrano: solo registrazione nell'elenco dei comandi, nessuna invocazione.
- **`vector_delete`.** Wiki dice: «nessun chiamante nel campione». Ora: nessun chiamante nell'ambito cercato, comando registrato (`lib.rs:674`). Il gap `llm-wiki-vector-v1-chiamanti` si chiude per l'ambito cercato.
- **`resetProjectState`.** Wiki dice: «chiama prima `pauseQueue`». Codice mostra: la funzione azzera prima, in modo sincrono, gli store di chat, review, lint, activity e research; poi ferma lo scheduled import e chiama `pauseQueue` di ingest e di dedup, azzera la cache del grafo e ferma la sincronizzazione file [^src: src/lib/reset-project-state.ts:18-122]. Non scrive né cancella file da sola: la scrittura su disco passa da `pauseQueue` (commento a `:80-83`, corpo non nella finestra). Il salvataggio di chat, review e lint spetta al chiamante (`flushAndSuspendAutoSave`, fetta B).
- **`vector_delete_page` e «pulizia id legacy».** Confermata, ma con un innesco in più non in wiki: `removeLegacyVectorIdIfSafe` parte anche dopo ogni `vectorUpsertPageChunks`. Agisce solo se l'id contiene `/` e se una sola pagina possiede lo stem; usa `vector_delete_page`, cioè cancella righe con id legacy nella tabella v2, non nella v1. Un tentativo per progetto e id (memoria di sessione), ripetibile se fallisce [^src: src/lib/embedding.ts:250-273].

## Cascata di cancellazione di una pagina

**Chiamanti della cascata (completi per ambito e stringa esatta).** Il modulo `wiki-page-delete` è importato da quattro file [^src: src/lib/wiki-page-delete.ts:1-288] (import: mappa grep).

| Chiamante | Tipo | Innesco |
|---|---|---|
| `knowledge-tree.tsx:128` (import statico `:12`) | Chiamata reale a `cascadeDeleteWikiPagesWithRefs` | Interfaccia: primo clic arma la riga, secondo clic sulla stessa riga esegue; poi ricarica pagine e albero [^src: src/components/layout/knowledge-tree.tsx:115-135] |
| `lint-view.tsx:343-346` | Import dinamico (`:343-345`) e chiamata reale (`:346`) | Interfaccia lint: eliminazione di una pagina orfana segnalata dal lint; poi rimuove la voce lint e aggiorna l'albero. La finestra inizia a metà della funzione: una eventuale conferma non è visibile [^src: src/components/lint/lint-view.tsx:335-350] |
| `source-lifecycle.ts:560-561` | Import dinamico e chiamata reale | `deleteSourceFiles`, per le pagine rimaste senza sorgenti [^src: src/lib/source-lifecycle.ts:558-563] |
| `ingest-queue.ts:277,284` | Import dinamico e chiamata reale a `cascadeDeleteWikiPage` | Solo dentro `cleanupWrittenFiles`, senza chiamanti [^src: src/lib/ingest-queue.ts:273-289] |
| `ingest.ts:3556` | **Riferimento in un commento**, non una chiamata | Il commento dichiara che, se manca la pagina di riepilogo della sorgente, lo sweep delle pagine orfane del lint potrebbe eliminare la cartella dei media (perdita silenziosa di immagini); descrive un rischio dichiarato dagli autori, non verificato qui [^src: src/lib/ingest.ts:3550-3560] |
| `wiki-page-delete.ts:231` | Chiamata interna | `cascadeDeleteWikiPagesWithRefs` verso `cascadeDeleteWikiPage` |

Graphify da solo vedeva solo `KnowledgeTree` (cascata con riferimenti) e la chiamata interna; i tre import dinamici sono emersi dalla lettura e dalla ricerca testuale.

**Ordine delle operazioni, `cascadeDeleteWikiPage(progetto, pagina)`** [^src: src/lib/wiki-page-delete.ts:70-109]:
1. File della pagina, con `delete_file` (vedi sezione `fs.rs`). Un errore si propaga e interrompe il resto.
2. Righe LanceDB v2 con quel `page_id`, poi la riga con id legacy se applicabile (`removePageEmbedding`). `removePageEmbedding` ingoia ogni errore [^src: src/lib/embedding.ts:848-858].
3. Solo se il percorso contiene `/wiki/sources/` e lo slug non è vuoto né inizia con un punto: cartella `wiki/media/<slug>`, con cancellazione ricorsiva. Errore ingoiato.

**`cascadeDeleteWikiPagesWithRefs(progetto, pagine)`** [^src: src/lib/wiki-page-delete.ts:133-288]:
1. Legge ogni pagina per il titolo, prima di cancellare.
2. Cascata di ogni pagina (sopra); un errore su una pagina è solo loggato e la pagina non entra nell'elenco dei cancellati.
3. Se ci sono pagine con slug: elenco dell'albero `wiki/`, poi per ogni pagina rimasta: voci di `wiki/index.md`, wikilink nel corpo trasformati in testo (alias mantenuto), voci di `related` nel frontmatter. Riscrive con `writeFile` diretta solo se il testo cambia.
4. `pruneDeletedPagesFromReviews`: riscrive `.llm-wiki/review.json` togliendo le pagine cancellate da `affectedPages`; le review che restano senza pagine sono eliminate; aggiorna lo store in memoria se il progetto è quello attivo. Errori solo loggati.

**Archivi toccati, in ordine:** pagina `.md` e media (disco), LanceDB v2 (righe), pagine `.md` rimaste e `wiki/index.md`, `review.json`. **Non toccati dal codice letto:** `ingest-cache.json` (se ne occupa `deleteSourceFiles`, solo per chiave sorgente; la voce si invalida da sola se manca un file di `filesWritten`, fetta B), `lint.json`, `dedup-queue.json`, `dedup-not-duplicates.json`, `ingest-queue.json`, `page-history/`, `wiki/log.md`. Se `vector_delete_page` tolga anche il file `embedding-revisions/<sha256>.revision`: non verificato (lato Rust non letto in questa fetta).

**Osservazioni.**
- Il commento in testa al file dice «errori propagati, non ingoiati»; il codice li propaga solo per la cancellazione del file della pagina.
- `listDirectory` a `:242` non è in try: se fallisce dopo la cancellazione, lo sweep e il prune delle review non partono (deduzione).
- La logica di sweep è duplicata in `cleanupDeletedWikiPages` (`source-lifecycle.ts:629-662`), che inoltre non pota le review ed è usata quando una pagina è già sparita da disco (chiamante `cleanupDeletedFiles`, `project-file-sync.ts:419`, solo mappa).
- Il controllo «pagina di sorgente» cerca `/wiki/sources/`, mentre `source-lifecycle.ts:620` accetta anche `wiki/sources/` relativo. Un percorso relativo passato alla cascata non attiverebbe la cancellazione dei media. È una deduzione: `normalizePath` non è nella finestra.

## Ciclo di vita delle sorgenti

`deleteSourceFile(s)` e `deleteSourceFolder` [^src: src/lib/source-lifecycle.ts:448-604].

Ordine in `deleteSourceFiles`:
1. File sorgente (se non già cancellato). Non è in try: un errore interrompe il batch e lascia il resto non eseguito (il commento di `sources-view.tsx:330-332` dice invece che il batch prosegue).
2. Per ogni sorgente: `removeParsedMarkdown` (copia in `raw/parsed`), poi `raw/sources/.cache/<nome>.txt` e `.txt.parser` (errori ignorati), poi la voce di `ingest-cache` per le chiavi identità e nome file (errori ignorati).
3. Scansione di tutte le pagine wiki: quelle con `sources:` che resta non vuoto sono riscritte; quelle che restano senza sorgenti vanno in cancellazione. **Qualsiasi pagina wiki, non solo il riepilogo**, la cui unica sorgente è quella cancellata viene eliminata, senza distinguere pagine modificate a mano. Pagine senza `sources:` leggibile sono saltate. Il confronto usa `sourceNameMatchesAny` (non letta).
4. Cascata con riferimenti sulle pagine da cancellare (sezione precedente).
5. Voce in `wiki/log.md` (`appendSourceDeleteLog`): rilegge l'intero file, con ripiego su un'intestazione se la lettura fallisce, e lo riscrive con la voce in coda [^src: src/lib/source-lifecycle.ts:691-708]. Formato della voce: data, motivo (`delete`, `external delete`, `folder delete`, `external folder delete`), nome o numero di sorgenti, e una frase con il numero di pagine cancellate e di pagine condivise tenute; con più sorgenti segue un elenco. Chiude uno degli «scrittori rimandati alla fetta C» della fetta B. Deduzione: se la lettura fallisce per un motivo diverso dall'assenza del file, la riscrittura sostituisce il contenuto del log.

`deleteSourceFolder`: raccoglie tutti i file della cartella (anche con punto), chiama `deleteSourceFiles` e poi elimina la cartella in modo ricorsivo; l'errore sulla cartella è solo loggato.

La cartella `.cache` cancellata al passo 2 è quella alla radice di `raw/sources`. La fetta B ha trovato una `.cache` accanto a ogni file sorgente: per i file in sottocartelle la cache accanto al file non è cancellata da questo codice (deduzione, valida per il singolo file; la cartella intera sparisce con `deleteSourceFolder`).

**Chiamanti.** UI: `sources-view.tsx:300` (file) e `:338` (cartella) [^src: src/components/sources/sources-view.tsx:290-345]; la conferma sta nel componente dell'albero, a due fasi (commento a `:295-298`). Solo mappa (graphify): `scheduled-import.ts:345` (`cleanupRemovedScheduledImports`), `project-file-sync.ts:402` (`cleanupDeletedFiles`, cancellazione esterna rilevata dal watcher, come descritto dalla fetta B).

**`migrateSourcePath`** (rinomina o spostamento) [^src: src/lib/source-lifecycle.ts:137-233]: riscrive `sources:` nelle pagine che citano la sorgente, sposta il riepilogo (scrive il nuovo, cancella il vecchio), sposta la voce di `ingest-cache` e la copia in `raw/parsed`. In caso di errore prima di questi ultimi passi cancella il nuovo riepilogo e ripristina il contenuto originale delle pagine riscritte (rollback best effort). Rifiuta se la destinazione esiste. Chiamante: spostamenti rilevati dal watcher (fetta B).

## File di chat: dove e quando si cancellano

- **Un solo punto di cancellazione trovato:** `ConversationSidebar`, pulsante cestino visibile al passaggio del mouse [^src: src/components/chat/chat-panel.tsx:235-265]. Nel gestore del clic: ferma la propagazione, cancella la conversazione dallo store, poi, se c'è un progetto attivo, cancella `.llm-wiki/chats/<id>.json` senza attendere e ignorando l'errore. Nella finestra non c'è conferma.
- `conversations.json` (l'indice) non è toccato dal gestore: si riallinea con l'auto-save (debounce di 2 s, fetta B), che salva solo gli ultimi 100 messaggi per conversazione.
- **Ricerca della stringa `chats/`** (non di test): `chat-panel.tsx:249` (letto) e `persist.ts:108,124,137` (solo mappa grep; fetta B ha letto `persist.ts` per intero e descrive la scrittura a `:79-112`). `persist.ts` non compare tra i chiamanti di `deleteFile` trovati da graphify: nessun'altra cancellazione dei file chat nell'ambito cercato. Nessuna ricerca è stata fatta sulla cancellazione dei file `agent-sessions/`.
- Rispetto all'ipotesi della prima estrazione (ricomparsa di chat cancellate perché `saveChatHistory` non elimina i file orfani): la rimozione fisica esiste, ma solo in questo gestore, senza attesa e con errore ignorato. Se la cancellazione fallisce in silenzio (per esempio file bloccato su Windows, dopo i tentativi di `delete_file`), il file orfano resta. Se l'indice è assente o vuoto al caricamento successivo, la ricostruzione da `chats/*.json` (fetta B, prima estrazione) potrebbe riproporlo: deduzione, non provata.

## `append_turn`: chiamanti e identificativo di sessione

- **Chiamanti di produzione, tre:** `lib.rs:128` [^src: src-tauri/src/lib.rs:95-135], `lib.rs:235` [^src: src-tauri/src/lib.rs:185-240] e `api_server.rs:2076` [^src: src-tauri/src/api_server.rs:2069-2080]. `agent/runtime.rs` **non** è un chiamante: la ricerca testuale su `append_turn(` trova solo `session.rs` (definizione e test), questi tre punti. L'ipotesi del gap `llm-wiki-persistenza-codice-non-letto` va corretta.
- La prima è la variante sincrona (`result?` poi accodamento), la seconda quella in streaming (task in background con sink di eventi, accodamento solo nel ramo di successo). Il nome della funzione contenitore non è nelle finestre; l'associazione con `agent_start_turn` e `agent_start_turn_stream`, registrati a `lib.rs:665-666`, è una deduzione dalla forma.
- **Identificativo di sessione:** tutti e tre passano `response.session_id`, cioè l'id restituito nella risposta del runtime, insieme a `project.id` e `project.path`, senza trasformazioni visibili. L'accodamento avviene solo se la richiesta ha il flag `persist_session`. I turni in errore non sono accodati.
- **Origine dell'id** (variabili `session_id` e `active_session_id`, usate prima della risposta per leggere i messaggi recenti e registrare la cancellazione): nasce prima delle finestre. **Non verificato** se venga dal client o sia generato dal backend. La rotta `chat/{session_id}/cancel` prende l'id da un segmento dell'URL [^src: src-tauri/src/api_server.rs:390-391].
- **Sanitizzazione:** non nei chiamanti. Per la prima estrazione avviene nello store (`session.rs`: «l'id viene sanitizzato»); la regola non è documentata, resta il gap `llm-wiki-id-chat-sessione`.

## Vecchio formato vettoriale (v1): chiamanti

- `vector_upsert` e `vector_delete` sono nell'elenco dei comandi esposti al frontend [^src: src-tauri/src/lib.rs:672,674] (l'apertura del macro che li raccoglie è fuori finestra). Accanto compaiono anche i comandi v1 `vector_search` e `vector_count`.
- **Nessun chiamante nell'ambito cercato.** Nessuna invocazione per nome nel TS non di test (ricerca sulla stringa esatta); in Rust, con confine di parola, compaiono solo nelle definizioni e nei test di `vectorstore.rs` (`:151,156`, `:278-279`, test da `:1291`) e nella registrazione di `lib.rs`. Fuori ambito: `mcp-server`, tool, estensione.
- Quindi il percorso di scrittura e di cancellazione v1 è raggiungibile solo da un chiamante esterno al sorgente cercato (il comando è comunque esposto): non risulta usato dall'applicazione. La cancellazione della tabella v1 avviene invece con `vector_drop_legacy` (righe 2 della tabella).

## Endpoint dell'API locale che scrivono o cancellano

La tabella delle rotte di `handle_request` è completa e chiusa da un 404 [^src: src-tauri/src/api_server.rs:360-395]. Nessuna rotta cancella pagine o file.

| Rotta | Gestore | Archivio toccato | Stato |
|---|---|---|---|
| `PATCH projects/{id}/reviews/{review}` | `handle_patch_review` → `patch_review_item` | `.llm-wiki/review.json`: imposta `resolved` e, se presente, `resolvedAction`, lavorando sull'array grezzo per non perdere i campi sconosciuti | Gestore letto; la chiamata di scrittura è oltre la finestra [^src: src-tauri/src/api_server.rs:1572-1604,1680-1700] |
| `DELETE projects/{id}/reviews/{review}` | `handle_delete_review` → `delete_review_item` | `review.json`: toglie la voce con quell'id; se non c'è risponde 404; scrive tramite `write_raw_review_array` (meccanismo non letto) | Letto [^src: src-tauri/src/api_server.rs:1616-1649] |
| `POST projects/{id}/reviews/resolve` | `handle_bulk_resolve_reviews` → `resolve_review_items` | `review.json`: risolve molte voci; successo parziale con 200 | Gestore letto, helper non letto [^src: src-tauri/src/api_server.rs:1651-1678] |
| `POST projects/{id}/pages/write` | `handle_write_page` → `write_wiki_page_verified` (in `agent/tools.rs`) | Una pagina `.md` del progetto; il rifiuto di sovrascrivere diventa 409, errori su percorso, tipo file o dimensione 400, altri 500 | Gestore letto; la funzione di scrittura (cartelle ammesse, atomicità, indice, log) **non letta** [^src: src-tauri/src/api_server.rs:1840-1878] |
| `POST projects/{id}/chat` | `handle_chat`, `persist_chat_response` | `agent-sessions/<id>.json` via `append_turn` (`:2076`) | Letto in parte; un turno può usare strumenti di scrittura (policy e `tools.rs` non letti) |
| `POST projects/{id}/pages/embed` | `handle_embed_page` | Indice vettoriale (per la prima estrazione, strumento `llm_wiki_embed_page`) | Corpo non letto |
| `POST projects/{id}/sources/rescan` | `handle_rescan` | Non verificato | Corpo non letto |

Il token è richiesto sempre per chat, scrittura pagina ed embed, anche con accesso non autenticato (fetta A). Nei corpi letti dei gestori delle review non c'è alcuna emissione di eventi verso l'interfaccia: se l'app è aperta, lo store in memoria non vede la modifica e un'auto-save successiva (innescata da modifiche allo store) potrebbe riscrivere `review.json` con lo stato precedente. È una deduzione, valida per le righe lette.

## Cancellazioni e copie nella scrittura generica (`fs.rs`)

[^src: src-tauri/src/commands/fs.rs:1660-1790]
- **`delete_file`:** marca il percorso come scrittura dell'app (il watcher la ignora) prima e dopo; se è una directory usa la cancellazione ricorsiva, altrimenti cancella il file. Il percorso passa da `remove_path_with_retry`: fino a 4 tentativi con attese di 250, 500 e 1000 ms, solo su errori transitori tipici di Windows (file in uso, permesso negato). Nessun controllo che il percorso sia dentro il progetto nelle righe lette; `run_guarded` non è nella finestra. Il wrapper TS invoca il comando a `fs.ts:113` (mappa); è l'unico punto di invocazione per nome. Chiamanti del wrapper `deleteFile` (graphify): `AgentFileActivity`, `ConversationSidebar`, `ReviewView`, `executeMerge` (`dedup-runner.ts:465`), `clearGenerationCheckpoint` (`ingest.ts:3103`), `clearLongSourceCheckpoint` (`:3162`), `migrateExactLegacySourceSummaryIfSafe` (`:1965`), `migrateLegacySourceSummaryIfSafe` (`:1918`), `moveParsedMarkdown` (`parsed-source-output.ts:102`), `removeParsedMarkdown` (`:78`), `cleanupDeletedWikiPages`, `deleteSourceFiles`, `deleteSourceFolder`, `migrateSourcePath`, `cascadeDeleteWikiPage`.
- **`copy_file`:** crea le cartelle padre, marca la destinazione e copia: **sovrascrive** la destinazione se esiste (comportamento della copia standard), senza controllo di esistenza visibile. Non atomica.
- **`copy_directory`:** copia ricorsiva; salta le voci il cui nome inizia con un punto (quindi `.cache` e `.llm-wiki`); sovrascrive i file esistenti; restituisce l'elenco dei file copiati. Se l'origine non è una directory, errore.
- Wrapper TS: invocazioni a `fs.ts:98` e `:105` (mappa). Chiamanti dei wrapper di copia: **non verificato** (non cercati).

## Operazioni distruttive non presenti nella tabella wiki

Input per `wiki-keeper`; la wiki non è toccata. Stato come sopra («letto» o «solo mappa»).

| Operazione | Archivio toccato | Chiamante o innesco | Osservazioni |
|---|---|---|---|
| `delete_file` / `deleteFile` | file e cartelle del progetto (ricorsiva sulle directory) | elenco nella sezione precedente | Nessun controllo di confine visibile nella finestra |
| `remove_path_with_retry` | idem | solo `delete_file` (graphify, `fs.rs:1743,1746`) | 4 tentativi, solo errori transitori Windows |
| `copy_file`, `copy_directory` | destinazione | chiamanti non verificati | Sovrascrivono; `copy_directory` salta le voci con punto |
| `cascadeDeleteWikiPage`, `cascadeDeleteWikiPagesWithRefs` | pagina, embedding, media, riferimenti, `review.json` | tabella «Cascata» sopra | Errori su embedding e media ingoiati |
| `deleteSourceFile(s)`, `deleteSourceFolder` | sorgente, `raw/parsed`, cache, `ingest-cache`, pagine wiki, `wiki/log.md` | UI, watcher, scheduled import | Cancella ogni pagina con unica sorgente |
| `cleanupDeletedWikiPages` | embedding, media, riferimenti nelle pagine | `cleanupDeletedFiles` (`project-file-sync.ts:419`, solo mappa) | Non pota le review |
| `appendSourceDeleteLog` | `wiki/log.md` | `deleteSourceFiles` | Rilettura e riscrittura dell'intero log |
| `migrateSourcePath` | pagine, riepilogo, cache | spostamenti dal watcher | Rollback best effort |
| `removeParsedMarkdown`, `moveParsedMarkdown` | `raw/parsed/<percorso>.md` | `deleteSourceFiles` (`:493`, letto), `migrateSourcePath` (`:211`, letto); definizioni `parsed-source-output.ts:78,102` (graphify, fetta B) | `moveParsedMarkdown` tollera l'errore di cancellazione |
| Azione `delete:<percorso>` delle review | un file del progetto | interfaccia: bottone di una review [^src: src/components/review/review-view.tsx:185-200] | `deleteFile` diretto: nessuna cascata (embedding e indice restano), nessuna validazione del percorso nella finestra; l'origine delle stringhe di azione non è nella finestra |
| Annullamento delle modifiche dell'agente | file creato dall'agente, oppure ripristino del contenuto precedente | interfaccia: `AgentFileActivity` [^src: src/components/chat/agent-file-activity.tsx:30-50] | Solo se il contenuto attuale coincide con quello scritto dall'agente; altrimenti errore di conflitto |
| `PATCH`, `DELETE`, bulk delle review | `review.json` | endpoint API | Vedi sezione endpoint |
| `POST pages/write` | pagina `.md` | endpoint API | Funzione di scrittura non letta |
| Cancellazione del file di chat | `chats/<id>.json` | `ConversationSidebar` | Senza attesa, errore ignorato |
| Checkpoint di ingest | `ingest-progress/…`, `ingest-generation/…` | `clearGenerationCheckpoint` (`ingest.ts:3103`), `clearLongSourceCheckpoint` (`:3162`), a ingest riuscito (fetta B) | Solo mappa per i chiamanti diretti |
| Migrazione di riepiloghi legacy | vecchio riepilogo | `migrateLegacySourceSummaryIfSafe` (`ingest.ts:1918`), `migrateExactLegacySourceSummaryIfSafe` (`:1965`) | Cancella il vecchio file (fetta B, solo mappa per i chiamanti) |
| Merge di duplicati | pagina unita | `executeMerge` (`dedup-runner.ts:465`) | `deleteFile` diretto per graphify; fetta B ha letto `:466-479` (riscrittura di `index.md`) |
| `pruneDeletedPagesFromReviews` | `review.json` | solo `cascadeDeleteWikiPagesWithRefs` | Riscrive il file |

## Copertura del gap `llm-wiki-persistenza-codice-non-letto`

**Coperti dalle tre fette:**
- `wiki-store.ts` (A), `src/commands/fs.ts` (A), `lint-store.ts` (B), `dedup-queue.ts` (B), `wiki-page-delete.ts` (C, intero).
- `lib.rs`: A lo dichiara letto per intero; C ha riaperto tre finestre e ha trovato i chiamanti di `append_turn` e la registrazione di `vector_upsert` e `vector_delete`, che A non riporta. Coperto con questa riserva.
- Cancellazione dei file di chat in `chat-panel.tsx` (C): punto individuato; il resto del file non è letto.
- Chiamanti di `append_turn` (C): risolti senza leggere `agent/runtime.rs`.
- Cascata, ciclo di vita delle sorgenti (parte letta), cancellazioni e copie generiche (C).
- Gap `llm-wiki-vector-v1-chiamanti`: chiuso per l'ambito cercato.

**Ancora scoperti:**
- `file_sync.rs` righe 445-1289 e test.
- `fs.rs`: righe 1385-1659 (compreso un uso di `OpenOptions`), 1791-1839, 1862-1931, 1948-fine e le righe non elencate dalle fette B e C.
- `search.rs` dalla riga 1201.
- `api_server.rs`: corpi di `handle_embed_page`, `handle_chat` e della preparazione, `handle_rescan`, `resolve_review_items`, `read_raw_review_array`, `write_raw_review_array`.
- `agent/runtime.rs` (origine dell'id di sessione) e `agent/tools.rs` (`write_wiki_page_verified`).
- `proxy.rs` dalla riga 261.
- `ingest.ts`: tutte le righe non elencate dalla fetta B.
- `source-lifecycle.ts`: righe 1-136, 236-447, 666-690, 711-fine.
- `sweep-reviews.ts`: parte di scrittura.
- `chat-panel.tsx`: tutto fuori dalle righe 235-265 (fuori ambito).

**File letti.**
- In questa fetta: **16 file** (2 interi, 14 a finestre). Otto erano già citati dalle estrazioni precedenti: `lib.rs`, `api_server.rs`, `fs.rs`, `review-view.tsx`, `ingest-queue.ts`, `embedding.ts`, `maintenance-section.tsx`, `reset-project-state.ts`. Otto sono nuovi: `wiki-page-delete.ts`, `source-lifecycle.ts`, `chat-panel.tsx`, `knowledge-tree.tsx`, `sources-view.tsx`, `activity-panel.tsx`, `agent-file-activity.tsx`, `lint-view.tsx`. La finestra extra di `ingest.ts` (3550-3560) cade nell'intervallo 3485-3584 letto dalla fetta B e non aggiunge un file.
- **`files_sampled` cumulativo: 93, dichiarato come massimo** (85 del manifest dopo la fetta B, più 8). Resta la riserva già usata: l'elenco esatto dei 30 file della prima estrazione non è verificabile, quindi il valore reale può essere più basso. `files_total_in_repo`: 476.
- Byte letti: circa 66 KB.

## Gap evidenti

1. Origine dell'id di sessione (`session_id`, `active_session_id`) e regola di sanitizzazione: non verificati.
2. `write_wiki_page_verified` (`agent/tools.rs`): cartelle ammesse, atomicità, aggiornamento di indice e log. Non letta.
3. Corpi di `handle_embed_page`, `handle_rescan`, `resolve_review_items` e meccanismo di `write_raw_review_array`.
4. Conferma e controlli della cancellazione di pagina orfana in `lint-view.tsx` (la finestra inizia a metà della funzione).
5. Meccanismo di `vector_delete_page` lato Rust sul file di revisione.
6. Chiamanti dei wrapper di copia (`copyFile`, `copyDirectory`), del chiamante di `optimizeChunkVectorTableBestEffort`, delle stringhe non classificate (`embedding.ts:705,731,745`, `auto-save.ts:12,28`).
7. `run_guarded` e l'eventuale controllo di confine in `delete_file`.
8. Cancellazione dei file `agent-sessions/`: non cercata.
9. Il comportamento di `removeTasks` e `cancelAllTasks` oltre la firma e la conferma di interfaccia: corpi non nelle finestre.
10. Origine delle stringhe di azione `delete:<percorso>` delle review (se generate dal modello).
11. Corretto in questo documento rispetto alle fette precedenti: `agent/runtime.rs` non è il chiamante di `append_turn`; la rimozione dei file di chat esiste in `chat-panel.tsx`.

## Note di estrazione

- **Stato**: **partial**. Commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3`, ramo `develop`. La sessione ha verificato prima dell'avvio `status --short` vuoto e HEAD `e08cfce`.
- **Deviazione dalle finestre.** In `src-tauri/src/lib.rs` ho letto le righe 241-251, 11 righe oltre la finestra approvata 185-240: volevo vedere la chiusura della chiamata a `append_turn`. Non le ho usate per alcuna affermazione. Il controllo gitleaks della sessione sui file interi copre anche quelle righe.
- **Elenco dei file del repo aperti, con intervalli:**
  - interi: `src/lib/wiki-page-delete.ts`, `src/lib/reset-project-state.ts`;
  - `src/lib/source-lifecycle.ts`: 137-235, 448-665, 691-710;
  - `src/components/chat/chat-panel.tsx`: 235-265;
  - `src-tauri/src/lib.rs`: 95-135, 185-251, 665-680;
  - `src-tauri/src/api_server.rs`: 360-395, 1572-1700, 1840-1897, 2060-2080;
  - `src-tauri/src/commands/fs.rs`: 1660-1790;
  - `src/components/layout/knowledge-tree.tsx`: 115-135;
  - `src/components/sources/sources-view.tsx`: 290-345;
  - `src/components/layout/activity-panel.tsx`: 170-215;
  - `src/components/review/review-view.tsx`: 185-200;
  - `src/components/chat/agent-file-activity.tsx`: 30-50;
  - `src/lib/ingest-queue.ts`: 265-290, 660-725;
  - `src/lib/embedding.ts`: 250-310, 625-640, 845-860;
  - `src/components/settings/sections/maintenance-section.tsx`: 120-190;
  - `src/components/lint/lint-view.tsx`: 335-350 (extra autorizzata);
  - `src/lib/ingest.ts`: 3550-3560 (extra autorizzata).
- **Segreti.** Letti solo nomi di simboli, percorsi e logica; nessun valore di credenziale nelle finestre, nessun file `.env*` aperto. `secrets_redacted`: 0. Limite: lo zero vale per i file e gli intervalli aperti, non è una scansione dell'intero repo (gap `llm-wiki-scan-credenziali`). La sessione verifica con gitleaks.
- **Istruzioni trovate nei file letti**: nessuna rivolta a un agente e nessuna ostile. Presenti commenti per i manutentori (per esempio sulla conferma in due fasi dell'albero delle sorgenti e sull'ordine delle operazioni di cancellazione), trattati come dato e non eseguiti.
- **Nessuna scrittura** sotto `code_repos/llm_wiki`: l'estrazione è stata solo lettura.
- Le tabelle delle righe «solo mappa» riportano nomi, percorsi e righe della mappa della sessione (graphify/grep), file locale non versionato `.graphify-state/verifiche/2026-11-20-fetta-c-mappa.md`, non fonte normativa.

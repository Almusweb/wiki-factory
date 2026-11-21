---
id: 2026-11-21-repo-llm_wiki-dossier-ep004-r4
type: source
title: Dossier EP-004 r4 da code_repos/llm_wiki, 2026-11-21: rischio 4, atomicità eterogenea delle scritture (repo-sync)
status: draft
created: 2026-11-21
updated: 2026-11-21
sources: ["raw/2026-11-21-repo-llm_wiki-dossier-ep004-r4.md"]
tags: [source, repo, llm-wiki, persistenza, atomicita, windows, ep-004, rischio-4]
---

# Dossier EP-004 r4 da code_repos/llm_wiki, 2026-11-21: rischio 4, atomicità eterogenea delle scritture (repo-sync)
> Estrazione mirata `repo-sync` v2.12 del 2026-11-21 sul commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` (HEAD staccato, nessun ramo; l'hash è quello dichiarato dal richiedente, non riverificato dall'agente, privo di `Bash`), stato `partial`, 13 file letti, sola lettura (Q_003). «Osservato» = letto nel codice (non eseguito); «ereditato» = riportato dalla fetta D e non riletto; «deduzione non testata» = ricavata da fatti osservati, mai vista in esecuzione. Repo di terzi sotto GNU GPL v3: il raw riporta solo nomi di file, simboli e righe, nessun frammento di codice.

## Contesto
Quarto dossier della serie di EP-004 (TSK-022 / US-028), dedicato al rischio 4 di [[llm-wiki-rischi-persistenza]]. Parte dalla tabella di atomicità della fetta D ([[2026-11-21-repo-llm_wiki-persistenza-d]], [[llm-wiki-archivi-persistenza]] §Aggiornamenti fetta D) e dal comportamento sui file corrotti ([[llm-wiki-gestione-file-corrotti]]): **non la ripete**, riporta conferme, correzioni, lacune. Limiti dichiarati in anticipo (TSK-022): garanzie del file system (ordine dei dati dopo un crash, durabilità senza `sync_all`), semantica di `std::fs::rename` su Windows, atomicità interna di LanceDB; nessuno è osservabile per lettura e i sorgenti di `std` e `lancedb` non sono letti. L'agente non aveva `Bash` né `Grep`: un «non trovato» del raw vale solo per le righe lette; la ricerca testuale globale è della sessione principale (sezione a parte). [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r4.md §Identità e perimetro]

## Dettaglio

### Modalità di scrittura riletta, archivio per archivio (osservato)
Righe dal dossier; percorsi relativi alla radice del repo del cliente.

| Archivio | Modalità | Righe | Esito |
|---|---|---|---|
| Revisioni embedding | temporaneo `tmp-<uuid>`, `fs::write`, `fs::rename`; ripiego; rimozione del temporaneo se il target non esiste | `page_embedding.rs:340-376` | **Confermato** atomica, con la finestra sotto |
| `scheduled-import-db.json` | `writeFileAtomic` → `write_file_atomic` (`.<nome>.<nanosecondi>.tmp`, `fs::write`, `fs::rename`, rimozione del temporaneo se la rinomina fallisce) | `scheduled-import.ts:410-422`; `fs.ts:32-35`; `fs.rs:1295-1344` | **Confermato** atomica |
| `lint-config.json` | `writeFileAtomic` | `lint-config.ts:42-49` | **Confermato** atomica |
| `history-settings.json` | `fs::write` diretto dopo il controllo symlink, sotto `HISTORY_LOCK` in processo | `file_history.rs:304-334` | **Confermato** diretta |
| `history/<hash>.json` | `fs::write` diretto (286), anche potatura per file (227-228) | `file_history.rs:234-290, 207-232` | **Confermato** diretta (ripristino 423-424 non riletto) |
| Sessioni agente | `fs::write` diretto (174), esito ignorato (72), mutex in processo (48) | `session.rs:166-175, 39-74` | **Confermato** diretta |
| LanceDB v2 | un `merge_insert` per pagina o `create_table`, sotto lock di scrittura; revisione come secondo passo | `vectorstore.rs:472-547` | Meccanismo **confermato**; atomicità interna **non conclusivo** |
| LanceDB v1 | `delete` con filtro, solo avviso se fallisce, poi `add` | `vectorstore.rs:151-205` | **Confermato** non atomica fra i due passi |
| `app-state.json` | scrittura diretta del plugin | ereditato dalla fetta D | ereditato, non riletto |
| `file-snapshot.json`, `file-change-queue.json` | `write_json`: temporaneo e rinomina; su Windows elimina prima l'originale | `file_sync.rs:1347-1381` | **Confermato** (vedi finestra) |

**Archivi che passano dalla scrittura generica** (perimetro del TSK, non chiusi in fetta D): `write_file` fa `fs::write` sul percorso finale dopo `create_dir_all` e `mark_app_write_path` (`fs.rs:1243-1267`, scrittura a 1258; wrapper TS `fs.ts:22-25`). Chiamanti riletti, tutti **diretti**: `review.json` (`persist.ts:14-18`), `lint.json` (`persist.ts:30-34`), `conversations.json` poi `chats/<id>.json` (`persist.ts:79-112`, indice per primo, poi un file per conversazione: più file in sequenza), `chat-preferences.json` (`persist.ts:244-251`), `ingest-cache.json` (`ingest-cache.ts:47-53`, errore ignorato), `dedup-not-duplicates.json` (`dedup-storage.ts:40-46`), `ingest-queue.json` (`ingest-queue.ts:125-158`, coda di scritture in processo, errore ignorato 149-150). `project.json`: diretta, già letta in r2, ereditata. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r4.md §1. Conferme della tabella di atomicità (fetta D) con riga di codice riletta]

### Che cosa resta dopo un crash e come reagisce il lettore (osservato, salvo dove indicato)
«Troncato o vuoto» è raggiungibile in teoria da `fs::write` (creazione con troncamento, poi scrittura): **deduzione non testata** dal comportamento di `std`, non letto. Per gli archivi atomici un file finale troncato richiederebbe una garanzia del file system non osservabile.

| Archivio | Reazione del lettore a file troncato o illeggibile | Tipo | Impatto sui dati |
|---|---|---|---|
| Sessioni agente | `load_session` → «nessun valore» (`session.rs:160-164`); `append_turn` parte da sessione vuota (54), poi `save_session` sostituisce il file (72, 174); `recent_messages` → vuoto (97-99); `list_sessions` salta il file (117-118) | ripartenza vuota, silenziosa | perdita dello storico di quella sessione (fino a 40 messaggi) alla prossima scrittura; nessun avviso, nessuna copia |
| `history/<hash>.json` | analisi fallita → vettore vuoto (`file_history.rs:267-270`), la scrittura successiva salva solo la voce nuova (274-286); potatura: file non analizzabile → `continue` (221-224) | ripartenza vuota (scrittura), salto (potatura) | perdita delle versioni precedenti di quel file; il file dell'utente non è toccato |
| `history-settings.json` | errore → impostazioni di default (71-81); default `enabled` falso (42-48) | ripiego a default | la cronologia si **disattiva in silenzio** (`record_file_version` esce a 245); con file illeggibile `set_file_history_settings` vede «nessuna impostazione» (318-323) e al salvataggio successivo esegue la potatura (327-329) |
| `review.json`, `lint.json`, `chat-preferences.json` | `catch` → elenco vuoto o default (`persist.ts:20-28, 36-44, 253-260`) | ripartenza vuota | perdita dell'elenco fino al prossimo salvataggio |
| Chat | indice illeggibile → recupero dai file orfani `chats/*.json` (`persist.ts:143-144, 205-242`), titolo dai primi 50 caratteri (199); file di conversazione illeggibile → conversazione senza messaggi (127-129) | ripiego (recupero parziale) | perdita dei titoli originali; messaggi del file troncato persi |
| `ingest-cache.json` | cache vuota (`ingest-cache.ts:32-39`) | ripartenza vuota | solo costo di ri-ingest |
| `dedup-not-duplicates.json` | `[]` (`dedup-storage.ts:19-38`) | ripartenza vuota | perdita della lista «non duplicati» al prossimo salvataggio |
| `ingest-queue.json` | `[]` (`ingest-queue.ts:160-174`) | ripartenza vuota | perdita dei task in coda |
| `lint-config.json` (atomico) | default con avviso in console (`lint-config.ts:31-40`) | ripiego a default | ripristino dei default |
| `scheduled-import-db.json` (atomico) | assente → store vuoto (366-368); non analizzabile → store vuoto con avviso (378-381) | ripartenza vuota | la scansione successiva riconsidera i file come nuovi |
| Revisione `.revision` (atomica) | errore o contenuto vuoto → `None` (`page_embedding.rs:333-338`); confronto con l'impronta (`vectorstore.rs:557-559`) | ripiego | pagina ri-incorporata: solo costo (deduzione non misurata) |
| `file-snapshot.json`, `file-change-queue.json` | file assente → default (`file_sync.rs:1339-1341`); file presente ma non analizzabile → **errore** `Failed to parse` (1344), propagato con `?` ai siti letti (475, 514, 578, 640, 677) | **errore**, non ripartenza vuota | vedi finestra Windows |
| LanceDB v2 e v1 | non determinabile per lettura (ereditato da r6: tabella assente → ricerca vuota; errore → ripiego su parole chiave) | non conclusivo | non conclusivo |
| `app-state.json` | ereditato dalla fetta D: errore ignorato, store vuoto, la prima `set` riscrive con la sola cache | ripartenza vuota (ereditato) | ereditato |

**Osservato, trasversale:** nessun lettore riletto mette in quarantena, copia o segnala all'utente il file illeggibile (al massimo un avviso in console: `lint-config.ts:37`, `scheduled-import.ts:379`). Conferma la «regola generale» di [[llm-wiki-gestione-file-corrotti]]. **Eccezione osservata:** i due file di `file_sync.rs`, dove un file non analizzabile dà errore e non default. **Deduzione non testata:** poiché ai siti letti (475, 640) l'errore di analisi esce prima di ogni scrittura, il file non analizzabile non risulta riscritto da quei percorsi; che l'errore si ripeta a ogni ciclo dipende dai percorsi 705-1280, non letti. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r4.md §2. Che cosa resta dopo un crash e come reagisce il lettore (AC3, AC5)]

### Finestra non atomica su Windows (osservato)
**Dove sta davvero il passaggio.** `embedAllPages` non contiene alcun passo «elimina l'originale e rinomina»: svuota con `drop_table` e riscrive (r6). Nel ramo TS le scritture usano `vector_upsert_chunks` senza revisione, che invalida la revisione con `remove_file` (`vectorstore.rs:467, 542-544`) e non chiama `save_revision`: la finestra di `save_revision` non è attraversata dal rebuild lanciato dalla UI (altri chiamanti non riletti). I punti «elimina l'originale prima della rinomina» osservati dal dossier sono due:

| Punto | Condizione | Sequenza | Righe |
|---|---|---|---|
| `save_revision` | solo se la prima `rename` fallisce **e** il target esiste (commento 355-356: Windows non sostituisce la destinazione) | `remove_file` del target (359), `rename` (362); se la seconda rinomina fallisce, ripristino del vecchio contenuto con `fs::write` **diretto**, esito ignorato (363-365), ritorno di errore (366-368) | `page_embedding.rs:354-374` |
| `write_json` (snapshot e coda) | **sempre su Windows** (`cfg(windows)`), prima di ogni rinomina | se il target esiste: `remove_file` (1368-1370), poi `rename` (1373) | `file_sync.rs:1347-1381` |

Un terzo punto, `rebuild_wiki_index_inner` (`project_maintenance.rs:344-350`), emerge solo dalla ricerca globale (sezione sotto), non dal dossier.

**`write_file_atomic` non ha il passaggio** (osservato): se la rinomina fallisce rimuove il temporaneo e ritorna errore, l'originale resta intatto (`fs.rs:1328-1336`). Non conclusivo: se su Windows `fs::rename` sostituisca la destinazione esistente (semantica di `std`, non letta); se non lo facesse, `lint-config.json` e `scheduled-import-db.json` fallirebbero con errore senza perdere il vecchio file (deduzione non testata). Il commento 355-356 di `save_revision` afferma il contrario per la rinomina semplice: è una dichiarazione degli autori, non una verifica.

**Che cosa vede un lettore concorrente.**
- `write_json`: nella finestra tra 1369 e 1373 il file finale **non esiste**; un lettore che non passa da `with_queue_lock` esegue `read_json`, che per file assente ritorna il default (1339-1341): snapshot o coda vuoti, senza errore. Ai siti letti lettori e scrittore `sync_snapshot_paths` (639-654, scrittura a 653) passano dal lock in processo (lettori 475, 514, 578, 677): nella finestra non vedono lo stato intermedio. Lettori di altri processi o senza lock: non letti. Deduzione non testata: uno snapshot vuoto fa risultare «nuovi» tutti i file al rescan (`enqueue_paths` non letta).
- `save_revision`: nella finestra il file finale non esiste, `load_revision` lo tratta come assente (333-338), il confronto ritorna `None` (557-559): pagina ri-incorporata. La scrittura avviene con il lock di scrittura di `vector_upsert_chunks_inner` (488-489) e `vector_page_revision_match` prende il lock di lettura (555-556): per questo percorso un lettore in processo non vede la finestra. Altri chiamanti di `load_revision` (`pub(crate)`): non letti.
- **Crash dentro la finestra** (deduzione non testata): file finale assente, temporaneo presente. Revisione: costo di ri-incorporare. Snapshot e coda: default al riavvio, silenzioso. Nessun ripristino automatico del file finale dal temporaneo nelle righe lette. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r4.md §3. Finestra non atomica su Windows (AC4)]

### Temporanei orfani (osservato)
Restano file temporanei se: (a) il processo termina fra la scrittura e la rinomina (`fs.rs:1324` e `1328`; `page_embedding.rs:352` e `354`; `file_sync.rs:1364` e `1373`); (b) su Windows `remove_file` di `write_json` fallisce: ritorna errore a 1369-1370 prima del blocco che rimuove il temporaneo (1373-1374); (c) in `save_revision` la seconda rinomina fallisce: ripristina il vecchio contenuto e ritorna errore senza rimuovere il temporaneo (362-368). Nomi: `.<nome>.<nanosecondi>.tmp` (`fs.rs`, `file_sync.rs`) e `<chiave>.tmp-<uuid>` (revisioni). Non letto dal dossier se qualcosa li ripulisce o li conta nelle dimensioni degli archivi (rimanda a US-018). [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r4.md §3.4 Temporanei orfani]

### Correzioni e precisazioni rispetto alla fetta D (C1-C8)
C1: la finestra è in due punti (`save_revision` solo ripiego, `write_json` incondizionata su Windows). C2: `embedAllPages` non la attraversa. C3: `writeFileAtomic` non ha ramo Windows né eliminazione dell'originale. C4: nel ripiego di `save_revision` c'è una seconda scrittura non atomica (ripristino con `fs::write`, esito ignorato, `page_embedding.rs:363-365`). C5: temporanei orfani in tre casi. C6: `history-settings.json` illeggibile **spegne** la cronologia (`file_history.rs:42-48, 71-81, 245`). C7: snapshot e coda: assente → default, presente non analizzabile → errore (`file_sync.rs:1339-1344`). C8: nessuna `sync_all` nelle righe lette di `write_file`, `write_file_atomic`, `write_json`, `save_revision`, `save_session`, scritture di `file_history.rs`. Nessuna dicitura «atomica» o «diretta» della fetta D risulta errata nelle righe rilette. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r4.md §4. Correzioni e precisazioni rispetto alla fetta D (riepilogo)]

### Esito proposto dal dossier
**CONFERMATO per lettura** il meccanismo (scrittura diretta in sessioni agente, cronologia, impostazioni della cronologia e archivi che passano da `write_file`; temporaneo e rinomina in lint-config, import schedulato, revisioni, snapshot e coda di sincronizzazione). **NON CONCLUSIVO** per: (a) quanto spesso un crash lasci un file troncato o vuoto e se un file atomico possa risultare vuoto dopo un'interruzione di corrente; (b) semantica di `rename` su Windows; (c) atomicità interna di LanceDB; (d) lettori e pulizia dei temporanei non letti. **SMENTITI** (due ipotesi del TSK): finestra in `writeFileAtomic` (`fs.rs:1328-1336`); `embedAllPages` che attraversa il ripiego di `save_revision` (`vectorstore.rs:467, 542-544`). Gravità proposta (non decisione): media per sessioni agente (unico archivio senza ricostruzione e con perdita silenziosa), bassa per cache, revisioni e indici derivati, da valutare per le code; decisione a US-033. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r4.md §5. Esito del rischio 4 (AC5, AC6)]

### Ricerca testuale globale (sessione principale, estende i negativi del dossier)
Eseguita su `src-tauri/src` e `src` (espressioni regolari, esclusi i test); il comando è riportato in TSK-022 §Chiusura (la sezione descrive ambito ed esclusioni; qui se ne citano gli esiti):
- **`fsync` quasi assente:** `sync_all`/`sync_data` solo in `agent/tools.rs:790` (`atomic_replace_file`, scritture dell'agente sui file dell'utente) e `project_maintenance.rs:344` (`rebuild_wiki_index_inner`, `index.md`). Nessun archivio di persistenza dell'inventario fa `fsync` prima della rinomina: l'atomicità vale contro il crash del processo, non contro la perdita di alimentazione (garanzia del file system non letta).
- **Siti di rinomina** (`fs::rename`, non test): `agent/tools.rs:798-817`, `page_embedding.rs:354, 362`, `file_sync.rs:1373`, `fs.rs:1328`, `project_maintenance.rs:350`. Il percorso più robusto è `atomic_replace_file` dell'agente (`tools.rs:769-817`): `sync_all`, poi su Windows rinomina dell'originale in un `.bak` e ripristino se la seconda rinomina fallisce. Le scritture degli archivi interni dell'app non usano quel meccanismo.
- **Eliminazione dell'originale prima della rinomina su Windows**, oltre a `file_sync.rs:1366-1372`: anche `project_maintenance.rs:346-349` (`index.md` ricostruito).
- **Nessuna pulizia dei temporanei orfani:** nessun `read_dir`/`remove` su `.tmp`/`tmp-` fuori dai test. **Nessuna quarantena né recupero di file corrotti** (`quarantine`, `.corrupt`, `recover`: solo occorrenze non pertinenti; `.bak` solo in `tools.rs:807`).
- **Volume:** 165 occorrenze di `fs::write(` fuori dai test in `src-tauri/src`: la scrittura diretta è il caso comune.

Restano non coperti: `mcp-server` ed `extension` (la ricerca cita solo `src-tauri/src` e `src`), i test, il comportamento di `std` e LanceDB. [^src: management/kanban/EP-004-verifica-rischi-di-persistenza/US-028-rischio-atomicita-eterogenea/TSK-022.md §Chiusura]

### File letti e non letti
Letti (13, sola lettura): `page_embedding.rs` (300-420), `fs.rs` (1235-1370), `session.rs` (1-217), `file_history.rs` (1-340), `file_sync.rs` (1-130, 445-704, 1280-1421), `vectorstore.rs` (151-206, 452-590), `fs.ts`, `lint-config.ts`, `scheduled-import.ts` (345-440), `persist.ts` (1-260), `ingest-cache.ts` (1-70), `dedup-storage.ts` (1-60), `ingest-queue.ts` (90-200). Non letti: `std` e `lancedb`; `file_sync.rs` 130-445 e 705-1280 (percorsi di scrittura di snapshot e coda, `enqueue_paths`, `process_queue`); `read_file` Rust su file troncato a metà carattere UTF-8; `page_embedding.rs` fuori da 300-420; `file_history.rs` da 340 (ripristino 423-427); `persist.ts` da 260, `project-identity.ts`, `project-store.ts`; sorgenti del plugin store; test sul troncamento. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r4.md §File letti e non letti]

### Controllo del repo e dei segreti dichiarato
L'agente non ha eseguito `git status` né `git log`: il controllo a comando è in TSK-022 §Chiusura (`git -C code_repos/llm_wiki log -1 --format=%h` → `e08cfce`, `status --short` → vuoto; `grep -ciE` sui pattern dei segreti sul dossier → 0). Il dossier ha letto solo file di persistenza e sincronizzazione, nessun valore di credenziale, nessun `.env*`. Nessuna istruzione rivolta a un agente trovata nei file letti. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r4.md §Note di estrazione] [^src: management/kanban/EP-004-verifica-rischi-di-persistenza/US-028-rischio-atomicita-eterogenea/TSK-022.md §Chiusura]

## Pagine collegate
[[llm-wiki-rischi-persistenza]] (§Esito della verifica di US-028), [[llm-wiki-archivi-persistenza]], [[llm-wiki-gestione-file-corrotti]], [[llm-wiki-operazioni-distruttive]], [[2026-11-21-repo-llm_wiki-dossier-ep004-r6]], [[gaps]].

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

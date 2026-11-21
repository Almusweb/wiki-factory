---
source_path: /home/user/wiki-factory/code_repos/llm_wiki
source_type: repo
git_branch: HEAD
git_commit: e08cfce65aad8b76b13546a081c1a8d4422b70c3
extracted_at: 2026-11-21
extractor: repo-sync@2.12.0
scope: dossier EP-004 r4 (TSK-022 / US-028), rischio 4, atomicità eterogenea delle scritture
---

# Specifiche estratte: llm-wiki, dossier EP-004 r4 (rischio 4, atomicità eterogenea)

> Documento generato da `repo-sync` v2.12 il 2026-11-21. Sorgente: `/home/user/wiki-factory/code_repos/llm_wiki`
> @ commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` (HEAD staccato, nessun nome di ramo; l'hash è quello dichiarato dal richiedente e dalle voci di manifest precedenti, non riverificato da questo agente, privo di `Bash`). Read-only verso la sorgente.

## Identità e perimetro

- Estrazione **mirata** (TSK-022 / US-028), per sola lettura del codice (Q_003). Parte dalla tabella di atomicità della fetta D (`raw/2026-11-21-repo-llm_wiki-persistenza-d.md` §Parte B; `wiki/concepts/llm-wiki-archivi-persistenza.md` §Aggiornamenti fetta D e §Esito della verifica di US-015; `wiki/concepts/llm-wiki-gestione-file-corrotti.md`). **Non la ripete**: riporta conferme, correzioni, lacune. Stack e struttura: non ripetuti.
- **Licenza**: repository di terzi, GNU GPL v3. Solo nomi di file, simboli e righe; nessun frammento di codice. Citazioni `[^src: percorso:righe]`, percorsi relativi alla radice del repo.
- «Osservato» = letto nel codice in questa sessione. «Ereditato» = riportato da fetta D o dossier precedenti, **non riletto qui**. «Deduzione non testata» = ricavata da fatti osservati, mai vista in esecuzione. Nessuna esecuzione, nessuna interruzione simulata. Nessuna ricerca testuale globale (l'agente non ha `Bash` né `Grep`): un «non trovato» vale solo per le righe lette di §File letti e non letti.
- **Limiti dichiarati in anticipo (TSK-022)**: (a) garanzie del file system (ordine di scrittura dei dati dopo un crash, durabilità senza `sync_all`); (b) semantica di `std::fs::rename` su Windows; (c) atomicità interna di LanceDB. Nessuno è osservabile per lettura: «non conclusivo» con motivo. I sorgenti di `std`, `lancedb` e delle dipendenze non sono stati letti.

## Ipotesi di partenza (US-028)

Atomici (temporaneo e rinomina): configurazione di lint, database di import schedulato, revisioni di embedding. Non atomici: sessioni agente e cronologia. Per gli altri archivi dipende dalla scrittura generica, chiusa da US-015. Su Windows un passaggio elimina l'originale prima della rinomina.

## 1. Conferme della tabella di atomicità (fetta D) con riga di codice riletta

| Archivio (riga fetta D) | Modalità riletta | Fonte (osservato) | Esito |
|---|---|---|---|
| Revisioni embedding (3) | temporaneo `tmp-<uuid>` (351), `fs::write` (352), `fs::rename` (354); ripiego 357-369; rimozione del temporaneo se il target non esiste (371) | src-tauri/src/commands/page_embedding.rs:340-376 | **CONFERMATO** atomica, con la finestra del §3 |
| `scheduled-import-db.json` (13) | `writeFileAtomic` (421) → `write_file_atomic`: `.<nome>.<nanosecondi>.tmp` (1310-1315), `fs::write` (1324), `fs::rename` (1328), rimozione del temporaneo se la rinomina fallisce (1329) | src/lib/scheduled-import.ts:410-422; src/commands/fs.ts:32-35; src-tauri/src/commands/fs.rs:1295-1344 | **CONFERMATO** atomica |
| `lint-config.json` (9) | `writeFileAtomic` (47) | src/lib/lint-config.ts:42-49 | **CONFERMATO** atomica |
| `history-settings.json` (14) | `fs::write` diretto (326) dopo verifica che non sia symlink (325), sotto `HISTORY_LOCK` (315; lock statico in processo, riga 14) | src-tauri/src/commands/file_history.rs:304-334 | **CONFERMATO** diretta |
| `history/<hash>.json` (15) | `fs::write` diretto (286), anche potatura per file (227-228) | file_history.rs:234-290, 207-232 | **CONFERMATO** diretta (423-424, ripristino: non riletto) |
| Sessioni agente (16) | `fs::write` diretto (174), esito ignorato (72), mutex in processo (48) | src-tauri/src/agent/session.rs:166-175, 39-74 | **CONFERMATO** diretta |
| LanceDB v2 (1) | un `merge_insert` per pagina (513-529) o `create_table` (530-535) sotto lock di scrittura (488-489); revisione come secondo passo (537-544) | src-tauri/src/commands/vectorstore.rs:472-547 | **CONFERMATO** il meccanismo; atomicità interna **NON CONCLUSIVO** (LanceDB non letto) |
| LanceDB v1 (2) | `delete` con filtro (183), solo avviso se fallisce (184-188), poi `add` (190) | vectorstore.rs:151-205 | **CONFERMATO** non atomica fra i due passi |
| `app-state.json` (17) | scrittura diretta del plugin | ereditato dalla fetta D (`store.rs:291-299` del crate `tauri-plugin-store`) | ereditato, non riletto |

**Archivi che dipendono dalla scrittura generica** (perimetro del TSK, non chiusi con righe di lettura in fetta D): `write_file` fa `fs::write` sul percorso finale, dopo `create_dir_all` e `mark_app_write_path` (src-tauri/src/commands/fs.rs:1243-1267, scrittura a 1258). Wrapper TS `writeFile` (src/commands/fs.ts:22-25). I chiamanti riletti:

| Archivio | Chiamante e righe | Modalità |
|---|---|---|
| `review.json` | src/lib/persist.ts:14-18 | diretta |
| `lint.json` | persist.ts:30-34 | diretta |
| `conversations.json` poi `chats/<id>.json` | persist.ts:79-112 (indice a 88-91, poi un file per conversazione 104-111) | diretta, **più file in sequenza**, indice per primo |
| `chat-preferences.json` | persist.ts:244-251 | diretta |
| `ingest-cache.json` | src/lib/ingest-cache.ts:47-53 (errore ignorato) | diretta |
| `dedup-not-duplicates.json` | src/lib/dedup-storage.ts:40-46 | diretta |
| `ingest-queue.json` | src/lib/ingest-queue.ts:125-158 (coda di scritture in processo, errore ignorato 149-150) | diretta |

`project.json`: scrittura diretta già letta in r2 (`project-identity.ts`), ereditata. Esito: **CONFERMATO** diretta per tutti i riletti.

## 2. Che cosa resta dopo un crash e come reagisce il lettore (AC3, AC5)

«Troncato o vuoto» è raggiungibile in teoria da `fs::write` (creazione con troncamento, poi scrittura): **deduzione non testata** dal comportamento di `std`, non letto. Per gli archivi atomici un file finale troncato richiederebbe una garanzia del file system non osservabile (§5).

| Archivio | Stato su disco dopo interruzione in scrittura | Reazione del lettore (osservato) | Tipo di reazione | Impatto sui dati |
|---|---|---|---|---|
| Sessioni agente | file troncato o vuoto | `load_session`: lettura o analisi fallita → «nessun valore» (160-164). `append_turn` parte da sessione vuota (54, `unwrap_or_default`), poi `save_session` sostituisce il file (72, 174). `recent_messages` → vettore vuoto (97-99). `list_sessions` salta il file (117-118) | **ripartenza vuota**, silenziosa | perdita dello storico di quella sessione (fino a 40 messaggi, costante 9) alla prossima scrittura; nessun avviso, nessuna copia |
| Cronologia `history/<hash>.json` | file troncato | `record_file_version`: analisi fallita → vettore vuoto (267-270), la scrittura successiva salva **solo la voce nuova** (274-286). Potatura: file non analizzabile → `continue` (221-224), non toccato. `latest_file_version` → `None` (91-92) | **ripartenza vuota** (scrittura) / **salto** (potatura, provenienza) | perdita delle versioni precedenti di quel file; il file dell'utente non è toccato |
| `history-settings.json` | file troncato | `read_history_settings`: errore → impostazioni di default (71-81); default: `enabled` falso (42-48) | **ripiego a default** | la cronologia dei file si **disattiva in silenzio** (`record_file_version` esce a 245); in più `set_file_history_settings` con file illeggibile considera «nessuna impostazione» (318-323) e al salvataggio successivo esegue la potatura (327-329) |
| `review.json`, `lint.json`, `chat-preferences.json` | file troncato | `catch` → elenco vuoto o default (persist.ts:20-28, 36-44; preferenze 253-260, riga non oltre letta) | **ripartenza vuota** | perdita dell'elenco fino al prossimo salvataggio, che lo sostituisce |
| Chat | `conversations.json` troncato, oppure indice nuovo e file di conversazione vecchi (interruzione fra 88 e 104-111) | indice illeggibile → `catch` (143) → recupero dai file orfani `chats/*.json` (144, 205-242), titolo dai primi 50 caratteri (199); file di una conversazione illeggibile → saltato, la conversazione compare senza messaggi (127-129); recupero: file corrotto ignorato uno a uno (232-234) | **ripiego** (recupero parziale) | perdita dei titoli originali; messaggi del file troncato persi |
| `ingest-cache.json` | file troncato | `loadCache` → cache vuota (32-39) | **ripartenza vuota** | solo costo di ri-ingest |
| `dedup-not-duplicates.json` | file troncato | `[]` (dedup-storage.ts:19-38) | **ripartenza vuota** | perdita della lista «non duplicati» al prossimo salvataggio |
| `ingest-queue.json` | file troncato | `loadQueue` → `[]` (ingest-queue.ts:160-174) | **ripartenza vuota** | perdita dei task in coda |
| `lint-config.json` | (atomico) | `loadLintConfig` → default con avviso in console (lint-config.ts:31-40) | **ripiego a default** | ripristino dei default |
| `scheduled-import-db.json` | (atomico) | file assente → store vuoto (366-368); non analizzabile → store vuoto con avviso (378-381) | **ripartenza vuota** | la scansione successiva riconsidera i file come nuovi |
| Revisione `.revision` | (atomica); nella finestra Windows: assente o ripristinata con scrittura diretta | `load_revision`: errore di lettura o contenuto vuoto → `None` (333-338); confronto con l'impronta (vectorstore.rs:557-559) | **ripiego**: la pagina è ri-incorporata | solo costo, nessuna perdita (deduzione sul costo non misurato) |
| `file-snapshot.json`, `file-change-queue.json` | (atomici); su Windows finestra del §3 | `read_json`: file assente → default (file_sync.rs:1339-1341); file presente ma non analizzabile → **errore** `Failed to parse` (1344), propagato con `?` ai siti letti (475, 514, 578, 640, 677) | **errore** (non ripartenza vuota) | vedi §3 |
| LanceDB v2 e v1 | non determinabile per lettura | vedi r6 §6 (ereditato): tabella assente → ricerca vuota; errore → ripiego su parole chiave | **non conclusivo** per lo stato su disco | non conclusivo |
| `app-state.json` | ereditato dalla fetta D | plugin ignora l'errore di caricamento, store vuoto; prima `set` riscrive con la sola cache | ripartenza vuota (ereditato) | ereditato |

**Osservato, trasversale**: nessuno dei lettori riletti mette in quarantena, copia o segnala all'utente il file illeggibile (al massimo un avviso in console: lint-config.ts:37, scheduled-import.ts:379). Conferma la «regola generale» della wiki. **Eccezione osservata**: i due file di `file_sync.rs`, dove un file non analizzabile produce errore e non default.

**Deduzione non testata**: poiché in `file_sync.rs` ai siti letti l'errore di analisi esce prima di ogni scrittura (475, 640), il file non analizzabile non risulta riscritto da quei percorsi; che una ripetizione dell'errore resti a ogni ciclo dipende dai percorsi di scrittura 705-1280, **non letti**.

## 3. Finestra non atomica su Windows (AC4)

### 3.1 Correzione del perimetro: dove sta davvero il passaggio

La formulazione del TSK («`embedAllPages`/ricostruzione dell'indice») va precisata:

1. **`embedAllPages` non contiene** alcun passo di eliminazione dell'originale e rinomina: svuota con `drop_table` e riscrive (r6 §1, ereditato). Nel ramo TS le scritture usano `vector_upsert_chunks` senza revisione, che **invalida** la revisione con `remove_file` (vectorstore.rs:467, 542-544) e **non** chiama `save_revision`. Quindi la finestra di `save_revision` non è attraversata dal rebuild lanciato dalla UI (osservato per le righe indicate; altri chiamanti di `embedAllPages` e la via Rust `vector_upsert_chunks_with_revision` da `page_embedding.rs`: non riletti).
2. I passaggi «elimina l'originale prima della rinomina» osservati sono **due**:

| Punto | Condizione | Sequenza osservata | Fonte |
|---|---|---|---|
| `save_revision` (revisioni di embedding) | **solo se** la prima `rename` fallisce **e** il target esiste (commento 355-356: Windows non sostituisce la destinazione) | `remove_file` del target (359) poi `rename` (362); se la seconda rinomina fallisce: ripristino del vecchio contenuto con `fs::write` **diretto**, esito ignorato (363-365), ritorno di errore (366-368) | page_embedding.rs:354-374 |
| `write_json` (`file-snapshot.json` e `file-change-queue.json`) | **sempre su Windows** (`cfg(windows)`), prima di ogni rinomina | se il target esiste: `remove_file` (1368-1370), poi `rename` (1373) | src-tauri/src/commands/file_sync.rs:1347-1381 |

Quindi quella che la wiki chiama «ricostruzione dell'indice» è, per il file-snapshot e la coda di sincronizzazione, **`write_json`**, non il ramo di `save_revision`. La fetta D («finestra non atomica nel solo ramo di ripiego», riga 3) è **confermata** per `save_revision`; la finestra **incondizionata** su Windows di `write_json` era nella wiki come dicitura generale (US-015, «altri scrittori») ma **senza righe**: ora ha le righe.

### 3.2 `write_file_atomic` (`writeFileAtomic`) non ha il passaggio

**Osservato**: `write_file_atomic` (fs.rs:1295-1344) non elimina mai l'originale: se la rinomina fallisce rimuove il temporaneo e ritorna errore (1328-1336), l'originale resta intatto. **Smentita** dell'ipotesi del TSK («finestra non atomica in `writeFileAtomic` di `fs.rs`») nel codice letto. **Non conclusivo**: se su Windows `fs::rename` sostituisca la destinazione esistente (semantica di `std`, non letta); se non lo facesse, `lint-config.json` e `scheduled-import-db.json` fallirebbero con errore senza perdere il vecchio file (deduzione non testata). Il commento di `save_revision` (355-356) afferma il contrario per la rinomina semplice: è una dichiarazione degli autori, non una verifica.

### 3.3 Che cosa vede un lettore concorrente nella finestra

- **`write_json`** (osservato): nella finestra tra 1369 e 1373 il file finale **non esiste**. Un lettore che non passa da `with_queue_lock` esegue `read_json`, che per file assente ritorna il valore di default (1339-1341): **snapshot o coda vuoti, senza errore**. Ai siti letti i lettori **e** lo scrittore `sync_snapshot_paths` passano dal lock in processo (lettori 475, 514, 578, 677; scrittore 639-654, scrittura a 653): nella finestra non vedono lo stato intermedio. Lettori di altri processi o altre vie senza il lock: non letti. **Deduzione non testata**: uno snapshot vuoto fa risultare «nuovi» tutti i file al rescan (la logica di `enqueue_paths` non è stata letta).
- **`save_revision`** (osservato): nella finestra il file finale non esiste; `load_revision` lo tratta come assente (333-338) e il confronto ritorna `None` (557-559): pagina ri-incorporata. La scrittura avviene mentre `vector_upsert_chunks_inner` tiene il lock di scrittura (488-489, rilasciato a fine funzione), e `vector_page_revision_match` prende il lock di lettura (555-556): per **questo** percorso un lettore in processo non vede la finestra. Altri chiamanti di `load_revision` (visibilità `pub(crate)`): non letti.
- **Crash dentro la finestra** (deduzione non testata): file finale assente, temporaneo presente. Per la revisione: costo di ri-incorporare. Per snapshot e coda: default al riavvio (silenzioso). Non esiste ripristino automatico del file finale dal temporaneo nelle righe lette.

### 3.4 Temporanei orfani

**Osservato**: restano file temporanei se (a) il processo termina fra la scrittura e la rinomina (fs.rs:1324 e 1328; page_embedding.rs:352 e 354; file_sync.rs:1364 e 1373); (b) su Windows `remove_file` di `write_json` fallisce: ritorna errore a 1369-1370 **prima** del blocco che rimuove il temporaneo (1373-1374), che quindi resta; (c) in `save_revision` la seconda rinomina fallisce: ripristina il vecchio contenuto e ritorna errore **senza** rimuovere il temporaneo (362-368). Nomi: `.<nome>.<nanosecondi>.tmp` (fs.rs, file_sync.rs) e `<chiave>.tmp-<uuid>` (revisioni). **Non letto**: se qualcosa li ripulisce o li conta nelle dimensioni degli archivi (rimanda a US-018).

## 4. Correzioni e precisazioni rispetto alla fetta D (riepilogo)

| # | Correzione o precisazione | Tipo | Fonte |
|---|---|---|---|
| C1 | La finestra non atomica è in **due** punti, non in «una ricostruzione dell'indice»: `save_revision` (solo ripiego) e `write_json` (incondizionata su Windows) | precisazione con righe | page_embedding.rs:354-374; file_sync.rs:1366-1372 |
| C2 | `embedAllPages` non la attraversa (non chiama `save_revision`) | correzione del perimetro del TSK | vectorstore.rs:467, 542-544 |
| C3 | `writeFileAtomic` non ha ramo Windows né eliminazione dell'originale | correzione dell'ipotesi del TSK | fs.rs:1328-1336 |
| C4 | Nel ripiego di `save_revision` c'è una **seconda** scrittura non atomica (ripristino del vecchio contenuto con `fs::write`, esito ignorato) | aggiunta | page_embedding.rs:363-365 |
| C5 | Temporanei orfani in tre casi, incluso l'errore di `remove_file` di `write_json` e il fallimento della seconda rinomina di `save_revision` | aggiunta | §3.4 |
| C6 | `history-settings.json` illeggibile: il default **spegne** la cronologia (`enabled` falso), non è un default neutro | precisazione dell'impatto | file_history.rs:42-48, 71-81, 245 |
| C7 | `file-snapshot.json`/`file-change-queue.json`: file assente → default, file presente non analizzabile → errore (asimmetria) | precisazione con righe | file_sync.rs:1339-1344 |
| C8 | Nessuna `sync_all` nelle righe lette di `write_file`, `write_file_atomic`, `write_json`, `save_revision`, `save_session`, scritture di `file_history.rs` | conferma della fetta D, per le righe lette | fs.rs:1243-1344; file_sync.rs:1347-1381; page_embedding.rs:340-376; session.rs:166-175; file_history.rs:285-288, 326 |

Nessuna dicitura «atomica» o «diretta» della fetta D risulta **errata** nelle righe rilette.

## 5. Esito del rischio 4 (AC5, AC6)

**Esito proposto: CONFERMATO per lettura** il meccanismo (scrittura diretta in sessioni agente, cronologia, impostazioni della cronologia e negli archivi che passano da `write_file`; temporaneo e rinomina in lint-config, import schedulato, revisioni, snapshot e coda di sincronizzazione). **NON CONCLUSIVO** per: (a) quanto spesso un crash lasci davvero un file troncato o vuoto, e se un file atomico possa risultare vuoto dopo un'interruzione di corrente (garanzie del file system, nessun `sync_all` nelle righe lette); (b) semantica di `rename` su Windows; (c) atomicità interna di LanceDB; (d) lettori e pulizia dei temporanei non letti.

| # | Punto | Esito | Livello | Evidenza | Impatto sui dati |
|---|---|---|---|---|---|
| 1 | Sessioni agente: scrittura diretta; lettore → sessione vuota | **CONFERMATO** | osservato | session.rs:54, 72, 97-99, 160-164, 174 | perdita dello storico della sessione al turno successivo; alto per il singolo utente, nessuna copia |
| 2 | Cronologia `history/<hash>.json`: diretta; lettore → vuoto, riscrittura con la sola voce nuova | **CONFERMATO** | osservato | file_history.rs:221-224, 267-270, 285-288 | perdita delle versioni precedenti del file; il file utente non è toccato |
| 3 | `history-settings.json`: diretta; lettore → default (cronologia spenta) | **CONFERMATO** | osservato | file_history.rs:42-48, 71-81, 324-326 | funzione disattivata in silenzio; non perde dati esistenti |
| 4 | Archivi via `write_file`: diretti; lettori → vuoto o default | **CONFERMATO** | osservato | fs.rs:1258; persist.ts, ingest-cache.ts, dedup-storage.ts, ingest-queue.ts (§1, §2) | perdita di elenchi e code fino al salvataggio successivo; chat parzialmente recuperabile |
| 5 | lint-config e import schedulato: atomici | **CONFERMATO** | osservato | fs.rs:1295-1344 | nessuna perdita nel meccanismo; troncamento da FS **non conclusivo** |
| 6 | Revisioni embedding: atomiche con ripiego Windows | **CONFERMATO** | osservato | page_embedding.rs:340-376 | solo costo di ri-embedding |
| 7 | Finestra `write_json` su Windows: file finale assente, lettore senza lock vede default | **CONFERMATO** (codice); effetto su disco dopo crash: deduzione non testata | osservato / deduzione | file_sync.rs:1366-1372, 1339-1341 | snapshot e coda vuoti al riavvio, silenzioso |
| 8 | Finestra in `writeFileAtomic` | **SMENTITO** nel codice letto | osservato | fs.rs:1328-1336 | — |
| 9 | `embedAllPages` attraversa il ripiego di `save_revision` | **SMENTITO** per il ramo TS | osservato | vectorstore.rs:467, 542-544 | — |
| 10 | Rinomina su Windows sostituisce o no la destinazione | **NON CONCLUSIVO** | — | `std` non letto | — |
| 11 | Troncamento reale dopo crash o spegnimento (file system, assenza di `sync_all`) | **NON CONCLUSIVO** | — | garanzie del FS non osservabili | — |
| 12 | LanceDB v2/v1: stato dopo interruzione | **NON CONCLUSIVO** | — | `lancedb` non letto; v1 `delete`+`add` non atomico (vectorstore.rs:183-190) | indice derivato, ricostruibile (r6) |
| 13 | `app-state.json` | ereditato dalla fetta D (non atomica, store vuoto su file corrotto) | ereditato | persistenza-d §Esiti A | ereditato |

**Gravità proposta (non decisione)**: media per sessioni agente (unico archivio senza ricostruzione e con perdita silenziosa); bassa per cache, revisioni e indici derivati; da valutare per le code (`ingest-queue.json`). Decisione sulle scritture atomiche: a US-033.

## File letti e non letti

**Repo del cliente, letti in questa sessione (13 file, sola lettura)**:
- `src-tauri/src/commands/page_embedding.rs` (300-420)
- `src-tauri/src/commands/fs.rs` (1235-1370)
- `src-tauri/src/agent/session.rs` (1-217)
- `src-tauri/src/commands/file_history.rs` (1-340)
- `src-tauri/src/commands/file_sync.rs` (1-130, 445-704, 1280-1421)
- `src-tauri/src/commands/vectorstore.rs` (151-206, 452-590)
- `src/commands/fs.ts` (intero)
- `src/lib/lint-config.ts` (intero)
- `src/lib/scheduled-import.ts` (345-440)
- `src/lib/persist.ts` (1-260)
- `src/lib/ingest-cache.ts` (1-70)
- `src/lib/dedup-storage.ts` (1-60)
- `src/lib/ingest-queue.ts` (90-200)

Letti come contesto factory: TSK-022, US-028, dossier r6, fetta D, `wiki/concepts/llm-wiki-archivi-persistenza.md`, `wiki/concepts/llm-wiki-gestione-file-corrotti.md`, manifest.

**Non letti, con motivo**:
- `std` (`fs::write`, `fs::rename` su Windows) e `lancedb`: fuori dal repo; esiti non conclusivi.
- `file_sync.rs` 130-445 e 705-1280: percorsi di scrittura di snapshot e coda, `enqueue_paths`, `process_queue`: non si sa se un file non analizzabile venga mai riscritto né come l'errore sia gestito dai chiamanti.
- `fs.rs` `read_file`: comportamento su file troncato a metà carattere UTF-8 (errore vs sostituzione): i lettori TS riletti catturano qualsiasi errore.
- `page_embedding.rs` fuori da 300-420: chiamanti di `vector_upsert_chunks_with_revision` e di `load_revision`.
- `file_history.rs` 340 in poi (ripristino 423-427, elenco): righe 423-424 della fetta D non riverificate.
- `persist.ts` 260 in poi (resto delle preferenze), `project-identity.ts` (r2), `project-store.ts`, sorgenti del plugin store (fetta D).
- Pulizia dei temporanei orfani (`.tmp`, `tmp-`): nessun codice trovato nelle righe lette; non è un «non esiste».
- Test che fissino il comportamento su file troncato (`session.rs` righe 211+, test di `file_history.rs`, `file_sync.rs`).

## Gap evidenti

1. Atomicità effettiva e stato dopo un crash: file system, rinomina su Windows, LanceDB (non conclusivo).
2. Percorsi di scrittura di `file_sync.rs` 705-1280: se un file di snapshot o coda non analizzabile resti tale.
3. Pulizia e conteggio dei temporanei orfani.
4. Altri chiamanti di `load_revision` e `save_revision` senza il lock di `vectorstore_v2_lock`.
5. Comportamento di `read_file` Rust su file troncato.
6. Frequenza reale di crash o chiusure durante la scrittura (nessuna misura).
7. Chiamanti applicativi dei comandi v1 (`vector_upsert`), da US-016.

## Stringhe esatte da cercare (ricerca testuale globale, da eseguire dal chiamante)

Cartelle `src/`, `src-tauri/src/` e, se presenti, `mcp-server/`, `extension/`; per ciascuna: conteggio e file. Usare espressioni larghe.

1. Scritture dirette Rust: `fs::write`, `std::fs::write`, `File::create`, `OpenOptions`, `write_all`, `fs::copy` (tutti gli scrittori non atomici, anche non in inventario)
2. Atomicità e flush: `fs::rename`, `rename(`, `sync_all`, `sync_data`, `persist(`, `tempfile`, `NamedTempFile`, `.tmp`, `tmp-` (altre scritture atomiche; dove manca il flush)
3. Windows: `cfg(windows)`, `cfg!(windows)`, `target_os = "windows"`, `MOVEFILE`, `ReplaceFile` (altri rami Windows di sostituzione)
4. Eliminazione prima di sostituire: `remove_file` e `fs::remove_file` nelle stesse funzioni di `rename`
5. TS: `writeFile(`, `writeFileAtomic(`, `writeFileBase64(`, `write_file`, `write_file_atomic`, `invoke("write_file` (chi scrive con quale garanzia)
6. Revisioni: `save_revision`, `load_revision`, `invalidate_page_revision`, `vector_upsert_chunks_with_revision`, `embedding-revisions`, `REVISION_DIR`, `.revision`
7. Sincronizzazione: `write_json`, `read_json`, `write_snapshot`, `write_queue`, `read_snapshot`, `read_queue`, `with_queue_lock`, `QUEUE_LOCKS`
8. Sessioni: `save_session`, `load_session`, `append_turn`, `agent-sessions`, `unwrap_or_default`
9. Cronologia: `record_file_version`, `prune_history_store`, `prune_entries_per_file`, `history_files_oldest_first`, `read_history_settings`, `HISTORY_LOCK`, `history-settings`
10. Lettori con ripiego: `JSON.parse(` seguito da `catch`, `serde_json::from_str`, `.ok()?`, `unwrap_or_default`, `Failed to parse` (confronto fra ripartenza vuota ed errore)
11. Pulizia e recupero: `.tmp`, `tmp-` insieme a `read_dir`, `remove_dir_all`, `quarantine`, `.corrupt`, `.bak`, `backup`, `recover` (qualunque ripulitura o recupero dei temporanei e dei file corrotti)
12. Test: `file_history`, `append_turn`, `write_json`, `save_revision` dentro `mod tests` e file `*.test.ts` (test sul troncamento)

## Note di estrazione

- **Stato**: **partial**. Commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` come da richiesta e voci di manifest precedenti; ramo non rilevato (HEAD staccato).
- **Gate**: Fase 1 e Fase 4 assolte dall'approvazione dell'utente in chat per il solo perimetro del TSK-022; nessuna conferma separata. Dedup: la voce `2026-11-21-repo-llm_wiki-dossier-ep004-r4` non esisteva nel manifest.
- **Controllo repo invariato**: questo agente non ha `Bash` e **non ha eseguito** `git -C code_repos/llm_wiki status --short` né `git log -1`. Nessuna scrittura sotto `code_repos/llm_wiki`. Il controllo a comando della DoD resta da eseguire dal chiamante.
- **Controllo segreti**: controllo per lettura dei 13 file elencati; nessun valore di credenziale incontrato (i file sono di persistenza e sincronizzazione; nessun `.env*` aperto). Segreti redatti: 0 (vale per le finestre lette, non è una scansione dell'intero repo).
- **Istruzioni trovate nei file letti**: nessuna rivolta a un agente; solo commenti per i manutentori, non eseguiti.
- **Nessuna scrittura** in `wiki/` né nel kanban.

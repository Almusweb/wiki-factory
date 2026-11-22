---
id: llm-wiki-sincronizzazione-file
type: concept
title: llm-wiki — sincronizzazione e osservazione dei file
status: draft
created: 2026-11-20
updated: 2026-11-21
sources: ["raw/2026-11-20-repo-llm_wiki-persistenza-b.md", "raw/2026-11-21-issues-llm_wiki-chiuse.md"]
tags: [llm-wiki, dati, persistenza, sync, db]
---

# llm-wiki — sincronizzazione e osservazione dei file
> Il backend osserva la radice del progetto e persiste in `.llm-wiki/` uno snapshot e una coda di task di cambio file; il frontend ascolta gli eventi e accoda l'ingest per `raw/sources`.

## Contesto
Pagina ricavata dalla fetta B dell'estrazione mirata sulla persistenza (commit `e08cfce`, ramo `develop`). Il tema non aveva una casa: [[llm-wiki-struttura-e-moduli]] cita `file_sync` solo per nome e [[llm-wiki-archivi-persistenza]] tratta i due file come archivi, non il comportamento. Letti `file_sync.rs` alle righe 1-444 e 1290-1409; i corpi di scansione e di `process_queue` non sono letti. «Osservato» indica lettura nel codice; gli indici di riga della sessione valgono per la stringa cercata e uno zero non dimostra l'assenza. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Identità e perimetro]

## Dettaglio

### Moduli
Il backend sta in `src-tauri/src/commands/file_sync.rs`; lato frontend ci sono il wrapper `src/commands/file-sync.ts`, lo store `src/stores/file-sync-store.ts` e `src/lib/project-file-sync.ts`. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Sincronizzazione e osservazione dei file]

### Stato persistito
Lo stato è persistito in due file per progetto, sempre in `.llm-wiki/` (`file-snapshot.json` e `file-change-queue.json`); non c'è alcun uso di `app_data_dir` (zero occorrenze, per la stringa esatta). I campi dei due file sono in [[llm-wiki-schema-dati]]. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Sincronizzazione e osservazione dei file]

### Scrittura e lettura
La scrittura passa da una sola funzione, `write_json` (file temporaneo e rinomina; su Windows elimina prima l'originale, quindi c'è una finestra non atomica). Prima di `mod tests` l'indice dà un solo `fs::write` e un solo `rename(`, e zero `File::create`, `OpenOptions` e `write_all`: il valore è limitato alle stringhe cercate. Secondo graphify, `write_json` e `read_json` sono usate solo da `write_queue`, `write_snapshot`, `read_queue` e `read_snapshot`. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Sincronizzazione e osservazione dei file]

`read_json` restituisce il valore di default se il file manca; su JSON illeggibile restituisce un errore (`Failed to parse`), a differenza della maggior parte dei caricamenti TS che tornano al valore vuoto in silenzio (vedi [[llm-wiki-gestione-file-corrotti]]). `read_snapshot` e `read_queue` portano `version` da 0 a 1. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Sincronizzazione e osservazione dei file]

### Comandi e avvio
`invalidate_project_file_snapshot_paths` toglie voci dallo snapshot (il frontend lo usa quando l'ingest in background non si può accodare); `ignore_file_change_task` rimuove un task dalla coda; `retry_file_change_task` lo riporta a `pending` e azzera i tentativi. All'avvio del watcher il Rust chiama `reset_processing_tasks`, poi un rescan iniziale e `process_queue`; i corpi di queste funzioni non sono letti (per graphify sono come descritto, `file_sync.rs:208-577`). [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Sincronizzazione e osservazione dei file]

### Stato in memoria
Non sono persistiti: il watcher e gli id del progetto (`FileSyncState`), un blocco per coda (`QUEUE_LOCKS`), la finestra di ignoro delle scritture dell'app (`APP_WRITE_IGNORES`, 4 secondi) e il contatore di generazione del watcher. Lo store TS `file-sync-store.ts` ha solo `tasks`, `running` e `lastError`, senza persistenza. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Sincronizzazione e osservazione dei file]

### Comportamento del watcher (osservato)
Osserva la radice del progetto in modo ricorsivo, più `raw/sources` e `wiki`; accumula i percorsi con una finestra di 700 ms; un rescan periodico (10 s su Linux, 60 s altrove) riallinea lo snapshot dopo eventi persi o overflow. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Sincronizzazione e osservazione dei file]

### Lato TS (osservato, `project-file-sync.ts`)
Non scrive file direttamente. Ascolta `file-sync://queue-updated` e `file-sync://changed`; per le modifiche a `raw/sources` accoda l'ingest (a progetto attivo o inattivo), cancella a cascata i file spariti (vedi [[llm-wiki-cancellazione-pagine-e-sorgenti]]) e migra i percorsi se un file è stato solo spostato (stesso hash, coppia unica creato e cancellato). Con la modalità «tutti i progetti» scansiona ogni 60 s i progetti recenti inattivi. Sono esclusi dalla cascata i percorsi con `/.cache/`, i file che iniziano con un punto e, per le pagine wiki, `index.md`, `log.md`, `overview.md` e `wiki/media/`. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Sincronizzazione e osservazione dei file]

### Non letto
`file_sync.rs` righe 445-1289 (scansione, `process_queue`, `enqueue_*`, `reset_processing_tasks`) e dalla 1410 in poi (test): non si sa se lo snapshot escluda `.llm-wiki` o `.cache`, né come si decida `needsRerun`. La copertura complessiva del codice non letto è nel gap `llm-wiki-persistenza-codice-non-letto` in [[gaps]]. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Gap evidenti]

## Pagine collegate
[[llm-wiki-archivi-persistenza]], [[llm-wiki-schema-dati]], [[llm-wiki-gestione-file-corrotti]], [[llm-wiki-struttura-e-moduli]], [[2026-11-20-repo-llm_wiki-persistenza-b]]. Gap aperto: [[gaps]] (`llm-wiki-persistenza-codice-non-letto`).

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

## Aggiornamenti (v2026-11-21, issue chiuse)
Dalla source page [[2026-11-21-issues-llm_wiki-chiuse]] (issue chiuse di `nashsu/llm_wiki`). Il testo sopra non è modificato. Solo dichiarazioni, nessuna osservazione sul codice di questo punto.

- **Monitoraggio delle cartelle con più progetti, dichiarazioni in contrasto (#648, issue rimasta chiusa).** **Dichiarato (maintainer), v0.6.9:** il monitoraggio elabora tutti i progetti configurati. **Dichiarato (segnalatore), 2026-08-25:** con due progetti configurati viene ancora elaborato solo quello aperto. Non è noto per lettura quale delle due descriva v0.6.13: gap `llm-wiki-monitoraggio-piu-progetti`. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §6. Altre dichiarazioni pertinenti (non chiudono)]
- **Coda dei cambi dopo il riavvio.** **Dichiarato (maintainer), #758, v0.6.12:** recupero degli eventi mancati del monitoraggio al riavvio; i task di ingest `pending` e `processing` persistiti riprendono (vedi [[llm-wiki-pipeline-ingest]]). [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §6. Altre dichiarazioni pertinenti (non chiudono)]

## Aggiornamenti (v2026-11-22, evidenze alm-wiki)
Dalle source page [[2026-11-22-repo-alm-wiki-evidenze-api]] e [[2026-11-22-repo-alm-wiki-bozza-skill]] (progetto locale dell'utente, non un `code_path` della factory; upstream v0.6.13). Il testo sopra non è modificato. Nessuna delle voci seguenti è verificata dalla factory sul codice.
- **Dichiarato dalla fonte come letto nel codice (C), da verificare:** il rescan dell'API aggiorna lo snapshot ed emette un evento e non accoda nulla (`file_sync.rs` 339-362, 946); è la UI ad accodare l'ingest, solo per il progetto aperto, con osservazione attiva (`enabled` e `autoIngest`) e un LLM disponibile (`project-file-sync.ts` 62-66, 344; `source-lifecycle.ts` 268). Ogni cambiamento è riportato una sola volta: `changedTasks` vuoto significa «già visto». Lo scope del rescan include anche `wiki/**/*.md`, `purpose.md` e `schema.md` (`file_sync.rs` 784-786, 946, 664, 1135-1177). [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Discrepanze skill/codice (25) con livello di prova]
- **Dichiarato dalla bozza come letto nel codice (`[code]`), da verificare:** con «Watch all projects» spento e progetto non aperto non c'è accodamento; con l'opzione attiva i progetti recenti sono scansionati ogni 60 s (`project-file-sync.ts` 337-370; `source-lifecycle.ts` 258-285). Il 60 s può essere lo stesso rescan periodico già descritto sopra, la bozza non lo dice. [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §api-reference.md]
- **Dichiarato dalla fonte, con osservazione dichiarata ma non letta:** il watcher vede le scritture manuali in `raw/sources` e le accoda in pochi secondi senza rescan; quelle in `wiki/` non avviano un ingest. La fonte cita come osservazione l'accodamento immediato di tre fonti il 2026-11-13 (fonti 007-009 del progetto dell'utente), che la factory non ha letto. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Discrepanze skill/codice (25) con livello di prova]
- **Prove aperte:** rescan su un progetto non attivo con «Watch all projects» spento e acceso, e rescan con token su un progetto aperto, sono fra le prove non eseguite (gap `llm-wiki-prove-in-esecuzione-aperte`). Non cambia lo stato del gap `llm-wiki-monitoraggio-piu-progetti`. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Prove ancora aperte e vincoli (T37, stato `in progress`, data 2026-11-13)]

## Contradictions
- **«per le modifiche a `raw/sources` accoda l'ingest (a progetto attivo o inattivo)» (§Lato TS) contro «solo per il progetto aperto» (evidenze alm-wiki, C da verificare).** Prima (§Lato TS, osservato nel raw della fetta B): `project-file-sync.ts` accoda l'ingest per le modifiche a `raw/sources` a progetto attivo o inattivo, e con la modalità «tutti i progetti» scansiona ogni 60 s i progetti recenti inattivi. Ora (fonte alm-wiki, discrepanza n. 16, livello C, non verificata dalla factory): l'interfaccia accoda l'ingest solo per il progetto aperto, con osservazione attiva e un LLM disponibile; la bozza aggiunge «o con Watch all projects», il che potrebbe riconciliare le due letture. Non risolta; da verificare nel codice (gap `llm-wiki-affermazioni-codice-da-verificare`, e `llm-wiki-monitoraggio-piu-progetti`). [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Sincronizzazione e osservazione dei file] [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Discrepanze skill/codice (25) con livello di prova] [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §api-reference.md]

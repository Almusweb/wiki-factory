---
id: 2026-11-20-repo-llm_wiki-persistenza-b
type: source
title: Specifiche estratte da code_repos/llm_wiki, persistenza fetta B (repo-sync)
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: ["raw/2026-11-20-repo-llm_wiki-persistenza-b.md"]
tags: [source, repo, llm-wiki, persistenza]
---

# Specifiche estratte da code_repos/llm_wiki, persistenza fetta B (repo-sync)
> Estrazione mirata «fetta B» sul commit `e08cfce`: scritture e atomicità per archivio, sincronizzazione file, coda dedup e lint, cache di ingest e didascalie, file citati non verificati, formato di log e indice. Stato `partial`.

## Contesto
Terza estrazione mirata sullo stesso commit, prodotta da `repo-sync@2.12.0` per TSK-003 (US-013, a servizio di US-015 e US-017) sul commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3`, ramo `develop`, estratta il 2026-11-20T18:54:25+01:00. Stesso commit della prima estrazione ([[2026-11-20-repo-llm_wiki]]) e della fetta A ([[2026-11-20-repo-llm_wiki-persistenza-a]]). [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Identità e perimetro]

## Dettaglio

### Metadati dell'estrazione
- Perimetro: scrittura generica di file (Rust e TS), atomicità per archivio, sincronizzazione e osservazione dei file, coda di dedup e lint, cache di ingest e didascalie, file e cartelle citati e non verificati, formato di log e indice. Restano fuori, per la fetta C, operazioni distruttive, loro chiamanti e vettoriale v1. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Identità e perimetro]
- Il repository è di terzi, sotto GNU GPL v3; il raw descrive il codice con parole proprie e cita solo nomi di file, simboli, campi e percorsi, senza frammenti di codice. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Identità e perimetro]
- Convenzione di certezza: «osservato» è letto nel codice; «deduzione» è ricavato da fatti osservati, non visto in esecuzione. Gli indici di riga vengono da `grep -n -o -F` della sessione e valgono per la stringa letterale cercata: uno zero non dimostra l'assenza della funzione. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Identità e perimetro]
- File aperti: 26 (11 interi, 15 a finestre). Il raw dichiara `files_sampled` cumulativo 80, come massimo perché l'elenco dei 30 file della prima estrazione non è verificabile; il manifest riporta 85 dopo l'aggiornamento (il testo del raw precede gli aggiornamenti, il manifest è il cumulativo successivo). `files_total_in_repo` 476; byte letti circa 200 KB contro una stima di 100-120 KB al gate di Fase 1; stato `partial`. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Note di estrazione] [^src: raw/.extraction-manifest.json §2026-11-20-repo-llm_wiki-persistenza-b.extraction_metadata.files_sampled]
- Il raw elenca i file aperti fuori dall'elenco nominato al gate di Fase 1, con il motivo: `review-view.tsx`, `lint.ts`, `scheduled-import.ts` (70-89), `persist.ts` e `fs.ts` (14-43), `dedup-runner.ts` (466-479). [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Note di estrazione]
- Segreti: nessun valore di credenziale nei file e negli intervalli aperti, nessun file `.env*` aperto, 0 segreti redatti; lo zero non è una scansione dell'intero repo (gap `llm-wiki-scan-credenziali`). Istruzioni nei file letti: nessuna ostile e nessuna rivolta a un agente; le stringhe di prompt destinate al modello dell'applicazione (in `ingest.ts`) sono dati, riportate come formato richiesto al modello dell'app e non eseguite. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Note di estrazione]

### Contenuto
- La sezione «Aggiornamenti (v2026-11-20)» lascia invariato il testo sopra e corregge con coppie «Prima» e «Ora»: ha letto quattro file nuovi a finestre o interi (`parsed-source-output.ts`, `mineru.ts` 600-625 e 995-1010, `maintenance-section.tsx` 195-240, `source-preprocess.ts` 55-70) più `scheduled-import.ts` 225-250; le voci «graphify affected» non sono riviste con la lettura. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Aggiornamenti (v2026-11-20)]
- Le verifiche con graphify (AST senza LLM), ctags e ricerca testuale sono dichiarate «metodo, non fonte normativa», da un file locale non versionato e rigenerabile; graphify non vede gli archi IPC tra TS e Rust, le costanti non sono nodi e uno zero non prova l'assenza di chiamanti. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Limiti]
- Il raw elenca 12 gap evidenti propri (meccanismo di `history-settings.json`, `write_file_inner`, righe non lette di `fs.rs` e `file_sync.rs`, `ingest-queue.ts` oltre la riga 219, chiamanti di `writeFileAtomic`, `LEGACY_DB_DIR`, tipi `DuplicateGroup` e `LintResult`, occorrenze non classificate di `index.md` e `log.md`, formato di voce dipendente dal prompt, dimensioni, conteggio archivi); nell'aggiornamento dichiara chiusi o rivisti i punti 6 e 7. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Gap evidenti]

### Pagine ricavate o aggiornate
- Nuova: [[llm-wiki-sincronizzazione-file]].
- Aggiornate: [[llm-wiki-archivi-persistenza]] (meccanismo di scrittura, nove archivi non in inventario, cache, code), [[llm-wiki-schema-dati]] (log e indice, snapshot e coda cambi, ciclo di vita di `.llm-wiki/`), [[llm-wiki-gestione-file-corrotti]], [[llm-wiki-versioni-e-migrazioni]], [[llm-wiki-rischi-persistenza]] (indizi, esito invariato).

### Gap aperti da questa fetta
Dai gap evidenti del raw sono stati aperti in [[gaps]], accorpati con quelli di altre fette: `llm-wiki-scritture-non-verificate`, `llm-wiki-chiamanti-non-verificati`, `llm-wiki-tipi-dedup-lint`, `llm-wiki-markdown-estratto-percorsi`. Le righe non lette di `file_sync.rs` restano nel gap esistente `llm-wiki-persistenza-codice-non-letto`. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Gap evidenti]

## Estratto non promosso a pagina
Nessun contenuto del raw è stato scartato. Il testo del raw non è stato modificato.

## Pagine collegate
[[2026-11-20-repo-llm_wiki]], [[2026-11-20-repo-llm_wiki-persistenza-a]], [[2026-11-20-repo-llm_wiki-persistenza-c]], [[gaps]]

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

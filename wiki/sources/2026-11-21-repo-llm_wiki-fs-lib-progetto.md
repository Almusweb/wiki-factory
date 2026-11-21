---
id: 2026-11-21-repo-llm_wiki-fs-lib-progetto
type: source
title: Specifiche estratte da code_repos/llm_wiki, estrazione 2026-11-21 fetta C1: FS, lib.rs, progetto (repo-sync)
status: draft
created: 2026-11-21
updated: 2026-11-21
sources: ["raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md"]
tags: [source, repo, llm-wiki, filesystem, progetto, persistenza]
---

# Specifiche estratte da code_repos/llm_wiki, estrazione 2026-11-21 fetta C1: FS, lib.rs, progetto (repo-sync)
> Estrazione mirata `repo-sync` v2.12 del 2026-11-21 sul commit `e08cfce` (v0.6.13): `persist.ts`, `project-identity.ts`, `project-store.ts`, `fs.ts`, `embedding.ts`, `project.rs`, `project_maintenance.rs`, `panic_guard.rs` per intero; `fs.rs`, `lib.rs`, `file_history.rs` in parte. Le conseguenze marcate «DEDUZIONE NON TESTATA» restano inferenze mai eseguite.

## Contesto
Quarta fetta del giro del 2026-11-21 (FS, `lib.rs`, progetto), sullo stesso commit delle estrazioni precedenti ([[2026-11-20-repo-llm_wiki]] e le fette di persistenza [[2026-11-20-repo-llm_wiki-persistenza-a]], [[2026-11-20-repo-llm_wiki-persistenza-b]], [[2026-11-20-repo-llm_wiki-persistenza-c]]). Il raw indica il ramo come HEAD staccato (artefatto del checkout del submodule rispetto al `develop` delle source page precedenti, stesso commit). [^src: raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md §Specifiche estratte: llm_wiki (fetta C1: FS, lib.rs, progetto)]

## Dettaglio

### Metadati dell'estrazione
- Prodotta da `repo-sync` v2.12 il 2026-11-21 sul commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` (v0.6.13, HEAD staccato), in sola lettura verso la sorgente. [^src: raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md §Specifiche estratte: llm_wiki (fetta C1: FS, lib.rs, progetto)]
- Letti per intero: `persist.ts`, `project-identity.ts`, `project-store.ts`, `commands/fs.ts`, `embedding.ts`, `project.rs`, `project_maintenance.rs`, `panic_guard.rs`. Letti in parte: `lib.rs` righe 1-780, `fs.rs` righe 1-650 e 1000-2229, `file_history.rs` righe 70-469, `tauri.conf.json` righe 1-40. Un chiamante non trovato nelle finestre lette è non verificato, non assente. Nessun segreto rilevato. [^src: raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md §Copertura]
- Non letti: `fs.rs` 651-999 (estrazione docx/pptx/org) e 2230-3300 (test), `file_history.rs` 1-69 e dalla 470, `lib.rs` dalla 780. [^src: raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md §Gap evidenti]

### Contenuto
- Nome e uso di `app-state.json`, chiavi viste, flush, `chat-history.json` legacy, cronologia dei file: [[llm-wiki-archivi-persistenza]]. [^src: raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md §Archivio dello stato app (gap 15)]
- Layout del progetto su disco, ciclo di vita lato frontend di `.llm-wiki/`, identità di progetto e registro globale: [[llm-wiki-schema-dati]]. [^src: raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md §Layout del progetto su disco e creazione di `.llm-wiki/` (gap 16)]
- `delete_file` senza confinamento al progetto, tabella dei controlli sul path dei comandi FS, export e import dell'archivio: [[llm-wiki-operazioni-distruttive]]. [^src: raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md §Comandi FS Rust e confini (gap 34, lato Rust)]
- Comandi vector v1 e v2 registrati in `lib.rs`; `embedding.ts` usa solo i v2: [[llm-wiki-versioni-e-migrazioni]]. [^src: raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md §Vector v1 vs v2 (gap 17)]
- Possibile memorizzazione in chiaro dei token e assenza di confinamento dei comandi FS di lettura, copia e cancellazione: [[llm-wiki-sicurezza]]; indizi sui rischi di collisione di id dopo l'import e di cancellazione non confinata: [[llm-wiki-rischi-persistenza]] (conseguenze solo deduzioni non testate). [^src: raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md §Identita' del progetto, registro e import (gap 26)]

### Limiti e gap
Il raw riporta cinque gap evidenti: path OS di `app_data_dir`, cifratura dei token in `app-state.json`, chiamante UI dell'import e collisione di id, chiamanti dei comandi vector v1 fuori da `embedding.ts`, chiamanti TS che confinano la cancellazione al progetto. [^src: raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md §Gap evidenti]

## Pagine ricavate o aggiornate
Aggiornate: [[llm-wiki-archivi-persistenza]], [[llm-wiki-schema-dati]], [[llm-wiki-operazioni-distruttive]], [[llm-wiki-versioni-e-migrazioni]], [[llm-wiki-sicurezza]], [[llm-wiki-rischi-persistenza]].

## Gap di questa fetta
- Chiuso: `llm-wiki-creazione-cartella-dati`.
- Parziali: `llm-wiki-app-state-percorso`, `llm-wiki-vector-v1-chiamanti`, `llm-wiki-import-id-duplicato`, `llm-wiki-cancellazione-controlli-confine`, `llm-wiki-archivi-sommario-conteggi`, `llm-wiki-riferimenti-incrociati`, `llm-wiki-scritture-non-verificate`, `llm-wiki-persistenza-codice-non-letto`, `llm-wiki-codice-non-letto`.
- Aperto: `llm-wiki-token-cifratura` (deduzione non testata), unito alla proposta analoga della fetta [[2026-11-21-repo-llm_wiki-ricerca-ui-residui]].
- Non aperti perché già coperti da gap esistenti ancora aperti: `llm-wiki-cancellazione-chiamanti-ts` (in `llm-wiki-cancellazione-controlli-confine`) e `llm-wiki-import-chiamante-ui` (in `llm-wiki-import-id-duplicato`).

Dettagli in [[gaps]]. [^src: raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md §Gap evidenti]

## Estratto non promosso a pagina
Nessun contenuto del raw è stato scartato. Il testo del raw non è stato modificato.

## Pagine collegate
[[2026-11-20-repo-llm_wiki]], [[2026-11-20-repo-llm_wiki-persistenza-a]], [[2026-11-20-repo-llm_wiki-persistenza-b]], [[2026-11-20-repo-llm_wiki-persistenza-c]], [[llm-wiki-archivi-persistenza]], [[llm-wiki-schema-dati]], [[llm-wiki-operazioni-distruttive]], [[llm-wiki-sicurezza]], [[llm-wiki-rischi-persistenza]], [[llm-wiki-versioni-e-migrazioni]], [[gaps]]

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

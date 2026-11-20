---
id: llm-wiki-schema-dati
type: concept
title: llm-wiki — schema dati
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: ["raw/2026-11-20-repo-llm_wiki.md"]
tags: [llm-wiki, dati]
---

# llm-wiki — schema dati
> In `llm-wiki` non c'è un database relazionale né un file `.proto`: i dati vivono su file.

## Contesto
Il raw non rileva schemi di database. Descrive il layout dei file di un progetto wiki (dalla README), i tipi TypeScript condivisi e l'indice vettoriale. [^src: raw/2026-11-20-repo-llm_wiki.md §Schema dati (se rilevato)]

## Dettaglio
- **Layout di un progetto wiki** (README): `purpose.md`, `schema.md`, `raw/sources`, `raw/assets`, `wiki/` con `index.md`, `log.md`, `overview.md` e le cartelle entities, concepts, sources, queries, synthesis, comparisons; poi `.obsidian/` e `.llm-wiki/` (configurazione, cronologia chat, review, `project.json` con l'identificativo UUID del progetto). [^src: raw/2026-11-20-repo-llm_wiki.md §Schema dati (se rilevato)]
- **Tipi TypeScript condivisi** (`src/types/wiki.ts`): `WikiProject` (id, name, path), `FileNode` (con figli opzionali) e `WikiPage` (percorso, contenuto, frontmatter). [^src: raw/2026-11-20-repo-llm_wiki.md §Schema dati (se rilevato)]
- **Indice vettoriale** su LanceDB con chunk. Il piano `plans/multimodal-images.md` descrive lo schema come solo testo, con un campo per il testo del chunk. Il piano ha stato «Spec, not started», quindi la descrizione va verificata sul codice. [^src: raw/2026-11-20-repo-llm_wiki.md §Schema dati (se rilevato)]
- **Instradamento dei tipi di pagina** letto dallo `schema.md` del progetto (`src/lib/wiki-schema.ts`, letto in parte): la funzione `parseWikiSchemaRouting` estrae da una tabella nella sezione «Page types» la corrispondenza tipo-directory, scartando directory non sicure. [^src: raw/2026-11-20-repo-llm_wiki.md §Schema dati (se rilevato)]

## Pagine collegate
Gap aperto sullo stato del piano multimodale: [[gaps]] (`llm-wiki-multimodale-stato`).

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

## Aggiornamenti (v2026-11-20)
Seconda estrazione, mirata al layer di persistenza, sullo stesso commit `e08cfce` (21 file letti, `files_sampled` cumulativo 50, estrazione ancora `partial`). Archivi, versioni, operazioni distruttive, file corrotti e rischi sono nelle pagine dedicate: [[llm-wiki-archivi-persistenza]], [[llm-wiki-versioni-e-migrazioni]], [[llm-wiki-operazioni-distruttive]], [[llm-wiki-gestione-file-corrotti]], [[llm-wiki-rischi-persistenza]]. [^src: raw/2026-11-20-repo-llm_wiki.md §Premessa e perimetro]

- **Schema LanceDB v2** (`wiki_chunks_v2`): sei colonne, quattro di testo (`chunk_id`, `page_id`, `chunk_text`, `heading_path`), una intera senza segno a 32 bit (`chunk_index`) e `vector`, lista a lunghezza fissa di numeri a 32 bit; nessuna colonna è nulla. **Schema v1** (`wiki_vectors`): due colonne (`page_id`, `vector`). [^src: raw/2026-11-20-repo-llm_wiki.md §Schemi e campi]
- **Tipi Rust in `vectorstore.rs`**: `VectorSearchResult` (v1: `page_id`, `score`), `ChunkSearchResult` (v2: `chunk_id`, `page_id`, `chunk_index`, `chunk_text`, `heading_path`, `score`), `ChunkUpsertInput` (`chunk_index`, `chunk_text`, `heading_path`, `embedding`). Il punteggio è ricavato dalla distanza con la formula 1 / (1 + distanza). [^src: raw/2026-11-20-repo-llm_wiki.md §Schemi e campi]
- **Id di pagina validato** (massimo 256 caratteri, niente apici, backslash, caratteri di controllo o invisibili) perché viene inserito in un filtro testuale. [^src: raw/2026-11-20-repo-llm_wiki.md §Schemi e campi]
- **Chunking e limiti** (`page_embedding.rs`): `PageEmbeddingResult` (`path`, `pageId`, `revision`, `chunks`, `vectorsWritten`, `status` con valori unchanged o indexed). Pagina massimo 2 MiB, massimo 512 chunk, chunk da 64 a 32.000 caratteri (default 1.000, sovrapposizione 200), batch da 64. Lato TS, `embedding.ts` aggrega i chunk per pagina con punteggio massimo più una coda pesata e limitata. [^src: raw/2026-11-20-repo-llm_wiki.md §Schemi e campi]
- **Layout creato da `create_project`**: cartelle `raw/sources`, `raw/assets` e `wiki/` con le sottocartelle entities, concepts, sources, queries, comparisons, synthesis; file `schema.md`, `purpose.md`, `wiki/index.md`, `wiki/log.md`, `wiki/overview.md`; cartella `.obsidian/` con `app.json`, `appearance.json`, `core-plugins.json`. **`.llm-wiki/` non viene creata da questo comando**: nasce dopo, lato TS (`ensureDir` in `persist.ts` e `ensureProjectId`). `open_project` valida solo la presenza di `schema.md` e della cartella `wiki/`. Chi crea `.llm-wiki/` per un progetto importato o aperto da disco non è noto: gap `llm-wiki-creazione-cartella-dati` in [[gaps]]. [^src: raw/2026-11-20-repo-llm_wiki.md §Schemi e campi]
- **Tipo `WikiProject`**: il commento di `src/types/wiki.ts` dice che l'`id` è un UUID persistito in `project.json`; il tipo Rust di ritorno di `create_project` e `open_project` è costruito solo con nome e percorso (`src-tauri/src/commands/project.rs`), quindi l'`id` viene assegnato dal lato TS (`ensureProjectId`). Rispetto alla voce sopra non è una contraddizione: ne precisa l'origine. [^src: raw/2026-11-20-repo-llm_wiki.md §Schemi e campi]
- **Versioni esplicite**: solo `version: 1` in `scheduled-import-db.json` e il suffisso `_v2` della tabella LanceDB. [^src: raw/2026-11-20-repo-llm_wiki.md §Versioni di formato e migrazioni]
- **Aggiornamento sul gap `llm-wiki-multimodale-stato`** (resta aperto): lo schema v2 non ha colonne per immagini, il che è coerente con lo stato «Spec, not started» del piano multimodale. È una deduzione dallo schema letto in `vectorstore.rs`; `ingest.ts` e il modulo `extract_images` non sono letti, quindi lo stato reale non è verificato. `multimodalConfig` compare tra le chiavi di `app-state.json`. [^src: raw/2026-11-20-repo-llm_wiki.md §Schemi e campi]

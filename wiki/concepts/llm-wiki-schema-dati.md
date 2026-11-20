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

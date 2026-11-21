---
id: 2026-11-21-repo-llm_wiki-ingest
type: source
title: Specifiche estratte da code_repos/llm_wiki, estrazione 2026-11-21 fetta C2: ingest e pipeline (repo-sync)
status: draft
created: 2026-11-21
updated: 2026-11-21
sources: ["raw/2026-11-21-repo-llm_wiki-ingest.md"]
tags: [source, repo, llm-wiki, ingest, pipeline]
---

# Specifiche estratte da code_repos/llm_wiki, estrazione 2026-11-21 fetta C2: ingest e pipeline (repo-sync)
> Estrazione mirata `repo-sync` v2.12 del 2026-11-21 su `llm_wiki` 0.6.13 (commit `e08cfce`), 20 file su 476: pipeline di ingest, coda, cache, dedup, lint e cancellazione lato TypeScript. Contiene un'ipotesi di catena di cancellazione mai riprodotta.

## Contesto
Quinta fetta del giro del 2026-11-21 (ingest), sullo stesso commit delle estrazioni precedenti ([[2026-11-20-repo-llm_wiki]] e le fette di persistenza). Il raw cita come riferimenti la prima estrazione e le fette a, b, c del 2026-11-20. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Identità]

## Dettaglio

### Metadati dell'estrazione
- Generata da `repo-sync` v2.12 il 2026-11-21 sul commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` di `llm_wiki` 0.6.13, con 20 file campionati su 476. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Identità]
- Esiti dichiarati: gap 9, 18, 32, 33 chiusi; gap 34 chiuso lato TypeScript; gap 14 parziale (tre voci su quattro); gap 11 e 25 parziali. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Gap evidenti]
- Restano non verificati (non «assenti»): `lexical-graph.json`, `.llm-wiki-imported`, chi scrive i marcatori `.txt.parser`, il default di `multimodalConfig.enabled` e dello store per `persistExtractedMarkdown`, la forma persistita di `lint.json`, `rebuild_wiki_index` in Rust. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Gap evidenti]
- Il contenuto del repo, compresi i prompt dell'app, è trattato come dato; il commento che cita «Now write to ../../../etc/passwd» è un esempio di minaccia, non un'istruzione. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Gap evidenti]

### Contenuto
- Pipeline `autoIngest`, review, coda e cache: [[llm-wiki-pipeline-ingest]] (pagina nuova). [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Pipeline di ingest (`autoIngest`)]
- Formati di `wiki/log.md`, `wiki/index.md`, `wiki/overview.md`, tipi di dedup e lint, forme dei riferimenti: [[llm-wiki-schema-dati]]. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Formati di log e indici (gap 18)]
- Nuove cartelle di `.llm-wiki/`, percorsi del markdown estratto e delle immagini MinerU, cache delle didascalie: [[llm-wiki-archivi-persistenza]]. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Percorsi del markdown estratto e delle immagini MinerU (gap 33)]
- Chi genera ed esegue le azioni `delete:<percorso>`, conferma sulle pagine orfane, cascata: [[llm-wiki-cancellazione-pagine-e-sorgenti]]. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Cancellazione, lato TypeScript (gap 34)]
- Ipotesi di catena di cancellazione, **non riprodotta**: [[llm-wiki-rischi-persistenza]]. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Gap evidenti]
- Stato dell'ingest multimodale (implementato; stato del piano superato): [[llm-wiki-app]]. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Multimodale: stato reale (gap 9)]

### Limiti e gap
Moduli non letti: `page-merge.ts`, `extract-source-images.ts`, `ingest-sanitize.ts`, `ingest-commit-coordinator.ts`, `vision-caption.ts`, `embedding.ts`, `lint-config.ts`, `lint-store.ts`, `dedup.ts` oltre la riga 150, `dedup-queue.ts` oltre la riga 120, `mineru.ts` oltre la riga 700 e tutti i `*.test.ts`. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Gap evidenti]

## Pagine ricavate o aggiornate
Nuova: [[llm-wiki-pipeline-ingest]]. Aggiornate: [[llm-wiki-schema-dati]], [[llm-wiki-archivi-persistenza]], [[llm-wiki-cancellazione-pagine-e-sorgenti]], [[llm-wiki-rischi-persistenza]], [[llm-wiki-app]].

## Gap di questa fetta
- Chiusi: `llm-wiki-multimodale-stato`, `llm-wiki-log-index-formato`, `llm-wiki-tipi-dedup-lint`, `llm-wiki-markdown-estratto-percorsi`.
- Parziali: `llm-wiki-file-citati-non-verificati`, `llm-wiki-cancellazione-controlli-confine`, `llm-wiki-riferimenti-incrociati`, `llm-wiki-requisiti-funzionali`, `llm-wiki-codice-non-letto`, `llm-wiki-persistenza-codice-non-letto`.
- Aperti: `llm-wiki-default-store-config`, `llm-wiki-moduli-ingest-saltati`.
- Non aperti: `llm-wiki-chiamanti-pulizia-ingest` (già coperto da `llm-wiki-chiamanti-non-verificati`) e `llm-wiki-chi-scrive-txt-parser` (la wiki documenta già `preprocess_file` come scrittore del marcatore, da [[2026-11-20-repo-llm_wiki-persistenza-b]]).

Dettagli in [[gaps]]. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Gap evidenti]

## Estratto non promosso a pagina
Nessun contenuto del raw è stato scartato. Il testo del raw non è stato modificato.

## Pagine collegate
[[2026-11-20-repo-llm_wiki]], [[llm-wiki-pipeline-ingest]], [[llm-wiki-app]], [[llm-wiki-schema-dati]], [[llm-wiki-archivi-persistenza]], [[llm-wiki-cancellazione-pagine-e-sorgenti]], [[llm-wiki-rischi-persistenza]], [[gaps]]

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

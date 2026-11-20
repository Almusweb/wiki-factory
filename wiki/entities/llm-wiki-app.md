---
id: llm-wiki-app
type: entity
title: llm-wiki (applicazione)
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: ["raw/2026-11-20-repo-llm_wiki.md"]
tags: [llm-wiki, entity, prodotto]
---

# llm-wiki (applicazione)
> Applicazione desktop multipiattaforma che costruisce in modo incrementale una wiki persistente di pagine Markdown a partire da documenti; repository di terzi sotto GNU General Public License v3.0.

## Contesto
Pagina entità del prodotto `llm-wiki`, descritto dal raw `repo-sync` sul ramo `develop`, commit `e08cfce`. L'estrazione è `partial` (vedi [[2026-11-20-repo-llm_wiki]]). Il termine «pattern LLM Wiki» indica invece il pattern: [[pattern-llm-wiki]]. [^src: raw/2026-11-20-repo-llm_wiki.md §Note di estrazione]

## Dettaglio

### Identità
- Nome `llm-wiki`; manifest root e manifest Tauri alla versione `0.6.13`; nome prodotto «LLM Wiki». [^src: raw/2026-11-20-repo-llm_wiki.md §Identità]
- Descrizione dalla README: «A personal knowledge base that builds itself. LLM reads your documents, builds a structured wiki, and keeps it current.» È un'applicazione desktop multipiattaforma che costruisce in modo incrementale una wiki persistente di pagine Markdown interconnesse a partire da documenti, invece di rifare retrieval da zero a ogni domanda. [^src: raw/2026-11-20-repo-llm_wiki.md §Identità]
- Autore e maintainer: la README cita nash_su come creatore e manutentore; l'intestazione di `LICENSE` riporta «Copyright (C) 2024-2026 Yong Su». La relazione tra i due nomi non è verificabile dal sampling. [^src: raw/2026-11-20-repo-llm_wiki.md §Identità]
- Top contributors da git (10): Ameisina, Andrew Chen, Bernardino Sassoli, Dongmin Yu, Kostadis Rousoss, Lucas Zhu, Po1nt9, PyZhang, Raphael Lin, Sergey Snigirev. [^src: raw/2026-11-20-repo-llm_wiki.md §Identità]
- Ultimo commit: 2026-10-21 19:17:06 +0800, `e08cfce65aad8b76b13546a081c1a8d4422b70c3`, «release: v0.6.13». Attività nell'ultimo anno: 907 commit. [^src: raw/2026-11-20-repo-llm_wiki.md §Identità]

### Funzioni dichiarate in README (sintesi, non confermate dal codice letto)
Ingest in due passi (analisi poi generazione), cache SHA256 incrementale e coda di ingest persistente, import di PDF/Office/EPUB/MOBI/immagini/web clip, ingest multimodale di immagini con didascalie da LLM visivo, grafo di conoscenza con modello di rilevanza a 4 segnali e rilevamento di community (Louvain), insight del grafo, ricerca semantica opzionale su LanceDB, Deep Research con ricerca web, sistema di review asincrono, agente di chat nel backend Rust con skill, estensione Chrome per il web clipping, API HTTP locale, server MCP. [^src: raw/2026-11-20-repo-llm_wiki.md §Identità]

Requisiti funzionali e regole di dominio sono derivabili solo dalla README e non sono confermati dal codice letto. [^src: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti]

### Lingue dell'interfaccia
La README dice «English + Chinese» per l'i18n, ma in `src/i18n/` esistono `en.json`, `it.json`, `ru.json`, `zh.json`. [^src: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti]

### Stato dell'ingest multimodale
`plans/multimodal-images.md` ha stato «Spec, not started», mentre la README descrive come già presente l'ingest multimodale. [^src: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti]

### Documenti correlati nel repository
`README.md` e le varianti `README_CN.md`, `README_JA.md`, `README_KO.md`; `llm-wiki.md`; `mcp-server/README.md`; `plans/multimodal-images.md`; `LICENSE`; `src/lib/changelog.ts` (54 KB, non letto); `.github/workflows/ci.yml` e `build.yml` (il secondo non letto). Non esistono cartelle `docs/` né `ADR/`; il `.gitignore` esclude `docs/` e `AGENTS.md` con il commento «Internal docs (not shipped)», e anche i file `.env`. [^src: raw/2026-11-20-repo-llm_wiki.md §Documenti correlati nel repo]

## Pagine collegate
- Pattern: [[pattern-llm-wiki]]
- Licenza: [[llm-wiki-licenza-e-standard]]
- Dati: [[llm-wiki-schema-dati]]
- Stack: [[llm-wiki-stack-e-dipendenze]]
- Test e CI: [[llm-wiki-test-e-ci]]
- Agente: [[llm-wiki-agente]]
- API locale: [[llm-wiki-api-locale]]
- Server MCP: [[llm-wiki-mcp-server]]
- Sicurezza: [[llm-wiki-sicurezza]]
- Struttura e moduli: [[llm-wiki-struttura-e-moduli]]
- Gap aperti: [[gaps]]

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

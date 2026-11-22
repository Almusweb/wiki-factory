---
id: llm-wiki-app
type: entity
title: llm-wiki (applicazione)
status: draft
created: 2026-11-20
updated: 2026-11-22
sources: ["raw/2026-11-20-repo-llm_wiki.md", "raw/2026-11-21-repo-llm_wiki-ingest.md", "raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md", "raw/2026-11-22-repo-llm_wiki_skill.md"]
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

## Aggiornamenti (v2026-11-21)
Dalle fette C2 ed E del giro del 2026-11-21 ([[2026-11-21-repo-llm_wiki-ingest]], [[2026-11-21-repo-llm_wiki-ricerca-ui-residui]], commit `e08cfce`). Il testo sopra non è modificato; dove è superato lo dice `## Contradictions` in coda. Chiusi in [[gaps]]: `llm-wiki-multimodale-stato` e `llm-wiki-i18n-lingue`; `llm-wiki-requisiti-funzionali` resta aperto in parte. Le sezioni sopra riportano il ramo `develop` per il commit `e08cfce`; i raw del 2026-11-21 lo indicano su HEAD detached: è lo stesso commit e la differenza è un artefatto del checkout del submodule (nota, non contraddizione di contenuto).

### Stato dell'ingest multimodale
- L'ingest multimodale è implementato: estrazione immagini da sorgente e dal markdown, riuso delle immagini MinerU, didascalie con modello di visione (cache per hash dei byte, concorrenza configurabile), sezione «Embedded Images» in `wiki/sources/<slug>.md` tra marcatori `llm-wiki:embedded-images` (idempotente, stub se la pagina manca), nuovo embedding della pagina sorgente dopo le didascalie. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Multimodale: stato reale (gap 9)]
- Con `multimodalConfig.enabled` spento i riferimenti immagine sono tolti dal testo dato al modello e la sezione non viene iniettata, ma le immagini restano sul disco. Il provider `codex-cli` non supporta l'input immagine: le didascalie sono saltate e contate come fallite. Il percorso chat (`executeIngestWrites`) inietta le immagini solo se multimodale è attivo. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Multimodale: stato reale (gap 9)]
- Lo stato «Spec, not started» di `plans/multimodal-images.md` risulta superato; il testo del piano non è stato riletto, lo stato è quello riportato dal gap. Non verificati: il default di `multimodalConfig.enabled` e il modulo Rust di estrazione (gap `llm-wiki-default-store-config`). [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Multimodale: stato reale (gap 9)]
- L'ingest in due stadi, la cache, la coda e gli altri requisiti confermati dal codice sono in [[llm-wiki-pipeline-ingest]]; chat, ricerca, deep research e API non sono coperti da quella fetta. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Requisiti funzionali confermati sull'ingest (gap 11, parte)]

### Lingue dell'interfaccia
- L'interfaccia registra quattro lingue: `en`, `it`, `zh`, `ru`; lingua iniziale e di ripiego `en`. La sezione Interface offre English, Italiano, 中文, Русский; al salvataggio, se la lingua cambia, si chiamano `i18n.changeLanguage` e `saveLanguage`. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Lingue dell'interfaccia (gap i18n-lingue)]
- La lingua di output delle pagine (`outputLanguage`, default `auto`) è un'impostazione distinta dalla lingua UI. Non verificato: dove la lingua salvata viene riletta all'avvio. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Lingue dell'interfaccia (gap i18n-lingue)]

## Aggiornamenti (v2026-11-22)
Dalla source page [[2026-11-22-repo-llm_wiki_skill]]: esiste una skill per agenti esterni, `llm_wiki_skill` (`main`, `642b438`), solo documentazione, che descrive l'API HTTP locale dell'app e dichiara di corrispondere ad API v1 «as shipped in app version 0.4.10+». È un repository distinto da `llm_wiki`; l'entità è [[llm-wiki-skill]] e le differenze con l'app v0.6.13 descritta in questa pagina sono in [[llm-wiki-skill-vs-app-v0-6-13]]. Il testo sopra non è modificato; nessuna contraddizione con questa pagina. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Versione dichiarata]

## Contradictions
- **Ingest multimodale: stato del piano contro codice.** Prima (sezione «Stato dell'ingest multimodale»): `plans/multimodal-images.md` ha stato «Spec, not started», mentre la README descrive come già presente l'ingest multimodale. Ora (fetta C2): il codice implementa l'ingest multimodale; la README è coerente con il codice e lo stato del piano è superato (testo del piano non riletto). [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Multimodale: stato reale (gap 9)]
- **Lingue dell'interfaccia: README «English + Chinese» contro codice.** Prima (sezione «Lingue dell'interfaccia»): la README dice «English + Chinese», ma `src/i18n/` contiene `en.json`, `it.json`, `ru.json`, `zh.json`. Ora (fetta E): il codice registra `en`, `it`, `zh`, `ru`; la README è indietro rispetto al codice. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Lingue dell'interfaccia (gap i18n-lingue)]
- **Funzioni «non confermate dal codice letto».** Prima: ingest in due passi, cache, coda persistente, agente di chat nel backend, API locale e server MCP sono «dichiarate in README, non confermate dal codice letto». Ora: ingest, cache, coda ([[llm-wiki-pipeline-ingest]]), agente ([[llm-wiki-agente]]), API ([[llm-wiki-api-locale]]) e server MCP ([[llm-wiki-mcp-server]]) sono descritti dal codice letto dalle fette del 2026-11-21; grafo, ricerca semantica, deep research e web clipping restano da confermare. Il gap `llm-wiki-requisiti-funzionali` resta aperto in parte. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Requisiti funzionali confermati sull'ingest (gap 11, parte)]

---
updated: 2026-11-23
---
<!-- generated, do not edit: python3 tools/kanban/generate_sprint.py -->

# Sprint view — wiki-factory

> View generata dal frontmatter dei TSK: non modificarla a mano, rigenerala con
> `python3 tools/kanban/generate_sprint.py`.
>
> Sprint corrente: TSK `in_progress`, `review`, `blocked` e `todo` P0/P1.
> Lookahead: TSK `todo` P2/P3 o senza priorita'.

## Epiche con lavoro aperto

| Epica | Titolo | Status epica | blocked | in_progress | review | todo |
|---|---|---|---|---|---|---|
| [EP-002](EP-002-conoscenza-layer-di-persistenza/EP-002.md) | Completare la conoscenza del layer di persistenza | defined | 0 | 1 | 0 | 3 |
| [LWS-EP-001](LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-EP-001.md) | Allineare la skill llm-wiki all'app llm_wiki v0.6.13 (fase A, PR generica upstream) | defined | 0 | 0 | 0 | 9 |

Totale TSK aperti: 13 (sprint corrente 7, lookahead 6).

## Sprint corrente

### EP-002 — Completare la conoscenza del layer di persistenza

| TSK | Titolo | US | Layer | Pri | Status | Owner | Dipende da |
|---|---|---|---|---|---|---|---|
| [TSK-029](EP-002-conoscenza-layer-di-persistenza/US-035-rebuild-index-e-scrittori-log-index/TSK-029.md) | Estrazione repo-sync mirata: rebuild_wiki_index, scrittori di index.md e log.md, rewriteIndexMd, ingest da conversazione, source-lifecycle.ts:642 | US-035 | docs | P2 | in_progress | — | — |

### LWS-EP-001 — Allineare la skill llm-wiki all'app llm_wiki v0.6.13 (fase A, PR generica upstream)

| TSK | Titolo | US | Layer | Pri | Status | Owner | Dipende da |
|---|---|---|---|---|---|---|---|
| [LWS-TSK-010](LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-007-scritture-chat-e-rescan/LWS-TSK-010.md) | Rescan e changedTasks nella skill, assenza di 499 e ricetta con una route nuova | LWS-US-007 | docs | P1 | todo | — | LWS-TSK-009 |
| [LWS-TSK-014](LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-009-coerenza-interna-e-versione/LWS-TSK-014.md) | Dichiarazione di versione, README e regola di drift nella skill | LWS-US-009 | docs | P1 | todo | — | LWS-TSK-010 |
| [LWS-TSK-015](LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-009-coerenza-interna-e-versione/LWS-TSK-015.md) | Verifica di coerenza fra i quattro file della skill sui termini toccati da 003..007 | LWS-US-009 | docs | P1 | todo | — | LWS-TSK-014 |
| [LWS-TSK-016](LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-010-preparare-la-pr-upstream/LWS-TSK-016.md) | Audit locale pre-PR: non-traccia, elementi non trasferibili, evidenza per ogni frase e bozza della descrizione | LWS-US-010 | docs | P1 | todo | — | LWS-TSK-015 |
| [LWS-TSK-017](LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-010-preparare-la-pr-upstream/LWS-TSK-017.md) | Push del branch condiviso sulla fork (gate umano) | LWS-US-010 | infra | P1 | todo | — | LWS-TSK-016 |
| [LWS-TSK-018](LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-010-preparare-la-pr-upstream/LWS-TSK-018.md) | Apertura della PR verso nashsu/llm_wiki_skill (gate umano) | LWS-US-010 | infra | P1 | todo | — | LWS-TSK-017 |

## Lookahead

### EP-002 — Completare la conoscenza del layer di persistenza

| TSK | Titolo | US | Layer | Pri | Status | Owner | Dipende da |
|---|---|---|---|---|---|---|---|
| [TSK-030](EP-002-conoscenza-layer-di-persistenza/US-035-rebuild-index-e-scrittori-log-index/TSK-030.md) | Ingest wiki-keeper del raw su rebuild_wiki_index e scrittori di log e indice, con controllo segreti | US-035 | docs | P2 | todo | — | TSK-029 |
| [TSK-031](EP-002-conoscenza-layer-di-persistenza/US-035-rebuild-index-e-scrittori-log-index/TSK-031.md) | Chiudere i punti di US-035 sul raw ingerito: formato dell'indice ricostruito e tabella degli scrittori in llm-wiki-schema-dati | US-035 | docs | P2 | todo | — | TSK-030 |
| [TSK-032](EP-002-conoscenza-layer-di-persistenza/US-035-rebuild-index-e-scrittori-log-index/TSK-032.md) | Chiudere il residuo rebuild_wiki_index del gap llm-wiki-log-index-formato in wiki/gaps.md | US-035 | docs | P2 | todo | — | TSK-031 |

### LWS-EP-001 — Allineare la skill llm-wiki all'app llm_wiki v0.6.13 (fase A, PR generica upstream)

| TSK | Titolo | US | Layer | Pri | Status | Owner | Dipende da |
|---|---|---|---|---|---|---|---|
| [LWS-TSK-011](LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-008-verificare-i-residui-sul-codice/LWS-TSK-011.md) | Estrazione repo-sync A: residui della superficie API HTTP di llm_wiki a e08cfce | LWS-US-008 | docs | P2 | todo | — | — |
| [LWS-TSK-012](LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-008-verificare-i-residui-sul-codice/LWS-TSK-012.md) | Estrazione repo-sync B: sourceWatchConfig, Watch all projects e voci V4, V20, V21, V22 | LWS-US-008 | docs | P2 | todo | — | — |
| [LWS-TSK-013](LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-008-verificare-i-residui-sul-codice/LWS-TSK-013.md) | Ingest wiki-keeper degli esiti delle estrazioni e aggiornamento dei gap | LWS-US-008 | docs | P2 | todo | — | LWS-TSK-011, LWS-TSK-012 |

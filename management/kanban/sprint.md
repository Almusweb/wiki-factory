---
updated: 2026-11-20
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
| [EP-001](EP-001-difetti-master-analisi-e-segnalazione/EP-001.md) | Difetti del master: analisi e segnalazione | defined | 0 | 0 | 0 | 1 |
| [EP-002](EP-002-conoscenza-layer-di-persistenza/EP-002.md) | Completare la conoscenza del layer di persistenza | defined | 0 | 0 | 0 | 8 |
| [EP-003](EP-003-schemi-attuali-layer-persistenza/EP-003.md) | Documentare gli schemi attuali del layer di persistenza | defined | 0 | 0 | 0 | 1 |

Totale TSK aperti: 10 (sprint corrente 9, lookahead 1).

## Sprint corrente

### EP-001 — Difetti del master: analisi e segnalazione

| TSK | Titolo | US | Layer | Pri | Status | Owner | Dipende da |
|---|---|---|---|---|---|---|---|
| [TSK-001](EP-001-difetti-master-analisi-e-segnalazione/US-012-convenzioni-segnalazione-master/TSK-001.md) | Modello di report di segnalazione e vocabolario di esito | US-012 | docs | P1 | todo | — | — |

### EP-002 — Completare la conoscenza del layer di persistenza

| TSK | Titolo | US | Layer | Pri | Status | Owner | Dipende da |
|---|---|---|---|---|---|---|---|
| [TSK-002](EP-002-conoscenza-layer-di-persistenza/US-013-estrazione-mirata-persistenza/TSK-002.md) | Estrazione repo-sync, fetta A: store applicativo, plugin store, area dati di progetto | US-013 | docs | P0 | todo | — | — |
| [TSK-003](EP-002-conoscenza-layer-di-persistenza/US-013-estrazione-mirata-persistenza/TSK-003.md) | Estrazione repo-sync, fetta B: scritture, sincronizzazione file, log e index, file citati non verificati | US-013 | docs | P0 | todo | — | TSK-002 |
| [TSK-004](EP-002-conoscenza-layer-di-persistenza/US-013-estrazione-mirata-persistenza/TSK-004.md) | Estrazione repo-sync, fetta C: operazioni distruttive, chiamanti, vecchio formato vettoriale | US-013 | docs | P0 | todo | — | TSK-003 |
| [TSK-005](EP-002-conoscenza-layer-di-persistenza/US-013-estrazione-mirata-persistenza/TSK-005.md) | Ingest wiki-keeper delle tre estrazioni e controllo segreti sui raw | US-013 | docs | P0 | todo | — | TSK-002, TSK-003, TSK-004 |
| [TSK-006](EP-002-conoscenza-layer-di-persistenza/US-014-store-applicativo-e-area-dati/TSK-006.md) | Chiudere i punti di US-014 sul raw ingerito: store applicativo, area dati, configurazioni | US-014 | docs | P1 | todo | — | TSK-005 |
| [TSK-007](EP-002-conoscenza-layer-di-persistenza/US-015-atomicita-scritture-e-sync-file/TSK-007.md) | Chiudere i punti di US-015 sul raw ingerito: atomicità delle scritture e sincronizzazione file | US-015 | docs | P1 | todo | — | TSK-005 |
| [TSK-008](EP-002-conoscenza-layer-di-persistenza/US-016-chiamanti-operazioni-distruttive/TSK-008.md) | Chiudere i punti di US-016 sul raw ingerito: chiamanti distruttivi e percorsi legacy | US-016 | docs | P1 | todo | — | TSK-005 |

### EP-003 — Documentare gli schemi attuali del layer di persistenza

| TSK | Titolo | US | Layer | Pri | Status | Owner | Dipende da |
|---|---|---|---|---|---|---|---|
| [TSK-010](EP-003-schemi-attuali-layer-persistenza/US-019-indice-db-schemas-e-relazioni/TSK-010.md) | Indice di db_schemas con identificatori, relazioni e convenzioni di marcatura | US-019 | db | P0 | todo | — | — |

## Lookahead

### EP-002 — Completare la conoscenza del layer di persistenza

| TSK | Titolo | US | Layer | Pri | Status | Owner | Dipende da |
|---|---|---|---|---|---|---|---|
| [TSK-009](EP-002-conoscenza-layer-di-persistenza/US-017-formato-log-e-index-progetto/TSK-009.md) | Chiudere i punti di US-017 sul raw ingerito: formato di log e index del progetto wiki | US-017 | docs | P2 | todo | — | TSK-005 |

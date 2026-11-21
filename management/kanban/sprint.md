---
updated: 2026-11-21
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
| [EP-002](EP-002-conoscenza-layer-di-persistenza/EP-002.md) | Completare la conoscenza del layer di persistenza | defined | 0 | 2 | 0 | 2 |

Totale TSK aperti: 4 (sprint corrente 3, lookahead 1).

## Sprint corrente

### EP-002 — Completare la conoscenza del layer di persistenza

| TSK | Titolo | US | Layer | Pri | Status | Owner | Dipende da |
|---|---|---|---|---|---|---|---|
| [TSK-006](EP-002-conoscenza-layer-di-persistenza/US-014-store-applicativo-e-area-dati/TSK-006.md) | Chiudere i punti di US-014 sul raw ingerito: store applicativo, area dati, configurazioni | US-014 | docs | P1 | in_progress | — | TSK-005 |
| [TSK-007](EP-002-conoscenza-layer-di-persistenza/US-015-atomicita-scritture-e-sync-file/TSK-007.md) | Chiudere i punti di US-015 sul raw ingerito: atomicità delle scritture e sincronizzazione file | US-015 | docs | P1 | in_progress | — | TSK-005 |
| [TSK-008](EP-002-conoscenza-layer-di-persistenza/US-016-chiamanti-operazioni-distruttive/TSK-008.md) | Chiudere i punti di US-016 sul raw ingerito: chiamanti distruttivi e percorsi legacy | US-016 | docs | P1 | todo | — | TSK-005 |

## Lookahead

### EP-002 — Completare la conoscenza del layer di persistenza

| TSK | Titolo | US | Layer | Pri | Status | Owner | Dipende da |
|---|---|---|---|---|---|---|---|
| [TSK-009](EP-002-conoscenza-layer-di-persistenza/US-017-formato-log-e-index-progetto/TSK-009.md) | Chiudere i punti di US-017 sul raw ingerito: formato di log e index del progetto wiki | US-017 | docs | P2 | todo | — | TSK-005 |

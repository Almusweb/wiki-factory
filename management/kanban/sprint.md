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
| [EP-002](EP-002-conoscenza-layer-di-persistenza/EP-002.md) | Completare la conoscenza del layer di persistenza | defined | 0 | 0 | 0 | 1 |
| [EP-004](EP-004-verifica-rischi-di-persistenza/EP-004.md) | Verificare i rischi di persistenza prima di correggerli | defined | 0 | 1 | 0 | 6 |

Totale TSK aperti: 8 (sprint corrente 3, lookahead 5).

## Sprint corrente

### EP-004 — Verificare i rischi di persistenza prima di correggerli

| TSK | Titolo | US | Layer | Pri | Status | Owner | Dipende da |
|---|---|---|---|---|---|---|---|
| [TSK-021](EP-004-verifica-rischi-di-persistenza/US-030-rischio-reindex-senza-rollback/TSK-021.md) | Ingerire il dossier r6 e registrare in wiki l'esito del rischio 6 (re-index senza rollback) | US-030 | docs | P1 | in_progress | — | TSK-020 |
| [TSK-026](EP-004-verifica-rischi-di-persistenza/US-032-rischio-segreti-in-chiaro/TSK-026.md) | Dossier EP-004, rischio 8: lettura dei campi sensibili dello store applicativo, senza valori (repo-sync) | US-032 | docs | P1 | todo | — | TSK-011, TSK-024 |
| [TSK-027](EP-004-verifica-rischi-di-persistenza/US-032-rischio-segreti-in-chiaro/TSK-027.md) | Ingerire il dossier r8 e registrare in wiki l'esito del rischio 8 (segreti in chiaro nello store) | US-032 | docs | P1 | todo | — | TSK-026 |

## Lookahead

### EP-002 — Completare la conoscenza del layer di persistenza

| TSK | Titolo | US | Layer | Pri | Status | Owner | Dipende da |
|---|---|---|---|---|---|---|---|
| [TSK-009](EP-002-conoscenza-layer-di-persistenza/US-017-formato-log-e-index-progetto/TSK-009.md) | Chiudere i punti di US-017 sul raw ingerito: formato di log e index del progetto wiki | US-017 | docs | P2 | todo | — | TSK-005 |

### EP-004 — Verificare i rischi di persistenza prima di correggerli

| TSK | Titolo | US | Layer | Pri | Status | Owner | Dipende da |
|---|---|---|---|---|---|---|---|
| [TSK-022](EP-004-verifica-rischi-di-persistenza/US-028-rischio-atomicita-eterogenea/TSK-022.md) | Dossier EP-004, rischio 4: lettura dell'atomicità di scrittura per archivio (repo-sync) | US-028 | docs | P2 | todo | — | TSK-011, TSK-020 |
| [TSK-023](EP-004-verifica-rischi-di-persistenza/US-028-rischio-atomicita-eterogenea/TSK-023.md) | Ingerire il dossier r4 e registrare in wiki l'esito del rischio 4 (atomicità eterogenea) | US-028 | docs | P2 | todo | — | TSK-022 |
| [TSK-024](EP-004-verifica-rischi-di-persistenza/US-031-rischio-cambio-modello-embedding/TSK-024.md) | Dossier EP-004, rischio 7: lettura della coerenza al cambio di modello o dimensione dell'embedding (repo-sync) | US-031 | docs | P2 | todo | — | TSK-011, TSK-022 |
| [TSK-025](EP-004-verifica-rischi-di-persistenza/US-031-rischio-cambio-modello-embedding/TSK-025.md) | Ingerire il dossier r7 e registrare in wiki l'esito del rischio 7 (cambio modello embedding) | US-031 | docs | P2 | todo | — | TSK-024 |

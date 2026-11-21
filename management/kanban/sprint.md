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
| [EP-002](EP-002-conoscenza-layer-di-persistenza/EP-002.md) | Completare la conoscenza del layer di persistenza | defined | 0 | 2 | 0 | 1 |
| [EP-004](EP-004-verifica-rischi-di-persistenza/EP-004.md) | Verificare i rischi di persistenza prima di correggerli | defined | 0 | 0 | 0 | 10 |

Totale TSK aperti: 13 (sprint corrente 10, lookahead 3).

## Sprint corrente

### EP-002 — Completare la conoscenza del layer di persistenza

| TSK | Titolo | US | Layer | Pri | Status | Owner | Dipende da |
|---|---|---|---|---|---|---|---|
| [TSK-006](EP-002-conoscenza-layer-di-persistenza/US-014-store-applicativo-e-area-dati/TSK-006.md) | Chiudere i punti di US-014 sul raw ingerito: store applicativo, area dati, configurazioni | US-014 | docs | P1 | in_progress | — | TSK-005 |
| [TSK-007](EP-002-conoscenza-layer-di-persistenza/US-015-atomicita-scritture-e-sync-file/TSK-007.md) | Chiudere i punti di US-015 sul raw ingerito: atomicità delle scritture e sincronizzazione file | US-015 | docs | P1 | in_progress | — | TSK-005 |

### EP-004 — Verificare i rischi di persistenza prima di correggerli

| TSK | Titolo | US | Layer | Pri | Status | Owner | Dipende da |
|---|---|---|---|---|---|---|---|
| [TSK-012](EP-004-verifica-rischi-di-persistenza/US-025-rischio-chat-cancellate/TSK-012.md) | Dossier EP-004, rischio 1: lettura del percorso cancella-salva-carica delle chat (repo-sync) | US-025 | docs | P1 | todo | — | TSK-011 |
| [TSK-013](EP-004-verifica-rischi-di-persistenza/US-025-rischio-chat-cancellate/TSK-013.md) | Ingerire il dossier r1 e registrare in wiki l'esito del rischio 1 (chat cancellate) | US-025 | docs | P1 | todo | — | TSK-012 |
| [TSK-014](EP-004-verifica-rischi-di-persistenza/US-026-rischio-identita-progetto/TSK-014.md) | Dossier EP-004, rischio 2: lettura della rigenerazione dell'identità del progetto (repo-sync) | US-026 | docs | P1 | todo | — | TSK-011, TSK-012 |
| [TSK-015](EP-004-verifica-rischi-di-persistenza/US-026-rischio-identita-progetto/TSK-015.md) | Ingerire il dossier r2 e registrare in wiki l'esito del rischio 2 (identità del progetto) | US-026 | docs | P1 | todo | — | TSK-014 |
| [TSK-016](EP-004-verifica-rischi-di-persistenza/US-027-rischio-scritture-registro/TSK-016.md) | Dossier EP-004, rischio 3: lettura delle scritture sul registro dei progetti (repo-sync) | US-027 | docs | P1 | todo | — | TSK-011, TSK-014 |
| [TSK-017](EP-004-verifica-rischi-di-persistenza/US-027-rischio-scritture-registro/TSK-017.md) | Ingerire il dossier r3 e registrare in wiki l'esito del rischio 3 (registro dei progetti) | US-027 | docs | P1 | todo | — | TSK-016 |
| [TSK-020](EP-004-verifica-rischi-di-persistenza/US-030-rischio-reindex-senza-rollback/TSK-020.md) | Dossier EP-004, rischio 6: lettura dell'ordine delle operazioni di ricostruzione dell'indice (repo-sync) | US-030 | docs | P1 | todo | — | TSK-011, TSK-018 |
| [TSK-021](EP-004-verifica-rischi-di-persistenza/US-030-rischio-reindex-senza-rollback/TSK-021.md) | Ingerire il dossier r6 e registrare in wiki l'esito del rischio 6 (re-index senza rollback) | US-030 | docs | P1 | todo | — | TSK-020 |

## Lookahead

### EP-002 — Completare la conoscenza del layer di persistenza

| TSK | Titolo | US | Layer | Pri | Status | Owner | Dipende da |
|---|---|---|---|---|---|---|---|
| [TSK-009](EP-002-conoscenza-layer-di-persistenza/US-017-formato-log-e-index-progetto/TSK-009.md) | Chiudere i punti di US-017 sul raw ingerito: formato di log e index del progetto wiki | US-017 | docs | P2 | todo | — | TSK-005 |

### EP-004 — Verificare i rischi di persistenza prima di correggerli

| TSK | Titolo | US | Layer | Pri | Status | Owner | Dipende da |
|---|---|---|---|---|---|---|---|
| [TSK-018](EP-004-verifica-rischi-di-persistenza/US-029-rischio-logica-duplicata/TSK-018.md) | Dossier EP-004, rischio 5: confronto per lettura delle logiche duplicate TS e Rust (repo-sync) | US-029 | docs | P2 | todo | — | TSK-011, TSK-016 |
| [TSK-019](EP-004-verifica-rischi-di-persistenza/US-029-rischio-logica-duplicata/TSK-019.md) | Ingerire il dossier r5 e registrare in wiki l'esito del rischio 5 (logica duplicata) | US-029 | docs | P2 | todo | — | TSK-018 |

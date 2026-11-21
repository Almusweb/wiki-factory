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
| [EP-004](EP-004-verifica-rischi-di-persistenza/EP-004.md) | Verificare i rischi di persistenza prima di correggerli | defined | 0 | 1 | 0 | 15 |

Totale TSK aperti: 17 (sprint corrente 10, lookahead 7).

## Sprint corrente

### EP-004 — Verificare i rischi di persistenza prima di correggerli

| TSK | Titolo | US | Layer | Pri | Status | Owner | Dipende da |
|---|---|---|---|---|---|---|---|
| [TSK-012](EP-004-verifica-rischi-di-persistenza/US-025-rischio-chat-cancellate/TSK-012.md) | Dossier EP-004, rischio 1: lettura del percorso cancella-salva-carica delle chat (repo-sync) | US-025 | docs | P1 | in_progress | — | TSK-011 |
| [TSK-013](EP-004-verifica-rischi-di-persistenza/US-025-rischio-chat-cancellate/TSK-013.md) | Ingerire il dossier r1 e registrare in wiki l'esito del rischio 1 (chat cancellate) | US-025 | docs | P1 | todo | — | TSK-012 |
| [TSK-014](EP-004-verifica-rischi-di-persistenza/US-026-rischio-identita-progetto/TSK-014.md) | Dossier EP-004, rischio 2: lettura della rigenerazione dell'identità del progetto (repo-sync) | US-026 | docs | P1 | todo | — | TSK-011, TSK-012 |
| [TSK-015](EP-004-verifica-rischi-di-persistenza/US-026-rischio-identita-progetto/TSK-015.md) | Ingerire il dossier r2 e registrare in wiki l'esito del rischio 2 (identità del progetto) | US-026 | docs | P1 | todo | — | TSK-014 |
| [TSK-016](EP-004-verifica-rischi-di-persistenza/US-027-rischio-scritture-registro/TSK-016.md) | Dossier EP-004, rischio 3: lettura delle scritture sul registro dei progetti (repo-sync) | US-027 | docs | P1 | todo | — | TSK-011, TSK-014 |
| [TSK-017](EP-004-verifica-rischi-di-persistenza/US-027-rischio-scritture-registro/TSK-017.md) | Ingerire il dossier r3 e registrare in wiki l'esito del rischio 3 (registro dei progetti) | US-027 | docs | P1 | todo | — | TSK-016 |
| [TSK-020](EP-004-verifica-rischi-di-persistenza/US-030-rischio-reindex-senza-rollback/TSK-020.md) | Dossier EP-004, rischio 6: lettura dell'ordine delle operazioni di ricostruzione dell'indice (repo-sync) | US-030 | docs | P1 | todo | — | TSK-011, TSK-018 |
| [TSK-021](EP-004-verifica-rischi-di-persistenza/US-030-rischio-reindex-senza-rollback/TSK-021.md) | Ingerire il dossier r6 e registrare in wiki l'esito del rischio 6 (re-index senza rollback) | US-030 | docs | P1 | todo | — | TSK-020 |
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
| [TSK-018](EP-004-verifica-rischi-di-persistenza/US-029-rischio-logica-duplicata/TSK-018.md) | Dossier EP-004, rischio 5: confronto per lettura delle logiche duplicate TS e Rust (repo-sync) | US-029 | docs | P2 | todo | — | TSK-011, TSK-016 |
| [TSK-019](EP-004-verifica-rischi-di-persistenza/US-029-rischio-logica-duplicata/TSK-019.md) | Ingerire il dossier r5 e registrare in wiki l'esito del rischio 5 (logica duplicata) | US-029 | docs | P2 | todo | — | TSK-018 |
| [TSK-022](EP-004-verifica-rischi-di-persistenza/US-028-rischio-atomicita-eterogenea/TSK-022.md) | Dossier EP-004, rischio 4: lettura dell'atomicità di scrittura per archivio (repo-sync) | US-028 | docs | P2 | todo | — | TSK-011, TSK-020 |
| [TSK-023](EP-004-verifica-rischi-di-persistenza/US-028-rischio-atomicita-eterogenea/TSK-023.md) | Ingerire il dossier r4 e registrare in wiki l'esito del rischio 4 (atomicità eterogenea) | US-028 | docs | P2 | todo | — | TSK-022 |
| [TSK-024](EP-004-verifica-rischi-di-persistenza/US-031-rischio-cambio-modello-embedding/TSK-024.md) | Dossier EP-004, rischio 7: lettura della coerenza al cambio di modello o dimensione dell'embedding (repo-sync) | US-031 | docs | P2 | todo | — | TSK-011, TSK-022 |
| [TSK-025](EP-004-verifica-rischi-di-persistenza/US-031-rischio-cambio-modello-embedding/TSK-025.md) | Ingerire il dossier r7 e registrare in wiki l'esito del rischio 7 (cambio modello embedding) | US-031 | docs | P2 | todo | — | TSK-024 |

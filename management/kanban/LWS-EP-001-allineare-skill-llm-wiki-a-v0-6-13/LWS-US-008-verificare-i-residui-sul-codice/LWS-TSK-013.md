---
id: LWS-TSK-013
title: "Ingest wiki-keeper degli esiti delle estrazioni e aggiornamento dei gap"
us: LWS-US-008
sprint: 01
layer: docs
consumer: human
priority: P2
estimate: S
status: done
depends_on: [LWS-TSK-011, LWS-TSK-012]
blocked_by: []
code_path: ["wiki/**"]
started_at: 2026-11-23
closed_at: 2026-11-23
decision_refs: []
---

# LWS-TSK-013 — Ingest degli esiti e aggiornamento dei gap

## Context
Gli esiti delle due estrazioni devono entrare in wiki attraverso `wiki-keeper`, mai scritti direttamente dal product-manager. L'ingest aggiorna i gap interessati. Le correzioni della skill che ne derivano diventano proposte, non modifiche. [^src: management/kanban/LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-008-verificare-i-residui-sul-codice/LWS-US-008.md §Acceptance Criteria]

## Technical Specs
- **Consumer:** `human` (l'ingest lo avvia la sessione principale con `/sync-docs` o il flusso `wiki-keeper`). **Nessun `target`:** non si tocca alcun repo cliente.
- **Input:** i due raw prodotti da `LWS-TSK-011` e `LWS-TSK-012`.
- **Gap da aggiornare** (chiusi, ristretti o aperti con motivo): `llm-wiki-skill-punti-da-verificare`, `llm-wiki-affermazioni-codice-da-verificare`, `llm-wiki-api-corpi-handler-non-letti`, `llm-wiki-source-watch-default`, `llm-wiki-watch-all-projects-residui`, `llm-wiki-prove-in-esecuzione-aperte`.
- **Non bloccante:** non è prerequisito di `LWS-TSK-014` né di `LWS-TSK-016`.
- **Incorporazione nella skill:** gli esiti non entrano nella skill. Se arrivano prima della chiusura di `LWS-TSK-009` e `LWS-TSK-010`, si incorporano solo per decisione esplicita dell'utente; altrimenti si registrano come storie nuove o PR successiva.
- Fonti: [^src: wiki/gaps.md §2026-11-22 12:39 — llm-wiki-affermazioni-codice-da-verificare] [^src: wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md §Che cosa resta da verificare]

## Implementation Steps
1. Verificare `LWS-TSK-011` e `LWS-TSK-012` chiusi e i raw presenti nel manifest.
2. Ingest con `wiki-keeper`.
3. Per ciascun gap: stato aggiornato con il motivo.
4. Elencare le correzioni della skill proposte dagli esiti, senza applicarle; ricordare la regola di incorporazione.
5. `python3 tools/lint/run-deterministic.py` e riportare l'esito.

## Definition of Done
- [x] Esiti ingeriti; nulla scritto in `wiki/` fuori dal flusso `wiki-keeper`.
- [x] Sei gap aggiornati con stato e motivo.
- [x] Correzioni proposte elencate come non applicate.

## Chiusura

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-008 AC4 | soddisfatto | 6 correzioni proposte dal keeper, nessuna applicata; code_repos non toccato |
| LWS-US-008 AC5 | soddisfatto | gap: 1 chiuso (source-watch-default), 5 ristretti e aperti con motivo; run-deterministic 0 ERROR, verify_gap_closures --check ok |

## Dependencies
- LWS-TSK-011 — estrazione A.
- LWS-TSK-012 — estrazione B.

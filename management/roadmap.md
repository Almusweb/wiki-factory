---
type: roadmap
status: active
created: 2026-11-20
updated: 2026-11-20
---

# Roadmap — wiki-factory

## Release 1
Tutte e quattro le epiche hanno confidence uguale o sopra il 50%.

Ordine di lavoro:

1. **EP-002 — Completare la conoscenza del layer di persistenza** (high, 65%). Chiude i gap di persistenza con una nuova estrazione mirata.
2. **EP-003 — Documentare gli schemi attuali del layer di persistenza** (high, 80%). Fa esistere `design_&_architecture/db_schemas/`, prerequisito di `db-dev`. Indipendente a livello di epica da EP-002; solo US-023 dipende da US-014.
3. **EP-004 — Verificare i rischi di persistenza prima di correggerli** (high, 55%). Le storie di verifica dipendono da storie di EP-002 (US-016, US-015, US-014).
4. **EP-001 — Difetti del master: analisi e segnalazione** (medium, 70%). In parallelo alle altre tre, perché indipendente: riguarda il meta-framework, non l'applicazione.

## Non pianificato
Gli interventi sul codice del layer di persistenza non sono pianificati prima di US-033 (sintesi dei rischi). Le storie di correzione si scrivono dopo, solo per i rischi confermati, e `db-dev` interviene solo dopo EP-003.

## Release 1.1+
Nessuna epica con confidence sotto 50% al momento.

## Question soft aperte
Aperta solo Q_004 (EP-002, US-018). Q_001, Q_002 e Q_003 sono chiuse il 2026-11-20 17:36. Dettagli in `management/questions.md`.

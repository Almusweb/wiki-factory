---
id: LWS-US-008
title: Verificare sul codice i soli residui
role: Maintainer della fork della skill llm-wiki
priority: medium
status: done
wiki_page: wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md
blocked_by: []
pending_clarification: []
depends_on: []
started_at: 2026-11-23
closed_at: 2026-11-23
---

# LWS-US-008 — Verificare sul codice i soli residui

## Descrizione
Come maintainer della fork della skill `llm-wiki`, voglio far leggere nel codice di `llm_wiki` a `e08cfce` i soli punti rimasti non verificati, affinché la skill si completi senza congetture e la PR dichiari con precisione ciò che resta fuori.

## Business Rules
- Regole trasversali dell'epica LWS-EP-001: valgono tutte.
- Storia **non bloccante** (decisione dell'utente D2): corre in parallelo e non è prerequisito di LWS-US-009 né di LWS-US-010.
- Il product-manager non scrive raw. L'estrazione è un `repo-sync` mirato su `code_repos/llm_wiki` a `e08cfce` (upstream v0.6.13), in sola lettura; `wiki-keeper` lo ingerisce e aggiorna i gap. Nessun esito è scritto direttamente in `wiki/` da questa storia.
- Nessuna nuova prova in esecuzione è pianificata (decisione dell'utente): le prove aperte restano «non verificate» e la PR le dichiara.
- Il nome della storia dice «soli residui»: non si rileggono i punti già chiusi o confermati dalla verifica sul codice del 2026-11-22.

### Residui reali (da leggere nel codice)
| Residuo | Gap |
|---|---|
| `handle_write_page`, `handle_chat`, `respond_chat_sse` e header della risposta SSE di successo | `llm-wiki-affermazioni-codice-da-verificare` |
| Struttura di `AgentChatRequest` ed eventi agente | `llm-wiki-api-corpi-handler-non-letti` |
| Corpi di `embed_wiki_page` e payload di `PATCH` e `resolve` delle review | `llm-wiki-api-corpi-handler-non-letti` |
| Campi di `rescan_project_files` ed elenco completo dei `kind` di `changedTasks` | `llm-wiki-skill-punti-da-verificare` |
| Codice del body generico troppo grande | `llm-wiki-skill-punti-da-verificare` |
| Default di `sourceWatchConfig` | `llm-wiki-source-watch-default` |
| Scala RRF e campi per risultato di `search`; `resolve_query_embedding` | `llm-wiki-skill-punti-da-verificare` |
| `offset`, `totalCount`, `hasMore` e cache di 5 s del grafo nel codice | `llm-wiki-skill-punti-da-verificare` |
| Limiti di corpo per route e ordine rispetto all'auth, riletti | `llm-wiki-skill-punti-da-verificare` |
| «Watch all projects»: default, LLM nel ramo inattivi, progetti recenti | `llm-wiki-watch-all-projects-residui` |
| Voci V20, V21, V22 e la soglia del 5% (V4) | `llm-wiki-affermazioni-codice-da-verificare` |

[^src: wiki/gaps.md §2026-11-22 11:24 — llm-wiki-skill-punti-da-verificare]
[^src: wiki/gaps.md §2026-11-22 12:39 — llm-wiki-affermazioni-codice-da-verificare]
[^src: wiki/gaps.md §2026-11-22 13:30 — llm-wiki-watch-all-projects-residui]
[^src: wiki/gaps.md §2026-11-21 07:31 — llm-wiki-api-corpi-handler-non-letti]
[^src: wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md §Che cosa resta da verificare]

## UI Reference
[^src: wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md §Che cosa resta da verificare]
[^src: wiki/concepts/llm-wiki-api-osservazioni-esecuzione-v0-6-13.md §Cosa questa prova non copre]

## Acceptance Criteria
- [x] È emessa una richiesta di estrazione mirata a `repo-sync` per `code_repos/llm_wiki` a `e08cfce` con l'elenco dei residui sopra; l'estrazione e l'ingest sono eseguiti dai ruoli competenti (non dal product-manager).
- [x] L'esito di ciascun residuo è «confermato», «smentito» o «non conclusivo», con file e riga riportati dal raw ingerito.
- [x] Le prove in esecuzione non pianificate restano elencate come «non verificate» e non sono portate nella skill: scritture con token, chat, `pages/embed`, 429 e 503 sotto carico, 413 e 415 sul contenuto, bind LAN, `allowUnauthenticated`, rescan su progetto non aperto, embedding attivi, corsa review/auto-save.
- [x] Le correzioni della skill che derivano dagli esiti non entrano in questa storia: diventano storie nuove o una PR successiva; se l'esito arriva prima della chiusura di LWS-US-007 può essere incorporato solo per decisione esplicita dell'utente.
- [x] I gap interessati sono aggiornati dal wiki-keeper (chiusi, ristretti o ancora aperti con il motivo).

## Fonti
[^src: wiki/gaps.md §2026-11-22 12:39 — llm-wiki-affermazioni-codice-da-verificare]
[^src: wiki/gaps.md §2026-11-22 12:39 — llm-wiki-prove-in-esecuzione-aperte]

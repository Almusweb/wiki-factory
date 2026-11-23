---
id: LWS-US-007
title: Scritture, chat e rescan
role: Agente AI che usa la skill llm-wiki
priority: high
status: done
wiki_page: wiki/concepts/llm-wiki-api-locale.md
blocked_by: []
pending_clarification: []
depends_on: [LWS-US-002]
started_at: 2026-11-23
closed_at: 2026-11-23
---

# LWS-US-007 — Scritture, chat e rescan

## Descrizione
Come agente AI che usa la skill `llm-wiki`, voglio che la skill dica quali route scrivono nella v0.6.13, che `chat` esiste e come si comporta il rescan, affinché non eviti route che esistono, non creda che ogni id non corrente sia in sola lettura e usi le scritture solo su richiesta esplicita dell'utente.

## Business Rules
- Regole trasversali dell'epica LWS-EP-001: valgono tutte.
- Copre D1, D2, D3, D21; incoerenze n. 12 e n. 13 (parte nota); V16, V17, V18, V19, V20.
- Decisione sui corpi non noti (D3 dell'utente): per `chat`, `PATCH` e `resolve` delle review e `pages/embed` si documentano solo esistenza, auth, limiti ed errori. Per `pages/write` il corpo è noto da codice e si riporta.
- Decisione sulle scritture (D4 dell'utente): lettura per default; le route che scrivono, `embed` e `chat` si usano solo su richiesta esplicita dell'utente.
- Non si portano come fatti: la sovrascrittura delle review da parte dell'auto-save (deduzione non provata), la perdita dei cambi dopo un rescan su progetto non aperto (inferenza), il codice 499 (non in wiki), il rapporto fra scritture manuali e watcher (V21, da verificare).

### Evidenza dei fatti
| Fatto | Livello |
|---|---|
| D1: `PATCH`, `DELETE` e `resolve` delle review riscrivono `.llm-wiki/review.json` del progetto indicato | [C]; non in esecuzione |
| D1: `pages/write` accetta `{path, content, allowOverwrite}`; 409 se la pagina esiste senza `allowOverwrite`; 400 per path, markdown o dimensione; 500 altrimenti | [C] contratto; l'interno di `handle_write_page` non è letto |
| D2: `chat` risponde in JSON o SSE (eventi `meta`, `agent`, `done`, `cancelled`, `error`), token sempre richiesto, rotta di cancel; `/health` riporta `agent.chat: true` | [C] contratto + [E] solo il flag; `handle_chat` e `respond_chat_sse` non letti, la chat non è stata provata |
| D3: `reviews` in lettura | [E+C] (campi osservati) |
| D3: `pages/embed` (400 se l'embedding non è configurato, 503 con 4 embed in volo), `pages/write`, `chat/{sessionId}/cancel` | [C] contratto; non in esecuzione |
| D21 e V19: `resolve_project` non verifica `current`; review, rescan ed embed agiscono su qualunque progetto indicato | [C]; `handle_write_page` e `handle_chat` non letti |
| V16-V18: il rescan non accoda nella coda di ingest dell'app ma aggiorna lo snapshot e accoda i cambi nella coda Rust; `changedTasks` vuoto significa già visto; `created` e `modified` avviano l'ingest; l'ingest parte per il progetto aperto con `enabled`, `autoIngest` e un LLM; per i progetti inattivi dipende da «Watch all projects» | [C] parziale |
| «Watch all projects»: default, LLM nel ramo inattivi; elenco completo dei `kind` | non noti |

[^src: wiki/syntheses/llm-wiki-skill-vs-app-v0-6-13.md §Aggiornamenti (v2026-11-22, verifica sul codice)]
[^src: wiki/concepts/llm-wiki-api-locale.md §Aggiornamenti (v2026-11-21)]
[^src: wiki/concepts/llm-wiki-review-store-e-auto-save.md §Dettaglio]
[^src: wiki/concepts/llm-wiki-sincronizzazione-file.md §Dettaglio]
[^src: wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md §Esito per voce]
[^src: wiki/gaps.md §2026-11-22 13:30 — llm-wiki-watch-all-projects-residui]

## UI Reference
[^src: wiki/concepts/llm-wiki-skill-api-v1-dichiarata.md §Sola lettura contro scrittura]
[^src: wiki/concepts/llm-wiki-skill-api-v1-dichiarata.md §`POST /projects/{id}/chat`]
[^src: wiki/concepts/llm-wiki-skill-api-v1-dichiarata.md §`POST /projects/{id}/sources/rescan`]

## Acceptance Criteria
- [x] In nessuno dei quattro file compaiono più «unico endpoint di scrittura `rescan`», «nessun endpoint di scrittura in v1» né l'invito a non inventarne, «`/chat` risponde 501», «non chiamare `/chat`» né «le chiamate su un id non corrente sono in sola lettura». Verifica: ricerca testuale su queste formule nei quattro file, compresi gli anti-pattern di `examples.md`. (LWS-TSK-009 §Chiusura, AC1)
- [x] La skill dice che scrivono `PATCH`, `DELETE` e `resolve` delle review, `pages/write`, `pages/embed` e `chat` (sessioni agente), e che review, rescan ed embed operano su qualunque progetto indicato, non solo su `current`. (LWS-TSK-009 §Chiusura, AC2)
- [x] Le route `reviews`, `pages/embed`, `pages/write` e `chat/{sessionId}/cancel` sono in `api-reference.md` e `SKILL.md` con solo ciò che la wiki sa: metodo, auth, limiti ed errori e, per `pages/write`, il corpo noto. I corpi di `AgentChatRequest`, di `PATCH` e `resolve` delle review e di `pages/embed` non sono descritti; la lacuna è dichiarata oppure la voce resta minima. (LWS-TSK-009 §Chiusura, AC3)
- [x] `chat` è descritta come JSON o SSE con eventi `meta`, `agent`, `done`, `cancelled`, `error`, token sempre richiesto e rotta di cancel; la skill non descrive il corpo della richiesta, il keepalive né l'esito della cancellazione. (LWS-TSK-009 §Chiusura, AC4)
- [x] La skill istruisce l'agente a usare le route che scrivono, `embed` e `chat` solo su richiesta esplicita dell'utente; il rischio di sovrascrittura delle review non è presentato come fatto. (LWS-TSK-009 §Chiusura, AC5)
- [x] Il rescan è descritto così: aggiorna lo snapshot e riporta `changedTasks`; `changedTasks` vuoto significa già visto; non accoda da sé l'ingest; l'ingest parte per il progetto aperto alle condizioni note. La skill non afferma che i cambi si perdano né che l'ingest parta per i progetti inattivi. (LWS-TSK-010 §Chiusura, AC6)
- [x] Per `changedTasks[].kind` la skill riporta solo che `created` e `modified` avviano l'ingest, senza elenco completo (n. 13). (LWS-TSK-010 §Chiusura, AC7)
- [x] Il codice 499 non compare; il 409 compare solo per `pages/write`. (LWS-TSK-010 §Chiusura, AC8)
- [x] Almeno una ricetta di `examples.md` mostra una delle route nuove, senza il corpo non noto. (LWS-TSK-010 §Chiusura, AC9)
- [x] Ogni affermazione cambiata ha nel TSK la riga di evidenza corrispondente; nessuna è priva di evidenza. (LWS-TSK-009 §Chiusura, AC10, per route che scrivono, chat e postura; LWS-TSK-010 §Chiusura, AC10, per rescan, `kind` e ricetta)

## Nota di modifica
- 2026-11-23 — Chiusura (rollup; fonte: tabelle §Chiusura di LWS-TSK-009 e LWS-TSK-010, entrambi `done`). Prima: `status: ready`, AC non spuntati. Ora: `status: done`, AC1..AC10 spuntati con riferimento ai TSK pertinenti (AC1..AC5 da LWS-TSK-009; AC6..AC9 da LWS-TSK-010; AC10 da entrambi, ciascuno per la sua parte); commit nel repo della skill `d3d3fd4` e `c73a69c` sul branch `docs/align-v0-6-13`; `started_at` e `closed_at` 2026-11-23 (date del lavoro, dai TSK). Nessun AC derogato. Decisioni dell'utente riportate dai TSK: il qualificatore «0.4.x» per il 501 è tolto con la riga e la dichiarazione di versione di `README.md` resta a LWS-TSK-014; `README.md` r. 113 («Ingest is queued by the UI only for the open project») è rinviato a LWS-TSK-014.

## Fonti
[^src: wiki/syntheses/llm-wiki-skill-vs-app-v0-6-13.md §Dettaglio]
[^src: wiki/entities/llm-wiki-skill.md §Incoerenze interne della skill (materiale per la PR)]

---
id: LWS-TSK-009
title: "Route che scrivono, chat e postura sulle scritture nella skill"
us: LWS-US-007
sprint: 01
layer: docs
consumer: agent
priority: P1
estimate: M
status: todo
depends_on: [LWS-TSK-008]
blocked_by: []
code_path: ["code_repos/llm_wiki_skill/SKILL.md", "code_repos/llm_wiki_skill/api-reference.md", "code_repos/llm_wiki_skill/examples.md", "code_repos/llm_wiki_skill/README.md"]
target: llm_wiki_skill
started_at:
closed_at:
decision_refs: []
---

# LWS-TSK-009 — Scritture, chat e postura

## Context
Prima parte di LWS-US-007 (AC1-AC5, AC10): route che scrivono (`reviews`, `pages/write`, `pages/embed`), `chat` e postura «lettura per default». Copre D1, D2, D3, D21; n. 12; V16-V20 per la parte di route. Il rescan è `LWS-TSK-010`. `README.md` va toccato solo se contiene le formule da togliere (AC1). `depends_on` su `LWS-TSK-008` per sovrapposizione di file e perché le route nuove devono esistere quando i limiti le citano. [^src: management/kanban/LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-007-scritture-chat-e-rescan/LWS-US-007.md §Acceptance Criteria]

## Technical Specs
- **Layer docs, consumer agent, target `llm_wiki_skill`.** Branch condiviso.
- **Corpi non noti** (`chat`/`AgentChatRequest`, `PATCH` e `resolve` delle review, `pages/embed`): solo esistenza, auth, limiti ed errori; la lacuna è dichiarata o la voce resta minima. Per `pages/write` il corpo è noto da codice e si riporta.
- **Non si portano come fatti:** sovrascrittura delle review da auto-save (deduzione), perdita dei cambi dopo rescan su progetto non aperto (inferenza), codice 499, rapporto fra scritture manuali e watcher (V21).
- **Evidenza dei fatti:**

| Fatto | Livello |
|---|---|
| D1: `PATCH`, `DELETE`, `resolve` delle review riscrivono `.llm-wiki/review.json` del progetto indicato | [C]; non in esecuzione |
| D1: `pages/write` accetta `{path, content, allowOverwrite}`; 409 se esiste senza `allowOverwrite`; 400 per path, markdown, dimensione; 500 altrimenti | [C] contratto; interno di `handle_write_page` non letto |
| D2: `chat` risponde in JSON o SSE (eventi `meta`, `agent`, `done`, `cancelled`, `error`), token sempre richiesto, rotta di cancel; `/health` riporta `agent.chat: true` | [C] contratto + [E] solo il flag; `handle_chat` e `respond_chat_sse` non letti |
| D3: `reviews` in lettura | [E+C] |
| D3: `pages/embed` (400 se embedding non configurato, 503 con 4 embed in volo), `pages/write`, `chat/{sessionId}/cancel` | [C] contratto; non in esecuzione |
| D21 e V19: `resolve_project` non verifica `current`; review, rescan ed embed agiscono su qualunque progetto indicato | [C]; `handle_write_page` e `handle_chat` non letti |

- Fonti: [^src: wiki/syntheses/llm-wiki-skill-vs-app-v0-6-13.md §Aggiornamenti (v2026-11-22, verifica sul codice)] [^src: wiki/concepts/llm-wiki-api-locale.md §Aggiornamenti (v2026-11-21)] [^src: wiki/concepts/llm-wiki-review-store-e-auto-save.md §Dettaglio] [^src: wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md §Esito per voce]

## Vincoli comuni (TSK docs di contenuto)
- Prima di scrivere: `git -C code_repos/llm_wiki_skill branch --show-current` = branch condiviso; altrimenti STOP.
- Si scrive solo nei file di `code_path`; nessun file nuovo, codice o script.
- Testi della skill senza ID kanban, riferimenti a ADR, wiki o factory, attribution AI o `Co-Authored-By`; [C]/[E] solo nel TSK.
- Se la wiki non documenta un comportamento v0.6.13, la skill non lo afferma.
- Commit: non lo esegue il dev-agent; propone un messaggio generico senza ID; la sessione principale lo esegue con `tools/vcs/sm_commit.py` dopo OK esplicito. `done` solo dopo il commit; Chiusura con i tre campi (dichiarati, committati, working tree).

## Implementation Steps
1. Verifica del branch.
2. Togliere dai quattro file (anti-pattern di `examples.md` compresi) le formule: «unico endpoint di scrittura `rescan`», «nessun endpoint di scrittura in v1» e l'invito a non inventarne, «`/chat` risponde 501», «non chiamare `/chat`», «le chiamate su un id non corrente sono in sola lettura».
3. Aggiungere in `api-reference.md` e `SKILL.md` le route `reviews`, `pages/embed`, `pages/write`, `chat/{sessionId}/cancel` con solo metodo, auth, limiti, errori e, per `pages/write`, il corpo noto.
4. Descrivere `chat` (JSON o SSE, eventi, token sempre richiesto, cancel) senza corpo, keepalive o esito della cancellazione.
5. Istruire l'agente a usare scritture, `embed` e `chat` solo su richiesta esplicita dell'utente; dire che review, rescan ed embed operano su qualunque progetto indicato.
6. Ricerca testuale sulle formule rimosse con comando ed esito.

## Definition of Done
- [ ] AC1..AC5 di LWS-US-007 verificati con ricerca testuale e hunk.
- [ ] AC10: riga di evidenza per ogni affermazione cambiata.
- [ ] Nessuna traccia nei file toccati.

## Chiusura
<!-- AC6-AC9 sono di LWS-TSK-010 -->

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-007 AC1 | | |
| LWS-US-007 AC2 | | |
| LWS-US-007 AC3 | | |
| LWS-US-007 AC4 | | |
| LWS-US-007 AC5 | | |
| LWS-US-007 AC10 | | |

## Dependencies
- LWS-TSK-008 — serializzazione per sovrapposizione di file.

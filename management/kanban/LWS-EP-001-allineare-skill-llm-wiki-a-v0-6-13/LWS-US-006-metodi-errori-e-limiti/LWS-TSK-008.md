---
id: LWS-TSK-008
title: "Metodi, preflight, rate limit, limiti di corpo e Retry-After nella skill"
us: LWS-US-006
sprint: 01
layer: docs
consumer: agent
priority: P1
estimate: M
status: todo
depends_on: [LWS-TSK-007]
blocked_by: []
code_path: ["code_repos/llm_wiki_skill/SKILL.md", "code_repos/llm_wiki_skill/api-reference.md", "code_repos/llm_wiki_skill/examples.md", "code_repos/llm_wiki_skill/README.md"]
target: llm_wiki_skill
started_at:
closed_at:
decision_refs: []
---

# LWS-TSK-008 — Metodi, errori e limiti

## Context
La skill interpreta 404, 405, 413 e 429 con regole vecchie. Copre D11, D12; n. 1 (parte nota), n. 7, n. 8; V14, V15; A4 (corpo oltre 1 MB che dà 400 e 413). Il codice del body generico troppo grande non è noto: la skill non ne indica uno. `depends_on` su `LWS-TSK-007` per sovrapposizione di file. [^src: management/kanban/LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-006-metodi-errori-e-limiti/LWS-US-006.md §Acceptance Criteria]

## Technical Specs
- **Layer docs, consumer agent, target `llm_wiki_skill`.** Branch condiviso.
- **Evidenza dei fatti:**

| Fatto | Livello |
|---|---|
| D11: 405 solo fuori da GET, POST, PATCH, DELETE; un verbo o rotta sbagliata fra gli ammessi dà 404; `OPTIONS` dà 204 con CORS prima di ogni altro controllo | [C+E] parziale |
| D11: 401 anche su route inesistenti e metodi sbagliati, senza token | [E] |
| n. 8: preflight `Access-Control-Max-Age: 600` | [E+C] |
| D12: finestra di 1 s con 120 richieste; `/health` e `OPTIONS` esclusi; rate limit prima dell'auth; 503 oltre 64 in volo, 8 stream chat, 4 embed | [C] |
| D12: body di `chat` 40 MiB, `pages/write` circa 12 MiB, body generico 1 MiB | [C] (da raw api-mcp, non riletti) |
| n. 7: `Retry-After` assente nei percorsi letti (riserva sugli header della risposta SSE di successo) | [C] |
| n. 1: `pages/write` troppo grande: 400 | [C] |
| n. 1: codice del body generico troppo grande | non noto |
| 429 e 503 sotto carico | non provati in esecuzione |

- Fonti: [^src: wiki/syntheses/llm-wiki-skill-vs-app-v0-6-13.md §Aggiornamenti (v2026-11-22, verifica sul codice)] [^src: wiki/concepts/llm-wiki-api-locale.md §Aggiornamenti (v2026-11-21)] [^src: wiki/concepts/llm-wiki-api-osservazioni-esecuzione-v0-6-13.md §Osservazioni del 2026-11-13 (app 0.6.13, progetto reale, non replicate)] [^src: wiki/gaps.md §2026-11-22 11:24 — llm-wiki-skill-punti-da-verificare]

## Vincoli comuni (TSK docs di contenuto)
- Prima di scrivere: `git -C code_repos/llm_wiki_skill branch --show-current` = branch condiviso; altrimenti STOP.
- Si scrive solo nei file di `code_path`; nessun file nuovo, codice o script.
- Testi della skill senza ID kanban, riferimenti a ADR, wiki o factory, attribution AI o `Co-Authored-By`; [C]/[E] solo nel TSK.
- Se la wiki non documenta un comportamento v0.6.13, la skill non lo afferma.
- Commit: non lo esegue il dev-agent; propone un messaggio generico senza ID; la sessione principale lo esegue con `tools/vcs/sm_commit.py` dopo OK esplicito. `done` solo dopo il commit; Chiusura con i tre campi (dichiarati, committati, working tree).

## Implementation Steps
1. Verifica del branch.
2. Metodi ammessi, 405 contro 404, `OPTIONS` 204; chiudere la contraddizione 405/preflight; preflight 600 s.
3. Rate limit prima dell'auth, esclusioni, 120 per 1 s con 429; tabella dei limiti con corpi `chat` 40 MiB, `pages/write` ~12 MiB, 8 stream chat e 4 embed in volo, 1 MiB generale.
4. `Retry-After`: non affermarne l'esistenza; attese consigliate come prudenza dell'agente.
5. `pages/write` troppo grande: 400; corpo generico: nessun codice, niente doppia indicazione 400/413.
6. Controlli testuali con comando ed esito.

## Definition of Done
- [ ] AC1..AC5 verificati con ricerca testuale e hunk.
- [ ] AC6: riga di evidenza per ogni affermazione cambiata (429, 503, limiti di corpo marcati «non provati in esecuzione»).
- [ ] Nessuna traccia nei file toccati.

## Chiusura

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-006 AC1 | | |
| LWS-US-006 AC2 | | |
| LWS-US-006 AC3 | | |
| LWS-US-006 AC4 | | |
| LWS-US-006 AC5 | | |
| LWS-US-006 AC6 | | |

## Dependencies
- LWS-TSK-007 — serializzazione per sovrapposizione di file.

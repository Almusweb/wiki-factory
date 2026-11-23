---
id: LWS-TSK-008
title: "Metodi, preflight, rate limit, limiti di corpo e Retry-After nella skill"
us: LWS-US-006
sprint: 01
layer: docs
consumer: agent
priority: P1
estimate: M
status: done
depends_on: [LWS-TSK-007]
blocked_by: []
code_path: ["code_repos/llm_wiki_skill/SKILL.md", "code_repos/llm_wiki_skill/api-reference.md", "code_repos/llm_wiki_skill/examples.md", "code_repos/llm_wiki_skill/README.md"]
target: llm_wiki_skill
started_at: 2026-11-23
closed_at: 2026-11-23
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
- [x] AC1..AC5 verificati con ricerca testuale e hunk.
- [x] AC6: riga di evidenza per ogni affermazione cambiata (429, 503, limiti di corpo marcati «non provati in esecuzione»).
- [x] Nessuna traccia nei file toccati.

## Chiusura

**Diff di chiusura (a comando, 2026-11-23).**
- Dichiarati: `code_repos/llm_wiki_skill/SKILL.md`, `api-reference.md`, `examples.md`, `README.md` (stessi quattro file di `code_path`).
- Committati: `887df67` nel repo della skill (4 file, 26+/21-), dopo OK esplicito dell'utente in chat (2026-11-23); `sm_commit.py --dry-run` → messaggio invariato; `git log -1` senza trailer né attribution. Dopo il commit `git status --short` della skill vuoto. Factory: commit con questo TSK, la sola entry di handoff di `wiki/log.md` (stage parziale) e il puntatore; `sprint.md` escluso (lavoro non committato di un'altra sessione sullo stesso clone).
- Punti dubbi 1-4 (decisione dell'utente, 2026-11-23): lasciati come proposti. Punto 5 (`chat` 501 on 0.4.x, frase su `pages/write` in `examples.md` r.273) rinviato a LWS-TSK-009.
- Nel working tree: `git -C code_repos/llm_wiki_skill status --short` → ` M README.md`, ` M SKILL.md`, ` M api-reference.md`, ` M examples.md`; `git diff --stat` → 4 file, 26 inserzioni, 21 cancellazioni. Nessun file nuovo. Branch verificato prima di scrivere: `git branch --show-current` → `docs/align-v0-6-13`.

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-006 AC1 | Verificato (ricerca testuale `405`, `404`, `OPTIONS`; hunk sotto) | `api-reference.md` §Methods: «The allowed methods are GET, POST, PATCH and DELETE. `OPTIONS` is the CORS preflight: it gets 204 before any other check, so it is never a 405. 405 appears only for other verbs (e.g. `PUT`) ... A wrong verb among the four allowed ones ... → **404**». `SKILL.md` r.190: «Only for verbs outside GET, POST, PATCH and DELETE ... `OPTIONS` is not a 405: it gets 204 with the CORS headers, before every other check». Contraddizione 405/preflight chiusa: tolte la riga che metteva `OPTIONS` fra i verbi del 405 e la frase «Non-GET / non-POST methods → 405 (0.4.x only)». |
| LWS-US-006 AC2 | Verificato (ricerca `Max-Age\|600`, `10 min`) | `api-reference.md` r.460: «A preflight response carries `Access-Control-Max-Age: 600`: a browser may cache it for 600 seconds (10 minutes).» La frase «OPTIONS → 204 without auth» è sostituita da «204 with the CORS headers, before every other check: no token is needed and the rate limit does not count it». |
| LWS-US-006 AC3 | Verificato (ricerca `120`, `1 MiB\|1 MB`, `40 MiB`, `12 MiB`, `sliding`) | `api-reference.md` tabella: «Rate limit \| 120 requests per 1 s window, global; `/health` and `OPTIONS` excluded; applied before the token check \| 429»; righe nuove «Request body, `chat` \| 40 MiB», «`pages/write` \| about 12 MiB», «Chat streams in flight \| 8», «Page embeds in flight \| 4»; il generico 1 MiB resta. Nota sotto la tabella: «The body limits, the rate limit and the in-flight limits come from the app code. They were not tested by running the app: the 429 and 503 responses were not seen under load.» «sliding» tolto (non è nei fatti). Nessuna sezione descrittiva di `chat` o `pages/write` reintrodotta. |
| LWS-US-006 AC4 | Verificato (ricerca `Retry-After`) | `api-reference.md` §`Retry-After`: «Do not assume that the server sends it. In the response paths known for 0.6.13, 429 and 503 carry no `Retry-After` header (the headers of a successful SSE response are not known). The waits suggested here, at least 1 s after a 429 and at least 2 s after a 503, are the agent's own caution, not a value from the server.» `SKILL.md` r.193 e r.196, `README.md` r.110-111 e `examples.md` r.283 allineati (nessuna frase assoluta «no `Retry-After` header»). |
| LWS-US-006 AC5 | Verificato (ricerca `413`, `1 MiB\|1 MB`) | `api-reference.md` r.446: «`pages/write` ... Too large → 400»; r.444: «generic ... The status code for a body over the limit is not known: do not rely on a specific one». `SKILL.md` r.186 (400: «a `pages/write` body that is too large») e r.191 (413: tolto «or request body > 1 MB»; aggiunta la frase «not known»). Nessuna doppia indicazione 400/413 sul corpo generico (ricerca `1 MiB\|1 MB` → 4 righe, nessuna con un codice). |
| LWS-US-006 AC6 | Verificato (tabella sotto) | Ogni affermazione cambiata ha una riga con livello e riga di evidenza; 429 e 503 sotto carico e limiti di corpo dichiarati nel testo come non provati in esecuzione. |

**Affermazioni cambiate (AC6).** Il numero fra parentesi indica la riga della tabella «Evidenza dei fatti» di questo TSK (1 = D11 metodi, 2 = D11 401, 3 = n. 8, 4 = D12 rate limit e in volo, 5 = D12 corpi, 6 = n. 7, 7 = n. 1 `pages/write`, 8 = n. 1 generico, 9 = 429 e 503 non provati).

| File | Affermazione | Livello | Riga |
|---|---|---|---|
| `SKILL.md` r.190, `api-reference.md` §Methods | 405 solo fuori da GET, POST, PATCH, DELETE; `OPTIONS` mai 405 | [C+E] parziale | (1) |
| `SKILL.md` r.189, `api-reference.md` §Methods | verbo sbagliato fra gli ammessi → 404 | [C+E] parziale | (1) |
| `api-reference.md` r.461 | `OPTIONS` → 204 con CORS prima di ogni altro controllo; non conta per il rate limit | [C+E] parziale; esclusione dal rate limit [C] | (1), (4) |
| `SKILL.md` r.187, `api-reference.md` §Methods | senza token 401 anche su route inesistenti e metodi sbagliati (formulazione neutra: «answered 401») | [E] | (2) |
| `api-reference.md` r.460 | preflight `Max-Age: 600` (600 s) | [E+C] | (3) |
| `SKILL.md` r.193, `api-reference.md` tabella, `README.md` r.111 e r.125 | finestra di 1 s con 120 richieste, `/health` e `OPTIONS` esclusi, prima dell'auth, 429; non provato sotto carico | [C]; 429 non provato | (4), (9) |
| `SKILL.md` r.196, `api-reference.md` tabella, `README.md` r.110 | 503 oltre 64 in volo, 8 stream chat, 4 embed; non provato sotto carico | [C]; 503 non provato | (4), (9) |
| `api-reference.md` tabella | body `chat` 40 MiB, `pages/write` circa 12 MiB, generico 1 MiB; limiti del codice, non provati | [C] (da raw api-mcp, non riletti) | (5) |
| `SKILL.md` r.193 e r.196, `api-reference.md` §`Retry-After`, `README.md` r.110-111, `examples.md` r.283 | `Retry-After` non affermato; assente nei percorsi noti (riserva SSE di successo); attese 1 s e 2 s = prudenza dell'agente | [C] | (6) |
| `SKILL.md` r.186, `api-reference.md` tabella | `pages/write` troppo grande → 400 | [C] | (7) |
| `SKILL.md` r.186 e r.191, `api-reference.md` tabella | corpo generico oltre 1 MiB: nessun codice; tolti «oversized body» da 400, «request body > 1 MB» da 413 e «Exceed → 400» | non noto | (8) |
| `SKILL.md` r.206, `README.md` r.125 | «120 req/sec» → «120 requests per 1 s window»; «1 MB» → «1 MiB» | [C] (formulazione) | (4), (5) |

**Ricerche testuali** (`grep -nE <pattern> SKILL.md api-reference.md examples.md README.md`, in `code_repos/llm_wiki_skill`, dopo le modifiche):
- `405` → 2 righe (`SKILL.md` r.190, `api-reference.md` §Methods), entrambe con la regola nuova; nessun «0.4.x only».
- `404` → 9 righe: le due regole nuove più usi invariati (progetto non registrato, file inesistente).
- `413` → 12 righe: invariati file e albero oltre il limite; `SKILL.md` r.191 non cita più il corpo.
- `429` e `503` → righe di tabella, `README.md`, `examples.md`: dove danno la regola, tutte con «not tested under load» o equivalente.
- `Retry-After` → 7 righe, nessuna lo afferma come esistente.
- `Max-Age|600` → 1 riga (`api-reference.md` r.460), con 600 secondi.
- `OPTIONS` → 7 righe, coerenti (204, escluso dal rate limit, mai 405).
- `\b120\b` → 5 righe di rate limit più `totalCount: 120` (esempio non correlato); nessun «req/sec» residuo.
- `1 MiB|1 MB` → 4 righe, nessun codice di stato per il corpo generico; `40 MiB` → 1 riga e `12 MiB` → 1 riga, solo nella tabella dei limiti; `sliding` → 0.
- Tracce: `grep -nEi "TSK|LWS|ADR|factory|wiki-keeper|Co-Authored|\[C\]|\[E\]|wiki/"` sulle righe aggiunte (`git diff -U0`) → 0 righe; sull'intero file restano solo percorsi d'esempio `wiki/concepts/...` e «Claude Code» (preesistenti, non sono tracce).

Messaggio di commit proposto: `docs: document HTTP methods, preflight, rate limit and request body limits` (nessun ID, nessuna attribution).

## Dependencies
- LWS-TSK-007 — serializzazione per sovrapposizione di file.

---
id: LWS-TSK-004
title: "Sicurezza della skill: CORS ad elenco, bind di rete e route che richiedono sempre il token"
us: LWS-US-003
sprint: 01
layer: docs
consumer: agent
priority: P1
estimate: S
status: done
depends_on: [LWS-TSK-003]
blocked_by: []
code_path: ["code_repos/llm_wiki_skill/SKILL.md", "code_repos/llm_wiki_skill/api-reference.md", "code_repos/llm_wiki_skill/examples.md", "code_repos/llm_wiki_skill/README.md"]
target: llm_wiki_skill
started_at: 2026-11-23
closed_at: 2026-11-23
decision_refs: []
---

# LWS-TSK-004 — Sicurezza, rete e autenticazione

## Context
La skill descrive CORS `*` e «solo localhost»; la v0.6.13 usa CORS ad elenco e può ascoltare su LAN. Copre D4, D5, D6, incoerenze n. 9 e n. 10, V23 e V24 (parte CORS). `depends_on` su `LWS-TSK-003` per sovrapposizione di file (serializzazione), non per dipendenza logica. [^src: management/kanban/LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-003-sicurezza-rete-e-autenticazione/LWS-US-003.md §Acceptance Criteria] [^src: wiki/concepts/llm-wiki-sicurezza.md §Aggiornamenti (v2026-11-21)]

## Technical Specs
- **Layer docs, consumer agent, target `llm_wiki_skill`.** Branch condiviso.
- **Evidenza dei fatti (da riportare in Chiusura con l'hunk del diff):**

| Fatto | Livello |
|---|---|
| D4: `Access-Control-Allow-Origin` riflette l'origine solo se in elenco (`chrome-extension://`, `moz-extension://`, localhost, `127.0.0.1`, `[::1]`, `tauri://localhost`, `tauri.localhost`), altrimenti l'header manca; nessun `*` | [C+E] |
| D4: una richiesta da origine non in elenco è comunque servita | [E] |
| D5: precedenza `LLM_WIKI_BIND_HOST`, poi `allowLanAccess` (bind `0.0.0.0`), poi `127.0.0.1`; nessuna distinzione di schema fra loopback e LAN; valutato al bind | [C]; bind LAN non provato in esecuzione |
| D6: `chat`, `chat/cancel`, `pages/embed`, `pages/write` richiedono sempre il token; restano aperte con `allowUnauthenticated`: `projects`, `files`, `files/content`, `reviews`, `search`, `graph`, `sources/rescan` | [C]; non in esecuzione |
| n. 9, n. 10: `?token=`, `X-LLM-Wiki-Token`, `Authorization: Bearer` accettati; `allowUnauthenticated` esiste | [C]; token in tre forme anche [E] |

- Fonti: [^src: wiki/syntheses/llm-wiki-skill-vs-app-v0-6-13.md §Dettaglio] [^src: wiki/concepts/llm-wiki-api-osservazioni-esecuzione-v0-6-13.md §Osservazioni del 2026-11-13 (app 0.6.13, progetto reale, non replicate)] [^src: wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md §Esito per voce]
- Non portare `Allow-Private-Network` né altri dettagli solo osservati; non toccare la rotazione del token.
- Il rischio cross-origin non è più «affidato alla segretezza del token» nel senso di CORS `*`.

## Vincoli comuni (TSK docs di contenuto)
- Prima di scrivere: `git -C code_repos/llm_wiki_skill branch --show-current` = branch condiviso; altrimenti STOP.
- Si scrive solo nei file di `code_path`; nessun file nuovo, codice o script.
- Testi della skill senza ID kanban, riferimenti a ADR, wiki o factory, attribution AI o `Co-Authored-By`; [C]/[E] solo nel TSK.
- Se la wiki non documenta un comportamento v0.6.13, la skill non lo afferma; fatti solo [E]: correzione neutra.
- Commit: non lo esegue il dev-agent; propone un messaggio generico senza ID; la sessione principale lo esegue con `tools/vcs/sm_commit.py` dopo OK esplicito. `done` solo dopo il commit; Chiusura con i tre campi (dichiarati, committati, working tree).

## Implementation Steps
1. Verifica del branch.
2. Riscrivere CORS e threat model in tutti i file che li citano.
3. Riscrivere ascolto di rete e precedenza; aggiungere l'avvertenza sul token in chiaro con ascolto su LAN.
4. Distinguere le route sempre autenticate da quelle aperte con `allowUnauthenticated`; citare `allowUnauthenticated` in `api-reference.md`.
5. Uniformare l'avvertenza su `?token=` in ogni file che lo cita.
6. Ricerche testuali (CORS `*`, «localhost», «solo localhost») con comando ed esito.

## Definition of Done
- [x] AC1..AC6 verificati con ricerca testuale e hunk del diff.
- [x] AC7: ogni affermazione cambiata ha la riga di evidenza in Chiusura; nessuna senza evidenza.
- [x] Nessuna traccia (ID, factory, attribution AI) nei file toccati.

## Chiusura

Branch `docs/align-v0-6-13`, HEAD `778b149` (verificato a comando prima di scrivere). Fine riga CRLF dei file della skill preservata.

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-003 AC1 | Verificato, da spuntare dopo il commit | `api-reference.md` riga 433: «reflected in `Access-Control-Allow-Origin` only for these origins: `chrome-extension://` and `moz-extension://` (any extension id), `localhost`, `127.0.0.1` and `[::1]` (with or without a port), `tauri://localhost` and `http(s)://tauri.localhost`. For any other origin the header is absent.» Riga 434: «A request from an origin that is not in the list is still served.» Nessun testo dice che il server rifiuti la richiesta. `README.md` riga 131 ripete l'elenco in forma breve. |
| LWS-US-003 AC2 | Verificato, da spuntare dopo il commit | Ricerca 1 sotto: nessun `Access-Control-Allow-Origin: *`; resta solo «never sends a wildcard origin» (`api-reference.md` 433). Ricerca 5: nessuna occorrenza di «secrecy» o «relies on». L'elemento del threat model (`README.md` 131) non cita più CORS `*` e non dice che il rischio sia affidato al token: dice che il server serve le richieste e che CORS non è controllo di accesso. |
| LWS-US-003 AC3 | Verificato, da spuntare dopo il commit | `api-reference.md` «### Listen address» (445-455): default `127.0.0.1`; ordine 1 `LLM_WIKI_BIND_HOST`, 2 `0.0.0.0` se `allowLanAccess`, 3 `127.0.0.1`; «evaluated each time the server binds ... not on each request»; «no difference of auth scheme between loopback and LAN ... on the LAN the token travels in clear text»; «listening on the LAN was not tested by running the app». `SKILL.md` 75 e `README.md` 118-120 dicono lo stesso; `SKILL.md` aggiunge «If `allowLanAccess` is `true`, warn the user». «localhost-only» (`SKILL.md` 75) e «binds to `127.0.0.1` only» (`README.md` 53) sostituiti da «by default» e «a default, not a guarantee». Ricerca 2: nessun «solo localhost» residuo. |
| LWS-US-003 AC4 | Verificato, da spuntare dopo il commit | `api-reference.md` 15-22: tabella «With `allowUnauthenticated: true`»: aperte `projects`, `files`, `files/content`, `reviews`, `search`, `graph`, `sources/rescan`; sempre con token `chat`, `chat/{sessionId}/cancel`, `pages/embed`, `pages/write`. Stessa distinzione in `SKILL.md` 81 e `README.md` 61. Nessuna sezione o descrizione delle route chat e pages è stata reintrodotta: solo i nomi nell'elenco. |
| LWS-US-003 AC5 | Verificato, da spuntare dopo il commit | `api-reference.md` cita `allowUnauthenticated` alle righe 15, 17 e 53 (oltre all'esempio `/health` e a `authRequired`). `?token=` compare in due file: `SKILL.md` 90 e `api-reference.md` 12, entrambi «last resort, leaks into logs» (ricerca 4). `README.md` e `examples.md` non citano `?token=`: nessuna avvertenza da uniformare. |
| LWS-US-003 AC6 | Verificato, da spuntare dopo il commit | Ricerca 5: nessun `Vary`, nessun `Private-Network`. Tolto il blocco «Observed: reflected for ... also on 401 responses; not for `https://example.com`, `null` or `http://localhost.evil.com`» (solo [E], oltre la tabella). Rotazione del token: `git diff -U0 \| grep -i -c rotat` → 0; le occorrenze di «rotat» nei file sono esempi di RoPE, non toccati. |
| LWS-US-003 AC7 | Verificato, da spuntare dopo il commit | Tabella delle affermazioni cambiate sotto: ogni riga ha livello e riga di evidenza; nessuna affermazione cambiata senza evidenza. Due righe oltre la tabella del TSK sono dichiarate (token in chiaro con HTTP semplice; elenco degli header ammessi, testo già in bozza). |

### Affermazioni cambiate e riga di evidenza (AC7)
| File e riga | Affermazione | Livello | Riga di evidenza |
|---|---|---|---|
| `api-reference.md` 433 | `Allow-Origin` riflesso solo per l'elenco (estensioni chrome e moz con qualunque id, `localhost`, `127.0.0.1`, `[::1]` con o senza porta, `tauri://localhost`, `http(s)://tauri.localhost`); altrimenti l'header manca; nessun `*` | [C+E] | [^src: wiki/syntheses/llm-wiki-skill-vs-app-v0-6-13.md §Dettaglio, riga D4]; [^src: wiki/concepts/llm-wiki-sicurezza.md §Aggiornamenti (v2026-11-22, verifica sul codice), voce «CORS.»]; [^src: wiki/concepts/llm-wiki-sicurezza.md §Aggiornamenti (v2026-11-21), voce «CORS (non è autenticazione)»]; [^src: wiki/concepts/llm-wiki-api-osservazioni-esecuzione-v0-6-13.md §Osservazioni del 2026-11-13, riga 12] |
| `api-reference.md` 433 | Metodi `GET, POST, PATCH, DELETE, OPTIONS`; header ammessi `Authorization`, `X-LLM-Wiki-Token`, `Content-Type` (testo già in bozza, solo spostato) | [C] | [^src: wiki/concepts/llm-wiki-sicurezza.md §Aggiornamenti (v2026-11-21), voce «CORS (non è autenticazione)»] |
| `api-reference.md` 434; `README.md` 131 | Una richiesta da origine non in elenco è comunque servita; CORS non è controllo di accesso | [E] | [^src: wiki/concepts/llm-wiki-sicurezza.md §Aggiornamenti (v2026-11-22, evidenze alm-wiki), voce «Richiesta da origine non ammessa»]; formulazione neutra, senza le tre origini provate |
| `api-reference.md` 445-453; `SKILL.md` 75; `README.md` 118-119 | Precedenza `LLM_WIKI_BIND_HOST`, `allowLanAccess` (`0.0.0.0`), `127.0.0.1`; valutato a ogni bind, non a ogni richiesta; `/health` mostra l'impostazione, non l'indirizzo | [C]; bind LAN non provato in esecuzione | [^src: wiki/concepts/llm-wiki-sicurezza.md §Aggiornamenti (v2026-11-22, verifica sul codice), voce «Bind, momento della valutazione»]; [^src: wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md §Esito per voce, riga 23]; [^src: wiki/concepts/llm-wiki-sicurezza.md §Aggiornamenti (v2026-11-22, evidenze alm-wiki), voce «Non provato in esecuzione»] |
| `api-reference.md` 455; `SKILL.md` 75; `README.md` 120 | Nessuna distinzione di schema fra loopback e LAN | [C] | [^src: wiki/concepts/llm-wiki-sicurezza.md §Aggiornamenti (v2026-11-21), voce «Non c'è distinzione tra loopback e LAN»] |
| `api-reference.md` 455; `SKILL.md` 75; `README.md` 120 | Con ascolto su LAN il token viaggia in chiaro (HTTP semplice). **Non è nella tabella del TSK**; la richiede l'AC3 | [C] | [^src: wiki/concepts/llm-wiki-sicurezza.md §Aggiornamenti (v2026-11-21, dossier r8), voce «Esposizione di rete»: «token in chiaro sulla rete locale (nessun TLS lato server nei file letti)»] |
| `api-reference.md` 15-22; `SKILL.md` 81; `README.md` 61 | Con `allowUnauthenticated` restano aperte `projects`, `files`, `files/content`, `reviews`, `search`, `graph`, `sources/rescan`; `chat`, `chat/{sessionId}/cancel`, `pages/embed`, `pages/write` richiedono sempre il token | [C]; non in esecuzione | [^src: wiki/concepts/llm-wiki-sicurezza.md §Aggiornamenti (v2026-11-21), voce «Token sempre richiesto per chat, chat/cancel, pages/embed e pages/write»]; [^src: wiki/syntheses/llm-wiki-skill-vs-app-v0-6-13.md §Dettaglio, riga D6]; la forma `chat/{sessionId}/cancel` è quella di D3 della stessa sintesi |
| `api-reference.md` 3, 53; `README.md` 53, 61 | Il default `127.0.0.1` non è una garanzia; `allowUnauthenticated` non è più «local-process»; «Any process or browser page on this machine» → «Any client that can reach the API port» (per default un processo locale) | [C] | Conseguenza dei fatti di bind e di D6 sopra; nessun fatto nuovo |
| `api-reference.md` 12; `SKILL.md` 90 | `?token=` accettato; avvertenza uniforme «last resort, leaks into logs» | [C]; token in tre forme anche [E] | [^src: wiki/entities/llm-wiki-skill.md §Incoerenze interne della skill, riga 9]; [^src: wiki/concepts/llm-wiki-sicurezza.md §Aggiornamenti (v2026-11-21), voce «Il token viene da ...»]; [^src: wiki/concepts/llm-wiki-api-osservazioni-esecuzione-v0-6-13.md §Osservazioni del 2026-11-13, riga 12] |
| `api-reference.md` 15, 17, 53; `SKILL.md` 81 | `allowUnauthenticated` esiste ed è citato nella sezione di autenticazione | [C] | [^src: wiki/entities/llm-wiki-skill.md §Incoerenze interne della skill, riga 10] |
| `README.md` 53 | Il server ascolta su `127.0.0.1:19828` per default (non «solo»), finché l'app è aperta | [C] | Stessa riga di bind sopra |

### Hunk del diff (brevi)
- `api-reference.md`: `-All non-/health endpoints require auth via one of:` → `+Except /health, every endpoint requires the token, sent in one of these forms:`; `+?token=<urlencoded-token>          # last resort, leaks into logs`; tabella `allowUnauthenticated` (+7 righe).
- `api-reference.md`: tolti `-CORS (upstream v1 docs, **0.4.x only**): ...: *.` e `-Observed: reflected for ...`; aggiunte le due righe CORS; `-allowLanAccess reflects the setting; ...` → `+### Listen address` (elenco 1-3 e due paragrafi).
- `SKILL.md`: `-The API is **localhost-only**. The token is one of:` → `+The API listens on 127.0.0.1 by default. That is a default, not a guarantee: ...`; voce 3: `-Even then chat, chat/.../cancel, pages/write and pages/embed still require the token.` → `+In this mode projects, files, ... stay open. chat, chat/{sessionId}/cancel, pages/embed and pages/write always require the token.`
- `README.md`: riga 53 (`binds ... only` → `By default ... listens`), riga 61 (route aperte e route sempre con token), riga 118 spezzata in tre punti (default, valutazione al bind, token in chiaro su LAN), riga 129 (CORS) riscritta.

### Ricerche testuali (cartella `code_repos/llm_wiki_skill`, `*.md`)
1. `grep -n -i -E "Allow-Origin: ?\*|CORS (was|is) .?\*|CORS `\*`|wildcard|\bCORS\b.*\*" *.md` → una riga: `api-reference.md` 433, «never sends a wildcard origin». Nessun `Allow-Origin: *` né «CORS `*`».
2. `grep -n -i -E "localhost.only|only localhost|solo localhost|127\.0\.0\.1.only|only on 127|only to 127|127\.0\.0\.1 only|localhost-only" *.md` → nessuna riga.
3. `grep -n "127\.0\.0\.1" *.md` → occorrenze valutate. Lasciate (indirizzo di default in esempi e messaggi): `SKILL.md` 3, 40, 63; `README.md` 71, 86, 92, 96, 105. Riscritte o già corrette: `README.md` 53, 118, 131; `api-reference.md` 3 (default con rinvio a «Listen address»), 433 (elenco CORS), 447-451 (ordine di scelta); `SKILL.md` 75. Nessuna occorrenza residua come garanzia di ascolto.
4. `grep -n -F "?token" *.md` → `SKILL.md` 90 e `api-reference.md` 12, stessa avvertenza.
5. `grep -n -i -E "secrecy|segretezza|relies on|Private-Network|Vary" *.md` → nessuna riga.
6. `grep -n "allowUnauthenticated" *.md` e `grep -n -E "LLM_WIKI_BIND_HOST|allowLanAccess" *.md` → occorrenze nelle righe sopra; nessuna in `examples.md`.
7. Tracce: `grep -n -i -E "LWS-|TSK-|US-[0-9]|EP-[0-9]|ADR|factory|wiki-factory|Co-Authored|Claude|Anthropic|generated with|\[C\]|\[E\]|\[\^src|raw/20" *.md` → solo «Claude Code» e `~/.claude/skills` in `README.md` 3, 17, 19, 23 (testo dell'originale `main`: nome del prodotto e percorso, non attribution).

### Residui per altri TSK
- `api-reference.md` 433: «Preflight cached 10 min via `Access-Control-Max-Age: 600`» e «`OPTIONS` → 204 without auth» restano come nella bozza (prima etichettati «0.4.x only» e in parte «Observed»). Per v0.6.13 `Max-Age: 600` è solo [E]: da riformulare o togliere nel TSK che copre `OPTIONS` e i metodi (D11).
- `api-reference.md` «Limits & defenses» e le righe sui metodi (405 e 404): non toccate qui.
- Clip server (stessi bind e CORS; da loopback senza token): non portato, fuori dalla tabella del TSK. `README.md` 118 lo cita solo nel nome dell'opzione.
- Tabella endpoint di `SKILL.md`: le righe `chat` e `reviews` restano quelle di LWS-TSK-003; nessuna descrizione delle route chat e pages aggiunta.

### Diff di chiusura (a comando)
- `git -C code_repos/llm_wiki_skill branch --show-current` → `docs/align-v0-6-13`; `log --oneline -1` → `778b149`.
- Dichiarati: `SKILL.md`, `api-reference.md`, `README.md` (repo della skill; `examples.md` letto, nessuna modifica necessaria) e questo file TSK.
- Committati: `753cbbd` nel repo della skill (README.md, SKILL.md, api-reference.md), dopo OK esplicito dell'utente in chat (2026-11-23); `sm_commit.py --dry-run` → messaggio invariato; `git log -1` senza trailer né attribution. Nella factory nessun commit.
- Dopo il commit (a comando): repo della skill `git status --short` e `git diff --name-only HEAD` vuoti; puntatore del submodule nella factory a `753cbbd`, non committato.
- Decisioni dell'utente (2026-11-23): `Access-Control-Max-Age: 600` e «`OPTIONS` → 204» restano a LWS-TSK-008; la forma `chat/{sessionId}/cancel` resta (AC4 «chat/cancel», stesso significato).
- Nel working tree della skill: `git status --short` → ` M README.md`, ` M SKILL.md`, ` M api-reference.md`. `git diff --name-only HEAD` → gli stessi tre file. `git diff --stat HEAD` → 3 file, 34 inserzioni, 18 cancellazioni (README 10, SKILL 6, api-reference 36 righe toccate).
- Nel working tree della factory: `git status --short` → ` M code_repos/llm_wiki_skill`, ` M` LWS-TSK-001, LWS-TSK-002, LWS-TSK-003, `sprint.md`, `wiki/log.md`, `?? DOSSIER-llm-wiki-qualita-ingest.md` (preesistenti); in più questo TSK.
- Messaggio di commit proposto: `docs: describe list-based CORS, configurable listen address and per-route token rules`

> Stato al momento del report del dev-agent: `in-progress`, DoD non spuntata. Superato: `done` dopo il commit `753cbbd` con OK dell'utente (2026-11-23), vedi frontmatter e «Committati».

## Dependencies
- LWS-TSK-003 — serializzazione per sovrapposizione di file.

---
id: LWS-TSK-009
title: "Route che scrivono, chat e postura sulle scritture nella skill"
us: LWS-US-007
sprint: 01
layer: docs
consumer: agent
priority: P1
estimate: M
status: done
depends_on: [LWS-TSK-008]
blocked_by: []
code_path: ["code_repos/llm_wiki_skill/SKILL.md", "code_repos/llm_wiki_skill/api-reference.md", "code_repos/llm_wiki_skill/examples.md", "code_repos/llm_wiki_skill/README.md"]
target: llm_wiki_skill
started_at: 2026-11-23
closed_at: 2026-11-23
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
- [x] AC1..AC5 di LWS-US-007 verificati con ricerca testuale e hunk.
- [x] AC10: riga di evidenza per ogni affermazione cambiata.
- [x] Nessuna traccia nei file toccati.

## Chiusura
<!-- AC6-AC9 sono di LWS-TSK-010 -->

Lavoro eseguito il 2026-11-23 sul branch `docs/align-v0-6-13` (HEAD di partenza `887df67`, verificato con `git -C code_repos/llm_wiki_skill branch --show-current`).

**Diff di chiusura (a comando)**

| Campo | Contenuto |
|---|---|
| Dichiarati | `SKILL.md`, `api-reference.md`, `examples.md`, `README.md` (tutti in `code_path`) |
| Committati | `d3d3fd4` nel repo della skill (4 file, 86+/10-), dopo OK esplicito dell'utente in chat (2026-11-23); messaggio: solo la prima riga della proposta del dev-agent, nel formato dei commit precedenti; `sm_commit.py --dry-run` → invariato; `git log -1` senza trailer né attribution. Dopo il commit `git status --short` della skill vuoto. Fini riga: il repo salva LF, la copia di lavoro era CRLF per `core.autocrlf=true`; il dev-agent ha scritto LF, il blob committato non cambia. Factory: commit `7c001a8` con questo TSK, la sola entry di `wiki/log.md` (stage parziale) e il puntatore; `sprint.md` escluso (lavoro non committato di un'altra sessione). Punti dubbi 1-3 decisi dall'utente come proposti (501 e «0.4.x» tolti, dichiarazione di versione a LWS-TSK-014) |
| Working tree (prima del commit `d3d3fd4`) | `git -C code_repos/llm_wiki_skill status --short`: `M README.md`, `M SKILL.md`, `M api-reference.md`, `M examples.md`; `git diff --stat`: 4 file, 86 inserzioni, 10 cancellazioni. Nella factory: questo TSK e il puntatore del submodule; `TSK-029` (EP-002) e `DOSSIER-llm-wiki-qualita-ingest.md` sono di altre sessioni, non toccati |

**Ricerche testuali** (`grep -n`, da `code_repos/llm_wiki_skill`, su `SKILL.md api-reference.md examples.md README.md`; le alternative di ogni comando sono unite con `|`, qui separate da virgole)

| Alternative cercate | Esito |
|---|---|
| `-i -E`: `501`, `only write`, `only mutat`, `no write endpoint`, `write endpoint`, `v1 had`, `stub`, `not implemented`, `read-only.*non-current`, `only endpoint` | 0 risultati (exit 1) |
| `-E`: `Don't .?POST`, `Don't call`, `Do not call`, `non-current` | 2 risultati, entrambi `examples.md` (r. 273 e 279): testo nuovo («not read-only», «Don't call a route that changes state unless the user explicitly asked»); nessuna formula rimossa |
| `-E`: `\b499\b`, `auto-save`, `autosave`, `~1 s`, `about 1 s`, `keepalive`, `keep-alive` | 0 risultati |
| `-E`: `\b409\b` | 4 risultati, tutti su `pages/write` (`SKILL.md` r. 179 e 206; `api-reference.md` r. 477 e 481) |
| `-E`: `LWS-`, `TSK-`, `US-[0-9]`, `EP-[0-9]`, `ADR`, `Co-Authored`, `[C]`, `[E]`, `[^src`, `wiki-factory`, `suppress`, `kanban` | 0 risultati (exit 1) |
| `-E`: `review\.json`, `allowOverwrite`, `SSE`, `sessionId` | solo nelle voci nuove di route (scritture review, `pages/write`, `chat`, cancel) |

**Esito per AC**

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-007 AC1 | soddisfatto | Ricerca 1: 0 risultati. Tolti: `SKILL.md` riga `chat` «0.4.x: 501 ... Don't call.» e riga 501 della tabella errori; `api-reference.md` «0.4.x: returns 501 ... Don't invoke»; `examples.md` anti-pattern «Don't `POST /chat` — on 0.4.x it returns 501» e la frase r. 273; `README.md` «v1 had no write endpoints». L'invito a non inventare endpoint non era presente in nessuno dei quattro file |
| LWS-US-007 AC2 | soddisfatto | `SKILL.md` §«Routes that change state»: «On app 0.6.13 these routes change state: `sources/rescan`, the review routes `PATCH`, `DELETE` and `resolve`, `pages/write`, `pages/embed` and `chat`» e «Review changes, `sources/rescan` and `pages/embed` act on the project named in `{id}`, not only on `current`». Stessa sezione in `api-reference.md`; `README.md` r. 38 e 126 |
| LWS-US-007 AC3 | soddisfatto | `SKILL.md` tabella «Endpoint contract»: righe `reviews` (GET, PATCH, DELETE, `resolve`), `pages/write`, `pages/embed`, `chat`, `chat/{sessionId}/cancel`. `api-reference.md`: sezioni `chat`, cancel, `pages/write`, `pages/embed`, scritture review. Corpi non noti dichiarati: «The request body is not documented here. Do not guess it.» (`chat`, `PATCH`, `resolve`, `pages/embed`); verbo del cancel non documentato |
| LWS-US-007 AC4 | soddisfatto | `api-reference.md` §`chat`: «The reply is JSON or an SSE stream. A stream carries these events: `meta`, `agent`, `done`, `cancelled`, `error`», «the token is always required», rotta di cancel. Nessun corpo, nessun keepalive (ricerca 3), nessun esito della cancellazione («What a cancellation leaves behind is not documented here.») |
| LWS-US-007 AC5 | soddisfatto | `SKILL.md` Etiquette: «The routes that change state ..., `pages/embed` and `chat` run only after the user explicitly asked for that action»; sezione «Routes that change state»: «Never call them to explore ...»; anti-pattern nuovo in `examples.md`. Nessuna frase sulla sovrascrittura delle review da auto-save: tolta quella su «rewrites the whole `review.json` about 1 s after each change» (ricerca 3: 0 risultati) |
| LWS-US-007 AC10 | soddisfatto | Tabella sotto: ogni affermazione cambiata ha la riga di evidenza |

**Affermazioni cambiate (AC10)**

| # | File | Affermazione nella skill | Livello | Evidenza |
|---|---|---|---|---|
| 1 | `SKILL.md` tabella, `api-reference.md` sezione review | `PATCH`, `DELETE`, `resolve` riscrivono `.llm-wiki/review.json` del progetto in `{id}` | [C]; non in esecuzione | Tabella Evidenza, D1 riga 1 |
| 2 | `SKILL.md` tabella, `api-reference.md` §`pages/write` | `pages/write` scrive una pagina markdown; corpo `{path, content, allowOverwrite}`; 409 se la pagina esiste senza `allowOverwrite`; 400 per path, markdown, dimensione; 500 altrimenti | [C] contratto; interno di `handle_write_page` non letto | Tabella Evidenza, D1 riga 2 |
| 3 | `SKILL.md`, `api-reference.md` §`chat` | `chat` risponde in JSON o SSE; eventi `meta`, `agent`, `done`, `cancelled`, `error`; token sempre richiesto; rotta di cancel; `agent.chat: true` osservato | [C] contratto + [E] solo il flag | Tabella Evidenza, D2 |
| 4 | `SKILL.md`, `api-reference.md` §`chat` | `chat` scrive nelle sessioni agente del progetto | [C]; non in esecuzione | `wiki/concepts/llm-wiki-api-locale.md` r. 62 («`POST projects/{id}/chat` (`agent-sessions` via `append_turn`)»). Non è nella tabella del TSK; è nella AC2 della US («`chat` (sessioni agente)») |
| 5 | `SKILL.md` tabella | `reviews` in lettura: riga con rinvio ai campi già in `api-reference.md` | [E+C] | Tabella Evidenza, D3 riga 1 |
| 6 | `SKILL.md`, `api-reference.md` §`pages/embed` | 400 se l'embedding non è configurato; 503 con 4 embed in volo; token sempre richiesto | [C] contratto; non in esecuzione | Tabella Evidenza, D3 riga 2 |
| 7 | `SKILL.md`, `api-reference.md` | `chat/{sessionId}/cancel`: route esistente, token sempre richiesto, `{sessionId}` segmento URL; verbo non dichiarato | [C] contratto | Tabella Evidenza, D3 riga 2; `llm-wiki-api-locale.md` r. 62 per il segmento |
| 8 | `SKILL.md`, `api-reference.md`, `examples.md`, `README.md` | Review, rescan ed embed agiscono su qualunque progetto indicato; una chiamata su un id non corrente non è di sola lettura; per `pages/write` e `chat` non è noto | [C]; `handle_write_page` e `handle_chat` non letti | Tabella Evidenza, D21 e V19 |
| 9 | `SKILL.md`, `api-reference.md` | `pages/embed` cambia lo stato; che cosa scriva non è documentato | [C]; corpo non letto | `llm-wiki-api-locale.md` r. 62 (`pages/embed` e `sources/rescan` fra le rotte che scrivono, «corpi non letti»); affermazione minima, lacuna dichiarata |
| 10 | `SKILL.md` errori | Riga 409 solo per `pages/write` | [C] contratto | Tabella Evidenza, D1 riga 2 |
| 11 | `SKILL.md`, `api-reference.md`, `README.md` | Elenco delle route che cambiano stato al posto di «unica scrittura rescan» e «altre POST/PATCH/DELETE» | come righe 1-9 | Righe 1-9 |
| 12 | `SKILL.md`, `api-reference.md`, `examples.md`, `README.md` | Postura: scritture, `embed` e `chat` solo su richiesta esplicita; non chiamarle per esplorare né per controllare che la route esista; non ritentare un 409 con `allowOverwrite` senza richiesta | decisione D4 dell'utente; cautela dell'agente, non un fatto sull'app | US-007 §Business Rules, «Decisione sulle scritture» |
| 13 | `SKILL.md`, `api-reference.md`, `examples.md` | Tolta la riga/sezione `chat` «0.4.x: 501 ... Don't call» e la riga 501 degli errori | rimozione, nessun fatto nuovo | AC1; D2 della sintesi; `agent.chat: true` osservato |
| 14 | `api-reference.md` | Tolta la frase «The desktop UI keeps reviews in memory and rewrites the whole `review.json` about 1 s after each change» | rimozione: deduzione non provata | Regola «non si portano come fatti» della US |
| 15 | `api-reference.md` §`pages/write` | Valori dell'esempio dichiarati illustrativi: «the rules for `path` are not documented here» | nessun fatto; esempio | n.a. |
| 16 | `api-reference.md` §rescan | Una riga: il rescan agisce sul progetto in `{id}`, non solo su `current` | [C] | Tabella Evidenza, D21 e V19 (rescan) |

**Scelte da segnalare**
- Il qualificatore «0.4.x» per il 501 è stato tolto con la riga, non conservato: la sezione Version di `README.md` (non toccata) dichiara ancora `0.4.10+` e la wiki non conferma il 501 sulla 0.4.x. La dichiarazione di versione resta a LWS-TSK-014.
- La riga 501 della tabella errori di `SKILL.md` è tolta del tutto (diceva solo `/chat`).
- La ricetta di `examples.md` con una route nuova (AC9) non è di questo TSK: resta a LWS-TSK-010.
- Il rescan (descrizione, `changedTasks`, `kind`) non è toccato oltre la riga 16: resta a LWS-TSK-010.

## Dependencies
- LWS-TSK-008 — serializzazione per sovrapposizione di file.

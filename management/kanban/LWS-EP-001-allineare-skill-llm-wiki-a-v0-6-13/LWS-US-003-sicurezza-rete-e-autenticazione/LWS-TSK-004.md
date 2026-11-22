---
id: LWS-TSK-004
title: "Sicurezza della skill: CORS ad elenco, bind di rete e route che richiedono sempre il token"
us: LWS-US-003
sprint: 01
layer: docs
consumer: agent
priority: P1
estimate: S
status: todo
depends_on: [LWS-TSK-003]
blocked_by: []
code_path: ["code_repos/llm_wiki_skill/SKILL.md", "code_repos/llm_wiki_skill/api-reference.md", "code_repos/llm_wiki_skill/examples.md", "code_repos/llm_wiki_skill/README.md"]
target: llm_wiki_skill
started_at:
closed_at:
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
- [ ] AC1..AC6 verificati con ricerca testuale e hunk del diff.
- [ ] AC7: ogni affermazione cambiata ha la riga di evidenza in Chiusura; nessuna senza evidenza.
- [ ] Nessuna traccia (ID, factory, attribution AI) nei file toccati.

## Chiusura

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-003 AC1 | | |
| LWS-US-003 AC2 | | |
| LWS-US-003 AC3 | | |
| LWS-US-003 AC4 | | |
| LWS-US-003 AC5 | | |
| LWS-US-003 AC6 | | |
| LWS-US-003 AC7 | | |

## Dependencies
- LWS-TSK-003 — serializzazione per sovrapposizione di file.

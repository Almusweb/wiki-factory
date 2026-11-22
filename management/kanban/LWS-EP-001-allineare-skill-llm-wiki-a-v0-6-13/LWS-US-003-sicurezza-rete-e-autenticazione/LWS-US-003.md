---
id: LWS-US-003
title: Sicurezza, rete e autenticazione
role: Agente AI che usa la skill llm-wiki
priority: high
status: ready
wiki_page: wiki/concepts/llm-wiki-sicurezza.md
blocked_by: []
pending_clarification: []
depends_on: [LWS-US-002]
---

# LWS-US-003 — Sicurezza, rete e autenticazione

## Descrizione
Come agente AI che usa la skill `llm-wiki`, voglio che la skill descriva CORS, ascolto di rete e autenticazione come funzionano nella v0.6.13, affinché non mi fidi di garanzie che non esistono («solo localhost», CORS `*`) e sappia quali route richiedono sempre il token.

## Business Rules
- Regole trasversali dell'epica LWS-EP-001: valgono tutte.
- Copre D4, D5, D6; incoerenze n. 9 e n. 10; V23 e V24 (parte CORS).
- Il rischio cross-origin non è più «affidato alla segretezza del token» nel senso di CORS `*`: l'header manca per le origini non in elenco.

### Evidenza dei fatti
| Fatto | Livello |
|---|---|
| D4: `Access-Control-Allow-Origin` riflette l'origine solo se in elenco (`chrome-extension://`, `moz-extension://`, localhost, `127.0.0.1`, `[::1]`, `tauri://localhost`, `tauri.localhost`), altrimenti l'header manca; nessun `*` | [C+E] |
| D4: una richiesta da origine non in elenco è comunque servita | [E] |
| D5: precedenza `LLM_WIKI_BIND_HOST`, poi `allowLanAccess` (bind `0.0.0.0`), poi `127.0.0.1`; nessuna distinzione di schema fra loopback e LAN; valutato al bind del server | [C]; bind LAN non provato in esecuzione |
| D6: `chat`, `chat/cancel`, `pages/embed` e `pages/write` richiedono sempre il token; restano aperte con `allowUnauthenticated` `projects`, `files`, `files/content`, `reviews`, `search`, `graph`, `sources/rescan` | [C] (`api_server.rs` letto per intero); non in esecuzione |
| n. 9, n. 10: `?token=`, `X-LLM-Wiki-Token` e `Authorization: Bearer` accettati; `allowUnauthenticated` esiste | [C]; token in tre forme anche [E] |

[^src: wiki/syntheses/llm-wiki-skill-vs-app-v0-6-13.md §Dettaglio]
[^src: wiki/concepts/llm-wiki-sicurezza.md §Aggiornamenti (v2026-11-21)]
[^src: wiki/concepts/llm-wiki-api-osservazioni-esecuzione-v0-6-13.md §Osservazioni del 2026-11-13 (app 0.6.13, progetto reale, non replicate)]
[^src: wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md §Esito per voce]

## UI Reference
[^src: wiki/concepts/llm-wiki-skill-api-v1-dichiarata.md §Autenticazione]
[^src: wiki/concepts/llm-wiki-skill-api-v1-dichiarata.md §Modello di sicurezza dichiarato]
[^src: wiki/entities/llm-wiki-skill.md §Incoerenze interne della skill (materiale per la PR)]

## Acceptance Criteria
- [ ] La skill dice che il CORS di v0.6.13 consente l'origine solo per l'elenco (`chrome-extension://`, `moz-extension://`, localhost, `127.0.0.1`, `[::1]`, `tauri://localhost`, `tauri.localhost`) e che per le altre origini l'header manca; non dice che la richiesta sia rifiutata dal server.
- [ ] In nessuno dei quattro file compare `Access-Control-Allow-Origin: *` né la tesi che il rischio cross-origin sia affidato solo alla segretezza del token; l'elenco dei casi fuori dal threat model non cita più CORS `*` come motivo. Verifica: ricerca testuale nei quattro file.
- [ ] La skill dice che il default di ascolto è `127.0.0.1`, che `allowLanAccess` porta il bind a `0.0.0.0` e che `LLM_WIKI_BIND_HOST` ha la precedenza; dice che la configurazione è applicata al bind del server, non a ogni richiesta; avverte che non c'è distinzione di schema fra loopback e LAN, quindi con ascolto su LAN il token viaggia in chiaro. Non resta «solo localhost» né «ascolto solo su 127.0.0.1» come garanzia.
- [ ] La skill distingue le route che con `allowUnauthenticated` richiedono comunque il token (`chat`, `chat/cancel`, `pages/embed`, `pages/write`) da quelle che restano aperte (`projects`, `files`, `files/content`, `reviews`, `search`, `graph`, `sources/rescan`).
- [ ] `api-reference.md` cita `allowUnauthenticated` (n. 10); `?token=` porta la stessa avvertenza («ultima scelta, finisce nei log») in ogni file che lo cita (n. 9).
- [ ] La skill non porta `Allow-Private-Network` né altri dettagli solo osservati; la rotazione del token non è toccata.
- [ ] Ogni affermazione cambiata ha nel TSK la riga di evidenza corrispondente; nessuna è priva di evidenza.

## Fonti
[^src: wiki/syntheses/llm-wiki-skill-vs-app-v0-6-13.md §Dettaglio]
[^src: wiki/concepts/llm-wiki-sicurezza.md §Aggiornamenti (v2026-11-21)]
[^src: wiki/concepts/llm-wiki-api-locale.md §Aggiornamenti (v2026-11-21)]

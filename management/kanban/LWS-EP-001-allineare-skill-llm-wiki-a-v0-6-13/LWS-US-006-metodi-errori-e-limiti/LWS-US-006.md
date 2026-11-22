---
id: LWS-US-006
title: Metodi, errori e limiti
role: Agente AI che usa la skill llm-wiki
priority: medium
status: ready
wiki_page: wiki/concepts/llm-wiki-api-locale.md
blocked_by: []
pending_clarification: []
depends_on: [LWS-US-002]
---

# LWS-US-006 — Metodi, errori e limiti

## Descrizione
Come agente AI che usa la skill `llm-wiki`, voglio che la skill descriva metodi ammessi, preflight, codici d'errore e limiti della v0.6.13, affinché non interpreti 404, 405, 413 e 429 con regole vecchie.

## Business Rules
- Regole trasversali dell'epica LWS-EP-001: valgono tutte.
- Copre D11, D12; incoerenze n. 1 (parte nota), n. 7, n. 8; V14 e V15; A4 (corpo oltre 1 MB che dà 400 e 413).
- Il codice del body generico troppo grande **non è noto** (gap `llm-wiki-skill-punti-da-verificare`): la skill non ne indica uno.

### Evidenza dei fatti
| Fatto | Livello |
|---|---|
| D11: 405 solo fuori da GET, POST, PATCH, DELETE; un verbo o una rotta sbagliata fra gli ammessi dà 404; `OPTIONS` dà 204 con CORS prima di ogni altro controllo | [C+E] parziale |
| D11: 401 anche su route inesistenti e su metodi sbagliati, senza token | [E] |
| n. 8: preflight `Access-Control-Max-Age: 600` | [E+C] |
| D12: finestra di 1 s con 120 richieste; `/health` e `OPTIONS` esclusi; rate limit applicato prima dell'auth; 503 oltre 64 in volo, 8 stream chat, 4 embed | [C] |
| D12: body di `chat` 40 MiB, `pages/write` circa 12 MiB, body generico 1 MiB | [C] (da raw api-mcp, non riletti nella verifica) |
| n. 7: `Retry-After` assente nei percorsi letti (riserva sugli header della risposta SSE di successo) | [C] |
| n. 1: `pages/write` troppo grande: 400 | [C] |
| n. 1: codice del body generico troppo grande | non noto |
| 429 e 503 sotto carico | non provati in esecuzione |

[^src: wiki/syntheses/llm-wiki-skill-vs-app-v0-6-13.md §Aggiornamenti (v2026-11-22, verifica sul codice)]
[^src: wiki/concepts/llm-wiki-api-locale.md §Aggiornamenti (v2026-11-21)]
[^src: wiki/concepts/llm-wiki-api-osservazioni-esecuzione-v0-6-13.md §Osservazioni del 2026-11-13 (app 0.6.13, progetto reale, non replicate)]
[^src: wiki/gaps.md §2026-11-22 11:24 — llm-wiki-skill-punti-da-verificare]

## UI Reference
[^src: wiki/concepts/llm-wiki-skill-api-v1-dichiarata.md §Codici d'errore e limiti]
[^src: wiki/entities/llm-wiki-skill.md §Incoerenze interne della skill (materiale per la PR)]

## Acceptance Criteria
- [ ] La skill dice che i metodi ammessi sono GET, POST, PATCH, DELETE; che il 405 vale per gli altri metodi; che su una route nota un verbo sbagliato dà 404; che `OPTIONS` dà 204 con CORS prima di ogni altro controllo. La contraddizione 405/preflight è chiusa (n. 8).
- [ ] Il preflight è dichiarato di 600 secondi.
- [ ] Il rate limit è dichiarato prima dell'auth e con `/health` e `OPTIONS` esclusi; restano 120 richieste per finestra di 1 s con 429; la tabella dei limiti aggiunge body di `chat` 40 MiB, `pages/write` circa 12 MiB, 8 stream chat in volo e 4 embed in volo, oltre al limite generale di 1 MiB sul body.
- [ ] La skill non afferma l'esistenza di `Retry-After`: dice che i 429 e 503 non lo portano nei percorsi noti (n. 7); i tempi di attesa consigliati (almeno 1 s su 429, almeno 2 s su 503) restano come prudenza dell'agente, non come dato del server.
- [ ] Il corpo troppo grande di `pages/write` è dichiarato 400; per il corpo generico oltre il limite la skill non indica un codice specifico e non resta la doppia indicazione 400 e 413 (n. 1).
- [ ] Ogni affermazione cambiata ha nel TSK la riga di evidenza corrispondente; nessuna è priva di evidenza.

## Fonti
[^src: wiki/syntheses/llm-wiki-skill-vs-app-v0-6-13.md §Dettaglio]
[^src: wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md §Esito per voce]

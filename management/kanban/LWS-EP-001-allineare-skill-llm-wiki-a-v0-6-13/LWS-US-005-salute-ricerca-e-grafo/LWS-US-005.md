---
id: LWS-US-005
title: Salute, ricerca e grafo
role: Agente AI che usa la skill llm-wiki
priority: high
status: ready
wiki_page: wiki/concepts/llm-wiki-ricerca-e-grafo-api.md
blocked_by: []
pending_clarification: []
depends_on: [LWS-US-002]
---

# LWS-US-005 — Salute, ricerca e grafo

## Descrizione
Come agente AI che usa la skill `llm-wiki`, voglio che la skill descriva `/health`, `search` e `graph` della v0.6.13, affinché legga correttamente `mode`, `graphHits`, la paginazione del grafo e la copertura reale della ricerca.

## Business Rules
- Regole trasversali dell'epica LWS-EP-001: valgono tutte.
- Copre D7, D9, D10, D14, D15, D16, D19, D20; incoerenze n. 3, n. 4, n. 15; V1-V9 e V13.
- I fatti solo osservati (D14 snippet) si riportano in forma neutra: si corregge soltanto la frase smentita (N1).

### Evidenza dei fatti
| Fatto | Livello |
|---|---|
| D7: `/health` con `mcpEnabled`, `allowLanAccess`, `agent{chat, streaming, streamProtocol}`; risponde anche su `/health` senza prefisso (e con `POST`); `currentProject` non è in `/health` | [E+C] parziale |
| D9: `graphHits` in `search` | [E+C] |
| D10: `offset`, `limit`, `totalCount`, `hasMore`, `edgeScope` (`page` o `filtered`; non valido: 400) | [E+C] parziale |
| D10: `limit` assente 200, ridotto a [1, 1000] (5000 diventa 1000), 400 per 0, negativo e non numerico | [C+E] |
| D10: cache di 5 s del grafo | [C] solo da raw api-mcp; non provata in esecuzione |
| D14: snippet di circa 110 caratteri, frontmatter compreso (la skill dice circa 160) | [E] soltanto: correzione neutra |
| D15: `hybrid` anche con zero risultati vettoriali; RRF solo con risultati vettoriali; keyword additivo (200, 50, 20 fino a 10 occorrenze, 5,0 e 1,0) | [C+E] |
| D15: scala RRF e score con embedding attivi | non noti |
| D16: il tipo è la prima riga `type:` di tutto il file, minuscolo, default `other`; i nodi `query` sono tolti dal grafo | [C+E] |
| D19: archi anche dai valori di `related:`; id nodo stem o percorso relativo in caso di collisione; link ambiguo scartato; dedup senza direzione | [C] |
| D20: la ricerca copre solo `wiki/**/*.md`, fino a 10.000 file, poi si ferma con un messaggio su stderr e la risposta non lo segnala | [C] |
| V1, V2: quota dei vicini del grafo 0,30 senza vettori, 0,15 a finestra piena | [C] |
| V3: `vectorScore` composito, non un coseno grezzo | [C] |
| V8: `q` non restituisce i vicini | [C] |
| `images` sempre `[]`, ordine non strettamente decrescente, `content` assente senza `includeContent` | [E] soltanto: non si portano |

[^src: wiki/syntheses/llm-wiki-skill-vs-app-v0-6-13.md §Aggiornamenti (v2026-11-22, verifica sul codice)]
[^src: wiki/concepts/llm-wiki-ricerca-e-grafo-api.md §Dettaglio]
[^src: wiki/concepts/llm-wiki-api-osservazioni-esecuzione-v0-6-13.md §Osservazioni del 2026-11-13 (app 0.6.13, progetto reale, non replicate)]
[^src: wiki/concepts/llm-wiki-api-locale.md §Aggiornamenti (v2026-11-21)]

## UI Reference
[^src: wiki/concepts/llm-wiki-skill-api-v1-dichiarata.md §`GET /health`]
[^src: wiki/concepts/llm-wiki-skill-api-v1-dichiarata.md §`POST /projects/{id}/search`]
[^src: wiki/concepts/llm-wiki-skill-api-v1-dichiarata.md §`GET /projects/{id}/graph`]

## Acceptance Criteria
- [ ] `/health` documenta anche `mcpEnabled`, `allowLanAccess` e `agent{chat, streaming, streamProtocol}` e dice che risponde anche su `/health` senza prefisso; l'elenco dei campi è lo stesso in tutti i file, `version` incluso, e l'esempio del README ha `version` (n. 3).
- [ ] `search` documenta `graphHits` accanto a `tokenHits` e `vectorHits` e dice di guardare `vectorHits` e `graphHits`, non solo `mode`; `queryEmbedding` compare nel corpo anche in `SKILL.md` (n. 4).
- [ ] La skill dice che `hybrid` può avere `vectorHits` 0, che l'RRF si applica solo con risultati vettoriali, che senza vettori il punteggio keyword è additivo, che `vectorScore` non è un coseno grezzo e che gli score non sono confrontabili fra modalità; non resta alcun intervallo numerico RRF dichiarato come universale.
- [ ] La skill documenta la copertura della ricerca: solo `wiki/**/*.md`, fino a 10.000 file, senza segnalazione di troncamento nella risposta.
- [ ] La lunghezza dello snippet non è più dichiarata «circa 160 caratteri»; la dicitura è neutra e non introduce una nuova garanzia (D14).
- [ ] `graph` documenta `offset`, `edgeScope` (`page` o `filtered`), i campi di risposta `offset`, `limit`, `totalCount` e `hasMore`, la cache di 5 s e il clamp di `limit` a [1, 1000] con 400 per 0, negativo e non numerico; `q` filtra solo i nodi; la frase «nessuna paginazione» riguarda solo `files`.
- [ ] La skill dice che gli archi vengono anche da `related:`, che i link ambigui sono scartati e che le pagine `type: query` non sono nodi; `nodeType` è descritto come insieme aperto derivato da `type:`, con esempi non esaustivi (n. 15).
- [ ] La skill non dichiara completo l'elenco dei campi di un risultato di `search` e non porta `images` sempre vuoto né l'ordine non strettamente decrescente.
- [ ] Ogni affermazione cambiata ha nel TSK la riga di evidenza corrispondente; nessuna è priva di evidenza.

## Fonti
[^src: wiki/syntheses/llm-wiki-skill-vs-app-v0-6-13.md §Dettaglio]
[^src: wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md §Esito per voce]

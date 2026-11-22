---
id: LWS-TSK-007
title: "Grafo nella skill: paginazione, edgeScope, cache, archi da related e tipi di nodo"
us: LWS-US-005
sprint: 01
layer: docs
consumer: agent
priority: P1
estimate: S
status: todo
depends_on: [LWS-TSK-006]
blocked_by: []
code_path: ["code_repos/llm_wiki_skill/SKILL.md", "code_repos/llm_wiki_skill/api-reference.md", "code_repos/llm_wiki_skill/examples.md", "code_repos/llm_wiki_skill/README.md"]
target: llm_wiki_skill
started_at:
closed_at:
decision_refs: []
---

# LWS-TSK-007 — `graph`

## Context
Seconda metà di LWS-US-005 (AC6, AC7, AC9): il grafo. Copre D10, D16, D19; n. 15; V4-V7 dove decisi. `depends_on` su `LWS-TSK-006` per sovrapposizione di file. [^src: management/kanban/LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-005-salute-ricerca-e-grafo/LWS-US-005.md §Acceptance Criteria]

## Technical Specs
- **Layer docs, consumer agent, target `llm_wiki_skill`.** Branch condiviso.
- **Evidenza dei fatti:**

| Fatto | Livello |
|---|---|
| D10: `offset`, `limit`, `totalCount`, `hasMore`, `edgeScope` (`page` o `filtered`; non valido: 400) | [E+C] parziale |
| D10: `limit` assente 200, ridotto a [1, 1000] (5000 diventa 1000), 400 per 0, negativo e non numerico | [C+E] |
| D10: cache di 5 s del grafo | [C] solo da raw api-mcp; non provata in esecuzione |
| D16: il tipo è la prima riga `type:` di tutto il file, minuscolo, default `other`; nodi `query` tolti dal grafo | [C+E] |
| D19: archi anche dai valori di `related:`; id nodo stem o percorso relativo in caso di collisione; link ambiguo scartato; dedup senza direzione | [C] |
| V8: `q` non restituisce i vicini (filtra solo i nodi) | [C] |

- Fonti: [^src: wiki/concepts/llm-wiki-ricerca-e-grafo-api.md §Dettaglio] [^src: wiki/syntheses/llm-wiki-skill-vs-app-v0-6-13.md §Aggiornamenti (v2026-11-22, verifica sul codice)] [^src: wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md §Esito per voce]
- La cache di 5 s resta marcata [C] da raw api-mcp, non provata: se l'esito di `LWS-TSK-011` arriva prima, si incorpora solo per decisione esplicita dell'utente.

## Vincoli comuni (TSK docs di contenuto)
- Prima di scrivere: `git -C code_repos/llm_wiki_skill branch --show-current` = branch condiviso; altrimenti STOP.
- Si scrive solo nei file di `code_path`; nessun file nuovo, codice o script.
- Testi della skill senza ID kanban, riferimenti a ADR, wiki o factory, attribution AI o `Co-Authored-By`; [C]/[E] solo nel TSK.
- Se la wiki non documenta un comportamento v0.6.13, la skill non lo afferma.
- Commit: non lo esegue il dev-agent; propone un messaggio generico senza ID; la sessione principale lo esegue con `tools/vcs/sm_commit.py` dopo OK esplicito. `done` solo dopo il commit; Chiusura con i tre campi (dichiarati, committati, working tree).

## Implementation Steps
1. Verifica del branch.
2. `graph`: `offset`, `edgeScope`, campi di risposta `offset`, `limit`, `totalCount`, `hasMore`, cache di 5 s, clamp di `limit` a [1, 1000] con 400 per 0, negativo e non numerico; `q` filtra solo i nodi.
3. «Nessuna paginazione» limitata a `files`.
4. Archi anche da `related:`, link ambigui scartati, `type: query` non nodi, `nodeType` insieme aperto con esempi non esaustivi.
5. Controlli testuali con comando ed esito.

## Definition of Done
- [ ] AC6 e AC7 di LWS-US-005 verificati con ricerca testuale e hunk.
- [ ] AC9: riga di evidenza per ogni affermazione cambiata.
- [ ] Nessuna traccia nei file toccati.

## Chiusura
<!-- AC1-AC5 e AC8 sono di LWS-TSK-006 -->

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-005 AC6 | | |
| LWS-US-005 AC7 | | |
| LWS-US-005 AC9 | | |

## Dependencies
- LWS-TSK-006 — serializzazione per sovrapposizione di file.

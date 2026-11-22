---
id: LWS-TSK-006
title: "Salute e ricerca nella skill: campi di /health, graphHits, copertura e snippet"
us: LWS-US-005
sprint: 01
layer: docs
consumer: agent
priority: P1
estimate: M
status: todo
depends_on: [LWS-TSK-005]
blocked_by: []
code_path: ["code_repos/llm_wiki_skill/SKILL.md", "code_repos/llm_wiki_skill/api-reference.md", "code_repos/llm_wiki_skill/examples.md", "code_repos/llm_wiki_skill/README.md"]
target: llm_wiki_skill
started_at:
closed_at:
decision_refs: []
---

# LWS-TSK-006 — `/health` e `search`

## Context
Prima metà di LWS-US-005 (AC1-AC5, AC8, AC9): `/health` e `search`. Il `graph` è `LWS-TSK-007`. Copre D7, D9, D14, D15, D20; n. 3, n. 4; V1-V3, V8, V13. `depends_on` su `LWS-TSK-005` per sovrapposizione di file. [^src: management/kanban/LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-005-salute-ricerca-e-grafo/LWS-US-005.md §Acceptance Criteria]

## Technical Specs
- **Layer docs, consumer agent, target `llm_wiki_skill`.** Branch condiviso.
- **Evidenza dei fatti:**

| Fatto | Livello |
|---|---|
| D7: `/health` con `mcpEnabled`, `allowLanAccess`, `agent{chat, streaming, streamProtocol}`; risponde anche su `/health` senza prefisso (e con `POST`); `currentProject` non è in `/health` | [E+C] parziale |
| D9: `graphHits` in `search` | [E+C] |
| D14: snippet di circa 110 caratteri, frontmatter compreso (la skill dice circa 160) | [E] soltanto: correzione neutra |
| D15: `hybrid` anche con zero risultati vettoriali; RRF solo con risultati vettoriali; keyword additivo (200, 50, 20 fino a 10 occorrenze, 5,0 e 1,0) | [C+E] |
| D15: scala RRF e score con embedding attivi | non noti |
| D20: la ricerca copre solo `wiki/**/*.md`, fino a 10.000 file, poi si ferma con messaggio su stderr e la risposta non lo segnala | [C] |
| V1, V2: quota dei vicini del grafo 0,30 senza vettori, 0,15 a finestra piena | [C] |
| V3: `vectorScore` composito, non un coseno grezzo | [C] |
| V8: `q` non restituisce i vicini | [C] |
| `images` sempre `[]`, ordine non strettamente decrescente, `content` assente senza `includeContent` | [E] soltanto: non si portano |

- Fonti: [^src: wiki/syntheses/llm-wiki-skill-vs-app-v0-6-13.md §Aggiornamenti (v2026-11-22, verifica sul codice)] [^src: wiki/concepts/llm-wiki-ricerca-e-grafo-api.md §Dettaglio] [^src: wiki/concepts/llm-wiki-api-osservazioni-esecuzione-v0-6-13.md §Osservazioni del 2026-11-13 (app 0.6.13, progetto reale, non replicate)] [^src: wiki/concepts/llm-wiki-api-locale.md §Aggiornamenti (v2026-11-21)]
- L'esempio di `/health` del README (con `version`) è completato da `LWS-TSK-014`; qui l'elenco dei campi deve già essere lo stesso in tutti i file.

## Vincoli comuni (TSK docs di contenuto)
- Prima di scrivere: `git -C code_repos/llm_wiki_skill branch --show-current` = branch condiviso; altrimenti STOP.
- Si scrive solo nei file di `code_path`; nessun file nuovo, codice o script.
- Testi della skill senza ID kanban, riferimenti a ADR, wiki o factory, attribution AI o `Co-Authored-By`; [C]/[E] solo nel TSK.
- Se la wiki non documenta un comportamento v0.6.13, la skill non lo afferma; fatti solo [E]: correzione neutra.
- Commit: non lo esegue il dev-agent; propone un messaggio generico senza ID; la sessione principale lo esegue con `tools/vcs/sm_commit.py` dopo OK esplicito. `done` solo dopo il commit; Chiusura con i tre campi (dichiarati, committati, working tree).

## Implementation Steps
1. Verifica del branch.
2. `/health`: campi `mcpEnabled`, `allowLanAccess`, `agent{...}`, `version`, risposta anche senza prefisso; stesso elenco in tutti i file.
3. `search`: `graphHits`, `queryEmbedding` nel corpo anche in `SKILL.md`, istruzione a guardare `vectorHits` e `graphHits`.
4. Semantica degli score (hybrid, RRF, keyword additivo, `vectorScore`, non confrontabili fra modalità); togliere ogni intervallo RRF universale.
5. Copertura: `wiki/**/*.md`, 10.000 file, nessuna segnalazione nella risposta. Snippet in forma neutra. Non dichiarare completo l'elenco dei campi di un risultato.
6. Controlli testuali con comando ed esito.

## Definition of Done
- [ ] AC1, AC2, AC3, AC4, AC5, AC8 di LWS-US-005 verificati.
- [ ] AC9: riga di evidenza per ogni affermazione cambiata.
- [ ] Nessuna traccia nei file toccati.

## Chiusura
<!-- AC6 e AC7 sono di LWS-TSK-007 -->

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-005 AC1 | | |
| LWS-US-005 AC2 | | |
| LWS-US-005 AC3 | | |
| LWS-US-005 AC4 | | |
| LWS-US-005 AC5 | | |
| LWS-US-005 AC6 | n/a | coperto da LWS-TSK-007 |
| LWS-US-005 AC7 | n/a | coperto da LWS-TSK-007 |
| LWS-US-005 AC8 | | |
| LWS-US-005 AC9 | | |

## Dependencies
- LWS-TSK-005 — serializzazione per sovrapposizione di file.

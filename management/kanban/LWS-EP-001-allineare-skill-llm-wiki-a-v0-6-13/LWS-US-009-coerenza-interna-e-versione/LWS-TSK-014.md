---
id: LWS-TSK-014
title: "Dichiarazione di versione, README e regola di drift nella skill"
us: LWS-US-009
sprint: 02
layer: docs
consumer: agent
priority: P1
estimate: S
status: todo
depends_on: [LWS-TSK-010]
blocked_by: []
code_path: ["code_repos/llm_wiki_skill/README.md", "code_repos/llm_wiki_skill/SKILL.md", "code_repos/llm_wiki_skill/api-reference.md"]
target: llm_wiki_skill
started_at:
closed_at:
decision_refs: []
---

# LWS-TSK-014 — Versione, README e drift

## Context
La skill deve dichiarare solo «verificata su v0.6.13» con la base dichiarata, avere README coerente e una regola di drift su qualunque versione diversa da quella verificata. Copre n. 11, n. 16 (valori di `status`), n. 17 e A4 (incongruenze ereditate). Decisioni dell'utente: niente «0.4.10+», nessuna storia delle versioni, base in termini generici. Dipende da `LWS-TSK-010` (ultimo dei TSK di contenuto, stessi file; AC3 richiede i campi coerenti con `LWS-TSK-006`). [^src: management/kanban/LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-009-coerenza-interna-e-versione/LWS-US-009.md §Acceptance Criteria] [^src: wiki/entities/llm-wiki-skill.md §Versione dichiarata]

## Technical Specs
- **Layer docs, consumer agent, target `llm_wiki_skill`.** Branch condiviso.
- **Base di verifica (formulazione generica):** lettura del codice sorgente dell'app alla v0.6.13 e alcune risposte verificate su un'app in esecuzione. **Non** si citano progetto, date né identificativi della prova.
- **Regola di drift:** confrontare la versione riportata da `/health` con quella verificata; per qualunque versione diversa, controllare `api-reference.md`. Non dipende più da un «major version bump».
- **README:** quattro file (non «three markdown files»); comando di update con il nome della skill `llm-wiki`, non `llm_wiki_skill`; esempio di `/health` con `version` e campi coerenti con LWS-US-005; «four forms» di `{id}` coerente con le tre forme del server più il nome risolto lato client.
- **Non si toccano:** licenza, rotazione del token, valori di `status` di `/health` (restano i quattro noti [C]).
- **Evidenza:** intra-skill per n. 11; [C] per i quattro valori di `status`; la base di verifica è la dichiarazione dell'epica. [^src: wiki/entities/llm-wiki-skill.md §Incoerenze interne della skill (materiale per la PR)] [^src: wiki/concepts/llm-wiki-skill-api-v1-dichiarata.md §Versione dichiarata]

## Vincoli comuni (TSK docs di contenuto)
- Prima di scrivere: `git -C code_repos/llm_wiki_skill branch --show-current` = branch condiviso; altrimenti STOP.
- Si scrive solo nei file di `code_path`; nessun file nuovo, codice o script.
- Testi della skill senza ID kanban, riferimenti a ADR, wiki o factory, attribution AI o `Co-Authored-By`; [C]/[E] solo nel TSK.
- Se la wiki non documenta un comportamento v0.6.13, la skill non lo afferma.
- Commit: non lo esegue il dev-agent; propone un messaggio generico senza ID; la sessione principale lo esegue con `tools/vcs/sm_commit.py` dopo OK esplicito. `done` solo dopo il commit; Chiusura con i tre campi (dichiarati, committati, working tree).

## Implementation Steps
1. Verifica del branch.
2. README: numero di file, nome della skill nel comando di update, esempio di `/health`.
3. Dichiarazione di versione e base di verifica in tutti i file che la citano; togliere «0.4.10+» e ogni «dalla versione X».
4. Riscrivere la regola di drift.
5. Allineare «four forms» di `{id}`.
6. Ricerche testuali (`0.4.10`, «major version», «dalla versione»/«since version», «three markdown files», `llm_wiki_skill`) con comando ed esito.

## Definition of Done
- [ ] AC1, AC2, AC3, AC4, AC6 di LWS-US-009 verificati con ricerca testuale e hunk.
- [ ] AC7: riga di evidenza per ogni affermazione cambiata.
- [ ] Nessuna traccia nei file toccati; progetto, date e identificativi della prova assenti.

## Chiusura
<!-- AC5 è di LWS-TSK-015 -->

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-009 AC1 | | |
| LWS-US-009 AC2 | | |
| LWS-US-009 AC3 | | |
| LWS-US-009 AC4 | | |
| LWS-US-009 AC5 | n/a | coperto da LWS-TSK-015 |
| LWS-US-009 AC6 | | |
| LWS-US-009 AC7 | | |

## Dependencies
- LWS-TSK-010 — ultimo TSK di contenuto; serializzazione per sovrapposizione di file.

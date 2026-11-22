---
id: LWS-TSK-017
title: "Push del branch condiviso sulla fork (gate umano)"
us: LWS-US-010
sprint: 02
layer: infra
consumer: human
priority: P1
estimate: XS
status: todo
depends_on: [LWS-TSK-016]
blocked_by: []
code_path: ["code_repos/llm_wiki_skill"]
target: llm_wiki_skill
started_at:
closed_at:
decision_refs: []
---

# LWS-TSK-017 — Push del branch condiviso

## Context
Il branch condiviso (nome neutro fissato da `LWS-TSK-001`, senza ID kanban) è l'unico branch dell'epica: si pusha tal quale sulla fork, senza refspec particolari. Operazione su remote: gate umano esplicito. [^src: management/kanban/LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-010-preparare-la-pr-upstream/LWS-US-010.md §Business Rules]

## Technical Specs
- **Consumer:** `human` (`routing.infra: human`); può eseguirlo la sessione principale con override esplicito dell'utente in chat, scritto nella Chiusura.
- **Gate 1 (prima del push), decisione dell'utente:** tenere un commit per TSK oppure ridurli (squash) prima del push. Se squash, la riscrittura della storia locale è un'operazione da confermare e da riportare con comando ed esito; dopo lo squash si ripetono i controlli di non-traccia di `LWS-TSK-016` sui messaggi dei nuovi commit.
- **Gate 2:** OK esplicito dell'utente al push.
- Il commit `HEAD` pushato è quello su cui `LWS-TSK-016` ha chiuso l'audit; se `HEAD` è cambiato dopo, si ripete l'audit.
- Nessun ID kanban nel nome del branch né nei messaggi.

## Implementation Steps
1. `git -C code_repos/llm_wiki_skill branch --show-current` e `git -C code_repos/llm_wiki_skill status --short` (vuoto).
2. `git -C code_repos/llm_wiki_skill log --oneline main..HEAD` e riportarlo all'utente; registrare la scelta commit-per-TSK o squash (gate 1).
3. Se squash: eseguirlo, poi ripetere i controlli di non-traccia sui messaggi.
4. Chiedere OK esplicito (gate 2); poi `git -C code_repos/llm_wiki_skill push -u origin <branch>` (verificare che `origin` sia la fork `Almusweb/llm_wiki_skill` con `git remote -v`).
5. Riportare comando ed esito, e `git -C code_repos/llm_wiki_skill rev-parse --short HEAD origin/<branch>` (uguali).

## Definition of Done
- [ ] Decisione dell'utente su commit per TSK o squash riportata.
- [ ] OK esplicito al push riportato.
- [ ] Push eseguito sulla fork con comando ed esito; `origin` verificato.
- [ ] Nessun ID kanban nel nome del branch.

## Chiusura

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-010 AC6 | | |

## Dependencies
- LWS-TSK-016 — audit locale chiuso.

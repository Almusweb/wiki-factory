---
id: LWS-TSK-017
title: "Push del branch condiviso sulla fork (gate umano)"
us: LWS-US-010
sprint: 02
layer: infra
consumer: human
priority: P1
estimate: XS
status: done
depends_on: [LWS-TSK-016]
blocked_by: []
code_path: ["code_repos/llm_wiki_skill"]
target: llm_wiki_skill
started_at: 2026-11-23
closed_at: 2026-11-23
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
- [x] Decisione dell'utente su commit per TSK o squash riportata.
- [x] OK esplicito al push riportato.
- [x] Push eseguito sulla fork con comando ed esito; `origin` verificato.
- [x] Nessun ID kanban nel nome del branch.

## Chiusura

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-010 AC6 | verificato (parte push) | Push eseguito dall'utente in persona, quindi con il suo consenso esplicito; dichiarato in chat il 2026-11-23 («ho già fatto io LWS-TSK-017»). Evidenza a comando, rilevata dalla sessione principale: `git -C code_repos/llm_wiki_skill reflog show origin/docs/align-v0-6-13` → `c73a69c` «update by push» 2026-11-23 16:32 +0100, poi `f6a99c7` «update by push» 2026-11-23 17:10 +0100; `git ls-remote --heads origin docs/align-v0-6-13` → `f6a99c7`, uguale a `git rev-parse HEAD`; upstream configurato `origin/docs/align-v0-6-13` (push con `-u`). Il comando letterale non è noto alla factory: il reflog registra solo «update by push». La parte PR di AC6 è di LWS-TSK-018. |

Eseguito dall'utente fuori dalla sessione principale; Chiusura compilata dalla sessione principale con le verifiche a comando.

- **Commit per TSK o squash (gate 1):** commit per TSK. `git log --oneline main..origin/docs/align-v0-6-13` → 12 commit, gli stessi del branch locale; nessuno squash.
- **`origin`:** `git remote get-url origin` → `https://github.com/Almusweb/llm_wiki_skill.git` (la fork).
- **Nome del branch:** `docs/align-v0-6-13`, senza ID kanban.
- **Messaggi dei commit pubblicati:** già verificati in LWS-TSK-016 con `ai_policy.find_factory_ids` e `is_ai_attribution` sui 12 messaggi → 0 hit.
- **Nota:** il primo push (`c73a69c`) è avvenuto prima dell'audit di LWS-TSK-016; per circa 40 minuti il branch pubblico conteneva i commit fino a LWS-TSK-010, senza le rimozioni dell'audit. I messaggi di quei commit non avevano tracce.
- **Diff di chiusura (factory):** dichiarati = questo TSK, `wiki/log.md`, `sprint.md`; nel repo della skill nessun file toccato da questo TSK.

## Dependencies
- LWS-TSK-016 — audit locale chiuso.

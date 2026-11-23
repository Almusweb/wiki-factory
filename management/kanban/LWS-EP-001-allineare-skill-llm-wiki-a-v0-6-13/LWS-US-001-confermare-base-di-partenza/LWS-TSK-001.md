---
id: LWS-TSK-001
title: "Confrontare main della fork con main di nashsu/llm_wiki_skill e creare il branch condiviso di lavoro"
us: LWS-US-001
sprint: 01
layer: infra
consumer: human
priority: P1
estimate: XS
status: done
depends_on: []
blocked_by: []
code_path: ["code_repos/llm_wiki_skill"]
target: llm_wiki_skill
started_at: 2026-11-23
closed_at: 2026-11-23
decision_refs: []
---

# LWS-TSK-001 — Confrontare `main` della fork con l'upstream e creare il branch condiviso

## Context
La PR upstream non deve poggiare su uno stato superato di `nashsu/llm_wiki_skill`. La fork è a `main` @ `642b438`; che coincida con l'upstream è un dato del chiamante dell'estrazione, non verificabile dal raw. Questo TSK lo verifica e crea l'unico branch di lavoro dell'epica (`branch_strategy: shared`). [^src: management/kanban/LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-001-confermare-base-di-partenza/LWS-US-001.md §Acceptance Criteria] [^src: wiki/entities/llm-wiki-skill.md §Contesto]

## Technical Specs
- **Consumer:** `human` (`routing.infra: human`), come TSK-011: operazione su remote. Può eseguirla la sessione principale con override esplicito dell'utente in chat, da scrivere nella Chiusura.
- **Gate umano:** il `git fetch` dell'upstream richiede OK esplicito dell'utente prima dell'esecuzione. La creazione del branch locale non è un'operazione remota e non ha gate.
- **Nessuna modifica ai file della skill.** Nessun commit, nessun push.
- **Branch condiviso:** nome neutro, senza ID kanban; proposta di default `docs/align-v0-6-13`, da confermare con l'utente a questo TSK. Tagliato da `main` (o dallo stato dell'upstream se avanti, vedi step 5). Tutti i TSK `LWS-TSK-002..016` lavorano su questo branch; `LWS-TSK-017` lo pusha.
- Il remote `upstream` (`https://github.com/nashsu/llm_wiki_skill.git`) va aggiunto se assente: è una scrittura di configurazione locale del repo cliente, da dichiarare nella Chiusura.

## Implementation Steps
1. `git -C code_repos/llm_wiki_skill status --short` (atteso vuoto) e `git -C code_repos/llm_wiki_skill log -1 --format=%h` (atteso `642b438`).
2. `git -C code_repos/llm_wiki_skill remote -v`; se manca `upstream`, aggiungerlo (dichiarare il comando).
3. Chiedere OK esplicito per il fetch; poi `git -C code_repos/llm_wiki_skill fetch upstream` e riportare l'esito.
4. `git -C code_repos/llm_wiki_skill rev-parse --short main upstream/main` e `git -C code_repos/llm_wiki_skill log --oneline main..upstream/main`: esito «identici» oppure elenco dei commit di scarto.
5. Se l'upstream è avanti: elencare le sovrapposizioni fra i commit di scarto e le correzioni previste dall'epica; il lavoro riparte dallo stato upstream (decisione dell'utente su come allineare `main` della fork prima del branch).
6. Confermare con l'utente il nome del branch e crearlo: `git -C code_repos/llm_wiki_skill switch -c <nome> <base>`.
7. Registrare il commit di partenza (`git rev-parse --short HEAD`) e verificare che nessun file sia modificato.

## Definition of Done
- [x] OK esplicito al fetch riportato nella Chiusura.
- [x] Esito del confronto `main` / `upstream/main` con comando ed esito.
- [x] Branch condiviso creato, nome neutro, commit di partenza registrato.
- [x] `git status --short` e `git diff --name-only` vuoti nel repo della skill.

## Chiusura
<!-- compilata a lavoro finito secondo dev-handoff §Semantica di `done` -->

Eseguito dalla sessione principale con override esplicito dell'utente in chat (2026-11-23): TSK `infra`/`consumer: human`, nessun dev-agent per il layer. Stesso turno: OK all'aggiunta del remote `upstream` e al fetch, nome del branch confermato (`docs/align-v0-6-13`).

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-001 AC1 | verificato | `git -C code_repos/llm_wiki_skill rev-parse --short main` → `642b438`; `rev-parse --short upstream/main` → `642b438`; `log --oneline main..upstream/main` e `upstream/main..main` → vuoti. Esito: **identici** (anche `origin/main` = `642b438`) |
| LWS-US-001 AC2 | non applicabile | condizione «upstream avanti» non verificata: `main..upstream/main` vuoto (AC1). Nessuna sovrapposizione da elencare |
| LWS-US-001 AC3 | verificato | `git -C code_repos/llm_wiki_skill switch -c docs/align-v0-6-13 main` → «Switched to a new branch»; `rev-parse --short HEAD` → `642b438` (commit di partenza) |
| LWS-US-001 AC4 | verificato | OK esplicito dell'utente in chat prima di `git fetch upstream` (esito: `* [new branch] main -> upstream/main`, exit 0) |
| LWS-US-001 AC5 | verificato | nel repo della skill `git status --short` → vuoto, `git diff --name-only` → vuoto |

Scritture di configurazione locale nel repo cliente: `git remote add upstream https://github.com/nashsu/llm_wiki_skill.git` (con OK), branch locale `docs/align-v0-6-13`. Nessun commit, nessun push. Il puntatore del submodule nella factory resta `642b438` (`git submodule status`).

Diff di chiusura (factory, `git status --short`): dichiarati = questo TSK, `wiki/log.md`, `management/kanban/sprint.md` (rigenerato); committati = nessuno; working tree = ` M wiki/log.md`, ` M management/kanban/sprint.md`, ` M` questo TSK, `?? DOSSIER-llm-wiki-qualita-ingest.md` (preesistente, non di questo TSK).

## Dependencies
- Nessuna. Blocca `LWS-TSK-002` (branch condiviso).

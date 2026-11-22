---
id: LWS-TSK-016
title: "Audit locale pre-PR: non-traccia, elementi non trasferibili, evidenza per ogni frase e bozza della descrizione"
us: LWS-US-010
sprint: 02
layer: docs
consumer: agent
priority: P1
estimate: M
status: todo
depends_on: [LWS-TSK-015]
blocked_by: []
code_path: ["code_repos/llm_wiki_skill/SKILL.md", "code_repos/llm_wiki_skill/api-reference.md", "code_repos/llm_wiki_skill/examples.md", "code_repos/llm_wiki_skill/README.md"]
target: llm_wiki_skill
started_at:
closed_at:
decision_refs: []
---

# LWS-TSK-016 — Audit locale pre-PR

## Context
Prima del push, il diff del branch condiviso rispetto a `main` deve essere pulito e verificabile: nessuna traccia della factory, nessun elemento non trasferibile della bozza, ogni frase cambiata con una riga di evidenza. È l'unico presidio di qualità di questa epica (CQRL esclude il layer `docs`). Solo operazioni locali: nessun fetch, push o PR. [^src: management/kanban/LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-010-preparare-la-pr-upstream/LWS-US-010.md §Acceptance Criteria] [^src: wiki/purpose.md §Pull request upstream]

## Technical Specs
- **Layer docs, consumer agent, target `llm_wiki_skill`.** Branch condiviso. Può modificare i quattro file solo per **togliere** frasi senza evidenza o tracce trovate.
- **Controlli:**
  1. Diff contro `main`: `git -C code_repos/llm_wiki_skill diff --name-status main..HEAD` → solo i quattro file esistenti, nessun file nuovo, nessun codice.
  2. Non-traccia nel diff e nei messaggi dei commit già fatti: pattern di `tools/vcs/ai_policy.py` (fonte unica, non ridefiniti) per attribution AI e ID kanban (`EP-`, `US-`, `TSK-`, `LWS-`), più ricerca di riferimenti a ADR, wiki, factory e `Co-Authored-By`.
  3. Elementi non trasferibili della bozza (stessa ricerca di `LWS-TSK-002`): `[obs]`/`[code]`, `FORK.md`, avvisi di fork, task interni, percorsi locali reali, dati di un progetto reale con data; nomi del progetto reale o dell'utente.
  4. Audit delle affermazioni: per ciascuna frase cambiata, riga di evidenza [C]/[E]/[C+E] raccolta dalle Chiusure di LWS-TSK-002..015; quelle senza riga sono tolte; elenco delle scartate **senza dati del progetto reale**.
  5. Nessuna fase B (estensioni personali) nel diff.
- **Bozza della descrizione PR:** generica, in un blocco della Chiusura, **senza** ID kanban né riferimenti alla factory; dichiara la base di verifica (lettura del codice sorgente dell'app alla v0.6.13 e alcune risposte verificate su un'app in esecuzione) e l'elenco dei punti non verificati lasciati invariati (EP §Cosa resta fuori dalla PR se non verificato e residui di LWS-US-008).
- Nessun commit, push o PR da questo TSK. Se l'audit toglie frasi, il commit di correzione lo esegue la sessione principale dopo OK esplicito con `tools/vcs/sm_commit.py`, messaggio generico senza ID.
- Fonti: [^src: wiki/entities/llm-wiki-skill-bozza-alm-wiki.md §Elementi non trasferibili a una PR upstream] [^src: wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md §Che cosa resta da verificare]

## Vincoli comuni
- Prima di operare: `git -C code_repos/llm_wiki_skill branch --show-current` = branch condiviso; altrimenti STOP.
- Nessun file nuovo, codice o script; testi senza ID, riferimenti a ADR/wiki/factory o attribution AI.

## Implementation Steps
1. Verifica del branch e del diff per nome file.
2. Esecuzione dei controlli 2 e 3 con comandi ed esiti.
3. Audit delle affermazioni: tabella `affermazione | livello | hunk | TSK di origine`.
4. Togliere le frasi senza evidenza; ripetere i controlli 2 e 3.
5. Scrivere la bozza della descrizione PR (senza ID né riferimenti alla factory) e verificarla con gli stessi pattern.

## Definition of Done
- [ ] AC1, AC2, AC3, AC4, AC5, AC7 di LWS-US-010 verificati con comando ed esito.
- [ ] Nessun commit, push o PR eseguito da questo TSK.

## Chiusura
<!-- AC6 è di LWS-TSK-017 e LWS-TSK-018 -->

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-010 AC1 | | |
| LWS-US-010 AC2 | | |
| LWS-US-010 AC3 | | |
| LWS-US-010 AC4 | | |
| LWS-US-010 AC5 | | |
| LWS-US-010 AC7 | | |

## Dependencies
- LWS-TSK-015 — tutti i TSK di contenuto chiusi e committati.

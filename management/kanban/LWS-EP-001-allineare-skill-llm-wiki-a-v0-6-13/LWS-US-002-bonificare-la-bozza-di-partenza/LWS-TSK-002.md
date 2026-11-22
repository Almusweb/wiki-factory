---
id: LWS-TSK-002
title: "Applicare la bozza sul branch condiviso e togliere gli elementi non trasferibili"
us: LWS-US-002
sprint: 01
layer: docs
consumer: agent
priority: P1
estimate: M
status: todo
depends_on: [LWS-TSK-001]
blocked_by: []
code_path: ["code_repos/llm_wiki_skill/SKILL.md", "code_repos/llm_wiki_skill/api-reference.md", "code_repos/llm_wiki_skill/examples.md", "code_repos/llm_wiki_skill/README.md"]
target: llm_wiki_skill
started_at:
closed_at:
decision_refs: []
---

# LWS-TSK-002 — Applicare la bozza e togliere gli elementi non trasferibili

## Context
Si riusano le 173 modifiche della bozza di riscrittura, privata di tutto ciò che non è trasferibile a una PR upstream. La bozza è un testo candidato, non una fonte di fatti sull'app. Questo TSK applica il testo e lo pulisce; il trattamento delle novità senza etichetta è `LWS-TSK-003`. [^src: management/kanban/LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-002-bonificare-la-bozza-di-partenza/LWS-US-002.md §Acceptance Criteria] [^src: wiki/entities/llm-wiki-skill-bozza-alm-wiki.md §Elementi non trasferibili a una PR upstream]

## Technical Specs
- **Layer docs, consumer agent (docs-dev), target `llm_wiki_skill`.** Branch condiviso creato da `LWS-TSK-001`.
- **Sorgente della bozza:** lettura **in sola lettura** dal progetto locale dell'utente fuori dalla factory. Il percorso lo passa la sessione principale nel prompt di lancio; **non compare in questo TSK né in alcun output** (TSK, log, report). Descrizione e inventario della bozza: `wiki/entities/llm-wiki-skill-bozza-alm-wiki.md`. Nulla è copiato nella factory: i quattro file si scrivono solo in `code_repos/llm_wiki_skill`.
- **Da togliere** (scheda wiki §Elementi non trasferibili): `FORK.md` e ogni riferimento; etichette `[obs]` e `[code]` e le loro legende; avviso di fork e istruzioni «non da eseguire su questa copia»; riferimenti a task interni; percorsi locali reali; dati di un progetto reale con data (score 122, 102 e 82; «Values seen on a real wiki»; fonti accodate il 2026-11-13; «seen once»; id e timestamp dell'esempio di review). Negli esempi, nessun nome del progetto reale né dell'utente.
- Le incongruenze ereditate (A4) non si risolvono qui: `LWS-TSK-008` e `LWS-TSK-014`.
- Nessun file nuovo oltre ai quattro.

## Vincoli comuni (TSK docs di contenuto)
- Prima di scrivere: `git -C code_repos/llm_wiki_skill branch --show-current` deve dare il branch condiviso; se diverso, STOP.
- Si scrive solo nei file di `code_path`; nessun file nuovo, nessun codice o script.
- Testi della skill senza ID kanban (`EP-`, `US-`, `TSK-`, `LWS-`), senza riferimenti a ADR, wiki o factory, senza attribution AI né `Co-Authored-By`. Le sigle [C]/[E] vivono solo nel TSK.
- Se la wiki non documenta un comportamento v0.6.13, la skill non lo afferma.
- Commit: non lo esegue il dev-agent. Propone un messaggio generico senza ID; lo esegue la sessione principale con `tools/vcs/sm_commit.py` dopo OK esplicito dell'utente. `done` solo dopo il commit; la Chiusura riporta i tre campi (dichiarati, committati, nel working tree).

## Implementation Steps
1. Verifica del branch (vedi Vincoli comuni).
2. Leggere la bozza in sola lettura dal percorso passato nel prompt; applicare il testo ai quattro file del repo della skill.
3. Rimuovere gli elementi non trasferibili elencati sopra; riscrivere gli esempi senza dati del progetto reale.
4. Ricerca testuale sui quattro file per ogni elemento (comando ed esito nella Chiusura).
5. `git status --short` e `git diff --name-only HEAD` nel repo della skill e nella factory (nessun file della bozza copiato nella factory).

## Definition of Done
- [ ] AC1: punto di partenza = bozza applicata; nessun file oltre ai quattro.
- [ ] AC2: ricerca testuale su tutti gli elementi non trasferibili → 0 occorrenze, comando ed esito riportati.
- [ ] AC3: nessun nome del progetto reale o dell'utente negli esempi.
- [ ] AC6: nessun file o dato della bozza nella factory; nel TSK solo il riferimento alla scheda wiki, mai il percorso assoluto.
- [ ] AC7: nessun ID kanban, riferimento a factory o attribution AI nei quattro file; commit solo dopo OK.

## Chiusura
<!-- US-002 AC4 e AC5 sono coperti da LWS-TSK-003: riportarli come n/a con rinvio -->

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-002 AC1 | | |
| LWS-US-002 AC2 | | |
| LWS-US-002 AC3 | | |
| LWS-US-002 AC4 | n/a | coperto da LWS-TSK-003 |
| LWS-US-002 AC5 | n/a | coperto da LWS-TSK-003 |
| LWS-US-002 AC6 | | |
| LWS-US-002 AC7 | | |

## Dependencies
- LWS-TSK-001 — branch condiviso e base confermata.

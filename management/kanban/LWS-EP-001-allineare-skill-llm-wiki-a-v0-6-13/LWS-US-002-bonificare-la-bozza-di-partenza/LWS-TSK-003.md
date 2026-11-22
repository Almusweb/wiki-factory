---
id: LWS-TSK-003
title: "Scartare le novità senza etichetta e senza evidenza e ripristinare il trigger originale"
us: LWS-US-002
sprint: 01
layer: docs
consumer: agent
priority: P1
estimate: S
status: todo
depends_on: [LWS-TSK-002]
blocked_by: []
code_path: ["code_repos/llm_wiki_skill/SKILL.md", "code_repos/llm_wiki_skill/api-reference.md", "code_repos/llm_wiki_skill/examples.md", "code_repos/llm_wiki_skill/README.md"]
target: llm_wiki_skill
started_at:
closed_at:
decision_refs: []
---

# LWS-TSK-003 — Scartare le novità senza evidenza e ripristinare il trigger

## Context
La regola della bozza «senza etichetta = upstream» è contraddetta da novità 0.6.13 senza etichetta (anomalia A1). Quelle senza una riga di evidenza non si portano. La `description` resta quella originale, con la sola clausola «read-only except for source rescan» corretta. [^src: management/kanban/LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-002-bonificare-la-bozza-di-partenza/LWS-US-002.md §Business Rules] [^src: wiki/entities/llm-wiki-skill-bozza-alm-wiki.md §Anomalie A1-A5 (della fonte)]

## Technical Specs
- **Layer docs, consumer agent, target `llm_wiki_skill`.** Stesso branch condiviso.
- **Novità senza etichetta da trattare (A1):** `description`, righe 0.6.13 di `SKILL.md`, 409 e 499, quasi tutta la sezione «Additions» di `api-reference.md`, CORS, `limit` 0 con 400.
- **Decise dal codice, restano:** solo `limit` 0 con 400, CORS e l'esclusione di `rtf`. Tutto il resto senza riga di evidenza esce; ciò che sarà coperto dalle storie di contenuto (003..007) rientra lì, con la sua riga.
- **Trigger (N4):** `description` = originale; unica modifica: «read-only except for source rescan» → «lettura per default, scrittura su richiesta esplicita dell'utente» (formulata in inglese coerente con il resto della frase della skill). Nessun altro cambio di trigger.
- L'elenco delle scartate nella Chiusura **senza dati del progetto reale**.
- Evidenza: [^src: wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md §Affermazioni della bozza senza etichetta (anomalia A1): non entrano come fatti] [^src: wiki/entities/llm-wiki-skill-bozza-alm-wiki.md §Aggiornamenti (v2026-11-22, verifica sul codice)]

## Vincoli comuni (TSK docs di contenuto)
- Prima di scrivere: `git -C code_repos/llm_wiki_skill branch --show-current` deve dare il branch condiviso; se diverso, STOP.
- Si scrive solo nei file di `code_path`; nessun file nuovo, nessun codice o script.
- Testi della skill senza ID kanban, riferimenti a ADR, wiki o factory, attribution AI o `Co-Authored-By`. Le sigle [C]/[E] solo nel TSK.
- Se la wiki non documenta un comportamento v0.6.13, la skill non lo afferma.
- Commit: non lo esegue il dev-agent; propone un messaggio generico senza ID; la sessione principale lo esegue con `tools/vcs/sm_commit.py` dopo OK esplicito. `done` solo dopo il commit; Chiusura con i tre campi (dichiarati, committati, working tree).

## Implementation Steps
1. Verifica del branch.
2. Confrontare il testo dei quattro file con l'elenco A1 e togliere ciò che non ha riga di evidenza.
3. Ripristinare la `description` originale con la sola clausola corretta (leggerla dal commit `main`: `git show main:SKILL.md` nel repo della skill).
4. Ricerca testuale: nessun 409/499 fuori dai casi decisi, nessuna riga 0.6.13 non coperta.
5. Elencare le scartate in Chiusura, senza dati del progetto reale.

## Definition of Done
- [ ] AC4: `description` originale con la sola clausola riformulata; diff della `description` contro `main` riportato.
- [ ] AC5: novità senza evidenza assenti; elenco delle scartate in Chiusura.
- [ ] Nessuna traccia (ricerca testuale su ID, factory, attribution AI) nei quattro file.

## Chiusura

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-002 AC4 | | |
| LWS-US-002 AC5 | | |
| LWS-US-002 AC7 | | |

## Dependencies
- LWS-TSK-002 — la bozza deve essere già applicata e bonificata.

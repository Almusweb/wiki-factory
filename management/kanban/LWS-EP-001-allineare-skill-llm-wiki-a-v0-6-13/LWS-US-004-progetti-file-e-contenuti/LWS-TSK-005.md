---
id: LWS-TSK-005
title: "Progetti, forme di {id}, files e files/content nella skill"
us: LWS-US-004
sprint: 01
layer: docs
consumer: agent
priority: P1
estimate: S
status: todo
depends_on: [LWS-TSK-004]
blocked_by: []
code_path: ["code_repos/llm_wiki_skill/SKILL.md", "code_repos/llm_wiki_skill/api-reference.md", "code_repos/llm_wiki_skill/examples.md", "code_repos/llm_wiki_skill/README.md"]
target: llm_wiki_skill
started_at:
closed_at:
decision_refs: []
---

# LWS-TSK-005 — Progetti, file e contenuti

## Context
La skill descrive in modo non più valido `projects`, le forme di `{id}`, `files` e `files/content`. Copre D13, D17, D18; incoerenze n. 2, n. 5, n. 6, n. 11 (parte sull'id); V10, V11, V12, V25 (parte decisa dal codice). `depends_on` su `LWS-TSK-004` per sovrapposizione di file. [^src: management/kanban/LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-004-progetti-file-e-contenuti/LWS-US-004.md §Acceptance Criteria]

## Technical Specs
- **Layer docs, consumer agent, target `llm_wiki_skill`.** Branch condiviso.
- **Evidenza dei fatti:**

| Fatto | Livello |
|---|---|
| D13: `Content-Type` è `application/json` senza `charset=utf-8` | [E] soltanto: correzione neutra |
| D17: chiave `currentProject` in `/projects` (non in `/health`) | [E+C] |
| D17: il nome del progetto come `{id}` dà 404; `resolve_project` accetta id o percorso | [E]; [C] solo su id o percorso |
| D18: leggibili md, mdx, txt, csv, json, yaml, yml, xml, html, htm, log; `rtf` fuori lista (415) | [C] |
| n. 2: 413 oltre `maxFiles`; `truncated` mai `true` osservato; presenza come `false` non chiara | [E+C] parziale |
| n. 5: alias `raw` e `raw/sources` di `root` | [C+E] |
| V10: su Windows il match del percorso non distingue le maiuscole e accetta `\` | [C] |
| V11: si divide su `/` prima di decodificare; i due punti non sono separatori; `?` spezza l'URL, `+` diventa spazio, `%XX` decodificato ovunque | [C] parziale |
| V25: `current` = progetto con `current` vero impostato dalla UI; «esterni» e «negli script l'UUID» non decisi | [C] parziale |
| `files/content` permissivo (`/` iniziale, backslash, maiuscole) | [E] soltanto: non si porta |

- Fonti: [^src: wiki/syntheses/llm-wiki-skill-vs-app-v0-6-13.md §Aggiornamenti (v2026-11-22, verifica sul codice)] [^src: wiki/concepts/llm-wiki-api-osservazioni-esecuzione-v0-6-13.md §Osservazioni del 2026-11-13 (app 0.6.13, progetto reale, non replicate)] [^src: wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md §Esito per voce]
- Fatti solo osservati in forma neutra: si corregge soltanto la frase smentita.

## Vincoli comuni (TSK docs di contenuto)
- Prima di scrivere: `git -C code_repos/llm_wiki_skill branch --show-current` = branch condiviso; altrimenti STOP.
- Si scrive solo nei file di `code_path`; nessun file nuovo, codice o script.
- Testi della skill senza ID kanban, riferimenti a ADR, wiki o factory, attribution AI o `Co-Authored-By`; [C]/[E] solo nel TSK.
- Se la wiki non documenta un comportamento v0.6.13, la skill non lo afferma.
- Commit: non lo esegue il dev-agent; propone un messaggio generico senza ID; la sessione principale lo esegue con `tools/vcs/sm_commit.py` dopo OK esplicito. `done` solo dopo il commit; Chiusura con i tre campi (dichiarati, committati, working tree).

## Implementation Steps
1. Verifica del branch.
2. `projects`: aggiungere `currentProject`, esempio coerente, nessuna attribuzione a `/health`.
3. `{id}`: togliere «esatta» e le prescrizioni su maiuscole e slash; tenere l'avvertenza `%2F`.
4. `files/content`: elenco estensioni identico ovunque, `rtf` 415. `files`: 413 oltre `maxFiles`, nessun `truncated`, alias `raw` e `raw/sources` ovunque.
5. `Content-Type` neutro; togliere «negli script serve l'UUID» e «progetti esterni»; non portare la permissività osservata.
6. Controlli testuali con comando ed esito.

## Definition of Done
- [ ] AC1..AC6 verificati con ricerca testuale e hunk del diff.
- [ ] AC7: riga di evidenza per ogni affermazione cambiata.
- [ ] Nessuna traccia nei file toccati.

## Chiusura

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-004 AC1 | | |
| LWS-US-004 AC2 | | |
| LWS-US-004 AC3 | | |
| LWS-US-004 AC4 | | |
| LWS-US-004 AC5 | | |
| LWS-US-004 AC6 | | |
| LWS-US-004 AC7 | | |

## Dependencies
- LWS-TSK-004 — serializzazione per sovrapposizione di file.

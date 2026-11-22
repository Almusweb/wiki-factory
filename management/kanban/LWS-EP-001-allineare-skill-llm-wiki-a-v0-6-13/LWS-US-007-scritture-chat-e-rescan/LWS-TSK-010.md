---
id: LWS-TSK-010
title: "Rescan e changedTasks nella skill, assenza di 499 e ricetta con una route nuova"
us: LWS-US-007
sprint: 01
layer: docs
consumer: agent
priority: P1
estimate: S
status: todo
depends_on: [LWS-TSK-009]
blocked_by: []
code_path: ["code_repos/llm_wiki_skill/SKILL.md", "code_repos/llm_wiki_skill/api-reference.md", "code_repos/llm_wiki_skill/examples.md"]
target: llm_wiki_skill
started_at:
closed_at:
decision_refs: []
---

# LWS-TSK-010 — Rescan, `changedTasks` e ricetta

## Context
Seconda parte di LWS-US-007 (AC6-AC9, AC10): comportamento del rescan, codici 499 e 409, almeno una ricetta di `examples.md` con una route nuova. Copre D21 (rescan), n. 13 (parte nota), V16-V18. `depends_on` su `LWS-TSK-009` per sovrapposizione di file. [^src: management/kanban/LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-007-scritture-chat-e-rescan/LWS-US-007.md §Acceptance Criteria]

## Technical Specs
- **Layer docs, consumer agent, target `llm_wiki_skill`.** Branch condiviso. `README.md` non è atteso.
- **Evidenza dei fatti:**

| Fatto | Livello |
|---|---|
| V16-V18: il rescan non accoda nella coda di ingest dell'app ma aggiorna lo snapshot e accoda i cambi nella coda Rust; `changedTasks` vuoto significa già visto; `created` e `modified` avviano l'ingest; l'ingest parte per il progetto aperto con `enabled`, `autoIngest` e un LLM; per i progetti inattivi dipende da «Watch all projects» | [C] parziale |
| «Watch all projects»: default, LLM nel ramo inattivi; elenco completo dei `kind` | non noti |
| 409 solo per `pages/write` (contratto); 499 non in wiki | [C] contratto / non in wiki |

- Non si afferma che i cambi si perdano né che l'ingest parta per i progetti inattivi.
- Fonti: [^src: wiki/concepts/llm-wiki-sincronizzazione-file.md §Dettaglio] [^src: wiki/gaps.md §2026-11-22 13:30 — llm-wiki-watch-all-projects-residui] [^src: wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md §Esito per voce]
- La ricetta di `examples.md` usa una route nuova senza il corpo non noto (per esempio la lettura di `reviews`, che ha evidenza [E+C]).

## Vincoli comuni (TSK docs di contenuto)
- Prima di scrivere: `git -C code_repos/llm_wiki_skill branch --show-current` = branch condiviso; altrimenti STOP.
- Si scrive solo nei file di `code_path`; nessun file nuovo, codice o script.
- Testi della skill senza ID kanban, riferimenti a ADR, wiki o factory, attribution AI o `Co-Authored-By`; [C]/[E] solo nel TSK.
- Se la wiki non documenta un comportamento v0.6.13, la skill non lo afferma.
- Commit: non lo esegue il dev-agent; propone un messaggio generico senza ID; la sessione principale lo esegue con `tools/vcs/sm_commit.py` dopo OK esplicito. `done` solo dopo il commit; Chiusura con i tre campi (dichiarati, committati, working tree).

## Implementation Steps
1. Verifica del branch.
2. Descrivere il rescan: aggiorna lo snapshot e riporta `changedTasks`; vuoto = già visto; non accoda da sé l'ingest; l'ingest parte per il progetto aperto alle condizioni note.
3. `changedTasks[].kind`: solo `created` e `modified` avviano l'ingest, senza elenco completo.
4. Verificare l'assenza del codice 499 e che il 409 compaia solo per `pages/write`.
5. Aggiungere in `examples.md` almeno una ricetta con una route nuova, senza il corpo non noto.
6. Ricerche testuali con comando ed esito.

## Definition of Done
- [ ] AC6..AC9 di LWS-US-007 verificati con ricerca testuale e hunk.
- [ ] AC10: riga di evidenza per ogni affermazione cambiata.
- [ ] Nessuna traccia nei file toccati.

## Chiusura
<!-- AC1-AC5 sono di LWS-TSK-009 -->

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-007 AC6 | | |
| LWS-US-007 AC7 | | |
| LWS-US-007 AC8 | | |
| LWS-US-007 AC9 | | |
| LWS-US-007 AC10 | | |

## Dependencies
- LWS-TSK-009 — serializzazione per sovrapposizione di file.

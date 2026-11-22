---
id: LWS-TSK-015
title: "Verifica di coerenza fra i quattro file della skill sui termini toccati da 003..007"
us: LWS-US-009
sprint: 02
layer: docs
consumer: agent
priority: P1
estimate: S
status: todo
depends_on: [LWS-TSK-014]
blocked_by: []
code_path: ["code_repos/llm_wiki_skill/SKILL.md", "code_repos/llm_wiki_skill/api-reference.md", "code_repos/llm_wiki_skill/examples.md", "code_repos/llm_wiki_skill/README.md"]
target: llm_wiki_skill
started_at:
closed_at:
decision_refs: []
---

# LWS-TSK-015 — Verifica di coerenza interna

## Context
Controllo di chiusura per n. 2, 3, 4, 5, 8, 9, 10: gli stessi termini devono avere lo stesso significato in tutti i punti dei quattro file. Gli unici interventi ammessi sono correzioni di coerenza con evidenza già in wiki; altrimenti la frase si toglie. [^src: management/kanban/LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-009-coerenza-interna-e-versione/LWS-US-009.md §Acceptance Criteria]

## Technical Specs
- **Layer docs, consumer agent, target `llm_wiki_skill`.** Branch condiviso.
- **Termini da verificare** (per le storie di contenuto, TSK 004..010): CORS, localhost, 404, 405, 501, «sola lettura», `hybrid`, «scrittura». Per ciascuno: ricerca testuale su tutti e quattro i file e confronto dei significati.
- Per ogni correzione: riga di evidenza ([C]/[E]/[C+E]) già presente nelle tabelle dei TSK 004..010; senza riga, la frase si toglie.
- Licenza e rotazione del token non si toccano; valori di `status` di `/health` restano i quattro noti.
- Fonti: [^src: wiki/entities/llm-wiki-skill.md §Incoerenze interne della skill (materiale per la PR)]

## Vincoli comuni (TSK docs di contenuto)
- Prima di scrivere: `git -C code_repos/llm_wiki_skill branch --show-current` = branch condiviso; altrimenti STOP.
- Si scrive solo nei file di `code_path`; nessun file nuovo, codice o script.
- Testi della skill senza ID kanban, riferimenti a ADR, wiki o factory, attribution AI o `Co-Authored-By`; [C]/[E] solo nel TSK.
- Se la wiki non documenta un comportamento v0.6.13, la skill non lo afferma.
- Commit: solo se il TSK produce modifiche; lo esegue la sessione principale con `tools/vcs/sm_commit.py` dopo OK esplicito, messaggio generico senza ID. Se non ci sono modifiche, la Chiusura lo dichiara (nessun commit). `done` solo dopo il commit o la dichiarazione di assenza di modifiche.

## Implementation Steps
1. Verifica del branch.
2. Per ogni termine: ricerca testuale nei quattro file (comando ed esito per ciascuno) e tabella dei significati trovati.
3. Correggere le divergenze o togliere le frasi senza evidenza.
4. Ripetere le ricerche dopo le correzioni.
5. Controllo di non-traccia (ID kanban, factory, attribution AI) sui file toccati.

## Definition of Done
- [ ] AC5 di LWS-US-009 verificato: stesso significato in tutti i punti, comandi ed esiti nella Chiusura.
- [ ] AC7: riga di evidenza per ogni affermazione cambiata.
- [ ] Nessuna traccia nei file toccati.

## Chiusura

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-009 AC5 | | |
| LWS-US-009 AC7 | | |

## Dependencies
- LWS-TSK-014 — ultima modifica di contenuto prima della verifica.

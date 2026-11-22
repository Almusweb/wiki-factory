---
id: LWS-TSK-018
title: "Apertura della PR verso nashsu/llm_wiki_skill (gate umano)"
us: LWS-US-010
sprint: 02
layer: infra
consumer: human
priority: P1
estimate: XS
status: todo
depends_on: [LWS-TSK-017]
blocked_by: []
code_path: ["code_repos/llm_wiki_skill"]
target: llm_wiki_skill
started_at:
closed_at:
decision_refs: []
---

# LWS-TSK-018 — Apertura della PR upstream

## Context
Con il branch pushato e l'audit chiuso, si apre la PR dal branch condiviso della fork (tagliato da `main`) verso `nashsu/llm_wiki_skill`. Operazione su remote: gate umano esplicito. Il legame fra ID kanban e PR vive solo nella factory. [^src: management/kanban/LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-010-preparare-la-pr-upstream/LWS-US-010.md §Business Rules] [^src: wiki/purpose.md §Pull request upstream]

## Technical Specs
- **Consumer:** `human`; può eseguirlo la sessione principale con override esplicito, scritto nella Chiusura.
- **Contenuto della PR:** titolo e descrizione generici, la descrizione è quella redatta da `LWS-TSK-016` e riletta con i pattern di `tools/vcs/ai_policy.py` (nessun ID kanban, riferimento alla factory o attribution AI). Dichiara la base di verifica (lettura del codice sorgente dell'app alla v0.6.13 e alcune risposte verificate su un'app in esecuzione) e i punti non verificati lasciati invariati.
- **Gate:** OK esplicito dell'utente sul testo finale (titolo e descrizione) e sull'apertura. Strumento (`gh pr create` o interfaccia web) a scelta dell'utente; se `gh` non è disponibile, si fornisce il testo e l'utente apre la PR.
- Nessuna personalizzazione (fase B) nella PR.
- Il collegamento fra la PR (URL) e gli ID `LWS-` si annota solo in `wiki/log.md` o nella Chiusura di questo TSK, mai nella PR.

## Implementation Steps
1. Rileggere il testo finale con i pattern di `tools/vcs/ai_policy.py` e riportare comando ed esito.
2. Mostrare titolo e descrizione all'utente e ottenere l'OK esplicito.
3. Aprire la PR da `<fork>:<branch>` verso `nashsu/llm_wiki_skill:main`; riportare comando ed esito e URL della PR.
4. Annotare l'URL nella Chiusura (lato factory).

## Definition of Done
- [ ] OK esplicito dell'utente al testo e all'apertura riportato.
- [ ] PR aperta con comando ed esito; URL registrato solo lato factory.
- [ ] Nessun ID kanban, riferimento alla factory o attribution AI nel testo della PR.

## Chiusura

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-010 AC6 | | |

## Dependencies
- LWS-TSK-017 — branch pushato sulla fork.

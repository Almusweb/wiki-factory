---
id: LWS-US-001
title: Confermare la base di partenza
role: Maintainer della fork della skill llm-wiki
priority: high
status: ready
wiki_page: wiki/entities/llm-wiki-skill.md
blocked_by: []
pending_clarification: []
depends_on: []
---

# LWS-US-001 — Confermare la base di partenza

## Descrizione
Come maintainer della fork della skill `llm-wiki`, voglio confermare che `main` della fork coincide con `main` di `nashsu/llm_wiki_skill` (o sapere di quanto differisce), affinché la PR non sia costruita su uno stato superato dell'upstream.

## Business Rules
- Regole trasversali dell'epica LWS-EP-001: valgono tutte.
- Evidenza in wiki: nessuna. La skill è a `main`, commit `642b438` (2026-05-19, «update»); che la fork sia identica all'upstream è un dato fornito dal chiamante dell'estrazione, non verificabile dal raw. [^src: wiki/entities/llm-wiki-skill.md §Contesto]
- Il fetch dell'upstream è un'operazione su remote: richiede OK esplicito dell'utente al gate.
- Nessuna modifica ai file della skill in questa storia.

## UI Reference
[^src: wiki/entities/llm-wiki-skill.md §Contesto]
[^src: wiki/entities/llm-wiki-skill.md §Struttura e installazione]

## Acceptance Criteria
- [ ] `main` della fork è confrontato con `main` di `nashsu/llm_wiki_skill`; l'esito (identici, oppure elenco dei commit di scarto) è registrato nel TSK con il comando eseguito e il suo esito.
- [ ] Se l'upstream è avanti, il lavoro riparte dal suo stato e sono elencate le sovrapposizioni fra i commit di scarto e le correzioni previste dall'epica.
- [ ] È registrato il commit di partenza del lavoro, su un branch da `main` dedicato a questa PR.
- [ ] Il fetch dell'upstream ha OK esplicito dell'utente, riportato nel TSK.
- [ ] Nessun file della skill è modificato da questa storia.

## Fonti
[^src: wiki/entities/llm-wiki-skill.md §Contesto]
[^src: wiki/purpose.md §Pull request upstream]

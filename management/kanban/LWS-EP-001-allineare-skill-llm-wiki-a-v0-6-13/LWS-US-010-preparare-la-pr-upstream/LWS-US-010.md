---
id: LWS-US-010
title: Preparare la PR upstream senza tracce e senza affermazioni scoperte
role: Maintainer della fork della skill llm-wiki
priority: high
status: ready
wiki_page: wiki/entities/llm-wiki-skill.md
blocked_by: []
pending_clarification: []
depends_on: [LWS-US-009]
---

# LWS-US-010 — Preparare la PR upstream senza tracce e senza affermazioni scoperte

## Descrizione
Come maintainer della fork della skill `llm-wiki`, voglio consegnare l'aggiornamento come contributo pulito e verificabile al maintainer upstream, affinché la PR non porti tracce della factory né affermazioni prive di evidenza.

## Business Rules
- Regole trasversali dell'epica LWS-EP-001: valgono tutte.
- La PR parte da `main` del submodule `code_repos/llm_wiki_skill` e contiene solo l'aggiornamento generico (fase A). La fase B (estensioni personali su `develop`) non ha materiale e non entra nel diff.
- Nessuna traccia della factory nei file della skill e nei commit: niente ID kanban (EP, US, TSK, LWS), niente riferimenti a ADR, wiki o factory, niente attribution AI né `Co-Authored-By`. I pattern sono quelli di `tools/vcs/ai_policy.py` (fonte unica); i commit nel repo cliente si fanno con `tools/vcs/sm_commit.py` quando il repo rientra nello scope della policy. [^src: wiki/purpose.md §Pull request upstream]
- Il legame fra ID kanban e PR vive solo nella factory, non nella PR. [^src: wiki/purpose.md §Pull request upstream]
- Commit, push e apertura della PR richiedono OK esplicito dell'utente a ogni gate (regola cliente).
- Con questa storia l'audit sulle affermazioni è completo: ogni frase cambiata ha una riga di evidenza nel TSK, o è tolta.
- Cosa resta fuori dalla PR se non verificato: l'elenco in `LWS-EP-001.md` (§Cosa resta fuori dalla PR se non verificato) e i residui di LWS-US-008.

## UI Reference
[^src: wiki/purpose.md §Pull request upstream]
[^src: wiki/entities/llm-wiki-skill-bozza-alm-wiki.md §Elementi non trasferibili a una PR upstream]
[^src: wiki/syntheses/llm-wiki-skill-vs-app-v0-6-13.md §Contesto]

## Acceptance Criteria
- [ ] La PR parte da `main` con un branch dedicato e modifica solo i quattro file markdown esistenti della skill (`SKILL.md`, `api-reference.md`, `examples.md`, `README.md`); nessun file nuovo, nessun codice.
- [ ] Il diff e i messaggi di commit non contengono ID kanban (`EP-`, `US-`, `TSK-`, `LWS-`), riferimenti a ADR, wiki o factory, attribution AI né `Co-Authored-By`; la verifica usa i pattern di `tools/vcs/ai_policy.py` e riporta comando ed esito.
- [ ] Il diff non contiene nessuno degli elementi non trasferibili della bozza (stessa ricerca testuale di LWS-US-002: etichette `[obs]` e `[code]`, `FORK.md`, avvisi di fork, task interni, percorsi locali reali, dati di un progetto reale con data) né nomi del progetto reale o dell'utente.
- [ ] **Audit delle affermazioni:** per ciascuna affermazione cambiata esiste nel TSK una riga di evidenza [C], [E] o [C+E]; quelle senza riga sono tolte, e l'elenco delle scartate è riportato senza dati del progetto reale.
- [ ] La descrizione della PR è generica e non riporta ID kanban né riferimenti alla factory; dichiara la base di verifica (lettura del codice sorgente dell'app alla v0.6.13 e alcune risposte verificate su un'app in esecuzione) e l'elenco dei punti non verificati lasciati invariati.
- [ ] Nessun commit, push o apertura di PR è avvenuto senza OK esplicito dell'utente al gate; per ciascuna operazione sono riportati il comando e il suo esito.
- [ ] Nessuna personalizzazione (fase B) è nel diff.

## Fonti
[^src: wiki/purpose.md §Pull request upstream]
[^src: wiki/entities/llm-wiki-skill-bozza-alm-wiki.md §Elementi non trasferibili a una PR upstream]
[^src: wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md §Che cosa resta da verificare]

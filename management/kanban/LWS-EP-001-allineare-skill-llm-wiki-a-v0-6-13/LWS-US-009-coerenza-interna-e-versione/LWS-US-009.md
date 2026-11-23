---
id: LWS-US-009
title: Coerenza interna e dichiarazione di versione
role: Agente AI che usa la skill llm-wiki
priority: medium
status: done
wiki_page: wiki/entities/llm-wiki-skill.md
blocked_by: []
pending_clarification: []
depends_on: [LWS-US-003, LWS-US-004, LWS-US-005, LWS-US-006, LWS-US-007]
started_at: 2026-11-23
closed_at: 2026-11-23
---

# LWS-US-009 — Coerenza interna e dichiarazione di versione

## Descrizione
Come agente AI che usa la skill `llm-wiki`, voglio che i quattro file della skill non si contraddicano e che la versione dichiarata dica che cosa è stato verificato, affinché sappia su quale app il contratto vale e quando controllare il drift.

## Business Rules
- Regole trasversali dell'epica LWS-EP-001: valgono tutte.
- Copre n. 11, n. 16 (valori di `status`), n. 17; A4 (incongruenze ereditate); è il controllo di chiusura per n. 2, 3, 4, 5, 8, 9, 10.
- Decisione dell'utente sulla versione: la skill dichiara solo «verificata su v0.6.13» con la base dichiarata; niente «0.4.10+»; nessuna funzione detta valida «dalla versione X» (la storia delle versioni è un gap aperto, `llm-wiki-api-storia-versioni`).
- Decisione dell'utente sul drift (N3): la regola diventa «qualunque versione riportata da `/health` diversa da quella verificata», non più solo «major version bump».
- La base della verifica si dichiara in termini generici: lettura del codice sorgente dell'app alla v0.6.13 e alcune risposte verificate su un'app in esecuzione. Non si citano progetto, date né identificativi della prova.
- Licenza e rotazione del token (n. 16) non si toccano. L'incoerenza n. 11 è interna alla skill (verificabile leggendo i file, senza dati di v0.6.13).
- Il campo `status` di `/health` ha quattro valori anche nella v0.6.13 [C].

[^src: wiki/entities/llm-wiki-skill.md §Incoerenze interne della skill (materiale per la PR)]
[^src: wiki/entities/llm-wiki-skill.md §Versione dichiarata]
[^src: wiki/concepts/llm-wiki-skill-api-v1-dichiarata.md §Versione dichiarata]
[^src: wiki/syntheses/llm-wiki-skill-vs-app-v0-6-13.md §Contesto]
[^src: wiki/gaps.md §2026-11-22 11:24 — llm-wiki-api-storia-versioni]

## UI Reference
[^src: wiki/entities/llm-wiki-skill.md §Versione dichiarata]
[^src: wiki/entities/llm-wiki-skill.md §Incoerenze interne della skill (materiale per la PR)]

## Acceptance Criteria
- [x] Il README dichiara il numero corretto di file (quattro) e il comando di update usa il nome della skill (`llm-wiki`, non `llm_wiki_skill`) (n. 11); «four forms» di `{id}` è coerente con le tre forme del server più il nome risolto lato client (A4). (LWS-TSK-014 §Chiusura, AC1)
- [x] La dichiarazione di versione dice «verificata su v0.6.13» e dichiara la base (lettura del codice sorgente, alcune risposte verificate su un'app in esecuzione); non resta «0.4.10+»; nessuna funzione è detta valida «dalla versione X»; non cita progetto, date né identificativi della prova. (LWS-TSK-014 §Chiusura, AC2)
- [x] L'esempio di `/health` del README ha `version` e i campi coerenti con LWS-US-005. (LWS-TSK-014 §Chiusura, AC3)
- [x] La regola di controllo del drift dice di confrontare la versione riportata da `/health` con quella verificata e di controllare `api-reference.md` per qualunque versione diversa; non dipende più da un «major version bump». (LWS-TSK-014 §Chiusura, AC4; la stessa regola è in `SKILL.md` per LWS-TSK-015 §Chiusura, AC7)
- [x] Una ricerca testuale sui quattro file per ogni termine toccato dalle storie LWS-US-003..007 (CORS, localhost, 404, 405, 501, «sola lettura», `hybrid`, «scrittura») mostra lo stesso significato in tutti i punti; il comando e l'esito sono riportati nel TSK. (LWS-TSK-015 §Chiusura, AC5)
- [x] I valori di `status` di `/health` restano i quattro noti; licenza e rotazione del token non sono toccate. (LWS-TSK-014 §Chiusura, AC6)
- [x] Ogni affermazione cambiata ha nel TSK la riga di evidenza corrispondente; nessuna è priva di evidenza. (LWS-TSK-014 §Chiusura, AC7, per README, dichiarazione di versione e marcatori di versione; LWS-TSK-015 §Chiusura, AC7, per la regola di drift in `SKILL.md` e l'intestazione di `examples.md`)

## Nota di modifica
- 2026-11-23 — Chiusura (rollup; fonte: tabelle §Chiusura di LWS-TSK-014 e LWS-TSK-015, entrambi `done`). Prima: `status: ready`, AC non spuntati. Ora: `status: done`, AC1..AC7 spuntati con riferimento ai TSK pertinenti (AC1..AC4 e AC6 da LWS-TSK-014; AC5 da LWS-TSK-015; AC7 da entrambi, ciascuno per la sua parte); commit nel repo della skill `9c2669e` (LWS-TSK-014) e `fd8a5a4` (LWS-TSK-015) sul branch `docs/align-v0-6-13`; `started_at` e `closed_at` 2026-11-23 (date del lavoro, dai TSK). Nessun AC derogato. Decisione dell'utente riportata da LWS-TSK-015: la regola di drift sta anche in `SKILL.md`, perché il README non si legge in esecuzione; «(verified on 0.6.13)» in `examples.md` r.173 tenuto; marcatori «0.6.13.» sulle route lasciati.
- Residui rinviati a LWS-TSK-016 (dichiarati nei due TSK, non toccati): «labelled "API Server" in older builds» (`README.md` r.55, `SKILL.md` r.80); «shorter than older docs stated» (`api-reference.md` r.326); `api-reference.md` r.525 («The old rule … does not hold on 0.6.13»); riferimenti a righe di codice (`api-reference.md` r.296, `commands/search.rs`); inferenza su `vectorScore` in `examples.md` r.179. Restano senza intervento: `SKILL.md` r.220 («routes that change state», ripetizione senza cambio di significato) e «Mutates state» in `api-reference.md` r.397 contro «Changes state» altrove.

## Fonti
[^src: wiki/entities/llm-wiki-skill.md §Incoerenze interne della skill (materiale per la PR)]
[^src: wiki/syntheses/llm-wiki-skill-vs-app-v0-6-13.md §Contesto]

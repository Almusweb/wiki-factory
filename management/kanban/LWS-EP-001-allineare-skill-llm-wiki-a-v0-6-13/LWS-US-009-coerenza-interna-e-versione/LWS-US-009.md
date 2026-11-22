---
id: LWS-US-009
title: Coerenza interna e dichiarazione di versione
role: Agente AI che usa la skill llm-wiki
priority: medium
status: ready
wiki_page: wiki/entities/llm-wiki-skill.md
blocked_by: []
pending_clarification: []
depends_on: [LWS-US-003, LWS-US-004, LWS-US-005, LWS-US-006, LWS-US-007]
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
- [ ] Il README dichiara il numero corretto di file (quattro) e il comando di update usa il nome della skill (`llm-wiki`, non `llm_wiki_skill`) (n. 11); «four forms» di `{id}` è coerente con le tre forme del server più il nome risolto lato client (A4).
- [ ] La dichiarazione di versione dice «verificata su v0.6.13» e dichiara la base (lettura del codice sorgente, alcune risposte verificate su un'app in esecuzione); non resta «0.4.10+»; nessuna funzione è detta valida «dalla versione X»; non cita progetto, date né identificativi della prova.
- [ ] L'esempio di `/health` del README ha `version` e i campi coerenti con LWS-US-005.
- [ ] La regola di controllo del drift dice di confrontare la versione riportata da `/health` con quella verificata e di controllare `api-reference.md` per qualunque versione diversa; non dipende più da un «major version bump».
- [ ] Una ricerca testuale sui quattro file per ogni termine toccato dalle storie LWS-US-003..007 (CORS, localhost, 404, 405, 501, «sola lettura», `hybrid`, «scrittura») mostra lo stesso significato in tutti i punti; il comando e l'esito sono riportati nel TSK.
- [ ] I valori di `status` di `/health` restano i quattro noti; licenza e rotazione del token non sono toccate.
- [ ] Ogni affermazione cambiata ha nel TSK la riga di evidenza corrispondente; nessuna è priva di evidenza.

## Fonti
[^src: wiki/entities/llm-wiki-skill.md §Incoerenze interne della skill (materiale per la PR)]
[^src: wiki/syntheses/llm-wiki-skill-vs-app-v0-6-13.md §Contesto]

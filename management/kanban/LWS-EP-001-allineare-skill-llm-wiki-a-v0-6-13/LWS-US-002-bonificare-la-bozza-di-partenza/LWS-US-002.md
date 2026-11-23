---
id: LWS-US-002
title: Bonificare la bozza come testo di partenza
role: Maintainer della fork della skill llm-wiki
priority: high
status: done
wiki_page: wiki/entities/llm-wiki-skill-bozza-alm-wiki.md
blocked_by: []
pending_clarification: []
depends_on: [LWS-US-001]
started_at: 2026-11-23
closed_at: 2026-11-23
---

# LWS-US-002 — Bonificare la bozza come testo di partenza

## Descrizione
Come maintainer della fork della skill `llm-wiki`, voglio partire dalla bozza di riscrittura già fatta, privata di tutto ciò che non è trasferibile a una PR upstream, affinché il lavoro riusi le 173 modifiche esistenti senza portare nella PR nulla che non sia generico o provato.

## Business Rules
- Regole trasversali dell'epica LWS-EP-001: valgono tutte.
- La bozza è un testo candidato scritto da un modello in un progetto locale dell'utente (vedi `wiki/entities/llm-wiki-skill-bozza-alm-wiki.md`): **non è una fonte di fatti sull'app**. I fatti entrano dalle righe di evidenza delle storie di contenuto. [^src: wiki/entities/llm-wiki-skill-bozza-alm-wiki.md §Contesto]
- docs-dev legge la bozza **in sola lettura** dal percorso esterno del progetto locale dell'utente; scrive solo nel branch del submodule `code_repos/llm_wiki_skill`; **nulla è copiato nella factory**; nessun dato del progetto reale compare in output della factory (TSK, log, report) né nella PR.
- Elementi non trasferibili, dalla scheda: `FORK.md` per intero; le etichette `[obs]` e `[code]` e le loro legende; l'avviso di fork e le istruzioni «non da eseguire su questa copia»; riferimenti a task interni e a un percorso locale reale; dati di un progetto reale in una data (score 122, 102 e 82, «Values seen on a real wiki», fonti accodate il 2026-11-13, «seen once», id e timestamp dell'esempio di review). [^src: wiki/entities/llm-wiki-skill-bozza-alm-wiki.md §Elementi non trasferibili a una PR upstream]
- Anomalia A1: la regola «senza etichetta = upstream» è contraddetta da novità 0.6.13 senza etichetta (`description`, righe 0.6.13 di `SKILL.md`, 409 e 499, quasi tutta la sezione «Additions» di `api-reference.md`, CORS, `limit` 0 con 400). Quelle senza una riga di evidenza non si portano. Decisi dal codice: solo `limit` 0 con 400, CORS e l'esclusione di `rtf`. [^src: wiki/entities/llm-wiki-skill-bozza-alm-wiki.md §Anomalie A1-A5 (della fonte)] [^src: wiki/entities/llm-wiki-skill-bozza-alm-wiki.md §Aggiornamenti (v2026-11-22, verifica sul codice)]
- Decisione sul trigger (N4): la `description` resta quella originale; si corregge solo la clausola «read-only except for source rescan», che è falsa, secondo la regola sulle scritture (lettura per default, scrittura su richiesta esplicita).
- Le incongruenze ereditate (A4: «four forms», 400 e 413 per il corpo, «three markdown files», `--skill llm_wiki_skill` contro `llm-wiki`) non si risolvono qui: toccano LWS-US-006 e LWS-US-009.

## UI Reference
[^src: wiki/entities/llm-wiki-skill-bozza-alm-wiki.md §Elementi non trasferibili a una PR upstream]
[^src: wiki/entities/llm-wiki-skill-bozza-alm-wiki.md §Anomalie A1-A5 (della fonte)]

## Acceptance Criteria
- [x] Il punto di partenza è la bozza applicata su un branch da `main` del submodule; nessun file nuovo oltre ai quattro della skill (`SKILL.md`, `api-reference.md`, `examples.md`, `README.md`). (LWS-TSK-002 §Chiusura, AC1)
- [x] Nei quattro file non resta nessuno di questi elementi: etichette `[obs]` e `[code]` e legende; `FORK.md` e ogni riferimento ad esso; avvisi di fork e istruzioni «non da eseguire su questa copia»; riferimenti a task interni; percorsi locali reali; dati di un progetto reale con data (score 122, 102 e 82, «Values seen on a real wiki», fonti accodate il 2026-11-13, «seen once», id e timestamp dell'esempio di review). La verifica è una ricerca testuale su questi elementi nei quattro file, con comando ed esito riportati nel TSK. (LWS-TSK-002 §Chiusura, AC2)
- [x] Gli esempi non contengono nomi del progetto reale né dell'utente. (LWS-TSK-002 §Chiusura, AC3)
- [x] La `description` (trigger) è quella originale, con la sola clausola «read-only except for source rescan» riformulata in «lettura per default, scrittura su richiesta esplicita dell'utente»; gli altri cambi di trigger della bozza non sono presenti. (LWS-TSK-003 §Chiusura, AC4)
- [x] Le novità senza etichetta della bozza (A1) non coperte da una riga di evidenza sono assenti dai quattro file; l'elenco di quelle scartate è registrato nel TSK senza riportare dati del progetto reale. (LWS-TSK-003 §Chiusura, AC5)
- [x] Nessun file e nessun dato della bozza è copiato dentro il repository della factory; il TSK riporta solo il riferimento alla scheda wiki, non il percorso assoluto dell'utente. (LWS-TSK-002 §Chiusura, AC6)
- [x] Nessun ID kanban, riferimento alla factory o attribution AI nei quattro file; nessun commit senza OK esplicito dell'utente. (LWS-TSK-002 §Chiusura, AC7; LWS-TSK-003 §Chiusura, AC7)

## Nota di modifica
- 2026-11-23 — Chiusura (rollup; fonte: tabelle §Chiusura di LWS-TSK-002 e LWS-TSK-003, entrambi `done`). Prima: `status: ready`, AC non spuntati. Ora: `status: done`, AC1..AC7 spuntati con riferimento ai TSK pertinenti (AC1, AC2, AC3, AC6 da LWS-TSK-002; AC4, AC5 da LWS-TSK-003; AC7 da entrambi); commit nel repo della skill `aeada6b` e `778b149` sul branch `docs/align-v0-6-13`; `started_at` e `closed_at` 2026-11-23 (date del lavoro, dai TSK).

## Fonti
[^src: wiki/entities/llm-wiki-skill-bozza-alm-wiki.md §Dettaglio]
[^src: wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md §Affermazioni della bozza senza etichetta (anomalia A1): non entrano come fatti]

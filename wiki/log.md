---
id: log
type: log
title: Wiki Log
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: []
tags: [audit]
---

# Wiki Log

Registro append-only delle operazioni (skill `wiki-log-entry`): le voci si aggiungono in coda, mai modificate.

## [2026-11-20] ingest | 2026-11-20-repo-llm_wiki
Pagine create: 12 | Figure: 1 | Aggiornamenti: 1 | Gap nuovi: 12 | Gap chiusi: 0

## [2026-11-20] lint | check completo
Orphan: 0 | Broken: 0 | Unsourced: 0 | Kanban: 0 err | Coerenza: 0 err

---
date: 2026-11-20
type: session-close
session_label: session-2026-11-20-16-3649aa67
operator: Alessandro Musio
outcome: completed
artifact: raw/sessions/session-2026-11-20-16-3649aa67.md
context: Bootstrap wiki-factory 2.48 su llm_wiki: ingest, opt-in, analisi persistenza, difetti del master
---

## [2026-11-20] ingest | 2026-11-20-repo-llm_wiki (aggiornamento) + session-2026-11-20-16-3649aa67
Pagine create: 9 | Figure: 0 | Aggiornamenti: 5 | Gap nuovi: 8 | Gap chiusi: 0

## [2026-11-20] lint | check completo (seconda esecuzione del giorno)
Orphan: 0 | Broken: 0 | Unsourced: 7 | Kanban: 0 err | Coerenza: 0 err

## [2026-11-20] ingest | 2026-11-20-repo-llm_wiki-persistenza-a + 2026-11-20-repo-llm_wiki-persistenza-b + 2026-11-20-repo-llm_wiki-persistenza-c
Pagine create: 5 | Figure: 0 | Aggiornamenti: 10 | Gap nuovi: 10 | Gap chiusi: 0
Ora: 21:12 | parallel_workers: 3 | Files touched: 18 (15 pagine, gaps.md, index.md, log.md)
Slug collisions risolte: 8, tutte concept compatibili, fuse (archivi-persistenza A+B; schema-dati A+B; gestione-file-corrotti A+B; rischi-persistenza A+B+C; versioni-e-migrazioni B+C; api-locale A+C; agente A+C; operazioni-distruttive A+C).
Contraddizioni: 25 segnalate dai worker, 18 distinte su 8 pagine, scritte in `## Contradictions` senza toccare il testo esistente.
Validazione contratto `proposed_pages`: primo giro exit 1 per tutti e tre i JSON; retry del worker C e pulizia dei campi extra di A e B; poi valido (exit 0).
Esito dei rischi di llm-wiki-rischi-persistenza invariato (EP-004): solo indizi da verificare. Nessun gap assegnato a US-014..US-017 è stato chiuso.

## [2026-11-20] lint | check completo (terza esecuzione del giorno)
Orphan: 0 | Broken: 0 | Unsourced: 6 | Kanban: 0 err | Coerenza: 0 err

## [2026-11-20] sweep | esito=closed
Categorie: unsupported-claim=6, dangling-concept=0, terminology-drift=0
Iter 1: applied=7, residual=0 | Files touched: 3 (master-difetti-rilevati.md, llm-wiki-archivi-persistenza.md, log.md)
Dettaglio: W8-W13 via Aggiornamenti; W15 riga `project.json` corretta in-place su decisione utente. Rinviati (fuori sweep): «17 archivi», «solo due versioni». Rescan non eseguito dal keeper (nessun Bash): da fare dalla sessione principale.

## [2026-11-20] sweep | correzione esito iterazione 1: esito=stuck (non closed)
La voce precedente dichiarava `esito=closed` senza rescan (il keeper non aveva Bash). Rescan eseguito: `wiki/lint/2026-11-20-sweep-rescan.md` (wiki-lint scoped, Check 2) e `python3 tools/lint/run-deterministic.py` (exit 0, 6 WARNING invariati, nessuno nuovo).
Chiusi: W15-r28 (`project.json`, correzione autorizzata dall'utente). Ancora presenti: W8-W13 — le fonti nel blocco `## Aggiornamenti` in coda non rientrano nella finestra di 3 righe dell'euristica del Check 2. Citazioni nuove verificate: tutte puntano a file e sezioni esistenti.

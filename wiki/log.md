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

## [2026-11-21] sweep | iterazione 2: esito=regression (W8-W13 chiusi, 2 nuovi candidati di igiene)
Categorie: unsupported-claim=6 | Iter 2: applied=6 (citazioni spostate in fondo alle righe 18, 37, 65, 79, 93 di master-difetti-rilevati e 49 di llm-wiki-archivi-persistenza; testo invariato, verificato con `git diff --word-diff`).
Rescan: `wiki/lint/2026-11-20-sweep-rescan.md` §Iterazione 2 (wiki-lint scoped, Check 2): W8-W13 chiusi. Nuovi W17 (master-difetti-rilevati r.128) e W18 (llm-wiki-archivi-persistenza r.127): note di metodo del keeper negli Aggiornamenti v2026-11-21, senza citazione; WARNING di igiene, non affermazioni sul raw. Fix possibile: esenzione o wikilink nella riga.

## [2026-11-21] ingest | 2026-11-21-repo-llm_wiki-api-mcp + 2026-11-21-repo-llm_wiki-agente-runtime + 2026-11-21-repo-llm_wiki-agente-tools + 2026-11-21-repo-llm_wiki-fs-lib-progetto + 2026-11-21-repo-llm_wiki-ingest + 2026-11-21-repo-llm_wiki-ricerca-ui-residui
Pagine create: 7 | Figure: 0 | Aggiornamenti: 13 | Gap nuovi: 14 | Gap chiusi: 12
Ora: 07:31 | parallel_workers: 6 | Files touched: 23 (7 create, 13 aggiornate, gaps.md, index.md, log.md)
Create: 6 source page (fette A, B1, B2, C1, C2, E del 2026-11-21) e il concept [[llm-wiki-pipeline-ingest]]. Aggiornate: llm-wiki-api-locale, llm-wiki-mcp-server, llm-wiki-sicurezza, llm-wiki-agente, llm-wiki-archivi-persistenza, llm-wiki-schema-dati, llm-wiki-operazioni-distruttive, llm-wiki-rischi-persistenza, llm-wiki-cancellazione-pagine-e-sorgenti, llm-wiki-versioni-e-migrazioni, llm-wiki-test-e-ci, llm-wiki-app e la source page 2026-11-20-repo-llm_wiki-persistenza-a (nota sul ramo).
Slug collisions risolte: 7, tutte concept o entity compatibili, fuse (sicurezza 5 worker; archivi-persistenza 4; rischi-persistenza 4; schema-dati 3; agente 2; cancellazione-pagine-e-sorgenti 2; llm-wiki-app 2). Claim ripetuti tra worker deduplicati (sanitize_session_id e id chat in 3 worker, approvazione shell in 2).
Contraddizioni: 13 segnalate dai worker, tutte applicate: 12 in `## Contradictions` (api-locale 2, sicurezza 2, mcp-server 1, agente 2, archivi-persistenza 2, schema-dati 1, llm-wiki-app 2) e 1 come nota sul ramo (develop contro HEAD detached, stesso commit `e08cfce`: artefatto del checkout del submodule, registrata anche in sicurezza, agente e llm-wiki-app e nella source page persistenza-a, non come contraddizione di contenuto). Aggiunte dal keeper in fase di merge come voci superate: 14 (api-locale 1, archivi-persistenza 2, schema-dati 2, operazioni-distruttive 2, rischi-persistenza 3, cancellazione-pagine-e-sorgenti 2, test-e-ci 1, llm-wiki-app 1), più due note di superamento annidate sotto voci esistenti (api-locale, sicurezza); nessuna voce esistente cancellata o riscritta.
Ipotesi e deduzioni lasciate tali: catena di cancellazione (OPTIONS, delete: in review-view, delete_file non confinato) ipotesi non riprodotta; aggiramento con virgolette in shell_command_tokens ipotesi non testata; collisione di sanitize_session_id inferenza non testata; saturazione del rate limit da LAN inferenza non testata; token in chiaro in app-state.json e collisione di id dopo l'import deduzioni non testate.
Gap non aperti per deduplica o superamento: llm-wiki-sessione-id-ui-vs-agente (in id-chat-sessione), llm-wiki-cancellazione-chiamanti-ts (in cancellazione-controlli-confine), llm-wiki-import-chiamante-ui (in import-id-duplicato), llm-wiki-chiamanti-pulizia-ingest (in chiamanti-non-verificati), llm-wiki-embedding-lancedb-dimensioni (in embedding-cambio-modello), llm-wiki-sessioni-agente-cancellazione (in cancellazione-file-orfani), llm-wiki-impostazioni-persistenza-residua (in ui-salvataggio-impostazioni), llm-wiki-runtime-approvazione-shell (risolto dalla fetta runtime), llm-wiki-searxng-nomi-ts (nomi TS già in wiki), llm-wiki-chi-scrive-txt-parser (scrittore già documentato da persistenza-b), llm-wiki-cifratura-segreti (unito in llm-wiki-token-cifratura).
Validazione contratto `proposed_pages`: 6/6 JSON exit 0 con `tools/contratti/validate-contratto.py proposed_pages`, eseguita dalla sessione principale (non dal wiki-keeper, che non ha Bash).
Il Check 4bc su `tools/wiki/verify_gap_closures.py --check` e `tools/wiki/gaps_append_guard.py` non sono stati eseguiti dal wiki-keeper: da lanciare dalla sessione principale.
[2026-11-21 07:31] gap-closed — llm-wiki-contratto-api-http via [[llm-wiki-api-locale]] — files touched: 1
[2026-11-21 07:31] gap-closed — llm-wiki-api-lan-auth via [[llm-wiki-sicurezza]] — files touched: 1
[2026-11-21 07:31] gap-closed — llm-wiki-mcp-readme-vs-codice via [[llm-wiki-mcp-server]] — files touched: 1
[2026-11-21 07:31] gap-closed — llm-wiki-approvazione-shell via [[llm-wiki-sicurezza]] — files touched: 1
[2026-11-21 07:31] gap-closed — llm-wiki-i18n-lingue via [[llm-wiki-app]] — files touched: 1
[2026-11-21 07:31] gap-closed — llm-wiki-multimodale-stato via [[llm-wiki-app]] — files touched: 1
[2026-11-21 07:31] gap-closed — llm-wiki-ci-test-build via [[llm-wiki-test-e-ci]] — files touched: 1
[2026-11-21 07:31] gap-closed — llm-wiki-creazione-cartella-dati via [[llm-wiki-schema-dati]] — files touched: 1
[2026-11-21 07:31] gap-closed — llm-wiki-log-index-formato via [[llm-wiki-schema-dati]] — files touched: 1
[2026-11-21 07:31] gap-closed — llm-wiki-embedding-trasporto via [[llm-wiki-sicurezza]] — files touched: 1
[2026-11-21 07:31] gap-closed — llm-wiki-tipi-dedup-lint via [[llm-wiki-schema-dati]] — files touched: 1
[2026-11-21 07:31] gap-closed — llm-wiki-markdown-estratto-percorsi via [[llm-wiki-archivi-persistenza]] — files touched: 1

## [2026-11-21] lint | check completo (prima esecuzione del giorno)
Orphan: 0 | Broken: 0 | Unsourced: 2 | Kanban: 0 err | Coerenza: 0 err
Totale: 0 ERROR, 18 WARNING, 10 INFO (heal-eligible: 0). Risolti W8-W13, W15 (riga `project.json`), I8; nuovi W19-W25. Report: `wiki/lint/2026-11-21-lint-report.md`.

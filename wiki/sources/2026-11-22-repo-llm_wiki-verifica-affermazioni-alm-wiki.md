---
id: 2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki
type: source
title: Specifiche estratte da llm_wiki, 2026-11-22: verifica sul codice delle affermazioni C di alm-wiki (repo-sync, e08cfce)
status: draft
created: 2026-11-22
updated: 2026-11-22
sources: ["raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md"]
tags: [source, repo, llm-wiki, api, verifica, diff-skill-app]
---

# Specifiche estratte da llm_wiki, 2026-11-22: verifica delle affermazioni C di alm-wiki
> **Linea e provenienza:** `code_repos/llm_wiki`, upstream v0.6.13, commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3`, ramo `develop` (coincide con `main`, identico alla personalizzazione al momento della lettura). Lettura diretta del codice da parte di `repo-sync`, in sola lettura, status `partial`: 17 file su 476, letture mirate a finestre. Nulla è stato eseguito. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Identita']

## Contesto
Il raw verifica sul codice le affermazioni di livello C («contratto letto nel codice») elencate in [[llm-wiki-api-affermazioni-codice-da-verificare]] (fonti di alm-wiki: [[2026-11-22-repo-alm-wiki-evidenze-api]] e [[2026-11-22-repo-alm-wiki-bozza-skill]]). Non confronta gli esiti con la wiki. Sono escluse le voci n. 20, 21 e 22 (senza riferimento al codice) e la soglia del 5% di n. 4 (inferenza). Per ogni affermazione dice cosa fa il codice, con righe di codice: la factory non le ha rilette. Ha lo stesso livello dei raw `repo-sync` di `llm_wiki` già ingeriti. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Come leggere gli esiti]

**Esiti:** CONFERMATA, SMENTITA, PARZIALE e NON CONCLUSIVA hanno il significato del raw: l'esito vale per il comportamento, e dove la riga citata dalla fonte non coincide la riga corretta è nella nota. Conteggio: 25 righe CONFERMATA nelle tabelle, una delle quali (`allowLanAccess`) è un rimando a n. 23, quindi 24 affermazioni distinte; 6 PARZIALI, 1 SMENTITA (lettura letterale), 1 NON CONCLUSIVA; più due contraddizioni aperte decise dal codice. Nessuna inferenza è promossa a fatto. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Come leggere gli esiti]

## Dettaglio

### Dove sono finiti i fatti
- Ricerca e grafo (n. 1-9): [[llm-wiki-ricerca-e-grafo-api]]. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: ricerca (`search.rs`)]
- Id progetto, `files/content`, `/health`, verbi, limiti, `resolve_project` (n. 10-15, 19, 25) e le due contraddizioni: [[llm-wiki-api-locale]] e [[llm-wiki-sincronizzazione-file]]. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: API (`api_server.rs`)]
- Rescan, scope del watcher e avvio dell'ingest (n. 16-18): [[llm-wiki-sincronizzazione-file]] e [[llm-wiki-pipeline-ingest]]. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: sincronizzazione file (Rust e UI)]
- Bind e CORS (n. 23, 24): [[llm-wiki-sicurezza]]. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: bind, CORS e sezione impostazioni]
- Cache di ingest: [[llm-wiki-pipeline-ingest]]. Id delle review, auto-save, pulizia automatica: [[llm-wiki-review-store-e-auto-save]]. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: cache di ingest e review]
- Stato delle differenze con la skill: [[llm-wiki-skill-vs-app-v0-6-13]] e [[llm-wiki-skill]].

### Le due contraddizioni
- **Id progetto «path esatto» (a):** il codice conferma la fonte. Normalizzazione di `\` e della `/` finale su ogni piattaforma; maiuscole ignorate solo con `cfg!(windows)`. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Contraddizione aperta (a): match del path del progetto su Windows (n. 10)]
- **Accodamento dell'ingest per progetto aperto o inattivo (b):** dipende da «Watch all projects». [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Contraddizione aperta (b): il rescan accoda l'ingest «a progetto attivo o inattivo» o «solo per il progetto aperto» (n. 16 e bozza)]

### La riga «Watch all projects spento, 60 s» della bozza
Nel raw la riga è una **sintesi ambigua** del raw della bozza ([[2026-11-22-repo-alm-wiki-bozza-skill]]): il testo originale non è nel raw, e il raw la classifica SMENTITA solo per lettura letterale, dicendo che con «acceso» sarebbe confermata. La verifica sul codice conferma il comportamento **«60 s solo con l'opzione accesa»**: l'intervallo di 60 s esiste solo in `startAllProjectFileSync`, chiamata solo se l'opzione è attiva; con l'opzione spenta c'è `stopAllProjectFileSync` e nessun timer. Non registro una smentita della bozza. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: sincronizzazione file (Rust e UI)]

### Righe della fonte sfasate
Il raw segnala che alcune righe citate dalle fonti di alm-wiki non coincidono con quelle del codice: n. 1 (684 è il punteggio dei vicini, la condizione è a 464-472), n. 2 (682 è lo snippet, la quota è a 541-553), n. 12 (956 è il 400 «Missing path», il 403 è a 958-960 e il 415 a 961-966), n. 15 (522-529 è `respond_error`, il 503 è a 112-114 e il 429 a 108-110), n. 25 (il confronto `current` è a 856). Le altre righe coincidono. L'esito vale per il comportamento, non per la riga. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Righe della fonte sfasate]

### Limiti e gap
Non letti: `handle_write_page`, `handle_chat`, `respond_chat_sse`; `enqueueInactiveProjectBatch` e un eventuale controllo LLM nel ramo inattivo; il chiamante di `sweepResolvedReviews` e `stable_review_id` in Rust; il nome del file di coda dell'ingest e il «progresso solo in UI» (NON CONCLUSIVA per questo raw); cosa passano i chiamanti come `sourceContent` alla cache. Condizioni a runtime non verificabili dal solo codice. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Gap evidenti]

## Pagine ricavate o aggiornate
Create: [[llm-wiki-ricerca-e-grafo-api]], [[llm-wiki-review-store-e-auto-save]]. Aggiornate (solo in accodamento): [[llm-wiki-api-affermazioni-codice-da-verificare]], [[llm-wiki-api-locale]], [[llm-wiki-sincronizzazione-file]], [[llm-wiki-pipeline-ingest]], [[llm-wiki-rischi-persistenza]], [[llm-wiki-sicurezza]], [[llm-wiki-skill-vs-app-v0-6-13]], [[llm-wiki-skill]], [[llm-wiki-skill-bozza-alm-wiki]], [[llm-wiki-api-osservazioni-esecuzione-v0-6-13]], [[2026-11-22-repo-alm-wiki-evidenze-api]], [[2026-11-22-repo-alm-wiki-bozza-skill]].

## Gap di questa fonte
- Chiuso: `llm-wiki-monitoraggio-piu-progetti`. Nuovo: `llm-wiki-watch-all-projects-residui`.
- Parziali, restano aperti: `llm-wiki-affermazioni-codice-da-verificare`, `llm-wiki-skill-punti-da-verificare`, `llm-wiki-api-corpi-handler-non-letti`, `llm-wiki-review-concorrenza-webview`, `llm-wiki-source-watch-default`; annotata l'inferenza in `llm-wiki-prove-in-esecuzione-aperte`.

## Pagine collegate
[[llm-wiki-api-affermazioni-codice-da-verificare]], [[2026-11-22-repo-alm-wiki-evidenze-api]], [[2026-11-22-repo-alm-wiki-bozza-skill]], [[llm-wiki-ricerca-e-grafo-api]], [[llm-wiki-review-store-e-auto-save]], [[gaps]]

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

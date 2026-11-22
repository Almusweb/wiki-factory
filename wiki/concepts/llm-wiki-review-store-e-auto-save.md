---
id: llm-wiki-review-store-e-auto-save
type: concept
title: llm-wiki — review, id, auto-save della UI e pulizia automatica (v0.6.13)
status: draft
created: 2026-11-22
updated: 2026-11-22
sources: ["raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md"]
tags: [llm-wiki, review, persistenza, concorrenza, api]
---

# llm-wiki — review, id, auto-save della UI e pulizia automatica (v0.6.13)
> Come la UI identifica e salva le review, come l'API le riscrive e come la pulizia automatica decide quali risolvere: letto nel codice a `e08cfce`, mai eseguito. La corsa fra API e auto-save **non è provata**.

## Contesto
**Linea e provenienza:** upstream v0.6.13, commit `e08cfce` (`develop` coincide con `main`). Lettura statica del `repo-sync` mirato ([[2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki]]). Le scritture API sulle review (non atomiche, senza lock) sono già in [[llm-wiki-api-locale]]; il rischio di sovrascrittura è registrato come deduzione in [[llm-wiki-rischi-persistenza]]. Questa pagina aggiunge il lato UI. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Come leggere gli esiti]

## Dettaglio

### Id delle review
`review-<8 cifre esadecimali>` da FNV-1a a 32 bit (base 0x811c9dc5, primo 0x01000193) calcolato su `tipo::titolo normalizzato`. L'id non dipende da `sourcePath`. Il raw non ha letto `stable_review_id` in Rust. **Deduzione, non testata:** due review dello stesso tipo e dello stesso titolo normalizzato, anche da sorgenti diverse, hanno lo stesso id; come lo store le tratti non è nel raw. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: cache di ingest e review] [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Gap evidenti]

### Auto-save della UI
Una sottoscrizione allo store riavvia a ogni cambiamento un `setTimeout` di 1000 ms; allo scadere scrive l'intero array in `.llm-wiki/review.json` (`JSON.stringify`). **Non c'è lettura né fusione col disco prima della scrittura.** Il salvataggio è sospeso durante il cambio progetto. Un commento di `review-view.tsx` dice che le scritture esterne restano invisibili finché non si ricarica. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: cache di ingest e review]

### Scritture dell'API sulle review
`PATCH`, `DELETE` e `resolve` delle review riscrivono `.llm-wiki/review.json` del progetto indicato (lettura, modifica, `fs::write`). Tutte le rotte con `{id}` passano da `resolve_project`, che accetta qualunque id o percorso e **non verifica `current`**: le scritture sulle review valgono quindi per qualunque progetto indicato, non solo per quello aperto. `rescan` ed `embed` risolvono il progetto allo stesso modo. Il raw ha letto `resolve_project` in review, rescan ed embed; `handle_write_page` e `handle_chat` non sono letti, quindi il fatto non è esteso a loro. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: API (`api_server.rs`)]

### Cosa ne segue, e cosa no
- **Letto nel codice:** l'auto-save scrive l'array intero dallo stato della UI senza fusione; l'API riscrive il file senza passare dallo stato della UI e senza emettere eventi nei corpi letti (vedi [[llm-wiki-api-locale]]).
- **Deduzione dalla lettura, non provata:** una modifica fatta via API mentre il progetto è aperto potrebbe essere sovrascritta dal primo salvataggio successivo a un cambiamento dello stato della UI, finché la UI non ricarica il file.
- **Non provato:** la corsa reale. Non esiste una prova di concorrenza; i task della fonte che la citano non sono stati letti dalla factory. Gap `llm-wiki-review-concorrenza-webview` e `llm-wiki-prove-in-esecuzione-aperte` in [[gaps]]. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: cache di ingest e review] [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Gap evidenti]

### Pulizia automatica delle review (`sweepResolvedReviews`)
Lavora sul progetto aperto; secondo il commento parte alla fine dell'ingest (il chiamante non è letto nel raw; la coda che la lancia a coda svuotata è in [[llm-wiki-pipeline-ingest]]).
- **Fase 1, regole:** `missing-page` se la pagina esiste per id (stem in minuscolo) o per titolo; `duplicate` se manca una pagina interessata.
- **Fase 2, giudizio LLM:** a lotti da 40, massimo 5 lotti, con arresto al primo lotto senza risolti; le azioni registrate sono `auto-resolved` e `llm-judged`.
- **Nessun filtro per tipo nella fase 2:** la prudenza su contraddizioni, suggerimenti e conferme sta solo nel testo del prompt, non in un controllo del codice. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: cache di ingest e review]

## Limiti
Lettura statica. Non letti: `stable_review_id` in Rust, il chiamante di `sweepResolvedReviews`, `handle_write_page` e `handle_chat`. Condizioni a runtime (progetto aperto, impostazioni dell'utente) non verificabili dal solo codice. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Gap evidenti]

## Pagine collegate
[[llm-wiki-api-locale]], [[llm-wiki-rischi-persistenza]], [[llm-wiki-pipeline-ingest]], [[llm-wiki-sicurezza]], [[2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki]]. Gap: [[gaps]] (`llm-wiki-review-concorrenza-webview`, `llm-wiki-prove-in-esecuzione-aperte`).

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->
Epica LWS-EP-001 — Allineare la skill llm-wiki all'app llm_wiki v0.6.13 (fase A, PR generica upstream)
- LWS-US-007 — Scritture, chat e rescan

---
id: 2026-11-21-repo-llm_wiki-ricerca-ui-residui
type: source
title: Specifiche estratte da code_repos/llm_wiki, estrazione 2026-11-21 fetta E: ricerca, vettori, UI, residui (repo-sync)
status: draft
created: 2026-11-21
updated: 2026-11-21
sources: ["raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md"]
tags: [source, repo, llm-wiki, ricerca, embedding, ui, ci]
---

# Specifiche estratte da code_repos/llm_wiki, estrazione 2026-11-21 fetta E: ricerca, vettori, UI, residui (repo-sync)
> Estrazione mirata `repo-sync` del 2026-11-21 sul commit `e08cfce`: trasporto e ciclo di vita dell'embedding, lingue dell'interfaccia, workflow CI e build, salvataggio delle impostazioni, campi segreti, identificatori, cancellazione di revisioni e sessioni. Completa [[2026-11-20-repo-llm_wiki]].

## Contesto
Sesta fetta del giro del 2026-11-21. È un'estrazione read-only del repository `llm_wiki` al commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` (HEAD detached; le source page del 2026-11-20 dicono `develop`, stesso commit: artefatto del checkout del submodule). [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Specifiche estratte: llm_wiki (ricerca, vettori, UI, residui)]

## Dettaglio

### Metadati dell'estrazione
- Esiti dichiarati sui gap: `i18n-lingue`, `ci-test-build` ed `embedding-trasporto` chiusi; `embedding-cambio-modello`, `ui-salvataggio-impostazioni`, `scan-credenziali`, `riferimenti-incrociati` e `chiamanti-non-verificati` parziali; `cancellazione-file-orfani` chiuso per i vettori, non chiuso per le sessioni agente. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Ambito e copertura]
- Non letti: `search.rs` righe 1-1129, i JSON delle lingue, `.github/scripts/*`, `lint-view.tsx` oltre la riga 340, `LlmProviderSection`, `WebSearchSection` e `src/lib/embedding.ts`. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Ambito e copertura]

### Contenuto
- CI (`ci.yml`) e build (`build.yml`), secret referenziati per nome: [[llm-wiki-test-e-ci]]. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §CI e build (gap ci-test-build)]
- Lingue dell'interfaccia (en, it, zh, ru) e divergenza con la README: [[llm-wiki-app]]. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Lingue dell'interfaccia (gap i18n-lingue)]
- Trasporto della chiave di embedding e campi segreti nei tipi di configurazione: [[llm-wiki-sicurezza]]. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Trasporto dell'embedding (gap embedding-trasporto)]
- Ciclo di vita dei vettori e cambio di modello (nessun controllo di dimensione nella scrittura): [[llm-wiki-rischi-persistenza]]. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Ciclo di vita dei vettori e cambio modello (gap embedding-cambio-modello)]
- File `.revision` e file di sessione agente dopo una cancellazione: [[llm-wiki-cancellazione-pagine-e-sorgenti]]. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Cancellazione di revisioni e sessioni (gap cancellazione-file-orfani)]
- Salvataggio delle impostazioni, identificatori, `lint-config.json` e chiamanti dei comandi vector: [[llm-wiki-archivi-persistenza]]. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Salvataggio delle impostazioni (gap ui-salvataggio-impostazioni)]

### Limiti e gap
Restano non verificati: comportamento di LanceDB su dimensioni diverse, chiamanti dei comandi e delle funzioni elencate, cancellazione delle sessioni agente da parte di altro codice, credenziali fuori dai file letti, salvataggio di `providerConfigs` e `searchApiConfig`. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Ambito e copertura]

## Pagine ricavate o aggiornate
Aggiornate: [[llm-wiki-test-e-ci]], [[llm-wiki-app]], [[llm-wiki-sicurezza]], [[llm-wiki-rischi-persistenza]], [[llm-wiki-cancellazione-pagine-e-sorgenti]], [[llm-wiki-archivi-persistenza]], [[llm-wiki-versioni-e-migrazioni]].

## Gap di questa fetta
- Chiusi: `llm-wiki-i18n-lingue`, `llm-wiki-ci-test-build`, `llm-wiki-embedding-trasporto`.
- Parziali: `llm-wiki-embedding-cambio-modello`, `llm-wiki-ui-salvataggio-impostazioni`, `llm-wiki-cancellazione-file-orfani`, `llm-wiki-scan-credenziali`, `llm-wiki-riferimenti-incrociati`, `llm-wiki-chiamanti-non-verificati`, `llm-wiki-id-chat-sessione`, `llm-wiki-vector-v1-chiamanti`, `llm-wiki-cancellazione-controlli-confine`.
- Aperti: `llm-wiki-test-fuori-workflow`, `llm-wiki-token-cifratura` (unito alla proposta della fetta [[2026-11-21-repo-llm_wiki-fs-lib-progetto]]).
- Non aperti perché già coperti da gap esistenti ancora aperti: `llm-wiki-embedding-lancedb-dimensioni` (in `llm-wiki-embedding-cambio-modello`), `llm-wiki-sessioni-agente-cancellazione` (in `llm-wiki-cancellazione-file-orfani`), `llm-wiki-impostazioni-persistenza-residua` (in `llm-wiki-ui-salvataggio-impostazioni`).

Dettagli in [[gaps]]. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Ambito e copertura]

## Estratto non promosso a pagina
Nessun contenuto del raw è stato scartato. Il testo del raw non è stato modificato.

## Pagine collegate
[[2026-11-20-repo-llm_wiki]], [[llm-wiki-app]], [[llm-wiki-test-e-ci]], [[llm-wiki-sicurezza]], [[llm-wiki-rischi-persistenza]], [[llm-wiki-archivi-persistenza]], [[llm-wiki-cancellazione-pagine-e-sorgenti]], [[llm-wiki-operazioni-distruttive]], [[llm-wiki-schema-dati]], [[llm-wiki-versioni-e-migrazioni]], [[gaps]]

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

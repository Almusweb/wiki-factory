---
id: factory-decisioni-di-configurazione
type: concept
title: wiki-factory — decisioni di configurazione della sessione 2026-11-20
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: ["raw/sessions/session-2026-11-20-16-3649aa67.md"]
tags: [factory, configurazione, sessione, decisioni]
---

# wiki-factory — decisioni di configurazione della sessione 2026-11-20
> Le dieci decisioni prese nella sessione di bootstrap della factory `wiki-factory` (PATTERN 2.48), con la fonte che il documento di sessione dichiara per ciascuna.

## Contesto
La sessione ha fatto il bootstrap della factory dal clone del master, con il repository di codice `llm_wiki` collegato come submodule su `develop`. Questa pagina riguarda la **factory**, non l'applicazione `llm_wiki`; per l'applicazione vedi [[llm-wiki-app]]. Le decisioni sono riportate come scritte nel documento di sessione, con la fonte tra parentesi quadre dichiarata dal raw. Il quadro della sessione è in [[session-2026-11-20-16-3649aa67]]. [^src: raw/sessions/session-2026-11-20-16-3649aa67.md §Decisioni prese]

## Dettaglio

### Origine e generazione della factory
1. **Allineamento del master.** Il master è stato allineato a origin/main v2.48.0-36 con `pull --ff-only`, dopo conferma dell'utente. Fonte dichiarata: conversazione; `git describe` = v2.48.0-36-ge3b2762f. [^src: raw/sessions/session-2026-11-20-16-3649aa67.md §Decisioni prese]
2. **Destinazione e installer.** Destinazione: repository esistente `wiki-factory`. Generazione con l'installer deterministico `installers/v2.45/install.py --topology custom --force`: il README vuoto è stato sovrascritto, recuperabile da `init`. Fonte dichiarata: commit dbf61ce. [^src: raw/sessions/session-2026-11-20-16-3649aa67.md §Decisioni prese]
3. **Submodule.** `llm_wiki` è collegato come submodule `code_repos/llm_wiki`, con `develop` come branch di riferimento. Fonte dichiarata: commit 7a77391 e `.gitmodules`. [^src: raw/sessions/session-2026-11-20-16-3649aa67.md §Decisioni prese]

### Politica sul repository di codice
4. **`llm_wiki` come repository di cliente.** Per dichiarazione dell'utente: `ai_attribution_policy.suppress_ai_traces: true` e `ai_policy_check` con scope `code_repos/llm_wiki`. Nel repository della factory l'attribuzione AI resta ammessa. Fonte dichiarata: conversazione; commit dbf61ce. [^src: raw/sessions/session-2026-11-20-16-3649aa67.md §Decisioni prese]
5. **Prima estrazione scartata.** La prima estrazione, eseguita da un sub-agente generico perché l'agente `repo-sync` non era ancora registrato nella sessione, è stata scartata e spostata in un backup fuori dal repository (22 file). È stata rifatta con l'agente `repo-sync` registrato. Fonte dichiarata: conversazione. [^src: raw/sessions/session-2026-11-20-16-3649aa67.md §Decisioni prese]

### Opt-in e routing
6. **Opt-in attivate.** `branch_awareness` sulla entry `llm_wiki`; `vcs_tooling.submodule_doctor` e `submodule_hooks`; `secrets_guard` (`required_from` 2026-11-20); `repo_align`; `session_start` e `session_close`; `wiki_search` (backend auto, quindi fts5); `code_intelligence` solo L1 ctags; `code_quality.trigger_default`. Inoltre: `commit_coupling` float, eccezioni `ingest_agent_tools` per figma-sync, graphify-sync e session-sync, `schema_local_keys: [ai_attribution_policy]`. Fonte dichiarata: commit d25a098. [^src: raw/sessions/session-2026-11-20-16-3649aa67.md §Decisioni prese]
7. **Layer db agentico.** `routing.db: agent`, dove db è il layer di persistenza (LanceDB incorporato, file JSON in `.llm-wiki/`, store `app-state.json`). Poi `routing.docs: agent` e layer `[fe, be, db, qa, docs]` sulla entry `llm_wiki`. Fonte dichiarata: conversazione; `factory.config.yaml` non ancora committato alla chiusura della sessione. I dati di persistenza sono in [[llm-wiki-archivi-persistenza]]. [^src: raw/sessions/session-2026-11-20-16-3649aa67.md §Decisioni prese]

### Qualità del codice (CQRL)
8. **Regole CQRL.** Copiata la regola canonical del master `design-complexity.md`; 12 regole team-specific per typescript.react e rust.tauri sono state scritte in bozza in `code_quality/rules/proposte/`, cartella non letta dal reviewer, in attesa della revisione dell'utente. Fonte dichiarata: conversazione; file non ancora committati alla chiusura della sessione. Il testo delle 12 regole non è nel documento di sessione. [^src: raw/sessions/session-2026-11-20-16-3649aa67.md §Decisioni prese]

### Controlli e tracciamento
9. **WARNING sul frontmatter di `wiki/gaps.md`.** Trattato come falso positivo: il `gaps.md` del master ha lo stesso frontmatter. Fonte dichiarata: conversazione. Vedi il difetto 5 in [[master-difetti-rilevati]]. [^src: raw/sessions/session-2026-11-20-16-3649aa67.md §Decisioni prese]
10. **Difetti del master.** Vanno tracciati nel kanban della factory, con il product-manager e il tpm. Fonte dichiarata: conversazione. Elenco in [[master-difetti-rilevati]]. [^src: raw/sessions/session-2026-11-20-16-3649aa67.md §Decisioni prese]

### Artefatti collegati
Gli artefatti toccati dalla sessione sono nella tabella di [[session-2026-11-20-16-3649aa67]]. Il documento di sessione non indica task del kanban avanzati: il kanban era vuoto. [^src: raw/sessions/session-2026-11-20-16-3649aa67.md §Task avanzati]

## Pagine collegate
[[session-2026-11-20-16-3649aa67]], [[master-difetti-rilevati]], [[llm-wiki-archivi-persistenza]].

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

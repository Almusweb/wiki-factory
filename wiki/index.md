---
id: index
type: index
title: Wiki Index
status: draft
created: 2026-11-20
updated: 2026-11-21
sources: []
tags: [navigation]
---

# Wiki Index

Indice delle pagine di `wiki/`, aggiornato da `wiki-keeper` a ogni ingest.

## Sources
- [[2026-11-20-repo-llm_wiki]] — specifiche estratte da `code_repos/llm_wiki` (`repo-sync`, estrazione partial; seconda estrazione sulla persistenza)
- [[2026-11-20-repo-llm_wiki-persistenza-a]] — fetta A della persistenza: store `app-state.json`, cartella dati, tipi delle configurazioni, lettori backend
- [[2026-11-20-repo-llm_wiki-persistenza-b]] — fetta B della persistenza: scritture e atomicità, sincronizzazione file, log e indice
- [[2026-11-20-repo-llm_wiki-persistenza-c]] — fetta C della persistenza: chiamanti delle operazioni distruttive, cancellazioni, `append_turn`, v1
- [[2026-11-21-repo-llm_wiki-api-mcp]] — estrazione 2026-11-21 fetta A: `api_server.rs` per intero, API HTTP locale, MCP, bind e autenticazione
- [[2026-11-21-repo-llm_wiki-agente-runtime]] — estrazione 2026-11-21 fetta B1: `agent/runtime.rs`, approvazione shell, sessioni e id
- [[2026-11-21-repo-llm_wiki-agente-tools]] — estrazione 2026-11-21 fetta B2: registry dei tool, `shell.exec`, serde delle config, `write_wiki_page_verified`
- [[2026-11-21-repo-llm_wiki-fs-lib-progetto]] — estrazione 2026-11-21 fetta C1: comandi FS, `lib.rs`, layout del progetto, identità e import
- [[2026-11-21-repo-llm_wiki-ingest]] — estrazione 2026-11-21 fetta C2: pipeline di ingest, coda, cache, formati, cancellazione lato TypeScript
- [[2026-11-21-repo-llm_wiki-ricerca-ui-residui]] — estrazione 2026-11-21 fetta E: embedding, i18n, CI e build, impostazioni, id, revisioni e sessioni
- [[2026-11-21-repo-llm_wiki-persistenza-d]] — estrazione 2026-11-21 fetta D: percorso e file corrotto di `app-state.json` per sistema operativo, atomicità dei sette archivi senza riga di codice
- [[2026-11-21-repo-llm_wiki-dossier-ep004-r1]] — dossier EP-004 r1 (2026-11-21): rischio 1, percorso cancella-salva-carica delle chat, esito non conclusivo per lettura
- [[2026-11-21-repo-llm_wiki-dossier-ep004-r2]] — dossier EP-004 r2 (2026-11-21): rischio 2, rigenerazione dell'identità del progetto, esito confermato per lettura
- [[2026-11-21-repo-llm_wiki-dossier-ep004-r3]] — dossier EP-004 r3 (2026-11-21): rischio 3, scritture sul registro dei progetti, esito confermato per lettura sul meccanismo e non conclusivo sulla concorrenza reale
- [[session-2026-11-20-16-3649aa67]] — sessione di bootstrap `wiki-factory` 2.48 su `llm_wiki` (in `wiki/sessions/`; indice delle sessioni: [sessions/index.md](sessions/index.md))

## Entities
- [[llm-wiki-app]] — l'applicazione desktop `llm-wiki`: identità, funzioni dichiarate in README
- [[llm-wiki-mcp-server]] — server MCP: 12 strumenti registrati, limiti di `llm_wiki_write_page`

## Concepts

### Applicazione llm-wiki
- [[pattern-llm-wiki]] — il pattern LLM Wiki come lo dichiara la README
- [[llm-wiki-struttura-e-moduli]] — layout, entrypoint e moduli
- [[llm-wiki-stack-e-dipendenze]] — i tre descriptor, dipendenze, toolchain
- [[llm-wiki-api-locale]] — API HTTP locale, clip server, comandi Tauri
- [[llm-wiki-agente]] — modulo agente, permessi e router
- [[llm-wiki-sicurezza]] — bind, CORS, estensione Chrome, Tauri, segreti nello store
- [[llm-wiki-schema-dati]] — dati su file, tipi condivisi, schemi LanceDB
- [[llm-wiki-archivi-persistenza]] — i 17 archivi di `.llm-wiki/` e le chiavi di `app-state.json`
- [[llm-wiki-versioni-e-migrazioni]] — versioni di formato e migrazioni
- [[llm-wiki-operazioni-distruttive]] — operazioni distruttive, innesco e salvaguardie
- [[llm-wiki-gestione-file-corrotti]] — comportamento sui file corrotti
- [[llm-wiki-sincronizzazione-file]] — watcher di progetto, snapshot e coda dei cambi file
- [[llm-wiki-cancellazione-pagine-e-sorgenti]] — cascata di cancellazione di una pagina e ciclo di vita delle sorgenti
- [[llm-wiki-pipeline-ingest]] — pipeline di ingest (due stadi), coda, cache e guardie di percorso
- [[llm-wiki-rischi-persistenza]] — divergenze e rischi del layer di persistenza (deduzioni; esito del rischio 1 da US-025: non conclusivo per lettura)
- [[llm-wiki-licenza-e-standard]] — GPL v3 di terzi, anomalia MIT del server MCP
- [[llm-wiki-test-e-ci]] — test e CI

### Factory (meta-framework, non riguarda l'applicazione)
- [[factory-decisioni-di-configurazione]] — le dieci decisioni di configurazione della sessione 2026-11-20
- [[master-difetti-rilevati]] — undici difetti del master con evidenza e stato di verifica

## Meta
- [[gaps]] — informazioni che servono e la wiki non ha

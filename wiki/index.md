---
id: index
type: index
title: Wiki Index
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: []
tags: [navigation]
---

# Wiki Index

Indice delle pagine di `wiki/`, aggiornato da `wiki-keeper` a ogni ingest.

## Sources
- [[2026-11-20-repo-llm_wiki]] — specifiche estratte da `code_repos/llm_wiki` (`repo-sync`, estrazione partial; seconda estrazione sulla persistenza)
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
- [[llm-wiki-rischi-persistenza]] — divergenze e rischi del layer di persistenza (deduzioni)
- [[llm-wiki-licenza-e-standard]] — GPL v3 di terzi, anomalia MIT del server MCP
- [[llm-wiki-test-e-ci]] — test e CI

### Factory (meta-framework, non riguarda l'applicazione)
- [[factory-decisioni-di-configurazione]] — le dieci decisioni di configurazione della sessione 2026-11-20
- [[master-difetti-rilevati]] — undici difetti del master con evidenza e stato di verifica

## Meta
- [[gaps]] — informazioni che servono e la wiki non ha

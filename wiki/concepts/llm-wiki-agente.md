---
id: llm-wiki-agente
type: concept
title: llm-wiki — agente, permessi e router
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: ["raw/2026-11-20-repo-llm_wiki.md"]
tags: [llm-wiki, agente, permessi]
---

# llm-wiki — agente, permessi e router
> Il modulo Rust `agent` è il substrato condiviso da UI desktop, API HTTP locale e MCP; il raw ha letto per intero solo i file dei permessi e del router, non il runtime né gli strumenti.

## Contesto
Il modulo `agent` è dichiarato, nel suo commento, come substrato condiviso tra UI desktop, API HTTP locale e MCP, per evitare che i tre comportamenti divergano. Comprende i sotto-moduli cancel, context, events, permissions, provider, router, runtime, session, skills, tools, types e workspace. [^src: raw/2026-11-20-repo-llm_wiki.md §Entrypoint e moduli chiave]

## Dettaglio

### Permessi (`src-tauri/src/agent/permissions.rs`, letto per intero)
- 9 capability: `ReadProject`, `ReadSource`, `SearchWiki`, `SearchWeb`, `SearchAnyTxt`, `WriteWiki`, `RunDeepResearch`, `Network`, `Process`. [^src: raw/2026-11-20-repo-llm_wiki.md §Superficie di sicurezza]
- La policy `api_default` ne consente 8 (tutte tranne `RunDeepResearch`), incluse scrittura wiki, rete e `Process`. [^src: raw/2026-11-20-repo-llm_wiki.md §Superficie di sicurezza]
- Il commento nel file dice che `Process` resta inerte finché la richiesta non porta un comando shell esatto approvato separatamente, e che quell'elenco non va popolato con output del modello o dati di conversazione persistiti. [^src: raw/2026-11-20-repo-llm_wiki.md §Superficie di sicurezza]
- Il file implementa solo il gate sulle capability: il controllo del comando approvato non è in questo file. Il raw non verifica dove venga applicata l'approvazione dei comandi shell (la README dice: «external shell commands still require explicit approval»). [^src: raw/2026-11-20-repo-llm_wiki.md §Superficie di sicurezza]

### Router (`src-tauri/src/agent/router.rs`, letto per intero)
- 7 intenti: `NeedsInternalSearch`, `NeedsExternalSearch`, `NeedsRawSourceSearch`, `NeedsGraph`, `NeedsWrite`, `SimpleConversational`, `Ambiguous`. [^src: raw/2026-11-20-repo-llm_wiki.md §Superficie di sicurezza]
- `route_query` riceve messaggio, modalità e opzioni degli strumenti e restituisce una `RouterDecision` (intento, hint web e anytxt, inclusione delle sorgenti, motivazione testuale). [^src: raw/2026-11-20-repo-llm_wiki.md §Superficie di sicurezza]
- La classificazione è per parole chiave in inglese e cinese, con priorità: scrittura, grafo, sorgenti raw, web, conversazionale, altrimenti ambiguo. Il confronto è per sottostringa, non per parola intera. [^src: raw/2026-11-20-repo-llm_wiki.md §Superficie di sicurezza]
- Il router non attiva mai la ricerca wiki da solo (`should_search_wiki` è sempre falso): la scelta degli strumenti spetta al planner del modello. `NeedsInternalSearch` non è prodotto da `route_query`. [^src: raw/2026-11-20-repo-llm_wiki.md §Superficie di sicurezza]

### Non letto
Il raw non ha aperto `agent/runtime.rs` (225 KB) né `agent/tools.rs` (139 KB), descritti solo tramite nomi e file vicini. [^src: raw/2026-11-20-repo-llm_wiki.md §Entrypoint e moduli chiave]

## Pagine collegate
Gap aperti: [[gaps]] (`llm-wiki-approvazione-shell`, `llm-wiki-codice-non-letto`).

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

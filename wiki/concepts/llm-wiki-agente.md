---
id: llm-wiki-agente
type: concept
title: llm-wiki — agente, permessi e router
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: ["raw/2026-11-20-repo-llm_wiki.md", "raw/2026-11-20-repo-llm_wiki-persistenza-a.md", "raw/2026-11-20-repo-llm_wiki-persistenza-c.md"]
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

## Aggiornamenti (v2026-11-20)
Dalle fette A e C delle estrazioni mirate sulla persistenza ([[2026-11-20-repo-llm_wiki-persistenza-a]], [[2026-11-20-repo-llm_wiki-persistenza-c]]). Il testo sopra non è modificato; `agent/runtime.rs` e `agent/tools.rs` restano non letti. I gap `llm-wiki-approvazione-shell` e `llm-wiki-id-chat-sessione` restano aperti. Qualificatori come nel raw.

### Configurazione letta dal runtime
- Il Rust legge da `app-state.json` `projectRegistry` e `recentProjects` (elenco progetti) e `embeddingConfig`, `llmConfig`, `searchApiConfig` e `searchApiConfig.anyTxt` (configurazione del runtime dell'agente) a ogni avvio di turno agente, con due funzioni e senza cache (`lib.rs`). Su store illeggibile l'agente usa la configurazione di default e nessun progetto dal registro (comportamento in [[llm-wiki-gestione-file-corrotti]]). [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Lettori backend di `apiConfig` e `proxyConfig`]
- `load_agent_runtime_config` è definita due volte (`lib.rs` e `api_server.rs`): la copia in `api_server.rs` usa la cache di 5 secondi, quella in `lib.rs` no; per graphify il nome è ambiguo. La compatibilità serde tra `llmConfig` dello store e `agent::provider::LlmConfig` non è verificata (`provider.rs` non letto). Vedi [[llm-wiki-api-locale]]. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Punto 4: lettori di `app-state.json` in `api_server.rs`]

### Sessioni agente: chi le scrive
- `append_turn` ha tre chiamanti di produzione: `lib.rs:128` (variante sincrona: `result?` poi accodamento), `lib.rs:235` (variante in streaming: task in background con sink di eventi, accodamento solo nel ramo di successo) e `api_server.rs:2076`. L'associazione con `agent_start_turn` e `agent_start_turn_stream` (registrati a `lib.rs:665-666`) è una deduzione dalla forma, perché il nome della funzione contenitore non è nelle finestre. `agent/runtime.rs` non è un chiamante: la ricerca testuale su `append_turn(` trova solo `session.rs` e questi tre punti. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §`append_turn`: chiamanti e identificativo di sessione]
- Tutti e tre passano `response.session_id` (l'id restituito nella risposta del runtime) con `project.id` e `project.path`, senza trasformazioni visibili; l'accodamento avviene solo con il flag `persist_session` e i turni in errore non sono accodati. L'origine di `session_id` e `active_session_id` (client o backend) non è verificata; la sanitizzazione non sta nei chiamanti e, per la prima estrazione, avviene nello store (`session.rs`), con regola non documentata. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §`append_turn`: chiamanti e identificativo di sessione]

### Non letto, precisazioni
`agent/runtime.rs` resta non letto, ma non è il chiamante di `append_turn`. Non è stata cercata la cancellazione dei file `agent-sessions/` e non è letta `write_wiki_page_verified` (`agent/tools.rs`, usata da `POST pages/write`). [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Gap evidenti]

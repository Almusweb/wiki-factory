---
id: llm-wiki-agente
type: concept
title: llm-wiki — agente, permessi e router
status: draft
created: 2026-11-20
updated: 2026-11-21
sources: ["raw/2026-11-20-repo-llm_wiki.md", "raw/2026-11-20-repo-llm_wiki-persistenza-a.md", "raw/2026-11-20-repo-llm_wiki-persistenza-c.md", "raw/2026-11-21-repo-llm_wiki-agente-runtime.md", "raw/2026-11-21-repo-llm_wiki-agente-tools.md"]
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

## Aggiornamenti (v2026-11-21)
Dalle fette B1 e B2 del giro del 2026-11-21 ([[2026-11-21-repo-llm_wiki-agente-runtime]], [[2026-11-21-repo-llm_wiki-agente-tools]], commit `e08cfce`): letti `agent/runtime.rs` (righe 1-4031, test esclusi), `agent/session.rs`, `agent/permissions.rs` e `agent/types.rs`, `agent/router.rs` per intero, `agent/tools.rs` per intero (1-3889) e `agent/provider.rs` righe 1-260 di circa 600. Il testo sopra non è modificato; dove è superato lo dice `## Contradictions` in coda. Il gap `llm-wiki-approvazione-shell` è chiuso in [[gaps]]; `llm-wiki-requisiti-funzionali` e `llm-wiki-codice-non-letto` restano aperti in parte. Le inferenze marcate «non testata» restano tali; l'approvazione shell è in [[llm-wiki-sicurezza]], le sessioni in [[llm-wiki-archivi-persistenza]].

### Ciclo di una richiesta (runtime)
- `run_once_with_cancel_and_events` determina il `session_id`: quello della richiesta se non vuoto, altrimenti `api_<uuid v4>`; applica `PermissionPolicy::api_default()`. [^src: raw/2026-11-21-repo-llm_wiki-agente-runtime.md §Ciclo di una richiesta]
- Esistono due percorsi: l'agent loop (`run_agent_loop`) se la configurazione LLM è utilizzabile dal backend HTTP, altrimenti il percorso legacy (planner con modello, poi retrieval deterministico). Senza generatore LLM il legacy restituisce solo retrieval, o errore se non ci sono riferimenti e `allow_empty_retrieval` è falso. [^src: raw/2026-11-21-repo-llm_wiki-agente-runtime.md §Ciclo di una richiesta]
- Modalità: `fast`, `standard`, `deep`, `local_first`. Retrieval: `standard`, `smart`, `faithful`; in `faithful` solo `source.search` è permesso e overview e schema sono esclusi dal contesto. [^src: raw/2026-11-21-repo-llm_wiki-agente-runtime.md §Ciclo di una richiesta]
- Limiti applicati nel backend perché API e MCP aggirano la UI: risultati di ricerca 5 di default e 10 al massimo; immagini al massimo 5 per turno, 7 MiB di base64 ciascuna, tipi png, jpeg, webp, gif; iterazioni del loop 4/8/12 (8/16/20 con skill); budget di retrieval `faithful` 2/3/5, `smart` 3/4/6, `standard` 2/4/8 (+4 con skill esplicite); moduli `user.ask` al massimo 12 campi, 8 opzioni, 400 caratteri. [^src: raw/2026-11-21-repo-llm_wiki-agente-runtime.md §Ciclo di una richiesta]
- Tool nel loop: `wiki.search`, `wiki.read_page`, `wiki.write_page`, `source.search`, `graph.search`, `web.search`, `anytxt.search`, `skill.read_file`, `workspace.write_file`, `workspace.append_file`, `shell.exec`, `user.ask`; `deep_research.run` è rifiutato nel loop. Le scritture wiki sono create-only salvo `allowOverwrite` esplicito; gli output di shell sono troncati a 8.000 (stdout) e 4.000 (stderr) caratteri; le immagini sono inviate solo al primo giro. [^src: raw/2026-11-21-repo-llm_wiki-agente-runtime.md §Ciclo di una richiesta]
- `api_default` permette `ReadProject`, `ReadSource`, `SearchWiki`, `SearchWeb`, `SearchAnyTxt`, `WriteWiki`, `Network` e `Process`; `Process` è solo il controllo di capability, sempre soddisfatto, e non aggira l'approvazione, che avviene dopo come passo distinto. [^src: raw/2026-11-21-repo-llm_wiki-agente-runtime.md §Permessi e approvazione shell (gap 5)]
- Il runtime non apre prompt: decide se eseguire o restituire un esito «serve approvazione». Nel percorso legacy usa `is_shell_command_approved` sull'elenco `approved_shell_commands`; nel loop usa `is_shell_command_allowed_without_prompt` e, se negativo, restituisce l'osservazione `shell.exec.approval_required`, dopo la quale `run_agent_loop` chiude il turno con il testo «The Agent needs approval...». [^src: raw/2026-11-21-repo-llm_wiki-agente-runtime.md §Permessi e approvazione shell (gap 5)]
- Se si raggiunge il limite di iterazioni il turno termina con un messaggio esplicito che elenca i file generati. Requisiti funzionali dedotti dell'agente backend (gap 11, parte): retrieval su wiki, sorgenti, grafo, web e AnyTXT secondo i tool abilitati; scrittura di pagine wiki e file nel workspace; input strutturato con `user.ask`; annullamento del turno; skill di progetto in modalità automatica o esplicita; allegati di contesto espliciti fino a 8. [^src: raw/2026-11-21-repo-llm_wiki-agente-runtime.md §Requisiti funzionali dedotti (gap 11, parte)]

### Registry dei tool, provider e router (tools)
- Il registry (`BuiltinToolRegistry::execute`) esegue `wiki.write_page`, `wiki.search`, `wiki.read_page`, `source.search`, `graph.search`, `web.search`, `anytxt.search`, `deep_research.run`, `workspace.write_file`, `workspace.append_file` e `shell.exec`; ogni altro nome risponde «Unknown Agent tool». [^src: raw/2026-11-21-repo-llm_wiki-agente-tools.md §Registry dei tool]
- `builtin_tool_specs` dichiara anche `llm.generate`, `skills.load` e `skill.read_file`, che il registry non esegue (`skill.read_file` compare però tra i tool del loop nel raw del runtime: dove sia eseguito non è detto da nessuna fonte, è un punto da verificare); l'elenco è marcato `#[allow(dead_code)]` e il commento dice che serve a discovery API/MCP e a future chiamate native. [^src: raw/2026-11-21-repo-llm_wiki-agente-tools.md §Registry dei tool]
- `deep_research.run` restituisce solo lo status `orchestrated_by_agent_runtime`; `anytxt.search` usa JSON-RPC verso un servizio AnyTXT con endpoint di default `http://127.0.0.1:9920`. [^src: raw/2026-11-21-repo-llm_wiki-agente-tools.md §Registry dei tool]
- I provider LLM gestiti da `LlmClient::generate_text` sono `openai`, `azure`, `ollama`, `custom` (formato Anthropic se `apiMode` è `anthropic_messages`, altrimenti OpenAI-compatibile), `anthropic`, `minimax` (senza immagini) e `google`; altri nomi producono errore. Timeout richiesta 180 s, max tokens di default 2048. [^src: raw/2026-11-21-repo-llm_wiki-agente-tools.md §Provider LLM, provider web e router]
- I provider web sono `firecrawl`, `searxng`, `tavily`, `ollama`, `brave`, `bocha` e `serpapi`, con timeout 30 s e limite risultati 20 (50 per `bocha`). [^src: raw/2026-11-21-repo-llm_wiki-agente-tools.md §Provider LLM, provider web e router]
- `route_query` è un'euristica di sola etichettatura per parole chiave; `should_search_wiki` è sempre falso e la scelta dei tool spetta al planner del modello. [^src: raw/2026-11-21-repo-llm_wiki-agente-tools.md §Provider LLM, provider web e router]
- Il commento a `tools.rs:28-30` dice che i limiti I/O sono confini di sicurezza del backend validi anche per i chiamanti API e MCP, che non passano dai componenti React. [^src: raw/2026-11-21-repo-llm_wiki-agente-tools.md §Registry dei tool]
- Non letti: i test di `runtime.rs` (gap `llm-wiki-runtime-test-non-letti`) e `provider.rs` oltre la riga 260 (gap `llm-wiki-provider-rs-non-letto`). Il chiamante di `append_turn` resta quello già registrato (tre punti in `lib.rs` e `api_server.rs`, non `runtime.rs`); il raw runtime non ne trova uno in `runtime.rs`. [^src: raw/2026-11-21-repo-llm_wiki-agente-runtime.md §Gap evidenti]

## Contradictions
- **Runtime e tool «non letti»; regola di sanitizzazione «non documentata».** Prima (sezioni «Non letto» e «Non letto, precisazioni», Aggiornamenti v2026-11-20): `agent/runtime.rs` e `agent/tools.rs` non letti, `provider.rs` non letto, regola di sanitizzazione dell'id di sessione «non documentata». Ora: `runtime.rs` (righe 1-4031) e `session.rs` sono letti e la regola è documentata; `tools.rs` è letto per intero e `provider.rs` per le righe 1-260. Va inteso come «superato», non «assente»; restano non letti il blocco di test di `runtime.rs` e `provider.rs` oltre la riga 260. [^src: raw/2026-11-21-repo-llm_wiki-agente-runtime.md §Ambito e copertura] [^src: raw/2026-11-21-repo-llm_wiki-agente-tools.md §Metodo e limiti]
- **Dove è applicata l'approvazione dei comandi shell.** Prima (sezione Permessi): il raw non verifica dove venga applicata l'approvazione dei comandi shell. Ora (fetta runtime): è applicata in `runtime.rs` come passo distinto dopo il controllo di capability, nel percorso legacy e nell'agent loop. [^src: raw/2026-11-21-repo-llm_wiki-agente-runtime.md §Permessi e approvazione shell (gap 5)]
- **Ramo del checkout (nota, non contraddizione di contenuto).** Le source page del 2026-11-20 indicano `e08cfce` sul ramo `develop`, i raw del 2026-11-21 su HEAD detached: stesso commit, artefatto del checkout del submodule. [^src: raw/2026-11-21-repo-llm_wiki-agente-tools.md §Specifiche estratte: llm_wiki, agente tools e provider (fetta B2)]

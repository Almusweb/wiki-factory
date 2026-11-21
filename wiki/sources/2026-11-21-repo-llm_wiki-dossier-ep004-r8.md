---
id: 2026-11-21-repo-llm_wiki-dossier-ep004-r8
type: source
title: Dossier EP-004 r8 da code_repos/llm_wiki, 2026-11-21: rischio 8, segreti in chiaro nello store applicativo (repo-sync)
status: draft
created: 2026-11-21
updated: 2026-11-21
sources: ["raw/2026-11-21-repo-llm_wiki-dossier-ep004-r8.md"]
tags: [source, repo, llm-wiki, persistenza, sicurezza, segreti, ep-004, rischio-8]
---

# Dossier EP-004 r8 da code_repos/llm_wiki, 2026-11-21: rischio 8, segreti in chiaro nello store applicativo (repo-sync)
> Estrazione mirata `repo-sync` v2.12 del 2026-11-21 sul commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` (HEAD staccato, nessun ramo), stato `partial`, 28 file letti, sola lettura (Q_003). «Osservato» = letto nel codice (mai eseguito); «ereditato» = dalla fetta D o dalla wiki, non riletto; «deduzione non testata» = ricavata da fatti osservati. Repo di terzi sotto GNU GPL v3: solo nomi di file, simboli, righe, nomi di campo e di header; nessun frammento di codice e **nessun valore di segreto**.

## Contesto
Ottavo dossier della serie di EP-004 (TSK-026 / US-032), dedicato al rischio 8 di [[llm-wiki-rischi-persistenza]]; segue [[2026-11-21-repo-llm_wiki-dossier-ep004-r7]]. Non ripete il comportamento di `app-state.json` su file corrotto con possibile perdita di `apiConfig` e delle chiavi ([[2026-11-21-repo-llm_wiki-persistenza-d]]). Limite dichiarato in anticipo: protezione del file da parte del plugin dello store o del sistema operativo non osservabile per lettura. L'agente non aveva `Bash` né `Grep`: la ricerca testuale globale è della sessione principale (TSK-026 §Chiusura) ed è riportata a parte. Il gap `llm-wiki-scan-credenziali` (credenziali hardcoded) è fuori perimetro e non è toccato. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r8.md §Identità e perimetro]

## Dettaglio

### Campi sensibili, per nome (osservato)
Tutti sono chiavi dello store `app-state.json`; i valori iniziali sono stringhe vuote o assenti. Quindici voci, solo nomi:
- `llmConfig`: `apiKey`, `customHeaders`, `extraRequestBody` (corpo libero, **potenzialmente** sensibile).
- `providerConfigs[<preset>]`: `apiKey`, `customHeaders`, `extraRequestBody` (la chiave per preset sopravvive al cambio preset).
- `searchApiConfig`: `apiKey`; `searchApiConfig.providerConfigs[<provider>]`: `apiKey` (tavily, serpapi, brave, bocha, ollama, firecrawl).
- `embeddingConfig`: `apiKey`, `extraHeaders`.
- `multimodalConfig`: `apiKey` (usata se `useMainLlm` è falso).
- `mineruConfig`: `token`, `localToken`.
- `proxyConfig`: `url`, che può portare le credenziali del proxy incorporate; il commento dichiara che sono conservate alla lettera accanto alle altre chiavi, senza archivio dei segreti separato.
- `apiConfig`: `token` (accesso all'API locale e al Clip server dalla rete).

Non sono segreti ma incidono sulla sicurezza: `apiConfig.allowUnauthenticated`, `allowLanAccess`, `enabled`, `mcpEnabled`; `proxyConfig.acceptInvalidCerts`, `bypassLocal`. Campi URL che **potrebbero** contenere credenziali incorporate (deduzione non testata: tipo stringa libera): `llmConfig.customEndpoint`, `ollamaUrl`, `baseUrl` dei provider LLM e di ricerca, `searXngUrl`, `embeddingConfig.endpoint`, `multimodalConfig.customEndpoint`, `mineruConfig.localEndpoint` e `localServerUrl`; osservato per uno solo, MinerU locale, che **rifiuta** un endpoint con utente o password. Non sensibili per costruzione: il profilo per progetto (`projectLlmOverrides[*].profile`) esclude `apiKey` e `customHeaders` (restano `extraRequestBody`, `customEndpoint`, `ollamaUrl`); `taskModelRouting` e `customLlmPresets` conservano solo id ed etichette. Fuori dallo store: la variabile d'ambiente `LLM_WIKI_API_TOKEN` (prevale sul token dello store; unica fonte del client MCP) e le credenziali del proxy nell'ambiente del processo (`HTTP_PROXY`, `HTTPS_PROXY`). [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r8.md §1. Elenco dei campi sensibili (AC2)]

### Come sono conservati (osservato)
Tutte le funzioni di salvataggio scrivono l'oggetto così com'è con `store.set` (`project-store.ts`: `saveLlmConfig`, `saveProviderConfigs`, `saveSearchApiConfig`, `saveEmbeddingConfig`, `saveMultimodalConfig`, `saveMineruConfig`, `saveProxyConfig`, `saveApiConfig`): nessuna cifratura né offuscamento; `normalizeMineruConfig` fa solo `trim` su `localToken`. Il token API è generato con 32 byte casuali in base64url, che non è cifratura a riposo. Il plugin store è registrato senza opzioni (`lib.rs:558`); scrittura diretta con `fs::write` ereditata dalla fetta D. Quattro moduli Rust leggono il file con `serde_json` sul testo (`api_server.rs`, `lib.rs`, `proxy.rs`, `server_bind.rs`): il formato su disco è JSON leggibile senza chiavi di decifratura, e i lettori usano il valore alla lettera (deduzione forte, non testata: un valore cifrato li renderebbe non funzionanti). Nessun crate o pacchetto di keyring, stronghold o cifratura simmetrica nei manifest diretti; dipendenze transitive (`Cargo.lock`) non lette. Nello stato `zustand` della WebView i segreti sono in chiaro. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r8.md §2. Come sono conservati (AC3)]

### Permessi del file e protezione di libreria o sistema operativo: NON CONCLUSIVO
Percorso ereditato dalla fetta D (`<data_dir>/com.llmwiki.app/app-state.json`). Nel repo non compare alcuna scrittura di `app-state.json` da parte del Rust (solo letture), e nessuna riga letta imposta permessi o attributi; la scrittura è del plugin. Motivo del non conclusivo: maschera di creazione, ACL ereditate dal profilo, `umask` e sandbox del pacchetto dipendono dal sistema operativo e dal codice del plugin, non osservabili senza leggere il file system dell'utente. Deduzioni non testate: su Linux e macOS permessi predefiniti dell'account; su Windows ereditati dalla cartella del profilo, che i profili di dominio possono sincronizzare. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r8.md §3. Permessi del file e protezione di libreria/OS (AC7): NON CONCLUSIVO]

### Chi altro legge i campi sensibili (osservato)
Frontend (tutte le chiavi, via `load` del plugin); API locale Rust (`apiConfig` con cache di 5 s, `llmConfig`, `providerConfigs`, `projectLlmOverrides`, `embeddingConfig`, `searchApiConfig`); runtime agente (`load_agent_runtime_config`); avvio Rust (`proxyConfig`); bind (`allowLanAccess`); Clip server (token, per richieste non loopback); client MCP (solo dalla variabile d'ambiente); comandi `shell.exec` approvati (qualunque file leggibile dall'utente, dedotto dal commento «non è una sandbox»); estensione browser non letta. Il frontend passa i segreti al Rust per IPC a ogni chiamata (`agent_start_turn*` con `llm_config`, `search_project` con `embedding_config`, `web_search` con le chiavi di **tutti** i provider di ricerca, `set_proxy_env` con l'URL del proxy). Le rotte `/health` e `projects` non restituiscono valori di configurazione (altre non rilette). [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r8.md §4. Chi altro legge i campi sensibili (AC4)]

### Esposizione (osservato, con deduzioni dichiarate)
- **Log:** il proxy è redatto prima dello stderr (`redact_url`, con test); il server API non stampa URL, query né header; il token può arrivare come parametro `?token=` e la UI lo sconsiglia. Sei tipi di configurazione derivano `Debug` con la chiave (`LlmConfig`, `LlmClient`, `SearchEmbeddingConfig`, `WebSearchConfig`, `WebSearchProviderOverride`, `AgentRuntimeConfig`): stampa effettiva non vista (deduzione non testata).
- **Chiave SerpApi nell'URL:** la ricerca SerpApi del backend compone l'URL con il parametro `api_key` nella query (`tools.rs:1983-2003`); gli altri provider mettono la chiave negli header o nel corpo. Che il testo dell'errore di `reqwest` includa l'URL, e quindi la chiave, è una deduzione non testata: **non conclusivo** (sorgente di `reqwest` non letto).
- **Export dello zip:** `app-state.json` non finisce nello zip (per percorsi: lo store sta in `app_data_dir`, l'export cammina la sola cartella del progetto); che nessun file di `.llm-wiki/` contenga una chiave non è verificato.
- **Rete:** API e Clip server in HTTP semplice (`Server::http`); con `allowLanAccess` bind `0.0.0.0` e token in chiaro in LAN; con `acceptInvalidCerts` i client nativi accettano certificati non validi. Le credenziali del proxy sono nell'ambiente di processo; il processo `claude` non fa `env_clear` e le eredita, `shell.exec` no (lista bianca).
- **Interfaccia:** campo del token di tipo `password`, ma il token reale compare in chiaro negli esempi `curl` e MCP copiabili; la maschera degli altri campi non è verificata. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r8.md §5. Esposizione: log, console, errori, export, telemetria, rete (AC1, AC6)]

### Esito proposto dal dossier
**CONFERMATO per lettura**: chiavi e token scritti nello store così come sono, senza cifratura, offuscamento né archivio protetto nel codice letto; lettori Rust sul valore in chiaro. **NON CONCLUSIVO** per: (a) permessi e protezione del file di plugin e sistema operativo; (b) chiave SerpApi nei messaggi d'errore; (c) telemetria e altre copie dei segreti fuori dalle righe lette; (d) contenuto reale del file (mai aperto, per divieto). Impatto se si verifica (deduzione non testata): chi legge il file dell'utente (altri processi dello stesso account, malware, backup, sincronizzazione del profilo) ottiene in un colpo le chiavi LLM, di ricerca e di embedding, i token MinerU, le credenziali del proxy e il token API locale; con `allowLanAccess` il token viaggia in chiaro sulla rete locale. Gravità proposta (non decisione): alta per concentrazione e assenza di protezione a riposo, attenuata dal modello di minaccia di un'app desktop locale; da valutare in US-033. Stato proposto del gap `llm-wiki-token-cifratura`: chiudibile come «confermato per lettura» con residui dichiarati. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r8.md §6. Esito proposto e tabella evidenze (AC1, AC6)]

### Ricerca testuale globale (sessione principale, estende i negativi del dossier)
Eseguita su `src`, `src-tauri/src`, `mcp-server/src`, `extension`, `src-tauri/Cargo.toml`, `package.json` (espressioni case-insensitive, esclusi i test, output limitato a file e riga); il comando è in TSK-026 §Chiusura:
- **Nessuna cifratura né archivio protetto** in tutto il codice e nelle dipendenze dirette: le sole occorrenze sono falsi positivi (hash SHA-256 di cache e immagini, documenti cifrati in ingresso, testo di avviso sul proxy).
- **Permessi del file mai impostati:** una sola occorrenza, in un test di `agent/runtime.rs` (dopo `#[cfg(test)]`, riga 4032). I permessi di `app-state.json` sono quelli predefiniti del plugin e del sistema, non letti.
- **Nessuna telemetria:** solo falsi positivi in `mineru.ts` (321, 330).
- **Nessuna copia delle chiavi in `localStorage`:** i `setItem`/`getItem` simili riguardano lo stato dei pannelli (`app-layout.tsx:30, 96`).
- **Nessun log diretto delle configurazioni** (`console.*`, `println!`/`eprintln!`/`dbg!`); resta il rischio, non osservato, di stampa indiretta tramite i `derive(Debug)`. [^src: management/kanban/EP-004-verifica-rischi-di-persistenza/US-032-rischio-segreti-in-chiaro/TSK-026.md §Chiusura]

### File letti e non letti
Letti (28, sola lettura): `wiki-store.ts`, `project-store.ts`, `api-token.ts`, `proxy-config.ts`, `llm-task-routing.ts`, `llm-providers.ts` (parziale), `llm-client.ts`, `mineru.ts`, `web-search.ts`, sezioni API e ricerca web delle impostazioni, `settings-view.tsx`, `proxy.rs`, `lib.rs`, `api_server.rs` (parziale), `provider.rs`, `tools.rs` (finestre), `events.rs`, `session.rs`, `search.rs` (parziale), `project_maintenance.rs`, `claude_cli.rs`, `clip_server.rs`, `server_bind.rs`, `Cargo.toml`, `capabilities/default.json`, `package.json`, `mcp-server/src/api-client.ts`. Non letti: sezioni LLM, embedding, MinerU, multimodale e rete delle impostazioni (maschera dei campi, chiamante di `saveProviderConfigs`); ramo `custom` di `llm-providers.ts`; `tauri-fetch.ts`; `external_search.rs`, `codex_cli.rs`, `cli_resolver.rs`; `runtime.rs`, `types.rs` e parti di `api_server.rs`; l'estensione (`popup.js`, `background.js`); sorgenti di `reqwest`, `tauri-plugin-store`, pacchetto JS `@tauri-apps/plugin-store`, `Cargo.lock`; `tauri.conf.json`. Nessun `.env*`, `app-state.json` reale né file di credenziali aperto. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r8.md §File letti e non letti]

### Controllo del repo e dei segreti dichiarato
L'agente non ha eseguito `git status` né `git log`: il controllo a comando è in TSK-026 §Chiusura (`git -C code_repos/llm_wiki log -1 --format=%h` → `e08cfce`, `status --short` → vuoto; `grep -ciE` sui pattern dei segreti sul dossier → 0). Il dossier dichiara 0 valori di segreto; le credenziali fittizie di un test in `proxy.rs` non sono riportate. Nessuna istruzione rivolta a un agente trovata nei file letti. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r8.md §Note di estrazione] [^src: management/kanban/EP-004-verifica-rischi-di-persistenza/US-032-rischio-segreti-in-chiaro/TSK-026.md §Chiusura]

## Pagine collegate
[[llm-wiki-rischi-persistenza]] (§Esito della verifica di US-032), [[llm-wiki-sicurezza]], [[llm-wiki-archivi-persistenza]], [[2026-11-21-repo-llm_wiki-dossier-ep004-r7]], [[2026-11-21-repo-llm_wiki-persistenza-d]], [[gaps]].

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

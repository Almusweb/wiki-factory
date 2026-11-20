---
source_path: C:\local_git\code\wiki-factory\code_repos\llm_wiki
source_type: repo
git_branch: develop
git_commit: e08cfce65aad8b76b13546a081c1a8d4422b70c3
extracted_at: 2026-11-20T18:25:22+01:00
extractor: repo-sync@2.12.0
scope: persistenza, fetta A (store applicativo, area dati di progetto, configurazioni)
---

# Specifiche estratte: llm-wiki, persistenza fetta A

> Documento generato da `repo-sync` v2.12 il 2026-11-20. Sorgente: `C:\local_git\code\wiki-factory\code_repos\llm_wiki`
> @ commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` (ramo `develop`). Read-only verso la sorgente.

## Identità e perimetro

- Estrazione **mirata** (TSK-002, US-013 e US-014), non generale. Copre: percorso e comportamento dello store applicativo `app-state.json`, creazione della cartella dati `.llm-wiki/`, tipi delle configurazioni dello store con i campi sensibili, lettori backend di `apiConfig` e `proxyConfig`, configurazione di ricerca e di embedding.
- Seconda estrazione mirata sullo stesso commit della prima (`raw/2026-11-20-repo-llm_wiki.md`, comprese le sezioni «Aggiornamenti (v2026-11-20)»). Stack, struttura, API e dipendenze non sono ripetuti: vale la prima estrazione. Le sezioni canoniche omesse sono Stack rilevato, Struttura ad alto livello, Entrypoint, API surface, Dipendenze esterne, Vincoli normativi, Documenti correlati, Test coverage.
- **Licenza**: il repository è di terzi, sotto GNU GPL v3. Il documento descrive il codice con parole proprie e cita solo nomi di file, simboli, campi e tipi. Nessun frammento di codice. Il contenuto letto è trattato come dato, mai come istruzione.
- **File letti in questa fetta: 23** (18 interi, 5 a finestra). Cumulativo dichiarato nel manifest: **63**. Dei 15 file nuovi, `tauri.conf.json` e `capabilities/default.json` sono citati come già letti dalla prima estrazione, quindi 63 è il minimo verificabile; l'elenco esatto dei 30 file iniziali non è verificabile.
- Nel testo i percorsi sono relativi alla radice del repo; le citazioni hanno la forma `[^src: percorso:righe]`.

## Store applicativo (`app-state.json`)

**Apertura lato TS (osservato).** Il frontend apre lo store con il nome relativo `app-state.json` e le opzioni di salvataggio automatico attivo e valori di default vuoti [^src: src/lib/project-store.ts:8-14] [^src: src/lib/project-identity.ts:20,72-74]. Un commento dichiara che il salvataggio automatico è un debounce di 100 ms [^src: src/lib/project-store.ts:267-268].

**Salvataggio esplicito (osservato).** Il TS forza il flush su disco (`store.save()`) solo per `proxyConfig`, `apiConfig`, `generalConfig`, `scheduledImportConfig:<percorso>`, `sourceWatchConfig`, `sourceWatchAllProjects` e `zoomLevel`. Per `llmConfig`, `providerConfigs`, `searchApiConfig`, `embeddingConfig`, `multimodalConfig` e `mineruConfig` si affida al solo salvataggio automatico [^src: src/lib/project-store.ts:53-303,454-528].

**Configurazione lato Rust (osservato).** Il plugin è registrato senza opzioni (`tauri_plugin_store::Builder::default().build()`) [^src: src-tauri/src/lib.rs:558]. La capability della finestra principale include `store:default` [^src: src-tauri/capabilities/default.json:13]. L'identificatore dell'app è `com.llmwiki.app` [^src: src-tauri/tauri.conf.json:4].

**Percorso effettivo.** Il Rust non usa il plugin per leggere: legge il file con le API del file system, componendo la cartella dati dell'app (`app_data_dir()`) con il nome `app-state.json`, in tre punti [^src: src-tauri/src/lib.rs:405-409] [^src: src-tauri/src/lib.rs:581-584] [^src: src-tauri/src/api_server.rs:740]. Il commento di `proxy.rs` afferma che è lo stesso file scritto dal plugin lato frontend [^src: src-tauri/src/proxy.rs:3-14]. Questa identità è affermata dagli autori nei commenti; non è verificata in esecuzione.

**Comportamento su file illeggibile o corrotto, lato Rust (osservato).**
- Agente: la lettura restituisce «assente»; configurazione di default e nessun progetto dal registro. Un progetto non trovato produce l'errore «Unknown project» [^src: src-tauri/src/lib.rs:343,405-409].
- Proxy all'avvio: nessuna configurazione, log «requests go direct» [^src: src-tauri/src/lib.rs:588].
- API: se la rilettura fallisce si riusa l'ultimo valore in cache; senza valore precedente il risultato è «assente». Con stato assente il token manca (risposta 401 su ogni endpoint tranne `/health`) mentre il flag `enabled` vale vero per default [^src: src-tauri/src/api_server.rs:694-703,727-753].

**Comportamento su file corrotto, lato TS.**
- Osservato: `loadRegistry` ha try/catch e restituisce un registro vuoto [^src: src/lib/project-identity.ts:76-84]. Gli altri caricamenti di `project-store.ts` non hanno gestione degli errori.
- Deduzione dal codice, non osservata in esecuzione: l'inizializzazione di `App.tsx` è racchiusa in un try con catch che ignora l'errore e in un finally che spegne il caricamento [^src: src/App.tsx:307-431]. Se l'apertura dello store rifiuta, il resto delle configurazioni non viene caricato e l'ultimo progetto non viene riaperto, senza avviso all'utente.

**Non verificato.** Il percorso fisico per sistema operativo (risoluzione di `app_data_dir()` e del nome relativo da parte del plugin) e il comportamento del plugin store su file corrotto. Motivo: sorgente e documentazione del plugin non disponibili offline (nessuna `node_modules`, nessun `src-tauri/target`, nessuna copia del plugin nella cache cargo locale).

## Cartella dati di progetto `.llm-wiki/`

| Caso | Punto di creazione | Fonte | Stato |
|---|---|---|---|
| Progetto creato | `createProject` (TS) chiama il comando Rust `create_project`, che non crea `.llm-wiki/` (prima estrazione), poi `ensureProjectId`, che prova a leggere `.llm-wiki/project.json` e, se manca, lo scrive con `writeFile` | src/commands/fs.ts:248-256; src/lib/project-identity.ts:47-68 | Osservato per il punto di chiamata; creazione implicita della cartella non verificata |
| Aperto da disco | Auto-riapertura dell'ultimo progetto, selezione da recenti e «Open Wiki Project» passano tutti da `openProject`, che chiama il comando Rust `open_project` (solo validazione, prima estrazione) e poi `ensureProjectId`: stesso punto del caso «creato» | src/App.tsx:415-423,595-617; src/commands/fs.ts:258-263 | Come sopra |
| Importato (archivio) | `import_project_archive` estrae ogni voce dello zip creando le cartelle genitore; se l'archivio contiene `.llm-wiki/` viene ripristinato. L'export include l'intera radice del progetto, `.llm-wiki/` compresa, senza esclusioni salvo i symlink. Richiede `wiki/index.md` e una destinazione vuota | src-tauri/src/commands/project_maintenance.rs:155-190,204-267 | Osservato per l'estrazione; chiamante UI e apertura successiva non letti |
| Creazione tardiva, tutti i casi | `ensureDir` crea `.llm-wiki` e `.llm-wiki/chats` con `createDirectory`, ignorando gli errori; è chiamata da `saveReviewItems`, `saveLintItems`, `saveChatHistory` e `saveChatPreferences`, cioè alla prima di queste scritture | src/lib/persist.ts:9-12,14-18,30-34,79-85,244-251 | Osservato; chi attiva queste scritture (auto-save) non letto |

Ulteriori fatti osservati:
- La dialog di creazione scrive `schema.md` e `purpose.md` e crea le `extraDirs` del template; salva poi la lingua di output nello store, indicizzata per id progetto [^src: src/components/project/create-project-dialog.tsx:115-131].
- I wrapper TS `writeFile` e `createDirectory` richiedono percorsi assoluti e delegano ai comandi Rust omonimi [^src: src/commands/fs.ts:22-25,123-126].
- Il Rust legge `.llm-wiki/project.json` per ricavare l'id dei progetti recenti, con ripiego sul percorso quando manca [^src: src-tauri/src/lib.rs:436-448] [^src: src-tauri/src/api_server.rs:877-884].

**Non verificato.** (a) Se i comandi Rust `write_file` e `create_directory` creano le cartelle genitore (`fs.rs`, fetta B): da questo dipende se `ensureProjectId` crea da solo `.llm-wiki/` all'apertura. (b) Il chiamante dell'auto-save e l'ordine della prima scrittura. (c) Cosa avviene dopo un import: il chiamante UI di `import_project_archive` non è stato letto.

## Configurazioni dello store: tipi e campi sensibili

Tipi in `src/stores/wiki-store.ts` (salvo diversa indicazione). Solo nomi e tipi; nessun valore. Il simbolo «S» marca i campi sensibili.

| Chiave dello store | Tipo | Campi (tipo) |
|---|---|---|
| `llmConfig` | `LlmConfig` | `provider` (unione di 9 valori: openai, anthropic, google, azure, ollama, custom, minimax, claude-code, codex-cli), **`apiKey` S** (string), `model`, `ollamaUrl`, `customEndpoint`, `maxContextSize` (number); opzionali: `azureApiVersion`, `azureModelFamily`, `apiMode`, `reasoning`, `ingestReasoning` (`ReasoningConfig`: `mode`, `budgetTokens?`), `localCliIsolation`, `codexCliTimeoutMinutes`, `requestTimeoutMinutes`, `streamingEnabled`, **`customHeaders` S?** (mappa string-string), `extraRequestBody` (mappa generica) |
| `providerConfigs` | `Record<string, ProviderOverride>` | **`apiKey?` S**, `model?`, `baseUrl?`, `azureApiVersion?`, `azureModelFamily?`, `apiMode?`, `maxContextSize?`, `reasoning?`, `ingestReasoning?`, `localCliIsolation?`, `codexCliTimeoutMinutes?`, `requestTimeoutMinutes?`, `streamingEnabled?`, **`customHeaders?` S?**, `extraRequestBody?` |
| `customLlmPresets` | `CustomLlmPreset[]` (massimo 50) | `id` (prefisso `custom-`), `label` (massimo 80 caratteri) |
| `activePresetId`, `taskModelRouting` | string o null; `TaskModelRoutingConfig` | `chatPresetId`, `ingestPresetId` (string o null) |
| `projectLlmOverrides` | mappa per id progetto di `ProjectLlmOverride` | `enabled`, `presetId`, `model`, `profile?` (copia di `LlmConfig` senza `apiKey` e `customHeaders`: omessi per scelta dichiarata, il Rust unisce la chiave da `providerConfigs[presetId]`) |
| `searchApiConfig` | `SearchApiConfig` | `provider` (tavily, serpapi, searxng, ollama, brave, bocha, firecrawl, none), **`apiKey` S**, `serpApiEngine?`, `searXngUrl?`, `searXngCategories?`, `ollamaUrl?`, `providerConfigs?` (per provider: **`apiKey?` S**, `baseUrl?`, `serpApiEngine?`, `searXngUrl?`, `searXngCategories?`, `ollamaUrl?`), `deepResearchSource?` (web, anytxt, both), `anyTxt?` (`enabled?`, `endpoint?`, `filterDir?`, `filterExt?`, `limit?`) |
| `embeddingConfig` | `EmbeddingConfig` | `enabled`, `endpoint`, **`apiKey` S**, `model`; opzionali `outputDimensionality`, `maxChunkChars`, `overlapChunkChars`, `concurrency`, `batchSize`, **`extraHeaders` S?** (mappa string-string) |
| `multimodalConfig` | `MultimodalConfig` | `enabled`, `useMainLlm`, `provider`, **`apiKey` S**, `model`, `ollamaUrl`, `customEndpoint`, `concurrency`; opzionali `azureApiVersion`, `azureModelFamily`, `apiMode` |
| `mineruConfig` | `MineruConfig` (normalizzato in project-store.ts:204-233) | `enabled`, **`token` S**, `modelVersion` (pipeline o vlm); opzionali `backend` (cloud o local), `localEndpoint`, **`localToken` S**, `localBackend` (5 valori), `localEffort`, `localParseMethod`, `localLanguage`, `localFormulaEnabled`, `localTableEnabled`, `localImageAnalysis`, `localServerUrl` |
| `proxyConfig` | `ProxyConfig` (anche in src/lib/proxy-config.ts) | `enabled`, **`url` S?** (può includere credenziali nell'URL, come dichiara il commento di proxy-config.ts:20-25), `bypassLocal`, `acceptInvalidCerts?` |
| `apiConfig` | `ApiConfig` | `enabled`, `allowUnauthenticated`, `allowLanAccess`, `mcpEnabled` (booleani), **`token` S** (string) |
| `generalConfig` | `GeneralConfig` | `autostart` (bool), `closeBehavior` (ask, minimize, exit) |
| `scheduledImportConfig:<percorso>` | `ScheduledImportConfig` | `enabled`, `path`, `interval` (minuti), `lastScan` (number o null) |
| `sourceWatchConfig` (per id progetto o `default`), `sourceWatchAllProjects` | `SourceWatchConfig`; bool | `enabled`, `autoIngest`, `persistExtractedMarkdown`, `parsingConcurrency`, `ingestConcurrency`, `includeExtensions`, `excludeExtensions`, `excludeDirs`, `excludeGlobs` (liste di string), `maxFileSizeMb` (da 1 a 4096) |
| `recentProjects` (massimo 10), `lastProject`, `projectRegistry`, `updateCheckState`, `language`, `theme`, `outputLanguage`, `projectOutputLanguages`, `zoomLevel`, `projectFileSyncEnabled` | `WikiProject[]`, `WikiProject`, mappa di voci con `id`, `path`, `name`, `lastOpened`; `enabled`, `lastCheckedAt`, `dismissedVersion`; string e number | non sensibili |

Fatti da riportare:
- Tutti i default dei campi sensibili nello stato iniziale dello store sono stringhe vuote [^src: src/stores/wiki-store.ts:491-719].
- Tutti i segreti sono salvati in chiaro nello stesso file: il commento di `proxy-config.ts` dichiara che gli URL con credenziali sono conservati insieme alle altre chiavi API, senza un archivio dei segreti separato [^src: src/lib/proxy-config.ts:20-25].
- Il token API è generato lato TS con 32 byte casuali codificati in base64url [^src: src/lib/api-token.ts:1-23]. Porta e URL base dell'API: 19828 [^src: src/lib/api-server-constants.ts:1-3].
- La bozza delle impostazioni in UI (`SettingsDraft`) rispecchia questi campi in forma piatta [^src: src/components/settings/settings-types.ts:10-108]. La rinomina dei campi proxy e api tra TS e Rust è un vincolo dichiarato nei commenti [^src: src/lib/project-store.ts:258-262,283-287].

## Lettori backend di `apiConfig` e `proxyConfig`

**`apiConfig`.**
- Lettore: il modulo `api_server.rs`, tramite `load_app_state` e gli helper `api_token`, `api_token_source`, `api_auth_required`, `api_allow_unauthenticated`, `api_allow_lan_access`, `api_enabled`, `api_mcp_enabled` [^src: src-tauri/src/api_server.rs:586-753].
- Frequenza: a ogni richiesta, con una cache di 5 secondi (`APP_STATE_CACHE_TTL`) [^src: src-tauri/src/api_server.rs:38,727-753]. Il comando Tauri `api_server_reload_config` invalida la cache [^src: src-tauri/src/lib.rs:55-62].
- `allowLanAccess` incide anche sull'host di ascolto, scelto al bind tramite `server_bind::configured_bind_host` (dettaglio nella prima estrazione): si rilegge a ogni (ri)bind del ciclo del server, non a ogni richiesta [^src: src-tauri/src/api_server.rs:134-136].
- Il token è accettato anche come parametro `token` nell'URL, oltre agli header `X-LLM-Wiki-Token` e `Authorization` [^src: src-tauri/src/api_server.rs:593-621]. La variabile d'ambiente `LLM_WIKI_API_TOKEN` prevale sul valore dello store [^src: src-tauri/src/api_server.rs:623-637].
- L'endpoint `/health` risponde senza autenticazione con flag di stato (`authRequired`, `authConfigured`, `tokenSource` in env, store o none, `enabled`, `mcpEnabled`, `allowUnauthenticated`, `allowLanAccess`), senza il valore del token [^src: src-tauri/src/api_server.rs:308-330].
- Gli endpoint di chat, di scrittura pagina e di embed richiedono sempre il token, anche con `allowUnauthenticated` attivo [^src: src-tauri/src/api_server.rs:433-445].

**`proxyConfig`.**
- Lettore: `proxy::read_proxy_config_from_store`, chiamato dal setup, una sola volta all'avvio [^src: src-tauri/src/lib.rs:581-589] [^src: src-tauri/src/proxy.rs:61-69].
- Il comando `set_proxy_env` riceve la configurazione come argomento e non rilegge il file; il TS fa prima il flush su disco [^src: src-tauri/src/lib.rs:509-514] [^src: src/lib/project-store.ts:264-276].
- L'URL del proxy è mascherato nei log (credenziali sostituite) [^src: src-tauri/src/proxy.rs:149-175].

**Altre chiavi lette dal Rust da `app-state.json`.** `projectRegistry` e `recentProjects` (elenco progetti); `embeddingConfig`, `llmConfig`, `searchApiConfig` e `searchApiConfig.anyTxt` (configurazione del runtime dell'agente). La lettura avviene a ogni avvio di turno agente (due funzioni, senza cache) [^src: src-tauri/src/lib.rs:105,191,346-434]. La conversione in struct usa un esito che scarta in silenzio i valori non deserializzabili (deduzione).

## Ricerca ed embedding

**`SearchEmbeddingConfig`** (Rust, serde in camelCase) [^src: src-tauri/src/commands/search.rs:86-105]:

| Campo | Tipo | Note |
|---|---|---|
| `enabled` | bool | obbligatorio |
| `endpoint` | string | obbligatorio |
| `apiKey` | string | obbligatorio, **sensibile** |
| `model` | string | obbligatorio |
| `outputDimensionality` | Option di f64 | |
| `extraHeaders` | Option di mappa string-string | default; potenzialmente sensibile |
| `maxChunkChars`, `overlapChunkChars` | Option di usize | default |

Il TS `EmbeddingConfig` ha in più `concurrency` e `batchSize`, che nella struct Rust non esistono (ignorati in deserializzazione: non c'è un divieto di campi sconosciuti). Il Rust richiede `enabled`, `endpoint`, `apiKey` e `model`: se manca uno di questi la deserializzazione fallisce (deduzione).

**`embedding_fetch`.**
- Comando Tauri con `text`, `cfg` e `max_retries` opzionale, default 3; delega a `fetch_embedding_with_retry`, che riduce a metà il testo su errore di dimensione eccessiva e ritenta [^src: src-tauri/src/commands/search.rs:131-141,1176-1200].
- La configurazione arriva dal frontend a ogni chiamata, quindi non è letta dal file; il TS passa l'intero oggetto, `apiKey` compresa, attraverso l'IPC [^src: src/lib/embedding.ts:93-116].
- `embedding_fetch_batch` è il comando gemello con elenco di testi [^src: src-tauri/src/commands/search.rs:143-152] [^src: src/lib/embedding.ts:118-136].
- `resolve_query_embedding`: usa un embedding esplicito se presente; altrimenti la configurazione, solo se `enabled` è vero e endpoint e modello non sono vuoti, con zero ritenti; in caso di errore degrada a ricerca per parole chiave con un log [^src: src-tauri/src/commands/search.rs:294-325].
- La costante `SEARCH_EMBEDDING_TIMEOUT_SECS` vale 8 [^src: src-tauri/src/commands/search.rs:22]; il suo uso non è nel campione.

**Ricerca web.** I comandi `web_search` (default 10 risultati) e `anytxt_search` (default 20) ricevono `WebSearchConfig` e `AnyTxtConfig` come argomento; le struct stanno in `agent/tools.rs`, non letto [^src: src-tauri/src/commands/external_search.rs:19-59].

**UI embedding.** La sezione Settings mantiene una bozza dei campi, ignora gli header riservati (autorizzazione, tipo di contenuto, host, lunghezza, intestazione della chiave Google) e usa la configurazione dello store per il re-index con svuotamento dell'indice esistente [^src: src/components/settings/sections/embedding-section.tsx:39-45,121-134,143-154]. Il salvataggio effettivo sta nel componente delle impostazioni, non letto.

## File letti e non letti

| File | Modalità | Non letto |
|---|---|---|
| src-tauri/tauri.conf.json, src-tauri/capabilities/default.json, src-tauri/src/lib.rs, src-tauri/src/commands/external_search.rs, src-tauri/src/commands/project_maintenance.rs | interi | |
| src/lib/project-store.ts, project-identity.ts, persist.ts, proxy-config.ts, source-watch-config.ts, api-token.ts, api-server-constants.ts | interi | |
| src/stores/wiki-store.ts, src/components/settings/settings-types.ts, src/commands/fs.ts, src/App.tsx, welcome-screen.tsx, create-project-dialog.tsx | interi | |
| src-tauri/src/proxy.rs | righe 1-260 | 261-fine (il modulo di test si apre alla riga 188: presumibilmente solo test, non verificato) |
| src-tauri/src/api_server.rs | righe 1-1200 | 1201-fine (gestori `handle_search`, `handle_embed_page`, `handle_write_page`, `handle_chat` e altri) |
| src-tauri/src/commands/search.rs | righe 1-1200 | 1201-fine (`fetch_embedding_once`, `fetch_embedding_batch` e altro) |
| src/lib/embedding.ts | righe 1-250 | 251-fine (già letto in parte nella prima estrazione) |
| src/components/settings/sections/embedding-section.tsx | righe 1-200 | 201-fine |

Già letti nella prima estrazione e non riletti: `src-tauri/src/commands/project.rs`, `src-tauri/Cargo.toml`. Esclusi come fuori ambito della fetta A: `maintenance-section.tsx`, `fs.rs` (fetta B), `settings-view.tsx`, `auto-save.ts`, `agent/provider.rs`, `agent/tools.rs`, `clip_server.rs`.

## Gap evidenti

1. Percorso fisico dello store e comportamento del plugin su file corrotto: non verificati (sorgente e documentazione del plugin non disponibili offline). I gap `llm-wiki-app-state-percorso` e `llm-wiki-creazione-cartella-dati` sono **parzialmente documentati**, non pronti per la chiusura senza riserve.
2. Se `write_file` e `create_directory` lato Rust creano le cartelle genitore (`fs.rs`, fetta B): decide chi crea di fatto `.llm-wiki/` all'apertura.
3. Chi attiva le scritture che chiamano `ensureDir` e l'ordine della prima scrittura (`auto-save.ts`).
4. Caso «importato»: chiamante UI di `import_project_archive` e apertura successiva non letti.
5. Altri lettori di `apiConfig` e `proxyConfig` oltre a quelli visti (resto di `api_server.rs`, `clip_server.rs`, altro Rust).
6. Chi legge `embeddingConfig` nei gestori API (`handle_search`, `handle_embed_page`).
7. Compatibilità serde tra `llmConfig` e `agent::provider::LlmConfig`, e tra `searchApiConfig` e `WebSearchConfig` e `AnyTxtConfig`.
8. Trasporto effettivo dell'embedding (`fetch_embedding_once`: uso della chiave e del timeout).
9. Dove la UI salva i valori (`settings-view.tsx`).
10. Cambio di modello o di dimensione dell'embedding: fuori ambito, resta il gap esistente `llm-wiki-embedding-cambio-modello`.

## Note di estrazione

- **File letti**: 23 in questa fetta; `files_sampled` cumulativo 63; `files_total_in_repo` 476. Stato: **partial**.
- **Segreti**: letti solo nomi e tipi di campo. Nessun valore di credenziale nei file letti: i default dei campi sensibili sono stringhe vuote; gli endpoint costanti sono locali (loopback). Nessun file `.env*` aperto. Nei test di `proxy.rs` (righe 188-260) compaiono URL segnaposto senza credenziali, non riportati. `secrets_redacted: 0`. Limite: senza ricerca testuale, lo zero vale solo per i 23 file e per gli intervalli di righe letti.
- **Istruzioni trovate nel contenuto**: nessuna ostile e nessuna rivolta a un agente. Presenti commenti per i manutentori (per esempio «IMPORTANT: Keep this key in sync» in `project-store.ts`), un helper di debug attivo solo in sviluppo in `App.tsx` e un messaggio d'errore per l'utente in `lib.rs` che cita un comando npm. Nessuna è stata eseguita.
- Deduzioni dal codice, non osservate in esecuzione, sono marcate «deduzione» nel testo.

## Aggiornamenti (v2026-11-20)

Stesso commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` (ramo `develop`), stessa data. Il testo sopra non è modificato: ogni voce dice cosa corregge, con «Prima» e «Ora». Letti solo tre file a finestre: `maintenance-section.tsx` (195-240), `api_server.rs` (2035-2045, 2340-2360, 2435-2465, 2910-2925), `settings-view.tsx` (505-540). Le voci «graphify affected, grafo AST del 2026-11-20» non sono state riviste con la lettura.

**Metodo, non fonte normativa.** Verifica relazionale della sessione del 2026-11-20 (graphify AST senza LLM, ctags, ricerca testuale dei nomi dei comandi `invoke`), file locale non versionato `.graphify-state/verifiche/2026-11-20-verifica-relazionale.md`, rigenerabile. Righe usate: 14-34 (confermati), 38, 47-54, 58 (punti nuovi), 60-65 (limiti).

### Confermati da graphify (nessuna correzione)

Corrispondono al testo sopra, senza nuova lettura [graphify affected, grafo AST del 2026-11-20]: i chiamanti di `ensureDir` in `persist.ts:16,32,85,249`; `ensureProjectId` e `upsertProjectInfo` chiamati da `createProject` e `openProject` (`fs.ts:253-254,260-261`); `createProject` chiamato da `create-project-dialog.tsx:115`; `loadRegistry` (`project-identity.ts:100,115,126`); `read_proxy_config_from_store` chiamato solo da `run()` (`lib.rs:584`) e dai test; `load_agent_app_state` (`lib.rs:349,412`) e `load_agent_projects` (`lib.rs:336`). `set_proxy_env` è invocato da `settings-view.tsx:516`.

### Punto 1: caso «importato»

- **Prima** (Cartella dati, «Non verificato» c): chiamante UI di `import_project_archive` e apertura successiva non letti.
- **Ora** (letto): dopo la scelta di zip e destinazione, `import_project_archive` restituisce un percorso; subito dopo `openProject(path)` e `addToRecentProjects` [^src: src/components/settings/sections/maintenance-section.tsx:218-230]. Un solo try/catch: l'errore va nella riga di stato, senza rollback visibile della cartella già estratta. Nella finestra nessuna chiamata imposta il progetto attivo.
- Che `openProject` passi da `ensureProjectId` e `upsertProjectInfo` è graphify (`fs.ts:260-261`) e il testo sopra: il caso importato converge sul punto di apertura degli altri casi. `.llm-wiki/project.json` è quello ripristinato dallo zip, se presente, altrimenti lo crea `ensureProjectId`.
- Resta non verificato: cosa accade se l'id ripristinato coincide con uno già nel registro.

### Punto 4: lettori di `app-state.json` in `api_server.rs`

- **Prima**: gap 5 e 6; la lettura di `embeddingConfig` nei gestori API non era chiara; lo scarto silenzioso delle conversioni serde era «deduzione».
- **Ora** (letto): `load_embedding_config` legge `embeddingConfig` [^src: src-tauri/src/api_server.rs:2349-2353]. La copia di `load_agent_runtime_config` in `api_server.rs` legge `embeddingConfig`, `llmConfig` (prima un override di progetto da `project_llm_config`, corpo non letto), `searchApiConfig` e `searchApiConfig.anyTxt` [^src: src-tauri/src/api_server.rs:2442-2465]; è usata a `:2041`. `load_source_watch_config` legge `sourceWatchConfig` per id progetto o `default` [^src: src-tauri/src/api_server.rs:2915-2925]. Tutte passano da `load_app_state`, quindi dalla cache di 5 secondi; la copia in `lib.rs` legge senza cache (testo sopra).
- Lo scarto silenzioso dei valori non deserializzabili è **osservato** per questa copia (`api_server.rs:2352,2450,2457,2462`). Per `lib.rs` resta «deduzione».
- Da graphify, non letto: `load_embedding_config` chiamato da `handle_embed_page` (`:1909`) e `handle_search` (`:1958`); `load_source_watch_config` da `handle_rescan` (`:2902`); `load_projects` (`:777`) da `handle_projects` (`:764`) e `resolve_project` (`:857`). Le chiavi di `load_projects` non sono confermate dalla lettura (solo graphify).
- **Stato dei gap**: gap 6 chiuso in parte (loader letto, chiamanti graphify). Gap 5 **resta aperto**: altri lettori di `apiConfig` e `proxyConfig` oltre a quelli visti ancora non verificati; i lettori delle altre chiavi (`embeddingConfig`, `llmConfig`, `searchApiConfig`, `sourceWatchConfig`, progetti) sono ora elencati.

### Punto 5: `resolve_query_embedding`

Non confermato dalla lettura (solo graphify): chiamanti `search_project` (`search.rs:118`), `handle_search` (`api_server.rs:1955`) e `run_wiki_search` (`agent/tools.rs:949`).

### Punto 9: quando la UI invoca `set_proxy_env` e il reload

- **Prima**: chiamante di `set_proxy_env` non nominato; il gap 9 chiedeva dove la UI salva i valori.
- **Ora** (letto): nel salvataggio delle impostazioni `set_proxy_env` riceve `newProxy` (errore solo in warn), poi `saveMineruConfig`, `saveApiConfig` e subito dopo `api_server_reload_config` (errore solo in warn) [^src: src/components/settings/settings-view.tsx:505-540]. Nessuna condizione visibile nella finestra. Un commento dice che le modifiche arrivano entro la cache di 5 s «senza IPC», ma il codice invoca comunque il reload: nota, non difetto. Il chiamante a `fs.ts:282` è solo graphify.
- Gap 9 chiuso in parte: proxy, API, MinerU e import pianificato sono collocati qui; le altre chiavi no.

### Limiti

Graphify non vede gli archi IPC tra TS e Rust: per quel confine vale la ricerca sui nomi dei comandi. Le costanti non sono nodi del grafo. `load_agent_runtime_config` è definita due volte (`lib.rs`, `api_server.rs`) ed è ambigua per graphify. Uno zero di graphify non prova l'assenza di chiamanti.

Segreti: nessun valore nelle finestre, solo nomi di chiavi. Istruzioni nel contenuto: solo commenti per i manutentori, non eseguiti.

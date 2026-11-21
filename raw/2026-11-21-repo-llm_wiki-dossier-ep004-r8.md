---
source_path: /home/user/wiki-factory/code_repos/llm_wiki
source_type: repo
git_branch: HEAD
git_commit: e08cfce65aad8b76b13546a081c1a8d4422b70c3
extracted_at: 2026-11-21
extractor: repo-sync@2.12.0
scope: dossier EP-004 r8 (TSK-026 / US-032), rischio 8, segreti in chiaro nello store applicativo
---

# Specifiche estratte: llm-wiki, dossier EP-004 r8 (rischio 8, segreti in chiaro nello store applicativo)

> Documento generato da `repo-sync` v2.12 il 2026-11-21. Sorgente: `/home/user/wiki-factory/code_repos/llm_wiki`
> @ commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` (HEAD staccato, nessun nome di ramo: il file `.git/modules/code_repos/llm_wiki/HEAD` della factory contiene solo l'hash, riletto in questa sessione). Read-only verso la sorgente.

## Identità e perimetro

- Estrazione **mirata** (TSK-026 / US-032), per sola lettura del codice (Q_003). Stack e struttura non ripetuti. Parte da wiki (rischio 8 in `wiki/concepts/llm-wiki-rischi-persistenza.md` §Dettaglio e §Aggiornamenti; `wiki/concepts/llm-wiki-sicurezza.md` §Segreti nello store; gap `llm-wiki-token-cifratura`) e **non ripete** la fetta D (`raw/2026-11-21-repo-llm_wiki-persistenza-d.md`): il comportamento di `app-state.json` su file corrotto, con possibile perdita di `apiConfig` e delle chiavi alla prima scrittura, resta lì. Qui compaiono solo l'elenco dei campi, la modalità di conservazione, i lettori e l'esposizione.
- **Divieto rispettato**: nessun valore di segreto letto, copiato o riportato; nessun `app-state.json` reale, nessun `.env*`, nessun file di credenziali aperto. Si citano solo nomi di campo, tipi, nomi di header e di variabili d'ambiente (nomi, non valori). Il gap `llm-wiki-scan-credenziali` (credenziali hardcoded) resta **fuori perimetro**.
- **Licenza**: repository di terzi, GNU GPL v3. Solo nomi di file, simboli e righe; nessun frammento di codice. Le uniche stringhe alla lettera sono nomi di header/variabili e testi mostrati all'utente, citate come stringhe.
- Citazioni `[^src: percorso:righe]`, percorsi relativi alla radice del repo del cliente.
- «Osservato» = letto nel codice in questa sessione. «Ereditato» = riportato dalla fetta D o dalla wiki, **non riletto qui**. «Deduzione non testata» = ricavata da fatti osservati, mai vista in esecuzione. Nessuna esecuzione dell'app, nessuna lettura del contenuto reale dello store. Nessuna ricerca testuale globale (l'agente non ha `Bash` né `Grep`): un «non trovato» vale solo per le righe lette di §File letti e non letti; le ricerche larghe sono affidate al chiamante (§Stringhe da cercare).
- **Limite dichiarato in anticipo (TSK-026)**: la protezione del file da parte della libreria dello store o del sistema operativo (permessi, ACL, cifratura del disco, sincronizzazione del profilo) non è osservabile per lettura. Esito «non conclusivo» con motivo (§3).

## Ipotesi di partenza (come in wiki / US-032)

Token e chiavi provider sono campi JSON dello store `app-state.json` senza passaggi di cifratura visibili nelle finestre lette: probabile memorizzazione in chiaro (deduzione non testata, gap `llm-wiki-token-cifratura`). Stato di partenza: nomi di campo letti, nessun valore; due token in `mineruConfig`, un token in `apiConfig`; presenza di chiavi in LLM, ricerca, embedding e provider non verificata (tipi non letti). Il tipo `wiki-store.ts` è ora letto per intero.

## 1. Elenco dei campi sensibili (AC2)

Tutti sono campi di chiavi dello store `app-state.json`. I tipi sono in [^src: src/stores/wiki-store.ts]; i valori iniziali (stato dello store prima di qualsiasi salvataggio) sono **stringhe vuote** o assenti [^src: src/stores/wiki-store.ts:504-526, 632-654, 656-672, 676-681, 692-706, 713-719].

| # | Chiave dello store | Campo sensibile (nome) | Tipo | Dove è definito | Categoria |
|---|---|---|---|---|---|
| 1 | `llmConfig` | `apiKey` | stringa | wiki-store.ts:29 | chiave provider LLM |
| 2 | `llmConfig` | `customHeaders` | mappa nome→valore, opzionale | wiki-store.ts:60 | header personalizzati (possono portare credenziali di gateway) |
| 3 | `llmConfig` | `extraRequestBody` | mappa libera, opzionale | wiki-store.ts:61-62 | corpo extra libero: **potenzialmente** sensibile (campo non vincolato) |
| 4 | `providerConfigs[<preset>]` | `apiKey` | stringa, opzionale | wiki-store.ts:339 (tipo `ProviderOverride`, 338-355) | chiave provider LLM per preset (sopravvive al cambio preset, commento 333-337) |
| 5 | `providerConfigs[<preset>]` | `customHeaders` | mappa, opzionale | wiki-store.ts:353 | header personalizzati per preset |
| 6 | `providerConfigs[<preset>]` | `extraRequestBody` | mappa libera, opzionale | wiki-store.ts:354 | come 3 |
| 7 | `searchApiConfig` | `apiKey` | stringa | wiki-store.ts:120 | chiave di ricerca web (provider attivo) |
| 8 | `searchApiConfig.providerConfigs[<provider>]` | `apiKey` | stringa, opzionale | wiki-store.ts:99-101, 125, 108 | chiave di ricerca per provider (tavily, serpapi, brave, bocha, ollama, firecrawl) |
| 9 | `embeddingConfig` | `apiKey` | stringa | wiki-store.ts:133 | chiave embedding |
| 10 | `embeddingConfig` | `extraHeaders` | mappa, opzionale | wiki-store.ts:156-163 | header personalizzati embedding (la UI scarta quelli riservati, search.rs:1378-1390) |
| 11 | `multimodalConfig` | `apiKey` | stringa | wiki-store.ts:322 | chiave del modello di didascalie (usata se `useMainLlm` è falso) |
| 12 | `mineruConfig` | `token` | stringa | wiki-store.ts:312 | token MinerU cloud |
| 13 | `mineruConfig` | `localToken` | stringa, opzionale | wiki-store.ts:302-303 | token Bearer del servizio MinerU locale |
| 14 | `proxyConfig` | `url` | stringa | wiki-store.ts:202 | **proxy con credenziali**: il commento dichiara che la forma `schema://utente:password@host:porta` è ammessa e conservata alla lettera accanto alle altre chiavi, senza archivio dei segreti separato [^src: src/lib/proxy-config.ts:20-25] |
| 15 | `apiConfig` | `token` | stringa | wiki-store.ts:238 | token API locale (Bearer), segreto di accesso all'API e al Clip server dalla rete |

**Non segreti ma rilevanti per la sicurezza (nello stesso file)**: `apiConfig.allowUnauthenticated`, `apiConfig.allowLanAccess`, `apiConfig.enabled`, `apiConfig.mcpEnabled` (wiki-store.ts:233-239); `proxyConfig.acceptInvalidCerts` e `bypassLocal` (200-205).

**Campi URL che *potrebbero* contenere credenziali incorporate** (deduzione non testata: il tipo è una stringa libera): `llmConfig.customEndpoint`, `ollamaUrl` (31-32), `ProviderOverride.baseUrl` (341), `SearchProviderOverride.baseUrl` e `searXngUrl` (101, 103), `embeddingConfig.endpoint` (132), `multimodalConfig.customEndpoint` (325), `mineruConfig.localEndpoint` e `localServerUrl` (301, 311). Osservato per uno solo: il lato MinerU locale **rifiuta** un endpoint con utente o password nell'URL [^src: src/lib/mineru.ts:81-93, 89-91]; per gli altri il codice letto non mostra un controllo analogo (non letti i punti di salvataggio, `llm-provider-section.tsx`, `embedding-section.tsx` intero lato validazione).

**Non sensibili per costruzione (osservato)**:
- `projectLlmOverrides[<idProgetto>].profile` è del tipo `Omit<LlmConfig, "apiKey" | "customHeaders">` con commento «credentials are not duplicated per project» [^src: src/stores/wiki-store.ts:371-383]; la funzione `projectLlmProfile` toglie a runtime `apiKey` e `customHeaders` [^src: src/lib/llm-task-routing.ts:33-38]. Il Rust ricompone la credenziale al volo da `providerConfigs[presetId]` [^src: src-tauri/src/api_server.rs:2375-2417]. **Restano nel profilo** `extraRequestBody`, `customEndpoint`, `ollamaUrl` (il tipo non li esclude). Il chiamante che compila `profile` non è letto.
- `taskModelRouting` conserva solo id di preset, non credenziali (commento) [^src: src/lib/llm-task-routing.ts:40-45; src/stores/wiki-store.ts:364-369].
- `customLlmPresets` conserva solo `id` ed `etichetta` [^src: src/lib/project-store.ts:88-103].

**Fuori dallo store (osservato)**:
- Variabile d'ambiente `LLM_WIKI_API_TOKEN` (nome): prevale sul token dello store [^src: src-tauri/src/api_server.rs:623-629, 639-659]; è anche la sola fonte del token per il client MCP [^src: mcp-server/src/api-client.ts:206-207].
- Credenziali del proxy nell'**ambiente del processo**: `HTTP_PROXY` e `HTTPS_PROXY` ricevono l'URL intero, credenziali comprese [^src: src-tauri/src/proxy.rs:126-127].
- Le credenziali del CLI Claude (OAuth in `~/.claude/`) sono del CLI, non dell'app: il modulo dichiara di riusarle e non le legge [^src: src-tauri/src/commands/claude_cli.rs:3-6] (osservato come commento; il modulo codex non letto).

## 2. Come sono conservati (AC3)

### 2.1 Punti di scrittura nello store: nessuna trasformazione dei segreti

Tutte le funzioni di salvataggio aprono lo store `app-state.json` con salvataggio automatico e valori di default vuoti [^src: src/lib/project-store.ts:8-14] e scrivono l'oggetto **così com'è** con `store.set(chiave, oggetto)`:

| Chiave | Funzione | Righe | Trasformazione del segreto |
|---|---|---|---|
| `llmConfig` | `saveLlmConfig` | project-store.ts:53-56 | nessuna |
| `providerConfigs` | `saveProviderConfigs` | 63-66 | nessuna |
| `searchApiConfig` | `saveSearchApiConfig` | 160-163 (chiamata da web-search-section.tsx:87-91) | nessuna |
| `embeddingConfig` | `saveEmbeddingConfig` | 172-175 | nessuna |
| `multimodalConfig` | `saveMultimodalConfig` | 184-187 | nessuna |
| `mineruConfig` | `saveMineruConfig` | 247-250, con `normalizeMineruConfig` 204-233 | solo `trim` su `localToken`; `token` passato com'è (230) |
| `proxyConfig` | `saveProxyConfig` | 264-276 | nessuna; flush esplicito `store.save()` (275) |
| `apiConfig` | `saveApiConfig` | 289-298 | nessuna; flush esplicito (297) |
| `projectLlmOverrides` | `saveProjectLlmOverride` | 130-144 | nessuna sul resto; profilo senza `apiKey` e `customHeaders` (§1) |

La sequenza di salvataggio delle impostazioni costruisce gli oggetti dal draft e li passa alle funzioni sopra [^src: src/components/settings/settings-view.tsx:383-459, 483-535]; `providerConfigs` e `searchApiConfig` sono salvati dalle rispettive sezioni (per la ricerca: `persist` → `saveSearchApiConfig`, a ogni modifica di un provider) [^src: src/components/settings/sections/web-search-section.tsx:87-110]. La sezione `llm-provider-section.tsx` che salva `providerConfigs` **non è letta**: il punto di scrittura di quelle chiavi è osservato solo nel modulo (`saveProviderConfigs`), non nel chiamante.

### 2.2 Cifratura, offuscamento, archivio protetto

- **Cifratura o offuscamento nei punti di scrittura**: **non osservati** (tabella §2.1). L'unica codifica di un segreto è la generazione del token (32 byte casuali in base64url), che non è cifratura a riposo [^src: src/lib/api-token.ts:8-23].
- **Lettori Rust usano il valore alla lettera**: il token API si confronta a tempo costante direttamente col valore letto dal campo `apiConfig.token` del JSON [^src: src-tauri/src/api_server.rs:593-637, 716-725]; `llmConfig.apiKey` diventa l'header di autorizzazione senza passaggi intermedi [^src: src-tauri/src/agent/provider.rs:634-691]. Un valore cifrato nel file renderebbe questi percorsi non funzionanti: coerente con la conservazione **in chiaro** (deduzione forte, non testata in esecuzione; il contenuto reale del file non è stato aperto per divieto).
- **Plugin store senza opzioni**: registrato con `Builder::default().build()` [^src: src-tauri/src/lib.rs:558]. **Ereditato dalla fetta D** (sorgente di `tauri-plugin-store` 2.4.3, non riletto): serializzazione predefinita JSON verso mappa chiave-valore e scrittura con `fs::write` diretto [^src: raw/2026-11-21-repo-llm_wiki-persistenza-d.md §File corrotto: che cosa si legge nel plugin]. Il pacchetto JS `@tauri-apps/plugin-store` non è letto.
- **Lettura diretta del file da più moduli Rust** con `serde_json` sul testo del file (nessun passaggio dal plugin): `api_server.rs:740-743`, `lib.rs:405-409`, `proxy.rs:64-69`, `server_bind.rs:22-25` (§4). Conferma che il formato su disco è JSON leggibile da codice senza chiavi di decifratura.
- **Archivio protetto del sistema (keychain, Credential Manager, Secret Service, Stronghold)**: nessuno nelle dipendenze dichiarate. `src-tauri/Cargo.toml` elenca tauri, opener, autostart, dialog, plugin-store, plugin-http, reqwest, tiny_http, zip, lancedb, arrow, sha2, md-5, base64 e simili, **nessun crate di keyring, stronghold o cifratura simmetrica** [^src: src-tauri/Cargo.toml:25-72]; `package.json` ha `@tauri-apps/plugin-store` e nessun pacchetto di keychain o stronghold [^src: package.json:19-60]. Limite: i manifest non mostrano le dipendenze transitive (`Cargo.lock` non letto) e un `Cargo.toml` non esclude un uso tramite API di sistema.
- **Capability della WebView**: `store:default` è concesso alla finestra principale [^src: src-tauri/capabilities/default.json:13] (l'insieme di permessi del plugin non è letto: che comprenda lettura di ogni chiave è una deduzione non testata dal nome).

### 2.3 Altri file e altri luoghi

- **Memoria della WebView**: tutti i segreti stanno nello stato `zustand` (`useWikiStore`) in chiaro [^src: src/stores/wiki-store.ts:431-451] e il TS compone gli header con la chiave (es. `Authorization`, `x-api-key`, `x-goog-api-key`, `api-key`) [^src: src/lib/llm-providers.ts:808-821, 941-956, 976-998, 1000-1017].
- **File di progetto**: i salvataggi di sessione agente persistono solo `role`, `content`, `timestamp`, `sessionId`, `projectId` [^src: src-tauri/src/agent/session.rs:14-31, 57-66, 172-174]: nessuna configurazione. Un segreto che l'utente incolla nel testo di una chat o di una sessione finirebbe nei file (deduzione generica, non testata).
- **Altri archivi di segreti nel repo letto**: nessuno individuato nelle finestre lette. `localStorage`, `sessionStorage`, `chrome.storage` dell'estensione: **non cercati** (§Stringhe da cercare).
- **Il token nelle istruzioni d'uso**: la UI incorpora il token reale nei testi copiabili (`curl` e configurazione MCP), da incollare in file esterni all'app (§5).

## 3. Permessi del file e protezione di libreria/OS (AC7): NON CONCLUSIVO

- **Percorso** (ereditato dalla fetta D): `<data_dir>/com.llmwiki.app/app-state.json`; su Windows `data_dir` è «Roaming AppData» [^src: raw/2026-11-21-repo-llm_wiki-persistenza-d.md §Catena di risoluzione del percorso].
- **Osservato**: nel repo del cliente non compare alcuna scrittura di `app-state.json` da parte del Rust (solo lettura: `api_server.rs:740-743`, `lib.rs:405-409`, `proxy.rs:64-69`, `server_bind.rs:22-25`); la scrittura è del plugin [^src: raw/2026-11-21-repo-llm_wiki-persistenza-d.md §File corrotto: i lettori Rust]. Nessuna riga letta del repo imposta permessi o attributi sul file. Il plugin lo scrive con `fs::write` diretto (ereditato, `store.rs:291-299`), senza riga di permessi nel corpo letto allora.
- **Motivo del «non conclusivo»**: la modalità effettiva (maschera di creazione, ACL ereditate da `%APPDATA%`, `umask`, sandbox del pacchetto) dipende dal sistema operativo e dal codice del plugin, qui non riletto, e non è osservabile senza leggere il file system dell'utente. Deduzioni non testate: su Linux e macOS il file nasce con i permessi predefiniti dell'account (tipicamente leggibile dal solo utente, ma non da una riga di codice letta); su Windows ereditato dalla cartella del profilo; la cartella «Roaming» è quella che i profili di dominio possono sincronizzare (non testato).

## 4. Chi altro legge i campi sensibili (AC4)

| Lettore | Cosa legge (nomi) | Come | Fonte |
|---|---|---|---|
| **Frontend (WebView)** | tutte le chiavi dello store | `load` del plugin e `store.get`; tutti i `load*` ricostruiscono lo stato in chiaro | project-store.ts:58-61, 68-71, 165-168, 177-180, 189-192, 252-256, 278-281, 300-303 |
| **API locale (Rust)** | `apiConfig.token`, `apiConfig.allowUnauthenticated`, `allowLanAccess`, `enabled`, `mcpEnabled`; `llmConfig`, `providerConfigs`, `projectLlmOverrides`, `customLlmPresets`, `embeddingConfig`, `searchApiConfig` | lettura del file con cache di 5 s e ripiego sul valore precedente se il file non si legge | api_server.rs:623-753, 2349-2353, 2363-2469; costante cache 38 |
| **Runtime agente (Rust, comandi UI)** | `embeddingConfig`, `llmConfig`, `searchApiConfig` (e `anyTxt`) | `load_agent_runtime_config`, lettura diretta del file | lib.rs:405-434 |
| **Avvio (Rust)** | `proxyConfig` (URL con credenziali) | all'avvio e al salvataggio, poi ambiente di processo | lib.rs:581-589; proxy.rs:64-69, 90-141 |
| **Bind (Rust)** | `apiConfig.allowLanAccess` | lettura diretta del file | server_bind.rs:22-31, 56-62 |
| **Clip server (Rust)** | token API (via `is_token_authorized`) per richieste non loopback | stessa funzione dell'API | clip_server.rs:124, 338-350 |
| **Client MCP** | token dalla **variabile d'ambiente** `LLM_WIKI_API_TOKEN`, mai da `app-state.json` | header `Authorization` Bearer | mcp-server/src/api-client.ts:206-207, 386-391 |
| **Comandi `shell.exec` approvati dell'agente** | qualunque file leggibile dall'utente, quindi anche `app-state.json` (deduzione dal commento che l'ambiente ridotto «non è una sandbox») | processo figlio con ambiente ridotto che conserva `HOME` | tools.rs:1197-1220 |
| **Estensione browser** | non letta (`popup.js`, `background.js`): se conservi il token | — | non letto |

**Passaggio di segreti tra frontend e Rust per IPC (osservato)**: il TS passa il segreto a ogni chiamata invece di lasciarlo leggere al Rust:
- `agent_start_turn` e `agent_start_turn_stream` accettano `llm_config` completo (con `apiKey`); la config del file è solo ripiego [^src: src-tauri/src/lib.rs:65-70, 105-106, 153-158, 191-192];
- `search_project` riceve `embedding_config` con `api_key` [^src: src-tauri/src/commands/search.rs:86-115];
- `web_search` riceve la configurazione risolta, che include **le chiavi di tutti i provider** in `providerConfigs`, non solo del provider attivo [^src: src/lib/web-search.ts:96-107, 157-161]; il comando Rust `web_search` (`external_search.rs`) **non è letto**: quali di quelle chiavi usi non è noto (lo strumento dell'agente usa il provider attivo, Firecrawl dal proprio override, tools.rs:392-427, 1729-1746);
- `set_proxy_env` riceve l'URL del proxy con credenziali [^src: src/components/settings/settings-view.tsx:516; src-tauri/src/lib.rs:509-514].
Le funzioni Rust che deserializzano questi oggetti derivano `Debug` (§5).

**Le rotte dell'API non restituiscono valori di configurazione (osservato per le rotte lette)**: `/health` risponde con indicatori (`authRequired`, `authConfigured`, `tokenSource` in `env`/`store`/`none`, `enabled`, `mcpEnabled`, `allowUnauthenticated`, `allowLanAccess`) e **non** con il token [^src: src-tauri/src/api_server.rs:314-330, 639-659]; `projects` restituisce id, nome, percorso, `current` [^src: api_server.rs:755-771]. Le altre risposte (chat, ricerca, file) non sono state rilette per questo scopo.

## 5. Esposizione: log, console, errori, export, telemetria, rete (AC1, AC6)

### 5.1 Log e console

- **Redatto, osservato**: il Rust maschera le credenziali dell'URL del proxy prima di scriverle su stderr (`redact_url`, sostituzione con `***`) e un test verifica che il riepilogo non contenga utente né password [^src: src-tauri/src/proxy.rs:149-175, 446-459]. Il test usa credenziali fittizie, non riportate qui. Anche il log di avvio riporta solo il percorso del file, non il contenuto [^src: src-tauri/src/lib.rs:583] e `set_proxy_env` scrive il riepilogo redatto [^src: lib.rs:509-514].
- **Server API**: gli `eprintln!` letti stampano indirizzo, errori di bind e payload di panic, **non URL, query né header** [^src: src-tauri/src/api_server.rs:102, 123, 129, 141-143, 278]. Il token può arrivare nella query (`?token=`), accettata dal codice [^src: api_server.rs:602-608]; la UI sconsiglia l'uso perché finirebbe in log e cronologia di shell [^src: src/components/settings/sections/api-server-section.tsx:489-493]. Righe 800-2280 e 2540-fine di `api_server.rs` non rilette per questo scopo.
- **Frontend**: `console.error` e `console.warn` letti nelle sezioni salvataggio e API stampano oggetti di errore, non configurazioni [^src: src/components/settings/settings-view.tsx:518, 579; api-server-section.tsx:116, 180, 190, 201, 207].
- **Non verificato**: l'uso di `{:?}`, `dbg!`, `console.log` su oggetti di configurazione in tutto il repo. Osservato che **derivano `Debug`** e contengono la chiave: `LlmConfig` (provider.rs:27), `LlmClient` (84), `SearchEmbeddingConfig` (search.rs:86), `WebSearchConfig` e `WebSearchProviderOverride` (tools.rs:342, 360), `AgentRuntimeConfig` (lib.rs:31; api_server.rs:2355). Se uno di questi fosse stampato con `{:?}`, la chiave finirebbe in stderr (deduzione non testata: nessun punto di stampa visto nelle righe lette).
- Per le CLI: stderr dei processi `claude` è ripetuto su stderr dell'app con prefisso `[claude-cli stderr]` [^src: src-tauri/src/commands/claude_cli.rs:379-387]; è output del CLI, non dell'app.

### 5.2 Messaggi d'errore

- **Header**: gli errori di header personalizzato riportano il **nome** e non il valore [^src: src-tauri/src/agent/provider.rs:693-703].
- **Risposte del provider**: gli errori HTTP riportano il corpo di risposta (LLM) o i primi 200 caratteri (embedding), cioè testo del provider, non la richiesta [^src: provider.rs:359-366, 452-453; search.rs:1264, 1269, 1409-1422]. MinerU riporta il corpo della risposta, non il token [^src: src/lib/mineru.ts:937, 1146, 1153].
- **Chiave di SerpApi nell'URL**: la ricerca SerpApi del backend compone l'URL con il parametro `api_key` nella query e, su errore di rete, formatta il messaggio «Network error reaching SerpApi: {err}» con l'errore di `reqwest` [^src: src-tauri/src/agent/tools.rs:1983-2003]. **Deduzione non testata**: se il `Display` dell'errore di `reqwest` 0.12 (versione dichiarata in Cargo.toml:36) include l'URL della richiesta, la chiave comparirebbe nel messaggio dello strumento; quel messaggio può arrivare agli eventi dell'agente (`ToolEnd.output`, events.rs:18-21; emessi alla UI con `agent-event`, lib.rs:215-221), alla risposta dell'API e, se il risultato dello strumento rientra nel contesto del modello, al provider LLM. Il sorgente di `reqwest` **non è letto**; `redact_for_external_api` toglie solo `previousContent` (events.rs:65-72). Esito: **non conclusivo**.
- **Gli altri provider mettono la chiave negli header, non nell'URL** (osservato): OpenAI e Azure (`Authorization`, `api-key`), Anthropic (`x-api-key` o Bearer), Google (`x-goog-api-key`), embedding (Bearer o `x-goog-api-key`), Tavily nel corpo JSON, Firecrawl Bearer [^src: llm-providers.ts:941-956, 976-998, 1000-1017, 808-821; provider.rs:634-691; search.rs:1371-1377; tools.rs:1729-1746]. Quindi l'URL negli errori non contiene la chiave, salvo credenziali scritte dall'utente nell'endpoint (§1, deduzione). Il messaggio TS «Network error reaching {url}» stampa l'URL del provider [^src: src/lib/llm-client.ts:310]; il ramo `custom` di `getProviderConfig` (llm-providers.ts da 1079) non è letto.

### 5.3 Export dello zip del progetto

- L'esportazione cammina **solo la cartella del progetto** (`WalkDir` sulla radice canonica), senza elenco di esclusioni, e inserisce ogni file [^src: src-tauri/src/commands/project_maintenance.rs:155-190]; il test di andata e ritorno conferma che i file nascosti di `.llm-wiki/` sono inclusi [^src: project_maintenance.rs:53-78].
- Lo store con le chiavi sta in `app_data_dir`, non nel progetto [^src: api_server.rs:740; lib.rs:406, 581-582]: **`app-state.json` non finisce nello zip** (osservato per percorsi). Nello zip finiscono sessioni, chat, cronologia e simili, in cui il codice letto non scrive configurazioni (§2.3). Che **nessun** file di `.llm-wiki/` o di `wiki/`/`raw/` contenga una chiave non è verificato (ricerca globale a carico del chiamante).
- L'archivio può includere segreti che l'utente ha scritto in pagine o sorgenti: fuori perimetro.

### 5.4 Telemetria

- Nessuna dipendenza di telemetria o analytics nei due manifest (Cargo.toml:25-72; package.json:19-60): **osservato per i manifest**. Non si esclude una chiamata di rete implementata con `reqwest` o `fetch` già presenti: il controllo degli aggiornamenti persiste uno stato (`updateCheckState`, project-store.ts:494-514) ma l'indirizzo e il contenuto delle sue richieste **non sono letti**. Esito: nessuna evidenza di telemetria che porti segreti; **non conclusivo** per il resto del codice.

### 5.5 Rete, ambiente e flusso dei segreti

- **API e Clip server in HTTP semplice**: entrambi usano `Server::http` [^src: api_server.rs:138; clip_server.rs:68]. Con `apiConfig.allowLanAccess` il bind diventa `0.0.0.0` [^src: server_bind.rs:22-31, 56-62]: il token viaggia in **chiaro** nell'header `Authorization` (o nella query) sulla rete locale, e il Clip server lo richiede alle richieste non loopback [^src: clip_server.rs:119-134]. Il TLS non è gestito dal codice letto (deduzione: nessuna riga di TLS lato server nei file letti).
- **Proxy con credenziali nell'ambiente di processo**: `HTTP_PROXY` e `HTTPS_PROXY` contengono l'URL intero [^src: proxy.rs:126-127]. Il processo figlio `shell.exec` parte con `env_clear` e una lista bianca che **non** include le variabili del proxy (osservato, tools.rs:1203-1220); il processo `claude` si avvia **senza** `env_clear` (solo `PATH` impostato) e quindi eredita l'ambiente, proxy compreso [^src: claude_cli.rs:298-304] (osservato per l'assenza di `env_clear` nelle righe lette; il modulo codex non è letto). Leggibilità dell'ambiente di un processo da parte di altri processi dello stesso utente: nozione del sistema operativo, non testata.
- **TLS non verificato**: con proxy attivo e `acceptInvalidCerts` vero, i client nativi accettano certificati non validi [^src: proxy.rs:25, 103-106, 145-147; usato da provider.rs:144, tools.rs:1301, search.rs:1224, 1357], quindi le richieste con chiavi passerebbero su TLS non verificato per scelta dell'utente.
- **Verso i provider**: le chiavi vanno solo all'endpoint configurato; per MinerU cloud l'URL base è fisso `https://mineru.net/api/v4` [^src: mineru.ts:8, 102-107] e la versione locale impedisce di seguire reindirizzamenti con le credenziali [^src: mineru.ts:116-128].

### 5.6 Interfaccia: mascheramento del token

- Il campo del token è di tipo `password` con pulsante mostra/nascondi [^src: api-server-section.tsx:389-418].
- Il token reale compare **in chiaro** negli esempi `curl` e nella configurazione MCP mostrati e copiabili, indipendentemente dal pulsante «mostra» [^src: api-server-section.tsx:127-141, 143-165, 518-524, 667-678]. Il testo dell'interfaccia avverte «Keep this token secret» [^src: api-server-section.tsx:479-495].
- Per le chiavi di `llm-provider-section.tsx`, `embedding-section.tsx` e `mineru-section.tsx` il tipo di input (maschera) **non è verificato** in questa sessione.

## 6. Esito proposto e tabella evidenze (AC1, AC6)

**Esito proposto: CONFERMATO per lettura** (le chiavi e i token sono scritti nello store `app-state.json` così come sono, **senza cifratura, offuscamento né archivio protetto** nel codice letto; i lettori Rust li usano in chiaro). Il file con le chiavi **non** è incluso nell'export dello zip del progetto (per percorsi). **NON CONCLUSIVO** per: (a) permessi e protezione del file da parte del plugin e del sistema operativo (§3); (b) se la chiave di SerpApi finisca nei messaggi d'errore (deduzione su `reqwest`, sorgente non letto); (c) l'esistenza di telemetria o altre copie dei segreti (`localStorage`, estensione, file di `.llm-wiki/`) fuori dalle righe lette; (d) il contenuto reale del file (mai aperto, per divieto).

**Precisazioni rispetto alla wiki**: (1) l'elenco è ora per nome e completo per i tipi letti: sei campi `apiKey` (`llmConfig`, `providerConfigs[*]`, `searchApiConfig`, `searchApiConfig.providerConfigs[*]`, `embeddingConfig`, `multimodalConfig`), due token MinerU, un token `apiConfig`, `customHeaders` e `extraHeaders`, `url` del proxy; (2) in più rispetto alla wiki: `extraRequestBody` (corpo libero) e gli URL che possono incorporare credenziali (deduzione), l'ambiente di processo del proxy, `acceptInvalidCerts`, la variabile `LLM_WIKI_API_TOKEN`; (3) la wiki dice «apiKey nei tipi di configurazione LLM, ricerca, embedding e provider non verificata»: **verificata** (tipi letti per intero); (4) i segreti viaggiano anche per IPC dal frontend al Rust, comprese le chiavi di **tutti** i provider di ricerca a ogni ricerca; (5) il profilo per progetto **non** duplica la chiave (osservato).

**Impatto (esposizione) se si verifica (deduzione non testata, non decisione)**: chiunque possa leggere il file dell'utente (altri processi dello stesso account, malware, backup, copia o sincronizzazione del profilo, soprattutto la cartella «Roaming» su Windows) ottiene in un colpo solo le chiavi dei provider LLM, di ricerca e di embedding, i token MinerU, le credenziali del proxy e il token API locale; quest'ultimo dà accesso a chat dell'agente, scrittura di pagine e embedding (sempre con token) e, con `allowUnauthenticated`, alle rotte di lettura. Con `allowLanAccess` il token viaggia in chiaro in HTTP sulla rete locale. Effetti economici (uso a pagamento di chiavi) e di riservatezza dei dati. Le chiavi sono ruotabili dai rispettivi provider. Gravità proposta (non decisione): **alta** per concentrazione e assenza di protezione a riposo, attenuata dal modello di minaccia di un'app desktop locale; da valutare in US-033.

| # | Punto | Esito | Evidenza | Livello |
|---|---|---|---|---|
| 1 | Elenco dei campi sensibili (15 voci + URL e corpo libero) | **CONFERMATO** | wiki-store.ts:27-63, 99-128, 130-164, 200-205, 233-239, 296-331, 338-355 | osservato |
| 2 | Default dei campi sensibili vuoti nello stato iniziale | **CONFERMATO** | wiki-store.ts:504-526, 632-654, 656-672, 676-681, 692-706, 713-719 | osservato |
| 3 | Scritto nello store così com'è | **CONFERMATO** | project-store.ts:53-66, 160-187, 247-250, 264-276, 289-298 | osservato |
| 4 | Cifratura o offuscamento nei punti di scrittura | **SMENTITO** (assenti) | project-store.ts (tabella §2.1); api-token.ts:8-23 | osservato (limitato ai file letti) |
| 5 | Archivio protetto (keychain, stronghold) | **SMENTITO** nelle dipendenze dichiarate | Cargo.toml:25-72; package.json:19-60 | osservato sui manifest; transitive non lette |
| 6 | Lettori Rust usano il segreto in chiaro | **CONFERMATO** | api_server.rs:593-637, 2363-2469; provider.rs:634-691; lib.rs:405-434 | osservato |
| 7 | Plugin store senza serializzatore o cifratura | CONFERMATO lato app; plugin ereditato | lib.rs:558; fetta D store.rs:291-299, lib.rs:333-337 | osservato / ereditato |
| 8 | Permessi del file e protezione di libreria/OS | **NON CONCLUSIVO** | nessuna riga del repo imposta permessi; plugin non riletto | motivo dichiarato (§3) |
| 9 | Proxy: credenziali nell'URL conservate alla lettera | **CONFERMATO** | proxy-config.ts:20-25; proxy.rs:126-127 | osservato |
| 10 | Proxy: credenziali redatte nei log | **CONFERMATO** | proxy.rs:149-175, 446-459; lib.rs:583 | osservato |
| 11 | Proxy: ambiente ereditato da `claude`, non da `shell.exec` | **CONFERMATO** per le righe lette | claude_cli.rs:298-304; tools.rs:1203-1220 | osservato (assenza di `env_clear`) |
| 12 | Profilo per progetto senza `apiKey` e `customHeaders` | **CONFERMATO** | llm-task-routing.ts:33-38; wiki-store.ts:371-383; api_server.rs:2375-2417 | osservato; chiamante non letto |
| 13 | IPC: il TS passa le chiavi al Rust (anche di provider non attivi) | **CONFERMATO** | lib.rs:65-70, 153-158; search.rs:107-115; web-search.ts:96-107, 157-161 | osservato |
| 14 | `app-state.json` nell'export dello zip | **SMENTITO** (per percorsi) | project_maintenance.rs:155-190; api_server.rs:740 | osservato; contenuto di `.llm-wiki/` non verificato |
| 15 | Chiave SerpApi nell'URL | **CONFERMATO** | tools.rs:1983-2003 | osservato |
| 16 | Chiave SerpApi nei messaggi d'errore | **NON CONCLUSIVO** | tools.rs:2003; `reqwest` non letto | deduzione non testata |
| 17 | `/health` e `projects` non restituiscono segreti | **CONFERMATO** | api_server.rs:314-330, 755-771 | osservato (altre rotte non rilette) |
| 18 | Log del server API senza URL né header | **CONFERMATO** per le righe lette | api_server.rs:102, 123, 129, 141-143, 278 | osservato (1-540) |
| 19 | Tipi di config con `Debug` che includono la chiave | **CONFERMATO** (derive) | provider.rs:27, 84; search.rs:86; tools.rs:342, 360; lib.rs:31 | osservato; stampa effettiva non verificata |
| 20 | Token API in HTTP semplice sulla LAN | **CONFERMATO** (assenza di TLS lato server) | api_server.rs:138; clip_server.rs:68; server_bind.rs:22-31 | osservato |
| 21 | Token reale mostrato in chiaro negli esempi copiabili | **CONFERMATO** | api-server-section.tsx:127-141, 143-165, 518-524, 667-678 | osservato |
| 22 | Client MCP legge il token solo da ambiente | **CONFERMATO** | mcp-server/src/api-client.ts:206-207, 386-391 | osservato |
| 23 | Telemetria | **NON CONCLUSIVO** (nessuna dipendenza nei manifest) | Cargo.toml; package.json; project-store.ts:494-514 | osservato sui manifest |
| 24 | `localStorage`, estensione, file di `.llm-wiki/` con copie dei segreti | **NON CONCLUSIVO** | non cercato | stringhe a carico del chiamante |

**Stato proposto del gap `llm-wiki-token-cifratura`**: chiudibile da `wiki-keeper` come **«confermato per lettura: nessuna cifratura né archivio protetto nel codice letto»**, con residui dichiarati (permessi/OS, plugin JS, dipendenze transitive, copie fuori dallo store) se l'utente accetta il «non conclusivo» sui punti 8, 16, 23, 24; altrimenti restano le ricerche globali (§Stringhe) e, per i permessi, un'osservazione in esecuzione (esclusa da Q_003). Il gap `llm-wiki-scan-credenziali` **non è toccato**.

## File letti e non letti

**Repo del cliente, letti in questa sessione (28 file, sola lettura)**:
- `src/stores/wiki-store.ts` (1-756, intero)
- `src/lib/project-store.ts` (1-528, intero)
- `src/lib/api-token.ts` (intero)
- `src/lib/proxy-config.ts` (intero)
- `src/lib/llm-task-routing.ts` (intero)
- `src/lib/llm-providers.ts` (1-450, 560-1079)
- `src/lib/llm-client.ts` (1-419)
- `src/lib/mineru.ts` (intero)
- `src/lib/web-search.ts` (intero)
- `src/components/settings/sections/api-server-section.tsx` (intero)
- `src/components/settings/sections/web-search-section.tsx` (1-260)
- `src/components/settings/settings-view.tsx` (356-665)
- `src-tauri/src/proxy.rs` (intero)
- `src-tauri/src/lib.rs` (intero)
- `src-tauri/src/api_server.rs` (1-799, 2280-2540)
- `src-tauri/src/agent/provider.rs` (1-1099)
- `src-tauri/src/agent/tools.rs` (1-260, 340-430, 1195-1253, 1300-1360, 1725-1785, 1960-2030)
- `src-tauri/src/agent/events.rs` (intero)
- `src-tauri/src/agent/session.rs` (1-190)
- `src-tauri/src/commands/search.rs` (1-130, 1000-1489)
- `src-tauri/src/commands/project_maintenance.rs` (1-210)
- `src-tauri/src/commands/claude_cli.rs` (1-459)
- `src-tauri/src/clip_server.rs` (1-459)
- `src-tauri/src/server_bind.rs` (1-70)
- `src-tauri/Cargo.toml` (intero)
- `src-tauri/capabilities/default.json` (intero)
- `package.json` (intero)
- `mcp-server/src/api-client.ts` (intero)

Letti anche, fuori dall'albero di lavoro: `.git/modules/code_repos/llm_wiki/HEAD` della factory (hash `e08cfce65aad8b76b13546a081c1a8d4422b70c3`). Letti come contesto factory: TSK-026, US-032, dossier r7 (modello), `raw/2026-11-21-repo-llm_wiki-persistenza-d.md` (1-120), `raw/2026-11-21-repo-llm_wiki-agente-tools.md` (intero, per i riferimenti di riga di `tools.rs`, riverificati sul sorgente), `wiki/concepts/llm-wiki-rischi-persistenza.md` (1-207 di 398), `wiki/concepts/llm-wiki-sicurezza.md` (intero), `wiki/gaps.md` (1-339; la voce del gap `llm-wiki-token-cifratura` **non** è in quel tratto: il suo testo è stato desunto da §Aggiornamenti delle due pagine wiki), manifest.

**Non letti, con motivo**:
- `src/components/settings/sections/llm-provider-section.tsx`, `embedding-section.tsx` (lato maschera dei campi), `mineru-section.tsx`, `multimodal-section.tsx`, `network-section.tsx`: tipo di input dei segreti e chiamante di `saveProviderConfigs` non verificati.
- `src/lib/llm-providers.ts` 450-560 e dal ramo `custom` (1079 in poi): dove vada la chiave per gli endpoint personalizzati.
- `src/lib/tauri-fetch.ts` e il lato Rust di `tauri-plugin-http`: come la WebView invii le richieste con gli header.
- `src-tauri/src/commands/external_search.rs` (comando `web_search`), `codex_cli.rs`, `cli_resolver.rs`: se ereditano l'ambiente, come usano la configurazione.
- `src-tauri/src/agent/runtime.rs`, `types.rs`, resto di `api_server.rs` (800-2280, 2540-fine): eventuale stampa di configurazioni, `external_chat_response`.
- `extension/popup.js`, `background.js`, `clipper-core.js`: se l'estensione conserva il token (`chrome.storage`).
- Il sorgente di `reqwest` 0.12, di `tauri-plugin-store` (riletto: solo ereditato dalla fetta D), del pacchetto JS `@tauri-apps/plugin-store`, `Cargo.lock`: dipendenze, non lette.
- `tauri.conf.json` (CSP) non riaperto qui.
- Qualsiasi file `.env*`, `app-state.json` reale, file di credenziali: **non aperti per divieto**.

## Gap evidenti

1. Permessi, ACL e protezione del file di `app-state.json` sui tre sistemi operativi e nei pacchetti sandbox (Flatpak, AppImage, MSIX): non osservabili per lettura.
2. Se `reqwest` 0.12 include l'URL (con `api_key` di SerpApi) nel `Display` degli errori e se quel testo raggiunge UI, API, sessioni o il modello.
3. Dove vada la chiave nel ramo `custom` di `getProviderConfig` e quali campi URL (`customEndpoint`, `baseUrl`, `ollamaUrl`, `endpoint`) accettino credenziali incorporate; tipo di input (maschera) dei campi nelle sezioni delle impostazioni.
4. Copie dei segreti fuori dallo store: `localStorage`, `sessionStorage`, `chrome.storage` dell'estensione, file di `.llm-wiki/` (anche `ingest-warnings.log`), diagnostica.
5. Punti di stampa di configurazioni con `{:?}` o `console.log`, nel codice non letto.
6. Telemetria e richieste di aggiornamento: indirizzo e contenuto non letti.
7. Come e chi compila `ProjectLlmOverride.profile` (il chiamante non è letto) e se `extraRequestBody` sia usato per credenziali nella pratica.
8. `codex_cli.rs`: se il processo figlio eredita l'ambiente con le variabili del proxy come `claude`.
9. Eventuale validazione o rifiuto di credenziali negli URL degli endpoint LLM, embedding e ricerca (solo MinerU locale osservato).

## Stringhe esatte da cercare (ricerca testuale globale, da eseguire dal chiamante)

Cartelle `src/`, `src-tauri/src/`, `src-tauri/capabilities/`, `src-tauri/*.json`, `mcp-server/src/`, `extension/` e, se presenti, `scripts/`, `plans/`, `.github/`; per ciascuna stringa: conteggio e file (e, dove indicato, il contesto di riga **senza copiare valori**). Espressioni larghe, senza distinzione di maiuscole dove utile. Escludere dall'esito qualunque valore letterale che assomigli a una chiave: segnalare solo file e riga.

1. **Nomi dei campi sensibili**: `apiKey`, `api_key`, `apikey`, `API_KEY`, `token`, `localToken`, `local_token`, `secret`, `password`, `passwd`, `credential`, `bearer`, `authorization`, `x-api-key`, `x-goog-api-key`, `api-key`, `X-LLM-Wiki-Token`, `customHeaders`, `custom_headers`, `extraHeaders`, `extra_headers`, `extraRequestBody`, `extra_request_body`, `proxyConfig`, `userinfo`, `username`, `://.*@`
2. **Cifratura, offuscamento, archivio protetto**: `encrypt`, `decrypt`, `cipher`, `aes`, `chacha`, `argon`, `pbkdf`, `scrypt`, `crypto.subtle`, `subtle.`, `keyring`, `keychain`, `stronghold`, `secret-service`, `libsecret`, `credential manager`, `DPAPI`, `safeStorage`, `keytar`, `obfuscat`, `redact`, `scrub`, `mask`, `plugin-stronghold`, `serialize` e `deserialize` accanto a `plugin_store` o `StoreBuilder`
3. **Permessi del file**: `set_permissions`, `PermissionsExt`, `from_mode`, `0o600`, `0o700`, `chmod`, `OpenOptionsExt`, `SetFileAttributes`, `icacls`, `umask`, `mode(`
4. **Log e console**: `console.log`, `console.warn`, `console.error`, `console.debug`, `eprintln!`, `println!`, `dbg!`, `log::`, `tracing::`, `{:?}`, `{:#?}`, `JSON.stringify(`, ciascuno accanto a `config`, `cfg`, `llmConfig`, `embeddingConfig`, `searchApiConfig`, `apiConfig`, `mineruConfig`, `providerConfigs`, `headers`
5. **Messaggi d'errore con URL o query**: `.url()`, `without_url`, `err.url`, `error sending request`, `for url`, `?key=`, `&key=`, `api_key=`, `apiKey=`, `access_token=`, `?token=`, `&token=`, `token=`, `url_encode(key`, `format!(` con `{err}` accanto a `reqwest`, `Network error reaching`
6. **Export e archivi**: `export_project_archive`, `ZipWriter`, `start_file`, `WalkDir::new`, `exclude`, `.llm-wiki`, `app-state`, `app_data_dir`, `appDataDir`, `BaseDirectory.AppData`, `app_config_dir`, `app_local_data_dir`, `JSZip`, `generateAsync`
7. **Telemetria e rete in uscita**: `sentry`, `posthog`, `telemetry`, `analytics`, `mixpanel`, `amplitude`, `gtag`, `crash`, `report`, `fetch(`, `httpFetch(`, `reqwest::`, `.post(`, `.get(`, `api.github.com`, `releases/latest`, `updateCheck`, `check_update`
8. **Lettori dello store**: `app-state.json`, `load_app_state`, `load_agent_app_state`, `read_proxy_config_from_store`, `configured_store_bind_host`, `parsed.get("`, `.get("apiConfig")`, `.get("llmConfig")`, `.get("providerConfigs")`, `.get("searchApiConfig")`, `.get("embeddingConfig")`, `.get("mineruConfig")`, `.get("multimodalConfig")`, `.get("proxyConfig")`, `plugin-store`, `store.get`, `loadLlmConfig`, `loadProviderConfigs`, `loadSearchApiConfig`, `loadEmbeddingConfig`, `loadMultimodalConfig`, `loadMineruConfig`, `loadProxyConfig`, `loadApiConfig`, `getTaskLlmConfig`, `useWikiStore.getState()`
9. **IPC con segreti**: `invoke(`, `invoke<`, `embedding_config`, `llm_config`, `embedding_fetch`, `embedding_fetch_batch`, `search_project`, `web_search`, `set_proxy_env`, `agent_start_turn`, `agent_start_turn_stream`, `claude_cli_spawn`, `codex_cli_spawn`
10. **Ambiente e processi figli**: `LLM_WIKI_API_TOKEN`, `LLM_WIKI_BIND_HOST`, `env::var`, `std::env::var`, `process.env`, `set_var`, `.env(`, `.envs(`, `env_clear`, `Command::new`, `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `NO_PROXY`
11. **Altri archivi lato frontend e estensione**: `localStorage`, `sessionStorage`, `chrome.storage`, `browser.storage`, `indexedDB`, `document.cookie`, `navigator.clipboard`, `writeText(`
12. **Derive che includono segreti**: `derive(` accanto a `Debug` e `Serialize` nei file con `api_key`; `serde_json::to_value(`, `serde_json::to_string(` e `to_string_pretty(` applicati a configurazioni
13. **Capability e CSP**: `store:`, `fs:`, `shell:`, `http:default`, `permissions`, `csp` in `src-tauri/capabilities/*.json` e `src-tauri/tauri*.conf.json`
14. **Input dei segreti nell'interfaccia**: `type="password"`, `type={` accanto a `showKey`, `showToken`, `Eye`, `EyeOff`, `autoComplete`
15. **Credenziali in URL (validazione)**: `username`, `password` accanto a `new URL(`, `parsed.username`, `parsed.password`, `without credentials`, `Url::parse`
16. **Documentazione**: `README`, `plans/`, `docs/` con `token`, `API key`, `secret`, `keychain`, `encrypt`, `plain text`, `plaintext`, `security`

## Note di estrazione

- **Stato**: **partial**. Commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` letto dal file `HEAD` del submodule; HEAD staccato, nessun nome di ramo. Perimetro letto parziale (vedi §Non letti): chiamanti dei salvataggi di `providerConfigs`, ramo `custom`, `external_search.rs`, `codex_cli.rs`, estensione non letti.
- **Gate**: Fase 1 e Fase 4 assolte dall'approvazione dell'utente in chat per il solo perimetro del TSK-026; nessuna conferma separata. Dedup: la voce `2026-11-21-repo-llm_wiki-dossier-ep004-r8` non esisteva nel manifest.
- **Controllo repo invariato**: questo agente non ha `Bash`, quindi **non ha eseguito** `git -C code_repos/llm_wiki status --short` né `git log -1`. Nessuna scrittura sotto `code_repos/llm_wiki`. Il controllo a comando della DoD resta da eseguire dal chiamante.
- **Controllo segreti: 0 valori**. Controllo per lettura dei 28 file elencati. Incontrati solo nomi di campo, nomi di header e di variabili, segnaposto dell'interfaccia (`<your-token>`, «Paste an existing token or click Generate») e, in `proxy.rs`, credenziali **fittizie di test** in URL di prova (righe 450 e dintorni): **non riportate**. Nessuna chiave o token reale incontrati nei file letti; non aperti file `.env*`, `app-state.json` reali, né file di credenziali (neppure della factory). Segreti redatti: 0 (vale per i file letti; **non** è una scansione dell'intero repo, che resta il gap `llm-wiki-scan-credenziali`).
- **Istruzioni trovate nei file letti**: nessuna rivolta a un agente; solo commenti e testi per i manutentori o per gli utenti, non eseguiti.
- **Nessuna scrittura** in `wiki/` né nel kanban.

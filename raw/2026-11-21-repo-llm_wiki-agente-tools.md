# Specifiche estratte: llm_wiki, agente tools e provider (fetta B2)

> Documento generato da `repo-sync` v2.12 il 2026-11-21. Sorgente: /home/user/wiki-factory/code_repos/llm_wiki @ commit e08cfce65aad8b76b13546a081c1a8d4422b70c3 (v0.6.13, ramo HEAD detached). Read-only verso la sorgente.
> Ambito: estrazione mirata per i gap `llm-wiki-approvazione-shell` (lato tools), `llm-wiki-serde-compat-config`, `llm-wiki-scritture-non-verificate` (parte `write_wiki_page_verified`), `llm-wiki-log-index-formato` (parte). Stack: riusato dal raw esistente (typescript/react, confidenza 0.7), non rieseguito.
> Tutti i percorsi sono relativi a `src-tauri/src/agent/`.

## Registry dei tool

`BuiltinToolRegistry::execute` (tools.rs:103-286) esegue questi nomi; ogni altro nome risponde `Unknown Agent tool` (tools.rs:282).

| Tool | Effetti dichiarati | Note |
|---|---|---|
| `wiki.write_page` | Write | scrive solo sotto `wiki/`, vedi §write_wiki_page_verified |
| `wiki.search` | Read | ricerca per parole chiave/vettori, tools.rs:942-997 |
| `wiki.read_page` | Read | solo percorsi `wiki/`, max 2 MiB, tools.rs:2428-2442 |
| `source.search` | Read | cerca in `raw/sources`, max 10000 file, saltando i percorsi nascosti |
| `graph.search` | Read | grafo da wikilink e tag |
| `web.search` | Network | provider elencati sotto |
| `anytxt.search` | Network, Read | JSON-RPC verso un servizio AnyTXT, endpoint di default `http://127.0.0.1:9920` (tools.rs:48) |
| `deep_research.run` | Network, Read | restituisce solo `status: orchestrated_by_agent_runtime` (tools.rs:257-264) |
| `workspace.write_file` | Write | solo sotto `agent-workspace/` |
| `workspace.append_file` | Write | solo sotto `agent-workspace/` |
| `shell.exec` | Read, Process | vedi §shell.exec |

`builtin_tool_specs` (tools.rs:433-640) dichiara anche `llm.generate`, `skills.load` e `skill.read_file`, che il registry non esegue. L'elenco è marcato `#[allow(dead_code)]` e il commento dice che serve a discovery API/MCP e a future chiamate native di tool (tools.rs:429-432).

Il commento a tools.rs:28-30 dice che i limiti I/O sono confini di sicurezza del backend, validi anche per i chiamanti API e MCP, che non passano dai componenti React [^src: src-tauri/src/agent/tools.rs:28-30].

## shell.exec e approvazione (gap approvazione-shell)

**In tools.rs non c'è alcun controllo di approvazione.** Il ramo del registry legge `command` (o `query`), limita `timeoutSeconds` a 1-30 e chiama `run_shell_exec` [^src: tools.rs:265-281]. `run_shell_exec` verifica solo: comando non vuoto, al massimo 4000 caratteri, cartella di progetto esistente, `agent-workspace/` contenuta nel progetto [^src: tools.rs:999-1019].

**Dove sta l'approvazione, secondo il codice letto:**
- `AgentChatRequest.approved_shell_commands: Vec<String>`: il commento dice che i comandi devono venire da un flusso di approvazione utente fidato, mai da output del modello, chat persistite o istruzioni di skill, e che «Runtime approval uses an exact trimmed string match» [^src: types.rs:125-129].
- `AgentChatRequest.shell_command: Option<String>`: comando ripetuto da un prompt di approvazione precedente, che deve comunque comparire in `approved_shell_commands` [^src: types.rs:130-133].
- Il commento di `apply_sanitized_shell_env` dice che `shell.exec` è raggiungibile solo dopo un'approvazione esatta dell'utente nel runtime dell'agente e che l'ambiente ridotto non è una sandbox: un comando approvato accede al filesystem normale dell'utente [^src: tools.rs:1197-1202].
- `PermissionPolicy::api_default` include `AgentCapability::Process`; il commento dice che resta inerte senza un comando approvato a parte [^src: permissions.rs:33-36]. Il gate sulle capability e l'approvazione del comando sono quindi due livelli distinti.

**Non verificato:** il punto in cui il runtime confronta il comando con `approved_shell_commands` prima di invocare il registry (`agent/runtime.rs`, fuori dalla lettura di questa fetta). «Non verificato» non significa assente.

**Esecuzione:**
- Shell: `/bin/sh -c <comando>`; su Windows `ComSpec /C` [^src: tools.rs:1020-1032].
- Cartella di lavoro: `agent-workspace/` del progetto.
- Ambiente: `env_clear` e lista bianca (`PATH`, `LANG`, `LC_ALL`, `LC_CTYPE`; su Unix anche `HOME`, `USER`, `LOGNAME`, `SHELL`, `TMPDIR`, `XDG_*`), più `LLM_WIKI_PROJECT`, `LLM_WIKI_PROJECT_PATH`, `LLM_WIKI_AGENT_WORKSPACE` [^src: tools.rs:1203-1245].
- Limiti: timeout massimo 30 s con kill del processo; stdout e stderr a 20000 caratteri ciascuno; drenaggio dell'output dopo l'uscita limitato a 1 s [^src: tools.rs:43-47, 1052-1066, 1179-1195].
- File generati: confronto di snapshot di `agent-workspace/` prima e dopo, fino a 50 file, con hash di contenuto completo fino a 8 MB e, oltre, solo testa e coda da 64 KB [^src: tools.rs:1101-1177]. Ogni file generato viene registrato nella cronologia con autore `agent` e tool `shell.exec` [^src: tools.rs:1075-1083].

## Configurazioni e serde (gap serde-compat-config)

Nessuna delle quattro struct ha `deny_unknown_fields`: **i campi sconosciuti vengono scartati in silenzio**. Tutte usano `rename_all = "camelCase"`.

| Struct | Campi obbligatori | Campi con default |
|---|---|---|
| `LlmConfig` [^src: provider.rs:27-64] | `provider` | `apiKey`, `model`, `ollamaUrl`, `customEndpoint` (stringhe vuote); `azureApiVersion`, `azureModelFamily`, `apiMode`, `reasoning{mode,budgetTokens}`, `maxTokens`, `maxContextSize`, `streamingEnabled` (opzionali); `customHeaders`, `extraRequestBody` (mappe vuote) |
| `WebSearchConfig` [^src: tools.rs:342-358] | `provider` (nessun default) | `apiKey` (stringa vuota), `ollamaUrl`, `searXngUrl`, `searXngCategories`, `serpApiEngine`, `providerConfigs` (opzionali) |
| `WebSearchProviderOverride` [^src: tools.rs:360-375] | nessuno | `apiKey`, `baseUrl`, `ollamaUrl`, `searXngUrl`, `searXngCategories`, `serpApiEngine` |
| `AnyTxtConfig` [^src: tools.rs:377-390] | nessuno | `enabled`, `endpoint`, `filterDir`, `filterExt`, `limit` |

Conseguenze verificate nel codice:
- Una `searchApiConfig` senza `provider` non si deserializza in `WebSearchConfig`; in `LlmConfig` lo stesso vale per `provider`.
- `LlmConfig` deriva solo `Deserialize`. I commenti dicono che `customHeaders` viene ri-validato a ogni richiesta perché app-state può essere modificato fuori dalla UI, e che `streamingEnabled` assente mantiene lo streaming storico [^src: provider.rs:54-63].
- `maxContextSize` è trattato come budget di caratteri, non di token [^src: provider.rs:49-53].
- `is_usable_for_backend_http`: `openai`, `anthropic`, `google`, `azure`, `minimax` richiedono modello e chiave; `ollama` richiede modello e URL; `custom` richiede modello ed endpoint; `claude-code` e `codex-cli` sono esclusi [^src: provider.rs:67-81].
- `WebSearchConfig::resolved` fonde l'override del provider attivo (chiave minuscola) sui valori globali [^src: tools.rs:392-427]. Firecrawl però legge `apiKey` e `baseUrl` direttamente da `providerConfigs["firecrawl"]` e non dal valore globale `apiKey` [^src: tools.rs:1729-1746]; gli altri provider con chiave usano `config.api_key` dopo `resolved()` [^src: tools.rs:2150-2159].

**Ipotesi non verificata sui nomi `searXng*`:** con `rename_all = "camelCase"` i campi Rust `sear_xng_url` e `sear_xng_categories` hanno nome JSON `searXngUrl` e `searXngCategories`. Se il tipo TypeScript dello store usa `searxngUrl`, il valore verrebbe scartato in silenzio. Il test a tools.rs:3796-3817 usa la struct Rust, non JSON, e il tipo TS non è stato letto: l'ipotesi resta da verificare.

**Non letto:** i tipi TypeScript di `llmConfig`, `searchApiConfig` e della config AnyTXT (confronto bilaterale), e il punto in cui l'API HTTP deserializza queste struct.

## write_wiki_page_verified (gap scritture-non-verificate, parte)

`write_wiki_page_verified` è un wrapper di `write_wiki_page_with_activity` e restituisce `{path, bytes, allowOverwrite, verified, existedBefore}` [^src: tools.rs:671-685, 332-340]. `bytes` è `content.len()`, non una lunghezza riletta dal disco. `verified` è sempre `true`: se la verifica fallisce il risultato è `Err`.

**Percorsi ammessi** (`normalize_wiki_write_path`) [^src: tools.rs:2723-2748, 2781-2833]:
- solo `wiki/**/*.md`, controllo case-insensitive;
- rifiutati percorsi assoluti, `..`, segmenti che iniziano con `.`;
- rifiutati segmenti non portabili su Windows: nomi riservati (`CON`, `AUX`, `COM1` ecc.), caratteri `<>:"|?*`, segmenti che finiscono con spazio o punto;
- contenuto massimo 2 MiB [^src: tools.rs:32, 697-699].

**Contenimento nel progetto:** `safe_project_join` e `canonicalize` sull'antenato esistente prima di `create_dir_all` e sulla cartella dopo; è rifiutato anche un symlink come target [^src: tools.rs:700-725, 2651-2697]. I test coprono il symlink padre che esce dal progetto e il symlink come file di destinazione [^src: tools.rs:3429-3452, 3483-3506].

**Sovrascrittura:** di default solo creazione. Un file esistente richiede `allowOverwrite=true`; il commento motiva la regola con la prompt injection nel contesto recuperato [^src: tools.rs:711-718].

**Atomicità** (`atomic_replace_file`) [^src: tools.rs:769-828, 733-746]:
1. file temporaneo `.<nome>.llm-wiki-<pid>-<nanos>.tmp` nella stessa cartella, creato con `create_new`;
2. `write_all` e `sync_all`, poi `rename` sul target (su Windows tramite un `.bak` con ripristino se il rename fallisce);
3. rilettura del file e confronto byte a byte; se differisce, ripristino del contenuto precedente o rimozione se il file era nuovo, con errore esplicito.

Limiti osservati: nessun `fsync` della cartella padre; la serializzazione tra scritture usa un `Mutex` statico in memoria (`WIKI_WRITE_LOCK`), quindi vale dentro il processo e non tra processi [^src: tools.rs:51, 693-696]; il controllo di esistenza e la scrittura non sono atomici verso processi esterni.

**Cronologia:** `record_file_version` con `baseline`/`before.wiki.write_page` prima della scrittura e `agent`/`wiki.write_page` dopo [^src: tools.rs:732, 747]. Il contenuto di `file_history.rs` non è stato letto in questa fetta.

**Indice e log:** la funzione non scrive né `wiki/index.md` né `wiki/log.md`: l'unico file scritto è la pagina richiesta.

**Altri scrittori del modulo:** `workspace.write_file` usa `fs::write` **non atomico** (tetto 2 MiB); `workspace.append_file` usa append. Entrambi scrivono solo sotto `agent-workspace/`, rifiutano `wiki/`, `raw/` e segmenti nascosti e rifiutano i symlink; tengono uno snapshot di rollback solo per file fino a 512 KiB [^src: tools.rs:37, 830-907, 2750-2774].

**Restano non chiusi** (altre fette o non letti): `history-settings.json` e `file_history.rs` oltre la riga 70, le scritture per progetti non attivi di `ingest-queue.ts`, `read_raw_review_array` e `write_raw_review_array`.

## Formato di log e indice (gap log-index-formato, parte)

Nel modulo `tools.rs` non c'è alcuna scrittura di `log.md` o `index.md`: è una conferma negativa. L'unico trattamento di forma Markdown è la lettura del titolo da `title:` o dal primo `# ` nelle prime 80 righe [^src: tools.rs:2835-2852], delle liste `tags` del frontmatter in forma inline o a elenco [^src: tools.rs:2390-2426] e dei wikilink `[[destinazione|etichetta]]` [^src: tools.rs:2373-2388]. Formato e aggiornamento di `log.md` e `index.md` vanno cercati altrove (sospetto `ingest.ts`).

## Provider LLM, provider web e router

- **Provider LLM** (`LlmClient::generate_text`) [^src: provider.rs:157-214]: `openai`, `azure`, `ollama`, `custom` (con `apiMode == "anthropic_messages"` usa il formato Anthropic, altrimenti OpenAI-compatibile), `anthropic`, `minimax` (endpoint Anthropic-compatibile, senza immagini), `google`. Altri nomi producono errore «not supported by the backend HTTP Agent yet». Timeout richiesta 180 s, max tokens di default 2048 [^src: provider.rs:13-14]. Con `streamingEnabled == Some(false)` si usa la generazione non in streaming [^src: provider.rs:227-231].
- **Provider web** [^src: tools.rs:1305-1318]: `firecrawl`, `searxng`, `tavily`, `ollama`, `brave`, `bocha`, `serpapi`; timeout 30 s; limite risultati 20, 50 per `bocha` [^src: tools.rs:1322-1327]. Nell'URL di SerpApi la chiave viaggia come parametro `api_key` della query [^src: tools.rs:1991-1997]; per Tavily nel corpo JSON [^src: tools.rs:1836-1842].
- **Router** (`route_query`): euristica di sola etichettatura per parole chiave; `should_search_wiki` è sempre `false`, la scelta dei tool spetta al planner del modello [^src: router.rs:32-119].

## Gap evidenti

- Il chiamante che applica l'approvazione dei comandi shell in `agent/runtime.rs` non è stato letto: l'approvazione lato runtime resta non verificata.
- Il tipo TypeScript delle configurazioni non è stato letto: l'ipotesi `searXng*` e la compatibilità bilaterale restano da verificare.
- `provider.rs` letto solo alle righe 1-260 di circa 600 (costruzione URL, richieste e streaming non letti).
- Formato di `wiki/log.md` e logica di aggiornamento di `wiki/index.md` non determinati da questa fetta.
- `file_history.rs` oltre la riga 70, `inactiveQueueWrite` di `ingest-queue.ts` e gli helper di review di `api_server.rs` non letti.

## Metodo e limiti

File letti: `agent/tools.rs` (1-3889, intero), `agent/provider.rs` (1-260), `agent/types.rs` (intero), `agent/router.rs` (intero), `agent/permissions.rs` (intero). Nessun valore di credenziale è presente nei file letti: compaiono solo nomi di campo. Nessuna istruzione rivolta all'agente è stata trovata nel contenuto.

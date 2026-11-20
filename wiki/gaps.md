---
type: gap
status: draft
created: 2026-11-20
updated: 2026-11-20
append_only: true
---

# Gaps — informazioni assenti in wiki/

File append-only: le informazioni che servono e la wiki non ha. Formato e chiusura dei gap: skill `wiki-gap-protocol`.

## 2026-11-20 15:31 — llm-wiki-codice-non-letto
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** la logica di business non è stata letta: `src/lib/ingest.ts` oltre la riga 70, `src-tauri/src/agent/runtime.rs`, `src-tauri/src/agent/tools.rs`, `src-tauri/src/api_server.rs`, `src-tauri/src/commands/fs.rs` (tutti oltre 50 KB) e le righe 201-479 di `src-tauri/src/lib.rs`. Il fan-in dei moduli core è una stima debole su 30 file. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (nuova estrazione `repo-sync` che copra i file indicati). Non bloccante.
**Impatto:** le pagine [[llm-wiki-agente]], [[llm-wiki-struttura-e-moduli]] e [[llm-wiki-api-locale]] descrivono questi moduli solo per nome.

## 2026-11-20 15:31 — llm-wiki-contratto-api-http
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** il contratto esatto dell'API HTTP locale non è noto: la README è l'unica fonte degli endpoint, `api_server.rs` e `mcp-server/src/api-client.ts` non sono stati letti. Gli endpoint HTTP corrispondenti a scrittura pagina ed embedding non sono verificati, e l'elenco endpoint della README non cita una scrittura pagina. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `api_server.rs` e `api-client.ts`). Non bloccante.
**Impatto:** [[llm-wiki-api-locale]] riporta gli endpoint solo come dichiarati in README.

## 2026-11-20 15:31 — llm-wiki-api-lan-auth
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** non è noto dove vengano usati `server_bind` e `cors` né quale autenticazione si applichi quando il server ascolta fuori dal loopback. La README descrive l'API come `127.0.0.1`-only e protetta da token, il codice prevede l'ascolto su LAN opzionale: documentazione e comportamento divergono, oppure ci sono vincoli aggiuntivi non letti. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `api_server.rs` e dei punti d'uso di `server_bind` e `cors`). Non bloccante.
**Impatto:** [[llm-wiki-sicurezza]] e [[llm-wiki-api-locale]] non possono dire quale protezione valga fuori dal loopback.

## 2026-11-20 15:31 — llm-wiki-mcp-readme-vs-codice
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** il README di `mcp-server` elenca 10 strumenti e il codice ne registra 12 (`llm_wiki_embed_page` e `llm_wiki_write_page` non documentati); il suo paragrafo di sicurezza parla solo di letture e non cita la scrittura di pagine. Non è chiaro se sia il README a essere indietro o se esistano vincoli non letti. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (confronto con `api_server.rs`, non letto). Non bloccante.
**Impatto:** [[llm-wiki-mcp-server]] riporta entrambe le versioni senza scegliere.

## 2026-11-20 15:31 — llm-wiki-approvazione-shell
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** il punto in cui viene applicata l'approvazione dei comandi shell non è verificato. La README dice «external shell commands still require explicit approval»; `agent/permissions.rs` implementa solo il gate sulle capability, e la policy `api_default` include `Process`. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `agent/runtime.rs` e `agent/tools.rs`). Non bloccante.
**Impatto:** [[llm-wiki-agente]] e [[llm-wiki-sicurezza]] non possono confermare il controllo sui comandi shell.

## 2026-11-20 15:31 — llm-wiki-i18n-lingue
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** la README dice «English + Chinese» per l'i18n, ma in `src/i18n/` esistono `en.json`, `it.json`, `ru.json`, `zh.json`. Non è noto quali lingue siano effettivamente supportate dall'interfaccia. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `src/i18n/` e della selezione lingua). Non bloccante.
**Impatto:** [[llm-wiki-app]] riporta la divergenza senza risolverla.

## 2026-11-20 15:31 — llm-wiki-autore-nash-su-yong-su
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** la README cita nash_su come creatore e manutentore, l'intestazione di `LICENSE` riporta «Copyright (C) 2024-2026 Yong Su». La relazione tra i due nomi non è verificabile dal sampling. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw. Non bloccante.
**Impatto:** [[llm-wiki-app]] e [[llm-wiki-licenza-e-standard]] riportano i due nomi senza metterli in relazione.

## 2026-11-20 15:31 — llm-wiki-licenza-mcp-server
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** `mcp-server/package.json` dichiara `"license": "MIT"`, diversa dalla GPL v3 della radice. Il raw la segnala come anomalia da verificare. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw. Non bloccante.
**Impatto:** [[llm-wiki-licenza-e-standard]] e [[llm-wiki-mcp-server]] riportano entrambe le licenze senza dire quale prevalga.

## 2026-11-20 15:31 — llm-wiki-multimodale-stato
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** `plans/multimodal-images.md` ha stato «Spec, not started», mentre la README descrive come già presente l'ingest multimodale. Lo stato reale va verificato sul codice. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `src/lib/ingest.ts` e dei moduli `extract_images`). Non bloccante.
**Impatto:** [[llm-wiki-app]] e [[llm-wiki-schema-dati]] riportano lo schema multimodale come da verificare.

## 2026-11-20 15:31 — llm-wiki-ci-test-build
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** la CI (`ci.yml`) non esegue i test e il workflow `build.yml` non è stato letto. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `.github/workflows/build.yml`). Non bloccante.
**Impatto:** [[llm-wiki-test-e-ci]] non descrive il workflow di build.

## 2026-11-20 15:31 — llm-wiki-requisiti-funzionali
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** requisiti funzionali e regole di dominio sono derivabili solo dalla README e non sono confermati dal codice letto. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura della logica di business, vedi `llm-wiki-codice-non-letto`). Non bloccante.
**Impatto:** [[llm-wiki-app]] elenca le funzioni solo come «dichiarate in README».

## 2026-11-20 15:31 — llm-wiki-scan-credenziali
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** nessuna scansione dei sorgenti non aperti alla ricerca di credenziali hardcoded: lo zero di secret redatti vale solo per i 30 file letti e per la ricerca dei nomi file. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (scansione testuale dei sorgenti). Non bloccante.
**Impatto:** [[llm-wiki-sicurezza]] e [[2026-11-20-repo-llm_wiki]] non possono affermare l'assenza di credenziali nel repository.

## 2026-11-20 17:06 — llm-wiki-persistenza-codice-non-letto
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki (aggiornamento v2026-11-20)
**Gap:** codice che incide sulla persistenza e non è stato letto. `src-tauri/src/commands/file_sync.rs` (70 KB): sincronizzazione e watcher dei file, non si sa se persista stato. Rust: `src-tauri/src/commands/fs.rs` (atomicità di `write_file` e `writeFileAtomic`, cancellazioni), `search.rs` (`embedding_fetch`, `SearchEmbeddingConfig`), `api_server.rs` (lettura di `apiConfig`, endpoint che scrivono), `agent/runtime.rs` (chi chiama `append_turn` e con quali id di sessione), `proxy.rs`, `lib.rs` oltre le parti già lette. TS: `src/stores/wiki-store.ts` (tipi di tutte le configurazioni, compresi i campi segreti), `lint-store.ts`, `dedup-queue.ts` (persistenza della coda dedup), `wiki-page-delete.ts` (cascata di cancellazione), `source-lifecycle.ts`, `ingest.ts` (scrittura di `ingest-cache` e della cache delle didascalie), `chat-panel.tsx` (cancellazione dei file chat), `sweep-reviews.ts`, `src/commands/fs.ts`. Si sovrappone in parte al gap `llm-wiki-codice-non-letto` (`fs.rs`, `api_server.rs`, `runtime.rs`, `lib.rs`, `ingest.ts`). Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (nuova estrazione `repo-sync` che copra i file indicati). Non bloccante.
**Impatto:** [[llm-wiki-archivi-persistenza]], [[llm-wiki-operazioni-distruttive]] e [[llm-wiki-rischi-persistenza]] non possono confermare atomicità, chiamanti e cancellazioni nei file non letti.

## 2026-11-20 17:06 — llm-wiki-file-citati-non-verificati
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki (aggiornamento v2026-11-20)
**Gap:** file e cartelle citati nei commenti del codice ma non verificati: `image-caption-cache.json`, `lexical-graph.json` (commento di `dedup-storage.ts`), la cartella `raw/sources/.cache` e la cartella legacy `.llm-wiki-imported`. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `ingest.ts`, `dedup-storage.ts` e dei punti d'uso). Non bloccante.
**Impatto:** [[llm-wiki-archivi-persistenza]] elenca 17 archivi senza questi file, di cui non è noto se esistano come archivi.

## 2026-11-20 17:06 — llm-wiki-app-state-percorso
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki (aggiornamento v2026-11-20)
**Gap:** il percorso effettivo di `app-state.json` e il comportamento del plugin store su file corrotto non sono determinabili dal campione. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (configurazione del plugin store in `lib.rs` e documentazione del plugin). Non bloccante.
**Impatto:** [[llm-wiki-archivi-persistenza]] e [[llm-wiki-gestione-file-corrotti]] non possono dire dove sia lo store né come reagisca a un file corrotto.

## 2026-11-20 17:06 — llm-wiki-creazione-cartella-dati
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki (aggiornamento v2026-11-20)
**Gap:** non è noto chi crei `.llm-wiki/` per un progetto importato o aperto da disco: `create_project` non la crea e `open_project` non la richiede. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `persist.ts` nei punti d'uso e dei flussi di apertura progetto non letti). Non bloccante.
**Impatto:** [[llm-wiki-schema-dati]] e [[llm-wiki-archivi-persistenza]] non possono descrivere il ciclo di vita della cartella dati.

## 2026-11-20 17:06 — llm-wiki-vector-v1-chiamanti
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki (aggiornamento v2026-11-20)
**Gap:** nessun chiamante di `vector_upsert` e `vector_delete` (v1) nel campione: non è chiaro se i percorsi v1 siano ancora usati. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura dei chiamanti dei comandi Tauri, ad esempio in `lib.rs`). Non bloccante.
**Impatto:** [[llm-wiki-versioni-e-migrazioni]] e [[llm-wiki-operazioni-distruttive]] non possono dire se il v1 sia ancora scritto.

## 2026-11-20 17:06 — llm-wiki-log-index-formato
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki (aggiornamento v2026-11-20)
**Gap:** formato di `wiki/log.md` e logica di aggiornamento di `wiki/index.md` oltre `rebuild_wiki_index`: non analizzati. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura della logica di ingest e dei comandi di scrittura di log e indice). Non bloccante.
**Impatto:** [[llm-wiki-schema-dati]] non descrive il formato dei file `log.md` e `index.md` del progetto wiki.

## 2026-11-20 17:06 — llm-wiki-archivi-dimensioni
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki (aggiornamento v2026-11-20)
**Gap:** nessun dato su dimensioni reali, prestazioni o crescita degli archivi. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (misure su progetti reali; non ricavabile dal solo codice). Non bloccante.
**Impatto:** [[llm-wiki-archivi-persistenza]] non può stimare la crescita dei file.

## 2026-11-20 17:06 — llm-wiki-embedding-cambio-modello
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki (aggiornamento v2026-11-20)
**Gap:** la dimensione del vettore è fissata dal primo chunk di una scrittura (`vector_upsert_chunks_inner`) e nel campione non c'è una verifica esplicita di coerenza con la tabella esistente; la gestione di un cambio di modello o di dimensione dell'embedding sembra affidata al re-index (l'impronta di revisione include il modello). Il raw la segna «Da verificare». Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Divergenze e rischi.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `search.rs`, dei punti d'uso di `embeddingConfig` e della UI Settings → Embedding). Non bloccante.
**Impatto:** [[llm-wiki-rischi-persistenza]] riporta il punto come deduzione da verificare.

## 2026-11-20 17:25 — master-difetti-impatto-priorita
**Origine:** product-manager @ EP-001
**Gap:** [[master-difetti-rilevati]] non contiene un'analisi di impatto né una priorità per gli 11 difetti del master: il documento di sessione elenca sintomo ed evidenza dichiarata, non conseguenze né gravità. Le priorità di US-001..US-011 sono quindi una proposta del product-manager basata sul solo sintomo dichiarato (high 1, 3, 7; medium 2, 4, 8, 9; low 5, 6, 10, 11), confermata dall'utente il 2026-11-20.
**Sospetta fonte:** nessuna fonte chiara, serve input dell'utente o nuovo raw di sessione. Non bloccante.
**Impatto:** la priorità di EP-001 e delle sue storie resta provvisoria finché non c'è un'analisi di impatto.

## 2026-11-20 17:53 — master-difetto-12-target-auto-derive
**Origine:** product-manager su segnalazione del tpm @ EP-001 (US-034)
**Gap:** ipotesi di difetto del master, non ancora in wiki e non riprodotta. Nel dev-protocol del master, fase 0 «gate steps», Caso B (multi-repo), passo 3, se un TSK non ha `target:` e una sola entry di `code_paths` lista il layer del TSK, il target è derivato automaticamente da quella entry e si procede [^code: .claude/skills/references/dev-protocol/fase-0-gate-steps.md:27-29]. Il testo è stato letto sulla copia locale della factory, non sul master. In una factory con un solo `code_path` cliente che lista i layer `docs` e `db`, un TSK `docs` o `db` che riguarda lavoro interno alla factory, con `consumer: agent`, verrebbe quindi risolto sul repository del cliente. Stato: **ipotesi dal testo del protocollo, non riprodotta**. Workaround in uso, dichiarato dal tpm: override `consumer: human` sui TSK dello sprint 01. La priorità è coperta dal gap `master-difetti-impatto-priorita`.
**Sospetta fonte:** nessuna fonte chiara, serve un report di verifica su caso neutro (US-034) da ingerire. Non bloccante.
**Impatto:** US-034 e la segnalazione al master: un TSK interno alla factory potrebbe essere preso da un dev-agent sul repository del cliente, che ha una politica anti-traccia AI e vincoli sulle modifiche.

## 2026-11-20 18:23 — llm-wiki-archivi-sommario-conteggi
**Origine:** lead-architect @ TSK-010 (indice di `design_&_architecture/db_schemas/`)
**Gap:** il sommario di [[llm-wiki-archivi-persistenza]] dice «17 archivi per progetto in `.llm-wiki/` più lo store `app-state.json`», ma la tabella §Inventario ha 17 righe con `app-state.json` compreso: 16 archivi per progetto, 17 solo contando la riga Chat come due file (`conversations.json` e `chats/<id>.json`). Lo stesso sommario dice che è dichiarata in modo esplicito una sola versione di formato, mentre [[llm-wiki-versioni-e-migrazioni]] e [[llm-wiki-schema-dati]] ne contano due (`version: 1` e il suffisso `_v2`). Il conteggio «17 più lo store» è ripreso da EP-003, US-019 e TSK-010. Inoltre il formato legacy `chat-history.json`, letto da `loadChatHistory` secondo [[llm-wiki-versioni-e-migrazioni]], non compare nell'inventario e la wiki non ne riporta la posizione.
**Sospetta fonte:** raw/2026-11-20-repo-llm_wiki.md §Inventario degli archivi (presente, già ingerito): verificare il criterio di conteggio e la posizione di `chat-history.json`. Non bloccante.
**Impatto:** l'indice `design_&_architecture/db_schemas/README.md` segue la tabella riga per riga (16 per progetto più lo store, decisione dell'utente del 2026-11-20) e non conferma il totale della metrica di EP-003 («17 più lo store»); US-024 eredita il conteggio delle versioni.

## 2026-11-20 18:23 — llm-wiki-id-chat-sessione
**Origine:** lead-architect @ TSK-010 (indice di `design_&_architecture/db_schemas/`)
**Gap:** la wiki non dice come si genera l'id di una conversazione chat (nome di `chats/<id>.json`, `conversationId` dei messaggi), da dove arriva il `sessionId` delle sessioni agente né quale regola di sanitizzazione gli si applica, se una conversazione chat e una sessione agente condividano un identificativo, e se il `projectId` delle sessioni agente coincida con l'`id` di `project.json`.
**Sospetta fonte:** raw/2026-11-20-repo-llm_wiki.md (presente: verificare se riporta la generazione degli id in `chat-store.ts` e `agent/session.rs`); per i chiamanti di `append_turn` serve nuovo raw (`agent/runtime.rs`, già nel gap `llm-wiki-persistenza-codice-non-letto`). Non bloccante.
**Impatto:** l'indice di `db_schemas/` (identificatori I1, I8, I9; relazioni R3, R9) e la scheda di US-022 marcano questi punti «non verificato».

## 2026-11-20 18:23 — llm-wiki-riferimenti-incrociati
**Origine:** lead-architect @ TSK-010 (indice di `design_&_architecture/db_schemas/`)
**Gap:** non è documentata la forma dei riferimenti fra archivi. Pagine: `affectedPages` di `review.json`, gli slug di `dedup-not-duplicates.json`, `ignorePages` di `lint-config.json`, `filesWritten` di `ingest-cache.json`, rispetto all'id di pagina v2 (percorso relativo sotto `wiki/` senza `.md`). Sorgenti: `sourcePath` di `ingest-queue.json` (relativo) e di `review.json`, il «nome sorgente» che indicizza `ingest-cache.json`, le chiavi di `files` in `scheduled-import-db.json`. Percorsi: la base del percorso relativo della cronologia; la forma del percorso di progetto in `projectRegistry`, `recentProjects`, `lastProject` e nella chiave `scheduledImportConfig:<percorso>`; come la chiave `default` di `sourceWatchConfig` e `projectFileSyncEnabled` conviva con le chiavi per id progetto. Hash: la codifica di `sha256(page_id)` nei nomi `.revision` e dell'hash FNV-1a nei nomi dei file di cronologia.
**Sospetta fonte:** raw/2026-11-20-repo-llm_wiki.md (presente: verificare se lo riporta); altrimenti nuovo raw (`review-store.ts`, `dedup-storage.ts`, `lint-config.ts`, `ingest-cache.ts`, `ingest-queue.ts`, `scheduled-import.ts`, `project-store.ts`, `page_embedding.rs`, `file_history.rs`). Non bloccante.
**Impatto:** l'indice di `db_schemas/` non può dire quali archivi condividano davvero l'id di pagina o il riferimento a sorgente: le relazioni R2 (in parte), R12 e R13 e gli identificatori I2, I6, I7, I10, I11 restano «non verificato».

## 2026-11-20 21:12 — llm-wiki-import-id-duplicato
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki-persistenza-a
**Gap:** dopo l'importazione di un archivio non è noto cosa accada se l'id in `.llm-wiki/project.json`, ripristinato dallo zip, coincide con uno già presente in `projectRegistry` o `recentProjects` (collisione, sovrascrittura o duplicato). Il flusso `import_project_archive`, `openProject` e `addToRecentProjects` è letto fino al chiamante UI, non oltre. Fonte del gap: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Punto 1: caso «importato».
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `project-identity.ts`, in particolare `upsertProjectInfo`, e del flusso di apertura progetto). Non bloccante.
**Impatto:** [[llm-wiki-archivi-persistenza]] e [[llm-wiki-operazioni-distruttive]] non possono descrivere l'esito dell'importazione; tocca i rischi 2 e 3 di [[llm-wiki-rischi-persistenza]].

## 2026-11-20 21:12 — llm-wiki-serde-compat-config
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki-persistenza-a
**Gap:** non è verificata la compatibilità serde tra `llmConfig` dello store e `agent::provider::LlmConfig`, né tra `searchApiConfig` e le struct `WebSearchConfig` e `AnyTxtConfig` (`agent/provider.rs` e `agent/tools.rs` non letti): non si sa se campi opzionali o sconosciuti vengano scartati in silenzio. Fonte del gap: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `agent/provider.rs` e `agent/tools.rs`). Non bloccante.
**Impatto:** [[llm-wiki-schema-dati]] e [[llm-wiki-agente]] non possono dire quali campi della configurazione arrivino davvero al runtime.

## 2026-11-20 21:12 — llm-wiki-embedding-trasporto
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki-persistenza-a
**Gap:** il trasporto effettivo dell'embedding non è letto: `fetch_embedding_once` e `fetch_embedding_batch` (`search.rs` oltre la riga 1200), l'uso della chiave API e l'uso di `SEARCH_EMBEDDING_TIMEOUT_SECS` (valore 8, uso non nel campione). Sottodomanda del gap `llm-wiki-persistenza-codice-non-letto`, tenuta a parte per l'impatto sulla sicurezza. Fonte del gap: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `search.rs` dalla riga 1201). Non bloccante.
**Impatto:** [[llm-wiki-sicurezza]] non può dire dove e come viaggia la chiave API dell'embedding; tocca il rischio 8 di [[llm-wiki-rischi-persistenza]].

## 2026-11-20 21:12 — llm-wiki-ui-salvataggio-impostazioni
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki-persistenza-a
**Gap:** il raw colloca nel salvataggio delle impostazioni (`settings-view.tsx`, finestra 505-540) solo proxy, API, MinerU e import pianificato; dove e come la UI salva le altre chiavi (`llmConfig`, `providerConfigs`, `searchApiConfig`, `embeddingConfig`, `multimodalConfig`, `generalConfig`) non è letto, così come il salvataggio effettivo della sezione embedding. Fonte del gap: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Punto 9: quando la UI invoca `set_proxy_env` e il reload.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `settings-view.tsx` fuori dalla finestra e di `embedding-section.tsx` dalla riga 201). Non bloccante.
**Impatto:** [[llm-wiki-archivi-persistenza]] non può dire quando una modifica alle altre chiavi è scritta su disco, oltre al salvataggio automatico con debounce.

## 2026-11-20 21:12 — llm-wiki-scritture-non-verificate
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki-persistenza-b (accorpa punti delle fette B e C)
**Gap:** il meccanismo di scrittura di alcuni archivi o scrittori non è verificato: `history-settings.json` (di `file_history.rs` sono lette solo le righe 1-70), le scritture per progetti non attivi di `ingest-queue.ts` (`inactiveQueueWrite`, file letto solo in parte), `write_wiki_page_verified` (`agent/tools.rs`: cartelle ammesse, atomicità, aggiornamento di indice e log) e `read_raw_review_array` e `write_raw_review_array` (senza i quali non si può dire se l'auto-save possa sovrascrivere le modifiche fatte alle review via API). Fonte del gap: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Atomicità per archivio, §Gap evidenti; raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (`file_history.rs` oltre la riga 70, `ingest-queue.ts`, `agent/tools.rs`, `api_server.rs` per i due helper di review). Non bloccante.
**Impatto:** [[llm-wiki-archivi-persistenza]], [[llm-wiki-api-locale]] e [[llm-wiki-rischi-persistenza]] non possono dire con quale atomicità siano scritti questi archivi; tocca il rischio 4.

## 2026-11-20 21:12 — llm-wiki-chiamanti-non-verificati
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki-persistenza-c (accorpa punti delle fette B e C)
**Gap:** restano chiamanti non verificati o non classificati: l'elenco completo dei chiamanti di `writeFileAtomic` (da graphify a profondità 1, non da ricerca testuale), i chiamanti dei wrapper `copyFile` e `copyDirectory` (`fs.ts:98` e `:105`), il chiamante di `optimizeChunkVectorTableBestEffort`, le stringhe non classificate (`embedding.ts:705`, `:731`, `:745`, `auto-save.ts:12`, `:28`), i corpi di `removeTasks` e `cancelAllTasks`; inoltre `cleanupWrittenFiles` e `clearCompletedTasks` non hanno chiamanti nell'ambito cercato, mentre i commenti dei sorgenti li descrivono come usati: non è noto se siano codice morto o chiamati da fuori ambito (`mcp-server`, `extension`, `scripts`, test) o per nome dinamico. Fonte del gap: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Gap evidenti, §Contraddizioni con la wiki; raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Punto 2: `writeFileAtomic` e il markdown estratto.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (ricerca testuale e lettura dei punti indicati, comprese le cartelle fuori ambito). Non bloccante.
**Impatto:** [[llm-wiki-operazioni-distruttive]] resta con righe «chiamante non verificato» (`copy_file`, `copy_directory`, `vector_optimize_chunks`) e con due operazioni «senza chiamanti nell'ambito cercato».

## 2026-11-20 21:12 — llm-wiki-tipi-dedup-lint
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki-persistenza-b
**Gap:** il tipo `DuplicateGroup` (`dedup.ts`) e i valori ammessi di `type` e `severity` di `LintResult` (`lint.ts`) non sono letti: il campo `group` di `dedup-queue.json` e `type` e `severity` di `lint.json` restano non descritti. Fonte del gap: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Coda di dedup e lint.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `dedup.ts` e `lint.ts`). Non bloccante.
**Impatto:** [[llm-wiki-schema-dati]] e [[llm-wiki-archivi-persistenza]] non possono descrivere per intero i campi di `dedup-queue.json` e `lint.json`.

## 2026-11-20 21:12 — llm-wiki-markdown-estratto-percorsi
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki-persistenza-b (accorpa due punti della fetta B)
**Gap:** per le immagini MinerU, `mineruAssetRelPath` non è letta e la cartella assoluta `mediaDir` non è nella finestra letta di `mineru.ts`: che le immagini vadano sotto `wiki/media/` è una deduzione dal prefisso. Per il markdown estratto in `raw/parsed`, il legame tra l'opzione di disattivazione (commento a `parsed-source-output.ts:80`) e `persistExtractedMarkdown` è solo dedotto; default e punto di lettura non sono verificati. Fonte del gap: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Punto 3: immagini MinerU; §Punto 2: `writeFileAtomic` e il markdown estratto.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `mineruAssetRelPath` e di `mineru.ts` fuori dalle finestre, dei punti di lettura dell'opzione). Non bloccante.
**Impatto:** [[llm-wiki-archivi-persistenza]] non può confermare la posizione delle immagini MinerU né il default della copia in `raw/parsed`.

## 2026-11-20 21:12 — llm-wiki-cancellazione-controlli-confine
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki-persistenza-c
**Gap:** non è noto se `delete_file` controlli che il percorso sia dentro il progetto: nelle righe lette di `fs.rs` (1660-1790) non c'è alcun controllo e `run_guarded` non è nella finestra. Restano ignorate l'origine delle stringhe di azione `delete:<percorso>` delle review (se generate dal modello) e la presenza di una conferma nella cancellazione di pagina orfana di `lint-view.tsx` (finestra 335-350, inizia a metà funzione). Fonte del gap: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (`run_guarded` e l'inizio del gestore di `delete_file` in `fs.rs`, `lint-view.tsx` prima della riga 335, generazione delle review in `ingest.ts` e `sweep-reviews.ts`). Non bloccante.
**Impatto:** [[llm-wiki-operazioni-distruttive]] e [[llm-wiki-rischi-persistenza]] non possono dire se la cancellazione sia confinata al progetto.

## 2026-11-20 21:12 — llm-wiki-cancellazione-file-orfani
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki-persistenza-c (accorpa due punti)
**Gap:** non è noto se `vector_delete_page` (lato Rust) cancelli anche il file `embedding-revisions/<sha256>.revision`: la cascata di cancellazione di una pagina lo lascia non toccato nel codice TS letto. Non è stata cercata la cancellazione dei file `agent-sessions/`: non è noto se qualche codice li cancelli o li ripulisca oltre al troncamento a 40 messaggi di `append_turn`. Fonte del gap: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Cascata di cancellazione di una pagina; §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (`vectorstore.rs` e `page_embedding.rs` per `vector_delete_page`; ricerca testuale su `agent-sessions` e funzioni di cancellazione di `session.rs`). Non bloccante.
**Impatto:** [[llm-wiki-operazioni-distruttive]], [[llm-wiki-cancellazione-pagine-e-sorgenti]] e [[llm-wiki-archivi-persistenza]] non descrivono il ciclo di vita dei file di revisione e di sessione dopo una cancellazione.

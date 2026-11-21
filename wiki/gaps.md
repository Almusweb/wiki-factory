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

**Aggiornamento (2026-11-21):** gap parziale, resta aperto. Letti nel giro del 2026-11-21: `api_server.rs` per intero (righe 1-4106), `ingest.ts` per intero (1-3940), `agent/tools.rs` per intero (1-3889), `agent/runtime.rs` righe 1-4031 (test esclusi), `fs.rs` righe 1-650 e 1000-2229, `lib.rs` righe 1-780 ([[2026-11-21-repo-llm_wiki-api-mcp]], [[2026-11-21-repo-llm_wiki-agente-runtime]], [[2026-11-21-repo-llm_wiki-agente-tools]], [[2026-11-21-repo-llm_wiki-fs-lib-progetto]], [[2026-11-21-repo-llm_wiki-ingest]]). Restano non letti: blocco di test di `runtime.rs` (dalla riga 4032), `fs.rs` 651-999 e 2230 in poi, `lib.rs` dalla riga 780, `provider.rs` oltre la riga 260 e i moduli elencati nel gap `llm-wiki-moduli-ingest-saltati`. [^src: raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md §Copertura]

## 2026-11-20 15:31 — llm-wiki-contratto-api-http
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** il contratto esatto dell'API HTTP locale non è noto: la README è l'unica fonte degli endpoint, `api_server.rs` e `mcp-server/src/api-client.ts` non sono stati letti. Gli endpoint HTTP corrispondenti a scrittura pagina ed embedding non sono verificati, e l'elenco endpoint della README non cita una scrittura pagina. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `api_server.rs` e `api-client.ts`). Non bloccante.
**Impatto:** [[llm-wiki-api-locale]] riporta gli endpoint solo come dichiarati in README.

**Risolto:** 2026-11-21 — [[llm-wiki-api-locale]]: contratto di 15 route più `/health` con autenticazione, payload, limiti ed errori; `pages/write` e `pages/embed` verificati; `api-client.ts` letto per intero. Residuo non bloccante: i corpi degli handler a valle (gap `llm-wiki-api-corpi-handler-non-letti`). [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Contratto API]

## 2026-11-20 15:31 — llm-wiki-api-lan-auth
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** non è noto dove vengano usati `server_bind` e `cors` né quale autenticazione si applichi quando il server ascolta fuori dal loopback. La README descrive l'API come `127.0.0.1`-only e protetta da token, il codice prevede l'ascolto su LAN opzionale: documentazione e comportamento divergono, oppure ci sono vincoli aggiuntivi non letti. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `api_server.rs` e dei punti d'uso di `server_bind` e `cors`). Non bloccante.
**Impatto:** [[llm-wiki-sicurezza]] e [[llm-wiki-api-locale]] non possono dire quale protezione valga fuori dal loopback.

**Risolto:** 2026-11-21 — [[llm-wiki-sicurezza]] e [[llm-wiki-api-locale]]: bind su `0.0.0.0` con `allowLanAccess`, nessuna distinzione di schema tra loopback e LAN, matrice token sempre richiesto o opzionale per route, CORS e uso di `server_bind` e `cors` in `api_server.rs`; la README «127.0.0.1-only» diverge dal codice. Residuo non bloccante: l'uso in `clip_server.rs` oltre la riga 60 (gap `llm-wiki-clip-server-uso-bind-cors`). [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Autenticazione e rete]

## 2026-11-20 15:31 — llm-wiki-mcp-readme-vs-codice
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** il README di `mcp-server` elenca 10 strumenti e il codice ne registra 12 (`llm_wiki_embed_page` e `llm_wiki_write_page` non documentati); il suo paragrafo di sicurezza parla solo di letture e non cita la scrittura di pagine. Non è chiaro se sia il README a essere indietro o se esistano vincoli non letti. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (confronto con `api_server.rs`, non letto). Non bloccante.
**Impatto:** [[llm-wiki-mcp-server]] riporta entrambe le versioni senza scegliere.

**Risolto:** 2026-11-21 — [[llm-wiki-mcp-server]]: il README elenca 10 strumenti contro i 12 del codice (mancano `llm_wiki_embed_page` e `llm_wiki_write_page`) ed è indietro anche sull'accesso senza token (embed, write e chat lo richiedono sempre); il codice conferma le scritture. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §README MCP vs codice]

## 2026-11-20 15:31 — llm-wiki-approvazione-shell
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** il punto in cui viene applicata l'approvazione dei comandi shell non è verificato. La README dice «external shell commands still require explicit approval»; `agent/permissions.rs` implementa solo il gate sulle capability, e la policy `api_default` include `Process`. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `agent/runtime.rs` e `agent/tools.rs`). Non bloccante.
**Impatto:** [[llm-wiki-agente]] e [[llm-wiki-sicurezza]] non possono confermare il controllo sui comandi shell.

**Risolto:** 2026-11-21 — [[llm-wiki-sicurezza]] e [[llm-wiki-agente]]: l'approvazione dei comandi shell è applicata in `runtime.rs` come passo distinto dopo la capability `Process` (percorso legacy con `is_shell_command_approved`, agent loop con `is_shell_command_allowed_without_prompt` e esito `shell.exec.approval_required`); uguaglianza esatta con `approved_shell_commands`, esenzione per i comandi confinati nel workspace solo nel loop; `tools.rs` non ha controlli di approvazione. Residui aperti come gap nuovi: `llm-wiki-approved-shell-origine`, `llm-wiki-runtime-test-non-letti`, `llm-wiki-shell-scoping-virgolette` (ipotesi non testata). [^src: raw/2026-11-21-repo-llm_wiki-agente-runtime.md §Permessi e approvazione shell (gap 5)]

## 2026-11-20 15:31 — llm-wiki-i18n-lingue
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** la README dice «English + Chinese» per l'i18n, ma in `src/i18n/` esistono `en.json`, `it.json`, `ru.json`, `zh.json`. Non è noto quali lingue siano effettivamente supportate dall'interfaccia. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `src/i18n/` e della selezione lingua). Non bloccante.
**Impatto:** [[llm-wiki-app]] riporta la divergenza senza risolverla.

**Risolto:** 2026-11-21 — [[llm-wiki-app]]: il codice registra quattro lingue di interfaccia (`en`, `it`, `zh`, `ru`, con `en` iniziale e di ripiego) e la sezione Interface le offre; la README «English + Chinese» è indietro. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Lingue dell'interfaccia (gap i18n-lingue)]

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

**Risolto:** 2026-11-21 — [[llm-wiki-app]] e [[llm-wiki-pipeline-ingest]]: l'ingest multimodale è implementato nel codice (estrazione immagini, didascalie con modello di visione, sezione «Embedded Images»); lo stato «Spec, not started» di `plans/multimodal-images.md` risulta superato (testo del piano non riletto). Residuo non bloccante: default di `multimodalConfig.enabled` e modulo Rust di estrazione (gap `llm-wiki-default-store-config`). [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Multimodale: stato reale (gap 9)]

## 2026-11-20 15:31 — llm-wiki-ci-test-build
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** la CI (`ci.yml`) non esegue i test e il workflow `build.yml` non è stato letto. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `.github/workflows/build.yml`). Non bloccante.
**Impatto:** [[llm-wiki-test-e-ci]] non descrive il workflow di build.

**Risolto:** 2026-11-21 — [[llm-wiki-test-e-ci]]: `build.yml` letto per intero (non esegue test, firma e notarizza su macOS, pubblica la release) e `ci.yml` senza passi di test. Residuo non bloccante: esecuzione dei test fuori dai workflow e `.github/scripts/*` (gap `llm-wiki-test-fuori-workflow`). [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §CI e build (gap ci-test-build)]

## 2026-11-20 15:31 — llm-wiki-requisiti-funzionali
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** requisiti funzionali e regole di dominio sono derivabili solo dalla README e non sono confermati dal codice letto. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura della logica di business, vedi `llm-wiki-codice-non-letto`). Non bloccante.
**Impatto:** [[llm-wiki-app]] elenca le funzioni solo come «dichiarate in README».

**Aggiornamento (2026-11-21):** gap parziale, resta aperto. Requisiti confermati dal codice letto: ingest, cache, coda e pulizia delle review ([[llm-wiki-pipeline-ingest]]), agente backend ([[llm-wiki-agente]]). Chat lato UI, ricerca, deep research, grafo, web clipping e API a valle non sono coperti. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Requisiti funzionali confermati sull'ingest (gap 11, parte)] [^src: raw/2026-11-21-repo-llm_wiki-agente-runtime.md §Requisiti funzionali dedotti (gap 11, parte)]

## 2026-11-20 15:31 — llm-wiki-scan-credenziali
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** nessuna scansione dei sorgenti non aperti alla ricerca di credenziali hardcoded: lo zero di secret redatti vale solo per i 30 file letti e per la ricerca dei nomi file. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (scansione testuale dei sorgenti). Non bloccante.
**Impatto:** [[llm-wiki-sicurezza]] e [[2026-11-20-repo-llm_wiki]] non possono affermare l'assenza di credenziali nel repository.

**Aggiornamento (2026-11-21):** gap parziale, resta aperto. Nessun valore di credenziale nei file letti dal giro del 2026-11-21 (secret dei workflow solo per nome); i campi che portano segreti sono elencati per nome in [[llm-wiki-sicurezza]]. La scansione resta limitata ai file letti: il resto del repository non è scansionato. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Tipi di configurazione e campi segreti (gap scan-credenziali, copertura parziale)]

## 2026-11-20 17:06 — llm-wiki-persistenza-codice-non-letto
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki (aggiornamento v2026-11-20)
**Gap:** codice che incide sulla persistenza e non è stato letto. `src-tauri/src/commands/file_sync.rs` (70 KB): sincronizzazione e watcher dei file, non si sa se persista stato. Rust: `src-tauri/src/commands/fs.rs` (atomicità di `write_file` e `writeFileAtomic`, cancellazioni), `search.rs` (`embedding_fetch`, `SearchEmbeddingConfig`), `api_server.rs` (lettura di `apiConfig`, endpoint che scrivono), `agent/runtime.rs` (chi chiama `append_turn` e con quali id di sessione), `proxy.rs`, `lib.rs` oltre le parti già lette. TS: `src/stores/wiki-store.ts` (tipi di tutte le configurazioni, compresi i campi segreti), `lint-store.ts`, `dedup-queue.ts` (persistenza della coda dedup), `wiki-page-delete.ts` (cascata di cancellazione), `source-lifecycle.ts`, `ingest.ts` (scrittura di `ingest-cache` e della cache delle didascalie), `chat-panel.tsx` (cancellazione dei file chat), `sweep-reviews.ts`, `src/commands/fs.ts`. Si sovrappone in parte al gap `llm-wiki-codice-non-letto` (`fs.rs`, `api_server.rs`, `runtime.rs`, `lib.rs`, `ingest.ts`). Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (nuova estrazione `repo-sync` che copra i file indicati). Non bloccante.
**Impatto:** [[llm-wiki-archivi-persistenza]], [[llm-wiki-operazioni-distruttive]] e [[llm-wiki-rischi-persistenza]] non possono confermare atomicità, chiamanti e cancellazioni nei file non letti.

**Aggiornamento (2026-11-21):** gap parziale, resta aperto. Ora letti: `agent/tools.rs` (per intero), `agent/runtime.rs` righe 1-4031, `session.rs` (per intero), `api_server.rs` (per intero), `fs.rs` in parte, `file_history.rs` righe 70-469, `ingest.ts`, `dedup-queue.ts` righe 1-120, `wiki-page-delete.ts`, `source-lifecycle.ts`, `sweep-reviews.ts`, `ingest-queue.ts`. Restano non letti, tra gli altri: `file_sync.rs`, `search.rs`, `proxy.rs`, `wiki-store.ts` (default), `lint-store.ts`, `chat-panel.tsx`. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Gap evidenti] [^src: raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md §Copertura]

**Aggiornamento (2026-11-21, TSK-007):** verifica della parte assegnata a US-015 (scrittura generica, sincronizzazione e osservazione dei file, persistenza di coda dedup e lint, scritture delle cache di ingest e delle didascalie). **Coperti:** stato persistito di `file_sync.rs` (righe 1-444 e 1290-1409), scrittura generica di `fs.rs` e wrapper TS, `dedup-queue.ts` (1-120), `lint-store.ts` (nota: il precedente aggiornamento lo elencava ancora tra i non letti, ma la fetta B lo riporta letto), `ingest.ts` per cache e didascalie, `agent/tools.rs`, `session.rs`, `api_server.rs`, `file_history.rs` 70-469. **Scoperti (restano aperti):** `file_sync.rs` 445-1289 e da 1410; `file_history.rs` 1-69 (scrittura di `history-settings.json`) e da 470; `fs.rs` 651-999 e 2230-3300; `search.rs`, `proxy.rs`, `lib.rs` oltre 780, `chat-panel.tsx`, `lint.ts`, `dedup.ts`, `inactiveQueueWrite` di `ingest-queue.ts`. Il gap **resta aperto**: la parte di US-015 non è chiudibile finché non è letto il meccanismo di scrittura di `history-settings.json` (nuovo raw su `file_history.rs`). Sintesi in [[llm-wiki-archivi-persistenza]] §Esito della verifica di US-015. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Copertura del gap `llm-wiki-persistenza-codice-non-letto`]

## 2026-11-20 17:06 — llm-wiki-file-citati-non-verificati
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki (aggiornamento v2026-11-20)
**Gap:** file e cartelle citati nei commenti del codice ma non verificati: `image-caption-cache.json`, `lexical-graph.json` (commento di `dedup-storage.ts`), la cartella `raw/sources/.cache` e la cartella legacy `.llm-wiki-imported`. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `ingest.ts`, `dedup-storage.ts` e dei punti d'uso). Non bloccante.
**Impatto:** [[llm-wiki-archivi-persistenza]] elenca 17 archivi senza questi file, di cui non è noto se esistano come archivi.

**Aggiornamento (2026-11-21):** gap parziale, resta aperto. `image-caption-cache.json` esiste (`.llm-wiki/image-caption-cache.json`, scritto con `writeFile`) e `raw/sources/.cache` esiste come `<cartella del sorgente>/.cache/<nomefile>.txt`; `lexical-graph.json` e `.llm-wiki-imported` restano non verificati in questo giro. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §File citati nei commenti (gap 14)]

**Aggiornamento (2026-11-21, TSK-007):** verifica di US-015 AC3, **pronto per la chiusura con riserva**, non chiuso qui. Esito per file: `image-caption-cache.json` esiste come archivio (`.llm-wiki/image-caption-cache.json`, campi e scrittura diretta in [[llm-wiki-archivi-persistenza]]); `raw/sources/.cache` esiste come cartella `.cache` accanto a ogni sorgente; `lexical-graph.json` non esiste nel codice (solo il commento «when added» di `dedup-storage.ts`; ricerca testuale della fetta B su `src` e `src-tauri/src`, valida per la stringa esatta); `.llm-wiki-imported` non è un archivio, è un nome di esclusione dalla scansione (`scheduled-import.ts:235`). Riserva: la fetta C2 del 2026-11-21 dichiara gli ultimi due «non verificati» nei suoi file e il solo uso di `.llm-wiki-imported` viene dalla sessione, non da un indice globale. La chiusura spetta all'utente su conferma della riserva. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §File e cartelle citati e non verificati] [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Punto 7: `.llm-wiki-imported`]

## 2026-11-20 17:06 — llm-wiki-app-state-percorso
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki (aggiornamento v2026-11-20)
**Gap:** il percorso effettivo di `app-state.json` e il comportamento del plugin store su file corrotto non sono determinabili dal campione. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (configurazione del plugin store in `lib.rs` e documentazione del plugin). Non bloccante.
**Impatto:** [[llm-wiki-archivi-persistenza]] e [[llm-wiki-gestione-file-corrotti]] non possono dire dove sia lo store né come reagisca a un file corrotto.

**Aggiornamento (2026-11-21):** gap parziale, resta aperto. Il percorso è `<app_data_dir>/app-state.json` ([[llm-wiki-archivi-persistenza]]); il path OS risolto da `app_data_dir` per piattaforma e il comportamento su file corrotto non sono verificati. [^src: raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md §Archivio dello stato app (gap 15)]

**Aggiornamento (2026-11-21, TSK-006):** verifica di US-014 sul raw ingerito: nessun nuovo elemento rispetto all'aggiornamento sopra, il gap **non è pronto per la chiusura**. Restano non verificati (a) il percorso fisico di `app_data_dir` per sistema operativo (dipende da Tauri) e (b) il comportamento del plugin store su file corrotto (sorgente e documentazione del plugin assenti dal raw). Per chiuderlo serve un nuovo raw: configurazione del plugin store e documentazione Tauri, oppure un'osservazione in esecuzione. Sintesi in [[llm-wiki-archivi-persistenza]]. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Store applicativo (`app-state.json`)]

## 2026-11-20 17:06 — llm-wiki-creazione-cartella-dati
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki (aggiornamento v2026-11-20)
**Gap:** non è noto chi crei `.llm-wiki/` per un progetto importato o aperto da disco: `create_project` non la crea e `open_project` non la richiede. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `persist.ts` nei punti d'uso e dei flussi di apertura progetto non letti). Non bloccante.
**Impatto:** [[llm-wiki-schema-dati]] e [[llm-wiki-archivi-persistenza]] non possono descrivere il ciclo di vita della cartella dati.

**Risolto:** 2026-11-21 — [[llm-wiki-schema-dati]]: `.llm-wiki/` nasce lato frontend; `createProject` e `openProject` chiamano `ensureProjectId`, che scrive `.llm-wiki/project.json` se manca, e `ensureDir` in `persist.ts` crea `.llm-wiki` e `.llm-wiki/chats` prima di salvare review, lint, chat e preferenze; `create_project` e `open_project` non la creano. [^src: raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md §Layout del progetto su disco e creazione di `.llm-wiki/` (gap 16)]

## 2026-11-20 17:06 — llm-wiki-vector-v1-chiamanti
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki (aggiornamento v2026-11-20)
**Gap:** nessun chiamante di `vector_upsert` e `vector_delete` (v1) nel campione: non è chiaro se i percorsi v1 siano ancora usati. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura dei chiamanti dei comandi Tauri, ad esempio in `lib.rs`). Non bloccante.
**Impatto:** [[llm-wiki-versioni-e-migrazioni]] e [[llm-wiki-operazioni-distruttive]] non possono dire se il v1 sia ancora scritto.

**Aggiornamento (2026-11-21):** gap parziale, resta aperto. `embedding.ts` (letto per intero) non invoca i comandi v1 e dopo un rebuild forzato elimina la tabella legacy; `EmbeddingSection` usa `vector_legacy_row_count` e `vector_drop_legacy`; i comandi v1 restano registrati e testati. Altri chiamanti (`api_server.rs`, `agent/tools.rs`, `search.rs`, `mcp-server`) non verificati; non si esclude un uso interno Rust. [^src: raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md §Vector v1 vs v2 (gap 17)] [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Chiamanti (gap chiamanti-non-verificati, parziale)]

## 2026-11-20 17:06 — llm-wiki-log-index-formato
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki (aggiornamento v2026-11-20)
**Gap:** formato di `wiki/log.md` e logica di aggiornamento di `wiki/index.md` oltre `rebuild_wiki_index`: non analizzati. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura della logica di ingest e dei comandi di scrittura di log e indice). Non bloccante.
**Impatto:** [[llm-wiki-schema-dati]] non descrive il formato dei file `log.md` e `index.md` del progetto wiki.

**Risolto:** 2026-11-21 — [[llm-wiki-schema-dati]]: formati di `wiki/log.md` (voce di ingest e voce di cancellazione sorgente, formato non uniforme tra scrittori), `wiki/index.md` (`## Recently Updated`, fino a 200 voci), `wiki/overview.md` (marcatori, fino a 50 voci) e `ingest-warnings.log`; `tools.rs` non scrive né log né indice. Residuo non bloccante: `rebuild_wiki_index` in Rust non analizzato. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Formati di log e indici (gap 18)]

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

**Aggiornamento (2026-11-21):** gap parziale, resta aperto. Verificati: dimensione del vettore dal primo chunk, assenza di controllo dimensionale in scrittura (`merge_insert`) e in ricerca, impronta di revisione (include modello ed endpoint, non la chiave API), re-index manuale con azzeramento della tabella v2, nessun re-index né avviso al salvataggio delle impostazioni ([[llm-wiki-rischi-persistenza]]). Restano non verificati il comportamento di LanceDB su dimensioni diverse e se `embedAllPages` (`src/lib/embedding.ts`) rilevi il cambio di modello. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Ciclo di vita dei vettori e cambio modello (gap embedding-cambio-modello)]

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

**Aggiornamento (2026-11-21):** gap parziale, resta aperto. Nota ora la posizione di `chat-history.json` (`<project>/.llm-wiki/chat-history.json`, solo legacy in lettura) ([[llm-wiki-archivi-persistenza]]); il criterio di conteggio 16/17 e la tesi «una sola versione di formato» non sono toccati. [^src: raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md §Storia dei file e persistenza in `.llm-wiki` (gap 13 parziale, gap 23 posizione)]

## 2026-11-20 18:23 — llm-wiki-id-chat-sessione
**Origine:** lead-architect @ TSK-010 (indice di `design_&_architecture/db_schemas/`)
**Gap:** la wiki non dice come si genera l'id di una conversazione chat (nome di `chats/<id>.json`, `conversationId` dei messaggi), da dove arriva il `sessionId` delle sessioni agente né quale regola di sanitizzazione gli si applica, se una conversazione chat e una sessione agente condividano un identificativo, e se il `projectId` delle sessioni agente coincida con l'`id` di `project.json`.
**Sospetta fonte:** raw/2026-11-20-repo-llm_wiki.md (presente: verificare se riporta la generazione degli id in `chat-store.ts` e `agent/session.rs`); per i chiamanti di `append_turn` serve nuovo raw (`agent/runtime.rs`, già nel gap `llm-wiki-persistenza-codice-non-letto`). Non bloccante.
**Impatto:** l'indice di `db_schemas/` (identificatori I1, I8, I9; relazioni R3, R9) e la scheda di US-022 marcano questi punti «non verificato».

**Aggiornamento (2026-11-21):** gap parziale, resta aperto. Documentati: id di conversazione `conv_<ms>_<6 base36>`, id di messaggio `msg_<ts>_<contatore>_<casuale>`, `sessionId` `api_<uuid v4>` se vuoto e regola `sanitize_session_id` ([[llm-wiki-archivi-persistenza]]); il chiamante di `append_turn` non è `runtime.rs`. Restano aperti: se la UI passi il `conversationId` come `sessionId` e se il `projectId` delle sessioni coincida con l'id di `project.json`. [^src: raw/2026-11-21-repo-llm_wiki-agente-runtime.md §Sessioni e id (gap 24)] [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Identificatori e riferimenti (gap riferimenti-incrociati, parziale)]

## 2026-11-20 18:23 — llm-wiki-riferimenti-incrociati
**Origine:** lead-architect @ TSK-010 (indice di `design_&_architecture/db_schemas/`)
**Gap:** non è documentata la forma dei riferimenti fra archivi. Pagine: `affectedPages` di `review.json`, gli slug di `dedup-not-duplicates.json`, `ignorePages` di `lint-config.json`, `filesWritten` di `ingest-cache.json`, rispetto all'id di pagina v2 (percorso relativo sotto `wiki/` senza `.md`). Sorgenti: `sourcePath` di `ingest-queue.json` (relativo) e di `review.json`, il «nome sorgente» che indicizza `ingest-cache.json`, le chiavi di `files` in `scheduled-import-db.json`. Percorsi: la base del percorso relativo della cronologia; la forma del percorso di progetto in `projectRegistry`, `recentProjects`, `lastProject` e nella chiave `scheduledImportConfig:<percorso>`; come la chiave `default` di `sourceWatchConfig` e `projectFileSyncEnabled` conviva con le chiavi per id progetto. Hash: la codifica di `sha256(page_id)` nei nomi `.revision` e dell'hash FNV-1a nei nomi dei file di cronologia.
**Sospetta fonte:** raw/2026-11-20-repo-llm_wiki.md (presente: verificare se lo riporta); altrimenti nuovo raw (`review-store.ts`, `dedup-storage.ts`, `lint-config.ts`, `ingest-cache.ts`, `ingest-queue.ts`, `scheduled-import.ts`, `project-store.ts`, `page_embedding.rs`, `file_history.rs`). Non bloccante.
**Impatto:** l'indice di `db_schemas/` non può dire quali archivi condividano davvero l'id di pagina o il riferimento a sorgente: le relazioni R2 (in parte), R12 e R13 e gli identificatori I2, I6, I7, I10, I11 restano «non verificato».

**Aggiornamento (2026-11-21):** gap parziale, resta aperto. Chiariti: forma di `projectRegistry` (`{id, path, name, lastOpened}`), hash FNV-1a 64 del path relativo per i nomi in `history/`, sha256 di `page_id` per i `.revision`, id di review (FNV-1a 32), id di pagina nei vettori, `ignorePages` di `lint-config.json`, forme di `sourceIdentity`, `filesWritten`, `sourcePath` (coda e review), `affectedPages` e slug di dedup ([[llm-wiki-schema-dati]], [[llm-wiki-archivi-persistenza]]). Restano non verificati: chiavi di `scheduled-import-db.json`, forma del path in `recentProjects` e `lastProject`, codifica e uso degli hash di cronologia. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Riferimenti incrociati nella fetta (gap 25, parte)] [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Identificatori e riferimenti (gap riferimenti-incrociati, parziale)]

## 2026-11-20 21:12 — llm-wiki-import-id-duplicato
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki-persistenza-a
**Gap:** dopo l'importazione di un archivio non è noto cosa accada se l'id in `.llm-wiki/project.json`, ripristinato dallo zip, coincide con uno già presente in `projectRegistry` o `recentProjects` (collisione, sovrascrittura o duplicato). Il flusso `import_project_archive`, `openProject` e `addToRecentProjects` è letto fino al chiamante UI, non oltre. Fonte del gap: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Punto 1: caso «importato».
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `project-identity.ts`, in particolare `upsertProjectInfo`, e del flusso di apertura progetto). Non bloccante.
**Impatto:** [[llm-wiki-archivi-persistenza]] e [[llm-wiki-operazioni-distruttive]] non possono descrivere l'esito dell'importazione; tocca i rischi 2 e 3 di [[llm-wiki-rischi-persistenza]].

**Aggiornamento (2026-11-21):** gap parziale, resta aperto. `upsertProjectInfo` sovrascrive la entry del registro per id senza controllare il path e `import_project_archive` non rigenera l'id; l'esito della collisione è una **deduzione non testata**; il chiamante UI di `import_project_archive` non è stato trovato in `src/` (nessun file `*archive*` o `*project-maintenance*`). [^src: raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md §Identita' del progetto, registro e import (gap 26)]

**Aggiornamento (2026-11-21):** corregge il «chiamante UI non trovato» qui sopra: il chiamante è documentato in persistenza-c (`MaintenanceSection`, poi `openProject` e `addToRecentProjects`); la fetta fs-lib-progetto aveva cercato solo per nome file. Resta aperto se l'id venga rigenerato prima di `openProject`; la collisione resta deduzione non testata. Gap non chiuso. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Operazioni distruttive: chiamanti, riga per riga]

## 2026-11-20 21:12 — llm-wiki-serde-compat-config
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki-persistenza-a
**Gap:** non è verificata la compatibilità serde tra `llmConfig` dello store e `agent::provider::LlmConfig`, né tra `searchApiConfig` e le struct `WebSearchConfig` e `AnyTxtConfig` (`agent/provider.rs` e `agent/tools.rs` non letti): non si sa se campi opzionali o sconosciuti vengano scartati in silenzio. Fonte del gap: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `agent/provider.rs` e `agent/tools.rs`). Non bloccante.
**Impatto:** [[llm-wiki-schema-dati]] e [[llm-wiki-agente]] non possono dire quali campi della configurazione arrivino davvero al runtime.

**Aggiornamento (2026-11-21):** gap parziale, resta aperto. Lato Rust nessuna struct ha `deny_unknown_fields` (campi sconosciuti scartati in silenzio), obbligatorio solo `provider`, default elencati per le quattro struct ([[llm-wiki-schema-dati]]). Restano non letti i tipi TypeScript di `llmConfig`, `searchApiConfig` e della config AnyTXT e il punto in cui l'API HTTP deserializza queste struct; l'ipotesi sui nomi `searXng*` resta non testata. [^src: raw/2026-11-21-repo-llm_wiki-agente-tools.md §Configurazioni e serde (gap serde-compat-config)]

## 2026-11-20 21:12 — llm-wiki-embedding-trasporto
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki-persistenza-a
**Gap:** il trasporto effettivo dell'embedding non è letto: `fetch_embedding_once` e `fetch_embedding_batch` (`search.rs` oltre la riga 1200), l'uso della chiave API e l'uso di `SEARCH_EMBEDDING_TIMEOUT_SECS` (valore 8, uso non nel campione). Sottodomanda del gap `llm-wiki-persistenza-codice-non-letto`, tenuta a parte per l'impatto sulla sicurezza. Fonte del gap: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `search.rs` dalla riga 1201). Non bloccante.
**Impatto:** [[llm-wiki-sicurezza]] non può dire dove e come viaggia la chiave API dell'embedding; tocca il rischio 8 di [[llm-wiki-rischi-persistenza]].

**Risolto:** 2026-11-21 — [[llm-wiki-sicurezza]]: la chiave API di embedding viaggia solo verso l'endpoint configurato, con header `Authorization: Bearer` (OpenAI-compatibili e Volcengine) o `x-goog-api-key` (Google), proxy applicativo, header extra filtrati, nessun controllo che imponga https nelle finestre lette; `fetch_embedding_once` e `fetch_embedding_batch` letti. Residuo non bloccante: il valore di `SEARCH_EMBEDDING_TIMEOUT_SECS` è fuori dalla finestra letta. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Trasporto dell'embedding (gap embedding-trasporto)]

## 2026-11-20 21:12 — llm-wiki-ui-salvataggio-impostazioni
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki-persistenza-a
**Gap:** il raw colloca nel salvataggio delle impostazioni (`settings-view.tsx`, finestra 505-540) solo proxy, API, MinerU e import pianificato; dove e come la UI salva le altre chiavi (`llmConfig`, `providerConfigs`, `searchApiConfig`, `embeddingConfig`, `multimodalConfig`, `generalConfig`) non è letto, così come il salvataggio effettivo della sezione embedding. Fonte del gap: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Punto 9: quando la UI invoca `set_proxy_env` e il reload.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `settings-view.tsx` fuori dalla finestra e di `embedding-section.tsx` dalla riga 201). Non bloccante.
**Impatto:** [[llm-wiki-archivi-persistenza]] non può dire quando una modifica alle altre chiavi è scritta su disco, oltre al salvataggio automatico con debounce.

**Aggiornamento (2026-11-21):** gap parziale, resta aperto. Chiusi i punti `embeddingConfig`, `multimodalConfig`, `generalConfig`, `llmConfig` e il salvataggio effettivo della sezione embedding (`handleSave` in sequenza; `embedding-section.tsx` modifica solo il draft) ([[llm-wiki-archivi-persistenza]]). Non verificati: salvataggio di `providerConfigs` e `searchApiConfig` (`LlmProviderSection` e `WebSearchSection` non lette), punto di rilettura della lingua UI all'avvio, persistenza di `maxHistoryMessages`. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Salvataggio delle impostazioni (gap ui-salvataggio-impostazioni)]

## 2026-11-20 21:12 — llm-wiki-scritture-non-verificate
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki-persistenza-b (accorpa punti delle fette B e C)
**Gap:** il meccanismo di scrittura di alcuni archivi o scrittori non è verificato: `history-settings.json` (di `file_history.rs` sono lette solo le righe 1-70), le scritture per progetti non attivi di `ingest-queue.ts` (`inactiveQueueWrite`, file letto solo in parte), `write_wiki_page_verified` (`agent/tools.rs`: cartelle ammesse, atomicità, aggiornamento di indice e log) e `read_raw_review_array` e `write_raw_review_array` (senza i quali non si può dire se l'auto-save possa sovrascrivere le modifiche fatte alle review via API). Fonte del gap: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Atomicità per archivio, §Gap evidenti; raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (`file_history.rs` oltre la riga 70, `ingest-queue.ts`, `agent/tools.rs`, `api_server.rs` per i due helper di review). Non bloccante.
**Impatto:** [[llm-wiki-archivi-persistenza]], [[llm-wiki-api-locale]] e [[llm-wiki-rischi-persistenza]] non possono dire con quale atomicità siano scritti questi archivi; tocca il rischio 4.

**Aggiornamento (2026-11-21):** gap parziale, resta aperto. Chiusi: `write_wiki_page_verified` (solo `wiki/**/*.md`, sostituzione atomica con rilettura byte a byte, nessuna scrittura di indice e log, limiti: nessun fsync della cartella padre, mutex solo intra-processo), `read_raw_review_array` e `write_raw_review_array` (scritture review non atomiche, non verificate, senza lock; concorrenza con la WebView non letta) e `file_history.rs` righe 70-469 ([[llm-wiki-rischi-persistenza]], [[llm-wiki-api-locale]]). Restano non letti `history-settings.json` (`file_history.rs` righe 1-69) e `inactiveQueueWrite` di `ingest-queue.ts`. Il raw della fetta A dichiara di chiudere il gap, ma `history-settings.json` non è letto da nessuna fetta: per questo non è chiuso. [^src: raw/2026-11-21-repo-llm_wiki-agente-tools.md §write_wiki_page_verified (gap scritture-non-verificate, parte)] [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Scritture sullo stato] [^src: raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md §Copertura]

## 2026-11-20 21:12 — llm-wiki-chiamanti-non-verificati
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki-persistenza-c (accorpa punti delle fette B e C)
**Gap:** restano chiamanti non verificati o non classificati: l'elenco completo dei chiamanti di `writeFileAtomic` (da graphify a profondità 1, non da ricerca testuale), i chiamanti dei wrapper `copyFile` e `copyDirectory` (`fs.ts:98` e `:105`), il chiamante di `optimizeChunkVectorTableBestEffort`, le stringhe non classificate (`embedding.ts:705`, `:731`, `:745`, `auto-save.ts:12`, `:28`), i corpi di `removeTasks` e `cancelAllTasks`; inoltre `cleanupWrittenFiles` e `clearCompletedTasks` non hanno chiamanti nell'ambito cercato, mentre i commenti dei sorgenti li descrivono come usati: non è noto se siano codice morto o chiamati da fuori ambito (`mcp-server`, `extension`, `scripts`, test) o per nome dinamico. Fonte del gap: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Gap evidenti, §Contraddizioni con la wiki; raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Punto 2: `writeFileAtomic` e il markdown estratto.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (ricerca testuale e lettura dei punti indicati, comprese le cartelle fuori ambito). Non bloccante.
**Impatto:** [[llm-wiki-operazioni-distruttive]] resta con righe «chiamante non verificato» (`copy_file`, `copy_directory`, `vector_optimize_chunks`) e con due operazioni «senza chiamanti nell'ambito cercato».

**Aggiornamento (2026-11-21):** gap parziale, resta aperto. Chiariti: usi UI di `vector_legacy_row_count` e `vector_drop_legacy` (`embedding-section.tsx`), comportamento di `vector_optimize_chunks`; `cleanupWrittenFiles` e `clearCompletedTasks` non hanno chiamanti nei file letti di `ingest-queue.ts` (non è noto se codice morto o chiamati da fuori ambito). Restano non verificati i chiamanti di `optimizeChunkVectorTableBestEffort`, `writeFileAtomic`, `copyFile`, `copyDirectory`, `removeTasks`, `cancelAllTasks` e le stringhe di `embedding.ts` e `auto-save.ts`. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Chiamanti (gap chiamanti-non-verificati, parziale)] [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Cancellazione, lato TypeScript (gap 34)]

## 2026-11-20 21:12 — llm-wiki-tipi-dedup-lint
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki-persistenza-b
**Gap:** il tipo `DuplicateGroup` (`dedup.ts`) e i valori ammessi di `type` e `severity` di `LintResult` (`lint.ts`) non sono letti: il campo `group` di `dedup-queue.json` e `type` e `severity` di `lint.json` restano non descritti. Fonte del gap: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Coda di dedup e lint.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `dedup.ts` e `lint.ts`). Non bloccante.
**Impatto:** [[llm-wiki-schema-dati]] e [[llm-wiki-archivi-persistenza]] non possono descrivere per intero i campi di `dedup-queue.json` e `lint.json`.

**Risolto:** 2026-11-21 — [[llm-wiki-schema-dati]]: `DuplicateGroup` (`{slugs, reason, confidence}`), `DedupTask`, `LintResult` (valori ammessi di `type` e `severity`) e `dedup-not-duplicates.json` descritti. Residuo non bloccante: la forma persistita di `lint.json` non è verificata. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Tipi di dedup e lint (gap 32)]

## 2026-11-20 21:12 — llm-wiki-markdown-estratto-percorsi
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki-persistenza-b (accorpa due punti della fetta B)
**Gap:** per le immagini MinerU, `mineruAssetRelPath` non è letta e la cartella assoluta `mediaDir` non è nella finestra letta di `mineru.ts`: che le immagini vadano sotto `wiki/media/` è una deduzione dal prefisso. Per il markdown estratto in `raw/parsed`, il legame tra l'opzione di disattivazione (commento a `parsed-source-output.ts:80`) e `persistExtractedMarkdown` è solo dedotto; default e punto di lettura non sono verificati. Fonte del gap: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Punto 3: immagini MinerU; §Punto 2: `writeFileAtomic` e il markdown estratto.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `mineruAssetRelPath` e di `mineru.ts` fuori dalle finestre, dei punti di lettura dell'opzione). Non bloccante.
**Impatto:** [[llm-wiki-archivi-persistenza]] non può confermare la posizione delle immagini MinerU né il default della copia in `raw/parsed`.

**Risolto:** 2026-11-21 — [[llm-wiki-archivi-persistenza]]: le immagini MinerU stanno sotto `wiki/media/<slug>/mineru/` (non più una deduzione) e la copia del markdown estratto in `raw/parsed` è scritta solo se `sourceWatchConfig.persistExtractedMarkdown` è vero (default `false` in `source-watch-defaults.json`). Residuo non bloccante: il default dello store (`wiki-store`) non è letto (gap `llm-wiki-default-store-config`). [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Percorsi del markdown estratto e delle immagini MinerU (gap 33)]

## 2026-11-20 21:12 — llm-wiki-cancellazione-controlli-confine
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki-persistenza-c
**Gap:** non è noto se `delete_file` controlli che il percorso sia dentro il progetto: nelle righe lette di `fs.rs` (1660-1790) non c'è alcun controllo e `run_guarded` non è nella finestra. Restano ignorate l'origine delle stringhe di azione `delete:<percorso>` delle review (se generate dal modello) e la presenza di una conferma nella cancellazione di pagina orfana di `lint-view.tsx` (finestra 335-350, inizia a metà funzione). Fonte del gap: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (`run_guarded` e l'inizio del gestore di `delete_file` in `fs.rs`, `lint-view.tsx` prima della riga 335, generazione delle review in `ingest.ts` e `sweep-reviews.ts`). Non bloccante.
**Impatto:** [[llm-wiki-operazioni-distruttive]] e [[llm-wiki-rischi-persistenza]] non possono dire se la cancellazione sia confinata al progetto.

**Aggiornamento (2026-11-21):** gap parziale, resta aperto. Lato Rust letto: `delete_file` (fs.rs 1737-1788) non ha alcun confinamento al progetto, `run_guarded` letto; origine delle azioni `delete:` chiarita (`lint-view.tsx` per `broken-link`, etichetta `OPTIONS:` del modello senza validazione); conferma presente sulle pagine orfane di `lint-view.tsx` e assente in `review-view.tsx` ([[llm-wiki-operazioni-distruttive]], [[llm-wiki-cancellazione-pagine-e-sorgenti]]). Restano non verificati i chiamanti TS che confinano `delete_file` al progetto; la combinazione dei passaggi è un'ipotesi non riprodotta ([[llm-wiki-rischi-persistenza]]). [^src: raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md §Comandi FS Rust e confini (gap 34, lato Rust)] [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Cancellazione, lato TypeScript (gap 34)]

## 2026-11-20 21:12 — llm-wiki-cancellazione-file-orfani
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki-persistenza-c (accorpa due punti)
**Gap:** non è noto se `vector_delete_page` (lato Rust) cancelli anche il file `embedding-revisions/<sha256>.revision`: la cascata di cancellazione di una pagina lo lascia non toccato nel codice TS letto. Non è stata cercata la cancellazione dei file `agent-sessions/`: non è noto se qualche codice li cancelli o li ripulisca oltre al troncamento a 40 messaggi di `append_turn`. Fonte del gap: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Cascata di cancellazione di una pagina; §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (`vectorstore.rs` e `page_embedding.rs` per `vector_delete_page`; ricerca testuale su `agent-sessions` e funzioni di cancellazione di `session.rs`). Non bloccante.
**Impatto:** [[llm-wiki-operazioni-distruttive]], [[llm-wiki-cancellazione-pagine-e-sorgenti]] e [[llm-wiki-archivi-persistenza]] non descrivono il ciclo di vita dei file di revisione e di sessione dopo una cancellazione.

**Aggiornamento (2026-11-21):** gap parziale, resta aperto. Parte vettori chiusa: `vector_delete_page` esegue solo `table.delete` sul `page_id` e non cancella il file `.revision` (rimosso solo da `invalidate_page_revision`); un `.revision` orfano non produce falsi «unchanged» ([[llm-wiki-cancellazione-pagine-e-sorgenti]]). Sessioni agente: nessuna funzione di `session.rs` cancella i file di `agent-sessions/`, che restano su disco oltre il troncamento a 40 messaggi; non è verificato (nessuna ricerca testuale) se UI, API, `runtime.rs` o `lib.rs` li cancellino. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Cancellazione di revisioni e sessioni (gap cancellazione-file-orfani)]

## 2026-11-21 07:31 — llm-wiki-api-corpi-handler-non-letti
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-api-mcp
**Gap:** non sono letti i corpi di `commands::page_embedding::embed_wiki_page`, `commands::search::*` (incluso `resolve_query_embedding`) e `commands::file_sync::rescan_project_files`, né gli eventi agente in `agent/`: di questi handler si conosce solo il contratto HTTP. La struttura di `AgentChatRequest` in `agent/types.rs` è stata letta dalla fetta [[2026-11-21-repo-llm_wiki-agente-tools]] solo per i commenti su `approved_shell_commands`. Fonte del gap: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Gap evidenti (residui di questa fetta).
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `page_embedding.rs`, `search.rs`, `file_sync.rs`, `agent/events.rs`). Non bloccante.
**Impatto:** [[llm-wiki-api-locale]] descrive questi endpoint solo per contratto HTTP, non per comportamento.

## 2026-11-21 07:31 — llm-wiki-clip-server-uso-bind-cors
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-api-mcp
**Gap:** l'uso effettivo di `server_bind` e `cors` in `clip_server.rs` oltre la riga 60 non è verificato: sono letti solo gli import (righe 7-8, 17). Non è noto se il Clip server (porta 19827) applichi gli stessi bind, token e CORS dell'API. Fonte del gap: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Autenticazione e rete.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `clip_server.rs` oltre la riga 60). Non bloccante.
**Impatto:** [[llm-wiki-sicurezza]] non può dire quale protezione valga per il Clip server.

## 2026-11-21 07:31 — llm-wiki-review-concorrenza-webview
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-api-mcp
**Gap:** l'interazione effettiva del processo WebView con `review.json` (finestra read-modify-write rispetto alle scritture API non atomiche e senza lock) non è stata letta; la concorrenza reale non è testata. Fonte del gap: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Scritture sullo stato.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (`review-store.ts`, `auto-save.ts` e prova di concorrenza). Non bloccante.
**Impatto:** [[llm-wiki-rischi-persistenza]] e [[llm-wiki-api-locale]] non possono dire se una modifica via API alle review possa essere sovrascritta dall'auto-save.

## 2026-11-21 07:31 — llm-wiki-api-ui-token-non-letti
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-api-mcp
**Gap:** non sono letti il resto di `api-server-section.tsx` (UI del token e rendering della lista endpoint), `mcp-server/src/project-binding.ts` e `version.ts`. `src/i18n/index.ts` risulta letto dalla fetta [[2026-11-21-repo-llm_wiki-ricerca-ui-residui]] e non è più incluso. Fonte del gap: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Provenienza e copertura.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw. Non bloccante.
**Impatto:** [[llm-wiki-api-locale]] e [[llm-wiki-mcp-server]] non descrivono la UI del token né il vincolo di progetto del client MCP oltre `set_project`.

## 2026-11-21 07:31 — llm-wiki-approved-shell-origine
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-agente-runtime
**Gap:** non è noto chi popoli `approved_shell_commands` di `AgentChatRequest` (UI o API) né come l'utente approvi un comando; servono `types.rs` (letto solo per i commenti) e il frontend. Fonte del gap: raw/2026-11-21-repo-llm_wiki-agente-runtime.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (frontend dell'approvazione e punti d'uso di `AgentChatRequest`). Non bloccante.
**Impatto:** [[llm-wiki-sicurezza]] e [[llm-wiki-agente]] non possono dire come arrivi l'approvazione dell'utente.

## 2026-11-21 07:31 — llm-wiki-shell-scoping-virgolette
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-agente-runtime
**Gap:** ipotesi non testata: `shell_command_tokens` non spezza il testo tra virgolette e un comando come `bash -c "cat /etc/passwd"` potrebbe sfuggire al controllo dei percorsi assoluti nell'esenzione workspace. Da verificare con un test prima di considerarla un difetto. Fonte del gap: raw/2026-11-21-repo-llm_wiki-agente-runtime.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (test di `runtime.rs` e prova mirata). Non bloccante.
**Impatto:** [[llm-wiki-sicurezza]] riporta il punto come ipotesi, non come difetto.

## 2026-11-21 07:31 — llm-wiki-sessione-collisione-id
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-agente-runtime
**Gap:** inferenza non testata: `sanitize_session_id` mappa id diversi sullo stesso file (per esempio `a b` e `a_b`); non verificata in pratica. Fonte del gap: raw/2026-11-21-repo-llm_wiki-agente-runtime.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (prova su `session.rs`). Non bloccante.
**Impatto:** [[llm-wiki-archivi-persistenza]] riporta la collisione come inferenza.

## 2026-11-21 07:31 — llm-wiki-sessione-concorrenza-file
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-agente-runtime
**Gap:** `append_turn` usa un mutex in-process senza lock su file; il comportamento con due processi sullo stesso progetto non è stato testato (osservazione dal codice). Fonte del gap: raw/2026-11-21-repo-llm_wiki-agente-runtime.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (prova con due processi). Non bloccante.
**Impatto:** [[llm-wiki-archivi-persistenza]] e [[llm-wiki-rischi-persistenza]] non possono dire se le sessioni agente siano sicure con più processi.

## 2026-11-21 07:31 — llm-wiki-runtime-test-non-letti
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-agente-runtime
**Gap:** il blocco `#[cfg(test)]` di `agent/runtime.rs` (dalla riga 4032, circa 5700 righe) non è stato letto: il comportamento descritto per approvazione e scoping non è confrontato con i test. Fonte del gap: raw/2026-11-21-repo-llm_wiki-agente-runtime.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `runtime.rs` dalla riga 4032). Non bloccante.
**Impatto:** [[llm-wiki-agente]] e [[llm-wiki-sicurezza]] non possono confermare approvazione e scoping contro i test.

## 2026-11-21 07:31 — llm-wiki-provider-rs-non-letto
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-agente-tools
**Gap:** `agent/provider.rs` è letto solo alle righe 1-260 di circa 600: costruzione degli URL, richieste e streaming non sono letti. Fonte del gap: raw/2026-11-21-repo-llm_wiki-agente-tools.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `provider.rs` dalla riga 261). Non bloccante.
**Impatto:** [[llm-wiki-agente]] descrive i provider LLM e web solo per i nomi gestiti e i limiti, non per il trasporto.

## 2026-11-21 07:31 — llm-wiki-token-cifratura
**Origine:** wiki-keeper @ ingest 2026-11-21 (raw fs-lib-progetto e ricerca-ui-residui)
**Gap:** non è verificato se i token di `apiConfig` e le chiavi dei provider in `app-state.json` siano cifrati: nelle finestre lette non c'è cifratura (deduzione non testata: memorizzazione in chiaro). Servono la lettura del resto del codice di salvataggio e della configurazione del plugin store; la ricerca di credenziali nel resto del repository resta nel gap `llm-wiki-scan-credenziali`. Fonte del gap: raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md §Archivio dello stato app (gap 15); raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Tipi di configurazione e campi segreti (gap scan-credenziali, copertura parziale).
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (configurazione del plugin store in `lib.rs` e codice di salvataggio). Non bloccante.
**Impatto:** [[llm-wiki-sicurezza]] e [[llm-wiki-rischi-persistenza]] (rischio 8) riportano la memorizzazione in chiaro come deduzione.

## 2026-11-21 07:31 — llm-wiki-default-store-config
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-ingest
**Gap:** non sono letti il default di `multimodalConfig.enabled` e il default dello store (`wiki-store`) per `persistExtractedMarkdown`; il default in `source-watch-defaults.json` è `false`. Fonte del gap: raw/2026-11-21-repo-llm_wiki-ingest.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `src/stores/wiki-store.ts`). Non bloccante.
**Impatto:** [[llm-wiki-app]] e [[llm-wiki-archivi-persistenza]] non possono dire se l'ingest multimodale e la copia in `raw/parsed` siano attivi di default.

## 2026-11-21 07:31 — llm-wiki-moduli-ingest-saltati
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-ingest
**Gap:** moduli dell'ingest non letti: `page-merge.ts`, `extract-source-images.ts`, `ingest-sanitize.ts`, `ingest-commit-coordinator.ts`, `vision-caption.ts`, `embedding.ts`, `lint-config.ts`, `lint-store.ts`, `dedup.ts` oltre la riga 150, `dedup-queue.ts` oltre la riga 120, `mineru.ts` oltre la riga 700 e tutti i `*.test.ts`. Fonte del gap: raw/2026-11-21-repo-llm_wiki-ingest.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura dei moduli indicati). Non bloccante.
**Impatto:** [[llm-wiki-pipeline-ingest]] descrive merge, commit coordinato e sanificazione solo per il comportamento visto in `ingest.ts`.

## 2026-11-21 07:31 — llm-wiki-test-fuori-workflow
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-ricerca-ui-residui
**Gap:** l'esecuzione dei test al di fuori dei workflow (test Rust `#[cfg(test)]` e TypeScript) e il contenuto degli script `.github/scripts/*` non sono verificati. Fonte del gap: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `.github/scripts/*` e della documentazione di contribuzione). Non bloccante.
**Impatto:** [[llm-wiki-test-e-ci]] non può dire se e dove i test girino.

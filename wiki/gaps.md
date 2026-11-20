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

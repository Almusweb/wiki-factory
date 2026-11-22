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

**Aggiornamento (2026-11-21 21:40):** gap parziale, resta aperto. `file_sync.rs` è ora letto in parte (righe 1-130, 445-704, 1280-1421: lettura e scrittura di snapshot e coda, `write_json`, `read_json`), restano non letti 130-445 e 705-1280 ([[llm-wiki-archivi-persistenza]] §Aggiornamenti dossier r4; gap `llm-wiki-file-sync-scritture-non-lette`). Letti anche `file_history.rs` 1-340, `persist.ts` 1-260, `ingest-cache.ts`, `dedup-storage.ts`, `ingest-queue.ts` 90-200, `lint-config.ts`, `scheduled-import.ts` 345-440. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r4.md §File letti e non letti]

**Aggiornamento (2026-11-21, TSK-007):** verifica della parte assegnata a US-015 (scrittura generica, sincronizzazione e osservazione dei file, persistenza di coda dedup e lint, scritture delle cache di ingest e delle didascalie). **Coperti:** stato persistito di `file_sync.rs` (righe 1-444 e 1290-1409), scrittura generica di `fs.rs` e wrapper TS, `dedup-queue.ts` (1-120), `lint-store.ts` (nota: il precedente aggiornamento lo elencava ancora tra i non letti, ma la fetta B lo riporta letto), `ingest.ts` per cache e didascalie, `agent/tools.rs`, `session.rs`, `api_server.rs`, `file_history.rs` 70-469. **Scoperti (restano aperti):** `file_sync.rs` 445-1289 e da 1410; `file_history.rs` 1-69 (scrittura di `history-settings.json`) e da 470; `fs.rs` 651-999 e 2230-3300; `search.rs`, `proxy.rs`, `lib.rs` oltre 780, `chat-panel.tsx`, `lint.ts`, `dedup.ts`, `inactiveQueueWrite` di `ingest-queue.ts`. Il gap **resta aperto**: la parte di US-015 non è chiudibile finché non è letto il meccanismo di scrittura di `history-settings.json` (nuovo raw su `file_history.rs`). Sintesi in [[llm-wiki-archivi-persistenza]] §Esito della verifica di US-015. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Copertura del gap `llm-wiki-persistenza-codice-non-letto`]

**Aggiornamento (2026-11-21, TSK-008):** verifica della parte assegnata a US-016. **Coperti:** cascata di cancellazione di una pagina (`wiki-page-delete.ts` per intero); ciclo di vita delle sorgenti (`source-lifecycle.ts` righe 137-233, 448-604, 629-662 e 691-708); pulizia delle review (`pruneDeletedPagesFromReviews`); cancellazione dei file di chat (`chat-panel.tsx` 235-265); chiamanti e id di sessione di `append_turn` (`lib.rs`, `api_server.rs:2069-2080`; correzione: `agent/runtime.rs` non è chiamante, l'ipotesi nel testo del gap è superata); endpoint dell'API che scrivono (tabella delle rotte completa); `delete_file`, `copy_file`, `copy_directory` di `fs.rs`. **Scoperti (restano aperti per US-016):** chiamanti dei wrapper `copyFile` e `copyDirectory`; origine dell'id di sessione e sua sanitizzazione (gap `llm-wiki-id-chat-sessione`); corpi di `handle_embed_page`, `handle_rescan`, `resolve_review_items`, `write_raw_review_array`; cancellazione dei file `agent-sessions/` fuori da `session.rs`; chiamanti di `optimizeChunkVectorTableBestEffort`; chiamanti «solo mappa» non riletti nel sorgente; `source-lifecycle.ts` righe 1-136, 236-447, 666-690, 711-fine. Il gap **resta aperto**. Sintesi in [[llm-wiki-operazioni-distruttive]] §Esito della verifica di US-016. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Copertura del gap `llm-wiki-persistenza-codice-non-letto`]

**Aggiornamento (2026-11-21, fetta D):** parte di US-015, gap **resta aperto** (parziale). Ora letti nei punti di scrittura: `file_history.rs` righe 1-550 (scrittura di `history-settings.json` a 304-334, cronologia a 285-288, 227-228, 423-424), `session.rs` righe 1-217 (scrittura a 166-175), `page_embedding.rs` righe 1-460, `vectorstore.rs` righe 1-730, `fs.rs` 1295-1344, `scheduled-import.ts` 380-440, `proxy.rs` 45-85 e 490-529, `lib.rs` 400-420 e 550-600, `api_server.rs` 725-765, `server_bind.rs` 10-45. L'ostacolo che impediva la chiusura della parte US-015 (meccanismo di scrittura di `history-settings.json`) è rimosso: diretta. Restano scoperti (non più per US-015): `file_history.rs` da 550, `file_sync.rs` 445-1289 e da 1410, `search.rs`, `proxy.rs` 85-490 e oltre 529, `lib.rs` oltre 780, `chat-panel.tsx`, `lint.ts`, `dedup.ts`, `inactiveQueueWrite` di `ingest-queue.ts`, `fs.rs` 651-999 e 2230-3300. Il gap resta aperto per le altre storie. [^src: raw/2026-11-21-repo-llm_wiki-persistenza-d.md §Note di estrazione] [^src: raw/2026-11-21-repo-llm_wiki-persistenza-d.md §Parte B. Atomicità dei sette archivi senza riga di codice (US-015 AC1)]

**Aggiornamento (2026-11-21, TSK-013):** parte di US-025, gap **resta aperto**. Dal dossier [[2026-11-21-repo-llm_wiki-dossier-ep004-r1]] ora letti: `chat-store.ts` (per intero), `persist.ts` (per intero), `chat-panel.tsx` righe 1-1829 (prima solo 235-265), `App.tsx` (per intero), `auto-save.ts` (per intero), `reset-project-state.ts` (per intero), `persist.integration.test.ts` (per intero), `commands/fs.ts` righe 1-120, `session.rs` (per intero). Ricerca testuale globale della sessione principale: `grep -rn "chats/" src` trova come unica cancellazione `chat-panel.tsx:249`, nessun riferimento a `chats` in `src-tauri/src`; `grep -rn "agent-sessions"` su `src`, `src-tauri/src`, `mcp-server`, `extension` trova solo `session.rs:107, 182` e un test (`session.rs:261`), nessuna cancellazione di `agent-sessions/`. Quindi la riserva di TSK-008 («`agent-sessions/` non cercato») è sciolta per questi ambiti. Restano scoperti per US-025: corpo di `delete_file` e `run_guarded` (`fs.rs`), `chat-panel.tsx` oltre 1829, `test-helpers/fs-temp.ts`, `chat-store.test.ts`, altri chiamanti di `loadChatHistory`, `saveChatHistory`, `deleteConversation`, comandi Rust che potrebbero cancellare `.llm-wiki/`, cancellazioni generiche di percorso arbitrario (`deleteFile` in `agent-file-activity.tsx:41` e `review-view.tsx:195`, `delete_file` Rust). Sintesi in [[llm-wiki-rischi-persistenza]] §Esito della verifica di US-025. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r1.md §File letti e non letti] [^src: management/kanban/EP-004-verifica-rischi-di-persistenza/US-025-rischio-chat-cancellate/TSK-012.md §Chiusura]

**Aggiornamento (2026-11-21, TSK-015):** parte di US-026, gap **resta aperto**. Dal dossier [[2026-11-21-repo-llm_wiki-dossier-ep004-r2]] ora letti: `project-identity.ts` (per intero), `project-store.ts` (per intero), `wiki-store.ts` (per intero), `ingest-queue.ts` (per intero), `App.tsx` 395-655, `commands/fs.ts` 1-60 e 225-287, `persist.ts` 1-80 e 240-304, `project.rs` 1-370, `project_maintenance.rs` 1-30 e 195-274, `types/wiki.rs`, `maintenance-section.tsx` (per intero). Ricerca testuale globale della sessione principale (`src`, `src-tauri/src`, TS/TSX/RS, esclusi test): chiamanti di `ensureProjectId`, `upsertProjectInfo`, `getProjectIdByPath`, `getProjectPathById`; `store.delete(` solo a `project-store.ts:357` e `379`; `restoreQueue` di `dedup-queue.ts:273-296`; letture per id in `api_server.rs`. Restano scoperti per US-026: corpi di `read_file` e `write_file` (`fs.rs`), `project-file-sync.ts`, clip watcher, `lib.rs` (lettura del registro per id), `source-watch-config.ts`, `dedup-queue.ts` fuori dalle righe 273-296. Sintesi in [[llm-wiki-rischi-persistenza]] §Esito della verifica di US-026. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r2.md §File letti e non letti] [^src: management/kanban/EP-004-verifica-rischi-di-persistenza/US-026-rischio-identita-progetto/TSK-014.md §Chiusura]

## 2026-11-20 17:06 — llm-wiki-file-citati-non-verificati
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki (aggiornamento v2026-11-20)
**Gap:** file e cartelle citati nei commenti del codice ma non verificati: `image-caption-cache.json`, `lexical-graph.json` (commento di `dedup-storage.ts`), la cartella `raw/sources/.cache` e la cartella legacy `.llm-wiki-imported`. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `ingest.ts`, `dedup-storage.ts` e dei punti d'uso). Non bloccante.
**Impatto:** [[llm-wiki-archivi-persistenza]] elenca 17 archivi senza questi file, di cui non è noto se esistano come archivi.

**Aggiornamento (2026-11-21):** gap parziale, resta aperto. `image-caption-cache.json` esiste (`.llm-wiki/image-caption-cache.json`, scritto con `writeFile`) e `raw/sources/.cache` esiste come `<cartella del sorgente>/.cache/<nomefile>.txt`; `lexical-graph.json` e `.llm-wiki-imported` restano non verificati in questo giro. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §File citati nei commenti (gap 14)]

**Aggiornamento (2026-11-21, TSK-007):** verifica di US-015 AC3, **pronto per la chiusura con riserva**, non chiuso qui. Esito per file: `image-caption-cache.json` esiste come archivio (`.llm-wiki/image-caption-cache.json`, campi e scrittura diretta in [[llm-wiki-archivi-persistenza]]); `raw/sources/.cache` esiste come cartella `.cache` accanto a ogni sorgente; `lexical-graph.json` non esiste nel codice (solo il commento «when added» di `dedup-storage.ts`; ricerca testuale della fetta B su `src` e `src-tauri/src`, valida per la stringa esatta); `.llm-wiki-imported` non è un archivio, è un nome di esclusione dalla scansione (`scheduled-import.ts:235`). Riserva: la fetta C2 del 2026-11-21 dichiara gli ultimi due «non verificati» nei suoi file e il solo uso di `.llm-wiki-imported` viene dalla sessione, non da un indice globale. La chiusura spetta all'utente su conferma della riserva. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §File e cartelle citati e non verificati] [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Punto 7: `.llm-wiki-imported`]

**Risolto:** 2026-11-21 — [[llm-wiki-archivi-persistenza]]: `image-caption-cache.json` è un archivio (`.llm-wiki/image-caption-cache.json`), `raw/sources/.cache` è la cartella `.cache` accanto a ogni sorgente, `lexical-graph.json` non esiste nel codice (solo un commento) e `.llm-wiki-imported` è un nome di esclusione dalla scansione, non un archivio. Riserva: gli ultimi due restano «non verificati» nella fetta C2 e l'uso di `.llm-wiki-imported` non deriva da un indice globale (residuo non bloccante). Chiusura approvata dall'utente in chat. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §File e cartelle citati e non verificati] [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Punto 7: `.llm-wiki-imported`]

## 2026-11-20 17:06 — llm-wiki-app-state-percorso
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki (aggiornamento v2026-11-20)
**Gap:** il percorso effettivo di `app-state.json` e il comportamento del plugin store su file corrotto non sono determinabili dal campione. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (configurazione del plugin store in `lib.rs` e documentazione del plugin). Non bloccante.
**Impatto:** [[llm-wiki-archivi-persistenza]] e [[llm-wiki-gestione-file-corrotti]] non possono dire dove sia lo store né come reagisca a un file corrotto.

**Aggiornamento (2026-11-21):** gap parziale, resta aperto. Il percorso è `<app_data_dir>/app-state.json` ([[llm-wiki-archivi-persistenza]]); il path OS risolto da `app_data_dir` per piattaforma e il comportamento su file corrotto non sono verificati. [^src: raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md §Archivio dello stato app (gap 15)]

**Aggiornamento (2026-11-21, TSK-006):** verifica di US-014 sul raw ingerito: nessun nuovo elemento rispetto all'aggiornamento sopra, il gap **non è pronto per la chiusura**. Restano non verificati (a) il percorso fisico di `app_data_dir` per sistema operativo (dipende da Tauri) e (b) il comportamento del plugin store su file corrotto (sorgente e documentazione del plugin assenti dal raw). Per chiuderlo serve un nuovo raw: configurazione del plugin store e documentazione Tauri, oppure un'osservazione in esecuzione. Sintesi in [[llm-wiki-archivi-persistenza]]. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Store applicativo (`app-state.json`)]

**Aggiornamento (2026-11-21, fetta D):** la fetta D ([[2026-11-21-repo-llm_wiki-persistenza-d]]) ha letto le due parti rimaste: (a) il percorso per sistema operativo, e (b) il comportamento del plugin store su file corrotto, dal sorgente di `tauri-plugin-store` 2.4.3, `tauri` 2.11.1 e `dirs` 6.0.0 da crates.io (dipendenze, non codice del cliente). Il punto (a) è accettato dall'utente. [^src: raw/2026-11-21-repo-llm_wiki-persistenza-d.md §Catena di risoluzione del percorso]

**Risolto:** 2026-11-21 — [[llm-wiki-archivi-persistenza]] e [[llm-wiki-gestione-file-corrotti]]: `app-state.json` sta in `<data_dir>/com.llmwiki.app/app-state.json`, con `data_dir` = `$XDG_DATA_HOME` (se assoluto) o `$HOME/.local/share` su Linux, `$HOME/Library/Application Support` su macOS, «Roaming AppData» su Windows; su file corrotto il plugin ignora l'errore di caricamento (store vuoto), non fonde dati parziali e la prima scrittura riscrive il file con la sola cache; i lettori Rust ripiegano su default, proxy spento o ultimo valore in cache (API). Residuo dichiarato, non bloccante: interno di `dirs-sys` e `tauri/src/path/mod.rs` e pacchetto JavaScript `@tauri-apps/plugin-store` non letti; nessuna prova in esecuzione (le conseguenze su file corrotto sono deduzioni non testate); contenitori e sandbox non verificati; `Cargo.lock` non riaperto (versioni dichiarate dal richiedente). Chiusura su valutazione del wiki-keeper dopo l'accettazione del punto (a) da parte dell'utente. [^src: raw/2026-11-21-repo-llm_wiki-persistenza-d.md §Catena di risoluzione del percorso] [^src: raw/2026-11-21-repo-llm_wiki-persistenza-d.md §File corrotto: che cosa si legge nel plugin]

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

**Aggiornamento (2026-11-21, TSK-008):** verifica di US-016 AC5, **pronto per la chiusura con riserva**, non chiuso qui (la chiusura spetta all'utente). Esito: `vector_upsert` e `vector_delete` non hanno chiamanti nell'ambito cercato (stringa esatta; TS non di test sotto `src`; Rust sotto `src-tauri/src` con confine di parola): compaiono solo la registrazione (`lib.rs:672,674`), le definizioni e i test di `vectorstore.rs`; `embedding.ts` usa solo i comandi v2 e dopo un rebuild forzato elimina la tabella legacy (`vector_drop_legacy`). Quindi l'applicazione non risulta scrivere né cancellare in formato v1. Riserva: i comandi restano esposti al frontend, `mcp-server`, `extension` e `scripts` sono fuori ambito, e i raw del 2026-11-21 dichiarano «non verificati» `api_server.rs`, `agent/tools.rs`, `search.rs` solo perché non cercati da quelle fette (la ricerca testuale della fetta C li copre). Sintesi in [[llm-wiki-operazioni-distruttive]] §Esito della verifica di US-016. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Vecchio formato vettoriale (v1): chiamanti]

**Risolto:** 2026-11-21 — [[llm-wiki-operazioni-distruttive]]: `vector_upsert` e `vector_delete` (v1) non hanno chiamanti nell'ambito cercato (solo registrazione in `lib.rs`, definizioni e test di `vectorstore.rs`); `embedding.ts` usa solo i comandi v2, quindi l'applicazione non risulta scrivere né cancellare in formato v1. Riserva: i comandi restano esposti al frontend e `mcp-server`, `extension` e `scripts` sono fuori ambito (residuo non bloccante). Chiusura approvata dall'utente in chat. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Vecchio formato vettoriale (v1): chiamanti]

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

**Aggiornamento (2026-11-21):** gap parziale, resta aperto. Raccolte dichiarazioni di terzi (non misure del progetto, versioni vecchie, un solo progetto ciascuna): indice LanceDB di 3,8 GB in v0.4.23 con 94,7% di versioni vecchie, ricostruzione oltre 2 ore su circa 46.000 chunk, 5.064 PNG per 2,2 GB da 16 PDF, `GET /graph` circa 24 s in v0.6.11, cronologia con «migliaia» di file ([[llm-wiki-archivi-persistenza]]). Resta: le misure del progetto sintetico deciso in Q_004, non ancora disponibili; i dati di terzi non le sostituiscono. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §3. Dimensioni reali degli archivi (gap `llm-wiki-archivi-dimensioni`)]

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

**Aggiornamento (2026-11-21, TSK-013):** gap parziale, resta aperto. Risolto uno dei due punti rimasti: la UI passa l'id di conversazione come `sessionId` (`chat-panel.tsx:992` e `1070`, osservato), quindi una conversazione chat e la sua sessione agente condividono l'identificativo e `agent-sessions/<id>.json` non è toccato dal cestino. Resta aperto se il `projectId` delle sessioni coincida con l'id di `project.json`. Il valore predefinito di `persistSession` nel percorso in streaming non è letto (il percorso non-streaming passa `persistSession: false`, riga 1072). [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r1.md §Stringa `agent-sessions/`]

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

**Aggiornamento (2026-11-21, TSK-015):** gap parziale, **resta aperto**. Dal dossier [[2026-11-21-repo-llm_wiki-dossier-ep004-r2]]: il chiamante UI è confermato in `handleImportProject` (`maintenance-section.tsx:218-230`: `import_project_archive`, poi `openProject` e `addToRecentProjects`, senza passare da `handleProjectOpened`); `import_project_archive_inner` non legge né rigenera l'id; `openProject` ritorna lo stesso id se `project.json` è nello zip e `upsertProjectInfo` lo assegna al nuovo percorso senza controllo (`project-identity.ts:52-54, 95-108`). Resta **non conclusivo**: la sovrascrittura del percorso nel registro e la scrittura dell'ingest nella copia sono deduzioni non testate; non letti clip watcher e `lib.rs`. Sintesi in [[llm-wiki-rischi-persistenza]] §Esito della verifica di US-026. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r2.md §Collisione di id dopo l'import (punto separato, rischio 3, non allarga l'esito del rischio 2)]

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

**Aggiornamento (2026-11-21 21:40):** gap parziale, resta aperto. Il punto `history-settings.json` è ora letto: `file_history.rs` 1-340, scrittura diretta (`:304-334`, 324-326) e lettore con default che spegne la cronologia (`:42-48, 71-81`) ([[llm-wiki-rischi-persistenza]] §Esito della verifica di US-028, [[llm-wiki-gestione-file-corrotti]]). Resta non verificato `inactiveQueueWrite` di `ingest-queue.ts` (il dossier ha letto `ingest-queue.ts` 90-200 e non lo cita). [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r4.md §2. Che cosa resta dopo un crash e come reagisce il lettore (AC3, AC5)]

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

**Aggiornamento (2026-11-22):** gap parziale, resta aperto. La skill `llm_wiki_skill` (`main`, `642b438`) **dichiara**, per API v1 e app 0.4.10+ (non per v0.6.13), il comportamento di `search` (modi `keyword`, `vector` e `hybrid`, campi per risultato, `queryEmbedding` che salta l'embed del server) e di `sources/rescan` (risultato con `queue` e `changedTasks`), in [[llm-wiki-skill-api-v1-dichiarata]]. È documentazione riferita a una versione più vecchia e non verificata nel codice: non sostituisce la lettura di `search.rs`, `page_embedding.rs`, `file_sync.rs` e `agent/events.rs` in v0.6.13, e per `search` v0.6.13 ha già `graphHits` che la skill non cita ([[llm-wiki-skill-vs-app-v0-6-13]]). [^src: raw/2026-11-22-repo-llm_wiki_skill.md §API surface]

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

**Aggiornamento (2026-11-22):** gap parziale, resta aperto. La skill `llm_wiki_skill` **dichiara**, per API v1 e app 0.4.10+ (non per v0.6.13), che il token si imposta in Settings, API Server, che «Enable local HTTP API» è attivo di default, che il token è vuoto di default e che con `tokenSource` uguale a `env` il campo token della UI è ignorato ([[llm-wiki-skill-api-v1-dichiarata]]). Descrive la UI solo a parole, non il codice: `api-server-section.tsx` oltre la riga 399, `project-binding.ts` e `version.ts` restano non letti. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Dipendenze esterne] [^src: raw/2026-11-22-repo-llm_wiki_skill.md §API surface]

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

**Aggiornamento (2026-11-21):** gap parziale, resta aperto. Osservato in v0.6.13: nessuna occorrenza di `single_instance` o `single-instance` sotto `src-tauri` (`git grep`); il Clip server ritenta il bind fino a 3 volte e il riavvio fino a 10 (`clip_server.rs:18-19`). Dichiarato (segnalatore, #648, v0.6.8 circa): non si possono aprire due istanze perché il Clip server va in conflitto. Deduzione non testata: la seconda istanza non è impedita dall'app; la raggiungibilità dello scenario a due processi non è determinata (la seconda istanza potrebbe non partire, oppure partire con il Clip server non funzionante) e cosa accada oltre al fallimento del bind non è letto. Resta la prova con due processi ([[llm-wiki-rischi-persistenza]]). [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §6. Altre dichiarazioni pertinenti (non chiudono)]

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

**Aggiornamento (2026-11-21):** gap parziale, resta aperto. Dichiarato (contributori, #170, #193, #228): eseguono in locale `npm run test:mocks`, `typecheck` e `build`. Osservati gli script di `package.json:8, 12-14` (`test` = `test:mocks` + `test:llm`, `typecheck` = `tsc --build`) ([[llm-wiki-test-e-ci]]). Restano: i test Rust (`cargo test`, nessuna issue letta lo cita), `.github/scripts/*` e la documentazione di contribuzione. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §6. Altre dichiarazioni pertinenti (non chiudono)]

## 2026-11-21 20:35 — llm-wiki-identita-innesco-e-read-file
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-dossier-ep004-r2
**Gap:** non è determinabile per lettura come un `project.json` diventi illeggibile o non valido (la scrittura avviene solo quando il file manca o non è valido, `project-identity.ts:58-66`; una scrittura interrotta è un candidato, deduzione non testata) e non è letto il comportamento di `read_file` Rust su errore transitorio (file bloccato, permessi), che il `catch` di `ensureProjectId` tratterebbe come «corrotto». Fonte del gap: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r2.md §Esito proposto: CONFERMATO per lettura (con una riserva sul negativo).
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (corpo di `read_file` e `write_file` in `fs.rs`); l'innesco reale richiede esecuzione, fuori dal metodo di EP-004 (Q_003). Non bloccante.
**Impatto:** [[llm-wiki-rischi-persistenza]] dichiara l'esito del rischio 2 confermato per lettura ma non può dire con quale probabilità si verifichi.

## 2026-11-21 20:35 — llm-wiki-dedup-queue-riscrittura
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-dossier-ep004-r2
**Gap:** `restoreQueue` di `dedup-queue.ts:273-296` scarta per id i task con `projectId` diverso (ricerca globale della sessione principale), ma non è verificato se riscriva il file su disco come fa la coda di ingest (`saveQueue`), cioè se lo scarto sia permanente anche per la coda di dedup. Non letti nemmeno `project-file-sync.ts` (se i sorgenti siano riaccodati dopo la perdita dei task) e `file-change-queue.json` per id. Fonte del gap: management/kanban/EP-004-verifica-rischi-di-persistenza/US-026-rischio-identita-progetto/TSK-014.md §Chiusura.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `dedup-queue.ts` oltre le righe 273-296 e di `project-file-sync.ts`). Non bloccante.
**Impatto:** [[llm-wiki-rischi-persistenza]] non può dire se l'impatto del rischio 2 includa la perdita dei task di dedup.
**Aggiornamento (2026-11-21 21:15):** un commento in `dedup-queue.ts:13` dichiara «Mirrors `ingest-queue.ts` almost line-for-line»: la coda di dedup è una copia dichiarata di quella di ingest (duplicazione TS-TS), indizio che anche la riscrittura su disco dopo lo scarto possa essere analoga a `saveQueue`; resta non verificato, il gap rimane aperto. [^src: management/kanban/EP-004-verifica-rischi-di-persistenza/US-029-rischio-logica-duplicata/TSK-018.md §Chiusura (Correzione)]

## 2026-11-21 20:35 — llm-wiki-source-watch-default
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-dossier-ep004-r2
**Gap:** non sono letti i valori predefiniti di `sourceWatchConfig` (`source-watch-config.ts`, `DEFAULT_SOURCE_WATCH_CONFIG`): con l'id nuovo `projectFileSyncEnabled` ripiega su `true` e `sourceWatchConfig` sul `default` o sul legacy, ma non è noto se questo riattivi davvero l'osservazione dei sorgenti. Fonte del gap: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r2.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (`src/lib/source-watch-config.ts`). Non bloccante.
**Impatto:** [[llm-wiki-rischi-persistenza]] non può quantificare il reset silenzioso delle impostazioni di osservazione nel rischio 2.

**Aggiornamento (2026-11-22):** gap parziale, resta aperto. La skill `llm_wiki_skill` **cita**, per API v1 e app 0.4.10+ (non per v0.6.13), che il `sourceWatchConfig` regola il `rescan` (filtri di tipo, directory escluse, dimensione massima) e che in un esempio il `.json` risulta escluso di default; il raw segnala che quei default non sono documentati altrove nella skill (voce n. 14 di [[llm-wiki-skill]]). Non sono i valori di `DEFAULT_SOURCE_WATCH_CONFIG` di v0.6.13 né rispondono alla domanda sul ripiego dell'id nuovo. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §API surface] [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Gap evidenti]

## 2026-11-21 20:50 — llm-wiki-registro-concorrenza-reale
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-dossier-ep004-r3
**Gap:** non è determinabile per lettura se due `upsertProjectInfo` si sovrappongano davvero (tempi di IPC, azioni utente) né come il plugin `@tauri-apps/plugin-store` (JS) e `tauri-plugin-store` (Rust) ordinino `get` e `set` e se due `load()` con lo stesso nome condividano l'istanza: pacchetto JS e `src/lib.rs`, `src/store.rs` del plugin non letti dal dossier. Se `get`+`set` fossero atomici lato Rust l'interleaving non cambierebbe, perché il difetto è nel RMW lato TS. Fonte del gap: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r3.md §4. Rischio di aggiornamento perso (AC5, AC6).
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (sorgente del plugin store, non disponibile offline per `repo-sync`); la sovrapposizione reale richiede esecuzione, fuori dal metodo di EP-004 (Q_003). Non bloccante.
**Impatto:** [[llm-wiki-rischi-persistenza]] dichiara l'esito del rischio 3 «non conclusivo» sulla concorrenza reale e non può dire se o con quale frequenza il registro perda voci.

**Aggiornamento (2026-11-21):** gap parziale, resta aperto. Il dossier r3 ragionava «dentro un unico frontend, finestra unica». Osservato in v0.6.13: nessun `single_instance` o `single-instance` sotto `src-tauri` (`git grep`); il Clip server ritenta il bind fino a 3 volte e il riavvio fino a 10 (`clip_server.rs:18-19`). Dichiarato (segnalatore, #648, v0.6.8 circa): la seconda istanza va in conflitto sul Clip server. Deduzione non testata: l'app non esclude per sé una seconda istanza che condividerebbe `app-state.json`; la raggiungibilità dello scenario non è determinata e cosa accada oltre al fallimento del bind non è letto. Restano non letti il pacchetto JS e `src/lib.rs`, `src/store.rs` del plugin store ([[llm-wiki-rischi-persistenza]]). [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §6. Altre dichiarazioni pertinenti (non chiudono)]

## 2026-11-21 20:50 — llm-wiki-registro-lettura-fallita-frequenza
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-dossier-ep004-r3
**Gap:** non è determinabile per lettura con quale frequenza `store.get` rifiuti mentre `store.set` riesce (unico caso in cui `loadRegistry` porterebbe a un registro di una voce senza avviso, `project-identity.ts:80-83, 107`); con `getStore()` rotto in modo persistente fallirebbe anche la scrittura. Fonte del gap: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r3.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (sorgente del plugin store e prova in esecuzione). Non bloccante.
**Impatto:** [[llm-wiki-rischi-persistenza]] non può quantificare il percorso «lettura fallita, poi scrittura» del rischio 3.

## 2026-11-21 20:50 — llm-wiki-registro-rientro-aperture
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-dossier-ep004-r3
**Gap:** restano non verificati: se il pulsante di importazione sia legato a `projectToolBusy` e se esista una guardia fra import e apertura (`maintenance-section.tsx`, binding non riletto); se `React.StrictMode` (`main.tsx:23-27`) raddoppi `init` anche in produzione; la dimensione reale della finestra fra due aperture ravvicinate (`handleSelectRecent`, `handleOpenProject` senza guardia di rientro, `App.tsx:595-617`). Chiusi dalla ricerca globale della sessione principale: elenco dei chiamanti di `openProject(` e `createProject(`, scrittore unico del registro, nessuna `WebviewWindow`. Fonte del gap: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r3.md §Gap evidenti; management/kanban/EP-004-verifica-rischi-di-persistenza/US-027-rischio-scritture-registro/TSK-016.md §Chiusura.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (rilettura di `maintenance-section.tsx` e della configurazione di build). Non bloccante.
**Impatto:** [[llm-wiki-rischi-persistenza]] non può dire se le sovrapposizioni fra azioni utente indicate come deduzione non testata siano raggiungibili dall'interfaccia.

## 2026-11-21 21:05 — llm-wiki-chunking-alternanza-frequenza
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-dossier-ep004-r5
**Gap:** i chiamanti dei due percorsi di embedding sono noti dalla ricerca globale (`embedPage` da `ingest.ts:1572, 3613` e `deep-research.ts:696`; `embed_wiki_page` da `api_server.rs:1915`, via MCP `embedPage`), ma non è determinabile per lettura con quale frequenza una stessa pagina sia scritta da entrambi i lati, né se esistano test che confrontano i due chunker o fissano come comportamento le differenze trovate (resto di `text-chunker.test.ts` e `embedding.test.ts` non letto). Fonte del gap: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r5.md §Gap evidenti; management/kanban/EP-004-verifica-rischi-di-persistenza/US-029-rischio-logica-duplicata/TSK-018.md §Chiusura.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura dei test e dei chiamanti); la frequenza reale richiede esecuzione, fuori dal metodo di EP-004 (Q_003). Non bloccante.
**Impatto:** [[llm-wiki-rischi-persistenza]] dichiara il rischio 5 confermato per lettura ma non può dire quanto spesso incida su costo e coerenza dell'indice.

## 2026-11-21 21:05 — llm-wiki-id-legacy-enumerazione-cache
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-dossier-ep004-r5
**Gap:** non sono letti il comportamento di `listDirectory` (`src/commands/fs.ts`, nascosti, collegamenti simbolici) e di `list_directory` Rust, né altre invalidazioni della cache `legacyStemOwnerCounts` / `attemptedLegacyVectorCleanup` fuori da `embedding.ts`. Per questo l'equivalenza della pulizia dell'id legacy fra TS e Rust resta non conclusiva. Fonte del gap: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r5.md §2.1 Esito del punto 2.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (`fs.ts` `listDirectory`, `fs.rs` `list_directory`, chiamanti della cache). Non bloccante.
**Impatto:** [[llm-wiki-rischi-persistenza]] non può chiudere l'esito del punto 2 del rischio 5 né quantificare il caso di conteggio superato.

## 2026-11-21 21:05 — llm-wiki-override-llm-resolveconfig
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-dossier-ep004-r5
**Gap:** non sono letti `resolveConfig` (preset-resolver), `findLlmPreset` (registro dei preset) e il tipo `ProjectLlmOverride` (`wiki-store.ts`): l'equivalenza della risoluzione LLM per progetto fra `resolveProjectLlmConfig` (TS) e `project_llm_config` (Rust) resta non conclusiva; la sola differenza trovata è `presetId` vuoto. Fonte del gap: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r5.md §4.2 `projectLlmOverrides`.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (`preset-resolver`, `llm-presets`, `wiki-store.ts`). Non bloccante.
**Impatto:** [[llm-wiki-rischi-persistenza]] non può dire se l'API locale e l'agente usino lo stesso modello dell'interfaccia per un progetto.

## 2026-11-21 21:05 — llm-wiki-source-watch-normalizzazione-rust
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-dossier-ep004-r5
**Gap:** non sono letti gli helper Rust `normalize_ext_list`, `normalize_string_list`, `SourceWatchRules` e `rescan_project_files` (`file_sync.rs` righe 250-380, 710-760 e oltre 1090), né la cache di `load_app_state` rispetto alle scritture del frontend: non è confermata né smentita la differenza sulle estensioni legacy (`png/jpg/jpeg`) e l'equivalenza su input validi di `sourceWatchConfig`. Fonte del gap: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r5.md §4.3 `sourceWatchConfig` e `projectFileSyncEnabled`.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (`file_sync.rs` e `api_server.rs` residui). Non bloccante.
**Impatto:** [[llm-wiki-rischi-persistenza]] non può dire se la riscansione avviata dall'API usi gli stessi filtri dell'interfaccia.

## 2026-11-21 21:05 — llm-wiki-coppie-id-pagina-non-confrontate
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-dossier-ep004-r5
**Gap:** la coppia `wikiPageIdFromPath` (`embedding.ts:450-462`) e `vector_page_id` (`page_embedding.rs:282-290`) esiste su entrambi i lati ma è fuori dal perimetro di TSK-018 e non è stata confrontata; restano ignote anche altre coppie duplicate TS/Rust oltre a quelle lette. Rilevante perché una divergenza nell'id cambierebbe lo schema `page_id#chunk_index` e la pulizia dell'id legacy. Fonte del gap: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r5.md §Gap evidenti (punto 6).
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (confronto mirato delle due funzioni; eventuale TSK dedicato). Non bloccante.
**Impatto:** [[llm-wiki-rischi-persistenza]] dichiara l'esito del rischio 5 senza coprire la derivazione dell'id di pagina; vedi anche [[llm-wiki-versioni-e-migrazioni]] (§Identificatore di pagina).

## 2026-11-21 21:05 — llm-wiki-commenti-allineamento-discrepanza
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-dossier-ep004-r5
**Gap:** il dossier r5 riporta commenti che dichiarano l'allineamento fra le copie TS/Rust (`text-chunker.ts:4-7`, `page_embedding.rs:507-509`, `llm-task-routing.ts:20-22`, `api_server.rs:2397`), mentre la ricerca testuale globale della sessione principale (TSK-018 §Chiusura) riporta nessun commento di allineamento salvo `file_sync.rs:142`. Le due fonti non sono riconciliate; la causa più probabile sono le stringhe cercate diverse da quelle dei commenti, ma non è verificata. Serve rieseguire la ricerca con le stringhe proposte dal dossier (`aligned`, `Keep`, `mirror`, `Match `, `in sync`). Fonte del gap: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r5.md §1. Chunking: le due implementazioni affiancate (AC2); management/kanban/EP-004-verifica-rischi-di-persistenza/US-029-rischio-logica-duplicata/TSK-018.md §Chiusura.
**Sospetta fonte:** nessuna fonte chiara, serve nuova ricerca testuale della sessione principale (non un raw nuovo). Non bloccante.
**Impatto:** [[llm-wiki-rischi-persistenza]] riporta entrambe le versioni in `## Contradictions` e non può dire se l'allineamento fra le copie sia dichiarato solo nei quattro commenti letti o anche altrove.
**Risolto:** 2026-11-21 — la ricerca di TSK-018 era errata (stringhe non coincidenti); ripetuta a comando con `grep -rniE` su `aligned`, `in sync`, `mirror(s|ed|ing)?`, `Match `, i quattro commenti del dossier esistono, a coppie (`text-chunker.ts:4-7` ↔ `page_embedding.rs:507-509`; `llm-task-routing.ts:20-22` ↔ `api_server.rs:2397`): duplicazione dichiarata e intenzionale, allineamento manuale. Emergono anche `dedup-queue.ts:13` ed `extract-source-images.ts:20`. [^src: management/kanban/EP-004-verifica-rischi-di-persistenza/US-029-rischio-logica-duplicata/TSK-018.md §Chiusura (Correzione)]
**Risolto (2026-11-21 21:25, rimando alla wiki):** esito registrato in [[llm-wiki-rischi-persistenza]] (§Esito della verifica di US-029 e `## Contradictions`, voce «Rischio 5: commenti di allineamento»), che cita il dossier [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r5.md §1. Chunking: le due implementazioni affiancate (AC2)]; pagina di origine [[2026-11-21-repo-llm_wiki-dossier-ep004-r5]]. Riga aggiunta in coda perché il registro è append-only: la chiusura precedente citava solo il kanban.

## 2026-11-21 21:25 — llm-wiki-reindex-lancedb-errore-parziale
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-dossier-ep004-r6
**Gap:** non sono determinabili per lettura l'atomicità e lo stato su disco di `drop_table`, `create_table` e `merge_insert` di LanceDB dopo un errore a metà pagina o un'uscita brusca fra `embedding.ts:705` e `:731`: il contenuto effettivo della tabella v2 resta non conclusivo (il commento del codice dichiara l'atomicità per pagina, non la verifica); stesso limite per l'errore dello svuotamento stesso (famiglia B). Fonte del gap: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r6.md §3. Che cosa resta nell'indice dopo un errore (AC3).
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (sorgente della libreria `lancedb`, non disponibile offline per `repo-sync`); la prova richiede esecuzione, fuori dal metodo di EP-004 (Q_003). Non bloccante.
**Impatto:** [[llm-wiki-rischi-persistenza]] dichiara l'esito del rischio 6 confermato sul meccanismo ma non può dire in quale stato resti la tabella dopo un errore parziale.

## 2026-11-21 21:25 — llm-wiki-reindex-segnalazione-ricerca-test
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-dossier-ep004-r6
**Gap:** non sono letti `search-view.tsx` (se la UI di ricerca mostri la modalità `keyword`/`hybrid` o l'assenza di indice, campi `mode` e `vector_hits` oggi inutilizzati dal TS), `embedding.test.ts` e `tests_v2` (se esistano test che fissano messaggio, ordine delle operazioni o il fallimento dopo lo svuotamento) e le traduzioni `it.json`, `ru.json`, `zh.json`. Fonte del gap: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r6.md §Gap evidenti (punti 3 e 4).
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura dei file indicati). Non bloccante.
**Impatto:** [[llm-wiki-rischi-persistenza]] non può dire se l'utente veda un indicatore di ricerca degradata dopo un re-index fallito.

## 2026-11-21 21:25 — llm-wiki-reindex-page-id-concorrenza-reale
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-dossier-ep004-r6
**Gap:** non è determinabile per lettura con quale frequenza i progetti reali abbiano nomi di pagina rifiutati da `validate_page_id_common` (`vectorstore.rs:78-114`), unica causa di errore post-svuotamento prevedibile e non controllata prima; né se un `embedPage` di ingest (`ingest.ts:1572, 3613`, `deep-research.ts:696`) eseguito durante la ricostruzione possa essere sovrascritto da righe preparate prima; né il comportamento del processo se l'app è chiusa fra `embedding.ts:705` e `:731` o se il pulsante resti disabilitato dopo un errore al passo di svuotamento (stato `running`). Fonte del gap: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r6.md §5. Il rilancio riparte da zero? Che cosa impedirebbe il recupero completo? (AC4).
**Sospetta fonte:** nessuna fonte chiara; la frequenza e la temporizzazione reali richiedono esecuzione, fuori dal metodo di EP-004 (Q_003). Non bloccante.
**Impatto:** [[llm-wiki-rischi-persistenza]] non può quantificare quanto spesso il re-index fallisca in modo deterministico o possa perdere un aggiornamento concorrente; la gravità proposta (media o bassa) dipende da questo.

**Aggiornamento (2026-11-21):** gap parziale, resta aperto. Solo il primo punto (frequenza dei nomi rifiutati) riceve un dato, dichiarato e non del progetto: 447 pagine su 6.566 (6,8%) rifiutate in v0.4.23 sotto una regola più stretta, poi allargata in v0.4.24 (#394, #396). Osservata la regola in v0.6.13: rifiuta vuoto, oltre 256 caratteri, controllo, `\`, `'`, `"` e caratteri invisibili (`vectorstore.rs:67, 78-114`); la frequenza con la regola attuale non si stima ([[llm-wiki-versioni-e-migrazioni]], [[llm-wiki-rischi-persistenza]]). Restano non toccati: `embedPage` di ingest durante la ricostruzione, chiusura dell'app fra `embedding.ts:705` e `:731`, stato `running` dopo un errore allo svuotamento. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §4. Nomi di pagina rifiutati dall'indice vettoriale (gap `llm-wiki-reindex-page-id-concorrenza-reale`)]

## 2026-11-21 21:40 — llm-wiki-atomicita-fs-rename-windows
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-dossier-ep004-r4
**Gap:** non sono determinabili per lettura: se `std::fs::rename` su Windows sostituisca la destinazione esistente (il commento di `page_embedding.rs:355-356` lo nega, ma è una dichiarazione degli autori; se non sostituisse, `lint-config.json` e `scheduled-import-db.json` fallirebbero con errore senza perdere il vecchio file, deduzione non testata); le garanzie del file system sull'ordine dei dati dopo un crash e se un file atomico possa risultare vuoto dopo un'interruzione di corrente (nessuna `sync_all` negli archivi dell'inventario, `sync_all` solo in `agent/tools.rs:790` e `project_maintenance.rs:344`); l'atomicità interna di LanceDB (si somma a `llm-wiki-reindex-lancedb-errore-parziale`). Fonte del gap: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r4.md §5. Esito del rischio 4 (AC6); management/kanban/EP-004-verifica-rischi-di-persistenza/US-028-rischio-atomicita-eterogenea/TSK-022.md §Chiusura.
**Sospetta fonte:** nessuna fonte chiara; i sorgenti di `std` e `lancedb` sono fuori dal repo e la prova richiede esecuzione, fuori dal metodo di EP-004 (Q_003). Non bloccante.
**Impatto:** [[llm-wiki-rischi-persistenza]] dichiara l'esito del rischio 4 confermato sul meccanismo ma non può dire se una scrittura atomica sopravviva a una perdita di alimentazione né come si comporti la rinomina su Windows.

## 2026-11-21 21:40 — llm-wiki-file-sync-scritture-non-lette
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-dossier-ep004-r4
**Gap:** non sono letti `file_sync.rs` 130-445 e 705-1280 (percorsi di scrittura di `file-snapshot.json` e `file-change-queue.json`, `enqueue_paths`, `process_queue`): non si sa se un file non analizzabile (errore `Failed to parse`, `file_sync.rs:1344`) venga mai riscritto o resti tale a ogni ciclo, come gli errori siano gestiti dai chiamanti, né se uno snapshot vuoto faccia risultare «nuovi» tutti i file al rescan (deduzione non testata); non si sa nemmeno se esistano lettori di altri processi o senza `with_queue_lock` che vedano la finestra Windows di `write_json`. Fonte del gap: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r4.md §Gap evidenti (punto 2) e §3.3 Che cosa vede un lettore concorrente nella finestra.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `file_sync.rs` nei tratti indicati). Non bloccante.
**Impatto:** [[llm-wiki-archivi-persistenza]] e [[llm-wiki-gestione-file-corrotti]] non possono dire se l'errore su snapshot o coda non analizzabili sia permanente né quali effetti abbia lo snapshot vuoto sulla sincronizzazione.

## 2026-11-21 21:40 — llm-wiki-temporanei-orfani-pulizia-conteggio
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-dossier-ep004-r4
**Gap:** i file temporanei orfani (`.<nome>.<nanosecondi>.tmp`, `<chiave>.tmp-<uuid>`) restano in tre casi osservati (`fs.rs:1324/1328`, `page_embedding.rs:352/354/362-368`, `file_sync.rs:1364/1369-1374`) e nessun codice li ripulisce (ricerca globale, esclusi i test; un negativo su regex, non una prova di assenza fuori dall'ambito `src-tauri/src` e `src`); non è letto se i temporanei vengano contati nelle dimensioni degli archivi né quanti se ne accumulino (nessuna misura). Fonte del gap: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r4.md §3.4 Temporanei orfani; management/kanban/EP-004-verifica-rischi-di-persistenza/US-028-rischio-atomicita-eterogenea/TSK-022.md §Chiusura.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura del calcolo delle dimensioni, rimanda a US-018) e, per l'accumulo reale, un'esecuzione fuori metodo (Q_003). Non bloccante.
**Impatto:** [[llm-wiki-archivi-persistenza]] non può dire se i temporanei orfani incidano sulle dimensioni degli archivi o si accumulino nel tempo.

## 2026-11-21 21:40 — llm-wiki-revisioni-chiamanti-read-file-troncato
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-dossier-ep004-r4
**Gap:** non sono letti: gli altri chiamanti di `load_revision` (visibilità `pub(crate)`) e `save_revision` e di `vector_upsert_chunks_with_revision` in `page_embedding.rs` fuori dalle righe 300-420, che potrebbero esporre la finestra Windows senza il lock di `vectorstore_v2_lock`; il comportamento di `read_file` Rust su un file troncato a metà carattere UTF-8 (errore o sostituzione; i lettori TS riletti catturano qualsiasi errore); `file_history.rs` da riga 340 (ripristino 423-427, righe 423-424 della fetta D non riverificate); `persist.ts` da riga 260. Fonte del gap: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r4.md §File letti e non letti e §Gap evidenti (punti 4 e 5).
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura dei punti indicati). Non bloccante.
**Impatto:** [[llm-wiki-rischi-persistenza]] limita al percorso di `vector_upsert_chunks_inner` l'affermazione che un lettore in processo non vede la finestra di `save_revision`.

## 2026-11-21 21:40 — llm-wiki-atomicita-frequenza-test
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-dossier-ep004-r4
**Gap:** non è determinabile per lettura la frequenza reale di crash o chiusure dell'app durante una scrittura (nessuna misura), né se esistano test che fissino il comportamento su file troncato (`session.rs` righe 211 e seguenti, test di `file_history.rs` e di `file_sync.rs`, non letti); la ricerca globale esclude i test e copre solo `src-tauri/src` e `src`, non `mcp-server` né `extension`. I chiamanti applicativi dei comandi v1 (`vector_upsert`) restano nel gap `llm-wiki-vector-v1-chiamanti`. Fonte del gap: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r4.md §Gap evidenti (punti 6 e 7) e §File letti e non letti.
**Sospetta fonte:** nessuna fonte chiara; la frequenza richiede esecuzione, fuori dal metodo di EP-004 (Q_003); i test richiedono nuovo raw. Non bloccante.
**Impatto:** [[llm-wiki-rischi-persistenza]] non può quantificare la probabilità dell'impatto sui dati del rischio 4; la gravità proposta (media per le sessioni agente) è una proposta, la decisione è di US-033.

- [x] llm-wiki-embedding-cambio-modello
**Risolto:** 2026-11-21 — [[llm-wiki-rischi-persistenza]] (§Esito della verifica di US-031 e `## Contradictions`): tutto ciò che è verificabile per lettura è chiuso, esito **confermato** per lettura sul commit `e08cfce`: la dimensione è fissata dal primo chunk e nessun codice Rust legge lo schema della tabella esistente né confronta la dimensione prima di `merge_insert` (`vectorstore.rs:495-535`, ricerca testuale globale su tutto il codice Rust); la ricerca non controlla la dimensione della query (`search.rs:317-325`; `vectorstore.rs:588-675`); l'impronta di revisione include modello, endpoint, `outputDimensionality`, `extraHeaders` e parametri di chunking, non la chiave API né la dimensione reale (`page_embedding.rs:266-280`); `embedAllPages` e `embedPage` non rilevano il cambio e il re-index manuale lo assorbe (`embedding.ts:578-762`); nessun avviso né re-index al salvataggio (`settings-view.tsx:356-658`), solo un suggerimento statico (`en.json:643`). **Residuo: il comportamento interno di LanceDB a una scrittura o a una query con dimensione diversa da quella della tabella (e a `create_table` dopo `drop_table` con dimensione nuova) è «non conclusivo per lettura»**: sorgenti di `lancedb` e `arrow` non letti, nessuna esecuzione (esclusa da Q_003); il residuo non è chiuso, è tracciato nel gap `llm-wiki-embedding-lancedb-dimensioni`. Chiusura motivata da US-031 AC7 («pronto per la chiusura con evidenza verificabile, oppure resta aperto con il motivo») e dal criterio del gap (verifica della coerenza al cambio, letta nel codice). Pagina di origine [[2026-11-21-repo-llm_wiki-dossier-ep004-r7]]. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r7.md §7. Esito proposto e tabella evidenze (AC5, AC6)]

## 2026-11-21 21:55 — llm-wiki-embedding-lancedb-dimensioni
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-dossier-ep004-r7 (residuo della chiusura di `llm-wiki-embedding-cambio-modello`)
**Gap:** non è determinabile per lettura che cosa faccia LanceDB a una scrittura (`merge_insert`) o a una query (`vector_search`) con dimensione diversa da quella della tabella v2 (errore, oppure accettazione con effetti non noti), né se `create_table` dopo `drop_table` accetti una dimensione nuova (plausibile, non provato), né se la tabella possa contenere righe di modelli diversi a pari dimensione senza segnale (deduzione dal codice, non provata). Stato «non conclusivo per lettura». Fonte del gap: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r7.md §7. Esito proposto e tabella evidenze (AC5, AC6).
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (sorgente di `lancedb` e `arrow`, non disponibile offline per `repo-sync`); la prova richiede esecuzione, fuori dal metodo di EP-004 (Q_003). Si somma a `llm-wiki-reindex-lancedb-errore-parziale`. Non bloccante.
**Impatto:** [[llm-wiki-rischi-persistenza]] dichiara l'esito del rischio 7 confermato sul meccanismo dell'applicazione ma non può dire se un cambio di dimensione produca errore, stato misto o ricerca priva di senso; la gravità proposta (media) per US-033 dipende da questo.

## 2026-11-21 21:55 — llm-wiki-embedding-config-origine-rust
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-dossier-ep004-r7
**Gap:** non sono letti `load_embedding_config` (`api_server.rs`, origine della configurazione del ramo Rust), `wiki-store.ts` (tipo `EmbeddingConfig`), `project-store.ts` (`saveEmbeddingConfig`, `loadEmbeddingConfig`) e `App.tsx` (abilitazione iniziale): non si sa se esista una finestra in cui il ramo TS (store in memoria, `settings-view.tsx:470`) e il ramo Rust (configurazione persistita, `485`) usino configurazioni diverse dopo il salvataggio (deduzione non testata). Fonte del gap: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r7.md §6. I due percorsi di embedding (TS e Rust, API/MCP) (AC3, AC5) e §Gap evidenti (punto 2).
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura dei file indicati). Non bloccante.
**Impatto:** [[llm-wiki-rischi-persistenza]] non può dire se dopo un cambio di modello l'indicizzazione di una pagina via API o MCP possa usare il modello vecchio mentre il TS usa il nuovo.

## 2026-11-21 21:55 — llm-wiki-embedding-chiamanti-test-i18n
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-dossier-ep004-r7
**Gap:** non è letto come i chiamanti di `embedPage` (`ingest.ts`, `deep-research.ts`) gestiscano un errore di scrittura da dimensione diversa; non sono letti test e documentazione sul cambio di modello (`embedding.test.ts`, `embedding.real-llm.test.ts`, README, `plans/`); il suggerimento «Rebuild embeddings after changing model or dimension.» è letto solo in `en.json`, non in `it.json`, `ru.json`, `zh.json`; `dedup_embedding.ts` (altro consumatore di vettori con dimensione propria) non è aperto, fuori perimetro. Fonte del gap: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r7.md §Gap evidenti (punti 3, 4, 5, 6).
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura dei file indicati). Non bloccante.
**Impatto:** [[llm-wiki-rischi-persistenza]] non può dire se l'ingest segnali un errore di scrittura dopo un cambio di modello né se esistano test o documentazione sul cambio.

- [x] llm-wiki-token-cifratura
**Risolto:** 2026-11-21 — **confermato per lettura: nessuna cifratura né archivio protetto nel codice letto**, con residui dichiarati. Esito in [[llm-wiki-rischi-persistenza]] (§Esito della verifica di US-032 e `## Contradictions`) e [[llm-wiki-sicurezza]] (§Aggiornamenti dossier r8); pagina di origine [[2026-11-21-repo-llm_wiki-dossier-ep004-r8]]. Osservato: tutte le funzioni di salvataggio di `project-store.ts` scrivono chiavi e token così come sono (`store.set`, `localToken` con il solo `trim`), i lettori Rust usano il valore in chiaro, nessun crate o pacchetto di keyring, stronghold o cifratura nei manifest diretti; la ricerca testuale globale della sessione principale estende il negativo a tutto il codice TS e Rust (esclusi i test), con soli falsi positivi. **Residui, non chiusi e tracciati in gap separati:** permessi e protezione del file da parte di plugin e sistema operativo (`llm-wiki-segreti-permessi-file`); chiave SerpApi nei messaggi d'errore (`llm-wiki-segreti-serpapi-errori`); copie fuori dallo store, estensione e file di `.llm-wiki/` (`llm-wiki-segreti-copie-fuori-store`); plugin JS, dipendenze transitive e codice non letto (`llm-wiki-segreti-codice-non-letto`). Chiusura motivata dalla proposta del dossier e da US-032 («confermato, smentito o non conclusivo per lettura»); l'accettazione dei residui come stato finale è del maintainer. `llm-wiki-scan-credenziali` resta aperto e non è toccato. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r8.md §6. Esito proposto e tabella evidenze (AC1, AC6)]

## 2026-11-21 22:10 — llm-wiki-segreti-permessi-file
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-dossier-ep004-r8 (residuo della chiusura di `llm-wiki-token-cifratura`)
**Gap:** non è determinabile per lettura quali permessi, ACL o protezione abbia `app-state.json` sul disco dell'utente: l'app non li imposta mai (ricerca globale: una sola occorrenza, in un test di `agent/runtime.rs`), quindi valgono quelli predefiniti del plugin store e del sistema operativo (maschera di creazione, ACL ereditate dal profilo, `umask`, sandbox di Flatpak, AppImage, MSIX; cartella «Roaming» sincronizzabile nei profili di dominio su Windows), non osservabili senza leggere il file system dell'utente. Stato «non conclusivo per lettura». Fonte del gap: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r8.md §3. Permessi del file e protezione di libreria/OS (AC7): NON CONCLUSIVO.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (sorgente di `tauri-plugin-store` e `dirs-sys`, non disponibile offline per `repo-sync`); la prova richiede esecuzione, fuori dal metodo di EP-004 (Q_003). Non bloccante.
**Impatto:** [[llm-wiki-rischi-persistenza]] dichiara l'esito del rischio 8 confermato sul meccanismo dell'applicazione ma non può dire chi, oltre all'utente, legga il file; la gravità proposta (alta) per US-033 dipende da questo.

## 2026-11-21 22:10 — llm-wiki-segreti-serpapi-errori
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-dossier-ep004-r8 (residuo della chiusura di `llm-wiki-token-cifratura`)
**Gap:** la chiave di SerpApi sta nella query dell'URL (`tools.rs:1983-2003`) e su errore di rete il messaggio è formattato con l'errore di `reqwest` 0.12; non è letto se il `Display` di quell'errore includa l'URL (e quindi la chiave) né se il testo raggiunga la UI (`agent-event`, `ToolEnd.output`), la risposta dell'API, le sessioni o il modello (`redact_for_external_api` toglie solo `previousContent`). Stato «non conclusivo» (deduzione non testata). Fonte del gap: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r8.md §5. Esposizione: log, console, errori, export, telemetria, rete (AC1, AC6).
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (sorgente di `reqwest` 0.12, non disponibile offline per `repo-sync`). Non bloccante.
**Impatto:** [[llm-wiki-sicurezza]] non può dire se la chiave SerpApi possa comparire in messaggi d'errore, sessioni o richieste al provider LLM.

## 2026-11-21 22:10 — llm-wiki-segreti-copie-fuori-store
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-dossier-ep004-r8 (residuo della chiusura di `llm-wiki-token-cifratura`)
**Gap:** copie dei segreti fuori dallo store non escluse: `chrome.storage` dell'estensione (`popup.js`, `background.js`, `clipper-core.js` non letti; la ricerca globale ha coperto `localStorage`, non `chrome.storage`), file di `.llm-wiki/` (anche `ingest-warnings.log`) che finiscono nello zip di esportazione, stampa indiretta delle configurazioni tramite i `derive(Debug)` di sei tipi (nessun punto di stampa visto), segreti incollati dall'utente in chat o sessioni, token incorporato negli esempi copiabili della UI. Fonte del gap: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r8.md §Gap evidenti (punti 4 e 5).
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura dell'estensione e ricerca testuale dedicata in `.llm-wiki/`); l'estensione non è nel perimetro già letto. Non bloccante.
**Impatto:** [[llm-wiki-rischi-persistenza]] dichiara l'esito del rischio 8 senza poter escludere altre copie dei segreti; l'export dello zip non include `app-state.json` per percorsi, ma il contenuto di `.llm-wiki/` non è verificato.

## 2026-11-21 22:10 — llm-wiki-segreti-codice-non-letto
**Origine:** wiki-keeper @ ingest 2026-11-21-repo-llm_wiki-dossier-ep004-r8 (residuo della chiusura di `llm-wiki-token-cifratura`)
**Gap:** non sono letti: pacchetto JS `@tauri-apps/plugin-store` e `Cargo.lock` (dipendenze transitive), sezioni LLM, embedding, MinerU, multimodale e rete delle impostazioni (maschera dei campi e chiamante di `saveProviderConfigs`), ramo `custom` di `getProviderConfig` (dove vada la chiave), `external_search.rs`, `codex_cli.rs` (se eredita l'ambiente con le variabili del proxy), indirizzo e contenuto della richiesta di aggiornamento, validazione di credenziali incorporate negli URL di endpoint LLM, embedding e ricerca, chiamante che compila `ProjectLlmOverride.profile`. Fonte del gap: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r8.md §Gap evidenti (punti 3, 6, 7, 8, 9).
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura dei file indicati). Non bloccante.
**Impatto:** [[llm-wiki-sicurezza]] non può dire se esista un archivio protetto transitivo né come viaggino le chiavi nel ramo `custom`; il «smentito» sull'archivio protetto vale per i manifest diretti.

- [x] llm-wiki-clip-server-uso-bind-cors
**Risolto:** 2026-11-21 — [[llm-wiki-sicurezza]] (§Aggiornamenti, issue chiuse) e [[llm-wiki-api-locale]] (§Aggiornamenti, issue chiuse). Criterio del gap, alla lettera: «Non è noto se il Clip server (porta 19827) applichi gli stessi bind, token e CORS dell'API.» Esito, osservato su upstream v0.6.13 (commit `e08cfce`, branch `develop` coincidente con `main`; letto, mai eseguito): **bind e CORS sì, stesse funzioni dell'API** (`server_bind::configured_bind_host` e `bind_addr`, `clip_server.rs:63-64`, `api_server.rs:135-136`, `server_bind.rs:10-14`; `cors.rs:11-41`, `clip_server.rs:324-325`); **token no, non allo stesso modo**: una richiesta non di loopback senza token valido riceve 401, una richiesta di loopback passa senza token (`clip_server.rs:118-134, 328-336, 349`; confronto a tempo costante e sorgenti del token come nell'API, `api_server.rs:593-618`; senza token configurato `is_token_authorized` dà falso, `:598-600`). Evidenza: le righe sono citate dal raw; la sessione principale ha riferito di averle lette a comando il 2026-11-21 con `sed -n '100,135p;340,352p' src-tauri/src/clip_server.rs`, `grep -n 'fn request_is_loopback' -A8`, `grep -n 'fn local_cors_headers' -A22 src-tauri/src/cors.rs`, `sed -n '8,24p' src-tauri/src/cors.rs` e `grep -n 'fn is_token_authorized' -A25 src-tauri/src/api_server.rs` (comandi riferiti dalla sessione principale e non rieseguiti dal wiki-keeper, che non ha Bash). **Residui, non chiusi e tracciati nel gap separato `llm-wiki-clip-server-input-non-limitato`:** corpo senza limite, `projectPath` non confrontato col registro, consumatore delle clip accodate. Pagina di origine [[2026-11-21-issues-llm_wiki-chiuse]]. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §1. Clip server: indirizzo di ascolto, CORS e token]

- [x] llm-wiki-coppie-id-pagina-non-confrontate
**Risolto:** 2026-11-21 — [[llm-wiki-versioni-e-migrazioni]] (§Aggiornamenti, issue chiuse) e [[llm-wiki-rischi-persistenza]] (§Aggiornamenti, issue chiuse). Criterio del gap, alla lettera: «la coppia `wikiPageIdFromPath` (`embedding.ts:450-462`) e `vector_page_id` (`page_embedding.rs:282-290`) esiste su entrambi i lati ma è fuori dal perimetro di TSK-018 e non è stata confrontata». Esito, osservato su upstream v0.6.13 (letto, mai eseguito): nel caso normale `wiki/<cartella>/<nome>.md` le due funzioni danno lo stesso id, il percorso relativo a `wiki/` senza `.md`; nei casi limite differiscono per costruzione (nome nudo senza `wiki/` accettato da TS e rifiutato da Rust; percorso senza `.md` dà un id in TS e nessun id in Rust; barre finali tolte solo da Rust; `\` convertita da Rust e, in TS, dipendente da `normalizePath`, non letto). **Residui, non chiusi e tracciati nel gap separato `llm-wiki-coppie-id-casi-limite`:** input reali dei chiamanti, `normalizePath` e le altre coppie TS e Rust non lette (la parte «restano ignote anche altre coppie duplicate» del gap è aperta per natura). Chiusura motivata dal confronto che il gap diceva mancare, con righe; l'accettazione dei residui come stato finale è del maintainer. Pagina di origine [[2026-11-21-issues-llm_wiki-chiuse]]. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §5. Id di pagina TS e Rust (gap `llm-wiki-coppie-id-pagina-non-confrontate`)]

## 2026-11-21 23:46 — llm-wiki-clip-server-input-non-limitato
**Origine:** wiki-keeper @ ingest 2026-11-21-issues-llm_wiki-chiuse (residuo della chiusura di `llm-wiki-clip-server-uso-bind-cors`)
**Gap:** non sono determinabili per lettura, per `POST /project`, `/projects` e `/clip` del Clip server: se la libreria del server HTTP (non letta) imponga un limite al corpo prima di `read_to_string` (nelle righe lette `clip_server.rs:163-165, 216-218, 266-268` nessun limite); se il corpo sia letto prima o dopo il controllo del token per le richieste non di loopback; chi consumi le clip accodate (`clip_server.rs:504-508`) e se il consumo avvii un'elaborazione; l'effetto reale della deduzione non testata, mai eseguita, per cui un processo locale potrebbe creare un file Markdown in `<percorso a scelta>/raw/sources/` (`projectPath` non confrontato col registro, `:411-428, 456-492`). Fonte del gap: raw/2026-11-21-issues-llm_wiki-chiuse.md §2. Clip server: fatti nuovi per la sicurezza (nessun gap esistente).
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura del consumatore delle clip accodate e della libreria del server HTTP, non disponibile offline per `repo-sync`); la prova richiede esecuzione, fuori dal metodo di EP-004 (Q_003). Non bloccante.
**Impatto:** [[llm-wiki-sicurezza]] riporta corpo senza limite e `projectPath` non confrontato come fatti osservati, ma l'effetto pratico come deduzione non testata.

## 2026-11-21 23:46 — llm-wiki-monitoraggio-piu-progetti
**Origine:** wiki-keeper @ ingest 2026-11-21-issues-llm_wiki-chiuse
**Gap:** due dichiarazioni opposte nella #648 (issue rimasta chiusa): il maintainer dichiara in v0.6.9 che il monitoraggio delle cartelle elabora tutti i progetti configurati; il segnalatore risponde il 2026-08-25 che con due progetti configurati viene ancora elaborato solo quello aperto. Nessuna delle due è un'osservazione del codice e non è noto quale descriva v0.6.13. Fonte del gap: raw/2026-11-21-issues-llm_wiki-chiuse.md §6. Altre dichiarazioni pertinenti (non chiudono).
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `src-tauri/src/commands/file_sync.rs` e del codice TS di sincronizzazione dei progetti per la selezione dei progetti monitorati). Non bloccante.
**Impatto:** [[llm-wiki-sincronizzazione-file]] non può dire quali progetti siano monitorati in contemporanea.

## 2026-11-21 23:46 — llm-wiki-dipendenze-vulnerabili
**Origine:** wiki-keeper @ ingest 2026-11-21-issues-llm_wiki-chiuse
**Gap:** il punto 6 di #318 (dipendenze vulnerabili, dichiarato dal segnalatore il 2026-06-01) risulta non verificato in v0.6.13: nessun audit delle dipendenze è stato eseguito. Fonte del gap: raw/2026-11-21-issues-llm_wiki-chiuse.md §7. Stato in v0.6.13 dei sei punti di #318.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (esito di un audit delle dipendenze npm e Cargo, che richiede esecuzione e accesso a banche dati di terzi, fuori dal metodo di sola lettura di EP-004, Q_003). Non bloccante. Distinto da `llm-wiki-segreti-codice-non-letto`, che riguarda `Cargo.lock` per un altro scopo (esistenza di un archivio protetto transitivo).
**Impatto:** [[llm-wiki-sicurezza]] riporta il punto come «non verificato» e non può dire se le dipendenze di `llm_wiki` abbiano vulnerabilità note.

## 2026-11-21 23:46 — llm-wiki-coppie-id-casi-limite
**Origine:** wiki-keeper @ ingest 2026-11-21-issues-llm_wiki-chiuse (residuo della chiusura di `llm-wiki-coppie-id-pagina-non-confrontate`)
**Gap:** restano non determinati: come `normalizePath` (TS) tratti `\` prima di `wikiPageIdFromPath`; con quali input reali i chiamanti invochino `wikiPageIdFromPath` e `vector_page_id` (nome nudo senza `wiki/`, percorso senza `.md`, barre finali) e quindi se le differenze osservate nei casi limite si manifestino; quali altre coppie duplicate TS e Rust esistano oltre a quelle lette. Fonte del gap: raw/2026-11-21-issues-llm_wiki-chiuse.md §5. Id di pagina TS e Rust (gap `llm-wiki-coppie-id-pagina-non-confrontate`).
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `normalizePath` e dei chiamanti delle due funzioni, ricerca testuale delle coppie TS e Rust). Non bloccante.
**Impatto:** [[llm-wiki-versioni-e-migrazioni]] e [[llm-wiki-rischi-persistenza]] non possono dire se una divergenza nell'id cambi lo schema `page_id#chunk_index` o la pulizia dell'id legacy nei casi reali.

## 2026-11-22 11:24 — llm-wiki-skill-punti-da-verificare
**Origine:** wiki-keeper @ ingest 2026-11-22-repo-llm_wiki_skill
**Gap:** la wiki non sa confrontare con l'app v0.6.13 alcuni punti che la skill `llm_wiki_skill` dichiara per API v1 e app 0.4.10+: elenco dei campi di ogni risultato di `search`, valori di `mode` e range degli score, campi del risultato di `rescan` e `kind` di `changedTasks`, `Retry-After`, durata del preflight, codice del body generico troppo grande, presenza del campo `truncated` in `files`, estensioni leggibili da `files/content`, default di `sourceWatchConfig`, valori di `nodeType`. L'elenco con il commento è in [[llm-wiki-skill-vs-app-v0-6-13]] §Non confrontabili; le voci interne della skill che ne dipendono sono numerate in [[llm-wiki-skill]] (n. 1, 6, 7, 12, 13, 14, 15). Fonte del gap: raw/2026-11-22-repo-llm_wiki_skill.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura mirata di `api_server.rs`, `search.rs` e `file_sync.rs` di v0.6.13: `api_server.rs` è già letto per intero ma questi punti non risultano nel raw [[2026-11-21-repo-llm_wiki-api-mcp]], controllato con ricerca testuale su `Retry-After`, `truncated`, `413` e `changedTasks`). Non bloccante.
**Impatto:** la PR che aggiornerà la skill alla v0.6.13 non può correggere questi punti con evidenza dalla wiki.

## 2026-11-22 11:24 — llm-wiki-api-storia-versioni
**Origine:** wiki-keeper @ ingest 2026-11-22-repo-llm_wiki_skill
**Gap:** la wiki non sa in quale versione, fra 0.4.10 (la skill) e 0.6.13, sia comparsa ciascuna delle differenze D1…Dn di [[llm-wiki-skill-vs-app-v0-6-13]] (endpoint di scrittura, `chat` operativo, CORS ad elenco, ascolto su LAN, metodi `PATCH` e `DELETE`, `graphHits`, paginazione del grafo). Dati parziali già in wiki, solo dichiarazioni: bind configurabile in v0.5.4 (#474) e CORS `*` segnalato il 2026-06-01 (#318), in [[2026-11-21-issues-llm_wiki-chiuse]]. Fonte del gap: raw/2026-11-22-repo-llm_wiki_skill.md §Versione dichiarata.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (note di release, `src/lib/changelog.ts` o storia dei tag di upstream, non letti).
**Impatto:** [[llm-wiki-skill-vs-app-v0-6-13]] non può dire da quale versione ciascuna riga valga, e la PR non può indicare una versione minima per ogni correzione della skill.

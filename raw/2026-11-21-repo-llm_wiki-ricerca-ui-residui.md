# Specifiche estratte: llm_wiki (ricerca, vettori, UI, residui)

> Documento generato da `repo-sync` v2.12 il 2026-11-21. Sorgente: /home/user/wiki-factory/code_repos/llm_wiki @ commit e08cfce65aad8b76b13546a081c1a8d4422b70c3 (ramo HEAD, detached). Read-only verso la sorgente. Estrazione mirata (fetta E) che completa `raw/2026-11-20-repo-llm_wiki.md`. Citazioni `[^src: percorso:riga]` relative alla radice del repo scansionato.

## Ambito e copertura

File letti (intervalli): `src-tauri/src/commands/search.rs` 1130-2453 (fine file); `vectorstore.rs` 1-1336 e `page_embedding.rs` 1-893 (interi); `src/components/settings/settings-view.tsx` 1-777 e `sections/embedding-section.tsx` 1-488 (interi); `sections/interface-section.tsx` 1-120 (solo lista lingue); `src/i18n/index.ts` (intero); `.github/workflows/build.yml` e `ci.yml` (interi); `src/stores/wiki-store.ts` (intero), `review-store.ts`, `chat-store.ts`, `src/lib/lint-config.ts` (interi); `src/components/lint/lint-view.tsx` 1-340; `src-tauri/src/agent/session.rs` 1-337 (intero). Non letti: `search.rs` 1-1129, i JSON delle lingue, `.github/scripts/*`, `lint-view.tsx` oltre 340, `LlmProviderSection`, `WebSearchSection`, `src/lib/embedding.ts`.

| Gap | Esito |
|---|---|
| i18n-lingue | chiuso |
| ci-test-build | chiuso |
| embedding-cambio-modello | parziale |
| embedding-trasporto | chiuso |
| ui-salvataggio-impostazioni | parziale |
| cancellazione-file-orfani | parziale (vettori chiuso, sessioni agente non chiuso) |
| scan-credenziali | parziale, solo file letti |
| riferimenti-incrociati | parziale |
| chiamanti-non-verificati | parziale |

## Lingue dell'interfaccia (gap i18n-lingue)

L'interfaccia registra quattro lingue: en, it, zh, ru; lingua iniziale e di ripiego `en` [^src: src/i18n/index.ts:3-18]. La sezione Interface le offre come English, Italiano, 中文, Русский [^src: src/components/settings/sections/interface-section.tsx:15-20]. Al salvataggio, se la lingua scelta differisce da quella corrente, si chiama `i18n.changeLanguage` e `saveLanguage` [^src: src/components/settings/settings-view.tsx:558-561]. La README («English + Chinese») è quindi indietro rispetto al codice. La lingua di output delle pagine (`outputLanguage`, default `auto`) è un'impostazione distinta [^src: src/stores/wiki-store.ts:674]. Non verificato: dove la lingua salvata viene riletta all'avvio.

## CI e build (gap ci-test-build)

`ci.yml`: parte su push e PR verso `main`, matrice macos-latest, ubuntu-22.04, windows-latest [^src: .github/workflows/ci.yml:3-14]. I passi sono `npx vite build`, build delle risorse MCP e `cargo build`; non ci sono passi di test [^src: .github/workflows/ci.yml:52-62].

`build.yml` (nome «Build & Release»): parte su tag `v*` o `workflow_dispatch` [^src: .github/workflows/build.yml:3-7]. Matrice: macOS (target aarch64-apple-darwin), ubuntu-22.04, ubuntu-22.04-arm, windows [^src: .github/workflows/build.yml:16-31]. Non esegue test. Passi principali:
- verifica dei checksum PDFium (non su Windows) e sostituzione della libreria ARM64 su Linux ARM [^src: .github/workflows/build.yml:80-90];
- `tauri-apps/tauri-action@v0`: per i tag crea una release in bozza, per i run manuali non crea release [^src: .github/workflows/build.yml:111-134];
- su tag e macOS verifica firma e notarizzazione con `.github/scripts/verify-macos-release.sh` (script non letto) [^src: .github/workflows/build.yml:136-138];
- su Windows crea uno zip portabile e lo allega alla release [^src: .github/workflows/build.yml:140-153];
- sui run manuali carica i bundle come artifact, retention 14 giorni [^src: .github/workflows/build.yml:160-176];
- job `package-extension`: zippa `extension/` con la versione di `package.json` e lo allega alla release [^src: .github/workflows/build.yml:178-210];
- job `publish-release`: toglie lo stato di bozza dopo `build` e `package-extension` [^src: .github/workflows/build.yml:212-221].

Nomi dei secret referenziati (valori non letti): `GITHUB_TOKEN` (integrato), `APPLE_CERTIFICATE`, `APPLE_CERTIFICATE_PASSWORD`, `APPLE_SIGNING_IDENTITY`, `APPLE_ID`, `APPLE_PASSWORD`, `APPLE_TEAM_ID` [^src: .github/workflows/build.yml:96,114-120]. Variabili di build per la robustezza di cargo: `CARGO_HTTP_MULTIPLEXING`, `CARGO_NET_RETRY`, `CARGO_HTTP_TIMEOUT` [^src: .github/workflows/build.yml:34-40]. Non verificato: se i test Rust (`#[cfg(test)]`) o TS girino in qualche altro modo fuori dai workflow.

## Trasporto dell'embedding (gap embedding-trasporto)

- Client HTTP con il proxy applicativo (`crate::proxy::configure_http_client`) e timeout `SEARCH_EMBEDDING_TIMEOUT_SECS` [^src: src-tauri/src/commands/search.rs:1224-1227,1357-1360]. Il valore (8, secondo il gap) è definito fuori dalla finestra letta.
- Chiave API: header `Authorization: Bearer` per endpoint OpenAI-compatibili e Volcengine; header `x-goog-api-key` per Google; con chiave vuota nessun header di autenticazione [^src: src-tauri/src/commands/search.rs:1235-1237,1371-1377]. Un eventuale `?key=` nell'endpoint Google viene rimosso [^src: src-tauri/src/commands/search.rs:1657-1689]. Nelle finestre lette non c'è un controllo che imponga `https`.
- Header extra scartati se vuoti, con nome non sicuro o riservati (`authorization`, `content-type`, `host`, `content-length`, `origin`, `x-goog-api-key`) [^src: src-tauri/src/commands/search.rs:1481-1512]. `Origin: http://localhost` aggiunto solo per endpoint loopback o privati (10/8, 172.16/12, 192.168/16, 127/8) [^src: src-tauri/src/commands/search.rs:1368-1370,1519-1550].
- Corpi: Google con `content.parts` e `output_dimensionality` solo se ≥ 1; Doubao `doubao-embedding-vision` su `/embeddings/multimodal` con input tipizzato; altri `{model, input}` [^src: src-tauri/src/commands/search.rs:1391-1397,1691-1716].
- Batch: da 1 a 64 input, non supportato per Google e Doubao multimodale [^src: src-tauri/src/commands/search.rs:1210-1221,1276-1278]. La risposta viene ordinata per `index`; indici duplicati, dimensioni incoerenti, valori non numerici o non finiti sono rifiutati [^src: src-tauri/src/commands/search.rs:1280-1329].
- Singolo: `fetch_embedding_with_retry` dimezza il testo (su confine di carattere, minimo 64) su errori di dimensione (HTTP 413 o messaggi tipo «too long») fino a `max_retries`, poi errore che invita ad abbassare Max Chunk Chars [^src: src-tauri/src/commands/search.rs:1176-1208,1429-1442]. `page_embedding.rs` passa 3 retry [^src: src-tauri/src/commands/page_embedding.rs:248].
- Gli errori HTTP riportano i primi 200 caratteri del corpo della risposta [^src: src-tauri/src/commands/search.rs:1264,1409].
- Timeout della fase provider per pagina: 300 s; la sostituzione nello storage non è annullabile [^src: src-tauri/src/commands/page_embedding.rs:22,170-185].

Per la sicurezza: la chiave API di embedding viaggia solo verso l'endpoint configurato, nell'header sopra indicato.

## Ciclo di vita dei vettori e cambio modello (gap embedding-cambio-modello)

Verificato:
- La dimensione del vettore è quella del primo chunk; chunk dello stesso batch con dimensione diversa causano errore [^src: src-tauri/src/commands/vectorstore.rs:410-418,495-498].
- Se la tabella v2 esiste, la scrittura è un `merge_insert` su `chunk_id` che elimina le righe della stessa pagina non presenti nel batch; non c'è confronto tra la dimensione nuova e lo schema esistente [^src: src-tauri/src/commands/vectorstore.rs:513-529]. La ricerca non verifica la dimensione della query [^src: src-tauri/src/commands/vectorstore.rs:588-624].
- L'impronta di revisione include contenuto, endpoint, modello, `outputDimensionality`, `extraHeaders`, `maxChunkChars` e `overlapChunkChars`, non la chiave API [^src: src-tauri/src/commands/page_embedding.rs:266-280,780-794]. Se cambia, la pagina viene riembeddata senza `force`; se coincide e i chunk esistono, risponde «unchanged» [^src: src-tauri/src/commands/page_embedding.rs:127-142] [^src: src-tauri/src/commands/vectorstore.rs:549-582].
- Dimensioni vuote o incoerenti dal provider sono rifiutate prima dello storage [^src: src-tauri/src/commands/page_embedding.rs:202-216].
- UI: «Re-index all pages» chiama `embedAllPages` con `clearExisting: true` [^src: src/components/settings/sections/embedding-section.tsx:121-134]; sul lato Rust `vector_clear_chunks` elimina l'intera tabella v2 [^src: src-tauri/src/commands/vectorstore.rs:756-787]. Il salvataggio delle impostazioni embedding non avvia alcun re-index né avvisa del cambio di modello [^src: src/components/settings/settings-view.tsx:397-485]. La sezione mostra solo il conteggio dei chunk [^src: src/components/settings/sections/embedding-section.tsx:86-115].

Non verificato: il comportamento di LanceDB su un `merge_insert` con dimensione diversa (l'errore sarebbe riportato come «Atomic page upsert failed») e su una query di dimensione diversa; se `embedAllPages` (`src/lib/embedding.ts`, non letto) rilevi da solo il cambio di modello. Conclusione: il percorso previsto è il re-index manuale con azzeramento della tabella; un re-index parziale su tabella esistente può fallire o mescolare dimensioni (non verificato).

## Cancellazione di revisioni e sessioni (gap cancellazione-file-orfani)

Vettori: `vector_delete_page` esegue solo `table.delete` sul `page_id` e non cancella il file `.revision` [^src: src-tauri/src/commands/vectorstore.rs:679-715]; `vector_clear_chunks` fa solo `drop_table` [^src: src-tauri/src/commands/vectorstore.rs:756-787]. Il file di revisione è rimosso solo da `invalidate_page_revision`, chiamata quando si scrive senza revisione o se `save_revision` fallisce [^src: src-tauri/src/commands/page_embedding.rs:378-384] [^src: src-tauri/src/commands/vectorstore.rs:537-544]. Il file orfano non produce falsi «unchanged»: la corrispondenza richiede anche almeno una riga per quel `page_id` [^src: src-tauri/src/commands/vectorstore.rs:549-582]. Nome: `.llm-wiki/embedding-revisions/<sha256(page_id) in esadecimale minuscolo>.revision` [^src: src-tauri/src/commands/page_embedding.rs:23,326-331], dove `page_id` è il percorso relativo sotto `wiki/` senza `.md` [^src: src-tauri/src/commands/page_embedding.rs:282-290].

Sessioni agente: in `session.rs` nessuna funzione cancella i file di sessione; l'unico `remove_dir_all` è nei test, su cartelle temporanee. I limiti sono il troncamento a 40 messaggi e la cache in memoria a 128 sessioni; i file restano su disco [^src: src-tauri/src/agent/session.rs:9-12,67-70,138-151]. File in `<progetto>/.llm-wiki/agent-sessions/<id>.json`; `sanitize_session_id` rifiuta vuoti, `/`, `\`, `..` e lunghezze > 128, e sostituisce i caratteri fuori da `[A-Za-z0-9-_.]` con `_` [^src: src-tauri/src/agent/session.rs:177-209]. Non verificato: se altro codice (UI, API, `runtime.rs`, `lib.rs`) li cancelli; non è stata fatta una ricerca testuale.

## Salvataggio delle impostazioni (gap ui-salvataggio-impostazioni)

- La barra «Save» globale è nascosta solo per le sezioni `about` e `llm`; `llm` si dichiara inline («saves per-row on every edit») [^src: src/components/settings/settings-view.tsx:665-668,755-773].
- `handleSave` aggiorna prima tutti gli store zustand, poi scrive in sequenza: llm, embedding, multimodal, lingua di output (per progetto), proxy, source-watch (per progetto), source-watch su tutti i progetti, file sync, `set_proxy_env`, import pianificato (solo con progetto aperto), MinerU, API più `api_server_reload_config`, generale, autostart, `set_close_behavior`, lingua UI (se cambiata), tema (se cambiato), zoom [^src: src/components/settings/settings-view.tsx:469-573].
- `embedding-section.tsx` non salva da sé: modifica solo il draft; la scrittura avviene con il pulsante globale [^src: src/components/settings/sections/embedding-section.tsx:143-154].
- In caso di errore ricarica dal disco le configurazioni negli store e mostra l'errore [^src: src/components/settings/settings-view.tsx:577-628].
- `maxHistoryMessages` è solo messo nello store in `handleSave`; la sua persistenza non è in questo file [^src: src/components/settings/settings-view.tsx:478].

Chiusi: `embeddingConfig`, `multimodalConfig`, `generalConfig`, `llmConfig`. Non verificati: `providerConfigs` e `searchApiConfig` (sezioni `LlmProviderSection` e `WebSearchSection` non lette).

## Tipi di configurazione e campi segreti (gap scan-credenziali, copertura parziale)

Copertura: solo i file elencati in Ambito. In essi non risulta alcun valore di credenziale scritto nel codice; i test Rust usano stringhe segnaposto per le chiavi, non riportate. Nei workflow i secret sono referenziati solo per nome.

Campi che portano segreti, per nome [^src: src/stores/wiki-store.ts:29,100,120,133,163,303,312,322,338-339,353,382]:
- `apiKey` in LlmConfig, SearchApiConfig, EmbeddingConfig, MultimodalConfig, ProviderOverride e SearchProviderOverride;
- `token` e `localToken` di MineruConfig;
- `token` di ApiConfig [^src: src/stores/wiki-store.ts:233-239];
- `customHeaders` (LlmConfig, ProviderOverride) ed `extraHeaders` (EmbeddingConfig), che possono contenere credenziali nei valori.

`ProjectLlmOverride.profile` omette esplicitamente `apiKey` e `customHeaders` [^src: src/stores/wiki-store.ts:371-383]. Il commento dei tipi dice che il backend risolve la chiave da `providerConfigs[presetId]`. L'`ApiConfig.token` può essere sovrascritto dalla variabile d'ambiente `LLM_WIKI_API_TOKEN` [^src: src/stores/wiki-store.ts:229-231]. Nei tipi letti non risulta cifratura (non verificato altrove). Il resto del repository non è stato scansionato.

I valori predefiniti di ApiConfig sono: `enabled: true`, `allowUnauthenticated: false`, `allowLanAccess: false`, `mcpEnabled: false`, `token` vuoto [^src: src/stores/wiki-store.ts:713-719].

## Identificatori e riferimenti (gap riferimenti-incrociati, parziale)

- Id di review: `"review-" + FNV-1a a 32 bit` di `<type>::<titolo normalizzato>`, in esadecimale a 8 cifre; indipendente da `sourcePath`; gli id vecchi `review-N` sono rimappati al caricamento [^src: src/stores/review-store.ts:49-58,95-103,156-164]. `affectedPages` e `sourcePath` sono stringhe senza formato dichiarato [^src: src/stores/review-store.ts:14-15].
- Id di pagina nei vettori: percorso relativo sotto `wiki/` senza `.md`; l'id legacy è lo stem senza directory, rimosso solo se esiste un unico `.md` con quello stem [^src: src-tauri/src/commands/page_embedding.rs:282-290,292-324] [^src: src-tauri/src/commands/search.rs:1768-1778]. La validazione rifiuta quote, backslash, caratteri di controllo e invisibili, lunghezza massima 256 caratteri [^src: src-tauri/src/commands/vectorstore.rs:67,78-114].
- `ignorePages` di `lint-config.json`: lista di stringhe separate da `,`, `，` o a capo, con trim e deduplicazione; la forma attesa del valore non è nel file [^src: src/lib/lint-config.ts:16-25]. Percorso: `<progetto>/.llm-wiki/lint-config.json`, scritto con `writeFileAtomic` [^src: src/lib/lint-config.ts:27-49].
- Review nate dal lint: `affectedPages` riceve `item.page`; la UI usa `<progetto>/wiki/<page>` e prova sia `wiki/<page>` sia `wiki/<page>.md`, quindi la presenza di `.md` non è fissata nelle finestre lette. Le azioni sono stringhe `open:<page>`, `delete:<percorso assoluto>`, `Skip` [^src: src/components/lint/lint-view.tsx:194-197,210-250,277,329].
- Id chat: conversazione `conv_<ms>_<6 caratteri casuali>`, messaggio `msg_<ms>_<contatore>_<6 caratteri casuali>` [^src: src/stores/chat-store.ts:102-109].

Non verificato: forma di `dedup-not-duplicates.json`, `ingest-cache.json`, `ingest-queue.json`, `scheduled-import-db.json`, `projectRegistry`/`recentProjects`, hash dei file di cronologia, origine di `sessionId` e `projectId` degli agenti.

## Chiamanti (gap chiamanti-non-verificati, parziale)

- `vector_optimize_chunks` compatta la tabella v2 e poi fa `Prune` con `older_than` a 0 secondi, senza cancellazione non verificata, per prudenza con più istanze sullo stesso progetto; è dichiarato best effort [^src: src-tauri/src/commands/vectorstore.rs:789-845]. Chi lo invoca (`optimizeChunkVectorTableBestEffort`) non è nei file letti.
- `vector_legacy_row_count` e `vector_drop_legacy` sono usati da `embedding-section.tsx`; il pulsante «Drop legacy» compare se esistono righe v1, e l'avviso di migrazione se ci sono righe v1 e nessun chunk v2 [^src: src/components/settings/sections/embedding-section.tsx:105-108,136-141,170-171,409-418,443-452].
- I comandi v1 `vector_upsert`, `vector_search`, `vector_delete`, `vector_count` restano presenti e testati [^src: src-tauri/src/commands/vectorstore.rs:149-346]. I loro chiamanti applicativi non sono verificati.
- Non verificati: chiamanti di `writeFileAtomic`, `copyFile`, `copyDirectory`, `removeTasks`, `cancelAllTasks`, `cleanupWrittenFiles`, `clearCompletedTasks`; stringhe `embedding.ts:705/731/745`, `auto-save.ts:12/28`.

Nota su cancellazione di pagine orfane: `lint-view.tsx` chiede una conferma distruttiva prima di cancellare [^src: src/components/lint/lint-view.tsx:326-334]. Resta non verificato il confine di percorso lato `delete_file`.

## Gap evidenti

- Comportamento di LanceDB su dimensione dei vettori diversa (scrittura e ricerca); rilevazione del cambio di modello in `src/lib/embedding.ts`.
- Cancellazione dei file `agent-sessions/` fuori da `session.rs`.
- Salvataggio di `providerConfigs` e `searchApiConfig`; punto di rilettura della lingua UI all'avvio; persistenza di `maxHistoryMessages`.
- Esecuzione dei test al di fuori dei workflow; contenuto degli script `.github/scripts/*`.
- Credenziali nel resto del repository; cifratura dei segreti nello store.
- Formati di riferimento degli archivi elencati nella sezione Identificatori.
- Chiamanti elencati nella sezione Chiamanti.

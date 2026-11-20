---
id: llm-wiki-rischi-persistenza
type: concept
title: llm-wiki — divergenze e rischi del layer di persistenza
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: ["raw/2026-11-20-repo-llm_wiki.md", "raw/2026-11-20-repo-llm_wiki-persistenza-a.md", "raw/2026-11-20-repo-llm_wiki-persistenza-b.md", "raw/2026-11-20-repo-llm_wiki-persistenza-c.md"]
tags: [llm-wiki, dati, persistenza, rischi, db]
---

# llm-wiki — divergenze e rischi del layer di persistenza
> Sette divergenze e rischi ricavati dalla lettura del codice: sono deduzioni, non fatti osservati in esecuzione.

## Contesto
Il raw dichiara che le voci seguenti sono **deduzioni dal codice letto**, non fatti osservati in esecuzione, e per ognuna indica file e simbolo. Le etichette «Non verificato» e «Da verificare» sono quelle del raw. Il campione è di 21 file; molto codice che incide sulla persistenza non è letto (gap `llm-wiki-persistenza-codice-non-letto` in [[gaps]]). [^src: raw/2026-11-20-repo-llm_wiki.md §Divergenze e rischi]

## Dettaglio

1. **Possibile ricomparsa di chat cancellate (deduzione).** `deleteConversation` (`src/stores/chat-store.ts`) rimuove la conversazione dallo store, ma `saveChatHistory` (`src/lib/persist.ts`) non elimina i file `chats/<id>.json` orfani, e `loadChatHistory` ricostruisce da quei file quando l'indice è vuoto. Se l'utente cancella tutte le conversazioni, il caricamento successivo potrebbe resuscitarle. **Non verificato**: la rimozione fisica dei file potrebbe stare in codice non letto (ad esempio `chat-panel.tsx`). [^src: raw/2026-11-20-repo-llm_wiki.md §Divergenze e rischi]
2. **Rigenerazione dell'identità del progetto (deduzione).** In `ensureProjectId` (`project-identity.ts`) un `project.json` corrotto produce un nuovo UUID. `restoreQueue` (`ingest-queue.ts`) scarta poi come «cross-project» i task con il vecchio id; le impostazioni per progetto in `app-state.json`, indicizzate per id (`projectLlmOverrides`, `projectOutputLanguages`, `sourceWatchConfig`, `projectFileSyncEnabled`), resterebbero orfane. [^src: raw/2026-11-20-repo-llm_wiki.md §Divergenze e rischi]
3. **Scritture non serializzate sul registro (deduzione).** Solo `saveProjectLlmOverride` e `saveCustomLlmPresets` (`project-store.ts`) hanno una catena di scrittura serializzata; `upsertProjectInfo` (`project-identity.ts`) usa lettura-modifica-scrittura non serializzata e parte da un registro vuoto se `loadRegistry` fallisce, con rischio di sovrascrivere l'intero `projectRegistry` con una sola voce. [^src: raw/2026-11-20-repo-llm_wiki.md §Divergenze e rischi]
4. **Atomicità eterogenea (deduzione).** Atomiche (file temporaneo e rinomina): `lint-config.json` (`writeFileAtomic`), `scheduled-import-db.json`, le revisioni embedding. Non atomiche: sessioni agente e cronologia (scrittura diretta in `session.rs` e `file_history.rs`). Per gli altri file TS dipende dall'implementazione di `writeFile` in `src/commands/fs.ts` e `src-tauri/src/commands/fs.rs`, non letta. [^src: raw/2026-11-20-repo-llm_wiki.md §Divergenze e rischi]
5. **Logica duplicata tra TS e Rust (deduzione).** Il chunking è duplicato tra `page_embedding.rs` e `src/lib/text-chunker.ts` (il commento in `page_embedding.rs` lo dichiara); la pulizia dell'id legacy è duplicata tra `embedding.ts` e `page_embedding.rs`. Inoltre `embedPage` (TS) scrive tramite `vector_upsert_chunks` senza impronta e quindi invalida le impronte salvate dal percorso Rust (`vector_upsert_chunks_inner`, ramo senza revisione). [^src: raw/2026-11-20-repo-llm_wiki.md §Divergenze e rischi]
6. **Re-index senza rollback (deduzione).** In `embedAllPages` (`embedding.ts`), dopo `vector_clear_chunks` un errore di scrittura lascia l'indice incompleto; il messaggio d'errore lo dice esplicitamente e chiede di rilanciare il re-index. [^src: raw/2026-11-20-repo-llm_wiki.md §Divergenze e rischi]
7. **Cambio di modello o di dimensione dell'embedding (da verificare).** La dimensione del vettore è fissata dal primo chunk di una scrittura (`vector_upsert_chunks_inner`). Nel campione non c'è una verifica esplicita di coerenza con la tabella esistente: la gestione di un cambio di modello sembra affidata al re-index (l'impronta di revisione include il modello). Gap: `llm-wiki-embedding-cambio-modello` in [[gaps]]. [^src: raw/2026-11-20-repo-llm_wiki.md §Divergenze e rischi]

Il raw aggiunge un ottavo punto, i segreti in chiaro in `app-state.json`, che rimanda a [[llm-wiki-archivi-persistenza]] (solo nomi di campo letti, nessun valore) e a [[llm-wiki-sicurezza]]. [^src: raw/2026-11-20-repo-llm_wiki.md §Divergenze e rischi]

## Pagine collegate
[[llm-wiki-archivi-persistenza]], [[llm-wiki-gestione-file-corrotti]], [[llm-wiki-operazioni-distruttive]], [[llm-wiki-versioni-e-migrazioni]].

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->
- EP-004 — Verificare i rischi di persistenza prima di correggerli
- US-025 — Rischio 1: chat cancellate che ricompaiono
- US-026 — Rischio 2: rigenerazione dell'identità del progetto
- US-027 — Rischio 3: scritture non serializzate sul registro dei progetti
- US-028 — Rischio 4: atomicità eterogenea delle scritture
- US-029 — Rischio 5: logica duplicata fra frontend e backend
- US-030 — Rischio 6: ricostruzione dell'indice senza rollback
- US-031 — Rischio 7: cambio di modello o di dimensione dell'embedding
- US-032 — Rischio 8: segreti in chiaro nello store applicativo
- US-033 — Sintesi dei rischi e decisione sugli interventi

## Aggiornamenti (v2026-11-20)
Dalle fette A, B e C delle estrazioni mirate sulla persistenza ([[2026-11-20-repo-llm_wiki-persistenza-a]], [[2026-11-20-repo-llm_wiki-persistenza-b]], [[2026-11-20-repo-llm_wiki-persistenza-c]]). **L'esito dei sette rischi sopra non cambia**: restano deduzioni o «da verificare» come nel testo. I rischi li verifica EP-004 con un dossier dedicato; questa sezione raccoglie solo elementi nuovi come indizi, con citazione. Il testo sopra non è modificato. Qualificatori come nel raw («osservato», «deduzione», «non verificato», «solo mappa»). Nessun valore di segreto è stato letto, solo nomi di campo.

### Indizi da verificare in EP-004 (non verificati)

Rischio 1, chat cancellate che ricompaiono
- La rimozione fisica di `chats/<id>.json` esiste, ma solo nel gestore del cestino di `ConversationSidebar` (`chat-panel.tsx:249`), senza attesa e con errore ignorato. Se la cancellazione fallisce in silenzio (per esempio file bloccato su Windows) il file orfano resta e, con indice assente o vuoto al caricamento successivo, la ricostruzione da `chats/*.json` potrebbe riproporlo: deduzione, non provata. La riserva «la rimozione potrebbe stare in codice non letto» è in parte sciolta: il punto è stato trovato. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §File di chat: dove e quando si cancellano]

Rischi 2 e 3, identità del progetto e registro
- `loadRegistry` restituisce un registro vuoto in caso di errore (osservato); le conseguenze sul rischio 3 (`upsertProjectInfo` che parte da registro vuoto) restano la deduzione già riportata. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Store applicativo (`app-state.json`)]

Rischio 4, atomicità eterogenea
- `writeFile` generico (TS `write_file`, Rust `fs::write`) è letto ed è diretto, quindi gli archivi TS che lo usano (`project.json`, `ingest-queue.json`, `ingest-cache.json`, `review.json`, `lint.json`, chat, `chat-preferences.json`, `dedup-not-duplicates.json`, `dedup-queue.json`, checkpoint di ingest, `ingest-warnings.log`, `page-history/`, `image-caption-cache.json`) sono scritti in modo non atomico. Il punto «dipende dall'implementazione di `writeFile`» del testo sopra è ora risolto per `write_file`; l'esito del rischio resta quello del testo. `write_file_inner` non è letta. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Atomicità per archivio]
- Atomici in più (file temporaneo e rinomina): `file-snapshot.json` e `file-change-queue.json` (con finestra non atomica su Windows, dove l'originale è eliminato prima della rinomina) e `raw/parsed/<percorso>.md`. Zero occorrenze di `sync_all` in `fs.rs` (stringa esatta): deduzione dichiarata dal raw che l'atomicità valga per i lettori concorrenti e non sia dimostrata come durabile a un crash. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Scrittura generica (Rust e TS)]
- Divergenza commento e codice (osservata): in `image-caption-pipeline.ts` un commento descrive la scrittura della cache come atomica e dice «before we added atomic writes», ma il codice usa `writeFile` (diretta). [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Atomicità per archivio]
- Il meccanismo di `history-settings.json` resta non verificato e l'elenco completo dei chiamanti di `writeFileAtomic` è limitato a graphify a profondità 1; cancellazioni e altri comandi di `fs.rs` non sono tutti letti. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Copertura del gap `llm-wiki-persistenza-codice-non-letto`]
- `copy_file` e `copy_directory` sovrascrivono la destinazione senza controllo di esistenza e `copy_file` non è atomica; la scrittura di pagina via API (`write_wiki_page_verified`) non è letta, quindi la sua atomicità resta ignota. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Cancellazioni e copie nella scrittura generica (`fs.rs`)]

Rischio 5, logica duplicata
- La logica di sweep delle pagine rimaste senza sorgenti è duplicata in `cleanupDeletedWikiPages` (`source-lifecycle.ts:629-662`), che inoltre non pota le review; il controllo «pagina di sorgente» cerca `/wiki/sources/` mentre `source-lifecycle.ts:620` accetta anche `wiki/sources/` relativo (deduzione). La pulizia dell'id legacy parte anche dopo ogni `vectorUpsertPageChunks`. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Cascata di cancellazione di una pagina]

Rischio 8, segreti in chiaro
- I tipi letti in `wiki-store.ts` confermano campi sensibili (`apiKey`, `customHeaders`, `extraHeaders`, `token`, `localToken`, `url` del proxy, `token` di `apiConfig`) salvati in `app-state.json`; il commento di `proxy-config.ts` dichiara che gli URL con credenziali stanno insieme alle altre chiavi API, senza archivio dei segreti separato. Letti solo nomi e tipi. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Configurazioni dello store: tipi e campi sensibili]
- Il TS passa l'intero `EmbeddingConfig`, `apiKey` compresa, attraverso l'IPC a ogni chiamata `embedding_fetch` (osservato). [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Ricerca ed embedding]

Elementi non assegnati a un rischio (da valutare in US-033, senza numero)
- Flush esplicito su disco solo per `proxyConfig`, `apiConfig`, `generalConfig`, `scheduledImportConfig`, `sourceWatchConfig`, `sourceWatchAllProjects` e `zoomLevel` (osservato); `llmConfig`, `providerConfigs`, `searchApiConfig`, `embeddingConfig`, `multimodalConfig` e `mineruConfig` dipendono dal solo salvataggio automatico con debounce dichiarato di 100 ms. Il raw non ne trae un rischio: è un dato da considerare. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Store applicativo (`app-state.json`)]
- Deduzione, non osservata in esecuzione: se l'apertura dello store rifiuta, l'inizializzazione di `App.tsx` ignora l'errore, non carica le altre configurazioni e non riapre l'ultimo progetto, senza avviso all'utente. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Store applicativo (`app-state.json`)]
- Formato del log (deduzione): il template di `schema.md` dichiara un log in ordine cronologico inverso, mentre tutti gli scrittori letti accodano in fondo con formati di voce diversi; il formato della voce di ingest dipende dal prompt al modello e il codice non lo valida. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Log e indice del progetto wiki]
- Possibile sovrascrittura di `review.json` da parte dell'auto-save: i gestori delle review dell'API (`PATCH`, `DELETE`, bulk) scrivono `review.json` senza emettere eventi verso l'interfaccia nei corpi letti; con l'app aperta lo store in memoria non vede la modifica e un'auto-save successiva potrebbe riscrivere il file con lo stato precedente. Deduzione; `write_raw_review_array` non è letto. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Endpoint dell'API locale che scrivono o cancellano]
- Cancellazione senza confine visibile: `delete_file` non mostra alcun controllo che il percorso sia dentro il progetto nelle righe lette (`run_guarded` non letta) e l'azione `delete:<percorso>` delle review chiama `deleteFile` direttamente, senza cascata (embedding e indice restano) e senza validazione del percorso nella finestra; l'origine delle stringhe di azione non è nota. Effetto complessivo non verificato. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Operazioni distruttive non presenti nella tabella wiki]
- `deleteSourceFiles` elimina qualsiasi pagina wiki la cui unica sorgente è quella cancellata, senza distinguere pagine modificate a mano; il passo di cancellazione della sorgente non è in try e interrompe il batch (il commento di `sources-view.tsx` dice il contrario); `listDirectory` a `wiki-page-delete.ts:242` non è in try e, se fallisce dopo la cancellazione, lo sweep e il prune delle review non partono (deduzione). [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Ciclo di vita delle sorgenti]
- `.cache` accanto a un file sorgente in sottocartella non è cancellata da `deleteSourceFiles` (deduzione, valida per il singolo file); la cartella intera sparisce con `deleteSourceFolder`. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Ciclo di vita delle sorgenti]

Per il contesto dei flussi di cancellazione vedi [[llm-wiki-cancellazione-pagine-e-sorgenti]] e [[llm-wiki-operazioni-distruttive]]; per la sincronizzazione [[llm-wiki-sincronizzazione-file]].

## Contradictions
- **Rischio 4: `writeFile` «non letta».** Prima: «Per gli altri file TS dipende dall'implementazione di `writeFile` in `src/commands/fs.ts` e `src-tauri/src/commands/fs.rs`, non letta». Ora (fetta B): `write_file` Rust e il wrapper TS sono letti e sono diretti; compaiono altri archivi atomici e la divergenza commento/codice sopra. È un aggiornamento del dato, non dell'esito: il rischio resta una deduzione da verificare in EP-004. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Atomicità per archivio]
- **Rischio 1: «potrebbe stare in codice non letto».** Prima: «Non verificato: la rimozione fisica dei file potrebbe stare in codice non letto (ad esempio `chat-panel.tsx`)». Ora (fetta C): la rimozione esiste in `chat-panel.tsx:235-265`, nel solo gestore del cestino (vedi sopra). Esito del rischio invariato; lo verifica EP-004. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §File di chat: dove e quando si cancellano]

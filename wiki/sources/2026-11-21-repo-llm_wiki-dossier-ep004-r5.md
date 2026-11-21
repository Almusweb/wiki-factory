---
id: 2026-11-21-repo-llm_wiki-dossier-ep004-r5
type: source
title: Dossier EP-004 r5 da code_repos/llm_wiki, 2026-11-21: rischio 5, logica duplicata fra frontend (TS) e backend (Rust) (repo-sync)
status: draft
created: 2026-11-21
updated: 2026-11-21
sources: ["raw/2026-11-21-repo-llm_wiki-dossier-ep004-r5.md"]
tags: [source, repo, llm-wiki, persistenza, chunking, embedding, ep-004, rischio-5]
---

# Dossier EP-004 r5 da code_repos/llm_wiki, 2026-11-21: rischio 5, logica duplicata fra frontend (TS) e backend (Rust) (repo-sync)
> Estrazione mirata `repo-sync` v2.12 del 2026-11-21 sul commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` (HEAD staccato, nessun ramo), stato `partial`, 11 file letti, sola lettura (Q_003). «Osservato» = letto nel codice (per costruzione, non eseguito); «deduzione non testata» = ricavata da fatti osservati, mai eseguita. Il repo è di terzi sotto GNU GPL v3: il raw cita solo nomi di file, simboli e righe, nessun frammento di codice.

## Contesto
Quinto dossier della serie di EP-004 (TSK-018 / US-029), dedicato al rischio 5 di [[llm-wiki-rischi-persistenza]]; segue [[2026-11-21-repo-llm_wiki-dossier-ep004-r3]]. Confronta per lettura le due implementazioni del chunking, la pulizia dell'id legacy e il ramo di `embedPage` che scrive senza impronta. Su indicazione del chiamante aggiunge (§4 del raw) le coppie TS/Rust sulla risoluzione di `projectLlmOverrides`, `projectFileSyncEnabled` e `sourceWatchConfig`. Limite dichiarato in anticipo: l'equivalenza su tutti gli input non è dimostrabile per lettura. L'agente non aveva `Bash` né `Grep`: un «non trovato» del raw vale solo per i file letti; la ricerca testuale globale è della sessione principale ed è riportata in TSK-018 §Chiusura, qui in una sezione a parte. Stack e struttura: [[2026-11-20-repo-llm_wiki]]. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r5.md §Identità e perimetro]

## Dettaglio

### Chunking: differenze osservate per costruzione (punto 1)
Simboli: TS `chunkMarkdown` (`text-chunker.ts:97-608`, chiamata da `preparePageEmbeddingRows`, `embedding.ts:382-440`); Rust `chunk_markdown`, `split_preserving_atomic_blocks`, `split_with_overlap`, `push_atomic_chunk` (`page_embedding.rs:510-695`). Entrambi i lati dichiarano la duplicazione con un commento (`text-chunker.ts:4-7`, `page_embedding.rs:507-509`). Nessun test letto confronta i due chunker. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r5.md §1. Chunking: le due implementazioni affiancate (AC2)]

| Aspetto | TS | Rust |
|---|---|---|
| Parametri predefiniti | bersaglio 1000, sovrapposizione 200 | uguali (nessuna differenza) |
| Limiti sul bersaglio | nessuno | limitato a 64..32000 |
| Sovrapposizione fra metà e bersaglio-1 | conservata | ridotta a metà |
| Fusione dei pezzi piccoli | sì (`mergeSmall`, `minChars` 200) | assente |
| Pagina troppo grande | nessun limite visto | rifiuto oltre 2 MiB o 512 chunk |
| Unità di misura | UTF-16 | caratteri Unicode |
| Fine riga CRLF | conservata nel testo del chunk | normalizzata in `\n` |
| Sezione sotto il bersaglio con blocco recintato o tabella | 1 chunk | almeno 2 (ogni blocco atomico è un chunk) |
| Sezione sopra il bersaglio | scala ricorsiva (paragrafi, righe, frasi, spazi) | finestra a caratteri con ricerca di un separatore |
| Fence | solo colonna 0, chiusura uguale all'apertura | anche rientrato, chiusura per carattere e larghezza `>=` |
| Tabella | almeno due righe a colonna 0 | qualsiasi riga che inizia con `|` |
| Intestazione `#` | seguita da qualunque spazio bianco | seguita da uno spazio, titolo non vuoto |
| Titolo senza frontmatter | id di pagina | prima riga `# `, poi id |
| Pagina vuota | `embedPage` ritorna `false` senza errore | errore `InvalidRequest` |

Nessuna differenza trovata su percorso di intestazione («## A > ### B») e testo del chunk con la riga di intestazione. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r5.md §1.1 Parametri, §1.2 Regole di taglio, §1.3 Titoli e frontmatter, §1.4 Pagine vuote]

**Esito del punto 1: confermato per lettura** (le logiche non sono identiche); l'equivalenza su tutti gli input è **smentita per costruzione**, non «non conclusiva», perché le differenze sono nel testo del codice. Impatto se si verifica (deduzione non testata): l'indice di una pagina riflette il chunker di chi ha scritto per ultimo; granularità e testo dei chunk diversi, punteggi di ricerca non comparabili; nessuna perdita (la sostituzione per pagina cancella i chunk non più presenti, `vectorstore.rs:521-529`). Gravità proposta dal dossier: bassa. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r5.md §1.5 Esito del punto 1]

### Pulizia dell'id legacy (punto 2)
Simboli: TS `removeLegacyVectorIdIfSafe` e `projectStemOwnerCounts` (`embedding.ts:224-264`); Rust `remove_legacy_vector_id_if_safe` (`page_embedding.rs:292-324`); entrambi dopo la scrittura dei vettori. Sui casi «nome base unico» (un solo `.md` con quel nome base: si cancella l'id legacy) e «nome base ambiguo» (non si cancella) **nessuna differenza di regola trovata** (nomi ASCII). Differenze marginali: maiuscole (`toLowerCase` Unicode contro `eq_ignore_ascii_case` ASCII); cache dei conteggi TS (`legacyStemOwnerCounts`) mai invalidata nel file letto, Rust ricalcola a ogni scrittura; enumerazione (`listDirectory` non letta contro `WalkDir` senza collegamenti). [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r5.md §2. Pulizia dell'id legacy (AC3)]

**Esito del punto 2: non conclusivo per lettura**, con motivo: l'equivalenza su tutti gli input dipende da `listDirectory` (non letta) e dall'invalidazione della cache altrove (non letta). Impatto se si verifica (deduzione non testata): con conteggio superato TS potrebbe cancellare l'id legacy di una pagina radice creata dopo il primo conteggio, con perdita dei vettori di quella pagina fino al prossimo embed (ripristinabile con re-index). [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r5.md §2.1 Esito del punto 2]

### Ramo senza impronta e invalidazione (punto 3, osservato)
`embedPage` (`embedding.ts:471-500`) non calcola impronte e chiama `vectorUpsertPageChunks` (266-273) → `vectorUpsertChunks` (179-194) → comando `vector_upsert_chunks`, che chiama `vector_upsert_chunks_inner` con `revision: None` (`vectorstore.rs:455-470`). Con righe non vuote il ramo `else` senza revisione (`vectorstore.rs:542-544`) chiama `invalidate_page_revision`, che **cancella** il file `.llm-wiki/embedding-revisions/<sha256 dell'id>.revision` (`page_embedding.rs:326-331, 378-384`); `NotFound` vale `Ok`, altri errori sono ignorati. Alla chiamata successiva di `embed_wiki_page` senza `force` il confronto non trova l'impronta e Rust rifà chunking, embedding e scrittura (`page_embedding.rs:125-142`; `vectorstore.rs:549-582`). Quindi l'invalidazione è una cancellazione del file, non un'impronta sbagliata. Precisazioni: l'impronta non copre né la chiave API né una versione del chunker (un cambio di algoritmo non invalida), usa i parametri grezzi mentre il chunking usa quelli limitati (sovra-invalidazione benigna); `embedAllPages` senza `clearExisting` non consulta alcuna impronta (`embedding.ts:737-754`). [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r5.md §3. Ramo senza impronta e effetto sull'impronta del backend (AC4)]

**Esito del punto 3: confermato per lettura.** Impatto: alternanza fra i due scrittori produce ri-embedding ripetuto di pagine invariate (costo e chiamate al provider) e chunk del chunker dell'ultimo scrittore; nessuna perdita di dati. Deduzione non testata: se l'invalidazione fallisse con errore diverso da `NotFound`, un'impronta superata potrebbe far risultare «unchanged» vettori scritti da TS. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r5.md §3.1 Esito del punto 3]

### Coppie TS/Rust su chiavi per progetto di `app-state.json` (aggiunta del chiamante)
- **`projectLlmOverrides`** (`resolveProjectLlmConfig`, `llm-task-routing.ts:14-31`, contro `project_llm_config`, `api_server.rs:2363-2440`): meccanismi diversi (ricalcolo a ogni uso contro profilo non segreto salvato dal frontend); differenza trovata per costruzione con `presetId` stringa vuota. **Non conclusivo** (motivo: `resolveConfig`, `findLlmPreset` e `ProjectLlmOverride` non letti). Impatto se si verifica: l'API locale e l'agente userebbero modello o endpoint diverso da quello dell'interfaccia.
- **`sourceWatchConfig` e `projectFileSyncEnabled`**: solo i default sono condivisi (stesso `source-watch-defaults.json`, importato da TS e incluso da Rust con `include_str!`, `file_sync.rs:34-35, 139-144`). Differenze su input malformati o legacy (voce con forma non valida: TS normalizza, Rust con `from_value` salta `default`; voce non booleana; `maxFileSizeMb` non intero; campi solo TS). **Confermato** come duplicazione con differenze su input anomali; **non conclusivo** sull'equivalenza per input validi (helper Rust di normalizzazione non letti). Impatto: la riscansione avviata dall'API (`handle_rescan`, `api_server.rs:2896-2913`) potrebbe usare filtri o abilitazione diversi da quelli dell'interfaccia. Nessuna differenza trovata sul caso «nessun dato salvato».
[^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r5.md §4. Coppie TS/Rust sulle chiavi per progetto di `app-state.json` (aggiunta del chiamante)]

### Ricerca testuale globale (sessione principale, estende i negativi del dossier)
Eseguita su `src`, `src-tauri/src`, `mcp-server`, `extension` (esclusi i test), riportata in TSK-018 §Chiusura (il comando è lì; qui se ne citano solo gli esiti):
- **Due sole implementazioni del chunking:** `chunkMarkdown` (`text-chunker.ts:97`, unico chiamante `embedding.ts:391`) e `chunk_markdown` (`page_embedding.rs:510`, chiamata a `:153`; le altre occorrenze sono test).
- **Due percorsi di embedding con chiamanti distinti:** frontend `embedPage` (`embedding.ts:471`), chiamato da `ingest.ts:1572`, `ingest.ts:3613`, `deep-research.ts:696`; Rust `embed_wiki_page` (`page_embedding.rs:66`), chiamato da `api_server.rs:1915` e raggiunto dallo strumento MCP `embedPage` (`mcp-server/src/index.ts:311` → `api-client.ts:347`, vedi [[llm-wiki-mcp-server]]). La stessa pagina può essere indicizzata con l'uno o con l'altro chunking a seconda di chi scrive per ultimo (ingest dall'interfaccia o scrittura via MCP/API).
- **Pulizia id legacy duplicata:** `removeLegacyVectorIdIfSafe` (`embedding.ts:249`, chiamata a `:272`, `:854`) e `remove_legacy_vector_id_if_safe` (`page_embedding.rs:292`, chiamata a `:191`).
- **`projectLlmOverrides` e `sourceWatchConfig`:** lato TS `resolveProjectLlmConfig` in `llm-provider-section.tsx` (85, 97, 114, 195) e `App.tsx:450`; lato Rust `project_llm_config` e `load_source_watch_config` (`api_server.rs:2902, 2915`).
- **Commenti di allineamento:** **[SUPERATO, vedi la nota di correzione sotto]** la ricerca della sessione principale non ha trovato commenti che dichiarino l'allineamento fra le copie; l'unica occorrenza pertinente è `file_sync.rs:142` («source-watch-defaults.json must match SourceWatchConfig»), cioè i default condivisi tramite lo stesso file JSON. **Questo risultato è in tensione con le letture del dossier** (commenti a `text-chunker.ts:4-7`, `page_embedding.rs:507-509`, `llm-task-routing.ts:20-22`, `api_server.rs:2397`): vedi `## Contradictions` di [[llm-wiki-rischi-persistenza]] e il gap `llm-wiki-commenti-allineamento-discrepanza`.

[^src: management/kanban/EP-004-verifica-rischi-di-persistenza/US-029-rischio-logica-duplicata/TSK-018.md §Chiusura]

### File non letti
`frontmatter.ts` (`parseFrontmatter`), `llm-presets` (`findLlmPreset`), `preset-resolver` (`resolveConfig`), `wiki-store.ts`; `listDirectory` (TS) e `list_directory` (Rust); `file_sync.rs` righe 250-380, 710-760 e oltre 1090 (`normalize_ext_list`, `normalize_string_list`, `SourceWatchRules`, `rescan_project_files`); `api_server.rs` oltre le righe indicate (`load_app_state` e sua cache); resto di `text-chunker.test.ts` e `embedding.test.ts` (non escluso che esistano test che fissano come comportamento le differenze qui riportate); `cleanupDeletedWikiPages` (fuori ambito, US-033). I chiamanti di `embedPage` e `embed_wiki_page` non erano letti dal dossier: sono ora noti dalla ricerca globale sopra. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r5.md §File letti e non letti]

### Controllo del repo e dei segreti dichiarato
L'agente non ha eseguito `git status` né `git log`: il controllo a comando è in TSK-018 §Chiusura (`git -C code_repos/llm_wiki log -1 --format=%h` → `e08cfce`, `status --short` → vuoto; `grep -ciE` sui pattern dei segreti sul dossier → 0). Il dossier ha letto solo nomi di chiavi e un valore fittizio di test, non riportato; nessun file `.env*` né `app-state.json` aperto. Nessuna istruzione rivolta a un agente trovata nei file letti. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r5.md §Note di estrazione] [^src: management/kanban/EP-004-verifica-rischi-di-persistenza/US-029-rischio-logica-duplicata/TSK-018.md §Chiusura]

## Aggiornamenti (v2026-11-21, correzione)
**Correzione al punto «Commenti di allineamento» della ricerca globale sopra.** La frase «nessun commento di allineamento, salvo `file_sync.rs:142`» è superata: la ricerca di TSK-018 usava stringhe non coincidenti con i commenti. Ripetuta a comando dalla sessione principale (`grep -rniE` su `aligned`, `in sync`, `mirror(s|ed|ing)?`, `Match `), i quattro commenti letti dal dossier esistono, a coppie: `text-chunker.ts:4-7` ↔ `page_embedding.rs:507-509` e `llm-task-routing.ts:20-22` ↔ `api_server.rs:2397`; duplicazione dichiarata e intenzionale, allineamento manuale. Il dossier aveva ragione; la tensione citata non sussiste più. Emergono anche `dedup-queue.ts:13` ed `extract-source-images.ts:20`. [^src: management/kanban/EP-004-verifica-rischi-di-persistenza/US-029-rischio-logica-duplicata/TSK-018.md §Chiusura (Correzione)] [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r5.md §1. Chunking: le due implementazioni affiancate (AC2)]

## Pagine collegate
[[llm-wiki-rischi-persistenza]] (§Esito della verifica di US-029), [[llm-wiki-versioni-e-migrazioni]], [[llm-wiki-schema-dati]], [[llm-wiki-mcp-server]], [[gaps]].

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

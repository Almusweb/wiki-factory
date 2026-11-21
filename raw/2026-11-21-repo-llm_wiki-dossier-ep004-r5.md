---
source_path: /home/user/wiki-factory/code_repos/llm_wiki
source_type: repo
git_branch: HEAD
git_commit: e08cfce65aad8b76b13546a081c1a8d4422b70c3
extracted_at: 2026-11-21
extractor: repo-sync@2.12.0
scope: dossier EP-004 r5 (TSK-018 / US-029), rischio 5, logica duplicata fra frontend (TS) e backend (Rust)
---

# Specifiche estratte: llm-wiki, dossier EP-004 r5 (rischio 5, logica duplicata TS e Rust)

> Documento generato da `repo-sync` v2.12 il 2026-11-21. Sorgente: `/home/user/wiki-factory/code_repos/llm_wiki`
> @ commit `e08cfce` (HEAD staccato, nessun nome di ramo: il file `HEAD` del submodule contiene solo l'hash, riletto in questa sessione). Read-only verso la sorgente.

## Identità e perimetro

- Estrazione **mirata** (TSK-018 / US-029), per sola lettura del codice (Q_003). Stack, struttura e dipendenze non sono ripetuti (vedi `raw/2026-11-20-repo-llm_wiki.md`). Non ripetuto dalla wiki: il testo del rischio 5 (chunking duplicato, pulizia id legacy duplicata, `embedPage` senza impronta) e la voce non assegnata su `cleanupDeletedWikiPages` (fuori ambito, US-033).
- **Licenza**: repository di terzi, GNU GPL v3. Solo nomi di file, simboli, campi e percorsi; nessun frammento di codice.
- Citazioni `[^src: percorso:righe]`, percorsi relativi alla radice del repo del cliente.
- «Osservato» = letto nel codice. «Deduzione non testata» = ricavato da fatti osservati, mai visto in esecuzione. Nessuna esecuzione, nessun test, nessuna ricerca testuale globale (questo agente non ha `Bash` né `Grep`). Un «non trovato» vale solo per i file e le righe di §File letti e non letti.
- **Limite dichiarato in anticipo** (TSK-018): l'equivalenza dei risultati su **tutti** gli input non è dimostrabile per lettura. Dove le due implementazioni non risultano identiche per costruzione l'esito è «non conclusivo» con motivo; dove una differenza è stata trovata nel testo del codice, è riportata come differenza osservata (per costruzione), senza averla eseguita.
- Perimetro del TSK: chunking (`text-chunker.ts` e `page_embedding.rs`), pulizia dell'id legacy (`embedding.ts` e `page_embedding.rs`), ramo senza impronta (`embedPage`, `vector_upsert_chunks`, `vector_upsert_chunks_inner`). **Aggiunto su indicazione del chiamante** (fatto già noto: `api_server.rs` legge da `app-state.json`, scritto dal frontend, tre chiavi per progetto): la coppia di logiche TS/Rust sulla risoluzione di `projectLlmOverrides`, `projectFileSyncEnabled` e `sourceWatchConfig` (§4).

## Ipotesi di partenza (come in wiki / US-029)

Deduzione: il chunking è duplicato (il commento del codice lo dichiara); la pulizia dell'id legacy è duplicata; il percorso del frontend scrive senza impronta e invaliderebbe le impronte salvate dal backend.

## 1. Chunking: le due implementazioni affiancate (AC2)

Simboli: TS `chunkMarkdown` e funzioni di supporto [^src: src/lib/text-chunker.ts:97-608]; chiamata da `preparePageEmbeddingRows` [^src: src/lib/embedding.ts:382-440]. Rust `chunk_markdown`, `split_preserving_atomic_blocks`, `split_with_overlap`, `push_atomic_chunk` [^src: src-tauri/src/commands/page_embedding.rs:510-695].

**Osservato, la duplicazione è dichiarata da entrambi i lati**: commento in testa a `text-chunker.ts` (righe 4-7) e commento sopra `chunk_markdown` (507-509): «mantenere allineati» titoli, frontmatter, blocchi recintati, tabelle, sovrapposizione, Unicode. Nessun test letto confronta i due chunker (i test Rust a 705-893 e l'inizio di `text-chunker.test.ts`, righe 1-60, esercitano ciascuno il proprio lato; il resto dei test TS non è letto).

### 1.1 Parametri

| Aspetto | TS | Rust | Differenza | Fonte |
|---|---|---|---|---|
| Dimensione di taglio | `targetChars` = `maxChunkChars` della config, predefinito 1000; nessun limite inferiore o superiore | `chunk_chars` = `max_chunk_chars`, predefinito 1000, **limitato a 64..32000** | Rust limita; TS no | embedding.ts:391-394; text-chunker.ts:64-69; page_embedding.rs:15-18, 145-148 |
| Sovrapposizione | `overlapChars` della config, predefinito 200; se `>= target` diventa `floor(target/2)` | predefinito 200; **`min(overlap, chunk/2)`** | per overlap fra metà e target-1: TS conserva il valore, Rust lo riduce a metà | text-chunker.ts:107-110; page_embedding.rs:149-152 |
| Limite massimo | `maxChars` 1500 (alzato a target se minore); non configurabile da `embedPage` | nessun `maxChars`; tetto assoluto 32000 solo per blocchi atomici | struttura diversa | text-chunker.ts:103-106, 279; page_embedding.rs:628-640 |
| Soglia minima, fusione dei piccoli | `minChars` 200: `mergeSmall` fonde i pezzi corti col successivo, se la somma è `<= maxChars` (solo per sezioni oltre il target) | **assente** (MIN_CHUNK_CHARS 64 è solo il minimo del parametro) | Rust non fonde | text-chunker.ts:545-561, 250-268; page_embedding.rs:17 |
| Pagina troppo grande | nessun limite visto | rifiuto se il file supera 2 MiB o produce più di 512 chunk | solo Rust | page_embedding.rs:19-20, 86-94, 160-168 |
| Unità di misura | `length` e `slice` su UTF-16 | caratteri Unicode (`Vec<char>`) | per caratteri fuori dal piano base le lunghezze differiscono; il taglio duro TS può dividere una coppia surrogata (deduzione, non testata) | text-chunker.ts:467-473; page_embedding.rs:661-695 |
| Fine riga CRLF | nessuna normalizzazione: il testo del chunk conserva `\r` | normalizza `\r\n` in `\n` prima di tutto | il testo salvato e inviato al provider differisce per input CRLF | page_embedding.rs:511; text-chunker.ts:168-169 |

I parametri di default coincidono: bersaglio 1000, sovrapposizione 200 (osservato).

### 1.2 Regole di taglio

| Aspetto | TS | Rust | Differenza |
|---|---|---|---|
| Sezione sotto il bersaglio | una sola chunk con tutta la sezione (blocchi recintati e tabelle compresi) [^src: text-chunker.ts:250-260] | **sempre** scomposta ai blocchi atomici: ogni blocco recintato o tabella è un chunk a sé, e il testo prima e dopo un chunk a parte, anche se minuscoli [^src: page_embedding.rs:567-626] | **differenza per costruzione**: una sezione breve con un blocco di codice dà 1 chunk in TS e almeno 2 in Rust |
| Sezione sopra il bersaglio | scala ricorsiva: paragrafi, righe, frasi (`. ` con spazio, `。！？!?；;`), spazi, taglio duro; poi impacchettamento fino al bersaglio e fusione dei piccoli [^src: text-chunker.ts:389-561] | finestra a caratteri: cerca all'indietro, nella seconda metà della finestra, uno spazio o `。！？.!?;；` e taglia dopo; altrimenti taglio duro; nessuna preferenza per i paragrafi [^src: page_embedding.rs:661-695] | punti di taglio diversi sullo stesso testo; in Rust anche un `.` dentro «3.14» è punto di taglio, in TS solo `.` seguito da spazio |
| Sovrapposizione | prefisso preso dalla coda del chunk precedente, riallineato a una frontiera di frase o di spazio; **applicato a tutti i pezzi adiacenti nella sezione, anche ai blocchi indivisibili** [^src: text-chunker.ts:571-608] | ultimi `overlap` caratteri, nessun riallineamento, solo dentro un tratto di testo ordinario; **nessuna sovrapposizione prima o dopo un blocco atomico** [^src: page_embedding.rs:692] | diverse |
| Blocco recintato (` ``` `, `~~~`) | riconosciuto solo a colonna 0; chiusura se la riga, tolti gli spazi, è **uguale** al marcatore di apertura [^src: text-chunker.ts:200-206, 306-326] | riconosciuto anche se rientrato; chiusura se stesso carattere e larghezza `>=`; **una riga con stringa informativa (es. un nuovo ` ```rust `) conta come chiusura** [^src: page_embedding.rs:534-541, 590-603, 642-650] | differenze su fence rientrati, più lunghi, con stringa informativa |
| Tabella | almeno due righe consecutive che iniziano con `|` a colonna 0; una riga sola è paragrafo [^src: text-chunker.ts:330-343] | **qualsiasi** riga che, tolti gli spazi iniziali, inizia con `|` (anche una sola, anche rientrata) è blocco atomico [^src: page_embedding.rs:608-616] | diverse |
| Blocco atomico oltre il limite | resta intero, `oversized: true` [^src: text-chunker.ts:279] | tagliato a 32000 con sovrapposizione 200 [^src: page_embedding.rs:628-640] | diverse |
| Pulizia degli spazi | testo della sezione non rifilato [^src: text-chunker.ts:185-192] | sezione e pezzi rifilati con `trim` [^src: page_embedding.rs:519, 686-688] | spazi e righe vuote ai bordi |

### 1.3 Titoli e frontmatter

| Aspetto | TS | Rust | Differenza |
|---|---|---|---|
| Intestazione di sezione | `#` da 1 a 6 seguiti da **qualunque spazio bianco** (anche tab); può avere titolo vuoto dopo il `trim` [^src: text-chunker.ts:214-221] | `#` da 1 a 6 seguiti da **uno spazio**; titolo non vuoto [^src: page_embedding.rs:652-659] | tab dopo i `#`; riga di soli spazi dopo i `#` |
| Percorso di intestazione («## A > ### B») | stack per livello, i livelli più profondi azzerati [^src: text-chunker.ts:216-231] | stack con `retain` dei livelli minori [^src: page_embedding.rs:550-557] | **nessuna differenza trovata** sulle sequenze lette |
| Testo del chunk | include la riga di intestazione [^src: text-chunker.ts:228-231] | include la riga di intestazione [^src: page_embedding.rs:558-561] | nessuna |
| Frontmatter | apertura `---\n` o `---\r\n`; chiusura: `---` all'inizio di riga seguita da spazi e fine riga [^src: text-chunker.ts:136-149] | apertura `---\n` (dopo normalizzazione CRLF); chiusura: riga che, tolti gli spazi **ai due lati**, vale `---` [^src: page_embedding.rs:485-505] | una chiusura rientrata (` ---`) è chiusura solo in Rust |
| Titolo per l'arricchimento | `extractEmbeddingTitle`: titolo del frontmatter, altrimenti l'id di pagina [^src: embedding.ts:377-380]; in `embedAllPages` è così [^src: embedding.ts:643, 742]; `embedPage` riceve il titolo dal chiamante (non letto) | `extract_title`: titolo del frontmatter, altrimenti **la prima riga `# `** (anche dentro un blocco di codice), altrimenti l'id [^src: page_embedding.rs:459-477] | una pagina con H1 e senza titolo nel frontmatter ha titolo diverso nei due lati (deduzione sul chiamante di `embedPage`, non letto) |
| Testo inviato al provider | titolo, percorso, testo, uniti da riga vuota [^src: embedding.ts:353-362] | uguale, scartando le parti vuote [^src: page_embedding.rs:697-703] | nessuna per chunk non vuoti (testo vuoto non producibile nelle righe lette; non provato) |

### 1.4 Pagine vuote

| TS | Rust | Fonte |
|---|---|---|
| `body.trim()` vuoto → nessun chunk → `preparePageEmbeddingRows` dà «empty» → `embedPage` ritorna `false`, **senza errore** | nessun chunk → errore `InvalidRequest` «Wiki page has no indexable content» | text-chunker.ts:112-113; embedding.ts:395, 482-488; page_embedding.rs:154-159 |

Stesso innesco (nessun contenuto oltre il frontmatter), esiti diversi per chi chiama. Adiacente, non perimetro: pagine aggregate escluse da Rust (`index`, `log`, `overview`) dentro `embed_wiki_page` e da TS (`index`, `log`, `overview`, `purpose`, `schema`) solo in `embedAllPages`, non in `embedPage` [^src: page_embedding.rs:115-124; embedding.ts:610].

### 1.5 Esito del punto 1

**CONFERMATO per lettura**: le due logiche non sono identiche. Differenze trovate per costruzione (ognuna è lettura del codice, non eseguita): sezione breve con blocco atomico; fusione dei piccoli; limite 32000 e 512 chunk; cattura del bordo di sovrapposizione; taglio per paragrafi e frasi contro finestra a caratteri; fence e tabelle riconosciuti diversamente; CRLF; unità UTF-16 contro caratteri. Nessuna differenza trovata sul percorso di intestazione e sui parametri predefiniti.

**Impatto se si verifica (deduzione non testata)**: stesso `page_id`, stessi nomi di colonna, stesso schema `page_id#chunk_index`; l'indice di una pagina riflette il chunker di **chi ha scritto per ultimo** (TS dal flusso di ingest e re-index, Rust dall'API locale). Conseguenze: granularità e testo dei chunk diversi, punteggi di ricerca non comparabili fra pagine scritte da lati diversi. **Nessuna perdita**: la sostituzione per pagina cancella i chunk non più presenti (`merge_insert` con cancellazione dei non corrispondenti, vectorstore.rs:521-529). Gravità proposta: bassa. Quali percorsi usino quale lato nei flussi reali: non determinato (chiamanti di `embedPage` e `embed_wiki_page` non letti).

## 2. Pulizia dell'id legacy (AC3)

Simboli: TS `removeLegacyVectorIdIfSafe` e `projectStemOwnerCounts` [^src: src/lib/embedding.ts:224-264]; Rust `remove_legacy_vector_id_if_safe` [^src: src-tauri/src/commands/page_embedding.rs:292-324]. Entrambi partono **dopo** la scrittura dei vettori [^src: embedding.ts:266-273; page_embedding.rs:188-191].

| Caso | TS | Rust | Differenza |
|---|---|---|---|
| Id senza `/` | esce | esce | nessuna |
| **Nome base unico** (un solo `.md` con quel nome base sotto `wiki/`) | conta i file per nome base minuscolo; se il conteggio è esattamente 1 cancella l'id legacy (il nome base) con `vector_delete_page` | enumera i file `.md` sotto `wiki/`, conta fino a 2; se esattamente 1 cancella l'id legacy | **nessuna differenza di regola trovata** (nomi ASCII, stessa enumerazione) |
| **Nome base ambiguo** (due o più file, o zero) | non cancella | non cancella (`owners != 1`) | **nessuna differenza di regola trovata** |
| Confronto maiuscole/minuscole | `toLowerCase` (Unicode) | `eq_ignore_ascii_case` (solo ASCII) | per nomi non ASCII (es. «É»/«é») i conteggi possono differire |
| Enumerazione | `listDirectory` su `wiki/` (comportamento non letto: nascosti, collegamenti simbolici) | `WalkDir` senza seguire i collegamenti | non determinabile |
| Cache | conteggi memorizzati per progetto in `legacyStemOwnerCounts` e **mai invalidati nel file**; `attemptedLegacyVectorCleanup` evita ritentativi dopo successo | ricalcolo a ogni scrittura | TS può usare un conteggio superato; invalidazioni altrove: non lette |
| Errore di cancellazione | avviso e nuova possibilità di ritentare | `eprintln` | simile |

[^src: embedding.ts:224-264; page_embedding.rs:292-324; embedding.ts:50-56 (cache azzerata solo dai test)]

Nota: nel percorso di ricostruzione completa TS usa `vectorUpsertChunks` senza pulizia, perché la tabella è appena svuotata (embedding.ts:705-712, commento a 710); nel ramo con errori usa `vectorUpsertPageChunks` (embedding.ts:681).

### 2.1 Esito del punto 2

**NON CONCLUSIVO per lettura**, con motivo: la regola è identica sui due casi richiesti per nomi ASCII; due differenze marginali trovate (maiuscole Unicode; cache TS non invalidata nel file); l'equivalenza su tutti gli input dipende dall'enumerazione di `listDirectory` (non letta) e dall'invalidazione della cache altrove (non letta). **Impatto se si verifica (deduzione non testata)**: con conteggio superato, TS potrebbe cancellare l'id legacy di una pagina radice creata dopo il primo conteggio (perdita dei vettori di quella pagina fino al prossimo embed; ripristinabile con re-index). Non provato.

## 3. Ramo senza impronta e effetto sull'impronta del backend (AC4)

Percorso osservato:

1. `embedPage` [^src: embedding.ts:471-500] prepara le righe (nessuna impronta calcolata) e chiama `vectorUpsertPageChunks` (266-273) → `vectorUpsertChunks` (179-194) → comando `vector_upsert_chunks` [^src: vectorstore.rs:455-470].
2. Il comando chiama `vector_upsert_chunks_inner` con `revision: None` (467).
3. Con righe non vuote, dopo `merge_insert`/creazione tabella (513-535), il **ramo `else` senza revisione** (542-544) chiama `invalidate_page_revision`, che **cancella** il file `.llm-wiki/embedding-revisions/<sha256 dell'id>.revision` (`NotFound` vale `Ok`; altri errori sono ignorati con `let _ =`) [^src: page_embedding.rs:326-331, 378-384; vectorstore.rs:542-544]. Con righe vuote la funzione esce prima (491-493) e l'impronta resta.
4. Il lato Rust, `vector_upsert_chunks_with_revision` (472-479), salva l'impronta dopo la scrittura (537-541), con ripiego di invalidazione se il salvataggio fallisce (539).
5. Alla chiamata successiva di `embed_wiki_page` senza `force`, `vector_page_revision_match` confronta l'impronta salvata con quella calcolata (557-559): senza file ritorna `None` e il Rust **rifà chunking, embedding e scrittura** anche se il contenuto non è cambiato [^src: page_embedding.rs:125-142; vectorstore.rs:549-582].

Quindi il ramo del frontend che «scrive senza impronta» è `embedPage` → `vector_upsert_chunks`; il suo effetto sull'impronta del backend è **l'invalidazione per cancellazione del file**, non un'impronta sbagliata. Osservato.

Precisazioni osservate: (a) l'impronta copre contenuto, endpoint, modello, dimensionalità, header extra, `maxChunkChars` e `overlapChunkChars`, **non** la chiave API né una versione del chunker [^src: page_embedding.rs:266-280], quindi un cambio dell'algoritmo di chunking non invalida le impronte; (b) i parametri nell'impronta sono quelli grezzi, mentre il chunking usa i valori limitati a 64..32000 (page_embedding.rs:273 contro 145-148): valori diversi dello stesso intervallo limitato danno impronte diverse e chunk uguali (sovra-invalidazione, benigna); (c) il percorso TS `embedAllPages` senza `clearExisting` non consulta alcuna impronta e ri-embedda ogni pagina (embedding.ts:737-754), pur dicendo il commento «not already indexed» (572-577).

### 3.1 Esito del punto 3

**CONFERMATO per lettura**. **Impatto**: alternanza fra i due scrittori ⇒ ri-embedding ripetuto di pagine invariate (costo e chiamate al provider) e sostituzione dei chunk con il chunker dell'ultimo scrittore; **nessuna perdita di dati**. Non verificato: se l'invalidazione fallisse (errore diverso da `NotFound`, ignorato), l'impronta superata potrebbe far risultare «unchanged» a Rust vettori scritti da TS (deduzione non testata). Chiamanti di `embedPage` (ingest) e di `embed_wiki_page` (API): non letti.

## 4. Coppie TS/Rust sulle chiavi per progetto di `app-state.json` (aggiunta del chiamante)

Fatto noto (r2, TSK-014): `api_server.rs` legge lato Rust `projectLlmOverrides`, `projectFileSyncEnabled` e `sourceWatchConfig`, che il frontend scrive (`project-store.ts`). Qui sono confrontate le **logiche di risoluzione**, non ripetuta la deduzione sull'id.

### 4.1 Contratto e accoppiamento (osservato)

- I valori sono scritti da TS con `store.set` e letti da Rust come `Value` non tipizzato, senza schema condiviso. **Solo i default di `sourceWatchConfig` sono condivisi**: stesso file JSON importato da TS (source-watch-config.ts:4) e incluso da Rust con `include_str!` (file_sync.rs:34-35, 139-144) → per i default la duplicazione è evitata. [^src: src/lib/source-watch-defaults.json:1-73]
- Scrittura TS: `saveProjectLlmOverride` e `saveProjectFileSyncEnabled` usano `set` senza `save()` esplicito (project-store.ts:140, 435, 439); `saveSourceWatchConfig` chiama `store.save()` (462). Una lettura Rust nei primi ≥100 ms può vedere il valore precedente (deduzione non testata, debounce già noto da r3).
- Commenti di allineamento: `resolveProjectLlmConfig` «mantieni allineato a `project_llm_config`» (llm-task-routing.ts:20-22) e il commento Rust «match resolveProjectLlmConfig» (api_server.rs:2397).

### 4.2 `projectLlmOverrides`: `resolveProjectLlmConfig` (TS) contro `project_llm_config` (Rust)

| Aspetto | TS | Rust | Differenza |
|---|---|---|---|
| Meccanismo | ricalcola a ogni uso da preset, `providerConfigs`, override e globale (`resolveConfig`, non letto) [^src: llm-task-routing.ts:14-31] | usa il **profilo** non segreto salvato dal frontend (`projectLlmProfile`, 33-38) e vi fonde otto chiavi del provider, il modello se vuoto e `baseUrl` [^src: api_server.rs:2363-2440] | snapshot salvato contro ricalcolo: i campi del profilo non fusi seguono il momento del salvataggio |
| Disattivato / preset mancante | globale se `!enabled` o `!presetId` o preset non trovato (`findLlmPreset`, non letto) | globale se `enabled` non è `true`; per `presetId` assente → `None` e il chiamante ripiega sul globale [^src: api_server.rs:2451-2458]; `custom-` senza registro → globale; id predefinito non verificato sul registro | per un id predefinito rimosso dal codice TS dà globale, Rust usa il profilo salvato (deduzione, registro dei preset non letto) |
| `presetId` stringa vuota | falsa → globale | `Some("")` → procede col profilo | differenza per costruzione su input estremo |

**Esito: NON CONCLUSIVO** (motivo: `resolveConfig`, `findLlmPreset` e il tipo `ProjectLlmOverride` non letti; i meccanismi sono diversi per progetto). Differenza trovata: caso `presetId` vuoto. **Impatto se si verifica**: l'API locale e l'agente userebbero un modello/endpoint diverso da quello dell'interfaccia per lo stesso progetto.

### 4.3 `sourceWatchConfig` e `projectFileSyncEnabled`

| Aspetto | TS | Rust | Differenza |
|---|---|---|---|
| Campi | normalizza anche `persistExtractedMarkdown`, `parsingConcurrency`, `ingestConcurrency` [^src: source-watch-config.ts:54-85] | la struttura non ha questi campi (serde li ignora) [^src: file_sync.rs:120-137] | campi solo TS; uso lato Rust altrove non letto |
| Voce del progetto con forma non valida | normalizzata sempre (mai errore); voce falsa → passa a `default` | `from_value` tipizzato: errore → **salta `default`** e cade sul valore legacy [^src: api_server.rs:2915-2945] | differenza su dati malformati |
| Estensioni legacy | aggiunge `png/jpg/jpeg` se l'elenco coincide col legacy [^src: source-watch-config.ts:36-38, 68-79] | `normalize_source_watch_config` non ha l'equivalente nelle righe lette; le funzioni `normalize_ext_list` e `normalize_string_list` non sono lette [^src: file_sync.rs:178-186] | possibile differenza su config legacy (non testata) |
| `maxFileSizeMb` | numero con limiti 1..4096 | `u64` limitato a 1..4096; un valore con decimali non deserializza | differenza su input non intero |
| `projectFileSyncEnabled`: voce del progetto non booleana | passa a `default`, poi `true` [^src: project-store.ts:442-452] | `None` (non passa a `default`) → `rescan_project_files(None)` → default dal JSON condiviso (`enabled: true`) [^src: api_server.rs:2930-2944] | differenza solo se la voce del progetto è non booleana e `default` è `false` |
| Nessun dato salvato | default (`enabled: true`) | `None` → default dallo stesso JSON | **nessuna differenza trovata** |

**Esito: CONFERMATO** come duplicazione con differenze su input malformati o legacy (per costruzione); **NON CONCLUSIVO** sull'equivalenza per input validi (helper di normalizzazione Rust non letti). **Impatto se si verifica**: la riscansione avviata dall'API (`handle_rescan`, api_server.rs:2896-2913) userebbe filtri o abilitazione diversi da quelli mostrati nell'interfaccia. Chiamanti Rust diversi da `handle_rescan`: non letti.

## 5. Esito proposto e tabella evidenze

| # | Punto | Esito | Evidenza principale | Livello |
|---|---|---|---|---|
| 1 | Chunking TS e Rust hanno logiche diverse | **CONFERMATO** | sezione breve con blocco atomico (1 chunk contro ≥2): text-chunker.ts:250-260 contro page_embedding.rs:567-626; fusione piccoli solo TS (545-561); limiti 512/32000 solo Rust (20, 160-168, 628-640); tabelle e fence (330-343 contro 608-616, 642-650) | osservato (per costruzione), non eseguito |
| 1b | Equivalenza su tutti gli input | **smentita per costruzione** (differenze trovate), non occorre il «non conclusivo» | come sopra; parametri predefiniti uguali (1000/200) | osservato |
| 2 | Pulizia id legacy: «nome base unico» | **nessuna differenza di regola trovata**; esito complessivo **NON CONCLUSIVO** | embedding.ts:249-264 contro page_embedding.rs:292-324 | osservato; enumerazione `listDirectory` non letta |
| 2b | Pulizia id legacy: «nome base ambiguo» | **nessuna differenza di regola trovata**; stesso esito | stesso | osservato; differenze marginali (Unicode, cache TS) |
| 3 | `embedPage` scrive senza impronta e invalida quella del backend | **CONFERMATO** (invalidazione = cancellazione del file di revisione; effetto: ri-embedding, nessuna perdita) | embedding.ts:471-500; vectorstore.rs:467, 542-544; page_embedding.rs:378-384; vectorstore.rs:557-559 | osservato |
| 4 | Risoluzione override LLM per progetto TS contro Rust | **NON CONCLUSIVO** (differenza su `presetId` vuoto) | llm-task-routing.ts:14-31; api_server.rs:2363-2440 | osservato in parte; `resolveConfig` non letto |
| 5 | Risoluzione `sourceWatchConfig` / `projectFileSyncEnabled` | **CONFERMATO** (differenze su malformati/legacy); equivalenza su validi **NON CONCLUSIVO** | project-store.ts:442-474; api_server.rs:2915-2945; file_sync.rs:120-186 | osservato (per costruzione) |

Per la sintesi (US-033): il rischio 5 è reale come divergenza di comportamento ma senza perdita di dati; impatti su costo, coerenza della granularità e coerenza fra interfaccia e API locale. Gravità proposta: bassa.

## File letti e non letti

**Repo del cliente, letti (11)**:
- `src/lib/text-chunker.ts` (1-609, intero)
- `src/lib/text-chunker.test.ts` (1-60)
- `src/lib/embedding.ts` (1-871, intero)
- `src-tauri/src/commands/page_embedding.rs` (1-894, intero)
- `src-tauri/src/commands/vectorstore.rs` (1-110, 380-709)
- `src-tauri/src/api_server.rs` (2330-2499, 2890-2964)
- `src-tauri/src/commands/file_sync.rs` (1-250, 380-710, 760-1090)
- `src/lib/project-store.ts` (120-189, 405-479)
- `src/lib/llm-task-routing.ts` (1-74, intero)
- `src/lib/source-watch-config.ts` (1-133, intero)
- `src/lib/source-watch-defaults.json` (1-73, intero)

Letti anche, fuori dall'albero di lavoro: `.git/modules/code_repos/llm_wiki/HEAD` della factory (hash `e08cfce65aad8b76b13546a081c1a8d4422b70c3`). Letti come contesto factory: TSK-018, US-029, r3, `wiki/concepts/llm-wiki-rischi-persistenza.md`, manifest.

**Non letti, con motivo**:
- `src/lib/frontmatter.ts` (`parseFrontmatter`), `src/components/settings/llm-presets` (`findLlmPreset`), `preset-resolver` (`resolveConfig`), `src/stores/wiki-store.ts` (tipi): non nel perimetro; fondano i «non conclusivo» di §4.2.
- Chiamanti di `embedPage` (ingest) e di `embed_wiki_page` (API): non nel perimetro del TSK, quindi quale lato scrive in quali flussi non è determinato.
- `src/commands/fs.ts` `listDirectory` e `list_directory` in Rust: non letti; fondano il «non conclusivo» del punto 2.
- `file_sync.rs` righe 250-380, 710-760 e oltre 1090, in particolare `normalize_ext_list`, `normalize_string_list`, `SourceWatchRules`, `rescan_project_files`: non letti.
- `api_server.rs` oltre le righe elencate, in particolare `load_app_state` e la sua cache (letti in r3 a 727-753, non riletti): invalidazione della cache rispetto alle scritture del frontend non riesaminata.
- Resto di `text-chunker.test.ts` e `embedding.test.ts`: non letti; non è escluso che esistano test che fissano comportamenti qui riportati come differenze.
- `source-lifecycle.ts` `cleanupDeletedWikiPages`: fuori ambito (US-033).

## Gap evidenti

1. Quali percorsi reali usano il chunker TS e quali il Rust; frequenza dell'alternanza.
2. Comportamento di `listDirectory` (nascosti, collegamenti) e invalidazione della cache dei conteggi dei nomi base fuori da `embedding.ts`.
3. `resolveConfig` e registro dei preset: equivalenza della risoluzione LLM per progetto.
4. Helper di normalizzazione Rust per le estensioni (conferma o smentita della differenza legacy sulle immagini).
5. Presenza di test che confrontino i due chunker o le due risoluzioni (non esclusa).
6. Quali altre coppie duplicate TS/Rust esistano oltre a quelle lette (es. `wikiPageIdFromPath` in embedding.ts:450-462 e `vector_page_id` in page_embedding.rs:282-290: osservato che esistono entrambe; **non confrontate**, fuori perimetro).

## Stringhe esatte da cercare (ricerca testuale globale, da eseguire dal chiamante)

Cartelle `src/`, `src-tauri/src/`, e se presenti `mcp-server/`, `extension/`; per ciascuna conteggio e file:

1. `chunkMarkdown` e `chunk_markdown` (quanti chiamanti per lato)
2. `text-chunker`
3. `embedPage(`
4. `embed_wiki_page`
5. `vector_upsert_chunks` (compresi `vector_upsert_chunks_with_revision` e `vector_upsert_chunks_inner`)
6. `vectorUpsertChunks` e `vectorUpsertPageChunks`
7. `invalidate_page_revision`, `save_revision`, `load_revision`, `embedding-revisions`
8. `removeLegacyVectorIdIfSafe` e `remove_legacy_vector_id_if_safe`
9. `legacyStemOwnerCounts` e `attemptedLegacyVectorCleanup` (altre invalidazioni della cache)
10. `projectLlmOverrides`, `projectFileSyncEnabled`, `sourceWatchConfig`
11. `project_llm_config`, `load_source_watch_config`, `load_app_state`, `resolveProjectLlmConfig`, `projectLlmProfile`
12. `normalize_ext_list`, `normalize_string_list`, `SourceWatchRules`
13. `maxChunkChars`, `max_chunk_chars`, `overlapChunkChars`, `overlap_chunk_chars`
14. `extractEmbeddingTitle` e `extract_title`
15. `wikiPageIdFromPath` e `vector_page_id`
16. Ammissioni di duplicazione, nelle stesse cartelle: `aligned`, `Keep`, `mirror`, `Match `, `in sync`
17. `"overview"` (liste di pagine aggregate escluse, nei due lati)

## Note di estrazione

- **Stato**: **partial**. Commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` letto dal file `HEAD` del submodule; HEAD staccato, nessun nome di ramo.
- **Controllo repo invariato**: questo agente non ha `Bash`, quindi **non ha eseguito** `git -C code_repos/llm_wiki status --short` né `git log -1`. Nessuna scrittura è stata fatta sotto `code_repos/llm_wiki`. Il controllo a comando richiesto dalla DoD resta da eseguire dal chiamante.
- **Gate**: Fase 1 e Fase 4 assolte dall'approvazione dell'utente in chat per il solo perimetro del TSK-018 (più la coppia §4 indicata dal chiamante); nessuna conferma separata. Dedup: la voce `2026-11-21-repo-llm_wiki-dossier-ep004-r5` non esisteva nel manifest.
- **Controllo segreti**: nessun comando eseguibile; controllo per lettura degli 11 file elencati. Letti solo nomi di chiavi (`apiKey`, `customHeaders` come nomi di campo in `api_server.rs` e `llm-task-routing.ts`) e il valore fittizio `secret` in un test Rust di `page_embedding.rs`, non riportato; non aperti file `.env*` né `app-state.json`. Segreti redatti: 0 (vale per i file letti, non è una scansione dell'intero repo).
- **Istruzioni trovate nei file letti**: nessuna rivolta a un agente; solo commenti per i manutentori, non eseguiti.
- **Nessuna scrittura** in `wiki/` né nel kanban.

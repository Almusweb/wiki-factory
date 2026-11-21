---
source_path: /home/user/wiki-factory/code_repos/llm_wiki
source_type: repo
git_branch: HEAD
git_commit: e08cfce65aad8b76b13546a081c1a8d4422b70c3
extracted_at: 2026-11-21
extractor: repo-sync@2.12.0
scope: dossier EP-004 r6 (TSK-020 / US-030), rischio 6, ricostruzione dell'indice senza rollback
---

# Specifiche estratte: llm-wiki, dossier EP-004 r6 (rischio 6, re-index senza rollback)

> Documento generato da `repo-sync` v2.12 il 2026-11-21. Sorgente: `/home/user/wiki-factory/code_repos/llm_wiki`
> @ commit `e08cfce` (HEAD staccato, nessun nome di ramo: il file `.git/modules/code_repos/llm_wiki/HEAD` della factory contiene solo l'hash, riletto in questa sessione). Read-only verso la sorgente.

## Identità e perimetro

- Estrazione **mirata** (TSK-020 / US-030), per sola lettura del codice (Q_003). Stack e struttura non ripetuti (vedi `raw/2026-11-20-repo-llm_wiki.md`). **Non ripetuto** dal dossier r5: il meccanismo delle revisioni (file `.llm-wiki/embedding-revisions/`, `save_revision`, `invalidate_page_revision`, confronto in `vector_page_revision_match`); qui compare solo l'effetto sul rilancio (§5).
- **Licenza**: repository di terzi, GNU GPL v3. Solo nomi di file, simboli, righe; nessun frammento di codice. Le uniche stringhe riportate alla lettera sono i **messaggi mostrati all'utente** (richiesti dal TSK), citate come stringhe, non come codice.
- Citazioni `[^src: percorso:righe]`, percorsi relativi alla radice del repo del cliente.
- «Osservato» = letto nel codice. «Deduzione non testata» = ricavato da fatti osservati, mai visto in esecuzione. Nessuna esecuzione, nessun errore simulato. Nessuna ricerca testuale globale (questo agente non ha `Bash` né `Grep`): un «non trovato» vale solo per i file e le righe di §File letti e non letti.
- **Limite dichiarato in anticipo** (TSK-020): il comportamento di LanceDB in caso di errore parziale (atomicità di `drop_table`, `create_table`, `merge_insert`; contenuto effettivo della tabella dopo un errore) non è osservabile per lettura: «non conclusivo» con motivo. Il sorgente di `lancedb` non è stato letto.
- **Prerequisito TSK-011 assolto**: `src/lib/embedding.ts` è ora letto **oltre la riga 250** (righe 264-871 in questa sessione, più 1-225), cioè per intero `embedAllPages` (578-762), lo stato del re-index (502-528) e `searchByEmbedding` (785-842). Le righe 226-263 (`removeLegacyVectorIdIfSafe`) non sono rilette qui: fuori perimetro, già in r5.

## Ipotesi di partenza (come in wiki / US-030)

Deduzione dalla wiki (`wiki/concepts/llm-wiki-rischi-persistenza.md`, rischio 6): in `embedAllPages`, dopo `vector_clear_chunks` un errore di scrittura lascia l'indice incompleto; il messaggio d'errore lo dice e chiede di rilanciare il re-index. Dalla US-030: lo svuotamento avviene solo dopo aver calcolato gli embedding, e salvaguardie lo impediscono in vari casi.

## 1. Ordine delle operazioni di `embedAllPages` con `clearExisting: true` (AC2)

Simbolo: `embedAllPages` [^src: src/lib/embedding.ts:578-762]. L'unico chiamante letto è `handleReindex` in `EmbeddingSection`, che passa `clearExisting: true` [^src: src/components/settings/sections/embedding-section.tsx:121-134]. Altri chiamanti: non letti.

| Passo | Cosa fa | Righe | Se fallisce |
|---|---|---|---|
| 0 | esce con 0 se embedding disabilitato o senza modello; azzera l'ultimo errore; stato in memoria `running` | embedding.ts:584-588 | nessun effetto sull'indice |
| 1 | `listDirectory` su `wiki/`; elenco dei `.md`, esclusi `index`, `log`, `overview`, `purpose`, `schema` | 590-616 | con `clearExisting`: errore «Could not read wiki tree; existing index was left unchanged.», stato `error`, **indice intatto** (594-598) |
| 2 | caso zero pagine: se ci sono chunk indicizzati → errore, indice intatto (623-630); se non ce ne sono → `clearChunkVectorTable`, `dropLegacyVectorTableBestEffort`, `done` con 0 | 623-635 | errore prima di ogni svuotamento |
| 3 | **fase di calcolo, senza scritture sul database**: per ogni pagina `readFile`, titolo, `preparePageEmbeddingRowsWithRetry` (3 tentativi, pausa `tentativo × 250` ms); raccoglie `preparedPages` e `failures` | 637-675; 548-570 | nessuna scrittura |
| 4 | se `failures.length > 0`: **non svuota**; scrive con `vectorUpsertPageChunks` solo le pagine riuscite, ognuna in try; poi errore «N of M pages could not be embedded…» | 677-693 | indice **non svuotato**; vedi §3 |
| 5 | se nessuna pagina pronta e ci sono chunk indicizzati → errore, indice intatto | 695-703 | prima dello svuotamento |
| 6 | **svuotamento**: `clearChunkVectorTable` → `vectorClearChunks` → comando Rust `vector_clear_chunks` | 705; 281-285, 309-311 | l'errore **non** è catturato: la promessa rifiuta, `embedAllPages` esce con l'errore del comando, **lo stato resta `running`** (nessun `setEmbeddingReindexState` di errore su questo passo) |
| 7 | **scritture**, in sequenza, una pagina alla volta (`vectorUpsertChunks`, senza pulizia id legacy: commento 710) | 707-723 | al primo errore: `throwEmbeddingReindexError` con il messaggio del §4; le pagine successive **non** sono tentate |
| 8 | solo se `written > 0`: `optimizeChunkVectorTableBestEffort` (errori solo in `console.warn`) | 725-727; 313-321 | non propaga |
| 9 | **eliminazione della versione legacy**: `dropLegacyVectorTableBestEffort` → `vector_drop_legacy` (tabella `wiki_vectors`); errori solo in `console.warn`; fuori dal guard `written > 0` (commento 728-730) | 731; 303-307, 323-331 | non propaga |
| 10 | stato `done` con `count: written`; ritorna `written` | 733-734 | — |

**Osservato**: il calcolo degli embedding (passo 3) precede lo svuotamento (passo 6); da passo 6 a passo 7 non c'è copia, rinomina o tabella di appoggio nel codice letto. `vector_clear_chunks` è `drop_table` della tabella `wiki_chunks_v2` [^src: src-tauri/src/commands/vectorstore.rs:759-787; costanti 62-66]; torna `Ok` se la tabella non esiste (776-778). La scrittura di una pagina crea la tabella se manca (`create_table`, 530-535) o fa `merge_insert` per `chunk_id` con cancellazione dei non corrispondenti **della stessa pagina** (513-529).

**Osservato, sull'ordine di scrittura**: `preparedPages` si riempie nell'ordine di **completamento** dei worker (`push` a 659 dentro `parallelForEach`, 530-546), non nell'ordine dell'albero. **Deduzione non testata**: con `concurrency > 1` l'insieme di pagine scritte prima di un errore cambia da un tentativo all'altro.

## 2. Dove un errore interrompe il flusso (AC2, AC3)

Tre famiglie, distinte per **momento** rispetto allo svuotamento:

| Famiglia | Punti | Stato dell'indice | Fonte |
|---|---|---|---|
| A. Prima dello svuotamento (albero illeggibile, zero pagine con chunk presenti, solo pagine vuote con chunk presenti, almeno una pagina non calcolata) | 594-598, 623-630, 677-693, 695-703 | tabella v2 invariata (salvo i casi di §3) | embedding.ts |
| B. **Lo svuotamento stesso** fallisce (passo 6) | 705 | **non determinabile per lettura**: dipende dal comportamento di `drop_table` | vectorstore.rs:780-782 (errore «Drop chunk table error: …»); LanceDB non letto |
| C. **Dopo lo svuotamento**: una scrittura fallisce (passo 7) | 708-718 | **tabella assente o parziale** (vedi sotto) | embedding.ts:707-723 |

**Cause di fallimento di scrittura osservate nel codice del comando** (passo 7), tutte **dopo** lo svuotamento:
- `page_id` rifiutato: caratteri di controllo, apice singolo, doppio apice, barra rovesciata e caratteri invisibili o di formato (soft hyphen, zero-width, bidi, tag, ecc.), oltre 256 caratteri o vuoto [^src: vectorstore.rs:67, 78-114, 378-380, 487]. **Osservato**: il lato TS **non** valida l'id né prima né durante il calcolo (`preparePageEmbeddingRows`, embedding.ts:382-440; `wikiPageIdFromPath` può restituire stringa vuota a 458-459). Quindi una pagina con, ad esempio, un apice nel nome di file supera il calcolo e fallisce solo in scrittura, **dopo** lo svuotamento (deduzione non testata sull'esistenza di tali nomi nei progetti reali).
- dimensione dei vettori incoerente fra chunk della stessa pagina: errore «Chunk #… has embedding dim … but batch dim is …» [^src: vectorstore.rs:410-418, 506]. Il TS non controlla la coerenza di dimensione (embedding.ts:421-423).
- errori di connessione, apertura, creazione tabella, `merge_insert` [^src: vectorstore.rs:500-535]; disco pieno, permessi: **non osservabili per lettura**.

**Caso a pagina senza righe**: `vector_upsert_chunks_inner` ritorna `Ok` con `chunks` vuoto (vectorstore.rs:491-493); in rebuild le pagine senza righe non entrano in `preparedPages` (652-663), quindi non sono scritte.

## 3. Che cosa resta nell'indice dopo un errore (AC3)

### 3.1 Errore dopo lo svuotamento (famiglia C) — osservato

- La tabella v2 è stata eliminata (705) e **ricreata dalla prima scrittura riuscita** (vectorstore.rs:530-535). Se fallisce **la prima** scrittura (`written == 0`), la tabella v2 **non esiste** (osservato: nessun passo successivo la ricrea; ottimizzazione e drop legacy saltati perché il `throw` esce a 714).
- Se fallisce la k-esima, restano le **pagine già scritte** (ognuna scritta in una singola chiamata `merge_insert`/`create_table`, dichiarata atomica per pagina nel commento a vectorstore.rs:455-459 e nel messaggio d'errore 529) e **mancano tutte le altre**, comprese quelle non ancora tentate (la ricerca si ferma al primo errore, 712-718). Il messaggio stesso lo dichiara: «may be incomplete».
- **Non** vengono eseguiti: ottimizzazione (725-727) e `vector_drop_legacy` (731). La tabella legacy `wiki_vectors`, se presente, **resta**.
- **Contenuto effettivo della tabella dopo l'errore su una pagina a metà scrittura**: **NON CONCLUSIVO** (motivo: l'atomicità di `merge_insert`/`create_table` in LanceDB non è stata letta; il commento del codice la dichiara, ma è una dichiarazione, non una verifica).

### 3.2 Errore prima dello svuotamento ma con pagine fallite (passo 4) — osservato

Non svuota. Scrive le pagine riuscite **sulla tabella esistente** (`merge_insert`, o `create_table` se assente), poi lancia l'errore 690-692 («failed pages kept their previous vectors»). Conseguenze **osservate**: le righe di pagine **eliminate** dal wiki **non** sono rimosse (la rimozione avviene solo con lo svuotamento); la dimensione dei vettori nuovi non è confrontata con quella dell'indice esistente (vectorstore.rs:513-529): con un cambio di modello l'effetto è un `merge_insert` su schema esistente, **non conclusivo** (comportamento di LanceDB non letto; rimanda a US-031).

### 3.3 Revisioni incoerenti? (senza ripetere r5)

- **Osservato**: `vector_clear_chunks` fa solo `drop_table` (vectorstore.rs:760-787): **non tocca** i file di revisione.
- **Osservato**: `vectorUpsertChunks` chiama `vector_upsert_chunks`, ramo senza revisione, che invalida la revisione della pagina scritta (vectorstore.rs:467, 542-544; meccanismo già in r5 §3). Quindi dopo un rebuild, anche riuscito: pagine scritte → **senza** revisione; pagine non scritte (dopo l'errore) → revisione **vecchia ancora presente**, ma senza righe in tabella.
- **Osservato**: `vector_page_revision_match` ritorna `None` se manca la tabella (570-572) o se le righe della pagina sono zero (581); altrimenti confronta la revisione (557-559). Quindi la revisione vecchia di una pagina **senza righe** non produce «unchanged» (letto nel codice, righe 557-581).
- **Deduzione non testata**: lo stato è «incoerente ma autoprotetto»: revisioni senza righe sono inerti perché il controllo richiede righe presenti; il costo è il ri-embedding delle pagine senza revisione alla prossima scrittura via Rust (costo, non perdita). L'unico dubbio residuo, **non conclusivo**: un'invalidazione fallita (errore ignorato con `let _ =`, vectorstore.rs:543) combinata con righe presenti.
- `embedAllPages` lato TS **non consulta mai le revisioni** (nessuna lettura nelle righe 578-762): il rilancio non ne sfrutta alcuna.

## 4. Messaggio all'utente e segnalazione nell'interfaccia (AC3, AC5)

**Testo del messaggio** (famiglia C) [^src: src/lib/embedding.ts:714-717]: «Rebuild write failed after clearing existing chunks (`<pageId>`: `<motivo>`). The rebuilt index may be incomplete; run re-index again after fixing the error.» Dice «may be incomplete» (non «è incompleto») e **non** riporta quante pagine sono state scritte né quante mancano (il contatore `written` non entra nel messaggio).

Altri messaggi (famiglia A): 595 «Could not read wiki tree; existing index was left unchanged.»; 628 e 700 «… Existing index was left unchanged.»; 690 «N of M pages could not be embedded (…). K successful page(s) were updated; failed pages kept their previous vectors and can be retried.»

**Come l'interfaccia lo mostra** (osservato):
- Lo stato è una variabile **in memoria** del modulo (`embeddingReindexState`, embedding.ts:508), non persistita; `throwEmbeddingReindexError` lo porta a `error` e rilancia (525-528).
- `EmbeddingSection` legge lo stato con `useSyncExternalStore`, lo mostra **solo se** `projectPath` coincide col progetto aperto (embedding-section.tsx:89-97) e, per `error`, stampa in rosso la stringa «Re-index failed: {{message}}» (461-465; testo in `src/i18n/en.json:667`). Solo la sezione Settings → Embedding lo mostra, nei file letti.
- `handleReindex` **cattura e scarta** l'errore (121-134): l'unica altra azione è `refreshStats`; nessun toast, nessun dialogo nei file letti.
- Durante la fase di scrittura (passo 7) il pulsante mostra «Indexing {{done}}/{{total}}…» (en.json:665) con i contatori dell'ultimo aggiornamento della fase di calcolo (`done == total`, 668-674); **nessun aggiornamento di avanzamento** nelle scritture 707-723 (osservato). Un errore al passo 6 lascia lo stato `running` (§1, passo 6): il pulsante resta disabilitato (433) finché non cambia lo stato (deduzione non testata sulla possibilità di sblocco senza riavvio).
- Il conteggio «{{count}} chunks indexed» è riletto da `getEmbeddingCount` (embedding.ts:864-870; section 102-115, 425), che ritorna **0 sia per tabella vuota/assente sia per errore** (866-869): nessuna distinzione, nessun confronto con le pagine attese.
- La sezione mostra l'avviso «Legacy per-page index detected» quando `legacyCount > 0` e `chunkCount` è 0 o `null` (170-171; en.json:668-669): dopo un errore famiglia C con prima scrittura fallita e tabella legacy ancora presente, l'avviso **compare** e invita a rilanciare «Re-index all pages». Nei file letti è l'unico indizio che non dipende dallo stato in memoria. Con la tabella legacy assente o con indice parziale non vuoto, non compare nulla di analogo.
- **Deduzione non testata**: dopo il riavvio dell'app o la chiusura del processo durante la scrittura, lo stato `error` non esiste più (variabile di modulo) e l'utente vede solo il numero di chunk, senza traccia di un re-index interrotto.

## 5. Il rilancio riparte da zero? Che cosa impedirebbe il recupero completo? (AC4)

**Osservato — riparte da zero**: il rilancio con `clearExisting` rifà l'intero passo 3 (lettura, chunking, chiamate al provider per **tutte** le pagine, 637-675), senza consultare né righe esistenti né revisioni; poi rifà `drop_table` (705) e riscrive tutto in sequenza (707-723). Non c'è checkpoint, indice di avanzamento né elenco delle pagine mancanti. Costo: tutte le chiamate al provider si ripetono (deduzione sul costo, non misurato).

**Che cosa non impedisce il recupero** (osservato): le salvaguardie 695-703 guardano `preparedPages.length === 0`, non lo stato parziale; una tabella parziale **non blocca** il rilancio, che la elimina e riparte.

**Che cosa impedirebbe il recupero completo** (cause che, se deterministiche, si ripresentano a ogni rilancio):
1. **Pagina con `page_id` rifiutato** da `validate_page_id_common` (vectorstore.rs:78-114): fallisce a ogni rilancio dopo lo svuotamento, e i `page` che seguono nell'ordine di completamento non vengono scritti. Il recupero completo richiede di rinominare il file. **Osservato** il meccanismo; **deduzione non testata** sul fatto che un progetto reale abbia tali nomi.
2. Vettori con dimensione incoerente nella stessa pagina (vectorstore.rs:410-418): stesso effetto.
3. Errori del database o del disco (disco pieno, permessi, file bloccato su Windows): **non conclusivo** (motivo: non osservabili per lettura).
4. Chiusura o crash dell'app **dopo** lo svuotamento: nessun rollback né ripresa; `finally` assente nel flusso 705-731. Il flusso è un `async` senza `try/catch` attorno a 705-731 salvo il `try` locale a 709-718: un `throw` da `vectorClearChunks` o l'uscita del processo non lascia nessuna compensazione (osservato); lo stato effettivo su disco dopo un'uscita brusca è **non conclusivo** (LanceDB non letto).
5. Concorrenza: nessun lock copre la sequenza 705-723. Ogni comando prende e rilascia da sé il lock di scrittura `vectorstore_v2_lock` (vectorstore.rs:52-60, 489, 763); fra uno svuotamento e le scritture, e fra una scrittura e l'altra, altri chiamanti possono scrivere. **Deduzione non testata**: un `embedPage` di ingest eseguito durante la ricostruzione potrebbe essere sovrascritto da righe preparate prima (contenuto più vecchio) quando la ricostruzione arriva a quella pagina. Altri chiamanti di `embedPage` e di `embedAllPages` e la prevenzione di una seconda esecuzione fuori dalla UI: non letti. Nella UI il pulsante è disabilitato durante `running` (embedding-section.tsx:433).

**Backup, rollback, ripresa nel codice letto**: **non trovati** in embedding.ts (intero `embedAllPages`), vectorstore.rs (comandi v2 e `vector_drop_legacy`) ed embedding-section.tsx. L'unica salvaguardia è la **sequenza** (calcolo prima di svuotare) e le uscite anticipate §1. La tabella legacy `wiki_vectors` sopravvive a un rebuild fallito (731 non raggiunto), ma **non è né letta dalla ricerca** (§6) **né usata per ripristinare**: nei file letti non esiste un percorso che ricostruisca v2 da v1. Non è un backup.

## 6. Ricerca con tabella assente o vuota (AC5)

Percorso reale della ricerca nell'interfaccia: `searchWiki` → comando `search_project` [^src: src/lib/search.ts:62-83], che calcola l'embedding della query e chiama `search_project_inner` [^src: src-tauri/src/commands/search.rs:107-129, 294-315, 327-495].

| Condizione | Comportamento (osservato) | Fonte |
|---|---|---|
| Tabella v2 assente | `vector_search_chunks` ritorna `Ok(vec![])` | vectorstore.rs:608-610 |
| Tabella v2 vuota | la ricerca vettoriale non produce righe; `search_by_embedding` ritorna `Ok(vec![])` se non ci sono chunk | search.rs:807-815 |
| Nessun risultato vettoriale | `vector_hits == 0` → niente fusione RRF; `mode` = `keyword` (o `hybrid` solo per grafo) | search.rs:464-472, 782-792 |
| Errore della ricerca vettoriale | `eprintln` «vector search failed; falling back to keyword results» e prosegue con i risultati per parole chiave | search.rs:455-459 |
| Errore nell'embedding della query | `eprintln` e `Ok(None)`: ricerca per parole chiave | search.rs:308-314 |
| Tabella **parziale** | compaiono solo le pagine già scritte; fuse in RRF con i risultati per parole chiave; nessun segnale | search.rs:437-472 |
| Lato TS `searchByEmbedding` (percorso diverso, API compatibile) | ritorna `[]` per vettore query nullo, per errore (log in console) e per nessun chunk | embedding.ts:791-804 |

**Osservato**: nessuna delle due ricerche legge la tabella legacy v1 (la funzione usa solo `vector_search_chunks`, search.rs:807; TS embedding.ts:799). Dopo un re-index fallito la ricerca **degrada in silenzio** a parole chiave o a indice parziale; il campo `mode`/`vector_hits` nella risposta Rust esiste (search.rs:54-60) ma il TS lo commenta come «riservato per badge o debug» e **non lo usa** (search.ts:20-28, 79-82). `search-view.tsx` non è letto: se mostri un indicatore di modalità, **non conclusivo**.

Durante il rebuild la lettura attende il lock di scrittura di ogni comando singolo (vectorstore.rs:594-595, 763), ma fra un comando e l'altro può passare: la ricerca può quindi vedere l'indice vuoto o parziale **mentre la ricostruzione è ancora in corso e riuscirà** (deduzione non testata).

## 7. Esito proposto e tabella evidenze

**Esito proposto: CONFERMATO per lettura** per il meccanismo e l'ipotesi della wiki (dopo lo svuotamento un errore di scrittura lascia tabella assente o parziale, nessun rollback, rilancio da zero, messaggio «may be incomplete»); **NON CONCLUSIVO** per il contenuto effettivo della tabella dopo un errore parziale e per lo stato dopo un'uscita brusca (motivo: comportamento di LanceDB non letto, nessuna esecuzione).

**Precisazioni rispetto alla wiki**: (a) le salvaguardie sono **più ampie** del solo elenco: coprono anche il caso di pagine fallite, ma in quel caso scrivono comunque le pagine riuscite sull'indice esistente (§3.2); (b) **una** causa di errore post-svuotamento è prevedibile e non controllata prima: la validità del `page_id`; (c) l'interfaccia segnala l'errore **solo** nella sezione Settings → Embedding, con stato in memoria, senza indicare quante pagine mancano.

**Impatto sull'utente (deduzione non testata)**: dopo un errore di scrittura il progetto resta con ricerca semantica assente o parziale, con ricerca che ripiega in silenzio sulle parole chiave; non c'è perdita di pagine wiki né di sorgenti (la tabella è un indice derivato dal testo delle pagine: ricostruibile rilanciando il re-index). Costo del rilancio: tutte le chiamate al provider. Gravità proposta: **media** se l'errore è deterministico (id non valido), **bassa** se transitorio. Decisione sulla salvaguardia: a US-033.

| # | Punto | Esito | Evidenza principale | Livello |
|---|---|---|---|---|
| 1 | Calcolo prima dello svuotamento | **CONFERMATO** | embedding.ts:637-675 prima di 705 | osservato |
| 2 | Salvaguardie pre-svuotamento (albero, zero pagine, solo vuote, pagine fallite) | **CONFERMATO**, con nota: pagine fallite → upsert sulle riuscite, nessun svuotamento | embedding.ts:594-598, 623-630, 677-693, 695-703 | osservato |
| 3 | Ordine: calcolo, `vector_clear_chunks`, scritture in sequenza, ottimizzazione, drop legacy | **CONFERMATO** | embedding.ts:705-734; vectorstore.rs:759-787, 889-915 | osservato |
| 4 | Errore di scrittura dopo lo svuotamento ferma il flusso; pagine successive non tentate | **CONFERMATO** | embedding.ts:708-718 | osservato |
| 5 | Stato dopo l'errore: tabella assente se fallisce la prima, parziale altrimenti; legacy non eliminata | **CONFERMATO** (stato logico) | embedding.ts:714, 725-731; vectorstore.rs:530-535 | osservato |
| 6 | Contenuto effettivo della tabella dopo errore a metà pagina o uscita brusca | **NON CONCLUSIVO** | atomicità di LanceDB non letta | motivo dichiarato |
| 7 | Testo del messaggio: «may be incomplete… run re-index again» | **CONFERMATO** | embedding.ts:714-717 | osservato |
| 8 | Rollback, backup, ripresa | **non trovati** nei file letti | embedding.ts, vectorstore.rs, embedding-section.tsx | osservato (limitato ai file letti) |
| 9 | Rilancio riparte da zero | **CONFERMATO** | embedding.ts:637-675, 705; nessuna lettura di revisioni | osservato |
| 10 | `page_id` non valido: fallimento solo dopo lo svuotamento, ripetibile | meccanismo **CONFERMATO**; esistenza di nomi reali: **deduzione non testata** | vectorstore.rs:78-114, 378-380, 487; embedding.ts:382-440 | osservato / deduzione |
| 11 | Revisioni incoerenti dopo rebuild parziale, ma inerti | **deduzione non testata** (controllo con righe presenti, osservato) | vectorstore.rs:557-581, 543, 760-787 | osservato in parte |
| 12 | Interfaccia: errore in rosso solo in Settings, stato in memoria; nessun avanzamento in scrittura | **CONFERMATO** | embedding-section.tsx:89-97, 121-134, 461-465; embedding.ts:508, 668-674 | osservato |
| 13 | Ricerca con tabella assente/vuota: ripiego silenzioso su parole chiave | **CONFERMATO** | vectorstore.rs:608-610; search.rs:437-472, 455-459 | osservato |
| 14 | Ricerca con tabella parziale: nessun segnale | **CONFERMATO** (assenza di segnale nei file letti) | search.rs:437-472; search.ts:79-82 | osservato; `search-view.tsx` non letto |
| 15 | Concorrenza con altre scritture durante il rebuild | **deduzione non testata** | vectorstore.rs:52-60, 489, 763; chiamanti non letti | non conclusivo |

## File letti e non letti

**Repo del cliente, letti (6 file, sola lettura)**:
- `src/lib/embedding.ts` (1-225, 264-871; **non** riletto 226-263)
- `src-tauri/src/commands/vectorstore.rs` (1-155, 205-948; **non** letto 155-205, v1 `vector_upsert`, e i test oltre 948)
- `src-tauri/src/commands/search.rs` (1-560, 640-900; **non** letto 560-640 e oltre 900)
- `src/components/settings/sections/embedding-section.tsx` (1-489, intero)
- `src/lib/search.ts` (1-84, intero)
- `src/i18n/en.json` (1-30, 560-760; solo per il testo dei messaggi dell'interfaccia)

Letti anche, fuori dall'albero di lavoro: `.git/modules/code_repos/llm_wiki/HEAD` della factory (hash `e08cfce65aad8b76b13546a081c1a8d4422b70c3`). Letti come contesto factory: TSK-020, US-030, dossier r5, `wiki/concepts/llm-wiki-rischi-persistenza.md` (righe 1-208), manifest.

**Non letti, con motivo**:
- Sorgente della libreria `lancedb` (e `drop_table`, `create_table`, `merge_insert`): comportamento su errore parziale **non conclusivo**; fuori dal repo del cliente.
- Altri chiamanti di `embedAllPages` (es. abilitazione iniziale in `App.tsx`), di `embedPage` e di `embed_wiki_page`; presenza di una seconda via di re-index lato Rust (`api_server.rs`, `page_embedding.rs` non riletto in questa sessione): non nel perimetro, quindi esclusi per lettura solo nei file letti.
- `src/components/search/search-view.tsx`: se la UI di ricerca segnali la modalità o l'assenza di indice: non letto.
- `src/lib/embedding.test.ts`: non è escluso che esistano test che fissano il messaggio o l'ordine delle operazioni.
- `en.json` oltre le righe elencate, `it.json`, `ru.json`, `zh.json`.
- `validate_page_id_for_v2` è letta (378-380); non è stata cercata una validazione dell'id nel flusso che precede `embedAllPages` fuori da embedding.ts.

## Gap evidenti

1. Atomicità e stato su disco di LanceDB dopo `drop_table`, `create_table` o `merge_insert` interrotti (non conclusivo).
2. Altri chiamanti di `embedAllPages` e se qualcuno la lanci senza il blocco del pulsante; esistenza di una via Rust di re-index.
3. Se `search-view.tsx` o altri componenti mostrino la modalità di ricerca o l'assenza di indice.
4. Se esistano test che coprano il fallimento dopo lo svuotamento.
5. Frequenza reale dei nomi di pagina con caratteri rifiutati da `validate_page_id_common`.
6. Comportamento del processo se l'app viene chiusa fra 705 e 731.

## Stringhe esatte da cercare (ricerca testuale globale, da eseguire dal chiamante)

Cartelle `src/`, `src-tauri/src/` e, se presenti, `mcp-server/`, `extension/`; per ciascuna: conteggio e file.

1. `embedAllPages(` e `clearExisting` (tutti i chiamanti e se qualcuno la lancia senza `clearExisting`)
2. `vector_clear_chunks`, `vectorClearChunks`, `clearChunkVectorTable` (altri chiamanti dello svuotamento, anche Rust)
3. `vector_drop_legacy`, `dropLegacyVectorTable`, `dropLegacyVectorTableBestEffort`
4. `Rebuild write failed after clearing`, `may be incomplete`, `Existing index was left unchanged`, `could not be embedded` (messaggi; test che li fissano)
5. `setEmbeddingReindexState`, `getEmbeddingReindexState`, `subscribeEmbeddingReindexState`, `EmbeddingReindexState` (altri consumatori dello stato; se qualcuno oltre `EmbeddingSection` mostra l'errore)
6. `reindexError`, `reindexAll`, `reindexing`, `legacyPromptTitle` (nei quattro `i18n/*.json` e nei componenti)
7. `embedPage(` (concorrenza con la ricostruzione)
8. `validate_page_id_for_v2`, `validate_page_id_common`, `Invalid page_id` (altri punti di validazione; test)
9. `wikiPageIdFromPath` (chiamanti; se l'id vuoto è gestito)
10. `vectorUpsertChunks`, `vector_upsert_chunks` (altri scrittori nel periodo di ricostruzione)
11. `getEmbeddingCount`, `vector_count_chunks` (chi mostra il conteggio e lo confronta con le pagine attese)
12. `vector_search_chunks`, `search_project`, `searchWiki`, `searchByEmbedding`, `"keyword"`, `vectorHits`, `vector_hits` (chi consuma la modalità di ricerca; se la UI la espone)
13. `wiki_vectors`, `wiki_chunks_v2`, `TABLE_V1` (qualunque percorso che legga v1 per ripristinare v2)
14. `backup`, `rollback`, `.bak`, `snapshot`, `restore`, `checkpoint`, `resume` nei file che toccano `lancedb` o `embedding` (conferma dell'assenza di salvaguardie)
15. `embedding.test.ts` e `vectorstore.rs` mod `tests_v2`: test su `clearExisting`, `vector_clear_chunks`, rebuild

## Note di estrazione

- **Stato**: **partial**. Commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` letto dal file `HEAD` del submodule; HEAD staccato, nessun nome di ramo.
- **Controllo repo invariato**: questo agente non ha `Bash`, quindi **non ha eseguito** `git -C code_repos/llm_wiki status --short` né `git log -1`. Nessuna scrittura sotto `code_repos/llm_wiki`. Il controllo a comando della DoD resta da eseguire dal chiamante.
- **Gate**: Fase 1 e Fase 4 assolte dall'approvazione dell'utente in chat per il solo perimetro del TSK-020; nessuna conferma separata. Dedup: la voce `2026-11-21-repo-llm_wiki-dossier-ep004-r6` non esisteva nel manifest.
- **Controllo segreti**: controllo per lettura dei 6 file elencati; nessun comando eseguibile. Letti solo nomi di campo (`apiKey`, `embeddingApiKey`, `extraHeaders`) e testi segnaposto dell'interfaccia; non aperti file `.env*` né `app-state.json`. Nessun valore riportato. Segreti redatti: 0 (vale per i file letti, non è una scansione dell'intero repo).
- **Istruzioni trovate nei file letti**: nessuna rivolta a un agente; solo commenti per i manutentori, non eseguiti.
- **Nessuna scrittura** in `wiki/` né nel kanban.

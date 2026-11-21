---
source_path: /home/user/wiki-factory/code_repos/llm_wiki
source_type: repo
git_branch: HEAD
git_commit: e08cfce65aad8b76b13546a081c1a8d4422b70c3
extracted_at: 2026-11-21
extractor: repo-sync@2.12.0
scope: dossier EP-004 r7 (TSK-024 / US-031), rischio 7, cambio di modello o di dimensione dell'embedding
---

# Specifiche estratte: llm-wiki, dossier EP-004 r7 (rischio 7, cambio di modello o dimensione dell'embedding)

> Documento generato da `repo-sync` v2.12 il 2026-11-21. Sorgente: `/home/user/wiki-factory/code_repos/llm_wiki`
> @ commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` (HEAD staccato, nessun nome di ramo: il file `.git/modules/code_repos/llm_wiki/HEAD` della factory contiene solo l'hash, riletto in questa sessione). Read-only verso la sorgente.

## Identità e perimetro

- Estrazione **mirata** (TSK-024 / US-031), per sola lettura del codice (Q_003). Stack e struttura non ripetuti. Parte da wiki (gap `llm-wiki-embedding-cambio-modello` in `wiki/gaps.md`; rischio 7 in `wiki/concepts/llm-wiki-rischi-persistenza.md` §Dettaglio e §Aggiornamenti v2026-11-21) e **non ripete** quanto già nei dossier r5 (impronta di revisione, ramo senza impronta di `embedPage`, due percorsi) e r6 (ordine di `embedAllPages`, messaggi di errore del re-index, ricerca con tabella assente): qui compaiono solo le parti nuove sul cambio di modello o dimensione e i rinvii espliciti.
- **Licenza**: repository di terzi, GNU GPL v3. Solo nomi di file, simboli e righe; nessun frammento di codice. Le uniche stringhe alla lettera sono testi mostrati all'utente o messaggi di errore, citate come stringhe.
- Citazioni `[^src: percorso:righe]`, percorsi relativi alla radice del repo del cliente.
- «Osservato» = letto nel codice in questa sessione. «Ereditato» = riportato da r5, r6 o dalla wiki, **non riletto qui**. «Deduzione non testata» = ricavata da fatti osservati, mai vista in esecuzione. Nessuna esecuzione, nessuna prova con un modello diverso. Nessuna ricerca testuale globale (l'agente non ha `Bash` né `Grep`): un «non trovato» vale solo per le righe lette di §File letti e non letti.
- **Limite dichiarato in anticipo (TSK-024)**: il comportamento di LanceDB a una scrittura (`merge_insert`, `create_table`) o a una query con dimensione diversa da quella della tabella non è deducibile per lettura: il sorgente di `lancedb` e di `arrow` non è stato letto. Esito «non conclusivo» con motivo.

## Ipotesi di partenza (come in wiki / US-031)

La dimensione del vettore è fissata dal primo chunk di una scrittura; nel campione non c'è un controllo esplicito di coerenza con la tabella esistente; la gestione del cambio di modello sembra affidata al re-index (l'impronta include il modello). La wiki (v2026-11-21) aggiunge già: assenza di confronto in scrittura (`merge_insert`) e in ricerca, impronta che include modello ed endpoint ma non la chiave API, re-index manuale con azzeramento della tabella, nessun re-index né avviso al salvataggio; restano non verificati il comportamento di LanceDB e se `embedAllPages` rilevi il cambio.

## 1. Scrittura con dimensione diversa nella tabella esistente (AC2)

Simbolo: `vector_upsert_chunks_inner` [^src: src-tauri/src/commands/vectorstore.rs:481-547].

| Passo | Cosa fa (osservato) | Righe |
|---|---|---|
| a | la dimensione `dim` è la lunghezza dell'embedding del **primo** chunk; zero → errore «Chunk #0 has empty embedding» | 495-498 |
| b | lo schema (`make_schema_v2(dim)`) e il batch sono costruiti **con quella dimensione**, prima di sapere se la tabella esiste | 505-506; 382-395, 397-453 |
| c | unico controllo dimensionale: ogni chunk del batch deve avere la `dim` del primo, altrimenti «Chunk #… has embedding dim … but batch dim is …» | 410-418 |
| d | se la tabella v2 esiste: `open_table`, poi `merge_insert` su `chunk_id`, con aggiornamento dei corrispondenti, inserimento dei nuovi, cancellazione dei non corrispondenti **della stessa pagina**; il batch porta lo schema di (b) | 513-529 |
| e | se non esiste: `create_table` con quel batch (la dimensione della tabella nasce dal primo chunk della prima scrittura) | 530-535 |
| f | errore di `merge_insert` riportato come «Atomic page upsert failed: …» | 529 |

**Osservato**: tra apertura (514-518) e `merge_insert` (521-529) **non c'è alcuna lettura dello schema o della dimensione della tabella esistente** né confronto con `dim`. Lo schema di v2 non ha colonne di modello, endpoint o dimensione dichiarata: solo `chunk_id`, `page_id`, `chunk_index`, `chunk_text`, `heading_path`, `vector` come lista a dimensione fissa (382-395). Quindi **l'indice non registra con quale modello è stato scritto**: l'unica traccia è il file di revisione per pagina, scritto solo dal ramo Rust (§3).

Il test che copre la dimensione (`v2_rejects_mismatched_embedding_dimensions`, [^src: vectorstore.rs:1243-1265]) verifica solo l'incoerenza **dentro lo stesso batch** (16 poi 8). **Nessun test letto** scrive con dimensione diversa su una tabella già esistente (i test `tests_v2` letti usano sempre 16, 1047-1326).

**Ereditato da r6 §2** (non riletto): lo stesso errore di dimensione intra-batch è osservato lato TS come assente (`embedding.ts:421-423` non controlla la coerenza). In questa sessione confermato: `preparePageEmbeddingRows` calcola `failedChunks` ma non confronta le lunghezze dei vettori [^src: src/lib/embedding.ts:421-439]. Lato Rust `validate_embedding_rows` controlla vettore non vuoto e dimensioni uguali **fra le righe della stessa chiamata**, mai con la tabella [^src: src-tauri/src/commands/page_embedding.rs:202-216].

**Che cosa succede quando la dimensione differisce dalla tabella**: **NON CONCLUSIVO** (motivo: l'esito di `merge_insert` con schema di dimensione diversa su una tabella a lista a dimensione fissa dipende da `lancedb`/`arrow`, non letti; il codice dell'applicazione non lo previene né lo gestisce in modo specifico, vedi riga f). Le due alternative (errore, oppure scrittura accettata con effetti non noti) non sono distinguibili per lettura.

**Osservato, se la scrittura fallisce**:
- Ramo Rust (`embed_wiki_page`): l'errore ritorna come `Storage` [^src: page_embedding.rs:188-190] → API 500 con il messaggio [^src: src-tauri/src/api_server.rs:1932, 1935]. `save_revision` non è raggiunta (la funzione esce con errore prima, vectorstore.rs:529, `?`); resta la revisione vecchia della pagina e restano le righe vecchie.
- Ramo TS (`embedPage`): `vectorUpsertPageChunks` non è in `try`; l'errore risale al chiamante [^src: embedding.ts:491]. Come lo gestiscano i chiamanti (`ingest.ts`, `deep-research.ts`, noti dalla wiki): **non letti**.

**Deduzione non testata (stessa dimensione, modello diverso)**: se il nuovo modello produce vettori della **stessa** dimensione della tabella (caso possibile fra modelli diversi), nessun controllo del codice letto lo rileva: la scrittura procede come una normale, e la tabella conterrebbe righe di modelli diversi nello spazio dei vettori, con punteggi non comparabili. Nessun modo di distinguerle dal solo schema (vedi sopra). Non provato.

## 2. Ricerca con vettore di query di dimensione diversa (AC2)

Due percorsi, entrambi senza controllo dimensionale:

| Percorso | Osservato | Fonte |
|---|---|---|
| Rust `vector_search_chunks` (usato da UI via `search_project` e dall'API) | apre la tabella v2 e chiama la ricerca vettoriale con il vettore ricevuto; nessun confronto con lo schema; gli errori sono mappati «Search error: …» e «Execute search error: …» | vectorstore.rs:588-675 (618-624) |
| `resolve_query_embedding` / `validate_query_embedding` | verifica solo «non vuoto» e «solo numeri finiti»; messaggi «queryEmbedding must not be empty», «queryEmbedding must contain only finite numbers»; nessuna dimensione | search.rs:294-325 |
| Esito dell'errore in `search_project_inner` | `Err` di `search_by_embedding` → `eprintln` «[Search] vector search failed; falling back to keyword results: …» e si prosegue con le sole parole chiave; nessun avviso all'utente | search.rs:437-462 (455-459); 802-852 |
| TS `searchByEmbedding` | `catch` attorno a `vectorSearchChunks`: `console.log` «[Embedding] LanceDB chunk search failed: …» e ritorno `[]` | embedding.ts:798-803 |

Il vettore di query è calcolato con la configurazione **corrente** (`fetch_embedding_with_retry` con `cfg`, search.rs:308; TS `fetchEmbedding(query, cfg)`, embedding.ts:793), quindi dopo un cambio di modello salvato la query ha la dimensione del modello nuovo mentre la tabella ha quella vecchia fino al re-index.

**Cosa succede alla ricerca con dimensione diversa**: **NON CONCLUSIVO** (stesso motivo: dipende da `lancedb`). **Osservato** il lato applicazione: se la libreria **rifiuta** la query, la ricerca ripiega **in silenzio** sulle parole chiave (log su stderr o console, nulla in interfaccia: il campo `mode` esiste nella risposta, search.rs:54-60, ma il TS non lo usa, ereditato da r6 §6). Se la libreria **non** rifiuta, i punteggi sono quelli che la libreria calcola: non determinabile (deduzione non testata: risultati privi di senso senza alcun segnale).

## 3. Impronta di revisione: che cosa cambia con modello e dimensione (AC3)

Simbolo: `embedding_fingerprint` [^src: page_embedding.rs:266-280]. Il meccanismo (file `.llm-wiki/embedding-revisions/<sha256 id>.revision`, `save_revision`, `invalidate_page_revision`, confronto in `vector_page_revision_match`) è in r5 §3 e **non è ripetuto**.

**Osservato, gli elementi**: sha256 del contenuto della pagina (`revision`, riga 125), `endpoint` (trim), `model` (trim), `outputDimensionality`, `extraHeaders`, `maxChunkChars` (default 1000), `overlapChunkChars` (default 200). **Non** la chiave API (confermato dal test `fingerprint_changes_with_embedding_semantics_but_not_api_key_rotation`, 780-794, che verifica modello diverso ⇒ impronta diversa e chiave ruotata ⇒ impronta uguale) e **non** la dimensione effettivamente restituita dal provider.

| Cambio nelle impostazioni | Cambia l'impronta? | Effetto sulla dimensione dei vettori |
|---|---|---|
| `model` | **sì** | dipende dal modello; non letto dal codice |
| `endpoint` | **sì** | idem |
| `outputDimensionality` | **sì** | **solo** per endpoint Gemini/`embedContent`: nel corpo della richiesta compare solo lì (search.rs:1391-1397); per gli endpoint OpenAI-compatibili il corpo è `model` più `input`, senza dimensione (1396; batch 1252) |
| `extraHeaders`, `maxChunkChars`, `overlapChunkChars` | sì | nessuna |
| chiave API | no | nessuna |

**Osservato, conseguenza**: per un endpoint non Gemini, cambiare `outputDimensionality` **cambia l'impronta senza cambiare i vettori** richiesti (il campo è ignorato dal corpo): le pagine risultano da ri-embeddare via Rust senza motivo. Lo conferma il testo dell'interfaccia, che dichiara «Sent only for Gemini native embedContent endpoints» [^src: src/i18n/en.json:643]. Viceversa, un cambio di modello su **endpoint e dimensione dichiarata invariati** cambia comunque l'impronta (campo `model`).

**Quali pagine risultano da re-indicizzare (osservato per la regola, deduzione non testata per l'insieme reale)**:
- Rust, `embed_wiki_page` senza `force`: una pagina è saltata («unchanged») solo se la revisione salvata coincide con l'impronta calcolata **e** la tabella ha righe per quella pagina [^src: page_embedding.rs:127-142; vectorstore.rs:549-582]. Dopo un cambio di modello l'impronta calcolata è nuova: **ogni pagina con una revisione salvata** risulta da ri-embeddare.
- Pagine senza revisione (scritte dal ramo TS `embedPage`, che invalida il file, vectorstore.rs:467, 542-544, ereditato r5 §3) risultano **sempre** da ri-embeddare via Rust, con o senza cambio.
- TS: `embedPage` e `embedAllPages` **non consultano l'impronta** (r5 §3, r6 §5; riconfermato: nessun riferimento a revisione o impronta in embedding.ts:471-500 e 578-762). Quindi nessun percorso TS usa l'impronta per decidere cosa re-indicizzare.
- L'impronta è per **pagina** ed è confrontata solo nel ramo Rust: non esiste un'impronta di tabella o di progetto (il file `.revision` è uno per pagina, page_embedding.rs:326-331; nessuna riga letta ne conserva una globale).

## 4. `embedAllPages` e `embedPage` rilevano il cambio? (AC3, AC5)

**Osservato: no.** In `embedAllPages` (578-762) l'unica condizione sulla configurazione è `enabled` e `model` non vuoto (584); non vengono letti il modello o la dimensione dei vettori già indicizzati, la dimensione della tabella, né le revisioni; non c'è confronto fra configurazione corrente e precedente. Il caso `clearExisting: true` (l'unico chiamante, `embedding-section.tsx:124-129`, dalla wiki/r6) **elimina la tabella** (705) e la ricrea alla prima scrittura (vectorstore.rs:530-535), quindi **ricostruisce con la dimensione del modello corrente**: il cambio è assorbito dalla ricostruzione manuale, non rilevato. (Che `create_table` con una dimensione nuova sia accettata dalla libreria dopo `drop_table`: **non conclusivo**, `lancedb` non letto; il percorso è quello di ogni creazione iniziale, quindi plausibile.)

**Il ramo non distruttivo**: se alcune pagine falliscono, `embedAllPages` non svuota e scrive le riuscite sulla tabella esistente (677-693), cioè col nuovo modello su una tabella potenzialmente di dimensione diversa (r6 §3.2). Qui il comportamento dipende da §1 (non conclusivo) e gli errori di scrittura per pagina finiscono nell'elenco dei fallimenti (684-686) e nel messaggio finale (690), che dice «failed pages kept their previous vectors and can be retried» (testo alla lettera, riga 690): **con un cambio di dimensione i vettori «precedenti» sono quelli del modello vecchio**; il messaggio non lo segnala (osservato come assenza di testo).
Il ramo senza `clearExisting` (737-754) ingoia gli errori per pagina in un `catch` vuoto (748-750), ma non è raggiunto dal chiamante letto (sempre `clearExisting: true`).

**`embedPage`** (471-500): nessun confronto di dimensione, né con la tabella né con le righe già scritte per quella pagina; usa la configurazione passata dal chiamante (non letto da dove la prendano).

**Pagine non toccate dal re-index**: un re-index completo con svuotamento riscrive tutte le pagine di contenuto (esclusi `index`, `log`, `overview`, `purpose`, `schema`, 610): nessuna pagina resta col modello vecchio **se il re-index termina senza errori** (r6 §3-5 per gli errori).

## 5. Avvisi all'utente al cambio di modello o dimensione (AC4)

**Osservato, il salvataggio delle impostazioni** (`handleSave`, [^src: src/components/settings/settings-view.tsx:356-658]): costruisce `newEmbed` dal bozza (397-408), aggiorna lo store (470) e lo persiste con `saveEmbeddingConfig` (485). **Nessun confronto** fra bozza e configurazione precedente (la configurazione precedente `embeddingConfig` compare solo fra le dipendenze del callback, 634, e nel ripristino dopo un errore di salvataggio, 611); **nessuna chiamata a `embedAllPages`** né ad altra funzione di re-index; l'unico messaggio è l'esito del salvataggio (`settings.savedTick`, `settings.saveFailed`, 761-766). Quindi **nessun avviso e nessuna richiesta di re-index al salvataggio**.

**Osservato, la schermata Embedding** (`EmbeddingSection`, [^src: src/components/settings/sections/embedding-section.tsx:81-488]):
- l'unico testo che menziona il cambio è un suggerimento **statico**, sotto il campo «Output dimensionality (Gemini only)»: «Optional. Sent only for Gemini native embedContent endpoints as `output_dimensionality`; OpenAI-compatible endpoints ignore this field. Leave empty for the model default. Rebuild embeddings after changing model or dimension.» [^src: src/i18n/en.json:643; uso: embedding-section.tsx:258-260]. È sempre visibile con l'embedding abilitato, **non condizionato** a un cambio avvenuto; il suggerimento del campo modello (en.json:641) non lo menziona;
- le statistiche mostrano solo «{{count}} chunks indexed» (en.json:662; section 424-426): niente modello, niente dimensione dell'indice, niente confronto con la configurazione;
- gli avvisi condizionati nella sezione sono tre: indice legacy (170-171, 409-418), errore dell'ultimo embedding (473-482), esito del re-index (455-465): **nessuno dipende da un cambio di modello o dimensione**;
- i test di provider mostrano la dimensione restituita («Returned {n} dimensions…», «Stable {n}-dimension finite vectors returned.») ma **non la confrontano con l'indice** [^src: src/lib/connection-tests.ts:12-33, 35-63];
- **Osservato, dettaglio che incide**: `handleReindex` usa `embeddingConfig` **dallo store** (84, 124-129, dipendenze 134), non la bozza (`draftEmbeddingConfig`, 143-154, usata solo dai test). Quindi un re-index lanciato **prima di salvare** il nuovo modello ricostruisce con il **modello vecchio** (deduzione non testata sull'effetto pratico; dipende dal fatto che lo store sia aggiornato solo da `handleSave`, 470).
- Ho letto solo `en.json`: `it.json`, `ru.json`, `zh.json` non letti (il testo potrebbe differire).

**Osservato, altri punti**: nessun avviso nel ramo Rust (`embed_wiki_page`, `PageEmbeddingResult` porta `path`, `pageId`, `revision`, `chunks`, `vectorsWritten`, `status`, nessun campo su modello o dimensione, page_embedding.rs:25-34; risposta API in api_server.rs:1921-1926).

## 6. I due percorsi di embedding (TS e Rust, API/MCP) (AC3, AC5)

| Aspetto | TS (`embedPage`, `embedAllPages`) | Rust (`embed_wiki_page`, via `pages/embed`, anche da MCP) |
|---|---|---|
| Chi lo avvia | ingest, deep research, Settings (wiki) | API `POST pages/embed` (api_server.rs:1897-1938), MCP `llm_wiki_embed_page` (raw api-mcp) |
| Configurazione usata | quella passata dal chiamante (store in memoria) | `load_embedding_config(app)` (api_server.rs:1909; corpo **non letto**) |
| Impronta | non calcolata né consultata | calcolata e salvata (page_embedding.rs:125-126, 188) |
| Rileva il cambio di modello | **no** | **sì, solo per pagina**, perché l'impronta cambia (§3); non rileva la dimensione |
| Scrittura | `vector_upsert_chunks` (senza revisione) | `vector_upsert_chunks_with_revision` |
| Controllo dimensione con la tabella | no | no |
| Avviso all'utente | no | errore `Storage` 500 se la scrittura fallisce; nessun avviso su modello |

**Deduzione non testata (due configurazioni)**: dopo il salvataggio, lo store in memoria (usato dal TS) è aggiornato per primo (settings-view.tsx:470) e quello persistito dopo (485); il lato Rust legge la configurazione persistita, con un debounce di salvataggio automatico di 100 ms dichiarato dalla wiki (non rilevato qui nel codice letto; il corpo di `load_embedding_config` non è letto). C'è quindi una breve finestra in cui i due percorsi userebbero configurazioni diverse. Non provato.

**Deduzione non testata (alternanza)**: dopo un cambio di modello, un'indicizzazione di singola pagina via TS (ingest) o via Rust (API/MCP) scrive righe del modello nuovo nella tabella del vecchio (§1): l'esito di quella scrittura è non conclusivo; se riuscisse, la tabella conterrebbe righe di due modelli fino al re-index manuale.

## 7. Esito proposto e tabella evidenze (AC5, AC6)

**Esito proposto: CONFERMATO per lettura** per l'ipotesi della wiki (nessun controllo di coerenza dimensionale con la tabella esistente; gestione del cambio affidata al re-index manuale; impronta che include il modello; nessun avviso al salvataggio; `embedAllPages` non rileva il cambio, lo assorbe solo se l'utente lancia «Re-index all pages»). **NON CONCLUSIVO** per: (a) che cosa faccia LanceDB a una scrittura o a una query con dimensione diversa da quella della tabella (errore o accettazione), (b) come reagisce `create_table` dopo `drop_table` con una nuova dimensione, (c) l'esistenza di righe di modelli diversi nella stessa tabella a parità di dimensione (deduzione dal codice, non provata). Motivo comune: sorgenti di `lancedb` e `arrow` non letti, nessuna esecuzione.

**Precisazioni rispetto alla wiki**: (1) lo schema di v2 non registra modello né dimensione dichiarata; l'unico dato per pagina è il file di revisione, scritto solo dal ramo Rust; (2) per endpoint non Gemini `outputDimensionality` entra nell'impronta ma non nella richiesta; (3) un avviso «Rebuild embeddings after changing model or dimension» esiste, ma come testo statico sul campo di dimensionalità, non come avviso al cambio; (4) il re-index usa la configurazione **salvata**, non la bozza.

**Impatto sui dati se si verifica (deduzione non testata)**: nessuna perdita di pagine wiki né di sorgenti (l'indice è derivato dal testo e ricostruibile, come in r6). Effetti sull'indice: (i) con dimensione diversa, ricerca semantica degradata o assente con ripiego silenzioso sulle parole chiave, e indicizzazioni di singola pagina che falliscono o producono uno stato misto (non conclusivo); (ii) con stessa dimensione e modello diverso, vettori incomparabili nella stessa tabella senza alcun errore; (iii) costo: tutte le chiamate al provider per il re-index. Dopo un re-index **riuscito** l'indice è coerente col nuovo modello (r6 per gli errori). Gravità proposta (non decisione): media, perché il guasto è silenzioso; da valutare in US-033.

**Stato proposto del gap `llm-wiki-embedding-cambio-modello`**: **resta aperto** per il solo comportamento di LanceDB (a). Tutte le parti verificabili per lettura sono ora chiuse: dimensione dal primo chunk e nessun confronto con la tabella (vectorstore.rs:495-535), ricerca senza controllo (vectorstore.rs:588-675; search.rs:317-325), impronta e suoi elementi (page_embedding.rs:266-280), `embedAllPages` non rileva il cambio (embedding.ts:578-762), nessun avviso al salvataggio (settings-view.tsx:356-658), testo statico (en.json:643). Chiudibile da `wiki-keeper` se l'utente accetta «non conclusivo per lettura» come stato finale, con il motivo dichiarato; altrimenti serve la lettura del sorgente di `lancedb` o una prova in esecuzione (esclusa da Q_003).

| # | Punto | Esito | Evidenza | Livello |
|---|---|---|---|---|
| 1 | Dimensione fissata dal primo chunk | **CONFERMATO** | vectorstore.rs:495, 505-506 | osservato |
| 2 | Confronto fra dimensione da scrivere e tabella esistente prima di scrivere | **SMENTITO** (non esiste nelle righe lette) | vectorstore.rs:513-529 (nessuna lettura di schema); 410-418 solo intra-batch; page_embedding.rs:202-216 solo intra-chiamata | osservato (limitato ai file letti) |
| 3 | Esito della scrittura con dimensione diversa | **NON CONCLUSIVO** | `lancedb` non letto; messaggio d'errore 529 | motivo dichiarato |
| 4 | Test su dimensione diversa dalla tabella | **non trovato** nei test letti | vectorstore.rs:1243-1265 (intra-batch); 1047-1326 solo dim 16 | osservato |
| 5 | Ricerca con query di dimensione diversa: controllo | **assente** nel codice dell'applicazione | search.rs:317-325; vectorstore.rs:618-624 | osservato |
| 6 | Ricerca con query di dimensione diversa: esito | **NON CONCLUSIVO** (errore → ripiego silenzioso; non errore → ignoto) | search.rs:455-459; embedding.ts:798-803 | osservato per il lato app |
| 7 | Elementi dell'impronta | **CONFERMATO**: contenuto, endpoint, modello, outputDimensionality, extraHeaders, maxChunkChars, overlapChunkChars; non chiave né dimensione reale | page_embedding.rs:266-280, 780-794 | osservato |
| 8 | `outputDimensionality` per endpoint non Gemini | cambia l'impronta, **non la richiesta** | page_embedding.rs:271; search.rs:1391-1397, 1252; en.json:643 | osservato |
| 9 | Schema di v2 senza modello né dimensione dichiarata | **CONFERMATO** | vectorstore.rs:382-395 | osservato |
| 10 | `embedAllPages` / `embedPage` rilevano il cambio | **SMENTITO** | embedding.ts:471-500, 578-762 | osservato |
| 11 | Re-index manuale assorbe il cambio (drop e ricreazione con la nuova dimensione) | **CONFERMATO** il meccanismo; accettazione di `create_table` con dimensione nuova **non conclusivo** | embedding.ts:705; vectorstore.rs:530-535, 760-787 | osservato / non conclusivo |
| 12 | Avviso o re-index richiesto al salvataggio | **SMENTITO** (nessuno) | settings-view.tsx:397-408, 470, 485, 761-766 | osservato |
| 13 | Testo che invita al re-index | esiste, **statico**, non condizionato | en.json:643; embedding-section.tsx:258-260 | osservato (solo `en.json`) |
| 14 | Re-index usa la bozza o la config salvata | config **salvata** (store) | embedding-section.tsx:84, 124-129, 143-154 | osservato |
| 15 | Percorso Rust: rileva il cambio | per **pagina**, via impronta; non la dimensione | page_embedding.rs:125-142; vectorstore.rs:549-582 | osservato |
| 16 | Righe di modelli diversi a pari dimensione nella stessa tabella | deduzione non testata | assenza di controllo (§1) | deduzione |
| 17 | Config diverse fra percorso TS e Rust durante il salvataggio | deduzione non testata | settings-view.tsx:470 vs 485; `load_embedding_config` non letto | deduzione |

## File letti e non letti

**Repo del cliente, letti in questa sessione (9 file, sola lettura)**:
- `src/lib/embedding.ts` (1-871, intero)
- `src/components/settings/sections/embedding-section.tsx` (1-489, intero)
- `src/components/settings/settings-view.tsx` (1-778, intero)
- `src/lib/connection-tests.ts` (1-125, intero)
- `src-tauri/src/commands/vectorstore.rs` (1-150, 380-1337)
- `src-tauri/src/commands/page_embedding.rs` (1-894, intero)
- `src-tauri/src/commands/search.rs` (1-340, 436-476, 770-909, 1000-1599)
- `src-tauri/src/api_server.rs` (1890-1945)
- `src/i18n/en.json` (625-700)

Letti anche, fuori dall'albero di lavoro: `.git/modules/code_repos/llm_wiki/HEAD` della factory (hash `e08cfce65aad8b76b13546a081c1a8d4422b70c3`). Letti come contesto factory: TSK-024, US-031, dossier r4, r5, r6, `raw/2026-11-21-repo-llm_wiki-api-mcp.md`, `wiki/gaps.md` (righe 1-241, incluso il gap), `wiki/concepts/llm-wiki-rischi-persistenza.md` (intero), manifest.

**Non letti, con motivo**:
- Sorgente di `lancedb` e `arrow` (`merge_insert`, `create_table`, `vector_search` con dimensione diversa): esiti non conclusivi.
- `api_server.rs` `load_embedding_config` e il resto del file: da dove arriva la configurazione del ramo Rust, cache.
- `src/stores/wiki-store.ts` (tipo `EmbeddingConfig`, `setEmbeddingConfig`), `src/lib/project-store.ts` (`saveEmbeddingConfig`, `loadEmbeddingConfig`): punti d'uso e persistenza della configurazione non riletti qui; `App.tsx` (abilitazione iniziale).
- Chiamanti di `embedPage`: `ingest.ts`, `deep-research.ts` (noti dalla wiki, non riletti; come gestiscono un errore di scrittura è ignoto).
- `src/components/search/search-view.tsx` (se mostri una modalità di ricerca), `mcp-server/src/index.ts` e `api-client.ts` (letti solo tramite il raw `api-mcp`).
- `src/i18n/it.json`, `ru.json`, `zh.json`; resto di `en.json`.
- `search.rs` 340-436, 476-770, 909-1000 e oltre 1599; `vectorstore.rs` 150-380 (comandi v1), già in r6.
- Test: `embedding.test.ts`, `embedding.real-llm.test.ts`, `dedup_embedding.ts` e relativi test (esistenza di test sul cambio di modello non esclusa); `dedup_embedding.ts` usa embedding e non è stato aperto (non esclusi altri consumatori di vettori con dimensione propria).

## Gap evidenti

1. Comportamento di LanceDB per scrittura e query con dimensione diversa, e per `create_table` dopo `drop_table` con dimensione nuova (non conclusivo).
2. Origine e aggiornamento della configurazione nel ramo Rust (`load_embedding_config`) rispetto allo store in memoria del TS; finestra fra `setEmbeddingConfig` e `saveEmbeddingConfig`.
3. Come i chiamanti di `embedPage` (ingest, deep research) gestiscono un errore di scrittura da dimensione diversa.
4. Presenza di test o documentazione sul cambio di modello (`embedding.test.ts`, README, `plans/`).
5. Testi in `it.json`, `ru.json`, `zh.json` del suggerimento sul re-index.
6. Altri consumatori di embedding con dimensione propria (`dedup_embedding.ts`), fuori perimetro.

## Stringhe esatte da cercare (ricerca testuale globale, da eseguire dal chiamante)

Cartelle `src/`, `src-tauri/src/` e, se presenti, `mcp-server/`, `extension/`; per ciascuna: conteggio e file. Usare espressioni larghe, senza distinzione di maiuscole dove utile.

1. Dimensione: `dim`, `dimension`, `dimensions`, `outputDimensionality`, `output_dimensionality`, `embedding.len()`, `FixedSizeList`, `list_size`, `vector_dim` (qualsiasi confronto o lettura della dimensione, anche in test e in altri moduli)
2. Schema della tabella: `schema()`, `.schema(`, `make_schema_v2`, `make_batch_v2`, `table.schema`, `get_schema` (se qualcuno legge lo schema esistente)
3. Modello e impronta: `embedding_fingerprint`, `embeddingConfig`, `embedding_config`, `load_embedding_config`, `saveEmbeddingConfig`, `loadEmbeddingConfig`, `setEmbeddingConfig`, `EmbeddingConfig`, `SearchEmbeddingConfig` (punti d'uso della configurazione)
4. Cambio di modello: `model changed`, `model change`, `changed model`, `different model`, `switch.*model`, `previousModel`, `lastModel`, `indexedModel`, `embeddingModel`, `modelId` (rilevamento o memoria del modello usato)
5. Invito al re-index: `Rebuild embeddings`, `re-index`, `reindex`, `Re-index`, `rebuild`, `reembed`, `re-embed`, `reindexAll`, `reindexRequired`, `needsReindex`, `stale` (nei quattro `i18n/*.json`, nei componenti e nei test)
6. Avvisi: `toast`, `warning`, `confirm(`, `window.confirm`, `Dialog` insieme a `embedding` (dialoghi o conferme attorno alla sezione embedding)
7. Ricerca: `vector_search`, `vector_search_chunks`, `vectorSearchChunks`, `search_by_embedding`, `searchByEmbedding`, `queryEmbedding`, `query_embedding`, `validate_query_embedding`, `resolve_query_embedding`, `vector search failed`, `chunk search failed`
8. Scrittura: `merge_insert`, `create_table`, `drop_table`, `Atomic page upsert failed`, `Create table error`, `batch dim`, `embedding dim`, `inconsistent vector dimensions`, `empty or inconsistent`
9. Percorsi di embedding: `embedPage(`, `embedAllPages(`, `embed_wiki_page`, `pages/embed`, `llm_wiki_embed_page`, `embedPage` nel client MCP (`mcp-server/src/index.ts`, `api-client.ts`)
10. Revisioni: `load_revision`, `save_revision`, `invalidate_page_revision`, `embedding-revisions`, `.revision`, `vector_page_revision_match`, `REVISION_DIR`
11. Test: `v2_rejects_mismatched_embedding_dimensions`, `mismatched`, `dimension`, `fingerprint_changes`, `embedding.test.ts`, `tests_v2` (test che coprano scrittura o ricerca con dimensioni diverse o cambio di modello)
12. Documentazione: `README`, `plans/`, `docs/` con `embedding`, `dimension`, `model` (descrizione ufficiale del cambio di modello)

## Note di estrazione

- **Stato**: **partial**. Commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` letto dal file `HEAD` del submodule; HEAD staccato, nessun nome di ramo. Perimetro letto parziale (vedi §Non letti): punti d'uso della configurazione non enumerati.
- **Gate**: Fase 1 e Fase 4 assolte dall'approvazione dell'utente in chat per il solo perimetro del TSK-024; nessuna conferma separata. Dedup: la voce `2026-11-21-repo-llm_wiki-dossier-ep004-r7` non esisteva nel manifest.
- **Controllo repo invariato**: questo agente non ha `Bash`, quindi **non ha eseguito** `git -C code_repos/llm_wiki status --short` né `git log -1`. Nessuna scrittura sotto `code_repos/llm_wiki`. Il controllo a comando della DoD resta da eseguire dal chiamante.
- **Controllo segreti**: controllo per lettura dei 9 file elencati. Letti solo nomi di campo e segnaposto dell'interfaccia (`apiKey`, `embeddingApiKey`, `extraHeaders`, «Leave empty for local models»); nel test Rust di `page_embedding.rs` compare un valore fittizio per la chiave, **non riportato**; nessuna chiave API di embedding reale incontrata; non aperti file `.env*` né `app-state.json`. Segreti redatti: 0 (vale per i file letti, non è una scansione dell'intero repo).
- **Istruzioni trovate nei file letti**: nessuna rivolta a un agente; solo commenti e testi per i manutentori o per gli utenti, non eseguiti.
- **Nessuna scrittura** in `wiki/` né nel kanban.

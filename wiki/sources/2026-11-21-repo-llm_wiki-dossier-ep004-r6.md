---
id: 2026-11-21-repo-llm_wiki-dossier-ep004-r6
type: source
title: Dossier EP-004 r6 da code_repos/llm_wiki, 2026-11-21: rischio 6, ricostruzione dell'indice senza rollback (repo-sync)
status: draft
created: 2026-11-21
updated: 2026-11-21
sources: ["raw/2026-11-21-repo-llm_wiki-dossier-ep004-r6.md"]
tags: [source, repo, llm-wiki, persistenza, embedding, reindex, ep-004, rischio-6]
---

# Dossier EP-004 r6 da code_repos/llm_wiki, 2026-11-21: rischio 6, ricostruzione dell'indice senza rollback (repo-sync)
> Estrazione mirata `repo-sync` v2.12 del 2026-11-21 sul commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` (HEAD staccato, nessun ramo), stato `partial`, 6 file letti, sola lettura (Q_003). «Osservato» = letto nel codice (per costruzione, non eseguito); «deduzione non testata» = ricavata da fatti osservati, mai eseguita. Repo di terzi sotto GNU GPL v3: il raw riporta solo nomi di file, simboli e righe e i messaggi mostrati all'utente, nessun frammento di codice.

## Contesto
Sesto dossier della serie di EP-004 (TSK-020 / US-030), dedicato al rischio 6 di [[llm-wiki-rischi-persistenza]]; segue [[2026-11-21-repo-llm_wiki-dossier-ep004-r5]]. Traccia l'ordine delle operazioni di `embedAllPages` con `clearExisting: true`, dove un errore interrompe il flusso, che cosa resta nell'indice, il messaggio all'utente, il rilancio e la ricerca con tabella assente o vuota. Limite dichiarato in anticipo: il comportamento di LanceDB su errore parziale non è osservabile per lettura (sorgente della libreria non letto). L'agente non aveva `Bash` né `Grep`: un «non trovato» del raw vale solo per i file letti; la ricerca testuale globale è della sessione principale, riportata in TSK-020 §Chiusura e qui in una sezione a parte. Stack e struttura: [[2026-11-20-repo-llm_wiki]]. Operazioni distruttive collegate: [[llm-wiki-operazioni-distruttive]]. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r6.md §Identità e perimetro]

## Dettaglio

### Ordine delle operazioni (osservato)
Simbolo `embedAllPages` (`src/lib/embedding.ts:578-762`). L'unico chiamante letto è `handleReindex` in `EmbeddingSection`, con `clearExisting: true` (`embedding-section.tsx:121-134`).

| Passo | Cosa fa | Righe | Se fallisce |
|---|---|---|---|
| 0-1 | uscita se embedding disabilitato; elenco dei `.md` sotto `wiki/` | `embedding.ts:584-616` | albero illeggibile: errore, **indice intatto** (594-598) |
| 2 | zero pagine: con chunk indicizzati errore, indice intatto; senza chunk svuota e termina | 623-635 | prima di ogni svuotamento |
| 3 | **calcolo degli embedding, nessuna scrittura al database** (3 tentativi per pagina) | 637-675; 548-570 | nessuna scrittura |
| 4 | se ci sono pagine non calcolate: **non svuota**, scrive con upsert solo le pagine riuscite, poi errore «N of M pages could not be embedded…» | 677-693 | indice non svuotato |
| 5 | nessuna pagina pronta e chunk presenti: errore, indice intatto | 695-703 | prima dello svuotamento |
| 6 | **svuotamento** `clearChunkVectorTable` → comando `vector_clear_chunks` (`drop_table` di `wiki_chunks_v2`) | 705; 281-285, 309-311; `vectorstore.rs:759-787` | errore non catturato: la promessa rifiuta, **stato in memoria resta `running`** |
| 7 | **scritture** una pagina alla volta, in sequenza | 707-723 | al primo errore il messaggio sotto; pagine successive non tentate |
| 8 | ottimizzazione solo se `written > 0`, errori solo `console.warn` | 725-727 | non propaga |
| 9 | eliminazione della tabella legacy `wiki_vectors` (`vector_drop_legacy`), errori solo `console.warn` | 731; `vectorstore.rs:889-915` | non propaga |
| 10 | stato `done` con `count: written` | 733-734 | – |

Il calcolo (passo 3) precede lo svuotamento (passo 6); fra 6 e 7 non c'è copia, rinomina o tabella di appoggio. `vector_clear_chunks` torna `Ok` anche se la tabella non esiste. L'ordine delle pagine scritte è quello di **completamento** dei worker, non dell'albero (`embedding.ts:530-546, 659`): deduzione non testata, con concorrenza maggiore di 1 l'insieme scritto prima di un errore varia da un tentativo all'altro. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r6.md §1. Ordine delle operazioni di `embedAllPages` con `clearExisting: true` (AC2)]

### Dove un errore interrompe il flusso (osservato)
Tre famiglie: **A** prima dello svuotamento (albero illeggibile, zero pagine, solo pagine vuote, pagine non calcolate): indice invariato, salvo le pagine riuscite del passo 4; **B** lo svuotamento stesso fallisce: stato **non determinabile per lettura** (dipende da `drop_table`); **C** una scrittura fallisce dopo lo svuotamento: tabella assente o parziale. Cause di fallimento di scrittura nel comando Rust, tutte dopo lo svuotamento: `page_id` rifiutato (caratteri di controllo, apici, barra rovesciata, caratteri invisibili, oltre 256 caratteri o vuoto: `vectorstore.rs:67, 78-114, 378-380, 487`); dimensione dei vettori incoerente nella stessa pagina (`vectorstore.rs:410-418, 506`); errori di connessione, apertura, creazione tabella, `merge_insert` (`vectorstore.rs:500-535`); disco pieno e permessi non osservabili. **Osservato:** il lato TS non valida l'id né la dimensione prima dello svuotamento (`embedding.ts:382-440`); deduzione non testata: una pagina con un nome file non ammesso supera il calcolo e fallisce solo in scrittura. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r6.md §2. Dove un errore interrompe il flusso (AC2, AC3)]

### Che cosa resta nell'indice dopo un errore (osservato)
- **Famiglia C, prima scrittura fallita:** la tabella v2 **non esiste** (la ricrea solo la prima scrittura riuscita, `vectorstore.rs:530-535`). **k-esima scrittura fallita:** restano le pagine già scritte (ognuna in una sola chiamata, dichiarata atomica per pagina dal codice) e mancano tutte le altre, comprese quelle non tentate. Ottimizzazione e `vector_drop_legacy` non eseguiti: la tabella legacy, se presente, **resta**.
- **Contenuto effettivo dopo un errore a metà pagina: NON CONCLUSIVO** (motivo: atomicità di `merge_insert` e `create_table` di LanceDB non letta; il commento del codice la dichiara, non la verifica).
- **Pagine fallite al passo 4:** nessuno svuotamento; le pagine riuscite sono scritte sulla tabella esistente; le righe di pagine eliminate dal wiki non sono rimosse; confronto della dimensione dei vettori con l'indice esistente assente (con cambio di modello effetto non conclusivo, rimanda a US-031).
- **Revisioni:** `vector_clear_chunks` non tocca i file di revisione; le pagine scritte restano senza revisione, quelle non scritte hanno una revisione vecchia ma nessuna riga, e `vector_page_revision_match` ritorna `None` senza righe (`vectorstore.rs:557-581`). Deduzione non testata: stato «incoerente ma autoprotetto», costo di ri-embedding, non perdita. Dubbio residuo non conclusivo: invalidazione fallita (errore ignorato, `vectorstore.rs:543`) con righe presenti. `embedAllPages` non consulta le revisioni. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r6.md §3. Che cosa resta nell'indice dopo un errore (AC3)]

### Messaggio all'utente e segnalazione nell'interfaccia (osservato)
Testo (famiglia C, `embedding.ts:714-717`): «Rebuild write failed after clearing existing chunks (`<pageId>`: `<motivo>`). The rebuilt index may be incomplete; run re-index again after fixing the error.» Dice «may be incomplete» e **non** riporta quante pagine sono state scritte né quante mancano. Altri messaggi (famiglia A): «Could not read wiki tree; existing index was left unchanged.» (595); «… Existing index was left unchanged.» (628, 700); «N of M pages could not be embedded (…). K successful page(s) were updated; failed pages kept their previous vectors and can be retried.» (690).

Interfaccia: lo stato è una variabile **in memoria** del modulo (`embedding.ts:508`, `525-528`), mostrata solo da `EmbeddingSection` e solo per il progetto aperto, in rosso come «Re-index failed: {{message}}» (`embedding-section.tsx:89-97, 461-465`; `en.json:667`). `handleReindex` cattura e scarta l'errore (121-134): nessun toast né dialogo nei file letti. Nessun avanzamento durante le scritture (707-723). Il conteggio «chunks indexed» ritorna 0 sia per tabella vuota o assente sia per errore (`embedding.ts:864-870`). L'avviso «Legacy per-page index detected» compare con tabella legacy presente e chunk 0 o `null` (`embedding-section.tsx:170-171`): è l'unico indizio che non dipende dallo stato in memoria. Deduzioni non testate: errore al passo 6 lascia `running` e il pulsante disabilitato (433); dopo un riavvio lo stato `error` non esiste più e l'utente vede solo il numero di chunk. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r6.md §4. Messaggio all'utente e segnalazione nell'interfaccia (AC3, AC5)]

### Il rilancio riparte da zero? (osservato)
**Sì:** il rilancio con `clearExisting` rifà tutto il passo 3 (lettura, chunking, chiamate al provider per tutte le pagine, `embedding.ts:637-675`), senza consultare righe né revisioni, poi rifà `drop_table` e riscrive tutto. Nessun checkpoint, indice di avanzamento o elenco delle pagine mancanti. Una tabella parziale **non blocca** il rilancio (le salvaguardie 695-703 guardano le pagine pronte, non lo stato parziale). **Che cosa impedirebbe il recupero completo** (se deterministico, si ripresenta a ogni rilancio): (1) pagina con `page_id` rifiutato (`vectorstore.rs:78-114`), serve rinominare il file; (2) dimensione dei vettori incoerente nella pagina (`vectorstore.rs:410-418`); (3) errori di database o disco: non conclusivo; (4) chiusura o crash dopo lo svuotamento: nessun rollback né ripresa, stato su disco non conclusivo; (5) concorrenza: nessun lock copre la sequenza 705-723, ogni comando prende da sé il lock (`vectorstore.rs:52-60, 489, 763`); deduzione non testata: un `embedPage` di ingest durante la ricostruzione potrebbe essere sovrascritto da righe preparate prima. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r6.md §5. Il rilancio riparte da zero? Che cosa impedirebbe il recupero completo? (AC4)]

### Ricerca con tabella assente, vuota o parziale (osservato)
Percorso reale: `searchWiki` → comando `search_project` (`search.ts:62-83`; `search.rs:107-129, 294-315, 327-495`). Tabella v2 assente: `vector_search_chunks` ritorna `Ok(vec![])` (`vectorstore.rs:608-610`); vuota: nessun risultato vettoriale (`search.rs:807-815`); nessun risultato vettoriale: niente fusione RRF, modalità `keyword` (`search.rs:464-472`); errore vettoriale: `eprintln` e ripiego sulle parole chiave (`search.rs:455-459`); errore nell'embedding della query: ripiego (308-314); tabella **parziale**: compaiono solo le pagine già scritte, fuse con le parole chiave, **nessun segnale**. Il lato TS `searchByEmbedding` ritorna `[]` in tutti i casi (`embedding.ts:791-804`). Nessuna delle due ricerche legge la tabella legacy v1. Il campo `mode`/`vector_hits` esiste (`search.rs:54-60`) ma il TS non lo usa (`search.ts:20-28, 79-82`); `search-view.tsx` non letto. Deduzione non testata: la ricerca può vedere indice vuoto o parziale mentre la ricostruzione è in corso e riuscirà. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r6.md §6. Ricerca con tabella assente o vuota (AC5)]

### Esito proposto dal dossier
**CONFERMATO per lettura** sul meccanismo e sull'ipotesi della wiki (dopo lo svuotamento un errore di scrittura lascia tabella assente o parziale, nessun rollback, rilancio da zero, messaggio «may be incomplete»); **NON CONCLUSIVO** sul contenuto effettivo della tabella dopo errore parziale e sullo stato dopo un'uscita brusca. Precisazioni rispetto alla wiki: (a) le salvaguardie sono più ampie dell'elenco ma con pagine fallite scrivono comunque le riuscite sull'indice esistente; (b) una causa di errore post-svuotamento è prevedibile e non controllata prima, la validità del `page_id`; (c) l'errore è segnalato solo in Settings → Embedding, con stato in memoria, senza dire quante pagine mancano. **Impatto sull'utente (deduzione non testata):** ricerca semantica assente o parziale con ripiego silenzioso sulle parole chiave; nessuna perdita di pagine wiki né di sorgenti (indice derivato, ricostruibile col re-index); costo del rilancio: tutte le chiamate al provider. Gravità proposta: media se l'errore è deterministico, bassa se transitorio; decisione sulla salvaguardia a US-033. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r6.md §7. Esito proposto e tabella evidenze]

### Ricerca testuale globale (sessione principale, estende i negativi del dossier)
Eseguita su `src`, `src-tauri/src`, `mcp-server`, `extension` (esclusi i test), riportata in TSK-020 §Chiusura (il comando è lì; qui se ne citano solo gli esiti):
- **Un solo innesco del rebuild distruttivo:** `embedAllPages(` ha un solo chiamante, `embedding-section.tsx:124`, sempre con `{ clearExisting: true }` (`:128`), cioè Settings → Embedding. Nessun percorso di re-index da API, MCP o Rust: chiude la riserva del dossier sulla seconda via.
- **Svuotamento solo da quel flusso:** `clearChunkVectorTable` è chiamata solo da `embedding.ts:631` e `:705`; il comando Rust `vector_clear_chunks` (`vectorstore.rs:760`, `drop_table` a `:780`) è registrato in `lib.rs:680` e invocato solo dal wrapper `embedding.ts:281-282`.
- **Nessun backup, rollback o ripresa dell'indice in tutto il codice TS/Rust:** le occorrenze di `backup|rollback|.bak|snapshot|restore|checkpoint|resume` nei file che citano `lancedb`, `embedding` o `vector` riguardano altro (rollback di `source-lifecycle.ts:221, 228`; checkpoint di ripresa dell'ingest LLM `ingest.ts:1148-1191`; ripristino delle code `App.tsx:491-505`; commenti in `settings-view.tsx:467`, `App.tsx:331`, `project-file-sync.ts:302`, `wiki-page-delete.ts:194`). Il negativo del dossier, limitato ai file letti, vale per tutto il codice.
- **La tabella v1 non è usata come ripristino:** `TABLE_V1` (`wiki_vectors`) compare solo nei comandi v1 di `vectorstore.rs` (175-298) e in `vector_drop_legacy` (`:908`).

Restano non coperti dalla ricerca: `search-view.tsx`, i test (`embedding.test.ts`, `tests_v2`) e il comportamento di LanceDB. [^src: management/kanban/EP-004-verifica-rischi-di-persistenza/US-030-rischio-reindex-senza-rollback/TSK-020.md §Chiusura]

### File letti e non letti
Letti (6, sola lettura): `src/lib/embedding.ts` (1-225, 264-871), `src-tauri/src/commands/vectorstore.rs` (1-155, 205-948), `src-tauri/src/commands/search.rs` (1-560, 640-900), `embedding-section.tsx` (intero), `src/lib/search.ts` (intero), `src/i18n/en.json` (righe scelte). Non letti: sorgente di `lancedb`; `search-view.tsx`; `embedding.test.ts`; `it.json`, `ru.json`, `zh.json`; `embedding.ts` 226-263 (già in r5). [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r6.md §File letti e non letti]

### Controllo del repo e dei segreti dichiarato
L'agente non ha eseguito `git status` né `git log`: il controllo a comando è in TSK-020 §Chiusura (`git -C code_repos/llm_wiki log -1 --format=%h` → `e08cfce`, `status --short` → vuoto; `grep -ciE` sui pattern dei segreti sul dossier → 0). Il dossier ha letto solo nomi di campo e testi segnaposto dell'interfaccia, nessun valore, nessun file `.env*` né `app-state.json`. Nessuna istruzione rivolta a un agente trovata nei file letti. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r6.md §Note di estrazione] [^src: management/kanban/EP-004-verifica-rischi-di-persistenza/US-030-rischio-reindex-senza-rollback/TSK-020.md §Chiusura]

## Pagine collegate
[[llm-wiki-rischi-persistenza]] (§Esito della verifica di US-030), [[llm-wiki-operazioni-distruttive]], [[llm-wiki-versioni-e-migrazioni]], [[2026-11-21-repo-llm_wiki-dossier-ep004-r5]], [[gaps]].

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

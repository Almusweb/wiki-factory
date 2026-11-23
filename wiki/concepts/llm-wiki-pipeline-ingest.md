---
id: llm-wiki-pipeline-ingest
type: concept
title: llm-wiki — pipeline di ingest, coda e cache
status: draft
created: 2026-11-21
updated: 2026-11-23
sources: ["raw/2026-11-21-repo-llm_wiki-ingest.md", "raw/2026-11-21-issues-llm_wiki-chiuse.md", "raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md", "raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md"]
tags: [llm-wiki, ingest, pipeline, coda, cache]
---

# llm-wiki — pipeline di ingest, coda e cache
> L'ingest di una sorgente è a due stadi (analisi, generazione) con review facoltativa, cache per hash, coda persistente con 3 tentativi e checkpoint di ripresa; le scritture sono confinate a `wiki/` e un'ingest parziale non è un successo.

## Contesto
Pagina ricavata dalla fetta C2 del giro del 2026-11-21 ([[2026-11-21-repo-llm_wiki-ingest]]), che ha letto `ingest.ts` per intero (1-3940) e `ingest-queue.ts`, `ingest-cache.ts`, `sweep-reviews.ts`, `source-lifecycle.ts`, `wiki-page-delete.ts` e altri 20 file su 476. La README descrive l'ingest in due passi come funzione dichiarata ([[llm-wiki-app]]): qui è confermato dal codice. I moduli non letti sono elencati in fondo. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Gap evidenti]

## Dettaglio

### Flusso di `autoIngest`
Blocco per sorgente; PDF verso MinerU con ripiego su pdfium; lettura di sorgente, `schema.md`, `purpose.md`, indice e overview; copia opzionale in `raw/parsed`; controllo cache per hash (la cascata immagini gira comunque); estrazione immagini e didascalie; Stadio 1 di analisi a temperatura 0.1; Stadio 2 di generazione di blocchi `---FILE:---` e `---REVIEW:---`; review facoltativa; scrittura sotto commit coordinato. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Pipeline di ingest (`autoIngest`)]

- Lo stadio di review parte se la generazione supera 10.000 caratteri, ha almeno 4 blocchi `FILE` o contiene già blocchi `REVIEW`. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Pipeline di ingest (`autoIngest`)]
- Un'ingest parziale lancia errore, salva un checkpoint e non scrive cache né review; solo se completa avvengono le review nello store, `saveIngestCache`, la pulizia dei checkpoint e l'embedding delle pagine scritte (esclusi index, log, overview). [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Pipeline di ingest (`autoIngest`)]
- Un'ingest annullata conserva i file già scritti, perché potrebbero essere merge su pagine esistenti; `cleanupWrittenFiles` esiste ma i chiamanti non sono stati trovati nei file letti. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Cancellazione, lato TypeScript (gap 34)]

### Scritture e guardie di percorso
- I percorsi dei blocchi `FILE` sono ammessi solo sotto `wiki/`: niente `..`, percorsi assoluti o con lettera di unità, caratteri o nomi riservati di Windows, caratteri di controllo. Il commento dichiara la minaccia di un sorgente ostile che spinge il modello a emettere percorsi fuori da `wiki/`. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Pipeline di ingest (`autoIngest`)]
- I blocchi del modello per `wiki/index.md` e `wiki/overview.md` sono ignorati con avviso; `wiki/log.md` è accodato; le altre pagine passano da un merge con la pagina esistente, salvo le pagine con un solo sorgente, che vengono sostituite. Tra le pagine sorgente è ammessa solo `wiki/sources/<slug>.md` del sorgente corrente. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Pipeline di ingest (`autoIngest`)]
- Formati di `log.md`, `index.md` e `overview.md` mantenuti dall'app: [[llm-wiki-schema-dati]].

### Cache di ingest
`.llm-wiki/ingest-cache.json`: voci per `sourceIdentity` con hash sha256, timestamp e `filesWritten[]`; un colpo di cache vale solo se tutti i file di `filesWritten` esistono ancora. Cartelle e file collegati (checkpoint, `page-history/`, `ingest-warnings.log`, cache delle didascalie): [[llm-wiki-archivi-persistenza]]. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Pipeline di ingest (`autoIngest`)]

### Coda
`.llm-wiki/ingest-queue.json` con `IngestTask {id, projectId, sourcePath, folderContext, status, addedAt, error, retryCount}`; stati `pending`, `processing`, `done`, `failed`, `cancelled`; massimo 3 tentativi; pausa automatica di 15 minuti su limite di utilizzo del provider; a coda svuotata parte `sweepResolvedReviews`. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Pipeline di ingest (`autoIngest`)]

### Requisiti confermati dal codice sull'ingest
Ingest a due stadi con review facoltativa, analisi a blocchi per sorgenti lunghe con ripresa, cache per hash, merge di pagine, guardia di percorso, controllo di lingua per pagina, coda persistente con 3 tentativi, pulizia delle review risolte in due fasi (regole poi giudizio LLM, massimo 5 batch da 40), dedup e lint, importazione, rinomina e cancellazione dei sorgenti. Chat, ricerca, deep research, agente e API non sono coperti da questa fetta (gap `llm-wiki-requisiti-funzionali`, resta aperto in parte). [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Requisiti funzionali confermati sull'ingest (gap 11, parte)]

### Non letto
`page-merge.ts`, `extract-source-images.ts`, `ingest-sanitize.ts`, `ingest-commit-coordinator.ts`, `vision-caption.ts`, `embedding.ts`, `lint-config.ts`, `lint-store.ts`, `dedup.ts` oltre la riga 150, `dedup-queue.ts` oltre la riga 120, `mineru.ts` oltre la riga 700 e tutti i `*.test.ts`: la logica di merge, il commit coordinato e la sanificazione sono descritti solo per il comportamento visto in `ingest.ts`. Gap `llm-wiki-moduli-ingest-saltati`. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Gap evidenti]

## Pagine collegate
[[llm-wiki-app]], [[llm-wiki-schema-dati]], [[llm-wiki-archivi-persistenza]], [[llm-wiki-cancellazione-pagine-e-sorgenti]], [[llm-wiki-sicurezza]], [[2026-11-21-repo-llm_wiki-ingest]]. Gap aperti: [[gaps]] (`llm-wiki-moduli-ingest-saltati`, `llm-wiki-default-store-config`).

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

## Aggiornamenti (v2026-11-21, issue chiuse)
Dalla source page [[2026-11-21-issues-llm_wiki-chiuse]] (upstream v0.6.13, commit `e08cfce`, branch `develop` coincidente con `main`). Il testo sopra non è modificato.

- **Coda dopo il riavvio.** **Dichiarato (maintainer), #758, v0.6.12:** i task `pending` e `processing` persistiti riprendono al riavvio, con recupero degli eventi mancati del monitoraggio. È una dichiarazione, non un'osservazione. Precisazione dalla wiki: `restoreQueue` tiene solo i task con l'id di progetto corrente e riscrive il file senza gli scartati (vedi [[llm-wiki-rischi-persistenza]], rischio 2), quindi «riprendono» non vale per i task di un id diverso. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §6. Altre dichiarazioni pertinenti (non chiudono)]
- **Guardia dei percorsi nelle scritture dell'ingest.** **Osservato v0.6.13:** `executeIngestWrites` scarta i percorsi non sicuri o gestiti dall'app (`isSafeIngestPath`, `ingest.ts:3719, 3849-3851`); il punto 3 di #318 (scritture dell'ingest senza questo controllo), dichiarato nel 2026-06-01, risulta corretto. Riguarda le scritture, non la cancellazione di file. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §6. Altre dichiarazioni pertinenti (non chiudono)]

## Aggiornamenti (v2026-11-22, verifica sul codice)
Dalla source page [[2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki]]: lettura del codice di `e08cfce` (upstream v0.6.13, `develop` coincide con `main`), non eseguita. Il testo sopra non è modificato.

- **Chiave della cache di ingest.** Le voci sono indicizzate per nome o identità della sorgente; l'hash è lo SHA-256 del solo `sourceContent`. `checkIngestCache` e `saveIngestCache` hanno come unici input il percorso del progetto, il nome della sorgente e il testo: **non entrano `schema.md`, `purpose.md` né il modello**. Un colpo di cache richiede anche che i file scritti esistano ancora (conferma §Cache di ingest, con la precisazione sulla chiave). **Deduzione dalla lettura, non testata:** un cambio di `schema.md`, `purpose.md` o del modello non invalida da solo la cache, quindi una sorgente invariata non verrebbe rielaborata; il raw non ha letto cosa passino i chiamanti come `sourceContent`. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: cache di ingest e review]
- **Quando l'ingest parte dal monitoraggio dei file.** Condizioni (`enabled && autoIngest`, task `created` o `modified` sotto `raw/sources/` con estensione ingeribile, LLM usabile nel ramo del progetto aperto, ramo dei progetti inattivi solo con «Watch all projects» attivo): [[llm-wiki-sincronizzazione-file]]. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: sincronizzazione file (Rust e UI)]
- **Pulizia delle review risolte (§Requisiti confermati, «due fasi»).** Letta nel dettaglio: fase 1 con regole (`missing-page`, `duplicate`), fase 2 con giudizio LLM a lotti da 40, massimo 5 lotti, arresto al primo lotto senza risolti, azioni `auto-resolved` e `llm-judged`. **La fase 2 non filtra per tipo:** la prudenza su contraddizioni, suggerimenti e conferme è solo nel testo del prompt. Il chiamante non è letto nel raw (la wiki ha già che parte a coda svuotata, §Coda). Dettaglio in [[llm-wiki-review-store-e-auto-save]]. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: cache di ingest e review]
- **Non conclusivo.** «Progresso solo in UI o in `.llm-wiki/ingest-queue.json`» (bozza di alm-wiki): `ingest-queue.ts` non è fra i file di questo raw, e la sintesi della bozza non dice cosa intenda per «progresso». Il confronto con §Coda e con i checkpoint di ripresa resta da fare con la bozza originale. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: cache di ingest e review]

## Aggiornamenti (v2026-11-23, TSK-030)
Dalla source page [[2026-11-23-repo-llm_wiki-rebuild-index-scrittori]]: upstream v0.6.13, commit `e08cfce`, branch `develop` coincidente con `main`; lettura del codice, non eseguita. Il testo sopra non è modificato. «Osservato» = letto nel sorgente; «dedotto» = mai eseguito.

- **Ingest da conversazione (osservato).** La funzione si chiama `executeIngestWrites` (`ingest.ts:3719-3729`): prende il blocco per progetto (`withProjectLock`) e delega a `executeIngestWritesImpl` (3731-3940). Il chiamante è `handleWriteToWiki` (`chat-panel.tsx:1409-1418`, chiamata a riga 1413). Il pulsante compare solo con `mode === "ingest"`, senza streaming e con almeno una risposta dell'assistente. [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Funzione di ingest da conversazione (osservato)]
- **Momento e effetti sui file aggregati (osservato).** La funzione scrive dopo una seconda richiesta al modello: legge `schema.md` e `wiki/index.md`, costruisce cronologia e prompt di scrittura, fa lo streaming, analizza i blocchi `FILE` e scrive ogni pagina. `log.md` è accodato solo se il modello emette un blocco `FILE` per `log.md`. `index.md` e `overview.md` non sono scritti: il blocco è scartato da `isAppManagedAggregatePath`. In 3731-3940 non c'è alcuna chiamata a `updateWikiIndexDeterministically`. Conferma e precisa la voce «Guardia dei percorsi» di §Aggiornamenti (v2026-11-21, issue chiuse). [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Funzione di ingest da conversazione (osservato)]
- **Secondo scrittore da conversazione (osservato).** `handleSave` di `SaveToWikiButton` (`chat-message.tsx:553-632`) scrive una pagina in `wiki/queries/`, inserisce una voce sotto `## Queries` di `index.md`, accoda una riga a `log.md` e poi lancia `autoIngest` sul file salvato: è un secondo ingresso nell'ingest, oltre alla coda. [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Funzione di ingest da conversazione (osservato)]
- **Indice e log scritti dall'ingest (osservato).** `updateWikiIndexDeterministically` ha un solo chiamante, `autoIngestImpl` (`ingest.ts:1388`): dato della sessione (`git grep` sul commit, 2 righe: definizione e chiamata). La voce deterministica di `log.md` di `autoIngestImpl` ha guardia a riga 1406 (solo se il modello non ha emesso il blocco) e scrittura a riga 1410. [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Controlli finali] [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Scrittori di `log.md`]
- **`writeFileBlocks` (osservato).** Accoda il blocco del modello a `log.md` (`ingest.ts:2241`). Per percorsi `…/index.md` diversi da `wiki/index.md` sovrascrive il file intero (`ingest.ts:2249`); `wiki/index.md` e `wiki/overview.md` sono scartati prima (`ingest.ts:2142-2147`). [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Scrittori di `index.md`]
- **Limite.** Il censimento degli scrittori vale per la stringa letterale `index.md` e `log.md`: `executeIngestWritesImpl` e `writeFileBlocks` scrivono qualunque percorso dei blocchi `FILE`, e un percorso costruito a runtime non è nelle 120 righe del raw. [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Ambito di ricerca dichiarato]

Formati di `index.md` e `log.md` e tabella degli scrittori: [[llm-wiki-schema-dati]] (le sezioni che chiudono i punti di US-035 sono aggiornate da un TSK successivo).

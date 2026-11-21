---
id: llm-wiki-pipeline-ingest
type: concept
title: llm-wiki — pipeline di ingest, coda e cache
status: draft
created: 2026-11-21
updated: 2026-11-21
sources: ["raw/2026-11-21-repo-llm_wiki-ingest.md"]
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

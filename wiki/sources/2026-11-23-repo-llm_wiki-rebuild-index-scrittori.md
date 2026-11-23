---
id: 2026-11-23-repo-llm_wiki-rebuild-index-scrittori
type: source
title: Specifiche estratte da code_repos/llm_wiki, estrazione 2026-11-23: indice ricostruito da rebuild_wiki_index e scrittori di index.md e log.md (repo-sync)
status: draft
created: 2026-11-23
updated: 2026-11-23
sources: ["raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md"]
tags: [source, repo, llm-wiki, persistenza, indice, log, scrittori]
---

# Specifiche estratte da code_repos/llm_wiki, estrazione 2026-11-23: indice ricostruito da rebuild_wiki_index e scrittori di index.md e log.md (repo-sync)
> Estrazione mirata `repo-sync` v2.12 del 2026-11-23, stato `success`. Linea: upstream v0.6.13, commit `e08cfce` (release v0.6.13), branch `develop`, che coincide con `main`. Lettura del codice, non eseguito. Distingue «osservato» (letto nel sorgente), «dedotto» (ricavato da fatti osservati, mai eseguito) e «non verificato» (non determinabile, con il motivo).

## Contesto
Sesta estrazione mirata sulla persistenza di `llm_wiki`, dopo le fette A, B, C e D ([[2026-11-20-repo-llm_wiki-persistenza-a]], [[2026-11-20-repo-llm_wiki-persistenza-b]], [[2026-11-20-repo-llm_wiki-persistenza-c]], [[2026-11-21-repo-llm_wiki-persistenza-d]]) e al giro del 2026-11-21 ([[2026-11-21-repo-llm_wiki-ingest]]). Serve US-035: dare un raw ingerito al formato dell'indice ricostruito e all'elenco degli scrittori di `index.md` e `log.md`. Il raw non ricopia i raw precedenti: verifica sul sorgente. Il repository è di terzi, sotto GNU GPL v3: il raw descrive il codice con parole proprie e cita solo nomi di file, simboli, campi e percorsi. Nessun frammento di codice. [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Identità e perimetro]

Limite dello strumento dichiarato dal raw: l'agente che ha letto non aveva `Bash` né `Grep` e ha aperto finestre di file con `Read`. Un «non visto» vale solo per le righe lette. I conteggi e i comandi di ricerca li ha eseguiti la sessione principale. [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Identità e perimetro]

Checkout letto (esiti eseguiti dalla sessione): commit `e08cfce`, branch `develop`, `git status --short` con output vuoto prima dell'estrazione. Con il working tree pulito i file letti coincidono con il commit. [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Checkout letto]

Controlli finali dichiarati dal raw: repo invariato dopo l'estrazione, commit invariato, scanner di segreti senza finding, 120 righe nella tabella delle occorrenze, 120 coppie `file:riga` senza differenze con l'elenco della sessione. [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Controlli finali]

## Dettaglio

### Indice prodotto da `rebuild_wiki_index` (osservato)
Il comando Tauri è in `project_maintenance.rs`, righe 287-292. La funzione che lavora è `rebuild_wiki_index_inner`, righe 294-355. [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Parte 1. `rebuild_wiki_index`]

- **Intestazione**: prima riga `# Wiki Index`, poi una riga vuota. Senza pagine il file contiene solo questa intestazione.
- **Sezioni**: una per ogni valore distinto del campo `type` del frontmatter, con intestazione `## <type>` e il valore copiato senza cambiare le maiuscole. Le sezioni sono in una mappa ordinata per stringa: ordine per byte, maiuscole prima delle minuscole.
- **Voce**: riga `- [[<percorso>|<titolo>]]`. Il percorso è relativo a `wiki/`, senza estensione, con `/` come separatore. Una riga vuota chiude ogni sezione.
- **Ordine nella sezione**: per titolo in minuscolo, con ordinamento stabile. A parità di titolo resta l'ordine di visita della directory (non verificato: il crate `walkdir` non è letto).
- **Pagine escluse**: le voci che non sono file; i file con estensione diversa da `md` (confronto esatto in minuscolo); i file con nome base `index`, `overview` o `log`, senza distinzione di maiuscole, in qualsiasi sottocartella di `wiki/`.
- **`type` mancante o vuoto**: la sezione è `other`. **`title` mancante**: il nome base del file senza estensione.
- **Scrittura**: file temporaneo `wiki/.index.md.rebuild.tmp`, sincronizzazione su disco, rinomina su `index.md`. Su Windows il vecchio file è cancellato prima della rinomina.
- **Vecchio indice**: mai aperto. Il file è costruito da zero con le sole pagine trovate.
- **Risultato**: una struttura con il numero di pagine e di gruppi.
- **Dedotto, non testato**: i link simbolici sono saltati, per `follow_links(false)` di `walkdir` (sorgente non letto). Il test `rebuilds_index_from_page_frontmatter` esiste ma non è stato eseguito.
- **Invocazione**: dato della sessione (`git grep` sul commit, ambito `src` e `src-tauri/src`): 6 righe, con una sola invocazione dall'interfaccia (`maintenance-section.tsx:201`) e la registrazione del comando in `lib.rs:655`.

[^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Parte 1. `rebuild_wiki_index`] [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Controlli finali]

### Sezioni di `create_project` e `## Recently Updated` dopo la ricostruzione (dedotto)
Esito di tutto il punto: **dedotto**. `cargo` e `rustc` non sono installati (dato della sessione): il test non è eseguibile e nessuna prova è stata eseguita. Nessuna esecuzione dell'app né build (Q_003). [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Parte 2. Sezioni di `create_project` e `## Recently Updated`]

| Sezione | Chi la scrive (osservato) | Dopo la ricostruzione (dedotto) |
|---|---|---|
| `# Wiki Index` | `create_project_impl` (`project.rs:155-169`) | ricreata con lo stesso testo: «conserva» |
| sei sezioni vuote (`## Entities`, `## Concepts`, `## Sources`, `## Queries`, `## Comparisons`, `## Synthesis`) | `create_project_impl` (`project.rs:157-167`) | sparisce: il nuovo file ha solo le sezioni `## <type>` dei valori trovati, con nomi diversi: «elimina» |
| `## Recently Updated` dell'indice | `updateBoundedRecentIndexSection` (`ingest.ts:1807-1821`), chiamata da `updateWikiIndexDeterministically` (`ingest.ts:1730`) | sparisce: «elimina» |

[^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Parte 2. Sezioni di `create_project` e `## Recently Updated`]

Note osservate: la stringa `## Recently Updated` compare anche per `overview.md`, tra due marcatori di commento. Quella sezione non riguarda l'indice. Dopo una ricostruzione l'ingest aggiunge di nuovo la sezione in fondo e non duplica le voci, perché legge quelle già presenti con un criterio che accetta `[[target|titolo]]`. [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Parte 2. Sezioni di `create_project` e `## Recently Updated`]

### Occorrenze di `index.md` e `log.md`: ambito e classi (osservato)
- **Ambito**: `src/`, `src-tauri/src/`, `mcp-server/src/`, `extension/`, `scripts/`. File `*.ts` e `*.tsx` in `src/`, `*.rs` in `src-tauri/src/`, tutti i file delle altre tre cartelle. Esclusi test TypeScript, stringhe UI in `src/i18n/*.json` e documenti `*.md` (103 righe). Inclusi i moduli di test Rust in linea. [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Ambito di ricerca dichiarato]
- **Criterio**: stringa fissa, sensibile alle maiuscole, come sottostringa. Unità di conteggio: la riga. [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Ambito di ricerca dichiarato]
- **Esito**: 120 righe trovate (`index.md` 95, `log.md` 37, 12 con entrambi), 120 classificate, in 31 file. [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Totali per classe]
- **Limite**: un percorso costruito a runtime (per esempio il nome di un blocco `FILE` del modello) non contiene la stringa e non è trovato. **La completezza dell'elenco vale solo rispetto al criterio letterale.** Le chiamate di scrittura usano variabili e non compaiono tra le 120 righe: i loro siti sono nei due elenchi sotto. [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Ambito di ricerca dichiarato]
- **Classi**: scrittura (la riga è una chiamata di scrittura o compone il suo argomento), lettura, altro. [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Classi]

| Classe | Righe | Sottotipi |
|---|---|---|
| scrittura | 22 | scrittura diretta 2; preparazione del percorso 12; annuncio dopo la scrittura 4; guardia di ramo 4 |
| lettura | 9 | contesto di prompt 5; verifica di presenza 3; lettura da insieme in memoria 1 |
| altro | 89 | test in linea 25; commento 23; filtro 16; messaggio di errore 8; testo di prompt 5; testo di schema 3; costante di testo 3; etichetta UI 2; voce di changelog 2; costante 1; descrizione di schema 1 |

[^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Totali per classe]

Le 22 righe di scrittura, per file (numeri di riga del raw): `project.rs` 169 e 180; `project_maintenance.rs` 339 e 340; `chat-message.tsx` 580 e 603; `review-view.tsx` 136, 149, 271 e 287; `dedup-runner.ts` 473; `ingest.ts` 1389, 1390, 1406, 1408, 1411, 1412 e 1711; `source-lifecycle.ts` 642 e 698; `wiki-page-delete.ts` 244 e 256. Le 9 righe di lettura: `claude_cli.rs` 496, `codex_cli.rs` 358, `project_maintenance.rs` 233, `dedup-runner.ts` 474, `deep-research.ts` 579, `enrich-wikilinks.ts` 35, `ingest.ts` 783, 3665 e 3752. La tabella completa con sottotipo e funzione contenitore resta nel raw e non si copia qui. [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Tabella delle 120 occorrenze]

### `rewriteIndexMd` (osservato, con un punto dedotto)
Funzione `dedup.ts:534-546`, aiuto `lineRefersToSlug` a `dedup.ts:548-558`. [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Parte 4. `rewriteIndexMd`]
- **Cosa fa**: toglie intere righe. Non riscrive voci e non fonde duplicati. Con insieme di slug vuoto ritorna il contenuto senza modifiche.
- **Una riga è tolta se**: contiene un wikilink il cui bersaglio coincide con lo slug (con o senza alias), oppure un link Markdown che termina con `<slug>.md`, oppure `<slug>.md` come parola intera.
- **Quando scrive**: al passo 6 di `executeMerge` (`dedup-runner.ts:472-483`), dopo la scrittura della pagina canonica, le riscritture dei riferimenti e la cancellazione delle pagine assorbite. La scrittura è a riga 481, solo se `wiki/index.md` è nell'insieme di pagine caricato (riga 404) e il testo riscritto è diverso dall'originale. Gli slug tolti sono quelli del gruppo meno lo slug canonico. Chiamante: `processNext` della coda (`dedup-queue.ts:369`).
- **Dedotto, non testato**: lo slug è il nome base senza estensione. Una voce con prefisso di cartella (`[[entities/a|Alpha]]` di `rebuild_wiki_index`, `[[entities/a]]` dell'ingest) non corrisponde alla regola 1 e, senza `.md`, nemmeno alle regole 2 e 3. Il test `dedup.test.ts` non è letto.
- **Non verificato**: un commento dichiara che l'interfaccia mostra un diff prima di scrivere, ma in `executeMerge` (394-486) non c'è alcuna conferma. Non è visto un blocco di progetto (`withProjectLock`).

[^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Parte 4. `rewriteIndexMd`]

### Ingest da conversazione e riga 642 di `source-lifecycle.ts` (osservato)
- **Funzione di ingest da conversazione**: `executeIngestWrites` (`ingest.ts:3719-3729`), con blocco per progetto, che delega a `executeIngestWritesImpl` (3731-3940). Chiamante `handleWriteToWiki` (`chat-panel.tsx:1409-1418`, chiamata a riga 1413). Il pulsante compare solo con `mode === "ingest"`, senza streaming e con almeno una risposta dell'assistente. Scrive dopo una seconda richiesta al modello. `log.md` è accodato solo se il modello emette un blocco `FILE` per `log.md`. `index.md` e `overview.md` non sono scritti: il blocco è scartato da `isAppManagedAggregatePath`. In 3731-3940 non c'è alcuna chiamata a `updateWikiIndexDeterministically`. [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Funzione di ingest da conversazione (osservato)]
- **Scrittore da conversazione distinto**: `handleSave` di `SaveToWikiButton` (`chat-message.tsx:553-632`). Scrive una pagina in `wiki/queries/`, inserisce una voce sotto `## Queries` (o aggiunge la sezione in fondo), accoda una riga a `log.md` e poi lancia `autoIngest` sul file salvato. [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Funzione di ingest da conversazione (osservato)]
- **`source-lifecycle.ts` riga 642**: classe **scrittura**, sottotipo «guardia di ramo», dentro `cleanupDeletedWikiPages` (606-663). La riga sceglie quando applicare `cleanIndexListing` al testo letto e vale per `wiki/index.md` e per qualsiasi file chiamato `index.md`. La scrittura è a riga 657, se il testo è cambiato (riga 655). Chiamante: `cleanupDeletedFiles` (`project-file-sync.ts:419`). [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §`src/lib/source-lifecycle.ts` riga 642 (osservato)]

### Scrittori associati e `cleanIndexListing` (osservato)
Il raw elenca i siti di scrittura fuori dal conteggio delle 120 righe, valido per le finestre lette e per il criterio letterale.

**Scrittori di `index.md` (nove funzioni).** `create_project_impl` (crea il file con intestazione e sei sezioni vuote); `rebuild_wiki_index_inner` (sostituisce il file intero); `updateWikiIndexDeterministically`, chiamata da `autoIngestImpl` (aggiunge `- [[target]] — titolo` sotto `## Recently Updated`, massimo 200 voci); `handleSave` di `SaveToWikiButton` (voce sotto `## Queries`); `handleResolve` della review (stessa logica, a riga 284 l'intestazione deriva dal nome della cartella con la prima lettera maiuscola); `executeMerge` tramite `rewriteIndexMd` (toglie righe); `cleanupDeletedWikiPages` e `cascadeDeleteWikiPagesWithRefs` tramite `cleanIndexListing` (tolgono voci); `writeFileBlocks` per percorsi `…/index.md` diversi da `wiki/index.md` (sovrascrive il file intero, `ingest.ts:2249`; `wiki/index.md` e `wiki/overview.md` sono scartati prima, `ingest.ts:2142-2147`). [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Scrittori di `index.md`]

**Scrittori di `log.md` (sette funzioni).** `create_project_impl` (crea `# Research Log` con una voce di creazione); `writeFileBlocks` (accoda il blocco del modello); `autoIngestImpl` (accoda una voce deterministica, solo se il modello non ha emesso il blocco, guardia a riga 1406, scrittura a riga 1410); `executeIngestWritesImpl` (accoda il blocco del modello, riga 3872); `handleSave` di `SaveToWikiButton` (accoda una riga, `chat-message.tsx:611`); `handleResolve` della review (accoda una riga, `review-view.tsx:152` e `:292`); `appendSourceDeleteLog` (accoda una voce alla cancellazione di una sorgente, `source-lifecycle.ts:704`). [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Scrittori di `log.md`]

**`cleanIndexListing`** (`wiki-cleanup.ts:98-108`, letta per intero). Toglie le righe di elenco (iniziano con `-` o `*`) il cui **primo** wikilink ha una chiave uguale a quella di una pagina cancellata. La chiave è l'ultimo segmento del percorso, in minuscolo, senza `.md`, senza spazi, trattini e underscore; per ogni pagina cancellata il set contiene la chiave dello slug e quella del titolo. Le voci con prefisso di cartella corrispondono. Dedotto, non testato: due pagine in cartelle diverse con lo stesso nome base hanno la stessa chiave, e una cancellazione toglie entrambe le voci. Un bersaglio con `#` è confrontato così com'è. [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Effetto di `cleanIndexListing` (osservato)]

### Punti «non verificato» rimasti
Sette punti restano aperti nel raw: la prova eseguita del punto «sezioni sparite» (resta dedotto); l'ordine delle pagine con titolo uguale; i link simbolici saltati; il diff mostrato prima della riscrittura di `rewriteIndexMd`; l'effetto di `rewriteIndexMd` sui formati con prefisso di cartella; il blocco di progetto in `executeMerge`; i percorsi costruiti a runtime. Altri due punti (altri chiamanti di `updateWikiIndexDeterministically`, invocazioni di `rebuild_wiki_index` dall'interfaccia) sono chiusi dalla sessione con `git grep`: un solo chiamante e una sola invocazione. [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Punti «non verificato» rimasti]

## Pagine ricavate o aggiornate
Aggiornate: [[llm-wiki-schema-dati]] (solo frontmatter e `## Contradictions`), [[llm-wiki-operazioni-distruttive]], [[llm-wiki-cancellazione-pagine-e-sorgenti]], [[llm-wiki-pipeline-ingest]]. Le sezioni di [[llm-wiki-schema-dati]] che chiudono i punti di US-035 sono riscritte da un TSK successivo, non da questo ingest.

## Gap di questa fetta
Nessuna chiusura. Aperti due gap non bloccanti: `llm-wiki-index-rewrite-prefisso-cartella` (formati con prefisso di cartella e `rewriteIndexMd`, dedotto) e `llm-wiki-merge-diff-e-blocco-non-visti` (diff prima della riscrittura e blocco di progetto in `executeMerge`). Il residuo `rebuild_wiki_index` del gap `llm-wiki-log-index-formato` non è chiuso qui. Dettagli in [[gaps]]. [^src: raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md §Punti «non verificato» rimasti]

## Estratto non promosso a pagina
La tabella completa delle 120 occorrenze (sottotipo e funzione contenitore per riga), l'elenco dei 33 file aperti con gli intervalli di riga e i confini dei moduli di test Rust restano nel raw e non sono ricopiati. Nessuna istruzione rivolta a un agente è stata trovata nel raw. Nessun valore segreto.

## Pagine collegate
[[2026-11-20-repo-llm_wiki]], [[2026-11-20-repo-llm_wiki-persistenza-b]], [[2026-11-21-repo-llm_wiki-ingest]], [[llm-wiki-schema-dati]], [[llm-wiki-operazioni-distruttive]], [[llm-wiki-cancellazione-pagine-e-sorgenti]], [[llm-wiki-pipeline-ingest]], [[gaps]]

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

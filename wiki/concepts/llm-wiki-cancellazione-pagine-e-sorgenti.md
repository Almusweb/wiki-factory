---
id: llm-wiki-cancellazione-pagine-e-sorgenti
type: concept
title: llm-wiki — cascata di cancellazione di una pagina e ciclo di vita delle sorgenti
status: draft
created: 2026-11-20
updated: 2026-11-21
sources: ["raw/2026-11-20-repo-llm_wiki-persistenza-c.md", "raw/2026-11-21-repo-llm_wiki-ingest.md", "raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md"]
tags: [llm-wiki, dati, persistenza, db]
---

# llm-wiki — cascata di cancellazione di una pagina e ciclo di vita delle sorgenti
> Ordine dei passi, chiamanti e archivi toccati dalla cascata di cancellazione di una pagina (`wiki-page-delete.ts`) e dal ciclo di vita delle sorgenti (`source-lifecycle.ts`): cancellazione, spostamento, voce di log.

## Contesto
Pagina ricavata dalla fetta C dell'estrazione mirata sulla persistenza (commit `e08cfce`). I due flussi hanno un ordine di passi, chiamanti con diverso innesco, archivi toccati e non toccati, e divergenze tra commenti e codice: non entrano in una riga di [[llm-wiki-operazioni-distruttive]], che ne tiene solo il rimando. Qualificatori del raw: «letto» (osservato in una finestra), «deduzione», «non verificato», «solo mappa (graphify/grep)»; quest'ultima è una riga della mappa della sessione, non riletta nel sorgente e non fonte normativa. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Identità e perimetro]

## Dettaglio

### Chiamanti della cascata
Il modulo `wiki-page-delete` è importato da quattro file (import da mappa grep). `knowledge-tree.tsx:128` chiama la variante con riferimenti (il primo clic arma la riga, il secondo esegue). `lint-view.tsx:343-346` la usa per eliminare una pagina orfana segnalata dal lint; la finestra letta inizia a metà funzione e una eventuale conferma non è visibile. `source-lifecycle.ts:560-561` la usa in `deleteSourceFiles` per le pagine rimaste senza sorgenti. `ingest-queue.ts:277,284` la chiama solo dentro `cleanupWrittenFiles`, che non ha chiamanti nell'ambito cercato. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Cascata di cancellazione di una pagina]

`ingest.ts:3556` cita la cascata in un commento, non la chiama: il commento dichiara che, senza la pagina di riepilogo della sorgente, lo sweep delle pagine orfane del lint potrebbe eliminare la cartella dei media (perdita silenziosa di immagini). È un rischio dichiarato dagli autori, non verificato. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Cascata di cancellazione di una pagina]

### Ordine dei passi
`cascadeDeleteWikiPage`: (1) file della pagina con `delete_file`, un errore si propaga e ferma il resto; (2) righe LanceDB v2 con quel `page_id` e riga con id legacy se applicabile, errori ingoiati da `removePageEmbedding`; (3) solo se il percorso contiene `/wiki/sources/` e lo slug non è vuoto né inizia con un punto, cartella `wiki/media/<slug>`, ricorsiva, errore ingoiato. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Cascata di cancellazione di una pagina]

`cascadeDeleteWikiPagesWithRefs`: legge ogni pagina per il titolo; esegue la cascata per pagina (un errore è solo loggato e la pagina non entra tra le cancellate); con slug, elenca l'albero `wiki/` e per ogni pagina rimasta ripulisce `wiki/index.md`, trasforma i wikilink in testo (alias mantenuto) e toglie le voci di `related`, riscrivendo solo se il testo cambia; infine `pruneDeletedPagesFromReviews` riscrive `review.json` togliendo le pagine da `affectedPages` ed eliminando le review rimaste senza pagine. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Cascata di cancellazione di una pagina]

### Archivi toccati e non toccati
Toccati: pagina `.md` e media, LanceDB v2, pagine rimaste e `wiki/index.md`, `review.json`. Non toccati dal codice letto: `ingest-cache.json`, `lint.json`, `dedup-queue.json`, `dedup-not-duplicates.json`, `ingest-queue.json`, `page-history/`, `wiki/log.md`. Se `vector_delete_page` tolga anche `embedding-revisions/<sha256>.revision` non è verificato (lato Rust non letto). [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Cascata di cancellazione di una pagina]

### Osservazioni sulla cascata
Il commento in testa a `wiki-page-delete.ts` dice «errori propagati, non ingoiati»; il codice li propaga solo per il file della pagina. Lo stesso commento cita tra gli utilizzatori la pulizia di ingest annullato in `ingest-queue`, uso che il codice cercato non mostra. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Cascata di cancellazione di una pagina]

Deduzione: `listDirectory` a `:242` non è in try, quindi se fallisce dopo la cancellazione lo sweep e il prune delle review non partono. Il controllo «pagina di sorgente» cerca `/wiki/sources/`, mentre `source-lifecycle.ts:620` accetta anche `wiki/sources/` relativo: un percorso relativo passato alla cascata non attiverebbe la cancellazione dei media (`normalizePath` non è nella finestra). [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Cascata di cancellazione di una pagina]

### Ciclo di vita delle sorgenti: `deleteSourceFiles`
Cinque passi. (1) File sorgente, non in try: un errore interrompe il batch (il commento di `sources-view.tsx:330-332` dice che prosegue). (2) Per ogni sorgente `removeParsedMarkdown`, cache `raw/sources/.cache/<nome>.txt` e `.txt.parser`, voce di `ingest-cache` per le chiavi identità e nome file, errori ignorati. (3) Scansione di tutte le pagine wiki: quelle con `sources:` ancora non vuoto sono riscritte, quelle rimaste senza sorgenti sono cancellate (qualsiasi pagina, non solo il riepilogo, senza distinguere pagine modificate a mano; pagine senza `sources:` leggibile sono saltate). (4) Cascata con riferimenti. (5) Voce in `wiki/log.md`, con rilettura e riscrittura dell'intero file. Il confronto usa `sourceNameMatchesAny`, non letta. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Ciclo di vita delle sorgenti]

### Voce di log di cancellazione
`appendSourceDeleteLog` scrive data, motivo (`delete`, `external delete`, `folder delete`, `external folder delete`), nome o numero di sorgenti e una frase con pagine cancellate e pagine condivise tenute; con più sorgenti segue un elenco. Se la lettura fallisce ripiega su un'intestazione. Deduzione: se la lettura fallisce per un motivo diverso dall'assenza del file, la riscrittura sostituisce il contenuto del log. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Ciclo di vita delle sorgenti]

### Cartelle e `.cache`
`deleteSourceFolder` raccoglie tutti i file della cartella (anche con punto), chiama `deleteSourceFiles` ed elimina la cartella in modo ricorsivo; l'errore sulla cartella è solo loggato. La `.cache` cancellata al passo 2 è quella alla radice di `raw/sources`: per un file in sottocartella la cache accanto al file non è cancellata da questo codice (deduzione, valida per il singolo file; la cartella intera sparisce con `deleteSourceFolder`). [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Ciclo di vita delle sorgenti]

### Chiamanti del ciclo di vita
UI: `sources-view.tsx:300` (file) e `:338` (cartella), con conferma a due fasi nel componente dell'albero. Solo mappa: `scheduled-import.ts:345` e `project-file-sync.ts:402` (cancellazione esterna rilevata dal watcher, vedi [[llm-wiki-sincronizzazione-file]]). `migrateSourcePath` (`source-lifecycle.ts:137-233`) è chiamata dagli spostamenti rilevati dal watcher. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Ciclo di vita delle sorgenti]

`cleanupDeletedWikiPages` (`source-lifecycle.ts:629-662`) duplica la logica di sweep, non pota le review ed è usata quando una pagina è già sparita da disco (chiamante `cleanupDeletedFiles`, `project-file-sync.ts:419`, solo mappa). [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Cascata di cancellazione di una pagina]

## Pagine collegate
[[llm-wiki-operazioni-distruttive]], [[llm-wiki-archivi-persistenza]], [[llm-wiki-rischi-persistenza]], [[llm-wiki-sincronizzazione-file]], [[2026-11-20-repo-llm_wiki-persistenza-c]]. Gap aperti: [[gaps]] (`llm-wiki-persistenza-codice-non-letto`, `llm-wiki-log-index-formato`, `llm-wiki-cancellazione-controlli-confine`, `llm-wiki-cancellazione-file-orfani`).

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

## Aggiornamenti (v2026-11-21)
Dalle fette C2 ed E del giro del 2026-11-21 ([[2026-11-21-repo-llm_wiki-ingest]], [[2026-11-21-repo-llm_wiki-ricerca-ui-residui]], commit `e08cfce`). Il testo sopra non è modificato; dove è superato lo dice `## Contradictions` in coda. Il gap `llm-wiki-cancellazione-controlli-confine` resta aperto in parte, `llm-wiki-cancellazione-file-orfani` resta aperto per le sessioni agente. Le conseguenze combinate delle azioni `delete:` restano un'**ipotesi non riprodotta** ([[llm-wiki-rischi-persistenza]]).

### Chi genera ed esegue `delete:<percorso>` (fetta C2)
- Le azioni `delete:<percorso>` sono generate da `lint-view.tsx` per le review di tipo `broken-link`, con `action = delete:${pp}/wiki/${item.page}` (percorso assoluto); le altre review del lint usano solo `open:` e `Skip`. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Cancellazione, lato TypeScript (gap 34)]
- Per le review generate dall'ingest, `parseReviewBlocks` costruisce ogni opzione con `action = label`, cioè il testo della riga `OPTIONS:` scritta dal modello, senza validazione; il prompt chiede solo `Create Page | Skip`, ma il parser accetterebbe un'etichetta qualsiasi. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Cancellazione, lato TypeScript (gap 34)]
- `review-view.tsx`, con `action.startsWith('delete:')`, fa `deleteFile(action.slice(7))`, aggiorna l'albero e risolve la review come «Deleted»: nessuna conferma, nessun controllo di confine, nessuna cascata (embedding, riferimenti). [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Cancellazione, lato TypeScript (gap 34)]
- La cancellazione di una pagina orfana da `lint-view` ha conferma `destructive` (`handleDeleteOrphan`) e poi chiama `cascadeDeleteWikiPagesWithRefs`. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Cancellazione, lato TypeScript (gap 34)] [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Cancellazione di revisioni e sessioni (gap cancellazione-file-orfani)]
- `delete_file` in Rust (confine del progetto) è fuori dalla fetta C2; è descritto in [[llm-wiki-operazioni-distruttive]] dalla fetta C1. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Cancellazione, lato TypeScript (gap 34)]

### Cascata e sorgenti, conferme dalla fetta C2
- `cascadeDeleteWikiPage` cancella il file, l'embedding e, per una pagina sorgente, `wiki/media/<slug>/` (guardia sullo slug vuoto o che inizia per `.`); `cascadeDeleteWikiPagesWithRefs` riscrive indice, wikilink e `related:` e pulisce le review (`affectedPages` assoluti o relativi a `wiki/`). [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Cancellazione, lato TypeScript (gap 34)]
- `deleteSourceFiles` toglie file, copia parsed, cache `.cache` e voce di `ingest-cache`; per ogni pagina che cita il sorgente riscrive `sources` oppure, se non resta alcun sorgente, cancella la pagina in cascata, poi accoda la voce di log; `removeParsedMarkdown` e `moveParsedMarkdown` sono chiamati da `deleteSourceFiles` e `migrateSourcePath`. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Percorsi del markdown estratto e delle immagini MinerU (gap 33)]
- Un'ingest annullata conserva i file già scritti, perché potrebbero essere merge su pagine esistenti; `cleanupWrittenFiles` non ha chiamanti trovati nei file letti. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Cancellazione, lato TypeScript (gap 34)]

### File di revisione e sessioni agente (fetta E)
- `vector_delete_page` esegue solo `table.delete` sul `page_id` e non cancella il file `.revision`; `vector_clear_chunks` fa solo `drop_table`. Il file di revisione è rimosso solo da `invalidate_page_revision` (scrittura senza revisione o `save_revision` fallito). Un `.revision` orfano non produce falsi «unchanged» perché la corrispondenza richiede almeno una riga per quel `page_id`. Nome: `.llm-wiki/embedding-revisions/<sha256(page_id) esadecimale minuscolo>.revision`. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Cancellazione di revisioni e sessioni (gap cancellazione-file-orfani)]
- In `session.rs` nessuna funzione cancella i file di sessione; limiti: troncamento a 40 messaggi e cache in memoria a 128 sessioni; i file restano su disco in `<progetto>/.llm-wiki/agent-sessions/<id>.json`. Non verificato (nessuna ricerca testuale): se UI, API, `runtime.rs` o `lib.rs` cancellino i file di sessione. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Cancellazione di revisioni e sessioni (gap cancellazione-file-orfani)]

## Contradictions
- **Conferma nella cancellazione di una pagina orfana e origine di `delete:`.** Prima (Chiamanti della cascata): `lint-view.tsx:343-346` usa la cascata per una pagina orfana e «una eventuale conferma non è visibile»; l'origine delle stringhe `delete:` non era nota. Ora (fetta C2 ed E): la conferma `destructive` è presente (`handleDeleteOrphan`); le azioni `delete:` hanno origine in `lint-view.tsx` (review `broken-link`) e, per le review da ingest, nell'etichetta `OPTIONS:` del modello senza validazione, ed `review-view.tsx` le esegue senza conferma. [^src: raw/2026-11-21-repo-llm_wiki-ingest.md §Cancellazione, lato TypeScript (gap 34)]
- **File `.revision` dopo `vector_delete_page`.** Prima (Archivi toccati e non toccati): se `vector_delete_page` tolga anche `embedding-revisions/<sha256>.revision` non è verificato (lato Rust non letto). Ora (fetta E): non lo toglie; l'orfano non causa falsi «unchanged». [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §Cancellazione di revisioni e sessioni (gap cancellazione-file-orfani)]

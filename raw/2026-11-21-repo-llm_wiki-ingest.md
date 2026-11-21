# Specifiche estratte: llm_wiki, ingest e pipeline (fetta C2)

> Documento generato da `repo-sync` v2.12 il 2026-11-21. Sorgente: /home/user/wiki-factory/code_repos/llm_wiki @ commit e08cfce65aad8b76b13546a081c1a8d4422b70c3 (ramo HEAD, detached). Read-only verso la sorgente. Estrazione mirata ai gap 9, 14, 18, 32, 33, 34 (lato TypeScript), e in parte 11 e 25. I percorsi citati sono relativi a `src/` salvo diversa indicazione.

## Identità
- **Nome**: llm_wiki, versione 0.6.13. Stack già rilevato in raw/2026-11-20-repo-llm_wiki.md: TypeScript/React (confidenza 0.7). Non rieseguito.
- **Ambito di questo documento**: pipeline di ingest, coda, cache, dedup, lint, ciclo di vita dei sorgenti, cascata di cancellazione.
- **File campionati**: 20 su 476 (vedi §Gap evidenti per gli intervalli).

## Pipeline di ingest (`autoIngest`)

Flusso per un sorgente, in ordine [^src: src/lib/ingest.ts:627-1597]:
1. Blocco per sorgente (`withProjectLock("ingest-source\0<progetto>\0<sorgente>")`) [^src: src/lib/ingest.ts:636-650].
2. PDF con MinerU abilitato e configurato: invio a MinerU; in caso di errore ripiega sull'estrazione interna (pdfium) [^src: src/lib/ingest.ts:736-777].
3. Lettura di sorgente, `schema.md`, `purpose.md`, `wiki/index.md`, `wiki/overview.md` [^src: src/lib/ingest.ts:779-785].
4. Se `persistExtractedMarkdown` è attivo, copia del markdown estratto in `raw/parsed` (vedi sotto) [^src: src/lib/ingest.ts:786-797].
5. Controllo cache per hash del contenuto. Se scatta, l'ingest è saltato ma la cascata immagini gira comunque [^src: src/lib/ingest.ts:806-908].
6. Estrazione immagini, didascalie, e se il sorgente supera il budget analisi a blocchi con checkpoint [^src: src/lib/ingest.ts:910-1062].
7. Stadio 1, analisi (temperatura 0.1); se troncata, l'ingest fallisce e il task viene riprovato [^src: src/lib/ingest.ts:1064-1109].
8. Stadio 2, generazione di blocchi `---FILE: ...---`/`---END FILE---` e `---REVIEW: ...---`. Con checkpoint di ripresa: i percorsi già scritti vengono passati al modello come «da non riemettere» [^src: src/lib/ingest.ts:1111-1208].
9. Stadio facoltativo di review: parte se la generazione supera 10.000 caratteri, ha almeno 4 blocchi FILE o contiene già blocchi REVIEW [^src: src/lib/ingest.ts:1210-1255] [^src: src/lib/ingest.ts:2391-2399] [^src: src/lib/ingest.ts:64-65].
10. Scrittura sotto il commit coordinato (`runCommit`): scrittura dei blocchi, riparazione dei blocchi troncati con una seconda chiamata, aggiornamento deterministico di indice, overview e log, pagina sorgente di ripiego se mancante [^src: src/lib/ingest.ts:1258-1453].
11. Un'ingest parziale non è un successo: lancia errore, salva un checkpoint e non scrive cache né review [^src: src/lib/ingest.ts:1478-1526].
12. Solo se completa: review nello store, `saveIngestCache`, pulizia dei checkpoint, embedding delle pagine scritte (esclusi index, log, overview) [^src: src/lib/ingest.ts:1528-1580].

Regole di scrittura dei blocchi FILE:
- Percorsi ammessi solo sotto `wiki/`: niente `..`, niente percorsi assoluti o con lettera di unità, niente caratteri o nomi riservati di Windows, niente caratteri di controllo [^src: src/lib/ingest.ts:438-473]. Il commento dichiara la minaccia: un sorgente ostile può spingere il modello a emettere percorsi fuori da `wiki/` [^src: src/lib/ingest.ts:412-425].
- Il parser gestisce CRLF, blocchi non chiusi (troncamento, segnalati e riparati), varianti di spaziatura e maiuscole dei marcatori, marcatori dentro recinti di codice, percorsi vuoti [^src: src/lib/ingest.ts:479-599].
- I blocchi del modello per `wiki/index.md` e `wiki/overview.md` sono ignorati con avviso; `wiki/log.md` è accodato; le altre pagine passano da un merge con la pagina esistente. Una pagina che ha un solo sorgente viene sostituita invece di fusa [^src: src/lib/ingest.ts:2142-2147] [^src: src/lib/ingest.ts:2238-2289].
- Solo `wiki/sources/<slug>.md` per il sorgente corrente è ammesso tra le pagine sorgente; altre e i duplicati sono scartati [^src: src/lib/ingest.ts:2079-2093].
- Controllo di lingua per pagina (solo se la lingua non è `auto`; escluse log, sources, entities) [^src: src/lib/ingest.ts:2209-2234].
- Instradamento per schema di progetto, con correzione e scarto [^src: src/lib/ingest.ts:2171-2199].

Cache di ingest: `.llm-wiki/ingest-cache.json`, `{ entries: { <sourceIdentity>: { hash: sha256, timestamp, filesWritten[] } } }`. Un colpo di cache vale solo se tutti i file di `filesWritten` esistono ancora [^src: src/lib/ingest-cache.ts:10-99].

Coda: `.llm-wiki/ingest-queue.json` con `IngestTask { id, projectId, sourcePath, folderContext, status, addedAt, error, retryCount }`; stati pending/processing/done/failed/cancelled; massimo 3 tentativi; pausa automatica di 15 minuti su limite di utilizzo del provider [^src: src/lib/ingest-queue.ts:12-24] [^src: src/lib/ingest-queue.ts:1030-1031] [^src: src/lib/ingest-queue.ts:1146-1175]. A coda svuotata parte `sweepResolvedReviews` [^src: src/lib/ingest-queue.ts:1056-1077].

## Formati di log e indici (gap 18)

- **`wiki/log.md`, voce di ingest dell'app**: intestazione `# Wiki Log` se vuoto, poi `## [YYYY-MM-DD] ingest | <sourceIdentity>`, voci separate da riga vuota. La data è locale [^src: src/lib/ingest.ts:676-685] [^src: src/lib/ingest.ts:2016-2021]. Scritta solo se il modello non ha emesso un blocco log [^src: src/lib/ingest.ts:1402-1418].
- **Blocco log del modello**: accodato come `esistente + "\n\n" + contenuto`; `YYYY-MM-DD` e la data della prima intestazione sono sostituite con la data odierna [^src: src/lib/ingest.ts:2238-2241] [^src: src/lib/ingest.ts:2060-2069].
- **Voce di cancellazione sorgente**: `## [data] <motivo> | <nome o "N source files">`, riga vuota, `Deleted N source file(s) and M wiki pages.` più `K shared pages kept (have other sources).` e un elenco `Sources:` se più di uno [^src: src/lib/source-lifecycle.ts:691-708].
- **Formato non uniforme**: dalla vista review le voci sono righe di elenco `- <data>: Saved query page ...` e `- <data>: Created N page(s) from review: ...` [^src: src/components/review/review-view.tsx:152] [^src: src/components/review/review-view.tsx:292].
- **`wiki/index.md`**: mantenuto dall'app. Predefinito `# Wiki Index`; aggiunge `- [[<percorso senza wiki/ e .md>]] — <titolo>` sotto `## Recently Updated`, senza duplicare target già presenti, fino a 200 voci [^src: src/lib/ingest.ts:1700-1732] [^src: src/lib/ingest.ts:1807-1821]. Il titolo viene dal frontmatter, altrimenti dal nome file.
- **`wiki/overview.md`**: sezione tra `<!-- llm-wiki:recent-start -->` e `<!-- llm-wiki:recent-end -->` con `## Recently Updated`, fino a 50 voci, stesso formato di riga [^src: src/lib/ingest.ts:1734-1798].
- **Creazione di pagine da review**: aggiunge `- [[<dir>/<slug>|<titolo>]]` sotto `## <Dir>` (o `## Queries` per i salvataggi) [^src: src/components/review/review-view.tsx:140-146] [^src: src/components/review/review-view.tsx:275-281].
- **`.llm-wiki/ingest-warnings.log`**: voci `## <ISO> | <sourceIdentity>` seguite da elenco numerato degli avvisi [^src: src/lib/ingest.ts:663-705].
- Non analizzato qui: il comando Rust `rebuild_wiki_index` (fuori fetta).

## Percorsi del markdown estratto e delle immagini MinerU (gap 33)

- **Immagini MinerU**: percorso relativo `media/<slug>/mineru/<percorso sanificato>`; segmenti ripuliti da caratteri non ammessi e tagliati a 80 caratteri. Scritte in `<progetto>/wiki/media/<slug>/mineru/` [^src: src/lib/mineru.ts:241-263] [^src: src/lib/mineru.ts:286-293] [^src: src/lib/mineru.ts:589-613]. Quindi le immagini MinerU stanno sotto `wiki/media/` (non più una deduzione).
- **Testo MinerU in cache**: `<cartella del sorgente>/.cache/<nomefile>.txt` [^src: src/lib/ingest.ts:745-756].
- **Copia visibile in `raw/parsed`**: `<progetto>/raw/parsed/<percorso relativo a raw/sources>.md`, con l'estensione originale mantenuta (`report.pdf.md`). Solo per le estensioni pdf, doc*, ppt*, xls*, odt, ods, odp, rtf, epub, mobi, org e solo per sorgenti sotto `raw/sources/`; percorsi con `..` rifiutati; scrittura atomica [^src: src/lib/parsed-source-output.ts:4-68].
- **Legame con l'opzione**: `persistParsedMarkdown` è chiamata solo se `sourceWatchConfig.persistExtractedMarkdown` è vero; un errore diventa un avviso e non fa fallire l'ingest [^src: src/lib/ingest.ts:786-797].
- **Default**: `persistExtractedMarkdown: false` [^src: src/lib/source-watch-defaults.json:4] [^src: src/lib/source-watch-config.ts:73-74]. Non letto il default dello store (`wiki-store`).
- Cancellazione e rename: `removeParsedMarkdown` e `moveParsedMarkdown` [^src: src/lib/parsed-source-output.ts:71-107], chiamati da `deleteSourceFiles` e `migrateSourcePath` [^src: src/lib/source-lifecycle.ts:211] [^src: src/lib/source-lifecycle.ts:493].

## Multimodale: stato reale (gap 9)

L'ingest multimodale è implementato nel codice, quindi la README è coerente con il codice. Lo stato «Spec, not started» di `plans/multimodal-images.md` risulta superato (testo del piano non riletto: lo stato è quello riportato dal gap).
- Estrazione immagini da sorgente e dal markdown [^src: src/lib/ingest.ts:910-942].
- Immagini MinerU riusate dal markdown [^src: src/lib/ingest.ts:798-804].
- Didascalie con modello di visione, cache per hash dei byte, concorrenza configurabile [^src: src/lib/ingest.ts:944-1034] [^src: src/lib/image-caption-pipeline.ts:417-623].
- Iniezione di una sezione «Embedded Images» in `wiki/sources/<slug>.md` tra due marcatori `<!-- llm-wiki:embedded-images -->`, idempotente; se la pagina manca scrive uno stub [^src: src/lib/ingest.ts:3514-3584].
- Nuovo embedding della pagina sorgente dopo l'aggiornamento delle didascalie [^src: src/lib/ingest.ts:3600-3627].
- Interruttore generale `multimodalConfig.enabled`: a spento, i riferimenti immagine sono tolti dal testo dato al modello e la sezione non viene iniettata [^src: src/lib/ingest.ts:983-995] [^src: src/lib/ingest.ts:1460-1468]. Le immagini restano sul disco.
- Il provider `codex-cli` non supporta l'input immagine: le didascalie sono saltate e contate come fallite [^src: src/lib/image-caption-pipeline.ts:444-454].
- Il percorso chat (`executeIngestWrites`) inietta le immagini solo se multimodale è attivo [^src: src/lib/ingest.ts:3909-3937].
- Non verificato: il default di `multimodalConfig.enabled`; il modulo Rust di estrazione.

## File citati nei commenti (gap 14)

| Voce | Esito | Evidenza |
|---|---|---|
| `image-caption-cache.json` | Esiste. `.llm-wiki/image-caption-cache.json`, oggetto `{ chiave: { caption, mimeType, model, capturedAt, imageHash?, outputLanguage? } }`; chiave = sha256 dei byte, oppure `<hash>::language:<lingua>` | [^src: src/lib/image-caption-pipeline.ts:46-57] [^src: src/lib/image-caption-pipeline.ts:116-119] |
| Scrittura della cache didascalie | Un solo `writeFile` a fine batch, solo se ci sono didascalie nuove; i commenti parlano di scrittura «atomica» ma il codice non usa `writeFileAtomic`. Cache corrotta: riparte vuota con avviso | [^src: src/lib/image-caption-pipeline.ts:121-152] [^src: src/lib/image-caption-pipeline.ts:584-597] |
| `lexical-graph.json` | Non verificato. Il commento dice «(when added)»; nessun codice che lo crei o lo legga nei file letti | [^src: src/lib/dedup-storage.ts:10-12] |
| `raw/sources/.cache` | Esiste come `<cartella del sorgente>/.cache/<nomefile>.txt`; la cancellazione toglie solo `raw/sources/.cache/<nomefile>.txt` e `.txt.parser` | [^src: src/lib/ingest.ts:745-756] [^src: src/lib/source-lifecycle.ts:495-500] |
| `.llm-wiki-imported` | Non verificato: nessun riferimento nei file letti | n/d |

Deduzione dal codice (non riprodotta): per un sorgente in sottocartella, la cache MinerU in `<sottocartella>/.cache/` non viene rimossa da `deleteSourceFiles`. Un percorso con segmento `.cache` non è ingeribile e `.cache` è tra gli `excludeDirs` di default [^src: src/lib/source-lifecycle.ts:235-242] [^src: src/lib/source-watch-defaults.json:54-64]. Chi scriva i marcatori `.txt.parser` non è nella fetta.

## Tipi di dedup e lint (gap 32)

- `DuplicateGroup = { slugs: string[]; reason: string; confidence: "high" | "medium" | "low" }` [^src: src/lib/dedup.ts:57-63].
- Il campo `group` di `dedup-queue.json` è un `DuplicateGroup`. Il file contiene `DedupTask[]` `{ id, projectId, group, canonicalSlug, status: pending|processing|done|failed, addedAt, error, retryCount }`, esclusi i `done` [^src: src/lib/dedup-queue.ts:29-38] [^src: src/lib/dedup-queue.ts:59-66].
- `LintResult`: `type` in `orphan | broken-link | no-outlinks | semantic`; `severity` in `warning | info`; `page`, `detail`; opzionali `affectedPages`, `brokenTarget`, `suggestedTarget`, `suggestedSource` [^src: src/lib/lint.ts:16-25].
- Il lint strutturale produce solo orphan, broken-link e no-outlinks [^src: src/lib/lint-structural-core.ts:9-17].
- Il lint semantico produce sempre `type: "semantic"`: `page` è il titolo del blocco `---LINT:`; severità `warning` solo se il modello scrive «warning», altrimenti `info`; il sottotipo (contradiction, stale, missing-page, suggestion) è il prefisso `[sottotipo]` dentro `detail`. I `missing-page` per pagine già esistenti sono scartati [^src: src/lib/lint.ts:202-203] [^src: src/lib/lint.ts:321-347].
- La lista «non duplicati» è `.llm-wiki/dedup-not-duplicates.json`, array di array di slug [^src: src/lib/dedup-storage.ts:17-46].
- Non verificato: la forma persistita di `lint.json`.

## Cancellazione, lato TypeScript (gap 34)

- **Chi genera `delete:<percorso>`**: `components/lint/lint-view.tsx` per le review di tipo `broken-link`, con `action = delete:${pp}/wiki/${item.page}` (percorso assoluto; `item.page` viene dal lint strutturale) [^src: src/components/lint/lint-view.tsx:219-223]. Le altre review del lint usano solo `open:` e `Skip` [^src: src/components/lint/lint-view.tsx:234-237] [^src: src/components/lint/lint-view.tsx:247-250].
- **Review generate dall'ingest**: `parseReviewBlocks` costruisce ogni opzione con `action = label`, dove il testo è quello della riga `OPTIONS:` scritta dal modello, senza validazione [^src: src/lib/ingest.ts:2346-2356]. Il prompt chiede solo `Create Page | Skip` [^src: src/lib/ingest.ts:2610-2618]. Il parser, però, accetterebbe un'etichetta qualsiasi.
- **Chi esegue**: `review-view.tsx`, con `action.startsWith("delete:")`, fa `deleteFile(action.slice(7))`, aggiorna l'albero e risolve la review come «Deleted». Nessuna conferma, nessun controllo di confine, nessuna cascata (embedding, riferimenti) [^src: src/components/review/review-view.tsx:189-206].
- **Conferma sulle pagine orfane**: presente. `handleDeleteOrphan` chiede conferma `destructive` e poi chiama `cascadeDeleteWikiPagesWithRefs` [^src: src/components/lint/lint-view.tsx:326-346].
- **Cascata**: `cascadeDeleteWikiPage` cancella il file, l'embedding e, per una pagina sorgente, `wiki/media/<slug>/` (con guardia sullo slug vuoto o che inizia per `.`). `cascadeDeleteWikiPagesWithRefs` riscrive indice, wikilink e `related:` e pulisce le review (`affectedPages` assoluti o relativi a `wiki/`) [^src: src/lib/wiki-page-delete.ts:70-109] [^src: src/lib/wiki-page-delete.ts:133-170] [^src: src/lib/wiki-page-delete.ts:202-288].
- **Cancellazione di un sorgente**: `deleteSourceFiles` toglie file, copia parsed, cache `.cache`, voce di ingest-cache; per ogni pagina che cita il sorgente riscrive `sources` o, se non resta alcun sorgente, cancella la pagina in cascata, poi accoda la voce di log [^src: src/lib/source-lifecycle.ts:460-578].
- **Ingest annullato**: i file già scritti si conservano, perché potrebbero essere merge su pagine esistenti [^src: src/lib/ingest-queue.ts:262-266] [^src: src/lib/ingest-queue.ts:1107-1112]. `cleanupWrittenFiles` esiste ma i commenti dicono che la cancellazione non lo chiama; chiamanti non trovati nei file letti [^src: src/lib/ingest-queue.ts:273-289].
- Fuori fetta e non letto qui: `delete_file` in Rust (confine del progetto), vedi §Gap evidenti.

## Riferimenti incrociati nella fetta (gap 25, parte)

- **`sourceIdentity`**: percorso relativo a `raw/sources/` (tolto il prefisso o il marcatore `/raw/sources/`), altrimenti solo il nome file [^src: src/lib/source-identity.ts:11-27]. Il campo `sources` delle pagine è canonicalizzato su di essa [^src: src/lib/ingest.ts:1835-1863].
- **`ingest-cache.json`**: indicizzato per `sourceIdentity`; `filesWritten` sono percorsi relativi `wiki/...`; la lettura accetta anche assoluti [^src: src/lib/ingest-cache.ts:17] [^src: src/lib/ingest-cache.ts:81-83] [^src: src/lib/ingest.ts:1548].
- **`ingest-queue.json`**: `sourcePath` relativo al progetto se interno, assoluto altrimenti [^src: src/lib/ingest-queue.ts:18] [^src: src/lib/ingest-queue.ts:182-188] [^src: src/lib/ingest-queue.ts:1086-1088].
- **`review.json`**: `sourcePath` è il percorso assoluto del sorgente, perché `parseReviewBlocks(generation, sp)` riceve `sp` e `runTask` passa un percorso completo. In review il riferimento sorgente è dunque assoluto, nella coda relativo [^src: src/lib/ingest.ts:1533] [^src: src/lib/ingest.ts:2377-2385] [^src: src/lib/ingest-queue.ts:1086-1094].
- **`affectedPages` di una review**: riga `PAGES:` del modello divisa per virgole, senza normalizzazione (esempio del prompt `wiki/page1.md`) [^src: src/lib/ingest.ts:2359-2362] [^src: src/lib/ingest.ts:2647]. Gli altri moduli accettano forme diverse: `sweep-reviews` usa il nome base senza `.md`, `wiki-page-delete` accetta assoluto o relativo a `wiki/` [^src: src/lib/sweep-reviews.ts:103-105] [^src: src/lib/wiki-page-delete.ts:145-150].
- **Slug di `dedup-not-duplicates.json`**: nome base senza `.md`, non un percorso; pagine omonime in cartelle diverse collidono [^src: src/lib/dedup.ts:136-139]. Il file salva gli slug ordinati con la grafia originale; la minuscola vale solo per la chiave di confronto, mentre il commento di intestazione dice «lowercased» [^src: src/lib/dedup-storage.ts:6-9] [^src: src/lib/dedup-storage.ts:62-68].
- **`related:` nel frontmatter**: slug nudi per prompt; la cascata li confronta con `normalizeWikiRefKey` [^src: src/lib/ingest.ts:2566-2567] [^src: src/lib/wiki-page-delete.ts:265-273].
- **Id**: review `review-<fnv1a32 esadecimale 8>` su `tipo::titolo normalizzato` [^src: src/stores/review-store.ts:49-58]; task `ingest-<ts>-<rand>` e `dedup-<ts>-<rand>` [^src: src/lib/ingest-queue.ts:178-180] [^src: src/lib/dedup-queue.ts:86-88].
- **Nuove cartelle in `.llm-wiki/`** trovate nella fetta: `ingest-progress/<slug>-<hash64>.json`, checkpoint dell'analisi a blocchi [^src: src/lib/ingest.ts:3043-3049]; `ingest-generation/<slug>-<fingerprint>.json`, checkpoint della generazione [^src: src/lib/ingest.ts:3051-3057]; `page-history/<percorso con "/" → "_">-<ISO con ":" e "." → "-">`, backup della pagina prima del merge [^src: src/lib/ingest.ts:3489-3498]; `ingest-warnings.log`. Hash: FNV-1a a 64 bit, 16 caratteri esadecimali [^src: src/lib/ingest.ts:3030-3041].

## Requisiti funzionali confermati sull'ingest (gap 11, parte)

Confermati dal codice: ingest a due stadi con review facoltativa; analisi a blocchi per sorgenti lunghe con ripresa [^src: src/lib/ingest.ts:3240-3377]; cache per hash; merge di pagine esistenti [^src: src/lib/ingest.ts:2266-2289]; guardia di percorso; controllo di lingua per pagina; coda persistente con 3 tentativi; pulizia delle review risolte a coda svuotata, in due fasi (regole poi giudizio LLM, massimo 5 batch da 40) [^src: src/lib/sweep-reviews.ts:182-184] [^src: src/lib/sweep-reviews.ts:342-462]; dedup di pagine e lint; importazione, rename e cancellazione dei sorgenti [^src: src/lib/source-lifecycle.ts:137-233]. Non coperti: chat, ricerca, deep research, agente, API.

## Dipendenze, normative, test
Non oggetto di questa fetta: vedi raw/2026-11-20-repo-llm_wiki.md. Nessun segreto rilevato nei file letti (compaiono solo nomi di campo come `apiKey`, `token`, mai valori).

## Documenti correlati
- raw/2026-11-20-repo-llm_wiki.md e le estrazioni di persistenza a, b, c del 2026-11-20.

## Gap evidenti

**Esiti.** Gap 9, 18, 32, 33 chiusi. Gap 34 chiuso lato TS. Gap 14 parziale (tre voci su quattro). Gap 11 e 25 parziali.

**Catena di cancellazione: IPOTESI NON RIPRODOTTA.** Dal solo testo del codice: (1) l'etichetta `OPTIONS:` scritta dal modello è accettata come `action` senza validazione [^src: src/lib/ingest.ts:2346-2356]; (2) `review-view.tsx` esegue `delete:<percorso>` senza conferma né controllo di confine [^src: src/components/review/review-view.tsx:189-206]; (3) secondo la fetta C1, `delete_file` in Rust non confina il percorso al progetto (`src-tauri/src/commands/fs.rs:1737-1788`, riportato dal coordinatore, non riletto da questa fetta). Se i tre passaggi si combinano, un sorgente ostile potrebbe portare a cancellare un percorso qualunque. Il prompt, che chiede solo `Create Page | Skip` [^src: src/lib/ingest.ts:2610-2618], è una barriera debole e non è una verifica. Mai riprodotta.

**Non verificati (non «assenti»)**: `lexical-graph.json`; `.llm-wiki-imported`; chi scrive i marcatori `.txt.parser`; default di `multimodalConfig.enabled` e dello store per `persistExtractedMarkdown`; forma persistita di `lint.json`; `ignorePages` di `lint-config`; `wikiPageIdFromPath`; chiavi di `scheduled-import-db.json`; chiamanti di `cleanupWrittenFiles` e `clearCompletedTasks`; `rebuild_wiki_index` in Rust.

**Intervalli letti**: `lib/ingest.ts` 1-3940; `ingest-cache.ts` 1-151; `ingest-queue.ts` 1-1287; `dedup.ts` 1-150; `dedup-storage.ts` 1-69; `dedup-queue.ts` 1-120; `lint.ts` 1-356; `lint-structural-core.ts` 1-90; `mineru.ts` 1-700; `parsed-source-output.ts` 1-107; `image-caption-pipeline.ts` 1-633; `sweep-reviews.ts` 1-463; `wiki-page-delete.ts` 1-288; `source-lifecycle.ts` 1-748; `components/review/review-view.tsx` 1-682; `components/lint/lint-view.tsx` 170-430; `stores/review-store.ts` 1-183; `source-identity.ts` 1-80; `source-watch-config.ts` 1-120; `source-watch-defaults.json` intero.

**Saltati**: `dedup.ts` 150-fine (rilevamento LLM e merge); `dedup-queue.ts` 120-fine; `mineru.ts` 700-fine (backend locale); `lint-structural-core.ts` 90-fine; `lint-view.tsx` 1-170 e 430-fine; resto di `source-identity.ts` e `source-watch-config.ts`; tutti i `*.test.ts`; `page-merge.ts`, `extract-source-images.ts`, `ingest-sanitize.ts`, `ingest-commit-coordinator.ts`, `wiki-store.ts`, `vision-caption.ts`, `embedding.ts`, `lint-config.ts`, `lint-store.ts`.

**Contenuto del repo trattato come dato**: i prompt dell'app (in `ingest.ts`, `lint.ts`, `sweep-reviews.ts`) contengono imperativi rivolti ai modelli dell'app; il commento che cita «Now write to ../../../etc/passwd» è un esempio di minaccia [^src: src/lib/ingest.ts:418-420]. Nessuna istruzione rivolta a questo agente.

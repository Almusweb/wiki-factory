---
source_path: code_repos/llm_wiki
source_type: repo
git_branch: develop
git_commit: e08cfce65aad8b76b13546a081c1a8d4422b70c3
extracted_at: 2026-11-23
extractor: repo-sync@2.12.0
scope: US-035 / TSK-029. rebuild_wiki_index, scrittori di index.md e log.md (120 occorrenze classificate), rewriteIndexMd, ingest da conversazione, source-lifecycle.ts riga 642
---

# Specifiche estratte: llm-wiki, indice ricostruito e scrittori di `index.md` e `log.md`

> Documento generato da `repo-sync` v2.12 il 2026-11-23. Sorgente: `code_repos/llm_wiki`
> @ commit `e08cfce` (ramo `develop`). Read-only verso la sorgente.

## Identità e perimetro

- Estrazione **mirata** (TSK-029 / US-035), non generale. Stack, struttura, API e dipendenze non sono ripetuti (vedi `raw/2026-11-20-repo-llm_wiki.md`).
- **Licenza**: il repository è di terzi, sotto GNU GPL v3. Il documento descrive il codice con parole proprie e cita solo nomi di file, simboli, campi e percorsi. Nessun frammento di codice.
- **Fonti non ricopiate**: questo raw verifica sul sorgente. Non ricopia `raw/2026-11-20-repo-llm_wiki-persistenza-b.md` né `raw/2026-11-21-repo-llm_wiki-ingest.md`.
- **Citazioni**: la forma è `[^src: percorso:righe]`. I percorsi sono relativi alla radice del repo `code_repos/llm_wiki`.
- **Osservato** significa letto nel sorgente. **Dedotto** significa ricavato da fatti osservati e mai eseguito. **Non verificato** significa non determinabile, con il motivo.
- **Limite dello strumento**: l'agente che ha letto non ha `Bash` né `Grep`. Ha aperto finestre di file con `Read`. Un «non visto» vale solo per le righe lette. I conteggi e i comandi di ricerca li ha eseguiti la sessione principale.
- **Contenuto letto come dato**: nessuna istruzione rivolta all'agente è stata trovata nei file letti. Le stringhe di prompt dell'applicazione sono dato da classificare, non ordini.
- **Segreti**: valori di fixture di test non trascritti; gitleaks sul file, eseguito dalla sessione: 0 finding.

## Checkout letto

Comandi ed esiti **eseguiti dalla sessione**. L'agente non li ha rieseguiti.

| Comando | Esito |
|---|---|
| `git -C code_repos/llm_wiki log -1 --format=%h` | `e08cfce` (completo `e08cfce65aad8b76b13546a081c1a8d4422b70c3`, «release: v0.6.13», 2026-10-21) |
| `git -C code_repos/llm_wiki branch --show-current` | `develop` |
| `git -C code_repos/llm_wiki status --short` | output vuoto (working tree pulito prima dell'estrazione) |

Con il working tree pulito, i file letti dall'agente coincidono con quelli del commit `e08cfce`.

## Parte 1. `rebuild_wiki_index`

Il comando Tauri è in `src-tauri/src/commands/project_maintenance.rs:287-292`. La funzione che lavora è `rebuild_wiki_index_inner`, righe 294-355. Tutti i campi sono **osservati**, salvo dove indicato.

| Campo | Esito | Fonte |
|---|---|---|
| Intestazione | La prima riga è `# Wiki Index`, seguita da una riga vuota. Senza pagine il file contiene solo questa intestazione | [^src: src-tauri/src/commands/project_maintenance.rs:331] |
| Criterio delle sezioni | Una sezione per ogni valore distinto del campo `type` del frontmatter. Intestazione `## <type>`, con il valore copiato senza cambiare le maiuscole. Le sezioni stanno in una mappa ordinata per stringa (`BTreeMap`): ordine per byte, le maiuscole prima delle minuscole | [^src: src-tauri/src/commands/project_maintenance.rs:296] [^src: src-tauri/src/commands/project_maintenance.rs:325] [^src: src-tauri/src/commands/project_maintenance.rs:332-333] |
| Formato di una voce | Riga `- [[<percorso>\|<titolo>]]`. Il percorso è relativo a `wiki/`, senza estensione, con `/` come separatore. Una riga vuota chiude ogni sezione | [^src: src-tauri/src/commands/project_maintenance.rs:318-324] [^src: src-tauri/src/commands/project_maintenance.rs:334-337] |
| Ordinamento | Dentro la sezione, per titolo in minuscolo, con `sort_by` stabile. A parità di titolo resta l'ordine di visita della directory, perché `WalkDir` è usato senza ordinamento esplicito | [^src: src-tauri/src/commands/project_maintenance.rs:327-329] [^src: src-tauri/src/commands/project_maintenance.rs:297] |
| Pagine escluse | (a) voci che non sono file; (b) file con estensione diversa da `md`, confronto esatto in minuscolo; (c) file con nome base `index`, `overview` o `log`, senza distinzione di maiuscole, in qualsiasi sottocartella di `wiki/` | [^src: src-tauri/src/commands/project_maintenance.rs:299-303] [^src: src-tauri/src/commands/project_maintenance.rs:309-313] |
| Valore usato quando manca `type` | `other`. Vale anche per un `type` vuoto, perché un valore vuoto è scartato | [^src: src-tauri/src/commands/project_maintenance.rs:316] [^src: src-tauri/src/commands/project_maintenance.rs:284] |
| Valore usato quando manca `title` | Il nome base del file senza estensione | [^src: src-tauri/src/commands/project_maintenance.rs:317] |
| Lettura di `type` e `title` | `frontmatter_value`: normalizza `\r\n`, richiede `---` in testa, cerca la chiave per nome, toglie virgolette singole e doppie. Una chiave indentata con lo stesso nome corrisponde ugualmente | [^src: src-tauri/src/commands/project_maintenance.rs:276-285] |
| Modo di scrittura | Scrive in `wiki/.index.md.rebuild.tmp`, sincronizza su disco, poi rinomina su `index.md`. Su Windows cancella prima `index.md` | [^src: src-tauri/src/commands/project_maintenance.rs:339-350] |
| Lettura del vecchio indice | Nessuna. In 294-355 il vecchio `index.md` non è mai aperto | [^src: src-tauri/src/commands/project_maintenance.rs:294-355] |
| Risultato | Una struttura con il numero di pagine e di gruppi | [^src: src-tauri/src/commands/project_maintenance.rs:269-274] [^src: src-tauri/src/commands/project_maintenance.rs:351-354] |

Dedotto (non testato): i link simbolici sono saltati. La causa è `follow_links(false)` di `walkdir`, il cui sorgente non è letto.

Contesto, non prova: il test `rebuilds_index_from_page_frontmatter` verifica `## entity` e due voci con percorso e titolo [^src: src-tauri/src/commands/project_maintenance.rs:28-50]. Il test non è stato eseguito.

Invocazione dall'interfaccia: la mappa della sessione indica `src/components/settings/sections/maintenance-section.tsx:201` e la registrazione `src-tauri/src/lib.rs:655`. Sono dati della sessione, non letti dall'agente.

## Parte 2. Sezioni di `create_project` e `## Recently Updated`

Esito di tutto il punto: **dedotto**. La sessione ha dichiarato che `cargo` e `rustc` non sono installati: il test non è eseguibile e nessuna prova è stata eseguita. Nessuna esecuzione dell'applicazione né build (Q_003).

| Sezione | Chi la scrive (osservato) | Dopo `rebuild_wiki_index` | Stato |
|---|---|---|---|
| `# Wiki Index` | `create_project_impl` [^src: src-tauri/src/commands/project.rs:155-169] | ricreata con lo stesso testo, riscritta da zero | dedotto: «conserva» |
| `## Entities`, `## Concepts`, `## Sources`, `## Queries`, `## Comparisons`, `## Synthesis` (tutte vuote) | `create_project_impl` [^src: src-tauri/src/commands/project.rs:157-167] | sparisce. Il nuovo file contiene solo le sezioni `## <type>` dei valori trovati (per esempio `entity`, `concept`), con nomi diversi | dedotto: «elimina» |
| `## Recently Updated` (indice) | `updateBoundedRecentIndexSection` [^src: src/lib/ingest.ts:1807-1821], stringa a riga 1808; chiamata da `updateWikiIndexDeterministically` [^src: src/lib/ingest.ts:1730] | sparisce | dedotto: «elimina» |

Motivo della deduzione: il file è costruito da zero con le sole pagine trovate e sostituito per rinomina. Il vecchio indice non è letto né fuso [^src: src-tauri/src/commands/project_maintenance.rs:331-350].

Note osservate:
- La stringa `## Recently Updated` compare anche per `overview.md`, tra due marcatori di commento [^src: src/lib/ingest.ts:1788-1793]. Quella sezione non riguarda l'indice. La ricostruzione salta `overview.md` [^src: src-tauri/src/commands/project_maintenance.rs:309-313].
- Dopo una ricostruzione, l'ingest aggiunge di nuovo la sezione in fondo al file (caso senza sezione presente) [^src: src/lib/ingest.ts:1809-1820]. Evita i doppioni perché legge le voci già presenti con un criterio che accetta il formato `[[target|titolo]]` [^src: src/lib/ingest.ts:1713-1720].
- La costante `AGGREGATE_WIKI_PATHS` (tre percorsi aggregati) è definito a [^src: src/lib/ingest.ts:67]. Due usi come esclusione stanno a `ingest.ts:1707` e `ingest.ts:1744`. Sono **dati della sessione** (`git grep` su `AGGREGATE_WIKI_PATHS`, 3 righe) e le righe non contengono la stringa letterale: sono fuori criterio e non entrano nel conteggio.

## Parte 3. Occorrenze di `index.md` e `log.md`

### Ambito di ricerca dichiarato

- **Percorsi**: `src/`, `src-tauri/src/`, `mcp-server/src/`, `extension/`, `scripts/`.
- **Tipi di file**: `*.ts` e `*.tsx` in `src/`, `*.rs` in `src-tauri/src/`, tutti i file di `mcp-server/src/`, `extension/` e `scripts/` per intero.
- **Esclusi**: `*.test.ts` e `src/test-helpers/**` e `mcp-server/test/**` (test TS, 60 righe); `src/i18n/*.json` (stringhe UI, 8 righe); documenti `*.md` (README in quattro lingue, `llm-wiki.md`, `mcp-server/README.md`, 35 righe). Totale escluso: 103 righe. Le righe di `extension/` e `scripts/` dentro l'ambito sono 0.
- **Inclusi**: i moduli di test Rust in linea (`#[cfg(test)]`). Le loro righe sono classificate «altro / test in linea».
- **Criterio**: stringa fissa, sensibile alle maiuscole, come sottostringa (comprende `wiki/index.md`, `"index.md"`, `/index.md`). Unità di conteggio: la riga (`file:riga`). Una riga con entrambi i termini conta una volta (12 righe). I file sono quelli tracciati al commit `e08cfce` (`git grep` sul commit).
- **Comando di conteggio** (eseguito dalla sessione, dalla radice della factory):

```
git -C code_repos/llm_wiki grep -n -F -e index.md -e log.md e08cfce -- 'src/*.ts' 'src/*.tsx' ':!src/**/*.test.ts' ':!src/test-helpers/**' 'src-tauri/src/*.rs' 'mcp-server/src/*' extension scripts | wc -l
```

- **Esiti** (dati della sessione): **120 righe trovate** (`index.md` 95 righe, `log.md` 37 righe, 12 con entrambi). Con le 103 escluse il totale su tutto il repo è 223 (120 + 60 + 8 + 35).
- **Righe classificate: 120.** Il numero delle classificate è uguale al numero delle trovate.
- **Limite del criterio**: un percorso costruito a runtime (per esempio il nome di file di un blocco `FILE` proposto dal modello, o un percorso composto con una variabile) non contiene la stringa e non è trovato. Gli identificatori `"index"` e `"log"` (filtri sul nome base, per esempio `project_maintenance.rs:311`, `page_embedding.rs:118`) non sono occorrenze del criterio. **La completezza dell'elenco vale solo rispetto a questo criterio letterale.**
- Le chiamate di scrittura usano variabili e quindi non compaiono nelle 120 righe. I loro siti sono nel capitolo «Siti di scrittura associati», fuori dal conteggio.

### Classi

- **scrittura**: la riga è, o compone l'argomento di, una chiamata che crea, modifica, rinomina o cancella `index.md` o `log.md`. Sottotipi: «scrittura diretta»; «preparazione del percorso» (la riga compone il percorso, scritto più avanti); «annuncio dopo la scrittura» (registra o notifica un file già scritto); «guardia di ramo» (la riga decide se il file è scritto).
- **lettura**: la riga legge il file o ne verifica la presenza.
- **altro**: tutto il resto. Sottotipi: test in linea (con «scrive fixture» se il test scrive un file), commento, filtro, messaggio di errore, testo di prompt, testo di schema, costante di testo, etichetta UI, voce di changelog, costante, descrizione di schema.

### Tabella delle 120 occorrenze

| File | Riga | Classe | Sottotipo | Funzione contenitore |
|---|---|---|---|---|
| mcp-server/src/index.ts | 88 | altro | descrizione di schema (tool MCP) | gestore `ListToolsRequestSchema` (riga 35), tool `llm_wiki_read_file` |
| src-tauri/src/agent/runtime.rs | 5641 | altro | test in linea (dato, nessuna scrittura) | test `iteration_limit_answer_reports_generated_workspace_files` |
| src-tauri/src/agent/runtime.rs | 5660 | altro | test in linea (assert) | test `iteration_limit_answer_reports_generated_workspace_files` |
| src-tauri/src/agent/runtime.rs | 5667 | altro | test in linea (dato, nessuna scrittura) | test `iteration_limit_answer_preserves_plain_limit_without_workspace_files` |
| src-tauri/src/api_server.rs | 2982 | altro | test in linea (assert) | test `safe_join_accepts_project_relative_paths` |
| src-tauri/src/api_server.rs | 2983 | altro | test in linea (assert) | test `safe_join_accepts_project_relative_paths` |
| src-tauri/src/api_server.rs | 2992 | altro | test in linea (scrive fixture) | test `graph_uses_relative_slugs_and_resolves_path_links` |
| src-tauri/src/api_server.rs | 3052 | altro | test in linea (scrive fixture) | test `graph_does_not_resolve_ambiguous_bare_stems` |
| src-tauri/src/api_server.rs | 3067 | altro | test in linea (scrive fixture) | test `graph_exact_id_wins_over_a_colliding_title` |
| src-tauri/src/api_server.rs | 3219 | altro | test in linea (assert) | test `public_api_paths_exclude_internal_state` |
| src-tauri/src/api_server.rs | 3220 | altro | test in linea (assert) | test `public_api_paths_exclude_internal_state` |
| src-tauri/src/api_server.rs | 3750 | altro | test in linea (assert) | test `text_content_filter_rejects_binary_extensions` |
| src-tauri/src/commands/claude_cli.rs | 496 | lettura | verifica di presenza (metadati di `wiki/index.md`) | `resolve_claude_working_directory` (riga 472) |
| src-tauri/src/commands/claude_cli.rs | 498 | altro | messaggio di errore (log) | `resolve_claude_working_directory` (riga 472) |
| src-tauri/src/commands/claude_cli.rs | 499 | altro | messaggio di errore | `resolve_claude_working_directory` (riga 472) |
| src-tauri/src/commands/claude_cli.rs | 503 | altro | messaggio di errore | `resolve_claude_working_directory` (riga 472) |
| src-tauri/src/commands/claude_cli.rs | 695 | altro | test in linea (assert) | test `claude_working_directory_requires_llm_wiki_project` (riga 661) |
| src-tauri/src/commands/claude_cli.rs | 699 | altro | test in linea (scrive fixture: crea una cartella) | test `claude_working_directory_requires_llm_wiki_project` (riga 661) |
| src-tauri/src/commands/claude_cli.rs | 704 | altro | test in linea (assert) | test `claude_working_directory_requires_llm_wiki_project` (riga 661) |
| src-tauri/src/commands/claude_cli.rs | 706 | altro | test in linea (scrive fixture) | test `claude_working_directory_requires_llm_wiki_project` (riga 661) |
| src-tauri/src/commands/codex_cli.rs | 358 | lettura | verifica di presenza (metadati di `wiki/index.md`) | `resolve_codex_working_directory` (riga 338) |
| src-tauri/src/commands/codex_cli.rs | 360 | altro | messaggio di errore (log) | `resolve_codex_working_directory` (riga 338) |
| src-tauri/src/commands/codex_cli.rs | 361 | altro | messaggio di errore | `resolve_codex_working_directory` (riga 338) |
| src-tauri/src/commands/codex_cli.rs | 365 | altro | messaggio di errore | `resolve_codex_working_directory` (riga 338) |
| src-tauri/src/commands/codex_cli.rs | 552 | altro | test in linea (assert) | test `codex_working_directory_requires_absolute_existing_project` (riga 495) |
| src-tauri/src/commands/codex_cli.rs | 557 | altro | test in linea (scrive fixture: crea una cartella) | test `codex_working_directory_requires_absolute_existing_project` (riga 495) |
| src-tauri/src/commands/codex_cli.rs | 563 | altro | test in linea (assert) | test `codex_working_directory_requires_absolute_existing_project` (riga 495) |
| src-tauri/src/commands/codex_cli.rs | 566 | altro | test in linea (scrive fixture) | test `codex_working_directory_requires_absolute_existing_project` (riga 495) |
| src-tauri/src/commands/file_sync.rs | 1837 | altro | test in linea (assert) | test `source_watch_config_filters_raw_source_extensions_and_dirs` (riga 1819) |
| src-tauri/src/commands/fs.rs | 1849 | altro | commento | `collect_related_pages` (riga 1813) |
| src-tauri/src/commands/fs.rs | 1850 | altro | filtro (salta `index.md`, `log.md`, `overview.md`) | `collect_related_pages` (riga 1813) |
| src-tauri/src/commands/fs.rs | 2726 | altro | commento (dentro un test) | test `collect_related_skips_index_log_overview` |
| src-tauri/src/commands/fs.rs | 2731 | altro | test in linea (scrive fixture: dato scritto da `make_wiki`) | test `collect_related_skips_index_log_overview` |
| src-tauri/src/commands/fs.rs | 2735 | altro | test in linea (scrive fixture: dato scritto da `make_wiki`) | test `collect_related_skips_index_log_overview` |
| src-tauri/src/commands/page_embedding.rs | 122 | altro | messaggio di errore (rifiuto di pagina aggregata) | `embed_wiki_page` (riga 66) |
| src-tauri/src/commands/project.rs | 89 | altro | testo di schema (contenuto di `schema.md`) | `create_project_impl` (riga 16) |
| src-tauri/src/commands/project.rs | 96 | altro | testo di schema (contenuto di `schema.md`) | `create_project_impl` (riga 16) |
| src-tauri/src/commands/project.rs | 106 | altro | testo di schema (contenuto di `schema.md`) | `create_project_impl` (riga 16) |
| src-tauri/src/commands/project.rs | 154 | altro | commento | `create_project_impl` (riga 16) |
| src-tauri/src/commands/project.rs | 169 | scrittura | scrittura diretta | `create_project_impl` (riga 16) |
| src-tauri/src/commands/project.rs | 171 | altro | commento | `create_project_impl` (riga 16) |
| src-tauri/src/commands/project.rs | 180 | scrittura | scrittura diretta | `create_project_impl` (riga 16) |
| src-tauri/src/commands/project_maintenance.rs | 44 | altro | test in linea (legge il risultato) | test `rebuilds_index_from_page_frontmatter` (riga 29) |
| src-tauri/src/commands/project_maintenance.rs | 59 | altro | test in linea (scrive fixture) | test `archive_round_trip_preserves_hidden_project_state` (riga 53) |
| src-tauri/src/commands/project_maintenance.rs | 103 | altro | test in linea (scrive fixture) | test `export_uses_the_resolved_destination_path` (riga 98) |
| src-tauri/src/commands/project_maintenance.rs | 233 | lettura | verifica di presenza (nome della voce nello zip) | `import_project_archive_inner` (riga 204) |
| src-tauri/src/commands/project_maintenance.rs | 240 | altro | messaggio di errore | `import_project_archive_inner` (riga 204) |
| src-tauri/src/commands/project_maintenance.rs | 339 | scrittura | preparazione del percorso (rinomina a riga 350) | `rebuild_wiki_index_inner` (riga 294) |
| src-tauri/src/commands/project_maintenance.rs | 340 | scrittura | preparazione del percorso (file temporaneo creato a riga 341) | `rebuild_wiki_index_inner` (riga 294) |
| src/components/chat/chat-message.tsx | 579 | altro | commento | `handleSave` di `SaveToWikiButton` (riga 553) |
| src/components/chat/chat-message.tsx | 580 | scrittura | preparazione del percorso (letto a riga 583, scritto a riga 600) | `handleSave` di `SaveToWikiButton` (riga 553) |
| src/components/chat/chat-message.tsx | 602 | altro | commento | `handleSave` di `SaveToWikiButton` (riga 553) |
| src/components/chat/chat-message.tsx | 603 | scrittura | preparazione del percorso (letto a riga 606, scritto a riga 611) | `handleSave` di `SaveToWikiButton` (riga 553) |
| src/components/layout/activity-panel.tsx | 80 | altro | etichetta UI (icona e tipo) | `getFileTypeInfo` (riga 69) |
| src/components/layout/activity-panel.tsx | 81 | altro | etichetta UI (icona e tipo) | `getFileTypeInfo` (riga 69) |
| src/components/layout/knowledge-tree.tsx | 72 | altro | commento | `loadPages` (riga 63) |
| src/components/layout/knowledge-tree.tsx | 73 | altro | filtro | `loadPages` (riga 63) |
| src/components/lint/lint-view.tsx | 338 | altro | commento | `handleDeleteOrphan` (riga 326) |
| src/components/lint/lint-view.tsx | 341 | altro | commento | `handleDeleteOrphan` (riga 326) |
| src/components/review/review-view.tsx | 136 | scrittura | preparazione del percorso (letto a riga 138, scritto a riga 146) | `handleResolve` (riga 90), ramo `save:` |
| src/components/review/review-view.tsx | 149 | scrittura | preparazione del percorso (scritto a riga 152) | `handleResolve` (riga 90), ramo `save:` |
| src/components/review/review-view.tsx | 271 | scrittura | preparazione del percorso (letto a riga 273, scritto a riga 284) | `handleResolve` (riga 90), ramo di creazione pagina |
| src/components/review/review-view.tsx | 287 | scrittura | preparazione del percorso (scritto a riga 292) | `handleResolve` (riga 90), ramo di creazione pagina |
| src/lib/changelog.ts | 675 | altro | voce di changelog (testo UI) | costante dati `CHANGELOG` (riga 29) |
| src/lib/changelog.ts | 683 | altro | voce di changelog (testo UI) | costante dati `CHANGELOG` (riga 29) |
| src/lib/dedup-runner.ts | 390 | altro | commento | `executeMerge` (riga 394) |
| src/lib/dedup-runner.ts | 472 | altro | commento | `executeMerge` (riga 394) |
| src/lib/dedup-runner.ts | 473 | scrittura | preparazione del percorso (scritto a riga 481) | `executeMerge` (riga 394) |
| src/lib/dedup-runner.ts | 474 | lettura | lettura da insieme di pagine in memoria (caricato a riga 404) | `executeMerge` (riga 394) |
| src/lib/dedup.ts | 23 | altro | commento | commento di modulo |
| src/lib/dedup.ts | 453 | altro | commento | `rewriteCrossReferences` (riga 456) |
| src/lib/dedup.ts | 520 | altro | commento | intestazione di sezione del modulo |
| src/lib/dedup.ts | 524 | altro | commento | `rewriteIndexMd` (riga 534) |
| src/lib/deep-research.ts | 579 | lettura | contesto di prompt | `executeResearch` (riga 524) |
| src/lib/enrich-wikilinks.ts | 35 | lettura | contesto di prompt | `enrichWithWikilinks` (riga 26) |
| src/lib/graph-filters.ts | 37 | altro | filtro | `isStructuralGraphNode` (riga 30) |
| src/lib/graph-filters.ts | 39 | altro | filtro | `isStructuralGraphNode` (riga 30) |
| src/lib/ingest-queue.ts | 197 | altro | filtro | `isStructuralWikiPath` (riga 194) |
| src/lib/ingest-queue.ts | 198 | altro | filtro | `isStructuralWikiPath` (riga 194) |
| src/lib/ingest-queue.ts | 200 | altro | filtro | `isStructuralWikiPath` (riga 194) |
| src/lib/ingest-queue.ts | 201 | altro | filtro | `isStructuralWikiPath` (riga 194) |
| src/lib/ingest.ts | 67 | altro | costante (`AGGREGATE_WIKI_PATHS`) | livello di modulo |
| src/lib/ingest.ts | 783 | lettura | contesto di prompt | `autoIngestImpl` (riga 707) |
| src/lib/ingest.ts | 1389 | scrittura | annuncio dopo la scrittura | `autoIngestImpl` (riga 707) |
| src/lib/ingest.ts | 1390 | scrittura | annuncio dopo la scrittura | `autoIngestImpl` (riga 707) |
| src/lib/ingest.ts | 1402 | altro | commento | `autoIngestImpl` (riga 707) |
| src/lib/ingest.ts | 1406 | scrittura | guardia di ramo (scrittura a riga 1410) | `autoIngestImpl` (riga 707) |
| src/lib/ingest.ts | 1408 | scrittura | preparazione del percorso (letto a riga 1409, scritto a riga 1410) | `autoIngestImpl` (riga 707) |
| src/lib/ingest.ts | 1411 | scrittura | annuncio dopo la scrittura | `autoIngestImpl` (riga 707) |
| src/lib/ingest.ts | 1412 | scrittura | annuncio dopo la scrittura | `autoIngestImpl` (riga 707) |
| src/lib/ingest.ts | 1634 | altro | filtro (predicato di percorso) | `isLogPath` (riga 1633) |
| src/lib/ingest.ts | 1639 | altro | filtro (predicato di percorso) | `isListingPath` (riga 1637) |
| src/lib/ingest.ts | 1640 | altro | filtro (predicato di percorso) | `isListingPath` (riga 1637) |
| src/lib/ingest.ts | 1648 | altro | filtro (predicato di percorso) | `isAppManagedAggregatePath` (riga 1646) |
| src/lib/ingest.ts | 1711 | scrittura | preparazione del percorso (letto a riga 1712, scritto a riga 1730) | `updateWikiIndexDeterministically` (riga 1700) |
| src/lib/ingest.ts | 1830 | altro | filtro | `isValidSourceReference` (riga 1823) |
| src/lib/ingest.ts | 2211 | altro | commento | `writeFileBlocks` (riga 2095) |
| src/lib/ingest.ts | 2521 | altro | testo di prompt | `buildGenerationPrompt` (riga 2498) |
| src/lib/ingest.ts | 2541 | altro | testo di prompt | `buildGenerationPrompt` (riga 2498) |
| src/lib/ingest.ts | 2544 | altro | testo di prompt | `buildGenerationPrompt` (riga 2498) |
| src/lib/ingest.ts | 3665 | lettura | contesto di prompt | `startIngest` (riga 3629) |
| src/lib/ingest.ts | 3752 | lettura | contesto di prompt | `executeIngestWritesImpl` (riga 3731) |
| src/lib/ingest.ts | 3783 | altro | testo di prompt | `executeIngestWritesImpl` (riga 3731) |
| src/lib/ingest.ts | 3784 | altro | testo di prompt | `executeIngestWritesImpl` (riga 3731) |
| src/lib/lint.ts | 170 | altro | commento | `runStructuralLint` (riga 157) |
| src/lib/lint.ts | 172 | altro | filtro | `runStructuralLint` (riga 157) |
| src/lib/lint.ts | 230 | altro | filtro (esclude solo `log.md`) | `runSemanticLint` (riga 205) |
| src/lib/project-file-sync.ts | 439 | altro | filtro | `isWikiPageForCascade` (riga 434) |
| src/lib/project-mutex.ts | 5 | altro | commento | commento di modulo |
| src/lib/source-lifecycle.ts | 642 | scrittura | guardia di ramo (scrittura a riga 657) | `cleanupDeletedWikiPages` (riga 606) |
| src/lib/source-lifecycle.ts | 698 | scrittura | preparazione del percorso (letto a riga 699, scritto a riga 704) | `appendSourceDeleteLog` (riga 691) |
| src/lib/templates.ts | 46 | altro | costante di testo (modello di schema `BASE_INDEX_FORMAT`) | livello di modulo |
| src/lib/templates.ts | 51 | altro | costante di testo (modello di schema `BASE_LOG_FORMAT`) | livello di modulo |
| src/lib/templates.ts | 59 | altro | costante di testo (modello di schema `BASE_CROSSREF`) | livello di modulo |
| src/lib/wiki-cleanup.ts | 9 | altro | commento | commento di modulo |
| src/lib/wiki-filename.ts | 31 | altro | commento | `makeQuerySlug` (riga 32) |
| src/lib/wiki-page-delete.ts | 177 | altro | commento | `cascadeDeleteWikiPagesWithRefs` (riga 202) |
| src/lib/wiki-page-delete.ts | 188 | altro | commento | `cascadeDeleteWikiPagesWithRefs` (riga 202) |
| src/lib/wiki-page-delete.ts | 244 | scrittura | guardia di ramo (percorso di confronto; scrittura a riga 277) | `cascadeDeleteWikiPagesWithRefs` (riga 202) |
| src/lib/wiki-page-delete.ts | 256 | scrittura | guardia di ramo (scrittura a riga 277) | `cascadeDeleteWikiPagesWithRefs` (riga 202) |

### Totali per classe

| Classe | Righe | Sottotipi |
|---|---|---|
| scrittura | 22 | scrittura diretta 2; preparazione del percorso 12; annuncio dopo la scrittura 4; guardia di ramo 4 |
| lettura | 9 | contesto di prompt 5; verifica di presenza 3; lettura da insieme in memoria 1 |
| altro | 89 | test in linea 25 (scrive fixture 11, nessuna scrittura 14); commento 23; filtro 16; messaggio di errore 8; testo di prompt 5; testo di schema 3; costante di testo 3; etichetta UI 2; voce di changelog 2; costante 1; descrizione di schema 1 |
| **Totale classificate** | **120** | uguale al totale delle trovate (120) |

Controllo della somma: 22 + 9 + 89 = 120. Sottotipi di «altro»: 25 + 23 + 16 + 8 + 5 + 3 + 3 + 2 + 2 + 1 + 1 = 89.

Le occorrenze stanno in 31 file.

### Confini dei moduli di test Rust

Dato della sessione (`git grep` sulle righe `mod` e `#[cfg(test)]`): ogni file ha un solo `mod tests` subito dopo `#[cfg(test)]`. Posizioni: `agent/runtime.rs` 4032-4033; `api_server.rs` 2947-2948 (attributo singolo a riga 2676); `commands/claude_cli.rs` 528-529; `commands/codex_cli.rs` 384-385; `commands/file_sync.rs` 1479-1480 (attributo singolo a riga 990); `commands/fs.rs` 2084-2085 (a righe 2080-2082 un `mod anydoc_benchmark;` con attributo); `commands/page_embedding.rs` 705-706; `commands/project_maintenance.rs` 19-20; `commands/project.rs` nessuno.

Verifica fatta dall'agente leggendo le ultime righe di ogni file: il modulo `tests` chiude con la graffa finale a fine file in `runtime.rs` (5818), `api_server.rs` (4106), `claude_cli.rs` (715), `codex_cli.rs` (572), `file_sync.rs` (2018), `fs.rs` (3121), `page_embedding.rs` (893). In `project_maintenance.rs` il modulo va dalla riga 19 alla riga 120 (chiuso a riga 120): le righe 44, 59 e 103 sono dentro, le righe 233-340 sono fuori. Le righe «test in linea» (25) stanno tutte in questi moduli.

## Parte 4. `rewriteIndexMd`

Funzione `src/lib/dedup.ts:534-546`. Aiuto `lineRefersToSlug` a `src/lib/dedup.ts:548-558`.

- **Cosa fa** (osservato): toglie intere righe. Non riscrive voci. Non fonde duplicati. Il testo che resta è invariato [^src: src/lib/dedup.ts:526-530] [^src: src/lib/dedup.ts:541-545].
- **Chiamata a vuoto** (osservato): se l'insieme degli slug da togliere è vuoto, ritorna il contenuto senza modifiche [^src: src/lib/dedup.ts:538].
- **Una riga è tolta se** (osservato) [^src: src/lib/dedup.ts:552] [^src: src/lib/dedup.ts:554] [^src: src/lib/dedup.ts:556]:
  1. contiene un wikilink il cui bersaglio coincide con lo slug, con o senza alias;
  2. contiene un link Markdown che termina con `<slug>.md`;
  3. contiene `<slug>.md` come parola intera.
- **Quando scrive** (osservato): dentro `executeMerge`, passo 6 [^src: src/lib/dedup-runner.ts:472-483]. Il passo viene dopo la scrittura della pagina canonica [^src: src/lib/dedup-runner.ts:455], le riscritture dei riferimenti [^src: src/lib/dedup-runner.ts:458-460] e la cancellazione delle pagine assorbite [^src: src/lib/dedup-runner.ts:463-470]. La scrittura di `wiki/index.md` è a riga 481. Avviene solo se (a) `wiki/index.md` è nell'insieme di pagine caricato a riga 404 (controllo a righe 474-475) e (b) il testo riscritto è diverso dall'originale (riga 480). Gli slug tolti sono quelli del gruppo meno lo slug canonico [^src: src/lib/dedup-runner.ts:476-478].
- **Chi chiama** (osservato): `processNext` della coda [^src: src/lib/dedup-queue.ts:369].
- **Dedotto, non testato**: lo slug è il nome base del file senza estensione [^src: src/lib/dedup-runner.ts:406-411]. Una voce con prefisso di cartella, come il formato di `rebuild_wiki_index` (`[[entities/a|Alpha]]`) e quello di `updateWikiIndexDeterministically` (`[[entities/a]]`, [^src: src/lib/ingest.ts:1719] [^src: src/lib/ingest.ts:1726]), non corrisponde alla regola 1. Non corrisponde nemmeno alle regole 2 e 3, perché non contiene `.md`. Il test `dedup.test.ts` non è letto.
- **Confronto con il percorso di cancellazione** (osservato): `cleanIndexListing` usa un altro criterio. Vedi il capitolo «Siti di scrittura associati».
- **Non verificato**: il commento a [^src: src/lib/dedup.ts:531-532] dichiara che l'interfaccia mostra all'utente un diff prima di scrivere. Nelle righe di `executeMerge` (394-486) non c'è alcuna conferma. Non ho letto l'interfaccia che usa la coda. Non ho visto un blocco di progetto (`withProjectLock`) in 394-486.

## Parte 5. Ingest da conversazione e `source-lifecycle.ts` riga 642

### Funzione di ingest da conversazione (osservato)

- **Nome**: `executeIngestWrites`, esportata, `src/lib/ingest.ts:3719-3729`. Prende il blocco per progetto (`withProjectLock`) e delega a `executeIngestWritesImpl`, `src/lib/ingest.ts:3731-3940`. Il nome è confermato dalla lettura.
- **Chiamante**: `handleWriteToWiki` in `src/components/chat/chat-panel.tsx:1409-1418`, chiamata a riga 1413. Il pulsante è mostrato solo se `mode === "ingest"`, non c'è streaming e c'è almeno una risposta dell'assistente [^src: src/components/chat/chat-panel.tsx:1420-1421]. Il collegamento è chiuso: il pulsante `Button` ha `onClick={handleWriteToWiki}` ed è renderizzato quando `showWriteButton` è vero [^src: src/components/chat/chat-panel.tsx:1472-1484].
- **Momento di scrittura**: dopo una seconda richiesta al modello. La funzione legge `schema.md` e `wiki/index.md` [^src: src/lib/ingest.ts:3750-3753], costruisce la cronologia [^src: src/lib/ingest.ts:3755-3757] e il prompt di scrittura [^src: src/lib/ingest.ts:3759-3791], fa lo streaming [^src: src/lib/ingest.ts:3815-3831]. Poi analizza i blocchi `FILE` [^src: src/lib/ingest.ts:3836] e scrive ogni pagina [^src: src/lib/ingest.ts:3872] [^src: src/lib/ingest.ts:3874].
- **`log.md`**: se il modello emette un blocco `FILE` per `log.md`, il testo è accodato al log esistente [^src: src/lib/ingest.ts:3867-3872]. Senza quel blocco la funzione non scrive `log.md`.
- **`index.md` e `overview.md`**: non scritti. Il blocco è scartato da `isAppManagedAggregatePath` [^src: src/lib/ingest.ts:3849-3852] [^src: src/lib/ingest.ts:1646-1649]. In 3731-3940 non c'è alcuna chiamata a `updateWikiIndexDeterministically`.
- **Altro scrittore da conversazione, distinto**: `handleSave` di `SaveToWikiButton`, `src/components/chat/chat-message.tsx:553-632`. Scrive una pagina in `wiki/queries/` [^src: src/components/chat/chat-message.tsx:577], inserisce una voce sotto `## Queries` o aggiunge la sezione in fondo [^src: src/components/chat/chat-message.tsx:591-600], accoda una riga a `log.md` [^src: src/components/chat/chat-message.tsx:610-611]. Poi lancia `autoIngest` sul file salvato [^src: src/components/chat/chat-message.tsx:619-626].

### `src/lib/source-lifecycle.ts` riga 642 (osservato)

- **Funzione contenitore**: `cleanupDeletedWikiPages`, `src/lib/source-lifecycle.ts:606-663`.
- **Classe**: **scrittura**, sottotipo «guardia di ramo». La riga sceglie quando applicare `cleanIndexListing` al testo letto [^src: src/lib/source-lifecycle.ts:641-644]. Poi `writeFile` a riga 657, se il testo è cambiato (riga 655).
- La condizione vale per `wiki/index.md` e per qualsiasi file chiamato `index.md` [^src: src/lib/source-lifecycle.ts:642].
- **Chiamante**: `cleanupDeletedFiles` [^src: src/lib/project-file-sync.ts:419].

## Siti di scrittura associati

Osservati nelle finestre lette. **Fuori dal conteggio delle 120 righe**: le chiamate di scrittura usano variabili e non contengono la stringa letterale. Valgono per le finestre lette e per il criterio letterale.

### Scrittori di `index.md`

| Funzione | Scrittura | Effetto |
|---|---|---|
| `create_project_impl` | [^src: src-tauri/src/commands/project.rs:169] | crea il file con intestazione e sei sezioni vuote |
| `rebuild_wiki_index_inner` | [^src: src-tauri/src/commands/project_maintenance.rs:341-350] | sostituisce il file intero (file temporaneo e rinomina) |
| `updateWikiIndexDeterministically`, chiamata da `autoIngestImpl` [^src: src/lib/ingest.ts:1388] | [^src: src/lib/ingest.ts:1730] | aggiunge `- [[target]] — titolo` sotto `## Recently Updated`, massimo 200 voci |
| `handleSave` di `SaveToWikiButton` | [^src: src/components/chat/chat-message.tsx:600] | inserisce una voce sotto `## Queries` |
| `handleResolve` (revisione) | [^src: src/components/review/review-view.tsx:146] e [^src: src/components/review/review-view.tsx:284] | stessa logica; a riga 284 l'intestazione deriva dal nome della cartella con la prima lettera maiuscola |
| `executeMerge` tramite `rewriteIndexMd` | [^src: src/lib/dedup-runner.ts:481] | toglie righe |
| `cleanupDeletedWikiPages` tramite `cleanIndexListing` | [^src: src/lib/source-lifecycle.ts:657] | toglie voci |
| `cascadeDeleteWikiPagesWithRefs` tramite `cleanIndexListing` | [^src: src/lib/wiki-page-delete.ts:277] | toglie voci |
| `writeFileBlocks`, percorsi `…/index.md` diversi da `wiki/index.md` | [^src: src/lib/ingest.ts:2249] | sovrascrive il file intero; `wiki/index.md` e `wiki/overview.md` sono scartati prima [^src: src/lib/ingest.ts:2142-2147] |

### Scrittori di `log.md`

| Funzione | Scrittura | Effetto |
|---|---|---|
| `create_project_impl` | [^src: src-tauri/src/commands/project.rs:180] | crea `# Research Log` con una voce di creazione |
| `writeFileBlocks` | [^src: src/lib/ingest.ts:2241] | accoda il blocco del modello al log esistente |
| `autoIngestImpl` | [^src: src/lib/ingest.ts:1410] | accoda una voce deterministica, solo se il modello non ha emesso il blocco [^src: src/lib/ingest.ts:1406] |
| `executeIngestWritesImpl` | [^src: src/lib/ingest.ts:3872] | accoda il blocco del modello |
| `handleSave` di `SaveToWikiButton` | [^src: src/components/chat/chat-message.tsx:611] | accoda una riga |
| `handleResolve` (revisione) | [^src: src/components/review/review-view.tsx:152] e [^src: src/components/review/review-view.tsx:292] | accoda una riga |
| `appendSourceDeleteLog` | [^src: src/lib/source-lifecycle.ts:704] | accoda una voce alla cancellazione di una sorgente |

### Effetto di `cleanIndexListing` (osservato)

Funzione `src/lib/wiki-cleanup.ts:98-108`, letta per intero.

- Toglie le righe di elenco (iniziano con `-` o `*`) il cui **primo** wikilink ha una chiave uguale a quella di una pagina cancellata [^src: src/lib/wiki-cleanup.ts:85-87] [^src: src/lib/wiki-cleanup.ts:98-108]. Tutte le altre righe restano invariate.
- La chiave è l'ultimo segmento del percorso, in minuscolo, senza `.md`, senza spazi, trattini e underscore [^src: src/lib/wiki-cleanup.ts:49-54]. Per ogni pagina cancellata il set contiene la chiave dello slug e quella del titolo [^src: src/lib/wiki-cleanup.ts:61-68].
- Una voce con prefisso di cartella, come quelle di `rebuild_wiki_index` e di `updateWikiIndexDeterministically`, corrisponde alla chiave. La differenza con `rewriteIndexMd` è osservata. Dedotto, non testato: due pagine in cartelle diverse con lo stesso nome base hanno la stessa chiave. Una cancellazione toglie quindi entrambe le voci.
- Un bersaglio con ancora `#` è confrontato così com'è: nel codice letto non c'è alcun trattamento dell'ancora.
- Le righe 642 e 256 restano classificate «scrittura / guardia di ramo»: `cleanIndexListing` conferma che il ramo modifica il testo dell'indice prima della scrittura.

## File del repo aperti

Totale: **33 file**. Sono 31 con occorrenze, più `src/lib/dedup-queue.ts` e `src/components/chat/chat-panel.tsx`, che non hanno occorrenze. Intervalli di righe aperti con `Read`, nell'ordine di apertura per punto.

Finestre del piano:
- `src-tauri/src/commands/project_maintenance.rs`: 1-355 (intero).
- `src-tauri/src/commands/project.rs`: 10-189.
- `src/lib/templates.ts`: 38-63.
- `src/lib/ingest.ts`: 60-71, 770-799, 1370-1424, 1620-1873, 3655-3940.
- `src/lib/dedup.ts`: 15-30, 440-559.
- `src/lib/dedup-runner.ts`: 380-486.
- `src/lib/dedup-queue.ts`: 355-376.
- `src/components/chat/chat-panel.tsx`: 1390-1614.
- `src/components/chat/chat-message.tsx`: 545-644.
- `src/lib/source-lifecycle.ts`: 555-723.
- `src/lib/project-file-sync.ts`: 410-443.

Finestre per le altre occorrenze del punto 3 e per le intestazioni di funzione:
- `src-tauri/src/agent/runtime.rs`: 4025-4040, 5620-5818.
- `src-tauri/src/api_server.rs`: 2944-2995, 3040-3074, 3210-3223, 3744-3755, 4090-4106.
- `src-tauri/src/commands/claude_cli.rs`: 466-535, 654-715.
- `src-tauri/src/commands/codex_cli.rs`: 330-390, 476-572.
- `src-tauri/src/commands/file_sync.rs`: 1476-1483, 1812-1839, 2005-2018.
- `src-tauri/src/commands/fs.rs`: 1810-1866, 2074-2089, 2540-2759, 3105-3121.
- `src-tauri/src/commands/page_embedding.rs`: 52-129, 702-707, 880-893.
- `mcp-server/src/index.ts`: 26-98.
- `src/components/layout/activity-panel.tsx`: 66-95.
- `src/components/layout/knowledge-tree.tsx`: 58-85.
- `src/components/lint/lint-view.tsx`: 322-361.
- `src/components/review/review-view.tsx`: 60-169, 235-309.
- `src/lib/changelog.ts`: 1-40, 670-686.
- `src/lib/deep-research.ts`: 470-679.
- `src/lib/enrich-wikilinks.ts`: 20-59.
- `src/lib/graph-filters.ts`: 18-52.
- `src/lib/ingest-queue.ts`: 180-214.
- `src/lib/lint.ts`: 155-244.
- `src/lib/project-mutex.ts`: 1-20.
- `src/lib/wiki-filename.ts`: 22-39.
- `src/lib/wiki-page-delete.ts`: 165-289.
- Letture aggiuntive autorizzate al gate di Fase 4: `src/lib/wiki-cleanup.ts` 1-130 (intero, per `cleanIndexListing`); `src-tauri/src/commands/fs.rs` 2540-2639 (helper `make_wiki`, righe 2583-2594, scrive i file di fixture); `src/components/chat/chat-panel.tsx` 1435-1614 (pulsante di scrittura); `src-tauri/src/commands/codex_cli.rs` 476-502 (nome del test); `src/lib/changelog.ts` 1-40 (nome della costante dati).
- Intestazioni di funzione fuori piano, lette per la colonna «Funzione contenitore»: `src/lib/ingest.ts` 640-710, 2085-2299, 2480-2552, 3615-3655.

## Controlli finali

I comandi sono da eseguire dalla sessione. L'agente non ha `Bash`. Gli esiti li ha inseriti la sessione il 2026-11-23, dopo la scrittura del raw.

1. Repo invariato. Atteso: output vuoto. Esito (sessione, 2026-11-23): output vuoto, exit 0.

```
git -C code_repos/llm_wiki status --short
```

2. Commit invariato. Atteso: `e08cfce`, uguale al passo 1. Esito (sessione): `e08cfce`.

```
git -C code_repos/llm_wiki log -1 --format=%h
```

3. Segreti, scanner. Atteso: 0 finding. Esito (sessione): `no leaks found`, exit 0.

```
gitleaks detect --no-git --redact --source <percorso del raw>
```

4. Segreti, prefissi di chiavi. Atteso: 0. Esito (sessione): 1, autoriferimento: la sola riga trovata è il testo di questo comando, che contiene il pattern. Senza questa riga: 0. Una seconda ricerca della sessione, più ampia (prefissi di chiavi, `Bearer`, `BEGIN … PRIVATE`, URL con credenziali, chiave=valore lungo): 0.

```
grep -c -E "(sk-[A-Za-z0-9]|ghp_|AKIA|xox[bap]-|-----BEGIN)" raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md
```

5. Righe della tabella delle occorrenze. Atteso: 120. Esito (sessione): 120.

```
grep -c -E "^\| (src|src-tauri|mcp-server)/" raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md
```

6. Coppie `file:riga`: confronto delle coppie della tabella con `us035-occorrenze.txt` (120 righe). Atteso: nessuna differenza. Esito (sessione, script Python sulla tabella): 120 righe, 120 coppie distinte, 0 mancanti, 0 in più; 31 file distinti; classi `scrittura` 22, `lettura` 9, `altro` 89.

Il gitleaks sul file `api_server.rs` (copia fuori da `code_repos/`) è già stato eseguito dalla sessione: 0 finding.

Verifiche aggiuntive della sessione (`git grep` sul commit `e08cfce`, percorsi `src` e `src-tauri/src`):
- `git grep -n -F updateWikiIndexDeterministically`: 2 righe, la definizione [^src: src/lib/ingest.ts:1700] e la sola chiamata, in `autoIngestImpl` [^src: src/lib/ingest.ts:1388]. Chiude il punto «non verificato» 8.
- `git grep -n -F rebuild_wiki_index`: 6 righe. Definizioni e chiamata interna in `project_maintenance.rs` (righe 288, 289, 294), chiamata nel test (riga 43), registrazione del comando [^src: src-tauri/src/lib.rs:655] e una sola invocazione dall'interfaccia [^src: src/components/settings/sections/maintenance-section.tsx:201]. Chiude il punto «non verificato» 9.

## Stato dell'estrazione

**`status: success`**. Ognuno dei cinque punti è determinato o dichiarato «dedotto» o «non verificato» con il motivo. Il punto 2 resta «dedotto» per scelta: la prova non è eseguibile.

### Punti «non verificato» rimasti

1. **Prova del punto 2**: nessuna esecuzione. `cargo` e `rustc` non sono installati (dato della sessione). Il punto resta «dedotto».
2. **Ordine delle pagine con titolo uguale** in `rebuild_wiki_index`: dipende dall'ordine di visita di `WalkDir`. Il sorgente del crate non è letto.
3. **Link simbolici saltati** da `rebuild_wiki_index`: dedotto dal comportamento di `walkdir`. Il crate non è letto.
4. **Diff mostrato prima della riscrittura** di `rewriteIndexMd`: dichiarato in un commento, non trovato nel codice letto. L'interfaccia che usa la coda non è letta.
5. **Effetto di `rewriteIndexMd` sui formati con prefisso di cartella**: dedotto dalla lettura dei criteri. `dedup.test.ts` non è letto.
6. **Blocco di progetto in `executeMerge`**: non visto in 394-486. Non determinato se un'altra funzione lo applica.
7. **Percorsi costruiti a runtime**: fuori dal criterio letterale. Per esempio `executeIngestWritesImpl` e `writeFileBlocks` scrivono qualunque percorso dei blocchi `FILE`. La completezza vale solo per la stringa letterale.
8. **Altri chiamanti di `updateWikiIndexDeterministically`**: osservato solo `autoIngestImpl` (riga 1388), come dato del grafo della sessione. Non cercato altrove. *Chiuso dalla sessione*: un solo chiamante (vedi «Controlli finali», verifiche aggiuntive).
9. **Invocazione di `rebuild_wiki_index` dall'interfaccia**: dato della sessione (`maintenance-section.tsx:201`, `lib.rs:655`). Non letto dall'agente. *Chiuso dalla sessione*: una sola invocazione dall'interfaccia (vedi «Controlli finali», verifiche aggiuntive).

### Punti chiusi dalle letture aggiuntive

- Criteri di rimozione di `cleanIndexListing`: letti (vedi capitolo «Siti di scrittura associati»).
- Fixture di `fs.rs` 2731 e 2735: `make_wiki` scrive file con `fs::write` (`src-tauri/src/commands/fs.rs:2583-2594`). Classe confermata «test in linea (scrive fixture)».
- Collegamento del pulsante a `handleWriteToWiki`: confermato (`chat-panel.tsx:1477`).
- Nome del test di `codex_cli.rs`: `codex_working_directory_requires_absolute_existing_project` (`src-tauri/src/commands/codex_cli.rs:494-495`).
- Nome della costante dati di `changelog.ts`: `CHANGELOG` (`src/lib/changelog.ts:29`).

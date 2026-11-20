---
id: llm-wiki-operazioni-distruttive
type: concept
title: llm-wiki — operazioni distruttive e innesco
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: ["raw/2026-11-20-repo-llm_wiki.md"]
tags: [llm-wiki, dati, persistenza, db]
---

# llm-wiki — operazioni distruttive e innesco
> Tabella delle operazioni che cancellano o sovrascrivono dati persistiti, con innesco e salvaguardie osservate nei 21 file letti; la più delicata è il re-index completo, che non ha rollback dopo il drop della tabella v2.

## Contesto
Pagina ricavata dalla seconda estrazione sulla persistenza (commit `e08cfce`). Le operazioni sono quelle individuate nel campione; i chiamanti di interfaccia non letti (ad esempio per `clear_file_history`) sono indicati come tali. Archivi: [[llm-wiki-archivi-persistenza]]. [^src: raw/2026-11-20-repo-llm_wiki.md §Operazioni distruttive e innesco]

## Dettaglio

| Operazione (simbolo) | Archivio | Innesco | Salvaguardie osservate |
|---|---|---|---|
| `vector_clear_chunks` (drop tabella) | LanceDB v2 | Re-index completo da Settings → Embedding (commento in `vectorstore.rs`; flusso `embedAllPages` con `clearExisting`) | Il drop avviene solo dopo aver calcolato gli embedding. Non si procede se: albero wiki non leggibile; zero pagine ma chunk presenti; solo pagine vuote; una qualsiasi pagina fallita (in quel caso si aggiornano solo le pagine riuscite). **Se una scrittura fallisce dopo il drop l'indice resta incompleto: nessun rollback** (errore esplicito) |
| `vector_drop_legacy` (drop tabella) | LanceDB v1 | Dopo un re-index riuscito (`dropLegacyVectorTableBestEffort`) e da Settings (commento) | No-op se la tabella non esiste |
| `vector_delete_page` | righe v2 per `page_id` | Cancellazione sorgente (`removePageEmbedding`), `cleanupWrittenFiles` e cascata `cascadeDeleteWikiPage` (`wiki-page-delete.ts`, non letto), pulizia id legacy | Id validato; operazione idempotente |
| `vector_delete` | righe v1 | Nessun chiamante nel campione | Come sopra |
| `vector_upsert_chunks` | righe v2 | Ogni embedding di pagina | Sostituzione atomica ristretta alla pagina (merge-insert con cancellazione delle righe non più presenti). Lista vuota = no-op, non cancella |
| `vector_upsert` | righe v1 | Chiamate legacy | Cancella e poi aggiunge in due passi (non atomico); l'errore di cancellazione è solo loggato |
| `vector_optimize_chunks` | versioni LanceDB | Ogni 20 pagine incrementali per progetto (contatore solo in memoria) e dopo scritture di massa | Compatta e pota le versioni precedenti, senza cancellazione «non verificata» (per l'uso multi-istanza); errori solo loggati |
| `invalidate_page_revision` | `embedding-revisions` | Ogni upsert di chunk senza impronta (ad esempio dal percorso TS) | L'assenza del file non è errore |
| `clear_file_history` | cartella `history/` | Comando Tauri (chiamante UI non nel campione) | Rifiuta symlink fuori dal progetto |
| `set_file_history_settings` | cartella `history/` o voci | Salvataggio impostazioni: limite a 0 elimina la cartella (anche file corrotti); riduzione del limite, o primo salvataggio, taglia le voci più vecchie | Massimo bloccato a 30 |
| `prune_history_store` | file di cronologia più vecchi | Dopo ogni registrazione, se si superano 128 MiB o 2.048 file | Salta il file appena scritto |
| `restore_file_history` | file di lavoro della wiki | Azione utente | Salva prima il contenuto attuale come voce `before.history.restore`; rifiuta se il file attuale supera 512 KB |
| `rebuild_wiki_index` | `wiki/index.md` | Comando Tauri (da Settings → manutenzione, per nome) | Sovrascrive per intero; file temporaneo e rinomina. Su Windows elimina prima l'originale: finestra non atomica |
| `import_project_archive` | cartella di destinazione | Importazione utente | Destinazione vuota obbligatoria; rifiuta percorsi non sicuri e symlink; massimo 100.000 voci e 4 GB; richiede `wiki/index.md` |
| `export_project_archive` | file zip | Esportazione utente | Include anche `.llm-wiki/` (chat, sessioni, cronologia, LanceDB). Destinazione fuori dal progetto |
| Troncamento sessione agente (`append_turn`) | messaggi più vecchi | Ogni turno | Mantiene gli ultimi 40 |
| Troncamento chat (`saveChatHistory`) | messaggi più vecchi | Ogni salvataggio | Salva solo gli ultimi 100 per conversazione: i precedenti si perdono al salvataggio |
| `removeTasks`, `discardTasksForSources`, `clearCompletedTasks`, `cancelAllTasks` | `ingest-queue.json` | Azioni utente; riconciliazione dello scheduled import | `removeTasks` salta i task con run attivo. `cancelAllTasks` conserva i task. `clearCompletedTasks` tiene solo pending e processing, quindi elimina anche failed e cancelled |
| `removeFromIngestCache`, `moveIngestCacheEntry` | `ingest-cache.json` | Cancellazione o rinomina di una sorgente | Gli errori di salvataggio sono ignorati |
| `removeFromRecentProjects` | `app-state.json` | Rimozione di un progetto dall'elenco recenti | Azzera anche `lastProject`; **non** rimuove la voce da `projectRegistry` e non cancella cartelle |
| `cleanupRemovedScheduledImports` | sorgenti mirror e pagine generate | Scansione quando un file sparisce o viene escluso | Solo per il progetto attivo; per gli altri si rinvia. Se fallisce, conserva il record per riprovare |
| `resetProjectState` | solo memoria | Apertura o uscita da un progetto | Non cancella nulla su disco; chiama prima `pauseQueue`, che scarica la coda su disco |

Fonte di tutte le righe: [^src: raw/2026-11-20-repo-llm_wiki.md §Operazioni distruttive e innesco]

## Pagine collegate
[[llm-wiki-archivi-persistenza]], [[llm-wiki-versioni-e-migrazioni]], [[llm-wiki-gestione-file-corrotti]], [[llm-wiki-rischi-persistenza]]. Gap aperto: [[gaps]] (`llm-wiki-persistenza-codice-non-letto`).

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->
- US-016 — Chiamanti delle operazioni distruttive e dei percorsi legacy
- US-017 — Formato di log e indice del progetto wiki
- US-025 — Rischio 1: chat cancellate che ricompaiono
- US-028 — Rischio 4: atomicità eterogenea delle scritture
- US-030 — Rischio 6: ricostruzione dell'indice senza rollback

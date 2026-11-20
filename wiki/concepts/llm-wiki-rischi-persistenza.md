---
id: llm-wiki-rischi-persistenza
type: concept
title: llm-wiki — divergenze e rischi del layer di persistenza
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: ["raw/2026-11-20-repo-llm_wiki.md"]
tags: [llm-wiki, dati, persistenza, rischi, db]
---

# llm-wiki — divergenze e rischi del layer di persistenza
> Sette divergenze e rischi ricavati dalla lettura del codice: sono deduzioni, non fatti osservati in esecuzione.

## Contesto
Il raw dichiara che le voci seguenti sono **deduzioni dal codice letto**, non fatti osservati in esecuzione, e per ognuna indica file e simbolo. Le etichette «Non verificato» e «Da verificare» sono quelle del raw. Il campione è di 21 file; molto codice che incide sulla persistenza non è letto (gap `llm-wiki-persistenza-codice-non-letto` in [[gaps]]). [^src: raw/2026-11-20-repo-llm_wiki.md §Divergenze e rischi]

## Dettaglio

1. **Possibile ricomparsa di chat cancellate (deduzione).** `deleteConversation` (`src/stores/chat-store.ts`) rimuove la conversazione dallo store, ma `saveChatHistory` (`src/lib/persist.ts`) non elimina i file `chats/<id>.json` orfani, e `loadChatHistory` ricostruisce da quei file quando l'indice è vuoto. Se l'utente cancella tutte le conversazioni, il caricamento successivo potrebbe resuscitarle. **Non verificato**: la rimozione fisica dei file potrebbe stare in codice non letto (ad esempio `chat-panel.tsx`). [^src: raw/2026-11-20-repo-llm_wiki.md §Divergenze e rischi]
2. **Rigenerazione dell'identità del progetto (deduzione).** In `ensureProjectId` (`project-identity.ts`) un `project.json` corrotto produce un nuovo UUID. `restoreQueue` (`ingest-queue.ts`) scarta poi come «cross-project» i task con il vecchio id; le impostazioni per progetto in `app-state.json`, indicizzate per id (`projectLlmOverrides`, `projectOutputLanguages`, `sourceWatchConfig`, `projectFileSyncEnabled`), resterebbero orfane. [^src: raw/2026-11-20-repo-llm_wiki.md §Divergenze e rischi]
3. **Scritture non serializzate sul registro (deduzione).** Solo `saveProjectLlmOverride` e `saveCustomLlmPresets` (`project-store.ts`) hanno una catena di scrittura serializzata; `upsertProjectInfo` (`project-identity.ts`) usa lettura-modifica-scrittura non serializzata e parte da un registro vuoto se `loadRegistry` fallisce, con rischio di sovrascrivere l'intero `projectRegistry` con una sola voce. [^src: raw/2026-11-20-repo-llm_wiki.md §Divergenze e rischi]
4. **Atomicità eterogenea (deduzione).** Atomiche (file temporaneo e rinomina): `lint-config.json` (`writeFileAtomic`), `scheduled-import-db.json`, le revisioni embedding. Non atomiche: sessioni agente e cronologia (scrittura diretta in `session.rs` e `file_history.rs`). Per gli altri file TS dipende dall'implementazione di `writeFile` in `src/commands/fs.ts` e `src-tauri/src/commands/fs.rs`, non letta. [^src: raw/2026-11-20-repo-llm_wiki.md §Divergenze e rischi]
5. **Logica duplicata tra TS e Rust (deduzione).** Il chunking è duplicato tra `page_embedding.rs` e `src/lib/text-chunker.ts` (il commento in `page_embedding.rs` lo dichiara); la pulizia dell'id legacy è duplicata tra `embedding.ts` e `page_embedding.rs`. Inoltre `embedPage` (TS) scrive tramite `vector_upsert_chunks` senza impronta e quindi invalida le impronte salvate dal percorso Rust (`vector_upsert_chunks_inner`, ramo senza revisione). [^src: raw/2026-11-20-repo-llm_wiki.md §Divergenze e rischi]
6. **Re-index senza rollback (deduzione).** In `embedAllPages` (`embedding.ts`), dopo `vector_clear_chunks` un errore di scrittura lascia l'indice incompleto; il messaggio d'errore lo dice esplicitamente e chiede di rilanciare il re-index. [^src: raw/2026-11-20-repo-llm_wiki.md §Divergenze e rischi]
7. **Cambio di modello o di dimensione dell'embedding (da verificare).** La dimensione del vettore è fissata dal primo chunk di una scrittura (`vector_upsert_chunks_inner`). Nel campione non c'è una verifica esplicita di coerenza con la tabella esistente: la gestione di un cambio di modello sembra affidata al re-index (l'impronta di revisione include il modello). Gap: `llm-wiki-embedding-cambio-modello` in [[gaps]]. [^src: raw/2026-11-20-repo-llm_wiki.md §Divergenze e rischi]

Il raw aggiunge un ottavo punto, i segreti in chiaro in `app-state.json`, che rimanda a [[llm-wiki-archivi-persistenza]] (solo nomi di campo letti, nessun valore) e a [[llm-wiki-sicurezza]]. [^src: raw/2026-11-20-repo-llm_wiki.md §Divergenze e rischi]

## Pagine collegate
[[llm-wiki-archivi-persistenza]], [[llm-wiki-gestione-file-corrotti]], [[llm-wiki-operazioni-distruttive]], [[llm-wiki-versioni-e-migrazioni]].

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->
- EP-004 — Verificare i rischi di persistenza prima di correggerli
- US-025 — Rischio 1: chat cancellate che ricompaiono
- US-026 — Rischio 2: rigenerazione dell'identità del progetto
- US-027 — Rischio 3: scritture non serializzate sul registro dei progetti
- US-028 — Rischio 4: atomicità eterogenea delle scritture
- US-029 — Rischio 5: logica duplicata fra frontend e backend
- US-030 — Rischio 6: ricostruzione dell'indice senza rollback
- US-031 — Rischio 7: cambio di modello o di dimensione dell'embedding
- US-032 — Rischio 8: segreti in chiaro nello store applicativo
- US-033 — Sintesi dei rischi e decisione sugli interventi

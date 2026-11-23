---
id: 2026-11-23-repo-llm_wiki-residui-watch-skill
type: source
title: Specifiche estratte da llm_wiki, 2026-11-23: residui sourceWatchConfig, «Watch all projects» e voci V (repo-sync, e08cfce, LWS-TSK-012)
status: draft
created: 2026-11-23
updated: 2026-11-23
sources: ["raw/2026-11-23-repo-llm_wiki-residui-watch-skill.md"]
tags: [source, repo, llm-wiki, sincronizzazione, verifica, diff-skill-app]
---

# Specifiche estratte da llm_wiki, 2026-11-23: residui watch
> **Linea e provenienza:** `code_repos/llm_wiki`, upstream v0.6.13, commit `e08cfce` (HEAD staccato, tag v0.6.13). Seconda estrazione di LWS-US-008 (LWS-TSK-012): lettura del codice, in sola lettura, nulla eseguito. Perimetro: default di `sourceWatchConfig`, «Watch all projects» e le voci V4, V20, V21, V22 di [[llm-wiki-api-affermazioni-codice-da-verificare]]. [^src: raw/2026-11-23-repo-llm_wiki-residui-watch-skill.md §Intestazione e identità]

## Contesto
Esiti come nel raw: confermato, smentito, non conclusivo. Il confronto con le frasi della skill spetta all'ingest. Il raw non corregge la skill e non tocca `llm_wiki_skill`; non contiene prove in esecuzione. [^src: raw/2026-11-23-repo-llm_wiki-residui-watch-skill.md §Come leggere gli esiti]

## Dettaglio

### Esiti in breve
| Residuo | Esito del raw | Punto non conclusivo o non verificato |
|---|---|---|
| R1 default di `sourceWatchConfig` | confermato | massimo di `clampUserConcurrency` non letto; composizione del filtro TS sui nomi con «.» e di `should_watch_rel` non verificata |
| R2 ripiego per id nuovo | confermato | |
| R3 json, yaml, yml, xml | confermato (non inclusi di default) | |
| W1 «Watch all projects» spento di default | confermato | etichetta dell'interfaccia e valore iniziale nello store `wiki-store` non letti |
| W2 ramo inattivi senza LLM né parsing all'accodamento | confermato | |
| W3 «recenti», limite 10, 60 s | confermato | |
| V4 soglia del 5% | non conclusivo | solo perché `vectorstore::vector_search_chunks` non è letto |
| V20 «POST /chat (501)» | non conclusivo sulle versioni precedenti | |
| V21 scrittura esterna «bypassa il watcher» | smentito per il watcher; «subito» non verificato | se le scritture del server API marchino i percorsi come scritture dell'app; tempi reali; `isIngestableSourcePath` |
| V22 corsa review / auto-save | meccanismo possibile; osservazione del 2026-11-10 non decidibile | ricarica dello store review, effetto di DELETE, chiamante di `sweepResolvedReviews` |

[^src: raw/2026-11-23-repo-llm_wiki-residui-watch-skill.md §Tabella di sintesi residuo/esito/file:righe]

Dove sono finiti i fatti: default, ripiego e filtri in [[llm-wiki-sincronizzazione-file]]; confronto con la skill in [[llm-wiki-skill-vs-app-v0-6-13]] (D28-D31); meccanismo di V22 in [[llm-wiki-review-store-e-auto-save]]; quadro per voce in [[llm-wiki-api-affermazioni-codice-da-verificare]].

### Osservazioni collaterali del raw (fuori perimetro, senza giudizio)
1. `cleanupDeletedFiles` agisce sulle cancellazioni anche senza condizione su `autoIngest`.
2. Con `autoIngest` spento i cambi già visti risultano consumati nello snapshot, perché `process_queue` lo aggiorna prima che il TS riceva `changedTasks`.
3. `isSensitiveConfigSourceFile` sta in `enqueueSourceIngest`; il ramo inattivi non lo richiama nel codice letto (non verificato se `isIngestableSourcePath` lo includa). [^src: raw/2026-11-23-repo-llm_wiki-residui-watch-skill.md §Fuori perimetro: osservazioni collaterali sul ramo inattivi]

### Prove in esecuzione
Nessuna eseguita e nessuna entra nella skill. Restano «non verificate»: scritture con token, chat (JSON, SSE, cancel, 502, tetto di 8 stream), `pages/embed` con embedding attivi, 429 e 503 sotto carico, 413 e 415 sul contenuto (`rtf` compreso), bind LAN e `allowUnauthenticated`, rescan su progetto non aperto con l'opzione spenta e accesa, corsa review/auto-save anche con DELETE. [^src: raw/2026-11-23-repo-llm_wiki-residui-watch-skill.md §Prove in esecuzione non pianificate «non verificate»]

## Limiti
Letti 15 file (fra cui `source-watch-defaults.json`, `source-watch-config.ts`, `project-store.ts` a finestre, `project-file-sync.ts`, `ingest-queue.ts` a finestre, `file_sync.rs`, e frammenti di `search.rs` e `api_server.rs`). Non letti: `vectorstore.rs`, `wiki-store.ts`, `review-store.ts`, `sweep-reviews.ts`, `concurrency-limits`, `isIngestableSourcePath`, `isSensitiveConfigSourceFile`, `en.json`, la tabella delle route e i percorsi di scrittura del server API, `agent/runtime.rs`, `cors.rs`, `server_bind.rs`. [^src: raw/2026-11-23-repo-llm_wiki-residui-watch-skill.md §Copertura file letti/non letti]

## Pagine collegate
[[llm-wiki-sincronizzazione-file]], [[llm-wiki-skill-vs-app-v0-6-13]], [[llm-wiki-api-affermazioni-codice-da-verificare]], [[llm-wiki-review-store-e-auto-save]], [[2026-11-23-repo-llm_wiki-residui-api-skill]]. Gap: [[gaps]].

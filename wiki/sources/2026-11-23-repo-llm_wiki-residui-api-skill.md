---
id: 2026-11-23-repo-llm_wiki-residui-api-skill
type: source
title: Specifiche estratte da llm_wiki, 2026-11-23: residui API per la skill (repo-sync, e08cfce, LWS-TSK-011)
status: draft
created: 2026-11-23
updated: 2026-11-23
sources: ["raw/2026-11-23-repo-llm_wiki-residui-api-skill.md"]
tags: [source, repo, llm-wiki, api, verifica, diff-skill-app]
---

# Specifiche estratte da llm_wiki, 2026-11-23: residui API per la skill
> **Linea e provenienza:** `code_repos/llm_wiki`, upstream v0.6.13, commit `e08cfce`, HEAD staccato. Lettura del codice da parte di `repo-sync`, in sola lettura: nulla è stato eseguito. Perimetro: solo i residui di LWS-US-008 / LWS-TSK-011 (handler e limiti dell'API HTTP); i punti chiusi dalla verifica del 2026-11-22 non sono riletti. [^src: raw/2026-11-23-repo-llm_wiki-residui-api-skill.md §Identità]

## Contesto
Il raw dà un esito per residuo (confermato, smentito, non conclusivo). «Confermato» vuol dire che il codice fa ciò che il residuo chiede di verificare; il confronto con le frasi della skill spetta all'ingest e nessuna correzione della skill è fatta. Le righe di codice sono quelle del raw: la factory non le ha rilette. [^src: raw/2026-11-23-repo-llm_wiki-residui-api-skill.md §Come leggere gli esiti]

## Dettaglio

### Dove sono finiti i fatti
Esiti R1-R17 con le righe del raw in [[llm-wiki-api-locale]] (§Aggiornamenti v2026-11-23: scritture, chat, SSE, embed, review, rescan, limiti di corpo e ordine rispetto all'auth), [[llm-wiki-ricerca-e-grafo-api]] (R12, R13, R14, R15) e [[llm-wiki-sincronizzazione-file]] (R10). Confronto con le frasi della skill in [[llm-wiki-skill-vs-app-v0-6-13]] (D22-D27) e quadro per voce in [[llm-wiki-api-affermazioni-codice-da-verificare]]. [^src: raw/2026-11-23-repo-llm_wiki-residui-api-skill.md §Esiti per residuo]

### Esiti in breve
| Residuo | Esito del raw | Punto non conclusivo |
|---|---|---|
| R1 `handle_write_page` | confermato | regole esatte di `normalize_wiki_write_path` non lette |
| R2 `handle_chat` | confermato | |
| R3 `respond_chat_sse` | confermato | |
| R4 header SSE di successo | confermato | codifica di trasferimento (dipende da `tiny_http`, non letto) |
| R5 `AgentChatRequest` | confermato | se il runtime onori `approvedShellCommands` e `shellCommand` dal body HTTP |
| R6 eventi agente | confermato | quali eventi emetta il runtime e in che ordine; nomi snake_case dei campi derivati da serde, non provati da un test |
| R7 `embed_wiki_page` | confermato | |
| R8 PATCH review | confermato | |
| R9 `resolve` review | confermato | |
| R10 `rescan` e `kind` | confermato | `relative_watch_path` / `should_watch_rel` non letti in questo raw |
| R11 body troppo grande | confermato: 400, non 413 | |
| R12 RRF e campi di `search` | confermato | scala keyword esatta (`score_file` non letto) |
| R13 `resolve_query_embedding` | confermato | uso del timeout di 8 s e verifica della dimensione contro l'indice |
| R14 `offset`, `totalCount`, `hasMore` | confermato | |
| R15 cache di 5 s del grafo | confermato, con precisazione | |
| R16 limiti di corpo per route | confermato | |
| R17 ordine rispetto all'auth | confermato | la lettura fino a 40 MiB prima del 401 è derivata dal codice, non provata |

Nessuna voce è «smentita» in senso stretto: un esito «smentito» richiede il testo delle frasi della skill, e lo decide l'ingest. [^src: raw/2026-11-23-repo-llm_wiki-residui-api-skill.md §Esiti per residuo]

## Limiti
Non letti: `agent/runtime.rs` (219 KB, fuori perimetro; tocca R5 e R6), `commands/search.rs` oltre la riga 830 (`score_file`, ricerca vettoriale), `commands/vectorstore.rs`, `agent/provider.rs`. `cors.rs` e `server_bind.rs` erano già chiusi dalla verifica del 2026-11-22. Letti per intero: `agent/types.rs`, `agent/events.rs`; `api_server.rs` righe 1-2999; parziali `agent/tools.rs`, `commands/page_embedding.rs`, `commands/file_sync.rs`, `commands/search.rs`. Il raw dichiara nessun valore di segreto incontrato e repo cliente non modificato. [^src: raw/2026-11-23-repo-llm_wiki-residui-api-skill.md §File letti e non letti]

## Pagine collegate
[[llm-wiki-api-locale]], [[llm-wiki-ricerca-e-grafo-api]], [[llm-wiki-sincronizzazione-file]], [[llm-wiki-skill-vs-app-v0-6-13]], [[llm-wiki-api-affermazioni-codice-da-verificare]], [[2026-11-23-repo-llm_wiki-residui-watch-skill]], [[2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki]]. Gap: [[gaps]].

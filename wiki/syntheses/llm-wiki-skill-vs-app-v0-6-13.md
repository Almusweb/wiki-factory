---
id: llm-wiki-skill-vs-app-v0-6-13
type: synthesis
title: Skill llm-wiki (API v1, app 0.4.10+) contro app llm_wiki v0.6.13, differenze per la PR upstream
status: draft
created: 2026-11-22
updated: 2026-11-22
sources: ["raw/2026-11-22-repo-llm_wiki_skill.md", "raw/2026-11-21-repo-llm_wiki-api-mcp.md"]
tags: [llm-wiki, skill, api, diff-skill-app, sintesi]
---

# Skill llm-wiki (API v1, app 0.4.10+) contro app llm_wiki v0.6.13
> Pagina di lavoro per la futura PR che porterà la skill alla v0.6.13: elenca dove la skill, riferita ad app 0.4.10+, diverge da quanto la wiki sa dell'app v0.6.13 (`e08cfce`), con id D1…Dn ritrovabili col tag `diff-skill-app`.

## Contesto
- **Lato skill:** repository `llm_wiki_skill`, `main`, commit `642b438`, contratto «API v1» per app «0.4.10+», documentazione e non codice; i riferimenti sono in [[llm-wiki-skill-api-v1-dichiarata]] e [[llm-wiki-skill]]. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Versione dichiarata]
- **Lato app:** `llm_wiki` upstream v0.6.13, commit `e08cfce`, letto nel codice e **mai eseguito** (`api_server.rs` per intero), come riportato da [[2026-11-21-repo-llm_wiki-api-mcp]] e dalle pagine [[llm-wiki-api-locale]] e [[llm-wiki-sicurezza]]. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Server HTTP]
- **Non sono contraddizioni da risolvere qui.** Dove la skill diverge, la differenza è informazione di versione: la wiki non decide quale delle due descrizioni valga per una versione intermedia (gap `llm-wiki-api-storia-versioni`). Le voci D1, D2, D4, D5, D11 sono registrate anche come `## Contradictions` in [[llm-wiki-api-locale]] e, per D4 e D5, in [[llm-wiki-sicurezza]].
- **Perché la skill non è ancora «al passo»:** il suffisso «0.4.10+» non ha tetto, quindi per come è scritto copre anche 0.6.13; il README chiede di controllare il drift solo su un «major version bump». **Deduzione, non testata:** tra 0.4.10 e 0.6.13 cambia la minor, quindi la regola alla lettera non scatterebbe. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Versione dichiarata]

## Dettaglio

### Contraddizioni (la skill afferma ciò che per v0.6.13 la wiki smentisce)

| Id | Skill (API v1, app 0.4.10+) | Wiki, v0.6.13 (`e08cfce`) |
|---|---|---|
| D1 | L'unica scrittura è `sources/rescan`; nessun endpoint di scrittura in v1 e la skill dice di non inventarne. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Read-only vs scrittura] | Scrivono anche `PATCH`, `DELETE` e `resolve` delle review, `pages/write`, `pages/embed` e `chat` (sessioni agente). [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Contratto API] |
| D2 | `POST /chat` è uno stub che risponde 501. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §API surface] | `chat` risponde in JSON o SSE (`meta`, `agent`, `done`, `cancelled`, `error`), con rotta di cancel e token sempre richiesto. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Contratto API] |
| D4 | CORS `Access-Control-Allow-Origin: *`; il rischio cross-origin è affidato alla segretezza del token. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Auth, errori e limiti] | `Access-Control-Allow-Origin` solo per un elenco (estensioni `chrome-extension://` e `moz-extension://`, localhost, `127.0.0.1`, `[::1]`, `tauri://localhost`, `tauri.localhost`); le altre origini non ricevono l'header. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Autenticazione e rete] Coerente con la #318 già in [[2026-11-21-issues-llm_wiki-chiuse]]. |
| D5 | «Solo localhost»: ascolto solo su `127.0.0.1` nel modello di sicurezza. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Auth, errori e limiti] | Default `127.0.0.1`, ma `apiConfig.allowLanAccess` porta il bind a `0.0.0.0` e `LLM_WIKI_BIND_HOST` ha precedenza; nessuna distinzione di schema fra loopback e LAN. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Autenticazione e rete] |
| D11 | Metodi HTTP diversi da GET e POST: 405. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §API surface] | Metodi ammessi GET, POST, PATCH, DELETE; `OPTIONS` dà 204 con CORS prima di ogni altro controllo. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Server HTTP] |

### Estensioni (la skill non lo dice; v0.6.13 sì)

| Id | Differenza |
|---|---|
| D3 | La skill ha 8 endpoint; v0.6.13 ha 15 route più `/health` doppio. Mancano nella skill `reviews` (anche in sola lettura), `pages/embed`, `pages/write` e `chat/{sessionId}/cancel`. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Contratto API] |
| D6 | Con `allowUnauthenticated` la skill non distingue le route: in v0.6.13 `chat`, `chat/cancel`, `pages/embed` e `pages/write` richiedono sempre il token, mentre restano aperte `projects`, `files`, `files/content`, `reviews`, `search`, `graph` e `sources/rescan`. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Autenticazione e rete] |
| D7 | `/health` di v0.6.13 riporta anche `mcpEnabled`, `allowLanAccess` e `agent{chat, streaming, streamProtocol}`; risponde anche su `/health` senza prefisso e con API disabilitata. La skill elenca 8 campi (`ok`, `status`, `version`, `enabled`, `authRequired`, `authConfigured`, `allowUnauthenticated`, `tokenSource`). [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Contratto API] |
| D9 | `search` di v0.6.13 restituisce anche `graphHits`; la skill documenta `tokenHits` e `vectorHits`. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Contratto API] |
| D10 | `graph` di v0.6.13 ha `offset` ed `edgeScope` (`page` o `filtered`), restituisce `offset`, `limit`, `totalCount` e `hasMore`, e ha cache di 5 s; la skill ha `q`, `nodeType` e `limit` e dichiara nessuna paginazione dell'albero file. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Contratto API] |
| D12 | Il rate limit di v0.6.13 esclude `/health` e `OPTIONS` e si applica prima dell'auth; ci sono limiti per route (body di `chat` 40 MiB, `pages/write` circa 12 MiB, stream chat in volo 8, embed in volo 4). La skill dichiara solo 120 req/s globali, body 1 MiB e 64 in volo. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Server HTTP] |

### Concordanze (restano corrette per v0.6.13 secondo la wiki)
Forme di `{id}` (UUID, percorso esatto, `current`); `root` di `files` con gli alias e `maxFiles` con clamp 1..10000, default 2000 e 413 al superamento; allow-list di `files/content` con 403, 413 oltre 2 MiB e 415; `topK` con default 10 e massimo 50; `limit` del grafo con default 200 e massimo 1000; sorgenti e trasporti del token (`LLM_WIKI_API_TOKEN`, `apiConfig.token`, `?token=`, `X-LLM-Wiki-Token`, `Authorization: Bearer`) e 401 senza token configurato; i quattro valori di stato; rate limit 120 al secondo con 429; 64 richieste in volo con 503; header CORS ammessi `Authorization`, `X-LLM-Wiki-Token` e `Content-Type`; `queryEmbedding`; `/health` senza auth. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Contratto API] [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Server HTTP] [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Autenticazione e rete]

### Non confrontabili (la wiki non ha il dato; confluiscono nel gap `llm-wiki-skill-punti-da-verificare`)
Elenco dei campi di ogni risultato di `search`; valori di `mode` e range degli score; campi del risultato di `rescan` e `kind` di `changedTasks`; `Retry-After`; durata del preflight (600 s nella skill); codice del body generico troppo grande; presenza del campo `truncated` in `files`; estensioni leggibili; default di `sourceWatchConfig`; elenco dei valori di `nodeType`. Per le incoerenze interne della skill vedi la tabella numerata in [[llm-wiki-skill]] (voci n. 1-17), che non ripeto qui. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Gap evidenti]

### Altro confronto utile
La skill descrive solo l'API HTTP, in sola lettura più il rescan, e non cita il server MCP; il server MCP di v0.6.13 espone 12 strumenti, fra cui `llm_wiki_write_page` e `llm_wiki_embed_page`, sulle stesse route (vedi [[llm-wiki-mcp-server]]). Non è una contraddizione: sono due vie d'accesso diverse alla stessa API. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Server MCP]

## Pagine collegate
[[llm-wiki-skill]], [[llm-wiki-skill-api-v1-dichiarata]], [[llm-wiki-api-locale]], [[llm-wiki-sicurezza]], [[llm-wiki-mcp-server]], [[2026-11-22-repo-llm_wiki_skill]]. Gap: [[gaps]] (`llm-wiki-skill-punti-da-verificare`, `llm-wiki-api-storia-versioni`).

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

## Aggiornamenti (v2026-11-22, evidenze alm-wiki)
Dalla source page [[2026-11-22-repo-alm-wiki-evidenze-api]]. Il testo sopra non è modificato. **Base:** osservato in esecuzione sull'app 0.6.13 il 2026-11-13 in un progetto locale dell'utente (alm-wiki), non riprodotto dalla factory: una prova, un progetto, non replicata. Linea: upstream v0.6.13; la build provata non è verificata come `e08cfce`. Dettaglio delle osservazioni in [[llm-wiki-api-osservazioni-esecuzione-v0-6-13]]. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Prova runtime del 2026-11-13 (P)]

### D1-D12 e osservazione in esecuzione
| Esito | Id | Osservazione |
|---|---|---|
| Confermata in esecuzione | D4 | Origini locali riecheggiate con `Vary: Origin` e `Allow-Private-Network: true`; per `https://example.com`, `null` e `http://localhost.evil.com` l'header manca (la richiesta è comunque servita) [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Osservazioni R della prova runtime (12, tutte R)] |
| Confermata in esecuzione | D7 | `/health` con `agent`, `mcpEnabled`, `allowLanAccess` e `version` 0.6.13; risponde anche senza prefisso e con `POST` [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Osservazioni R della prova runtime (12, tutte R)] |
| Confermata in esecuzione | D9 | `graphHits` presente nella risposta di `search` [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Osservazioni R della prova runtime (12, tutte R)] |
| Confermata in esecuzione | D10 | `offset`, `limit`, `totalCount` e `hasMore` sempre presenti; `edgeScope` non valido dà 400; la cache di 5 s non è provata in esecuzione [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Osservazioni R della prova runtime (12, tutte R)] |
| Parziale | D11 | `OPTIONS` dà 204 senza auth e `PUT` con token dà 405; `POST` e `DELETE` su `projects` e `GET` su `search` danno 404, non 405: la skill (405 fuori da `GET` e `POST`) è smentita in questo punto, e il 404 è coerente con l'ordine dei controlli già in wiki [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Osservazioni R della prova runtime (12, tutte R)] |
| Parziale | D2 | `/health` riporta `agent.chat: true` (2026-11-08); la chat come funzione non è stata provata [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Fatti R del task 002 (2026-11-08)] |
| Parziale | D3 | `reviews` in lettura risponde (GET osservato); `pages/embed`, `pages/write` e `chat/cancel` non sono stati provati con token [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Osservazioni R della prova runtime (12, tutte R)] |
| Non confermate in esecuzione | D1, D5, D6, D12 | Scritture con token, bind LAN, `allowUnauthenticated` e 429/503 non sono stati provati [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Gap evidenti] |

Per D1 la fonte cita come osservata la risposta 409 e la sostituzione di `pages/write`, ma l'origine di quel dato (task 015 e 016) è fuori dallo scope letto e la prova P non l'ha provata con token. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Gap evidenti] Le concordanze elencate sopra (forme di `{id}`, alias di `root`, clamp di `topK` e `limit`, token in tre forme) risultano coerenti anche con la prova, secondo la fonte, che però non ne dichiara il livello di prova voce per voce. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Coerente con la skill (7 voci; livello non esplicitato dalla fonte, che le elenca nel file di prova runtime)]

### Nuove differenze osservate (numerazione proposta D13-D17; D8 resta inesistente)
| Id | Skill (API v1, app 0.4.10+) | App 0.6.13 osservata il 2026-11-13 |
|---|---|---|
| D13 | `Content-Type: application/json; charset=utf-8` [^src: raw/2026-11-22-repo-llm_wiki_skill.md §API surface] | `application/json` senza `charset=utf-8` [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Osservazioni R della prova runtime (12, tutte R)] |
| D14 | Snippet di circa 160 caratteri [^src: raw/2026-11-22-repo-llm_wiki_skill.md §API surface] | Snippet di circa 110 caratteri, frontmatter compreso [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Osservazioni R della prova runtime (12, tutte R)] |
| D15 | `hybrid` quando agiscono entrambe le pipeline, score RRF 0,015-0,033 [^src: raw/2026-11-22-repo-llm_wiki_skill.md §API surface] | `hybrid` anche con `vectorHits:0` (candidati del grafo), score additivi (122, 102, 82, 42, 22, 7, 2), `keyword` con `topK` uguale o minore di 1; con embedding attivi non provato [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Osservazioni R della prova runtime (12, tutte R)] |
| D16 | `nodeType` con esempi `entity`, `concept`, `query`, `other` [^src: raw/2026-11-22-repo-llm_wiki_skill.md §API surface] | Tipi osservati in un progetto: finding, concept, source, entity, comparison, methodology, other, overview; nessun nodo `query` (assenza in un progetto, non prova di esclusione) [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Osservazioni R della prova runtime (12, tutte R)] |
| D17 | `projects[]` con `current` per progetto [^src: raw/2026-11-22-repo-llm_wiki_skill.md §API surface] | In più la chiave `currentProject`; il nome del progetto come `{id}` dà 404 [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Osservazioni R della prova runtime (12, tutte R)] |

La numerazione è una proposta del keeper, approvata nel gate di questo ingest; D13-D17 sono ritrovabili col tag `diff-skill-app`.

### Punti «non confrontabili» toccati
Del gap `llm-wiki-skill-punti-da-verificare`: durata del preflight (osservato `Max-Age: 600`), presenza di `truncated` in `files` (413 oltre `maxFiles`, `truncated` mai `true`), valori di `mode` e range degli score senza embedding, elenco parziale dei campi di `search` e valori osservati di `nodeType` risultano ristretti o chiariti con la base sopra. Restano non confrontabili: campi di `rescan` e `kind` di `changedTasks`, `Retry-After`, codice del body generico troppo grande, estensioni leggibili, default di `sourceWatchConfig`. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Osservazioni R della prova runtime (12, tutte R)]

### Affermazioni C della fonte
Le affermazioni sul codice di `e08cfce` delle fonti di alm-wiki non sono verificate: confronto e punti da verificare in [[llm-wiki-api-affermazioni-codice-da-verificare]]. La bozza della skill è descritta in [[llm-wiki-skill-bozza-alm-wiki]]. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Discrepanze skill/codice (25) con livello di prova]

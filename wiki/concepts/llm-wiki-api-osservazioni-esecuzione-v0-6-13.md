---
id: llm-wiki-api-osservazioni-esecuzione-v0-6-13
type: concept
title: API HTTP locale di llm-wiki osservata in esecuzione (app 0.6.13, prova del 2026-11-13)
status: draft
created: 2026-11-22
updated: 2026-11-22
sources: ["raw/2026-11-22-repo-alm-wiki-evidenze-api.md"]
tags: [llm-wiki, api, osservato-in-esecuzione, diff-skill-app]
---

# API HTTP locale di llm-wiki osservata in esecuzione (app 0.6.13)
> Le dodici osservazioni sull'API locale, fatte in esecuzione sull'app 0.6.13 il 2026-11-13 in un progetto locale dell'utente (alm-wiki), non riprodotte dalla factory: **una prova, un progetto, non replicata**.

## Contesto
- **Linea e provenienza:** upstream v0.6.13 (la wiki descrive il codice `e08cfce` in [[llm-wiki-api-locale]]). L'app provata è la «0.6.13» riportata da `/health`; la fonte non dice che la build coincida con `e08cfce`, e la factory non l'ha verificato. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Prova runtime del 2026-11-13 (P)]
- **Origine:** prova di un agente `general-purpose` il 2026-11-13, su un progetto reale dell'utente. Non è un `code_path` della factory e la factory non l'ha eseguita né ripetuta. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Identità e provenienza]
- **Metodo dichiarato dalla fonte:** solo chiamate GET più `POST /search`. `sources/rescan` e `pages/write` sono state chiamate solo senza token (risposta 401) e non è stata fatta nessuna scrittura. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Prova runtime del 2026-11-13 (P)]
- **Limite dichiarato:** nessun finding ha `replicated: true`. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Avvertenze della fonte]
- **Uso:** le osservazioni restringono le domande che chiedono il comportamento osservabile, ma non sono la lettura del codice e non valgono per altre versioni, progetti o configurazioni (per esempio embedding attivi).

## Dettaglio

### Osservazioni del 2026-11-13 (app 0.6.13, progetto reale, non replicate)
Colonna «Rapporto»: confronto fatto dal keeper con le pagine già in wiki (lettura del codice, [[llm-wiki-api-locale]], [[llm-wiki-sicurezza]]) e con la skill originale ([[llm-wiki-skill-api-v1-dichiarata]]); è un giudizio di lettura, non un'osservazione.

| # | Endpoint | Osservazione | Rapporto |
|---|---|---|---|
| 1 | `files` | `path` è assoluto in forma verbatim Windows (`//?/C:/.../wiki/concepts`) per tutti i root. Gli item hanno `name`, `path`, `isDir`, `size`, `children`; `size` e `children` sono `null` sulle directory con `recursive=false`. Con `root=all` compaiono 4 voci (`purpose.md`, `schema.md`, `wiki`, `sources`). Gli alias `raw` e `raw/sources` funzionano. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Osservazioni R della prova runtime (12, tutte R)] | Alias e struttura concordano; il path assoluto è un dettaglio nuovo |
| 2 | `files` | Oltre `maxFiles`: 413 con messaggio `File listing exceeds maxFiles limit (N)`; `truncated` non è mai `true`. `maxFiles=0` diventa 1, `99999` è ridotto al massimo, `abc` usa il default; `root=bogus` dà 400; `recursive=maybe` è trattato come vero. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Osservazioni R della prova runtime (12, tutte R)] | Concorda con 413 e clamp già in wiki |
| 3 | `files/content` | Più permissivo del documentato dalla skill: accetta `/` iniziale, backslash e maiuscole/minuscole diverse. Path mancante: 400 `Missing path query parameter`; `path=` vuoto: 403; file inesistente: 404 con il messaggio del sistema operativo. 403 confermato per `.llm-wiki/`, `..` (anche codificato), directory, dotfile e `%00`. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Osservazioni R della prova runtime (12, tutte R)] | I 403 concordano con la wiki; la permissività è nuova |
| 4 | `search` | `mode` vale `hybrid` anche con `vectorHits:0`. Gli score sono additivi (122, 102, 82, 42, 22, 7, 2) e non RRF (0,015-0,035). Con `topK` uguale o minore di 1 la modalità è `keyword` e `graphHits` è 0; con `topK` uguale o maggiore di 2 compaiono candidati del grafo nel `topK` (3 su 10, 15 su 50). L'ordine non è strettamente decrescente. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Osservazioni R della prova runtime (12, tutte R)] | Contraddice la skill (hybrid = keyword più vettori con RRF); la wiki aveva solo `graphHits` come campo |
| 5 | `search` | Campi non documentati dalla skill: `graphHits` al livello principale, `graphRelatedTo` sui candidati del grafo, `images` sempre `[]`. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Osservazioni R della prova runtime (12, tutte R)] | `graphHits` concorda con la wiki; gli altri due sono nuovi |
| 6 | `search` | Senza `includeContent` il campo `content` è assente (non `null`); `vectorScore` è assente senza vettori; `limit` è ignorato; un `queryEmbedding` di dimensione sbagliata è ignorato senza errore, uno vuoto, non finito o non numerico dà 400; lo snippet è di circa 110 caratteri, frontmatter compreso; `topK` 0 diventa 1, 999 diventa 50, -1 o `abc` danno 400. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Osservazioni R della prova runtime (12, tutte R)] | Il clamp concorda con la wiki; snippet e assenza di `content` e `vectorScore` sono nuovi (la skill dichiara circa 160 caratteri) |
| 7 | `projects` | Chiave `currentProject` oltre a `projects[]`. Come `{id}`: il nome del progetto dà 404; UUID, `current` e path codificato danno 200. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Osservazioni R della prova runtime (12, tutte R)] | Concorda con le tre forme di `{id}`; `currentProject` è nuovo |
| 8 | `graph` | `offset`, `limit`, `totalCount` e `hasMore` sono sempre presenti. `limit` 5000 è ridotto a 1000; 0, -1 e `abc` danno 400; `offset` -1 o `abc` dà 400; `edgeScope` non valido dà 400. Tipi di nodo reali: finding, concept, source, entity, comparison, methodology, other, overview; nessun nodo `query`. `node_type` (con trattino basso) è ignorato in silenzio; un `nodeType` inesistente dà 0 nodi; `q` non distingue le maiuscole. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Osservazioni R della prova runtime (12, tutte R)] | Paginazione ed `edgeScope` concordano con la wiki; l'assenza di nodi `query` vale per un progetto e non è una prova di esclusione |
| 9 | `reviews` | `createdAt` è un numero in virgola mobile; `sourcePath` è assoluto; `resolvedAction` è assente sulle review non risolte (non `null`); `limit=abc` è ignorato; un `type` sconosciuto dà 200 con lista vuota; `status` distingue le maiuscole (`ALL` dà 400); `pending` è riportato come `unresolved`. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Osservazioni R della prova runtime (12, tutte R)] | Nuovo; la lettura GET delle review non è in skill |
| 10 | Header | `Content-Type` è `application/json` senza `charset=utf-8`. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Osservazioni R della prova runtime (12, tutte R)] | Differisce dalla skill, che dichiara `charset=utf-8` |
| 11 | `health` | Risponde anche senza il prefisso `/api/v1` e anche con `POST`. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Osservazioni R della prova runtime (12, tutte R)] | Concorda con il doppio `/health` già in wiki |
| 12 | Errori e CORS | Senza token o con token errato: 401, anche su route inesistenti e su metodi sbagliati. Token in tre forme: `Authorization: Bearer`, `X-LLM-Wiki-Token`, `?token=`. `PUT` con token: 405. `POST` e `DELETE` su `projects` e `GET` su `search`: 404, non 405. Origini locali (localhost, 127.0.0.1, `[::1]`, `chrome-extension`, tauri): `Access-Control-Allow-Origin` riecheggia l'origine, con `Vary: Origin` e `Allow-Private-Network: true`, anche sui 401. Per `https://example.com`, `null` e `http://localhost.evil.com` l'header manca ma la richiesta è servita lo stesso. `OPTIONS`: 204 senza auth, `Max-Age: 600`. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Osservazioni R della prova runtime (12, tutte R)] | Vedi sotto |

### Sul 404 di `POST` e `DELETE` su `projects` (nessuna contraddizione con la wiki)
[[llm-wiki-api-locale]] riporta come metodi ammessi `GET`, `POST`, `PATCH` e `DELETE`, con 405 per gli altri dopo l'auth, e il match della route dopo il controllo del metodo. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Contratto API] Secondo questa lettura (deduzione del keeper), `POST` e `DELETE` su `projects` superano il controllo del metodo e non trovano la route, quindi il 404 è atteso; `PUT` è fuori dall'insieme e dà 405. L'osservazione non contraddice la wiki: restringe e conferma l'ordine dei controlli e smentisce la skill originale, che indica 405 per ogni metodo diverso da `GET` e `POST` (differenza D11 in [[llm-wiki-skill-vs-app-v0-6-13]]). Resta ambiguo se «route inesistenti» nella fonte significhi sotto `/api/v1`: fuori dal prefisso la wiki prevede 404 prima dell'auth. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Osservazioni R della prova runtime (12, tutte R)]

### Osservazioni del task 002 (2026-11-08), distinte da quelle del 2026-11-13
Prova diversa, di cinque giorni prima, con l'app aperta e il token configurato (valore non riportato). Stessa app dichiarata 0.6.13, stesso progetto di lavoro dell'utente. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Fatti R del task 002 (2026-11-08)]
- `GET /health`: `status: running`, `authConfigured: true`, `tokenSource: store`, versione 0.6.13; espone `agent.chat: true`, `agent.streamProtocol: "sse"` e `mcpEnabled: true`. La chat come funzione non è stata provata. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Fatti R del task 002 (2026-11-08)]
- `GET /projects` con token: 200; l'app ha altri progetti registrati oltre a quello di lavoro. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Fatti R del task 002 (2026-11-08)]
- `search` per UUID con `topK` 3: 200, `mode: "hybrid"` con `vectorHits: 0` e candidati dal grafo (`graphHits`, `graphRelatedTo`). [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Fatti R del task 002 (2026-11-08)]
- Il token funziona come `Bearer`. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Fatti R del task 002 (2026-11-08)]

### Voci elencate come coerenti con la skill
La fonte elenca sette voci coerenti con la skill (clamp di `topK` e `limit`, ordine degli errori 400/401/403/404/405, paginazione del grafo con `edgeScope`, alias `pending` e `raw`, token in tre forme, CORS che riecheggia le origini locali, campi di `/health`) senza dichiarare il livello di prova di ciascuna. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Coerente con la skill (7 voci; livello non esplicitato dalla fonte, che le elenca nel file di prova runtime)] Le due metà del confronto non coincidono su un punto: la fonte, altrove, dice che la paginazione del grafo è confermata dal codice ma non a runtime, mentre qui è osservata. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Confermato (CF; livello non specificato dalla fonte, salvo dove indicato)]

### Cosa questa prova non copre
Dichiarato dalla fonte come non provato: 413 e 415 sul contenuto, 429 e 503, `rtf`, scritture con token, chat (JSON, SSE, cancel), `pages/embed`, embedding attivi, bind LAN, `allowUnauthenticated`, corsa fra auto-save e review replicata. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Gap evidenti] Le prove aperte sono nel gap `llm-wiki-prove-in-esecuzione-aperte` ([[gaps]]).

### Incoerenze fra le parti della fonte (non risolte)
- Il confronto con il codice dice che `limit` del grafo fuori da 1..1000 dà 400; la prova ha osservato che 5000 è ridotto a 1000 mentre 0, -1 e `abc` danno 400. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Discrepanze skill/codice (25) con livello di prova] [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Osservazioni R della prova runtime (12, tutte R)]
- La prova dichiara che rescan e `pages/write` sono stati chiamati solo senza token, mentre il confronto riporta `pages/write` (409 e sostituzione) come osservato: la sorgente di quel dato è fuori dallo scope letto. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Gap evidenti]

## Pagine collegate
[[2026-11-22-repo-alm-wiki-evidenze-api]], [[llm-wiki-api-locale]], [[llm-wiki-sicurezza]], [[llm-wiki-skill-api-v1-dichiarata]], [[llm-wiki-skill-vs-app-v0-6-13]], [[llm-wiki-api-affermazioni-codice-da-verificare]]. Gap: [[gaps]] (`llm-wiki-skill-punti-da-verificare`, `llm-wiki-prove-in-esecuzione-aperte`).

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

---
id: llm-wiki-skill-api-v1-dichiarata
type: concept
title: API HTTP locale di llm-wiki come la documenta la skill (API v1, app 0.4.10+)
status: draft
created: 2026-11-22
updated: 2026-11-22
sources: ["raw/2026-11-22-repo-llm_wiki_skill.md"]
tags: [llm-wiki, api, skill, diff-skill-app]
---

# API HTTP locale di llm-wiki come la documenta la skill (API v1, app 0.4.10+)
> Contratto dichiarato dalla skill `llm-wiki` per «LLM Wiki API v1 as shipped in app version 0.4.10+»: documentazione, non osservazione del codice, e non descrizione dell'app v0.6.13.

## Contesto
Ogni affermazione di questa pagina vale per **quanto dichiara la skill**, riferita ad API v1 e ad app 0.4.10 o successive (etichetta «Skill»). Non è comportamento accertato di nessuna versione dell'app e non è il comportamento di v0.6.13 (`e08cfce`), descritto in [[llm-wiki-api-locale]] e [[llm-wiki-sicurezza]]. Il raw avverte che la skill è documentazione e non implementazione: non è verificabile dalla sola sorgente se i comportamenti descritti corrispondano al codice. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Gap evidenti] Le differenze con v0.6.13 sono in [[llm-wiki-skill-vs-app-v0-6-13]]. L'entità che descrive la skill è [[llm-wiki-skill]]; le incoerenze interne della skill sono numerate lì (rimando «voce n.» nel testo sotto).

## Dettaglio

### Base e endpoint
- **Skill (API v1, app 0.4.10+):** base URL `http://127.0.0.1:19828`, prefisso `/api/v1`, content type `application/json; charset=utf-8`; il contratto è etichettato «v1». [^src: raw/2026-11-22-repo-llm_wiki_skill.md §API surface]
- **Skill:** 8 endpoint. Auth non richiesta solo per `GET /health`. Sola lettura: `GET projects`, `GET projects/{id}/files`, `GET .../files/content`, `POST .../search`, `GET .../graph`. L'unica scrittura è `POST .../sources/rescan`. `POST .../chat` è uno stub che risponde 501. Altri metodi HTTP: 405. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §API surface]
- **Skill:** `{id}` accetta nel server tre forme (UUID, percorso assoluto URL-encoded, `current`). Il nome non è accettato: va risolto lato client con `GET /projects` e confronto case-insensitive per sottostringa su `name`. SKILL.md parla di «four forms» contando il nome (voce di contesto, non una incoerenza numerata). Su Windows: slash in avanti, caso conservato, `:` codificato `%3A`, e su 404 ripiego sull'UUID. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §API surface]

### `GET /health`
- **Skill:** senza auth. Campi dell'esempio: `ok`, `status` (`starting`, `running`, `port_conflict`, `error`), `version` (esempio `"0.4.x"`), `enabled`, `authRequired`, `authConfigured`, `allowUnauthenticated`, `tokenSource` (`env`, `store`, `none`; con `env` il campo token della UI è ignorato). `authRequired` è falso se e solo se `allowUnauthenticated`. Con `enabled: false` gli altri endpoint rispondono 503. Il numero di campi differisce fra i file della skill (voce n. 3). [^src: raw/2026-11-22-repo-llm_wiki_skill.md §API surface]

### `GET /projects`
**Skill:** risposta `{ok, projects[{id, name, path, current}]}`; `current` marca il progetto aperto nella UI desktop. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §API surface]

### `GET /projects/{id}/files`
**Skill:** parametri `root` (default `wiki`; `wiki`, `sources` con alias `raw` e `raw/sources`, `all` che comprende `purpose.md`, `schema.md`, `wiki/` e `raw/sources/`), `recursive` (default `true`), `maxFiles` (default 2000, clamp 1..10000, oltre: 413). Risposta `{ok, projectId, root, files[{name, path, isDir, size, children}], truncated}`, con `size` e `children` nulli dove non applicabili. File nascosti e symlink sono saltati in silenzio. Quando valga 413 e quando `truncated` non è chiaro (voce n. 2). [^src: raw/2026-11-22-repo-llm_wiki_skill.md §API surface]

### `GET /projects/{id}/files/content`
**Skill:** parametro `path` obbligatorio, relativo al progetto. Allow-list `purpose.md`, `schema.md`, `wiki/**`, `raw/sources/**`; niente segmenti dotfile né `..`. Risposta `{ok, projectId, path, content}`. Errori: 403 fuori allow-list, 404, 413 oltre 2 MB, 415 per binario o non UTF-8. Estensioni testuali accettate: md, mdx, txt, json, yaml, yml, csv, html, htm, xml, rtf, log (elencate solo in SKILL.md, voce n. 6). [^src: raw/2026-11-22-repo-llm_wiki_skill.md §API surface]

### `POST /projects/{id}/search`
- **Skill:** body con `query` (obbligatorio e non vuoto, altrimenti 400), `topK` (default 10, clamp 1..50), `includeContent` (default false), `queryEmbedding` (opzionale, array non vuoto di numeri finiti, altrimenti 400; il server salta il proprio embed). `queryEmbedding` compare solo in `api-reference.md` (voce n. 4). [^src: raw/2026-11-22-repo-llm_wiki_skill.md §API surface]
- **Skill:** risposta con `ok`, `projectId`, `mode`, `tokenHits`, `vectorHits`, `note` e `results[]`. Per risultato: `path`, `title` (frontmatter `title:`, altrimenti primo `# Heading`, altrimenti nome file), `snippet` (circa 160 caratteri), `titleMatch`, `score`, `vectorScore` (opzionale, circa 0-1, assente nei match solo keyword), `images[{url, alt}]` deduplicate per URL e `content` (solo con `includeContent`). [^src: raw/2026-11-22-repo-llm_wiki_skill.md §API surface]
- **Skill, modo di retrieval scelto dal server** in base all'`embeddingConfig` attivo e a un indice vettoriale con dati: `keyword` (nessun `embeddingConfig`, fetch dell'embedding fallito o indice vuoto; score additivo, match esatto sul nome file circa 200), `vector` (l'indice dà risultati e la keyword nessuno; score RRF `1/(60+rank)`, circa 0,015-0,017), `hybrid` (entrambe le pipeline; RRF fino a circa 0,0328). Gli score non sono confrontabili fra modi. I risultati vettoriali vengono da LanceDB. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §API surface]

### `GET /projects/{id}/graph`
**Skill:** parametri `q` (sottostringa su `id` o `label`), `nodeType` (frontmatter `type:`, per esempio `entity`, `concept`, `query`, `other`; elenco parziale in SKILL.md, voce n. 15) e `limit` (default 200, clamp 1..1000). Risposta `nodes[{id, label, nodeType, path, linkCount}]` e `edges[{source, target, weight}]`. Gli archi vengono dai `[[wikilink]]` in `wiki/*.md`, deduplicati per coppia non ordinata, self-edge scartati, `weight` 1.0 «in v1»; `linkCount` è il grado nel grafo deduplicato. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §API surface]

### `POST /projects/{id}/sources/rescan`
**Skill:** senza body. Risposta `{ok, projectId, result{queue{version, tasks}, changedTasks[{id, path, kind}]}}`. `changedTasks` elenca i file rilevati come cambiati (created, modified, deleted; nell'esempio solo `created`, voce n. 13). L'ingest è asincrono e la chiamata ritorna a diff accodato. Rispetta `sourceWatchConfig` (filtri di tipo, directory escluse, dimensione massima); con auto-ingest disattivato i file sono rilevati ma non accodati alla pipeline LLM. Il comportamento su un progetto non corrente non è chiarito (voce n. 12). [^src: raw/2026-11-22-repo-llm_wiki_skill.md §API surface]

### `POST /projects/{id}/chat`
**Skill:** risponde 501; la pipeline chat/RAG vive nella WebView in v1; la skill dice di non chiamarlo e di usare la chat desktop. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §API surface]

### Autenticazione
- **Skill:** solo localhost. Sorgenti del token in ordine: variabile `LLM_WIKI_API_TOKEN` (sovrascrive la UI), `apiConfig.token` da Settings, API Server, e la modalità `allowUnauthenticated: true` (opt-in, rara). Trasporti: `Authorization: Bearer`, `X-LLM-Wiki-Token`, `?token=` (ultima scelta: finisce nei log; elencato senza avvertenze in `api-reference.md`, voce n. 9). Token non configurato: ogni endpoint risponde 401. Con `authConfigured: false` e `allowUnauthenticated: false` l'agente deve chiedere all'utente di generare il token. Il file `api-reference.md` dichiara l'auth «sempre richiesta» senza citare `allowUnauthenticated` (voce n. 10). [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Auth, errori e limiti]
- **Skill, dipendenze:** app in esecuzione, porta 19828 sul loopback, API abilitata da Settings, API Server, «Enable local HTTP API» (default attivo), token configurato (default vuoto). [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Dipendenze esterne]

### Codici d'errore e limiti
- **Skill, codici:** 200 (da leggere anche `body.ok`); 400 (query vuota, `root` invalido, body troppo grande); 401; 403 (traversal o fuori ambito, non ritentare); 404 (progetto o rotta ignoti); 405; 413 (file oltre 2 MB, albero oltre `maxFiles`, body oltre 1 MB); 415; 429 (rate limit); 500; 501 (`/chat`); 503 (API disattivata, oppure cap in-flight con messaggio «busy»). Connessione rifiutata significa app non in esecuzione. Il body troppo grande compare sia come 400 sia come 413 (voce n. 1). [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Auth, errori e limiti]
- **Skill, limiti:**

| Limite | Valore dichiarato | Effetto |
|---|---|---|
| Body | 1 MiB | 400 (api-reference) o 413 (SKILL.md) |
| Lettura file | 2 MiB | 413 |
| Nodi albero | 10000 | 413 |
| `topK` | 50 | clamp silenzioso |
| Grafo `limit` | 1000 | clamp silenzioso |
| Rate | 120 req/s globale | 429, attendere almeno 1 s |
| In-flight | 64 | 503 «busy», attendere almeno 2 s |

[^src: raw/2026-11-22-repo-llm_wiki_skill.md §Auth, errori e limiti]
- **Skill, CORS:** `Access-Control-Allow-Origin: *`, preflight 600 s, header ammessi `Authorization`, `X-LLM-Wiki-Token` e `Content-Type`. Il rapporto fra metodi non GET/POST che danno 405 e il preflight non è chiarito (voce n. 8); `Retry-After` è «implied» e non dichiarato (voce n. 7). [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Auth, errori e limiti]

### Modello di sicurezza dichiarato
**Skill:** ascolto solo su `127.0.0.1`; confronto del token a tempo costante; traversal bloccato nel route handler (`safe_join` con prefisso del percorso canonico); letture limitate a whitelist, estensioni testuali e 2 MB; nessun endpoint di scrittura in v1. Fuori dal threat model dichiarato: un processo locale malevolo che possieda il token, `/health` senza auth (rivela solo l'esistenza dell'API) e le pagine web cross-origin (CORS `*`, affidato alla segretezza del token). [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Auth, errori e limiti]

### Sola lettura contro scrittura
**Skill:** l'unica mutazione è `sources/rescan`, che «only reads disk + queues internal work»; la skill dice di non inventare endpoint di scrittura perché «non esistono in v1». Sconsiglia le scritture dirette su `wiki/**` o `raw/sources/**` via filesystem perché aggirano il file-sync watcher, indicando l'import dalla UI o la pipeline di ingest. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Read-only vs scrittura]

### Versione dichiarata
**Skill:** il README dice che la skill corrisponde a «LLM Wiki API v1 as shipped in app version 0.4.10+», con retrieval ibrido attivo (`mode`, `tokenHits`, `vectorHits`, `vectorScore`); se `/health` riporta un «major version bump» invita a controllare `api-reference.md` per il drift. Mancano un tetto superiore, la versione su cui il contratto è stato verificato e la distinzione fra versione dell'API e versione dell'app (il campo `version` di `/health` è la versione dell'app); non c'è alcun riferimento alla serie 0.5 o successive. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Versione dichiarata]

## Pagine collegate
[[llm-wiki-skill]], [[llm-wiki-skill-vs-app-v0-6-13]], [[llm-wiki-api-locale]], [[llm-wiki-sicurezza]], [[llm-wiki-mcp-server]], [[2026-11-22-repo-llm_wiki_skill]]. Gap: [[gaps]] (`llm-wiki-skill-punti-da-verificare`, `llm-wiki-api-storia-versioni`).

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

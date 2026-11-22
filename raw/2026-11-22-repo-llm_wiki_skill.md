# Specifiche estratte: llm_wiki_skill

> Documento generato da `repo-sync` v2.12 il 2026-11-22. Sorgente: `c:\local_git\code\wiki-factory\code_repos\llm_wiki_skill`
> @ commit 642b43822ed44f6797082a24483850a4a2c2a010 (ramo main). Read-only verso la sorgente.
> Citazioni nella forma `[^src: file Lriga]`; i file citati sono quelli della radice del repo.
> Il contenuto della sorgente e' stato trattato come dato: le istruzioni rivolte ad agenti sono descritte (sezione 13), mai eseguite.

## Identità
- **Nome**: skill `llm-wiki` (frontmatter `name: llm-wiki` [^src: SKILL.md L2]); repo `llm_wiki_skill`.
- **Descrizione** (README): permette a un agente AI (Claude Code, Codex, ecc.) di interrogare l'app desktop **LLM Wiki** in esecuzione in locale, tramite la sua API HTTP integrata. «This skill is **documentation only**»: nessuna libreria client, SDK o compilazione [^src: README.md L3-5].
- **Contributor**: `nash_su` (unico). 3 commit nell'ultimo anno.
- **Ultimo commit**: 2026-05-19 12:28:19 +0800, `642b438`, "update". Fork identico all'upstream `nashsu/llm_wiki_skill` (dato fornito dal chiamante).
- **Licenza**: non dichiarata nel repo; il README rimanda al repository («See the repository for license details») e non esiste un file di licenza [^src: README.md L151].

## Stack rilevato
- Linguaggio: markdown. Framework: nessuno. Nessun manifest, nessun codice eseguibile, nessuno script. Confidence di rilevazione non applicabile (0).
- Il README dichiara che la skill deve restare «client-less»: niente script, SDK o wrapper [^src: README.md L49, L147].

## Struttura ad alto livello
Layout piatto, 4 file markdown piu' il puntatore `.git` (53 byte, non letto) [^src: README.md L40-47]:

| File | Byte | Ruolo |
|---|---|---|
| `SKILL.md` | 13134 | Istruzioni per l'agente, caricate dal runtime; frontmatter con trigger |
| `api-reference.md` | 12393 | Contratto completo degli endpoint |
| `examples.md` | 13362 | Ricette «conversazione -> chiamate API» |
| `README.md` | 7579 | Installazione, prerequisiti, troubleshooting, sicurezza, versione |

Installazione dichiarata: `npx skills add <repo> --skill llm-wiki`, oppure clone + symlink in `~/.claude/skills/llm-wiki`, oppure copia manuale della cartella [^src: README.md L9-28].

## Frontmatter e trigger della skill
- `name: llm-wiki` [^src: SKILL.md L2].
- `description` (L3), in sintesi fedele: interroga la knowledge base dell'utente tramite l'app desktop LLM Wiki a `127.0.0.1:19828`, esplicitamente «NOT Obsidian, Notion, Apple Notes, Logseq, or any other PKM tool». Copre: ricerca pagine, elenco file, lettura contenuti, navigazione del grafo, rescan delle sorgenti. «Read-only except for source rescan». Il testo contiene anche termini cinesi (知识库, 知识图谱, 重新索引) come trigger.
- **Condizioni di attivazione** [^src: SKILL.md L12-22]: l'utente nomina LLM Wiki, dice "my wiki" / "my knowledge base" / 我的知识库; chiede cosa dica la wiki su X; chiede di leggere una pagina per stem o titolo; chiede il grafo / panoramica / struttura; ha aggiunto file nella cartella sorgenti e vuole il re-ingest; dice "use my wiki for context"; nomina un progetto per ID, path assoluto o `current`.
- **Condizioni di non attivazione** [^src: SKILL.md L24-31]: "search my notes" generico, "my notebook", vault Obsidian/Notion/Roam/Logseq, Anki/Readwise/Pocket, "my files / Documents", conoscenza generale o web.
- **In dubbio** [^src: SKILL.md L33]: chiedere «Do you mean your LLM Wiki specifically, or another tool?», senza chiamare l'API di nascosto.
- Il frontmatter contiene solo `name` e `description` (nessun altro campo, es. nessun elenco di tool consentiti).

## API surface
Base URL `http://127.0.0.1:19828`, prefisso `/api/v1`, content type `application/json; charset=utf-8` [^src: api-reference.md L3-5]. Contratto etichettato «v1» [^src: SKILL.md L156].

### Tabella endpoint
| Metodo | Path | Auth | Natura |
|---|---|---|---|
| GET | `/api/v1/health` | no | read-only |
| GET | `/api/v1/projects` | si' | read-only |
| GET | `/api/v1/projects/{id}/files` | si' | read-only |
| GET | `/api/v1/projects/{id}/files/content` | si' | read-only |
| POST | `/api/v1/projects/{id}/search` | si' | read-only |
| GET | `/api/v1/projects/{id}/graph` | si' | read-only |
| POST | `/api/v1/projects/{id}/sources/rescan` | si' | **scrittura** (unica) |
| POST | `/api/v1/projects/{id}/chat` | si' | stub, risponde 501 |

Fonte: [^src: SKILL.md L156-169], [^src: api-reference.md §ogni endpoint]. Altri metodi HTTP: 405 [^src: api-reference.md L370].

### `{id}` (risoluzione del progetto)
Accetta 3 forme nel server: UUID, path assoluto URL-encoded, stringa `current`. Il **nome** non e' accettato: va risolto lato client con `GET /projects` e match case-insensitive per sottostringa su `name` [^src: api-reference.md L71-94]. SKILL.md li presenta come «four forms», contando il nome come quarto caso non supportato [^src: SKILL.md L113-120]. Esiti: 0 match -> dirlo e chiedere; 1 -> usare l'`id` e metterlo in cache; 2+ -> chiedere. Su Windows: slash in avanti, caso conservato, `:` percent-encoded (`%3A`); 404 -> ripiegare sull'UUID [^src: api-reference.md L112-119].

### GET /health
Senza auth. Campi dell'esempio: `ok`, `status` (`starting`/`running`/`port_conflict`/`error`), `version` (esempio `"0.4.x"`), `enabled`, `authRequired` (false se e solo se `allowUnauthenticated`), `authConfigured`, `allowUnauthenticated`, `tokenSource` (`env`/`store`/`none`; se `env` il campo token della UI e' ignorato). `enabled: false` -> tutti gli altri endpoint danno 503 [^src: api-reference.md L17-41].

### GET /projects
Risposta `{ok, projects[{id, name, path, current}]}`. `current` marca il progetto aperto nella UI desktop [^src: api-reference.md L45-69].

### GET /projects/{id}/files
Parametri: `root` (default `wiki`; `wiki`, `sources` con alias `raw` e `raw/sources`, `all` = `purpose.md`, `schema.md`, `wiki/`, `raw/sources/`), `recursive` (default `true`), `maxFiles` (default 2000, clamp [1, 10000], oltre -> 413). Risposta: `{ok, projectId, root, files[{name, path, isDir, size, children}], truncated}`; `size` e `children` sono `null` dove non applicabili. File nascosti e symlink sono saltati in silenzio [^src: api-reference.md L123-163].

### GET /projects/{id}/files/content
Parametro `path` obbligatorio (relativo al progetto). Allow-list: `purpose.md`, `schema.md`, `wiki/**`, `raw/sources/**`; niente segmenti dotfile, niente `..`. Risposta `{ok, projectId, path, content}`. Errori: 403 (fuori allow-list), 404, 413 (> 2 MB), 415 (binario / non UTF-8) [^src: api-reference.md L167-193]. Estensioni testuali accettate: md, mdx, txt, json, yaml, yml, csv, html, htm, xml, rtf, log [^src: SKILL.md L163].

### POST /projects/{id}/search
Body: `query` (obbligatorio, non vuoto, altrimenti 400), `topK` (default 10, clamp [1, 50]), `includeContent` (default false), `queryEmbedding` (opzionale `number[]` di numeri finiti non vuoto, altrimenti 400; il server salta il proprio embed) [^src: api-reference.md L201-217].
Risposta: `ok`, `projectId`, `mode`, `tokenHits`, `vectorHits`, `note`, `results[]`. Per risultato: `path`, `title` (frontmatter `title:`, altrimenti primo `# Heading`, altrimenti nome file), `snippet` (~160 caratteri; in vettoriale il chunk, con eventuale prefisso del percorso di heading), `titleMatch`, `score`, `vectorScore` (opzionale, ~coseno 0-1, assente nei match solo keyword), `images[{url, alt}]` (immagini `![alt](url)` deduplicate per URL), `content` (solo con `includeContent`) [^src: api-reference.md L219-271].
**Modo di retrieval** scelto dal server in base a `embeddingConfig` attivo e a indice vettoriale con dati [^src: api-reference.md L246-256]:
- `keyword`: nessun embeddingConfig, o fetch embedding fallito, o indice vuoto. Score additivo (match esatto sul nome file ~200, frase nel titolo ~50+, bag-of-token a una cifra).
- `vector`: l'indice vettoriale da' risultati ma la keyword nessuno (raro). Score RRF `1/(60+rank)` ~0.015-0.017.
- `hybrid`: entrambe le pipeline; RRF combinato fino a ~0.0328.
Gli score non sono confrontabili fra modi; usare l'ordine relativo e `vectorScore` per la forza semantica [^src: SKILL.md L102-109]. Backend: servizio di retrieval condiviso, risultati vettoriali da LanceDB [^src: api-reference.md L228].

### GET /projects/{id}/graph
Parametri: `q` (sottostringa su `id` o `label`), `nodeType` (frontmatter `type:`, es. `entity`, `concept`, `query`, `other`), `limit` (default 200, clamp [1, 1000]). Risposta: `nodes[{id, label, nodeType, path, linkCount}]`, `edges[{source, target, weight}]`. Archi dai `[[wikilink]]` in `wiki/*.md`, deduplicati per coppia non ordinata, self-edge scartati, `weight` 1.0 in v1; `linkCount` = grado nel grafo deduplicato [^src: api-reference.md L275-314].

### POST /projects/{id}/sources/rescan
Senza body. Risposta `{ok, projectId, result{queue{version, tasks}, changedTasks[{id, path, kind}]}}`. `changedTasks` = file rilevati come cambiati (created/modified/deleted); l'ingest e' asincrono e la chiamata ritorna a diff accodato. Rispetta `sourceWatchConfig` (filtri tipo, directory escluse, dimensione massima); con auto-ingest disattivato i file sono rilevati ma non accodati alla pipeline LLM [^src: api-reference.md L318-346].

### POST /projects/{id}/chat
501: pipeline chat/RAG nella WebView in v1; non chiamare, usare la chat desktop [^src: api-reference.md L350-352].

## Auth, errori e limiti
**Auth.** Solo localhost. Sorgenti del token, in ordine: variabile `LLM_WIKI_API_TOKEN` (sovrascrive la UI), `apiConfig.token` da Settings -> API Server, modalita' `allowUnauthenticated: true` (opt-in, rara) [^src: SKILL.md L73-81]. Invio: `Authorization: Bearer`, `X-LLM-Wiki-Token`, `?token=` (ultima scelta, finisce nei log) [^src: SKILL.md L83-91]. Token non configurato: ogni endpoint risponde 401 [^src: README.md L57]. Se `authConfigured: false` e `allowUnauthenticated: false` l'agente deve chiedere all'utente di generare il token [^src: SKILL.md L81].

**Codici** [^src: SKILL.md L171-188]: 200 (usare anche `body.ok`); 400 (query vuota, `root` invalido, body troppo grande); 401; 403 (traversal / fuori ambito, non ritentare); 404 (progetto o rotta ignoti); 405; 413 (file > 2 MB, albero > maxFiles, body > 1 MB); 415; 429 (rate limit); 500; 501 (`/chat`); 503 (API disattivata, messaggio con "disabled"; oppure cap in-flight, "busy"). Connessione rifiutata = app non in esecuzione.

**Limiti e difese** [^src: api-reference.md L356-370]:
| Limite | Valore | Effetto |
|---|---|---|
| Body | 1 MiB | 400 (api-reference) |
| Lettura file | 2 MiB | 413 |
| Nodi albero | 10000 | 413 |
| `topK` | 50 | clamp silenzioso |
| Grafo `limit` | 1000 | clamp silenzioso |
| Rate | 120 req/s globale | 429, attendere >= 1 s |
| In-flight | 64 | 503 "busy", attendere >= 2 s |

CORS: `Access-Control-Allow-Origin: *`, preflight 600 s, header ammessi `Authorization`, `X-LLM-Wiki-Token`, `Content-Type`.

**Modello di sicurezza dichiarato** [^src: README.md L114-127]: ascolto solo su `127.0.0.1`; confronto token a tempo costante; traversal bloccato nel route handler (`safe_join` con prefisso del percorso canonico); letture limitate a whitelist, estensioni testuali, 2 MB; nessun endpoint di scrittura in v1. Fuori dal threat model: processo locale malevolo con il token (legge tutto il progetto attivo), `/health` senza auth (rivela solo l'esistenza dell'API), pagine web cross-origin (CORS `*`, affidato alla segretezza del token).

## Read-only vs scrittura
- Unica mutazione: `sources/rescan` («only reads disk + queues internal work») [^src: README.md L121; SKILL.md L195].
- Tutto il resto e' lettura. `/chat` e' uno stub. «Don't invent write endpoints — they don't exist in v1» [^src: SKILL.md L195].
- Le scritture dirette su `wiki/**` o `raw/sources/**` via filesystem sono sconsigliate perche' aggirano il file-sync watcher; si indica l'import dalla UI o la pipeline di ingest [^src: examples.md L272].

## Cosa la skill dichiara di NON coprire
- Endpoint di scrittura (nessuno in v1) e chat/RAG (501) [^src: SKILL.md L167, L195].
- Contenuti binari o non UTF-8 (PDF, PNG): «API is text-only» [^src: api-reference.md L193].
- Paginazione dell'albero file: nessun offset o cursore [^src: examples.md L271].
- Filtro per nome progetto: assente (`?name=` non esiste) [^src: api-reference.md L79].
- Piu' di 50 risultati per ricerca [^src: examples.md L168-172]; per sweep esaustivi di stringhe esatte si suggerisce di percorrere `files` + `files/content` e fare grep lato client [^src: examples.md L172].
- Client, SDK, script, wrapper: volutamente assenti [^src: README.md L5, L49].
- Fuori dal threat model: i tre casi della sezione precedente.

## Pattern d'uso dagli esempi
Sintesi per pattern; gli snippet completi restano in `examples.md` [^src: examples.md].
1. **Nota cross-platform** (L7-24): snippet bash/jq per macOS/Linux; per Windows, equivalenti PowerShell e cmd, `curl.exe`, slash in avanti, `:` codificato.
2. **«Cosa dice la mia wiki su X»** (L28-58): `search` con `topK: 5`, `includeContent: true`; leggere `mode`; se non c'e' un vincitore netto leggere i primi 3-5; citare ogni `path`; se vuoto dirlo, senza inventare.
3. **«Leggi la pagina su X»** (L62-86): eventuale `search` con `topK: 1` per risolvere lo stem, poi `files/content`.
4. **Vicinato nel grafo** (L90-115): `graph?limit=1000` e filtro lato client su `edges`, oppure `graph?q=...`; opzionale diagramma mermaid.
5. **Panoramica** (L119-143): `files?root=wiki&recursive=true&maxFiles=500` per la struttura; lettura di `wiki/index.md`, `wiki/overview.md`, `purpose.md` per il quadro tematico.
6. **Re-index** (L147-162): `POST sources/rescan`, riportare quanti file nuovi/modificati/cancellati; se `changedTasks` e' vuoto suggerire di controllare i filtri Source Watch (l'esempio cita `.json` escluso di default).
7. **Sweep esaustivo** (L166-173): `topK: 50`, rilancio con query piu' specifica, grep lato client, uso di `vectorScore` per distinguere i match semantici.
8. **Progetto nominato / confronto fra progetti / cambio progetto** (L177-264): risolvere con `GET /projects`, id esplicito per piu' progetti (`current` e' solo l'attivo), confermare il cambio una volta.
9. **Anti-pattern** (L268-275): non chiamare `/chat`; non paginare con `maxFiles` piccoli; non scrivere via filesystem; non mettere il token nelle URL; non ritentare ciecamente su 429/503; non usare wrapper.
10. **Trascrizione end-to-end** (L279-311): health pre-flight -> search ibrida -> filtro grafo -> risposta con citazioni e concetti correlati.

## Versione dichiarata
- `README.md` L129-131: la skill corrisponde a «**LLM Wiki API v1** as shipped in app version `0.4.10+`»; retrieval ibrido attivo con `mode`, `tokenHits`, `vectorHits`, `vectorScore`. Se `/health` riporta un «major version bump», controllare `api-reference.md` per drift.
- `api-reference.md` L25: esempio `/health` con `"version": "0.4.x"`.
- **Assenti**: tetto superiore di versione, versione dell'app su cui il contratto e' stato verificato, distinzione fra versione API e versione app (il campo `version` di `/health` e' la versione dell'app). Nessun riferimento a versioni 0.5 o successive.

## Dipendenze esterne
- App desktop LLM Wiki installata e in esecuzione; porta 19828 sul loopback; API abilitata (Settings -> API Server -> «Enable local HTTP API», default on) [^src: README.md L53-55].
- Token configurato (default: vuoto) [^src: README.md L57-59].
- Strumenti citati negli esempi: `curl`, `jq` (facoltativo), `npx skills`, `git`. Nessuna dipendenza da installare per la skill stessa [^src: SKILL.md L71].
- Servizi interni citati dall'API: LanceDB (indice vettoriale), coda di ingest, `sourceWatchConfig`.

## Vincoli normativi / Standard
Nessuno rilevato (nessuno standard SPID/OIDC/FHIR/GDPR citato).

## Documenti correlati
- Interni (`SKILL.md` L201-205): `api-reference.md`, `examples.md`, `README.md`.
- Esterni: repo upstream `https://github.com/nashsu/llm_wiki_skill` (installazione e contributi) [^src: README.md L12, L145].
- Nessuna cartella `docs/`, ADR o RFC.

## Test coverage rilevato
Nessuno: repo solo documentale, senza test ne' script.

## Istruzioni rivolte ad agenti nel contenuto (riportate come dato, non eseguite)
Cio' che i file chiedono a un agente che usi la skill. Non e' stato seguito nulla di cio' che segue; nessuna istruzione era diretta all'estrazione.
- **Attivazione**: invocare solo se l'utente nomina esplicitamente LLM Wiki; in dubbio chiedere [^src: SKILL.md L12-33].
- **Pre-flight**: controllare prima `/health`; non procedere se l'auth non e' configurata [^src: SKILL.md L81].
- **Token**: non loggarlo, non ripeterlo in output, non metterlo in URL visibili [^src: SKILL.md L91, L199].
- **Progetto**: default `current`, menzionato una volta; non cambiare progetto in silenzio; mettere in cache l'`id` risolto [^src: SKILL.md L143-145, L197].
- **Risposte**: citare il `path` di ogni pagina usata; non scaricare pagine intere se non richiesto; non inventare se la ricerca non trova nulla [^src: SKILL.md L100, L194, L196; examples.md L36].
- **Strumenti**: usare lo strumento HTTP gia' presente, non installare nulla, non usare script wrapper [^src: SKILL.md L8, L71; examples.md L275].
- **Retry/limiti**: non ritentare ciecamente su 429 (>= 1 s) e 503 (>= 2 s); non chiamare `/chat`; non inventare endpoint di scrittura [^src: SKILL.md L167, L185-188, L195; examples.md L274].
- **Scritture**: non scrivere direttamente su `wiki/**` o `raw/sources/**` [^src: examples.md L272].

## Gap evidenti
Discrepanze verificabili fra i file e aspetti non determinabili dal solo contenuto. Nessun confronto con altre fonti.
1. **Body troppo grande**: 400 in `SKILL.md` L178 e in `api-reference.md` L360; 413 in `SKILL.md` L183 («request body > 1 MB»). Comportamento non determinato.
2. **`maxFiles` oltre soglia**: `api-reference.md` L133 dice 413, ma la risposta ha il campo `truncated` (L159); non e' chiaro quando valga l'uno o l'altro. `SKILL.md` L162 parla di cap a 10000 nodi con 413.
3. **Forma di `/health`**: 4 campi in `SKILL.md` L81, 8 campi in L160; l'esempio del README (L74-81) omette `version`.
4. **`queryEmbedding`**: solo in `api-reference.md` (L208, L217), assente dal body in `SKILL.md` L164.
5. **Alias `raw`, `raw/sources` di `root`**: solo in `api-reference.md` L131.
6. **Estensioni leggibili**: elencate solo in `SKILL.md` L163; gli altri file dicono genericamente «text-only».
7. **`Retry-After`**: `api-reference.md` L365 lo dice «implied»; l'header non e' dichiarato.
8. **OPTIONS vs 405**: i metodi non GET/POST danno 405 (L370) ma e' descritto un preflight CORS (L368); comportamento di OPTIONS non chiarito.
9. **`?token=`**: elencato senza avvertenze in `api-reference.md` L7-13, «last resort» che perde nei log in `SKILL.md` L88-91.
10. **Auth «sempre richiesta»**: `api-reference.md` L7 non cita `allowUnauthenticated` (`SKILL.md` L79, `README.md` L61).
11. **README**: «three markdown files» (L28) contro quattro file in tabella (L40-47); comando di update con `--skill llm_wiki_skill` (L138) contro `--skill llm-wiki` (L12) e `name: llm-wiki`.
12. **Rescan su progetto non corrente**: `examples.md` L264 afferma che le chiamate verso un id non corrente sono read-only; il rescan e' una scrittura, quindi l'affermazione non vale per esso e il comportamento non e' chiarito.
13. **`kind` di `changedTasks`**: prosa created/modified/deleted (`api-reference.md` L344), esempio solo `created`.
14. **`sourceWatchConfig`**: default (es. `.json` escluso, `examples.md` L162) non documentati altrove.
15. **`nodeType`**: elenco parziale in `SKILL.md` L150, piu' completo in `api-reference.md` L284.
16. **Licenza** assente; versione massima compatibile non dichiarata; nessuna indicazione sulla rotazione del token; valori di `status` oltre i quattro elencati non documentati.
17. Non verificabile dalla sorgente: se i comportamenti descritti corrispondano al codice dell'app. La skill e' documentazione, non implementazione.

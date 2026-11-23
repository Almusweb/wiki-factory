---
id: llm-wiki-api-affermazioni-codice-da-verificare
type: synthesis
title: Affermazioni di alm-wiki sul codice llm_wiki e08cfce, confronto con la wiki e punti da verificare
status: draft
created: 2026-11-22
updated: 2026-11-23
sources: ["raw/2026-11-23-repo-llm_wiki-residui-api-skill.md", "raw/2026-11-23-repo-llm_wiki-residui-watch-skill.md", "raw/2026-11-22-repo-alm-wiki-evidenze-api.md", "raw/2026-11-22-repo-alm-wiki-bozza-skill.md", "raw/2026-11-21-repo-llm_wiki-api-mcp.md", "raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md"]
tags: [llm-wiki, api, diff-skill-app, da-verificare]
---

# Affermazioni di alm-wiki sul codice llm_wiki e08cfce
> Le affermazioni «C» (contratto letto nel codice) delle due fonti di alm-wiki **non sono verificate dalla factory**: qui sono messe a confronto con quanto la wiki ha già da `api_server.rs` letto per intero e sono l'elenco di input di un `repo-sync` mirato su `code_repos/llm_wiki`.

## Contesto
- **Provenienza:** i `file:riga` sono scritti dalla fonte per il codice upstream v0.6.13 (commit `e08cfce`); la fonte dice di non averli verificati nel suo scope, e la factory non ha letto quel codice per questa pagina. Alcuni file sono citati senza directory (`project-file-sync.ts`, `source-lifecycle.ts`, `en.json`, `cors.rs`, `server_bind.rs`). Nei riferimenti con numeri nudi dopo il primo, la fonte non dice che siano righe dello stesso file. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Gap evidenti]
- **Abbreviazioni della fonte:** `as` = `src-tauri/src/api_server.rs`, `se` = `commands/search.rs`, `fs` = `commands/file_sync.rs`. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Come leggere questo documento]
- **Regola applicata** (da `purpose.md` e dalle regole di fiducia): una C che coincide con la wiki registra la concordanza; una C che aggiunge un fatto entra come «dichiarato dalla fonte come letto nel codice, da verificare» e non chiude gap; una C che contraddice la wiki va in `## Contradictions` della pagina impattata. Le inferenze (livello I) non entrano come fatti.
- **Chi le ha classificate:** i livelli (C, R+C, C/I, I) sono della fonte; la colonna «Rapporto con la wiki» è un confronto di lettura del keeper.

## Dettaglio

### Le 25 discrepanze skill/codice del confronto
Livelli della fonte: 15 C, 4 R+C, 3 C/I, 1 C+R (n. 20), 1 C con nota R (n. 21), 1 I (n. 22). [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Discrepanze skill/codice (25) con livello di prova]

| # | Affermazione della fonte | Livello | File:riga (fonte) | Rapporto con la wiki |
|---|---|---|---|---|
| 1 | `mode` vale `hybrid` appena `graphHits>0`, anche con `vectorHits=0`; l'RRF solo se `vectorHits>0` | R+C | `se` 782-792, 464, 684 | Nuova per il codice (`search.rs` non letto); il comportamento è osservato ([[llm-wiki-api-osservazioni-esecuzione-v0-6-13]], oss. 4) |
| 2 | Fra il 15% e il 30% della finestra dei risultati è riservato ai vicini del grafo | R+C | `se` 541-553, 682 | Nuova per il codice; osservati 3 su 10 e 15 su 50 senza vettori |
| 3 | `vectorScore` non è grezzo: chunk migliore più il 30% degli altri, limitato a 1 | C | `se` 835-836 | Nuova |
| 4 | Pesi del punteggio keyword diversi da quelli della skill (la soglia del 5% non ha prove) | C / I | `se` 14-20, 960-970 | Nuova per i pesi; la soglia è inferenza, esclusa |
| 5 | La ricerca copre solo `wiki/**/*.md`, fino a 10.000 file, e si ferma senza avvisare | C | `se` 350-369 | Nuova |
| 6 | Le pagine `type: query` sono escluse dal grafo; il tipo viene dalla prima riga `type:`, in minuscolo | C | `as` 2722-2725, 2852-2862 | Nuova; nessun nodo `query` osservato in un progetto, assenza non probante |
| 7 | Archi anche da `related:`; id = stem, percorsi relativi se c'è collisione; link ambigui scartati | C | `se` 721-770; `as` 2699-2708 | Nuova |
| 8 | `q` non restituisce i vicini (gli archi collegano solo nodi filtrati) | C | `as` 2559-2593 | Nuova |
| 9 | `limit` del grafo da 1 a 1000, fuori range 400; la stima «< 1 MB» non ha prove | C / I | `as` 2516-2521 | Nuova; **in tensione con l'osservazione** (5000 ridotto a 1000, 0 dà 400) |
| 10 | Su Windows il match del path del progetto non distingue le maiuscole e accetta `\` | C | `as` 867-875, 894-896 | **Contraddice** «path esatto» in [[llm-wiki-api-locale]] (vedi `## Contradictions`) |
| 11 | Va codificato solo `/` (come `%2F`); i due punti non creano problemi | C | `as` 458-470, 855 | Nuova; la skill dice di codificare i due punti |
| 12 | `rtf` non leggibile (415); ordine dei controlli: 403, 415 (estensione), 404, 413, 415 (UTF-8) | C | `as` 1046-1056, 956 | Concorda sul 415 per non UTF-8; il controllo dell'estensione e l'ordine sono nuovi |
| 13 | Gli esempi della skill mostrano la 0.4.x; manca `currentProject`; `/health` risponde anche senza prefisso | R+C | `as` 766-770, 308 | Concorda con il doppio `/health` già in wiki; osservato |
| 14 | Un verbo sbagliato su una route nota dà 404; il 405 solo per metodi fuori da GET, POST, PATCH, DELETE | C | `as` 393, 349-354 | Concorda con l'ordine dei controlli già in wiki; osservato |
| 15 | Mancano altri 503 (più di 8 stream chat, più di 4 embed); nessun `Retry-After`; limite su finestra di 1 s, non per `/health` né `OPTIONS` | C | `as` 254-262, 1912, 522-529, 397-420 | Concorda su 503, finestra ed esclusioni; **assenza di `Retry-After` nuova** |
| 16 | Il rescan non accoda nulla: aggiorna lo snapshot ed emette un evento; è l'interfaccia ad accodare, solo per il progetto aperto, con `enabled`, `autoIngest` e un LLM disponibile | C | `fs` 339-362, 946; `project-file-sync.ts` 62-66, 344; `source-lifecycle.ts` 268 | Nuova per il corpo di `rescan`; **in tensione** con [[llm-wiki-sincronizzazione-file]] (vedi `## Contradictions` lì) |
| 17 | Ogni cambiamento è riportato una sola volta (`changedTasks` vuoto = già visto); lo scope include anche `wiki/**/*.md`, `purpose.md`, `schema.md` | C | `fs` 784-786, 946, 664, 1135-1177 | Nuova |
| 18 | Che l'ingest parta va condizionato al progetto aperto (che i file si perdano davvero è inferenza) | C / I | come n. 16 | Come n. 16; l'inferenza è esclusa |
| 19 | Le chiamate su un `{id}` diverso da `current` non sono di sola lettura | C | `as` 360-392 | Nuova; la skill (voce n. 12 di [[llm-wiki-skill]]) non lo chiarisce |
| 20 | «Non fare POST /chat (501)» non vale più | C+R | `/health` `agent.chat: true` | Concorda con D2; osservato solo il flag |
| 21 | La skill dice che scrivere nel filesystem «bypassa il watcher»; il watcher vede le scritture manuali in `raw/sources`, quelle in `wiki/` non avviano un ingest | C (con nota R) | fonte 007 (non letta) | Nuova; la nota R è dichiarata, non verificabile qui |
| 22 | Corsa fra auto-save e review osservata una volta (2026-11-10) e non replicata | I | task 015 (non letto) | Esclusa come fatto; nota nel gap `llm-wiki-review-concorrenza-webview` |
| 23 | `allowLanAccess` letto solo all'avvio del server; `LLM_WIKI_BIND_HOST` ha la precedenza | C | `server_bind.rs` 10-31 | La precedenza e il riavvio concordano con [[llm-wiki-sicurezza]]; la riga è nuova |
| 24 | La sezione si chiama «API + MCP»; il CORS non è `*`; le scritture esistono; il README consiglia `npx skills add` in contrasto con `FORK.md` | C | `en.json` 822; `cors.rs` 11-41 | CORS e scritture concordano (D1, D4); il nome della sezione è nuovo; l'ultimo punto riguarda la skill, non l'app |
| 25 | `current` è il progetto aperto nella UI (negli script va usato l'UUID); `/projects` elenca anche progetti esterni | R+C | `as` 857-863; task 002 | Nuova per il codice; osservato |

### Altre affermazioni C della bozza della skill
Dalla sezione «When does ingest actually start» e dalle aggiunte della bozza (livello `[code]`, righe `api-reference.md` L393-407, L459, L478-479, riferimenti «verbatim» della bozza). Nessuna è verificata. [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §Riferimenti al codice dell'app (verbatim)]

| Affermazione della bozza | Riferimento nella bozza | Rapporto con la wiki |
|---|---|---|
| Il rescan non accoda; la UI accoda per il progetto aperto (o con «Watch all projects») con `enabled` e `autoIngest` e un LLM; con «Watch all projects» spento, 60 s | `file_sync.rs` 339-362; `project-file-sync.ts` 62-66 e 337-370; `source-lifecycle.ts` 258-285 | Come n. 16; il 60 s potrebbe coincidere col rescan periodico già in [[llm-wiki-sincronizzazione-file]], la bozza non lo dice |
| Cache di ingest: hash del testo; la chiave non include `schema.md`, `purpose.md` né il modello; il progresso solo in UI o in `.llm-wiki/ingest-queue.json` | `ingest-cache.ts` (senza righe) | Da confrontare con [[llm-wiki-pipeline-ingest]]; non confrontato |
| `allowLanAccess` letto all'avvio; `LLM_WIKI_BIND_HOST` | `server_bind.rs` (senza righe) | Come n. 23 |
| La UI riscrive `review.json` circa 1 s dopo i suoi cambi; id delle review FNV-1a; auto-resolve | `review-store.ts`, `sweep-reviews.ts` (senza righe) | Nuova; riguarda il gap `llm-wiki-review-concorrenza-webview` |

[^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §Differenze rispetto a raw/2026-11-22-repo-llm_wiki_skill.md]

### Affermazioni della bozza senza etichetta (anomalia A1): non entrano come fatti
La bozza dice che le frasi senza etichetta sono quelle dell'upstream, ma restano senza etichetta novità 0.6.13: la `description` della skill, le righe 0.6.13 di `SKILL.md` (L174-179), 409 e 499, quasi tutta la sezione «Additions» di `api-reference.md` (L443-559), la politica CORS 0.6.13 (L431) e `limit` 0 con risposta 400 (L425). «Additions» dichiara solo in intestazione «Source: app code at tag v0.6.13» e non è promossa a `[code]` per affermazione. [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §Anomalie e incongruenze] Alcuni di questi punti coincidono con quanto la wiki ha già (limiti di corpo 1 MiB, chat 40 MiB, `pages/write` circa 12 MiB; token sempre richiesto per `chat`, cancel, `pages/write` e `pages/embed`), ma nella bozza non hanno etichetta, quindi la coincidenza non dà alla bozza valore di prova. [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §Differenze rispetto a raw/2026-11-22-repo-llm_wiki_skill.md] Confronto con la wiki: [[llm-wiki-api-locale]] §Server HTTP.

### Contraddizioni interne alle fonti
- **Limite del grafo:** il confronto (n. 9, C) dice 400 fuori da 1..1000, la prova osserva un clamp a 1000 per 5000. In pratica il 400 vale sotto il minimo. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Discrepanze skill/codice (25) con livello di prova]
- **Paginazione del grafo:** `[obs]` in `SKILL.md` L172 e `[—]` in `api-reference.md` L555-559 della bozza; la fonte delle evidenze la dà per confermata dal codice ma non a runtime. [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §Anomalie e incongruenze]
- **Stato delle fonti di alm-wiki su `pages/write`:** il confronto la riporta come osservata (409 e sostituzione) mentre la prova del 2026-11-13 non l'ha chiamata con token. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Gap evidenti]

## Come usare questa pagina
È l'elenco di partenza di un `repo-sync` mirato su `code_repos/llm_wiki` a `e08cfce`: `search.rs` (righe citate), `file_sync.rs`, `project-file-sync.ts`, `source-lifecycle.ts`, `api_server.rs` (righe citate), `server_bind.rs`, `cors.rs`, `en.json`, `review-store.ts`, `sweep-reviews.ts`, `ingest-cache.ts`. Finché non è fatto, nessuna riga della tabella chiude un gap. Gap: `llm-wiki-affermazioni-codice-da-verificare` ([[gaps]]).

## Pagine collegate
[[2026-11-22-repo-alm-wiki-evidenze-api]], [[2026-11-22-repo-alm-wiki-bozza-skill]], [[llm-wiki-api-osservazioni-esecuzione-v0-6-13]], [[llm-wiki-skill-bozza-alm-wiki]], [[llm-wiki-api-locale]], [[llm-wiki-sicurezza]], [[llm-wiki-sincronizzazione-file]], [[llm-wiki-skill-vs-app-v0-6-13]], [[2026-11-21-repo-llm_wiki-api-mcp]].

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->
Epica LWS-EP-001 — Allineare la skill llm-wiki all'app llm_wiki v0.6.13 (fase A, PR generica upstream)
- LWS-US-002 — Bonificare la bozza come testo di partenza
- LWS-US-007 — Scritture, chat e rescan
- LWS-US-008 — Verificare sul codice i soli residui
- LWS-US-010 — Preparare la PR upstream senza tracce e senza affermazioni scoperte

## Aggiornamenti (v2026-11-22, verifica sul codice)
Dalla source page [[2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki]]: `repo-sync` ha letto il codice di `llm_wiki` a `e08cfce` (upstream v0.6.13, `develop` coincide con `main`), in sola lettura e senza eseguire nulla, per le affermazioni C elencate sopra. Il testo sopra non è modificato. **Supera** la frase «Finché non è fatto, nessuna riga della tabella chiude un gap» di §Come usare questa pagina: le righe confermate sono ora fatti letti nel codice, non più «da verificare». Escluse dal raw: n. 20, 21, 22, la soglia del 5% di n. 4 e la parte «i file si perdono» di n. 18. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Come leggere gli esiti]

### Esito per voce
| # | Esito | Cosa fa il codice (precisazione) |
|---|---|---|
| 1, 2, 3 | Confermate | `mode`, quota del grafo (0,30 senza vettori, 0,15 a finestra piena, tetto) e `vectorScore` composito: [[llm-wiki-ricerca-e-grafo-api]] |
| 4 (pesi) | Confermata | 200, 50, 20 (max 10), 5,0 e 1,0; la soglia del 5% resta fuori |
| 5 | Confermata | Solo `wiki/**/*.md`, stop al 10.001-esimo file su stderr, nessun campo di troncamento nella risposta |
| 6, 7, 8 | Confermate | Tipo dalla prima riga `type:` di tutto il file, `query` tolto, archi anche da `related:`, link ambiguo scartato, `q` non restituisce vicini |
| 9 | **Parziale** | `limit` assente 200; maggiore di 0 ridotto a `[1,1000]` (5000 diventa 1000); 400 solo per 0, negativo e non numerico; «meno di 1 MB» senza riscontro |
| 10 | Confermata | Vedi contraddizione (a) in [[llm-wiki-api-locale]] |
| 11 | **Parziale** | Si divide su `/` prima di decodificare (una `/` nell'id va codificata `%2F`); i due punti non sono separatori; «solo `/`» è troppo stretto: `?` spezza l'URL, `+` diventa spazio, `%XX` è decodificato ovunque |
| 12 | Confermata | Ordine: 404, 400, 403, 415 (estensione), 400 (`safe_join`), 404, 413, 415 (UTF-8); 11 estensioni, `rtf` esclusa |
| 13, 14, 15 | Confermate | `/health` doppio senza `currentProject` (lo ha `/projects`); 405 solo fuori da GET, POST, PATCH, DELETE; rate limit e 503; nessun `Retry-After` nei percorsi letti, con riserva sugli header SSE di successo non letti |
| 16 | **Parziale** | Il rescan non tocca la coda di ingest ma accoda nella coda Rust dei cambi e la elabora subito: «non accoda nulla» della fonte è impreciso; «solo progetto aperto» dipende da «Watch all projects» |
| 17 | Confermata | Idempotenza per hash e dimensione; scope di `should_watch_rel` |
| 18 (parte C) | **Parziale** | Condizioni di avvio dell'ingest; il ramo inattivi esiste solo con «Watch all projects» attivo |
| 19 | Confermata | Verificata su review, rescan ed embed; `handle_write_page` e `handle_chat` non letti |
| 23, 24 | Confermate | Ordine del bind; CORS con `Origin` riflesso solo se in elenco, nessun `*`; sezione «API + MCP» |
| 25 | **Parziale** | `current` è il progetto con `current` vero, impostato dalla UI via POST al clip server; «esterni» e «negli script l'UUID» non sono decisi dal codice |
[^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: ricerca (`search.rs`)] [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: API (`api_server.rs`)] [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: sincronizzazione file (Rust e UI)] [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: bind, CORS e sezione impostazioni]

Le altre affermazioni C della bozza: cache di ingest (chiave senza `schema.md`, `purpose.md` e modello) **confermata**; id delle review FNV-1a, riscrittura di `review.json` circa 1 s dopo i cambi e auto-resolve **confermati** (vedi [[llm-wiki-review-store-e-auto-save]]); `allowLanAccess` e `LLM_WIKI_BIND_HOST` **confermati**; «progresso solo in UI o in `.llm-wiki/ingest-queue.json`» **non conclusiva** per questo raw (`ingest-queue.ts` non letto; la sintesi della bozza non dice cosa intenda per «progresso»). [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: cache di ingest e review]

### Rettifica della riga «Watch all projects spento, 60 s»
La riga della tabella «Altre affermazioni C della bozza» («con "Watch all projects" spento, 60 s») riporta una sintesi del raw della bozza che è **ambigua**: il raw non porta il testo originale. La verifica sul codice conferma il comportamento «60 s solo con l'opzione accesa»: l'intervallo esiste solo in `startAllProjectFileSync`, chiamata solo con l'opzione attiva. Non è una smentita della bozza. L'ipotesi della stessa riga («il 60 s potrebbe coincidere col rescan periodico») non è sostenuta dalle posizioni nel codice (**deduzione, dalle citazioni**): il 60 s del ramo inattivi è un timer lato TS (`project-file-sync.ts:45, 123-140`), il rescan periodico del watcher (10 s su Linux, 60 s altrove) è un meccanismo Rust descritto in [[llm-wiki-sincronizzazione-file]]; il raw non li confronta. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: sincronizzazione file (Rust e UI)]

### Contraddizioni interne alle fonti
- **Limite del grafo (n. 9):** deciso dal codice, concorda con la prova in esecuzione: clamp a 1000 per i valori maggiori, 400 per 0, negativo e non numerico. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: API (`api_server.rs`)]

### Che cosa resta da verificare
Voci n. 20, 21 e 22; soglia del 5%; parte «i file si perdono» di n. 18; `handle_write_page`, `handle_chat` e `respond_chat_sse` (e gli header SSE di successo); `enqueueInactiveProjectBatch` e un eventuale controllo LLM nel ramo inattivi; chiamante di `sweepResolvedReviews`; nome del file di coda dell'ingest; cosa passano i chiamanti come `sourceContent`; quasi tutta l'anomalia A1 (novità 0.6.13 della bozza senza etichetta: sono toccati solo `limit` 0 con 400, CORS e l'esclusione di `rtf`). Gap `llm-wiki-affermazioni-codice-da-verificare`, parziale, resta aperto ([[gaps]]). [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Gap evidenti]

## Aggiornamenti (v2026-11-23, residui)
Dalle source page [[2026-11-23-repo-llm_wiki-residui-api-skill]] e [[2026-11-23-repo-llm_wiki-residui-watch-skill]]: seconda lettura del codice di `e08cfce` (upstream v0.6.13), non eseguita. Il testo sopra e la sezione precedente non sono modificati. **Supera** la sezione «Che cosa resta da verificare» per i punti sotto; ciò che i raw dichiarano «non conclusivo» o «non verificato» resta tale.

| Voce | Esito | Cosa dicono i raw |
|---|---|---|
| n. 4, soglia del 5% | **Non conclusivo** | Nel codice letto non esiste una soglia relativa del 5% (il «5» è `TITLE_TOKEN_WEIGHT=5.0`); non conclusivo solo perché `vector_search_chunks` non è letto [^src: raw/2026-11-23-repo-llm_wiki-residui-watch-skill.md §Voci V4/V20/V21/V22] |
| n. 20, «Non fare POST /chat (501)» | **Non conclusivo sulle versioni precedenti** | Nessun 501 sul percorso POST chat letto; che cosa dicessero le versioni precedenti non è decidibile dal solo commit [^src: raw/2026-11-23-repo-llm_wiki-residui-watch-skill.md §Voci V4/V20/V21/V22] |
| n. 21, scrittura esterna «bypassa il watcher» | **Smentita per il watcher; «accodate subito» non verificato** | Il watcher vede le scritture esterne; non verificato se le scritture del server API siano marcate come scritture dell'app; tempi reali non verificati [^src: raw/2026-11-23-repo-llm_wiki-residui-watch-skill.md §Voci V4/V20/V21/V22] |
| n. 22, corsa review / auto-save | **Meccanismo possibile; osservazione del 2026-11-10 non decidibile** | Vedi [[llm-wiki-review-store-e-auto-save]] [^src: raw/2026-11-23-repo-llm_wiki-residui-watch-skill.md §Voci V4/V20/V21/V22] |
| `handle_write_page`, `handle_chat`, `respond_chat_sse` | **Letti** | [[llm-wiki-api-locale]] §Aggiornamenti v2026-11-23; non conclusivi: codifica di trasferimento SSE, `approvedShellCommands` e `shellCommand` nel runtime, eventi emessi dal runtime, `normalize_wiki_write_path` [^src: raw/2026-11-23-repo-llm_wiki-residui-api-skill.md §Esiti per residuo] |
| `enqueueInactiveProjectBatch` e controllo LLM nel ramo inattivi | **Letto** | Nessun controllo LLM né parsing all'accodamento; ingest alla riapertura [^src: raw/2026-11-23-repo-llm_wiki-residui-watch-skill.md §«Watch all projects» W1-W3] |
| `stable_review_id` in Rust | **Letto in parte** | L'id stabile `review-<hex8>` è confrontato nel server API; resta non letto il chiamante di `sweepResolvedReviews` [^src: raw/2026-11-23-repo-llm_wiki-residui-api-skill.md §Esiti per residuo] |
| Anomalia A1 (novità 0.6.13 senza etichetta) | **Toccata, non chiusa** | Il codice conferma limiti di corpo per route (chat 40 MiB, `pages/write` circa 12 MiB), `limit` e `offset` del grafo e i 409/499; la classificazione dell'etichetta della bozza (upstream, nuove, inferite) non è decidibile dal codice [^src: raw/2026-11-23-repo-llm_wiki-residui-api-skill.md §Esiti per residuo] |

**Restano non letti o non decisi:** n. 22 e la parte «i file si perdono» di n. 18 (rescan HTTP su progetto non aperto); chiamante di `sweepResolvedReviews`; nome del file di coda dell'ingest; cosa passano i chiamanti come `sourceContent`; classificazione di A1. Gap `llm-wiki-affermazioni-codice-da-verificare`, parziale, resta aperto ([[gaps]]).


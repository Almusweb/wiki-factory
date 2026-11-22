---
id: llm-wiki-api-affermazioni-codice-da-verificare
type: synthesis
title: Affermazioni di alm-wiki sul codice llm_wiki e08cfce, confronto con la wiki e punti da verificare
status: draft
created: 2026-11-22
updated: 2026-11-22
sources: ["raw/2026-11-22-repo-alm-wiki-evidenze-api.md", "raw/2026-11-22-repo-alm-wiki-bozza-skill.md", "raw/2026-11-21-repo-llm_wiki-api-mcp.md"]
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

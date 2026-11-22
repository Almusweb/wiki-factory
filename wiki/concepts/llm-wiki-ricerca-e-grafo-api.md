---
id: llm-wiki-ricerca-e-grafo-api
type: concept
title: llm-wiki — ricerca ibrida e grafo dell'API, come li calcola il codice (v0.6.13)
status: draft
created: 2026-11-22
updated: 2026-11-22
sources: ["raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md"]
tags: [llm-wiki, api, ricerca, grafo, diff-skill-app]
---

# llm-wiki — ricerca ibrida e grafo dell'API (v0.6.13)
> Come `search.rs` ordina i risultati e come `api_server.rs` costruisce il grafo, letto nel codice a `e08cfce` e mai eseguito. Il contratto HTTP delle due route è in [[llm-wiki-api-locale]].

## Contesto
**Linea e provenienza:** upstream v0.6.13, commit `e08cfce` (`develop` coincide con `main`). I comportamenti sotto sono **letti nel codice, non eseguiti**; l'esecuzione osservata il 2026-11-13 su un progetto locale dell'utente (una prova, un progetto, non replicata) è in [[llm-wiki-api-osservazioni-esecuzione-v0-6-13]]. Le righe di codice sono quelle del raw; la factory non le ha rilette. Sono affermazioni che le fonti di alm-wiki davano come lette nel codice: qui sono verificate sul codice dal `repo-sync` mirato ([[2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki]]). [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Come leggere gli esiti]

## Dettaglio

### Ricerca (`search.rs`)
- **Valore di `mode`:** `hybrid` se i candidati del grafo sono più di zero, anche con zero risultati vettoriali; altrimenti `keyword` se i risultati vettoriali sono zero, `vector` se i token non hanno rank, `hybrid` negli altri casi. La fusione RRF si applica solo se i risultati vettoriali sono più di zero. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: ricerca (`search.rs`)]
- **Quota di slot dei vicini del grafo:** ratio 0,30 senza vettori, 0,15 a finestra piena di vettori, interpolata su `min(vector_hits, limit) / limit`; arrotondata per eccesso, limitata a `[1, limit-1]` e pari a 0 se `limit` è minore di 2. È un tetto: i candidati sono troncati alla quota, e senza vicini gli slot restano a keyword e vettori. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: ricerca (`search.rs`)]
- **`vectorScore`:** per pagina è il chunk migliore più `min(0,3 x somma degli altri chunk, max(1 - migliore, 0))`; con il migliore minore o uguale a 1 il risultato non supera 1, quindi non è un coseno grezzo. Il campo è copiato nel risultato solo quando l'RRF è applicato, oppure per i risultati solo-vettore. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: ricerca (`search.rs`)]
- **Punteggio keyword:** 200 per nome file esatto, 50 per la frase nel titolo, 20 per ogni occorrenza della frase nel contenuto (massimo 10 occorrenze), più 5,0 volte il punteggio dei token del titolo e 1,0 volte quello dei token del contenuto. La soglia del 5% della fonte non è nel raw (esclusa come inferenza). [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: ricerca (`search.rs`)] [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Come leggere gli esiti]
- **Copertura:** enumera con `WalkDir` solo `wiki/`, file con estensione `md` senza distinzione di maiuscole. Al 10.001-esimo file stampa «stopped scanning wiki» su stderr ed esce dal ciclo. La risposta (`mode`, `tokenHits`, `vectorHits`, `graphHits`, `results`) non ha campi di troncamento, quindi il chiamante non vede che la scansione si è fermata. `WalkDir` non ha ordinamento: il raw dice di non sapere quali file restino fuori. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: ricerca (`search.rs`)]
- **Link del grafo nella ricerca:** `extract_graph_links` aggiunge ai wikilink i valori di `related:` (forma `[a, b]` e forma a elenco). Nel blend dei vicini gli alias in collisione si sovrascrivono (vince l'ultimo inserito) e non vengono scartati: è diverso dal grafo dell'API, dove il link ambiguo è scartato. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: ricerca (`search.rs`)]
- Il raw non riporta la costante dell'RRF né il comportamento di `resolve_query_embedding`: la scala degli score con embedding attivi non è decisa da questa lettura (punto aperto del gap `llm-wiki-skill-punti-da-verificare`).

### Grafo (`api_server.rs`)
- **Tipo del nodo:** `extract_type` prende la prima riga (`trim`) che inizia con `type:` in tutto il file, non solo nel frontmatter, toglie gli apici e porta in minuscolo; il default è `other`. Quindi i valori di `nodeType` sono un insieme aperto, non un elenco chiuso. I nodi di tipo `query` sono tolti prima di risolvere i link. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: API (`api_server.rs`)]
- **Archi e id:** gli archi vengono dai link estratti da `extract_graph_links`, quindi anche da `related:`. L'id del nodo è lo stem se è unico, altrimenti il percorso relativo a `wiki/` senza estensione. Gli alias in collisione diventano `None` e `resolve_link` restituisce `None` senza provare il livello successivo: il link ambiguo è scartato. Gli archi sono deduplicati senza direzione. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: API (`api_server.rs`)]
- **Filtro `q` ed `edgeScope`:** `q` filtra per sottostringa (minuscolo) su id o etichetta. Gli archi restituiti hanno la sorgente nella pagina e il target nella pagina (`edgeScope` assente o `page`), oppure fra i nodi filtrati anche fuori pagina (`edgeScope=filtered`). I vicini non filtrati non sono mai restituiti come nodi. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: API (`api_server.rs`)]
- **`limit`:** assente vale 200; numerico maggiore di 0 viene ridotto a `[1, 1000]` (5000 diventa 1000 e non dà 400); 0, negativo o non numerico dà 400. «Fuori range 400» vale quindi solo per 0 e non numerici. La stima «meno di 1 MB» della fonte non ha riscontro nel codice letto. Concorda con le osservazioni in esecuzione già in wiki (5000 ridotto a 1000, 0 dà 400). [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Esiti: API (`api_server.rs`)]

## Limiti
Lettura statica, nessuna esecuzione. Non sono coperti da questo raw: `offset`, `totalCount` e `hasMore` del grafo, la cache di 5 s, la scala RRF e `resolve_query_embedding`. Il comportamento a runtime dipende da impostazioni e dati del progetto, non verificabili dal solo codice. [^src: raw/2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki.md §Gap evidenti]

## Pagine collegate
[[llm-wiki-api-locale]], [[llm-wiki-api-osservazioni-esecuzione-v0-6-13]], [[llm-wiki-skill-vs-app-v0-6-13]], [[llm-wiki-api-affermazioni-codice-da-verificare]], [[2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki]]. Gap: [[gaps]] (`llm-wiki-skill-punti-da-verificare`, `llm-wiki-api-corpi-handler-non-letti`).

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

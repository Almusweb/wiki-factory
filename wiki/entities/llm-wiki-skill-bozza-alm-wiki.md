---
id: llm-wiki-skill-bozza-alm-wiki
type: entity
title: Bozza di riscrittura della skill llm-wiki allineata all'app 0.6.13 (alm-wiki)
status: draft
created: 2026-11-22
updated: 2026-11-22
sources: ["raw/2026-11-22-repo-alm-wiki-bozza-skill.md"]
tags: [llm-wiki, entity, skill, bozza, diff-skill-app]
---

# Bozza di riscrittura della skill llm-wiki (alm-wiki)
> Testo candidato, scritto da un modello nel repo locale dell'utente (alm-wiki) per portare la skill `llm-wiki` all'app 0.6.13, con etichette `[obs]` e `[code]`: **non è una fonte di fatti sull'app** e non va confusa con la skill originale.

## Contesto
**Linea e provenienza:** cartella di 5 file markdown nel repo locale dell'utente (non un `code_path` della factory), ramo `main`, commit del repo `050f023`; ultimo commit sulla cartella `26406be` del 2026-11-13, «docs(skill): llm-wiki fork aligned with app 0.6.13 using only proven facts», senza modifiche locali. Il confronto è con l'originale `llm_wiki_skill` a `642b438`, descritto in [[llm-wiki-skill]]. [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §Identita']
**Perché una pagina a parte:** [[llm-wiki-skill]] descrive la linea upstream (originale, API v1, app 0.4.10+); questa bozza è un testo di un'altra linea e mescolarla violerebbe la regola di provenienza di `purpose.md`. I fatti sull'app che la bozza riporta entrano in wiki attraverso le pagine di evidenza ([[llm-wiki-api-osservazioni-esecuzione-v0-6-13]], [[llm-wiki-api-affermazioni-codice-da-verificare]]), non da qui.

## Dettaglio

### Identità
Riscrittura locale, fatta da un modello, della skill `llm-wiki`; dichiara di documentare l'app 0.6.13 mentre l'originale dichiara «API v1, app 0.4.10+». Dimensioni in byte (bozza, tra parentesi l'originale): `SKILL.md` 17812 (13134), `api-reference.md` 26709 (12393), `examples.md` 16083 (13362), `README.md` 9518 (7579); `FORK.md` 4521 è nuovo, in italiano, senza equivalente nell'originale. [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §Identita']

### Etichette di prova e loro limite
`[obs]` indica osservato sull'app 0.6.13 il 2026-11-13; `[code]` indica letto nel codice al tag `v0.6.13` (commit `e08cfce`), non osservato. La bozza dice che le frasi senza etichetta vengono dalla skill upstream e valgono ancora; le inferenze sono escluse. L'equivalenza fra tag e commit è asserita dalla bozza. L'etichetta chiude la frase che la porta, e la fonte non promuove nessuna `[code]` a `[obs]`. [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §Etichette di prova e loro limite]

### Cosa aggiunge rispetto all'originale
173 affermazioni cambiate rispetto all'originale (aggiunte, cambiate o tolte): 60 `[obs]`, 51 `[code]`, 6 con entrambe le etichette, 56 senza etichetta; per file: `SKILL.md` 50, `api-reference.md` 77, `examples.md` 30, `README.md` 16. Le tabelle per file stanno nel raw e non sono ripetute qui. [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §Differenze rispetto a raw/2026-11-22-repo-llm_wiki_skill.md] In sintesi, per tema:
- **Versione e ambito:** dichiara 0.6.13; la `description` passa da «read-only except for source rescan» a «read-only by default», con scritture, gestione delle review, `pages/write`, `pages/embed` e chat agente dopo conferma esplicita; la sezione Settings diventa «API + MCP». [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §SKILL.md]
- **Ricerca:** guardare `vectorHits` e `graphHits` e non solo `mode`; `hybrid` anche senza vettori; score additivi senza vettori e RRF solo con `vectorHits>0`; `vectorScore` composito; campi `graphHits` e `graphRelatedTo`; ricerca solo su `wiki/**/*.md`. [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §SKILL.md]
- **Grafo:** `offset`, `limit`, `totalCount`, `hasMore`, `edgeScope`; `nodeType` in camelCase, `node_type` ignorato; archi anche da `related:`; le pagine `type: query` non sono nodi; `q` filtra solo i nodi. [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §api-reference.md]
- **Progetti e file:** `currentProject`; negli script usare l'UUID; path assoluti `//?/C:/...`; 413 oltre `maxFiles`; `files/content` più permissivo e senza `rtf`. [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §api-reference.md]
- **Rescan e ingest:** il rescan non dimostra che l'ingest sia in coda; sezione «When does ingest actually start»; cache di ingest; watcher sui file esterni in `raw/sources`. [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §api-reference.md]
- **Errori e rete:** 404 anche per verbo sbagliato su route nota, 405 solo fuori dall'insieme dei verbi, 409, 499, 429 senza `Retry-After`, 503 anche per più di 8 stream di chat o più di 4 embed; CORS con `Origin` riflesso solo per origini locali; bind letto all'avvio. [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §api-reference.md]
- **Endpoint nuovi:** `reviews` (lettura e mutazioni), `pages/write`, `pages/embed`, `chat` con SSE e cancel, paginazione del grafo, descritti quasi del tutto senza etichetta (vedi A1). [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §api-reference.md]
- **`FORK.md`:** elenco delle modifiche per file, revisione del 2026-11-13 (task 038), definizione delle etichette, procedura di riallineamento e avvertenza di non rilanciare l'installazione dall'originale; è contenuto della fork locale, non della skill. [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §FORK.md (nuovo, 68 righe)]

### Elementi non trasferibili a una PR upstream
- `FORK.md` per intero: riferimenti ai task interni dell'utente, a cartelle di lavoro, a un percorso locale reale dell'utente e alla fonte circolare delle sue note. [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §Elementi non trasferibili a una PR upstream]
- Le etichette `[obs]` e `[code]` e le loro legende (`SKILL.md`, `api-reference.md`, `examples.md`, `README.md`); l'avviso di fork e le istruzioni «non da eseguire su questa copia». [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §Elementi non trasferibili a una PR upstream]
- Dati di un progetto reale in una data: gli score di esempio 122, 102 e 82, «Values seen on a real wiki», le fonti accodate il 2026-11-13, «seen once», id e timestamp dell'esempio di review. [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §Elementi non trasferibili a una PR upstream]
- Da valutare: la `description` estesa cambia il trigger e non ha etichetta. [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §Elementi non trasferibili a una PR upstream]
- La fonte dichiara che negli esempi non compaiono nomi del progetto reale né dell'utente. [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §Elementi non trasferibili a una PR upstream]

### Anomalie A1-A5 (della fonte)
- **A1:** la regola «senza etichetta = upstream» e la dichiarazione di FORK.md «ognuno con un'etichetta» sono contraddette dalle novità 0.6.13 senza etichetta (`description`, righe 0.6.13 di `SKILL.md`, 409 e 499, quasi tutta «Additions», CORS 0.6.13, `limit` 0 con 400). [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §Anomalie e incongruenze]
- **A2:** stesso fatto con etichette diverse (paginazione del grafo, lettura delle review, `agent.chat`). [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §Anomalie e incongruenze]
- **A3:** FORK.md esclude le inferenze, ma il rischio di sovrascrittura delle review è in `api-reference.md` come «seen once and not replicated» senza etichetta, e le premesse del rescan sono `[code]` senza la conclusione; `limit` del grafo è marcato «0.4.x only» in FORK.md ma emendato nella riga senza marcarla. [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §Anomalie e incongruenze]
- **A4:** cambi che contraddicono l'originale (scala dello score per `vectorHits`, `hybrid` senza vettori, risultati non strettamente ordinati, `vectorScore` non coseno, `type: query` non è nodo, 429 senza `Retry-After`, «No write endpoints in v1» sostituito) e incongruenze ereditate non corrette («four forms», corpo oltre 1 MB che dà 400 e 413, «three markdown files», `--skill llm_wiki_skill` contro `llm-wiki`). [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §Anomalie e incongruenze]
- **A5:** le istruzioni per agenti nella bozza (trigger, «Never log or echo the token», «Non rilanciare `npx skills add`») sono descritte e non eseguite; nessuna anomala; nessun segreto (placeholder). [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §Anomalie e incongruenze]

### Uso consigliato (proposta del keeper)
Come testo di partenza per la PR upstream della skill alla 0.6.13 ([[llm-wiki-skill-vs-app-v0-6-13]]): le affermazioni `[obs]` si appoggiano alla prova del 2026-11-13 (una prova, un progetto, non replicata); le `[code]` restano da verificare nel codice ([[llm-wiki-api-affermazioni-codice-da-verificare]]); le senza etichetta non si portano alla PR finché non sono classificate. I riferimenti al codice della bozza non sono verificati. [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §Gap evidenti]

## Pagine collegate
[[2026-11-22-repo-alm-wiki-bozza-skill]], [[llm-wiki-skill]], [[llm-wiki-skill-api-v1-dichiarata]], [[llm-wiki-skill-vs-app-v0-6-13]], [[llm-wiki-api-osservazioni-esecuzione-v0-6-13]], [[llm-wiki-api-affermazioni-codice-da-verificare]]. Gap: [[gaps]] (`llm-wiki-affermazioni-codice-da-verificare`).

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

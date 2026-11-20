---
id: 2026-11-20-repo-llm_wiki
type: source
title: Specifiche estratte da code_repos/llm_wiki (repo-sync)
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: ["raw/2026-11-20-repo-llm_wiki.md", "raw/images/2026-11-20-repo-llm_wiki-tree.md", "raw/2026-11-20-repo-llm_wiki-persistenza-b.md", "raw/2026-11-20-repo-llm_wiki-persistenza-c.md"]
tags: [source, repo, llm-wiki]
---

# Specifiche estratte da code_repos/llm_wiki (repo-sync)
> Estrazione `partial` di `code_repos/llm_wiki` (ramo `develop`, commit `e08cfce`): 30 file campionati su 476.

## Contesto
Il raw primario è stato prodotto da `repo-sync` v2.12 il 2026-11-20 dalla sorgente `code_repos/llm_wiki`, in sola lettura. Il repository scansionato è di terzi, sotto GNU General Public License v3.0. [^src: raw/2026-11-20-repo-llm_wiki.md §Specifiche estratte: llm-wiki]

## Dettaglio

### Metadati dell'estrazione
- Sorgente: `code_repos/llm_wiki`, ramo `develop`, commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3`; estrattore `repo-sync@2.12.0`; estratto il 2026-11-20 alle 15:28 (+01:00). [^src: raw/2026-11-20-repo-llm_wiki.md §Specifiche estratte: llm-wiki]
- File campionati: 30 su 476 (cap di 30 file, 50 KB per file). [^src: raw/2026-11-20-repo-llm_wiki.md §Note di estrazione]
- Esito: **partial**. Motivo: cinque file ad alto valore (`agent/runtime.rs`, `agent/tools.rs`, `api_server.rs`, `commands/fs.rs` e `ingest.ts` oltre la riga 70) superano i 50 KB e sono descritti solo tramite nomi e file vicini; `lib.rs` è letto in parte; 446 file non sono stati campionati; non c'è stata scansione dei sorgenti alla ricerca di credenziali hardcoded. [^src: raw/2026-11-20-repo-llm_wiki.md §Note di estrazione]
- Secret redatti: 0. Il valore vale per i 30 file letti e per la ricerca dei nomi file: non esiste una scansione dei sorgenti non aperti. [^src: raw/2026-11-20-repo-llm_wiki.md §Note di estrazione]
- Istruzioni nei file letti: il raw riporta nessuna ostile (comandi di installazione e consigli per utenti umani, un invito in `llm-wiki.md`, note per i contributor nei commenti Rust) e nessuna è stata eseguita. [^src: raw/2026-11-20-repo-llm_wiki.md §Note di estrazione]
- Il raw descrive il codice con parole proprie e riporta solo nomi, simboli e firme, senza frammenti di codice. [^src: raw/2026-11-20-repo-llm_wiki.md §Specifiche estratte: llm-wiki]

### Artefatti
- Primario: `raw/2026-11-20-repo-llm_wiki.md`.
- Companion: [albero filesystem a depth 3](../../raw/images/2026-11-20-repo-llm_wiki-tree.md), 41 directory. [^src: raw/images/2026-11-20-repo-llm_wiki-tree.md §Albero filesystem — llm_wiki (depth 3)]

### Pagine ricavate
- [[llm-wiki-app]] — identità e funzioni dichiarate in README.
- [[pattern-llm-wiki]] — il pattern su cui si basa l'applicazione.
- [[llm-wiki-struttura-e-moduli]] — layout, entrypoint, moduli.
- [[llm-wiki-stack-e-dipendenze]] — stack, dipendenze, toolchain.
- [[llm-wiki-api-locale]] — API HTTP locale, clip server, comandi Tauri.
- [[llm-wiki-mcp-server]] — strumenti del server MCP.
- [[llm-wiki-agente]] — modulo agente, permessi, router.
- [[llm-wiki-sicurezza]] — bind, CORS, estensione, Tauri.
- [[llm-wiki-schema-dati]] — dati su file, tipi, indice vettoriale.
- [[llm-wiki-licenza-e-standard]] — licenza e standard citati.
- [[llm-wiki-test-e-ci]] — test e CI.

### Gap aperti da questa sorgente
Il raw elenca i propri gap nella sezione «Gap evidenti»; sono stati aperti in [[gaps]] con prefisso `llm-wiki-`. [^src: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti]

## Estratto non promosso a pagina
Nessun contenuto del raw è stato scartato. Le sezioni sono confluite nelle pagine sopra.

## Pagine collegate
[[llm-wiki-app]], [[gaps]]

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

## Aggiornamenti (v2026-11-20)
Questa pagina riporta sopra «30 su 476» file campionati e 30 file per il valore di zero secret: sono i valori della prima estrazione, superati dall'aggiornamento seguente.

### Seconda estrazione (layer di persistenza)
- Sorgente: stesso commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3`, ramo `develop`. Il manifest dà `extracted_at` 2026-11-20T16:58:00+01:00 e `files_sampled: 50`; il raw aggiunge in coda la sezione `## Aggiornamenti (v2026-11-20)`, senza modificare le precedenti. [^src: raw/2026-11-20-repo-llm_wiki.md §Premessa e perimetro]
- Campione di questo giro: 21 file, tutti sotto 50.000 byte (circa 357 KB). Il cumulativo di 50 è la somma dei 30 della prima estrazione e dei 20 nuovi: `src/types/wiki.ts` era già stato letto ed è l'unico overlap verificabile; se il campione precedente contenesse altri file di questo giro, il valore reale sarebbe leggermente inferiore. [^src: raw/2026-11-20-repo-llm_wiki.md §Premessa e perimetro]
- Non letto per limite di dimensione: `src-tauri/src/commands/file_sync.rs` (70 KB). [^src: raw/2026-11-20-repo-llm_wiki.md §Premessa e perimetro]
- Segreti redatti: 0; nessun file `.env*` e nessun valore di credenziale in chiaro nei 21 file. Limite invariato: nessuna scansione testuale dei sorgenti non aperti. Istruzioni trovate nei file letti: nessuna. Stato complessivo: **partial**. [^src: raw/2026-11-20-repo-llm_wiki.md §Note di estrazione dell'update]

### Pagine ricavate dall'aggiornamento
- [[llm-wiki-archivi-persistenza]] — inventario dei 17 archivi e chiavi di `app-state.json`.
- [[llm-wiki-versioni-e-migrazioni]] — versioni di formato e migrazioni.
- [[llm-wiki-operazioni-distruttive]] — operazioni distruttive, innesco e salvaguardie.
- [[llm-wiki-gestione-file-corrotti]] — comportamento sui file corrotti.
- [[llm-wiki-rischi-persistenza]] — divergenze e rischi (deduzioni).
- Pagine aggiornate: [[llm-wiki-schema-dati]], [[llm-wiki-sicurezza]], [[llm-wiki-stack-e-dipendenze]], [[llm-wiki-test-e-ci]].

### Gap aperti dall'aggiornamento
Dalla sezione `### Gap` dell'aggiornamento sono stati aperti in [[gaps]]: `llm-wiki-persistenza-codice-non-letto`, `llm-wiki-file-citati-non-verificati`, `llm-wiki-app-state-percorso`, `llm-wiki-creazione-cartella-dati`, `llm-wiki-vector-v1-chiamanti`, `llm-wiki-log-index-formato`, `llm-wiki-archivi-dimensioni`. Dalla sezione `### Divergenze e rischi`: `llm-wiki-embedding-cambio-modello`. I 12 gap della prima estrazione restano aperti. [^src: raw/2026-11-20-repo-llm_wiki.md §Gap]

### Correzione di percorso
Dove il raw cita `fs.rs` come non letto, il percorso corretto segnalato dall'estrattore è `src-tauri/src/commands/fs.rs`. Il raw non è stato modificato; la correzione vale in wiki.

### Estrazioni mirate successive (fette A, B e C)
Sullo stesso commit `e08cfce` sono seguite tre estrazioni mirate sulla persistenza, ognuna con una propria pagina: [[2026-11-20-repo-llm_wiki-persistenza-a]] (store e configurazioni), [[2026-11-20-repo-llm_wiki-persistenza-b]] (scritture, sincronizzazione, log e indice) e [[2026-11-20-repo-llm_wiki-persistenza-c]] (cancellazioni e chiamanti). Il testo sopra non è modificato; i valori cumulativi dei file campionati sono riportati nelle pagine delle fette, con la riserva che sono un massimo non verificabile. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Copertura del gap `llm-wiki-persistenza-codice-non-letto`]

Due frasi sopra sono toccate dalle fette: «Non letto per limite di dimensione: `file_sync.rs` (70 KB)» (ora letto alle righe 1-444 e 1290-1409, vedi [[llm-wiki-sincronizzazione-file]]) e «inventario dei 17 archivi» (la fetta B trova archivi non presenti nell'inventario e non corregge né conferma il conteggio, vedi [[llm-wiki-archivi-persistenza]]). [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Sincronizzazione e osservazione dei file]

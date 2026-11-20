---
id: 2026-11-20-repo-llm_wiki
type: source
title: Specifiche estratte da code_repos/llm_wiki (repo-sync)
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: ["raw/2026-11-20-repo-llm_wiki.md", "raw/images/2026-11-20-repo-llm_wiki-tree.md"]
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

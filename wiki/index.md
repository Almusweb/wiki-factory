---
id: index
type: index
title: Wiki Index
status: draft
created: 2026-11-20
updated: 2026-11-23
sources: []
tags: [navigation]
---

# Wiki Index

Indice delle pagine di `wiki/`, aggiornato da `wiki-keeper` a ogni ingest.

## Sources
- [[2026-11-20-repo-llm_wiki]] — specifiche estratte da `code_repos/llm_wiki` (`repo-sync`, estrazione partial; seconda estrazione sulla persistenza)
- [[2026-11-20-repo-llm_wiki-persistenza-a]] — fetta A della persistenza: store `app-state.json`, cartella dati, tipi delle configurazioni, lettori backend
- [[2026-11-20-repo-llm_wiki-persistenza-b]] — fetta B della persistenza: scritture e atomicità, sincronizzazione file, log e indice
- [[2026-11-20-repo-llm_wiki-persistenza-c]] — fetta C della persistenza: chiamanti delle operazioni distruttive, cancellazioni, `append_turn`, v1
- [[2026-11-21-repo-llm_wiki-api-mcp]] — estrazione 2026-11-21 fetta A: `api_server.rs` per intero, API HTTP locale, MCP, bind e autenticazione
- [[2026-11-21-repo-llm_wiki-agente-runtime]] — estrazione 2026-11-21 fetta B1: `agent/runtime.rs`, approvazione shell, sessioni e id
- [[2026-11-21-repo-llm_wiki-agente-tools]] — estrazione 2026-11-21 fetta B2: registry dei tool, `shell.exec`, serde delle config, `write_wiki_page_verified`
- [[2026-11-21-repo-llm_wiki-fs-lib-progetto]] — estrazione 2026-11-21 fetta C1: comandi FS, `lib.rs`, layout del progetto, identità e import
- [[2026-11-21-repo-llm_wiki-ingest]] — estrazione 2026-11-21 fetta C2: pipeline di ingest, coda, cache, formati, cancellazione lato TypeScript
- [[2026-11-21-repo-llm_wiki-ricerca-ui-residui]] — estrazione 2026-11-21 fetta E: embedding, i18n, CI e build, impostazioni, id, revisioni e sessioni
- [[2026-11-21-repo-llm_wiki-persistenza-d]] — estrazione 2026-11-21 fetta D: percorso e file corrotto di `app-state.json` per sistema operativo, atomicità dei sette archivi senza riga di codice
- [[2026-11-21-repo-llm_wiki-dossier-ep004-r1]] — dossier EP-004 r1 (2026-11-21): rischio 1, percorso cancella-salva-carica delle chat, esito non conclusivo per lettura
- [[2026-11-21-repo-llm_wiki-dossier-ep004-r2]] — dossier EP-004 r2 (2026-11-21): rischio 2, rigenerazione dell'identità del progetto, esito confermato per lettura
- [[2026-11-21-repo-llm_wiki-dossier-ep004-r3]] — dossier EP-004 r3 (2026-11-21): rischio 3, scritture sul registro dei progetti, esito confermato per lettura sul meccanismo e non conclusivo sulla concorrenza reale
- [[2026-11-21-repo-llm_wiki-dossier-ep004-r4]] — dossier EP-004 r4 (2026-11-21): rischio 4, atomicità eterogenea delle scritture, confermato per lettura sul meccanismo (scrittura diretta o temporaneo e rinomina per archivio, finestra Windows in `save_revision`, `write_json` e `index.md`), smentite due ipotesi del TSK, non conclusivo su file system, `rename` su Windows e LanceDB
- [[2026-11-21-repo-llm_wiki-dossier-ep004-r5]] — dossier EP-004 r5 (2026-11-21): rischio 5, logica duplicata TS e Rust, chunking confermato diverso per lettura, pulizia id legacy non conclusiva, invalidazione dell'impronta confermata
- [[2026-11-21-repo-llm_wiki-dossier-ep004-r6]] — dossier EP-004 r6 (2026-11-21): rischio 6, re-index senza rollback, confermato per lettura (tabella assente o parziale dopo lo svuotamento, rilancio da zero, un solo innesco), non conclusivo sullo stato su disco dopo errore parziale
- [[2026-11-21-repo-llm_wiki-dossier-ep004-r7]] — dossier EP-004 r7 (2026-11-21): rischio 7, cambio di modello o dimensione dell'embedding, confermato per lettura (nessun confronto con la tabella, `embedAllPages` non rileva il cambio, nessun avviso al salvataggio, impronta con modello), non conclusivo sul comportamento di LanceDB
- [[2026-11-21-repo-llm_wiki-dossier-ep004-r8]] — dossier EP-004 r8 (2026-11-21): rischio 8, segreti in chiaro nello store applicativo, confermato per lettura (15 campi sensibili scritti così come sono, nessuna cifratura né archivio protetto, token API in HTTP sulla LAN, chiave SerpApi nell'URL), non conclusivo su permessi del file, SerpApi negli errori e copie fuori dallo store
- [[2026-11-21-issues-llm_wiki-chiuse]] — issue chiuse di `nashsu/llm_wiki` (2026-11-21, `github-issues`): dichiarazioni di segnalatori e maintainer con la versione, più controlli puntuali su v0.6.13; Clip server (bind, CORS e token osservati, corpo senza limite, `projectPath` non confrontato col registro, loopback senza token), misure di terzi sulle dimensioni, regole di `page_id` e confronto degli id TS e Rust, stato dei sei punti di #318
- [[2026-11-22-repo-llm_wiki_skill]] — estrazione 2026-11-22 di `code_repos/llm_wiki_skill` (`main`, `642b438`): skill per agenti sull'API HTTP locale, documentazione dichiarata per API v1 e app 0.4.10+
- [[2026-11-22-repo-alm-wiki-evidenze-api]] — estrazione 2026-11-22 da alm-wiki (progetto locale dell'utente, `partial`, 5 file): prova in esecuzione dell'API 0.6.13 del 2026-11-13 (una prova, un progetto, non replicata), confronto skill/codice con livelli R/C/I, prove aperte
- [[2026-11-22-repo-alm-wiki-bozza-skill]] — estrazione 2026-11-22 da alm-wiki: bozza di riscrittura della skill `llm-wiki` per l'app 0.6.13, testo candidato con etichette `[obs]` e `[code]` e 173 differenze rispetto all'originale
- [[2026-11-22-repo-llm_wiki-verifica-affermazioni-alm-wiki]] — estrazione 2026-11-22 di `code_repos/llm_wiki` (`e08cfce`, `partial`, 17 file): verifica sul codice delle affermazioni C di alm-wiki (24 confermate, 6 parziali, 1 non conclusiva) e decisione delle due contraddizioni aperte
- [[2026-11-23-repo-llm_wiki-rebuild-index-scrittori]] — estrazione 2026-11-23 di `code_repos/llm_wiki` (`e08cfce`, `success`, 33 file): indice prodotto da `rebuild_wiki_index`, 120 occorrenze di `index.md` e `log.md` classificate, scrittori di indice (9) e log (7), `rewriteIndexMd`, ingest da conversazione; letto, non eseguito
- [[session-2026-11-20-16-3649aa67]] — sessione di bootstrap `wiki-factory` 2.48 su `llm_wiki` (in `wiki/sessions/`; indice delle sessioni: [sessions/index.md](sessions/index.md))

## Entities
- [[llm-wiki-app]] — l'applicazione desktop `llm-wiki`: identità, funzioni dichiarate in README
- [[llm-wiki-mcp-server]] — server MCP: 12 strumenti registrati, limiti di `llm_wiki_write_page`
- [[llm-wiki-skill]] — skill `llm_wiki_skill` per agenti: identità, trigger, versione dichiarata (0.4.10+), istruzioni descritte e le 17 incoerenze interne
- [[llm-wiki-skill-bozza-alm-wiki]] — bozza di riscrittura della skill alla 0.6.13 (alm-wiki): cosa aggiunge, livelli di prova, elementi non trasferibili alla PR upstream, anomalie A1-A5

## Concepts

### Applicazione llm-wiki
- [[pattern-llm-wiki]] — il pattern LLM Wiki come lo dichiara la README
- [[llm-wiki-struttura-e-moduli]] — layout, entrypoint e moduli
- [[llm-wiki-stack-e-dipendenze]] — i tre descriptor, dipendenze, toolchain
- [[llm-wiki-api-locale]] — API HTTP locale, clip server, comandi Tauri
- [[llm-wiki-skill-api-v1-dichiarata]] — contratto dell'API HTTP locale come lo dichiara la skill (API v1, app 0.4.10+), non v0.6.13
- [[llm-wiki-api-osservazioni-esecuzione-v0-6-13]] — le dodici osservazioni sull'API locale in esecuzione (app 0.6.13, 2026-11-13, una prova, un progetto, non replicata) e i fatti del 2026-11-08
- [[llm-wiki-ricerca-e-grafo-api]] — come il codice v0.6.13 calcola `search` (modalità, quota del grafo, `vectorScore`, pesi, copertura) e `graph` (tipo, id, archi, `limit`); letto, non eseguito
- [[llm-wiki-review-store-e-auto-save]] — review: id FNV-1a, auto-save della UI senza fusione col disco, scritture API su qualunque progetto, pulizia automatica senza filtro per tipo nella fase LLM
- [[llm-wiki-agente]] — modulo agente, permessi e router
- [[llm-wiki-sicurezza]] — bind, CORS, estensione Chrome, Tauri, segreti nello store, Clip server (token solo da rete locale, corpo senza limite, `projectPath` non confrontato)
- [[llm-wiki-schema-dati]] — dati su file, tipi condivisi, schemi LanceDB
- [[llm-wiki-archivi-persistenza]] — i 17 archivi di `.llm-wiki/` e le chiavi di `app-state.json`
- [[llm-wiki-versioni-e-migrazioni]] — versioni di formato e migrazioni
- [[llm-wiki-operazioni-distruttive]] — operazioni distruttive, innesco e salvaguardie
- [[llm-wiki-gestione-file-corrotti]] — comportamento sui file corrotti
- [[llm-wiki-sincronizzazione-file]] — watcher di progetto, snapshot e coda dei cambi file
- [[llm-wiki-cancellazione-pagine-e-sorgenti]] — cascata di cancellazione di una pagina e ciclo di vita delle sorgenti
- [[llm-wiki-pipeline-ingest]] — pipeline di ingest (due stadi), coda, cache e guardie di percorso
- [[llm-wiki-rischi-persistenza]] — divergenze e rischi del layer di persistenza (deduzioni; esiti verificati in EP-004: rischio 1 non conclusivo, rischio 2 confermato, rischio 3 confermato sul meccanismo, rischio 4 confermato sul meccanismo e non conclusivo su file system, `rename` su Windows e LanceDB, rischio 5 confermato sul chunking e sull'invalidazione dell'impronta, non conclusivo sulla pulizia id legacy, rischio 6 confermato sul meccanismo e non conclusivo sullo stato su disco dopo errore parziale)
- [[llm-wiki-licenza-e-standard]] — GPL v3 di terzi, anomalia MIT del server MCP
- [[llm-wiki-test-e-ci]] — test e CI

### Factory (meta-framework, non riguarda l'applicazione)
- [[factory-decisioni-di-configurazione]] — le dieci decisioni di configurazione della sessione 2026-11-20
- [[master-difetti-rilevati]] — undici difetti del master con evidenza e stato di verifica

## Syntheses
- [[llm-wiki-sintesi-rischi-persistenza]] — sintesi dei rischi di persistenza verificati in EP-004 (US-033): tabella degli 8 rischi con gravità, probabilità e priorità proposte, correzioni da aprire, non conclusivi, prerequisito `db-dev`, decisioni richieste all'utente
- [[llm-wiki-skill-vs-app-v0-6-13]] — differenze fra la skill (API v1, app 0.4.10+) e l'app v0.6.13 per la PR upstream: 5 contraddizioni, 6 estensioni, concordanze e punti non confrontabili, più D13-D17 (osservate) e D18-D21 (dal codice) (tag `diff-skill-app`)
- [[llm-wiki-api-affermazioni-codice-da-verificare]] — affermazioni di alm-wiki sul codice `e08cfce` (livello C): confronto con la wiki e, nelle Aggiornamenti, esito della verifica sul codice (confermate, parziali, non conclusiva) e punti ancora da verificare

## Meta
- [[gaps]] — informazioni che servono e la wiki non ha

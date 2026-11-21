---
id: 2026-11-20-repo-llm_wiki-persistenza-a
type: source
title: Specifiche estratte da code_repos/llm_wiki, persistenza fetta A (repo-sync)
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: ["raw/2026-11-20-repo-llm_wiki-persistenza-a.md"]
tags: [source, repo, llm-wiki, persistenza]
---

# Specifiche estratte da code_repos/llm_wiki, persistenza fetta A (repo-sync)
> Estrazione mirata «fetta A» sul commit `e08cfce`: store `app-state.json`, cartella dati `.llm-wiki/`, tipi delle configurazioni con i campi sensibili (solo nomi), lettori backend di `apiConfig` e `proxyConfig`, ricerca ed embedding. Stato `partial`.

## Contesto
Seconda estrazione mirata sullo stesso commit della prima ([[2026-11-20-repo-llm_wiki]]), prodotta da `repo-sync` v2.12 per TSK-002 (US-013 e US-014) sul commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3`, ramo `develop`. Stack, struttura, API e dipendenze non sono ripetuti. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Identità e perimetro]

## Dettaglio

### Metadati dell'estrazione
- Il repository scansionato è di terzi, sotto GNU GPL v3; il raw lo descrive con parole proprie e cita solo nomi di file, simboli, campi e tipi, senza frammenti di codice. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Identità e perimetro]
- File letti in questa fetta: 23 (18 interi, 5 a finestra). Il raw dichiara un cumulativo di 63, minimo verificabile perché due dei file nuovi risultano già letti nella prima estrazione e l'elenco esatto dei 30 iniziali non è verificabile; `files_total_in_repo` è 476, stato complessivo `partial`. Il manifest riporta `files_sampled` 65 dopo l'aggiornamento: il testo del raw precede gli aggiornamenti, il manifest è il cumulativo successivo (massimo, non verificabile). [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Identità e perimetro] [^src: raw/.extraction-manifest.json §2026-11-20-repo-llm_wiki-persistenza-a.extraction_metadata.files_sampled]
- Sono letti solo nomi e tipi di campo, nessun valore di credenziale: i default dei campi sensibili sono stringhe vuote, gli endpoint costanti sono loopback, nessun file `.env*` è aperto. `secrets_redacted` vale 0 solo per i 23 file e gli intervalli letti, perché non c'è stata una ricerca testuale (gap `llm-wiki-scan-credenziali`). [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Note di estrazione]
- Istruzioni trovate nel contenuto: nessuna ostile e nessuna rivolta a un agente; presenti commenti per i manutentori (un avviso di mantenere una chiave allineata in `project-store.ts`), un helper di debug attivo solo in sviluppo in `App.tsx` e un messaggio d'errore per l'utente in `lib.rs` che cita un comando npm. Nessuna è stata eseguita. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Note di estrazione]
- Il raw distingue «osservato» (letto nel codice) da «deduzione» dal codice non osservata in esecuzione; i qualificatori sono riportati nelle pagine come nel raw. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Note di estrazione]

### Contenuto
- Non verificati: il percorso fisico di `app-state.json` per sistema operativo e il comportamento del plugin store su file corrotto, perché sorgente e documentazione del plugin non erano disponibili offline. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Store applicativo (`app-state.json`)]
- File non letti dichiarati: `proxy.rs` dalla riga 261, `api_server.rs` dalla riga 1201 (con i gestori `handle_search`, `handle_embed_page`, `handle_write_page`, `handle_chat`), `search.rs` dalla riga 1201, `embedding.ts` dalla riga 251, `embedding-section.tsx` dalla riga 201; esclusi come fuori ambito `maintenance-section.tsx`, `fs.rs` (fetta B), `settings-view.tsx`, `auto-save.ts`, `agent/provider.rs`, `agent/tools.rs`, `clip_server.rs`. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §File letti e non letti]
- La sezione «Aggiornamenti (v2026-11-20)» è sullo stesso commit e non modifica il testo sopra: ogni voce dice cosa corregge con «Prima» e «Ora». Ha letto solo tre file a finestre (`maintenance-section.tsx`, `api_server.rs`, `settings-view.tsx`); le voci marcate «graphify affected, grafo AST del 2026-11-20» non sono riviste con la lettura. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Aggiornamenti (v2026-11-20)]
- La verifica relazionale (graphify AST senza LLM, ctags, ricerca testuale dei nomi dei comandi `invoke`) è un metodo, non una fonte normativa; si appoggia a un file locale non versionato e rigenerabile. Graphify non vede gli archi IPC tra TS e Rust, le costanti non sono nodi, `load_agent_runtime_config` è definita due volte ed è ambigua per graphify, e uno zero di graphify non prova l'assenza di chiamanti. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Limiti]
- Il raw elenca 10 gap evidenti e dichiara che i gap `llm-wiki-app-state-percorso` e `llm-wiki-creazione-cartella-dati` sono parzialmente documentati e non pronti per la chiusura senza riserve. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Gap evidenti]

### Pagine ricavate o aggiornate
- Aggiornate: [[llm-wiki-archivi-persistenza]] (lettori e flush di `app-state.json`, `project.json` letto dal Rust), [[llm-wiki-schema-dati]] (tipi delle configurazioni, ciclo di vita di `.llm-wiki/`), [[llm-wiki-gestione-file-corrotti]], [[llm-wiki-sicurezza]], [[llm-wiki-api-locale]], [[llm-wiki-agente]], [[llm-wiki-operazioni-distruttive]] (import), [[llm-wiki-rischi-persistenza]] (indizi, esito invariato).

### Gap aperti da questa fetta
Dai gap evidenti del raw sono stati aperti in [[gaps]]: `llm-wiki-import-id-duplicato`, `llm-wiki-serde-compat-config`, `llm-wiki-embedding-trasporto`, `llm-wiki-ui-salvataggio-impostazioni`. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Gap evidenti]

## Estratto non promosso a pagina
Nessun contenuto del raw è stato scartato. Il testo del raw non è stato modificato.

## Pagine collegate
[[2026-11-20-repo-llm_wiki]], [[2026-11-20-repo-llm_wiki-persistenza-b]], [[2026-11-20-repo-llm_wiki-persistenza-c]], [[gaps]]

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

## Aggiornamenti (v2026-11-21)
Nota sul ramo del checkout (non una contraddizione di contenuto): questa source page indica il commit `e08cfce` sul ramo `develop`, mentre i raw del giro del 2026-11-21 ([[2026-11-21-repo-llm_wiki-agente-tools]] e le altre cinque fette) lo indicano su HEAD detached. È lo stesso commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3`; la differenza è un artefatto del checkout del submodule. Le conferme e i superamenti di quanto qui riportato sono nelle pagine concept aggiornate in `## Aggiornamenti (v2026-11-21)`. [^src: raw/2026-11-21-repo-llm_wiki-agente-tools.md §Specifiche estratte: llm_wiki, agente tools e provider (fetta B2)]

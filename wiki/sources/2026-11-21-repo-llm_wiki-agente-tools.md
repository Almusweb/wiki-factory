---
id: 2026-11-21-repo-llm_wiki-agente-tools
type: source
title: Specifiche estratte da code_repos/llm_wiki, estrazione 2026-11-21 fetta B2: agente tools e provider (repo-sync)
status: draft
created: 2026-11-21
updated: 2026-11-21
sources: ["raw/2026-11-21-repo-llm_wiki-agente-tools.md"]
tags: [source, repo, llm-wiki, agente, tools, provider]
---

# Specifiche estratte da code_repos/llm_wiki, estrazione 2026-11-21 fetta B2: agente tools e provider (repo-sync)
> Estrazione mirata `repo-sync` v2.12 del 2026-11-21 sul commit `e08cfce` (v0.6.13), limitata a `src-tauri/src/agent/`: registry dei tool, `shell.exec`, serde delle configurazioni, `write_wiki_page_verified`, provider e router.

## Contesto
Terza fetta del giro del 2026-11-21 (agente, parte tool). Il raw indica il ramo come HEAD detached; la source page [[2026-11-20-repo-llm_wiki-persistenza-a]] indica `develop`. Il commit è lo stesso (`e08cfce`): la differenza è un artefatto del checkout del submodule e si registra come nota, non come contraddizione di contenuto. [^src: raw/2026-11-21-repo-llm_wiki-agente-tools.md §Specifiche estratte: llm_wiki, agente tools e provider (fetta B2)]

## Dettaglio

### Metadati dell'estrazione
- Prodotta da `repo-sync` v2.12 il 2026-11-21 sul commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` (v0.6.13, HEAD detached), in sola lettura verso la sorgente; i percorsi sono relativi a `src-tauri/src/agent/`. [^src: raw/2026-11-21-repo-llm_wiki-agente-tools.md §Specifiche estratte: llm_wiki, agente tools e provider (fetta B2)]
- Letti: `agent/tools.rs` (1-3889, intero), `agent/provider.rs` (righe 1-260 di circa 600), `agent/types.rs`, `agent/router.rs` e `agent/permissions.rs` interi. [^src: raw/2026-11-21-repo-llm_wiki-agente-tools.md §Metodo e limiti]
- Nei file letti non compare alcun valore di credenziale, solo nomi di campo; nessuna istruzione rivolta all'agente è stata trovata nel contenuto. [^src: raw/2026-11-21-repo-llm_wiki-agente-tools.md §Metodo e limiti]

### Contenuto
- Registry dei tool (11 eseguiti, 3 solo dichiarati), provider LLM e web, router: [[llm-wiki-agente]]. [^src: raw/2026-11-21-repo-llm_wiki-agente-tools.md §Registry dei tool]
- `shell.exec` e approvazione (nessun controllo in `tools.rs`, ambiente ridotto non sandbox): [[llm-wiki-sicurezza]]. [^src: raw/2026-11-21-repo-llm_wiki-agente-tools.md §shell.exec e approvazione (gap approvazione-shell)]
- Serde delle quattro struct di configurazione e formato di log e indice (conferma negativa): [[llm-wiki-schema-dati]]. [^src: raw/2026-11-21-repo-llm_wiki-agente-tools.md §Configurazioni e serde (gap serde-compat-config)]
- `write_wiki_page_verified` (atomicità, rilettura, limiti) e scritture del workspace: [[llm-wiki-rischi-persistenza]]. [^src: raw/2026-11-21-repo-llm_wiki-agente-tools.md §write_wiki_page_verified (gap scritture-non-verificate, parte)]

### Limiti e gap
Il raw elenca cinque gap evidenti: approvazione a runtime non letta (risolta dalla fetta [[2026-11-21-repo-llm_wiki-agente-runtime]]), tipi TypeScript delle config non letti, `provider.rs` letto solo in parte, formato di `log.md` e logica di `index.md` non determinati, `file_history.rs` oltre la riga 70 e `inactiveQueueWrite` e helper review non letti. [^src: raw/2026-11-21-repo-llm_wiki-agente-tools.md §Gap evidenti]

## Pagine ricavate o aggiornate
Aggiornate: [[llm-wiki-agente]], [[llm-wiki-sicurezza]], [[llm-wiki-schema-dati]], [[llm-wiki-rischi-persistenza]].

## Gap di questa fetta
- Parziali: `llm-wiki-serde-compat-config`, `llm-wiki-scritture-non-verificate`, `llm-wiki-log-index-formato` (poi chiuso dalla fetta [[2026-11-21-repo-llm_wiki-ingest]]), `llm-wiki-codice-non-letto`, `llm-wiki-persistenza-codice-non-letto`. Il gap `llm-wiki-approvazione-shell` è chiuso dalla fetta del runtime.
- Aperto: `llm-wiki-provider-rs-non-letto`.
- Non aperti: `llm-wiki-runtime-approvazione-shell` (risolto dalla fetta del runtime) e `llm-wiki-searxng-nomi-ts` (vedi [[llm-wiki-schema-dati]]: i nomi TS `searXngUrl` e `searXngCategories` sono già registrati dalla fetta A di persistenza; il confronto bilaterale resta non testato nella sezione «Aggiornamenti» della pagina).

Dettagli in [[gaps]]. [^src: raw/2026-11-21-repo-llm_wiki-agente-tools.md §Gap evidenti]

## Estratto non promosso a pagina
Nessun contenuto del raw è stato scartato. Il testo del raw non è stato modificato.

## Pagine collegate
[[2026-11-20-repo-llm_wiki]], [[2026-11-20-repo-llm_wiki-persistenza-a]], [[2026-11-20-repo-llm_wiki-persistenza-b]], [[llm-wiki-agente]], [[llm-wiki-sicurezza]], [[llm-wiki-schema-dati]], [[llm-wiki-rischi-persistenza]], [[gaps]]

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

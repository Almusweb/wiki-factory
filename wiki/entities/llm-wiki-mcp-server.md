---
id: llm-wiki-mcp-server
type: entity
title: llm-wiki — server MCP
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: ["raw/2026-11-20-repo-llm_wiki.md"]
tags: [llm-wiki, mcp, entity]
---

# llm-wiki — server MCP
> Il server MCP (`mcp-server/src/index.ts`, letto per intero) inoltra ogni chiamata all'API locale e registra 12 strumenti, mentre il suo README ne dichiara 10.

## Contesto
`mcp-server/src/index.ts` usa trasporto stdio e inoltra ogni chiamata all'API HTTP locale (vedi [[llm-wiki-api-locale]]). Si configura con le variabili `LLM_WIKI_API_TOKEN` e `LLM_WIKI_API_BASE_URL`. [^src: raw/2026-11-20-repo-llm_wiki.md §Server MCP]

## Dettaglio

### Strumenti registrati nel codice
1. `llm_wiki_status` (stato e progetto corrente).
2. `llm_wiki_projects`.
3. `llm_wiki_set_project` (vincola la sessione MCP a un progetto).
4. `llm_wiki_files`.
5. `llm_wiki_read_file` (limite di 120 KB sul testo restituito).
6. `llm_wiki_reviews`.
7. `llm_wiki_search`.
8. `llm_wiki_chat` (modalità `fast`, `standard`, `deep`, `local_first`).
9. `llm_wiki_graph`.
10. `llm_wiki_rescan_sources`.
11. `llm_wiki_embed_page` (non documentato nel README di `mcp-server`).
12. `llm_wiki_write_page` (non documentato nel README di `mcp-server`).

[^src: raw/2026-11-20-repo-llm_wiki.md §Server MCP]

### Discrepanza README e codice
Il README di `mcp-server` dichiara 10 strumenti, il codice ne registra 12. Il suo paragrafo di sicurezza parla solo di letture e non cita la scrittura di pagine. [^src: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti]

### `llm_wiki_write_page`
- Crea o sovrascrive una pagina Markdown sotto `wiki/`. Parametri: percorso, contenuto, flag di sovrascrittura (default falso). [^src: raw/2026-11-20-repo-llm_wiki.md §Server MCP]
- Vincoli nel codice: percorso canonico sotto `wiki/` con estensione `.md`, senza segmenti nascosti o `..`, percorso massimo 4096 byte, contenuto massimo 2 MiB. [^src: raw/2026-11-20-repo-llm_wiki.md §Server MCP]
- La descrizione dello strumento dichiara che il successo viene restituito solo dopo la verifica byte per byte della scrittura. [^src: raw/2026-11-20-repo-llm_wiki.md §Server MCP]

### Comportamento comune
- Ogni strumento tranne `llm_wiki_status` controlla prima il flag `mcpEnabled` restituito dall'API di salute e, se è disabilitato, risponde con un errore esplicito. [^src: raw/2026-11-20-repo-llm_wiki.md §Server MCP]
- Dopo `llm_wiki_set_project`, gli altri strumenti non possono uscire dal progetto vincolato e ogni risposta riporta un marcatore `activeProject`. [^src: raw/2026-11-20-repo-llm_wiki.md §Server MCP]

### Pacchetto
Versione del package `0.4.26`; dipendenze `@modelcontextprotocol/sdk@^1.29.0` (dev: `typescript@^5.7.3`, `@types/node@^20`); licenza dichiarata nel `package.json`: MIT, diversa dalla GPL v3 della radice (vedi [[llm-wiki-licenza-e-standard]]). [^src: raw/2026-11-20-repo-llm_wiki.md §Dipendenze esterne]

## Pagine collegate
[[llm-wiki-api-locale]], [[llm-wiki-agente]], [[llm-wiki-sicurezza]]. Gap aperti: [[gaps]] (`llm-wiki-mcp-readme-vs-codice`, `llm-wiki-licenza-mcp-server`).

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

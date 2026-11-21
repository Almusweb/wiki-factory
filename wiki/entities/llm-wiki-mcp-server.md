---
id: llm-wiki-mcp-server
type: entity
title: llm-wiki — server MCP
status: draft
created: 2026-11-20
updated: 2026-11-21
sources: ["raw/2026-11-20-repo-llm_wiki.md", "raw/2026-11-21-repo-llm_wiki-api-mcp.md"]
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

## Aggiornamenti (v2026-11-21)
Dalla fetta A del giro del 2026-11-21 ([[2026-11-21-repo-llm_wiki-api-mcp]]): letti per intero `mcp-server/src/api-client.ts`, `mcp-server/src/index.ts` e `mcp-server/README.md`, in confronto con `api_server.rs`. Il testo sopra non è modificato; il gap `llm-wiki-mcp-readme-vs-codice` è chiuso in [[gaps]]. Il contratto delle route raggiunte è in [[llm-wiki-api-locale]], la matrice di autenticazione in [[llm-wiki-sicurezza]].

- Il server MCP è un processo Node su stdio (`@modelcontextprotocol/sdk`), nome `llm-wiki`; la base URL viene da `LLM_WIKI_API_BASE_URL` (default `http://127.0.0.1:19828`) e il token da `LLM_WIKI_API_TOKEN`, inviato come `Authorization: Bearer` tranne per `/health`. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Server MCP]
- Gli strumenti sono 12: `llm_wiki_status` (`GET /health` e `/projects`, non richiede MCP abilitato), `projects`, `set_project` (pin locale), `files`, `read_file` (output troncato a 120.000 byte), `reviews`, `search`, `chat` (non streaming), `graph` (`edgeScope` default `filtered` se c'è `offset`, altrimenti `page`), `rescan_sources`, `embed_page` e `write_page`. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Server MCP]
- Tutti gli strumenti tranne `status` chiamano prima `GET /health` e rifiutano se `mcpEnabled === false`. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Server MCP]
- `write_page` valida lato client path (canonico, sotto `wiki/`, `.md`, senza componenti nascosti, max 4096 byte) e content (max 2 MiB); il client richiede `result.verified === true`, altrimenti lancia errore. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Server MCP]
- Il client non espone `PATCH`/`DELETE` review né `reviews/resolve`: il tipo del metodo è `"GET" | "POST"` e non esistono strumenti corrispondenti. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Server MCP]
- Un agente MCP con token può scrivere pagine wiki e creare indici vettoriali, perché le route `pages/embed` e `pages/write` sono raggiunte dal client. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Server MCP]
- README contro codice: il README elenca 10 strumenti contro i 12 del codice (mancano `llm_wiki_embed_page` e `llm_wiki_write_page`). Presenta «Allow access without a token» come alternativa al token, ma embed, write e chat richiedono sempre il token: senza token funzionano solo gli strumenti di lettura e review/rescan. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §README MCP vs codice]
- Coerenti col codice: i prerequisiti «Enable local HTTP API» ed «Enable MCP access», il fatto che `llm_wiki_status` funzioni con MCP disabilitato e il default `127.0.0.1`. Il README non menziona la modalità LAN (`allowLanAccess`) né che il client MCP assume l'host loopback salvo override con `LLM_WIKI_API_BASE_URL`. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §README MCP vs codice]
- Restano non letti `mcp-server/src/project-binding.ts` e `version.ts` (gap `llm-wiki-api-ui-token-non-letti`). [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Provenienza e copertura]

## Contradictions
- **README e codice: strumenti e accesso senza token.** Prima (sezione «Discrepanza README e codice»): il README dichiara 10 strumenti, il codice ne registra 12, il suo paragrafo di sicurezza parla solo di letture; non è chiaro se il README sia indietro. Ora (fetta A): il README è indietro su `embed_page` e `write_page` e presenta «Allow access without a token» come alternativa al token, mentre `chat`, `embed` e `write` richiedono sempre il token; il testo UI per «Agent chat» omette embed e write. Il codice conferma le scritture. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §README MCP vs codice]

---
id: 2026-11-21-repo-llm_wiki-api-mcp
type: source
title: Specifiche estratte da code_repos/llm_wiki, estrazione 2026-11-21 fetta A: API HTTP locale, MCP, rete (repo-sync)
status: draft
created: 2026-11-21
updated: 2026-11-21
sources: ["raw/2026-11-21-repo-llm_wiki-api-mcp.md"]
tags: [source, repo, llm-wiki, api, mcp, rete]
---

# Specifiche estratte da code_repos/llm_wiki, estrazione 2026-11-21 fetta A: API HTTP locale, MCP, rete (repo-sync)
> Estrazione mirata `repo-sync` v2.12 del 2026-11-21 sul commit `e08cfce` (v0.6.13): `api_server.rs` letto per intero, `server_bind.rs`, `cors.rs`, il client e il server MCP. Chiude i gap sul contratto API, sull'autenticazione fuori dal loopback e sul README MCP; le letture a valle restano aperte.

## Contesto
Quinta estrazione sullo stesso commit, dopo [[2026-11-20-repo-llm_wiki]] e le tre fette di persistenza ([[2026-11-20-repo-llm_wiki-persistenza-a]], [[2026-11-20-repo-llm_wiki-persistenza-b]], [[2026-11-20-repo-llm_wiki-persistenza-c]]). Questa è la fetta A del giro del 2026-11-21 (API, MCP, rete); le altre cinque fette sono [[2026-11-21-repo-llm_wiki-agente-runtime]], [[2026-11-21-repo-llm_wiki-agente-tools]], [[2026-11-21-repo-llm_wiki-fs-lib-progetto]], [[2026-11-21-repo-llm_wiki-ingest]] e [[2026-11-21-repo-llm_wiki-ricerca-ui-residui]]. Il raw indica il ramo come HEAD detached, mentre le source page del 2026-11-20 dicono `develop`: è lo stesso commit e la differenza è un artefatto del checkout del submodule, non un fatto di contenuto. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Specifiche estratte: llm_wiki, API HTTP locale, MCP, rete]

## Dettaglio

### Metadati dell'estrazione
- Il raw è generato da `repo-sync` v2.12 il 2026-11-21 sul commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` (v0.6.13, HEAD detached), in sola lettura sulla sorgente. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Specifiche estratte: llm_wiki, API HTTP locale, MCP, rete]
- Letti per intero: `api_server.rs` (1-4106), `server_bind.rs`, `cors.rs`, `api-token.ts`, `api-server-constants.ts`, `mcp-server/src/api-client.ts`, `mcp-server/src/index.ts` e `mcp-server/README.md`. Letti in parte: `api-server-section.tsx` (1-399) e `clip_server.rs` (1-60, solo import). [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Provenienza e copertura]
- Non letti: il resto di `api-server-section.tsx`, `src/i18n/index.ts`, `project-binding.ts`, `version.ts` e il corpo di `clip_server.rs` oltre la riga 60. Un chiamante non trovato nelle finestre lette è «non verificato», non «assente». [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Provenienza e copertura]
- Tutte le osservazioni derivano da lettura statica: nessun test è stato eseguito. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Gap evidenti (residui di questa fetta)]

### Contenuto
- Server HTTP: `tiny_http` sulla porta 19828, 15 route sotto `/api/v1` più `/health`, limiti, rate limit globale, ordine dei controlli e stato globale: dettaglio in [[llm-wiki-api-locale]]. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Server HTTP]
- Contratto per route (payload, errori, limiti di `files/content`, `search`, `graph`, `pages/write`, `pages/embed`, `chat` in JSON o SSE) e confronto con la lista `API_ENDPOINTS` della UI (13 voci contro 15 route): [[llm-wiki-api-locale]]. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Contratto API]
- Bind, token, matrice di autenticazione per route, CORS e le due inferenze non testate: [[llm-wiki-sicurezza]]. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Autenticazione e rete]
- Server MCP (12 strumenti) e confronto con il README (10 strumenti): [[llm-wiki-mcp-server]]. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §README MCP vs codice]
- Scritture sullo stato: le scritture delle review (`PATCH`, `DELETE`, `resolve`) lavorano sull'array grezzo di `.llm-wiki/review.json` e non sono atomiche, non sono verificate e non usano lock; `pages/write` delega a `write_wiki_page_verified`, la cui implementazione è letta dalla fetta [[2026-11-21-repo-llm_wiki-agente-tools]]. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Scritture sullo stato]

### Limiti e gap
- Residui dichiarati: corpi non letti di `embed_wiki_page`, `commands::search::*` (incluso `resolve_query_embedding`) e `rescan_project_files`; struttura di `AgentChatRequest` e degli eventi agente; uso di `server_bind` e `cors` in `clip_server.rs` oltre la riga 60; interazione del processo WebView con `review.json`. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Gap evidenti (residui di questa fetta)]
- Il raw dichiara di chiudere i gap 2, 3, 4 e 30 e la parte `api_server.rs` del gap 1. Il keeper chiude formalmente i gap 2, 3 e 4; il gap 30 (`llm-wiki-scritture-non-verificate`) resta aperto in parte perché `history-settings.json` (`file_history.rs` righe 1-69) non è letto da nessuna fetta. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Specifiche estratte: llm_wiki, API HTTP locale, MCP, rete]

## Pagine ricavate o aggiornate
Aggiornate: [[llm-wiki-api-locale]], [[llm-wiki-mcp-server]], [[llm-wiki-sicurezza]]. Nessuna pagina nuova.

## Gap di questa fetta
- Chiusi: `llm-wiki-contratto-api-http`, `llm-wiki-api-lan-auth`, `llm-wiki-mcp-readme-vs-codice`.
- Parziali: `llm-wiki-scritture-non-verificate`, `llm-wiki-codice-non-letto`.
- Aperti: `llm-wiki-api-corpi-handler-non-letti`, `llm-wiki-clip-server-uso-bind-cors`, `llm-wiki-review-concorrenza-webview`, `llm-wiki-api-ui-token-non-letti`.

Dettagli in [[gaps]]. [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Gap evidenti (residui di questa fetta)]

## Estratto non promosso a pagina
Nessun contenuto del raw è stato scartato. Il testo del raw non è stato modificato.

## Pagine collegate
[[2026-11-20-repo-llm_wiki]], [[llm-wiki-api-locale]], [[llm-wiki-mcp-server]], [[llm-wiki-sicurezza]], [[gaps]]

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

---
id: llm-wiki-test-e-ci
type: concept
title: llm-wiki — test e CI
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: ["raw/2026-11-20-repo-llm_wiki.md"]
tags: [llm-wiki, test, ci]
---

# llm-wiki — test e CI
> Il repository ha molti test, ma il workflow CI `ci.yml` non li esegue; il workflow `build.yml` non è stato letto.

## Contesto
Pagina costruita dalla sezione di test coverage del raw, che è `partial`: i file campionati sono 30 su 476. [^src: raw/2026-11-20-repo-llm_wiki.md §Test coverage rilevato]

## Dettaglio
- **Framework**: `vitest@^4.1.4` con `fast-check@^4.7.0` per i test di proprietà; il server MCP usa invece il runner nativo di Node. [^src: raw/2026-11-20-repo-llm_wiki.md §Test coverage rilevato]
- **Script in `package.json`**: `test:mocks` (esclude i test con LLM reale e quelli di `mcp-server`), `test:llm` (test con LLM reale, senza parallelismo), `mcp:test`. [^src: raw/2026-11-20-repo-llm_wiki.md §Test coverage rilevato]
- **Suite**: molti file `*.test.ts` accanto ai sorgenti in `src/lib`, `src/stores`, `src/components`, `src/commands`; varianti `.property.`, `.scenarios.`, `.race.`, `.integration.` e `.real-llm.`; cartella `src/lib/__tests__/`; `mcp-server/test/` (3 file); helper e scenari in `src/test-helpers/`. [^src: raw/2026-11-20-repo-llm_wiki.md §Test coverage rilevato]
- **Test Rust**: unitari incorporati nei moduli (`#[cfg(test)]`), visti in `server_bind.rs`, `cors.rs`, `permissions.rs`, `router.rs`. [^src: raw/2026-11-20-repo-llm_wiki.md §Test coverage rilevato]
- **Test con LLM reale**: `vite.config.ts` registra un file di setup che carica un file di ambiente; tale file di ambiente non è nel repository. [^src: raw/2026-11-20-repo-llm_wiki.md §Test coverage rilevato]
- **Coverage**: nessuna configurazione di coverage tool rilevata. [^src: raw/2026-11-20-repo-llm_wiki.md §Test coverage rilevato]
- **CI** (`ci.yml`): su macOS, Ubuntu e Windows esegue build del frontend e build Rust e non esegue i test. Il workflow `build.yml` non è stato letto. [^src: raw/2026-11-20-repo-llm_wiki.md §Test coverage rilevato]

## Pagine collegate
Gap aperto su CI e test: [[gaps]] (`llm-wiki-ci-test-build`).

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

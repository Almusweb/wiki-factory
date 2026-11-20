---
id: llm-wiki-stack-e-dipendenze
type: concept
title: llm-wiki — stack e dipendenze
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: ["raw/2026-11-20-repo-llm_wiki.md"]
tags: [llm-wiki, stack, dipendenze]
---

# llm-wiki — stack e dipendenze
> Repository multi-stack con tre descriptor (frontend React 19, backend Rust con Tauri 2, server MCP su Node), ciascuno con confidence 0.7.

## Contesto
Il raw riporta l'output di `stack-detector`: il repository ha tre descriptor, senza workspace npm né Cargo workspace. [^src: raw/2026-11-20-repo-llm_wiki.md §Stack rilevato]

## Dettaglio

### Frontend: TypeScript con React 19
- Linguaggio `typescript`, framework `react` `^19.0.0`, `ruleset_id` `typescript.react.v19`. [^src: raw/2026-11-20-repo-llm_wiki.md §Stack rilevato]
- Librerie secondarie principali: `vite@^8.0.0`, `tailwindcss@^4.2.2`, `zustand@^5.0.12`, `@milkdown/kit@^7.20.0`, `sigma@^3.0.2`, `graphology@^0.26.0`, `i18next@^26.0.3`, `react-i18next@^17.0.2`, `react-markdown@^10.1.0`, `mermaid@^11.14.0`, `katex@^0.16.45`, `@tauri-apps/api@^2.11.0`, `vitest@^4.1.4`, `fast-check@^4.7.0`. [^src: raw/2026-11-20-repo-llm_wiki.md §Stack rilevato]
- Confidence 0.7 (medio): manifest 0.5 e config 0.2. Gli import di React confermati nel campione sono 2, sotto i 5 richiesti dal detector, quindi gli import non contribuiscono. [^src: raw/2026-11-20-repo-llm_wiki.md §Stack rilevato]

### Backend desktop: Rust con Tauri 2
- Linguaggio `rust`, framework `tauri` (non nella lista del detector, riportato come `other`), versione `2`, edition 2021, `rust-version = 1.88`, `ruleset_id` `rust.other.v2`. [^src: raw/2026-11-20-repo-llm_wiki.md §Stack rilevato]
- Crate secondari principali: `lancedb@0.27.2`, `pdfium-render@0.9`, `tiny_http@0.12`, `reqwest@0.12`, `tokio@1`, `notify@8`, `docx-rs@0.4.20`, `calamine@0.34.0`, `epub@2.1.5`, `mobi@0.8`, `anydoc@0.1.6`, `office_oxide@=0.1.2`. [^src: raw/2026-11-20-repo-llm_wiki.md §Stack rilevato]
- Confidence 0.7: manifest 0.5 e config 0.2. Gli import di `tauri` nel campione compaiono in 2 file, sotto soglia. [^src: raw/2026-11-20-repo-llm_wiki.md §Stack rilevato]

### Server MCP: TypeScript su Node
- Linguaggio `typescript`, framework `none`, Node `>=20`, `ruleset_id` `typescript.none.v1`, dipendenze `@modelcontextprotocol/sdk@^1.29.0` e `typescript@^5.7.3`. Confidence 0.7; l'import dell'SDK MCP è stato letto in 1 solo file. [^src: raw/2026-11-20-repo-llm_wiki.md §Stack rilevato]

### Dipendenze dichiarate
- **Frontend** (`package.json`, versione `0.6.13`): circa 40 dipendenze dirette, tra cui react, plugin Tauri (autostart, dialog, http, opener, store), editor Milkdown, grafo (`@react-sigma/core`, `graphology-communities-louvain`, `graphology-layout-forceatlas2`), `pdfjs-dist`, `jszip`, `js-yaml`, `shadcn`, `lucide-react`. [^src: raw/2026-11-20-repo-llm_wiki.md §Dipendenze esterne]
- **Backend** (`src-tauri/Cargo.toml`): circa 30 crate, tra cui `tauri@2` (feature protocol-asset e tray-icon), `serde`, `chrono`, `zip@2`, `arrow-array@57`, `arrow-schema@57`, `sha2@0.10`, `md-5@0.10`, `walkdir@2`, `html2text@0.17.1`; `office_oxide@=0.1.2` è a versione bloccata. Profilo release con LTO, `opt-level = "s"`, `panic = "unwind"` e `strip`. [^src: raw/2026-11-20-repo-llm_wiki.md §Dipendenze esterne]
- **Server MCP**: versione del package `0.4.26`, licenza dichiarata MIT. [^src: raw/2026-11-20-repo-llm_wiki.md §Dipendenze esterne]
- **Servizi esterni**, tutti opzionali e configurati dall'utente (da README e preset): provider LLM (OpenAI, Anthropic, Google, Azure, Ollama, MiniMax, endpoint custom, `claude-code` e `codex-cli` locali), endpoint di embedding compatibili con OpenAI, ricerca web (Tavily, SerpApi, SearXNG), Firecrawl, MinerU (cloud o locale), AnyTXT. [^src: raw/2026-11-20-repo-llm_wiki.md §Dipendenze esterne]
- **Toolchain**: Node 20 o superiore, Rust 1.88 o superiore, `protoc` per la build. [^src: raw/2026-11-20-repo-llm_wiki.md §Dipendenze esterne]

## Pagine collegate
[[llm-wiki-licenza-e-standard]], [[llm-wiki-schema-dati]]

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

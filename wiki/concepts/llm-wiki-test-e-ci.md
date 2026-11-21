---
id: llm-wiki-test-e-ci
type: concept
title: llm-wiki — test e CI
status: draft
created: 2026-11-20
updated: 2026-11-21
sources: ["raw/2026-11-20-repo-llm_wiki.md", "raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md"]
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

## Aggiornamenti (v2026-11-20)
- Il campione cumulativo del raw passa da 30 a 50 file su 476 (`files_sampled` nel manifest); l'estrazione resta `partial`. La sezione di test coverage del raw non è stata modificata dall'aggiornamento: le voci sopra valgono per la prima estrazione. [^src: raw/2026-11-20-repo-llm_wiki.md §Premessa e perimetro]
- Nei test Rust di `page_embedding.rs` compaiono le stringhe «secret» e «rotated» come segnaposto; in `vectorstore.rs` un id di pagina con apice e parola chiave SQL è usato come caso di prova per la validazione dell'input. Sono fixture, non istruzioni né credenziali. [^src: raw/2026-11-20-repo-llm_wiki.md §Note di estrazione dell'update]

## Aggiornamenti (v2026-11-21)
Dalla fetta E del giro del 2026-11-21 ([[2026-11-21-repo-llm_wiki-ricerca-ui-residui]], commit `e08cfce`): letti `ci.yml` e `build.yml` per intero. Il testo sopra non è modificato; dove è superato lo dice `## Contradictions` in coda. Il gap `llm-wiki-ci-test-build` è chiuso in [[gaps]]; resta aperto `llm-wiki-test-fuori-workflow`.

- `ci.yml` parte su push e PR verso `main` con matrice `macos-latest`, `ubuntu-22.04`, `windows-latest`; i passi sono `npx vite build`, build delle risorse MCP e `cargo build`; non ci sono passi di test. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §CI e build (gap ci-test-build)]
- `build.yml` («Build & Release») parte su tag `v*` o `workflow_dispatch`, con matrice macOS aarch64, `ubuntu-22.04`, `ubuntu-22.04-arm` e Windows; non esegue test. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §CI e build (gap ci-test-build)]
- `build.yml` verifica i checksum PDFium (non su Windows), usa `tauri-apps/tauri-action@v0` (release in bozza sui tag, nessuna release sui run manuali), verifica firma e notarizzazione macOS con `.github/scripts/verify-macos-release.sh` (script non letto), crea uno zip portabile su Windows, carica artifact con retention 14 giorni sui run manuali. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §CI e build (gap ci-test-build)]
- I job `package-extension` (zip di `extension/` con la versione di `package.json`) e `publish-release` (toglie lo stato di bozza dopo build e `package-extension`) completano il workflow. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §CI e build (gap ci-test-build)]
- Secret referenziati per nome (valori non letti): `GITHUB_TOKEN`, `APPLE_CERTIFICATE`, `APPLE_CERTIFICATE_PASSWORD`, `APPLE_SIGNING_IDENTITY`, `APPLE_ID`, `APPLE_PASSWORD`, `APPLE_TEAM_ID`. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §CI e build (gap ci-test-build)]
- Non verificato: se i test Rust (`#[cfg(test)]`) o TypeScript girino in altro modo fuori dai workflow; `.github/scripts/*` non letti. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §CI e build (gap ci-test-build)]

## Contradictions
- **`build.yml` «non letto».** Prima (Contesto, sezione CI): il workflow `build.yml` non è stato letto. Ora (fetta E): è letto per intero e non esegue test; l'affermazione che la CI non esegue i test vale per entrambi i workflow letti. [^src: raw/2026-11-21-repo-llm_wiki-ricerca-ui-residui.md §CI e build (gap ci-test-build)]

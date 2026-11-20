---
tier: team-specific
applies_to:
  language: rust
  framework: "*"        # lo stack-detector non ha 'tauri' nell'enum: il backend risulta rust/other
  context: ["robustness", "design"]
status: draft
created: 2026-11-20
proposta: true   # in code_quality/rules/proposte/: NON letta dal code-reviewer finche' non e' spostata in team-specific/
sources:
  - https://v2.tauri.app/develop/calling-rust/
  - https://rust-lang.github.io/rust-clippy/master/index.html#unwrap_used
  - https://docs.rs/tokio/latest/tokio/sync/struct.Mutex.html
  - https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html
  - https://docs.lancedb.com/core/schema-evolution
  - https://docs.lancedb.com/tables/schema
  - raw/2026-11-20-repo-llm_wiki.md §Entrypoint e moduli chiave
  - raw/2026-11-20-repo-llm_wiki.md §Schema dati (se rilevato)
---

# Regole di progetto — backend Rust + Tauri 2 (+ LanceDB embedded)

Bozza per il backend in `code_repos/llm_wiki/src-tauri/`. Le regole si basano sulla
documentazione ufficiale in frontmatter e sulle convenzioni gia' presenti nel codice: i comandi
passano da un guardiano dei panic (modulo `panic_guard`, `run_guarded_async` in
`commands/vectorstore.rs`) e i dati vettoriali stanno in tabelle LanceDB versionate per nome
(`wiki_vectors` v1, `wiki_chunks_v2`). La sicurezza (capability, CSP, bind, token) e' fuori
scope del CQRL (R.Q7): va a `/security-scan` e alle ADR.

---

## `rust.tauri.robustness.unwrap_in_command`

```yaml
rule_id: "rust.tauri.robustness.unwrap_in_command"
version: v1
tier: team-specific
title: "unwrap/expect nel percorso di un comando Tauri"
applies_to:
  language: rust
  framework: "*"
  context: ["robustness"]
severity_default: high
auto_fixable: false
```

**Rationale**: un panic dentro un comando interrompe la richiesta senza un errore leggibile dal
frontend. I comandi Tauri restituiscono `Result<T, E>` con `E` serializzabile; l'errore va
propagato con `?`/`map_err`. Clippy ha il lint `unwrap_used` per questo.

**Detection hints**:
- `.unwrap()`, `.expect(` in funzioni `#[tauri::command]` o nelle funzioni che chiamano, fuori
  dai moduli `#[cfg(test)]`.
- Eccezione accettata: `expect` su invarianti di processo documentate (es. lock avvelenato) con
  messaggio esplicito.

**Refactoring suggeriti**:
- `?` con `map_err(|e| format!(...))` o un tipo d'errore `thiserror` serializzabile.

---

## `rust.tauri.robustness.command_without_panic_guard`

```yaml
rule_id: "rust.tauri.robustness.command_without_panic_guard"
version: v1
tier: team-specific
title: "Comando nuovo che non passa dal guardiano dei panic"
applies_to:
  language: rust
  framework: "*"
  context: ["robustness", "design"]
severity_default: medium
auto_fixable: false
```

**Rationale**: convenzione prevalente del repository: il modulo `panic_guard` espone
`run_guarded` e `run_guarded_async`, che trasformano un panic in un errore restituito invece di
far cadere la richiesta. Misura del 2026-11-20 su develop @ e08cfce (78 comandi): la usano
`fs.rs`, `vectorstore.rs`, `file_sync.rs`, `search.rs`, `extract_images.rs`, `project.rs`,
`external_search.rs`; non la usano `skills.rs`, `claude_cli.rs`, `codex_cli.rs`,
`file_history.rs`, `project_maintenance.rs`; `lib.rs` in parte (5 su 11). La regola vale per i
comandi nuovi o modificati nei moduli che gia' la seguono; negli altri moduli e' un'osservazione
(severity low), non un difetto del diff.

**Detection hints**:
- `#[tauri::command]` nuova o modificata il cui corpo non passa da `run_guarded*`, in un modulo
  dove gli altri comandi lo fanno.

**Refactoring suggeriti**:
- Racchiudere il corpo nello stesso guardiano dei comandi del modulo.

---

## `rust.tauri.robustness.blocking_io_in_async`

```yaml
rule_id: "rust.tauri.robustness.blocking_io_in_async"
version: v1
tier: team-specific
title: "I/O bloccante dentro un comando asincrono"
applies_to:
  language: rust
  framework: "*"
  context: ["robustness"]
severity_default: medium
auto_fixable: false
```

**Rationale**: i comandi `async` girano sul runtime asincrono; `std::fs`, parsing pesante
(PDF, Office) o calcoli lunghi bloccano un worker del runtime e rallentano gli altri comandi.

**Detection hints**:
- `std::fs::*`, `std::thread::sleep`, chiamate sincrone a librerie di parsing dentro `async fn`
  senza `tokio::task::spawn_blocking`.

**Refactoring suggeriti**:
- `tokio::fs` per l'I/O; `spawn_blocking` per il lavoro CPU-bound o le librerie sincrone.

---

## `rust.tauri.robustness.std_mutex_across_await`

```yaml
rule_id: "rust.tauri.robustness.std_mutex_across_await"
version: v1
tier: team-specific
title: "Guard di std::sync::Mutex tenuto attraverso un .await"
applies_to:
  language: rust
  framework: "*"
  context: ["robustness"]
severity_default: high
auto_fixable: false
```

**Rationale**: tenere il guard di un `std::sync::Mutex` attraverso un `.await` puo' bloccare il
thread del runtime e produrre deadlock; la documentazione di tokio indica di rilasciarlo prima
dell'`await` o di usare `tokio::sync::Mutex`/`RwLock` (come fa gia' `vectorstore_v2_lock`).

**Detection hints**:
- `let g = m.lock()...;` seguito da `.await` nello stesso scope prima del drop di `g`.

**Refactoring suggeriti**:
- Limitare lo scope del guard a un blocco senza `await`; oppure lock asincrono di tokio.

---

## `rust.lancedb.robustness.schema_change_without_migration`

```yaml
rule_id: "rust.lancedb.robustness.schema_change_without_migration"
version: v1
tier: team-specific
title: "Schema di una tabella LanceDB cambiato senza percorso di migrazione"
applies_to:
  language: rust
  framework: "*"
  context: ["robustness", "reliability"]
severity_default: high
auto_fixable: false
```

**Rationale**: lo schema Arrow delle tabelle vettoriali e' definito nel codice (`make_schema`,
`make_schema_v2`). Cambiarlo, o cambiare la dimensione del vettore (`FixedSizeList`), rende
illeggibili o incompatibili i dati gia' scritti nei progetti degli utenti. LanceDB non converte
in place la dimensione di una `FixedSizeList`: serve una nuova colonna/tabella e un re-index.
Il repository ha gia' un precedente: tabella nuova `wiki_chunks_v2`, conteggio delle righe
legacy e drop della v1 su conferma dell'utente.

**Detection hints**:
- Diff che modifica i `Field::new` di uno schema esistente o il nome di una tabella senza:
  nuova tabella o versione, rilevamento dei dati vecchi, percorso di re-index.
- `drop_table`/cancellazioni di massa raggiungibili senza un'azione esplicita dell'utente.

**Refactoring suggeriti**:
- Tabella versionata per nome (pattern v1 → v2), rilevamento dei dati legacy, re-index guidato,
  drop solo su conferma.

---

## `rust.tauri.design.cross_language_contract_drift`

```yaml
rule_id: "rust.tauri.design.cross_language_contract_drift"
version: v1
tier: team-specific
title: "Contratto condiviso TS/Rust cambiato da un lato solo"
applies_to:
  language: rust
  framework: "*"
  context: ["design"]
severity_default: high
auto_fixable: false
```

**Rationale**: alcune strutture sono lette da entrambi i lati: lo store `app-state.json`
(letto dal TypeScript con `@tauri-apps/plugin-store` e dal setup Rust), i payload dei comandi
IPC, i file JSON in `.llm-wiki/`. Il codice stesso avverte di non rinominare una chiave da un
lato solo. Un rename o un cambio di tipo non speculare rompe in silenzio a runtime.

**Detection hints**:
- Diff che cambia nomi di campi `serde` (o `#[serde(rename)]`), argomenti di un
  `#[tauri::command]` o chiavi di `app-state.json` senza la modifica corrispondente in `src/`.

**Refactoring suggeriti**:
- Cambiare entrambi i lati nello stesso TSK; per i file persistiti, leggere il formato vecchio
  e scrivere il nuovo (compatibilita' in lettura).

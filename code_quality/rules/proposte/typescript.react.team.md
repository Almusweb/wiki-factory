---
tier: team-specific
applies_to:
  language: typescript
  framework: react
  context: ["idiomaticity", "robustness", "design"]
status: draft
created: 2026-11-20
proposta: true   # in code_quality/rules/proposte/: NON letta dal code-reviewer finche' non e' spostata in team-specific/
sources:
  - https://react.dev/learn/you-might-not-need-an-effect
  - https://react.dev/learn/synchronizing-with-effects
  - https://react.dev/reference/rules/rules-of-hooks
  - https://zustand.docs.pmnd.rs/reference/hooks/use-shallow
  - https://github.com/pmndrs/zustand/releases/tag/v5.0.0
  - https://v2.tauri.app/develop/calling-rust/
  - https://v2.tauri.app/develop/calling-frontend/
  - raw/2026-11-20-repo-llm_wiki.md §Stack rilevato
  - raw/2026-11-20-repo-llm_wiki.md §Entrypoint e moduli chiave
---

# Regole di progetto — frontend TypeScript + React 19 (+ zustand 5, IPC Tauri 2)

Bozza per il frontend in `code_repos/llm_wiki/src/`. Le regole descrivono pratiche documentate
dalle fonti ufficiali in frontmatter, non il gusto di chi scrive. Il code-reviewer usa solo i
`rule_id` qui definiti (mai regole inventate, `code-review-protocol` Fase 0).

Stack di riferimento (dal raw): React 19 in StrictMode, zustand 5 per gli store, IPC verso il
backend con `invoke()` e gli eventi di `@tauri-apps/api`.

---

## `typescript.react.idiomaticity.effect_for_derived_state`

```yaml
rule_id: "typescript.react.idiomaticity.effect_for_derived_state"
version: v1
tier: team-specific
title: "useEffect usato per calcolare stato derivato"
applies_to:
  language: typescript
  framework: react
  context: ["idiomaticity"]
severity_default: medium
auto_fixable: false
```

**Rationale**: un effetto che legge props o stato e chiama `setState` con un valore calcolabile
durante il render produce un render in piu' e uno stato duplicato che puo' divergere. La
documentazione di React indica di calcolarlo nel render (eventualmente con `useMemo`).

**Detection hints**:
- `useEffect(() => { setX(f(a, b)) }, [a, b])` dove `f` e' pura e non ha effetti esterni.
- Coppie di `useState` dove una e' sempre funzione dell'altra.

**Refactoring suggeriti**:
- Calcolare il valore nel corpo del componente; `useMemo` solo se il calcolo e' costoso.
- Per il reset di stato al cambio di una prop: `key` sul componente.

---

## `typescript.react.idiomaticity.exhaustive_deps_suppressed`

```yaml
rule_id: "typescript.react.idiomaticity.exhaustive_deps_suppressed"
version: v1
tier: team-specific
title: "Dipendenze di un hook escluse senza motivazione"
applies_to:
  language: typescript
  framework: react
  context: ["idiomaticity"]
severity_default: medium
auto_fixable: false
```

**Rationale**: le dipendenze mancanti di `useEffect`/`useMemo`/`useCallback` producono closure
su valori vecchi. Le Rules of Hooks e la regola `react-hooks/exhaustive-deps` esistono per questo.

**Detection hints**:
- Commento `eslint-disable` su `react-hooks/exhaustive-deps` senza una riga che spieghi perche'.
- Array di dipendenze vuoto in un effetto che legge props o stato.

**Refactoring suggeriti**:
- Aggiungere le dipendenze; spostare dentro l'effetto le funzioni che usa.
- Per logica non reattiva dentro un effetto: `useEffectEvent` (React 19.2), dove disponibile.

---

## `typescript.react.robustness.effect_without_cleanup`

```yaml
rule_id: "typescript.react.robustness.effect_without_cleanup"
version: v1
tier: team-specific
title: "Effetto con sottoscrizione o timer senza cleanup"
applies_to:
  language: typescript
  framework: react
  context: ["robustness"]
severity_default: high
auto_fixable: false
```

**Rationale**: in StrictMode React monta, smonta e rimonta i componenti in sviluppo; un effetto
senza cleanup duplica listener, timer e sottoscrizioni. Nell'IPC di Tauri `listen()` restituisce
una funzione di unlisten (in una Promise): se non viene chiamata nel cleanup, il listener resta.

**Detection hints**:
- `listen(`/`once(` di `@tauri-apps/api/event`, `addEventListener`, `setInterval`, `setTimeout`,
  `subscribe` di uno store dentro `useEffect` senza `return () => ...`.
- Cleanup che non attende la Promise di `listen()` prima di chiamare l'unlisten.

**Refactoring suggeriti**:
- Restituire sempre la funzione di cleanup; per `listen()` conservare la Promise e chiamare
  l'unlisten quando risolve.

---

## `typescript.react.robustness.async_effect_race`

```yaml
rule_id: "typescript.react.robustness.async_effect_race"
version: v1
tier: team-specific
title: "Richiesta asincrona in un effetto senza guardia sulla risposta vecchia"
applies_to:
  language: typescript
  framework: react
  context: ["robustness"]
severity_default: medium
auto_fixable: false
```

**Rationale**: un `invoke()` o `fetch()` lanciato da un effetto puo' risolvere dopo che le
dipendenze sono cambiate o il componente e' smontato, e scrivere uno stato non piu' valido
(race condition). La documentazione di React mostra la guardia con flag `ignore` nel cleanup.

**Detection hints**:
- `useEffect` con `invoke(`/`fetch(` e `setState` nel `.then`/dopo `await`, senza flag
  `ignore`/`cancelled` o `AbortController` impostato nel cleanup.

**Refactoring suggeriti**:
- Flag `let ignore = false` + `return () => { ignore = true }`; `AbortController` per `fetch`.

---

## `typescript.react.robustness.invoke_error_unhandled`

```yaml
rule_id: "typescript.react.robustness.invoke_error_unhandled"
version: v1
tier: team-specific
title: "Errore di un comando Tauri non gestito"
applies_to:
  language: typescript
  framework: react
  context: ["robustness"]
severity_default: medium
auto_fixable: false
```

**Rationale**: un comando Rust che restituisce `Err` arriva al frontend come Promise rifiutata.
Senza `catch`/`try` l'errore finisce in un unhandled rejection e l'utente non vede nulla.

**Detection hints**:
- `invoke(` (o i wrapper in `src/commands/`) senza `await` dentro `try/catch` e senza `.catch`.

**Refactoring suggeriti**:
- Gestire l'errore nel wrapper del comando o nel chiamante e portarlo in UI (toast, stato di errore).

---

## `typescript.zustand.idiomaticity.unstable_selector`

```yaml
rule_id: "typescript.zustand.idiomaticity.unstable_selector"
version: v1
tier: team-specific
title: "Selettore zustand che restituisce un oggetto o array nuovo"
applies_to:
  language: typescript
  framework: react
  context: ["idiomaticity", "robustness"]
severity_default: high
auto_fixable: false
```

**Rationale**: in zustand 5 il confronto di default e' `Object.is` e non esiste piu' l'argomento
di equality della v4. Un selettore che crea un oggetto o un array a ogni chiamata causa render
continui fino a «Maximum update depth exceeded». La documentazione indica `useShallow`.

**Detection hints**:
- `useXStore((s) => ({ ... }))`, `useXStore((s) => [s.a, s.b])`, `.filter(`/`.map(` nel selettore,
  senza `useShallow`.
- Fallback inline (`?? []`, `?? {}`) nel selettore.

**Refactoring suggeriti**:
- Un selettore per campo; `useShallow` per selezioni multiple; fallback come costante di modulo.

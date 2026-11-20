---
id: master-difetti-rilevati
type: concept
title: Difetti del master soli-multi-agents-factory rilevati il 2026-11-20
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: ["raw/sessions/session-2026-11-20-16-3649aa67.md"]
tags: [factory, master, difetti, kanban]
---

# Difetti del master soli-multi-agents-factory rilevati il 2026-11-20
> Gli undici difetti del meta-framework (master) emersi nella sessione di bootstrap, ciascuno con l'evidenza dichiarata dal documento di sessione e con lo stato di verifica.

## Contesto
**Questi difetti riguardano il meta-framework (il master e le sue derivate), non l'applicazione `llm_wiki`.** Sono stati rilevati durante il bootstrap della factory `wiki-factory` (PATTERN 2.48). Il documento di sessione li elenca con numerazione da 1 a 11, mantenuta qui; la decisione di tracciarli nel kanban con il product-manager e il tpm è in [[factory-decisioni-di-configurazione]] (decisione 10). Quadro della sessione: [[session-2026-11-20-16-3649aa67]]. [^src: raw/sessions/session-2026-11-20-16-3649aa67.md §Insight]

**Come leggere lo stato di verifica.** «Osservato in sessione» indica un comando o un check di cui il raw riporta l'esito; il wiki-keeper non lo ha rieseguito. «Verificato dal keeper» indica un controllo sulla copia locale `.claude/` di questa factory, che è una copia del master e non il master stesso. «Dichiarato nel raw» indica un'affermazione senza comando né riga di evidenza nel raw: per la regola del protocollo di chiusura della factory è un'ipotesi finché non viene verificata. Il documento di sessione non contiene un'analisi di impatto né una priorità per i difetti.

## Dettaglio

### 1. `run-deterministic.py` esce con errore su console Windows cp1252
- **Sintomo.** `tools/lint/run-deterministic.py` esce con `UnicodeEncodeError` sulla console Windows cp1252 (riga 171, `print`). Funziona con `PYTHONUTF8=1 PYTHONIOENCODING=utf-8`.
- **Evidenza dichiarata.** Primo `/lint`: exit 1, poi exit 0.
- **Stato.** Osservato in sessione.

[^src: raw/sessions/session-2026-11-20-16-3649aa67.md §Insight]

### 2. `ingest-protocol` non descrive il ramo `repo`
- **Sintomo.** `ingest-protocol` descrive solo i rami `pdf` e `figma`: un raw `source: repo` è stato trattato come testo per analogia.
- **Evidenza dichiarata.** `.claude/skills/ingest-protocol.md`, Fase 1.
- **Stato.** Verificato dal keeper: nella copia locale la Fase 1 ha i rami `pdf` e `figma` [^code: .claude/skills/ingest-protocol.md:46-80]; la ricerca di `source: repo`, `ramo repo` e `repo-sync` nel file non dà risultati.

[^src: raw/sessions/session-2026-11-20-16-3649aa67.md §Insight]

### 3. L'hook `commit-msg` dei submodule riconosce solo ID con prefisso di namespace
- **Sintomo.** L'hook `commit-msg` installato nei submodule con `suppress_ai_traces` riconosce solo gli ID con prefisso di namespace (`[A-Z]{2,4}-(TSK|US|EP)-[0-9]+`). Un messaggio con `TSK-042` passa (exit 0), mentre `tools/vcs/ai_policy.py` `find_factory_ids` lo rileva. `Co-Authored-By` è bloccato correttamente (exit 1).
- **Evidenza dichiarata.** Test sull'hook del submodule, senza commit.
- **Stato.** Osservato in sessione. Il CLAUDE.md della factory dice che in `ai_policy.py` il prefisso di namespace è opzionale, coerente con la parte su `find_factory_ids`.

[^src: raw/sessions/session-2026-11-20-16-3649aa67.md §Insight]

### 4. Lo schema di configurazione non dichiara `ai_attribution_policy`
- **Sintomo.** `schemas/factory.config.schema.json` non dichiara `ai_attribution_policy` (PATTERN §23.9): `check-config-schema-coverage.py` esce con 1 finché la chiave non sta in `schema_local_keys`.
- **Evidenza dichiarata.** Exit code del check; la chiave è stata messa in `schema_local_keys` (decisione 6).
- **Stato.** Osservato in sessione.

[^src: raw/sessions/session-2026-11-20-16-3649aa67.md §Insight]

### 5. Il frontmatter minimo di `scrivi-wiki-page` non esenta `wiki/gaps.md`
- **Sintomo.** L'installer e il master scrivono `gaps.md` senza `sources` e `tags`, e il lint a lettura dà WARNING.
- **Evidenza dichiarata.** Nessuna riga di evidenza nel raw oltre all'affermazione. La decisione 9 tratta il WARNING come falso positivo.
- **Stato.** Dichiarato nel raw.

[^src: raw/sessions/session-2026-11-20-16-3649aa67.md §Insight]

### 6. Comandi solo del master citati da agenti presenti nelle derivate
- **Sintomo.** `.claude/agents/fleet-doctor.md` cita `/factory-upgrade` e `release-manager.md` cita `/release`. Sono comandi solo del master, assenti nelle derivate: Check 4ai.3 WARNING.
- **Evidenza dichiarata.** Check 4ai.3 WARNING.
- **Stato.** Verificato dal keeper nella copia locale: `fleet-doctor.md` cita `/factory-upgrade` alle righe 125 e 137 [^code: .claude/agents/fleet-doctor.md:125], `release-manager.md` cita `/release` alla riga 54 [^code: .claude/agents/release-manager.md:54]; in `.claude/commands/` non esistono `factory-upgrade` né `release` (esiste solo `release-artifact.md`).

[^src: raw/sessions/session-2026-11-20-16-3649aa67.md §Insight]

### 7. L'installer copia tutti i dev-agent qualunque sia la topologia
- **Sintomo.** Con la topologia `custom` l'installer imposta tutto il routing a human: Check 4c ERROR `orphan-dev-agent`. `factory-upgrade-apply.py` (non-destructive ADD) rimetterebbe un agente rimosso.
- **Evidenza dichiarata.** Check 4c ERROR. La parte su `factory-upgrade-apply.py` è espressa al condizionale.
- **Stato.** Il check è osservato in sessione; la previsione su `factory-upgrade-apply.py` è un'**ipotesi**, non eseguita.

[^src: raw/sessions/session-2026-11-20-16-3649aa67.md §Insight]

### 8. Il CQRL carica le regole senza filtrare per `status`
- **Sintomo.** Il CQRL carica le regole da `code_quality/rules/{team-specific,emergent,canonical}/**` senza filtrare per `status`: una regola in bozza sarebbe attiva subito.
- **Evidenza dichiarata.** `code-review-protocol/fase-0-bootstrap.md` §Input comune.
- **Stato.** Verificato dal keeper solo il glob sulle tre cartelle, con priorità team-specific > emergent > canonical [^code: .claude/skills/references/code-review-protocol/fase-0-bootstrap.md:101]. L'assenza di un filtro su `status` non è verificata nel resto del file. Collegamento con la decisione 8: le bozze sono in `code_quality/rules/proposte/`, cartella non letta dal reviewer.

[^src: raw/sessions/session-2026-11-20-16-3649aa67.md §Insight]

### 9. L'installer non copia le regole canonical
- **Sintomo.** L'installer non copia le regole canonical di `code_quality/rules/`: con `trigger_default` attivo e il ruleset vuoto la review va in ABORT («Regole vuote per stack»).
- **Evidenza dichiarata.** Nessuna riga di evidenza nel raw oltre all'affermazione.
- **Stato.** Dichiarato nel raw. Oggi `code_quality/rules/canonical/design-complexity.md` esiste, copiato a mano come da decisione 8.

[^src: raw/sessions/session-2026-11-20-16-3649aa67.md §Insight]

### 10. Il Check 4c legge solo `code_path` (legacy)
- **Sintomo.** Con `code_paths` multi-repo il Check 4c dà il WARNING `dev-agents-without-code-path` come falso positivo.
- **Evidenza dichiarata.** Check 4c WARNING.
- **Stato.** Osservato in sessione.

[^src: raw/sessions/session-2026-11-20-16-3649aa67.md §Insight]

### 11. Il Check 4ax suggerisce di modificare `.gitmodules`
- **Sintomo.** Il Check 4ax suggerisce di modificare `.gitmodules` (`ignore = dirty`), mentre PATTERN-integration vieta agli agenti di modificare `.gitmodules` fuori da vcs-handoff.
- **Evidenza dichiarata.** Nessuna riga di evidenza nel raw oltre all'affermazione.
- **Stato.** Dichiarato nel raw; non verificato dal keeper.

[^src: raw/sessions/session-2026-11-20-16-3649aa67.md §Insight]

## Pagine collegate
[[session-2026-11-20-16-3649aa67]], [[factory-decisioni-di-configurazione]].

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

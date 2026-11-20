# CLAUDE.md — wiki-factory

Factory creata dall'installer della Soli Multi-Agents Factory il 2026-11-20, PATTERN v2.48.
Questo file e' della factory: aggiungi stack, convenzioni e repository di codice del progetto.

Pattern autoritativo: [`PATTERN.md`](PATTERN.md) — indice §0-§11 + tabella §Moduli; §12+ in `PATTERN-{integration,runtime,governance,capabilities}.md`.
Capability per scenario d'uso, chiavi di `factory.config.yaml` e fonte di `/help`: [`CAPABILITIES.md`](CAPABILITIES.md).
Configurazione: [`factory.config.yaml`](factory.config.yaml) (topologia `custom`), schema in `schemas/factory.config.schema.json`.

## Adapter

| Adapter | Cartella | Maturita' |
|---|---|---|
| `claude` | `.claude/` | full |

## Comandi rapidi

```bash
/help <domanda>                                      # routing capability in linguaggio naturale
/run                                                 # stato progetto + prossimo passo (orchestrator)
/onboarding                                          # report contestuale per nuovi contributor
/sync-docs                                           # ingest PDF da raw/
/repo-sync <path>                                    # estrazione spec da un repo esistente
/query <domanda>                                     # query wiki (--ephemeral per non salvare)
/lint                                                # health check wiki + kanban
/dev <TSK-id>                                        # dev-agent sul TSK (layer con routing: agent)
/review <TSK-id>                                     # code review CQRL
python3 tools/lint/run-deterministic.py              # check deterministici
python3 tools/lint/check-version-coherence.py        # coerenza versioni (Check 4am)
```

Aggiornare la factory: dal clone del meta-framework,
`python3 tools/factory-upgrade-apply.py <questa-cartella> --dry-run`, poi `--apply`.

> Le sezioni che seguono vengono dal CLAUDE.md del meta-framework e valgono in ogni factory
> derivata: non ammorbidirle. Vanno riallineate a mano a ogni upgrade.

## Mapping ruoli PATTERN.md → file adapter

| Ruolo §2 | File |
|---|---|
| Orchestrator | `.claude/agents/orchestrator.md` |
| Sync (PDF) | `.claude/agents/sync-docs.md` |
| Sync (Figma, v2.9) | `.claude/agents/figma-sync.md` |
| Sync (Repo, v2.12) | `.claude/agents/repo-sync.md` |
| Analyst | `.claude/agents/wiki-keeper.md` |
| PM | `.claude/agents/product-manager.md` |
| Arch | `.claude/agents/lead-architect.md` |
| TPM | `.claude/agents/tpm.md` |
| Query | `.claude/agents/wiki-query.md` |
| Lint | `.claude/agents/wiki-lint.md` |
| BE-Dev (v2.7, opt) | `.claude/agents/be-dev.md` |
| FE-Dev (v2.7, opt) | `.claude/agents/fe-dev.md` |
| DB-Dev (v2.7, opt) | `.claude/agents/db-dev.md` |
| QA-Dev (v2.7, opt) | `.claude/agents/qa-dev.md` |
| Publisher GitHub (v2.10, opt) | `.claude/agents/github-publisher.md` |
| Code Reviewer (v2.12, opt) | `.claude/agents/code-reviewer.md` |
| Release Manager (v2.40, opt) | `.claude/agents/release-manager.md` |
| Fleet Doctor (v2.41, opt) | `.claude/agents/fleet-doctor.md` |
| Kanban Coordinator (v2.43, opt) | `.claude/agents/kanban-coordinator.md` |
| Security Interpreter (v2.48, opt) | `.claude/agents/security-interpreter.md` |
| Log Operator (v2.45, opt) | `.claude/agents/log-operator.md` |
| DB Operator (v2.45, opt) | `.claude/agents/db-operator.md` |
| Storage Operator (v2.48, opt) | `.claude/agents/storage-operator.md` |
| Cypress Test Analyst / Reviewer (v2.45, opt) | `.claude/agents/cypress-test-analyst.md`, `cypress-test-reviewer.md` |
| Ingest worker (v2.4, sub-agent) | `.claude/agents/wiki-keeper-worker.md` |

## Protocollo di chiusura — sempre attivo (v2.44, EP-068 US-298)

Ogni dev-agent, **prima** di scrivere in `wiki/log.md` e **prima** di mettere
`status: done`, esegue le verifiche di `.claude/skills/dev-handoff.md`
§«Protocollo di chiusura». Non e' gated da alcun flag, e vincola anche l'orchestratore
quando propaga lo stato a valle.

| | Regola |
|---|---|
| **Evidenza** | un'affermazione ambientale che non cita il comando eseguito e il suo esito e' un'**ipotesi**, anche se formulata come certezza. Non puo' motivare uno skip ne' dichiarare un AC soddisfatto |
| **Diff di chiusura** | i file toccati si confrontano **a comando** (`git status --short`, `git diff --name-only HEAD`), non a memoria. Tre campi distinti: dichiarati, committati, nel working tree. Un file toccato e non dichiarato non e' un errore — **non segnalarlo lo e'** |
| **Semantica di `done`** | lo stato si **deriva** dalla tabella AC, non si sceglie a parte. AC non verificato e non derogato → `in-progress` o `blocked`. La deroga resta legittima: l'obiettivo e' renderla impossibile **in silenzio** |
| **Date di lavoro** (EP-079) | chi cambia lo stato scrive `started_at` (→ `in-progress`) e `closed_at` (→ `done`), con la data del lavoro, non della registrazione. Check 4be, ERROR, dai cambi di stato da `kanban_dates.required_from` |

## §ai_policy — guardia di scope (invariante)

Per factory con un `code_path` di un cliente con `suppress_ai_traces: true`: usa
`tools/vcs/sm-commit.sh "messaggio"` per i commit nel repo cliente (non per i commit
del framework). Chiavi config e dettaglio layer-1/layer-2: [`CAPABILITIES.md` §Riferimento chiavi](CAPABILITIES.md) §ai_policy. Vedi anche PATTERN §23.9.

> **Guardia di scope, invariante.** Il repo della factory **non e' mai scansionato**,
> nemmeno se passato esplicitamente a `--repos`. Qui l'attribution AI nei commit del
> framework e' **dovuta**, non vietata: uno scan indiscriminato segnalerebbe ogni commit, e
> un check che urla sempre viene spento. Il tentativo produce un **rifiuto esplicito**, non
> uno skip silenzioso. Si scansionano solo i path dichiarati in `ai_policy_check.scope[]`.

`tools/vcs/ai_policy.py` e' la **fonte unica** dei pattern (attribution AI + ID kanban):
nessun altro file li ridefinisce. Il prefisso di namespace negli ID e' **opzionale**, cosi'
il modulo legge sia `TSK-690` (questa factory) sia `XX-TSK-268` (derivate multi-namespace).

`tools/vcs/sm_commit.py` (Python, cross-platform) applica i filtri e **avvisa** invece di
scartare in silenzio. Quando il messaggio viene **alterato**, il risultato si mostra e il
commit si **conferma** — `--yes` per l'uso non interattivo: rimuovere un ID incastonato
nella prosa rompe la frase, e committarlo in silenzio e' peggio che non filtrare affatto.

## §kanban_coordination — Cosa NON da' (vincolante, US-267 AC8)

Non ammorbidibile in nessun documento:

- **non impedisce la doppia presa** dello stesso TSK;
- **non risolve la contesa** a runtime: nessun lock, nessun lease, nessun arbitro;
- **non garantisce alcuna latenza**. La visibilita' e' al **ciclo di push**: minuti, non
  secondi. L'osservatore mostra lo stato **all'ultimo push** e dichiara quanto e' vecchio.

Un documento che lascia intendere il contrario e' un difetto, non una semplificazione.
Dettagli, tabella, oracolo asimmetrico e motivazione dell'arbitro non costruito: [`CAPABILITIES.md`](CAPABILITIES.md) §kanban_coordination.

## §visual_channel — Cosa NON fa (vincolante)

- **non e' uno scrittore**: ogni azione e' una `submit()`, lo scrittore resta la sessione;
- **non arbitra** la concorrenza: dichiara le altre sessioni, nessun lock ne' lease;
- la **mascotte non e' un canale di accesso**: e' codifica ridondante, sempre nascosta
  alle tecnologie assistive, mai unico veicolo di un'informazione;
- il verde WCAG **non dichiara «accessibile»**: la validazione con persone non c'e' — US-287 e' fuori
  scope (Q-007, esito (b), 2026-11-16) e la plancia non porta alcun claim di accessibilita'.

Configurazione e dettagli: [`CAPABILITIES.md`](CAPABILITIES.md) §visual_channel.

## Token Ledger (EP-022, v2.21)

`analytics.token_ledger.enabled: true` — **a fine di ogni risposta che include tool call, sub-agent o modifiche file**, esegui e mostra inline:

```bash
python3 tools/analytics/show-session-tokens.py
```

Output compatto (default) — oppure `--full` per il box completo. Questo sostituisce il
meccanismo hook `Stop` che non è visibile nella chat dell'estensione VS Code. Per altri
adapter (Cursor, Aider) il hook nel rispettivo adapter config gestisce la visualizzazione.
Invariante: mai omettere il token count se `token_ledger.enabled: true` e la risposta ha
prodotto lavoro concreto (modifica file, tool use, lancio agente).

**`/ponytail-gain` (EP-057, v2.39, opt-in)**: se `ponytail.enabled: true` e almeno un report
`code_quality/reports/ponytail-audit-*.md` esiste, `show-session-tokens.py` stampa una riga
aggiuntiva `◉ PONYTAIL  audit: <N> file  candidati: <M>  saving stimato: ~<K> righe`
(dall'ultimo audit). A flag spento o senza report la riga è omessa (fail-open, zero nuove
dipendenze). Alimentata da `/ponytail-audit`.

**Cost Alert (opt-in)**: con `analytics.cost_alert.enabled: true` il costo di sessione, giornata
e settimana si confronta con le soglie di `analytics/alert-rules.yaml` (`/cost-alert`, skill
`cost-alert-protocol`): regole generali e, per singolo operatore, regole personali (`operator`) o quota del piano di abbonamento (`plans`/`subscriptions`). Il ledger mostra il costo, cost-alert lo giudica: prima di lanciare agenti
segui `dispatch-policy` §13.

**Alternativa compatta (v2.40)**: `python3 tools/analytics/statusline-ledger.py` →
output su 1 riga (`◉ TOKENS  in: Xk  out: Yk  cost: $Z`); `--json` per machine-readable.
Degrada gracefully se il ledger non è attivo (exit 0, riga vuota).

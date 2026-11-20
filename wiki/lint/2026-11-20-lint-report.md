---
type: lint
date: 2026-11-20
heal_eligible_count: 0
heal_eligible_categories: []
---
# Lint Report — 2026-11-20

Factory `wiki-factory`, PATTERN v2.48, topologia `custom`. Esecutore: wiki-lint. Nessun auto-fix: solo report.

Report deterministico completo (righe di dettaglio non trascritte): [2026-11-20-deterministic.md](2026-11-20-deterministic.md).

## Popolazione effettiva letta

| Fonte | Valore letto |
|---|---|
| Pagine wiki (`wiki/**`, esclusi `lint/`) | 15 file: 12 pagine di contenuto (1 source, 9 concept, 2 entity) + `index.md`, `log.md`, `gaps.md` |
| Check 1 (script) | `Check 1 completato su 13 file — 0 orphan rilevati, 0 broken-link rilevati` |
| Kanban | `[3] popolazione: 0 EP, 0 US, 0 TSK`; `management/kanban/` vuota, `management/questions.md` con `[APERTE]` e `[CHIUSE]` vuote |
| File tracciati da git (`git ls-files`) | 3 voci: `.gitmodules`, `README.md`, gitlink `code_repos/llm_wiki` (e08cfce65aad8b76b13546a081c1a8d4422b70c3, `heads/develop`) |
| Contenuto di HEAD (`git ls-tree -r HEAD`) | solo `README.md` |
| Commit che toccano `wiki/log.md` e `wiki/gaps.md` | 0 (`[4bb] 0 commit di wiki/log.md esaminati`, `[4bd] 0 commit di wiki/gaps.md esaminati`) |

Conseguenza: i check che leggono la storia git o i soli file tracciati (4bb, 4bd, 4be, 4bj, 4bn, 4aq) girano su una popolazione quasi vuota; il loro esito pulito non dice nulla su `wiki/`, `raw/`, `tools/`, `.claude/`, che sono untracked. Vedi sezione INFO.

## Riepilogo deterministico (script, `run-deterministic.py`)

Exit code del runner: 0. Totale script: 0 ERROR, 6 WARNING, 0 INFO.

| Check | Cosa | ERROR | WARNING | INFO | Exit |
|---|---|---|---|---|---|
| 1, 4, 4ag | Struttura wiki: orphan, broken-link, storie collegate, staleness | 0 | 0 | 0 | 0 |
| 3, 4as, 4b | Integrita' kanban, assignee, question | 0 | 0 | 0 | 0 |
| 4au | Roll-up di stato TSK, US, epica e sprint.md | 0 | 0 | 0 | 0 |
| 4am | Coerenza delle versioni dichiarate | 0 | 0 | 0 | 0 |
| 4ar | Annotazioni SUNSET scadute | 0 | 0 | 0 | 0 |
| 4aq | Path portabili su Windows | 0 | 0 | 0 | 0 |
| 4ax | ignore = dirty sui submodule | 0 | 1 | 0 | 0 |
| 4bb | wiki/log.md append-only | 0 | 0 | 0 | 0 |
| 4bc | Chiusure dei gap verificate | 0 | 0 | 0 | 0 |
| 4bd | wiki/gaps.md append-only | 0 | 0 | 0 | 0 |
| 4be | Date di lavoro dei TSK | 0 | 0 | 0 | 0 |
| 4bf, 4bg | Ordine del log, contatore Sources | 0 | 0 | 0 | 0 |
| 4bh | Evidenza di test sui TSK be (regola spenta) | 0 | 0 | 0 | 0 |
| 4bi | Tracciabilita' design (spento) | 0 | 0 | 0 | 0 |
| 4bj | Segreti nei file tracciati (gitleaks) | 0 | 0 | 0 | 0 |
| 4bl | Path assoluti in `.claude/settings.json` | 0 | 0 | 0 | 0 |
| 4bk | Agenti lettori di contenuto non fidato con Bash | 0 | 3 | 0 | 0 |
| 4g | depends_on e scheduler | 0 | 0 | 0 | 0 |
| 4ai | Integrita' del layer agenti | 0 | 2 | 0 | 0 |
| 4aj, 4bm | `model:` degli agenti contro il registro | 0 | 0 | 0 | 0 |
| 4bn | Marcatori di conflitto su HEAD | 0 | 0 | 0 | 0 |
| 4bo | Lettori diretti del registro sessioni | 0 | 0 | 0 | 0 |
| 4j | Repository risolvibile sui TSK (regola spenta) | 0 | 0 | 0 | 0 |
| **Totale** | | **0** | **6** | **0** | 0 |

## Riepilogo check a lettura

| Check | Errors | Warnings | Note |
|---|---|---|---|
| 1 — Orphan + wikilink | 0 | 0 | script; verifica indipendente: 90 wikilink in 15 file, 0 rotti |
| 2 — Claim senza fonte | 0 | 0 | 14 file con prosa (log escluso) scansionati per riga, soglia 20 parole, finestra 3 righe: 0 claim non citati |
| Citation audit | 0 | 0 | 113 citazioni `[^src: ...]`, path e sezione verificati: 0 rotte (inline, nessun file separato) |
| 3 — Integrita' kanban | 0 | 0 | script, popolazione 0 |
| 4 — Coerenza wiki↔kanban | 0 | 0 | script, 12 sezioni «Storie collegate», nessuna storia |
| 4b — Coerenza Q↔kanban | 0 | 0 | script, 0 question aperte/risolte |
| 4c — Topology/routing | 2 | 1 | vedi sotto; famiglia config non obbligatoria (flag spenti), eseguita comunque |
| 4d — Coerenza VCS | 0 | 1 | vedi sotto |
| 4e — Manifest↔raw | 0 | 0 | 1 entry, primary e secondary esistenti |
| 4f — Publisher | 0 | 0 | `kanban_publish.provider: none` |
| 4g — Scheduler/depends_on | 0 | 0 | script, 0 artefatti |
| 4ah — Branch Awareness config | 0 | 0 | blocco presente, `enabled: false`, nessun sotto-flag |
| 4ai — Agent infrastructure | 0 | 2 | script |
| 4ak — content_share | — | — | skip, `content_share.enabled: false` |
| 4am — Versioni | 0 | 0 | script, `SSOT factory.config.yaml#pattern_version = 2.48` |
| 4at — Disciplina d'ingresso | — | — | NON ESEGUITO (esecutore assente) |
| 4ag — Staleness | — | 0 | script, 12 file, 0 MISSING-DATE, 0 STALE |
| Struttura frontmatter wiki | 0 | 1 | vedi WARNING |

## ERROR meccanici (heal-eligible)

Nessuno. `heal_eligible_count: 0`. Nessun broken-wikilink, nessun citation-section-mismatch, nessun missing-frontmatter-field di tipo ERROR.

## ERROR non meccanici

- [ERROR][orphan-dev-agent][4c] `.claude/agents/db-dev.md` (heal-eligible: false). Valore letto: `factory.config.yaml` riga 98 `  db: human`. La regola (`lint-checks-config.md` riga 25-26, check 4c) richiede `routing.db: agent` per ogni `<X>-dev.md` presente. Fix suggerito, due strade alternative che spettano al proprietario: (a) portare `routing.db` ad `agent`; (b) rimuovere o archiviare `db-dev.md`. Nota: la config dichiara a riga 94 «db, infra, docs umani» come scelta voluta della topologia `custom`, quindi il disallineamento nasce dal fatto che l'installer ha copiato comunque gli agenti non instradati. Se la scelta e' (b) per entrambi gli agenti, e' un intervento sulla flotta, non sul wiki.
- [ERROR][orphan-dev-agent][4c] `.claude/agents/docs-dev.md` (heal-eligible: false). Valore letto: `factory.config.yaml` riga 101 `  docs: human`. Stessa regola e stesse due strade del finding precedente. Il layer `docs` e' nell'enum dello schema (`schemas/factory.config.schema.json` riga 223, `"docs": { "type": "string", "enum": ["agent", "human"] }`).

## WARNING (igiene, mai heal-eligible)

Da script (testo del finding invariato, dettaglio nel file deterministico):

- [WARNING][submodule-ignore-missing][4ax] `.gitmodules` riga 1 (sezione `[submodule "code_repos/llm_wiki"]`, righe 1-4, nessun `ignore`). Valore letto dallo script: `submodule "code_repos/llm_wiki" con nessun ignore: ogni git status sul padre apre un processo dentro questo submodule`. Fix suggerito: `git config -f .gitmodules submodule.code_repos/llm_wiki.ignore dirty`. Lo script etichetta il finding «heal-eligible»; per il contratto del wiki-lint e per la whitelist di `heal-protocol` (solo broken-wikilink, missing-frontmatter-field, citation-section-mismatch) un WARNING non e' mai heal-eligible: qui e' trattato come non eligible. Nota di coerenza tra script e contratto, non un difetto della factory.
- [WARNING][ingest-tools][4bk] `.claude/agents/figma-sync.md` riga 5 `tools: [Read, Write, Edit, Glob, Bash]`; capability `raw-sync` e `figma-extraction` (righe 7-8): legge contenuto non fidato, dichiara Bash e non ha eccezione. Fix suggerito: togliere `Bash` da `tools:` oppure aggiungere un'eccezione con `agente`, `motivo`, `scade` in `ingest_agent_tools.exceptions` di `factory.config.yaml` (blocco oggi assente).
- [WARNING][ingest-tools][4bk] `.claude/agents/graphify-sync.md` riga 5 `tools: [Read, Write, Edit, Glob, Bash]`; capability `raw-sync` e `graph-extraction` (righe 7-8). Stesso fix.
- [WARNING][ingest-tools][4bk] `.claude/agents/session-sync.md` riga 5 `tools: [Read, Write, Edit, Glob, Bash]`; capability `raw-sync` e `session-extraction` (righe 7-8). Stesso fix.
- [WARNING][agent-command-missing][4ai.3] `.claude/agents/fleet-doctor.md` riga 125 (`Azione: /factory-upgrade <external_path> --to=v2-41 --apply`, anche riga 137): referenzia il comando `/factory-upgrade` ma `.claude/commands/factory-upgrade.md` non esiste (letto con `ls .claude/commands`: nessun `factory-upgrade.md`). Fix suggerito: aggiungere il comando o correggere il nome nell'agente; l'upgrade documentato in `CLAUDE.md` passa da `tools/factory-upgrade-apply.py` dal clone del meta-framework.
- [WARNING][agent-command-missing][4ai.3] `.claude/agents/release-manager.md` riga 54 (`Invocazione esplicita /release <VERSION> [<branch>] [<description>]`): referenzia il comando `/release` ma `.claude/commands/release.md` non esiste (in `.claude/commands/` c'e' `release-artifact.md`, non `release.md`). Stesso fix.

Da lettura:

- [WARNING][dev-agents-without-code-path][4c] `factory.config.yaml` riga 62 `code_path: ""`, con `topology: custom` (riga 50) e `routing` con `be`, `fe`, `qa` a `agent` (righe 96-99). La lettera della regola (`lint-checks-config.md` riga 29-30) da' WARNING. Contesto letto: `code_paths` (riga 72 in poi) e' valorizzato con la entry `llm_wiki`, e il commento a righe 60-61 dice che con `code_path` vuoto la factory usa `code_paths:`. Probabile falso positivo semantico della regola v2.7 su una factory multi-repo v2.12; si riporta perche' la regola non menziona `code_paths`. Fix suggerito: nessuna modifica alla config; decisione di chi mantiene il check.
- [WARNING][missing-factory-lock][4d] `.factory-lock` assente alla radice (`ls .factory-lock`: `No such file or directory`). Valore letto: `factory.config.yaml` riga 83 `      commit_coupling: pin` nella entry `code_paths[0].vcs` (`mode: submodule`, `submodule_path: code_repos/llm_wiki`). Regola 4d: con `commit_coupling: pin` il file deve esistere almeno con header. Fix suggerito: creare `.factory-lock` oppure portare `commit_coupling` a `float`. Il pin attuale e' comunque registrato dal gitlink in stage (`git submodule status`: ` e08cfce65aad8b76b13546a081c1a8d4422b70c3 code_repos/llm_wiki (heads/develop)`).
- [WARNING][missing-frontmatter-field][struttura wiki] `wiki/gaps.md` righe 1-7. Valore letto: frontmatter con `type: gap`, `status: draft`, `created`, `updated`, `append_only: true`; mancano `sources` e `tags`. La skill `scrivi-wiki-page` §Frontmatter minimo elenca `sources` e `tags` e include `gap` tra i valori di `type`. Non e' un check codificato in `lint-checks*` (nessuna regola enumera i campi obbligatori delle pagine wiki), per questo e' WARNING e non ERROR; non e' deducibile dal path, quindi non heal-eligible. Fix suggerito: decidere se `gaps.md` e' esente dal frontmatter minimo (e dichiararlo nella skill) oppure aggiungere `sources: []` e `tags: [gaps]`. Attenzione: `gaps.md` e' append-only, la modifica del frontmatter spetta a wiki-keeper.

## INFO

- [INFO][popolazione-git][4bb, 4bd, 4be] Nessun commit oltre `init` (`git ls-tree -r HEAD`: solo `README.md`). 4bb e 4bd riportano `0 commit esaminati`, 4be `nessun TSK con date mancanti`: sono esiti vuoti, non verifiche sul contenuto. Gli append-only di `wiki/log.md` e `wiki/gaps.md` non sono verificabili finche' non esiste un primo commit che li contiene.
- [INFO][popolazione-git][4bn] Il check legge HEAD (`git ls-tree`: solo `README.md`): `wiki/log.md`, `wiki/gaps.md`, `wiki/index.md`, `raw/.extraction-manifest.json` non sono su HEAD, quindi «nessun marcatore di conflitto» non li ha esaminati.
- [INFO][popolazione-git][4bj] `gitleaks: nessun finding su 2 file`: sono i file di `git ls-files` (`.gitmodules`, `README.md`). `wiki/`, `raw/`, `tools/`, `.claude/` e `factory.config.yaml` sono untracked e non scansionati. Rielanciare il check dopo il primo commit. Lo zero di secret nel raw (`raw/2026-11-20-repo-llm_wiki.md` §Note di estrazione) vale per 30 file su 476, come dichiarato dal gap `llm-wiki-scan-credenziali`.
- [INFO][popolazione-git][4aq] `path tracciati: 3`: la verifica di portabilita' dei path non copre i file untracked. I path di `wiki/` e `raw/` letti a vista usano solo caratteri ammessi (`raw/images/2026-11-20-repo-llm_wiki-tree.md`, `wiki/concepts/llm-wiki-*.md`).
- [INFO][kanban-vuoto] Check 3, 4, 4b, 4g, 4m, 4as, 4au, 4be, 4bh, 4bi, 4j sono vacui: 0 EP, 0 US, 0 TSK, 0 question. Nessun `risk_classification` (4m no-op), nessun `management/risk-registry.md`.
- [INFO][config] Nessun blocco `lint:` in `factory.config.yaml` (valgono le regole di default del master) e nessun `tools/lint/checks_locali.py` (`ls tools/lint`): nessun check locale della factory. Nessuna eccezione `ingest_agent_tools` dichiarata.
- [INFO][4f] `kanban_publish.provider: none` (riga 132), `kanban_publish` non ha le chiavi `mode`, `target`, `auth_env`: coerente con provider spento, nessun finding.
- [INFO][4aj] Superato da 4bm (script): `[4bm] OK — 44 agenti, model: coerente con il registro dei modelli`. `ls .claude/agents/*.md | wc -l` = 44.
- [INFO][log] `wiki/log.md`: 1 entry di ingest (`## [2026-11-20] ingest | 2026-11-20-repo-llm_wiki`). I conteggi dichiarati («Pagine create: 12, Figure: 1, Gap nuovi: 12») coincidono con quanto letto: 12 pagine create (1 source + 9 concept + 2 entity), 12 intestazioni `## 2026-11-20 15:31 — <slug>` in `wiki/gaps.md`, 1 companion in `raw/images/`. Slug dei gap: lunghezza massima 31 caratteri (limite 40), tutti univoci.
- [INFO][gaps] `wiki/gaps.md`: il riferimento alla fonte nei gap e' testo semplice («Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti»), non nella forma `[^src: ...]`. `citation-rules` non lo richiede per i gap; la sezione `§Gap evidenti` esiste (riga 204 del raw). Nessun finding.
- [INFO][raw-partial] La fonte e' `partial` (30 file su 476) per dichiarazione del manifest (`raw/.extraction-manifest.json`: `"status": "partial"`, `"files_sampled": 30`, `"files_total_in_repo": 476`). Le 12 pagine lo riportano e i 12 gap aperti coprono le lacune; nessun gap chiuso, quindi 4bc ha esaminato 12 gap senza chiusure da verificare.

## Check NON ESEGUITI o saltati

| Check | Stato | Motivo |
|---|---|---|
| 4at — disciplina d'ingresso capability | NON ESEGUITO | l'esecutore dichiarato e' `pytest tests/test_fleet_contract.py -k asse4`: `tests/` non esiste in questa factory (`find . -name "test_fleet_contract*"` senza risultati) e Bash e' limitato agli script di `tools/lint/` e `tools/kanban/`. Lettura parziale, non sostitutiva: tra le chiavi top-level con `enabled:` solo `ai_policy_check` (righe 120-121, `enabled: true`) non e' nell'allowlist; `grep` su `PATTERN*.md`, `.claude/skills/lint-checks*.md` e `wiki/` non trova `ai_policy_check` ne' `ai-policy-check`, e `wiki/runbooks/` non esiste. Il passo 5 (metrica `observe.py --load`) non e' stato eseguito. Il verdetto va chiesto al test |
| 4an | NON ESEGUIBILE | citato nell'header di `lint-checks-wiki-structure.md` ma senza sezione nel file: nessuna specifica da applicare |
| 4af | saltato | `wiki_lint.semantic_check.enabled: false` |
| 4ak | saltato | `content_share.enabled: false` |
| 4ah | eseguito, 0 finding | blocco `vcs.branch_awareness` presente con `enabled: false`; `.factory-branches.yaml` assente (esiste solo `.factory-branches.yaml.example`) |
| 4v, 4w, 4x | saltati | `complexity_budget` assente in config; `release_governance.battle_test_gate.enabled: false` |
| 4al | saltato | `CHANGELOG.md` assente: skip silenzioso previsto dalla regola |
| 4ad, 4ae | saltati | `qa_layer.failure_taxonomy.enabled: false`, `qa_layer.flakiness_detection.enabled: false` |
| 4ap | saltato | `refactor_agent_skills` assente in config |
| FE quality (4n, 4o, 4p, 4ac, 4y, 4ao) | saltati | `fe_correctness.enabled: false`, `a11y.enabled: false` |
| Compression (4s, 4u, 4aa, 4ab, 4ab-bis) | saltati | `compression.output.enabled: false`, `compression.context.enabled: false` |
| Oracle/analytics (4z, 4q, 4r) | saltati | `fe_correctness.functional_oracle.enabled: false`, nessun task analytics nel kanban |
| 4bh, 4bi, 4j | script, regola spenta | `lint.kanban.be_test_evidence: off`, `design_traceability.enabled` non true, `lint.kanban.tsk_target: off` |

Nota sulla famiglia config: per `lint-checks.md` il modulo `lint-checks-config.md` e' obbligatorio solo con `vcs.branch_awareness.enabled`, `kanban_publish.provider != none` o `content_share.enabled`; nessuna delle tre condizioni e' vera (`enabled: false`, `provider: none`, `enabled: false`). I check 4c, 4d, 4e sono stati eseguiti comunque perche' la factory ha un submodule e un manifest; i loro finding sono riportati sopra.

## Citation audit (inline)

Metodo: script di sola lettura (nel scratchpad di sessione, non nel repo) che estrae ogni `[^src: <path> §<sez>]` da `wiki/**` (esclusi `lint/`), verifica che il path esista e che `<sez>` coincida con un header markdown del file citato.

| Misura | Valore |
|---|---|
| File wiki con citazioni | 15 (include index, log, gaps) |
| Citazioni totali | 113 |
| Malformate | 0 |
| Path inesistente | 0 |
| Sezione assente nel file citato | 0 |
| Wikilink interni (doppia parentesi quadra) totali | 90, tutti risolti a uno slug esistente |
| Path in `sources:` del frontmatter | `raw/2026-11-20-repo-llm_wiki.md` e `raw/images/2026-11-20-repo-llm_wiki-tree.md`, entrambi esistenti |

File citati: `raw/2026-11-20-repo-llm_wiki.md` (header letti: Identità, Stack rilevato, Struttura ad alto livello, Entrypoint e moduli chiave, API surface (se rilevata), Server MCP, Superficie di sicurezza, Schema dati (se rilevato), Dipendenze esterne, Vincoli normativi / Standard, Documenti correlati nel repo, Test coverage rilevato, Gap evidenti, Note di estrazione, Specifiche estratte: llm-wiki) e `raw/images/2026-11-20-repo-llm_wiki-tree.md` (header `Albero filesystem — llm_wiki (depth 3)`).

Limite dichiarato: la verifica e' di forma (esistenza di path e header), non di fedelta' del contenuto citato; il contenuto non e' stato riconfrontato frase per frase con il raw.

Check 2 (claim senza fonte): ogni riga di prosa con almeno 20 parole (escluse intestazioni, frontmatter, blocchi di codice, commenti) ha una citazione `[^src: ...]` o un wikilink nella stessa riga o nelle 3 successive. Risultato: 0 unsourced-claim su 14 file (il log, append-only, e' escluso dallo scan). Il controllo e' euristico a livello di riga; non separa le frasi dentro una riga.

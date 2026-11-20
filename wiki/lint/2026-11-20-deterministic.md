## Check eseguiti da script

Data di riferimento: 2026-11-20. Comando: `python3 tools/lint/run-deterministic.py`.

| Check | Cosa | ERROR | WARNING | INFO | Exit |
|---|---|---|---|---|---|
| 1, 4, 4ag | Struttura wiki: orphan, broken-link, storie collegate, staleness | 0 | 0 | 0 | 0 |
| 3, 4as, 4b | Integrita' kanban, assignee, question | 0 | 1 | 0 | 0 |
| 4au | Roll-up di stato TSK -> US -> epica e sprint.md | 0 | 1 | 1 | 0 |
| 4am | Coerenza delle versioni dichiarate | 0 | 0 | 0 | 0 |
| 4ar | Annotazioni SUNSET scadute | 0 | 0 | 0 | 0 |
| 4aq | Path portabili su Windows | 0 | 0 | 0 | 0 |
| 4ax | ignore = dirty sui submodule di .gitmodules | 0 | 1 | 0 | 0 |
| 4bb | wiki/log.md append-only (ultimo commit che lo tocca) | 0 | 0 | 0 | 0 |
| 4bc | Chiusure dei gap verificate sulla wiki | 0 | 0 | 0 | 0 |
| 4bd | wiki/gaps.md append-only (ultimo commit che lo tocca) | 0 | 0 | 0 | 0 |
| 4be | Date di lavoro dei TSK (started_at, closed_at) dalla data di adozione | 0 | 0 | 0 | 0 |
| 4bf, 4bg | Ordine delle voci di wiki/log.md e contatore Sources dell'index | 0 | 0 | 0 | 0 |
| 4bh | Evidenza di test sui TSK layer be chiusi (regola lint.kanban.be_test_evidence) | 0 | 0 | 0 | 0 |
| 4bi | Tracciabilita' decisione -> requisito -> task (design_traceability, solo forma) | 0 | 0 | 0 | 0 |
| 4bj | Segreti nei file tracciati (oracolo gitleaks; WARN; ERROR da secrets_guard.required_from) | 0 | 1 | 0 | 0 |
| 4bl | Path assoluti o fuori repo in .claude/settings.json (WARN; ERROR da settings_paths_check.required_from) | 0 | 0 | 0 | 0 |
| 4bk | Agenti che leggono contenuto non fidato con Bash nei tools (WARN; ERROR da ingest_agent_tools.required_from) | 0 | 0 | 0 | 0 |
| 4g | depends_on e scheduler: tipo, orfani, cicli, code_path, blocked_by, blocco scheduler: | 0 | 0 | 2 | 0 |
| 4ai | Integrita' del layer agenti: tool in whitelist, skill e comandi referenziati esistenti | 0 | 2 | 0 | 0 |
| 4aj, 4bm | model: degli agenti coerente con il registro models: (fuori registro, override disatteso) | 0 | 0 | 0 | 0 |
| 4bn | Marcatori di conflitto nei file in coda e append-only su HEAD (WARN) | 0 | 0 | 0 | 0 |
| 4bo | Lettori diretti di memory/active-sessions.yaml, senza registry_path() (WARN) | 0 | 0 | 0 | 0 |
| 4j | Repository risolvibile sui TSK aperti degli agenti (regola lint.kanban.tsk_target) | 0 | 0 | 0 | 0 |

**Totale script**: 0 ERROR, 6 WARNING, 3 INFO

### 1, 4, 4ag — Struttura wiki: orphan, broken-link, storie collegate, staleness

`python3 tools/lint/check-wiki-structure.py --root . --oggi 2026-11-20`

```
Check 1 completato su 26 file — 0 orphan rilevati, 0 broken-link rilevati
Check 4 completato su 25 sezioni «Storie collegate»
Check 4ag completato su 22 file (oggi=2026-11-20) — 0 MISSING-DATE, 0 STALE, 0 INFO
```

### 3, 4as, 4b — Integrita' kanban, assignee, question

`python3 tools/lint/check-kanban-integrity.py --root .`

```
- [WARNING][questions][4b] US-018: orphan-pending-clarification — Q_004 non citata nel pending_clarification di alcun ADR
[3] popolazione: 4 EP, 34 US, 10 TSK (aperti e chiusi, archivio incluso)
[4b] question lette: 1 aperte, 0 risolte
[3/4as/4b] 0 ERROR, 1 WARNING — 4b/questions=1
```

### 4au — Roll-up di stato TSK -> US -> epica e sprint.md

`python3 tools/lint/check-status-rollup.py --root .`

```
- [WARNING][status-rollup][4au.1] management/kanban/EP-001-difetti-master-analisi-e-segnalazione/US-012-convenzioni-segnalazione-master/US-012.md
  US status=in_progress — tutti i 1 TSK sono terminali
- [INFO][status-rollup][4au.5] management/kanban/sprint.md
  1 righe con ultima colonna che non e' uno stato, non confrontate (es. EP-002)
[Passo 1] Raccolti: 4 EP, 34 US, 10 TSK
[4au.5] sprint.md: 5 righe lette (forma rilevata: EP-level=1, TSK-level=4 — status in ultima colonna)
Riepilogo 4au: 4au.1=1, 4au.2=0, 4au.3=0, 4au.4=0, 4au.5=1, 4au.6=0, 4au.7=0
```

### 4am — Coerenza delle versioni dichiarate

`python3 tools/lint/check-version-coherence.py --root .`

```
SSOT factory.config.yaml#pattern_version = 2.48
Root: /home/user/wiki-factory
Profilo: derived
Non applicabili al profilo derived (5): CLAUDE.md, README.md, management/kanban/sprint.md, .claude/commands/factory-bootstrap.md, meta-prompts/README.md
OK — tutti i siti di dichiarazione concordano su 2.48
```

### 4ar — Annotazioni SUNSET scadute

`python3 tools/lint/check-expired-sunset.py .`

```
[4ar] OK — nessuna annotazione SUNSET scaduta
```

### 4aq — Path portabili su Windows

`python3 tools/lint/check-portable-paths.py`

```
path tracciati: 1057
OK — ogni path e' scrivibile su Windows, macOS e Linux
```

### 4ax — ignore = dirty sui submodule di .gitmodules

`python3 tools/lint/check-submodule-ignore.py .`

```
## WARNING (prestazioni, heal-eligible)
- [WARNING][submodule-ignore-missing][4ax] .gitmodules: submodule "code_repos/llm_wiki" con nessun `ignore`: ogni `git status` sul padre apre un processo dentro questo submodule. Heal: git config -f .gitmodules submodule.code_repos/llm_wiki.ignore dirty

Totale: 1 submodule senza `ignore = dirty`
```

### 4bb — wiki/log.md append-only (ultimo commit che lo tocca)

`python3 tools/lint/check-log-append-guard.py .`

```
[4bb] OK — 1 commit di wiki/log.md esaminati, nessuna riga tolta senza archivio
```

### 4bc — Chiusure dei gap verificate sulla wiki

`python3 tools/lint/check-gap-closures.py .`

```
[4bc] OK — 35 gap, nessuna chiusura non verificata
```

### 4bd — wiki/gaps.md append-only (ultimo commit che lo tocca)

`python3 tools/lint/check-gaps-append-guard.py .`

```
[4bd] OK — 1 commit di wiki/gaps.md esaminati, nessuna riga tolta
```

### 4be — Date di lavoro dei TSK (started_at, closed_at) dalla data di adozione

`python3 tools/lint/check-date-lavoro.py .`

```
[4be] OK — nessun TSK con date mancanti (dal 2026-11-20)
```

### 4bf, 4bg — Ordine delle voci di wiki/log.md e contatore Sources dell'index

`python3 tools/lint/check_dati_derivati.py .`

```
[4bf-4bg] OK — ordine di wiki/log.md entro 7 giorni (0 retrodatazioni tollerate), contatore Sources coerente
```

### 4bh — Evidenza di test sui TSK layer be chiusi (regola lint.kanban.be_test_evidence)

`python3 tools/lint/check_evidenza_test_be.py --root .`

```
[4bh] regola spenta (lint.kanban.be_test_evidence: off)
```

### 4bi — Tracciabilita' decisione -> requisito -> task (design_traceability, solo forma)

`python3 tools/lint/check_tracciabilita_design.py --root .`

```
[4bi] spento (design_traceability.enabled non e' true)
```

### 4bj — Segreti nei file tracciati (oracolo gitleaks; WARN; ERROR da secrets_guard.required_from)

`python3 tools/lint/check-secrets.py --root . --oggi 2026-11-20`

```
- [WARNING][secrets][4bj] verifica non eseguita: NON_VERIFICABILE: gitleaks assente (non nel PATH ne' nei percorsi noti): va installato. Nessuna verifica dei segreti e' avvenuta (previene nel percorso cooperativo, rileva negli altri).
```

### 4bl — Path assoluti o fuori repo in .claude/settings.json (WARN; ERROR da settings_paths_check.required_from)

`python3 tools/lint/check-settings-paths.py --root . --oggi 2026-11-20`

```
[4bl] OK — nessun path assoluto o fuori repo in .claude/settings.json
```

### 4bk — Agenti che leggono contenuto non fidato con Bash nei tools (WARN; ERROR da ingest_agent_tools.required_from)

`python3 tools/lint/check-ingest-agent-tools.py --root . --oggi 2026-11-20`

```
[4bk] OK — nessun lettore di contenuto non fidato con Bash fuori da eccezioni valide
```

### 4g — depends_on e scheduler: tipo, orfani, cicli, code_path, blocked_by, blocco scheduler:

`python3 tools/lint/check-depends-on.py --root .`

```
- [INFO][code-path-overlap][4g] TSK-006, TSK-007, TSK-008, TSK-009 condividono code_path wiki/** al level 0: lo scheduler li serializza
- [INFO][dependencies-drift-candidate][4g] TSK-005: ## Dependencies e depends_on differiscono (solo corpo: -; solo frontmatter: TSK-003, TSK-004)
[4g] 48 artefatti, 34 con depends_on, 44 archi nel grafo
```

### 4ai — Integrita' del layer agenti: tool in whitelist, skill e comandi referenziati esistenti

`python3 tools/lint/check-agent-infrastructure.py --root .`

```
- [WARNING][agent-command-missing][4ai.3] .claude/agents/fleet-doctor.md: referenzia comando /factory-upgrade ma .claude/commands/factory-upgrade.md non esiste.
- [WARNING][agent-command-missing][4ai.3] .claude/agents/release-manager.md: referenzia comando /release ma .claude/commands/release.md non esiste.
```

### 4aj, 4bm — model: degli agenti coerente con il registro models: (fuori registro, override disatteso)

`python3 tools/lint/check-model-tier.py --root .`

```
[4bm] OK — 44 agenti, model: coerente con il registro dei modelli
```

### 4bn — Marcatori di conflitto nei file in coda e append-only su HEAD (WARN)

`python3 tools/lint/check_marcatori_conflitto.py .`

```
[4bn] OK — nessun marcatore di conflitto nei file in coda su HEAD
```

### 4bo — Lettori diretti di memory/active-sessions.yaml, senza registry_path() (WARN)

`python3 tools/lint/check_lettori_registro_sessioni.py --root .`

```
OK lettori-registro-sessioni: nessun lettore diretto di memory/active-sessions.yaml
```

### 4j — Repository risolvibile sui TSK aperti degli agenti (regola lint.kanban.tsk_target)

`python3 tools/lint/check_target_tsk.py --root .`

```
[4j] regola spenta (lint.kanban.tsk_target: off)
```

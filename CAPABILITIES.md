# Capability della factory — per scenario d'uso

> Copia per factory derivata, generata da `tools/factory_scope.py`: senza i comandi del meta-framework e con i rimandi a pagine che questa factory non ha resi come testo.

## Come leggere questo documento

Ogni sezione risponde a una domanda concreta: "quando devo fare X, quale capability uso?".
Ogni riga di tabella e' un punto di ingresso operativo: il comando e' eseguibile direttamente,
l'agente e' il motore che lo esegue. La colonna **Approfondimento** linka alle pagine wiki
con il design dettagliato della capability (concept, runbook). Un trattino (`—`) indica che
non esiste ancora una pagina wiki dedicata.

Questo file e' l'**indice operativo corrente** ed e' la fonte che `/help` interroga. La
mappa di design `wiki/concepts/capability-map.md` copre
il ragionamento per cluster ma e' allineata alla v2.23: in caso di divergenza vale questo
file (o, per i flag, `factory.config.yaml`).

---

## Nota: capability sempre attive e capability opt-in

Alcune capability sono **sempre attive** in ogni factory (colonna "Sempre attiva?" = si).
Altre sono **opt-in**: disabilitate di default, si abilitano impostando il flag indicato
in `factory.config.yaml`. Un flag spento = comportamento identico alla versione precedente
(nessun impatto su factory esistenti).

---

## Quando sono nuovo o non so quale capability usare

| Capability | Comando / Agente | Sempre attiva? | Quando usarla | Approfondimento |
|---|---|---|---|---|
| Onboarding in-chat | `/onboarding` | si | Sei nuovo sulla factory: report contestuale (versione, TSK facili, 5 invarianti, next step) senza scrivere file | — |
| Router capability | `/help <domanda>` | si | Hai una domanda in linguaggio naturale e vuoi il comando/agente giusto | questo file (`CAPABILITIES.md`) |
| Da dove partire | leggi `docs/START-HERE.md` (o `.it.md`) | si | Vuoi un ordine di lettura per il tuo ruolo: valutare, usare, estendere, governare | START-HERE |

---

## Quando devo ingestare nuovi dati nella knowledge base

| Capability | Comando / Agente | Sempre attiva? | Quando usarla | Approfondimento |
|---|---|---|---|---|
| Ingest PDF | `/sync-docs` + `sync-docs` | si | Hai un PDF in `raw/` da trasformare in wiki. Le figure le estrae prima lo script deterministico `tools/sync/pdf_figures.py` (JPEG/JPEG 2000 copiati, FlateDecode come PNG, pagina se ricavabile, limite di decompressione; cio' che non sa trattare lo dichiara); l'agente, senza Bash, scrive testo e descrizioni | [`tools/sync/pdf_figures.py`](tools/sync/pdf_figures.py) |
| Ingest Figma | `/figma-sync <url>` + `figma-sync` | si | Hai un file Figma con wireframe o spec | figma-extraction-agent |
| Ingest repo esistente | `/repo-sync <path>` + `repo-sync` | si | Vuoi estrarre spec da un codebase esistente | — |
| Ingest knowledge graph | `/graphify-sync <target>` + `graphify-sync` | opt-in: `compression.context.enabled: true` | Vuoi sostituire il codice raw con un grafo di dipendenze come contesto per i dev-agent | knowledge-graph-codebase · graphify · installazione |
| Costruzione wiki | `wiki-keeper` + `wiki-keeper-worker` | si | Dopo ogni ingest: trasforma `raw/` in pagine `wiki/` strutturate | — |

---

## Quando voglio interrogare la knowledge base o controllare lo stato

| Capability | Comando / Agente | Sempre attiva? | Quando usarla | Approfondimento |
|---|---|---|---|---|
| Dashboard stato + wave dispatch | `/run` + `orchestrator` | si | Vuoi sapere cosa e' pronto, cosa e' bloccato, suggerimento prossimo step | parallel-scheduler |
| Query knowledge base | `/query <domanda>` + `wiki-query` | si | Hai una domanda in linguaggio naturale sulla wiki o sul kanban | — |
| Health check | `/lint` + `wiki-lint` | si | Vuoi verificare integrita' strutturale, link rotti, staleness, errori | — |
| Riparazione errori meccanici | `/heal` | si | Il lint ha trovato ERROR meccanici e vuoi ripararli in automatico | evaluator-optimizer |
| Pass di qualita' semantica wiki | `/sweep-reviews` | opt-in: `wiki_sweep.enabled: true` | Vuoi risolvere claim non supportati, wikilink dangling e deriva terminologica (loop bounded, gated) | — |
| Scopo semantico della wiki | `wiki/purpose.md` (letto da `wiki-keeper`) | opt-in: file presente | Vuoi dichiarare dominio, entita' prioritarie, tono ed esclusioni che guidano l'ingest | — |
| Promozione status | `/promote <path> <status>` | si | Vuoi avanzare lo status di una pagina wiki o di un TSK | promotion-pipeline |
| Topologia e routing | `/topology [show\|set]` | si | Vuoi vedere o cambiare la topologia della factory | routing |
| Stato branch VCS (submodule) | `/vcs-status [target]` | si (read-only) | Progetti multi-repo/submodule: vuoi sapere su quale branch sei e su quale dovresti stare (detached HEAD, drift parent-ref, submodule non init) + comando di remediation | vcs-and-code-path |
| Allineamento repo con il remote | `/repo-align [--repos=<lista>] [--json]` | opt-in: `repo_align.enabled: true` (eseguibile anche a flag spento) | Vuoi sapere se il tuo lavoro locale e' gia' sul remote — per tutti i `vcs.mode` di PATTERN §15 (monorepo, submodule, sibling, external). Zero mutazione: usa solo `git ls-remote`. Per `diverged` distingue **avanti** (commit locali non pushati, silenzio invisibile) da **indietro** (remote avanti). Non allinea, non pusha, non fetcha: osserva e dichiara | US-299 |
| Check attribution AI su repo cliente | `/ai-policy-check [--repos=...] [--strict]` | opt-in: `ai_policy_check.enabled: true` (eseguibile anche a flag spento) | Stai lavorando su un repo cliente con `suppress_ai_traces: true` e vuoi verificare che attribution AI e ID kanban factory non siano finiti nella history. Layer-2 detective (non sostituisce gli hook git Layer-1). Il repo della factory e' rifiutato esplicitamente. `--strict` per gate pre-push | — |
| Ricerca semantica wiki | `/wiki-search <query>` | opt-in: `wiki_search.enabled: true` | Vuoi ricerca su `wiki/`: con `backend: auto` fts5 senza dipendenze (indice costruito alla prima ricerca), ibrida vector+FTS (LanceDB) se installata; `/wiki-search reindex` per l'indice ibrido | attivazione |
| Burndown sprint | `/sprint-progress [N]` | opt-in: `analytics.sprint_progress.enabled: true` | Vuoi il burndown dello sprint corrente (o N) con fallback kanban | — |
| Velocity del team | `/velocity [--epiche A,B] [--settimane N] [--dal DATA] [--per-persona] [--json]` | si, su richiesta (config facoltativa: `analytics/velocity/config.example.json`) | Vuoi la serie storica su tutto il kanban: punti e TSK chiusi per settimana ISO, media sulle ultime settimane concluse, proiezione sul backlog, tempo di attraversamento. Data di chiusura da `closed_at`, altrimenti dalla storia git; dichiara la qualita' dei dati (registrazioni in blocco, TSK senza taglia o senza inizio). Vista per persona solo con `--per-persona`. Diverso da `/sprint-progress`, che fa il burndown dello sprint corrente da `sprint.md` | [`tools/analytics/team-velocity.py`](tools/analytics/team-velocity.py) |
| Date di lavoro dei TSK | `python3 tools/lint/check-date-lavoro.py [--strict]` · Check 4be | si (ERROR; a `kanban_dates.required_from` assente non segnala nulla) | Vuoi che `/velocity` abbia le date vere: un TSK che passa a `in-progress` dalla data di adozione ha `started_at`, uno che passa a `done` ha `started_at` e `closed_at` (AAAA-MM-GG, `closed_at >= started_at`), con la data del lavoro. Include i cambi non committati; lo storico e' esente; non verifica chi ha lavorato | [`tools/kanban/date_lavoro_check.py`](tools/kanban/date_lavoro_check.py) |
| Report PM deterministico | `/coordinamento` + `pm-report-coordinator` | opt-in: `pm_report.enabled: true` | Vuoi sapere a che punto sono gli obiettivi misurando il kanban a un commit: avanzamento per epica (e per sezione e sottoperimetro — sviluppo, configurazione, test — se configurati, con l'ambiente di rilascio dell'obiettivo), TSK senza owner con eta', avvisi a regole; ogni numero e' ricalcolato da una verifica L0 indipendente prima di essere mostrato. Con `--pianifica` (blocco `pianificazione` della config) classifica i TSK aperti per priorita', urgenza e sblocco e propone un owner (`tools/coordinamento/pianifica.py`, deterministico). **Non scrive nel kanban** (proposte al tpm su gate PO), non arbitra | [tools/coordinamento/README.md](tools/coordinamento/README.md) |
| Dati derivati della wiki | `python3 tools/lint/check_dati_derivati.py [--tolleranza N]` · Check 4bf, 4bg | si (WARNING) | Vuoi sapere se `wiki/log.md` ha voci fuori ordine cronologico oltre `N` giorni (default 7: tipico dopo un merge a unione) e se il contatore `## Sources (N)` dell'index corrisponde alle fonti elencate (no-op se la sezione manca) | [`tools/lint/check_dati_derivati.py`](tools/lint/check_dati_derivati.py) |
| Evidenza dei test BE | `python3 tools/lint/check_evidenza_test_be.py` · Check 4bh | opt-in: `lint.kanban.be_test_evidence: warning\|error` (default `off`) | Vuoi che un TSK `layer: be` chiuso abbia un TSK qa chiuso con `## Esito` verificabile; `be_test_evidence_consumers` (default `[agent]`) e `be_test_evidence_since` (i chiusi prima sono esenti) | [`tools/lint/check_evidenza_test_be.py`](tools/lint/check_evidenza_test_be.py) |
| Tracciabilita' decisione -> requisito -> task | `python3 tools/lint/check_tracciabilita_design.py` · Check 4bi | opt-in: `design_traceability.enabled` + `required_from` (default spento) | Vuoi che gli artefatti nuovi siano collegati: ADR `accepted` con `satisfies: [US-…]`, ID di `satisfies`/`supersedes`/`decision_refs` esistenti, TSK `done` con un `ACn` nella `## Chiusura`. Solo WARNING e solo forma (link esistenti, non pertinenti); no-op senza report W1 e con `required_from` non successivo alla sua data; si sospende oltre `soglia_spegnimento`. con `premortem_pre_tpm: true` segnala anche gli ADR `accepted` senza `premortem:` (`adr-senza-premortem`). `--forza [--dal D]` misura a flag spento | [`tools/lint/check_tracciabilita_design.py`](tools/lint/check_tracciabilita_design.py) |
| Segreti nei file tracciati | `python3 tools/lint/check-secrets.py [--strict]` · Check 4bj | si (WARNING; ERROR da `secrets_guard.required_from`, nel master dal 2026-11-19: da quella data un FAIL fa uscire 1 il lint e la CI; gitleaks assente = WARNING NON_VERIFICABILE) | Vuoi rilevare segreti nei file tracciati con l'oracolo `tools/security/secrets_guard.py` (gitleaks), senza pattern propri; gira anche con `secrets_guard.enabled` spento, che governa solo l'hook. Previene nel percorso cooperativo, rileva negli altri. Cosa NON garantisce: i falsi negativi di gitleaks; senza il binario nessuna verifica; non copre la storia git (solo `secrets_guard.py --storia CODE_PATH` sui `code_paths[]` del cliente, mai la factory) ne' i file gitignorati; in CI rileva dopo il push | [`tools/lint/check-secrets.py`](tools/lint/check-secrets.py) |
| Lettori di contenuto non fidato con Bash | `python3 tools/lint/check-ingest-agent-tools.py [--strict]` · Check 4bk | si (WARNING; ERROR da `ingest_agent_tools.required_from`, nel master dal 2026-11-18) | Vuoi che gli agenti che leggono contenuto non fidato (capability `raw-sync` o `*-extraction`, piu' `ingest_agent_tools.agenti`: log-operator, db-operator, cypress-test-analyst, code-cartographer) non dichiarino `Bash` in `tools:`, salvo eccezioni con motivo e scadenza in `ingest_agent_tools.exceptions`; scaduta = segnalata, agente nuovo = segnalato. Cosa NON garantisce: legge i `tools:` dichiarati, non gli effettivi (permission mode, approvazioni e `settings.local.json` li scavalcano); il gruppo e' una convenzione sulle capability; «raw/ = dato non fidato» e' una mitigazione comportamentale; esclusi dichiarati i dev-agent e `code-reviewer` | [`tools/lint/check-ingest-agent-tools.py`](tools/lint/check-ingest-agent-tools.py) |
| Path assoluti nei settings versionati | `python3 tools/lint/check-settings-paths.py [--strict]` · Check 4bl | si (WARNING; ERROR da `settings_paths_check.required_from`) | Vuoi che `.claude/settings.json` non contenga percorsi assoluti (`/`, `~`, `C:\\`) o fuori repo (`..`) in `permissions.additionalDirectories` e nelle liste di path analoghe; i valori con variabili (`${CLAUDE_PROJECT_DIR}`) sono ignorati. Cosa NON garantisce: non vede `settings.local.json`, i settings user-level ne' i permessi effettivi (es. `python3 -c *`), non cerca segreti, non risolve symlink | [`tools/lint/check-settings-paths.py`](tools/lint/check-settings-paths.py) |
| Misure W1 del layer analisi-design | `python3 tools/analytics/design_w1_misure.py [--out wiki/lint/<data>-w1-design.md]` | si, su richiesta (stdlib + git) | Vuoi sapere quanto regge l'OK in chat al design (ADR nati `accepted`, Decisione riscritta prima o dopo l'OK) e quanto e' affidabile `updated:` nella wiki. Misura anche la quota di ADR con `premortem:` e quanti hanno cambiato la Decisione dopo. Il report e' la precondizione del Check 4bi. Non dice se il design era giusto | [`tools/analytics/design_w1_misure.py`](tools/analytics/design_w1_misure.py) |
| Target dei TSK | `python3 tools/lint/check_target_tsk.py` · Check 4j | opt-in: `lint.kanban.tsk_target: warning\|error` (default `off`) | Vuoi che un TSK aperto con `consumer: agent` abbia un `target:` e un repository risolvibile (il Check 4j del gate di Fase 0); `tsk_target_gitmodules: true` richiede che un `code_path` sotto `code_repos/` sia in `.gitmodules` | [`tools/lint/check_target_tsk.py`](tools/lint/check_target_tsk.py) |
| Lint deterministico | `python3 tools/lint/run-deterministic.py [--out wiki/lint/AAAA-MM-GG-deterministic.md] [--json] [--strict]` | si | Vuoi i check di `/lint` eseguiti su tutta la popolazione invece che stimati: 1, 4, 4ag, 3, 4as, 4b, 4au, 4am, 4ar, 4aq, 4ax, 4bb, 4bc, 4bd, 4be, 4bf, 4bg, 4bh, 4bi, 4bn, 4j. `wiki-lint` li esegue e cita le righe | — |
| Registro della wiki append-only | `python3 tools/wiki/log_append_guard.py [--commit <sha> | --storia N]` · Check 4bb · hook `pre-commit` da `tools/vcs/install_factory_hooks.py` | check sempre; hook opt-in: `wiki_lint.log_append_guard.hook: true` | Vuoi sapere se un commit ha tolto o riscritto righe di `wiki/log.md` senza archiviarle (`rotate_log.py`), o bloccarlo prima del commit. Le entry perse si recuperano verbatim dalla storia con `tools/wiki/recover_log_entries.py` | — |
| Marcatori di conflitto nei file in coda | `python3 tools/wiki/conflict_markers_check.py [--staged | --pre-push | --rev <ref> | --worktree] [--json]` · Check 4bn · hook `pre-commit` e `pre-push` da `tools/vcs/install_factory_hooks.py` | check sempre (WARNING); hook installati sempre | Vuoi bloccare prima del commit o del push le righe `<<<<<<<`/`=======`/`>>>>>>>` lasciate da un pull o stash in conflitto in `wiki/log*.md`, `wiki/gaps.md`, `wiki/index.md`, manifest di `raw/`, `sprint.md` (non il registro sessioni: e' locale al clone e non tracciato). Un file illeggibile e' «non verificabile» (exit 2), mai «pulito». Il `pre-push` controlla anche le voci nuove di `wiki/log.md` (`tools/wiki/log_tail_check.py`: chiavi ripetute nello stesso blocco, intestazione senza `date`/`type`/`operator` o `agent`) | — |
| Driver di merge per file in coda | `.gitattributes` · `python3 tools/vcs/install_factory_hooks.py` registra `factory-log-union`, `factory-events-union`, `factory-manifest-union` | si, registrazione locale per clone | Vuoi che due branch che aggiungono in coda a `wiki/log.md`, `analytics/events/*.jsonl` o `raw/.extraction-manifest.json` si fondano senza conflitto fisso. Il manifest resta in conflitto se la stessa chiave cambia in modo diverso nei due lati; `wiki/log.md` se il frontmatter diverge. Senza registrazione git usa il merge standard | — |
| Chiusure dei gap verificate | `python3 tools/wiki/verify_gap_closures.py [--tema RE] [--elenco] [--json] [--check]` · Check 4bc | si | Vuoi sapere quali gap chiusi lo sono davvero: conta come chiuso solo il gap la cui chiusura rimanda a una pagina della wiki esistente che cita un raw presente. Gli altri vanno trattati come aperti (WARNING, mai ERROR) | — |
| Registro dei gap append-only | `python3 tools/wiki/gaps_append_guard.py [--storia N] [--strict]` · Check 4bd | si (solo avviso; `--strict` per uscire con errore) | Vuoi sapere se un commit ha tolto o riscritto righe di `wiki/gaps.md`: sono ammessi solo righe aggiunte, il passaggio `- [ ]` → `- [x]` e la sostituzione di un **Aggiornamento** con **Risolto:** nel commit di chiusura. Non agganciato al pre-commit | [`wiki-gap-protocol`](.claude/skills/wiki-gap-protocol.md) §Chiusura con evidenza |
| Citazioni verbatim | `python3 tools/docs/verify_verbatim.py <documento> [--pattern ETICHETTA=REGEX] [--pattern-file F]` | si | Vuoi controllare che un documento derivato riporti alla lettera citazioni e blocchi copiati dalla fonte e non esponga codici interni (ID kanban, ADR, regole; i codici di progetto si passano con `--pattern`) | — |
| Regole del lint per factory | blocco `lint:` in `factory.config.yaml` · `tools/lint/checks_locali.py` · `tools/lint/version_sites_locali.py` | opzionale (senza blocco valgono le regole del master) | La tua factory ha convenzioni proprie: campi obbligatori e raccomandati per tipo, severita' del layer, ID duplicati, scope sui soli aperti, orfani per raggiungibilita', campi data; check propri eseguiti dal runner; siti di versione propri per il 4am. File che il master non ha: l'upgrade non li tocca | `.claude/skills/lint-checks.md` §Check eseguiti da script |
| Contatori a fine TSK | `python3 tools/vcs/contatore_chiusure.py --tsk <id>` (da `dev-handoff`) | opt-in: `repo_align` / `ai_policy_check` con `triggers.on_tsk_closed_count` > 0 | Vuoi che `/repo-align` o `/ai-policy-check` partano da soli ogni N TSK chiusi; contatori in `memory/*-counter.yaml`, mai bloccante | `.claude/skills/dev-handoff.md` |
| Rotazione di `wiki/log.md` | `python3 tools/wiki/rotate_log.py [--apply] [--soglia N] [--forza]` | si | Il log raggiunge 180.000 byte: sposti in `wiki/log-AAAA-MM-GG.md` il prefisso di entry datate fino a oggi, verbatim (sha256 verificato). Dry-run di default | — |
| Lookup simbolo nel codice (L1) | `tools/code-intelligence/ctags-index.sh` + `grep` su `.ctags-state/` | opt-in: `code_intelligence.l1_ctags.enabled: true` | Vuoi sapere dove e' definito un simbolo, senza ML (richiede `universal-ctags`) | code-intelligence |
| Ricerca semantica nel codice (L2) | `/code-search <domanda>` | opt-in: `code_intelligence.l2_semantic.enabled: true` | Vuoi sapere dove viene gestita una funzionalita', a livello di simbolo; `/code-search reindex` per l'indice | code-intelligence |
| Impact graph / blast radius (L3) | `graphify affected "<symbol>"` (Fase 0.bis `dev-protocol`) | opt-in: `code_intelligence.l3_impact.enabled: true` | Vuoi sapere cosa si rompe se cambi un simbolo, prima di toccarlo | code-intelligence |
| Coordinamento kanban multi-utente | `/kanban-status` + `kanban-coordinator` | opt-in: `kanban_coordination.enabled: true` | Siete in piu' persone sullo stesso kanban e vuoi sapere **chi sta su cosa**: cosa hanno pushato gli altri che non vedi, **cosa hai fatto tu che gli altri non vedono**, l'igiene di `assignee:` (assegnazioni ferme) e la contesa misurata. **Non impedisce la doppia presa, non risolve la contesa, non garantisce latenza**: la visibilita' e' al ciclo di push (minuti, non secondi). Se ti serve un lock vero, questa non e' la capability giusta — e non esiste (EP-064 §Esito 2026-09-18) | kanban-coordination |
| Plancia — canale visivo | `/plancia` (`python3 -m visual`) | opt-in: `visual_channel.enabled: true` | Vuoi **vedere** cosa sta facendo la factory invece di ricostruirlo dal transcript: sessione in corso, event store, sprint, costo — ognuno con la propria fonte e la propria eta'. Da li' puoi anche avviare lavoro e rispondere ai gate umani, e accendere il canale vocale. **Non e' uno scrittore**: ogni azione passa dalla sessione. **Non arbitra** la concorrenza. Progettata sui criteri WCAG 2.2 AA e provata in simulazione (US-397), **senza claim di accessibilita'**: la validazione con persone e' fuori scope (EP-067 US-287, Q-007 esito (b)) | `.claude/commands/plancia.md` |
| Apertura di sessione | `/session-start [--auto\|--quick]` | opt-in: `session_start.enabled: true` (eseguibile anche a flag spento) | Vuoi aprire una sessione di lavoro: ambiente, claim advisory, pull e submodule, raw/ non ingestati, briefing su gap, sprint e sessione precedente. I claim sono advisory: avvisano, non bloccano. Con `session_start.auto_launch` l'hook `tools/session/auto_start_hook.py` e' registrato su `UserPromptSubmit` (su `SessionStart` non raggiungeva la chat nell'estensione VS Code): salta i messaggi che sono gia' `/session-start` e le chat riprese | `.claude/commands/session-start.md` |
| Chiusura di sessione | `/session-close` + `session-sync` | opt-in: `session_close.enabled: true` | Vuoi produrre il documento L1 di fine sessione in `raw/sessions/` (git log, delta wiki/log.md, gap): report citabile, non storico verbatim. La Fase 0 si raccoglie in un passo con `tools/session/close_collect.py` (busta JSON in sola lettura, controlli in parallelo, exit 3 se incompleta); il mutex fra chiusure e' `tools/session/close_lock.py` (acquire/release, TTL, lock orfani) | `.claude/commands/session-close.md` |
| Log applicativi su OpenSearch | `/log` + `log-operator` | opt-in: `log_access.enabled: true` + registro `tools/logs/log-targets.yaml` | Devi analizzare un ticket o un errore guardando i log di un cluster OpenSearch: dal largo allo stretto (count, search, trace), rumore ed errori gestiti per app con conferma, dati personali mascherati di default (HMAC per esecuzione; CF/P.IVA come insiemi opt-in). Sola lettura (`_search`, `_count`, `_field_caps`), solo lato client, senza mai la cache del cluster e con il certificato verificato per impronta anche dal Python di sistema di macOS; l'output di un ambiente protetto non si scrive con `--out` in `raw/`, `wiki/`, `deliverables/`, `management/` (rifiuto nel codice) | skill `log-access-protocol` · `indagine-protocol` |
| Database PostgreSQL | `/db` + `db-operator` | opt-in: `db_access.enabled: true` + registro `tools/db/db-targets.yaml` e `.env.db` | Devi leggere un database partendo da ambiente e servizio, schema, tabella o funzionalita': catalogo DDL versionato (`db_catalog.py`) con avviso di obsolescenza, mappa funzionalita'-servizio-tabella (`db_map.py`), gate di costo con EXPLAIN e timeout per ambiente. Lettura con whitelist + transazione READ ONLY lato server; TLS `verify-full`; scrub dei dati personali nel catalogo acceso; segreti mascherati in ogni output con i pattern di `log_access` (`log_mask.mask_secrets`, EP-108 US-421), dati personali delle righe non mascherati. Scrittura spenta (`db_access.write.enabled`), mai su `read_only_envs`, `--commit` solo con token e gate umano | skill `db-access-protocol` |
| Oggetti nei bucket S3-compatibili | `/storage` (alias `/minio`) + `storage-operator` | opt-in: `object_storage_access.enabled: true` + registro `tools/object_storage/storage-targets.yaml` e `.env.object-storage` | Devi vedere un file nello storage a oggetti di un ambiente: elenco, metadati e download di un oggetto o di una cartella, link pre-firmati di lettura (scadenza di default `default_link_expires_s`, massimo 7 giorni) e rinnovo di un link scaduto. TLS verificato per default (`ca_file` nel registro; `verify_tls: false` solo esplicito, con avviso). Scrittura (upload, delete) spenta (`object_storage_access.write.enabled`), mai su `read_only_envs`; `--commit` solo con dry-run, token e gate umano (`--human-gate-approved`), con etag invariato, copia di sicurezza dell'oggetto e audit append-only. Dipendenza opzionale `boto3` | skill `object-storage-access-protocol` |
| Test Cypress da TSK qa | `/cypress-gen <TSK-id>` + `cypress-test-analyst` / `qa-dev` (modalita' Cypress) / `cypress-test-reviewer` | opt-in: `cypress_pipeline.enabled: true` + repo in `cypress_pipeline.repos[]` | Hai un TSK `layer: qa` che chiede spec Cypress in un repo di test registrato: analisi, generazione, review statica con 2 gate umani; artefatti in `code_quality/cypress/<TSK-id>/`, mai nel repo di test; report dei lanci con `tools/cypress/run_report.py` (profilo `generic` o custom) | skill `cypress-generation-protocol` · [`tools/cypress/README.md`](tools/cypress/README.md) |
| Promemoria fra operatori | `/promemoria` | opt-in: `promemoria_operatori.enabled: true` | Vuoi lasciare un promemoria a te o a un altro operatore della factory, consegnato a chi apre la sessione, con ricevute di lettura e anagrafica (`memory/promemoria/operatori/`, esempio `.example`). Remote e ramo configurabili; ogni push passa da un gate di conferma (`--yes` solo dopo consenso esplicito). Il mittente viene da `git config`, non e' firmato | `.claude/commands/promemoria.md` |
| Onboarding Day 0 per ruolo | `/onboarding [--ruolo R] [--compact] [--check-env]` | opt-in: `onboarding_day0.enabled: true` (spento: `/onboarding` v1.0) | Un nuovo contributor deve partire dal suo ruolo: passi Day 0 da `day0-per-ruolo.md` o da `onboarding_day0.roles`, verifica con `tools/onboarding/verifica_day0.py`. Funziona senza `/promemoria` | skill `onboarding` |
| Controllo ambiente factory | `/init-check [--probes] [--json]` | si (no flag; blocco `environment:` opzionale in config) | Vuoi verificare che l'ambiente locale sia pronto: python3/git/shell/autocrlf/code_paths/submodule + binari (anche alternativi, `any_of`)/env_file/variabili (dall'ambiente o da un file `.env`, `variables.source_file`)/`.nvmrc` per code_path/sonde dichiarate in `environment:`. Sonde di rete solo con `--probes` | `tools/env/init_check.py` |
| Vista gap aperti | `python3 tools/wiki/gaps_open_view.py` | si | Vuoi i gap wiki ancora aperti (`wiki/gaps.md`) in forma compatta in `memory/gaps-open.md`; riconosce il formato (sezioni chiuse da `**Risolto:**` o voci `- [ ]` / `- [x]`) | `tools/wiki/gaps_open_view.py` |
| Registro namespace kanban e prenotazione ID | `tools/kanban/next-id.py --namespace <ns>`; `next-id.py <tipo> <n> --reserve --epic EP-x [--dry-run]` | opt-in: `kanban_namespaces.enabled: true` (acceso nel master) | Vuoi generare ID con prefisso di namespace (derivate multi-namespace) oppure, nel master (`prefix: ""`), prenotare gli ID prima di creare i file: `--reserve` pubblica solo il registro su `main` (senza toccare working tree ne' branch, max 3 tentativi, mai `--force`) e le prenotazioni di `origin/main` sono lette da chi calcola dopo. Non e' un lock (§kanban_coordination). A flag spento il namespace e' assente e `--reserve` esce con errore. Indipendente dal flag: `next-id.py` unisce gli ID del ramo remoto (`--remote`/`--branch`, default `origin`/`main`; `git fetch` fail-open, `--no-fetch`), cosi' due macchine non assegnano lo stesso ID; `--no-remote` o `NEXT_ID_OFFLINE=1` lo spengono, `--strict` fallisce se il remoto non e' leggibile, `--json` per gli script | `tools/kanban/README-namespaces.md` |
| Sprint come vista generata | `python3 tools/kanban/generate_sprint.py [--check] [--stdout] [--root]` | opzionale (adottarlo = `sprint.md` non piu' curato a mano) | Vuoi che `sprint.md` non deragli dal frontmatter: lo rigenera dai TSK aperti (sprint corrente e lookahead per epica); `--check` esce 1 se la vista non e' aggiornata | `tools/kanban/generate_sprint.py` |
| Resolver session_id canonico | `tools/session/session_id.py` | si (stdlib) | Vuoi un session_id univoco per sessione (env → scratchpad → generato, mai in silenzio). Usato da session-close/start e da harvest-tokens | `tools/session/session_id.py` |

---

## Quando devo pianificare o gestire il prodotto

| Capability | Comando / Agente | Sempre attiva? | Quando usarla | Approfondimento |
|---|---|---|---|---|
| Trasformazione wiki in backlog | `product-manager` | si | Hai la wiki pronta e vuoi produrre EP/US dal materiale ingestato | prd-driven-autonomy |
| Design architetturale | `lead-architect` | si | Hai EP/US e vuoi disegnare BE/FE/API/DB | — |
| Task planning | `tpm` | si | Hai US approvate e vuoi scomporle in TSK atomici con `sprint.md` | — |
| Riconciliazione periodica del kanban | `tpm` + skill `tpm-reconcile` | si (sola lettura) | Vuoi sapere dove il kanban dichiarato diverge dall'esecuzione: dipendenze insoddisfatte, drift temporale, blocco silenzioso, assegnazione ferma; report con una raccomandazione per anomalia, nessuna scrittura | `.claude/skills/tpm-reconcile.md` |
| Chiusura di una wave | `tpm` + skill `tpm-wave-close` | si | A fine wave, prima di report e push: gate DoD, patch git↔status proposta, gap CRITICAL senza `bridge_tsk`, commit atomico del kanban (gate umano su patch e apertura TSK) | `.claude/skills/tpm-wave-close.md` |
| Query kanban | `wiki-query` | si | Vuoi rispondere a domande sullo stato di epiche, sprint, TSK | — |

---

## Quando voglio sviluppare codice o documentazione con agenti

Richiede `topology: full-stack-agents` o `hybrid-*` in `factory.config.yaml`.

| Capability | Comando / Agente | Sempre attiva? | Quando usarla | Approfondimento |
|---|---|---|---|---|
| Sviluppo backend | `/dev <TSK-id>` → `be-dev` | topologia | Hai un TSK `layer: be` pronto (status: todo) | topology-and-dev-agents |
| Sviluppo frontend | `/dev <TSK-id>` → `fe-dev` | topologia | Hai un TSK `layer: fe` pronto | topology-and-dev-agents |
| Sviluppo database | `/dev <TSK-id>` → `db-dev` | topologia | Hai un TSK `layer: db` (migration, schema) | — |
| Sviluppo QA | `/dev <TSK-id>` → `qa-dev` | topologia | Hai un TSK `layer: qa` (test unit/integration/e2e) | — |
| Sviluppo documentazione | `/dev <TSK-id>` → `docs-dev` | topologia | Hai un TSK `layer: docs` (skill, command, agente, config, wiki) | — |
| Submodule tooling guidato | `/sm-doctor` + `sm_commit --coordinated` | opt-in: `vcs_tooling.submodule_doctor.enabled: true` | Vuoi gestire i submodule dichiarati in `code_paths[]` (doctor, status, checkout, update, hook pre-commit); con `vcs_tooling.submodule_scope: gitmodules` tutti quelli di `.gitmodules`. Senza entry submodule in config: exit 0 + messaggio esplicito. Zero costanti verticali cablate | `tools/vcs/README-submodule.md` |
| Sito di documentazione tecnica | `/doc-tecnica [--out DIR] [--sections a,b] [--dry-run]` | opt-in: `documentation.enabled: true` | Vuoi pubblicare la wiki come sito statico HTML autocontenuto (indice, navigazione, ricerca), dopo un controllo segreti bloccante | `tools/docs/build_tech_site.py` |
| Documentazione funzionale di un servizio | `/doc-funzionale <servizio> --pubblico=cliente\|utente\|entrambi` + skill `functional-docs-protocol` | opt-in: `documentation.enabled: true` | Vuoi manuale per il cliente e/o guida utente di un servizio, scritti dalla sola wiki con fonti e lacune dichiarate (bozza fino ad approvazione umana) e resi in HTML/Word | `.claude/skills/functional-docs-protocol.md` |
| Digest settimanale per il management | `/digest-settimanale [--settimana=YYYY-Www] [--commento=<file.md>] [--json]` | opt-in: `documentation.enabled: true` | Vuoi un riepilogo settimanale (TSK chiusi, rilasci, gap, incidenti, costi) con numeri calcolati da script, mai dal modello | `tools/docs/weekly_digest.py` |
| Portabilita' shell script | skill `shell-portability` | si (skill, no gate) | Vuoi scrivere script shell portabili su bash/zsh/gitbash/wsl; la skill elenca i costrutti da evitare e le alternative POSIX | `.claude/skills/shell-portability.md` |
| Scrittura controllata (STE-lite) | `/ste-lite <file> [--rewrite]` + skill `ste-lite-protocol` | opt-in: `ste_lite.enabled: true` (su file espliciti gira anche spenta) | Un testo che legge una persona e' troppo denso: il linter deterministico `tools/lint/ste_lite.py` controlla le regole strutturali di ASD-STE100 (frasi, paragrafi, un'istruzione per frase, voce attiva nelle procedure, glossario); `--rewrite` riscrive tenendo tutti i fatti e chiude con la sezione «Omesso». Il verdetto e' del linter, non di chi scrive. Il dizionario dello standard resta fuori. Resta spenta per decisione (EP-076 TSK-809): su richiesta, solo variante lite. Allunga il testo, non lo accorcia | sorgente |

---

## Quando voglio verificare la qualita' del codice

Si attiva con `code_quality.enabled: true` in `factory.config.yaml`.

| Capability | Comando / Agente | Sempre attiva? | Quando usarla | Approfondimento |
|---|---|---|---|---|
| Code review automatizzato | `/review <TSK-id>` + `code-reviewer` | opt-in: `code_quality.enabled: true` | Hai un TSK `status: done` e vuoi un verdict idiomaticita'/design/robustezza | code-quality-review-layer · runbook |
| Review CQRL di default | Fase 4-quater di `dev-protocol` + `dispatch-policy` §12 | opt-in: `code_quality.trigger_default.enabled: true` | Vuoi che la review parta da sola sui TSK dei layer/consumer scelti: il dev-agent imposta `review_status: pending`, l'orchestrator dispatcha `code-reviewer` su `/run` (su `/dev` lo segnala la verifica di chiusura) | `.claude/skills/references/dev-protocol/fase4-quater-cqrl-trigger.md` |
| Rilevamento test instabili | `flakiness-detection-protocol` (skill) | opt-in: `qa_layer.flakiness_detection.enabled: true` | Vuoi identificare test flaky su rolling window di run | flakiness-detector |
| YAGNI review di un diff | `/ponytail-review <TSK\|branch\|file>` | opt-in: `ponytail.enabled: true` (HARD DEP su `code_quality.enabled`) | Vuoi i candidati alla semplificazione via Decision Ladder a 7 livelli (advisory, nessun verdict) | decision-ladder · ponytail |
| YAGNI audit full-repo | `/ponytail-audit [<path>]` | opt-in: `ponytail.enabled: true` | Vuoi lo scan YAGNI su tutto il `code_path`; alimenta la riga `ponytail-gain` del token ledger | ponytail-ab-study |
| Verifica consistenza output | `consistency-checker` (agente) | opt-in: `compression.output.consistency_check.enabled: true` | Vuoi verificare che un sub-agent non contraddica le decision anchor | consistency-checker · runbook |
| Verifica migrazione codice | `/migration-verify` + `code-cartographer` + `migration-verifier` | opt-in: `code_migration.enabled: true` (eseguibile anche a flag spento) | Hai migrato o stai migrando un codebase fra due repo (es. Vue 2 → Vue 3, CRA → Vite) e vuoi misurare la parita' funzionale su quattro assi. Oracolo, non attuatore: `reject`/`divergent`/`ambiguous` sono gate umani JSON | `.claude/commands/migration-verify.md` |

---

## Quando voglio analizzare il rischio prima di iniziare

Capability core, sempre disponibile: nessun flag. Si invoca esplicitamente e l'output non viene mai applicato da solo.

| Capability | Comando / Agente | Sempre attiva? | Quando usarla | Approfondimento |
|---|---|---|---|---|
| Analisi premortem | `/premortem` | si | Vuoi identificare failure mode probabili prima di iniziare un epic o TSK | premortem-skill · factory-premortem-integration · runbook |

---

## Quando voglio lavorare su design, UX o accessibilita'

| Capability | Comando / Agente | Sempre attiva? | Quando usarla | Approfondimento |
|---|---|---|---|---|
| Design UI | `/ux-ui-design` + `ui-designer` | opt-in: `ux_ui.enabled: true` | Vuoi produrre wireframe, spec, flussi con rationale esplicito | ux-ui-review-design-capability · runbook |
| Review UX/UI | `/ux-ui-review` + `ux-ui-reviewer` | opt-in: `ux_ui.enabled: true` | Vuoi valutare un'implementazione contro rubrica Nielsen + 6 dimensioni UI | ux-ui-review-design-capability · rubrica anti-soggettivita' · runbook |
| Accessibilita' WCAG 2.2 AA | `/a11y` + `a11y-specialist` | opt-in: `a11y.enabled: true` | Vuoi uno scan accessibilita' end-to-end con report | accessibility-testing-capability · runbook |
| Visual Oracle FE | `/visual-oracle` | opt-in: `fe_correctness.enabled: true` | Vuoi confrontare screenshot expected vs actual per regressioni visive | correctness-oracle · installazione |
| Functional Oracle FE | `/functional-oracle <TSK-id\|app>` | opt-in: `fe_correctness.functional_oracle.enabled: true` | Vuoi verificare il comportamento funzionale navigando l'app con scenari | correctness-oracle |
| Design Intelligence Layer | protocolli interni EP-019 | opt-in: `design_intelligence.enabled: true` | Vuoi coordinamento tematico centralizzato (art-director DSL), separazione LLM/generatore, Critic/Judge design | art-director-coordination · llm-generator-separation · critic-judge-agent · intention-economy |

---

## Quando devo analizzare costi e tempi

Si attiva con `analytics.measurement.enabled: true` in `factory.config.yaml`.

| Capability | Comando / Agente | Sempre attiva? | Quando usarla | Approfondimento |
|---|---|---|---|---|
| Misurazione costi/tempi reali | `/analytics` + `analytics-reporter` | opt-in: `analytics.measurement.enabled: true` | Vuoi misurare costi e tempi effettivi per TSK, sprint, periodo. Faccia retrospettiva | task-analytics-cost-estimation-capability · runbook · prezzi |
| Stima costi/tempi futuri | `/estimate` + `estimation-analyst` | opt-in: `analytics.estimation.enabled: true` | Vuoi produrre stime difendibili: intervallo + confidenza + contingency. Faccia previsionale | task-analytics-cost-estimation-capability |
| Token ledger inline | automatico + `/token-ledger [--full]` | opt-in: `analytics.token_ledger.enabled: true` | Vuoi vedere token reali e costo stimato a fine di ogni risposta con tool call (o su richiesta) | — |
| Alert sui costi in token | `/cost-alert [--period=...] [--breakdown] [--pending] [--ack=<id>]` + agente `cost-alert` | opt-in: `analytics.cost_alert.enabled: true` (+ `agent: true` per il path escalate) | Vuoi sapere se sessione, giornata, settimana o mese hanno superato le soglie di `analytics/alert-rules.yaml`: regole generali, regole personali per operatore (`operator`, che per il suo periodo sostituisce la generale) e quota inclusa nel piano di abbonamento dell'operatore (`plans` + `subscriptions`, con stima di addebito). Gira anche da solo: statusLine, `/session-start`, `/session-close`, `/run`, `/analytics`, `/session-analysis`, prima di lanciare agenti (`dispatch-policy` §13), nei wave e nella plancia. Misura solo le sessioni Claude Code della macchina | skill `cost-alert-protocol` |
| Stima adattiva di durata | `temporal-estimate-protocol` (skill) | opt-in: `temporal.estimate_protocol.enabled: true` | Vuoi stime elapsed/progress adattive durante l'esecuzione agentica | — |
| Session analysis post-hoc | `/session-analysis [--depth=full] [--retro]` | opt-in: `session_analysis.enabled: true` (`--retro` anche `engineering_practices.enabled`) | Vuoi analizzare anomalie (ERROR/BUDGET/DISPATCH) di una sessione Claude Code **chiusa** (out-of-band, no auto-fix). Con `--depth=full` una nota LLM advisory sugli aggregati redatti, solo in «Punti Aperti» (`llm-advisory.py` via `claude -p`, budget, STOP su fughe, modello da `session_analysis.advisory_model` o `models.routing.tier_fast`); con `--retro` la retrospettiva di `pocock-retro` | session-agentic-analyser · handoff fleet-doctor |

---

## Quando affronto un problema complesso multi-dominio o voglio un prototipo

| Capability | Comando / Agente | Sempre attiva? | Quando usarla | Approfondimento |
|---|---|---|---|---|
| Tavola Rotonda | `/tavola-rotonda "<topic>"` | opt-in: `tavola_rotonda.enabled: true` | Problema genuinamente complesso/multi-dominio: deliberazione strutturata multi-agente con Critico anti-compiacenza. I partecipanti li lancia la sessione principale (un subagente non lancia altri agenti); il moderatore cura setup, convergenza e sintesi; `tools/tavola-rotonda/verifica-lanci.py --registro` verifica che i lanci siano reali (ADR-EP073-001) | runbook |
| Prototype generation | `/prototype [--variants=N]` + `prototype-generator` | opt-in: `prototyping.enabled: true` | Vuoi un prototipo grafico (cascata figma→penpot→react→html, fallback html garantito) | — |
| Diagnostica prototyping | `/prototype-status` | opt-in: `prototyping.enabled: true` | Vuoi sapere quale backend verrebbe scelto e cosa e' disponibile, senza generare nulla | — |
| Tutoring adattivo | `tutor` (agente) | opt-in: `capability_formativa.enabled: true` | Vuoi spiegazioni con tag epistemici L1/L2/L3, retrieval citato e scaffolding adattivo (Student Model SM-2) | design-capability-formativa |
| Fleet health / skill hygiene | `/refactor` + `fleet-doctor` | opt-in: `refactor_agent_skills.enabled: true` | Vuoi rifattorizzare skill/agenti sovradimensionati in divulgazione progressiva | skill-hygiene |

---

## Quando devo gestire la governance del framework

| Capability | Comando / Agente | Sempre attiva? | Quando usarla | Approfondimento |
|---|---|---|---|---|
| Complexity budget | `/complexity-budget` | opt-in: `complexity_budget.required_on_release: true` | Vuoi verificare che ogni EP rispetti il budget N:1 (aggiunta vs deprecazione) | complexity-budget · runbook |
| Semantic drift detection | `/semantic-drift-scan` | opt-in: `wiki_lint.semantic_check.enabled: true` | Vuoi rilevare divergenza tra wiki e codice reale (L1 staleness always-on, L2 LLM-judge, L3 embedding) | semantic-drift-prerequisites |
| Wiki gap detection | `wiki-gap-protocol` (skill) | si | Vuoi identificare lacune nella wiki rispetto al kanban | — |
| Temporal budget governor | `temporal-budget-governor` (skill) | opt-in: `temporal.budget.enabled: true` | Vuoi vincolare la durata economica di processi agentici (anti-runaway) | temporal-budget-governor · runbook |
| Viste filtrate del PATTERN | `/pattern-view [profilo]` | si | Vuoi leggere solo le sezioni del PATTERN pertinenti al tuo profilo di adozione (minimal/standard/full) | — |
| Ciclo di vita delle capability | campo `status:` nei blocchi di `factory.config.yaml` (PATTERN-governance §23.11) | si (metadata) | Vuoi dichiarare se una capability accesa e' davvero in uso: `active` / `dormant` / `deprecated` / `removed`; nessuna transizione cambia `enabled` senza decisione umana | `PATTERN-governance.md` §23.11 |
| Handover fra repo senza history | `/repo-handover` | opt-in: `repo_handover.enabled: true` | Vuoi esportare lo stato corrente di un code_path su un repo vergine (SHA fisso, nessuna history, push mai automatico, gate locali opzionali su SHA immutabile) | `.claude/commands/repo-handover.md` |
| Registro namespace kanban (config) | `tools/kanban/id_registry_check.py` · `namespace_orphans.py` | opt-in: `kanban_namespaces.enabled: true` | Vuoi verificare la coerenza del registro dei namespace e trovare ID orfani nelle derivate multi-namespace | `tools/kanban/README-namespaces.md` |
| PATTERN in moduli + manifesto | `PATTERN.md` (indice §0-§11) + `PATTERN-{integration,runtime,governance,capabilities}.md` | si | Il PATTERN e' diviso in un indice e quattro moduli tematici: carica solo il modulo pertinente al tuo comando o agente consultando il manifesto | `.claude/skills/references/dispatch-policy/manifesto-caricamento.md` |
| Controlli di sicurezza | sezione `§controlli_sicurezza` di questo file · `python3 tools/lint/check-secrets.py` (4bj) | opt-in: `secrets_guard.enabled` per l'hook; 4bj/4bk/4bl girano nel lint | Vuoi la vista d'insieme dei controlli di sicurezza deterministici, con cio' che NON garantiscono e i rischi residui accettati | questo file (`§controlli_sicurezza`) |
| Sicurezza applicativa del codice del cliente | `/security-scan <code_path> [--oracoli sast,iac,sca,segreti]` · `python3 tools/security/security_scan.py` + `security-interpreter` | opt-in: `security_scan.enabled` (default false, letto dall'ancora) | Vuoi eseguire su un code_path del cliente gli oracoli deterministici (semgrep, trivy config, osv-scanner offline, gitleaks sulla storia) e avere un report a campi enumerati; PASS non significa codice sicuro | questo file (`§security_scan`), [`.claude/skills/security-scan-protocol.md`](.claude/skills/security-scan-protocol.md) |
| Copertura schema config | `python3 tools/lint/check-config-schema-coverage.py [--json] [--root]` | si (stdlib) | Vuoi verificare che tutte le chiavi top-level di `factory.config.yaml` siano dichiarate in `schemas/factory.config.schema.json`. Exit 1 se ci sono chiavi non dichiarate (UNDECLARED); schema-only e' solo INFO | `tools/lint/check-config-schema-coverage.py` |
| Stato degli adapter dai manifest | `python3 tools/docs/gen-status.py [--check]` | si (stdlib, in CI) | Vuoi che la maturita' degli adapter abbia una sola fonte: il blocco generato di `docs/STATUS.md` e `docs/STATUS.it.md` nasce da `adapters/*/manifest.yaml`; `--check` (exit 1) segnala un blocco indietro o una riga della tabella «Adapter registry» di CLAUDE.md con maturita' o contract diversi dal manifest (EP-080) | `docs/STATUS.md` |
| Traccia di un'epica | `python3 tools/docs/trace-epic.py EP-NNN [--ref R] [--out F]` | si, su richiesta (stdlib + git) | Vuoi mostrare la catena decisione → criteri → task con date e chiusure alla lettera → commit → PR → voce di log, generata da kanban e git invece che scritta a mano. Sola lettura sul kanban (EP-080) | `docs/trace/` |
| Esempio eseguibile | `examples/hello-factory/` · `python3 -m pytest tools/tests/test_hello_factory.py` | si (in CI) | Vuoi vedere la catena completa in miniatura senza installare nulla: fonte, pagina wiki citata, epica, storia, task chiuso con evidenza, codice, review, log. Il test esegue i check deterministici sull'esempio e verifica che un anello rotto venga trovato (EP-081) | `examples/hello-factory/README.md` |
| CI sulle PR | `.github/workflows/ci.yml` | si, su ogni PR e push su main | Vuoi che i check deterministici e la suite girino senza che qualcuno li lanci: bloccanti i check verdi (4au, 4am, 4ar, 4aq, 4ax, 4bb, 4bc, 4bd, 4be), `gen-status --check` e pytest; 1 e 3 in sola lettura finche' il loro debito non e' a zero (EP-080) | `docs/GUARANTEES.md` |

---

## Quando devo pubblicare il kanban, usare piu' adapter o creare una nuova factory

| Capability | Comando / Agente | Sempre attiva? | Quando usarla | Approfondimento |
|---|---|---|---|---|
| Publish kanban esterno | `/kanban-publish` + `github-publisher` | opt-in: `kanban_publish.provider: github` | Vuoi un mirror push-only di EP/US/TSK su GitHub Issues/Milestones (o GitLab/Jira/Linear) | publisher-adapters |
| Multi-adapter | `adapters/<name>/` | si (dichiarazione) | La factory deve girare su Claude Code, Cursor, Aider, OpenAI, Gemini contemporaneamente | multi-adapter-scaffolding |
| Condivisione artefatti HTML | `/share <html-path> [--dry-run]` | opt-in: `content_share.enabled: true` | Vuoi pubblicare un artefatto HTML su soli-frames via `repository_dispatch` (gate umano obbligatorio R.CS3) | content-share-hub-pattern · setup |
| Canale vocale handsfree | `/voice-install` + `voice-channel-installer` | opt-in: `voice_channel.enabled: true` | Vuoi parlare con la factory: STT/TTS/VAD, wake word, state machine 5 stati, LaunchAgent macOS | voice-channel · installazione · uso |
| Factory come MCP server | `adapters/mcp/` | opt-in: `mcp_server.enabled: true` | Vuoi esporre la factory in read-only a un client MCP esterno (R.MCP1 no-write) | — |
| Release artefatti applicativi | `/release-artifact <target> [--dry-run]` + `artifact-release-manager` | opt-in: `artifact_release.enabled: true` + `release_targets: [...]` non vuoto | Vuoi rilasciare un artefatto (container-gitops, package-registry, manifest-edit) a partire da SHA immutabile verificato da `worktree-gate`. Gate umano R.14 obbligatorio; push mai automatico | `.claude/commands/release-artifact.md` |

---

## Quando voglio ridurre i token usati dagli agenti

Si attiva con i flag `compression.*` in `factory.config.yaml`.

| Capability | Comando | Sempre attiva? | Quando usarla | Approfondimento |
|---|---|---|---|---|
| Output compression (Caveman) | `/compression` | opt-in: `compression.output.enabled: true` | Vuoi ridurre la verbosita' degli output degli agenti interni (Fase 1) | factory-compression-layer · token-compression |
| Context compression (Graphify) | `/graphify-sync` | opt-in: `compression.context.enabled: true` | Vuoi sostituire il codice sorgente con un knowledge graph come contesto per i dev-agent (Fase 2) | factory-compression-layer · knowledge-graph-codebase · installazione |
| Token harvest compatto | `/harvest-tokens` | si | Vuoi contare i token usati nella sessione corrente senza path cablati: discovery automatica del transcript via session_id | `.claude/commands/harvest-tokens.md` |

Caveman comprime solo i messaggi fra agenti: verso l'utente e verso gli artefatti e' spento (PATTERN §20.2, R.C1). Per i testi che legge una persona c'e' la grammatica opposta, STE-lite (`/ste-lite`), che vieta di togliere articoli e verbi.

---

## Quando applico le pratiche di ingegneria (EP-077, opt-in)

Adattate dalle skill di Matt Pocock (MIT, copia fedele al commit 49dd158 in `vendor/mattpocock-skills/`).
Provenienza: pilota della derivata portale-servizi-factory. **Stato: spente** (`engineering_practices.enabled: false`);
la misura finale del pilota nella derivata non e' ancora disponibile. Le skill interattive girano solo nella sessione principale.

| Capability | Comando / Agente | Sempre attiva? | Quando usarla | Approfondimento |
|---|---|---|---|---|
| TDD a fette verticali | skill `pocock-tdd` (dev-protocol Fase 3) | opt-in: `engineering_practices.enabled`, sui TSK con `test_seams_status: confermati` | TSK con logica testabile: test rosso, codice minimo, verde, seam per seam | `.claude/skills/pocock-tdd.md` |
| Diagnosi dei bug difficili | skill `pocock-diagnosing-bugs` | opt-in: `engineering_practices.enabled` | Bug con causa ignota: segnale rosso, ipotesi, gate del Tech Lead, test di regressione | `.claude/skills/pocock-diagnosing-bugs.md` |
| Intervista sulle decisioni | skill `pocock-grilling` | opt-in: `engineering_practices.enabled` | Prima di un'epica: domande a turni con risposta consigliata | `.claude/skills/pocock-grilling.md` |
| Aderenza alla specifica in CQRL | `/review` (Passata 6) | opt-in: `code_quality.passes.spec_adherence: true` | Il diff confrontato con TSK, US e constraints dell'epica | `.claude/skills/references/code-review-protocol/passata-6-aderenza-spec.md` |
| Retrospettiva sull'ambiente | skill `pocock-retro` | opt-in: `engineering_practices.enabled` | Su una sessione chiusa: proposte, con gli errori meccanici trasformati in controlli | `.claude/skills/pocock-retro.md` |
| Glossario e moduli profondi | `pocock-domain-modeling`, `pocock-codebase-design`, `pocock-improve-codebase-architecture` | opt-in: `engineering_practices.enabled` | Si chiarisce un termine del dominio; si progetta o si cerca un modulo superficiale | `.claude/skills/pocock-codebase-design.md` |
| Indicatori e bilancio N:1 | `python3 tools/pocock/kpi_pilota.py --dal <data>` · `python3 tools/pocock/bilancio_n1.py` · `python3 tools/pocock/verify_vendor.py` | si (stdlib + pyyaml) | Gli 8 indicatori, il bilancio delle parole aggiunte e potate, la verifica della copia vendorizzata | `analytics/pocock-pilota/README.md` |

---

## Quando curo il mestiere della UI (EP-090, opt-in)

Adattate da emilkowalski/skills (MIT, copia fedele al commit 715c180 in `vendor/emilkowalski-skills/`).
Si adotta il metodo, non il gusto come legge: le regole del motion sono euristiche d'autore, quindi la passata
e' **advisory** e non produce verdetto. **Stato: spente** (`ui_craft.enabled: false`, `prototyping.variants: 1`).

| Capability | Comando / Agente | Sempre attiva? | Quando usarla | Approfondimento |
|---|---|---|---|---|
| Dati del caso peggiore | `/worst-case <componente\|TSK-id\|path>` · fase opzionale del functional oracle | opt-in: `ui_craft.enabled` + `ui_craft.worst_case_data` | Una UI che regge solo con i dati demo: valori dallo schema reale, fixture Empty/One/Huge, toggle solo dev, report delle rotture prima di correggere | `.claude/skills/kowalski-worst-case-data.md` |
| Revisione del motion in CQRL | `/review` (Passata 7) | opt-in: `ui_craft.enabled` + `ui_craft.motion_review`, solo diff con motion | 10 standard (easing, durate, origine, interrompibilita', GPU, reduced-motion), tabella Prima/Dopo/Perche', nessun verdetto | `.claude/skills/kowalski-motion-review.md` |
| Varianti divergenti | `/prototype --variants N` (2..5) | opt-in: `prototyping.enabled`; N anche da `prototyping.variants` | Esplorare N direzioni su assi nominati dietro un selettore neutro; la scelta e' umana. Solo backend html, gli altri degradano a 1 | `.claude/skills/references/prototype-generation-protocol/varianti.md` |
| Stop sulla deriva del TSK | campo TSK `base_commit:` | opt-in per presenza del campo | TSK che cita `file:riga`: se il codice e' cambiato dal commit, il dev-agent si ferma (`blocked`) invece di improvvisare | `.claude/skills/references/dev-protocol/base-commit-deriva.md` |
| Verifica delle copie vendorizzate | `python3 tools/pocock/verify_vendor.py [--vendor <cartella>\|--all] [--clone <path>]` | si (stdlib) | Le copie in `vendor/` coincidono con il commit dichiarato in `ORIGINE.md` | `vendor/emilkowalski-skills/ORIGINE.md` |

---

## §session_registry — Registro sessioni locale al clone (EP-112, US-438)

`session_start.enabled: true` (acceso 2026-11-19; `auto_launch.enabled: false`). Il registro
(`tools/session/active_sessions.py`) sta nella git common dir del clone, condivisa tra checkout principale e worktree;
fuori da git ricade su `memory/active-sessions.yaml`. Lo legge `/run` (state-scan 8.ter) e il briefing di `/session-start`.

**Cosa NON garantisce** — vincolante: non vede le altre macchine ne' gli altri clone; non impedisce la doppia presa;
non arbitra (nessun lock, nessun lease). Tra macchine resta `status: in-progress` pushato sul TSK. Visibilita' al ciclo
di scrittura dei claim, minuti.

**Criterio di spegnimento** — `# SUNSET: v2.49` sul blocco `session_start` (letto dal Check 4ar): se fino alla
scadenza il registro e' rimasto vuoto con transcript attivi, l'adozione si spegne e non si ritenta (non si rinnova).
L'ipotesi «le sessioni concorrenti stanno sullo stesso clone» e' misurata in TSK-1068.

## §kanban_coordination — Kanban Multi-User Coordination (EP-064, v2.43, opt-in)

Capability opt-in per il coordinamento fra piu' persone che lavorano lo stesso kanban
su git. Read-only sul kanban, zero dipendenze esterne (stdlib Python), zero processi
permanenti. `kanban_coordination.enabled: false` di default.

**Cosa da':**

| | Segnale |
|---|---|
| Disgiunzione in **pianificazione** | campo `assignee:` advisory (US-253) — chi si e' preso cosa, prima di iniziare |
| **Visibilita' bidirezionale** al ciclo di push | cosa hanno fatto gli altri che non vedi **e cosa hai fatto tu che gli altri non vedono** (US-266) — la seconda meta' e' quella che previene la collisione: rende visibile all'autore il proprio silenzio |
| **Misura** della contesa | collisioni reali nella finestra, con la condizione di riapertura eseguibile in un comando (US-251) |

**Cosa NON da'** — vincolante (US-267 AC8), non ammorbidibile in nessun documento: non impedisce la doppia presa; non risolve la contesa a runtime (nessun lock, nessun lease, nessun arbitro); non garantisce alcuna latenza (visibilita' al ciclo di push, minuti non secondi). Dettaglio in `CLAUDE.md §kanban_coordination`.

| Aspetto | Valore |
|---|---|
| Agente owner | `kanban-coordinator` (`.claude/agents/kanban-coordinator.md`) |
| Skill | `.claude/skills/kanban-coordination-protocol.md` |
| Comando | `/kanban-status` (`.claude/commands/kanban-status.md`) — report in-chat; fallback esplicito a capability non configurata, mai errore |
| Tool | `tools/kanban-observer/kanban-observe.py` (visibilita', `[--json] [--no-fetch]`), `tools/kanban-trial/collision-oracle.py` (misura, `--days N`) |
| Config gate | `kanban_coordination.enabled: false` (default) + `oracle_window_days: 30` + `stale_assignment_days: 7` |
| Soglia assegnazione ferma | riferimento per `assegnazione_ferma_soglia_giorni` di [`tpm-reconcile`](.claude/skills/tpm-reconcile.md) §3.4 (FM-NEW-1) |
| Runbook | `wiki/runbooks/kanban-coordination.md` |
| Vincoli | read-only sul kanban; nessun `git push`/`git pull` (§7 r.14); nessuna scrittura in `wiki/` (§7 r.12); nessuna modifica di `status:`. Osserva, misura, **raccomanda** (US-267 AC4) |
| Provenienza | Tavola Rotonda TR-9b4e7c02 — `wiki/decisions/tavola-rotonda-9b4e7c02-5a1d-4f38-8c61-2d7a3e9f5b40-2026-09-17.md` (§Sintesi + §Addendum) |

### L'oracolo e' asimmetrico — invariante di lettura

```bash
python3 tools/kanban-trial/collision-oracle.py --days 30
```

- `>=1` collisione ⇒ il problema **e' reale**: i **43 TSK** chiusi (US-254..US-261, l'arbitro
  self-hosted con lease) si riaprono col loro contenuto tecnico intatto. La condizione e'
  eseguibile e **non discrezionale**.
- `0` collisioni ⇒ **nessuna informazione**. Mai «il problema non esiste». Su questo repo
  `management/kanban/` ha **320 commit da un solo autore**: lo zero e' inevitabile **per
  costruzione**, non e' un'evidenza di assenza di contesa.

L'agente non deve poter concludere che la contesa non esiste (US-267 AC3).

### Perche' l'arbitro non e' stato costruito

EP-064 ha chiuso **43 TSK come superflui, non rinviati**: l'arbitro con lease costava
**12-23 sprint della capacita' totale** della factory per risolvere una contesa misurata
**zero volte** su questo repo, su un host che dietro NAT domestico o aziendale **non e'
raggiungibile**. Nessuna variante sposta la stima — designazione, non-24/7 e mesh attaccano
tutte la periferia mentre il costo e' nel core. **Tre istruttorie indipendenti convergono**
(US-252 modello di allocazione, US-263 stima ricalcolata, US-265 variante host designato).

Cosa si perde rispetto alla richiesta iniziale: il blocco duro sulla doppia presa e la
latenza 1-5 s. Cosa si ottiene: la disgiunzione in pianificazione e la visibilita'
bidirezionale, a **meno dell'1% del costo**. Dettaglio in
`EP-064.md`
§«Esito 2026-09-18».

---

## §visual_channel — Plancia, canale visivo (EP-067, v2.44, opt-in)

Implementazione del **canale visivo** che il contratto `FactoryRuntime` di EP-041 dichiara
e che era rimasto «stdout strutturato in MVP» (PATTERN §30.13). Gemello dello stesso porto
del Voice Channel: voce e schermo leggono **la stessa sequenza di eventi**, distribuita da
un unico `Tee`.

```bash
python3 -m visual --force          # http://127.0.0.1:8756
python3 -m visual --check          # configurazione risolta, senza avviare
python3 -m visual --root ../altra-factory
```

**Cosa mostra**: sessione in corso (dal transcript del runtime), event store, sprint,
avanzamento delle attivita' (report PM di EP-070, numeri del motore verificati da L0, con
link al report completo), sessioni con claim, costo. Ogni misura dichiara **fonte, eta' della lettura e eta' del
dato** — tre cose distinte. Una fonte illeggibile dice «non osservabile» con la ragione,
**mai zero**.

**Cosa NON fa** — vincolante: non e' uno scrittore (ogni azione e' una `submit()`, lo scrittore
resta la sessione); non arbitra la concorrenza (dichiara le altre sessioni, nessun lock ne'
lease); la mascotte non e' un canale di accesso (codifica ridondante, sempre nascosta alle
tecnologie assistive, mai unico veicolo di un'informazione); il verde WCAG non dichiara
«accessibile» (la validazione con persone e' fuori scope: US-287, Q-007 esito (b)). Dettaglio in `CLAUDE.md §visual_channel`.

| Aspetto | Valore |
|---|---|
| Comando | `/plancia` (`.claude/commands/plancia.md`) |
| Pacchetto | `visual/` — solo stdlib, nessuna dipendenza nuova |
| Config gate | `visual_channel.enabled: false` (default) + `host` + `port` + `runtime_timeout_seconds` + `stale_after_seconds` + `coordinamento.{fonte,config}` |
| Report PM | riquadro `coordinamento`: rilancia `tools/coordinamento/run.py` solo quando cambia l'impronta del kanban; richiede `pm_report.enabled: true`; uscite in una cartella temporanea fuori dal repo |
| Canale vocale | si accende dalla plancia; stesso flusso, stesso filtro `tts_payload` |
| A11y | axe 0/0/0 + 17 check deterministici (`tools/a11y/target-checks.mjs`) |
| Documentazione | `.claude/commands/plancia.md` — uso, configurazione, diagnostica |
| Pattern | §30 (canale asimmetrico). Nessuna sezione propria: §23.8 vieta la cerimonia prima dell'esercizio |

---

## §controlli_sicurezza — Controlli deterministici di sicurezza (EP-098, opt-in)

Vista d'insieme. Le righe dei check stanno nella tabella dei check e nelle chiavi
`secrets_guard:` di questo file: qui non si ripetono.

**Cosa c'e'**

- **Un solo oracolo dei segreti**: `tools/security/secrets_guard.py`, che chiama gitleaks.
  L'esito e' `NON_VERIFICABILE`, mai PASS, quando gitleaks manca o fallisce, il report e'
  illeggibile, o non c'e' nessun file leggibile da verificare (zero file, root non git, solo
  symlink). L'OK dichiara quanti file ha visto: «gitleaks: nessun finding su N file».
  Lo chiamano il pre-commit (spento di default), `/lint` (check 4bj) e la CI, dove gitleaks e'
  installato a versione fissata (8.30.1) con sha256 verificato. Nessun altro file definisce pattern.
  **Da quando blocca**: nel master `secrets_guard.required_from: 2026-11-19` (EP-108 US-418). Da quella
  data un FAIL (finding di gitleaks) e' ERROR: blocca il commit nell'hook e fa fallire `/lint --strict` e la
  CI. Prima era WARNING. Nel lint e in CI `NON_VERIFICABILE` resta WARNING (manca la verifica, non c'e'
  un segreto); nell'hook, a severita' ERROR, blocca anche `NON_VERIFICABILE`, salvo un record di deroga.
- **Il pre-commit legge lo stage**: i blob dell'indice git, non i file su disco. Un segreto in
  stage e poi tolto dal disco e' visto; rinomine e nomi non ASCII sono coperti. La config e' il
  `.gitleaks.toml` di HEAD: un `.gitleaks.toml` messo in stage non spegne la scansione.
- **Check 4bk**: i lettori di contenuto non fidato non hanno Bash, salvo eccezione motivata a scadenza
  (2027-05-16). Il gruppo comprende gli agenti di ingest e, dal 2026-11-18 (EP-108 US-419), gli operatori
  che leggono log, righe di database e codice del cliente (tutti in eccezione: lavorano solo con uno script).
  ERROR nel master dal 2026-11-18. Esclusi dichiarati: i dev-agent e `code-reviewer`. Il frontmatter si legge con sola stdlib; senza PyYAML le eccezioni non
  si leggono e il check da' WARNING «non verificabile», non OK.
- **Check 4bl**: i path nei settings versionati, comprese le regole `permissions.allow|deny|ask`.
  Ammessi solo `${CLAUDE_PROJECT_DIR}` e path relativi interni; `~`, `$HOME`, `%VAR%` e `..` sono
  finding. JSON non valido: WARNING «non verificabile», mai OK.
- **repo-sync** legge senza Bash: l'elenco dei file e' una enumerazione deterministica.

**Cosa NON garantisce** (vincolante, non ammorbidibile)

- **Previene solo nel percorso cooperativo.** `--no-verify` e `core.hooksPath` aggirano
  l'hook. L'hook vale per clone: chi non lo installa non ce l'ha.
- **CI e lint rilevano dopo il fatto**: il segreto e' gia' nel commit, o nel push.
- **Senza gitleaks nessuna verifica e' avvenuta.** `NON_VERIFICABILE` non e' un via libera.
- **Una modifica di `.gitleaks.toml` non passa in silenzio** (EP-108 US-422). L'hook la segnala
  sempre; a severita' ERROR la blocca, salvo un record di deroga con `ambito: config_gitleaks` sul ref
  protetto. In CI, nelle PR, `secrets_guard.py --config-diff` stampa il diff come `::warning`: segnala,
  non blocca.
- **Codice del repo eseguito da solo** (elenco ricavato dai file, EP-108 US-422). Chi apre o aggiorna
  un clone esegue script dell'albero che ha appena scaricato:

  | Dove | Quando | Cosa esegue |
  |---|---|---|
  | `.claude/settings.json` | `Stop` (fine risposta) | `tools/analytics/show-session-tokens.py`; su `/dev`, `/lint`, `/run`, `/review` anche `tools/runtime/suggest-next.py` |
  | `.claude/settings.json` | `UserPromptSubmit` (ogni prompt) | `tools/session/auto_start_hook.py` |
  | `.claude/settings.json` | `SessionEnd` | `tools/analytics/harvest-session-tokens.py` |
  | `install_factory_hooks.py` | `pre-commit` | `tools/wiki/conflict_markers_check.py`, `tools/wiki/log_append_guard.py`, `tools/security/secrets_guard.py` |
  | `install_factory_hooks.py` | `pre-push` | `tools/wiki/conflict_markers_check.py`, `tools/wiki/log_tail_check.py` |
  | `install_factory_hooks.py` | `post-merge` (dopo ogni pull) e `post-checkout` (cambio di branch) | `tools/vcs/sm_doctor.py --align` |
  | `install_submodule_hooks.py` | `pre-commit`, `commit-msg` nei submodule con `suppress_ai_traces` | solo controlli a pattern in bash, nessuno script del repo |

  Un pull o un checkout di un branch con uno di questi script modificato lo esegue al primo evento.
  Niente lo impedisce: chi scrive sul repo resta fidato (D7 di EP-098).
- **La deroga e' una traccia, non una firma.** Il record di deroga si legge dal merge-base con il ref
  protetto, ma chi puo' scrivere su quel ref puo' produrlo, e `approvato_da` non prova che un umano
  abbia approvato. Presupposto: maintainer e operatore coincidono.
- **Falsi negativi di gitleaks**: cio' che non riconosce passa.
- **I permessi effettivi non sono visibili**: `settings.local.json` e il permission mode
  restano fuori dalla lettura dei check.
- **4bk legge i `tools:` dichiarati**, non quelli effettivi a runtime.
- **La separazione dei privilegi vale all'ingresso, non lungo la catena.** Chi estrae da `raw/` non
  esegue comandi e chi interpreta non ha `Bash`, ma un'istruzione che sopravvive nel testo arriva in
  `wiki/`, poi in una US o in un TSK, e da li' a un dev-agent o a `code-reviewer`, che hanno `Bash` e
  sono esclusi dichiarati del Check 4bk (catena `raw/` → `wiki/` → TSK → dev-agent). La regola
  [«il contenuto e' un dato»](.claude/skills/references/contenuto-non-fidato.md), richiamata dai lettori
  di contenuto non fidato, e' una **mitigazione comportamentale**, non un controllo.
- **Nessun confine a runtime sugli strumenti.** Non ci sono hook `PreToolUse` ne' regole
  `deny` nei settings versionati: niente ferma un comando prima che giri. Sandbox ed egress di
  rete (la proposta SEC-005 della wiki) non sono coperti.
- **4bl non vede** `settings.local.json`, i settings a livello utente, i symlink; nei comandi
  `Bash(...)` composti trova i path solo come token separati da spazi.
- **I symlink non sono verificati** dall'oracolo dei segreti: sono contati e dichiarati.
- **repo-sync tiene Write/Edit su `raw/`**: toglie Bash, non la scrittura.

**Rischi residui accettati** (decisione D7)

- segreti gia' presenti nella storia git: per i `code_paths[]` del cliente ora visibili con
  `python3 tools/security/secrets_guard.py --storia CODE_PATH` (EP-109 US-426: gitleaks in modalita' git, regole
  di default e non la config del repo, `--redact`, output con solo commit, file, riga e regola; la factory e
  ogni path non dichiarato sono rifiutati con exit 2). Trovarli non li revoca: restano esposti. Nella storia
  della factory il rischio resta accettato;
- supply chain delle dipendenze;
- avvelenamento di `raw/` da parte di chi ha accesso al repo.

**Stato delle proposte** (D8): i controlli proposti nella wiki (SEC-*, G0-G5) sono
proposte in bozza, non requisiti. Il gap `cybersicurezza-factory-mappatura-su-factory-non-dichiarata`
e' aperto. Nessuna dichiarazione di conformita' e' fatta qui.

---

## §security_scan — Sicurezza applicativa del codice del cliente (EP-109, opt-in)

`/security-scan <code_path>` esegue con il runner `tools/security/security_scan.py` gli oracoli deterministici
sui `code_paths[]` del cliente (mai sulla factory): `sast_guard.py` (semgrep), `iac_guard.py` (trivy config),
`sca_guard.py` (osv-scanner offline, delta dal baseline) e `secrets_guard.py --storia` (gitleaks sulla storia).
Protocollo: [`.claude/skills/security-scan-protocol.md`](.claude/skills/security-scan-protocol.md). Chiavi: il blocco
`security_scan` nel riferimento qui sotto e `scanner_identity`, `suppression_check`.

- **Opt-in**: `security_scan.enabled` (default `false`) letto dall'ancora `origin/main`. A flag spento il runner
  stampa «CAPABILITY SPENTA» ed esce 3: nessuna verifica e' avvenuta.
- **Esiti**: PASS, FAIL, NON_VERIFICABILE per oracolo e complessivo (FAIL prevale, poi NON_VERIFICABILE).
- **Report**: `security/reports/`, ignorato da git; per voce solo campi enumerati, mai testo di advisory.
- **Interpretazione**: l'agente `security-interpreter` (`.claude/agents/security-interpreter.md`, `tools: [Read, Write]`,
  senza Bash, sorvegliato dal Check 4bk come lettore di contenuto non fidato) legge solo `<report>.agente.json` e
  scrive `<report>.triage.md`: raggiungibilita' e falso positivo come ipotesi, priorita'. Non decide; ogni
  accettazione e' un record umano.
- **Threat model**: ADR dell'architetto, senza tool; input facoltativo del protocollo.
- **Fix con gate** (US-431, decisione D4 = a): [`.claude/skills/security-fix-protocol.md`](.claude/skills/security-fix-protocol.md)
  e `python3 tools/security/fix_gate.py CODE_PATH --finding ID --pacchetto NOME`. Nel primo ciclo solo manifest e
  lockfile (un lockfile solo con il suo manifest); soppressioni, CI, `.claude/`, `security/` e registri sono FAIL;
  oracolo SCA rieseguito con lo stesso DB; chiusura solo legittima (pacchetto a un'altra versione, advisory assente);
  loop bounded da `security_scan.fix_max_iterations` (default 3). Mai push sul default ne' merge: proposta per un umano.
- **Confine con CQRL** (US-430, R.Q7 invariata): il report di `/review` porta il campo
  `security_scan: assente | <path>` e il digest la riga fissa «pass non attesta la sicurezza». CQRL legge, non
  produce: un CVE (anche gia' nel baseline accettato) non fa scattare `reject`; resta `reject` solo un secret in
  chiaro nel diff.
- **Riscansione al cambio del DB** (US-432): `python3 tools/security/rescan.py CODE_PATH [--scanner osv-scanner|trivy]`
  confronta l'istantanea a HEAD (commit, id del DB, finding per identita') con il riferimento locale in
  `security/reports/`: stesso commit e stesso DB = `invariato` (determinismo); stesso commit e DB diverso = evento
  di riscansione con i finding nuovi e spariti, file `.evento.json` per il maintainer, **exit 0, mai FAIL**; finding
  diversi a DB e commit fermi = NON_VERIFICABILE (non deterministico); commit diverso = delta di `sca_guard`.

**Cosa NON garantisce** (tabella consolidata della Tavola Rotonda a6d2f8c3, vincolante)

| Capability | Cosa NON garantisce |
|---|---|
| Oracolo statico (SAST/SCA/IaC) e `/security-scan` | Assenza di vulnerabilita'; copertura di logica di business, authz, 0-day; PASS vale solo per versioni e regole fissate; NON_VERIFICABILE non vale PASS; FAIL→PASS non prova la rimozione del rischio; la raggiungibilita' reale del codice vulnerabile |
| Identita' dello scanner | Per binario singolo (gitleaks, trivy, osv-scanner) e' provata dall'hash del file risolto; per scanner con interprete (semgrep da pip) l'identita' non e' provata per intero (`semgrep-core`, ruleset: ipotesi non verificata); un hash dell'entrypoint non e' identita' |
| Esecuzione dello scanner | Un oracolo installato non garantisce di essere eseguito; un agente con Bash puo' eseguire lo scanner con un'altra config o non eseguirlo; il confine e' il runner, non il wrapper |
| SCA (DB advisory) | Vulnerabilita' non ancora pubblicate; riproducibilita' senza pinning del DB (senza pinning, solo inventario piu' delta); tempestivita' oltre l'ultimo DB; integrita' della fonte a monte |
| Baseline SCA e deroghe | `accettato_da`, `approvato_da` e `riferimento_gate` sono tracce e non firme: un record non prova che un umano l'abbia approvato, un agente con Bash puo' produrlo; il baseline non dice nulla sul rischio accettato; il merge-base protegge dalla deriva, non da chi controlla il ref; le formule A12-A19 presumono maintainer = operatore (se D9 e' (c)) |
| Segreti nella storia (gitleaks) | La rotazione o la revoca dei segreti esposti; che non siano gia' compromessi; segreti fuori dal repo o in storie riscritte altrove |
| Comparatore di identita' / diff-check | Non distingue un refactor legittimo da una cancellazione elusiva (per questo NON_VERIFICABILE); la correttezza di una chiusura legittima oltre l'identita' del finding |
| Fix gated | Che il fix non rompa la semantica o non produca regressioni oltre l'oracolo e i test; fix di cause strutturali; la review umana resta necessaria |
| Gate R.14 | La correttezza della decisione umana: garantisce solo che sia stata presa (e il token di dry-run non prova approvazione umana, `db_access.py:19-29`) |
| Rimando CQRL→report di sicurezza | Un CQRL `pass` non attesta la sicurezza; non garantisce che l'oracolo sia stato eseguito (campo `security_scan: assente|<path>`) |
| Threat model (ADR) | Completezza; e' un documento umano, non una verifica |
| Riscansione per cambio di DB / requisito 4 | «Aggiornamento della conoscenza sulle vulnerabilita': non e' "da solo" se non per l'identita' del DB dello scanner registrata nel report (versione e hash). Se il DB non e' pinnabile (ipotesi A13 non verificata), l'esito e' solo inventario piu' delta, non riproducibile. Non garantisce completezza, tempestivita' oltre l'ultimo DB, ne' integrita' della fonte a monte. Nessuna voce di conoscenza e' un requisito: il requisito nasce da una storia R.14.» |
| KB futura (`security/kb-data/`) | Completezza; tempo reale; correttezza della fonte; la barriera di percorso non e' un confine |
| DAST (futuro, fuori epica) | Legittimita' legale del consenso (verifica un record, non il contratto); assenza di impatto sul target; copertura dell'app, delle logiche di business e delle aree autenticate; protezione se il registro e' alterato |
| Varianti e fuzzing (futuro, fuori epica) | Completezza; assenza di falsi negativi; dimostrano solo cio' che riproducono; zero-day |

## §code_intelligence — Code Intelligence Stack (EP-054, v2.37, opt-in)

Stack a tre layer local-first per navigazione codice da parte degli agenti.
Zero dipendenze esterne. `code_intelligence.enabled: false` di default (R.CI1).

| Layer | Tool | Risponde a | Comando |
|---|---|---|---|
| L1 Symbol Resolver | universal-ctags | "dove è definita X?" | `grep` su `.ctags-state/` |
| L2 Semantic Search | tree-sitter + nomic-embed-code + LanceDB | "dove viene gestita Y?" | `/code-search <query>` |
| L3 Impact Graph | graphify (EP-052) | "cosa si rompe se cambio Z?" | Fase 0.bis dev-protocol |

Installazione e configurazione completa: `wiki/runbooks/code-intelligence.md`

---

## §refactor_agent_skills — Fleet Health (EP-060, v2.41, opt-in)

Capability opt-in per il refactor di skill/agenti/flotte via divulgazione
progressiva. Zero dipendenze esterne (stdlib Python).

| Aspetto | Valore |
|---|---|
| Skill | `.claude/skills/refactor-agent-skills.md` |
| Foglie | `.claude/skills/references/refactor/` (5 file) |
| Script | `tools/refactor/{analizza_target,mappa_riferimenti,verifica_flotta}.py` |
| Agente owner | `fleet-doctor` (`.claude/agents/fleet-doctor.md`) |
| Config gate | `refactor_agent_skills.enabled: false` (default) |
| Lint check | Check 4ap (WARNING-only, `.claude/skills/lint-checks-agent-fleet.md`) |
| Runbook | `wiki/runbooks/skill-hygiene.md` |

Vedi PATTERN.md §36 per il pattern completo.

---

## §session_analysis — Session Agentic Analyser (EP-061, v2.42, opt-in)

Capability opt-in per analisi critica post-hoc dell'attivita agentica di sessioni
Claude Code chiuse. Determinism-first (regole deterministiche, no LLM per detection),
LLM advisory. Solo out-of-band (mai in-sessione, R-SAA-8). Zero dipendenze esterne
(stdlib Python).

| Aspetto | Valore |
|---|---|
| Skill | `.claude/skills/session-analysis-protocol.md` (5 fasi) |
| Comando | `/session-analysis [--last N|<session-id>] [--depth=quick|full] [--json] [--save]` |
| Tool | `tools/session-analysis/{parse-transcript,fleet-metrics,detect-anomalies,generate-report}.py` |
| Schema | `tools/session-analysis/schema-anomaly.json` (Draft 2020-12) |
| Config gate | `session_analysis.enabled: false` (default) |
| Precondizione HARD | EP-062 Fleet Telemetry Hardening (walker subagent-aware) |
| Report output | `raw/YYYY-MM-DD-session-analysis-<id-8char>.{md,json}` (dual) |
| Frontmatter invariante | `ingest_eligible: false`, `wiki_ingest_policy: incidents-only`, `ttl_days: 90` |
| Tassonomia v1 (deterministica) | ERROR, BUDGET, DISPATCH (3 core enabled); LATENCY, FLEET (2 opt-in roadmap) |
| Integrazione fleet-doctor | Advisory (`fleet_recommendations` campo JSON), mai auto-invoke (R-SAA-6) |
| Runbook handoff | `wiki/runbooks/session-analysis-fleet-doctor-handoff.md` |
| Kill criterion §23.8 | Hard sunset v2.44 se <5 anomalie azionabili con TSK reale (vedi `EP-061.md#sunset_condition`) |
| Invarianti | R-SAA-1..10 (read-only, redazione, no auto-fix, out-of-band, schema-guard, kill criterion) |
| Provenienza | Tavola Rotonda TR-c4e8f1b2 (forced-synthesis Round 3) — `wiki/decisions/tavola-rotonda-c4e8f1b2-...-2026-09-08.md` |

Concept wiki: `wiki/concepts/session-agentic-analyser.md`

---

## Pipeline tipica con CQRL attivo (v2.12)

```
TSK status:todo ─/dev─▶ status:done, review_status:pending
                              │
                              ▼ (auto via /run, dominio scheduler `review`)
                       /review <TSK-id>
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
       pass: chiusura  conditional: dispatch  reject: gate umano
                       dev-agent (loop max 3) (PATTERN §7 r.16)
```

---

## Memoria cross-conversazione e Storage CQRL

**Memoria cross-conversazione**: il tree `memory/{episodic,semantic,procedural}/` persiste tra
conversazioni. L'orchestrator scrive in `episodic/`; `semantic/` e `procedural/` sono curati
a mano o promossi. Con CQRL attivo (v2.12), il `feedback-router` aggiorna
`memory/semantic/dev-<layer>-recurring-issues.md` con i pattern ricorrenti per dev-agent →
input per i prossimi Develop ("miglioramento a monte").

**Storage CQRL (v2.12)**:

- `code_quality/rules/{canonical,emergent,team-specific}/<rule_id>.md` — KB evolutiva (filesystem-based)
- `code_quality/reports/<TSK-id>-iter-<N>.{json,md}` — report per iterazione (JSON machine-readable + digest umano)
- `code_quality/reports/_digests/<dev-agent>-<YYYY-WW>.md` — digest aggregati settimanali per dev-agent

Side-channel (non un layer del cascade L1→L5), analogo a `memory/`. Scritto solo da
`code-reviewer` (R.Q2 + R.Q6). Le regole `canonical` e `team-specific` sono curate a mano.

---

## Riferimento chiavi factory.config.yaml

> Spostato da CLAUDE.md (US-305). Sta qui e non in `wiki/runbooks/`: e' un indice di
> configurazione, non un runbook, e un runbook su una capability del bucket di ingresso e'
> cerimonia (PATTERN §23.8, `tests/test_fleet_contract.py` asse 4).

[`factory.config.yaml`](factory.config.yaml) al root del repo configura tutte le capability
della factory. Ogni chiave e' documentata qui. Per le capability opt-in, a flag spento la factory
e' identica alla versione precedente (nessun impatto su factory esistenti).

## Central Model Registry (v2.27)

`models.routing.tier_fast` / `tier_default` / `tier_deep` — unico posto dove aggiornare i model ID
per tutti gli agenti; `models.overrides: {}` per eccezioni per-agente.
Tier di default: `tier_fast: claude-haiku-5-5`, `tier_default: claude-sonnet-5-5`,
`tier_deep: claude-opus-5-5` (PATTERN §29.2, cap fan-out + costo ottimizzato).

## Topologia e Stack mode

- **Topologia**: `knowledge-only` | `plan-only` | `full-stack-agents` | `hybrid-be-agents` | `hybrid-fe-agents` | `custom`
- **Stack mode**: `manual` | `guided` | `auto`
- **Routing** TSK → consumer (`agent` | `human`) per layer

## Code paths (v2.12 multi-repo, PATTERN §13)

Lista di entry `{name, path, layers, tags, vcs}` per supportare FE/BE disaccoppiati, microservizi,
micro-frontend, monorepo logico. Legacy `code_path:` (singolare) accettato e auto-promosso.
TSK guadagna campo `target:` opzionale (required solo se ambiguità).

## VCS mode (v2.8, PATTERN §15)

Per ciascuna entry (multi-repo) o top-level (legacy): `monorepo` | `submodule` | `sibling` | `external` | `none`
+ `branch_strategy` + `commit_coupling`. Al massimo **una** entry può essere `monorepo` (R.B6).

## Kanban publish (v2.10, PATTERN §17)

`kanban_publish.provider` (`none` | `github` | `gitlab` | `jira` | `linear` | `custom`)
+ `target` + `auth_env` + `mode: push-only` + `batch_limit` + `mapping` + `labels` + `filter`

## Parallel scheduler (v2.11, PATTERN §18)

`scheduler.enabled` (default `true`) + `max_parallel` (cap fan-out, default `4`)
+ `parallel_gate_threshold` (gate umano sopra N parallel, default `3`)
+ `code_path_conflict` (`strict|warn|off`) + `empty_code_path_policy` (`serial|parallel`)
+ `domains:` (opt-in/out per dominio: ingest/develop/lint/query/plan/design/publish/sync/**review v2.12**)

## Date di lavoro dei TSK (EP-079)

`kanban_dates.required_from` (AAAA-MM-GG, default assente = nessun controllo): data di adozione del Check 4be, conta il giorno del commit che cambia lo stato. Schema in `schemas/factory.config.schema.json`.

`settings_paths_check.required_from` (AAAA-MM-GG, default assente = solo WARNING): da questa data il Check 4bl e' ERROR. Schema in `schemas/factory.config.schema.json`.

`ingest_agent_tools` (Check 4bk): `agenti` (agenti del gruppo oltre alle capability), `exceptions` (lista di `{agente, motivo, scade AAAA-MM-GG}`), `required_from` (AAAA-MM-GG, default assente = solo WARNING; da quella data ERROR). Schema in `schemas/factory.config.schema.json`.

`design_traceability` (EP-097, Check 4bi): `enabled` (default `false`), `required_from` (AAAA-MM-GG, successivo alla `date` del report W1; vuota = spento), `report_w1` (glob, default `wiki/lint/*-w1-design.md`), `soglia_spegnimento` (default `0.10`), `premortem_pre_tpm` (default `false`: premortem del lead-architect prima del TPM, campo `premortem:` sull'ADR, WARNING `adr-senza-premortem`). Campi degli artefatti: `satisfies` e `supersedes` sugli ADR, `decision_refs` sui TSK.

## Lint (v2.44, opzionale)

`lint.kanban`: `scope` (`all` | `open`), `required` e `warning` per tipo (`EP`/`US`/`TSK`: elenchi di
campi), `layer_severity` (`error` | `warning`), `layer_segment`, `id_duplicate`, `equivalents`
(campo → alternative accettate), `in_progress_needs_sprint`, `be_test_evidence` (+ `_consumers`, `_since`, Check 4bh), `tsk_target` (+ `tsk_target_gitmodules`, Check 4j). `lint.wiki`: `orphan` (`index` |
`reachability`), `append_only_links` (`error` | `info`), `date_fields`. Blocco assente = regole del
master (`tools/lint/lint_comune.py`, `REGOLE_DEFAULT`); mappe solo in forma a blocco (una mappa
inline `{...}` e' un errore esplicito). `wiki/log.md` ha in `.gitattributes` il merge driver
`factory-log-union` (`tools/wiki/log_union_driver.py`: unione delle voci append-only, nessuna persa):
registrazione locale con `tools/vcs/install_factory_hooks.py` (anche `--only <hook>`), da ripetere in
ogni clone; senza registrazione git usa il merge di default. L'installer calcola la cartella degli hook
con `git rev-parse --git-path hooks`, quindi funziona anche da un worktree. `wiki_lint.log_append_guard.hook` (default `false`): con `true`
`tools/vcs/install_factory_hooks.py` installa il hook `pre-commit` che rifiuta il commit se una riga di
`wiki/log.md` sparisce senza archivio `wiki/log-*.md`; il Check 4bb resta attivo a flag spento. Hook
locale: ogni collaboratore rilancia l'installer.
`secrets_guard.enabled` (default `false`) e `secrets_guard.required_from` (`AAAA-MM-GG` o `null`):
con `enabled: true` il hook `pre-commit` esegue, dopo la guardia del log, `tools/security/secrets_guard.py --hook`
`--staged` sui blob dell'indice (oracolo gitleaks, nessun pattern proprio). Con `required_from`
raggiunta (severita' ERROR) FAIL e NON_VERIFICABILE bloccano il commit. La deroga per NON_VERIFICABILE
(mai per un FAIL) e' un record in `secrets_guard.deroghe` (default `security/secrets-guard-deroghe.json`,
lista JSON con `motivo`, `scadenza`, `approvato_da`, `riferimento_gate`, e `ambito` facoltativo: `non_verificabile` di default, `config_gitleaks` per una modifica di `.gitleaks.toml`) letto dal merge-base fra HEAD e
`secrets_guard.ref_protetto` (default `origin/main`): non dal working tree ne' dal branch, e scaduto vale
come assente. Il record e' una traccia, non una firma. `SECRETS_GUARD_OVERRIDE` non e' piu' letta (EP-108
US-423). NON_VERIFICABILE per binario mancante distingue «assente» da «presente ma non raggiungibile dal
PATH del processo». Prima, o con `null` (severita' WARN), il commit
passa e l'hook stampa «commit NON bloccato». Previene nel percorso cooperativo, rileva negli altri:
`--no-verify` e `core.hooksPath` aggirano il hook, e gitleaks ha falsi negativi.
`scanner_identity.pins` (default `security/scanner-pins.json`) e `scanner_identity.ref_protetto` (default
`origin/main`): identita' fissate degli scanner di sicurezza (EP-109 US-424, decisione D7: percorso assoluto
piu' sha256). `tools/security/scanner_identity.py` risolve gitleaks, osv-scanner, trivy e semgrep: con un pin
il PATH non si consulta; il pin si legge dal merge-base, mai dal working tree; la versione si legge eseguendo
lo scanner solo dopo che lo sha256 coincide. Esiti: IDENTIFICATO, oppure NON_VERIFICABILE con motivo `assente`,
`non_raggiungibile`, `identita_divergente` o `identita_non_fissata`. Pin nuovo: `--misura SCANNER --path P`
(esegue P). Per semgrep l'identita' e' parziale (script, interprete, RECORD; i file del pacchetto non sono
ricontrollati). Oggi nessun oracolo lo chiama: lo useranno gli oracoli di EP-109, e `secrets_guard.py` risolve
ancora gitleaks col PATH.
`suppression_check.accettazioni` (default `security/suppression-accettazioni.json`) e
`suppression_check.ref_protetto` (default `origin/main`): `tools/security/suppression_check.py` (EP-109 US-428
AC3) da' FAIL su ogni soppressione aggiunta fra il merge-base e HEAD (`nosemgrep`, `nosec`, `gitleaks:allow`,
`trivy:ignore` in un commento; righe di `.trivyignore`, `.gitleaksignore`, `.semgrepignore`, `osv-scanner.toml`;
un file di soppressioni rinominato conta tutto), salvo un record di accettazione gia' presente al merge-base
(`path`, `tipo`, `testo`, `motivo`, `scadenza`, `accettato_da`, `riferimento_gate`). Ref non risolto =
NON_VERIFICABILE. Il record e' una traccia, non una firma. Accanto a `tools/security/finding_compare.py`, che
confronta due esecuzioni per identita' del finding: li compongono gli oracoli di analisi statica qui sotto.
`security_scan.semgrep_ruleset`, `security_scan.trivy_config` (default `null`) e `security_scan.ref_protetto`
(default `origin/main`): oracoli `python3 tools/security/sast_guard.py CODE_PATH` (semgrep) e
`python3 tools/security/iac_guard.py CODE_PATH` (trivy config), motore in `tools/security/oracolo_statico.py`
(EP-109 US-427). Solo `code_paths[]` dichiarati, mai la factory (exit 2); binario identificato con
`scanner_identity` ed eseguito dal percorso fissato; ruleset della factory al merge-base (sha256 e commit nel
report); alberi PRIMA (merge-base del code_path) e DOPO (HEAD) con i file di config dello scanner del
merge-base; confronto con `finding_compare` e diff-check con `suppression_check`. FAIL per finding o
soppressione nuova, NON_VERIFICABILE per file cancellato o spostato, binario non identificato o ruleset
`null`; PASS = nessun finding nuovo rispetto al merge-base, non «codice sicuro». Nel master i ruleset sono
`null`: oggi gli oracoli danno NON_VERIFICABILE.
`security_scan.osv_db_dir`, `security_scan.trivy_cache_dir` (default `null`) e `security_scan.sca_baseline` (default
`security/sca-baseline.json`): oracolo SCA `python3 tools/security/sca_guard.py CODE_PATH [--scanner osv-scanner|trivy]`
(EP-109 US-425). CycloneDX offline (osv `--offline`, trivy `--skip-db-update --offline-scan`): inventario (purl),
identita' del DB nel report (sha256 degli `all.zip`; sha256 di `trivy.db` e `UpdatedAt`) e due delta sullo stesso DB:
vulnerabilita' nuova dal commit e non nel baseline = FAIL; presente anche al merge-base e non nel baseline = debito non
nominato o DB aggiornato a commit fermo, NON_VERIFICABILE e mai FAIL; senza baseline il primo run e' NON_VERIFICABILE.
Baseline (US-425 AC4): record `{id, accettato_da, riferimento_gate, accettato_il, scadenza, purl?, motivo?}` con
scadenza al massimo 90 giorni dopo l'accettazione; scaduto, incompleto o con altri campi (niente testo di advisory)
vale come assente ed e' elencato fra gli scartati. `security_scan.sca_required_from` (default `null`): prima di quella
data un FAIL e' WARN (exit 0, «non bloccante»), da quella data blocca (exit 1).
Senza lockfile vede solo le dipendenze dirette. Il DB si scarica una volta fuori dall'oracolo
(`osv-scanner ... --download-offline-databases`, `trivy ... --download-db-only`).

## Code quality review (v2.12, PATTERN §19)

`code_quality.enabled` (default `false`) + `max_iterations` (default 3, R.Q4)
+ `thresholds` (`confidence_min: 0.6`, `batching_split: 7`, `pass_rate_warn: 0.05`, `false_positive_warn: 0.30`)
+ `passes` (idiomaticity/design/robustness)
+ `router` (`strategy: severity-tiered`, `max_diff_lines: 80`)
+ `ruleset.path` + `reports.path`
+ `trigger_default` (`enabled`, `layer[]`, `consumer[]`, `review_status_field`, `review_status_default`: review di default, Fase 4-quater + dispatch §12)

## Compression layer (v2.14, PATTERN §20)

**Asse output (Fase 1)**: `compression.output.enabled` (default `false`, opt-in R.C6)
+ `provider: caveman` + `policy_profile` (`conservative` default | `aggressive` | `custom`)
+ `invariants` non overridabili (`to_user`/`to_artifact`/`propagate_resolution` sempre off, R.C1)
+ `channels` (solo se `custom`) + `chain_depth_downgrade` (R.C3)
+ `cross_factory: off` (R.C4 in federated) + `drift_fallback` (R.C5, marker `AMBIGUOUS_HANDOFF`/`REQUEST_CLARIFY`)

**Asse context (Fase 2)**: `compression.context.enabled` (default `false`, opt-in R.G6)
+ `provider` (`none` | `graphify-cloud` | `graphify-ollama`)
+ `targets` (lista `{kind: code_path|wiki, name|path, gitignore_patterns}`)
+ `update_strategy` (default `incremental`) + `full_rebuild_cron` (weekly drift mitigation R.G4)
+ `ci_strategy` (`cache-with-fallback` default)
+ `confidence_gating` (R.G2: executor → `EXTRACTED` only / explorer → `+INFERRED` / reviewer → tutto)
+ `full_rebuild_cost_warn` (USD soglia conferma esplicita)
+ `mcp_server` (per-agent default | shared opt-in)

## Hybrid Wiki Search (v2.29, EP-042, PATTERN §31, opt-in)

`wiki_search.enabled` (default `false`) + `backend: auto` (auto|fts5|hybrid; auto = fts5 se mancano
`lancedb`/`sentence-transformers`) + `fts_db: .wiki-search/fts.sqlite` + `embedding_model: paraphrase-multilingual-MiniLM-L12-v2`
+ `mode: hybrid` (hybrid|vector|fts) + `top_k: 5` + `exclude_types: [meta]`;
a flag spento factory identica a v2.28; dipendenze `lancedb`/`sentence-transformers` non importate (R.WS2);
indice in `.wiki-search/index.lance` (gitignored); aggiornamento via `/wiki-search reindex`

## Temporal Estimate Protocol (v2.30, EP-043, opt-in)

`temporal.estimate_protocol.enabled` (default `false`) + `budget_ms` (S/M/L/XL in ms)
+ `thresholds` (warn/escalate_time_ratio, escalate_confidence_min);
skill `.claude/skills/temporal-estimate-protocol.md` 4 fasi;
invocazione post temporal-budget-governor pre-retry-wave

## Sprint Progress Signal (v2.30, EP-043, opt-in)

`analytics.sprint_progress.enabled` (default `false`) + `velocity_rolling_days: 7`;
tool `tools/analytics/sprint-progress.py`; comando `/sprint-progress`; fallback kanban garantito

## Ponytail Decision Ladder (v2.39, EP-057, opt-in)

`ponytail.enabled` (default `false`) + `passes.yagni_ladder` (richiede `code_quality.enabled: true`, HARD DEP)
+ `lint.severity` (warning|info, forzato info su `code_path: "."`) + `audit.exclude_patterns`;
YAGNI gate a 7 livelli (Lint Check 4ao WARNING-only post-develop + Pass 4 advisory in code-review-protocol mai determinante);
comandi `/ponytail-review` + `/ponytail-audit` + riga `ponytail-gain` nel token ledger;
invariante locale R.PY1 (security/a11y/trust-boundary inviolabili, non bypassabile);
a flag spento factory identica a v2.38; vedi `wiki/concepts/decision-ladder.md`

## Grafo della conoscenza (EP-106, stadio 1, opt-in)

`grafo_conoscenza.enabled` (default `false` nelle derivate; **acceso nel master il 2026-11-18** per decisione del maintainer, con deroga al contratto della flotta, tetto 32 → 33; nel master la plancia si avvia con `python3 -m visual --force`). Il comando
`python3 tools/graph/build_graph.py [--formato md|json] [--out <cartella>] [--ref <ref>]` gira anche a flag
spento, come gli altri tool su richiesta: il flag governa le superfici che lo consumeranno.
Legge `wiki/`, `management/kanban/` e `raw/` (solo path) e produce la topologia JSON (senza coordinate, ordine
stabile, un arco per coppia sorgente -> target con `count`) e un report. Ogni arco ha `origin`
(`declared`, `derived`, `inferred`) e `resolution` (`resolved`, `unresolved-path`, `id-kanban`, `placeholder`;
`null` se `origin` non e' `declared`). `resolved` si legge «fonte trovata»: il file esiste, non e' verificato
che la pagina dica cio' che la fonte dice. Il report elenca gli archi non risolti per pagina con `status`
(«non dichiarato» se manca) e «a chi spetta» (`wiki-keeper` per draft, `wiki-keeper, poi maintainer` per
review, approved e non dichiarato). In sola lettura; `--out` rifiutato sotto `apps/` e negli alberi di
`sync-docs.ts`. Nessun arco `inferred` in questo stadio, nessun agente nuovo, nessun comando slash.
Il parser dei wikilink e' condiviso con Check 1 (`tools/lint/wikilink.py`).

## Documentazione (EP-075, opt-in)

`documentation.enabled` (default `false`) + `redaction.enabled` (default `true`) + `tech_site`
(`output_dir`, `include_sections`, `exclude_sections`) + `functional_docs` (`output_dir`, `services`:
catalogo servizio -> pagine wiki, vuoto = si usano i file di `wiki/user-flows/`) + `weekly_digest`
(`output_dir`, `release_kinds`: lista di `{prefix, label}` per etichettare i rilasci del registro).
Tre comandi: `/doc-tecnica`, `/doc-funzionale`, `/digest-settimanale`. Ogni output passa da
`tools/docs/redact.py` (PAT, token, JWT, chiavi private, `password:`, `Authorization:`): un
segreto blocca la scrittura (exit 2/3), il controllo non si aggira. A `documentation.enabled: false`
gli script stampano un avviso ed escono con codice 0. Gli output generati (`deliverables/doc-tecnica/`,
`deliverables/doc-funzionale/`, `deliverables/digest/`) non si versionano. Nasce dalla derivata
portale-servizi-factory, generalizzata (nessun servizio o cliente cablato).
Il Word di `build_functional_docs.py --file` (EP-113) ripete l'intestazione delle tabelle su ogni
pagina, non manda a capo le celle con un identificativo e rende `!titolo` come figura con
didascalia «Figura N – titolo» a campo SEQ ed Elenco delle figure in coda (Word aggiorna i campi
all'apertura); un'immagine remota o mancante resta un segnaposto con avviso, non blocca.

## Cost alert (EP-074, EP-075, opt-in)

`analytics.cost_alert.enabled` (default `false`) + `agent` (default `false`: con `true` il path
escalate scrive un record in `alerts_dir`) + `rules_file: analytics/alert-rules.yaml` +
`alerts_dir: analytics/alerts` (record locali, non versionati). Nel file delle regole: `rules[]`
(`period` session|daily|weekly|monthly, `threshold_usd`, `action` warn|escalate, `notes`,
`operator` per una regola personale), `plans` (`license_usd_month`, `central_funding_usd_month`,
`included_usd`, `included_period` weekly|monthly, `action`) e `subscriptions[]` (`operator`,
`plan`). Precedenza per periodo: regola personale > quota del piano > regola generale. Le soglie
del master sono esempi; i costi sono a listino API, in USD (`analytics/pricing.yaml`).
Cosa NON garantisce: misura solo i transcript locali, quindi non rileva l'uso di chiavi API o
credenziali cloud fuori dalla macchina (LLMjacking); budget e alert vanno impostati lato provider.

`cost_alert.py reconcile` confronta lo store con i transcript dell'operatore (tutte le cartelle
sotto `--transcripts-root`) ed emette l'etichetta `affidabile` | `sottostima` | `non verificabile`,
mostrata anche da `check` e `breakdown`. Chiavi: `analytics.reconcile.underestimate_threshold`
(default `0.05`, da confermare dopo due settimane di misura) e `analytics.reconcile.worktree_aliases`
(lista di regex sui nomi delle cartelle dei transcript da attribuire alla factory; default `[]`).
Lettura: `tools/analytics/MODELLO.md`.

## STE-lite (EP-076, opt-in)

`ste_lite.enabled` (default `false`, spenta per decisione TSK-809) + `targets` (glob controllati da
`tools/lint/ste_lite.py --targets` a flag acceso) + `limits` (`procedural_words: 20`,
`descriptive_words: 25`, `paragraph_sentences: 6`) + `glossary` (termine preferito → sinonimi
vietati) + `max_fact_loss: 0.10` (soglia di `tools/lint/fact_loss.py`). `/ste-lite <file>` su
file espliciti gira anche a flag spento.

## Pratiche di ingegneria (EP-077, opt-in)

`engineering_practices.enabled` (default `false`, R.P3) + `kanban_path` (default `management/kanban`)
+ `analytics_path` (default `analytics/pocock-pilota`, registri `controlli.yaml`, `invenzioni.yaml`,
`bilancio-n1.yaml`). Gli agganci in dev-protocol, scrivi-task, tpm, product-manager, lead-architect,
fe-dev e code-reviewer valgono solo a flag acceso; la Passata 6 ha il proprio flag
`code_quality.passes.spec_adherence` (default `false`). Registri vuoti: gli indicatori nascono dall'uso.
Non adottate dalla derivata: setup-matt-pocock-skills, triage, to-spec, implement, implement-spec,
wizard, pr; wayfinder rinviata.

## Mestiere della UI (EP-090, opt-in)

`ui_craft.enabled` (default `false`, R.P3) + `worst_case_data` (skill `kowalski-worst-case-data`, `/worst-case`,
fase opzionale del functional oracle) + `motion_review` (Passata 7 advisory di `code-review-protocol`).
`prototyping.variants` (intero 1..5, default 1 = invariato). Campo TSK `base_commit:` opzionale, nessun flag.
Non adottate: emil-design-eng, apple-design, animate, animate-expo, choreograph, gestures, mobile-native,
write-swift, ask-sonner, pick-ui-library, animation-vocabulary, find/remove-animations, animation-performance.

## Repo align (v2.44, EP-068, opt-in)

`repo_align.enabled` (default `false`) + `triggers.on_explicit: true`
(il comando funziona anche a flag spento) + `on_tsk_closed_count` (0 = disabilitato; contato a fine TSK
da `tools/vcs/contatore_chiusure.py`, chiamato da `dev-handoff`, anche per `ai_policy_check`)
+ `auth_domains: []` (opzionale, per remote privati: lookup per `name` o `path`, token da `token_env`/`token_env_var`)
+ `env_file` (opzionale, file `KEY=VALUE` letto e mai eseguito).
Zero mutazione: `git ls-remote` e' l'unica operazione con effetti remoti (R.14, R.B8)

> Spostato da PATTERN (§15) nel 2026-10-05: per §23.8 una capability non ancora esercitata
> non ha norma nel PATTERN (`tests/test_fleet_contract.py` asse 4).

**Verifica dell'allineamento** (v2.44, EP-068 US-299): `/repo-align` risponde a «il lavoro
locale e' gia' sul remote?» per ciascuna entry, **secondo il suo `mode`** — `monorepo` e
`sibling` confrontano HEAD locale con il tip del remote, `submodule` confronta il
**gitlink-SHA registrato nel parent** (mai HEAD del checkout: un detached HEAD del submodule
non e' segnale di divergenza), `external` restituisce `unverified: opaque_topology` per
definizione, `none` e' escluso dal set. `git ls-remote` e' l'unica operazione con effetti
remoti: mai `fetch`, `pull`, `checkout`, `reset`, `submodule update` (R.14, R.B8). Per
`diverged` distingue **avanti** da **indietro**; la prima meta' e' quella che rende visibile
il proprio silenzio. Opt-in via `repo_align:`, ma il comando funziona anche a flag spento.

## §ai_policy — AI policy check (v2.44, EP-068, opt-in)

`ai_policy_check.enabled` (default `false`) + `scope: []`
(i soli path scansionati; vuoto = «nulla da scansionare», exit 0, **non** un errore)
+ `triggers.on_explicit: true`.

**Due layer**:

| | Layer-1 — preventivo | Layer-2 — detective |
|---|---|---|
| Dove | hook git in `.git/hooks/` | `tools/vcs/ai-policy-scan.py` + `/ai-policy-check` |
| Quando | prima del commit | dopo, sulla finestra `@{u}..HEAD` + diff staged |
| Limite | locale, non committato, non condiviso; un runner di hook di progetto che ridirige `core.hooksPath` lo rende inerte | non impedisce nulla: segnala |


> Spostato da PATTERN §23.9 nel 2026-10-05, stessa ragione (§23.8).

**Enforcement a due layer** (v2.44, EP-068 US-300):

| | Layer-1 — preventivo | Layer-2 — detective |
|---|---|---|
| Meccanismo | hook git `pre-commit` / `commit-msg` in `.git/hooks/` | `tools/vcs/ai-policy-scan.py`, comando `/ai-policy-check` |
| Momento | prima del commit | dopo: finestra `@{u}..HEAD` + diff staged, messaggio **e** righe aggiunte |
| Visibilita' | locale, non committato, **non condiviso** fra i clone | committato in `.claude/` e `tools/`, visibile a tutti |
| Limite | un runner di hook di progetto che ridirige `core.hooksPath` lo rende **inerte** | non impedisce nulla: segnala |
| Config | — | `ai_policy_check:` in `factory.config.yaml`, default `enabled: false` |

I due layer sono complementari, non alternativi: il Layer-1 previene, il Layer-2 **vede**
cio' che il Layer-1 non ha prevenuto. Output partition `{clean, violations, unscanned}`,
advisory per default (exit 0 sempre), `--strict` per l'uso come gate pre-push.

> **Guardia di scope — invariante, non convenzione.** Il repo della factory stessa **non e'
> mai scansionato**, nemmeno se passato esplicitamente a `--repos`; il tentativo produce un
> rifiuto esplicito, mai uno skip silenzioso. Nel repo del framework l'attribution AI e'
> **dovuta**, non vietata (quarta regola qui sopra): uno scan indiscriminato segnalerebbe
> ogni commit, e un check che urla sempre e' un check che viene spento. Si scansionano
> soltanto i path dichiarati in `ai_policy_check.scope[]`.

Per il pattern (policy di attribution): PATTERN §23.9.

## Kanban coordination (v2.43, EP-064, opt-in)

`kanban_coordination.enabled` (default `false`) + `oracle_window_days: 30` + `stale_assignment_days: 7`

## Visual channel (v2.44, EP-067, opt-in)

`visual_channel.enabled` (default `false`) + `host` + `port` + `runtime_timeout_seconds` + `stale_after_seconds`
+ `coordinamento.fonte` (`worktree` | `commit`, default `worktree`) + `coordinamento.config` (default
`analytics/coordinamento/config-<git user.name>.json`)

## Session analysis (v2.42, EP-061, opt-in)

`session_analysis.enabled` (default `false`). Precondizione HARD: EP-062 Fleet Telemetry Hardening.
`session_analysis.advisory_model` (default `""` = `models.routing.tier_fast`): modello della nota LLM
advisory di `--depth=full` (`tools/session-analysis/llm-advisory.py`, via `claude -p`).

## Velocity e report PM (EP-078)

`/velocity`: config facoltativa `analytics/velocity/config.json` (copia di `config.example.json`; senza
file valgono i default), tutte chiavi opzionali: `kanban`, `epiche` (vuoto = tutte, o `{id, gruppo}`),
`includi_archivio`, `punti` (taglia → punti), `giorni` (taglia → giorni), `stati_chiusi_esclusi`,
`finestra_settimane` (3), `soglia_chiusura_in_blocco` (5), `team` (per `--per-persona`), `agenti`,
`obiettivo`.

`/coordinamento --pianifica`: blocco `pianificazione` della config operatore
(`analytics/coordinamento/config-schema.json`; senza, `pianifica.py` esce con codice 2). Obbligatori:
`persone_assegnabili`, `orizzonte_giorni_lavorativi`, `dimensione_predefinita`, `punti_priorita`,
`fasce_urgenza`, `punti_sblocco_per_tsk`. Opzionali: `persone_da_riassegnare`, `referente_bloccanti`,
`dimensioni_giorni` (taglia → giorni; obbligatoria salvo `velocity_config`), `velocity_config` (path di
una config di `/velocity`: fornisce la tabella taglia → giorni e la velocity misurata per persona, come
dato di confronto), `velocity_misurata` (default `true`), `dimensione_minima_giorni`. Per obiettivo:
`ambiente_rilascio` (default `test`); per sezione: `tsk` e `sottoperimetro`.

## Altre capability opt-in (riferimenti PATTERN)

Vedi `PATTERN.md` §13 (topology), §14 (stack modes), §15 (VCS),
§16 (sync adapters multi-sorgente — PDF + Figma + repo esistente v2.12 + **graph v2.14 Fase 2**),
§17 (publisher adapters multi-target), §18 (parallel scheduling v2.11),
§19 (code quality review layer v2.12), §20 (compression layer a due assi v2.14),
**§29 (factory scalability patterns v2.27: thin-orchestrator, capability advertisement, WAVE_ID propagation, Check 4ai)**.

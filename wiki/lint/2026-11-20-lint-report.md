---
type: lint
date: 2026-11-20
run: 3
heal_eligible_count: 0
heal_eligible_categories: []
script_heal_label: [4ax]
---
# Lint Report — 2026-11-20 (terza esecuzione del giorno)

> **Terza esecuzione del 2026-11-20.** Sostituisce il report del run 2 (committato in `c11af0a`, resta in `HEAD`). Il run 2 era precedente all'ingest delle fette B e C della persistenza (commit `00c395f`) e alla chiusura di TSK-003, TSK-004, TSK-005 e US-013 (commit `df6e9f1`, `6ec0b9c`).

Factory `wiki-factory`, PATTERN v2.48, topologia `custom`. Esecutore: wiki-lint. Solo report, nessun auto-fix. `code_repos/llm_wiki` non e' stato letto ne' scritto: l'unica interrogazione e' `git submodule status`, che non entra nel submodule.

Report deterministico completo (righe di dettaglio non trascritte): [2026-11-20-deterministic.md](2026-11-20-deterministic.md).

**Totale: 0 ERROR, 15 WARNING, 7 INFO.** Script: 0 ERROR, 6 WARNING, 3 INFO. Lettura: 0 ERROR, 9 WARNING, 4 INFO. `heal_eligible_count: 0` (vedi §heal-eligible per la posizione su 4ax).

Il run 2 aveva 0 ERROR, 15 WARNING, 9 INFO.

## Cosa e' cambiato rispetto al run 2

| Esito | Finding (ID del run 2) | Evidenza letta ora |
|---|---|---|
| **Risolto** | W14 `unsourced-claim` in `wiki/sources/2026-11-20-repo-llm_wiki.md` riga 78 | il file e' stato riscritto dall'ingest (`00c395f`, 7 righe toccate); lo scan Check 2 non produce piu' candidati su di esso |
| **Risolto** | I1, I2 `raw-non-ingerito` / fetta B | `raw/.extraction-manifest.json`: 5 entry (a, b, c, base, sessione), tutti i `primary_artifact` esistono; le tre fette sono citate in `wiki/**` (427 citazioni, vedi audit); TSK-003, TSK-004, TSK-005 `status: done`, `closed_at: 2026-11-20` |
| **Risolto** | I3 `popolazione-untracked` | `git status --short` a inizio run: nessun `??`, solo `M wiki/lint/2026-11-20-deterministic.md` (output dello script, rigenerato da questo run) |
| **Risolto** | I4 `session-lock` | `ls -la | grep -i lock` alla radice: nessun risultato, `.session-close.lock/` non esiste piu' |
| **Risolto** | I7 `closure` di TSK-002 | US-013 `status: done`, i 5 AC `[x]`; TSK-005 §Chiusura riporta AC1 e AC2 come `n/a` con la parola «deroga» e perimetro di TSK-002..004 |
| **Nuovo** | W16 `gitleaks` assente (4bj) | script: `NON_VERIFICABILE: gitleaks assente (non nel PATH ne' nei percorsi noti)`. Il run 2 lo aveva eseguito su 1045 file |
| **Nuovo** | I8 submodule non inizializzato | `git submodule status` → `-e08cfce65aad8b76b13546a081c1a8d4422b70c3 code_repos/llm_wiki` (prefisso `-`); nel run 2 era ` e08cfce...` (inizializzato) |
| **Nuovo** | I9 conteggio contraddizioni | 8 pagine con `## Contradictions` (non 9) e 20 voci; il log dell'ingest dichiara «18 distinte su 8 pagine» (vedi §Contraddizioni) |
| **Esteso** | W15 | ora copre tre testi superati nel corpo (sommario di `archivi-persistenza`, tesi «solo due» di `versioni-e-migrazioni` e `schema-dati`, riga `project.json`), tutti dichiarati in `## Contradictions` |
| **Invariato** | W1, W2, W3, W4, W5, W6, W7, W8-W13, I5, I6, e i 3 INFO da script | stessi valori letti (dettaglio sotto); W8-W13 hanno le stesse righe del run 2 |

Nota di numerazione: gli ID W/I del run 2 sono mantenuti dove il finding e' invariato; W14, I1-I4 e I7 non esistono piu'. I nuovi sono W16, I8, I9.

## Popolazione effettiva letta

| Fonte | Valore letto |
|---|---|
| Pagine wiki (`wiki/**`, esclusi `lint/`) | 29 file `.md` (script di audit nello scratchpad: `29 files`) |
| Check 1 (script) | `Check 1 completato su 26 file — 0 orphan rilevati, 0 broken-link rilevati` |
| Check 4 (script) | `Check 4 completato su 25 sezioni «Storie collegate»` |
| Check 4ag (script) | `22 file — 0 MISSING-DATE, 0 STALE` |
| Kanban | `[3] popolazione: 4 EP, 34 US, 10 TSK`; TSK: 6 `done` (001-005, 010), 4 `todo` (006-009); US-013 `done`, US-012 `in_progress`; EP-001..EP-004 `defined` |
| Gap | `[4bc] OK — 35 gap, nessuna chiusura non verificata` (erano 25: +10 dall'ingest, come dichiarato) |
| Git | ultimo commit `6ec0b9c`; working tree pulito a inizio run |

## Riepilogo deterministico (script, `run-deterministic.py`)

Exit code del runner: 0. Tabella copiata dal file deterministico.

| Check | Cosa | ERROR | WARNING | INFO | Exit |
|---|---|---|---|---|---|
| 1, 4, 4ag | Struttura wiki: orphan, broken-link, storie collegate, staleness | 0 | 0 | 0 | 0 |
| 3, 4as, 4b | Integrita' kanban, assignee, question | 0 | 1 | 0 | 0 |
| 4au | Roll-up di stato TSK, US, epica e sprint.md | 0 | 1 | 1 | 0 |
| 4am | Coerenza delle versioni dichiarate | 0 | 0 | 0 | 0 |
| 4ar | Annotazioni SUNSET scadute | 0 | 0 | 0 | 0 |
| 4aq | Path portabili (1057 path tracciati) | 0 | 0 | 0 | 0 |
| 4ax | ignore = dirty sui submodule | 0 | 1 | 0 | 0 |
| 4bb | wiki/log.md append-only | 0 | 0 | 0 | 0 |
| 4bc | Chiusure dei gap verificate | 0 | 0 | 0 | 0 |
| 4bd | wiki/gaps.md append-only | 0 | 0 | 0 | 0 |
| 4be | Date di lavoro dei TSK | 0 | 0 | 0 | 0 |
| 4bf, 4bg | Ordine del log, contatore Sources | 0 | 0 | 0 | 0 |
| 4bh | Evidenza di test sui TSK be (regola spenta) | 0 | 0 | 0 | 0 |
| 4bi | Tracciabilita' design (spento) | 0 | 0 | 0 | 0 |
| 4bj | Segreti nei file tracciati (gitleaks) | 0 | 1 | 0 | 0 |
| 4bl | Path assoluti in `.claude/settings.json` | 0 | 0 | 0 | 0 |
| 4bk | Agenti lettori di contenuto non fidato con Bash | 0 | 0 | 0 | 0 |
| 4g | depends_on e scheduler | 0 | 0 | 2 | 0 |
| 4ai | Integrita' del layer agenti | 0 | 2 | 0 | 0 |
| 4aj, 4bm | `model:` degli agenti contro il registro | 0 | 0 | 0 | 0 |
| 4bn | Marcatori di conflitto su HEAD | 0 | 0 | 0 | 0 |
| 4bo | Lettori diretti del registro sessioni | 0 | 0 | 0 | 0 |
| 4j | Repository risolvibile sui TSK (regola spenta) | 0 | 0 | 0 | 0 |
| **Totale** | | **0** | **6** | **3** | 0 |

## Riepilogo check a lettura

| Check | Errors | Warnings | Note |
|---|---|---|---|
| 1 — Orphan + wikilink | 0 | 0 | script; verifica indipendente: 347 wikilink in 28 file (escluso `lint/`), 0 rotti |
| 2 — Claim senza fonte | 0 | 6 | euristica a riga, soglia 20 parole, finestra 3 righe; W8-W13 |
| Citation audit | 0 | 0 | 427 citazioni, 0 malformate, 0 path inesistenti, 0 sezioni assenti (inline) |
| 3, 4 — Kanban e coerenza wiki↔kanban | 0 | 0 | script |
| 4b — Q↔kanban | 0 | 1 | script, W1 |
| 4c — Topology/routing | 0 | 1 | W6 |
| 4d — Coerenza VCS | 0 | 0 | `factory.config.yaml` riga 83: `commit_coupling: float` |
| 4e — Manifest↔raw | 0 | 0 | 5 entry, tutti i `primary_artifact` esistono; `ls raw`: 4 `.md` piu' `images/` e `sessions/`, nessun `.txt`/`.kb.json` orfano |
| 4f — Publisher | 0 | 0 | `factory.config.yaml` riga 147: `provider: none` |
| 4g | 0 | 0 | script; il candidato `dependencies-drift` e' scartato come nel run 2 |
| 4ah | 0 | 0 | invariato dal run 2 (config non modificata: `git status` pulito) |
| 4ai | 0 | 2 | script, W4 e W5 |
| 4am — Versioni | 0 | 0 | script, `SSOT pattern_version = 2.48` |
| Struttura frontmatter wiki | 0 | 1 | W7 (`wiki/gaps.md`); le altre 28 pagine hanno i 6 campi (inclusi i 5 file nuovi) |
| Contradictions (8 pagine) | 0 | 1 | W15, piu' I9 |

## ERROR meccanici (heal-eligible)

Nessuno. `heal_eligible_count: 0`.

## ERROR non meccanici

Nessuno.

## WARNING (igiene, mai heal-eligible)

### Da script

- **W1** [orphan-pending-clarification][4b] `management/kanban/EP-002-conoscenza-layer-di-persistenza/US-018-dimensioni-e-crescita-archivi/US-018.md`: «Q_004 non citata nel pending_clarification di alcun ADR». Letto: `pending_clarification: [Q_004]` (riga 9), `status: ready`; Q_004 in `management/questions.md` riga 11. Invariato; atteso finche' Q_004 e' aperta. Fix: nessuno, risponde l'utente a Q_004.
- **W2** [status-rollup][4au.1] `management/kanban/EP-001-difetti-master-analisi-e-segnalazione/US-012-convenzioni-segnalazione-master/US-012.md`: «US status=in_progress — tutti i 1 TSK sono terminali». Letto: `status: in_progress`; TSK-001 `status: done`. Invariato. La motivazione del run 2 (AC7 derogato a livello di TSK, resta `in_progress` fino ai TSK dello sprint 02) non e' stata riletta in questo run. Fix: nessuno finche' AC7 non e' verificato.
- **W3** [submodule-ignore-missing][4ax] `.gitmodules`, sezione `submodule "code_repos/llm_wiki"`. Script: «nessun `ignore`». Fix suggerito dallo script: `git config -f .gitmodules submodule.code_repos/llm_wiki.ignore dirty`. Non conteggiato come heal-eligible secondo il contratto (vedi §heal-eligible). **Non applicare senza decidere il difetto 11**: `wiki/concepts/master-difetti-rilevati.md` riga 93 riporta che il fix modifica `.gitmodules`, che PATTERN-integration vieta agli agenti fuori da vcs-handoff. Invariato.
- **W4** [agent-command-missing][4ai.3] `.claude/agents/fleet-doctor.md` referenzia `/factory-upgrade`, `.claude/commands/factory-upgrade.md` non esiste. Fix: aggiungere il comando o correggere il nome. US-006. Invariato.
- **W5** [agent-command-missing][4ai.3] `.claude/agents/release-manager.md` referenzia `/release`, `.claude/commands/release.md` non esiste. Stesso fix, US-006. Invariato.
- **W16** [secrets][4bj] (nuovo) script: «NON_VERIFICABILE: gitleaks assente (non nel PATH ne' nei percorsi noti): va installato. Nessuna verifica dei segreti e' avvenuta». Nessun segreto e' stato rilevato ne' escluso da questo run. Evidenza esterna letta: TSK-005 §Chiusura AC3 riporta `gitleaks detect --no-git --redact` → `no leaks found` sui tre raw prima dell'ingest. Fix: installare gitleaks nell'ambiente e rilanciare `python3 tools/lint/check-secrets.py --root . --oggi 2026-11-20`.

### Da lettura

- **W6** [dev-agents-without-code-path][4c] `factory.config.yaml` riga 62 `code_path: ""`, riga 50 `topology: custom`. Falso positivo semantico: `code_paths` e' valorizzato con `llm_wiki`. US-010. Invariato.
- **W7** [missing-frontmatter-field] `wiki/gaps.md`: mancano `sources` e `tags` (scansione: unico file su 29). Non deducibile dal path. Fix: dichiarare `gaps.md` esente nella skill o aggiungere `sources: []` e `tags: [gaps]` (a carico di wiki-keeper, file append-only). US-005. Invariato.
- **W8-W13** [unsourced-claim][Check 2] sei righe di prosa con almeno 20 parole senza `[^src: ...]`/`[^code: ...]`/wikilink in [riga, riga+3]. Invariate rispetto al run 2:

  | ID | File e riga | Parole | Lettura |
  |---|---|---|---|
  | W8 | `wiki/concepts/master-difetti-rilevati.md` riga 18 | 94 | testo di metodo; candidato a esenzione |
  | W9 | stesso file, riga 37 (difetto 3) | 36 | citazione a fine blocco, riga 41 |
  | W10 | stesso file, riga 65 (difetto 7) | 24 | citazione a riga 69 |
  | W11 | stesso file, riga 79 (difetto 9) | 26 | citazione a riga 83 |
  | W12 | stesso file, riga 93 (difetto 11) | 23 | citazione a riga 97 |
  | W13 | `wiki/concepts/llm-wiki-archivi-persistenza.md` riga 49 | 27 | voce di elenco coperta dall'introduzione riga 45, oltre la finestra in avanti |

  Fix: spostare la citazione subito dopo la riga (W9-W13), per W8 dichiarare l'esenzione. Escluse due righe «Storie collegate» (`master-difetti-rilevati.md` riga 117, `llm-wiki-sicurezza.md` riga 47). Le pagine nuove e aggiornate dall'ingest `00c395f` non producono altri candidati (vedi §Pagine dell'ingest). Righe di tabella non valutate dallo script di audit (trattate come blocco, come nel run 2).
- **W15** [contradiction] testo del corpo superato da un'osservazione successiva, non corretto. Tutti e tre sono gia' dichiarati nelle sezioni `## Contradictions` e il gap `llm-wiki-archivi-sommario-conteggi` e' aperto (`wiki/gaps.md`, 1 occorrenza dell'intestazione):
  1. `wiki/concepts/llm-wiki-archivi-persistenza.md` riga 13: «17 archivi per progetto in `.llm-wiki/` più lo store `app-state.json`; una sola versione di formato è dichiarata in modo esplicito». La riga 127 (Contradictions) segnala che l'inventario ha 17 righe con lo store compreso (cioe' 16 piu' lo store) e che compaiono altri campi `version`.
  2. `wiki/concepts/llm-wiki-versioni-e-migrazioni.md` riga 13 e `wiki/concepts/llm-wiki-schema-dati.md` riga 43: «solo due» versioni esplicite; le righe 77 e 87 dichiarano campi `version` anche in `file-snapshot.json`, `file-change-queue.json`, `ingest-progress`, `ingest-generation`. Nuovo rispetto al run 2 (le contraddizioni sono entrate con la fetta B).
  3. `wiki/concepts/llm-wiki-archivi-persistenza.md` riga 28: «RS non lo legge» per `project.json`; la riga 93 e la riga 125 dicono che il Rust lo legge (`lib.rs:436-448`, `api_server.rs:877-884`). La pagina e' internamente incoerente.

  Fix: aggiornare i tre testi nel corpo a cura di wiki-keeper, dopo la decisione dell'utente sul criterio di conteggio (TSK-010, `llm-wiki-archivi-sommario-conteggi`). Mai heal-eligible.

## INFO

Da script (invariati): **4au.5** `management/kanban/sprint.md` 1 riga con ultima colonna non-stato (riga di epica EP-002, non un difetto); **4g code-path-overlap** TSK-006, TSK-007, TSK-008, TSK-009 condividono `wiki/**`, lo scheduler li serializza; **4g dependencies-drift-candidate** TSK-005 (solo frontmatter: TSK-003, TSK-004), scartato come nel run 2 perche' la riga del corpo li elenca in forma non puntata (giudizio del run 2, non rilettura).

A lettura:

- **I5** [log] `wiki/log.md` ha un blocco in stile frontmatter `type: session-close` a meta' file; non viola 4bb, 4bf, 4bg. Append-only: nessuna correzione. Invariato.
- **I6** [tsk-testo] `management/kanban/EP-003-schemi-attuali-layer-persistenza/US-019-indice-db-schemas-e-relazioni/TSK-010.md` righe 34 e 41: «i 17 archivi più lo store» (la riga 60 dichiara la discrepanza D1: 16 piu' lo store). Invariato; da allineare a cura del product-manager.
- **I8** [submodule] (nuovo) `git submodule status` → `-e08cfce65aad8b76b13546a081c1a8d4422b70c3 code_repos/llm_wiki`: il prefisso `-` indica submodule non inizializzato, il gitlink e' invariato (`e08cfce`). Il run 2 leggeva ` e08cfce...`. Il run 3 non ha verificato altro (non si entra nel submodule). Se la factory deve lavorare sul codice, inizializzarlo con il flusso di vcs-handoff.
- **I9** [contradictions-conteggio] (nuovo) le sezioni `## Contradictions` sono in **8** pagine (grep `^## Contradictions`: `gestione-file-corrotti` riga 61, `rischi-persistenza` 82, `operazioni-distruttive` 115, `schema-dati` 85, `versioni-e-migrazioni` 76, `sicurezza` 73, `api-locale` 58, `archivi-persistenza` 124), non 9, e contano 20 voci (2+2+4+2+3+1+1+5). Il log dell'ingest dichiara «25 segnalate dai worker, 18 distinte su 8 pagine»: 8 pagine coincide, 18 contro 20 no. Non e' un finding di integrita'; le due cifre vanno allineate se servono come metrica. Nessuna pagina ha un titolo «Contradictions» fuori da queste 8 (grep case-insensitive sulle intestazioni).

## Pagine dell'ingest persistenza B e C (commit `00c395f`)

Copertura esplicita: 5 create e 10 aggiornate (`git show --stat`: 18 file, 636 inserzioni, 10 cancellazioni; il log dichiara «Pagine create: 5, Aggiornamenti: 10»).

| Gruppo | Pagine | Esito |
|---|---|---|
| Create (3 source) | `wiki/sources/2026-11-20-repo-llm_wiki-persistenza-a.md`, `-b.md`, `-c.md` | frontmatter completo, `status: draft`, `created`/`updated: 2026-11-20`; nell'index (righe aggiunte da `00c395f`) |
| Create (2 concept) | `llm-wiki-sincronizzazione-file`, `llm-wiki-cancellazione-pagine-e-sorgenti` | frontmatter completo, nell'index, nessun wikilink rotto, nessun candidato Check 2 |
| Aggiornate (9 concept) | `llm-wiki-agente`, `-api-locale`, `-archivi-persistenza`, `-gestione-file-corrotti`, `-operazioni-distruttive`, `-rischi-persistenza`, `-schema-dati`, `-sicurezza`, `-versioni-e-migrazioni` | frontmatter completo; W13 e W15 sono le sole osservazioni; 0 broken-link |
| Aggiornata (1 source) | `wiki/sources/2026-11-20-repo-llm_wiki.md` | W14 del run 2 risolto |

Verifiche a comando: 0 orphan (script); 0 broken-link su 347 wikilink; contatore Sources dell'index coerente (4bf-4bg OK); `wiki/gaps.md` e `wiki/log.md` solo aggiunte (4bb, 4bd OK); 5 slug di gap citati dalle `## Contradictions` (`llm-wiki-vector-v1-chiamanti`, `llm-wiki-creazione-cartella-dati`, `llm-wiki-mcp-readme-vs-codice`, `llm-wiki-persistenza-codice-non-letto`, `llm-wiki-archivi-sommario-conteggi`) trovati ciascuno come intestazione in `wiki/gaps.md` (221 righe, letto per intero con `wc -l` e `grep`).

### Sezioni `## Contradictions` (8 pagine, 20 voci)

Ogni voce ha la forma «Prima / Ora» e almeno una `[^src: raw/...persistenza-{a,b,c}.md §...]`; tutte le 20 citazioni risolvono path e sezione (audit sotto). Il testo preesistente non e' stato toccato (coerente con il log dell'ingest e con TSK-005 §Metodo: «le uniche righe rimosse sono le 10 righe `sources:`»; confermato dalle 10 cancellazioni di `git show --stat`). Conseguenza: il corpo contiene ancora le affermazioni superate (W15). Le voci che segnalano solo estensione o precisazione e non smentita: `gestione-file-corrotti` righe 62-63, `rischi-persistenza` 83-84 (esito dei rischi invariato), `sicurezza` 74, `api-locale` 59, `archivi-persistenza` 126 e 128, `operazioni-distruttive` 118. Le contraddizioni dirette sono quelle di W15.

## Verifiche su kanban e config (a comando)

| Verifica | Valore letto | Esito |
|---|---|---|
| 4be date di lavoro | TSK-001..005 e TSK-010 `done` con `started_at` e `closed_at: 2026-11-20`; TSK-006..009 `todo` senza date | script OK |
| Sprint view | `sprint.md`: «Totale TSK aperti: 4 (sprint corrente 3, lookahead 1)», TSK-006..009 | coerente con i `todo` letti |
| US-013 | `status: done`, 5 AC `[x]` | coerente con TSK-005 §Chiusura (AC3, AC4, AC5 `SI`, AC1-AC2 `n/a` con deroga) |
| 4e manifest | 5 entry, `primary_artifact` tutti esistenti | OK |
| 4f | `factory.config.yaml` riga 147 `provider: none`; nessun `external_id:` atteso | OK |
| Repository del cliente | `git submodule status` → `-e08cfce65aad8b76b13546a081c1a8d4422b70c3 code_repos/llm_wiki` | gitlink invariato, vedi I8 |

## Check NON ESEGUITI o saltati

Invariati dal run 2 (la config non e' cambiata: `git status` pulito), salvo dove indicato.

| Check | Stato | Motivo |
|---|---|---|
| 4at | NON ESEGUITO | l'esecutore dichiarato e' un test pytest (`tests/test_fleet_contract.py`) e Bash e' limitato agli script di lint; non rieseguito ne' stimato |
| 4an | NON ESEGUIBILE | citato in un header senza sezione nel file |
| 4af, 4ak | saltati | `wiki_lint.semantic_check.enabled: false`, `content_share.enabled: false` |
| 4v, 4w, 4x, 4al | saltati | `complexity_budget` assente, `release_governance.enabled: false`, `CHANGELOG.md` assente (valori del run 2) |
| 4ad, 4ae, 4ap | saltati | `qa_layer.*` disattivati, `refactor_agent_skills` assente (valori del run 2) |
| FE quality, Compression, Oracle/analytics | saltati | flag `fe_correctness`, `compression`, `functional_oracle` a `false` (valori del run 2) |
| 4bh, 4bi, 4j | script, regola spenta | output dello script |
| 4m | no-op | nessun `risk_classification:` nel kanban, `management/risk-registry.md` non verificato di nuovo in questo run |

## heal-eligible

- **ERROR heal-eligible: 0.** `heal_eligible_count: 0`, `heal_eligible_categories: []`.
- **4ax (W3)**: lo script lo etichetta «heal-eligible» (fix meccanico `git config -f .gitmodules submodule.code_repos/llm_wiki.ignore dirty`) e nel frontmatter e' registrato come `script_heal_label: [4ax]`. Non e' contato in `heal_eligible_count` perche' `heal-protocol` (whitelist: broken-wikilink, missing-frontmatter-field, citation-section-mismatch; nessuna menzione di 4ax o submodule) non lo include e le regole dell'agente escludono i WARNING. Inoltre il difetto 11 vieta di modificare `.gitmodules` agli agenti. Il fix e' meccanico per forma ma richiede una decisione.
- W7 (frontmatter di `gaps.md`) non e' deducibile dal path: non heal-eligible.

## Citation audit (inline)

Metodo: script di sola lettura nello scratchpad di sessione (non nel repo). Estrae ogni `[^src: <path> §<sez>]` e `[^code: ...]` da `wiki/**` (escluso `lint/`), verifica l'esistenza del path e che `<sez>` corrisponda a un header del file citato (uguaglianza, prefisso o inclusione, senza distinzione di maiuscole).

| Misura | Run 2 | Run 3 |
|---|---|---|
| File wiki con citazioni | 21 | 27 |
| Citazioni totali | 211 | 427 |
| Malformate | 0 | 0 |
| Path inesistente | 0 | 0 |
| Sezione assente nel file citato | 0 | 0 |
| Wikilink interni totali | 197 | 347, tutti risolti |

Limiti dichiarati: verifica di forma (path e header), non di fedelta' del contenuto; il match per inclusione e' piu' permissivo dell'uguaglianza esatta del run 2; le citazioni `[^code: ...]` sono contate ma non verificate contro il submodule (non si entra in `code_repos/llm_wiki`).

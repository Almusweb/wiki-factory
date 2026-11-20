---
type: lint
date: 2026-11-20
run: 2
heal_eligible_count: 0
heal_eligible_categories: []
---
# Lint Report — 2026-11-20 (seconda esecuzione del giorno)

> **Seconda esecuzione del 2026-11-20.** Questo file sostituisce il report della prima esecuzione (committato, resta in `HEAD`). Il report precedente descriveva una factory con kanban vuoto e un solo commit: le sue sezioni «popolazione», i 2 ERROR `orphan-dev-agent` e il WARNING `missing-factory-lock` non valgono piu' (vedi §Risolti dalla prima esecuzione).

Factory `wiki-factory`, PATTERN v2.48, topologia `custom`. Esecutore: wiki-lint. Nessun auto-fix: solo report. `code_repos/llm_wiki` non e' stato letto ne' scritto (la sola interrogazione e' `git submodule status`, che non entra nel submodule).

Report deterministico completo (righe di dettaglio non trascritte): [2026-11-20-deterministic.md](2026-11-20-deterministic.md).

**Totale: 0 ERROR, 15 WARNING, 9 INFO.** Script: 0 ERROR, 5 WARNING, 2 INFO. Lettura: 0 ERROR, 10 WARNING, 7 INFO. `heal_eligible_count: 0`.

## Dichiarazione sul raw della fetta B

All'avvio `ls raw` mostrava `raw/2026-11-20-repo-llm_wiki.md` e `raw/2026-11-20-repo-llm_wiki-persistenza-a.md`. A meta' esecuzione, dopo il lancio degli script, `raw/2026-11-20-repo-llm_wiki-persistenza-b.md` e' comparso in `raw/` e la sua voce e' comparsa in `raw/.extraction-manifest.json` (chiave `2026-11-20-repo-llm_wiki-persistenza-b`, `source: repo`, `primary_artifact` esistente). **Ignorato come richiesto**: il file non e' stato letto, non e' stato contato e nessun finding lo riguarda. Gli script deterministici sono girati prima della sua comparsa; il check 4e e' stato valutato sul manifest letto prima (entry: `2026-11-20-repo-llm_wiki`, `...-persistenza-a`, sessione). Il manifest letto a fine esecuzione ha 4 entry, ma la sola verifica fatta sulla nuova e' l'esistenza del `primary_artifact`.

## Popolazione effettiva letta

| Fonte | Valore letto |
|---|---|
| Pagine wiki (`wiki/**`, esclusi `lint/`) | 24 file `.md`: 16 concept, 2 entity, 1 source, 2 in `sessions/`, `index.md`, `log.md`, `gaps.md` (`find wiki -name '*.md'`) |
| Check 1 (script) | `Check 1 completato su 21 file — 0 orphan rilevati, 0 broken-link rilevati` |
| Kanban | `[3] popolazione: 4 EP, 34 US, 10 TSK (aperti e chiusi, archivio incluso)`; `[4b] question lette: 1 aperte, 0 risolte` (le 4 chiuse sono nella sezione `[CHIUSE]`, lette a mano) |
| Git | `git ls-files`: 1046 file; ultimo commit `51956f0` (`git log --oneline`) |
| Lavoro non committato | 31 voci in `git status --short` all'avvio; piu' i file nuovi elencati sotto |

I check che leggono HEAD o i file tracciati (4bb, 4bd, 4bj, 4bn, 4aq) ora girano su una popolazione reale (1045 file per gitleaks, 1046 path per 4aq), a differenza della prima esecuzione. Non vedono pero' il lavoro non committato: vedi INFO I3.

## Riepilogo deterministico (script, `run-deterministic.py`)

Eseguito con `PYTHONUTF8=1 PYTHONIOENCODING=utf-8`; exit code del runner: 0. Totale script: 0 ERROR, 5 WARNING, 2 INFO.

| Check | Cosa | ERROR | WARNING | INFO | Exit |
|---|---|---|---|---|---|
| 1, 4, 4ag | Struttura wiki: orphan, broken-link, storie collegate, staleness | 0 | 0 | 0 | 0 |
| 3, 4as, 4b | Integrita' kanban, assignee, question | 0 | 1 | 0 | 0 |
| 4au | Roll-up di stato TSK, US, epica e sprint.md | 0 | 1 | 1 | 0 |
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
| 4bk | Agenti lettori di contenuto non fidato con Bash | 0 | 0 | 0 | 0 |
| 4g | depends_on e scheduler | 0 | 0 | 1 | 0 |
| 4ai | Integrita' del layer agenti | 0 | 2 | 0 | 0 |
| 4aj, 4bm | `model:` degli agenti contro il registro | 0 | 0 | 0 | 0 |
| 4bn | Marcatori di conflitto su HEAD | 0 | 0 | 0 | 0 |
| 4bo | Lettori diretti del registro sessioni | 0 | 0 | 0 | 0 |
| 4j | Repository risolvibile sui TSK (regola spenta) | 0 | 0 | 0 | 0 |
| **Totale** | | **0** | **5** | **2** | 0 |

## Riepilogo check a lettura

| Check | Errors | Warnings | Note |
|---|---|---|---|
| 1 — Orphan + wikilink | 0 | 0 | script; verifica indipendente: 197 wikilink in 23 file, 0 rotti |
| 2 — Claim senza fonte | 0 | 7 | euristica a riga, soglia 20 parole, finestra 3 righe; log e gaps esclusi; vedi WARNING W6-W12 |
| Citation audit | 0 | 0 | 211 citazioni `[^src: ...]` in `wiki/**`: 0 malformate, 0 path inesistenti, 0 sezioni assenti (inline) |
| 3 — Integrita' kanban | 0 | 0 | script (la riga `[WARNING]` di 4b e' sotto) |
| 4 — Coerenza wiki↔kanban | 0 | 0 | script, 20 sezioni «Storie collegate» |
| 4b — Coerenza Q↔kanban | 0 | 1 | script, US-018 / Q_004; Q_005 chiusa senza residui in `blocked_by` o `pending_clarification` (grep su `management/kanban`) |
| 4c — Topology/routing | 0 | 1 | `dev-agents-without-code-path`; i 2 ERROR della prima esecuzione sono risolti |
| 4d — Coerenza VCS | 0 | 0 | `commit_coupling: float` (riga 83): `.factory-lock` non richiesto |
| 4e — Manifest↔raw | 0 | 0 | vedi §Dichiarazione sul raw della fetta B; entry lette prima: primary e secondary esistenti, nessun `raw/*.txt` o `*.kb.json` orfano |
| 4f — Publisher | 0 | 0 | `kanban_publish.provider: none`; nessun `external_id:` nel kanban (`grep -rln "^external_id:"` senza risultati) |
| 4g — Scheduler/depends_on | 0 | 0 | script; il candidato `dependencies-drift` e' giudicato e scartato (INFO sotto) |
| 4ah — Branch Awareness config | 0 | 0 | vedi sotto |
| 4ai — Agent infrastructure | 0 | 2 | script |
| 4ak — content_share | — | — | skip, `content_share.enabled: false` (riga 395) |
| 4am — Versioni | 0 | 0 | script, `SSOT factory.config.yaml#pattern_version = 2.48` |
| 4at — Disciplina d'ingresso | — | — | NON ESEGUITO |
| 4ag — Staleness | — | 0 | script, 20 file, 0 MISSING-DATE, 0 STALE |
| Struttura frontmatter wiki | 0 | 1 | `wiki/gaps.md` |

## ERROR meccanici (heal-eligible)

Nessuno. `heal_eligible_count: 0`.

## ERROR non meccanici

Nessuno.

## WARNING (igiene, mai heal-eligible)

I findings sono raggruppati per origine, come richiesto. Ogni WARNING ha un identificativo W per i rimandi.

### 1. Introdotti dal lavoro di oggi (file elencati nel mandato)

Nessun WARNING di struttura o di citazione dipende dai file nuovi o modificati oggi. Verifiche fatte (a comando, vedi §Verifiche sul lavoro di oggi): nessuna citazione rotta in `design_&_architecture/**`, `management/**` e `deliverables/`; nessun wikilink rotto; `wiki/gaps.md` cresce solo in coda; i 39 marcatori «non verificato» dell'indice `db_schemas` puntano a 10 gap esistenti. Il solo WARNING nato dal lavoro di oggi e' W2 (US-012), che e' anche atteso e si legge nella sezione 3.

Osservazioni a severita' INFO dello stesso gruppo: I3, I4, I6, I7 (sezione INFO).

### 2. Preesistenti (nel commit `51956f0` o precedenti)

- **W3** [WARNING][submodule-ignore-missing][4ax] `.gitmodules` (sezione `[submodule "code_repos/llm_wiki"]`: `path`, `url`, `branch`, nessun `ignore`). Valore letto dallo script: `submodule "code_repos/llm_wiki" con nessun ignore: ogni git status sul padre apre un processo dentro questo submodule`. Fix suggerito dallo script: `git config -f .gitmodules submodule.code_repos/llm_wiki.ignore dirty`. **Non applicare senza decidere prima il difetto 11**: `wiki/concepts/master-difetti-rilevati.md` riga 92-93 riporta che questo fix modifica `.gitmodules` mentre PATTERN-integration lo vieta agli agenti fuori da vcs-handoff (stato «dichiarato nel raw; non verificato dal keeper»); tracciato in US-011. Lo script etichetta il finding «heal-eligible»: per il contratto del wiki-lint un WARNING non lo e' mai.
- **W4** [WARNING][agent-command-missing][4ai.3] `.claude/agents/fleet-doctor.md` (script: «referenzia comando /factory-upgrade ma .claude/commands/factory-upgrade.md non esiste»). Fix: aggiungere il comando o correggere il nome nell'agente. Tracciato in US-006 (difetto 6).
- **W5** [WARNING][agent-command-missing][4ai.3] `.claude/agents/release-manager.md` (script: «referenzia comando /release ma .claude/commands/release.md non esiste»). Stesso fix e stessa storia (US-006).
- **W6** [WARNING][dev-agents-without-code-path][4c] `factory.config.yaml` riga 62 `code_path: ""`, riga 50 `topology: custom`, righe 104-109 `routing:` con `be`, `fe`, `db`, `qa`, `docs` a `agent`. La lettera della regola (`lint-checks-config.md` righe 29-30) da' WARNING; `code_paths` (riga 72 in poi) e' valorizzato con la entry `llm_wiki`, quindi e' un falso positivo semantico di una regola che non conosce il multi-repo. Fix: nessuna modifica alla config; decisione di chi mantiene il check. Tracciato in US-010 (difetto 10).
- **W7** [WARNING][missing-frontmatter-field][struttura wiki] `wiki/gaps.md` righe 1-7: letti `type: gap`, `status: draft`, `created`, `updated`, `append_only: true`; mancano `sources` e `tags` del frontmatter minimo di `scrivi-wiki-page` (righe 21-29: `type`, `sources`, `status`, `created`, `updated`, `tags`). Tutte le altre 23 pagine wiki hanno i campi (scansione a comando). Non deducibile dal path, quindi non heal-eligible. Fix: decidere se `gaps.md` e' esente e dichiararlo nella skill, oppure aggiungere `sources: []` e `tags: [gaps]` (modifica a carico di wiki-keeper; il file e' append-only). Tracciato in US-005 (difetto 5, decisione 9 dichiarata: «falso positivo»).
- **W8-W14** [WARNING][unsourced-claim][Check 2] sette righe di prosa con almeno 20 parole senza `[^src: ...]` o wikilink entro 3 righe (finestra [riga, riga+3]; una tabella conta come un blocco unico). Le pagine sono tutte nel commit `b8459d6` o precedente (nessuna e' modificata oggi: `git status` non le elenca). Il controllo e' euristico a livello di riga:

  | ID | File e riga | Parole | Citazione piu' vicina | Lettura |
  |---|---|---|---|---|
  | W8 | `wiki/concepts/master-difetti-rilevati.md` riga 18 («Come leggere lo stato di verifica») | 94 | riga 27 (+9) | testo di metodo sulle etichette della pagina, non un fatto della fonte; candidato a esenzione |
  | W9 | stesso file, riga 37 (difetto 3, Sintomo) | oltre 20 | riga 41 (+4) | citazione a fine blocco, una riga oltre la finestra |
  | W10 | stesso file, riga 65 (difetto 7, Sintomo) | oltre 20 | riga 69 (+4) | idem |
  | W11 | stesso file, riga 79 (difetto 9, Sintomo) | oltre 20 | riga 83 (+4) | idem |
  | W12 | stesso file, riga 93 (difetto 11, Sintomo) | oltre 20 | riga 97 (+4) | idem |
  | W13 | `wiki/concepts/llm-wiki-archivi-persistenza.md` riga 49 (voce «Configurazione LLM» dell'elenco di `app-state.json`) | 27 | riga 45 (-4, introduce l'elenco) e riga 54 (+5) | l'elenco e' coperto dalla citazione dell'introduzione, non entro la finestra in avanti |
  | W14 | `wiki/sources/2026-11-20-repo-llm_wiki.md` riga 78 («Correzione di percorso», ultima riga del file) | 26 | nessuna | affermazione sul percorso corretto di `fs.rs` senza citazione |

  Fix suggerito: spostare la citazione a fine blocco subito dopo la riga (W9-W13) o aggiungere `[^src: raw/2026-11-20-repo-llm_wiki.md §<sezione>]` a W14; per W8 dichiarare l'esenzione. Le righe «Storie collegate» (`llm-wiki-sicurezza.md` riga 47, `master-difetti-rilevati.md` riga 117) sono escluse: sezione gestita dal product-manager.
- **W15** [WARNING][contradiction][wiki, non codificato in `lint-checks`] `wiki/concepts/llm-wiki-archivi-persistenza.md` riga 13: «17 archivi per progetto in `.llm-wiki/` più lo store `app-state.json`; una sola versione di formato è dichiarata in modo esplicito». Letto a comando: la tabella `### Inventario` ha 19 righe di tabella meno intestazione e separatore, cioe' 17 righe di dati, di cui l'ultima e' `app-state.json`: 16 archivi per progetto piu' lo store. Per le versioni, `wiki/concepts/llm-wiki-versioni-e-migrazioni.md` riga 13 e `wiki/concepts/llm-wiki-schema-dati.md` riga 43 dicono «solo due» (`version: 1` in `scheduled-import-db.json` e il suffisso `_v2` di LanceDB). La pagina e' preesistente; la contraddizione e' emersa oggi ed e' gia' aperta come gap `llm-wiki-archivi-sommario-conteggi` (`wiki/gaps.md` riga 145, verificato: la sezione `### Inventario degli archivi` esiste nel raw alla riga 244). Fix: correggere il sommario riga 13, a carico di wiki-keeper, dopo la decisione dell'utente sul criterio di conteggio gia' registrata in TSK-010.

### 3. Attesi per lavoro non ancora fatto

- **W1** [WARNING][orphan-pending-clarification][4b] `management/kanban/EP-002-conoscenza-layer-di-persistenza/US-018-dimensioni-e-crescita-archivi/US-018.md` (script: «US-018: orphan-pending-clarification — Q_004 non citata nel pending_clarification di alcun ADR»). Valore letto: `pending_clarification: [Q_004]` (riga 9) e `management/questions.md` `### Q_004` in `[APERTE]`, `Bloccante: soft`. Motivo dell'attesa: Q_004 e' aperta, soft, e US-018 e' una storia di conoscenza di EP-002 senza ADR. Si risolve quando l'utente risponde a Q_004; non richiede un ADR. Non e' un difetto da correggere.
- **W2** [WARNING][status-rollup][4au.1] `management/kanban/EP-001-difetti-master-analisi-e-segnalazione/US-012-convenzioni-segnalazione-master/US-012.md` (script: «US status=in_progress — tutti i 1 TSK sono terminali»). Valori letti: US-012 `status: in_progress`, `started_at: 2026-11-20`; TSK-001 `status: done`. Origine: il lavoro di oggi (chiusura di TSK-001 e roll-up di US-012 del 18:41). Motivo dell'attesa: nel `git diff` di US-012 AC1-AC6 sono `[x]` e AC7 e' `[ ]` con la nota «derogato a livello di TSK (TSK-001 §Chiusura, AC7, deroga autorizzata dall'utente il 2026-11-20); si verifica con i TSK dello sprint 02». Nel kanban non esiste alcun TSK per US-001..US-011 (`find` su `TSK-*.md`: 10 file, tutti TSK-001..TSK-010), quindi la storia resta `in_progress` finche' i TSK dello sprint 02 non applicano il modello. Fix: nessuno ora; `in_progress` e' la derivazione corretta dalla tabella AC (protocollo di chiusura).
- Il WARNING W15 e' anch'esso in attesa di lavoro (correzione del sommario da parte di wiki-keeper, gap aperto); il suo testo sta nella sezione 2 perche' la pagina e' preesistente.

## INFO

Da script (testo invariato):

- [INFO][status-rollup][4au.5] `management/kanban/sprint.md`: «1 righe con ultima colonna che non e' uno stato, non confrontate (es. EP-002)»; `[4au.5] sprint.md: 8 righe lette (forma rilevata: EP-level=1, TSK-level=7 — status in ultima colonna)`. La riga di epica ha come ultima colonna un contatore e non uno stato: non e' un difetto. Lo `sprint.md` e' modificato rispetto a `HEAD` (3 inserzioni, 18 cancellazioni) e le sue 7 righe TSK corrispondono ai TSK aperti letti dal frontmatter (TSK-003..TSK-009).
- [INFO][dependencies-drift-candidate][4g] TSK-005: «`## Dependencies` e `depends_on` differiscono (solo corpo: -; solo frontmatter: TSK-003, TSK-004)». **Giudicato e scartato**: la sezione `## Dependencies` di TSK-005 contiene la riga «TSK-002, TSK-003, TSK-004 — le tre estrazioni da ingerire», cioe' gli stessi tre ID di `depends_on: [TSK-002, TSK-003, TSK-004]`. Lo script ha letto solo il primo ID di una riga non in forma di elenco puntato. Non e' un WARNING `dependencies-drift`.

A lettura:

- **I1** [INFO][raw-non-ingerito] `raw/2026-11-20-repo-llm_wiki-persistenza-a.md` (22.075 byte, `wc -c`) e' nel manifest (`2026-11-20-repo-llm_wiki-persistenza-a`, `files_sampled: 63`, `status: partial`) ma nessuna pagina wiki lo cita (la citation audit non trova `[^src: raw/...persistenza-a...]` in `wiki/**`). **Atteso**: l'ingest e' TSK-005 (`status: todo`, dipende da TSK-002, TSK-003, TSK-004); TSK-003 e' `in_progress`. Non e' un orphan di struttura wiki.
- **I2** [INFO][raw-fetta-b] Vedi §Dichiarazione sul raw della fetta B: `persistenza-b` comparso a meta' esecuzione, ignorato. TSK-003 e' `in_progress` con `closed_at:` vuoto, coerente.
- **I3** [INFO][popolazione-untracked] 4bj (`gitleaks: nessun finding su 1045 file`), 4aq, 4bb, 4bd e 4bn leggono file tracciati o HEAD. Non coprono i file non committati: `raw/2026-11-20-repo-llm_wiki-persistenza-a.md`, `design_&_architecture/db_schemas/README.md`, `design_&_architecture/decisions/ADR-EP003-001-formato-db-schemas.md`, `deliverables/modello-report-segnalazione-master.md` (`git status --short`: `??`). 4bd esamina «1 commit di wiki/gaps.md»: l'append-only delle 3 nuove voci di `gaps.md` e' stato verificato a mano con `git diff -- wiki/gaps.md` (18 inserzioni, 0 cancellazioni; vedi §Verifiche). Rilanciare 4bj e 4aq dopo il commit. Il TSK-002 dichiara un gitleaks sul raw con esito `no leaks found` (non rieseguito qui).
- **I4** [INFO][session-lock] `.session-close.lock/` esiste alla radice, non tracciato (`ls -la`: contiene `lock.json`, 122 byte, data 18:06). Non e' in `.gitignore` secondo `git status` (compare come `??`). Non incide su nessun check; lo si riporta perche' comparira' in un `git add -A`. Inoltre `active_sessions.py gc` al preflight ha rimosso il claim `3649aa67` (session-sync, `domain=raw/sessions`, «TTL scaduto»): comportamento previsto dal comando, non una modifica ai dati della factory.
- **I5** [INFO][log] `wiki/log.md` contiene a meta' file un blocco in stile frontmatter (`date`, `type: session-close`, `session_label`, `operator`, `outcome`, `artifact`, `context`, tra due righe `---`) prima dell'ultima entry di ingest. Non viola 4bb, 4bf o 4bg (script puliti) ma non e' una entry nel formato `## [data] operazione | titolo`. Il log e' append-only: nessuna correzione proposta.
- **I6** [INFO][tsk-testo] `management/kanban/EP-003-schemi-attuali-layer-persistenza/US-019-indice-db-schemas-e-relazioni/TSK-010.md` righe 34 e 41 dicono ancora «i 17 archivi piu' lo store» e «un indice dei 17 archivi e dello store» (la casella e' `[x]`), mentre l'indice ha 17 righe A01-A17 che includono lo store (16 per progetto piu' lo store). La riga 60 dichiara la discrepanza D1 e dice che l'allineamento di EP-003, US-019 e della DoD e' del product-manager «in un passaggio successivo»; US-019 ed EP-003 risultano gia' allineati (voci di storia delle 18:41). Resta da allineare solo il testo di TSK-010.
- **I7** [INFO][closure] `management/kanban/EP-002-conoscenza-layer-di-persistenza/US-013-estrazione-mirata-persistenza/TSK-002.md` §Chiusura: AC1 e' `SI` per la sola fetta A (la riga stessa dice «l'AC della storia si completa con quei TSK») e AC5 e' `n/a` perche' di TSK-005, senza la parola «deroga» che TSK-001 usa per AC7. Coerente col perimetro dichiarato e con US-013 `in_progress`; la lettura non e' un finding del protocollo di chiusura, ma chi ricalcola `done` di US-013 deve contare AC1 solo quando TSK-003 e TSK-004 sono chiusi.

## Verifiche sul lavoro di oggi (a comando, non a memoria)

| Verifica | Comando o lettura | Esito |
|---|---|---|
| Indice `db_schemas`: righe archivi | `grep -c '^| A[0-9][0-9] '` su `README.md` | 17 (A01-A17), come in TSK-010 AC1 |
| Righe fuori inventario, identificatori, relazioni | stessa forma con `X`, `I`, `R` | 6, 11, 13, come in TSK-010 AC1 e AC3 |
| Marcatori «non verificato» | regex di ADR-EP003-001 §D, `grep -o` | 39, come in TSK-010 AC4; ogni occorrenza di `**non verificato**` e' seguita da `[gap: ...]` |
| Slug dei gap nei marcatori | confronto con le intestazioni `## ... — <slug>` di `wiki/gaps.md` | 10 slug, 10 trovati, 0 mancanti |
| Stato derivato delle righe A | conteggio per riga dei marcatori contro la colonna Stato | 10 `documentato`, 7 `parziale` (incl. 3 con riserva nel testo), coerente con TSK-010 |
| Citazioni dell'indice | `[[`, `[^src: wiki/` | 0 e 0 (ADR §F); le 45 citazioni risolvono path e sezione |
| Citation audit `design_&_architecture/**` | script nello scratchpad di sessione | 47 citazioni, 45 ok; 2 «problemi» sono i pattern di esempio dentro `ADR-EP003-001` (`US-*/US-*.md §<sezione>` e `wiki/...`), non citazioni reali |
| Citation audit `management/kanban/**` e `management/questions.md` | idem | 162 citazioni, 161 ok; 1 «problema» e' il segnaposto `raw/... §...` nel testo di TSK-005 riga 28, non una citazione |
| Raw fetta A | `wc -c`, intestazione, §«Identità e perimetro» | 22.075 byte come dichiarato da TSK-002; «File letti in questa fetta: 23 (18 interi, 5 a finestra)», «Cumulativo dichiarato nel manifest: 63», uguale a `files_sampled: 63` |
| Manifest | `json.load` + esistenza dei `primary_artifact` | JSON valido; `primary_artifact` esistenti |
| `wiki/gaps.md` append-only (working tree) | `git diff --stat` e lettura del diff | solo righe aggiunte in coda (3 gap, `2026-11-20 18:23`: `llm-wiki-archivi-sommario-conteggi`, `llm-wiki-id-chat-sessione`, `llm-wiki-riferimenti-incrociati`); 4bc: «25 gap, nessuna chiusura non verificata» |
| Q_005 chiusa | `grep -rn "Q_005" management/kanban` | solo voci di storia del 17:53 e del 18:41; nessuna in `blocked_by` o `pending_clarification` |
| Q_004 aperta | `management/questions.md` `[APERTE]` | Q_004, `Bloccante: soft`, EP-002/US-018; riga `[^src: wiki/gaps.md §2026-11-20 17:06 — llm-wiki-archivi-dimensioni]` risolta dall'audit |
| Date di lavoro (4be) | script, `kanban_dates.required_from: "2026-11-20"` (config riga 398) | TSK-001, TSK-002, TSK-010 `done` con `started_at` e `closed_at` del 2026-11-20; TSK-003 `in_progress` con `started_at`; «nessun TSK con date mancanti» |
| Deliverable senza dettagli esclusi | `grep -i -E "llm[_-]wiki\|wiki-factory\|musio\|local_git\|e08cfce\|almusweb"` su `deliverables/modello-report-segnalazione-master.md` | 0 occorrenze. Non e' la verifica con la lista di valori di TSK-001 (non letta), solo un controllo su forme generiche |
| Repository del cliente | `git submodule status` | ` e08cfce65aad8b76b13546a081c1a8d4422b70c3 code_repos/llm_wiki (heads/develop)`: nessun prefisso `+` ne' `-`, gitlink invariato e inizializzato |

## Risolti dalla prima esecuzione (valore letto ora)

| Finding della prima esecuzione | Stato ora | Valore letto |
|---|---|---|
| ERROR `orphan-dev-agent` per `db-dev.md` (4c) | risolto | `factory.config.yaml` riga 106 `  db: agent` |
| ERROR `orphan-dev-agent` per `docs-dev.md` (4c) | risolto | riga 109 `  docs: agent`; `ls .claude/agents/*-dev.md`: be, db, docs, fe, qa; i layer `be`, `fe`, `db`, `qa`, `docs` hanno routing `agent`, `infra` e' `human` |
| WARNING `missing-factory-lock` (4d) | non applicabile | riga 83 `      commit_coupling: float`; `.factory-lock` assente e non richiesto |
| 3 WARNING `ingest-tools` (4bk) | risolti | `[4bk] OK — nessun lettore di contenuto non fidato con Bash fuori da eccezioni valide`; righe 409-411 di `factory.config.yaml` dichiarano le eccezioni `figma-sync`, `graphify-sync`, `session-sync`, `scade: "2027-05-16"` |
| Popolazione kanban vuota, 3 file tracciati, HEAD con il solo `README.md` | superata | 4 EP, 34 US, 10 TSK; 1046 file tracciati |

## Check NON ESEGUITI o saltati

| Check | Stato | Motivo |
|---|---|---|
| 4at — disciplina d'ingresso capability | NON ESEGUITO | l'esecutore dichiarato e' `pytest tests/test_fleet_contract.py -k asse4`: `ls tests` → `No such file or directory`, e Bash e' limitato agli script di `tools/lint/` e `tools/kanban/`. La lettura parziale della prima esecuzione non e' stata riportata: la config ha ora un blocco «OPT-IN ATTIVATE IL 2026-11-20» e piu' chiavi con `enabled: true`, quindi il bucket di ingresso e' cambiato. Il verdetto va chiesto al test |
| 4an | NON ESEGUIBILE | citato nell'header di `lint-checks-wiki-structure.md` senza sezione nel file: nessuna specifica da applicare |
| 4af | saltato | `wiki_lint.semantic_check.enabled: false` (riga 355) |
| 4ak | saltato | `content_share.enabled: false` (riga 395) |
| 4ah | eseguito, 0 finding | `code_paths[0].vcs.branch_awareness` righe 84-89: `enabled: true`, `preflight: true`, `dispatch_gate: warn`, `auto_align: propose`, `drift_check: true`, tutti nei valori ammessi; `vcs.mode: submodule`; top-level `vcs.branch_awareness.enabled: false` (riga 68) senza sotto-flag; `.factory-branches.yaml` assente (esiste solo `.factory-branches.yaml.example`) |
| 4v, 4w, 4x | saltati | `complexity_budget` assente; `release_governance.enabled: false` (riga 288) |
| 4al | saltato | `CHANGELOG.md` assente (`ls`: `No such file or directory`) |
| 4ad, 4ae | saltati | `qa_layer.failure_taxonomy.enabled: false`, `qa_layer.flakiness_detection.enabled: false` (righe 345, 347) |
| 4ap | saltato | `refactor_agent_skills` assente in config |
| FE quality (4n, 4o, 4p, 4ac, 4y, 4ao) | saltati | `fe_correctness.enabled: false` (riga 269), `a11y.enabled: false` (riga 278) |
| Compression (4s, 4u, 4aa, 4ab, 4ab-bis) | saltati | `compression.output.enabled: false`, `compression.context.enabled: false` |
| Oracle/analytics (4z, 4q, 4r) | saltati | `fe_correctness.functional_oracle.enabled: false` (riga 273), nessun task analytics nel kanban |
| 4bh, 4bi, 4j | script, regola spenta | `[4bh] regola spenta`, `[4bi] spento`, `[4j] regola spenta` |
| 4m | no-op | nessun `risk_classification:` nel kanban (`grep -rln` senza risultati), `management/risk-registry.md` assente |

Nota: la famiglia config (`lint-checks-config.md`) e' obbligatoria con `vcs.branch_awareness.enabled` vero in una entry di `code_paths` (riga 85): le condizioni di `lint-checks.md` sono soddisfatte, il modulo e' stato letto per intero.

## Citation audit (inline)

Metodo: script di sola lettura nello scratchpad di sessione (non nel repo) che estrae ogni `[^src: <path> §<sez>]` da `wiki/**` (esclusi `lint/`), verifica che il path esista e che `<sez>` coincida con un header markdown del file citato (uguaglianza o prefisso, senza distinzione di maiuscole).

| Misura | Valore |
|---|---|
| File wiki con citazioni | 21 |
| Citazioni totali | 211 |
| Malformate | 0 |
| Path inesistente | 0 |
| Sezione assente nel file citato | 0 |
| Wikilink interni (`[[...]]`) totali | 197, tutti risolti a uno slug esistente |

Limite dichiarato: verifica di forma (esistenza di path e header), non di fedelta' del contenuto citato. Check 2: ogni riga di prosa con almeno 20 parole (escluse intestazioni, frontmatter, blocchi di codice, commenti, `log.md` e `gaps.md`) cerca una citazione `[^src: ...]`, `[^code: ...]` o un wikilink nella riga o nelle 3 successive; le righe di tabella contano come blocco. Risultato: 9 candidati, 2 esclusi come «Storie collegate», 7 riportati (W8-W14). Il metodo non separa le frasi dentro una riga.

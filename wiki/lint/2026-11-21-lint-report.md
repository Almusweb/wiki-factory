---
type: lint
date: 2026-11-21
run: 1
heal_eligible_count: 0
heal_eligible_categories: []
script_heal_label: [4ax]
---
# Lint Report — 2026-11-21 (prima esecuzione del giorno)

Factory `wiki-factory`, PATTERN v2.48, topologia `custom`. Esecutore: wiki-lint. Solo report, nessun auto-fix. `code_repos/llm_wiki` non e' stato letto ne' scritto: l'unica interrogazione e' `git submodule status`. Commit di riferimento: `c28db3b` (ingest del 2026-11-21); working tree a inizio run: pulito.

Report deterministico completo (righe di dettaglio non trascritte): [2026-11-21-deterministic.md](2026-11-21-deterministic.md).

**Totale: 0 ERROR, 18 WARNING, 10 INFO.** Script: 0 ERROR, 6 WARNING, 3 INFO. Lettura: 0 ERROR, 12 WARNING, 7 INFO. `heal_eligible_count: 0`.

Run 3 del 2026-11-20: 0 ERROR, 15 WARNING, 7 INFO.

## Risolti / nuovi / invariati (contro run 3 del 2026-11-20 e `2026-11-20-sweep-rescan.md`)

**Risolti**

| ID | Finding | Evidenza letta ora |
|---|---|---|
| W8-W13 | `unsourced-claim` (6 righe in `master-difetti-rilevati.md` 18/37/65/79/93 e `llm-wiki-archivi-persistenza.md` 49) | lo scan Check 2 non le segnala piu': citazione spostata in riga (sweep-rescan, Iterazione 2), ora in `HEAD` |
| W15 (parte) | riga `project.json` di `archivi-persistenza` (riga 28) | riga 28 ora: «RS lo legge ... (`lib.rs:436-448`, `api_server.rs:877-884`)», coerente con le righe 93 e 125. Restano 2 dei 3 testi superati (vedi W15) |
| I8 | submodule non inizializzato | `git submodule status` → ` e08cfce65aad8b76b13546a081c1a8d4422b70c3 code_repos/llm_wiki (heads/main)`: nessun prefisso `-`, gitlink invariato `e08cfce` |

**Nuovi** (W19-W25, I10-I12 e I14; tutti dall'ingest `c28db3b` o da verifiche non fatte nel run 3)

| ID | Finding |
|---|---|
| W19 | contraddizione tra pagine non dichiarata: chiamante UI di `import_project_archive` |
| W20-W22 | «segreti in chiaro» formulati come fatto (3 occorrenze) |
| W23-W24 | `sources:` di frontmatter incompleto su 2 pagine (cita un raw non elencato) |
| W25 | `updated:` non aggiornato su una source page toccata il 2026-11-21 |
| I10-I12, I14 | vedi §INFO |

**Invariati**: W1, W2, W3 (4ax), W4, W5, W6, W7, W16 (4bj gitleaks), W17, W18, I5, I6, I9 (cifre aggiornate, vedi §INFO), W15 (2 testi su 3). Script: gli stessi 6 WARNING e 3 INFO del run 3 (4b US-018 Q_004; 4au US-012; 4ax; 4ai x2; 4bj gitleaks).

## Popolazione effettiva letta

| Fonte | Valore letto |
|---|---|
| Pagine wiki (`wiki/**`, escluso `lint/`) | 36 file `.md` (29 al run 3, +7: 6 source page `2026-11-21-repo-llm_wiki-*` e `llm-wiki-pipeline-ingest`) |
| Check 1 (script) | `Check 1 completato su 33 file — 0 orphan rilevati, 0 broken-link rilevati` |
| Check 4 (script) | `Check 4 completato su 32 sezioni «Storie collegate»` |
| Check 4ag (script) | `23 file (oggi=2026-11-21) — 0 MISSING-DATE, 0 STALE, 0 INFO` |
| Kanban | `[3] popolazione: 4 EP, 34 US, 10 TSK`; `git diff --stat 74ff34f HEAD -- management factory.config.yaml .gitmodules` vuoto: kanban, config e `.gitmodules` non toccati dall'ingest |
| Gap | `[4bc] OK — 49 gap, nessuna chiusura non verificata` (35 al run 3, +14); `verify_gap_closures --check`: `aperti 37 | chiusi e verificati 12 | chiusi non verificati 0` |
| Citazioni | 774 `[^src|code:]` in `wiki/**` (run 3: 427); wikilink 655 |
| Git | `HEAD` = `c28db3b`; a inizio run nessun file modificato o non tracciato |

## Riepilogo deterministico (script, `run-deterministic.py`)

Tabella copiata dal file deterministico; exit code 0 per ogni check.

| Check | Cosa | ERROR | WARNING | INFO |
|---|---|---|---|---|
| 1, 4, 4ag | Struttura wiki | 0 | 0 | 0 |
| 3, 4as, 4b | Integrita' kanban, assignee, question | 0 | 1 | 0 |
| 4au | Roll-up di stato | 0 | 1 | 1 |
| 4am | Coerenza versioni | 0 | 0 | 0 |
| 4ar | SUNSET scadute | 0 | 0 | 0 |
| 4aq | Path portabili (1071 path) | 0 | 0 | 0 |
| 4ax | ignore = dirty sui submodule | 0 | 1 | 0 |
| 4bb | `wiki/log.md` append-only | 0 | 0 | 0 |
| 4bc | Chiusure dei gap verificate | 0 | 0 | 0 |
| 4bd | `wiki/gaps.md` append-only | 0 | 0 | 0 |
| 4be | Date di lavoro dei TSK | 0 | 0 | 0 |
| 4bf, 4bg | Ordine del log, contatore Sources | 0 | 0 | 0 |
| 4bh, 4bi, 4j | regole spente | 0 | 0 | 0 |
| 4bj | Segreti (gitleaks) | 0 | 1 | 0 |
| 4bl, 4bk | settings.json, agenti lettori | 0 | 0 | 0 |
| 4g | depends_on e scheduler | 0 | 0 | 2 |
| 4ai | Layer agenti | 0 | 2 | 0 |
| 4aj, 4bm, 4bn, 4bo | model, conflitti, lettori registro | 0 | 0 | 0 |
| **Totale** | | **0** | **6** | **3** |

## Riepilogo check a lettura

| Check | Errors | Warnings | Note |
|---|---|---|---|
| 1 — Orphan + wikilink | 0 | 0 | script; verifica indipendente: 655 wikilink, i 2 non risolti (`schema-dati` righe 105, 107) sono segnaposto dentro backtick (I11) |
| 2 — Claim senza fonte | 0 | 2 | W17, W18 (invariati); candidati in `log.md`/`gaps.md` in I10 |
| Citation audit | 0 | 0 | vedi §Citation audit |
| 3, 4 — Kanban e coerenza | 0 | 0 | script |
| 4b — Q↔kanban | 0 | 1 | W1 |
| 4c — Topology | 0 | 1 | W6 |
| 4d — VCS | 0 | 0 | `factory.config.yaml` riga 83: `commit_coupling: float` |
| 4e — Manifest↔raw | 0 | 0 | 11 entry, tutti i `primary_artifact` esistono (6 nuove: `2026-11-21-repo-llm_wiki-{api-mcp,agente-runtime,agente-tools,fs-lib-progetto,ingest,ricerca-ui-residui}`); `ls raw`: 10 `.md` piu' `images/` e `sessions/`, nessun orfano |
| 4f — Publisher | 0 | 0 | `factory.config.yaml` riga 147: `provider: none` |
| 4g, 4ai, 4am | 0 | 2 | script (4ai: W4, W5) |
| Frontmatter wiki | 0 | 1 | W7; gli altri 35 file hanno `id`/`type`/`title`/`status`/`created`/`updated`/`sources`/`tags`; nessun `id` duplicato |
| Contradictions | 0 | 1 | W15, W19; I9 |
| Ipotesi non testate | 0 | 3 | W20-W22 |
| Gap ↔ log ↔ pagine | 0 | 0 | coerente, vedi §Gap |

## ERROR meccanici (heal-eligible)

Nessuno. `heal_eligible_count: 0`.

## ERROR non meccanici

Nessuno.

## WARNING (igiene, mai heal-eligible)

### Da script (invariati)

- **W1** [4b] `management/kanban/EP-002-conoscenza-layer-di-persistenza/US-018-dimensioni-e-crescita-archivi/US-018.md` riga 9: `pending_clarification: [Q_004]`; Q_004 aperta in `management/questions.md`. Fix: nessuno, risponde l'utente a Q_004.
- **W2** [4au.1] `.../US-012-convenzioni-segnalazione-master/US-012.md` riga 6 `status: in_progress`, TSK-001 `status: done`. Fix: nessuno finche' AC7 non e' verificato.
- **W3** [4ax] `.gitmodules`, `submodule "code_repos/llm_wiki"`: nessun `ignore`. Fix suggerito dallo script: `git config -f .gitmodules submodule.code_repos/llm_wiki.ignore dirty`. Non conteggiato heal-eligible (vedi §heal-eligible); non applicare senza decidere il difetto 11 (`wiki/concepts/master-difetti-rilevati.md`).
- **W4** [4ai.3] `.claude/agents/fleet-doctor.md` referenzia `/factory-upgrade`, `.claude/commands/factory-upgrade.md` non esiste. Fix: aggiungere il comando o correggere il nome.
- **W5** [4ai.3] `.claude/agents/release-manager.md` referenzia `/release`, `.claude/commands/release.md` non esiste. Stesso fix.
- **W16** [4bj] script: «NON_VERIFICABILE: gitleaks assente (non nel PATH ne' nei percorsi noti)». Nessuna verifica dei segreti avvenuta. Fix: installare gitleaks e rilanciare `python3 tools/lint/check-secrets.py --root . --oggi 2026-11-21`. Le 6 nuove source page e i 6 raw del 2026-11-21 non hanno quindi una verifica di segreti da questo run.

### Da lettura, invariati

- **W6** [4c] `factory.config.yaml` riga 62 `code_path: ""`, riga 50 `topology: custom`; `code_paths:` valorizzato (riga 72). Falso positivo semantico.
- **W7** `wiki/gaps.md` righe 1-8: frontmatter con `type`, `status`, `created`, `updated`, `append_only`; mancano `sources` e `tags` (come nel run 3) e anche `title` (non citato nel run 3; il frontmatter non e' cambiato). Fix: a carico di wiki-keeper, file append-only; non deducibile dal path.
- **W15** [contradiction] due testi del corpo superati, dichiarati in `## Contradictions` e nel gap `llm-wiki-archivi-sommario-conteggi` (`wiki/gaps.md` riga 179, ancora aperto, nessun `**Risolto:**` per questo slug): (1) `llm-wiki-archivi-persistenza.md` riga 13 «17 archivi ... una sola versione di formato e' dichiarata»; (2) `llm-wiki-versioni-e-migrazioni.md` riga 13 e `llm-wiki-schema-dati.md` riga 43 «solo due» versioni esplicite. Il 2026-11-21 `versioni-e-migrazioni` e `schema-dati` sono stati aggiornati ma le due righe sono rimaste. Fix: wiki-keeper dopo la decisione utente sul criterio di conteggio (TSK-010).
- **W17** `wiki/concepts/master-difetti-rilevati.md` riga 128 (35 parole, nessuna citazione in 128-131): nota di metodo, come nello sweep-rescan. Invariato.
- **W18** `wiki/concepts/llm-wiki-archivi-persistenza.md` riga 127 (25 parole, nessuna citazione in 127-130): nota di metodo. Invariato. Fix per W17/W18: wikilink o `[^src]` nella riga, oppure esenzione di metodo dichiarata in `citation-rules`.

### Da lettura, nuovi (ingest `c28db3b`)

- **W19** [contradiction-non-dichiarata] `wiki/concepts/llm-wiki-operazioni-distruttive.md` riga 77: `import_project_archive` ha come chiamante UI `MaintenanceSection` (`:218-230`), «riportato dalla fetta A»; riga 89 ripete che non e' verificato cosa accada se l'id ripristinato coincide. Contro: `wiki/concepts/llm-wiki-rischi-persistenza.md` riga 86 «il chiamante UI dell'import non e' stato trovato in `src/`» e `wiki/gaps.md` riga 209 (stessa frase; raw `2026-11-21-repo-llm_wiki-fs-lib-progetto.md` riga 41: «nessun file `*archive*`/`*project-maintenance*` in `src/`»). Nessuna voce `## Contradictions` la dichiara (grep di `MaintenanceSection` e della frase in `wiki/**`). Fix: voce `## Contradictions` in `rischi-persistenza` e correzione della riga 86 e del gap `llm-wiki-import-id-duplicato` (a cura di wiki-keeper).
- **W20** [ipotesi-come-fatto] `wiki/concepts/llm-wiki-rischi-persistenza.md` riga 28: «i segreti in chiaro in `app-state.json`» (rischio 8, riga di cui `git blame` dice commit `b8459d65`, non toccata dall'ingest). La stessa pagina alla riga 106 dichiara la cosa «**Deduzione non testata**» (gap `llm-wiki-token-cifratura`). Fix: riformulare la riga 28 come deduzione.
- **W21** [ipotesi-come-fatto] `wiki/concepts/llm-wiki-sicurezza.md` riga 54: «**Segreti in chiaro nello store.** Tra i campi in chiaro compaiono `token` e `localToken`...» (commit `b8459d65`); la riga 100 della stessa pagina e' la versione corretta («Deduzione non testata ... probabile memorizzazione in chiaro»). Fix come W20.
- **W22** [ipotesi-come-fatto] `wiki/concepts/llm-wiki-archivi-persistenza.md` riga 60: «Tra i campi in chiaro compaiono `token` e `localToken` in `mineruConfig`» (commit `b8459d65`); la pagina non rimanda alla deduzione. Fix come W20, con rinvio a `llm-wiki-token-cifratura`.
- **W23** [sources-frontmatter] `wiki/concepts/llm-wiki-sicurezza.md` riga 8: `sources:` elenca 7 raw senza `raw/2026-11-21-repo-llm_wiki-ingest.md`, citato alla riga 110. Non heal-eligible: il campo esiste e la correzione richiede giudizio.
- **W24** [sources-frontmatter] `wiki/concepts/llm-wiki-operazioni-distruttive.md` riga 8: `sources:` senza `raw/2026-11-21-repo-llm_wiki-agente-tools.md`, citato alla riga 144.
- **W25** [updated-non-aggiornato] `wiki/sources/2026-11-20-repo-llm_wiki-persistenza-a.md` riga 7 `updated: 2026-11-20`; il file e' stato modificato dal commit di ingest del 2026-11-21 (sezione `## Aggiornamenti (v2026-11-21)`, +3 righe). 4ag non lo segnala (0 STALE). Fix: `updated: 2026-11-21`, a cura di wiki-keeper.

## INFO

Da script (invariati): **4au.5** `management/kanban/sprint.md` 1 riga con ultima colonna non-stato (EP-002); **4g code-path-overlap** TSK-006..009 su `wiki/**`; **4g dependencies-drift-candidate** TSK-005 (solo frontmatter: TSK-003, TSK-004).

A lettura:

- **I5** `wiki/log.md` riga 24 `type: session-close`: blocco in stile frontmatter a meta' file, non viola 4bb/4bf/4bg. Invariato.
- **I6** `.../US-019-indice-db-schemas-e-relazioni/TSK-010.md` righe 34 e 41: «17 archivi piu' lo store» (D1 dichiara 16 piu' lo store). Invariato; allineamento a cura del product-manager.
- **I9** [contradictions-conteggio] Le sezioni `## Contradictions` sono ora in **13 pagine** (8 al run 3) e contano **47 voci** (20 al run 3), contate con lo stesso metodo (righe `- ` di primo livello nella sezione). Il log dell'ingest dichiara «13 segnalate dai worker, 12 in `## Contradictions` (api-locale 2, sicurezza 2, mcp-server 1, agente 2, archivi-persistenza 2, schema-dati 1, llm-wiki-app 2)»: l'incremento letto e' +27 (api-locale +2, sicurezza +3, mcp-server +1, agente +3, archivi-persistenza +4, schema-dati +3, llm-wiki-app +3, rischi-persistenza +3, operazioni-distruttive +2, cancellazione-pagine-e-sorgenti +2, test-e-ci +1) e coinvolge 5 pagine nuove (agente, cancellazione-pagine-e-sorgenti, test-e-ci, llm-wiki-app, mcp-server). Non e' un difetto di integrita': le cifre del log vanno allineate se servono come metrica. **Nessuna voce preesistente e' stata cancellata**: per le 8 pagine che avevano la sezione a `74ff34f`, tutte le righe della sezione di `74ff34f` sono presenti in `HEAD` (confronto riga a riga con `git show 74ff34f:<file>`, 0 righe mancanti); le 10 cancellazioni di `git diff 74ff34f HEAD --numstat -- wiki` su 13 file sono righe `updated:`/`sources:` del frontmatter (letto con `git diff | grep '^-'`), piu' un'altra riga `updated:` in `index.md`.
- **I10** [check2-log-gaps] Lo scan con la stessa euristica trova candidati anche in file che il run 3 non elencava: `wiki/gaps.md` righe 177, 189, 197 (descrizioni di assenza `**Impatto:**`/`**Gap:**`) e `wiki/log.md` righe 41, 43, 52, 55, 56, 59, 60, 66, 67, 68. Sono registri operativi (append-only), non pagine di conoscenza: non conteggiati come WARNING. Non so se il run 3 li escludesse; lo dichiaro invece di assumerlo.
- **I11** [wikilink-in-codice] `wiki/concepts/llm-wiki-schema-dati.md` righe 105 e 107: `[[<percorso senza wiki/ e .md>]]` e `[[destinazione|etichetta]]` dentro backtick, descrizione del formato di llm-wiki. Il Check 1 script non li segnala; il mio scan indipendente li contava come non risolti: falso positivo.
- **I12** [citazione-manifest] `wiki/sources/2026-11-20-repo-llm_wiki-persistenza-a.md` riga 22 e `-b.md` riga 24 citano `raw/.extraction-manifest.json §<entry>.extraction_metadata.files_sampled`: il path esiste e le chiavi `2026-11-20-repo-llm_wiki-persistenza-{a,b}` e `files_sampled` esistono, ma `§` indica una chiave JSON e non un header Markdown. Preesistente (commit `00c395f`). Fuori dalla grammatica `.md §header`.
- **I14** [catena-cancellazione] La catena OPTIONS → `delete:` → `delete_file` e' marcata ipotesi in `rischi-persistenza` righe 109 e 116 («IPOTESI NON RIPRODOTTA»), `sicurezza` riga 110, `operazioni-distruttive` riga 116, source `2026-11-21-repo-llm_wiki-ingest` righe 13 e 31, `gaps.md` riga 273 e log. Nessuna pagina afferma la combinazione come fatto. `cancellazione-pagine-e-sorgenti` riga 78 e `operazioni-distruttive` riga 143 elencano i tre passaggi come letture di codice senza rimando all'ipotesi, e `sicurezza` riga 63 titola «Segreti in chiaro nello stesso file» (supportata dal commento di `proxy-config.ts`): non sono WARNING perche' non formulano la combinazione, ma un rimando a `rischi-persistenza` le renderebbe esplicite. Titoli di rischio 8 «segreti in chiaro» a `rischi-persistenza` righe 43, 67, 105 e `sicurezza` riga 48 (titoli di US, righe 105-106 gia' seguite dalla deduzione).

## Ipotesi: dove compaiono e come sono formulate

| Ipotesi | Occorrenze | Esito |
|---|---|---|
| Catena OPTIONS → `delete:` → `delete_file` | `rischi-persistenza` 109, 116; `sicurezza` 110; `operazioni-distruttive` 116; source `ingest` 13, 31; `gaps.md` 273 | tutte «ipotesi non riprodotta» (I14), nessun WARNING |
| Virgolette in `shell_command_tokens` | `sicurezza` 91 («**Ipotesi non testata** ... non e' un fatto confermato»); `rischi-persistenza` 110; `gaps.md` 315; source `agente-runtime` 39 | tutte ipotesi |
| Token in chiaro | `rischi-persistenza` 106; `sicurezza` 100, 101; `gaps.md` 345; source `fs-lib-progetto` 30, 41 («Possibile ... deduzioni non testate») | ipotesi; formulate come fatto: **W20, W21, W22** |
| Collisione id all'import | `rischi-persistenza` 86 («deduzione dal codice, non testata»); `operazioni-distruttive` 127 («[DEDUZIONE NON TESTATA]»), 144; `gaps.md` 209 | tutte deduzione; ma vedi W19 sul chiamante UI |
| Collisione `sanitize_session_id` | `archivi-persistenza` 157 («Inferenza non testata»); `gaps.md` 321; source `agente-runtime` 31, 39 | tutte inferenza |
| Saturazione del rate limit da LAN (nel log, non nella richiesta) | `sicurezza` 84 («Inferenza non testata») | ipotesi |

## Gap, log e pagine citate

- `wiki/gaps.md`: 49 intestazioni `## 2026-...` (35 + 14 nuove, 14 intestazioni `2026-11-21 07:31` alle righe 283-361). Chiusi: 12 righe `**Risolto:** 2026-11-21` (righe 27, 35, 43, 51, 59, 79, 87, 135, 151, 225, 257, 265) e 12 voci `gap-closed` in `wiki/log.md` (righe 72-83). Gli slug coincidono uno a uno: `contratto-api-http`, `api-lan-auth`, `mcp-readme-vs-codice`, `approvazione-shell`, `i18n-lingue`, `multimodale-stato`, `ci-test-build`, `creazione-cartella-dati`, `log-index-formato`, `embedding-trasporto`, `tipi-dedup-lint`, `markdown-estratto-percorsi`.
- Pagine citate: ogni voce di log nomina una pagina `via [[...]]`; il `**Risolto:**` corrispondente cita la stessa pagina (a volte con una seconda: `approvazione-shell` anche `llm-wiki-agente`, `api-lan-auth` anche `api-locale`, `multimodale-stato` anche `llm-wiki-pipeline-ingest`). Tutte le pagine esistono. `verify_gap_closures --check` e 4bc: 12 verificati, 0 non verificati; 4bd: nessuna riga tolta a `gaps.md` (`git diff 74ff34f HEAD -- wiki/gaps.md`: 0 righe `-`).
- Il log dichiara «Gap nuovi: 14 | Gap chiusi: 12»: coerente con le intestazioni lette.
- Il log dell'ingest riporta «Files touched: 23 (7 create, 13 aggiornate, gaps.md, index.md, log.md)»: `git diff --name-only 74ff34f HEAD -- wiki` elenca 23 file (7 create, 13 aggiornate comprese `persistenza-a` e le due entity, piu' i tre registri).

## Pagine dell'ingest del 2026-11-21 (commit `c28db3b`)

| Gruppo | Pagine | Esito |
|---|---|---|
| Create (6 source) | `wiki/sources/2026-11-21-repo-llm_wiki-{api-mcp,agente-runtime,agente-tools,fs-lib-progetto,ingest,ricerca-ui-residui}.md` | frontmatter completo, `updated: 2026-11-21`, nell'index (7 righe aggiunte), 0 broken-link, 0 candidati Check 2 |
| Creata (1 concept) | `wiki/concepts/llm-wiki-pipeline-ingest.md` | frontmatter completo, nell'index, 11 citazioni, 0 candidati Check 2; non ha sezione `## Aggiornamenti` (pagina nuova) |
| Aggiornate (12) | `llm-wiki-agente`, `-api-locale`, `-archivi-persistenza`, `-cancellazione-pagine-e-sorgenti`, `-operazioni-distruttive`, `-rischi-persistenza`, `-schema-dati`, `-sicurezza`, `-test-e-ci`, `-versioni-e-migrazioni`, `llm-wiki-app`, `llm-wiki-mcp-server` | tutte hanno una sezione `## Aggiornamenti (v2026-11-21)` (1 occorrenza ciascuna) e `updated: 2026-11-21`; osservazioni: W19, W20-W22, W23-W24 |
| Aggiornata (1 source) | `2026-11-20-repo-llm_wiki-persistenza-a.md` | sezione `## Aggiornamenti (v2026-11-21)` (nota sul ramo), W25 |

Check 2 (euristica del run 3: a riga, soglia 20 parole senza marcatori, finestra [riga, riga+3], righe di tabella e «Storie collegate» non valutate) sulle 36 pagine: nessun candidato nelle 7 pagine create ne' nelle sezioni `## Aggiornamenti (v2026-11-21)` delle 13 aggiornate. Candidati in `concepts/`: solo W17 (riga 128), W18 (riga 127) e le due righe «Storie collegate» escluse (`master-difetti-rilevati.md` riga 117, `llm-wiki-sicurezza.md` riga 47).

## Citation audit (inline)

Metodo: script di sola lettura nello scratchpad di sessione (non nel repo). Per ogni `[^src: <path> §<sez>]` verifica l'esistenza del path e che `<sez>` sia un header del file citato; seconda passata piu' severa sulle citazioni ai raw del 2026-11-21 (uguaglianza esatta, senza backtick e maiuscole).

| Misura | Run 3 (2026-11-20) | Run 1 (2026-11-21) |
|---|---|---|
| Citazioni `[^src|code:]` totali | 427 | 774 (di cui 8 `[^code:]`) |
| Citazioni a `raw/2026-11-21-*` | - | 330, in 21 file (le 6 source, `pipeline-ingest`, 12 concept/entity aggiornati, `persistenza-a`, `gaps.md`) |
| Path inesistente | 0 | 0 |
| Sezione assente nel file citato | 0 | 0; sui 330 riferimenti ai raw del 2026-11-21: 330 a uguaglianza esatta, 0 per prefisso, 0 per inclusione |
| Fuori grammatica | 0 | 2 (I12, `§` su chiave JSON del manifest, preesistenti) |
| Wikilink rotti | 0 | 0 (2 falsi positivi, I11) |

Ogni citazione `[^src: raw/2026-11-21-...md §Sezione]` punta a un file esistente e a un header esistente. Limiti: verifica di forma, non di fedelta' del contenuto; le `[^code: ...]` sono contate e non verificate contro il submodule (non si entra in `code_repos/llm_wiki`). Cio' che e' stato controllato oltre la forma: i raw citati sono quelli nel manifest (4e) e, per W23-W24, la coerenza con `sources:` di frontmatter.

## Check NON ESEGUITI o saltati

Config invariata (`git diff --stat 74ff34f HEAD -- factory.config.yaml` vuoto).

| Check | Stato | Motivo |
|---|---|---|
| 4at | NON ESEGUITO | esecutore dichiarato: test pytest, fuori dai comandi consentiti a questo agente |
| 4an | NON ESEGUIBILE | citato in un header senza sezione nel file |
| 4af, 4ak | saltati | `semantic_check.enabled: false`, `content_share.enabled: false` (valori del run 2) |
| 4v, 4w, 4x, 4al, 4ad, 4ae, 4ap, FE quality, Compression, Oracle | saltati | flag a `false` o assenti (valori del run 2) |
| 4bh, 4bi, 4j | script, regola spenta | output dello script |
| 4m | no-op | `grep risk_classification management/kanban`: nessun risultato |

## heal-eligible

- **ERROR heal-eligible: 0.** `heal_eligible_count: 0`, `heal_eligible_categories: []`. Nessun `broken-wikilink` reale, nessun `missing-frontmatter-field` (W7 non deducibile dal path e WARNING, W23-W24 hanno il campo), nessun `citation-section-mismatch`.
- **4ax (W3)**: etichettato «heal-eligible» dallo script, registrato come `script_heal_label: [4ax]`, non contato: fuori dalla whitelist di `heal-protocol` e soggetto al difetto 11 (modifica di `.gitmodules`).

## Rescan correzioni W19-W25

Rescan scoped del 2026-11-21 sulle modifiche non committate di wiki-keeper (`git status --short`: 6 pagine wiki + `gaps.md` + `log.md` modificati). Letti: diff completo, righe originali, frontmatter, header dei raw citati. Nessun auto-fix, `wiki/log.md` non toccato.

| Finding | Esito | Motivo |
|---|---|---|
| W19 | CHIUSO (con residuo minore) | Il chiamante `MaintenanceSection` e' registrato in `operazioni-distruttive` (nota dopo riga 127), in `rischi-persistenza` (`### Correzioni da lint`, sotto `## Aggiornamenti (v2026-11-21)`) e in `gaps.md` (`Aggiornamento` dopo riga 209, gap `llm-wiki-import-id-duplicato` resta aperto). Nuova voce in `## Contradictions` di `operazioni-distruttive` («Chiamante UI di `import_project_archive`: trovato contro non trovato»). Citazione `raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Operazioni distruttive: chiamanti, riga per riga`: header presente (riga 25), e la riga 44 del raw riporta `import_project_archive` -> `MaintenanceSection`. Residuo: la voce `## Contradictions` e' in `operazioni-distruttive`, non in `rischi-persistenza` come suggerito; la riga 86 di `rischi-persistenza` («non e' stato trovato in `src/`») e la frase di `gaps.md` 209 restano com'erano, corrette da note adiacenti e non riscritte. Contraddizione dichiarata, quindi chiuso per il criterio del Check 3. |
| W20 | ANCORA PRESENTE (attenuato) | `rischi-persistenza` riga 28 letta: «il raw aggiunge un ottavo punto, i segreti in chiaro in `app-state.json`...» e' invariata e resta formulata come fatto. La nota aggiunta (riga ~114) la qualifica «DEDUZIONE NON TESTATA», ma non la modifica. Per il criterio del lint (affermazione presentata come fatto nel punto in cui compare) il finding non e' chiuso. E' declassabile a INFO solo se si accetta la nota di rettifica come qualifica sufficiente: decisione dell'utente. Il fix originale era «riformulare la riga 28». |
| W21 | ANCORA PRESENTE (attenuato) | `sicurezza` riga 54 letta: «**Segreti in chiaro nello store.** Tra i campi in chiaro compaiono `token` e `localToken`...» invariata, intestazione compresa. La nota (dopo riga 112, in coda a `## Aggiornamenti`) e' distante dalla riga e il lettore della sezione v2026-11-20 non la incontra. Stesso esito di W20. |
| W22 | ANCORA PRESENTE (attenuato) | `archivi-persistenza` riga 60 letta: «Tra i campi in chiaro compaiono `token` e `localToken` in `mineruConfig`...» invariata. La nota e' alla riga ~171, in fondo alla sezione v2026-11-21, con rinvio al gap `llm-wiki-token-cifratura` (presente in `gaps.md` riga 345, aperto). Stesso esito di W20. |
| W23 | CHIUSO | `sicurezza.md` riga 8 letta: `sources:` ora include `raw/2026-11-21-repo-llm_wiki-ingest.md` (8 raw, uno in piu'). |
| W24 | CHIUSO | `operazioni-distruttive.md` riga 8 letta: `sources:` ora include `raw/2026-11-21-repo-llm_wiki-agente-tools.md`; il file esiste. |
| W25 | CHIUSO | `sources/2026-11-20-repo-llm_wiki-persistenza-a.md` riga 7 letta: `updated: 2026-11-21` (diff: 1 riga). |

### Verdetto onesto su W20-W22

Con il criterio del lint il finding NON e' chiuso: la riga originale e' ancora scritta come fatto («i segreti in chiaro», «Tra i campi in chiaro compaiono», «Segreti in chiaro nello store»). Le note sono corrette nel contenuto, ma la correzione e' un cerotto a distanza, non una riformulazione. In `rischi-persistenza` e in `sicurezza` la pagina ha anche la versione gia' corretta (righe 106 e 100), quindi l'incoerenza interna e' ora dichiarata ma non eliminata. Per chiuderli: riformulare le tre righe (es. «campi che, nelle finestre lette, non risultano cifrati: deduzione non testata») oppure decidere esplicitamente che la nota basta e declassare a INFO. Stato proposto: 3 WARNING aperti (W20-W22).

### Check 2 sulle righe aggiunte (nuovi candidati)

- `archivi-persistenza` nota W22: 0 `[^src:]`; contiene un'affermazione («nelle finestre lette non si vede alcuna cifratura») non citata nella riga stessa, sostenuta solo dal gap `llm-wiki-token-cifratura` (riga 345 di `gaps.md`, che cita `fs-lib-progetto §Archivio dello stato app (gap 15)`). Candidato Check 2 WARNING (**W26**), fix: citare `raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md §Archivio dello stato app (gap 15)`. Non verificata la fedelta' del rinvio.
- `sicurezza` nota W21 (riga ~112): stessa formulazione, 0 citazioni: candidato (**W27**), stesso fix.
- `rischi-persistenza`, secondo punto della nota (riga 28 / W20): stessa formulazione, 0 citazioni: candidato (**W28**), stesso fix.
- `operazioni-distruttive` nota W19: 1 citazione; la frase «Resta NON verificato se l'id venga rigenerato...» e' una dichiarazione di non verificato, non un claim: non e' candidato.
- `rischi-persistenza` primo punto della nota: citato. `gaps.md` aggiornamento: citato. Voce Contradictions: 2 citazioni, ok.

W26-W28 sono lo stesso difetto (nota senza citazione) su tre pagine; sono WARNING nuovi indotti dalla correzione, heal-eligible: false.

### Citazioni nuove: esistenza delle sezioni

- `raw/2026-11-20-repo-llm_wiki-persistenza-c.md §Operazioni distruttive: chiamanti, riga per riga`: esiste (riga 25). Usata 4 volte (3 pagine + gaps).
- `raw/2026-11-21-repo-llm_wiki-fs-lib-progetto.md §Identita' del progetto, registro e import (gap 26)`: esiste (riga 34).
- Nessuna citazione nuova rotta. `persistenza-c` e' in `sources:` di `rischi-persistenza` e `operazioni-distruttive`.
- Link `[[...]]` nuovi: nessuno. Nessun frontmatter alterato oltre a W23-W25.

### Totali dopo il rescan (solo per W19-W25 e derivati)

Chiusi: W19, W23, W24, W25 (4). Aperti: W20, W21, W22. Nuovi: W26-W28. Variazione netta WARNING: 18 -> 17 (-4 chiusi, +3 nuovi), da riverificare con il lint completo; ERROR 0, heal-eligible 0.

---
id: LWS-TSK-010
title: "Rescan e changedTasks nella skill, assenza di 499 e ricetta con una route nuova"
us: LWS-US-007
sprint: 01
layer: docs
consumer: agent
priority: P1
estimate: S
status: done
depends_on: [LWS-TSK-009]
blocked_by: []
code_path: ["code_repos/llm_wiki_skill/SKILL.md", "code_repos/llm_wiki_skill/api-reference.md", "code_repos/llm_wiki_skill/examples.md"]
target: llm_wiki_skill
started_at: 2026-11-23
closed_at: 2026-11-23
decision_refs: []
---

# LWS-TSK-010 — Rescan, `changedTasks` e ricetta

## Context
Seconda parte di LWS-US-007 (AC6-AC9, AC10): comportamento del rescan, codici 499 e 409, almeno una ricetta di `examples.md` con una route nuova. Copre D21 (rescan), n. 13 (parte nota), V16-V18. `depends_on` su `LWS-TSK-009` per sovrapposizione di file. [^src: management/kanban/LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-007-scritture-chat-e-rescan/LWS-US-007.md §Acceptance Criteria]

## Technical Specs
- **Layer docs, consumer agent, target `llm_wiki_skill`.** Branch condiviso. `README.md` non è atteso.
- **Evidenza dei fatti:**

| Fatto | Livello |
|---|---|
| V16-V18: il rescan non accoda nella coda di ingest dell'app ma aggiorna lo snapshot e accoda i cambi nella coda Rust; `changedTasks` vuoto significa già visto; `created` e `modified` avviano l'ingest; l'ingest parte per il progetto aperto con `enabled`, `autoIngest` e un LLM; per i progetti inattivi dipende da «Watch all projects» | [C] parziale |
| «Watch all projects»: default, LLM nel ramo inattivi; elenco completo dei `kind` | non noti |
| 409 solo per `pages/write` (contratto); 499 non in wiki | [C] contratto / non in wiki |

- Non si afferma che i cambi si perdano né che l'ingest parta per i progetti inattivi.
- Fonti: [^src: wiki/concepts/llm-wiki-sincronizzazione-file.md §Dettaglio] [^src: wiki/gaps.md §2026-11-22 13:30 — llm-wiki-watch-all-projects-residui] [^src: wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md §Esito per voce]
- La ricetta di `examples.md` usa una route nuova senza il corpo non noto (per esempio la lettura di `reviews`, che ha evidenza [E+C]).

## Vincoli comuni (TSK docs di contenuto)
- Prima di scrivere: `git -C code_repos/llm_wiki_skill branch --show-current` = branch condiviso; altrimenti STOP.
- Si scrive solo nei file di `code_path`; nessun file nuovo, codice o script.
- Testi della skill senza ID kanban, riferimenti a ADR, wiki o factory, attribution AI o `Co-Authored-By`; [C]/[E] solo nel TSK.
- Se la wiki non documenta un comportamento v0.6.13, la skill non lo afferma.
- Commit: non lo esegue il dev-agent; propone un messaggio generico senza ID; la sessione principale lo esegue con `tools/vcs/sm_commit.py` dopo OK esplicito. `done` solo dopo il commit; Chiusura con i tre campi (dichiarati, committati, working tree).

## Implementation Steps
1. Verifica del branch.
2. Descrivere il rescan: aggiorna lo snapshot e riporta `changedTasks`; vuoto = già visto; non accoda da sé l'ingest; l'ingest parte per il progetto aperto alle condizioni note.
3. `changedTasks[].kind`: solo `created` e `modified` avviano l'ingest, senza elenco completo.
4. Verificare l'assenza del codice 499 e che il 409 compaia solo per `pages/write`.
5. Aggiungere in `examples.md` almeno una ricetta con una route nuova, senza il corpo non noto.
6. Ricerche testuali con comando ed esito.

## Definition of Done
- [x] AC6..AC9 di LWS-US-007 verificati con ricerca testuale e hunk.
- [x] AC10: riga di evidenza per ogni affermazione cambiata.
- [x] Nessuna traccia nei file toccati.

## Chiusura
<!-- AC1-AC5 sono di LWS-TSK-009 -->

Branch verificato prima di scrivere: `docs/align-v0-6-13`, HEAD `d3d3fd4`, working tree pulito. Fini riga dei tre file: LF (0 CR con `grep -c $'
'`), mantenute.

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-007 AC6 | Soddisfatto | `api-reference.md` 421-425: `changedTasks` vuoto = già visto; 433-435: «does not queue into the app's ingest queue itself. It updates the snapshot, queues the changes in the app's file-change queue and emits events to the desktop UI»; 436-438 condizioni per il progetto aperto (`enabled`, `autoIngest`, LLM); 439-445 progetti non aperti: «Whether the ingest starts for those projects is not documented here». `SKILL.md` 162 e 174 allineati («does not prove that ingest was queued»). Ricerca `lost\|lose\|perd` sui 4 file: nessuna occorrenza riferita ai cambi (solo «relative gaps» in `SKILL.md` 221, non pertinente) |
| LWS-US-007 AC7 | Soddisfatto | `api-reference.md` 421-423: «Only `created` and `modified` start ingest; the other values of `kind` are not documented here»; `examples.md` 151-152 senza `deleted`. Ricerca `created\|modified\|deleted`: `deleted` assente dalla skill |
| LWS-US-007 AC8 | Soddisfatto | Ricerca `499` sui 4 file: 0 occorrenze. Ricerca `409`: solo `SKILL.md` 179 e 206 e `api-reference.md` 483 e 487, tutte su `pages/write` |
| LWS-US-007 AC9 | Soddisfatto | `examples.md` 173-186: nuova ricetta «What is waiting for my review?» con `GET .../reviews?status=unresolved&limit=20`; il passo 4 dichiara che i corpi di `PATCH`, `DELETE` e `resolve` non sono documentati e non vanno indovinati |
| LWS-US-007 AC10 | Soddisfatto | Tabella sotto: una riga per ogni affermazione cambiata |

### Affermazioni cambiate (AC10)

| # | File e riga | Affermazione (sintesi) | Livello | Evidenza |
|---|---|---|---|---|
| 1 | `SKILL.md` 162 | `changedTasks` vuoto = l'app ha già visto i cambi; elenco non vuoto non prova l'accodamento; solo `created` e `modified` avviano l'ingest | [C] parziale | concetto `llm-wiki-sincronizzazione-file` §Aggiornamenti (verifica sul codice), «Idempotenza» e «Quando parte l'ingest» |
| 2 | `SKILL.md` 174 | il rescan aggiorna lo snapshot, restituisce coda e `changedTasks`, non accoda da sé l'ingest nell'app | [C] parziale | stesso concetto, «Rescan (HTTP o manuale)» |
| 3 | `api-reference.md` 421-425 | `changedTasks` vuoto = già visto; si tolgono `(created / modified / deleted)`; solo `created` e `modified` avviano l'ingest; gli altri `kind` non sono documentati | [C] parziale; elenco `kind` non noto | stesso concetto, «Idempotenza»; tabella dei fatti del TSK (elenco `kind` non noto) |
| 4 | `api-reference.md` 433-435 | il rescan non accoda nella coda di ingest dell'app: aggiorna lo snapshot, accoda i cambi nella coda dei cambi di file (Rust), emette eventi alla UI; la UI accoda l'ingest solo per `created` e `modified` sotto `raw/sources/` | [C] parziale | stesso concetto, «Rescan (HTTP o manuale)» (`enqueue_rescan_changes`, `write_queue`, `queue-updated` e `changed`) |
| 5 | `api-reference.md` 436-438 | progetto aperto: ingest solo con `enabled`, `autoIngest` e un LLM usabile | [C] parziale | stesso concetto, «Quando parte l'ingest» (ramo progetto aperto) |
| 6 | `api-reference.md` 439-445 | progetto non aperto: il listener ignora i suoi eventi; solo «Watch all projects» aggiunge un percorso (rescan ogni 60 s dei progetti recenti con `enabled`); l'avvio dell'ingest non è documentato (default e LLM non noti); l'effetto di un rescan su un progetto non aperto non è documentato | [C] parziale; default e LLM non noti | stesso concetto, Contradictions (nota di risoluzione) e «I 60 s»; gap `llm-wiki-watch-all-projects-residui`. Tolto «off by default» e «events for other projects are dropped» |
| 7 | `examples.md` 148 | per un progetto non aperto l'ingest dipende da «Watch all projects» e non si promette | [C] parziale; default non noto | come riga 6 |
| 8 | `examples.md` 151-152, 165 | rapporto con `created` e `modified` (senza «K deleted»); solo questi avviano l'ingest; «already seen» | [C] parziale | come righe 1 e 3 |
| 9 | `examples.md` 173-186 | ricetta di lettura delle `reviews` (`status`, `type`, `limit`, campi `count`, `type`, `title`, `description`, `sourcePath` assoluto); le scritture restano senza corpo | [E+C] lettura; [C] riscrittura di `review.json` (già in `api-reference.md` 564-570, TSK-009) | `api-reference.md` §GET /projects/{id}/reviews, campi osservati |
| 10 | 499 e 409 | 499 assente; 409 solo per `pages/write` | non in wiki / [C] contratto | ricerche testuali sotto: nessuna modifica, verifica di assenza |

### Ricerche testuali (cartella `code_repos/llm_wiki_skill`, file `SKILL.md api-reference.md examples.md`, più `README.md` dove indicato)
Comando: `grep -nEi "<modello>" SKILL.md api-reference.md examples.md README.md`.

| Modello | Esito |
|---|---|
| `499` | 0 occorrenze |
| `409` | 4 righe, tutte `pages/write` (`SKILL.md` 179, 206; `api-reference.md` 483, 487) |
| `changedTasks` | 12 righe, tutte coerenti con le righe 1-3 e 8 della tabella |
| `kind` | `api-reference.md` 328 (non pertinente, «Its kind depends on»), 414, 421-423; `examples.md` 151 |
| `created\|modified\|deleted` | `deleted` assente; `created` e `modified` solo nei contesti delle righe 3, 4 e 8 (più `createdAt` delle review) |
| `Watch all projects` | `api-reference.md` 441; `examples.md` 148 (nessun default affermato) |
| `off by default\|by default` | solo bind di rete, «read-only by default»: nessuna riga su «Watch all projects» |
| `lost\|lose\|perd` | nessuna riferita ai cambi |
| `queued\|queue` | verificate: `README.md` 113 dice «queued by the UI only for the open project» (fuori da `code_path`, vedi residui) |
| `autoIngest` | `api-reference.md` 438; `examples.md` 148, 165; `README.md` 113 |
| `reviews` | ricetta nuova e righe già scritte da LWS-TSK-009 |
| `501\|only write\|no write\|write endpoint\|do not invent\|read-only` | nessuna formula vietata dell'AC1 |
| tracce: `LWS\|TSK\|US-\|ADR\|wiki-factory\|factory\|kanban\|Co-Authored\|Anthropic\|\[C\]\|\[E\]` | nessuna nelle righe toccate; occorrenze solo di «gap» (score) e «Claude Code» (README, come prodotto) |

### Diff di chiusura (a comando)
- Dichiarati: `code_repos/llm_wiki_skill/SKILL.md`, `api-reference.md`, `examples.md`.
- Committati: `c73a69c` nel repo della skill (3 file, 37+/13-), dopo OK esplicito dell'utente in chat (2026-11-23); `sm_commit.py --dry-run` → messaggio invariato; `git log -1` senza trailer né attribution. Dopo il commit `git status --short` della skill vuoto. Factory: commit con questo TSK, `wiki/log.md`, `sprint.md` e il puntatore.
- Punti dubbi (decisione dell'utente, 2026-11-23): `README.md` r.113 («Ingest is queued by the UI only for the open project») rinviato a LWS-TSK-014; punti 2 e 3 tenuti come proposti. Evidenza dei 60 s: `wiki/concepts/llm-wiki-sincronizzazione-file.md` r.75 (solo con «Watch all projects» attivo).
- Working tree: `git -C code_repos/llm_wiki_skill status --short` = `M SKILL.md`, `M api-reference.md`, `M examples.md`; nella factory `git status --short` mostra anche `m code_repos/llm_wiki_skill` (puntatore del submodulo), `M ...TSK-029.md` (altra sessione, non toccato) e `?? DOSSIER-llm-wiki-qualita-ingest.md` (non toccato) e questo TSK.

## Dependencies
- LWS-TSK-009 — serializzazione per sovrapposizione di file.

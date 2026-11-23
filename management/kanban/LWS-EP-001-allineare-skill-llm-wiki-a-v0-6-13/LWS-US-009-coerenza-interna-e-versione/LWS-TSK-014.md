---
id: LWS-TSK-014
title: "Dichiarazione di versione, README e regola di drift nella skill"
us: LWS-US-009
sprint: 02
layer: docs
consumer: agent
priority: P1
estimate: S
status: done
depends_on: [LWS-TSK-010]
blocked_by: []
code_path: ["code_repos/llm_wiki_skill/README.md", "code_repos/llm_wiki_skill/SKILL.md", "code_repos/llm_wiki_skill/api-reference.md"]
target: llm_wiki_skill
started_at: 2026-11-23
closed_at: 2026-11-23
decision_refs: []
---

# LWS-TSK-014 — Versione, README e drift

## Context
La skill deve dichiarare solo «verificata su v0.6.13» con la base dichiarata, avere README coerente e una regola di drift su qualunque versione diversa da quella verificata. Copre n. 11, n. 16 (valori di `status`), n. 17 e A4 (incongruenze ereditate). Decisioni dell'utente: niente «0.4.10+», nessuna storia delle versioni, base in termini generici. Dipende da `LWS-TSK-010` (ultimo dei TSK di contenuto, stessi file; AC3 richiede i campi coerenti con `LWS-TSK-006`). [^src: management/kanban/LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-009-coerenza-interna-e-versione/LWS-US-009.md §Acceptance Criteria] [^src: wiki/entities/llm-wiki-skill.md §Versione dichiarata]

## Technical Specs
- **Layer docs, consumer agent, target `llm_wiki_skill`.** Branch condiviso.
- **Base di verifica (formulazione generica):** lettura del codice sorgente dell'app alla v0.6.13 e alcune risposte verificate su un'app in esecuzione. **Non** si citano progetto, date né identificativi della prova.
- **Regola di drift:** confrontare la versione riportata da `/health` con quella verificata; per qualunque versione diversa, controllare `api-reference.md`. Non dipende più da un «major version bump».
- **README:** quattro file (non «three markdown files»); comando di update con il nome della skill `llm-wiki`, non `llm_wiki_skill`; esempio di `/health` con `version` e campi coerenti con LWS-US-005; «four forms» di `{id}` coerente con le tre forme del server più il nome risolto lato client.
- **Non si toccano:** licenza, rotazione del token, valori di `status` di `/health` (restano i quattro noti [C]).
- **Evidenza:** intra-skill per n. 11; [C] per i quattro valori di `status`; la base di verifica è la dichiarazione dell'epica. [^src: wiki/entities/llm-wiki-skill.md §Incoerenze interne della skill (materiale per la PR)] [^src: wiki/concepts/llm-wiki-skill-api-v1-dichiarata.md §Versione dichiarata]

## Vincoli comuni (TSK docs di contenuto)
- Prima di scrivere: `git -C code_repos/llm_wiki_skill branch --show-current` = branch condiviso; altrimenti STOP.
- Si scrive solo nei file di `code_path`; nessun file nuovo, codice o script.
- Testi della skill senza ID kanban, riferimenti a ADR, wiki o factory, attribution AI o `Co-Authored-By`; [C]/[E] solo nel TSK.
- Se la wiki non documenta un comportamento v0.6.13, la skill non lo afferma.
- Commit: non lo esegue il dev-agent; propone un messaggio generico senza ID; la sessione principale lo esegue con `tools/vcs/sm_commit.py` dopo OK esplicito. `done` solo dopo il commit; Chiusura con i tre campi (dichiarati, committati, working tree).

## Implementation Steps
1. Verifica del branch.
2. README: numero di file, nome della skill nel comando di update, esempio di `/health`.
3. Dichiarazione di versione e base di verifica in tutti i file che la citano; togliere «0.4.10+» e ogni «dalla versione X».
4. Riscrivere la regola di drift.
5. Allineare «four forms» di `{id}`.
6. Ricerche testuali (`0.4.10`, «major version», «dalla versione»/«since version», «three markdown files», `llm_wiki_skill`) con comando ed esito.

## Definition of Done
- [x] AC1, AC2, AC3, AC4, AC6 di LWS-US-009 verificati con ricerca testuale e hunk.
- [x] AC7: riga di evidenza per ogni affermazione cambiata.
- [x] Nessuna traccia nei file toccati; progetto, date e identificativi della prova assenti.

## Chiusura
<!-- AC5 è di LWS-TSK-015 -->

**Diff di chiusura** (tre campi distinti; «Working tree» è lo stato prima del commit)
- Dichiarati: `code_repos/llm_wiki_skill/README.md`, `code_repos/llm_wiki_skill/SKILL.md`, `code_repos/llm_wiki_skill/api-reference.md`; questo TSK (`status`, `started_at`, Chiusura).
- Committati: `9c2669e` nel repo della skill (3 file, 24+/23-), dopo OK esplicito dell'utente in chat (2026-11-23); `sm_commit.py --dry-run` → messaggio invariato; `git log -1` senza trailer né attribution. Dopo il commit `git status --short` della skill vuoto. Factory: commit di chiusura `ea89982` con questo TSK, `wiki/log.md`, `sprint.md` e il puntatore; lo stesso commit contiene anche tre file di TSK-029 che un'altra sessione aveva messo in stage nello stesso momento (indice condiviso), dichiarato in `6e62468`.
- Aggiornamento dopo LWS-TSK-015 (2026-11-23): l'intestazione di `examples.md` r.173 e la regola di drift in `SKILL.md` sono decise e fatte in LWS-TSK-015 (`fd8a5a4`); «older builds» e «shorter than older docs stated» sono rinviati a LWS-TSK-016; i marcatori «0.6.13.» sulle route restano. Le righe «Residui», «Punti dubbi» e «Non toccati e da valutare» sopra descrivono lo stato al momento della chiusura di questo TSK.
- Verifica della sessione principale: la sezione «Additions in app 0.6.13» tolta ripeteva solo i campi di `/health`, ancora documentati sopra; le altre righe perdono solo il prefisso di versione (confronto delle righe `-`/`+` del diff).
- Punti dubbi (decisione dell'utente, 2026-11-23): «labelled "API Server" in older builds» e «shorter than older docs stated» → LWS-TSK-016; marcatori «0.6.13.» sulle route lasciati; regola di drift in `SKILL.md` → decisione in LWS-TSK-015.
- Working tree, skill (`git -C code_repos/llm_wiki_skill status --short` e `diff HEAD --stat`; branch `docs/align-v0-6-13`, HEAD `c73a69c`): ` M README.md`, ` M SKILL.md`, ` M api-reference.md` (3 file, 24 inserzioni, 23 cancellazioni). `examples.md` non toccato.
- Working tree, factory (`git status --short`): `m code_repos/llm_wiki_skill` (puntatore del submodule, atteso). ` M .../TSK-029.md`, ` M raw/.extraction-manifest.json`, `?? DOSSIER-llm-wiki-qualita-ingest.md` e `?? raw/2026-11-23-repo-llm_wiki-rebuild-index-scrittori.md` sono di altre sessioni e non sono toccati. Questo TSK si aggiunge ai modificati.
- Fini riga: `grep -c $'\r'` = 0 sui quattro file della skill (LF mantenuto).

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-009 AC1 | soddisfatto | `README.md` r.28 «The skill is four markdown files»; r.147 `--skill llm-wiki` (hunk: `-npx skills add ... --skill llm_wiki_skill` / `+npx skills add ... --skill llm-wiki`). `SKILL.md` r.116 «accepts **three forms** on the server. The table adds a fourth line, the project name, which the server does not accept: resolve it on the client to an `id`». `api-reference.md` r.105 elenca tre forme (UUID, percorso, `current`) e r.111 «Resolving a user-spoken project name» risolve il nome lato client. |
| LWS-US-009 AC2 | soddisfatto | `README.md` r.136-140 (hunk: `-This skill matches **LLM Wiki API v1** as shipped in app 0.4.10+ ...` / `+This skill documents **LLM Wiki API v1** as implemented by app **0.6.13** ...` / `+Verified on 0.6.13 by reading the app source code at v0.6.13 and by checking some responses on a running app.`). Ricerca `grep -nE '0\.4\.10\|0\.4'` sui quattro file: nessuna riga. Ricerca `grep -niE 'major version\|since version\|from version\|0\.6\.13\+\|addition'`: nessuna riga. Tolti anche «0.6.13+», «0.6.13 additions/addition», «0.6.13 adds», il prefisso «0.6.13:» dei campi di `/health` e di `graphRelatedTo`, «(0.6.13)» di `graphHits` e la sezione «Additions in app 0.6.13» (duplicava l'elenco dei campi di `/health`). Progetto, date e identificativi della prova assenti (ricerca date `[0-9]{4}-[0-9]{2}-[0-9]{2}`: nessuna riga). |
| LWS-US-009 AC3 | soddisfatto | `README.md` r.77 `"version": "0.6.13"` (già presente, da LWS-TSK-006). I campi dell'esempio (`ok`, `status`, `version`, `enabled`, `authConfigured`, `tokenSource`, `allowUnauthenticated`) sono tutti nell'elenco di `api-reference.md` r.40-72 e di `SKILL.md` r.83. L'esempio resta parziale (`...`). Nessuna modifica all'esempio. |
| LWS-US-009 AC4 | soddisfatto | `README.md` r.140: «Drift check: compare the `version` that `/health` reports with `0.6.13`. If it is any other version, check `api-reference.md` for drift before relying on the contract verbatim.» Ricerca `grep -niE 'major version'` sui quattro file: nessuna riga. |
| LWS-US-009 AC5 | n/a | coperto da LWS-TSK-015 |
| LWS-US-009 AC6 | soddisfatto | `git -C code_repos/llm_wiki_skill diff HEAD` non ha hunk sui quattro valori di `status` (`api-reference.md` r.63), sulla sezione «License» (`README.md` r.158) né sulla rotazione del token. |
| LWS-US-009 AC7 | soddisfatto | Tabella sotto: una riga per ogni affermazione cambiata. |

**Affermazioni cambiate (AC7)**

| File:riga (dopo la modifica) | Affermazione cambiata | Livello | Evidenza |
|---|---|---|---|
| `README.md`:28 | tre file → quattro file | intra-skill | tabella «Files» del README elenca 4 file; la cartella ha `README.md SKILL.md api-reference.md examples.md` |
| `README.md`:147 | update con `--skill llm-wiki` | intra-skill | `README.md`:12 e frontmatter di `SKILL.md` `name: llm-wiki` |
| `README.md`:136 | «as shipped in app 0.4.10+» tolto; «documents ... as implemented by app 0.6.13» | dichiarazione dell'epica (decisione dell'utente) | LWS-US-009 Business Rules, decisione sulla versione |
| `README.md`:138 | base di verifica in termini generici | dichiarazione dell'epica (decisione dell'utente) | LWS-US-009 Business Rules, base della verifica |
| `README.md`:136 | «search adds» → «search results can include» (`graphHits`, `graphRelatedTo`, `hybrid`) | editoriale: stesso contenuto, senza storia delle versioni | `api-reference.md`:291, 303 |
| `README.md`:140 | regola di drift su qualunque versione diversa da 0.6.13 | dichiarazione dell'epica (decisione dell'utente N3) | LWS-US-009 Business Rules, decisione sul drift |
| `README.md`:113 | percorso di «Watch all projects» nella riga di troubleshooting del rescan | già nella skill | `api-reference.md`:430-448 (sezione «When does ingest actually start») e `examples.md`:148 |
| `SKILL.md`:116 | «four forms» → tre forme del server più il nome risolto lato client | intra-skill | `api-reference.md`:105-109 e 111-130; `SKILL.md`:123 («Project name ... Not supported directly (404)») |
| `SKILL.md`:83, 168 | «adds `mcpEnabled`...» → «also returns» | editoriale, stesso elenco di campi | `api-reference.md`:40-57 e 70-72 |
| `SKILL.md`:169 | «0.6.13 adds top-level `currentProject`» → «plus a top-level `currentProject`» | editoriale | `api-reference.md`:101 |
| `SKILL.md`:157, 173 | «Pagination (0.6.13+)» e «**0.6.13+:**» tolti | editoriale, stessa semantica | `api-reference.md`:351-352, 387 |
| `api-reference.md`:58 | frase «The last three fields are 0.6.13 additions» tolta | editoriale | `api-reference.md`:40-57 (i campi restano nell'esempio) |
| `api-reference.md`:70-72 | prefisso «0.6.13:» tolto da `mcpEnabled`, `allowLanAccess`, `agent` | editoriale | stesso elenco in `SKILL.md`:83 |
| `api-reference.md`:101 | «is a 0.6.13 addition» tolto | editoriale | `SKILL.md`:169 |
| `api-reference.md`:291, 332 | «(0.6.13)» e «0.6.13:» tolti da `graphHits` e `graphRelatedTo` | editoriale | `api-reference.md`:269-305 |
| `api-reference.md`:351, 352, 387 | «0.6.13+» tolto da `offset`, `edgeScope` e dai campi di paginazione | editoriale | `SKILL.md`:157, 173 |
| `api-reference.md` (r.529, prima) | sezione «Additions in app 0.6.13» rimossa | editoriale: duplicava `/health` | `api-reference.md`:40-72 |

**Ricerche testuali** (cartella `code_repos/llm_wiki_skill`; file `README.md SKILL.md api-reference.md examples.md`)
- `grep -nE '0\.4\.10|0\.4'`: nessuna riga, anche su `examples.md` (sola lettura).
- `grep -niE 'major version|since version|from version|three markdown|three files|four forms|0\.6\.13\+|addition'`: nessuna riga, anche su `examples.md`.
- `grep -nE 'llm_wiki_skill'`: 5 righe, tutte nel `README.md` (URL del repo r.12, 22, 147, 154; cartella di clone r.23); legittime. Nessuna `--skill llm_wiki_skill`.
- `grep -n 'Watch all projects'`: `README.md`:113, `api-reference.md`:441, `examples.md`:148; coerenti fra loro.
- Date e tracce (`TSK|LWS|ADR|wiki-factory|Co-Authored|Anthropic|\[C\]|\[E\]`): nessuna riga. «Claude» compare solo come «Claude Code» (agente destinatario della skill).
- Residui per LWS-TSK-015 (`examples.md`, non toccato): intestazione r.173 «(0.6.13)». Nessun «0.4.x» né dichiarazione di versione.
- Non toccati e da valutare: «older builds» in `README.md` r.55 e `SKILL.md` r.80; «shorter than older docs stated» in `api-reference.md` r.326; marcatori «0.6.13.» di route in `SKILL.md` r.175-182 e `api-reference.md` r.456, 467, 473, 493, 566.

## Dependencies
- LWS-TSK-010 — ultimo TSK di contenuto; serializzazione per sovrapposizione di file.

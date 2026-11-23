---
id: LWS-TSK-005
title: "Progetti, forme di {id}, files e files/content nella skill"
us: LWS-US-004
sprint: 01
layer: docs
consumer: agent
priority: P1
estimate: S
status: done
depends_on: [LWS-TSK-004]
blocked_by: []
code_path: ["code_repos/llm_wiki_skill/SKILL.md", "code_repos/llm_wiki_skill/api-reference.md", "code_repos/llm_wiki_skill/examples.md", "code_repos/llm_wiki_skill/README.md"]
target: llm_wiki_skill
started_at: 2026-11-23
closed_at: 2026-11-23
decision_refs: []
---

# LWS-TSK-005 — Progetti, file e contenuti

## Context
La skill descrive in modo non più valido `projects`, le forme di `{id}`, `files` e `files/content`. Copre D13, D17, D18; incoerenze n. 2, n. 5, n. 6, n. 11 (parte sull'id); V10, V11, V12, V25 (parte decisa dal codice). `depends_on` su `LWS-TSK-004` per sovrapposizione di file. [^src: management/kanban/LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-004-progetti-file-e-contenuti/LWS-US-004.md §Acceptance Criteria]

## Technical Specs
- **Layer docs, consumer agent, target `llm_wiki_skill`.** Branch condiviso.
- **Evidenza dei fatti:**

| Fatto | Livello |
|---|---|
| D13: `Content-Type` è `application/json` senza `charset=utf-8` | [E] soltanto: correzione neutra |
| D17: chiave `currentProject` in `/projects` (non in `/health`) | [E+C] |
| D17: il nome del progetto come `{id}` dà 404; `resolve_project` accetta id o percorso | [E]; [C] solo su id o percorso |
| D18: leggibili md, mdx, txt, csv, json, yaml, yml, xml, html, htm, log; `rtf` fuori lista (415) | [C] |
| n. 2: 413 oltre `maxFiles`; `truncated` mai `true` osservato; presenza come `false` non chiara | [E+C] parziale |
| n. 5: alias `raw` e `raw/sources` di `root` | [C+E] |
| V10: su Windows il match del percorso non distingue le maiuscole e accetta `\` | [C] |
| V11: si divide su `/` prima di decodificare; i due punti non sono separatori; `?` spezza l'URL, `+` diventa spazio, `%XX` decodificato ovunque | [C] parziale |
| V25: `current` = progetto con `current` vero impostato dalla UI; «esterni» e «negli script l'UUID» non decisi | [C] parziale |
| `files/content` permissivo (`/` iniziale, backslash, maiuscole) | [E] soltanto: non si porta |

- Fonti: [^src: wiki/syntheses/llm-wiki-skill-vs-app-v0-6-13.md §Aggiornamenti (v2026-11-22, verifica sul codice)] [^src: wiki/concepts/llm-wiki-api-osservazioni-esecuzione-v0-6-13.md §Osservazioni del 2026-11-13 (app 0.6.13, progetto reale, non replicate)] [^src: wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md §Esito per voce]
- Fatti solo osservati in forma neutra: si corregge soltanto la frase smentita.

## Vincoli comuni (TSK docs di contenuto)
- Prima di scrivere: `git -C code_repos/llm_wiki_skill branch --show-current` = branch condiviso; altrimenti STOP.
- Si scrive solo nei file di `code_path`; nessun file nuovo, codice o script.
- Testi della skill senza ID kanban, riferimenti a ADR, wiki o factory, attribution AI o `Co-Authored-By`; [C]/[E] solo nel TSK.
- Se la wiki non documenta un comportamento v0.6.13, la skill non lo afferma.
- Commit: non lo esegue il dev-agent; propone un messaggio generico senza ID; la sessione principale lo esegue con `tools/vcs/sm_commit.py` dopo OK esplicito. `done` solo dopo il commit; Chiusura con i tre campi (dichiarati, committati, working tree).

## Implementation Steps
1. Verifica del branch.
2. `projects`: aggiungere `currentProject`, esempio coerente, nessuna attribuzione a `/health`.
3. `{id}`: togliere «esatta» e le prescrizioni su maiuscole e slash; tenere l'avvertenza `%2F`.
4. `files/content`: elenco estensioni identico ovunque, `rtf` 415. `files`: 413 oltre `maxFiles`, nessun `truncated`, alias `raw` e `raw/sources` ovunque.
5. `Content-Type` neutro; togliere «negli script serve l'UUID» e «progetti esterni»; non portare la permissività osservata.
6. Controlli testuali con comando ed esito.

## Definition of Done
- [x] AC1..AC6 verificati con ricerca testuale e hunk del diff.
- [x] AC7: riga di evidenza per ogni affermazione cambiata.
- [x] Nessuna traccia nei file toccati.

## Chiusura

Branch verificato prima di scrivere: `git -C code_repos/llm_wiki_skill branch --show-current` → `docs/align-v0-6-13`; HEAD `753cbbd`, working tree pulito.

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-004 AC1 | soddisfatto | `currentProject` era già in `/projects` (SKILL.md r.125 e r.168; api-reference r.79-83; examples r.200). Cambiato l'esempio di api-reference: ora `id` e `path` pieni, uguali a `projects[0]`. Hunk: `-"currentProject": { "id": "a0e90b29-...", "name": "Research Notes", "path": "...", ...` → `+"currentProject": { "id": "a0e90b29-fcf3-4364-9502-8bd1272de820", ..., "path": "/Users/me/wiki-projects/research", ...`; aggiunto `+belongs to this response, not to /health`. Ricerca `health` con `current`: nessuna attribuzione a `/health` (la sola riga pertinente è la negazione, api-reference r.83). |
| LWS-US-004 AC2 | soddisfatto | «exact/esatta» assente per il percorso del progetto (ricerca `exact`: 6 righe, tutte non pertinenti). Tolto il consiglio upstream «preserve case, use only `/`». Hunk SKILL.md: `-Only `/` needs encoding (`%2F`); on Windows the match is case-insensitive and `\` is accepted.` → `+A `/` in the path must be sent as `%2F`. On Windows the match does not distinguish letter case and accepts `\`.` Hunk api-reference: `-the drive-letter colon is harmless (encoding it as `%3A` also works)` → `+A colon is not a separator.` Ricerca `%3A`: 0 occorrenze. Avvertenza `%2F` in SKILL.md r.122, api-reference r.131, examples r.21. |
| LWS-US-004 AC3 | soddisfatto | Elenco identico in SKILL.md r.170 e api-reference r.193 (`grep -o` della stessa stringa `md, mdx, txt, csv, json, yaml, yml, xml, html, htm, log`: 2 occorrenze); nessun altro file lo cita. `rtf` → 415 in SKILL.md r.170 e api-reference r.193 e r.212. Hunk: `-md/mdx/txt/json/yaml/yml/csv/html/htm/xml/log (**not** rtf)` → `+md, mdx, txt, csv, json, yaml, yml, xml, html, htm, log. `rtf` is not readable (415).` |
| LWS-US-004 AC4 | soddisfatto | 413 oltre `maxFiles` in SKILL.md, api-reference, examples, README. Ricerca `truncat` nei 4 file: 0 occorrenze. Hunk: `-(not a truncated list; `truncated` stays `false`)`; `-the list is never returned truncated and `truncated` stays `false`.`; `-  ],\n  "truncated": false\n}` → `+  ]\n}`; `-(0.6.13 does not truncate)`; `-instead of returning a partial tree`. Alias: `+`root`: `wiki`, `sources` (alias `raw`, `raw/sources`) or `all`.` in SKILL.md r.169; già in api-reference r.146. README ed examples non descrivono i valori di `root` (usano solo `root=wiki` e «narrow `root=`»): nessun alias aggiunto. |
| LWS-US-004 AC5 | soddisfatto | Hunk api-reference r.5: `-Default content type: `application/json; charset=utf-8` (0.6.13 sends `application/json` without `charset`; the body is UTF-8)` → `+Default content type: `application/json``. Ricerca `charset`: 0 occorrenze. |
| LWS-US-004 AC6 | soddisfatto | Tolto «in scripts resolve once and use the UUID» (SKILL.md r.120, api-reference r.85) e «every project… including unrelated ones» (SKILL.md r.125, api-reference r.83, examples r.204). Ricerche: `external\|esterni\|unrelated` 0 occorrenze; `in scripts` 0 occorrenze. Permissività di `files/content` tolta: `-On 0.6.13 a leading `/`, backslashes and a different letter case are also accepted.` (api-reference r.193) e `-On 0.6.13 backslashes and a different letter case are also accepted by `files/content`, but the forward-slash form is the one the API returns.` (examples r.20). Ricerca `letter case\|backslash\|case-insens`: restano solo le righe sul percorso del progetto (V10) e sul filtro per nome. |
| LWS-US-004 AC7 | soddisfatto | Tabella «Affermazioni cambiate» qui sotto: una riga di evidenza per ogni modifica. |

### Affermazioni cambiate (AC7)

| File | Affermazione dopo la modifica | Livello | Riga di evidenza del TSK |
|---|---|---|---|
| api-reference.md r.5 | Content type `application/json` (tolti `charset=utf-8` e «body is UTF-8») | [E], correzione neutra | D13 |
| api-reference.md r.79-83 | `currentProject` in `/projects`, esempio coerente con `projects[0]`; non in `/health` | [E+C] | D17 (chiave) |
| api-reference.md r.83, SKILL.md r.125, examples.md r.204 | La lista può contenere più progetti; tolti «every… known to the app» e «unrelated» | [C] parziale: V25 non decide «esterni» | V25 |
| api-reference.md r.85, SKILL.md r.120 | `current` = progetto con `current: true` impostato dalla UI; tolti «negli script l'UUID» e «può cambiare tra le chiamate» | [C] parziale | V25 |
| api-reference.md r.130, SKILL.md r.122 | Su Windows il match del percorso del progetto non distingue le maiuscole e accetta `\` | [C] | V10 |
| api-reference.md r.131, SKILL.md r.122, examples.md r.21 | Si divide su `/` prima di decodificare: `/` nell'id come `%2F`; i due punti non sono separatori; `%XX` decodificato ovunque, `+` = spazio, `?` chiude il percorso; tolti «Only `/` needs encoding» e il consiglio upstream su maiuscole e slash | [C] parziale | V11 |
| SKILL.md r.123 (invariata) | Nome del progetto come `{id}`: non supportato (404); id o percorso accettati | [E]; [C] solo su id o percorso | D17 (404, `resolve_project`) |
| SKILL.md r.170, api-reference.md r.193 e r.212 | Estensioni leggibili: md, mdx, txt, csv, json, yaml, yml, xml, html, htm, log; `rtf` → 415 (per estensione) | [C] | D18 |
| SKILL.md r.169, api-reference.md r.148 e r.170-173, README.md r.111, examples.md r.129 | 413 oltre `maxFiles`; nessuna affermazione su `truncated` (campo tolto anche dall'esempio) | [E+C] parziale | n. 2 |
| SKILL.md r.169 | Alias `raw` e `raw/sources` di `root` (già in api-reference.md r.146) | [C+E] | n. 5 |
| api-reference.md r.193, examples.md r.20 | Tolta la permissività osservata di `files/content` (`/` iniziale, backslash, maiuscole); resta «Prefer forward slashes» | [E] soltanto: non si porta | `files/content` permissivo |

### Ricerche testuali (comando ed esito)

Comando base, in `code_repos/llm_wiki_skill`: `grep -n -i -E '<pattern>' SKILL.md api-reference.md examples.md README.md`.

| Pattern | Esito |
|---|---|
| `exact` | 6 righe, tutte non pertinenti (pesi keyword, `nodeType`, «exact-string», esempio di risposta); nessuna per il percorso del progetto |
| `charset` | 0 |
| `truncat` | 0 |
| `rtf` | 3 righe: SKILL.md r.170, api-reference.md r.193 e r.212, tutte con 415 |
| `maxFiles` | 7 righe, tutte con 413 o con il valore del parametro |
| `md, mdx, txt, csv, json, yaml, yml, xml, html, htm, log` (`grep -o`) | 2 occorrenze identiche (SKILL.md r.170, api-reference.md r.193); nessun altro elenco di estensioni |
| `currentProject` | 5 righe (SKILL.md r.125, r.168; api-reference.md r.79, r.83; examples.md r.200) |
| `health` con `current` | api-reference.md r.83 (negazione) e README.md r.119 (`allowLanAccess`, non pertinente) |
| `UUID` | 7 righe: forma `{id}`, esempio, ricerca per nome; nessuna prescrizione «negli script» (`in scripts` e `script`: solo righe non pertinenti) |
| `external\|esterni\|unrelated` | 0 |
| `%2F` | 3 righe (SKILL.md r.122, api-reference.md r.131, examples.md r.21); `%3A`: 0 |
| `alias` | alias di `root`: SKILL.md r.169, api-reference.md r.146 |
| tracce: `LWS-\|TSK-\|US-[0-9]\|EP-[0-9]\|ADR\|Co-Authored\|Claude\|Anthropic\|factory\|\[E\]\|\[C\]\|\[\^src` | solo «Claude Code» in README.md (testo originale) e percorsi di esempio `wiki/concepts/...`; nessuna traccia della factory |
| `git diff --check` | nessun errore |

### Diff di chiusura

- **Dichiarati:** `code_repos/llm_wiki_skill/SKILL.md`, `api-reference.md`, `examples.md`, `README.md`; questo TSK (`status`, `started_at` e Chiusura).
- **Committati:** `69dece1` nel repo della skill (4 file, 21+/23-), dopo OK esplicito dell'utente in chat (2026-11-23); `sm_commit.py --dry-run` → messaggio invariato; `git log -1` senza trailer né attribution. Nella factory: commit di chiusura con TSK, log, sprint e puntatore a `69dece1`.
- Dopo il commit (a comando): repo della skill `git status --short` vuoto.
- Punti dubbi 1-6 del report: decisi dall'utente (2026-11-23) come proposti, nessuna modifica. Alias di `root`: presenti nei due file che descrivono `files` (`SKILL.md` r.169, `api-reference.md` r.146); `README.md` ed `examples.md` usano `root` senza descriverlo.
- **Nel working tree:** `git -C code_repos/llm_wiki_skill status --short` → `M README.md`, `M SKILL.md`, `M api-reference.md`, `M examples.md`; `git status --short` (factory) → `m code_repos/llm_wiki_skill`, `M` su questo TSK, `?? DOSSIER-llm-wiki-qualita-ingest.md` (preesistente, non toccato). Nessun file toccato e non dichiarato.

## Dependencies
- LWS-TSK-004 — serializzazione per sovrapposizione di file.

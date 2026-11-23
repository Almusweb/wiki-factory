---
id: LWS-TSK-007
title: "Grafo nella skill: paginazione, edgeScope, cache, archi da related e tipi di nodo"
us: LWS-US-005
sprint: 01
layer: docs
consumer: agent
priority: P1
estimate: S
status: done
depends_on: [LWS-TSK-006]
blocked_by: []
code_path: ["code_repos/llm_wiki_skill/SKILL.md", "code_repos/llm_wiki_skill/api-reference.md", "code_repos/llm_wiki_skill/examples.md", "code_repos/llm_wiki_skill/README.md"]
target: llm_wiki_skill
started_at: 2026-11-23
closed_at: 2026-11-23
decision_refs: []
---

# LWS-TSK-007 — `graph`

## Context
Seconda metà di LWS-US-005 (AC6, AC7, AC9): il grafo. Copre D10, D16, D19; n. 15; V4-V7 dove decisi. `depends_on` su `LWS-TSK-006` per sovrapposizione di file. [^src: management/kanban/LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-005-salute-ricerca-e-grafo/LWS-US-005.md §Acceptance Criteria]

## Technical Specs
- **Layer docs, consumer agent, target `llm_wiki_skill`.** Branch condiviso.
- **Evidenza dei fatti:**

| Fatto | Livello |
|---|---|
| D10: `offset`, `limit`, `totalCount`, `hasMore`, `edgeScope` (`page` o `filtered`; non valido: 400) | [E+C] parziale |
| D10: `limit` assente 200, ridotto a [1, 1000] (5000 diventa 1000), 400 per 0, negativo e non numerico | [C+E] |
| D10: cache di 5 s del grafo | [C] solo da raw api-mcp; non provata in esecuzione |
| D16: il tipo è la prima riga `type:` di tutto il file, minuscolo, default `other`; nodi `query` tolti dal grafo | [C+E] |
| D19: archi anche dai valori di `related:`; id nodo stem o percorso relativo in caso di collisione; link ambiguo scartato; dedup senza direzione | [C] |
| V8: `q` non restituisce i vicini (filtra solo i nodi) | [C] |

- Fonti: [^src: wiki/concepts/llm-wiki-ricerca-e-grafo-api.md §Dettaglio] [^src: wiki/syntheses/llm-wiki-skill-vs-app-v0-6-13.md §Aggiornamenti (v2026-11-22, verifica sul codice)] [^src: wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md §Esito per voce]
- La cache di 5 s resta marcata [C] da raw api-mcp, non provata: se l'esito di `LWS-TSK-011` arriva prima, si incorpora solo per decisione esplicita dell'utente.

## Vincoli comuni (TSK docs di contenuto)
- Prima di scrivere: `git -C code_repos/llm_wiki_skill branch --show-current` = branch condiviso; altrimenti STOP.
- Si scrive solo nei file di `code_path`; nessun file nuovo, codice o script.
- Testi della skill senza ID kanban, riferimenti a ADR, wiki o factory, attribution AI o `Co-Authored-By`; [C]/[E] solo nel TSK.
- Se la wiki non documenta un comportamento v0.6.13, la skill non lo afferma.
- Commit: non lo esegue il dev-agent; propone un messaggio generico senza ID; la sessione principale lo esegue con `tools/vcs/sm_commit.py` dopo OK esplicito. `done` solo dopo il commit; Chiusura con i tre campi (dichiarati, committati, working tree).

## Implementation Steps
1. Verifica del branch.
2. `graph`: `offset`, `edgeScope`, campi di risposta `offset`, `limit`, `totalCount`, `hasMore`, cache di 5 s, clamp di `limit` a [1, 1000] con 400 per 0, negativo e non numerico; `q` filtra solo i nodi.
3. «Nessuna paginazione» limitata a `files`.
4. Archi anche da `related:`, link ambigui scartati, `type: query` non nodi, `nodeType` insieme aperto con esempi non esaustivi.
5. Controlli testuali con comando ed esito.

## Definition of Done
- [x] AC6 e AC7 di LWS-US-005 verificati con ricerca testuale e hunk.
- [x] AC9: riga di evidenza per ogni affermazione cambiata.
- [x] Nessuna traccia nei file toccati.

## Chiusura
<!-- AC1-AC5 e AC8 sono di LWS-TSK-006 -->

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-005 AC6 | verificato | `api-reference.md` §graph: righe `offset` e `edgeScope` (`page`/`filtered`, altro valore 400), `limit` «Absent → 200 … 5000 becomes 1000; 0, negative or non-numeric → 400», JSON con `offset, limit, totalCount, hasMore`, «the backend keeps a 5 s cache of it», `q` «Filters nodes … does not return a node's neighbours», «Pagination applies to `graph` only: the `files` tree has no pagination». `SKILL.md` righe 154-158 e 173 e `examples.md` righe 94, 104, 280 coerenti |
| LWS-US-005 AC7 | verificato | «Edges come from `[[wikilinks]]` **and** the frontmatter `related:` list; a link that matches more than one page is dropped» (`SKILL.md`:158; `api-reference.md`:375); «`nodeType` is an open set … `entity`, `concept` and `other` are examples, not a complete list» (`SKILL.md`:155; `api-reference.md`:340); «Pages with `type: query` are **not** graph nodes» (4 punti) |
| LWS-US-005 AC9 | verificato | Tabella delle affermazioni cambiate qui sotto |

### Affermazioni cambiate (AC9)

| # | File | Affermazione nella skill | Livello | Evidenza (TSK) |
|---|---|---|---|---|
| 1 | `api-reference.md` | `offset` ed `edgeScope` nella tabella dei parametri; campi `offset`, `limit`, `totalCount`, `hasMore` nell'esempio | [E+C] parziale | Riga D10 della tabella del TSK |
| 2 | `api-reference.md`, `SKILL.md` | `edgeScope`: `page` solo archi con i due estremi nella pagina; `filtered` archi fra i nodi filtrati anche fuori pagina; altro valore 400 | [E+C] parziale | Riga D10 (400 osservato; semantica `page`/`filtered` dal codice, wiki llm-wiki-ricerca-e-grafo-api §Dettaglio, «Filtro q ed edgeScope») |
| 3 | `api-reference.md`, `SKILL.md` | `limit` assente 200, ridotto a [1, 1000] (5000 diventa 1000), 400 per 0, negativo e non numerico | [C+E] | Riga D10 `limit` |
| 4 | `api-reference.md`, `SKILL.md` | cache di 5 s del grafo; tolta la frase «a new page can take up to ~5 s to appear» (conseguenza non nella tabella) | [C] solo da raw api-mcp, non provata | Riga D10 cache |
| 5 | `api-reference.md`, `SKILL.md`, `examples.md` | «Nessuna paginazione» solo per `files`; la paginazione è di `graph` | [E+C] parziale | Righe D10 e passo 3 del TSK |
| 6 | `SKILL.md`, `api-reference.md` | `nodeType` insieme aperto: prima riga `type:`, minuscolo, `other` di default; esempi non esaustivi | [C+E] | Riga D16 |
| 7 | `SKILL.md`, `api-reference.md`, `examples.md` | pagine `type: query` non sono nodi | [C+E] | Riga D16 |
| 8 | `SKILL.md` | archi anche da `related:`; link ambiguo scartato | [C] | Riga D19 |
| 9 | `api-reference.md` | id nodo stem o percorso relativo, link ambiguo scartato, dedup senza direzione (testo già presente, invariato) | [C] | Riga D19 |
| 10 | `api-reference.md`, `SKILL.md` | `q` filtra solo i nodi, non restituisce i vicini (testo già presente, invariato; aggiunto il rinvio a `SKILL.md`:173) | [C] | Riga V8 |
| 11 | `examples.md` | con `edgeScope=page` un arco è restituito solo se i due estremi sono nella pagina | [C] | Riga D10 `edgeScope`, wiki «Filtro q ed edgeScope» |
| 12 | `SKILL.md` | tolto «(≥ 0)» da `offset` | — | Fatto non nella tabella del TSK: rimosso, non affermato |
| 13 | `api-reference.md` | valori dell'esempio JSON (`limit` 200, `totalCount` 120, `hasMore` false) | illustrativi | Nessun dato reale; coerenti fra loro |

### Ricerche testuali (`grep -n -o -i -E` su `SKILL.md api-reference.md examples.md README.md`)
- `offset`: SKILL 154/157/173, api-reference 337/366/373, examples 94/280. `edgeScope`: SKILL 157/173, api-reference 338, examples 94/104. `hasMore`, `totalCount`: presenti in SKILL 154/173 e api-reference 337-373. Esito: ok.
- `no pagination|not paginated|no offset|has no pagination`: SKILL 157, api-reference 342, examples 280, tutte riferite a `files`. Esito: ok.
- `related` (archi): SKILL 158/173, api-reference 375, README 33. `type: query`: SKILL 155/173, api-reference 340, examples 105. `nodeType`/`node_type`: solo i punti attesi. Esito: ok.
- `5 s|5s|cache`: grafo in SKILL 158/173 e api-reference 375; le altre occorrenze di `cache` sono ingest e id di progetto, fuori ambito. `1000` e `200`: limiti del grafo coerenti in SKILL 154/157/173, api-reference 336/448, examples 94/99/104/307; le altre occorrenze sono `files`, `topK` e pesi di ricerca. Esito: ok.
- Tracce (`LWS-|TSK-|US-|ADR|factory|Co-Authored|Claude|Anthropic|[C]|[E]|alm-wiki|code_repos`): nessuna nei testi aggiunti; solo «Claude Code» preesistente in README 3/17-23 (nome di prodotto) e `../app-state.json` (percorso d'esempio). Esito: ok.

### Diff di chiusura (a comando)
- **Dichiarati**: `code_repos/llm_wiki_skill/SKILL.md`, `api-reference.md`, `examples.md` (README.md in `code_path`, non toccato).
- **Committati**: `541e610` nel repo della skill (3 file, 22+/11-), dopo OK esplicito dell'utente in chat (2026-11-23); `sm_commit.py --dry-run` → messaggio invariato; `git log -1` senza trailer né attribution. Dopo il commit `git status --short` della skill vuoto. Factory: commit con questo TSK, la sola entry di handoff di `wiki/log.md` (stage parziale) e il puntatore; `sprint.md` escluso perché contiene anche il lavoro non committato di un'altra sessione sullo stesso clone (decisione dell'utente).
- Punti dubbi (decisione dell'utente, 2026-11-23): `offset` negativo → 400 resta fuori (solo [E], non in tabella); semantica di `totalCount`/`hasMore` e cache di 5 s del grafo da verificare in LWS-TSK-011.
- **Nel working tree** (`git -C code_repos/llm_wiki_skill status --short`, `git diff --name-only HEAD`): `SKILL.md`, `api-reference.md`, `examples.md` (3 file, 22 inserzioni, 11 cancellazioni). Nella factory, oltre a questo TSK, il working tree ha modifiche di altre sessioni (`sprint.md`, EP-002 TSK-009, `wiki/*`, `DOSSIER-...`) e il puntatore `code_repos/llm_wiki_skill` modificato.

## Dependencies
- LWS-TSK-006 — serializzazione per sovrapposizione di file.

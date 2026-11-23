---
id: LWS-TSK-006
title: "Salute e ricerca nella skill: campi di /health, graphHits, copertura e snippet"
us: LWS-US-005
sprint: 01
layer: docs
consumer: agent
priority: P1
estimate: M
status: done
depends_on: [LWS-TSK-005]
blocked_by: []
code_path: ["code_repos/llm_wiki_skill/SKILL.md", "code_repos/llm_wiki_skill/api-reference.md", "code_repos/llm_wiki_skill/examples.md", "code_repos/llm_wiki_skill/README.md"]
target: llm_wiki_skill
started_at: 2026-11-23
closed_at: 2026-11-23
decision_refs: []
---

# LWS-TSK-006 — `/health` e `search`

## Context
Prima metà di LWS-US-005 (AC1-AC5, AC8, AC9): `/health` e `search`. Il `graph` è `LWS-TSK-007`. Copre D7, D9, D14, D15, D20; n. 3, n. 4; V1-V3, V8, V13. `depends_on` su `LWS-TSK-005` per sovrapposizione di file. [^src: management/kanban/LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-005-salute-ricerca-e-grafo/LWS-US-005.md §Acceptance Criteria]

## Technical Specs
- **Layer docs, consumer agent, target `llm_wiki_skill`.** Branch condiviso.
- **Evidenza dei fatti:**

| Fatto | Livello |
|---|---|
| D7: `/health` con `mcpEnabled`, `allowLanAccess`, `agent{chat, streaming, streamProtocol}`; risponde anche su `/health` senza prefisso (e con `POST`); `currentProject` non è in `/health` | [E+C] parziale |
| D9: `graphHits` in `search` | [E+C] |
| D14: snippet di circa 110 caratteri, frontmatter compreso (la skill dice circa 160) | [E] soltanto: correzione neutra |
| D15: `hybrid` anche con zero risultati vettoriali; RRF solo con risultati vettoriali; keyword additivo (200, 50, 20 fino a 10 occorrenze, 5,0 e 1,0) | [C+E] |
| D15: scala RRF e score con embedding attivi | non noti |
| D20: la ricerca copre solo `wiki/**/*.md`, fino a 10.000 file, poi si ferma con messaggio su stderr e la risposta non lo segnala | [C] |
| V1, V2: quota dei vicini del grafo 0,30 senza vettori, 0,15 a finestra piena | [C] |
| V3: `vectorScore` composito, non un coseno grezzo | [C] |
| V8: `q` non restituisce i vicini | [C] |
| `images` sempre `[]`, ordine non strettamente decrescente, `content` assente senza `includeContent` | [E] soltanto: non si portano |

- Fonti: [^src: wiki/syntheses/llm-wiki-skill-vs-app-v0-6-13.md §Aggiornamenti (v2026-11-22, verifica sul codice)] [^src: wiki/concepts/llm-wiki-ricerca-e-grafo-api.md §Dettaglio] [^src: wiki/concepts/llm-wiki-api-osservazioni-esecuzione-v0-6-13.md §Osservazioni del 2026-11-13 (app 0.6.13, progetto reale, non replicate)] [^src: wiki/concepts/llm-wiki-api-locale.md §Aggiornamenti (v2026-11-21)]
- L'esempio di `/health` del README (con `version`) è completato da `LWS-TSK-014`; qui l'elenco dei campi deve già essere lo stesso in tutti i file.

## Vincoli comuni (TSK docs di contenuto)
- Prima di scrivere: `git -C code_repos/llm_wiki_skill branch --show-current` = branch condiviso; altrimenti STOP.
- Si scrive solo nei file di `code_path`; nessun file nuovo, codice o script.
- Testi della skill senza ID kanban, riferimenti a ADR, wiki o factory, attribution AI o `Co-Authored-By`; [C]/[E] solo nel TSK.
- Se la wiki non documenta un comportamento v0.6.13, la skill non lo afferma; fatti solo [E]: correzione neutra.
- Commit: non lo esegue il dev-agent; propone un messaggio generico senza ID; la sessione principale lo esegue con `tools/vcs/sm_commit.py` dopo OK esplicito. `done` solo dopo il commit; Chiusura con i tre campi (dichiarati, committati, working tree).

## Implementation Steps
1. Verifica del branch.
2. `/health`: campi `mcpEnabled`, `allowLanAccess`, `agent{...}`, `version`, risposta anche senza prefisso; stesso elenco in tutti i file.
3. `search`: `graphHits`, `queryEmbedding` nel corpo anche in `SKILL.md`, istruzione a guardare `vectorHits` e `graphHits`.
4. Semantica degli score (hybrid, RRF, keyword additivo, `vectorScore`, non confrontabili fra modalità); togliere ogni intervallo RRF universale.
5. Copertura: `wiki/**/*.md`, 10.000 file, nessuna segnalazione nella risposta. Snippet in forma neutra. Non dichiarare completo l'elenco dei campi di un risultato.
6. Controlli testuali con comando ed esito.

## Definition of Done
- [x] AC1, AC2, AC3, AC4, AC5, AC8 di LWS-US-005 verificati.
- [x] AC9: riga di evidenza per ogni affermazione cambiata.
- [x] Nessuna traccia nei file toccati.

## Chiusura
<!-- AC6 e AC7 sono di LWS-TSK-007 -->

Branch verificato prima di scrivere: `docs/align-v0-6-13`, HEAD `69dece1`, working tree pulito (`git -C code_repos/llm_wiki_skill branch --show-current`, `rev-parse --short HEAD`, `status --short`).

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-005 AC1 | verificato | Esempio del README completato dalla sessione principale su decisione dell'utente (2026-11-23), invece del rinvio a LWS-TSK-014: hunk `+#   "version": "0.6.13",` in `README.md` (esempio di `/health`, dopo `status`; valore uguale a `api-reference.md` r.32). LWS-TSK-014 lo verifica soltanto. Elenco campi identico in SKILL.md (r.83 e tabella endpoint) e api-reference.md (esempio, riferimento campi, «Additions»). Hunk: «+it returns ok, status, version, enabled, authRequired, authConfigured, allowUnauthenticated and tokenSource; app 0.6.13 adds mcpEnabled, allowLanAccess and agent (chat, streaming, streamProtocol)»; «+and also answers on /health without the prefix». README: l'esempio resta con `...` e senza `version` (LWS-TSK-014) |
| LWS-US-005 AC2 | Soddisfatto | «+Body: { "query": "...", "topK": 10, "includeContent": false, "queryEmbedding": null }» in SKILL.md (tabella endpoint); «+look at vectorHits and graphHits» in api-reference.md; «+Inspect vectorHits and graphHits (not just mode)» in SKILL.md r.100 |
| LWS-US-005 AC3 | Soddisfatto | «+hybrid can have vectorHits: 0: without embeddings it means keyword + one-hop graph neighbours, with additive keyword scores (no RRF). RRF is applied only when vectorHits > 0»; «+No numeric range is documented for RRF scores or for scores with embeddings»; «+Scores are not comparable between modes». Tolti: «small absolute numbers», «1/(60+rank)», «100×+ larger», «divided by 61», «tens to hundreds». Resta solo l'esempio JSON `"score": 0.0315...` (valore d'esempio, nessun intervallo) |
| LWS-US-005 AC4 | Soddisfatto | «+The scan covers at most 10,000 files: after that it stops and the app writes a message to its own stderr. The response has no field that reports this» (api-reference.md); «+at most 10,000 files; past that limit it stops and the response does not say so» (SKILL.md r.100, examples.md) |
| LWS-US-005 AC5 | Soddisfatto | «-~160-char window (observed ~110 chars ...)» / «+A short excerpt; its length is not fixed, so don't rely on one». Forma neutra scelta, senza numero: D14 è solo [E] (una prova, un progetto, non replicata) e un numero, anche «circa 110», sarebbe una nuova garanzia. `grep 160` senza esiti |
| LWS-US-005 AC6 | n/a | coperto da LWS-TSK-007 |
| LWS-US-005 AC7 | n/a | coperto da LWS-TSK-007 |
| LWS-US-005 AC8 | Soddisfatto | «+(for example path, title, snippet, score, titleMatch, optional vectorScore, and graphRelatedTo on graph candidates; this is not a complete list of result fields)» (SKILL.md r.100, con `images` tolto dall'elenco); «+These are the fields the skill documents, not a complete list: a result can carry other fields» (api-reference.md). Tolte tutte le frasi sull'ordine non strettamente decrescente («interleaved», «not strictly sorted»): grep senza esiti. Non si portano «images sempre vuoto» né l'ordine |
| LWS-US-005 AC9 | Soddisfatto | Tabella sotto: ogni affermazione cambiata ha la sua riga di evidenza |

### Affermazioni cambiate (AC9)

| # | File | Affermazione | Livello | Riga di evidenza |
|---|---|---|---|---|
| 1 | SKILL.md (r.83, tabella endpoint); api-reference.md | `/health`: ok, status, version, enabled, authRequired, authConfigured, allowUnauthenticated, tokenSource, più mcpEnabled, allowLanAccess, agent{chat, streaming, streamProtocol} | [E+C] parziale | D7 |
| 2 | SKILL.md (tabella endpoint) | `/health` risponde anche senza prefisso | [E+C] | D7 |
| 3 | api-reference.md (riferimento campi) | `agent`: osservati `chat: true` e `streamProtocol: "sse"`; per `streaming` nessun valore dichiarato nel riferimento | [E] | D7 (osservazioni 2026-11-08 e 2026-11-13) |
| 4 | SKILL.md (tabella endpoint); api-reference.md | `allowLanAccess` mostra l'impostazione, non l'indirizzo | coerenza con «Listen address» | sezione «Listen address» di api-reference.md (LWS-TSK-004) |
| 5 | SKILL.md (tabella endpoint); api-reference.md | `queryEmbedding` nel corpo di `search` anche in SKILL.md; guardare `vectorHits` e `graphHits`, non solo `mode` | [E+C] | D9; n. 4 |
| 6 | SKILL.md r.109; api-reference.md | RRF solo con `vectorHits > 0` | [C+E] | D15 |
| 7 | SKILL.md r.108; api-reference.md; examples.md | `hybrid` anche con `vectorHits: 0`; senza vettori il punteggio keyword è additivo | [C+E] | D15 |
| 8 | SKILL.md; api-reference.md; examples.md | nessun intervallo RRF né scala con embedding attivi; score non confrontabili fra modalità | non noti (negazione) | D15 «scala RRF e score con embedding attivi: non noti» |
| 9 | SKILL.md r.109; api-reference.md; examples.md | `vectorScore` composito, non un coseno grezzo; copiato solo con RRF applicato o per i risultati solo-vettore | [C] | V3 |
| 10 | SKILL.md; api-reference.md; examples.md | copertura: solo `wiki/**/*.md`, fino a 10.000 file, poi si ferma con messaggio su stderr; nessun campo nella risposta lo segnala; quali file restino fuori non è definito | [C] | D20 |
| 11 | api-reference.md (campi del risultato) | snippet: lunghezza non fissa, nessun numero | [E] soltanto: forma neutra | D14 |
| 12 | SKILL.md r.100 e tabella endpoint; api-reference.md | l'elenco dei campi di risposta e di risultato non è completo | negazione di completezza, nessuna nuova garanzia | D15, §Aggiornamenti della sintesi: «campi di ogni risultato di search» ristretti, non elencati per intero |
| 13 | SKILL.md; api-reference.md; examples.md | rimossi «divided by 61», «100×+ larger», «1/(60+rank)», «tens to hundreds», «small absolute numbers» | rimozione di affermazioni senza evidenza nella wiki | D15 (scala RRF non nota); i valori additivi osservati non fissano un intervallo |
| 14 | SKILL.md; api-reference.md; examples.md | rimosse le frasi su graph candidates «interleaved» e lista «not strictly sorted by score» | [E] soltanto: non si porta | riga «ordine non strettamente decrescente» della tabella del TSK |

### Ricerche testuali

Cartella `code_repos/llm_wiki_skill`, file SKILL.md api-reference.md examples.md README.md.

| Comando | Esito |
|---|---|
| `grep -nE "160"` | 0 righe |
| `grep -nE "interleav\|strictly\|divided by\|100×\|61\|1/\(60"` | 0 righe |
| `grep -nE "0\.0[0-9]"` | 1 riga: `"score": 0.0315136476426799` (esempio JSON, api-reference.md r.266), nessun intervallo |
| `grep -nE "RRF"` | tutte le righe dicono «RRF solo con vectorHits > 0» o «nessun intervallo documentato»; nessun intervallo universale |
| `grep -nE "graphHits"`, `"vectorHits"`, `"queryEmbedding"` | `queryEmbedding` ora anche in SKILL.md r.171; `graphHits` in SKILL.md, api-reference.md, examples.md, README.md |
| `grep -nE "mcpEnabled\|streamProtocol"` | SKILL.md r.83 e r.167; api-reference.md (esempio, riferimento campi, «Additions») |
| `grep -nE "allowLanAccess"` | coerente con «Listen address»: mostra l'impostazione, non l'indirizzo (SKILL.md r.75 e r.167, api-reference.md, README.md) |
| `grep -nE "10000\|10,000\|10\.000"` | 10,000 file di ricerca in SKILL.md r.100 e r.171, api-reference.md, examples.md; gli altri 10000 sono i limiti di `files` |
| `grep -nE "wiki/\*\*"` | copertura della ricerca nei tre file; le altre righe sono allow-list, grafo, scan, avvertenza sulle modifiche dirette |
| `grep -nE "images"` | 2 righe in api-reference.md (esempio JSON e tabella dei campi); nessuna «sempre vuoto» |
| `git diff -U0 \| grep '^+' \| grep -E "LWS\|TSK\|US-\|EP-\|ADR\|[Ff]actory\|Claude\|Anthropic\|Co-Authored\|Q_[0-9]"` | 0 righe |

### Diff di chiusura (a comando)

| Campo | Valore |
|---|---|
| Dichiarati | `code_repos/llm_wiki_skill/SKILL.md`, `api-reference.md`, `examples.md`, `README.md` (riga `version`, aggiunta dalla sessione principale); questo TSK (`status`, `started_at`, Chiusura) |
| Committati | `460d634` nel repo della skill (4 file, 37+/24-), dopo OK esplicito dell'utente in chat (2026-11-23); `sm_commit.py --dry-run` → messaggio invariato; `git log -1` senza trailer né attribution. Dopo il commit `git status --short` della skill vuoto. Punti dubbi 1-3: lasciati come sono; punto 4 (`examples.md` r.179, inferenza su `vectorScore`) rinviato a LWS-TSK-016, decisione dell'utente |
| Working tree | skill (`git -C code_repos/llm_wiki_skill status --short`): ` M SKILL.md`, ` M api-reference.md`, ` M examples.md`. Factory (`git status --short`): ` m code_repos/llm_wiki_skill` (puntatore), questo TSK, `?? DOSSIER-llm-wiki-qualita-ingest.md` (già presente prima del lavoro) |

README.md non toccato dal dev-agent. Superato: la sessione principale ha aggiunto la riga `version` all'esempio di `/health` su decisione dell'utente (vedi AC1 e «Dichiarati»); LWS-TSK-014 la verifica soltanto.

## Dependencies
- LWS-TSK-005 — serializzazione per sovrapposizione di file.

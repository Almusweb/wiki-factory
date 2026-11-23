---
id: LWS-TSK-015
title: "Verifica di coerenza fra i quattro file della skill sui termini toccati da 003..007"
us: LWS-US-009
sprint: 02
layer: docs
consumer: agent
priority: P1
estimate: S
status: done
depends_on: [LWS-TSK-014]
blocked_by: []
code_path: ["code_repos/llm_wiki_skill/SKILL.md", "code_repos/llm_wiki_skill/api-reference.md", "code_repos/llm_wiki_skill/examples.md", "code_repos/llm_wiki_skill/README.md"]
target: llm_wiki_skill
started_at: 2026-11-23
closed_at: 2026-11-23
decision_refs: []
---

# LWS-TSK-015 — Verifica di coerenza interna

## Context
Controllo di chiusura per n. 2, 3, 4, 5, 8, 9, 10: gli stessi termini devono avere lo stesso significato in tutti i punti dei quattro file. Gli unici interventi ammessi sono correzioni di coerenza con evidenza già in wiki; altrimenti la frase si toglie. [^src: management/kanban/LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-009-coerenza-interna-e-versione/LWS-US-009.md §Acceptance Criteria]

## Technical Specs
- **Layer docs, consumer agent, target `llm_wiki_skill`.** Branch condiviso.
- **Termini da verificare** (per le storie di contenuto, TSK 004..010): CORS, localhost, 404, 405, 501, «sola lettura», `hybrid`, «scrittura». Per ciascuno: ricerca testuale su tutti e quattro i file e confronto dei significati.
- Per ogni correzione: riga di evidenza ([C]/[E]/[C+E]) già presente nelle tabelle dei TSK 004..010; senza riga, la frase si toglie.
- Licenza e rotazione del token non si toccano; valori di `status` di `/health` restano i quattro noti.
- Fonti: [^src: wiki/entities/llm-wiki-skill.md §Incoerenze interne della skill (materiale per la PR)]

## Vincoli comuni (TSK docs di contenuto)
- Prima di scrivere: `git -C code_repos/llm_wiki_skill branch --show-current` = branch condiviso; altrimenti STOP.
- Si scrive solo nei file di `code_path`; nessun file nuovo, codice o script.
- Testi della skill senza ID kanban, riferimenti a ADR, wiki o factory, attribution AI o `Co-Authored-By`; [C]/[E] solo nel TSK.
- Se la wiki non documenta un comportamento v0.6.13, la skill non lo afferma.
- Commit: solo se il TSK produce modifiche; lo esegue la sessione principale con `tools/vcs/sm_commit.py` dopo OK esplicito, messaggio generico senza ID. Se non ci sono modifiche, la Chiusura lo dichiara (nessun commit). `done` solo dopo il commit o la dichiarazione di assenza di modifiche.

## Implementation Steps
1. Verifica del branch.
2. Per ogni termine: ricerca testuale nei quattro file (comando ed esito per ciascuno) e tabella dei significati trovati.
3. Correggere le divergenze o togliere le frasi senza evidenza.
4. Ripetere le ricerche dopo le correzioni.
5. Controllo di non-traccia (ID kanban, factory, attribution AI) sui file toccati.

## Definition of Done
- [x] AC5 di LWS-US-009 verificato: stesso significato in tutti i punti, comandi ed esiti nella Chiusura.
- [x] AC7: riga di evidenza per ogni affermazione cambiata.
- [x] Nessuna traccia nei file toccati.

## Chiusura

**Diff di chiusura** (tre campi distinti; «Working tree» è lo stato prima del commit)
- Dichiarati: `code_repos/llm_wiki_skill/SKILL.md`, `code_repos/llm_wiki_skill/examples.md`; questo TSK (`status`, `started_at`, Chiusura).
- Committati: `fd8a5a4` nel repo della skill (2 file, 3+/1-), dopo OK esplicito dell'utente in chat (2026-11-23); `sm_commit.py --dry-run` → messaggio invariato; `git log -1` senza trailer né attribution. Dopo il commit `git status --short` della skill vuoto. Factory: commit con `git commit --only` su questo TSK, `wiki/log.md`, `sprint.md` (rigenerato da una copia di `HEAD` più questo TSK) e il puntatore.
- Punti dubbi (decisione dell'utente, 2026-11-23): regola di drift in `SKILL.md` aggiunta; «(verified on 0.6.13)» tenuto; `SKILL.md` r.220 e «mutates state» lasciati. Residuo nuovo per LWS-TSK-016: `api-reference.md` r.525 («The old rule … does not hold on 0.6.13»).
- Working tree, skill (`git -C code_repos/llm_wiki_skill status --short`, `diff --stat`; branch `docs/align-v0-6-13`, HEAD `9c2669e`): ` M SKILL.md`, ` M examples.md` (2 file, 3 inserzioni, 1 cancellazione). `README.md` e `api-reference.md` non toccati.
- Working tree, factory (`git status --short`): `m code_repos/llm_wiki_skill` (puntatore, atteso) e questo TSK. ` M .../TSK-030.md`, ` M management/kanban/sprint.md`, `?? DOSSIER-llm-wiki-qualita-ingest.md` e i `?? .../EP-003-*/TSK-033..044` sono di altre sessioni, non toccati. Nessun file in stage (`git diff --cached --name-only` vuoto).
- Fini riga: `grep -c $'\r'` = 0 sui quattro file della skill (LF mantenuto). Controllo di non-traccia sui file toccati (`TSK|LWS|ADR|wiki-factory|Co-Authored|Anthropic|\[C\]|\[E\]|factory`, SKILL.md ed examples.md): nessuna riga.

**Ricerche e tabelle dei significati** (cartella `code_repos/llm_wiki_skill`; `grep -n -i -E` sui quattro file; i numeri di riga di `SKILL.md` sono quelli dopo la modifica, +2 dopo r.84)

| Termine (comando) | Righe trovate (README / SKILL / api-reference / examples) | Significato trovato | Esito |
|---|---|---|---|
| CORS (`CORS\|Access-Control\|preflight`) | 132 / 207 / 522, 523, 525 / nessuna | `Origin` riflesso solo per estensioni, `localhost`, `127.0.0.1`, `[::1]`, Tauri; altre origini senza header ma servite; CORS non è controllo d'accesso; `OPTIONS` → 204 prima di ogni altro controllo | coerente |
| localhost (`localhost\|127\.0\.0\.1\|0\.0\.0\.0\|\[::1\]`) | 53, 71, 87, 93, 97, 106, 119, 132 / 3, 40, 63, 75 / 3, 522, 531, 534, 535 / nessuna | due usi: origine ammessa da CORS (README 132, api-ref 522) e indirizzo di ascolto predefinito `127.0.0.1`, `0.0.0.0` con `allowLanAccess`, `LLM_WIKI_BIND_HOST` prima (README 119, SKILL 75, api-ref 531-535); i due usi non si contraddicono | coerente |
| 404 (`404`) | nessuna / 125, 144, 206 / 150, 152, 228, 232, 525 / 22 | progetto sconosciuto o nome progetto come `{id}`; rotta sconosciuta; verbo sbagliato fra GET, POST, PATCH, DELETE; file inesistente | coerente |
| 405 (`405`) | nessuna / 207 / 525 / nessuna | solo per verbi fuori da GET, POST, PATCH, DELETE (es. `PUT`); `OPTIONS` mai 405 | coerente |
| 501 (`501`) | nessuna / nessuna / nessuna / nessuna | assente: tolto da LWS-TSK-009 | coerente (0 risultati, exit 1) |
| «sola lettura» (`read-only\|read only\|not read-only`) | 38 / 3, 193, 220 / 34 / 175, 291 | letture di default; le rotte che cambiano stato solo su richiesta esplicita; una chiamata di review, rescan o embed su un id non corrente non è di sola lettura; per `pages/write` e `chat` non è noto. r.3 di SKILL è la descrizione del trigger (non una regola) | coerente |
| `hybrid` (`hybrid`) | 136 / 110, 112 / 269, 273, 303, 305 / 47, 51, 60 | `mode` è `hybrid` se `graphHits > 0` (anche con `vectorHits: 0`) o se keyword e vettori hanno trovato; RRF solo con `vectorHits > 0`; con `topK < 2` `mode` è `keyword` | coerente |
| «scrittura» / write (`writes?\|written\|rewrite\|mutates\|changes? state`) | 38, 61, 126 / 81, 178-183, 188, 190, 193, 203, 208, 220 / 20-34, 259, 397, 445, 456, 471-493, 508, 563 / 161, 186, 291, 297 | elenco delle rotte che cambiano stato identico in README 38 e 126, SKILL 188 e 193, api-ref 22-34, examples 297: `sources/rescan`, review `PATCH`/`DELETE`/`resolve`, `pages/write`, `pages/embed`, `chat`; `pages/write` e `pages/embed` sempre con token; «Writes» (review, `pages/write`) e «Changes state» (embed, rescan, `chat`) indicano la stessa classe | coerente |

Dopo le correzioni le stesse ricerche sono state rilanciate: stessi esiti; unica differenza lo spostamento di riga in `SKILL.md` e la riga di drift (r.85) e l'intestazione `examples.md` r.173, che non contengono i termini cercati tranne «0.6.13».

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-009 AC5 | soddisfatto | Tabella sopra: per ognuno degli otto termini i quattro file danno lo stesso significato; nessuna divergenza da correggere e nessuna frase da togliere. 501: 0 risultati. Ricerca finale `grep -n -i -E` rilanciata dopo le due modifiche |
| LWS-US-009 AC7 | soddisfatto | Tabella «Affermazioni cambiate» sotto: due righe, ciascuna con evidenza |

**Affermazioni cambiate (AC7)**

| File:riga (dopo la modifica) | Affermazione cambiata | Livello | Evidenza (TSK di origine) |
|---|---|---|---|
| `SKILL.md`:85 | aggiunta la regola di drift: confrontare `version` di `/health` con `0.6.13`; per qualunque altra versione controllare `api-reference.md` | intra-skill (decisione dell'utente, 2026-11-23) | stessa regola in `README.md`:140 (LWS-TSK-014, AC4); LWS-US-009 Business Rules, decisione N3 |
| `examples.md`:173 | intestazione «(0.6.13)» → «(verified on 0.6.13)» | editoriale: stessa informazione, senza storia delle versioni | `README.md`:138 «Verified on 0.6.13» (LWS-TSK-014, AC2); marcatori «0.6.13.» sulle route lasciati (decisione dell'utente) |

**Scelta sulla regola di drift (punto 1).** Aggiunta in `SKILL.md` perché è il file che l'agente carica: il README non viene letto in esecuzione, quindi la regola nel solo README non avrebbe effetto. Una riga, identica nel significato al README; nessun fatto nuovo.

**Punti dubbi (non toccati)**
- `SKILL.md` r.220: «The routes that change state ..., `pages/embed` and `chat`» ripete rotte già nell'elenco; il significato non cambia, la formula viene da LWS-TSK-009 (AC5). Raccomandazione: lasciare.
- `api-reference.md` r.525 «The old rule "every verb except GET and POST gives 405" does not hold on 0.6.13» e r.296 (riferimenti `commands/search.rs`): residui per LWS-TSK-016 (storia delle versioni e riferimenti a righe di codice).
- «Mutates state» (`api-reference.md` r.397) contro «Changes state» altrove: stesso significato, differenza di parola; non cambiato (nessuna affermazione da correggere).
- Residui già assegnati a LWS-TSK-016, non toccati: «labelled "API Server" in older builds» (`README.md` r.55, `SKILL.md` r.80), «shorter than older docs stated» (`api-reference.md` r.326), riferimenti a righe di codice, inferenza su `vectorScore` in `examples.md` r.179.

## Dependencies
- LWS-TSK-014 — ultima modifica di contenuto prima della verifica.

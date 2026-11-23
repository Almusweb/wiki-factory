---
id: LWS-TSK-016
title: "Audit locale pre-PR: non-traccia, elementi non trasferibili, evidenza per ogni frase e bozza della descrizione"
us: LWS-US-010
sprint: 02
layer: docs
consumer: agent
priority: P1
estimate: M
status: done
depends_on: [LWS-TSK-015]
blocked_by: []
code_path: ["code_repos/llm_wiki_skill/SKILL.md", "code_repos/llm_wiki_skill/api-reference.md", "code_repos/llm_wiki_skill/examples.md", "code_repos/llm_wiki_skill/README.md"]
target: llm_wiki_skill
started_at: 2026-11-23
closed_at: 2026-11-23
decision_refs: []
---

# LWS-TSK-016 — Audit locale pre-PR

## Context
Prima del push, il diff del branch condiviso rispetto a `main` deve essere pulito e verificabile: nessuna traccia della factory, nessun elemento non trasferibile della bozza, ogni frase cambiata con una riga di evidenza. È l'unico presidio di qualità di questa epica (CQRL esclude il layer `docs`). Solo operazioni locali: nessun fetch, push o PR. [^src: management/kanban/LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-010-preparare-la-pr-upstream/LWS-US-010.md §Acceptance Criteria] [^src: wiki/purpose.md §Pull request upstream]

## Technical Specs
- **Layer docs, consumer agent, target `llm_wiki_skill`.** Branch condiviso. Può modificare i quattro file solo per **togliere** frasi senza evidenza o tracce trovate.
- **Controlli:**
  1. Diff contro `main`: `git -C code_repos/llm_wiki_skill diff --name-status main..HEAD` → solo i quattro file esistenti, nessun file nuovo, nessun codice.
  2. Non-traccia nel diff e nei messaggi dei commit già fatti: pattern di `tools/vcs/ai_policy.py` (fonte unica, non ridefiniti) per attribution AI e ID kanban (`EP-`, `US-`, `TSK-`, `LWS-`), più ricerca di riferimenti a ADR, wiki, factory e `Co-Authored-By`.
  3. Elementi non trasferibili della bozza (stessa ricerca di `LWS-TSK-002`): `[obs]`/`[code]`, `FORK.md`, avvisi di fork, task interni, percorsi locali reali, dati di un progetto reale con data; nomi del progetto reale o dell'utente.
  4. Audit delle affermazioni: per ciascuna frase cambiata, riga di evidenza [C]/[E]/[C+E] raccolta dalle Chiusure di LWS-TSK-002..015; quelle senza riga sono tolte; elenco delle scartate **senza dati del progetto reale**.
  5. Nessuna fase B (estensioni personali) nel diff.
- **Bozza della descrizione PR:** generica, in un blocco della Chiusura, **senza** ID kanban né riferimenti alla factory; dichiara la base di verifica (lettura del codice sorgente dell'app alla v0.6.13 e alcune risposte verificate su un'app in esecuzione) e l'elenco dei punti non verificati lasciati invariati (EP §Cosa resta fuori dalla PR se non verificato e residui di LWS-US-008).
- Nessun commit, push o PR da questo TSK. Se l'audit toglie frasi, il commit di correzione lo esegue la sessione principale dopo OK esplicito con `tools/vcs/sm_commit.py`, messaggio generico senza ID.
- Fonti: [^src: wiki/entities/llm-wiki-skill-bozza-alm-wiki.md §Elementi non trasferibili a una PR upstream] [^src: wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md §Che cosa resta da verificare]

## Vincoli comuni
- Prima di operare: `git -C code_repos/llm_wiki_skill branch --show-current` = branch condiviso; altrimenti STOP.
- Nessun file nuovo, codice o script; testi senza ID, riferimenti a ADR/wiki/factory o attribution AI.

## Implementation Steps
1. Verifica del branch e del diff per nome file.
2. Esecuzione dei controlli 2 e 3 con comandi ed esiti.
3. Audit delle affermazioni: tabella `affermazione | livello | hunk | TSK di origine`.
4. Togliere le frasi senza evidenza; ripetere i controlli 2 e 3.
5. Scrivere la bozza della descrizione PR (senza ID né riferimenti alla factory) e verificarla con gli stessi pattern.

## Definition of Done
- [x] AC1, AC2, AC3, AC4, AC5, AC7 di LWS-US-010 verificati con comando ed esito.
- [x] Nessun commit, push o PR eseguito da questo TSK (il commit di correzione `f6a99c7` è della sessione principale dopo OK, come prescritto dalle Technical Specs).

## Chiusura
<!-- AC6 è di LWS-TSK-017 e LWS-TSK-018 -->

Branch verificato prima di scrivere: `git -C code_repos/llm_wiki_skill branch --show-current` → `docs/align-v0-6-13`; HEAD `fd8a5a4`; `git merge-base main HEAD` → `642b438` (= `main`); 11 commit sopra `main`; working tree pulito. Fini riga: LF (`0` CR nei quattro file, prima e dopo le modifiche; `core.autocrlf=true` avvisa solo sulla copia di lavoro). Le modifiche di questo TSK sono **non committate** (in attesa di OK): gli esiti sotto valgono per il working tree contro `main` e valgono per il commit dopo l'OK.

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-010 AC1 | verificato | `git -C code_repos/llm_wiki_skill diff --name-status main` → `M` su `README.md`, `SKILL.md`, `api-reference.md`, `examples.md`, nessun altro; `git ls-files --others --exclude-standard` vuoto (nessun file nuovo); `git diff --name-status main..HEAD` (solo commit) identico. Branch dedicato `docs/align-v0-6-13` con base `642b438` = `main`. |
| LWS-US-010 AC2 | verificato | Pattern importati da `tools/vcs/ai_policy.py` (`find_factory_ids` con `FACTORY_ID_RE`, che copre `TSK-`, `US-`, `EP-` e il prefisso `LWS-TSK-`; `is_ai_attribution` con `co-authored-by`, `generated with/by`, `claude`, `anthropic`), senza ridefinirli, con uno script nello scratchpad: righe aggiunte di `git diff main` (931 righe, 372 aggiunte) → `hits 0`; `git log main..HEAD --format=%B` (22 righe, 11 commit) → `hits 0`; bozza della descrizione PR → `hits 0`. Ricerca aggiuntiva sulle righe aggiunte: `grep -n -i -E '\bADR\b\|wiki-keeper\|wiki-factory\|factory\|kanban\|Co-Authored\|Generated (with\|by)\|Anthropic\|Claude\|raw/20\|\[\^src\|\[C\]\|\[E\]\|\[obs\]\|\[code\]\|Q_[0-9]\|sprint\|code_repos\|dossier\|\bLWS\b\|\bTSK\b\|\bUS-\|\bEP-'` → nessuna riga. `git log main..HEAD --format='%an'` → un solo autore, l'identità git dell'utente (metadato del commit, non testo del diff). |
| LWS-US-010 AC3 | verificato | `grep -n -E 'FORK\|[Ff]ork\|task 0\|Alessandro\|Musio\|Almusweb\|accenture\|alm-wiki\|local_git\|knowledge/\|Values seen\|real wiki\|seen once\|1794168986046\|review-1a2b3c4d\|e08cfce\|[0-9]{4}-[0-9]{2}-[0-9]{2}\|\b(122\|102\|82)\b'` sulle righe aggiunte → nessuna riga (nessuna data, punteggio d'esempio, id di review o hash di commit). `[obs]`/`[code]` e `[C]`/`[E]` assenti (ricerca sopra). `C:/Users/me/...` e `/Users/me/...` sono segnaposto (`me`), già in `main` o in esempi con utente segnaposto. |
| LWS-US-010 AC4 | verificato | Tabella dell'audit sotto; 31 gruppi di frasi tolte o ridotte in questo TSK, elenco sotto senza dati del progetto reale. Dopo le correzioni ogni frase cambiata contro `main` ha una riga, o è stata tolta. |
| LWS-US-010 AC5 | Verificato | Bozza della descrizione PR sotto: generica, in inglese, senza ID né riferimenti alla factory (stessi pattern: `hits 0`; `grep` sui termini factory/ID: nessuna riga); dichiara la base di verifica e i punti non verificati lasciati invariati. |
| LWS-US-010 AC7 | Verificato | Il diff tocca solo i quattro file esistenti; `grep -n -i -E 'develop\|personal\|custom extension\|fase B\|phase B'` sulle righe aggiunte → nessuna riga; nessuna estensione personale, nessun file `FORK.md`. |

### Controlli eseguiti (comando ed esito)
1. `git -C code_repos/llm_wiki_skill diff --name-status main` → 4 file `M` (vedi AC1).
2. Script `check2.py` (scratchpad, importa `ai_policy`): `diff` → `hits 0`; `log` → `hits 0`; `file` sulla bozza PR → `hits 0`.
3. Ricerche testuali sulle righe aggiunte di `git diff main` (AC2, AC3, AC7): nessuna riga. Ricerca dei residui (`older builds\|older docs\|old rule\|in older\|API Server\|[a-z_]+\.(rs\|ts) [0-9]\|[0-9]+-[0-9]+\)`) → solo «API server enabled» (titolo originale del README) e il messaggio «API server is busy»; nessun numero di riga di codice.
4. Audit: tabella sotto, costruita dalle Chiusure di LWS-TSK-002..015, dalla tabella delle osservazioni (`llm-wiki-api-osservazioni-esecuzione-v0-6-13`), da `llm-wiki-ricerca-e-grafo-api`, `llm-wiki-sincronizzazione-file`, `llm-wiki-pipeline-ingest`, `llm-wiki-review-store-e-auto-save`, `llm-wiki-api-locale`, `llm-wiki-skill-vs-app-v0-6-13` e dal raw di verifica sul codice.
5. Nessuna fase B (AC7).

### Audit delle affermazioni (stato finale contro `main`)
Livelli: [C] letto nel codice; [E] osservato, una prova su un progetto; [C+E] entrambi; «decisione» = decisione dell'utente dell'epica; «intra» = coerenza interna della skill. Le sigle D/V/n. sono quelle dell'epica.

| Affermazione | Livello | Hunk | TSK di origine |
|---|---|---|---|
| `description`: «Read-only by default, writes only on the user's explicit request»; resto invariato | decisione | `SKILL.md` frontmatter | 003 |
| Dichiara 0.6.13 come versione documentata e la base di verifica; regola di drift (versione di `/health` diversa da 0.6.13) | decisione (N3) | `README.md` §Version; `SKILL.md` §Auth model | 014, 015 |
| «four markdown files»; `--skill llm-wiki`; «three forms» più il nome risolto lato client; esempi di `/health` | intra | `README.md`, `SKILL.md` §Project resolution | 014 |
| Ascolto su `127.0.0.1` di default, `allowLanAccess` → `0.0.0.0`, `LLM_WIKI_BIND_HOST` ha la precedenza, valutato al bind, `/health` mostra l'impostazione; stesso schema di auth e token in chiaro su LAN | [C] | `README.md` §Prerequisites e §Security model; `SKILL.md` §Auth model; `api-reference.md` §Listen address | 004 |
| CORS a elenco di origini, nessun `*`; altre origini servite senza header; CORS non è controllo d'accesso; `Max-Age: 600`; `OPTIONS` → 204 prima di ogni controllo | [C+E] | `README.md` §Security model; `api-reference.md` §Limits & defenses | 004, 008 |
| Con `allowUnauthenticated` restano aperte `projects`, `files`, `files/content`, `reviews`, `search`, `graph`, `sources/rescan`; `chat`, cancel, `pages/embed`, `pages/write` sempre con token | [C] | `README.md`; `SKILL.md`; `api-reference.md` §Auth | 004 |
| Sezione «API + MCP»; `?token=` ultima risorsa | [C] | tutti e quattro | 003, 004 |
| `/health`: `version`, `mcpEnabled`, `allowLanAccess`, `agent`; risponde anche senza prefisso; `agent.chat` e `streamProtocol` osservati | [E+C] | `SKILL.md`, `api-reference.md` §health | 006 |
| `Content-Type: application/json` (senza `charset`) | [E] correzione neutra (D13) | `api-reference.md` r.5 | 005 |
| `currentProject` solo in `/projects`; lista con più progetti; `current` = progetto con `current: true` impostato dalla UI | [E+C] / [C] parziale (D17, V25) | `SKILL.md`, `api-reference.md` §projects, `examples.md` | 005 |
| `{id}` come percorso: `/` come `%2F`, due punti non separatori, `%XX` decodificato, `+` spazio, `?` chiude; su Windows senza distinzione di maiuscole e `\` accettato; nome progetto → 404 | [C] parziale (V10, V11); 404 [E] | `SKILL.md`, `api-reference.md`, `examples.md` | 005 |
| `files`: `path` assoluto (su Windows `//?/C:/...`); 413 oltre `maxFiles`; nessuna affermazione su `truncated`; alias `raw`, `raw/sources` | [E+C] (correzione dell'esempio originale; n. 2, n. 5) | `SKILL.md`, `api-reference.md`, `examples.md`, `README.md` | 005 |
| `files/content`: estensioni leggibili, `rtf` → 415; ordine dei controlli; 400 senza `path` | [C] (D18, V12) | `SKILL.md`, `api-reference.md` | 005 |
| `search`: guardare `vectorHits` e `graphHits`; solo `wiki/**/*.md`, fino a 10.000 file, nessun segnale nella risposta; campi non elencati per intero | [C] (D20) / negazione | `SKILL.md`, `api-reference.md`, `examples.md` | 006 |
| Scala dello score da `vectorHits`; pesi 200/50/20(max 10)/×5/×1; RRF solo con `vectorHits>0`; nessun intervallo RRF documentato; `vectorScore` composito, copiato solo con RRF o per i soli vettori | [C+E] (D15, V3, V4) | `SKILL.md`, `api-reference.md` §Retrieval mode, `examples.md` | 006 |
| `mode` = `hybrid` con `graphHits>0` anche con `vectorHits:0`; vicini 15–30% di `topK` (30% senza vettori; 0 con `topK<2`); snippet «Graph neighbor of»; `graphRelatedTo` esiste sui candidati | [C+E] (D9, D15); `graphRelatedTo` [E] (solo esistenza) | idem | 006 |
| Snippet: «lunghezza non fissa», nessun numero | [E] forma neutra (D14) | `api-reference.md` §result fields | 006 |
| `content` assente (non `null`) senza `includeContent` | [E] correzione dell'esempio (obs. 6) | `SKILL.md`, `api-reference.md` | 006 |
| Grafo: `offset`, `limit` (assente 200; clamp 1–1000; 0, negativo e non numerico → 400), `totalCount`, `hasMore`, `edgeScope`; `q` solo nodi; `nodeType` insieme aperto, prima riga `type:`, minuscolo; `type: query` non è nodo; archi anche da `related:`, link ambiguo scartato | [C+E] / [C] (D10, D16, D19, V6-V8) | `SKILL.md`, `api-reference.md`, `examples.md` | 007 |
| Cache del grafo di 5 s | [C] solo da raw api-mcp, non provata; lasciata, dichiarata come non verificata nella PR | `SKILL.md`, `api-reference.md` | 007 |
| Semantica di `totalCount` e `hasMore` | non letta nel codice; campi osservati [E+C] parziale; dichiarata non verificata nella PR | `api-reference.md` §graph | 007 |
| 405 solo fuori da GET, POST, PATCH, DELETE (dopo il token); verbo sbagliato fra i quattro → 404; senza token 401 anche su rotte e metodi sbagliati | [C+E] (D11); 401 [E] forma neutra | `SKILL.md` §errori, `api-reference.md` §Methods | 008 |
| Rate limit 120 per finestra di 1 s, `/health` e `OPTIONS` esclusi, prima del token; 64 in volo, 8 stream chat, 4 embed; corpo `chat` 40 MiB, `pages/write` circa 12 MiB, generico 1 MiB senza codice noto; nessun `Retry-After` noto; attese 1 s e 2 s = prudenza dell'agente; non provato sotto carico | [C]; 429 e 503 non provati | `README.md`, `SKILL.md`, `api-reference.md` §Limits, `examples.md` | 008 |
| Elenco delle rotte che cambiano stato; postura «solo su richiesta esplicita»; review, rescan, embed agiscono sul progetto in `{id}` | [C] + decisione (D1, D21, V19) | `README.md`, `SKILL.md`, `api-reference.md` §Routes that change state, `examples.md` | 009 |
| `reviews` GET (campi, `status`, `type`); `PATCH`, `DELETE`, `resolve` riscrivono `review.json` del progetto in `{id}`; corpi non documentati | lettura [E+C] (D3); scritture [C] | `SKILL.md`, `api-reference.md` | 009, 010 |
| Id delle review FNV-1a 32 bit su `tipo::titolo normalizzato`; auto-resolve a coda svuotata (`auto-resolved`, `llm-judged`) | [C] (confermate) | `api-reference.md` §reviews | 010 |
| `pages/write`: contratto 409, 400, 500, `allowOverwrite`, corpo ~12 MiB; `pages/embed`: 400 senza embedding, 503 con 4 in volo; `chat`: JSON o SSE (`meta`, `agent`, `done`, `cancelled`, `error`), token sempre; cancel: route esistente, verbo e esito non documentati | [C] contratto | `SKILL.md`, `api-reference.md` | 009 |
| `changedTasks` vuoto = già visto; il rescan non accoda l'ingest dell'app; solo `created` e `modified` lo avviano; condizioni `enabled`, `autoIngest`, LLM; «Watch all projects» e progetto non aperto: non documentati; scope del rescan anche `wiki/**/*.md`, `purpose.md`, `schema.md`; `sourceWatchConfig` per UUID poi `default` | [C] parziale | `SKILL.md`, `api-reference.md`, `examples.md`, `README.md` | 010, 014 |
| Chiave della cache di ingest senza `schema.md`, `purpose.md`, modello | [C] confermata | `api-reference.md`, `examples.md` | 010 |
| Ricetta «What is waiting for my review?»; anti-pattern sulle rotte che cambiano stato | [E+C] lettura / decisione | `examples.md` | 010, 009 |
| Esempio con grafo scaricato e filtrato lato client (`q` solo nodi); dialogo con `graphHits` | [C] derivato da V8 | `examples.md` | 007 |

### Frasi tolte o ridotte in questo TSK (senza dati del progetto reale)
Regola: «senza evidenza → si toglie; storia delle versioni → si toglie».

`README.md`
- «the section was called "API Server" in older builds» (storia delle versioni, nessuna evidenza).
- Etichetta di interfaccia dell'opzione di rete locale: l'unico riscontro è una dichiarazione del maintainer in una issue chiusa (v0.5.4), non la lettura del codice 0.6.13; resta `allowLanAccess` (fatto [C]).
- «Unchanged sources hit the ingest cache»: la verifica dice che un hit richiede anche che i file scritti esistano ancora e non ha letto cosa passano i chiamanti come testo.

`SKILL.md`
- «labelled "API Server" in older builds and in some messages» (storia, nessuna evidenza).
- `graphRelatedTo: [titles]`: solo l'esistenza del campo è osservata; il contenuto non ha riga.
- `node_type` ignorato e `nodeType` ignoto → 0 nodi: solo [E], nessuna frase originale da correggere.
- `limit` ignorato in `search`: solo [E], idem.
- «directories» fra i casi di 403: solo [E].
- «The graph does not depend on embeddings»: nessuna riga (la verifica non l'ha letto).

`api-reference.md`
- `/health` risponde anche a `POST`: solo [E], idem.
- «Paths use forward slashes on Windows»: nessuna riga.
- `files`: `root` (400, «4 entries», «no container node»), `recursive` (`size` e `children` `null`, ogni valore ≠ `false` è vero), `maxFiles` (`0` → 1, non numerico → default, testo del messaggio 413): solo [E] (obs. 1 e 2) e senza frase originale smentita; ripristinate le tre righe originali.
- `files/content`: testo del 400, «message includes the OS error text» del 404, `403` per `..` codificato, directory e `path=` vuoto: solo [E].
- `search`: messaggio `"query is required"`, «missing or non-string → 400», `topK` `0` → 1 e negativo/non numerico → 400, `includeContent` solo booleano, vettore di dimensione errata ignorato, `limit` ignorato: nessuna riga, o solo [E]; ripristinate le righe originali.
- Testo della `note` nell'esempio di risposta: il testo nuovo non ha riga (la wiki dice solo «testo cambiato»); ripristinato l'originale.
- Numeri di riga di codice (`commands/search.rs` 464, 541-551, 782-792; `search.rs` 14-20, 960-970; `file_sync.rs` 339-362, `project-file-sync.ts` 62-66 e 337-370, `source-lifecycle.ts` 258-285): tolti i numeri, lasciati i nomi dei file (letti dalla verifica).
- Punto elenco «Embeddings only affect search …; the `/graph` endpoint does not use them»: la parte sul grafo non ha riga.
- Snippet: «observed shorter than older docs stated, with a trailing `...`, frontmatter text included, newlines flattened» (storia più dettagli solo [E]).
- `graphRelatedTo`: «Titles of the hits …» → «Present on graph candidates».
- `nodeType`: «Exact match … `node_type` (snake_case) is ignored» e «on purpose».
- «there is no indexing state and embeddings play no part».
- Punto elenco sul watcher («Files written into `raw/sources/` … picked up by the app's own watcher, without any rescan»): voce V21, esclusa dalla verifica e dall'epica («non portate»).
- Cache di ingest: «An unchanged source is **not** ingested again … hash of the extracted text … re-queuing from the UI hits the same cache» ridotto al solo fatto verificato (chiave senza `schema.md`, `purpose.md`, modello).
- «Ingest progress is visible only in the desktop UI … `.llm-wiki/ingest-queue.json` …»: esito «non conclusivo» della verifica.
- «The old rule "every verb except GET and POST gives 405" does not hold on 0.6.13» (storia delle versioni).
- `reviews`: valori predefiniti di `status` e di `limit` («default 200, clamped to 1-1000»), «Fields are present only if stored», «`searchQueries` may be missing», «(ms)»: nessuna riga; «the same review from a re-ingest merges into the existing item, and a resolved item stays resolved»: la wiki lo dà come deduzione non testata.

`examples.md`
- «Often no rescan is needed: … the app's watcher picks up files …» (V21).
- Paragrafo «An **unchanged** source is never ingested again …»: ridotto alla sola frase verificata sulla chiave della cache.
- Anti-pattern «Don't edit `wiki/**` behind the app's back … skip merge, ingest cache and file history … the app's watcher sees them»: V21 e inferenza; **ripristinata la frase originale upstream** (non toccata dalla PR; vedi punti dubbi).
- «pages without `vectorScore` matched only via keyword» (inferenza: con `graphHits` anche i vicini del grafo non hanno `vectorScore`).
- «files the watcher already saw» → «files the app already saw» (stessa ragione di V21).

### Residui rinviati dai TSK precedenti: decisione
| Residuo | Decisione | Motivo |
|---|---|---|
| «labelled "API Server" in older builds» (`README.md` r.55, `SKILL.md` r.80) | tolto | storia delle versioni, nessuna riga |
| «shorter than older docs stated» (`api-reference.md` r.326) | tolto con il resto della parentesi | storia delle versioni; i dettagli restanti sono solo [E] senza frase smentita (D14 resta in forma neutra) |
| `api-reference.md` r.525 «The old rule … does not hold on 0.6.13» | tolto | storia delle versioni; resta la regola attuale (405 solo fuori dai quattro verbi, 404 per il verbo sbagliato) [C+E] |
| Riferimenti a righe di codice (`search.rs`, `file_sync.rs`, …) | tolti i **numeri**, lasciati i nomi dei file e i fatti | il raw di verifica dà `search.rs` 464-472, 541-553, 15-20; `file_sync.rs` 339-362; `source-lifecycle.ts` 258-268: 4 dei numeri della skill (464, 541-551, 14-20, 258-285) non coincidono con la verifica; la factory non ha riletto le righe; i numeri legano la skill a un commit. I fatti hanno evidenza [C] (V1-V4, V16-V18). I nomi `ingest-cache.ts`, `review-store.ts`, `sweep-reviews.ts` sono file letti per intero dalla verifica. `api_server.rs`, `cors.rs`, `server_bind.rs` non sono più nel diff |
| Inferenza `vectorScore` (`examples.md` r.~197) | tolta la clausola dopo il trattino (frase upstream) | con `graphHits` i vicini del grafo mancano di `vectorScore`: «solo keyword» non è più vero; nessuna riga che la sostenga |

### Bozza della descrizione PR (inglese; da usare allo stato finale)
```text
Update the skill documentation for LLM Wiki app 0.6.13

This PR updates the four existing markdown files (`SKILL.md`, `api-reference.md`, `examples.md`, `README.md`). It changes no code, adds no files and adds no scripts.

How it was verified: by reading the app source code at v0.6.13 and checking some responses on a running app. Statements that I could not support this way were left out. Some statements about response shapes come from one check on one running app and were not repeated.

What changed, by area:

- Version: the skill now documents the API as implemented by app 0.6.13 and gives the basis of verification. The drift check compares the `version` reported by `/health` with 0.6.13. The old "0.4.10+" wording is gone.
- Security and network: CORS uses a list of origins (no wildcard). The listen address can change (`LLM_WIKI_BIND_HOST`, `allowLanAccess`) and is applied when the server binds. The token travels in clear text on a LAN. With `allowUnauthenticated`, some routes stay open and others always need the token. The "localhost-only" wording is removed.
- Projects and files: `currentProject` in `/projects`; which forms of `{id}` the server accepts; `/` in a path used as id must be sent as `%2F`; `files` paths are absolute; 413 above `maxFiles`; the list of readable file extensions (`rtf` is not readable).
- Health, search and graph: new `/health` fields; `graphHits` and `graphRelatedTo` in search; the score scale depends on `vectorHits`, not on `mode`; search covers `wiki/**/*.md` only, up to 10,000 files; `vectorScore` is a composite value. Graph pagination (`offset`, `limit`, `totalCount`, `hasMore`, `edgeScope`), `related:` links, open `nodeType` values, and `type: query` pages excluded from the graph.
- Methods, errors and limits: 405 only for verbs outside GET, POST, PATCH and DELETE; a wrong verb among those four gives 404; `OPTIONS` preflight; rate limit and in-flight limits; request body limits; no `Retry-After` header in the response paths that were read.
- Routes that change state: the skill no longer says that rescan is the only write. It lists the review routes, `pages/write`, `pages/embed` and `chat`, and tells the agent to call them only when the user explicitly asks. A call on an `{id}` that is not the current project is not read-only.
- Rescan and ingest: what `changedTasks` means, which conditions must hold before the desktop UI queues an ingest, and a recipe to read the review list.
- README: file count, the `--skill llm-wiki` name in the update command, and the settings section name.

Not verified, and left as it is (the skill says "not documented" or "not tested" where it applies):

- Request bodies of `chat`, review `PATCH` and `resolve`, and `pages/embed`; the HTTP verb and the outcome of a chat cancel; what `pages/write` does beyond its documented 409, 400 and 500.
- The status code for a generic request body that is too large, and the defaults of the source watch settings.
- The score scale with embeddings active and for RRF; the full list of fields in a search result; the full list of `kind` values and result fields of a rescan.
- The "Watch all projects" option (its default, whether an LLM is needed, which projects count) and a rescan on a project that is not open.
- The graph cache of 5 seconds, and the exact meaning of `totalCount` and `hasMore`.
- Behaviour on a running app for: writes with a token, chat, embeds, 429 and 503 under load, 413 and 415 on file content, listening on the LAN, and `allowUnauthenticated`.
- The interaction between the desktop auto-save and review edits.
```
Verifica della bozza con i pattern del controllo 2: `check2.py file` → `hits 0`; `grep` su ADR, factory, kanban, `Co-Authored`, `Claude`, `Anthropic`, `LWS`, `TSK`, `US-`, `EP-`, `gap`, `code_repos`, `sprint` → nessuna riga.

### Diff di chiusura (a comando)
- **Dichiarati:** `code_repos/llm_wiki_skill/README.md`, `SKILL.md`, `api-reference.md`, `examples.md`; questo TSK (`status`, `started_at`, Chiusura).
- **Committati:** `f6a99c7` nel repo della skill (4 file, 42+/56-), commit di correzione eseguito dalla sessione principale dopo OK esplicito dell'utente in chat (2026-11-23); `sm_commit.py --dry-run` → messaggio invariato. Dopo il commit: `git status --short` della skill vuoto; i 12 messaggi di `git log main..HEAD` ricontrollati con `ai_policy.find_factory_ids` e `is_ai_attribution` → 0 hit. Nessun push né PR. Factory: commit con questo TSK, `wiki/log.md`, `sprint.md` (da `HEAD`) e il puntatore, costruito in un indice privato.
- Punti dubbi (decisione dell'utente, 2026-11-23): fatti solo [E] che correggono una frase originale o descrivono una route nuova lasciati; «bypasses the file-sync watcher» lasciato, da verificare in LWS-TSK-012 (V21); cache del grafo 5 s e `totalCount`/`hasMore` lasciati e dichiarati non verificati nella PR; etichetta UI dell'opzione LAN tolta.
- **Working tree** (prima del commit): `git -C code_repos/llm_wiki_skill status --short` → ` M` sui 4 file; `git diff --stat HEAD` → 4 file, 42 inserzioni, 56 cancellazioni (README 6, SKILL 12, api-reference 68, examples 12 righe toccate); `git diff --stat main` → 4 file, 372 inserzioni, 128 cancellazioni. `git diff --check HEAD` senza errori. Nella factory è modificato solo questo TSK da questa sessione (altre sessioni lavorano sullo stesso clone).
- Messaggio di commit proposto: `docs: drop unverified details, version-history wording and code line numbers`

### Punti dubbi (con raccomandazione)
1. **Sola evidenza [E] lasciata:** `currentProject`, `path` assoluto di `files`, `Content-Type`, 401 in forma neutra, campi osservati di `agent`, e la sezione `GET reviews` (campi, `status`, `type`, `limit`): hanno una riga di osservazione e, per le review, la riga D3 [E+C] dell'epica. Raccomandazione: lasciare, perché correggono una frase originale o descrivono un endpoint nuovo senza altra fonte. Se si vuole la regola più stretta, togliere i campi di `GET reviews` oltre `count` e `reviews`.
2. **Frase originale lasciata:** `examples.md` «Writing to `wiki/**` or `raw/sources/**` via the filesystem directly bypasses the file-sync watcher» è testo upstream. La wiki dice che il watcher osserva `raw/sources` e `wiki`, quindi la frase è probabilmente inesatta, ma la verifica sul codice (V21) è aperta. Raccomandazione: non correggerla in questa PR; aprire una verifica (LWS-US-008) e un'eventuale PR successiva.
3. **Cache di 5 s e semantica di `totalCount`/`hasMore`:** restano nella skill come da istruzione e sono nella descrizione PR come non verificate. Raccomandazione: se si vuole il rigore pieno, toglierle prima della PR; il costo è minimo.
4. **Etichetta dell'opzione di rete locale** tolta (solo dichiarazione di issue chiusa). Raccomandazione: lasciarla fuori; è reintegrabile se il codice 0.6.13 la conferma.
5. **Commit già fatti:** i 11 commit hanno l'identità git dell'utente come autore e nessun trailer. Nessuna azione.
6. **Fini riga:** i file sono LF; i quattro file di lavoro non hanno CR.

## Dependencies
- LWS-TSK-015 — tutti i TSK di contenuto chiusi e committati.

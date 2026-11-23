---
id: LWS-TSK-003
title: "Scartare le novità senza etichetta e senza evidenza e ripristinare il trigger originale"
us: LWS-US-002
sprint: 01
layer: docs
consumer: agent
priority: P1
estimate: S
status: done
depends_on: [LWS-TSK-002]
blocked_by: []
code_path: ["code_repos/llm_wiki_skill/SKILL.md", "code_repos/llm_wiki_skill/api-reference.md", "code_repos/llm_wiki_skill/examples.md", "code_repos/llm_wiki_skill/README.md"]
target: llm_wiki_skill
started_at: 2026-11-23
closed_at: 2026-11-23
decision_refs: []
---

# LWS-TSK-003 — Scartare le novità senza evidenza e ripristinare il trigger

## Context
La regola della bozza «senza etichetta = upstream» è contraddetta da novità 0.6.13 senza etichetta (anomalia A1). Quelle senza una riga di evidenza non si portano. La `description` resta quella originale, con la sola clausola «read-only except for source rescan» corretta. [^src: management/kanban/LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-002-bonificare-la-bozza-di-partenza/LWS-US-002.md §Business Rules] [^src: wiki/entities/llm-wiki-skill-bozza-alm-wiki.md §Anomalie A1-A5 (della fonte)]

## Technical Specs
- **Layer docs, consumer agent, target `llm_wiki_skill`.** Stesso branch condiviso.
- **Novità senza etichetta da trattare (A1):** `description`, righe 0.6.13 di `SKILL.md`, 409 e 499, quasi tutta la sezione «Additions» di `api-reference.md`, CORS, `limit` 0 con 400.
- **Decise dal codice, restano:** solo `limit` 0 con 400, CORS e l'esclusione di `rtf`. Tutto il resto senza riga di evidenza esce; ciò che sarà coperto dalle storie di contenuto (003..007) rientra lì, con la sua riga.
- **Trigger (N4):** `description` = originale; unica modifica: «read-only except for source rescan» → «lettura per default, scrittura su richiesta esplicita dell'utente» (formulata in inglese coerente con il resto della frase della skill). Nessun altro cambio di trigger.
- L'elenco delle scartate nella Chiusura **senza dati del progetto reale**.
- Evidenza: [^src: wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md §Affermazioni della bozza senza etichetta (anomalia A1): non entrano come fatti] [^src: wiki/entities/llm-wiki-skill-bozza-alm-wiki.md §Aggiornamenti (v2026-11-22, verifica sul codice)]

## Vincoli comuni (TSK docs di contenuto)
- Prima di scrivere: `git -C code_repos/llm_wiki_skill branch --show-current` deve dare il branch condiviso; se diverso, STOP.
- Si scrive solo nei file di `code_path`; nessun file nuovo, nessun codice o script.
- Testi della skill senza ID kanban, riferimenti a ADR, wiki o factory, attribution AI o `Co-Authored-By`. Le sigle [C]/[E] solo nel TSK.
- Se la wiki non documenta un comportamento v0.6.13, la skill non lo afferma.
- Commit: non lo esegue il dev-agent; propone un messaggio generico senza ID; la sessione principale lo esegue con `tools/vcs/sm_commit.py` dopo OK esplicito. `done` solo dopo il commit; Chiusura con i tre campi (dichiarati, committati, working tree).

## Implementation Steps
1. Verifica del branch.
2. Confrontare il testo dei quattro file con l'elenco A1 e togliere ciò che non ha riga di evidenza.
3. Ripristinare la `description` originale con la sola clausola corretta (leggerla dal commit `main`: `git show main:SKILL.md` nel repo della skill).
4. Ricerca testuale: nessun 409/499 fuori dai casi decisi, nessuna riga 0.6.13 non coperta.
5. Elencare le scartate in Chiusura, senza dati del progetto reale.

## Definition of Done
- [x] AC4: `description` originale con la sola clausola riformulata; diff della `description` contro `main` riportato.
- [x] AC5: novità senza evidenza assenti; elenco delle scartate in Chiusura.
- [x] Nessuna traccia (ricerca testuale su ID, factory, attribution AI) nei quattro file.

## Chiusura

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-002 AC4 | Verificato, da spuntare dopo il commit | Branch `docs/align-v0-6-13`, HEAD `aeada6b`. La `description` coincide con `git show main:SKILL.md` riga 3 salvo la clausola finale. Diff contro `main` (prefisso comune di 775 caratteri, nessun altro cambio): `main` = «Read-only except for source rescan.» → ora = «Read-only by default, writes only on the user's explicit request.» Nessun altro cambio di trigger. |
| LWS-US-002 AC5 | Verificato, da spuntare dopo il commit | Restano solo i tre punti decisi dal codice: `limit` del grafo 0, negativo o non numerico → 400; CORS ad elenco senza `*`; `rtf` non leggibile. Tutto il resto dell'elenco A1 senza riga di evidenza è uscito (elenco sotto). Ricerca testuale sotto. |
| LWS-US-002 AC7 | verificato | Nessun ID kanban, riferimento a factory o attribution AI nei quattro file (ricerca sotto). Commit dopo OK esplicito dell'utente in chat (2026-11-23), eseguito dalla sessione principale: `sm_commit.py --dry-run` → messaggio invariato; `--yes` → `778b149` su `docs/align-v0-6-13`, 4 file, 15+/111-; `git log -1` senza trailer né attribution. |

### Righe di evidenza dei tre punti rimasti
- `limit` 0 → 400: [^src: wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md §Esito per voce, riga 9] (assente 200; maggiore di 0 ridotto a `[1,1000]`; 400 per 0, negativo e non numerico). Testo: righe «Graph `limit`» di `api-reference.md` (Limits) e `limit` della tabella dei parametri del grafo; la riga `graph` di `SKILL.md` lo aveva già («0/negative → 400»). La tabella ora dice «non numerico» (la bozza diceva «non intero»), secondo l'evidenza.
- CORS: [^src: wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md §Esito per voce, righe 23, 24] (`Origin` riflesso solo se in elenco: estensioni chrome e moz, `localhost`, `127.0.0.1`, `[::1]`, `tauri://localhost`, `http(s)://tauri.localhost`; altrimenti manca l'header; nessun `*`; metodi GET, POST, PATCH, DELETE, OPTIONS). Tolti dal paragrafo i dettagli senza riga: `Vary: Origin`, `Access-Control-Allow-Private-Network: true`, forma `[:port]` e schema `http://` nell'elenco.
- `rtf`: [^src: wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md §Esito per voce, riga 12] (11 estensioni, `rtf` esclusa).

### Criterio applicato
- Una frase resta se la bozza le dava `[obs]` o `[code]` (non è A1) oppure se è uno dei tre punti decisi.
- Una frase A1 senza etichetta e senza riga di evidenza esce, anche se la wiki ha una riga sul tema: rientra con la sua riga nelle storie 003..007.
- Dove la bozza aveva sostituito un testo originale con testo A1, si è ripristinato l'originale (chat) o una formula generica fondata sulla riga «le scritture esistono: rotte POST/PATCH/DELETE» (riga 24: Etiquette di `SKILL.md`, `README.md`).

### Novità scartate (nessuna riga di evidenza)
`SKILL.md`
- `description`: la clausola estesa su gestione delle review, scrittura ed embed di pagine e chat dell'agente (sostituita dall'originale con la sola clausola riformulata).
- Tabella endpoint, riga `chat`: la metà 0.6.13 (chat agente, JSON o SSE, token sempre, consumo di chiamate LLM). Resta «0.4.x: 501 — not implemented. Don't call.»
- Tabella endpoint: righe `chat/{sessionId}/cancel`, `reviews` (lettura), mutazioni delle review, `pages/write`, `pages/embed`.
- Tabella errori: righe 409 e 499.
- Etiquette: l'elenco di endpoint 0.6.13 e «Check `/health` → `version`» (sostituiti da una regola generica sulle scritture).

`api-reference.md`
- Sezione `chat`: il rinvio alla chat agente 0.6.13 (ripristinato il testo originale con il qualificatore 0.4.x).
- Riga «Graph `limit`» dei limiti: il rinvio alla sezione di paginazione e il testo del messaggio d'errore.
- CORS 0.6.13: `Vary: Origin`, `Access-Control-Allow-Private-Network`, forma `[:port]` e schema `http://` nell'elenco.
- «Additions», nota di provenienza («Source: app code at tag …»).
- «Additions», «Common checks (in order)»: ordine dei controlli e limiti di corpo specifici (chat, `pages/write`).
- «Additions»: regola «token sempre richiesto» per chat, cancel, `pages/write`, `pages/embed` (la stessa frase con `[code]` in `SKILL.md` e `README.md` resta).
- «Additions», elenco dei tipi di review.
- «Additions», sezione mutazioni delle review (tabella, riapertura con `resolved: false`, visibilità dopo il refresh, rischio di sovrascrittura, «re-list»).
- «Additions», sezioni `pages/write`, `pages/embed`, `chat` (campi, risposta, SSE, cancel, 499, 502).
- «Additions», sezione «graph (pagination)»: `offset`, `edgeScope`, campi di risposta, messaggio d'errore. Resta solo il 400 di `limit`, spostato nelle due righe sopra.

`examples.md`
- «within seconds» sul watcher (la frase sul watcher resta come in `api-reference.md`, senza tempi: la riga 21 della verifica non è confermata dal codice).
- Anti-pattern `/chat`: «real agent chat that spends the app's LLM calls … use it only after the user confirmed» (resta il fatto `agent.chat: true`).
- Anti-pattern sulle scritture: «on 0.6.13 use `pages/write` (with user confirmation)».

`README.md`
- «On **0.6.13** reviews, `pages/write`, `pages/embed` and `chat` also change state or spend LLM calls» (sostituita da una formula generica).
- «chat 40 MiB, `pages/write` ~12 MiB on 0.6.13» nel limite di corpo.
- «**0.6.13 adds** review mutations, `pages/write`, `pages/embed` and an agent chat (see … Additions …)».

### Ricerca testuale finale (cartella `code_repos/llm_wiki_skill`, quattro file)
- Comando 1: `grep -n -i -E "(EP|US|TSK|LWS)-[0-9]|wiki-factory|factory|\bADR\b|Co-Authored|Anthropic|Generated with|alm-wiki|almus|musio|core-wiki|FORK\.md|\[obs\]|\[code\]|local_git|kanban" *.md` → nessuna riga (exit 1). Le parole «Claude Code» e «gap» nel testo sono dell'originale `main`.
- Comando 2: `grep -n -E "\b(409|499)\b|within seconds|Vary|Private-Network|pages/write|pages/embed|reviews/resolve|sessionId" *.md` → 409 e 499 assenti; «within seconds», `Vary`, `Private-Network`, `reviews/resolve`, `sessionId` assenti; `pages/write` e `pages/embed` restano solo nelle tre frasi con `[code]` sul token (`SKILL.md` riga 79, `README.md` riga 61) e sul cambio di stato (`examples.md` riga 273).
- Comando 3: `grep -n "0\.6\.13" *.md`. Le righe 0.6.13 restanti sono tutte `[obs]` o `[code]` nella bozza, oppure decise dal codice (CORS, `rtf`), oppure frasi generiche riformulate qui sulla riga 24. Eccezioni senza etichetta nella bozza e fuori dall'elenco A1, lasciate: `README.md` righe 109, 111, 133 (stessi fatti con `[code]`/`[obs]` altrove).

### Residui per altri TSK
- LWS-TSK-016: riferimenti a righe di codice con `[code]` non verificati nel testo: `api-reference.md` `api_server.rs` 855-896, `commands/search.rs` 464, 541-551, 782-792, `search.rs` 14-20, 960-970, `file_sync.rs` 339-362 con `project-file-sync.ts` e `source-lifecycle.ts`, e i nomi senza righe (`ingest-cache.ts`, `server_bind.rs`, `review-store.ts`, `sweep-reviews.ts`). Il file `src-tauri/src/cors.rs` ha una riga di verifica (11-41).
- LWS-TSK-007 (grafo): `SKILL.md` e `examples.md` citano ancora `offset`, `edgeScope`, `hasMore` (`[obs]`/senza etichetta) mentre `api-reference.md` non ha più la sezione di paginazione.
- LWS-TSK-009 e LWS-TSK-004: frasi `[code]` non coperte dalla verifica (`handle_write_page` e `handle_chat` non letti): token sempre richiesto per chat, cancel, `pages/write`, `pages/embed` (`SKILL.md` riga 79, `README.md` riga 61); «rescan, reviews, `pages/write`, `pages/embed`, chat cambiano lo stato» (`examples.md` riga 273); `SKILL.md` e la riga 503 citano ancora chat ed embed senza la loro sezione. In `api-reference.md` resta la frase sulla riscrittura di `review.json` dopo circa 1 s (`[code]`), senza il contesto delle mutazioni.
- LWS-TSK-010 e LWS-TSK-012: in «When does ingest actually start» la frase «off by default» per «Watch all projects» non ha riga (il default non è noto).
- LWS-TSK-006 e LWS-TSK-009 (A4, fuori dall'elenco A1): restano senza etichetta la scala dello score per `vectorHits`, `hybrid` senza vettori, `current` e «negli script l'UUID» (riga 25 della verifica: «negli script l'UUID» non è deciso dal codice), «does not prove that ingest was queued», «on 0.4.x» nelle righe 501 e chat.

### Diff di chiusura (a comando)
- `git -C code_repos/llm_wiki_skill branch --show-current` → `docs/align-v0-6-13`; HEAD `aeada6b` invariato.
- Dichiarati: `SKILL.md`, `api-reference.md`, `examples.md`, `README.md` (repo della skill) e questo file TSK.
- Committati: `778b149` nel repo della skill con i 4 file (`git diff --cached --name-only` prima del commit); nella factory nessun commit.
- Dopo il commit (a comando): repo della skill `git status --short` e `git diff --name-only HEAD` vuoti; factory ` M code_repos/llm_wiki_skill` (puntatore a `778b149`, non committato), ` M` questo TSK, LWS-TSK-001/002, `sprint.md`, `wiki/log.md`; `?? DOSSIER-llm-wiki-qualita-ingest.md` preesistente. La riga «Nel working tree» sotto descrive lo stato prima del commit.
- Nel working tree della skill: `git status --short` → ` M README.md`, ` M SKILL.md`, ` M api-reference.md`, ` M examples.md`. `git diff --name-only HEAD` → gli stessi quattro file. `git diff --stat HEAD` → 4 file, 15 inserzioni, 111 cancellazioni (README 6, SKILL 13, api-reference 100, examples 7). Contro `main`: 4 file, 226 inserzioni, 114 cancellazioni.
- Fine riga CRLF dei quattro file preservata.
- Messaggio di commit proposto: `docs: drop unproven 0.6.13 additions and restore the original trigger wording`

> Stato: `in-progress`, DoD non spuntata. Passa a `done` solo dopo il commit con OK esplicito dell'utente.

## Dependencies
- LWS-TSK-002 — la bozza deve essere già applicata e bonificata.

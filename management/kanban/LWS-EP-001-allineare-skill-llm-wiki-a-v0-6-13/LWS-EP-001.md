---
id: LWS-EP-001
title: Allineare la skill llm-wiki all'app llm_wiki v0.6.13 (fase A, PR generica upstream)
status: defined
priority: high
confidence: 70%
confidence_rationale: D4, D5, D7, D9-D12, D15, D16, D18-D21 sono letti nel codice di e08cfce (D4, D7, D9, D10 anche osservati in esecuzione), quattro dei dieci punti non confrontabili sono chiusi e esiste una bozza di partenza. Il codice non e' mai eseguito dalla factory, l'esecuzione e' una prova su un progetto non replicata, e restano non letti handle_write_page, handle_chat e i corpi di chat, review ed embed.
wiki_pages: [wiki/syntheses/llm-wiki-skill-vs-app-v0-6-13.md, wiki/entities/llm-wiki-skill.md, wiki/concepts/llm-wiki-skill-api-v1-dichiarata.md, wiki/concepts/llm-wiki-api-locale.md, wiki/concepts/llm-wiki-sicurezza.md, wiki/concepts/llm-wiki-api-osservazioni-esecuzione-v0-6-13.md, wiki/concepts/llm-wiki-ricerca-e-grafo-api.md, wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md, wiki/entities/llm-wiki-skill-bozza-alm-wiki.md]
created: 2026-11-22
depends_on: []
---

# LWS-EP-001 — Allineare la skill llm-wiki all'app llm_wiki v0.6.13 (fase A, PR generica upstream)
> Portare i quattro file markdown della skill `llm-wiki` dal contratto «API v1, app 0.4.10+» a quanto la wiki documenta per l'app v0.6.13, come aggiornamento generico per una PR verso `nashsu/llm_wiki_skill`, senza personalizzazioni e senza tracce della factory.

## Obiettivo
La skill `llm-wiki` (`SKILL.md`, `api-reference.md`, `examples.md`, `README.md`, solo markdown) dichiara «LLM Wiki API v1 as shipped in app version 0.4.10+» e descrive un'API più vecchia della v0.6.13. Un agente che la segue oggi:
- non conosce le route che esistono (`reviews`, `pages/embed`, `pages/write`, `chat/{sessionId}/cancel`) e crede che l'unica scrittura sia il rescan;
- evita `/chat`, che nella v0.6.13 risponde in JSON o SSE;
- si fida di un modello di sicurezza non più vero (CORS `*`, «solo localhost»), mentre v0.6.13 usa CORS ad elenco e può ascoltare su LAN;
- interpreta male 404 e 405, legge la ricerca ibrida come RRF e il grafo come non paginato.

L'epica produce un aggiornamento generico della skill, partendo da `main` della fork `code_repos/llm_wiki_skill`, destinato a una PR upstream. Dichiara come base «verificata su v0.6.13» (lettura del codice di `e08cfce` e alcune risposte verificate su un'app in esecuzione) e non porta alcun fatto privo di evidenza in wiki. La skill resta «documentation only» e «client-less». Come testo di partenza si usa la bozza di riscrittura nel progetto locale dell'utente (vedi `wiki/entities/llm-wiki-skill-bozza-alm-wiki.md`), solo dopo bonifica e mai come fonte di fatti. [^src: wiki/syntheses/llm-wiki-skill-vs-app-v0-6-13.md §Dettaglio] [^src: wiki/entities/llm-wiki-skill.md §Struttura e installazione] [^src: wiki/entities/llm-wiki-skill-bozza-alm-wiki.md §Uso consigliato (proposta del keeper)]

## Valore di business
- 20 differenze su 20 (D1-D7 e D9-D21; **D8 non esiste**, la numerazione della sintesi salta) non più affermate in senso contrario dalla skill.
- 0 affermazioni nuove senza una riga di evidenza (codice e/o esecuzione) in wiki.
- 0 elementi della bozza non trasferibili (etichette, `FORK.md`, dati di un progetto reale) nel diff della PR.
- Una PR upstream da `main`, solo markdown, con 0 ID kanban, riferimenti alla factory o attribution AI nei file e nei commit.

## Decisioni dell'utente (2026-11-22)
- **Versione:** la skill dichiara solo «verificata su v0.6.13» con base dichiarata; niente «0.4.10+»; nessuna storia delle versioni (nessun «dalla versione X»).
- **Punti non decidibili dalla wiki:** verifica sul codice in parallelo, non bloccante (LWS-US-008).
- **Corpi non noti** (chat, review, embed): solo esistenza, auth, limiti ed errori.
- **Scritture:** lettura per default; scrittura solo su richiesta esplicita dell'utente.
- **Prove in esecuzione:** nessuna nuova prova pianificata; quelle aperte restano non verificate e dichiarate.
- **MCP:** fuori scope. **Fase B:** nessuna storia segnaposto. **`purpose.md`:** decisione dell'utente, fuori dall'epica.
- **Gate:** espliciti su fetch dell'upstream, commit, push e PR.
- **Fatti solo osservati:** si corregge soltanto la frase che l'osservazione smentisce, in forma neutra, senza nuove garanzie.
- **Bozza:** letta in sola lettura dal percorso esterno del progetto locale dell'utente; nulla è copiato nella factory; si scrive solo nel branch del submodule `code_repos/llm_wiki_skill`; nessun dato del progetto reale in output della factory né nella PR.
- **Drift:** la regola del README diventa «qualunque versione riportata da `/health` diversa da quella verificata».
- **Trigger:** `description` originale; si corregge solo la clausola «read-only except for source rescan».

## Scope

**In scope**
- D1-D7, D9-D21 e le incoerenze interne risolvibili con fatti ora in wiki.
- La dichiarazione di versione e la regola di drift del README.
- La bonifica del testo della bozza come punto di partenza.
- La verifica sul codice dei soli residui reali, in parallelo.
- I controlli di non-traccia e l'audit delle affermazioni sulla PR.

**Out of scope**
- Fase B (estensioni personali su `develop`, oggi senza materiale perché `develop` di `llm_wiki` coincide con `main`): nota di scope, nessuna storia.
- MCP, client, SDK, script, modifiche a `llm_wiki`.
- Licenza e rotazione del token (incoerenza n. 16).
- Nuove prove in esecuzione.
- Storia delle versioni 0.4.10 → 0.6.13 (gap `llm-wiki-api-storia-versioni`).

## Regole trasversali (valgono per tutte le storie)
- Se la wiki non documenta un comportamento v0.6.13, la skill non lo afferma.
- Sigle di evidenza, **solo lato factory e mai nella skill**: **[C]** letto nel codice di `e08cfce` (upstream v0.6.13), mai eseguito; **[E]** osservato in esecuzione su app 0.6.13 il 2026-11-13 in un progetto locale dell'utente, una prova, non replicata; **[C+E]** entrambe. [C] ed [E] non si sostituiscono.
- Un fatto con sola evidenza [E] si riporta in forma neutra o non si riporta: si corregge soltanto la frase smentita, senza nuove garanzie.
- Non si portano inferenze (per esempio la sovrascrittura delle review dall'auto-save o la perdita dei cambi dopo un rescan su un progetto non aperto).
- Una frase della bozza si porta solo se ha una riga di evidenza; le novità senza etichetta della bozza (anomalia A1) non si portano finché non sono coperte da una riga.
- Nessun ID kanban (`EP-`, `US-`, `TSK-`, `LWS-`), nessun riferimento ad ADR, wiki o factory, nessuna attribution AI né `Co-Authored-By` nei file della skill e nei messaggi di commit.
- La skill resta solo markdown, senza script, SDK o wrapper; i file toccati sono i quattro esistenti.
- Postura sulle scritture: lettura per default; scrittura solo su richiesta esplicita dell'utente.
- Nessun fetch dell'upstream, commit, push o apertura di PR senza OK esplicito dell'utente al gate; i comandi eseguiti e il loro esito sono riportati.
- Sigle usate nelle storie: D1-D21 (sintesi `llm-wiki-skill-vs-app-v0-6-13`); n. 1-17 (incoerenze interne della skill, in `llm-wiki-skill`); V1-V25 (le 25 affermazioni di `llm-wiki-api-affermazioni-codice-da-verificare`, sigla del product-manager per il «#» della pagina); A1-A5 (anomalie della bozza).

## Storie incluse
- [LWS-US-001](LWS-US-001-confermare-base-di-partenza/LWS-US-001.md) — Confermare la base di partenza
- [LWS-US-002](LWS-US-002-bonificare-la-bozza-di-partenza/LWS-US-002.md) — Bonificare la bozza come testo di partenza
- [LWS-US-003](LWS-US-003-sicurezza-rete-e-autenticazione/LWS-US-003.md) — Sicurezza, rete e autenticazione
- [LWS-US-004](LWS-US-004-progetti-file-e-contenuti/LWS-US-004.md) — Progetti, file e contenuti
- [LWS-US-005](LWS-US-005-salute-ricerca-e-grafo/LWS-US-005.md) — Salute, ricerca e grafo
- [LWS-US-006](LWS-US-006-metodi-errori-e-limiti/LWS-US-006.md) — Metodi, errori e limiti
- [LWS-US-007](LWS-US-007-scritture-chat-e-rescan/LWS-US-007.md) — Scritture, chat e rescan
- [LWS-US-008](LWS-US-008-verificare-i-residui-sul-codice/LWS-US-008.md) — Verificare sul codice i soli residui
- [LWS-US-009](LWS-US-009-coerenza-interna-e-versione/LWS-US-009.md) — Coerenza interna e dichiarazione di versione
- [LWS-US-010](LWS-US-010-preparare-la-pr-upstream/LWS-US-010.md) — Preparare la PR upstream senza tracce e senza affermazioni scoperte

## Matrice di copertura

| Elemento | Storia | Evidenza |
|---|---|---|
| D1 | LWS-US-007 | [C] parziale; non eseguito |
| D2 | LWS-US-007 | [C] contratto + [E] solo il flag `agent.chat`; interno non letto |
| D3 | LWS-US-007 | `reviews` in lettura [E+C]; il resto [C] a livello di contratto |
| D4 | LWS-US-003 | [C+E] |
| D5 | LWS-US-003 | [C]; non eseguito |
| D6 | LWS-US-003 | [C]; non eseguito |
| D7 | LWS-US-005 | [E+C] parziale |
| D9 | LWS-US-005 | [E+C] |
| D10 | LWS-US-005 | [E+C] parziale; cache di 5 s solo [C] da raw api-mcp |
| D11 | LWS-US-006 | [C+E] parziale |
| D12 | LWS-US-006 | [C] parziale; non eseguito |
| D13 | LWS-US-004 | [E] soltanto: correzione neutra |
| D14 | LWS-US-005 | [E] soltanto: correzione neutra |
| D15 | LWS-US-005 | [C+E]; scala RRF e embedding attivi non noti |
| D16 | LWS-US-005 | [C+E] |
| D17 | LWS-US-004 | [E+C] parziale |
| D18 | LWS-US-004 | [C] |
| D19 | LWS-US-005 | [C] |
| D20 | LWS-US-005 | [C] |
| D21 | LWS-US-007 | [C] su review, rescan, embed |
| n. 1 | LWS-US-006 (`pages/write` 400); corpo generico: LWS-US-008 / fuori PR | [C] / non noto |
| n. 2 | LWS-US-004 | [E+C]; presenza di `truncated` non chiara |
| n. 3, n. 4 | LWS-US-005 | [E+C] / [C] |
| n. 5 | LWS-US-004 | [C+E] |
| n. 6 | LWS-US-004 | chiuso per lettura (D18) |
| n. 7 | LWS-US-006 | [C]; riserva sugli header SSE di successo |
| n. 8 | LWS-US-006 | [C+E] |
| n. 9, n. 10 | LWS-US-003 | [C] |
| n. 11 | LWS-US-009 | intra-skill |
| n. 12 | LWS-US-007 | [C] |
| n. 13 | LWS-US-007 (parte nota), LWS-US-008 | [C] parziale |
| n. 14 | LWS-US-008 / fuori PR | non noto |
| n. 15 | LWS-US-005 | chiuso per lettura (D16, D19) |
| n. 16 | LWS-US-009 (valori di `status`); licenza e rotazione fuori scope | [C] |
| n. 17 | LWS-US-009 e LWS-US-010 | dichiarazione della base di verifica |
| V1-V9 | LWS-US-005 | [C]; V9 parziale |
| V10, V11, V12, V25 | LWS-US-004 | [C]; V11 e V25 parziali |
| V13, V14, V15 | LWS-US-005 (V13), LWS-US-006 (V14, V15) | [C+E] |
| V16, V17, V18 | LWS-US-007 | [C] parziale |
| V19 | LWS-US-007 | [C] |
| V20 | LWS-US-007 | [C] contratto + [E] flag |
| V21, V22 | non portate | da verificare (LWS-US-008); V22 è inferenza |
| V23, V24 | LWS-US-003 | [C] |
| A1 | LWS-US-002 (scarto) e LWS-US-010 (audit) | — |
| A4 (incongruenze ereditate) | LWS-US-006 e LWS-US-009 | — |

## Cosa resta fuori dalla PR se non verificato
- Corpi di `chat` (`AgentChatRequest`), di `PATCH` e `resolve` delle review e di `pages/embed`.
- Interno di `pages/write` oltre il contratto già noto (409, 400, 500).
- Codice del body generico troppo grande e default di `sourceWatchConfig`.
- Scala RRF e score con embedding attivi; elenco completo dei campi di un risultato di `search`.
- Campi del risultato di `rescan` e elenco completo dei `kind`.
- «Watch all projects» (default, LLM nel ramo inattivi, progetti recenti) e rescan su progetto non aperto.
- Corsa fra auto-save e review.
- Comportamento in esecuzione di scritture con token, chat, embed, 429/503, 413/415, bind LAN e `allowUnauthenticated`.
- Il codice 499 e le novità senza etichetta della bozza non coperte da una riga di evidenza.

## Confidence: 70%
Abbiamo: 20 differenze tabellate con evidenza di codice per quasi tutte e di esecuzione per D4, D7, D9, D10 (parziale per D2, D3, D11); 17 incoerenze interne; esiti della verifica sul codice (24 affermazioni confermate, 6 parziali, 1 non conclusiva); una bozza di riscrittura da cui partire. Ci manca: l'esecuzione delle scritture, della chat e dei limiti; la lettura di `handle_write_page`, `handle_chat`, `respond_chat_sse` e dei corpi di chat, review ed embed; la conferma che l'upstream sia fermo a `642b438`; la classificazione delle novità senza etichetta della bozza. Per questo la confidence sale da 60% a 70% ma non oltre. L'accettazione della PR da parte di upstream non dipende dalla factory e non è nel criterio di done.

## Dipendenze
Nessuna epica prerequisito. Ordine fra le storie: LWS-US-001 poi LWS-US-002; poi LWS-US-003..007 in parallelo; LWS-US-008 parallela e indipendente; poi LWS-US-009 e LWS-US-010. Gap collegati, tutti non bloccanti: `llm-wiki-skill-punti-da-verificare`, `llm-wiki-affermazioni-codice-da-verificare`, `llm-wiki-api-corpi-handler-non-letti`, `llm-wiki-prove-in-esecuzione-aperte`, `llm-wiki-watch-all-projects-residui`, `llm-wiki-api-storia-versioni`.

## Nota per il tpm (TSK)
- Layer `docs`, target `llm_wiki_skill`, `consumer: agent` (docs-dev), branch da `main`.
- docs-dev legge la bozza in sola lettura dal percorso esterno del progetto locale dell'utente e scrive solo nel branch del submodule `code_repos/llm_wiki_skill`; nulla è copiato nella factory.
- Le citazioni di evidenza vivono nei TSK e nelle storie, mai nella skill.
- Commit nel repo della skill: nessun ID kanban né attribution AI nei messaggi; commit solo con OK esplicito dell'utente.

## Nota di modifica
- 2026-11-22 — Creazione. Storie LWS-US-001..010 prenotate nel registro (`management/kanban/id-registry.yaml`). Proposta approvata dall'utente con le risposte alle domande N1-N4 (correzione neutra dei fatti solo osservati; bozza letta in sola lettura dal progetto locale dell'utente; regola di drift su qualunque versione diversa da quella verificata; `description` originale con la sola clausola «read-only except for source rescan» corretta).

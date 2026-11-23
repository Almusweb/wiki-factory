---
id: LWS-TSK-011
title: "Estrazione repo-sync A: residui della superficie API HTTP di llm_wiki a e08cfce"
us: LWS-US-008
sprint: 01
layer: docs
consumer: human
priority: P2
estimate: M
status: done
depends_on: []
blocked_by: []
code_path: ["raw/**"]
target: llm_wiki
started_at: 2026-11-23
closed_at: 2026-11-23
decision_refs: []
---

# LWS-TSK-011 — Estrazione mirata A: handler e limiti dell'API

## Context
LWS-US-008 vuole leggere nel codice di `llm_wiki` a `e08cfce` (v0.6.13) i soli punti rimasti non verificati, senza congetture. Il product-manager non scrive raw: l'estrazione è un `repo-sync` mirato in sola lettura; `wiki-keeper` ingerisce (`LWS-TSK-013`). Storia non bloccante: non è prerequisito di LWS-TSK-014 né di LWS-TSK-016. [^src: management/kanban/LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-008-verificare-i-residui-sul-codice/LWS-US-008.md §Business Rules]

## Technical Specs
- **Consumer:** `human`, override esplicito di `routing.docs: agent` (precedente TSK-012): il lavoro lo fa `repo-sync` con `/repo-sync`, mai automatico, con STOP di fase 4 e conferma umana. Un TSK `docs` agentico si risolverebbe sul repository del cliente. **Non è lavoro di docs-dev nel code_path della skill:** nessun file di `llm_wiki_skill` è toccato.
- **Target:** `llm_wiki`, sola lettura, commit `e08cfce`. Nessuna esecuzione dell'applicazione, nessuna modifica al repo cliente.
- **Output:** `raw/<data>-repo-llm_wiki-residui-api-skill.md` con voce `source: repo` in `raw/.extraction-manifest.json`, aggiunta senza sovrascrivere voci altrui.
- **Perimetro (residui della US, righe 1-5 e 7-9):**

| Residuo | Gap |
|---|---|
| `handle_write_page`, `handle_chat`, `respond_chat_sse` e header della risposta SSE di successo | `llm-wiki-affermazioni-codice-da-verificare` |
| Struttura di `AgentChatRequest` ed eventi agente | `llm-wiki-api-corpi-handler-non-letti` |
| Corpi di `embed_wiki_page` e payload di `PATCH` e `resolve` delle review | `llm-wiki-api-corpi-handler-non-letti` |
| Campi di `rescan_project_files` ed elenco completo dei `kind` di `changedTasks` | `llm-wiki-skill-punti-da-verificare` |
| Codice del body generico troppo grande | `llm-wiki-skill-punti-da-verificare` |
| Scala RRF e campi per risultato di `search`; `resolve_query_embedding` | `llm-wiki-skill-punti-da-verificare` |
| `offset`, `totalCount`, `hasMore` e cache di 5 s del grafo nel codice | `llm-wiki-skill-punti-da-verificare` |
| Limiti di corpo per route e ordine rispetto all'auth, riletti | `llm-wiki-skill-punti-da-verificare` |

- Non si rileggono i punti già chiusi o confermati dalla verifica del 2026-11-22.
- Esiti: «confermato», «smentito» o «non conclusivo», con file e riga dal raw. Nessuna correzione della skill in questo TSK (US-008 AC4).
- Nessuna nuova prova in esecuzione. Nessun valore di segreto.
- Fonti: [^src: wiki/gaps.md §2026-11-22 11:24 — llm-wiki-skill-punti-da-verificare] [^src: wiki/gaps.md §2026-11-22 12:39 — llm-wiki-affermazioni-codice-da-verificare] [^src: wiki/gaps.md §2026-11-21 07:31 — llm-wiki-api-corpi-handler-non-letti]

## Implementation Steps
1. `git -C code_repos/llm_wiki log -1 --format=%h` → `e08cfce`; se diverso, fermarsi. Se il submodule non è inizializzato, vale la nota di TSK-011 (`git submodule update --init code_repos/llm_wiki`, senza `--remote`).
2. Lanciare `/repo-sync` su `code_repos/llm_wiki` con il solo perimetro sopra; alla fase 4 confermare solo questo ambito.
3. Per ogni residuo: file, simbolo, righe, esito proposto con motivo del «non conclusivo».
4. Dichiarare commit, branch, file letti e non letti con motivo; controllo segreti.
5. `git -C code_repos/llm_wiki status --short` vuoto (repo cliente invariato).

## Definition of Done
- [x] Il raw esiste in `raw/` con file, simboli e righe per ogni conclusione; voce nel manifest.
- [x] Ogni residuo ha esito confermato / smentito / non conclusivo.
- [x] Il raw dichiara commit, branch, file letti e non letti.
- [x] Repo cliente invariato a comando.

## Chiusura

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-008 AC1 | soddisfatto | raw/2026-11-23-repo-llm_wiki-residui-api-skill.md, voce manifest residui-api-skill, perimetro R1-R17 |
| LWS-US-008 AC2 | soddisfatto | ogni residuo con esito e file:righe nel raw; sei punti non conclusivi dichiarati |
| LWS-US-008 AC4 | soddisfatto | nessun file di llm_wiki_skill toccato; correzioni non applicate |

<!-- AC3 e AC5 sono di LWS-TSK-012 / LWS-TSK-013 -->

## Dependencies
- Nessuna. Alimenta `LWS-TSK-013`.

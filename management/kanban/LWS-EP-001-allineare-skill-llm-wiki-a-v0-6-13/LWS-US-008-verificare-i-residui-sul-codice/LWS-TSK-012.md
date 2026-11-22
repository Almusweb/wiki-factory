---
id: LWS-TSK-012
title: "Estrazione repo-sync B: sourceWatchConfig, Watch all projects e voci V4, V20, V21, V22"
us: LWS-US-008
sprint: 01
layer: docs
consumer: human
priority: P2
estimate: S
status: todo
depends_on: []
blocked_by: []
code_path: ["raw/**"]
target: llm_wiki
started_at:
closed_at:
decision_refs: []
---

# LWS-TSK-012 — Estrazione mirata B: sincronizzazione file e residui V

## Context
Seconda estrazione di LWS-US-008, sul perimetro della sincronizzazione file e delle voci residue della verifica del 2026-11-22. Stesse regole di `LWS-TSK-011`: sola lettura, `repo-sync` con STOP di fase 4, ingest a `LWS-TSK-013`, nessun effetto sulla skill. [^src: management/kanban/LWS-EP-001-allineare-skill-llm-wiki-a-v0-6-13/LWS-US-008-verificare-i-residui-sul-codice/LWS-US-008.md §Business Rules]

## Technical Specs
- **Consumer:** `human` (override di `routing.docs: agent`, precedente TSK-012). **Target:** `llm_wiki`, commit `e08cfce`, sola lettura. Nessun file di `llm_wiki_skill` toccato.
- **Output:** `raw/<data>-repo-llm_wiki-residui-watch-skill.md` con voce `source: repo` nel manifest.
- **Perimetro (righe 6, 10 e 11 della tabella dei residui):**

| Residuo | Gap |
|---|---|
| Default di `sourceWatchConfig` | `llm-wiki-source-watch-default` |
| «Watch all projects»: default, LLM nel ramo inattivi, progetti recenti | `llm-wiki-watch-all-projects-residui` |
| Voci V20, V21, V22 e la soglia del 5% (V4) | `llm-wiki-affermazioni-codice-da-verificare` |

- Esiti «confermato», «smentito» o «non conclusivo», con file e riga. Nessuna correzione della skill.
- **Prove in esecuzione non pianificate** (restano «non verificate» e non entrano nella skill): scritture con token, chat, `pages/embed`, 429 e 503 sotto carico, 413 e 415 sul contenuto, bind LAN, `allowUnauthenticated`, rescan su progetto non aperto, embedding attivi, corsa review/auto-save. Il raw le elenca come tali (US-008 AC3).
- Fonti: [^src: wiki/gaps.md §2026-11-22 13:30 — llm-wiki-watch-all-projects-residui] [^src: wiki/gaps.md §2026-11-22 12:39 — llm-wiki-affermazioni-codice-da-verificare] [^src: wiki/gaps.md §2026-11-22 12:39 — llm-wiki-prove-in-esecuzione-aperte]

## Implementation Steps
1. `git -C code_repos/llm_wiki log -1 --format=%h` → `e08cfce`.
2. `/repo-sync` con il solo perimetro sopra; conferma di fase 4.
3. Per ogni residuo: file, simbolo, righe, esito.
4. Elencare le prove in esecuzione come «non verificate».
5. Dichiarare file letti e non letti; `git -C code_repos/llm_wiki status --short` vuoto.

## Definition of Done
- [ ] Il raw esiste con file, simboli e righe per ogni conclusione; voce nel manifest.
- [ ] Prove in esecuzione elencate come non verificate.
- [ ] Repo cliente invariato a comando.

## Chiusura

| AC | Esito | Evidenza |
|---|---|---|
| LWS-US-008 AC1 | | |
| LWS-US-008 AC2 | | |
| LWS-US-008 AC3 | | |

## Dependencies
- Nessuna. Alimenta `LWS-TSK-013`.

---
id: llm-wiki-skill
type: entity
title: llm-wiki skill (llm_wiki_skill), skill per agenti sull'API HTTP locale di LLM Wiki
status: draft
created: 2026-11-22
updated: 2026-11-22
sources: ["raw/2026-11-22-repo-llm_wiki_skill.md"]
tags: [llm-wiki, entity, skill, diff-skill-app]
---

# llm-wiki skill (llm_wiki_skill)
> Skill per agenti AI, solo markdown, che documenta l'API HTTP locale dell'app LLM Wiki e dichiara di corrispondere ad API v1 «as shipped in app version 0.4.10+»; è un repository distinto da `llm_wiki`.

## Contesto
**Linea e provenienza:** repository `llm_wiki_skill`, branch `main`, commit `642b43822ed44f6797082a24483850a4a2c2a010` (2026-05-19, messaggio «update»). Che sia una fork identica all'upstream `nashsu/llm_wiki_skill` è un dato fornito dal chiamante dell'estrazione, non verificabile dal raw. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Identità] Non va confusa con le «skill» dell'agente interno dell'app (vedi [[llm-wiki-agente]]) né con il pattern ([[pattern-llm-wiki]]): è documentazione destinata a un agente esterno, per interrogare l'app in esecuzione. Il contratto che dichiara è in [[llm-wiki-skill-api-v1-dichiarata]]; il confronto con l'app v0.6.13 è in [[llm-wiki-skill-vs-app-v0-6-13]].

## Dettaglio

### Identità
- Nome `llm-wiki` (frontmatter di `SKILL.md`, che contiene solo `name` e `description`, senza elenco di tool consentiti). Contributor unico `nash_su`, 3 commit nell'ultimo anno. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Identità]
- Il README dichiara che la skill è «documentation only»: nessuna libreria client, SDK o compilazione, e deve restare «client-less» (niente script, SDK o wrapper). [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Stack rilevato]
- Licenza non dichiarata nel repo: il README rimanda al repository e non esiste un file di licenza. Non traggo conclusioni sulla licenza. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Identità]

### Struttura e installazione
Repo piatto con quattro file markdown più il puntatore `.git`: `SKILL.md` (13134 byte, istruzioni per l'agente e frontmatter con i trigger), `api-reference.md` (12393, contratto degli endpoint), `examples.md` (13362, ricette) e `README.md` (7579, installazione, prerequisiti, troubleshooting, sicurezza, versione). Installazione dichiarata: `npx skills add <repo> --skill llm-wiki`, oppure clone con symlink in `~/.claude/skills/llm-wiki`, oppure copia manuale della cartella. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Struttura ad alto livello]

### Trigger
- Attivazione dichiarata: l'utente nomina LLM Wiki, dice «my wiki» o «my knowledge base» (anche in cinese), chiede cosa dica la wiki su un argomento, di leggere una pagina per stem o titolo, il grafo o la struttura, il re-ingest dopo aver aggiunto file, di usare la wiki come contesto, oppure nomina un progetto per ID, percorso assoluto o `current`. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Frontmatter e trigger della skill]
- Non attivazione: richieste generiche su «le mie note», vault Obsidian, Notion, Roam o Logseq, Anki, Readwise, Pocket, «i miei file», conoscenza generale o web. In dubbio la skill chiede se si intenda LLM Wiki, senza chiamare l'API. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Frontmatter e trigger della skill]

### Versione dichiarata
La skill dichiara «LLM Wiki API v1 as shipped in app version 0.4.10+» (README), con esempio di `/health` alla versione `0.4.x`. Non c'è tetto superiore né riferimento alla serie 0.5 e successive: la wiki documenta invece l'app alla v0.6.13. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Versione dichiarata]

### Cosa la skill dichiara di non coprire
Endpoint di scrittura (nessuno in v1) e chat/RAG (501); contenuti binari o non UTF-8 («API is text-only»); paginazione dell'albero file; filtro per nome progetto; più di 50 risultati per ricerca (per sweep esaustivi suggerisce di scorrere `files` e `files/content` con grep lato client); client, SDK, script e wrapper; e i tre casi fuori dal threat model (processo locale malevolo col token, `/health` senza auth, pagine web cross-origin). [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Cosa la skill dichiara di NON coprire]

### Pattern d'uso negli esempi
`examples.md` mostra ricette dalla conversazione alle chiamate: ricerca con `topK: 5` e `includeContent`, lettura di una pagina per stem, vicinato nel grafo, panoramica via `files` e lettura di `wiki/index.md`, `wiki/overview.md` e `purpose.md`, re-index con `rescan`, sweep esaustivo, progetto nominato e confronto fra progetti, anti-pattern e una trascrizione end-to-end con health pre-flight. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Pattern d'uso dagli esempi]

### Istruzioni che la skill rivolge a un agente (contenuto descritto, non istruzioni per la wiki)
Sono dati sulla skill, non regole di questa wiki. La skill chiede a un agente che la usi di: attivarsi solo se l'utente nomina LLM Wiki; controllare prima `/health` e non procedere se l'auth non è configurata; non loggare né ripetere il token e non metterlo in URL; usare `current` come progetto di default dichiarandolo una volta, non cambiare progetto in silenzio e mettere in cache l'`id`; citare il `path` di ogni pagina usata, non scaricare pagine intere se non richiesto e non inventare quando la ricerca è vuota; usare lo strumento HTTP già presente senza installare nulla; non ritentare ciecamente su 429 (almeno 1 s) e 503 (almeno 2 s), non chiamare `/chat`; non scrivere direttamente su `wiki/**` o `raw/sources/**`. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Istruzioni rivolte ad agenti nel contenuto (riportate come dato, non eseguite)] Il raw non segnala istruzioni dirette a chi estrae.

### Incoerenze interne della skill (materiale per la PR)
Sede unica delle 17 voci del raw (numerazione del raw): discrepanze verificabili fra i file della skill e aspetti non determinabili dal solo contenuto. Altre pagine rimandano a questi numeri senza ripeterle. La colonna «Con v0.6.13» si appoggia solo a quanto la wiki ha già (raw [[2026-11-21-repo-llm_wiki-api-mcp]], fatti letti nel codice e mai eseguiti); «non decidibile» vuol dire che la wiki non ha il dato. Sono tutte riferite alla skill 0.4.10+, non al comportamento di v0.6.13. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Gap evidenti]

| N. | Incoerenza nella skill | Con v0.6.13 |
|---|---|---|
| 1 | Body troppo grande: 400 in `SKILL.md` e `api-reference.md`, 413 in `SKILL.md` (body oltre 1 MB) | non decidibile per il body generico (per `pages/write` troppo grande: 400) |
| 2 | `maxFiles` oltre soglia: `api-reference.md` dice 413 ma la risposta ha il campo `truncated`; `SKILL.md` parla di cap a 10000 nodi con 413 | 413 al superamento; il campo `truncated` non è confermato |
| 3 | Forma di `/health`: 4 campi in un punto di `SKILL.md`, 8 in un altro; l'esempio del README omette `version` | v0.6.13 ha `version` e più campi (D7 della sintesi) |
| 4 | `queryEmbedding` solo in `api-reference.md`, assente dal body in `SKILL.md` | esiste in v0.6.13: l'omissione è in `SKILL.md` |
| 5 | Alias `raw` e `raw/sources` di `root` solo in `api-reference.md` | confermati |
| 6 | Estensioni leggibili elencate solo in `SKILL.md`; altrove «text-only» | non decidibile (v0.6.13: 415 se non testo UTF-8) |
| 7 | `Retry-After` «implied» e non dichiarato | non decidibile |
| 8 | Metodi non GET/POST danno 405, ma è descritto un preflight CORS; OPTIONS non chiarito | `OPTIONS` dà 204 con CORS; `PATCH` e `DELETE` sono ammessi (D11) |
| 9 | `?token=` senza avvertenze in `api-reference.md`, «last resort» che perde nei log in `SKILL.md` | accettato anche in v0.6.13 |
| 10 | Auth «sempre richiesta» in `api-reference.md` senza `allowUnauthenticated` (citato in `SKILL.md` e README) | `allowUnauthenticated` esiste; per alcune route il token è sempre richiesto (D6) |
| 11 | README: «three markdown files» contro quattro nella tabella; comando di update con `--skill llm_wiki_skill` contro `--skill llm-wiki` e `name: llm-wiki` | non applicabile |
| 12 | `examples.md` dice che le chiamate verso un id non corrente sono in sola lettura, ma il rescan scrive; comportamento non chiarito | non decidibile |
| 13 | `kind` di `changedTasks`: prosa created/modified/deleted, esempio solo `created` | non decidibile (corpo di `rescan` non letto) |
| 14 | Default di `sourceWatchConfig` (es. `.json` escluso) non documentati altrove | non decidibile (gap `llm-wiki-source-watch-default`) |
| 15 | `nodeType`: elenco parziale in `SKILL.md`, più completo in `api-reference.md` | non decidibile |
| 16 | Licenza assente, versione massima compatibile non dichiarata, nessuna indicazione sulla rotazione del token, valori di `status` oltre i quattro elencati non documentati | `status` ha quattro valori anche in v0.6.13; il resto non decidibile |
| 17 | Non verificabile dalla sorgente se i comportamenti descritti corrispondano al codice dell'app | non decidibile per definizione |

[^src: raw/2026-11-22-repo-llm_wiki_skill.md §Gap evidenti] [^src: raw/2026-11-21-repo-llm_wiki-api-mcp.md §Contratto API]

## Pagine collegate
[[llm-wiki-skill-api-v1-dichiarata]], [[llm-wiki-skill-vs-app-v0-6-13]], [[llm-wiki-app]], [[llm-wiki-api-locale]], [[llm-wiki-mcp-server]], [[2026-11-22-repo-llm_wiki_skill]]. Gap: [[gaps]] (`llm-wiki-skill-punti-da-verificare`, `llm-wiki-api-storia-versioni`).

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

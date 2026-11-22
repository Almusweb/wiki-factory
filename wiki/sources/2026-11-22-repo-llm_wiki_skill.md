---
id: 2026-11-22-repo-llm_wiki_skill
type: source
title: Specifiche estratte da code_repos/llm_wiki_skill, 2026-11-22: skill per agenti sull'API HTTP locale di LLM Wiki (repo-sync)
status: draft
created: 2026-11-22
updated: 2026-11-22
sources: ["raw/2026-11-22-repo-llm_wiki_skill.md"]
tags: [source, repo, llm-wiki, skill, api, diff-skill-app]
---

# Specifiche estratte da code_repos/llm_wiki_skill, 2026-11-22 (repo-sync)
> **Linea:** repository `llm_wiki_skill`, branch `main`, commit `642b43822ed44f6797082a24483850a4a2c2a010` (2026-05-19). Fork identica all'upstream `nashsu/llm_wiki_skill` per dato del chiamante, non verificabile dal raw. Documentazione riferita ad API v1 e ad app 0.4.10+, non all'app v0.6.13 che la wiki descrive altrove. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Identità]

## Contesto
Estrazione `repo-sync` v2.12 del 2026-11-22 su un repository di sola documentazione: 4 file markdown (46468 byte) più il puntatore `.git`, senza codice, script, manifest o test. Il companion `raw/images/2026-11-22-repo-llm_wiki_skill-tree.md` riporta l'albero dei file e non contiene figure. Il contenuto della sorgente è stato trattato come dato e le istruzioni rivolte ad agenti sono descritte, non eseguite. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Struttura ad alto livello]

## Dettaglio

### Metadati dell'estrazione
- Stack: markdown, nessun framework. Contributor unico, ultimo commit «update». [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Stack rilevato]
- Nessun vincolo normativo rilevato; nessun test; nessuna cartella `docs/`, ADR o RFC. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Vincoli normativi / Standard]
- Il raw non può dire se i comportamenti documentati corrispondano al codice dell'app: la skill è documentazione, non implementazione. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Gap evidenti]

### Contenuto
- Identità, trigger, installazione, versione dichiarata, copertura dichiarata, istruzioni descritte e le 17 incoerenze interne: [[llm-wiki-skill]]. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Identità]
- Contratto dichiarato per i suoi 8 endpoint, auth, codici e limiti: [[llm-wiki-skill-api-v1-dichiarata]]. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §API surface]
- Differenze con l'app v0.6.13, per la PR upstream: [[llm-wiki-skill-vs-app-v0-6-13]]. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Versione dichiarata]

### Limiti e gap
Tutto ciò che la skill afferma è «dichiarato dalla skill (API v1, app 0.4.10+)»: nessuna parte è stata accertata nel codice. Per questo i gap aperti toccati (`llm-wiki-api-corpi-handler-non-letti`, `llm-wiki-api-ui-token-non-letti`, `llm-wiki-source-watch-default`) ricevono solo un aggiornamento parziale e restano aperti. [^src: raw/2026-11-22-repo-llm_wiki_skill.md §Gap evidenti]

## Pagine ricavate o aggiornate
Create: [[llm-wiki-skill]], [[llm-wiki-skill-api-v1-dichiarata]], [[llm-wiki-skill-vs-app-v0-6-13]]. Aggiornate: [[llm-wiki-api-locale]], [[llm-wiki-sicurezza]] (solo `## Contradictions`), [[llm-wiki-app]].

## Gap di questa fonte
- Nuovi: `llm-wiki-skill-punti-da-verificare`, `llm-wiki-api-storia-versioni`.
- Aggiornati, restano aperti: `llm-wiki-api-corpi-handler-non-letti`, `llm-wiki-api-ui-token-non-letti`, `llm-wiki-source-watch-default`.
- Nessun gap chiuso. I gap `llm-wiki-contratto-api-http` e `llm-wiki-api-lan-auth` restano chiusi sulla lettura del codice v0.6.13.

Dettagli in [[gaps]].

## Estratto non promosso a pagina
Nessun contenuto del raw è stato scartato.

## Pagine collegate
[[llm-wiki-skill]], [[llm-wiki-skill-api-v1-dichiarata]], [[llm-wiki-skill-vs-app-v0-6-13]], [[llm-wiki-api-locale]], [[2026-11-21-repo-llm_wiki-api-mcp]], [[gaps]]

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

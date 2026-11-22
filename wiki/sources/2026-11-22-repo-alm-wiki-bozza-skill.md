---
id: 2026-11-22-repo-alm-wiki-bozza-skill
type: source
title: Specifiche estratte da alm-wiki, 2026-11-22: bozza della skill llm-wiki allineata all'app 0.6.13 (repo-sync)
status: draft
created: 2026-11-22
updated: 2026-11-22
sources: ["raw/2026-11-22-repo-alm-wiki-bozza-skill.md"]
tags: [source, repo, llm-wiki, skill, bozza, diff-skill-app]
---

# Specifiche estratte da alm-wiki, 2026-11-22: bozza della skill llm-wiki (repo-sync)
> **Linea e provenienza:** cartella della skill nel repo locale dell'utente (alm-wiki), non un `code_path` della factory, ramo `main`, commit `050f023`; ultimo commit sulla cartella `26406be`. È un **testo candidato**, non una fonte di fatti sull'app. [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §Identita']

## Contesto
Estrazione `repo-sync` v2.12 del 2026-11-22 su 5 file markdown (`SKILL.md`, `api-reference.md`, `examples.md`, `README.md`, `FORK.md`), senza codice, manifest o script; stack non applicabile. Il confronto è con la baseline dell'originale `llm_wiki_skill` a `642b438` ([[2026-11-22-repo-llm_wiki_skill]]). Contenuto scritto da agenti, trattato come dato: le istruzioni agli agenti sono descritte, non eseguite; le prove su cui la bozza si appoggia sono in [[2026-11-22-repo-alm-wiki-evidenze-api]] e non si ripetono. [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §Stack rilevato]

## Dettaglio

### Contenuto e dove sta in wiki
- La bozza come entità (cosa aggiunge, livelli di prova, elementi non trasferibili alla PR upstream, anomalie A1-A5): [[llm-wiki-skill-bozza-alm-wiki]]. [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §Elementi non trasferibili a una PR upstream]
- Le 173 differenze rispetto all'originale restano nel raw (per file: `SKILL.md` 50, `api-reference.md` 77, `examples.md` 30, `README.md` 16; 60 `[obs]`, 51 `[code]`, 6 con entrambe, 56 senza etichetta); la wiki non ne duplica le tabelle. [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §Differenze rispetto a raw/2026-11-22-repo-llm_wiki_skill.md]
- I riferimenti al codice dell'app (`api_server.rs`, `search.rs`, `file_sync.rs`, `project-file-sync.ts`, `source-lifecycle.ts`, altri senza righe) sono verificabili solo sul commit `e08cfce`: [[llm-wiki-api-affermazioni-codice-da-verificare]]. [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §Riferimenti al codice dell'app (verbatim)]

### Limiti e gap
I `file:riga` non sono verificabili; per le frasi senza etichetta non è sempre determinabile se siano upstream, nuove o inferite; non provati secondo le evidenze: scritture con token, 413 e 415 sul contenuto, 429 e 503, `rtf`. [^src: raw/2026-11-22-repo-alm-wiki-bozza-skill.md §Gap evidenti]

## Pagine ricavate o aggiornate
Create: [[llm-wiki-skill-bozza-alm-wiki]]. Aggiornata (in accodamento): [[llm-wiki-skill]].

## Gap di questa fonte
- Nuovo: `llm-wiki-affermazioni-codice-da-verificare` (comprende le affermazioni senza etichetta, anomalia A1).
- Nessun gap chiuso.

## Estratto non promosso a pagina
Le tabelle delle 173 differenze e `FORK.md` (descritto, non riportato): restano nel raw.

## Pagine collegate
[[llm-wiki-skill-bozza-alm-wiki]], [[2026-11-22-repo-alm-wiki-evidenze-api]], [[2026-11-22-repo-llm_wiki_skill]], [[llm-wiki-skill]], [[llm-wiki-api-affermazioni-codice-da-verificare]], [[gaps]]

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

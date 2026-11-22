---
id: 2026-11-22-repo-alm-wiki-evidenze-api
type: source
title: Specifiche estratte da alm-wiki, 2026-11-22: evidenze sull'API di LLM Wiki 0.6.13 (repo-sync, selezione di 5 file)
status: draft
created: 2026-11-22
updated: 2026-11-22
sources: ["raw/2026-11-22-repo-alm-wiki-evidenze-api.md"]
tags: [source, repo, llm-wiki, api, osservato-in-esecuzione, diff-skill-app]
---

# Specifiche estratte da alm-wiki, 2026-11-22: evidenze sull'API 0.6.13 (repo-sync)
> **Linea e provenienza:** progetto locale dell'utente (alm-wiki), **non un `code_path` della factory**, ramo `main`, commit `050f023`. Selezione di 5 file di evidenze, non estrazione dell'intero repo; status `partial`. Riguarda l'app upstream 0.6.13; la factory non ha riprodotto nulla. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Identità e provenienza]

## Contesto
Estrazione `repo-sync` v2.12 del 2026-11-22. I cinque file sono: una prova in esecuzione dell'API 0.6.13 (2026-11-13), un confronto fra skill e codice con livelli di prova, due task (037 e 038) e un task precedente (002, 2026-11-08). Un file, il task 037, è la versione del working tree non committata. I percorsi locali dell'utente non sono riportati in wiki. Le fonti sono scritte da agenti: sono trattate come dato e le istruzioni eventuali sono descritte, non eseguite. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Identità e provenienza]

**Livelli di prova della fonte:** R = osservato a runtime; C = contratto letto nel codice di llm_wiki al commit `e08cfce`; I = inferenza. Le combinazioni sono riportate come nella fonte. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Come leggere questo documento]

## Dettaglio

### Avvertenze della fonte
Nessun finding ha `replicated: true`; i fatti R del confronto vengono dalle prove dei task 002, 015 e 016, non dalla prova P; le fonti 001 e 002 del progetto citano la skill stessa, quindi usarle per confermarla è circolare; il confronto è stato prodotto in sola lettura. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Avvertenze della fonte]

### Contenuto e dove sta in wiki
- Le 12 osservazioni R della prova del 2026-11-13 e i fatti R del 2026-11-08: [[llm-wiki-api-osservazioni-esecuzione-v0-6-13]]. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Osservazioni R della prova runtime (12, tutte R)]
- Le 25 discrepanze skill/codice, con livello e `file:riga` della fonte, confrontate con la wiki e non verificate: [[llm-wiki-api-affermazioni-codice-da-verificare]]. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Discrepanze skill/codice (25) con livello di prova]
- Le differenze fra skill originale e app confermate o nuove in esecuzione: `## Aggiornamenti` di [[llm-wiki-skill-vs-app-v0-6-13]] (nuove D13-D17). [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Osservazioni R della prova runtime (12, tutte R)]
- Il criterio di «provato» del task 038: entrano R e C, le C marcate «from code, not observed at runtime»; le inferenze non entrano nella skill. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Decisioni del task 038 sul criterio di «provato» (T38, 2026-11-13)]
- Il dubbio dell'utente sugli embedding è stato verificato dalla fonte nel codice (C): `graph` non usa embedding; `search` senza embedding non usa l'RRF e riserva il 30% al grafo; gli errori non dipendono dai tempi del grafo. Non verificato dalla factory. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Decisioni del task 038 sul criterio di «provato» (T38, 2026-11-13)]
- Le prove ancora aperte (task 037, 13 voci) e le 8 inferenze passate al 037: gap `llm-wiki-prove-in-esecuzione-aperte` in [[gaps]]. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Prove ancora aperte e vincoli (T37, stato `in progress`, data 2026-11-13)]
- Le otto contraddizioni interne alla wiki del progetto dell'utente sono dichiarazioni della fonte sul suo corpus e non sono riportate come fatti sulla wiki della factory. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Contraddizioni interne alla wiki (CF, 8; affermazioni della fonte, non verificate sul codice)]

### Limiti e gap
I `file:riga` non sono verificati; task 015 e 016, fonti 007-009 e i file del fork della skill non sono stati letti dall'estrazione; la prova dichiara rescan e `pages/write` chiamati solo senza token, mentre il confronto riporta `pages/write` come osservato; il task 037 letto può differire dal commit. [^src: raw/2026-11-22-repo-alm-wiki-evidenze-api.md §Gap evidenti]

## Pagine ricavate o aggiornate
Create: [[llm-wiki-api-osservazioni-esecuzione-v0-6-13]], [[llm-wiki-api-affermazioni-codice-da-verificare]]. Aggiornate (solo in accodamento): [[llm-wiki-skill-vs-app-v0-6-13]], [[llm-wiki-api-locale]], [[llm-wiki-sicurezza]], [[llm-wiki-sincronizzazione-file]], [[llm-wiki-rischi-persistenza]], [[llm-wiki-skill]].

## Gap di questa fonte
- Nuovi: `llm-wiki-prove-in-esecuzione-aperte`, `llm-wiki-affermazioni-codice-da-verificare`.
- Aggiornati, restano aperti: `llm-wiki-skill-punti-da-verificare`, `llm-wiki-api-corpi-handler-non-letti`, `llm-wiki-review-concorrenza-webview`, `llm-wiki-monitoraggio-piu-progetti`, `llm-wiki-api-ui-token-non-letti`.
- Nessun gap chiuso: l'evidenza è una prova su un progetto, non replicata.

## Estratto non promosso a pagina
Non riportato: il nome del progetto di prova, il suo UUID, i percorsi locali e l'indirizzo del remoto del repo dell'utente (esclusione di dati personali di `wiki/purpose.md`). Le otto contraddizioni interne al corpus dell'utente sono solo citate.

## Pagine collegate
[[llm-wiki-api-osservazioni-esecuzione-v0-6-13]], [[llm-wiki-api-affermazioni-codice-da-verificare]], [[2026-11-22-repo-alm-wiki-bozza-skill]], [[llm-wiki-skill-vs-app-v0-6-13]], [[2026-11-21-repo-llm_wiki-api-mcp]], [[gaps]]

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

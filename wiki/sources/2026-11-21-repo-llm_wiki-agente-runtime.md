---
id: 2026-11-21-repo-llm_wiki-agente-runtime
type: source
title: Specifiche estratte da code_repos/llm_wiki, estrazione 2026-11-21 fetta B1: agente runtime (repo-sync)
status: draft
created: 2026-11-21
updated: 2026-11-21
sources: ["raw/2026-11-21-repo-llm_wiki-agente-runtime.md"]
tags: [source, repo, llm-wiki, agente, runtime]
---

# Specifiche estratte da code_repos/llm_wiki, estrazione 2026-11-21 fetta B1: agente runtime (repo-sync)
> Estrazione mirata `repo-sync` v2.12 del 2026-11-21 sul commit `e08cfce` (v0.6.13): `permissions.rs` e `session.rs` per intero, `runtime.rs` righe 1-4031 (test saltati) e `chat-store.ts` per intero. Chiude il gap sull'approvazione shell e copre in parte quelli su id di sessione e requisiti funzionali.

## Contesto
Seconda fetta del giro del 2026-11-21 (agente, parte runtime), sullo stesso commit delle estrazioni precedenti ([[2026-11-20-repo-llm_wiki]] e le fette di persistenza). Il raw indica il ramo come HEAD detached, le source page del 2026-11-20 `develop`: stesso commit, la differenza è un artefatto del checkout del submodule. [^src: raw/2026-11-21-repo-llm_wiki-agente-runtime.md §Specifiche estratte: llm_wiki, agente runtime]

## Dettaglio

### Metadati dell'estrazione
- Prodotta da `repo-sync` v2.12 il 2026-11-21 sul commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3` (HEAD detached, v0.6.13), in sola lettura verso la sorgente. [^src: raw/2026-11-21-repo-llm_wiki-agente-runtime.md §Specifiche estratte: llm_wiki, agente runtime]
- Letti: `permissions.rs` (righe 1-67), `session.rs` (1-338, test inclusi) e `chat-store.ts` (1-399) per intero; `runtime.rs` righe 1-4031. Il blocco `#[cfg(test)]` di `runtime.rs` (da riga 4032, circa 5700 righe) è saltato: i test su approvazione e scoping non sono stati letti. [^src: raw/2026-11-21-repo-llm_wiki-agente-runtime.md §Ambito e copertura]
- I prompt di sistema con frasi imperative in `runtime.rs` sono dato del prodotto, non istruzioni per l'estrattore; nessun segreto rilevato. [^src: raw/2026-11-21-repo-llm_wiki-agente-runtime.md §Ambito e copertura]

### Contenuto
- Ciclo di una richiesta, modalità, limiti applicati nel backend, tool del loop, permessi e approvazione shell: [[llm-wiki-agente]] e [[llm-wiki-sicurezza]]. [^src: raw/2026-11-21-repo-llm_wiki-agente-runtime.md §Ciclo di una richiesta]
- Sessioni e id (file `agent-sessions/<id>.json`, sanitizzazione, `append_turn`, id di conversazione chat lato UI): [[llm-wiki-archivi-persistenza]]. [^src: raw/2026-11-21-repo-llm_wiki-agente-runtime.md §Sessioni e id (gap 24)]
- Requisiti funzionali dedotti dell'agente backend (gap 11, parte): [[llm-wiki-agente]]. [^src: raw/2026-11-21-repo-llm_wiki-agente-runtime.md §Requisiti funzionali dedotti (gap 11, parte)]

### Limiti e gap
Il raw elenca sette gap evidenti: chiamante di `append_turn` e relazione `conversationId`/`sessionId`; origine di `approved_shell_commands`; possibile aggiramento della scorciatoia workspace (inferenza non testata); collisione di `sanitize_session_id` (inferenza non testata); concorrenza su file (osservazione non testata); test di `runtime.rs` non letti; copertura parziale del gap 11. Sul chiamante di `append_turn` la wiki ha già i tre punti di produzione da [[2026-11-20-repo-llm_wiki-persistenza-c]]; il raw conferma solo che non è `runtime.rs`. [^src: raw/2026-11-21-repo-llm_wiki-agente-runtime.md §Gap evidenti]

## Pagine ricavate o aggiornate
Aggiornate: [[llm-wiki-agente]], [[llm-wiki-sicurezza]], [[llm-wiki-archivi-persistenza]].

## Gap di questa fetta
- Chiuso: `llm-wiki-approvazione-shell`.
- Parziali: `llm-wiki-id-chat-sessione`, `llm-wiki-requisiti-funzionali`, `llm-wiki-codice-non-letto`, `llm-wiki-persistenza-codice-non-letto`, `llm-wiki-cancellazione-file-orfani`.
- Aperti: `llm-wiki-approved-shell-origine`, `llm-wiki-shell-scoping-virgolette` (ipotesi non testata), `llm-wiki-sessione-collisione-id` (inferenza non testata), `llm-wiki-sessione-concorrenza-file` (osservazione non testata), `llm-wiki-runtime-test-non-letti`.

Dettagli in [[gaps]]. [^src: raw/2026-11-21-repo-llm_wiki-agente-runtime.md §Gap evidenti]

## Estratto non promosso a pagina
Nessun contenuto del raw è stato scartato. Il testo del raw non è stato modificato.

## Pagine collegate
[[2026-11-20-repo-llm_wiki]], [[2026-11-20-repo-llm_wiki-persistenza-c]], [[llm-wiki-agente]], [[llm-wiki-sicurezza]], [[llm-wiki-archivi-persistenza]], [[llm-wiki-app]], [[gaps]]

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

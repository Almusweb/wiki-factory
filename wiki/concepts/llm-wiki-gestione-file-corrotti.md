---
id: llm-wiki-gestione-file-corrotti
type: concept
title: llm-wiki — gestione dei file corrotti
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: ["raw/2026-11-20-repo-llm_wiki.md"]
tags: [llm-wiki, dati, persistenza, resilienza, db]
---

# llm-wiki — gestione dei file corrotti
> Quasi tutti i caricamenti ripiegano su un valore vuoto o di default senza quarantena, backup del file corrotto o segnale all'utente; la prima scrittura successiva sostituisce il file corrotto.

## Contesto
Pagina ricavata dalla seconda estrazione sulla persistenza (commit `e08cfce`), sui 21 file letti. Elenca il comportamento osservato nel codice per ciascun archivio; gli archivi sono in [[llm-wiki-archivi-persistenza]]. [^src: raw/2026-11-20-repo-llm_wiki.md §Gestione dei file corrotti]

## Dettaglio

- **Regola generale.** Quasi tutti i caricamenti usano un `try/catch` che restituisce un valore vuoto o di default (`persist.ts`, `ingest-cache.ts`, `dedup-storage.ts`, `ingest-queue.ts`, `lint-config.ts`, `scheduled-import.ts`). Nessuna rinomina in quarantena, nessun backup del file corrotto, nessun segnale all'utente nel campione (al massimo un avviso in console). [^src: raw/2026-11-20-repo-llm_wiki.md §Gestione dei file corrotti]
- **Effetto della prima scrittura dopo un file corrotto.** Dove il caricamento ricade sul valore vuoto e la scrittura successiva salva l'intero contenuto (coda, cache di ingest, elenco «non duplicati», database di scheduled import), il file corrotto viene sostituito dal nuovo contenuto. [^src: raw/2026-11-20-repo-llm_wiki.md §Gestione dei file corrotti]
- **Sessioni agente** (`agent/session.rs`). `list_sessions` salta i file non leggibili. `append_turn` però carica la sessione con ripiego sul valore vuoto e poi salva: un file corrotto verrebbe quindi sostituito al turno successivo. La scrittura è diretta, non atomica. [^src: raw/2026-11-20-repo-llm_wiki.md §Gestione dei file corrotti]
- **Chat** (`persist.ts`). Se `conversations.json` manca o non si legge, `loadChatHistory` ricostruisce un indice minimo dai file `chats/*.json`, ignorando i file corrotti uno alla volta; se serve, prova poi il vecchio formato. Titolo della conversazione ricostruita: i primi 50 caratteri del primo messaggio utente, oppure «Previous Conversation». [^src: raw/2026-11-20-repo-llm_wiki.md §Gestione dei file corrotti]
- **Cronologia file** (`file_history.rs`). I file non leggibili sono saltati in conteggio e potatura; sono rimossi quando la cronologia viene disattivata a limite 0. Rifiuta symlink per impostazioni, cartella e singoli file. [^src: raw/2026-11-20-repo-llm_wiki.md §Gestione dei file corrotti]
- **Identità del progetto** (`project-identity.ts`). File mancante o corrotto: nuovo UUID e sovrascrittura. Conseguenze dedotte in [[llm-wiki-rischi-persistenza]]. [^src: raw/2026-11-20-repo-llm_wiki.md §Gestione dei file corrotti]
- **Embedding** (`page_embedding.rs`). La revisione illeggibile o vuota è trattata come assente. Un errore nel salvare i metadati di revisione invalida la revisione e non fallisce la scrittura dei vettori. [^src: raw/2026-11-20-repo-llm_wiki.md §Gestione dei file corrotti]
- **LanceDB.** Nessuna gestione dedicata: gli errori di connessione, apertura o scrittura sono propagati come messaggi di testo; nel percorso TS di ricerca un errore produce un elenco vuoto con messaggio di log. [^src: raw/2026-11-20-repo-llm_wiki.md §Gestione dei file corrotti]
- **`app-state.json`.** `loadRegistry` ritorna un registro vuoto in caso di errore. Per le altre chiavi dipende dal comportamento del plugin store, non verificato. [^src: raw/2026-11-20-repo-llm_wiki.md §Gestione dei file corrotti]

## Pagine collegate
[[llm-wiki-archivi-persistenza]], [[llm-wiki-operazioni-distruttive]], [[llm-wiki-rischi-persistenza]]. Gap aperto: [[gaps]] (`llm-wiki-app-state-percorso`).

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

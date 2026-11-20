---
id: llm-wiki-gestione-file-corrotti
type: concept
title: llm-wiki — gestione dei file corrotti
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: ["raw/2026-11-20-repo-llm_wiki.md", "raw/2026-11-20-repo-llm_wiki-persistenza-a.md", "raw/2026-11-20-repo-llm_wiki-persistenza-b.md"]
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
- US-014 — Posizione e ciclo di vita dello store applicativo e dell'area dati di progetto (gap `llm-wiki-app-state-percorso`)
- US-021 — Schema degli archivi per progetto
- US-026 — Rischio 2: rigenerazione dell'identità del progetto
- US-027 — Rischio 3: scritture non serializzate sul registro dei progetti

## Aggiornamenti (v2026-11-20)
Dalle fette A e B delle estrazioni mirate sulla persistenza ([[2026-11-20-repo-llm_wiki-persistenza-a]], [[2026-11-20-repo-llm_wiki-persistenza-b]]). Il testo sopra non è modificato. Archivi in [[llm-wiki-archivi-persistenza]]; qualificatori («osservato», «deduzione», «non verificato») come nel raw.

### `app-state.json`: comportamento lato Rust (osservato)
- Agente: su store illeggibile la lettura restituisce «assente»; configurazione di default e nessun progetto dal registro; un progetto non trovato produce l'errore «Unknown project». [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Store applicativo (`app-state.json`)]
- Proxy all'avvio: nessuna configurazione e log «requests go direct». [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Store applicativo (`app-state.json`)]
- API: se la rilettura fallisce si riusa l'ultimo valore in cache, senza valore precedente il risultato è «assente». Con stato assente il token manca (risposta 401 su ogni endpoint tranne `/health`) mentre il flag `enabled` vale vero per default. Vedi [[llm-wiki-api-locale]] e [[llm-wiki-sicurezza]]. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Store applicativo (`app-state.json`)]
- Per le conversioni in struct delle chiavi lette dal Rust l'esito scarta in silenzio i valori non deserializzabili: osservato per la copia in `api_server.rs`, deduzione per la copia in `lib.rs`. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Punto 4: lettori di `app-state.json` in `api_server.rs`]

### `app-state.json`: comportamento lato TS
- Osservato: `loadRegistry` ha try/catch e restituisce un registro vuoto; gli altri caricamenti di `project-store.ts` non hanno gestione degli errori. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Store applicativo (`app-state.json`)]
- Deduzione dal codice, non osservata in esecuzione: l'inizializzazione di `App.tsx` è in un try con catch che ignora l'errore e finally che spegne il caricamento; se l'apertura dello store rifiuta, le altre configurazioni non vengono caricate e l'ultimo progetto non viene riaperto, senza avviso all'utente. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Store applicativo (`app-state.json`)]
- Non verificato: il comportamento del plugin store su file corrotto (sorgente e documentazione del plugin non disponibili offline). Il comportamento di tutte le chiavi lette via plugin lato TS resta quindi sconosciuto oltre a `loadRegistry`. Gap `llm-wiki-app-state-percorso` ancora aperto. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Store applicativo (`app-state.json`)]

### Archivi della fetta B
- `file-snapshot.json` e `file-change-queue.json`: su JSON illeggibile `read_json` restituisce un errore (`Failed to parse`) invece del valore vuoto; se il file manca restituisce il default. È l'eccezione al ripiego silenzioso della maggior parte dei caricamenti TS. Vedi [[llm-wiki-sincronizzazione-file]]. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Sincronizzazione e osservazione dei file]
- `dedup-queue.json`: un file illeggibile dà una coda vuota; scrittura diretta con errori ignorati. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Coda di dedup e lint]
- `image-caption-cache.json` mancante o corrotto: mappa vuota con avviso in console. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Cache di ingest, didascalie e checkpoint]
- `ingest-cache.json` e `ingest-queue.json`: scritture dirette con errori ignorati (in `ingest-queue.ts` le scritture sono serializzate in processo da una coda di richieste); un crash in scrittura non è mitigato da file temporaneo e rinomina (osservato per la scrittura, impatto dedotto). [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Atomicità per archivio]
- Markdown estratto: `moveParsedMarkdown` tollera un errore di cancellazione della vecchia copia (preferisce un duplicato a una migrazione fallita); la cache Office `.cache` rimuove il marcatore `.txt.parser` prima di rimpiazzare il contenuto, così un crash può causare solo una ricostruzione in più. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §File e cartelle citati e non verificati]

## Contradictions
- **Chiavi diverse da `loadRegistry`.** Prima (voce `app-state.json`): «Per le altre chiavi dipende dal comportamento del plugin store, non verificato». Ora (fetta A): è osservato il comportamento lato Rust (agente, proxy, API ripiegano su assente, default o cache) e che gli altri caricamenti TS di `project-store.ts` non hanno gestione degli errori; il comportamento del plugin resta non verificato. Estensione del testo, nessuna contraddizione sul plugin. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Store applicativo (`app-state.json`)]
- **Regola generale.** Prima: «Quasi tutti i caricamenti ripiegano su un valore vuoto o di default senza segnale all'utente». Ora (fetta B): per `file-snapshot.json` e `file-change-queue.json` `read_json` su JSON illeggibile restituisce un errore e ripiega sul default solo se il file manca. È un'eccezione alla regola (la pagina dice «quasi»), non una smentita totale. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Sincronizzazione e osservazione dei file]

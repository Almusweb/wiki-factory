---
id: llm-wiki-gestione-file-corrotti
type: concept
title: llm-wiki — gestione dei file corrotti
status: draft
created: 2026-11-20
updated: 2026-11-21
sources: ["raw/2026-11-20-repo-llm_wiki.md", "raw/2026-11-20-repo-llm_wiki-persistenza-a.md", "raw/2026-11-20-repo-llm_wiki-persistenza-b.md", "raw/2026-11-21-repo-llm_wiki-persistenza-d.md", "raw/2026-11-21-repo-llm_wiki-dossier-ep004-r2.md", "raw/2026-11-21-repo-llm_wiki-dossier-ep004-r4.md"]
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

## Aggiornamenti (v2026-11-21, fetta D)
Dalla fetta D ([[2026-11-21-repo-llm_wiki-persistenza-d]]). Il testo sopra non è modificato. «Osservato» = letto nel codice; «deduzione non testata» = mai eseguita. Le righe `store.rs` e `lib.rs` del plugin sono sorgenti della dipendenza `tauri-plugin-store` 2.4.3 da crates.io, **non codice del cliente**. Percorso del file per sistema operativo: [[llm-wiki-archivi-persistenza]].

### Plugin store su `app-state.json` corrotto (osservato)
- La costruzione dello store chiama il caricamento da disco e **ignora l'esito** (`let _ =`, `store.rs:218-224`): un errore di lettura o di deserializzazione non interrompe la creazione e non arriva al chiamante; il comando `load` ritorna solo l'identificativo di risorsa (`lib.rs:130-133`). [^src: raw/2026-11-21-repo-llm_wiki-persistenza-d.md §File corrotto: che cosa si legge nel plugin]
- Il caricamento aggiunge le chiavi alla cache solo se la deserializzazione riesce (`store.rs:304-311`): nessuna unione parziale. La deserializzazione è JSON verso una mappa chiave-valore (`lib.rs:333-337`): file vuoto, JSON troncato o radice non oggetto sono errori. La cache parte dai default, vuoti dal TS (`store.rs:280-288`). [^src: raw/2026-11-21-repo-llm_wiki-persistenza-d.md §File corrotto: che cosa si legge nel plugin]
- Il salvataggio scrive l'intera cache con `fs::write` sul percorso finale, senza temporaneo, rinomina o copia di riserva (`store.rs:291-299`); `set` e `delete` attivano il salvataggio automatico con debounce di 100 ms. [^src: raw/2026-11-21-repo-llm_wiki-persistenza-d.md §File corrotto: che cosa si legge nel plugin]

### Conseguenze (deduzione non testata, mai eseguite)
1. All'avvio con file corrotto lo store risulta vuoto, senza errore né avviso visibile al TS; i getter di `project-store.ts` rispondono `[]` o `null` (righe 16-26; gli altri getter non riletti).
2. Il file corrotto resta su disco finché non c'è una scrittura; alla prima `set`, `delete` o `clear` viene riscritto con la sola cache corrente: contenuto corrotto e chiavi non ricaricate sono perse, senza copia.
3. Un'interruzione a metà di `fs::write` può lasciare un file troncato (comportamento di `std`, non letto): via per arrivare al caso «corrotto».
4. Una scrittura del plugin può sovrapporsi a una lettura dei lettori Rust, che vedrebbero un file troncato o vuoto; nessun lock condiviso nelle righe lette.
[^src: raw/2026-11-21-repo-llm_wiki-persistenza-d.md §File corrotto: che cosa si legge nel plugin]

### Lettori Rust su file mancante o JSON non valido (osservato)
| Punto | Comportamento | Fonte |
|---|---|---|
| Runtime dell'agente | errore di lettura o analisi, «nessun valore», configurazione di default; nessun log | `src-tauri/src/lib.rs:405-414` |
| Proxy all'avvio | «nessuno»; log «no proxyConfig in store, requests go direct»; nessun proxy applicato | `proxy.rs:61-69`, `lib.rs:581-589` |
| Stato per l'API | analisi fallita: si tiene il valore precedente in cache, se c'è; altrimenti «nessun valore»; il risultato è messo in cache | `api_server.rs:727-753` |
| Host di bind | errore: «nessun valore», si usa `DEFAULT_BIND_HOST` (valore non letto) | `server_bind.rs:22-31` |

[^src: raw/2026-11-21-repo-llm_wiki-persistenza-d.md §File corrotto: i lettori Rust]
- Non risulta un test su file corrotto in `proxy.rs:491-518` (righe 85-490 non lette). Deduzione non testata: con file corrotto il proxy è spento, l'agente parte con la configurazione di default, il bind torna al valore predefinito; solo l'API ha un ripiego sull'ultimo stato valido, e solo se la cache era già popolata. Effetti sul token dell'API non letti in questa fetta. Il Rust non scrive `app-state.json` nei punti letti. [^src: raw/2026-11-21-repo-llm_wiki-persistenza-d.md §File corrotto: i lettori Rust]
- **Residuo:** pacchetto JavaScript del plugin, `tauri/src/path/mod.rs`, `dirs-sys` non letti; nessuna prova in esecuzione. [^src: raw/2026-11-21-repo-llm_wiki-persistenza-d.md §Gap evidenti]

## Aggiornamenti (v2026-11-21, dossier r2)
Dal dossier [[2026-11-21-repo-llm_wiki-dossier-ep004-r2]] (commit `e08cfce`, sola lettura). Il testo sopra non è modificato; esito completo in [[llm-wiki-rischi-persistenza]] §Esito della verifica di US-026.
- **Identità del progetto, `project.json` illeggibile (osservato).** `ensureProjectId` (`project-identity.ts:47-68`) tratta allo stesso modo file assente, illeggibile per qualunque errore, non JSON, senza `id` o con `id` vuoto: nuovo UUID, nuovo `createdAt`, sovrascrittura senza copia; il vecchio id non è conservato. Se la scrittura fallisce resta solo un `console.warn` e l'id è effimero. Alla ripartenza `restoreQueue` scarta i task con il vecchio id e riscrive `ingest-queue.json` (`ingest-queue.ts:985-1004`): lo scarto è permanente su disco. Le impostazioni per id tornano a default o globale. Esito del rischio: confermato per lettura; innesco non conclusivo. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r2.md §Esito proposto: CONFERMATO per lettura (con una riserva sul negativo)]
- **Deduzione non testata:** un errore di lettura transitorio potrebbe sostituire un `project.json` valido; il comportamento di `read_file` Rust su errore transitorio non è stato letto. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r2.md §Passo 2. Generazione del nuovo id in `ensureProjectId` (osservato)]

## Aggiornamenti (v2026-11-21, dossier r3)
Dal dossier [[2026-11-21-repo-llm_wiki-dossier-ep004-r3]] (commit `e08cfce`, sola lettura). Il testo sopra non è modificato; esito completo in [[llm-wiki-rischi-persistenza]] §Esito della verifica di US-027.
- **`loadRegistry`: errore e chiave assente indistinguibili (osservato).** Qualsiasi eccezione di `getStore()` o `get` ritorna `{}`, senza log né flag (`project-identity.ts:76-84`); un successivo `upsertProjectInfo` scrive una sola voce sostituendo la chiave (`project-identity.ts:86-108`). Con `app-state.json` corrotto non è `loadRegistry` a perdere i dati ma il file (deduzione non testata, già nella fetta D). Esito del rischio 3: confermato per lettura sul meccanismo, concorrenza reale non conclusiva. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r3.md §2. Percorso «lettura fallita, poi scrittura» (AC3)]

## Aggiornamenti (v2026-11-21, dossier r4)
Dal dossier [[2026-11-21-repo-llm_wiki-dossier-ep004-r4]] (commit `e08cfce`, sola lettura) e dalla ricerca testuale globale (TSK-022 §Chiusura). Il testo sopra non è modificato; esito completo in [[llm-wiki-rischi-persistenza]] §Esito della verifica di US-028. «Troncato o vuoto» è raggiungibile in teoria da `fs::write` (deduzione non testata, `std` non letto).
- **Reazione del lettore per archivio (osservato):** sessioni agente, `history/<hash>.json`, `review.json`, `lint.json`, `chat-preferences.json`, `ingest-cache.json`, `dedup-not-duplicates.json`, `ingest-queue.json`, `scheduled-import-db.json`: ripartenza vuota, senza segnale (al massimo un avviso in console, `lint-config.ts:37`, `scheduled-import.ts:379`); la scrittura successiva sostituisce il file. Sessioni agente: `load_session` → «nessun valore», `append_turn` parte vuota (`session.rs:54, 72, 160-164`), perdita dello storico fino a 40 messaggi. Cronologia: la scrittura successiva salva solo la voce nuova (`file_history.rs:267-286`), potatura che salta il file illeggibile (221-224). Chat: indice illeggibile → recupero parziale dai file orfani `chats/*.json` (`persist.ts:143-144, 205-242`), perdita dei titoli. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r4.md §2. Che cosa resta dopo un crash e come reagisce il lettore (AC3, AC5)]
- **`history-settings.json` illeggibile spegne la cronologia (osservato).** Default `enabled` falso (`file_history.rs:42-48, 71-81`), `record_file_version` esce a 245: funzione disattivata in silenzio; un salvataggio successivo vede «nessuna impostazione» (318-323) ed esegue la potatura (327-329). Non è un default neutro. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r4.md §2. Che cosa resta dopo un crash e come reagisce il lettore (AC3, AC5)]
- **Eccezione: `file-snapshot.json` e `file-change-queue.json` (osservato).** File assente → default (`file_sync.rs:1339-1341`); presente ma non analizzabile → errore `Failed to parse` (1344), propagato ai siti letti. Nella finestra Windows di `write_json` il file finale non esiste e un lettore senza lock vede il default (vedi [[llm-wiki-archivi-persistenza]] §Aggiornamenti dossier r4). Se un file non analizzabile resti tale dipende da `file_sync.rs` 705-1280, non letto. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r4.md §3. Finestra non atomica su Windows (AC4)]
- **Nessuna quarantena, nessun recupero, nessuna pulizia (ricerca globale, ambito `src-tauri/src` e `src`, esclusi i test).** Nessun meccanismo di quarantena o recupero di file corrotti (`quarantine`, `.corrupt`, `recover`: solo occorrenze non pertinenti; `.bak` solo in `agent/tools.rs:807`, scritture dell'agente) e nessuna pulizia dei temporanei orfani (`.tmp`, `tmp-`). Estende al codice intero il negativo del dossier, limitato alle righe lette. [^src: management/kanban/EP-004-verifica-rischi-di-persistenza/US-028-rischio-atomicita-eterogenea/TSK-022.md §Chiusura]

## Contradictions
- **Identità del progetto: «nuovo UUID e sovrascrittura» e `loadRegistry`.** Prima (voce «Identità del progetto»): file mancante o corrotto, nuovo UUID e sovrascrittura, conseguenze dedotte altrove. Ora (dossier r2): le conseguenze sono lette (scarto permanente dei task su disco, ripiego delle impostazioni su default o globale); inoltre l'apertura dello store e le chiavi per id stanno in `project-store.ts`, non in `persist.ts` (che non accede ad `app-state.json`). Estensione del dato, nessuna smentita. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r2.md §Gap evidenti]
- **Plugin store «non verificato» (fetta D).** Prima («`app-state.json`: comportamento lato TS» e voce `app-state.json`): comportamento del plugin su file corrotto «non verificato (sorgente e documentazione non disponibili offline)»; gap `llm-wiki-app-state-percorso` aperto. Ora (fetta D): il sorgente del plugin 2.4.3 è letto (errore ignorato, store vuoto, prima scrittura riscrive il file con la sola cache); le conseguenze restano deduzioni non testate. Il gap è chiuso con riserva, vedi [[gaps]]. [^src: raw/2026-11-21-repo-llm_wiki-persistenza-d.md §Esiti A, in breve]
- **`loadRegistry` e «altre chiavi».** Prima: `loadRegistry` ripiega su registro vuoto, il resto dipende dal plugin. Ora: il plugin non propaga l'errore di caricamento, quindi `loadRegistry` non è l'unico percorso protetto; i getter restituiscono `[]` o `null` su chiave mancante (osservato per quelli letti). Estensione, non smentita. [^src: raw/2026-11-21-repo-llm_wiki-persistenza-d.md §File corrotto: che cosa si legge nel plugin]
- **Chiavi diverse da `loadRegistry`.** Prima (voce `app-state.json`): «Per le altre chiavi dipende dal comportamento del plugin store, non verificato». Ora (fetta A): è osservato il comportamento lato Rust (agente, proxy, API ripiegano su assente, default o cache) e che gli altri caricamenti TS di `project-store.ts` non hanno gestione degli errori; il comportamento del plugin resta non verificato. Estensione del testo, nessuna contraddizione sul plugin. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Store applicativo (`app-state.json`)]
- **Regola generale.** Prima: «Quasi tutti i caricamenti ripiegano su un valore vuoto o di default senza segnale all'utente». Ora (fetta B): per `file-snapshot.json` e `file-change-queue.json` `read_json` su JSON illeggibile restituisce un errore e ripiega sul default solo se il file manca. È un'eccezione alla regola (la pagina dice «quasi»), non una smentita totale. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-b.md §Sincronizzazione e osservazione dei file]
- **Regola generale e `history-settings.json` (dossier r4).** Prima: «ripiegano su un valore vuoto o di default senza segnale». Ora: confermata per tutti i lettori riletti, con l'eccezione di `file_sync.rs`; ma per `history-settings.json` il default non è neutro, spegne la cronologia (`file_history.rs:42-48, 71-81`). Precisazione dell'impatto, non smentita. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r4.md §4. Correzioni e precisazioni rispetto alla fetta D (riepilogo)]
- **Eccezione `file_sync.rs`: «ripiega sul default solo se il file manca».** Prima (fetta B): errore su JSON illeggibile, default se manca. Ora (dossier r4): confermata con righe (`file_sync.rs:1339-1344`, siti 475, 514, 578, 640, 677); nella finestra Windows di `write_json` il file manca e il lettore senza lock vede il default senza errore. [^src: raw/2026-11-21-repo-llm_wiki-dossier-ep004-r4.md §3. Finestra non atomica su Windows (AC4)]
- **«Nessuna quarantena» limitata alle righe lette.** Prima: il dossier r4 dichiarava il negativo valido per i 13 file letti. Ora: esteso a `src-tauri/src` e `src` (esclusi i test) dalla ricerca globale della sessione principale: nessuna quarantena, recupero o pulizia dei temporanei; `.bak` solo in `agent/tools.rs:807`. [^src: management/kanban/EP-004-verifica-rischi-di-persistenza/US-028-rischio-atomicita-eterogenea/TSK-022.md §Chiusura]

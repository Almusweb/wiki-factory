---
id: 2026-11-21-issues-llm_wiki-chiuse
type: source
title: Issue chiuse di nashsu/llm_wiki, 2026-11-21: dichiarazioni e controlli puntuali su v0.6.13 per i gap aperti (github-issues)
status: draft
created: 2026-11-21
updated: 2026-11-21
sources: ["raw/2026-11-21-issues-llm_wiki-chiuse.md"]
tags: [source, github-issues, llm-wiki, sicurezza, clip-server, persistenza, dichiarazioni]
---

# Issue chiuse di nashsu/llm_wiki, 2026-11-21: dichiarazioni e controlli puntuali su v0.6.13 per i gap aperti (github-issues)
> **Linea:** upstream v0.6.13, commit `e08cfce65aad8b76b13546a081c1a8d4422b70c3`; branch `develop`, che coincide con `main` al commit indicato (così il raw). Estratto della sessione principale del 2026-11-21 (`gh` 2.101.0, lettura pubblica), stato `partial`. **Natura della fonte: dichiarazioni, non osservazioni.** Le etichette del raw sono conservate alla lettera: «Dichiarato (segnalatore)», «Dichiarato (maintainer)», «Osservato v0.6.13» (letto nel codice con file e righe, mai eseguito). Un dato dichiarato non chiude da solo un gap. Repo di terzi sotto GNU GPL v3: solo nomi di file, simboli e righe, nessun frammento di codice; nessun valore di segreto. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §Identità e perimetro]

## Contesto
Le 362 issue chiuse del repository upstream `nashsu/llm_wiki` sono state lette per titolo e circa 40 per intero, poi confrontate con 55 gap aperti di [[gaps]] (quelli senza «Risolto» al 2026-11-21 22:10). I controlli «Osservato v0.6.13» sono `grep -n` e `sed -n` sul submodule `code_repos/llm_wiki`, in sola lettura. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §Identità e perimetro]

Avvertenze di lettura:
- **«Chiusa come completata» non vuol dire «corretta»**: la #318 è chiusa come completata il 2026-06-06 senza alcun commento e tre dei sei difetti segnalati sono presenti in v0.6.13 (vedi sotto, tabella dei sei punti); la #648 è rimasta chiusa con una dichiarazione contraria del segnalatore. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §Identità e perimetro]
- **Dati di terzi**: le misure delle issue vengono da progetti di singoli utenti, su versioni vecchie; non sono dati del cliente né di un progetto sintetico della factory. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §Identità e perimetro]
- **Copertura e metodo**: la ricerca per parole chiave è fatta con uno script nello scratchpad della sessione principale, non versionato, quindi non riproducibile da qui. Un «non trovato» (per esempio «nessuna issue cita `cargo test`») vale per quanto letto, non per l'intero archivio. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §Identità e perimetro]

## Dettaglio

### 1. Clip server: indirizzo di ascolto, CORS e token
- **Dichiarato (segnalatore), #474, v0.5.1:** API (porta 19828) e Clip server (porta 19827) ascoltavano solo su `127.0.0.1`, scritto nel codice. **Dichiarato (maintainer), #474, chiusa 2026-06-30, v0.5.4:** indirizzo di ascolto configurabile con la variabile `LLM_WIKI_BIND_HOST` e con l'opzione «Allow API and Clip server access from the local network»; con l'opzione attiva, dopo il riavvio, entrambi ascoltano su `0.0.0.0`; il default resta `127.0.0.1`; la UI avverte di tenere attivo il token. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §1. Clip server: indirizzo di ascolto, CORS e token]
- **Dichiarato (maintainer), #510, chiusa 2026-08-25, v0.6.5:** l'estensione Chrome può collegarsi al Clip server tramite l'IP di rete locale; consiglia di tenere attiva l'autenticazione a token. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §1. Clip server: indirizzo di ascolto, CORS e token]
- **Osservato v0.6.13, bind:** il Clip server ricava l'indirizzo con le stesse funzioni dell'API, `server_bind::configured_bind_host` e `server_bind::bind_addr` (`clip_server.rs:63-64`, `api_server.rs:135-136`); ordine: variabile d'ambiente, valore nello store, default (`server_bind.rs:10-14`). [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §1. Clip server: indirizzo di ascolto, CORS e token]
- **Osservato v0.6.13, CORS:** `Access-Control-Allow-Origin` solo per origini in elenco (`chrome-extension://`, `moz-extension://`, `http://localhost`, `http://127.0.0.1` e `http://[::1]` con o senza porta, `tauri://localhost`, `http://tauri.localhost`, `https://tauri.localhost`), con `Vary: Origin` e `Access-Control-Allow-Private-Network: true` (`cors.rs:11-41`); il Clip server usa questa funzione (`clip_server.rs:324-325`). [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §1. Clip server: indirizzo di ascolto, CORS e token]
- **Osservato v0.6.13, token:** una richiesta non di loopback senza token valido riceve 401; una richiesta di loopback passa senza token (il commento del codice parla di comportamento precedente alla rete locale, per l'app e le estensioni vecchie) (`clip_server.rs:118-134, 328-336`); il token è lo stesso dell'API, confronto a tempo costante, da query `token`, header `X-LLM-Wiki-Token` o `Authorization: Bearer` (`clip_server.rs:349`, `api_server.rs:593-618`); senza token configurato `is_token_authorized` dà falso (`api_server.rs:598-600`). [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §1. Clip server: indirizzo di ascolto, CORS e token]

### 2. Clip server: fatti nuovi per la sicurezza
- **Dichiarato (segnalatore), #318, 2026-06-01** (audit di sicurezza in sei punti): il Clip server accetta corpi senza limite di dimensione; `/clip` accetta un `projectPath` dal corpo e scrive Markdown in `<projectPath>/raw/sources/`; CORS `*`; nessuna autenticazione. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §2. Clip server: fatti nuovi per la sicurezza (nessun gap esistente)]
- **Osservato v0.6.13, corpo senza limite:** `POST /project`, `POST /projects` e `POST /clip` leggono il corpo con `read_to_string` su `request.as_reader()`, senza limite nelle righe lette (`clip_server.rs:163-165, 216-218, 266-268`); nel file le sole costanti `MAX_` riguardano i tentativi di bind e di riavvio (`:18-19`). [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §2. Clip server: fatti nuovi per la sicurezza (nessun gap esistente)]
- **Osservato v0.6.13, `projectPath` non confrontato col registro:** il gestore della clip usa il `projectPath` del corpo, se presente, altrimenti il progetto corrente; lo normalizza (barre), lo rifiuta solo se vuoto, crea `<projectPath>/raw/sources` con `create_dir_all` e vi scrive `<slug>-<data>.md` (`clip_server.rs:411-428, 456-492`); nelle righe 408-512 non c'è alcun confronto con il registro dei progetti né con i progetti recenti. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §2. Clip server: fatti nuovi per la sicurezza (nessun gap esistente)]
- **Deduzione non testata** (così nel raw; non eseguita): combinato con il loopback senza token, un processo locale qualsiasi dell'utente potrebbe creare un file Markdown in `<percorso a scelta>/raw/sources/` dove l'utente ha permessi di scrittura, e accodarlo fra le clip in attesa (`clip_server.rs:504-508`). [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §2. Clip server: fatti nuovi per la sicurezza (nessun gap esistente)]

### 3. Dimensioni reali degli archivi (misure di terzi)
Tutti i dati sono «Dichiarato (segnalatore)», da un solo progetto ciascuno, sulla versione indicata. Non sono misure del progetto. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §3. Dimensioni reali degli archivi (gap `llm-wiki-archivi-dimensioni`)]

| Issue | Versione | Progetto | Misura dichiarata | Esito dichiarato dal maintainer |
|---|---|---|---|---|
| #398 | v0.4.23, macOS | 6.445 pagine, 44.879 chunk | indice LanceDB 3,8 GB: `_versions/` 3,6 GB (13.125 manifest), `_transactions/` 51 MB, `data/` 216 MB (94,7% versioni vecchie); dopo pulizia e compattazione manuali 195 MB | v0.4.24: pulizia delle versioni e compattazione a fine ricostruzione o indicizzazione |
| #397 | v0.4.23, macOS | 6.566 pagine, circa 46.000 chunk | ricostruzione dell'indice oltre 2 ore, embedding locale a circa 0,16 s per richiesta, esecuzione seriale | v0.6.12: concorrenza configurabile, limite portato a 64 per embedding, elaborazione documenti, descrizione immagini e ingest |
| #641 | non indicata (agosto 2026) | non indicato | `.llm-wiki/history`: «migliaia» di file JSON | v0.6.9: cronologia disattivata per default, conservazione configurabile da 0 a 30 versioni, comandi di disattivazione e pulizia in Impostazioni → Manutenzione; un contributore (non il maintainer) dichiara limiti di 2.048 file e 128 MB e potatura solo alla scrittura di una nuova voce, quindi i file vecchi restano se la funzione è spenta |
| #469 | non indicata | 16 libri PDF | 5.064 PNG di pagine intere, 2,2 GB | (richiesta di estrarre solo le immagini incorporate) |
| #714 | v0.6.11, macOS | 4.359 pagine, 16.417 archi distinti | `GET /graph` circa 24 s a ogni richiesta, poi blocco dell'endpoint dopo alcune richieste | v0.6.12: paginazione, totale, cache per progetto con ricostruzione all'invalidazione |

I limiti di codice già in wiki per la cronologia (128 MiB e 2.048 file) coincidono con quelli dichiarati dal contributore in #641; il segnalatore dichiara «migliaia» di file senza numero esatto, quindi non si può dire se il limite di 2.048 sia stato raggiunto. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §3. Dimensioni reali degli archivi (gap `llm-wiki-archivi-dimensioni`)]

### 4. Nomi di pagina rifiutati dall'indice vettoriale
- **Dichiarato (segnalatore), #394 e #396, v0.4.23:** 447 pagine su 6.566 (6,8%) rifiutate dalla validazione di `page_id`, che allora ammetteva solo lettere, cifre, `-`, `_`, `.`; rifiuto silenzioso. **Dichiarato (maintainer), #396, chiusa 2026-06-16, v0.4.24:** validazione allargata, rifiuta solo caratteri pericolosi per i percorsi e di controllo. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §4. Nomi di pagina rifiutati dall'indice vettoriale (gap `llm-wiki-reindex-page-id-concorrenza-reale`)]
- **Dichiarato (segnalatore), #770, v0.6.11:** pagine con lo stesso nome di file in cartelle diverse (anche solo per maiuscole) rifiutate dall'API di embedding con 409; nell'ingest, sovrascrittura silenziosa dei vettori. **Dichiarato (maintainer), #770, chiusa 2026-09-27, v0.6.12:** identità di pagina con la cartella, in API, ingest, ricerca, cancellazione, revisioni e sincronizzazione. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §4. Nomi di pagina rifiutati dall'indice vettoriale (gap `llm-wiki-reindex-page-id-concorrenza-reale`)]
- **Osservato v0.6.13:** `validate_page_id_common` rifiuta solo stringa vuota, oltre 256 caratteri (`MAX_PAGE_ID_CHARS`, `vectorstore.rs:67`), caratteri di controllo, `\`, `'`, `"` e un insieme di caratteri invisibili o di formattazione (`vectorstore.rs:78-114`); ideogrammi e punteggiatura CJK passano. **Deduzione non testata:** il 6,8% vale per la regola di v0.4.23 e non stima la frequenza attuale, che riguarda solo nomi con apici, barre inverse o caratteri invisibili. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §4. Nomi di pagina rifiutati dall'indice vettoriale (gap `llm-wiki-reindex-page-id-concorrenza-reale`)]

### 5. Id di pagina TS e Rust
- **Osservato v0.6.13, TS:** `wikiPageIdFromPath` toglie il prefisso `<progetto>/wiki/` o `wiki/`; se il percorso non ha quei prefissi e contiene `/` restituisce stringa vuota; se è un nome senza `/` lo accetta; toglie le barre iniziali e `.md` finale senza distinzione di maiuscole (`embedding.ts:450-462`). [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §5. Id di pagina TS e Rust (gap `llm-wiki-coppie-id-pagina-non-confrontate`)]
- **Osservato v0.6.13, Rust:** `vector_page_id` converte `\` in `/`, richiede il prefisso `wiki/` e il suffisso `.md` (senza distinzione di maiuscole), toglie barre iniziali e finali, rifiuta il risultato vuoto (`page_embedding.rs:282-290`). [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §5. Id di pagina TS e Rust (gap `llm-wiki-coppie-id-pagina-non-confrontate`)]
- **Esito:** caso normale `wiki/<cartella>/<nome>.md`, stesso id (percorso relativo a `wiki/` senza `.md`). Casi limite, osservati per costruzione e non eseguiti: il nome nudo senza `wiki/` è accettato da TS e rifiutato da Rust; un percorso senza `.md` dà un id in TS e nessun id in Rust; le barre finali sono tolte solo da Rust; `\` è convertita da Rust e, in TS, dipende da `normalizePath` (non letto). [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §5. Id di pagina TS e Rust (gap `llm-wiki-coppie-id-pagina-non-confrontate`)]

### 6. Altre dichiarazioni pertinenti
- **Segreti in chiaro:** #318, punto 5, **dichiara** che chiavi API, token dell'API locale e credenziali dei provider stanno in chiaro in `app-state.json` e raccomanda il portachiavi del sistema operativo: conferma indipendente dichiarata dell'esito del rischio 8 già in wiki; nessuna informazione su permessi del file, copie fuori dallo store o messaggi di errore. #1 (chiusa 2026-04-10, maintainer: «fixed in v0.2.0»): la chiave Google passava nella query dell'URL ed è stata spostata; precedente per il caso SerpApi, che non chiude il gap. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §6. Altre dichiarazioni pertinenti (non chiudono)]
- **Confini dei comandi sui file:** #318, punto 4, **dichiara** comandi sui file con percorsi arbitrari e permessi Tauri ampi. **Osservato v0.6.13:** `assetProtocol.scope` è `["**"]` (`tauri.conf.json:28`); i permessi HTTP includono `http://**` e `https://**` (`capabilities/default.json:17-26`). Il punto 3 di #318 (scritture dell'ingest senza `isSafeIngestPath`) risulta corretto: `executeIngestWrites` scarta i percorsi non sicuri o gestiti dall'app (`ingest.ts:3719, 3849-3851`); riguarda le scritture dell'ingest e non dice nulla sui controlli di `delete_file`. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §6. Altre dichiarazioni pertinenti (non chiudono)]
- **Test fuori dai workflow:** i contributori **dichiarano** di eseguire in locale `npm run test:mocks`, `npm run typecheck`, `npm run build` (#170, #193, #228). **Osservato v0.6.13:** `test` = `test:mocks` + `test:llm`; `test:mocks` = vitest escludendo `*.real-llm.test.ts` e `mcp-server`; `test:llm` = vitest sui test `real-llm`, senza parallelismo fra file; `typecheck` = `tsc --build` (`package.json:8, 12-14`). Nessuna issue letta cita `cargo test`; gli script `.github/scripts/*` non sono letti. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §6. Altre dichiarazioni pertinenti (non chiudono)]
- **Più processi sullo stesso computer:** #648, commento di un utente (v0.6.8 circa), **dichiara** che non si possono aprire due istanze dell'app perché il Clip server va in conflitto. **Osservato v0.6.13:** nessuna occorrenza di `single_instance` o `single-instance` sotto `src-tauri` (`git grep`); il Clip server ritenta il bind fino a 3 volte e il riavvio fino a 10 (`clip_server.rs:18-19`). **Deduzione non testata:** la seconda istanza non è impedita dall'app; che cosa accada oltre al fallimento del bind del Clip server non è letto. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §6. Altre dichiarazioni pertinenti (non chiudono)]
- **Override LLM per progetto:** #562, **Dichiarato (maintainer)**, v0.6.4: l'override per progetto «è condiviso anche dal backend dell'API locale». Dichiarazione d'intento; non verifica l'equivalenza fra TS e Rust. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §6. Altre dichiarazioni pertinenti (non chiudono)]
- **Cronologia dei file:** #641 dice quali impostazioni esistono (attivazione, conservazione da 0 a 30 versioni) ma non come vengono scritte. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §6. Altre dichiarazioni pertinenti (non chiudono)]
- **Re-index con errori:** #515, **Dichiarato (maintainer)**, v0.6.2: con pagine fallite le riuscite si aggiornano e le fallite conservano i vettori precedenti; non dice nulla sullo stato dopo un errore successivo allo svuotamento. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §6. Altre dichiarazioni pertinenti (non chiudono)]
- **Monitoraggio delle cartelle per più progetti:** #648, **Dichiarato (maintainer)**, v0.6.9: il monitoraggio elabora tutti i progetti configurati; **Dichiarato (segnalatore)**, 2026-08-25: con due progetti configurati viene ancora elaborato solo quello aperto. Issue rimasta chiusa. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §6. Altre dichiarazioni pertinenti (non chiudono)]
- **Coda di ingest dopo il riavvio:** #758, **Dichiarato (maintainer)**, v0.6.12: i task `pending` e `processing` persistiti riprendono al riavvio; recupero degli eventi mancati del monitoraggio. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §6. Altre dichiarazioni pertinenti (non chiudono)]

### 7. Stato in v0.6.13 dei sei punti di #318

| Punto di #318 | Stato in v0.6.13 | Evidenza |
|---|---|---|
| 1. Clip server senza autenticazione, CORS `*`, `projectPath` dal client | **parziale**: CORS a elenco; token richiesto solo da rete locale; da loopback nessun token; `projectPath` non confrontato col registro | §1, §2 |
| 2. Corpo della richiesta senza limite | **presente** | §2 |
| 3. Scritture dell'ingest senza `isSafeIngestPath` | **corretto** | §6 |
| 4. Permessi Tauri ampi | **presente** | §6 |
| 5. Segreti in chiaro | **presente** (già in wiki, rischio 8) | §6 |
| 6. Dipendenze vulnerabili | **non verificato**: nessun audit eseguito | — |

[^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §7. Stato in v0.6.13 dei sei punti di #318]

## Gap toccati
Esito per ciascun gap preso in carico; la chiusura effettiva è decisione dell'utente e, dove indicato, è registrata in [[gaps]].

| Gap | Esito | Che cosa resta |
|---|---|---|
| `llm-wiki-clip-server-uso-bind-cors` | chiuso (evidenza osservata, §1) | residui nel gap `llm-wiki-clip-server-input-non-limitato` |
| `llm-wiki-coppie-id-pagina-non-confrontate` | chiuso con residui (§5) | gap `llm-wiki-coppie-id-casi-limite` |
| `llm-wiki-archivi-dimensioni` | aggiornamento parziale, resta aperto | misure del progetto sintetico (Q_004) |
| `llm-wiki-reindex-page-id-concorrenza-reale` | aggiornamento parziale, resta aperto | frequenza con la regola attuale, `embedPage` concorrente, stato dopo chiusura o errore |
| `llm-wiki-test-fuori-workflow` | aggiornamento parziale, resta aperto | `cargo test`, `.github/scripts/*`, documentazione di contribuzione |
| `llm-wiki-sessione-concorrenza-file`, `llm-wiki-registro-concorrenza-reale` | aggiornamento parziale, restano aperti | prova con due processi; semantica del plugin store |
| `llm-wiki-segreti-permessi-file`, `-copie-fuori-store`, `-serpapi-errori`, `llm-wiki-cancellazione-controlli-confine`, `llm-wiki-override-llm-resolveconfig`, `llm-wiki-scritture-non-verificate`, `llm-wiki-reindex-lancedb-errore-parziale` | nessun cambiamento | invariato |

Gap nuovi: `llm-wiki-clip-server-input-non-limitato`, `llm-wiki-monitoraggio-piu-progetti`, `llm-wiki-dipendenze-vulnerabili`, `llm-wiki-coppie-id-casi-limite`.

## Pagine collegate
[[llm-wiki-sicurezza]], [[llm-wiki-api-locale]], [[llm-wiki-archivi-persistenza]], [[llm-wiki-versioni-e-migrazioni]], [[llm-wiki-rischi-persistenza]], [[llm-wiki-test-e-ci]], [[llm-wiki-sincronizzazione-file]], [[llm-wiki-pipeline-ingest]], [[gaps]].

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

## Contradictions
- **Clip server «non letto» o «non verificato».** Prima ([[llm-wiki-sicurezza]], [[llm-wiki-api-locale]]): l'uso di bind, token e CORS nel Clip server non è verificato. Ora (§1, osservato v0.6.13): letto. Superamento, non assenza. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §1. Clip server: indirizzo di ascolto, CORS e token]
- **Nota sul raw, §6.** Il raw cita `isSafeIngestPath` (punto 3 di #318) sotto il gap sulla cancellazione, ma il controllo riguarda le scritture dell'ingest: non è evidenza sui confini di `delete_file`. [^src: raw/2026-11-21-issues-llm_wiki-chiuse.md §6. Altre dichiarazioni pertinenti (non chiudono)]

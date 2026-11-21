---
source_path: https://github.com/nashsu/llm_wiki/issues?q=is%3Aissue+is%3Aclosed
source_type: github-issues
git_branch: develop (coincide con main al commit indicato, `git -C code_repos/llm_wiki log -1`)
git_commit: e08cfce65aad8b76b13546a081c1a8d4422b70c3
extracted_at: 2026-11-21
extractor: sessione principale (gh CLI 2.101.0, lettura pubblica)
scope: issue chiuse del repository upstream confrontate con i gap aperti di wiki/gaps.md, con controllo puntuale sul codice v0.6.13
---

# Issue chiuse di nashsu/llm_wiki: dati e dichiarazioni per i gap aperti

> Estratto scritto dalla sessione principale il 2026-11-21. Fonte: le 362 issue chiuse del repository upstream
> `nashsu/llm_wiki` (corpo e commenti), scaricate con `gh issue list --repo nashsu/llm_wiki --state closed --limit 1000 --json number,title,body,closedAt,createdAt,labels,stateReason,comments`.
> Controllo sul codice: submodule `code_repos/llm_wiki` al commit `e08cfce` (v0.6.13), sola lettura.

## Identità e perimetro

- **Natura della fonte.** Un'issue è una **dichiarazione**, non un'osservazione del codice corrente. Ogni voce porta una di queste etichette:
  - «Dichiarato (segnalatore)»: chi ha aperto l'issue o un contributore, con la versione indicata nell'issue;
  - «Dichiarato (maintainer)»: commento del maintainer del repository upstream, con la versione in cui dice che la modifica è uscita;
  - «Osservato v0.6.13»: letto in questa sessione nel codice al commit `e08cfce`, con file e righe; mai eseguito.
- **«Chiusa come completata» non vuol dire «corretta».** Lo stato di chiusura di GitHub non è evidenza di una correzione: vedi §7 (la #318 è chiusa come completata senza commento e tre dei sei difetti segnalati sono ancora presenti in v0.6.13) e la #648 (§6).
- **Dati di terzi.** Le misure delle issue vengono da progetti di singoli utenti, su versioni vecchie. Non sono dati del cliente né di un progetto sintetico della factory. Nessun percorso utente, id di progetto, id di sessione o contenuto di pagina è riportato qui: solo conteggi, dimensioni, versioni e nomi di file del repository.
- **Licenza.** Repository di terzi, GNU GPL v3: solo nomi di file, simboli e righe; nessun frammento di codice.
- **Metodo.** Ricerca per parole chiave su titolo, corpo e commenti (script nel scratchpad della sessione, non versionato), poi lettura per intero delle issue pertinenti. I controlli «Osservato v0.6.13» usano `grep -n` e `sed -n` sui file citati; i comandi sono riportati in ciascuna sezione. Un «non trovato» vale per il file e le righe indicati.
- **Copertura.** 362 issue chiuse lette per titolo; circa 40 lette per intero. Gap aperti confrontati: 55 (tutti quelli senza «Risolto» in `wiki/gaps.md` al 2026-11-21 22:10).

## 1. Clip server: indirizzo di ascolto, CORS e token (gap `llm-wiki-clip-server-uso-bind-cors`)

- **Dichiarato (segnalatore), #474, v0.5.1:** API (porta 19828) e Clip server (porta 19827) ascoltavano solo su `127.0.0.1`, indirizzo scritto nel codice.
- **Dichiarato (maintainer), #474, chiusa 2026-06-30, v0.5.4:** entrambi i server supportano un indirizzo di ascolto configurabile: variabile `LLM_WIKI_BIND_HOST` e opzione nelle impostazioni «Allow API and Clip server access from the local network»; con l'opzione attiva, dopo il riavvio, entrambi ascoltano su `0.0.0.0`; il default resta `127.0.0.1`; la UI avverte di tenere attivo il token.
- **Dichiarato (maintainer), #510, chiusa 2026-08-25, v0.6.5:** l'estensione Chrome può collegarsi al Clip server tramite l'IP di rete locale del computer; consiglia di tenere attiva l'autenticazione a token.
- **Osservato v0.6.13:**
  - il Clip server ricava l'indirizzo con le stesse funzioni dell'API: `server_bind::configured_bind_host` e `server_bind::bind_addr` [^src: src-tauri/src/clip_server.rs:63-64] [^src: src-tauri/src/api_server.rs:135-136]; l'ordine è variabile d'ambiente, poi valore nello store, poi default [^src: src-tauri/src/server_bind.rs:10-14];
  - CORS: `Access-Control-Allow-Origin` è restituito solo per origini in elenco (`chrome-extension://`, `moz-extension://`, `http://localhost[:porta]`, `http://127.0.0.1[:porta]`, `http://[::1][:porta]`, `tauri://localhost`, `http://tauri.localhost`, `https://tauri.localhost`), con `Vary: Origin` e `Access-Control-Allow-Private-Network: true` [^src: src-tauri/src/cors.rs:11-23] [^src: src-tauri/src/cors.rs:25-41]; il Clip server usa questa funzione [^src: src-tauri/src/clip_server.rs:324-325];
  - token: una richiesta **non di loopback** senza token valido riceve 401 «Missing or invalid API token»; una richiesta **di loopback** passa senza token (commento: comportamento precedente alla rete locale, per l'app e le estensioni vecchie) [^src: src-tauri/src/clip_server.rs:118-134] [^src: src-tauri/src/clip_server.rs:328-336]; il token è lo stesso dell'API e si confronta in tempo costante da query `token`, header `X-LLM-Wiki-Token` o `Authorization: Bearer` [^src: src-tauri/src/clip_server.rs:349] [^src: src-tauri/src/api_server.rs:593-618]; senza token configurato `is_token_authorized` restituisce falso [^src: src-tauri/src/api_server.rs:598-600].
- Comandi: `grep -nE 'server_bind|cors|token|Authorization' src-tauri/src/clip_server.rs`; `sed -n '100,135p;340,352p' src-tauri/src/clip_server.rs`; `grep -n 'fn local_cors_headers' -A22 src-tauri/src/cors.rs`; `grep -n 'fn configured_bind_host' -A12 src-tauri/src/server_bind.rs`; `grep -n 'fn is_token_authorized' -A25 src-tauri/src/api_server.rs`.

## 2. Clip server: fatti nuovi per la sicurezza (nessun gap esistente)

- **Dichiarato (segnalatore), #318, 2026-06-01** (audit di sicurezza, sei punti; issue chiusa come completata il 2026-06-06 **senza alcun commento**): il Clip server accetta corpi di richiesta senza limite di dimensione; l'endpoint `/clip` accetta un `projectPath` dal corpo della richiesta e scrive Markdown in `<projectPath>/raw/sources/`; CORS `*`; nessuna autenticazione.
- **Osservato v0.6.13:**
  - **corpo senza limite:** `POST /project`, `POST /projects` e `POST /clip` leggono il corpo con `read_to_string` su `request.as_reader()`, senza limite di dimensione nelle righe lette [^src: src-tauri/src/clip_server.rs:163-165] [^src: src-tauri/src/clip_server.rs:216-218] [^src: src-tauri/src/clip_server.rs:266-268]; nessuna costante di limite del corpo nel file (le sole costanti `MAX_` sono i tentativi di bind e di riavvio [^src: src-tauri/src/clip_server.rs:18-19]);
  - **`projectPath` non confrontato con il registro:** il gestore della clip usa il `projectPath` del corpo se presente, altrimenti il progetto corrente; lo normalizza (barre) e lo rifiuta solo se vuoto; crea `<projectPath>/raw/sources` con `create_dir_all` e vi scrive `<slug>-<data>.md` [^src: src-tauri/src/clip_server.rs:411-428] [^src: src-tauri/src/clip_server.rs:456-492]; nelle righe 408-512 non c'è alcun confronto con il registro dei progetti né con i progetti recenti;
  - combinato con §1 (loopback senza token): **deduzione non testata** — un processo locale qualsiasi dell'utente può creare un file Markdown in `<percorso a scelta>/raw/sources/` dove l'utente ha permessi di scrittura, e accodarlo fra le clip in attesa [^src: src-tauri/src/clip_server.rs:504-508]. Non eseguito.
- Comandi: `grep -nE 'read_to_string|\(&Method::(Post|Get)' src-tauri/src/clip_server.rs`; `sed -n '408,512p' src-tauri/src/clip_server.rs`.

## 3. Dimensioni reali degli archivi (gap `llm-wiki-archivi-dimensioni`)

Tutti i dati sono «Dichiarato (segnalatore)», da un solo progetto ciascuno, sulla versione indicata.

| Issue | Versione | Progetto | Misura dichiarata | Esito dichiarato dal maintainer |
|---|---|---|---|---|
| #398 | v0.4.23, macOS | 6.445 pagine, 44.879 chunk | indice LanceDB 3,8 GB: `_versions/` 3,6 GB (13.125 manifest), `_transactions/` 51 MB, `data/` 216 MB (94,7% versioni vecchie); dopo pulizia e compattazione manuali 195 MB | v0.4.24: pulizia delle versioni e compattazione a fine ricostruzione/indicizzazione |
| #397 | v0.4.23, macOS | 6.566 pagine, circa 46.000 chunk | ricostruzione dell'indice oltre 2 ore, embedding locale a circa 0,16 s per richiesta, esecuzione seriale | v0.6.12: concorrenza configurabile, limite portato a 64 per embedding, elaborazione documenti, descrizione immagini e ingest |
| #641 | non indicata (agosto 2026) | non indicato | `.llm-wiki/history`: «migliaia» di file JSON | v0.6.9: cronologia disattivata per default, conservazione configurabile da 0 a 30 versioni, comandi di disattivazione e pulizia in Impostazioni → Manutenzione. Un contributore (non il maintainer) dichiara limiti di 2.048 file / 128 MB e potatura solo alla scrittura di una nuova voce, quindi i file vecchi restano se la funzione è spenta |
| #469 | non indicata | 16 libri PDF | 5.064 PNG di pagine intere, 2,2 GB | (richiesta di estrarre solo le immagini incorporate) |
| #714 | v0.6.11, macOS | 4.359 pagine, 16.417 archi distinti | `GET /graph` circa 24 s a ogni richiesta, poi blocco dell'endpoint dopo alcune richieste | v0.6.12: paginazione, totale, cache per progetto con ricostruzione all'invalidazione |

- Per US-018: i limiti di codice citati (cronologia 128 MiB e 2.048 file) coincidono con quelli dichiarati dal contributore in #641; il segnalatore di #641 dichiara «migliaia» di file, senza numero esatto: non si può dire se il limite di 2.048 sia stato raggiunto.

## 4. Nomi di pagina rifiutati dall'indice vettoriale (gap `llm-wiki-reindex-page-id-concorrenza-reale`)

- **Dichiarato (segnalatore), #394 e #396, v0.4.23:** 447 pagine su 6.566 (6,8%) rifiutate dalla validazione di `page_id`, che allora ammetteva solo lettere, cifre, `-`, `_`, `.`; rifiuto silenzioso.
- **Dichiarato (maintainer), #396, chiusa 2026-06-16, v0.4.24:** validazione allargata, rifiuta solo caratteri pericolosi per i percorsi e di controllo.
- **Dichiarato (segnalatore), #770, v0.6.11:** pagine con lo stesso nome di file in cartelle diverse (`sources/` ed `entities/`, anche solo per maiuscole) rifiutate dall'API di embedding con 409; nell'ingest, sovrascrittura silenziosa dei vettori.
- **Dichiarato (maintainer), #770, chiusa 2026-09-27, v0.6.12:** identità di pagina con la cartella, in API, ingest, ricerca, cancellazione, revisioni e sincronizzazione.
- **Osservato v0.6.13:** `validate_page_id_common` rifiuta solo: stringa vuota, oltre `MAX_PAGE_ID_CHARS` (256) caratteri [^src: src-tauri/src/commands/vectorstore.rs:67], caratteri di controllo, `\`, `'`, `"` e un insieme di caratteri invisibili o di formattazione (U+00AD, U+061C, U+200B-U+200F, U+2028-U+202E, U+2060-U+206F, U+FEFF, U+FFF9-U+FFFB, U+E0000-U+E007F) [^src: src-tauri/src/commands/vectorstore.rs:78-114]. Ideogrammi e punteggiatura CJK passano. **Deduzione non testata:** il dato del 6,8% vale per la regola di v0.4.23 e non stima la frequenza attuale, che riguarda solo nomi con apici, barre inverse o caratteri invisibili.
- Comando: `sed -n '78,114p' src-tauri/src/commands/vectorstore.rs`.

## 5. Id di pagina TS e Rust (gap `llm-wiki-coppie-id-pagina-non-confrontate`)

- **Dichiarato (maintainer), #770, v0.6.12:** vedi §4.
- **Osservato v0.6.13:**
  - `wikiPageIdFromPath` toglie il prefisso `<progetto>/wiki/` o `wiki/`; se il percorso non ha quei prefissi e contiene `/` restituisce stringa vuota; se è un nome senza `/` lo accetta; toglie le barre iniziali e `.md` finale senza distinzione di maiuscole [^src: src/lib/embedding.ts:450-462];
  - `vector_page_id` converte `\` in `/`, richiede il prefisso `wiki/` e il suffisso `.md` (senza distinzione di maiuscole), toglie barre iniziali e finali, rifiuta il risultato vuoto [^src: src-tauri/src/commands/page_embedding.rs:282-290].
  - Esito per il caso normale (`wiki/<cartella>/<nome>.md`): stesso id, percorso relativo a `wiki/` senza `.md`. Differenze nei casi limite (osservate per costruzione, non eseguite): il nome nudo senza `wiki/` è accettato da TS e rifiutato da Rust; un percorso senza `.md` dà un id in TS e nessun id in Rust; le barre finali sono tolte solo da Rust; `\` è convertita da Rust e, in TS, dipende da `normalizePath` (non letto qui).
- Comandi: `sed -n '448,464p' src/lib/embedding.ts`; `sed -n '280,292p' src-tauri/src/commands/page_embedding.rs`.

## 6. Altre dichiarazioni pertinenti (non chiudono)

- **Segreti in chiaro** (gap `llm-wiki-segreti-permessi-file`, `-copie-fuori-store`, `-serpapi-errori`): #318, punto 5, dichiara che chiavi API, token dell'API locale e credenziali dei provider stanno in chiaro in `app-state.json` e raccomanda il portachiavi del sistema operativo. È una conferma indipendente dell'esito del rischio 8 già in wiki; nessuna informazione su permessi del file, copie fuori dallo store o messaggi di errore. #1 (chiusa 2026-04-10, maintainer: «fixed in v0.2.0»): la chiave Google passava nella query dell'URL ed è stata spostata; precedente per il caso SerpApi, che non chiude il gap.
- **Confini dei comandi sui file** (gap `llm-wiki-cancellazione-controlli-confine`): #318, punto 4, dichiara che i comandi sui file accettano percorsi arbitrari e che i permessi Tauri sono ampi. **Osservato v0.6.13:** `assetProtocol.scope` è `["**"]` [^src: src-tauri/tauri.conf.json:28]; i permessi HTTP includono `http://**` e `https://**` [^src: src-tauri/capabilities/default.json:17-26]. Il punto 3 di #318 (scritture dell'ingest senza `isSafeIngestPath`) risulta invece corretto: `executeIngestWrites` scarta i percorsi non sicuri o gestiti dall'app [^src: src/lib/ingest.ts:3719] [^src: src/lib/ingest.ts:3849-3851]. Comandi: `grep -n '"scope"' -A3 src-tauri/tauri.conf.json`; `grep -nE '"url"' src-tauri/capabilities/default.json`; `grep -n 'isSafeIngestPath' src/lib/ingest.ts`.
- **Test fuori dai workflow** (gap `llm-wiki-test-fuori-workflow`): i contributori dichiarano di eseguire in locale `npm run test:mocks`, `npm run typecheck`, `npm run build` (#170, #193, #228). **Osservato v0.6.13:** `test` = `test:mocks` + `test:llm`; `test:mocks` = vitest escludendo `*.real-llm.test.ts` e `mcp-server`; `test:llm` = vitest sui test `real-llm`, senza parallelismo fra file; `typecheck` = `tsc --build` [^src: package.json:8] [^src: package.json:12-14]. Nessuna issue cita `cargo test`. Gli script `.github/scripts/*` non sono letti.
- **Più processi sullo stesso computer** (gap `llm-wiki-sessione-concorrenza-file`, `llm-wiki-registro-concorrenza-reale`): #648, commento di un utente (v0.6.8 circa): non si possono aprire due istanze dell'app perché il Clip server va in conflitto. **Osservato v0.6.13:** nessuna occorrenza di `single_instance` o `single-instance` sotto `src-tauri` (`git grep`); il Clip server ritenta il bind fino a 3 volte e il riavvio fino a 10 [^src: src-tauri/src/clip_server.rs:18-19]. **Deduzione non testata:** la seconda istanza non è impedita dall'app; cosa accada oltre al fallimento del bind del Clip server non è letto.
- **Override LLM per progetto** (gap `llm-wiki-override-llm-resolveconfig`): #562, maintainer, v0.6.4: l'override per progetto «è condiviso anche dal backend dell'API locale». Dichiarazione d'intento; non verifica l'equivalenza fra TS e Rust.
- **Cronologia dei file** (gap `llm-wiki-scritture-non-verificate`, parte `history-settings.json`): #641 dice quali impostazioni esistono (attivazione, conservazione da 0 a 30 versioni) ma non come vengono scritte.
- **Re-index con errori** (gap `llm-wiki-reindex-lancedb-errore-parziale`): #515, maintainer, v0.6.2: con pagine fallite, le riuscite si aggiornano e le fallite conservano i vettori precedenti. Coerente con l'esito del rischio 6 già in wiki (con pagine fallite il flusso non svuota); non dice nulla sullo stato dopo un errore successivo allo svuotamento.
- **Monitoraggio delle cartelle per più progetti** (nessun gap): #648, maintainer, v0.6.9: il monitoraggio elabora tutti i progetti configurati. Il segnalatore risponde il 2026-08-25 che con due progetti configurati viene ancora elaborato solo quello aperto. Issue rimasta chiusa.
- **Coda di ingest dopo il riavvio** (nessun gap aperto): #758, maintainer, v0.6.12: i task `pending` e `processing` persistiti riprendono al riavvio; recupero degli eventi mancati del monitoraggio.

## 7. Stato in v0.6.13 dei sei punti di #318

| Punto di #318 | Stato in v0.6.13 | Evidenza |
|---|---|---|
| 1. Clip server senza autenticazione, CORS `*`, `projectPath` dal client | **parziale**: CORS a elenco; token richiesto solo da rete locale; da loopback nessun token; `projectPath` non confrontato col registro | §1, §2 |
| 2. Corpo della richiesta senza limite | **presente** | §2 |
| 3. Scritture dell'ingest senza `isSafeIngestPath` | **corretto** | §6 |
| 4. Permessi Tauri ampi | **presente** | §6 |
| 5. Segreti in chiaro | **presente** (già in wiki, rischio 8) | §6 |
| 6. Dipendenze vulnerabili | non verificato | nessun audit eseguito |

## Gap senza contributo dalle issue

`llm-wiki-autore-nash-su-yong-su`, `llm-wiki-licenza-mcp-server`, `llm-wiki-embedding-lancedb-dimensioni`, `llm-wiki-import-id-duplicato` (#522 dice solo che esportazione e importazione del progetto esistono da v0.6.4), i gap `master-*` (non riguardano llm_wiki) e gli altri gap aperti non citati sopra.

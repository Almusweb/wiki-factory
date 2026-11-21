---
source_path: /home/user/wiki-factory/code_repos/llm_wiki
source_type: repo
git_branch: HEAD
git_commit: e08cfce65aad8b76b13546a081c1a8d4422b70c3
extracted_at: 2026-11-21
extractor: repo-sync@2.12.0
scope: persistenza, fetta D (percorso e file corrotto di app-state.json per sistema operativo; atomicità dei sette archivi senza riga di codice)
---

# Specifiche estratte: llm-wiki, persistenza fetta D

> Documento generato da `repo-sync` v2.12 il 2026-11-21. Sorgente: `/home/user/wiki-factory/code_repos/llm_wiki`
> @ commit `e08cfce` (ramo non rilevato, come nelle estrazioni del 2026-11-21 «HEAD»). Read-only verso la sorgente.

## Identità e perimetro

- Estrazione **mirata** (TSK-006 / US-014 AC5 e TSK-007 / US-015 AC1), non generale. Stesso commit delle fette A, B, C e del giro del 2026-11-21. Stack, struttura, API e dipendenze non sono ripetuti (vedi `raw/2026-11-20-repo-llm_wiki.md`).
- **Licenza**: il repository è di terzi, sotto GNU GPL v3. Il documento descrive il codice con parole proprie e cita solo nomi di file, simboli, campi e percorsi. Nessun frammento di codice.
- **Due tipi di fonte, da non confondere.**
  - **Repo del cliente** (`code_repos/llm_wiki`): citazioni nella forma `[^src: percorso:righe]`, percorsi relativi alla radice del repo.
  - **Sorgente di una dipendenza da crates.io** (stesse versioni del `Cargo.lock`, scaricata in sola lettura fuori dal repo): citata come «sorgente della dipendenza `<crate> <versione>` da crates.io», con percorso interno al crate. Non è codice del cliente. Letta come dato non fidato: nessuna istruzione trovata, nessuna eseguita.
- «Osservato» = letto nel codice; «deduzione non testata» = ricavato da fatti osservati, mai visto in esecuzione. Nessun test, nessuna esecuzione dell'app.
- Versioni dichiarate dalla richiesta e riscontrate nei nomi delle cartelle delle dipendenze: `tauri` 2.11.1, `tauri-plugin-store` 2.4.3, `dirs` 6.0.0. Il `Cargo.lock` del repo **non è stato riaperto** in questa estrazione (nessun indice di riga): la corrispondenza con il lock è quella dichiarata dal richiedente.
- Le righe indicate sono quelle delle finestre lette; nessuna ricerca testuale globale (l'agente non ha `Bash` né `Grep`): un «non visto» vale solo per le righe lette.

## Parte A. `app-state.json`: percorso per sistema operativo (US-014 AC5)

### Identificatore dell'app

- `identifier` è `com.llmwiki.app` [^src: src-tauri/tauri.conf.json:5].
- I tre file di configurazione per piattaforma (`tauri.linux.conf.json`, `tauri.macos.conf.json`, `tauri.windows.conf.json`) sono stati letti **per intero** e **non contengono la chiave `identifier`** (contengono solo risorse del bundle, i framework pdfium su macOS e le proprietà della finestra su Windows) [^src: src-tauri/tauri.linux.conf.json:1-10] [^src: src-tauri/tauri.macos.conf.json:1-12] [^src: src-tauri/tauri.windows.conf.json:1-19]. Osservato: nessuna sovrascrittura dell'identificatore nel repo. Non ho letto altri file di configurazione di Tauri (per esempio varianti JSON5 o TOML): glob sul solo schema `tauri.*.conf.json` ha dato questi tre.

### Catena di risoluzione del percorso

1. **Lato TS**: lo store si apre con il nome relativo `app-state.json`, salvataggio automatico `true` e valori di default vuoti [^src: src/lib/project-store.ts:8-13].
2. **Lato Rust**: il plugin store è registrato senza opzioni [^src: src-tauri/src/lib.rs:558]. Il comando `load` del plugin costruisce lo store e passa dal percorso risolto [sorgente della dipendenza `tauri-plugin-store` 2.4.3 da crates.io, `src/lib.rs:124-134`].
3. **Risoluzione**: il percorso relativo si risolve con la base «AppData» di Tauri [sorgente della dipendenza `tauri-plugin-store` 2.4.3, `src/store.rs:26-31`].
4. **`app_data_dir`** è la cartella dati dell'utente più l'identificatore dell'app [sorgente della dipendenza `tauri` 2.11.1, `src/path/desktop.rs:244-251`].
5. **Cartella dati dell'utente** (`data_dir`), per sistema operativo [sorgente della dipendenza `dirs` 6.0.0, `src/lib.rs:113-124` (tabella nei commenti), `src/lin.rs:11`, `src/mac.rs:7,12`, `src/win.rs:10`]:

| Sistema | `data_dir` (osservato) | Percorso di `app-state.json` |
|---|---|---|
| Linux | `$XDG_DATA_HOME` se è un percorso assoluto, altrimenti `$HOME/.local/share` | `<data_dir>/com.llmwiki.app/app-state.json`, per esempio `/home/<utente>/.local/share/com.llmwiki.app/app-state.json` |
| macOS | `$HOME/Library/Application Support` | `$HOME/Library/Application Support/com.llmwiki.app/app-state.json` |
| Windows | cartella nota «Roaming AppData» (`FOLDERID_RoamingAppData`), non «Local» | per esempio `C:\Users\<utente>\AppData\Roaming\com.llmwiki.app\app-state.json` (esempio dei commenti di `dirs`) |

- **Confermato dal codice letto**: la forma `<data_dir>/com.llmwiki.app/app-state.json`, con `data_dir` come nella tabella.
- **Non letto, quindi deduzione non testata**:
  - il passaggio da «base AppData» a `app_data_dir` avviene in `src/path/mod.rs` di `tauri`, **non scaricato né letto**. È una deduzione forte (il nome coincide, e il Rust del repo compone `app_data_dir()` con lo stesso nome file), non un fatto letto;
  - le funzioni `home_dir` e `known_folder_roaming_app_data` stanno nel crate `dirs-sys`, **non scaricato**: il valore di Windows poggia sulla tabella dei commenti e su `win.rs:10`, non sul corpo della funzione di sistema;
  - confezionamenti che alterano le variabili d'ambiente o la home (contenitori, sandbox, AppImage, Flatpak): non verificati;
  - il TS non è stato osservato passare il nome senza modifiche: il pacchetto `@tauri-apps/plugin-store` (lato JavaScript) non è stato letto.

### Lettori Rust del file (stessa cartella)

Quattro punti compongono `app_data_dir()` con `app-state.json`: `src-tauri/src/lib.rs:406` (stato per il runtime dell'agente), `lib.rs:581-582` (proxy, nell'hook di setup), `src-tauri/src/api_server.rs:740` (stato dell'API, con cache) e `src-tauri/src/server_bind.rs:23` (host di bind). Osservato: usano la stessa funzione del plugin per la cartella; quindi (deduzione non testata) puntano allo stesso file.

### File corrotto: che cosa si legge nel plugin

Cosa leggo [sorgente della dipendenza `tauri-plugin-store` 2.4.3, `src/store.rs`]:

- La costruzione dello store chiama il caricamento da disco e **ignora l'esito** (`let _ =`): un errore di lettura o di deserializzazione non interrompe la creazione e non arriva al chiamante (righe 218-224). Il comando `load` ritorna l'identificativo di risorsa e basta [`src/lib.rs:130-133`].
- Il caricamento legge i byte del file, li deserializza e **solo se riesce** aggiunge le chiavi alla cache (righe 304-311): nessuna unione parziale con un file danneggiato. Se la lettura fallisce (file mancante o non leggibile) il risultato è lo stesso.
- La deserializzazione predefinita è JSON verso una mappa chiave-valore [`src/lib.rs:333-337`]: file vuoto, JSON troncato o con radice che non è un oggetto sono errori di deserializzazione.
- La cache parte dai valori di default (righe 280-288). Dal TS i default sono vuoti, quindi la cache parte vuota.
- `set` e `delete` aggiornano la cache e attivano il salvataggio automatico (righe 455-477, 565-599). Con l'opzione `autoSave: true` del TS, l'opzione serde `Bool(true)` non entra in nessun ramo e resta il valore predefinito del builder: debounce di 100 ms (righe 66-70) [`src/lib.rs:85-95`].
- Il salvataggio crea la cartella padre e scrive **l'intera cache** con `fs::write` direttamente sul percorso finale (righe 291-299): nessun file temporaneo, nessuna rinomina, nessuna copia di riserva del file precedente visibile nel corpo letto. Un salvataggio esplicito annulla quello in coda (righe 544-550); allo `Drop` dello store un salvataggio in attesa viene eseguito (righe 601-614).

Che cosa **deduco** (deduzione non testata, mai eseguito):

1. All'avvio con `app-state.json` corrotto lo store risulta vuoto, senza errore né avviso visibile al TS. I getter TS di `project-store.ts` rispondono `[]` o `null` quando la chiave manca (righe 16-26); gli altri getter non sono stati riletti qui.
2. Il file corrotto **resta su disco finché non c'è una scrittura**; alla prima `set` (o `delete`, `clear`) il salvataggio automatico lo **riscrive con la sola cache corrente**: il contenuto corrotto e tutte le chiavi non ricaricate vanno perse, senza copia. Dopo quel momento il file torna valido.
3. La scrittura **non è atomica**: `fs::write` sul percorso finale (osservato). Che un'interruzione a metà scrittura lasci un file troncato è una deduzione dal comportamento di `std` (creazione con troncamento seguita da scrittura), non letto e non testato; sarebbe una via per arrivare al caso «file corrotto» di cui sopra.
4. Una scrittura del plugin e una lettura dei quattro lettori Rust possono sovrapporsi: un lettore potrebbe vedere un file troncato o vuoto e trattarlo come corrotto (nessun lock condiviso visibile nelle righe lette).

### File corrotto: i lettori Rust

| Punto | Comportamento su file mancante o JSON non valido (osservato) | Fonte |
|---|---|---|
| Stato per il runtime dell'agente | errore di lettura o di analisi → «nessun valore» → configurazione dell'agente di default; nessun log | src-tauri/src/lib.rs:405-414 |
| Proxy all'avvio | `read_proxy_config_from_store`: mancante, non analizzabile o senza `proxyConfig` → «nessuno»; il chiamante scrive in log «no proxyConfig in store, requests go direct» e non applica alcun proxy | src-tauri/src/proxy.rs:61-69; lib.rs:581-589 |
| Stato per l'API (cache) | analisi fallita → si tiene il **valore precedente in cache**, se c'è; altrimenti «nessun valore». Il risultato (anche vuoto) viene messo in cache; durata della cache dichiarata di 5 secondi dalle estrazioni precedenti, costante non riletta qui | src-tauri/src/api_server.rs:727-753 |
| Host di bind | errore di lettura o di analisi → «nessun valore» → si usa `DEFAULT_BIND_HOST` (valore non letto); la modalità di accesso da rete locale (valore pubblico) si attiva solo se la lettura riesce e la chiave lo consente | src-tauri/src/server_bind.rs:22-31 |

- I test di `proxy.rs` nelle righe 490-529 coprono file mancante e file senza sezione proxy; **non risulta un test su un file corrotto** in quelle righe (le righe 85-490 non sono state lette) [^src: src-tauri/src/proxy.rs:491-518].
- Deduzione non testata: con un file corrotto il proxy è «spento» (richieste dirette), l'agente parte con la configurazione di default e il bind torna al valore predefinito; solo l'API ha un ripiego sull'ultimo stato valido, e solo se la cache era già popolata. Effetti sul token dell'API: non letti in questa fetta.
- Il Rust **non scrive** `app-state.json` nei punti letti (solo lettura); la scrittura è del plugin lato TS.

### Esiti A, in breve

| Voce | Esito | Livello |
|---|---|---|
| Identificatore | `com.llmwiki.app`, nessuna sovrascrittura per piattaforma | osservato (tauri.conf.json:5; tre file di piattaforma letti interi) |
| Linux | `<XDG_DATA_HOME o $HOME/.local/share>/com.llmwiki.app/app-state.json` | osservato per `data_dir` (dirs lin.rs:11); collegamento a `app_data_dir` dedotto |
| macOS | `$HOME/Library/Application Support/com.llmwiki.app/app-state.json` | idem (dirs mac.rs:12) |
| Windows | `<Roaming AppData>\com.llmwiki.app\app-state.json` | osservato in tabella e in win.rs:10; corpo di `dirs-sys` non letto |
| File corrotto, plugin | errore ignorato, store vuoto con default `{}`; prima `set` riscrive il file con la sola cache | letto (store.rs) + deduzione non testata sulle conseguenze |
| Scrittura del plugin | diretta (`fs::write`), non atomica | osservato (store.rs:291-299) |
| File corrotto, lettori Rust | default silenzioso (agente, bind), proxy diretto con log, API con ripiego sul valore in cache | osservato |

## Parte B. Atomicità dei sette archivi senza riga di codice (US-015 AC1)

L'inventario a 17 righe è quello di `wiki/concepts/llm-wiki-archivi-persistenza.md` §«Esito della verifica di US-015»; qui si risolvono le righe 1, 2, 3, 13, 14, 15, 16. «Atomica» = file temporaneo e rinomina; «diretta» = scrittura sul percorso finale. Nessuna delle scritture seguenti risulta chiamare `sync_all` nelle righe lette: l'atomicità vale per i lettori concorrenti, non è dimostrata come durabile a un crash (deduzione non testata).

| # | Archivio | Scrittura (file:righe) | Meccanismo | Atomica |
|---|---|---|---|---|
| 1 | LanceDB v2 `wiki_chunks_v2` | src-tauri/src/commands/vectorstore.rs:472-547 (merge a 513-529; creazione tabella a 530-535) | un solo `merge_insert` per pagina, chiave `chunk_id`: aggiorna i corrispondenti, inserisce i nuovi, **cancella gli assenti della stessa pagina**; sotto un blocco di scrittura in processo per percorso di progetto (488-489). Alla prima scrittura la tabella si crea con `create_table` | **Sì per pagina, per dichiarazione del codice** (messaggio di errore «Atomic page upsert failed», 529; commento 455-459). La garanzia interna di `lancedb` **non è verificata** (sorgente non letto) |
| 2 | LanceDB v1 `wiki_vectors` | src-tauri/src/commands/vectorstore.rs:151-205 | `delete` con filtro sulla pagina (183), poi `add` (190); se la cancellazione fallisce si stampa solo un avviso e si prosegue (184-188). Nessun blocco di scrittura nelle righe lette | **No** fra i due passi (una interruzione fra delete e add lascia la pagina senza vettore; deduzione non testata) |
| 3 | `embedding-revisions/<sha256>.revision` | src-tauri/src/commands/page_embedding.rs:340-376 | file temporaneo con estensione `tmp-<uuid>` accanto al target (351), `fs::write` del temporaneo (352), `fs::rename` (354). Se la rinomina fallisce e il target esiste: lo cancella e riprova, ripristinando il vecchio contenuto se anche questo fallisce (357-369); se il target non esiste rimuove il temporaneo (371) | **Sì** (temporaneo e rinomina); finestra non atomica nel solo ramo di ripiego pensato per Windows (357-369, commento a 355-356) |
| 13 | `scheduled-import-db.json` | src/lib/scheduled-import.ts:410-422 (chiamata a 421) → src-tauri/src/commands/fs.rs:1295-1344 | `writeFileAtomic`, comando Rust `write_file_atomic`: file `.<nome>.<nanosecondi>.tmp` accanto al target, `fs::write`, `fs::rename`; rimuove il temporaneo se la rinomina fallisce (1310-1336) | **Sì** |
| 14 | `history-settings.json` | src-tauri/src/commands/file_history.rs:304-334 (scrittura a 324-326; percorso a 58-60) | `to_string_pretty` poi `fs::write` sul percorso finale, sotto blocco in processo (315); prima verifica che non sia un symlink (325) | **No** (diretta). Letture: qualsiasi errore → impostazioni di default (71-81) |
| 15 | `history/<hash>.json` | src-tauri/src/commands/file_history.rs:285-288 (`record_file_version`); anche 227-228 (potatura per file) e 423-424 (ripristino) | `fs::write` diretto del file della cronologia, sotto un `Mutex` statico solo in processo (riga 14) | **No** (diretta). Lettura corrotta: array vuoto (267-270); la scrittura successiva sostituisce il file con la sola voce nuova |
| 16 | Sessioni agente `agent-sessions/<id>.json` | src-tauri/src/agent/session.rs:166-175 (scrittura a 174), chiamata da `append_turn` a 72 | `create_dir_all` del padre, `to_string_pretty`, `fs::write` diretto; esito ignorato (`let _ =`, 72); mutex in processo sull'archivio (48) | **No** (diretta). Lettura corrotta: `load_session` dà «nessun valore» (160-164), si parte da una sessione vuota (54) e il salvataggio successivo sostituisce il file |

Note per riga:

- **Riga 1.** Dopo il `merge_insert` il codice salva la revisione dell'embedding (537-541): due passi separati (lance, poi file). Se il salvataggio della revisione fallisce, la revisione viene invalidata e si stampa un messaggio: la pagina sarà ri-incorporata (osservato). Una scrittura senza revisione invalida la revisione esistente (542-544).
- **Riga 2.** `vector_delete` (277-311) fa solo la cancellazione. Il comando v1 è presente nel codice letto; i suoi chiamanti applicativi non sono verificati qui.
- **Riga 3.** Il temporaneo sostituisce l'estensione `.revision` del percorso (351): il nome finale non cambia.
- **Riga 13.** `saveImportDb` costruisce un archivio con `version: 1` e **una sola directory** (l'attiva) (415-420): osservato che la scrittura non fonde le altre directory; se `loadDbStore` o i chiamanti le conservino altrove non è stato letto in questa fetta.
- **Riga 14.** In `set_file_history_settings` la scrittura precede la potatura delle voci (327-329): se la potatura fallisce il comando ritorna errore ma il file nuovo è già scritto (osservato).
- **Riga 15.** Altro scrittore diretto osservato di passaggio: `restore_file_history` scrive il **file dell'utente** con `fs::write` (427), non in modo atomico. Non è un archivio dell'inventario.
- **Riga 16.** Quando due ID di sessione differiscono solo per caratteri sostituiti da `_` il file è lo stesso (deduzione già nota, `session.rs:187-209`).

### Esiti B, in breve

Atomiche: 3 (temporaneo e rinomina), 13 (`writeFileAtomic`). Per dichiarazione del codice e non verificata a livello di `lancedb`: 1. Non atomiche (dirette o in due passi): 2, 14, 15, 16. Nessuna riga resta «non verificato» per mancanza di codice; resta non verificato l'interno di `lancedb` (riga 1).

## Gap evidenti

1. `tauri/src/path/mod.rs` (passaggio da «base AppData» a `app_data_dir`) e il crate `dirs-sys` (`home_dir`, cartella Roaming) non letti.
2. Pacchetto JavaScript `@tauri-apps/plugin-store`: non verificato che il nome `app-state.json` e le opzioni arrivino invariati al comando `load`.
3. Nessuna prova in esecuzione: file corrotto, primo salvataggio e sovrapposizione fra scrittura del plugin e letture Rust sono deduzioni non testate.
4. `DEFAULT_BIND_HOST` e la durata della cache dell'API (costante) non riletti; `proxy.rs` righe 85-490 non lette (altri test eventuali su file corrotto).
5. Effetti di un file corrotto su `apiConfig` (token) non letti; consegue dal lettore dell'API, non analizzato qui.
6. Contenitori e sandbox che spostano `XDG_DATA_HOME` o la home: non verificati.
7. Interno di `lancedb` (atomicità di `merge_insert`): sorgente non letto.
8. Chiamanti applicativi dei comandi v1 (`vector_upsert`, `vector_delete`) non verificati.
9. `Cargo.lock` non riaperto: le versioni sono quelle dichiarate dal richiedente e dai nomi delle cartelle scaricate.

## Note di estrazione

- **Stato**: **partial**. Commit `e08cfce` come da richiesta (confermato dall'hash completo delle voci esistenti; HEAD non riverificato da questo agente, privo di `Bash`). Ramo non rilevato.
- **Gate**: Fase 1 (validazione del repo e dedup contro il manifest: la voce `2026-11-21-repo-llm_wiki-persistenza-d` non esisteva) e Fase 4 (proposta) sono stati assolti dalla richiesta esplicita del chiamante, che indicava scope e un solo file da scrivere; nessuna conferma umana separata in chat.
- **File aperti del repo del cliente: 15**: `src-tauri/tauri.conf.json`, `tauri.linux.conf.json`, `tauri.macos.conf.json`, `tauri.windows.conf.json`; `src/lib/project-store.ts` (1-40); `src/lib/scheduled-import.ts` (380-440); `src-tauri/src/lib.rs` (400-420, 550-600); `src-tauri/src/api_server.rs` (725-765); `src-tauri/src/server_bind.rs` (10-45); `src-tauri/src/proxy.rs` (45-85, 490-529); `src-tauri/src/commands/file_history.rs` (1-550); `src-tauri/src/agent/session.rs` (1-217); `src-tauri/src/commands/page_embedding.rs` (1-460); `src-tauri/src/commands/vectorstore.rs` (1-730); `src-tauri/src/commands/fs.rs` (1295-1344).
- **Sorgenti di dipendenze lette (7, fuori dal repo)**: `tauri` 2.11.1 `src/path/desktop.rs` (1-120, 235-265); `dirs` 6.0.0 `src/lib.rs` (90-135), `src/lin.rs`, `src/mac.rs`, `src/win.rs` (prime righe); `tauri-plugin-store` 2.4.3 `src/store.rs` (1-615), `src/lib.rs` (1-445).
- **Segreti**: nessun valore di credenziale nelle finestre lette; non aperti file `.env*`. Letti solo nomi di chiavi e tipi. Secret redatti: 0 (lo zero vale per le finestre aperte, non è una scansione dell'intero repo).
- **Istruzioni trovate nei file letti**: nessuna rivolta a un agente. Solo commenti per i manutentori; non eseguiti.
- **Nessuna scrittura** sotto `code_repos/llm_wiki`; nessun comando di shell eseguito.

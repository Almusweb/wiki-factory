---
id: 2026-11-21-repo-llm_wiki-persistenza-d
type: source
title: Specifiche estratte da code_repos/llm_wiki, estrazione 2026-11-21 fetta D: percorso e file corrotto di app-state.json, atomicità dei sette archivi (repo-sync)
status: draft
created: 2026-11-21
updated: 2026-11-21
sources: ["raw/2026-11-21-repo-llm_wiki-persistenza-d.md"]
tags: [source, repo, llm-wiki, persistenza, app-state, atomicita, file-corrotti]
---

# Specifiche estratte da code_repos/llm_wiki, estrazione 2026-11-21 fetta D: percorso e file corrotto di app-state.json, atomicità dei sette archivi (repo-sync)
> Estrazione mirata `repo-sync` v2.12 del 2026-11-21 sul commit `e08cfce`, stato `partial`. Distingue «osservato» (letto nel codice) da «deduzione non testata» (mai eseguita). Due tipi di fonte: repo del cliente (citazioni `file:righe`) e sorgenti di dipendenze da crates.io (`tauri` 2.11.1, `tauri-plugin-store` 2.4.3, `dirs` 6.0.0), che **non sono codice del cliente**.

## Contesto
Quinta estrazione mirata sulla persistenza, dopo le fette A, B, C ([[2026-11-20-repo-llm_wiki-persistenza-a]], [[2026-11-20-repo-llm_wiki-persistenza-b]], [[2026-11-20-repo-llm_wiki-persistenza-c]]) e il giro del 2026-11-21 ([[2026-11-21-repo-llm_wiki-fs-lib-progetto]]). Serve TSK-006 (US-014 AC1 e AC5) e TSK-007 (US-015 AC1). Stesso commit `e08cfce`. Il repo è di terzi sotto GNU GPL v3: il raw cita solo nomi, simboli e percorsi. Il `Cargo.lock` non è stato riaperto: le versioni delle dipendenze sono quelle dichiarate dal richiedente e dai nomi delle cartelle. [^src: raw/2026-11-21-repo-llm_wiki-persistenza-d.md §Identità e perimetro]

## Dettaglio

### Percorso di `app-state.json` per sistema operativo
- Identificatore `com.llmwiki.app` in `src-tauri/tauri.conf.json:5`; i tre file di piattaforma (Linux, macOS, Windows) letti per intero non lo sovrascrivono. [^src: raw/2026-11-21-repo-llm_wiki-persistenza-d.md §Identificatore dell'app]
- Catena: nome relativo lato TS (`project-store.ts:8-13`), plugin store registrato senza opzioni (`lib.rs:558`), base «AppData» (dipendenza `tauri-plugin-store` 2.4.3), `app_data_dir` = cartella dati più identificatore (dipendenza `tauri` 2.11.1), `data_dir` per sistema (dipendenza `dirs` 6.0.0). [^src: raw/2026-11-21-repo-llm_wiki-persistenza-d.md §Catena di risoluzione del percorso]
- Linux `<XDG_DATA_HOME assoluto, altrimenti $HOME/.local/share>/com.llmwiki.app/app-state.json`; macOS `$HOME/Library/Application Support/com.llmwiki.app/app-state.json`; Windows `<Roaming AppData>\com.llmwiki.app\app-state.json`. [^src: raw/2026-11-21-repo-llm_wiki-persistenza-d.md §Catena di risoluzione del percorso]
- Deduzione non testata, perché non letti: il passaggio «base AppData» a `app_data_dir` (`src/path/mod.rs` di `tauri`), le funzioni di sistema in `dirs-sys`, i confezionamenti che alterano variabili d'ambiente o home (contenitori, sandbox, AppImage, Flatpak), il pacchetto JavaScript `@tauri-apps/plugin-store`. [^src: raw/2026-11-21-repo-llm_wiki-persistenza-d.md §Catena di risoluzione del percorso]
- Quattro lettori Rust compongono `app_data_dir()` con `app-state.json` (`lib.rs:406`, `lib.rs:581-582`, `api_server.rs:740`, `server_bind.rs:23`); puntano allo stesso file per deduzione non testata. [^src: raw/2026-11-21-repo-llm_wiki-persistenza-d.md §Lettori Rust del file (stessa cartella)]

### File corrotto
- Plugin store (osservato, dipendenza `tauri-plugin-store` 2.4.3): la costruzione dello store ignora l'esito del caricamento (`let _ =`); la deserializzazione riuscita è tutto-o-niente; il formato è JSON verso una mappa; la cache parte dai default (vuoti dal TS); il salvataggio scrive l'intera cache con `fs::write` sul percorso finale, senza temporaneo, rinomina o copia di riserva. [^src: raw/2026-11-21-repo-llm_wiki-persistenza-d.md §File corrotto: che cosa si legge nel plugin]
- Deduzioni non testate: all'avvio lo store risulta vuoto senza errore visibile; il file corrotto resta finché non c'è una scrittura, poi la prima `set`, `delete` o `clear` lo riscrive con la sola cache e le chiavi non ricaricate vanno perse; un'interruzione a metà scrittura può lasciare un file troncato; una scrittura del plugin e una lettura Rust possono sovrapporsi. [^src: raw/2026-11-21-repo-llm_wiki-persistenza-d.md §File corrotto: che cosa si legge nel plugin]
- Lettori Rust (osservato): agente su default silenzioso (`lib.rs:405-414`); proxy «nessuno» con log (`proxy.rs:61-69`, `lib.rs:581-589`); API con ripiego sul valore precedente in cache (`api_server.rs:727-753`); bind su `DEFAULT_BIND_HOST` (`server_bind.rs:22-31`). Non risulta un test su file corrotto in `proxy.rs:491-518`. Il Rust non scrive `app-state.json` nei punti letti. [^src: raw/2026-11-21-repo-llm_wiki-persistenza-d.md §File corrotto: i lettori Rust]

### Atomicità delle righe 1, 2, 3, 13, 14, 15, 16
- Riga 1 (LanceDB v2): `merge_insert` per pagina sotto blocco in processo (`vectorstore.rs:472-547`), atomica per dichiarazione del codice; l'interno di `lancedb` non è verificato.
- Riga 2 (LanceDB v1): delete poi add (`vectorstore.rs:151-205`), non atomica fra i due passi.
- Riga 3 (revisioni): temporaneo e rinomina (`page_embedding.rs:340-376`), atomica; ramo di ripiego non atomico per Windows.
- Riga 13 (`scheduled-import-db.json`): `writeFileAtomic` (`scheduled-import.ts:410-422` e `fs.rs:1295-1344`), atomica.
- Riga 14 (`history-settings.json`): `fs::write` diretto sotto blocco in processo (`file_history.rs:304-334`), non atomica.
- Riga 15 (`history/<hash>.json`): `fs::write` diretto sotto `Mutex` statico (`file_history.rs:285-288`), non atomica.
- Riga 16 (sessioni agente): `fs::write` diretto, esito ignorato (`session.rs:166-175`, chiamata a riga 72), non atomica.
- Nessuna di queste scritture chiama `sync_all` nelle righe lette: durabilità a un crash non dimostrata (deduzione non testata). [^src: raw/2026-11-21-repo-llm_wiki-persistenza-d.md §Parte B. Atomicità dei sette archivi senza riga di codice (US-015 AC1)]

### Limiti e gap
Nove gap evidenti nel raw: `tauri/src/path/mod.rs` e `dirs-sys` non letti; pacchetto JS del plugin non verificato; nessuna prova in esecuzione; `DEFAULT_BIND_HOST`, costante della cache e `proxy.rs` 85-490 non riletti; effetti di un file corrotto su `apiConfig` (token) non letti; contenitori e sandbox; interno di `lancedb`; chiamanti dei comandi v1; `Cargo.lock` non riaperto. [^src: raw/2026-11-21-repo-llm_wiki-persistenza-d.md §Gap evidenti]

## Pagine ricavate o aggiornate
Aggiornate: [[llm-wiki-archivi-persistenza]], [[llm-wiki-gestione-file-corrotti]], [[llm-wiki-rischi-persistenza]], [[llm-wiki-sicurezza]].

## Gap di questa fetta
- Chiuso con riserva: `llm-wiki-app-state-percorso`.
- Parziale: `llm-wiki-persistenza-codice-non-letto` (parte di US-015: `history-settings.json`, `file_history.rs` e `session.rs` letti nei punti di scrittura).
- Invariati: `llm-wiki-token-cifratura`, `llm-wiki-vector-v1-chiamanti` (chiuso in precedenza), `llm-wiki-archivi-sommario-conteggi`.

Dettagli in [[gaps]]. [^src: raw/2026-11-21-repo-llm_wiki-persistenza-d.md §Gap evidenti]

## Estratto non promosso a pagina
Nessun contenuto del raw è stato scartato; il testo del raw non è stato modificato. Nessuna istruzione rivolta a un agente trovata nel raw.

## Pagine collegate
[[2026-11-20-repo-llm_wiki]], [[2026-11-20-repo-llm_wiki-persistenza-a]], [[2026-11-20-repo-llm_wiki-persistenza-b]], [[2026-11-20-repo-llm_wiki-persistenza-c]], [[2026-11-21-repo-llm_wiki-fs-lib-progetto]], [[llm-wiki-archivi-persistenza]], [[llm-wiki-gestione-file-corrotti]], [[llm-wiki-rischi-persistenza]], [[llm-wiki-sicurezza]], [[gaps]]

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

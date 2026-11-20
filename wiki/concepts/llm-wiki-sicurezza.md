---
id: llm-wiki-sicurezza
type: concept
title: llm-wiki — superficie di sicurezza
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: ["raw/2026-11-20-repo-llm_wiki.md", "raw/2026-11-20-repo-llm_wiki-persistenza-a.md"]
tags: [llm-wiki, sicurezza, cors, bind]
---

# llm-wiki — superficie di sicurezza
> Il codice prevede l'ascolto fuori dal loopback e un elenco di origini CORS ammesse; il raw non ha letto dove `server_bind` e `cors` siano usati né quale autenticazione si applichi fuori dal loopback.

## Contesto
Il raw riporta la superficie di sicurezza come fatto, senza giudizio. Sono stati letti per intero `server_bind.rs`, `cors.rs`, `agent/permissions.rs` e `agent/router.rs`; i permessi e il router dell'agente sono in [[llm-wiki-agente]]. [^src: raw/2026-11-20-repo-llm_wiki.md §Superficie di sicurezza]

## Dettaglio

### Bind (`src-tauri/src/server_bind.rs`)
- L'host di default è `127.0.0.1`. [^src: raw/2026-11-20-repo-llm_wiki.md §Superficie di sicurezza]
- Si esce dal loopback in due casi: la variabile d'ambiente `LLM_WIKI_BIND_HOST` con un host valido, oppure il flag `apiConfig.allowLanAccess` vero in `app-state.json`; nel secondo caso l'host diventa `0.0.0.0`. Se entrambi sono presenti vince la variabile d'ambiente. [^src: raw/2026-11-20-repo-llm_wiki.md §Superficie di sicurezza]
- L'host viene sanitizzato: sono ammessi solo caratteri alfanumerici e i simboli `.`, `-`, `_`, `:`, `[`, `]`; valori vuoti o con altri caratteri sono scartati. Gli IPv6 senza parentesi sono racchiusi tra parentesi quadre. [^src: raw/2026-11-20-repo-llm_wiki.md §Superficie di sicurezza]
- I test del file coprono host LAN comuni, il rifiuto di input con percorso o separatori di comando e la lettura del flag. [^src: raw/2026-11-20-repo-llm_wiki.md §Superficie di sicurezza]

### CORS (`src-tauri/src/cors.rs`)
- Metodi dichiarati: GET, POST, PATCH, DELETE, OPTIONS. Gli header ammessi li passa il chiamante. [^src: raw/2026-11-20-repo-llm_wiki.md §Superficie di sicurezza]
- Origini ammesse: qualsiasi `chrome-extension://*` e `moz-extension://*` (qualunque identificativo di estensione), `http://localhost`, `http://127.0.0.1` e `http://[::1]` con o senza porta, `tauri://localhost`, `http://tauri.localhost` e `https://tauri.localhost`. Il confronto è esatto: i test escludono sottodomini ingannevoli, `https://localhost`, maiuscole e domini esterni. [^src: raw/2026-11-20-repo-llm_wiki.md §Superficie di sicurezza]
- Per un'origine ammessa il server riflette l'origine, aggiunge `Vary: Origin` e l'header di accesso alla rete privata; per le altre non emette l'header di origine ammessa. [^src: raw/2026-11-20-repo-llm_wiki.md §Superficie di sicurezza]
- Il file non mostra se una richiesta da origine non ammessa venga poi rifiutata: CORS non lo impone da solo ai client non browser. [^src: raw/2026-11-20-repo-llm_wiki.md §Superficie di sicurezza]

### Estensione Chrome (`extension/manifest.json`)
Permessi `activeTab`, `scripting`, `storage`; host `127.0.0.1:19827` e `localhost:19827`; host opzionali http e https ovunque; comando da tastiera per il clip della pagina. [^src: raw/2026-11-20-repo-llm_wiki.md §Superficie di sicurezza]

### Tauri
CSP con `connect-src` verso http e https; la capability `http:default` ammette host http e https arbitrari; schema di asset con ambito `**`. Il raw lo riporta come fatto, senza giudizio. [^src: raw/2026-11-20-repo-llm_wiki.md §Superficie di sicurezza]

### Divergenza dichiarata e punti non verificati
- La README descrive l'API come `127.0.0.1`-only e protetta da token, ma il codice prevede l'ascolto su LAN opzionale. Il raw non sa dove vengano usati `server_bind` e `cors` né quale autenticazione si applichi fuori dal loopback: documentazione e comportamento divergono, oppure ci sono vincoli aggiuntivi non letti. [^src: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti]
- Le credenziali hardcoded non sono state cercate nei sorgenti non aperti: i secret redatti sono 0 solo per i 30 file letti e per la ricerca dei nomi file. [^src: raw/2026-11-20-repo-llm_wiki.md §Note di estrazione]

## Pagine collegate
[[llm-wiki-api-locale]], [[llm-wiki-mcp-server]], [[llm-wiki-agente]]. Gap aperti: [[gaps]] (`llm-wiki-api-lan-auth`, `llm-wiki-approvazione-shell`, `llm-wiki-scan-credenziali`).

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->
- US-014 — Posizione e ciclo di vita dello store applicativo e dell'area dati di progetto (tipi delle configurazioni e campi sensibili)
- US-032 — Rischio 8: segreti in chiaro nello store applicativo

## Aggiornamenti (v2026-11-20)
Dalla seconda estrazione, mirata alla persistenza (21 file letti, commit `e08cfce`). Dettagli sugli archivi in [[llm-wiki-archivi-persistenza]].

- **Configurazione letta dal Rust.** I commenti di `project-store.ts` indicano che `proxyConfig` e `apiConfig` sono le chiavi di `app-state.json` che il codice Rust legge (`apiConfig` a ogni richiesta, con cache di 5 secondi), e che i nomi devono coincidere: se divergono, l'API resta senza token configurato. Il codice Rust che le legge (`api_server.rs`) non è letto. [^src: raw/2026-11-20-repo-llm_wiki.md §Schemi e campi]
- **Segreti in chiaro nello store.** Tra i campi in chiaro compaiono `token` e `localToken` in `mineruConfig`; per `apiConfig` i commenti parlano di un token API. Sono stati letti solo i nomi dei campi, nessun valore. I tipi di `llmConfig`, `embeddingConfig`, `searchApiConfig` e `providerConfigs` sono in `src/stores/wiki-store.ts`, non letto: la presenza di chiavi API non è verificata. [^src: raw/2026-11-20-repo-llm_wiki.md §Schemi e campi]
- **Validazione dell'id di pagina.** L'id di pagina nelle operazioni LanceDB è validato (massimo 256 caratteri, niente apici, backslash, caratteri di controllo o invisibili) perché viene inserito in un filtro testuale. Il caso di prova con un apice e una parola chiave SQL in `vectorstore.rs` è una fixture di test, non un'istruzione. [^src: raw/2026-11-20-repo-llm_wiki.md §Schemi e campi] [^src: raw/2026-11-20-repo-llm_wiki.md §Note di estrazione dell'update]
- **Cronologia e importazione.** La cronologia file e l'importazione di archivi rifiutano symlink; l'importazione rifiuta anche percorsi non sicuri, con massimo 100.000 voci e 4 GB. L'esportazione include `.llm-wiki/` (chat, sessioni, cronologia, LanceDB). Vedi [[llm-wiki-operazioni-distruttive]]. [^src: raw/2026-11-20-repo-llm_wiki.md §Operazioni distruttive e innesco]
- **Aggiornamento sul gap `llm-wiki-scan-credenziali`** (resta aperto). Nei 21 file di questo giro non risultano file `.env*` né valori di credenziale in chiaro, con 0 segreti redatti; le stringhe «secret» e «rotated» nei test Rust di `page_embedding.rs` sono segnaposto di test. Il campione cumulativo sale a 50 file, ma il limite è invariato: nessuna scansione testuale dei sorgenti non aperti, quindi lo zero non vale per l'intero repository. [^src: raw/2026-11-20-repo-llm_wiki.md §Note di estrazione dell'update]
- **Aggiornamento sul gap `llm-wiki-api-lan-auth`** (resta aperto). Il punto in cui `apiConfig` è letto è `api_server.rs`, non letto; non è noto quale autenticazione si applichi fuori dal loopback. [^src: raw/2026-11-20-repo-llm_wiki.md §Gap]

### Fette A, B e C
Dalla fetta A delle estrazioni mirate sulla persistenza ([[2026-11-20-repo-llm_wiki-persistenza-a]], 23 file, commit `e08cfce`). Il testo sopra non è modificato; dove è superato lo dice `## Contradictions` in coda. Sono letti solo nomi e tipi di campo, nessun valore di credenziale; qualificatori come nel raw. I tipi completi sono in [[llm-wiki-schema-dati]], i lettori backend in [[llm-wiki-api-locale]].

- **Segreti in chiaro nello stesso file.** Il commento di `proxy-config.ts` dichiara che gli URL con credenziali sono conservati insieme alle altre chiavi API, senza un archivio dei segreti separato. Campi sensibili, solo nomi: `apiKey` (`llmConfig`, `providerConfigs`, `searchApiConfig`, `embeddingConfig`, `multimodalConfig`), `customHeaders` ed `extraHeaders`, `token` e `localToken` di `mineruConfig`, `url` del proxy, `token` di `apiConfig`. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Configurazioni dello store: tipi e campi sensibili]
- Tutti i default dei campi sensibili nello stato iniziale dello store sono stringhe vuote. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Configurazioni dello store: tipi e campi sensibili]
- **Token API.** È generato lato TS con 32 byte casuali codificati in base64url. Nel Rust è accettato come parametro `token` nell'URL oltre che negli header `X-LLM-Wiki-Token` e `Authorization`; la variabile d'ambiente `LLM_WIKI_API_TOKEN` prevale sul valore dello store. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Lettori backend di `apiConfig` e `proxyConfig`]
- `/health` risponde senza autenticazione con flag di stato (`authRequired`, `authConfigured`, `tokenSource` in env, store o none, `enabled`, `mcpEnabled`, `allowUnauthenticated`, `allowLanAccess`), senza il valore del token. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Lettori backend di `apiConfig` e `proxyConfig`]
- Gli endpoint di chat, di scrittura pagina e di embed richiedono sempre il token, anche con `allowUnauthenticated` attivo (osservato in `api_server.rs`). [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Lettori backend di `apiConfig` e `proxyConfig`]
- `allowLanAccess` incide sull'host di ascolto tramite `server_bind::configured_bind_host` e si rilegge a ogni (ri)bind del ciclo del server, non a ogni richiesta; `apiConfig` invece è riletto a ogni richiesta con cache di 5 secondi. Il gap `llm-wiki-api-lan-auth` resta aperto: non è verificato quale protezione valga fuori dal loopback oltre al token, e `api_server.rs` è letto solo in parte (righe 1-1200 più finestre). [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Lettori backend di `apiConfig` e `proxyConfig`]
- L'URL del proxy è mascherato nei log (credenziali sostituite). [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Lettori backend di `apiConfig` e `proxyConfig`]
- `embedding_fetch` riceve la configurazione dal frontend a ogni chiamata e il TS passa l'intero oggetto, `apiKey` compresa, attraverso l'IPC. La UI embedding ignora gli header riservati (autorizzazione, tipo di contenuto, host, lunghezza, intestazione della chiave Google). Dove e come viaggia la chiave dell'embedding (`fetch_embedding_once`) non è letto. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Ricerca ed embedding]
- **Gap `llm-wiki-scan-credenziali`** (resta aperto). Nei 23 file di questa fetta nessun valore di credenziale e nessun file `.env*`; `secrets_redacted` 0 vale solo per i file e gli intervalli letti, perché non c'è stata una ricerca testuale. [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Note di estrazione]

## Contradictions
- **Lettura di `apiConfig` e chiavi API nei tipi.** Prima (sezione «Aggiornamenti», tre voci): «il codice Rust che le legge (`api_server.rs`) non è letto»; «i tipi di `llmConfig`, `embeddingConfig`, `searchApiConfig` e `providerConfigs` sono in `wiki-store.ts`, non letto: la presenza di chiavi API non è verificata»; «`api_server.rs`, non letto». Ora (fetta A): i lettori di `apiConfig` sono letti (`api_server.rs` righe 586-753, con `api_server.rs` letto alle righe 1-1200 più quattro finestre) e i tipi di `wiki-store.ts` confermano campi sensibili (`apiKey`, `token`, `customHeaders`, `extraHeaders`; solo nomi). «Non letto» va quindi inteso come «letto solo in parte», non «assente». [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §File letti e non letti] [^src: raw/2026-11-20-repo-llm_wiki-persistenza-a.md §Configurazioni dello store: tipi e campi sensibili]

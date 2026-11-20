---
id: llm-wiki-sicurezza
type: concept
title: llm-wiki — superficie di sicurezza
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: ["raw/2026-11-20-repo-llm_wiki.md"]
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

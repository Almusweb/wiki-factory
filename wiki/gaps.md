---
type: gap
status: draft
created: 2026-11-20
updated: 2026-11-20
append_only: true
---

# Gaps — informazioni assenti in wiki/

File append-only: le informazioni che servono e la wiki non ha. Formato e chiusura dei gap: skill `wiki-gap-protocol`.

## 2026-11-20 15:31 — llm-wiki-codice-non-letto
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** la logica di business non è stata letta: `src/lib/ingest.ts` oltre la riga 70, `src-tauri/src/agent/runtime.rs`, `src-tauri/src/agent/tools.rs`, `src-tauri/src/api_server.rs`, `src-tauri/src/commands/fs.rs` (tutti oltre 50 KB) e le righe 201-479 di `src-tauri/src/lib.rs`. Il fan-in dei moduli core è una stima debole su 30 file. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (nuova estrazione `repo-sync` che copra i file indicati). Non bloccante.
**Impatto:** le pagine [[llm-wiki-agente]], [[llm-wiki-struttura-e-moduli]] e [[llm-wiki-api-locale]] descrivono questi moduli solo per nome.

## 2026-11-20 15:31 — llm-wiki-contratto-api-http
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** il contratto esatto dell'API HTTP locale non è noto: la README è l'unica fonte degli endpoint, `api_server.rs` e `mcp-server/src/api-client.ts` non sono stati letti. Gli endpoint HTTP corrispondenti a scrittura pagina ed embedding non sono verificati, e l'elenco endpoint della README non cita una scrittura pagina. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `api_server.rs` e `api-client.ts`). Non bloccante.
**Impatto:** [[llm-wiki-api-locale]] riporta gli endpoint solo come dichiarati in README.

## 2026-11-20 15:31 — llm-wiki-api-lan-auth
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** non è noto dove vengano usati `server_bind` e `cors` né quale autenticazione si applichi quando il server ascolta fuori dal loopback. La README descrive l'API come `127.0.0.1`-only e protetta da token, il codice prevede l'ascolto su LAN opzionale: documentazione e comportamento divergono, oppure ci sono vincoli aggiuntivi non letti. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `api_server.rs` e dei punti d'uso di `server_bind` e `cors`). Non bloccante.
**Impatto:** [[llm-wiki-sicurezza]] e [[llm-wiki-api-locale]] non possono dire quale protezione valga fuori dal loopback.

## 2026-11-20 15:31 — llm-wiki-mcp-readme-vs-codice
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** il README di `mcp-server` elenca 10 strumenti e il codice ne registra 12 (`llm_wiki_embed_page` e `llm_wiki_write_page` non documentati); il suo paragrafo di sicurezza parla solo di letture e non cita la scrittura di pagine. Non è chiaro se sia il README a essere indietro o se esistano vincoli non letti. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (confronto con `api_server.rs`, non letto). Non bloccante.
**Impatto:** [[llm-wiki-mcp-server]] riporta entrambe le versioni senza scegliere.

## 2026-11-20 15:31 — llm-wiki-approvazione-shell
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** il punto in cui viene applicata l'approvazione dei comandi shell non è verificato. La README dice «external shell commands still require explicit approval»; `agent/permissions.rs` implementa solo il gate sulle capability, e la policy `api_default` include `Process`. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `agent/runtime.rs` e `agent/tools.rs`). Non bloccante.
**Impatto:** [[llm-wiki-agente]] e [[llm-wiki-sicurezza]] non possono confermare il controllo sui comandi shell.

## 2026-11-20 15:31 — llm-wiki-i18n-lingue
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** la README dice «English + Chinese» per l'i18n, ma in `src/i18n/` esistono `en.json`, `it.json`, `ru.json`, `zh.json`. Non è noto quali lingue siano effettivamente supportate dall'interfaccia. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `src/i18n/` e della selezione lingua). Non bloccante.
**Impatto:** [[llm-wiki-app]] riporta la divergenza senza risolverla.

## 2026-11-20 15:31 — llm-wiki-autore-nash-su-yong-su
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** la README cita nash_su come creatore e manutentore, l'intestazione di `LICENSE` riporta «Copyright (C) 2024-2026 Yong Su». La relazione tra i due nomi non è verificabile dal sampling. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw. Non bloccante.
**Impatto:** [[llm-wiki-app]] e [[llm-wiki-licenza-e-standard]] riportano i due nomi senza metterli in relazione.

## 2026-11-20 15:31 — llm-wiki-licenza-mcp-server
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** `mcp-server/package.json` dichiara `"license": "MIT"`, diversa dalla GPL v3 della radice. Il raw la segnala come anomalia da verificare. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw. Non bloccante.
**Impatto:** [[llm-wiki-licenza-e-standard]] e [[llm-wiki-mcp-server]] riportano entrambe le licenze senza dire quale prevalga.

## 2026-11-20 15:31 — llm-wiki-multimodale-stato
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** `plans/multimodal-images.md` ha stato «Spec, not started», mentre la README descrive come già presente l'ingest multimodale. Lo stato reale va verificato sul codice. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `src/lib/ingest.ts` e dei moduli `extract_images`). Non bloccante.
**Impatto:** [[llm-wiki-app]] e [[llm-wiki-schema-dati]] riportano lo schema multimodale come da verificare.

## 2026-11-20 15:31 — llm-wiki-ci-test-build
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** la CI (`ci.yml`) non esegue i test e il workflow `build.yml` non è stato letto. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura di `.github/workflows/build.yml`). Non bloccante.
**Impatto:** [[llm-wiki-test-e-ci]] non descrive il workflow di build.

## 2026-11-20 15:31 — llm-wiki-requisiti-funzionali
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** requisiti funzionali e regole di dominio sono derivabili solo dalla README e non sono confermati dal codice letto. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (lettura della logica di business, vedi `llm-wiki-codice-non-letto`). Non bloccante.
**Impatto:** [[llm-wiki-app]] elenca le funzioni solo come «dichiarate in README».

## 2026-11-20 15:31 — llm-wiki-scan-credenziali
**Origine:** wiki-keeper @ ingest 2026-11-20-repo-llm_wiki
**Gap:** nessuna scansione dei sorgenti non aperti alla ricerca di credenziali hardcoded: lo zero di secret redatti vale solo per i 30 file letti e per la ricerca dei nomi file. Fonte del gap: raw/2026-11-20-repo-llm_wiki.md §Gap evidenti.
**Sospetta fonte:** nessuna fonte chiara, serve nuovo raw (scansione testuale dei sorgenti). Non bloccante.
**Impatto:** [[llm-wiki-sicurezza]] e [[2026-11-20-repo-llm_wiki]] non possono affermare l'assenza di credenziali nel repository.

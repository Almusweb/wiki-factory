---
id: llm-wiki-licenza-e-standard
type: concept
title: llm-wiki — licenza e standard
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: ["raw/2026-11-20-repo-llm_wiki.md"]
tags: [llm-wiki, licenza, standard]
---

# llm-wiki — licenza e standard
> Il repository `llm_wiki` è di terzi, sotto GNU General Public License v3.0; il server MCP dichiara invece MIT nel proprio `package.json`.

## Contesto
Il raw descrive il codice con parole proprie e riporta solo nomi, simboli e firme. Lo dichiara in una nota di licenza: il repository scansionato è di terzi, sotto GNU General Public License v3.0. [^src: raw/2026-11-20-repo-llm_wiki.md §Specifiche estratte: llm-wiki]

## Dettaglio
- La README dice, verbatim: «This project is licensed under the **GNU General Public License v3.0**». Il file `LICENSE` (righe 1-12 lette) conferma «Version 3, 29 June 2007». [^src: raw/2026-11-20-repo-llm_wiki.md §Vincoli normativi / Standard]
- L'intestazione di `LICENSE` riporta «Copyright (C) 2024-2026 Yong Su», mentre la README cita nash_su come creatore e manutentore. La relazione tra i due nomi non è verificabile dal sampling. [^src: raw/2026-11-20-repo-llm_wiki.md §Identità]
- Anomalia da verificare: `mcp-server/package.json` dichiara la licenza MIT, diversa dalla GPL v3 della radice. [^src: raw/2026-11-20-repo-llm_wiki.md §Vincoli normativi / Standard]
- Protocolli citati senza essere vincoli normativi: Model Context Protocol, Chrome Manifest V3 (README) e client compatibili OpenAI per gli embedding. [^src: raw/2026-11-20-repo-llm_wiki.md §Vincoli normativi / Standard]
- Nei testi letti non c'è menzione di SPID, OIDC, OAuth2, SAML, eIDAS, FHIR, GDPR, HIPAA, PCI-DSS, HL7, ISO 27001 o RFC numerati. Il raw è `partial`: l'assenza vale solo per i testi letti. [^src: raw/2026-11-20-repo-llm_wiki.md §Vincoli normativi / Standard]

## Pagine collegate
Gap aperti su questi punti: [[gaps]] (`llm-wiki-licenza-mcp-server`, `llm-wiki-autore-nash-su-yong-su`).

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->

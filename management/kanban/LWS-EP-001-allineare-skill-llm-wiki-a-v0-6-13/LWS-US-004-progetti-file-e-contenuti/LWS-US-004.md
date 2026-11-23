---
id: LWS-US-004
title: Progetti, file e contenuti
role: Agente AI che usa la skill llm-wiki
priority: high
status: done
wiki_page: wiki/concepts/llm-wiki-api-locale.md
blocked_by: []
pending_clarification: []
depends_on: [LWS-US-002]
started_at: 2026-11-23
closed_at: 2026-11-23
---

# LWS-US-004 — Progetti, file e contenuti

## Descrizione
Come agente AI che usa la skill `llm-wiki`, voglio che la skill descriva correttamente `projects`, le forme di `{id}`, `files` e `files/content` della v0.6.13, affinché interpreti bene identificatori, elenchi e letture di file.

## Business Rules
- Regole trasversali dell'epica LWS-EP-001: valgono tutte.
- Copre D13, D17, D18; incoerenze n. 2, n. 5, n. 6, n. 11 (parte sull'id); V10, V11, V12, V25 (parte decisa dal codice).
- I fatti solo osservati si riportano in forma neutra: si corregge soltanto la frase smentita (N1).

### Evidenza dei fatti
| Fatto | Livello |
|---|---|
| D13: `Content-Type` è `application/json` senza `charset=utf-8` | [E] soltanto: correzione neutra |
| D17: chiave `currentProject` in `/projects` (non in `/health`) | [E+C] |
| D17: il nome del progetto come `{id}` dà 404 (la skill lo dice già); `resolve_project` accetta id o percorso | [E]; [C] solo su id o percorso |
| D18: estensioni leggibili md, mdx, txt, csv, json, yaml, yml, xml, html, htm, log; `rtf` fuori lista (415) | [C] |
| n. 2: 413 oltre `maxFiles`; `truncated` mai `true` osservato; presenza del campo come `false` non chiara | [E+C] parziale |
| n. 5: alias `raw` e `raw/sources` di `root` | [C+E] |
| V10: su Windows il match del percorso del progetto non distingue le maiuscole e accetta `\` | [C] |
| V11: si divide su `/` prima di decodificare; i due punti non sono separatori; `?` spezza l'URL, `+` diventa spazio, `%XX` decodificato ovunque | [C] parziale |
| V25: `current` è il progetto con `current` vero, impostato dalla UI; «esterni» e «negli script l'UUID» non decisi | [C] parziale |
| `files/content` permissivo (accetta `/` iniziale, backslash, maiuscole) | [E] soltanto: non si porta |

[^src: wiki/syntheses/llm-wiki-skill-vs-app-v0-6-13.md §Aggiornamenti (v2026-11-22, verifica sul codice)]
[^src: wiki/concepts/llm-wiki-api-osservazioni-esecuzione-v0-6-13.md §Osservazioni del 2026-11-13 (app 0.6.13, progetto reale, non replicate)]
[^src: wiki/syntheses/llm-wiki-api-affermazioni-codice-da-verificare.md §Esito per voce]

## UI Reference
[^src: wiki/concepts/llm-wiki-skill-api-v1-dichiarata.md §Base e endpoint]
[^src: wiki/concepts/llm-wiki-skill-api-v1-dichiarata.md §`GET /projects/{id}/files`]
[^src: wiki/concepts/llm-wiki-skill-api-v1-dichiarata.md §`GET /projects/{id}/files/content`]

## Acceptance Criteria
- [x] `projects` documenta la chiave `currentProject` oltre a `projects[]`, e l'esempio della risposta è coerente; la skill non la attribuisce a `/health`. (LWS-TSK-005 §Chiusura, AC1)
- [x] La forma «percorso» di `{id}` non è più dichiarata «esatta» né accompagnata da prescrizioni su maiuscole e slash: il codice accetta maiuscole diverse e `\` su Windows. Resta l'avvertenza che una `/` nell'id va codificata `%2F`; non si prescrive di codificare i due punti. (LWS-TSK-005 §Chiusura, AC2)
- [x] `files/content` elenca come leggibili md, mdx, txt, csv, json, yaml, yml, xml, html, htm, log e dice che `rtf` non è leggibile (415); l'elenco è identico in tutti i file che lo citano (n. 6). (LWS-TSK-005 §Chiusura, AC3)
- [x] `files` dice 413 oltre `maxFiles` e non descrive il campo `truncated` (n. 2); gli alias `raw` e `raw/sources` di `root` compaiono in tutti i file che descrivono `files` (n. 5). (LWS-TSK-005 §Chiusura, AC4)
- [x] Il `Content-Type` non è più dichiarato con `charset=utf-8`; se non si riporta il dato osservato, la dicitura è neutra («`application/json`») (D13). (LWS-TSK-005 §Chiusura, AC5)
- [x] La skill non afferma che negli script serva l'UUID né che `/projects` elenchi progetti esterni; non porta la permissività osservata di `files/content`. (LWS-TSK-005 §Chiusura, AC6)
- [x] Ogni affermazione cambiata ha nel TSK la riga di evidenza corrispondente; nessuna è priva di evidenza. (LWS-TSK-005 §Chiusura, AC7)

## Nota di modifica
- 2026-11-23 — Chiusura (rollup; fonte: tabella §Chiusura di LWS-TSK-005, unico TSK della storia, `done`). Prima: `status: ready`, AC non spuntati. Ora: `status: done`, AC1..AC7 spuntati con riferimento a LWS-TSK-005 §Chiusura; commit nel repo della skill `69dece1` sul branch `docs/align-v0-6-13`; `started_at` e `closed_at` 2026-11-23 (date del lavoro, da LWS-TSK-005).

## Fonti
[^src: wiki/syntheses/llm-wiki-skill-vs-app-v0-6-13.md §Dettaglio]
[^src: wiki/entities/llm-wiki-skill.md §Incoerenze interne della skill (materiale per la PR)]

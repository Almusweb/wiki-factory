---
description: Estrae testo + immagini dai PDF in raw/.
---

Due passi, perche' l'agente `sync-docs` non ha Bash (EP-098 TSK-974):

1. **Figure (sessione principale, deterministico).** Per ogni `raw/*.pdf` non ancora nel manifest:
   `python3 tools/sync/pdf_figures.py raw/<data>-<nome>.pdf --out raw/images --prefix <data>-<nome>`.
   Lo script scrive i binari (`-fig-NN.png|jpg|jp2`) e stampa un JSON: `figure` (con pagina, se
   ricavabile) e `saltate` (formato non gestito o oltre il limite di decompressione, con il motivo).
   Exit 2 = PDF illeggibile: lo si riporta, non si passa all'agente.
2. **Testo e descrizioni (agente).** Invoca `sync-docs` via `Agent` passandogli il JSON di ogni PDF e
   `ora_utc: <date -u +%Y-%m-%dT%H:%M:%SZ>`. L'agente:

1. Scansiona `raw/*.pdf` per file non ancora nel manifest.
2. Estrae testo → `raw/<data>-<nome>.txt`.
3. Descrive le figure → `raw/images/<data>-<nome>-fig-NN.md`, che citano il binario dello script.
4. Aggiorna `raw/.extraction-manifest.json`.
5. Suggerisce di invocare `wiki-keeper` per l'ingest.

Prerequisito per `wiki-keeper`: `wiki-keeper` legge i `.txt` estratti, mai i PDF direttamente.

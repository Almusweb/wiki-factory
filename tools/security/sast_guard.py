#!/usr/bin/env python3
"""Oracolo SAST con semgrep e ruleset fissato letto dal merge-base (EP-109 US-427, TSK-1041).

Motore, contratto ed esiti in oracolo_statico.py. Specifico di semgrep:
- ruleset: file `security_scan.semgrep_ruleset` della factory (YAML di regole semgrep), letto al
  merge-base della factory con il ref protetto e passato con `--config`; nessun registry remoto;
- `--disable-nosem`: un `# nosemgrep` aggiunto non nasconde il finding (e il diff-check lo segnala);
- `.semgrepignore` e `.gitignore` (che il `.semgrepignore` di default include) dell'albero sostituiti con
  quelli del merge-base del code_path;
- `--metrics off --disable-version-check`: nessuna chiamata di rete dello scanner;
- identita' del finding: (semgrep, check_id, path) senza riga.

Cosa NON garantisce: oltre a quanto dichiarato nel motore, gli errori di parsing di semgrep su singoli
file non cambiano l'esito (quei file non sono analizzati) e semgrep e' identificato solo in parte
(scanner_identity: script, interprete, RECORD).

CLI: sast_guard.py CODE_PATH [--root FACTORY] [--json]   exit 0 PASS, 1 FAIL, 2 rifiutato, 3 NON_VERIFICABILE
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oracolo_statico as os_  # noqa: E402


def comando(exe, albero, ruleset, uscita):
    # --no-git-ignore: semgrep non consulta .gitignore ne' .git/info/exclude (l'albero non e' un repo, ma
# la difesa non dipende da questo: CQRL iter-3). --max-target-bytes=0: nessun limite di dimensione; col default (1 MB) un file nuovo grande e'
    # saltato senza errori e senza traccia (CQRL iter-2, provato con semgrep 1.186.0)
    return [exe, "scan", "--config", ruleset, "--json", "--output", uscita, "--disable-nosem",
            "--metrics", "off", "--disable-version-check", "--quiet", "--max-target-bytes=0",
            "--no-git-ignore", "."]


def _senza_prefisso(check_id, ruleset):
    """semgrep premette al check_id la cartella del file di regole in forma puntata (provato con semgrep
    1.186.0). Il ruleset sta in una cartella temporanea diversa a ogni esecuzione: senza togliere il
    prefisso l'identita' del finding cambierebbe fra due esecuzioni."""
    cartella = os.path.dirname(os.path.abspath(ruleset)).strip(os.sep)
    for prefisso in (cartella.replace(os.sep, ".") + ".",
                     os.path.dirname(os.path.realpath(ruleset)).strip(os.sep).replace(os.sep, ".") + "."):
        if check_id.startswith(prefisso):
            return check_id[len(prefisso):]
    return check_id


def analizza(dati, albero, ruleset):
    out = []
    for r in dati["results"]:
        path = r["path"]
        if path.startswith("./"):
            path = path[2:]
        out.append({"rule_id": _senza_prefisso(r["check_id"], ruleset), "path": path, "symbol": ""})
    # file non analizzati del tutto: errori con un path (timeout, parsing); un errore di livello `error`
    # senza path (es. regola invalida) vale per tutti
    non_analizzati = set()
    for e in dati.get("errors") or []:
        p = e.get("path")
        if isinstance(p, str):
            non_analizzati.add(p[2:] if p.startswith("./") else p)
        elif e.get("level") == "error":
            non_analizzati.add("*")
    out.append(non_analizzati)
    return out


SEMGREP = os_.Scanner("semgrep", "semgrep_ruleset", (".semgrepignore", ".gitignore"), ("nosemgrep", "nosem", ".semgrepignore"),
                      comando, analizza)

if __name__ == "__main__":
    sys.exit(os_.main(SEMGREP))

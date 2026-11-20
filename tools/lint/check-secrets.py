#!/usr/bin/env python3
"""Check 4bj — segreti nei file tracciati, delegato all'oracolo gitleaks.

Passa all'oracolo (`tools/security/secrets_guard.py`) i file elencati da `git ls-files` nel root
indicato. Non definisce pattern ne' logica di rilevamento: importa `scan` e `severita`.

Mappatura:
    PASS              -> OK
    FAIL              -> un finding per segreto, severita' da `severita(root)`
                         (WARNING di default, ERROR da `secrets_guard.required_from` passata)
    NON_VERIFICABILE  -> WARNING che lo dichiara (gitleaks assente o in errore): mai un OK silenzioso;
                         resta WARNING anche con `required_from` passata, perche' manca la verifica,
                         non c'e' un segreto.

Il check gira a prescindere da `secrets_guard.enabled`: quel flag governa solo l'hook di pre-commit.
Il lint rileva sempre, l'hook previene.

Zero file tracciati, root non git o nessun file leggibile: NON_VERIFICABILE (mai OK).
Il messaggio OK dichiara quanti file gitleaks ha esaminato.

Previene nel percorso cooperativo, rileva negli altri: questo e' il percorso che rileva.

Non garantisce: i falsi negativi di gitleaks; senza il binario nessuna verifica; non copre la storia
git ne' i file gitignorati (solo i file tracciati); in CI rileva dopo il push, non prima.

Uso:
    python3 tools/lint/check-secrets.py [--root <repo>] [--json] [--strict]
Exit code: 0 anche con finding e WARNING; con --strict 1 se c'e' almeno un ERROR.
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import subprocess
import sys

QUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(QUI.parent / "security"))
import secrets_guard as sg  # noqa: E402

DICHIARAZIONE = "previene nel percorso cooperativo, rileva negli altri"


def tracciati(root):
    """File tracciati dal repo in `root`; lista vuota se non e' un repo git."""
    try:
        r = subprocess.run(["git", "-C", str(root), "ls-files", "-z"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError:
        return []
    if r.returncode != 0:
        return []
    return [p for p in r.stdout.decode("utf-8", "replace").split("\0") if p]


def check(root, oggi=None):
    """(esito dell'oracolo, severita' dei finding, file tracciati). Zero file o root non git:
    l'oracolo risponde NON_VERIFICABILE, mai OK."""
    files = tracciati(root)
    return sg.scan(files, str(root)), sg.severita(str(root), oggi), files


def righe(esito, sev):
    """Righe di output nel formato del lint."""
    if esito.stato == sg.PASS:
        return ["[4bj] OK — %s" % esito.messaggio.replace("PASS: ", "", 1)]
    if esito.stato == sg.NON_VERIFICABILE:
        return ["- [WARNING][secrets][4bj] verifica non eseguita: %s" % esito.messaggio]
    sev = "ERROR" if sev == "ERROR" else "WARNING"
    out = ["## %s (segreti nei file tracciati)" % sev]
    for f in esito.findings:
        if isinstance(f, dict):
            out.append("- [%s][secrets][4bj] %s:%s regola %s"
                       % (sev, f.get("File", "?"), f.get("StartLine", "?"), f.get("RuleID", "?")))
        else:
            out.append("- [%s][secrets][4bj] finding non strutturato" % sev)
    out.append("\nTotale: %d segreti (%s)" % (len(esito.findings), DICHIARAZIONE))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Check 4bj — segreti nei file tracciati (oracolo gitleaks)")
    ap.add_argument("root", nargs="?", default=None, help="root del repo (alternativa a --root)")
    ap.add_argument("--root", dest="root_opt", default=None)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--oggi", default=None, help="data di riferimento AAAA-MM-GG per required_from")
    ap.add_argument("--strict", action="store_true", help="exit 1 se c'e' un ERROR")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.root_opt or args.root or ".").resolve()
    oggi = datetime.date.fromisoformat(args.oggi) if args.oggi else None
    esito, sev, files = check(root, oggi)
    if args.json:
        print(json.dumps({"check": "4bj", "stato": esito.stato, "severita": sev,
                          "messaggio": esito.messaggio, "file_controllati": len(files),
                          "findings": esito.findings}, indent=2, ensure_ascii=False))
    else:
        print("\n".join(righe(esito, sev)))
    return 1 if args.strict and esito.stato == sg.FAIL and sev == "ERROR" else 0


if __name__ == "__main__":
    sys.exit(main())

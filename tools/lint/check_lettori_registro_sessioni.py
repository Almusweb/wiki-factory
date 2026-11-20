#!/usr/bin/env python3
"""Check 4bo — lettori diretti di `memory/active-sessions.yaml` (WARNING, detective).

Dal 2.48 il registro delle sessioni sta sulla git common dir; l'unico modo giusto di trovarlo e'
`registry_path()` in `tools/session/active_sessions.py`. Codice che apre il path vecchio, di solito
dopo un controllo di esistenza del file, conta zero sessioni senza dare errore.

Segnala i file Python tracciati che contengono, come costante stringa del codice, un path che
finisce con `memory/active-sessions.yaml` (nessuno spazio: un testo che lo cita in una frase,
come un messaggio o un help, non e' un path). Non guarda docstring e commenti (l'analisi e' sull'AST),
`tools/session/active_sessions.py` (definisce il path), i test (`test_*.py`, `*_test.py`, cartelle
`tests`/`test`) e le cartelle `.claude/worktrees`.

Non garantisce: un path costruito a pezzi (`"memory" / "active-sessions.yaml"`) non e' visto; i
file che non si leggono o non si analizzano sono riportati come INFO, mai come puliti.

Uso:
    python3 tools/lint/check_lettori_registro_sessioni.py [--root <factory>] [--json]
Exit code: 0 anche con finding (sempre WARNING).
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys

PATH_RE = re.compile(r"^\S*memory/active-sessions\.yaml$")
ESCLUSO = "tools/session/active_sessions.py"


def file_python(root):
    r = subprocess.run(["git", "ls-files", "-z", "*.py"], cwd=root, capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    if r.returncode == 0:
        return sorted(p for p in r.stdout.split("\0") if p)
    out = []
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in (".git", "node_modules")]
        out += [os.path.relpath(os.path.join(d, f), root).replace(os.sep, "/")
                for f in files if f.endswith(".py")]
    return sorted(out)


def escluso(rel):
    parti = rel.split("/")
    nome = parti[-1]
    return (rel == ESCLUSO or rel.startswith(".claude/worktrees/")
            or nome.startswith("test_") or nome.endswith("_test.py")
            or "tests" in parti[:-1] or "test" in parti[:-1])


def _docstring_ids(albero):
    ids = set()
    for n in ast.walk(albero):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            c = n.body[0] if n.body else None
            if isinstance(c, ast.Expr) and isinstance(c.value, ast.Constant) and isinstance(c.value.value, str):
                ids.add(id(c.value))
    return ids


def righe_con_path(sorgente):
    """Numeri di riga delle costanti stringa del codice (non docstring) che sono il path vecchio."""
    albero = ast.parse(sorgente)
    doc = _docstring_ids(albero)
    return sorted(n.lineno for n in ast.walk(albero)
                  if isinstance(n, ast.Constant) and isinstance(n.value, str)
                  and id(n) not in doc and PATH_RE.match(n.value))


def check(root):
    finding = []
    for rel in file_python(root):
        if escluso(rel):
            continue
        try:
            with open(os.path.join(root, rel), encoding="utf-8") as f:
                sorgente = f.read()
            if "active-sessions.yaml" not in sorgente:
                continue
            righe = righe_con_path(sorgente)
        except (OSError, SyntaxError, ValueError) as e:
            finding.append({"severita": "INFO", "file": rel, "riga": 0,
                            "messaggio": "non verificabile (%s)" % type(e).__name__})
            continue
        for n in righe:
            finding.append({"severita": "WARNING", "file": rel, "riga": n,
                            "messaggio": "apre `memory/active-sessions.yaml` direttamente: dal 2.48 il "
                                         "registro sta sulla git common dir, usa registry_path() di "
                                         "tools/session/active_sessions.py (altrimenti conta zero sessioni "
                                         "senza errore)"})
    return finding


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--oggi", help="ignorato (uniformita' con gli altri check)")
    a = ap.parse_args(argv)
    f = check(a.root)
    if a.json:
        print(json.dumps(f, indent=2, ensure_ascii=False))
    else:
        for x in f:
            print("[%s] lettori-registro-sessioni: %s:%d %s" % (x["severita"], x["file"], x["riga"], x["messaggio"]))
        if not f:
            print("OK lettori-registro-sessioni: nessun lettore diretto di memory/active-sessions.yaml")
    return 0


if __name__ == "__main__":
    sys.exit(main())

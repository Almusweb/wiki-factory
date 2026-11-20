#!/usr/bin/env python3
"""Check 4bn — marcatori di conflitto nei file in coda su HEAD (WARNING, detective, mai bloccante).

Esegue `tools/wiki/conflict_markers_check.py --rev HEAD`: righe `<<<<<<< `, `=======` o
`>>>>>>> ` in wiki/log*.md, wiki/gaps.md, wiki/index.md, raw/.extraction-manifest.json,
management/kanban/sprint.md e manifest che non e' JSON valido.
Il blocco preventivo sta nel pre-commit (tools/vcs/install_factory_hooks.py) e nel pre-push
(tools/vcs/install_factory_hooks.py); questo check trova cio' che e' entrato prima dei gate o da
un clone senza hook.

Uso:
    python3 tools/lint/check_marcatori_conflitto.py [--json] [--rev REF] [--strict] [<root>]
Exit code: 0 anche con finding; 1 con --strict e almeno un finding; 2 se il controllo non e'
stato eseguito (git in errore, ref sconosciuto), in ogni caso.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import sys

CHECKER = pathlib.Path(__file__).resolve().parents[1] / "wiki" / "conflict_markers_check.py"


def carica(root: pathlib.Path):
    spec = importlib.util.spec_from_file_location("conflict_markers_check", CHECKER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.ROOT = root
    return m


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Check 4bn — marcatori di conflitto nei file in coda")
    ap.add_argument("root", nargs="?", default=".", help="root della factory (default: .)")
    ap.add_argument("--rev", default="HEAD", help="ref da esaminare (default HEAD)")
    ap.add_argument("--json", action="store_true", help="output machine-readable")
    ap.add_argument("--strict", action="store_true", help="exit 1 se ci sono finding")
    a = ap.parse_args(argv)

    m = carica(pathlib.Path(a.root).resolve())
    try:
        if m.git("rev-parse", "--verify", "-q", f"{a.rev}^{{commit}}").returncode:
            raise m.GitError(f"ref sconosciuto {a.rev}")
        problems = m.check_rev(a.rev)
    except m.GitError as e:
        print(f"[ERROR][marcatori-conflitto][4bn] controllo non eseguito: {e}", file=sys.stderr)
        return 2

    if a.json:
        print(json.dumps({"check": "4bn", "rev": a.rev, "findings": problems}, indent=2, ensure_ascii=False))
    elif not problems:
        print(f"[4bn] OK — nessun marcatore di conflitto nei file in coda su {a.rev}")
    else:
        print("## WARNING (marcatori di conflitto)")
        for p in problems:
            righe = ", ".join(str(n) for n, _ in p["markers"][:8]) or "-"
            extra = f"; JSON non valido: {p['json_error']}" if p["json_error"] else ""
            print(f"- [WARNING][marcatori-conflitto][4bn] {p['path']}: marcatori alle righe {righe}"
                  f" su {a.rev}{extra}. {m.procedura(p['path'])}")
        print(f"\nTotale: {len(problems)} file")
    return 1 if problems and a.strict else 0


if __name__ == "__main__":
    sys.exit(main())

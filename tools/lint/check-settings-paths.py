#!/usr/bin/env python3
"""Check 4bl — nessun path assoluto o fuori repo in `.claude/settings.json`.

Legge solo i settings versionati. Segnala ogni valore di `permissions.additionalDirectories` (e
delle altre liste di path ovvie: chiavi `additionalDirectories`, `allowedDirectories`,
`directories`, `additionalPaths`, a qualunque profondita') che e' assoluto (`/...`, `~...`,
lettera di unita' Windows `C:\\...`) o che contiene un segmento `..` (il controllo `..` precede
l'esenzione delle variabili). Le variabili ammesse sono solo `${CLAUDE_PROJECT_DIR}`/`$CLAUDE_PROJECT_DIR`;
`$HOME`, `${HOME}`, `~`, `%USERPROFILE%` e ogni altra variabile in testa al path puntano fuori dal
progetto e sono finding. Le regole di `permissions.allow|deny|ask` sono lette: si estrae il path tra
parentesi (per `Bash(...)` ogni token che sembra un path) e vale la stessa regola.
File assente: nessun finding. JSON non valido: un finding «non verificabile» (sempre WARNING).

Severita': WARNING; ERROR solo se `settings_paths_check.required_from` (factory.config.yaml) e'
presente ed e' <= oggi. Chiave assente = solo WARNING.

Non garantisce: non vede `settings.local.json`, i settings user-level ne' i permessi effettivi;
non risolve symlink.

Uso:
    python3 tools/lint/check-settings-paths.py [--root <factory>] [--oggi AAAA-MM-GG] [--json] [--strict]
Exit code: 0 anche con finding; con --strict 1 se c'e' almeno un ERROR.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys

CHIAVI_PATH = {"additionalDirectories", "allowedDirectories", "directories", "additionalPaths"}
UNITA = re.compile(r"^[A-Za-z]:[\\/]")


def required_from(root):
    """Valore di settings_paths_check.required_from, o None se blocco o chiave mancano."""
    cfg = pathlib.Path(root) / "factory.config.yaml"
    if not cfg.exists():
        return None
    in_blocco = False
    for line in cfg.read_text(encoding="utf-8", errors="replace").splitlines():
        if re.match(r"^settings_paths_check:\s*(#.*)?$", line):
            in_blocco = True
            continue
        if in_blocco:
            if line.strip() and not line.startswith((" ", "\t", "#")):
                break
            m = re.match(r"^\s+required_from:\s*[\"']?([^\"'#\s]*)", line)
            if m:
                return m.group(1) or None
    return None
# La lettura a regex di required_from resta (non yaml): il check e' solo stdlib e legge una sola chiave
# scalare; 4bk usa PyYAML solo per le eccezioni strutturate.


PROGETTO = re.compile(r"^(\$\{CLAUDE_PROJECT_DIR\}|\$CLAUDE_PROJECT_DIR)(?=$|[\\/])")
VARIABILE = re.compile(r"^(\$\{[^}]*\}|\$[A-Za-z_][A-Za-z0-9_]*|%[^%]+%)")
NON_PATH = {"/dev/null"}


def motivo(valore):
    """Motivo per cui il path non e' ammesso, o None se e' pulito."""
    v = valore.strip()
    if ".." in re.split(r"[\\/]", v):
        return "esce dal repo (..)"
    if PROGETTO.match(v):
        return None
    if VARIABILE.match(v):
        return "variabile che punta fuori dal progetto"
    if v.startswith(("/", "\\", "~")) or UNITA.match(v):
        return "path assoluto"
    return None


def _motivo_regola(regola):
    """Motivo per una regola di permessi `Tool(spec)`, o None."""
    m = re.match(r"^\s*([A-Za-z_*][\w*.-]*)\((.*)\)\s*$", regola, re.S)
    if not m:
        return None
    tool, spec = m.group(1), m.group(2).strip()
    candidati = spec.split() if tool == "Bash" else [spec]
    for c in candidati:
        c = c.strip("\"'")
        if c in NON_PATH:
            continue
        r = motivo(c)
        if r:
            return r
    return None


def _scansiona(nodo, percorso, out):
    if isinstance(nodo, dict):
        for k, v in nodo.items():
            p = percorso + [k]
            if k in ("allow", "deny", "ask") and p[-2:-1] == ["permissions"] and isinstance(v, list):
                for i, val in enumerate(v):
                    if isinstance(val, str):
                        m = _motivo_regola(val)
                        if m:
                            out.append({"chiave": ".".join(p) + "[%d]" % i, "valore": val, "motivo": m})
            elif k in CHIAVI_PATH and isinstance(v, list):
                for i, val in enumerate(v):
                    if isinstance(val, str):
                        m = motivo(val)
                        if m:
                            out.append({"chiave": ".".join(p) + "[%d]" % i, "valore": val, "motivo": m})
            else:
                _scansiona(v, p, out)
    elif isinstance(nodo, list):
        for i, v in enumerate(nodo):
            _scansiona(v, percorso + [str(i)], out)


def check(root):
    f = pathlib.Path(root) / ".claude" / "settings.json"
    if not f.is_file():
        return []
    try:
        dati = json.loads(f.read_text(encoding="utf-8"))
    except ValueError:
        return [{"chiave": "(file)", "valore": "", "motivo": "non verificabile: JSON non valido",
                 "nonverificabile": True}]
    out = []
    _scansiona(dati, [], out)
    return out


def severita(root, oggi, findings=()):
    if findings and all(x.get("nonverificabile") for x in findings):
        return "WARNING"
    since = required_from(root)
    if since and re.match(r"^\d{4}-\d{2}-\d{2}$", since) and since <= oggi:
        return "ERROR"
    return "WARNING"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Check 4bl — path assoluti o fuori repo nei settings versionati")
    ap.add_argument("root", nargs="?", default=None, help="root della factory (alternativa a --root)")
    ap.add_argument("--root", dest="root_opt", default=None)
    ap.add_argument("--oggi", default=None, help="data di riferimento AAAA-MM-GG (default: oggi)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true", help="exit 1 se c'e' un ERROR")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.root_opt or args.root or ".").resolve()
    oggi = args.oggi or dt.date.today().isoformat()
    v = check(root)
    sev = severita(root, oggi, v)
    if args.json:
        print(json.dumps({"check": "4bl", "severita": sev, "findings": v}, indent=2, ensure_ascii=False))
    elif not v:
        print("[4bl] OK — nessun path assoluto o fuori repo in .claude/settings.json")
    else:
        print("## %s (path nei settings versionati)" % sev)
        for x in v:
            print("- [%s][settings-paths][4bl] .claude/settings.json %s = %r: %s"
                  % (sev, x["chiave"], x["valore"], x["motivo"]))
        print("\nTotale: %d valori" % len(v))
    return 1 if v and sev == "ERROR" and args.strict else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
conflict_markers_check.py — marcatori di conflitto nei file append-only e derivati.

Un pull con stash o `--autostash` che va in conflitto lascia nel file le righe di git
(`<<<<<<< Updated upstream`, `=======`, `>>>>>>> Stashed changes`). Nei file sotto elenco
nessuno le guarda a occhio prima del commit, e una volta pubblicate la correzione si scontra con
il gate append-only di wiki/log.md (R.5): vanno fermate prima che entrino.

File controllati (FILES):
  wiki/log.md e gli archivi wiki/log-*.md, wiki/gaps.md, wiki/index.md,
  raw/.extraction-manifest.json (anche come JSON valido), management/kanban/sprint.md.
  Non controlla il registro sessioni (`.git/active-sessions.yaml`, oppure `memory/active-sessions.yaml`
  fuori da git): e' locale al clone e non tracciato, quindi mai tra i file in coda su HEAD.

Marcatore = riga che inizia con `<<<<<<< `, `||||||| ` o `>>>>>>> ` (o che e' solo `<<<<<<<`,
`|||||||`, `>>>>>>>`), oppure riga intera `=======`. Nei file .md `=======` dentro un blocco di
codice delimitato da ``` o ~~~ non conta: e' testo citato, non un conflitto. Gli altri marcatori
contano ovunque, perche' git non li scrive mai come testo normale.

Modalita' (exit 0 = pulito, 1 = marcatori o manifest non valido, 2 = controllo incompleto:
ref sconosciuto, git in errore o scaduto):
  --staged          contenuto in stage dei file in stage (hook pre-commit)
  --pre-push        legge da stdin le righe dell'hook pre-push e controlla, alla punta di ogni ref
                    pubblicato, i file toccati dai commit che il push porta sul remoto
  --rev <ref>       tutti i file dell'elenco cosi' come sono in <ref> (Check 4bn del lint: HEAD)
  --worktree        i file dell'elenco nel working tree e i file in conflitto di `git status`
                    (subito dopo un pull)
  --json            esito in JSON (con --rev e --worktree)

Solo stdlib + git. Nessuna scrittura.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
ZERO = "0" * 40

FILES = (
    "wiki/log.md",
    "wiki/log-*.md",
    "wiki/gaps.md",
    "wiki/index.md",
    "raw/.extraction-manifest.json",
    "management/kanban/sprint.md",
)
JSON_FILES = ("raw/.extraction-manifest.json",)

_MARKER = re.compile(rb"^(?:<<<<<<<|\|\|\|\|\|\|\||>>>>>>>)(?: |\r?$)")
_SEPARATOR = re.compile(rb"^=======\r?$")
_FENCE = re.compile(rb"^ {0,3}(```|~~~)")

PROCEDURA = {
    "wiki/log.md": (
        "wiki/log.md e' append-only (R.5): non togliere le righe a mano. Ruota il log con "
        "`python3 tools/wiki/rotate_log.py --apply --forza` (le entry con i marcatori passano in "
        "wiki/log-<data>.md), poi in un commit separato togli i marcatori dall'archivio, ripristina "
        "le intestazioni `---` / `date:` rimaste fuse e aggiungi una voce in coda al log che lo dice "
        "(come per i casi gia' avvenuti)."),
    "wiki/log-*.md": (
        "Archivio del log: togli i marcatori, tieni entrambe le versioni delle righe in conflitto e "
        "ripristina le intestazioni `---` / `date:` delle entry fuse; aggiungi una voce in coda a "
        "wiki/log.md."),
    "raw/.extraction-manifest.json": (
        "Togli i marcatori tenendo entrambe le entry (upstream e tua) e controlla il JSON con "
        "`python3 -m json.tool raw/.extraction-manifest.json >/dev/null`."),
    "management/kanban/sprint.md": (
        "sprint.md: togli i marcatori tenendo entrambe le versioni delle sezioni in conflitto e rileggi il file; "
        "se e' una vista generata, rigeneralo con il suo generatore."),
}
PROCEDURA_DEFAULT = (
    "Risolvi il conflitto tenendo entrambe le versioni delle righe (sono file in coda: si aggiunge, "
    "non si sceglie) e rimetti il file in stage.")


GIT_TIMEOUT = 60


class GitError(RuntimeError):
    """Comando git fallito o scaduto: il controllo e' incompleto, mai un «pulito»."""


def git(*args, must=False):
    """Esegue git. Con must=True un exit != 0 o il timeout alzano GitError (comando, exit, stderr)."""
    cmd = ["git", *args]
    try:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, timeout=GIT_TIMEOUT)
    except subprocess.TimeoutExpired:
        raise GitError(f"{' '.join(cmd)}: timeout dopo {GIT_TIMEOUT}s")
    if must and r.returncode:
        raise GitError(f"{' '.join(cmd)}: exit {r.returncode}: {r.stderr.decode('utf-8', 'replace').strip()[:300]}")
    return r


def is_watched(path: str) -> bool:
    return any(fnmatch.fnmatchcase(path, p) for p in FILES)


def find_markers(data: bytes, markdown: bool) -> list[tuple[int, str]]:
    """(numero di riga, riga) dei marcatori di conflitto in `data`."""
    found = []
    fence = None
    for n, line in enumerate(data.splitlines(), 1):
        if markdown:
            m = _FENCE.match(line)
            if m:
                if fence is None:
                    fence = m.group(1)
                elif m.group(1) == fence:
                    fence = None
        if _MARKER.match(line) or (_SEPARATOR.match(line) and fence is None):
            found.append((n, line.decode("utf-8", "replace").rstrip("\r")))
    return found


def check_content(path: str, data: bytes) -> dict | None:
    """Problemi di un file: {'path', 'markers': [(riga, testo)], 'json_error': str|None} o None."""
    markers = find_markers(data, path.endswith(".md"))
    json_error = None
    if path in JSON_FILES and data.strip():
        try:
            json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as e:
            json_error = str(e)
    if not markers and not json_error:
        return None
    return {"path": path, "markers": markers, "json_error": json_error}


def procedura(path: str) -> str:
    for pattern, testo in PROCEDURA.items():
        if fnmatch.fnmatchcase(path, pattern):
            return testo
    return PROCEDURA_DEFAULT


def report(problems: list[dict], where: str) -> str:
    out = [f"Marcatori di conflitto ({where}) in {len(problems)} file:"]
    for p in problems:
        out.append(f"  {p['path']}")
        for n, line in p["markers"][:6]:
            out.append(f"    riga {n}: {line[:100]}")
        if len(p["markers"]) > 6:
            out.append(f"    … e altri {len(p['markers']) - 6}")
        if p["json_error"]:
            out.append(f"    JSON non valido: {p['json_error']}")
        out.append("    → " + procedura(p["path"]))
    return "\n".join(out)


def blob(spec: str) -> bytes | None:
    r = git("cat-file", "blob", spec)
    return r.stdout if r.returncode == 0 else None


# --- modalita' -------------------------------------------------------------------------------

def check_staged() -> list[dict]:
    names = git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z", must=True).stdout.decode().split("\0")
    problems = []
    for path in filter(is_watched, filter(None, names)):
        data = blob(f":{path}")
        if data is not None and (p := check_content(path, data)):
            problems.append(p)
    return problems


def check_rev(rev: str) -> list[dict]:
    names = git("ls-tree", "-r", "--name-only", "-z", rev, must=True).stdout.decode().split("\0")
    problems = []
    for path in filter(is_watched, filter(None, names)):
        data = blob(f"{rev}:{path}")
        if data is not None and (p := check_content(path, data)):
            problems.append(p)
    return problems


def _pushed_files(local_sha: str, remote_sha: str) -> list[str]:
    if remote_sha != ZERO and git("cat-file", "-e", f"{remote_sha}^{{commit}}").returncode == 0:
        rng = [f"{remote_sha}..{local_sha}"]
    else:
        # ref nuovo sul remoto: i commit che nessun ref remoto conosce gia'
        rng = [local_sha, "--not", "--remotes"]
    out = git("log", "--format=", "--name-only", "--diff-filter=ACMR", "-z", *rng, must=True).stdout.decode()
    return sorted({n.strip("\n") for n in out.split("\0") if n.strip("\n")})


def check_pre_push(stdin_text: str) -> list[dict]:
    problems, seen = [], set()
    for line in stdin_text.splitlines():
        parts = line.split()
        if len(parts) != 4 or parts[1] == ZERO:
            continue  # riga malformata o cancellazione di un ref
        _, local_sha, remote_ref, remote_sha = parts
        for path in filter(is_watched, _pushed_files(local_sha, remote_sha)):
            if (local_sha, path) in seen:
                continue
            seen.add((local_sha, path))
            data = blob(f"{local_sha}:{path}")
            if data is not None and (p := check_content(path, data)):
                p["ref"] = remote_ref
                problems.append(p)
    return problems


def unmerged_paths() -> list[str]:
    out = git("diff", "--name-only", "--diff-filter=U", "-z", must=True).stdout.decode()
    return [n for n in out.split("\0") if n]


def check_worktree() -> tuple[list[str], list[dict]]:
    unmerged = unmerged_paths()
    problems = []
    for pattern in FILES:
        for f in sorted(ROOT.glob(pattern)):
            if f.is_file():
                rel = f.relative_to(ROOT).as_posix()
                if (p := check_content(rel, f.read_bytes())):
                    problems.append(p)
    return unmerged, problems


def _utf8_output() -> None:
    # Su Windows la console e i pipe sono spesso in cp1252: il report contiene caratteri come «→»
    # e una stampa fallita non deve diventare «controllo incompleto» quando i marcatori ci sono.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except (AttributeError, ValueError, OSError):
            pass  # stream non riconfigurabile (es. sostituito da un test): le stampe passano da _print_safe


def _print_safe(text: str, file=None) -> None:
    """Stampa che non cambia l'esito: se lo stream non sa codificare il testo, scrive in ASCII."""
    file = file or sys.stdout
    try:
        print(text, file=file)
    except UnicodeEncodeError:
        print(text.encode("ascii", "backslashreplace").decode("ascii"), file=file)


def main(argv=None) -> int:
    _utf8_output()
    try:
        return _main(argv)
    except GitError as e:
        _print_safe(f"conflict_markers_check: controllo incompleto — {e}", file=sys.stderr)
        return 2


def _main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--staged", action="store_true")
    g.add_argument("--pre-push", action="store_true")
    g.add_argument("--rev")
    g.add_argument("--worktree", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    if a.pre_push:
        problems = check_pre_push(sys.stdin.read())
        if problems:
            refs = ", ".join(sorted({p["ref"] for p in problems}))
            _print_safe(f"\n[conflitti] PUSH BLOCCATO — {refs}\n\n" + report(problems, "commit da pubblicare")
                        + "\n\nCorreggi con un nuovo commit (niente force push, niente --no-verify) e ripeti il push.\n",
                        file=sys.stderr)
            return 1
        return 0

    if a.worktree:
        unmerged, problems = check_worktree()
        if a.json:
            _print_safe(json.dumps({"unmerged": unmerged, "problems": problems}, ensure_ascii=False, indent=2))
        else:
            if unmerged:
                _print_safe("File in conflitto secondo git status: " + ", ".join(unmerged))
            if problems:
                _print_safe(report(problems, "working tree"))
            if not unmerged and not problems:
                print("conflitti: nessun file in conflitto, nessun marcatore nei file in coda")
        return 1 if unmerged or problems else 0

    if a.rev:
        if git("rev-parse", "--verify", "-q", f"{a.rev}^{{commit}}").returncode:
            _print_safe(f"conflict_markers_check: ref sconosciuto {a.rev}", file=sys.stderr)
            return 2
        problems = check_rev(a.rev)
        if a.json:
            _print_safe(json.dumps({"rev": a.rev, "problems": problems}, ensure_ascii=False, indent=2))
        elif problems:
            _print_safe(report(problems, a.rev))
        return 1 if problems else 0

    problems = check_staged()
    if problems:
        _print_safe(report(problems, "stage"))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

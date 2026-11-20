#!/usr/bin/env python3
"""Enumeratore deterministico di un repository locale: struttura e metadati git, mai contenuto.

Produce su stdout un JSON con metadati git, albero delle directory e elenco dei file.
Non apre, non legge e non interpreta nessun file del repository: usa solo
`git -C <path> rev-parse/log/ls-tree` e la visita del filesystem (nomi e dimensioni).
Il contenuto dei file e' input non fidato e lo legge un altro attore, senza shell.

Uso:
    python3 tools/sync/repo_enumerate.py <path> [--depth N] [--max-files N]

Exit code: 0 ok, 2 path non valido.
"""
import argparse
import json
import os
import re
import subprocess
import sys

EXCLUDED_DIRS = {
    ".git", "node_modules", "vendor", "dist", "build", "target", ".venv",
    "__pycache__", ".next", ".nuxt", "coverage", ".pytest_cache", ".mypy_cache",
}
EXCLUDED_FILES = {".DS_Store"}
MANIFESTS = {
    "package.json", "pyproject.toml", "pom.xml", "go.mod", "Cargo.toml", "Gemfile",
    "composer.json", "requirements.txt", "setup.py",
}


def _git(path, *args):
    """Esegue un sottocomando git di sola lettura sui metadati; '' se fallisce."""
    try:
        out = subprocess.run(
            ["git", "-C", path] + list(args),
            capture_output=True, text=True, timeout=60, encoding="utf-8", errors="replace"
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return out.stdout.strip() if out.returncode == 0 else ""


def make_slug(path, max_len=40):
    name = os.path.basename(os.path.abspath(path).rstrip(os.sep))
    slug = re.sub(r"[^a-z0-9._-]+", "-", name.lower()).strip("-")
    return slug[:max_len] or "repo"


def git_metadata(path):
    if not os.path.exists(os.path.join(path, ".git")):
        return None
    commits_year = _git(path, "log", "--since=1 year ago", "--format=%ai")
    head = _git(path, "log", "-1", "--format=%H|%ai|%s")
    parts = head.split("|", 2) if head else ["", "", ""]
    contributors = sorted({c for c in _git(path, "log", "--format=%an").splitlines() if c})
    return {
        "branch": _git(path, "rev-parse", "--abbrev-ref", "HEAD"),
        "commit": parts[0],
        "commit_date": parts[1] if len(parts) > 1 else "",
        "commit_subject": parts[2] if len(parts) > 2 else "",
        "contributors": contributors[:10],
        "commits_last_year": len(commits_year.splitlines()) if commits_year else 0,
    }


def walk(path, depth, max_files):
    """Visita nomi e dimensioni (lstat): nessuna open(), nessun follow dei symlink."""
    dirs, files, counts = [], [], {}
    total = 0
    root = os.path.abspath(path)
    for cur, dnames, fnames in os.walk(root, followlinks=False):
        dnames[:] = sorted(d for d in dnames if d not in EXCLUDED_DIRS)
        rel = os.path.relpath(cur, root)
        level = 0 if rel == "." else rel.count(os.sep) + 1
        if rel != "." and level <= depth:
            dirs.append(rel)
        top = "." if rel == "." else rel.split(os.sep)[0]
        for fn in sorted(fnames):
            if fn in EXCLUDED_FILES:
                continue
            total += 1
            counts[top] = counts.get(top, 0) + 1
            if len(files) < max_files:
                full = os.path.join(cur, fn)
                try:
                    size = os.lstat(full).st_size
                except OSError:
                    size = -1
                files.append({"path": os.path.relpath(full, root), "bytes": size})
    return dirs, files, counts, total


def enumerate_repo(path, depth=3, max_files=2000):
    dirs, files, counts, total = walk(path, depth, max_files)
    return {
        "source_path": os.path.abspath(path),
        "slug": make_slug(path),
        "is_git": os.path.exists(os.path.join(path, ".git")),
        "git": git_metadata(path),
        "tree_depth": depth,
        "directories": dirs,
        "files_per_top_level": counts,
        "files_total": total,
        "files_listed": len(files),
        "files_truncated": total > len(files),
        "files": files,
        "manifests": sorted(f["path"] for f in files if os.path.basename(f["path"]) in MANIFESTS),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("path")
    ap.add_argument("--depth", type=int, default=3)
    ap.add_argument("--max-files", type=int, default=2000)
    args = ap.parse_args(argv)
    if not os.path.isdir(args.path):
        print("path non valido: %s" % args.path, file=sys.stderr)
        return 2
    json.dump(enumerate_repo(args.path, args.depth, args.max_files), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

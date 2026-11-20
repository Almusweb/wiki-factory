#!/usr/bin/env python3
"""log_union_driver.py — merge driver `factory-log-union` per wiki/log.md.

Il log e' append-only: ogni branch aggiunge voci in coda. `git merge-file --union` non basta:
le righe identiche aggiunte da entrambi i lati (`---`, `type: session-start`, `scope: all`, ...)
sono trattate come una modifica comune e prese una sola volta, quindi due voci simili si fondono
in un unico blocco con le righe mescolate (es. due `context:` nella stessa voce).

Il driver lavora sui blocchi interi: se entrambi i lati estendono la base (la base e' un prefisso
di %A e di %B) il risultato e' %A seguito dalla coda aggiunta da %B. Il controllo del prefisso
riguarda il solo corpo: il frontmatter iniziale (`---` ... `---`) si risolve a parte, prendendo
la versione del lato che lo ha cambiato. Se il frontmatter e' cambiato in modo diverso dai due
lati, o se un lato non estende il corpo della base (rotazione del log), ricade su
`git merge-file --union`; nel caso di frontmatter divergente l'esito e' non zero (conflitto).

Configurazione (registrata da tools/vcs/install_factory_hooks.py):
    python3 tools/wiki/log_union_driver.py %O %A %B

Scrive il risultato in %A, exit 0. Solo stdlib + git.
"""
import subprocess
import sys


def _split(data: bytes):
    """(frontmatter, corpo): il frontmatter e' il blocco iniziale `---\\n...\\n---\\n`, se presente."""
    if data.startswith(b"---\n"):
        fine = data.find(b"\n---\n", 3)
        if fine != -1:
            taglio = fine + len(b"\n---\n")
            return data[:taglio], data[taglio:]
    return b"", data


def _frontmatter(base: bytes, ours: bytes, theirs: bytes):
    if ours == theirs or theirs == base:
        return ours
    if ours == base:
        return theirs
    return None


def _corpo(base: bytes, ours: bytes, theirs: bytes):
    if not (ours.startswith(base) and theirs.startswith(base)):
        return None
    coda = theirs[len(base):]
    if not coda or ours == theirs:
        return ours
    if ours and not ours.endswith(b"\n"):
        ours += b"\n"
    return ours + coda


def merge(base: bytes, ours: bytes, theirs: bytes):
    """Contenuto fuso, o None se il frontmatter diverge o un lato non estende il corpo della base."""
    fb, cb = _split(base)
    fo, co = _split(ours)
    ft, ct = _split(theirs)
    fm = _frontmatter(fb, fo, ft)
    corpo = _corpo(cb, co, ct)
    if fm is None or corpo is None:
        return None
    return fm + corpo


def driver(base_path: str, ours_path: str, theirs_path: str) -> int:
    with open(base_path, "rb") as f:
        base = f.read()
    with open(ours_path, "rb") as f:
        ours = f.read()
    with open(theirs_path, "rb") as f:
        theirs = f.read()
    fuso = merge(base, ours, theirs)
    if fuso is None:
        rc = subprocess.run(["git", "merge-file", "--union", ours_path, base_path, theirs_path]).returncode
        fb, fo, ft = (_split(x)[0] for x in (base, ours, theirs))
        if rc == 0 and _frontmatter(fb, fo, ft) is None:
            return 1
        return rc
    with open(ours_path, "wb") as f:
        f.write(fuso)
    return 0


def main(argv):
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    return driver(*argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

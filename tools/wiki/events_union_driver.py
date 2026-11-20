#!/usr/bin/env python3
"""events_union_driver.py — merge driver `factory-events-union` per analytics/events/*.jsonl.

Gli eventi sono append-only: ogni branch aggiunge righe in coda. Due session-close vicini
aggiungono righe diverse nello stesso punto e git segnala un conflitto fisso.

Il driver unisce per righe, senza duplicati: il risultato e' %A (ordine invariato) seguito dalle
righe di %B che non sono gia' in %A, nell'ordine di %B. Una riga identica presente su entrambi i
lati compare una sola volta (anche se gia' ripetuta dentro %A: le righe di %A non si toccano oltre
al riordino dei fine riga). %O non serve: il file e' append-only, le cancellazioni non sono un
caso atteso e si preferisce non perdere dati.

Configurazione (registrata da tools/vcs/install_factory_hooks.py):
    python3 tools/wiki/events_union_driver.py %O %A %B

Scrive il risultato in %A, exit 0. Solo stdlib.
"""
import sys


def merge(base: bytes, ours: bytes, theirs: bytes) -> bytes:
    """Righe di ours + righe di theirs non gia' presenti (base non serve: unione pura)."""
    righe_ours = ours.splitlines()
    viste = set(righe_ours)
    nuove = []
    for riga in theirs.splitlines():
        if riga not in viste:
            viste.add(riga)
            nuove.append(riga)
    tutte = righe_ours + nuove
    return b"".join(r + b"\n" for r in tutte)


def driver(base_path: str, ours_path: str, theirs_path: str) -> int:
    with open(base_path, "rb") as f:
        base = f.read()
    with open(ours_path, "rb") as f:
        ours = f.read()
    with open(theirs_path, "rb") as f:
        theirs = f.read()
    with open(ours_path, "wb") as f:
        f.write(merge(base, ours, theirs))
    return 0


def main(argv):
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    return driver(*argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

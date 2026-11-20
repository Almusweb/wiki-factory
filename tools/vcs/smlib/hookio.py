"""Scrittura degli hook git con fine riga LF, su ogni sistema operativo."""
from __future__ import annotations

from pathlib import Path


def to_lf(data: bytes) -> bytes:
    """Riporta i fine riga CRLF a LF."""
    return data.replace(b"\r\n", b"\n")


def write_hook(hook_path: Path, content: str) -> None:
    """Scrive l'hook in byte.

    Su Windows write_text tradurrebbe i fine riga in CRLF e la shell di Git non eseguirebbe
    l'hook («set: pipefail: invalid option name», interprete con \\r finale).
    write_text(newline=...) non e' un'alternativa: esiste solo da Python 3.10.
    """
    hook_path.write_bytes(content.encode("utf-8"))

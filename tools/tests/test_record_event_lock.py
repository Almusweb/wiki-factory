"""_FileLock di record-event.py, ramo Windows (spin-lock con file .spin).

Un .spin lasciato da un processo morto va rimosso quando e' piu' vecchio di 2x timeout.
L'eta' si calcolava come time.monotonic() - st_mtime: due orologi diversi, eta' sempre
negativa, lock mai considerato stale. Su Windows ogni record-event successivo andava in
timeout e l'evento si perdeva. Il ramo si esercita anche su POSIX forzando _HAS_FCNTL.
"""
from __future__ import annotations

import importlib.util
import os
import time
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "analytics" / "record-event.py"


def _modulo():
    spec = importlib.util.spec_from_file_location("record_event_lock_test", _SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def test_spin_stale_viene_rimosso(tmp_path, monkeypatch):
    mod = _modulo()
    monkeypatch.setattr(mod, "_HAS_FCNTL", False)
    lock_path = tmp_path / "events.lock"
    spin = lock_path.with_suffix(".spin")
    spin.write_text("99999", encoding="utf-8")
    un_ora_fa = time.time() - 3600
    os.utime(spin, (un_ora_fa, un_ora_fa))

    lock = mod._FileLock(lock_path, timeout=0.5)
    try:
        assert lock.acquire() is True, "un .spin vecchio di 1 h deve essere considerato stale"
    finally:
        lock.release()
    assert not spin.exists()


def test_spin_fresco_non_viene_rubato(tmp_path, monkeypatch):
    mod = _modulo()
    monkeypatch.setattr(mod, "_HAS_FCNTL", False)
    lock_path = tmp_path / "events.lock"
    spin = lock_path.with_suffix(".spin")
    spin.write_text("12345", encoding="utf-8")  # mtime = adesso: lock di un processo vivo

    lock = mod._FileLock(lock_path, timeout=0.3)
    assert lock.acquire() is False, "un .spin fresco appartiene a un altro processo"
    assert spin.read_text(encoding="utf-8") == "12345"

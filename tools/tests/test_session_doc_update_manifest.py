"""Sottocomando `update-manifest` di session_doc.py: formato canonico e rifiuto di entry non valide."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = ROOT / "tools" / "session" / "session_doc.py"


def _serializza():
    spec = importlib.util.spec_from_file_location("mud", ROOT / "tools" / "wiki" / "manifest_union_driver.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.serializza


def _run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, encoding="utf-8", errors="replace")


def test_update_manifest_formato_canonico(tmp_path):
    m = tmp_path / "manifest.json"
    m.write_text(_serializza()({"a": {"x": 1}}), encoding="utf-8")
    r = _run("update-manifest", str(m), "raw/sessions/s1", "--entry-json", '{"titolo": "città"}')
    assert r.returncode == 0, r.stderr
    testo = m.read_text(encoding="utf-8")
    assert testo.endswith("\n")
    dati = json.loads(testo)
    assert testo == _serializza()(dati)
    assert dati["a"] == {"x": 1}
    assert dati["raw/sessions/s1"] == {"titolo": "città"}


def test_update_manifest_entry_file(tmp_path):
    m = tmp_path / "manifest.json"
    e = tmp_path / "entry.json"
    e.write_text('{"k": 2}', encoding="utf-8")
    r = _run("update-manifest", str(m), "chiave", "--entry-file", str(e))
    assert r.returncode == 0, r.stderr
    assert m.read_text(encoding="utf-8") == _serializza()({"chiave": {"k": 2}})


def test_update_manifest_entry_non_valida_lascia_file_intatto(tmp_path):
    m = tmp_path / "manifest.json"
    originale = _serializza()({"a": 1})
    m.write_text(originale, encoding="utf-8")
    for bad in ("{non json", "[1, 2]"):
        r = _run("update-manifest", str(m), "k", "--entry-json", bad)
        assert r.returncode != 0
        assert m.read_text(encoding="utf-8") == originale

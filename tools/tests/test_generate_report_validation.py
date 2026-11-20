"""generate-report: senza jsonschema la validazione non viene saltata in silenzio."""
import builtins
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SA = ROOT / "tools" / "session-analysis"


def _load():
    spec = importlib.util.spec_from_file_location("generate_report_mod", SA / "generate-report.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def no_jsonschema(monkeypatch):
    monkeypatch.delitem(sys.modules, "jsonschema", raising=False)
    real_find = importlib.util.find_spec
    monkeypatch.setattr(importlib.util, "find_spec",
                        lambda n, *a, **k: None if n == "jsonschema" else real_find(n, *a, **k))
    real_import = builtins.__import__

    def fake(name, *a, **k):
        if name == "jsonschema" or name.startswith("jsonschema."):
            raise ImportError("blocked")
        return real_import(name, *a, **k)
    monkeypatch.setattr(builtins, "__import__", fake)


def test_schema_reale_validato_dallo_stdlib(no_jsonschema):
    # Lo schema reale ($ref locali, const, type a unione) rientra nel sottoinsieme
    # dello stdlib: senza jsonschema la validazione avviene davvero.
    mod = _load()
    out = mod._validate_json_report({}, SA / "schema-anomaly.json")
    assert out and all(w.startswith("SCHEMA_ERROR:") for w in out)
    assert not any(w.startswith("INFO:") for w in out)


def test_schema_fuori_allowlist_da_errore_esplicito(no_jsonschema, tmp_path):
    mod = _load()
    schema = {"$defs": {"SessionAnalysisReport": {"type": "object", "oneOf": []}}}
    p = tmp_path / "s.json"
    p.write_text(json.dumps(schema))
    out = mod._validate_json_report({}, p)
    assert out and out[0].startswith("ERROR:")
    assert "NOT performed" in out[0]
    assert not any(w.startswith("INFO:") for w in out)


def test_schema_nell_allowlist_usa_validatore_stdlib(no_jsonschema, tmp_path):
    mod = _load()
    schema = {"$defs": {"SessionAnalysisReport": {
        "type": "object", "required": ["a"], "additionalProperties": False,
        "properties": {"a": {"type": "integer"}}}}}
    p = tmp_path / "s.json"
    p.write_text(json.dumps(schema))
    assert mod._validate_json_report({"a": 1}, p) == []
    bad = mod._validate_json_report({"a": "x"}, p)
    assert bad and bad[0].startswith("SCHEMA_ERROR:")


def test_main_esce_con_errore_e_non_scrive(no_jsonschema, tmp_path, monkeypatch):
    mod = _load()
    for n in ("a", "m", "p"):
        (tmp_path / f"{n}.json").write_text("{}")
    out_dir = tmp_path / "out"
    monkeypatch.setattr(mod, "_validate_json_report", lambda r, s: ["ERROR: validazione non eseguita"])
    monkeypatch.setattr(sys, "argv", ["generate-report.py", str(tmp_path / "a.json"),
                                      str(tmp_path / "m.json"), str(tmp_path / "p.json"),
                                      "--output-dir", str(out_dir)])
    assert mod.main() == 3
    assert not out_dir.exists()


def test_schema_assente_da_errore_esplicito(tmp_path):
    mod = _load()
    out = mod._validate_json_report({}, tmp_path / "non-esiste.json")
    assert out and out[0].startswith("ERROR:") and "NOT performed" in out[0]
    assert not any(w.startswith("WARN:") for w in out)


def test_sottoschema_assente_da_errore_esplicito(tmp_path):
    mod = _load()
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"$defs": {}}))
    out = mod._validate_json_report({}, p)
    assert out and out[0].startswith("ERROR:")
    assert not any(w.startswith("WARN:") for w in out)


def test_main_con_schema_assente_esce_3_e_non_scrive(tmp_path, monkeypatch):
    mod = _load()
    for n in ("a", "m", "p"):
        (tmp_path / f"{n}.json").write_text("{}")
    out_dir = tmp_path / "out"
    monkeypatch.setattr(sys, "argv", ["generate-report.py", str(tmp_path / "a.json"),
                                      str(tmp_path / "m.json"), str(tmp_path / "p.json"),
                                      "--schema", str(tmp_path / "manca.json"),
                                      "--output-dir", str(out_dir)])
    assert mod.main() == 3
    assert not out_dir.exists()

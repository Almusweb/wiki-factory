"""
Affidabilita' del consuntivo dei token: versione e schema nell'evento, verifica di versione con
conteggio indipendente, allowlist del writer. Gli eventi si scrivono solo in factory di prova
sotto tmp_path.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_harvest_session_tokens import (  # noqa: E402
    HARVEST, _events, _factory_with_harvest, _harvest, _transcript)

ROOT = Path(__file__).resolve().parents[2]


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / "analytics" / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


hv = _load("harvest_aff", "harvest-session-tokens.py")
rec = _load("record_event_aff", "record-event.py")


def _with_version(path: Path, version: str) -> Path:
    first = json.dumps({"type": "user", "version": version, "timestamp": "2026-09-10T09:59:00Z"})
    path.write_text(first + "\n" + path.read_text(encoding="utf-8"), encoding="utf-8")
    return path


def _verify(t):
    return subprocess.run([sys.executable, str(HARVEST), "--verify-version", str(t)],
                          capture_output=True, text=True, timeout=300, encoding="utf-8", errors="replace")


def _supported_version():
    return sorted(hv.SUPPORTED_CC_VERSIONS)[0]


def test_evento_porta_versione_e_schema_di_primo_livello(tmp_path):
    root = _factory_with_harvest(tmp_path)
    t = _with_version(_transcript(tmp_path), "9.9.999")
    p = _harvest(root, t)
    assert p.returncode == 0, p.stderr
    out = json.loads(p.stdout)
    assert out["cc_version"] == "9.9.999" and out["schema_degraded"] is True
    ev = _events(root)[0]
    assert ev["cc_version"] == "9.9.999" and ev["schema_degraded"] is True and "extras" not in ev


def test_versione_supportata_non_degradata_e_idempotenza(tmp_path):
    root = _factory_with_harvest(tmp_path)
    t = _with_version(_transcript(tmp_path), _supported_version())
    assert _harvest(root, t).returncode == 0
    assert _harvest(root, t).returncode == 0
    evs = _events(root)
    assert len(evs) == 1 and evs[0]["schema_degraded"] is False
    assert evs[0]["cc_version"] == _supported_version()


def test_versione_assente_diventa_unknown_e_degradata(tmp_path):
    root = _factory_with_harvest(tmp_path)
    t = _transcript(tmp_path)  # nessuna riga con "version"
    p = _harvest(root, t)
    assert p.returncode == 0, p.stderr
    ev = _events(root)[0]
    assert ev["cc_version"] == "unknown" and ev["schema_degraded"] is True


def test_dry_run_riporta_i_campi_senza_scrivere(tmp_path):
    root = _factory_with_harvest(tmp_path)
    t = _with_version(_transcript(tmp_path), "9.9.999")
    p = subprocess.run([sys.executable, str(root / "tools" / "analytics" / HARVEST.name), str(t),
                        "--dry-run"], cwd=root, capture_output=True, text=True, timeout=300, encoding="utf-8", errors="replace")
    ev = json.loads(p.stdout)["results"][0]["event"]
    assert ev["cc_version"] == "9.9.999" and _events(root) == []


def test_verify_version_concorda(tmp_path):
    t = _with_version(_transcript(tmp_path), _supported_version())
    p = _verify(t)
    d = json.loads(p.stdout)
    assert p.returncode == 0 and d["concordant"] and d["supportable"]
    assert d["mismatches"] == [] and d["cc_version"] == _supported_version()


def test_verify_version_senza_finale_nei_subagenti_non_e_supportabile(tmp_path):
    t = _with_version(_transcript(tmp_path), "9.9.998")
    sub = t.parent / t.stem / "subagents"
    sub.mkdir(parents=True)
    row = {"type": "assistant", "timestamp": "2026-09-10T10:01:00Z",
           "message": {"id": "s1", "model": "claude-opus-5-5", "stop_reason": None,
                       "usage": {"input_tokens": 1, "output_tokens": 3}}}
    (sub / "agent-a.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
    p = _verify(t)
    d = json.loads(p.stdout)
    assert d["concordant"] and not d["supportable"] and d["subagent_without_final"] == 1
    assert p.returncode == 1


def test_verify_version_discordanza(tmp_path, monkeypatch):
    t = _with_version(_transcript(tmp_path), _supported_version())
    real = hv.independent_count

    def skewed(path):
        tot, n, m = real(path)
        for v in tot.values():
            v["output"] += 1
        return tot, n, m
    monkeypatch.setattr(hv, "independent_count", skewed)
    d = hv.verify_version(str(t))
    assert not d["concordant"] and d["mismatches"] and not d["supportable"]


def test_verify_version_transcript_illeggibile(tmp_path):
    p = _verify(tmp_path)
    assert p.returncode in (0, 1)
    assert json.loads(p.stdout)["status"] in ("skip", "error")


def _base_event():
    return {"task_id": "TSK-001", "project_id": "demo", "actor_type": "agent",
            "actor_id": "claude-code:main", "task_type": "session-aggregate",
            "state": "finished", "ts": "2026-11-18T10:00:00Z",
            "tokens": {"input": 1, "output": 1, "cache_read": 0, "cache_write": 0},
            "model": "test-model", "tool_calls": []}


def test_writer_ammette_i_due_campi_al_primo_livello():
    ev = _base_event()
    ev["cc_version"] = "2.1.325"
    ev["schema_degraded"] = False
    assert rec._check_pii(ev) is None
    ev["cc_version"] = "unknown"
    ev["schema_degraded"] = True
    assert rec._check_pii(ev) is None
    ev["campo_ignoto"] = 1
    assert rec._check_pii(ev) is not None


def test_writer_rifiuta_tipi_sbagliati():
    for field, bad in (("cc_version", 2), ("cc_version", ""), ("cc_version", None),
                       ("schema_degraded", "false"), ("schema_degraded", 1)):
        ev = _base_event()
        ev[field] = bad
        assert rec._check_pii(ev) is not None, (field, bad)

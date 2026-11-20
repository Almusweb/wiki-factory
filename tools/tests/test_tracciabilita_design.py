"""Check 4bi: tracciabilita' ADR -> US -> TSK (tools/lint/check_tracciabilita_design.py), EP-097 US-384.

Ogni test costruisce una factory minima in tmp_path; il check gira come sottoprocesso con --json.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

LINT = Path(__file__).resolve().parents[1] / "lint"

W1 = "---\ntype: lint-report\nreport: w1-design\ndate: 2026-11-16\nn: 90\nok_chat_rate: 1.0\n---\n\n# W1\n"
CHIUSURA_OK = "## Chiusura\n\n| AC | Esito | Evidenza |\n|---|---|---|\n| US-001 AC1 | SI | test |\n"
CHIUSURA_KO = "## Chiusura\n\n- Verifica fatta, tutto ok.\n"


def _cfg(root: Path, enabled="true", dal="2026-11-17", soglia="0.50", premortem="false") -> None:
    (root / "factory.config.yaml").write_text(
        "design_traceability:\n"
        f"  enabled: {enabled}\n  required_from: \"{dal}\"\n"
        "  report_w1: \"wiki/lint/*-w1-design.md\"\n"
        f"  soglia_spegnimento: {soglia}\n  premortem_pre_tpm: {premortem}\n", encoding="utf-8")


def _w1(root: Path, testo: str = W1) -> None:
    d = root / "wiki" / "lint"
    d.mkdir(parents=True, exist_ok=True)
    (d / "2026-11-16-w1-design.md").write_text(testo, encoding="utf-8")


def _art(root: Path, tid: str, corpo: str = "", **fm) -> None:
    d = root / "management" / "kanban" / "EP-001-x" / "US-001-x"
    d.mkdir(parents=True, exist_ok=True)
    righe = "".join(f"{k}: {v}\n" for k, v in fm.items())
    (d / f"{tid}.md").write_text(f"---\nid: {tid}\n{righe}---\n\n# {tid}\n\n{corpo}", encoding="utf-8")


def _adr(root: Path, aid: str, **fm) -> None:
    d = root / "design_&_architecture" / "decisions"
    d.mkdir(parents=True, exist_ok=True)
    righe = "".join(f"{k}: {v}\n" for k, v in fm.items())
    (d / f"{aid}.md").write_text(f"---\nid: {aid}\n{righe}---\n\n# {aid}\n\n## Decisione\n\nx\n", encoding="utf-8")


def _base(root: Path) -> None:
    _cfg(root)
    _w1(root)
    _art(root, "EP-001", status="todo")
    _art(root, "US-001", status="ready", epic="EP-001")
    _adr(root, "ADR-001", status="accepted", created="2026-01-01")  # storico: fuori perimetro


def _run(root: Path, *args: str):
    r = subprocess.run([sys.executable, str(LINT / "check_tracciabilita_design.py"), "--root", str(root),
                        "--json", *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def _codici(out):
    return sorted(f["codice"] for f in out["findings"])


def test_spento_di_default(tmp_path):
    _base(tmp_path)
    _cfg(tmp_path, enabled="false")
    _adr(tmp_path, "ADR-002", status="accepted", created="2026-11-20")
    out = _run(tmp_path)
    assert out["findings"] == [] and "spento" in out["diagnostica"][0]


def test_noop_senza_report_w1(tmp_path):
    _base(tmp_path)
    (tmp_path / "wiki" / "lint" / "2026-11-16-w1-design.md").unlink()
    _adr(tmp_path, "ADR-002", status="accepted", created="2026-11-20")
    out = _run(tmp_path)
    assert out["findings"] == [] and "report W1" in out["diagnostica"][0]


def test_noop_report_w1_senza_numeri(tmp_path):
    _base(tmp_path)
    _w1(tmp_path, "---\ndate: 2026-11-16\n---\n")
    _adr(tmp_path, "ADR-002", status="accepted", created="2026-11-20")
    assert _run(tmp_path)["findings"] == []


def test_noop_se_required_from_non_successivo_al_report(tmp_path):
    _base(tmp_path)
    _cfg(tmp_path, dal="2026-11-16")
    _adr(tmp_path, "ADR-002", status="accepted", created="2026-11-20")
    out = _run(tmp_path)
    assert out["findings"] == [] and "successivo" in out["diagnostica"][0]


def test_storico_esente_e_ok(tmp_path):
    _base(tmp_path)
    _adr(tmp_path, "ADR-002", status="accepted", created="2026-11-20", satisfies="[US-001]")
    _art(tmp_path, "TSK-001", CHIUSURA_OK, status="done", story="US-001", created="2026-11-20",
         decision_refs="[ADR-002]")
    _art(tmp_path, "TSK-000", CHIUSURA_KO, status="done", story="US-001", created="2026-10-01")
    out = _run(tmp_path)
    assert out["findings"] == [], out["findings"]
    assert out["stats"]["adr_nel_perimetro"] == 1 and out["stats"]["tsk_nel_perimetro"] == 1


def test_difetti_rilevati(tmp_path):
    _base(tmp_path)
    _cfg(tmp_path, soglia="5")  # 5 finding su 4 artefatti: senza soglia alta il check si sospenderebbe
    _adr(tmp_path, "ADR-002", status="accepted", created="2026-11-20")                      # senza satisfies
    _adr(tmp_path, "ADR-003", status="accepted", created="2026-11-20", satisfies="[US-999]",
         supersedes="ADR-404 §A")                                                          # 2 ref ignoti
    _art(tmp_path, "TSK-001", CHIUSURA_KO, status="done", story="US-001", created="2026-11-20",
         decision_refs="[ADR-777]")                                                        # ref ignoto + no AC
    _art(tmp_path, "TSK-002", "", status="todo", story="US-001", created="2026-11-20")      # aperto: nulla
    out = _run(tmp_path)
    assert _codici(out) == ["adr-senza-satisfies", "chiusura-senza-ac", "unknown-ref", "unknown-ref", "unknown-ref"]
    assert all(f["sev"] == "WARNING" for f in out["findings"])


def test_supersedes_parziale_risolve_l_id(tmp_path):
    _base(tmp_path)
    _adr(tmp_path, "ADR-002", status="accepted", created="2026-11-20", satisfies="[US-001]",
         supersedes="ADR-001 §A")
    assert _run(tmp_path)["findings"] == []


def test_sospeso_oltre_soglia(tmp_path):
    _base(tmp_path)
    _cfg(tmp_path, soglia="0.10")
    _adr(tmp_path, "ADR-002", status="accepted", created="2026-11-20")
    out = _run(tmp_path)
    assert out["findings"] == [] and out["stats"]["sospeso"] is True
    assert "SOSPESO" in out["diagnostica"][0]


def test_info_dismissione_decision_refs(tmp_path):
    _base(tmp_path)
    _art(tmp_path, "TSK-001", CHIUSURA_OK, status="done", story="US-001", created="2026-11-20")
    out = _run(tmp_path, "--oggi", "2026-12-20")
    assert _codici(out) == ["decision-refs-vuoto"] and out["findings"][0]["sev"] == "INFO"
    assert _run(tmp_path, "--oggi", "2026-11-30")["findings"] == []


def test_forza_misura_a_flag_spento(tmp_path):
    _base(tmp_path)
    _cfg(tmp_path, enabled="false", dal="")
    _adr(tmp_path, "ADR-002", status="accepted", created="2026-11-20")
    assert "adr-senza-satisfies" in _codici(_run(tmp_path, "--forza", "--dal", "2026-11-01"))


def test_runner_registra_4bi():
    testo = (LINT / "run-deterministic.py").read_text(encoding="utf-8")
    assert "check_tracciabilita_design.py" in testo and "('4bi',)" in testo


PM_OK = "{data: 2026-11-20, report: wiki/pm.md, esito: modificato}"


def test_premortem_acceso_segnala_adr_senza(tmp_path):
    _base(tmp_path)
    _cfg(tmp_path, soglia="5", premortem="true")
    _adr(tmp_path, "ADR-002", status="accepted", created="2026-11-20", satisfies="[US-001]")
    out = _run(tmp_path)
    assert _codici(out) == ["adr-senza-premortem"] and out["findings"][0]["sev"] == "WARNING"


def test_premortem_spento_nessun_effetto(tmp_path):
    _base(tmp_path)
    _adr(tmp_path, "ADR-002", status="accepted", created="2026-11-20", satisfies="[US-001]")
    assert _run(tmp_path)["findings"] == []


def test_premortem_valido_non_segnala(tmp_path):
    _base(tmp_path)
    _cfg(tmp_path, soglia="5", premortem="true")
    _adr(tmp_path, "ADR-002", status="accepted", created="2026-11-20", satisfies="[US-001]", premortem=PM_OK)
    assert _run(tmp_path)["findings"] == []
    _adr(tmp_path, "ADR-003", status="accepted", created="2026-11-20", satisfies="[US-001]",
         premortem="{data: 2026-11-20, report: wiki/pm.md, esito: boh}")  # esito non ammesso
    assert _codici(_run(tmp_path)) == ["adr-senza-premortem"]

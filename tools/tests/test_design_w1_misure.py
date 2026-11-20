"""Misure W1 del layer analisi-design (tools/analytics/design_w1_misure.py), EP-097 US-383.

Repo git minimo in tmp_path: un ADR nato accepted e poi riscritto, uno nato proposed e rivisto
prima dell'OK, una pagina wiki con `updated:` indietro rispetto al commit.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "analytics" / "design_w1_misure.py"


def _git(root, *args, data="2026-11-01T10:00:00"):
    env = dict(os.environ, GIT_AUTHOR_DATE=data, GIT_COMMITTER_DATE=data,
               GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, env=env)


def _adr(root, nome, status, decisione):
    d = root / "design_&_architecture" / "decisions"
    d.mkdir(parents=True, exist_ok=True)
    (d / nome).write_text(f"---\nid: {nome[:-3]}\nstatus: {status}\n---\n\n## Decisione\n\n{decisione}\n\n## Conseguenze\n\nx\n", encoding="utf-8")


def test_misure(tmp_path):
    _git(tmp_path, "init", "-q")
    _adr(tmp_path, "ADR-001.md", "accepted", "usa A")
    _adr(tmp_path, "ADR-002.md", "proposed", "usa B")
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki" / "p.md").write_text("---\nupdated: 2026-10-01\n---\n\nx\n", encoding="utf-8")
    _git(tmp_path, "add", "-A"); _git(tmp_path, "commit", "-qm", "1")
    _adr(tmp_path, "ADR-001.md", "accepted", "usa A2")          # Decisione cambiata dopo accepted
    _adr(tmp_path, "ADR-002.md", "accepted", "usa B rivista")   # rivista prima dell'OK
    _git(tmp_path, "add", "-A"); _git(tmp_path, "commit", "-qm", "2", data="2026-11-02T10:00:00")
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(tmp_path), "--json"],
                       capture_output=True, text=True, check=True, encoding="utf-8", errors="replace")
    s = json.loads(r.stdout)["sintesi"]
    assert s["n_adr"] == 2 and s["n_adr_nati_accepted"] == 1
    assert s["ok_chat_rate"] == 0.0 and s["adr_decisione_cambiata"] == ["ADR-001"]
    assert s["n_rivisti_prima_di_accepted"] == 1
    assert s["n_pagine_updated"] == 1 and s["quota_updated_scarto_gt7"] == 1.0


def test_report_ha_il_frontmatter_letto_dal_4bi(tmp_path):
    _git(tmp_path, "init", "-q")
    _adr(tmp_path, "ADR-001.md", "accepted", "usa A")
    _git(tmp_path, "add", "-A"); _git(tmp_path, "commit", "-qm", "1")
    out = tmp_path / "wiki" / "lint" / "2026-11-16-w1-design.md"
    subprocess.run([sys.executable, str(SCRIPT), "--root", str(tmp_path), "--out", str(out), "--oggi", "2026-11-16"],
                   capture_output=True, text=True, check=True, encoding="utf-8", errors="replace")
    fm = out.read_text(encoding="utf-8").split("---")[1]
    for campo in ("date: 2026-11-16", "n: 1", "ok_chat_rate: 1.0"):
        assert campo in fm


def test_misure_premortem(tmp_path):
    _git(tmp_path, "init", "-q")
    _adr(tmp_path, "ADR-001.md", "accepted", "usa A")
    _adr(tmp_path, "ADR-002.md", "accepted", "usa B")
    _adr(tmp_path, "ADR-003.md", "accepted", "usa C")
    d = tmp_path / "design_&_architecture" / "decisions"
    for nome, esito in (("ADR-002", "invariato"), ("ADR-003", "modificato")):
        t = (d / f"{nome}.md").read_text(encoding="utf-8").replace(
            "status: accepted\n", f"status: accepted\npremortem: {{data: 2026-11-20, report: wiki/pm.md, esito: {esito}}}\n")
        (d / f"{nome}.md").write_text(t, encoding="utf-8")
    _git(tmp_path, "add", "-A"); _git(tmp_path, "commit", "-qm", "1")
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(tmp_path), "--json"],
                       capture_output=True, text=True, check=True, encoding="utf-8", errors="replace")
    s = json.loads(r.stdout)["sintesi"]
    assert s["n_con_premortem"] == 2 and s["quota_con_premortem"] == 0.667
    assert s["n_premortem_decisione_cambiata"] == 1
    out = tmp_path / "w1.md"
    subprocess.run([sys.executable, str(SCRIPT), "--root", str(tmp_path), "--out", str(out)],
                   capture_output=True, text=True, check=True, encoding="utf-8", errors="replace")
    assert "quota_con_premortem: 0.667" in out.read_text(encoding="utf-8").split("---")[1]

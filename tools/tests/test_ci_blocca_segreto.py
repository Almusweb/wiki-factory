"""EP-108 TSK-1025: un FAIL di gitleaks a severita' ERROR fa uscire 1 il runner della CI.

Riproduce F1 dell'analisi del 2026-11-18: con `required_from: null` un finding usciva WARNING e
`run-deterministic.py --strict` restava a exit 0, cioe' la CI verde con un segreto committato.
Qui il runner gira su un repo temporaneo, con un gitleaks finto nel PATH che riconosce un marcatore.
Non dipende dal binario vero: quello lo prova la CI, che installa gitleaks a versione fissata.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RADICE = Path(__file__).resolve().parents[2]
RUNNER = RADICE / "tools" / "lint" / "run-deterministic.py"
MARCATORE = "FAKE-SECRET-MARKER-CI"

FINTO = """#!/usr/bin/env python3
import sys, os, json
a = sys.argv[1:]
if a[:2] == ["dir", "--help"]:
    sys.exit(0)
rep = a[a.index("--report-path") + 1]
radice = a[-1] if a[0] == "dir" else "."
found = []
for d, _, fs in os.walk(radice):
    for f in fs:
        p = os.path.join(d, f)
        if "@@M@@" in open(p, errors="replace").read():
            found.append({"File": os.path.relpath(p, radice), "StartLine": 1, "RuleID": "fake"})
json.dump(found, open(rep, "w"))
sys.exit(1 if found else 0)
""".replace("@@M@@", MARCATORE)


def _repo(tmp_path, required_from):
    r = tmp_path / "repo"
    r.mkdir()
    (r / "factory.config.yaml").write_text(
        "secrets_guard:\n  enabled: true\n  required_from: %s\n" % required_from, encoding="utf-8")
    (r / "segreto.txt").write_text("token " + MARCATORE + "\n", encoding="utf-8")
    for c in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"],
              ["add", "-A"], ["commit", "-qm", "base"]):
        subprocess.run(["git", "-C", str(r)] + c, check=True, capture_output=True)
    return r


def _bin(tmp_path, con_gitleaks):
    b = tmp_path / "bin"
    b.mkdir()
    os.symlink(shutil.which("git"), str(b / "git"))
    os.symlink(sys.executable, str(b / "python3"))  # per lo shebang del gitleaks finto
    if con_gitleaks:
        g = b / "gitleaks"
        g.write_text(FINTO, encoding="utf-8")
        g.chmod(0o755)
    return str(b)


def _ci(repo, path_bin):
    env = dict(os.environ, PATH=path_bin)
    return subprocess.run([sys.executable, str(RUNNER), "--root", str(repo), "--strict", "--solo", "4bj"],
                          capture_output=True, text=True, env=env, encoding="utf-8", errors="replace")


def test_fail_a_error_fa_uscire_1_il_runner_strict(tmp_path):
    """US-418 AC3: con required_from passata, un segreto fa fallire la CI."""
    r = _ci(_repo(tmp_path, "2020-01-01"), _bin(tmp_path, True))
    assert r.returncode == 1, r.stdout + r.stderr
    assert "[ERROR][secrets][4bj] segreto.txt:1" in r.stdout


def test_fail_a_warn_non_blocca_e_lo_dice(tmp_path):
    """Con required_from futura il finding resta WARNING: exit 0, segnalato."""
    r = _ci(_repo(tmp_path, "2999-01-01"), _bin(tmp_path, True))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "[WARNING][secrets][4bj] segreto.txt:1" in r.stdout and "NON_VERIFICABILE" not in r.stdout


@pytest.mark.parametrize("required_from", ["2020-01-01", "null"])
def test_senza_gitleaks_e_warning_non_verificabile(tmp_path, required_from, monkeypatch):
    """US-418 AC4: NON_VERIFICABILE resta WARNING (manca la verifica, non c'e' un segreto)."""
    r = _ci(_repo(tmp_path, required_from), _bin(tmp_path, False))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "NON_VERIFICABILE" in r.stdout and "[WARNING][secrets][4bj]" in r.stdout

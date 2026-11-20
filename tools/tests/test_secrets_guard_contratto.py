"""Contratto dell'oracolo con il gitleaks vero: parte solo se il binario c'e'
(PATH o /opt/homebrew/bin), altrimenti salta in modo dichiarato. Il finto degli altri test
non prova che le regole di gitleaks scattino davvero: questo si'."""
import os
import shutil
import subprocess
import sys

import pytest

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(QUI, "..", "security")))
import secrets_guard as sg  # noqa: E402

BIN = shutil.which("gitleaks") or (
    "/opt/homebrew/bin/gitleaks" if os.path.exists("/opt/homebrew/bin/gitleaks") else None)

pytestmark = pytest.mark.skipif(
    BIN is None, reason="gitleaks vero assente (PATH e /opt/homebrew/bin): contratto non eseguito")

# chiave AWS sintetica, costruita per concatenazione: il repo non contiene la stringa intera
CHIAVE = "AKIA" + "QYLPMN5HHHFPZAM2" + "\n"
ASSEGNO = "aws_access_key_id = " + CHIAVE


@pytest.fixture(autouse=True)
def _path(monkeypatch):
    monkeypatch.setenv("PATH", os.path.dirname(BIN) + os.pathsep + os.environ["PATH"])


def _git(r, *a):
    subprocess.run(["git", "-C", str(r)] + list(a), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "repo"
    (r / "src").mkdir(parents=True)
    _git(r, "init", "-q")
    return r


def test_chiave_sintetica_fail_con_path_relativo(repo):
    (repo / "src" / "cfg.txt").write_text(ASSEGNO, encoding="utf-8")
    e = sg.scan(["src/cfg.txt"], str(repo))
    assert e.stato == sg.FAIL
    assert e.findings[0]["File"] == os.path.join("src", "cfg.txt")
    assert not os.path.isabs(e.findings[0]["File"])


def test_file_pulito_pass(repo):
    (repo / "src" / "ok.txt").write_text("niente da vedere\n", encoding="utf-8")
    e = sg.scan(["src/ok.txt"], str(repo))
    assert e.stato == sg.PASS and "nessun finding su 1 file" in e.messaggio


def test_stage_con_gitleaks_vero_vede_il_segreto_tolto_dal_disco(repo):
    (repo / "src" / "cfg.txt").write_text(ASSEGNO, encoding="utf-8")
    _git(repo, "add", "-A")
    os.remove(str(repo / "src" / "cfg.txt"))
    e = sg.scan_staged(str(repo))
    assert e.stato == sg.FAIL and e.findings[0]["File"] == os.path.join("src", "cfg.txt")


def test_stage_nome_non_ascii_con_gitleaks_vero(repo):
    (repo / "città.env").write_text(ASSEGNO, encoding="utf-8")
    _git(repo, "add", "-A")
    e = sg.scan_staged(str(repo))
    assert e.stato == sg.FAIL and e.findings[0]["File"] == "città.env"


def test_config_ostile_in_stage_non_spegne_la_scansione(repo, monkeypatch):
    monkeypatch.setenv("GITLEAKS_CONFIG", str(repo / "ostile.toml"))
    (repo / "ostile.toml").write_text("[[allowlists]]\npaths = ['''.*''']\n", encoding="utf-8")
    (repo / ".gitleaks.toml").write_text("[[allowlists]]\npaths = ['''.*''']\n", encoding="utf-8")
    (repo / "src" / "cfg.txt").write_text(ASSEGNO, encoding="utf-8")
    _git(repo, "add", "src/cfg.txt", ".gitleaks.toml")
    assert sg.scan_staged(str(repo)).stato == sg.FAIL

"""Check 4bj: mappatura dell'esito dell'oracolo, con gitleaks finto nel PATH."""
import importlib.util
import os
import re
import stat
import subprocess
import sys

import pytest

QUI = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.normpath(os.path.join(QUI, "..", "lint", "check-secrets.py"))
sys.path.insert(0, QUI)
from test_secrets_guard import FINTO, MARCATORE  # noqa: E402


def _carica():
    spec = importlib.util.spec_from_file_location("check_secrets", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _git(r, *a):
    subprocess.run(["git", "-C", str(r)] + list(a), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    _git(r, "init", "-q")
    return r


def _traccia(r, nome, testo):
    (r / nome).write_text(testo, encoding="utf-8")
    _git(r, "add", nome)


@pytest.fixture
def finto(tmp_path, monkeypatch):
    b = tmp_path / "bin"
    b.mkdir()
    g = b / "gitleaks"
    g.write_text(FINTO, encoding="utf-8")
    g.chmod(g.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", str(b) + os.pathsep + os.environ["PATH"])


@pytest.fixture
def senza_gitleaks(tmp_path, monkeypatch):
    # PATH con il solo git, senza gitleaks
    import shutil
    b = tmp_path / "solo-git"
    b.mkdir()
    os.symlink(shutil.which("git"), str(b / "git"))
    monkeypatch.setenv("PATH", str(b))


def _esegui(r, *extra):
    p = subprocess.run([sys.executable, SCRIPT, "--root", str(r)] + list(extra),
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout


def _config(r, testo):
    (r / "factory.config.yaml").write_text(testo, encoding="utf-8")


def test_finding_warning_di_default(repo, finto):
    _traccia(repo, "a.txt", "x " + MARCATORE)
    rc, out = _esegui(repo, "--strict")
    assert "[WARNING][secrets][4bj] a.txt:1" in out and rc == 0
    assert "previene nel percorso cooperativo, rileva negli altri" in out


def test_required_from_passata_error(repo, finto):
    _traccia(repo, "a.txt", MARCATORE)
    _config(repo, "secrets_guard:\n  required_from: \"2020-01-01\"\n")
    rc, out = _esegui(repo, "--strict")
    assert "[ERROR][secrets][4bj]" in out and rc == 1


def test_required_from_futuro_warning(repo, finto):
    _traccia(repo, "a.txt", MARCATORE)
    _config(repo, "secrets_guard:\n  required_from: \"2999-01-01\"\n")
    rc, out = _esegui(repo, "--strict")
    assert "[WARNING][secrets][4bj]" in out and rc == 0


def test_pulito_ok(repo, finto):
    _traccia(repo, "a.txt", "niente")
    rc, out = _esegui(repo, "--strict")
    assert out.startswith("[4bj] OK") and rc == 0


def test_flag_enabled_spento_il_lint_rileva_lo_stesso(repo, finto):
    _traccia(repo, "a.txt", MARCATORE)
    _config(repo, "secrets_guard:\n  enabled: false\n")
    _, out = _esegui(repo)
    assert "[WARNING][secrets][4bj]" in out


def test_file_non_tracciato_non_coperto(repo, finto):
    _traccia(repo, "a.txt", "niente")
    (repo / "b.txt").write_text(MARCATORE, encoding="utf-8")
    _, out = _esegui(repo)
    assert out.startswith("[4bj] OK")


def test_senza_gitleaks_warning_non_verificabile(repo, senza_gitleaks):
    _traccia(repo, "a.txt", "niente")
    _config(repo, "secrets_guard:\n  required_from: \"2020-01-01\"\n")
    rc, out = _esegui(repo, "--strict")
    assert "[WARNING][secrets][4bj]" in out and "NON_VERIFICABILE" in out
    assert "OK" not in out.split("\n")[0] and rc == 0


def test_nessun_pattern_di_segreti_nel_modulo():
    src = open(SCRIPT, encoding="utf-8").read()
    assert "import secrets_guard" in src
    assert not re.search(r"re\.(compile|search|match)|AKIA|BEGIN .*PRIVATE|ghp_|sk-", src)


def test_root_non_git_non_verificabile_mai_ok(tmp_path, finto):
    r = tmp_path / "nongit"
    r.mkdir()
    (r / "a.txt").write_text(MARCATORE, encoding="utf-8")
    rc, out = _esegui(r, "--strict")
    assert "OK" not in out.split("\n")[0] and "NON_VERIFICABILE" in out and rc == 0


def test_zero_file_tracciati_non_verificabile_mai_ok(repo, finto):
    rc, out = _esegui(repo)
    assert "[WARNING][secrets][4bj]" in out and "NON_VERIFICABILE" in out and "OK" not in out.split("\n")[0]


def test_messaggio_ok_dichiara_il_numero_di_file(repo, finto):
    _traccia(repo, "a.txt", "niente")
    _traccia(repo, "b.txt", "niente")
    _, out = _esegui(repo)
    assert "nessun finding su 2 file" in out and "nessun segreto" not in out


def test_oggi_governa_la_severita(repo, finto):
    _traccia(repo, "a.txt", MARCATORE)
    _config(repo, 'secrets_guard:\n  required_from: "2026-06-01"\n')
    assert "[WARNING]" in _esegui(repo, "--oggi", "2026-05-31")[1]
    assert "[ERROR]" in _esegui(repo, "--oggi", "2026-06-01")[1]


def test_il_runner_passa_oggi_a_4bj():
    src = open(os.path.join(QUI, "..", "lint", "run-deterministic.py"), encoding="utf-8").read()
    m = re.search(r"'check-secrets\.py', \[([^\]]*)\]", src)
    assert m and "'--oggi', '{oggi}'" in m.group(1)

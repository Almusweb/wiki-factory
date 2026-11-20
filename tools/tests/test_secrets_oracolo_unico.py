"""Un solo oracolo dei segreti: hook di pre-commit, check 4bj e runner del lint lo invocano
tutti, nessun altro file definisce pattern o chiama gitleaks, e la dichiarazione di limite compare
dove deve."""
import os
import re
import shutil
import stat
import subprocess
import sys

import pytest

QUI = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.normpath(os.path.join(QUI, ".."))
RADICE = os.path.normpath(os.path.join(TOOLS, ".."))
sys.path.insert(0, os.path.join(TOOLS, "security"))
sys.path.insert(0, os.path.join(TOOLS, "vcs"))
sys.path.insert(0, QUI)
import secrets_guard as sg  # noqa: E402
import install_factory_hooks as ifh  # noqa: E402
from test_secrets_guard import FINTO, MARCATORE  # noqa: E402

DICHIARAZIONE = "previene nel percorso cooperativo, rileva negli altri"

# il gitleaks finto registra ogni invocazione in $FAKE_LOG
FINTO_CON_TRACCIA = FINTO


def _run(cwd, *a, **kw):
    return subprocess.run(list(a), cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          universal_newlines=True, encoding="utf-8", errors="replace", **kw)


@pytest.fixture
def ambiente(tmp_path, monkeypatch):
    b = tmp_path / "bin"
    b.mkdir()
    g = b / "gitleaks"
    g.write_text(FINTO_CON_TRACCIA, encoding="utf-8")
    g.chmod(g.stat().st_mode | stat.S_IEXEC)
    log = tmp_path / "gitleaks.log"
    monkeypatch.setenv("PATH", str(b) + os.pathsep + os.environ["PATH"])
    monkeypatch.setenv("FAKE_LOG", str(log))
    return log


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "repo"
    (r / "tools" / "security").mkdir(parents=True)
    for m in ("secrets_guard.py", "config_ancorata.py"):
        shutil.copy(os.path.join(TOOLS, "security", m), str(r / "tools" / "security"))
    (r / "factory.config.yaml").write_text("secrets_guard:\n  enabled: true\n  required_from: \"2020-01-01\"\n", encoding="utf-8")
    for c in (("init", "-q"), ("config", "user.email", "t@t"), ("config", "user.name", "t")):
        _run(r, "git", *c)
    return r


def _invocazioni(log):
    return log.read_text(encoding="utf-8").count("invocato") if log.exists() else 0


def test_hook_generato_invoca_l_oracolo_e_blocca(repo, ambiente):
    ifh._install("pre-commit", ifh.PRE_COMMIT_HOOK, repo / ".git" / "hooks", False, False)
    (repo / "a.txt").write_text("x " + MARCATORE, encoding="utf-8")
    _run(repo, "git", "add", "a.txt")
    r = _run(repo, "git", "commit", "-qm", "x")
    assert _invocazioni(ambiente) == 1
    assert r.returncode != 0
    assert DICHIARAZIONE in r.stdout


def test_hook_generato_commit_pulito_passa_dall_oracolo(repo, ambiente):
    ifh._install("pre-commit", ifh.PRE_COMMIT_HOOK, repo / ".git" / "hooks", False, False)
    (repo / "a.txt").write_text("niente", encoding="utf-8")
    _run(repo, "git", "add", "a.txt")
    r = _run(repo, "git", "commit", "-qm", "x")
    assert _invocazioni(ambiente) == 1 and r.returncode == 0


def _traccia_file(repo, contenuto):
    (repo / "a.txt").write_text(contenuto, encoding="utf-8")
    _run(repo, "git", "add", "a.txt")


def test_check_4bj_invoca_l_oracolo(repo, ambiente):
    _traccia_file(repo, "x " + MARCATORE)
    r = _run(repo, sys.executable, os.path.join(TOOLS, "lint", "check-secrets.py"), "--root", str(repo))
    assert _invocazioni(ambiente) == 1
    assert "[ERROR][secrets][4bj] a.txt:1" in r.stdout
    assert DICHIARAZIONE in r.stdout


def test_check_4bj_pulito_dichiara_il_limite(repo, ambiente):
    _traccia_file(repo, "niente")
    r = _run(repo, sys.executable, os.path.join(TOOLS, "lint", "check-secrets.py"), "--root", str(repo))
    assert _invocazioni(ambiente) == 1
    assert r.stdout.startswith("[4bj] OK") and DICHIARAZIONE in r.stdout


def test_ci_via_run_deterministic_solo_4bj_invoca_l_oracolo(repo, ambiente):
    _traccia_file(repo, "x " + MARCATORE)
    r = _run(repo, sys.executable, os.path.join(TOOLS, "lint", "run-deterministic.py"),
             "--root", str(repo), "--solo", "4bj")
    assert _invocazioni(ambiente) == 1
    assert "[secrets][4bj] a.txt:1" in r.stdout


def test_ci_esegue_4bj_con_solo():
    ci = open(os.path.join(RADICE, ".github", "workflows", "ci.yml"), encoding="utf-8").read()
    m = re.search(r"run-deterministic\.py[^\n]*--solo\s+(\S+)", ci)
    assert m and "4bj" in m.group(1).split(",")


def test_i_punti_d_ingresso_non_ridefiniscono_l_oracolo():
    """Check 4bj importa scan/severita dall'oracolo; l'hook lo lancia come script."""
    src = open(os.path.join(TOOLS, "lint", "check-secrets.py"), encoding="utf-8").read()
    assert "import secrets_guard as sg" in src and "sg.scan(" in src
    assert "tools/security/secrets_guard.py" in ifh.PRE_COMMIT_HOOK and "--hook" in ifh.PRE_COMMIT_HOOK \
        and "--staged" in ifh.PRE_COMMIT_HOOK
    # il modulo importato dal check e' lo stesso file dell'oracolo
    assert os.path.samefile(sg.__file__, os.path.join(TOOLS, "security", "secrets_guard.py"))


def _file_del_framework():
    """File di codice/test/config fuori da wiki/, management/, .git e tools/security/."""
    out = subprocess.run(["git", "ls-files", "-z"], cwd=RADICE, stdout=subprocess.PIPE).stdout
    for p in out.decode("utf-8", "replace").split("\0"):
        if not p or p.startswith(("wiki/", "management/", "tools/security/")):
            continue
        if p.endswith((".py", ".sh", ".yml", ".yaml", ".md")) and os.path.isfile(os.path.join(RADICE, p)):
            yield p


def test_nessun_pattern_di_segreti_nei_punti_d_ingresso():
    """I tre punti d'ingresso non contengono regex di segreti (le redazioni di altri strumenti,
    come il mascheramento dei log, hanno un altro scopo e restano fuori)."""
    firme = re.compile(r"AKIA[0-9A-Z]{8}|BEGIN [A-Z ]*PRIVATE KEY|ghp_|xox[baprs]|AIza[0-9A-Za-z]|sk-[A-Za-z0-9]{6}")
    for p in ("tools/lint/check-secrets.py", "tools/lint/run-deterministic.py",
              "tools/vcs/install_factory_hooks.py", ".github/workflows/ci.yml"):
        assert not firme.search(_leggi(p)), p


def test_nessuna_invocazione_diretta_di_gitleaks_fuori_dall_oracolo():
    diretta = re.compile(r"""(subprocess|os\.system|Popen|check_output)[^\n]*gitleaks|^\s*gitleaks\s+(detect|dir|git)\b""",
                         re.M)
    trovati = []
    for p in _file_del_framework():
        if p.endswith(".md") or p.startswith("tools/tests/"):
            continue
        if diretta.search(open(os.path.join(RADICE, p), encoding="utf-8", errors="replace").read()):
            trovati.append(p)
    assert trovati == []


def _leggi(rel):
    return open(os.path.join(RADICE, rel), encoding="utf-8").read()


def test_dichiarazione_in_hook_check_e_documentazione():
    assert DICHIARAZIONE in ifh.PRE_COMMIT_HOOK.lower()
    assert DICHIARAZIONE in _leggi("tools/lint/check-secrets.py").lower()
    assert DICHIARAZIONE in _leggi(".claude/skills/lint-checks-kanban.md").lower()
    assert DICHIARAZIONE in _leggi("CAPABILITIES.md").lower()


def test_nessun_testo_dice_sec_010_coperto():
    # La regex e' scritta per concatenazione: una volta tracciato, questo file non deve
    # trovare se stesso (prima del commit `git ls-files` non lo elencava e il test passava).
    sec = "SEC" + "-010"
    vietato = re.compile(sec + r"[^\n]{0,60}copert|copert[^\n]{0,60}" + sec, re.I)
    for p in _file_del_framework():
        assert not vietato.search(_leggi(p)), p


def test_nessun_sec_o_g0_g5_nel_codice_e_nei_test_della_guardia():
    comp = ["tools/security/secrets_guard.py", "tools/lint/check-secrets.py", "tools/vcs/install_factory_hooks.py",
            "tools/tests/test_secrets_guard.py", "tools/tests/test_check_secrets.py",
            "tools/tests/test_install_factory_hooks_precommit.py", "tools/tests/test_secrets_oracolo_unico.py"]
    vietato = re.compile(r"\bSEC-\d+|\bSEC-\*|\bG[0-5]\b")
    for p in comp:
        testo = _leggi(p)
        if p.endswith("test_secrets_oracolo_unico.py"):
            testo = testo.replace('r"\\bSEC-\\d+|\\bSEC-\\*|\\bG[0-5]\\b"', "").replace("SEC-010", "")
        assert not vietato.search(re.sub(r"SEC-010", "", testo) if p.endswith("unico.py") else testo), p

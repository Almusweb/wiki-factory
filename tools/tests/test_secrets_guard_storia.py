"""Modalita' storia della guardia dei segreti (EP-109 US-426, TSK-1040).

Layout: una factory finta (repo git) che dichiara in code_paths[] un repo cliente annidato (altro repo
git, come un submodule). Il segreto sintetico si genera a runtime: un literal nel sorgente farebbe
scattare la guardia stessa e gli scanner esterni."""
from __future__ import annotations

import json
import os
import random
import shutil
import stat
import string
import subprocess
import sys

import pytest

QUI = os.path.dirname(os.path.abspath(__file__))
MODULO = os.path.normpath(os.path.join(QUI, "..", "security", "secrets_guard.py"))
sys.path.insert(0, os.path.dirname(MODULO))
import scanner_identity as si  # noqa: E402
import secrets_guard as sg  # noqa: E402

GITLEAKS_REALE = shutil.which("gitleaks") or (
    "/opt/homebrew/bin/gitleaks" if os.path.isfile("/opt/homebrew/bin/gitleaks") else None)


def _git(repo, *a):
    r = subprocess.run(["git", "-C", str(repo)] + list(a), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert r.returncode == 0, r.stderr
    return r.stdout.decode().strip()


def _init(repo):
    repo.mkdir(parents=True, exist_ok=True)
    for c in (("init", "-q"), ("config", "user.email", "t@t"), ("config", "user.name", "t"),
              ("config", "commit.gpgsign", "false")):
        _git(repo, *c)


def _commit(repo, msg):
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "--allow-empty", "-m", msg, "--no-verify")
    return _git(repo, "rev-parse", "HEAD")


def segreto_sintetico():
    rnd = random.Random(1044)
    return "ghp_" + "".join(rnd.choice(string.ascii_letters + string.digits) for _ in range(36))


@pytest.fixture
def factory(tmp_path):
    f = tmp_path / "factory"
    _init(f)
    (f / "factory.config.yaml").write_text(
        "code_paths:\n"
        "  - name: cliente\n    path: code_repos/cliente/\n    vcs:\n      mode: submodule\n"
        "  - name: interno\n    path: apps/interno/\n    vcs:\n      mode: monorepo\n"
        "secrets_guard:\n  enabled: true\n")
    (f / "apps" / "interno").mkdir(parents=True)
    (f / "apps" / "interno" / "x.txt").write_text("x\n")
    _commit(f, "factory")
    _git(f, "update-ref", "refs/remotes/origin/main", "HEAD")
    cliente = f / "code_repos" / "cliente"
    _init(cliente)
    (cliente / "README.md").write_text("cliente\n")
    _commit(cliente, "init")
    return f


def pinna_gitleaks(factory, exe):
    """Pin di `exe` sull'ancora della factory finta (D7: la modalita' storia usa scanner_identity)."""
    _, sha, _, err = si.misura("gitleaks", str(exe))
    assert err is None, err
    (factory / "security").mkdir(exist_ok=True)
    (factory / "security" / "scanner-pins.json").write_text(json.dumps({"gitleaks": [{"path": str(exe), "sha256": sha}]}))
    _git(factory, "add", "security")
    _git(factory, "commit", "-q", "-m", "pin gitleaks", "--no-verify")
    _git(factory, "update-ref", "refs/remotes/origin/main", "HEAD")


def con_segreto_rimosso(cliente):
    """Committa un file col segreto e poi lo rimuove: il segreto resta solo nella storia."""
    s = segreto_sintetico()
    (cliente / "config.py").write_text("TOKEN = '%s'\n" % s)
    sha = _commit(cliente, "aggiunge config")
    (cliente / "config.py").write_text("TOKEN = os.environ['TOKEN']\n")
    _commit(cliente, "toglie il segreto")
    return s, sha


# --- AC2: perimetro ---------------------------------------------------------------------------

def test_root_della_factory_rifiutata(factory):
    motivo = sg.guardia_storia(str(factory), str(factory))
    assert motivo and "repo della factory" in motivo


def test_code_path_monorepo_dentro_la_factory_rifiutato_anche_se_dichiarato(factory):
    motivo = sg.guardia_storia(str(factory / "apps" / "interno"), str(factory))
    assert motivo and "repo della factory" in motivo


def test_factory_che_contiene_lo_script_rifiutata(factory):
    motivo = sg.guardia_storia(str(sg.RADICE_FACTORY), str(factory))
    assert motivo and "repo della factory" in motivo


def test_path_non_dichiarato_rifiutato(factory, tmp_path):
    altro = tmp_path / "altro"
    _init(altro)
    motivo = sg.guardia_storia(str(altro), str(factory))
    assert motivo and "non e' dichiarato" in motivo


def test_git_che_non_risponde_rifiuta_per_sicurezza(factory, monkeypatch):
    def rotto(_p):
        raise sg._ToplevelNonVerificabile("timeout")
    monkeypatch.setattr(sg, "_toplevel", rotto)
    motivo = sg.guardia_storia(str(factory / "code_repos" / "cliente"), str(factory))
    assert motivo and "rifiutato per sicurezza" in motivo


def test_code_path_dichiarato_ammesso(factory):
    assert sg.guardia_storia(str(factory / "code_repos" / "cliente"), str(factory)) is None


def test_cli_rifiuto_esplicito_exit_2(factory):
    r = subprocess.run([sys.executable, MODULO, "--root", str(factory), "--storia", str(factory)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert r.returncode == 2 and b"RIFIUTATO" in r.stdout


# --- AC1: un solo oracolo, nessun pattern proprio ---------------------------------------------

def test_nessuna_regex_di_segreti_nuova():
    with open(MODULO, encoding="utf-8") as fh:
        sorgente = fh.read()
    for indizio in ("ghp_", "AKIA", "BEGIN RSA", "xox[", "sk_live"):
        assert indizio not in sorgente, indizio
    assert sg.CONFIG_SOLO_DEFAULT.strip().splitlines() == ["[extend]", "useDefault = true"]


# --- AC3: scansione con gitleaks finto --------------------------------------------------------

FINTO_GIT = r"""#!/usr/bin/env python3
import json, os, sys
a = sys.argv[1:]
if a[:2] == ["git", "--help"]:
    sys.exit(0)
if os.environ.get("FAKE_ARGV"):
    open(os.environ["FAKE_ARGV"], "w").write(json.dumps(a))
rep = a[a.index("--report-path") + 1]
f = {"Commit": "abc123def4567890", "File": "config.py", "StartLine": 1, "RuleID": "github-pat",
     "Secret": "REDACTED", "Match": "TOKEN = 'REDACTED'", "Fingerprint": "abc:config.py:github-pat:1"}
json.dump([f] if os.environ.get("FAKE_TROVA") else [], open(rep, "w"))
sys.exit(1 if os.environ.get("FAKE_TROVA") else 0)
"""


@pytest.fixture
def finto(tmp_path, monkeypatch, factory):
    b = tmp_path / "bin"
    b.mkdir()
    g = b / "gitleaks"
    g.write_text(FINTO_GIT)
    g.chmod(g.stat().st_mode | stat.S_IEXEC)
    argv = tmp_path / "argv.json"
    monkeypatch.setenv("PATH", str(b) + os.pathsep + os.environ.get("PATH", ""))
    monkeypatch.setenv("FAKE_ARGV", str(argv))
    pinna_gitleaks(factory, g)
    return argv


def test_finto_invocazione_git_redact_e_config_solo_default(factory, finto, monkeypatch):
    monkeypatch.setenv("FAKE_TROVA", "1")
    e = sg.scan_storia(str(factory / "code_repos" / "cliente"), str(factory))
    argv = json.loads(finto.read_text())
    assert argv[0] == "git" and "--redact" in argv and "--config" in argv
    assert e.stato == sg.FAIL
    assert e.findings == [{"Commit": "abc123def4567890", "File": "config.py", "StartLine": 1, "RuleID": "github-pat"}]


def test_finto_nessun_finding_pass(factory, finto):
    e = sg.scan_storia(str(factory / "code_repos" / "cliente"), str(factory))
    assert e.stato == sg.PASS and "storia git" in e.messaggio


def test_config_del_cliente_non_usata(factory, finto):
    cliente = factory / "code_repos" / "cliente"
    (cliente / ".gitleaks.toml").write_text("[allowlist]\npaths = ['''.*''']\n")
    _commit(cliente, "config ostile")
    sg.scan_storia(str(cliente), str(factory))
    argv = json.loads(finto.read_text())
    cfg = argv[argv.index("--config") + 1]
    assert not cfg.startswith(str(cliente))


def test_senza_pin_non_verificabile_anche_con_gitleaks_nel_path(factory, finto):
    """D7: senza pin all'ancora gitleaks non e' identificato, anche se e' nel PATH."""
    _git(factory, "rm", "-q", "security/scanner-pins.json")
    _git(factory, "commit", "-q", "-m", "pin tolto", "--no-verify")
    _git(factory, "update-ref", "refs/remotes/origin/main", "HEAD")
    e = sg.scan_storia(str(factory / "code_repos" / "cliente"), str(factory))
    assert e.stato == sg.NON_VERIFICABILE and "non identificato" in e.messaggio


def test_gitleaks_sostituito_non_verificabile(factory, finto, tmp_path):
    g = tmp_path / "bin" / "gitleaks"
    g.write_text(g.read_text() + "# sostituito\n")
    e = sg.scan_storia(str(factory / "code_repos" / "cliente"), str(factory))
    assert e.stato == sg.NON_VERIFICABILE


# --- AC3: integrazione col gitleaks reale -----------------------------------------------------

@pytest.mark.skipif(not GITLEAKS_REALE, reason="integrazione NON eseguita: gitleaks non installato")
def test_integrazione_segreto_in_un_commit_passato_trovato_e_redatto(factory, monkeypatch):
    monkeypatch.setenv("PATH", os.path.dirname(GITLEAKS_REALE) + os.pathsep + os.environ.get("PATH", ""))
    pinna_gitleaks(factory, GITLEAKS_REALE)
    cliente = factory / "code_repos" / "cliente"
    segreto, sha = con_segreto_rimosso(cliente)
    assert segreto not in (cliente / "config.py").read_text()   # nel working tree non c'e' piu'
    r = subprocess.run([sys.executable, MODULO, "--root", str(factory), "--storia", str(cliente)],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=dict(os.environ))
    out = r.stdout.decode()
    assert r.returncode == 1, out
    assert segreto not in out and segreto[4:20] not in out
    assert "config.py:1" in out and sha[:12] in out
    e = sg.scan_storia(str(cliente), str(factory))
    assert e.stato == sg.FAIL
    assert set(e.findings[0]) == set(sg.CAMPI_STORIA) and e.findings[0]["Commit"] == sha
    assert segreto not in json.dumps(e.findings)


# --- CQRL iter-1 ------------------------------------------------------------------------------

def test_worktree_collegato_della_factory_rifiutato_anche_se_dichiarato(factory, tmp_path):
    """F2: un `git worktree add` della factory ha un altro toplevel ma la stessa storia."""
    wt = factory / "code_repos" / "wt"
    _git(factory, "worktree", "add", "-q", "--detach", str(wt))
    (factory / "factory.config.yaml").write_text(
        (factory / "factory.config.yaml").read_text().replace("code_repos/cliente/", "code_repos/wt/"))
    motivo = sg.guardia_storia(str(wt), str(factory))
    assert motivo and "repo della factory" in motivo


def test_clone_shallow_non_verificabile(factory, tmp_path, finto):
    cliente = factory / "code_repos" / "cliente"
    _commit(cliente, "secondo")
    shallow = factory / "code_repos" / "shallow"
    subprocess.run(["git", "clone", "-q", "--depth", "1", "file://" + str(cliente), str(shallow)], check=True)
    (factory / "factory.config.yaml").write_text(
        (factory / "factory.config.yaml").read_text().replace("code_repos/cliente/", "code_repos/shallow/"))
    e = sg.scan_storia(str(shallow), str(factory))
    assert e.stato == sg.NON_VERIFICABILE and "shallow" in e.messaggio


def test_finto_clone_bare_ignore_vuoto_e_gitleaks_allow_ignorato(factory, finto):
    sg.scan_storia(str(factory / "code_repos" / "cliente"), str(factory))
    argv = json.loads(finto.read_text())
    assert "--ignore-gitleaks-allow" in argv
    ign = argv[argv.index("--gitleaks-ignore-path") + 1]
    assert os.path.basename(ign) == "nessun-ignore"   # cartella vuota creata apposta (rimossa a fine scansione)
    assert argv[-1].endswith("storia.git") and not argv[-1].startswith(str(factory))


@pytest.mark.skipif(not GITLEAKS_REALE, reason="integrazione NON eseguita: gitleaks non installato")
def test_integrazione_gitleaksignore_non_tracciato_non_spegne(factory, monkeypatch):
    """F1: un .gitleaksignore non tracciato col fingerprint del finding dava PASS."""
    monkeypatch.setenv("PATH", os.path.dirname(GITLEAKS_REALE) + os.pathsep + os.environ.get("PATH", ""))
    pinna_gitleaks(factory, GITLEAKS_REALE)
    cliente = factory / "code_repos" / "cliente"
    _, sha = con_segreto_rimosso(cliente)
    e = sg.scan_storia(str(cliente), str(factory))
    assert e.stato == sg.FAIL
    f = e.findings[0]
    (cliente / ".gitleaksignore").write_text("%s:%s:%s:%s\n" % (f["Commit"], f["File"], f["RuleID"], f["StartLine"]))
    assert sg.scan_storia(str(cliente), str(factory)).stato == sg.FAIL


@pytest.mark.skipif(not GITLEAKS_REALE, reason="integrazione NON eseguita: gitleaks non installato")
def test_integrazione_gitleaks_allow_in_un_commit_passato_non_nasconde(factory, monkeypatch):
    monkeypatch.setenv("PATH", os.path.dirname(GITLEAKS_REALE) + os.pathsep + os.environ.get("PATH", ""))
    pinna_gitleaks(factory, GITLEAKS_REALE)
    cliente = factory / "code_repos" / "cliente"
    (cliente / "config.py").write_text("TOKEN = '%s'  # gitleaks:allow\n" % segreto_sintetico())
    _commit(cliente, "con allow")
    (cliente / "config.py").write_text("TOKEN = None\n")
    _commit(cliente, "tolto")
    assert sg.scan_storia(str(cliente), str(factory)).stato == sg.FAIL


# --- CQRL iter-2 ------------------------------------------------------------------------------

@pytest.mark.skipif(not GITLEAKS_REALE, reason="integrazione NON eseguita: gitleaks non installato")
def test_integrazione_segreto_solo_su_un_ramo_remoto(factory, monkeypatch, tmp_path):
    """N1: il clone --bare non copiava refs/remotes/*: segreto raggiungibile solo da origin/feature-x."""
    monkeypatch.setenv("PATH", os.path.dirname(GITLEAKS_REALE) + os.pathsep + os.environ.get("PATH", ""))
    pinna_gitleaks(factory, GITLEAKS_REALE)
    cliente = factory / "code_repos" / "cliente"
    _git(cliente, "checkout", "-q", "-b", "feature-x")
    (cliente / "config.py").write_text("TOKEN = '%s'\n" % segreto_sintetico())
    sha = _commit(cliente, "segreto sul ramo")
    _git(cliente, "checkout", "-q", "-")
    _git(cliente, "update-ref", "refs/remotes/origin/feature-x", sha)
    _git(cliente, "branch", "-q", "-D", "feature-x")
    e = sg.scan_storia(str(cliente), str(factory))
    assert e.stato == sg.FAIL and e.findings[0]["Commit"] == sha


@pytest.mark.skipif(not GITLEAKS_REALE, reason="integrazione NON eseguita: gitleaks non installato")
def test_integrazione_git_replace_non_nasconde(factory, monkeypatch):
    """N2: con --mirror arrivano i refs/replace/*: un replace del commit col segreto lo nascondeva."""
    monkeypatch.setenv("PATH", os.path.dirname(GITLEAKS_REALE) + os.pathsep + os.environ.get("PATH", ""))
    pinna_gitleaks(factory, GITLEAKS_REALE)
    cliente = factory / "code_repos" / "cliente"
    _, sha = con_segreto_rimosso(cliente)
    pulito = _git(cliente, "commit-tree", _git(cliente, "rev-parse", sha + "~1^{tree}"), "-p",
                  _git(cliente, "rev-parse", sha + "~1"), "-m", "finto")
    _git(cliente, "replace", "-f", sha, pulito)
    e = sg.scan_storia(str(cliente), str(factory))
    assert e.stato == sg.FAIL

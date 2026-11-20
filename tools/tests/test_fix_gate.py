"""Gate del fix di sicurezza (EP-109 US-431 AC2, AC3, AC4, AC5; TSK-1048, TSK-1049; D4 = (a)).

Scanner finto di test_sca_guard (DB finto {"nome@versione": [id]}): il fix legittimo porta jinja2 da 2.10
(GHSA-uno) a 2.11 (nessun advisory nel DB)."""
from __future__ import annotations

import json
import os
import stat
import subprocess
import sys

import pytest

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.normpath(os.path.join(QUI, "..", "security")))
import fix_gate as fg  # noqa: E402
import scanner_identity as si  # noqa: E402
import secrets_guard as sg  # noqa: E402
from test_sca_guard import FINTO, _commit, _git, _init, _scrivi  # noqa: E402

PROTOCOLLO = os.path.normpath(os.path.join(QUI, "..", "..", ".claude", "skills", "security-fix-protocol.md"))


@pytest.fixture
def caso(tmp_path):
    exe = tmp_path / "bin" / "osv-scanner"
    _scrivi(exe, FINTO % "osv")
    exe.chmod(exe.stat().st_mode | stat.S_IEXEC)
    db_dir = tmp_path / "db"
    db = db_dir / "osv-scalibr" / "PyPI" / "all.zip"
    _scrivi(db, json.dumps({"jinja2@2.10": ["GHSA-uno"], "jinja2@2.10.1": ["GHSA-uno"], "requests@2.19.0": ["GHSA-due"]}))
    f = tmp_path / "factory"
    _init(f)
    _scrivi(f / "factory.config.yaml", "code_paths:\n  - name: cliente\n    path: code_repos/cliente/\n"
            "security_scan:\n  osv_db_dir: %s\n  fix_max_iterations: 3\n" % db_dir)
    _, sha, _, err = si.misura("osv-scanner", str(exe))
    assert err is None, err
    _scrivi(f / "security" / "scanner-pins.json", json.dumps({"osv-scanner": [{"path": str(exe), "sha256": sha}]}))
    _commit(f, "factory", protetto=True, percorsi=("factory.config.yaml", "security"))
    cl = f / "code_repos" / "cliente"
    _init(cl)
    _scrivi(cl / "requirements.txt", "jinja2==2.10\n")
    _scrivi(cl / "app.py", "import jinja2\n")
    _commit(cl, "base", protetto=True)
    return {"factory": f, "cliente": cl, "db": db}


def verifica(c):
    return fg.verifica(str(c["cliente"]), str(c["factory"]), "GHSA-uno", "jinja2")


def fix(c, contenuto="jinja2==2.11\n", extra=None):
    _scrivi(c["cliente"] / "requirements.txt", contenuto)
    for p, t in (extra or {}).items():
        _scrivi(c["cliente"] / p, t)
    _commit(c["cliente"], "fix")


# --- perimetro (AC2, D4 = a) ------------------------------------------------------------------

@pytest.mark.parametrize("toccati,ok", [
    (["requirements.txt"], True),
    (["sub/requirements-dev.txt"], True),
    (["package.json", "package-lock.json"], True),
    (["go.mod", "go.sum"], True),
    (["package-lock.json"], False),           # lockfile senza manifest
    (["poetry.lock"], False),
    ([".semgrepignore"], False),
    ([".trivyignore"], False),
    (["osv-scanner.toml"], False),
    ([".github/workflows/ci.yml"], False),
    ([".gitlab-ci.yml"], False),
    ([".claude/agents/x.md"], False),
    (["security/sca-baseline.json"], False),
    (["management/kanban/id-registry.yaml"], False),
    (["app.py"], False),
])
def test_perimetro(toccati, ok):
    assert (fg.perimetro(toccati) == []) is ok, fg.perimetro(toccati)


@pytest.mark.parametrize("extra", [
    {".semgrepignore": "app.py\n"},
    {".github/workflows/ci.yml": "on: push\n"},
    {".claude/agents/x.md": "x\n"},
    {"security/sca-baseline.json": "[]\n"},
    {"management/id-registry.yaml": "x: 1\n"},
    {"app.py": "import jinja2  # cambiato\n"},
])
def test_diff_fuori_perimetro_fail(caso, extra):
    fix(caso, extra=extra)
    rep = verifica(caso)
    assert rep["esito"] == fg.FAIL and rep["motivo"] == "perimetro violato"
    assert [v[0] for v in rep["violazioni"]] == list(extra)


# --- chiusura legittima e non (AC3, US-428) ---------------------------------------------------

def test_versione_che_chiude_l_advisory_pass(caso):
    fix(caso)
    rep = verifica(caso)
    assert rep["esito"] == fg.PASS and "jinja2@2.11" in rep["motivo"]


def test_versione_ancora_vulnerabile_aperto(caso):
    fix(caso, "jinja2==2.10.1\n")
    assert verifica(caso)["esito"] == fg.APERTO


def test_pacchetto_rimosso_non_verificabile(caso):
    fix(caso, "flask==3.0.0\n")
    rep = verifica(caso)
    assert rep["esito"] == fg.NON_VERIFICABILE and "rimosso" in rep["motivo"]


def test_fix_che_introduce_una_vulnerabilita_fail(caso):
    fix(caso, "jinja2==2.11\nrequests==2.19.0\n")
    rep = verifica(caso)
    assert rep["esito"] == fg.FAIL and "nuova" in rep["motivo"]


def test_working_tree_sporco_non_verificabile(caso):
    fix(caso)
    _scrivi(caso["cliente"] / "requirements.txt", "jinja2==2.12\n")
    assert verifica(caso)["esito"] == fg.NON_VERIFICABILE


# --- AC5: non sopprime, non accetta rischi ----------------------------------------------------

def test_soppressione_nel_manifest_fail(caso):
    fix(caso, "jinja2==2.10  # nosec\n")
    rep = verifica(caso)
    assert rep["esito"] == fg.FAIL and "non sopprime" in rep["motivo"]


def test_baseline_o_accettazioni_fuori_perimetro(caso):
    fix(caso, extra={"security/suppression-accettazioni.json": "[]\n"})
    assert verifica(caso)["esito"] == fg.FAIL


# --- AC3: loop bounded ------------------------------------------------------------------------

def test_ciclo_si_ferma_al_primo_esito_non_aperto():
    esiti = iter([{"esito": "APERTO", "motivo": "a", "file_toccati": ["r.txt"]},
                  {"esito": "PASS", "motivo": "ok", "file_toccati": ["r.txt"]}])
    giri = []
    r = fg.ciclo(lambda: next(esiti), giri.append, 5)
    assert r["esito"] == "PASS" and giri == [1, 2]


def test_ciclo_bounded_loop_exhausted():
    n = iter(range(100))
    r = fg.ciclo(lambda: {"esito": "APERTO", "motivo": "m%d" % next(n), "file_toccati": []}, lambda i: None, 3)
    assert r["esito"] == "APERTO" and r["markers"]["loop_exhausted"] and len(r["iterazioni"]) == 3


def test_ciclo_no_progress():
    r = fg.ciclo(lambda: {"esito": "APERTO", "motivo": "uguale", "file_toccati": ["r.txt"]}, lambda i: None, 5)
    assert r["markers"]["no_progress"] and len(r["iterazioni"]) == 2


def test_max_iterazioni_dall_ancora(caso):
    assert fg.max_iterazioni(str(caso["factory"])) == 3


def test_ciclo_reale_fino_al_pass(caso):
    versioni = iter(["jinja2==2.10.1\n", "jinja2==2.11\n"])
    r = fg.ciclo(lambda: verifica(caso), lambda i: fix(caso, next(versioni)), fg.max_iterazioni(str(caso["factory"])))
    assert [g["esito"] for g in r["iterazioni"]] == ["APERTO", "PASS"]


# --- AC4: nessun push, nessun merge -----------------------------------------------------------

def test_verifica_non_invoca_push_ne_merge(caso, monkeypatch):
    fix(caso)
    comandi = []
    vero_run, vero_popen = subprocess.run, subprocess.Popen

    def run(argv, *a, **k):
        comandi.append(list(argv))
        return vero_run(argv, *a, **k)

    class Popen(vero_popen):
        def __init__(self, argv, *a, **k):
            comandi.append(list(argv))
            super().__init__(argv, *a, **k)

    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setattr(subprocess, "Popen", Popen)
    assert verifica(caso)["esito"] == fg.PASS
    vietati = {"push", "merge", "pr", "rebase", "reset", "commit"}
    assert comandi and not [c for c in comandi if vietati & set(c)], [c for c in comandi if vietati & set(c)]


def test_ne_il_gate_ne_il_protocollo_contengono_comandi_di_merge():
    sorgente = open(fg.__file__, encoding="utf-8").read()
    assert not any(x in sorgente for x in ('"push"', '"merge"', "gh pr merge", "git push"))
    protocollo = open(PROTOCOLLO, encoding="utf-8").read()
    for riga in protocollo.splitlines():
        if "git push" in riga or "gh pr merge" in riga or "git merge" in riga:
            assert "mai" in riga.lower() or "non " in riga.lower(), riga


def test_factory_rifiutata(caso):
    with pytest.raises(sg.Rifiuto):
        fg.verifica(str(caso["factory"]), str(caso["factory"]), "GHSA-uno", "jinja2")

"""Riscansione al cambio del DB (EP-109 US-432 AC2, AC3; TSK-1050).

Stessi scanner finti di test_sca_guard (DB finto in JSON nel posto dei veri). AC1 e' l'esito dello spike
TSK-1037 (pinning offline verificato), citato nel docstring del modulo e nel TSK."""
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
import rescan as rs  # noqa: E402
import scanner_identity as si  # noqa: E402
import secrets_guard as sg  # noqa: E402
from test_sca_guard import FINTO, _commit, _init, _scrivi  # noqa: E402


@pytest.fixture(params=["osv-scanner", "trivy"])
def caso(request, tmp_path):
    nome = request.param
    exe = tmp_path / "bin" / nome
    _scrivi(exe, FINTO % ("osv" if nome == "osv-scanner" else "trivy"))
    exe.chmod(exe.stat().st_mode | stat.S_IEXEC)
    db_dir = tmp_path / "db"
    db = db_dir / ("osv-scalibr/PyPI/all.zip" if nome == "osv-scanner" else "db/trivy.db")
    _scrivi(db, json.dumps({"jinja2@2.10": ["GHSA-uno"]}))
    if nome == "trivy":
        _scrivi(db_dir / "db" / "metadata.json", json.dumps({"Version": 2, "UpdatedAt": "2026-11-19T07:06:49Z"}))
    f = tmp_path / "factory"
    _init(f)
    chiave = "osv_db_dir" if nome == "osv-scanner" else "trivy_cache_dir"
    _scrivi(f / "factory.config.yaml", "code_paths:\n  - name: cliente\n    path: code_repos/cliente/\n"
            "security_scan:\n  %s: %s\n" % (chiave, db_dir))
    _, sha, _, err = si.misura(nome, str(exe))
    assert err is None, err
    _scrivi(f / "security" / "scanner-pins.json", json.dumps({nome: [{"path": str(exe), "sha256": sha}]}))
    _commit(f, "factory", protetto=True, percorsi=("factory.config.yaml", "security"))
    cl = f / "code_repos" / "cliente"
    _init(cl)
    _scrivi(cl / "requirements.txt", "jinja2==2.10\nrequests==2.19.0\n")
    _commit(cl, "base", protetto=True)
    return {"nome": nome, "factory": f, "cliente": cl, "db": db, "exe": exe}


def esegui(c):
    return rs.esegui(str(c["cliente"]), str(c["factory"]), c["nome"])


def aggiorna_db(c, voci):
    c["db"].write_text(json.dumps(voci))
    if c["nome"] == "trivy":
        (c["db"].parent / "metadata.json").write_text(json.dumps({"Version": 2, "UpdatedAt": "2026-11-20T07:00:00Z"}))


# --- AC2: determinismo e mai FAIL ------------------------------------------------------------

def test_primo_run_crea_il_riferimento(caso):
    rep = esegui(caso)
    assert rep["esito"] == rs.CREATO and os.path.exists(rep["riferimento"])


def test_stesso_commit_stesso_db_stesso_esito(caso):
    esegui(caso)
    a, b = esegui(caso), esegui(caso)
    assert a["esito"] == b["esito"] == rs.INVARIATO and a["db"] == b["db"]
    assert json.loads(open(a["riferimento"]).read())["finding"] == [["GHSA-uno", "pkg:pypi/jinja2@2.10"]]


def test_db_diverso_solo_evento_exit_0(caso):
    esegui(caso)
    aggiorna_db(caso, {"jinja2@2.10": ["GHSA-uno"], "requests@2.19.0": ["GHSA-due"]})
    rep = esegui(caso)
    assert rep["esito"] == rs.EVENTO and rs.EXIT[rep["esito"]] == 0
    r = subprocess.run([sys.executable, rs.__file__, str(caso["cliente"]), "--root", str(caso["factory"]),
                        "--scanner", caso["nome"]], stdout=subprocess.PIPE)
    assert r.returncode == 0   # anche dalla CLI: mai bloccante


def test_stesso_db_finding_diversi_non_deterministico(caso):
    esegui(caso)
    rif = json.loads(open(esegui(caso)["riferimento"]).read())
    rif["finding"] = []       # riferimento con lo stesso DB ma un altro insieme
    open(esegui(caso)["riferimento"], "w").write(json.dumps(rif))
    rep = esegui(caso)
    assert rep["esito"] == rs.NON_VERIFICABILE and "deterministica" in rep["motivo"]
    assert json.loads(open(rep["riferimento"]).read())["finding"] == []   # il riferimento non si aggiorna


def test_commit_cambiato_non_e_una_riscansione(caso):
    esegui(caso)
    _scrivi(caso["cliente"] / "requirements.txt", "jinja2==2.10\n")
    _commit(caso["cliente"])
    assert esegui(caso)["esito"] == rs.COMMIT_CAMBIATO


# --- AC3: l'evento elenca i finding nuovi per identita' --------------------------------------

def test_evento_elenca_nuovi_e_spariti_per_identita(caso):
    esegui(caso)
    aggiorna_db(caso, {"requests@2.19.0": ["GHSA-due"]})
    rep = esegui(caso)
    ev = rep["evento"]
    assert ev["nuovi"] == [["GHSA-due", "pkg:pypi/requests@2.19.0"]]
    assert ev["spariti"] == [["GHSA-uno", "pkg:pypi/jinja2@2.10"]]
    assert ev["db_prima"] != ev["db_dopo"] and ev["commit"] == rep["commit"]
    salvato = json.loads(open(rep["file_evento"]).read())
    assert salvato == ev and ":" not in os.path.basename(rep["file_evento"])
    assert "maintainer" in ev["nota"] and "risolt" not in json.dumps(ev).lower()


def test_dopo_l_evento_il_riferimento_e_il_nuovo_db(caso):
    esegui(caso)
    aggiorna_db(caso, {"jinja2@2.10": ["GHSA-uno", "GHSA-tre"]})
    esegui(caso)
    assert esegui(caso)["esito"] == rs.INVARIATO


# --- confronta (puro) e bordi ----------------------------------------------------------------

def test_confronta_puro():
    a = {"commit": "c1", "db": "d1", "tool": "t", "finding": [["X", "pkg:a@1"]]}
    assert rs.confronta(None, a) == (rs.CREATO, None)
    assert rs.confronta(a, dict(a))[0] == rs.INVARIATO
    assert rs.confronta(a, dict(a, commit="c2"))[0] == rs.COMMIT_CAMBIATO
    esito, ev = rs.confronta(a, dict(a, db="d2", finding=[["X", "pkg:a@1"], ["Y", "pkg:b@2"]]))
    assert esito == rs.EVENTO and ev["nuovi"] == [["Y", "pkg:b@2"]] and ev["spariti"] == []


def test_db_assente_non_verificabile_senza_toccare_il_riferimento(caso):
    rif = esegui(caso)["riferimento"]
    prima = open(rif).read()
    caso["db"].unlink()
    rep = esegui(caso)
    assert rep["esito"] == rs.NON_VERIFICABILE and open(rif).read() == prima


def test_riferimento_illeggibile_non_verificabile(caso):
    rif = esegui(caso)["riferimento"]
    open(rif, "w").write("{rotto")
    assert esegui(caso)["esito"] == rs.NON_VERIFICABILE


def test_factory_rifiutata(caso):
    with pytest.raises(sg.Rifiuto):
        rs.esegui(str(caso["factory"]), str(caso["factory"]), caso["nome"])


# --- integrazione: determinismo coi binari reali sul DB dello spike TSK-1037 ------------------

SPIKE = os.environ.get("SCA_TEST_DB_SPIKE", "")


@pytest.mark.skipif(not (SPIKE and os.path.isdir(SPIKE)), reason="integrazione NON eseguita: SCA_TEST_DB_SPIKE non impostata")
@pytest.mark.parametrize("nome,sotto", [("osv-scanner", "osv-cache"), ("trivy", "trivy-cache")])
def test_integrazione_determinismo_reale(nome, sotto, tmp_path):
    exe = "/opt/homebrew/bin/" + nome
    if not os.path.isfile(exe):
        pytest.skip("integrazione NON eseguita: %s non installato" % nome)
    _, sha, _, _ = si.misura(nome, exe)
    f = tmp_path / "factory"
    _init(f)
    chiave = "osv_db_dir" if nome == "osv-scanner" else "trivy_cache_dir"
    _scrivi(f / "factory.config.yaml", "code_paths:\n  - name: c\n    path: code_repos/c/\n"
            "security_scan:\n  %s: %s\n" % (chiave, os.path.join(SPIKE, sotto)))
    _scrivi(f / "security" / "scanner-pins.json", json.dumps({nome: [{"path": exe, "sha256": sha}]}))
    _commit(f, "f", protetto=True, percorsi=("factory.config.yaml", "security"))
    cl = f / "code_repos" / "c"
    _init(cl)
    _scrivi(cl / "requirements.txt", "jinja2==2.10\nrequests==2.19.0\n")
    _commit(cl, "base", protetto=True)
    assert rs.esegui(str(cl), str(f), nome)["esito"] == rs.CREATO
    rep = rs.esegui(str(cl), str(f), nome)
    assert rep["esito"] == rs.INVARIATO, rep
    assert len(json.loads(open(rep["riferimento"]).read())["finding"]) > 0

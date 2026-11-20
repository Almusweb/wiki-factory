"""Oracolo SCA (EP-109 US-425 AC2, AC3, AC5; TSK-1038).

Scanner finti: leggono `requirements.txt` dell'albero e un DB finto (JSON {"nome@versione": [id]}) nel posto
in cui i veri tengono il loro (osv: <dir>/osv-scalibr/PyPI/all.zip; trivy: <cache>/db/trivy.db), e scrivono
CycloneDX. Il baseline e i pin stanno sull'ancora origin/main della factory finta."""
from __future__ import annotations

import datetime
import json
import os
import stat
import subprocess
import sys

import pytest

QUI = os.path.dirname(os.path.abspath(__file__))
SEC = os.path.normpath(os.path.join(QUI, "..", "security"))
sys.path.insert(0, SEC)
import sca_guard as sca  # noqa: E402
import scanner_identity as si  # noqa: E402
import secrets_guard as sg  # noqa: E402

FINTO = r'''#!/usr/bin/env python3
import json, os, sys
a = sys.argv[1:]
NOME = %r
if a[:1] in (["--version"], ["version"]):
    print("osv-scanner version: 2.7.1" if NOME == "osv" else "Version: 0.76.2"); sys.exit(0)
def opt(n):
    return a[a.index(n) + 1] if n in a else None
if NOME == "osv":
    assert a[:2] == ["scan", "source"] and "--offline" in a and "--offline-vulnerabilities" in a, a
    db = os.path.join(os.environ["OSV_SCANNER_LOCAL_DB_CACHE_DIRECTORY"], "osv-scalibr", "PyPI", "all.zip")
    uscita = opt("--output-file")
else:
    assert a[0] == "fs" and "--skip-db-update" in a and "--offline-scan" in a, a
    db = os.path.join(opt("--cache-dir"), "db", "trivy.db")
    uscita = opt("--output")
if not os.path.exists(db):
    sys.stderr.write("no offline database\n"); sys.exit(127)
vuln = json.load(open(db))
comp, vul = [], []
righe = open("requirements.txt").read().split() if os.path.exists("requirements.txt") else []
if not righe and NOME == "osv":
    sys.exit(128)
for r in righe:
    n, v = r.split("==")
    purl = "pkg:pypi/%%s@%%s" %% (n, v)
    comp.append({"bom-ref": purl, "name": n, "version": v, "purl": purl})
    for i in vuln.get("%%s@%%s" %% (n, v), []):
        vul.append({"id": i, "affects": [{"ref": purl}]})
json.dump({"bomFormat": "CycloneDX", "components": comp, "vulnerabilities": vul}, open(uscita, "w"))
sys.exit(1 if (vul and NOME == "osv") else 0)
'''


def _git(repo, *a):
    r = subprocess.run(["git", "-C", str(repo)] + list(a), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert r.returncode == 0, r.stderr
    return r.stdout.decode().strip()


def _init(repo):
    repo.mkdir(parents=True, exist_ok=True)
    for c in (("init", "-q"), ("config", "user.email", "t@t"), ("config", "user.name", "t"),
              ("config", "commit.gpgsign", "false")):
        _git(repo, *c)


def _commit(repo, msg="c", protetto=False, percorsi=("-A",)):
    _git(repo, "add", *percorsi)
    _git(repo, "commit", "-q", "--allow-empty", "-m", msg, "--no-verify")
    if protetto:
        _git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")


def _scrivi(p, testo):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(testo)


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
    _scrivi(f / "factory.config.yaml",
            "code_paths:\n  - name: cliente\n    path: code_repos/cliente/\n"
            "security_scan:\n  %s: %s\n  sca_baseline: security/sca-baseline.json\n" % (chiave, db_dir))
    _, sha, _, err = si.misura(nome, str(exe))
    assert err is None, err
    _scrivi(f / "security" / "scanner-pins.json", json.dumps({nome: [{"path": str(exe), "sha256": sha}]}))
    _commit(f, "factory", protetto=True, percorsi=("factory.config.yaml", "security"))
    cl = f / "code_repos" / "cliente"
    _init(cl)
    _scrivi(cl / "requirements.txt", "jinja2==2.10\n")
    _commit(cl, "base", protetto=True)
    return {"nome": nome, "factory": f, "cliente": cl, "db": db, "db_dir": db_dir, "exe": exe}


OGGI = datetime.date.today()


def rec(vid, purl=None, **kw):
    """Record valido oggi: accettato ieri, scade fra 30 giorni."""
    r = {"id": vid, "accettato_da": "maintainer", "riferimento_gate": "PR #0",
         "accettato_il": (OGGI - datetime.timedelta(days=1)).isoformat(),
         "scadenza": (OGGI + datetime.timedelta(days=30)).isoformat()}
    if purl:
        r["purl"] = purl
    r.update(kw)
    return {k: v for k, v in r.items() if v is not None}


def baseline(caso, record):
    _scrivi(caso["factory"] / "security" / "sca-baseline.json", json.dumps(record))
    _commit(caso["factory"], "baseline", protetto=True, percorsi=("security",))


def esegui(caso):
    return sca.esegui(str(caso["cliente"]), str(caso["factory"]), caso["nome"])


def stati(rep):
    return sorted((v["id"], v["stato"]) for v in rep["voci"])


# --- AC3: senza baseline nessun PASS ----------------------------------------------------------

def test_senza_baseline_il_primo_run_non_verificabile(caso):
    rep = esegui(caso)
    assert rep["esito"] == sca.NON_VERIFICABILE and "baseline" in rep["motivo"]
    assert rep["baseline"]["presente"] is False


def test_baseline_solo_sul_branch_non_vale(caso):
    _scrivi(caso["factory"] / "security" / "sca-baseline.json", json.dumps([rec("GHSA-uno")]))
    _commit(caso["factory"], "baseline sul branch", percorsi=("security",))
    assert esegui(caso)["esito"] == sca.NON_VERIFICABILE


def test_baseline_solo_nel_working_tree_non_vale(caso):
    _scrivi(caso["factory"] / "security" / "sca-baseline.json", json.dumps([rec("GHSA-uno")]))
    assert esegui(caso)["esito"] == sca.NON_VERIFICABILE


# --- AC2: report con SBOM, DB, identita', finding fuori baseline -------------------------------

def test_debito_accettato_pass_e_report_completo(caso):
    baseline(caso, [rec("GHSA-uno", "pkg:pypi/jinja2@2.10")])
    rep = esegui(caso)
    assert rep["esito"] == sca.PASS
    assert rep["sbom"] == ["pkg:pypi/jinja2@2.10"]
    assert rep["identita"]["stato"] == si.IDENTIFICATO
    assert len(rep["db"]["file"]) == 1 and len(rep["db"]["file"][0]["sha256"]) == 64
    if caso["nome"] == "trivy":
        assert rep["db"]["updated_at"] == "2026-11-19T07:06:49Z"
    assert stati(rep) == [("GHSA-uno", sca.ACCETTATO)]


def test_dipendenza_vulnerabile_aggiunta_dal_commit_fail(caso):
    baseline(caso, [rec("GHSA-uno")])
    db = json.loads(caso["db"].read_text())
    db["requests@2.19.0"] = ["GHSA-due"]
    caso["db"].write_text(json.dumps(db))
    _scrivi(caso["cliente"] / "requirements.txt", "jinja2==2.10\nrequests==2.19.0\n")
    _commit(caso["cliente"])
    rep = esegui(caso)
    assert rep["esito"] == sca.FAIL
    assert ("GHSA-due", sca.NUOVO) in stati(rep)


def test_stesso_advisory_a_un_altra_versione_e_debito_non_nuovo(caso):
    """Un fix che sale a una versione ancora vulnerabile non e' una vulnerabilita' nuova dal commit."""
    baseline(caso, [])
    db = json.loads(caso["db"].read_text())
    db["jinja2@2.10.1"] = ["GHSA-uno"]
    caso["db"].write_text(json.dumps(db))
    _scrivi(caso["cliente"] / "requirements.txt", "jinja2==2.10.1\n")
    _commit(caso["cliente"])
    rep = esegui(caso)
    assert rep["esito"] == sca.NON_VERIFICABILE
    assert ("GHSA-uno", sca.DEBITO) in stati(rep) and ("GHSA-uno", sca.SPARITO) in stati(rep)


def test_record_con_purl_diverso_non_accetta(caso):
    baseline(caso, [rec("GHSA-uno", "pkg:pypi/jinja2@9.9")])
    rep = esegui(caso)
    assert rep["esito"] == sca.NON_VERIFICABILE and stati(rep) == [("GHSA-uno", sca.DEBITO)]


def test_dipendenza_tolta_sparita_non_contata(caso):
    baseline(caso, [rec("GHSA-uno")])
    _scrivi(caso["cliente"] / "requirements.txt", "flask==3.0.0\n")
    _commit(caso["cliente"])
    rep = esegui(caso)
    assert stati(rep) == [("GHSA-uno", sca.SPARITO)]
    assert "risolt" not in json.dumps(rep["voci"]).lower() and not any(isinstance(v, int) for v in rep.values())


# --- AC5: DB cambiato a commit fermo non da' FAIL ---------------------------------------------

def test_db_cambiato_a_commit_fermo_nessun_fail(caso):
    baseline(caso, [rec("GHSA-uno")])
    caso["db"].write_text(json.dumps({"jinja2@2.10": ["GHSA-uno", "GHSA-nuovo-nel-db"]}))
    rep = esegui(caso)
    assert rep["esito"] == sca.NON_VERIFICABILE   # riscansione, non FAIL
    assert ("GHSA-nuovo-nel-db", sca.DEBITO) in stati(rep)


def test_stesso_commit_stesso_db_stesso_esito(caso):
    baseline(caso, [rec("GHSA-uno")])
    a, b = esegui(caso), esegui(caso)
    assert (a["esito"], a["voci"], a["db"]["id"]) == (b["esito"], b["voci"], b["db"]["id"])


# --- DB, identita', perimetro -----------------------------------------------------------------

def test_db_assente_non_verificabile(caso):
    baseline(caso, [rec("GHSA-uno")])
    caso["db"].unlink()
    rep = esegui(caso)
    assert rep["esito"] == sca.NON_VERIFICABILE and "DB" in rep["motivo"]


def test_db_non_configurato_non_verificabile(caso):
    cfg = caso["factory"] / "factory.config.yaml"
    cfg.write_text(cfg.read_text().replace(str(caso["db_dir"]), "null"))
    _commit(caso["factory"], "db null", protetto=True, percorsi=("factory.config.yaml",))
    assert "non configurato" in esegui(caso)["motivo"]


def test_binario_sostituito_non_verificabile(caso):
    caso["exe"].write_text(caso["exe"].read_text() + "# sostituito\n")
    rep = esegui(caso)
    assert rep["esito"] == sca.NON_VERIFICABILE and "non identificato" in rep["motivo"]


def test_factory_rifiutata(caso):
    with pytest.raises(sg.Rifiuto):
        sca.esegui(str(caso["factory"]), str(caso["factory"]), caso["nome"])


def test_cyclonedx_con_riferimento_sconosciuto_illeggibile():
    with pytest.raises(ValueError):
        sca.leggi_cyclonedx({"components": [], "vulnerabilities": [{"id": "X", "affects": [{"ref": "boh"}]}]})


def test_cli_exit_code(caso):
    def cli(*extra):
        return subprocess.run([sys.executable, sca.__file__, str(caso["cliente"]), "--root", str(caso["factory"]),
                               "--scanner", caso["nome"]] + list(extra), stdout=subprocess.PIPE).returncode
    assert cli() == 3
    baseline(caso, [rec("GHSA-uno")])
    assert cli("--json") == 0


# --- AC4: record del baseline (TSK-1039) ------------------------------------------------------

def _scartato(rep, frammento):
    return any(frammento in r["motivo"] for r in rep["baseline"]["scartati"])


@pytest.mark.parametrize("mut,frammento", [
    ({"scadenza": (OGGI - datetime.timedelta(days=1)).isoformat(),
      "accettato_il": (OGGI - datetime.timedelta(days=10)).isoformat()}, "scaduto"),
    ({"scadenza": (OGGI + datetime.timedelta(days=95)).isoformat()}, "oltre 90 giorni"),
    ({"accettato_il": (OGGI + datetime.timedelta(days=1)).isoformat()}, "nel futuro"),
    ({"accettato_da": ""}, "accettato_da"),
    ({"riferimento_gate": None}, "riferimento_gate"),
    ({"scadenza": "fra un mese"}, "date"),
    ({"summary": "Jinja2 sandbox escape via ..."}, "campi non ammessi"),
    ({"purl": "jinja2@2.10"}, "purl"),
])
def test_record_non_valido_vale_come_assente(caso, mut, frammento):
    baseline(caso, [rec("GHSA-uno", **mut)])
    rep = esegui(caso)
    assert rep["esito"] == sca.NON_VERIFICABILE and stati(rep) == [("GHSA-uno", sca.DEBITO)]
    assert _scartato(rep, frammento), rep["baseline"]["scartati"]


def test_record_valido_con_motivo_e_purl_accettato(caso):
    baseline(caso, [rec("GHSA-uno", "pkg:pypi/jinja2@2.10", motivo="nessun template utente")])
    rep = esegui(caso)
    assert rep["esito"] == sca.PASS and rep["baseline"]["scartati"] == []


def test_scadenza_esattamente_a_90_giorni_ammessa(caso):
    baseline(caso, [rec("GHSA-uno", accettato_il=OGGI.isoformat(),
                        scadenza=(OGGI + datetime.timedelta(days=90)).isoformat())])
    assert esegui(caso)["esito"] == sca.PASS


def _cli(caso):
    return subprocess.run([sys.executable, sca.__file__, str(caso["cliente"]), "--root", str(caso["factory"]),
                           "--scanner", caso["nome"]], stdout=subprocess.PIPE)


def _fail_dal_commit(caso):
    db = json.loads(caso["db"].read_text())
    db["requests@2.19.0"] = ["GHSA-due"]
    caso["db"].write_text(json.dumps(db))
    _scrivi(caso["cliente"] / "requirements.txt", "jinja2==2.10\nrequests==2.19.0\n")
    _commit(caso["cliente"])


def test_severita_warn_prima_di_required_from_non_blocca(caso):
    baseline(caso, [rec("GHSA-uno")])
    _fail_dal_commit(caso)
    rep = esegui(caso)
    assert rep["esito"] == sca.FAIL and rep["severita"] == "WARN"
    r = _cli(caso)
    assert r.returncode == 0 and b"non bloccante" in r.stdout


def test_severita_error_da_required_from_blocca(caso):
    cfg = caso["factory"] / "factory.config.yaml"
    cfg.write_text(cfg.read_text() + "  sca_required_from: %s\n" % OGGI.isoformat())
    _commit(caso["factory"], "required_from", protetto=True, percorsi=("factory.config.yaml",))
    baseline(caso, [rec("GHSA-uno")])
    _fail_dal_commit(caso)
    assert esegui(caso)["severita"] == "ERROR" and _cli(caso).returncode == 1


def test_required_from_solo_su_disco_non_vale(caso):
    cfg = caso["factory"] / "factory.config.yaml"
    cfg.write_text(cfg.read_text() + "  sca_required_from: 2000-01-01\n")
    baseline(caso, [rec("GHSA-uno")])
    _fail_dal_commit(caso)
    assert esegui(caso)["severita"] == "WARN"


# --- integrazione coi binari reali (DB dello spike TSK-1037, se presente) ---------------------

SPIKE = os.environ.get("SCA_TEST_DB_SPIKE", "")


@pytest.mark.skipif(not (SPIKE and os.path.isdir(SPIKE)), reason="integrazione NON eseguita: SCA_TEST_DB_SPIKE non impostata")
@pytest.mark.parametrize("nome,sotto", [("osv-scanner", "osv-cache"), ("trivy", "trivy-cache")])
def test_integrazione_scanner_reale(nome, sotto, tmp_path):
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
    _scrivi(f / "security" / "sca-baseline.json", "[]")   # baseline presente e vuoto
    _commit(f, "f", protetto=True, percorsi=("factory.config.yaml", "security"))
    cl = f / "code_repos" / "c"
    _init(cl)
    _scrivi(cl / "requirements.txt", "jinja2==2.10\nrequests==2.19.0\n")
    _commit(cl, "base", protetto=True)
    rep = sca.esegui(str(cl), str(f), nome)
    assert rep["identita"]["stato"] == si.IDENTIFICATO, rep.get("motivo")
    assert set(rep["sbom"]) >= {"pkg:pypi/jinja2@2.10", "pkg:pypi/requests@2.19.0"}
    assert rep["esito"] == sca.NON_VERIFICABILE and any(v["stato"] == sca.DEBITO for v in rep["voci"])
    _scrivi(cl / "requirements.txt", "jinja2==2.10\nrequests==2.19.0\nurllib3==1.23\n")
    _commit(cl, "urllib3 vecchio")
    rep2 = sca.esegui(str(cl), str(f), nome)
    assert rep2["esito"] == sca.FAIL and any(v["stato"] == sca.NUOVO and "urllib3" in v["purl"] for v in rep2["voci"])

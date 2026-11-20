"""Runner di /security-scan (EP-109 US-429 AC1, AC3 per il formato; TSK-1045).

Gli oracoli veri hanno i loro test (test_oracoli_statici, test_sca_guard, test_secrets_guard_storia): qui il
registro e' sostituito da oracoli finti, e si prova cio' che e' del runner: flag dall'ancora, aggregazione,
report a campi enumerati, nome del file portabile."""
from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.normpath(os.path.join(QUI, "..", ".."))
MODULO = os.path.join(RADICE, "tools", "security", "security_scan.py")
sys.path.insert(0, os.path.dirname(MODULO))
import security_scan as ss  # noqa: E402
import secrets_guard as sg  # noqa: E402


def _git(repo, *a):
    r = subprocess.run(["git", "-C", str(repo)] + list(a), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert r.returncode == 0, r.stderr
    return r.stdout.decode().strip()


def _factory(tmp_path, enabled):
    f = tmp_path / "factory"
    f.mkdir()
    for c in (("init", "-q"), ("config", "user.email", "t@t"), ("config", "user.name", "t"),
              ("config", "commit.gpgsign", "false")):
        _git(f, *c)
    (f / "factory.config.yaml").write_text("security_scan:\n  enabled: %s\n" % ("true" if enabled else "false"))
    _git(f, "add", "-A")
    _git(f, "commit", "-q", "-m", "c", "--no-verify")
    _git(f, "update-ref", "refs/remotes/origin/main", "HEAD")
    return f


def finto(esito, voci=(), motivo=None):
    return lambda code_path, root: {"esito": esito, "motivo": motivo, "tool": "finto", "identita": {},
                                    "voci": list(voci)}


# --- AC1: opt-in, spento di default, messaggio esplicito --------------------------------------

def test_flag_spento_messaggio_esplicito_e_nessun_oracolo(tmp_path):
    f = _factory(tmp_path, enabled=False)
    chiamati = []
    reg = {o: (lambda o: lambda c, r: chiamati.append(o))(o) for o in ss.ORACOLI}
    rep = ss.esegui(str(tmp_path), str(f), registro=reg)
    assert rep["spento"] and rep["esito"] == ss.NON_VERIFICABILE and chiamati == []
    assert "opt-in" in rep["motivo"] and "nessuna verifica" in rep["motivo"]


def test_cli_a_flag_spento_esce_3_e_lo_dice(tmp_path):
    f = _factory(tmp_path, enabled=False)
    r = subprocess.run([sys.executable, MODULO, str(tmp_path), "--root", str(f)], stdout=subprocess.PIPE)
    assert r.returncode == 3 and b"CAPABILITY SPENTA" in r.stdout
    assert not (f / "security" / "reports").exists()


def test_enabled_solo_su_disco_non_accende(tmp_path):
    f = _factory(tmp_path, enabled=False)
    (f / "factory.config.yaml").write_text("security_scan:\n  enabled: true\n")
    assert ss.abilitato(str(f))[0] is False


def test_master_spento_di_default():
    """Nel master il blocco esiste e l'opt-in e' spento (schema: default false)."""
    testo = open(os.path.join(RADICE, "factory.config.yaml"), encoding="utf-8").read()
    import config_ancorata as ca
    assert ca.blocco_da_testo(testo, "security_scan").get("enabled") == "false"
    schema = json.load(open(os.path.join(RADICE, "schemas", "factory.config.schema.json"), encoding="utf-8"))
    assert schema["properties"]["security_scan"]["properties"]["enabled"]["default"] is False


# --- aggregazione ---------------------------------------------------------------------------

@pytest.mark.parametrize("esiti,atteso", [
    (["PASS", "PASS", "PASS", "PASS"], "PASS"),
    (["PASS", "NON_VERIFICABILE", "PASS", "PASS"], "NON_VERIFICABILE"),
    (["NON_VERIFICABILE", "FAIL", "PASS", "PASS"], "FAIL"),
])
def test_esito_complessivo(tmp_path, esiti, atteso):
    f = _factory(tmp_path, enabled=True)
    reg = {o: finto(e) for o, e in zip(ss.ORACOLI, esiti)}
    assert ss.esegui(str(tmp_path), str(f), registro=reg)["esito"] == atteso


def test_oracolo_che_si_rompe_o_rifiuta_non_verificabile(tmp_path):
    f = _factory(tmp_path, enabled=True)
    def rotto(c, r):
        raise RuntimeError("boom")
    def rifiuta(c, r):
        raise sg.Rifiuto("repo della factory")
    rep = ss.esegui(str(tmp_path), str(f), oracoli=("sast", "iac"), registro={"sast": rotto, "iac": rifiuta})
    assert rep["esito"] == ss.NON_VERIFICABILE
    assert [r["motivo"].split(" ")[0] for r in rep["oracoli"]] == ["errore", "rifiutato:"]


def test_nessun_oracolo_scelto_non_e_pass(tmp_path):
    f = _factory(tmp_path, enabled=True)
    assert ss.esegui(str(tmp_path), str(f), oracoli=(), registro={})["esito"] == ss.NON_VERIFICABILE


# --- report: campi enumerati, nome portabile, cartella ignorata --------------------------------

CAMPI_VOCE = {"id", "path", "purl", "riga", "commit", "stato", "motivo"}


def test_adattatore_statico_tiene_solo_campi_enumerati():
    rep = {"confronto": {"voci": [{"identita": ["semgrep", "python.sqli", "app/db.py::"], "esito": "nuovo",
                                   "dettaglio": "testo libero dello scanner"}]},
           "soppressioni": {"voci": [{"tipo": "nosemgrep", "path": "app/db.py", "testo": "x # nosemgrep",
                                      "accettata": False}]}}
    voci = ss._voci_statiche(rep)
    assert all(set(v) <= CAMPI_VOCE for v in voci)
    assert "testo libero" not in json.dumps(voci) and "x # nosemgrep" not in json.dumps(voci)


def test_report_scritto_con_nome_portabile(tmp_path):
    f = _factory(tmp_path, enabled=True)
    cl = tmp_path / "cliente con spazi"
    cl.mkdir()
    rep = ss.esegui(str(cl), str(f), oracoli=("sca",),
                    registro={"sca": finto("FAIL", [{"id": "GHSA-x", "purl": "pkg:pypi/a@1", "stato": "nuovo_dal_commit",
                                                    "motivo": None}])})
    p = ss.scrivi_report(rep, str(f), str(cl))
    assert p.parent == f / "security" / "reports" and ":" not in p.name and " " not in p.name
    assert json.loads(p.read_text())["oracoli"][0]["voci"][0]["id"] == "GHSA-x"


def test_cartella_dei_report_ignorata_da_git():
    r = subprocess.run(["git", "-C", RADICE, "check-ignore", "-q", "security/reports/x.json"])
    assert r.returncode == 0, "security/reports/ deve essere in .gitignore: contiene finding del cliente"


def test_oracolo_sconosciuto_uso_errato(tmp_path):
    f = _factory(tmp_path, enabled=True)
    r = subprocess.run([sys.executable, MODULO, str(tmp_path), "--root", str(f), "--oracoli", "dast"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert r.returncode == 2 and b"dast" in r.stderr

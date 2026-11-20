"""Comparatore dei finding per identita' (EP-109 US-428 AC1, AC2, AC4; TSK-1043).

Esecuzioni finte nel formato del contratto d'ingresso: una base PRIMA e, per ogni caso, un DOPO
ottenuto per mutazione. Le sparizioni non legittime devono dare NON_VERIFICABILE, mai PASS."""
from __future__ import annotations

import copy
import json
import os
import subprocess
import sys

import pytest

QUI = os.path.dirname(os.path.abspath(__file__))
MODULO = os.path.normpath(os.path.join(QUI, "..", "security", "finding_compare.py"))
sys.path.insert(0, os.path.dirname(MODULO))
import finding_compare as fc  # noqa: E402

SCA = {"rule_id": "GHSA-aaaa", "package": "lodash", "version": "4.17.20"}
SAST = {"rule_id": "python.sqli", "path": "app/db.py", "symbol": "query"}


def base(**kw):
    e = {"tool": "finto", "tool_version": "1.0.0", "db_id": "db-2026-11-19", "commit": "c1",
         "findings": [dict(SCA), dict(SAST)],
         "inventario": {"lodash": "4.17.20"},
         "esiti_db": {"lodash@4.17.20": {"noto": True, "fixed_per": []}},
         "file_presenti": {"app/db.py": "blob-db", "app/main.py": "blob-main"},
         "simboli_presenti": ["app/db.py::query", "app/main.py::main"]}
    e.update(kw)
    return e


def dopo_senza(*rimossi, **kw):
    d = base(commit="c2", **kw)
    d["findings"] = [f for f in d["findings"] if f["rule_id"] not in rimossi]
    return d


def voce(rep, regola):
    [v] = [v for v in rep["voci"] if v["identita"][1] == regola]
    return v


# --- AC1: identita' e le due sole chiusure legittime ------------------------------------------

def test_identita_sca_e_sast():
    assert fc.identita("t", SCA) == ("t", "GHSA-aaaa", "lodash@4.17.20")
    assert fc.identita("t", SAST) == ("t", "python.sqli", "app/db.py::query")


def test_stesse_esecuzioni_pass_tutto_persistente():
    rep = fc.confronta(base(), base(commit="c2"))
    assert rep["esito"] == fc.PASS
    assert {v["esito"] for v in rep["voci"]} == {fc.PERSISTENTE}


def test_numero_di_riga_non_fa_parte_dell_identita():
    p, d = base(), base(commit="c2")
    p["findings"][1]["line"] = 10
    d["findings"][1]["line"] = 42
    assert fc.confronta(p, d)["esito"] == fc.PASS


def test_chiusura_legittima_simbolo_presente():
    rep = fc.confronta(base(), dopo_senza("python.sqli"))
    assert voce(rep, "python.sqli")["esito"] == fc.CHIUSO_SIMBOLO
    assert rep["esito"] == fc.PASS


def test_chiusura_legittima_versione_marcata_fixed():
    d = dopo_senza("GHSA-aaaa", inventario={"lodash": "4.17.21"},
                   esiti_db={"lodash@4.17.21": {"noto": True, "fixed_per": ["GHSA-aaaa"]}})
    rep = fc.confronta(base(), d)
    assert voce(rep, "GHSA-aaaa")["esito"] == fc.CHIUSO_FIXED
    assert rep["esito"] == fc.PASS


def test_finding_nuovo_fail():
    d = base(commit="c2")
    d["findings"].append({"rule_id": "python.xss", "path": "app/main.py", "symbol": "main"})
    rep = fc.confronta(base(), d)
    assert rep["esito"] == fc.FAIL and voce(rep, "python.xss")["esito"] == fc.NUOVO


def test_stessa_regola_altra_versione_e_lo_stesso_rischio_non_nuovo():
    d = base(commit="c2", inventario={"lodash": "4.17.21"})
    d["findings"][0]["version"] = "4.17.21"
    rep = fc.confronta(base(), d)
    v = voce(rep, "GHSA-aaaa")
    assert v["esito"] == fc.PERSISTENTE and v["identita_dopo"][2] == "lodash@4.17.21"
    assert rep["esito"] == fc.PASS


def test_seconda_istanza_dello_stesso_pacchetto_e_nuova():
    d = base(commit="c2")
    d["findings"].append(dict(SCA, version="3.0.0"))
    rep = fc.confronta(base(), d)
    assert rep["esito"] == fc.FAIL
    assert [v["identita"][2] for v in rep["voci"] if v["esito"] == fc.NUOVO] == ["lodash@3.0.0"]


# --- AC2: mutanti -> NON_VERIFICABILE ---------------------------------------------------------

def _nv(rep, regola, motivo):
    v = voce(rep, regola)
    assert v["esito"] == fc.NV and v["motivo"] == motivo, v
    assert rep["esito"] == fc.NON_VERIFICABILE


def test_file_cancellato():
    d = dopo_senza("python.sqli", file_presenti={"app/main.py": "blob-main"},
                   simboli_presenti=["app/main.py::main"])
    _nv(fc.confronta(base(), d), "python.sqli", fc.CANCELLATO)


def test_file_spostato():
    d = dopo_senza("python.sqli", file_presenti={"app/main.py": "blob-main", "app/altro.py": "blob-db"})
    _nv(fc.confronta(base(), d), "python.sqli", fc.SPOSTATO)


def test_file_vendorizzato():
    d = dopo_senza("python.sqli", file_presenti={"app/main.py": "blob-main", "vendor/app/db.py": "blob-db"})
    _nv(fc.confronta(base(), d), "python.sqli", fc.VENDORIZZATO)


def test_prefisso_di_vendoring_configurabile():
    d = dopo_senza("python.sqli", file_presenti={"app/main.py": "blob-main", "libs/db.py": "blob-db"})
    rep = fc.confronta(base(), d, vendor=("libs/",))
    _nv(rep, "python.sqli", fc.VENDORIZZATO)


def test_simbolo_assente():
    d = dopo_senza("python.sqli", simboli_presenti=["app/main.py::main"])
    _nv(fc.confronta(base(), d), "python.sqli", fc.SIMBOLO_ASSENTE)


def test_pacchetto_rimosso_o_vendorizzato():
    d = dopo_senza("GHSA-aaaa", inventario={})
    _nv(fc.confronta(base(), d), "GHSA-aaaa", fc.PACCHETTO_RIMOSSO)


def test_downgrade_a_versione_ignota_al_db():
    d = dopo_senza("GHSA-aaaa", inventario={"lodash": "4.0.0-fork"}, esiti_db={})
    _nv(fc.confronta(base(), d), "GHSA-aaaa", fc.VERSIONE_IGNOTA)


def test_versione_nota_ma_non_fixed():
    d = dopo_senza("GHSA-aaaa", inventario={"lodash": "4.16.0"},
                   esiti_db={"lodash@4.16.0": {"noto": True, "fixed_per": ["GHSA-altro"]}})
    _nv(fc.confronta(base(), d), "GHSA-aaaa", fc.VERSIONE_NON_FIXED)


def test_sparito_a_versione_invariata():
    _nv(fc.confronta(base(), dopo_senza("GHSA-aaaa")), "GHSA-aaaa", fc.SPARITO_INVARIATO)


def test_nuovo_prevale_su_non_verificabile():
    d = dopo_senza("GHSA-aaaa")
    d["findings"].append({"rule_id": "python.xss", "path": "app/main.py", "symbol": "main"})
    assert fc.confronta(base(), d)["esito"] == fc.FAIL


# --- confrontabilita' (A13) e contratto -------------------------------------------------------

def test_db_cambiato_a_commit_fermo_e_riscansione_non_decisione():
    rep = fc.confronta(base(), base(db_id="db-2026-11-20"))
    assert rep["esito"] == fc.NON_VERIFICABILE and rep["motivo"] == "riscansione"


@pytest.mark.parametrize("campo,valore", [("tool", "altro"), ("tool_version", "2.0.0"), ("db_id", "db-x")])
def test_esecuzioni_non_confrontabili(campo, valore):
    rep = fc.confronta(base(), base(commit="c2", **{campo: valore}))
    assert rep["esito"] == fc.NON_VERIFICABILE and rep["motivo"] == "non_confrontabili"


@pytest.mark.parametrize("mutazione", [
    lambda e: e.pop("db_id"),
    lambda e: e.update(findings="x"),
    lambda e: e["findings"].append({"rule_id": "r"}),
    lambda e: e["findings"].append({"rule_id": "r", "package": "p", "path": "x"}),
    lambda e: e["findings"].append({"rule_id": "r", "package": "p"}),
    lambda e: e["findings"].append({"package": "p", "version": "1"}),
])
def test_esecuzione_malformata_non_verificabile(mutazione):
    d = base(commit="c2")
    mutazione(d)
    rep = fc.confronta(base(), d)
    assert rep["esito"] == fc.NON_VERIFICABILE and rep["motivo"] == "esecuzione_non_valida"


def test_confronto_non_muta_gli_ingressi():
    p, d = base(), dopo_senza("python.sqli")
    p0, d0 = copy.deepcopy(p), copy.deepcopy(d)
    fc.confronta(p, d)
    assert (p, d) == (p0, d0)


# --- CLI e AC4: nessun contatore «risolti» ----------------------------------------------------

def _cli(tmp_path, prima, dopo, *args):
    a, b = tmp_path / "prima.json", tmp_path / "dopo.json"
    a.write_text(json.dumps(prima), encoding="utf-8")
    b.write_text(json.dumps(dopo), encoding="utf-8")
    r = subprocess.run([sys.executable, MODULO, str(a), str(b)] + list(args),
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return r.returncode, r.stdout.decode()


@pytest.mark.parametrize("dopo,rc", [
    (lambda: base(commit="c2"), 0),
    (lambda: dict(base(commit="c2"), findings=base()["findings"] + [{"rule_id": "n", "path": "app/main.py"}]), 1),
    (lambda: dopo_senza("GHSA-aaaa"), 3),
])
def test_cli_exit_code(tmp_path, dopo, rc):
    assert _cli(tmp_path, base(), dopo())[0] == rc


def test_cli_file_illeggibile_non_verificabile(tmp_path):
    a = tmp_path / "prima.json"
    a.write_text("{rotto", encoding="utf-8")
    r = subprocess.run([sys.executable, MODULO, str(a), str(a)], stdout=subprocess.PIPE)
    assert r.returncode == 3


@pytest.mark.parametrize("args", [(), ("--json",)])
def test_nessun_contatore_di_risolti(tmp_path, args):
    d = dopo_senza("python.sqli", inventario={"lodash": "4.17.21"},
                   esiti_db={"lodash@4.17.21": {"noto": True, "fixed_per": ["GHSA-aaaa"]}})
    d["findings"] = []
    _, out = _cli(tmp_path, base(), d, *args)
    assert "risolt" not in out.lower() and "resolved" not in out.lower()
    if args:
        rep = json.loads(out)
        assert not any(isinstance(v, int) for v in rep.values()), "nessun conteggio nel report"


def test_sorgente_senza_contatore_di_risolti():
    with open(MODULO, encoding="utf-8") as fh:
        righe = [r for r in fh if "risolt" in r.lower()]
    assert all("Nessun contatore" in r or "non e' un rischio risolto" in r for r in righe), righe


# --- CQRL iter-1 ------------------------------------------------------------------------------

def test_sast_senza_simbolo_e_file_presente_non_e_una_chiusura():
    p = base(findings=[{"rule_id": "sqli", "path": "app/db.py"}])
    d = base(commit="c2", findings=[], file_presenti={"app/db.py": "altro-blob"})
    rep = fc.confronta(p, d)
    assert rep["esito"] == fc.NON_VERIFICABILE
    assert voce(rep, "sqli")["motivo"] == fc.SIMBOLO_NON_DICHIARATO


@pytest.mark.parametrize("campo,valore", [
    ("esiti_db", {"lodash@4.17.21": {"noto": "false", "fixed_per": ["GHSA-aaaa"]}}),
    ("esiti_db", {"lodash@4.17.21": {"noto": True, "fixed_per": "GHSA-aaaa"}}),
    ("esiti_db", []),
    ("inventario", {"lodash": 4}),
    ("file_presenti", ["app/db.py"]),
    ("simboli_presenti", "app/db.py::query"),
])
def test_sezioni_malformate_non_diventano_chiusure(campo, valore):
    d = dopo_senza("GHSA-aaaa", inventario={"lodash": "4.17.21"})
    d[campo] = valore
    rep = fc.confronta(base(), d)
    assert rep["esito"] == fc.NON_VERIFICABILE and rep["motivo"] == "esecuzione_non_valida"


def test_eccezione_interna_e_non_verificabile_non_fail(tmp_path, monkeypatch):
    a = tmp_path / "p.json"
    a.write_text(json.dumps(base()))
    monkeypatch.setattr(fc, "confronta", lambda *x, **k: 1 / 0)
    assert fc.main([str(a), str(a)]) == 3

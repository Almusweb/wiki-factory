"""La pila di /security-scan dipende dall'interfaccia di contratto_segreti, non dal secrets_guard del master.

Un modulo dei segreti finto, che espone solo i quattro nomi dell'interfaccia, prende il posto di
`secrets_guard`: la pila lo usa, solleva e cattura la sua eccezione, e non tocca il modulo vero."""
from __future__ import annotations

import os
import subprocess
import sys
import types

import pytest

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.normpath(os.path.join(QUI, "..", ".."))
sys.path.insert(0, os.path.join(RADICE, "tools", "security"))
import contratto_segreti as cs  # noqa: E402
import fix_gate  # noqa: E402
import oracolo_statico  # noqa: E402
import rescan  # noqa: E402
import sca_guard  # noqa: E402
import secrets_guard  # noqa: E402
import security_scan as ss  # noqa: E402


class _Esito(object):
    def __init__(self, stato, messaggio, findings=()):
        self.stato, self.messaggio, self.findings = stato, messaggio, list(findings)


def _finto(motivo="fuori perimetro (finto)", stato="OK"):
    """Modulo dei segreti di una derivata: solo l'interfaccia, nomi e valori diversi dal master."""
    m = types.ModuleType("secrets_guard")
    chiamate = []

    class RifiutoDerivata(Exception):
        pass

    def guardia_storia(code_path, root):
        chiamate.append(("guardia", code_path))
        return motivo

    def scan_storia(code_path, root):
        chiamate.append(("scan", code_path))
        if motivo:
            raise RifiutoDerivata(motivo)
        return _Esito(stato, "pulita", [{"RuleID": "r", "File": "f", "StartLine": 1, "Commit": "c"}])

    m.Rifiuto, m.guardia_storia, m.scan_storia, m.PASS = RifiutoDerivata, guardia_storia, scan_storia, "OK"
    m.chiamate = chiamate
    return m


@pytest.fixture
def finto(monkeypatch):
    m = _finto()
    monkeypatch.setitem(sys.modules, "secrets_guard", m)
    return m


def test_il_master_soddisfa_il_contratto():
    assert cs.mancanti(secrets_guard) == []
    assert cs.Rifiuto is secrets_guard.Rifiuto and cs.PASS == secrets_guard.PASS


def test_nome_mancante_lo_dice(monkeypatch):
    m = types.ModuleType("secrets_guard")
    m.Rifiuto = type("R", (Exception,), {})
    monkeypatch.setitem(sys.modules, "secrets_guard", m)
    assert cs.mancanti() == ["guardia_storia", "scan_storia", "PASS"]
    with pytest.raises(AttributeError, match="guardia_storia"):
        cs.guardia_storia


@pytest.mark.parametrize("chiama", [
    lambda: sca_guard.esegui("/x", "."),
    lambda: oracolo_statico.esegui(None, "/x", "."),
    lambda: fix_gate.verifica("/x", "."),
    lambda: rescan.esegui("/x", "."),
], ids=["sca_guard", "oracolo_statico", "fix_gate", "rescan"])
def test_la_pila_usa_guardia_e_rifiuto_della_derivata(finto, chiama):
    with pytest.raises(finto.Rifiuto, match="finto"):
        chiama()
    assert finto.chiamate == [("guardia", "/x")]
    assert not issubclass(finto.Rifiuto, secrets_guard.Rifiuto)


def test_security_scan_usa_scan_storia_e_pass_della_derivata(monkeypatch):
    m = _finto(motivo=None)
    monkeypatch.setitem(sys.modules, "secrets_guard", m)
    r = ss._segreti("/x", ".")
    assert r["esito"] == "OK" and r["motivo"] is None and r["voci"][0]["id"] == "r"
    assert m.chiamate == [("scan", "/x")]


def test_security_scan_cattura_il_rifiuto_della_derivata(tmp_path, finto):
    f = tmp_path / "factory"
    f.mkdir()
    for c in (("init", "-q"), ("config", "user.email", "t@t"), ("config", "user.name", "t"),
              ("config", "commit.gpgsign", "false")):
        subprocess.run(["git", "-C", str(f)] + list(c), check=True)
    (f / "factory.config.yaml").write_text("security_scan:\n  enabled: true\n")
    subprocess.run(["git", "-C", str(f), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(f), "commit", "-q", "-m", "c", "--no-verify"], check=True)
    subprocess.run(["git", "-C", str(f), "update-ref", "refs/remotes/origin/main", "HEAD"], check=True)
    rep = ss.esegui(str(tmp_path), str(f), oracoli=("segreti",), registro={"segreti": ss._segreti})
    assert rep["esito"] == ss.NON_VERIFICABILE
    assert rep["oracoli"][0]["motivo"].startswith("rifiutato:")

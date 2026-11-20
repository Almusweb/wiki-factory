"""Identita' degli scanner (EP-109 US-424, TSK-1036, decisione D7 = percorso pinnato con hash).

Scanner finti: script che stampano una versione e, se eseguiti, lasciano un marcatore su disco, cosi'
si prova anche che un binario non identificato non viene eseguito. I pin stanno in un repo git
temporaneo con `refs/remotes/origin/main` impostato, perche' il modulo li legge dal merge-base."""
from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys

import pytest

QUI = os.path.dirname(os.path.abspath(__file__))
MODULO = os.path.normpath(os.path.join(QUI, "..", "security", "scanner_identity.py"))
sys.path.insert(0, os.path.dirname(MODULO))
import scanner_identity as si  # noqa: E402

PATH_AGENTICO = "/usr/bin:/bin:/usr/sbin:/sbin"
CONFIG = "scanner_identity:\n  pins: security/scanner-pins.json\n  ref_protetto: origin/main\n"


def _git(repo, *a):
    r = subprocess.run(["git", "-C", str(repo)] + list(a), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert r.returncode == 0, r.stderr
    return r.stdout.decode().strip()


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    for c in (("init", "-q"), ("config", "user.email", "t@t"), ("config", "user.name", "t"),
              ("config", "commit.gpgsign", "false")):
        _git(r, *c)
    (r / "factory.config.yaml").write_text(CONFIG, encoding="utf-8")
    _git(r, "add", "-A")
    _git(r, "commit", "-q", "-m", "base", "--no-verify")
    _git(r, "update-ref", "refs/remotes/origin/main", "HEAD")
    return r


def pinna(repo, dati, protetto=True):
    """Committa il file dei pin; con protetto=True sposta anche origin/main sul commit."""
    (repo / "security").mkdir(exist_ok=True)
    (repo / "security" / "scanner-pins.json").write_text(json.dumps(dati), encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "pin", "--no-verify")
    if protetto:
        _git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")


def finto(cartella, nome="gitleaks", versione="8.30.1", extra=""):
    """Scanner finto: stampa la versione e scrive <nome>.eseguito accanto a se'."""
    cartella.mkdir(parents=True, exist_ok=True)
    p = cartella / nome
    marcatore = cartella / (nome + ".eseguito")
    p.write_text("#!/bin/sh\necho x >> '%s'\necho 'v%s'\n%s" % (marcatore, versione, extra), encoding="utf-8")
    p.chmod(p.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return p, marcatore


def pin_di(path, versione="8.30.1"):
    return {"path": str(path), "sha256": si.sha256_file(os.path.realpath(str(path))), "version": versione}


def cli(repo, *args, path=PATH_AGENTICO):
    """CLI con ambiente vuoto e PATH agentico (`env -i PATH=...`), come le sessioni ridotte."""
    r = subprocess.run([sys.executable, MODULO, "--root", str(repo)] + list(args),
                       env={"PATH": path}, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return r.returncode, r.stdout.decode(), r.stderr.decode()


# --- AC1: esito con pin, ambiente agentico ----------------------------------------------------

def test_pin_valido_identifica_senza_consultare_il_path(repo, tmp_path):
    exe, _ = finto(tmp_path / "fuori-dal-path")
    pinna(repo, {"gitleaks": [pin_di(exe)]})
    rc, out, _ = cli(repo, "--json", "gitleaks")
    assert rc == 0, out
    rep = json.loads(out)[0]
    assert rep["stato"] == si.IDENTIFICATO
    assert rep["realpath"] == os.path.realpath(str(exe))
    assert rep["version"] == "8.30.1"
    assert rep["sha256"] == si.sha256_file(str(exe))
    assert rep["cosa_si_hasha"] == si.COSA_SI_HASHA[si.BINARIO]


def test_binario_sostituito_stesso_nome_altro_sha_divergente_e_non_eseguito(repo, tmp_path):
    exe, marcatore = finto(tmp_path / "bin")
    pinna(repo, {"gitleaks": [pin_di(exe)]})
    exe.write_text(exe.read_text(encoding="utf-8") + "# sostituito\n", encoding="utf-8")   # stesso nome, altro sha256
    rc, out, _ = cli(repo, "--json", "gitleaks")
    assert rc == 3
    rep = json.loads(out)[0]
    assert rep["stato"] == si.NON_VERIFICABILE and rep["motivo"] == si.DIVERGENTE
    assert rep["sha256"] != rep["pin"]["sha256"]
    assert not marcatore.exists(), "un binario non identificato non si esegue"


def test_sha_coincide_ma_versione_diversa_e_divergente(repo, tmp_path):
    exe, _ = finto(tmp_path / "bin")
    pinna(repo, {"gitleaks": [pin_di(exe, versione="9.9.9")]})
    e = si.identifica("gitleaks", str(repo))
    assert e.motivo == si.DIVERGENTE and "versione 8.30.1, fissata 9.9.9" in e.messaggio


def test_percorso_fissato_mancante_e_assente(repo, tmp_path):
    exe, _ = finto(tmp_path / "bin")
    voce = pin_di(exe)
    exe.unlink()
    pinna(repo, {"gitleaks": [voce]})
    rc, out, _ = cli(repo, "--json", "gitleaks")
    assert rc == 3 and json.loads(out)[0]["motivo"] == si.ASSENTE


def test_piu_voci_la_prima_esistente_e_identica_vince(repo, tmp_path):
    exe, _ = finto(tmp_path / "bin")
    pinna(repo, {"gitleaks": [{"path": "/inesistente/gitleaks", "sha256": "0" * 64}, pin_di(exe)]})
    assert si.identifica("gitleaks", str(repo)).identificato


# --- AC1: senza pin ---------------------------------------------------------------------------

def test_senza_pin_fuori_dal_path_non_raggiungibile(repo, tmp_path):
    exe, marcatore = finto(tmp_path / "homebrew")
    e = si.identifica("gitleaks", str(repo), percorsi_noti=[str(exe.parent)], env_path=PATH_AGENTICO)
    assert e.motivo == si.NON_RAGGIUNGIBILE and str(exe) in e.messaggio
    assert not marcatore.exists()


@pytest.mark.skipif(not os.path.isfile("/opt/homebrew/bin/gitleaks")
                    or shutil.which("gitleaks", path=PATH_AGENTICO),
                    reason="integrazione: serve gitleaks reale in /opt/homebrew/bin e fuori dal PATH agentico")
def test_integrazione_gitleaks_reale_fuori_dal_path_agentico(repo):
    rc, out, _ = cli(repo, "--json", "gitleaks")
    assert rc == 3 and json.loads(out)[0]["motivo"] == si.NON_RAGGIUNGIBILE


def test_senza_pin_ne_binario_assente(repo, tmp_path):
    vuota = tmp_path / "vuota"
    vuota.mkdir()
    e = si.identifica("trivy", str(repo), percorsi_noti=[], env_path=str(vuota))
    assert e.motivo == si.ASSENTE


def test_senza_pin_nel_path_non_fissata_e_non_eseguito(repo, tmp_path):
    exe, marcatore = finto(tmp_path / "bin", nome="osv-scanner")
    rc, out, _ = cli(repo, "--json", "osv-scanner", path=str(exe.parent) + ":" + PATH_AGENTICO)
    rep = json.loads(out)[0]
    assert rc == 3 and rep["motivo"] == si.NON_FISSATA
    assert rep["sha256"] == si.sha256_file(str(exe))   # misurato, non eseguito
    assert not marcatore.exists()


def test_tre_motivi_distinti():
    codici = {si.ASSENTE, si.NON_RAGGIUNGIBILE, si.DIVERGENTE}
    assert len(codici) == 3
    assert len({si.MOTIVI[c] for c in codici}) == 3
    assert si.MOTIVI[si.NON_RAGGIUNGIBILE] == "non raggiungibile dal PATH del processo"


# --- pin incompleti e provenienza dei pin -----------------------------------------------------

@pytest.mark.parametrize("voce", [
    {"path": "/x/gitleaks"},
    {"path": "/x/gitleaks", "sha256": "abc"},
    {"path": "relativo/gitleaks", "sha256": "0" * 64},
    "non un oggetto",
])
def test_pin_incompleto_non_e_un_pin(repo, voce):
    pinna(repo, {"gitleaks": [voce]})
    e = si.identifica("gitleaks", str(repo))
    assert e.stato == si.NON_VERIFICABILE and e.motivo == si.NON_FISSATA


def test_pin_solo_nel_working_tree_non_vale(repo, tmp_path):
    exe, _ = finto(tmp_path / "bin")
    (repo / "security").mkdir()
    (repo / "security" / "scanner-pins.json").write_text(json.dumps({"gitleaks": [pin_di(exe)]}), encoding="utf-8")
    e = si.identifica("gitleaks", str(repo), percorsi_noti=[], env_path=PATH_AGENTICO)
    assert not e.identificato


def test_pin_cambiato_solo_sul_branch_non_vale(repo, tmp_path):
    vero, _ = finto(tmp_path / "vero")
    pinna(repo, {"gitleaks": [pin_di(vero)]})
    sostituto, _ = finto(tmp_path / "sostituto", extra="# altro binario\n")
    pinna(repo, {"gitleaks": [pin_di(sostituto)]}, protetto=False)   # ripinnato sul branch
    e = si.identifica("gitleaks", str(repo))
    assert e.identificato and e.realpath == os.path.realpath(str(vero))


def test_ref_protetto_assente_nessun_pin(repo, tmp_path):
    exe, _ = finto(tmp_path / "bin")
    pinna(repo, {"gitleaks": [pin_di(exe)]})
    _git(repo, "update-ref", "-d", "refs/remotes/origin/main")
    e = si.identifica("gitleaks", str(repo), percorsi_noti=[], env_path=PATH_AGENTICO)
    assert not e.identificato and "non risolt" in e.messaggio


def test_pin_json_non_valido_nessun_pin(repo):
    (repo / "security").mkdir()
    (repo / "security" / "scanner-pins.json").write_text("{non json", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "rotto", "--no-verify")
    _git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    e = si.identifica("gitleaks", str(repo), percorsi_noti=[], env_path=PATH_AGENTICO)
    assert not e.identificato and "non e' JSON valido" in e.messaggio


# --- AC2: cosa si hasha, per scanner ----------------------------------------------------------

def test_tabella_cosa_si_hasha_copre_i_quattro_scanner():
    assert set(si.SCANNER) == {"gitleaks", "osv-scanner", "trivy", "semgrep"}
    for nome, d in si.SCANNER.items():
        assert d["tipo"] in si.COSA_SI_HASHA, nome
    assert si.SCANNER["semgrep"]["tipo"] == si.ENTRYPOINT_PYTHON
    assert "parziale" in si.COSA_SI_HASHA[si.ENTRYPOINT_PYTHON]


def _semgrep_finto(radice):
    """Prefisso stile pip: bin/python3 (file vero), bin/semgrep con shebang, dist-info con RECORD."""
    (radice / "bin").mkdir(parents=True)
    interprete = radice / "bin" / "python3"
    interprete.write_text("#!/bin/sh\necho interprete finto\n", encoding="utf-8")
    interprete.chmod(0o755)
    dist = radice / "lib" / "python3.9" / "site-packages" / "semgrep-1.95.0.dist-info"
    dist.mkdir(parents=True)
    (dist / "RECORD").write_text("semgrep/bin/semgrep-core,sha256=abc,123\n", encoding="utf-8")
    (dist / "METADATA").write_text("Name: semgrep\nVersion: 1.95.0\n", encoding="utf-8")
    core = radice / "lib" / "python3.9" / "site-packages" / "semgrep" / "bin" / "semgrep-core"
    core.parent.mkdir(parents=True)
    core.write_bytes(b"\xcf\xfa\xed\xfe motore finto")
    entry = radice / "bin" / "semgrep"
    entry.write_text("#!%s\nimport semgrep\n" % interprete, encoding="utf-8")
    entry.chmod(0o755)
    return entry, dist / "RECORD"


def test_semgrep_digest_composto_di_tre_artefatti(repo, tmp_path):
    entry, record = _semgrep_finto(tmp_path / "venv")
    real, sha, artefatti, errore = si.misura("semgrep", str(entry))
    assert errore is None
    assert [a["ruolo"] for a in artefatti] == ["entrypoint", "interprete", "motore", "record"]
    pinna(repo, {"semgrep": [{"path": str(entry), "sha256": sha}]})
    assert si.identifica("semgrep", str(repo)).identificato
    record.write_text("semgrep/bin/semgrep-core,sha256=def,123\n", encoding="utf-8")   # pacchetto cambiato
    e = si.identifica("semgrep", str(repo))
    assert e.motivo == si.DIVERGENTE


def test_semgrep_senza_record_usa_metadata_come_homebrew(tmp_path):
    entry, record = _semgrep_finto(tmp_path / "venv")
    record.unlink()
    _, sha, artefatti, errore = si.misura("semgrep", str(entry))
    assert errore is None and [a["ruolo"] for a in artefatti][-1] == "metadata"


def test_semgrep_motore_cambiato_divergente(repo, tmp_path):
    entry, _ = _semgrep_finto(tmp_path / "venv")
    _, sha, _, _ = si.misura("semgrep", str(entry))
    pinna(repo, {"semgrep": [{"path": str(entry), "sha256": sha}]})
    core = next((tmp_path / "venv").rglob("semgrep-core"))
    core.write_bytes(b"altro motore")
    assert si.identifica("semgrep", str(repo)).motivo == si.DIVERGENTE


def test_semgrep_senza_motore_ne_manifest_divergente_non_identificato(repo, tmp_path):
    entry, record = _semgrep_finto(tmp_path / "venv")
    _, sha, _, _ = si.misura("semgrep", str(entry))
    pinna(repo, {"semgrep": [{"path": str(entry), "sha256": sha}]})
    next((tmp_path / "venv").rglob("semgrep-core")).unlink()
    e = si.identifica("semgrep", str(repo))
    assert e.motivo == si.DIVERGENTE and "incompleto" in e.messaggio


def test_semgrep_con_shebang_env_non_identificabile(tmp_path):
    entry, _ = _semgrep_finto(tmp_path / "venv")
    entry.write_text("#!/usr/bin/env python3\nimport semgrep\n", encoding="utf-8")
    _, sha, _, errore = si.misura("semgrep", str(entry))
    assert sha is None and "shebang" in errore


def test_ref_protetto_head_nel_working_tree_non_fa_valere_i_pin_del_branch(repo, tmp_path):
    """Mutante CQRL iter-1 (F1): il branch ripinna un binario sostituito e mette ref_protetto: HEAD
    nel factory.config.yaml su disco, senza committarlo. I pin restano quelli dell'ancora."""
    vero, _ = finto(tmp_path / "vero")
    pinna(repo, {"gitleaks": [pin_di(vero)]})
    vero.write_text(vero.read_text(encoding="utf-8") + "# sostituito\n", encoding="utf-8")
    pinna(repo, {"gitleaks": [pin_di(vero)]}, protetto=False)
    (repo / "factory.config.yaml").write_text(CONFIG.replace("origin/main", "HEAD"), encoding="utf-8")
    e = si.identifica("gitleaks", str(repo))
    assert e.motivo == si.DIVERGENTE


# --- misura -----------------------------------------------------------------------------------

def test_misura_produce_un_pin_che_identifica(repo, tmp_path):
    exe, _ = finto(tmp_path / "bin")
    rc, out, _ = cli(repo, "--misura", "gitleaks", "--path", str(exe), "--nota", "test")
    assert rc == 0
    proposta = json.loads(out)
    pinna(repo, {"gitleaks": proposta["gitleaks"]})
    e = si.identifica("gitleaks", str(repo))
    assert e.identificato and e.pin["nota"] == "test"


def test_scanner_sconosciuto_e_uso_errato(repo):
    rc, _, err = cli(repo, "nmap")
    assert rc == 2 and "sconosciuto" in err


def test_semgrep_in_un_venv_con_python_symlink(repo, tmp_path):
    """pipx e venv: bin/python3 e' un symlink al Python di sistema, il pacchetto sta nel venv."""
    venv = tmp_path / "venv"
    (venv / "bin").mkdir(parents=True)
    os.symlink(os.path.realpath(sys.executable), str(venv / "bin" / "python3"))
    dist = venv / "lib" / "python3.9" / "site-packages" / "semgrep-1.95.0.dist-info"
    dist.mkdir(parents=True)
    (dist / "RECORD").write_text("semgrep/__init__.py,sha256=x,1\n", encoding="utf-8")
    core = venv / "lib" / "python3.9" / "site-packages" / "semgrep" / "bin" / "semgrep-core"
    core.parent.mkdir(parents=True)
    core.write_bytes(b"motore")
    entry = venv / "bin" / "semgrep"
    entry.write_text("#!%s\nprint('1.95.0')\n" % (venv / "bin" / "python3"), encoding="utf-8")
    entry.chmod(0o755)
    real, sha, artefatti, errore = si.misura("semgrep", str(entry))
    assert errore is None, errore
    ruoli = {a["ruolo"]: a["path"] for a in artefatti}
    assert ruoli["interprete"] == os.path.realpath(sys.executable)   # si hasha il file vero
    assert ruoli["record"] == os.path.realpath(str(dist / "RECORD"))  # trovato nel venv
    pinna(repo, {"semgrep": [{"path": str(entry), "sha256": sha, "version": "1.95.0"}]})
    e = si.identifica("semgrep", str(repo))
    assert e.identificato and e.version == "1.95.0"

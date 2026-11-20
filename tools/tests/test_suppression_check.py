"""Diff-check sulle soppressioni (EP-109 US-428 AC3, TSK-1044; mutanti di A18).

Repo git temporaneo: il commit base e' `origin/main` (ref protetto), il branch aggiunge commit. Le
soppressioni si cercano nel diff merge-base..HEAD; i record di accettazione valgono solo dal merge-base."""
from __future__ import annotations

import datetime
import json
import os
import subprocess
import sys

import pytest

QUI = os.path.dirname(os.path.abspath(__file__))
MODULO = os.path.normpath(os.path.join(QUI, "..", "security", "suppression_check.py"))
sys.path.insert(0, os.path.dirname(MODULO))
import suppression_check as sc  # noqa: E402

OGGI = datetime.date(2026, 11, 19)
ACC = "security/suppression-accettazioni.json"


def _git(repo, *a):
    r = subprocess.run(["git", "-C", str(repo)] + list(a), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert r.returncode == 0, r.stderr
    return r.stdout.decode().strip()


def scrivi(repo, rel, testo):
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(testo, encoding="utf-8")


def commit(repo, msg="c", protetto=False):
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "--allow-empty", "-m", msg, "--no-verify")
    if protetto:
        _git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    for c in (("init", "-q"), ("config", "user.email", "t@t"), ("config", "user.name", "t"),
              ("config", "commit.gpgsign", "false")):
        _git(r, *c)
    scrivi(r, "app/db.py", "def query(x):\n    return run('select ' + x)\n")
    scrivi(r, "infra/.trivyignore", "# vecchia\nAVD-AWS-0001\n")
    commit(r, "base", protetto=True)
    return r


def esito(repo, **kw):
    return sc.controlla(str(repo), oggi=OGGI, **kw)


def record(**kw):
    r = {"path": "app/db.py", "tipo": "nosemgrep", "testo": "return run('select ' + x)  # nosemgrep",
         "motivo": "falso positivo: x e' una costante", "scadenza": "2027-02-17",
         "accettato_da": "maintainer", "riferimento_gate": "PR #0"}
    r.update(kw)
    return r


def con_nosemgrep(repo):
    scrivi(repo, "app/db.py", "def query(x):\n    return run('select ' + x)  # nosemgrep\n")


# --- nessuna soppressione ---------------------------------------------------------------------

def test_branch_senza_soppressioni_pass(repo):
    scrivi(repo, "app/db.py", "def query(x):\n    return run('select ?', x)\n")
    commit(repo)
    rep = esito(repo)
    assert rep["esito"] == sc.PASS and rep["soppressioni"] == []


def test_soppressione_gia_nel_base_non_e_nuova(repo):
    scrivi(repo, "app/other.py", "x = 1\n")
    commit(repo)
    assert esito(repo)["esito"] == sc.PASS   # .trivyignore del base non e' nel diff


def test_rimuovere_una_soppressione_pass(repo):
    scrivi(repo, "infra/.trivyignore", "# vecchia\n")
    commit(repo)
    assert esito(repo)["esito"] == sc.PASS


# --- soppressione aggiunta -> FAIL ------------------------------------------------------------

@pytest.mark.parametrize("riga,tipo", [
    ("    return run(x)  # nosemgrep", "nosemgrep"),
    ("    return run(x)  # nosemgrep: python.sqli", "nosemgrep"),
    ("    return run(x)  # nosec B608", "nosec"),
    ("    q := run(x) // #nosec G201", "nosec"),
    ("    token = 'abc'  # gitleaks:allow", "gitleaks:allow"),
    ("  -- trivy:ignore:AVD-DS-0002", "trivy:ignore"),
    ("  <!-- NOSEMGREP -->", "nosemgrep"),
])
def test_soppressione_inline_aggiunta_fail(repo, riga, tipo):
    scrivi(repo, "app/db.py", "def query(x):\n%s\n" % riga)
    commit(repo)
    rep = esito(repo)
    assert rep["esito"] == sc.FAIL
    assert [s["tipo"] for s in rep["soppressioni"]] == [tipo]
    assert rep["soppressioni"][0]["path"] == "app/db.py"


@pytest.mark.parametrize("riga", [
    "    nosec = True",                       # non in un commento
    "    # nosecurity review",                 # parola diversa
    "    msg = 'usa nosemgrep con cautela'",   # stringa, nessun marcatore di commento
])
def test_parola_fuori_da_un_commento_o_diversa_non_conta(repo, riga):
    scrivi(repo, "app/db.py", "def query(x):\n%s\n" % riga)
    commit(repo)
    assert esito(repo)["esito"] == sc.PASS


@pytest.mark.parametrize("rel,riga", [
    ("infra/.trivyignore", "AVD-AWS-0002"),
    ("deploy/.trivyignore.yaml", "vulnerabilities:"),
    (".gitleaksignore", "abc123:app/db.py:generic-api-key:2"),
    ("sub/dir/.semgrepignore", "app/"),
    ("osv-scanner.toml", "[[IgnoredVulns]]"),
    ("osv-scanner.toml", "[[PackageOverrides]]"),
])
def test_riga_aggiunta_a_un_file_di_soppressioni_fail(repo, rel, riga):
    vecchio = (repo / rel).read_text() if (repo / rel).exists() else ""
    scrivi(repo, rel, vecchio + riga + "\n")
    commit(repo)
    rep = esito(repo)
    assert rep["esito"] == sc.FAIL
    assert [(s["path"], s["testo"]) for s in rep["soppressioni"]] == [(rel, riga)]


def test_commenti_e_righe_vuote_nei_file_di_soppressioni_non_contano(repo):
    scrivi(repo, "infra/.trivyignore", "# vecchia\nAVD-AWS-0001\n\n# solo un commento\n")
    commit(repo)
    assert esito(repo)["esito"] == sc.PASS


def test_file_di_soppressioni_rinominato_o_spostato_conta_tutto(repo):
    (repo / "altrove").mkdir()
    _git(repo, "mv", "infra/.trivyignore", "altrove/.trivyignore")
    commit(repo)
    rep = esito(repo)
    assert rep["esito"] == sc.FAIL
    assert [s["testo"] for s in rep["soppressioni"]] == ["AVD-AWS-0001"]


def test_soppressione_in_un_commit_intermedio_poi_restata(repo):
    con_nosemgrep(repo)
    commit(repo, "aggiunge")
    scrivi(repo, "app/other.py", "y = 2\n")
    commit(repo, "altro")
    assert esito(repo)["esito"] == sc.FAIL


def test_riga_aggiunta_che_inizia_con_piu_piu_non_confonde_il_path(repo):
    scrivi(repo, "a.txt", "++ x\n")
    con_nosemgrep(repo)
    commit(repo)
    rep = esito(repo)
    assert [s["path"] for s in rep["soppressioni"]] == ["app/db.py"]


def test_path_non_ascii(repo):
    scrivi(repo, "app/caffè.py", "x = run(y)  # nosemgrep\n")
    commit(repo)
    assert [s["path"] for s in esito(repo)["soppressioni"]] == ["app/caffè.py"]


# --- record di accettazione -------------------------------------------------------------------

def test_record_al_merge_base_ammette_la_soppressione(repo):
    scrivi(repo, ACC, json.dumps([record()]))
    commit(repo, "accettazione sul ref protetto", protetto=True)
    con_nosemgrep(repo)
    commit(repo)
    rep = esito(repo)
    assert rep["esito"] == sc.PASS
    assert rep["soppressioni"][0]["accettata"] and rep["soppressioni"][0]["record"]["accettato_da"] == "maintainer"


def test_record_solo_sul_branch_non_vale(repo):
    con_nosemgrep(repo)
    scrivi(repo, ACC, json.dumps([record()]))
    commit(repo)
    rep = esito(repo)
    assert rep["esito"] == sc.FAIL and not rep["soppressioni"][0]["accettata"]


@pytest.mark.parametrize("mut", [
    {"scadenza": "2026-11-18"},
    {"scadenza": "domani"},
    {"accettato_da": ""},
    {"riferimento_gate": " "},
    {"testo": "altra riga  # nosemgrep"},
    {"path": "app/altro.py"},
    {"tipo": "nosec"},
])
def test_record_scaduto_incompleto_o_diverso_non_vale(repo, mut):
    scrivi(repo, ACC, json.dumps([record(**mut)]))
    commit(repo, "accettazione", protetto=True)
    con_nosemgrep(repo)
    commit(repo)
    assert esito(repo)["esito"] == sc.FAIL


def test_record_in_json_non_valido_nessuna_accettazione(repo):
    scrivi(repo, ACC, "{rotto")
    commit(repo, "accettazione", protetto=True)
    con_nosemgrep(repo)
    commit(repo)
    rep = esito(repo)
    assert rep["esito"] == sc.FAIL and "non e' JSON valido" in rep["spiegazione"]


def test_record_con_scadenza_futura_per_la_cli(repo):
    scrivi(repo, ACC, json.dumps([record(scadenza="2999-12-31")]))
    commit(repo, "accettazione", protetto=True)
    con_nosemgrep(repo)
    commit(repo)
    assert _cli(repo)[0] == 0


def test_path_delle_accettazioni_dalla_config(repo):
    scrivi(repo, "factory.config.yaml", "suppression_check:\n  accettazioni: sec/acc.json\n  ref_protetto: origin/main\n")
    scrivi(repo, "sec/acc.json", json.dumps([record()]))
    commit(repo, "config", protetto=True)
    con_nosemgrep(repo)
    commit(repo)
    assert esito(repo)["esito"] == sc.PASS


# --- NON_VERIFICABILE e CLI -------------------------------------------------------------------

def test_ref_protetto_non_risolto_non_verificabile(repo):
    con_nosemgrep(repo)
    commit(repo)
    _git(repo, "update-ref", "-d", "refs/remotes/origin/main")
    assert esito(repo)["esito"] == sc.NON_VERIFICABILE


def test_cartella_non_git_non_verificabile(tmp_path):
    assert sc.controlla(str(tmp_path), oggi=OGGI)["esito"] == sc.NON_VERIFICABILE


def _cli(repo, *args):
    r = subprocess.run([sys.executable, MODULO, "--root", str(repo)] + list(args),
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return r.returncode, r.stdout.decode()


def test_cli_exit_code_e_json(repo):
    assert _cli(repo)[0] == 0
    con_nosemgrep(repo)
    commit(repo)
    rc, out = _cli(repo, "--json")
    assert rc == 1 and json.loads(out)["soppressioni"][0]["tipo"] == "nosemgrep"
    rc, out = _cli(repo, "--ref", "refs/inesistente")
    assert rc == 3 and "NON_VERIFICABILE" in out


# --- CQRL iter-1 ------------------------------------------------------------------------------

def test_ref_protetto_head_nel_working_tree_non_svuota_il_diff(repo):
    """F1: `ref_protetto: HEAD` non committato renderebbe il diff vuoto; si legge dall'ancora."""
    con_nosemgrep(repo)
    commit(repo)
    scrivi(repo, "factory.config.yaml", "suppression_check:\n  ref_protetto: HEAD\n")
    assert esito(repo, richiedi_pulito=False)["esito"] == sc.FAIL
    assert esito(repo)["esito"] == sc.NON_VERIFICABILE   # e il working tree sporco non da' PASS


def test_ancora_assente_non_verificabile(repo):
    _git(repo, "update-ref", "-d", "refs/remotes/origin/main")
    assert esito(repo)["esito"] == sc.NON_VERIFICABILE


def test_attributo_binary_non_nasconde_le_righe(repo):
    """F2: `.trivyignore binary` in .gitattributes farebbe stampare «Binary files differ»."""
    scrivi(repo, ".gitattributes", ".trivyignore binary\n")
    scrivi(repo, "infra/.trivyignore", "# vecchia\nAVD-AWS-0001\nCVE-2024-0001\n")
    commit(repo)
    assert [s["testo"] for s in esito(repo)["soppressioni"]] == ["CVE-2024-0001"]


def test_nul_nel_file_non_nasconde_le_righe(repo):
    (repo / "infra" / ".trivyignore").write_bytes(b"# vecchia\nAVD-AWS-0001\nCVE-2024-0002\n\x00\n")
    commit(repo)
    assert "CVE-2024-0002" in [s["testo"] for s in esito(repo)["soppressioni"]]


@pytest.mark.parametrize("cartella", ['we"ird', "con\\barra", "tab\tqui"])
def test_path_quotati_da_git(repo, cartella):
    """F3: git quota in stile C i path con virgolette, barre rovesciate o tab."""
    scrivi(repo, cartella + "/.trivyignore", "CVE-2024-0003\n")
    commit(repo)
    rep = esito(repo)
    assert [(s["path"], s["tipo"]) for s in rep["soppressioni"]] == [(cartella + "/.trivyignore", ".trivyignore")]


@pytest.mark.parametrize("riga", [
    "    return run(x)  # nosem",
    " * nosemgrep: python.sqli",
    "    % nosec",
])
def test_alias_e_commenti_di_continuazione(repo, riga):
    """F4: `# nosem` e' l'alias di semgrep; righe di continuazione di un blocco e commenti `%`."""
    scrivi(repo, "app/db.py", "def query(x):\n%s\n" % riga)
    commit(repo)
    assert esito(repo)["esito"] == sc.FAIL


def test_un_record_copre_una_sola_riga(repo):
    """F5: due righe identiche con un solo record: la seconda resta non accettata."""
    riga = "    return run('select ' + x)  # nosemgrep"
    scrivi(repo, ACC, json.dumps([record(testo=riga.strip())]))
    commit(repo, "accettazione", protetto=True)
    scrivi(repo, "app/db.py", "def query(x):\n%s\n%s\n" % (riga, riga))
    commit(repo)
    rep = esito(repo)
    assert rep["esito"] == sc.FAIL and [s["accettata"] for s in rep["soppressioni"]] == [True, False]


def test_cli_senza_flag_oggi(repo):
    """F8: nessun flag nascosto per far tornare validi record scaduti."""
    rc, _ = _cli(repo, "--oggi", "2000-01-01")
    assert rc == 2


@pytest.mark.parametrize("opzione", ["diff.noprefix", "diff.mnemonicPrefix"])
def test_config_diff_dell_utente_non_cambia_il_parsing(repo, opzione):
    """F9: con diff.noprefix i path non avrebbero `b/`."""
    _git(repo, "config", opzione, "true")
    con_nosemgrep(repo)
    commit(repo)
    assert [s["path"] for s in esito(repo)["soppressioni"]] == ["app/db.py"]


# --- CQRL iter-2 ------------------------------------------------------------------------------

@pytest.mark.parametrize("cartella", ["my dir", 'a "b'])
def test_path_con_spazio_header_con_tab_finale(repo, cartella):
    """N1: con uno spazio nel path git chiude l'intestazione +++ con un TAB."""
    scrivi(repo, cartella + "/.trivyignore", "CVE-1\n")
    commit(repo)
    rep = esito(repo)
    assert rep["esito"] == sc.FAIL
    assert [(s["path"], s["tipo"]) for s in rep["soppressioni"]] == [(cartella + "/.trivyignore", ".trivyignore")]


def test_form_feed_prima_del_commento(repo):
    """N2: splitlines() spezzava su \f e il `# nosec` finiva su una riga senza `+`."""
    with open(str(repo / "app" / "db.py"), "a") as fh:
        fh.write("eval(x)\f# nosec\n")
    commit(repo)
    assert esito(repo)["esito"] == sc.FAIL


@pytest.mark.parametrize("sporco", ["modificato", "non tracciato"])
def test_working_tree_sporco_non_verificabile(repo, sporco):
    """F6: il check vede solo HEAD: una soppressione non committata non deve dare PASS."""
    if sporco == "modificato":
        con_nosemgrep(repo)
    else:
        scrivi(repo, "nuovo/.trivyignore", "CVE-9\n")
    rep = esito(repo)
    assert rep["esito"] == sc.NON_VERIFICABILE and "non committate" in rep["spiegazione"]
    assert _cli(repo)[0] == 3

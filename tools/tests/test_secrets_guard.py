"""Guardia dei segreti: oracolo con gitleaks finto nel PATH."""
import datetime
import json
import os
import shutil
import stat
import subprocess
import sys

import pytest

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(QUI, "..", "security")))
import secrets_guard as sg  # noqa: E402

MARCATORE = "FAKE-SECRET-MARKER"

# gitleaks finto: rifiuta i flag che il vero non conosce (cosi' non nasconde errori d'invocazione),
# scansiona la cartella corrente (o --source) e cerca il marcatore. `dir --help` esce 0 salvo
# FAKE_NO_DIR=1 (versioni vecchie: ripiego su `detect`). Registra le invocazioni in $FAKE_LOG e
# gli argv in $FAKE_ARGV. Una config che contiene la parola DISABLE spegne le regole, come
# farebbe una config ostile.
FINTO = """#!/usr/bin/env python3
import sys, os, json
a = sys.argv[1:]
nodir = os.environ.get("FAKE_NO_DIR") == "1"
if a[:2] == ["dir", "--help"]:
    sys.exit(2 if nodir else 0)
if os.environ.get("FAKE_LOG"):
    open(os.environ["FAKE_LOG"], "a").write("invocato\\n")
if os.environ.get("FAKE_ARGV"):
    open(os.environ["FAKE_ARGV"], "a").write(json.dumps({"argv": a, "cwd": os.getcwd(),
        "env_config": os.environ.get("GITLEAKS_CONFIG")}) + "\\n")
sub = a[0] if a else ""
if sub == "dir" and nodir or sub not in ("dir", "detect"):
    sys.stderr.write("unknown command\\n"); sys.exit(2)
CON_VALORE = ("--report-format", "--report-path", "--exit-code", "--config", "--source")
SENZA = ("--no-banner", "--redact") + (("--no-git",) if sub == "detect" else ())
opts = {}
i = 1
posiz = []
while i < len(a):
    t = a[i]
    if t in CON_VALORE:
        opts[t] = a[i + 1]; i += 2
    elif t in SENZA:
        i += 1
    elif t.startswith("-"):
        sys.stderr.write("unknown flag: %s\\n" % t); sys.exit(2)
    else:
        posiz.append(t); i += 1
if sub == "dir" and len(posiz) > 1 or sub == "detect" and posiz:
    sys.stderr.write("argomenti posizionali non validi\\n"); sys.exit(2)
mode = os.environ.get("FAKE_MODE", "")
if mode == "errore":
    sys.exit(2)
rep = opts["--report-path"]
if mode == "illeggibile":
    open(rep, "w").write("{non json")
    sys.exit(0)
radice = opts.get("--source") or (posiz[0] if posiz else ".")
disabilitata = False
if "--config" in opts:
    disabilitata = "DISABLE" in open(opts["--config"]).read()
found = []
for d, _, fs in os.walk(radice):
    for f in fs:
        p = os.path.join(d, f)
        if not disabilitata and "@@M@@" in open(p, errors="replace").read():
            found.append({"File": os.path.relpath(p, radice), "StartLine": 1, "RuleID": "fake"})
json.dump(found, open(rep, "w"))
sys.exit(1 if found else 0)
""".replace("@@M@@", MARCATORE)


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "repo"
    (r / "sub").mkdir(parents=True)
    return r


@pytest.fixture
def finto(tmp_path, monkeypatch):
    b = tmp_path / "bin"
    b.mkdir()
    g = b / "gitleaks"
    g.write_text(FINTO, encoding="utf-8")
    g.chmod(g.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", str(b) + os.pathsep + os.environ["PATH"])
    return g


def test_finding_fail(repo, finto):
    (repo / "sub" / "a.txt").write_text("x " + MARCATORE, encoding="utf-8")
    e = sg.scan(["sub/a.txt"], str(repo))
    assert e.stato == sg.FAIL and e.exit_code == 1
    assert e.findings[0]["File"] == os.path.join("sub", "a.txt")  # relativo al repo


def test_pulito_pass(repo, finto):
    (repo / "a.txt").write_text("niente", encoding="utf-8")
    e = sg.scan(["a.txt"], str(repo))
    assert e.stato == sg.PASS and e.exit_code == 0


def test_senza_gitleaks_non_verificabile(repo, tmp_path, monkeypatch):
    vuota = tmp_path / "vuota"
    vuota.mkdir()
    monkeypatch.setenv("PATH", str(vuota))
    (repo / "a.txt").write_text("niente", encoding="utf-8")
    e = sg.scan(["a.txt"], str(repo))
    assert e.stato == sg.NON_VERIFICABILE and e.exit_code == 3
    assert "NON_VERIFICABILE" in e.messaggio


def test_errore_gitleaks_fail_closed(repo, finto, monkeypatch):
    monkeypatch.setenv("FAKE_MODE", "errore")
    (repo / "a.txt").write_text("niente", encoding="utf-8")
    assert sg.scan(["a.txt"], str(repo)).stato == sg.NON_VERIFICABILE


def test_report_illeggibile_fail_closed(repo, finto, monkeypatch):
    monkeypatch.setenv("FAKE_MODE", "illeggibile")
    (repo / "a.txt").write_text("niente", encoding="utf-8")
    assert sg.scan(["a.txt"], str(repo)).stato == sg.NON_VERIFICABILE


def test_messaggio_dichiara_e_non_cita_riferimenti(repo, finto):
    (repo / "a.txt").write_text("niente", encoding="utf-8")
    m = sg.scan(["a.txt"], str(repo)).messaggio
    assert "previene nel percorso cooperativo, rileva negli altri" in m
    import re
    sorgente = open(sg.__file__.replace(".pyc", ".py"), encoding="utf-8").read()
    assert not re.search("S" + "EC-\\d|\\bG[0-5]\\b", m + sorgente)


def cfg(repo, testo):
    (repo / "factory.config.yaml").write_text(testo, encoding="utf-8")


def test_severita_assente_futuro_passato(repo):
    oggi = datetime.date(2026, 11, 16)
    assert sg.severita(str(repo), oggi) == "WARN"  # nessun file
    cfg(repo, "secrets_guard:\n  enabled: false\n  required_from: null\n")
    assert sg.severita(str(repo), oggi) == "WARN"
    cfg(repo, 'secrets_guard:\n  required_from: "2027-01-01"\n')
    assert sg.severita(str(repo), oggi) == "WARN"
    cfg(repo, 'secrets_guard:\n  required_from: "2026-11-16"\n')
    assert sg.severita(str(repo), oggi) == "ERROR"
    cfg(repo, 'secrets_guard:\n  required_from: "2026-01-01"\n')
    assert sg.severita(str(repo), oggi) == "ERROR"


def test_enabled_tollerante(repo):
    assert sg.enabled(str(repo)) is False
    cfg(repo, "altro: 1\n")
    assert sg.enabled(str(repo)) is False
    cfg(repo, "secrets_guard:\n  enabled: true\n")
    assert sg.enabled(str(repo)) is True


def test_cli_exit_code(repo, finto):
    (repo / "a.txt").write_text(MARCATORE, encoding="utf-8")
    script = os.path.join(QUI, "..", "security", "secrets_guard.py")
    r = subprocess.run([sys.executable, script, "--root", str(repo), "a.txt"],
                       stdout=subprocess.PIPE, universal_newlines=True, encoding="utf-8", errors="replace")
    assert r.returncode == 1 and "FAIL" in r.stdout


def _git(r, *a):
    subprocess.run(["git", "-C", str(r)] + list(a), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


@pytest.fixture
def grepo(repo):
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")
    return repo


def test_hook_exit_per_severita(grepo, finto, capsys):
    repo = grepo
    (repo / "sub" / "a.txt").write_text("x " + MARCATORE, encoding="utf-8")
    _git(repo, "add", "sub/a.txt")
    cfg = repo / "factory.config.yaml"
    cfg.write_text("secrets_guard:\n  enabled: false\n", encoding="utf-8")
    assert sg.main(["--hook", "--root", str(repo)]) == 0
    cfg.write_text("secrets_guard:\n  enabled: true\n  required_from: null\n", encoding="utf-8")
    assert sg.main(["--hook", "--root", str(repo)]) == 0
    assert "commit NON bloccato" in capsys.readouterr().out
    cfg.write_text("secrets_guard:\n  enabled: true\n  required_from: 2020-01-01\n", encoding="utf-8")
    assert sg.main(["--hook", "--root", str(repo)]) == 1
    assert sg.main(["--root", str(repo), "sub/a.txt"]) == 1


def test_hook_nulla_in_stage_non_blocca_e_lo_dichiara(grepo, finto, capsys):
    (grepo / "factory.config.yaml").write_text("secrets_guard:\n  enabled: true\n  required_from: 2020-01-01\n", encoding="utf-8")
    assert sg.main(["--hook", "--root", str(grepo)]) == 0
    assert "nessuna verifica eseguita" in capsys.readouterr().out


ALLARGA = "[allowlist]\npaths = ['.*']\n"


def test_hook_sola_config_in_stage_a_warn_passa_con_avviso(grepo, finto, capsys):
    """US-422 AC3: a WARN la modifica di .gitleaks.toml passa, ma non in silenzio."""
    (grepo / "factory.config.yaml").write_text("secrets_guard:\n  enabled: true\n  required_from: null\n", encoding="utf-8")
    (grepo / ".gitleaks.toml").write_text("# regole\n", encoding="utf-8")
    (grepo / ".gitleaksignore").write_text("# esclusioni\n", encoding="utf-8")
    _git(grepo, "add", ".gitleaks.toml", ".gitleaksignore")
    assert sg.main(["--hook", "--root", str(grepo)]) == 0
    out = capsys.readouterr().out
    assert "AVVISO" in out and "bypass in due commit" in out and "solo la configurazione" in out


def test_hook_config_a_error_blocca_senza_record(grepo, finto, capsys):
    """US-422 AC3 (mutante F8): a ERROR la sola config in stage blocca, anche senza altri file."""
    (grepo / "factory.config.yaml").write_text("secrets_guard:\n  enabled: true\n  required_from: 2020-01-01\n", encoding="utf-8")
    (grepo / ".gitleaks.toml").write_text(ALLARGA, encoding="utf-8")
    _git(grepo, "add", ".gitleaks.toml")
    assert sg.main(["--hook", "--root", str(grepo)]) == 1
    assert "ambito config_gitleaks" in capsys.readouterr().out


def test_hook_config_a_error_passa_con_record_config_sul_ref_protetto(grepo, finto, capsys):
    _protetto(grepo, dict(RECORD, ambito="config_gitleaks"))
    (grepo / ".gitleaks.toml").write_text("# regole riviste\n", encoding="utf-8")
    _git(grepo, "add", ".gitleaks.toml")
    assert sg.main(["--hook", "--root", str(grepo)]) == 0
    assert "DEROGA DA RECORD per .gitleaks.toml" in capsys.readouterr().out


def test_record_non_verificabile_non_copre_la_config(grepo, finto):
    """Un record copre solo il proprio ambito."""
    _protetto(grepo, RECORD)  # ambito implicito: non_verificabile
    (grepo / ".gitleaks.toml").write_text("# regole\n", encoding="utf-8")
    _git(grepo, "add", ".gitleaks.toml")
    assert sg.main(["--hook", "--root", str(grepo)]) == 1
    assert sg.deroga(str(grepo))[0] is not None
    assert sg.deroga(str(grepo), ambito="config_gitleaks")[0] is None


def test_hook_config_con_altri_file_viene_verificata(grepo, finto, capsys):
    _protetto(grepo, dict(RECORD, ambito="config_gitleaks"))
    (grepo / ".gitleaks.toml").write_text("# regole\n", encoding="utf-8")
    (grepo / "a.txt").write_text("x " + MARCATORE, encoding="utf-8")
    _git(grepo, "add", ".gitleaks.toml", "a.txt")
    assert sg.main(["--hook", "--root", str(grepo)]) == 1
    out = capsys.readouterr().out
    assert "solo la configurazione" not in out and "FAIL" in out


def test_config_diff_segnala_solo_se_la_config_cambia(grepo, capsys):
    """US-422 AC4: in CI una PR che modifica .gitleaks.toml e' segnalata con ::warning."""
    (grepo / ".gitleaks.toml").write_text("# base\n", encoding="utf-8")
    _git(grepo, "add", "-A")
    _git(grepo, "commit", "-qm", "base")
    _git(grepo, "update-ref", "refs/remotes/origin/main", "HEAD")
    assert sg.main(["--config-diff", "origin/main", "--root", str(grepo)]) == 0
    assert "invariato" in capsys.readouterr().out
    (grepo / ".gitleaks.toml").write_text("# base\n" + ALLARGA, encoding="utf-8")
    _git(grepo, "commit", "-qam", "allarga l'allowlist")
    assert sg.main(["--config-diff", "origin/main", "--root", str(grepo)]) == 0
    out = capsys.readouterr().out
    assert out.startswith("::warning title=.gitleaks.toml modificato::") and "+[allowlist]" in out
    assert sg.main(["--config-diff", "origin/inesistente", "--root", str(grepo)]) == 0
    assert "NON verificata" in capsys.readouterr().out


def _solo_git(tmp_path, monkeypatch):
    """PATH con il solo git, senza gitleaks; nessun percorso noto con gitleaks."""
    solo_git = tmp_path / "solo-git"
    solo_git.mkdir()
    os.symlink(shutil.which("git"), str(solo_git / "git"))
    monkeypatch.setenv("PATH", str(solo_git))
    monkeypatch.setattr(sg, "PERCORSI_NOTI", ())


ERRORE = "secrets_guard:\n  enabled: true\n  required_from: 2020-01-01\n"
RECORD = {"motivo": "gitleaks in manutenzione", "scadenza": "2999-01-01",
          "approvato_da": "maintainer", "riferimento_gate": "R.14-test"}


def _protetto(grepo, record=None, nome="security/secrets-guard-deroghe.json"):
    """Commit base (con il record, se dato) e ref origin/main su quel commit."""
    (grepo / "factory.config.yaml").write_text(ERRORE, encoding="utf-8")
    if record is not None:
        (grepo / "security").mkdir(exist_ok=True)
        (grepo / nome).write_text(json.dumps(record if isinstance(record, list) else [record]), encoding="utf-8")
    _git(grepo, "add", "-A")
    _git(grepo, "commit", "-qm", "base")
    _git(grepo, "update-ref", "refs/remotes/origin/main", "HEAD")


def _stage(grepo, nome="a.txt"):
    (grepo / nome).write_text("niente", encoding="utf-8")
    _git(grepo, "add", nome)


def test_hook_non_verificabile_blocca_a_error_e_indica_il_record(grepo, tmp_path, monkeypatch, capsys):
    _protetto(grepo)
    _stage(grepo)
    _solo_git(tmp_path, monkeypatch)
    assert sg.main(["--hook", "--root", str(grepo)]) == 1
    out = capsys.readouterr().out
    assert "record di deroga" in out and "SECRETS_GUARD_OVERRIDE=1" not in out
    (grepo / "factory.config.yaml").write_text("secrets_guard:\n  enabled: true\n  required_from: 2999-01-01\n", encoding="utf-8")
    assert sg.main(["--hook", "--root", str(grepo)]) == 0
    assert "commit NON bloccato" in capsys.readouterr().out


def test_variabile_d_ambiente_non_e_piu_una_deroga(grepo, tmp_path, monkeypatch, capsys):
    """US-423 AC1: con SECRETS_GUARD_OVERRIDE=1 e senza record l'esito resta bloccante."""
    _protetto(grepo)
    _stage(grepo)
    _solo_git(tmp_path, monkeypatch)
    monkeypatch.setenv("SECRETS_GUARD_OVERRIDE", "1")
    assert sg.main(["--hook", "--root", str(grepo)]) == 1
    out = capsys.readouterr().out
    assert "non e' piu' letta" in out and "DEROGA" not in out


def test_record_sul_ref_protetto_deroga_e_lo_dichiara(grepo, tmp_path, monkeypatch, capsys):
    _protetto(grepo, RECORD)
    _stage(grepo)
    _solo_git(tmp_path, monkeypatch)
    assert sg.main(["--hook", "--root", str(grepo)]) == 0
    out = capsys.readouterr().out
    assert "DEROGA DA RECORD" in out and "traccia, non una firma" in out and "R.14-test" in out


def test_record_solo_nel_working_tree_non_vale(grepo, tmp_path, monkeypatch):
    """US-423 AC2: il record non committato non deroga."""
    _protetto(grepo)
    (grepo / "security").mkdir()
    (grepo / "security" / "secrets-guard-deroghe.json").write_text(json.dumps([RECORD]), encoding="utf-8")
    _git(grepo, "add", "security/secrets-guard-deroghe.json")  # anche in stage: conta il merge-base
    _solo_git(tmp_path, monkeypatch)
    assert sg.main(["--hook", "--root", str(grepo)]) == 1


def test_record_committato_solo_sul_branch_non_vale(grepo, tmp_path, monkeypatch):
    """US-423 AC2 (mutante A25): il record su un branch, assente dal merge-base, non deroga."""
    _protetto(grepo)
    _git(grepo, "checkout", "-q", "-b", "lavoro")
    (grepo / "security").mkdir()
    (grepo / "security" / "secrets-guard-deroghe.json").write_text(json.dumps([RECORD]), encoding="utf-8")
    _git(grepo, "add", "-A")
    _git(grepo, "commit", "-qm", "deroga sul branch")
    _stage(grepo)
    _solo_git(tmp_path, monkeypatch)
    assert sg.main(["--hook", "--root", str(grepo)]) == 1
    rec, spiega = sg.deroga(str(grepo))
    assert rec is None and "al merge-base" in spiega


def test_record_scaduto_o_incompleto_non_vale(grepo):
    """US-423 AC3: scaduto o con un campo vuoto vale come assente."""
    scaduto = dict(RECORD, scadenza="2020-01-01")
    incompleto = dict(RECORD, approvato_da=" ")
    _protetto(grepo, [scaduto, incompleto])
    rec, spiega = sg.deroga(str(grepo))
    assert rec is None and "nessun record valido" in spiega
    rec, _ = sg.deroga(str(grepo), oggi=datetime.date(2019, 12, 31))
    assert rec is not None and rec["scadenza"] == "2020-01-01"


def test_ref_protetto_assente_nessuna_deroga(grepo):
    (grepo / "a.txt").write_text("x", encoding="utf-8")
    _git(grepo, "add", "-A")
    _git(grepo, "commit", "-qm", "base")
    rec, spiega = sg.deroga(str(grepo))
    assert rec is None and "non risolto" in spiega


def test_causa_assente_o_non_raggiungibile(tmp_path):
    """US-423 AC4: le due cause sono distinte."""
    vuota = tmp_path / "vuota"
    vuota.mkdir()
    assert "assente" in sg.causa_binario_mancante([str(vuota)])
    altrove = tmp_path / "altrove"
    altrove.mkdir()
    g = altrove / "gitleaks"
    g.write_text("#!/bin/sh\n", encoding="utf-8")
    g.chmod(0o755)
    c = sg.causa_binario_mancante([str(vuota), str(altrove)])
    assert "non raggiungibile dal PATH" in c and str(g) in c


def test_non_verificabile_riporta_la_causa_con_path_ridotto(repo, tmp_path, monkeypatch):
    """US-423 AC4, come una sessione agentica: PATH ridotto e binario in un percorso noto."""
    altrove = tmp_path / "homebrew-bin"
    altrove.mkdir()
    g = altrove / "gitleaks"
    g.write_text("#!/bin/sh\n", encoding="utf-8")
    g.chmod(0o755)
    monkeypatch.setenv("PATH", "/usr/bin:/bin:/usr/sbin:/sbin")
    monkeypatch.setattr(sg, "PERCORSI_NOTI", (str(altrove),))
    (repo / "a.txt").write_text("niente", encoding="utf-8")
    e = sg.scan(["a.txt"], str(repo))
    assert e.stato == sg.NON_VERIFICABILE and "non raggiungibile dal PATH" in e.messaggio


# --- R1: modalita' stage ---------------------------------------------------------------------

def test_stage_segreto_tolto_dal_disco_e_visto(grepo, finto):
    (grepo / "a.txt").write_text("x " + MARCATORE, encoding="utf-8")
    _git(grepo, "add", "a.txt")
    (grepo / "a.txt").write_text("pulito", encoding="utf-8")  # corretto dopo git add: l'indice ha ancora il segreto
    assert sg.scan_staged(str(grepo)).stato == sg.FAIL
    os.remove(str(grepo / "a.txt"))
    e = sg.scan_staged(str(grepo))
    assert e.stato == sg.FAIL and e.findings[0]["File"] == "a.txt"


def test_stage_nome_non_ascii(grepo, finto):
    d = grepo / "configurazione"
    d.mkdir()
    (d / "credenziali-citt\u00e0.env").write_text(MARCATORE, encoding="utf-8")
    _git(grepo, "add", "-A")
    e = sg.scan_staged(str(grepo))
    assert e.stato == sg.FAIL
    assert e.findings[0]["File"] == "configurazione/credenziali-citt\u00e0.env"


def test_stage_rinomina(grepo, finto):
    (grepo / "a.txt").write_text("x " + MARCATORE + "\nriga\nriga\nriga\n", encoding="utf-8")
    _git(grepo, "add", "a.txt")
    _git(grepo, "commit", "-qm", "base")
    _git(grepo, "mv", "a.txt", "b.txt")
    e = sg.scan_staged(str(grepo))
    assert e.stato == sg.FAIL and e.findings[0]["File"] == "b.txt"


def test_stage_pulito_pass_con_n_file(grepo, finto):
    (grepo / "a.txt").write_text("niente", encoding="utf-8")
    (grepo / "b.txt").write_text("niente", encoding="utf-8")
    _git(grepo, "add", "-A")
    e = sg.scan_staged(str(grepo))
    assert e.stato == sg.PASS and "nessun finding su 2 file" in e.messaggio
    assert "nessun segreto" not in e.messaggio


# --- R2: niente input = niente verifica --------------------------------------------------------

def test_zero_file_non_verificabile(grepo, finto):
    assert sg.scan([], str(grepo)).stato == sg.NON_VERIFICABILE
    assert sg.scan(["non-esiste.txt"], str(grepo)).stato == sg.NON_VERIFICABILE
    assert sg.scan_staged(str(grepo)).stato == sg.NON_VERIFICABILE


def test_root_non_git_stage_non_verificabile(tmp_path, finto):
    r = tmp_path / "nongit"
    r.mkdir()
    e = sg.scan_staged(str(r))
    assert e.stato == sg.NON_VERIFICABILE and "git" in e.messaggio


def test_symlink_saltato_e_contato(repo, finto):
    (repo / "vero.txt").write_text("niente", encoding="utf-8")
    os.symlink(str(repo / "vero.txt"), str(repo / "link.txt"))
    e = sg.scan(["vero.txt", "link.txt"], str(repo))
    assert e.stato == sg.PASS and "1 symlink" in e.messaggio and "su 1 file" in e.messaggio
    solo = sg.scan(["link.txt"], str(repo))
    assert solo.stato == sg.NON_VERIFICABILE


def test_stessi_nomi_in_cartelle_diverse_non_collidono(repo, finto):
    (repo / "x").mkdir()
    (repo / "y").mkdir()
    (repo / "x" / "n.txt").write_text(MARCATORE, encoding="utf-8")
    (repo / "y" / "n.txt").write_text("niente", encoding="utf-8")
    e = sg.scan(["x/n.txt", "y/n.txt"], str(repo))
    assert e.stato == sg.FAIL and len(e.findings) == 1


# --- config di gitleaks e invocazione ----------------------------------------------------------

def _argv(log):
    return [json.loads(l) for l in open(str(log), encoding="utf-8").read().splitlines() if l]


def test_config_in_stage_non_spegne_la_scansione(grepo, finto, tmp_path, monkeypatch):
    log = tmp_path / "argv.log"
    monkeypatch.setenv("FAKE_ARGV", str(log))
    monkeypatch.setenv("GITLEAKS_CONFIG", "/tmp/ostile.toml")
    (grepo / "a.txt").write_text(MARCATORE, encoding="utf-8")
    (grepo / ".gitleaks.toml").write_text("# DISABLE tutte le regole\n", encoding="utf-8")
    _git(grepo, "add", "-A")
    e = sg.scan_staged(str(grepo))
    assert e.stato == sg.FAIL
    inv = _argv(log)[0]
    assert "--config" not in inv["argv"] and inv["env_config"] is None
    assert not os.path.exists(os.path.join(inv["cwd"], ".gitleaks.toml"))


def test_config_di_head_passata_con_config(grepo, finto, tmp_path, monkeypatch):
    log = tmp_path / "argv.log"
    monkeypatch.setenv("FAKE_ARGV", str(log))
    (grepo / ".gitleaks.toml").write_text("# DISABLE\n", encoding="utf-8")
    _git(grepo, "add", ".gitleaks.toml")
    _git(grepo, "commit", "-qm", "config")
    (grepo / "a.txt").write_text(MARCATORE, encoding="utf-8")
    _git(grepo, "add", "a.txt")
    e = sg.scan_staged(str(grepo))
    assert e.stato == sg.PASS  # la config committata e' quella che comanda
    assert "--config" in _argv(log)[0]["argv"]
    assert sg.scan(["a.txt"], str(grepo)).stato == sg.PASS  # working tree: config del disco


def test_invocazione_dir_con_ripiego_su_detect(repo, finto, tmp_path, monkeypatch):
    log = tmp_path / "argv.log"
    monkeypatch.setenv("FAKE_ARGV", str(log))
    (repo / "a.txt").write_text("niente", encoding="utf-8")
    assert sg.scan(["a.txt"], str(repo)).stato == sg.PASS
    assert _argv(log)[0]["argv"][0] == "dir"
    monkeypatch.setenv("FAKE_NO_DIR", "1")
    assert sg.scan(["a.txt"], str(repo)).stato == sg.PASS
    assert _argv(log)[-1]["argv"][0] == "detect"


def test_flag_sconosciuto_non_passa_inosservato(repo, finto, monkeypatch):
    # il finto rifiuta i flag che non conosce: un errore d'invocazione diventa NON_VERIFICABILE
    (repo / "a.txt").write_text("niente", encoding="utf-8")
    import secrets_guard
    originale = secrets_guard.subprocess.run

    def run(cmd, *a, **k):
        if len(cmd) > 2 and cmd[1] == "dir" and "--help" not in cmd:
            cmd = list(cmd) + ["--flag-inventato"]
        return originale(cmd, *a, **k)
    monkeypatch.setattr(secrets_guard.subprocess, "run", run)
    assert sg.scan(["a.txt"], str(repo)).stato == sg.NON_VERIFICABILE

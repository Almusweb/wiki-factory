"""Oracoli semgrep (sast_guard, TSK-1041) e trivy (iac_guard, TSK-1042): EP-109 US-427 AC1, AC2, AC3.

Scanner finti con il comportamento dei veri che conta qui: semgrep onora `# nosemgrep` salvo
`--disable-nosem` e legge `.semgrepignore` dall'albero; trivy onora `.trivyignore` e `trivy:ignore`
inline. Il semgrep finto sta in un venv con `bin/python3` symlink, come con pipx. Le regole finte sono
`id:` + `pattern:` nel file di ruleset della factory."""
from __future__ import annotations

import json
import os
import stat
import subprocess
import sys

import pytest

QUI = os.path.dirname(os.path.abspath(__file__))
SEC = os.path.normpath(os.path.join(QUI, "..", "security"))
sys.path.insert(0, SEC)
import iac_guard  # noqa: E402
import oracolo_statico as ost  # noqa: E402
import sast_guard  # noqa: E402
import scanner_identity as si  # noqa: E402
import secrets_guard as sg  # noqa: E402

COMUNE_FINTO = r'''
import json, os, sys
a = sys.argv[1:]
def opt(n):
    return a[a.index(n) + 1] if n in a else None
regola = {}
for riga in (open(opt("--config")).read().splitlines() if opt("--config") else []):
    if ":" in riga:
        k, v = riga.split(":", 1)
        regola[k.strip()] = v.strip()
def ignorati(nome):
    return [l.strip() for l in open(nome).read().splitlines() if l.strip() and not l.startswith("#")] \
        if os.path.exists(nome) else []
def file_albero():
    for base, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d != ".git"]
        for f in files:
            yield os.path.relpath(os.path.join(base, f), ".")
'''

SEMGREP_FINTO = COMUNE_FINTO + r'''
if a[:1] == ["--version"]:
    print("1.95.0"); sys.exit(0)
assert a[0] == "scan" and "--metrics" in a, a
esclusi = ignorati(".semgrepignore")
res = []
errori = []
for p in file_albero():
    if any(p.startswith(e) for e in esclusi) or p.startswith("."):
        continue
    if "TIMEOUT-FINTO" in open(p, errors="replace").read():
        errori.append({"type": "Timeout", "level": "warn", "path": p})
        continue
    for n, l in enumerate(open(p, errors="replace").read().splitlines(), 1):
        if regola["pattern"] in l and ("nosemgrep" not in l or "--disable-nosem" in a):
            res.append({"check_id": regola["id"], "path": p, "start": {"line": n}})
json.dump({"results": res, "errors": errori}, open(opt("--output"), "w"))
'''

TRIVY_FINTO = "#!/usr/bin/env python3\n" + COMUNE_FINTO + r'''
if a[:1] == ["--version"]:
    print("Version: 0.57.0"); sys.exit(0)
assert a[0] == "config" and "--skip-check-update" in a, a
ign = ignorati(".trivyignore")
per_target = {}
for p in file_albero():
    if not p.endswith(".tf"):
        continue
    for l in open(p).read().splitlines():
        if regola["pattern"] in l and "trivy:ignore" not in l and regola["id"] not in ign:
            per_target.setdefault(p, []).append({"ID": regola["id"], "Status": "FAIL"})
json.dump({"Results": [{"Target": t, "Misconfigurations": m} for t, m in per_target.items()]},
          open(opt("--output"), "w"))
'''

CASI = {
    "semgrep": dict(modulo=sast_guard, scanner=sast_guard.SEMGREP, file="app.py", riga="x = eval(data)",
                    pattern="eval(", regola="fake.eval", inline="x = eval(data)  # nosemgrep",
                    cfg=".semgrepignore", cfg_riga="src/", ruleset="security/semgrep.yml",
                    versione="1.95.0"),
    "trivy": dict(modulo=iac_guard, scanner=iac_guard.TRIVY, file="main.tf", riga='acl = "BADCFG"',
                  pattern="BADCFG", regola="AVD-FAKE-0001", inline='acl = "BADCFG"  # trivy:ignore:AVD-FAKE-0001',
                  cfg=".trivyignore", cfg_riga="AVD-FAKE-0001", ruleset="security/trivy.yaml",
                  versione="0.57.0"),
}


def _git(repo, *a):
    r = subprocess.run(["git", "-C", str(repo)] + list(a), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert r.returncode == 0, r.stderr
    return r.stdout.decode().strip()


def _init(repo):
    repo.mkdir(parents=True, exist_ok=True)
    for c in (("init", "-q"), ("config", "user.email", "t@t"), ("config", "user.name", "t"),
              ("config", "commit.gpgsign", "false")):
        _git(repo, *c)


def _commit(repo, msg="c", protetto=False):
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "--allow-empty", "-m", msg, "--no-verify")
    if protetto:
        _git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")


def _scrivi(p, testo, eseguibile=False):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(testo)
    if eseguibile:
        p.chmod(p.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


def _scanner_finti(tmp):
    venv = tmp / "venv"
    (venv / "bin").mkdir(parents=True)
    os.symlink(os.path.realpath(sys.executable), str(venv / "bin" / "python3"))
    _scrivi(venv / "lib" / "python3.9" / "site-packages" / "semgrep-1.95.0.dist-info" / "RECORD", "semgrep,x,1\n")
    _scrivi(venv / "lib" / "python3.9" / "site-packages" / "semgrep" / "bin" / "semgrep-core", "motore finto\n")
    semgrep = venv / "bin" / "semgrep"
    _scrivi(semgrep, "#!%s\n%s" % (venv / "bin" / "python3", SEMGREP_FINTO), eseguibile=True)
    trivy = tmp / "trivy-bin" / "trivy"
    _scrivi(trivy, TRIVY_FINTO, eseguibile=True)
    return {"semgrep": semgrep, "trivy": trivy}


@pytest.fixture(params=sorted(CASI))
def caso(request, tmp_path):
    c = dict(CASI[request.param], nome=request.param)
    finti = _scanner_finti(tmp_path)
    f = tmp_path / "factory"
    _init(f)
    _scrivi(f / "factory.config.yaml",
            "code_paths:\n  - name: cliente\n    path: code_repos/cliente/\n"
            "scanner_identity:\n  pins: security/scanner-pins.json\n  ref_protetto: origin/main\n"
            "security_scan:\n  semgrep_ruleset: security/semgrep.yml\n  trivy_config: security/trivy.yaml\n"
            "  ref_protetto: origin/main\n")
    for k in CASI:
        _scrivi(f / CASI[k]["ruleset"], "id: %s\npattern: %s\n" % (CASI[k]["regola"], CASI[k]["pattern"]))
    pins = {}
    for k, exe in finti.items():
        _, sha, _, err = si.misura(k, str(exe))
        assert err is None, err
        pins[k] = [{"path": str(exe), "sha256": sha, "version": CASI[k]["versione"]}]
    _scrivi(f / "security" / "scanner-pins.json", json.dumps(pins))
    _commit(f, "factory", protetto=True)
    cl = f / "code_repos" / "cliente"
    _init(cl)
    _scrivi(cl / "src" / c["file"], "%s\n" % c["riga"])
    _scrivi(cl / "src" / "pulito.txt", "niente\n")
    _commit(cl, "base", protetto=True)
    c.update(factory=f, cliente=cl, exe=finti[request.param])
    return c


def esegui(c):
    return ost.esegui(c["scanner"], str(c["cliente"]), str(c["factory"]))


def voci(rep):
    return [(v["esito"], v.get("motivo")) for v in rep["confronto"]["voci"]]


# --- base e AC2 -------------------------------------------------------------------------------

def test_branch_invariato_pass_con_finding_persistenti_elencati(caso):
    rep = esegui(caso)
    assert rep["esito"] == ost.PASS
    assert voci(rep) == [("persistente", None)]


def test_report_con_identita_del_binario_e_versione_del_ruleset(caso):
    rep = esegui(caso)
    ident = rep["identita"]
    assert ident["stato"] == si.IDENTIFICATO and ident["version"] == caso["versione"]
    assert ident["realpath"] == os.path.realpath(str(caso["exe"])) and len(ident["sha256"]) == 64
    rs = rep["ruleset"]
    contenuto = _git(caso["factory"], "show", "origin/main:%s" % caso["ruleset"]) + "\n"
    import hashlib
    assert rs["path"] == caso["ruleset"] and rs["sha256"] == hashlib.sha256(contenuto.encode()).hexdigest()
    assert rs["merge_base_factory"] == _git(caso["factory"], "rev-parse", "origin/main")


def test_fix_col_file_presente_non_verificabile_senza_simbolo(caso):
    """CQRL iter-1: senza simbolo il fix non si distingue dalla riga cancellata: review umana."""
    _scrivi(caso["cliente"] / "src" / caso["file"], "sicuro = True\n")
    _commit(caso["cliente"])
    rep = esegui(caso)
    assert rep["esito"] == ost.NON_VERIFICABILE and voci(rep) == [("non_verificabile", "simbolo_non_dichiarato")]


def test_finding_nuovo_fail(caso):
    _scrivi(caso["cliente"] / "src" / ("altro" + os.path.splitext(caso["file"])[1]), "%s\n" % caso["riga"])
    _commit(caso["cliente"])
    rep = esegui(caso)
    assert rep["esito"] == ost.FAIL and ("nuovo", None) in voci(rep)


# --- AC3: mutanti -----------------------------------------------------------------------------

def test_mutante_soppressione_inline_aggiunta_fail(caso):
    _scrivi(caso["cliente"] / "src" / caso["file"], "%s\n" % caso["inline"])
    _commit(caso["cliente"])
    rep = esegui(caso)
    assert rep["esito"] == ost.FAIL
    assert [s["accettata"] for s in rep["soppressioni"]["voci"]] == [False]


def test_mutante_file_cancellato_non_verificabile(caso):
    _git(caso["cliente"], "rm", "-q", "src/" + caso["file"])
    _commit(caso["cliente"])
    rep = esegui(caso)
    assert rep["esito"] == ost.NON_VERIFICABILE and voci(rep) == [("non_verificabile", "cancellato")]


def test_mutante_file_spostato_non_verificabile(caso):
    (caso["cliente"] / "altrove").mkdir()
    _git(caso["cliente"], "mv", "src/" + caso["file"], "altrove/" + caso["file"])
    _commit(caso["cliente"])
    rep = esegui(caso)
    # la regola trova il file nel nuovo path (nuovo) e il vecchio e' sparito per spostamento
    assert rep["esito"] in (ost.FAIL, ost.NON_VERIFICABILE)
    assert ("non_verificabile", "spostato") in voci(rep)
    assert rep["esito"] != ost.PASS


def test_mutante_file_spostato_sotto_path_escluso_non_verificabile(caso):
    if caso["nome"] != "semgrep":
        pytest.skip("trivy finto: nessun path escluso per cartella")
    _scrivi(caso["cliente"] / ".semgrepignore", "vendor/\n")
    _commit(caso["cliente"], "esclusione sul ref protetto", protetto=True)
    (caso["cliente"] / "vendor").mkdir()
    _git(caso["cliente"], "mv", "src/" + caso["file"], "vendor/" + caso["file"])
    _commit(caso["cliente"])
    rep = esegui(caso)
    assert rep["esito"] == ost.NON_VERIFICABILE and voci(rep) == [("non_verificabile", "vendorizzato")]


def test_mutante_file_rinominato_non_verificabile(caso):
    nuovo = "rinominato" + os.path.splitext(caso["file"])[1]
    _git(caso["cliente"], "mv", "src/" + caso["file"], "src/" + nuovo)
    _commit(caso["cliente"])
    rep = esegui(caso)
    assert ("non_verificabile", "spostato") in voci(rep) and rep["esito"] != ost.PASS


# --- AC1: ruleset e config dal merge-base -----------------------------------------------------

def test_config_del_cliente_modificata_sul_branch_ignorata(caso):
    _scrivi(caso["cliente"] / caso["cfg"], "%s\n" % caso["cfg_riga"])
    _commit(caso["cliente"])
    rep = esegui(caso)
    assert voci(rep) == [("persistente", None)], "il finding resta: la config del branch non vale"
    assert rep["esito"] == ost.FAIL   # e la riga aggiunta alla config e' una soppressione nuova
    assert [s["tipo"] for s in rep["soppressioni"]["voci"]] == [caso["cfg"]]


def test_ruleset_della_factory_modificato_sul_branch_ignorato(caso):
    _scrivi(caso["factory"] / caso["ruleset"], "id: %s\npattern: NON-CORRISPONDE-MAI\n" % caso["regola"])
    _commit(caso["factory"], "ruleset indebolito sul branch")
    rep = esegui(caso)
    assert rep["esito"] == ost.PASS and voci(rep) == [("persistente", None)]
    assert rep["ruleset"]["merge_base_factory"] == _git(caso["factory"], "rev-parse", "origin/main")


def test_ruleset_non_dichiarato_non_verificabile(caso):
    _scrivi(caso["factory"] / "factory.config.yaml",
            (caso["factory"] / "factory.config.yaml").read_text().replace(caso["scanner"].chiave_ruleset, "altro"))
    _commit(caso["factory"], "chiave tolta sull'ancora", protetto=True)
    rep = esegui(caso)
    assert rep["esito"] == ost.NON_VERIFICABILE and "ruleset non fissato" in rep["motivo"]


def test_ruleset_null_non_e_la_stringa_null(caso):
    cfg = caso["factory"] / "factory.config.yaml"
    cfg.write_text(cfg.read_text().replace("semgrep_ruleset: security/semgrep.yml", "semgrep_ruleset: null")
                   .replace("trivy_config: security/trivy.yaml", "trivy_config: null"))
    _commit(caso["factory"], "null", protetto=True)
    rep = esegui(caso)
    assert rep["esito"] == ost.NON_VERIFICABILE and "ruleset non fissato" in rep["motivo"]


# --- CQRL iter-1: config della factory dal disco, export-ignore, exit code ---------------------

def _nuovo_vulnerabile(caso):
    _scrivi(caso["cliente"] / "src" / ("altro" + os.path.splitext(caso["file"])[1]), "%s\n" % caso["riga"])
    _commit(caso["cliente"])


def test_ref_protetto_head_sul_disco_della_factory_non_vale(caso):
    """F1: `ref_protetto: HEAD` non committato faceva coincidere PRIMA e DOPO: PASS su un finding nuovo."""
    _nuovo_vulnerabile(caso)
    cfg = caso["factory"] / "factory.config.yaml"
    cfg.write_text(cfg.read_text().replace("  ref_protetto: origin/main\n", "  ref_protetto: HEAD\n"))
    assert esegui(caso)["esito"] == ost.FAIL


def test_path_del_ruleset_cambiato_sul_disco_non_vale(caso):
    """F2: il path veniva dal disco e il contenuto dal merge-base: un altro file dava PASS con 0 voci."""
    _scrivi(caso["factory"] / "security" / "vuoto.yml", "id: nessuna\npattern: MAI-PRESENTE\n")
    _commit(caso["factory"], "file vuoto", protetto=True)
    _nuovo_vulnerabile(caso)
    cfg = caso["factory"] / "factory.config.yaml"
    cfg.write_text(cfg.read_text().replace(caso["ruleset"], "security/vuoto.yml"))
    rep = esegui(caso)
    assert rep["esito"] == ost.FAIL and rep["ruleset"]["path"] == caso["ruleset"]


def test_export_ignore_non_nasconde_un_file(caso):
    """F3: `export-ignore` toglieva il file nuovo dall'albero DOPO: PASS. Gli alberi non passano piu' da
    git archive (iter-2), quindi il file c'e' e il finding nuovo e' visto."""
    nome = "altro" + os.path.splitext(caso["file"])[1]
    _scrivi(caso["cliente"] / ".gitattributes", "src/%s export-ignore\n" % nome)
    _nuovo_vulnerabile(caso)
    rep = esegui(caso)
    assert rep["esito"] == ost.FAIL and ("nuovo", None) in voci(rep)


def test_trivy_exit_1_e_un_errore(caso, monkeypatch):
    if caso["nome"] != "trivy":
        pytest.skip("solo trivy: per semgrep exit 1 = finding")
    caso["exe"].write_text(caso["exe"].read_text() + "\nsys.exit(1)\n")
    _, sha, _, _ = si.misura("trivy", str(caso["exe"]))
    pins = json.loads((caso["factory"] / "security" / "scanner-pins.json").read_text())
    pins["trivy"][0]["sha256"] = sha
    _scrivi(caso["factory"] / "security" / "scanner-pins.json", json.dumps(pins))
    _commit(caso["factory"], "pin", protetto=True)
    rep = esegui(caso)
    assert rep["esito"] == ost.NON_VERIFICABILE and "exit 1" in rep["motivo"]


# --- identita' e perimetro --------------------------------------------------------------------

def test_binario_sostituito_non_verificabile_e_non_eseguito(caso, tmp_path):
    caso["exe"].write_text(caso["exe"].read_text() + "\n# sostituito\n")
    rep = esegui(caso)
    assert rep["esito"] == ost.NON_VERIFICABILE and "non identificato" in rep["motivo"]
    assert rep["identita"]["motivo"] == si.DIVERGENTE


def test_factory_rifiutata(caso):
    with pytest.raises(sg.Rifiuto):
        ost.esegui(caso["scanner"], str(caso["factory"]), str(caso["factory"]))


def test_cli_exit_code(caso):
    mod = caso["modulo"].__file__
    def cli(path):
        return subprocess.run([sys.executable, mod, str(path), "--root", str(caso["factory"]), "--json"],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    r = cli(caso["cliente"])
    assert r.returncode == 0, r.stdout + r.stderr
    assert json.loads(r.stdout)["tool"] == caso["nome"]
    assert cli(caso["factory"]).returncode == ost.EXIT_RIFIUTO


# --- CQRL iter-2 ------------------------------------------------------------------------------

def test_export_subst_non_riscrive_il_contenuto(caso):
    """R1: git archive applicava export-subst e un `$Format:` chiudeva una stringa sopra il codice."""
    nome = "altro" + os.path.splitext(caso["file"])[1]
    _scrivi(caso["cliente"] / ".gitattributes", "src/%s export-subst\n" % nome)
    _scrivi(caso["cliente"] / "src" / nome, 'z = 1  # $Format:%%x0a"""$\n%s\n' % caso["riga"])
    _commit(caso["cliente"])
    rep = esegui(caso)
    assert rep["esito"] == ost.FAIL and ("nuovo", None) in voci(rep)


def test_errore_dello_scanner_su_un_file_cambiato_non_verificabile(caso):
    if caso["nome"] != "semgrep":
        pytest.skip("solo semgrep riporta errori per file")
    _scrivi(caso["cliente"] / "src" / "lento.py", "TIMEOUT-FINTO\n%s\n" % caso["riga"])
    _commit(caso["cliente"])
    rep = esegui(caso)
    assert rep["esito"] == ost.NON_VERIFICABILE and "lento.py" in rep["motivo"]


# --- CQRL iter-3: materializza ---------------------------------------------------------------

def _commit_da_tree(repo, voci, genitore=None):
    """Commit con un tree costruito a mano: voci = [(modo, path a un livello o cartella/file, contenuto)]."""
    def blob(dati):
        r = subprocess.run(["git", "-C", str(repo), "hash-object", "-w", "--stdin"], input=dati,
                           stdout=subprocess.PIPE, check=True)
        return r.stdout.decode().strip()
    def tree(righe):
        r = subprocess.run(["git", "-C", str(repo), "mktree"], input="".join(righe).encode(),
                           stdout=subprocess.PIPE, check=True)
        return r.stdout.decode().strip()
    radice, cartelle = [], {}
    for modo, path, dati in voci:
        if "/" in path:
            c, nome = path.split("/", 1)
            cartelle.setdefault(c, []).append("%s blob %s\t%s\n" % (modo, blob(dati), nome))
        else:
            radice.append("%s blob %s\t%s\n" % (modo, blob(dati), path))
    for c, righe in cartelle.items():
        radice.append("040000 tree %s\t%s\n" % (tree(righe), c))
    t = tree(radice)
    r = subprocess.run(["git", "-C", str(repo), "commit-tree", t, "-m", "a mano"] + (["-p", genitore] if genitore else []),
                       stdout=subprocess.PIPE, check=True)
    return r.stdout.decode().strip()


@pytest.mark.parametrize("nome", [".git", ".GIT", ".Git"])
def test_materializza_rifiuta_una_cartella_git_nel_tree(tmp_path, nome):
    repo = tmp_path / "r"
    _init(repo)
    c = _commit_da_tree(repo, [("100644", "app.py", b"x = 1\n"), ("100644", nome + "/info", b"*\n")])
    assert ost.materializza(str(repo), c, str(tmp_path / "out")) is False


def test_materializza_conserva_il_bit_eseguibile(tmp_path):
    repo = tmp_path / "r"
    _init(repo)
    c = _commit_da_tree(repo, [("100755", "tool", b"#!/usr/bin/env python3\neval(x)\n"), ("100644", "a.py", b"1\n")])
    out = tmp_path / "out"
    out.mkdir()
    assert ost.materializza(str(repo), c, str(out)) is True
    assert os.access(str(out / "tool"), os.X_OK) and not os.access(str(out / "a.py"), os.X_OK)


def test_materializza_collisione_file_cartella_non_solleva(tmp_path):
    repo = tmp_path / "r"
    _init(repo)
    c = _commit_da_tree(repo, [("100644", "X", b"1\n"), ("100644", "x/y", b"2\n")])
    out = tmp_path / "out"
    out.mkdir()
    esito = ost.materializza(str(repo), c, str(out))   # case-insensitive: False; case-sensitive: True
    assert esito in (True, False)


def test_esegui_tree_con_cartella_git_non_verificabile(caso):
    base = _git(caso["cliente"], "rev-parse", "HEAD")
    c = _commit_da_tree(caso["cliente"], [("100644", "src/" + caso["file"], ("%s\n" % caso["riga"]).encode()),
                                          ("100644", ".GIT/info", b"*\n")], genitore=base)
    _git(caso["cliente"], "reset", "-q", "--soft", c)
    rep = esegui(caso)
    assert rep["esito"] == ost.NON_VERIFICABILE and "non sicuro" in rep["motivo"], (base, rep.get("motivo"))


# --- integrazione coi binari reali (prova D8 della CLI) ---------------------------------------

REALI = {k: "/opt/homebrew/bin/" + k for k in ("semgrep", "trivy")}


@pytest.mark.parametrize("nome", sorted(REALI))
def test_integrazione_scanner_reale(nome, tmp_path):
    exe = REALI[nome]
    if not os.path.isfile(exe):
        pytest.skip("integrazione NON eseguita: %s non installato" % nome)
    _, sha, _, err = si.misura(nome, exe)
    assert err is None, err
    f = tmp_path / "factory"
    _init(f)
    _scrivi(f / "factory.config.yaml",
            "code_paths:\n  - name: cliente\n    path: code_repos/cliente/\n"
            "security_scan:\n  semgrep_ruleset: security/rules.yml\n  trivy_config: security/trivy.yaml\n")
    _scrivi(f / "security" / "rules.yml", "rules:\n  - id: fake-eval\n    pattern: eval($X)\n"
            "    languages: [python]\n    severity: ERROR\n    message: eval\n")
    _scrivi(f / "security" / "trivy.yaml", "severity:\n  - HIGH\n  - CRITICAL\n")
    _scrivi(f / "security" / "scanner-pins.json",
            json.dumps({nome: [{"path": exe, "sha256": sha, "version": si.leggi_versione(nome, os.path.realpath(exe))}]}))
    _commit(f, "factory", protetto=True)
    cl = f / "code_repos" / "cliente"
    _init(cl)
    _scrivi(cl / "app.py", "def f(d):\n    return eval(d)\n")
    _scrivi(cl / "main.tf", 'resource "aws_s3_bucket" "b" {\n  bucket = "x"\n  acl    = "public-read"\n}\n')
    _commit(cl, "base", protetto=True)
    scanner = sast_guard.SEMGREP if nome == "semgrep" else iac_guard.TRIVY
    rep = ost.esegui(scanner, str(cl), str(f))
    assert rep["esito"] == ost.PASS, rep.get("motivo")
    assert rep["identita"]["stato"] == si.IDENTIFICATO
    ids = {v["identita"][1] for v in rep["confronto"]["voci"]}
    assert ids and all(v["esito"] == "persistente" for v in rep["confronto"]["voci"])
    if nome == "semgrep":
        assert ids == {"fake-eval"}, ids           # senza il prefisso della cartella temporanea
    # finding nuovo col binario reale
    _scrivi(cl / "altro.py", "x = eval(input())\n")
    _scrivi(cl / "altro.tf", 'resource "aws_s3_bucket" "c" {\n  bucket = "y"\n  acl    = "public-read"\n}\n')
    _commit(cl, "nuovo")
    assert ost.esegui(scanner, str(cl), str(f))["esito"] == ost.FAIL
    if nome == "semgrep":
        # iter-3 N2: uno script senza estensione e' riconosciuto dallo shebang solo se eseguibile
        _scrivi(cl / "bin" / "tool", "#!/usr/bin/env python3\nx = eval(input())\n", eseguibile=True)
        _commit(cl, "script")
        rep = ost.esegui(scanner, str(cl), str(f))
        assert any(v["identita"][2].startswith("bin/tool") for v in rep["confronto"]["voci"]), rep["confronto"]["voci"]
        # R2: un file nuovo oltre 1 MB era saltato in silenzio col default di --max-target-bytes
        _git(cl, "rm", "-q", "altro.py")
        _commit(cl, "via")
        _git(cl, "update-ref", "refs/remotes/origin/main", "HEAD")
        _scrivi(cl / "grande.py", "x = eval(input())\n" + "# riempitivo\n" * 100000)
        _commit(cl, "grande")
        rep = ost.esegui(scanner, str(cl), str(f))
        assert rep["esito"] == ost.FAIL and any(v["identita"][2].startswith("grande.py")
                                                for v in rep["confronto"]["voci"] if v["esito"] == "nuovo")


# --- CQRL iter-4 ------------------------------------------------------------------------------

def test_path_non_utf8_non_verificabile(tmp_path):
    """N6: con decode("replace") due path non UTF-8 diventavano lo stesso nome: uno sovrascriveva l'altro."""
    repo = tmp_path / "r"
    _init(repo)
    def blob(d):
        return subprocess.run(["git", "-C", str(repo), "hash-object", "-w", "--stdin"], input=d,
                              stdout=subprocess.PIPE, check=True).stdout.strip()
    inp = (b"100644 blob " + blob(b"eval(x)\n") + b"\tevil\xfe.py\n" +
           b"100644 blob " + blob(b"1\n") + b"\tevil\xff.py\n")
    t = subprocess.run(["git", "-C", str(repo), "mktree"], input=inp, stdout=subprocess.PIPE, check=True).stdout.decode().strip()
    c = subprocess.run(["git", "-C", str(repo), "commit-tree", t, "-m", "x"], stdout=subprocess.PIPE, check=True).stdout.decode().strip()
    assert ost.materializza(str(repo), c, str(tmp_path / "out")) is False
    assert ost.file_presenti(str(repo), c) is None


def test_oggetto_dichiarato_blob_ma_tree_non_blocca(tmp_path):
    """N7: un tree grande dichiarato blob lasciava cat-file appeso e l'oracolo bloccato per sempre."""
    import binascii
    import threading
    repo = tmp_path / "r"
    _init(repo)
    b = subprocess.run(["git", "-C", str(repo), "hash-object", "-w", "--stdin"], input=b"x\n",
                       stdout=subprocess.PIPE, check=True).stdout.decode().strip()
    inp = "".join("100644 blob %s\tf_%05d.txt\n" % (b, i) for i in range(3000)).encode()
    grande = subprocess.run(["git", "-C", str(repo), "mktree"], input=inp, stdout=subprocess.PIPE, check=True).stdout.decode().strip()
    raw = b"100644 aaa_finto.py\0" + binascii.unhexlify(grande)
    t = subprocess.run(["git", "-C", str(repo), "hash-object", "-t", "tree", "-w", "--literally", "--stdin"],
                       input=raw, stdout=subprocess.PIPE, check=True).stdout.decode().strip()
    c = subprocess.run(["git", "-C", str(repo), "commit-tree", t, "-m", "x"], stdout=subprocess.PIPE, check=True).stdout.decode().strip()
    out = tmp_path / "out"
    out.mkdir()
    esito = []
    th = threading.Thread(target=lambda: esito.append(ost.materializza(str(repo), c, str(out))), daemon=True)
    th.start()
    th.join(60)
    assert esito == [False], "materializza bloccata o non fallita: %r" % esito

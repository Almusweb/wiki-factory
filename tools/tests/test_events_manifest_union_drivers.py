"""Merge driver `factory-events-union` e `factory-manifest-union` e loro registrazione."""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RADICE = Path(__file__).resolve().parents[2]
TOOLS = RADICE / "tools"
EVENTI = "analytics/events/2026-11.jsonl"
MANIFEST = "raw/.extraction-manifest.json"


def _carica(nome: str, percorso: Path):
    spec = importlib.util.spec_from_file_location(nome, percorso)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(percorso.parent))
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.path.remove(str(percorso.parent))
    return mod


installer = _carica("install_factory_hooks_t2", TOOLS / "vcs" / "install_factory_hooks.py")


@pytest.fixture(autouse=True)
def git_isolato(monkeypatch, tmp_path_factory):
    vuoto = tmp_path_factory.mktemp("gitcfg") / "config"
    vuoto.write_text("", encoding="utf-8")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(vuoto))
    monkeypatch.setenv("GIT_CONFIG_SYSTEM", str(vuoto))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode:
        raise AssertionError(f"git {' '.join(args)}: {r.stdout}{r.stderr}")
    return r


def dump(d: dict) -> str:
    return json.dumps(d, indent=2, ensure_ascii=False) + "\n"


BASE_EVENTI = '{"id":"base1"}\n{"id":"base2"}\n'
BASE_MANIFEST = {"a": {"source": "x", "note": "è"}, "b": {"source": "y"}}


def crea_repo(tmp_path: Path, con_driver: bool) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "checkout", "-q", "-b", "main")
    git(repo, "config", "user.email", "prova@example.invalid")
    git(repo, "config", "user.name", "prova")
    shutil.copy2(RADICE / ".gitattributes", repo / ".gitattributes")
    (repo / "analytics" / "events").mkdir(parents=True)
    (repo / "raw").mkdir()
    (repo / EVENTI).write_text(BASE_EVENTI, encoding="utf-8")
    (repo / MANIFEST).write_text(dump(BASE_MANIFEST), encoding="utf-8")
    (repo / "tools" / "wiki").mkdir(parents=True)
    for nome in ("events_union_driver.py", "manifest_union_driver.py"):
        shutil.copy2(TOOLS / "wiki" / nome, repo / "tools" / "wiki")
    git(repo, "add", "--", ".")
    git(repo, "commit", "-q", "-m", "base")
    if con_driver:
        assert set(installer.ensure_merge_drivers(repo).values()) == {"installed"}
    return repo


def ramo(repo: Path, nome: str, percorso: str, scrivi) -> None:
    git(repo, "checkout", "-q", "-b", nome, "main")
    f = repo / percorso
    f.write_text(scrivi(f.read_text(encoding="utf-8")), encoding="utf-8")
    git(repo, "commit", "-q", "-am", nome)


def unisci(repo: Path) -> subprocess.CompletedProcess:
    git(repo, "checkout", "-q", "ramo-a")
    return git(repo, "merge", "-q", "ramo-b", "-m", "merge", check=False)


def conflitti(repo: Path):
    return git(repo, "diff", "--name-only", "--diff-filter=U").stdout.split()


# --- attributi ----------------------------------------------------------------

def test_gitattributes_assegna_i_due_driver():
    r = subprocess.run(["git", "-C", str(RADICE), "check-attr", "merge", "--", EVENTI, MANIFEST],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert f"{EVENTI}: merge: factory-events-union" in r.stdout
    assert f"{MANIFEST}: merge: factory-manifest-union" in r.stdout


# --- eventi -------------------------------------------------------------------

def test_eventi_righe_diverse_in_coda_si_fondono(tmp_path):
    repo = crea_repo(tmp_path, con_driver=True)
    ramo(repo, "ramo-a", EVENTI, lambda t: t + '{"id":"A1"}\n{"id":"A2"}\n')
    ramo(repo, "ramo-b", EVENTI, lambda t: t + '{"id":"B1"}\n')
    r = unisci(repo)
    assert r.returncode == 0, r.stdout + r.stderr
    assert conflitti(repo) == []
    assert (repo / EVENTI).read_text(encoding="utf-8") == BASE_EVENTI + '{"id":"A1"}\n{"id":"A2"}\n{"id":"B1"}\n'


def test_eventi_riga_identica_su_entrambi_i_lati_una_sola_volta(tmp_path):
    repo = crea_repo(tmp_path, con_driver=True)
    ramo(repo, "ramo-a", EVENTI, lambda t: t + '{"id":"comune"}\n{"id":"A1"}\n')
    ramo(repo, "ramo-b", EVENTI, lambda t: t + '{"id":"B1"}\n{"id":"comune"}\n')
    r = unisci(repo)
    assert r.returncode == 0, r.stdout + r.stderr
    righe = (repo / EVENTI).read_text(encoding="utf-8").splitlines()
    assert righe.count('{"id":"comune"}') == 1
    assert sorted(righe) == sorted(['{"id":"base1"}', '{"id":"base2"}', '{"id":"comune"}',
                                    '{"id":"A1"}', '{"id":"B1"}'])


def test_eventi_senza_driver_conflitto_come_prima(tmp_path):
    repo = crea_repo(tmp_path, con_driver=False)
    ramo(repo, "ramo-a", EVENTI, lambda t: t + '{"id":"A1"}\n')
    ramo(repo, "ramo-b", EVENTI, lambda t: t + '{"id":"B1"}\n')
    r = unisci(repo)
    assert r.returncode != 0
    assert conflitti(repo) == [EVENTI]
    git(repo, "merge", "--abort")


# --- manifest -----------------------------------------------------------------

def test_manifest_chiavi_diverse_dai_due_lati(tmp_path):
    repo = crea_repo(tmp_path, con_driver=True)
    ramo(repo, "ramo-a", MANIFEST,
         lambda t: dump({**json.loads(t), "ñ-chiave-a": {"source": "A", "titolo": "perché"}}))
    ramo(repo, "ramo-b", MANIFEST, lambda t: dump({**json.loads(t), "chiave-b": {"source": "B"}}))
    r = unisci(repo)
    assert r.returncode == 0, r.stdout + r.stderr
    assert conflitti(repo) == []
    testo = (repo / MANIFEST).read_text(encoding="utf-8")
    atteso = {**BASE_MANIFEST, "ñ-chiave-a": {"source": "A", "titolo": "perché"},
              "chiave-b": {"source": "B"}}
    assert json.loads(testo) == atteso
    assert testo == dump(atteso)  # indent=2, ensure_ascii=False, ordine: nostro poi nuove dei loro
    assert "perché" in testo and "\\u" not in testo


def test_manifest_stessa_chiave_modificata_in_modo_diverso_e_conflitto(tmp_path):
    repo = crea_repo(tmp_path, con_driver=True)
    ramo(repo, "ramo-a", MANIFEST, lambda t: dump({**json.loads(t), "a": {"source": "da A"}}))
    ramo(repo, "ramo-b", MANIFEST, lambda t: dump({**json.loads(t), "a": {"source": "da B"}}))
    r = unisci(repo)
    assert r.returncode != 0
    assert conflitti(repo) == [MANIFEST]
    git(repo, "merge", "--abort")


def test_manifest_stessa_chiave_modificata_da_un_solo_lato_o_ugualmente(tmp_path):
    repo = crea_repo(tmp_path, con_driver=True)
    ramo(repo, "ramo-a", MANIFEST, lambda t: dump({**json.loads(t), "a": {"source": "nuovo"}}))
    ramo(repo, "ramo-b", MANIFEST, lambda t: dump({**json.loads(t), "b": {"source": "y"}, "c": 1}))
    assert unisci(repo).returncode == 0
    assert json.loads((repo / MANIFEST).read_text(encoding="utf-8")) == {"a": {"source": "nuovo"}, "b": {"source": "y"}, "c": 1}


def test_manifest_driver_funzioni_di_merge():
    drv = _carica("manifest_union_driver_t", TOOLS / "wiki" / "manifest_union_driver.py")
    assert drv.merge({}, {"x": 1}, {"x": 1, "y": 2}) == {"x": 1, "y": 2}
    assert drv.merge({"x": 1}, {}, {"x": 1}) == {}  # tolta da un lato, invariata dall'altro
    with pytest.raises(drv.Conflitto):
        drv.merge({"x": 1}, {"x": 2}, {"x": 3})
    with pytest.raises(drv.Conflitto):
        drv.merge({}, {"x": 2}, {"x": 3})  # aggiunta con valori diversi
    assert drv.main([]) == 2


def test_manifest_driver_json_non_valido_esce_non_zero(tmp_path):
    p = {n: tmp_path / n for n in ("o", "a", "b")}
    p["o"].write_text("{}", encoding="utf-8")
    p["a"].write_text("{rotto", encoding="utf-8")
    p["b"].write_text("{}", encoding="utf-8")
    r = subprocess.run([sys.executable, str(TOOLS / "wiki" / "manifest_union_driver.py"),
                        str(p["o"]), str(p["a"]), str(p["b"])], capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r.returncode == 1
    assert p["a"].read_text(encoding="utf-8") == "{rotto"


def test_manifest_reale_serializzazione_identica(tmp_path):
    """Il file reale del repo e' gia' nel formato del driver: un merge senza modifiche non lo riscrive."""
    reale = RADICE / MANIFEST
    if not reale.exists():
        pytest.skip("manifest assente")
    drv = _carica("manifest_union_driver_t2", TOOLS / "wiki" / "manifest_union_driver.py")
    testo = reale.read_text(encoding="utf-8")
    assert drv.serializza(json.loads(testo)) == testo


# --- registrazione ------------------------------------------------------------

def _config_locale(repo: Path) -> str:
    return git(repo, "config", "--local", "--list").stdout


def test_installer_registra_i_due_driver_ed_e_idempotente(tmp_path):
    repo = crea_repo(tmp_path, con_driver=False)
    esiti = installer.ensure_merge_drivers(repo)
    assert esiti["factory-events-union"] == "installed" and esiti["factory-manifest-union"] == "installed"
    dopo1 = _config_locale(repo)
    assert "merge.factory-events-union.driver=python3 tools/wiki/events_union_driver.py %O %A %B" in dopo1
    assert "merge.factory-manifest-union.driver=python3 tools/wiki/manifest_union_driver.py %O %A %B" in dopo1
    assert set(installer.ensure_merge_drivers(repo).values()) == {"ok"}
    assert _config_locale(repo) == dopo1

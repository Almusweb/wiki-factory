"""Check 4bf (ordine di wiki/log.md) e 4bg (contatore Sources di wiki/index.md)."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

RADICE = Path(__file__).resolve().parents[2]
TOOLS = RADICE / "tools"
PY = sys.executable

TESTA_LOG = (
    "---\ntype: wiki-log\nappend_only: true\n---\n\n# Wiki Log\n\n"
    "---\ndate: 2026-11-01\ntype: develop\ncontext: voce di partenza\n---\n"
)


def voce(data: str, contesto: str) -> str:
    return f"\n---\ndate: {data}\ntype: develop\ncontext: {contesto}\n---\n"


def _carica(nome: str, percorso: Path):
    spec = importlib.util.spec_from_file_location(nome, percorso)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


derivati = _carica("check_dati_derivati_t", TOOLS / "lint" / "check_dati_derivati.py")


def _wiki(tmp_path: Path, log: str | None = None, index: str | None = None) -> Path:
    (tmp_path / "wiki").mkdir(exist_ok=True)
    if log is not None:
        (tmp_path / "wiki" / "log.md").write_text(log, encoding="utf-8")
    if index is not None:
        (tmp_path / "wiki" / "index.md").write_text(index, encoding="utf-8")
    return tmp_path


def _cli(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([PY, str(TOOLS / "lint" / "check_dati_derivati.py"), *args, str(root)],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


def test_4bf_log_in_ordine_non_segnala(tmp_path):
    root = _wiki(tmp_path, TESTA_LOG + voce("2026-11-02", "b") + voce("2026-11-05", "c"))
    findings, entro = derivati.check_ordine_log(root, 7)
    assert findings == [] and entro == 0
    assert _cli(root, "--strict").returncode == 0


def test_4bf_ordine_rotto_fallisce_il_lint(tmp_path):
    root = _wiki(tmp_path, TESTA_LOG + voce("2026-11-09", "recente") + voce("2026-09-01", "molto vecchia"))
    findings, _ = derivati.check_ordine_log(root, 7)
    assert len(findings) == 1
    f = findings[0]
    assert f["check"] == "4bf" and f["data"] == "2026-09-01" and f["precedente"] == "2026-11-09"
    assert f["giorni"] == 69
    out = _cli(root, "--strict")
    assert out.returncode == 1 and "[4bf]" in out.stdout and "[ERROR]" in out.stdout
    # senza --strict il comando riporta ma non fallisce
    assert _cli(root).returncode == 0


def test_4bf_tolleranza_di_sette_giorni(tmp_path):
    log = TESTA_LOG + voce("2026-11-10", "avanti") + voce("2026-11-03", "indietro di 7")
    root = _wiki(tmp_path, log)
    findings, entro = derivati.check_ordine_log(root, 7)
    assert findings == [] and entro == 1
    findings, entro = derivati.check_ordine_log(root, 6)
    assert len(findings) == 1 and entro == 0
    assert _cli(root, "--strict", "--tolleranza", "6").returncode == 1
    assert _cli(root, "--strict").returncode == 0


def test_4bf_riconosce_anche_le_voci_a_titolo(tmp_path):
    log = "# Log\n\n## 2026-11-10 10:00 — nuova\n\ntesto\n\n## 2026-10-01 10:00 — vecchia dopo\n\ntesto\n"
    findings, _ = derivati.check_ordine_log(_wiki(tmp_path, log), 7)
    assert [f["data"] for f in findings] == ["2026-10-01"]


def test_4bf_senza_log_nessun_finding(tmp_path):
    assert derivati.check_ordine_log(tmp_path, 7) == ([], 0)


def test_4bf_il_confronto_e_con_la_data_massima_non_con_la_precedente(tmp_path):
    log = TESTA_LOG + voce("2026-11-20", "a") + voce("2026-11-10", "b") + voce("2026-11-09", "c")
    findings, _ = derivati.check_ordine_log(_wiki(tmp_path, log), 7)
    assert [f["data"] for f in findings] == ["2026-11-10", "2026-11-09"]
    assert all(f["precedente"] == "2026-11-20" for f in findings)


def _index(dichiarato: int, voci: int, dopo: str = "## Altro\n\n- [[fuori-sezione]]\n") -> str:
    corpo = "".join(f"- [[fonte-{i}]]\n" for i in range(voci))
    return f"# Index\n\n## Sources ({dichiarato})\n\n<!-- commento -->\n{corpo}\n{dopo}"


def test_4bg_contatore_corretto_accettato(tmp_path):
    root = _wiki(tmp_path, index=_index(3, 3))
    assert derivati.check_contatore_sources(root) is None
    assert "contatore Sources coerente" in _cli(root, "--strict").stdout
    assert _cli(root, "--strict").returncode == 0


def test_4bg_scarto_segnalato_con_i_due_valori(tmp_path):
    root = _wiki(tmp_path, index=_index(2, 5))
    f = derivati.check_contatore_sources(root)
    assert f == {"check": "4bg", "dichiarato": 2, "reale": 5, "scarto": 3}
    out = _cli(root, "--strict")
    assert out.returncode == 1
    assert "[WARNING][sources-contatore][4bg]" in out.stdout and "Sources (2)" in out.stdout and "5 voci" in out.stdout


def test_4bg_contatore_superiore_alle_voci(tmp_path):
    f = derivati.check_contatore_sources(_wiki(tmp_path, index=_index(9, 4)))
    assert f["scarto"] == -5


def test_4bg_conta_solo_la_sezione_sources(tmp_path):
    # la voce dopo «## Altro» non entra nel conteggio; ultima sezione senza intestazione successiva
    assert derivati.check_contatore_sources(_wiki(tmp_path, index=_index(2, 2))) is None
    solo = "# Index\n\n## Sources (1)\n\n- [[a]]\n- [[b]]\n"
    assert derivati.check_contatore_sources(_wiki(tmp_path, index=solo))["reale"] == 2


def test_4bg_senza_sezione_o_senza_index_nessun_finding(tmp_path):
    assert derivati.check_contatore_sources(tmp_path) is None
    assert derivati.check_contatore_sources(_wiki(tmp_path, index="# Index\n\n## Altro\n")) is None


def test_json_riporta_entrambi_i_check(tmp_path):
    root = _wiki(tmp_path, TESTA_LOG + voce("2026-11-20", "a") + voce("2026-10-01", "b"), _index(1, 2))
    dati = json.loads(_cli(root, "--json").stdout)
    assert {f["check"] for f in dati["findings"]} == {"4bf", "4bg"}


def test_4bg_sul_repository_reale_e_in_sola_lettura():
    """Il check gira sui file reali senza modificarli e produce solo finding ben formati."""
    index = RADICE / "wiki" / "index.md"
    if not index.is_file():
        # una derivata puo' non avere l'indice: il check torna None, non c'e' niente da leggere
        assert derivati.check_contatore_sources(RADICE) is None
        return
    prima = index.read_bytes()
    f = derivati.check_contatore_sources(RADICE)
    assert f is None or {"dichiarato", "reale", "scarto"} <= set(f)
    assert index.read_bytes() == prima


def test_registrato_nel_runner_deterministico():
    mod = _carica("run_det_t", TOOLS / "lint" / "run-deterministic.py")
    voci = [c for c in mod.CHECKS if "4bf" in c[0]]
    assert len(voci) == 1 and voci[0][0] == ("4bf", "4bg")
    assert (TOOLS / "lint" / voci[0][2]).is_file()
    assert "{root}" in voci[0][3]


# --- esenzioni per voce del 4bf ---------------------------------------------------------------

def _esenzioni(root: Path, righe: str) -> None:
    (root / "tools" / "lint").mkdir(parents=True, exist_ok=True)
    (root / "tools" / "lint" / "log-ordine-esenzioni.txt").write_text(righe, encoding="utf-8")


def _impronta(root: Path, data: str) -> str:
    out = _cli(root, "--impronte").stdout.splitlines()
    return next(r.split()[1] for r in out if r.startswith(data))


def test_4bf_voce_esentata_non_segnalata_e_non_sposta_la_massima(tmp_path):
    log = TESTA_LOG + voce("2026-11-20", "fuori ordine in avanti") + voce("2026-11-02", "normale")
    root = _wiki(tmp_path, log)
    # senza esenzione: la voce del 02/11 e' 18 giorni dietro quella del 20/11
    assert len(derivati.check_ordine_log(root, 7)[0]) == 1
    # la voce anomala qui e' quella del 20/11 (avanti): se la esento, il 02/11 torna in ordine
    impr = derivati._voci((root / "wiki" / "log.md").read_text(encoding="utf-8"))[1][2]
    _esenzioni(root, f"2026-11-20 {impr} voce datata in avanti per errore\n")
    stato = {}
    findings, _ = derivati.check_ordine_log(root, 7, stato)
    assert findings == [] and len(stato["esentate"]) == 1 and stato["avvisi"] == []
    out = _cli(root, "--strict")
    assert out.returncode == 0 and "1 voci esentate" in out.stdout


def test_4bf_esenzione_copre_solo_quella_voce(tmp_path):
    log = (TESTA_LOG + voce("2026-11-20", "recente") + voce("2026-10-01", "vecchia A")
           + voce("2026-10-01", "vecchia B"))
    root = _wiki(tmp_path, log)
    _esenzioni(root, f"2026-10-01 {_impronta(root, '2026-10-01')} solo la prima\n")
    findings, _ = derivati.check_ordine_log(root, 7)
    assert len(findings) == 1 and findings[0]["data"] == "2026-10-01"


def test_4bf_impronta_indipendente_dal_numero_di_riga(tmp_path):
    corpo = voce("2026-11-20", "recente") + voce("2026-10-01", "vecchia")
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    a = _wiki(tmp_path / "a", TESTA_LOG + corpo)
    b = _wiki(tmp_path / "b", TESTA_LOG + "\nriga in piu'\n\naltra riga\n" + corpo)
    assert _impronta(a, "2026-10-01") == _impronta(b, "2026-10-01")


def test_4bf_esenzione_orfana_e_senza_motivo_sono_warning(tmp_path):
    root = _wiki(tmp_path, TESTA_LOG + voce("2026-11-02", "b"))
    _esenzioni(root, "# commento\n2026-01-01 0123456789ab voce che non esiste piu'\n"
                     "2026-11-02 abcdefabcdef\n")
    stato = {}
    findings, _ = derivati.check_ordine_log(root, 7, stato)
    codici = sorted(a["codice"] for a in stato["avvisi"])
    assert findings == [] and codici == ["esenzione-orfana", "esenzione-senza-motivo"]
    out = _cli(root, "--strict")
    assert out.returncode == 1 and "[WARNING][esenzione-orfana][4bf]" in out.stdout
    assert "[WARNING][esenzione-senza-motivo][4bf]" in out.stdout and "[ERROR]" not in out.stdout


def test_4bf_repository_reale_a_zero_con_le_esenzioni_dichiarate():
    if not (RADICE / "meta-prompts" / "README.md").is_file():
        pytest.skip("solo nel meta-framework: il log e le esenzioni di una derivata sono suoi")
    out = _cli(RADICE, "--json")
    d = json.loads(out.stdout)
    assert [f for f in d["findings"] if f.get("check") == "4bf"] == []


def test_4bf_esenzioni_del_master_non_arrivano_in_una_factory_nuova(tmp_path):
    sys.path.insert(0, str(TOOLS))
    import factory_scope as fs
    assert fs.is_meta_only("tools/lint/log-ordine-esenzioni.txt")
    # una derivata senza il file di esenzioni: nessun finding ne' avviso, anche con un log fuori ordine
    root = _wiki(tmp_path, TESTA_LOG + voce("2026-11-02", "b"))
    stato = {}
    findings, esenzioni = derivati.check_ordine_log(root, 7, stato)
    assert [f for f in findings if f.get("codice") == "esenzione-orfana"] == []
    assert stato.get("avvisi", []) == []

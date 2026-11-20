"""
Riconciliazione dello store con i transcript dell'operatore (cost_alert.py reconcile).

Fixture neutre in tmp_path: una factory di prova, una radice di transcript con piu' cartelle e
uno store di eventi. Prezzi di prova (USD per 1M token): input 1, output 2, lettura cache 0.5,
scrittura cache 5m 4, scrittura cache 1h 8: ogni voce si legge dal numero di token.
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[2] / "tools" / "analytics" / "cost_alert.py"
_spec = importlib.util.spec_from_file_location("cost_alert_reconcile", _SCRIPT)
ca = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ca)

M = 1_000_000
PRICING = """currency: USD
models:
  - id: test-model
    pricing:
      - valid_from: 2026-01-01
        input_per_1m_tokens: 1.0
        output_per_1m_tokens: 2.0
        cache_read_per_1m_tokens: 0.5
        cache_write_per_1m_tokens: 4.0
        cache_write_1h_per_1m_tokens: 8.0
"""
# input 1M (1) + output 1M (2) + lettura 2M (1) + scrittura 1M di cui 0.4M a 1h (2.4 + 3.2)
USAGE = {"input": M, "output": M, "cache_read": 2 * M, "cache_write": M, "cache_write_1h": 400_000}
FULL, NO_READ = 9.6, 8.6


def _now(seconds=5) -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=seconds)


def _iso(t: dt.datetime) -> str:
    return t.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _config(extra: str = "") -> str:
    return "analytics:\n  cost_alert:\n    enabled: true\n    agent: false\n" + extra


def _factory(tmp_path, config=None, pricing=PRICING) -> Path:
    root = tmp_path / "factory"
    (root / "analytics").mkdir(parents=True)
    (root / "factory.config.yaml").write_text(config or _config(), encoding="utf-8")
    if pricing is not None:
        (root / "analytics" / "pricing.yaml").write_text(pricing, encoding="utf-8")
    (root / "analytics" / "alert-rules.yaml").write_text(
        "version: 1\nrules:\n  - period: weekly\n    threshold_usd: 1000\n    action: warn\n",
        encoding="utf-8")
    return root


def _assistant(mid, usage, ts, version=None):
    d = {"type": "assistant", "timestamp": _iso(ts), "message": {
        "id": mid, "model": "test-model", "usage": {
            "input_tokens": usage["input"], "output_tokens": usage["output"],
            "cache_read_input_tokens": usage["cache_read"],
            "cache_creation_input_tokens": usage["cache_write"],
            "cache_creation": {"ephemeral_1h_input_tokens": usage["cache_write_1h"]}}}}
    if version:
        d["version"] = version
    return json.dumps(d)


def _folder(troot: Path, name: str, usage: dict, sid="aaaaaaaa-0000", version=None) -> Path:
    d = troot / name
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{sid}.jsonl").write_text(_assistant(f"m-{name}", usage, _now(), version) + "\n",
                                    encoding="utf-8")
    return d


def _event(task_id, usage, ts=None):
    return {"task_id": task_id, "task_type": "session-aggregate", "state": "finished",
            "ts": _iso(ts or _now(2)), "model": "test-model", "tokens": usage}


def _store(root: Path, *events):
    d = root / "analytics" / "events"
    d.mkdir(parents=True, exist_ok=True)
    (d / "e.jsonl").write_text("\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8")


def _setup(tmp_path, config=None, factory_usage=USAGE, other_usage=None, store_usage=USAGE):
    root = _factory(tmp_path, config)
    troot = tmp_path / "projects"
    _folder(troot, ca.transcripts_dir(root).name, factory_usage)
    if other_usage:
        _folder(troot, "elsewhere", other_usage, sid="bbbbbbbb-0000")
    if store_usage:
        _store(root, _event("session:aaaaaaaa:main:test-model", store_usage))
    return root, troot


def _run(root, troot, capsys, *extra, cmd="reconcile", period="weekly"):
    argv = ["--root", str(root), "--project-dir", str(root), "--transcripts-dir",
            str(troot / "x"), cmd, "--period", period, "--transcripts-root", str(troot), *extra]
    code = ca.main(argv)
    return code, capsys.readouterr().out


def test_operator_sum_due_cartelle_con_e_senza_cache_read(tmp_path):
    root, troot = _setup(tmp_path, other_usage={**USAGE, "cache_read": 0, "cache_write": 0,
                                                "cache_write_1h": 0, "output": 0})
    pricer = ca.Pricer(root)
    now = dt.datetime.now().astimezone()
    op = ca.operator_sum(troot, pricer, ca.period_start("weekly", now), now,
                         ca.factory_folder_names(root))
    assert op["cost_usd"] == pytest.approx(FULL + 1.0)
    assert op["cost_usd_excl_cache_read"] == pytest.approx(NO_READ + 1.0)
    assert op["attributed_cost_usd"] == pytest.approx(FULL)
    assert op["attributed_cost_usd_excl_cache_read"] == pytest.approx(NO_READ)
    assert set(op["by_project_dir"]) == {ca.transcripts_dir(root).name, "elsewhere"}


def test_scrittura_cache_5m_e_1h_prezzate_separatamente(tmp_path):
    root, troot = _setup(tmp_path)
    now = dt.datetime.now().astimezone()
    op = ca.operator_sum(troot, ca.Pricer(root), ca.period_start("weekly", now), now,
                         ca.factory_folder_names(root))
    assert op["by_component"]["cache_write_5m"] == pytest.approx(0.6 * 4.0)
    assert op["by_component"]["cache_write_1h"] == pytest.approx(0.4 * 8.0)
    assert op["by_component"]["cache_read"] == pytest.approx(1.0)


def test_etichetta_affidabile_con_store_uguale(tmp_path, capsys):
    root, troot = _setup(tmp_path)
    code, out = _run(root, troot, capsys, "--json")
    r = json.loads(out)
    assert code == 0 and r["label"] == "affidabile"
    assert r["store"]["cost_usd"] == pytest.approx(FULL)
    assert r["store"]["cost_usd_excl_cache_read"] == pytest.approx(NO_READ)
    assert r["gap"]["pct"] == 0 and r["gap_excl_cache_read"]["pct"] == 0
    assert r["threshold"] == 0.05 and "da confermare" in r["threshold_note"]


def test_etichetta_sottostima(tmp_path, capsys):
    half = {**USAGE, "output": 0}  # store senza l'output: 2 USD in meno
    root, troot = _setup(tmp_path, store_usage=half)
    r = json.loads(_run(root, troot, capsys, "--json")[1])
    assert r["label"] == "sottostima" and r["gap"]["pct"] == pytest.approx(2 / 9.6 * 100, abs=0.01)


def test_soglia_dalla_config(tmp_path, capsys):
    # store 3% sotto: affidabile col default 5%, sottostima con soglia 0.02
    under = {**USAGE, "output": M - 144_000}  # 0.288 USD in meno su 9.6 = 3%
    root, troot = _setup(tmp_path, store_usage=under)
    assert json.loads(_run(root, troot, capsys, "--json")[1])["label"] == "affidabile"
    root2, troot2 = _setup(tmp_path / "b", config=_config(
        "  reconcile:\n    underestimate_threshold: 0.02\n"), store_usage=under)
    r = json.loads(_run(root2, troot2, capsys, "--json")[1])
    assert r["label"] == "sottostima" and r["threshold"] == 0.02


def test_config_assente_o_non_valida_usa_i_default(tmp_path):
    root = _factory(tmp_path)
    assert ca.load_reconcile_config(root) == {"underestimate_threshold": 0.05,
                                              "worktree_aliases": [], "errors": []}
    (root / "factory.config.yaml").write_text(_config(
        "  reconcile:\n    underestimate_threshold: 7\n    worktree_aliases: ['(', 'ok-.*']\n"),
        encoding="utf-8")
    cfg = ca.load_reconcile_config(root)
    assert cfg["underestimate_threshold"] == 0.05 and cfg["worktree_aliases"] == ["ok-.*"]
    assert len(cfg["errors"]) == 2


def test_alias_dalla_config_attribuiscono_una_cartella(tmp_path, capsys):
    extra = {"input": M, "output": 0, "cache_read": 0, "cache_write": 0, "cache_write_1h": 0}
    store_all = {**USAGE, "input": 2 * M}  # lo store include anche il lavoro dell'alias
    root, troot = _setup(tmp_path, other_usage=extra, store_usage=store_all)
    r = json.loads(_run(root, troot, capsys, "--json")[1])
    assert r["operator"]["attributed_folders"] == [ca.transcripts_dir(root).name]
    assert r["label"] == "affidabile" and r["gap"]["pct"] < 0  # store sopra: non sottostima
    # alias su "elsewhere": l'operatore attribuito sale e lo store pareggia
    root2, troot2 = _setup(tmp_path / "b", config=_config(
        "  reconcile:\n    worktree_aliases: ['^else']\n"), other_usage=extra,
        store_usage=store_all)
    r2 = json.loads(_run(root2, troot2, capsys, "--json")[1])
    assert "elsewhere" in r2["operator"]["attributed_folders"]
    assert r2["operator"]["attributed_cost_usd"] == pytest.approx(FULL + 1.0)
    assert r2["gap"]["pct"] == 0


def test_non_verificabile_senza_transcript(tmp_path, capsys):
    root = _factory(tmp_path)
    _store(root, _event("session:aaaaaaaa:main:test-model", USAGE))
    troot = tmp_path / "vuota"
    troot.mkdir()
    r = json.loads(_run(root, troot, capsys, "--json")[1])
    assert r["label"] == "non verificabile" and "transcript" in r["reason"]


def test_non_verificabile_listino_non_caricato(tmp_path, capsys):
    root, troot = _setup(tmp_path)
    (root / "analytics" / "pricing.yaml").write_text("models: [non: valido: :\n", encoding="utf-8")
    code, out = _run(root, troot, capsys, "--json")
    assert code == 2 and json.loads(out)["label"] == "non verificabile"   # exit 2 come ogni sottocomando
    assert "listino" in json.loads(out)["reason"]
    (root / "analytics" / "pricing.yaml").unlink()  # listino assente: tabella vuota
    assert json.loads(_run(root, troot, capsys, "--json")[1])["label"] == "non verificabile"


def test_non_verificabile_versione_non_verificata(tmp_path, capsys):
    root, troot = _setup(tmp_path)
    _folder(troot, ca.transcripts_dir(root).name, USAGE, version="0.0.1")
    r = json.loads(_run(root, troot, capsys, "--json")[1])
    assert r["label"] == "non verificabile" and "0.0.1" in r["reason"]


def test_testo_riporta_etichetta_soglia_e_scarti(tmp_path, capsys):
    root, troot = _setup(tmp_path)
    code, out = _run(root, troot, capsys)
    assert code == 0 and "affidabile" in out and "senza letture dalla cache" in out
    assert "da confermare" in out


def test_periodo_sessione(tmp_path, capsys):
    root, troot = _setup(tmp_path)
    argv = ["--root", str(root), "--project-dir", str(root), "--transcripts-dir",
            str(troot / "x"), "reconcile", "--period", "session", "--session-id",
            "aaaaaaaa-0000", "--transcripts-root", str(troot), "--json"]
    assert ca.main(argv) == 0
    r = json.loads(capsys.readouterr().out)
    assert r["label"] == "affidabile" and r["store"]["events"] == 1


def test_check_e_breakdown_portano_l_etichetta_senza_cambiare_exit(tmp_path, capsys):
    root, troot = _setup(tmp_path, other_usage=None)
    code, out = _run(root, troot, capsys, "--json", cmd="check")
    v = json.loads(out)
    assert code == 0 and v["reliability"]["label"] == "affidabile"
    code, out = _run(root, troot, capsys, cmd="check")
    assert code == 0 and "affidabilita' del costo: affidabile" in out
    code, out = _run(root, troot, capsys, "--json", cmd="breakdown")
    assert code == 0 and json.loads(out)["reliability"]["label"] == "affidabile"


def test_store_events_finestra_e_duplicati(tmp_path):
    root = _factory(tmp_path)
    e1 = _event("t1", USAGE, _now(100))
    e2 = _event("t2", USAGE, _now(1))
    d = root / "analytics" / "events"
    d.mkdir()
    (d / "e.jsonl").write_text(
        "\n".join([json.dumps(e1), json.dumps(e2), json.dumps(e2), "non json",
                   json.dumps({**e2, "task_type": "altro", "task_id": "t3"})]) + "\n",
        encoding="utf-8")
    events, dups, bad = ca.store_events(root, _iso(_now(10)))
    assert [e["task_id"] for e in events] == ["t2"] and dups == 1 and bad == 1
    # lo stesso task cumulato non si conta due volte: store_sum somma le differenze
    cum = [_event("t", {**USAGE, "input": M}, _now(50)), _event("t", {**USAGE, "input": 3 * M}, _now(1))]
    s = ca.store_sum(cum, ca.Pricer(root))
    assert s["tokens"]["input"] == 3 * M

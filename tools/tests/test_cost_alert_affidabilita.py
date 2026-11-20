"""
Affidabilita' del costo in tools/analytics/cost_alert.py e show-session-tokens.py:
listino presente ma non caricabile e somma degli eventi cumulati dello store.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, _REPO_ROOT / "tools" / "analytics" / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ca = _load("cost_alert_aff", "cost_alert.py")

PRICING = """currency: USD
models:
  - id: test-model
    pricing:
      - valid_from: 2026-01-01
        input_per_1m_tokens: 1.0
        output_per_1m_tokens: 0.0
        cache_read_per_1m_tokens: 0.0
        cache_write_per_1m_tokens: 0.0
"""


def _root(tmp_path, pricing=None) -> Path:
    root = tmp_path / "factory"
    (root / "analytics").mkdir(parents=True)
    (root / "factory.config.yaml").write_text(
        "analytics:\n  cost_alert:\n    enabled: true\n    agent: true\n", encoding="utf-8")
    (root / "analytics" / "alert-rules.yaml").write_text(
        "version: 1\nrules:\n  - period: session\n    threshold_usd: 2.0\n    action: warn\n",
        encoding="utf-8")
    if pricing is not None:
        (root / "analytics" / "pricing.yaml").write_text(pricing, encoding="utf-8")
    return root


def _argv(root, tmp_path):
    return ["--root", str(root), "--project-dir", str(root),
            "--transcripts-dir", str(tmp_path / "t"), "check", "--period", "session", "--json"]


def test_listino_illeggibile_esce_2_con_messaggio(tmp_path, capsys):
    root = _root(tmp_path, "models: [non: valido: :\n")
    with pytest.raises(ca.PricingUnavailable):
        ca.Pricer(root)
    assert ca.main(_argv(root, tmp_path)) == 2
    assert "prezzi di fallback" in capsys.readouterr().err


def test_listino_con_pyyaml_assente_esce_2(tmp_path, capsys, monkeypatch):
    root = _root(tmp_path, PRICING)
    monkeypatch.setitem(sys.modules, "yaml", None)  # import yaml -> ImportError
    assert ca.main(_argv(root, tmp_path)) == 2
    assert "non caricato" in capsys.readouterr().err


def test_listino_assente_comportamento_invariato(tmp_path, capsys):
    root = _root(tmp_path)
    pricer = ca.Pricer(root)  # nessuna eccezione
    assert pricer.table == {}
    assert ca.main(_argv(root, tmp_path)) != 2


def test_show_session_tokens_avvisa_su_stderr(tmp_path, capsys):
    root = _root(tmp_path, "models: [non: valido: :\n")
    led = _load("ledger_aff", "show-session-tokens.py")
    assert led.load_pricing(str(root)) == {}
    assert "non caricato" in capsys.readouterr().err


def test_show_session_tokens_listino_assente_resta_silenzioso(tmp_path, capsys):
    root = _root(tmp_path)
    led = _load("ledger_aff2", "show-session-tokens.py")
    assert led.load_pricing(str(root)) == {}
    assert capsys.readouterr().err == ""


def _ev(task, ts, inp, model="test-model"):
    return {"task_id": task, "ts": ts, "model": model, "tokens": {"input": inp}}


def test_store_sum_stesso_task_cumulato_non_conta_due_volte(tmp_path):
    root = _root(tmp_path, PRICING)
    events = [_ev("t1", "2026-11-01T10:00:00Z", 1_000_000),
              _ev("t1", "2026-11-01T11:00:00Z", 1_500_000)]
    naive = sum(ca.event_tokens(e)[0] for e in events)  # somma diretta: doppio conteggio
    assert naive == 2_500_000
    r = ca.store_sum(events, ca.Pricer(root))
    assert r["tokens"]["input"] == 1_500_000 and r["cost_usd"] == pytest.approx(1.5)


def test_store_sum_task_diversi_si_sommano(tmp_path):
    root = _root(tmp_path, PRICING)
    events = [_ev("t1", "2026-11-01T10:00:00Z", 1_000_000),
              _ev("t2", "2026-11-01T11:00:00Z", 500_000)]
    r = ca.store_sum(events, ca.Pricer(root))
    assert r["tokens"]["input"] == 1_500_000 and r["cost_usd"] == pytest.approx(1.5)


def test_store_sum_eventi_non_cumulati_restano_somma(tmp_path):
    root = _root(tmp_path, PRICING)
    events = [_ev("t1", "2026-11-01T10:00:00Z", 1_000_000),
              _ev("t1", "2026-11-01T11:00:00Z", 400_000)]  # cala: non e' cumulato
    assert ca.store_sum(events, ca.Pricer(root))["tokens"]["input"] == 1_400_000


def test_store_sum_finestra_usa_il_precedente_fuori_finestra(tmp_path):
    root = _root(tmp_path, PRICING)
    events = [_ev("t1", "2026-10-31T10:00:00Z", 1_000_000),
              _ev("t1", "2026-11-01T11:00:00Z", 1_500_000)]
    r = ca.store_sum(events, ca.Pricer(root), start="2026-11-01T00:00:00Z")
    assert r["tokens"]["input"] == 500_000

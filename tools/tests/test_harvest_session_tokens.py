"""harvest-session-tokens.py: scrittura dell'evento con record-event.py e l'interprete corrente.

Lo script lanciava ``record-event.sh``: su Windows un ``.sh`` non si esegue (WinError 193) e la
sessione restava senza evento di consumo. Ora lancia ``record-event.py`` con ``sys.executable``.
Qui si verificano, su una factory di prova in una cartella temporanea:

* l'evento viene scritto con lo scrittore vero, e un secondo harvest non lo duplica;
* il JSON in uscita resta lo stesso; exit 0 se tutto è registrato, 1 se un evento non lo è;
* il timeout dello scrittore diventa un evento non registrato, non un'eccezione;
* nessun riferimento residuo a ``record-event.sh`` nello script.
"""
from __future__ import annotations

import importlib.util
import io
import json
import re
import shutil
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_analytics_py import _factory  # noqa: E402 — factory di prova condivisa

ROOT = Path(__file__).resolve().parents[2]
HARVEST = ROOT / "tools" / "analytics" / "harvest-session-tokens.py"
SESSION = "1234abcd-0000-4000-8000-000000000001"


def _transcript(base: Path) -> Path:
    """Transcript minimo: due risposte di Opus (una su due righe, come lo streaming)."""
    rows = [
        {"type": "assistant", "timestamp": "2026-09-10T10:00:00Z",
         "message": {"id": "m1", "model": "claude-opus-5-5",
                     "usage": {"input_tokens": 3, "output_tokens": 10, "cache_read_input_tokens": 1000,
                               "cache_creation_input_tokens": 200,
                               "cache_creation": {"ephemeral_1h_input_tokens": 50}}}},
        {"type": "assistant", "timestamp": "2026-09-10T10:00:01Z",
         "message": {"id": "m1", "model": "claude-opus-5-5",
                     "usage": {"input_tokens": 3, "output_tokens": 40, "cache_read_input_tokens": 1000,
                               "cache_creation_input_tokens": 200,
                               "cache_creation": {"ephemeral_1h_input_tokens": 50}}}},
        {"type": "assistant", "timestamp": "2026-09-10T10:05:00Z",
         "message": {"id": "m2", "model": "claude-opus-5-5",
                     "usage": {"input_tokens": 1, "output_tokens": 5, "cache_read_input_tokens": 1200,
                               "cache_creation_input_tokens": 0}}},
    ]
    path = base / f"{SESSION}.jsonl"
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    return path


def _factory_with_harvest(tmp_path: Path) -> Path:
    root = _factory(tmp_path / "factory", events=False)
    shutil.copy2(HARVEST, root / "tools" / "analytics" / HARVEST.name)
    return root


def _harvest(root: Path, transcript: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(root / "tools" / "analytics" / HARVEST.name),
                           str(transcript), "--project", "fixture"],
                          cwd=root, capture_output=True, text=True, timeout=300, encoding="utf-8", errors="replace")


def _events(root: Path) -> list[dict]:
    path = root / "analytics" / "events" / "2026-09.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_writes_event_with_python_writer_and_is_idempotent(tmp_path):
    root = _factory_with_harvest(tmp_path)
    transcript = _transcript(tmp_path)

    first = _harvest(root, transcript)
    assert first.returncode == 0, first.stderr
    out = json.loads(first.stdout)
    assert out["status"] == "ok" and out["groups"] == 1
    assert all(r["recorded"] for r in out["results"])

    events = _events(root)
    assert len(events) == 1
    ev = events[0]
    assert ev["task_id"] == "session:1234abcd:main:claude-opus-5-5"
    assert ev["project_id"] == "fixture"
    # una risposta = un message.id: m1 conta una volta sola (massimo fra le sue righe)
    assert ev["tokens"]["output"] == 45
    assert ev["tokens"]["cache_read"] == 2200
    assert ev["tokens"]["cache_write_1h"] == 50

    second = _harvest(root, transcript)
    assert second.returncode == 0, second.stderr
    assert len(_events(root)) == 1, "il secondo harvest non deve duplicare l'evento"


def test_dry_run_writes_nothing_and_exits_zero(tmp_path):
    root = _factory_with_harvest(tmp_path)
    cp = subprocess.run([sys.executable, str(root / "tools" / "analytics" / HARVEST.name),
                         str(_transcript(tmp_path)), "--dry-run"],
                        cwd=root, capture_output=True, text=True, timeout=300, encoding="utf-8", errors="replace")
    assert cp.returncode == 0
    assert json.loads(cp.stdout)["results"][0]["recorded"] is False
    assert _events(root) == []


def _load_module():
    spec = importlib.util.spec_from_file_location("harvest_mod", HARVEST)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run_main(mod, monkeypatch, transcript: Path) -> tuple[int, dict]:
    monkeypatch.setattr(sys, "argv", [str(HARVEST), str(transcript), "--project", "fixture"])
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = mod.main()
    return code, json.loads(buf.getvalue())


def _fake_writer(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "fake-record-event.py"
    path.write_text("import sys, time, json\n" + body + "\n", encoding="utf-8")
    return path


def test_writer_failure_gives_exit_one_and_keeps_json(tmp_path, monkeypatch):
    mod = _load_module()
    monkeypatch.setattr(mod, "RECORD", _fake_writer(
        tmp_path, "sys.stderr.write('boom'); print(json.dumps({'status':'error'})); sys.exit(2)"))
    code, out = _run_main(mod, monkeypatch, _transcript(tmp_path))
    assert code == 1
    assert out["status"] == "ok"
    res = out["results"][0]
    assert res["recorded"] is False and "boom" in res["stderr"]


def test_writer_runs_with_current_interpreter(tmp_path, monkeypatch):
    mod = _load_module()
    seen = tmp_path / "seen.txt"
    monkeypatch.setattr(mod, "RECORD", _fake_writer(
        tmp_path, f"open({str(seen)!r}, 'w').write(sys.executable + '\\n' + ' '.join(sys.argv[1:2]))"))
    code, out = _run_main(mod, monkeypatch, _transcript(tmp_path))
    assert code == 0 and out["results"][0]["recorded"] is True
    exe, flag = seen.read_text(encoding="utf-8").splitlines()
    assert Path(exe).resolve() == Path(sys.executable).resolve()
    assert flag == "--event"


def test_writer_timeout_is_not_recorded(tmp_path, monkeypatch):
    mod = _load_module()
    monkeypatch.setattr(mod, "RECORD", _fake_writer(tmp_path, "time.sleep(5)"))
    monkeypatch.setattr(mod, "RECORD_TIMEOUT_S", 1)
    code, out = _run_main(mod, monkeypatch, _transcript(tmp_path))
    assert code == 1
    assert out["results"][0]["recorded"] is False
    assert "timeout" in out["results"][0]["error"]


def test_no_reference_to_shell_writer():
    text = HARVEST.read_text(encoding="utf-8")
    assert "record-event.sh" not in text
    assert 'RECORD = HERE / "record-event.py"' in text


# --------------------------------------------------------------------------- cartella dei transcript

import pytest  # noqa: E402

PATHS = [
    "/Users/a/Documents/Work/Factories/my-factory",
    "/Users/a b/My Factory_v2&co/repo.git",
    "C:\\Users\\Mario Rossi\\Documents\\factory_1",
    "/home/u/progetti/citt\u00e0 & dintorni",
]


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / "analytics" / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("project_dir", PATHS)
def test_transcripts_dir_same_rule_in_harvest_cost_alert_and_ledger(project_dir, monkeypatch, tmp_path):
    harvest = _load_module()
    cost_alert = _load("cost_alert_mod", "cost_alert.py")
    ledger = _load("ledger_mod", "show-session-tokens.py")
    expected = harvest.transcripts_dir(project_dir)
    assert expected.parent == Path.home() / ".claude" / "projects"
    assert re.fullmatch(r"[A-Za-z0-9-]+", expected.name), expected.name
    assert cost_alert.transcripts_dir(project_dir) == expected
    # il ledger cerca nella stessa cartella: la creo con un transcript e verifico che lo trovi
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID", raising=False)
    target = harvest.transcripts_dir(project_dir)
    target.mkdir(parents=True)
    (target / "s.jsonl").write_text("{}\n", encoding="utf-8")
    assert ledger.find_transcript(project_dir) == str(target / "s.jsonl")


def test_transcripts_dir_examples():
    harvest = _load_module()
    assert harvest.transcripts_dir("/Users/a b/My_Dir&x.y").name == "-Users-a-b-My-Dir-x-y"
    assert harvest.transcripts_dir("C:\\Users\\a\\f.v2").name == "C--Users-a-f-v2"

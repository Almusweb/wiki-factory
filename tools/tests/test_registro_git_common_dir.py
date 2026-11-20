"""Registro sessioni: path sulla git common dir, condiviso tra worktree, con lock sul file locale."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "tools" / "session" / "active_sessions.py"
sys.path.insert(0, str(ROOT / "tools" / "session"))
import active_sessions as A  # noqa: E402


def _git(cwd, *a):
    subprocess.run(["git", "-C", str(cwd), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                   check=True, capture_output=True)


def _repo(tmp_path):
    main = tmp_path / "main"
    main.mkdir()
    _git(main, "init", "-q")
    (main / "f").write_text("x")
    _git(main, "add", "f")
    _git(main, "commit", "-q", "-m", "init")
    wt = tmp_path / "wt"
    _git(main, "worktree", "add", "-q", str(wt), "-b", "other")
    return main, wt


def _cli(root, *a):
    return subprocess.run([sys.executable, str(CLI), "--root", str(root), "--json", *a],
                          capture_output=True, text=True)


def test_stesso_file_da_worktree_e_checkout_principale(tmp_path):
    main, wt = _repo(tmp_path)
    assert A.registry_path(main) == A.registry_path(wt)
    assert A.registry_path(main).parent == (main / ".git").resolve()


def test_claim_in_due_worktree_e_conflicts_li_mostra(tmp_path):
    main, wt = _repo(tmp_path)
    r = _cli(main, "claim", "--agent", "a", "--domain", "kanban", "--uuid", "aaaa1111", "--operator", "uno")
    assert r.returncode == 0, r.stderr
    r = _cli(wt, "claim", "--agent", "b", "--domain", "kanban", "--uuid", "bbbb2222", "--operator", "due")
    assert r.returncode == 0, r.stderr
    assert [c["uuid"] for c in json.loads(r.stdout)["conflicts"]] == ["aaaa1111"]
    r = _cli(main, "conflicts", "--domain", "kanban", "--uuid", "aaaa1111")
    assert [c["uuid"] for c in json.loads(r.stdout)["conflicts"]] == ["bbbb2222"]
    assert not (main / "memory").exists() and not (wt / "memory").exists()
    assert not list(A.registry_path(main).parent.glob("*.lock"))


def test_fuori_da_git_ripiega_su_memory(tmp_path):
    assert A.registry_path(tmp_path) == tmp_path / "memory" / "active-sessions.yaml"


def test_lock_orfano_scaduto_viene_rimosso(tmp_path):
    import os, time
    path = tmp_path / "r.yaml"
    lock = tmp_path / "r.yaml.lock"
    lock.write_text("")
    old = time.time() - 120
    os.utime(lock, (old, old))
    with A._locked(path):
        assert lock.exists()
    assert not lock.exists()

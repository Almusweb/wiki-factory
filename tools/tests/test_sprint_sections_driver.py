import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DRIVER = ROOT / "tools" / "kanban" / "sprint_sections_driver.py"
REAL = ROOT / "management" / "kanban" / "sprint.md"
FM = b"---\ntype: sprint\nsprint_current: 5\n---\n\n"


def git(cwd, *args, check=True):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, check=check)


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "config", "user.email", "t@example.com")
    git(tmp_path, "config", "user.name", "t")
    git(tmp_path, "config", "commit.gpgsign", "false")
    git(tmp_path, "config", "merge.sec.name", "sezioni")
    git(tmp_path, "config", "merge.sec.driver",
        '"%s" "%s" %%O %%A %%B' % (sys.executable, DRIVER))
    (tmp_path / ".gitattributes").write_text("sprint.md merge=sec\n", encoding="utf-8")
    return tmp_path


def commit(repo, data, msg):
    (repo / "sprint.md").write_bytes(data)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", msg)


def scenario(repo, base, ours, theirs):
    commit(repo, base, "base")
    git(repo, "checkout", "-q", "-b", "theirs")
    commit(repo, theirs, "theirs")
    git(repo, "checkout", "-q", "main")
    commit(repo, ours, "ours")
    r = git(repo, "merge", "theirs", "-m", "m", check=False)
    return r.returncode, (repo / "sprint.md").read_bytes()


BASE = FM + b"## Sprint 2\nuno\n### sotto\nx\n\n## Sprint 1\ndue\n"


def test_two_new_sections_on_top_real_file(repo):
    base = REAL.read_bytes()
    first = base.index(b"\n## ") + 1
    ours = base[:first] + b"## Sprint 900 nostra\na\n\n" + base[first:]
    theirs = base[:first] + b"## Sprint 901 loro\nb\n\n" + base[first:]
    rc, out = scenario(repo, base, ours, theirs)
    assert rc == 0
    expected = base[:first] + b"## Sprint 900 nostra\na\n\n## Sprint 901 loro\nb\n\n" + base[first:]
    assert out == expected


def test_same_section_both_sides_conflicts(repo):
    rc, out = scenario(repo, BASE,
                       BASE.replace(b"uno", b"NOSTRO"), BASE.replace(b"uno", b"LORO"))
    assert rc != 0
    assert b"<<<<<<< ours" in out and b"=======" in out and b">>>>>>> theirs" in out
    assert b"NOSTRO" in out and b"LORO" in out


def test_different_sections_modified(repo):
    rc, out = scenario(repo, BASE,
                       BASE.replace(b"uno", b"UNO"), BASE.replace(b"due", b"DUE"))
    assert rc == 0
    assert out == BASE.replace(b"uno", b"UNO").replace(b"due", b"DUE")


def test_frontmatter_vs_section(repo):
    rc, out = scenario(repo, BASE,
                       BASE.replace(b"sprint_current: 5", b"sprint_current: 6"),
                       BASE.replace(b"due", b"DUE"))
    assert rc == 0
    assert b"sprint_current: 6" in out and b"DUE" in out


def test_deleted_vs_modified_conflicts(repo):
    deleted = FM + b"## Sprint 2\nuno\n### sotto\nx\n\n"
    rc, out = scenario(repo, BASE, deleted, BASE.replace(b"due", b"DUE"))
    assert rc != 0
    assert b"<<<<<<< ours" in out and b"DUE" in out


def test_deleted_vs_unchanged_is_deleted(repo):
    deleted = FM + b"## Sprint 2\nuno\n### sotto\nx\n\n"
    rc, out = scenario(repo, BASE, deleted, BASE.replace(b"uno", b"UNO"))
    assert rc == 0
    assert b"Sprint 1" not in out and b"UNO" in out


def test_bytes_crlf_no_trailing_newline(repo):
    base = (FM + b"## B\nb\n\n## A\na").replace(b"\n", b"\r\n")
    ours = base.replace(b"## B", b"## N1\r\nn\r\n\r\n## B", 1)
    theirs = base.replace(b"\r\na", b"\r\nA")  # sezione A modificata, senza newline finale
    rc, out = scenario(repo, base, ours, theirs)
    assert rc == 0
    assert out == ours.replace(b"\r\na", b"\r\nA")
    assert not out.endswith(b"\n")


def test_no_sections_fallback(repo):
    base = b"a\nb\nc\nd\ne\n"
    commit(repo, base, "base")
    git(repo, "checkout", "-q", "-b", "theirs")
    commit(repo, b"a\nb\nc\nd\nE\n", "t")
    git(repo, "checkout", "-q", "main")
    commit(repo, b"A\nb\nc\nd\ne\n", "o")
    r = git(repo, "merge", "theirs", "-m", "m", check=False)
    assert r.returncode == 0  # standard merge-file fonde righe distinte
    assert (repo / "sprint.md").read_bytes() == b"A\nb\nc\nd\nE\n"
    assert b"nessuna sezione" in r.stderr


def test_no_sections_fallback_conflict(tmp_path):
    for n, c in (("o", b"x\n"), ("a", b"y\n"), ("b", b"z\n")):
        (tmp_path / n).write_bytes(c)
    (tmp_path / "base").write_bytes(b"q\n")
    r = subprocess.run([sys.executable, str(DRIVER), str(tmp_path / "base"),
                        str(tmp_path / "a"), str(tmp_path / "b")], capture_output=True)
    assert r.returncode == 1
    assert b"<<<<<<<" in (tmp_path / "a").read_bytes()


def test_init_check_segnala_driver_non_registrato(tmp_path):
    """EP-100: un driver dichiarato in .gitattributes ma non registrato fa ripiegare git sul merge
    riga per riga senza avvisare. /init-check lo deve dire."""
    import importlib.util
    radice = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location("init_check", radice / "tools/env/init_check.py")
    ic = importlib.util.module_from_spec(spec)
    sys.modules["init_check"] = ic  # @dataclass cerca il modulo in sys.modules
    spec.loader.exec_module(ic)
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".gitattributes").write_text("a.md merge=factory-x\nb.md -merge\nc.md merge=binary\n", encoding="utf-8")
    r = ic.Report(); ic.check_merge_drivers(r, tmp_path)
    assert r.checks[-1].status == ic.STATUS_WARN and "factory-x" in r.checks[-1].note
    subprocess.run(["git", "-C", str(tmp_path), "config", "merge.factory-x.driver", "true"], check=True)
    r = ic.Report(); ic.check_merge_drivers(r, tmp_path)
    assert r.checks[-1].status == ic.STATUS_PASS

"""Hook git scritti con fine riga LF e subprocess in modo testo con lettura UTF-8."""
import ast
import importlib.util
import io
import os
import subprocess
import sys

import pytest

QUI = os.path.dirname(os.path.abspath(__file__))
FACTORY = os.path.normpath(os.path.join(QUI, '..', '..'))
VCS = os.path.join(FACTORY, 'tools', 'vcs')
sys.path.insert(0, VCS)


def _carica(nome, rel):
    spec = importlib.util.spec_from_file_location(nome, os.path.join(FACTORY, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


ifh = _carica('install_factory_hooks', 'tools/vcs/install_factory_hooks.py')
ish = _carica('install_submodule_hooks', 'tools/vcs/install_submodule_hooks.py')
smd = _carica('sm_doctor', 'tools/vcs/sm_doctor.py')


def _crlf(testo):
    return testo.replace('\n', '\r\n').encode('utf-8')


@pytest.fixture
def hooks_dir(tmp_path):
    d = tmp_path / 'hooks'
    d.mkdir()
    return d


# --- hook della factory -------------------------------------------------------------------

def test_factory_install_scrive_lf(hooks_dir):
    assert ifh._install('pre-push', ifh.HOOKS['pre-push'], hooks_dir, False, False) == 'installed'
    dati = (hooks_dir / 'pre-push').read_bytes()
    assert b'\r' not in dati
    assert dati == ifh.HOOKS['pre-push'].encode('utf-8')


def test_factory_hook_identico_in_crlf_riscritto_senza_prompt(hooks_dir, monkeypatch):
    monkeypatch.setattr(ifh, '_prompt', lambda msg: pytest.fail('non deve chiedere conferma'))
    contenuto = ifh.HOOKS['pre-push']
    h = hooks_dir / 'pre-push'
    h.write_bytes(_crlf(contenuto))
    assert ifh._install('pre-push', contenuto, hooks_dir, False, False) == 'installed'
    assert h.read_bytes() == contenuto.encode('utf-8')


def test_factory_hook_estraneo_intatto(hooks_dir, monkeypatch):
    monkeypatch.setattr(ifh, '_prompt', lambda msg: 'n')
    h = hooks_dir / 'pre-push'
    estraneo = b'#!/bin/sh\r\necho hook di qualcun altro\r\n'
    h.write_bytes(estraneo)
    assert ifh._install('pre-push', ifh.HOOKS['pre-push'], hooks_dir, False, False) == 'skipped'
    assert h.read_bytes() == estraneo


def test_factory_dry_run_non_scrive_il_crlf_identico(hooks_dir):
    h = hooks_dir / 'pre-push'
    h.write_bytes(_crlf(ifh.HOOKS['pre-push']))
    ifh._install('pre-push', ifh.HOOKS['pre-push'], hooks_dir, True, False)
    assert b'\r\n' in h.read_bytes()


def test_factory_template_senza_cr():
    for nome, contenuto in list(ifh.HOOKS.items()) + [('pre-commit', ifh.PRE_COMMIT_HOOK)]:
        assert '\r' not in contenuto, nome


# --- hook dei submodule -------------------------------------------------------------------

def test_submodule_install_scrive_lf(hooks_dir):
    c = ish.Counters()
    ish._install_hook('pre-commit', ish.HOOKS['pre-commit'], hooks_dir, False, False, c)
    assert c.installed == 1
    assert (hooks_dir / 'pre-commit').read_bytes() == ish.HOOKS['pre-commit'].encode('utf-8')
    assert b'\r' not in (hooks_dir / 'pre-commit').read_bytes()


def test_submodule_hook_identico_in_crlf_riscritto_senza_prompt(hooks_dir, monkeypatch):
    monkeypatch.setattr(ish, '_prompt', lambda msg: pytest.fail('non deve chiedere conferma'))
    h = hooks_dir / 'commit-msg'
    h.write_bytes(_crlf(ish.HOOKS['commit-msg']))
    c = ish.Counters()
    ish._install_hook('commit-msg', ish.HOOKS['commit-msg'], hooks_dir, False, False, c)
    assert c.installed == 1
    assert h.read_bytes() == ish.HOOKS['commit-msg'].encode('utf-8')


def test_submodule_hook_estraneo_intatto(hooks_dir, monkeypatch):
    monkeypatch.setattr(ish, '_prompt', lambda msg: 'n')
    h = hooks_dir / 'commit-msg'
    estraneo = b'#!/bin/sh\r\necho altro\r\n'
    h.write_bytes(estraneo)
    c = ish.Counters()
    ish._install_hook('commit-msg', ish.HOOKS['commit-msg'], hooks_dir, False, False, c)
    assert c.skipped == 1
    assert h.read_bytes() == estraneo


def test_submodule_template_senza_cr():
    for nome, contenuto in ish.HOOKS.items():
        assert '\r' not in contenuto, nome


# --- sm_doctor ----------------------------------------------------------------------------

def test_sm_doctor_reinstalla_hook_in_lf(tmp_path, monkeypatch):
    hooks = tmp_path / 'sm' / '.git' / 'hooks'
    hooks.mkdir(parents=True)
    monkeypatch.setattr(smd, 'resolve_hooks_dir', lambda p: hooks)
    assert smd._reinstall_hooks(tmp_path, 'sm', ['pre-commit', 'commit-msg'], False)
    for nome in ('pre-commit', 'commit-msg'):
        assert (hooks / nome).read_bytes() == ish.HOOKS[nome].encode('utf-8')
        assert b'\r' not in (hooks / nome).read_bytes()


# --- subprocess in modo testo con encoding esplicito --------------------------------------

FILE_UTF8 = [
    'tools/analytics/kanban_history.py',
    'tools/kanban/date_lavoro_check.py',
    'tools/session/close_collect.py',
    'tools/wiki/conflict_markers_check.py',
    'tools/kanban/next-id.py',
    'tools/security/secrets_guard.py',
]
CHIAMATE = {'run', 'check_output', 'check_call', 'Popen', 'call'}


def _in_modo_testo(call):
    kw = {k.arg: k.value for k in call.keywords if k.arg}
    for chiave in ('text', 'universal_newlines'):
        v = kw.get(chiave)
        if isinstance(v, ast.Constant) and v.value is True:
            return True
    return 'encoding' in kw or 'errors' in kw


@pytest.mark.parametrize('rel', FILE_UTF8)
def test_subprocess_in_modo_testo_dichiara_encoding(rel):
    with open(os.path.join(FACTORY, rel), encoding='utf-8') as f:
        albero = ast.parse(f.read())
    trovate = 0
    for n in ast.walk(albero):
        if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr in CHIAMATE and isinstance(n.func.value, ast.Name)
                and n.func.value.id == 'subprocess'):
            continue
        if not _in_modo_testo(n):
            continue
        trovate += 1
        kw = {k.arg: k.value for k in n.keywords if k.arg}
        assert isinstance(kw.get('encoding'), ast.Constant) and kw['encoding'].value == 'utf-8', \
            f'{rel}:{n.lineno} senza encoding="utf-8"'
        assert isinstance(kw.get('errors'), ast.Constant) and kw['errors'].value == 'replace', \
            f'{rel}:{n.lineno} senza errors="replace"'
    if rel != 'tools/wiki/conflict_markers_check.py':  # quest'ultimo legge in byte
        assert trovate, f'{rel}: nessun subprocess in modo testo trovato (lista da aggiornare?)'


# --- conflict_markers_check con console non UTF-8 -----------------------------------------

def _git(cwd, *a):
    return subprocess.run(['git', *a], cwd=cwd, capture_output=True, text=True,
                          encoding='utf-8', errors='replace', check=True)


def _no_reconfigure(**kw):
    raise ValueError('stream non riconfigurabile')


def test_conflict_markers_stdout_cp1252_esce_1(tmp_path, monkeypatch):
    cmc = _carica('conflict_markers_check_cp', 'tools/wiki/conflict_markers_check.py')
    _git(tmp_path, 'init', '-q')
    (tmp_path / 'wiki').mkdir()
    (tmp_path / 'wiki' / 'gaps.md').write_bytes(
        b'<<<<<<< a\nuno\n=======\ndue\n>>>>>>> b\n')
    _git(tmp_path, 'add', 'wiki/gaps.md')
    monkeypatch.setattr(cmc, 'ROOT', tmp_path)
    # stream che non sa codificare «→» (e nemmeno «—»), non riconfigurabile
    out = io.TextIOWrapper(io.BytesIO(), encoding='cp1252', errors='strict')
    monkeypatch.setattr(out, 'reconfigure', _no_reconfigure, raising=False)  # ripiego su _print_safe
    monkeypatch.setattr(sys, 'stdout', out)
    assert cmc.main(['--staged']) == 1
    out.flush()
    assert b'conflitt' in out.buffer.getvalue().lower()


def test_conflict_markers_processo_con_pythonioencoding_cp1252(tmp_path):
    _git(tmp_path, 'init', '-q')
    (tmp_path / 'tools' / 'wiki').mkdir(parents=True)
    script = tmp_path / 'tools' / 'wiki' / 'conflict_markers_check.py'
    script.write_bytes(open(os.path.join(FACTORY, 'tools', 'wiki', 'conflict_markers_check.py'), 'rb').read())
    (tmp_path / 'wiki').mkdir()
    (tmp_path / 'wiki' / 'gaps.md').write_bytes(b'<<<<<<< a\nuno\n=======\ndue\n>>>>>>> b\n')
    _git(tmp_path, 'add', 'wiki/gaps.md')
    # il report contiene «→»: con cp1252 imposto da fuori l'esito resta 1
    env = dict(os.environ, PYTHONIOENCODING='cp1252', PYTHONUTF8='0')
    r = subprocess.run([sys.executable, str(script), '--staged'], cwd=tmp_path, env=env,
                       capture_output=True)
    assert r.returncode == 1, r.stderr

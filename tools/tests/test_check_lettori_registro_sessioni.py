"""Check 4bo: un file che apre memory/active-sessions.yaml direttamente e' segnalato;
registry_path(), docstring, commenti, messaggi e test no."""
import importlib.util
import os
import subprocess

QUI = os.path.dirname(os.path.abspath(__file__))
FACTORY = os.path.normpath(os.path.join(QUI, '..', '..'))
_spec = importlib.util.spec_from_file_location(
    'lettori', os.path.join(FACTORY, 'tools/lint/check_lettori_registro_sessioni.py'))
L = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L)


def _repo(tmp_path, files):
    subprocess.run(['git', 'init', '-q'], cwd=str(tmp_path), check=True)
    for rel, testo in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(testo, encoding='utf-8')
    subprocess.run(['git', 'add', '-A'], cwd=str(tmp_path), check=True)
    return [f for f in L.check(str(tmp_path)) if f['severita'] == 'WARNING']


def test_lettore_diretto_segnalato(tmp_path):
    f = _repo(tmp_path, {
        'tools/cattivo.py': 'import os\nif os.path.exists("memory/active-sessions.yaml"):\n    pass\n',
        'tools/cattivo2.py': 'p = f"{root}/memory/active-sessions.yaml"\n',
    })
    assert sorted((x['file'], x['riga']) for x in f) == [('tools/cattivo.py', 2), ('tools/cattivo2.py', 1)]


def test_registry_path_docstring_commenti_e_test_non_segnalati(tmp_path):
    f = _repo(tmp_path, {
        'tools/buono.py': '"""Legge memory/active-sessions.yaml (vecchio path)."""\n'
                          'from tools.session.active_sessions import registry_path\n'
                          '# memory/active-sessions.yaml\n'
                          'def f(root):\n    """memory/active-sessions.yaml"""\n    return registry_path(root)\n'
                          'MSG = "non scrivere in memory/active-sessions.yaml adesso"\n',
        'tools/session/active_sessions.py': 'REL = "memory/active-sessions.yaml"\n',
        'tools/tests/test_x.py': 'P = "memory/active-sessions.yaml"\n',
        'tests/y.py': 'P = "memory/active-sessions.yaml"\n',
    })
    assert f == []


def test_master_pulito():
    assert [f for f in L.check(FACTORY) if f['severita'] == 'WARNING'] == []

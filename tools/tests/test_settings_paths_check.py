"""Check 4bl: path assoluti o fuori repo in .claude/settings.json."""
import json
import os
import subprocess
import sys

import pytest

QUI = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.normpath(os.path.join(QUI, '..', 'lint', 'check-settings-paths.py'))
OGGI = '2026-11-16'


def prepara(tmp_path, dirs=None, cfg=None, settings=True):
    if settings:
        (tmp_path / '.claude').mkdir()
        perm = {'allow': []}
        if dirs is not None:
            perm['additionalDirectories'] = dirs
        (tmp_path / '.claude' / 'settings.json').write_text(json.dumps({'permissions': perm}), encoding="utf-8")
    if cfg is not None:
        (tmp_path / 'factory.config.yaml').write_text(cfg, encoding="utf-8")
    return tmp_path


def esegui(root, *extra):
    r = subprocess.run([sys.executable, SCRIPT, '--json', '--root', str(root), '--oggi', OGGI, *extra],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, json.loads(r.stdout)


@pytest.mark.parametrize('valore', ['/Users/x/repo', '~/repo', 'C:\\repo', 'D:/repo', '../altro', 'a/../../b'])
def test_segnala_assoluti_e_fuori_repo(tmp_path, valore):
    _, out = esegui(prepara(tmp_path, [valore]))
    assert [f['valore'] for f in out['findings']] == [valore]
    assert out['severita'] == 'WARNING'


@pytest.mark.parametrize('valore', ['docs', './docs/sub', '${CLAUDE_PROJECT_DIR}/x', '$CLAUDE_PROJECT_DIR/x', 'a..b'])
def test_relativi_e_variabili_puliti(tmp_path, valore):
    _, out = esegui(prepara(tmp_path, [valore]))
    assert out['findings'] == []


def test_file_assente_ok(tmp_path):
    code, out = esegui(prepara(tmp_path, settings=False))
    assert code == 0 and out['findings'] == []


def test_required_from_assente_futuro_passato(tmp_path):
    assert esegui(prepara(tmp_path, ['/x']))[1]['severita'] == 'WARNING'
    base = 'settings_paths_check:\n  required_from: "%s"\n'
    (tmp_path / 'factory.config.yaml').write_text(base % '2026-12-01', encoding="utf-8")
    assert esegui(tmp_path)[1]['severita'] == 'WARNING'
    (tmp_path / 'factory.config.yaml').write_text(base % '2026-11-16', encoding="utf-8")
    code, out = esegui(tmp_path, '--strict')
    assert out['severita'] == 'ERROR' and code == 1
    (tmp_path / 'factory.config.yaml').write_text(base % '2026-11-01', encoding="utf-8")
    assert esegui(tmp_path)[1]['severita'] == 'ERROR'


def test_warning_non_rompe_strict(tmp_path):
    code, _ = esegui(prepara(tmp_path, ['/x']), '--strict')
    assert code == 0


def test_repo_reale_pulito():
    radice = os.path.normpath(os.path.join(QUI, '..', '..'))
    _, out = esegui(radice)
    assert out['findings'] == []


@pytest.mark.parametrize('valore', ['${CLAUDE_PROJECT_DIR}/../x', '$CLAUDE_PROJECT_DIR/a/../../x',
                                    '$HOME/x', '${HOME}/x', '%USERPROFILE%\\x', '$USERPROFILE/x', '${OTHER}/x'])
def test_variabili_fuori_progetto_e_dotdot_con_variabile(tmp_path, valore):
    _, out = esegui(prepara(tmp_path, [valore]))
    assert [f['valore'] for f in out['findings']] == [valore]


def scrivi_permessi(tmp_path, **liste):
    (tmp_path / '.claude').mkdir()
    (tmp_path / '.claude' / 'settings.json').write_text(json.dumps({'permissions': liste}), encoding="utf-8")
    return tmp_path


@pytest.mark.parametrize('lista,regola', [
    ('allow', 'Read(//Users/x/repo/**)'), ('allow', 'Edit(/home/x/f)'), ('deny', 'Read(~/.ssh/**)'),
    ('ask', 'Bash(cat /Users/x/f)'), ('allow', 'Read(${CLAUDE_PROJECT_DIR}/../x)'),
    ('allow', 'Bash(cat $HOME/f)')])
def test_regole_permessi_con_path_esterni(tmp_path, lista, regola):
    _, out = esegui(scrivi_permessi(tmp_path, **{lista: [regola]}))
    assert [f['valore'] for f in out['findings']] == [regola]


@pytest.mark.parametrize('regola', ['Read(docs/**)', 'Bash(git push:*)', 'Bash(ls ${CLAUDE_PROJECT_DIR}/x)',
                                    'Bash(echo hi > /dev/null)', 'WebFetch', 'Read(${CLAUDE_PROJECT_DIR}/**)'])
def test_regole_permessi_pulite(tmp_path, regola):
    _, out = esegui(scrivi_permessi(tmp_path, allow=[regola]))
    assert out['findings'] == []


def test_json_non_valido_warning_non_verificabile(tmp_path):
    (tmp_path / '.claude').mkdir()
    (tmp_path / '.claude' / 'settings.json').write_text('{ rotto', encoding="utf-8")
    (tmp_path / 'factory.config.yaml').write_text('settings_paths_check:\n  required_from: "2026-01-01"\n', encoding="utf-8")
    code, out = esegui(tmp_path, '--strict')
    assert len(out['findings']) == 1 and 'non verificabile' in out['findings'][0]['motivo']
    assert out['severita'] == 'WARNING' and code == 0

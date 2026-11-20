"""Hook pre-commit opt-in della guardia del log (EP-077): flag di config e blocco reale su repo temporaneo."""
import importlib.util
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
from test_secrets_guard import FINTO, MARCATORE  # noqa: E402
TOOLS = os.path.normpath(os.path.join(QUI, '..'))
sys.path.insert(0, os.path.join(TOOLS, 'vcs'))
spec = importlib.util.spec_from_file_location('ifh', os.path.join(TOOLS, 'vcs', 'install_factory_hooks.py'))
ifh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ifh)

TESTA = b'---\ntype: wiki-log\nupdated: 2026-10-01\n---\n\n'
E1 = b'## 2026-10-01 10:00 \xe2\x80\x94 prima\n\ntesto uno\n\n'
E2 = b'## 2026-10-02 10:00 \xe2\x80\x94 seconda\n\ntesto due\n\n'


def cfg(tmp, corpo):
    p = pathlib.Path(tmp)
    (p / 'factory.config.yaml').write_text(corpo, encoding="utf-8")
    return p


def test_flag_spento_di_default_e_acceso_solo_con_true():
    d = tempfile.mkdtemp()
    try:
        assert ifh.log_guard_enabled(pathlib.Path(d)) is False            # nessun file
        assert ifh.log_guard_enabled(cfg(d, 'wiki_lint:\n  log_append_guard:\n    hook: false\n')) is False
        assert ifh.log_guard_enabled(cfg(d, 'wiki_lint:\n  semantic_check:\n    enabled: true\n')) is False
        assert ifh.log_guard_enabled(cfg(d, 'altro:\n  log_append_guard:\n    hook: true\n')) is False
        assert ifh.log_guard_enabled(cfg(d, 'wiki_lint:\n  log_append_guard:\n    hook: true  # si\n')) is True
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_install_idempotente():
    d = tempfile.mkdtemp()
    try:
        hooks = pathlib.Path(d)
        assert ifh._install('pre-commit', ifh.PRE_COMMIT_HOOK, hooks, False, False) == 'installed'
        assert ifh._install('pre-commit', ifh.PRE_COMMIT_HOOK, hooks, False, False) == 'skipped'
        assert ifh._install('pre-commit', ifh.PRE_COMMIT_HOOK, pathlib.Path(d) / 'x', True, False) in ('skipped', 'conflict')
    finally:
        shutil.rmtree(d, ignore_errors=True)


def run(cwd, *a):
    return subprocess.run(list(a), cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def test_hook_blocca_riga_tolta_e_lascia_passare_append():
    r = tempfile.mkdtemp(prefix='hook-log-')
    try:
        os.makedirs(os.path.join(r, 'tools', 'wiki'))
        os.makedirs(os.path.join(r, 'wiki'))
        shutil.copy(os.path.join(TOOLS, 'wiki', 'log_append_guard.py'), os.path.join(r, 'tools', 'wiki'))
        log = os.path.join(r, 'wiki', 'log.md')
        for c in (('init', '-q'), ('config', 'user.email', 't@t'), ('config', 'user.name', 't')):
            run(r, 'git', *c)
        open(log, 'wb').write(TESTA + E1 + E2)
        run(r, 'git', 'add', '.')
        run(r, 'git', 'commit', '-qm', 'base')
        ifh._install('pre-commit', ifh.PRE_COMMIT_HOOK, pathlib.Path(r, '.git', 'hooks'), False, False)

        open(log, 'wb').write(TESTA + E2)
        run(r, 'git', 'add', 'wiki/log.md')
        assert run(r, 'git', 'commit', '-qm', 'tronca').returncode != 0
        run(r, 'git', 'reset', '-q', '--hard')

        open(log, 'wb').write(TESTA.replace(b'2026-10-01', b'2026-10-16') + E1 + E2 + b'## 2026-10-03 \xe2\x80\x94 t\n\nx\n')
        run(r, 'git', 'add', 'wiki/log.md')
        assert run(r, 'git', 'commit', '-qm', 'coda').returncode == 0
    finally:
        shutil.rmtree(r, ignore_errors=True)


# --- catena di guardie: log + segreti ---------------------------------------------------------

GITLEAKS_FINTO = FINTO  # rifiuta i flag sconosciuti e registra le chiamate in $FAKE_LOG


def repo_catena(config, con_gitleaks=True):
    """Repo temporaneo con entrambe le guardie, hook installato e (opz.) gitleaks finto nel PATH."""
    r = tempfile.mkdtemp(prefix='hook-catena-')
    for sub in ('tools/wiki', 'tools/security', 'wiki'):
        os.makedirs(os.path.join(r, sub))
    shutil.copy(os.path.join(TOOLS, 'wiki', 'log_append_guard.py'), os.path.join(r, 'tools', 'wiki'))
    for m in ('secrets_guard.py', 'config_ancorata.py'):   # la deroga legge la config dall'ancora
        shutil.copy(os.path.join(TOOLS, 'security', m), os.path.join(r, 'tools', 'security'))
    open(os.path.join(r, 'factory.config.yaml'), 'w', encoding="utf-8").write(config)
    for c in (('init', '-q'), ('config', 'user.email', 't@t'), ('config', 'user.name', 't')):
        run(r, 'git', *c)
    open(os.path.join(r, 'wiki', 'log.md'), 'wb').write(TESTA + E1 + E2)
    run(r, 'git', 'add', '.')
    run(r, 'git', 'commit', '-qm', 'base')
    ifh._install('pre-commit', ifh.PRE_COMMIT_HOOK, pathlib.Path(r, '.git', 'hooks'), False, False)
    env = dict(os.environ, FAKE_LOG=os.path.join(r, 'chiamate.txt'))
    if con_gitleaks:
        b = os.path.join(r, '_bin')
        os.makedirs(b)
        g = os.path.join(b, 'gitleaks')
        open(g, 'w', encoding="utf-8").write(GITLEAKS_FINTO)
        os.chmod(g, 0o755)
        env['PATH'] = b + os.pathsep + env['PATH']
    return r, env


def commit(r, env, nome, contenuto):
    open(os.path.join(r, nome), 'w', encoding="utf-8").write(contenuto)
    run(r, 'git', 'add', nome)
    return subprocess.run(['git', 'commit', '-qm', 'x'], cwd=r, capture_output=True, text=True, env=env, encoding="utf-8", errors="replace")


def chiamate(r):
    p = os.path.join(r, 'chiamate.txt')
    return open(p, encoding="utf-8").read().count('invocato') if os.path.exists(p) else 0


def test_flag_spento_solo_log_nessuna_chiamata_all_oracolo():
    r, env = repo_catena('secrets_guard:\n  enabled: false\n  required_from: null\n')
    try:
        res = commit(r, env, 'a.txt', 'x ' + MARCATORE)
        assert res.returncode == 0 and chiamate(r) == 0
    finally:
        shutil.rmtree(r, ignore_errors=True)


def test_flag_acceso_warn_stampa_e_lascia_passare():
    r, env = repo_catena('secrets_guard:\n  enabled: true\n  required_from: null\n')
    try:
        res = commit(r, env, 'a.txt', 'x ' + MARCATORE)
        assert res.returncode == 0 and chiamate(r) == 1
        assert 'FAIL' in res.stdout + res.stderr and 'commit NON bloccato' in res.stdout + res.stderr
    finally:
        shutil.rmtree(r, ignore_errors=True)


def test_flag_acceso_error_blocca_con_messaggio_e_pulito_passa():
    r, env = repo_catena('secrets_guard:\n  enabled: true\n  required_from: 2020-01-01\n')
    try:
        res = commit(r, env, 'a.txt', 'x ' + MARCATORE)
        assert res.returncode != 0
        assert 'previene nel percorso cooperativo, rileva negli altri' in res.stdout + res.stderr
        run(r, 'git', 'reset', '-q', '--hard')
        assert commit(r, env, 'b.txt', 'pulito').returncode == 0
        assert chiamate(r) == 2
    finally:
        shutil.rmtree(r, ignore_errors=True)


def _senza_gitleaks(env):
    env['PATH'] = os.path.dirname(shutil.which('git')) + os.pathsep + os.path.dirname(sys.executable) \
        + os.pathsep + '/usr/bin' + os.pathsep + '/bin'
    return env


def test_non_verificabile_blocca_a_error_e_la_variabile_non_deroga():
    r, env = repo_catena('secrets_guard:\n  enabled: true\n  required_from: 2020-01-01\n', con_gitleaks=False)
    try:
        env = _senza_gitleaks(env)
        res = commit(r, env, 'a.txt', 'x ' + MARCATORE)
        out = res.stdout + res.stderr
        assert res.returncode != 0 and 'NON_VERIFICABILE' in out and 'record di deroga' in out
        env['SECRETS_GUARD_OVERRIDE'] = '1'
        res = subprocess.run(['git', 'commit', '-qm', 'x'], cwd=r, capture_output=True, text=True, env=env, encoding="utf-8", errors="replace")
        assert res.returncode != 0 and "non e' piu' letta" in res.stdout + res.stderr
    finally:
        shutil.rmtree(r, ignore_errors=True)


def test_non_verificabile_a_error_passa_con_record_sul_ref_protetto():
    """US-423: la deroga e' un record committato sul ref protetto (qui origin/main simulato)."""
    r, env = repo_catena('secrets_guard:\n  enabled: true\n  required_from: 2020-01-01\n', con_gitleaks=False)
    try:
        os.makedirs(os.path.join(r, 'security'))
        open(os.path.join(r, 'security', 'secrets-guard-deroghe.json'), 'w', encoding="utf-8").write(
            '[{"motivo": "test", "scadenza": "2999-01-01", "approvato_da": "m", "riferimento_gate": "g"}]')
        run(r, 'git', 'add', 'security')
        run(r, 'git', '-c', 'core.hooksPath=/dev/null', 'commit', '-qm', 'deroga')
        run(r, 'git', 'update-ref', 'refs/remotes/origin/main', 'HEAD')
        res = commit(r, _senza_gitleaks(env), 'a.txt', 'niente')
        out = res.stdout + res.stderr
        assert res.returncode == 0 and 'DEROGA DA RECORD' in out
    finally:
        shutil.rmtree(r, ignore_errors=True)


def test_non_verificabile_a_warn_non_blocca_e_lo_dice():
    r, env = repo_catena('secrets_guard:\n  enabled: true\n  required_from: null\n', con_gitleaks=False)
    try:
        res = commit(r, _senza_gitleaks(env), 'a.txt', 'x ' + MARCATORE)
        out = res.stdout + res.stderr
        assert res.returncode == 0 and 'NON_VERIFICABILE' in out and 'commit NON bloccato' in out
    finally:
        shutil.rmtree(r, ignore_errors=True)


def test_hook_vede_il_segreto_in_stage_anche_se_tolto_dal_disco():
    r, env = repo_catena('secrets_guard:\n  enabled: true\n  required_from: 2020-01-01\n')
    try:
        open(os.path.join(r, 'a.txt'), 'w', encoding="utf-8").write('x ' + MARCATORE)
        run(r, 'git', 'add', 'a.txt')
        os.remove(os.path.join(r, 'a.txt'))
        res = subprocess.run(['git', 'commit', '-qm', 'x'], cwd=r, capture_output=True, text=True, env=env, encoding="utf-8", errors="replace")
        assert res.returncode != 0 and 'FAIL' in res.stdout + res.stderr
    finally:
        shutil.rmtree(r, ignore_errors=True)


def test_hook_commit_di_sole_cancellazioni_non_e_bloccato():
    r, env = repo_catena('secrets_guard:\n  enabled: true\n  required_from: 2020-01-01\n', con_gitleaks=False)
    try:
        run(r, 'git', 'rm', '-q', 'factory.config.yaml')
        res = subprocess.run(['git', 'commit', '-qm', 'x'], cwd=r, capture_output=True, text=True,
                             env=_senza_gitleaks(env), encoding="utf-8", errors="replace")
        assert res.returncode == 0
    finally:
        shutil.rmtree(r, ignore_errors=True)


def test_hook_non_ha_piu_il_secondo_parser_ne_la_lista_dei_file():
    assert 'STAGED' not in ifh.PRE_COMMIT_HOOK and '--staged' in ifh.PRE_COMMIT_HOOK


def test_log_guard_blocca_ancora_a_flag_segreti_acceso():
    r, env = repo_catena('secrets_guard:\n  enabled: true\n  required_from: null\n')
    try:
        open(os.path.join(r, 'wiki', 'log.md'), 'wb').write(TESTA + E2)
        run(r, 'git', 'add', 'wiki/log.md')
        res = subprocess.run(['git', 'commit', '-qm', 'tronca'], cwd=r, capture_output=True, text=True, env=env, encoding="utf-8", errors="replace")
        assert res.returncode != 0
    finally:
        shutil.rmtree(r, ignore_errors=True)


def test_secrets_guard_enabled_legge_solo_il_blocco():
    d = tempfile.mkdtemp()
    try:
        assert ifh.secrets_guard_enabled(pathlib.Path(d)) is False
        assert ifh.secrets_guard_enabled(cfg(d, 'secrets_guard:\n  enabled: false\n')) is False
        assert ifh.secrets_guard_enabled(cfg(d, 'altro:\n  enabled: true\n')) is False
        assert ifh.secrets_guard_enabled(cfg(d, 'secrets_guard:\n  enabled: true  # si\n')) is True
    finally:
        shutil.rmtree(d, ignore_errors=True)

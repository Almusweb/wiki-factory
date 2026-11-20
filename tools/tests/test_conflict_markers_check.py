"""conflict_markers_check.py — marcatori di conflitto nei file in coda: riconoscimento, pre-commit,
pre-push, Check 4bn del lint."""
import importlib.util
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

import pytest

QUI = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.normpath(os.path.join(QUI, '..'))
FACTORY = os.path.normpath(os.path.join(TOOLS, '..'))


def _carica(nome, rel):
    spec = importlib.util.spec_from_file_location(nome, os.path.join(FACTORY, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


cmc = _carica('conflict_markers_check', 'tools/wiki/conflict_markers_check.py')

CONFLITTO = (b'<<<<<<< Updated upstream\nvoce di upstream\n=======\nvoce mia\n'
             b'>>>>>>> Stashed changes\n')
PULITO = {
    'wiki/log.md': b'---\ntype: wiki-log\n---\n\n## 2026-11-11 10:00 \xe2\x80\x94 voce\n\ntesto\n',
    'wiki/log-2026-11-10.md': b'## 2026-11-10 \xe2\x80\x94 archivio\n\ntesto\n',
    'wiki/gaps.md': b'# Gap\n\n- [ ] **G-X-001** \xe2\x80\x94 aperto\n',
    'wiki/index.md': b'# Index\n\n## Sources (1)\n',
    'raw/.extraction-manifest.json': b'{"a": {"source": "repo"}}\n',
    'management/kanban/sprint.md': b'# Sprint\n\n| TSK | stato |\n|---|---|\n',
}


# --- riconoscimento -------------------------------------------------------------------------

@pytest.mark.parametrize('path', sorted(PULITO))
def test_file_pulito_nessun_problema(path):
    assert cmc.check_content(path, PULITO[path]) is None


@pytest.mark.parametrize('path', sorted(PULITO))
def test_marcatori_trovati_in_ogni_file_dell_elenco(path):
    if path.endswith('.json'):
        data = b'{\n' + CONFLITTO + b'}\n'
    else:
        data = PULITO[path] + CONFLITTO
    p = cmc.check_content(path, data)
    assert p is not None and [l for _, l in p['markers']] == [
        '<<<<<<< Updated upstream', '=======', '>>>>>>> Stashed changes']


@pytest.mark.parametrize('path', sorted(PULITO))
def test_file_dell_elenco_riconosciuti(path):
    assert cmc.is_watched(path)


@pytest.mark.parametrize('path', ['wiki/concepts/x.md', 'raw/2026-11-11-x.md', 'tools/wiki/log.py',
                                  'management/kanban/EP-001/TSK-001.md', 'wiki/logbook.md'])
def test_file_fuori_elenco_ignorati(path):
    assert not cmc.is_watched(path)


def test_numeri_di_riga():
    p = cmc.check_content('wiki/log.md', b'a\nb\n' + CONFLITTO)
    assert [n for n, _ in p['markers']] == [3, 5, 7]


def test_separatore_in_blocco_di_codice_non_e_falso_positivo():
    data = b'## voce\n\n```text\ntitolo\n=======\n```\n\n~~~\n=======\n~~~\n'
    assert cmc.check_content('wiki/log.md', data) is None


def test_separatore_fuori_dal_blocco_di_codice_trovato():
    data = b'## voce\n\n```\ncodice\n```\n=======\n'
    assert [n for n, _ in cmc.check_content('wiki/log.md', data)['markers']] == [6]


def test_apertura_e_chiusura_contano_anche_nel_blocco_di_codice():
    data = b'```\n<<<<<<< HEAD\n```\n'
    assert cmc.check_content('wiki/log.md', data)['markers'] == [(2, '<<<<<<< HEAD')]


def test_separatore_conta_nel_json_e_nello_yaml():
    assert cmc.find_markers(b'=======\n', markdown=False) == [(1, '=======')]


@pytest.mark.parametrize('riga', [b'========', b'====== ', b'=======x', b' =======', b'<<<<<<<<',
                                  b'>>>>>>>>x', b'<<<<<<x', b'citazione <<<<<<< HEAD'])
def test_righe_simili_non_sono_marcatori(riga):
    assert cmc.find_markers(riga + b'\n', markdown=True) == []


@pytest.mark.parametrize('riga', [b'<<<<<<< HEAD', b'<<<<<<<', b'||||||| base', b'>>>>>>> 1a2b3c',
                                  b'>>>>>>>', b'=======\r'])
def test_marcatori_riconosciuti(riga):
    assert len(cmc.find_markers(riga + b'\n', markdown=False)) == 1


def test_manifest_json_non_valido_senza_marcatori():
    p = cmc.check_content('raw/.extraction-manifest.json', b'{"a": 1,,}\n')
    assert p['markers'] == [] and p['json_error']


def test_json_valido_solo_per_il_manifest():
    assert cmc.check_content('wiki/index.md', b'{non json\n') is None


def test_procedura_per_file():
    assert 'rotate_log.py' in cmc.procedura('wiki/log.md')
    assert 'archivio' in cmc.procedura('wiki/log-2026-11-10.md').lower()
    assert 'sprint.md' in cmc.procedura('management/kanban/sprint.md')
    assert 'json.tool' in cmc.procedura('raw/.extraction-manifest.json')
    assert cmc.procedura('wiki/gaps.md') == cmc.PROCEDURA_DEFAULT


# --- repo temporaneo ------------------------------------------------------------------------

def _run(cwd, *args, stdin=None):
    return subprocess.run(list(args), cwd=cwd, capture_output=True, text=True, input=stdin, timeout=120, encoding="utf-8", errors="replace")


def _git(cwd, *args):
    r = _run(cwd, 'git', *args)
    assert r.returncode == 0, (args, r.stderr)
    return r.stdout.strip()


COPIATI = ('tools/wiki/conflict_markers_check.py',
           'tools/wiki/log_append_guard.py', 'tools/lint/check_marcatori_conflitto.py')


@pytest.fixture
def repo():
    r = tempfile.mkdtemp(prefix='conflitti-')
    try:
        for rel in COPIATI:
            os.makedirs(os.path.join(r, os.path.dirname(rel)), exist_ok=True)
            shutil.copy(os.path.join(FACTORY, rel), os.path.join(r, rel))
        for rel, data in PULITO.items():
            os.makedirs(os.path.join(r, os.path.dirname(rel)), exist_ok=True)
            open(os.path.join(r, rel), 'wb').write(data)
        _git(r, 'init', '-q', '-b', 'main')
        _git(r, 'config', 'user.email', 't@t')
        _git(r, 'config', 'user.name', 't')
        _git(r, 'config', 'commit.gpgsign', 'false')
        _git(r, 'add', '.')
        _git(r, 'commit', '-qm', 'base')
        yield r
    finally:
        shutil.rmtree(r, ignore_errors=True)


def _script(r):
    return [sys.executable, os.path.join(r, 'tools', 'wiki', 'conflict_markers_check.py')]


def _sporca(r, rel='wiki/log.md'):
    with open(os.path.join(r, rel), 'ab') as f:
        f.write(CONFLITTO)


def test_staged_blocca_e_lascia_passare(repo):
    _sporca(repo)
    _git(repo, 'add', 'wiki/log.md')
    esito = _run(repo, *_script(repo), '--staged')
    assert esito.returncode == 1 and 'wiki/log.md' in esito.stdout and 'riga ' in esito.stdout
    _git(repo, 'checkout', 'HEAD', '--', 'wiki/log.md')
    assert _run(repo, *_script(repo), '--staged').returncode == 0


def test_staged_guarda_lo_stage_non_il_working_tree(repo):
    _sporca(repo, 'wiki/gaps.md')  # sporco ma non in stage
    assert _run(repo, *_script(repo), '--staged').returncode == 0


def test_hook_pre_commit_blocca_e_lascia_passare(repo):
    ifh_ = _carica('install_factory_hooks_pc', 'tools/vcs/install_factory_hooks.py')
    assert ifh_.main(['--only', 'pre-commit', '--root', repo]) == 0
    _sporca(repo, 'management/kanban/sprint.md')
    _git(repo, 'add', 'management/kanban/sprint.md')
    esito = _run(repo, 'git', 'commit', '-qm', 'sporco')
    assert esito.returncode != 0 and 'management/kanban/sprint.md' in esito.stderr
    _git(repo, 'checkout', 'HEAD', '--', 'management/kanban/sprint.md')
    with open(os.path.join(repo, 'wiki/log.md'), 'ab') as f:
        f.write(b'\n## 2026-11-11 11:00 \xe2\x80\x94 altra\n\ntesto\n')
    _git(repo, 'add', 'wiki/log.md')
    esito = _run(repo, 'git', 'commit', '-qm', 'pulito')
    assert esito.returncode == 0, esito.stderr


def test_rev_e_json(repo):
    assert _run(repo, *_script(repo), '--rev', 'HEAD').returncode == 0
    _sporca(repo, 'raw/.extraction-manifest.json')
    _git(repo, 'commit', '-qam', 'sporco')
    esito = _run(repo, *_script(repo), '--rev', 'HEAD', '--json')
    assert esito.returncode == 1
    dati = json.loads(esito.stdout)
    assert [p['path'] for p in dati['problems']] == ['raw/.extraction-manifest.json']
    assert dati['problems'][0]['json_error']
    assert _run(repo, *_script(repo), '--rev', 'HEAD~1').returncode == 0


def test_rev_sconosciuto_esce_2(repo):
    esito = _run(repo, *_script(repo), '--rev', 'nonesiste')
    assert esito.returncode == 2 and 'sconosciuto' in esito.stderr


def test_worktree_con_pull_in_conflitto(repo):
    """Stash ripreso sopra una voce nuova dell'upstream."""
    log = os.path.join(repo, 'wiki/log.md')
    with open(log, 'ab') as f:
        f.write(b'\n## upstream\n')
    _git(repo, 'commit', '-qam', 'upstream')
    _git(repo, 'checkout', '-q', 'HEAD~1')
    with open(log, 'ab') as f:
        f.write(b'\n## mia\n')
    _git(repo, 'stash', 'push', '-q', '-m', 'test-stash')
    _git(repo, 'checkout', '-q', 'main')
    assert _run(repo, 'git', 'stash', 'pop').returncode != 0  # conflitto voluto
    esito = _run(repo, *_script(repo), '--worktree', '--json')
    assert esito.returncode == 1
    dati = json.loads(esito.stdout)
    assert dati['unmerged'] == ['wiki/log.md']
    assert [p['path'] for p in dati['problems']] == ['wiki/log.md']


def test_worktree_pulito(repo):
    esito = _run(repo, *_script(repo), '--worktree', '--json')
    assert esito.returncode == 0 and json.loads(esito.stdout) == {'unmerged': [], 'problems': []}


def test_worktree_marcatori_senza_conflitto_git(repo):
    _sporca(repo, 'management/kanban/sprint.md')
    esito = _run(repo, *_script(repo), '--worktree')
    assert esito.returncode == 1 and 'management/kanban/sprint.md' in esito.stdout


def _remote(repo):
    bare = repo + '-remote.git'
    _git(repo, 'init', '-q', '--bare', bare)
    _git(repo, 'remote', 'add', 'origin', bare)
    _git(repo, 'push', '-q', 'origin', 'main')
    return bare


def test_pre_push_stdin(repo):
    bare = _remote(repo)
    try:
        base = _git(repo, 'rev-parse', 'HEAD')
        _sporca(repo)
        _git(repo, 'commit', '-qam', 'sporco')
        tip = _git(repo, 'rev-parse', 'HEAD')
        riga = f'refs/heads/main {tip} refs/heads/main {base}\n'
        esito = _run(repo, *_script(repo), '--pre-push', stdin=riga)
        assert esito.returncode == 1 and 'PUSH BLOCCATO' in esito.stderr and 'refs/heads/main' in esito.stderr
        # cancellazione di un ref: niente da controllare
        assert _run(repo, *_script(repo), '--pre-push',
                    stdin=f'(delete) {cmc.ZERO} refs/heads/x {base}\n').returncode == 0
        # corretto in un commit successivo: la punta e' pulita, il push passa
        _git(repo, 'checkout', base, '--', 'wiki/log.md')
        _git(repo, 'commit', '-qam', 'corretto')
        tip2 = _git(repo, 'rev-parse', 'HEAD')
        assert _run(repo, *_script(repo), '--pre-push',
                    stdin=f'refs/heads/main {tip2} refs/heads/main {base}\n').returncode == 0
    finally:
        shutil.rmtree(bare, ignore_errors=True)


def test_pre_push_ref_nuovo(repo):
    bare = _remote(repo)
    try:
        _git(repo, 'checkout', '-qb', 'nuovo')
        _sporca(repo, 'wiki/index.md')
        _git(repo, 'commit', '-qam', 'sporco')
        tip = _git(repo, 'rev-parse', 'HEAD')
        esito = _run(repo, *_script(repo), '--pre-push',
                     stdin=f'refs/heads/nuovo {tip} refs/heads/nuovo {cmc.ZERO}\n')
        assert esito.returncode == 1 and 'wiki/index.md' in esito.stderr
    finally:
        shutil.rmtree(bare, ignore_errors=True)


def test_pre_push_ignora_file_non_toccati_dal_push(repo):
    """Un marcatore gia' sul remoto non blocca un push che non tocca quel file (lo segnala /lint)."""
    bare = _remote(repo)
    try:
        _sporca(repo, 'wiki/gaps.md')
        _git(repo, 'commit', '-qam', 'sporco')
        _git(repo, 'push', '-q', '--no-verify', 'origin', 'main')
        base = _git(repo, 'rev-parse', 'HEAD')
        open(os.path.join(repo, 'altro.txt'), 'w', encoding="utf-8").write('x\n')
        _git(repo, 'add', 'altro.txt')
        _git(repo, 'commit', '-qm', 'altro')
        tip = _git(repo, 'rev-parse', 'HEAD')
        assert _run(repo, *_script(repo), '--pre-push',
                    stdin=f'refs/heads/main {tip} refs/heads/main {base}\n').returncode == 0
    finally:
        shutil.rmtree(bare, ignore_errors=True)


# --- hook reali (install_factory_hooks) -----------------------------------------------------

ifh = _carica('install_factory_hooks', 'tools/vcs/install_factory_hooks.py')


def test_hook_pre_push_installato_blocca_il_push(repo):
    bare = _remote(repo)
    try:
        assert ifh.main(['--only', 'pre-push', '--root', repo]) == 0
        _sporca(repo)
        _git(repo, 'commit', '-qam', 'sporco')  # nessun pre-commit nel repo di test
        esito = _run(repo, 'git', 'push', 'origin', 'main')
        assert esito.returncode != 0 and 'PUSH BLOCCATO' in esito.stderr
        assert _git(repo, 'rev-parse', 'HEAD~1') == _run(bare, 'git', 'rev-parse', 'main').stdout.strip()
        _git(repo, 'checkout', 'HEAD~1', '--', 'wiki/log.md')
        _git(repo, 'commit', '-qam', 'corretto')
        esito = _run(repo, 'git', 'push', 'origin', 'main')
        assert esito.returncode == 0, esito.stderr
    finally:
        shutil.rmtree(bare, ignore_errors=True)


def test_hook_pre_push_senza_script_non_blocca(repo):
    bare = _remote(repo)
    try:
        assert ifh.main(['--only', 'pre-push', '--root', repo]) == 0
        os.remove(os.path.join(repo, 'tools/wiki/conflict_markers_check.py'))
        _sporca(repo)
        _git(repo, 'commit', '-qam', 'sporco')
        assert _run(repo, 'git', 'push', 'origin', 'main').returncode == 0
    finally:
        shutil.rmtree(bare, ignore_errors=True)


# --- errori e timeout -----------------------------------------------------------------------

def test_timeout_di_git_e_controllo_incompleto(monkeypatch, capsys):
    def scaduto(*a, **k):
        raise subprocess.TimeoutExpired(a[0], k.get('timeout'))
    monkeypatch.setattr(cmc.subprocess, 'run', scaduto)
    assert cmc.main(['--staged']) == 2
    assert 'timeout' in capsys.readouterr().err


def test_git_in_errore_non_e_un_pulito(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(cmc, 'ROOT', tmp_path)  # non e' un repo git
    assert cmc.main(['--staged']) == 2
    assert 'controllo incompleto' in capsys.readouterr().err


# --- check di lint 4bn ----------------------------------------------------------------------

def test_lint_4bn(repo):
    lint = [sys.executable, os.path.join(repo, 'tools/lint/check_marcatori_conflitto.py')]
    esito = _run(repo, *lint, repo)
    assert esito.returncode == 0 and '[4bn] OK' in esito.stdout
    _sporca(repo, 'wiki/log-2026-11-10.md')
    _git(repo, 'commit', '-qam', 'sporco')
    esito = _run(repo, *lint, repo)
    assert esito.returncode == 0 and '[WARNING][marcatori-conflitto][4bn] wiki/log-2026-11-10.md' in esito.stdout
    assert _run(repo, *lint, '--strict', repo).returncode == 1
    dati = json.loads(_run(repo, *lint, '--json', repo).stdout)
    assert dati['check'] == '4bn' and dati['findings'][0]['path'] == 'wiki/log-2026-11-10.md'
    esito = _run(repo, *lint, '--rev', 'nonesiste', repo)
    assert esito.returncode == 2 and '[ERROR]' in esito.stderr


# --- file reali della factory ---------------------------------------------------------------

def test_nessun_falso_positivo_su_head():
    vecchio = cmc.ROOT
    try:
        cmc.ROOT = pathlib.Path(FACTORY)
        assert cmc.check_rev('HEAD') == []
    finally:
        cmc.ROOT = vecchio


def test_registro_sessioni_non_e_un_file_in_coda():
    # TSK-1070: il registro e' locale al clone e non tracciato, quindi fuori da FILES.
    assert not any('active-sessions' in p for p in cmc.FILES)
    assert not cmc.is_watched('memory/active-sessions.yaml')

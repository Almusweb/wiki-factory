"""Split di repo-sync: lettore senza Bash, coerenza command/script, output su repo di fixture."""
import json
import os
import re
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(QUI, '..', '..'))
AGENTE = os.path.join(ROOT, '.claude', 'agents', 'repo-sync.md')
SKILL = os.path.join(ROOT, '.claude', 'skills', 'repo-extraction-protocol.md')
COMANDO = os.path.join(ROOT, '.claude', 'commands', 'repo-sync.md')
SCRIPT = os.path.join(ROOT, 'tools', 'sync', 'repo_enumerate.py')
CHECK = os.path.join(ROOT, 'tools', 'lint', 'check-ingest-agent-tools.py')


def leggi(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


def tools_agente():
    m = re.search(r'^tools:\s*\[(.*?)\]', leggi(AGENTE), re.M)
    return [t.strip() for t in m.group(1).split(',')]


def test_lettore_senza_bash_ne_grep():
    t = tools_agente()
    assert 'Bash' not in t
    assert 'Grep' not in t
    assert 'Read' in t and 'Glob' in t


def test_skill_non_chiede_all_agente_comandi_shell():
    skill = leggi(SKILL)
    # unica occorrenza di `git -C` e' la descrizione dello script, nella Fase E
    fase_e = skill.split('## Fase E')[1].split('## Fase 2')[0]
    resto = skill.replace(fase_e, '')
    assert 'git -C' not in resto
    assert 'non ha `Bash`' in fase_e


def test_comando_lancia_script_con_argomenti_accettati():
    cmd = leggi(COMANDO)
    m = re.search(r'python3 tools/sync/repo_enumerate\.py <path>((?: --[a-z-]+ <N>)*)', cmd)
    assert m, 'il comando non lancia repo_enumerate.py'
    help_ = subprocess.run([sys.executable, SCRIPT, '--help'], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    for flag in re.findall(r'--[a-z-]+', m.group(1)):
        assert flag in help_
    assert 'enumeration: <JSON' in cmd


def test_check_4bk_non_segnala_il_lettore():
    r = subprocess.run([sys.executable, CHECK, '--json', '--root', ROOT], capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r.returncode == 0
    dati = json.loads(r.stdout)
    testo = json.dumps(dati)
    assert not re.search(r'repo-sync[^"]*Bash|Bash[^"]*repo-sync', testo)


def _git(cwd, *a):
    subprocess.run(['git', '-C', str(cwd)] + list(a), check=True, capture_output=True)


def test_enumerazione_fixture_contiene_campi_letti_dalla_skill(tmp_path):
    repo = tmp_path / 'My Repo'
    (repo / 'src').mkdir(parents=True)
    (repo / 'node_modules').mkdir()
    (repo / 'README.md').write_text('# x\n', encoding="utf-8")
    (repo / 'package.json').write_text('{}', encoding="utf-8")
    (repo / 'src' / 'main.py').write_text('print(1)\n', encoding="utf-8")
    (repo / 'node_modules' / 'a.js').write_text('x', encoding="utf-8")
    _git(repo, 'init', '-q')
    _git(repo, '-c', 'user.name=T', '-c', 'user.email=t@e.x', 'add', '.')
    _git(repo, '-c', 'user.name=T', '-c', 'user.email=t@e.x', 'commit', '-q', '-m', 'init')
    r = subprocess.run([sys.executable, SCRIPT, str(repo), '--depth', '2'], capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r.returncode == 0
    e = json.loads(r.stdout)
    skill = leggi(SKILL)
    for campo in ('slug', 'is_git', 'git', 'directories', 'files_per_top_level', 'files', 'manifests'):
        assert campo in e and ('enumeration.%s' % campo in skill or campo in skill)
    assert e['slug'] == 'my-repo' and e['is_git'] is True
    for k in ('branch', 'commit', 'commit_date', 'commit_subject', 'contributors', 'commits_last_year'):
        assert k in e['git'] and ('`%s`' % k in skill or k in skill)
    assert e['git']['commit_subject'] == 'init' and e['git']['commits_last_year'] == 1
    assert 'src' in e['directories'] and not any('node_modules' in d for d in e['directories'])
    assert e['manifests'] == ['package.json']
    assert not any('node_modules' in f['path'] for f in e['files'])
    assert e['files_total'] == 3


def test_path_non_valido_exit_2(tmp_path):
    r = subprocess.run([sys.executable, SCRIPT, str(tmp_path / 'no')], capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r.returncode == 2

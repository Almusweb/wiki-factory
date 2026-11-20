"""log_tail_check.py — voci nuove di wiki/log.md: chiavi ripetute e intestazione incompleta."""
import importlib.util
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

import pytest

QUI = os.path.dirname(os.path.abspath(__file__))
FACTORY = os.path.normpath(os.path.join(QUI, '..', '..'))


def _carica(nome, rel):
    spec = importlib.util.spec_from_file_location(nome, os.path.join(FACTORY, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


ltc = _carica('log_tail_check', 'tools/wiki/log_tail_check.py')
ifh = _carica('install_factory_hooks_lt', 'tools/vcs/install_factory_hooks.py')

TESTATA = '---\ntype: wiki-log\nappend_only: true\n---\n\n# Wiki Log\n\n'

START = ('---\ndate: 2026-11-12\ntype: session-start\nsession_id: aaaa1111\noperator: Tester\n'
         'branch: main\n---\n\n')
CLOSE = ('---\ndate: 2026-11-12\ntype: session-close\nsession_label: session-2026-11-12-10-aaaa1111\n'
         'operator: Tester\noutcome: completed\nartifact: raw/sessions/x.md\ncontext: "lavoro"\n---\n\n')
REVIEW = ('---\ndate: 2026-11-12\ntype: review\nagent: code-reviewer\ntsk: X-TSK-1\niter: 1\nverdict: pass\n'
          'context: "review"\n---\n\n')
DEVELOP = ('---\ndate: 2026-11-12\nagent: fe-dev\ntask: X-TSK-2\ntype: develop\noutcome: completed\n'
           'summary: >\n  prima riga rientrata\n  seconda riga\nwork_commits: [abc]\n---\n\n')
VOCE_TITOLO = ('## [2026-11-12T10:00Z] fix | Titolo della voce (wiki-keeper)\n\n'
               '- context: testo libero in un elenco\n- date: non e una chiave\n\n')

# voce rovinata come quella di una sessione reale: la chiusura di una sessione fusa con la successiva
FUSA = ('---\ndate: 2026-11-12\ntype: session-close\nsession_label: s-1\noperator: Tester\noutcome: completed\n'
        'artifact: a.md\ncontext: "uno"\nsession_label: s-2\noperator: Luisa\noutcome: completed\n'
        'artifact: b.md\ncontext: "due"\n---\n\n')
SENZA_DATE_TYPE = '---\nagent: fe-dev\ntask: X-TSK-3\noutcome: completed\nsummary: "voce senza intestazione"\n---\n\n'


def _p(base, nuovo):
    return ltc.check_texts(nuovo, base)


# --- regole ---------------------------------------------------------------------------------

def test_voci_corrette_passano():
    base = TESTATA + START
    assert _p(base, base + CLOSE + REVIEW + DEVELOP) == []


def test_chiavi_ripetute_nel_blocco_nuovo():
    base = TESTATA + START
    problemi = _p(base, base + FUSA)
    assert len(problemi) == 1
    assert 'chiavi ripetute' in problemi[0] and 'session_label' in problemi[0]
    assert 'wiki/log.md, riga' in problemi[0]


@pytest.mark.parametrize('rimosso', ['type: review\n', 'date: 2026-11-12\n', 'agent: code-reviewer\n'])
def test_review_senza_date_type_o_autore_ora_blocca(rimosso):
    """Una voce di review senza una di queste chiavi e senza chiavi ripetute prima passava."""
    base = TESTATA + START
    problemi = _p(base, base + REVIEW.replace(rimosso, ''))
    assert len(problemi) == 1 and 'intestazione incompleta' in problemi[0]


def test_develop_senza_date_e_type():
    base = TESTATA + START
    problemi = _p(base, base + SENZA_DATE_TYPE)
    assert len(problemi) == 1
    assert 'manca date, type' in problemi[0] and 'operator' not in problemi[0]
    senza_autore = ltc.check_texts('\n---\nsummary: x\n---\n', '')
    assert 'manca date, type, operator (o agent)' in senza_autore[0]


def test_agent_al_posto_di_operator_e_accettato():
    # le voci di review, develop e dev-handoff del log attuale non hanno `operator`
    base = TESTATA + START
    assert _p(base, base + REVIEW) == []


def test_valore_a_piu_righe_non_genera_chiavi():
    base = TESTATA
    voce = DEVELOP.replace('  prima riga rientrata\n', '  prima riga rientrata\n  note: dentro il testo\n')
    assert _p(base, base + voce) == []


def test_voci_con_titolo_non_sono_blocchi():
    base = TESTATA + START
    assert _p(base, base + VOCE_TITOLO + VOCE_TITOLO.replace('10:00', '11:00')) == []


def test_voce_con_titolo_tra_due_blocchi_non_si_fonde_con_i_vicini():
    base = TESTATA
    nuovo = base + START + VOCE_TITOLO + CLOSE
    assert _p(base, nuovo) == []


def test_base_rovinata_voci_nuove_corrette():
    base = TESTATA + START + FUSA + SENZA_DATE_TYPE
    assert _p(base, base + CLOSE + REVIEW) == []


def test_base_rovinata_voce_nuova_rovinata():
    base = TESTATA + START + FUSA
    assert len(_p(base, base + FUSA.replace('s-1', 's-9'))) == 1


def test_frontmatter_di_apertura_del_file_non_e_una_voce():
    assert _p('', TESTATA + START) == []


def test_blocco_senza_separatore_con_chiavi_ripetute():
    base = TESTATA
    nuovo = base + 'date: 2026-11-12\ncontext: "a"\ncontext: "b"\n\n'
    problemi = _p(base, nuovo)
    assert len(problemi) == 1 and 'chiavi ripetute context' in problemi[0]


def test_fine_riga_windows():
    base = (TESTATA + START).replace('\n', '\r\n')
    nuovo = base + (CLOSE + REVIEW).replace('\n', '\r\n')
    assert _p(base, nuovo) == []
    assert len(_p(base, base + FUSA.replace('\n', '\r\n'))) == 1
    # base con \n e nuovo con \r\n: le stesse voci non risultano nuove
    assert _p(TESTATA + START, base + CLOSE.replace('\n', '\r\n')) == []


def test_messaggio_dice_file_blocco_e_cosa_manca():
    base = TESTATA
    problemi = _p(base, base + REVIEW.replace('type: review\n', ''))
    assert problemi[0].startswith('wiki/log.md, riga ')
    assert 'date: 2026-11-12' in problemi[0] and 'tsk: X-TSK-1' in problemi[0]
    assert 'manca type' in problemi[0]


def test_nel_testo_nessun_nome_di_persona():
    testo = pathlib.Path(FACTORY, 'tools/wiki/log_tail_check.py').read_text(encoding='utf-8')
    assert 'Musio' not in testo and 'Alessandro' not in testo


# --- repo temporaneo ------------------------------------------------------------------------

def _run(cwd, *args, stdin=None):
    return subprocess.run(list(args), cwd=cwd, capture_output=True, text=True, input=stdin, timeout=120, encoding="utf-8", errors="replace")


def _git(cwd, *args):
    r = _run(cwd, 'git', *args)
    assert r.returncode == 0, (args, r.stderr)
    return r.stdout.strip()


@pytest.fixture
def repo():
    r = tempfile.mkdtemp(prefix='logtail-')
    try:
        os.makedirs(os.path.join(r, 'tools/wiki'))
        os.makedirs(os.path.join(r, 'wiki'))
        shutil.copy(os.path.join(FACTORY, 'tools/wiki/log_tail_check.py'), os.path.join(r, 'tools/wiki/log_tail_check.py'))
        _scrivi(r, TESTATA + START)
        _git(r, 'init', '-q', '-b', 'main')
        _git(r, 'config', 'user.email', 't@t')
        _git(r, 'config', 'user.name', 't')
        _git(r, 'config', 'commit.gpgsign', 'false')
        _git(r, 'add', '.')
        _git(r, 'commit', '-qm', 'base')
        yield r
    finally:
        shutil.rmtree(r, ignore_errors=True)


def _scrivi(r, testo, newline=None):
    with open(os.path.join(r, 'wiki/log.md'), 'w', encoding='utf-8', newline=newline) as f:
        f.write(testo)


def _accoda(r, testo, msg='voce'):
    with open(os.path.join(r, 'wiki/log.md'), 'a', encoding='utf-8', newline='') as f:
        f.write(testo)
    _git(r, 'commit', '-qam', msg)
    return _git(r, 'rev-parse', 'HEAD')


def _script(r):
    return [sys.executable, os.path.join(r, 'tools', 'wiki', 'log_tail_check.py')]


def _remote(repo):
    bare = repo + '-remote.git'
    _git(repo, 'init', '-q', '--bare', bare)
    _git(repo, 'remote', 'add', 'origin', bare)
    _git(repo, 'push', '-q', 'origin', 'main')
    _git(repo, 'fetch', '-q', 'origin')
    return bare


def test_pre_push_commit_rovinato_blocca(repo):
    bare = _remote(repo)
    try:
        base = _git(repo, 'rev-parse', 'HEAD')
        tip = _accoda(repo, FUSA)
        esito = _run(repo, *_script(repo), '--pre-push', stdin=f'refs/heads/main {tip} refs/heads/main {base}\n')
        assert esito.returncode == 1
        assert 'PUSH BLOCCATO' in esito.stderr and 'chiavi ripetute' in esito.stderr and 'wiki/log.md' in esito.stderr
    finally:
        shutil.rmtree(bare, ignore_errors=True)


def test_pre_push_commit_corretto_passa(repo):
    bare = _remote(repo)
    try:
        base = _git(repo, 'rev-parse', 'HEAD')
        tip = _accoda(repo, CLOSE + REVIEW + VOCE_TITOLO)
        esito = _run(repo, *_script(repo), '--pre-push', stdin=f'refs/heads/main {tip} refs/heads/main {base}\n')
        assert esito.returncode == 0, esito.stderr
    finally:
        shutil.rmtree(bare, ignore_errors=True)


def test_pre_push_voce_rovinata_in_un_commit_intermedio_si_vede_alla_punta(repo):
    bare = _remote(repo)
    try:
        base = _git(repo, 'rev-parse', 'HEAD')
        _accoda(repo, SENZA_DATE_TYPE)
        tip = _accoda(repo, CLOSE)
        esito = _run(repo, *_script(repo), '--pre-push', stdin=f'refs/heads/main {tip} refs/heads/main {base}\n')
        assert esito.returncode == 1 and 'intestazione incompleta' in esito.stderr
    finally:
        shutil.rmtree(bare, ignore_errors=True)


def test_pre_push_ref_nuovo_usa_il_merge_base_con_origin_main(repo):
    bare = _remote(repo)
    try:
        _git(repo, 'checkout', '-q', '-b', 'feature')
        tip = _accoda(repo, FUSA)
        esito = _run(repo, *_script(repo), '--pre-push', stdin=f'refs/heads/feature {tip} refs/heads/feature {"0" * 40}\n')
        assert esito.returncode == 1
        # una base gia' rovinata sul remoto non e' colpa del push
        _git(repo, 'checkout', '-q', 'main')
        _git(repo, 'merge', '-q', '--ff-only', 'feature')
        _git(repo, 'push', '-q', 'origin', 'main')
        _git(repo, 'fetch', '-q', 'origin')
        tip2 = _accoda(repo, CLOSE)
        base2 = _git(repo, 'rev-parse', 'HEAD~1')
        esito = _run(repo, *_script(repo), '--pre-push', stdin=f'refs/heads/main {tip2} refs/heads/main {base2}\n')
        assert esito.returncode == 0, esito.stderr
    finally:
        shutil.rmtree(bare, ignore_errors=True)


def test_pre_push_cancellazione_e_righe_malformate_ignorate(repo):
    assert _run(repo, *_script(repo), '--pre-push',
                stdin=f'(delete) {"0" * 40} refs/heads/x {"a" * 40}\nmalformata\n').returncode == 0


def test_pre_push_senza_origin_main_e_controllo_incompleto(repo):
    tip = _git(repo, 'rev-parse', 'HEAD')
    esito = _run(repo, *_script(repo), '--pre-push', stdin=f'refs/heads/x {tip} refs/heads/x {"0" * 40}\n')
    assert esito.returncode == 2 and 'incompleto' in esito.stderr


def test_pre_push_fine_riga_windows(repo):
    bare = _remote(repo)
    try:
        base = _git(repo, 'rev-parse', 'HEAD')
        tip = _accoda(repo, (CLOSE + FUSA).replace('\n', '\r\n'))
        esito = _run(repo, *_script(repo), '--pre-push', stdin=f'refs/heads/main {tip} refs/heads/main {base}\n')
        assert esito.returncode == 1
    finally:
        shutil.rmtree(bare, ignore_errors=True)


# --- uso a mano -----------------------------------------------------------------------------

def test_manuale_contro_la_base(repo):
    base = _git(repo, 'rev-parse', 'HEAD')
    _scrivi(repo, TESTATA + START + CLOSE)
    esito = _run(repo, *_script(repo), '--base', base)
    assert esito.returncode == 0 and 'ben formate' in esito.stdout
    _scrivi(repo, TESTATA + START + FUSA)
    esito = _run(repo, *_script(repo), '--base', base)
    assert esito.returncode == 1 and 'chiavi ripetute' in esito.stdout


def test_manuale_base_sconosciuta_e_controllo_incompleto(repo):
    esito = _run(repo, *_script(repo), '--base', 'origin/non-esiste')
    assert esito.returncode == 2 and 'incompleto' in esito.stderr


# --- caso reale -----------------------------------------------------------------------------

def test_caso_reale_della_close_rovinata_del_12_11():
    """Commit b421673c8: la close di 068e8b2f con due blocchi fusi."""
    sha = 'b421673c8'
    r = subprocess.run(['git', 'show', f'{sha}:wiki/log.md'], cwd=FACTORY, capture_output=True, timeout=60)
    if r.returncode:
        pytest.skip('storia della factory non disponibile')
    padre = subprocess.run(['git', 'show', f'{sha}^:wiki/log.md'], cwd=FACTORY, capture_output=True, timeout=60)
    assert padre.returncode == 0
    problemi = ltc.check_texts(r.stdout.decode('utf-8'), padre.stdout.decode('utf-8'))
    assert problemi and any('chiavi ripetute' in p and 'session_label' in p for p in problemi)


# --- aggancio al pre-push -------------------------------------------------------------------

def test_hook_pre_push_installato_blocca_il_log_rovinato(repo):
    bare = _remote(repo)
    try:
        assert ifh.main(['--only', 'pre-push', '--root', repo]) == 0
        _accoda(repo, FUSA)
        esito = _run(repo, 'git', 'push', 'origin', 'main')
        assert esito.returncode != 0 and 'PUSH BLOCCATO' in esito.stderr
        _git(repo, 'reset', '-q', '--hard', 'HEAD~1')
        _accoda(repo, CLOSE)
        esito = _run(repo, 'git', 'push', 'origin', 'main')
        assert esito.returncode == 0, esito.stderr
    finally:
        shutil.rmtree(bare, ignore_errors=True)


def test_hook_pre_push_senza_il_controllo_non_blocca(repo):
    bare = _remote(repo)
    try:
        assert ifh.main(['--only', 'pre-push', '--root', repo]) == 0
        os.remove(os.path.join(repo, 'tools/wiki/log_tail_check.py'))
        _accoda(repo, FUSA)
        assert _run(repo, 'git', 'push', 'origin', 'main').returncode == 0
    finally:
        shutil.rmtree(bare, ignore_errors=True)


def test_pre_push_installato_contiene_il_controllo_del_log():
    assert 'log_tail_check.py' in ifh.PRE_PUSH_HOOK and 'conflict_markers_check.py' in ifh.PRE_PUSH_HOOK

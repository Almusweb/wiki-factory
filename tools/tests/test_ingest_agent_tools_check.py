"""Check 4bk: agenti che leggono contenuto non fidato con Bash nei tools."""
import importlib.util
import json
import os
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.normpath(os.path.join(QUI, '..', 'lint', 'check-ingest-agent-tools.py'))
OGGI = '2026-11-16'


def agente(root, nome, tools, caps):
    d = root / '.claude' / 'agents'
    d.mkdir(parents=True, exist_ok=True)
    righe = ''.join('  - %s\n' % c for c in caps)
    (d / (nome + '.md')).write_text(
        '---\nname: %s\ntools: [%s]\ncapabilities:\n%s---\n# corpo\n' % (nome, ', '.join(tools), righe), encoding="utf-8")


def config(root, testo):
    (root / 'factory.config.yaml').write_text(testo, encoding="utf-8")


def esegui(root, *extra):
    r = subprocess.run([sys.executable, SCRIPT, '--json', '--root', str(root), '--oggi', OGGI, *extra],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, json.loads(r.stdout)


def con_eccezione(scade, required_from='null'):
    return ('ingest_agent_tools:\n  exceptions:\n'
            '    - {agente: est, motivo: "serve la shell", scade: %s}\n'
            '  required_from: %s\n' % (scade, required_from))


def test_estrattore_senza_bash_ok(tmp_path):
    agente(tmp_path, 'est', ['Read', 'Write'], ['raw-sync', 'x-extraction'])
    assert esegui(tmp_path)[1]['findings'] == []


def test_estrattore_con_bash_senza_eccezione_warning(tmp_path):
    agente(tmp_path, 'est', ['Read', 'Bash'], ['x-extraction'])
    _, out = esegui(tmp_path)
    assert [f['agente'] for f in out['findings']] == ['est']
    assert out['severita'] == 'WARNING'


def test_raw_sync_da_solo_basta(tmp_path):
    agente(tmp_path, 'est', ['Bash'], ['raw-sync'])
    assert len(esegui(tmp_path)[1]['findings']) == 1


def test_eccezione_valida_ok(tmp_path):
    agente(tmp_path, 'est', ['Bash'], ['x-extraction'])
    config(tmp_path, con_eccezione('2027-05-16'))
    assert esegui(tmp_path)[1]['findings'] == []


def test_eccezione_scaduta_warning(tmp_path):
    agente(tmp_path, 'est', ['Bash'], ['x-extraction'])
    config(tmp_path, con_eccezione('2026-11-15'))
    _, out = esegui(tmp_path)
    assert 'scaduta' in out['findings'][0]['motivo']
    assert out['severita'] == 'WARNING'


def test_eccezione_non_copre_agente_nuovo(tmp_path):
    agente(tmp_path, 'est', ['Bash'], ['x-extraction'])
    agente(tmp_path, 'nuovo', ['Bash'], ['y-extraction'])
    config(tmp_path, con_eccezione('2027-05-16'))
    assert [f['agente'] for f in esegui(tmp_path)[1]['findings']] == ['nuovo']


def test_required_from_passata_error(tmp_path):
    agente(tmp_path, 'est', ['Bash'], ['x-extraction'])
    config(tmp_path, con_eccezione('2026-01-01', required_from='2026-11-16'))
    rc, out = esegui(tmp_path, '--strict')
    assert out['severita'] == 'ERROR' and rc == 1


def test_required_from_futura_resta_warning(tmp_path):
    agente(tmp_path, 'est', ['Bash'], ['x-extraction'])
    config(tmp_path, 'ingest_agent_tools:\n  required_from: 2027-01-01\n')
    rc, out = esegui(tmp_path, '--strict')
    assert out['severita'] == 'WARNING' and rc == 0


def test_agente_non_estrattore_con_bash_ok(tmp_path):
    agente(tmp_path, 'dev', ['Read', 'Bash'], ['code-writing'])
    assert esegui(tmp_path)[1]['findings'] == []


def test_agente_esplicito_in_config(tmp_path):
    agente(tmp_path, 'dev', ['Bash'], ['code-writing'])
    config(tmp_path, 'ingest_agent_tools:\n  agenti: [dev]\n')
    assert [f['agente'] for f in esegui(tmp_path)[1]['findings']] == ['dev']


def carica_senza_yaml(monkeypatch):
    monkeypatch.setitem(sys.modules, 'yaml', None)
    spec = importlib.util.spec_from_file_location('check_4bk_noyaml', SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.yaml is None
    return mod


def test_senza_pyyaml_eccezioni_non_lette_warning(tmp_path, monkeypatch):
    mod = carica_senza_yaml(monkeypatch)
    agente(tmp_path, 'est', ['Read', 'Bash'], ['pdf-extraction'])
    config(tmp_path, con_eccezione('2027-05-16'))
    v = mod.check(tmp_path, OGGI)
    assert len(v) == 1 and 'PyYAML assente' in v[0]['motivo']
    assert mod.severita(tmp_path, OGGI, v) == 'WARNING'


def test_senza_pyyaml_severita_nonverificabile_resta_warning(tmp_path, monkeypatch):
    mod = carica_senza_yaml(monkeypatch)
    config(tmp_path, con_eccezione('2027-05-16', '2026-01-01'))
    v = mod.check(tmp_path, OGGI)
    assert mod.severita(tmp_path, OGGI, v) == 'WARNING'


def test_senza_pyyaml_frontmatter_stdlib(tmp_path, monkeypatch):
    mod = carica_senza_yaml(monkeypatch)
    fm = mod.frontmatter('---\nname: est\ntools: [Read, Bash]\ncapabilities:\n  - raw-sync   # c\n'
                         '  - pdf-extraction\n\n---\n')
    assert fm == {'name': 'est', 'tools': ['Read', 'Bash'], 'capabilities': ['raw-sync', 'pdf-extraction']}
    assert mod.frontmatter('---\nname: a\ntools: Read, Bash\n---\n')['tools'] == ['Read', 'Bash']


def test_senza_pyyaml_senza_config_rileva_comunque(tmp_path, monkeypatch):
    mod = carica_senza_yaml(monkeypatch)
    agente(tmp_path, 'est', ['Bash'], ['raw-sync'])
    v = mod.check(tmp_path, OGGI)
    assert [x['agente'] for x in v] == ['est']

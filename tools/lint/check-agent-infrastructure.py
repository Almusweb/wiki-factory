#!/usr/bin/env python3
"""Check 4ai — integrita' strutturale del layer agenti (WARNING, always-on).

Esecuzione a script della specifica in `.claude/skills/lint-checks-agent-qa.md` §Check 4ai
(migrazione dei check LLM a script, tavola rotonda 3f8a1c5e A12). Tre sotto-check:

- 4ai.1 `agent-invalid-tool`: un tool in `tools:` fuori dalla whitelist della specifica.
- 4ai.2 `agent-skill-missing`: un riferimento a skill senza `.claude/skills/<nome>.md`.
  Candidati: path espliciti `.claude/skills/<nome>.md` e token in backtick preceduti da `vedi`.
  I nomi di agenti e comandi esistenti non sono skill mancanti.
- 4ai.3 `agent-command-missing`: un riferimento a comando senza `.claude/commands/<nome>.md`.
  Candidati: path espliciti `.claude/commands/<nome>.md` e slash-command `/<nome>` in backtick
  (es. `` `/run` ``). Gli slash nudi nel testo non sono candidati: sono quasi sempre path.

Severita': WARNING, mai ERROR, mai heal-eligible.

Non garantisce: i riferimenti scritti in altre forme (prosa senza backtick, link markdown
senza path esplicito); che una skill esistente sia quella giusta; i tool effettivi a runtime.

Uso:
    python3 tools/lint/check-agent-infrastructure.py [--root <factory>] [--json] [--strict]
Exit code: 0 anche con finding; con --strict 1 se c'e' almeno un ERROR (mai, per costruzione).
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lint_comune as lc  # noqa: E402

CHECK = '4ai'
# Whitelist della specifica (lint-checks-agent-qa.md §4ai, passo 3).
TOOL_VALIDI = {
    'Read', 'Write', 'Edit', 'Glob', 'Bash', 'TodoWrite', 'Task', 'Grep', 'WebFetch', 'WebSearch',
    'Agent', 'SendMessage', 'Monitor', 'CronCreate', 'CronDelete', 'CronList', 'DesignSync',
    'EnterPlanMode', 'ExitPlanMode', 'EnterWorktree', 'ExitWorktree', 'NotebookEdit',
    'PushNotification', 'RemoteTrigger', 'TaskOutput', 'TaskStop',
}
_SKILL_PATH = re.compile(r'\.claude/skills/([a-z0-9][a-z0-9-]*)\.md')
_SKILL_VEDI = re.compile(r'\bvedi\s+`([a-z0-9][a-z0-9-]*)`', re.I)
_CMD_PATH = re.compile(r'\.claude/commands/([a-z0-9][a-z0-9-]*)\.md')
_CMD_SLASH = re.compile(r'`/([a-z][a-z0-9-]*)(?:\s[^`]*)?`')


def _corpo(testo):
    m = re.match(r'^---\n.*?\n---\n?', testo, re.S)
    return testo[m.end():] if m else testo


def _tools(fm):
    v = fm.get('tools')
    if isinstance(v, list):
        voci = v
    else:
        voci = re.split(r'[,\s]+', lc.testo_di(v))
    return [t.strip().strip('"\'') for t in voci if t and t.strip()]


def _nomi(cartella):
    return {f[:-3] for f in os.listdir(cartella) if f.endswith('.md')} if os.path.isdir(cartella) else set()


def verifica(radice):
    base = os.path.join(radice, '.claude')
    agenti, skill, comandi = (_nomi(os.path.join(base, d)) for d in ('agents', 'skills', 'commands'))
    findings, stats = [], {'agenti': len(agenti)}
    for nome in sorted(agenti):
        rel = os.path.join('.claude', 'agents', nome + '.md')
        testo = lc.leggi(os.path.join(radice, rel))
        fm = lc.frontmatter_da_testo(testo) or {}
        corpo = _corpo(testo)
        for tool in _tools(fm):
            if tool not in TOOL_VALIDI:
                findings.append(lc.finding('WARNING', 'agent-invalid-tool', '4ai.1',
                                           "%s: tool '%s' non in whitelist. Correggi il frontmatter tools:." % (rel, tool),
                                           path=rel))
        ref_skill = set(_SKILL_PATH.findall(corpo)) | {
            t for t in _SKILL_VEDI.findall(corpo) if t not in agenti and t not in comandi}
        for s in sorted(ref_skill - skill):
            findings.append(lc.finding('WARNING', 'agent-skill-missing', '4ai.2',
                                       "%s: referenzia skill '%s' ma .claude/skills/%s.md non esiste." % (rel, s, s),
                                       path=rel))
        ref_cmd = set(_CMD_PATH.findall(corpo)) | set(_CMD_SLASH.findall(corpo))
        for c in sorted(ref_cmd - comandi):
            findings.append(lc.finding('WARNING', 'agent-command-missing', '4ai.3',
                                       "%s: referenzia comando /%s ma .claude/commands/%s.md non esiste." % (rel, c, c),
                                       path=rel))
    return findings, stats


def main(argv=None):
    args = lc.parser(__doc__).parse_args(argv)
    args.root = os.path.abspath(args.root)
    findings, stats = verifica(args.root)
    diag = [] if findings else ['[%s] OK — %d agenti: tool, skill e comandi referenziati esistono' % (
        CHECK, stats['agenti'])]
    return lc.emetti(args, CHECK, findings, diag, stats)


if __name__ == '__main__':
    sys.exit(main())

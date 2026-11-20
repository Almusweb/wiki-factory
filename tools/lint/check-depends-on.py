#!/usr/bin/env python3
"""Check 4g — coerenza scheduler / depends_on del kanban.

Esecuzione a script della specifica in `.claude/skills/lint-checks-kanban.md` §4g (migrazione dei
check LLM a script, tavola rotonda 3f8a1c5e A12). Legge tutta la popolazione di
`management/kanban/**` (archivio incluso) e il blocco `scheduler:` di factory.config.yaml.

| Codice | Severita' | Regola |
|---|---|---|
| invalid-depends-on-type | ERROR | un id in `depends_on` di tipo diverso dall'host (EP->EP, US->US, TSK->TSK) |
| self-depends-on | ERROR | `depends_on` contiene il proprio id |
| orphan-depends-on | WARNING | id in `depends_on` senza file `<id>.md` nel kanban |
| depends-on-cycle | ERROR | ciclo nel grafo `depends_on` (Kahn), con i nodi coinvolti |
| dependencies-drift-candidate | INFO | TSK: `## Dependencies` del corpo e `depends_on` sembrano differire |
| empty-code-path-glob | WARNING | TSK: glob vuoto in `code_path` |
| code-path-overlap | INFO | con `code_path_conflict: strict`, >= 2 TSK `todo` al level 0 con lo stesso glob |
| orphan-blocked-by-q | WARNING | TSK: `blocked_by` cita una Q assente da management/questions.md |
| stale-blocked-by-tsk | WARNING | TSK: `blocked_by` cita una Q gia' in [RISOLTE] |
| invalid-scheduler-* | ERROR/WARNING | valori del blocco `scheduler:` fuori dominio |

Differenza dichiarata dalla specifica: `dependencies-drift` (WARNING) e' semantico, perche' la sezione
`## Dependencies` e' prosa libera (dipendenze a valle, intenzioni, intervalli). Lo script emette solo
candidati INFO; il giudizio resta all'esecutore, che li conferma o scarta uno per uno.

Scelte dichiarate dove la specifica e' muta: il level 0 di code-path-overlap considera i soli TSK
`status: todo` (i candidati dello scheduler) con dipendenze assenti o tutte `done`; il drift
conta come dipendenze della sezione `## Dependencies` le voci che iniziano con un id TSK
(`- TSK-NNN`, anche in grassetto o backtick) e quelle che dicono «depends_on» / «dipende da» /
«bloccato da»; le altre voci (es. «Output per: TSK-NNN», dipendenze a valle) non contano.

Uso:
    python3 tools/lint/check-depends-on.py [--root <factory>] [--json] [--strict]
Exit code: 0 anche con finding; con --strict 1 se c'e' almeno un ERROR.
"""
from __future__ import annotations

import os
import re
import sys
from collections import defaultdict, deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lint_comune as lc  # noqa: E402
import kanban_ids  # noqa: E402

CHECK = '4g'
QUESTIONS = 'management/questions.md'
Q_RE = re.compile(r'\bQ[-_](?:[A-Z0-9]+-)*\d+\b')
_SEZ_DEP = re.compile(r'^##\s+Dependencies\s*$', re.M)
_VOCE = re.compile(r'^\s*[-*]\s+(.*)$', re.M)
_TSK_IN_TESTO = re.compile(r'\b(?:[A-Z]{2,4}-)?TSK-\d+\b')
_INIZIA_CON_TSK = re.compile(r'^[*`\[\s]*((?:[A-Z]{2,4}-)?TSK-\d+)\b')
_INTERVALLO = re.compile(r'\b((?:[A-Z]{2,4}-)?TSK-)(\d+)\s*\.\.\s*(?:(?:[A-Z]{2,4}-)?TSK-)?(\d+)\b')
_INTERVALLO_MAX = 500  # come kanban_ids.tsk_dichiarati


def _espandi(voce):
    """Gli id TSK di una voce, con gli intervalli `TSK-a..TSK-b` espansi."""
    ids = set(_TSK_IN_TESTO.findall(voce))
    for pre, a, b in _INTERVALLO.findall(voce):
        if 0 <= int(b) - int(a) <= _INTERVALLO_MAX:
            ids.update('%s%0*d' % (pre, len(a), n) for n in range(int(a), int(b) + 1))
    return ids


_DIPENDE = re.compile(r'depends[_ ]on|dipende\s+da|bloccat[oa]\s+da', re.I)


def _ids(valore):
    return [m.group(0) for m in kanban_ids.ID_IN_TESTO.finditer(lc.testo_di(valore))]


def _lista(valore):
    if isinstance(valore, list):
        return [lc.testo_di(v) for v in valore]
    s = lc.testo_di(valore)
    return [s] if s or valore == '' else []


def _dipendenze_nel_corpo(testo):
    m = _SEZ_DEP.search(testo)
    if not m:
        return None
    resto = testo[m.end():]
    fine = re.search(r'^##\s', resto, re.M)
    deps = set()
    for voce in _VOCE.findall(resto[:fine.start()] if fine else resto):
        m = _INIZIA_CON_TSK.match(voce)
        if m and _INTERVALLO.match(voce.lstrip('*`[ ')):
            deps.update(_espandi(voce.split(' ')[0] if ' ' in voce else voce))
        elif m:
            deps.add(m.group(1))
        elif _DIPENDE.search(voce):
            deps.update(_espandi(voce))
    return deps


def _questions(radice):
    path = os.path.join(radice, QUESTIONS)
    if not os.path.isfile(path):
        return None, None
    tutte, risolte, sezione = set(), set(), None
    for riga in lc.leggi(path).splitlines():
        m = re.match(r'^##\s+\[(APERTE|RISOLTE)\]', riga)
        if m:
            sezione = m.group(1)
            continue
        if re.match(r'^##\s', riga) and not riga.startswith('###'):
            sezione = None
            continue
        if sezione and re.match(r'^###+\s', riga):
            ids = set(Q_RE.findall(riga))
            tutte |= ids
            if sezione == 'RISOLTE':
                risolte |= ids
    return tutte, risolte


def _scheduler(radice):
    path = os.path.join(radice, 'factory.config.yaml')
    if not os.path.isfile(path):
        return None
    m = re.search(r'^scheduler:\n((?:[ \t]+[^\n]*\n?|[ \t]*\n)*)', lc.leggi(path), re.M)
    if not m:
        return None
    out = {}
    for riga in m.group(1).splitlines():
        km = re.match(r'^  ([a-z_]+):\s*([^\s#]*)', riga)
        if km:
            out[km.group(1)] = km.group(2).strip('"\'')
    return out


def _intero(v):
    return int(v) if re.fullmatch(r'\d+', v or '') else None


def check_scheduler(sch):
    out = []
    if sch is None:
        return out
    f = lambda sev, cod, msg: out.append(lc.finding(sev, cod, CHECK, msg, path='factory.config.yaml'))  # noqa: E731
    if 'enabled' in sch and sch['enabled'] not in ('true', 'false'):
        f('ERROR', 'invalid-scheduler-enabled', 'scheduler.enabled = %r, atteso true|false' % sch['enabled'])
    mp, gt = _intero(sch.get('max_parallel')), _intero(sch.get('parallel_gate_threshold'))
    if 'max_parallel' in sch and (mp is None or mp < 1):
        f('WARNING', 'invalid-max-parallel', 'scheduler.max_parallel = %r, atteso intero >= 1 (default 4)' % sch['max_parallel'])
    if 'parallel_gate_threshold' in sch and (gt is None or gt < 1 or (mp is not None and mp >= 1 and gt > mp)):
        f('WARNING', 'invalid-gate-threshold',
          'scheduler.parallel_gate_threshold = %r, atteso intero fra 1 e max_parallel (default 3)' % sch['parallel_gate_threshold'])
    if 'code_path_conflict' in sch and sch['code_path_conflict'] not in ('strict', 'warn', 'off'):
        f('ERROR', 'invalid-conflict-mode', 'scheduler.code_path_conflict = %r, atteso strict|warn|off' % sch['code_path_conflict'])
    if 'empty_code_path_policy' in sch and sch['empty_code_path_policy'] not in ('serial', 'parallel'):
        f('ERROR', 'invalid-empty-policy', 'scheduler.empty_code_path_policy = %r, atteso serial|parallel' % sch['empty_code_path_policy'])
    return out


def _cicli(grafo):
    """Nodi rimasti dopo Kahn = nodi su un ciclo o a valle di un ciclo; si riportano le componenti cicliche."""
    nodi = set(grafo) | {d for ds in grafo.values() for d in ds}
    indeg = {n: 0 for n in nodi}
    for n, ds in grafo.items():
        for d in ds:
            indeg[n] += 1  # n dipende da d: arco d -> n
    figli = defaultdict(set)
    for n, ds in grafo.items():
        for d in ds:
            figli[d].add(n)
    coda = deque(n for n, k in indeg.items() if k == 0)
    while coda:
        d = coda.popleft()
        for n in figli[d]:
            indeg[n] -= 1
            if indeg[n] == 0:
                coda.append(n)
    resto = {n for n, k in indeg.items() if k > 0}
    # componenti fortemente connesse fra i rimasti (Tarjan iterativo-ricorsivo, grafo piccolo)
    idx, low, stack, on, comp, contatore = {}, {}, [], set(), [], [0]

    def visita(v):
        idx[v] = low[v] = contatore[0]
        contatore[0] += 1
        stack.append(v)
        on.add(v)
        for w in grafo.get(v, ()):
            if w not in resto:
                continue
            if w not in idx:
                visita(w)
                low[v] = min(low[v], low[w])
            elif w in on:
                low[v] = min(low[v], idx[w])
        if low[v] == idx[v]:
            c = []
            while True:
                w = stack.pop()
                on.discard(w)
                c.append(w)
                if w == v:
                    break
            if len(c) > 1:
                comp.append(sorted(c))

    sys.setrecursionlimit(max(10000, sys.getrecursionlimit()))
    for v in sorted(resto):
        if v not in idx:
            visita(v)
    return sorted(comp)


def verifica(radice):
    arts = lc.raccogli_kanban(radice)
    per_id = {}
    for a in arts:
        per_id.setdefault(a.id, a)
    findings = []
    grafo = {}
    con_dep = 0
    for a in arts:
        fm = a.fm or {}
        if 'depends_on' not in fm:
            continue
        deps = _ids(fm.get('depends_on'))
        if deps:
            con_dep += 1
        validi = set()
        for d in deps:
            if d == a.id:
                findings.append(lc.finding('ERROR', 'self-depends-on', CHECK, '%s: depends_on contiene il proprio id' % a.id, path=a.rel))
                continue
            if kanban_ids.tipo_di(d) != a.tipo:
                findings.append(lc.finding('ERROR', 'invalid-depends-on-type', CHECK,
                                           '%s: depends_on cita %s (%s), atteso solo %s' % (a.id, d, kanban_ids.tipo_di(d), a.tipo),
                                           path=a.rel))
                continue
            if d not in per_id:
                findings.append(lc.finding('WARNING', 'orphan-depends-on', CHECK,
                                           '%s: depends_on cita %s, che non esiste nel kanban' % (a.id, d), path=a.rel))
                continue
            validi.add(d)
        if validi:
            grafo[a.id] = validi
        if a.tipo == 'TSK':
            corpo = _dipendenze_nel_corpo(a.testo)
            fm_tsk = {d for d in deps if kanban_ids.tipo_di(d) == 'TSK'}
            if corpo is not None and corpo != fm_tsk:
                solo_corpo, solo_fm = sorted(corpo - fm_tsk), sorted(fm_tsk - corpo)
                findings.append(lc.finding('INFO', 'dependencies-drift-candidate', CHECK,
                                           '%s: ## Dependencies e depends_on differiscono (solo corpo: %s; solo frontmatter: %s)' % (
                                               a.id, ', '.join(solo_corpo) or '-', ', '.join(solo_fm) or '-'),
                                           path=a.rel))
    for c in _cicli(grafo):
        findings.append(lc.finding('ERROR', 'depends-on-cycle', CHECK, 'ciclo in depends_on: %s' % ' -> '.join(c),
                                   path=per_id[c[0]].rel))

    sch = _scheduler(radice)
    findings += check_scheduler(sch)
    strict = (sch or {}).get('code_path_conflict', 'strict') == 'strict'
    livello0 = defaultdict(list)
    for a in arts:
        if a.tipo != 'TSK' or not a.fm or 'code_path' not in a.fm:
            continue
        globs = _lista(a.fm.get('code_path'))
        if any(not g.strip() for g in globs):
            findings.append(lc.finding('WARNING', 'empty-code-path-glob', CHECK, '%s: glob vuoto in code_path' % a.id, path=a.rel))
        stato = lc.testo_di(a.fm.get('status')).strip()
        deps = grafo.get(a.id, set())
        if strict and stato == 'todo' and all(lc.testo_di((per_id[d].fm or {}).get('status')).strip() == 'done' for d in deps):
            for g in {g.strip() for g in globs if g.strip()}:
                livello0[g].append(a.id)
    for g, ids in sorted(livello0.items()):
        if len(ids) >= 2:
            findings.append(lc.finding('INFO', 'code-path-overlap', CHECK,
                                       '%s condividono code_path %s al level 0: lo scheduler li serializza' % (', '.join(sorted(ids)), g)))

    tutte, risolte = _questions(radice)
    if tutte is not None:
        for a in arts:
            if a.tipo != 'TSK' or not a.fm:
                continue
            for q in sorted(set(Q_RE.findall(lc.testo_di(a.fm.get('blocked_by'))))):
                if q not in tutte:
                    findings.append(lc.finding('WARNING', 'orphan-blocked-by-q', CHECK,
                                               '%s: blocked_by cita %s, assente da %s' % (a.id, q, QUESTIONS), path=a.rel))
                elif q in risolte:
                    findings.append(lc.finding('WARNING', 'stale-blocked-by-tsk', CHECK,
                                               '%s: blocked_by cita %s, gia\' risolta (reconcile-needed)' % (a.id, q), path=a.rel))
    stats = {'artefatti': len(arts), 'con_depends_on': con_dep, 'archi': sum(len(v) for v in grafo.values())}
    return findings, stats


def main(argv=None):
    args = lc.parser(__doc__).parse_args(argv)
    args.root = os.path.abspath(args.root)
    findings, stats = verifica(args.root)
    diag = ['[%s] %d artefatti, %d con depends_on, %d archi nel grafo' % (
        CHECK, stats['artefatti'], stats['con_depends_on'], stats['archi'])]
    return lc.emetti(args, CHECK, findings, diag, stats)


if __name__ == '__main__':
    sys.exit(main())

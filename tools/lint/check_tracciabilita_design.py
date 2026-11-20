#!/usr/bin/env python3
"""Check 4bi — tracciabilita' decisione -> requisito -> task, di sola forma (EP-097, US-384).

Verifica, solo sugli artefatti creati da `design_traceability.required_from` in poi:
  adr-senza-satisfies      ADR `accepted` senza `satisfies: [US-…]`
  unknown-ref              ID in `satisfies` (US), `supersedes` o `decision_refs` (ADR) che non esiste
  adr-senza-premortem      ADR `accepted` senza `premortem: {data, report, esito}` valido; solo con
                           `design_traceability.premortem_pre_tpm: true` (a sottochiave spenta nessun effetto)
  chiusura-senza-ac        TSK `done` la cui tabella `## Chiusura` non cita alcun AC (`ACn`)
  decision-refs-vuoto      INFO: dopo 2 sprint (28 giorni) dall'adozione nessun TSK nel perimetro ha
                           `decision_refs` (criterio di dismissione del campo, Accordo D1)

E' un controllo di FORMA. Un verde dice che i link esistono e sono risolvibili, non che il
requisito sia giusto ne' che la decisione lo soddisfi (Accordo 8 della Tavola Rotonda 5c1d9a7e).

Resta no-op (nessun finding, una riga di diagnostica) se:
  - `design_traceability.enabled` non e' true, o `required_from` manca;
  - non esiste un report W1 (glob `report_w1`, default `wiki/lint/*-w1-design.md`) con frontmatter
    `date`, `n`, `ok_chat_rate`, oppure `required_from` non e' successivo alla sua `date`
    (condizione del Critico: il flag si accende solo dopo una misura con data e numeri);
  - i finding superano `soglia_spegnimento` (default 0.10) degli artefatti nel perimetro: il check
    si sospende e lo dice, perche' un controllo che segnala troppo viene spento a mano e poi ignorato.

Data di un artefatto: `created:` del frontmatter (ADR anche `date:`); senza data e' fuori perimetro.

Uso:
    python3 tools/lint/check_tracciabilita_design.py [--root R] [--json] [--strict] [--forza]
`--forza` ignora enabled, report W1 e soglia (misura a flag spento, come --severita di 4bh);
`--dal AAAA-MM-GG` con --forza sostituisce required_from per stimare i finding su una finestra.
Exit code: 0 anche con finding; con --strict 1 se c'e' almeno un ERROR (qui non ce ne sono).
"""
from __future__ import annotations

import datetime as dt
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lint_comune as lc  # noqa: E402

CHECK = '4bi'
DEFAULT = {'enabled': False, 'required_from': '', 'report_w1': 'wiki/lint/*-w1-design.md',
           'soglia_spegnimento': '0.10', 'premortem_pre_tpm': False}
ADR_DIRS = ('design_&_architecture/decisions', 'wiki')
ADR_ID = re.compile(r'\bADR-(?:[A-Z]+\d*-)*\d+[a-z]?\b')
US_ID = re.compile(r'\b(?:[A-Z]{2,4}-)?US-\d+\b')
AC_ID = re.compile(r'\bAC\d+\b')
CHIUSURA = re.compile(r'^##\s+Chiusura\s*$(.*?)(?=^##\s|\Z)', re.M | re.S)
ESITI_PREMORTEM = ('invariato', 'modificato', 'ritirato')
ISO = re.compile(r'^\d{4}-\d{2}-\d{2}$')
DISMISSIONE_GIORNI = 28


def impostazioni(radice):
    cfg = dict(DEFAULT)
    path = os.path.join(radice, 'factory.config.yaml')
    if os.path.isfile(path):
        m = re.search(r'^design_traceability:[ \t]*(?:#[^\n]*)?\n((?:[ \t]+[^\n]*\n?|[ \t]*\n)*)',
                      lc.leggi(path), re.M)
        if m:
            cfg.update(lc._mini_yaml(m.group(1).splitlines(), 2))
    return cfg


def _data(fm, *campi):
    for c in campi:
        v = lc.testo_di(fm.get(c)).strip().strip('"\'')[:10]
        if ISO.match(v):
            return v
    return ''


def premortem_valido(fm):
    """`premortem: {data: AAAA-MM-GG, report: <path>, esito: invariato|modificato|ritirato}`."""
    v = lc.testo_di(fm.get('premortem'))
    campo = lambda k: (re.search(r'\b%s:\s*["\']?([^,}"\']+)' % k, v) or [None, ''])[1].strip()
    return bool(ISO.match(campo('data')) and campo('report') and campo('esito') in ESITI_PREMORTEM)


def report_w1(radice, pattern):
    """Il report W1 piu' recente con frontmatter valido, o None."""
    validi = []
    for p in glob.glob(os.path.join(radice, pattern)):
        fm = lc.frontmatter(p) or {}
        if _data(fm, 'date') and lc.testo_di(fm.get('n')).strip() and lc.testo_di(fm.get('ok_chat_rate')).strip():
            validi.append((_data(fm, 'date'), os.path.relpath(p, radice).replace(os.sep, '/')))
    return max(validi) if validi else None


def raccogli_adr(radice):
    out = []
    for base in ADR_DIRS:
        for d, _, fs in os.walk(os.path.join(radice, base)):
            for f in sorted(fs):
                if not (f.startswith('ADR-') and f.endswith('.md')):
                    continue
                p = os.path.join(d, f)
                fm = lc.frontmatter(p) or {}
                dal_nome = ADR_ID.search(f)
                ids = {x for x in (lc.testo_di(fm.get('id')).strip(), dal_nome and dal_nome.group(0)) if x}
                ident = lc.testo_di(fm.get('id')).strip() or (dal_nome.group(0) if dal_nome else f[:-3])
                out.append({'id': ident, 'ids': ids, 'rel': os.path.relpath(p, radice).replace(os.sep, '/'),
                            'fm': fm})
    return out


def verifica(radice, forza=False, oggi=None, dal_forzato=None):
    cfg = impostazioni(radice)
    dal = dal_forzato or lc.testo_di(cfg.get('required_from')).strip().strip('"\'')
    stats = {'attivo': False, 'dal': dal or None}
    if not forza:
        if cfg.get('enabled') is not True:
            return [], stats, ['[%s] spento (design_traceability.enabled non e\' true)' % CHECK]
        if not ISO.match(dal):
            return [], stats, ['[%s] spento: design_traceability.required_from assente o non AAAA-MM-GG' % CHECK]
        w1 = report_w1(radice, lc.testo_di(cfg.get('report_w1')) or DEFAULT['report_w1'])
        if not w1:
            return [], stats, ['[%s] no-op: nessun report W1 con frontmatter date/n/ok_chat_rate (%s)'
                               % (CHECK, cfg.get('report_w1'))]
        if dal <= w1[0]:
            return [], stats, ['[%s] no-op: required_from %s non e\' successivo al report W1 del %s (%s)'
                               % (CHECK, dal, w1[0], w1[1])]
        stats['report_w1'] = w1[1]
    stats['attivo'] = True
    dal = dal if ISO.match(dal) else '0000-00-00'
    arts = lc.raccogli_kanban(radice)
    us_ids = {a.id for a in arts if a.tipo == 'US'}
    adrs = raccogli_adr(radice)
    adr_ids = set().union(*(a['ids'] for a in adrs)) if adrs else set()
    findings = []
    adr_scope = [a for a in adrs if _data(a['fm'], 'created', 'date') >= dal]
    tsk_scope = [a for a in arts if a.tipo == 'TSK' and _data(a.fm, 'created') >= dal]
    for a in adr_scope:
        fm = a['fm']
        sat = US_ID.findall(lc.testo_di(fm.get('satisfies')))
        if lc.testo_di(fm.get('status')).strip().lower() == 'accepted' and not sat:
            findings.append(lc.finding('WARNING', 'adr-senza-satisfies', CHECK,
                '%s (accepted): manca `satisfies: [US-…]`' % a['id'], path=a['rel']))
        if (cfg.get('premortem_pre_tpm') is True and lc.testo_di(fm.get('status')).strip().lower() == 'accepted'
                and not premortem_valido(fm)):
            findings.append(lc.finding('WARNING', 'adr-senza-premortem', CHECK,
                '%s (accepted): manca `premortem: {data, report, esito}` valido' % a['id'], path=a['rel']))
        for u in sat:
            if u not in us_ids:
                findings.append(lc.finding('WARNING', 'unknown-ref', CHECK,
                    '%s: satisfies cita %s, che non esiste nel kanban' % (a['id'], u), path=a['rel']))
        for x in ADR_ID.findall(lc.testo_di(fm.get('supersedes'))):
            if x not in adr_ids:
                findings.append(lc.finding('WARNING', 'unknown-ref', CHECK,
                    '%s: supersedes cita %s, che non esiste' % (a['id'], x), path=a['rel']))
    con_refs = 0
    for t in tsk_scope:
        refs = ADR_ID.findall(lc.testo_di(t.fm.get('decision_refs')))
        con_refs += bool(refs)
        for x in refs:
            if x not in adr_ids:
                findings.append(lc.finding('WARNING', 'unknown-ref', CHECK,
                    '%s: decision_refs cita %s, che non esiste' % (t.id, x), path=t.rel))
        if lc.testo_di(t.fm.get('status')).strip() == 'done':
            m = CHIUSURA.search(t.testo)
            if not m or not AC_ID.search(m.group(1)):
                findings.append(lc.finding('WARNING', 'chiusura-senza-ac', CHECK,
                    '%s (done): la tabella `## Chiusura` non cita alcun AC della US' % t.id, path=t.rel))
    perimetro = len(adr_scope) + len(tsk_scope)
    stats.update({'adr_nel_perimetro': len(adr_scope), 'tsk_nel_perimetro': len(tsk_scope),
                  'tsk_con_decision_refs': con_refs, 'finding': len(findings)})
    diag = []
    oggi = oggi or dt.date.today().isoformat()
    if (not forza and tsk_scope and con_refs == 0
            and (dt.date.fromisoformat(oggi) - dt.date.fromisoformat(dal)).days >= DISMISSIONE_GIORNI):
        findings.append(lc.finding('INFO', 'decision-refs-vuoto', CHECK,
            'nessuno dei %d TSK creati dal %s usa decision_refs: criterio di dismissione del campo raggiunto '
            '(Accordo D1, decide il maintainer)' % (len(tsk_scope), dal)))
    soglia = float(lc.testo_di(cfg.get('soglia_spegnimento')) or DEFAULT['soglia_spegnimento'])
    avvisi = [f for f in findings if f['sev'] == 'WARNING']
    if not forza and perimetro and len(avvisi) / perimetro > soglia:
        diag.append('[%s] SOSPESO: %d finding su %d artefatti nel perimetro (%.0f%% > soglia %.0f%%). '
                    'Il check non segnala finche\' la quota non scende o la soglia non cambia '
                    '(design_traceability.soglia_spegnimento).'
                    % (CHECK, len(avvisi), perimetro, 100 * len(avvisi) / perimetro, 100 * soglia))
        stats['sospeso'] = True
        return [], stats, diag
    if not findings:
        diag.append('[%s] OK — %d ADR e %d TSK dal %s, tutti tracciati (solo forma: link esistenti, non pertinenti)'
                    % (CHECK, len(adr_scope), len(tsk_scope), dal))
    return findings, stats, diag


def main(argv=None):
    ap = lc.parser(__doc__)
    ap.add_argument('--forza', action='store_true', help='misura ignorando enabled, report W1 e soglia')
    ap.add_argument('--dal', help='con --forza: sovrascrive required_from (AAAA-MM-GG)')
    ap.add_argument('--oggi', help='data di riferimento (AAAA-MM-GG) per il criterio di dismissione')
    args = ap.parse_args(argv)
    args.root = os.path.abspath(args.root)
    findings, stats, diag = verifica(args.root, args.forza, args.oggi, args.dal if args.forza else None)
    return lc.emetti(args, CHECK, findings, diag, stats)


if __name__ == '__main__':
    sys.exit(main())

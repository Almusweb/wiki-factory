#!/usr/bin/env python3
"""Check 4bm — il `model:` di ogni agente e' coerente con il registro dei modelli.

Il registro e' `models:` in factory.config.yaml: `routing` (tier -> model id) e `overrides`
(agente -> model id oppure nome di tier). Gli agenti NON dichiarano un `tier:` (verificato
2026-11-16: 0 agenti su 43), quindi il tier naturale di un agente non e' derivabile. Il check
verifica le due cose che il registro permette di verificare:

- MODEL_FUORI_REGISTRO (ERROR): un `model:` che non e' nessuno dei modelli di `routing` ne' di
  `overrides`. E' il caso di un ID rimasto alla generazione precedente dopo un cambio di registro.
- OVERRIDE_DISATTESO (ERROR): un agente elencato in `overrides` il cui `model:` non e' l'override
  risolto (un nome di tier si risolve con `routing`).
- MODEL_ASSENTE (WARNING): agente senza `model:` (eredita il modello della sessione).

Senza blocco `models:` (factory derivate che non lo usano) il check e' un no-op dichiarato.

Non garantisce: che il tier scelto sia quello giusto per l'agente (manca la dichiarazione);
che il registro stesso punti ai modelli correnti; il modello effettivo a runtime (un override
di sessione o del chiamante lo scavalca).

Uso:
    python3 tools/lint/check-model-tier.py [--root <factory>] [--json] [--strict]
Exit code: 0 anche con finding; con --strict 1 se c'e' almeno un ERROR.
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lint_comune as lc  # noqa: E402

CHECK = '4bm'
_TOP = re.compile(r'^([A-Za-z_][\w.-]*):')
_SUB = re.compile(r'^  ([A-Za-z_][\w-]*):\s*(.*)$')
_VOCE = re.compile(r'^    ([A-Za-z_][\w.-]*):\s*([^\s#]+)')


def leggi_registro(radice):
    """(routing, overrides) dal blocco `models:` di factory.config.yaml; None se il blocco manca."""
    path = os.path.join(radice, 'factory.config.yaml')
    if not os.path.isfile(path):
        return None
    routing, overrides = {}, {}
    dentro, sezione, trovato = False, None, False
    for riga in lc.leggi(path).splitlines():
        if _TOP.match(riga):
            dentro = riga.startswith('models:')
            trovato = trovato or dentro
            sezione = None
            continue
        if not dentro or not riga.strip() or riga.lstrip().startswith('#'):
            continue
        sub = _SUB.match(riga)
        if sub:
            sezione = sub.group(1)
            continue
        voce = _VOCE.match(riga)
        if voce and sezione in ('routing', 'overrides'):
            (routing if sezione == 'routing' else overrides)[voce.group(1)] = voce.group(2).strip('"\'')
    return (routing, overrides) if trovato else None


def risolvi(valore, routing):
    """Un override puo' nominare un tier (`tier_fast`) o un model id."""
    return routing.get(valore, valore)


def verifica(radice):
    registro = leggi_registro(radice)
    stats = {'attivo': registro is not None, 'agenti': 0}
    if registro is None:
        return [], stats
    routing, overrides = registro
    ammessi = set(routing.values()) | {risolvi(v, routing) for v in overrides.values()}
    findings = []
    cartella = os.path.join(radice, '.claude', 'agents')
    nomi = sorted(f for f in os.listdir(cartella) if f.endswith('.md')) if os.path.isdir(cartella) else []
    for nome in nomi:
        rel = os.path.join('.claude', 'agents', nome)
        fm = lc.frontmatter(os.path.join(radice, rel)) or {}
        agente = lc.testo_di(fm.get('name')) or nome[:-3]
        model = lc.testo_di(fm.get('model')).strip()
        stats['agenti'] += 1
        if not model:
            findings.append(lc.finding('WARNING', 'MODEL_ASSENTE', CHECK,
                                       '%s: nessun `model:` nel frontmatter (eredita il modello della sessione)' % agente,
                                       path=rel))
            continue
        if agente in overrides:
            atteso = risolvi(overrides[agente], routing)
            if model != atteso:
                findings.append(lc.finding('ERROR', 'OVERRIDE_DISATTESO', CHECK,
                                           '%s: `model: %s` ma models.overrides dice %s' % (agente, model, atteso),
                                           path=rel))
            continue
        if model not in ammessi:
            findings.append(lc.finding('ERROR', 'MODEL_FUORI_REGISTRO', CHECK,
                                       '%s: `model: %s` non e\' nel registro (models.routing: %s)' % (
                                           agente, model, ', '.join(sorted(set(routing.values())))),
                                       path=rel))
    return findings, stats


def main(argv=None):
    args = lc.parser(__doc__).parse_args(argv)
    args.root = os.path.abspath(args.root)
    findings, stats = verifica(args.root)
    diag = []
    if not stats['attivo']:
        diag.append('[%s] nessun blocco models: in factory.config.yaml, check non applicabile' % CHECK)
    elif not findings:
        diag.append('[%s] OK — %d agenti, model: coerente con il registro dei modelli' % (CHECK, stats['agenti']))
    return lc.emetti(args, CHECK, findings, diag, stats)


if __name__ == '__main__':
    sys.exit(main())

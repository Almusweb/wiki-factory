#!/usr/bin/env python3
"""Config dei controlli di sicurezza letta da un'ancora fissa, mai dal working tree (EP-109 CQRL iter-1).

Un controllo che legge `ref_protetto` (o il path di un ruleset) dal `factory.config.yaml` su disco si
lascia spegnere da una modifica non committata: con `ref_protetto: HEAD` il merge-base diventa HEAD e pin,
accettazioni e ruleset vengono dal branch in esame. Qui la config si legge cosi':

  1. `ref_protetto` del blocco, letto dal `factory.config.yaml` dell'ANCORA (`origin/main` di default, non
     configurabile dal working tree);
  2. merge-base fra HEAD e quel ref;
  3. il blocco intero dal `factory.config.yaml` di quel merge-base.

Un ref che non si risolve, o un file assente all'ancora, da' `None` con la spiegazione: il chiamante
risponde NON_VERIFICABILE. `null`, `~` e il valore vuoto valgono come chiave assente.

Cosa NON garantisce: chi scrive sull'ancora decide la config; un clone senza `origin/main` (o con un
`origin/main` locale manomesso) non ha ancora affidabile, e lo si dichiara come NON_VERIFICABILE.
"""
from __future__ import annotations

import re
import subprocess

ANCORA_DEFAULT = "origin/main"
_NULLI = ("", "null", "~", "Null", "NULL")


def _git(root, *args):
    try:
        r = subprocess.run(["git", "-C", str(root)] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError:
        return None, b""
    return r.returncode, r.stdout


def blocco_da_testo(testo, nome):
    """Dict {chiave: valore} delle chiavi scalari del blocco top-level `nome`; i nulli sono omessi."""
    out = {}
    in_blocco = False
    for line in testo.splitlines():
        if re.match(r"^%s:\s*(#.*)?$" % re.escape(nome), line):
            in_blocco = True
            continue
        if in_blocco:
            if line.strip() and not line.startswith((" ", "\t", "#")):
                break
            m = re.match(r"^\s+([A-Za-z_]+):\s*[\"']?([^\"'#\s]*)", line)
            if m and m.group(2) not in _NULLI:
                out[m.group(1)] = m.group(2)
    return out


def config_al(root, rev):
    """Testo di factory.config.yaml a `rev`, o None."""
    rc, out = _git(root, "show", "%s:factory.config.yaml" % rev)
    return out.decode("utf-8", "replace") if rc == 0 else None


def merge_base(root, ref):
    rc, out = _git(root, "merge-base", "HEAD", ref)
    return out.decode("ascii", "replace").strip() if rc == 0 and out.strip() else None


def blocco(root, nome, ancora=ANCORA_DEFAULT, ref_default=ANCORA_DEFAULT):
    """(blocco, ref_protetto, merge_base, spiegazione). blocco None = non verificabile.

    Il blocco assente all'ancora non e' un errore: vale `{}` (default del chiamante), ma il ref e il
    merge-base restano quelli dell'ancora."""
    rc, _ = _git(root, "rev-parse", "--verify", ancora + "^{commit}")
    if rc != 0:
        return None, None, None, "ancora %s: ref non risolto, config non leggibile in modo affidabile" % ancora
    testo_ancora = config_al(root, ancora)
    ref = blocco_da_testo(testo_ancora or "", nome).get("ref_protetto") or ref_default
    mb = merge_base(root, ref)
    if not mb:
        return None, ref, None, "ref protetto %s (letto all'ancora %s) non risolto da HEAD" % (ref, ancora)
    testo_mb = config_al(root, mb)
    return blocco_da_testo(testo_mb or "", nome), ref, mb, (
        "config del blocco %s letta al merge-base %s con %s" % (nome, mb[:8], ref))

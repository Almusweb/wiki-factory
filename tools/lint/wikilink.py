"""Parser dei wikilink condiviso fra Check 1 e il produttore del grafo della conoscenza.

Un punto solo per le regole di lettura, cosi' il lint e il grafo non possono divergere su
cosa e' un link:
- `[[target]]`; `|alias` e `#ancora` ignorati;
- il codice non contiene link: blocchi ``` e codice fra backtick tolti prima dell'analisi
  (`new Map([['k', 'v']])` in un esempio JS e la sintassi `[[name]]` citata non sono link);
- un target si risolve per path relativo a `wiki/` oppure per slug (nome del file).

Non garantisce: che il target dica cio' che il link lascia intendere (solo che il file esiste),
ne' la lettura di link non-wiki (`[testo](path.md)`, che Check 1 legge per conto suo).

Solo stdlib. Nessuna scrittura.
"""
from __future__ import annotations

import os
import re

WIKILINK = re.compile(r'\[\[([^\]]+)\]\]')


def senza_codice(testo):
    """Il codice non contiene wikilink: blocchi ``` e codice fra backtick tolti prima dell'analisi."""
    testo = re.sub(r'```.*?```', '', testo, flags=re.S)
    return re.sub(r'`[^`\n]*`', '', testo)


def estrai(testo):
    """Target grezzi (contenuto fra `[[` e `]]`) dei wikilink fuori dal codice, nell'ordine del testo."""
    return [m.group(1) for m in WIKILINK.finditer(senza_codice(testo))]


def destinazione(grezzo):
    """Target senza `|alias` e `#ancora`, in minuscolo e senza spazi ai bordi."""
    return grezzo.split('|')[0].split('#')[0].strip().lower()


class Risolutore:
    """Risolve un wikilink su un elenco di file wiki (path relativi alla radice, con `/`).

    Chiamato con il contenuto grezzo di un link ritorna il path del file, `None` se il target non
    esiste, `''` se il target e' vuoto (un link vuoto non e' rotto: Check 1 lo ha sempre trattato cosi')."""

    def __init__(self, files):
        self.per_rel = {p[len('wiki/'):-3].lower(): p for p in files}
        self.per_slug = {}
        for p in files:
            self.per_slug.setdefault(os.path.basename(p)[:-3].lower(), p)

    @property
    def slugs(self):
        return sorted(self.per_slug)

    def __call__(self, grezzo):
        t = destinazione(grezzo)
        if not t:
            return ''
        if t.startswith('wiki/'):
            t = t[len('wiki/'):]
        if t.endswith('.md'):
            t = t[:-3]
        return self.per_rel.get(t) or self.per_slug.get(os.path.basename(t))

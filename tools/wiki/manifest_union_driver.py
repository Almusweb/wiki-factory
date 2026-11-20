#!/usr/bin/env python3
"""manifest_union_driver.py — merge driver `factory-manifest-union` per raw/.extraction-manifest.json.

Il manifest e' un oggetto JSON {chiave: valore}. Due branch che aggiungono chiavi diverse in coda
confliggono sempre in testo; per chiave non c'e' nessun conflitto reale.

Regola per ogni chiave, confrontando base (%O), nostro (%A) e loro (%B); l'assenza e' un valore:
  - uguale nei due lati            -> quel valore
  - cambiato solo da un lato       -> il valore cambiato
  - cambiato da entrambi in modo diverso -> CONFLITTO: il driver non scrive nulla, exit 1
    (git lascia il file in conflitto all'operatore).
Ordine delle chiavi: quelle di %A com'erano, poi quelle nuove di %B nel loro ordine.
Serializzazione identica a tools/session/session_doc.py:
    json.dumps(manifest, indent=2, ensure_ascii=False) + "\\n"
Se uno dei tre file non e' JSON oggetto valido: exit 1 senza scrivere. Una base vuota
(file assente nella base) vale {}.

Configurazione (registrata da tools/vcs/install_factory_hooks.py):
    python3 tools/wiki/manifest_union_driver.py %O %A %B

Solo stdlib.
"""
import json
import sys

ASSENTE = object()


class Conflitto(Exception):
    pass


def _carica(testo: str) -> dict:
    if not testo.strip():
        return {}
    dati = json.loads(testo)
    if not isinstance(dati, dict):
        raise ValueError("il manifest deve essere un oggetto JSON")
    return dati


def merge(base: dict, ours: dict, theirs: dict) -> dict:
    """Dizionario fuso; solleva Conflitto se la stessa chiave cambia in modo diverso."""
    chiavi = list(ours) + [k for k in theirs if k not in ours]
    fuso = {}
    for k in chiavi:
        b = base.get(k, ASSENTE)
        o = ours.get(k, ASSENTE)
        t = theirs.get(k, ASSENTE)
        if o == t:
            scelto = o
        elif o == b:
            scelto = t
        elif t == b:
            scelto = o
        else:
            raise Conflitto(k)
        if scelto is not ASSENTE:
            fuso[k] = scelto
    return fuso


def serializza(dati: dict) -> str:
    return json.dumps(dati, indent=2, ensure_ascii=False) + "\n"


def driver(base_path: str, ours_path: str, theirs_path: str) -> int:
    try:
        testi = []
        for p in (base_path, ours_path, theirs_path):
            with open(p, encoding="utf-8") as f:
                testi.append(_carica(f.read()))
        fuso = merge(*testi)
    except Conflitto as e:
        print(f"manifest_union_driver: la chiave {e.args[0]!r} cambia in modo diverso nei due lati",
              file=sys.stderr)
        return 1
    except ValueError as e:  # include json.JSONDecodeError
        print(f"manifest_union_driver: file non valido: {e}", file=sys.stderr)
        return 1
    with open(ours_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(serializza(fuso))
    return 0


def main(argv):
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    return driver(*argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

"""Interfaccia minima che la pila di /security-scan chiede al modulo dei segreti.

La pila (sca_guard, oracolo_statico, fix_gate, rescan, security_scan) non importa `secrets_guard`
direttamente: passa da qui, e usa solo questi quattro nomi.

    Rifiuto                       eccezione: il path non si puo' scansionare
    guardia_storia(code_path, root) -> None se il path si puo' scansionare, altrimenti il motivo (str)
    scan_storia(code_path, root)  -> esito con .stato, .messaggio, .findings; solleva Rifiuto fuori perimetro
    PASS                          valore di .stato quando la storia e' pulita

I nomi si risolvono a ogni accesso dal modulo `secrets_guard` sul path di import, quindi:

- `Rifiuto` e' la stessa classe che il modulo solleva, e gli `except` la catturano;
- una factory con un proprio `secrets_guard.py` adotta la pila esponendo questi quattro nomi
  (anche come alias verso le proprie funzioni), senza prendere il modulo del master.

Un nome mancante produce un AttributeError che dice quale nome dell'interfaccia manca."""
from __future__ import annotations

import importlib

MODULO = "secrets_guard"
INTERFACCIA = ("Rifiuto", "guardia_storia", "scan_storia", "PASS")


def modulo():
    return importlib.import_module(MODULO)


def mancanti(mod=None):
    """Nomi dell'interfaccia che il modulo dei segreti non espone (lista vuota: contratto soddisfatto)."""
    mod = mod if mod is not None else modulo()
    return [n for n in INTERFACCIA if not hasattr(mod, n)]


def __getattr__(nome):
    if nome not in INTERFACCIA:
        raise AttributeError("module %r has no attribute %r" % (__name__, nome))
    mod = modulo()
    try:
        return getattr(mod, nome)
    except AttributeError:
        raise AttributeError("il modulo dei segreti %r non espone %r, richiesto dall'interfaccia della pila "
                             "di /security-scan (%s)" % (MODULO, nome, ", ".join(INTERFACCIA)))

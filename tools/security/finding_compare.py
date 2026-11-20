#!/usr/bin/env python3
"""Comparatore dei finding di sicurezza per identita' (EP-109 US-428, TSK-1043; accordi A6, A13, A17).

Confronta due esecuzioni dello stesso scanner (PRIMA e DOPO) e dice, finding per finding, cosa e'
successo. Non conta: un finding che sparisce non e' un rischio risolto finche' la sparizione non e'
una delle due chiusure legittime. Nessun contatore «N risolti» nell'output (US-428 AC4).

Identita' del finding (A17):
    SCA   (tool, regola, pacchetto@versione)   -- appaiati per (tool, regola, pacchetto): la stessa
                                                  regola sullo stesso pacchetto a un'altra versione e'
                                                  lo stesso rischio che persiste, non uno nuovo
    SAST  (tool, regola, path, simbolo)        -- niente numero di riga: si sposta a ogni modifica

Chiusure legittime, solo due:
    chiuso_simbolo_presente   SAST: il finding non c'e' piu', il file e il simbolo ci sono ancora
    chiuso_versione_fixed     SCA: il pacchetto e' a una versione che il DB marca fixed per quella
                              regola (lo dice l'oracolo in `esiti_db`, che conosce la semantica delle
                              versioni dell'ecosistema)

Ogni altra sparizione e' NON_VERIFICABILE, con motivo:
    cancellato, spostato, vendorizzato     il file del finding non c'e' piu' (spostato/vendorizzato:
                                           lo stesso blob compare a un altro path, sotto un prefisso
                                           di vendoring o no)
    simbolo_assente                        file presente, simbolo no (refactor o elusione: decide un umano)
    simbolo_non_dichiarato                 finding SAST senza simbolo: col file presente non si distingue
                                           il fix dalla riga cancellata (CQRL iter-1), quindi niente chiusura
    pacchetto_rimosso                      pacchetto sparito dall'inventario (rimosso o vendorizzato)
    versione_ignota_db                     nuova versione sconosciuta al DB (anche un downgrade)
    versione_non_fixed                     nuova versione nota ma non marcata fixed per quella regola
    sparito_a_versione_invariata           stesso pacchetto, stessa versione, finding sparito
                                           (soppressione o config: il diff-check e' TSK-1044)

Esito complessivo:
    FAIL               almeno un finding nuovo
    NON_VERIFICABILE   nessun nuovo ma almeno una sparizione non legittima, oppure esecuzioni non
                       confrontabili (tool, versione del tool o db_id diversi: A13, il DB cambiato a
                       commit fermo e' un evento di riscansione, non una decisione sul fix), oppure
                       esecuzione malformata
    PASS               nessun nuovo e ogni sparizione e' una chiusura legittima. Non dice che il codice
                       sia sicuro: dice che, con questo tool e questo DB, non c'e' nulla di nuovo

Contratto d'ingresso (un file JSON per esecuzione; lo producono gli oracoli, a partire da TSK-1038):
    {
      "tool": "osv-scanner", "tool_version": "1.9.2", "db_id": "<id o hash del DB / del ruleset>",
      "commit": "<sha>",
      "findings": [ {"rule_id": "GHSA-...", "package": "lodash", "version": "4.17.20"},
                    {"rule_id": "python.lang.x", "path": "app/db.py", "symbol": "query"} ],
      "inventario": {"lodash": "4.17.21"},                        # SCA: pacchetto -> versione
      "esiti_db": {"lodash@4.17.21": {"noto": true, "fixed_per": ["GHSA-..."]}},   # SCA
      "file_presenti": {"app/db.py": "<blob sha>"},               # SAST: path -> blob
      "simboli_presenti": ["app/db.py::query"]                    # SAST
    }
Le sezioni SCA servono nell'esecuzione DOPO; `file_presenti` serve in entrambe (lo spostamento si
riconosce dal blob di PRIMA). Il finding e' SCA se ha `package`, SAST se ha `path`.

Cosa NON garantisce: l'identita' SCA non porta ecosistema ne' lockfile e `inventario` tiene una sola
versione per nome: un pacchetto presente a piu' versioni, o con lo stesso nome in due ecosistemi, non e'
rappresentabile, e l'oracolo che produce l'esecuzione (TSK-1038) deve dare NON_VERIFICABILE in quel caso
invece di scegliere una versione; non distingue un refactor legittimo che rimuove il codice vulnerabile da una
cancellazione elusiva (entrambi a review umana); uno spostamento con modifiche non e' riconosciuto come
spostamento (risulta cancellato, sempre NON_VERIFICABILE); la correttezza di `esiti_db` e dei simboli e'
dell'oracolo che li produce.

CLI: finding_compare.py PRIMA.json DOPO.json [--json] [--vendor PREFISSO ...]
     exit 0 PASS, 1 FAIL, 3 NON_VERIFICABILE, 2 uso errato
"""
from __future__ import annotations

import argparse
import json
import sys

PASS = "PASS"
FAIL = "FAIL"
NON_VERIFICABILE = "NON_VERIFICABILE"
EXIT_CODES = {PASS: 0, FAIL: 1, NON_VERIFICABILE: 3}

PERSISTENTE = "persistente"
NUOVO = "nuovo"
CHIUSO_SIMBOLO = "chiuso_simbolo_presente"
CHIUSO_FIXED = "chiuso_versione_fixed"
NV = "non_verificabile"

CANCELLATO = "cancellato"
SPOSTATO = "spostato"
VENDORIZZATO = "vendorizzato"
SIMBOLO_ASSENTE = "simbolo_assente"
PACCHETTO_RIMOSSO = "pacchetto_rimosso"
VERSIONE_IGNOTA = "versione_ignota_db"
VERSIONE_NON_FIXED = "versione_non_fixed"
SPARITO_INVARIATO = "sparito_a_versione_invariata"
SIMBOLO_NON_DICHIARATO = "simbolo_non_dichiarato"

VENDOR_DEFAULT = ("vendor/", "third_party/", "node_modules/", "external/")

CAMPI_ESECUZIONE = ("tool", "tool_version", "db_id")


class EsecuzioneNonValida(ValueError):
    pass


def _str(v):
    return isinstance(v, str) and v.strip() != ""


def valida(esec, nome):
    """Solleva EsecuzioneNonValida se l'esecuzione non rispetta il contratto."""
    if not isinstance(esec, dict):
        raise EsecuzioneNonValida("%s: non e' un oggetto JSON" % nome)
    for c in CAMPI_ESECUZIONE:
        if not _str(esec.get(c)):
            raise EsecuzioneNonValida("%s: campo %s mancante o vuoto (A13: senza id del DB nessun "
                                      "confronto)" % (nome, c))
    fs = esec.get("findings")
    if not isinstance(fs, list):
        raise EsecuzioneNonValida("%s: findings non e' una lista" % nome)
    # sezioni facoltative, ma se ci sono hanno il tipo del contratto: un valore malformato non deve
    # diventare una chiusura (es. noto: "false" vero per truthiness, fixed_per stringa = sottostringa)
    def _dict_str(campo):
        v = esec.get(campo)
        if v is not None and not (isinstance(v, dict) and all(isinstance(k, str) and isinstance(x, str)
                                                               for k, x in v.items())):
            raise EsecuzioneNonValida("%s: %s deve essere un oggetto {stringa: stringa}" % (nome, campo))
    _dict_str("inventario")
    _dict_str("file_presenti")
    sp = esec.get("simboli_presenti")
    if sp is not None and not (isinstance(sp, list) and all(isinstance(x, str) for x in sp)):
        raise EsecuzioneNonValida("%s: simboli_presenti deve essere una lista di stringhe" % nome)
    ed = esec.get("esiti_db")
    if ed is not None:
        if not isinstance(ed, dict):
            raise EsecuzioneNonValida("%s: esiti_db deve essere un oggetto" % nome)
        for k, v in ed.items():
            if not (isinstance(v, dict) and isinstance(v.get("noto"), bool)
                    and isinstance(v.get("fixed_per", []), list)
                    and all(isinstance(x, str) for x in v.get("fixed_per", []))):
                raise EsecuzioneNonValida("%s: esiti_db[%s] vuole noto booleano e fixed_per lista di "
                                          "stringhe" % (nome, k))
    for i, f in enumerate(fs):
        if not isinstance(f, dict) or not _str(f.get("rule_id")):
            raise EsecuzioneNonValida("%s: finding %d senza rule_id" % (nome, i))
        sca, sast = "package" in f, "path" in f
        if sca == sast:
            raise EsecuzioneNonValida("%s: finding %d deve avere package (SCA) oppure path (SAST)" % (nome, i))
        if sca and not (_str(f.get("package")) and _str(f.get("version"))):
            raise EsecuzioneNonValida("%s: finding %d SCA senza package o version" % (nome, i))
        if sast and not _str(f.get("path")):
            raise EsecuzioneNonValida("%s: finding %d SAST senza path" % (nome, i))


def identita(tool, f):
    """Identita' del finding come in A17 (tupla, ordinabile)."""
    if "package" in f:
        return (tool, f["rule_id"], "%s@%s" % (f["package"], f["version"]))
    return (tool, f["rule_id"], "%s::%s" % (f["path"], f.get("symbol") or ""))


def _chiave_appaiamento(f):
    if "package" in f:
        return ("sca", f["rule_id"], f["package"])
    return ("sast", f["rule_id"], f["path"], f.get("symbol") or "")


def _voce(tool, f, esito, motivo=None, dettaglio="", dopo=None):
    v = {"identita": list(identita(tool, f)), "esito": esito}
    if motivo:
        v["motivo"] = motivo
    if dettaglio:
        v["dettaglio"] = dettaglio
    if dopo is not None:
        v["identita_dopo"] = list(identita(tool, dopo))
    return v


def _sparizione_sast(tool, f, prima, dopo, vendor):
    path, simbolo = f["path"], f.get("symbol") or ""
    file_dopo = dopo.get("file_presenti") or {}
    if path in file_dopo:
        if simbolo == "":
            return _voce(tool, f, NV, SIMBOLO_NON_DICHIARATO,
                         "finding senza simbolo: con %s presente il fix non si distingue da una cancellazione" % path)
        if ("%s::%s" % (path, simbolo)) in set(dopo.get("simboli_presenti") or []):
            return _voce(tool, f, CHIUSO_SIMBOLO, dettaglio="file e simbolo presenti, finding assente")
        return _voce(tool, f, NV, SIMBOLO_ASSENTE,
                     "il file c'e', il simbolo %s no: refactor o elusione, decide un umano" % simbolo)
    blob = (prima.get("file_presenti") or {}).get(path)
    if blob:
        altrove = sorted(p for p, b in file_dopo.items() if b == blob and p != path)
        if altrove:
            dest = altrove[0]
            if dest.startswith(tuple(vendor)):
                return _voce(tool, f, NV, VENDORIZZATO, "stesso contenuto ora in %s" % dest)
            return _voce(tool, f, NV, SPOSTATO, "stesso contenuto ora in %s" % dest)
    return _voce(tool, f, NV, CANCELLATO, "%s non c'e' piu'" % path)


def _sparizione_sca(tool, f, dopo):
    pkg, ver, regola = f["package"], f["version"], f["rule_id"]
    inventario = dopo.get("inventario") or {}
    if pkg not in inventario:
        return _voce(tool, f, NV, PACCHETTO_RIMOSSO,
                     "%s non e' piu' nell'inventario: rimosso o vendorizzato" % pkg)
    nuova = inventario[pkg]
    if nuova == ver:
        return _voce(tool, f, NV, SPARITO_INVARIATO,
                     "%s resta a %s ma il finding non c'e' piu'" % (pkg, ver))
    esito_db = (dopo.get("esiti_db") or {}).get("%s@%s" % (pkg, nuova)) or {}
    if not esito_db.get("noto"):
        return _voce(tool, f, NV, VERSIONE_IGNOTA, "%s@%s sconosciuta al DB %s" % (pkg, nuova, dopo["db_id"]))
    if regola in (esito_db.get("fixed_per") or []):
        return _voce(tool, f, CHIUSO_FIXED, dettaglio="%s@%s marcata fixed per %s dal DB %s"
                     % (pkg, nuova, regola, dopo["db_id"]))
    return _voce(tool, f, NV, VERSIONE_NON_FIXED,
                 "%s@%s nota al DB ma non marcata fixed per %s" % (pkg, nuova, regola))


def confronta(prima, dopo, vendor=VENDOR_DEFAULT):
    """Dict con `esito`, `motivo` e `voci` (una per identita'). Nessun conteggio di chiusure."""
    try:
        valida(prima, "PRIMA")
        valida(dopo, "DOPO")
    except EsecuzioneNonValida as e:
        return {"esito": NON_VERIFICABILE, "motivo": "esecuzione_non_valida", "dettaglio": str(e), "voci": []}
    diversi = [c for c in CAMPI_ESECUZIONE if prima[c] != dopo[c]]
    if diversi:
        riscansione = diversi == ["db_id"] and prima.get("commit") and prima.get("commit") == dopo.get("commit")
        return {"esito": NON_VERIFICABILE,
                "motivo": "riscansione" if riscansione else "non_confrontabili",
                "dettaglio": ("stesso commit, DB diverso: evento di riscansione, non una decisione sul fix (A13)"
                              if riscansione else "campi diversi fra le esecuzioni: %s" % ", ".join(diversi)),
                "voci": []}
    tool = prima["tool"]
    dopo_per_chiave = {}
    for f in dopo["findings"]:
        dopo_per_chiave.setdefault(_chiave_appaiamento(f), []).append(f)
    usati = set()
    voci = []
    # appaiamento uno a uno: prima l'identita' esatta, poi la stessa chiave a un'altra versione
    for f in sorted(prima["findings"], key=lambda x: 0 if any(
            identita(tool, g) == identita(tool, x) for g in dopo_per_chiave.get(_chiave_appaiamento(x), [])) else 1):
        liberi = [g for g in dopo_per_chiave.get(_chiave_appaiamento(f), []) if id(g) not in usati]
        esatti = [g for g in liberi if identita(tool, g) == identita(tool, f)]
        g = (esatti or liberi or [None])[0]
        if g is not None:
            usati.add(id(g))
            voci.append(_voce(tool, f, PERSISTENTE, dopo=g if identita(tool, g) != identita(tool, f) else None))
        elif "package" in f:
            voci.append(_sparizione_sca(tool, f, dopo))
        else:
            voci.append(_sparizione_sast(tool, f, prima, dopo, vendor))
    for f in dopo["findings"]:
        if id(f) not in usati:
            voci.append(_voce(tool, f, NUOVO))
    voci.sort(key=lambda v: v["identita"])
    if any(v["esito"] == NUOVO for v in voci):
        esito = FAIL
    elif any(v["esito"] == NV for v in voci):
        esito = NON_VERIFICABILE
    else:
        esito = PASS
    return {"esito": esito, "tool": tool, "tool_version": prima["tool_version"], "db_id": prima["db_id"],
            "commit_prima": prima.get("commit"), "commit_dopo": dopo.get("commit"), "voci": voci}


def testo(rep):
    righe = ["[finding-compare] %s" % rep["esito"]]
    if rep.get("motivo"):
        righe[0] += " (%s): %s" % (rep["motivo"], rep.get("dettaglio", ""))
    else:
        righe[0] += " — %s %s, DB %s" % (rep["tool"], rep["tool_version"], rep["db_id"])
    for v in rep["voci"]:
        r = "  %-24s %s" % (v["esito"] + ("/" + v["motivo"] if v.get("motivo") else ""), " ".join(v["identita"]))
        if v.get("dettaglio"):
            r += " — " + v["dettaglio"]
        righe.append(r)
    return "\n".join(righe)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("prima")
    ap.add_argument("dopo")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--vendor", action="append", help="prefisso di vendoring (ripetibile; default %s)"
                    % ", ".join(VENDOR_DEFAULT))
    a = ap.parse_args(argv)
    try:
        return _main(a)
    except Exception as e:  # un'eccezione non e' un FAIL: nessun confronto e' avvenuto
        print("[finding-compare] NON_VERIFICABILE: errore interno (%s: %s)" % (type(e).__name__, e))
        return EXIT_CODES[NON_VERIFICABILE]


def _main(a):
    esec = []
    for p in (a.prima, a.dopo):
        try:
            with open(p, encoding="utf-8") as fh:
                esec.append(json.load(fh))
        except (OSError, ValueError) as e:
            esec.append({"_errore": str(e)})
    rep = confronta(esec[0], esec[1], tuple(a.vendor) if a.vendor else VENDOR_DEFAULT)
    print(json.dumps(rep, indent=2, ensure_ascii=False) if a.json else testo(rep))
    return EXIT_CODES[rep["esito"]]


if __name__ == "__main__":
    sys.exit(main())

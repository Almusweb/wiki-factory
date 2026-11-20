#!/usr/bin/env python3
"""Riscansione al cambio del DB degli advisory (EP-109 US-432, TSK-1050; accordi A13, A27).

Due delta separati (A13): il commit che cambia lo decide `sca_guard.py` (FAIL possibile); il DB che cambia a
commit fermo e' un **evento di riscansione**, segnalato al maintainer e mai bloccante. Questo modulo fa il
secondo.

Condizione d'avvio (US-432 AC1): lo spike TSK-1037 ha verificato a comando il pinning offline del DB per
osv-scanner (sha256 di `<ecosistema>/all.zip`) e trivy (digest OCI + sha256 di `trivy.db`), con esito
deterministico a DB fisso. Senza quello la storia si sarebbe chiusa come «non costruibile».

Istantanea: scanner identificato (D7), albero di HEAD scritto blob per blob, CycloneDX offline come in
`sca_guard.py`; registra commit, id del DB e insieme dei finding (id dell'advisory, purl). Il riferimento
precedente sta in `security/reports/rescan-<code_path>-<scanner>.json` (ignorato da git, locale alla macchina).

| Rispetto al riferimento          | Esito                 | Exit |
|----------------------------------|-----------------------|------|
| nessun riferimento               | riferimento_creato    | 0    |
| stesso commit, stesso DB, uguale | invariato             | 0    |
| stesso commit, stesso DB, diverso| NON_VERIFICABILE      | 3    |  (non deterministico: il riferimento resta)
| stesso commit, DB diverso        | evento_riscansione    | 0    |  (mai FAIL: AC2)
| commit diverso                   | commit_cambiato       | 0    |  (il delta dal commit e' di sca_guard)

L'evento (`security/reports/rescan-<code_path>-<scanner>-<AAAAMMGG>-<HHMMSS>.evento.json`) elenca per identita' i
finding nuovi e quelli spariti fra i due DB, con l'id dei due DB (AC3), ed e' per il maintainer: nessuna voce
e' accettata o rifiutata qui.

Cosa NON garantisce (A27, testo concordato): «Aggiornamento della conoscenza sulle vulnerabilita': non e' "da
solo" se non per l'identita' del DB dello scanner registrata nel report (versione e hash). Non garantisce
completezza, tempestivita' oltre l'ultimo DB, ne' integrita' della fonte a monte. Nessuna voce di conoscenza e' un
requisito: il requisito nasce da una storia R.14.» In piu': il DB lo aggiorna chi lo scarica, fuori da questo
modulo; il riferimento e' locale (un'altra macchina parte da `riferimento_creato`).

CLI: rescan.py CODE_PATH [--root FACTORY] [--scanner osv-scanner|trivy] [--json]
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config_ancorata as ca  # noqa: E402
import oracolo_statico as ost  # noqa: E402
import sca_guard as sca  # noqa: E402
import scanner_identity as si  # noqa: E402
import contratto_segreti as sg  # noqa: E402

NON_VERIFICABILE = "NON_VERIFICABILE"
CREATO, INVARIATO, EVENTO, COMMIT_CAMBIATO = ("riferimento_creato", "invariato", "evento_riscansione",
                                               "commit_cambiato")
EXIT = {CREATO: 0, INVARIATO: 0, EVENTO: 0, COMMIT_CAMBIATO: 0, NON_VERIFICABILE: 3}
CARTELLA = "security/reports"


def istantanea(code_path, root=".", nome="osv-scanner"):
    """{commit, db, tool, version, finding: [[id, purl], ...]} a HEAD. Solleva sca._NonVerificabile."""
    ident = si.identifica(nome, root)
    if not ident.identificato:
        raise sca._NonVerificabile("binario non identificato: %s" % ident.messaggio)
    cfg, _ref, _mb, spiega = ca.blocco(root, "security_scan")
    if cfg is None:
        raise sca._NonVerificabile(spiega)
    db_dir = sca._db_dir(cfg, sca.SCANNER[nome]["chiave_db"], root)
    db = sca.SCANNER[nome]["db"](db_dir)
    repo = str(Path(code_path).resolve())
    head = ost.rev(repo, "HEAD")
    if not head:
        raise sca._NonVerificabile("HEAD non risolto in %s" % code_path)
    with tempfile.TemporaryDirectory(prefix="rescan-") as tmp:
        ost._albero(repo, head, os.path.join(tmp, "albero"))
        _inv, finding, _meta = sca._scansiona(nome, ident.realpath, os.path.join(tmp, "albero"), db_dir, tmp)
    if sca.SCANNER[nome]["db"](db_dir)["id"] != db["id"]:
        raise sca._NonVerificabile("il DB e' cambiato durante la scansione")
    return {"commit": head, "db": db["id"], "tool": nome, "version": ident.version,
            "finding": sorted([list(f) for f in finding])}


def _file_stato(root, code_path, nome):
    base = re.sub(r"[^A-Za-z0-9._-]+", "-", Path(code_path).resolve().name) or "code_path"
    return Path(root) / CARTELLA / ("rescan-%s-%s.json" % (base, nome))


def confronta(prec, ora):
    """(esito, evento o None) secondo la tabella del docstring. Funzione pura."""
    if prec is None:
        return CREATO, None
    if prec["commit"] != ora["commit"]:
        return COMMIT_CAMBIATO, None
    a, b = {tuple(f) for f in prec["finding"]}, {tuple(f) for f in ora["finding"]}
    if prec["db"] == ora["db"]:
        return (INVARIATO, None) if a == b else (NON_VERIFICABILE, None)
    evento = {"tipo": EVENTO, "commit": ora["commit"], "tool": ora["tool"], "db_prima": prec["db"],
              "db_dopo": ora["db"], "nuovi": sorted([list(f) for f in b - a]),
              "spariti": sorted([list(f) for f in a - b]),
              "nota": "evento di riscansione a commit fermo: non bloccante, per il maintainer (US-432)"}
    return EVENTO, evento


def esegui(code_path, root=".", nome="osv-scanner"):
    motivo = sg.guardia_storia(code_path, root)
    if motivo:
        raise sg.Rifiuto(motivo)
    try:
        ora = istantanea(code_path, root, nome)
    except (sca._NonVerificabile, ost._NonVerificabile) as e:
        return {"esito": NON_VERIFICABILE, "motivo": str(e)}
    stato = _file_stato(root, code_path, nome)
    try:
        prec = json.loads(stato.read_text(encoding="utf-8")) if stato.exists() else None
    except ValueError:
        return {"esito": NON_VERIFICABILE, "motivo": "riferimento %s illeggibile" % stato}
    esito, evento = confronta(prec, ora)
    rep = {"esito": esito, "commit": ora["commit"], "db": ora["db"], "riferimento": str(stato)}
    if esito == NON_VERIFICABILE:
        rep["motivo"] = ("stesso commit e stesso DB ma finding diversi: la scansione non e' deterministica; "
                         "il riferimento non e' aggiornato")
        return rep
    stato.parent.mkdir(parents=True, exist_ok=True)
    if evento:
        p = stato.with_name(stato.name[:-len(".json")] + "-%s.evento.json"
                            % datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
        p.write_text(json.dumps(evento, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        rep.update({"evento": evento, "file_evento": str(p)})
    stato.write_text(json.dumps(ora, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return rep


def testo(rep):
    r = ["[rescan] %s" % rep["esito"] + (": " + rep["motivo"] if rep.get("motivo") else "")]
    ev = rep.get("evento")
    if ev:
        r.append("  DB %s -> %s, commit %s (non bloccante)" % (ev["db_prima"], ev["db_dopo"], ev["commit"][:12]))
        r += ["  nuovo    %s %s" % tuple(f) for f in ev["nuovi"]]
        r += ["  sparito  %s %s" % tuple(f) for f in ev["spariti"]]
        r.append("  evento per il maintainer: %s" % rep["file_evento"])
    return "\n".join(r)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("code_path")
    ap.add_argument("--root", default=".")
    ap.add_argument("--scanner", choices=sorted(sca.SCANNER), default="osv-scanner")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        rep = esegui(a.code_path, a.root, a.scanner)
    except sg.Rifiuto as e:
        print("[rescan] RIFIUTATO: %s." % e)
        return ost.EXIT_RIFIUTO
    except Exception as e:  # un'eccezione non e' un esito
        print("[rescan] NON_VERIFICABILE: errore interno (%s: %s)" % (type(e).__name__, e))
        return EXIT[NON_VERIFICABILE]
    print(json.dumps(rep, indent=2, ensure_ascii=False) if a.json else testo(rep))
    return EXIT[rep["esito"]]


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Runner di /security-scan (EP-109 US-429, TSK-1045; accordi A1, A10, A11, A22).

Esegue sugli `code_paths[]` del cliente gli oracoli deterministici del layer di sicurezza e scrive un
report consolidato a soli campi enumerati, che e' l'unico input dell'agente interprete (TSK-1046):

    sast      tools/security/sast_guard.py   semgrep, ruleset della factory
    iac       tools/security/iac_guard.py    trivy config, config della factory
    sca       tools/security/sca_guard.py    osv-scanner offline, delta dal baseline
    segreti   tools/security/secrets_guard.py --storia   gitleaks sulla storia git

Opt-in: `security_scan.enabled` (default false) letto dall'ANCORA (config_ancorata), non dal
factory.config.yaml su disco. A flag spento il runner lo dice ed esce 3: nessuna verifica e' avvenuta, e un
exit 0 sarebbe letto come «tutto a posto».

Esito complessivo: FAIL se un oracolo da' FAIL; altrimenti NON_VERIFICABILE se uno non e' verificabile o e'
rifiutato; altrimenti PASS («con questi binari, regole e DB nessun finding nuovo»), mai «codice sicuro».
Exit: 0 PASS, 1 FAIL, 3 NON_VERIFICABILE o capability spenta.

Input dell'agente interprete: accanto al report, `<...>.agente.json` (per_agente): solo campi enumerati e
validati per formato (id, path, purl, riga, commit, stato, motivo enumerato, CVSS numerico, CWE come `CWE-n`
dai campi strutturati di CycloneDX); un valore fuori formato e' scartato e dichiarato. L'agente legge solo quello.

Report: `security/reports/<code_path>-<AAAAMMGG>-<HHMMSS>.json` (nessun `:` nel nome: il repo si clona anche su
Windows), cartella ignorata da git perche' contiene path e finding del codice del cliente. Campi per voce,
enumerati: identificativo della regola o dell'advisory, path o purl, stato, motivo enumerato; mai testo di
advisory, messaggi dello scanner o contenuto dei file (A11). Le soppressioni compaiono con tipo e path,
non con la riga.

Cosa NON garantisce: che gli oracoli siano eseguiti (un agente con Bash puo' eseguire uno scanner con
un'altra config o non eseguirlo: il confine e' il runner, non il wrapper); che il codice sia sicuro;
l'accettazione di un rischio, che resta un gate umano R.14. Tabella completa: CAPABILITIES.md
§security_scan.

CLI: security_scan.py CODE_PATH [--root FACTORY] [--oracoli sast,iac,sca,segreti] [--json] [--no-report]
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config_ancorata as ca  # noqa: E402

PASS, FAIL, NON_VERIFICABILE = "PASS", "FAIL", "NON_VERIFICABILE"
EXIT_CODES = {PASS: 0, FAIL: 1, NON_VERIFICABILE: 3}
CARTELLA_REPORT = "security/reports"
ORACOLI = ("sast", "iac", "sca", "segreti")


# --- adattatori: ogni oracolo -> {esito, motivo, tool, identita, voci enumerate} ---------------

def _identita(rep):
    i = rep.get("identita") or {}
    return {"stato": i.get("stato"), "version": i.get("version"), "sha256": i.get("sha256")}


def _voci_statiche(rep):
    out = []
    for v in (rep.get("confronto") or {}).get("voci", []):
        ident = v.get("identita") or ["", "", ""]
        out.append({"id": ident[1], "path": ident[2].split("::")[0], "stato": v.get("esito"),
                    "motivo": v.get("motivo")})
    for s in (rep.get("soppressioni") or {}).get("voci", []):
        out.append({"id": "soppressione:" + s["tipo"], "path": s["path"],
                    "stato": "accettata" if s["accettata"] else "soppressione_nuova", "motivo": None})
    return out


def _statico(modulo, attr):
    def esegui(code_path, root):
        import oracolo_statico as ost
        mod = __import__(modulo)
        rep = ost.esegui(getattr(mod, attr), code_path, root)
        return {"esito": rep["esito"], "motivo": rep.get("motivo"), "tool": rep["tool"],
                "identita": _identita(rep), "voci": _voci_statiche(rep)}
    return esegui


def _sca(code_path, root):
    import sca_guard
    rep = sca_guard.esegui(code_path, root, "osv-scanner")
    voci = [{"id": v["id"], "purl": v["purl"], "stato": v["stato"], "motivo": None, "cvss": v.get("cvss"),
             "cwe": v.get("cwe") or []} for v in rep.get("voci", [])]
    return {"esito": rep["esito"], "motivo": rep.get("motivo"), "tool": rep["tool"], "identita": _identita(rep),
            "voci": voci, "db": (rep.get("db") or {}).get("id"), "severita": rep.get("severita")}


def _segreti(code_path, root):
    import contratto_segreti as sg
    e = sg.scan_storia(code_path, root)
    voci = [{"id": f.get("RuleID"), "path": f.get("File"), "riga": f.get("StartLine"), "commit": f.get("Commit"),
             "stato": "segreto_nella_storia", "motivo": None} for f in e.findings]
    return {"esito": e.stato, "motivo": None if e.stato == sg.PASS else e.messaggio, "tool": "gitleaks",
            "identita": {}, "voci": voci}


REGISTRO = {"sast": _statico("sast_guard", "SEMGREP"), "iac": _statico("iac_guard", "TRIVY"),
            "sca": _sca, "segreti": _segreti}


# --- input dell'agente interprete: soli campi enumerati (US-429 AC3, TSK-1046) -----------------

STATI = {"persistente", "nuovo", "chiuso_simbolo_presente", "chiuso_versione_fixed", "non_verificabile",
         "accettata", "soppressione_nuova", "nuovo_dal_commit", "debito_non_nominato", "accettato", "sparito",
         "segreto_nella_storia"}
MOTIVI = {None, "cancellato", "spostato", "vendorizzato", "simbolo_assente", "simbolo_non_dichiarato",
          "pacchetto_rimosso", "versione_ignota_db", "versione_non_fixed", "sparito_a_versione_invariata"}
ESITI = {PASS, FAIL, NON_VERIFICABILE}
_FORMATI = {
    "id": re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,199}$"),
    "path": re.compile(r"^[A-Za-z0-9._/@+ -]{1,300}$"),
    "purl": re.compile(r"^pkg:[a-z0-9.+-]+/[A-Za-z0-9._/@%+:-]{1,250}$"),
    "commit": re.compile(r"^[0-9a-f]{7,64}$"),
}
_CWE = re.compile(r"^CWE-[0-9]{1,5}$")


def _campo(nome, valore):
    """(valore valido, True) o (None, False). Nessuna stringa libera passa: solo i formati sopra."""
    if valore is None:
        return None, True
    if nome in _FORMATI:
        return (valore, True) if isinstance(valore, str) and _FORMATI[nome].match(valore) else (None, False)
    if nome == "stato":
        return (valore, True) if valore in STATI else (None, False)
    if nome == "motivo":
        return (valore, True) if valore in MOTIVI else (None, False)
    if nome == "riga":
        return (valore, True) if isinstance(valore, int) and not isinstance(valore, bool) and valore >= 0 else (None, False)
    if nome == "cvss":
        ok = isinstance(valore, (int, float)) and not isinstance(valore, bool) and 0 <= valore <= 10
        return (float(valore), True) if ok else (None, False)
    if nome == "cwe":
        ok = isinstance(valore, list) and all(isinstance(c, str) and _CWE.match(c) for c in valore)
        return (sorted(valore), True) if ok else (None, False)
    return None, False


def per_agente(rep):
    """Report per l'agente interprete: oracolo, esito, e per voce solo campi enumerati validati. Un valore
    fuori formato si scarta e si dichiara in `campi_scartati`; il motivo libero dell'oracolo non passa (solo
    `non_verificabile: true`). E' l'unico file che l'agente legge."""
    out = {"esito": rep["esito"] if rep.get("esito") in ESITI else NON_VERIFICABILE, "oracoli": []}
    for r in rep.get("oracoli", []):
        o = {"oracolo": r.get("oracolo") if r.get("oracolo") in ORACOLI else None,
             "esito": r.get("esito") if r.get("esito") in ESITI else NON_VERIFICABILE, "voci": []}
        for v in r.get("voci", []):
            voce, scartati = {}, []
            for nome in ("id", "path", "purl", "riga", "commit", "stato", "motivo", "cvss", "cwe"):
                if nome not in v:
                    continue
                valore, ok = _campo(nome, v[nome])
                if ok:
                    if valore is not None:
                        voce[nome] = valore
                else:
                    scartati.append(nome)
            ignoti = sorted(set(v) - {"id", "path", "purl", "riga", "commit", "stato", "motivo", "cvss", "cwe"})
            if scartati or ignoti:
                voce["campi_scartati"] = sorted(scartati + ignoti)
            o["voci"].append(voce)
        out["oracoli"].append(o)
    return out


# --- runner -------------------------------------------------------------------------------------

def abilitato(root):
    """(True|False, spiegazione). `enabled` dall'ancora: un `enabled: true` solo su disco non accende nulla."""
    cfg, _ref, _mb, spiega = ca.blocco(root, "security_scan")
    if cfg is None:
        return False, spiega
    if str(cfg.get("enabled", "")).lower() != "true":
        return False, ("security_scan.enabled non e' true all'ancora (default false): /security-scan e' una "
                       "capability opt-in; nessun oracolo e' stato eseguito, nessuna verifica e' avvenuta")
    return True, spiega


def esegui(code_path, root=".", oracoli=ORACOLI, registro=None):
    registro = registro or REGISTRO
    acceso, spiega = abilitato(root)
    if not acceso:
        return {"esito": NON_VERIFICABILE, "spento": True, "motivo": spiega, "oracoli": []}
    import contratto_segreti as sg
    risultati = []
    for nome in oracoli:
        try:
            r = registro[nome](code_path, root)
        except sg.Rifiuto as e:
            r = {"esito": NON_VERIFICABILE, "motivo": "rifiutato: %s" % e, "voci": []}
        except Exception as e:  # un oracolo che si rompe non e' un PASS ne' un FAIL
            r = {"esito": NON_VERIFICABILE, "motivo": "errore interno (%s: %s)" % (type(e).__name__, e), "voci": []}
        r["oracolo"] = nome
        risultati.append(r)
    esiti = {r["esito"] for r in risultati}
    esito = FAIL if FAIL in esiti else (NON_VERIFICABILE if NON_VERIFICABILE in esiti or not risultati else PASS)
    return {"esito": esito, "spento": False, "code_path": code_path, "oracoli": risultati,
            "data": datetime.datetime.now().strftime("%Y-%m-%d %H%M%S")}


def scrivi_report(rep, root, code_path):
    cartella = Path(root) / CARTELLA_REPORT
    cartella.mkdir(parents=True, exist_ok=True)
    nome = re.sub(r"[^A-Za-z0-9._-]+", "-", Path(code_path).resolve().name) or "code_path"
    base = "%s-%s" % (nome, datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    file_ = cartella / (base + ".json")
    file_.write_text(json.dumps(rep, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (cartella / (base + ".agente.json")).write_text(
        json.dumps(per_agente(rep), indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return file_


def testo(rep):
    if rep.get("spento"):
        return "[security-scan] CAPABILITY SPENTA: %s." % rep["motivo"]
    righe = ["[security-scan] %s su %s" % (rep["esito"], rep["code_path"])]
    for r in rep["oracoli"]:
        righe.append("  %-8s %-16s %s" % (r["oracolo"], r["esito"], r.get("motivo") or "%d voci" % len(r["voci"])))
    righe.append("  PASS non significa «codice sicuro»: vedi CAPABILITIES.md §security_scan, Cosa NON garantisce.")
    return "\n".join(righe)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("code_path")
    ap.add_argument("--root", default=".")
    ap.add_argument("--oracoli", default=",".join(ORACOLI), help="sottoinsieme di %s" % ",".join(ORACOLI))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-report", action="store_true", help="non scrivere il report in security/reports/")
    a = ap.parse_args(argv)
    scelti = [o.strip() for o in a.oracoli.split(",") if o.strip()]
    ignoti = [o for o in scelti if o not in ORACOLI]
    if ignoti:
        ap.error("oracoli sconosciuti: %s (noti: %s)" % (", ".join(ignoti), ", ".join(ORACOLI)))
    try:
        rep = esegui(a.code_path, a.root, scelti)
    except Exception as e:
        print("[security-scan] NON_VERIFICABILE: errore interno (%s: %s)" % (type(e).__name__, e))
        return EXIT_CODES[NON_VERIFICABILE]
    if not rep.get("spento") and not a.no_report:
        rep["report"] = str(scrivi_report(rep, a.root, a.code_path))
    print(json.dumps(rep, indent=2, ensure_ascii=False) if a.json else testo(rep))
    if rep.get("report") and not a.json:
        print("  report: %s" % rep["report"])
    return EXIT_CODES[rep["esito"]]


if __name__ == "__main__":
    sys.exit(main())

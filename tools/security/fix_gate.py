#!/usr/bin/env python3
"""Gate del fix di sicurezza (EP-109 US-431, TSK-1048/1049; accordi A3, A7, A16; decisione D4 = (a)).

Un dev-agent propone il fix di un finding SCA confermato su un branch; questo gate dice, giro per giro, se la
proposta resta nel perimetro e se l'oracolo, rieseguito con lo stesso DB, la conferma. Non applica il fix, non
fa push, non apre ne' mergia PR: il fix resta una proposta per un umano (r.14, r.16).

`verifica`, su `merge-base(ref_protetto)..HEAD` del code_path:
  1. perimetro sul diff (A16, D4 = (a)): solo manifest e lockfile delle dipendenze; un lockfile solo se nello
     stesso diff cambia il suo manifest (il lockfile si rigenera dal manifest con il tool dell'ecosistema).
     Qualunque altro file e' FAIL, e i file che spengono controlli lo dicono per nome: `.semgrepignore`,
     `.trivyignore*`, `.gitleaksignore`, `osv-scanner.toml`, CI, `.claude/`, `security/`, registri;
  2. diff-check sulle soppressioni (`suppression_check.py`): una soppressione nuova e' FAIL (il fix non sopprime);
  3. oracolo SCA rieseguito (`sca_guard.py`, stesso DB): una vulnerabilita' nuova dal commit e' FAIL;
  4. chiusura del finding bersaglio (id dell'advisory + nome del pacchetto), solo legittima (US-428):
     pacchetto ancora nell'inventario a un'altra versione e advisory assente con lo stesso DB = chiuso;
     pacchetto rimosso (o vendorizzato) o versione invariata = NON_VERIFICABILE; advisory ancora presente =
     non chiuso.
Esito: PASS (proposta pronta per la review umana), FAIL, NON_VERIFICABILE, oppure APERTO (nel perimetro, nessun
FAIL, ma il finding non e' chiuso: il loop puo' fare un altro giro).

`ciclo(verifica, passo, max_iterations)`: loop bounded. Si ferma al primo PASS, FAIL o NON_VERIFICABILE, quando
due giri consecutivi danno lo stesso esito APERTO senza nuovi file nel diff (no_progress), o a `max_iterations`
(`security_scan.fix_max_iterations`, default 3) con `loop_exhausted`: gate umano.

Cosa NON garantisce: che il fix non rompa il comportamento (restano i test di qa-dev e il merge umano); che la
nuova versione sia nota al DB (un advisory assente puo' voler dire anche «versione sconosciuta»: osv-scanner non
lo distingue); che il lockfile sia davvero rigenerato dal tool (si verifica che cambi insieme al manifest); cause
strutturali. Un agente con Bash puo' fare cose fuori dal gate: quell'esito non vale come esito del gate.

CLI: fix_gate.py CODE_PATH --finding GHSA-xxxx --pacchetto NOME [--root FACTORY] [--json]
     exit 0 PASS, 1 FAIL, 3 NON_VERIFICABILE, 4 APERTO, 2 rifiutato/uso errato
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config_ancorata as ca  # noqa: E402
import oracolo_statico as ost  # noqa: E402
import sca_guard as sca  # noqa: E402
import contratto_segreti as sg  # noqa: E402
import suppression_check as sc  # noqa: E402

PASS, FAIL, NON_VERIFICABILE, APERTO = "PASS", "FAIL", "NON_VERIFICABILE", "APERTO"
EXIT = {PASS: 0, FAIL: 1, NON_VERIFICABILE: 3, APERTO: 4}
MAX_ITERAZIONI_DEFAULT = 3

# manifest -> lockfile dello stesso ecosistema (D4 = (a): solo dipendenze)
COPPIE = {
    "requirements.txt": None, "requirements.in": "requirements.txt", "pyproject.toml": "poetry.lock",
    "Pipfile": "Pipfile.lock", "setup.cfg": None, "package.json": ("package-lock.json", "yarn.lock",
                                                                    "pnpm-lock.yaml"),
    "go.mod": "go.sum", "Cargo.toml": "Cargo.lock", "Gemfile": "Gemfile.lock", "composer.json": "composer.lock",
    "pom.xml": None, "build.gradle": "gradle.lockfile", "build.gradle.kts": "gradle.lockfile",
}
_REQ = re.compile(r"^requirements[-_.A-Za-z0-9]*\.(txt|in)$")


def _lockfile_di(nome):
    out = set()
    for m, l in COPPIE.items():
        for x in (l if isinstance(l, tuple) else (l,)):
            if x == nome:
                out.add(m)
    return out


VIETATI = ((".semgrepignore", "soppressione"), (".trivyignore", "soppressione"), (".gitleaksignore", "soppressione"),
           ("osv-scanner.toml", "soppressione"), (".github/", "CI"), (".gitlab-ci.yml", "CI"),
           (".claude/", "istruzioni degli agenti"), ("security/", "baseline, pin o accettazioni"),
           ("id-registry", "registro"), ("registry", "registro"), ("factory.config.yaml", "config della factory"))


def _perche_vietato(path):
    base = os.path.basename(path)
    for chiave, perche in VIETATI:
        if path.startswith(chiave) or ("/" + chiave) in ("/" + path) or base.startswith(chiave):
            return perche
    return None


def perimetro(file_toccati):
    """Lista di violazioni [(path, motivo)] per il diff dato (vuota = nel perimetro D4 (a))."""
    nomi = {os.path.basename(p) for p in file_toccati}
    violazioni = []
    for p in sorted(file_toccati):
        base = os.path.basename(p)
        vietato = _perche_vietato(p)
        if vietato:
            violazioni.append((p, "fuori perimetro: %s" % vietato))
        elif base in COPPIE or _REQ.match(base):
            continue
        elif _lockfile_di(base):
            if not (_lockfile_di(base) & nomi):
                violazioni.append((p, "lockfile senza il suo manifest nello stesso diff: si rigenera dal manifest"))
        else:
            violazioni.append((p, "fuori perimetro: nel primo ciclo solo manifest e lockfile (D4 = a)"))
    return violazioni


def file_toccati(repo, ref):
    mb = ost.merge_base(repo, ref)
    if not mb:
        return None, None
    rc, out = ost._git(repo, "-c", "core.quotepath=false", "diff", "--no-renames", "--name-only", "-z", mb, "HEAD")
    if rc != 0:
        return None, mb
    return [p.decode("utf-8", "replace") for p in out.split(b"\0") if p], mb


def _chiusura(rep_sca, finding, pacchetto, purl_prima):
    """Esito della chiusura del finding bersaglio sul report di sca_guard."""
    presenti = [v for v in rep_sca.get("voci", []) if v["id"] == finding and v["stato"] != sca.SPARITO]
    if presenti:
        return APERTO, "l'advisory %s c'e' ancora (%s)" % (finding, ", ".join(v["purl"] for v in presenti))
    ora = [p for p in rep_sca.get("sbom", []) if re.match(r"^pkg:[^/]+/%s@" % re.escape(pacchetto), p)]
    if not ora:
        return NON_VERIFICABILE, ("%s non e' piu' nell'inventario: rimosso o vendorizzato, non e' una chiusura "
                                  "legittima (US-428)" % pacchetto)
    if purl_prima and purl_prima in ora:
        return NON_VERIFICABILE, "%s e' alla stessa versione: advisory sparito senza fix" % pacchetto
    return PASS, "%s ora a %s, advisory %s assente con lo stesso DB" % (pacchetto, ", ".join(ora), finding)


def verifica(code_path, root=".", finding="", pacchetto=""):
    motivo = sg.guardia_storia(code_path, root)
    if motivo:
        raise sg.Rifiuto(motivo)
    repo = str(Path(code_path).resolve())
    cfg, ref, _mb, spiega = ca.blocco(root, "security_scan")
    if cfg is None:
        return {"esito": NON_VERIFICABILE, "motivo": spiega}
    toccati, mb = file_toccati(repo, ref)
    if toccati is None:
        return {"esito": NON_VERIFICABILE, "motivo": "diff dal merge-base con %s non leggibile" % ref}
    rep = {"file_toccati": toccati, "merge_base": mb}
    violazioni = perimetro(toccati)
    if violazioni:
        rep.update({"esito": FAIL, "motivo": "perimetro violato", "violazioni": [list(v) for v in violazioni]})
        return rep
    supp = sc.controlla(repo, ref, richiedi_pulito=True)
    nuove = [s for s in supp["soppressioni"] if not s["accettata"]]
    if nuove or supp["esito"] == sc.NON_VERIFICABILE:
        rep.update({"esito": FAIL if nuove else NON_VERIFICABILE,
                    "motivo": "il fix non sopprime: %d soppressioni nuove" % len(nuove) if nuove else supp["spiegazione"]})
        return rep
    rep_sca = sca.esegui(code_path, root, "osv-scanner")
    rep["sca"] = {"esito": rep_sca["esito"], "db": (rep_sca.get("db") or {}).get("id")}
    if rep_sca["esito"] == sca.FAIL:
        rep.update({"esito": FAIL, "motivo": "il fix introduce una vulnerabilita' nuova dal commit"})
        return rep
    if "voci" not in rep_sca:
        rep.update({"esito": NON_VERIFICABILE, "motivo": rep_sca.get("motivo")})
        return rep
    prima = [v["purl"] for v in rep_sca["voci"] if v["id"] == finding and v["stato"] == sca.SPARITO]
    esito, perche = _chiusura(rep_sca, finding, pacchetto, prima[0] if prima else None)
    rep.update({"esito": esito, "motivo": perche})
    return rep


def ciclo(verifica_giro, passo, max_iterazioni=MAX_ITERAZIONI_DEFAULT):
    """Loop bounded. `passo(i)` e' il giro del dev-agent (fuori da questo modulo); `verifica_giro()` il gate."""
    storia = []
    for i in range(1, max_iterazioni + 1):
        passo(i)
        r = verifica_giro()
        storia.append({"iterazione": i, "esito": r["esito"], "motivo": r.get("motivo"),
                       "file_toccati": sorted(r.get("file_toccati", []))})
        if r["esito"] != APERTO:
            return {"esito": r["esito"], "iterazioni": storia, "markers": {"no_progress": False, "loop_exhausted": False}}
        if len(storia) >= 2 and storia[-1]["motivo"] == storia[-2]["motivo"] and \
                storia[-1]["file_toccati"] == storia[-2]["file_toccati"]:
            return {"esito": APERTO, "iterazioni": storia, "markers": {"no_progress": True, "loop_exhausted": False}}
    return {"esito": APERTO, "iterazioni": storia, "markers": {"no_progress": False, "loop_exhausted": True}}


def max_iterazioni(root):
    cfg, _r, _m, _s = ca.blocco(root, "security_scan")
    try:
        return max(1, int((cfg or {}).get("fix_max_iterations") or MAX_ITERAZIONI_DEFAULT))
    except ValueError:
        return MAX_ITERAZIONI_DEFAULT


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("code_path")
    ap.add_argument("--finding", required=True, help="id dell'advisory da chiudere (es. GHSA-...)")
    ap.add_argument("--pacchetto", required=True, help="nome del pacchetto vulnerabile")
    ap.add_argument("--root", default=".")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        rep = verifica(a.code_path, a.root, a.finding, a.pacchetto)
    except sg.Rifiuto as e:
        print("[fix-gate] RIFIUTATO: %s." % e)
        return 2
    except Exception as e:
        print("[fix-gate] NON_VERIFICABILE: errore interno (%s: %s)" % (type(e).__name__, e))
        return EXIT[NON_VERIFICABILE]
    if a.json:
        print(json.dumps(rep, indent=2, ensure_ascii=False))
    else:
        print("[fix-gate] %s: %s" % (rep["esito"], rep.get("motivo")))
        for p, m in rep.get("violazioni", []):
            print("  %s: %s" % (p, m))
        print("  Il fix resta una proposta: nessun push, nessun merge (r.14, r.16).")
    return EXIT[rep["esito"]]


if __name__ == "__main__":
    sys.exit(main())

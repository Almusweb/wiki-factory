#!/usr/bin/env python3
"""Diff-check sulle soppressioni degli scanner di sicurezza (EP-109 US-428 AC3, TSK-1044; accordi A6, A18).

Una soppressione nuova fa sparire un finding senza toglierne la causa. Questo check guarda il diff fra
il merge-base con il ref protetto e HEAD e da' FAIL su ogni soppressione aggiunta, salvo un record di
accettazione che esiste gia' al merge-base: un record committato solo sul branch non vale, perche'
chi aggiunge la soppressione non deve poterla accettare nello stesso branch.

Cosa conta come soppressione aggiunta (righe aggiunte del diff, con `--no-renames`: un file di
soppressioni rinominato o spostato risulta tutto aggiunto):
    inline      in una riga di commento (`#`, `//`, `/*`, `*` di continuazione, `--`, `<!--`, `;`, `%`):
                nosemgrep e il suo alias nosem, nosec, gitleaks:allow, trivy:ignore
    file        ogni riga non vuota e non di commento aggiunta a .trivyignore, .trivyignore.yaml,
                .gitleaksignore, .semgrepignore (qualunque cartella), e a osv-scanner.toml: per
                osv-scanner conta qualunque riga, perche' anche PackageOverrides spegne finding

Record di accettazione: file `suppression_check.accettazioni` (default
`security/suppression-accettazioni.json`), lista JSON letta con `git show <merge-base>:<path>`.
Campi: `path`, `tipo` (nome della soppressione, es. `nosemgrep` o `.trivyignore`), `testo` (la riga
aggiunta senza spazi ai bordi), `motivo`, `scadenza` (AAAA-MM-GG, inclusa), `accettato_da`,
`riferimento_gate`, tutti non vuoti. Il numero di riga non conta. Scaduto o incompleto = assente.
`accettato_da` e' una traccia, non una firma: chi scrive sul ref protetto puo' produrlo.

Esiti ed exit code:
    PASS              0  nessuna soppressione aggiunta senza record valido
    FAIL              1  almeno una soppressione aggiunta senza record valido al merge-base
    NON_VERIFICABILE  3  ref protetto non risolto, git non eseguibile o diff illeggibile: nessuna
                         verifica, mai PASS

Ogni record copre una sola riga aggiunta: due righe identiche nello stesso file vogliono due record.

Cosa NON garantisce: copre solo le forme elencate; non copre i file di config che spengono regole
(`.gitleaks.toml` con allowlist, `trivy.yaml`, `:include` in `.semgrepignore`): gli oracoli li prendono
dal merge-base, non dal branch (una config dello scanner passata da riga di comando,
una regola tolta dal ruleset o un `--exclude` non sono righe di soppressione: le regole e la config si
leggono dal merge-base negli oracoli, A6); un commento che contiene la parola per caso e' segnalato
(falso positivo, da accettare con record); le modifiche non committate danno NON_VERIFICABILE (dalla CLI), non sono analizzate; i file ignorati
da `.gitignore` non risultano modificati (un `.trivyignore` ignorato e non tracciato sul disco non e' visto:
gli oracoli scansionano HEAD, chi lancia uno scanner a mano sul working tree no).

CLI: suppression_check.py [--root R] [--ref REF] [--json]
     (la data e' sempre quella di oggi: nessun flag per far tornare validi record scaduti)
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config_ancorata  # noqa: E402

PASS = "PASS"
FAIL = "FAIL"
NON_VERIFICABILE = "NON_VERIFICABILE"
EXIT_CODES = {PASS: 0, FAIL: 1, NON_VERIFICABILE: 3}

ACCETTAZIONI_DEFAULT = "security/suppression-accettazioni.json"
REF_PROTETTO_DEFAULT = "origin/main"
CAMPI_RECORD = ("path", "tipo", "testo", "motivo", "scadenza", "accettato_da", "riferimento_gate")

INLINE = ("nosemgrep", "nosem", "nosec", "gitleaks:allow", "trivy:ignore")
_COMMENTO = r"(?:#|//|/\*|--|<!--|;|%|^\s*\*)"
_INLINE_RE = [(t, re.compile(_COMMENTO + r"[^\n]*?(?<![A-Za-z0-9_])" + re.escape(t) + r"(?![A-Za-z0-9_])",
                             re.IGNORECASE)) for t in INLINE]

FILE_SOPPRESSIONI = (".trivyignore", ".trivyignore.yaml", ".gitleaksignore", ".semgrepignore")
FILE_OGNI_RIGA = ("osv-scanner.toml",)


def _git(root, *args):
    try:
        r = subprocess.run(["git", "-C", str(root)] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError:
        return None, b""
    return r.returncode, r.stdout


_ESCAPE = {"a": "\a", "b": "\b", "t": "\t", "n": "\n", "v": "\v", "f": "\f", "r": "\r", '"': '"', "\\": "\\"}


def _path_git(campo):
    """Path di un'intestazione `+++`: git mette fra virgolette (stile C) i path con `"`, `\\`, tab o
    a capo anche con core.quotepath=false. Restituisce il path senza il prefisso `b/`."""
    # git aggiunge un TAB in coda all'intestazione quando il path contiene uno spazio (CQRL iter-2)
    if campo.endswith("\t"):
        campo = campo[:-1]
    if campo.startswith('"') and campo.endswith('"') and len(campo) >= 2:
        corpo, out, i = campo[1:-1], bytearray(), 0
        while i < len(corpo):
            c = corpo[i]
            if c == "\\" and i + 1 < len(corpo):
                n = corpo[i + 1]
                if n in "01234567" and i + 3 < len(corpo) + 1 and all(x in "01234567" for x in corpo[i + 1:i + 4]):
                    out.append(int(corpo[i + 1:i + 4], 8))
                    i += 4
                    continue
                out.extend(_ESCAPE.get(n, n).encode("utf-8"))
                i += 2
                continue
            out.extend(c.encode("utf-8"))
            i += 1
        campo = out.decode("utf-8", "replace")
    return campo[2:] if campo.startswith("b/") else campo


def righe_aggiunte(diff_text):
    """[(path, testo)] delle righe aggiunte in un diff unificato (path del lato b)."""
    out = []
    path = None
    in_hunk = False
    # split("\n"), non splitlines(): \f, \x1c-\x1e, U+2028/2029 non sono fine riga per git ne' per
    # gli scanner, e splitlines() porterebbe il commento dopo un \f su una «riga» senza `+` (CQRL iter-2)
    for riga in diff_text.split("\n"):
        if riga.startswith("diff --git "):
            path, in_hunk = None, False
            continue
        if not in_hunk:
            if riga.startswith("+++ "):
                dest = riga[4:]
                path = None if dest == "/dev/null" else _path_git(dest)
            elif riga.startswith("@@"):
                in_hunk = True
            continue
        if riga.startswith("@@"):
            continue
        if riga.startswith("+") and path is not None:
            out.append((path, riga[1:]))
    return out


def soppressioni(aggiunte):
    """[{path, tipo, testo}] delle soppressioni fra le righe aggiunte."""
    trovate = []
    for path, testo in aggiunte:
        nome = os.path.basename(path)
        pulito = testo.strip()
        if nome in FILE_OGNI_RIGA:
            if pulito:
                trovate.append({"path": path, "tipo": nome, "testo": pulito})
            continue
        if nome in FILE_SOPPRESSIONI:
            if pulito and not pulito.startswith("#"):
                trovate.append({"path": path, "tipo": nome, "testo": pulito})
            continue
        for tipo, rx in _INLINE_RE:
            if rx.search(testo):
                trovate.append({"path": path, "tipo": tipo, "testo": pulito})
    return trovate


def _record_valido(r, oggi):
    if not isinstance(r, dict):
        return False
    for c in CAMPI_RECORD:
        if not isinstance(r.get(c), str) or not r[c].strip():
            return False
    try:
        return datetime.date.fromisoformat(r["scadenza"].strip()) >= oggi
    except ValueError:
        return False


def _accettazioni(root, mb, path, oggi):
    rc, dati = _git(root, "show", "%s:%s" % (mb, path))
    if rc != 0:
        return [], "nessun file di accettazioni %s al merge-base (%s)" % (path, mb[:8])
    try:
        voci = json.loads(dati.decode("utf-8"))
    except ValueError:
        return [], "%s al merge-base (%s) non e' JSON valido: nessuna accettazione" % (path, mb[:8])
    voci = voci if isinstance(voci, list) else []
    return [r for r in voci if _record_valido(r, oggi)], "accettazioni da %s al merge-base (%s)" % (path, mb[:8])


def _modifiche_non_committate(root):
    """Path tracciati modificati o non tracciati (non ignorati); None se git non risponde."""
    rc, out = _git(root, "status", "--porcelain", "-z", "--untracked-files=all")
    if rc != 0:
        return None
    voci, out_ = out.split(b"\0"), []
    i = 0
    while i < len(voci):
        v = voci[i]
        if len(v) > 3:
            out_.append(v[3:].decode("utf-8", "replace"))
            if v[:1] in (b"R", b"C"):   # con -z la rinomina porta il path vecchio come voce a se'
                i += 1
        i += 1
    return out_


def controlla(root=".", ref=None, oggi=None, richiedi_pulito=True):
    """Dict con esito, spiegazione e soppressioni (ciascuna con `accettata` e, se si', il record).

    `ref` esplicito (chiamante, es. un oracolo che l'ha letto dall'ancora) prevale; altrimenti blocco e
    `ref_protetto` si leggono dall'ancora con config_ancorata, mai dal factory.config.yaml su disco.

    Il check vede solo HEAD: con `richiedi_pulito` (default, la CLI) modifiche non committate danno
    NON_VERIFICABILE invece di un PASS su cio' che non e' stato guardato. Gli oracoli lo chiamano con
    False perche' anche loro scansionano HEAD (alberi da git), non il working tree."""
    if richiedi_pulito:
        sporchi = _modifiche_non_committate(root)
        if sporchi is None or sporchi:
            return {"esito": NON_VERIFICABILE, "spiegazione": (
                "modifiche non committate (%s): il check vede solo HEAD, nessun PASS sul working tree"
                % (", ".join(sporchi[:5]) if sporchi else "git status fallito")), "soppressioni": []}
    cfg, ref_ancora, _mb, spiega = config_ancorata.blocco(root, "suppression_check")
    if cfg is None and not ref:
        return {"esito": NON_VERIFICABILE, "spiegazione": spiega + ": nessuna verifica delle soppressioni",
                "soppressioni": []}
    cfg = cfg or {}
    ref = ref or ref_ancora or REF_PROTETTO_DEFAULT
    path_acc = cfg.get("accettazioni") or ACCETTAZIONI_DEFAULT
    oggi = oggi or datetime.date.today()
    rc, out = _git(root, "merge-base", "HEAD", ref)
    if rc != 0 or not out.strip():
        return {"esito": NON_VERIFICABILE, "spiegazione": "ref protetto %s non risolto da HEAD (o git assente): "
                "nessuna verifica delle soppressioni" % ref, "soppressioni": []}
    mb = out.decode("ascii", "replace").strip()
    # --text --no-textconv: un attributo `binary` o un NUL non nascondono le righe aggiunte;
    # prefissi espliciti: diff.noprefix / diff.mnemonicPrefix dell'utente non cambiano il parsing
    rc, diff = _git(root, "-c", "core.quotepath=false", "diff", "--no-renames", "--no-color", "--unified=0",
                    "--no-ext-diff", "--text", "--no-textconv", "--src-prefix=a/", "--dst-prefix=b/", mb, "HEAD")
    if rc != 0:
        return {"esito": NON_VERIFICABILE, "spiegazione": "git diff %s..HEAD fallito" % mb[:8], "soppressioni": []}
    trovate = soppressioni(righe_aggiunte(diff.decode("utf-8", "replace")))
    accettate, spiegazione = _accettazioni(root, mb, path_acc, oggi)
    liberi = list(accettate)   # un record copre una sola riga: righe identiche ne vogliono uno ciascuna
    for s in trovate:
        rec = next((r for r in liberi if r["path"] == s["path"] and r["tipo"] == s["tipo"]
                    and r["testo"].strip() == s["testo"]), None)
        s["accettata"] = rec is not None
        if rec:
            s["record"] = rec
            liberi.remove(rec)
    esito = FAIL if any(not s["accettata"] for s in trovate) else PASS
    return {"esito": esito, "merge_base": mb, "ref_protetto": ref, "spiegazione": spiegazione,
            "soppressioni": trovate}


def testo(rep):
    righe = ["[suppression-check] %s: %s" % (rep["esito"], rep["spiegazione"])]
    for s in rep["soppressioni"]:
        righe.append("  %s %s %s: %s" % ("accettata " if s["accettata"] else "NUOVA     ", s["tipo"], s["path"], s["testo"]))
    if rep["esito"] == FAIL:
        righe.append("  Ogni soppressione nuova va accettata con un record sul ref protetto prima del branch "
                     "(campi: %s)." % ", ".join(CAMPI_RECORD))
    return "\n".join(righe)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--ref", help="ref protetto (default: suppression_check.ref_protetto o origin/main)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    rep = controlla(a.root, a.ref)
    print(json.dumps(rep, indent=2, ensure_ascii=False) if a.json else testo(rep))
    return EXIT_CODES[rep["esito"]]


if __name__ == "__main__":
    sys.exit(main())

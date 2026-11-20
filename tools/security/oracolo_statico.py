#!/usr/bin/env python3
"""Motore comune degli oracoli di analisi statica (EP-109 US-427: semgrep in sast_guard.py, trivy in
iac_guard.py). Contratto PASS / FAIL / NON_VERIFICABILE, nessun giudizio di un agente.

Passi, uguali per ogni scanner:
  1. perimetro: solo un `code_paths[]` dichiarato, mai il repo della factory (stessa guardia della
     modalita' storia di secrets_guard.py, che fallisce chiusa);
  2. identita' del binario con scanner_identity.py (decisione D7): si esegue il percorso fissato e
     verificato, mai quello trovato nel PATH; non identificato = NON_VERIFICABILE;
  3. ruleset o config dello scanner dal dominio della factory, letti al merge-base fra HEAD della factory
     e `security_scan.ref_protetto` (A6): un ruleset cambiato solo sul branch non vale. La versione del
     ruleset entra nel report (sha256 del contenuto e commit del merge-base della factory, US-427 AC2);
  4. due alberi scritti blob per blob (`cat-file --batch`, non `git archive`) dal repo del cliente: il merge-base con il ref protetto
     (PRIMA) e HEAD (DOPO). I file di config che lo scanner legge da solo nell'albero (`.semgrepignore`,
     `.trivyignore`, ...) si tolgono da entrambi e si rimettono nella versione del merge-base: una
     modifica sul branch non spegne nulla;
  5. confronto per identita' con finding_compare.py: file cancellato, spostato o rinominato =
     NON_VERIFICABILE, mai PASS; finding nuovo = FAIL;
  6. diff-check con suppression_check.py, filtrato sulle soppressioni di questo scanner: una soppressione
     aggiunta senza record al merge-base = FAIL.

Esito complessivo: FAIL se il confronto o il diff-check danno FAIL; altrimenti NON_VERIFICABILE se uno
dei passi non e' verificabile; altrimenti PASS, che significa «con questo binario e questo ruleset nessun
finding nuovo rispetto al merge-base». I finding gia' presenti al merge-base sono elencati, non assolti.

Config: il blocco `security_scan` (ref e path dei ruleset) si legge dall'ancora `origin/main` con
config_ancorata, mai dal factory.config.yaml su disco. Gli alberi non passano da `git archive`, quindi
export-ignore ed export-subst non tolgono ne' riscrivono file; un file tracciato non scritto da'
NON_VERIFICABILE. Uno scanner che riporta errori su un file cambiato (o un errore globale) da'
NON_VERIFICABILE.

Cosa NON garantisce: non vede logica di business ne' autorizzazione; copre solo cio' che le regole
conoscono; l'identita' del finding e' (regola, file) senza simbolo, quindi un finding che sparisce col
file presente e' NON_VERIFICABILE (simbolo_non_dichiarato), mai una chiusura: un fix SAST si conferma solo
con una review umana; le soppressioni si leggono dal
repo del cliente (il record di accettazione sta li', non nel dominio della factory); un agente con Bash
puo' eseguire lo scanner fuori dall'oracolo.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import hashlib
from pathlib import Path

QUI = os.path.dirname(os.path.abspath(__file__))
if QUI not in sys.path:
    sys.path.insert(0, QUI)
import config_ancorata as ca  # noqa: E402
import finding_compare as fc  # noqa: E402
import scanner_identity as si  # noqa: E402
import contratto_segreti as sg  # noqa: E402
import suppression_check as sc  # noqa: E402

PASS = "PASS"
FAIL = "FAIL"
NON_VERIFICABILE = "NON_VERIFICABILE"
EXIT_CODES = {PASS: 0, FAIL: 1, NON_VERIFICABILE: 3}
EXIT_RIFIUTO = 2
TIMEOUT_SCANNER = 1800


class Scanner(object):
    """Cio' che distingue uno scanner: nome per scanner_identity, chiave del ruleset in `security_scan`,
    file di config letti dall'albero, tipi di soppressione di suppression_check, comando e parser."""

    def __init__(self, nome, chiave_ruleset, config_albero, soppressioni, comando, analizza, exit_ok=(0, 1)):
        self.nome = nome
        self.exit_ok = exit_ok        # exit code dello scanner che non sono errori
        self.chiave_ruleset = chiave_ruleset
        self.config_albero = config_albero
        self.soppressioni = soppressioni
        self.comando = comando        # (exe, albero, ruleset, uscita) -> argv
        self.analizza = analizza      # (dati json, albero, ruleset) -> [{"rule_id", "path", "symbol"}]
                                      # in coda, facoltativo, un set dei path non analizzati ("*" = tutti)


def _git(repo, *args):
    try:
        r = subprocess.run(["git", "-C", str(repo)] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError:
        return None, b""
    return r.returncode, r.stdout


def merge_base(repo, ref):
    rc, out = _git(repo, "merge-base", "HEAD", ref)
    return out.decode("ascii", "replace").strip() if rc == 0 and out.strip() else None


def rev(repo, nome):
    rc, out = _git(repo, "rev-parse", "--verify", nome + "^{commit}")
    return out.decode("ascii", "replace").strip() if rc == 0 else None


def _voci_tree(repo, commit):
    """[(path, modo, blob)] dei blob di `commit` (modi 100644, 100755, 120000); None se git fallisce."""
    rc, out = _git(repo, "ls-tree", "-r", "-z", commit)
    if rc != 0:
        return None
    res = []
    for voce in out.split(b"\0"):
        if not voce:
            continue
        meta, path = voce.split(b"\t", 1)
        parti = meta.split()
        if len(parti) == 3 and parti[1] == b"blob":
            try:
                nome = path.decode("utf-8")
            except UnicodeDecodeError:
                # con "replace" due path non UTF-8 diventavano lo stesso nome e uno sovrascriveva l'altro
                # (CQRL iter-4 N6): un path non decodificabile rende l'albero non verificabile
                return None
            res.append((nome, parti[0].decode("ascii"), parti[2].decode("ascii")))
    return res


def file_presenti(repo, commit, solo_regolari=False):
    """{path: blob} dei file tracciati a `commit` (con solo_regolari, senza i symlink: modo 120000)."""
    voci = _voci_tree(repo, commit)
    if voci is None:
        return None
    return {p: b for p, m, b in voci if not (solo_regolari and m == "120000")}


def file_estratti(albero):
    out = set()
    for base, _dirs, files in os.walk(albero):
        for f in files:
            out.add(os.path.relpath(os.path.join(base, f), albero).replace(os.sep, "/"))
    return out


def _path_sicuro(path):
    """False per path assoluti, con `..`, vuoti o con un componente che vale `.git` senza distinguere
    maiuscole (come verify_path di git: su un filesystem case-insensitive `.GIT` e' `.git`). Una cartella
    `.git` scritta nell'albero farebbe credere allo scanner di essere in un repo e gli farebbe onorare
    `.git/info/exclude` (CQRL iter-3)."""
    parti = path.split("/")
    if not path or path.startswith("/") or any(p in ("", ".", "..") for p in parti):
        return False
    return not any(p.rstrip(". ").lower() == ".git" for p in parti)


def materializza(repo, commit, dest):
    """Scrive in `dest` i blob regolari di `commit` cosi' come sono nel repo (ls-tree + cat-file --batch).

    Non usa `git archive`: applica `export-ignore` (toglie file) ed `export-subst` (riscrive il contenuto,
    puo' chiudere una stringa sopra codice vulnerabile), cioe' attributi che il branch controlla (CQRL
    iter-1 e iter-2). Conserva il bit eseguibile (100755): semgrep riconosce dallo shebang solo i file
    eseguibili (iter-3). I symlink (120000) e i submodule non si scrivono. Legge un blob alla volta (niente
    output intero in memoria). False se git fallisce, un path non e' sicuro o la scrittura fallisce (es. `X`
    e `x/` nello stesso tree su un filesystem case-insensitive)."""
    voci = _voci_tree(repo, commit)
    if voci is None:
        return False
    voci = [(p, m, b) for p, m, b in voci if m != "120000"]
    if not all(_path_sicuro(p) for p, _m, _b in voci):
        return False
    if not voci:
        return True
    try:
        proc = subprocess.Popen(["git", "-C", str(repo), "cat-file", "--batch"], stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    except OSError:
        return False
    try:
        for path, modo, sha in voci:
            proc.stdin.write(sha.encode("ascii") + b"\n")
            proc.stdin.flush()
            testa = proc.stdout.readline().split()
            if len(testa) != 3 or testa[0].decode("ascii") != sha or testa[1] != b"blob":
                return False
            n = int(testa[2])
            dati = proc.stdout.read(n)
            if len(dati) != n or proc.stdout.read(1) != b"\n":
                return False
            destinazione = Path(dest) / path
            destinazione.parent.mkdir(parents=True, exist_ok=True)
            destinazione.write_bytes(dati)
            if modo == "100755":
                destinazione.chmod(0o755)
        return True
    except (OSError, ValueError):
        return False
    finally:
        # kill prima di wait: uscendo a meta' (intestazione inattesa) il corpo dell'oggetto resta nella pipe
        # e cat-file non termina mai (CQRL iter-4 N7)
        try:
            proc.stdin.close()
        except OSError:
            pass
        if proc.poll() is None:
            proc.kill()
        proc.wait()


def _metti_config_del_merge_base(repo, mb, albero, nomi):
    """Toglie dall'albero ogni file di config dello scanner e rimette la versione del merge-base."""
    for base, _dirs, files in os.walk(albero):
        for f in files:
            if f in nomi:
                os.remove(os.path.join(base, f))
    mb_files = file_presenti(repo, mb) or {}
    for p in mb_files:
        if os.path.basename(p) in nomi:
            rc, dati = _git(repo, "show", "%s:%s" % (mb, p))
            if rc == 0:
                dest = Path(albero) / p
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(dati)


def _nv(motivo, **extra):
    r = {"esito": NON_VERIFICABILE, "motivo": motivo}
    r.update(extra)
    return r


def _scansiona(scanner, exe, albero, ruleset, tmp, nome):
    uscita = os.path.join(tmp, "%s-%s.json" % (scanner.nome, nome))
    try:
        r = subprocess.run(scanner.comando(exe, albero, ruleset, uscita), stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, cwd=albero, timeout=TIMEOUT_SCANNER)
    except (OSError, subprocess.SubprocessError) as e:
        return None, "%s non eseguibile (%s)" % (scanner.nome, e)
    if r.returncode not in scanner.exit_ok:
        return None, "%s e' terminato con errore (exit %d)" % (scanner.nome, r.returncode)
    try:
        import json
        with open(uscita, encoding="utf-8") as fh:
            dati = json.load(fh)
        return scanner.analizza(dati, albero, ruleset), None
    except (OSError, ValueError, KeyError, TypeError) as e:
        return None, "report di %s illeggibile (%s)" % (scanner.nome, e)


class _NonVerificabile(Exception):
    pass


def _ruleset(scanner, root):
    """(ref, merge-base della factory, path, contenuto, sha256) del ruleset, dall'ancora della factory.

    Blocco security_scan, ref e path dall'ancora, mai dal factory.config.yaml su disco (CQRL iter-1:
    `ref_protetto: HEAD` o un path diverso non committati davano PASS)."""
    cfg, ref, mb_factory, spiega = ca.blocco(root, "security_scan")
    if cfg is None:
        raise _NonVerificabile(spiega)
    path_rs = cfg.get(scanner.chiave_ruleset)
    if not path_rs:
        raise _NonVerificabile("ruleset non fissato: security_scan.%s assente o null al merge-base della "
                               "factory (%s)" % (scanner.chiave_ruleset, mb_factory[:8]))
    rc, contenuto = _git(root, "show", "%s:%s" % (mb_factory, path_rs))
    if rc != 0:
        raise _NonVerificabile("ruleset %s assente al merge-base della factory (%s)" % (path_rs, mb_factory[:8]))
    return ref, mb_factory, path_rs, contenuto, hashlib.sha256(contenuto).hexdigest()


def _albero(repo, commit, albero):
    """Scrive l'albero di `commit` e controlla che contenga tutti i file regolari tracciati."""
    os.mkdir(albero)
    if not materializza(repo, commit, albero):
        raise _NonVerificabile("estrazione dei blob di %s fallita (git, path non sicuro o scrittura)" % commit[:8])
    attesi = file_presenti(repo, commit, solo_regolari=True)
    if attesi is None:
        raise _NonVerificabile("ls-tree di %s fallito: nessun confronto dei file estratti" % commit[:8])
    mancanti = sorted(set(attesi) - file_estratti(albero))
    if mancanti:
        raise _NonVerificabile("%d file tracciati a %s non estratti: %s"
                               % (len(mancanti), commit[:8], ", ".join(mancanti[:5])))
    return attesi


def _esecuzione(scanner, ident, repo, commit, mb, cartella, ruleset, db_id, cambiati_rispetto_a=None):
    """Esecuzione nel contratto di finding_compare per `commit`. Con `cambiati_rispetto_a` (i blob del
    merge-base) un errore dello scanner su un file cambiato rende la scansione non verificabile."""
    os.makedirs(cartella, exist_ok=True)
    albero = os.path.join(cartella, "albero-" + commit[:12])
    attesi = _albero(repo, commit, albero)
    _metti_config_del_merge_base(repo, mb, albero, scanner.config_albero)
    findings, errore = _scansiona(scanner, ident.realpath, albero, ruleset, cartella, commit[:12])
    if errore:
        raise _NonVerificabile(errore)
    non_analizzati = findings.pop() if findings and isinstance(findings[-1], set) else set()
    cambiati = set()
    if cambiati_rispetto_a is not None:
        cambiati = {p for p, b in attesi.items() if cambiati_rispetto_a.get(p) != b}
    bloccanti = sorted(x for x in non_analizzati if x == "*" or x in cambiati)
    if bloccanti:
        raise _NonVerificabile("%s non ha analizzato del tutto %s (errori dello scanner): un finding assente "
                               "li' non e' verificato" % (scanner.nome, ", ".join(bloccanti[:5])))
    return {"tool": scanner.nome, "tool_version": ident.version or "non dichiarata", "db_id": db_id,
            "commit": commit, "findings": findings, "file_presenti": file_presenti(repo, commit) or {},
            "simboli_presenti": []}


def _verdetto(confronto, supp, proprie):
    if confronto["esito"] == fc.FAIL or any(not s["accettata"] for s in proprie):
        return FAIL
    if confronto["esito"] == fc.NON_VERIFICABILE or supp["esito"] == sc.NON_VERIFICABILE:
        return NON_VERIFICABILE
    return PASS


def esegui(scanner, code_path, root="."):
    """Report dell'oracolo per `code_path`. Solleva sg.Rifiuto fuori perimetro."""
    motivo = sg.guardia_storia(code_path, root)
    if motivo:
        raise sg.Rifiuto(motivo)
    ident = si.identifica(scanner.nome, root)
    rep = {"tool": scanner.nome, "code_path": code_path, "identita": ident.report()}
    try:
        if not ident.identificato:
            raise _NonVerificabile("binario non identificato: %s" % ident.messaggio)
        ref, mb_factory, path_rs, contenuto, sha_rs = _ruleset(scanner, root)
        rep["ruleset"] = {"path": path_rs, "sha256": sha_rs, "merge_base_factory": mb_factory}
        repo = str(Path(code_path).resolve())
        mb, head = merge_base(repo, ref), rev(repo, "HEAD")
        if not mb or not head:
            raise _NonVerificabile("ref protetto %s non risolto nel code_path: nessun confronto possibile" % ref)
        rep["merge_base"], rep["head"] = mb, head
        db_id = "ruleset:%s@%s" % (sha_rs[:12], mb_factory[:12])
        with tempfile.TemporaryDirectory(prefix="oracolo-%s-" % scanner.nome) as tmp:
            ruleset = os.path.join(tmp, "ruleset-" + os.path.basename(path_rs))
            with open(ruleset, "wb") as fh:
                fh.write(contenuto)
            prima = _esecuzione(scanner, ident, repo, mb, mb, os.path.join(tmp, "prima"), ruleset, db_id)
            dopo = _esecuzione(scanner, ident, repo, head, mb, os.path.join(tmp, "dopo"), ruleset, db_id,
                               cambiati_rispetto_a=file_presenti(repo, mb) or {})
    except _NonVerificabile as e:
        rep.update(_nv(str(e)))
        return rep
    confronto = fc.confronta(prima, dopo)
    supp = sc.controlla(repo, ref, richiedi_pulito=False)   # anche l'oracolo guarda HEAD, non il disco
    proprie = [s for s in supp["soppressioni"] if s["tipo"] in scanner.soppressioni]
    rep["confronto"] = confronto
    rep["soppressioni"] = {"esito": supp["esito"], "spiegazione": supp["spiegazione"], "voci": proprie}
    rep["esito"] = _verdetto(confronto, supp, proprie)
    return rep


def riga(rep):
    testa = "[%s-guard] %s" % (rep["tool"], rep["esito"])
    if rep.get("motivo"):
        return testa + ": " + rep["motivo"]
    righe = [testa + " — %s %s, ruleset %s (sha256 %s)" % (
        rep["tool"], rep["identita"].get("version"), rep["ruleset"]["path"], rep["ruleset"]["sha256"][:12])]
    for v in rep["confronto"].get("voci", []):
        righe.append("  %-30s %s" % (v["esito"] + ("/" + v["motivo"] if v.get("motivo") else ""),
                                     " ".join(v["identita"][1:])))
    if rep["confronto"].get("motivo"):
        righe.append("  confronto: %s — %s" % (rep["confronto"]["motivo"], rep["confronto"].get("dettaglio", "")))
    for s in rep["soppressioni"]["voci"]:
        righe.append("  soppressione %s %s %s: %s" % ("accettata" if s["accettata"] else "NUOVA", s["tipo"],
                                                     s["path"], s["testo"]))
    return "\n".join(righe)


def main(scanner, argv=None):
    import argparse
    import json
    ap = argparse.ArgumentParser(description="Oracolo %s (EP-109 US-427)" % scanner.nome)
    ap.add_argument("code_path")
    ap.add_argument("--root", default=".", help="radice della factory")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        rep = esegui(scanner, a.code_path, a.root)
    except sg.Rifiuto as e:
        print("[%s-guard] RIFIUTATO: %s." % (scanner.nome, e))
        return EXIT_RIFIUTO
    except Exception as e:  # un'eccezione non e' un FAIL: nessuna verifica e' avvenuta (CQRL iter-4 N10)
        print("[%s-guard] NON_VERIFICABILE: errore interno (%s: %s)" % (scanner.nome, type(e).__name__, e))
        return EXIT_CODES[NON_VERIFICABILE]
    print(json.dumps(rep, indent=2, ensure_ascii=False) if a.json else riga(rep))
    return EXIT_CODES[rep["esito"]]

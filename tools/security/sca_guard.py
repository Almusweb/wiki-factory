#!/usr/bin/env python3
"""Oracolo SCA: inventario (SBOM), identita' del DB degli advisory e delta dal baseline (EP-109 US-425,
TSK-1038; accordi A8, A12, A13, A27). Nessun PASS assoluto.

Scanner: osv-scanner (default) o trivy, identificati con scanner_identity (D7) ed eseguiti dal percorso
fissato. Entrambi in CycloneDX, che porta nello stesso file l'inventario (componenti con purl) e le
vulnerabilita' (con `affects` verso i componenti). Offline per costruzione (spike TSK-1037):
    osv-scanner  scan source -r --offline --offline-vulnerabilities, DB in
                 `security_scan.osv_db_dir` (OSV_SCANNER_LOCAL_DB_CACHE_DIRECTORY); identita' del DB =
                 sha256 di ogni `<ecosistema>/all.zip`. Senza `--offline` osv-scanner risolverebbe in rete
                 le dipendenze transitive e l'inventario dipenderebbe dal giorno
    trivy        fs --skip-db-update --skip-java-db-update --offline-scan --scanners vuln, cache in
                 `security_scan.trivy_cache_dir`; identita' del DB = sha256 di `db/trivy.db` piu'
                 `UpdatedAt` di `db/metadata.json` (il report di trivy non li contiene)

Due delta separati (A13), con lo stesso DB, sugli alberi PRIMA (merge-base del code_path con il ref
protetto) e DOPO (HEAD), scritti blob per blob come negli altri oracoli:
    nuovo_dal_commit       in DOPO e non in PRIMA, non nel baseline          -> FAIL
                           (lo stesso advisory sullo stesso pacchetto a un'altra versione non e' nuovo: debito)
    debito_non_nominato    in PRIMA e in DOPO, non nel baseline: debito mai accettato, oppure
                           effetto di un DB aggiornato a commit fermo          -> NON_VERIFICABILE (mai FAIL,
                           US-425 AC5: e' un evento di riscansione, US-432)
    accettato              nel baseline (per id, e per purl se il record lo dichiara)
    sparito                in PRIMA e non in DOPO: elencato, mai contato come risolto
Identita' del finding = (id dell'advisory, purl): il purl porta ecosistema e versione, quindi un pacchetto
a due versioni o lo stesso nome in due ecosistemi restano distinti.

Baseline (US-425 AC4, TSK-1039; accordo A12): file `security_scan.sca_baseline` (default
`security/sca-baseline.json`) nel dominio della factory, letto dal merge-base con l'ancora (config_ancorata),
mai dal working tree ne' dal branch. Senza baseline il primo run e' NON_VERIFICABILE, mai PASS (AC3). Un
record vale solo se ha `id`, `accettato_da`, `riferimento_gate`, `accettato_il` e `scadenza` (AAAA-MM-GG) non
vuoti, con `accettato_il` <= oggi <= `scadenza` e `scadenza` al massimo 90 giorni dopo `accettato_il`;
facoltativi `purl` e `motivo`. Ogni altro campo rende il record non valido: il baseline e' un dato
strutturato, senza testo di advisory. Un record scaduto o non valido vale come assente (il finding torna
debito non nominato, NON_VERIFICABILE) ed e' elencato fra gli scartati con il motivo. `accettato_da` e
`riferimento_gate` sono tracce, non firme.

Severita': WARN fino a `security_scan.sca_required_from` (AAAA-MM-GG, dall'ancora), ERROR da quella data. A
WARN un FAIL esce 0 e lo dichiara («non bloccante»); NON_VERIFICABILE esce sempre 3.

Esito: FAIL per un nuovo_dal_commit; altrimenti NON_VERIFICABILE per baseline assente, debito non
nominato, DB non identificabile, binario non identificato o scansione fallita; altrimenti PASS, che dice
«con questo binario e questo DB nessuna vulnerabilita' fuori dal baseline», non «dipendenze sicure».

Cosa NON garantisce: nessuna vulnerabilita' non pubblicata o non presente nel DB; senza lockfile si
vedono solo le dipendenze dirette dichiarate (offline nessuna risoluzione transitiva); la raggiungibilita'
dal codice non e' valutata; il DB non e' fissato a un valore atteso (lo confronta US-432); il baseline e'
una traccia, non una firma.

CLI: sca_guard.py CODE_PATH [--root FACTORY] [--scanner osv-scanner|trivy] [--json]
     exit 0 PASS, 1 FAIL, 2 rifiutato, 3 NON_VERIFICABILE
"""
from __future__ import annotations

import argparse
import datetime
import glob
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config_ancorata as ca  # noqa: E402
import oracolo_statico as ost  # noqa: E402
import scanner_identity as si  # noqa: E402
import contratto_segreti as sg  # noqa: E402

PASS, FAIL, NON_VERIFICABILE = ost.PASS, ost.FAIL, ost.NON_VERIFICABILE
EXIT_CODES = ost.EXIT_CODES
BASELINE_DEFAULT = "security/sca-baseline.json"
TIMEOUT = 1800

NUOVO = "nuovo_dal_commit"
DEBITO = "debito_non_nominato"
ACCETTATO = "accettato"
SPARITO = "sparito"


class _NonVerificabile(Exception):
    pass


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# --- per scanner: comando, ambiente, exit ammessi, identita' del DB --------------------------

def _db_osv(db_dir):
    zips = sorted(glob.glob(os.path.join(db_dir, "**", "all.zip"), recursive=True))
    if not zips:
        raise _NonVerificabile("nessun DB offline di osv-scanner in %s (serve --download-offline-databases "
                               "una volta, fuori dall'oracolo)" % db_dir)
    file_ = [{"path": os.path.relpath(z, db_dir), "sha256": _sha(z)} for z in zips]
    return {"tipo": "osv-offline", "file": file_,
            "id": "osv:" + hashlib.sha256("".join(f["path"] + f["sha256"] for f in file_).encode()).hexdigest()[:16]}


def _db_trivy(db_dir):
    db = os.path.join(db_dir, "db", "trivy.db")
    meta = os.path.join(db_dir, "db", "metadata.json")
    if not os.path.isfile(db) or not os.path.isfile(meta):
        raise _NonVerificabile("DB di trivy assente in %s/db (serve --download-db-only una volta, fuori "
                               "dall'oracolo; con --skip-db-update il primo run fallisce)" % db_dir)
    try:
        with open(meta, encoding="utf-8") as fh:
            updated = json.load(fh).get("UpdatedAt")
    except ValueError:
        raise _NonVerificabile("metadata.json del DB di trivy illeggibile")
    sha = _sha(db)
    return {"tipo": "trivy-db", "file": [{"path": "db/trivy.db", "sha256": sha}], "updated_at": updated,
            "id": "trivy:%s@%s" % (sha[:16], updated)}


SCANNER = {
    "osv-scanner": {
        "chiave_db": "osv_db_dir",
        "comando": lambda exe, uscita: [exe, "scan", "source", "-r", "--offline", "--offline-vulnerabilities",
                                        "--format", "cyclonedx-1-5", "--output-file", uscita, "."],
        "env": lambda db: {"OSV_SCANNER_LOCAL_DB_CACHE_DIRECTORY": db},
        "exit_ok": (0, 1, 128),          # 1 = vulnerabilita' trovate, 128 = nessun pacchetto
        "db": _db_osv,
    },
    "trivy": {
        "chiave_db": "trivy_cache_dir",
        "comando": lambda exe, uscita: [exe, "fs", "--skip-db-update", "--skip-java-db-update", "--offline-scan",
                                        "--scanners", "vuln", "--format", "cyclonedx", "--output", uscita,
                                        "--quiet", "."],
        "env": lambda db: {},
        "exit_ok": (0,),
        "db": _db_trivy,
    },
}


def _comando(nome, exe, uscita, db_dir):
    cmd = SCANNER[nome]["comando"](exe, uscita)
    if nome == "trivy":
        cmd[2:2] = ["--cache-dir", db_dir]
    return cmd


# --- CycloneDX --------------------------------------------------------------------------------

def _meta_vuln(v):
    """CVSS massimo e CWE dai campi strutturati di CycloneDX (`ratings[].score`, `cwes[]` interi): mai dal testo."""
    punteggi = [r.get("score") for r in (v.get("ratings") or []) if isinstance(r, dict)]
    punteggi = [float(x) for x in punteggi if isinstance(x, (int, float)) and not isinstance(x, bool) and 0 <= x <= 10]
    cwe = sorted({"CWE-%d" % c for c in (v.get("cwes") or []) if isinstance(c, int) and not isinstance(c, bool) and c > 0})
    return {"cvss": max(punteggi) if punteggi else None, "cwe": cwe}


def leggi_cyclonedx(dati):
    """(inventario: lista ordinata di purl, finding: set di (id, purl), meta: {(id, purl): {cvss, cwe}}).
    Solleva ValueError se malformato."""
    if not isinstance(dati, dict):
        raise ValueError("report CycloneDX non e' un oggetto")
    ref_purl, inventario = {}, set()
    for c in dati.get("components") or []:
        purl = c.get("purl")
        if isinstance(purl, str) and purl:
            inventario.add(purl)
            if c.get("bom-ref"):
                ref_purl[c["bom-ref"]] = purl
    finding, meta = set(), {}
    for v in dati.get("vulnerabilities") or []:
        vid = v.get("id")
        if not isinstance(vid, str) or not vid:
            raise ValueError("vulnerabilita' senza id")
        for a in v.get("affects") or []:
            ref = a.get("ref")
            purl = ref_purl.get(ref, ref if isinstance(ref, str) and ref.startswith("pkg:") else None)
            if not purl:
                raise ValueError("vulnerabilita' %s riferita a un componente sconosciuto (%s)" % (vid, ref))
            finding.add((vid, purl))
            meta[(vid, purl)] = _meta_vuln(v)
    return sorted(inventario), finding, meta


def _scansiona(nome, exe, albero, db_dir, cartella):
    uscita = os.path.join(cartella, "sbom.json")
    env = dict(os.environ)
    env.update(SCANNER[nome]["env"](db_dir))
    try:
        r = subprocess.run(_comando(nome, exe, uscita, db_dir), cwd=albero, env=env, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=TIMEOUT)
    except (OSError, subprocess.SubprocessError) as e:
        raise _NonVerificabile("%s non eseguibile (%s)" % (nome, e))
    if r.returncode not in SCANNER[nome]["exit_ok"]:
        raise _NonVerificabile("%s e' terminato con errore (exit %d): %s" % (
            nome, r.returncode, r.stderr.decode("utf-8", "replace").strip()[-200:]))
    if not os.path.exists(uscita):
        if r.returncode == 128:          # osv-scanner: nessun pacchetto trovato
            return [], set(), {}
        raise _NonVerificabile("%s non ha scritto il report (exit %d)" % (nome, r.returncode))
    try:
        with open(uscita, encoding="utf-8") as fh:
            return leggi_cyclonedx(json.load(fh))
    except (OSError, ValueError) as e:
        raise _NonVerificabile("report CycloneDX di %s illeggibile (%s)" % (nome, e))


# --- baseline ---------------------------------------------------------------------------------

CAMPI_OBBLIGATORI = ("id", "accettato_da", "riferimento_gate", "accettato_il", "scadenza")
CAMPI_FACOLTATIVI = ("purl", "motivo")
VALIDITA_MASSIMA = datetime.timedelta(days=90)


def _data(v):
    try:
        return datetime.date.fromisoformat(v.strip())
    except (AttributeError, ValueError):
        return None


def valida_record(r, oggi):
    """None se il record vale oggi, altrimenti il motivo per cui non vale."""
    if not isinstance(r, dict):
        return "non e' un oggetto"
    extra = sorted(set(r) - set(CAMPI_OBBLIGATORI) - set(CAMPI_FACOLTATIVI))
    if extra:
        return "campi non ammessi (niente testo di advisory nel baseline): %s" % ", ".join(extra)
    vuoti = [c for c in CAMPI_OBBLIGATORI if not isinstance(r.get(c), str) or not r[c].strip()]
    if vuoti:
        return "campi obbligatori mancanti o vuoti: %s" % ", ".join(vuoti)
    if r.get("purl") is not None and (not isinstance(r["purl"], str) or not r["purl"].startswith("pkg:")):
        return "purl non valido"
    il, fino = _data(r["accettato_il"]), _data(r["scadenza"])
    if il is None or fino is None:
        return "accettato_il o scadenza non sono date AAAA-MM-GG"
    if fino - il > VALIDITA_MASSIMA:
        return "scadenza oltre 90 giorni dall'accettazione (%s -> %s)" % (il, fino)
    if il > oggi:
        return "accettato_il nel futuro (%s)" % il
    if fino < oggi:
        return "scaduto il %s" % fino
    return None


def leggi_baseline(root, cfg, mb, oggi=None):
    """(record validi, record scartati con motivo) del baseline al merge-base della factory, o (None, [])
    se il file e' assente o illeggibile."""
    oggi = oggi or datetime.date.today()
    path = cfg.get("sca_baseline") or BASELINE_DEFAULT
    rc, dati = ost._git(root, "show", "%s:%s" % (mb, path))
    if rc != 0:
        return None, []
    try:
        voci = json.loads(dati.decode("utf-8"))
    except ValueError:
        return None, []
    if isinstance(voci, dict):
        voci = voci.get("accettati")
    if not isinstance(voci, list):
        return None, []
    validi, scartati = [], []
    for r in voci:
        motivo = valida_record(r, oggi)
        if motivo:
            scartati.append({"id": r.get("id") if isinstance(r, dict) else None, "motivo": motivo})
        else:
            validi.append(r)
    return validi, scartati


def severita(cfg, oggi=None):
    rf = _data(cfg.get("sca_required_from") or "")
    return "ERROR" if rf is not None and rf <= (oggi or datetime.date.today()) else "WARN"


def _accettato(f, baseline):
    vid, purl = f
    return any(r["id"] == vid and (not r.get("purl") or r.get("purl") == purl) for r in baseline)


def _senza_versione(purl):
    """pkg:tipo/[ns/]nome@versione?qualificatori -> pkg:tipo/[ns/]nome."""
    return purl.split("?", 1)[0].rsplit("@", 1)[0]


def classifica(prima, dopo, baseline):
    """Voci per identita'; nessun contatore. Lo stesso advisory sullo stesso pacchetto a un'altra versione e' lo
    stesso rischio che persiste (come in finding_compare), non una vulnerabilita' nuova dal commit: un fix che
    sale a una versione ancora vulnerabile e' debito, non FAIL."""
    pacchetti_prima = {(vid, _senza_versione(purl)) for vid, purl in prima}
    voci = []
    for f in sorted(dopo | prima):
        if f in dopo and baseline is not None and _accettato(f, baseline):
            stato = ACCETTATO
        elif f in dopo and f not in prima and (f[0], _senza_versione(f[1])) not in pacchetti_prima:
            stato = NUOVO
        elif f in dopo:
            stato = DEBITO
        else:
            stato = SPARITO
        voci.append({"id": f[0], "purl": f[1], "stato": stato})
    return voci


# --- esecuzione -------------------------------------------------------------------------------

def _db_dir(cfg, chiave, root):
    v = cfg.get(chiave)
    if not v:
        raise _NonVerificabile("DB non configurato: security_scan.%s assente o null all'ancora" % chiave)
    p = v if os.path.isabs(v) else os.path.join(str(root), v)
    if not os.path.isdir(p):
        raise _NonVerificabile("cartella del DB %s inesistente" % p)
    return p


def esegui(code_path, root=".", nome="osv-scanner", oggi=None):
    motivo = sg.guardia_storia(code_path, root)
    if motivo:
        raise sg.Rifiuto(motivo)
    ident = si.identifica(nome, root)
    rep = {"tool": nome, "code_path": code_path, "identita": ident.report()}
    try:
        if not ident.identificato:
            raise _NonVerificabile("binario non identificato: %s" % ident.messaggio)
        cfg, ref, mb_factory, spiega = ca.blocco(root, "security_scan")
        if cfg is None:
            raise _NonVerificabile(spiega)
        db_dir = _db_dir(cfg, SCANNER[nome]["chiave_db"], root)
        db_prima = SCANNER[nome]["db"](db_dir)
        repo = str(Path(code_path).resolve())
        mb, head = ost.merge_base(repo, ref), ost.rev(repo, "HEAD")
        if not mb or not head:
            raise _NonVerificabile("ref protetto %s non risolto nel code_path" % ref)
        rep.update({"merge_base": mb, "head": head})
        with tempfile.TemporaryDirectory(prefix="sca-guard-") as tmp:
            risultati = {}
            for fase, commit in (("prima", mb), ("dopo", head)):
                cartella = os.path.join(tmp, fase)
                os.makedirs(cartella)
                ost._albero(repo, commit, os.path.join(cartella, "albero"))
                risultati[fase] = _scansiona(nome, ident.realpath, os.path.join(cartella, "albero"), db_dir, cartella)
        if SCANNER[nome]["db"](db_dir)["id"] != db_prima["id"]:
            raise _NonVerificabile("il DB e' cambiato durante la scansione: PRIMA e DOPO non sono confrontabili")
    except ost._NonVerificabile as e:
        rep.update({"esito": NON_VERIFICABILE, "motivo": str(e)})
        return rep
    except _NonVerificabile as e:
        rep.update({"esito": NON_VERIFICABILE, "motivo": str(e)})
        return rep
    baseline, scartati = leggi_baseline(root, cfg, mb_factory, oggi)
    rep["severita"] = severita(cfg, oggi)
    inv_dopo, f_dopo, meta = risultati["dopo"]
    _inv_prima, f_prima, meta_prima = risultati["prima"]
    voci = classifica(f_prima, f_dopo, baseline)
    for v in voci:
        v.update((meta.get((v["id"], v["purl"])) or meta_prima.get((v["id"], v["purl"])) or {"cvss": None, "cwe": []}))
    rep.update({"db": db_prima, "sbom": inv_dopo, "voci": voci,
                "baseline": {"path": cfg.get("sca_baseline") or BASELINE_DEFAULT, "merge_base_factory": mb_factory,
                             "presente": baseline is not None, "scartati": scartati}})
    stati = {v["stato"] for v in voci}
    if NUOVO in stati:
        rep["esito"] = FAIL
    elif baseline is None:
        rep.update({"esito": NON_VERIFICABILE, "motivo": "nessun baseline al merge-base della factory: il primo "
                    "run non e' un PASS (US-425 AC3); il debito va accettato per nome"})
    elif DEBITO in stati:
        rep.update({"esito": NON_VERIFICABILE, "motivo": "vulnerabilita' presenti anche al merge-base e non nel "
                    "baseline: debito non nominato o DB aggiornato a commit fermo (riscansione, non FAIL)"})
    else:
        rep["esito"] = PASS
    return rep


def testo(rep):
    righe = ["[sca-guard] %s" % rep["esito"] + (" (severita' %s%s)" % (rep["severita"], ", non bloccante" if
             rep["esito"] == FAIL and rep["severita"] == "WARN" else "") if rep.get("severita") else "")
             + (": " + rep["motivo"] if rep.get("motivo") else "")]
    if "db" in rep:
        righe.append("  %s %s, DB %s, %d componenti nell'inventario" % (
            rep["tool"], rep["identita"].get("version"), rep["db"]["id"], len(rep["sbom"])))
        for v in rep["voci"]:
            righe.append("  %-22s %s %s" % (v["stato"], v["id"], v["purl"]))
        for r in rep["baseline"]["scartati"]:
            righe.append("  record scartato        %s: %s" % (r["id"], r["motivo"]))
    return "\n".join(righe)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("code_path")
    ap.add_argument("--root", default=".")
    ap.add_argument("--scanner", choices=sorted(SCANNER), default="osv-scanner")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        rep = esegui(a.code_path, a.root, a.scanner)
    except sg.Rifiuto as e:
        print("[sca-guard] RIFIUTATO: %s." % e)
        return ost.EXIT_RIFIUTO
    print(json.dumps(rep, indent=2, ensure_ascii=False) if a.json else testo(rep))
    if rep["esito"] == FAIL and rep.get("severita") == "WARN":
        return 0   # fino a sca_required_from il FAIL e' segnalato ma non blocca
    return EXIT_CODES[rep["esito"]]


if __name__ == "__main__":
    sys.exit(main())

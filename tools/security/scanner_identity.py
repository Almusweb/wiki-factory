#!/usr/bin/env python3
"""Risoluzione e identita' degli scanner di sicurezza (EP-109 US-424, decisione D7 = (b)).

Un esito di sicurezza vale solo per lo strumento dichiarato. Prima di dare un esito, ogni oracolo
chiede a questo modulo quale binario eseguire; il modulo risponde IDENTIFICATO con percorso
assoluto (dopo `realpath`), versione e sha256 confrontati coi valori fissati, oppure
NON_VERIFICABILE con un motivo. Mai PASS: questo modulo non scansiona nulla.

Decisione D7 (maintainer, 2026-11-19): percorso assoluto fissato piu' hash. Il PATH sceglie il
primo binario che trova, l'hash identifica il binario. Con un pin presente il PATH non si consulta.

Pin: file JSON `scanner_identity.pins` (default `security/scanner-pins.json`), letto con
`git show <merge-base>:<path>` dove il merge-base e' fra HEAD e `scanner_identity.ref_protetto`
(default `origin/main`). Mai dal working tree: un pin cambiato solo sul branch non vale, cosi' chi
sostituisce un binario non puo' ripinnarlo nello stesso branch. Formato:

    {"gitleaks": [{"path": "/opt/homebrew/bin/gitleaks", "sha256": "<64 hex>",
                   "version": "8.30.1", "nota": "macOS, Homebrew"}]}

Piu' voci per scanner = piu' macchine o piattaforme ammesse; si provano in ordine.

Motivi di NON_VERIFICABILE (codice stabile, messaggio per umani):
    assente               con pin: nessun percorso fissato esiste o e' eseguibile;
                          senza pin: binario ne' nel PATH ne' nei percorsi noti
    non_raggiungibile     senza pin: il binario esiste in un percorso noto ma il PATH del processo
                          non lo vede (rimedio: PATH della sessione, poi un pin)
    identita_divergente   con pin: il file esiste ma sha256 (o versione dichiarata) non coincide
    identita_non_fissata  nessun pin valido per lo scanner (assente, incompleto o illeggibile):
                          il binario puo' anche esserci, ma la sua identita' non e' dichiarata

Cosa si hasha (AC2), per tipo di scanner (tabella COSA_SI_HASHA):
    binario           gitleaks, osv-scanner, trivy: il file risolto con realpath
    entrypoint-python semgrep da pip, pipx o Homebrew: digest composto di quattro artefatti,
                      ciascuno col proprio sha256: lo script di avvio (realpath), l'interprete del
                      suo shebang (realpath; lo shebang con `env` non e' identificabile), il motore
                      `semgrep/bin/semgrep-core` e il RECORD del dist-info, o METADATA dove manca
                      (Homebrew). Trovati sul filesystem accanto al percorso dello shebang, senza
                      eseguire nulla.

La versione si legge eseguendo lo scanner solo DOPO che lo sha256 coincide: un binario non
identificato non si esegue. Se il pin dichiara una versione, versione diversa o illeggibile =
identita_divergente.

Cosa NON garantisce:
- un binario identificato non e' uno scanner corretto ne' completo;
- semgrep: il RECORD elenca gli hash dei file del pacchetto (anche `semgrep-core`) ma questo modulo
  non li ricontrolla uno per uno: l'identita' di semgrep e' provata solo in parte;
- un agente con Bash puo' eseguire lo scanner fuori dall'oracolo, o un altro binario;
- fra l'hash e l'esecuzione il file puo' cambiare (TOCTOU): l'hash prova il file letto, non quello
  eseguito un istante dopo;
- il pin e' una traccia, non una firma: chi scrive sul ref protetto puo' cambiarlo;
- in CI gitleaks si installa in una cartella temporanea (`$RUNNER_TEMP`): il percorso non e'
  fissabile, la CI verifica lo sha256 dell'archivio scaricato, non passa da qui.

CLI:
    scanner_identity.py [--root R] [--json] [scanner ...]     exit 0 tutti IDENTIFICATI, 3 altrimenti
    scanner_identity.py --misura SCANNER --path P             stampa un pin proposto (ESEGUE P per
                                                              leggerne la versione: atto del maintainer)
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config_ancorata  # noqa: E402

IDENTIFICATO = "IDENTIFICATO"
NON_VERIFICABILE = "NON_VERIFICABILE"

ASSENTE = "assente"
NON_RAGGIUNGIBILE = "non_raggiungibile"
DIVERGENTE = "identita_divergente"
NON_FISSATA = "identita_non_fissata"

MOTIVI = {
    ASSENTE: "assente",
    NON_RAGGIUNGIBILE: "non raggiungibile dal PATH del processo",
    DIVERGENTE: "identita' divergente",
    NON_FISSATA: "identita' non fissata",
}

EXIT_CODES = {IDENTIFICATO: 0, NON_VERIFICABILE: 3}

PINS_DEFAULT = "security/scanner-pins.json"
REF_PROTETTO_DEFAULT = "origin/main"
TIMEOUT_VERSIONE = 20

BINARIO = "binario"
ENTRYPOINT_PYTHON = "entrypoint-python"

SCANNER = {
    "gitleaks": {"tipo": BINARIO, "versione": ["version"]},
    "osv-scanner": {"tipo": BINARIO, "versione": ["--version"]},
    "trivy": {"tipo": BINARIO, "versione": ["--version"]},
    "semgrep": {"tipo": ENTRYPOINT_PYTHON, "versione": ["--version"], "dist": "semgrep", "motore": "semgrep-core"},
}

COSA_SI_HASHA = {
    BINARIO: "il file risolto con realpath",
    ENTRYPOINT_PYTHON: ("digest composto: script di avvio (realpath), interprete del suo shebang "
                        "(realpath), motore semgrep-core, RECORD (o METADATA) del dist-info; identita' "
                        "parziale: gli altri file Python del pacchetto non sono ricontrollati"),
}

# Dove uno scanner si trova di solito quando c'e' ma il PATH del processo non lo vede. Servono solo a
# dire la causa, mai a eseguire da li'.
PERCORSI_NOTI = ("/opt/homebrew/bin", "/usr/local/bin", "/home/linuxbrew/.linuxbrew/bin",
                 os.path.expanduser("~/.local/bin"), "/snap/bin")

_SHA = re.compile(r"^[0-9a-f]{64}$")
_VERSIONE = re.compile(r"(\d+\.\d+\.\d+)")


class Identita:
    """Esito della risoluzione di uno scanner. `report()` e' cio' che l'oracolo scrive nel report."""

    def __init__(self, scanner, stato, motivo=None, messaggio="", path=None, realpath=None,
                 version=None, sha256=None, artefatti=None, pin=None):
        self.scanner = scanner
        self.stato = stato
        self.motivo = motivo
        self.messaggio = messaggio
        self.path = path
        self.realpath = realpath
        self.version = version
        self.sha256 = sha256
        self.artefatti = artefatti or []
        self.pin = pin

    @property
    def identificato(self):
        return self.stato == IDENTIFICATO

    def report(self):
        tipo = SCANNER.get(self.scanner, {}).get("tipo")
        return {
            "scanner": self.scanner,
            "stato": self.stato,
            "motivo": self.motivo,
            "messaggio": self.messaggio,
            "path": self.path,
            "realpath": self.realpath,
            "version": self.version,
            "sha256": self.sha256,
            "cosa_si_hasha": COSA_SI_HASHA.get(tipo),
            "artefatti": self.artefatti,
            "pin": self.pin,
        }

    def riga(self):
        if self.identificato:
            return "[scanner-identity] %s: IDENTIFICATO %s (versione %s, sha256 %s)" % (
                self.scanner, self.realpath, self.version or "non dichiarata", self.sha256[:12])
        return "[scanner-identity] %s: NON_VERIFICABILE (%s): %s" % (
            self.scanner, MOTIVI.get(self.motivo, self.motivo), self.messaggio)


def _nv(scanner, motivo, messaggio, **kw):
    return Identita(scanner, NON_VERIFICABILE, motivo, messaggio, **kw)


# --- config e pin ---------------------------------------------------------------------------

def _git(root, *args):
    try:
        r = subprocess.run(["git", "-C", str(root)] + list(args),
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError:
        return None, b""
    return r.returncode, r.stdout


def leggi_pins(root):
    """(dict scanner -> lista di voci, spiegazione). Dal merge-base con il ref protetto, mai dal
    working tree: anche `pins` e `ref_protetto` si leggono dall'ancora (config_ancorata), perche' un
    `ref_protetto: HEAD` non committato farebbe venire i pin dal branch. Dict vuoto se l'ancora o il
    ref non si risolvono, il file manca o non e' JSON valido."""
    cfg, ref, mb, spiega = config_ancorata.blocco(root, "scanner_identity")
    if cfg is None:
        return {}, spiega + ": nessun pin leggibile"
    path = cfg.get("pins") or PINS_DEFAULT
    rc, dati = _git(root, "show", "%s:%s" % (mb, path))
    if rc != 0:
        return {}, "nessun file di pin %s al merge-base con %s (%s)" % (path, ref, mb[:8])
    try:
        voci = json.loads(dati.decode("utf-8"))
    except ValueError:
        return {}, "%s al merge-base con %s non e' JSON valido: nessun pin" % (path, ref)
    if not isinstance(voci, dict):
        return {}, "%s al merge-base con %s non e' un oggetto JSON: nessun pin" % (path, ref)
    return voci, "pin letti da %s al merge-base con %s (%s)" % (path, ref, mb[:8])


def _pin_valido(voce):
    """None se la voce e' un pin completo, altrimenti il motivo per cui non lo e'."""
    if not isinstance(voce, dict):
        return "voce non e' un oggetto"
    p = voce.get("path")
    if not isinstance(p, str) or not os.path.isabs(p):
        return "path mancante o non assoluto"
    s = voce.get("sha256")
    if not isinstance(s, str) or not _SHA.match(s.strip().lower()):
        return "sha256 mancante o non di 64 cifre esadecimali (un pin senza hash non e' un pin)"
    v = voce.get("version")
    if v is not None and not isinstance(v, str):
        return "version non e' una stringa"
    return None


# --- misura dell'identita' (senza eseguire) ---------------------------------------------------

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blocco in iter(lambda: fh.read(1 << 20), b""):
            h.update(blocco)
    return h.hexdigest()


def _interprete_shebang(script):
    """(percorso dello shebang, percorso risolto) dell'interprete, o (None, None).

    Il percorso dello shebang serve a trovare il site-packages (in un venv o con pipx `bin/python` e'
    un symlink verso il Python di sistema, ma il pacchetto sta nel venv); quello risolto e' il file
    che si hasha."""
    try:
        with open(script, "rb") as fh:
            prima = fh.readline(4096)
    except OSError:
        return None, None
    if not prima.startswith(b"#!"):
        return None, None
    parti = prima[2:].decode("utf-8", "replace").strip().split()
    if not parti:
        return None, None
    if os.path.basename(parti[0]) == "env" or not os.path.isabs(parti[0]):
        # `#!/usr/bin/env python3` sceglie l'interprete dal PATH al momento dell'esecuzione: l'identita'
        # misurata non sarebbe quella eseguita (D7), quindi l'entrypoint non e' identificabile
        return None, None
    return parti[0], os.path.realpath(parti[0])


def _dist_info(interpreti, dist):
    """Cartella `dist-*.dist-info` nel site-packages del prefisso di uno degli interpreti (cartella sopra
    bin/): prima il percorso dello shebang (venv, pipx, Homebrew libexec), poi quello risolto. None se non
    trovata o ambigua."""
    for interprete in interpreti:
        prefisso = os.path.dirname(os.path.dirname(os.path.abspath(interprete)))
        candidati = sorted(set(
            glob.glob(os.path.join(prefisso, "lib", "python*", "site-packages", "%s-*.dist-info" % dist))
            + glob.glob(os.path.join(prefisso, "Lib", "site-packages", "%s-*.dist-info" % dist))))
        if len(candidati) == 1:
            return candidati[0]
        if len(candidati) > 1:
            return None
    return None


def misura(scanner, path):
    """(realpath, sha256, artefatti, errore). Nessuna esecuzione: solo lettura di file."""
    real = os.path.realpath(path)
    if not os.path.isfile(real) or not os.access(real, os.X_OK):
        return real, None, [], "%s non esiste o non e' eseguibile" % path
    tipo = SCANNER[scanner]["tipo"]
    if tipo == BINARIO:
        sha = sha256_file(real)
        return real, sha, [{"ruolo": "binario", "path": real, "sha256": sha}], None
    # entrypoint-python
    shebang, interprete = _interprete_shebang(real)
    if not interprete or not os.path.isfile(interprete):
        return real, None, [], ("shebang di %s non identificabile: con `env` (o un percorso relativo) "
                                "l'interprete lo sceglie il PATH al momento dell'esecuzione (D7), oppure "
                                "non porta a un interprete leggibile" % real)
    dist_info = _dist_info([shebang, interprete], SCANNER[scanner]["dist"])
    if not dist_info:
        return real, None, [], ("dist-info %s-* non trovato (o ambiguo) accanto a %s"
                                % (SCANNER[scanner]["dist"], shebang))
    # manifest: RECORD (hash dei file del pacchetto) se c'e'; Homebrew lo omette, allora METADATA
    manifest = next((os.path.join(dist_info, m) for m in ("RECORD", "METADATA")
                     if os.path.isfile(os.path.join(dist_info, m))), None)
    core = os.path.join(os.path.dirname(dist_info), SCANNER[scanner]["dist"], "bin", SCANNER[scanner]["motore"])
    if not manifest or not os.path.isfile(core):
        return real, None, [], ("pacchetto %s incompleto: manca %s" % (
            SCANNER[scanner]["dist"], "RECORD/METADATA" if not manifest else core))
    artefatti = [
        {"ruolo": "entrypoint", "path": real, "sha256": sha256_file(real)},
        {"ruolo": "interprete", "path": interprete, "sha256": sha256_file(interprete)},
        {"ruolo": "motore", "path": os.path.realpath(core), "sha256": sha256_file(core)},
        {"ruolo": os.path.basename(manifest).lower(), "path": os.path.realpath(manifest),
         "sha256": sha256_file(manifest)},
    ]
    composto = hashlib.sha256("".join("%s %s\n" % (a["ruolo"], a["sha256"]) for a in artefatti)
                              .encode("ascii")).hexdigest()
    return real, composto, artefatti, None


def leggi_versione(scanner, real):
    """Versione x.y.z stampata dallo scanner, o None. ESEGUE il file: chiamarla solo dopo l'hash."""
    try:
        r = subprocess.run([real] + SCANNER[scanner]["versione"], stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, timeout=TIMEOUT_VERSIONE)
    except (OSError, subprocess.SubprocessError):
        return None
    m = _VERSIONE.search(r.stdout.decode("utf-8", "replace"))
    return m.group(1) if m else None


# --- risoluzione ------------------------------------------------------------------------------

def _senza_pin(scanner, spiegazione, percorsi_noti, env_path):
    trovato = shutil.which(scanner, path=env_path)
    if trovato:
        real, sha, artefatti, _ = misura(scanner, trovato)
        return _nv(scanner, NON_FISSATA,
                   "%s trovato nel PATH in %s ma la sua identita' non e' fissata (%s); D7: serve un "
                   "pin con percorso assoluto e sha256 (--misura)" % (scanner, trovato, spiegazione),
                   path=trovato, realpath=real, sha256=sha, artefatti=artefatti)
    for d in percorsi_noti:
        p = os.path.join(d, scanner)
        if os.path.isfile(p) and os.access(p, os.X_OK):
            return _nv(scanner, NON_RAGGIUNGIBILE,
                       "%s presente in %s ma non raggiungibile dal PATH del processo, e nessun pin "
                       "(%s)" % (scanner, p, spiegazione), path=p)
    return _nv(scanner, ASSENTE, "%s ne' nel PATH ne' nei percorsi noti, e nessun pin (%s)"
               % (scanner, spiegazione))


def identifica(scanner, root=".", percorsi_noti=None, env_path=None):
    """Identita' di `scanner` secondo la decisione D7. `env_path` default: PATH del processo."""
    if scanner not in SCANNER:
        raise ValueError("scanner sconosciuto: %s (noti: %s)" % (scanner, ", ".join(sorted(SCANNER))))
    percorsi_noti = PERCORSI_NOTI if percorsi_noti is None else percorsi_noti
    env_path = os.environ.get("PATH", "") if env_path is None else env_path
    pins, spiegazione = leggi_pins(root)
    voci = pins.get(scanner)
    if voci is None:
        return _senza_pin(scanner, spiegazione, percorsi_noti, env_path)
    if not isinstance(voci, list) or not voci:
        return _nv(scanner, NON_FISSATA, "pin di %s non e' una lista non vuota (%s)" % (scanner, spiegazione))
    for voce in voci:
        errore = _pin_valido(voce)
        if errore:
            return _nv(scanner, NON_FISSATA, "pin di %s incompleto: %s (%s)" % (scanner, errore, spiegazione),
                       pin=voce if isinstance(voce, dict) else None)
    divergenze = []
    for voce in voci:
        path = voce["path"]
        if not os.path.isfile(os.path.realpath(path)) or not os.access(os.path.realpath(path), os.X_OK):
            continue
        real, sha, artefatti, errore = misura(scanner, path)
        if errore or sha != voce["sha256"].strip().lower():
            divergenze.append(_nv(
                scanner, DIVERGENTE,
                "%s in %s: %s" % (scanner, path, errore or "sha256 %s, fissato %s"
                                  % (sha, voce["sha256"].strip().lower())),
                path=path, realpath=real, sha256=sha, artefatti=artefatti, pin=voce))
            continue
        versione = leggi_versione(scanner, real)
        attesa = voce.get("version")
        if attesa and versione != attesa:
            divergenze.append(_nv(
                scanner, DIVERGENTE, "%s in %s: sha256 coincide ma versione %s, fissata %s"
                % (scanner, path, versione or "illeggibile", attesa),
                path=path, realpath=real, version=versione, sha256=sha, artefatti=artefatti, pin=voce))
            continue
        return Identita(scanner, IDENTIFICATO, None, spiegazione, path=path, realpath=real,
                        version=versione, sha256=sha, artefatti=artefatti, pin=voce)
    if divergenze:
        return divergenze[0]
    return _nv(scanner, ASSENTE, "nessuno dei percorsi fissati per %s esiste o e' eseguibile: %s (%s)"
               % (scanner, ", ".join(v["path"] for v in voci), spiegazione))


def proponi_pin(scanner, path, nota=""):
    """Pin proposto per `path`: misura e poi ESEGUE il file per la versione. Atto del maintainer."""
    real, sha, artefatti, errore = misura(scanner, path)
    if errore:
        raise ValueError(errore)
    voce = {"path": os.path.abspath(path), "sha256": sha, "version": leggi_versione(scanner, real)}
    if nota:
        voce["nota"] = nota
    return voce, artefatti


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("scanner", nargs="*", help="scanner da identificare (default: tutti)")
    ap.add_argument("--root", default=".")
    ap.add_argument("--json", action="store_true", help="report JSON (lista)")
    ap.add_argument("--misura", metavar="SCANNER", help="stampa un pin proposto per --path")
    ap.add_argument("--path", help="percorso del binario da misurare (con --misura)")
    ap.add_argument("--nota", default="", help="nota del pin proposto (con --misura)")
    a = ap.parse_args(argv)
    if a.misura:
        if a.misura not in SCANNER or not a.path:
            ap.error("--misura vuole uno scanner noto (%s) e --path" % ", ".join(sorted(SCANNER)))
        try:
            voce, artefatti = proponi_pin(a.misura, a.path, a.nota)
        except ValueError as e:
            print("[scanner-identity] %s" % e, file=sys.stderr)
            return 3
        print(json.dumps({a.misura: [voce], "_artefatti": artefatti}, indent=2, ensure_ascii=False))
        return 0
    nomi = a.scanner or sorted(SCANNER)
    for n in nomi:
        if n not in SCANNER:
            ap.error("scanner sconosciuto: %s (noti: %s)" % (n, ", ".join(sorted(SCANNER))))
    esiti = [identifica(n, a.root) for n in nomi]
    if a.json:
        print(json.dumps([e.report() for e in esiti], indent=2, ensure_ascii=False))
    else:
        for e in esiti:
            print(e.riga())
    return 0 if all(e.identificato for e in esiti) else EXIT_CODES[NON_VERIFICABILE]


if __name__ == "__main__":
    sys.exit(main())

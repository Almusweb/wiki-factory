#!/usr/bin/env python3
"""Oracolo unico dei segreti: delega a gitleaks, senza pattern propri.

Tre ingressi, un solo motore:
    scan(files, repo_root)   file del working tree (CI, lint): copia in una cartella
                             temporanea preservando i path relativi
    scan_staged(repo_root)   blob dell'indice git (pre-commit): `git diff --cached
                             --name-only -z --diff-filter=ACMR` e contenuto dal blob, quindi
                             un segreto in stage e poi tolto dal disco e' visto, le rinomine
                             sono coperte e i nomi non ASCII funzionano
    scan_storia(code_path)   storia git di un code_path dichiarato (EP-109 US-426): `gitleaks git`
                             (ripiego `detect`), solo sui `code_paths[].path` di factory.config.yaml; il
                             repo della factory e' rifiutato esplicitamente (stesso toplevel git, anche
                             se dichiarato come monorepo), fallendo chiuso se git non risponde
    CLI                      `secrets_guard.py [--staged] [--hook] [--storia CODE_PATH] [--root R] [file...]`

Modalita' storia: la config non e' quella del repo scansionato (un `.gitleaks.toml` del cliente potrebbe
allargare l'allowlist): si passa una config temporanea che estende solo le regole di default di gitleaks.
L'esito riporta per ogni finding solo commit, file, riga e regola (`--redact`, e il resto del report non
si stampa ne' si restituisce). Si scansiona un clone bare in una cartella temporanea, con
`--gitleaks-ignore-path` su una cartella vuota e `--ignore-gitleaks-allow`: ne' un `.gitleaksignore` del
working tree ne' un commento `gitleaks:allow` in un commit passato nascondono un segreto. Il clone e'
`--mirror` (tutti i ref, anche refs/remotes) e gitleaks gira con GIT_NO_REPLACE_OBJECTS=1. Un clone shallow
e' NON_VERIFICABILE. gitleaks si risolve con scanner_identity (D7: percorso fissato e sha256 dai pin
dell'ancora), non col PATH. Non vede lo stash ne' i diff dei merge commit (gitleaks usa `git log -p` senza
`-m`). Non revoca ne' ruota un segreto: nella storia e' gia' esposto.

Invocazione: `gitleaks dir` (8.19+), con ripiego su `detect --no-git` se `dir` non esiste;
`--config` esplicito solo se esiste un `.gitleaks.toml` committato alla radice (in modalita'
stage quello di HEAD, non quello in stage); `GITLEAKS_CONFIG` ripulito dall'ambiente del
sottoprocesso; `.gitleaks.toml` e `.gitleaksignore` non sono copiati nella sorgente
scansionata. Exit di gitleaks: 0 nessun finding, 1 finding, altro = errore.

Esiti e exit code della CLI:
    PASS             0  gitleaks ha girato su almeno un file e non ha trovato nulla
    FAIL             1  gitleaks ha trovato almeno un segreto
    (uso errato)     2  argomenti non validi (argparse)
    NON_VERIFICABILE 3  nessuna verifica avvenuta: gitleaks assente o in errore, report
                        illeggibile, zero file leggibili, root non git. Mai PASS (fail-closed).
I symlink si saltano e si contano come non verificati (dichiarato nel messaggio).

Severita': WARN di default; ERROR solo se `secrets_guard.required_from` (AAAA-MM-GG)
e' presente e <= oggi. Il blocco assente equivale a spento.

Con `--hook` (pre-commit; senza `--staged` esplicito vale `--staged`):
    FAIL + ERROR               blocca (exit 1)
    NON_VERIFICABILE + ERROR   blocca (exit 1), salvo un record di deroga valido (sotto)
    a severita' WARN           non blocca e lo dice: «commit NON bloccato»

Deroga (EP-108 US-423): un record nel file `secrets_guard.deroghe` (default
`security/secrets-guard-deroghe.json`), letto con `git show <merge-base>:<path>` dove il
merge-base e' fra HEAD e `secrets_guard.ref_protetto` (default `origin/main`). Mai dal
working tree ne' dal branch in esame: una deroga committata solo sul branch non vale.
Il file e' una lista JSON di record con `motivo`, `scadenza` (AAAA-MM-GG, inclusa),
`approvato_da`, `riferimento_gate` non vuoti; scaduto o incompleto vale come assente.
Campo facoltativo `ambito`: `non_verificabile` (default) o `config_gitleaks`; un record copre
solo il proprio ambito. La deroga copre NON_VERIFICABILE o una modifica di `.gitleaks.toml`, mai
un FAIL.

Modifica di `.gitleaks.toml` in stage (EP-108 US-422): l'hook la segnala sempre, perche' dal
commit successivo la nuova allowlist vale per la scansione (bypass in due commit). A severita'
ERROR blocca, salvo un record con `ambito: config_gitleaks`. In CI `--config-diff BASE` stampa
il diff come annotazione `::warning` nelle PR: segnala, non blocca. La variabile SECRETS_GUARD_OVERRIDE non e'
piu' letta: se e' impostata, l'output lo dice. Il record e' una traccia, non una firma:
chi puo' scrivere sul ref protetto puo' produrlo.

NON_VERIFICABILE per binario mancante dice la causa: «gitleaks assente» oppure «gitleaks
presente in <percorso> ma non raggiungibile dal PATH del processo» (percorsi noti:
PERCORSI_NOTI). Le due cause chiedono rimedi diversi (installazione contro PATH).
Con `secrets_guard.enabled` diverso da true `--hook` non fa nulla. Nulla in stage da
verificare (solo cancellazioni, commit vuoto): exit 0 dichiarato, nessuna verifica millantata.

La guardia previene nel percorso cooperativo, rileva negli altri: --no-verify e
core.hooksPath la aggirano, e gitleaks ha falsi negativi.
"""
import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


PASS = "PASS"
FAIL = "FAIL"
NON_VERIFICABILE = "NON_VERIFICABILE"

EXIT_CODES = {PASS: 0, FAIL: 1, NON_VERIFICABILE: 3}

DICHIARAZIONE = "previene nel percorso cooperativo, rileva negli altri"


class Esito(object):
    def __init__(self, stato, messaggio, findings=None):
        self.stato = stato
        self.messaggio = messaggio
        self.findings = findings or []
        self.n_file = 0

    @property
    def exit_code(self):
        return EXIT_CODES[self.stato]

    def __repr__(self):
        return "Esito(%s)" % self.stato


def _blocco_config(root):
    """Dict {chiave: valore} del blocco `secrets_guard:`; vuoto se assente."""
    cfg = Path(root) / "factory.config.yaml"
    out = {}
    if not cfg.exists():
        return out
    in_blocco = False
    for line in cfg.read_text(encoding="utf-8", errors="replace").splitlines():
        if re.match(r"^secrets_guard:\s*(#.*)?$", line):
            in_blocco = True
            continue
        if in_blocco:
            if line.strip() and not line.startswith((" ", "\t", "#")):
                break
            m = re.match(r"^\s+([A-Za-z_]+):\s*[\"']?([^\"'#\s]*)", line)
            if m:
                out[m.group(1)] = m.group(2)
    return out


def enabled(root):
    return _blocco_config(root).get("enabled", "").lower() == "true"


def required_from(root):
    """Valore di secrets_guard.required_from, o None se blocco o chiave mancano."""
    v = _blocco_config(root).get("required_from", "")
    return None if v in ("", "null", "~") else v


def severita(root, oggi=None):
    """'ERROR' se required_from e' una data ISO <= oggi, altrimenti 'WARN'."""
    rf = required_from(root)
    if not rf:
        return "WARN"
    try:
        da = datetime.date.fromisoformat(rf)
    except ValueError:
        return "WARN"
    oggi = oggi or datetime.date.today()
    return "ERROR" if da <= oggi else "WARN"


CONFIG_ESCLUSI = (".gitleaks.toml", ".gitleaksignore")
ENV_PULITE = ("GITLEAKS_CONFIG", "GITLEAKS_CONFIG_TOML")
OVERRIDE_ENV = "SECRETS_GUARD_OVERRIDE"   # non piu' letta (US-423): la si nomina solo per dirlo
DEROGHE_DEFAULT = "security/secrets-guard-deroghe.json"
REF_PROTETTO_DEFAULT = "origin/main"
CAMPI_DEROGA = ("motivo", "scadenza", "approvato_da", "riferimento_gate")
# Dove gitleaks si trova di solito quando c'e' ma il PATH del processo non lo vede (sessioni
# agentiche con PATH ridotto). Serve solo a dire la causa, mai a eseguirlo da li'.
PERCORSI_NOTI = ("/opt/homebrew/bin", "/usr/local/bin", "/home/linuxbrew/.linuxbrew/bin",
                 os.path.expanduser("~/.local/bin"), "/snap/bin")


def _scrivi(dest, rel, dati):
    tgt = Path(dest) / rel
    tgt.parent.mkdir(parents=True, exist_ok=True)
    with open(str(tgt), "wb") as fh:
        fh.write(dati)


def _git(root, *args):
    """(returncode, stdout bytes) di git -C root ...; (None, b'') se git non e' eseguibile."""
    try:
        r = subprocess.run(["git", "-C", str(root)] + list(args),
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError:
        return None, b""
    return r.returncode, r.stdout


def _nv(motivo):
    return Esito(NON_VERIFICABILE,
                 "NON_VERIFICABILE: %s. Nessuna verifica dei segreti e' avvenuta (%s)."
                 % (motivo, DICHIARAZIONE))


def causa_binario_mancante(percorsi=None):
    """Motivo di NON_VERIFICABILE quando `shutil.which` non trova gitleaks.

    Distingue il binario assente da quello presente in un percorso noto ma fuori dal PATH del
    processo: il primo si risolve installando, il secondo correggendo il PATH della sessione."""
    for d in (PERCORSI_NOTI if percorsi is None else percorsi):
        p = os.path.join(d, "gitleaks")
        if os.path.isfile(p) and os.access(p, os.X_OK):
            return ("gitleaks presente in %s ma non raggiungibile dal PATH del processo "
                    "(aggiungi %s al PATH della sessione)" % (p, d))
    return "gitleaks assente (non nel PATH ne' nei percorsi noti): va installato"


def _record_valido(r, oggi):
    if not isinstance(r, dict):
        return False
    for c in CAMPI_DEROGA:
        if not isinstance(r.get(c), str) or not r[c].strip():
            return False
    try:
        return datetime.date.fromisoformat(r["scadenza"].strip()) >= oggi
    except ValueError:
        return False


def deroga(root, oggi=None, ambito="non_verificabile"):
    """(record valido o None, spiegazione). Legge il file di deroga dal merge-base fra HEAD e il
    ref protetto, mai dal working tree ne' dal branch: una deroga solo sul branch non vale.

    `ambito` del record (default `non_verificabile`): `non_verificabile` copre l'assenza di verifica,
    `config_gitleaks` una modifica di `.gitleaks.toml`. Un record copre solo il proprio ambito."""
    # `deroghe` e `ref_protetto` dall'ancora, non dal factory.config.yaml su disco: un `ref_protetto: HEAD`
    # non committato farebbe valere una deroga committata solo sul branch (CQRL EP-109 iter-1)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import config_ancorata  # import locale: l'hook senza deroga non dipende da altri file
    cfg, ref, mb, spiega = config_ancorata.blocco(root, "secrets_guard")
    if cfg is None:
        return None, spiega + ": nessuna deroga leggibile"
    path = cfg.get("deroghe") or DEROGHE_DEFAULT
    rc, dati = _git(root, "show", "%s:%s" % (mb, path))
    if rc != 0:
        return None, ("nessun record di deroga in %s al merge-base con %s (%s)" % (path, ref, mb[:8]))
    try:
        voci = json.loads(dati.decode("utf-8"))
    except ValueError:
        return None, "%s al merge-base con %s non e' JSON valido: nessuna deroga" % (path, ref)
    if isinstance(voci, dict):
        voci = voci.get("deroghe", [])
    oggi = oggi or datetime.date.today()
    for r in (voci if isinstance(voci, list) else []):
        if _record_valido(r, oggi) and str(r.get("ambito") or "non_verificabile") == ambito:
            return r, ("letta da %s al merge-base con %s (%s)" % (path, ref, mb[:8]))
    return None, ("in %s al merge-base con %s nessun record valido con ambito %s (servono %s non "
                  "vuoti e scadenza non passata)" % (path, ref, ambito, ", ".join(CAMPI_DEROGA)))


CONFIG_GITLEAKS = ".gitleaks.toml"
AVVISO_CONFIG = ("AVVISO: %s e' modificato in questo commit. La scansione di questo commit usa la "
                 "versione di HEAD, ma dal commit successivo vale la nuova: un'allowlist allargata qui "
                 "spegne la verifica dopo (bypass in due commit). Il diff va rivisto da un umano." % CONFIG_GITLEAKS)


def config_diff(root, base):
    """Diff di `.gitleaks.toml` fra il merge-base con `base` e HEAD ('' se invariato, None se `base`
    non si risolve). Per la CI: rende visibile una modifica della config nelle PR."""
    rc, out = _git(root, "merge-base", "HEAD", base)
    if rc != 0 or not out.strip():
        return None
    mb = out.decode("ascii", "replace").strip()
    rc, diff = _git(root, "diff", "--no-color", mb, "HEAD", "--", CONFIG_GITLEAKS)
    if rc != 0:
        return None
    return diff.decode("utf-8", "replace")


def _supporta_dir(exe):
    try:
        r = subprocess.run([exe, "dir", "--help"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError:
        return False
    return r.returncode == 0


def _supporta(exe, sub):
    try:
        r = subprocess.run([exe, sub, "--help"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError:
        return False
    return r.returncode == 0


def _rimappa(path, basi):
    """Path del finding relativo alla sorgente scansionata (non alla cartella temporanea)."""
    for b in basi:
        if path.startswith(b + os.sep):
            return path[len(b) + 1:]
    return path


def _esegui_gitleaks(exe, src, tmp, config, n_file, n_saltati):
    report = os.path.join(tmp, "report.json")
    comune = ["--report-format", "json", "--report-path", report, "--exit-code", "1",
              "--no-banner", "--redact"]
    if config:
        comune += ["--config", config]
    if _supporta_dir(exe):
        cmd = [exe, "dir"] + comune + ["."]
    else:
        cmd = [exe, "detect", "--no-git", "--source", "."] + comune
    env = dict((k, v) for k, v in os.environ.items() if k not in ENV_PULITE)
    try:
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           universal_newlines=True, encoding="utf-8", errors="replace",
                           cwd=src, env=env)
    except OSError as e:
        return _nv("gitleaks non eseguibile (%s)" % e)
    if r.returncode not in (0, 1):
        return _nv("gitleaks e' terminato con errore (exit %d)" % r.returncode)
    findings = None
    if os.path.exists(report):
        try:
            with open(report, encoding="utf-8") as fh:
                findings = json.load(fh)
            if findings is None:
                findings = []
            if not isinstance(findings, list):
                raise ValueError("report non e' una lista")
        except (ValueError, OSError):
            return _nv("report di gitleaks illeggibile")
    elif r.returncode == 0:
        findings = []  # versioni che non scrivono il report senza finding
    else:
        return _nv("gitleaks ha segnalato finding ma senza report")
    basi = (src, os.path.realpath(src))
    for f in findings:
        if isinstance(f, dict) and isinstance(f.get("File"), str):
            f["File"] = _rimappa(f["File"], basi)
    extra = ""
    if n_saltati:
        extra = ", %d symlink o voci non verificati" % n_saltati
    if findings:
        e = Esito(FAIL, "FAIL: %d segreto/i rilevato/i da gitleaks su %d file%s (%s)."
                  % (len(findings), n_file, extra, DICHIARAZIONE), findings)
        e.n_file = n_file
        return e
    if r.returncode == 1:
        return _nv("gitleaks exit 1 con report vuoto")
    e = Esito(PASS, "PASS: gitleaks: nessun finding su %d file%s (%s)."
              % (n_file, extra, DICHIARAZIONE))
    e.n_file = n_file
    return e


# --- modalita' storia (EP-109 US-426) ----------------------------------------------------------

CAMPI_STORIA = ("Commit", "File", "StartLine", "RuleID")
CONFIG_SOLO_DEFAULT = "[extend]\nuseDefault = true\n"
RADICE_FACTORY = Path(__file__).resolve().parents[2]


class _ToplevelNonVerificabile(Exception):
    pass


def _common_dir(path):
    """Cartella git comune (condivisa dai worktree collegati), assoluta e risolta; None se non e' un repo."""
    try:
        r = subprocess.run(["git", "-C", str(path), "rev-parse", "--path-format=absolute", "--git-common-dir"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
    except (OSError, subprocess.SubprocessError) as e:
        raise _ToplevelNonVerificabile(str(e))
    if r.returncode != 0:
        return None
    return Path(r.stdout.decode("utf-8", "replace").strip()).resolve()


def _toplevel(path):
    try:
        r = subprocess.run(["git", "-C", str(path), "rev-parse", "--show-toplevel"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
    except (OSError, subprocess.SubprocessError) as e:
        raise _ToplevelNonVerificabile(str(e))
    if r.returncode != 0:
        return None
    return Path(r.stdout.decode("utf-8", "replace").strip()).resolve()


def code_paths_dichiarati(root):
    """Path (risolti rispetto a root) di `code_paths[].path` in factory.config.yaml."""
    cfg = Path(root) / "factory.config.yaml"
    if not cfg.exists():
        return []
    out = []
    in_blocco = False
    for line in cfg.read_text(encoding="utf-8", errors="replace").splitlines():
        if re.match(r"^code_paths:\s*(#.*)?$", line):
            in_blocco = True
            continue
        if in_blocco:
            if line.strip() and not line.startswith((" ", "\t", "#")):
                break
            m = re.match(r"^  (?:- |  )path:\s*[\"']?([^\"'#\s]+)", line)
            if m:
                out.append((Path(root) / m.group(1)).resolve())
    return out


def guardia_storia(code_path, root, radici_factory=None):
    """None se `code_path` si puo' scansionare, altrimenti il motivo del rifiuto.

    Rifiuta il repo della factory (stesso toplevel git di `root` o della factory che contiene questo
    script) anche se dichiarato, e ogni path non dichiarato in `code_paths[]`. Fallisce chiusa: se git
    non risponde il path si rifiuta."""
    p = Path(code_path).resolve()
    radici = radici_factory or [Path(root).resolve(), RADICE_FACTORY]
    try:
        top = _toplevel(p) if p.exists() else None
        comune = _common_dir(p) if top is not None else None
        # stesso toplevel o stessa cartella git comune: un `git worktree add` della factory ha un toplevel
        # diverso ma la stessa storia (CQRL EP-109 iter-1)
        if any(p == r for r in radici) or (top is not None and (
                any(top == _toplevel(r) for r in radici)
                or any(comune is not None and comune == _common_dir(r) for r in radici))):
            return ("%s e' il repo della factory: la modalita' storia scansiona solo i code_path del cliente "
                    "(rifiuto esplicito, come ai_policy_check)" % code_path)
    except _ToplevelNonVerificabile as e:
        return "guardia di scope non verificabile per %s (%s): rifiutato per sicurezza" % (code_path, e)
    if p not in code_paths_dichiarati(root):
        return "%s non e' dichiarato in code_paths[] di factory.config.yaml: rifiutato" % code_path
    if top is None:
        return "%s non e' un repo git: nessuna storia da scansionare" % code_path
    return None


class Rifiuto(Exception):
    pass


def _gitleaks_identificato(root):
    """(percorso eseguibile, None) del gitleaks identificato con scanner_identity (D7), o (None, Esito NV).

    Import locale: l'hook pre-commit (scan_staged) non dipende da scanner_identity."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import scanner_identity
    ident = scanner_identity.identifica("gitleaks", root)
    if not ident.identificato:
        return None, _nv("gitleaks non identificato (D7): %s" % ident.messaggio)
    return ident.realpath, None


def _gitleaks_su_mirror(exe, orig, tmp):
    """(returncode, finding grezzi) di gitleaks su un clone --mirror di `orig` in `tmp`, o (None, Esito NV).

    Clone in una cartella temporanea: gitleaks non vede il working tree del cliente, quindi un
    `.gitleaksignore` (anche non tracciato) li' non spegne nulla (CQRL iter-1). --mirror e non --bare:
    --bare non copia refs/remotes/* (iter-2). GIT_NO_REPLACE_OBJECTS=1: un `git replace` non nasconde
    il commit col segreto (iter-2)."""
    src = os.path.join(tmp, "storia.git")
    rc, _ = _git(tmp, "clone", "-q", "--mirror", "--no-local", "--", orig, src)
    if rc != 0:
        return None, _nv("clone --mirror di %s fallito" % orig)
    vuota = os.path.join(tmp, "nessun-ignore")
    os.mkdir(vuota)
    report = os.path.join(tmp, "report.json")
    config = os.path.join(tmp, "solo-default.toml")
    with open(config, "w", encoding="utf-8") as fh:
        fh.write(CONFIG_SOLO_DEFAULT)
    comune = ["--report-format", "json", "--report-path", report, "--exit-code", "1", "--no-banner",
              "--redact", "--config", config, "--gitleaks-ignore-path", vuota, "--ignore-gitleaks-allow"]
    cmd = ([exe, "git"] + comune + [src]) if _supporta(exe, "git") else ([exe, "detect", "--source", src] + comune)
    env = dict((k, v) for k, v in os.environ.items() if k not in ENV_PULITE)
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    try:
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=vuota,
                           universal_newlines=True, encoding="utf-8", errors="replace", env=env)
    except OSError as e:
        return None, _nv("gitleaks non eseguibile (%s)" % e)
    if r.returncode not in (0, 1):
        return None, _nv("gitleaks e' terminato con errore (exit %d)" % r.returncode)
    if not os.path.exists(report):
        return (0, []) if r.returncode == 0 else (None, _nv("gitleaks ha segnalato finding ma senza report"))
    try:
        with open(report, encoding="utf-8") as fh:
            grezzi = json.load(fh) or []
    except (ValueError, OSError):
        return None, _nv("report di gitleaks illeggibile")
    if not isinstance(grezzi, list):
        return None, _nv("report di gitleaks illeggibile")
    return r.returncode, grezzi


def scan_storia(code_path, root):
    """Esito della scansione della storia git di `code_path`. Solleva Rifiuto fuori perimetro."""
    motivo = guardia_storia(code_path, root)
    if motivo:
        raise Rifiuto(motivo)
    exe, nv = _gitleaks_identificato(root)
    if nv:
        return nv
    orig = str(Path(code_path).resolve())
    rc, out = _git(orig, "rev-parse", "--is-shallow-repository")
    if rc != 0 or out.strip() != b"false":
        return _nv("%s e' un clone shallow (o git non risponde): la storia non e' completa e nessun PASS "
                   "e' dichiarabile; serve `git fetch --unshallow`" % code_path)
    with tempfile.TemporaryDirectory(prefix="secrets-guard-storia-") as tmp:
        rc, grezzi = _gitleaks_su_mirror(exe, orig, tmp)
    if rc is None:
        return grezzi
    findings = [dict((k, f.get(k)) for k in CAMPI_STORIA) for f in grezzi if isinstance(f, dict)]
    if findings:
        return Esito(FAIL, "FAIL: %d segreto/i nella storia git di %s (gitleaks, regole di default; il "
                     "segreto e' gia' esposto: va revocato, non solo rimosso)." % (len(findings), code_path),
                     findings)
    if rc == 1:
        return _nv("gitleaks exit 1 con report vuoto")
    return Esito(PASS, "PASS: gitleaks: nessun finding nella storia git di %s (regole di default; %s)."
                 % (code_path, DICHIARAZIONE))


def _config_committata(root, da_head):
    """Contenuto di `.gitleaks.toml` alla radice: di HEAD in modalita' stage, del disco altrimenti."""
    if da_head:
        rc, out = _git(root, "show", "HEAD:.gitleaks.toml")
        return out if rc == 0 else None
    p = Path(root) / ".gitleaks.toml"
    if p.is_file() and not p.is_symlink():
        return p.read_bytes()
    return None


def _scansiona(voci, root, da_head, saltati):
    """`voci`: iterabile di (rel, callable -> bytes). Materializza e lancia gitleaks."""
    exe = shutil.which("gitleaks")
    if not exe:
        return _nv(causa_binario_mancante())
    tmp = tempfile.mkdtemp(prefix="secrets-guard-")
    try:
        src = os.path.join(tmp, "src")
        os.makedirs(src)
        n = 0
        for rel, leggi in voci:
            if os.path.basename(rel) in CONFIG_ESCLUSI and os.sep not in rel.replace("/", os.sep):
                continue  # config di gitleaks alla radice: mai dentro la sorgente
            try:
                dati = leggi()
            except OSError:
                saltati += 1
                continue
            _scrivi(src, rel, dati)
            n += 1
        if n == 0:
            return _nv("nessun file leggibile da verificare (%d voci non verificate)" % saltati)
        config = None
        dati_cfg = _config_committata(root, da_head)
        if dati_cfg is not None:
            config = os.path.join(tmp, "gitleaks-config.toml")
            with open(config, "wb") as fh:
                fh.write(dati_cfg)
        return _esegui_gitleaks(exe, src, tmp, config, n, saltati)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def scan(files, repo_root):
    """Esito per i file indicati del working tree (path relativi alla radice)."""
    root = Path(repo_root)
    voci = []
    saltati = 0
    for f in files:
        p = Path(f)
        src = p if p.is_absolute() else root / p
        if os.path.islink(str(src)):
            saltati += 1
            continue
        if not src.is_file():
            continue
        try:
            rel = os.path.relpath(str(src.resolve()), str(root.resolve()))
        except ValueError:
            continue
        if rel.startswith(".."):
            continue  # fuori dal repo: mai copiato con collisioni di nome
        voci.append((rel, (lambda s=src: s.read_bytes())))
    return _scansiona(voci, repo_root, False, saltati)


def staged_entries(repo_root):
    """Voci ACMR dell'indice: lista di (path, sha, modo). None se non e' un repo git."""
    rc, out = _git(repo_root, "diff", "--cached", "--raw", "-z", "--no-abbrev",
                   "--diff-filter=ACMR")
    if rc != 0:
        return None
    tok = out.split(b"\0")
    voci = []
    i = 0
    while i < len(tok):
        t = tok[i]
        i += 1
        if not t.startswith(b":"):
            continue
        campi = t[1:].split()
        stato = campi[-1][:1]
        n = 2 if stato in (b"R", b"C") else 1
        if i + n > len(tok):
            break
        path = tok[i + n - 1]
        i += n
        voci.append((os.fsdecode(path), campi[3].decode("ascii"), campi[1].decode("ascii")))
    return voci


def scan_staged(repo_root):
    """Esito per i blob dell'indice git della radice indicata."""
    voci = staged_entries(repo_root)
    if voci is None:
        return _nv("la radice non e' un repository git")
    saltati = 0
    out = []
    for path, sha, modo in voci:
        if modo in ("120000", "160000"):  # symlink, submodule
            saltati += 1
            continue

        def leggi(sha=sha):
            rc, dati = _git(repo_root, "cat-file", "blob", sha)
            if rc != 0:
                raise OSError("blob illeggibile")
            return dati
        out.append((path, leggi))
    return _scansiona(out, repo_root, True, saltati)


def _stampa_findings(esito):
    for f in esito.findings:
        if isinstance(f, dict):
            commit = (" @%s" % f["Commit"][:12]) if isinstance(f.get("Commit"), str) else ""
            print("  - %s:%s %s%s" % (f.get("File", "?"), f.get("StartLine", "?"), f.get("RuleID", ""), commit))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Guardia dei segreti (gitleaks).")
    ap.add_argument("files", nargs="*", help="file del working tree da controllare")
    ap.add_argument("--root", default=".", help="radice del repo")
    ap.add_argument("--staged", action="store_true",
                    help="controlla i blob dell'indice git invece dei file indicati")
    ap.add_argument("--hook", action="store_true",
                    help="modalita' pre-commit: blocca FAIL e NON_VERIFICABILE a severita' ERROR")
    ap.add_argument("--config-diff", metavar="BASE",
                    help="CI: segnala (annotazione ::warning) una modifica di .gitleaks.toml rispetto a BASE")
    ap.add_argument("--storia", metavar="CODE_PATH",
                    help="scansiona la storia git di un code_path dichiarato (mai la factory)")
    a = ap.parse_args(argv)
    if a.storia:
        try:
            esito = scan_storia(a.storia, a.root)
        except Rifiuto as e:
            print("[secrets-guard] RIFIUTATO: %s." % e)
            return 2
        print("[secrets-guard] %s" % esito.messaggio)
        _stampa_findings(esito)
        return esito.exit_code
    if a.config_diff:
        d = config_diff(a.root, a.config_diff)
        if d is None:
            print("::warning title=secrets-guard::base %s non risolta: modifica di %s NON verificata"
                  % (a.config_diff, CONFIG_GITLEAKS))
        elif d.strip():
            print("::warning title=%s modificato::%s" % (CONFIG_GITLEAKS, AVVISO_CONFIG))
            print(d)
        else:
            print("[secrets-guard] %s invariato rispetto a %s." % (CONFIG_GITLEAKS, a.config_diff))
        return 0
    if a.hook and not enabled(a.root):
        return 0
    staged = a.staged or a.hook
    if staged:
        voci = staged_entries(a.root)
        if a.hook and voci is not None and not voci:
            print("[secrets-guard] nessun file in stage da verificare: nessuna verifica eseguita, "
                  "commit NON bloccato.")
            return 0
        if a.hook and voci and any(v[0] == CONFIG_GITLEAKS for v in voci):
            # EP-108 US-422: la modifica della config non passa mai in silenzio. A severita' ERROR
            # blocca, salvo un record di deroga con ambito config_gitleaks sul ref protetto.
            print("[secrets-guard] " + AVVISO_CONFIG)
            if severita(a.root) == "ERROR":
                rec, spiega = deroga(a.root, ambito="config_gitleaks")
                if rec is None:
                    print("[secrets-guard] commit bloccato (severita' ERROR): una modifica di %s richiede "
                          "un record di deroga con ambito config_gitleaks sul ref protetto: %s."
                          % (CONFIG_GITLEAKS, spiega))
                    return 1
                print("[secrets-guard] DEROGA DA RECORD per %s: %s (approvato_da %s, riferimento %s, "
                      "scade %s); traccia, non firma." % (CONFIG_GITLEAKS, rec["motivo"],
                                                          rec["approvato_da"], rec["riferimento_gate"],
                                                          rec["scadenza"]))
        if a.hook and voci and all(v[0] in CONFIG_ESCLUSI for v in voci):
            # la config di gitleaks alla radice non entra mai nella sorgente scansionata: senza
            # altri file non c'e' nulla da verificare
            print("[secrets-guard] in stage solo la configurazione di gitleaks: nessun file da "
                  "verificare, commit NON bloccato.")
            return 0
        esito = scan_staged(a.root)
    else:
        esito = scan(a.files, a.root)
    sev = severita(a.root)
    print("[secrets-guard] %s (severita' %s)" % (esito.messaggio, sev))
    _stampa_findings(esito)
    if not a.hook:
        return esito.exit_code
    if esito.stato == PASS:
        return 0
    bloccante = sev == "ERROR"
    if os.environ.get(OVERRIDE_ENV):
        print("[secrets-guard] %s e' impostata ma non e' piu' letta: una deroga e' un record "
              "committato sul ref protetto (EP-108 US-423)." % OVERRIDE_ENV)
    if esito.stato == NON_VERIFICABILE and bloccante:
        rec, spiega = deroga(a.root)
        if rec is not None:
            print("[secrets-guard] DEROGA DA RECORD: %s (approvato_da %s, riferimento %s, scade %s), %s. "
                  "Commit NON bloccato pur senza alcuna verifica dei segreti; il record e' una "
                  "traccia, non una firma." % (rec["motivo"], rec["approvato_da"],
                                               rec["riferimento_gate"], rec["scadenza"], spiega))
            return 0
        cfg = _blocco_config(a.root)
        print("[secrets-guard] commit bloccato (severita' ERROR). Per procedere senza verifica serve "
              "un record di deroga (%s) nel file %s committato sul ref protetto %s: %s."
              % (", ".join(CAMPI_DEROGA), cfg.get("deroghe") or DEROGHE_DEFAULT,
                 cfg.get("ref_protetto") or REF_PROTETTO_DEFAULT, spiega))
        return 1
    if bloccante:
        print("[secrets-guard] commit bloccato (severita' ERROR).")
        return 1
    print("[secrets-guard] severita' WARN: commit NON bloccato.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

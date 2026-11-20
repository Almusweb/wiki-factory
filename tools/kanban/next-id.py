#!/usr/bin/env python3
"""next-id.py — il prossimo identificativo libero, EP / US / TSK.

    python3 tools/kanban/next-id.py tsk [quanti]
    python3 tools/kanban/next-id.py tsk [quanti] --namespace UP   # factory con piu' code_path

**Perche' esiste.** La numerazione dei TSK e' globale ma viene allocata per-epica, e
quando due epiche si lavorano in parallelo nascono collisioni: nel repo ce ne sono
**19** (TSK-292..295 fra EP-039 ed EP-041, TSK-545..559 fra EP-060, EP-061 ed EP-062).
Due lavori diversi con lo stesso identificativo, per sempre.

Ci si casca in un modo preciso, e il 2026-09-23 ci e' cascato anche un agente: si
prende il massimo fra i TSK **aperti** invece che fra **tutti**, e i `cancelled` — che
in questo repo arrivano fino a TSK-632 — restano invisibili. Il massimo va cercato su
tutto, archivio compreso.

**Flag --namespace PREFIX** (EP-069 US-314, opt-in):
Senza questo flag, e senza il registro `management/kanban/id-registry.yaml`, il
comportamento e' identico a quello pre-US-314. Con il flag, lo script cerca file
`{PREFIX}-{TIPO}-*.md` e rispetta le prenotazioni dichiarate nel registro.

**Remoto.** Prima di calcolare, lo script fa `git fetch origin main` e unisce
agli ID del filesystem quelli presenti in `origin/main` (`git ls-tree`), cosi' un ID creato
da un'altra macchina e non ancora scaricato non viene riassegnato. Se il fetch non riesce
(offline, errore di rete) si continua con il filesystem locale (e con l'ultimo `origin/main`
gia' scaricato, se esiste) e lo si dichiara: su stderr una riga `# AVVISO ...` piu' la riga
leggibile da macchina `# next-id-remote: <stato>`; con `--json` lo stato e' nel documento.
Remote e branch si cambiano con `--remote` e `--branch` (default origin e main).
`--no-remote` (o `NEXT_ID_OFFLINE=1`) salta del tutto la lettura del remoto: stato `disabled`,
nessun avviso, calcolo sul solo filesystem.
Stati: `ok` (fetch riuscito), `disabled` (remoto escluso), `no-fetch` (richiesto con --no-fetch, si legge il ref locale),
`stale` (fetch fallito, ref locale vecchio usato), `unavailable` (nessun origin/main leggibile).
Lo stdout e l'exit code (0) restano quelli di prima; `--strict` esce con 3 se lo stato non
e' `ok`/`no-fetch`/`disabled`. Il registro `tsk-id-registry.yaml` non e' letto da qui.

**Prenotazioni nel namespace del master** (EP-107, richiede `kanban_namespaces.enabled: true`).
Una prenotazione con `prefix: ""` (o `prefix` assente) vale per gli ID senza prefisso. In modalita'
base il prossimo ID e' il massimo fra filesystem, remoto e `to` delle prenotazioni dello stesso
tipo, lette sia dal registro locale sia da quello su `origin/<branch>` (unione). Con
`--namespace` a flag acceso il massimo e' quello del prefisso fra filesystem, remoto e prenotazioni
con quel `prefix`, anch'esse unite fra registro locale e remoto; a flag spento il registro e'
quello locale, come prima.

    python3 tools/kanban/next-id.py tsk 3 --reserve --epic EP-108 [--dry-run] [--co-author "Nome <mail>"]

`--reserve` scrive la voce nel registro e la pubblica **sul branch del remoto** (default `main`)
senza toccare working tree ne' branch corrente: worktree temporaneo staccato sul remoto, commit
del solo registro, push `HEAD:<branch>`. Se il push e' rifiutato perche' il branch e' avanzato:
fetch, ricalcolo, nuovo tentativo (massimo 3); mai `--force`. Il co-autore arriva da `--co-author`
o da `NEXT_ID_CO_AUTHOR`. `--dry-run` stampa la voce senza commit ne' push.

Codici d'uscita di `--reserve`: 0 prenotato (o dry-run); 2 uso errato (flag spento, `--epic`
mancante o non valido, `quanti` < 1); 3 `origin/<branch>` non aggiornato, non si calcola su dati
vecchi; 4 errore (registro assente o non leggibile, scrittura non verificabile, worktree o commit
falliti, push rifiutato per ragioni diverse dal branch avanzato: hook, branch protetto, lock sul
ref); 5 tre tentativi falliti perche' il branch avanzava; 6 timeout del push, esito incerto: la
prenotazione potrebbe essere pubblicata, si verifica con `git fetch` prima di rilanciare.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parents[2]
PREFISSI = {"tsk": "TSK", "us": "US", "ep": "EP"}
REGISTRY_PATH = RADICE / "management" / "kanban" / "id-registry.yaml"
REMOTE = "origin"
BRANCH = "main"
REMOTE_REF = f"{REMOTE}/{BRANCH}"
KANBAN_REL = "management/kanban"
FETCH_TIMEOUT = 30
PUSH_TIMEOUT = 60
MAX_TENTATIVI = 3


# ---------------------------------------------------------------------------
# ID presenti sul branch remoto (default origin/main)
# ---------------------------------------------------------------------------

def _git(*args: str, timeout: int | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    return subprocess.run(["git", *args], cwd=RADICE, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", env=env, timeout=timeout)


def stems_remoti() -> list[str] | None:
    """Nomi (senza .md) dei file kanban su origin/main, None se il ref non si legge."""
    try:
        r = _git("ls-tree", "-r", "--name-only", REMOTE_REF, "--", KANBAN_REL)
    except OSError:
        return None
    if r.returncode != 0:
        return None
    return [Path(riga).stem for riga in r.stdout.splitlines() if riga.endswith(".md")]


def carica_remoto(fetch: bool = True, enabled: bool = True) -> tuple[list[str], str, str]:
    """(stems, stato, dettaglio). Mai eccezioni: l'assenza di rete e' uno stato.

    Con enabled=False non tocca ne' la rete ne' il ref: stato `disabled`."""
    if not enabled:
        return [], "disabled", ""
    dettaglio = ""
    stato = "no-fetch"
    if fetch:
        try:
            r = _git("fetch", "-q", REMOTE, BRANCH, timeout=FETCH_TIMEOUT)
            if r.returncode == 0:
                stato = "ok"
            else:
                stato, dettaglio = "stale", (r.stderr.strip().splitlines() or ["fetch fallito"])[-1]
        except subprocess.TimeoutExpired:
            stato, dettaglio = "stale", f"fetch oltre {FETCH_TIMEOUT}s"
        except OSError as e:
            stato, dettaglio = "stale", str(e)
    stems = stems_remoti()
    if stems is None:
        return [], "unavailable", dettaglio or f"{REMOTE_REF} non leggibile"
    return stems, stato, dettaglio


# ---------------------------------------------------------------------------
# Comportamento base (senza namespace) — invariato rispetto a pre-US-314
# ---------------------------------------------------------------------------

def massimo(prefisso: str, remoti: list[str] | None = None,
            prenotazioni: list[dict] | None = None) -> int:
    """Il massimo su TUTTI i file, inclusi `cancelled` e archivio (e, se dati, quelli remoti
    e le prenotazioni del namespace del master, `prefix` vuoto)."""
    trovati = [
        int(m.group(1))
        for percorso in RADICE.joinpath("management/kanban").rglob(f"{prefisso}-*.md")
        for m in [re.match(rf"{prefisso}-(\d+)", percorso.stem)] if m
    ]
    trovati += [int(m.group(1)) for st in remoti or []
                for m in [re.match(rf"{prefisso}-(\d+)", st)] if m]
    trovati += [int(r.get("to", 0)) for r in prenotazioni or []
                if not (r.get("prefix") or "")
                and str(r.get("kind", "")).lower() == prefisso.lower()]
    return max(trovati, default=0)


def duplicati(prefisso: str) -> dict[str, list[str]]:
    visti: dict[str, list[str]] = {}
    for percorso in RADICE.joinpath("management/kanban").rglob(f"{prefisso}-*.md"):
        visti.setdefault(percorso.stem, []).append(
            str(percorso.relative_to(RADICE / "management/kanban")))
    return {k: v for k, v in visti.items() if len(v) > 1}


# ---------------------------------------------------------------------------
# Comportamento con --namespace (EP-069 US-314)
# ---------------------------------------------------------------------------

def _load_registry() -> dict:
    """Carica il registro YAML. Ritorna {} se assente o malformato (fail-open)."""
    if not REGISTRY_PATH.exists():
        return {}
    try:
        import yaml  # PyYAML — gia' usato da altri tool di M
        return yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def massimo_con_namespace(prefisso: str, namespace: str,
                          remoti: list[str] | None = None,
                          prenotazioni: list[dict] | None = None) -> int:
    """Massimo considerando file sul filesystem E prenotazioni nel registro.

    Garantisce che il prossimo ID suggerito non cada in un range gia' prenotato
    da un'altra epica — anche se i file non sono ancora stati creati.
    """
    kanban = RADICE / "management" / "kanban"
    pattern = re.compile(rf"^{re.escape(namespace)}-{prefisso}-(\d+)$")
    fs_max = max(
        (int(m.group(1))
         for percorso in kanban.rglob(f"{namespace}-{prefisso}-*.md")
         for m in [pattern.match(percorso.stem)] if m),
        default=0,
    )

    # `prenotazioni`, se dato, e' l'unione locale+remoto; altrimenti solo il registro locale
    reservations = (prenotazioni if prenotazioni is not None
                    else _load_registry().get("reservations") or [])
    kind_lc = prefisso.lower()
    reg_max = max(
        (int(r.get("to", 0))
         for r in reservations
         if r.get("prefix") == namespace and r.get("kind", "").lower() == kind_lc),
        default=0,
    )
    remote_max = max(
        (int(m.group(1)) for st in remoti or [] for m in [pattern.match(st)] if m),
        default=0,
    )
    return max(fs_max, reg_max, remote_max)


def duplicati_con_namespace(prefisso: str, namespace: str) -> dict[str, list[str]]:
    kanban = RADICE / "management" / "kanban"
    pattern = re.compile(rf"^{re.escape(namespace)}-{prefisso}-\d+$")
    visti: dict[str, list[str]] = {}
    for percorso in kanban.rglob(f"{namespace}-{prefisso}-*.md"):
        if pattern.match(percorso.stem):
            visti.setdefault(percorso.stem, []).append(
                str(percorso.relative_to(kanban)))
    return {k: v for k, v in visti.items() if len(v) > 1}


# ---------------------------------------------------------------------------
# Prenotazioni nel namespace del master e --reserve (EP-107)
# ---------------------------------------------------------------------------

def flag_namespaces_attivo(radice: Path | None = None) -> bool:
    """`kanban_namespaces.enabled: true` in factory.config.yaml (assente o spento: False).

    Legge il YAML: conta solo la chiave `enabled` direttamente sotto `kanban_namespaces`."""
    cfg = (radice or RADICE) / "factory.config.yaml"
    if not cfg.is_file():
        return False
    try:
        import yaml
        dati = yaml.safe_load(cfg.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return False
    blocco = dati.get("kanban_namespaces") if isinstance(dati, dict) else None
    return isinstance(blocco, dict) and blocco.get("enabled") is True


def prenotazioni_locali() -> list[dict]:
    reg = _load_registry()
    return [v for v in reg.get("reservations") or [] if isinstance(v, dict)]


def _registro_rel() -> str:
    return REGISTRY_PATH.relative_to(RADICE).as_posix()


def prenotazioni_remote() -> list[dict]:
    """Prenotazioni del registro su origin/<branch> (git show).

    Calcolo informativo, fail-open: [] se non leggibile, con avviso su stderr."""
    try:
        r = _git("show", f"{REMOTE_REF}:{_registro_rel()}")
    except OSError:
        return []
    if r.returncode != 0:
        return []
    try:
        return _parse_registro(r.stdout, f"{REMOTE_REF}:{_registro_rel()}")
    except ErroreRiserva as e:
        print(f"# AVVISO: {e.messaggio}; le prenotazioni remote sono ignorate.", file=sys.stderr)
        return []


def prenotazioni_remote_strict() -> list[dict]:
    """Come prenotazioni_remote, ma per --reserve: registro assente, malformato o non
    parsabile e' un errore (non si pubblica sopra un registro che non si legge)."""
    try:
        r = _git("show", f"{REMOTE_REF}:{_registro_rel()}")
    except OSError as e:
        raise ErroreRiserva(4, f"registro su {REMOTE_REF} non leggibile: {e}")
    if r.returncode != 0:
        raise ErroreRiserva(4, f"{_registro_rel()} assente o non leggibile su {REMOTE_REF}: "
                               f"{r.stderr.strip()}")
    return _parse_registro(r.stdout, f"{REMOTE_REF}:{_registro_rel()}")


def unisci_prenotazioni(*liste: list[dict]) -> list[dict]:
    visti: set = set()
    out: list[dict] = []
    for lista in liste:
        for v in lista:
            k = (v.get("prefix") or "", str(v.get("kind", "")).lower(),
                 v.get("from"), v.get("to"), v.get("epic"))
            if k not in visti:
                visti.add(k)
                out.append(v)
    return out


def riga_prenotazione(prefix: str, kind: str, da: int, a: int, epic: str, oggi: str) -> str:
    return (f'  - {{prefix: "{prefix}", kind: {kind}, from: {da}, to: {a}, '
            f'epic: {epic}, reserved_at: "{oggi}"}}')


def _ultima_riga_del_blocco(righe: list[str], idx: int) -> int:
    """Indice dell'ultima riga di contenuto del blocco che inizia alla chiave `righe[idx]`."""
    ultimo = idx
    for k in range(idx + 1, len(righe)):
        r = righe[k]
        if not r.strip() or r.lstrip().startswith("#"):
            continue
        if r[0] not in " \t-":
            break
        ultimo = k
    return ultimo


def _aggiungi_riga(testo: str, riga: str) -> str:
    """Inserisce la voce dentro il blocco `reservations`, ovunque si trovi nel file.

    Conserva commenti e formato. Se la chiave manca, la aggiunge in coda. Il risultato va
    sempre verificato con `verifica_scrittura`: forme che qui non si riconoscono (lista
    inline non vuota, chiave duplicata) producono un registro che la verifica rifiuta."""
    if not testo.endswith("\n"):
        testo += "\n"
    righe = testo.split("\n")[:-1]
    chiave = re.compile(r"^reservations:[ \t]*(\[\][ \t]*)?(#.*)?$")
    idx = next((i for i, r in enumerate(righe) if chiave.match(r)), None)
    if idx is None:
        righe += ["", "reservations:", riga]
        return "\n".join(righe) + "\n"
    righe[idx] = re.sub(r"[ \t]*\[\]", "", righe[idx], count=1)  # lo spazio prima di `#` resta
    ultimo = _ultima_riga_del_blocco(righe, idx)
    primo_item = next((r for r in righe[idx + 1:ultimo + 1] if r.lstrip().startswith("-")), None)
    if primo_item is not None:  # stessa indentazione delle voci esistenti
        riga = primo_item[:len(primo_item) - len(primo_item.lstrip())] + riga.lstrip()
    righe.insert(ultimo + 1, riga)
    return "\n".join(righe) + "\n"


def _parse_registro(testo: str, origine: str) -> list[dict]:
    """Le voci `reservations` del testo; ErroreRiserva se non e' un registro valido."""
    try:
        import yaml
        reg = yaml.safe_load(testo)
    except ImportError:
        raise ErroreRiserva(4, "PyYAML non disponibile: non posso leggere il registro")
    except Exception as e:
        raise ErroreRiserva(4, f"registro {origine} non parsabile: {str(e).splitlines()[0]}")
    if reg is None:
        reg = {}
    if not isinstance(reg, dict):
        raise ErroreRiserva(4, f"registro {origine} malformato: la radice non e' una mappa")
    voci = reg.get("reservations")
    if voci is None:
        return []
    if not isinstance(voci, list) or not all(isinstance(v, dict) for v in voci):
        raise ErroreRiserva(4, f"registro {origine} malformato: `reservations` non e' una lista di voci")
    return voci


def verifica_scrittura(nuovo_testo: str, precedenti: list[dict], voce: dict) -> None:
    """Il file riscritto deve parsarsi e contenere tutte le voci precedenti piu' la nuova."""
    voci = _parse_registro(nuovo_testo, "dopo la scrittura")
    atteso = [*precedenti, voce]
    if voci != atteso:
        raise ErroreRiserva(4, "la scrittura del registro non produce le voci attese "
                               f"({len(voci)} trovate, {len(atteso)} attese): non pubblico")


def _calcola_primo(prefisso: str, namespace: str | None, remoti: list[str],
                   prenotazioni: list[dict]) -> int:
    if namespace:
        # filesystem, remoto e prenotazioni unite (locale + remoto)
        return massimo_con_namespace(prefisso, namespace, remoti, prenotazioni) + 1
    return massimo(prefisso, remoti, prenotazioni) + 1


# Rifiuto "il branch e' avanzato": si ricalcola. Altri rifiuti (branch protetto, hook, permessi)
# sono errori immediati: ritentare non li cambia.
# Anche la corsa sul ref ("cannot lock ref ... is at X but expected Y") significa che il branch e'
# avanzato; un lock rimasto sul ref ("Unable to create '...lock': File exists") no: errore immediato.
_NON_FAST_FORWARD = ("non-fast-forward", "fetch first", "but expected")


def _push_non_fast_forward(stderr: str) -> bool:
    return any(t in stderr for t in _NON_FAST_FORWARD)


class ErroreRiserva(Exception):
    def __init__(self, rc: int, messaggio: str):
        super().__init__(messaggio)
        self.rc = rc
        self.messaggio = messaggio


class Calcolo:
    """Esito del calcolo di una prenotazione."""
    def __init__(self, prefisso: str, tipo: str, prefix: str, primo: int, quanti: int,
                 epic: str, oggi: str):
        self.voce = {"prefix": prefix, "kind": tipo, "from": primo, "to": primo + quanti - 1,
                     "epic": epic, "reserved_at": oggi}
        self.riga = riga_prenotazione(prefix, tipo, primo, primo + quanti - 1, epic, oggi)
        self.ids = [f"{(prefix + '-') if prefix else ''}{prefisso}-{primo + i:03d}"
                    for i in range(quanti)]
        self.messaggio = (f"kanban(registry): prenota {self.ids[0]}" +
                          (f"..{self.ids[-1]}" if quanti > 1 else "") + f" per {epic}")


def calcola(tipo: str, quanti: int, epic: str, namespace: str | None, fetch: bool) -> Calcolo:
    """Fetch, lettura del remoto (registro obbligatorio) e calcolo del range."""
    prefisso = PREFISSI[tipo]
    remoti, stato, dettaglio = carica_remoto(fetch=fetch, enabled=True)
    if stato not in ("ok", "no-fetch"):
        raise ErroreRiserva(3, f"{REMOTE_REF} non aggiornato ({stato}: {dettaglio}); una "
                               "prenotazione calcolata su dati vecchi non e' affidabile, non pubblico.")
    prenotazioni = unisci_prenotazioni(prenotazioni_locali(), prenotazioni_remote_strict())
    primo = _calcola_primo(prefisso, namespace, remoti, prenotazioni)
    return Calcolo(prefisso, tipo, namespace or "", primo, quanti, epic, date.today().isoformat())


def scrivi_nel_worktree(wt: Path, calc: Calcolo, co_author: str) -> None:
    """Riscrive il registro nel worktree, lo verifica e crea il commit del solo registro."""
    reg_wt = wt / _registro_rel()
    testo = reg_wt.read_text(encoding="utf-8") if reg_wt.is_file() else ""
    if not testo:
        raise ErroreRiserva(4, f"{_registro_rel()} assente su {REMOTE_REF}: nulla da aggiornare.")
    precedenti = _parse_registro(testo, f"{REMOTE_REF}:{_registro_rel()}")
    nuovo = _aggiungi_riga(testo, calc.riga)
    verifica_scrittura(nuovo, precedenti, calc.voce)
    reg_wt.write_text(nuovo, encoding="utf-8")
    messaggio = calc.messaggio + (f"\n\nCo-Authored-By: {co_author}" if co_author else "")
    r = _git("-C", str(wt), "add", "--", _registro_rel())
    if r.returncode == 0:
        r = _git("-C", str(wt), "commit", "-q", "-m", messaggio, "--", _registro_rel())
    if r.returncode != 0:
        raise ErroreRiserva(4, f"commit della prenotazione fallito: {(r.stderr or r.stdout).strip()}")


def pubblica(wt: Path) -> tuple[bool, str]:
    """Push di HEAD:<branch> e nient'altro. (True, sha) se pubblicato, (False, stderr) se il
    branch e' avanzato; ErroreRiserva per ogni altro esito (compreso il timeout, incerto)."""
    sha = _git("-C", str(wt), "rev-parse", "HEAD").stdout.strip()
    try:
        r = _git("-C", str(wt), "push", "--no-follow-tags", REMOTE, f"HEAD:{BRANCH}",
                 timeout=PUSH_TIMEOUT)
    except subprocess.TimeoutExpired:
        raise ErroreRiserva(6, (
            f"push oltre {PUSH_TIMEOUT}s: ESITO INCERTO, la prenotazione potrebbe essere stata "
            f"pubblicata. Non ritento. Verifica: `git fetch {REMOTE} {BRANCH}` poi cerca la voce "
            f"({sha[:10]}) in `git show {REMOTE_REF}:{_registro_rel()}`; se manca, rilancia."))
    if r.returncode == 0:
        return True, sha
    if _push_non_fast_forward(r.stderr):
        return False, r.stderr.strip()
    raise ErroreRiserva(4, f"push rifiutato: {r.stderr.strip()}")


def _rimuovi_worktree(wt: Path, registrato: bool) -> None:
    """Toglie la directory temporanea; se git conosceva il worktree lo scollega prima."""
    if registrato:
        r = _git("worktree", "remove", "--force", str(wt))
        if r.returncode != 0:
            print(f"# AVVISO: worktree temporaneo {wt} non rimosso ({r.stderr.strip()}); "
                  "esegui `git worktree prune` dopo aver cancellato la cartella.", file=sys.stderr)
    shutil.rmtree(wt, ignore_errors=True)
    if registrato:
        _git("worktree", "prune")


def tentativo(calc: Calcolo, co_author: str) -> tuple[bool, str]:
    """Un giro in un worktree temporaneo, rimosso sempre (anche se `worktree add` fallisce)."""
    wt: Path | None = None
    registrato = False
    try:
        wt = Path(tempfile.mkdtemp(prefix="next-id-reserve-"))
        r = _git("worktree", "add", "--detach", str(wt), REMOTE_REF)
        if r.returncode != 0:
            raise ErroreRiserva(4, f"worktree temporaneo non creato: {r.stderr.strip()}")
        registrato = True
        scrivi_nel_worktree(wt, calc, co_author)
        return pubblica(wt)
    finally:
        if wt is not None:
            _rimuovi_worktree(wt, registrato)


def riserva(tipo: str, quanti: int, epic: str, namespace: str | None, dry_run: bool,
            co_author: str, fetch: bool) -> int:
    ultimo_errore = ""
    try:
        for n in range(1, MAX_TENTATIVI + 1):
            calc = calcola(tipo, quanti, epic, namespace, fetch)
            if dry_run:
                print("# dry-run: nessun commit, nessun push. Voce che verrebbe scritta in "
                      f"{_registro_rel()} su {REMOTE_REF}:")
                print(calc.riga)
                print("\n".join(calc.ids))
                return 0
            pubblicato, esito = tentativo(calc, co_author)
            if pubblicato:
                print("\n".join(calc.ids))
                print(f"# prenotato su {REMOTE}/{BRANCH}: commit {esito}")
                return 0
            ultimo_errore = esito
            print(f"# tentativo {n}/{MAX_TENTATIVI}: {BRANCH} e' avanzato, ricalcolo.", file=sys.stderr)
            fetch = True
    except ErroreRiserva as e:
        print(f"errore: {e.messaggio}", file=sys.stderr)
        return e.rc
    print(f"errore: {MAX_TENTATIVI} tentativi di push falliti ({ultimo_errore}). Nessuna prenotazione "
          "pubblicata; riprova.", file=sys.stderr)
    return 5


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    global REMOTE, BRANCH, REMOTE_REF
    parser = argparse.ArgumentParser(
        description="Prossimo identificativo libero, EP / US / TSK.",
        add_help=True,
    )
    parser.add_argument(
        "tipo", nargs="?", default="tsk",
        help="tipo di artefatto: tsk | us | ep (default: tsk)",
    )
    parser.add_argument(
        "quanti", nargs="?", type=int, default=1,
        help="quanti identificativi consecutivi stampare (default: 1)",
    )
    parser.add_argument(
        "--namespace", metavar="PREFIX",
        help="prefisso namespace (es. UP, FAC) — opt-in, richiede id-registry.yaml",
    )
    parser.add_argument(
        "--no-fetch", action="store_true",
        help="non fa il fetch: legge l'origin/main gia' scaricato",
    )
    parser.add_argument(
        "--remote", default=REMOTE, help=f"remote da cui leggere gli ID (default {REMOTE})",
    )
    parser.add_argument(
        "--branch", default=BRANCH, help=f"branch del remote (default {BRANCH})",
    )
    parser.add_argument(
        "--no-remote", action="store_true",
        help="non legge il remoto (come NEXT_ID_OFFLINE=1): solo filesystem locale",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="stampa un documento JSON (ids, remote, detail) invece degli ID in chiaro",
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="esce con 3 se l'origin/main non e' stato aggiornato (offline) invece di 0",
    )
    parser.add_argument(
        "--reserve", action="store_true",
        help="prenota gli ID nel registro e lo pubblica sul branch del remoto (richiede --epic)",
    )
    parser.add_argument("--epic", metavar="EP-x", help="epica che prenota (con --reserve)")
    parser.add_argument("--dry-run", action="store_true",
                        help="con --reserve: stampa la voce senza commit ne' push")
    parser.add_argument("--co-author", default=os.environ.get("NEXT_ID_CO_AUTHOR", ""),
                        metavar="'Nome <mail>'",
                        help="riga Co-Authored-By del commit di --reserve (o NEXT_ID_CO_AUTHOR)")
    args = parser.parse_args(argv)

    tipo = args.tipo.lower()
    if tipo not in PREFISSI:
        print(f"tipo sconosciuto: {tipo} (attesi: {', '.join(PREFISSI)})", file=sys.stderr)
        return 2

    prefisso = PREFISSI[tipo]
    REMOTE, BRANCH = args.remote, args.branch
    REMOTE_REF = f"{REMOTE}/{BRANCH}"
    errore = _valida_reserve(args)
    if errore:
        print(errore, file=sys.stderr)
        return 2
    if args.reserve:
        ns = args.namespace.upper() if args.namespace else None
        return riserva(tipo, args.quanti, args.epic, ns, args.dry_run, args.co_author,
                       fetch=not args.no_fetch)
    offline = args.no_remote or os.environ.get("NEXT_ID_OFFLINE", "").strip().lower() in (
        "1", "true", "yes", "si")
    remoti, stato, dettaglio = carica_remoto(fetch=not args.no_fetch, enabled=not offline)
    rc = 3 if args.strict and stato in ("stale", "unavailable") else 0
    unite = _prenotazioni_informative(stato)
    ns = args.namespace.upper() if args.namespace else None
    if ns:
        primo = massimo_con_namespace(prefisso, ns, remoti, unite) + 1
        ids = [f"{ns}-{prefisso}-{primo + i:03d}" for i in range(args.quanti)]
    else:
        primo = massimo(prefisso, remoti, unite) + 1
        # Zero-padding a 3 cifre: gli identificativi del repo sono `EP-067`, non `EP-67`.
        # Stamparli senza padding produce un ID che non corrisponde a nessuna convenzione
        # e che il giorno dopo qualcuno copia.
        ids = [f"{prefisso}-{primo + i:03d}" for i in range(args.quanti)]

    if args.json:
        print(json.dumps({"ids": ids, "remote": stato, "detail": dettaglio}))
    else:
        for i in ids:
            print(i)
    _avvisa_remoto_vecchio(stato, dettaglio)
    _segnala_duplicati(prefisso, ns)
    return rc


def _valida_reserve(args) -> str | None:
    """Il messaggio d'errore (uscita 2) se la combinazione di opzioni non e' valida, altrimenti None."""
    if args.dry_run and not args.reserve:
        return "--dry-run vale solo con --reserve"
    if not args.reserve:
        return None
    if not flag_namespaces_attivo():
        return "--reserve richiede kanban_namespaces.enabled: true in factory.config.yaml"
    if not args.epic or not re.fullmatch(r"(?:[A-Z]{2,4}-)?EP-\d+", args.epic):
        return "--reserve richiede --epic EP-<n> (es. --epic EP-108)"
    if args.quanti < 1:
        return "quanti deve essere >= 1"
    return None


def _prenotazioni_informative(stato: str) -> list[dict] | None:
    """Prenotazioni che entrano nel calcolo informativo (senza --reserve): None a flag spento
    (nel ramo --namespace il registro locale resta letto da `massimo_con_namespace`), altrimenti
    locali piu' quelle di origin/<branch> se il remoto e' stato letto."""
    if not flag_namespaces_attivo():
        return None
    unite = prenotazioni_locali()
    if stato not in ("disabled", "unavailable"):
        unite = unisci_prenotazioni(unite, prenotazioni_remote())
    return unite


def _avvisa_remoto_vecchio(stato: str, dettaglio: str) -> None:
    if stato not in ("stale", "unavailable"):
        return
    quale = ("uso l'ultimo origin/main gia' scaricato, potrebbe essere vecchio"
             if stato == "stale" else "calcolo sul solo filesystem locale")
    print(f"# AVVISO: {REMOTE_REF} non aggiornato ({dettaglio}): {quale}. "
          "L'ID potrebbe collidere con uno creato altrove.", file=sys.stderr)
    print(f"# next-id-remote: {stato}", file=sys.stderr)


def _segnala_duplicati(prefisso: str, ns: str | None) -> None:
    dup = duplicati_con_namespace(prefisso, ns) if ns else duplicati(prefisso)
    if not dup:
        return
    if ns:
        print(f"\n# {len(dup)} identificativi {ns}-{prefisso} duplicati:", file=sys.stderr)
    else:
        print(f"\n# {len(dup)} identificativi {prefisso} duplicati nel repo "
              f"(storici, vedi tests/test_id_unici.py):", file=sys.stderr)
    for k in sorted(dup)[:5]:
        print(f"#   {k}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())

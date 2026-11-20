#!/usr/bin/env python3
"""
log_tail_check.py — controllo delle voci NUOVE di wiki/log.md prima del push.

Un merge o uno stash finito male puo' fondere due blocchi `---` / `chiave: valore` del log (chiavi
ripetute) o far perdere l'intestazione di una voce (date, type, operator): il log resta append-only
e leggibile, ma la voce e' rovinata e una volta pubblicata si corregge solo con una voce di rettifica.

Si guardano solo i blocchi che NON c'erano nella base (il log della base, di solito origin/main):
  (a) chiave ripetuta nello stesso blocco nuovo (tipico delle voci fuse, es. due `context:`);
  (b) blocco frontmatter nuovo che segue un separatore `---` senza `date`, `type` o chi l'ha scritto.
      Chi l'ha scritto e' `operator` oppure `agent`: le voci di review, develop e dev-handoff usano
      `agent` e nel log attuale non hanno `operator`.

Un blocco frontmatter va dal separatore `---` alla riga `---` successiva (o a un titolo `#`, o alla
fine del file); contano solo le righe `chiave: valore` a colonna 0 (le righe rientrate di un valore
a piu' righe, es. `summary: >`, non sono chiavi). Le voci in formato `## [data] tipo | titolo` non
sono blocchi frontmatter e non vengono controllate. Il frontmatter di apertura del file (riga 1) e'
l'intestazione del documento: non e' una voce. Sono accettati i fine riga \\r\\n.

Se la base e' gia' rovinata ma i blocchi nuovi sono corretti, l'esito e' 0. Si controlla solo
wiki/log.md, non gli archivi wiki/log-*.md.

Uso:
  python3 tools/wiki/log_tail_check.py [--base <ref>]   working tree contro <ref> (default origin/main)
  python3 tools/wiki/log_tail_check.py --pre-push       righe dell'hook pre-push su stdin:
                                                        <local ref> <local sha> <remote ref> <remote sha>
Exit 0 = ok, 1 = voci rovinate (stampa file, blocco e cosa manca), 2 = controllo incompleto
(ref sconosciuto, git in errore o scaduto): avvisa, non e' un «pulito».
Nel pre-push la base e' il remote sha; se e' zero (ref nuovo) o sconosciuto, il merge-base con origin/main.

Solo stdlib + git. Nessuna scrittura.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
ZERO = "0" * 40
LOG = "wiki/log.md"
GIT_TIMEOUT = 60

KEY = re.compile(r"^([a-z_]+):(\s|$)")
HEADING = re.compile(r"^#{1,6}\s")
AUTORE = ("operator", "agent")


class GitError(RuntimeError):
    """Comando git fallito o scaduto: il controllo e' incompleto, mai un «pulito»."""


def git(*args, must=False):
    cmd = ["git", *args]
    try:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, timeout=GIT_TIMEOUT)
    except subprocess.TimeoutExpired:
        raise GitError(f"{' '.join(cmd)}: timeout dopo {GIT_TIMEOUT}s")
    if must and r.returncode:
        raise GitError(f"{' '.join(cmd)}: exit {r.returncode}: {r.stderr.decode('utf-8', 'replace').strip()[:300]}")
    return r


# --- analisi del testo ----------------------------------------------------------------------

def parse_blocks(text: str) -> list[dict]:
    """Blocchi `chiave: valore` del log.

    Ogni blocco: {'line': riga (da 1) della prima chiave, 'sep': True se segue un `---`,
    'keys': [(chiave, riga di testo)], 'sig': firma per il confronto con la base}.
    """
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    blocks = []
    i, n = 0, len(lines)
    while i < n:
        if i > 0 and lines[i].strip() == "---" and i + 1 < n and KEY.match(lines[i + 1]):
            j, keys = i + 1, []
            while j < n and lines[j].strip() != "---" and not HEADING.match(lines[j]):
                m = KEY.match(lines[j])
                if m:
                    keys.append((m.group(1), lines[j]))
                j += 1
            blocks.append({"line": i + 2, "sep": True, "keys": keys})
            i = j
        elif KEY.match(lines[i]):
            j, keys = i, []
            while j < n and KEY.match(lines[j]):
                keys.append((KEY.match(lines[j]).group(1), lines[j]))
                j += 1
            blocks.append({"line": i + 1, "sep": False, "keys": keys})
            i = j
        else:
            i += 1
    for b in blocks:
        b["sig"] = (b["sep"], tuple(l for _, l in b["keys"]))
    return blocks


def _etichetta(b: dict) -> str:
    """Come si riconosce il blocco: tipo, data e sessione/task, dalle sue stesse chiavi."""
    valori = {}
    for k, l in b["keys"]:
        valori.setdefault(k, l.split(":", 1)[1].strip()[:50])
    parti = [f"{k}: {valori[k]}" for k in ("date", "type", "session_label", "session_id", "tsk", "task")
             if k in valori]
    return ", ".join(parti[:3]) or b["keys"][0][1][:60]


def check_texts(new_text: str, base_text: str, path: str = LOG) -> list[str]:
    """Problemi dei blocchi presenti in new_text e non in base_text (messaggi pronti da stampare)."""
    base = {b["sig"] for b in parse_blocks(base_text)}
    problemi = []
    for b in parse_blocks(new_text):
        if b["sig"] in base:
            continue
        chiavi = [k for k, _ in b["keys"]]
        dup = sorted({k for k in chiavi if chiavi.count(k) > 1})
        dove = f"{path}, riga {b['line']} ({_etichetta(b)})"
        if dup:
            problemi.append(f"{dove}: chiavi ripetute {', '.join(dup)} nello stesso blocco "
                            "(probabile fusione di due voci: ripristina la riga `---` e le chiavi della seconda)")
        if b["sep"]:
            mancano = [k for k in ("date", "type") if k not in chiavi]
            if not any(k in chiavi for k in AUTORE):
                mancano.append("operator (o agent)")
            if mancano:
                problemi.append(f"{dove}: intestazione incompleta, manca {', '.join(mancano)}")
    return problemi


# --- git ------------------------------------------------------------------------------------

def _blob(rev: str) -> bytes | None:
    """wiki/log.md in <rev>; None se il file non c'e'. Errori di git: GitError."""
    if git("cat-file", "-e", f"{rev}:{LOG}").returncode:
        # il file manca oppure il rev non esiste: distinguo
        git("rev-parse", "--verify", "-q", f"{rev}^{{commit}}", must=True)
        return None
    return git("cat-file", "blob", f"{rev}:{LOG}", must=True).stdout


def _testo(data: bytes | None) -> str:
    return "" if data is None else data.decode("utf-8", "replace")


def _risolvi_base(remote_sha: str) -> str:
    """Remote sha se lo conosciamo, altrimenti merge-base con origin/main; GitError se non c'e' nulla."""
    if remote_sha != ZERO and git("cat-file", "-e", f"{remote_sha}^{{commit}}").returncode == 0:
        return remote_sha
    return "origin/main"


def check_pre_push(stdin_text: str) -> list[str]:
    problemi, visti = [], set()
    for line in stdin_text.splitlines():
        parts = line.split()
        if len(parts) != 4 or parts[1] == ZERO:
            continue  # riga malformata o cancellazione di un ref
        _, local_sha, remote_ref, remote_sha = parts
        base = _risolvi_base(remote_sha)
        if base == "origin/main":
            base = git("merge-base", local_sha, "origin/main", must=True).stdout.decode().strip()
        if (local_sha, base) in visti:
            continue
        visti.add((local_sha, base))
        nuovo = _blob(local_sha)
        if nuovo is None:
            continue
        vecchio = _blob(base)
        if nuovo == vecchio:
            continue
        for p in check_texts(_testo(nuovo), _testo(vecchio)):
            problemi.append(f"[{remote_ref}] {p}")
    return problemi


def check_worktree(base: str) -> list[str]:
    path = ROOT / LOG
    if not path.is_file():
        return []
    vecchio = _blob(base)
    return check_texts(path.read_bytes().decode("utf-8", "replace"), _testo(vecchio))


# --- uscita ---------------------------------------------------------------------------------

def _utf8_output() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except (AttributeError, ValueError, OSError):
            pass


def _print_safe(text: str, file=None) -> None:
    file = file or sys.stdout
    try:
        print(text, file=file)
    except UnicodeEncodeError:
        print(text.encode("ascii", "backslashreplace").decode("ascii"), file=file)


def _report(problemi: list[str]) -> str:
    return (f"Voci nuove di {LOG} rovinate ({len(problemi)}):\n"
            + "\n".join(f"  - {p}" for p in problemi))


def main(argv=None) -> int:
    _utf8_output()
    try:
        return _main(argv)
    except GitError as e:
        print(f"log_tail_check: controllo incompleto — {e}", file=sys.stderr)
        return 2
    except (OSError, UnicodeError) as e:
        print(f"log_tail_check: controllo incompleto — {type(e).__name__}: {e}", file=sys.stderr)
        return 2


def _main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pre-push", action="store_true")
    ap.add_argument("--base", default="origin/main")
    a = ap.parse_args(argv)

    if a.pre_push:
        problemi = check_pre_push(sys.stdin.read())
        if problemi:
            _print_safe("\n[log] PUSH BLOCCATO\n\n" + _report(problemi)
                        + "\n\nCorreggi con un nuovo commit (niente force push, niente --no-verify) e ripeti il push.\n",
                        file=sys.stderr)
            return 1
        return 0

    problemi = check_worktree(a.base)
    if problemi:
        _print_safe(_report(problemi))
        return 1
    print(f"log: voci nuove di {LOG} ben formate rispetto a {a.base}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

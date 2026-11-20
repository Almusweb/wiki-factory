#!/usr/bin/env python3
"""
install_factory_hooks.py -- installa gli hook del REPO PADRE (factory) che
allineano i submodule dopo ogni pull/checkout, chiamando sm_doctor.py in
modalita' non distruttiva (--align --quiet).

Complementare a install_submodule_hooks.py (che installa gli hook §ai_policy
DENTRO i submodule). Qui gli hook stanno in <factory>/.git/hooks e rendono
l'allineamento automatico e sicuro: dopo `git pull` / `git checkout <branch>`
i submodule seguono automaticamente il commit tracciato dalla factory, senza
mai toccare un working tree con modifiche non committate (niente --force).

HOOK INSTALLATI:
  - post-merge     -> dopo pull/merge sul repo padre
  - post-checkout  -> dopo checkout/switch di branch (non su checkout di file)
  - pre-commit     -> 1. marcatori di conflitto (`<<<<<<<`, `=======`, `>>>>>>>`) nei file in coda e
                         append-only (tools/wiki/conflict_markers_check.py --staged): BLOCCANTE;
                         exit 2 (controllo incompleto) avvisa e lascia passare.
                      2. con `wiki_lint.log_append_guard.hook: true` in factory.config.yaml
                         (default false): se wiki/log.md e' in stage lancia
                         tools/wiki/log_append_guard.py e rifiuta il commit se una riga sparisce
                         senza archivio wiki/log-*.md. Opt-in.
                      Catena di guardie: dopo il log, la guardia dei segreti sui blob dell'indice
                      (tools/security/secrets_guard.py --hook --staged) se `secrets_guard.enabled: true`;
                      blocca con severita' ERROR (FAIL, e NON_VERIFICABILE salvo un
                      record di deroga sul ref protetto, EP-108 US-423). Previene nel percorso cooperativo, rileva
                      negli altri (--no-verify e core.hooksPath la aggirano).
                      Installato sempre (la guardia dei marcatori non ha flag).
  - pre-push       -> 1. marcatori di conflitto nei file in coda dei commit da pubblicare
                         (conflict_markers_check.py --pre-push): BLOCCANTE, ferma anche un commit
                         fatto senza pre-commit (clone nuovo, hook mancante).
                      2. voci nuove di wiki/log.md rovinate: chiavi ripetute nello stesso blocco o
                         intestazione senza date/type/operator|agent (tools/wiki/log_tail_check.py
                         --pre-push): BLOCCANTE; exit 2 (controllo incompleto) avvisa e lascia passare.

MERGE DRIVER (git config locale, non versionata: va registrata in ogni clone):
  - factory-log-union -> wiki/log.md: voci aggiunte in coda da due branch si fondono senza
                         conflitto (tools/wiki/log_union_driver.py). Associato a .gitattributes.
  - factory-events-union -> analytics/events/*.jsonl: righe aggiunte da due branch unite senza
                         duplicati (tools/wiki/events_union_driver.py). Associato a .gitattributes.
  - factory-manifest-union -> raw/.extraction-manifest.json: unione per chiave JSON; se la stessa
                         chiave cambia in modo diverso nei due lati il merge resta in conflitto
                         (tools/wiki/manifest_union_driver.py). Associato a .gitattributes.
  Senza driver registrato git ignora il nome del driver e usa il merge standard: nessun danno,
  solo i conflitti di prima. La cartella hook e' quella che git legge davvero
  (`git rev-parse --git-path hooks`), quindi l'installer funziona anche da un worktree.

USO:
  python3 tools/vcs/install_factory_hooks.py [--dry-run] [--force]
  python3 tools/vcs/install_factory_hooks.py --only post-merge [--dry-run] [--force]

--only <hook> installa SOLO quell'hook (niente altri hook, niente merge driver). Un hook diverso
gia' presente non si sovrascrive senza --force.

Esegui prima con --dry-run. Idempotente (checksum sha256). stdlib-only.

Riferimenti: tools/vcs/sm_doctor.py, tools/vcs/install_submodule_hooks.py
             tools/vcs/README-submodule.md
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

# Rende importabile smlib da qualsiasi CWD
sys.path.insert(0, str(Path(__file__).resolve().parent))

from smlib import color, factory_root
from smlib.hookio import to_lf, write_hook

# ---------------------------------------------------------------------------
# Contenuto hook -- bash (Git for Windows li invoca via shebang).
# Non distruttivi: exit 0 sempre (|| true) per non bloccare mai un'operazione git.
# Il path dello script fa riferimento a tools/vcs/sm_doctor.py.
# ---------------------------------------------------------------------------
_COMMON = r'''# --- factory submodule auto-align (sm_doctor, non distruttivo) ---
# Allinea i submodule al commit tracciato dalla factory. Salta i tree con
# modifiche non committate (mai --force). Errori non bloccano l'operazione git.
ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
PY="$(command -v python3 || command -v python || command -v py || true)"
[ -z "$PY" ] && exit 0
[ -f "$ROOT/tools/vcs/sm_doctor.py" ] || exit 0
"$PY" "$ROOT/tools/vcs/sm_doctor.py" --align --quiet || true
exit 0
'''

POST_MERGE_HOOK = (
    "#!/usr/bin/env bash\n"
    "# post-merge hook -- factory (auto-generato, install_factory_hooks.py)\n"
    "set -uo pipefail\n"
    + _COMMON
)

# post-checkout riceve: $1=prev-HEAD $2=new-HEAD $3=flag (1=branch checkout).
# Esegue il doctor solo sul checkout di branch, non sul checkout di singoli file.
POST_CHECKOUT_HOOK = (
    "#!/usr/bin/env bash\n"
    "# post-checkout hook -- factory (auto-generato, install_factory_hooks.py)\n"
    "set -uo pipefail\n"
    'if [ "${3:-0}" != "1" ]; then exit 0; fi\n'
    + _COMMON
)

# pre-commit: catena di guardie in sequenza; il fallimento di una blocca il commit (exit 1).
# 1) guardia del log (solo se wiki/log.md e' in stage), 2) guardia dei segreti sui file staged:
# l'oracolo con --hook non fa nulla se `secrets_guard.enabled` non e' true e blocca solo con
# severita' ERROR. Senza python o senza gli script la guardia corrispondente e' saltata:
# un ambiente incompleto non deve impedire i commit.
PRE_COMMIT_HOOK = (
    "#!/usr/bin/env bash\n"
    "# pre-commit hook -- factory (auto-generato, install_factory_hooks.py)\n"
    "set -uo pipefail\n"
    'ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0\n'
    'PY="$(command -v python3 || command -v python || command -v py || true)"\n'
    '[ -z "$PY" ] && exit 0\n'
    "# --- 0. marcatori di conflitto nei file in coda (conflict_markers_check): blocca con exit 1 ---\n"
    'if [ -f "$ROOT/tools/wiki/conflict_markers_check.py" ]; then\n'
    '  "$PY" "$ROOT/tools/wiki/conflict_markers_check.py" --staged\n'
    '  rc=$?\n'
    '  [ "$rc" -eq 1 ] && exit 1\n'
    '  [ "$rc" -ne 0 ] && echo "[pre-commit] avviso: controllo dei marcatori non eseguito (exit $rc)" >&2\n'
    "fi\n"
    "# --- 1. wiki/log.md append-only (log_append_guard) ---\n"
    'if [ -f "$ROOT/tools/wiki/log_append_guard.py" ] \\\n'
    '   && git diff --cached --name-only | grep -qx "wiki/log.md"; then\n'
    '  "$PY" "$ROOT/tools/wiki/log_append_guard.py" || exit 1\n'
    "fi\n"
    "# --- 2. segreti nei blob dell'indice (secrets_guard, attiva solo con secrets_guard.enabled: true) ---\n"
    "# Previene nel percorso cooperativo, rileva negli altri: --no-verify e core.hooksPath la aggirano.\n"
    "# NON_VERIFICABILE a severita' ERROR blocca; deroga solo da record sul ref protetto (US-423).\n"
    'if [ -f "$ROOT/tools/security/secrets_guard.py" ]; then\n'
    '  "$PY" "$ROOT/tools/security/secrets_guard.py" --hook --staged --root "$ROOT" || {\n'
    '    echo "[pre-commit] guardia segreti: commit bloccato (previene nel percorso cooperativo, rileva negli altri)." >&2\n'
    "    exit 1\n"
    "  }\n"
    "fi\n"
    "exit 0\n"
)

# pre-push: due controlli in fila sugli stessi dati di stdin (l'hook li riceve una volta sola).
#   1. conflict_markers_check.py --pre-push: marcatori nei file in coda dei commit da pubblicare.
#   2. log_tail_check.py --pre-push: voci nuove di wiki/log.md con chiavi ripetute o intestazione
#      incompleta.
# Exit 1 blocca; exit 2 (controllo incompleto) avvisa e lascia passare. Ogni script si cerca nel
# worktree che pusha e, se manca (worktree nato prima), nel checkout principale: gli oggetti git
# sono comuni. Senza Python o senza script non blocca.
PRE_PUSH_HOOK = (
    "#!/usr/bin/env bash\n"
    "# pre-push hook -- factory (auto-generato, install_factory_hooks.py)\n"
    "# 1. marcatori di conflitto nei file in coda (conflict_markers_check.py): blocca.\n"
    "# 2. voci nuove di wiki/log.md con chiavi ripetute o intestazione incompleta (log_tail_check.py): blocca.\n"
    "set -uo pipefail\n"
    'PY="$(command -v python3 || command -v python || command -v py || true)"\n'
    '[ -z "$PY" ] && exit 0\n'
    'INPUT="$(cat)"\n'
    'ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0\n'
    'MAIN="$(cd "$(git rev-parse --git-common-dir 2>/dev/null)/.." 2>/dev/null && pwd)"\n'
    'trova() {\n'
    '  if [ -f "$ROOT/$1" ]; then printf \'%s\\n\' "$ROOT/$1"; return 0; fi\n'
    '  if [ -n "$MAIN" ] && [ -f "$MAIN/$1" ]; then printf \'%s\\n\' "$MAIN/$1"; return 0; fi\n'
    '  return 1\n'
    '}\n'
    'if C="$(trova tools/wiki/conflict_markers_check.py)"; then\n'
    '  printf \'%s\\n\' "$INPUT" | "$PY" "$C" --pre-push\n'
    '  rc=$?\n'
    '  # 2 = controllo incompleto: avviso gia\' stampato, il push prosegue\n'
    '  [ "$rc" -eq 1 ] && exit 1\n'
    'fi\n'
    'if L="$(trova tools/wiki/log_tail_check.py)"; then\n'
    '  printf \'%s\\n\' "$INPUT" | "$PY" "$L" --pre-push\n'
    '  rc=$?\n'
    '  [ "$rc" -eq 1 ] && exit 1\n'
    'fi\n'
    'exit 0\n'
)

HOOKS = {
    "post-merge": POST_MERGE_HOOK,
    "post-checkout": POST_CHECKOUT_HOOK,
    "pre-push": PRE_PUSH_HOOK,
}


# Merge driver: nome -> (descrizione, comando). Il comando gira con cwd = radice del working tree.
MERGE_DRIVERS = {
    "factory-log-union": (
        "wiki/log.md: union delle voci aggiunte in coda",
        "python3 tools/wiki/log_union_driver.py %O %A %B",
    ),
    "factory-events-union": (
        "analytics/events/*.jsonl: unione per righe senza duplicati",
        "python3 tools/wiki/events_union_driver.py %O %A %B",
    ),
    "factory-manifest-union": (
        "raw/.extraction-manifest.json: unione per chiave JSON, conflitto se la stessa chiave diverge",
        "python3 tools/wiki/manifest_union_driver.py %O %A %B",
    ),
    "factory-sprint-sections": (
        "management/kanban/sprint.md: unione per sezioni, testo curato preservato, conflitto se la stessa sezione cambia dai due lati",
        "python3 tools/kanban/sprint_sections_driver.py %O %A %B",
    ),
}


def _git_config(root: Path, *args: str):
    return subprocess.run(["git", "-C", str(root), "config", "--local", *args],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


def ensure_merge_drivers(root: Path, dry_run: bool = False, overwrite: bool = False,
                         quiet: bool = True) -> dict:
    """Registra i merge driver nella config locale. Idempotente: se il valore c'e' gia' non scrive.

    Con overwrite=False un driver con comando diverso non viene toccato. Ritorna
    {nome: 'ok' | 'installed' | 'updated' | 'conflict'}. Con dry_run non scrive.
    """
    esiti = {}
    for nome, (descrizione, comando) in MERGE_DRIVERS.items():
        chiave = f"merge.{nome}.driver"
        attuale = _git_config(root, "--get", chiave).stdout.strip()
        if attuale == comando:
            esiti[nome] = "ok"
        elif attuale and not overwrite:
            esiti[nome] = "conflict"
        else:
            esiti[nome] = "updated" if attuale else "installed"
            if not dry_run:
                _git_config(root, chiave, comando)
                _git_config(root, f"merge.{nome}.name", descrizione)
        if not quiet:
            print("  " + {
                "ok": color.green(f"OK -- driver {nome} gia' registrato."),
                "conflict": color.yellow(f"ATTENZIONE -- driver {nome} diverso ({attuale}); "
                                         "riesegui senza --only per riallinearlo."),
                "installed": color.cyan(f"{'[dry-run] Registrerebbe' if dry_run else 'Registrato'} driver {nome}."),
                "updated": color.cyan(f"{'[dry-run] Aggiornerebbe' if dry_run else 'Aggiornato'} driver {nome}."),
            }[esiti[nome]])
    return esiti


def log_guard_enabled(root: Path) -> bool:
    """`wiki_lint.log_append_guard.hook: true` in factory.config.yaml (lettura per indentazione,
    senza YAML: stdlib-only). Assente, illeggibile o diverso da true -> False."""
    cfg = root / "factory.config.yaml"
    if not cfg.is_file():
        return False
    path = ["wiki_lint", "log_append_guard"]
    depth = 0
    for raw in cfg.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        key = line.strip()
        if depth < len(path):
            if indent == 2 * depth and key == path[depth] + ":":
                depth += 1
            elif indent == 0 and depth:
                depth = 0
                if key == path[0] + ":":
                    depth = 1
            continue
        if indent < 2 * depth:
            return False
        m = re.match(r"hook:\s*(\S+)$", key)
        if indent == 2 * depth and m:
            return m.group(1).strip("\"'").lower() == "true"
    return False


def secrets_guard_enabled(root: Path) -> bool:
    """`secrets_guard.enabled: true`: l'unico parser e' quello dell'oracolo (secrets_guard.enabled).
    Se l'oracolo non e' presente nel repo il flag vale false (nessun hook da installare)."""
    guardia = Path(__file__).resolve().parent.parent / "security" / "secrets_guard.py"
    if not guardia.is_file():
        return False
    spec = importlib.util.spec_from_file_location("secrets_guard_oracolo", str(guardia))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return bool(mod.enabled(str(root)))


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _prompt(msg: str) -> str:
    try:
        with open("/dev/tty", "r", encoding="utf-8") as tty:
            sys.stdout.write(msg)
            sys.stdout.flush()
            return tty.readline().strip()
    except OSError:
        return input(msg).strip()


def _factory_hooks_dir(root: Path) -> Path:
    """Directory hooks letta da git (comune a tutti i worktree, rispetta core.hooksPath).

    Da un worktree il file .git punta a .git/worktrees/<nome>, la cui cartella hooks git non
    legge: per questo si chiede a git. Il calcolo dal file .git resta come riserva.
    """
    try:
        r = subprocess.run(["git", "-C", str(root), "rev-parse", "--path-format=absolute",
                            "--git-path", "hooks"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    except OSError:
        r = None
    if r is not None and r.returncode == 0 and r.stdout.strip():
        return Path(r.stdout.strip())
    git_marker = root / ".git"
    if git_marker.is_file():
        raw = git_marker.read_text(encoding="utf-8").strip()
        gitdir = raw.split("gitdir:", 1)[1].strip() if "gitdir:" in raw else raw
        gitdir_path = Path(gitdir)
        if not gitdir_path.is_absolute():
            gitdir_path = (root / gitdir_path).resolve()
        return gitdir_path / "hooks"
    return git_marker / "hooks"


def _install(name: str, content: str, hooks_dir: Path,
             dry_run: bool, force: bool) -> str:
    """Ritorna 'installed' | 'skipped' | 'conflict'."""
    hook_path = hooks_dir / name
    expected = _sha256(content.encode("utf-8"))

    crlf_only = False
    if hook_path.exists():
        raw = hook_path.read_bytes()
        if _sha256(raw) == expected:
            print("  " + color.green(f"OK -- {name} gia' aggiornato (checksum identico)."))
            return "skipped"
        crlf_only = _sha256(to_lf(raw)) == expected
    if crlf_only:
        print("  " + color.yellow(f"{name} identico ma con fine riga CRLF: lo riscrivo con LF."))
    elif hook_path.exists():
        print("  " + color.yellow(f"ATTENZIONE -- esiste un {name} diverso: {hook_path}"))
        if dry_run:
            print("  " + color.yellow("[dry-run] Sovrascrittura richiesta -- esegui senza --dry-run."))
            return "conflict"
        if not force:
            if _prompt(f"  Sovrascrivere il hook {name} esistente? [y/N] ") not in ("y", "Y"):
                print("  " + color.yellow(f"SKIP -- {name} non sovrascritto."))
                return "skipped"
        else:
            print("  " + color.yellow(f"--force: sovrascrittura di {name}."))

    if dry_run:
        print("  " + color.cyan(f"[dry-run] Installerebbe {name} in: {hook_path}"))
        return "skipped"

    write_hook(hook_path, content)
    hook_path.chmod(0o755)
    print("  " + color.green(f"Installato: {hook_path}"))
    return "installed"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Installa gli hook del repo padre (auto-align submodule).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostra cosa verrebbe installato.")
    parser.add_argument("--force", action="store_true",
                        help="Sovrascrive senza prompt.")
    parser.add_argument("--only", choices=sorted(set(HOOKS) | {"pre-commit"}),
                        help="Installa solo questo hook (niente altri hook ne' merge driver).")
    parser.add_argument("--root", help=argparse.SUPPRESS)  # test
    args = parser.parse_args(argv)

    root = Path(args.root) if args.root else factory_root()
    if args.only:
        hooks_dir = _factory_hooks_dir(root)
        if not args.dry_run:
            hooks_dir.mkdir(parents=True, exist_ok=True)
        print(color.cyan(args.only) + ":")
        content = PRE_COMMIT_HOOK if args.only == "pre-commit" else HOOKS[args.only]
        esito = _install(args.only, content, hooks_dir, args.dry_run, args.force)
        return 1 if esito == "conflict" else 0
    hooks_dir = _factory_hooks_dir(root)
    if not hooks_dir.is_dir():
        if args.dry_run:
            print(color.yellow(f"[dry-run] Creerebbe directory: {hooks_dir}"))
        else:
            hooks_dir.mkdir(parents=True, exist_ok=True)

    print(color.cyan(f"Repo padre: {root}"))
    print(color.cyan(f"Hooks dir : {hooks_dir}"))
    print()

    # il pre-commit parte sempre: la guardia dei marcatori non ha flag; log e segreti restano opt-in
    hooks = dict(HOOKS)
    hooks["pre-commit"] = PRE_COMMIT_HOOK

    installed = skipped = conflicts = 0
    for name, content in hooks.items():
        print(color.cyan(name) + ":")
        outcome = _install(name, content, hooks_dir, args.dry_run, args.force)
        installed += outcome == "installed"
        skipped += outcome == "skipped"
        conflicts += outcome == "conflict"

    print(color.cyan("merge driver (git config locale):"))
    ensure_merge_drivers(root, dry_run=args.dry_run, overwrite=True, quiet=False)
    print()
    if args.dry_run:
        print(color.cyan(
            f"[dry-run] Riepilogo: {installed} da installare, {skipped} skip, "
            f"{conflicts} conflitti."))
        print(color.yellow("Esegui senza --dry-run per procedere."))
    else:
        print(color.green(f"Riepilogo: {installed} hook installati, {skipped} skip."))
        if installed:
            print(color.yellow(
                "Gli hook sono locali (.git/hooks non e' versionato): ogni collaboratore "
                "deve eseguire questo installer una volta."))
    return 0


if __name__ == "__main__":
    sys.exit(main())

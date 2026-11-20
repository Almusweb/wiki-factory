#!/usr/bin/env python3
"""wsl_proxy.py — proxy lato Windows per raggiungere da WSL gli host interni dietro la VPN aziendale.

Con la VPN attiva, gli host interni (ambienti di test, collaudo e simili) rispondono ai processi Windows ma
non a quelli di WSL. Questo comando avvia sul Python di Windows un piccolo proxy (`winproxy.py`) in
ascolto solo su 127.0.0.1; in WSL (networkingMode=mirrored) curl, npm e il browser di Playwright ci
passano e il traffico esce dalla rete di Windows. Guida completa: `tools/README-wsl-vpn.md`.

Sotto-comandi:
  start  [--port N]             avvia il proxy (idempotente: se e' gia' attivo lo riporta e basta).
                                Porta di default 18765; se occupata prova le successive (fino a +20).
  stop   [--force]              ferma il proxy avviato da questo comando. Rifiuta se ha connessioni
                                aperte (qualcuno lo sta usando), salvo --force.
  status [--url U] [--no-check] stato del proxy e prova di raggiungibilita' di un host interno via proxy.
                                Senza --url ne' WSL_PROXY_CHECK_URL la prova si salta e lo si dichiara.
  env    [--port N]             righe `export` per la shell: HTTPS_PROXY/HTTP_PROXY/NO_PROXY e, se
                                presenti, le librerie per Chromium di Playwright (LD_LIBRARY_PATH).
                                Uso: eval "$(python3 tools/env/wsl_proxy.py env)"
  playwright-config BASE [--port N]
                                scrive accanto a BASE una config `<nome>.proxy.local.ts` che estende BASE
                                con `use.proxy`. I file `*.proxy.local.ts` sono ignorati da git.

Opzioni comuni: --json (risultato in JSON su stdout). Diagnostica su stderr.
Exit: 0 ok; 1 esito negativo (proxy non attivo, in uso, host non raggiungibile); 2 errore
(non e' WSL, Python di Windows assente, rete WSL non mirrored, comando in timeout).

Nessun percorso o nome utente cablato: Python, cartella temporanea e profilo di Windows si leggono a
runtime. Variabili facoltative: WSL_PROXY_WINDOWS_PYTHON (python.exe da usare, percorso Windows o WSL),
WSL_PROXY_CHECK_URL (host della prova di status), WSL_PROXY_STATE_DIR (dove salvare lo stato).
Nessuna credenziale letta o scritta.

Un solo proxy per Windows: lo stato e' per utente WSL (o per WSL_PROXY_STATE_DIR), ma con networkingMode=mirrored
la porta su 127.0.0.1 e' quella di Windows, condivisa da tutte le distro. Per questo start, prima di avviarne uno
nuovo, cerca fra i processi di Windows un winproxy.py gia' avviato da questo comando (anche da un'altra distro o
con un'altra cartella di stato) e, se ascolta, lo adotta invece di aprire una seconda porta. stop di una distro
ferma il proxy anche per le altre: per questo rifiuta se ci sono connessioni aperte.
"""
from __future__ import annotations

import argparse
import filecmp
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_PORT = 18765
PORT_TRIES = 20
# Nessun host di prova cablato: dipende dalla rete di chi usa la factory (--url o WSL_PROXY_CHECK_URL).
PROXY_SCRIPT = Path(__file__).resolve().parent / "winproxy.py"
WIN_SUBDIR = "factory-wsl-proxy"
CMD_TIMEOUT = 30
START_WAIT = 10  # secondi di attesa perche' il proxy appena avviato ascolti
SYSLIBS = Path.home() / ".cache/ms-playwright/syslibs/root/usr/lib/x86_64-linux-gnu"


class ToolError(Exception):
    """Errore che termina il comando con exit 2."""


# --------------------------------------------------------------------------- comandi esterni

def run_status(cmd: list[str], timeout: int = CMD_TIMEOUT) -> tuple[int, str, str]:
    """Esegue un comando (lista, niente shell) e ritorna (exit, stdout, stderr); errore solo su timeout o assenza."""
    # i .exe di Windows lanciati da una cartella WSL avvisano del percorso UNC: si parte da /mnt/c se c'e'
    cwd = "/mnt/c" if cmd[0].endswith(".exe") and os.path.isdir("/mnt/c") else None
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
    except subprocess.TimeoutExpired as e:
        raise ToolError(f"timeout dopo {timeout}s: {cmd[0]} {' '.join(cmd[1:3])}") from e
    except FileNotFoundError as e:
        raise ToolError(f"comando non trovato: {cmd[0]}") from e
    return p.returncode, p.stdout.replace("\r", ""), p.stderr.replace("\r", "")


def run(cmd: list[str], timeout: int = CMD_TIMEOUT) -> str:
    """Esegue un comando (lista, niente shell) e ritorna stdout; errore leggibile su exit != 0 o timeout."""
    rc, out, err = run_status(cmd, timeout)
    if rc != 0:
        msg = (err or out).strip()[:400]
        raise ToolError(f"{cmd[0]} {' '.join(cmd[1:3])}: exit {rc}: {msg}")
    return out


def powershell(script: str, timeout: int = CMD_TIMEOUT) -> str:
    return run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script], timeout).strip()


def ps_quote(s: str) -> str:
    """Stringa PowerShell fra apici singoli."""
    return "'" + s.replace("'", "''") + "'"


def wslpath(path: str, to_windows: bool = False) -> str:
    return run(["wslpath", "-w" if to_windows else "-u", path]).strip()


def win_cmdline(exe: str, args: list[str], log: str) -> str:
    """Riga di comando cmd.exe che lancia exe con args e manda stdout e stderr nel log."""
    q = lambda s: f'"{s}"' if (" " in s or "\\" in s) else s  # noqa: E731
    inner = " ".join([q(exe), *(q(x) for x in args)])
    return f'cmd.exe /d /c "{inner} > "{log}" 2>&1"'


def spawn_hidden(exe: str, args: list[str], log: str, cwd: str) -> int:
    """Avvia un processo Windows staccato da WSL e senza finestra; ritorna il PID (di cmd.exe).

    Win32_Process.Create non fa ereditare handle al figlio: con Start-Process e la redirezione l'interop
    di WSL resterebbe appesa finche' il proxy vive. Il processo appartiene a Windows e sopravvive alla
    chiusura della shell WSL.
    """
    out = powershell(
        "$si = New-CimInstance -ClassName Win32_ProcessStartup -ClientOnly -Property @{ShowWindow=[uint16]0}; "
        "$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments "
        f"@{{CommandLine={ps_quote(win_cmdline(exe, args, log))}; CurrentDirectory={ps_quote(cwd)}; "
        "ProcessStartupInformation=$si}; \"$($r.ReturnValue) $($r.ProcessId)\"")
    try:
        rv, pid = (int(x) for x in out.split()[-2:])
    except ValueError as e:
        raise ToolError(f"Win32_Process.Create: risposta non leggibile: {out[:120]}") from e
    if rv != 0:
        raise ToolError(f"Win32_Process.Create: ReturnValue {rv}")
    return pid


# --------------------------------------------------------------------------- ambiente Windows

def is_wsl() -> bool:
    if os.environ.get("WSL_DISTRO_NAME"):
        return True
    try:
        return "microsoft" in Path("/proc/version").read_text().lower()
    except OSError:
        return False


def windows_env() -> dict[str, str]:
    """%TEMP% e %USERPROFILE% di Windows, letti in una sola chiamata."""
    out = run(["cmd.exe", "/c", "echo %TEMP%& echo %USERPROFILE%"]).strip().splitlines()
    if len(out) < 2 or "%" in out[0]:
        raise ToolError("cmd.exe non ha restituito %TEMP% e %USERPROFILE%")
    return {"TEMP": out[0].strip(), "USERPROFILE": out[1].strip()}


def pick_python(where_output: str) -> tuple[str, list[str]] | None:
    """Sceglie l'interprete dall'output di `where python py`: python.exe vero, poi il launcher py.exe.

    Gli alias del Microsoft Store (cartella WindowsApps) sono esclusi: senza Python installato aprono lo Store.
    """
    lines = [l.strip() for l in where_output.splitlines() if l.strip().lower().endswith(".exe")]
    real = [l for l in lines if "\\windowsapps\\" not in l.lower()]
    for l in real:
        if l.lower().endswith("\\python.exe"):
            return l, []
    for l in real:
        if l.lower().endswith("\\py.exe"):
            return l, ["-3"]
    return None


def windows_python() -> tuple[str, list[str]]:
    """Percorso Windows del Python da usare e argomenti iniziali."""
    forced = os.environ.get("WSL_PROXY_WINDOWS_PYTHON")
    if forced:
        return (wslpath(forced, to_windows=True) if forced.startswith("/") else forced), []
    # `where` esce 1 se anche uno solo dei nomi manca (python.exe senza py.exe con conda, scoop, winget):
    # i percorsi trovati sono comunque su stdout, e si sceglie solo fra quelli (mai dallo stderr)
    _, out, _ = run_status(["cmd.exe", "/c", "where python py"])
    found = pick_python(out)
    if not found:
        raise ToolError("Python di Windows non trovato (where python py): installalo da python.org "
                        "o imposta WSL_PROXY_WINDOWS_PYTHON; vedi tools/README-wsl-vpn.md")
    return found


def networking_mode(wslconfig_text: str) -> str:
    """networkingMode della sezione [wsl2] di .wslconfig ('nat' se non dichiarato)."""
    section = ""
    for raw in wslconfig_text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip().lower()
        elif section == "wsl2" and "=" in line:
            k, v = (x.strip() for x in line.split("=", 1))
            if k.lower() == "networkingmode":
                return v.lower()
    return "nat"


def read_networking_mode(userprofile_win: str) -> str:
    path = Path(wslpath(userprofile_win)) / ".wslconfig"
    try:
        return networking_mode(path.read_text(errors="replace"))
    except FileNotFoundError:
        return "nat"


# --------------------------------------------------------------------------- stato e porte

def state_file() -> Path:
    base = os.environ.get("WSL_PROXY_STATE_DIR") or os.path.join(
        os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local/state"), "factory-wsl-proxy")
    return Path(base) / "state.json"


def load_state() -> dict | None:
    try:
        return json.loads(state_file().read_text())
    except FileNotFoundError:
        return None
    except (OSError, ValueError) as e:
        print(f"stato illeggibile ({state_file()}): {e}; lo ignoro", file=sys.stderr)
        return None


def save_state(state: dict) -> None:
    f = state_file()
    f.parent.mkdir(parents=True, exist_ok=True)
    tmp = f.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2))
    tmp.replace(f)


def clear_state() -> None:
    try:
        state_file().unlink()
    except FileNotFoundError:
        pass  # gia' assente: niente da pulire


def port_listening(port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=timeout):
            return True
    except OSError:
        return False


def choose_port(preferred: int, busy, tries: int = PORT_TRIES) -> int:
    for port in range(preferred, preferred + tries + 1):
        if not busy(port):
            return port
    raise ToolError(f"nessuna porta libera fra {preferred} e {preferred + tries}: usa --port")


def process_cmdline(pid: int) -> str | None:
    out = powershell(f"(Get-CimInstance Win32_Process -Filter \"ProcessId={int(pid)}\").CommandLine")
    return out or None


def is_proxy_cmdline(cmdline: str | None) -> bool:
    return bool(cmdline and WIN_SUBDIR in cmdline and "winproxy.py" in cmdline)


def pid_is_ours(state: dict | None) -> bool:
    """Il processo salvato nello stato esiste ed e' il nostro proxy (senza guardare la porta)."""
    if not state or not state.get("pid") or not state.get("port"):
        return False
    return is_proxy_cmdline(process_cmdline(state["pid"]))


def is_ours(state: dict | None) -> bool:
    """Il processo salvato nello stato esiste, e' il nostro proxy e ascolta sulla sua porta."""
    return pid_is_ours(state) and port_listening(state["port"])


def parse_running(output: str) -> list[tuple[int, int]]:
    """(pid, porta) dei winproxy.py avviati da questo comando, dall'elenco `pid<TAB>riga di comando`.

    Per ogni porta si tiene il cmd.exe che lo ha lanciato (e' il PID salvato da start: taskkill /T ferma anche
    il Python figlio); se manca, il python.exe.
    """
    found: dict[int, tuple[int, bool]] = {}
    for line in output.splitlines():
        pid_s, _, cmdline = line.partition("\t")
        m = re.search(r'winproxy\.py"?\s+(\d+)', cmdline)
        if not pid_s.strip().isdigit() or not m or not is_proxy_cmdline(cmdline):
            continue
        pid, port, is_cmd = int(pid_s), int(m.group(1)), cmdline.lower().lstrip('"').startswith("cmd.exe")
        if port not in found or (is_cmd and not found[port][1]):
            found[port] = (pid, is_cmd)
    return sorted((pid, port) for port, (pid, _) in found.items())


def running_proxies() -> list[tuple[int, int]]:
    """winproxy.py di questo comando in esecuzione su Windows, avviati da qualunque distro o cartella di stato."""
    out = powershell("Get-CimInstance Win32_Process -Filter \"CommandLine LIKE '%" + WIN_SUBDIR + "%winproxy.py%'\" "
                     "| ForEach-Object { \"$($_.ProcessId)`t$($_.CommandLine)\" }")
    return parse_running(out)


def kill_tree(pid: int) -> None:
    run(["taskkill.exe", "/PID", str(int(pid)), "/T", "/F"])


def established_connections(port: int) -> int:
    out = powershell(f"@(Get-NetTCPConnection -LocalPort {int(port)} -State Established "
                     f"-ErrorAction SilentlyContinue).Count")
    try:
        return int(out.splitlines()[-1]) if out else 0
    except ValueError as e:
        raise ToolError(f"conteggio connessioni non leggibile: {out[:80]}") from e


def health(port: int, url: str, timeout: int = 15) -> int | None:
    """Codice HTTP dell'host interno via proxy (anche 3xx/4xx = raggiungibile); None se non risponde."""
    proxy = f"http://127.0.0.1:{port}"
    if shutil.which("curl"):
        try:
            p = subprocess.run(["curl", "-sS", "-k", "-o", "/dev/null", "-w", "%{http_code}",
                                "--max-time", str(timeout), "-x", proxy, url],
                               capture_output=True, text=True, timeout=timeout + 5)
        except subprocess.TimeoutExpired:
            return None
        code = p.stdout.strip()
        return int(code) if code.isdigit() and code != "000" else None
    import ssl
    import urllib.error
    import urllib.request
    ctx = ssl.create_default_context()
    ctx.check_hostname, ctx.verify_mode = False, ssl.CERT_NONE

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None

    opener = urllib.request.build_opener(urllib.request.ProxyHandler({"https": proxy, "http": proxy}),
                                         urllib.request.HTTPSHandler(context=ctx), NoRedirect)
    try:
        return opener.open(url, timeout=timeout).status
    except urllib.error.HTTPError as e:
        return e.code
    except (urllib.error.URLError, OSError):
        return None


# --------------------------------------------------------------------------- comandi

def emit(result: dict, as_json: bool, text: str) -> None:
    print(json.dumps(result, ensure_ascii=False) if as_json else text)


def require_wsl() -> dict[str, str]:
    if not is_wsl():
        raise ToolError("non sei in WSL: su Windows, macOS e Linux nativo il proxy non serve")
    env = windows_env()
    mode = read_networking_mode(env["USERPROFILE"])
    if mode != "mirrored":
        raise ToolError(f"networkingMode di WSL e' '{mode}': serve 'mirrored' in %USERPROFILE%\\.wslconfig "
                        "(sezione [wsl2]), poi `wsl --shutdown`; vedi tools/README-wsl-vpn.md")
    return env


def wait_listening(port: int, seconds: float) -> bool:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline and not port_listening(port):
        time.sleep(0.3)
    return port_listening(port)


def cmd_start(a) -> int:
    state = load_state()
    if pid_is_ours(state):
        # processo vivo: se la prova veloce della porta e' scaduta si aspetta, mai un secondo proxy
        if not wait_listening(state["port"], START_WAIT):
            raise ToolError(f"il proxy (pid {state['pid']}) e' vivo ma non ascolta su {state['port']}: "
                            f"vedi {state.get('log', 'il log in %TEMP%')}, poi stop --force e start")
        emit({"status": "running", "already": True, **state}, a.json,
             f"proxy gia' attivo su 127.0.0.1:{state['port']} (pid Windows {state['pid']})")
        return 0
    env = require_wsl()
    adopted = [(pid, port) for pid, port in running_proxies() if port_listening(port)]
    if adopted:
        pid, port = adopted[0]
        state = {"port": port, "pid": pid, "adopted": True,
                 "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        save_state(state)
        emit({"status": "running", "already": True, **state}, a.json,
             f"proxy gia' attivo su 127.0.0.1:{port} (pid Windows {pid}), avviato da un'altra shell o distro: "
             "lo uso")
        return 0
    py, py_args = windows_python()
    win_dir = env["TEMP"].rstrip("\\") + "\\" + WIN_SUBDIR
    local_dir = Path(wslpath(win_dir))
    local_dir.mkdir(parents=True, exist_ok=True)
    target = local_dir / "winproxy.py"
    if not target.exists() or not filecmp.cmp(PROXY_SCRIPT, target, shallow=False):
        shutil.copyfile(PROXY_SCRIPT, target)
        print(f"copiato winproxy.py in {win_dir}", file=sys.stderr)
    port = choose_port(a.port, port_listening)
    if port != a.port:
        print(f"porta {a.port} occupata: uso {port}", file=sys.stderr)
    script_win, log_win = win_dir + "\\winproxy.py", win_dir + f"\\winproxy-{port}.log"
    pid = spawn_hidden(py, [*py_args, "-u", script_win, str(port)], log_win, win_dir)
    state = {"port": port, "pid": pid, "python": py, "script": script_win, "log": log_win,
             "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    if not wait_listening(port, START_WAIT):
        # avvio lento (Defender, primo avvio a freddo): niente proxy orfano sulla porta
        try:
            kill_tree(pid)
        except ToolError as e:
            save_state(state)  # non fermato: stop deve poterlo trovare
            raise ToolError(f"il proxy (pid {pid}) non ascolta su {port} dopo {START_WAIT}s e non si e' fermato "
                            f"({e}): stato salvato, usa stop --force; vedi {log_win}") from e
        raise ToolError(f"il proxy (pid {pid}) non ascolta su {port} dopo {START_WAIT}s: fermato. "
                        f"Riprova start; vedi {log_win}")
    save_state(state)
    emit({"status": "running", "already": False, **state}, a.json,
         f"proxy avviato su 127.0.0.1:{port} (pid Windows {pid})\n"
         f"prossimo passo: eval \"$(python3 tools/env/wsl_proxy.py env)\"")
    return 0


def cmd_stop(a) -> int:
    state = load_state()
    # si guarda il PID, non la porta: una prova di connessione scaduta non vuol dire che il proxy sia morto
    if not pid_is_ours(state):
        clear_state()
        emit({"status": "stopped", "was_running": False}, a.json, "proxy non attivo: niente da fermare")
        return 0
    conns = established_connections(state["port"])
    if conns and not a.force:
        emit({"status": "in_use", "port": state["port"], "pid": state["pid"], "connections": conns}, a.json,
             f"proxy in uso ({conns} connessioni aperte su {state['port']}): non lo fermo. "
             "Aspetta che finiscano i giri in corso, oppure --force")
        return 1
    kill_tree(state["pid"])
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and port_listening(state["port"]):
        time.sleep(0.2)
    if port_listening(state["port"]):
        raise ToolError(f"la porta {state['port']} risponde ancora dopo lo stop del pid {state['pid']}")
    clear_state()
    emit({"status": "stopped", "was_running": True, "port": state["port"], "pid": state["pid"]}, a.json,
         f"proxy fermato (porta {state['port']}, pid Windows {state['pid']})")
    return 0


def cmd_status(a) -> int:
    state = load_state()
    running = is_ours(state)
    result: dict = {"status": "running" if running else "stopped"}
    if not running:
        emit(result, a.json, "proxy non attivo: python3 tools/env/wsl_proxy.py start")
        return 1
    result.update(state)
    if a.no_check:
        emit(result, a.json, f"proxy attivo su 127.0.0.1:{state['port']} (pid Windows {state['pid']})")
        return 0
    url = a.url or os.environ.get("WSL_PROXY_CHECK_URL")
    if not url:
        result["check"] = "skipped"
        emit(result, a.json, f"proxy attivo su 127.0.0.1:{state['port']} (pid Windows {state['pid']}); "
             "prova di raggiungibilita' saltata: nessun host indicato (--url o WSL_PROXY_CHECK_URL)")
        return 0
    code = health(state["port"], url)
    result.update({"check_url": url, "http_code": code, "reachable": code is not None})
    emit(result, a.json,
         f"proxy attivo su 127.0.0.1:{state['port']} (pid Windows {state['pid']}); "
         + (f"{url} -> HTTP {code}" if code else f"{url} NON raggiungibile: VPN attiva lato Windows?"))
    return 0 if code else 1


def resolve_port(a) -> int:
    if a.port:
        return a.port
    state = load_state()
    if state and state.get("port"):
        port = int(state["port"])
        # dopo un riavvio di Windows lo stato resta ma il proxy no: meglio dirlo che dare una porta morta
        if not port_listening(port, timeout=1.0):
            raise ToolError(f"proxy non attivo (porta salvata {port}, nessuno ascolta): "
                            "python3 tools/env/wsl_proxy.py start")
        return port
    raise ToolError("proxy non avviato e --port non indicata: python3 tools/env/wsl_proxy.py start")


def env_lines(port: int, syslibs: Path | None) -> list[str]:
    proxy = f"http://127.0.0.1:{port}"
    lines = [f"export {k}={proxy}" for k in ("HTTPS_PROXY", "HTTP_PROXY", "https_proxy", "http_proxy")]
    lines += [f"export {k}=localhost,127.0.0.1,::1" for k in ("NO_PROXY", "no_proxy")]
    lines.append(f"export WSL_PROXY_URL={proxy}")
    if syslibs is not None:
        lines.append(f'export LD_LIBRARY_PATH="{syslibs}${{LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}}"')
    return lines


def cmd_env(a) -> int:
    port = resolve_port(a)
    syslibs = SYSLIBS if SYSLIBS.is_dir() else None
    if syslibs is None:
        print(f"# {SYSLIBS} assente: LD_LIBRARY_PATH non impostata (serve solo se Chromium non parte)",
              file=sys.stderr)
    lines = env_lines(port, syslibs)
    emit({"port": port, "exports": lines}, a.json, "\n".join(lines))
    return 0


def playwright_config_text(base_name: str, port: int) -> str:
    return (
        "// Generato da tools/env/wsl_proxy.py playwright-config: non versionare (*.proxy.local.ts e' in .gitignore).\n"
        f"// Estende {base_name} facendo passare il browser dal proxy lato Windows (guida: tools/README-wsl-vpn.md).\n"
        f"import base from './{base_name}';\n\n"
        f"const server = process.env.WSL_PROXY_URL ?? 'http://127.0.0.1:{port}';\n"
        "export default { ...base, use: { ...base.use, proxy: { server, bypass: 'localhost,127.0.0.1' } } };\n"
    )


def cmd_playwright_config(a) -> int:
    base = Path(a.base).resolve()
    if not base.is_file() or base.suffix != ".ts":
        raise ToolError(f"config di partenza non trovata o non .ts: {a.base}")
    if base.name.endswith(".proxy.local.ts"):
        raise ToolError("la config indicata e' gia' una config del proxy")
    port = resolve_port(a)
    out = base.with_name(base.name[:-3] + ".proxy.local.ts")
    text = playwright_config_text(base.stem, port)
    changed = not out.exists() or out.read_text() != text
    if changed:
        out.write_text(text)
    rel = os.path.relpath(out, Path.cwd())
    emit({"config": str(out), "port": port, "written": changed}, a.json,
         f"{rel}\nuso: npx playwright test -c {out.name} (da {os.path.relpath(out.parent, Path.cwd())}/, con le variabili di `env`)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="wsl_proxy.py", description="Proxy lato Windows per raggiungere la VPN da WSL.")
    sub = p.add_subparsers(dest="cmd", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", help="risultato in JSON su stdout")
    s = sub.add_parser("start", parents=[common], help="avvia il proxy (idempotente)")
    s.add_argument("--port", type=int, default=DEFAULT_PORT)
    s = sub.add_parser("stop", parents=[common], help="ferma il proxy")
    s.add_argument("--force", action="store_true", help="ferma anche con connessioni aperte")
    s = sub.add_parser("status", parents=[common], help="stato e prova di raggiungibilita'")
    s.add_argument("--url", help="host interno da provare (default: WSL_PROXY_CHECK_URL; senza, la prova si salta)")
    s.add_argument("--no-check", action="store_true", help="solo stato, senza prova di rete")
    s = sub.add_parser("env", parents=[common], help="righe export per la shell")
    s.add_argument("--port", type=int)
    s = sub.add_parser("playwright-config", parents=[common], help="config Playwright locale con il proxy")
    s.add_argument("base", help="config Playwright di partenza (es. tests/e2e/playwright.config.staging.ts)")
    s.add_argument("--port", type=int)
    return p


COMMANDS = {"start": cmd_start, "stop": cmd_stop, "status": cmd_status, "env": cmd_env,
            "playwright-config": cmd_playwright_config}


def main(argv: list[str] | None = None) -> int:
    a = build_parser().parse_args(argv)
    try:
        return COMMANDS[a.cmd](a)
    except ToolError as e:
        if getattr(a, "json", False):
            print(json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False))
        print(f"wsl_proxy: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

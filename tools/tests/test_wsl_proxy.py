"""Test per tools/env/wsl_proxy.py e tools/env/winproxy.py (proxy WSL verso la VPN lato Windows).

Copertura:
  - funzioni pure: scelta del Python di Windows, networkingMode di .wslconfig, scelta della porta,
    righe di export, riga di comando cmd.exe, testo della config Playwright
  - comandi: exit code e JSON (errore, proxy non attivo, start idempotente), timeout simulato,
    playwright-config idempotente e rifiuto di una config gia' generata
  - casi limite di start/stop/env: `where` con exit 1, avvio lento senza proxy orfano, stop con la prova
    della porta scaduta, porta salvata morta, proxy gia' avviato da un'altra distro, esclusione in .gitignore
  - winproxy.py eseguito con il Python locale: tunnel CONNECT e richiesta HTTP con URL assoluto
Nessun test richiede Windows, la VPN o la rete esterna.
"""
from __future__ import annotations

import contextlib
import http.server
import io
import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "env"))

import wsl_proxy as W  # noqa: E402

WINPROXY = Path(W.__file__).resolve().parent / "winproxy.py"


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def call(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = W.main(argv)
    return rc, out.getvalue(), err.getvalue()


class PurePieces(unittest.TestCase):
    def test_pick_python_prefers_real_python_and_skips_store_alias(self):
        where = ("C:\\Users\\u\\AppData\\Local\\Microsoft\\WindowsApps\\python.exe\r\n"
                 "C:\\Users\\u\\AppData\\Local\\Programs\\Python\\Python314\\python.exe\r\n"
                 "C:\\Users\\u\\AppData\\Local\\Programs\\Python\\Launcher\\py.exe\r\n")
        self.assertEqual(W.pick_python(where), ("C:\\Users\\u\\AppData\\Local\\Programs\\Python\\Python314\\python.exe", []))

    def test_pick_python_falls_back_to_launcher(self):
        where = "C:\\Windows\\py.exe\nC:\\Users\\u\\AppData\\Local\\Microsoft\\WindowsApps\\python.exe\n"
        self.assertEqual(W.pick_python(where), ("C:\\Windows\\py.exe", ["-3"]))

    def test_pick_python_only_store_alias_is_none(self):
        self.assertIsNone(W.pick_python("C:\\Users\\u\\AppData\\Local\\Microsoft\\WindowsApps\\python.exe\n"))
        self.assertIsNone(W.pick_python("INFO: Could not find files for the given pattern(s).\n"))

    def test_networking_mode(self):
        self.assertEqual(W.networking_mode("[wsl2]\nnetworkingMode=mirrored\ndnsTunneling=true\n"), "mirrored")
        self.assertEqual(W.networking_mode("[wsl2]\n# networkingMode=mirrored\nmemory=8GB\n"), "nat")
        self.assertEqual(W.networking_mode("[experimental]\nnetworkingMode=mirrored\n"), "nat")
        self.assertEqual(W.networking_mode("[WSL2]\n NetworkingMode = Mirrored \n"), "mirrored")

    def test_choose_port_skips_busy_ports(self):
        self.assertEqual(W.choose_port(18765, lambda p: False), 18765)
        self.assertEqual(W.choose_port(18765, lambda p: p < 18768), 18768)
        with self.assertRaises(W.ToolError):
            W.choose_port(18765, lambda p: True, tries=3)

    def test_env_lines(self):
        lines = W.env_lines(18765, None)
        self.assertIn("export HTTPS_PROXY=http://127.0.0.1:18765", lines)
        self.assertIn("export no_proxy=localhost,127.0.0.1,::1", lines)
        self.assertFalse(any("LD_LIBRARY_PATH" in l for l in lines))
        self.assertTrue(any(l.startswith('export LD_LIBRARY_PATH="/x/lib$') for l in W.env_lines(1, Path("/x/lib"))))

    def test_win_cmdline_quotes_paths_and_redirects(self):
        line = W.win_cmdline("C:\\Py 3\\python.exe", ["-u", "C:\\T\\winproxy.py", "18765"], "C:\\T\\w.log")
        self.assertEqual(line, 'cmd.exe /d /c ""C:\\Py 3\\python.exe" -u "C:\\T\\winproxy.py" 18765 > "C:\\T\\w.log" 2>&1"')

    def test_parse_running_keeps_cmd_parent_per_port(self):
        out = ('101\tcmd.exe /d /c "C:\\Py\\python.exe -u C:\\T\\factory-wsl-proxy\\winproxy.py 18765 > x 2>&1"\n'
               '102\tC:\\Py\\python.exe -u C:\\T\\factory-wsl-proxy\\winproxy.py 18765\n'
               '200\t"C:\\Py\\python.exe" -u "C:\\T\\factory-wsl-proxy\\winproxy.py" 18766\n'
               '300\tC:\\Py\\python.exe altro.py 18767\n')
        self.assertEqual(W.parse_running(out), [(101, 18765), (200, 18766)])

    def test_playwright_config_text(self):
        text = W.playwright_config_text("playwright.config.staging", 18770)
        self.assertIn("import base from './playwright.config.staging';", text)
        self.assertIn("process.env.WSL_PROXY_URL ?? 'http://127.0.0.1:18770'", text)
        self.assertIn("...base.use, proxy:", text)


class Commands(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = mock.patch.dict(os.environ, {"WSL_PROXY_STATE_DIR": self.tmp.name})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def test_start_outside_wsl_is_error_exit_2_with_json(self):
        with mock.patch.object(W, "is_wsl", return_value=False):
            rc, out, err = call(["start", "--json"])
        self.assertEqual(rc, 2)
        self.assertEqual(json.loads(out)["status"], "error")
        self.assertIn("non sei in WSL", err)

    def test_status_without_proxy_is_exit_1(self):
        rc, out, _ = call(["status", "--json", "--no-check"])
        self.assertEqual(rc, 1)
        self.assertEqual(json.loads(out), {"status": "stopped"})

    def test_stop_without_proxy_is_ok_and_idempotent(self):
        for _ in range(2):
            rc, out, _ = call(["stop", "--json"])
            self.assertEqual(rc, 0)
            self.assertEqual(json.loads(out)["was_running"], False)

    def test_start_is_idempotent_when_already_running(self):
        W.save_state({"port": 18765, "pid": 42})
        with mock.patch.object(W, "pid_is_ours", return_value=True), \
                mock.patch.object(W, "port_listening", return_value=True), \
                mock.patch.object(W, "spawn_hidden", side_effect=AssertionError("non deve avviare")):
            rc, out, _ = call(["start", "--json"])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(out)["already"], True)

    def test_stop_refuses_when_in_use(self):
        W.save_state({"port": 18765, "pid": 42})
        with mock.patch.object(W, "pid_is_ours", return_value=True), \
                mock.patch.object(W, "established_connections", return_value=3), \
                mock.patch.object(W, "run", side_effect=AssertionError("non deve fermare")):
            rc, out, _ = call(["stop", "--json"])
        self.assertEqual(rc, 1)
        self.assertEqual(json.loads(out)["status"], "in_use")

    def test_status_unreachable_host_is_exit_1(self):
        W.save_state({"port": 18765, "pid": 42})
        with mock.patch.object(W, "is_ours", return_value=True), mock.patch.object(W, "health", return_value=None):
            rc, out, _ = call(["status", "--json", "--url", "https://interno.example/"])
        self.assertEqual(rc, 1)
        self.assertEqual(json.loads(out)["reachable"], False)

    def test_status_without_check_url_skips_and_says_so(self):
        # nessun host di prova cablato: senza --url ne' WSL_PROXY_CHECK_URL la prova si salta, dichiarata
        W.save_state({"port": 18765, "pid": 42})
        env = {k: v for k, v in os.environ.items() if k != "WSL_PROXY_CHECK_URL"}
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch.object(W, "is_ours", return_value=True), \
                mock.patch.object(W, "health", side_effect=AssertionError("non deve sondare")):
            rc, out, _ = call(["status", "--json"])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(out)["check"], "skipped")

    def test_env_without_state_or_port_is_error(self):
        rc, out, _ = call(["env", "--json"])
        self.assertEqual(rc, 2)
        self.assertEqual(json.loads(out)["status"], "error")

    def test_env_uses_saved_port(self):
        W.save_state({"port": 18771, "pid": 1})
        with mock.patch.object(W, "port_listening", return_value=True):
            rc, out, _ = call(["env", "--json"])
        self.assertEqual(rc, 0)
        self.assertIn("export HTTPS_PROXY=http://127.0.0.1:18771", json.loads(out)["exports"])

    def test_timeout_is_reported_as_error(self):
        with self.assertRaises(W.ToolError) as cm:
            W.run([sys.executable, "-c", "import time; time.sleep(5)"], timeout=1)
        self.assertIn("timeout dopo 1s", str(cm.exception))

    def test_failing_command_reports_exit_code(self):
        with self.assertRaises(W.ToolError) as cm:
            W.run([sys.executable, "-c", "import sys; sys.stderr.write('boom'); sys.exit(3)"])
        self.assertIn("exit 3", str(cm.exception))
        self.assertIn("boom", str(cm.exception))

    def test_playwright_config_is_idempotent_and_refuses_generated_input(self):
        base = Path(self.tmp.name) / "playwright.config.staging.ts"
        base.write_text("export default {};\n")
        rc, out, _ = call(["playwright-config", str(base), "--port", "18765", "--json"])
        self.assertEqual((rc, json.loads(out)["written"]), (0, True))
        generated = Path(json.loads(out)["config"])
        self.assertEqual(generated.name, "playwright.config.staging.proxy.local.ts")
        rc, out, _ = call(["playwright-config", str(base), "--port", "18765", "--json"])
        self.assertEqual((rc, json.loads(out)["written"]), (0, False))
        rc, _, err = call(["playwright-config", str(generated), "--port", "18765"])
        self.assertEqual(rc, 2)
        self.assertIn("gia' una config del proxy", err)


    # --- casi limite segnalati in review

    def test_where_exit_1_still_uses_stdout_paths(self):
        found = "C:\\Users\\u\\miniconda3\\python.exe\n"
        missing = "INFO: Could not find files for the given pattern(s).\n"
        with mock.patch.dict(os.environ, {"WSL_PROXY_WINDOWS_PYTHON": ""}), \
                mock.patch.object(W, "run_status", return_value=(1, found, missing)):
            self.assertEqual(W.windows_python(), ("C:\\Users\\u\\miniconda3\\python.exe", []))
        with mock.patch.dict(os.environ, {"WSL_PROXY_WINDOWS_PYTHON": ""}), \
                mock.patch.object(W, "run_status", return_value=(1, "", missing)), \
                self.assertRaises(W.ToolError) as cm:
            W.windows_python()
        self.assertIn("Python di Windows non trovato", str(cm.exception))

    def _start_mocks(self, **extra):
        win = Path(self.tmp.name) / "win"
        patches = {"require_wsl": mock.Mock(return_value={"TEMP": "C:\\T", "USERPROFILE": "C:\\U"}),
                   "windows_python": mock.Mock(return_value=("C:\\Py\\python.exe", [])),
                   "wslpath": mock.Mock(return_value=str(win)), "running_proxies": mock.Mock(return_value=[]),
                   "spawn_hidden": mock.Mock(return_value=77), "port_listening": mock.Mock(return_value=False),
                   "START_WAIT": 0, **extra}
        return contextlib.ExitStack(), patches

    def _run_start(self, **extra):
        stack, patches = self._start_mocks(**extra)
        with stack:
            for name, value in patches.items():
                stack.enter_context(mock.patch.object(W, name, value))
            return call(["start", "--json"]), patches

    def test_slow_start_stops_the_process_and_saves_nothing(self):
        kill = mock.Mock()
        (rc, out, _), patches = self._run_start(kill_tree=kill)
        self.assertEqual(rc, 2)
        kill.assert_called_once_with(77)
        self.assertIn("fermato", json.loads(out)["error"])
        self.assertIsNone(W.load_state())

    def test_slow_start_that_cannot_be_stopped_saves_the_pid(self):
        (rc, out, _), _ = self._run_start(kill_tree=mock.Mock(side_effect=W.ToolError("accesso negato")))
        self.assertEqual(rc, 2)
        self.assertEqual(W.load_state()["pid"], 77)
        self.assertIn("stop --force", json.loads(out)["error"])

    def test_start_adopts_proxy_started_elsewhere(self):
        listening = mock.Mock(side_effect=lambda port, timeout=0.5: port == 18765)
        (rc, out, _), patches = self._run_start(running_proxies=mock.Mock(return_value=[(500, 18765)]),
                                                port_listening=listening)
        self.assertEqual(rc, 0)
        patches["spawn_hidden"].assert_not_called()
        self.assertEqual({k: W.load_state()[k] for k in ("pid", "port", "adopted")},
                         {"pid": 500, "port": 18765, "adopted": True})

    def test_start_with_live_pid_and_slow_port_does_not_spawn_a_second_proxy(self):
        W.save_state({"port": 18765, "pid": 42})
        with mock.patch.object(W, "pid_is_ours", return_value=True), \
                mock.patch.object(W, "port_listening", return_value=False), mock.patch.object(W, "START_WAIT", 0), \
                mock.patch.object(W, "spawn_hidden", side_effect=AssertionError("non deve avviare")):
            rc, out, _ = call(["start", "--json"])
        self.assertEqual(rc, 2)
        self.assertIn("vivo ma non ascolta", json.loads(out)["error"])
        self.assertEqual(W.load_state()["pid"], 42)

    def test_stop_with_live_pid_and_expired_port_probe_stops_it(self):
        W.save_state({"port": 18765, "pid": 42})
        kill = mock.Mock()
        with mock.patch.object(W, "pid_is_ours", return_value=True), \
                mock.patch.object(W, "port_listening", return_value=False), \
                mock.patch.object(W, "established_connections", return_value=0), \
                mock.patch.object(W, "kill_tree", kill):
            rc, out, _ = call(["stop", "--json"])
        self.assertEqual((rc, json.loads(out)["was_running"]), (0, True))
        kill.assert_called_once_with(42)
        self.assertIsNone(W.load_state())

    def test_env_with_saved_port_but_no_listener_is_error(self):
        W.save_state({"port": free_port(), "pid": 1})
        rc, out, _ = call(["env", "--json"])
        self.assertEqual(rc, 2)
        self.assertIn("nessuno ascolta", json.loads(out)["error"])

    def test_generated_configs_are_ignored_by_the_root_gitignore(self):
        root = Path(__file__).resolve().parents[2] / ".gitignore"
        self.assertIn("*.proxy.local.ts", [l.strip() for l in root.read_text().splitlines()])


class _Hello(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = f"ciao {self.path}".encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        return  # silenzioso nei test


class WinproxyIntegration(unittest.TestCase):
    """winproxy.py usa solo la standard library: gira anche con il Python di Linux."""

    @classmethod
    def setUpClass(cls):
        cls.http = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Hello)
        threading.Thread(target=cls.http.serve_forever, daemon=True).start()
        cls.port = free_port()
        cls.proc = subprocess.Popen([sys.executable, "-u", str(WINPROXY), str(cls.port)],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and not W.port_listening(cls.port):
            time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        cls.proc.wait(timeout=10)
        cls.proc.stdout.close()
        cls.http.shutdown()
        cls.http.server_close()

    def test_listens_only_on_loopback(self):
        self.assertTrue(W.port_listening(self.port))
        out = subprocess.run(["ss", "-ltn", f"sport = :{self.port}"], capture_output=True, text=True, timeout=10).stdout \
            if os.path.exists("/usr/bin/ss") or os.path.exists("/bin/ss") else f"127.0.0.1:{self.port}"
        self.assertIn(f"127.0.0.1:{self.port}", out)
        self.assertNotIn(f"0.0.0.0:{self.port}", out)

    def test_connect_tunnel(self):
        target = self.http.server_address[1]
        with socket.create_connection(("127.0.0.1", self.port), timeout=5) as s:
            s.sendall(f"CONNECT 127.0.0.1:{target} HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n".encode())
            self.assertIn(b"200 Connection Established", s.recv(200))
            s.sendall(b"GET /tunnel HTTP/1.1\r\nHost: x\r\nConnection: close\r\n\r\n")
            data = b""
            while chunk := s.recv(4096):
                data += chunk
        self.assertIn(b"ciao /tunnel", data)

    def test_plain_http_with_absolute_url(self):
        target = self.http.server_address[1]
        with socket.create_connection(("127.0.0.1", self.port), timeout=5) as s:
            s.sendall(f"GET http://127.0.0.1:{target}/assoluto HTTP/1.1\r\nHost: x\r\nConnection: close\r\n\r\n".encode())
            data = b""
            while chunk := s.recv(4096):
                data += chunk
        self.assertIn(b"ciao /assoluto", data)

    def test_unreachable_target_gives_502(self):
        with socket.create_connection(("127.0.0.1", self.port), timeout=25) as s:
            s.sendall(f"CONNECT 127.0.0.1:{free_port()} HTTP/1.1\r\n\r\n".encode())
            self.assertIn(b"502", s.recv(200))


if __name__ == "__main__":
    unittest.main()

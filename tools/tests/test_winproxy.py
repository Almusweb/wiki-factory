"""Test per tools/env/winproxy.py: correzioni della review del proxy lato Windows.

Copertura:
  - una richiesta HTTP in chiaro per connessione: una seconda richiesta sulla stessa connessione verso un
    altro host non arriva al server della prima (Connection: close verso il server, connessione chiusa
    dopo la risposta)
  - parsing della destinazione: URL senza path ma con query, IPv6 fra parentesi quadre (CONNECT e HTTP)
  - half-close: con CONNECT, la fine dei dati del client (shutdown SHUT_WR) non chiude il server e la
    risposta arriva
  - riscrittura della riga di richiesta sui byte (target non ASCII intatto) e intestazioni hop-by-hop
    (Proxy-Connection, Keep-Alive e quelle elencate in Connection) non inoltrate
winproxy.py usa solo la standard library: gira anche con il Python di Linux. Nessun test richiede
Windows, la VPN o la rete esterna.
"""
from __future__ import annotations

import http.server
import os
import socket
import subprocess
import sys
import threading
import time
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "env"))

import winproxy as P  # noqa: E402

WINPROXY = Path(P.__file__).resolve()


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def listening(port: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def ipv6_loopback() -> bool:
    if not socket.has_ipv6:
        return False
    try:
        with socket.socket(socket.AF_INET6) as s:
            s.bind(("::1", 0))
        return True
    except OSError:
        return False


def read_all(s: socket.socket) -> bytes:
    data = b""
    try:
        while chunk := s.recv(4096):
            data += chunk
    except (ConnectionResetError, socket.timeout):
        pass
    return data


def make_handler(name: str, seen: list):
    class Echo(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"  # keep-alive: il server terrebbe aperta la connessione

        def do_GET(self):
            seen.append((self.path, dict(self.headers)))
            body = f"{name} {self.path}".encode("latin-1")
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            return  # silenzioso nei test

    return Echo


class _Ipv6Server(http.server.ThreadingHTTPServer):
    address_family = socket.AF_INET6


class RewriteRequest(unittest.TestCase):
    def test_query_without_path(self):
        host, port, out = P.rewrite_request(b"GET http://example.test?x=1 HTTP/1.1\r\nHost: example.test\r\n\r\n")
        self.assertEqual((host, port), ("example.test", 80))
        self.assertTrue(out.startswith(b"GET /?x=1 HTTP/1.1\r\n"))

    def test_host_only_and_fragment(self):
        _, _, out = P.rewrite_request(b"GET http://example.test:8080 HTTP/1.1\r\n\r\n")
        self.assertTrue(out.startswith(b"GET / HTTP/1.1\r\n"))
        _, _, out = P.rewrite_request(b"GET http://example.test/a?b=1#frammento HTTP/1.1\r\n\r\n")
        self.assertTrue(out.startswith(b"GET /a?b=1 HTTP/1.1\r\n"))

    def test_ipv6_absolute_url(self):
        host, port, out = P.rewrite_request(b"GET http://[::1]:8080/p HTTP/1.1\r\n\r\n")
        self.assertEqual((host, port), ("::1", 8080))
        self.assertTrue(out.startswith(b"GET /p HTTP/1.1\r\n"))
        self.assertEqual(P.rewrite_request(b"GET http://[::1]/ HTTP/1.1\r\n\r\n")[:2], ("::1", 80))

    def test_connect_target(self):
        self.assertEqual(P.split_hostport("[::1]:443"), ("::1", 443))
        self.assertEqual(P.split_hostport("api.example.test:8443"), ("api.example.test", 8443))
        with self.assertRaises(ValueError):
            P.split_hostport("api.example.test")

    def test_non_ascii_target_kept_as_bytes(self):
        raw = b"GET http://example.test/caff\xc3\xa8?q=\xe8 HTTP/1.1\r\nHost: example.test\r\n\r\n"
        _, _, out = P.rewrite_request(raw)
        self.assertTrue(out.startswith(b"GET /caff\xc3\xa8?q=\xe8 HTTP/1.1\r\n"))

    def test_hop_by_hop_headers_not_forwarded(self):
        raw = (b"GET http://example.test/ HTTP/1.1\r\nHost: example.test\r\nProxy-Connection: keep-alive\r\n"
               b"Connection: keep-alive, X-Solo-Proxy\r\nKeep-Alive: timeout=5\r\nX-Solo-Proxy: 1\r\n"
               b"Accept: */*\r\n\r\n")
        _, _, out = P.rewrite_request(raw)
        lowered = out.lower()
        for name in (b"proxy-connection", b"keep-alive", b"x-solo-proxy", b"connection: keep-alive"):
            self.assertNotIn(name, lowered)
        self.assertIn(b"\r\nHost: example.test\r\n", out)
        self.assertIn(b"\r\nAccept: */*\r\n", out)
        self.assertTrue(out.endswith(b"\r\nConnection: close\r\n\r\n"))

    def test_rejects_non_http_scheme(self):
        with self.assertRaises(ValueError):
            P.rewrite_request(b"GET ftp://example.test/ HTTP/1.1\r\n\r\n")
        with self.assertRaises(ValueError):
            P.rewrite_request(b"GET /relativo HTTP/1.1\r\n\r\n")


class WinproxyLive(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seen_a, cls.seen_b = [], []
        cls.srv_a = http.server.ThreadingHTTPServer(("127.0.0.1", 0), make_handler("A", cls.seen_a))
        cls.srv_b = http.server.ThreadingHTTPServer(("127.0.0.1", 0), make_handler("B", cls.seen_b))
        for srv in (cls.srv_a, cls.srv_b):
            threading.Thread(target=srv.serve_forever, daemon=True).start()
        cls.port = free_port()
        cls.proc = subprocess.Popen([sys.executable, "-u", str(WINPROXY), str(cls.port)],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and not listening(cls.port):
            time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        cls.proc.wait(timeout=10)
        cls.proc.stdout.close()
        for srv in (cls.srv_a, cls.srv_b):
            srv.shutdown()
            srv.server_close()

    def setUp(self):
        self.seen_a.clear()
        self.seen_b.clear()

    def proxy(self) -> socket.socket:
        s = socket.create_connection(("127.0.0.1", self.port), timeout=5)
        self.addCleanup(s.close)
        return s

    def test_second_request_on_same_connection_does_not_reach_first_server(self):
        a, b = self.srv_a.server_address[1], self.srv_b.server_address[1]
        s = self.proxy()
        s.sendall(f"GET http://127.0.0.1:{a}/uno HTTP/1.1\r\nHost: 127.0.0.1:{a}\r\n"
                  "Proxy-Connection: keep-alive\r\n\r\n".encode())
        first = read_all(s)  # il proxy chiude dopo la risposta: si legge fino alla fine
        self.assertIn(b"A /uno", first)
        try:
            s.sendall(f"GET http://127.0.0.1:{b}/due HTTP/1.1\r\nHost: 127.0.0.1:{b}\r\n\r\n".encode())
            second = read_all(s)
        except (BrokenPipeError, ConnectionResetError):
            second = b""
        self.assertNotIn(b"A ", second)
        self.assertEqual([p for p, _ in self.seen_a], ["/uno"])
        self.assertEqual(self.seen_b, [])

    def test_query_without_path_through_proxy(self):
        a = self.srv_a.server_address[1]
        s = self.proxy()
        s.sendall(f"GET http://127.0.0.1:{a}?x=1 HTTP/1.1\r\nHost: x\r\n\r\n".encode())
        self.assertIn(b"A /?x=1", read_all(s))

    def test_proxy_connection_not_forwarded_and_non_ascii_path_intact(self):
        a = self.srv_a.server_address[1]
        s = self.proxy()
        s.sendall(f"GET http://127.0.0.1:{a}/caff".encode() + b"\xc3\xa8" +
                  b" HTTP/1.1\r\nHost: x\r\nProxy-Connection: keep-alive\r\n\r\n")
        self.assertIn(b"A /caff\xc3\xa8", read_all(s))
        path, headers = self.seen_a[0]
        self.assertEqual(path.encode("latin-1"), b"/caff\xc3\xa8")
        self.assertNotIn("proxy-connection", {k.lower() for k in headers})
        self.assertEqual(headers.get("Connection"), "close")

    def test_connect_half_close_keeps_response(self):
        srv = socket.socket()
        srv.bind(("127.0.0.1", 0))
        srv.listen(1)
        self.addCleanup(srv.close)

        def until_eof_then_reply():
            conn, _ = srv.accept()
            with conn:
                received = b""
                while chunk := conn.recv(4096):
                    received += chunk
                conn.sendall(f"letti {len(received)} byte".encode())

        threading.Thread(target=until_eof_then_reply, daemon=True).start()
        s = self.proxy()
        s.sendall(f"CONNECT 127.0.0.1:{srv.getsockname()[1]} HTTP/1.1\r\n\r\n".encode())
        self.assertIn(b"200 Connection Established", s.recv(200))
        s.sendall(b"x" * 1000)
        s.shutdown(socket.SHUT_WR)
        self.assertEqual(read_all(s), b"letti 1000 byte")

    @unittest.skipUnless(ipv6_loopback(), "IPv6 di loopback non disponibile")
    def test_connect_ipv6(self):
        seen = []
        srv = _Ipv6Server(("::1", 0), make_handler("V6", seen))
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.addCleanup(srv.server_close)
        self.addCleanup(srv.shutdown)
        s = self.proxy()
        s.sendall(f"CONNECT [::1]:{srv.server_address[1]} HTTP/1.1\r\n\r\n".encode())
        self.assertIn(b"200 Connection Established", s.recv(200))
        s.sendall(b"GET /sei HTTP/1.1\r\nHost: x\r\nConnection: close\r\n\r\n")
        self.assertIn(b"V6 /sei", read_all(s))


if __name__ == "__main__":
    unittest.main()

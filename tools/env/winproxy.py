"""winproxy.py — proxy HTTP minimale, in ascolto solo su 127.0.0.1, da eseguire con il Python di Windows.

Serve a chi lavora in WSL: la VPN aziendale instrada gli host interni solo per i processi Windows, quindi
il traffico di WSL (browser di Playwright, curl, npm) passa da qui e esce dalla rete di Windows.
Non si lancia a mano: lo avvia, lo ferma e lo controlla `tools/env/wsl_proxy.py`, che copia questo file
nella cartella temporanea di Windows. Guida: `tools/README-wsl-vpn.md`.

Gestisce CONNECT (HTTPS, il traffico resta cifrato end-to-end) e richieste HTTP in chiaro con URL assoluto.
Una connessione HTTP in chiaro porta una sola richiesta: il proxy chiede `Connection: close` al server e
chiude la connessione dopo la risposta, cosi' una seconda richiesta del client verso un altro host non
finisce sul server della prima. Il client riapre la connessione da solo.
Non legge, non salva e non registra il contenuto: nel log solo metodo e host di destinazione.
Solo standard library, Python 3.8+.

Uso: python winproxy.py [porta]   (default 18765)
"""
import asyncio
import sys
from urllib.parse import urlsplit

DEFAULT_PORT = 18765

# intestazioni che valgono solo fra client e proxy (RFC 9110 §7.6.1): non vanno al server
HOP_BY_HOP = {b"connection", b"proxy-connection", b"keep-alive"}


def split_hostport(hostport):
    """'host:443' o '[::1]:443' -> ('host', 443); la porta e' obbligatoria."""
    parts = urlsplit("//" + hostport)
    if not parts.hostname or parts.port is None:
        raise ValueError("destinazione senza host o porta")
    return parts.hostname, parts.port


def rewrite_request(head):
    """Testa di una richiesta con URL assoluto -> (host, porta, testa da inoltrare al server).

    Lavora sui byte: il target non viene decodificato, quindi i byte non ASCII arrivano al server come sono.
    La riga diventa relativa (`GET /path?query HTTP/1.1`); le intestazioni hop-by-hop, compresa
    Proxy-Connection e quelle elencate in Connection, non vengono inoltrate; si aggiunge `Connection: close`.
    """
    lines = head.split(b"\r\n")
    method, target, version = lines[0].split(b" ", 2)
    scheme, sep, rest = target.partition(b"://")
    if not sep or scheme.lower() != b"http":
        raise ValueError("URL non assoluto o schema non http")
    cut = min((i for i in (rest.find(b"/"), rest.find(b"?"), rest.find(b"#")) if i >= 0), default=len(rest))
    hostport, tail = rest[:cut], rest[cut:].split(b"#", 1)[0]
    if not tail.startswith(b"/"):
        tail = b"/" + tail
    parts = urlsplit("//" + hostport.decode("ascii"))
    if not parts.hostname:
        raise ValueError("URL senza host")
    host, port = parts.hostname, parts.port or 80

    headers = [h for h in lines[1:] if h]
    drop = set(HOP_BY_HOP)
    for h in headers:
        name, _, value = h.partition(b":")
        if name.strip().lower() == b"connection":
            drop.update(t.strip().lower() for t in value.split(b",") if t.strip())
    kept = [h for h in headers if h.partition(b":")[0].strip().lower() not in drop]
    out = b"\r\n".join([b" ".join((method, tail, version))] + kept + [b"Connection: close"]) + b"\r\n\r\n"
    return host, port, out


def close(writer):
    try:
        writer.close()
    except Exception:
        # fail-open voluto: il socket puo' essere gia' chiuso dall'altro lato
        pass


async def pipe(reader, writer):
    """Copia da reader a writer; alla fine dei dati chiude solo la scrittura (half-close), non il socket."""
    try:
        while True:
            data = await reader.read(65536)
            if not data:
                break
            writer.write(data)
            await writer.drain()
        if writer.can_write_eof():
            writer.write_eof()
    except Exception:
        # fail-open voluto: una connessione chiusa da uno dei due lati termina solo questo tunnel
        close(writer)


async def handle(cr, cw):
    try:
        head = await cr.readuntil(b"\r\n\r\n")
    except Exception:
        close(cw)
        return
    try:
        method, target, _ = head.split(b"\r\n", 1)[0].split(b" ", 2)
    except ValueError:
        close(cw)
        return
    method = method.decode("latin-1")
    shown = "?"
    try:
        if method == "CONNECT":
            host, port = split_hostport(target.decode("ascii"))
            shown = f"{host}:{port}"
            ur, uw = await asyncio.wait_for(asyncio.open_connection(host, port), 20)
            cw.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            await cw.drain()
        else:
            host, port, out = rewrite_request(head)
            shown = f"{host}:{port}"
            ur, uw = await asyncio.wait_for(asyncio.open_connection(host, port), 20)
            uw.write(out)
            await uw.drain()
    except Exception as e:
        print(f"errore verso {shown}: {e.__class__.__name__}", flush=True)
        cw.write(b"HTTP/1.1 502 Bad Gateway\r\nConnection: close\r\nContent-Length: 0\r\n\r\n")
        close(cw)
        return
    print(f"{method} {shown}", flush=True)
    try:
        if method == "CONNECT":
            await asyncio.gather(pipe(cr, uw), pipe(ur, cw))
        else:
            # una richiesta per connessione: finita la risposta del server si chiude anche il lato client
            upload = asyncio.ensure_future(pipe(cr, uw))
            await pipe(ur, cw)
            upload.cancel()
    finally:
        close(uw)
        close(cw)


async def main(port):
    srv = await asyncio.start_server(handle, "127.0.0.1", port)
    print(f"proxy su 127.0.0.1:{port}", flush=True)
    async with srv:
        await srv.serve_forever()


if __name__ == "__main__":
    asyncio.run(main(int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT))

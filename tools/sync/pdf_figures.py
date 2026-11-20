#!/usr/bin/env python3
"""Estrattore deterministico delle figure di un PDF: i binari delle immagini, mai il testo.

Lanciato da `/sync-docs` PRIMA dell'agente `sync-docs`, che non ha Bash: lo script produce i file
immagine, l'agente scrive testo e descrizioni. Stesso schema di `tools/sync/repo_enumerate.py`: la
parte che ha bisogno di shell e' codice deterministico, l'agente che legge input non fidato no.

Solo libreria standard. Il PDF e' input non fidato: lo script non esegue nulla, non segue link, non
decompatta oltre `--max-bytes` per immagine (difesa dalle zip bomb), scrive solo in `--out`.

Formati:
  DCTDecode  (JPEG)       copiato com'e'                      -> .jpg
  JPXDecode  (JPEG 2000)  copiato com'e'                      -> .jp2
  FlateDecode             campioni ricostruiti come PNG       -> .png
                          (DeviceGray/RGB/CMYK, ICCBased con /N, Indexed su RGB; 8 bit;
                           predittori PNG 10-15 e TIFF 2 nelle DecodeParms)
  altro                   saltato e dichiarato nel JSON (mai un file inventato)

Pagina: ricavata dalle /Resources /XObject delle pagine (anche dentro object stream); se non si
trova, `page: null` e lo si dichiara. Le immagini usate solo come maschera (SMask) non sono figure.

Uso:
    python3 tools/sync/pdf_figures.py <file.pdf> --out raw/images [--prefix <data>-<nome>] [--max-bytes N]
Stampa un JSON su stdout. Exit code: 0 ok (anche con 0 figure), 2 PDF illeggibile o argomenti errati.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import struct
import sys
import zlib

MAX_BYTES = 64 * 1024 * 1024
OBJ_RE = re.compile(rb'(\d+)\s+(\d+)\s+obj\b')
REF_RE = re.compile(rb'(\d+)\s+(\d+)\s+R\b')


class PDFError(Exception):
    pass


# ---------------------------------------------------------------- lettura degli oggetti

def _dict_span(b: bytes, start: int) -> int:
    """Indice subito dopo il `>>` che chiude il dizionario aperto a `start` (che punta a `<<`)."""
    depth, i, n = 0, start, len(b)
    while i < n - 1:
        if b[i:i + 2] == b'<<':
            depth += 1
            i += 2
            continue
        if b[i:i + 2] == b'>>':
            depth -= 1
            i += 2
            if depth == 0:
                return i
            continue
        if b[i:i + 1] == b'(':  # stringa letterale: salta, con parentesi annidate ed escape
            d, i = 1, i + 1
            while i < n and d:
                c = b[i:i + 1]
                if c == b'\\':
                    i += 2
                    continue
                d += (c == b'(') - (c == b')')
                i += 1
            continue
        i += 1
    raise PDFError('dizionario non chiuso')


def _oggetti(b: bytes) -> dict[int, tuple[bytes, bytes | None]]:
    """{numero: (dizionario, stream grezzo o None)} per gli oggetti in chiaro nel file."""
    out: dict[int, tuple[bytes, bytes | None]] = {}
    for m in OBJ_RE.finditer(b):
        num, i = int(m.group(1)), m.end()
        while i < len(b) and b[i:i + 1] in b' \r\n\t':
            i += 1
        if b[i:i + 2] != b'<<':
            continue
        try:
            fine = _dict_span(b, i)
        except PDFError:
            continue
        d = b[i:fine]
        stream = None
        j = fine
        while j < len(b) and b[j:j + 1] in b' \r\n\t':
            j += 1
        if b[j:j + 6] == b'stream':
            j += 6
            if b[j:j + 2] == b'\r\n':
                j += 2
            elif b[j:j + 1] in b'\r\n':
                j += 1
            stream = (j, d)  # lunghezza risolta dopo, puo' essere un riferimento
        out[num] = (d, stream)  # type: ignore[assignment]
    # risolve /Length (diretta o indiretta) e ritaglia gli stream
    def intero(v: bytes) -> int | None:
        r = REF_RE.match(v.strip())
        if r:
            v = _valore_grezzo(int(r.group(1)), b)
        mm = re.match(rb'\s*(\d+)', v)
        return int(mm.group(1)) if mm else None
    risolti: dict[int, tuple[bytes, bytes | None]] = {}
    for num, (d, s) in out.items():
        if s is None:
            risolti[num] = (d, None)
            continue
        inizio = s[0]
        m = re.search(rb'/Length\s+((?:\d+\s+\d+\s+R)|\d+)', d)
        lung = intero(m.group(1)) if m else None
        if lung is None or inizio + lung > len(b):  # fallback: fino a endstream
            k = b.find(b'endstream', inizio)
            lung = (k if k >= 0 else len(b)) - inizio
        risolti[num] = (d, b[inizio:inizio + lung])
    return risolti


def _valore_grezzo(num: int, b: bytes) -> bytes:
    """Valore di un oggetto non-dizionario (es. `12 0 obj 5267 endobj`), per /Length indiretti."""
    m = re.search(rb'(?<!\d)%d\s+0\s+obj\s+(.*?)\s*endobj' % num, b, re.S)
    return m.group(1) if m else b''


def _inflate(data: bytes, limite: int) -> bytes:
    d = zlib.decompressobj()
    out = d.decompress(data, limite + 1)
    if len(out) > limite or d.unconsumed_tail:
        raise PDFError('stream oltre il limite di decompressione')
    return out


def _oggetti_da_objstm(oggetti: dict, limite: int) -> dict[int, bytes]:
    """Oggetti compressi negli object stream (PDF 1.5+): {numero: testo dell'oggetto}."""
    extra: dict[int, bytes] = {}
    for num, (d, s) in oggetti.items():
        if s is None or b'/ObjStm' not in d:
            continue
        try:
            dati = _inflate(s, limite) if b'/FlateDecode' in d else s
        except (PDFError, zlib.error):
            continue
        n = int(re.search(rb'/N\s+(\d+)', d).group(1))
        first = int(re.search(rb'/First\s+(\d+)', d).group(1))
        nums = list(map(int, dati[:first].split()))
        coppie = list(zip(nums[0::2], nums[1::2]))[:n]
        for k, (on, off) in enumerate(coppie):
            fine = coppie[k + 1][1] if k + 1 < len(coppie) else len(dati) - first
            extra[on] = dati[first + off:first + fine]
    return extra


# ---------------------------------------------------------------- PNG

def _png(larghezza: int, altezza: int, componenti: int, righe: bytes) -> bytes:
    tipo = {1: 0, 3: 2, 4: 6}[componenti]  # gray, RGB, RGBA (CMYK gia' convertito)
    def chunk(t: bytes, dati: bytes) -> bytes:
        return struct.pack('>I', len(dati)) + t + dati + struct.pack('>I', zlib.crc32(t + dati) & 0xFFFFFFFF)
    grezzo = b''.join(b'\x00' + righe[y * larghezza * componenti:(y + 1) * larghezza * componenti]
                      for y in range(altezza))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', larghezza, altezza, 8, tipo, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(grezzo, 9)) + chunk(b'IEND', b''))


def _togli_predittore(dati: bytes, larghezza: int, comp: int, pred: int) -> bytes:
    riga = larghezza * comp
    if pred == 2:  # TIFF
        out = bytearray(dati)
        for y in range(len(out) // riga):
            for x in range(comp, riga):
                out[y * riga + x] = (out[y * riga + x] + out[y * riga + x - comp]) & 0xFF
        return bytes(out)
    out, prec = bytearray(), bytearray(riga)
    for y in range(len(dati) // (riga + 1)):
        filtro = dati[y * (riga + 1)]
        r = bytearray(dati[y * (riga + 1) + 1:(y + 1) * (riga + 1)])
        for x in range(riga):
            a = r[x - comp] if x >= comp else 0
            b_, c = prec[x], (prec[x - comp] if x >= comp else 0)
            if filtro == 1:
                r[x] = (r[x] + a) & 0xFF
            elif filtro == 2:
                r[x] = (r[x] + b_) & 0xFF
            elif filtro == 3:
                r[x] = (r[x] + (a + b_) // 2) & 0xFF
            elif filtro == 4:
                p = a + b_ - c
                pa, pb, pc = abs(p - a), abs(p - b_), abs(p - c)
                r[x] = (r[x] + (a if pa <= pb and pa <= pc else b_ if pb <= pc else c)) & 0xFF
        out += r
        prec = r
    return bytes(out)


# ---------------------------------------------------------------- estrazione

def _nome(d: bytes, chiave: bytes) -> bytes | None:
    m = re.search(rb'/' + chiave + rb'\s*(\[[^\]]*\]|/\w+|\d+\s+\d+\s+R)', d)
    return m.group(1) if m else None


def _componenti(cs: bytes | None, testi: dict[int, bytes]) -> tuple[int | None, str]:
    if cs is None:
        return None, 'assente'
    r = REF_RE.fullmatch(cs.strip())
    if r:
        cs = testi.get(int(r.group(1)), b'').strip()
    if cs.startswith(b'['):
        if b'/ICCBased' in cs:
            ref = REF_RE.search(cs)
            n = re.search(rb'/N\s+(\d+)', testi.get(int(ref.group(1)), b'')) if ref else None
            return (int(n.group(1)) if n else None), 'ICCBased'
        if b'/Indexed' in cs:
            return -1, 'Indexed'
        cs = cs.strip(b'[]').split()[0]
    nome = cs.decode('latin-1').lstrip('/')
    return {'DeviceGray': 1, 'DeviceRGB': 3, 'DeviceCMYK': 4, 'CalGray': 1, 'CalRGB': 3}.get(nome), nome


def _pagine_per_oggetto(testi: dict[int, bytes]) -> dict[int, int]:
    """{numero dell'XObject immagine: pagina 1-based}, seguendo /Pages -> /Kids -> /Resources."""
    radice = next((n for n, t in testi.items() if re.search(rb'/Type\s*/Catalog', t)), None)
    if radice is None:
        return {}
    m = re.search(rb'/Pages\s+(\d+)\s+\d+\s+R', testi[radice])
    ordine: list[int] = []

    def visita(n: int, prof: int = 0) -> None:
        t = testi.get(n, b'')
        if prof > 50:
            return
        if re.search(rb'/Type\s*/Page\b', t):
            ordine.append(n)
            return
        kids = re.search(rb'/Kids\s*\[([^\]]*)\]', t)
        for r in REF_RE.finditer(kids.group(1) if kids else b''):
            visita(int(r.group(1)), prof + 1)
    if m:
        visita(int(m.group(1)))
    mappa: dict[int, int] = {}
    for idx, pn in enumerate(ordine, 1):
        t = testi.get(pn, b'')
        res = re.search(rb'/Resources\s+(\d+)\s+\d+\s+R', t)
        res_t = testi.get(int(res.group(1)), b'') if res else t
        xo = re.search(rb'/XObject\s*(<<.*?>>|\d+\s+\d+\s+R)', res_t, re.S)
        if not xo:
            continue
        corpo = xo.group(1)
        rr = REF_RE.fullmatch(corpo.strip())
        if rr:
            corpo = testi.get(int(rr.group(1)), b'')
        for r in REF_RE.finditer(corpo):
            mappa.setdefault(int(r.group(1)), idx)
    return mappa


def estrai(pdf: pathlib.Path, out: pathlib.Path, prefisso: str, limite: int = MAX_BYTES) -> dict:
    b = pdf.read_bytes()
    if not b.startswith(b'%PDF-'):
        raise PDFError('non e\' un PDF (intestazione %PDF- assente)')
    oggetti = _oggetti(b)
    testi = {n: d for n, (d, _) in oggetti.items()}
    testi.update(_oggetti_da_objstm(oggetti, limite))
    pagine = _pagine_per_oggetto(testi)
    maschere = {int(r.group(1)) for d in testi.values() for r in re.finditer(rb'/SMask\s+(\d+)\s+\d+\s+R', d)}

    figure, saltate = [], []
    immagini = sorted(n for n, (d, s) in oggetti.items()
                      if s is not None and re.search(rb'/Subtype\s*/Image', d) and n not in maschere)
    out.mkdir(parents=True, exist_ok=True)
    for k, num in enumerate(immagini, 1):
        d, s = oggetti[num]
        w = int(re.search(rb'/Width\s+(\d+)', d).group(1))
        h = int(re.search(rb'/Height\s+(\d+)', d).group(1))
        filtri = re.findall(rb'/(DCTDecode|JPXDecode|FlateDecode|LZWDecode|CCITTFaxDecode|JBIG2Decode|RunLengthDecode|ASCII85Decode|ASCIIHexDecode)', d)
        filtro = filtri[-1].decode() if filtri else 'nessuno'
        voce = {'n': k, 'oggetto': num, 'page': pagine.get(num), 'width': w, 'height': h, 'filtro': filtro}
        nome = f'{prefisso}-fig-{k:02d}'
        try:
            if filtri and filtri[-1] in (b'DCTDecode', b'JPXDecode') and len(filtri) == 1:
                est = '.jpg' if filtro == 'DCTDecode' else '.jp2'
                (out / (nome + est)).write_bytes(s)
                voce['file'] = str(out / (nome + est))
            elif filtri == [b'FlateDecode'] or not filtri:
                bpc = int((re.search(rb'/BitsPerComponent\s+(\d+)', d) or re.match(rb'(8)', b'8')).group(1))
                comp, cs = _componenti(_nome(d, b'ColorSpace'), testi)
                if bpc != 8 or comp in (None, -1):
                    raise PDFError(f'formato non gestito: {bpc} bit, spazio colore {cs}')
                dati = _inflate(s, limite) if filtri else s
                pm = re.search(rb'/Predictor\s+(\d+)', d)
                if pm and int(pm.group(1)) > 1:
                    dati = _togli_predittore(dati, w, comp, int(pm.group(1)))
                attesi = w * h * comp
                if len(dati) < attesi:
                    raise PDFError(f'campioni insufficienti: {len(dati)} invece di {attesi}')
                dati = dati[:attesi]
                if comp == 4 and cs in ('DeviceCMYK', 'ICCBased'):  # CMYK -> RGB ingenuo, dichiarato
                    rgb = bytearray()
                    for i in range(0, len(dati), 4):
                        c, m_, y, kk = dati[i:i + 4]
                        rgb += bytes((255 - min(255, c + kk), 255 - min(255, m_ + kk), 255 - min(255, y + kk)))
                    dati, comp = bytes(rgb), 3
                    voce['nota'] = 'CMYK convertito in RGB senza profilo colore'
                (out / (nome + '.png')).write_bytes(_png(w, h, comp, dati))
                voce['file'] = str(out / (nome + '.png'))
            else:
                raise PDFError(f'filtro non gestito: {"+".join(f.decode() for f in filtri)}')
            figure.append(voce)
        except (PDFError, zlib.error, ValueError, AttributeError) as e:
            voce['saltata'] = str(e)
            saltate.append(voce)
    return {'pdf': str(pdf), 'figure': figure, 'saltate': saltate,
            'pagine_note': bool(pagine), 'limite_bytes': limite}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('pdf', type=pathlib.Path)
    ap.add_argument('--out', type=pathlib.Path, required=True)
    ap.add_argument('--prefix')
    ap.add_argument('--max-bytes', type=int, default=MAX_BYTES)
    a = ap.parse_args(argv)
    try:
        esito = estrai(a.pdf, a.out, a.prefix or a.pdf.stem, a.max_bytes)
    except (OSError, PDFError) as e:
        print(json.dumps({'pdf': str(a.pdf), 'errore': str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps(esito, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())

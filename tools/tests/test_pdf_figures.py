"""tools/sync/pdf_figures.py — figure dei PDF senza Bash nell'agente (EP-098 US-398, TSK-974).

Ogni PDF e' costruito nel test con contenuto noto; il verdetto confronta i pixel estratti con quelli
di partenza, non la sola presenza di un file.
"""
from __future__ import annotations

import json
import subprocess
import sys
import zlib
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "sync" / "pdf_figures.py"
PIL = pytest.importorskip("PIL.Image")


def _pdf(oggetti: list[bytes]) -> bytes:
    """PDF minimo: oggetti numerati da 1 in ordine, catalogo = oggetto 1."""
    corpo = b"%PDF-1.5\n"
    for i, o in enumerate(oggetti, 1):
        corpo += b"%d 0 obj " % i + o + b" endobj\n"
    return corpo + b"trailer <</Root 1 0 R>>\n%%EOF\n"


def _stream(diz: bytes, dati: bytes) -> bytes:
    return diz[:-2] + b" /Length %d>> stream\n" % len(dati) + dati + b"\nendstream"


def _immagine_flate(w, h, cs, pixel: bytes, extra=b""):
    return _stream(b"<</Type /XObject /Subtype /Image /Width %d /Height %d /ColorSpace %s /BitsPerComponent 8 /Filter /FlateDecode%s>>"
                   % (w, h, cs, extra), zlib.compress(pixel))


def _pagine(*xobj_refs: bytes) -> list[bytes]:
    kids = b" ".join(b"%d 0 R" % (3 + i) for i in range(len(xobj_refs)))
    out = [b"<</Type /Catalog /Pages 2 0 R>>", b"<</Type /Pages /Kids [%s] /Count %d>>" % (kids, len(xobj_refs))]
    for r in xobj_refs:
        out.append(b"<</Type /Page /Parent 2 0 R /Resources <</XObject <<%s>> >> >>" % r)
    return out


def _run(pdf: Path, out: Path, *extra):
    r = subprocess.run([sys.executable, str(SCRIPT), str(pdf), "--out", str(out), "--prefix", "doc", *extra],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, json.loads(r.stdout)


def test_flate_rgb_pixel_uguali_e_pagina(tmp_path):
    w, h = 4, 2
    pix = bytes([255, 0, 0] * 4 + [0, 0, 255] * 4)
    oggetti = _pagine(b"/Im1 6 0 R", b"/Im2 5 0 R")  # img oggetto 5 sulla pagina 2, 6 sulla pagina 1
    oggetti += [_immagine_flate(w, h, b"/DeviceRGB", pix), _immagine_flate(1, 1, b"/DeviceGray", b"\x80")]
    (tmp_path / "a.pdf").write_bytes(_pdf(oggetti))
    rc, esito = _run(tmp_path / "a.pdf", tmp_path / "img")
    assert rc == 0 and not esito["saltate"]
    f1 = next(f for f in esito["figure"] if f["oggetto"] == 5)
    assert f1["page"] == 2 and f1["file"].endswith("doc-fig-01.png")
    im = PIL.open(f1["file"])
    assert im.size == (4, 2) and im.getpixel((0, 0)) == (255, 0, 0) and im.getpixel((3, 1)) == (0, 0, 255)
    g = PIL.open(next(f for f in esito["figure"] if f["oggetto"] == 6)["file"])
    assert g.mode == "L" and g.getpixel((0, 0)) == 0x80


def test_jpeg_copiato_com_e(tmp_path):
    from PIL import Image
    src = Image.new("RGB", (40, 20), (10, 180, 40))
    src.save(tmp_path / "j.pdf", "PDF", resolution=72)
    rc, esito = _run(tmp_path / "j.pdf", tmp_path / "img")
    assert rc == 0 and len(esito["figure"]) == 1 and esito["figure"][0]["filtro"] == "DCTDecode"
    px = Image.open(esito["figure"][0]["file"]).getpixel((5, 5))
    assert all(abs(a - b) <= 4 for a, b in zip(px, (10, 180, 40)))  # JPEG: tolleranza di compressione
    assert esito["figure"][0]["page"] == 1


def test_smask_non_e_una_figura(tmp_path):
    oggetti = _pagine(b"/Im1 4 0 R")
    oggetti += [_immagine_flate(1, 1, b"/DeviceRGB", b"\x01\x02\x03", extra=b" /SMask 5 0 R"),
                _immagine_flate(1, 1, b"/DeviceGray", b"\xff")]
    (tmp_path / "m.pdf").write_bytes(_pdf(oggetti))
    rc, esito = _run(tmp_path / "m.pdf", tmp_path / "img")
    assert [f["oggetto"] for f in esito["figure"]] == [4]


def test_predittore_png(tmp_path):
    w, h = 3, 2
    righe = [bytes([10, 20, 30] * 3), bytes([40, 50, 60] * 3)]
    # filtro PNG «Sub» (1) sulla prima riga, «Up» (2) sulla seconda
    sub = bytearray(righe[0]); sub[3:] = bytes((righe[0][i] - righe[0][i - 3]) & 0xFF for i in range(3, 9))
    up = bytes((righe[1][i] - righe[0][i]) & 0xFF for i in range(9))
    dati = b"\x01" + bytes(sub) + b"\x02" + up
    img = _stream(b"<</Type /XObject /Subtype /Image /Width 3 /Height 2 /ColorSpace /DeviceRGB /BitsPerComponent 8 "
                  b"/Filter /FlateDecode /DecodeParms <</Predictor 15 /Colors 3 /Columns 3>>>>", zlib.compress(dati))
    (tmp_path / "p.pdf").write_bytes(_pdf(_pagine(b"/Im1 4 0 R") + [img]))
    rc, esito = _run(tmp_path / "p.pdf", tmp_path / "img")
    im = PIL.open(esito["figure"][0]["file"])
    assert im.getpixel((2, 0)) == (10, 20, 30) and im.getpixel((1, 1)) == (40, 50, 60)


def test_pagine_dentro_object_stream(tmp_path):
    # catalogo, albero delle pagine e pagina compressi in un /ObjStm (PDF 1.5); l'immagine fuori
    testi = [b"<</Type /Catalog /Pages 2 0 R>>", b"<</Type /Pages /Kids [3 0 R] /Count 1>>",
             b"<</Type /Page /Parent 2 0 R /Resources <</XObject <</Im1 4 0 R>> >> >>"]
    corpo, off = b"", []
    for t in testi:
        off.append(len(corpo)); corpo += t + b"\n"
    intest = b" ".join(b"%d %d" % (i + 1, o) for i, o in enumerate(off)) + b"\n"
    objstm = _stream(b"<</Type /ObjStm /N 3 /First %d /Filter /FlateDecode>>" % len(intest), zlib.compress(intest + corpo))
    img = _immagine_flate(1, 1, b"/DeviceRGB", b"\x09\x08\x07")
    pdf = b"%PDF-1.5\n4 0 obj " + img + b" endobj\n5 0 obj " + objstm + b" endobj\ntrailer <</Root 1 0 R>>\n%%EOF\n"
    (tmp_path / "o.pdf").write_bytes(pdf)
    rc, esito = _run(tmp_path / "o.pdf", tmp_path / "img")
    assert esito["figure"][0]["page"] == 1 and esito["pagine_note"] is True


def test_zip_bomb_saltata_e_dichiarata(tmp_path):
    z = zlib.compressobj(9)
    dati = z.compress(b"\0" * (8 * 1024 * 1024)) + z.flush()
    img = _stream(b"<</Type /XObject /Subtype /Image /Width 4000 /Height 1000 /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /FlateDecode>>", dati)
    (tmp_path / "b.pdf").write_bytes(_pdf(_pagine(b"/Im1 4 0 R") + [img]))
    rc, esito = _run(tmp_path / "b.pdf", tmp_path / "img", "--max-bytes", str(1024 * 1024))
    assert rc == 0 and not esito["figure"] and "limite" in esito["saltate"][0]["saltata"]
    assert not list((tmp_path / "img").glob("*"))  # nessun file parziale


def test_formato_non_gestito_saltato_non_inventato(tmp_path):
    img = _stream(b"<</Type /XObject /Subtype /Image /Width 1 /Height 1 /ColorSpace /DeviceGray /BitsPerComponent 1 /Filter /CCITTFaxDecode>>", b"\x00")
    (tmp_path / "c.pdf").write_bytes(_pdf(_pagine(b"/Im1 4 0 R") + [img]))
    rc, esito = _run(tmp_path / "c.pdf", tmp_path / "img")
    assert rc == 0 and not esito["figure"] and "CCITTFaxDecode" in esito["saltate"][0]["saltata"]


def test_non_pdf_exit_2(tmp_path):
    (tmp_path / "x.pdf").write_bytes(b"ciao")
    rc, esito = _run(tmp_path / "x.pdf", tmp_path / "img")
    assert rc == 2 and "PDF" in esito["errore"] and not (tmp_path / "img").exists()


def test_deterministico(tmp_path):
    pix = bytes(range(48))
    (tmp_path / "d.pdf").write_bytes(_pdf(_pagine(b"/Im1 4 0 R") + [_immagine_flate(4, 4, b"/DeviceRGB", pix)]))
    _run(tmp_path / "d.pdf", tmp_path / "i1"); _run(tmp_path / "d.pdf", tmp_path / "i2")
    assert (tmp_path / "i1/doc-fig-01.png").read_bytes() == (tmp_path / "i2/doc-fig-01.png").read_bytes()

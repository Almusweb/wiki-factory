"""Test di tools/docs/build_functional_docs.py su una factory finta in tmp_path."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "docs"))
import build_functional_docs as b  # noqa: E402

PAT = "a2" * 26

MANUALE = """---
title: Manuale cliente - Servizio demo
servizio: demo
pubblico: cliente
stato: bozza
---
# Manuale cliente - Servizio demo

## Scopo

Il servizio serve a dichiarare dati.

Fonti: `wiki/user-flows/demo.md`, `wiki/entities/assente.md`

## Stati

| Stato | Significato |
|---|---|
| Aperta | Appena inviata |

1. Primo
2. Secondo

## Fonti

- `wiki/user-flows/demo.md`
"""


@pytest.fixture
def factory(tmp_path):
    root = tmp_path / "factory"
    root.mkdir()
    (root / "factory.config.yaml").write_text("project: t\n", encoding="utf-8")
    d = root / "deliverables" / "doc-funzionale" / "demo"
    d.mkdir(parents=True)
    (d / "manuale-cliente.md").write_text(MANUALE, encoding="utf-8")
    site = root / "deliverables" / "doc-tecnica" / "2026-10-13" / "user-flows"
    site.mkdir(parents=True)
    (site / "demo.html").write_text("<html></html>", encoding="utf-8")
    return root


def run(root, *args):
    return b.main(["--root", str(root), *args])


def test_html_con_banner_e_link_fonti(factory):
    assert run(factory, "demo") == 0
    h = (factory / "deliverables/doc-funzionale/demo/manuale-cliente.html").read_text(encoding="utf-8")
    assert '<html lang="it">' in h
    assert b.BANNER_TEXT in h
    assert "<table" in h and "<ol" in h
    assert 'href="../../doc-tecnica/2026-10-13/user-flows/demo.html"' in h
    # fonte senza pagina nel sito: resta testo
    assert "wiki/entities/assente.md" in h
    assert 'href="../../doc-tecnica/2026-10-13/entities/assente.html"' not in h
    assert "http://" not in h and "https://" not in h


def test_senza_sito_tecnico_fonti_testo(factory):
    import shutil
    shutil.rmtree(factory / "deliverables" / "doc-tecnica")
    assert run(factory, "demo") == 0
    h = (factory / "deliverables/doc-funzionale/demo/manuale-cliente.html").read_text(encoding="utf-8")
    assert "doc-tecnica" not in h
    assert "wiki/user-flows/demo.md" in h


def test_approvata_senza_banner(factory):
    p = factory / "deliverables/doc-funzionale/demo/manuale-cliente.md"
    p.write_text(MANUALE.replace("stato: bozza", "stato: approvata\napprovata_da: Mario\napprovata_il: 2026-10-14"),
                 encoding="utf-8")
    assert run(factory, "demo") == 0
    h = p.with_suffix(".html").read_text(encoding="utf-8")
    assert b.BANNER_TEXT not in h
    assert "Approvata da Mario" in h


def test_docx_se_disponibile(factory):
    docx = pytest.importorskip("docx")
    assert run(factory, "demo") == 0
    f = factory / "deliverables/doc-funzionale/demo/manuale-cliente.docx"
    assert f.is_file()
    d = docx.Document(str(f))
    assert "bozza" in d.sections[0].header.paragraphs[0].text
    assert len(d.tables) == 1
    assert any(p.text == "Scopo" for p in d.paragraphs)


def test_docx_assente_non_blocca(factory, monkeypatch, capsys):
    monkeypatch.setitem(sys.modules, "docx", None)
    assert run(factory, "demo") == 0
    assert "Word saltato" in capsys.readouterr().err
    assert not (factory / "deliverables/doc-funzionale/demo/manuale-cliente.docx").exists()


def test_redazione_blocca_tutto(factory):
    d = factory / "deliverables/doc-funzionale/demo"
    (d / "guida-utente.md").write_text("---\nstato: bozza\n---\n# G\n\npassword: %s\n" % "segretissima1", encoding="utf-8")
    assert run(factory, "demo") == 2
    assert not list(d.glob("*.html"))


def test_tutti_e_servizio_mancante(factory):
    assert run(factory, "inesistente") == 1
    assert run(factory, "--tutti") == 0
    assert (factory / "deliverables/doc-funzionale/demo/manuale-cliente.html").is_file()


def test_config_output_dir(factory):
    pytest.importorskip("yaml")
    (factory / "factory.config.yaml").write_text(
        "documentation:\n  functional_docs:\n    output_dir: altro/dir\n", encoding="utf-8")
    cfg = b.load_config(factory)
    assert cfg["output_dir"] == "altro/dir"


def test_guida_utente_approvata_senza_fonti():
    body = ("## A cosa serve\nTesto.\n\nFonti: `wiki/a.md`\n\n## Lacune\n- x\n\nFonti: `wiki/b.md`\n\n"
            "## Fonti\n\n- `wiki/a.md`\n- `wiki/b.md`\n")
    out = b.for_audience({"pubblico": "utente", "stato": "approvata"}, body)
    assert "wiki/" not in out and "Fonti" not in out
    assert "## A cosa serve" in out and "## Lacune" in out
    assert b.for_audience({"pubblico": "utente", "stato": "bozza"}, body) == body
    assert b.for_audience({"pubblico": "cliente", "stato": "approvata"}, body) == body


def test_strip_sources_fonte_e_varianti_di_heading():
    body = ("# T\n\n## Scopo\n\nTesto.\n\nFonte: `wiki/a.md`\n\n**Fonti:** `wiki/b.md`\n\n"
            "### Fonti\n\n- `wiki/c.md`\n\n## Fonti e riferimenti\n\n- `wiki/d.md`\n\n"
            "## Fonte primaria\n\n- `wiki/e.md`\n\n## Dopo\n\nRiga finale.\n")
    out = b.strip_sources(body)
    assert "wiki/" not in out and "Fonte" not in out
    assert "Testo." in out and "## Dopo" in out and "Riga finale." in out


def test_link_sources_riconosce_fonte(tmp_path):
    site = tmp_path / "site"
    (site / "user-flows").mkdir(parents=True)
    (site / "user-flows" / "demo.html").write_text("x", encoding="utf-8")
    md = "Fonte: `wiki/user-flows/demo.md`\n\n## Fonte\n\n- `wiki/user-flows/demo.md`\n"
    out = b.link_sources(md, site, tmp_path / "out")
    assert out.count("](") == 2


def test_docx_celle_con_pipe_escapato_e_righe_senza_pipe_iniziale(tmp_path):
    docx = pytest.importorskip("docx")
    body = "# T\n\n| A | B |\n|---|---|\n| x \\| y | z |\n\nChiave | Valore\n--- | ---\nuno | due\n"
    dest = tmp_path / "t.docx"
    assert b.write_docx({}, body, "t", dest, "2026-10-13") is True
    tabs = docx.Document(str(dest)).tables
    assert len(tabs) == 2
    assert [c.text for c in tabs[0].rows[1].cells] == ["x | y", "z"]
    assert [c.text for c in tabs[1].rows[1].cells] == ["uno", "due"]
    assert [c.text for c in tabs[1].rows[0].cells] == ["Chiave", "Valore"]


def test_documentazione_disattivata(factory, capsys):
    pytest.importorskip("yaml")
    (factory / "factory.config.yaml").write_text("documentation:\n  enabled: false\n", encoding="utf-8")
    assert run(factory, "--tutti") == 0
    assert "disattivata" in capsys.readouterr().out
    assert not (factory / "deliverables/doc-funzionale/demo/manuale-cliente.html").exists()


def test_redazione_spenta_solo_se_false(factory):
    pytest.importorskip("yaml")
    for body, atteso in (("documentation:\n  redaction:\n    enabled: false\n", False),
                         ("documentation:\n  redaction:\n    enabled:\n", True),
                         ("documentation:\n  redaction:\n", True)):
        (factory / "factory.config.yaml").write_text(body, encoding="utf-8")
        assert b.load_config(factory)["redaction"] is atteso, body


DOC_LIBERO = """---
title: Documento libero
---
# Documento libero

## Parte A

Testo con **grassetto** e `codice`.

- primo
  - secondo livello
- terzo con
  continuazione

<!-- col-widths: 8.5,8.5 -->
| Domanda | Risposta |
|---|---|
| Quale? | |

<!-- col-widths: 1.1,6.0,5.0 -->
| a | b |
|---|---|
| 1 | 2 |
"""


def _cm(w):
    return round(w / 360000, 2)


def test_file_produce_html_e_docx_con_larghezze(tmp_path, capsys):
    docx = pytest.importorskip("docx")
    src = tmp_path / "doc.md"
    src.write_text(DOC_LIBERO, encoding="utf-8")
    out = tmp_path / "out"
    assert b.main(["--root", str(tmp_path), "--file", str(src), "--out", str(out)]) == 0
    assert (out / "doc.html").is_file()
    d = docx.Document(str(out / "doc.docx"))
    assert len(d.tables) == 2
    t0 = d.tables[0]
    assert [_cm(c.width) for c in t0.rows[0].cells] == [8.5, 8.5]
    assert t0.style.name == "Table Grid"
    assert all(r.bold for r in t0.rows[0].cells[0].paragraphs[0].runs)
    # commento con numero di valori sbagliato: ignorato con avviso
    assert "larghezze ignorate" in capsys.readouterr().err
    styles = [p.style.name for p in d.paragraphs]
    assert "Heading 1" in styles and "List Bullet 2" in styles
    # la riga di continuazione e' unita alla voce
    assert any(p.text == "terzo con continuazione" for p in d.paragraphs)


def test_file_accanto_al_sorgente_e_template(tmp_path):
    docx = pytest.importorskip("docx")
    tpl = tmp_path / "modello.docx"
    docx.Document().save(str(tpl))
    src = tmp_path / "doc.md"
    src.write_text(DOC_LIBERO, encoding="utf-8")
    assert b.main(["--root", str(tmp_path), "--file", str(src), "--template", str(tpl)]) == 0
    assert (tmp_path / "doc.docx").is_file() and (tmp_path / "doc.html").is_file()


def test_file_senza_python_docx_exit_non_zero(tmp_path, monkeypatch, capsys):
    src = tmp_path / "doc.md"
    src.write_text(DOC_LIBERO, encoding="utf-8")
    monkeypatch.setitem(sys.modules, "docx", None)
    assert b.main(["--root", str(tmp_path), "--file", str(src)]) == 1
    assert "python-docx" in capsys.readouterr().err
    assert not (tmp_path / "doc.html").exists()


def test_file_redazione_blocca(tmp_path):
    pytest.importorskip("docx")
    src = tmp_path / "doc.md"
    src.write_text("# T\n\nsegreto " + PAT + "\n", encoding="utf-8")
    assert b.main(["--root", str(tmp_path), "--file", str(src)]) == 2
    assert not (tmp_path / "doc.docx").exists()


def test_template_senza_file_e_errore(tmp_path):
    with pytest.raises(SystemExit):
        b.main(["--root", str(tmp_path), "--template", "x.docx"])


def test_word_corsivo_e_grassetto_nei_run():
    docx = pytest.importorskip("docx")
    d = docx.Document()
    par = d.add_paragraph()
    b._add_runs(par, "a *corsivo* e **grassetto** e 2*3*4 e `cod`")
    kinds = {r.text: (r.italic, r.bold) for r in par.runs}
    assert kinds["corsivo"][0] is True
    assert kinds["grassetto"][1] is True
    assert "2*3*4" in "".join(r.text for r in par.runs)


# --------------------------------------------------------------------------- EP-113 US-442: meccanica Word

def _png(path: Path, w: int, h: int) -> None:
    """PNG valido in scala di grigi, senza dipendenze (python-docx legge le dimensioni dall'header)."""
    import struct
    import zlib

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    raw = b"".join(b"\x00" + b"\x80" * w for _ in range(h))
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0))
                     + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


DOC_FIGURE = """# Documento con figure

## Requisiti

| ID | Descrizione |
|---|---|
| REQ-UC02 | Un requisito con testo lungo |
| RU.10_005 | Altro requisito |

![Maschera di accesso](img/accesso.png)

Testo fra le figure.

![Mappa larga](img/larga.png)

![Assente](img/non-esiste.png)
"""


def _xml(el) -> str:
    from lxml import etree  # type: ignore  # dipendenza di python-docx

    return etree.tostring(el, encoding="unicode")


def test_word_intestazione_ripetuta_e_id_senza_a_capo(tmp_path):
    docx = pytest.importorskip("docx")
    src = tmp_path / "doc.md"
    src.write_text(DOC_FIGURE, encoding="utf-8")
    b.write_docx_file({}, DOC_FIGURE, "doc", tmp_path / "doc.docx", base_dir=tmp_path)
    t = docx.Document(str(tmp_path / "doc.docx")).tables[0]
    assert "w:tblHeader" in _xml(t.rows[0]._tr)
    assert "w:tblHeader" not in _xml(t.rows[1]._tr)
    # le celle con un identificativo non vanno a capo, il testo libero si'
    assert "w:noWrap" in _xml(t.cell(1, 0)._tc) and "w:noWrap" in _xml(t.cell(2, 0)._tc)
    assert "w:noWrap" not in _xml(t.cell(1, 1)._tc)


def test_id_cell_riconosce_solo_identificativi():
    for ok in ("REQ-UC02", "RU.10_005", "TSK-1074", "RP.2-F13"):
        assert b._ID_CELL.match(ok), ok
    for ko in ("Descrizione", "testo con 1-2 spazi", "2026", "a-b", ""):
        assert not b._ID_CELL.match(ko), ko


def test_word_figure_con_didascalia_seq_ed_elenco(tmp_path, capsys):
    docx = pytest.importorskip("docx")
    (tmp_path / "img").mkdir()
    _png(tmp_path / "img" / "accesso.png", 40, 20)
    _png(tmp_path / "img" / "larga.png", 4000, 1000)  # 4000 px a 72 dpi: oltre 15 cm, va ridotta
    src = tmp_path / "doc.md"
    src.write_text(DOC_FIGURE, encoding="utf-8")
    assert b.main(["--root", str(tmp_path), "--file", str(src)]) == 0
    d = docx.Document(str(tmp_path / "doc.docx"))
    shapes = d.inline_shapes
    assert len(shapes) == 2
    assert _cm(shapes[1].width) == 15.0
    assert abs(shapes[1].height / shapes[1].width - 0.25) < 0.01  # proporzioni mantenute
    caps = [p for p in d.paragraphs if p.text.startswith("Figura ")]
    assert [p.text for p in caps] == ["Figura 1 – Maschera di accesso", "Figura 1 – Mappa larga"]
    assert all("SEQ Figura" in _xml(p._p) for p in caps)
    # immagine mancante: segnaposto e avviso, il documento si produce lo stesso
    assert any(p.text == "[immagine non inclusa: img/non-esiste.png]" for p in d.paragraphs)
    assert "immagine non inclusa (img/non-esiste.png)" in capsys.readouterr().err
    # in coda l'elenco delle figure, e Word aggiorna i campi all'apertura
    assert any(p.text == "Elenco delle figure" and p.style.name == "Heading 1" for p in d.paragraphs)
    assert 'TOC \\h \\z \\c "Figura"' in _xml(d.element.body)
    assert "w:updateFields" in _xml(d.settings.element)


def test_word_senza_figure_niente_elenco_ne_update_fields(tmp_path):
    docx = pytest.importorskip("docx")
    b.write_docx_file({}, "# Titolo\n\nSolo testo.\n", "doc", tmp_path / "doc.docx")
    d = docx.Document(str(tmp_path / "doc.docx"))
    assert not any(p.text == "Elenco delle figure" for p in d.paragraphs)
    assert "w:updateFields" not in _xml(d.settings.element)


def test_immagine_remota_non_scaricata(tmp_path, capsys):
    docx = pytest.importorskip("docx")
    b.write_docx_file({}, "# T\n\n![Logo](https://example.test/logo.png)\n", "doc", tmp_path / "doc.docx")
    d = docx.Document(str(tmp_path / "doc.docx"))
    assert len(d.inline_shapes) == 0
    assert "remota o non trovata" in capsys.readouterr().err

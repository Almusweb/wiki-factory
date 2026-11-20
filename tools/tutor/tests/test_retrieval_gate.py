"""Il retrieval semantico del tutor: doppio gate, degradazione, citazioni (US-175).

Tre invarianti, e la piu' importante e' la seconda:

  1. **Doppio gate.** Il retrieval sta all'incrocio di due capability indipendenti e serve
     che siano accese entrambe, piu' l'interruttore dell'integrazione — perche' avere le
     due capability accese non implica volerle collegate.
  2. **Silenzio mai.** Ogni volta che il retrieval semantico non viene usato, la ragione
     e' registrata. Il grep funziona comunque, quindi nulla fallisce e nulla verrebbe
     detto: e la risposta esce piu' povera senza che nessuno sappia perche'.
  3. **Citazioni verificabili.** Una pagina citata che non esiste e' un'inferenza
     travestita da fonte, ed e' esattamente cio' che i tag epistemici L1/L2/L3 esistono
     per impedire.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

RADICE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RADICE))

from tools.tutor.retrieval_tool import (  # noqa: E402
    _DEGRADAZIONI, retrieval_gate, search_wiki, ultima_degradazione, verifica_citazioni,
)

TRE_FLAG = ("capability_formativa:\n  enabled: {cf}\n  wiki_search_integration: {integr}\n"
            "wiki_search:\n  enabled: {ws}\n")


def _radice(tmp_path, cf="true", ws="true", integr="true"):
    (tmp_path / "factory.config.yaml").write_text(TRE_FLAG.format(cf=cf, ws=ws, integr=integr), encoding="utf-8")
    return str(tmp_path)


# ── Invariante 1 — doppio gate ──────────────────────────────────────────────

@pytest.mark.parametrize("cf,ws,integr,atteso", [
    ("true",  "true",  "true",  True),
    ("true",  "true",  "false", False),   # capability accese ma integrazione spenta
    ("true",  "false", "true",  False),   # nessun indice da interrogare
    ("false", "true",  "true",  False),   # nessun tutor che interroghi
    ("false", "false", "false", False),
])
def test_le_combinazioni_dei_tre_flag(tmp_path, cf, ws, integr, atteso):
    attivo, ragione = retrieval_gate(_radice(tmp_path, cf, ws, integr))
    assert attivo is atteso
    assert (ragione is None) is atteso, "a gate chiuso la ragione non puo' mancare"


def test_l_interruttore_dell_integrazione_governa_davvero(tmp_path):
    """Prima di US-175 bastava `wiki_search.enabled`: il flag
    `capability_formativa.wiki_search_integration` era dichiarato in configurazione e
    **non governava niente**. Questo test esiste perche' non torni cosi'."""
    attivo, ragione = retrieval_gate(_radice(tmp_path, integr="false"))
    assert attivo is False
    assert "wiki_search_integration" in ragione


def test_flag_assente_e_flag_falso_dicono_cose_diverse(tmp_path):
    """«Non dichiarato» e «dichiarato spento» portano a rimedi diversi."""
    (tmp_path / "factory.config.yaml").write_text("wiki_search:\n  enabled: true\n", encoding="utf-8")
    _, assente = retrieval_gate(str(tmp_path))
    _, falso = retrieval_gate(_radice(tmp_path, integr="false"))
    assert "non e' dichiarato" in assente
    assert "non e' attivo" in falso


def test_config_illeggibile_chiude_il_gate(tmp_path):
    """Fail-closed: in dubbio non si interroga l'indice."""
    attivo, ragione = retrieval_gate(str(tmp_path / "inesistente"))
    assert attivo is False and ragione


# ── Invariante 2 — la degradazione si dichiara ──────────────────────────────

def test_a_gate_chiuso_la_ragione_e_registrata(tmp_path):
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki" / "nota.md").write_text("# Nota\n\nparola-cercata qui.\n", encoding="utf-8")
    _DEGRADAZIONI.clear()
    search_wiki("parola-cercata", _radice(tmp_path, integr="false"))
    degrado = ultima_degradazione()
    assert degrado and degrado["tipo"] == "gate-chiuso"
    assert "wiki_search_integration" in degrado["ragione"]


def test_il_grep_risponde_comunque(tmp_path):
    """R.WS1: a gate chiuso il tutor risponde lo stesso, col comportamento di prima."""
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki" / "nota.md").write_text("# Nota\n\n## Sezione\n\nparola-cercata qui.\n", encoding="utf-8")
    risultati = search_wiki("parola-cercata", _radice(tmp_path, integr="false"))
    assert risultati and risultati[0]["source"].endswith("nota.md")


def test_indice_assente_nomina_il_comando_che_lo_costruisce(tmp_path):
    """`wiki_search.enabled: true` non garantisce che l'indice esista. Un messaggio che
    non dice come rimediare costringe a cercare il rimedio."""
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki" / "nota.md").write_text("# Nota\n\nparola-cercata.\n", encoding="utf-8")
    _DEGRADAZIONI.clear()
    search_wiki("parola-cercata", _radice(tmp_path))   # gate aperto, nessun indice
    degrado = ultima_degradazione()
    assert degrado is not None, "gate aperto e indice assente: la ragione va registrata"
    assert degrado["tipo"] == "indice-non-utilizzabile"


def test_indice_presente_risponde_senza_degradare(tmp_path):
    """Gate aperto e indice fts5 costruito: le citazioni arrivano dall'indice. Prima il
    tutor invocava un modulo `wiki_search` inesistente e degradava sempre al grep."""
    import subprocess
    (tmp_path / "wiki" / "concepts").mkdir(parents=True)
    (tmp_path / "wiki" / "concepts" / "nota.md").write_text(
        "---\ntitle: Nota\nstatus: draft\n---\n# Nota\n\n## Sezione\n\nparolarara presente.\n", encoding="utf-8")
    radice = _radice(tmp_path)
    subprocess.run([sys.executable, str(RADICE / "tools" / "wiki-search" / "fts_index.py"),
                    "--root", radice, "build"], check=True, capture_output=True)
    _DEGRADAZIONI.clear()
    citazioni = search_wiki("parolarara", radice)
    assert ultima_degradazione() is None
    assert [c["source"] for c in citazioni] == ["wiki/concepts/nota.md"]


# ── Invariante 3 — citazioni verificabili ───────────────────────────────────

def test_una_citazione_che_non_risolve_viene_scartata():
    valide = verifica_citazioni([
        {"source": "PATTERN.md", "section": "x"},
        {"source": "wiki/concepts/mai-esistita.md", "section": "y"},
        {"source": "", "section": "z"},
    ], str(RADICE))
    assert [c["source"] for c in valide] == ["PATTERN.md"]


def test_lo_scarto_e_registrato_non_silenzioso():
    """Una citazione persa in silenzio fa sembrare povero il retrieval invece che
    stantio l'indice: due diagnosi diverse, due rimedi diversi."""
    _DEGRADAZIONI.clear()
    verifica_citazioni([{"source": "wiki/concepts/mai-esistita.md", "section": "y"}], str(RADICE))
    degrado = ultima_degradazione()
    assert degrado and "scartate" in degrado["ragione"]
    assert "reindex" in degrado["ragione"] or "indice" in degrado["ragione"]


def test_le_citazioni_valide_non_vengono_toccate():
    dentro = [{"source": "PATTERN.md", "section": "§1", "excerpt": "testo"}]
    assert verifica_citazioni(dentro, str(RADICE)) == dentro

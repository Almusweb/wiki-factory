"""Dipendenze di un nodo (stadio 2 del grafo della conoscenza). Solo stdlib, solo lettura.

Il grafo NON ha un secondo parser: lo costruisce `tools/graph/build_graph.py`, caricato come
libreria, e la plancia lo tiene **in memoria**. Nessun file viene scritto, da nessuna parte.

La domanda a cui risponde e' l'analisi d'impatto a vicinato inverso («chi dipende da questo
ADR o concept?»): una tabella per nodo, non una vista globale.

Provenienza ed eta' come per ogni dato della plancia: il grafo e' una `Reading`. Se la costruzione
fallisce (libreria assente, non e' un repo git, ...) la risposta e' «non osservabile» con il
motivo, mai una tabella vuota che si legge come «nessuna dipendenza».

Cache: il grafo si ricostruisce quando l'eta' supera `REFRESH_SECONDS`, o su richiesta
(`forza=True`); forzature concorrenti si fondono in una sola costruzione.

Tempo di costruzione sul corpus reale di questa factory (2026-11-18, macchina di sviluppo, tre
misure con `Grafo(root).leggi()`): 1,53-1,60 s per 2637 nodi. Cresce con il corpus: ogni
risposta riporta `costruito_in_s`, il valore da leggere in esercizio.
"""
from __future__ import annotations

import importlib.util
import threading
import time
from pathlib import Path

from visual.collectors.base import Reading

REFRESH_SECONDS = 120.0
#: Dopo un fallo non si riprova a ogni richiesta: una costruzione che fallisce costa quanto una
#: che riesce (git log) e il pannello interroga ripetutamente.
RETRY_SECONDS = 5.0
LIMITE_RICERCA = 20
SORGENTE = "tools/graph/build_graph.py (wiki/, management/kanban/, raw/)"
LIBRERIA = Path(__file__).resolve().parents[1] / "tools" / "graph" / "build_graph.py"

#: Testo di ciascuna risoluzione. Gli archi non dichiarati non hanno risoluzione: «n/a».
RISOLUZIONE_TESTO = {
    "resolved": "fonte trovata",
    "unresolved-path": "percorso non risolto",
    "id-kanban": "id kanban non trovato",
    "placeholder": "segnaposto",
    None: "n/a",
}
NOTA_FONTE_TROVATA = "il file esiste; non verifica che la pagina dica cio' che la fonte dice"
ORDINE_TIPO = {"wiki": 0, "kanban": 1, "raw": 2}


def carica_libreria():
    """`build_graph` come libreria, dal repo che contiene questo pacchetto."""
    spec = importlib.util.spec_from_file_location("plancia_build_graph", str(LIBRERIA))
    if spec is None or spec.loader is None or not LIBRERIA.is_file():
        raise FileNotFoundError("tools/graph/build_graph.py non trovato")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


class Grafo:
    """Grafo in memoria con eta' e provenienza. Thread-safe: una sola costruzione alla volta."""

    def __init__(self, root: Path, refresh_seconds: float = REFRESH_SECONDS) -> None:
        self.root = Path(root)
        self.refresh_seconds = refresh_seconds
        self._lock = threading.Lock()
        self._lettura = None   # type: Reading | None
        self._avviata_a = None  # type: float | None  # inizio dell'ultima costruzione (monotonic)

    # -- costruzione ------------------------------------------------------------------
    def _costruisci(self) -> Reading:
        inizio = time.monotonic()
        try:
            libreria = carica_libreria()
            grafo, report = libreria.costruisci(str(self.root))
        except BaseException as problema:   # noqa: BLE001 — SystemExit incluso: e' un dato
            if isinstance(problema, KeyboardInterrupt):
                raise
            return Reading.unavailable("grafo", SORGENTE, f"{type(problema).__name__}: {problema}")
        durata = time.monotonic() - inizio
        return Reading.ok("grafo", _indicizza(grafo, report), SORGENTE, unit="nodi",
                          label="Grafo della conoscenza", costruito_in_s=round(durata, 3))

    def leggi(self, forza: bool = False) -> Reading:
        """Forzature concorrenti: una forzatura riusa l'esito di una costruzione solo se quella e'
        **iniziata dopo** la richiesta (ha quindi visto i file com'erano al momento della forzatura),
        invece di ricostruire in serie. Una costruzione gia' in corso quando la forzatura arriva
        non basta: chi forza ha probabilmente appena cambiato un file (review iter-2 F10).
        Una forzatura isolata ricostruisce sempre."""
        richiesta = time.monotonic()
        with self._lock:
            ultima = self._lettura
            if ultima is not None:
                if forza and self._avviata_a is not None and self._avviata_a >= richiesta:
                    return ultima
                if not forza:
                    limite = self.refresh_seconds if ultima.available else RETRY_SECONDS
                    if ultima.age_seconds() < limite:
                        return ultima
            self._avviata_a = time.monotonic()
            self._lettura = self._costruisci()
            return self._lettura

    # -- risposte ---------------------------------------------------------------------
    def _base(self, lettura: Reading) -> dict:
        base = {"fonte": lettura.source, "letto_da_s": round(lettura.age_seconds(), 1)}
        if lettura.available:
            base.update(osservabile=True, costruito_in_s=lettura.detail.get("costruito_in_s"))
        else:
            base.update(osservabile=False, ragione=lettura.reason)
        return base

    def cerca(self, q: str, forza: bool = False) -> dict:
        lettura = self.leggi(forza)
        risposta = self._base(lettura)
        risposta["q"] = q
        if not lettura.available:
            return risposta
        ago = q.strip().lower()
        trovati = []
        if ago:
            for nodo in lettura.value["nodi"].values():
                chiavi = (nodo["id"].lower(), (nodo.get("titolo") or "").lower(),
                          (nodo.get("kanban_id") or "").lower())
                if any(ago in k for k in chiavi):
                    esatto = ago in (chiavi[2], chiavi[1], chiavi[0])
                    trovati.append((0 if esatto else 1, nodo["id"], nodo))
        trovati.sort(key=lambda t: (t[0], t[1]))
        risposta["risultati"] = [_nodo_breve(n) for _, _, n in trovati[:LIMITE_RICERCA]]
        risposta["totale"] = len(trovati)
        risposta["troncato"] = len(trovati) > LIMITE_RICERCA
        return risposta

    def nodo(self, ident: str, hop: int, forza: bool = False) -> dict:
        """Vicini in ingresso e in uscita a `hop` passi. `nodo_trovato: false` se l'id non esiste."""
        lettura = self.leggi(forza)
        risposta = self._base(lettura)
        risposta["id"], risposta["hop"] = ident, hop
        if not lettura.available:
            return risposta
        indice = lettura.value
        nodo = indice["nodi"].get(ident)
        if nodo is None:
            risposta["nodo_trovato"] = False
            return risposta
        risposta["nodo_trovato"] = True
        risposta["nodo"] = _nodo_breve(nodo)
        ingresso = _vicini(indice, ident, hop, entrante=True)
        uscita = _vicini(indice, ident, hop, entrante=False)
        risposta["in_ingresso"], risposta["in_uscita"] = ingresso, uscita
        risposta["conteggi"] = {"in_ingresso": _conta(ingresso), "in_uscita": _conta(uscita)}
        risposta["avvertenza"] = ("fonte trovata: " + NOTA_FONTE_TROVATA)
        return risposta


# -- indice e attraversamento (funzioni pure) --------------------------------------------

def _indicizza(grafo: dict, report: dict) -> dict:
    nodi = {n["id"]: n for n in grafo["nodi"]}
    entranti, uscenti = {}, {}
    for a in grafo["archi"]:
        entranti.setdefault(a["target"], []).append(a)
        uscenti.setdefault(a["source"], []).append(a)
    # chi deve riparare un arco non risolto: gli stessi gruppi del report dello stadio 1
    gruppi = {g["file_citante"]: g for g in report.get("non_risolti", [])}
    return {"nodi": nodi, "entranti": entranti, "uscenti": uscenti, "gruppi": gruppi}


def _nodo_breve(nodo: dict) -> dict:
    return {"id": nodo["id"], "titolo": nodo.get("titolo") or nodo["id"], "tipo": nodo["tipo"],
            "sottotipo": nodo.get("tipo_kanban") or nodo.get("sezione") or "",
            "status": nodo.get("status") or ""}


def _riga(indice: dict, arco: dict, altro: str, passo: int, via_nodo) -> dict:
    """Una riga di tabella: `altro` e' il nodo all'altro capo dell'arco."""
    nodo = indice["nodi"].get(altro)
    base = _nodo_breve(nodo) if nodo else {"id": altro, "titolo": altro, "tipo": "fuori dal grafo",
                                           "sottotipo": "", "status": ""}
    risoluzione = arco["resolution"]
    riga = dict(base, passo=passo, origin=arco["origin"], resolution=risoluzione,
                risoluzione_testo=RISOLUZIONE_TESTO.get(risoluzione, str(risoluzione)),
                citazioni=arco["count"], via_nodo=via_nodo)
    if risoluzione == "resolved":
        riga["nota"] = NOTA_FONTE_TROVATA
    elif arco["origin"] == "declared":
        g = indice["gruppi"].get(arco["source"])
        if g:
            riga.update(area=g["area"], status_citante=g["status"], a_chi_spetta=g["a_chi_spetta"],
                        file_citante=g["file_citante"])
    return riga


def _vicini(indice: dict, ident: str, hop: int, entrante: bool) -> list:
    """Visita in ampiezza: ogni nodo compare una volta, al passo piu' corto. `via_nodo` e' il
    vicino a un passo attraverso cui si arriva a un nodo a due passi (None a un passo)."""
    visti = {ident}
    frontiera = [(ident, None)]  # (nodo, da quale nodo ci si e' arrivati)
    righe = []
    adiacenza = indice["entranti"] if entrante else indice["uscenti"]
    for passo in range(1, hop + 1):
        prossima = []
        for corrente, _ in frontiera:
            for arco in adiacenza.get(corrente, ()):
                altro = arco["source"] if entrante else arco["target"]
                if altro in visti:
                    continue
                visti.add(altro)
                righe.append(_riga(indice, arco, altro, passo, corrente if passo > 1 else None))
                prossima.append((altro, corrente))
        frontiera = prossima
    righe.sort(key=lambda r: (r["passo"], ORDINE_TIPO.get(r["tipo"], 9), r["sottotipo"], r["id"]))
    return righe


def _conta(righe: list) -> dict:
    per_origin, per_res = {}, {}
    for r in righe:
        per_origin[r["origin"]] = per_origin.get(r["origin"], 0) + 1
        if r["resolution"]:
            per_res[r["resolution"]] = per_res.get(r["resolution"], 0) + 1
    return {"totale": len(righe), "per_origin": per_origin, "per_resolution": per_res}

"""Registro degli accessi della plancia: opt-in, spento di default.

E' l'UNICA scrittura della plancia e va nominata come eccezione al principio di sola
lettura: il resto del pacchetto non scrive nulla. Esiste perche' senza di essa la domanda
«la plancia e' mai stata aperta mentre accadeva qualcosa?» non e' rispondibile dai dati.

Cosa registra, per richiesta: `ts` (UTC), `metodo` e `rotta` NORMALIZZATA (`/api/state`,
mai la query string). Mai l'IP, mai il percorso assoluto della root, mai un nome di TSK:
le rotte sconosciute e i file statici collassano su `/altro` e `/static`.

Destinazione: `analytics/plancia-accessi-AAAAMMGG.jsonl`, fuori dal versionato, un file al
giorno, senza `:` nel nome (portabilita' Windows). All'avvio si cancellano i file piu'
vecchi di `RETENZIONE_GIORNI`. Scrittura best-effort: un disco pieno o un path non
scrivibile non fanno cadere la plancia. A flag spento nessun file, nessuna scrittura.
"""
from __future__ import annotations

import json
import re
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

RETENZIONE_GIORNI = 14
PREFISSO = "plancia-accessi-"
ROTTE_NOTE = {"/", "/api/state", "/api/identity", "/healthz", "/coordinamento/vista",
              "/api/voce", "/api/invia", "/api/rispondi",
              "/api/grafo/cerca", "/api/grafo/nodo"}


def acceso(root: Path) -> bool:
    """`visual_channel.registro_accessi.enabled` in factory.config.yaml. Illeggibile = spento."""
    try:
        testo = (root / "factory.config.yaml").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    blocco = re.search(r"^visual_channel:\s*\n((?:[ \t].*\n?|\s*\n)*)", testo, re.M)
    if not blocco:
        return False
    sotto = re.search(r"^  registro_accessi:\s*(?:#.*)?\n((?:    .*\n?|[ \t]*\n)*)",
                      blocco.group(1), re.M)
    if not sotto:
        return False
    return re.search(r"^    enabled:\s*true\b", sotto.group(1), re.M) is not None


def normalizza(route: str) -> str:
    """Rotta ammessa nel registro. Tutto cio' che non e' noto perde il suo nome."""
    if route in ROTTE_NOTE:
        return route
    if route.startswith("/api/grafo/"):
        return "/api/grafo/altro"
    if route.startswith("/api/"):
        return "/api/altro"
    return "/static" if "." in route.rsplit("/", 1)[-1] else "/altro"


class RegistroAccessi:
    def __init__(self, cartella: Path, abilitato: bool) -> None:
        self.cartella, self.abilitato = cartella, abilitato
        self._lock = threading.Lock()
        if abilitato:
            self._pulisci()

    def nome_file(self, quando: datetime) -> str:
        return f"{PREFISSO}{quando:%Y%m%d}.jsonl"

    def _pulisci(self) -> None:
        limite = datetime.now(timezone.utc) - timedelta(days=RETENZIONE_GIORNI)
        try:
            for f in self.cartella.glob(f"{PREFISSO}*.jsonl"):
                m = re.fullmatch(rf"{re.escape(PREFISSO)}(\d{{8}})\.jsonl", f.name)
                if m and datetime.strptime(m.group(1), "%Y%m%d").replace(
                        tzinfo=timezone.utc) < limite:
                    f.unlink()
        except (OSError, ValueError):
            pass

    def registra(self, metodo: str, route: str) -> None:
        if not self.abilitato:
            return
        ora = datetime.now(timezone.utc)
        riga = json.dumps({"ts": ora.isoformat(timespec="seconds"), "metodo": metodo,
                           "rotta": normalizza(route)}, ensure_ascii=False)
        try:
            with self._lock:
                self.cartella.mkdir(parents=True, exist_ok=True)
                with open(self.cartella / self.nome_file(ora), "a", encoding="utf-8") as f:
                    f.write(riga + "\n")
        except Exception:      # noqa: BLE001 — best-effort: la plancia non cade per un log
            pass

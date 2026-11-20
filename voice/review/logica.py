"""Logica pura della review in ascolto continuo (EP-117, spike del 2026-11-20).

Nessuna dipendenza oltre la libreria standard: si testa senza microfono, senza
faster-whisper e senza modello. Il lanciatore (`ascolto_spike.py`) la usa sui segmenti veri.

Contenuto:
- `comando`: riconosce la parola chiave nel TESTO trascritto (spike) e il comando che segue;
- `valuta_parte`: filtro per parte di segmento, non sul massimo del segmento;
- `ripetizione_sospetta`: ripetizione allucinata in coda, da dichiarare e non cancellare;
- `verifica_citazioni`: una citazione vale solo se e' sottostringa esatta dei segmenti citati.
"""
from __future__ import annotations

import re
import unicodedata

PAROLA_CHIAVE = "prometeus"
DISTANZA_MAX = 3            # voice_channel.wake_word.filter_threshold
NO_SPEECH_MAX = 0.6         # voice_channel.stt.no_speech_prob_threshold
LOGPROB_MIN = -1.0          # regola di Whisper: silenzio solo se no_speech alto E logprob basso
COMPRESSION_MAX = 2.4       # voice_channel.stt.compression_ratio_threshold (NON calibrata)

# Allucinazioni ricorrenti di Whisper sul silenzio, in italiano. Osservata 2 volte su 2 nella
# simulazione, sempre in coda a un segmento lungo. E' una LISTA: un'allucinazione nuova non la
# ferma, e la regola no_speech/logprob da sola l'avrebbe lasciata passare (avg_logprob -0,35).
ALLUCINAZIONI_NOTE = ("amara.org", "sottotitoli creati", "sottotitoli a cura", "grazie per la visione")


def _normalizza(testo: str) -> str:
    s = unicodedata.normalize("NFKD", testo.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z ]", " ", s)


def _levenshtein(x: str, y: str) -> int:
    d = list(range(len(y) + 1))
    for i, cx in enumerate(x, 1):
        p, d[0] = d[0], i
        for j, cy in enumerate(y, 1):
            p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (cx != cy))
    return d[-1]


def comando(testo: str) -> tuple[str | None, str | None]:
    """(comando, parola letta) se il testo contiene la parola chiave, altrimenti (None, None).

    Comandi: «inizio» (inizia la review / avvia), «fine» (fine, chiudi, stop, termina),
    «rilievo» (rilievo, nota), «sconosciuto» (parola chiave senza comando riconosciuto).
    Whisper scrive la parola chiave in molti modi (osservati: Prometheus, Prometeo, Prometeos):
    la distanza di edit li accoglie. Falso positivo noto: «il prometeo incatenato».
    """
    parole = _normalizza(testo).split()
    for i, w in enumerate(parole):
        if _levenshtein(w, PAROLA_CHIAVE) <= DISTANZA_MAX:
            resto = " ".join(parole[i + 1:i + 5])
            if re.search(r"\binizi\w*\b.*\breview\b|\bavvia\w*\b", resto):
                return "inizio", w
            if re.search(r"\bfine\b|\bchiud\w*\b|\bstop\b|\btermin\w*\b", resto):
                return "fine", w
            if re.search(r"\brilievo\b|\bnota\b", resto):
                return "rilievo", w
            return "sconosciuto", w
    return None, None


def valuta_parte(testo: str, no_speech_prob: float, avg_logprob: float,
                 compression_ratio: float) -> str | None:
    """Motivo dello scarto di UNA parte di segmento, oppure None se la parte si tiene.

    Correzione della simulazione: il massimo di no_speech_prob sul segmento aveva scartato
    16 s di parlato vero (S006: 0,979, avg_logprob -0,597) per una pausa interna.
    """
    t = testo.strip()
    if not t:
        return "vuota"
    if any(h in t.lower() for h in ALLUCINAZIONI_NOTE):
        return "allucinazione nota"
    if no_speech_prob > NO_SPEECH_MAX and avg_logprob < LOGPROB_MIN:
        return f"no_speech_prob {no_speech_prob:.2f} e avg_logprob {avg_logprob:.2f}"
    if compression_ratio > COMPRESSION_MAX:
        return f"compression_ratio {compression_ratio:.2f} (soglia non calibrata)"
    return None


def ripetizione_sospetta(testo: str, n: int = 4) -> str | None:
    """La prima sequenza di n parole che ricompare nello stesso testo, oppure None."""
    w = testo.lower().split()
    visti: set[tuple[str, ...]] = set()
    for i in range(len(w) - n + 1):
        k = tuple(w[i:i + n])
        if k in visti:
            return " ".join(k)
        visti.add(k)
    return None


def _spazi(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def verifica_citazioni(segmenti: dict[str, dict], candidati: list[dict]) -> tuple[list[str], list[dict]]:
    """(validi, scartati). Nessuna correzione: chi non passa e' scartato con il motivo.

    La fonte e' il testo dei segmenti citati, concatenati in ordine; contano anche il testo
    scartato dal filtro (`testo_scartato`), perche' un rilievo puo' stare li' (C6 del verbale).
    """
    validi, scartati = [], []
    for c in candidati:
        mancanti = [s for s in c["segmenti"] if s not in segmenti]
        if mancanti:
            scartati.append({**c, "motivo": f"segmenti inesistenti: {mancanti}"})
            continue
        # Due fonti, provate in ordine: il solo testo tenuto (un'allucinazione scartata in coda a
        # un segmento non deve spezzare una citazione continua), poi anche il testo scartato.
        tenuto = _spazi(" ".join(segmenti[s].get("testo", "") for s in c["segmenti"]))
        con_scarti = _spazi(" ".join(
            " ".join(x for x in (segmenti[s].get("testo", ""), segmenti[s].get("testo_scartato", "")) if x)
            for s in c["segmenti"]))
        cit = _spazi(c["citazione"])
        if cit in tenuto or cit in con_scarti:
            validi.append(c["id"])
        else:
            scartati.append({**c, "motivo": "citazione non ritrovata nei segmenti citati"})
    return validi, scartati

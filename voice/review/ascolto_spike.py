"""Spike EP-117 (US-447): review in ascolto continuo, trascrizione append-only.

NON e' l'implementazione di EP-117: e' la prova del flusso usata il 2026-11-20 (vedi README).
Nessun audio su disco. La logica senza dipendenze sta in `voice/review/logica.py` ed e' testata.

Uso, dalla radice della factory, con l'ambiente vocale (faster-whisper + sounddevice):
    ~/.local/share/soli-voice/venv/bin/python -m voice.review.ascolto_spike \
        --out ~/.local/share/soli-voice/review/<sessione>.jsonl [--device NOME] [--model medium]
Stop: crea il file <out>.stop, oppure SIGTERM.
"""
import argparse, json, os, queue, signal, sys, time
from datetime import datetime, timezone

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from faster_whisper.vad import VadOptions, get_speech_timestamps

SR = 16000
SILENZIO_MS = 700          # voice_channel.vad.endpoint_silence_ms
TETTO_S = 25               # oltre, si taglia comunque al silenzio piu' recente
from voice.review.logica import comando, ripetizione_sospetta, valuta_parte

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--device", default=None)
ap.add_argument("--model", default="medium")
a = ap.parse_args()

stato_path = a.out + ".stato.json"
stop_path = a.out + ".stop"
fermo = False
def _stop(*_):
    global fermo; fermo = True
signal.signal(signal.SIGTERM, _stop)

def ora():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def scrivi_stato(**kw):
    kw["aggiornato"] = ora()
    with open(stato_path, "w") as f:
        json.dump(kw, f, ensure_ascii=False)

import subprocess

# La parola chiave si riconosce NEL TESTO (spike): fuori sessione l'audio viene trascritto e
# scartato. Nella versione vera va riconosciuta prima della trascrizione (openWakeWord).
def parla(frase):
    subprocess.Popen(["say", "-v", "Alice", frase])

in_review = False
fuori_sessione_scartati = 0
modello = WhisperModel(a.model, device="cpu", compute_type="int8")
vad = VadOptions(min_silence_duration_ms=SILENZIO_MS, threshold=0.35)
q = queue.Queue()
def cb(indata, frames, t, status):
    q.put(indata[:, 0].copy())

buf = np.zeros(0, dtype=np.float32)
buf_t0 = time.time()
n = sum(1 for _ in open(a.out)) if os.path.exists(a.out) else 0   # append: la numerazione prosegue
livello_max = 0.0
inizio_sessione = ora()
with sd.InputStream(samplerate=SR, channels=1, dtype="float32", device=a.device, callback=cb, blocksize=SR // 10):
    scrivi_stato(stato="attivo", segmenti=0, inizio=inizio_sessione, device=a.device or "default")
    ultimo_controllo = time.time()
    while not fermo and not os.path.exists(stop_path):
        try:
            chunk = q.get(timeout=0.5)
        except queue.Empty:
            continue
        livello_max = max(livello_max, float(np.sqrt(np.mean(chunk ** 2))))
        buf = np.concatenate([buf, chunk])
        if time.time() - ultimo_controllo < 0.5:
            continue
        ultimo_controllo = time.time()
        scrivi_stato(stato=("review" if in_review else "in attesa della parola chiave"), segmenti=n, inizio=inizio_sessione, device=a.device or "default",
                     livello_rms_max_dall_ultimo_segmento=round(livello_max, 4), in_buffer_s=round(len(buf) / SR, 1))
        durata = len(buf) / SR
        ts = get_speech_timestamps(buf, vad)
        if not ts:
            if durata > 5:                      # solo silenzio: si scarta il buffer
                buf = buf[-SR:]; buf_t0 = time.time() - 1
            continue
        fine_parlato = ts[-1]["end"] / SR
        chiuso = (durata - fine_parlato) * 1000 >= SILENZIO_MS
        if not chiuso and durata < TETTO_S:
            continue
        taglio = int(ts[-1]["end"]) if chiuso else int(ts[-1]["start"]) if len(ts) > 1 else len(buf)
        seg_audio = buf[: max(taglio, int(ts[0]["start"]) + SR // 2)]
        t_ini = buf_t0 + ts[0]["start"] / SR
        t_fin = buf_t0 + len(seg_audio) / SR
        buf = buf[len(seg_audio):]
        buf_t0 = t_fin
        t0 = time.time()
        segs, _ = modello.transcribe(seg_audio, language="it", vad_filter=False, beam_size=5)
        segs = list(segs)
        # Filtro PER PARTE, non sul massimo del segmento (correzione 2026-11-20: il massimo
        # scartava 16 s di parlato vero per una pausa interna). Regola di Whisper: una parte
        # e' silenzio solo se no_speech_prob alto E avg_logprob basso, insieme.
        parti, parti_scartate = [], []
        for s in segs:
            t = s.text.strip()
            m = valuta_parte(t, s.no_speech_prob, s.avg_logprob, s.compression_ratio)
            d = {"testo": t, "no_speech_prob": round(s.no_speech_prob, 3), "avg_logprob": round(s.avg_logprob, 3),
                 "compression_ratio": round(s.compression_ratio, 3), "scartata": m is not None, "motivo": m}
            (parti_scartate if m else parti).append(d)
        testo = " ".join(p["testo"] for p in parti).strip()
        testo_scartato = " ".join(p["testo"] for p in parti_scartate).strip()
        ripetizione = ripetizione_sospetta(testo)
        nsp = max((s.no_speech_prob for s in segs), default=1.0)
        cr = max((s.compression_ratio for s in segs), default=0.0)
        lp = min((s.avg_logprob for s in segs), default=0.0)
        cmd, kw = comando(testo) if testo else (None, None)
        if cmd == "inizio" and not in_review:
            in_review = True; parla("Ascolto la review.")
        elif cmd == "fine" and in_review:
            in_review = False
            parla(f"Fine della review. {n} segmenti raccolti.")
        elif cmd == "sconosciuto":
            parla("Comando non riconosciuto.")
        if not in_review and cmd != "fine":
            # Fuori sessione nulla si scrive: si conta soltanto.
            fuori_sessione_scartati += 1
            scrivi_stato(stato="in attesa della parola chiave", segmenti=n, inizio=inizio_sessione,
                         device=a.device or "default", fuori_sessione_scartati=fuori_sessione_scartati)
            livello_max = 0.0
            continue
        motivo = None if testo else ("tutte le parti scartate" if parti_scartate else "testo vuoto")
        n += 1
        riga = {"id": f"S{n:03d}",
                "inizio": datetime.fromtimestamp(t_ini, timezone.utc).isoformat(timespec="seconds"),
                "fine": datetime.fromtimestamp(t_fin, timezone.utc).isoformat(timespec="seconds"),
                "durata_audio_s": round(len(seg_audio) / SR, 2),
                "trascrizione_s": round(time.time() - t0, 2),
                "testo": testo, "no_speech_prob": round(nsp, 3),
                "compression_ratio": round(cr, 3), "avg_logprob": round(lp, 3),
                "scartato": motivo is not None, "motivo": motivo,
                "parlante": "non attribuito",
                "comando": cmd, "parola_chiave_letta": kw,
                "marcato_rilievo": cmd == "rilievo",
                "testo_scartato": testo_scartato, "ripetizione_sospetta": ripetizione,
                "parti": parti + parti_scartate}
        with open(a.out, "a") as f:
            f.write(json.dumps(riga, ensure_ascii=False) + "\n")
        scrivi_stato(stato=("review" if in_review else "in attesa della parola chiave"), segmenti=n, inizio=inizio_sessione, device=a.device or "default",
                     livello_rms_max=round(livello_max, 4), ultimo_segmento=riga["id"])
        livello_max = 0.0
scrivi_stato(stato="fermo", segmenti=n, inizio=inizio_sessione, device=a.device or "default")

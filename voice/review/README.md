# voice/review — spike della review in ascolto continuo (EP-117)

**Stato: spike, non implementazione.** È il codice usato il 2026-11-20 per simulare una revisione
funzionale col canale vocale prima di costruire EP-117. Serve a ripartire da ciò che è stato
provato, non come base da estendere senza i criteri di US-447..US-450.

| File | Che cosa fa | Dipendenze |
|---|---|---|
| `logica.py` | parola chiave e comandi, filtro per parte di segmento, ripetizioni sospette, verifica delle citazioni | nessuna (stdlib); testata in `voice/tests/test_review_logica.py` |
| `ascolto_spike.py` | ascolto dal microfono, segmentazione sui silenzi (700 ms), trascrizione faster-whisper, JSONL append-only, conferma vocale con `say` di macOS | `faster-whisper`, `sounddevice`, `numpy`; macOS per `say` |

## Come si lancia

```bash
# ambiente vocale dedicato (non tocca il Python di sistema)
/usr/bin/python3 -m venv ~/.local/share/soli-voice/venv
~/.local/share/soli-voice/venv/bin/pip install faster-whisper sounddevice numpy

# dalla radice della factory
~/.local/share/soli-voice/venv/bin/python -m voice.review.ascolto_spike \
    --out ~/.local/share/soli-voice/review/<sessione>.jsonl
# stop: touch <out>.stop
```

Comandi a voce (decisione del committente, 2026-11-20):

- «prometeus, inizia la review» apre la sessione, con la conferma vocale «Ascolto la review»;
- «prometeus, rilievo …» dentro la sessione marca un rilievo esplicito;
- «prometeus, fine review» (oppure «chiudi») chiude la sessione e annuncia quanti segmenti ha raccolto.

Fuori sessione **niente si scrive**: si conta soltanto.

## Che cosa la simulazione ha mostrato

Fonte: `deliverables/plancia-redesign/08-sessione-revisione.md`, §«Simulazione della review in
ascolto continuo». In breve:

1. **Il filtro sul massimo di `no_speech_prob` ha scartato il rilievo vero** (16 s di parlato,
   0,979). Il filtro si applica **per parte**, con la regola di Whisper (`no_speech_prob` alto **e**
   `avg_logprob` basso).
2. **«Sottotitoli creati dalla comunità Amara.org»** è comparsa 2 volte su 2 in coda ai segmenti
   lunghi. La ferma solo la lista `ALLUCINAZIONI_NOTE`, che è una lista: una variante nuova passa.
3. **Senza audio un segmento scartato non si ritrascrive**: per questo le metriche si salvano per
   ogni parte, e il testo scartato resta nel JSONL (`testo_scartato`).
4. **Un ascolto muto sembra fermo**: per questo servono la conferma vocale e lo stato aggiornato
   anche nel silenzio.
5. **La parola chiave è stata riconosciuta 5 volte su 5**, in quattro grafie. Qui però è
   riconosciuta **nel testo**, quindi fuori sessione l'audio viene trascritto e poi buttato. La
   versione vera la riconosce prima della trascrizione (openWakeWord, già nel canale).
6. **Un microfono con soppressione del rumore dà zeri esatti nel silenzio.** Il microfono si
   verifica mentre qualcuno parla.

## Che cosa questo spike NON fa

- non riconosce la parola chiave dall'audio: trascrive tutto e poi scarta;
- non estrae i rilievi: nella simulazione l'estrattore era la sessione (US-448 da costruire);
- non ha la vista in plancia (US-449);
- non ha misurato la qualità della trascrizione (WER) né la resa dell'estrattore (US-450);
- `say` esiste solo su macOS; piper (il TTS del canale) non era installato.

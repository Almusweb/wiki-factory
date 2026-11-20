"""Test della logica pura della review in ascolto continuo (EP-117, spike 2026-11-20).

I casi vengono dalla simulazione reale (segmenti S004-S013 del verbale della plancia).
Nessuna dipendenza: niente microfono, niente faster-whisper.
"""
from voice.review.logica import comando, ripetizione_sospetta, valuta_parte, verifica_citazioni


def test_parola_chiave_nelle_grafie_osservate():
    assert comando("Prometheus inizia la review.") == ("inizio", "prometheus")
    assert comando("Prometeo, si inizia la review.") == ("inizio", "prometeo")
    assert comando("Prometeos, fine review.") == ("fine", "prometeos")
    assert comando("Prometheus, chiudi review.") == ("fine", "prometheus")
    assert comando("prometeus rilievo: la barra è alta")[0] == "rilievo"


def test_senza_parola_chiave_non_e_un_comando():
    # S007 e S012: «fine review» / «Chiudi il review» detti senza parola chiave
    assert comando("registra la review, fine review") == (None, None)
    assert comando("Chiudi il review") == (None, None)
    assert comando("Promemoria per domani") == (None, None)


def test_parola_chiave_senza_comando_e_dichiarata():
    assert comando("Prometeus, che ore sono?")[0] == "sconosciuto"


def test_filtro_per_parte_tiene_il_parlato_vero():
    # S006: il massimo di no_speech_prob (0,979) aveva scartato il rilievo; logprob -0,597 = parlato
    assert valuta_parte("applichiamo alla plancia le review grafiche", 0.979, -0.597, 1.222) is None


def test_filtro_per_parte_scarta_il_silenzio():
    assert valuta_parte("...", 0.9, -1.5, 1.0) is not None
    assert valuta_parte("", 0.1, -0.1, 1.0) == "vuota"


def test_allucinazione_nota_e_fermata_solo_dalla_lista():
    # S005: avg_logprob -0,348 -> la regola no_speech/logprob da sola la lascerebbe passare
    t = "Sottotitoli creati dalla comunità Amara.org"
    assert valuta_parte(t, 0.859, -0.348, 0.846) == "allucinazione nota"


def test_ripetizione_in_coda_dichiarata():
    s006 = ("Perfetto, facciamo una review di prova, applichiamo alla plancia le review grafiche "
            "che erano state richieste. Perfetto, facciamo una review grafiche che erano state richieste.")
    assert ripetizione_sospetta(s006) == "perfetto, facciamo una review"
    assert ripetizione_sospetta("la barra dei compartimenti su telefono è troppo alta") is None


SEGMENTI = {
    "S010": {"testo": "nel caso specifico sono stati prodotti diversi documenti.",
             "testo_scartato": "Sottotitoli creati dalla comunità Amara.org"},
    "S011": {"testo": "che dovrebbero rispettare i template canonici di documentazione"},
}


def test_citazione_esatta_su_piu_segmenti_e_valida():
    c = [{"id": "K3", "segmenti": ["S010", "S011"],
          "citazione": "sono stati prodotti diversi documenti. che dovrebbero rispettare i template canonici"}]
    assert verifica_citazioni(SEGMENTI, c) == (["K3"], [])


def test_citazione_alterata_e_scartata_non_corretta():
    c = [{"id": "K9", "segmenti": ["S011"], "citazione": "che devono rispettare i template"}]
    validi, scartati = verifica_citazioni(SEGMENTI, c)
    assert validi == [] and scartati[0]["motivo"] == "citazione non ritrovata nei segmenti citati"


def test_segmento_inesistente_e_scartato():
    validi, scartati = verifica_citazioni(SEGMENTI, [{"id": "K8", "segmenti": ["S099"], "citazione": "x"}])
    assert validi == [] and "inesistenti" in scartati[0]["motivo"]

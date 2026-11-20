// Plancia — resa dello stato (EP-067). Nessuna dipendenza, nessun passo di build.
//
// Tre regole che il resto del file rispetta ovunque:
//   1. `available: false` NON diventa mai 0. Diventa «non osservabile» + la ragione.
//   2. Le etichette arrivano dal server, mai dal frontend. Chi produce una misura sa
//      come si chiama; chi la disegna no — e infatti la pagina ha mostrato per un po'
//      `events.by_state` a esseri umani.
//   3. Ogni transizione di stato passa da annuncia(), che scrive in una regione live
//      senza spostare il focus, e annuncia solo i CAMBIAMENTI.

'use strict';

import { Mascotte, statoDa, statoFactory, STATI } from '/mascotte.js';

const INTERVALLO_MS = 5000;
let ultimaFase = null;
let ultimeAssenti = '';
let ultimaDomanda = null;
let inSospeso = null;
let mascotte = null;
let appenaAvviato = false;
let innesco = null;          // il comando che ha aperto la conferma: li' si torna chiudendola
let staleAttivo = false;
let ricevutoMs = null;       // quando e' arrivata l'ultima lettura riuscita
let voceInVolo = false;

const $ = (id) => document.getElementById(id);

function elemento(tag, testo, classe) {
  const el = document.createElement(tag);
  if (testo !== undefined && testo !== null) el.textContent = String(testo);
  if (classe) el.className = classe;
  return el;
}

function eta(secondi) {
  if (secondi === null || secondi === undefined) return 'mai';
  if (secondi < 60) return `${Math.round(secondi)} s fa`;
  if (secondi < 3600) return `${Math.round(secondi / 60)} min fa`;
  return `${Math.round(secondi / 3600)} h fa`;
}

// Due regioni live distinte: `annuncio` per le azioni (esito di un comando, un canale
// acceso o spento), `annuncio-fonti` per lo stato delle fonti e del collegamento. Con una
// sola, un annuncio sovrascriveva l'altro prima che fosse letto.
function annuncia(messaggio, regione = 'annuncio') {
  const el = $(regione);
  if (el.textContent !== messaggio) el.textContent = messaggio;
}

// Un'eta' viva: porta con se' l'eta' al momento della lettura e il prefisso, e un unico
// timer la tiene vera fra un aggiornamento e l'altro. Un'ora di orologio («14:05:34»
// ) costringe a sapere che ora e' adesso; «letto 12 s fa» no.
function elementoEta(prefisso, secondi, classe = 'eta') {
  const el = elemento('span', `${prefisso} ${eta(secondi)}`, classe);
  el.dataset.etaBase = String(Math.round(secondi));
  el.dataset.prefisso = prefisso;
  return el;
}

function ticchettio() {
  if (ricevutoMs === null) return;
  const trascorso = (Date.now() - ricevutoMs) / 1000;
  document.querySelectorAll('[data-eta-base]').forEach((el) => {
    const testo = `${el.dataset.prefisso} ${eta(Number(el.dataset.etaBase) + trascorso)}`;
    if (el.textContent !== testo) el.textContent = testo;
  });
}

// Un guasto di rete e un errore del servizio sono due cose diverse con due rimedi
// diversi, e a chi legge serve la frase, non il nome dell'eccezione.
class ErroreDiComunicazione extends Error {
  constructor(tipo, codice) { super(tipo); this.tipo = tipo; this.codice = codice; }
}

async function chiama(percorso, corpo) {
  let risposta;
  try {
    risposta = await fetch(percorso, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(corpo),
    });
  } catch (problema) {
    console.error('[plancia]', problema);
    throw new ErroreDiComunicazione('rete');
  }
  let esito = null;
  try { esito = await risposta.json(); } catch { /* corpo non JSON: vale il codice */ }
  if (esito === null || (risposta.status >= 500)) {
    throw new ErroreDiComunicazione('servizio', risposta.status);
  }
  return { codice: risposta.status, esito };
}

function fraseErrore(problema, cosa) {
  if (problema instanceof ErroreDiComunicazione && problema.tipo === 'rete') {
    return `Non riesco a raggiungere la plancia: ${cosa} potrebbe non essere partito. ` +
           'Controlla la connessione e riprova.';
  }
  if (problema instanceof ErroreDiComunicazione) {
    return `Il servizio ha risposto con un errore (${problema.codice}): ${cosa} non è stato eseguito. ` +
           'Riprova fra poco.';
  }
  console.error('[plancia]', problema);
  return `Si è verificato un errore imprevisto: ${cosa} potrebbe non essere stato eseguito. Ricarica la pagina.`;
}

// Esito dei comandi e fine del turno: una regione `log` VISIBILE accanto ai comandi.
// Le voci si aggiungono (le ultime tre restano), cosi' un annuncio non cancella il
// precedente e chi ingrandisce la pagina lo vede dove ha premuto.
function esito(messaggio, problema = false) {
  const log = $('esito-comando');
  const ultimo = log.lastElementChild;
  if (ultimo && ultimo.textContent === messaggio) return;
  log.append(elemento('p', messaggio, problema ? 'ragione' : null));
  while (log.children.length > 3) log.firstElementChild.remove();
}

// Aggiorna il DOM esistente invece di rimpiazzarlo: un nodo ricreato a ogni lettura fa
// perdere il fuoco a chi sta navigando con la tastiera (e a chi ci mette piu' di cinque
// secondi fra un Tab e un Invio). I nodi uguali restano gli stessi.
const ATTRIBUTI_DEL_BROWSER = {
  scorrevole: ['tabindex', 'role', 'aria-label', 'data-scorre'],  // per classe
  DETAILS:    ['open'],                                            // per nodeName
};

// NON aggiungere qui `value`, `checked` o `selected`: sembrano casi uguali a `open` e non lo
// sono. Quando si digita in un campo o si spunta una casella, il browser cambia la PROPRIETA'
// (`input.value`, `input.checked`), non l'attributo: l'attributo continua a riflettere il
// valore di default. Tenerli in questa tabella non protegge nulla di cio' che la persona ha
// scritto, e lascia credere il contrario a chi legge. Cio' che protegge il testo digitato e'
// un'altra cosa, gia' garantita da `riconciliaFigli`: il nodo non viene sostituito, quindi la
// sua proprieta' sopravvive. `open` di <details> e' diverso perche' il browser scrive davvero
// l'ATTRIBUTO.

function attributiDelBrowser(nodo) {
  const elenco = [...(ATTRIBUTI_DEL_BROWSER[nodo.nodeName] || [])];
  if (nodo.classList) {
    for (const classe of nodo.classList) {
      if (Object.hasOwn(ATTRIBUTI_DEL_BROWSER, classe)) elenco.push(...ATTRIBUTI_DEL_BROWSER[classe]);
    }
  }
  return elenco;
}

function riconcilia(vecchio, nuovo) {
  if (vecchio.nodeType !== nuovo.nodeType || vecchio.nodeName !== nuovo.nodeName) {
    vecchio.replaceWith(nuovo);
    return;
  }
  if (vecchio.nodeType === Node.TEXT_NODE) {
    if (vecchio.data !== nuovo.data) vecchio.data = nuovo.data;
    return;
  }
  // Alcuni attributi non li scrive il renderer: li scrive il BROWSER (`open` di un <details>
  // aperto dalla persona) oppure una misura a runtime (`tabindex` delle regioni a scorrimento,
  // governato da `aggiornaScorrevoli`). Sul nodo appena renderizzato non ci sono mai: se li
  // togliessimo a ogni lettura, un <details> si richiuderebbe da solo entro 5 s e una regione
  // col fuoco lo perderebbe.
  // Criterio di ammissione in `ATTRIBUTI_DEL_BROWSER`: ci entra solo un attributo che il
  // browser o una nostra misura a runtime scrivono DAVVERO sul DOM come attributo, mai uno che
  // il renderer sa produrre e mai uno che in realta' vive come proprieta' (vedi la nota accanto
  // alla tabella).
  const misurati = attributiDelBrowser(vecchio);
  for (const a of [...vecchio.attributes]) {
    if (misurati.includes(a.name)) continue;
    if (!nuovo.hasAttribute(a.name)) vecchio.removeAttribute(a.name);
  }
  for (const a of nuovo.attributes) {
    if (misurati.includes(a.name)) continue;
    if (vecchio.getAttribute(a.name) !== a.value) vecchio.setAttribute(a.name, a.value);
  }
  riconciliaFigli(vecchio, nuovo);
}

function riconciliaFigli(vecchio, nuovo) {
  const v = [...vecchio.childNodes];
  const n = [...nuovo.childNodes];
  n.forEach((figlio, i) => (v[i] ? riconcilia(v[i], figlio) : vecchio.append(figlio)));
  v.slice(n.length).forEach((figlio) => figlio.remove());
}

// Il contenitore e' riempito in un frammento a parte e poi riconciliato.
function riempi(contenitore, costruisci) {
  const bozza = document.createElement(contenitore.tagName);
  costruisci(bozza);
  riconciliaFigli(contenitore, bozza);
}

// ── Stato delle fonti: una sola classificazione, usata da riga di testata, marcatori e
//    annuncio, cosi' i tre contano allo stesso modo ──────────────────────────────────

const IN_LETTURA = /lettura in corso/;

function statoFonte(pannello) {
  if (!pannello.observable) {
    const attesa = pannello.readings.length > 0 &&
      pannello.readings.every((r) => !r.available && IN_LETTURA.test(r.reason || ''));
    return attesa ? 'in-lettura' : 'assente';
  }
  return pannello.readings.some((r) => r.stale) ? 'stantio' : 'ok';
}

function fraseFonti(pannelli) {
  const stati = pannelli.map(statoFonte);
  const conta = (nome) => stati.filter((x) => x === nome).length;
  const assenti = conta('assente');
  const inLettura = conta('in-lettura');
  const stantie = conta('stantio');
  const parti = [`${pannelli.length - assenti - inLettura} osservabili su ${pannelli.length}`];
  if (assenti) parti.push(`${assenti} non osservabili`);
  if (inLettura) parti.push(`${inLettura} in lettura`);
  if (stantie) parti.push(`${stantie} con dati stantii`);
  return `Fonti: ${parti.join(', ')}.`;
}

// ── Testata ────────────────────────────────────────────────────────────

function renderTestata(payload) {
  // La frase di stato e' scritta SEMPRE, prima del ramo che decide se disegnare la
  // mascotte: se stesse dopo, spegnere la mascotte spegnerebbe anche l'informazione.
  // La frase parla della FACTORY (il lavoro, le altre sessioni); le fonti hanno la loro
  // riga, contata come la regione `status`. La mascotte, invece, puo' mostrare entrambe.
  const chiave = statoDa(payload);
  $('stato-frase').textContent = STATI[statoFactory(payload)].testo;
  $('stato-fonti').textContent = fraseFonti(payload.panels || []);

  const host = $('mascotte');
  const accesa = Mascotte.attiva();
  host.hidden = !accesa;
  if (accesa) {
    if (!mascotte) mascotte = new Mascotte(host);
    mascotte.mostra(chiave);
  }

  const id = payload.identity;

  // Il titolo arriva dalla configurazione (`visual_channel.titolo`, default «Plancia»): chi
  // apre la pagina deve riconoscere il proprio progetto, non lo strumento. Si scrive solo se
  // e' cambiato, perche' `riconcilia` non governa gli elementi fuori dai riquadri e riscrivere
  // un h1 a ogni ciclo di 5 s lo farebbe rileggere da una tecnologia assistiva.
  const titolo = id.titolo || 'Plancia';
  const h1 = $('titolo-pagina');
  if (h1 && h1.textContent !== titolo) h1.textContent = titolo;
  if (document.title.indexOf(titolo) !== 0) document.title = `${titolo} · attività della factory`;

  const dl = document.createElement('dl');
  const voci = [
    ['Plancia', `v${id.plancia_version}`],
    ['Pattern factory', id.pattern_version + (id.pattern_version_drift ? ' — divergente' : '')],
    ['Dati', id.read_only ? 'sola lettura' : 'scrittura'],
    ['Aggiornamento', `ogni ${INTERVALLO_MS / 1000} s`],
  ];
  for (const [nome, valore] of voci) {
    const riga = document.createElement('div');
    riga.append(elemento('dt', nome), elemento('dd', valore));
    dl.append(riga);
  }
  riconciliaFigli($('identita'), dl);
}

// ── Turno ──────────────────────────────────────────────────────────────

function renderTurno(turno, attesa) {
  riempi($('turno'), (box) => disegnaTurno(box, turno, attesa));
  aggiornaModuloEAnnunci(turno);
}

function disegnaTurno(box, turno, attesa) {
  if (turno.phase === 'inattivo') {
    box.append(elemento('p', 'Nessun lavoro in corso.', 'attesa'));
    box.append(elementoEta('Stato letto', 0));
  } else {
    box.append(elemento('p', STATI[statoFactory({ turn: turno })]?.testo || turno.phase, 'valore'));
    box.append(elementoEta('Stato letto', 0));

    if (turno.question) box.append(elemento('p', `Domanda: ${turno.question}`));
    if (turno.acknowledgment) box.append(elemento('p', turno.acknowledgment));

    // Gli adapter non-streaming non emettono avanzamenti: fra l'acknowledgment e la fine non arriva
    // alcun `Progress`. La plancia non puo' inventare un avanzamento che non le e' stato
    // comunicato, ma puo' dire da quanto attende e quanto manca — e «immobile» era
    // indistinguibile da «rotta».
    if (attesa) {
      const rimane = attesa.scade_fra_secondi;
      box.append(elemento('p',
        `In attesa da ${Math.round(attesa.da_secondi)} s — scade fra ${rimane} s.`,
        rimane < 30 ? 'ragione' : 'eta'));
      const barra = document.createElement('progress');
      barra.max = attesa.da_secondi + rimane;
      barra.value = attesa.da_secondi;
      barra.setAttribute('aria-label', `attesa della risposta, ${rimane} secondi alla scadenza`);
      box.append(barra);

      // Il dettaglio viene dal transcript della sessione figlia, non dal contratto: il
      // adapter non fa streaming e fra l'acknowledgment e la fine non arriva nulla.
      // Senza questo la sezione resta su una riga sola per minuti.
      const azioni = attesa.attivita || [];
      if (azioni.length) {
        box.append(elemento('p', `Sta facendo — ${azioni.length} azioni finora`, 'etichetta'));
        const lista = document.createElement('ol');
        lista.className = 'azioni-turno';
        lista.setAttribute('aria-label', 'azioni svolte finora');
        for (const azione of azioni) {
          const voce = document.createElement('li');
          voce.append(elemento('span', azione.strumento, 'strumento'));
          if (azione.su) voce.append(elemento('span', azione.su));
          lista.append(voce);
        }
        box.append(lista);
      } else {
        box.append(elemento('p',
          'Nessuna azione ancora visibile: la sessione non ha ancora registrato il suo lavoro.',
          'eta'));
      }
    }

    if (turno.progress) {
      const barra = document.createElement('progress');
      if (!turno.progress.indeterminate) { barra.max = 1; barra.value = turno.progress.pct; }
      barra.setAttribute('aria-label', turno.progress.text || 'avanzamento');
      box.append(elemento('p', turno.progress.text || 'in corso'), barra);
    }
    if (turno.summary) box.append(elemento('p', turno.summary));
    if (turno.error) box.append(elemento('p', `Errore: ${turno.error}`, 'ragione'));
    if (turno.artifact_count) {
      box.append(elemento('p',
        `${turno.artifact_count} file prodotti — mostrati solo qui, mai letti ad alta voce.`, 'eta'));
    }
  }
}

function aggiornaModuloEAnnunci(turno) {

  // Il modulo NON dipende da `turno.question`: nessuno dei sei adapter emette mai quel
  // tipo, e una domanda dell'agente («Palla a te: approvi Wave 1?») arriva dentro la
  // sintesi, con il turno che si chiude normalmente. Legare il modulo al `Question`
  // mandava la domanda in un vicolo cieco.
  const modulo = $('risposta');
  const concluso = turno.phase === 'concluso' || turno.phase === 'errore';
  modulo.hidden = !(turno.question || concluso);

  // Il focus va sul campo solo per un `Question` esplicito, e solo alla PRIMA comparsa:
  // strapparlo a ogni ciclo a chi sta scrivendo sarebbe peggio che non darlo. Su un turno
  // concluso non si prende il focus — la conversazione la riprende l'utente quando vuole.
  if (turno.question && turno.question !== ultimaDomanda) {
    ultimaDomanda = turno.question;
    $('risposta-testo').focus();
  }
  if (!turno.question) ultimaDomanda = null;

  if (turno.phase !== ultimaFase) {
    const primaLettura = ultimaFase === null;
    ultimaFase = turno.phase;
    const frase = fraseDiFase(turno);
    // All'apertura della pagina un «nessun lavoro in corso» non e' una novita'. E
    // «sta lavorando» subito dopo «Avviato» ripeterebbe cio' che l'esito ha gia' detto.
    const ridondante = (primaLettura && ['inattivo', 'concluso'].includes(turno.phase)) ||
                       (turno.phase === 'in-lavorazione' && appenaAvviato);
    appenaAvviato = false;
    if (frase && !ridondante) esito(frase, turno.phase === 'errore');
  }
}

// La fase interna («concluso», «in-lavorazione») non e' una frase: a chi ascolta si dice
// cosa e' successo e dove leggere il risultato.
function fraseDiFase(turno) {
  switch (turno.phase) {
    case 'attesa-risposta':
      return `La factory attende una tua risposta. ${turno.question || ''}`.trim();
    case 'concluso':
      return 'Il lavoro si è concluso. Il risultato è in «Lavoro in corso»; ' +
             'puoi rispondere con il modulo sotto il risultato.';
    case 'errore':
      return 'Il lavoro si è chiuso con un errore. Il dettaglio è in «Lavoro in corso».';
    case 'in-lavorazione':
      return 'La factory sta lavorando. Il risultato comparirà in «Lavoro in corso».';
    case 'inattivo':
      return 'Nessun lavoro in corso.';
    default:
      return STATI[turno.phase]?.testo || null;
  }
}

// ── Comandi ────────────────────────────────────────────────────────────

const SFONDO = ['.salta', 'header', 'main', 'footer', '#dati-stantii'];
let azioniCorrenti = new Map();

function frasePerConferma(azione, esitoServer) {
  // La conseguenza arriva dal server; il nome del comando la completa, perche' «cambia lo
  // status di una pagina» detto da solo non dice di quale operazione si parla. I
  // backtick del testo sorgente non si pronunciano: diventano virgolette.
  const testo = String(esitoServer.conseguenza).replace(/`([^`]*)`/g, '«$1»');
  return `«${azione.nome}»: ${testo}`;
}

function mostraConferma(azione, esitoServer) {
  inSospeso = azione;
  $('conferma-titolo').textContent = `Conferma: ${azione.nome}`;
  $('conferma-testo').textContent = frasePerConferma(azione, esitoServer);
  $('conferma-si').setAttribute('aria-label', `Procedi con ${azione.nome}`);
  $('conferma-no').setAttribute('aria-label', `Annulla ${azione.nome}`);
  $('conferma').hidden = false;
  for (const sel of SFONDO) document.querySelectorAll(sel).forEach((e) => { e.inert = true; });
  // Il focus parte da «Annulla»: l'azione difficile da annullare non deve essere quella
  // che un Invio istintivo conferma. Il dialogo si legge UNA volta, dal suo nome e dalla
  // sua descrizione: niente annuncio duplicato in una regione live.
  $('conferma-no').focus();
}

function nascondiConferma({ tornaAlComando = true } = {}) {
  inSospeso = null;
  $('conferma').hidden = true;
  for (const sel of SFONDO) document.querySelectorAll(sel).forEach((e) => { e.inert = false; });
  if (tornaAlComando && innesco && innesco.isConnected) innesco.focus();
}

function annullaConferma() {
  nascondiConferma();
  esito('Azione annullata.');
}

async function esegui(azione, conferma) {
  let risposta;
  try {
    risposta = await chiama('/api/invia', { testo: azione.direttiva, conferma });
  } catch (problema) {
    if ($('conferma').hidden === false) nascondiConferma();
    esito(fraseErrore(problema, `«${azione.nome}»`), true);
    return;
  }
  const { codice, esito: esitoServer } = risposta;
  if (esitoServer.stato === 'conferma-richiesta') return mostraConferma(azione, esitoServer);
  nascondiConferma();
  const messaggi = {
    'avviato': `Avviato: ${azione.nome}. Il risultato comparirà in «Lavoro in corso», ` +
               'in alto nella pagina; ti avviso qui quando il lavoro è concluso.',
    'non-disponibile': `Comandi non disponibili: ${esitoServer.ragione}`,
    'occupato': `Non posso avviarlo adesso: ${esitoServer.ragione}`,
  };
  appenaAvviato = esitoServer.stato === 'avviato';
  esito(messaggi[esitoServer.stato] || `Esito ${codice}: ${esitoServer.stato}`,
        esitoServer.stato !== 'avviato');
  aggiorna();
}

function renderComandi(scrittura, concorrenza) {
  const nota = $('scrittura-stato');
  nota.className = 'sezione-nota';
  nota.textContent = scrittura.scrittura_disponibile
    ? (scrittura.turno_in_corso
        ? 'Un lavoro è in corso. I comandi tornano disponibili quando finisce.'
        : 'I comandi sono disponibili. Ogni comando passa dalla sessione: la plancia non scrive nulla da sola.')
    : `Comandi non disponibili — ${scrittura.ragione_indisponibile}`;

  azioniCorrenti = new Map(scrittura.azioni.map((a) => [a.direttiva, a]));
  const bloccati = !scrittura.scrittura_disponibile || !!scrittura.turno_in_corso;
  riempi($('azioni'), (contenitore) => {
    for (const azione of scrittura.azioni) {
      const cella = elemento('div', null, 'comando');
      const b = document.createElement('button');
      b.type = 'button';
      b.dataset.direttiva = azione.direttiva;
      b.append(elemento('span', azione.nome));
      // Il nome accessibile e' il testo visibile e basta («Controllo di salute»): la
      // descrizione e il motivo di un eventuale blocco si leggono dopo, come descrizione.
      if (azione.difficile_da_annullare) {
        const pastiglia = elemento('span', 'conferma', 'pastiglia');
        pastiglia.setAttribute('aria-hidden', 'true');
        b.append(pastiglia);
      }
      const idDescrizione = `descrizione-${azione.direttiva.replace(/\W+/g, '')}`;
      b.setAttribute('aria-describedby', bloccati ? `${idDescrizione} scrittura-stato` : idDescrizione);
      // `aria-disabled` e non `disabled`: un pulsante disabilitato esce dall'ordine di
      // tabulazione e il fuoco che ci stava sopra va a `body`. Cosi' resta dov'e' e,
      // se lo si preme, la pagina dice perche' non succede nulla.
      if (bloccati) b.setAttribute('aria-disabled', 'true');
      const descrizione = elemento('p', azione.descrizione +
        (azione.difficile_da_annullare ? '. Chiede una conferma prima di partire.' : ''),
        'comando-descrizione');
      descrizione.id = idDescrizione;
      cella.append(b, descrizione);
      contenitore.append(cella);
    }
  });

  const avviso = $('concorrenza');
  if (concorrenza && concorrenza.avvertenza) {
    avviso.textContent = `${concorrenza.avvertenza} Osservato ${eta(concorrenza.eta_osservazione_s)}.`;
    avviso.hidden = false;
  } else {
    avviso.hidden = true;
  }
}

// Etichetta STATICA + `aria-pressed` + una pastiglia che dice lo stato a chi vede.
// Cambiare etichetta e `aria-pressed` insieme e' un antipattern noto: lo screen reader
// legge «Disattiva il canale vocale, premuto» e chi ascolta non sa piu' se e' acceso.
function interruttore(elementoBottone, etichetta, acceso, parolaOn, parolaOff) {
  // La pastiglia e' `aria-hidden`: lo stato lo dice gia' `aria-pressed`, e lasciarla
  // leggere produceva il nome accessibile «Canale vocalespento» — due informazioni
  // attaccate, una delle quali gia' ridondante. Per chi vede resta, perche' `aria-pressed`
  // non si vede.
  const pastiglia = elemento('span', acceso ? parolaOn : parolaOff, 'pastiglia');
  pastiglia.setAttribute('aria-hidden', 'true');
  elementoBottone.replaceChildren(elemento('span', etichetta), pastiglia);
  elementoBottone.setAttribute('aria-pressed', String(acceso));
}

function renderVoce(voce) {
  const b = $('voce-toggle');
  const bloccato = !voce.disponibile && !voce.attivo;
  interruttore(b, 'Canale vocale', voce.attivo, 'attivo', bloccato ? 'non disponibile' : 'spento');
  // Come per i comandi: `aria-disabled` lascia il pulsante nell'ordine di Tab, e il motivo
  // (la nota qui sotto) e' collegato come descrizione, non solo vicino.
  if (bloccato || voceInVolo) b.setAttribute('aria-disabled', 'true');
  else b.removeAttribute('aria-disabled');
  b.setAttribute('aria-describedby', 'voce-stato');

  const nota = $('voce-stato');
  if (!voce.disponibile && !voce.attivo) {
    nota.className = 'sezione-nota ragione';
    nota.textContent = `Il canale vocale non è disponibile: ${voce.ragione}.`;
  } else if (voce.attivo) {
    nota.className = 'sezione-nota';
    nota.textContent = `Voce ${voce.voce}: ${voce.pronunciati} frasi lette ad alta voce. ` +
      `I file prodotti non vengono mai letti (${voce.artefatti_non_pronunciati} finora).`;
  } else {
    nota.className = 'sezione-nota';
    nota.textContent = 'Il canale vocale legge ad alta voce le stesse frasi dello schermo. I file prodotti non vengono mai letti.';
  }
}

// ── Fonti ──────────────────────────────────────────────────────────────

function renderValore(lettura) {
  const valore = lettura.value;

  if (Array.isArray(valore) && valore.length && typeof valore[0] === 'object') {
    const frammento = document.createDocumentFragment();
    // Il singolare lo dichiara il server, come il «vuoto»: dedurlo da `unit` al plurale
    // produceva «1 avvisi».
    const unita = valore.length === 1 && lettura.detail && lettura.detail.singolare
      ? lettura.detail.singolare : (lettura.unit || 'voci');
    frammento.append(elemento('p', `${valore.length} ${unita}`, 'valore'));
    const tabella = document.createElement('table');
    const colonne = Object.keys(valore[0]);
    const testa = document.createElement('thead');
    const riga = document.createElement('tr');
    colonne.forEach((c) => riga.append(elemento('th', c)));
    testa.append(riga);
    tabella.append(testa);
    const corpo = document.createElement('tbody');
    // Il taglio a 8 righe e' il default; una misura che va letta per intero lo dichiara
    // (`detail.righe: null`). Deciderlo qui nasconderebbe in silenzio meta' di un report.
    const limite = lettura.detail && 'righe' in lettura.detail ? lettura.detail.righe : 8;
    valore.slice(0, limite ?? valore.length).forEach((voce) => {
      const tr = document.createElement('tr');
      colonne.forEach((c) => tr.append(elemento('td', voce[c] ?? '—')));
      corpo.append(tr);
    });
    tabella.append(corpo);
    const scorrevole = elemento('div', null,
      valore.length > 8 && limite === null ? 'scorrevole lunga' : 'scorrevole');
    // Punto di Tab, ruolo e nome li assegna `aggiornaScorrevoli` SOLO se la regione scorre
    // davvero (2.1.1): una regione che mostra tutto non e' un punto di sosta ne' un
    // landmark.
    scorrevole.dataset.etichetta = lettura.label;
    scorrevole.append(tabella);
    frammento.append(scorrevole);
    return frammento;
  }

  if (valore && typeof valore === 'object' && !Array.isArray(valore)) {
    const dl = elemento('dl', null, 'coppie');
    for (const [k, v] of Object.entries(valore)) {
      const riga = document.createElement('div');
      riga.append(elemento('dt', k), elemento('dd', v));
      dl.append(riga);
    }
    return dl;
  }

  if (Array.isArray(valore)) {
    // Il testo del «vuoto» arriva dal server con l'accordo giusto. Comporlo qui da
    // `unit` al plurale produceva «nessuna sessioni».
    return elemento('p', valore.length ? valore.join(', ')
                                       : (lettura.vuoto || 'nessun elemento'), 'valore');
  }
  // Un collegamento lo dichiara il server (`detail.href`), mai il frontend: chi produce
  // la misura sa dove sta la sua vista completa.
  if (lettura.detail && lettura.detail.href) {
    const p = elemento('p', null, 'valore');
    const a = elemento('a', valore);
    a.href = lettura.detail.href;
    a.target = '_blank';
    a.rel = 'noopener';
    a.append(elemento('span', ' (si apre in una nuova scheda)', 'solo-lettori'));
    p.append(a);
    return p;
  }
  if (valore === null || valore === undefined) return elemento('p', '—', 'valore');
  if (typeof valore === 'number') {
    const n = Number.isInteger(valore) ? valore : valore.toFixed(2);
    return elemento('p', `${n}${lettura.unit ? ' ' + lettura.unit : ''}`, 'valore');
  }
  return elemento('p', `${valore}${lettura.unit ? ' ' + lettura.unit : ''}`, 'valore');
}

// Etichetta e valore sono associati (`dl`/`dt`/`dd`) in ogni lettura, come gia' in «Task
// per stato»: una tecnologia assistiva legge «Numero sprint: 95», non due paragrafi
// vicini. L'eta' non sta qui: un riquadro ne ha una sola, nell'intestazione.
function renderLettura(lettura) {
  const blocco = elemento('div', null, 'lettura');
  const dl = elemento('dl', null, 'misura');
  const dd = elemento('dd');
  dl.append(elemento('dt', lettura.label, 'etichetta'), dd);
  blocco.append(dl);

  if (!lettura.available) {
    dd.append(elemento('p', 'non osservabile', 'valore'));
    dd.append(elemento('p', lettura.reason || 'ragione non dichiarata', 'ragione'));
    return blocco;
  }

  dd.append(renderValore(lettura));
  if (lettura.stale) dd.append(elemento('p', 'lettura stantia', 'eta'));
  return blocco;
}

function renderFonti(pannelli) {
  const assenti = [];
  const bozza = document.createElement('div');

  for (const pannello of pannelli) {
    const sezione = document.createElement('article');
    sezione.className = 'riquadro';
    sezione.setAttribute('aria-labelledby', `titolo-${pannello.key}`);

    const testa = elemento('div', null, 'riquadro-testa');
    const titolo = elemento('h3', pannello.titolo || pannello.key);
    titolo.id = `titolo-${pannello.key}`;
    const stato = statoFonte(pannello);
    const [classe, parola] = {
      ok: ['ok', 'osservabile'],
      stantio: ['stantio', 'dato stantio'],
      'in-lettura': ['attesa', 'in lettura'],
      assente: ['assente', 'non osservabile'],
    }[stato];
    testa.append(titolo, elemento('span', parola, `marcatore ${classe}`));
    if (stato === 'assente') assenti.push(pannello.titolo || pannello.key);

    // UNA sola eta' per riquadro, quella che dice se cio' che vedi e' ancora vero: se un
    // dato porta l'eta' della sua fonte (un file fermo da ore) e' quella; altrimenti e'
    // la lettura. «Letto 0 s fa» accanto a «dato di 15 min fa» faceva chiedere quale
    // delle due fosse l'aggiornamento.
    if (pannello.observable) {
      const datate = pannello.readings.filter((l) => l.available &&
        l.data_age_seconds !== null && l.data_age_seconds !== undefined && l.data_age_seconds > 90);
      const etaLettura = Math.min(...pannello.readings.map((l) => l.age_seconds));
      testa.append(datate.length
        ? elementoEta('dato aggiornato', Math.max(...datate.map((l) => l.data_age_seconds)))
        : elementoEta('letto', etaLettura));
    }
    sezione.append(testa);
    if (pannello.descrizione) sezione.append(elemento('p', pannello.descrizione, 'riquadro-nota'));
    // La fonte sta subito sotto il titolo e dice il FILE, non la cartella.
    sezione.append(elemento('p', `Fonte: ${pannello.source}`, 'fonte'));
    pannello.readings.forEach((l) => sezione.append(renderLettura(l)));
    bozza.append(sezione);
  }
  if (!pannelli.length) bozza.append(elemento('p', 'Nessuna fonte dichiarata.', 'attesa'));
  riconciliaFigli($('riquadri'), bozza);
  aggiornaScorrevoli();

  const firma = assenti.slice().sort().join(',');
  if (firma !== ultimeAssenti) {
    ultimeAssenti = firma;
    if (assenti.length) {
      annuncia(`Fonti non osservabili (${assenti.length}): ${assenti.join(', ')}.`, 'annuncio-fonti');
    }
  }
}

// Una regione e' un punto di Tab, un `region` con nome e un luogo con un segnale visivo
// SOLO quando il suo contenuto scorre. Si rimisura a ogni lettura e a ogni cambio di
// dimensione (zoom, rotazione).
let misurandoScorrevoli = false;
function aggiornaScorrevoli() {
  if (misurandoScorrevoli) return;  // tetto anti-ciclo: gli attributi scritti qui non devono rientrare
  misurandoScorrevoli = true;
  try { misuraScorrevoli(); } finally { misurandoScorrevoli = false; }
}

function misuraScorrevoli() {
  document.querySelectorAll('.scorrevole').forEach((el) => {
    const scorre = el.scrollWidth > el.clientWidth + 1 || el.scrollHeight > el.clientHeight + 1;
    if (scorre) {
      if (el.getAttribute('tabindex') !== '0') el.setAttribute('tabindex', '0');
      el.setAttribute('role', 'region');
      el.setAttribute('aria-label', `${el.dataset.etichetta} (tabella che scorre)`);
      el.dataset.scorre = 'true';
    } else {
      el.removeAttribute('tabindex');
      el.removeAttribute('role');
      el.removeAttribute('aria-label');
      el.removeAttribute('data-scorre');
    }
  });
}
window.addEventListener('resize', aggiornaScorrevoli);
// `toggle` non risale: serve la cattura. Dentro un <details> chiuso le misure valgono 0,
// quindi all'apertura la regione va rimisurata subito, non al ciclo dopo.
document.addEventListener('toggle', aggiornaScorrevoli, true);

// ── Ciclo ──────────────────────────────────────────────────────────────

function segnaStantio(motivo) {
  const banner = $('dati-stantii');
  const quando = ricevutoMs !== null
    ? `dell'ultima lettura riuscita (${eta((Date.now() - ricevutoMs) / 1000)})`
    : 'non ancora letti';
  const frase = `${motivo} I dati mostrati sono ${quando} e potrebbero non essere aggiornati. ` +
                `Riprovo da solo ogni ${INTERVALLO_MS / 1000} s.`;
  banner.textContent = frase;
  banner.hidden = false;
  if (ricevutoMs !== null) {
    $('aggiornamento').dataset.prefisso = 'Aggiornamento non riuscito. Ultima lettura riuscita';
    ticchettio();
  } else {
    $('aggiornamento').removeAttribute('data-eta-base');
    $('aggiornamento').textContent = 'Aggiornamento non riuscito.';
  }
  document.querySelectorAll('.riquadro .marcatore').forEach((m) => {
    m.textContent = 'dato stantio';
    m.className = 'marcatore stantio';
  });
  document.querySelectorAll('#turno, #riquadri').forEach((e) => e.setAttribute('data-stantio', 'true'));
  if (!staleAttivo) annuncia(frase, 'annuncio-fonti');
  staleAttivo = true;
}

function segnaRecupero() {
  if (!staleAttivo) return;
  staleAttivo = false;
  $('dati-stantii').hidden = true;
  document.querySelectorAll('[data-stantio]').forEach((e) => e.removeAttribute('data-stantio'));
  annuncia('Collegamento ripristinato: i dati sono di nuovo aggiornati.', 'annuncio-fonti');
}

async function aggiorna() {
  let stato;
  try {
    const risposta = await fetch('/api/state', { cache: 'no-store' });
    if (!risposta.ok) {
      const e = new ErroreDiComunicazione('servizio', risposta.status);
      throw e;
    }
    stato = await risposta.json();
  } catch (problema) {
    // «Il servizio non risponde» e «la resa e' rotta» sono due guasti con due rimedi: la
    // frase dice quale, il dettaglio tecnico va in console, non davanti a chi legge.
    console.error('[plancia]', problema);
    if (problema instanceof ErroreDiComunicazione) {
      segnaStantio(`Il servizio ha risposto con un errore (${problema.codice}).`);
    } else {
      segnaStantio('Non riesco a raggiungere la plancia: controlla la connessione.');
    }
    return;
  }
  try {
    ricevutoMs = Date.now();
    segnaRecupero();
    renderTestata(stato);
    renderTurno(stato.turn, stato.scrittura.turno_in_corso);
    renderComandi(stato.scrittura, stato.concorrenza);
    renderVoce(stato.voce);
    renderFonti(stato.panels);
    $('aggiornamento').dataset.prefisso = 'Ultima lettura riuscita';
    $('aggiornamento').dataset.etaBase = '0';
    $('aggiornamento').textContent = `Ultima lettura riuscita ${eta(0)}`;
  } catch (problema) {
    console.error('[plancia]', problema);
    segnaStantio('La pagina non riesce a mostrare i dati ricevuti: ricaricala; se capita ancora, segnalalo.');
  }
}

// ── Comandi dell'interfaccia ───────────────────────────────────────────

$('conferma-si').addEventListener('click', () => {
  if (!inSospeso) return;
  const azione = inSospeso;
  nascondiConferma();
  esegui(azione, true);
});
$('conferma-no').addEventListener('click', annullaConferma);

// Escape chiude, Tab non esce: `inert` sul resto della pagina fa gia' il grosso, ma un
// browser senza `inert` o un'estensione che lo ignora non deve poter portare il fuoco fuori.
document.addEventListener('keydown', (evento) => {
  if ($('conferma').hidden) return;
  if (evento.key === 'Escape') {
    evento.preventDefault();
    annullaConferma();
    return;
  }
  if (evento.key !== 'Tab') return;
  const comandi = [...$('conferma').querySelectorAll('button')];
  const primo = comandi[0];
  const ultimo = comandi[comandi.length - 1];
  const dentro = comandi.includes(document.activeElement);
  if (evento.shiftKey && (document.activeElement === primo || !dentro)) {
    evento.preventDefault(); ultimo.focus();
  } else if (!evento.shiftKey && (document.activeElement === ultimo || !dentro)) {
    evento.preventDefault(); primo.focus();
  }
});

// Un solo ascoltatore sul contenitore: i pulsanti sono riconciliati e non ricreati,
// quindi un ascoltatore per pulsante resterebbe legato all'azione di quando e' nato.
$('azioni').addEventListener('click', (evento) => {
  const b = evento.target.closest('button[data-direttiva]');
  if (!b) return;
  const azione = azioniCorrenti.get(b.dataset.direttiva);
  if (!azione) return;
  if (b.getAttribute('aria-disabled') === 'true') {
    esito($('scrittura-stato').textContent);
    return;
  }
  innesco = b;
  esegui(azione, false);
});

// Lo skip link sposta il fuoco davvero: l'ancora da sola scorre la pagina ma lascia il
// fuoco dov'era, e il Tab successivo riparte dall'inizio.
document.querySelector('.salta').addEventListener('click', (evento) => {
  evento.preventDefault();
  $('contenuto').focus();
});

function erroreRisposta(messaggio) {
  const campo = $('risposta-testo');
  const nota = $('risposta-errore');
  if (messaggio) {
    campo.setAttribute('aria-invalid', 'true');
    nota.hidden = false;
    nota.textContent = messaggio;
  } else {
    campo.removeAttribute('aria-invalid');
    nota.hidden = true;
    nota.textContent = '';
  }
}
$('risposta-testo').addEventListener('input', () => erroreRisposta(null));

$('risposta').addEventListener('submit', async (evento) => {
  evento.preventDefault();
  const campo = $('risposta-testo');
  if (!campo.value.trim()) {
    erroreRisposta('Scrivi una risposta prima di inviarla: il campo è vuoto.');
    campo.focus();
    return;
  }
  erroreRisposta(null);
  let risposta;
  try {
    risposta = await chiama('/api/rispondi', { testo: campo.value.trim() });
  } catch (problema) {
    // Il testo resta nel campo: un errore di rete non deve costare la risposta scritta.
    esito(fraseErrore(problema, 'la risposta'), true);
    return;
  }
  campo.value = '';
  const ok = risposta.esito.stato === 'avviato';
  esito(ok ? 'Risposta inviata. La nuova risposta della factory comparirà in «Lavoro in corso».'
           : `Risposta rifiutata: ${risposta.esito.ragione || risposta.esito.stato}`, !ok);
  // Il modulo sparisce mentre la factory lavora: il fuoco va dove comparira' il risultato.
  appenaAvviato = ok;
  $('t-turno').focus();
  aggiorna();
});

$('voce-toggle').addEventListener('click', async () => {
  // `evento.currentTarget` e' `null` dopo il primo `await`: la propagazione dell'evento
  // e' gia' finita quando la promessa si risolve. Il riferimento va preso PRIMA.
  const bottone = $('voce-toggle');
  if (bottone.getAttribute('aria-disabled') === 'true') {
    // Non succede nulla, e lo si dice: il motivo e' la nota collegata come descrizione.
    annuncia($('voce-stato').textContent);
    return;
  }
  const attiva = bottone.getAttribute('aria-pressed') !== 'true';
  voceInVolo = true;
  bottone.setAttribute('aria-disabled', 'true');
  let risposta;
  try {
    risposta = await chiama('/api/voce', { attiva });
  } catch (problema) {
    esito(fraseErrore(problema, 'il cambio del canale vocale'), true);
    return;
  } finally {
    voceInVolo = false;
    bottone.removeAttribute('aria-disabled');
  }
  const esitoVoce = risposta.esito;
  renderVoce(esitoVoce);
  annuncia(esitoVoce.attivo
    ? 'Canale vocale attivo.'
    : (esitoVoce.disponibile ? 'Canale vocale disattivato.' : `Canale vocale non disponibile: ${esitoVoce.ragione}`));
});

$('mascotte-toggle').addEventListener('click', (evento) => {
  const accesa = !Mascotte.attiva();
  Mascotte.imposta(accesa);
  interruttore(evento.currentTarget, 'Mascotte', accesa, 'visibile', 'nascosta');
  // Si applica SUBITO, senza aspettare il prossimo `aggiorna()`. Prima l'effetto arrivava
  // solo col fetch successivo: lo stato della mascotte e' locale al browser e non ha
  // niente da chiedere al server, ma il codice lo trattava come se lo avesse. Con cinque
  // collettori quel fetch e' abbastanza lento da far sembrare il comando rotto — e un
  // comando che sembra rotto viene premuto due volte.
  $('mascotte').hidden = !accesa;
  annuncia(accesa ? 'Mascotte mostrata.' : 'Mascotte nascosta. Nessuna informazione è andata persa.');
  aggiorna();
});
interruttore($('mascotte-toggle'), 'Mascotte', Mascotte.attiva(), 'visibile', 'nascosta');

$('ricarica').addEventListener('click', aggiorna);

// L'indice porta DAVVERO il fuoco sulla sezione: l'ancora da sola scorre ma lascia il
// fuoco dov'era, e il Tab successivo riparte da la'.
document.querySelectorAll('.indice a').forEach((link) => {
  link.addEventListener('click', (evento) => {
    const sezione = document.querySelector(link.getAttribute('href'));
    if (!sezione) return;
    evento.preventDefault();
    sezione.focus();
  });
});

setInterval(ticchettio, 1000);

aggiorna();
setInterval(aggiorna, INTERVALLO_MS);

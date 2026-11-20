// Pannello «Dipendenze» (stadio 2 del grafo della conoscenza). Nessuna dipendenza, nessun build.
//
// Caricato dal server SOLO a capability accesa. Tre regole:
//   1. Solo GET su /api/grafo/*: la plancia non e' uno scrittore.
//   2. Una costruzione fallita e' «non osservabile» con il motivo, mai una tabella vuota
//      che si legge come «nessuna dipendenza».
//   3. La tabella e' il canale primario; ogni etichetta e' testo, non solo tooltip o colore.
'use strict';

const COLONNE = ['Nodo', 'Tipo', 'Passo', 'Provenienza', 'Risoluzione'];
const NOTA_FONTE = "il file esiste; non verifica che la pagina dica cio' che la fonte dice";
const $ = (id) => document.getElementById(id);

// Solo la richiesta piu' recente puo' scrivere nel pannello: ogni azione prende un numero di
// generazione e, dopo ogni await, lo confronta. Una risposta in ritardo si scarta.
let generazione = 0;
const aggiornata = (mia) => mia === generazione;
const SPENTO = 'Il grafo della conoscenza è spento (grafo_conoscenza.enabled): ricarica la pagina.';

function el(tag, testo, attrs) {
  const nodo = document.createElement(tag);
  if (testo !== undefined && testo !== null) nodo.textContent = String(testo);
  for (const [k, v] of Object.entries(attrs || {})) nodo.setAttribute(k, v);
  return nodo;
}

async function chiedi(percorso, parametri) {
  const risposta = await fetch(`${percorso}?${new URLSearchParams(parametri)}`, { method: 'GET' });
  let corpo = null;
  try { corpo = await risposta.json(); } catch (_) { /* corpo non JSON */ }
  return { stato: risposta.status, corpo };
}

function costruisciSezione() {
  const sezione = el('section', null, { class: 'sezione', 'aria-labelledby': 't-grafo' });
  const testa = el('div', null, { class: 'sezione-testa' });
  testa.append(el('h2', 'Dipendenze', { id: 't-grafo', tabindex: '-1' }),
    el('p', 'Chi dipende da un nodo della wiki o del kanban, e cosa cita. Solo lettura: il grafo si ' +
      'ricostruisce in memoria, non scrive nulla.', { class: 'sezione-nota' }));
  const form = el('form', null, { class: 'grafo-form', id: 'grafo-form', role: 'search' });
  const campo = el('div');
  campo.append(el('label', 'Nodo (titolo, percorso o id kanban)', { for: 'grafo-q' }),
    el('input', null, { type: 'search', id: 'grafo-q', name: 'q', autocomplete: 'off' }));
  const passi = el('div');
  const scelta = el('select', null, { id: 'grafo-hop', name: 'hop' });
  scelta.append(el('option', '1 passo', { value: '1' }), el('option', '2 passi', { value: '2' }));
  passi.append(el('label', 'Profondità', { for: 'grafo-hop' }), scelta);
  form.append(campo, passi, el('button', 'Cerca', { type: 'submit' }));
  sezione.append(testa, form,
    el('p', null, { id: 'grafo-stato', class: 'grafo-nota', role: 'status', 'aria-live': 'polite' }),
    el('ul', null, { id: 'grafo-esiti', class: 'grafo-esiti', 'aria-label': 'Nodi trovati' }),
    el('div', null, { id: 'grafo-nodo' }));
  return sezione;
}

function nonOsservabile(corpo) {
  const box = el('p', `Non osservabile: ${corpo.ragione || 'motivo non dichiarato'}. ` +
    'Nessuna tabella: l\'assenza di righe qui non vuol dire «nessuna dipendenza».',
    { class: 'grafo-non-osservabile', role: 'alert' });
  return box;
}

function celleNodo(riga, scegli) {
  const td = el('td');
  const bottone = el('button', riga.titolo, { type: 'button', 'data-id': riga.id });
  if (riga.tipo === 'fuori dal grafo') bottone.disabled = true;
  else bottone.addEventListener('click', () => scegli(riga.id));
  td.append(bottone, el('span', riga.id, { class: 'path' }));
  return td;
}

function celleRisoluzione(riga) {
  const td = el('td', riga.risoluzione_testo);
  if (riga.resolution === 'resolved') td.append(el('span', NOTA_FONTE, { class: 'nota' }));
  if (riga.area) {
    td.append(el('span', `area: ${riga.area} · status: ${riga.status_citante} · a chi spetta: ${riga.a_chi_spetta}`,
      { class: 'nota' }));
  }
  return td;
}

function tabella(titolo, righe, scegli) {
  const wrap = el('div', null, { class: 'scorrevole' });
  const t = el('table', null, { class: 'grafo-tabella' });
  t.append(el('caption', `${titolo} (${righe.length})`));
  const testa = el('tr');
  for (const c of COLONNE) testa.append(el('th', c, { scope: 'col' }));
  const intestazione = el('thead'); intestazione.append(testa); t.append(intestazione);
  const corpo = el('tbody');
  if (!righe.length) {
    const r = el('tr'); r.append(el('td', 'Nessuna riga: il grafo è stato letto e non ci sono archi di questo tipo.',
      { colspan: String(COLONNE.length) }));
    corpo.append(r);
  }
  for (const riga of righe) {
    const r = el('tr');
    r.append(celleNodo(riga, scegli),
      el('td', riga.sottotipo ? `${riga.tipo} · ${riga.sottotipo}` : riga.tipo),
      el('td', riga.passo === 2 && riga.via_nodo ? `2 (via ${riga.via_nodo})` : riga.passo),
      el('td', riga.origin), celleRisoluzione(riga));
    corpo.append(r);
  }
  t.append(corpo); wrap.append(t);
  return wrap;
}

function conteggi(titolo, c) {
  const ul = el('ul', null, { class: 'grafo-conteggi', 'aria-label': `Conteggi: ${titolo}` });
  ul.append(el('li', `${titolo}: ${c.totale}`));
  for (const [k, n] of Object.entries(c.per_origin)) ul.append(el('li', `${k}: ${n}`));
  for (const [k, n] of Object.entries(c.per_resolution)) ul.append(el('li', `${k}: ${n}`));
  return ul;
}

async function mostraNodo(ident) {
  const mia = ++generazione;
  const dove = $('grafo-nodo'), stato = $('grafo-stato');
  const hop = $('grafo-hop').value;
  stato.textContent = 'Lettura del grafo in corso…';
  dove.replaceChildren();
  let r;
  try { r = await chiedi('/api/grafo/nodo', { id: ident, hop }); }
  catch (problema) {
    if (!aggiornata(mia)) return;
    stato.textContent = ''; dove.append(nonOsservabile({ ragione: String(problema) })); return;
  }
  if (!aggiornata(mia)) return;
  const c = r.corpo || {};
  if (c.osservabile === false) { stato.textContent = ''; dove.append(nonOsservabile(c)); return; }
  if (c.nodo_trovato === false) {
    stato.textContent = `Nodo «${ident}» non presente nel grafo.`; return;
  }
  if (r.stato === 404) { stato.textContent = ''; dove.append(nonOsservabile({ ragione: SPENTO })); return; }
  if (r.stato !== 200) { stato.textContent = ''; dove.append(nonOsservabile({ ragione: c.errore || `HTTP ${r.stato}` })); return; }
  const eta = `fonte: ${c.fonte} · letto ${Math.round(c.letto_da_s)} s fa · costruito in ${c.costruito_in_s} s`;
  stato.textContent = eta;
  const testa = el('div', null, { class: 'grafo-testata' });
  testa.append(el('h3', c.nodo.titolo), el('p', `${c.nodo.id} · ${c.nodo.tipo}` +
    (c.nodo.sottotipo ? ` · ${c.nodo.sottotipo}` : '') + (c.nodo.status ? ` · status: ${c.nodo.status}` : ''),
    { class: 'grafo-nota' }),
    conteggi('Chi dipende da questo nodo', c.conteggi.in_ingresso),
    conteggi('Cosa cita', c.conteggi.in_uscita),
    el('p', `«fonte trovata»: ${NOTA_FONTE}.`, { class: 'grafo-nota' }));
  dove.append(testa, tabella('Chi dipende da questo nodo', c.in_ingresso, mostraNodo),
    tabella('Cosa cita', c.in_uscita, mostraNodo));
  $('grafo-q').value = c.nodo.id;
}

async function cerca(evento) {
  evento.preventDefault();
  const q = $('grafo-q').value.trim();
  const mia = ++generazione;
  const esiti = $('grafo-esiti'), stato = $('grafo-stato');
  esiti.replaceChildren(); $('grafo-nodo').replaceChildren();
  if (!q) { stato.textContent = 'Scrivi un titolo, un percorso o un id.'; return; }
  stato.textContent = 'Ricerca in corso…';
  let r;
  try { r = await chiedi('/api/grafo/cerca', { q }); }
  catch (problema) {
    if (!aggiornata(mia)) return;
    stato.textContent = ''; $('grafo-nodo').append(nonOsservabile({ ragione: String(problema) })); return;
  }
  if (!aggiornata(mia)) return;
  const c = r.corpo || {};
  if (c.osservabile === false) { stato.textContent = ''; $('grafo-nodo').append(nonOsservabile(c)); return; }
  if (r.stato === 404 && !c.risultati) { stato.textContent = ''; $('grafo-nodo').append(nonOsservabile({ ragione: SPENTO })); return; }
  const trovati = c.risultati || [];
  stato.textContent = trovati.length
    ? `${c.totale} nodi trovati${c.troncato ? `, mostrati i primi ${trovati.length}` : ''}.`
    : 'Nessun nodo trovato per questa ricerca.';
  for (const n of trovati) {
    const li = el('li');
    li.append(el('button', `${n.titolo} — ${n.id}`, { type: 'button' }));
    li.firstChild.addEventListener('click', () => mostraNodo(n.id));
    esiti.append(li);
  }
}

function avvia() {
  const glossario = $('t-glossario') && $('t-glossario').closest('section');
  const sezione = costruisciSezione();
  if (glossario) glossario.before(sezione); else document.querySelector('main').append(sezione);
  const lista = document.querySelector('nav.indice ul');
  if (lista) {
    const voce = el('li'); voce.append(el('a', 'Dipendenze', { href: '#t-grafo' }));
    const g = lista.lastElementChild; if (g) g.before(voce); else lista.append(voce);
  }
  $('grafo-form').addEventListener('submit', cerca);
  $('grafo-hop').addEventListener('change', () => {
    const q = $('grafo-q').value.trim();
    if ($('grafo-nodo').childElementCount && q) mostraNodo(q);
  });
}

// Collegamento diretto a un nodo: `/#grafo=<id>[&hop=2]`.
function nodoDaIndirizzo() {
  const m = /^#grafo=([^&]+)(?:&hop=([12]))?$/.exec(location.hash);
  if (!m) return;
  let ident;
  try { ident = decodeURIComponent(m[1]); }
  catch (_) { $('grafo-stato').textContent = 'Indirizzo non valido: il nodo nell\'hash non è codificato correttamente.'; return; }
  if (m[2]) $('grafo-hop').value = m[2];
  $('grafo-q').value = ident;
  mostraNodo(ident);
}

avvia();
nodoDaIndirizzo();

/**
 * difetti-simulazione.mjs — riproduce, in un browser vero, le difficolta' emerse dalla
 * simulazione con tecnologie assistive e dice per ciascuna se si presenta ancora.
 *
 * Una simulazione non e' una validazione: questo script verifica che le difficolta'
 * trovate non si ripresentino, non che la plancia sia accessibile.
 *
 * Premere i comandi avvia un lavoro: l'URL DEVE essere quello di una plancia con il
 * runtime finto (`python tests/visual/lanciatore_finto.py <porta>`), mai una col runtime vero.
 *
 * Uso:  node tools/a11y/difetti-simulazione.mjs <url>
 *       (Playwright: modulo `playwright` risolvibile, oppure A11Y_PLAYWRIGHT_DIR =
 *        cartella che contiene node_modules/playwright)
 * Stampa un JSON {esiti:[{id, tsk, passed, detail}]}; esce 0 sempre.
 */
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

let chromium;
try { ({ chromium } = await import('playwright')); }
catch {
  const base = process.env.A11Y_PLAYWRIGHT_DIR;
  if (!base) { console.error('playwright non risolvibile: imposta A11Y_PLAYWRIGHT_DIR'); process.exit(2); }
  ({ chromium } = await import(pathToFileURL(resolve(base, 'node_modules/playwright/index.mjs')).href));
}

const url = process.argv[2];
if (!url) { console.error('uso: node difetti-simulazione.mjs <url>'); process.exit(2); }

const esiti = [];
const prova = (tsk, id, passed, detail) => esiti.push({ tsk, id, passed: !!passed, detail });
const attendi = (ms) => new Promise((r) => setTimeout(r, ms));

const browser = await chromium.launch();

async function nuovaPagina(opzioni = {}) {
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 }, ...opzioni });
  const page = await ctx.newPage();
  // Registra ogni testo che compare in una regione live, con l'istante.
  await page.addInitScript(() => {
    window.__annunci = [];
    const t0 = performance.now();
    const viva = (n) => n && n.closest && n.closest('[aria-live],[role=status],[role=log],[role=alert]');
    new MutationObserver((muts) => {
      for (const m of muts) {
        const regione = viva(m.target.nodeType === 3 ? m.target.parentElement : m.target);
        if (!regione) continue;
        const testo = (regione.textContent || '').trim();
        if (testo) window.__annunci.push({ t: Math.round(performance.now() - t0), id: regione.id, testo });
      }
    }).observe(document, { subtree: true, childList: true, characterData: true });
  });
  await page.goto(url, { waitUntil: 'load' });
  await page.waitForSelector('.riquadro', { timeout: 15000 });
  await page.waitForSelector('#azioni button');
  return page;
}

async function turnoLibero() {
  for (let i = 0; i < 40; i++) {
    const s = await (await fetch(new URL('/api/state', url))).json();
    if (!s.scrittura.turno_in_corso) return;
    await attendi(500);
  }
}

// «Pronti» per la pagina, non per il server: la pagina lo sa al prossimo aggiornamento.
// `aria-disabled` e `disabled` sono entrambi «non premibile».
const pronti = (page) => page.waitForFunction(() =>
  [...document.querySelectorAll('#azioni button')].every((b) =>
    !b.disabled && b.getAttribute('aria-disabled') !== 'true'), null, { timeout: 12000 });

const attivo = (page) => page.evaluate(() => {
  const a = document.activeElement;
  return { tag: a.tagName, id: a.id, testo: (a.textContent || '').trim().slice(0, 40), body: a === document.body };
});
const bottone = (page, nome) => page.locator('#azioni button', { hasText: nome }).first();
const regioniVisibili = (page) => page.evaluate(() =>
  [...document.querySelectorAll('[aria-live],[role=status],[role=log],[role=alert]')]
    .filter((e) => { const r = e.getBoundingClientRect(); return r.width > 20 && r.height > 8 && !e.closest('[hidden]'); })
    .map((e) => ({ id: e.id, testo: e.textContent.trim() })));

// ── TSK-962 — fine del turno ed esito visibili accanto al comando ───────────
{
  const page = await nuovaPagina();
  await bottone(page, 'Controllo di salute').click();
  await attendi(2500);
  const dopoAvvio = await regioniVisibili(page);
  prova('TSK-962', 'avvio-visibile-dopo-2s', dopoAvvio.some((r) => /Avviato/.test(r.testo)),
    { regioni_visibili: dopoAvvio });
  await page.waitForFunction(() => window.__annunci.some((a) => /concluso/i.test(a.testo)), null, { timeout: 9000 }).catch(() => {});
  await attendi(500);
  const fine = await regioniVisibili(page);
  const annunci = await page.evaluate(() => window.__annunci);
  prova('TSK-962', 'fine-turno-visibile', fine.some((r) => /conclus/i.test(r.testo)), { regioni_visibili: fine });
  prova('TSK-962', 'nessun-valore-interno-negli-annunci',
    !annunci.some((a) => /Stato della factory: (concluso|in-lavorazione|inattivo)/.test(a.testo)),
    { annunci: annunci.map((a) => a.testo).slice(-6) });
  prova('TSK-962', 'fine-turno-nel-contesto-del-comando',
    await page.evaluate(() => {
      const regione = [...document.querySelectorAll('[aria-live],[role=status],[role=log]')]
        .find((e) => /conclus/i.test(e.textContent));
      const sezione = document.getElementById('t-comandi')?.closest('section');
      return !!(regione && sezione && sezione.contains(regione));
    }), {});
  await page.context().close();
  await turnoLibero();
}

// ── TSK-963 — il poll non ricrea pulsanti e regioni ─────────────────────────
{
  const page = await nuovaPagina();
  await bottone(page, 'Stato del progetto').focus();
  await page.evaluate(() => { window.__nodo = document.activeElement; });
  await attendi(6500);
  const dopo = await page.evaluate(() => ({ stessa: document.activeElement === window.__nodo,
                                            body: document.activeElement === document.body }));
  prova('TSK-963', 'focus-sul-comando-dopo-un-poll', dopo.stessa && !dopo.body, dopo);

  await page.context().close();
}
{
  // Una regione a scorrimento e' un punto di Tab solo se scorre: a 480 px le tabelle del
  // coordinamento sono piu' larghe del riquadro.
  const stretta = await nuovaPagina({ viewport: { width: 480, height: 900 } });
  const regione = stretta.locator('.scorrevole[tabindex="0"]').first();
  await regione.waitFor({ timeout: 15000 }).catch(() => {});
  if (await regione.count()) {
    await regione.focus();
    await stretta.evaluate(() => { window.__reg = document.activeElement; });
    await attendi(6500);
    const r = await stretta.evaluate(() => ({ stessa: document.activeElement === window.__reg }));
    prova('TSK-963', 'focus-su-regione-dopo-un-poll', r.stessa, r);
  } else {
    prova('TSK-963', 'focus-su-regione-dopo-un-poll', false, { errore: 'nessuna regione scorrevole nel fixture' });
  }
  await stretta.context().close();
}

// ── TSK-964 — focus definito dopo Avvia, Annulla, Invia, skip link ──────────
{
  const page = await nuovaPagina();
  await page.keyboard.press('Tab');
  await page.keyboard.press('Enter');
  const salta = await attivo(page);
  prova('TSK-964', 'dopo-skip-link', !salta.body, salta);

  await bottone(page, 'Controllo di salute').focus();
  await page.keyboard.press('Enter');
  await attendi(700);
  const avvia = await attivo(page);
  prova('TSK-964', 'dopo-avvia', !avvia.body, avvia);
  await page.waitForSelector('#risposta:not([hidden])', { timeout: 12000 });
  await turnoLibero();
  await pronti(page);

  await bottone(page, 'Promuovi una pagina').focus();
  await page.keyboard.press('Enter');
  await page.waitForSelector('#conferma:not([hidden])');
  await page.locator('#conferma-no').click();
  await attendi(300);
  const annulla = await attivo(page);
  prova('TSK-964', 'dopo-annulla-torna-al-comando', /Promuovi/.test(annulla.testo), annulla);

  await page.fill('#risposta-testo', 'si');
  await page.locator('#risposta button[type=submit]').focus();
  await page.keyboard.press('Enter');
  await attendi(500);
  const invia = await attivo(page);
  prova('TSK-964', 'dopo-invia', !invia.body, invia);
  await turnoLibero();
  await page.context().close();
}

// ── TSK-965 — dialogo di conferma ───────────────────────────────────────────
{
  const page = await nuovaPagina();
  await bottone(page, 'Promuovi una pagina').click();           // aperto col CLICK
  await page.waitForSelector('#conferma:not([hidden])');
  await attendi(300);
  const dlg = await page.evaluate(() => {
    const d = document.getElementById('conferma');
    const a = document.activeElement;
    const stile = getComputedStyle(a);
    return {
      modale: d.getAttribute('aria-modal'),
      focus: (a.textContent || '').trim(),
      anello: stile.outlineStyle !== 'none' && parseFloat(stile.outlineWidth) > 0,
      sfondo_inert: ['main', 'header', 'footer'].every((s) => document.querySelector(s)?.inert === true),
      testo: document.getElementById('conferma-testo').textContent,
      titolo: document.getElementById('conferma-titolo').textContent,
      nomi: [...d.querySelectorAll('button')].map((b) => b.getAttribute('aria-label') || b.textContent.trim()),
    };
  });
  prova('TSK-965', 'aria-modal-true', dlg.modale === 'true', dlg);
  prova('TSK-965', 'sfondo-inert', dlg.sfondo_inert, dlg);
  prova('TSK-965', 'focus-iniziale-su-annulla', /^Annulla/.test(dlg.focus), dlg);
  prova('TSK-965', 'anello-visibile-aperto-col-click', dlg.anello, dlg);
  prova('TSK-965', 'conseguenza-nomina-lo-oggetto', /Promuovi una pagina/.test(dlg.testo + ' ' + dlg.titolo), dlg);
  prova('TSK-965', 'pulsanti-con-oggetto', dlg.nomi.every((n) => /Promuovi una pagina/.test(n)), dlg);

  const lette = await page.evaluate(() => window.__annunci.filter((a) => /status/.test(a.testo)).length);
  prova('TSK-965', 'conseguenza-non-ripetuta-in-regione-live', lette === 0, { annunci_con_conseguenza: lette });

  const dentro = [];
  for (let i = 0; i < 5; i++) {
    await page.keyboard.press('Tab');
    dentro.push(await page.evaluate(() => !!document.activeElement.closest('#conferma')));
  }
  prova('TSK-965', 'tab-resta-nel-dialogo', dentro.every(Boolean), { dentro });
  await page.keyboard.press('Shift+Tab');
  prova('TSK-965', 'shift-tab-resta-nel-dialogo',
    await page.evaluate(() => !!document.activeElement.closest('#conferma')), {});

  await page.keyboard.press('Escape');
  await attendi(300);
  const esc = await page.evaluate(() => ({ chiuso: document.getElementById('conferma').hidden,
                                           focus: (document.activeElement.textContent || '').trim(),
                                           inert: document.querySelector('main').inert }));
  prova('TSK-965', 'escape-chiude-e-riporta-al-comando',
    esc.chiuso && /Promuovi/.test(esc.focus) && !esc.inert, esc);
  await page.context().close();

  // zoom 400%: 1280 px -> 320 px di larghezza CSS, 900 -> 225 di altezza
  const z = await nuovaPagina({ viewport: { width: 320, height: 225 } });
  await bottone(z, 'Promuovi una pagina').click();
  await z.waitForSelector('#conferma:not([hidden])');
  await attendi(300);
  const r = await z.evaluate(() => {
    const dentro = (el) => { const b = el.getBoundingClientRect();
      return b.top >= 0 && b.left >= 0 && b.bottom <= innerHeight && b.right <= innerWidth; };
    return { titolo: dentro(document.getElementById('conferma-titolo')),
             testo: dentro(document.getElementById('conferma-testo')) &&
             document.getElementById('conferma-testo').scrollHeight <= document.getElementById('conferma-testo').clientHeight,
             annulla: dentro(document.getElementById('conferma-no')),
             pagina_scorre_oltre: document.documentElement.scrollWidth > innerWidth };
  });
  prova('TSK-965', 'zoom-400-titolo-e-conseguenza-visibili', r.titolo && r.testo && r.annulla, r);
  await z.context().close();
}

// ── TSK-966 — rete caduta ed errori del servizio ────────────────────────────
{
  const page = await nuovaPagina();
  await page.route('**/api/invia', (r) => r.abort());
  await bottone(page, 'Controllo di salute').click();
  await attendi(800);
  const vis = await regioniVisibili(page);
  const corpo = await page.evaluate(() => document.body.innerText);
  prova('TSK-966', 'rete-caduta-su-comando-messaggio',
    vis.some((r) => /raggiung|connession|rete/i.test(r.testo)) && /non (e'|è) partit|potrebbe non|non avviat/i.test(corpo),
    { regioni_visibili: vis });
  await page.unroute('**/api/invia');
  await page.context().close();
}
{
  const page = await nuovaPagina();
  await page.route('**/api/state', (r) => r.fulfill({ status: 500, body: 'boom' }));
  await page.locator('#ricarica').click();
  await attendi(800);
  const t = await page.evaluate(() => ({
    agg: document.getElementById('dati-stantii')?.textContent ?? document.getElementById('aggiornamento').textContent,
    corpo: document.body.innerText,
    marcatori: [...document.querySelectorAll('.riquadro .marcatore')].map((m) => m.textContent),
  }));
  prova('TSK-966', 'errore-servizio-messaggio-comprensibile',
    !/Error:|TypeError|SyntaxError/.test(t.agg) && /servizio/i.test(t.agg), t);
  prova('TSK-966', 'dati-marcati-stantii',
    /non aggiornat|stantii|potrebbero non/i.test(t.corpo) && t.marcatori.length > 0 && t.marcatori.every((m) => /stantio/.test(m)), t);
  await page.unroute('**/api/state');
  await page.locator('#ricarica').click();
  // La lettura dello stato interroga i collettori e puo' durare piu' di un secondo.
  await page.waitForFunction(() => window.__annunci.some((a) => /ripristinat/i.test(a.testo)),
    null, { timeout: 10000 }).catch(() => {});
  const annunci = await page.evaluate(() => window.__annunci.map((a) => a.testo));
  prova('TSK-966', 'recupero-annunciato', annunci.some((x) => /ripristinat|di nuovo|tornat/i.test(x)), { annunci: annunci.slice(-4) });
  await page.context().close();
}

// ── TSK-967 — risposta vuota ────────────────────────────────────────────────
{
  const page = await nuovaPagina();
  await bottone(page, 'Controllo di salute').click();
  await page.waitForSelector('#risposta:not([hidden])', { timeout: 12000 });
  await turnoLibero();
  const richieste = [];
  page.on('request', (r) => { if (r.url().includes('/api/rispondi')) richieste.push(r.url()); });
  await page.fill('#risposta-testo', '   ');
  await page.locator('#risposta button[type=submit]').click();
  await attendi(500);
  const s = await page.evaluate(() => {
    const c = document.getElementById('risposta-testo');
    const regioni = [...document.querySelectorAll('[role=alert],[aria-live],[role=status],[role=log]')]
      .map((e) => e.textContent.trim()).join(' | ');
    return { invalid: c.getAttribute('aria-invalid'), fuoco_sul_campo: document.activeElement === c, regioni };
  });
  prova('TSK-967', 'vuota-non-parte', richieste.length === 0, { richieste: richieste.length });
  prova('TSK-967', 'vuota-aria-invalid', s.invalid === 'true', s);
  prova('TSK-967', 'vuota-messaggio-annunciato', /scrivi|vuota|obbligator/i.test(s.regioni), s);
  prova('TSK-967', 'vuota-focus-sul-campo', s.fuoco_sul_campo, s);
  await page.context().close();
}

// ════════ Seconda ondata ════════════════════════════════════════════════════

const ETA = /\b\d+ (s|min|h) fa\b/;

// ── TSK-968 — stato ed eta' leggibili ───────────────────────────────────────
{
  const page = await nuovaPagina();
  await attendi(1500);          // i collettori lenti hanno risposto: i riquadri sono assestati
  const t = await page.evaluate(() => ({
    turno: document.getElementById('turno').innerText,
    agg: document.getElementById('aggiornamento').textContent,
    frase: document.getElementById('stato-frase').textContent,
    fonti: document.getElementById('stato-fonti')?.textContent ?? '',
    riquadri: [...document.querySelectorAll('.riquadro')].map((r) => ({
      titolo: r.querySelector('h3').textContent,
      osservabile: !r.querySelector('.marcatore.assente') && !r.querySelector('.marcatore.attesa'),
      eta: [...r.querySelectorAll('.eta')].map((e) => e.textContent).filter((x) => /\bfa\b/.test(x)),
    })),
    assenti: document.querySelectorAll('.marcatore.assente').length,
    annuncio: [...window.__annunci].reverse().find((a) => a.id === 'annuncio-fonti' && /non osservabil/.test(a.testo))?.testo ?? '',
  }));
  prova('TSK-968', 'eta-accanto-allo-stato-del-turno', ETA.test(t.turno), { turno: t.turno });
  prova('TSK-968', 'ultima-lettura-e-un-eta-non-un-orologio',
    ETA.test(t.agg) && !/\d{1,2}:\d{2}/.test(t.agg), { aggiornamento: t.agg });
  const male = t.riquadri.filter((r) => (r.osservabile && r.eta.length !== 1) || r.eta.length > 1);
  prova('TSK-968', 'una-sola-eta-per-riquadro', male.length === 0, { riquadri_fuori_regola: male });
  prova('TSK-968', 'frase-di-testata-parla-della-factory',
    t.frase.length > 8 && !/\bfont[ei]\b/i.test(t.frase), { frase: t.frase });
  const n = Number((t.fonti.match(/(\d+) non osservabil/) || [])[1] ?? 0);
  const nAnnuncio = Number((t.annuncio.match(/\((\d+)\)/) || [])[1] ?? 0);
  prova('TSK-968', 'fonti-contate-come-lo-status',
    /Fonti:/.test(t.fonti) && n === t.assenti && n === nAnnuncio,
    { riga: t.fonti, marcatori_assenti: t.assenti, annuncio: t.annuncio });
  await page.context().close();
}

// ── TSK-969 — riquadro Sprint ───────────────────────────────────────────────
{
  const page = await nuovaPagina();
  const file = readFileSync(resolve(import.meta.dirname, '../../management/kanban/sprint.md'), 'utf8');
  const atteso = (file.match(/^sprint_current:\s*(\d+)/m) || [])[1];
  const r = await page.evaluate(() => {
    const riquadro = document.querySelector('[aria-labelledby="titolo-sprint"]');
    const dt = [...riquadro.querySelectorAll('dt')].find((x) => /Numero sprint/.test(x.textContent));
    const fonte = riquadro.querySelector('.fonte');
    const prima = riquadro.querySelector('.lettura');
    return {
      valore: dt?.nextElementSibling?.tagName === 'DD' ? dt.nextElementSibling.textContent.trim() : null,
      fonte: fonte?.textContent ?? '',
      fonte_prima_delle_misure: !!(fonte && prima && (fonte.compareDocumentPosition(prima) & Node.DOCUMENT_POSITION_FOLLOWING)),
      letture_senza_dl: [...document.querySelectorAll('.lettura')].filter((l) => !l.querySelector('dl > dt + dd')).length,
    };
  });
  prova('TSK-969', 'valore-associato-all-etichetta-dt-dd', r.valore !== null && r.valore.startsWith(atteso ?? '?'),
    { dd: r.valore, atteso_da_sprint_md: atteso });
  prova('TSK-969', 'ogni-lettura-ha-dt-dd', r.letture_senza_dl === 0, { senza: r.letture_senza_dl });
  prova('TSK-969', 'fonte-cita-il-file', /management\/kanban\/sprint\.md/.test(r.fonte), { fonte: r.fonte });
  prova('TSK-969', 'fonte-vicina-al-titolo', r.fonte_prima_delle_misure ?? r.fonte_prima_delle_misure, r);
  await page.context().close();
}

// ── TSK-970 — navigazione per sezioni, regioni, tabelle tagliate ────────────
{
  const page = await nuovaPagina();
  const nav = await page.evaluate(() => {
    const n = document.querySelector('nav[aria-label]');
    const link = n ? [...n.querySelectorAll('a[href^="#"]')] : [];
    return { presente: !!n, link: link.map((a) => a.getAttribute('href')),
             h2: [...document.querySelectorAll('h2')].map((h) => '#' + h.id) };
  });
  prova('TSK-970', 'navigazione-per-sezioni',
    nav.presente && nav.h2.every((id) => nav.link.includes(id) || /glossario/.test(id)), nav);
  const fonti = page.locator('nav[aria-label] a', { hasText: 'Fonti' });
  if (await fonti.count()) {
    await fonti.click();
    await attendi(200);
    const dove = await page.evaluate(() => ({ id: document.activeElement.id,
      visibile: document.activeElement.getBoundingClientRect().top < innerHeight }));
    prova('TSK-970', 'il-link-porta-il-fuoco-sulla-sezione', dove.id === 't-fonti' && dove.visibile, dove);
  } else {
    prova('TSK-970', 'il-link-porta-il-fuoco-sulla-sezione', false, { errore: 'nessun link «Fonti»' });
  }
  const inutili = await page.evaluate(() => [...document.querySelectorAll('[tabindex="0"]')]
    .filter((e) => !/^(A|BUTTON|INPUT|SELECT|TEXTAREA)$/.test(e.tagName))
    .filter((e) => !(e.scrollWidth > e.clientWidth + 1 || e.scrollHeight > e.clientHeight + 1))
    .map((e) => e.getAttribute('aria-label') || e.tagName));
  prova('TSK-970', 'regioni-che-non-scorrono-non-sono-tab-stop', inutili.length === 0, { inutili });
  await page.context().close();

  const stretta = await nuovaPagina({ viewport: { width: 480, height: 900 } });
  await stretta.locator('.scorrevole[data-scorre="true"]').first().waitFor({ timeout: 15000 }).catch(() => {});
  const t = await stretta.evaluate(() => [...document.querySelectorAll('.scorrevole')]
    .filter((e) => e.scrollWidth > e.clientWidth + 1)
    .map((e) => { const st = getComputedStyle(e);
      return { nome: e.getAttribute('aria-label'), tabindex: e.getAttribute('tabindex'),
               segnale: e.dataset.scorre === 'true' && st.borderTopStyle === 'dashed' &&
                        st.backgroundImage !== 'none' }; }));
  prova('TSK-970', 'tabelle-tagliate-hanno-segnale-e-sono-raggiungibili',
    t.length > 0 && t.every((x) => x.segnale && x.tabindex === '0'), { tabelle: t });
  await stretta.context().close();
}

// ── TSK-971 — testo dell'interfaccia ────────────────────────────────────────
{
  const page = await nuovaPagina();
  await bottone(page, 'Controllo di salute').click();
  await page.waitForFunction(() => window.__annunci.some((a) => /concluso/i.test(a.testo)), null, { timeout: 12000 }).catch(() => {});
  const t = await page.evaluate(() => {
    const copia = document.body.cloneNode(true);
    copia.querySelectorAll('script,.scorrevole,.coppie,.azioni-turno,.glossario,#turno .valore + *').forEach((n) => n.remove());
    const testo = copia.textContent.replace(/\s+/g, ' ');
    const h = (sel) => [...document.querySelectorAll(sel)].map((x) => x.textContent.trim());
    const nomi = [...document.querySelectorAll('#azioni button')].map((b) => {
      const c = b.cloneNode(true); c.querySelectorAll('[aria-hidden="true"]').forEach((n) => n.remove());
      return { nome: (b.getAttribute('aria-label') || c.textContent).trim(), visibile: c.textContent.trim(),
               descritto_da: (b.getAttribute('aria-describedby') || '').split(' ').filter(Boolean)
                 .map((id) => document.getElementById(id)?.textContent ?? '').join(' ') };
    });
    return { testo, annunci: window.__annunci.map((a) => a.testo), titoli: h('h2,h3'),
             glossario: h('.glossario dt'), nomi };
  });
  const apostrofi = (x) => x.match(/[A-Za-z]'(?=[\s.,;:)»]|$)/g) || [];
  prova('TSK-971', 'accenti-veri-nel-testo-della-pagina', apostrofi(t.testo).length === 0,
    { trovati: apostrofi(t.testo).slice(0, 6), contesto: (t.testo.match(/.{20}[A-Za-z]'(?=[\s.,;:)»]|$)/g) || []).slice(0, 4) });
  prova('TSK-971', 'accenti-veri-negli-annunci', t.annunci.every((a) => apostrofi(a).length === 0),
    { annunci: t.annunci.filter((a) => apostrofi(a).length) });
  const gergo = ['turno', 'direttiva', 'runtime', 'transcript', 'claim', 'ciclo di push', 'dev-protocol', 'TSK']
    .filter((g) => new RegExp(`\\b${g}\\b`, g === 'TSK' ? '' : 'i').test(t.testo));
  prova('TSK-971', 'gergo-non-definito-fuori-dal-glossario', gergo.length === 0, { termini: gergo });
  prova('TSK-971', 'glossario-presente', t.glossario.length >= 5, { voci: t.glossario });
  prova('TSK-971', 'un-solo-nome-per-i-comandi',
    t.titoli.filter((x) => /^Comandi$/.test(x)).length === 1 && !t.titoli.some((x) => /Avvia lavoro|direttiv/i.test(x)),
    { titoli: t.titoli });
  prova('TSK-971', 'nomi-accessibili-brevi-e-uguali-al-visibile',
    t.nomi.every((n) => n.nome === n.visibile && n.nome.length <= 40) && t.nomi.every((n) => n.descritto_da.length > 10),
    { nomi: t.nomi });
  const stato = await (await fetch(new URL('/api/state', url))).json();
  const sessione = stato.panels.find((p) => p.key === 'sessione');
  const percorsi = [];
  for (const l of (sessione?.readings ?? [])) {
    if (Array.isArray(l.value)) l.value.forEach((v) => v && v.su && percorsi.push(v.su));
    else if (l.value && typeof l.value === 'object') percorsi.push(...Object.keys(l.value));
  }
  // Il vecchio taglio cadeva a 54 e a 70 caratteri, in mezzo a una parola; il nuovo accorcia ai separatori e lo dichiara con «…».
  const tagliati = percorsi.filter((x) => (x.length === 54 || x.length === 70) && !x.startsWith('…') && !x.endsWith('…'));
  prova('TSK-971', 'percorsi-non-tagliati-a-meta-parola', tagliati.length === 0, { tagliati: tagliati.slice(0, 3), esaminati: percorsi.length });
  await page.context().close();
  await turnoLibero();
}

// ── TSK-972 — comando disabilitato ──────────────────────────────────────────
{
  const page = await nuovaPagina();
  const v = await page.evaluate(() => {
    const b = document.getElementById('voce-toggle');
    const contrasto = (el) => {
      const lum = (c) => { const [r, g, bl] = c.match(/[\d.]+/g).slice(0, 3).map(Number)
        .map((x) => { x /= 255; return x <= 0.03928 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4; });
        return 0.2126 * r + 0.7152 * g + 0.0722 * bl; };
      let bg = getComputedStyle(el).backgroundColor, n = el;
      while ((bg === 'rgba(0, 0, 0, 0)' || !bg) && n.parentElement) { n = n.parentElement; bg = getComputedStyle(n).backgroundColor; }
      const [a, c] = [lum(getComputedStyle(el).color), lum(bg)].sort((x, y) => y - x);
      return (a + 0.05) / (c + 0.05);
    };
    const pastiglia = b.querySelector('.pastiglia');
    const motivo = (b.getAttribute('aria-describedby') || '').split(' ').filter(Boolean)
      .map((id) => document.getElementById(id)?.textContent ?? '').join(' ');
    return { bloccato: b.getAttribute('aria-disabled') === 'true' || b.disabled, disabled_html: b.disabled, tabindex: b.tabIndex,
             motivo, opacita: getComputedStyle(b).opacity, contrasto_testo: contrasto(b),
             contrasto_pastiglia: pastiglia ? contrasto(pastiglia) : null,
             corpo_pastiglia: pastiglia ? parseFloat(getComputedStyle(pastiglia).fontSize) : null };
  });
  if (!v.bloccato) {
    prova('TSK-972', 'canale-vocale-non-bloccato-nell-ambiente', true, { nota: 'canale disponibile: controllo non applicabile', ...v });
  } else {
    prova('TSK-972', 'voce-aria-disabled-e-non-disabled', !v.disabled_html && v.tabindex === 0, v);
    prova('TSK-972', 'voce-motivo-collegato-e-comprensibile',
      v.motivo.length > 10 && !/piper|dipendenza/i.test(v.motivo), { motivo: v.motivo });
    prova('TSK-972', 'voce-testo-leggibile',
      v.opacita === '1' && v.contrasto_testo >= 4.5 && v.contrasto_pastiglia >= 4.5 && v.corpo_pastiglia >= 12, v);
    await bottone(page, 'Promuovi').focus();
    let raggiunto = false;
    for (let i = 0; i < 4 && !raggiunto; i++) {
      await page.keyboard.press('Tab');
      raggiunto = await page.evaluate(() => document.activeElement.id === 'voce-toggle');
    }
    prova('TSK-972', 'voce-raggiungibile-da-tab', raggiunto, {});
  }
  // un comando bloccato dal lavoro in corso dice perche'
  await bottone(page, 'Controllo di salute').click();
  await attendi(1200);
  const c = await page.evaluate(() => [...document.querySelectorAll('#azioni button')].map((b) => ({
    bloccato: b.getAttribute('aria-disabled') === 'true', opacita: getComputedStyle(b).opacity,
    motivo: (b.getAttribute('aria-describedby') || '').split(' ').filter(Boolean)
      .map((id) => document.getElementById(id)?.textContent ?? '').join(' ') })));
  prova('TSK-972', 'comando-bloccato-dal-lavoro-dice-perche',
    c.some((x) => x.bloccato) && c.filter((x) => x.bloccato).every((x) => /lavoro (è|e') in corso/.test(x.motivo) && x.opacita === '1'),
    { comandi: c });
  await page.context().close();
  await turnoLibero();
}

// ── TSK-973 — regioni live distinte, alto contrasto ─────────────────────────
{
  const page = await nuovaPagina();
  await attendi(1500);
  const live = await page.evaluate(() => ({
    azioni: document.getElementById('annuncio')?.getAttribute('aria-live'),
    fonti: document.getElementById('annuncio-fonti')?.getAttribute('aria-live'),
    fonti_testo: document.getElementById('annuncio-fonti')?.textContent ?? '',
    azioni_testo: document.getElementById('annuncio')?.textContent ?? '' }));
  prova('TSK-973', 'due-regioni-live-distinte', live.azioni === 'polite' && live.fonti === 'polite', live);
  prova('TSK-973', 'stato-fonti-solo-nella-sua-regione',
    /non osservabil/.test(live.fonti_testo) && !/non osservabil/.test(live.azioni_testo), live);
  await page.locator('#mascotte-toggle').click();
  await attendi(400);
  const dopo = await page.evaluate(() => ({ azioni: document.getElementById('annuncio').textContent,
                                            fonti: (document.getElementById('annuncio-fonti')?.textContent ?? '') }));
  prova('TSK-973', 'azione-non-sovrascrive-lo-stato-delle-fonti',
    /Mascotte/.test(dopo.azioni) && dopo.fonti === live.fonti_testo, { dopo, prima: live.fonti_testo });
  await page.route('**/api/state', (r) => r.fulfill({ status: 500, body: 'boom' }));
  await page.locator('#ricarica').click();
  await attendi(600);
  // Un aggiornamento gia' in volo puo' chiudersi dopo e annunciare il ripristino: si guarda
  // la storia degli annunci, non l'ultimo.
  const guasto = await page.evaluate(() => ({
    nelle_fonti: window.__annunci.some((a) => a.id === 'annuncio-fonti' && /servizio/i.test(a.testo)),
    nelle_azioni: window.__annunci.some((a) => a.id === 'annuncio' && /servizio/i.test(a.testo)) }));
  prova('TSK-973', 'guasto-di-lettura-nella-regione-delle-fonti', guasto.nelle_fonti && !guasto.nelle_azioni, guasto);
  await page.unroute('**/api/state');
  await page.context().close();

  const hc = await nuovaPagina({ forcedColors: 'active' });
  const firma = (id) => hc.evaluate((i) => { const s = getComputedStyle(document.getElementById(i));
    return [s.borderTopWidth, s.borderTopStyle, s.color, s.backgroundColor].join('|'); }, id);
  // Lo STESSO pulsante premuto e non premuto: confrontarne due diversi mescolerebbe lo stato
  // premuto con altre differenze (per esempio un canale non disponibile).
  const premuto = await hc.evaluate(() => document.getElementById('mascotte-toggle').getAttribute('aria-pressed'));
  const acceso = await firma('mascotte-toggle');
  await hc.locator('#mascotte-toggle').click();
  await attendi(300);
  const spento = await firma('mascotte-toggle');
  prova('TSK-973', 'forced-colors-premuto-si-distingue',
    premuto === 'true' && acceso !== spento, { premuto: acceso, non_premuto: spento });
  await bottone(hc, 'Promuovi una pagina').click();
  await hc.waitForSelector('#conferma:not([hidden])');
  const [si, no] = [await firma('conferma-si'), await firma('conferma-no')];
  prova('TSK-973', 'forced-colors-procedi-e-annulla-si-distinguono', si !== no, { procedi: si, annulla: no });
  await hc.context().close();
}

await browser.close();
console.log(JSON.stringify({ esiti }, null, 1));

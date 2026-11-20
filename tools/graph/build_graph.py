#!/usr/bin/env python3
"""build_graph.py — topologia della conoscenza della factory e classificazione dei suoi archi (stadio 1).

Legge `wiki/`, `management/kanban/` e `raw/` (di quest'ultimo solo i metadati: path) e produce:
- il **grafo**: nodi e archi, JSON di sola topologia (nessuna coordinata: il layout si calcola dove si legge);
- il **report**: conteggi per classe e, per ogni arco non risolto, chi deve ripararlo.

Ogni arco ha due campi ortogonali:
  origin      declared | derived | inferred
  resolution  resolved | unresolved-path | id-kanban | placeholder      (null se origin != declared)

  declared   scritto da qualcuno: wikilink, `[^src: ...]`, frontmatter del kanban (epic, story,
             depends_on, decision_refs)
  derived    ricostruito dalla storia: epica -> storia -> task (struttura del kanban), task -> commit
             (ID nel titolo del commit), commit -> PR (merge del branch dell'epica). Da
             `tools/docs/trace-epic.py`, importato come libreria, si usa il parser del frontmatter; la
             storia git la legge `_git` di questo modulo, che su errore solleva `ErroreGit` invece di
             restituire "" (review iter-1 F4: `trace-epic.git()` degradava in silenzio)
  inferred   non prodotto qui: e' un layer separato, di uno stadio successivo

Risoluzione di un arco declared: un ID kanban presente nell'indice del kanban, un titolo di tavola
rotonda che corrisponde a un file, un path che esiste, un ADR che ha il suo file sono `resolved`;
`id-kanban` conta solo gli ID non trovati; un path o un titolo che non risolve e un wikilink con
target mancante sono `unresolved-path`; `...`, `…`, `<pagina>`, `name` sono `placeholder`.
«declared-unverified» non e' un valore di campo: e' solo un'etichetta del testo del report.

Segnaposto: sono `placeholder` un target vuoto, fatto solo di punti o `…`, con `<` e `>`, che finisce
per `...` o `…`, oppure una delle parole `name`, `nome`, `pagina`, `page`, `slug` (le ultime solo se non
risolvono a un file).

Deduplica per coppia sorgente -> target; il numero di citazioni grezze resta nell'attributo `count`.
Se la stessa coppia arriva con origin diversi non si fondono: vince l'origin piu' forte (declared, poi
derived, poi inferred, l'ordine di ORIGINS), l'altro non contribuisce a `count` ne' a `via`, e il
conflitto resta elencato nel report (`conflitti_origin`) e contato nei conteggi.
Il codice fra backtick e i blocchi ``` non si analizzano (regole di `tools/lint/wikilink.py`, le stesse
di Check 1). Le pagine di `wiki/lint/` e `wiki/query/` (report generati, domande effimere) sono nodi
ma non sorgenti di archi.

Archi non risolti, «a chi spetta»: per le pagine di `wiki/` valgono le regole degli accordi 24-25 della
tavola rotonda (wiki-keeper per draft, «wiki-keeper, poi maintainer» negli altri casi); per i file di
`management/kanban/` (decisione del maintainer 2026-11-18) il destinatario e' «product-manager / TPM» e
lo status e' quello del frontmatter del TSK/US/EP («non dichiarato» se manca). Ogni gruppo porta
`area: wiki|kanban`.

Confine di scrittura: `--out` e' rifiutato dentro `apps/`, dentro gli alberi che `sync-docs.ts` legge
(estratti dal file stesso: se il file esiste e l'estrazione non trova nulla e' un errore, non un
ripiego; se il file manca si usano i default ALBERI_SYNC_DEFAULT) e dentro gli alberi che questo
produttore legge (`wiki/`, `management/kanban/`, `raw/`), perche' l'output entrerebbe nel corpus al giro
dopo. Non sono coperti i file che le schede di `apps/factory-guide/content/units/*.json` citano fuori
da quegli alberi (es. `PATTERN-capabilities.md`, un ADR): rischio pratico nullo, perche' l'output si
scrive in una cartella e mai sopra un file esistente del repo (review iter-2 N2).

USO:
  python3 tools/graph/build_graph.py                       # report in markdown su stdout
  python3 tools/graph/build_graph.py --formato json        # {"grafo": ..., "report": ...} su stdout
  python3 tools/graph/build_graph.py --out deliverables/grafo   # grafo.json, report.json, report.md
  python3 tools/graph/build_graph.py --root <factory> --ref origin/main

Non garantisce:
- che la pagina dica cio' che la fonte dice: `resolved` si legge «fonte trovata» (il file esiste), il
  controllo del §header e' fuori da questo stadio;
- che lo `status` dichiarato da una pagina sia vero: il report lo mostra come scritto;
- la completezza degli archi `derived`: i commit si attribuiscono dal titolo, non dal corpo;
- che nessun altro processo legga o copi l'output: il confine e' sul dove si scrive (mai sotto `apps/`
  ne' negli alberi letti da `apps/factory-guide/scripts/sync-docs.ts`), non su chi legge.

Solo stdlib e git. In sola lettura: non scrive in `wiki/gaps.md` ne' nel kanban; scrive solo in --out.
Exit 0; 2 se --out cade in un percorso vietato o se `sync-docs.ts` non e' interpretabile; 3 se git
fallisce (ref inesistente, non e' un repo): gli archi derived non si degradano in silenzio.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import posixpath
import re
import subprocess
import sys
from pathlib import Path

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE_DEFAULT = os.path.dirname(os.path.dirname(QUI))
sys.path.insert(0, os.path.join(RADICE_DEFAULT, 'tools', 'lint'))
sys.path.insert(0, os.path.join(RADICE_DEFAULT, 'tools', 'coordinamento'))

import kanban_ids  # noqa: E402  (forma degli ID: fonte unica)
import wikilink  # noqa: E402  (parser condiviso con Check 1)

RESOLVED, UNRESOLVED, ID_KANBAN, PLACEHOLDER = 'resolved', 'unresolved-path', 'id-kanban', 'placeholder'
RESOLUTIONS = (RESOLVED, UNRESOLVED, ID_KANBAN, PLACEHOLDER)
ORIGINS = ('declared', 'derived', 'inferred')
NON_DICHIARATO = 'non dichiarato'
STATI_PAGINA = ('draft', 'review', 'approved')
A_CHI_SPETTA = {'draft': 'wiki-keeper'}
A_CHI_SPETTA_DEFAULT = 'wiki-keeper, poi maintainer'
A_CHI_SPETTA_KANBAN = 'product-manager / TPM'  # decisione del maintainer 2026-11-18, solo management/kanban/
AREE = ('wiki', 'kanban')
ALBERI_LETTI = ('wiki', 'management/kanban', 'raw')  # gli alberi che questo produttore legge
NOMI_OUTPUT = ('grafo.json', 'report.json', 'report.md')
COORDINATE = ('x', 'y', 'z', 'pos', 'position', 'layout', 'coords', 'coordinates')
SENZA_ARCHI_DA = ('wiki/lint/', 'wiki/query/')
CAMPI_FRONTMATTER = ('epic', 'story', 'depends_on', 'decision_refs')
PAROLE_SEGNAPOSTO = {'name', 'nome', 'pagina', 'page', 'slug'}
VALORI_VUOTI = {'', 'none', 'null', '-', '[]', 'n/a', 'nessuno', 'nessuna'}
SRC = re.compile(r'\[\^src:([^\]]*)\]')
SPLIT_SRC = re.compile(r'\s+\+\s+|\s*;\s*|,\s+(?=(?:raw|wiki|management|design_&_architecture)/)')
TAVOLA = re.compile(r'(?:tavola[ -]rotonda[ -]|\bTR-)([0-9a-f]{8})\b', re.I)
ID_INIZIALE = re.compile(r'^((?:[A-Z]{2,4}-)?(?:EP|US|TSK)-\d+)(?![\w-])')
ADR = re.compile(r'^ADR-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$')
ALBERI_SYNC_DEFAULT = ('.claude/agents', '.claude/commands', '.claude/skills')
SYNC_DOCS = 'apps/factory-guide/scripts/sync-docs.ts'


def carica_trace_epic(radice):
    """`tools/docs/trace-epic.py` come libreria (il nome ha un trattino: import da file).
    Se ne usa `frontmatter_testo`; la storia git passa da `_git` (vedi docstring del modulo).
    `ROOT` si punta comunque alla radice analizzata, per coerenza se altre primitive venissero usate."""
    spec = importlib.util.spec_from_file_location(
        'trace_epic', os.path.join(RADICE_DEFAULT, 'tools', 'docs', 'trace-epic.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.ROOT = Path(radice)
    return mod


def _elenca(radice, base, solo_md=True):
    out = []
    for d, dirnames, fs in os.walk(os.path.join(radice, base)):
        dirnames[:] = sorted(x for x in dirnames if not x.startswith('.'))
        for f in sorted(fs):
            if f.startswith('.') or (solo_md and not f.endswith('.md')):
                continue
            out.append(os.path.relpath(os.path.join(d, f), radice).replace(os.sep, '/'))
    return sorted(out)


def _leggi(radice, rel):
    with open(os.path.join(radice, rel), encoding='utf-8', errors='replace') as fh:
        return fh.read()


def _scalare(v):
    if isinstance(v, list):
        return ''
    return re.split(r'\s+#', str(v or ''))[0].strip().strip('"\'')


def _valori(v):
    """Valori di un campo del frontmatter: lista a trattini, lista in linea `[a, b]` o scalare."""
    if isinstance(v, list):
        return [x.strip().strip('"\'') for x in v if x.strip()]
    s = _scalare(v)
    if s.startswith('[') and s.endswith(']'):
        return [x.strip().strip('"\'') for x in s[1:-1].split(',') if x.strip()]
    return [s] if s else []


def stato_pagina(fm):
    """`status` dichiarato se e' draft|review|approved, altrimenti il valore esplicito «non dichiarato»."""
    v = _scalare((fm or {}).get('status')).lower()
    return v if v in STATI_PAGINA else NON_DICHIARATO


def a_chi_spetta(stato):
    return A_CHI_SPETTA.get(stato, A_CHI_SPETTA_DEFAULT)


def prefisso_target(t):
    """Primo segmento del path (`raw/`), altrimenti prima parola (`ADR`, `Tavola`); `(nessuno)` se vuoto."""
    t = (t or '').strip()
    if '/' in t:
        return t.split('/')[0] + '/'
    m = re.match(r'[^\s-]+', t)
    return m.group(0) if m else '(nessuno)'


class Contesto:
    """Indici di sola lettura sul repo analizzato: file, ID kanban, tavole rotonde, ADR."""

    def __init__(self, radice):
        self.radice = radice
        self.te = carica_trace_epic(radice)
        self.wiki = _elenca(radice, 'wiki')
        self.kanban = _elenca(radice, 'management/kanban')
        self.raw = _elenca(radice, 'raw', solo_md=False)
        self.fm = {}
        self.testo = {}
        for p in self.wiki + self.kanban:
            self.testo[p] = _leggi(radice, p)
            self.fm[p], _ = self.te.frontmatter_testo(self.testo[p])
        self.risolvi = wikilink.Risolutore(self.wiki)
        self.indice_kanban = {}
        for p in self.kanban:
            i = _scalare(self.fm[p].get('id'))
            if kanban_ids.tipo_di(i) and i not in self.indice_kanban:
                self.indice_kanban[i] = p
        self.tavole = {}
        self.adr = {}
        for p in _elenca(radice, 'wiki/decisions') + _elenca(radice, 'design_&_architecture'):
            base = os.path.basename(p)
            m = TAVOLA.match(base)
            if m:
                self.tavole.setdefault(m.group(1).lower(), p)
            if base.startswith('ADR-'):
                self.adr[base] = p

    def esiste(self, rel):
        return os.path.exists(os.path.join(self.radice, rel))

    def trova_adr(self, ident):
        for base in sorted(self.adr):
            if base == ident + '.md' or base.startswith(ident + '-'):
                return self.adr[base]
        return None


def _forte(t):
    return (not t) or bool(re.fullmatch(r'[.…\s]+', t)) or ('<' in t and '>' in t) or t.endswith(('...', '…'))


def classifica_wikilink(grezzo, ctx):
    """(resolution, target): path del file se risolve, altrimenti il target normalizzato."""
    dest = wikilink.destinazione(grezzo)
    if _forte(dest):
        return PLACEHOLDER, dest
    r = ctx.risolvi(grezzo)
    if r:
        return RESOLVED, r
    if dest in PAROLE_SEGNAPOSTO:
        return PLACEHOLDER, dest
    return UNRESOLVED, dest


def _e_path(c):
    return bool(c) and ('/' in c or c.endswith('.md'))


def _cit_id_iniziale(t, ctx):
    """«TSK-507 — analisi...»: la citazione e' l'ID che apre il testo."""
    iniziale = ID_INIZIALE.match(t)
    if not iniziale:
        return None
    p = ctx.indice_kanban.get(iniziale.group(1))
    return (RESOLVED, p) if p else (ID_KANBAN, iniziale.group(1))


def _cit_tavola(t, ctx):
    tr = TAVOLA.search(t)
    if not tr:
        return None
    p = ctx.tavole.get(tr.group(1).lower())
    return (RESOLVED, p) if p else (UNRESOLVED, t)


def _candidati_path(t):
    """Il testo senza ancora, senza la parentesi finale, e la sua prima parola."""
    senza_ancora = t.split('#')[0].strip()
    return [senza_ancora, re.sub(r'\s+\(.*$', '', senza_ancora),
            senza_ancora.split()[0] if senza_ancora else '']


def _cit_path_esistente(t, ctx):
    for c in _candidati_path(t):
        if not _e_path(c):
            continue
        norm = posixpath.normpath(c[2:] if c.startswith('./') else c)
        if not norm.startswith('..') and ctx.esiste(norm):
            return RESOLVED, norm
    return None


def _cit_path_mancante(t, ctx):
    senza_ancora, _, prima_parola = _candidati_path(t)
    c0 = prima_parola if _e_path(prima_parola) else senza_ancora
    return (UNRESOLVED, c0) if _e_path(c0) else None


def _cit_adr(t, ctx):
    if not ADR.match(t):
        return None
    p = ctx.trova_adr(t)
    return (RESOLVED, p) if p else (UNRESOLVED, t)


def _cit_file_radice(t, ctx):
    """PATTERN, README: file della radice citati senza estensione."""
    if re.fullmatch(r'[A-Za-z][\w-]*', t) and ctx.esiste(t + '.md'):
        return RESOLVED, t + '.md'
    return None


def _cit_segnaposto(t, ctx):
    return (PLACEHOLDER, t) if t.lower() in PAROLE_SEGNAPOSTO else None


#: In ordine di precedenza: vince il primo che riconosce la citazione.
RISOLUTORI_CITAZIONE = (_cit_id_iniziale, _cit_tavola, _cit_path_esistente, _cit_path_mancante,
                        _cit_adr, _cit_file_radice, _cit_segnaposto)


def classifica_citazione(parte, ctx):
    """(resolution, target) di una citazione (`[^src:]` o valore di frontmatter)."""
    t = parte.split('§')[0].strip().strip('`"\'').strip()
    if _forte(t):
        return PLACEHOLDER, t
    for risolvi in RISOLUTORI_CITAZIONE:
        esito = risolvi(t, ctx)
        if esito:
            return esito
    return UNRESOLVED, t


class Archi:
    """Accumulatore: un arco per coppia sorgente -> target, con il conteggio delle citazioni grezze.

    Precedenza se la coppia arriva con origin diversi: l'origin piu' forte (indice minore in ORIGINS)
    resta, quello scartato non entra in `count` ne' in `via` ed e' registrato in `conflitti`."""

    def __init__(self):
        self._d = {}
        self.conflitti = {}

    def _nuovo(self, src, tgt, origin, resolution):
        return {'source': src, 'target': tgt, 'origin': origin, 'resolution': resolution,
                'count': 0, 'via': set()}

    def _registra_conflitto(self, src, tgt, tenuto, scartato):
        self.conflitti[(src, tgt)] = {'source': src, 'target': tgt,
                                      'origin_tenuta': tenuto, 'origin_scartata': scartato}

    def aggiungi(self, src, tgt, origin, resolution, via):
        if src == tgt:
            return
        a = self._d.setdefault((src, tgt), self._nuovo(src, tgt, origin, resolution))
        if a['origin'] != origin:
            if ORIGINS.index(origin) < ORIGINS.index(a['origin']):
                self._registra_conflitto(src, tgt, origin, a['origin'])
                a = self._d[(src, tgt)] = self._nuovo(src, tgt, origin, resolution)
            else:
                self._registra_conflitto(src, tgt, a['origin'], origin)
                return
        a['count'] += 1
        a['via'].add(via)

    def lista(self):
        out = []
        for k in sorted(self._d):
            a = dict(self._d[k])
            a['via'] = sorted(a['via'])
            out.append(a)
        return out

    def elenco_conflitti(self):
        return [self.conflitti[k] for k in sorted(self.conflitti)]


def _archi_da_testo(p, ctx, archi):
    """Wikilink e `[^src: ...]` del corpo di una pagina."""
    for g in wikilink.estrai(ctx.testo[p]):
        res, tgt = classifica_wikilink(g, ctx)
        archi.aggiungi(p, tgt, 'declared', res, 'wikilink')
    for m in SRC.finditer(wikilink.senza_codice(ctx.testo[p])):
        for parte in SPLIT_SRC.split(m.group(1).strip()):
            res, tgt = classifica_citazione(parte, ctx)
            archi.aggiungi(p, tgt, 'declared', res, 'src')


def _citazioni_frontmatter(fm):
    """(chiave, citazione) per ogni valore non vuoto dei campi che puntano ad altri nodi."""
    for chiave in CAMPI_FRONTMATTER:
        for v in _valori(fm.get(chiave)):
            if v.lower() in VALORI_VUOTI:
                continue
            ids = kanban_ids.ID_IN_TESTO.findall(v) if chiave != 'decision_refs' else []
            for parte in (ids or [v]):
                yield chiave, parte


def archi_declared(ctx, archi):
    for p in ctx.wiki + ctx.kanban:
        if not p.startswith(SENZA_ARCHI_DA):
            _archi_da_testo(p, ctx, archi)
    for p in ctx.kanban:
        for chiave, parte in _citazioni_frontmatter(ctx.fm[p]):
            res, tgt = classifica_citazione(parte, ctx)
            archi.aggiungi(p, tgt, 'declared', res, 'frontmatter:' + chiave)


class ErroreGit(RuntimeError):
    """Git non ha potuto leggere la storia richiesta: il produttore si ferma, non degrada."""


def _git(radice, *args):
    try:
        r = subprocess.run(['git', *args], cwd=radice, capture_output=True, text=True, encoding="utf-8", errors="replace")
    except OSError as e:
        raise ErroreGit('git non eseguibile: %s' % e)
    if r.returncode != 0:
        raise ErroreGit('git %s fallito (rc %d): %s' % (' '.join(args), r.returncode,
                                                       (r.stderr or '').strip() or 'nessun messaggio'))
    return r.stdout


def _righe_log(radice, ref, filtro):
    out = []
    for r in _git(radice, 'log', ref, filtro, '--date=short', '--format=%H|%ad|%s').splitlines():
        h, data, sogg = r.split('|', 2)
        out.append((h[:10], data, sogg))
    return out


def _commit_e_merge(ctx, ref):
    """(commit, merge) raggiungibili da `ref`; ErroreGit se il ref non esiste o git fallisce."""
    _git(ctx.radice, 'rev-parse', '--verify', '--quiet', ref + '^{commit}')
    return _righe_log(ctx.radice, ref, '--no-merges'), _righe_log(ctx.radice, ref, '--merges')


def _id_di(ctx, rel):
    return _scalare(ctx.fm.get(rel, {}).get('id'))


def _sottocartelle(d):
    return [os.path.join(d, n) for n in sorted(os.listdir(d)) if os.path.isdir(os.path.join(d, n))]


def _rel(ctx, path):
    return os.path.relpath(path, ctx.radice).replace(os.sep, '/')


def _file_con_tipo(ctx, cartella, tipo):
    """Path relativi dei .md di una cartella il cui `id` e' del tipo dato (EP, US, TSK)."""
    base = _rel(ctx, cartella)
    return [base + '/' + f for f in sorted(os.listdir(cartella))
            if f.endswith('.md') and kanban_ids.tipo_di(_id_di(ctx, base + '/' + f)) == tipo]


def _epiche_del_kanban(ctx):
    """(path dell'epica, sua cartella) per ogni cartella `EP-*` presente nell'indice."""
    kan = os.path.join(ctx.radice, 'management', 'kanban')
    if not os.path.isdir(kan):
        return
    for nome_ep in sorted(os.listdir(kan)):
        d = os.path.join(kan, nome_ep)
        ep_id, tipo = kanban_ids.id_cartella(nome_ep)
        ep_p = ctx.indice_kanban.get(ep_id)
        if tipo == 'EP' and os.path.isdir(d) and ep_p:
            yield ep_p, d


def _archi_di_storia(ctx, ep_p, cartella_us, archi, epica_di):
    storie = _file_con_tipo(ctx, cartella_us, 'US')
    if not storie:
        return
    us_p = storie[0]
    archi.aggiungi(ep_p, us_p, 'derived', None, 'catena')
    epica_di[us_p] = ep_p
    for rel in _file_con_tipo(ctx, cartella_us, 'TSK'):
        if rel != us_p:
            archi.aggiungi(us_p, rel, 'derived', None, 'catena')
            epica_di[rel] = ep_p


def _catena_kanban(ctx, archi):
    """Epica -> storia -> task dalla struttura delle cartelle: (epica_di, branch_di)."""
    epica_di = {}   # path di un'epica/storia/task -> path dell'epica
    branch_di = {}  # path dell'epica -> branch
    for ep_p, d in _epiche_del_kanban(ctx):
        epica_di[ep_p] = ep_p
        branch_di[ep_p] = _scalare(ctx.fm[ep_p].get('branch'))
        for cartella_us in _sottocartelle(d):
            _archi_di_storia(ctx, ep_p, cartella_us, archi, epica_di)
    return epica_di, branch_di


def _pr_di_epica(branch_di, merges, nodi):
    """Per ogni epica con un branch, il primo merge del branch: aggiunge il nodo PR."""
    pr_di_epica = {}
    for ep_p, branch in sorted(branch_di.items()):
        if not branch:
            continue
        pat = re.compile(r'from [^ ]*/' + re.escape(branch) + r'$')
        for h, data, sogg in merges:
            if not pat.search(sogg):
                continue
            pr = re.search(r'#(\d+)', sogg)
            nid = 'pr:#' + pr.group(1) if pr else 'merge:' + h
            nodi[nid] = {'id': nid, 'tipo': 'pr', 'titolo': sogg, 'data': data}
            pr_di_epica[ep_p] = nid
            break
    return pr_di_epica


def _legami_del_commit(ctx, sogg):
    """Path dei TSK citati nel titolo, altrimenti quelli delle epiche citate; solo ID in indice."""
    ids = set(kanban_ids.ID_IN_TESTO.findall(sogg))
    noti = sorted(i for i in ids if i in ctx.indice_kanban)
    tsk = [i for i in noti if kanban_ids.tipo_di(i) == 'TSK']
    eps = [i for i in noti if kanban_ids.tipo_di(i) == 'EP']
    return [ctx.indice_kanban[i] for i in (tsk or eps)]


def _archi_dei_commit(ctx, commits, epica_di, pr_di_epica, archi, nodi):
    """Task -> commit e commit -> PR; restituisce i PR agganciati ad almeno un commit."""
    usati = set()
    for h, data, sogg in commits:
        legami = _legami_del_commit(ctx, sogg)
        if not legami:
            continue
        cid = 'commit:' + h
        nodi[cid] = {'id': cid, 'tipo': 'commit', 'titolo': sogg, 'data': data}
        for p in legami:
            archi.aggiungi(p, cid, 'derived', None, 'catena')
            pr = pr_di_epica.get(epica_di.get(p))
            if pr:
                usati.add(pr)
                archi.aggiungi(cid, pr, 'derived', None, 'catena')
    return usati


def archi_derived(ctx, ref, archi, nodi):
    """Catena epica -> storia -> task (struttura del kanban), task -> commit, commit -> PR."""
    epica_di, branch_di = _catena_kanban(ctx, archi)
    commits, merges = _commit_e_merge(ctx, ref)
    pr_di_epica = _pr_di_epica(branch_di, merges, nodi)
    usati = _archi_dei_commit(ctx, commits, epica_di, pr_di_epica, archi, nodi)
    for nid in [k for k, n in nodi.items() if n['tipo'] == 'pr' and k not in usati]:
        del nodi[nid]


def costruisci_nodi(ctx):
    nodi = {}
    for p in ctx.wiki:
        fm = ctx.fm[p]
        corpo = ctx.testo[p]
        h1 = re.search(r'^#\s+(.+)$', corpo.split('\n---\n', 1)[-1] if corpo.startswith('---') else corpo, re.M)
        titolo = _scalare(fm.get('title')) or (h1.group(1).replace('`', '').strip() if h1 else
                                               os.path.basename(p)[:-3])
        nodi[p] = {'id': p, 'tipo': 'wiki', 'titolo': titolo, 'status': stato_pagina(fm),
                   'sezione': p.split('/')[1] if p.count('/') > 1 else ''}
    for p in ctx.kanban:
        fm = ctx.fm[p]
        i = _scalare(fm.get('id'))
        nodi[p] = {'id': p, 'tipo': 'kanban', 'titolo': _scalare(fm.get('title')) or os.path.basename(p)[:-3],
                   'kanban_id': i, 'tipo_kanban': kanban_ids.tipo_di(i) or '',
                   'status': _scalare(fm.get('status')) or NON_DICHIARATO}
    for p in ctx.raw:
        nodi[p] = {'id': p, 'tipo': 'raw'}
    return nodi


def controlla_archi(archi):
    """Invarianti dello schema. Un arco non declared con `resolution` valorizzata, o un arco declared
    senza una `resolution` valida, e' un difetto del produttore: solleva ValueError."""
    for a in archi:
        if a['origin'] not in ORIGINS:
            raise ValueError('origin non valida: %r (%s -> %s)' % (a['origin'], a['source'], a['target']))
        if a['origin'] == 'declared':
            if a['resolution'] not in RESOLUTIONS:
                raise ValueError('arco declared senza resolution valida: %s -> %s' % (a['source'], a['target']))
        elif a['resolution'] is not None:
            raise ValueError('arco %s con resolution valorizzata (%r): %s -> %s'
                             % (a['origin'], a['resolution'], a['source'], a['target']))


def costruisci(radice, ref='HEAD'):
    """(grafo, report) in strutture JSON-serializzabili."""
    ctx = Contesto(radice)
    nodi = costruisci_nodi(ctx)
    acc = Archi()
    archi_declared(ctx, acc)
    archi_derived(ctx, ref, acc, nodi)
    archi = acc.lista()
    for a in archi:
        a['in_graph'] = a['target'] in nodi
    controlla_archi(archi)
    grafo = {'nodi': [nodi[k] for k in sorted(nodi)], 'archi': archi}
    return grafo, report_di(grafo, acc.elenco_conflitti())


def _gruppo_non_risolto(src, nodo):
    """Intestazione del gruppo per pagina: area, status e destinatario secondo l'area della sorgente."""
    tipo = nodo.get('tipo', '')
    if tipo == 'kanban':
        area, status, spetta = 'kanban', nodo.get('status') or NON_DICHIARATO, A_CHI_SPETTA_KANBAN
    else:
        status = nodo.get('status', NON_DICHIARATO) if tipo == 'wiki' else NON_DICHIARATO
        area, spetta = 'wiki', a_chi_spetta(status)
    return {'pagina': nodo.get('titolo', src), 'file_citante': src, 'tipo_nodo': tipo, 'area': area,
            'status': status, 'a_chi_spetta': spetta, 'archi': []}


def _non_risolti(archi, nodi):
    gruppi = {}
    for a in archi:
        if a['origin'] != 'declared' or a['resolution'] == RESOLVED:
            continue
        g = gruppi.setdefault(a['source'], _gruppo_non_risolto(a['source'], nodi.get(a['source'], {})))
        g['archi'].append({'target': a['target'], 'prefisso': prefisso_target(a['target']),
                           'resolution': a['resolution'], 'count': a['count'], 'via': a['via']})
    return [gruppi[k] for k in sorted(gruppi)]


def _conteggi_per_classe(archi):
    per_origin = {o: 0 for o in ORIGINS}
    per_res = {r: 0 for r in RESOLUTIONS}
    per_res_cit = {r: 0 for r in RESOLUTIONS}
    for a in archi:
        per_origin[a['origin']] += 1
        if a['resolution']:
            per_res[a['resolution']] += 1
            per_res_cit[a['resolution']] += a['count']
    return per_origin, per_res, per_res_cit


def _senza_archi(nodi, archi):
    entranti, collegati = set(), set()
    for a in archi:
        if a['target'] in nodi and a['source'] in nodi:
            entranti.add(a['target'])
            collegati.update((a['source'], a['target']))
    return sorted(k for k in nodi if k not in entranti), sorted(k for k in nodi if k not in collegati)


def report_di(grafo, conflitti=()):
    nodi = {n['id']: n for n in grafo['nodi']}
    archi = grafo['archi']
    per_origin, per_res, per_res_cit = _conteggi_per_classe(archi)
    no_inbound, isolated = _senza_archi(nodi, archi)
    non_risolti = _non_risolti(archi, nodi)
    per_area = {area: sum(1 for g in non_risolti if g['area'] == area) for area in AREE}
    return {
        'conteggi': {
            'nodi': len(nodi), 'archi': len(archi),
            'citazioni_grezze_declared': sum(a['count'] for a in archi if a['origin'] == 'declared'),
            'per_origin': per_origin, 'per_resolution': per_res, 'citazioni_per_resolution': per_res_cit,
            'no_inbound': len(no_inbound), 'isolated': len(isolated),
            'pagine_non_risolte_per_area': per_area, 'conflitti_origin': len(conflitti)},
        'no_inbound': no_inbound, 'isolated': isolated, 'non_risolti': non_risolti,
        'conflitti_origin': list(conflitti),
        'avvertenza': 'resolved = fonte trovata: il file esiste; non verifica che la pagina dica cio\' '
                      'che la fonte dice (il controllo del §header e\' fuori da questo stadio).'}


def json_di(obj):
    return json.dumps(obj, indent=1, ensure_ascii=False, sort_keys=True) + '\n'


def _cella(s):
    return str(s).replace('|', '\\|').replace('\n', ' ')


def markdown_di(grafo, report):
    c = report['conteggi']
    nodi = {n['id']: n for n in grafo['nodi']}
    o = ['# Grafo della conoscenza — classificazione degli archi', '',
         '> Fonte trovata non vuol dire fonte verificata: **resolved** significa che il file esiste, '
         'non che la pagina dica cio\' che la fonte dice.', '',
         '## Conteggi', '', '| Misura | Valore |', '|---|---|',
         '| Nodi | %d |' % c['nodi'], '| Archi (coppie sorgente -> target) | %d |' % c['archi'],
         '| Citazioni grezze declared | %d |' % c['citazioni_grezze_declared'],
         '| Pagine con archi non risolti, area wiki | %d |' % c['pagine_non_risolte_per_area']['wiki'],
         '| Pagine con archi non risolti, area kanban | %d |' % c['pagine_non_risolte_per_area']['kanban'],
         '| Coppie con origin in conflitto | %d |' % c['conflitti_origin'], '',
         '| origin | archi |', '|---|---|']
    o += ['| %s | %d |' % (k, v) for k, v in c['per_origin'].items()]
    o += ['', '| resolution | etichetta | archi | citazioni |', '|---|---|---|---|']
    et = {RESOLVED: 'fonte trovata', UNRESOLVED: 'non risolto (path o titolo)',
          ID_KANBAN: 'ID kanban non trovato', PLACEHOLDER: 'segnaposto'}
    o += ['| %s | %s | %d | %d |' % (k, et[k], c['per_resolution'][k], c['citazioni_per_resolution'][k])
          for k in RESOLUTIONS]
    o += ['| n/a (derived, inferred) | — | %d | — |' % (c['per_origin']['derived'] + c['per_origin']['inferred']), '',
          '## Nodi senza archi', '',
          'Il termine `orphan` e\' riservato a Check 1 (pagina non raggiungibile da `wiki/index.md`): qui si dice '
          '**no-inbound** (nessun arco entrante da un altro nodo) e **isolated** (nessun arco, ne\' entrante ne\' uscente).',
          '', '| tipo nodo | no-inbound | isolated |', '|---|---|---|']
    tipi = sorted({n['tipo'] for n in grafo['nodi']})
    for t in tipi:
        o.append('| %s | %d | %d |' % (t, sum(1 for k in report['no_inbound'] if nodi[k]['tipo'] == t),
                                      sum(1 for k in report['isolated'] if nodi[k]['tipo'] == t)))
    o += ['', 'L\'elenco completo e\' nel JSON del report (`no_inbound`, `isolated`).', '',
          '## Archi non risolti, per pagina', '']
    if not report['non_risolti']:
        o.append('Nessuno.')
    for g in report['non_risolti']:
        o += ['### %s' % _cella(g['pagina']), '',
              '- file citante: `%s`' % g['file_citante'], '- area: %s' % g['area'],
              '- status: %s' % g['status'],
              '- a chi spetta: %s' % g['a_chi_spetta'], '',
              '| prefisso | target | resolution | etichetta | citazioni | via |', '|---|---|---|---|---|---|']
        for a in g['archi']:
            o.append('| %s | %s | %s | declared-unverified | %d | %s |' % (
                _cella(a['prefisso']), _cella(a['target']), a['resolution'], a['count'], ', '.join(a['via'])))
        o.append('')
    o += _markdown_conflitti(report['conflitti_origin'])
    return '\n'.join(o).rstrip() + '\n'


def _markdown_conflitti(conflitti):
    if not conflitti:
        return []
    o = ['## Coppie con origin in conflitto', '',
         'Vince l\'origin piu\' forte (declared, derived, inferred); l\'altro non entra in `count` ne\' in `via`.',
         '', '| sorgente | target | origin tenuta | origin scartata |', '|---|---|---|---|']
    o += ['| %s | %s | %s | %s |' % (_cella(c['source']), _cella(c['target']), c['origin_tenuta'],
                                    c['origin_scartata']) for c in conflitti]
    return o + ['']


class ErroreSync(RuntimeError):
    """`sync-docs.ts` esiste ma non si riesce a estrarne il perimetro: il confine non e' verificabile."""


def _voci_dichiarate(testo, nome):
    m = re.search(r'const %s[^=]*=\s*\[(.*?)\n\]' % nome, testo, re.S)
    return re.findall(r"\[\s*'([^']+)'", m.group(1)) if m else []


def alberi_di_sync(radice):
    """(alberi, file) che `sync-docs.ts` legge, estratti dal file, piu' `apps/`.
    Senza il file valgono i default dichiarati (ALBERI_SYNC_DEFAULT, nessun file); con il file ma senza
    voci estraibili e' un ErroreSync, non un ripiego silenzioso."""
    if not os.path.isfile(os.path.join(radice, SYNC_DOCS)):
        return ['apps'] + list(ALBERI_SYNC_DEFAULT), []
    testo = _leggi(radice, SYNC_DOCS)
    trees, file_letti = _voci_dichiarate(testo, 'TREES'), _voci_dichiarate(testo, 'ROOT_FILES')
    if not trees or not file_letti:
        raise ErroreSync('%s non interpretabile: TREES (%d voci) o ROOT_FILES (%d voci) non estratti'
                         % (SYNC_DOCS, len(trees), len(file_letti)))
    return ['apps'] + trees, file_letti


def _dentro(dest, t):
    return dest == t or dest.startswith(t + os.sep)


def verifica_out(radice, out):
    """None se --out e' ammesso, altrimenti il motivo del rifiuto."""
    base = os.path.realpath(radice)
    dest = os.path.realpath(out if os.path.isabs(out) else os.path.join(radice, out))
    alberi, file_letti = alberi_di_sync(radice)
    for a in alberi:
        if _dentro(dest, os.path.join(base, a)):
            return '--out dentro %s/: l\'output completo non si scrive in un albero pubblicato o letto da sync-docs' % a
    for a in ALBERI_LETTI:
        if _dentro(dest, os.path.join(base, a)):
            return '--out dentro %s/: e\' un albero letto da questo stesso produttore, l\'output entrerebbe nel corpus' % a
    for f in file_letti:
        for nome in NOMI_OUTPUT:
            if os.path.join(dest, nome) == os.path.join(base, f) or dest == os.path.join(base, f):
                return '--out scriverebbe su %s, letto da sync-docs' % f
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--root', default=RADICE_DEFAULT, help='radice della factory (default: questa)')
    ap.add_argument('--ref', default='HEAD', help='storia git da leggere per gli archi derived (default HEAD)')
    ap.add_argument('--formato', choices=('md', 'json'), default='md', help='formato su stdout (default md)')
    ap.add_argument('--out', help='cartella dove scrivere grafo.json, report.json, report.md '
                                  '(mai sotto apps/, negli alberi di sync-docs ne\' in wiki/, management/kanban/, raw/)')
    a = ap.parse_args(argv)
    try:
        motivo = verifica_out(a.root, a.out) if a.out else None
    except ErroreSync as e:
        print('errore: %s' % e, file=sys.stderr)
        return 2
    if motivo:
        print('rifiutato: ' + motivo, file=sys.stderr)
        return 2
    try:
        grafo, report = costruisci(a.root, a.ref)
    except ErroreGit as e:
        print('errore: storia git non leggibile: %s' % e, file=sys.stderr)
        return 3
    if a.out:
        dest = a.out if os.path.isabs(a.out) else os.path.join(a.root, a.out)
        os.makedirs(dest, exist_ok=True)
        for nome, testo in zip(NOMI_OUTPUT, (json_di(grafo), json_di(report), markdown_di(grafo, report))):
            with open(os.path.join(dest, nome), 'w', encoding='utf-8') as fh:
                fh.write(testo)
        print('scritto %s (grafo.json, report.json, report.md)' % dest)
        return 0
    sys.stdout.write(json_di({'grafo': grafo, 'report': report}) if a.formato == 'json'
                     else markdown_di(grafo, report))
    return 0


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""
verify_gap_closures.py — quali gap di wiki/gaps.md sono chiusi davvero.

Un gap e' chiuso se ha la checkbox `[x]`, una riga di chiusura (`**Risolto:**`, anche nelle forme
`**Risolto (data, contesto):**` e `**Superato:**`), una riga `[CLOSED]` che lo nomina o `~~CHIUSO~~`
nel titolo. La chiusura e' **verificata** se il testo di chiusura rimanda (wikilink `[[pagina]]`
o path `wiki/...md`) ad almeno una pagina della wiki che esiste e cita una fonte `[^src: raw/...]`
presente in raw/ (motivo «fonte: raw»), oppure a un ADR esistente in design_&_architecture/decisions/
con `status: accepted` nel frontmatter (link markdown, path o `[[ADR-...]]`; motivo «fonte: ADR
accepted»; un ADR proposed o inesistente non basta), oppure a una sezione che esiste davvero di un
PATTERN*.md (`PATTERN.md §3`, `PATTERN-runtime.md §18.5`, `PATTERN §18`: un heading con `§N` o
numerato `## N.`; con il nome del file la sezione si cerca in quel file, senza in tutti; motivo
«fonte: PATTERN §N»). Riferimenti a codice, config o kanban NON bastano. Oppure se rimanda (`gaps.md:<riga>` o ID) a un altro gap la cui chiusura e'
verificata: un duplicato chiuso altrove eredita la verifica, non la sostituisce. Una chiusura non verificata conta come gap aperto: prima di un'intervista sulle
decisioni (.claude/skills/pocock-grilling.md) i gap del tema si leggono da qui, non dalle checkbox.

Gap riconosciuti:
  - righe di elenco `- [ ]` / `- [x]`, con ID `G-...` se presente (altrimenti la riga stessa);
  - righe `- [CONFIRMED OPEN]`: il gap e' (di nuovo) aperto. Su un ID gia' chiuso piu' sopra la
    riga annulla checkbox e chiusure precedenti: vale solo una chiusura scritta dopo di lei;
  - sezioni `## AAAA-MM-GG ... — <slug>` senza checkbox (formato di wiki-gap-protocol).
Le righe `**Risolto:**` e `[CLOSED]` si attaccano al gap precedente o a quello che nominano.

Uso:
  python3 tools/wiki/verify_gap_closures.py                         # riepilogo su tutto il registro
  python3 tools/wiki/verify_gap_closures.py --tema 'NCC|ncc-'       # solo i gap del tema (regex)
  python3 tools/wiki/verify_gap_closures.py --tema NCC --elenco     # una riga per gap
  python3 tools/wiki/verify_gap_closures.py --json
  python3 tools/wiki/verify_gap_closures.py --tema NCC --check      # exit 1 se il tema ha chiusure non verificate
Solo stdlib. Nessuna scrittura.
"""
import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
WIKI = ROOT / "wiki"
GAPS = WIKI / "gaps.md"

ITEM = re.compile(r"^\s*- \[( |x|X|CONFIRMED OPEN)\]\s*(.*)")
GAP_ID = re.compile(r"\bG-[A-Z0-9][A-Za-z0-9-]*[A-Za-z0-9]")
SECTION = re.compile(r"^## (\d{4}-\d{2}-\d{2})\S*\s.*?[—-]\s*([a-z0-9][a-z0-9-]{2,})\s*$")
# `**Risolto:**`, `**Risolto (2026-10-16T09:31Z, ...):**`, `**Superato:**` (forme della derivata portale-servizi)
RISOLTO = re.compile(r"\*\*(?:Risolto|Superato)\b[^*\n]*\*\*")
CHIUSO_TITOLO = re.compile(r"~~\s*CHIUSO")
RIMANDO_RIGA = re.compile(r"gaps\.md:(\d+)")
CLOSED = re.compile(r"\[CLOSED\]")
CLOSED_ITEM = re.compile(r"^\s*- \[CLOSED\]\s*(.*)")
CODE_SPAN = re.compile(r"`[^`]*`")
WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]")
WIKIPATH = re.compile(r"wiki/[\w./-]+\.md")
ADR_REF = re.compile(r"\bADR-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*")
PATTERN_REF = re.compile(r"\b(PATTERN(?:-[a-z]+)?(?:\.md)?)\s*§\s*(\d+(?:\.\d+)*)")
HEADING_SEC = re.compile(r"^#{1,6}\s.*?§(\d+(?:\.\d+)*)|^#{1,6}\s+(\d+(?:\.\d+)*)\.?\s")
SRC_RAW = re.compile(r"\[\^src:\s*(raw/[^\s\]§]+)")


class Gap:
    def __init__(self, key, line, text):
        self.key, self.line, self.text = key, line, text
        self.checked = False
        self.evidence = []          # (riga, testo) delle chiusure
        self.lines = {line}         # righe di gaps.md che appartengono al gap (per i rimandi)

    @property
    def closed(self):
        return self.checked or bool(self.evidence)


def page_index():
    idx = {}
    for p in WIKI.rglob("*.md"):
        idx.setdefault(p.stem, p)
        idx.setdefault(str(p.relative_to(WIKI))[:-3], p)
    return idx


def cites_existing_raw(page):
    for src in SRC_RAW.findall(page.read_text(encoding="utf-8", errors="replace")):
        if (ROOT / src.rstrip("`.,;)")).exists():
            return True
    return False


def adr_accepted(text_id):
    """None se l'ADR non esiste, altrimenti (path, accepted?)."""
    adr_dir = ROOT / "design_&_architecture" / "decisions"
    stems = sorted(adr_dir.glob(text_id + "*.md")) if adr_dir.is_dir() else []
    for p in stems:
        if p.stem == text_id or p.stem.startswith(text_id + "-"):
            head = p.read_text(encoding="utf-8", errors="replace").split("---")
            fm = head[1] if len(head) > 2 and not head[0].strip() else ""
            m = re.search(r"^status:\s*[\"']?([A-Za-z-]+)", fm, re.M)
            return p, bool(m) and m.group(1).lower() == "accepted"
    return None


def pattern_has_section(name, sec):
    """Il PATTERN indicato (o tutti, se il nome non e' qualificato) ha l'heading di quella sezione?"""
    if name == "PATTERN":
        files = sorted(ROOT.glob("PATTERN*.md"))
    else:
        files = [ROOT / (name if name.endswith(".md") else name + ".md")]
    for f in files:
        if not f.is_file():
            continue
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            m = HEADING_SEC.match(line)
            if m and (m.group(1) or m.group(2)) == sec:
                return f
    return None


def parse():
    gaps, by_key, current = [], {}, None
    lines = GAPS.read_text(encoding="utf-8", errors="replace").splitlines()
    for n, line in enumerate(lines, 1):
        m = ITEM.match(line)
        if m:
            ids = GAP_ID.findall(m.group(2))
            key = ids[0] if ids else f"riga-{n}"
            g = by_key.get(key)
            if g is None:
                g = Gap(key, n, m.group(2).strip())
                gaps.append(g)
                by_key[key] = g
            g.lines.add(n)
            if m.group(1).lower() == "x":
                g.checked = True
            elif m.group(1) == "CONFIRMED OPEN":
                # riapertura in coda (append-only): le chiusure scritte prima non valgono piu'
                g.checked = False
                g.evidence = []
            if CHIUSO_TITOLO.search(m.group(2)):
                g.evidence.append((n, line.strip()))
            current = g
            continue
        s = SECTION.match(line)
        if s:
            key = s.group(2)
            g = by_key.get(key) or Gap(key, n, line[3:].strip())
            if key not in by_key:
                gaps.append(g)
                by_key[key] = g
            current = g
            continue
        if line.startswith("## "):
            current = None
            continue
        cm = CLOSED_ITEM.match(line)
        if cm and not any(i in by_key for i in GAP_ID.findall(cm.group(1))):
            # voce `- [CLOSED]` che non nomina un gap gia' registrato: e' un gap a se', gia' chiuso,
            # non una chiusura del gap precedente
            ids = GAP_ID.findall(cm.group(1))
            key = ids[0] if ids else f"riga-{n}"
            g = Gap(key, n, cm.group(1).strip())
            g.evidence.append((n, line.strip()))
            gaps.append(g)
            by_key[key] = g
            current = g
            continue
        # «**Risolto:**» o «[CLOSED]» citati fra backtick sono istruzioni, non chiusure
        bare = CODE_SPAN.sub("", line)
        if RISOLTO.search(bare) or CLOSED.search(bare):
            named = [by_key[i] for i in GAP_ID.findall(line) if i in by_key and RISOLTO.search(bare) is None]
            targets = named or ([current] if current else [])
            for g in targets:
                g.evidence.append((n, line.strip()))
                g.lines.add(n)
    return gaps


def verify(g, idx):
    """(esito, [pagine/file valide], [fonti]): fonti in «raw», «ADR accepted», «PATTERN §N»."""
    if not g.closed:
        return "aperto", [], []
    if not g.evidence:
        return "solo checkbox, nessun testo di chiusura", [], []
    text = "\n".join(t for _, t in g.evidence)
    links = []
    for _, t in g.evidence:
        links += [l.strip() for l in WIKILINK.findall(t)]
        links += [p[len("wiki/"):-3] for p in WIKIPATH.findall(t)]
    links = [l for l in links if l and l != "gaps" and not l.startswith("ADR-")]
    adrs = list(dict.fromkeys(ADR_REF.findall(text)))
    secs = list(dict.fromkeys(PATTERN_REF.findall(text)))
    if not (links or adrs or secs):
        return "chiusura senza pagina della wiki", [], []
    pages, fonti, motivi = [], [], []
    wiki = [idx[l] for l in links if l in idx]
    good = [p for p in wiki if cites_existing_raw(p)]
    if links and not wiki:
        motivi.append("pagina indicata assente")
    elif links and not good:
        motivi.append("pagina senza fonte in raw/")
    if good:
        pages += good
        fonti.append("raw")
    for a in adrs:
        r = adr_accepted(a)
        if r is None:
            motivi.append("ADR indicato assente")
        elif not r[1]:
            motivi.append("ADR non accepted")
        else:
            pages.append(r[0])
            fonti.append("ADR accepted")
    for name, sec in secs:
        f = pattern_has_section(name, sec)
        if f is None:
            motivi.append("sezione PATTERN assente")
        else:
            pages.append(f)
            fonti.append(f"PATTERN §{sec}")
    if fonti:
        return "verificata", pages, list(dict.fromkeys(fonti))
    return motivi[0], [], []


def verify_all(gaps, idx):
    """{key: (esito, pagine, via, fonti)}: verify() di ogni gap, piu' i rimandi.

    Una chiusura non verificata che cita `gaps.md:<riga>` o l'ID di un altro gap la cui chiusura e'
    verificata da pagina diventa verificata `via` quel gap. Un solo passo, senza catene: un rimando
    a un rimando non conta (niente cicli, niente verifiche costruite su altre eredita')."""
    base = {g.key: verify(g, idx) for g in gaps}
    by_line = {n: g for g in gaps for n in g.lines}
    by_key = {g.key: g for g in gaps}
    out = {}
    for g in gaps:
        esito, pages, fonti = base[g.key]
        via = None
        if esito not in ("verificata", "aperto"):
            for _, text in g.evidence:
                refs = [by_line.get(int(n)) for n in RIMANDO_RIGA.findall(text)]
                refs += [by_key.get(i) for i in GAP_ID.findall(text)]
                r = next((r for r in refs if r is not None and r.key != g.key
                          and base[r.key][0] == "verificata"), None)
                if r is not None:
                    esito, pages, fonti, via = "verificata", base[r.key][1], base[r.key][2], r.key
                    break
        out[g.key] = (esito, pages, via, fonti)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tema", help="regex (case-insensitive) su ID e testo del gap")
    ap.add_argument("--elenco", action="store_true", help="una riga per gap")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check", action="store_true", help="exit 1 se ci sono chiusure non verificate")
    a = ap.parse_args(argv)

    idx = page_index()
    gaps = parse()
    esiti = verify_all(gaps, idx)       # i rimandi si risolvono su tutto il registro, prima del filtro
    if a.tema:
        rx = re.compile(a.tema, re.I)
        gaps = [g for g in gaps if rx.search(g.key) or rx.search(g.text) or any(rx.search(t) for _, t in g.evidence)]

    rows = []
    for g in gaps:
        esito, pages, via, fonti = esiti[g.key]
        stato = "aperto" if esito == "aperto" else ("chiuso" if esito == "verificata" else "chiuso-non-verificato")
        rows.append({"gap": g.key, "riga": g.line, "stato": stato, "esito": esito, "via": via, "fonti": fonti,
                     "pagine": [str(p.relative_to(ROOT)) for p in pages], "testo": g.text[:160]})

    count = {k: sum(r["stato"] == k for r in rows) for k in ("aperto", "chiuso", "chiuso-non-verificato")}
    if a.json:
        print(json.dumps({"tema": a.tema, "conteggi": count, "gap": rows}, ensure_ascii=False, indent=2))
    else:
        print(f"gap{' del tema ' + repr(a.tema) if a.tema else ''}: {len(rows)} | aperti {count['aperto']} | "
              f"chiusi e verificati {count['chiuso']} | chiusi non verificati {count['chiuso-non-verificato']}")
        motivi = {}
        for r in rows:
            if r["stato"] == "chiuso-non-verificato":
                motivi[r["esito"]] = motivi.get(r["esito"], 0) + 1
        for k, v in sorted(motivi.items(), key=lambda kv: -kv[1]):
            print(f"  non verificati — {k}: {v}")
        basi = {}
        for r in rows:
            if r["stato"] == "chiuso":
                for f in (r["fonti"] or ["via altro gap"]):
                    k = f if f == "via altro gap" else "fonte: " + f
                    basi[k] = basi.get(k, 0) + 1
        for k, v in sorted(basi.items()):
            print(f"  verificati su — {k}: {v}")
        print(f"gap da trattare come aperti (aperti + chiusi non verificati): "
              f"{count['aperto'] + count['chiuso-non-verificato']}")
        if a.elenco:
            for r in rows:
                print(f"{r['gap']:<40} gaps.md:{r['riga']:<5} {r['stato']:<22} {r['esito']}")
    return 1 if a.check and count["chiuso-non-verificato"] else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Merge driver git per un file markdown diviso in sezioni `## `.

Uso (registrato come merge driver):  python3 sprint_sections_driver.py %O %A %B
  %O base, %A nostro (qui va il risultato), %B loro.
  Exit 0 = fuso pulito; exit 1 = conflitto, marcatori scritti in %A.

Unita' di merge: il preambolo (tutto cio' che precede la prima riga `## `,
frontmatter incluso) e ciascuna sezione, che inizia con una riga `## ` e arriva
alla successiva. Le righe `###` sono contenuto della sezione. Le righe `## ` dentro
un blocco di codice recintato non aprono una sezione.

Regole per ogni unita' (chiave = titolo, riga intera; titoli ripetuti sono
distinti dal numero d'ordine):
  - invariata da un lato -> si prende l'altro;
  - cambiata in modo identico dai due lati -> una copia;
  - cambiata in modo diverso -> CONFLITTO con marcatori, mai una scelta e mai
    un merge riga per riga dentro la sezione;
  - nuova da un lato -> aggiunta; nuova dai due lati con lo stesso titolo e testo
    diverso -> conflitto;
  - cancellata da un lato e invariata dall'altro -> cancellata; cancellata da un
    lato e modificata dall'altro -> conflitto.

Ordine: quello di «nostro». Le sezioni nuove di «loro» vanno subito dopo la sezione
che le precede in «loro» (se e' presente nel risultato), oppure, se non hanno
predecessore, in testa; in entrambi i casi dopo le sezioni nuove di «nostro»
adiacenti, cosi' con due aggiunte in testa viene prima la nostra e poi la loro.

Il testo e' preservato byte per byte: nessuna normalizzazione di newline, righe
vuote o newline finale. Se nessuno dei tre file ha sezioni, o un file non e'
UTF-8, si ricade su `git merge-file -p` dichiarandolo su stderr.
"""
import re
import subprocess
import sys

OPEN = "<<<<<<< ours"
MID = "======="
CLOSE = ">>>>>>> theirs"
_LINE = re.compile(r"[^\n]*\n|[^\n]+")


def split_units(text):
    """Ritorna lista ordinata di (chiave, testo); chiave None = preambolo."""
    units = []
    key, buf = None, []
    seen = {}
    fence = None
    for line in _LINE.findall(text):
        stripped = line.lstrip(" ")
        m = re.match(r"(`{3,}|~{3,})", stripped)
        if m:
            marker = m.group(1)[0]
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
        if fence is None and line.startswith("## "):
            units.append((key, "".join(buf)))
            title = line.rstrip("\r\n")
            n = seen.get(title, 0)
            seen[title] = n + 1
            key, buf = (title, n), [line]
        else:
            buf.append(line)
    units.append((key, "".join(buf)))
    return units


def _eol(text):
    return "\r\n" if "\r\n" in text else "\n"


def _conflict(a, b, eol):
    def nl(s):
        return s if (not s or s.endswith("\n")) else s + eol
    return OPEN + eol + nl(a) + MID + eol + nl(b) + CLOSE + eol


def merge(base, ours, theirs):
    """Ritorna (testo, n_conflitti)."""
    eol = _eol(ours) if "\n" in ours else _eol(theirs)
    B = dict(split_units(base))
    ou = split_units(ours)
    th = split_units(theirs)
    O = dict(ou)
    T = dict(th)
    conflicts = 0
    resolved = {}  # chiave -> testo (o None se cancellata)

    def decide(k):
        nonlocal conflicts
        b, o, t = B.get(k), O.get(k), T.get(k)
        if o == t:
            return o
        if o == b:
            return t
        if t == b:
            return o
        conflicts += 1
        return _conflict(o or "", t or "", eol)

    for k in dict.fromkeys([k for k, _ in ou] + [k for k, _ in th]):
        resolved[k] = decide(k)

    # ordine: nostro, poi le nuove di loro
    order = [k for k, _ in ou]
    in_ours = set(order)
    # chiavi di nostro che non esistono in loro e non in base: aggiunte nostre
    ours_only_new = {k for k in order if k not in T and k not in B}
    prev = None
    for k, _ in th:
        if k in in_ours:
            prev = k
            continue
        if prev is None:
            pos = 1  # dopo il preambolo (sempre primo)
        else:
            pos = order.index(prev) + 1
        while pos < len(order) and order[pos] in ours_only_new:
            pos += 1
        order.insert(pos, k)
        in_ours.add(k)
        prev = k
    # il preambolo (None) e' sempre primo
    out = "".join(resolved[k] for k in order if resolved.get(k) is not None)
    return out, conflicts


def fallback(base_p, ours_p, theirs_p, why):
    sys.stderr.write("sprint_sections_driver: %s; uso git merge-file standard\n" % why)
    r = subprocess.run(
        ["git", "merge-file", "-p", "-L", "ours", "-L", "base", "-L", "theirs",
         ours_p, base_p, theirs_p],
        capture_output=True,
    )
    if r.returncode < 0 or r.returncode > 127:
        sys.stderr.write("sprint_sections_driver: git merge-file fallito\n")
        return 2
    with open(ours_p, "wb") as f:
        f.write(r.stdout)
    return 1 if r.returncode > 0 else 0


def main(argv):
    if len(argv) != 4:
        sys.stderr.write("uso: sprint_sections_driver.py BASE OURS THEIRS\n")
        return 2
    base_p, ours_p, theirs_p = argv[1:4]
    raw = []
    for p in (base_p, ours_p, theirs_p):
        with open(p, "rb") as f:
            raw.append(f.read())
    try:
        base, ours, theirs = (r.decode("utf-8") for r in raw)
    except UnicodeDecodeError:
        return fallback(base_p, ours_p, theirs_p, "file non UTF-8")
    if all(len(split_units(t)) == 1 for t in (base, ours, theirs)):
        return fallback(base_p, ours_p, theirs_p, "nessuna sezione `## `")
    text, n = merge(base, ours, theirs)
    with open(ours_p, "wb") as f:
        f.write(text.encode("utf-8"))
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

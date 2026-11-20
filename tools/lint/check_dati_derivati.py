#!/usr/bin/env python3
"""Check 4bf e 4bg — dati append-only e derivati che non si correggono a mano.

4bf — ordine delle voci di `wiki/log.md`. Il merge union (`.gitattributes`) concatena le voci
aggiunte in coda da due branch: ogni lato e' in ordine, ma l'insieme puo' non esserlo. Il check
legge la data di ogni voce (`date:` dei blocchi `---`, o `## AAAA-MM-GG` delle voci a titolo) e
segnala una voce piu' vecchia di oltre `--tolleranza` giorni rispetto alla piu' recente che la
precede (default 7: il log e' in ordine di scrittura e due chat in parallelo si sovrappongono di
qualche giorno senza che nulla sia rotto). Entro la tolleranza lo scarto e' solo conteggiato.
Severita' ERROR.

Esenzioni per voce: `tools/lint/log-ordine-esenzioni.txt`, una riga `AAAA-MM-GG <impronta> <motivo>`.
L'impronta (12 hex) e' lo SHA-256 del testo della voce, dalla sua intestazione all'inizio della
voce successiva: non dipende dal numero di riga e copre solo quella voce. Il motivo e' obbligatorio.
Una voce esentata non entra nel confronto e non sposta la data massima. Un'esenzione senza motivo
e' ignorata (WARNING `esenzione-senza-motivo`); una che non trova piu' la sua voce e' WARNING
`esenzione-orfana`. `--impronte` stampa l'impronta delle voci fuori tolleranza, per scriverne una.

4bg — contatore «## Sources (N)» di `wiki/index.md`. N e' il numero delle voci `- [[...]]` della
sezione, calcolato qui; uno scarto e' WARNING con i due valori (la correzione e' del wiki-keeper).

Uso:
    python3 tools/lint/check_dati_derivati.py [--json] [--strict] [--tolleranza N] [<root>]
Exit code: 0 anche con finding; con --strict 1 se c'e' almeno un finding.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re

DATA_BLOCCO = re.compile(r"^---\s*\n(?:[^\n]*\n)??date:\s*(\d{4}-\d{2}-\d{2})", re.M)
DATA_TITOLO = re.compile(r"^##\s+\[?(\d{4}-\d{2}-\d{2})", re.M)
SOURCES_TITOLO = re.compile(r"^##\s+Sources\s*\((\d+)\)\s*$", re.M)
VOCE_INDEX = re.compile(r"^- \[\[", re.M)
ESENZIONI = pathlib.Path("tools") / "lint" / "log-ordine-esenzioni.txt"
RIGA_ESENZIONE = re.compile(r"^(\d{4}-\d{2}-\d{2})\s+([0-9a-f]{12})(?:\s+(.*\S))?\s*$")


def _voci(testo: str) -> list[tuple[int, str, str]]:
    """(numero di riga, data, impronta) per ogni voce del log, in ordine di file."""
    trovate = []
    for rx in (DATA_BLOCCO, DATA_TITOLO):
        for m in rx.finditer(testo):
            trovate.append((m.start(1), m.start(), m.group(1)))
    trovate.sort()
    out = []
    for i, (pos, inizio, d) in enumerate(trovate):
        fine = trovate[i + 1][1] if i + 1 < len(trovate) else len(testo)
        impronta = hashlib.sha256(testo[inizio:fine].encode("utf-8")).hexdigest()[:12]
        out.append((testo.count("\n", 0, pos) + 1, d, impronta))
    return out


def date_voci(testo: str) -> list[tuple[int, str]]:
    """(numero di riga, data) per ogni voce del log, in ordine di file."""
    return [(riga, d) for riga, d, _ in _voci(testo)]


def leggi_esenzioni(root: pathlib.Path) -> tuple[dict, list[dict]]:
    """({(data, impronta): motivo}, finding sulle righe senza motivo)."""
    f = root / ESENZIONI
    esenzioni, finding = {}, []
    if not f.is_file():
        return esenzioni, finding
    for n, riga in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
        riga = riga.strip()
        if not riga or riga.startswith("#"):
            continue
        m = RIGA_ESENZIONE.match(riga)
        if not m or not m.group(3):
            finding.append({"check": "4bf", "codice": "esenzione-senza-motivo", "riga_file": n})
            continue
        esenzioni[(m.group(1), m.group(2))] = m.group(3)
    return esenzioni, finding


def check_ordine_log(root: pathlib.Path, tolleranza: int,
                     stato: dict | None = None) -> tuple[list[dict], int]:
    """(finding, scarti entro la tolleranza). `stato` riceve esentate e avvisi sulle esenzioni."""
    log = root / "wiki" / "log.md"
    stato = stato if stato is not None else {}
    stato.update(esentate=[], avvisi=[])
    if not log.is_file():
        return [], 0
    esenzioni, stato["avvisi"] = leggi_esenzioni(root)
    usate = set()
    findings, entro = [], 0
    massima = None
    for riga, data, impronta in _voci(log.read_text(encoding="utf-8")):
        if (data, impronta) in esenzioni:
            usate.add((data, impronta))
            stato["esentate"].append({"riga": riga, "data": data, "impronta": impronta,
                                      "motivo": esenzioni[(data, impronta)]})
            continue
        d = dt.date.fromisoformat(data)
        if massima is not None and d < massima[0]:
            scarto = (massima[0] - d).days
            if scarto > tolleranza:
                findings.append({"check": "4bf", "riga": riga, "data": data, "impronta": impronta,
                                 "precedente": massima[0].isoformat(), "riga_precedente": massima[1],
                                 "giorni": scarto})
            else:
                entro += 1
        if massima is None or d >= massima[0]:
            massima = (d, riga)
    for (data, impronta) in sorted(set(esenzioni) - usate):
        stato["avvisi"].append({"check": "4bf", "codice": "esenzione-orfana", "data": data,
                                "impronta": impronta})
    return findings, entro


def check_contatore_sources(root: pathlib.Path) -> dict | None:
    index = root / "wiki" / "index.md"
    if not index.is_file():
        return None
    testo = index.read_text(encoding="utf-8")
    m = SOURCES_TITOLO.search(testo)
    if not m:
        return None
    resto = testo[m.end():]
    fine = re.search(r"^## ", resto, re.M)
    sezione = resto[:fine.start()] if fine else resto
    reale = len(VOCE_INDEX.findall(sezione))
    dichiarato = int(m.group(1))
    if dichiarato == reale:
        return None
    return {"check": "4bg", "dichiarato": dichiarato, "reale": reale, "scarto": reale - dichiarato}


def main() -> int:
    ap = argparse.ArgumentParser(description="Check 4bf/4bg — ordine di wiki/log.md e contatore Sources")
    ap.add_argument("root", nargs="?", default=".", help="root della factory (default: .)")
    ap.add_argument("--json", action="store_true", help="output machine-readable")
    ap.add_argument("--strict", action="store_true", help="exit 1 se ci sono finding")
    ap.add_argument("--tolleranza", type=int, default=7,
                    help="giorni di retrodatazione tollerati fra voci del log (default 7)")
    ap.add_argument("--impronte", action="store_true",
                    help="stampa data e impronta delle voci fuori tolleranza (per scriverne l'esenzione)")
    args = ap.parse_args()

    root = pathlib.Path(args.root).resolve()
    stato: dict = {}
    ordine, entro = check_ordine_log(root, args.tolleranza, stato)
    sources = check_contatore_sources(root)
    avvisi = stato["avvisi"]
    findings = ordine + avvisi + ([sources] if sources else [])

    if args.impronte:
        for f in ordine:
            print(f"{f['data']} {f['impronta']} <motivo>   # wiki/log.md riga {f['riga']}")
        return 0
    if args.json:
        print(json.dumps({"check": "4bf-4bg", "entro_tolleranza": entro, "esentate": stato["esentate"],
                          "findings": findings}, indent=2, ensure_ascii=False))
    elif not findings:
        esentate = f", {len(stato['esentate'])} voci esentate" if stato["esentate"] else ""
        print(f"[4bf-4bg] OK — ordine di wiki/log.md entro {args.tolleranza} giorni "
              f"({entro} retrodatazioni tollerate{esentate}), contatore Sources coerente")
    else:
        if ordine:
            print("## ERROR (ordine di wiki/log.md)")
            for f in ordine:
                print(f"- [ERROR][log-ordine-rotto][4bf] wiki/log.md riga {f['riga']}: voce del {f['data']} "
                      f"dopo una del {f['precedente']} (riga {f['riga_precedente']}), {f['giorni']} giorni "
                      f"oltre la tolleranza di {args.tolleranza}. Il log e' in ordine di scrittura: "
                      f"controlla il merge union e la data della voce.")
        if avvisi:
            print("## WARNING (esenzioni dell'ordine del log)")
            for a in avvisi:
                if a["codice"] == "esenzione-orfana":
                    print(f"- [WARNING][esenzione-orfana][4bf] {ESENZIONI}: {a['data']} {a['impronta']} "
                          f"non corrisponde a nessuna voce di wiki/log.md: togliere la riga.")
                else:
                    print(f"- [WARNING][esenzione-senza-motivo][4bf] {ESENZIONI} riga {a['riga_file']}: "
                          f"serve «AAAA-MM-GG <impronta> <motivo>»; la riga e' ignorata.")
        if sources:
            print("## WARNING (contatore del catalogo)")
            print(f"- [WARNING][sources-contatore][4bg] wiki/index.md: «## Sources ({sources['dichiarato']})» "
                  f"ma la sezione elenca {sources['reale']} voci (scarto {sources['scarto']:+d}). "
                  f"Aggiornare il contatore (wiki-keeper).")
        print(f"\nTotale: {len(findings)} finding")
    return 1 if findings and args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())

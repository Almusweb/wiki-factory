#!/usr/bin/env python3
"""design_w1_misure.py — misure W1 del layer analisi-design (EP-097, US-383).

Misure una tantum, ripetibili, richieste dalla Tavola Rotonda 5c1d9a7e (Accordo D8) prima di
accendere `design_traceability`. Leggono solo git e i file: nessun LLM, nessuna scrittura salvo
`--out`.

  (a) tenuta dell'OK in chat al design. Per ogni ADR in design_&_architecture/decisions/:
      - stato al primo commit (accepted gia' alla nascita = OK dato in chat prima di scrivere,
        nessuna revisione tracciata in git);
      - sezione «## Decisione…» modificata in un commit successivo al primo in cui l'ADR e'
        `accepted` (testo normalizzato: spazi finali e righe vuote multiple non contano).
      ok_chat_rate = quota di ADR nati `accepted` la cui Decisione non e' piu' cambiata.
  (c) premortem pre-TPM: quota di ADR col campo `premortem: {data, report, esito}` nel frontmatter e,
      fra questi, quanti hanno esito `modificato` o `ritirato` (la Decisione e' cambiata dopo il premortem).
  (b) disciplina di `updated:` nelle pagine wiki: scarto in giorni fra il campo `updated:` e la
      data dell'ultimo commit del file; quota con scarto > 0 e > 7 giorni.

Cosa NON misura: se la Decisione era giusta; se l'utente ha letto il design prima dell'OK (la
chat non e' in git); modifiche cosmetiche dentro la sezione Decisione contano come modifiche.

USO:
  python3 tools/analytics/design_w1_misure.py [--root R] [--json] [--out wiki/lint/<data>-w1-design.md]
Solo stdlib + git. Read-only salvo --out.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import subprocess
import sys

ADR_DIR = "design_&_architecture/decisions"
SEZ_DECISIONE = re.compile(r"^##\s+(?:\d+\.\s*)?Decision[ei]\b.*?$(.*?)(?=^##\s|\Z)", re.M | re.S)
STATUS = re.compile(r"^status:\s*['\"]?([A-Za-z_-]+)", re.M)
PREMORTEM = re.compile(r"^premortem:\s*\{[^}\n]*\besito:\s*['\"]?(invariato|modificato|ritirato)\b", re.M)
UPDATED = re.compile(r"^updated:\s*['\"]?(\d{4}-\d{2}-\d{2})", re.M)


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout


def norm(testo):
    righe = [r.rstrip() for r in testo.strip().splitlines()]
    return re.sub(r"\n{2,}", "\n", "\n".join(righe))


def decisione(testo):
    m = SEZ_DECISIONE.search(testo or "")
    return norm(m.group(1)) if m else None


def frontmatter(testo):
    if not testo.startswith("---"):
        return ""
    fine = testo.find("\n---", 3)
    return testo[:fine] if fine > 0 else ""


def misura_adr(root):
    righe = []
    for p in sorted((root / ADR_DIR).glob("ADR-*.md")):
        rel = p.relative_to(root).as_posix()
        commits = git(root, "log", "--follow", "--format=%H", "--reverse", "--", rel).split()
        if not commits:
            continue
        versioni = []
        for c in commits:
            t = git(root, "show", f"{c}:{rel}")
            if not t:  # rinomina: il path era diverso in quel commit
                nomi = git(root, "show", "--name-only", "--format=", c).split("\n")
                alt = next((n for n in nomi if n.endswith(p.name)), None)
                t = git(root, "show", f"{c}:{alt}") if alt else ""
            s = STATUS.search(frontmatter(t))
            versioni.append((c, s.group(1).lower() if s else None, decisione(t)))
        nato = versioni[0][1]
        idx_acc = next((i for i, v in enumerate(versioni) if v[1] == "accepted"), None)
        cambi = 0
        # revisione prima dell'OK: Decisione diversa fra la prima versione e quella accettata
        rivista = (idx_acc is not None and idx_acc > 0 and versioni[0][2] is not None
                   and versioni[idx_acc][2] != versioni[0][2])
        if idx_acc is not None:
            base = versioni[idx_acc][2]
            for _, _, d in versioni[idx_acc + 1:]:
                if d is not None and base is not None and d != base:
                    cambi += 1
                    base = d
        pm = PREMORTEM.search(frontmatter(p.read_text(encoding="utf-8", errors="replace")))
        righe.append({"adr": p.stem, "premortem": pm.group(1) if pm else None, "commit": len(commits), "stato_nascita": nato,
                      "accepted_in_commit": None if idx_acc is None else idx_acc + 1,
                      "ha_sezione_decisione": versioni[-1][2] is not None,
                      "decisione_rivista_prima_di_accepted": rivista,
                      "decisione_cambiata_dopo_accepted": cambi})
    return righe


def misura_updated(root):
    righe = []
    for p in sorted((root / "wiki").rglob("*.md")):
        rel = p.relative_to(root).as_posix()
        m = UPDATED.search(frontmatter(p.read_text(encoding="utf-8", errors="replace")))
        if not m:
            continue
        ultimo = git(root, "log", "-1", "--format=%cs", "--", rel).strip()
        if not ultimo:
            continue
        scarto = (dt.date.fromisoformat(ultimo) - dt.date.fromisoformat(m.group(1))).days
        righe.append({"pagina": rel, "updated": m.group(1), "ultimo_commit": ultimo, "scarto_giorni": scarto})
    return righe


def sintesi(adr, upd):
    accettati = [r for r in adr if r["accepted_in_commit"] is not None]
    nati_acc = [r for r in adr if r["stato_nascita"] == "accepted"]
    tenuti = [r for r in nati_acc if r["decisione_cambiata_dopo_accepted"] == 0]
    cambiati = [r for r in accettati if r["decisione_cambiata_dopo_accepted"] > 0]
    nati_prop = [r for r in accettati if r["stato_nascita"] != "accepted"]
    rivisti = [r for r in nati_prop if r["decisione_rivista_prima_di_accepted"]]
    n_upd = len(upd)
    con_pm = [r for r in adr if r.get("premortem")]
    pm_cambiati = [r for r in con_pm if r["premortem"] in ("modificato", "ritirato")]
    def quota(k, n):
        return round(k / n, 3) if n else None
    return {
        "n_adr": len(adr), "n_adr_accepted": len(accettati),
        "n_adr_nati_accepted": len(nati_acc),
        "ok_chat_rate": quota(len(tenuti), len(nati_acc)),
        "quota_nati_accepted": quota(len(nati_acc), len(adr)),
        "n_nati_proposed": len(nati_prop),
        "n_rivisti_prima_di_accepted": len(rivisti),
        "quota_rivisti_prima_di_accepted": quota(len(rivisti), len(nati_prop)),
        "n_decisione_cambiata_dopo_accepted": len(cambiati),
        "quota_decisione_cambiata": quota(len(cambiati), len(accettati)),
        "adr_decisione_cambiata": [r["adr"] for r in cambiati],
        "adr_senza_sezione_decisione": [r["adr"] for r in adr if not r["ha_sezione_decisione"]],
        "n_con_premortem": len(con_pm), "quota_con_premortem": quota(len(con_pm), len(adr)),
        "n_premortem_decisione_cambiata": len(pm_cambiati),
        "n_pagine_updated": n_upd,
        "quota_updated_scarto_gt0": quota(sum(1 for r in upd if r["scarto_giorni"] > 0), n_upd),
        "quota_updated_scarto_gt7": quota(sum(1 for r in upd if r["scarto_giorni"] > 7), n_upd),
        "quota_updated_nel_futuro": quota(sum(1 for r in upd if r["scarto_giorni"] < 0), n_upd),
    }


def report(s, oggi, sha):
    fm = ["---", "type: lint-report", "report: w1-design", f"date: {oggi}", f"base_commit: {sha}",
          f"n: {s['n_adr']}", f"ok_chat_rate: {s['ok_chat_rate']}",
          f"quota_decisione_cambiata: {s['quota_decisione_cambiata']}",
          f"quota_rivisti_prima_di_accepted: {s['quota_rivisti_prima_di_accepted']}",
          f"quota_con_premortem: {s['quota_con_premortem']}",
          f"n_pagine_updated: {s['n_pagine_updated']}",
          f"quota_updated_scarto_gt7: {s['quota_updated_scarto_gt7']}", "---", ""]
    corpo = [
        f"# Misure W1 del layer analisi-design — {oggi}", "",
        "Prodotto da `python3 tools/analytics/design_w1_misure.py` sul commit "
        f"`{sha}` (EP-097 US-383, Accordo D8 della Tavola Rotonda 5c1d9a7e).", "",
        "## (a) Tenuta dell'OK in chat al design", "",
        f"- ADR letti: **{s['n_adr']}**; arrivati ad `accepted`: **{s['n_adr_accepted']}**.",
        f"- Nati gia' `accepted` al primo commit: **{s['n_adr_nati_accepted']}** "
        f"(quota {s['quota_nati_accepted']}). Per questi l'OK e' stato dato in chat prima di scrivere: "
        "git non conserva alcuna revisione.",
        f"- `ok_chat_rate` (nati accepted con Decisione mai cambiata dopo): **{s['ok_chat_rate']}**.",
        f"- Nati `proposed` e poi accettati: **{s['n_nati_proposed']}**; di questi, con la Decisione "
        f"riscritta fra la prima versione e quella accettata: **{s['n_rivisti_prima_di_accepted']}** "
        f"(quota {s['quota_rivisti_prima_di_accepted']}). E' l'unica traccia in git di una revisione prima dell'OK.",
        f"- ADR con la sezione Decisione cambiata dopo `accepted`: **{s['n_decisione_cambiata_dopo_accepted']}** "
        f"(quota {s['quota_decisione_cambiata']}): {', '.join(s['adr_decisione_cambiata']) or 'nessuno'}.",
        f"- ADR senza una sezione «## Decisione…» riconoscibile: {', '.join(s['adr_senza_sezione_decisione']) or 'nessuno'}.",
        "", "## (c) Premortem pre-TPM", "",
        f"- ADR con `premortem:` registrato: **{s['n_con_premortem']}** su {s['n_adr']} "
        f"(quota {s['quota_con_premortem']}); con esito `modificato` o `ritirato`: "
        f"**{s['n_premortem_decisione_cambiata']}**.",
        "", "## (b) Disciplina di `updated:` nella wiki", "",
        f"- Pagine con `updated:` e almeno un commit: **{s['n_pagine_updated']}**.",
        f"- Scarto ultimo commit − updated > 0 giorni: **{s['quota_updated_scarto_gt0']}**; "
        f"> 7 giorni: **{s['quota_updated_scarto_gt7']}**; updated nel futuro: {s['quota_updated_nel_futuro']}.",
        "", "## Cosa NON dimostrano", "",
        "- Un ok_chat_rate alto non dice che il design fosse giusto, ne' che l'OK sia stato dato dopo "
        "una lettura: dice solo che la Decisione non e' stata riscritta. Un gate che approva tutto "
        "e uno che approva solo cose giuste producono lo stesso numero.",
        "- Una modifica alla Decisione puo' essere un refuso: la misura conta il testo, non il significato.",
        "- La quota su `updated:` misura la disciplina del campo, non la freschezza dei contenuti.", "",
    ]
    return "\n".join(fm + corpo)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=str(pathlib.Path(__file__).resolve().parents[2]))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--oggi", default=dt.date.today().isoformat())
    a = ap.parse_args(argv)
    root = pathlib.Path(a.root).resolve()
    adr, upd = misura_adr(root), misura_updated(root)
    s = sintesi(adr, upd)
    sha = git(root, "rev-parse", "--short", "HEAD").strip()
    if a.json:
        print(json.dumps({"sintesi": s, "adr": adr}, indent=2, ensure_ascii=False))
    else:
        testo = report(s, a.oggi, sha)
        print(testo)
        if a.out:
            dest = pathlib.Path(a.out)
            dest = dest if dest.is_absolute() else root / dest
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(testo + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    import sys as _sys
    for _s in (_sys.stdout, _sys.stderr):  # console Windows cp1252: forza utf-8
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    sys.exit(main())

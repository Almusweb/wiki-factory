#!/usr/bin/env python3
"""Check 4bk — gli agenti che leggono contenuto non fidato non dichiarano `Bash` nei `tools:`.

Un agente e' un «lettore di contenuto non fidato» se ha, nel frontmatter `capabilities:`, la voce `raw-sync`
oppure una voce che termina in `-extraction` (gli agenti di ingest), oppure se e' elencato in
`ingest_agent_tools.agenti` (factory.config.yaml): dal 2026-11-18 (EP-108 US-419) ci sono gli operatori
che leggono log, righe di database e codice del cliente. Esclusi dichiarati: i dev-agent e `code-reviewer`,
che leggono codice del cliente e hanno `Bash` per definizione del ruolo.
Se dichiara `Bash` in `tools:` e non ha un'eccezione valida, e' un finding. Le eccezioni stanno in
`ingest_agent_tools.exceptions` (`agente`, `motivo`, `scade` AAAA-MM-GG): una eccezione scaduta vale
come assente; un agente del gruppo non elencato e' coperto da nulla e si segnala.

Severita': WARNING; ERROR solo se `ingest_agent_tools.required_from` e' presente ed e' <= oggi.

Non garantisce: legge i `tools:` DICHIARATI, non quelli effettivi (permission mode, approvazioni e
`settings.local.json` li scavalcano); l'elenco dei lettori di contenuto non fidato e' una convenzione sulle
capability; la regola «raw/ e' dato non fidato» e' una mitigazione comportamentale, non un controllo.

Uso:
    python3 tools/lint/check-ingest-agent-tools.py [--root <factory>] [--oggi AAAA-MM-GG] [--json] [--strict]
Exit code: 0 anche con finding; con --strict 1 se c'e' almeno un ERROR.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

DATA = re.compile(r"^\d{4}-\d{2}-\d{2}$")


NON_LEGGIBILE = "non verificabile: PyYAML assente, eccezioni non lette"


def frontmatter(testo):
    """Campi name, tools, capabilities del frontmatter, letti con sola stdlib (righe semplici)."""
    m = re.match(r"^---\r?\n(.*?)\r?\n---", testo, re.S)
    if not m:
        return {}
    fm, caps, in_caps = {}, [], False
    for riga in m.group(1).splitlines():
        if in_caps:
            c = re.match(r"^\s+-\s*([^\s#]+)", riga)
            if c:
                caps.append(c.group(1).strip("\"'"))
                continue
            if not riga.strip() or riga.lstrip().startswith("#"):
                continue
            in_caps = False
        k = re.match(r"^(name|tools|capabilities):\s*(.*?)\s*$", riga)
        if not k:
            continue
        chiave, val = k.group(1), re.sub(r"\s+#.*$", "", k.group(2))
        if chiave == "capabilities":
            in_caps = not val
            if val.startswith("["):
                caps = [x.strip().strip("\"'") for x in val.strip("[]").split(",") if x.strip()]
        elif chiave == "tools":
            fm["tools"] = [x.strip().strip("\"'") for x in val.strip("[]").split(",") if x.strip()]
        else:
            fm["name"] = val.strip("\"'")
    fm["capabilities"] = caps
    return fm


def _blocco_presente(root):
    cfg = pathlib.Path(root) / "factory.config.yaml"
    if not cfg.exists():
        return False
    return bool(re.search(r"^ingest_agent_tools:", cfg.read_text(encoding="utf-8", errors="replace"), re.M))


def configurazione(root):
    cfg = pathlib.Path(root) / "factory.config.yaml"
    if not cfg.exists() or yaml is None:
        return {}
    try:
        d = yaml.safe_load(cfg.read_text(encoding="utf-8", errors="replace")) or {}
    except yaml.YAMLError:
        return {}
    blocco = d.get("ingest_agent_tools") if isinstance(d, dict) else None
    return blocco if isinstance(blocco, dict) else {}


def e_ingest(fm, nome, espliciti):
    caps = [str(c) for c in (fm.get("capabilities") or [])]
    return nome in espliciti or any(c == "raw-sync" or c.endswith("-extraction") for c in caps)


def check(root, oggi):
    """Elenco dei finding {agente, motivo}."""
    cfg = configurazione(root)
    espliciti = {str(a) for a in (cfg.get("agenti") or [])}
    eccezioni = {}
    for e in cfg.get("exceptions") or []:
        if isinstance(e, dict) and e.get("agente"):
            eccezioni[str(e["agente"])] = str(e.get("scade") or "")
    out = []
    if yaml is None and _blocco_presente(root):
        out.append({"agente": "*", "motivo": NON_LEGGIBILE, "nonverificabile": True})
        return out
    dir_agenti = pathlib.Path(root) / ".claude" / "agents"
    for f in sorted(dir_agenti.glob("*.md")) if dir_agenti.is_dir() else []:
        fm = frontmatter(f.read_text(encoding="utf-8", errors="replace"))
        tools = fm.get("tools") or []
        nome = str(fm.get("name") or f.stem)
        if "Bash" not in [str(t) for t in tools] or not e_ingest(fm, nome, espliciti):
            continue
        scade = eccezioni.get(nome)
        if scade is None:
            out.append({"agente": nome, "motivo": "legge contenuto non fidato, dichiara Bash e non ha eccezione"})
        elif not DATA.match(scade):
            out.append({"agente": nome, "motivo": "eccezione senza data di scadenza valida (scade: %r)" % scade})
        elif scade < oggi:
            out.append({"agente": nome, "motivo": "eccezione scaduta il %s" % scade})
    return out


def _required_from(root):
    if yaml is not None:
        return str(configurazione(root).get("required_from") or "")
    cfg = pathlib.Path(root) / "factory.config.yaml"
    if not cfg.exists():
        return ""
    in_b = False
    for riga in cfg.read_text(encoding="utf-8", errors="replace").splitlines():
        if re.match(r"^ingest_agent_tools:", riga):
            in_b = True
        elif in_b and riga.strip() and not riga.startswith((" ", "\t", "#")):
            break
        elif in_b:
            m = re.match(r"^\s+required_from:\s*[\"']?(\d{4}-\d{2}-\d{2})", riga)
            if m:
                return m.group(1)
    return ""


def severita(root, oggi, findings=()):
    if findings and all(x.get("nonverificabile") for x in findings):
        return "WARNING"
    since = _required_from(root)
    return "ERROR" if DATA.match(since) and since <= oggi else "WARNING"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Check 4bk — lettori di contenuto non fidato con Bash")
    ap.add_argument("root", nargs="?", default=None)
    ap.add_argument("--root", dest="root_opt", default=None)
    ap.add_argument("--oggi", default=None, help="data di riferimento AAAA-MM-GG (default: oggi)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.root_opt or args.root or ".").resolve()
    oggi = args.oggi or dt.date.today().isoformat()
    v = check(root, oggi)
    sev = severita(root, oggi, v)
    if args.json:
        print(json.dumps({"check": "4bk", "severita": sev, "findings": v}, indent=2, ensure_ascii=False))
    elif not v:
        print("[4bk] OK — nessun lettore di contenuto non fidato con Bash fuori da eccezioni valide")
    else:
        print("## %s (lettori di contenuto non fidato con Bash)" % sev)
        for x in v:
            dove = "factory.config.yaml" if x["agente"] == "*" else ".claude/agents/%s.md" % x["agente"]
            print("- [%s][ingest-tools][4bk] %s: %s" % (sev, dove, x["motivo"]))
        print("\nTotale: %d agenti" % len(v))
    return 1 if v and sev == "ERROR" and args.strict else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
cost_alert.py — controllo dei costi in token dell'operatore contro le regole di
analytics/alert-rules.yaml (deterministico, no LLM).

Fonte del costo: i transcript JSONL di Claude Code di questa macchina per il progetto
corrente (~/.claude/projects/<cwd-mangled>/), sessione principale + subagents/, più le
cartelle del checkout principale e dei worktree della factory (vedi transcript_dirs).
Il conteggio per risposta API riusa parse_responses di harvest-session-tokens.py
(una riga per content block → una risposta per message.id); i prezzi vengono da
analytics/pricing.yaml tramite load_pricing di show-session-tokens.py.
I transcript sono per macchina, quindi il costo è quello dell'operatore che la usa:
non dipende dall'event store, che si popola solo con un harvest esplicito.

USO:
  cost_alert.py check [--period session|daily|weekly|monthly|all] [--session-id <uuid>]
                      [--record [--note <testo>]] [--json | --compact | --gate]
  cost_alert.py breakdown --period session|daily|weekly|monthly [--top N] [--json]
  cost_alert.py reconcile [--period session|daily|weekly|monthly] [--session-id <uuid>]
                          [--transcripts-root <dir>] [--json]
  cost_alert.py pending [--json]
  cost_alert.py ack (--id <alert_id> | --all)
  cost_alert.py status-line --cost <usd>      # suffisso per la statusLine, vuoto se nulla da dire

CONFIG:
  factory.config.yaml → analytics.cost_alert.{enabled, agent, rules_file, alerts_dir}
  factory.config.yaml → analytics.reconcile.{underestimate_threshold, worktree_aliases}
  analytics/alert-rules.yaml → rules: [{period, threshold_usd, action, notes?, operator?}]
    period ∈ session | daily | weekly | monthly ; action ∈ warn | escalate ; threshold_usd > 0
  analytics/alert-rules.yaml → plans: {<id>: {label, license_usd_month, central_funding_usd_month,
                                              included_usd, included_period, action?}}
                             → subscriptions: [{operator, plan}]
    Il piano dell'operatore genera una regola sulla quota inclusa (included_usd per
    included_period) e la stima di addebito sul centro di costo: quota fissa mensile più eccedenza.

RECORD (solo `check --record`, path escalate): analytics/alerts/<alert_id>.json, locale
(gitignored), uno per operatore e finestra; ri-eseguire aggiorna il costo e conserva l'ack.

RECONCILE: confronta lo store (analytics/events) con i transcript dell'operatore sotto
--transcripts-root, con e senza le letture dalla cache, e dichiara l'etichetta
affidabile | sottostima | non verificabile (stessa etichetta in `check` e `breakdown`).

EXIT: 0 sempre (fail-open: errori e config mancante finiscono in `notes`), 2 su argomenti
non validi o listino presente ma non caricato; `reconcile` esce 1 se le letture sono incomplete.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

PERIODS = ("session", "daily", "weekly", "monthly")
PLAN_PERIODS = ("weekly", "monthly")
ACTIONS = ("warn", "escalate")
PERIOD_LABEL = {"session": "sessione", "daily": "giorno", "weekly": "settimana",
                "monthly": "mese"}
NEAR_RATIO = 0.8  # soglia di preavviso mostrata dalla statusLine

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]


def _load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


_harvest = _load_module("harvest_session_tokens", "harvest-session-tokens.py")
_ledger = _load_module("show_session_tokens", "show-session-tokens.py")


# ---------------------------------------------------------------------------
# Config e regole
# ---------------------------------------------------------------------------

def _yaml_load(path: Path):
    import yaml  # type: ignore
    loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    with open(path, encoding="utf-8") as fh:
        return yaml.load(fh, Loader=loader)


def load_config(root: Path) -> dict:
    cfg = (((_yaml_load(root / "factory.config.yaml") or {}).get("analytics") or {})
           .get("cost_alert") or {})
    return {
        "enabled": cfg.get("enabled") is True,
        "agent": cfg.get("agent") is True,
        "rules_file": cfg.get("rules_file") or "analytics/alert-rules.yaml",
        "alerts_dir": cfg.get("alerts_dir") or "analytics/alerts",
    }


def load_rules(path: Path) -> tuple[list[dict], list[str]]:
    """Regole valide + errori di validazione (le regole non valide vengono scartate)."""
    if not path.exists():
        return [], [f"file regole assente: {path.name}"]
    data = _yaml_load(path) or {}
    rules, errors = [], []
    for i, r in enumerate(data.get("rules") or [], 1):
        if not isinstance(r, dict):
            errors.append(f"regola {i}: non è una mappa")
            continue
        period, action, thr = r.get("period"), r.get("action"), r.get("threshold_usd")
        if period not in PERIODS:
            errors.append(f"regola {i}: period '{period}' non ammesso ({'|'.join(PERIODS)})")
            continue
        if action not in ACTIONS:
            errors.append(f"regola {i}: action '{action}' non ammessa ({'|'.join(ACTIONS)})")
            continue
        if isinstance(thr, bool) or not isinstance(thr, (int, float)) or thr <= 0:
            errors.append(f"regola {i}: threshold_usd deve essere un numero > 0")
            continue
        op = r.get("operator")
        if op is not None and (not isinstance(op, str) or not op.strip()):
            errors.append(f"regola {i}: operator deve essere il nome git dell'operatore")
            continue
        rules.append({"period": period, "action": action, "threshold_usd": float(thr),
                      "notes": str(r.get("notes") or ""), "operator": (op or "").strip()})
    return rules, errors


def _usd(value) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float)) and value >= 0


def load_plans(path: Path) -> tuple[dict, dict, list[str]]:
    """Piani di abbonamento, assegnazione operatore → piano, errori di validazione.
    Un piano non valido viene scartato e le assegnazioni che lo citano restano senza piano."""
    if not path.exists():
        return {}, {}, []
    data = _yaml_load(path) or {}
    plans, subs, errors = {}, {}, []
    for pid, p in (data.get("plans") or {}).items():
        if not isinstance(p, dict):
            errors.append(f"piano {pid}: non è una mappa")
            continue
        fields = ("license_usd_month", "central_funding_usd_month", "included_usd")
        bad = [f for f in fields if not _usd(p.get(f))]
        if bad:
            errors.append(f"piano {pid}: {', '.join(bad)} deve essere un numero >= 0")
            continue
        if p.get("included_period") not in PLAN_PERIODS:
            errors.append(f"piano {pid}: included_period '{p.get('included_period')}' non "
                          f"ammesso ({'|'.join(PLAN_PERIODS)})")
            continue
        action = p.get("action") or "escalate"
        if action not in ACTIONS:
            errors.append(f"piano {pid}: action '{action}' non ammessa ({'|'.join(ACTIONS)})")
            continue
        license_usd, funding = float(p["license_usd_month"]), float(p["central_funding_usd_month"])
        plans[str(pid)] = {
            "id": str(pid), "label": str(p.get("label") or pid),
            "license_usd_month": license_usd, "central_funding_usd_month": funding,
            # il finanziamento centrale copre prima la licenza: il resto è la quota fissa
            "fixed_usd_month": max(0.0, license_usd - funding),
            "included_usd": float(p["included_usd"]),
            "included_period": p["included_period"], "action": action,
        }
    for i, s in enumerate(data.get("subscriptions") or [], 1):
        op = s.get("operator") if isinstance(s, dict) else None
        pid = s.get("plan") if isinstance(s, dict) else None
        if not isinstance(op, str) or not op.strip() or not isinstance(pid, str):
            errors.append(f"abbonamento {i}: servono operator (nome git) e plan")
            continue
        if pid not in plans:
            errors.append(f"abbonamento {i}: piano '{pid}' non definito o non valido")
            continue
        subs[op.strip()] = pid
    return plans, subs, errors


def plan_rule(plan: dict, op: str) -> dict | None:
    """Regola sulla quota inclusa nel piano. Nessuna regola se la quota è zero."""
    if plan["included_usd"] <= 0:
        return None
    return {"period": plan["included_period"], "action": plan["action"],
            "threshold_usd": plan["included_usd"], "operator": op, "plan": plan["id"],
            "notes": f"quota inclusa nel piano {plan['label']}"}


def applicable_rules(rules: list[dict], op: str, plan: dict | None = None) -> list[dict]:
    """Regole che valgono per l'operatore, per periodo, in quest'ordine di precedenza: le sue
    personali, la quota inclusa nel suo piano, quelle generali. Le regole personali di altri
    operatori non si applicano."""
    chosen = [r for r in rules if r["operator"] == op]
    taken = {r["period"] for r in chosen}
    pr = plan_rule(plan, op) if plan else None
    if pr and pr["period"] not in taken:
        chosen.append(pr)
        taken.add(pr["period"])
    return chosen + [r for r in rules if not r["operator"] and r["period"] not in taken]


def pricing_currency(root: Path) -> str | None:
    try:
        text = (root / "analytics" / "pricing.yaml").read_text(encoding="utf-8")
    except OSError:
        return None
    m = re.search(r"^currency\s*:\s*['\"]?([A-Za-z]{3})", text, re.M)
    return m.group(1).upper() if m else None


def operator(root: Path) -> str:
    try:
        p = subprocess.run(["git", "-C", str(root), "config", "user.name"],
                           capture_output=True, text=True, timeout=5, encoding="utf-8", errors="replace")
        name = p.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        name = ""
    return name or os.environ.get("USER") or os.environ.get("USERNAME") or "unknown"


# ---------------------------------------------------------------------------
# Transcript
# ---------------------------------------------------------------------------

def transcripts_dir(project_dir: str) -> Path:
    # una sola regola per i path di ~/.claude/projects/: quella dell'harvest
    return _harvest.transcripts_dir(project_dir)


def factory_checkouts(root: Path) -> list[str]:
    """Checkout del repo della factory (principale per primo, poi i worktree)."""
    try:
        p = subprocess.run(["git", "-C", str(root), "worktree", "list", "--porcelain"],
                           capture_output=True, text=True, timeout=10, encoding="utf-8", errors="replace")
    except (OSError, subprocess.SubprocessError):
        return []  # fail-open voluto: resta la cartella del progetto corrente
    if p.returncode != 0:
        return []
    return [ln[len("worktree "):] for ln in p.stdout.splitlines() if ln.startswith("worktree ")]


def transcript_dirs(project_dir: str, root: Path) -> list[Path]:
    """Cartelle di ~/.claude/projects/ della factory su questa macchina.

    Claude Code salva i transcript nella cartella del cwd di avvio: una chiusura lanciata
    da un worktree vedrebbe solo la cartella del worktree (spesso vuota, se la sessione è
    partita dal checkout principale) e misurerebbe 0. Si leggono quindi la cartella del
    progetto corrente, quelle di tutti i checkout elencati da `git worktree list` e quelle
    dei worktree sotto .claude/worktrees/ già rimossi (stesso prefisso del principale).
    """
    checkouts = factory_checkouts(root)
    dirs = [transcripts_dir(project_dir)] + [transcripts_dir(c) for c in checkouts]
    if checkouts:
        main = transcripts_dir(checkouts[0])
        dirs += sorted(main.parent.glob(main.name + "--claude-worktrees-*"))
    out: list[Path] = []
    for d in dirs:
        if d not in out and d.is_dir():
            out.append(d)
    return out or dirs[:1]


def _dirs(tdir) -> list[Path]:
    return [tdir] if isinstance(tdir, Path) else list(tdir)


def _main_transcripts(tdir) -> dict[str, Path]:
    """Transcript principali per session id; con lo stesso id in due cartelle vince il
    file più grande (una sessione ripresa altrove riparte dalla storia completa)."""
    found: dict[str, Path] = {}
    for d in _dirs(tdir):
        for path in d.glob("*.jsonl"):
            try:
                size = path.stat().st_size
                if path.stem in found and found[path.stem].stat().st_size >= size:
                    continue
            except OSError:
                continue
            found[path.stem] = path
    return found


def session_files(tdir, session_id: str) -> list[tuple[Path, str | None]]:
    main = _main_transcripts(tdir).get(session_id)
    if main is None:
        return []
    return _harvest.collect_jsonl_files(str(main))


def resolve_session_id(tdir, explicit: str | None) -> str | None:
    sid = explicit or os.environ.get("CLAUDE_CODE_SESSION_ID")
    if sid:
        return sid
    try:
        latest = max(_main_transcripts(tdir).values(), key=lambda p: p.stat().st_mtime)
        return latest.stem
    except (ValueError, OSError):
        return None


def window_files(tdir, start: dt.datetime) -> list[tuple[Path, str | None]]:
    """File di tutte le sessioni toccate dopo `start` (mtime), con i loro subagents.

    `tdir` è una cartella o una lista di cartelle (vedi transcript_dirs)."""
    floor = start.timestamp()
    out = []
    for _sid, main in sorted(_main_transcripts(tdir).items()):
        try:
            if main.stat().st_mtime < floor:
                continue
        except OSError:
            continue
        out.extend(_harvest.collect_jsonl_files(str(main)))
    return out


def _parse_ts(ts: str) -> dt.datetime | None:
    try:
        return dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def period_start(period: str, now: dt.datetime) -> dt.datetime:
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if period == "daily":
        return midnight
    if period == "monthly":
        return midnight.replace(day=1)
    return midnight - dt.timedelta(days=midnight.weekday())  # lunedì della settimana ISO


# ---------------------------------------------------------------------------
# Costo
# ---------------------------------------------------------------------------

class PricingUnavailable(RuntimeError):
    """analytics/pricing.yaml esiste ma non si e' caricato: i costi sarebbero di fallback."""


class Pricer:
    def __init__(self, root: Path):
        self.table = _ledger.load_pricing(str(root))
        listino = Path(root) / "analytics" / "pricing.yaml"
        if listino.exists() and not self.table:
            raise PricingUnavailable(
                f"listino {listino} presente ma non caricato (PyYAML assente o file non valido): "
                "i costi uscirebbero con i prezzi di fallback")
        self.fallback_models: set[str] = set()
        self.unverified_versions: set[str] = set()

    def rates(self, model: str) -> dict:
        norm = _ledger.normalize_model(model)
        if norm in self.table:
            return self.table[norm]
        self.fallback_models.add(norm)
        for prefix, p in _ledger._MODEL_FALLBACKS.items():
            if norm.startswith(prefix):
                return p
        return _ledger._FALLBACK_PRICING

    def cost(self, model: str, vals) -> float:
        if not any(vals):
            return 0.0
        return _ledger.tokens_cost(self.rates(model), *vals)


# check valuta giorno, settimana e mese nello stesso processo: senza memo ogni
# transcript veniva riletto e decodificato una volta per periodo. La chiave
# include mtime e dimensione, quindi un file che cresce viene riletto.
_PARSED: dict[tuple, list] = {}


def _responses(path: Path, force_scope):
    st = path.stat()
    key = (str(path), force_scope, st.st_mtime_ns, st.st_size)
    if key not in _PARSED:
        _PARSED[key] = _harvest.parse_responses(str(path), force_scope)
    return _PARSED[key]


def _note_version(path: Path, pricer: Pricer) -> None:
    ver = _harvest.detect_cc_version(str(path))
    if ver and ver not in _harvest.SUPPORTED_CC_VERSIONS:
        pricer.unverified_versions.add(ver)


def measure(files, pricer: Pricer, start: dt.datetime | None = None) -> dict:
    """Costo delle risposte nei file (filtrate per timestamp >= start, se dato)."""
    total, by_session, by_scope, by_model = 0.0, {}, {}, {}
    for path, force_scope in files:
        sid = path.stem if force_scope is None else path.parent.parent.name
        if force_scope is None:
            _note_version(path, pricer)
        try:
            responses = _responses(path, force_scope)
        except (OSError, UnicodeDecodeError):
            continue
        for model, scope, vals, ts in responses:
            if start is not None:
                t = _parse_ts(ts)
                if t is None or t < start:
                    continue
            c = pricer.cost(model, vals)
            if not c:
                continue
            total += c
            by_session[sid] = by_session.get(sid, 0.0) + c
            by_scope[scope] = by_scope.get(scope, 0.0) + c
            by_model[model] = by_model.get(model, 0.0) + c
    return {"cost_usd": total, "by_session": by_session, "by_scope": by_scope,
            "by_model": by_model}


def measure_period(period: str, ctx: dict) -> dict:
    tdir, pricer, now = ctx.get("tdirs") or ctx["tdir"], ctx["pricer"], ctx["now"]
    if period == "session":
        sid = ctx["session_id"]
        files = session_files(tdir, sid) if sid else []
        m = measure(files, pricer)
        m["window"] = {"session_id": sid}
        m["available"] = bool(files)
        return m
    start = period_start(period, now)
    m = measure(window_files(tdir, start), pricer, start)
    m["window"] = {"from": start.isoformat(timespec="seconds"),
                   "to": now.isoformat(timespec="seconds")}
    m["available"] = True
    return m


# ---------------------------------------------------------------------------
# Somma degli eventi dello store
# ---------------------------------------------------------------------------

COMPONENTS = ("input", "output", "cache_read", "cache_write", "cache_write_1h")


def event_tokens(ev: dict) -> tuple:
    """(input, output, cache_read, cache_write, cache_write_1h) dichiarati dall'evento."""
    t = ev.get("tokens") or {}
    return tuple(int(t.get(k, 0) or 0) for k in COMPONENTS)


def event_deltas(events: list) -> list:
    """Per ogni evento il consumo che porta: la differenza dal precedente dello stesso task_id
    se i totali sono cumulati (mai in calo), altrimenti il valore dell'evento."""
    streams: dict = {}
    for ev in events:
        streams.setdefault(str(ev.get("task_id") or ""), []).append(ev)
    out = []
    for evs in streams.values():
        evs.sort(key=lambda e: (str(e.get("ts") or ""), json.dumps(e, sort_keys=True, default=str)))
        vals = [event_tokens(e) for e in evs]
        cumulative = all(all(b[i] >= a[i] for i in range(5)) for a, b in zip(vals, vals[1:]))
        prev = (0, 0, 0, 0, 0)
        for ev, v in zip(evs, vals):
            out.append((ev, tuple(v[i] - prev[i] for i in range(5)) if cumulative else v))
            if cumulative:
                prev = v
    return out


def store_sum(events: list, pricer: Pricer, start: str | None = None) -> dict:
    """Costo e token degli eventi dello store. Lo stesso task_id registrato piu' volte con
    totali cumulati non si conta due volte: si sommano le differenze. Gli eventi precedenti a
    `start` entrano nel calcolo delle differenze ma non nel totale."""
    in_window = [(ev, v) for ev, v in event_deltas(events)
                 if start is None or str(ev.get("ts") or "") >= start]
    total = 0.0
    tokens = [0] * 5
    for ev, vals in in_window:
        total += pricer.cost(str(ev.get("model") or "unknown"), vals)
        tokens = [a + b for a, b in zip(tokens, vals)]
    return {"cost_usd": total, "tokens": dict(zip(COMPONENTS, tokens)), "events": len(in_window)}


# ---------------------------------------------------------------------------
# Riconciliazione: store contro transcript dell'operatore
# ---------------------------------------------------------------------------

LABEL_RELIABLE = "affidabile"
LABEL_UNDERESTIMATE = "sottostima"
LABEL_UNVERIFIABLE = "non verificabile"
DEFAULT_UNDERESTIMATE_THRESHOLD = 0.05  # da confermare dopo due settimane di misura
THRESHOLD_NOTE = "soglia da confermare dopo due settimane di misura"
CACHE_WRITE_PARTS = ("input", "output", "cache_read", "cache_write_5m", "cache_write_1h")


def load_reconcile_config(root: Path) -> dict:
    """analytics.reconcile di factory.config.yaml, con i default se le chiavi mancano.
    Valori non validi si scartano con un avviso in `errors`."""
    out = {"underestimate_threshold": DEFAULT_UNDERESTIMATE_THRESHOLD,
           "worktree_aliases": [], "errors": []}
    try:
        cfg = (((_yaml_load(root / "factory.config.yaml") or {}).get("analytics") or {})
               .get("reconcile") or {})
    except Exception as exc:  # noqa: BLE001 — fail-open: si usano i default
        out["errors"].append(f"config non leggibile: {exc}")
        return out
    thr = cfg.get("underestimate_threshold")
    if thr is not None:
        if isinstance(thr, bool) or not isinstance(thr, (int, float)) or not 0 <= thr <= 1:
            out["errors"].append("analytics.reconcile.underestimate_threshold deve essere "
                                 "un numero tra 0 e 1: uso il default")
        else:
            out["underestimate_threshold"] = float(thr)
    for pat in cfg.get("worktree_aliases") or []:
        try:
            re.compile(str(pat))
        except re.error:
            out["errors"].append(f"worktree_aliases: espressione non valida '{pat}', scartata")
            continue
        out["worktree_aliases"].append(str(pat))
    return out


def _event_hash(ev: dict) -> str:
    h = ev.get("hash")
    if h:
        return str(h)
    raw = f"{ev.get('task_id')}|{ev.get('state')}|{ev.get('ts')}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def store_events(root: Path, start: str | None = None, end: str | None = None) -> tuple:
    """Eventi di consumo (session-aggregate) di analytics/events/*.jsonl con ts in
    [start, end) (ISO), una volta per hash. Sola lettura.
    Ritorna (eventi, duplicati_scartati, righe_illeggibili)."""
    seen: set = set()
    events: list = []
    dups = bad = 0
    for f in sorted((root / "analytics" / "events").glob("*.jsonl")):
        try:
            lines = f.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            bad += 1
            continue
        for line in lines:
            if not line.strip():
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                bad += 1
                continue
            if not isinstance(ev, dict) or ev.get("task_type") != "session-aggregate":
                continue
            ts = str(ev.get("ts") or "")
            if (start and ts < start) or (end and ts >= end):
                continue
            h = _event_hash(ev)
            if h in seen:
                dups += 1
                continue
            seen.add(h)
            events.append(ev)
    return events, dups, bad


def _without_cache_read(events: list) -> list:
    out = []
    for ev in events:
        t = dict(ev.get("tokens") or {})
        t["cache_read"] = 0
        out.append({**ev, "tokens": t})
    return out


def factory_folder_names(root: Path, project_dir: str | None = None) -> set:
    """Nomi delle cartelle dei transcript che appartengono alla factory: progetto corrente e
    checkout elencati da `git worktree list`."""
    paths = [str(root)] + ([project_dir] if project_dir else []) + factory_checkouts(root)
    return {transcripts_dir(p).name for p in paths}


def folder_attributed(name: str, factory_names: set, aliases: list) -> bool:
    if name in factory_names or any(name.startswith(n + "--claude-worktrees-")
                                    for n in factory_names):
        return True
    return any(re.search(a, name) for a in aliases)


def operator_sum(transcripts_root: Path, pricer: Pricer, start=None, end=None,
                 factory_names: set = frozenset(), aliases: list = (), session_id=None) -> dict:
    """Costo a listino dei transcript dell'operatore sotto `transcripts_root` (tutte le
    cartelle), nella finestra [start, end) (datetime) o per una sessione.

    Si somma per voce di costo: la scrittura in cache e' un totale con la parte a TTL 1h
    dentro, quindi si prezza come (cache_write - cache_write_1h) a 5m piu' la parte a 1h a
    1h. Ritorna anche il totale senza le letture dalla cache e la quota delle cartelle
    attribuite alla factory (per nome, o per alias di configurazione)."""
    dirs = (sorted(p for p in transcripts_root.iterdir() if p.is_dir())
            if transcripts_root.is_dir() else [])
    if session_id:
        files = session_files(dirs, session_id)
    else:
        files = window_files(dirs, start) if start else []
    comp = dict.fromkeys(CACHE_WRITE_PARTS, 0.0)
    by_dir: dict = {}
    cr_by_dir: dict = {}
    read = unreadable = 0
    for path, scope in files:
        if scope is None:
            _note_version(path, pricer)
        try:
            responses = _responses(path, scope)
        except (OSError, UnicodeDecodeError):
            unreadable += 1
            continue
        read += 1
        folder = (path.parent if scope is None else path.parent.parent.parent).name
        for model, _scope, vals, ts in responses:
            if not session_id:
                t = _parse_ts(ts)
                if t is None or t < start or (end is not None and t >= end):
                    continue
            i, o, cr, cw, cw1h = vals
            parts = {"input": (i, 0, 0, 0, 0), "output": (0, o, 0, 0, 0),
                     "cache_read": (0, 0, cr, 0, 0),
                     "cache_write_5m": (0, 0, 0, cw - cw1h, 0),
                     "cache_write_1h": (0, 0, 0, cw1h, cw1h)}
            for k, one in parts.items():
                c = pricer.cost(model, one)
                comp[k] += c
                by_dir[folder] = by_dir.get(folder, 0.0) + c
                if k == "cache_read":
                    cr_by_dir[folder] = cr_by_dir.get(folder, 0.0) + c
    total = sum(comp.values())
    attr = [d for d in by_dir if folder_attributed(d, set(factory_names), list(aliases))]
    attr_total = sum(by_dir[d] for d in attr)
    attr_cr = sum(cr_by_dir.get(d, 0.0) for d in attr)
    return {"transcripts_root": str(transcripts_root), "files_read": read,
            "unreadable_files": unreadable,
            "cost_usd": round(total, 4),
            "cost_usd_excl_cache_read": round(total - comp["cache_read"], 4),
            "attributed_cost_usd": round(attr_total, 4),
            "attributed_cost_usd_excl_cache_read": round(attr_total - attr_cr, 4),
            "attributed_folders": sorted(attr),
            "by_component": {k: round(v, 4) for k, v in comp.items()},
            "by_project_dir": {k: round(v, 4) for k, v in sorted(by_dir.items())}}


def _gap(operator_usd: float, store_usd: float) -> dict:
    """Quanto lo store sta sotto l'operatore (positivo = sottostima)."""
    usd = operator_usd - store_usd
    return {"usd": round(usd, 4),
            "pct": round(usd / operator_usd * 100, 2) if operator_usd else None}


def reliability_label(store: dict, op: dict | None, pricer: Pricer, threshold: float) -> tuple:
    """(etichetta, motivo, scarto). L'etichetta si decide sul confronto a listino pieno,
    omogeneo con lo store (che prezza anche le letture dalla cache); il confronto senza
    cache e' informativo."""
    if pricer.table == {}:
        return LABEL_UNVERIFIABLE, "listino non caricato", None
    if op is None or op["files_read"] == 0:
        return LABEL_UNVERIFIABLE, "nessun transcript leggibile nella finestra", None
    if pricer.unverified_versions:
        return (LABEL_UNVERIFIABLE, "versione di Claude Code non verificata: "
                + ", ".join(sorted(pricer.unverified_versions)), None)
    base = op["attributed_cost_usd"]
    if base <= 0:
        return LABEL_UNVERIFIABLE, "nessun consumo attribuito alla factory nella finestra", None
    gap = _gap(base, store["cost_usd"])
    if gap["pct"] / 100 > threshold:
        return (LABEL_UNDERESTIMATE,
                f"lo store sta {gap['pct']:.1f}% sotto l'operatore (soglia {threshold * 100:g}%)",
                gap)
    return (LABEL_RELIABLE,
            f"scarto {gap['pct']:+.1f}% entro la soglia {threshold * 100:g}%", gap)


def _utc_z(t: dt.datetime) -> str:
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def reconcile_period(ctx: dict, period: str) -> dict:
    """Confronto tra lo store della factory e il contatore dell'operatore su un periodo."""
    root, now = ctx["root"], ctx["now"]
    cfg = load_reconcile_config(root)
    pricer = Pricer(root)
    sid = ctx.get("session_id") if period == "session" else None
    if period == "session":
        start_dt = None
        window = {"session_id": sid}
        events, dups, bad = store_events(root)
        events = [e for e in events
                  if sid and str(e.get("task_id") or "").startswith(f"session:{sid[:8]}:")]
        store_start = None
    else:
        start_dt = period_start(period, now)
        window = {"from": start_dt.isoformat(timespec="seconds"),
                  "to": now.isoformat(timespec="seconds")}
        store_start = _utc_z(start_dt)
        # gli eventi precedenti alla finestra servono al calcolo delle differenze
        events, dups, bad = store_events(root, None, _utc_z(now))
    store = store_sum(events, pricer, store_start)
    store["cost_usd_excl_cache_read"] = store_sum(
        _without_cache_read(events), pricer, store_start)["cost_usd"]
    store["duplicates_skipped"], store["unreadable_lines"] = dups, bad
    store["cost_usd"] = round(store["cost_usd"], 4)
    store["cost_usd_excl_cache_read"] = round(store["cost_usd_excl_cache_read"], 4)
    op = operator_sum(Path(ctx["transcripts_root"]), pricer, start_dt, now,
                      factory_folder_names(root, ctx.get("project_dir")),
                      cfg["worktree_aliases"], sid)
    label, reason, gap = reliability_label(store, op, pricer, cfg["underestimate_threshold"])
    out = {"period": period, "window": window, "label": label, "reason": reason,
           "threshold": cfg["underestimate_threshold"], "threshold_note": THRESHOLD_NOTE,
           "store": store, "operator": op, "gap": gap, "gap_excl_cache_read": None,
           "notes": list(cfg["errors"])}
    if op["attributed_cost_usd_excl_cache_read"] > 0:
        out["gap_excl_cache_read"] = _gap(op["attributed_cost_usd_excl_cache_read"],
                                          store["cost_usd_excl_cache_read"])
    if pricer.fallback_models:
        out["notes"].append("modelli assenti da analytics/pricing.yaml, stimati con il prezzo "
                            "di famiglia: " + ", ".join(sorted(pricer.fallback_models)))
    return out


def reliability_of(ctx: dict, period: str) -> dict | None:
    """Etichetta di affidabilita' per verdetto e breakdown; None se non calcolabile
    (il comando che la mostra non cambia esito)."""
    try:
        r = reconcile_period(ctx, period)
    except Exception:  # noqa: BLE001 — l'etichetta e' un'aggiunta: non rompe check/breakdown
        return None
    return {"label": r["label"], "reason": r["reason"], "threshold": r["threshold"],
            "threshold_note": r["threshold_note"]}


def fmt_reliability(r: dict) -> str:
    return (f"affidabilita' del costo: {r['label']} ({r['reason']}; {r['threshold_note']}) "
            f"→ cost_alert.py reconcile")


def cmd_reconcile(args) -> int:
    try:
        ctx = build_context(args)
    except PricingUnavailable as exc:
        # senza listino l'etichetta e' «non verificabile» e, come ogni sottocomando, l'uscita e' 2
        out = {"period": args.period, "label": LABEL_UNVERIFIABLE,
               "reason": f"listino non caricato ({exc})"}
        print(json.dumps(out, indent=2, ensure_ascii=False) if args.json else
              f"[cost-alert] riconciliazione {PERIOD_LABEL[args.period]}: {out['label']} "
              f"— {out['reason']}")
        return 2
    out = reconcile_period(ctx, args.period)
    op, st = out["operator"], out["store"]
    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print(f"[cost-alert] riconciliazione {PERIOD_LABEL[args.period]}: {out['label']} "
              f"— {out['reason']}")
        print(f"  operatore (tutte le cartelle) {op['cost_usd']:.2f} USD a listino, "
              f"{op['cost_usd_excl_cache_read']:.2f} senza letture dalla cache "
              f"({op['files_read']} file)")
        print(f"  operatore attribuito alla factory {op['attributed_cost_usd']:.2f} / "
              f"{op['attributed_cost_usd_excl_cache_read']:.2f} USD "
              f"({len(op['attributed_folders'])} cartelle)")
        print(f"  store {st['cost_usd']:.2f} / {st['cost_usd_excl_cache_read']:.2f} USD "
              f"su {st['events']} eventi ({st['duplicates_skipped']} duplicati scartati)")
        for label, g in (("scarto con cache", out["gap"]),
                         ("scarto senza cache", out["gap_excl_cache_read"])):
            if g and g["pct"] is not None:
                print(f"  {label}: {g['pct']:+.1f}% ({g['usd']:+.2f} USD) "
                      f"(positivo = lo store sottostima)")
        print(f"  {out['threshold_note']} (soglia {out['threshold'] * 100:g}%)")
        for n in out["notes"]:
            print(f"  nota: {n}")
    if st["unreadable_lines"] or op["unreadable_files"]:
        print(f"letture incomplete: righe dello store {st['unreadable_lines']}, transcript "
              f"{op['unreadable_files']}", file=sys.stderr)
        return 1  # risultato incompleto: non e' un successo
    return 0


# ---------------------------------------------------------------------------
# Comandi
# ---------------------------------------------------------------------------

def build_context(args) -> dict:
    root = Path(args.root).resolve() if args.root else ROOT
    project_dir = args.project_dir or os.environ.get("CLAUDE_PROJECT_DIR") or str(root)
    tdirs = ([Path(args.transcripts_dir)] if args.transcripts_dir
             else transcript_dirs(project_dir, root))
    troot = getattr(args, "transcripts_root", None)
    if troot:
        transcripts_root = Path(troot).expanduser()
    elif args.transcripts_dir:  # cartella dei transcript data a mano: la radice e' il suo genitore
        transcripts_root = Path(args.transcripts_dir).parent
    else:
        transcripts_root = Path.home() / ".claude" / "projects"
    return {"root": root, "tdir": tdirs[0], "tdirs": tdirs, "pricer": Pricer(root),
            "transcripts_root": transcripts_root, "project_dir": project_dir,
            "now": dt.datetime.now().astimezone(),
            "session_id": resolve_session_id(tdirs, getattr(args, "session_id", None))}


def evaluate(ctx: dict, periods: tuple[str, ...]) -> dict:
    root = ctx["root"]
    out = {"enabled": False, "agent_enabled": False, "operator": operator(root),
           "source": "transcript di questa macchina ("
                     + ", ".join(d.name for d in (ctx.get("tdirs") or [ctx["tdir"]])) + ")",
           "generated_at": ctx["now"].isoformat(timespec="seconds"),
           "plan": None, "results": [], "escalations": [], "notes": []}
    try:
        cfg = load_config(root)
    except Exception as exc:  # noqa: BLE001 — fail-open
        out["notes"].append(f"config non leggibile: {exc}")
        return out
    out["enabled"], out["agent_enabled"] = cfg["enabled"], cfg["agent"]
    if not cfg["enabled"]:
        out["notes"].append("analytics.cost_alert.enabled è false: nessun controllo")
        return out
    currency = pricing_currency(root)
    if currency != "USD":
        out["notes"].append(f"valuta non omogenea: attesa USD, pricing.yaml dichiara "
                            f"{currency or 'nulla'} — nessun confronto con threshold_usd")
        return out
    try:
        rules, errors = load_rules(root / cfg["rules_file"])
    except Exception as exc:  # noqa: BLE001
        out["notes"].append(f"{cfg['rules_file']} non leggibile: {exc}")
        return out
    out["notes"].extend(errors)
    try:
        plans, subs, plan_errors = load_plans(root / cfg["rules_file"])
    except Exception as exc:  # noqa: BLE001
        plans, subs, plan_errors = {}, {}, [f"piani non leggibili: {exc}"]
    out["notes"].extend(plan_errors)
    plan = plans.get(subs.get(out["operator"], ""))
    out["plan"] = plan

    cache: dict[str, dict] = {}
    for rule in applicable_rules(rules, out["operator"], plan):
        if rule["period"] not in periods:
            continue
        m = cache.get(rule["period"]) or measure_period(rule["period"], ctx)
        cache[rule["period"]] = m
        ratio = m["cost_usd"] / rule["threshold_usd"]
        res = {**rule, "cost_usd": round(m["cost_usd"], 4), "ratio": round(ratio, 3),
               "breached": m["available"] and ratio >= 1, "window": m["window"]}
        if not m["available"]:
            res["note"] = "transcript della sessione non trovato"
        if rule.get("plan"):
            res["excess_usd"] = round(max(0.0, m["cost_usd"] - rule["threshold_usd"]), 4)
        out["results"].append(res)
        if res["breached"] and rule["action"] == "escalate":
            out["escalations"].append(res)

    if plan and plan["included_period"] == "weekly":
        out["notes"].append("la settimana del piano è calcolata dal lunedì: la finestra usata "
                            "per l'addebito non è nota, la stima può spostarsi di qualche giorno")
    if plan:
        out["notes"].append("costi a prezzo di listino: la quota del piano potrebbe essere "
                            "misurata con tariffe diverse")
    if any(p in cache for p in ("daily", "weekly", "monthly")):
        out["notes"].append("giorno/settimana/mese contano solo le sessioni di questo progetto su "
                            "questa macchina (checkout principale e worktree della factory): "
                            "altre cartelle e transcript già ripuliti da Claude Code restano "
                            "fuori")
    if ctx["pricer"].fallback_models:
        out["notes"].append("modelli assenti da analytics/pricing.yaml, stimati con il prezzo "
                            "di famiglia: " + ", ".join(sorted(ctx["pricer"].fallback_models)))
    if ctx["pricer"].unverified_versions:
        out["notes"].append("versioni di Claude Code non verificate dal parser ("
                            + ", ".join(sorted(ctx["pricer"].unverified_versions))
                            + "): l'output dei subagenti può risultare sottostimato")
    if out["escalations"] and not cfg["agent"]:
        out["notes"].append("escalation non disponibile: analytics.cost_alert.agent è false, "
                            "le regole escalate valgono come warn")
    return out


def alert_id(res: dict, op: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", op.lower()).strip("-") or "unknown"
    w = res["window"]
    key = (w.get("session_id") or "")[:8] if res["period"] == "session" else w["from"][:10]
    return f"{res['period']}-{key}-{slug}"


def write_records(ctx: dict, verdict: dict, note: str) -> list[str]:
    cfg = load_config(ctx["root"])
    adir = ctx["root"] / cfg["alerts_dir"]
    adir.mkdir(parents=True, exist_ok=True)
    now = ctx["now"].isoformat(timespec="seconds")
    written = []
    for res in verdict["escalations"]:
        aid = alert_id(res, verdict["operator"])
        path = adir / f"{aid}.json"
        prev = {}
        if path.exists():
            try:
                prev = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                prev = {}
        rec = {
            "alert_id": aid, "operator": verdict["operator"], "period": res["period"],
            "window": res["window"], "threshold_usd": res["threshold_usd"],
            "cost_usd": res["cost_usd"], "session_id": ctx["session_id"],
            "source": verdict["source"],
            "created_at": prev.get("created_at") or now, "updated_at": now,
            "acknowledged_at": prev.get("acknowledged_at"),
            "note": note or prev.get("note") or "",
        }
        path.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written.append(str(path.relative_to(ctx["root"])))
    return written


def load_records(root: Path) -> list[dict]:
    try:
        adir = root / load_config(root)["alerts_dir"]
    except Exception:  # noqa: BLE001
        return []
    recs = []
    for p in sorted(adir.glob("*.json")):
        try:
            recs.append(json.loads(p.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue
    return recs


def pending(root: Path, op: str) -> list[dict]:
    return [r for r in load_records(root)
            if r.get("operator") == op and not r.get("acknowledged_at")]


def fmt_verdict(v: dict) -> str:
    lines = [f"[cost-alert] operatore {v['operator']} · fonte: {v['source']}"]
    for r in v["results"]:
        state = (f"SUPERATA → {r['action']}" if r["breached"]
                 else ("vicina" if r["ratio"] >= NEAR_RATIO else "ok"))
        label = PERIOD_LABEL[r["period"]] + ("†" if r.get("plan") else
                                             "*" if r.get("operator") else "")
        lines.append(f"  {label:<10} {r['cost_usd']:>8.2f} / "
                     f"{r['threshold_usd']:.2f} USD  {r['ratio'] * 100:>4.0f}%  {state}")
    if any(r.get("operator") and not r.get("plan") for r in v["results"]):
        lines.append(f"  * regola personale di {v['operator']}")
    plan = v.get("plan")
    if plan:
        excess = [r for r in v["results"] if r.get("plan")]
        line = (f"  † piano {plan['label']}: {plan['fixed_usd_month']:.2f} USD/mese fissi "
                f"sul centro di costo")
        if excess:
            r = excess[0]
            line += (f", eccedenza {PERIOD_LABEL[r['period']]} {r['excess_usd']:.2f} USD "
                     f"oltre i {r['threshold_usd']:.2f} inclusi")
        lines.append(line)
    if v["enabled"] and not v["results"]:
        lines.append("  (nessuna regola per i periodi richiesti)")
    for n in v["notes"]:
        lines.append(f"  nota: {n}")
    return "\n".join(lines)


def fmt_compact(v: dict) -> str:
    """Una riga per gli ospiti (/run): stato delle regole, pendenti, quante note leggere."""
    rules = [f"{PERIOD_LABEL[r['period']]} {r['cost_usd']:.2f}/{r['threshold_usd']:g} USD"
             + (" ⚠" if r["breached"] else "") for r in v["results"]]
    parts = ["◉ COSTI  " + ("  ·  ".join(rules) if rules else "nessuna regola applicabile")]
    if v["pending"]:
        parts.append(f"{v['pending']} alert pendenti")
    if v["notes"]:
        parts.append(f"{len(v['notes'])} note")
    return "  ·  ".join(parts) + "  → /cost-alert"


def cmd_check(args) -> int:
    ctx = build_context(args)
    periods = PERIODS if args.period == "all" else (args.period,)
    v = evaluate(ctx, periods)
    if args.record and v["escalations"] and v["agent_enabled"]:
        try:
            v["records"] = write_records(ctx, v, args.note or "")
        except OSError as exc:
            v["notes"].append(f"record non scritto: {exc}")
    v["pending"] = len(pending(ctx["root"], v["operator"])) if v["enabled"] else 0
    if v["enabled"] and v["results"] and not (args.compact or args.gate):
        widest = max((r["period"] for r in v["results"]), key=PERIODS.index)
        v["reliability"] = reliability_of(ctx, widest)
    if args.compact or args.gate:
        alarm = any(r["breached"] for r in v["results"]) or v["pending"]
        if v["enabled"] and (args.compact or alarm):
            print(fmt_compact(v))
        return 0
    if args.json:
        print(json.dumps(v, indent=2, ensure_ascii=False))
    else:
        print(fmt_verdict(v))
        if v.get("reliability"):
            print("  " + fmt_reliability(v["reliability"]))
        if v.get("records"):
            print("  record: " + ", ".join(v["records"]))
        if v["pending"]:
            print(f"  alert pendenti: {v['pending']} (/cost-alert --pending)")
    return 0


def cmd_breakdown(args) -> int:
    ctx = build_context(args)
    m = measure_period(args.period, ctx)
    top = sorted(m["by_session"].items(), key=lambda kv: kv[1], reverse=True)[: args.top]
    out = {"period": args.period, "window": m["window"],
           "cost_usd": round(m["cost_usd"], 4),
           "by_scope": {k: round(c, 4) for k, c in m["by_scope"].items()},
           "by_model": {k: round(c, 4) for k, c in
                        sorted(m["by_model"].items(), key=lambda kv: kv[1], reverse=True)},
           "top_sessions": [{"session_id": s, "cost_usd": round(c, 4)} for s, c in top],
           "fallback_models": sorted(ctx["pricer"].fallback_models)}
    rel = reliability_of(ctx, args.period)
    if rel:
        out["reliability"] = rel
    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0
    print(f"[cost-alert] {PERIOD_LABEL[args.period]}: {out['cost_usd']:.2f} USD")
    if rel:
        print("  " + fmt_reliability(rel))
    for k, c in out["by_scope"].items():
        print(f"  {k:<10} {c:>8.2f} USD")
    for k, c in out["by_model"].items():
        print(f"  {k:<28} {c:>8.2f} USD")
    for s in out["top_sessions"]:
        print(f"  sessione {s['session_id'][:8]}  {s['cost_usd']:>8.2f} USD")
    return 0


def cmd_pending(args) -> int:
    root = Path(args.root).resolve() if args.root else ROOT
    recs = pending(root, operator(root))
    if args.json:
        print(json.dumps(recs, indent=2, ensure_ascii=False))
        return 0
    if not recs:
        print("[cost-alert] nessun alert pendente")
    for r in recs:
        print(f"[cost-alert] {r['alert_id']}: {PERIOD_LABEL.get(r['period'], r['period'])} "
              f"{r['cost_usd']:.2f} / {r['threshold_usd']:.2f} USD (aggiornato {r['updated_at']})"
              + (f" — {r['note']}" if r.get("note") else ""))
    return 0


def cmd_ack(args) -> int:
    root = Path(args.root).resolve() if args.root else ROOT
    adir = root / load_config(root)["alerts_dir"]
    now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    done = []
    for r in pending(root, operator(root)):
        if args.all or r["alert_id"] == args.id:
            r["acknowledged_at"] = now
            (adir / f"{r['alert_id']}.json").write_text(
                json.dumps(r, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            done.append(r["alert_id"])
    print(f"[cost-alert] presi in carico: {', '.join(done) if done else 'nessuno'}")
    return 0


def status_line_suffix(cost_usd: float | None, root: Path = ROOT) -> str:
    """Suffisso per la statusLine: regola di sessione sul costo fornito da Claude Code e
    alert pendenti. Stringa vuota se la capability è spenta o non c'è nulla da segnalare."""
    try:
        cfg = load_config(root)
        if not cfg["enabled"]:
            return ""
        parts = []
        if isinstance(cost_usd, (int, float)):
            rules, _ = load_rules(root / cfg["rules_file"])
            # solo regole generali: l'operatore richiede `git config`, che qui non si lancia
            thr = [r["threshold_usd"] for r in rules
                   if r["period"] == "session" and not r["operator"]]
            if thr:
                t = min(thr)
                if cost_usd >= t:
                    parts.append(f"⚠ soglia sessione superata ({cost_usd:.2f}/{t:.2f} USD)")
                elif cost_usd >= NEAR_RATIO * t:
                    parts.append(f"budget sessione {cost_usd / t * 100:.0f}%")
        # niente `git config` qui: la statusLine gira dopo ogni risposta e non lancia
        # sottoprocessi. I record sono locali alla macchina, quindi bastano i non presi in carico.
        n = sum(1 for r in load_records(root) if not r.get("acknowledged_at"))
        if n:
            parts.append(f"⚠ {n} alert costi da vedere (/cost-alert --pending)")
        return "  ·  ".join(parts)
    except Exception:  # noqa: BLE001 — la statusLine non deve mai rompersi
        return ""


def cmd_status_line(args) -> int:
    root = Path(args.root).resolve() if args.root else ROOT
    s = status_line_suffix(args.cost, root)
    if s:
        print(s)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Controllo dei costi in token contro le regole.")
    ap.add_argument("--root", help=argparse.SUPPRESS)
    ap.add_argument("--project-dir", help="cwd di Claude Code (default: CLAUDE_PROJECT_DIR o root)")
    ap.add_argument("--transcripts-dir", help=argparse.SUPPRESS)
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check")
    c.add_argument("--period", choices=PERIODS + ("all",), default="all")
    c.add_argument("--session-id")
    c.add_argument("--record", action="store_true",
                   help="scrive il record delle regole escalate superate (agente cost-alert)")
    c.add_argument("--note", default="")
    c.add_argument("--json", action="store_true")
    c.add_argument("--compact", action="store_true",
                   help="una riga, nulla a capability spenta (per /run)")
    c.add_argument("--gate", action="store_true",
                   help="come --compact, ma stampa solo se una regola è superata o ci sono "
                        "alert pendenti (controlli prima di lanciare agenti)")
    c.add_argument("--transcripts-root", help="cartella dei transcript dell'operatore, per "
                   "l'etichetta di affidabilita' (default ~/.claude/projects)")
    c.set_defaults(fn=cmd_check)

    b = sub.add_parser("breakdown")
    b.add_argument("--period", choices=PERIODS, required=True)
    b.add_argument("--session-id")
    b.add_argument("--top", type=int, default=5)
    b.add_argument("--json", action="store_true")
    b.add_argument("--transcripts-root", help="cartella dei transcript dell'operatore, per "
                   "l'etichetta di affidabilita' (default ~/.claude/projects)")
    b.set_defaults(fn=cmd_breakdown)

    r = sub.add_parser("reconcile", help="confronta lo store con i transcript dell'operatore "
                                         "(tutte le cartelle) ed emette l'etichetta di "
                                         "affidabilita'")
    r.add_argument("--period", choices=PERIODS, default="weekly")
    r.add_argument("--session-id")
    r.add_argument("--transcripts-root", help="cartella dei transcript dell'operatore "
                   "(default ~/.claude/projects)")
    r.add_argument("--json", action="store_true")
    r.set_defaults(fn=cmd_reconcile)

    p = sub.add_parser("pending")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_pending)

    a = sub.add_parser("ack")
    g = a.add_mutually_exclusive_group(required=True)
    g.add_argument("--id")
    g.add_argument("--all", action="store_true")
    a.set_defaults(fn=cmd_ack)

    s = sub.add_parser("status-line")
    s.add_argument("--cost", type=float)
    s.set_defaults(fn=cmd_status_line)

    args = ap.parse_args(argv)
    try:
        return args.fn(args)
    except PricingUnavailable as exc:
        print(f"cost_alert: {exc}", file=sys.stderr)
        return 2  # risultato non affidabile: non esce come successo


if __name__ == "__main__":
    sys.exit(main())

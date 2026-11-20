"""Confine fra CQRL e /security-scan (EP-109 US-430, TSK-1047; accordo A26, R.Q7).

Test di testo: il confine e' scritto nelle istruzioni del code-reviewer e del protocollo, non in codice.
Bloccano le quattro invarianti contro una riscrittura che le perda."""
from __future__ import annotations

import hashlib
import os
import re

RADICE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def _leggi(rel):
    with open(os.path.join(RADICE, rel), encoding="utf-8") as fh:
        return fh.read()


RIGA_FISSA = "pass non attesta la sicurezza: CQRL non esegue oracoli di sicurezza (R.Q7)."


def test_ac3_riga_fissa_nel_digest():
    assert RIGA_FISSA in _leggi(".claude/skills/code-review-protocol.md")


def test_campo_security_scan_nello_schema_del_report():
    p = _leggi(".claude/skills/code-review-protocol.md")
    assert '"security_scan": "assente | security/reports/' in p
    assert "CQRL lo **legge**, non lo produce" in p


def test_ac1_reject_solo_per_il_secret_in_chiaro():
    r = _leggi(".claude/agents/code-reviewer.md")
    blocco = r[r.index("- **Mai security**"):r.index("## Output schema")]
    assert "secret in chiaro nel diff" in blocco and "verdict `reject` (invariato)" in blocco
    assert "nessun finding CQRL e nessun `reject`" in blocco and "vedi /security-scan" in blocco
    assert "CVE noti, apri" not in r   # la vecchia riga che dava reject anche per i CVE non c'e' piu'


def test_ac2_cve_nel_baseline_non_fa_scattare_reject():
    r = _leggi(".claude/agents/code-reviewer.md")
    p = _leggi(".claude/skills/code-review-protocol.md")
    assert "Un CVE gia' accettato nel baseline\n    SCA non fa scattare `reject`" in r or \
        "CVE gia' accettato nel baseline" in r
    assert "Caso documentato (US-430 AC2)" in p


def test_ac4_r_q7_invariata():
    t = _leggi("PATTERN-runtime.md")
    m = re.search(r"- \*\*R\.Q7 — Niente sicurezza\.\*\*.*?(?=\n\n)", t, re.S)
    assert m, "R.Q7 non trovata"
    assert hashlib.sha256(m.group(0).encode("utf-8")).hexdigest()[:16] == IMPRONTA_RQ7, m.group(0)


IMPRONTA_RQ7 = "491fa4175fcd1b0b"

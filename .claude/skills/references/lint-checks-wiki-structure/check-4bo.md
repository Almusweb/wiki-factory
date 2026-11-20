---
skill: lint-checks
leaf_of: lint-checks-wiki-structure.md
section: "wiki-structure"
description: "Check 4bo: lettori diretti di memory/active-sessions.yaml senza registry_path()"
---

> Eseguito da `tools/lint/run-deterministic.py` (registrato in `CHECKS`).

# 4bo — Lettori diretti di `memory/active-sessions.yaml` (always-on, WARNING)

**Eseguibile, non interpretato.**

```bash
python3 tools/lint/check_lettori_registro_sessioni.py [--root <factory>] [--json]
```

**Cosa controlla.** Dal 2.48 il registro delle sessioni sta sulla git common dir; l'unico modo giusto di
trovarlo e' `registry_path()` in `tools/session/active_sessions.py`. Codice che apre il path vecchio, di
solito dopo un controllo di esistenza del file, conta zero sessioni senza errore. Lo script analizza
(AST) i file `*.py` tracciati e segnala ogni costante stringa del codice che e' un path terminante in
`memory/active-sessions.yaml` (senza spazi: un messaggio che lo cita in una frase non conta).

**Esclusioni.** Docstring e commenti, `tools/session/active_sessions.py`, i test (`test_*.py`, `*_test.py`,
cartelle `tests`/`test`), `.claude/worktrees/`.

**Non garantisce.** Un path costruito a pezzi (`"memory" / "active-sessions.yaml"`) non e' visto. File
illeggibili o con sintassi non valida sono INFO «non verificabile», mai «puliti».

**Codice e severita'.** `lettori-registro-sessioni` (WARNING). Nessuna chiave in `factory.config.yaml`.
Exit 0 sempre.

**Chi corregge.** Il proprietario dello strumento: sostituire il path con `registry_path()`. Il piano di
`/factory-upgrade` verso 2.48 lo esegue sulla derivata e riporta i file (`factory-upgrade-protocol.md`,
«Nota di migrazione 2.48»).

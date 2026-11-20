---
skill: lint-checks
leaf_of: lint-checks-wiki-structure.md
section: "wiki-structure"
description: "Check 4bn: marcatori di conflitto nei file in coda e append-only"
---

> Eseguito da `tools/lint/run-deterministic.py` (registrato in `CHECKS`).

# 4bn — Marcatori di conflitto nei file in coda (always-on, WARNING)

**Eseguibile, non interpretato.**

```bash
python3 tools/lint/check_marcatori_conflitto.py [--json] [--rev REF] [--strict] .
```

**Cosa controlla.** Un pull con stash o `--autostash` in conflitto lascia nel file le righe di git
(`<<<<<<< Updated upstream`, `=======`, `>>>>>>> Stashed changes`, e `|||||||`). Lo script legge dal ref
(default `HEAD`) i file seguenti e segnala ogni riga marcatore:

- `wiki/log.md` e gli archivi `wiki/log-*.md`, `wiki/gaps.md`, `wiki/index.md`
- `raw/.extraction-manifest.json` (controllato anche come JSON valido)
- `management/kanban/sprint.md`

Il registro sessioni (`.git/active-sessions.yaml`, o `memory/active-sessions.yaml` fuori da git) non e'
tracciato: non e' tra i file in coda su HEAD e il check non lo guarda.

Nei `.md` un `=======` dentro un blocco delimitato da ``` o ~~~ e' testo citato e non conta; gli altri
marcatori contano ovunque.

**Configurazione.** Nessuna chiave in `factory.config.yaml`. Lista dei file e logica in
`tools/wiki/conflict_markers_check.py` (unica fonte, usata anche dagli hook).

**Codice e severita'.** `marcatori-conflitto` (WARNING, con righe e procedura di correzione per file).
Ref sconosciuto, git in errore o scaduto: `[ERROR]`, exit 2, controllo non eseguito. Exit 0 con finding,
exit 1 solo con `--strict`.

**Prevenzione.** `tools/vcs/install_factory_hooks.py` installa `pre-commit` (`--staged`) e `pre-push`
(`--pre-push`, insieme al controllo delle voci nuove del log). Sono hook locali, aggirabili con
`--no-verify`: questo check e' la rete di chi non li ha.

**Chi corregge.** Chi ha il file in conflitto, con la procedura stampata per file; il check non modifica
nulla.

---
name: security-fix-protocol
description: "Protocollo del fix di sicurezza con gate (EP-109 US-431, decisione D4 = (a)): un dev-agent propone su un branch il fix di un finding SCA confermato da /security-scan, solo su manifest e lockfile; ogni giro passa da tools/security/fix_gate.py (perimetro sul diff, diff-check sulle soppressioni, oracolo SCA rieseguito con lo stesso DB, chiusura legittima); loop bounded da security_scan.fix_max_iterations. Mai push sul default, mai merge, mai PR mergiata dall'agente: il fix e' una proposta per un umano (r.14, r.16)."
---

# Protocollo del fix gated — 4 fasi

Vale per il **primo ciclo** con la decisione D4 = (a) del maintainer (2026-11-19): **solo dipendenze**. Nessun
autofix semgrep, nessuna modifica al codice applicativo. Parte solo dopo US-428 (comparatore di identita' e
diff-check sulle soppressioni, A7): `depends_on` di TSK-1048 su TSK-1044, entrambe chiuse.

## Fase 0 — Ingresso

- Un finding SCA **confermato** da `/security-scan` (voce `nuovo_dal_commit` o `debito_non_nominato` in
  `sca_guard`), con id dell'advisory e nome del pacchetto.
- Branch dedicato sul code_path del cliente, da `merge-base` con il ref protetto. Mai lavorare sul branch di
  default.

## Fase 1 — Proposta (dev-agent)

Il dev-agent cambia **solo** il manifest delle dipendenze (es. `requirements.txt`, `package.json`, `go.mod`) e,
se serve, rigenera il lockfile **con il tool dell'ecosistema** a partire dal manifest (`npm install`, `go mod
tidy`, `poetry lock`). Non scrive a mano il lockfile, non tocca altro e committa sul branch.

Vietato, e il gate lo rifiuta per nome: `.semgrepignore`, `.trivyignore*`, `.gitleaksignore`, `osv-scanner.toml`,
la CI, `.claude/`, `security/` (baseline, pin, accettazioni), i registri, `factory.config.yaml`, il codice
applicativo. Il fix **non accetta rischi e non sopprime regole**: una soppressione nel diff e' FAIL.

## Fase 2 — Gate (deterministico, ogni giro)

`python3 tools/security/fix_gate.py <code_path> --finding <id> --pacchetto <nome>`:

| Esito | Significato | Exit |
|---|---|---|
| PASS | nel perimetro, nessuna soppressione, nessuna vulnerabilita' nuova, finding chiuso legittimamente (pacchetto a un'altra versione, advisory assente con lo stesso DB) | 0 |
| FAIL | perimetro violato, soppressione nuova o vulnerabilita' nuova dal commit | 1 |
| NON_VERIFICABILE | working tree sporco, DB o binario non verificabili, pacchetto rimosso, versione invariata | 3 |
| APERTO | nel perimetro ma l'advisory c'e' ancora: un altro giro | 4 |

## Fase 3 — Loop bounded

Si ripetono Fase 1 e 2 fino a `security_scan.fix_max_iterations` (default 3), con `fix_gate.ciclo`: stop al primo
esito diverso da APERTO; `no_progress` se due giri danno lo stesso esito sugli stessi file; `loop_exhausted` a fine
budget. In entrambi i casi: gate umano, nessun altro giro.

## Fase 4 — Consegna

Con PASS il dev-agent **apre al massimo una PR** sul branch dedicato e si ferma. **Mai** `git push` sul branch di
default, **mai** `gh pr merge` o `git merge` verso il default, mai approvare la PR: il merge e' umano (r.14, r.16).
Nella PR: id del finding, esito del gate (JSON), id del DB usato. Il protocollo di chiusura di `dev-handoff.md`
vale come per ogni TSK.

## Cosa NON garantisce

Che il fix non rompa il comportamento (restano i test di qa-dev e il merge umano); che la nuova versione sia nota
al DB (un advisory assente puo' voler dire «versione sconosciuta»); che il lockfile sia davvero rigenerato dal tool
(si verifica solo che cambi insieme al manifest); cause strutturali. Un agente con Bash puo' agire fuori dal gate:
quell'esito non vale come esito del gate.

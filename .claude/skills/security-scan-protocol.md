---
name: security-scan-protocol
description: "Protocollo di /security-scan (EP-109 US-429): fasi, input e confini del layer di sicurezza applicativa. Esegue gli oracoli deterministici (sast_guard semgrep, iac_guard trivy config, sca_guard osv-scanner offline, secrets_guard --storia gitleaks) tramite il runner tools/security/security_scan.py, scrive un report a campi enumerati in security/reports/ e lo passa all'agente interprete, che classifica senza decidere. Opt-in security_scan.enabled dall'ancora. Il threat model resta un ADR dell'architetto, input facoltativo."
---

# Protocollo di /security-scan — 4 fasi

Il layer di sicurezza applicativa e' distinto da CQRL: CQRL giudica idiomaticita' e design, questo protocollo
esegue oracoli deterministici e non attesta la sicurezza. Nessun agente decide: gli esiti vengono dagli strumenti,
le accettazioni da record umani.

## Input

| Cosa | Dove | Obbligatorio |
|---|---|---|
| Code path del cliente | `factory.config.yaml → code_paths[].path` (la factory e' rifiutata) | si' |
| Opt-in | `security_scan.enabled`, letto dall'ancora `origin/main` (`tools/security/config_ancorata.py`) | si' |
| Identita' degli scanner | `security/scanner-pins.json` al merge-base (decisione D7) | si' |
| Ruleset e config | `security_scan.semgrep_ruleset`, `security_scan.trivy_config` (file della factory, al merge-base) | per sast, iac |
| DB degli advisory | `security_scan.osv_db_dir` (offline, scaricato fuori dall'oracolo) | per sca |
| Baseline SCA | `security_scan.sca_baseline` (record nominativi, scadenza 90 giorni) | per sca |
| Threat model | ADR dell'architetto (`lead-architect`, sezione threat model dell'ADR del code_path), **senza tool** (A20) | **facoltativo**: orienta la lettura dei finding, non cambia gli esiti |

## Fase 1 — Gate

`python3 tools/security/security_scan.py <code_path>`. A flag spento: messaggio «CAPABILITY SPENTA», exit 3,
fine. Nessuna esecuzione manuale degli scanner al posto del runner.

## Fase 2 — Oracoli

Il runner esegue, per ogni oracolo scelto: perimetro, identita' del binario, ruleset dall'ancora, alberi PRIMA
(merge-base) e DOPO (HEAD) blob per blob, confronto per identita' del finding e diff-check sulle soppressioni
(`finding_compare.py`, `suppression_check.py`). Un oracolo che fallisce, rifiuta o si rompe vale
NON_VERIFICABILE, mai PASS.

**Interfaccia del modulo dei segreti.** La pila non importa `secrets_guard` direttamente: passa da
`tools/security/contratto_segreti.py`, che risolve dal modulo `secrets_guard` sul path solo quattro nomi —
`Rifiuto` (eccezione di rifiuto, la stessa classe che il modulo solleva), `guardia_storia(code_path, root)`
(None o il motivo del rifiuto), `scan_storia(code_path, root)` (esito con `stato`, `messaggio`, `findings`) e
`PASS`. Una derivata con un proprio `secrets_guard.py` adotta la pila esponendo quei nomi;
`contratto_segreti.mancanti()` dice quali mancano. Test: `tools/tests/test_contratto_segreti.py`.

## Fase 3 — Report

`security/reports/<code_path>-<AAAAMMGG>-<HHMMSS>.json`, ignorato da git (contiene finding del cliente). Per voce
solo campi enumerati: id della regola o dell'advisory, path o purl, stato, motivo, e per i segreti riga e commit.
Mai testo di advisory, messaggi dello scanner o contenuto dei file (A11).

## Fase 4 — Interpretazione (agente `security-interpreter`)

L'agente `security-interpreter` legge solo `<report>.agente.json` (soli campi enumerati, scritto dal runner): classifica raggiungibilita', ipotesi di falso positivo, priorita'.
Non accetta rischi e non sopprime: un falso positivo e' una **proposta** che diventa valida solo con un record di
accettazione umano sul ref protetto (baseline SCA o `security/suppression-accettazioni.json`, gate R.14).

## Cosa NON garantisce

Tabella consolidata in `CAPABILITIES.md` §security_scan. In breve: nessun oracolo attesta che il codice sia
sicuro; un oracolo installato non garantisce di essere eseguito; un agente con Bash puo' eseguire lo scanner
con un'altra config o non eseguirlo; il confine e' il runner, non il wrapper. Presupposto dichiarato: maintainer
e operatore coincidono (decisione D9 aperta).

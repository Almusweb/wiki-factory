---
description: "Esegue sugli code_paths del cliente gli oracoli deterministici di sicurezza (semgrep, trivy config, osv-scanner offline, gitleaks sulla storia) e scrive un report a campi enumerati. Opt-in security_scan.enabled, letto dall'ancora: a flag spento lo dice ed esce senza verifiche. PASS non significa codice sicuro; l'accettazione di un rischio resta un gate umano."
argument-hint: "<code_path> [--oracoli sast,iac,sca,segreti] [--json]"
allowed-tools: Bash, Read
---

# /security-scan

Argomenti utente: `$ARGUMENTS`

Segui `.claude/skills/security-scan-protocol.md`. Runner unico: `tools/security/security_scan.py`.

## Sintassi

```
/security-scan <code_path>                          # tutti gli oracoli: sast, iac, sca, segreti
/security-scan <code_path> --oracoli sca,segreti    # un sottoinsieme
/security-scan <code_path> --json                   # report consolidato su stdout
```

`<code_path>`: un `code_paths[].path` di `factory.config.yaml`. Il repo della factory e ogni path non dichiarato
sono rifiutati (NON_VERIFICABILE per quell'oracolo).

## Comportamento

1. Esegui `python3 tools/security/security_scan.py <code_path> [opzioni]` e riporta l'output **cosi' com'e'**.
2. A flag spento (`security_scan.enabled: false`, il default) il runner stampa «CAPABILITY SPENTA» ed esce 3:
   riportalo, non eseguire gli scanner a mano al suo posto.
3. Esito: PASS, FAIL o NON_VERIFICABILE per oracolo e complessivo. Non riformulare un NON_VERIFICABILE come PASS,
   non dire «codice sicuro».
4. Il report sta in `security/reports/` (ignorato da git). Per classificare i finding lo legge l'agente
   interprete, che non decide: ogni accettazione di rischio o soppressione e' un record umano (R.14).

## Cosa NON fa

Non installa ne' aggiorna scanner o DB, non scrive soppressioni o baseline, non corregge il codice, non apre PR.
Un agente con Bash puo' eseguire uno scanner fuori dal runner: quell'esito non vale come esito del layer.

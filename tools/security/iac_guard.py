#!/usr/bin/env python3
"""Oracolo trivy sulle configurazioni IaC e container del filesystem, config dal merge-base (EP-109 US-427,
TSK-1042).

Motore, contratto ed esiti in oracolo_statico.py. Specifico di trivy:
- `trivy config` (equivale a `trivy fs --scanners misconfig`): Terraform, Kubernetes, Dockerfile, Helm,
  CloudFormation sull'albero materializzato; le vulnerabilita' delle dipendenze sono dell'oracolo SCA;
- config: file `security_scan.trivy_config` della factory (trivy.yaml), letto al merge-base della factory
  e passato con `--config`;
- `.trivyignore`, `.trivyignore.yaml` e `trivy.yaml` dell'albero sostituiti con quelli del merge-base del
  code_path; un `#trivy:ignore` inline aggiunto fa sparire il finding ma il diff-check lo segnala (FAIL);
- `--skip-check-update`: si usa il bundle dei controlli gia' in cache, senza aggiornarlo durante la scansione;
- identita' del finding: (trivy, ID del controllo, Target) senza riga; contano solo gli esiti FAIL;
- exit accettato solo 0 (senza `--exit-code` trivy esce 1 solo per errore).

Cosa NON garantisce: oltre a quanto dichiarato nel motore, il bundle dei controlli di trivy non e' fissato
ne' identificato (la riproducibilita' del DB e' lo spike TSK-1037): due macchine con bundle diversi possono
dare esiti diversi; un albero senza file IaC da' PASS vuoto.

CLI: iac_guard.py CODE_PATH [--root FACTORY] [--json]   exit 0 PASS, 1 FAIL, 2 rifiutato, 3 NON_VERIFICABILE
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oracolo_statico as os_  # noqa: E402


def comando(exe, albero, ruleset, uscita):
    return [exe, "config", "--format", "json", "--output", uscita, "--config", ruleset, "--quiet",
            "--skip-check-update", "."]


def analizza(dati, albero, ruleset):
    out = []
    for res in dati.get("Results") or []:
        target = res["Target"]
        for m in res.get("Misconfigurations") or []:
            if m.get("Status", "FAIL") == "FAIL":
                out.append({"rule_id": m["ID"], "path": target, "symbol": ""})
    return out


TRIVY = os_.Scanner("trivy", "trivy_config", (".trivyignore", ".trivyignore.yaml", "trivy.yaml"),
                    ("trivy:ignore", ".trivyignore", ".trivyignore.yaml"), comando, analizza, exit_ok=(0,))

if __name__ == "__main__":
    sys.exit(os_.main(TRIVY))

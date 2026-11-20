#!/usr/bin/env python3
"""Valida un contratto JSON tra agenti contro lo schema versionato.

Uso: validate-contratto.py <contratto|path-schema> <file.json>
  <contratto> e' il nome di uno schema in schemas/contratti/ (proposed_pages,
  task_package) oppure il percorso di un file schema .json.

Exit: 0 valido; 1 non valido (file malformato o non conforme);
      2 schema assente/illeggibile o keyword fuori allowlist. Mai 0 senza schema.

Cosa NON garantisce: la forma valida non prova la verita' del contenuto. Un
claim con citazione ben formata puo' citare una fonte inesistente o che non dice
quanto affermato; il validatore controlla solo struttura, tipi e pattern.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from tools.lib.schema_min import SchemaError, validate  # noqa: E402

SCHEMAS = ROOT / "schemas" / "contratti"


def resolve_schema(name: str) -> Path:
    direct = Path(name)
    if direct.suffix == ".json" or direct.exists():
        return direct
    return SCHEMAS / f"{name}.schema.json"


def main(argv: list) -> int:
    if len(argv) != 3:
        print(__doc__.split("Exit:")[0].strip(), file=sys.stderr)
        return 2
    schema_path = resolve_schema(argv[1])
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"schema illeggibile {schema_path}: {exc}", file=sys.stderr)
        return 2
    try:
        doc = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"non valido: file illeggibile o JSON malformato: {exc}")
        return 1
    try:
        errors = validate(doc, schema)
    except SchemaError as exc:
        print(f"schema non utilizzabile: {exc}", file=sys.stderr)
        return 2
    if errors:
        print("non valido:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("valido")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

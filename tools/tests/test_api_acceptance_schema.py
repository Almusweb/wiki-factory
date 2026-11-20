"""Valida gli esempi dello schema api-acceptance-spec.

jsonschema non e' una dipendenza del repo: si usa un validatore minimale che copre
le parole chiave presenti nello schema (type, enum, required, properties, items,
additionalProperties, minimum, maximum, minItems), piu' i vincoli incrociati
elencati nell'intestazione dello schema.
"""
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from tools.lib.schema_min import validate  # noqa: E402

DIR = Path(__file__).resolve().parent.parent.parent / ".claude" / "schemas"


def load(name):
    return yaml.safe_load((DIR / name).read_text(encoding="utf-8"))


def cross_checks(spec):
    errors = []
    fixtures = [f for group in (spec.get("fixtures") or {}).values() for f in group]
    steps = spec.get("scenario") or []
    for label, items in (("fixtures", fixtures), ("scenario", steps), ("assertions", spec.get("assertions") or [])):
        ids = [i.get("id") for i in items]
        if len(ids) != len(set(ids)):
            errors.append(f"{label}: id duplicati")
    fixture_ids = {f.get("id") for f in fixtures}
    step_ids = {s.get("id") for s in steps}
    for s in steps:
        for fid in s.get("uses_fixtures", []):
            if fid not in fixture_ids:
                errors.append(f"scenario {s.get('id')}: fixture {fid} inesistente")
    for a in spec.get("assertions") or []:
        if a.get("step") not in step_ids:
            errors.append(f"assertion {a.get('id')}: step {a.get('step')} inesistente")
    target = spec.get("target") or {}
    if target.get("mode") == "http" and "base_url" not in target:
        errors.append("target: mode http richiede base_url")
    return errors


def check(name):
    spec = load(name)
    return validate(spec, load("api-acceptance-spec.schema.yaml")) + cross_checks(spec)


def test_valid_example_passes():
    assert check("api-acceptance-spec.example.yaml") == []


def test_invalid_example_is_rejected():
    errors = "\n".join(check("api-acceptance-spec.example.invalid.yaml"))
    for expected in ("manca thresholds", "grpc", "FETCH", "status_between", "step missing inesistente", "info"):
        assert expected in errors, expected


def test_fe_schema_untouched_and_loadable():
    # lo schema FE contiene segnaposto (<integer>) ma resta un documento YAML valido
    assert load("acceptance-spec.schema.yaml") is not None

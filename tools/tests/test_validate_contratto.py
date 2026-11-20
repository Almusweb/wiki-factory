"""Test del validatore dei contratti tra agenti (modulo e CLI)."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from tools.lib.schema_min import SchemaError, validate  # noqa: E402

CLI = ROOT / "tools" / "contratti" / "validate-contratto.py"

PAGES = {
    "source_txt": "raw/a.txt",
    "proposed_pages": [{
        "path": "wiki/concepts/x.md", "type": "concept", "status": "draft", "title": "X",
        "sources": ["raw/a.txt"], "summary_3lines": "s",
        "claims": [{"text": "t", "cite": "[^src: raw/a.txt p.1]"}],
        "wikilinks_out": ["y"],
    }],
    "gaps_opened": [{"slug": "g", "reason": "r", "blocking": False}],
    "contradictions_flagged": [{"target_page": "wiki/concepts/z.md", "summary": "s"}],
}
PACKAGE = {
    "tsk_id": "TSK-1", "iter": 1,
    "constraint": {"scope": "fix only", "max_diff_lines": 80},
    "actions": [{
        "rule_id": "R1", "rule_ref": "code_quality/rules/canonical/R1.md", "file": "a.py",
        "lines": [1, 3], "current_snippet": "x", "expected_fix": "y", "acceptance_criteria": "z",
    }],
    "report_ref": "code_quality/reports/TSK-1-iter-1.md",
    "previous_files_modified": [],
}


def run(tmp_path, contratto, doc, raw=None):
    f = tmp_path / "in.json"
    f.write_text(raw if raw is not None else json.dumps(doc), encoding="utf-8")
    return subprocess.run([sys.executable, str(CLI), contratto, str(f)], capture_output=True, text=True)


@pytest.mark.parametrize("name,doc", [("proposed_pages", PAGES), ("task_package", PACKAGE)])
def test_valid_fixture_exit_0(tmp_path, name, doc):
    assert run(tmp_path, name, doc).returncode == 0


def test_missing_required_exit_1(tmp_path):
    bad = copy.deepcopy(PAGES)
    del bad["gaps_opened"]
    r = run(tmp_path, "proposed_pages", bad)
    assert r.returncode == 1 and "gaps_opened" in r.stdout


def test_bad_cite_and_enum_exit_1(tmp_path):
    bad = copy.deepcopy(PAGES)
    bad["proposed_pages"][0]["claims"][0]["cite"] = "nessuna"
    bad["proposed_pages"][0]["type"] = "blog"
    r = run(tmp_path, "proposed_pages", bad)
    assert r.returncode == 1 and "pattern" in r.stdout and "blog" in r.stdout


def test_extra_field_and_empty_actions_exit_1(tmp_path):
    bad = copy.deepcopy(PACKAGE)
    bad["actions"] = []
    bad["extra"] = 1
    r = run(tmp_path, "task_package", bad)
    assert r.returncode == 1 and "extra" in r.stdout


def test_malformed_json_exit_1(tmp_path):
    assert run(tmp_path, "task_package", None, raw="{non json").returncode == 1


def test_unknown_keyword_exit_2(tmp_path):
    schema = tmp_path / "s.json"
    schema.write_text(json.dumps({"type": "object", "oneOf": []}), encoding="utf-8")
    r = run(tmp_path, str(schema), {})
    assert r.returncode == 2 and "oneOf" in r.stderr


def test_missing_schema_never_zero(tmp_path):
    assert run(tmp_path, "inesistente", {}).returncode == 2
    assert run(tmp_path, str(tmp_path / "manca.json"), {}).returncode == 2


def test_unreadable_schema_exit_2(tmp_path):
    schema = tmp_path / "s.json"
    schema.write_text("{rotto", encoding="utf-8")
    assert run(tmp_path, str(schema), {}).returncode == 2


def test_module_rejects_unknown_keyword_even_if_nested():
    with pytest.raises(SchemaError):
        validate({"a": 1}, {"type": "object", "properties": {"a": {"type": "integer", "oneOf": []}}})


def test_module_pattern_and_minlength():
    s = {"type": "string", "pattern": "^a", "minLength": 2}
    assert validate("ab", s) == []
    assert len(validate("b", s)) == 2


@pytest.mark.parametrize("skill,contract", [
    (".claude/skills/ingest-protocol.md", "proposed_pages"),
    (".claude/skills/code-review-protocol.md", "task_package"),
])
def test_protocols_prescribe_validator_step(skill, contract):
    text = (ROOT / skill).read_text(encoding="utf-8")
    assert f"tools/contratti/validate-contratto.py {contract}" in text
    assert "comportamentale" in text
    assert "non prova" in text


def test_module_ref_const_union_e_additionalproperties_schema():
    root = {"$defs": {"N": {"type": ["string", "null"], "maxLength": 3}},
            "type": "object", "properties": {"k": {"const": "x"}, "n": {"$ref": "#/$defs/N"}},
            "additionalProperties": {"type": "integer"}}
    assert validate({"k": "x", "n": None, "extra": 1}, root) == []
    errs = validate({"k": "y", "n": "lungo", "extra": "s"}, root)
    assert len(errs) == 3


def test_module_ref_non_locale_rifiutato():
    with pytest.raises(SchemaError):
        validate({}, {"$ref": "https://example.com/s.json"})


def test_module_format_e_annotazione_non_validata():
    # `format` non e' validato: dichiarato nel docstring («Cosa NON garantisce»).
    assert validate("non-una-data", {"type": "string", "format": "date-time"}) == []

"""Validatore minimale di schemi JSON, in sola libreria standard.

jsonschema non e' una dipendenza del repo. Questo modulo copre un sottoinsieme
esplicito di parole chiave e, a differenza di un validatore permissivo, rifiuta
ogni parola chiave fuori allowlist con SchemaError (fail-closed): uno schema che
usa una keyword non supportata non puo' dare un esito «valido».

Cosa NON garantisce: la forma valida non prova la verita' del contenuto (per
esempio che le citazioni di un claim esistano o dicano cio' che si afferma);
risolve solo `$ref` locali verso `#/$defs/<nome>` (o `#/definitions/<nome>`) rispetto alla
radice dello schema; non supporta oneOf/anyOf/allOf ne' vincoli incrociati; `format` e
`default` sono annotazioni e NON vengono validati (come in JSON Schema 2020-12 per default).
"""
from __future__ import annotations

import re
from typing import Any, Dict, List

TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "null": type(None),
}

# Keyword di validazione supportate.
VALIDATION_KEYWORDS = {
    "type", "enum", "minimum", "maximum", "required", "properties",
    "additionalProperties", "minItems", "items", "pattern", "minLength",
    "maxLength", "const", "$ref", "$defs", "definitions",
}
# Keyword di sola annotazione: non influiscono sull'esito.
ANNOTATION_KEYWORDS = {"$schema", "$id", "title", "description", "default", "format"}
ALLOWLIST = VALIDATION_KEYWORDS | ANNOTATION_KEYWORDS


class SchemaError(Exception):
    """Schema non utilizzabile: keyword fuori allowlist o forma non valida."""


def _type_list(t: Any) -> List[str]:
    return list(t) if isinstance(t, list) else [t]


def _resolve(ref: Any, root: Dict[str, Any], path: str) -> Dict[str, Any]:
    if not isinstance(ref, str):
        raise SchemaError(f"{path}.$ref: atteso stringa")
    for prefix, key in (("#/$defs/", "$defs"), ("#/definitions/", "definitions")):
        if ref.startswith(prefix):
            target = root.get(key, {}).get(ref[len(prefix):])
            if not isinstance(target, dict):
                raise SchemaError(f"{path}.$ref: riferimento non risolto {ref!r}")
            return target
    raise SchemaError(f"{path}.$ref: supportati solo riferimenti locali #/$defs/<nome> ({ref!r})")


def check_schema(schema: Any, path: str = "$", root: Any = None) -> None:
    """Solleva SchemaError se lo schema usa keyword o tipi non supportati."""
    if not isinstance(schema, dict):
        raise SchemaError(f"{path}: lo schema deve essere un oggetto")
    root = schema if root is None else root
    for key in schema:
        if key not in ALLOWLIST:
            raise SchemaError(f"{path}: keyword non supportata {key!r}")
    t = schema.get("type")
    if t is not None:
        for one in _type_list(t):
            if one not in TYPES:
                raise SchemaError(f"{path}: type non supportato {one!r}")
    if "pattern" in schema:
        try:
            re.compile(schema["pattern"])
        except (re.error, TypeError) as exc:
            raise SchemaError(f"{path}: pattern non valido ({exc})")
    if "$ref" in schema:
        _resolve(schema["$ref"], root, path)   # verifica che si risolva; i $defs si controllano a parte
    for key in ("$defs", "definitions"):
        defs = schema.get(key)
        if defs is not None:
            if not isinstance(defs, dict):
                raise SchemaError(f"{path}.{key}: atteso oggetto")
            for name, sub in defs.items():
                check_schema(sub, f"{path}.{key}.{name}", root)
    props = schema.get("properties", {})
    if not isinstance(props, dict):
        raise SchemaError(f"{path}.properties: atteso oggetto")
    for name, sub in props.items():
        check_schema(sub, f"{path}.{name}", root)
    ap = schema.get("additionalProperties")
    if ap is not None:
        if isinstance(ap, dict):
            check_schema(ap, f"{path}.additionalProperties", root)
        elif not isinstance(ap, bool):
            raise SchemaError(f"{path}.additionalProperties: atteso booleano o schema")
    if "items" in schema:
        check_schema(schema["items"], f"{path}[]", root)


def _is_int(node: Any) -> bool:
    return isinstance(node, int) and not isinstance(node, bool)


def _matches_type(node: Any, t: str) -> bool:
    if t in ("integer", "number") and isinstance(node, bool):
        return False
    if t == "integer":
        return _is_int(node) or (isinstance(node, float) and node.is_integer())
    return isinstance(node, TYPES[t])


def _validate(node: Any, schema: Dict[str, Any], path: str, root: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if "$ref" in schema:
        errors += _validate(node, _resolve(schema["$ref"], root, path), path, root)
    t = schema.get("type")
    if t:
        types = _type_list(t)
        if not any(_matches_type(node, one) for one in types):
            return errors + [f"{path}: atteso {' | '.join(types)}"]
    if "const" in schema and node != schema["const"]:
        errors.append(f"{path}: atteso il valore {schema['const']!r}")
    if "enum" in schema and node not in schema["enum"]:
        errors.append(f"{path}: {node!r} non in {schema['enum']}")
    if isinstance(node, (int, float)) and not isinstance(node, bool):
        if "minimum" in schema and node < schema["minimum"]:
            errors.append(f"{path}: sotto il minimo")
        if "maximum" in schema and node > schema["maximum"]:
            errors.append(f"{path}: sopra il massimo")
    if isinstance(node, str):
        if "minLength" in schema and len(node) < schema["minLength"]:
            errors.append(f"{path}: stringa troppo corta")
        if "maxLength" in schema and len(node) > schema["maxLength"]:
            errors.append(f"{path}: stringa troppo lunga")
        if "pattern" in schema and not re.search(schema["pattern"], node):
            errors.append(f"{path}: non rispetta il pattern {schema['pattern']!r}")
    if isinstance(node, dict):
        props = schema.get("properties", {})
        ap = schema.get("additionalProperties")
        for req in schema.get("required", []):
            if req not in node:
                errors.append(f"{path}: manca {req}")
        for k, v in node.items():
            if k in props:
                errors += _validate(v, props[k], f"{path}.{k}", root)
            elif ap is False:
                errors.append(f"{path}: campo non ammesso {k}")
            elif isinstance(ap, dict):
                errors += _validate(v, ap, f"{path}.{k}", root)
    if isinstance(node, list):
        if "minItems" in schema and len(node) < schema["minItems"]:
            errors.append(f"{path}: troppo corto")
        if "items" in schema:
            for i, el in enumerate(node):
                errors += _validate(el, schema["items"], f"{path}[{i}]", root)
    return errors


def validate(node: Any, schema: Any, path: str = "$", root: Any = None) -> List[str]:
    """Ritorna la lista degli errori (vuota = valido).

    `root` e' lo schema contro cui risolvere i `$ref` locali (default: `schema`).
    Solleva SchemaError se lo schema usa keyword fuori allowlist.
    """
    root = schema if root is None else root
    check_schema(schema, path, root)
    return _validate(node, schema, path, root)

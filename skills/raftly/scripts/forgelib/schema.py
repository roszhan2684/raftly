"""A small JSON Schema validator (draft 2020-12 subset), standard library only.

Supported keywords: type, enum, const, properties, required,
additionalProperties, patternProperties, items, minItems, maxItems,
uniqueItems, minLength, maxLength, pattern, minimum, maximum, format
(date, date-time), $ref (local ``#/$defs/...`` only), allOf, anyOf, oneOf,
not, if/then. Unknown keywords such as title/description are ignored.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .fsutil import SKILL_ROOT

SCHEMA_DIR = SKILL_ROOT / "schemas"

_TYPES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:?\d{2})?$")


class SchemaError(Exception):
    pass


def load_schema(name: str) -> dict:
    path = SCHEMA_DIR / (name if name.endswith(".json") else f"{name}.schema.json")
    if not path.exists():
        raise SchemaError(f"schema not found: {path.name}")
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def validate(instance: Any, schema: dict, root: dict | None = None, path: str = "$") -> list[str]:
    """Return a list of human-readable errors (empty list == valid)."""
    root = root if root is not None else schema
    errors: list[str] = []

    if schema is True or schema == {}:
        return errors
    if schema is False:
        return [f"{path}: value not allowed"]

    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/"):
            raise SchemaError(f"only local $ref supported: {ref}")
        target: Any = root
        for part in ref[2:].split("/"):
            target = target[part]
        errors.extend(validate(instance, target, root, path))

    t = schema.get("type")
    if t is not None:
        types = t if isinstance(t, list) else [t]
        if not any(_TYPES[x](instance) for x in types):
            errors.append(f"{path}: expected {' or '.join(types)}, got {_typename(instance)}")
            return errors

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} is not one of {schema['enum']}")
    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: expected {schema['const']!r}")

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: shorter than {schema['minLength']}")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            errors.append(f"{path}: longer than {schema['maxLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append(f"{path}: {instance!r} does not match {schema['pattern']}")
        fmt = schema.get("format")
        if fmt == "date" and not _DATE_RE.match(instance):
            errors.append(f"{path}: {instance!r} is not a YYYY-MM-DD date")
        if fmt == "date-time" and not _DATETIME_RE.match(instance):
            errors.append(f"{path}: {instance!r} is not an ISO-8601 date-time")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: {instance} < minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: {instance} > maximum {schema['maximum']}")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: fewer than {schema['minItems']} items")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path}: more than {schema['maxItems']} items")
        if schema.get("uniqueItems"):
            seen = []
            for item in instance:
                key = json.dumps(item, sort_keys=True, default=str)
                if key in seen:
                    errors.append(f"{path}: duplicate item {item!r}")
                seen.append(key)
        if "items" in schema:
            for i, item in enumerate(instance):
                errors.extend(validate(item, schema["items"], root, f"{path}[{i}]"))

    if isinstance(instance, dict):
        props = schema.get("properties", {})
        for req in schema.get("required", []):
            if req not in instance:
                errors.append(f"{path}: missing required field '{req}'")
        pattern_props = schema.get("patternProperties", {})
        for key, value in instance.items():
            sub = f"{path}.{key}"
            matched = False
            if key in props:
                matched = True
                errors.extend(validate(value, props[key], root, sub))
            for pat, pschema in pattern_props.items():
                if re.search(pat, key):
                    matched = True
                    errors.extend(validate(value, pschema, root, sub))
            if not matched:
                addl = schema.get("additionalProperties", True)
                if addl is False:
                    errors.append(f"{path}: unexpected field '{key}'")
                elif isinstance(addl, dict):
                    errors.extend(validate(value, addl, root, sub))

    for sub in schema.get("allOf", []):
        errors.extend(validate(instance, sub, root, path))
    if "anyOf" in schema:
        if not any(not validate(instance, s, root, path) for s in schema["anyOf"]):
            errors.append(f"{path}: does not match any allowed shape")
    if "oneOf" in schema:
        n = sum(1 for s in schema["oneOf"] if not validate(instance, s, root, path))
        if n != 1:
            errors.append(f"{path}: must match exactly one allowed shape (matched {n})")
    if "not" in schema and not validate(instance, schema["not"], root, path):
        errors.append(f"{path}: matches a forbidden shape")
    if "if" in schema and not validate(instance, schema["if"], root, path):
        if "then" in schema:
            errors.extend(validate(instance, schema["then"], root, path))
    elif "if" in schema and "else" in schema:
        errors.extend(validate(instance, schema["else"], root, path))

    return errors


def _typename(v: Any) -> str:
    for name in ("null", "boolean", "integer", "number", "string", "array", "object"):
        if _TYPES[name](v):
            return name
    return type(v).__name__


def validate_named(instance: Any, name: str) -> list[str]:
    return validate(instance, load_schema(name))


def schema_files() -> list[Path]:
    return sorted(SCHEMA_DIR.glob("*.schema.json"))

"""Turn compact ``field:type[:description]`` specs into a JSON Schema dict.

Example::

    build_object_schema(["name:str", "age:int", "bio:str:a short biography", "tags:str[]"])

produces an object schema with string/integer/string/array-of-string properties.
The result is consumed by ``session.respond(json_schema=...)`` for structured output.
"""

from __future__ import annotations

_TYPE_MAP = {
    "str": "string",
    "string": "string",
    "int": "integer",
    "integer": "integer",
    "float": "number",
    "number": "number",
    "bool": "boolean",
    "boolean": "boolean",
}

_SUPPORTED_KINDS = ("object",)


class SchemaSpecError(ValueError):
    """Raised when a field spec or schema kind can't be parsed."""


def _types_help() -> str:
    return ", ".join(sorted(set(_TYPE_MAP)))


def _field_type(token: str) -> dict:
    is_array = token.endswith("[]")
    base = token[:-2] if is_array else token
    json_type = _TYPE_MAP.get(base.lower())
    if json_type is None:
        raise SchemaSpecError(
            f"Unknown type {base!r}. Supported: {_types_help()} "
            f"(append [] for an array, e.g. str[])."
        )
    if is_array:
        return {"type": "array", "items": {"type": json_type}}
    return {"type": json_type}


def parse_field(spec: str) -> tuple[str, dict]:
    """Parse one ``name:type[:description]`` token into ``(name, property_schema)``."""
    parts = spec.split(":", 2)
    if len(parts) < 2 or not parts[0]:
        raise SchemaSpecError(
            f"Bad field {spec!r}. Expected name:type or name:type:description "
            f"(e.g. age:int or bio:str:a short biography)."
        )
    name, type_token = parts[0], parts[1]
    prop = _field_type(type_token)
    if len(parts) == 3 and parts[2]:
        prop["description"] = parts[2]
    return name, prop


def build_object_schema(fields: list[str], *, title: str | None = None) -> dict:
    """Build a JSON Schema object from field specs. All fields are required."""
    if not fields:
        raise SchemaSpecError("No fields given. Example: fmx schema object name:str age:int")
    properties: dict[str, dict] = {}
    required: list[str] = []
    for spec in fields:
        name, prop = parse_field(spec)
        if name in properties:
            raise SchemaSpecError(f"Duplicate field {name!r}.")
        properties[name] = prop
        required.append(name)
    # Apple's on-device schema decoder requires `additionalProperties`, `x-order`
    # (property ordering), and `title` in addition to vanilla JSON Schema.
    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
        "x-order": list(properties.keys()),
        "title": title or "Output",
    }


def build_schema(kind: str, fields: list[str], *, title: str | None = None) -> dict:
    """Dispatch on schema kind. Only ``object`` is supported today."""
    if kind not in _SUPPORTED_KINDS:
        raise SchemaSpecError(
            f"Unsupported schema kind {kind!r}. Supported: {', '.join(_SUPPORTED_KINDS)}."
        )
    return build_object_schema(fields, title=title)

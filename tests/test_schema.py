"""Pure-logic tests for schema spec parsing — no SDK required, runs anywhere."""

import pytest

from fmx import schema


def test_basic_object():
    result = schema.build_object_schema(["name:str", "age:int"])
    assert result == {
        "type": "object",
        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
        "required": ["name", "age"],
        "additionalProperties": False,
        "x-order": ["name", "age"],
        "title": "Output",
    }


def test_description_and_array():
    result = schema.build_object_schema(["bio:str:a short biography", "tags:str[]"])
    assert result["properties"]["bio"] == {"type": "string", "description": "a short biography"}
    assert result["properties"]["tags"] == {"type": "array", "items": {"type": "string"}}


def test_all_scalar_types():
    result = schema.build_object_schema(["a:str", "b:int", "c:float", "d:bool"])
    types = {k: v["type"] for k, v in result["properties"].items()}
    assert types == {"a": "string", "b": "integer", "c": "number", "d": "boolean"}


def test_description_with_colon_is_preserved():
    # split(":", 2) keeps colons in the description.
    _, prop = schema.parse_field("when:str:time, e.g. 3:00pm")
    assert prop["description"] == "time, e.g. 3:00pm"


@pytest.mark.parametrize("bad", ["x:widget", "notype", "", ":str"])
def test_invalid_field_raises(bad):
    with pytest.raises(schema.SchemaSpecError):
        schema.build_object_schema([bad])


def test_empty_fields_raises():
    with pytest.raises(schema.SchemaSpecError):
        schema.build_object_schema([])


def test_duplicate_field_raises():
    with pytest.raises(schema.SchemaSpecError):
        schema.build_object_schema(["a:str", "a:int"])


def test_unsupported_kind_raises():
    with pytest.raises(schema.SchemaSpecError):
        schema.build_schema("array", ["a:str"])


def test_title_is_added():
    result = schema.build_object_schema(["a:str"], title="Thing")
    assert result["title"] == "Thing"

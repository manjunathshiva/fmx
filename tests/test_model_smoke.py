"""End-to-end smoke tests that actually hit the on-device model.

Marked `require_model`; conftest skips them when no model is available.
"""

import asyncio

import pytest

try:
    from fmx import core, respond, schema
except Exception:
    pytest.skip("apple-fm-sdk unavailable", allow_module_level=True)

pytestmark = pytest.mark.require_model


def test_model_reports_available():
    ok, message = core.availability()
    assert ok is True
    assert message is None


def test_basic_respond(capsys):
    asyncio.run(respond.run_respond("Reply with exactly the word: pong"))
    out = capsys.readouterr().out.lower()
    assert "pong" in out


def test_structured_respond_is_valid_json(tmp_path, capsys):
    schema_file = tmp_path / "person.json"
    schema_file.write_text(
        __import__("json").dumps(schema.build_object_schema(["name:str", "age:int"]))
    )
    asyncio.run(respond.run_respond("Make up a person.", schema_path=schema_file))
    payload = __import__("json").loads(capsys.readouterr().out)
    assert "name" in payload and "age" in payload

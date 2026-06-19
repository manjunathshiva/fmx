"""CLI wiring tests. Skipped if apple-fm-sdk can't be imported (e.g. non-macOS-26 CI)."""

import json

import pytest

try:
    from fmx import cli
except Exception:  # SDK / C bindings unavailable on this platform
    pytest.skip("fmx.cli unavailable (apple-fm-sdk import failed)", allow_module_level=True)

from typer.testing import CliRunner

runner = CliRunner()


def test_version():
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert "fmx" in result.stdout


def test_schema_command_emits_json():
    result = runner.invoke(cli.app, ["schema", "object", "name:str", "age:int"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["properties"]["age"] == {"type": "integer"}
    assert data["required"] == ["name", "age"]


def test_schema_command_bad_field_exits_nonzero():
    result = runner.invoke(cli.app, ["schema", "object", "oops"])
    assert result.exit_code == 1


def test_no_args_shows_help():
    result = runner.invoke(cli.app, [])
    # no_args_is_help -> Typer exits 0 (or 2 on older versions) and prints usage
    assert "chat" in result.stdout and "respond" in result.stdout

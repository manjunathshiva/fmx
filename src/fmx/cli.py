"""Typer entry point wiring `fmx chat`, `fmx respond`, and `fmx schema`."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import typer
from rich.console import Console

from . import __version__, chat, core, respond, schema

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="A friendly CLI for Apple's on-device Foundation Model (macOS 26+).",
)
_err = Console(stderr=True)


def _require_model() -> None:
    ok, message = core.availability()
    if not ok:
        _err.print(f"[bold red]Foundation Models unavailable.[/]\n{message}")
        raise typer.Exit(1)


def _version_callback(value: bool) -> None:
    if value:
        print(f"fmx {__version__}")
        raise typer.Exit()


@app.callback()
def _main(
    _version: bool = typer.Option(
        False, "--version", callback=_version_callback, is_eager=True,
        help="Show the version and exit.",
    ),
) -> None:
    """fmx — chat, respond, and schema against Apple's on-device model."""


@app.command(name="chat")
def chat_cmd(
    instructions: str | None = typer.Option(
        None, "--instructions", "-i", help="System instructions for the assistant."
    ),
) -> None:
    """Start an interactive chat session."""
    _require_model()
    asyncio.run(chat.run_chat(instructions))


@app.command(name="respond")
def respond_cmd(
    prompt: str = typer.Argument(..., help="Prompt text, or '-' to read from stdin."),
    schema_file: Path | None = typer.Option(
        None, "--schema", help="JSON Schema file (or '-' for stdin) for structured JSON output."
    ),
    image: list[Path] | None = typer.Option(
        None, "--image", help="Attach an image (repeatable)."
    ),
    stream: bool = typer.Option(False, "--stream", help="Stream tokens as they generate."),
    instructions: str | None = typer.Option(
        None, "--instructions", "-i", help="System instructions."
    ),
    temperature: float | None = typer.Option(None, "--temperature", "-t"),
    max_tokens: int | None = typer.Option(None, "--max-tokens"),
) -> None:
    """Generate a single response and print it (great for scripting)."""
    _require_model()
    text = sys.stdin.read().strip() if prompt == "-" else prompt
    try:
        asyncio.run(
            respond.run_respond(
                text,
                schema_path=schema_file,
                images=list(image) if image else [],
                stream=stream,
                instructions=instructions,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        )
    except Exception as exc:  # surface SDK/IO errors cleanly, no traceback
        _err.print(f"[bold red]error:[/] {exc}")
        raise typer.Exit(1) from exc


@app.command(name="schema")
def schema_cmd(
    kind: str = typer.Argument("object", help="Schema kind (only 'object' is supported)."),
    fields: list[str] | None = typer.Argument(
        None, help="field:type[:description] specs, e.g. name:str age:int 'bio:str:short bio'."
    ),
    title: str | None = typer.Option(None, "--title", help="Optional schema title."),
) -> None:
    """Build a JSON Schema for structured output and print it to stdout."""
    try:
        result = schema.build_schema(kind, fields or [], title=title)
    except schema.SchemaSpecError as exc:
        _err.print(f"[bold red]error:[/] {exc}")
        raise typer.Exit(1) from exc
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    app()

"""One-shot generation for `fmx respond` — scripting-friendly, writes to stdout."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import apple_fm_sdk as fm

from . import core


def make_options(
    temperature: float | None, max_tokens: int | None
) -> fm.GenerationOptions | None:
    """Build GenerationOptions, or None when no knobs are set."""
    if temperature is None and max_tokens is None:
        return None
    return fm.GenerationOptions(temperature=temperature, maximum_response_tokens=max_tokens)


def _build_prompt(text: str, images: list[Path]):
    """Return a plain string, or a [text, ImageAttachment...] list for multimodal."""
    if not images:
        return text
    return [text, *(fm.ImageAttachment(p) for p in images)]


def _read_schema(schema_path: Path) -> dict:
    raw = sys.stdin.read() if str(schema_path) == "-" else schema_path.read_text()
    return json.loads(raw)


async def run_respond(
    prompt: str,
    *,
    schema_path: Path | None = None,
    images: list[Path] | None = None,
    stream: bool = False,
    instructions: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> None:
    """Generate a response and print it to stdout."""
    images = images or []
    session = core.make_session(instructions)
    options = make_options(temperature, max_tokens)
    prompt_arg = _build_prompt(prompt, images)

    if schema_path is not None:
        schema = _read_schema(schema_path)
        result = await session.respond(prompt_arg, json_schema=schema, options=options)
        # GeneratedContent.to_json() yields machine-parseable JSON.
        print(result.to_json())
        return

    if stream:
        shown = 0
        async for snapshot in session.stream_response(prompt_arg, options):
            sys.stdout.write(snapshot[shown:])
            sys.stdout.flush()
            shown = len(snapshot)
        sys.stdout.write("\n")
        return

    print(await session.respond(prompt_arg, options=options))

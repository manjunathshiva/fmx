"""Interactive REPL for `fmx chat` — multi-turn, streaming, with slash commands."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import apple_fm_sdk as fm
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

from . import core, store

_SLASH_HELP = [
    ("/help", "Show this help."),
    ("/save <path>", "Save the conversation to a JSON file."),
    ("/load <path>", "Load a conversation from a JSON file."),
    ("/clear", "Start a fresh conversation (keeps your instructions)."),
    ("/system <text>", "Replace the system instructions and start fresh."),
    ("/model", "Show model info (on-device only in this version)."),
    ("/exit", "Leave the chat (or press Ctrl-D)."),
]

_MODEL_NOTE = (
    "Running Apple's [bold]on-device[/] Foundation Model.\n"
    "Switching to Private Cloud Compute isn't available yet: the Python SDK "
    "(apple-fm-sdk) exposes only the on-device model. This will arrive with the "
    "native [bold]fm[/] tool in macOS 27, or when Apple ships PCC access in the SDK."
)


def _print_help(console: Console) -> None:
    table = Table(title="fmx chat — commands", show_header=True, header_style="bold")
    table.add_column("command", style="cyan", no_wrap=True)
    table.add_column("what it does")
    for cmd, desc in _SLASH_HELP:
        table.add_row(cmd, desc)
    console.print(table)


async def _respond_turn(
    console: Console, session: fm.LanguageModelSession, prompt: str
) -> None:
    """Stream one assistant turn; keep the REPL alive on model errors."""
    try:
        console.print("[bold green]fmx[/] ❯ ", end="")
        shown = 0
        async for snapshot in session.stream_response(prompt):
            sys.stdout.write(snapshot[shown:])
            sys.stdout.flush()
            shown = len(snapshot)
        sys.stdout.write("\n\n")
    except fm.FoundationModelsError as exc:
        console.print(f"\n[red]error:[/] {exc}\n")


async def run_chat(instructions: str | None = None) -> None:
    """Run the interactive chat loop until the user exits."""
    console = Console()
    session = core.make_session(instructions)
    current_instructions = instructions

    console.print("[bold]fmx chat[/] — Apple on-device Foundation Model")
    console.print("Type a message, or [cyan]/help[/] for commands. [cyan]/exit[/] to quit.\n")

    while True:
        try:
            line = (await asyncio.to_thread(console.input, "[bold cyan]you[/] ❯ ")).strip()
        except (EOFError, KeyboardInterrupt):
            console.print()
            break

        if not line:
            continue

        if not line.startswith("/"):
            await _respond_turn(console, session, line)
            continue

        cmd, _, arg = line[1:].partition(" ")
        cmd = cmd.lower()
        arg = arg.strip()

        if cmd in ("exit", "quit"):
            break
        elif cmd == "help":
            _print_help(console)
        elif cmd == "model":
            console.print(Markdown("---"))
            console.print(_MODEL_NOTE + "\n")
        elif cmd == "clear":
            session = core.make_session(current_instructions)
            console.print("[dim]Started a new conversation.[/]\n")
        elif cmd == "system":
            if not arg:
                console.print("[yellow]Usage: /system <instructions text>[/]\n")
                continue
            current_instructions = arg
            session = core.make_session(current_instructions)
            console.print("[dim]Updated instructions and started a new conversation.[/]\n")
        elif cmd == "save":
            if not arg:
                console.print("[yellow]Usage: /save <path>[/]\n")
                continue
            try:
                count = await store.save_session(session, Path(arg))
                console.print(f"[dim]Saved {count} entries to {arg}.[/]\n")
            except (OSError, fm.FoundationModelsError) as exc:
                console.print(f"[red]Could not save:[/] {exc}\n")
        elif cmd == "load":
            if not arg:
                console.print("[yellow]Usage: /load <path>[/]\n")
                continue
            try:
                session = await store.load_session(Path(arg))
                console.print(f"[dim]Loaded conversation from {arg}.[/]\n")
            except (OSError, ValueError, fm.FoundationModelsError) as exc:
                console.print(f"[red]Could not load:[/] {exc}\n")
        else:
            console.print(f"[yellow]Unknown command /{cmd}. Try /help.[/]\n")

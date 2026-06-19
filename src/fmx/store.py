"""Persist and resume chat sessions via the SDK's transcript serialization."""

from __future__ import annotations

import json
from pathlib import Path

import apple_fm_sdk as fm


async def save_session(session: fm.LanguageModelSession, path: Path) -> int:
    """Write the session's transcript to ``path`` as JSON. Returns entry count."""
    data = await session.transcript.to_dict()
    path.write_text(json.dumps(data, indent=2))
    return len(data.get("transcript", {}).get("entries", []))


async def load_session(path: Path) -> fm.LanguageModelSession:
    """Rebuild a session from a saved transcript file.

    Instructions are embedded in the transcript, so they're restored automatically.
    (Tool *capabilities* are not — this CLI's chat is tool-free.)
    """
    data = json.loads(path.read_text())
    transcript = await fm.Transcript.from_dict(data)
    return fm.LanguageModelSession.from_transcript(transcript)

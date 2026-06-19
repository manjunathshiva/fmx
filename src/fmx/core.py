"""Availability gate and session factory.

This is the single place where the on-device model is created, so a future
Private Cloud Compute / cloud backend can slot in here without touching the
command modules.
"""

from __future__ import annotations

import apple_fm_sdk as fm

SUPPORT_URL = "https://support.apple.com/en-us/121115"

_REASON_HELP = {
    fm.SystemLanguageModelUnavailableReason.APPLE_INTELLIGENCE_NOT_ENABLED: (
        "Apple Intelligence is turned off. Enable it in "
        "System Settings → Apple Intelligence & Siri, then try again."
    ),
    fm.SystemLanguageModelUnavailableReason.DEVICE_NOT_ELIGIBLE: (
        "This Mac isn't eligible. Apple Intelligence needs Apple silicon "
        f"(M1 or later). See {SUPPORT_URL}."
    ),
    fm.SystemLanguageModelUnavailableReason.MODEL_NOT_READY: (
        "The model is still downloading or preparing. Wait a few minutes "
        "and try again."
    ),
}


def availability() -> tuple[bool, str | None]:
    """Return ``(is_available, help_message)``.

    ``help_message`` is ``None`` when available, otherwise an actionable string.
    """
    ok, reason = fm.SystemLanguageModel().is_available()
    if ok:
        return True, None
    label = getattr(reason, "name", reason)
    return False, _REASON_HELP.get(reason, f"Foundation Models are unavailable ({label}).")


def make_session(instructions: str | None = None) -> fm.LanguageModelSession:
    """Create a fresh on-device session.

    The future seam: a PCC/cloud backend would branch here once the SDK exposes it.
    """
    return fm.LanguageModelSession(instructions=instructions)

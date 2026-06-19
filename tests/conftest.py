"""Auto-skip tests marked `require_model` when the on-device model isn't available."""

import pytest


def _model_available() -> bool:
    try:
        import apple_fm_sdk as fm
    except Exception:
        return False
    try:
        ok, _ = fm.SystemLanguageModel().is_available()
        return bool(ok)
    except Exception:
        return False


def pytest_collection_modifyitems(config, items):
    if _model_available():
        return
    skip = pytest.mark.skip(reason="on-device Foundation Model not available on this machine")
    for item in items:
        if "require_model" in item.keywords:
            item.add_marker(skip)

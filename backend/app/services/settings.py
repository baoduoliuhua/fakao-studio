import json
from pathlib import Path

from ..db import DATA_DIR


SETTINGS_PATH = DATA_DIR / "settings.json"

DEFAULTS = {
    "mock": True,
    "base_url": "https://api.deepseek.com/v1",
    "api_key": "",
    "model": "deepseek-chat",
}


def get_settings() -> dict:
    if not SETTINGS_PATH.exists():
        return dict(DEFAULTS)
    try:
        data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except Exception:
        data = {}
    return {**DEFAULTS, **data}


def save_settings(settings: dict) -> dict:
    merged = {**DEFAULTS, **settings}
    SETTINGS_PATH.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return merged

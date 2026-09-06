from fastapi import APIRouter

from ..schemas import SettingsOut, SettingsUpdate
from ..services.settings import get_settings, save_settings

router = APIRouter(prefix="/api", tags=["settings"])


@router.get("/settings", response_model=SettingsOut)
def read_settings():
    settings = get_settings()
    return {
        "mock": settings["mock"],
        "base_url": settings["base_url"],
        "api_key_set": bool(settings.get("api_key")),
        "model": settings["model"],
    }


@router.put("/settings", response_model=SettingsOut)
def update_settings(payload: SettingsUpdate):
    current = get_settings()
    updates = payload.model_dump(exclude_unset=True)
    if updates.get("api_key") is not None and updates["api_key"] == "":
        updates["api_key"] = current.get("api_key", "")
    saved = save_settings(updates)
    return {
        "mock": saved["mock"],
        "base_url": saved["base_url"],
        "api_key_set": bool(saved.get("api_key")),
        "model": saved["model"],
    }

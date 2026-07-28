import json
import logging
import os

from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger("agnes.settings")

router = APIRouter()

CONFIG_FILE = "config.json"


def _get_config_dir() -> str:
    """Ermittelt das Config-Verzeichnis (neben .exe oder CWD)."""
    # Vom Launcher gesetzt
    env_dir = os.environ.get("AGNES_CONFIG_DIR")
    if env_dir:
        return env_dir
    # Fallback: CWD
    return os.getcwd()


def _get_config_path() -> str:
    return os.path.join(_get_config_dir(), CONFIG_FILE)


def _load_config() -> dict:
    path = _get_config_path()
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            logger.warning("Could not read config.json", exc_info=True)
    return {}


def _save_config(data: dict) -> None:
    path = _get_config_path()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    logger.info("Settings saved to %s", path)


def _mask_key(key: str) -> str:
    """Zeigt nur die ersten 4 und letzten 4 Zeichen."""
    if len(key) <= 12:
        return key[:4] + "..." + key[-4:] if len(key) > 8 else key
    return key[:4] + "..." + key[-4:]


class SettingsResponse(BaseModel):
    configured: bool
    key_masked: str | None = None


class SettingsRequest(BaseModel):
    api_key: str


@router.get("/settings", response_model=SettingsResponse)
async def get_settings():
    config = _load_config()
    key = config.get("agnes_api_key", "") or ""
    if key:
        return SettingsResponse(configured=True, key_masked=_mask_key(key))
    return SettingsResponse(configured=False)


@router.post("/settings")
async def save_settings(body: SettingsRequest):
    key = body.api_key.strip()
    if not key:
        return {"status": "error", "message": "API key is empty"}

    config = _load_config()
    config["agnes_api_key"] = key
    _save_config(config)

    # Update runtime env
    os.environ["AGNES_API_KEY"] = key
    os.environ["OPENAI_API_KEY"] = key

    logger.info("API key updated via settings")
    return {"status": "ok", "key_masked": _mask_key(key)}

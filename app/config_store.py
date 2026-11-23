"""Configuración local (credenciales en %LOCALAPPDATA%, no en el repo)."""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

APP_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "BilkySubirFacturas"
SETTINGS_PATH = APP_DIR / "settings.json"


@dataclass
class AppSettings:
    bilky_user: str = ""
    bilky_password: str = ""
    show_browser: bool = True
    headless: bool = False
    last_folder: str = ""
    last_client_search: str = ""

    def masked_password(self) -> str:
        if not self.bilky_password:
            return ""
        if len(self.bilky_password) <= 2:
            return "•" * len(self.bilky_password)
        return self.bilky_password[0] + "•" * (len(self.bilky_password) - 2) + self.bilky_password[-1]


def ensure_app_dir() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)


def load_settings() -> AppSettings:
    ensure_app_dir()
    if not SETTINGS_PATH.exists():
        return AppSettings()
    try:
        data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        return AppSettings(**{k: v for k, v in data.items() if k in AppSettings.__dataclass_fields__})
    except (json.JSONDecodeError, TypeError):
        return AppSettings()


def save_settings(settings: AppSettings) -> None:
    ensure_app_dir()
    payload = asdict(settings)
    SETTINGS_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
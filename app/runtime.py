"""Rutas y Playwright en ejecutable empaquetado."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip() if (ROOT / "VERSION").exists() else "0.0.0"


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def app_base_dir() -> Path:
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return ROOT


def resource_path(*parts: str) -> Path:
    if is_frozen() and hasattr(sys, "_MEIPASS"):
        candidate = Path(sys._MEIPASS).joinpath(*parts)
        if candidate.exists():
            return candidate
    return ROOT.joinpath(*parts)


def configure_playwright_path() -> None:
    """Usa Chromium junto al .exe si existe la carpeta ms-playwright."""
    bundled = app_base_dir() / "ms-playwright"
    if bundled.is_dir():
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(bundled)
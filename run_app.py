"""Punto de entrada para desarrollo y empaquetado (flet pack)."""
from app.main import run_app
from app.runtime import configure_playwright_path

if __name__ == "__main__":
    configure_playwright_path()
    run_app()
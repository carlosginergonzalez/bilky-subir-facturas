"""Recorre el flujo post-login (diagnóstico)."""
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

URL = "https://asesoriacolon.bilky.es/"


def dump_interactive(page, label: str):
    print(f"\n=== {label} | {page.url} ===")
    for role, name in [
        ("link", None),
        ("button", None),
    ]:
        loc = page.get_by_role(role)
        n = min(loc.count(), 30)
        for i in range(n):
            el = loc.nth(i)
            try:
                t = (el.inner_text() or "").strip().replace("\n", " | ")
            except Exception:
                t = ""
            if t:
                print(f"  [{role}] {t[:100]}")


def main():
    user = os.environ.get("BILKY_USER", "")
    password = os.environ.get("BILKY_PASSWORD", "")
    if not user or not password:
        print("Define BILKY_USER y BILKY_PASSWORD en el entorno para esta prueba.")
        return 1

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=60_000)
        page.fill("#taxid", user)
        page.fill("#password", password)
        page.get_by_role("button", name="Iniciar sesión").click()
        page.wait_for_load_state("networkidle", timeout=60_000)
        dump_interactive(page, "Select empresa")

        # auth/select suele tener tarjetas con "Acceder"
        page.get_by_role("link", name="Acceder").first.click()
        page.wait_for_load_state("networkidle", timeout=60_000)
        dump_interactive(page, "Tras Acceder")

        # Menú documentación / gestión contable
        for text in (
            "Documentación",
            "Gestión contable",
            "Gestion contable",
            "CONTABILIDAD",
        ):
            loc = page.get_by_text(text, exact=False)
            if loc.count():
                print(f"Click text: {text!r} ({loc.count()} matches)")
                try:
                    loc.first.click(timeout=5000)
                    page.wait_for_load_state("networkidle", timeout=30_000)
                    dump_interactive(page, f"After {text}")
                except Exception as e:
                    print("  click failed:", e)

        # Buscar input de búsqueda clientes
        for inp in page.locator("input").all()[:15]:
            meta = inp.evaluate(
                """el => ({
                    type: el.type, name: el.name, id: el.id,
                    placeholder: el.placeholder, class: el.className
                })"""
            )
            print("input:", meta)

        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
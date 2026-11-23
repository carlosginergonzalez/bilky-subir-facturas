"""Diagnóstico: categoría → agregar archivos."""
import os
from playwright.sync_api import sync_playwright

URL = "https://asesoriacolon.bilky.es/"
CLIENT_SEARCH = "GINER GONZALEZ"


def login_and_open_client(page, user: str, password: str):
    page.goto(URL, wait_until="domcontentloaded", timeout=60_000)
    page.fill("#taxid", user)
    page.fill("#password", password)
    page.get_by_role("button", name="Iniciar sesión").click()
    page.wait_for_load_state("networkidle", timeout=60_000)
    if "/auth/select" in page.url:
        page.get_by_role("link", name="Acceder").first.click()
        page.wait_for_load_state("networkidle", timeout=60_000)
    page.get_by_role("link", name="Gestión Contable").click()
    page.wait_for_load_state("networkidle", timeout=60_000)
    page.locator("input.tag-search").fill(CLIENT_SEARCH)
    page.wait_for_timeout(1500)
    client_row = page.locator("tr", has_text="GINER GONZALEZ").first
    client_row.get_by_role("link", name="Acceder").click()
    page.wait_for_load_state("networkidle", timeout=60_000)
    page.get_by_text("Subir facturas", exact=False).first.click()
    page.wait_for_load_state("networkidle", timeout=60_000)


def main():
    user = os.environ["BILKY_USER"]
    password = os.environ["BILKY_PASSWORD"]
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        login_and_open_client(page, user, password)
        print("category URL:", page.url)
        for text in (
            "Factura recibida",
            "Factura emitida",
            "Otros",
            "recibida",
            "emitida",
        ):
            loc = page.get_by_text(text, exact=False)
            print(f"  {text!r}: {loc.count()}")
        page.get_by_text("Factura recibida", exact=False).first.click()
        page.wait_for_load_state("networkidle", timeout=60_000)
        print("after category:", page.url)
        print("file inputs:", page.locator('input[type="file"]').count())
        for t in ("agregar archivo", "Agregar", "Subir facturas"):
            print(t, page.get_by_text(t, exact=False).count())
        # dump links/buttons with text
        for el in page.locator("a, button, label").all()[:40]:
            tx = (el.inner_text() or "").strip().replace("\n", " ")
            if tx:
                print(" -", tx[:80])
        browser.close()


if __name__ == "__main__":
    main()
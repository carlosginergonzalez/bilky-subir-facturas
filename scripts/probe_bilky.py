"""Exploración rápida de la página de login (sin guardar credenciales)."""
from playwright.sync_api import sync_playwright

URL = "https://asesoriacolon.bilky.es/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, wait_until="networkidle", timeout=60_000)
    print("title:", page.title())
    inputs = page.locator("input").all()
    for i, inp in enumerate(inputs):
        attrs = inp.evaluate(
            """el => ({
                type: el.type,
                name: el.name,
                id: el.id,
                placeholder: el.placeholder,
                autocomplete: el.autocomplete,
            })"""
        )
        print(f"input[{i}]:", attrs)
    print("buttons:", [b.inner_text()[:50] for b in page.locator("button").all()[:10]])
    browser.close()
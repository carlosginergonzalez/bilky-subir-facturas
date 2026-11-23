"""Automatización del flujo de subida en Bilky (Playwright)."""
from __future__ import annotations

import re
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

from app.config_store import APP_DIR
from app.models import DocumentType, UploadJob, UploadResult
from app.runtime import configure_playwright_path

BILKY_URL = "https://asesoriacolon.bilky.es/"
LogFn = Callable[[str, str], None]


def _screenshot(page: Page, tag: str) -> Path:
    shots = APP_DIR / "screenshots"
    shots.mkdir(parents=True, exist_ok=True)
    path = shots / f"{datetime.now():%Y%m%d_%H%M%S}_{tag}.png"
    page.screenshot(path=str(path), full_page=True)
    return path


def _log(fn: LogFn | None, level: str, msg: str) -> None:
    if fn:
        fn(level, msg)


def list_pdfs(folder: Path) -> list[Path]:
    if not folder.is_dir():
        raise FileNotFoundError(f"La carpeta no existe: {folder}")
    pdfs = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".pdf")
    if not pdfs:
        raise ValueError(f"No hay PDF en la carpeta: {folder}")
    return pdfs


def _login(page: Page, user: str, password: str, log: LogFn | None) -> None:
    _log(log, "info", "Abriendo Bilky…")
    page.goto(BILKY_URL, wait_until="domcontentloaded", timeout=90_000)
    page.fill("#taxid", user)
    page.fill("#password", password)
    page.get_by_role("button", name="Iniciar sesión").click()
    page.wait_for_load_state("networkidle", timeout=90_000)
    if "/auth/select" in page.url:
        _log(log, "info", "Seleccionando portal del asesor…")
        page.get_by_role("link", name="Acceder").first.click()
        page.wait_for_load_state("networkidle", timeout=90_000)


def _open_gestion_contable(page: Page, log: LogFn | None) -> None:
    _log(log, "info", "Entrando en Gestión contable…")
    page.get_by_role("link", name=re.compile(r"Gestión\s+Contable", re.I)).click()
    page.wait_for_load_state("networkidle", timeout=90_000)


def _open_client(page: Page, client_search: str, log: LogFn | None) -> None:
    search = client_search.strip()
    if not search:
        raise ValueError("Indica un texto para buscar el cliente en Bilky.")
    _log(log, "info", f"Buscando cliente: {search!r}…")
    page.locator("input.tag-search").fill(search)
    page.wait_for_timeout(1200)
    rows = page.locator("tr").filter(has_text=re.compile(re.escape(search[:20]), re.I))
    if rows.count() == 0:
        rows = page.locator("tr").filter(has_text=re.compile(search.split()[0], re.I))
    if rows.count() == 0:
        shot = _screenshot(page, "cliente_no_encontrado")
        raise RuntimeError(
            "No se encontró ningún cliente con ese criterio. "
            "Prueba con otro fragmento del nombre (p. ej. apellidos)."
        ) from None
    row = rows.first
    name_cell = row.inner_text().strip().replace("\n", " ")
    _log(log, "info", f"Cliente localizado: {name_cell[:120]}")
    row.get_by_role("link", name="Acceder").click()
    page.wait_for_load_state("networkidle", timeout=90_000)


def _select_document_type(page: Page, doc: DocumentType, log: LogFn | None) -> None:
    _log(log, "info", "Abriendo subida de facturas…")
    page.get_by_text("Subir facturas", exact=False).first.click()
    page.wait_for_load_state("networkidle", timeout=90_000)
    _log(log, "info", f"Tipo de documento: {doc.value}")
    label = doc.value if doc != DocumentType.OTROS else "Otros"
    page.get_by_text(label, exact=False).first.click()
    page.wait_for_load_state("networkidle", timeout=90_000)


def _wait_uploads_settle(page: Page, file_count: int, log: LogFn | None) -> None:
    _log(log, "info", f"Esperando a que se suban {file_count} archivo(s)…")
    deadline = time.time() + max(120, file_count * 45)
    last = ""
    while time.time() < deadline:
        page.wait_for_timeout(800)
        body = page.locator("body").inner_text()
        lowered = body.lower()
        if "error" in lowered and "subir" in lowered:
            pass
        # Heurística: barra de progreso o texto de carga desaparece
        busy = page.locator("[class*='progress'], .spinner, .loading").count()
        if busy == 0 and "subiendo" not in lowered and "cargando" not in lowered:
            break
        snippet = body[:200].replace("\n", " ")
        if snippet != last:
            last = snippet
            _log(log, "debug", "Procesando en la web…")
    page.wait_for_load_state("networkidle", timeout=120_000)


def _confirm_upload(page: Page, log: LogFn | None) -> None:
    _log(log, "info", "Confirmando lote (Subir facturas)…")
    confirm = page.get_by_role("button", name=re.compile(r"Subir facturas", re.I))
    if confirm.count() == 0:
        confirm = page.get_by_text("Subir facturas", exact=False)
    # Último botón suele ser la confirmación del modal/página
    confirm.last.click()
    page.wait_for_load_state("networkidle", timeout=120_000)


def run_upload(job: UploadJob, on_log: LogFn | None = None) -> UploadResult:
    configure_playwright_path()
    pdfs = list_pdfs(job.folder)
    _log(on_log, "info", f"{len(pdfs)} PDF encontrados en la carpeta.")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=not job.show_browser)
            context = browser.new_context(locale="es-ES")
            page = context.new_page()
            try:
                _login(page, job.bilky_user, job.bilky_password, on_log)
                _open_gestion_contable(page, on_log)
                _open_client(page, job.client_search, on_log)
                _select_document_type(page, job.document_type, on_log)

                file_input = page.locator('input[type="file"]').first
                file_input.wait_for(state="attached", timeout=30_000)
                _log(on_log, "info", "Asignando archivos al formulario (sin diálogo de Windows)…")
                file_input.set_input_files([str(p) for p in pdfs])

                _wait_uploads_settle(page, len(pdfs), on_log)
                _confirm_upload(page, on_log)

                body = page.locator("body").inner_text()
                if "actualizad" in body.lower() or "subid" in body.lower() or "éxito" in body.lower():
                    msg = "Subida completada. Revisa Bilky por avisos (p. ej. duplicados)."
                else:
                    msg = "Proceso finalizado. Comprueba el resultado en Bilky."

                _log(on_log, "success", msg)
                return UploadResult(ok=True, message=msg, files_count=len(pdfs))
            except Exception as exc:
                shot = _screenshot(page, "error")
                _log(on_log, "error", str(exc))
                return UploadResult(
                    ok=False,
                    message=str(exc),
                    files_count=len(pdfs),
                    screenshot=shot,
                )
            finally:
                context.close()
                browser.close()
    except PlaywrightTimeout as exc:
        return UploadResult(ok=False, message=f"Tiempo de espera agotado: {exc}")
    except Exception as exc:
        return UploadResult(ok=False, message=str(exc))
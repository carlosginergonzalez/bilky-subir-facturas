"""
Bilky — Subir facturas · aplicación de escritorio para Windows.
"""
from __future__ import annotations

import threading
from pathlib import Path

import flet as ft

from app.automation.bilky_uploader import list_pdfs, run_upload
from app.config_store import AppSettings, load_settings, save_settings
from app.models import DocumentType, UploadJob
from app.runtime import VERSION, resource_path

ROOT = Path(__file__).resolve().parents[1]

PALETTE = {
    "bg": "#0f1419",
    "surface": "#1a2332",
    "surface2": "#243044",
    "primary": "#3b9ddd",
    "primary_dark": "#2878b4",
    "accent": "#5eead4",
    "text": "#e8eef4",
    "muted": "#94a3b8",
    "success": "#4ade80",
    "error": "#f87171",
    "warn": "#fbbf24",
}

LOG_COLORS = {
    "info": PALETTE["text"],
    "debug": PALETTE["muted"],
    "success": PALETTE["success"],
    "error": PALETTE["error"],
    "warn": PALETTE["warn"],
}


def main(page: ft.Page) -> None:
    settings = load_settings()
    uploading = {"active": False}

    page.title = f"Bilky · Subir facturas v{VERSION}"
    icon_path = resource_path("assets", "icon.ico")
    if icon_path.is_file():
        page.window.icon = str(icon_path)
    page.window.width = 1060
    page.window.height = 780
    page.window.min_width = 880
    page.window.min_height = 640
    page.padding = 0
    page.bgcolor = PALETTE["bg"]
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(
        color_scheme_seed=PALETTE["primary"],
        font_family="Segoe UI",
    )

    tf_user = ft.TextField(
        label="Usuario Bilky (NIF)",
        value=settings.bilky_user,
        border_radius=12,
        bgcolor=PALETTE["surface2"],
        border_color=ft.Colors.TRANSPARENT,
        focused_border_color=PALETTE["primary"],
        label_style=ft.TextStyle(color=PALETTE["muted"]),
        text_style=ft.TextStyle(color=PALETTE["text"]),
        expand=True,
    )
    tf_pass = ft.TextField(
        label="Contraseña",
        value=settings.bilky_password,
        password=True,
        can_reveal_password=True,
        border_radius=12,
        bgcolor=PALETTE["surface2"],
        border_color=ft.Colors.TRANSPARENT,
        focused_border_color=PALETTE["primary"],
        label_style=ft.TextStyle(color=PALETTE["muted"]),
        text_style=ft.TextStyle(color=PALETTE["text"]),
        expand=True,
    )
    sw_browser = ft.Switch(
        label="Mostrar navegador durante la subida",
        value=settings.show_browser,
        label_style=ft.TextStyle(color=PALETTE["text"], size=14),
        active_color=PALETTE["primary"],
    )

    tf_folder = ft.TextField(
        label="Carpeta con los PDF",
        value=settings.last_folder,
        read_only=True,
        border_radius=12,
        bgcolor=PALETTE["surface2"],
        border_color=ft.Colors.TRANSPARENT,
        label_style=ft.TextStyle(color=PALETTE["muted"]),
        text_style=ft.TextStyle(color=PALETTE["text"]),
        expand=True,
    )
    tf_client = ft.TextField(
        label="Buscar cliente en Bilky",
        hint_text="Ej.: GINER GONZALEZ",
        value=settings.last_client_search,
        border_radius=12,
        bgcolor=PALETTE["surface2"],
        border_color=ft.Colors.TRANSPARENT,
        focused_border_color=PALETTE["primary"],
        label_style=ft.TextStyle(color=PALETTE["muted"]),
        text_style=ft.TextStyle(color=PALETTE["text"]),
        expand=True,
    )
    dd_type = ft.Dropdown(
        label="Tipo de documento",
        value=DocumentType.RECIBIDA.value,
        options=[ft.dropdown.Option(v) for v in DocumentType.choices()],
        border_radius=12,
        bgcolor=PALETTE["surface2"],
        border_color=ft.Colors.TRANSPARENT,
        label_style=ft.TextStyle(color=PALETTE["muted"]),
        text_style=ft.TextStyle(color=PALETTE["text"]),
        expand=True,
    )
    lbl_pdfs = ft.Text("—", color=PALETTE["muted"], size=13)

    log_column = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=4, expand=True)
    progress = ft.ProgressRing(visible=False, width=28, height=28, color=PALETTE["accent"])
    status_chip = ft.Container(
        content=ft.Text("Listo", color=PALETTE["muted"], size=13),
        bgcolor=PALETTE["surface2"],
        border_radius=20,
        padding=ft.padding.symmetric(horizontal=14, vertical=8),
    )

    def refresh_pdf_count() -> None:
        path = tf_folder.value.strip()
        if not path:
            lbl_pdfs.value = "Selecciona una carpeta"
            lbl_pdfs.update()
            return
        try:
            n = len(list_pdfs(Path(path)))
            lbl_pdfs.value = f"{n} PDF en la carpeta"
            lbl_pdfs.color = PALETTE["accent"]
        except Exception as exc:
            lbl_pdfs.value = str(exc)
            lbl_pdfs.color = PALETTE["error"]
        lbl_pdfs.update()

    def append_log(level: str, message: str) -> None:
        log_column.controls.append(
            ft.Text(
                message,
                size=13,
                color=LOG_COLORS.get(level, PALETTE["text"]),
                selectable=True,
            )
        )
        if len(log_column.controls) > 400:
            log_column.controls.pop(0)
        log_column.update()

    def persist_settings() -> None:
        save_settings(
            AppSettings(
                bilky_user=tf_user.value.strip(),
                bilky_password=tf_pass.value,
                show_browser=sw_browser.value,
                headless=not sw_browser.value,
                last_folder=tf_folder.value.strip(),
                last_client_search=tf_client.value.strip(),
            )
        )

    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)

    async def pick_folder(_: ft.ControlEvent) -> None:
        path = await file_picker.get_directory_path(dialog_title="Carpeta con facturas PDF")
        if path:
            tf_folder.value = path
            tf_folder.update()
            refresh_pdf_count()
            persist_settings()

    def set_status(text: str, color: str = PALETTE["muted"]) -> None:
        status_chip.content = ft.Text(text, color=color, size=13)
        status_chip.update()

    def set_busy(busy: bool) -> None:
        uploading["active"] = busy
        btn_start.disabled = busy
        progress.visible = busy
        btn_start.update()
        progress.update()

    def on_log(level: str, msg: str) -> None:
        page.run_thread(lambda: append_log(level, msg))

    def worker() -> None:
        try:
            job = UploadJob(
                folder=Path(tf_folder.value.strip()),
                client_search=tf_client.value.strip(),
                document_type=DocumentType(dd_type.value),
                bilky_user=tf_user.value.strip(),
                bilky_password=tf_pass.value,
                show_browser=sw_browser.value,
            )
            result = run_upload(job, on_log=on_log)

            def finish() -> None:
                set_busy(False)
                if result.ok:
                    set_status(f"Completado · {result.files_count} archivos", PALETTE["success"])
                    append_log("success", result.message)
                else:
                    set_status("Error", PALETTE["error"])
                    append_log("error", result.message)
                    if result.screenshot:
                        append_log("info", f"Captura guardada: {result.screenshot}")
                persist_settings()

            page.run_thread(finish)
        except Exception as exc:
            def fail() -> None:
                set_busy(False)
                set_status("Error", PALETTE["error"])
                append_log("error", str(exc))

            page.run_thread(fail)

    def start_upload(_: ft.ControlEvent) -> None:
        if uploading["active"]:
            return
        if not tf_user.value.strip() or not tf_pass.value:
            page.open(ft.SnackBar(ft.Text("Indica usuario y contraseña de Bilky."), bgcolor=PALETTE["error"]))
            return
        if not tf_folder.value.strip():
            page.open(ft.SnackBar(ft.Text("Elige la carpeta con los PDF."), bgcolor=PALETTE["error"]))
            return
        if not tf_client.value.strip():
            page.open(ft.SnackBar(ft.Text("Indica cómo buscar el cliente en Bilky."), bgcolor=PALETTE["error"]))
            return
        try:
            list_pdfs(Path(tf_folder.value.strip()))
        except Exception as exc:
            page.open(ft.SnackBar(ft.Text(str(exc)), bgcolor=PALETTE["error"]))
            return

        log_column.controls.clear()
        log_column.update()
        set_status("Subiendo…", PALETTE["accent"])
        set_busy(True)
        persist_settings()
        threading.Thread(target=worker, daemon=True).start()

    btn_folder = ft.FilledButton(
        "Elegir carpeta",
        icon=ft.Icons.FOLDER_OPEN,
        style=ft.ButtonStyle(
            bgcolor=PALETTE["surface2"],
            color=PALETTE["text"],
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
        on_click=pick_folder,
    )
    btn_start = ft.FilledButton(
        "Iniciar subida",
        icon=ft.Icons.CLOUD_UPLOAD,
        style=ft.ButtonStyle(
            bgcolor=PALETTE["primary"],
            color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.padding.symmetric(horizontal=28, vertical=16),
        ),
        on_click=start_upload,
    )

    def card(title: str, subtitle: str, body: ft.Control) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(title, size=20, weight=ft.FontWeight.W_600, color=PALETTE["text"]),
                    ft.Text(subtitle, size=13, color=PALETTE["muted"]),
                    ft.Container(height=8),
                    body,
                ],
                spacing=6,
            ),
            bgcolor=PALETTE["surface"],
            border_radius=16,
            padding=24,
            border=ft.border.all(1, PALETTE["surface2"]),
        )

    header = ft.Container(
        content=ft.Row(
            [
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.ROCKET_LAUNCH, color=PALETTE["accent"], size=32),
                                ft.Text(
                                    "Bilky · Subir facturas",
                                    size=28,
                                    weight=ft.FontWeight.BOLD,
                                    color=PALETTE["text"],
                                ),
                            ],
                            spacing=12,
                        ),
                        ft.Text(
                            f"Sube un lote de PDF al portal del asesor · versión {VERSION}",
                            color=PALETTE["muted"],
                            size=14,
                        ),
                    ],
                    spacing=4,
                    expand=True,
                ),
                ft.Row([progress, status_chip], spacing=12),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=ft.padding.only(left=32, right=32, top=28, bottom=12),
    )

    credentials_card = card(
        "Acceso",
        "Las credenciales se guardan solo en este ordenador (%LOCALAPPDATA%).",
        ft.Column(
            [
                ft.Row([tf_user, tf_pass], spacing=16),
                sw_browser,
            ],
            spacing=16,
        ),
    )

    upload_card = card(
        "Lote de facturas",
        "La carpeta debe coincidir con el cliente que buscas en Gestión contable.",
        ft.Column(
            [
                ft.Row([tf_folder, btn_folder], spacing=12, vertical_alignment=ft.CrossAxisAlignment.END),
                lbl_pdfs,
                ft.Row([tf_client, dd_type], spacing=16),
                ft.Container(height=8),
                ft.Row([btn_start], alignment=ft.MainAxisAlignment.END),
            ],
            spacing=12,
        ),
    )

    log_card = ft.Container(
        content=ft.Column(
            [
                ft.Text("Registro", size=20, weight=ft.FontWeight.W_600, color=PALETTE["text"]),
                ft.Text("Actividad de la última ejecución.", size=13, color=PALETTE["muted"]),
                ft.Container(
                    content=log_column,
                    bgcolor=PALETTE["bg"],
                    border_radius=12,
                    padding=16,
                    border=ft.border.all(1, PALETTE["surface2"]),
                    expand=True,
                    height=220,
                ),
            ],
            spacing=8,
            expand=True,
        ),
        bgcolor=PALETTE["surface"],
        border_radius=16,
        padding=24,
        border=ft.border.all(1, PALETTE["surface2"]),
        expand=True,
    )

    body = ft.Container(
        content=ft.Column(
            [
                ft.ResponsiveRow(
                    [
                        ft.Container(credentials_card, col={"xs": 12, "md": 5}),
                        ft.Container(upload_card, col={"xs": 12, "md": 7}),
                    ],
                    spacing=16,
                    run_spacing=16,
                ),
                log_card,
            ],
            spacing=16,
            expand=True,
        ),
        padding=ft.padding.symmetric(horizontal=32, vertical=8),
        expand=True,
    )

    page.add(
        ft.Column(
            [header, body],
            expand=True,
            spacing=0,
        )
    )
    refresh_pdf_count()


def run_app() -> None:
    ft.app(target=main)


if __name__ == "__main__":
    run_app()
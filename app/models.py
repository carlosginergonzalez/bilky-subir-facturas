from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class DocumentType(str, Enum):
    EMITIDA = "Factura emitida"
    RECIBIDA = "Factura recibida"
    OTROS = "Otros (nóminas, seguros, recibo autónomo...)"

    @classmethod
    def choices(cls) -> list[str]:
        return [m.value for m in cls]


@dataclass
class UploadJob:
    folder: Path
    client_search: str
    document_type: DocumentType
    bilky_user: str
    bilky_password: str
    show_browser: bool


@dataclass
class UploadResult:
    ok: bool
    message: str
    files_count: int = 0
    screenshot: Path | None = None
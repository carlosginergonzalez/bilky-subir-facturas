# CHANGELOG

Historial de cambios del proyecto **BILKY - SUBIR FACTURAS**.

Formato: más reciente primero.

---

## 2026-11-23 — Icono, EXE y GitHub Releases

- Icono de aplicación (`assets/icon.ico`, `assets/icon.png`).
- Empaquetado Windows: `scripts/build_release.ps1` → `dist/BilkySubirFacturas.exe` + ZIP con Chromium.
- Repositorio público GitHub y **Releases** descargables (sustituye `run.bat` para compañeros).
- Credenciales retiradas del repositorio; solo configuración local en cada PC.

## 2026-11-23 — Aplicación de escritorio (Windows)

- Añadida app **Bilky · Subir facturas**: Python 3 + **Flet** (interfaz moderna) + **Playwright** (automatización).
- Flujo automatizado: login → Gestión contable → búsqueda de cliente → Subir facturas → tipo de documento → asignación de PDF (sin diálogo de Windows) → confirmación.
- Credenciales y preferencias en `%LOCALAPPDATA%\BilkySubirFacturas\`.
- Arranque para compañeros: `run.bat`; documentación en `README.md`.
- **No requiere Node.js** en PATH; solo Python la primera vez (o `.exe` empaquetado).

## 2026-11-23 — Prueba de subida, Carlos Giner

- Carpeta: `...\GINER CONSULTORES\CONTABILIDAD\RECIBIDAS\2026\4t`.
- Cliente en Bilky: **CARLOS ALBERTO GINER GONZALEZ** (buscar `GINER GONZALEZ`; `CARLOS GINER` no coincide).
- Tres PDF como **Factura recibida**, trimestre 4-2026: `A0018.pdf`, `A0023.pdf`, `factura-FRMC20260000960.pdf`.
- Resultado: **3 archivos actualizados de 3**.
- En Documentos quedó el aviso **EXISTEN FACTURAS DUPLICADAS DE SUBCATEGORIA**.

## 2026-11-23 — Creación del proyecto

- Creada la carpeta del proyecto en `C:\CURSOR\BILKY - SUBIR FACTURAS`.
- Añadido `AGENTS.md` con el contexto operativo: acceso a https://asesoriacolon.bilky.es/, flujo Portal asesor → Documentación → Gestión contable → cliente → Subir facturas, y tipo de documento por defecto **Factura recibida**.
- Documentadas las tres opciones futuras de tipo de documento (emitida / recibida / otros) para cuando exista el programa de automatización.
- Documentado el paso de **+ agregar archivo**, selección de todos los PDF de la carpeta indicada, espera a que termine la subida y confirmación con **Subir facturas**.
- Añadida la regla de actualizar este CHANGELOG de forma periódica.
- Añadida la regla de autogenerar / mantener `CURRENT_STATE.md` si el CHANGELOG crece demasiado, conservando solo lo vivo y descartando lo ya finalizado.

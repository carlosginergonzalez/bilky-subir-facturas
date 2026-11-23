# CURRENT_STATE

Estado vivo del proyecto **BILKY - SUBIR FACTURAS**. Solo lo que está en vigor ahora. El historial cerrado está en `CHANGELOG.md`.

Última actualización: 2026-11-23

## En vigor

- Destino: https://asesoriacolon.bilky.es/
- Credenciales Bilky: las introduce cada usuario en la app (no van en el repo)
- Tipo de documento por defecto en la app: **Factura recibida** (selector con emitida / otros)
- **App Windows**: carpeta `app/`, arranque `run.bat` o `python -m app.main` (ver `README.md`)
- Automatización: Playwright asigna los PDF al `<input type="file">` (no usa el diálogo del escritorio)
- Búsqueda de cliente: texto libre en Gestión contable (ej. `GINER GONZALEZ`)
- Si no hay coincidencia clara de cliente: la app aborta y guarda captura en `%LOCALAPPDATA%\BilkySubirFacturas\screenshots\`

## Abierto / siguiente paso

- Validar en un PC de compañero: doble clic en `run.bat`, subida de prueba con navegador visible.
- Opcional: empaquetar `.exe` con PyInstaller y repartir sin instalar Python.
- Revisar aviso Bilky **EXISTEN FACTURAS DUPLICADAS DE SUBCATEGORIA** (caso Carlos Giner, 2026-11-23).
- Node.js **no es necesario** salvo que se decida migrar a Electron más adelante.

## Descartado de este fichero

Nada aún (proyecto recién creado).

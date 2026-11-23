# BILKY - SUBIR FACTURAS

Proyecto de automatización para subir facturas de clientes a Bilky.

Ruta local: `C:\CURSOR\BILKY - SUBIR FACTURAS`

## Tarea principal

Subir las facturas de nuestros clientes (normalmente en una carpeta local indicada al inicio) a:

https://asesoriacolon.bilky.es/

## Acceso (credenciales)

- Usuario y contraseña de Bilky del **portal asesoría** (NIF + contraseña del gestor).
- Cada compañero las introduce en la **aplicación de escritorio**; se guardan solo en su PC (`%LOCALAPPDATA%\BilkySubirFacturas\`).

**No incluir contraseñas en el repositorio, issues, capturas ni el CHANGELOG.**

## Flujo de trabajo en Bilky (manual o automatizado)

1. Abrir https://asesoriacolon.bilky.es/ e iniciar sesión.
2. Entrar en **Portal asesor**.
3. En el submenú **Documentación**, abrir **Gestión contable**.
4. En la lista de clientes, localizar el nombre que coincida con la **carpeta de documentación** del cliente.
5. Pulsar **Acceder**.
6. Pulsar **Subir facturas**.
7. Elegir el tipo de documento (ver siguiente apartado).
8. En la ventana siguiente, pulsar **+ agregar archivo**.
9. En el desplegable / selector de archivos, elegir **todos los PDF** de la carpeta indicada al inicio.
10. Esperar a que la web complete la subida de todos los ficheros (dar tiempo; no continuar si aún están cargando).
11. Pulsar **Subir facturas** para confirmar. Con esto termina el lote.

## Tipo de documento

Hay tres opciones:

- **Factura emitida**
- **Factura recibida**
- **Otros (nóminas, seguros, recibo autónomo...)**

Cuando exista un programa de automatización, el usuario podrá elegir una de las tres opciones en cada ejecución.

**De momento, todas las subidas se hacen como Factura recibida.**

## Correspondencia carpeta ↔ cliente

El nombre de la carpeta local del cliente debe coincidir (o ser claramente identificable) con el nombre del cliente en la lista de Gestión contable. Si no hay coincidencia clara, no subir y dejar constancia en el CHANGELOG / CURRENT_STATE.

## Documentación viva del proyecto

- **CHANGELOG.md**: historial de cambios. Actualizarlo de forma **periódica** en cada sesión de trabajo relevante (al terminar un lote de subidas, un cambio de proceso, un error recurrente o una decisión).
- **CURRENT_STATE.md**: estado vivo. Si CHANGELOG.md crece demasiado (por ejemplo más de ~200 líneas o varias versiones antiguas que ya no aportan operación diaria), **autogenerar o actualizar CURRENT_STATE.md** con:
  - lo último que está en vigor (flujo, credenciales vigentes, convenciones, bloqueos abiertos, siguiente paso);
  - y **descartar de CURRENT_STATE** lo ya finalizado (eso permanece solo en el CHANGELOG).

El agente debe:

1. Añadir entradas al CHANGELOG cuando haya trabajo real.
2. Revisar el tamaño/utilidad del CHANGELOG al inicio o al cierre de sesión.
3. Mantener CURRENT_STATE.md alineado con la realidad actual y recortado de tareas cerradas.

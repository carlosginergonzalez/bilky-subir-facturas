@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Creando entorno virtual...
  py -m venv .venv
  call .venv\Scripts\pip install -r requirements.txt
  call .venv\Scripts\playwright install chromium
)
call .venv\Scripts\python run_app.py
pause
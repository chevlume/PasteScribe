@echo off
cd /d "%~dp0"
python -m pip install --quiet -r requirements.txt
if errorlevel 1 (
  echo No se pudieron instalar las dependencias. Comprueba que Python esta instalado y en el PATH.
  pause
  exit /b 1
)
python pastescribe.py

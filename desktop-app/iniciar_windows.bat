@echo off
rem Installs the dependencies and opens PasteScribe without leaving a console window open.
rem Instala las dependencias y abre PasteScribe sin dejar la ventana de comandos abierta.
cd /d "%~dp0"
python -m pip install --quiet -r requirements.txt
if errorlevel 1 (
  echo Could not install the dependencies. Check that Python is installed and in the PATH.
  echo No se pudieron instalar las dependencias. Comprueba que Python esta instalado y en el PATH.
  pause
  exit /b 1
)
rem pythonw runs the app without a console window
start "" pythonw pastescribe.py

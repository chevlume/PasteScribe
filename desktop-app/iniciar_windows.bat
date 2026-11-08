@echo off
rem Installs what PasteScribe needs and opens it without leaving a console window open.
rem Instala lo necesario y abre PasteScribe sin dejar la ventana de comandos abierta.
cd /d "%~dp0"

rem 1) Is Python installed? / Python esta instalado?
python -c "import sys" >nul 2>nul
if errorlevel 1 goto nopython

rem 2) Does that Python include tkinter (the window)? / Incluye tkinter (la ventana)?
python -c "import tkinter" >nul 2>nul
if errorlevel 1 goto notk

rem 3) Dependencies / Dependencias
python -m pip install --quiet -r requirements.txt
if errorlevel 1 (
  echo Could not install the dependencies. Check your internet connection and try again.
  echo No se pudieron instalar las dependencias. Comprueba tu conexion a internet e intentalo de nuevo.
  pause
  exit /b 1
)

rem pythonw runs the app without a console window / pythonw abre la app sin consola
start "" pythonw pastescribe.py
exit /b 0

:nopython
echo Python was not found on this PC.
echo.
echo Easiest option: download PasteScribe.exe from
echo   https://github.com/chevlume/PasteScribe/releases
echo It needs no Python and no installation.
echo.
echo Or install Python 3.9 or newer from https://www.python.org/downloads/
echo and tick "Add python.exe to PATH" during setup. Then run this file again.
echo.
echo ------------------------------------------------------------
echo No se encontro Python en este PC.
echo.
echo Opcion mas facil: descarga PasteScribe.exe desde
echo   https://github.com/chevlume/PasteScribe/releases
echo No necesita Python ni instalacion.
echo.
echo O instala Python 3.9 o superior desde https://www.python.org/downloads/
echo y marca "Add python.exe to PATH" durante la instalacion. Despues vuelve a ejecutar este archivo.
pause
exit /b 1

:notk
echo Your Python does not include tkinter, which PasteScribe needs for its window.
echo Reinstall Python from https://www.python.org/downloads/ keeping "tcl/tk and IDLE" ticked,
echo or download PasteScribe.exe from https://github.com/chevlume/PasteScribe/releases
echo ------------------------------------------------------------
echo Tu Python no incluye tkinter, que PasteScribe necesita para su ventana.
echo Reinstala Python desde https://www.python.org/downloads/ dejando marcada la opcion "tcl/tk and IDLE",
echo o descarga PasteScribe.exe desde https://github.com/chevlume/PasteScribe/releases
pause
exit /b 1

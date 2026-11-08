@echo off
rem Builds dist\PasteScribe.exe: a single file that opens WITHOUT a console window.
rem Requires Python 3.9+ (with tkinter) installed on this Windows PC.
setlocal
cd /d "%~dp0"

echo [1/3] Installing dependencies...
python -m pip install --quiet -r requirements.txt pyinstaller
if errorlevel 1 goto fail

echo [2/3] Building PasteScribe.exe ...
python -m PyInstaller --noconfirm --clean --onefile --windowed --name PasteScribe --icon pastescribe.ico ^
  --hidden-import pynput.keyboard._win32 --hidden-import pynput.mouse._win32 ^
  --hidden-import pynput._util.win32 --hidden-import pynput._util.win32_vks ^
  pastescribe.py
if errorlevel 1 goto fail

echo [3/3] Checking the build...
start /wait "" "dist\PasteScribe.exe" --selftest
if errorlevel 1 (
  echo The self-test failed. Details: %USERPROFILE%\.pastescribe.log
  goto fail
)

echo.
echo Done: %cd%\dist\PasteScribe.exe
echo You can copy that single file to your desktop.
pause
exit /b 0

:fail
echo.
echo The build failed.
pause
exit /b 1

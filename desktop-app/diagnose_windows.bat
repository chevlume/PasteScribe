@echo off
rem Checks PasteScribe on this PC and shows the results. Double-click it.
rem Comprueba PasteScribe en este PC y muestra los resultados. Doble clic.
setlocal
cd /d "%~dp0"
echo ===== PasteScribe diagnostics =====
echo.
echo [1/4] Python:
python --version
if errorlevel 1 (
  echo Python was not found. Install Python 3.9+ and tick "Add python.exe to PATH".
  goto end
)
echo.
echo [2/4] Installing dependencies...
python -m pip install --quiet -r requirements.txt
if errorlevel 1 ( echo FAILED installing dependencies. & goto end )
echo OK
echo.
echo [3/4] Unit tests:
python -m unittest discover -s tests
if errorlevel 1 ( echo TESTS FAILED. ) else ( echo TESTS OK )
echo.
echo [4/4] Self-test (window + keyboard control):
python pastescribe.py --selftest
if exist "dist\PasteScribe.exe" (
  echo.
  echo Self-test of dist\PasteScribe.exe:
  start /wait "" "dist\PasteScribe.exe" --selftest
  if errorlevel 1 ( echo PasteScribe.exe SELF-TEST FAILED ) else ( echo PasteScribe.exe SELF-TEST OK )
)
if exist "%USERPROFILE%\.pastescribe.log" (
  echo.
  echo Error log ^(%USERPROFILE%\.pastescribe.log^):
  type "%USERPROFILE%\.pastescribe.log"
)
:end
echo.
echo ===== Copy everything above and send it to me if something failed =====
pause

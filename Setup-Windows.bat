@echo off
setlocal
cd /d "%~dp0"
if errorlevel 1 goto folder_error
echo MotionSketch - Windows setup
echo Keep this window open. Installation requires an internet connection.
echo.

if exist ".venv\Scripts\python.exe" goto validate_python
py -3.11 -c "import struct; assert struct.calcsize('P') == 8" >nul 2>&1
if not errorlevel 1 goto create_311
py -3.12 -c "import struct; assert struct.calcsize('P') == 8" >nul 2>&1
if not errorlevel 1 goto create_312
echo Python 3.11 or 3.12, 64-bit, was not found by the Python launcher.
echo Install one of these versions with the Python launcher enabled.
echo Then double-click this file again. See WINDOWS-START-HERE.txt.
goto failed

:create_311
py -3.11 -m venv .venv
if errorlevel 1 goto failed
goto validate_python

:create_312
py -3.12 -m venv .venv
if errorlevel 1 goto failed

:validate_python
".venv\Scripts\python.exe" -c "import sys, struct; assert sys.version_info[:2] in ((3,11),(3,12)) and struct.calcsize('P') == 8, 'Use 64-bit Python 3.11 or 3.12'"
if errorlevel 1 goto incompatible_env
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
if exist "models\pose_landmarker_lite.task" goto ready
".venv\Scripts\python.exe" -m motionsketch.cli download-model
if errorlevel 1 goto model_failed

:ready
echo.
echo Setup finished. Double-click Start-Windows.bat to open MotionSketch.
pause
exit /b 0

:model_failed
echo.
echo Packages are installed, but the pose model could not be downloaded.
echo You can launch the app and try the synthetic demo.
echo Retry this setup file or use the app's Download human pose model button.
goto failed

:incompatible_env
echo.
echo The existing .venv uses an incompatible Python version.
echo Rename the .venv folder to .venv-old, then run setup again.
goto failed

:folder_error
echo Cannot open the project folder. Extract the ZIP to a local writable folder first.

:failed
echo.
echo Setup did not finish. Copy the error above if you need help.
pause
exit /b 1

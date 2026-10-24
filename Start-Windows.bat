@echo off
setlocal
cd /d "%~dp0"
if errorlevel 1 goto failed
if not exist ".venv\Scripts\python.exe" goto setup_required
".venv\Scripts\python.exe" -c "import streamlit" >nul 2>&1
if errorlevel 1 goto setup_required
echo Starting MotionSketch. Keep this window open while using the app.
echo If your browser does not open, visit http://localhost:8501
echo To stop the app, close this window or press Ctrl+C.
".venv\Scripts\python.exe" -m streamlit run app.py --server.address=127.0.0.1 --server.port=8501 --server.headless=false --browser.gatherUsageStats=false
if errorlevel 1 goto failed
exit /b 0

:setup_required
echo Double-click Setup-Windows.bat first, then try this file again.
pause
exit /b 1

:failed
echo.
echo The app could not start. Read the error above.
echo If port 8501 is already in use, close the other MotionSketch window and retry.
pause
exit /b 1

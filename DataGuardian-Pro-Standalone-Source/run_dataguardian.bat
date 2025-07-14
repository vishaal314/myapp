@echo off
title DataGuardian Pro - Enterprise Privacy Compliance Platform
color 0A

echo.
echo ====================================================
echo       DataGuardian Pro - Windows Standalone
echo ====================================================
echo.
echo Starting DataGuardian Pro...
echo.

REM Check if running from correct directory
if not exist "app.py" (
    echo ERROR: app.py not found in current directory
    echo Please run this script from the DataGuardian Pro installation folder
    pause
    exit /b 1
)

REM Start the application
echo [INFO] Initializing DataGuardian Pro...
echo [INFO] Starting web server on http://localhost:5000
echo [INFO] Your browser will open automatically
echo.
echo ====================================================
echo   DataGuardian Pro is now running!
echo   
echo   Web Interface: http://localhost:5000
echo   
echo   Press Ctrl+C to stop the application
echo ====================================================
echo.

REM Open browser automatically after 3 seconds
timeout /t 3 /nobreak >nul
start http://localhost:5000

REM Start the Streamlit application
streamlit run app.py --server.port 5000 --server.address 0.0.0.0 --server.headless true --server.runOnSave false

echo.
echo DataGuardian Pro has stopped.
pause
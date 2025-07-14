@echo off
echo Installing DataGuardian Pro...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.11 from python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found. Installing dependencies...
pip install -r requirements.txt

echo.
echo Installation complete!
echo.
echo To run DataGuardian Pro:
echo   Double-click "run_dataguardian.bat"
echo.
echo To build standalone executable:
echo   Double-click "build_windows_package.bat"
echo.
pause

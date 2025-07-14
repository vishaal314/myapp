@echo off
echo Building DataGuardian Pro Windows Package...
echo.

REM Clean previous builds
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM Create virtual environment
python -m venv build_env
call build_env\Scripts\activate

REM Install dependencies from pyproject.toml
pip install -e .
pip install pyinstaller

REM Create executable
echo Creating executable...
pyinstaller --onefile --windowed --name "DataGuardian Pro" ^
    --icon=static/icon.ico ^
    --add-data "static;static" ^
    --add-data "templates;templates" ^
    --add-data "translations;translations" ^
    --add-data "services;services" ^
    --add-data "utils;utils" ^
    --add-data "pages;pages" ^
    --add-data "components;components" ^
    --hidden-import streamlit ^
    --hidden-import psycopg2 ^
    --hidden-import redis ^
    --hidden-import plotly ^
    --hidden-import pandas ^
    --hidden-import bcrypt ^
    --hidden-import jwt ^
    --hidden-import stripe ^
    --hidden-import anthropic ^
    --hidden-import openai ^
    app.py

REM Create distribution package
echo Creating distribution package...
mkdir "DataGuardian-Pro-Windows"
copy "dist\DataGuardian Pro.exe" "DataGuardian-Pro-Windows\"

REM Create startup script
echo @echo off > "DataGuardian-Pro-Windows\run_dataguardian.bat"
echo cd /d "%%~dp0" >> "DataGuardian-Pro-Windows\run_dataguardian.bat"
echo echo Starting DataGuardian Pro... >> "DataGuardian-Pro-Windows\run_dataguardian.bat"
echo echo Open your browser to: http://localhost:5000 >> "DataGuardian-Pro-Windows\run_dataguardian.bat"
echo start http://localhost:5000 >> "DataGuardian-Pro-Windows\run_dataguardian.bat"
echo "DataGuardian Pro.exe" >> "DataGuardian-Pro-Windows\run_dataguardian.bat"
echo pause >> "DataGuardian-Pro-Windows\run_dataguardian.bat"

REM Create configuration directory
mkdir "DataGuardian-Pro-Windows\config"
if exist ".env.example" copy ".env.example" "DataGuardian-Pro-Windows\config\"

REM Create documentation
mkdir "DataGuardian-Pro-Windows\documentation"
echo DataGuardian Pro - Windows Standalone > "DataGuardian-Pro-Windows\documentation\README.txt"
echo. >> "DataGuardian-Pro-Windows\documentation\README.txt"
echo 1. Double-click run_dataguardian.bat to start the application >> "DataGuardian-Pro-Windows\documentation\README.txt"
echo 2. Your browser will open automatically to http://localhost:5000 >> "DataGuardian-Pro-Windows\documentation\README.txt"
echo 3. Use the application for GDPR compliance scanning >> "DataGuardian-Pro-Windows\documentation\README.txt"
echo 4. Press Ctrl+C in the console window to stop the application >> "DataGuardian-Pro-Windows\documentation\README.txt"

REM Create zip package
echo Creating zip package...
powershell Compress-Archive -Path "DataGuardian-Pro-Windows" -DestinationPath "DataGuardian-Pro-Windows.zip" -Force

echo.
echo Build complete!
echo - Executable: DataGuardian-Pro-Windows\DataGuardian Pro.exe
echo - Startup Script: DataGuardian-Pro-Windows\run_dataguardian.bat
echo - Package: DataGuardian-Pro-Windows.zip
echo.
echo To distribute: Share the DataGuardian-Pro-Windows.zip file
echo To run: Extract zip and double-click run_dataguardian.bat

REM Cleanup
deactivate
rmdir /s /q "build_env"
echo.
echo Cleanup complete. Ready for distribution!
pause
@echo off
title DataGuardian Pro - Enterprise Privacy Compliance Platform
color 0A

echo.
echo ====================================================
echo       DataGuardian Pro - Source Distribution
echo ====================================================
echo.
echo This package contains the source code for DataGuardian Pro
echo.
echo To run immediately (requires Python 3.11+):
echo   1. Double-click "run_dataguardian.bat"
echo.
echo To build standalone executable:
echo   1. Double-click "build_windows_package.bat"
echo   2. Wait for build to complete
echo   3. Find executable in DataGuardian-Pro-Windows folder
echo.
echo ====================================================
echo.

echo Choose an option:
echo 1. Run DataGuardian Pro now (requires Python)
echo 2. Build standalone executable
echo 3. Exit
echo.
set /p choice=Enter your choice (1-3): 

if "%choice%"=="1" goto run_now
if "%choice%"=="2" goto build_exe
if "%choice%"=="3" goto exit

:run_now
echo Starting DataGuardian Pro...
call run_dataguardian.bat
goto end

:build_exe
echo Building standalone executable...
call build_windows_package.bat
goto end

:exit
exit

:end
pause

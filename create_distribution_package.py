#!/usr/bin/env python3
"""
Create a distribution package for DataGuardian Pro
Since PyInstaller can't run in Replit, we'll create a source distribution
that users can easily convert to executable on Windows
"""

import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

def create_distribution_package():
    """Create a distributable package"""
    
    print("Creating DataGuardian Pro Distribution Package...")
    
    # Create package directory
    package_dir = "DataGuardian-Pro-Standalone-Source"
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)
    
    # Core files to include
    core_files = [
        "app.py",
        "pyproject.toml",
        ".env.example",
        "README.md",
        "WINDOWS_DEPLOYMENT_GUIDE.md",
        "ULTRA_BUDGET_SETUP.md",
        "build_windows_package.bat",
        "run_dataguardian.bat",
        "dataguardian_installer.nsi"
    ]
    
    # Copy core files
    for file in core_files:
        if os.path.exists(file):
            shutil.copy2(file, package_dir)
            print(f"✓ Copied {file}")
    
    # Core directories to include
    core_dirs = [
        "services",
        "utils",
        "static",
        "translations",
        "pages",
        "components",
        "docs",
        "examples"
    ]
    
    # Copy directories
    for dir_name in core_dirs:
        if os.path.exists(dir_name):
            shutil.copytree(dir_name, f"{package_dir}/{dir_name}")
            print(f"✓ Copied {dir_name}/")
    
    # Create startup script for immediate use
    startup_script = """@echo off
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
"""
    
    with open(f"{package_dir}/START_HERE.bat", 'w') as f:
        f.write(startup_script)
    
    # Create comprehensive README
    readme_content = f"""DataGuardian Pro - Windows Distribution Package
================================================

This package contains the complete source code and build tools for DataGuardian Pro,
a comprehensive GDPR compliance platform for Windows.

QUICK START OPTIONS:
===================

Option 1: Run Immediately (Python Required)
-------------------------------------------
1. Ensure Python 3.11+ is installed
2. Double-click "START_HERE.bat"
3. Choose option 1 to run now

Option 2: Build Standalone Executable
-------------------------------------
1. Double-click "START_HERE.bat"
2. Choose option 2 to build executable
3. Wait 5-10 minutes for build
4. Find executable in DataGuardian-Pro-Windows folder

Option 3: Manual Installation
-----------------------------
1. Open Command Prompt
2. Navigate to this folder
3. Run: pip install -e .
4. Run: streamlit run app.py --server.port 5000

FEATURES:
=========
✅ 10 Different Scanner Types
✅ Netherlands UAVG Compliance
✅ EU AI Act 2025 Support
✅ Professional HTML/PDF Reports
✅ Role-Based Access Control
✅ Multi-Language Support (English/Dutch)
✅ SQLite Database (no PostgreSQL required)
✅ Portable USB Version Support

SCANNER TYPES:
==============
1. Code Scanner - Source code security and PII detection
2. Website Scanner - GDPR cookie and privacy compliance
3. Document Scanner - PDF, Word, and text file analysis
4. Image Scanner - OCR-based PII detection in images
5. Database Scanner - Direct database PII scanning
6. API Scanner - REST API security assessment
7. AI Model Scanner - AI/ML model privacy compliance
8. SOC2 Scanner - SOC2 compliance validation
9. DPIA Scanner - Data Protection Impact Assessment
10. Sustainability Scanner - Environmental impact analysis

SYSTEM REQUIREMENTS:
===================
- Windows 10/11 (64-bit)
- 4GB RAM minimum (8GB recommended)
- 500MB free disk space
- Python 3.11+ (if running from source)
- Modern web browser

DEPLOYMENT OPTIONS:
==================
1. Source Code - Run with Python (immediate)
2. Standalone Executable - PyInstaller build (~200MB)
3. Docker Container - Full environment
4. Portable USB - No installation required
5. Professional Installer - Enterprise deployment

SUPPORT:
========
- Documentation: See docs/ folder
- Build Issues: Check WINDOWS_DEPLOYMENT_GUIDE.md
- Budget Options: See ULTRA_BUDGET_SETUP.md
- Community: GitHub discussions

Built: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Version: 1.0.0
Platform: Windows 10/11 (64-bit)
"""
    
    with open(f"{package_dir}/README.txt", 'w') as f:
        f.write(readme_content)
    
    # Create requirements.txt from pyproject.toml
    requirements_content = """# DataGuardian Pro Dependencies
streamlit>=1.44.1
psycopg2-binary>=2.9.10
redis>=6.2.0
plotly>=6.1.2
pandas>=2.2.3
bcrypt>=4.3.0
pyjwt>=2.10.1
stripe>=12.0.0
openai>=1.75.0
anthropic>=0.53.0
reportlab>=4.4.0
beautifulsoup4>=4.8.2
requests>=2.32.3
pillow>=11.2.1
textract>=1.6.5
trafilatura>=2.0.0
# Build dependencies
pyinstaller>=6.0.0
"""
    
    with open(f"{package_dir}/requirements.txt", 'w') as f:
        f.write(requirements_content)
    
    # Create one-click installer
    installer_script = """@echo off
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
"""
    
    with open(f"{package_dir}/INSTALL.bat", 'w') as f:
        f.write(installer_script)
    
    # Create configuration directory
    config_dir = f"{package_dir}/config"
    os.makedirs(config_dir, exist_ok=True)
    
    # Copy configuration files
    if os.path.exists(".env.example"):
        shutil.copy2(".env.example", config_dir)
    
    # Create documentation directory
    docs_dir = f"{package_dir}/documentation"
    os.makedirs(docs_dir, exist_ok=True)
    
    # Copy documentation files
    doc_files = [
        "WINDOWS_DEPLOYMENT_GUIDE.md",
        "ULTRA_BUDGET_SETUP.md",
        "DOCKER_DESKTOP_SETUP_GUIDE.md",
        "DataGuardian-Pro-Standalone-README.md"
    ]
    
    for doc_file in doc_files:
        if os.path.exists(doc_file):
            shutil.copy2(doc_file, docs_dir)
    
    # Create zip package
    zip_filename = "DataGuardian-Pro-Windows-Distribution.zip"
    print(f"\nCreating {zip_filename}...")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arcname)
    
    # Get package size
    package_size = sum(os.path.getsize(os.path.join(root, file)) 
                      for root, dirs, files in os.walk(package_dir) 
                      for file in files) / (1024 * 1024)
    
    zip_size = os.path.getsize(zip_filename) / (1024 * 1024)
    
    print(f"\n✓ DISTRIBUTION PACKAGE CREATED!")
    print(f"Package size: {package_size:.1f} MB")
    print(f"ZIP size: {zip_size:.1f} MB")
    print(f"Package: {os.path.abspath(zip_filename)}")
    print(f"Folder: {os.path.abspath(package_dir)}")
    
    print(f"\nDISTRIBUTION INSTRUCTIONS:")
    print(f"1. Share {zip_filename} with users")
    print(f"2. Users extract and run START_HERE.bat")
    print(f"3. Choose option 1 to run immediately")
    print(f"4. Choose option 2 to build standalone executable")
    
    return True

if __name__ == "__main__":
    success = create_distribution_package()
    if success:
        print("\n✓ Distribution package ready!")
    else:
        print("\n✗ Package creation failed")
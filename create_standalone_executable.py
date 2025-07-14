#!/usr/bin/env python3
"""
DataGuardian Pro Standalone Executable Builder
Creates a self-contained Windows executable with no dependencies
"""

import os
import sys
import subprocess
import shutil
import zipfile
from pathlib import Path

def create_standalone_executable():
    """Create standalone executable for DataGuardian Pro"""
    
    print("=" * 60)
    print("DataGuardian Pro Standalone Executable Builder")
    print("=" * 60)
    
    # Check if PyInstaller is available
    try:
        import PyInstaller
        print(f"✓ PyInstaller found: {PyInstaller.__version__}")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed")
    
    # Clean previous builds
    print("\nCleaning previous builds...")
    for dir_name in ["build", "dist", "DataGuardian-Pro-Standalone"]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✓ Removed {dir_name}")
    
    # Create PyInstaller spec file for better control
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Add all data files and directories
added_files = [
    ('static', 'static'),
    ('templates', 'templates'),
    ('translations', 'translations'),
    ('services', 'services'),
    ('utils', 'utils'),
    ('pages', 'pages'),
    ('components', 'components'),
    ('docs', 'docs'),
    ('examples', 'examples'),
    ('.env.example', '.'),
]

# Hidden imports for all dependencies
hidden_imports = [
    'streamlit',
    'streamlit.web.cli',
    'streamlit.runtime.scriptrunner.script_runner',
    'psycopg2',
    'redis',
    'plotly',
    'pandas',
    'bcrypt',
    'jwt',
    'stripe',
    'anthropic',
    'openai',
    'PIL',
    'reportlab',
    'textract',
    'trafilatura',
    'beautifulsoup4',
    'requests',
    'aiohttp',
    'cachetools',
    'psutil',
    'memory_profiler',
    'python_whois',
    'tldextract',
    'dnspython',
    'svglib',
    'pyyaml',
    'pypdf2',
    'python_jose'
]

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DataGuardian Pro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='static/icon.ico' if os.path.exists('static/icon.ico') else None,
)
'''
    
    # Write spec file
    with open('dataguardian_standalone.spec', 'w') as f:
        f.write(spec_content)
    print("✓ Created PyInstaller spec file")
    
    # Build executable
    print("\nBuilding standalone executable...")
    print("This may take 5-10 minutes...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "dataguardian_standalone.spec"
        ], check=True, capture_output=True, text=True)
        print("✓ Executable built successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    
    # Create distribution package
    print("\nCreating distribution package...")
    
    # Create package directory
    package_dir = "DataGuardian-Pro-Standalone"
    os.makedirs(package_dir, exist_ok=True)
    
    # Copy executable
    if os.path.exists("dist/DataGuardian Pro.exe"):
        shutil.copy2("dist/DataGuardian Pro.exe", package_dir)
        print("✓ Copied executable")
    else:
        print("✗ Executable not found")
        return False
    
    # Create startup script
    startup_script = f"""@echo off
title DataGuardian Pro - Enterprise Privacy Compliance Platform
color 0A

echo.
echo ====================================================
echo       DataGuardian Pro - Standalone Version
echo ====================================================
echo.
echo Starting DataGuardian Pro...
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if executable exists
if not exist "DataGuardian Pro.exe" (
    echo ERROR: DataGuardian Pro.exe not found
    echo Please ensure you're running this script from the correct folder
    pause
    exit /b 1
)

echo [INFO] Initializing DataGuardian Pro...
echo [INFO] Starting web server on http://localhost:5000
echo [INFO] Your browser will open automatically
echo.
echo ====================================================
echo   DataGuardian Pro is now running!
echo   
echo   Web Interface: http://localhost:5000
echo   
echo   Close this window to stop the application
echo ====================================================
echo.

REM Wait 3 seconds then open browser
timeout /t 3 /nobreak >nul
start http://localhost:5000

REM Start the application
"DataGuardian Pro.exe"

echo.
echo DataGuardian Pro has stopped.
pause
"""
    
    with open(f"{package_dir}/Start DataGuardian Pro.bat", 'w') as f:
        f.write(startup_script)
    print("✓ Created startup script")
    
    # Create configuration directory
    config_dir = f"{package_dir}/config"
    os.makedirs(config_dir, exist_ok=True)
    
    # Copy example configuration
    if os.path.exists(".env.example"):
        shutil.copy2(".env.example", config_dir)
        print("✓ Copied configuration example")
    
    # Create documentation
    docs_dir = f"{package_dir}/documentation"
    os.makedirs(docs_dir, exist_ok=True)
    
    # Create README
    readme_content = """DataGuardian Pro - Standalone Windows Application
==================================================

Quick Start:
1. Double-click "Start DataGuardian Pro.bat"
2. Wait for the application to start (10-20 seconds)
3. Your browser will open automatically to http://localhost:5000
4. Login with default credentials (see User Guide)

Features:
- Complete GDPR compliance scanning
- 10 different scanner types
- Professional HTML/PDF reports
- Netherlands-specific UAVG compliance
- EU AI Act 2025 compliance
- No internet connection required for basic features

System Requirements:
- Windows 10/11 (64-bit)
- 4GB RAM minimum (8GB recommended)
- 500MB free disk space
- Modern web browser (Chrome, Edge, Firefox)

Troubleshooting:
- If port 5000 is busy, edit .env file to change port
- For antivirus warnings, add exclusion for DataGuardian Pro folder
- For performance issues, close unnecessary programs

Support:
- Documentation: See documentation folder
- Issues: GitHub repository
- Community: Discord server

Version: 1.0.0
Built: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    with open(f"{docs_dir}/README.txt", 'w') as f:
        f.write(readme_content)
    print("✓ Created README")
    
    # Copy important documentation files
    doc_files = [
        "WINDOWS_DEPLOYMENT_GUIDE.md",
        "ULTRA_BUDGET_SETUP.md",
        "CUSTOMER_PAIN_POINT_SOLUTIONS.md"
    ]
    
    for doc_file in doc_files:
        if os.path.exists(doc_file):
            shutil.copy2(doc_file, docs_dir)
            print(f"✓ Copied {doc_file}")
    
    # Create zip package
    print("\nCreating ZIP package...")
    zip_filename = "DataGuardian-Pro-Standalone-Windows.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arcname)
    
    print(f"✓ Created {zip_filename}")
    
    # Get file sizes
    exe_size = os.path.getsize(f"{package_dir}/DataGuardian Pro.exe") / (1024 * 1024)
    zip_size = os.path.getsize(zip_filename) / (1024 * 1024)
    
    print("\n" + "=" * 60)
    print("BUILD COMPLETE!")
    print("=" * 60)
    print(f"Executable size: {exe_size:.1f} MB")
    print(f"Package size: {zip_size:.1f} MB")
    print(f"Package location: {os.path.abspath(package_dir)}")
    print(f"ZIP package: {os.path.abspath(zip_filename)}")
    print("\nDistribution Instructions:")
    print("1. Share the ZIP file with users")
    print("2. Users extract and run 'Start DataGuardian Pro.bat'")
    print("3. No installation or dependencies required")
    print("4. Works on any Windows 10/11 computer")
    
    return True

if __name__ == "__main__":
    import datetime
    success = create_standalone_executable()
    if success:
        print("\n✓ Standalone executable created successfully!")
    else:
        print("\n✗ Failed to create standalone executable")
        sys.exit(1)
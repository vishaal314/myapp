#!/usr/bin/env python3
"""
Quick Standalone Executable Builder for DataGuardian Pro
"""

import os
import sys
import subprocess
import shutil
import zipfile
from datetime import datetime

def build_standalone():
    """Build standalone executable quickly"""
    
    print("Building DataGuardian Pro Standalone Executable...")
    
    # Clean previous builds
    for dir_name in ["build", "dist", "DataGuardian-Pro-Standalone"]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    # Create simple PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "DataGuardian Pro",
        "--add-data", "static:static",
        "--add-data", "templates:templates",
        "--add-data", "translations:translations",
        "--add-data", "services:services",
        "--add-data", "utils:utils",
        "--hidden-import", "streamlit",
        "--hidden-import", "psycopg2",
        "--hidden-import", "redis",
        "--hidden-import", "plotly",
        "--hidden-import", "pandas",
        "--hidden-import", "bcrypt",
        "--hidden-import", "jwt",
        "--hidden-import", "stripe",
        "--hidden-import", "openai",
        "--hidden-import", "anthropic",
        "app.py"
    ]
    
    # Add icon if available
    if os.path.exists("static/icon.ico"):
        cmd.extend(["--icon", "static/icon.ico"])
    
    print("Running PyInstaller...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ Executable built successfully")
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print("STDERR:", e.stderr)
        return False
    
    # Create distribution package
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
    startup_script = """@echo off
title DataGuardian Pro - Enterprise Privacy Compliance Platform
color 0A

echo.
echo ====================================================
echo       DataGuardian Pro - Standalone Version
echo ====================================================
echo.
echo Starting DataGuardian Pro...
echo Web server will start on http://localhost:5000
echo Your browser will open automatically
echo.
echo Close this window to stop the application
echo ====================================================
echo.

timeout /t 3 /nobreak >nul
start http://localhost:5000

"DataGuardian Pro.exe"

echo.
echo DataGuardian Pro has stopped.
pause
"""
    
    with open(f"{package_dir}/Start DataGuardian Pro.bat", 'w') as f:
        f.write(startup_script)
    
    # Create README
    readme_content = f"""DataGuardian Pro - Standalone Windows Application
==================================================

Quick Start:
1. Double-click "Start DataGuardian Pro.bat"
2. Wait for the application to start (10-20 seconds)
3. Your browser will open automatically to http://localhost:5000
4. Use the application for GDPR compliance scanning

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
- Modern web browser

Built: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Version: 1.0.0
"""
    
    with open(f"{package_dir}/README.txt", 'w') as f:
        f.write(readme_content)
    
    # Create zip package
    zip_filename = "DataGuardian-Pro-Standalone-Windows.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arcname)
    
    # Get sizes
    exe_size = os.path.getsize(f"{package_dir}/DataGuardian Pro.exe") / (1024 * 1024)
    zip_size = os.path.getsize(zip_filename) / (1024 * 1024)
    
    print(f"\n✓ BUILD COMPLETE!")
    print(f"Executable size: {exe_size:.1f} MB")
    print(f"Package size: {zip_size:.1f} MB")
    print(f"Package: {os.path.abspath(zip_filename)}")
    
    return True

if __name__ == "__main__":
    success = build_standalone()
    if success:
        print("\n✓ Standalone executable ready for distribution!")
    else:
        print("\n✗ Build failed")
        sys.exit(1)
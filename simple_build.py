#!/usr/bin/env python3
"""
Simple PyInstaller build for DataGuardian Pro
"""

import os
import sys
import subprocess
import shutil
import zipfile
from datetime import datetime

def simple_build():
    """Simple PyInstaller build"""
    
    print("Building DataGuardian Pro Standalone Executable...")
    
    # Clean previous builds
    for dir_name in ["build", "dist", "DataGuardian-Pro-Standalone"]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    # Find existing directories
    data_dirs = []
    for dir_name in ["static", "templates", "translations", "services", "utils", "pages", "components"]:
        if os.path.exists(dir_name):
            data_dirs.extend(["--add-data", f"{dir_name}:{dir_name}"])
    
    # Basic PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name", "DataGuardian-Pro",
        "--console",  # Use console mode for debugging
        "--hidden-import", "streamlit",
        "--hidden-import", "streamlit.web.cli",
        "--hidden-import", "psycopg2",
        "--hidden-import", "redis",
        "--hidden-import", "plotly",
        "--hidden-import", "pandas",
        "--hidden-import", "bcrypt",
        "--hidden-import", "jwt",
        "--hidden-import", "stripe",
        "app.py"
    ]
    
    # Add data directories
    cmd.extend(data_dirs)
    
    print("Running PyInstaller...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ Executable built successfully")
        print("STDOUT:", result.stdout[-500:])  # Last 500 chars
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print("STDERR:", e.stderr[-1000:])  # Last 1000 chars
        return False
    
    # Create distribution package
    package_dir = "DataGuardian-Pro-Standalone"
    os.makedirs(package_dir, exist_ok=True)
    
    # Copy executable
    exe_path = "dist/DataGuardian-Pro.exe"
    if os.path.exists(exe_path):
        shutil.copy2(exe_path, package_dir)
        print("✓ Copied executable")
    else:
        # Try different extensions
        exe_path = "dist/DataGuardian-Pro"
        if os.path.exists(exe_path):
            shutil.copy2(exe_path, f"{package_dir}/DataGuardian-Pro.exe")
            print("✓ Copied executable (Linux binary)")
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

DataGuardian-Pro.exe

echo.
echo DataGuardian Pro has stopped.
pause
"""
    
    with open(f"{package_dir}/Start-DataGuardian-Pro.bat", 'w') as f:
        f.write(startup_script)
    
    # Create Linux startup script
    linux_script = """#!/bin/bash
echo "Starting DataGuardian Pro..."
echo "Web server will start on http://localhost:5000"
echo "Open your browser to: http://localhost:5000"
echo
./DataGuardian-Pro.exe
"""
    
    with open(f"{package_dir}/start-dataguardian-pro.sh", 'w') as f:
        f.write(linux_script)
    
    # Make Linux script executable
    os.chmod(f"{package_dir}/start-dataguardian-pro.sh", 0o755)
    
    # Create README
    readme_content = f"""DataGuardian Pro - Standalone Application
========================================

Quick Start:
1. Windows: Double-click "Start-DataGuardian-Pro.bat"
2. Linux: Run "./start-dataguardian-pro.sh"
3. Wait for application to start (10-20 seconds)
4. Open browser to: http://localhost:5000

Features:
- Complete GDPR compliance scanning
- 10 different scanner types
- Professional HTML/PDF reports
- Netherlands-specific UAVG compliance
- EU AI Act 2025 compliance
- SQLite database (no PostgreSQL needed)

System Requirements:
- Windows 10/11 or Linux (64-bit)
- 4GB RAM minimum (8GB recommended)
- 500MB free disk space
- Modern web browser

Built: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Version: 1.0.0
"""
    
    with open(f"{package_dir}/README.txt", 'w') as f:
        f.write(readme_content)
    
    # Create zip package
    zip_filename = "DataGuardian-Pro-Standalone.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arcname)
    
    # Get sizes
    exe_files = [f for f in os.listdir(package_dir) if f.endswith('.exe')]
    if exe_files:
        exe_size = os.path.getsize(f"{package_dir}/{exe_files[0]}") / (1024 * 1024)
    else:
        exe_size = 0
    
    zip_size = os.path.getsize(zip_filename) / (1024 * 1024)
    
    print(f"\n✓ BUILD COMPLETE!")
    print(f"Executable size: {exe_size:.1f} MB")
    print(f"Package size: {zip_size:.1f} MB")
    print(f"Package: {os.path.abspath(zip_filename)}")
    print(f"Folder: {os.path.abspath(package_dir)}")
    
    return True

if __name__ == "__main__":
    success = simple_build()
    if success:
        print("\n✓ Standalone executable ready for distribution!")
    else:
        print("\n✗ Build failed")
        sys.exit(1)
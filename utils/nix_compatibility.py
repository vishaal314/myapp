"""
Nix Package Compatibility Layer
Simulates Replit's Nix package management using system package manager
"""

import subprocess
import sys
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class NixCompatibilityLayer:
    """Simulates Nix package management using apt/system packages"""
    
    def __init__(self):
        self.package_mappings = {
            # Nix package name -> apt package name
            'pkgs.tesseract': 'tesseract-ocr',
            'pkgs.poppler_utils': 'poppler-utils',
            'pkgs.imagemagick': 'imagemagick',
            'pkgs.ffmpeg': 'ffmpeg',
            'pkgs.postgresql': 'postgresql-client',
            'pkgs.redis': 'redis-tools',
            'pkgs.git': 'git',
            'pkgs.curl': 'curl',
            'pkgs.wget': 'wget',
            'pkgs.jq': 'jq',
            'pkgs.htop': 'htop',
            'pkgs.vim': 'vim',
            'pkgs.nano': 'nano',
            'pkgs.python311': 'python3.11',
            'pkgs.python311Packages.pip': 'python3-pip',
            'pkgs.nodejs': 'nodejs',
            'pkgs.npm': 'npm',
        }
    
    def install_nix_package(self, nix_package: str) -> bool:
        """Install Nix package using system package manager"""
        apt_package = self.package_mappings.get(nix_package, nix_package.replace('pkgs.', ''))
        
        try:
            logger.info(f"Installing {nix_package} -> {apt_package}")
            result = subprocess.run([
                'apt-get', 'install', '-y', apt_package
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Successfully installed {apt_package}")
                return True
            else:
                logger.error(f"Failed to install {apt_package}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error installing {nix_package}: {e}")
            return False
    
    def ensure_system_dependencies(self) -> bool:
        """Ensure all required system dependencies are installed"""
        required_packages = [
            'pkgs.tesseract',
            'pkgs.poppler_utils', 
            'pkgs.postgresql',
            'pkgs.git',
            'pkgs.curl'
        ]
        
        success = True
        for package in required_packages:
            if not self.install_nix_package(package):
                success = False
        
        return success

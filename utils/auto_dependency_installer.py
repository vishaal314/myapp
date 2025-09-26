"""
Automatic Dependency Installer - Mimics Replit's auto-install feature
Automatically detects and installs missing Python imports.
"""

import os
import ast
import subprocess
import sys
import importlib
import logging
from pathlib import Path
from typing import Set, List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoDependencyInstaller:
    """Automatically detects and installs missing Python dependencies"""
    
    def __init__(self, project_root: str = "/app"):
        self.project_root = Path(project_root)
        self.requirements_file = self.project_root / "requirements.txt"
        self.installed_packages = self._get_installed_packages()
        
        # Common import to package name mappings (like Replit knows)
        self.import_mappings = {
            'PIL': 'pillow',
            'cv2': 'opencv-python-headless',
            'sklearn': 'scikit-learn',
            'yaml': 'pyyaml',
            'magic': 'python-magic',
            'docx': 'python-docx',
            'openpyxl': 'openpyxl',
            'xlrd': 'xlrd',
            'psycopg2': 'psycopg2-binary',
            'MySQLdb': 'mysql-connector-python',
            'jose': 'python-jose',
            'jwt': 'pyjwt',
            'bcrypt': 'bcrypt',
            'cryptography': 'cryptography',
            'authlib': 'authlib',
            'stripe': 'stripe',
            'redis': 'redis',
            'streamlit': 'streamlit',
            'pandas': 'pandas',
            'numpy': 'numpy',
            'plotly': 'plotly',
            'requests': 'requests',
            'beautifulsoup4': 'beautifulsoup4',
            'bs4': 'beautifulsoup4',
            'trafilatura': 'trafilatura',
            'tldextract': 'tldextract',
            'reportlab': 'reportlab',
            'weasyprint': 'weasyprint',
            'pytesseract': 'pytesseract',
            'anthropic': 'anthropic',
            'openai': 'openai',
            'psutil': 'psutil',
        }
    
    def _get_installed_packages(self) -> Set[str]:
        """Get list of currently installed packages"""
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                                  capture_output=True, text=True)
            packages = set()
            for line in result.stdout.split('\n')[2:]:  # Skip header
                if line.strip():
                    package_name = line.split()[0].lower()
                    packages.add(package_name)
            return packages
        except Exception as e:
            logger.error(f"Error getting installed packages: {e}")
            return set()
    
    def extract_imports_from_file(self, file_path: Path) -> Set[str]:
        """Extract all imports from a Python file"""
        imports = set()
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
        except Exception as e:
            logger.warning(f"Could not parse {file_path}: {e}")
        return imports
    
    def scan_project_imports(self) -> Set[str]:
        """Scan entire project for imports"""
        all_imports = set()
        
        # Scan Python files
        for py_file in self.project_root.rglob("*.py"):
            if '.pythonlibs' not in str(py_file) and '__pycache__' not in str(py_file):
                imports = self.extract_imports_from_file(py_file)
                all_imports.update(imports)
        
        return all_imports
    
    def get_missing_packages(self) -> List[str]:
        """Get packages that are imported but not installed"""
        project_imports = self.scan_project_imports()
        missing_packages = []
        
        for import_name in project_imports:
            # Skip standard library and local imports
            if self._is_standard_library(import_name) or self._is_local_import(import_name):
                continue
                
            # Map import name to package name
            package_name = self.import_mappings.get(import_name, import_name)
            
            # Check if package is installed
            if package_name.lower() not in self.installed_packages:
                # Try the import name directly if mapping didn't work
                if import_name.lower() not in self.installed_packages:
                    missing_packages.append(package_name)
        
        return list(set(missing_packages))  # Remove duplicates
    
    def _is_standard_library(self, module_name: str) -> bool:
        """Check if module is part of Python standard library"""
        standard_libs = {
            'os', 'sys', 'json', 'datetime', 'time', 'random', 'math', 'collections',
            'itertools', 'functools', 'typing', 'pathlib', 'tempfile', 'shutil',
            'urllib', 'http', 'email', 'html', 'xml', 'csv', 'configparser',
            'logging', 'threading', 'multiprocessing', 'subprocess', 'socket',
            'ssl', 'hashlib', 're', 'uuid', 'base64', 'pickle', 'gzip',
            'zipfile', 'tarfile', 'sqlite3', 'io', 'contextlib', 'warnings',
            'traceback', 'inspect', 'ast', 'dis', 'importlib'
        }
        return module_name in standard_libs
    
    def _is_local_import(self, module_name: str) -> bool:
        """Check if import is a local project module"""
        local_modules = {'utils', 'services', 'components', 'config', 'translations'}
        return module_name in local_modules
    
    def install_missing_packages(self, packages: List[str]) -> bool:
        """Install missing packages automatically"""
        if not packages:
            logger.info("No missing packages to install")
            return True
        
        logger.info(f"Installing missing packages: {', '.join(packages)}")
        
        try:
            # Install packages
            for package in packages:
                logger.info(f"Installing {package}...")
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', package
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    logger.error(f"Failed to install {package}: {result.stderr}")
                else:
                    logger.info(f"Successfully installed {package}")
            
            # Update requirements.txt
            self._update_requirements_file(packages)
            return True
            
        except Exception as e:
            logger.error(f"Error installing packages: {e}")
            return False
    
    def _update_requirements_file(self, new_packages: List[str]):
        """Update requirements.txt with newly installed packages"""
        try:
            existing_requirements = set()
            if self.requirements_file.exists():
                with open(self.requirements_file, 'r') as f:
                    existing_requirements = {
                        line.strip().split('>=')[0].split('==')[0].split('<')[0]
                        for line in f.readlines()
                        if line.strip() and not line.strip().startswith('#')
                    }
            
            # Add new packages that aren't already in requirements
            with open(self.requirements_file, 'a') as f:
                for package in new_packages:
                    if package not in existing_requirements:
                        f.write(f"{package}\n")
                        logger.info(f"Added {package} to requirements.txt")
                        
        except Exception as e:
            logger.error(f"Error updating requirements.txt: {e}")
    
    def run_auto_install(self) -> bool:
        """Run the complete auto-install process (like Replit)"""
        logger.info("🤖 Running automatic dependency detection...")
        
        missing_packages = self.get_missing_packages()
        if missing_packages:
            logger.info(f"Found {len(missing_packages)} missing packages")
            return self.install_missing_packages(missing_packages)
        else:
            logger.info("All dependencies are satisfied!")
            return True

def main():
    """Main function to run auto dependency installation"""
    installer = AutoDependencyInstaller()
    success = installer.run_auto_install()
    if success:
        print("✅ Automatic dependency installation complete!")
    else:
        print("❌ Some dependencies could not be installed")
        sys.exit(1)

if __name__ == "__main__":
    main()

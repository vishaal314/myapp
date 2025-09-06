#!/usr/bin/env python3
"""
DataGuardian Pro - Logging Integration Script
Automated script to integrate centralized logging across all scanners
"""

import os
import re
from pathlib import Path
from typing import List, Dict

class LoggingIntegrator:
    """Integrate centralized logging into all scanner files"""
    
    def __init__(self):
        self.services_dir = Path("services")
        self.utils_dir = Path("utils")
        self.scanner_files = []
        self.backup_dir = Path("backup_before_logging")
    
    def find_scanner_files(self) -> List[Path]:
        """Find all scanner files that need logging integration"""
        scanner_patterns = [
            "*scanner*.py",
            "*scan*.py",
            "code_*.py",
            "blob_*.py",
            "image_*.py",
            "website_*.py",
            "database_*.py",
            "dpia_*.py",
            "ai_model_*.py",
            "sustainability_*.py"
        ]
        
        scanner_files = []
        for pattern in scanner_patterns:
            scanner_files.extend(self.services_dir.glob(pattern))
            scanner_files.extend(self.utils_dir.glob(pattern))
        
        # Remove duplicates and filter existing files
        unique_files = list(set(f for f in scanner_files if f.exists()))
        return unique_files
    
    def backup_files(self, files: List[Path]):
        """Create backup of files before modification"""
        self.backup_dir.mkdir(exist_ok=True)
        
        for file_path in files:
            backup_path = self.backup_dir / file_path.name
            backup_path.write_text(file_path.read_text())
            print(f"📁 Backed up: {file_path} -> {backup_path}")
    
    def update_imports(self, file_path: Path) -> bool:
        """Update file imports to include centralized logging"""
        content = file_path.read_text()
        
        # Check if already updated
        if "from utils.centralized_logger import" in content:
            return False
        
        # Find existing logging import
        import_pattern = r'import logging\n'
        import_match = re.search(import_pattern, content)
        
        if import_match:
            # Add centralized logging import after existing logging import
            new_import = """import logging

# Import centralized logging
try:
    from utils.centralized_logger import get_scanner_logger
    logger = get_scanner_logger("{}")
except ImportError:
    # Fallback to standard logging if centralized logger not available
    logger = logging.getLogger(__name__)
""".format(file_path.stem)
            
            # Replace the standard logger initialization
            logger_pattern = r'logger = logging\.getLogger\(__name__\)'
            if re.search(logger_pattern, content):
                content = re.sub(logger_pattern, '', content)
            
            content = re.sub(import_pattern, new_import, content)
            
            file_path.write_text(content)
            print(f"✅ Updated imports in: {file_path}")
            return True
        
        return False
    
    def add_scan_logging(self, file_path: Path) -> bool:
        """Add scan start/complete/failed logging"""
        content = file_path.read_text()
        modified = False
        
        # Add scan start logging to scan functions
        scan_function_patterns = [
            r'def scan_.*?\(.*?\):',
            r'def perform_.*?scan.*?\(.*?\):',
            r'def analyze_.*?\(.*?\):'
        ]
        
        for pattern in scan_function_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                # Check if scan_started is already called
                func_start = match.start()
                func_end = content.find('\n\ndef ', func_start)
                if func_end == -1:
                    func_end = len(content)
                
                func_content = content[func_start:func_end]
                if 'scan_started' not in func_content and 'logger.info' not in func_content[:200]:
                    # Add scan start logging
                    func_lines = func_content.split('\n')
                    if len(func_lines) > 2:
                        # Insert after function definition and docstring
                        insert_pos = 2
                        while insert_pos < len(func_lines) and (func_lines[insert_pos].strip().startswith('"""') or func_lines[insert_pos].strip().startswith('"""')):
                            insert_pos += 1
                        
                        log_line = "    # Log scan start\n    if hasattr(logger, 'scan_started'):\n        logger.scan_started('{}', 'scan_target')\n".format(file_path.stem)
                        func_lines.insert(insert_pos, log_line)
                        
                        new_func_content = '\n'.join(func_lines)
                        content = content[:func_start] + new_func_content + content[func_end:]
                        modified = True
        
        if modified:
            file_path.write_text(content)
            print(f"🔍 Added scan logging to: {file_path}")
        
        return modified
    
    def run_integration(self):
        """Run complete logging integration"""
        print("🚀 Starting DataGuardian Pro Logging Integration...")
        
        # Find scanner files
        scanner_files = self.find_scanner_files()
        print(f"📝 Found {len(scanner_files)} scanner files to update:")
        for f in scanner_files:
            print(f"   - {f}")
        
        if not scanner_files:
            print("⚠️  No scanner files found to update")
            return
        
        # Create backups
        print("\n📁 Creating backups...")
        self.backup_files(scanner_files)
        
        # Update each file
        print("\n🔧 Updating scanner files...")
        updated_count = 0
        
        for file_path in scanner_files:
            try:
                import_updated = self.update_imports(file_path)
                scan_updated = self.add_scan_logging(file_path)
                
                if import_updated or scan_updated:
                    updated_count += 1
                    
            except Exception as e:
                print(f"❌ Error updating {file_path}: {e}")
        
        print(f"\n✅ Logging integration completed!")
        print(f"📊 Updated {updated_count}/{len(scanner_files)} files")
        print(f"💾 Backups saved in: {self.backup_dir}")
        print(f"📋 Next steps:")
        print(f"   1. Test scanners to ensure they work correctly")
        print(f"   2. Check logs/ directory for structured log files")
        print(f"   3. Use the log dashboard for monitoring")

def main():
    """Main integration function"""
    integrator = LoggingIntegrator()
    integrator.run_integration()

if __name__ == "__main__":
    main()
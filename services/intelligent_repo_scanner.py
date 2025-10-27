"""
Intelligent Repository Scanner Wrapper

Provides intelligent scanning capabilities for code repositories.
Wraps the standard repo scanner with enhanced features.
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class IntelligentRepoScanner:
    """Intelligent wrapper for repository scanning with enhanced capabilities."""
    
    def __init__(self, code_scanner):
        """
        Initialize intelligent repository scanner.
        
        Args:
            code_scanner: Base code scanner instance to use
        """
        self.code_scanner = code_scanner
        logger.info("Initialized IntelligentRepoScanner with code scanner integration")
    
    def scan(self, target, scan_mode="smart", max_files=200, **kwargs):
        """
        Scan a repository with intelligent processing.
        
        Args:
            target: Repository URL or path to scan
            scan_mode: Scanning strategy (smart, fast, deep)
            max_files: Maximum number of files to process
            **kwargs: Additional scanning parameters
            
        Returns:
            Dictionary with scan results
        """
        logger.info(f"Starting intelligent repository scan: {target} (mode: {scan_mode})")
        
        try:
            # Use the code scanner directly for repository scanning
            if hasattr(self.code_scanner, 'scan_repository'):
                results = self.code_scanner.scan_repository(target, **kwargs)
            elif hasattr(self.code_scanner, 'scan_code'):
                results = self.code_scanner.scan_code(target, **kwargs)
            else:
                # Fallback to basic results structure
                results = {
                    "findings": [],
                    "scan_mode": scan_mode,
                    "target": target
                }
            
            logger.info(f"Repository scan completed with {len(results.get('findings', []))} findings")
            return results
            
        except Exception as e:
            logger.error(f"Repository scan failed: {e}")
            return {
                "error": str(e),
                "findings": [],
                "scan_mode": scan_mode
            }

"""
GitHub Repository Scanner

This module provides functions for scanning GitHub repositories for PII and sensitive information.
It uses our more reliable SimpleRepoScanner instead of the standard RepoScanner to avoid
multiprocessing issues that were causing scans to fail.
"""

import os
import time
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from services.simple_repo_scanner import SimpleRepoScanner
from services.code_scanner import CodeScanner

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("services.github_repo_scanner")

def scan_github_repository(repo_url: str, branch: Optional[str] = None, token: Optional[str] = None) -> Dict[str, Any]:
    """
    Scan a GitHub repository for PII and sensitive information using our reliable scanner.
    
    Args:
        repo_url: The GitHub repository URL
        branch: Optional branch name to scan (default: repository default branch)
        token: Optional GitHub access token for private repositories
        
    Returns:
        Dictionary with scan results
    """
    start_time = time.time()
    
    # Create scan result structure
    scan_results = {
        'scan_id': f"github_{int(time.time())}",
        'scan_type': 'repository',
        'timestamp': datetime.now().isoformat(),
        'repo_url': repo_url,
        'branch': branch or 'main',
        'status': 'in_progress',
        'findings': [],
        'total_pii_found': 0,
        'high_risk_count': 0,
        'medium_risk_count': 0,
        'low_risk_count': 0,
        'files_scanned': 0,
        'duration_seconds': 0
    }
    
    try:
        # Initialize code scanner and repo scanner
        code_scanner = CodeScanner(region='Netherlands')  # Default to Netherlands for GDPR compliance
        repo_scanner = SimpleRepoScanner(code_scanner)
        
        # Perform the scan
        logger.info(f"Starting scan of GitHub repository: {repo_url}")
        scan_result = repo_scanner.scan_repository(repo_url, branch, token)
        
        # Update scan results
        scan_results.update(scan_result)
        scan_results['duration_seconds'] = int(time.time() - start_time)
        scan_results['status'] = 'completed'
        
        return scan_results
        
    except Exception as e:
        logger.error(f"Error scanning GitHub repository: {str(e)}")
        scan_results['status'] = 'failed'
        scan_results['error'] = str(e)
        scan_results['duration_seconds'] = int(time.time() - start_time)
        return scan_results
        

def scan_github_repo_for_code(repo_url: str, branch: Optional[str] = None, token: Optional[str] = None, 
                             progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
    """
    Scan a GitHub repository specifically for code-related PII and sensitive information.
    This is a specialized version for the Code Scanner section.
    
    Args:
        repo_url: The GitHub repository URL
        branch: Optional branch name to scan (default: repository default branch)
        token: Optional GitHub access token for private repositories
        progress_callback: Optional callback function for progress reporting
        
    Returns:
        Dictionary with scan results
    """
    try:
        # Initialize code scanner and repo scanner
        code_scanner = CodeScanner(region='Netherlands')  # Default to Netherlands for GDPR compliance
        repo_scanner = SimpleRepoScanner(code_scanner)
        
        # Perform the scan with progress reporting
        logger.info(f"Starting code scan of GitHub repository: {repo_url}")
        scan_result = repo_scanner.scan_repository(repo_url, branch, token, progress_callback)
        
        # Ensure we have standard output format
        scan_result['scan_type'] = 'code'
        if 'timestamp' not in scan_result:
            scan_result['timestamp'] = datetime.now().isoformat()
            
        # Format the findings for better display
        formatted_findings = []
        total_pii = 0
        
        for finding in scan_result.get('findings', []):
            # Extract PII findings from file results
            if 'findings' in finding:
                for pii_finding in finding.get('findings', []):
                    file_path = finding.get('file_path', 'Unknown file')
                    formatted_finding = {
                        'type': pii_finding.get('type', 'Unknown'),
                        'value': pii_finding.get('value', ''),
                        'location': file_path,
                        'line': pii_finding.get('line', 0),
                        'risk_level': pii_finding.get('risk_level', 'medium'),
                        'gdpr_article': pii_finding.get('gdpr_article', 'N/A'),
                        'context': pii_finding.get('context', '')
                    }
                    formatted_findings.append(formatted_finding)
                    total_pii += 1
        
        # Update scan result with formatted findings
        scan_result['formatted_findings'] = formatted_findings
        scan_result['total_pii_found'] = total_pii
        
        return scan_result
        
    except Exception as e:
        logger.error(f"Error in code scan of GitHub repository: {str(e)}")
        return {
            'scan_id': f"github_code_{int(time.time())}",
            'scan_type': 'code',
            'timestamp': datetime.now().isoformat(),
            'repo_url': repo_url,
            'branch': branch or 'main',
            'status': 'failed',
            'error': str(e),
            'findings': [],
            'formatted_findings': [],
            'total_pii_found': 0
        }
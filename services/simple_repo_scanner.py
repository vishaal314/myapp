"""
Simple Repository Scanner

This module provides a simplified repository scanning implementation that avoids multiprocessing
to ensure reliable operation without pickling errors. It's designed to be more robust
for scanning GitHub repositories.
"""

import os
import re
import git
import uuid
import time
import shutil
import fnmatch
import logging
import tempfile
import traceback
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Set, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("services.simple_repo_scanner")

class SimpleRepoScanner:
    """
    A simplified repository scanner that avoids multiprocessing for better reliability.
    This scanner is designed to be used as a fallback when the main scanner encounters issues.
    """
    
    def __init__(self, code_scanner):
        """
        Initialize the simple repository scanner.
        
        Args:
            code_scanner: The code scanner to use for scanning files
        """
        self.code_scanner = code_scanner
        self.temp_dirs = []
        
        # List of supported Git platforms
        self.supported_platforms = [
            'github.com',
            'gitlab.com', 
            'bitbucket.org',
            'dev.azure.com'
        ]
        
    def is_valid_repo_url(self, repo_url: str) -> bool:
        """
        Check if a URL is a valid Git repository URL.
        
        Args:
            repo_url: URL to check
            
        Returns:
            True if valid, False otherwise
        """
        if not repo_url:
            return False
            
        # Basic pattern matching for Git repository URLs
        pattern = r'https?://([^/]+)/([^/]+)/([^/]+)'
        match = re.match(pattern, repo_url)
        
        if not match:
            return False
        
        # Check if the domain is a supported Git platform
        domain = match.group(1)
        valid_domain = any(platform in domain for platform in self.supported_platforms)
        
        if not valid_domain:
            logger.warning(f"Domain validation failed for: {domain} in URL: {repo_url}")
            
        return valid_domain
    
    def _prepare_auth_for_clone(self, repo_url: str, auth_token: Optional[str] = None) -> str:
        """
        Prepare repository URL with authentication if needed.
        
        Args:
            repo_url: Original repository URL
            auth_token: Authentication token for private repositories
            
        Returns:
            Repository URL with authentication included if needed
        """
        if not auth_token:
            return repo_url
            
        # Add auth token to URL based on platform
        if 'github.com' in repo_url:
            # For GitHub
            parts = repo_url.split('https://')
            return f'https://{auth_token}:x-oauth-basic@{parts[1]}'
        elif 'gitlab.com' in repo_url:
            # For GitLab
            parts = repo_url.split('https://')
            return f'https://oauth2:{auth_token}@{parts[1]}'
        elif 'bitbucket.org' in repo_url:
            # For Bitbucket
            parts = repo_url.split('https://')
            return f'https://x-token-auth:{auth_token}@{parts[1]}'
        elif 'dev.azure.com' in repo_url:
            # For Azure DevOps
            parts = repo_url.split('https://')
            return f'https://{auth_token}@{parts[1]}'
        
        return repo_url
    
    def clone_repository(self, repo_url: str, branch: Optional[str] = None, 
                        auth_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Clone a Git repository to a temporary directory.
        
        Args:
            repo_url: URL of the Git repository
            branch: Branch to clone (default: repository default branch)
            auth_token: Authentication token for private repositories
            
        Returns:
            Dictionary with cloning results
        """
        start_time = time.time()
        
        if not self.is_valid_repo_url(repo_url):
            return {
                'status': 'error',
                'message': f'Invalid repository URL: {repo_url}'
            }
        
        # Create a temporary directory for the repository
        temp_dir = tempfile.mkdtemp(prefix="repo_scan_")
        self.temp_dirs.append(temp_dir)
        
        # Prepare auth URL if token is provided
        clone_url = self._prepare_auth_for_clone(repo_url, auth_token)
        
        # Try to clone the repository with the specified branch first
        logger.info(f"Fast cloning repository from {repo_url}" + 
                   (f" (branch: {branch})" if branch else " (default branch)"))
        
        is_large_repo = False
        repo_size_mb = 0
        
        try:
            clone_args = ['git', 'clone', '--depth', '1']
            
            # Add branch if specified
            if branch:
                clone_args.extend(['--branch', branch])
                
            # Add clone arguments for faster, smaller clones
            clone_args.extend(['--single-branch', '--filter=blob:none', clone_url, temp_dir])
            
            result = subprocess.run(clone_args, 
                                   capture_output=True, 
                                   text=True,
                                   timeout=300)  # 5-minute timeout
            
            if result.returncode != 0:
                error_message = result.stderr.strip()
                
                if branch and "Remote branch not found" in error_message:
                    # Branch not found, try cloning without specifying branch
                    logger.warning(f"Failed to clone branch '{branch}', will try default branch instead.")
                    
                    # Clean up and try again with default branch
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    temp_dir = tempfile.mkdtemp(prefix="repo_scan_")
                    self.temp_dirs.append(temp_dir)
                    
                    # Clone with default branch
                    clone_args = ['git', 'clone', '--depth', '1', '--single-branch', 
                                 '--filter=blob:none', clone_url, temp_dir]
                    
                    result = subprocess.run(clone_args, 
                                           capture_output=True, 
                                           text=True,
                                           timeout=300)
                    
                    if result.returncode != 0:
                        return {
                            'status': 'error',
                            'message': f"Failed to clone repository: {result.stderr.strip()}"
                        }
                else:
                    return {
                        'status': 'error',
                        'message': f"Failed to clone repository: {error_message}"
                    }
            
            # Get repository size
            repo_size = 0
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    try:
                        repo_size += os.path.getsize(os.path.join(root, file))
                    except:
                        pass
            
            repo_size_mb = repo_size / (1024 * 1024)
            is_large_repo = repo_size_mb > 500  # Consider repositories over 500MB as large
            
            if is_large_repo:
                logger.warning(f"Large repository detected: {repo_size_mb:.1f} MB")
                
            # Create a .scanignore file for directories that should be excluded
            try:
                with open(os.path.join(temp_dir, '.scanignore'), 'w') as f:
                    f.write('\n'.join([
                        ".git/",
                        "node_modules/",
                        "venv/",
                        "__pycache__/",
                        "*.min.js",
                        "*.min.css",
                        "dist/",
                        "build/",
                        "vendor/",
                        "*.jpg",
                        "*.jpeg",
                        "*.png",
                        "*.gif",
                        "*.ico",
                        "*.svg",
                        "*.woff",
                        "*.woff2",
                        "*.ttf",
                        "*.eot",
                        "*.mp4",
                        "*.zip",
                        "*.tar.gz",
                        "*.tgz"
                    ]))
            except Exception as e:
                logger.warning(f"Failed to create .scanignore file: {str(e)}")
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Error cloning repository: {str(e)}"
            }
                
        return {
            'status': 'success',
            'message': 'Repository cloned successfully',
            'repo_path': temp_dir,
            'time_ms': int((time.time() - start_time) * 1000),
            'is_large_repo': is_large_repo,
            'repo_size_mb': repo_size_mb
        }
    
    def get_repo_metadata(self, repo_path: str) -> Dict[str, Any]:
        """
        Get metadata about a Git repository.
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            Dictionary with repository metadata
        """
        metadata = {
            'branch': 'unknown',
            'last_commit_date': None,
            'commit_count': 0,
            'contributors': []
        }
        
        try:
            # Get the current branch
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                metadata['branch'] = result.stdout.strip()
                
            # Get last commit date
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%cd', '--date=iso'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                metadata['last_commit_date'] = result.stdout.strip()
                
            # Get commit count
            result = subprocess.run(
                ['git', 'rev-list', '--count', 'HEAD'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                metadata['commit_count'] = int(result.stdout.strip())
                
            # Get contributors (limited to top 10)
            result = subprocess.run(
                ['git', 'shortlog', '-sn', '--no-merges', 'HEAD', '--max-count=10'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                contributors = []
                for line in result.stdout.strip().split('\n'):
                    if not line.strip():
                        continue
                    parts = line.strip().split('\t')
                    if len(parts) == 2:
                        count, name = int(parts[0].strip()), parts[1].strip()
                        contributors.append({'name': name, 'commits': count})
                
                metadata['contributors'] = contributors
                
        except Exception as e:
            logger.warning(f"Error getting repository metadata: {str(e)}")
            
        return metadata
    
    def scan_repository(self, repo_url: str, branch: Optional[str] = None, 
                      auth_token: Optional[str] = None, 
                      progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Clone and scan a Git repository using a simplified approach without multiprocessing.
        
        Args:
            repo_url: URL of the Git repository
            branch: Branch to clone (default: repository default branch)
            auth_token: Authentication token for private repositories
            progress_callback: Optional callback for reporting progress
            
        Returns:
            Dictionary with scan results
        """
        start_time = time.time()
        
        # Create a unique scan ID
        scan_id = f"repo_{uuid.uuid4().hex[:8]}"
        
        # Create scan_results structure
        scan_results = {
            'scan_id': scan_id,
            'scan_type': 'repository',
            'status': 'in_progress',
            'url': repo_url,
            'branch': branch,
            'timestamp': datetime.now().isoformat(),
            'findings': [],
            'total_pii_found': 0,
            'high_risk_count': 0,
            'medium_risk_count': 0,
            'low_risk_count': 0,
            'files_scanned': 0,
            'files_skipped': 0,
            'duration_seconds': 0
        }
        
        try:
            # Clone the repository
            logger.info(f"Cloning repository: {repo_url}")
            clone_result = self.clone_repository(repo_url, branch, auth_token)
            
            if clone_result['status'] != 'success':
                scan_results['status'] = 'failed'
                scan_results['error'] = clone_result.get('message', 'Failed to clone repository')
                return scan_results
                
            repo_path = clone_result['repo_path']
            repo_size_mb = clone_result.get('repo_size_mb', 0)
            is_large_repo = clone_result.get('is_large_repo', False)
            
            # Get repository metadata
            logger.info(f"Getting repository metadata")
            repo_info = self.get_repo_metadata(repo_path)
            actual_branch = repo_info.get('branch', branch or 'default')
            
            # Add repository metadata to results
            scan_results['repository'] = {
                'url': repo_url,
                'branch': actual_branch,
                'clone_time_ms': clone_result.get('time_ms', 0),
                'metadata': repo_info,
                'size_mb': repo_size_mb
            }
            
            # Collect files to scan
            logger.info(f"Collecting files to scan in {repo_path}")
            files_to_scan = []
            
            # Define patterns to ignore
            ignore_patterns = [
                '.git/', 'node_modules/', 'venv/', '__pycache__/', 
                'dist/', 'build/', 'vendor/', '.vscode/', '.idea/',
                '*.jpg', '*.jpeg', '*.png', '*.gif', '*.ico', '*.svg',
                '*.woff', '*.woff2', '*.ttf', '*.eot', '*.zip', '*.tar.gz',
                '*.min.js', '*.min.css', '*.map', '*.lock'
            ]
            
            # Collect files that don't match ignore patterns
            for root, dirs, files in os.walk(repo_path):
                # Remove directories to ignore from the walk
                dirs_to_remove = []
                for i, dir_name in enumerate(dirs):
                    if any(fnmatch.fnmatch(dir_name, pattern.rstrip('/')) for pattern in ignore_patterns if pattern.endswith('/')):
                        dirs_to_remove.append(i)
                
                # Remove directories from bottom to top to preserve indices
                for i in sorted(dirs_to_remove, reverse=True):
                    dirs.pop(i)
                
                # Add files that don't match ignore patterns
                for file_name in files:
                    full_path = os.path.join(root, file_name)
                    rel_path = os.path.relpath(full_path, repo_path)
                    
                    # Skip files matching ignore patterns
                    if any(fnmatch.fnmatch(file_name, pattern) for pattern in ignore_patterns if not pattern.endswith('/')):
                        scan_results['files_skipped'] += 1
                        continue
                    
                    # Skip files larger than 10MB
                    try:
                        if os.path.getsize(full_path) > 10 * 1024 * 1024:
                            scan_results['files_skipped'] += 1
                            continue
                    except:
                        scan_results['files_skipped'] += 1
                        continue
                    
                    files_to_scan.append(full_path)
            
            # Limit files for very large repositories
            max_files = 1000
            if is_large_repo and len(files_to_scan) > max_files:
                logger.warning(f"Large repository detected. Limiting scan to {max_files} files out of {len(files_to_scan)}")
                files_to_scan = files_to_scan[:max_files]
            
            # Scan files in sequence
            total_files = len(files_to_scan)
            logger.info(f"Scanning {total_files} files")
            
            # Process files one by one
            for i, file_path in enumerate(files_to_scan):
                if progress_callback:
                    rel_path = os.path.relpath(file_path, repo_path)
                    progress_callback(i + 1, total_files, rel_path)
                
                # Scan the file
                try:
                    # Use the CodeScanner's scan_file method
                    if hasattr(self.code_scanner, 'scan_file'):
                        # This is the standard method name in CodeScanner
                        file_result = self.code_scanner.scan_file(file_path)
                    else:
                        # Simple fallback implementation
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                
                            # Check for PII in the content
                            from utils.pii_detection import identify_pii_in_text
                            pii_findings = identify_pii_in_text(content, region='Netherlands')
                            
                            findings = []
                            for finding in pii_findings:
                                findings.append({
                                    'type': finding.get('pii_type', 'unknown'),
                                    'value': finding.get('value', ''),
                                    'risk_level': 'medium',  # Default risk level
                                })
                                
                            file_result = {
                                'file_path': file_path,
                                'findings': findings,
                                'pii_count': len(findings)
                            }
                        except Exception as e:
                            file_result = {
                                'file_path': file_path,
                                'error': f"Error scanning file: {str(e)}",
                                'findings': [],
                                'pii_count': 0
                            }
                    
                    # Always count files scanned even if no findings
                    scan_results['files_scanned'] += 1
                    
                    # Add file findings to results
                    rel_path = os.path.relpath(file_path, repo_path)
                    file_result['file_path'] = rel_path
                    
                    # Process findings if they exist
                    findings = file_result.get('findings', [])
                    if findings:
                        # Count risk levels
                        for finding in findings:
                            risk_level = finding.get('risk_level', 'medium').lower()
                            if risk_level == 'high':
                                scan_results['high_risk_count'] += 1
                            elif risk_level == 'medium':
                                scan_results['medium_risk_count'] += 1
                            elif risk_level == 'low':
                                scan_results['low_risk_count'] += 1
                        
                        scan_results['total_pii_found'] += len(findings)
                        scan_results['findings'].append(file_result)
                    
                except Exception as e:
                    logger.warning(f"Error scanning file {file_path}: {str(e)}")
                    scan_results['files_skipped'] += 1
            
            # Mark scan as completed
            scan_results['status'] = 'completed'
            scan_results['duration_seconds'] = int(time.time() - start_time)
            
        except Exception as e:
            logger.error(f"Error scanning repository: {str(e)}")
            logger.error(traceback.format_exc())
            scan_results['status'] = 'failed'
            scan_results['error'] = f"Error scanning repository: {str(e)}"
            
        finally:
            # Clean up temporary directories
            for temp_dir in self.temp_dirs:
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except Exception as e:
                    logger.warning(f"Error cleaning up temporary directory {temp_dir}: {str(e)}")
            
            self.temp_dirs = []
            
        return scan_results
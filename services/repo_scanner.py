"""
Repository Scanner module for cloning and scanning Git repositories.

This module provides functionality to clone Git repositories from URLs (GitHub, GitLab, Bitbucket)
and scan the codebase for PII and sensitive information using the CodeScanner.
"""

import os
import re
import shutil
import tempfile
import subprocess
import logging
import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import uuid

from services.code_scanner import CodeScanner
from services.consent_analyzer import apply_consent_analyzer, check_consent_patterns

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RepoScanner:
    """
    A scanner that clones and analyzes Git repositories for PII and sensitive information.
    """
    
    def __init__(self, code_scanner: CodeScanner):
        """
        Initialize the repository scanner.
        
        Args:
            code_scanner: An instance of CodeScanner to use for scanning files
        """
        self.code_scanner = code_scanner
        # Expanded list to include more GitHub domains and variations
        self.supported_platforms = [
            'github.com', 
            'gitlab.com', 
            'bitbucket.org', 
            'dev.azure.com',
            'github.io',
            'githubusercontent.com',
            'raw.githubusercontent.com'
        ]
        self.temp_dirs = []
        
    def __del__(self):
        """
        Cleanup temporary directories on object destruction.
        """
        self._cleanup_temp_dirs()
        
    def _cleanup_temp_dirs(self):
        """
        Clean up all temporary directories created during scanning.
        """
        for temp_dir in self.temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    logger.info(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                logger.error(f"Error cleaning up temporary directory {temp_dir}: {str(e)}")
    
    def is_valid_repo_url(self, repo_url: str) -> bool:
        """
        Check if a repository URL is valid.
        
        Args:
            repo_url: URL of the Git repository
            
        Returns:
            True if the URL seems to be a valid Git repository URL, False otherwise
        """
        # Handle empty URL
        if not repo_url or repo_url.strip() == "":
            return False
            
        # Basic URL validation - allow URLs with repository paths (like /tree/master/.github)
        # More permissive pattern - just ensure it's an http(s) URL with at least org/repo pattern
        url_pattern = r'^https?://(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/[^/]+/[^/]+'
        match = re.match(url_pattern, repo_url)
        
        if not match:
            logger.warning(f"URL pattern validation failed for: {repo_url}")
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
        Clone a Git repository to a temporary directory with optimized performance.
        
        Args:
            repo_url: URL of the Git repository
            branch: Branch to clone (default: repository default branch)
            auth_token: Authentication token for private repositories
            
        Returns:
            Dictionary with cloning results and local path
        """
        start_time = time.time()
        
        if not self.is_valid_repo_url(repo_url):
            return {
                'status': 'error',
                'message': 'Invalid repository URL format',
                'repo_path': None,
                'time_ms': int((time.time() - start_time) * 1000)
            }
        
        # Create a unique temporary directory
        temp_dir = os.path.join(tempfile.gettempdir(), f"repo_scan_{uuid.uuid4().hex}")
        self.temp_dirs.append(temp_dir)
        os.makedirs(temp_dir, exist_ok=True)
        
        # Prepare authentication if needed
        clone_url = self._prepare_auth_for_clone(repo_url, auth_token)
        
        # Try with the specified branch first
        success = False
        error_msg = ""
        
        # PERFORMANCE OPTIMIZATION 1: Reduce clone depth and use sparse checkout
        # PERFORMANCE OPTIMIZATION 2: Reduce timeout from 10 minutes to 2 minutes
        # PERFORMANCE OPTIMIZATION 3: Add --filter=blob:none to avoid retrieving large blobs
        timeout_seconds = 120  # 2 min timeout instead of 10
        
        if branch:
            # First attempt with specified branch
            # Performance-optimized clone command with sparse checkout
            cmd = [
                'git', 'clone',
                '--branch', branch,
                '--depth', '1',  # Get only most recent commit
                '--filter=blob:none',  # Don't download file contents initially
                '--no-checkout',  # Don't check out files initially (for faster clone)
                clone_url, temp_dir
            ]
            
            try:
                # Execute git clone command
                logger.info(f"Cloning repository from {repo_url} (branch: {branch})")
                
                # Use subprocess with timeout to prevent hanging
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True,
                    timeout=timeout_seconds
                )
                
                if result.returncode == 0:
                    success = True
                else:
                    # Save error message for logging later
                    error_msg = result.stderr
                    # If branch-specific clone fails, clean up for next attempt
                    shutil.rmtree(temp_dir)
                    os.makedirs(temp_dir, exist_ok=True)
                    logger.warning(f"Failed to clone branch '{branch}', will try default branch instead.")
            
            except Exception as e:
                error_msg = str(e)
                # Clean up for next attempt
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    os.makedirs(temp_dir, exist_ok=True)
        
        # If branch-specific clone failed or no branch was specified, try without branch specifier
        if not success:
            # Performance-optimized clone command with sparse checkout
            cmd = [
                'git', 'clone',
                '--depth', '1',  # Get only most recent commit
                '--filter=blob:none',  # Don't download file contents initially
                '--no-checkout',  # Don't check out files initially (for faster clone)
                clone_url, temp_dir
            ]
            
            try:
                # Execute git clone command
                logger.info(f"Cloning repository from {repo_url} (default branch)")
                
                # Use subprocess with timeout to prevent hanging
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True,
                    timeout=timeout_seconds
                )
                
                if result.returncode != 0:
                    error_msg = result.stderr
                    # Remove auth token from error message if present
                    if auth_token:
                        error_msg = error_msg.replace(auth_token, '********')
                        
                    logger.error(f"Git clone failed: {error_msg}")
                    return {
                        'status': 'error',
                        'message': f'Failed to clone repository: {error_msg}',
                        'repo_path': None,
                        'time_ms': int((time.time() - start_time) * 1000)
                    }
                else:
                    success = True
                    
            except subprocess.TimeoutExpired:
                logger.error("Git clone operation timed out")
                return {
                    'status': 'error',
                    'message': f'Git clone operation timed out after {timeout_seconds} seconds',
                    'repo_path': None,
                    'time_ms': int((time.time() - start_time) * 1000)
                }
            except Exception as e:
                logger.error(f"Error cloning repository: {str(e)}")
                return {
                    'status': 'error',
                    'message': f'Error cloning repository: {str(e)}',
                    'repo_path': None,
                    'time_ms': int((time.time() - start_time) * 1000)
                }
        
        # PERFORMANCE OPTIMIZATION 4: Use sparse checkout to only get important files
        # Now setup sparse checkout for only important file types
        try:
            # Initialize sparse checkout
            subprocess.run(
                ['git', 'sparse-checkout', 'init', '--cone'],
                cwd=temp_dir,
                capture_output=True,
                timeout=30
            )
            
            # Set sparse checkout patterns to only check out important files
            # Create patterns file for important file types to check out
            patterns = [
                '*.py', '*.js', '*.ts', '*.java', '*.cs', '*.go', '*.rs', '*.rb',
                '*.php', '*.jsx', '*.tsx', '*.yml', '*.yaml', '*.json', '*.xml',
                '*.tf', '*.tfvars', '*.html', '*.htm', '*.css', '*.sql', '*.sh',
                '*.ps1', '*.env', '*.properties', '*.conf', '*.ini'
            ]
            
            # Write patterns to file
            patterns_file = os.path.join(temp_dir, 'sparse-checkout-patterns.txt')
            with open(patterns_file, 'w') as f:
                for pattern in patterns:
                    f.write(f"{pattern}\n")
            
            # Set sparse checkout patterns
            subprocess.run(
                ['git', 'sparse-checkout', 'set', '--stdin'],
                input='\n'.join(patterns),
                text=True,
                cwd=temp_dir,
                capture_output=True,
                timeout=30
            )
            
            # Checkout the files
            subprocess.run(
                ['git', 'checkout'],
                cwd=temp_dir,
                capture_output=True,
                timeout=30
            )
            
        except Exception as e:
            logger.warning(f"Failed to set up sparse checkout: {str(e)}. Falling back to regular checkout.")
            # If sparse checkout fails, fall back to regular checkout of the HEAD commit
            try:
                subprocess.run(
                    ['git', 'checkout', 'HEAD'],
                    cwd=temp_dir,
                    capture_output=True,
                    timeout=30
                )
            except Exception as checkout_error:
                logger.error(f"Error checking out repository: {str(checkout_error)}")
                return {
                    'status': 'error',
                    'message': f'Error checking out repository: {str(checkout_error)}',
                    'repo_path': None,
                    'time_ms': int((time.time() - start_time) * 1000)
                }
        
        # Verify the clone was successful
        if not os.listdir(temp_dir) or not os.path.exists(os.path.join(temp_dir, '.git')):
            logger.error("Git clone completed but repository appears empty")
            return {
                'status': 'error',
                'message': 'Repository appears to be empty or not a Git repository',
                'repo_path': None,
                'time_ms': int((time.time() - start_time) * 1000)
            }
            
        # Get repository metadata
        repo_info = self._get_repo_metadata(temp_dir)
        
        # Get the actual branch name that was cloned
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=10  # Short timeout for this simple command
            )
            if result.returncode == 0:
                actual_branch = result.stdout.strip()
                repo_info['active_branch'] = actual_branch
        except Exception:
            # If we can't get the branch name, that's okay
            pass
            
        logger.info(f"Repository cloned successfully to {temp_dir}")
        return {
            'status': 'success',
            'message': 'Repository cloned successfully',
            'repo_path': temp_dir,
            'metadata': repo_info,
            'time_ms': int((time.time() - start_time) * 1000)
        }
    
    def _get_repo_metadata(self, repo_path: str) -> Dict[str, Any]:
        """
        Get Git repository metadata.
        
        Args:
            repo_path: Path to the cloned repository
            
        Returns:
            Dictionary with repository metadata
        """
        metadata = {
            'commit_count': 0,
            'latest_commit': '',
            'latest_commit_date': '',
            'branches': [],
            'authors': [],
            'file_count': 0,
            'repo_size_bytes': 0
        }
        
        try:
            # Get latest commit info
            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=format:%H|%an|%ae|%ad|%s'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout:
                parts = result.stdout.split('|')
                if len(parts) >= 5:
                    metadata['latest_commit'] = parts[0]
                    metadata['latest_commit_author'] = parts[1]
                    metadata['latest_commit_email'] = parts[2]
                    metadata['latest_commit_date'] = parts[3]
                    metadata['latest_commit_message'] = parts[4]
            
            # Count total files (excluding .git directory)
            file_count = 0
            repo_size = 0
            
            for root, _, files in os.walk(repo_path):
                if '.git' in root:
                    continue
                for file in files:
                    file_count += 1
                    try:
                        file_path = os.path.join(root, file)
                        repo_size += os.path.getsize(file_path)
                    except:
                        pass
                        
            metadata['file_count'] = file_count
            metadata['repo_size_bytes'] = repo_size
            
            # Get other metadata as needed
            return metadata
            
        except Exception as e:
            logger.error(f"Error getting repository metadata: {str(e)}")
            return metadata
    
    def scan_repository(self, repo_url: str, branch: Optional[str] = None, 
                        auth_token: Optional[str] = None,
                        progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Clone a repository and scan it for PII and sensitive information.
        
        Args:
            repo_url: URL of the Git repository
            branch: Branch to clone (default: repository default branch)
            auth_token: Authentication token for private repositories
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Dictionary with scan results
        """
        start_time = time.time()
        
        # Performance improvement logging
        logger.info(f"Starting optimized repository scan for {repo_url}")
        
        if progress_callback:
            progress_callback(0, 100, f"Cloning repository: {repo_url}")
        
        # First, clone the repository
        clone_result = self.clone_repository(repo_url, branch, auth_token)
        
        if clone_result['status'] != 'success':
            logger.warning(f"Failed to clone repository: {clone_result['message']}")
            if progress_callback:
                progress_callback(100, 100, f"Error: {clone_result['message']}")
                
            return {
                'scan_type': 'repository',
                'status': 'error',
                'message': clone_result['message'],
                'repo_url': repo_url,
                'branch': branch or 'default',
                'scan_time': datetime.now().isoformat(),
                'process_time_seconds': time.time() - start_time,
                'findings': []
            }
        
        repo_path = clone_result['repo_path']
        
        # Log cloning performance
        clone_time = time.time() - start_time
        logger.info(f"Repository cloned in {clone_time:.2f} seconds")
        
        if progress_callback:
            progress_callback(10, 100, f"Repository cloned successfully. Starting scan...")
        
        # Now scan the repository using the code scanner
        try:
            # Configure improved ignore patterns specific to repositories
            ignore_patterns = [
                # Git and version control
                "**/.git/**",           # Git internals
                "**/.svn/**",           # SVN internals
                "**/.hg/**",            # Mercurial internals
                "**/.bzr/**",           # Bazaar internals
                
                # Dependencies and packages
                "**/node_modules/**",   # Node.js dependencies
                "**/bower_components/**", # Bower components
                "**/jspm_packages/**",  # JSPM packages
                "**/vendor/**",         # Vendor packages (PHP, Ruby)
                "**/packages/**",       # Generic packages directory
                "**/Pods/**",           # CocoaPods
                "**/dist/**",           # Distribution artifacts
                "**/build/**",          # Build artifacts
                
                # Python specific
                "**/__pycache__/**",    # Python cache
                "**/venv/**",           # Python virtual environment
                "**/env/**",            # Python virtual environment
                "**/*.pyc",             # Python compiled files
                "**/*.pyo",             # Python optimized files
                
                # Java specific
                "**/target/**",         # Maven build directory
                "**/bin/**",            # Binary directory
                "**/build/**",          # Gradle build directory
                "**/*.class",           # Java compiled files
                
                # JavaScript and web specific
                "**/*.min.js",          # Minified JavaScript
                "**/*.min.css",         # Minified CSS
                "**/bundle.js",         # Bundled JavaScript
                "**/coverage/**",       # Code coverage reports
                
                # IDE and system files
                "**/.idea/**",          # IntelliJ IDEA
                "**/.vscode/**",        # VS Code
                "**/.DS_Store",         # macOS metadata
                "**/Thumbs.db",         # Windows metadata
                
                # Common binary file extensions
                "**/*.jpg", "**/*.jpeg", "**/*.png", "**/*.gif", "**/*.bmp", "**/*.ico",
                "**/*.pdf", "**/*.zip", "**/*.tar", "**/*.gz", "**/*.rar", "**/*.7z",
                "**/*.exe", "**/*.dll", "**/*.so", "**/*.dylib", "**/*.jar", "**/*.war",
                "**/*.ear", "**/*.db", "**/*.sqlite", "**/*.sqlite3"
            ]
            
            # Pass the progress callback to the code scanner
            if progress_callback:
                # Create a wrapper function to offset the progress (10-90% range)
                def adjusted_progress_callback(current, total, current_file):
                    adjusted_progress = 10 + int((current / total) * 80)
                    progress_callback(adjusted_progress, 100, f"Scanning file {current}/{total}: {current_file}")
                    
                self.code_scanner.set_progress_callback(adjusted_progress_callback)
            
            # Measure scan time separately
            scan_start_time = time.time()
            
            # Scan the directory with optimized performance settings
            scan_results = self.code_scanner.scan_directory(
                directory_path=repo_path,
                ignore_patterns=ignore_patterns,
                max_file_size_mb=20,     # Limit max file size to 20MB
                continue_from_checkpoint=True,
                max_files=500            # Limit to 500 files maximum for better performance
            )
            
            # Log scan performance
            scan_time = time.time() - scan_start_time
            total_time = time.time() - start_time
            
            logger.info(f"Repository scanning completed in {scan_time:.2f} seconds")
            logger.info(f"Total process time: {total_time:.2f} seconds")
            logger.info(f"Files scanned: {scan_results.get('files_scanned', 0)}")
            logger.info(f"Files skipped: {scan_results.get('files_skipped', 0)}")
            logger.info(f"Findings: {scan_results.get('total_findings', 0)}")
            
            if progress_callback:
                progress_callback(90, 100, "Finalizing results...")
            
            # Add repository metadata
            scan_results['scan_type'] = 'repository'
            scan_results['repo_url'] = repo_url
            scan_results['branch'] = branch or 'default'
            scan_results['repository_metadata'] = clone_result.get('metadata', {})
            scan_results['scan_time'] = datetime.now().isoformat()
            scan_results['process_time_seconds'] = time.time() - start_time
            scan_results['clone_time_seconds'] = clone_time
            scan_results['scan_time_seconds'] = scan_time
            
            # Apply consent analyzer to enhance findings with remediation suggestions
            if progress_callback:
                progress_callback(95, 100, "Analyzing consent and legal basis issues...")
            
            scan_results['repo_path'] = repo_path  # Add repo path for context in consent analyzer
            scan_results = apply_consent_analyzer(scan_results)
            
            if progress_callback:
                progress_callback(100, 100, "Scan completed successfully")
            
            return scan_results
            
        except Exception as e:
            logger.error(f"Error scanning repository: {str(e)}")
            
            if progress_callback:
                progress_callback(100, 100, f"Error: {str(e)}")
                
            return {
                'scan_type': 'repository',
                'status': 'error',
                'message': f'Error scanning repository: {str(e)}',
                'repo_url': repo_url,
                'branch': branch or 'default',
                'scan_time': datetime.now().isoformat(),
                'process_time_seconds': time.time() - start_time,
                'findings': []
            }
        finally:
            # Clean up temporary directory
            self._cleanup_temp_dirs()
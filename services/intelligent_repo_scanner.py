"""
Intelligent Repository Scanner - Advanced Scalable Scanning Strategy

Implements multiple scanning strategies based on repository characteristics:
1. Sampling Strategy - Statistical sampling for massive repos
2. Priority-Based Strategy - Focus on high-risk files first
3. Progressive Scanning - Incremental depth scanning
4. Pattern-Based Strategy - Focus on specific patterns/directories
"""

import os
import re
import git
import uuid
import time
import shutil
import tempfile
import logging

# Import centralized logging
try:
    from utils.centralized_logger import get_scanner_logger
    logger = get_scanner_logger("intelligent_repo_scanner")
except ImportError:
    # Fallback to standard logging if centralized logger not available
    logger = logging.getLogger(__name__)
import subprocess
import concurrent.futures
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Tuple
from pathlib import Path
import random
from collections import Counter

logger = logging.getLogger("services.intelligent_repo_scanner")

class IntelligentRepoScanner:
    """Advanced repository scanner with multiple scaling strategies."""
    
    def __init__(self, code_scanner):
        self.code_scanner = code_scanner
        self.temp_dirs = []
        
        # Scanning configuration
        self.MAX_SCAN_TIME = 60  # Maximum scan time in seconds
        self.MAX_FILES_BASIC = 50  # Basic scan limit
        self.MAX_FILES_DEEP = 200  # Deep scan limit
        self.SAMPLING_THRESHOLD = 500  # Use sampling for repos with >500 files
        
        # File priority weights
        self.FILE_PRIORITIES = {
            # High priority - likely to contain sensitive data
            'config': 3.0,     # config files, .env files
            'auth': 3.0,       # authentication, security
            'api': 2.5,        # API endpoints, controllers
            'model': 2.5,      # data models, entities
            'service': 2.0,    # business logic services
            'util': 1.5,       # utility functions
            'test': 0.5,       # test files (lower priority)
            'doc': 0.3,        # documentation
        }
        
        # Directory priority weights
        self.DIR_PRIORITIES = {
            'src/main': 3.0,
            'app': 2.8,
            'lib': 2.5,
            'config': 3.0,
            'auth': 3.0,
            'api': 2.5,
            'models': 2.5,
            'services': 2.0,
            'controllers': 2.5,
            'middleware': 2.0,
            'utils': 1.5,
            'test': 0.5,
            'tests': 0.5,
            'docs': 0.3,
            'documentation': 0.3,
        }

    def scan_repository_intelligent(self, repo_url: str, branch: Optional[str] = None, 
                                  scan_mode: str = "smart", max_files: Optional[int] = None,
                                  progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Intelligent repository scanning with adaptive strategies.
        
        Args:
            repo_url: URL of the Git repository
            branch: Branch to clone (optional)
            scan_mode: "fast", "smart", "deep", "sampling"
            max_files: Maximum files to scan (overrides mode defaults)
            progress_callback: Progress reporting callback
            
        Returns:
            Dictionary with comprehensive scan results
        """
        start_time = time.time()
        scan_id = f"smart_repo_{uuid.uuid4().hex[:8]}"
        
        # Initialize comprehensive results
        scan_results = {
            'scan_id': scan_id,
            'scan_type': 'Intelligent Code Scanner',
            'timestamp': datetime.now().isoformat(),
            'region': 'Netherlands',
            'url': repo_url,
            'scan_mode': scan_mode,
            'repository_stats': {},
            'scanning_strategy': {},
            'findings': [],
            'files_scanned': 0,
            'files_skipped': 0,
            'total_files_found': 0,
            'total_lines': 0,
            'scan_coverage': 0.0,
            'status': 'completed'
        }
        
        try:
            # Step 1: Fast repository analysis
            repo_path = self._clone_repository_shallow(repo_url, branch)
            if not repo_path:
                scan_results['status'] = 'failed'
                scan_results['error'] = 'Failed to clone repository'
                return scan_results
            
            # Step 2: Repository analysis and strategy selection
            repo_analysis = self._analyze_repository_structure(repo_path)
            scan_results['repository_stats'] = repo_analysis
            
            # Step 3: Select optimal scanning strategy
            strategy = self._select_scanning_strategy(repo_analysis, scan_mode, max_files)
            scan_results['scanning_strategy'] = strategy
            
            if progress_callback:
                progress_callback(10, 100, "Repository analyzed, starting intelligent scan...")
            
            # Step 4: Execute selected strategy
            if strategy['type'] == 'sampling':
                files_to_scan = self._select_files_by_sampling(repo_path, repo_analysis, strategy)
            elif strategy['type'] == 'priority':
                files_to_scan = self._select_files_by_priority(repo_path, repo_analysis, strategy)
            else:  # comprehensive or progressive
                files_to_scan = self._select_files_comprehensive(repo_path, repo_analysis, strategy)
            
            scan_results['total_files_found'] = repo_analysis['total_files']
            # Improved coverage calculation
            actual_coverage = (len(files_to_scan) / max(repo_analysis['total_files'], 1)) * 100
            scan_results['scan_coverage'] = min(actual_coverage, 100.0)  # Cap at 100%
            
            # Step 5: Parallel scanning execution
            findings = self._execute_parallel_scanning(
                files_to_scan, repo_path, scan_results, progress_callback
            )
            
            scan_results['findings'] = findings
            scan_results['duration_seconds'] = time.time() - start_time
            
            logger.info(f"Intelligent scan completed: {len(findings)} findings in {scan_results['duration_seconds']:.1f}s")
            logger.info(f"Coverage: {scan_results['scan_coverage']:.1f}% ({scan_results['files_scanned']}/{scan_results['total_files_found']} files)")
            
        except Exception as e:
            logger.error(f"Intelligent repository scan failed: {str(e)}")
            scan_results['status'] = 'failed'
            scan_results['error'] = str(e)
        finally:
            self._cleanup()
            
        return scan_results

    def _analyze_repository_structure(self, repo_path: str) -> Dict[str, Any]:
        """Analyze repository structure to determine optimal scanning strategy."""
        analysis = {
            'total_files': 0,
            'code_files': 0,
            'config_files': 0,
            'test_files': 0,
            'languages': Counter(),
            'directories': [],
            'file_sizes': [],
            'depth_levels': Counter(),
            'high_priority_files': 0,
            'estimated_risk_level': 'low'
        }
        
        code_extensions = {'.py', '.js', '.ts', '.java', '.php', '.cs', '.go', '.rb', '.cpp', '.c', '.h'}
        config_extensions = {'.json', '.yml', '.yaml', '.xml', '.env', '.ini', '.conf', '.config'}
        test_patterns = {'test', 'tests', 'spec', '__test__', '.test.', '.spec.'}
        
        try:
            for root, dirs, files in os.walk(repo_path):
                # Skip common exclude directories
                dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__', 
                          'dist', 'build', '.vscode', '.idea', 'target', 'bin', 'obj'}]
                
                depth = root.replace(repo_path, '').count(os.sep)
                analysis['depth_levels'][depth] += len(files)
                
                for filename in files:
                    file_path = os.path.join(root, filename)
                    analysis['total_files'] += 1
                    
                    # Get file extension and size
                    _, ext = os.path.splitext(filename.lower())
                    try:
                        size = os.path.getsize(file_path)
                        analysis['file_sizes'].append(size)
                    except:
                        size = 0
                    
                    # Categorize files
                    if ext in code_extensions:
                        analysis['code_files'] += 1
                        analysis['languages'][ext] += 1
                        
                        # Check for high-priority patterns
                        if any(pattern in filename.lower() or pattern in root.lower() 
                               for pattern in ['config', 'auth', 'api', 'model', 'service']):
                            analysis['high_priority_files'] += 1
                    
                    elif ext in config_extensions or any(pattern in filename.lower() 
                                                       for pattern in ['.env', 'config', 'settings']):
                        analysis['config_files'] += 1
                        analysis['high_priority_files'] += 1
                    
                    elif any(pattern in filename.lower() or pattern in root.lower() 
                            for pattern in test_patterns):
                        analysis['test_files'] += 1
        except Exception as e:
            logger.error(f"Error analyzing repository structure: {str(e)}")
        
        # Calculate estimated risk level
        risk_score = (
            analysis['config_files'] * 2 +
            analysis['high_priority_files'] * 1.5 +
            len(analysis['languages']) * 0.5
        )
        
        if risk_score > 50:
            analysis['estimated_risk_level'] = 'high'
        elif risk_score > 20:
            analysis['estimated_risk_level'] = 'medium'
        
        logger.info(f"Repository analysis: {analysis['total_files']} files, "
                   f"{analysis['code_files']} code files, "
                   f"{analysis['estimated_risk_level']} risk level")
        
        return analysis

    def _select_scanning_strategy(self, repo_analysis: Dict[str, Any], 
                                scan_mode: str, max_files: Optional[int]) -> Dict[str, Any]:
        """Select optimal scanning strategy based on repository characteristics."""
        
        total_files = repo_analysis['total_files']
        code_files = repo_analysis['code_files']
        risk_level = repo_analysis['estimated_risk_level']
        
        # Determine strategy based on repository size and scan mode
        if scan_mode == "fast" or total_files <= 50:
            strategy_type = "comprehensive"
            target_files = min(total_files, 50)
            
        elif scan_mode == "sampling" or total_files > self.SAMPLING_THRESHOLD:
            strategy_type = "sampling"
            target_files = min(max_files or 100, total_files)
            
        elif scan_mode == "deep" or risk_level == "high":
            strategy_type = "priority"
            target_files = min(max_files or self.MAX_FILES_DEEP, total_files)
            
        else:  # smart mode
            if total_files > 200:
                strategy_type = "sampling"
                target_files = 150
            elif total_files > 100:
                strategy_type = "priority"
                target_files = 100
            else:
                strategy_type = "comprehensive"
                target_files = total_files
        
        return {
            'type': strategy_type,
            'target_files': target_files,
            'max_scan_time': self.MAX_SCAN_TIME,
            'parallel_workers': min(4, max(1, target_files // 20)),
            'reasoning': f"Selected {strategy_type} strategy for {total_files} files with {risk_level} risk"
        }

    def _select_files_by_sampling(self, repo_path: str, repo_analysis: Dict[str, Any], 
                                strategy: Dict[str, Any]) -> List[str]:
        """Statistical sampling strategy for massive repositories."""
        all_files = []
        target_files = strategy['target_files']
        
        # Collect all scannable files with priorities
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__', 'dist', 'build'}]
            
            for filename in files:
                if self._is_scannable_file(filename):
                    file_path = os.path.join(root, filename)
                    priority = self._calculate_file_priority(file_path, repo_path)
                    all_files.append((file_path, priority))
        
        # Sort by priority and apply weighted sampling
        all_files.sort(key=lambda x: x[1], reverse=True)
        
        # Take top 50% by priority, then random sample the rest
        high_priority_count = min(target_files // 2, len(all_files) // 2)
        selected_files = [f[0] for f in all_files[:high_priority_count]]
        
        # Random sample from remaining files
        remaining_files = all_files[high_priority_count:]
        if remaining_files and len(selected_files) < target_files:
            sample_size = min(target_files - len(selected_files), len(remaining_files))
            sampled = random.sample(remaining_files, sample_size)
            selected_files.extend([f[0] for f in sampled])
        
        logger.info(f"Sampling strategy: selected {len(selected_files)} files from {len(all_files)} total")
        return selected_files

    def _select_files_by_priority(self, repo_path: str, repo_analysis: Dict[str, Any], 
                                strategy: Dict[str, Any]) -> List[str]:
        """Priority-based selection focusing on high-risk files."""
        all_files = []
        target_files = strategy['target_files']
        
        # Collect all files with detailed priority scoring
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__', 'dist', 'build'}]
            
            for filename in files:
                if self._is_scannable_file(filename):
                    file_path = os.path.join(root, filename)
                    priority = self._calculate_file_priority(file_path, repo_path)
                    all_files.append((file_path, priority))
        
        # Sort by priority and take top files
        all_files.sort(key=lambda x: x[1], reverse=True)
        selected_files = [f[0] for f in all_files[:target_files]]
        
        logger.info(f"Priority strategy: selected top {len(selected_files)} priority files")
        return selected_files

    def _select_files_comprehensive(self, repo_path: str, repo_analysis: Dict[str, Any], 
                                   strategy: Dict[str, Any]) -> List[str]:
        """Comprehensive selection for smaller repositories."""
        all_files = []
        target_files = strategy['target_files']
        
        # Collect all scannable files
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__', 'dist', 'build'}]
            
            for filename in files:
                if self._is_scannable_file(filename):
                    file_path = os.path.join(root, filename)
                    all_files.append(file_path)
        
        # Take all files up to target limit
        selected_files = all_files[:target_files]
        logger.info(f"Comprehensive strategy: selected {len(selected_files)} files")
        return selected_files

    def _calculate_file_priority(self, file_path: str, repo_path: str) -> float:
        """Calculate priority score for a file based on multiple factors."""
        rel_path = os.path.relpath(file_path, repo_path).lower()
        filename = os.path.basename(file_path).lower()
        
        priority = 1.0  # Base priority
        
        # File type priority
        for pattern, weight in self.FILE_PRIORITIES.items():
            if pattern in filename or pattern in rel_path:
                priority += weight
        
        # Directory priority
        for dir_pattern, weight in self.DIR_PRIORITIES.items():
            if dir_pattern in rel_path:
                priority += weight
        
        # Special patterns (high risk)
        high_risk_patterns = ['password', 'secret', 'key', 'token', 'credential', 
                             'config', '.env', 'database', 'db', 'auth', 'login']
        for pattern in high_risk_patterns:
            if pattern in filename:
                priority += 2.0
        
        # File extension priority
        ext = os.path.splitext(filename)[1]
        if ext in {'.env', '.conf', '.config', '.ini', '.properties'}:
            priority += 2.5
        elif ext in {'.py', '.js', '.java', '.php', '.cs'}:
            priority += 1.0
        elif ext in {'.json', '.yml', '.yaml', '.xml'}:
            priority += 1.5
        
        return priority

    def _is_scannable_file(self, filename: str) -> bool:
        """Check if file should be scanned."""
        scannable_extensions = {
            '.py', '.js', '.ts', '.java', '.php', '.cs', '.go', '.rb', '.cpp', '.c', '.h',
            '.json', '.yml', '.yaml', '.xml', '.env', '.ini', '.conf', '.config', '.properties',
            '.sql', '.sh', '.bat', '.ps1', '.tf', '.dockerfile'
        }
        
        _, ext = os.path.splitext(filename.lower())
        return ext in scannable_extensions and not filename.startswith('.')

    def _execute_parallel_scanning(self, files_to_scan: List[str], repo_path: str, 
                                 scan_results: Dict[str, Any], 
                                 progress_callback: Optional[Callable]) -> List[Dict[str, Any]]:
        """Execute file scanning in parallel with progress tracking."""
        all_findings = []
        workers = scan_results['scanning_strategy']['parallel_workers']
        
        start_time = time.time()
        max_time = scan_results['scanning_strategy']['max_scan_time']
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            # Submit all scanning tasks
            future_to_file = {
                executor.submit(self._scan_single_file, file_path, repo_path): file_path 
                for file_path in files_to_scan
            }
            
            completed = 0
            for future in concurrent.futures.as_completed(future_to_file, timeout=max_time):
                try:
                    # Check timeout
                    if time.time() - start_time > max_time:
                        logger.warning("Parallel scanning timeout reached")
                        break
                    
                    file_path = future_to_file[future]
                    findings = future.result(timeout=5)  # 5 second per file timeout
                    
                    if findings:
                        all_findings.extend(findings)
                    
                    completed += 1
                    # Update scan results with actual progress
                    scan_results['files_scanned'] = completed
                    scan_results['files_processed'] = completed  # For metrics compatibility
                    
                    # Progress callback
                    if progress_callback:
                        progress = 20 + int(70 * completed / len(files_to_scan))
                        rel_path = os.path.relpath(file_path, repo_path)
                        progress_callback(progress, 100, f"Scanned {rel_path}")
                
                except concurrent.futures.TimeoutError:
                    scan_results['files_skipped'] += 1
                    logger.warning(f"File scan timeout: {future_to_file[future]}")
                except Exception as e:
                    scan_results['files_skipped'] += 1
                    logger.warning(f"File scan error: {str(e)}")
        
        # Ensure files_scanned is set even if no files were completed
        if 'files_scanned' not in scan_results:
            scan_results['files_scanned'] = completed
            scan_results['files_processed'] = completed
        
        logger.info(f"Intelligent scan completed: {len(all_findings)} findings from {completed} files")
        return all_findings

    def _scan_single_file(self, file_path: str, repo_path: str) -> List[Dict[str, Any]]:
        """Scan a single file for findings."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Use the existing code scanner
            findings = []
            rel_path = os.path.relpath(file_path, repo_path)
            
            # Enhanced PII patterns for Python algorithms and code repositories
            patterns = [
                # Email patterns
                (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'Email Address'),
                # Phone patterns  
                (r'\b(?:\+31|0031|0)\s*[1-9](?:\s*\d){8}\b', 'Dutch Phone Number'),
                (r'\b\d{3}-\d{3}-\d{4}\b', 'US Phone Number'),
                (r'\b\+\d{1,3}\s?\d{1,4}\s?\d{1,4}\s?\d{1,9}\b', 'International Phone'),
                # ID patterns
                (r'\b\d{9}\b', 'Potential BSN'),
                (r'\b\d{3}-\d{2}-\d{4}\b', 'SSN'),
                (r'\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b', 'Credit Card'),
                # Credential patterns
                (r'password\s*[:=]\s*["\']([^"\']+)["\']', 'Hardcoded Password'),
                (r'api[_-]?key\s*[:=]\s*["\']([^"\']+)["\']', 'API Key'),
                (r'secret\s*[:=]\s*["\']([^"\']+)["\']', 'Secret'),
                (r'token\s*[:=]\s*["\']([^"\']+)["\']', 'Access Token'),
                # AWS and cloud patterns
                (r'AKIA[0-9A-Z]{16}', 'AWS Access Key'),
                (r'aws[_-]?secret\s*[:=]\s*["\']([^"\']+)["\']', 'AWS Secret'),
                # Database patterns
                (r'db[_-]?password\s*[:=]\s*["\']([^"\']+)["\']', 'Database Password'),
                (r'mongodb://[^"\'\\s]+', 'MongoDB Connection String'),
                (r'mysql://[^"\'\\s]+', 'MySQL Connection String'),
                # Private key patterns
                (r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----', 'Private Key'),
                (r'-----BEGIN\s+CERTIFICATE-----', 'Certificate'),
                # Personal info in comments (common in algorithm repos)
                (r'#\s*Author:\s*([A-Za-z\s]+)', 'Author Name'),
                (r'#\s*Email:\s*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})', 'Author Email'),
                (r'#\s*Contact:\s*(.+)', 'Contact Information'),
            ]
            
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                for pattern, finding_type in patterns:
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        findings.append({
                            'type': finding_type,
                            'file': rel_path,
                            'line': line_num,
                            'description': f'{finding_type} detected in {rel_path}',
                            'severity': 'High' if finding_type in ['Hardcoded Password', 'API Key', 'Secret'] else 'Medium',
                            'risk_level': 'high' if finding_type in ['Hardcoded Password', 'API Key', 'Secret'] else 'medium',
                            'matched_text': match.group()[:50] + ('...' if len(match.group()) > 50 else '')
                        })
            
            return findings
            
        except Exception as e:
            logger.warning(f"Error scanning file {file_path}: {str(e)}")
            return []

    def _clone_repository_shallow(self, repo_url: str, branch: Optional[str] = None) -> Optional[str]:
        """Clone repository with minimal depth for faster cloning."""
        try:
            # Validate and fix repository URL
            if repo_url.endswith('/') and repo_url.count('/') == 4:
                # Incomplete URL like "https://github.com/big-data-europe/"
                suggested_repos = [
                    "docker-hadoop", "docker-spark", "docker-hive", 
                    "docker-hadoop-spark-workbench", "docker-flink", "README"
                ]
                raise Exception(f"❌ Incomplete repository URL '{repo_url}'. Please specify a repository name.\n\n✅ Popular big-data-europe repos to try:\n• {repo_url}docker-hadoop\n• {repo_url}docker-spark\n• {repo_url}docker-hive")
            
            # Handle directory-specific URLs (like /tree/master/data)
            if '/tree/' in repo_url:
                base_repo = repo_url.split('/tree/')[0]
                logger.info(f"Converting directory URL to repository URL: {repo_url} -> {base_repo}")
                repo_url = base_repo
            
            temp_dir = tempfile.mkdtemp(prefix="intelligent_repo_")
            self.temp_dirs.append(temp_dir)
            
            # Shallow clone with single branch - try without specifying branch first
            clone_args = ['git', 'clone', '--depth', '1']
            if branch:
                clone_args.extend(['--branch', branch, '--single-branch'])
            clone_args.extend([repo_url, temp_dir])
            
            result = subprocess.run(
                clone_args,
                capture_output=True,
                text=True,
                timeout=45  # 45 second timeout for cloning
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully cloned repository to {temp_dir}")
                return temp_dir
            else:
                error_msg = result.stderr
                if "not found" in error_msg.lower():
                    if "big-data-europe" in repo_url:
                        raise Exception(f"❌ Repository not found.\n\n✅ Try one of these popular big-data-europe repos:\n• https://github.com/big-data-europe/docker-hadoop\n• https://github.com/big-data-europe/docker-spark\n• https://github.com/big-data-europe/docker-hive\n• https://github.com/big-data-europe/docker-hadoop-spark-workbench")
                logger.error(f"Clone failed: {error_msg}")
                raise Exception(f"Clone failed: {error_msg}")
                
        except subprocess.TimeoutExpired:
            logger.error("Repository clone timed out")
            raise Exception("Repository clone timed out after 45 seconds")
        except Exception as e:
            logger.error(f"Clone error: {str(e)}")
            # Only return None for non-critical errors, re-raise for important ones
            if "Repository not found" in str(e) or "not found" in str(e).lower():
                raise e
            return None

    def _cleanup(self):
        """Clean up temporary directories."""
        for temp_dir in self.temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"Cleanup error: {str(e)}")
        self.temp_dirs.clear()
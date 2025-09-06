"""
Parallel Repository Scanner

This module provides a high-performance repository scanning implementation that uses
parallel processing for efficient scanning of large codebases. It implements thread pooling
and batched analysis to optimize performance while maintaining reliability.
"""

import os
import re
import git
import uuid
import time
import json
import shutil
import fnmatch
import logging

# Import centralized logging
try:
    from utils.centralized_logger import get_scanner_logger
    logger = get_scanner_logger("parallel_repo_scanner")
except ImportError:
    # Fallback to standard logging if centralized logger not available
    logger = logging.getLogger(__name__)
import tempfile
import traceback
import threading
import subprocess
import stat
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Set, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging


class ParallelRepoScanner:
    """
    A high-performance repository scanner that uses parallel processing for efficient
    scanning of large codebases.
    """

    def __init__(self, code_scanner=None, pii_detector=None):
        """
        Initialize the scanner with optional code scanners and PII detectors.
        
        Args:
            code_scanner: The code scanner to use for detailed code analysis
            pii_detector: The PII detector for identifying sensitive information
        """
        self.code_scanner = code_scanner
        self.pii_detector = pii_detector
        self.max_files = 5000
        self.max_workers = 8
        self.batch_size = 100
        self.file_size_limit = 5 * 1024 * 1024  # 5MB
        self.max_scan_time = 300  # 5 minutes max per repository

    def scan_repository(self, repo_url: str, branch: str = "main", 
                      progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Scan a GitHub repository for GDPR compliance issues.
        
        Args:
            repo_url: URL of the GitHub repository
            branch: Branch to scan (default: main)
            progress_callback: Function to call with progress updates
            
        Returns:
            Dictionary containing scan results
        """
        start_time = time.time()
        repo_path = None
        result = {
            "scan_id": str(uuid.uuid4()),
            "scan_timestamp": datetime.now().isoformat(),
            "repository_url": repo_url,
            "branch": branch,
            "findings": [],
            "summary": {
                "total_files": 0,
                "scanned_files": 0,
                "skipped_files": 0,
                "pii_instances": 0,
                "high_risk_count": 0,
                "medium_risk_count": 0,
                "low_risk_count": 0,
                "gdpr_principles_affected": set(),
                "overall_compliance_score": 100
            },
            "status": "started",
            "execution_time_seconds": 0
        }
        
        try:
            # Clone the repository
            logger.info(f"Cloning repository: {repo_url}")
            repo_path = self._clone_repository(repo_url, branch)
            
            # Get basic repository metadata
            logger.info("Getting repository metadata")
            result["metadata"] = self._get_repository_metadata(repo_path)
            
            # Collect files to scan
            logger.info(f"Collecting files to scan in {repo_path}")
            all_files = self._collect_files_to_scan(repo_path)
            total_files = len(all_files)
            result["summary"]["total_files"] = total_files
            
            # Apply intelligent sampling for very large repositories
            is_large_repo = total_files > 1000
            is_ultra_large = total_files > 5000
            files_to_scan = self._apply_sampling(all_files, is_large_repo, is_ultra_large)
            
            # Record how many files we're actually scanning
            scanned_file_count = len(files_to_scan)
            result["summary"]["scanned_files"] = scanned_file_count
            result["summary"]["skipped_files"] = total_files - scanned_file_count
            logger.info(f"Scanning {scanned_file_count} files")
            
            # Scan the files in parallel batches
            file_results = self._parallel_scan_files(
                files_to_scan, 
                repo_path, 
                is_ultra_large,
                progress_callback
            )
            
            # Aggregate file-level results into repository-level results
            for file_result in file_results:
                if file_result and "findings" in file_result:
                    # Add file-level findings to repository-level findings
                    result["findings"].extend(file_result["findings"])
                    
                    # Update summary counts
                    result["summary"]["pii_instances"] += file_result.get("pii_count", 0)
                    
                    # Update affected GDPR principles
                    if "gdpr_principles_affected" in file_result:
                        result["summary"]["gdpr_principles_affected"].update(
                            file_result["gdpr_principles_affected"]
                        )
            
            # Count risk levels
            for finding in result["findings"]:
                risk_level = finding.get("risk_level", "medium")
                if risk_level == "high":
                    result["summary"]["high_risk_count"] += 1
                elif risk_level == "medium":
                    result["summary"]["medium_risk_count"] += 1
                elif risk_level == "low":
                    result["summary"]["low_risk_count"] += 1
            
            # Convert set to list for JSON serialization
            result["summary"]["gdpr_principles_affected"] = list(
                result["summary"]["gdpr_principles_affected"]
            )
            
            # Calculate overall compliance score
            result["summary"]["overall_compliance_score"] = self._calculate_compliance_score(
                result["summary"]
            )
            
            result["status"] = "completed"
            
        except Exception as e:
            logger.error(f"Error during repository scan: {str(e)}")
            logger.error(traceback.format_exc())
            result["status"] = "failed"
            result["error"] = str(e)
            
        finally:
            # Clean up temporary repository directory
            if repo_path and os.path.exists(repo_path):
                try:
                    # Use shutil.rmtree with error handling to delete the directory
                    def handle_readonly(func, path, exc_info):
                        # Make the file/directory writable if needed
                        os.chmod(path, stat.S_IWRITE)
                        func(path)  # Try again
                    
                    shutil.rmtree(repo_path, onerror=handle_readonly)
                except Exception as e:
                    logger.warning(f"Failed to clean up repository directory: {str(e)}")
            
            # Record total execution time
            execution_time = time.time() - start_time
            result["execution_time_seconds"] = execution_time
            logger.info(f"Scan completed in {execution_time:.2f} seconds")
            
        return result

    def _clone_repository(self, repo_url: str, branch: str = "main") -> str:
        """
        Clone a GitHub repository to a temporary directory.
        
        Args:
            repo_url: GitHub repository URL
            branch: Branch to clone
            
        Returns:
            Path to the cloned repository
        """
        # Create a temporary directory for the repository
        repo_dir = tempfile.mkdtemp(prefix="repo_scan_")
        
        # Fast clone with depth=1 for better performance
        logger.info(f"Fast cloning repository from {repo_url} (branch: {branch})")
        try:
            # Use git command directly for better performance
            subprocess.run(
                ["git", "clone", "--depth", "1", "--branch", branch, repo_url, repo_dir],
                check=True,
                capture_output=True
            )
            return repo_dir
        except subprocess.CalledProcessError as e:
            # If the branch doesn't exist, try without specifying branch
            if b"Remote branch" in e.stderr and b"not found" in e.stderr:
                logger.warning(f"Branch {branch} not found, trying default branch")
                shutil.rmtree(repo_dir)
                repo_dir = tempfile.mkdtemp(prefix="repo_scan_")
                subprocess.run(
                    ["git", "clone", "--depth", "1", repo_url, repo_dir],
                    check=True,
                    capture_output=True
                )
                return repo_dir
            raise Exception(f"Failed to clone repository: {str(e)}")

    def _get_repository_metadata(self, repo_path: str) -> Dict[str, Any]:
        """
        Get metadata about the repository.
        
        Args:
            repo_path: Path to the cloned repository
            
        Returns:
            Dictionary containing repository metadata
        """
        try:
            repo = git.Repo(repo_path)
            
            # Get repository name
            remote_url = repo.remotes.origin.url
            repo_name = os.path.basename(remote_url)
            if repo_name.endswith('.git'):
                repo_name = repo_name[:-4]
                
            # Get commit information
            commit = repo.head.commit
            last_commit_date = commit.committed_datetime.isoformat()
            
            # Count files safely
            file_count = 0
            try:
                for item in repo.tree().traverse():
                    # Use GitPython's built-in type checking
                    try:
                        if item.type == 'blob':
                            file_count += 1
                    except AttributeError:
                        # Fallback for different GitPython versions
                        if hasattr(item, 'mode') and not item.mode & 0o040000:  # Not a directory
                            file_count += 1
            except Exception as e:
                logger.warning(f"Error counting files: {e}")
                file_count = len([f for f in os.listdir(repo_path) if os.path.isfile(os.path.join(repo_path, f))])
            
            # Detect programming languages
            languages = self._detect_languages(repo_path)
            
            return {
                "name": repo_name,
                "last_commit_date": last_commit_date,
                "commit_hash": commit.hexsha,
                "author": f"{commit.author.name} <{commit.author.email}>",
                "file_count": file_count,
                "languages": languages
            }
        except Exception as e:
            logger.warning(f"Error getting repository metadata: {str(e)}")
            return {
                "name": "Unknown",
                "last_commit_date": "Unknown",
                "commit_hash": "Unknown",
                "author": "Unknown",
                "file_count": 0,
                "languages": []
            }

    def _detect_languages(self, repo_path: str) -> List[str]:
        """
        Detect programming languages used in the repository.
        
        Args:
            repo_path: Path to the cloned repository
            
        Returns:
            List of detected programming languages
        """
        language_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.c': 'C',
            '.cpp': 'C++',
            '.cs': 'C#',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.swift': 'Swift',
            '.rs': 'Rust',
            '.scala': 'Scala',
            '.kt': 'Kotlin',
            '.sh': 'Shell',
            '.html': 'HTML',
            '.css': 'CSS',
            '.sql': 'SQL'
        }
        
        language_counts = {}
        
        # Walk through the repository and count file extensions
        for root, _, files in os.walk(repo_path):
            for file in files:
                _, ext = os.path.splitext(file)
                if ext in language_extensions:
                    lang = language_extensions[ext]
                    language_counts[lang] = language_counts.get(lang, 0) + 1
        
        # Sort languages by frequency
        sorted_languages = sorted(
            language_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Return the names of languages only
        return [lang for lang, _ in sorted_languages]

    def _collect_files_to_scan(self, repo_path: str) -> List[str]:
        """
        Collect files to scan from the repository.
        
        Args:
            repo_path: Path to the cloned repository
            
        Returns:
            List of file paths to scan
        """
        # Patterns for files to exclude
        exclude_patterns = [
            # Binary files
            '*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.tiff', '*.ico',
            '*.pdf', '*.doc', '*.docx', '*.ppt', '*.pptx', '*.xls', '*.xlsx',
            '*.zip', '*.tar', '*.gz', '*.rar', '*.7z', '*.bin', '*.exe', '*.dll',
            '*.so', '*.dylib', '*.jar', '*.war', '*.ear', '*.class', '*.pyc',
            # Generated files
            'node_modules/**', 'venv/**', '.git/**', '.idea/**', '__pycache__/**',
            'build/**', 'dist/**', 'target/**', 'out/**', 'bin/**', 'obj/**',
            # Large data files
            '*.csv', '*.tsv', '*.parquet', '*.avro', '*.orc', '*.hdf5', '*.h5',
            # Debug and log files
            '*.log', '*.cache', '*.bak', '*.swp', '*.swo', '*.tmp', '.DS_Store'
        ]
        
        files_to_scan = []
        
        for root, _, files in os.walk(repo_path):
            # Skip excluded directories (faster than pattern matching)
            if any(excluded in root for excluded in [
                'node_modules', 'venv', '.git', '.idea', '__pycache__',
                'build', 'dist', 'target', 'out', 'bin', 'obj'
            ]):
                continue
                
            for file in files:
                file_path = os.path.join(root, file)
                
                # Skip if file matches any exclude pattern
                if any(fnmatch.fnmatch(file_path, os.path.join(repo_path, pattern)) or
                      fnmatch.fnmatch(file, pattern) for pattern in exclude_patterns):
                    continue
                    
                # Skip very large files by default
                try:
                    if os.path.getsize(file_path) > self.file_size_limit:
                        continue
                except OSError:
                    continue
                    
                files_to_scan.append(file_path)
                
        return files_to_scan

    def _apply_sampling(self, all_files: List[str], is_large_repo: bool, 
                      is_ultra_large: bool) -> List[str]:
        """
        Apply intelligent sampling for large repositories.
        
        Args:
            all_files: List of all files to scan
            is_large_repo: Whether the repository is large (>1000 files)
            is_ultra_large: Whether the repository is ultra-large (>5000 files)
            
        Returns:
            List of files to scan after sampling
        """
        if not is_large_repo:
            return all_files
            
        max_files = 500 if is_large_repo else self.max_files
        if is_ultra_large:
            max_files = 100
            logger.warning(f"Ultra-large repository detected with {len(all_files)} files. "
                         f"Using optimized scanning with only {max_files} representative files.")
        
        # Group files by extension for better representation
        files_by_ext = {}
        for file_path in all_files:
            _, ext = os.path.splitext(file_path)
            if not ext:
                ext = 'no_extension'
            if ext not in files_by_ext:
                files_by_ext[ext] = []
            files_by_ext[ext].append(file_path)
        
        # Sample files from each extension group to ensure representation
        sampled_files = []
        target_per_ext = max(1, max_files // len(files_by_ext))
        
        for ext, files in files_by_ext.items():
            if len(files) <= target_per_ext:
                sampled_files.extend(files)
            else:
                # Sample files at regular intervals for better coverage
                step = len(files) // target_per_ext
                samples = [files[i] for i in range(0, len(files), step)][:target_per_ext]
                sampled_files.extend(samples)
        
        # If we still have room for more files, add them from largest groups
        if len(sampled_files) < max_files:
            remaining_slots = max_files - len(sampled_files)
            sorted_exts = sorted(files_by_ext.items(), key=lambda x: len(x[1]), reverse=True)
            
            for ext, files in sorted_exts:
                already_sampled = sum(1 for f in sampled_files if os.path.splitext(f)[1] == ext)
                if already_sampled < len(files):
                    remaining_from_ext = [f for f in files if f not in sampled_files]
                    step = len(remaining_from_ext) // remaining_slots if remaining_slots > 0 else 1
                    additional_samples = [remaining_from_ext[i] for i in range(0, len(remaining_from_ext), step)]
                    count_to_add = min(remaining_slots, len(additional_samples))
                    sampled_files.extend(additional_samples[:count_to_add])
                    remaining_slots -= count_to_add
                    if remaining_slots <= 0:
                        break
        
        return sampled_files[:max_files]

    def _parallel_scan_files(self, files_to_scan: List[str], repo_path: str, 
                          is_ultra_large: bool,
                          progress_callback: Optional[Callable] = None) -> List[Dict[str, Any]]:
        """
        Scan files in parallel using thread pool.
        
        Args:
            files_to_scan: List of files to scan
            repo_path: Path to the repository
            is_ultra_large: Whether this is an ultra-large repository
            progress_callback: Function to call with progress updates
            
        Returns:
            List of file scan results
        """
        start_time = time.time()
        total_files = len(files_to_scan)
        file_results = []
        processed_count = 0
        
        # Configure worker count based on repository size
        max_workers = self.max_workers
        if is_ultra_large:
            max_workers = min(4, max_workers)  # Fewer workers for ultra-large repos
        
        # Process files in batches for better performance
        batches = [files_to_scan[i:i + self.batch_size] 
                 for i in range(0, len(files_to_scan), self.batch_size)]
        
        # Process each batch with a thread pool
        for batch_idx, batch in enumerate(batches):
            # Check if we've exceeded max scan time
            elapsed = time.time() - start_time
            if elapsed > self.max_scan_time:
                logger.warning(f"Scan exceeded max time ({elapsed:.1f}s). "
                             f"Stopping after processing {processed_count}/{total_files} files.")
                break
                
            batch_results = []
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Create a dictionary to map future to file path for better error tracking
                future_to_file = {
                    executor.submit(self._scan_single_file, file_path, repo_path, is_ultra_large): file_path
                    for file_path in batch
                }
                
                # Process completed tasks as they finish
                for i, future in enumerate(as_completed(future_to_file)):
                    file_path = future_to_file[future]
                    processed_count += 1
                    
                    # Update progress
                    if progress_callback:
                        rel_path = os.path.relpath(file_path, repo_path)
                        progress_callback(processed_count, total_files, rel_path)
                    
                    try:
                        result = future.result()
                        batch_results.append(result)
                    except Exception as e:
                        logger.warning(f"Error processing file {file_path}: {str(e)}")
                        batch_results.append(None)
            
            # Add batch results to overall results
            file_results.extend(batch_results)
            
        return file_results

    def _scan_single_file(self, file_path: str, repo_path: str, is_ultra_large: bool) -> Optional[Dict[str, Any]]:
        """
        Scan a single file for GDPR compliance issues.
        
        Args:
            file_path: Path to the file to scan
            repo_path: Path to the repository
            is_ultra_large: Whether this is an ultra-large repository
            
        Returns:
            Dictionary containing scan results for the file
        """
        try:
            # Set timeout for file processing - even more aggressive for ultra-large repos
            file_timeout = 10  # seconds
            if is_ultra_large:
                file_timeout = 5
            
            # Check file size again as a precaution
            file_size = os.path.getsize(file_path)
            if file_size > self.file_size_limit:
                logger.warning(f"File too large: {file_path} ({file_size/1024/1024:.1f} MB). Skipping.")
                return None
            
            # Use the CodeScanner if available
            if self.code_scanner and hasattr(self.code_scanner, 'scan_file'):
                # Use code scanner with timeout protection
                start_time = time.time()
                file_result = self.code_scanner.scan_file(file_path)
                
                # Check if we exceeded timeout
                if time.time() - start_time > file_timeout:
                    logger.warning(f"File scanning timeout for {file_path}. Limiting analysis.")
                    # Truncate findings if needed to prevent processing bottlenecks
                    if file_result and "findings" in file_result and len(file_result["findings"]) > 10:
                        file_result["findings"] = file_result["findings"][:10]
                return file_result if file_result else None
            
            # Fallback to direct file scanning
            try:
                # Read file with timeout and size limit protection
                start_read_time = time.time()
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(self.file_size_limit)  # Limit reading
                    
                    # Check if reading took too long
                    if time.time() - start_read_time > file_timeout / 2:  # Half the timeout for reading
                        logger.warning(f"File reading took too long for {file_path}. Limiting content.")
                        content = content[:100000]  # Limit to first 100K chars
                
                # If file is empty after reading, skip
                if not content.strip():
                    return None
                
                # Detect file type from extension and full path
                file_ext = os.path.splitext(file_path)[1].lower()
                file_base = os.path.basename(file_path).lower()
                
                # Identify PII in the file content
                pii_findings = []
                
                # Use dedicated PII detector if available
                if self.pii_detector:
                    pii_findings = self.pii_detector.detect_pii(content)
                else:
                    # Fallback to built-in PII detection
                    from utils.pii_detection import identify_pii_in_text
                    pii_findings = identify_pii_in_text(content)
                
                # Add file-type specific findings based on extensions and common patterns
                self._add_file_type_findings(pii_findings, file_ext, file_base, content)
                
                # Process findings into a standardized format
                findings = []
                for finding in pii_findings:
                    # Generate representative line number
                    line_number = 1
                    try:
                        if content:
                            lines = content.split('\n')
                            if lines:
                                line_number = min(len(lines) // 2, 50)  # Middle of file
                    except:
                        line_number = 1
                    
                    # Add GDPR-specific attributes with detailed information
                    findings.append({
                        'type': finding.get('pii_type', 'unknown'),
                        'value': finding.get('value', ''),
                        'risk_level': finding.get('risk_level', 'medium'),
                        'line_number': line_number,
                        'gdpr_principle': finding.get('gdpr_principle', 'data_minimization'),
                        'description': self._get_finding_description(finding.get('pii_type', 'unknown')),
                        'recommendation': self._get_finding_recommendation(finding.get('pii_type', 'unknown')),
                        'compliance_score_impact': self._get_score_impact(finding.get('risk_level', 'medium')),
                        'file_name': os.path.basename(file_path),
                        'file_path': os.path.relpath(file_path, repo_path),
                        'code_context': f"// Example potentially problematic code\n// related to {finding.get('pii_type', 'unknown')}"
                    })
                
                return {
                    'file_path': file_path,
                    'findings': findings,
                    'pii_count': len(findings),
                    'gdpr_compliant': len(findings) == 0,
                    'gdpr_principles_affected': list(set(f.get('gdpr_principle', 'data_minimization') for f in findings)),
                    'netherlands_specific_issues': any(f.get('pii_type') in ['BSN', 'MEDICAL_DATA', 'MINOR_CONSENT'] for f in findings)
                }
                
            except Exception as e:
                logger.warning(f"Error reading file {file_path}: {str(e)}")
                return None
                
        except Exception as e:
            logger.warning(f"Error scanning file {file_path}: {str(e)}")
            return None

    def _add_file_type_findings(self, pii_findings: List[Dict[str, Any]], 
                              file_ext: str, file_base: str, content: str):
        """
        Add file-type specific findings based on extensions and content patterns.
        
        Args:
            pii_findings: List to add findings to
            file_ext: File extension
            file_base: Base filename
            content: File content
        """
        # If we already have findings, don't add more for certain files
        if pii_findings and len(pii_findings) >= 3:
            return
            
        # Java files - common in Spring Boot
        if file_ext in ['.java', '.class', '.jar']:
            if 'user' in content.lower() or 'personal' in content.lower():
                pii_findings.append({
                    'pii_type': 'PERSONAL_DATA',
                    'value': 'USER_OBJECT_CONTAINS_PERSONAL_DATA',
                    'risk_level': 'high',
                    'gdpr_principle': 'data_minimization'
                })
            if 'consent' not in content.lower() and ('user' in content.lower() or 'data' in content.lower()):
                pii_findings.append({
                    'pii_type': 'CONSENT_HANDLING',
                    'value': 'MISSING_CONSENT_VALIDATION',
                    'risk_level': 'high',
                    'gdpr_principle': 'lawfulness'
                })
                
        # Configuration files
        elif file_ext in ['.properties', '.yml', '.yaml', '.xml', '.json']:
            if 'password' in content.lower() or 'secret' in content.lower() or 'key' in content.lower():
                pii_findings.append({
                    'pii_type': 'CREDENTIALS',
                    'value': 'HARDCODED_CREDENTIALS',
                    'risk_level': 'high',
                    'gdpr_principle': 'integrity_confidentiality'
                })
            if 'database' in content.lower() or 'db' in content.lower():
                pii_findings.append({
                    'pii_type': 'DATABASE_CREDENTIALS',
                    'value': 'DATABASE_CONNECTION_STRING',
                    'risk_level': 'high',
                    'gdpr_principle': 'integrity_confidentiality'
                })
                
        # Documentation
        elif file_ext in ['.md', '.txt', '.adoc', '.asciidoc', '.html']:
            if '@' in content and '.' in content:
                pii_findings.append({
                    'pii_type': 'EMAIL_ADDRESS',
                    'value': 'DEVELOPER_EMAIL_EXPOSED',
                    'risk_level': 'medium',
                    'gdpr_principle': 'storage_limitation'
                })
            if 'privacy' not in content.lower() and 'policy' not in content.lower():
                pii_findings.append({
                    'pii_type': 'DOCUMENTATION',
                    'value': 'MISSING_PRIVACY_POLICY',
                    'risk_level': 'medium',
                    'gdpr_principle': 'accountability'
                })
                
        # Scripts/Other code
        else:
            if 'api' in content.lower() and 'key' in content.lower():
                pii_findings.append({
                    'pii_type': 'API_KEY',
                    'value': 'HARDCODED_API_KEY',
                    'risk_level': 'high',
                    'gdpr_principle': 'integrity_confidentiality'
                })
            if 'delete' not in content.lower() and ('data' in content.lower() or 'user' in content.lower()):
                pii_findings.append({
                    'pii_type': 'DATA_STORAGE',
                    'value': 'UNLIMITED_DATA_RETENTION',
                    'risk_level': 'medium',
                    'gdpr_principle': 'storage_limitation'
                })

    def _get_finding_description(self, pii_type: str) -> str:
        """
        Get a description for a PII finding.
        
        Args:
            pii_type: The type of PII finding
            
        Returns:
            A description of the finding
        """
        descriptions = {
            'EMAIL_ADDRESS': 'Email addresses are considered personal data under GDPR and must be protected.',
            'PHONE_NUMBER': 'Phone numbers are personal data that could identify individuals.',
            'ADDRESS': 'Physical addresses can directly identify individuals and must be protected.',
            'NAME': 'Names are direct personal identifiers under GDPR.',
            'IP_ADDRESS': 'IP addresses are considered personal data as they can identify individuals.',
            'SSN': 'Social Security Numbers are highly sensitive personal identifiers.',
            'CREDIT_CARD': 'Credit card data is financial information requiring strong protection.',
            'API_KEY': 'API keys could provide access to systems containing personal data.',
            'PASSWORD': 'Passwords should never be stored in plaintext or hardcoded.',
            'PERSONAL_DATA': 'Objects containing personal data require proper handling under GDPR.',
            'CONSENT_HANDLING': 'Explicit consent must be obtained before processing personal data.',
            'DATABASE_CREDENTIALS': 'Database credentials could grant access to personal data stores.',
            'CONFIGURATION': 'Application configuration may contain secrets or personal data.',
            'DOCUMENTATION': 'Documentation should include privacy-related information.',
            'DATA_STORAGE': 'Data storage solutions must implement proper retention policies.',
            'BSN': 'Dutch Citizen Service Numbers (BSN) require special handling under UAVG.',
            'MEDICAL_DATA': 'Medical data requires special safeguards under GDPR.',
            'MINOR_CONSENT': 'Processing data of minors requires parental consent in the Netherlands.',
            'CREDENTIALS': 'Hardcoded credentials present significant security risks.',
            'unknown': 'Potential personal data requiring investigation.'
        }
        
        return descriptions.get(pii_type, 'Potential personal data requiring investigation.')

    def _get_finding_recommendation(self, pii_type: str) -> str:
        """
        Get a recommendation for addressing a PII finding.
        
        Args:
            pii_type: The type of PII finding
            
        Returns:
            A recommendation for addressing the finding
        """
        recommendations = {
            'EMAIL_ADDRESS': 'Implement email anonymization or pseudonymization.',
            'PHONE_NUMBER': 'Apply masking or encryption for phone numbers.',
            'ADDRESS': 'Store addresses in a secured, encrypted database with access controls.',
            'NAME': 'Apply pseudonymization techniques for names when possible.',
            'IP_ADDRESS': 'Implement IP anonymization or use shorter retention periods.',
            'SSN': 'Apply strong encryption and access controls for SSN data.',
            'CREDIT_CARD': 'Use a PCI-compliant payment processor instead of storing card data.',
            'API_KEY': 'Store API keys in secure environment variables or secrets management.',
            'PASSWORD': 'Use secure password hashing and never store in code or config files.',
            'PERSONAL_DATA': 'Implement data minimization and proper validation in user objects.',
            'CONSENT_HANDLING': 'Add explicit consent validation before processing personal data.',
            'DATABASE_CREDENTIALS': 'Move database credentials to secure environment variables.',
            'CONFIGURATION': 'Use secrets management for sensitive application configuration.',
            'DOCUMENTATION': 'Add privacy policy and data handling documentation.',
            'DATA_STORAGE': 'Implement data retention policies with automatic data deletion.',
            'BSN': 'Apply special safeguards for BSN as required by Dutch UAVG regulations.',
            'MEDICAL_DATA': 'Implement enhanced security measures for medical data processing.',
            'MINOR_CONSENT': 'Add age verification and parental consent for users under 16.',
            'CREDENTIALS': 'Move credentials to environment variables or secrets management.',
            'unknown': 'Investigate and classify this data to determine appropriate safeguards.'
        }
        
        return recommendations.get(pii_type, 'Investigate and classify this data to determine appropriate safeguards.')

    def _get_score_impact(self, risk_level: str) -> int:
        """
        Get the impact on compliance score based on risk level.
        
        Args:
            risk_level: Risk level (high, medium, low)
            
        Returns:
            Score impact value
        """
        impacts = {
            'high': -15,
            'medium': -7,
            'low': -3
        }
        
        return impacts.get(risk_level, -5)

    def _calculate_compliance_score(self, summary: Dict[str, Any]) -> int:
        """
        Calculate the overall compliance score based on findings.
        
        Args:
            summary: Summary of findings
            
        Returns:
            Compliance score (0-100)
        """
        base_score = 100
        high_impact = summary.get('high_risk_count', 0) * 15
        medium_impact = summary.get('medium_risk_count', 0) * 7
        low_impact = summary.get('low_risk_count', 0) * 3
        
        # Apply additional impact for affected GDPR principles
        principles_count = len(summary.get('gdpr_principles_affected', []))
        principles_impact = principles_count * 3
        
        # Calculate final score
        score = base_score - (high_impact + medium_impact + low_impact + principles_impact)
        
        # Ensure score stays within valid range
        return max(0, min(100, score))
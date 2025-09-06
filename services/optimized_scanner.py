"""
Optimized Scanner module for scanning large repositories efficiently using multiprocessing.

This module provides a more performant version of the code scanner, 
leveraging parallel processing to handle large repositories with thousands of files.
"""

import os
import re
import time
import json
import hashlib
import logging

# Import centralized logging
try:
    from utils.centralized_logger import get_scanner_logger
    logger = get_scanner_logger("optimized_scanner")
except ImportError:
    # Fallback to standard logging if centralized logger not available
    logger = logging.getLogger(__name__)
import multiprocessing
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class OptimizedScanner:
    """
    An optimized file scanner that uses multiprocessing to efficiently scan large repositories.
    """
    
    def __init__(self, base_scanner, max_workers=None, batch_size=100, chunk_size=10):
        """
        Initialize the optimized scanner with parallel processing capabilities.
        
        Args:
            base_scanner: The base scanner class to use for individual file scanning
            max_workers: Maximum number of worker processes (default: CPU count)
            batch_size: Number of files to process in a batch
            chunk_size: Number of files to assign to a worker at once
        """
        self.base_scanner = base_scanner
        self.max_workers = max_workers or max(1, multiprocessing.cpu_count() - 1)
        self.batch_size = batch_size
        self.chunk_size = chunk_size
        self.start_time = None
        self.progress_callback = None
        
    def set_progress_callback(self, callback_function):
        """
        Set a callback function to report progress during long-running scans.
        
        Args:
            callback_function: Function that takes (current_progress, total_files, current_file_name)
        """
        self.progress_callback = callback_function
        
    def _process_file_batch(self, file_batch, directory_path, max_file_size_mb):
        """
        Process a batch of files in parallel.
        
        Args:
            file_batch: List of files to process
            directory_path: Base directory path
            max_file_size_mb: Maximum file size to scan
            
        Returns:
            List of scan results
        """
        results = []
        
        for file_path, rel_path in file_batch:
            # Check file size
            try:
                file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                if file_size_mb > max_file_size_mb:
                    logger.info(f"Skipping large file: {rel_path} ({file_size_mb:.2f} MB)")
                    results.append({
                        "status": "skipped",
                        "reason": f"File too large ({file_size_mb:.2f} MB)",
                        "file_name": os.path.basename(file_path),
                        "relative_path": rel_path
                    })
                    continue
            except Exception as e:
                logger.warning(f"Error checking file size for {rel_path}: {str(e)}")
                results.append({
                    "status": "error",
                    "error": f"File size check failed: {str(e)}",
                    "file_name": os.path.basename(file_path),
                    "relative_path": rel_path
                })
                continue
                
            # Check file extension
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in self.base_scanner.extensions and not file_ext == '':
                results.append({
                    "status": "skipped",
                    "reason": f"Unsupported file extension: {file_ext}",
                    "file_name": os.path.basename(file_path),
                    "relative_path": rel_path
                })
                continue
                
            # Scan the file
            try:
                scan_result = self.base_scanner._scan_file_with_timeout(file_path)
                scan_result["relative_path"] = rel_path
                results.append(scan_result)
            except Exception as e:
                logger.error(f"Error scanning file {rel_path}: {str(e)}")
                results.append({
                    "status": "error",
                    "error": str(e),
                    "file_name": os.path.basename(file_path),
                    "relative_path": rel_path
                })
                
        return results
    
    def _worker_scan_files(self, files_chunk, directory_path, max_file_size_mb):
        """
        Worker function to scan a chunk of files.
        
        Args:
            files_chunk: List of file paths to scan
            directory_path: Base directory path
            max_file_size_mb: Maximum file size to scan in MB
            
        Returns:
            List of scan results
        """
        results = []
        
        for file_path, rel_path in files_chunk:
            try:
                # Set up a new scanner instance for this process
                scan_result = self._process_file_batch([(file_path, rel_path)], directory_path, max_file_size_mb)[0]
                results.append(scan_result)
            except Exception as e:
                logger.error(f"Worker error scanning {rel_path}: {str(e)}")
                results.append({
                    "status": "error",
                    "error": f"Worker exception: {str(e)}",
                    "file_name": os.path.basename(file_path),
                    "relative_path": rel_path
                })
                
        return results
    
    def scan_directory(self, directory_path: str, progress_callback=None, 
                      ignore_patterns=None, max_file_size_mb=50, 
                      continue_from_checkpoint=False) -> Dict[str, Any]:
        """
        Scan a directory efficiently using parallel processing.
        
        Args:
            directory_path: Path to the directory to scan
            progress_callback: Optional callback to report progress
            ignore_patterns: List of glob patterns to ignore
            max_file_size_mb: Max file size to scan in MB
            continue_from_checkpoint: Whether to continue from last checkpoint if available
            
        Returns:
            Dictionary containing aggregated scan results
        """
        if progress_callback:
            self.progress_callback = progress_callback
            
        # Setup for scan
        self.start_time = datetime.now()
        scan_id = hashlib.md5(f"{directory_path}:{self.start_time.isoformat()}".encode()).hexdigest()[:10]
        
        # Prepare checkpoint file path
        checkpoint_path = f"scan_checkpoint_{scan_id}.json"
        
        # Try to restore from checkpoint if requested
        scan_checkpoint_data = None
        if continue_from_checkpoint and os.path.exists(checkpoint_path):
            try:
                with open(checkpoint_path, 'r') as f:
                    scan_checkpoint_data = json.load(f)
                    completed_files = set(scan_checkpoint_data.get('completed_files', []))
                logger.info(f"Restored scan from checkpoint, {len(completed_files)} files already processed")
            except Exception as e:
                logger.error(f"Failed to load checkpoint: {str(e)}")
        
        if not scan_checkpoint_data:
            # Initialize checkpoint data
            scan_checkpoint_data = {
                'scan_id': scan_id,
                'start_time': self.start_time.isoformat(),
                'directory': directory_path,
                'completed_files': [],
                'findings': [],
                'stats': {'files_scanned': 0, 'files_skipped': 0, 'total_findings': 0}
            }
            completed_files = set()
            
        # Compile ignore patterns
        ignore_regexes = []
        if ignore_patterns:
            for pattern in ignore_patterns:
                # Convert glob pattern to regex
                regex_pattern = pattern.replace('.', '\\.').replace('*', '.*').replace('?', '.?')
                if '/' in pattern:
                    # Path pattern
                    ignore_regexes.append(re.compile(regex_pattern))
                else:
                    # File pattern
                    ignore_regexes.append(re.compile(f".*{regex_pattern}$"))
        
        # Add common patterns to ignore
        default_ignore_patterns = [
            r"\.git/", r"\.svn/", r"node_modules/", r"__pycache__/",
            r"\.venv/", r"env/", r"venv/", r"\.env/", r"\.pytest_cache/",
            r"\.DS_Store$", r"\.pyc$", r"\.pyo$", r"\.pyd$", r"\.so$", r"\.dylib$",
            r"\.jpg$", r"\.jpeg$", r"\.png$", r"\.gif$", r"\.bmp$", r"\.ico$",
            r"\.mp3$", r"\.mp4$", r"\.mov$", r"\.avi$", r"\.wmv$",
            r"\.zip$", r"\.tar$", r"\.gz$", r"\.rar$", r"\.7z$"
        ]
        
        for pattern in default_ignore_patterns:
            ignore_regexes.append(re.compile(pattern))
        
        # Walk directory and get all files
        all_files = []
        logger.info(f"Gathering files from {directory_path}...")
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, directory_path)
                
                # Skip already processed files
                if rel_path in completed_files:
                    continue
                    
                # Check ignore patterns
                skip_file = False
                for regex in ignore_regexes:
                    if regex.match(rel_path) or regex.match(file):
                        skip_file = True
                        break
                
                if not skip_file:
                    all_files.append((file_path, rel_path))
        
        total_files = len(all_files)
        logger.info(f"Found {total_files} files to scan")
        
        if total_files == 0:
            return {
                'scan_id': scan_id,
                'scan_time': self.start_time.isoformat(),
                'completion_time': datetime.now().isoformat(),
                'directory': directory_path,
                'findings': scan_checkpoint_data.get('findings', []),
                'stats': scan_checkpoint_data.get('stats', {'files_scanned': 0, 'files_skipped': 0, 'total_findings': 0})
            }
        
        # Main scanning logic with parallel processing
        all_scan_results = []
        processed_count = 0
        
        # Process files in batches for better progress reporting and checkpointing
        logger.info(f"Starting parallel scan with {self.max_workers} workers")
        
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Split files into chunks for workers
            file_chunks = [all_files[i:i + self.chunk_size] for i in range(0, len(all_files), self.chunk_size)]
            
            # Submit all chunks for processing
            future_to_chunk = {
                executor.submit(self._worker_scan_files, chunk, directory_path, max_file_size_mb): chunk 
                for chunk in file_chunks
            }
            
            # Process results as they complete
            for future in as_completed(future_to_chunk):
                chunk = future_to_chunk[future]
                try:
                    results = future.result()
                    all_scan_results.extend(results)
                    
                    # Update completed files
                    for file_path, rel_path in chunk:
                        scan_checkpoint_data['completed_files'].append(rel_path)
                    
                    # Update processed count
                    processed_count += len(chunk)
                    
                    # Report progress
                    if self.progress_callback:
                        current_file = chunk[-1][1] if chunk else "Unknown"
                        self.progress_callback(processed_count, total_files, current_file)
                    
                    # Periodically save checkpoint (every 50 files)
                    if processed_count % 50 == 0:
                        # Extract findings from scan results
                        for result in results:
                            if result.get('status') == 'success' and 'findings' in result:
                                scan_checkpoint_data['findings'].extend(result['findings'])
                                
                        # Update stats
                        scan_checkpoint_data['stats']['files_scanned'] = processed_count
                        scan_checkpoint_data['stats']['total_findings'] = len(scan_checkpoint_data['findings'])
                        
                        # Save checkpoint
                        with open(checkpoint_path, 'w') as f:
                            json.dump(scan_checkpoint_data, f)
                        
                        logger.info(f"Saved checkpoint after processing {processed_count}/{total_files} files")
                        
                except Exception as e:
                    logger.error(f"Error processing chunk: {str(e)}")
        
        # Final results processing
        findings = []
        stats = {
            'files_scanned': 0,
            'files_skipped': 0,
            'errors': 0,
            'total_findings': 0
        }
        
        for result in all_scan_results:
            if result.get('status') == 'success':
                stats['files_scanned'] += 1
                if 'findings' in result:
                    findings.extend(result['findings'])
            elif result.get('status') == 'skipped':
                stats['files_skipped'] += 1
            elif result.get('status') == 'error':
                stats['errors'] += 1
        
        stats['total_findings'] = len(findings)
        
        # Final checkpoint update
        scan_checkpoint_data['findings'] = findings
        scan_checkpoint_data['stats'] = stats
        
        with open(checkpoint_path, 'w') as f:
            json.dump(scan_checkpoint_data, f)
        
        # Return final results
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        return {
            'scan_id': scan_id,
            'scan_time': self.start_time.isoformat(),
            'completion_time': end_time.isoformat(),
            'duration_seconds': duration,
            'directory': directory_path,
            'findings': findings,
            'stats': stats
        }
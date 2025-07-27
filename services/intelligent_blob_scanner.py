"""
Intelligent Blob Scanner - Scalable Document Processing

Implements smart file selection and parallel processing for document scanning:
- Priority-based file selection (config files, sensitive documents first)
- Parallel OCR processing with timeout protection
- Adaptive sampling for large document collections
- Memory-efficient processing for large files
"""

import os
import tempfile
import shutil
import logging
import concurrent.futures
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
import uuid

logger = logging.getLogger("services.intelligent_blob_scanner")

class IntelligentBlobScanner:
    """Smart blob scanner with scalability optimizations."""
    
    def __init__(self, blob_scanner):
        self.blob_scanner = blob_scanner
        self.MAX_SCAN_TIME = 180  # 3 minutes max
        self.MAX_FILES_DEFAULT = 100
        self.MAX_FILE_SIZE_MB = 50  # Skip files larger than 50MB
        self.PARALLEL_WORKERS = 4
        
        # File priority scoring
        self.FILE_PRIORITIES = {
            # High priority - likely to contain sensitive data
            'config': 3.0,
            'credential': 3.0,
            'secret': 3.0,
            'password': 3.0,
            'key': 3.0,
            'cert': 3.0,
            'invoice': 2.5,
            'contract': 2.5,
            'agreement': 2.5,
            'personal': 2.5,
            'customer': 2.5,
            'user': 2.0,
            'employee': 2.5,
            'medical': 3.0,
            'financial': 2.8,
            'payment': 2.8,
            'bank': 2.8,
            'legal': 2.5,
            'hr': 2.5,
            'report': 2.0,
            'log': 1.5,
            'backup': 1.0,
            'test': 0.8,
            'demo': 0.5,
            'sample': 0.5,
        }
        
        # File type priorities
        self.TYPE_PRIORITIES = {
            '.env': 3.0,
            '.conf': 2.8,
            '.config': 2.8,
            '.ini': 2.5,
            '.properties': 2.5,
            '.pdf': 2.0,
            '.docx': 2.0,
            '.doc': 2.0,
            '.xlsx': 2.0,
            '.csv': 1.8,
            '.json': 1.5,
            '.xml': 1.5,
            '.txt': 1.2,
            '.log': 1.0,
        }

    def scan_documents_intelligent(self, file_paths: List[str], 
                                 scan_mode: str = "smart",
                                 max_files: Optional[int] = None,
                                 progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Intelligent document scanning with adaptive strategies.
        
        Args:
            file_paths: List of file paths to scan
            scan_mode: "fast", "smart", "deep"
            max_files: Maximum files to scan
            progress_callback: Progress reporting callback
            
        Returns:
            Comprehensive scan results
        """
        start_time = time.time()
        scan_id = f"blob_scan_{uuid.uuid4().hex[:8]}"
        
        scan_results = {
            'scan_id': scan_id,
            'scan_type': 'Intelligent Document Scanner',
            'timestamp': datetime.now().isoformat(),
            'region': self.blob_scanner.region,
            'scan_mode': scan_mode,
            'files_analyzed': 0,
            'files_processed': 0,
            'files_skipped': 0,
            'total_files_found': len(file_paths),
            'findings': [],
            'file_types_found': {},
            'processing_strategy': {},
            'status': 'completed'
        }
        
        try:
            # Step 1: Analyze and categorize files
            file_analysis = self._analyze_document_collection(file_paths)
            scan_results['file_types_found'] = file_analysis['file_types']
            
            # Step 2: Select processing strategy
            strategy = self._select_processing_strategy(file_analysis, scan_mode, max_files)
            scan_results['processing_strategy'] = strategy
            
            if progress_callback:
                progress_callback(10, 100, "Files analyzed, selecting documents...")
            
            # Step 3: Select files based on strategy
            files_to_process = self._select_files_intelligent(file_paths, file_analysis, strategy)
            scan_results['files_analyzed'] = len(files_to_process)
            
            # Step 4: Process files in parallel
            findings = self._process_files_parallel(
                files_to_process, scan_results, progress_callback
            )
            
            scan_results['findings'] = findings
            scan_results['duration_seconds'] = time.time() - start_time
            
            # Calculate coverage and success metrics
            scan_results['scan_coverage'] = (
                scan_results['files_processed'] / max(scan_results['total_files_found'], 1) * 100
            )
            
            logger.info(f"Intelligent blob scan completed: {len(findings)} findings in {scan_results['duration_seconds']:.1f}s")
            logger.info(f"Processed {scan_results['files_processed']}/{scan_results['total_files_found']} files ({scan_results['scan_coverage']:.1f}% coverage)")
            
        except Exception as e:
            logger.error(f"Intelligent blob scan failed: {str(e)}")
            scan_results['status'] = 'failed'
            scan_results['error'] = str(e)
        
        return scan_results

    def _analyze_document_collection(self, file_paths: List[str]) -> Dict[str, Any]:
        """Analyze the document collection to determine optimal processing strategy."""
        analysis = {
            'total_files': len(file_paths),
            'file_types': {},
            'size_distribution': [],
            'priority_distribution': {},
            'estimated_processing_time': 0,
            'risk_level': 'low'
        }
        
        priority_counts = {'high': 0, 'medium': 0, 'low': 0}
        
        for file_path in file_paths:
            try:
                # Get file info
                file_size = os.path.getsize(file_path)
                _, ext = os.path.splitext(file_path.lower())
                
                # Track file types
                analysis['file_types'][ext] = analysis['file_types'].get(ext, 0) + 1
                analysis['size_distribution'].append(file_size)
                
                # Calculate priority
                priority_score = self._calculate_file_priority(file_path)
                if priority_score >= 2.5:
                    priority_counts['high'] += 1
                elif priority_score >= 1.5:
                    priority_counts['medium'] += 1
                else:
                    priority_counts['low'] += 1
                
                # Estimate processing time (rough)
                analysis['estimated_processing_time'] += min(file_size / 1024 / 1024, 10)  # Max 10s per file
                
            except Exception as e:
                logger.warning(f"Error analyzing file {file_path}: {str(e)}")
                continue
        
        analysis['priority_distribution'] = priority_counts
        
        # Determine risk level
        risk_score = priority_counts['high'] * 3 + priority_counts['medium'] * 1.5
        if risk_score > 20:
            analysis['risk_level'] = 'high'
        elif risk_score > 10:
            analysis['risk_level'] = 'medium'
        
        return analysis

    def _select_processing_strategy(self, file_analysis: Dict[str, Any], 
                                  scan_mode: str, max_files: Optional[int]) -> Dict[str, Any]:
        """Select optimal processing strategy based on file analysis."""
        
        total_files = file_analysis['total_files']
        estimated_time = file_analysis['estimated_processing_time']
        risk_level = file_analysis['risk_level']
        
        # Determine strategy based on analysis
        if scan_mode == "fast" or total_files <= 20:
            strategy_type = "comprehensive"
            target_files = min(total_files, 25)
            workers = 2
            
        elif scan_mode == "deep" or risk_level == "high":
            strategy_type = "priority_deep"
            target_files = min(max_files or 150, total_files)
            workers = 4
            
        elif estimated_time > self.MAX_SCAN_TIME or total_files > 200:
            strategy_type = "sampling"
            target_files = min(max_files or 75, total_files)
            workers = 4
            
        else:  # smart mode
            if total_files > 100:
                strategy_type = "priority"
                target_files = min(max_files or 100, total_files)
                workers = 3
            else:
                strategy_type = "comprehensive"
                target_files = total_files
                workers = 2
        
        return {
            'type': strategy_type,
            'target_files': target_files,
            'parallel_workers': workers,
            'max_scan_time': self.MAX_SCAN_TIME,
            'reasoning': f"Selected {strategy_type} for {total_files} files with {risk_level} risk"
        }

    def _select_files_intelligent(self, file_paths: List[str], 
                                file_analysis: Dict[str, Any],
                                strategy: Dict[str, Any]) -> List[str]:
        """Select files based on intelligent criteria."""
        
        # Calculate priorities for all files
        file_priorities = []
        for file_path in file_paths:
            try:
                # Skip files that are too large
                file_size = os.path.getsize(file_path)
                if file_size > self.MAX_FILE_SIZE_MB * 1024 * 1024:
                    continue
                
                priority = self._calculate_file_priority(file_path)
                file_priorities.append((file_path, priority, file_size))
                
            except Exception as e:
                logger.warning(f"Error processing file {file_path}: {str(e)}")
                continue
        
        # Sort by priority
        file_priorities.sort(key=lambda x: x[1], reverse=True)
        
        # Select files based on strategy
        target_files = strategy['target_files']
        
        if strategy['type'] == 'sampling':
            # Take top 60% by priority, random sample the rest
            high_priority_count = min(target_files * 60 // 100, len(file_priorities) // 2)
            selected = file_priorities[:high_priority_count]
            
            # Random sample from remaining
            remaining = file_priorities[high_priority_count:]
            if remaining and len(selected) < target_files:
                import random
                sample_size = min(target_files - len(selected), len(remaining))
                selected.extend(random.sample(remaining, sample_size))
                
        else:
            # Take top priority files
            selected = file_priorities[:target_files]
        
        selected_files = [f[0] for f in selected]
        
        logger.info(f"Selected {len(selected_files)} files using {strategy['type']} strategy")
        return selected_files

    def _calculate_file_priority(self, file_path: str) -> float:
        """Calculate priority score for a file."""
        file_path_lower = file_path.lower()
        filename = os.path.basename(file_path_lower)
        _, ext = os.path.splitext(filename)
        
        priority = 1.0  # Base priority
        
        # File name content priority
        for pattern, weight in self.FILE_PRIORITIES.items():
            if pattern in filename or pattern in file_path_lower:
                priority += weight
        
        # File extension priority
        if ext in self.TYPE_PRIORITIES:
            priority += self.TYPE_PRIORITIES[ext]
        
        # Special high-risk patterns
        high_risk_patterns = [
            'password', 'secret', 'key', 'token', 'credential', 'auth',
            'personal', 'medical', 'financial', 'bank', 'invoice',
            'contract', 'agreement', 'ssn', 'bsn', 'passport'
        ]
        
        for pattern in high_risk_patterns:
            if pattern in filename:
                priority += 2.0
        
        # Directory context
        if any(folder in file_path_lower for folder in ['config', 'conf', 'secret', 'private']):
            priority += 1.5
        
        return priority

    def _process_files_parallel(self, files_to_process: List[str], 
                              scan_results: Dict[str, Any],
                              progress_callback: Optional[Callable]) -> List[Dict[str, Any]]:
        """Process files in parallel with progress tracking."""
        
        all_findings = []
        workers = scan_results['processing_strategy']['parallel_workers']
        max_time = scan_results['processing_strategy']['max_scan_time']
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            # Submit all file processing tasks
            future_to_file = {
                executor.submit(self._process_single_file, file_path): file_path
                for file_path in files_to_process
            }
            
            completed = 0
            for future in concurrent.futures.as_completed(future_to_file, timeout=max_time):
                try:
                    # Check timeout
                    if time.time() - start_time > max_time:
                        logger.warning("Parallel document processing timeout reached")
                        break
                    
                    file_path = future_to_file[future]
                    findings = future.result(timeout=30)  # 30 second per file timeout
                    
                    if findings:
                        all_findings.extend(findings)
                    
                    completed += 1
                    scan_results['files_processed'] = completed
                    
                    # Progress callback
                    if progress_callback:
                        progress = 20 + int(70 * completed / len(files_to_process))
                        filename = os.path.basename(file_path)
                        progress_callback(progress, 100, f"Processed {filename}")
                
                except concurrent.futures.TimeoutError:
                    scan_results['files_skipped'] += 1
                    logger.warning(f"File processing timeout: {future_to_file[future]}")
                except Exception as e:
                    scan_results['files_skipped'] += 1
                    logger.warning(f"File processing error: {str(e)}")
        
        return all_findings

    def _process_single_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Process a single file for PII detection."""
        try:
            # Use the existing blob scanner
            result = self.blob_scanner.scan_blob(file_path)
            
            # Extract findings from result
            if isinstance(result, dict) and 'findings' in result:
                return result['findings']
            elif isinstance(result, list):
                return result
            else:
                return []
                
        except Exception as e:
            logger.warning(f"Error processing file {file_path}: {str(e)}")
            return []
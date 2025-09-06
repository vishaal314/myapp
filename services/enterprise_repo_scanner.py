"""
DataGuardian Pro - Enterprise Repository Scanner
Optimized for extremely large repositories (100k+ files)
Includes memory optimization, streaming processing, and enterprise features
"""

import os
import time
import tempfile
import subprocess
import shutil
import mmap
import logging

# Import centralized logging
try:
    from utils.centralized_logger import get_scanner_logger
    logger = get_scanner_logger("enterprise_repo_scanner")
except ImportError:
    # Fallback to standard logging if centralized logger not available
    logger = logging.getLogger(__name__)
import traceback
import uuid
import hashlib
import psutil
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
from pathlib import Path
import fnmatch
import git



class EnterpriseRepoScanner:
    """
    Enterprise-grade repository scanner optimized for massive repositories.
    Handles repositories with 100k+ files efficiently with memory streaming.
    """
    
    def __init__(self, max_workers: Optional[int] = None, memory_limit_gb: int = 4):
        # Optimize based on system resources
        cpu_count = psutil.cpu_count()
        available_memory_gb = psutil.virtual_memory().total / (1024**3)
        
        self.max_workers = max_workers if max_workers is not None else min(cpu_count, 8)
        self.memory_limit_gb = min(memory_limit_gb, available_memory_gb * 0.7)
        self.max_scan_time = 3600  # 1 hour max
        self.file_size_limit = 50 * 1024 * 1024  # 50MB per file
        self.batch_size = 200  # Files per batch
        
        # Repository size thresholds
        self.LARGE_REPO_THRESHOLD = 5000      # 5k files
        self.ULTRA_LARGE_THRESHOLD = 25000    # 25k files  
        self.MASSIVE_REPO_THRESHOLD = 100000  # 100k files
        
        # Sampling strategies for different repo sizes
        self.sampling_limits = {
            'normal': None,           # No limit
            'large': 2000,           # Sample 2k files
            'ultra_large': 1000,     # Sample 1k files
            'massive': 500           # Sample 500 files
        }
        
        logger.info(f"Enterprise scanner initialized: {self.max_workers} workers, "
                   f"{self.memory_limit_gb:.1f}GB memory limit")

    def scan_repository(self, repo_url: str, branch: str = "main", 
                       token: Optional[str] = None,
                       progress_callback: Optional[Callable] = None,
                       scan_level: str = "adaptive") -> Dict[str, Any]:
        """
        Scan repository with enterprise optimizations for massive repos.
        
        Args:
            repo_url: Repository URL
            branch: Branch to scan
            token: Authentication token
            progress_callback: Progress reporting function
            scan_level: 'fast', 'standard', 'thorough', 'adaptive'
            
        Returns:
            Comprehensive scan results with performance metrics
        """
        start_time = time.time()
        memory_start = psutil.virtual_memory().used
        repo_path = None
        
        result = {
            "scan_id": str(uuid.uuid4()),
            "scan_timestamp": datetime.now().isoformat(),
            "repository_url": repo_url,
            "branch": branch,
            "scan_level": scan_level,
            "findings": [],
            "performance_metrics": {
                "total_files": 0,
                "scanned_files": 0,
                "skipped_files": 0,
                "clone_time_seconds": 0,
                "scan_time_seconds": 0,
                "memory_peak_mb": 0,
                "files_per_second": 0
            },
            "summary": {
                "pii_instances": 0,
                "high_risk_count": 0,
                "medium_risk_count": 0,
                "low_risk_count": 0,
                "gdpr_principles_affected": set(),
                "overall_compliance_score": 100,
                "repository_size_category": "unknown"
            },
            "status": "started"
        }
        
        try:
            # Step 1: Intelligent cloning with size detection
            clone_start = time.time()
            repo_path, repo_size_info = self._intelligent_clone(repo_url, branch, token)
            result["performance_metrics"]["clone_time_seconds"] = time.time() - clone_start
            
            # Step 2: Repository analysis and categorization
            total_files = repo_size_info["total_files"]
            repo_category = self._categorize_repository(total_files)
            result["summary"]["repository_size_category"] = repo_category
            result["performance_metrics"]["total_files"] = total_files
            
            logger.info(f"Repository categorized as '{repo_category}' with {total_files:,} files")
            
            # Step 3: Adaptive scan strategy based on repository size
            scan_strategy = self._determine_scan_strategy(repo_category, scan_level)
            
            # Step 4: File collection with intelligent filtering
            all_files = self._collect_files_optimized(repo_path, scan_strategy)
            
            # Step 5: Apply sampling strategy
            files_to_scan = self._apply_enterprise_sampling(
                all_files, repo_category, scan_strategy
            )
            
            result["performance_metrics"]["scanned_files"] = len(files_to_scan)
            result["performance_metrics"]["skipped_files"] = total_files - len(files_to_scan)
            
            # Step 6: Memory-optimized scanning
            scan_start = time.time()
            file_results = self._scan_with_memory_optimization(
                files_to_scan, repo_path, scan_strategy, progress_callback
            )
            result["performance_metrics"]["scan_time_seconds"] = time.time() - scan_start
            
            # Step 7: Results aggregation
            self._aggregate_results(result, file_results)
            
            # Step 8: Performance metrics
            total_time = time.time() - start_time
            memory_peak = (psutil.virtual_memory().used - memory_start) / (1024**2)
            result["performance_metrics"]["memory_peak_mb"] = memory_peak
            result["performance_metrics"]["files_per_second"] = len(files_to_scan) / max(total_time, 1)
            
            result["status"] = "completed"
            logger.info(f"Enterprise scan completed: {len(files_to_scan):,} files in {total_time:.1f}s")
            
        except Exception as e:
            logger.error(f"Enterprise scan failed: {str(e)}")
            result["status"] = "failed"
            result["error"] = str(e)
            
        finally:
            # Cleanup
            if repo_path and os.path.exists(repo_path):
                self._cleanup_repository(repo_path)
                
        return result
    
    def _intelligent_clone(self, repo_url: str, branch: str, token: Optional[str] = None) -> tuple:
        """
        Clone repository with size detection and optimization.
        Uses sparse checkout for massive repositories.
        """
        repo_dir = tempfile.mkdtemp(prefix="enterprise_scan_")
        
        # Step 1: Quick size estimation
        logger.info("Estimating repository size...")
        try:
            # Use git ls-remote to estimate size without cloning
            size_estimate = self._estimate_repo_size(repo_url, token)
            logger.info(f"Estimated repository size: {size_estimate['estimated_files']:,} files")
            
            # Step 2: Choose cloning strategy
            if size_estimate['estimated_files'] > self.MASSIVE_REPO_THRESHOLD:
                logger.info("Using sparse checkout for massive repository")
                repo_path = self._sparse_clone(repo_url, branch, repo_dir, token)
            else:
                logger.info("Using standard shallow clone")
                repo_path = self._shallow_clone(repo_url, branch, repo_dir, token)
                
            # Step 3: Actual file count
            actual_files = self._count_files_fast(repo_path)
            
            return repo_path, {
                "total_files": actual_files,
                "estimated_files": size_estimate['estimated_files'],
                "clone_method": "sparse" if actual_files > self.MASSIVE_REPO_THRESHOLD else "shallow"
            }
            
        except Exception as e:
            shutil.rmtree(repo_dir, ignore_errors=True)
            raise Exception(f"Failed to clone repository: {str(e)}")
    
    def _estimate_repo_size(self, repo_url: str, token: Optional[str] = None) -> Dict[str, int]:
        """Estimate repository size without cloning"""
        try:
            # Use git ls-remote to get basic info
            cmd = ["git", "ls-remote", "--heads", "--tags", repo_url]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Rough estimation based on refs count
            ref_count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
            
            # Heuristic: more refs usually means larger repository
            if ref_count > 100:
                estimated_files = 50000  # Likely massive
            elif ref_count > 20:
                estimated_files = 10000  # Likely large
            else:
                estimated_files = 1000   # Likely normal
                
            return {"estimated_files": estimated_files, "ref_count": ref_count}
            
        except Exception:
            # Conservative estimate if estimation fails
            return {"estimated_files": 5000, "ref_count": 0}
    
    def _sparse_clone(self, repo_url: str, branch: str, repo_dir: str, token: Optional[str] = None) -> str:
        """
        Sparse checkout for massive repositories.
        Only checks out source code files, skips large assets.
        """
        clone_url = self._prepare_auth_url(repo_url, token)
        
        # Initialize repository
        subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True)
        subprocess.run(["git", "remote", "add", "origin", clone_url], cwd=repo_dir, check=True)
        
        # Enable sparse checkout
        subprocess.run(["git", "config", "core.sparseCheckout", "true"], cwd=repo_dir, check=True)
        
        # Define sparse-checkout patterns (focus on source code)
        sparse_patterns = [
            "*.py", "*.js", "*.ts", "*.java", "*.cpp", "*.c", "*.cs", "*.php", "*.rb", "*.go",
            "*.sql", "*.json", "*.yaml", "*.yml", "*.xml", "*.properties", "*.config",
            "*.md", "*.txt", "*.rst", "requirements.txt", "package.json", "Dockerfile",
            "!node_modules/", "!venv/", "!__pycache__/", "!.git/", "!build/", "!dist/"
        ]
        
        sparse_file = os.path.join(repo_dir, ".git", "info", "sparse-checkout")
        with open(sparse_file, "w") as f:
            f.write("\n".join(sparse_patterns))
        
        # Fetch and checkout
        subprocess.run(
            ["git", "fetch", "--depth=1", "origin", branch], 
            cwd=repo_dir, check=True, capture_output=True
        )
        subprocess.run(["git", "checkout", branch], cwd=repo_dir, check=True, capture_output=True)
        
        return repo_dir
    
    def _shallow_clone(self, repo_url: str, branch: str, repo_dir: str, token: Optional[str] = None) -> str:
        """Standard shallow clone for normal/large repositories"""
        clone_url = self._prepare_auth_url(repo_url, token)
        
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", "--branch", branch, clone_url, repo_dir],
                check=True, capture_output=True
            )
        except subprocess.CalledProcessError:
            # Try without branch specification
            subprocess.run(
                ["git", "clone", "--depth", "1", clone_url, repo_dir],
                check=True, capture_output=True
            )
        
        return repo_dir
    
    def _prepare_auth_url(self, repo_url: str, token: Optional[str] = None) -> str:
        """Prepare URL with authentication if token provided"""
        if token and "https://" in repo_url:
            return repo_url.replace("https://", f"https://{token}@")
        return repo_url
    
    def _count_files_fast(self, repo_path: str) -> int:
        """Fast file counting using os.walk with optimization"""
        count = 0
        try:
            for root, dirs, files in os.walk(repo_path):
                # Skip large directories that don't contain source code
                dirs[:] = [d for d in dirs if d not in {
                    '.git', 'node_modules', 'venv', '__pycache__', 'build', 'dist',
                    'target', 'out', 'bin', 'obj', '.idea', '.vscode'
                }]
                count += len(files)
                
                # Break early if we detect it's massive (for categorization)
                if count > self.MASSIVE_REPO_THRESHOLD:
                    break
                    
        except Exception as e:
            logger.warning(f"Error counting files: {e}")
            return 0
            
        return count
    
    def _categorize_repository(self, file_count: int) -> str:
        """Categorize repository size for optimization strategy"""
        if file_count > self.MASSIVE_REPO_THRESHOLD:
            return "massive"
        elif file_count > self.ULTRA_LARGE_THRESHOLD:
            return "ultra_large"
        elif file_count > self.LARGE_REPO_THRESHOLD:
            return "large"
        else:
            return "normal"
    
    def _determine_scan_strategy(self, repo_category: str, scan_level: str) -> Dict[str, Any]:
        """Determine optimal scanning strategy based on repository size and requirements"""
        strategies = {
            "fast": {"parallel_workers": self.max_workers, "file_limit": 100, "memory_conservative": True},
            "standard": {"parallel_workers": self.max_workers // 2, "file_limit": 500, "memory_conservative": False},
            "thorough": {"parallel_workers": 2, "file_limit": 2000, "memory_conservative": False},
            "adaptive": {"parallel_workers": None, "file_limit": None, "memory_conservative": None}
        }
        
        if scan_level == "adaptive":
            # Adaptive strategy based on repository category
            if repo_category == "massive":
                return {"parallel_workers": 2, "file_limit": 200, "memory_conservative": True}
            elif repo_category == "ultra_large":
                return {"parallel_workers": 4, "file_limit": 500, "memory_conservative": True}
            elif repo_category == "large":
                return {"parallel_workers": 6, "file_limit": 1000, "memory_conservative": False}
            else:
                return {"parallel_workers": self.max_workers, "file_limit": None, "memory_conservative": False}
        
        return strategies.get(scan_level, strategies["standard"])
    
    def _collect_files_optimized(self, repo_path: str, scan_strategy: Dict[str, Any]) -> List[str]:
        """Optimized file collection with memory-efficient iteration"""
        files_to_scan = []
        
        # High-priority extensions for GDPR scanning
        priority_extensions = {
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go',
            '.sql', '.json', '.yaml', '.yml', '.xml', '.properties', '.config',
            '.md', '.txt', '.rst', '.log'
        }
        
        exclude_dirs = {
            '.git', 'node_modules', 'venv', '__pycache__', 'build', 'dist',
            'target', 'out', 'bin', 'obj', '.idea', '.vscode', 'vendor'
        }
        
        for root, dirs, files in os.walk(repo_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                # Skip if not priority extension and repository is large
                if scan_strategy.get("memory_conservative") and file_ext not in priority_extensions:
                    continue
                
                # Skip large files
                try:
                    if os.path.getsize(file_path) > self.file_size_limit:
                        continue
                except OSError:
                    continue
                
                files_to_scan.append(file_path)
        
        return files_to_scan
    
    def _apply_enterprise_sampling(self, all_files: List[str], repo_category: str, 
                                 scan_strategy: Dict[str, Any]) -> List[str]:
        """
        Enterprise sampling strategy with intelligent file selection
        """
        file_limit = scan_strategy.get("file_limit") or self.sampling_limits.get(repo_category)
        
        if not file_limit or len(all_files) <= file_limit:
            return all_files
        
        logger.info(f"Applying sampling: {len(all_files):,} -> {file_limit} files")
        
        # Group files by importance and extension
        priority_files = []
        regular_files = []
        
        priority_keywords = [
            'config', 'secret', 'password', 'key', 'auth', 'login', 'user', 'person',
            'customer', 'patient', 'employee', 'admin', 'database', 'db', 'api'
        ]
        
        for file_path in all_files:
            file_name = os.path.basename(file_path).lower()
            file_content_hint = os.path.dirname(file_path).lower()
            
            # Check if file likely contains sensitive data
            is_priority = any(keyword in file_name or keyword in file_content_hint 
                            for keyword in priority_keywords)
            
            if is_priority:
                priority_files.append(file_path)
            else:
                regular_files.append(file_path)
        
        # Sample prioritizing important files
        sampled_files = []
        
        # Take all priority files (up to half the limit)
        priority_limit = file_limit // 2
        sampled_files.extend(priority_files[:priority_limit])
        
        # Fill remaining slots with regular files
        remaining_slots = file_limit - len(sampled_files)
        if remaining_slots > 0 and regular_files:
            # Systematic sampling for better coverage
            step = max(1, len(regular_files) // remaining_slots)
            sampled_files.extend(regular_files[::step][:remaining_slots])
        
        return sampled_files
    
    def _scan_with_memory_optimization(self, files_to_scan: List[str], repo_path: str,
                                     scan_strategy: Dict[str, Any], 
                                     progress_callback: Optional[Callable] = None) -> List[Dict]:
        """
        Memory-optimized scanning with streaming and batch processing
        """
        results = []
        total_files = len(files_to_scan)
        processed = 0
        
        # Determine batch size based on memory constraints
        batch_size = self._calculate_optimal_batch_size(scan_strategy)
        workers = scan_strategy.get("parallel_workers", self.max_workers)
        
        logger.info(f"Starting memory-optimized scan: {workers} workers, batch size {batch_size}")
        
        # Process in batches to control memory usage
        for i in range(0, total_files, batch_size):
            batch = files_to_scan[i:i + batch_size]
            
            # Monitor memory usage
            memory_usage = psutil.virtual_memory().percent
            if memory_usage > 85:  # Reduce workers if memory is high
                workers = max(1, workers // 2)
                logger.warning(f"High memory usage ({memory_usage:.1f}%), reducing workers to {workers}")
            
            # Process batch
            batch_results = self._process_batch(batch, repo_path, workers)
            results.extend(batch_results)
            
            processed += len(batch)
            if progress_callback:
                progress_callback(processed, total_files, f"Processed {processed:,}/{total_files:,} files")
        
        return results
    
    def _calculate_optimal_batch_size(self, scan_strategy: Dict[str, Any]) -> int:
        """Calculate optimal batch size based on available memory"""
        available_memory_mb = psutil.virtual_memory().available / (1024**2)
        
        if scan_strategy.get("memory_conservative"):
            # Conservative: 1MB per file in memory
            return min(self.batch_size, int(available_memory_mb // 4))
        else:
            # Standard: 2MB per file in memory
            return min(self.batch_size, int(available_memory_mb // 8))
    
    def _process_batch(self, batch: List[str], repo_path: str, workers: int) -> List[Dict]:
        """Process a batch of files with error handling"""
        results = []
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_file = {
                executor.submit(self._scan_single_file_optimized, file_path, repo_path): file_path
                for file_path in batch
            }
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result(timeout=30)  # 30s timeout per file
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.warning(f"Error scanning {file_path}: {str(e)}")
        
        return results
    
    def _scan_single_file_optimized(self, file_path: str, repo_path: str) -> Optional[Dict]:
        """
        Optimized single file scanning with memory-mapped I/O for large files
        """
        try:
            file_size = os.path.getsize(file_path)
            relative_path = os.path.relpath(file_path, repo_path)
            
            # Use memory mapping for larger files
            if file_size > 1024 * 1024:  # 1MB
                return self._scan_file_with_mmap(file_path, relative_path)
            else:
                return self._scan_file_standard(file_path, relative_path)
                
        except Exception as e:
            logger.warning(f"Error reading file {file_path}: {str(e)}")
            return None
    
    def _scan_file_with_mmap(self, file_path: str, relative_path: str) -> Optional[Dict]:
        """Scan large file using memory mapping"""
        try:
            with open(file_path, 'rb') as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    # Convert to string for pattern matching
                    content = mm.read().decode('utf-8', errors='ignore')
                    return self._analyze_content(content, relative_path)
        except Exception:
            return None
    
    def _scan_file_standard(self, file_path: str, relative_path: str) -> Optional[Dict]:
        """Standard file scanning for smaller files"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                return self._analyze_content(content, relative_path)
        except Exception:
            return None
    
    def _analyze_content(self, content: str, file_path: str) -> Optional[Dict]:
        """
        Analyze file content for PII and GDPR compliance issues
        """
        findings = []
        
        # Common PII patterns (optimized regex)
        patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'phone': r'\b\d{3}-\d{3}-\d{4}\b',
            'credit_card': r'\b\d{4}-\d{4}-\d{4}-\d{4}\b',
            'api_key': r'[\'\"](sk_|pk_|api_key)[a-zA-Z0-9]{20,}[\'\"]',
            'password': r'[\'\"](password|pwd|pass)[\'\"]\s*[:=]\s*[\'\"]\w+[\'\"]'
        }
        
        for pattern_name, pattern in patterns.items():
            import re
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                findings.append({
                    'type': pattern_name,
                    'file_path': file_path,
                    'instances': len(matches),
                    'risk_level': 'high' if pattern_name in ['ssn', 'credit_card', 'api_key'] else 'medium'
                })
        
        return {'findings': findings} if findings else None
    
    def _aggregate_results(self, result: Dict, file_results: List[Dict]):
        """Aggregate file-level results into repository-level summary"""
        total_findings = 0
        
        for file_result in file_results:
            if file_result and 'findings' in file_result:
                for finding in file_result['findings']:
                    result['findings'].append(finding)
                    total_findings += finding.get('instances', 1)
                    
                    # Update risk counts
                    risk_level = finding.get('risk_level', 'medium')
                    result['summary'][f'{risk_level}_risk_count'] += 1
        
        result['summary']['pii_instances'] = total_findings
        
        # Calculate compliance score
        if total_findings == 0:
            result['summary']['overall_compliance_score'] = 100
        else:
            # Reduce score based on findings
            score_reduction = min(90, total_findings * 5)  # Max 90% reduction
            result['summary']['overall_compliance_score'] = max(10, 100 - score_reduction)
    
    def _cleanup_repository(self, repo_path: str):
        """Clean up cloned repository with error handling"""
        try:
            def handle_readonly(func, path, exc_info):
                os.chmod(path, 0o777)
                func(path)
            
            shutil.rmtree(repo_path, onerror=handle_readonly)
        except Exception as e:
            logger.warning(f"Failed to clean up repository: {e}")

    def get_performance_recommendations(self, result: Dict) -> List[str]:
        """Generate performance recommendations based on scan results"""
        recommendations = []
        metrics = result.get('performance_metrics', {})
        
        files_per_second = metrics.get('files_per_second', 0)
        memory_peak = metrics.get('memory_peak_mb', 0)
        repo_category = result.get('summary', {}).get('repository_size_category', 'unknown')
        
        if files_per_second < 10:
            recommendations.append("Consider using faster storage (SSD) for improved scan performance")
        
        if memory_peak > self.memory_limit_gb * 1024 * 0.8:
            recommendations.append("High memory usage detected - consider increasing memory limit or using more conservative scanning")
        
        if repo_category in ['ultra_large', 'massive']:
            recommendations.append("For repositories this size, consider setting up dedicated scanning infrastructure")
            
        return recommendations
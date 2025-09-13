"""
Repository Metadata Caching System

Implements intelligent caching for repository metadata to improve scan performance
and reduce redundant git operations for repeat scans.
"""

import os
import json
import time
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger("utils.repository_cache")

class RepositoryCache:
    """
    Caching system for repository metadata and scan results.
    Reduces clone operations and improves scan performance for repeat scans.
    """
    
    def __init__(self, cache_dir: str = "/tmp/repo_cache", cache_ttl_hours: int = 24):
        """
        Initialize repository cache.
        
        Args:
            cache_dir: Directory to store cache files
            cache_ttl_hours: Time-to-live for cache entries in hours
        """
        self.cache_dir = Path(cache_dir)
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        
        # Create cache directory if it doesn't exist (with proper error handling)
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            # Fallback to user's home directory if system temp fails
            fallback_dir = Path.home() / ".dataguardian_cache"
            logger.warning(f"Cannot create cache dir {cache_dir}: {e}. Using fallback: {fallback_dir}")
            self.cache_dir = fallback_dir
            try:
                self.cache_dir.mkdir(parents=True, exist_ok=True)
            except Exception as fallback_error:
                logger.error(f"Cannot create fallback cache dir: {fallback_error}. Cache disabled.")
                self.cache_dir = None
        
        # Cache statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'invalidations': 0,
            'total_space_saved_mb': 0
        }
        
        logger.info(f"Repository cache initialized: {cache_dir} (TTL: {cache_ttl_hours}h)")
    
    def _get_repo_hash(self, repo_url: str, branch: Optional[str] = None, directory_path: Optional[str] = None) -> str:
        """Generate unique hash for repository URL, branch, and directory path."""
        # Enhanced cache key that includes directory scope
        cache_key = f"{repo_url}#{branch or 'default'}#{directory_path or 'root'}"
        return hashlib.sha256(cache_key.encode()).hexdigest()[:16]
    
    def _get_cache_path(self, repo_hash: str) -> Optional[Path]:
        """Get cache file path for repository hash."""
        if self.cache_dir is None:
            return None
        return self.cache_dir / f"{repo_hash}.json"
    
    def _is_cache_valid(self, cache_file: Path) -> bool:
        """Check if cache file is still valid (not expired)."""
        if not cache_file.exists():
            return False
        
        try:
            # Check file modification time
            mod_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
            return datetime.now() - mod_time < self.cache_ttl
        except Exception as e:
            logger.warning(f"Error checking cache validity: {e}")
            return False
    
    def get_repository_metadata(self, repo_url: str, branch: Optional[str] = None, directory_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get cached repository metadata.
        
        Args:
            repo_url: Repository URL
            branch: Git branch (optional)
            
        Returns:
            Cached metadata dict or None if not found/expired
        """
        # Return None if cache is disabled
        if self.cache_dir is None:
            self.stats['misses'] += 1
            return None
            
        repo_hash = self._get_repo_hash(repo_url, branch, directory_path)
        cache_file = self._get_cache_path(repo_hash)
        
        try:
            
            if cache_file is None:
                self.stats['misses'] += 1
                return None
            
            if not self._is_cache_valid(cache_file):
                self.stats['misses'] += 1
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            # Validate cached data structure
            if not isinstance(cached_data, dict) or 'metadata' not in cached_data:
                logger.warning(f"Invalid cache data structure in {cache_file}")
                self.stats['misses'] += 1
                return None
            
            self.stats['hits'] += 1
            logger.info(f"Cache HIT for {repo_url} (saved clone operation)")
            
            return cached_data.get('metadata')
            
        except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
            cache_file_str = str(cache_file) if cache_file else "unknown"
            logger.warning(f"Cache file corrupted or missing {cache_file_str}: {e}")
            self.stats['misses'] += 1
            return None
        except Exception as e:
            cache_file_str = str(cache_file) if cache_file else "unknown"
            logger.error(f"Unexpected error reading cache file {cache_file_str}: {e}")
            self.stats['misses'] += 1
            return None
    
    def cache_repository_metadata(self, repo_url: str, metadata: Dict[str, Any], 
                                 branch: Optional[str] = None, directory_path: Optional[str] = None) -> None:
        """
        Cache repository metadata.
        
        Args:
            repo_url: Repository URL
            metadata: Repository metadata to cache
            branch: Git branch (optional)
            directory_path: Directory path within repository (optional)
        """
        repo_hash = self._get_repo_hash(repo_url, branch, directory_path)
        cache_file = self._get_cache_path(repo_hash)
        
        if cache_file is None:
            return
        
        try:
            cache_data = {
                'repo_url': repo_url,
                'branch': branch,
                'directory_path': directory_path,
                'cached_at': datetime.now().isoformat(),
                'metadata': metadata,
                'cache_version': '2.0'  # Updated version for directory support
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            # Estimate space saved (typical git clone is 5-50MB)
            estimated_saved_mb = min(max(metadata.get('total_files', 100) * 0.1, 5), 50)
            self.stats['total_space_saved_mb'] += estimated_saved_mb
            
            logger.info(f"Cached metadata for {repo_url} ({metadata.get('total_files', 0)} files)")
            
        except Exception as e:
            logger.error(f"Error caching metadata for {repo_url}: {e}")
    
    def get_cached_scan_result(self, repo_url: str, scan_mode: str, max_files: int,
                              branch: Optional[str] = None, directory_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get cached scan result for specific parameters.
        
        Args:
            repo_url: Repository URL
            scan_mode: Scan mode used
            max_files: Maximum files scanned
            branch: Git branch
            directory_path: Directory path within repository (optional)
            
        Returns:
            Cached scan result or None
        """
        if self.cache_dir is None:
            return None
            
        repo_hash = self._get_repo_hash(repo_url, branch, directory_path)
        scan_key = f"{scan_mode}_{max_files}_{directory_path or 'root'}"
        cache_file = self.cache_dir / f"{repo_hash}_scan_{hashlib.md5(scan_key.encode()).hexdigest()[:8]}.json"
        
        if not self._is_cache_valid(cache_file):
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cached_scan = json.load(f)
            
            self.stats['hits'] += 1
            logger.info(f"Cache HIT for scan result {repo_url} ({scan_mode})")
            
            return cached_scan.get('scan_result')
            
        except Exception as e:
            logger.warning(f"Error reading scan cache: {e}")
            return None
    
    def cache_scan_result(self, repo_url: str, scan_result: Dict[str, Any], 
                         scan_mode: str, max_files: int, branch: Optional[str] = None, directory_path: Optional[str] = None) -> None:
        """
        Cache complete scan result.
        
        Args:
            repo_url: Repository URL
            scan_result: Complete scan result to cache
            scan_mode: Scan mode used
            max_files: Maximum files scanned
            branch: Git branch
        """
        if self.cache_dir is None:
            return
            
        repo_hash = self._get_repo_hash(repo_url, branch, directory_path)
        scan_key = f"{scan_mode}_{max_files}_{directory_path or 'root'}"
        cache_file = self.cache_dir / f"{repo_hash}_scan_{hashlib.md5(scan_key.encode()).hexdigest()[:8]}.json"
        
        try:
            cache_data = {
                'repo_url': repo_url,
                'branch': branch,
                'directory_path': directory_path,
                'scan_mode': scan_mode,
                'max_files': max_files,
                'cached_at': datetime.now().isoformat(),
                'scan_result': scan_result,
                'cache_version': '2.0'  # Updated version for directory support
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.info(f"Cached scan result for {repo_url} ({len(scan_result.get('findings', []))} findings)")
            
        except Exception as e:
            logger.error(f"Error caching scan result: {e}")
    
    def invalidate_repository(self, repo_url: str, branch: Optional[str] = None) -> None:
        """
        Invalidate all cache entries for a repository.
        
        Args:
            repo_url: Repository URL to invalidate
            branch: Specific branch to invalidate (optional)
        """
        repo_hash = self._get_repo_hash(repo_url, branch)
        
        # Find and remove all cache files for this repository
        pattern = f"{repo_hash}*"
        removed_count = 0
        
        try:
            if self.cache_dir is None:
                return
                
            for cache_file in self.cache_dir.glob(pattern):
                cache_file.unlink()
                removed_count += 1
            
            self.stats['invalidations'] += removed_count
            logger.info(f"Invalidated {removed_count} cache entries for {repo_url}")
            
        except Exception as e:
            logger.error(f"Error invalidating cache for {repo_url}: {e}")
    
    def cleanup_expired_entries(self) -> int:
        """
        Clean up expired cache entries.
        
        Returns:
            Number of entries removed
        """
        removed_count = 0
        
        try:
            if self.cache_dir is None:
                return removed_count
                
            for cache_file in self.cache_dir.glob("*.json"):
                if not self._is_cache_valid(cache_file):
                    cache_file.unlink()
                    removed_count += 1
            
            logger.info(f"Cleaned up {removed_count} expired cache entries")
            
        except Exception as e:
            logger.error(f"Error during cache cleanup: {e}")
        
        return removed_count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        # Calculate cache directory size
        cache_size_mb = 0
        try:
            if self.cache_dir is not None:
                for cache_file in self.cache_dir.glob("*.json"):
                    cache_size_mb += cache_file.stat().st_size / (1024 * 1024)
        except:
            cache_size_mb = 0
        
        return {
            'hit_rate_percent': round(hit_rate, 1),
            'total_hits': self.stats['hits'],
            'total_misses': self.stats['misses'],
            'invalidations': self.stats['invalidations'],
            'cache_size_mb': round(cache_size_mb, 1),
            'estimated_space_saved_mb': round(self.stats['total_space_saved_mb'], 1),
            'cache_directory': str(self.cache_dir)
        }
    
    def clear_all_cache(self) -> int:
        """
        Clear entire cache directory.
        
        Returns:
            Number of files removed
        """
        removed_count = 0
        
        try:
            if self.cache_dir is None:
                return removed_count
                
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
                removed_count += 1
            
            # Reset stats
            self.stats = {
                'hits': 0,
                'misses': 0,
                'invalidations': 0,
                'total_space_saved_mb': 0
            }
            
            logger.info(f"Cleared entire cache: {removed_count} files removed")
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
        
        return removed_count

# Global cache instance
repository_cache = RepositoryCache()
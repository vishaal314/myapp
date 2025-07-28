"""
Redis Caching Layer for DataGuardian Pro
Provides high-performance caching for scan results and user sessions
"""

import redis
import json
import pickle
import logging
import time
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

class RedisCache:
    """High-performance Redis cache manager"""
    
    def __init__(self):
        self.redis_client = None
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0
        }
        self.default_ttl = 3600  # 1 hour
        self.connect()
    
    def connect(self):
        """Connect to Redis server"""
        try:
            # Try to connect to Redis
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            self.redis_client = redis.from_url(redis_url, decode_responses=False)
            
            # Test connection
            self.redis_client.ping()
            logger.info("Redis cache connected successfully")
            
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using in-memory fallback.")
            self.redis_client = None
    
    def _get_key(self, key: str, namespace: str = "dg") -> str:
        """Get namespaced cache key"""
        return f"{namespace}:{key}"
    
    def get(self, key: str, namespace: str = "dg") -> Any:
        """Get value from cache"""
        if not self.redis_client:
            return None
            
        try:
            cache_key = self._get_key(key, namespace)
            value = self.redis_client.get(cache_key)
            
            if value is not None:
                self.stats['hits'] += 1
                # Try JSON first, then pickle
                try:
                    return json.loads(value.decode('utf-8') if isinstance(value, bytes) else str(value))
                except (json.JSONDecodeError, TypeError, UnicodeDecodeError):
                    return pickle.loads(value if isinstance(value, bytes) else str(value).encode())
            else:
                self.stats['misses'] += 1
                return None
                
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            self.stats['errors'] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, namespace: str = "dg") -> bool:
        """Set value in cache"""
        if not self.redis_client:
            return False
            
        try:
            cache_key = self._get_key(key, namespace)
            expiry = ttl or self.default_ttl
            
            # Try JSON first, then pickle
            try:
                serialized_value = json.dumps(value)
            except (TypeError, ValueError):
                serialized_value = pickle.dumps(value)
            
            result = self.redis_client.setex(cache_key, expiry, serialized_value)
            
            if result:
                self.stats['sets'] += 1
                return True
            else:
                self.stats['errors'] += 1
                return False
                
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            self.stats['errors'] += 1
            return False
    
    def delete(self, key: str, namespace: str = "dg") -> bool:
        """Delete value from cache"""
        if not self.redis_client:
            return False
            
        try:
            cache_key = self._get_key(key, namespace)
            result = self.redis_client.delete(cache_key)
            
            if result:
                self.stats['deletes'] += 1
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            self.stats['errors'] += 1
            return False
    
    def exists(self, key: str, namespace: str = "dg") -> bool:
        """Check if key exists in cache"""
        if not self.redis_client:
            return False
            
        try:
            cache_key = self._get_key(key, namespace)
            return bool(self.redis_client.exists(cache_key))
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    def get_or_set(self, key: str, generator_func, ttl: Optional[int] = None, namespace: str = "dg") -> Any:
        """Get value from cache or generate and set it"""
        value = self.get(key, namespace)
        
        if value is None:
            value = generator_func()
            self.set(key, value, ttl, namespace)
        
        return value
    
    def increment(self, key: str, amount: int = 1, namespace: str = "dg") -> Optional[int]:
        """Increment counter in cache"""
        if not self.redis_client:
            return None
            
        try:
            cache_key = self._get_key(key, namespace)
            result = self.redis_client.incr(cache_key, amount)
            return int(result) if result is not None else None
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.redis_client:
            return {**self.stats, 'connected': False}
            
        try:
            info = self.redis_client.info()
            return {
                **self.stats,
                'connected': True,
                'memory_used': info.get('used_memory_human', 'N/A'),
                'total_keys': info.get('db0', {}).get('keys', 0) if 'db0' in info else 0,
                'hit_rate': self.stats['hits'] / (self.stats['hits'] + self.stats['misses']) if (self.stats['hits'] + self.stats['misses']) > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {**self.stats, 'connected': False}
    
    def clear_namespace(self, namespace: str = "dg") -> int:
        """Clear all keys in namespace"""
        if not self.redis_client:
            return 0
            
        try:
            pattern = f"{namespace}:*"
            keys = self.redis_client.keys(pattern)
            
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"Cleared {deleted} keys from namespace {namespace}")
                return deleted
            else:
                return 0
                
        except Exception as e:
            logger.error(f"Error clearing namespace {namespace}: {e}")
            return 0

# Specialized cache managers for DataGuardian Pro

class ScanResultsCache:
    """Cache manager for scan results"""
    
    def __init__(self, redis_cache: RedisCache):
        self.cache = redis_cache
        self.namespace = "scan_results"
        self.ttl = 7200  # 2 hours
    
    def get_scan_result(self, scan_id: str) -> Optional[Dict]:
        """Get scan result from cache"""
        return self.cache.get(f"result:{scan_id}", self.namespace)
    
    def set_scan_result(self, scan_id: str, result: Dict) -> bool:
        """Cache scan result"""
        return self.cache.set(f"result:{scan_id}", result, self.ttl, self.namespace)
    
    def get_user_scans(self, user_id: str) -> Optional[List]:
        """Get user's scan history from cache"""
        return self.cache.get(f"user_scans:{user_id}", self.namespace)
    
    def set_user_scans(self, user_id: str, scans: List) -> bool:
        """Cache user's scan history"""
        return self.cache.set(f"user_scans:{user_id}", scans, self.ttl, self.namespace)
    
    def invalidate_user_scans(self, user_id: str) -> bool:
        """Invalidate user's cached scans"""
        return self.cache.delete(f"user_scans:{user_id}", self.namespace)

class SessionCache:
    """Cache manager for user sessions"""
    
    def __init__(self, redis_cache: RedisCache):
        self.cache = redis_cache
        self.namespace = "sessions"
        self.ttl = 3600  # 1 hour
    
    def get(self, key: str) -> Any:
        """Get value from session cache"""
        return self.cache.get(key, self.namespace)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in session cache"""
        return self.cache.set(key, value, ttl or self.ttl, self.namespace)
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data from cache"""
        return self.cache.get(f"session:{session_id}", self.namespace)
    
    def set_session(self, session_id: str, session_data: Dict) -> bool:
        """Cache session data"""
        return self.cache.set(f"session:{session_id}", session_data, self.ttl, self.namespace)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session from cache"""
        return self.cache.delete(f"session:{session_id}", self.namespace)
    
    def get_user_sessions(self, user_id: str) -> Optional[List]:
        """Get all sessions for a user"""
        return self.cache.get(f"user_sessions:{user_id}", self.namespace)
    
    def track_user_activity(self, user_id: str, activity: str) -> bool:
        """Track user activity"""
        key = f"activity:{user_id}"
        activities = self.cache.get(key, self.namespace) or []
        
        activities.append({
            'activity': activity,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 100 activities
        if len(activities) > 100:
            activities = activities[-100:]
        
        return self.cache.set(key, activities, self.ttl * 24, self.namespace)  # 24 hours

class PerformanceCache:
    """Cache manager for performance metrics"""
    
    def __init__(self, redis_cache: RedisCache):
        self.cache = redis_cache
        self.namespace = "performance"
        self.ttl = 300  # 5 minutes
    
    def get_system_metrics(self) -> Optional[Dict]:
        """Get cached system metrics"""
        return self.cache.get("system_metrics", self.namespace)
    
    def set_system_metrics(self, metrics: Dict) -> bool:
        """Cache system metrics"""
        return self.cache.set("system_metrics", metrics, self.ttl, self.namespace)
    
    def get_scanner_stats(self, scanner_type: str) -> Optional[Dict]:
        """Get scanner performance stats"""
        return self.cache.get(f"scanner_stats:{scanner_type}", self.namespace)
    
    def set_scanner_stats(self, scanner_type: str, stats: Dict) -> bool:
        """Cache scanner performance stats"""
        return self.cache.set(f"scanner_stats:{scanner_type}", stats, self.ttl, self.namespace)
    
    def increment_scan_counter(self, scanner_type: str) -> Optional[int]:
        """Increment scan counter for analytics"""
        return self.cache.increment(f"scan_count:{scanner_type}", 1, self.namespace)

# Global cache instances
redis_cache = RedisCache()
scan_cache = ScanResultsCache(redis_cache)
session_cache = SessionCache(redis_cache)
performance_cache = PerformanceCache(redis_cache)

def get_cache():
    """Get the main Redis cache instance"""
    return redis_cache

def get_scan_cache():
    """Get the scan results cache"""
    return scan_cache

def get_session_cache():
    """Get the session cache"""
    return session_cache

def get_performance_cache():
    """Get the performance cache"""
    return performance_cache
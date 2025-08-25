"""
PostgreSQL Database Optimization Module
Optimizes database performance for DataGuardian Pro
"""

import os
import psycopg2
import psycopg2.pool as pool  # Fix import structure
from psycopg2.extras import RealDictCursor
import logging
import time
from contextlib import contextmanager
from typing import Dict, Any, Optional
import threading

logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    """Optimized database connection manager with performance tuning"""
    
    def __init__(self):
        self.connection_pool = None
        self.pool_lock = threading.Lock()
        self.stats = {
            'total_connections': 0,
            'active_connections': 0,
            'total_queries': 0,
            'slow_queries': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'avg_query_time': 0.0
        }
        self.query_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
    def initialize_optimized_pool(self):
        """Initialize connection pool with optimized settings"""
        try:
            # Optimized connection parameters
            conn_params = {
                'host': os.getenv('PGHOST', 'localhost'),
                'database': os.getenv('PGDATABASE', 'dataguardian'),
                'user': os.getenv('PGUSER', 'postgres'),
                'password': os.getenv('PGPASSWORD', ''),
                'port': os.getenv('PGPORT', '5432'),
                # Performance optimizations
                'options': '-c default_transaction_isolation=read_committed '
                          '-c statement_timeout=30000 '
                          '-c lock_timeout=10000 '
                          '-c idle_in_transaction_session_timeout=300000'
            }
            
            self.connection_pool = pool.ThreadedConnectionPool(
                minconn=10,    # Increased minimum connections
                maxconn=50,    # Increased maximum connections
                **conn_params
            )
            
            # Apply database-level optimizations
            self._apply_database_optimizations()
            
            logger.info("Optimized database connection pool initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize optimized connection pool: {e}")
            raise
    
    def _apply_database_optimizations(self):
        """Apply PostgreSQL performance optimizations"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Performance optimization queries
                optimizations = [
                    # Memory settings
                    "SET shared_buffers = '256MB'",
                    "SET effective_cache_size = '1GB'",
                    "SET work_mem = '16MB'",
                    "SET maintenance_work_mem = '64MB'",
                    
                    # Checkpoint settings
                    "SET checkpoint_completion_target = 0.9",
                    "SET wal_buffers = '16MB'",
                    
                    # Query planner settings
                    "SET random_page_cost = 1.1",
                    "SET effective_io_concurrency = 200",
                    
                    # Connection settings
                    "SET max_connections = 100",
                    
                    # Logging settings for monitoring
                    "SET log_min_duration_statement = 1000",  # Log slow queries
                    "SET log_statement = 'mod'",
                ]
                
                for optimization in optimizations:
                    try:
                        cursor.execute(optimization)
                        conn.commit()
                    except Exception as e:
                        logger.warning(f"Could not apply optimization '{optimization}': {e}")
                        conn.rollback()
                
                # Create indexes for common queries
                self._create_performance_indexes(cursor, conn)
                
        except Exception as e:
            logger.error(f"Failed to apply database optimizations: {e}")
    
    def _create_performance_indexes(self, cursor, conn):
        """Create indexes for common DataGuardian Pro queries"""
        indexes = [
            # Scan results indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scan_results_user_id ON scan_results(user_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scan_results_created_at ON scan_results(created_at DESC)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scan_results_scan_type ON scan_results(scan_type)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scan_results_status ON scan_results(status)",
            
            # User activity indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_activity_timestamp ON user_activity(timestamp DESC)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_activity_user_id ON user_activity(user_id)",
            
            # Findings indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_findings_scan_id ON findings(scan_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_findings_severity ON findings(severity)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_findings_type ON findings(finding_type)",
            
            # Payment indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_payments_user_id ON payments(user_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_payments_status ON payments(status)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_payments_created_at ON payments(created_at DESC)",
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                conn.commit()
                logger.info(f"Created index: {index_sql.split('IF NOT EXISTS')[1].split('ON')[0].strip()}")
            except Exception as e:
                logger.warning(f"Could not create index: {e}")
                conn.rollback()
    
    @contextmanager
    def get_connection(self):
        """Get optimized database connection from pool"""
        conn = None
        start_time = time.time()
        
        try:
            with self.pool_lock:
                if not self.connection_pool:
                    self.initialize_optimized_pool()
                
                # Type-safe connection pool access
                if self.connection_pool is not None:
                    conn = self.connection_pool.getconn()
                else:
                    raise Exception("Connection pool not initialized")
                self.stats['active_connections'] += 1
                self.stats['total_connections'] += 1
            
            yield conn
            
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn and self.connection_pool is not None:
                with self.pool_lock:
                    self.connection_pool.putconn(conn)
                    self.stats['active_connections'] -= 1
                
                # Update query time statistics
                query_time = time.time() - start_time
                self.stats['avg_query_time'] = (
                    (self.stats['avg_query_time'] * self.stats['total_queries'] + query_time) / 
                    (self.stats['total_queries'] + 1)
                )
                self.stats['total_queries'] += 1
    
    def execute_cached_query(self, query: str, params: Optional[tuple] = None, cache_key: Optional[str] = None) -> Any:
        """Execute query with caching for better performance"""
        if cache_key:
            # Check cache first
            cached_result = self.query_cache.get(cache_key)
            if cached_result and time.time() - cached_result['timestamp'] < self.cache_ttl:
                self.stats['cache_hits'] += 1
                return cached_result['data']
            
            self.stats['cache_misses'] += 1
        
        # Execute query
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            start_time = time.time()
            cursor.execute(query, params)
            execution_time = time.time() - start_time
            
            if execution_time > 1.0:  # Log slow queries
                self.stats['slow_queries'] += 1
                logger.warning(f"Slow query detected ({execution_time:.2f}s): {query[:100]}...")
            
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                
                # Cache the result
                if cache_key:
                    self.query_cache[cache_key] = {
                        'data': result,
                        'timestamp': time.time()
                    }
                
                return result
            else:
                conn.commit()
                return cursor.rowcount
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get database performance statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get database statistics
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    attname,
                    n_distinct,
                    correlation
                FROM pg_stats 
                WHERE schemaname = 'public' 
                ORDER BY tablename, attname;
            """)
            table_stats = cursor.fetchall()
            
            # Get connection statistics
            cursor.execute("""
                SELECT 
                    count(*) as total_connections,
                    count(*) FILTER (WHERE state = 'active') as active_connections,
                    count(*) FILTER (WHERE state = 'idle') as idle_connections
                FROM pg_stat_activity 
                WHERE datname = current_database();
            """)
            conn_stats = cursor.fetchone()
            
            # Get query statistics
            cursor.execute("""
                SELECT 
                    query,
                    calls,
                    total_time,
                    mean_time,
                    rows
                FROM pg_stat_statements 
                ORDER BY total_time DESC 
                LIMIT 10;
            """)
            query_stats = cursor.fetchall()
            
            return {
                'pool_stats': self.stats,
                'connection_stats': dict(conn_stats) if conn_stats else {},
                'table_stats': [dict(row) for row in table_stats],
                'top_queries': [dict(row) for row in query_stats],
                'cache_size': len(self.query_cache)
            }
    
    def cleanup_cache(self):
        """Clean up expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, value in self.query_cache.items()
            if current_time - value['timestamp'] > self.cache_ttl
        ]
        
        for key in expired_keys:
            del self.query_cache[key]
        
        logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

# Global instance
db_optimizer = DatabaseOptimizer()

def get_optimized_db():
    """Get the optimized database instance"""
    return db_optimizer
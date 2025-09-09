"""
Database Manager with Connection Pooling

Handles all database operations with proper connection pooling
and error handling for the Simple DPIA application.
"""

import psycopg2
import psycopg2.pool
import os
import json
from datetime import datetime
import streamlit as st
from contextlib import contextmanager

class DatabaseManager:
    _instance = None
    _connection_pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._connection_pool is None:
            self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize database connection pool with optimized settings"""
        try:
            DATABASE_URL = os.environ.get('DATABASE_URL')
            if not DATABASE_URL:
                st.error("Database URL not configured")
                return
            
            # Dynamic connection pool sizing based on system resources
            import psutil
            cpu_count = psutil.cpu_count(logical=True)
            # Scale connections: minimum 8, maximum 35, optimal ~2x CPU cores + some overhead
            min_connections = max(8, cpu_count)
            max_connections = min(35, cpu_count * 2 + 10)
            
            # Create connection pool with optimized settings
            self._connection_pool = psycopg2.pool.ThreadedConnectionPool(
                min_connections, max_connections, DATABASE_URL,
                # Connection optimization parameters
                application_name="DataGuardian_Pro",
                connect_timeout=10,
                # Keep connections alive to reduce overhead
                keepalives_idle=600,  # 10 minutes
                keepalives_interval=30,  # 30 seconds
                keepalives_count=3
            )
            self.min_connections = min_connections
            self.max_connections = max_connections
            
            # Create tables on initialization
            self._create_tables()
            
            # Pre-warm connection pool for better performance
            self._prewarm_connections()
            
        except Exception as e:
            st.error(f"Failed to initialize database pool: {str(e)}")
    
    def _prewarm_connections(self):
        """Pre-warm database connections to reduce initial latency"""
        try:
            # Create and immediately return connections to establish them
            connections = []
            for _ in range(min(5, self.min_connections)):
                try:
                    conn = self._connection_pool.getconn()
                    if conn:
                        # Test connection with a simple query
                        with conn.cursor() as cursor:
                            cursor.execute("SELECT 1")
                        connections.append(conn)
                except Exception:
                    pass
            
            # Return all connections to the pool
            for conn in connections:
                self._connection_pool.putconn(conn)
                
        except Exception:
            # Pre-warming is optional, don't fail if it doesn't work
            pass
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections with retry logic"""
        conn = None
        max_retries = 3
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                if self._connection_pool:
                    conn = self._connection_pool.getconn()
                    yield conn
                    break
            except psycopg2.pool.PoolError as e:
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                else:
                    raise Exception(f"Connection pool exhausted after {max_retries} attempts")
            except Exception as e:
                if conn:
                    conn.rollback()
                raise e
            finally:
                if conn and self._connection_pool:
                    try:
                        self._connection_pool.putconn(conn)
                    except Exception:
                        pass  # Connection already returned or closed
    
    def _create_tables(self):
        """Create necessary database tables"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS simple_dpia_assessments (
                        id SERIAL PRIMARY KEY,
                        assessment_id VARCHAR(255) UNIQUE,
                        project_name VARCHAR(255),
                        organization VARCHAR(255),
                        created_date TIMESTAMP,
                        assessment_data JSONB,
                        risk_score INTEGER,
                        risk_level VARCHAR(50),
                        compliance_status VARCHAR(100),
                        updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create index for faster queries
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_assessment_id 
                    ON simple_dpia_assessments(assessment_id)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_created_date 
                    ON simple_dpia_assessments(created_date)
                """)
                
                conn.commit()
                cursor.close()
                
        except Exception as e:
            st.error(f"Error creating tables: {str(e)}")
    
    def save_assessment(self, assessment_data):
        """Save assessment to database with proper error handling"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO simple_dpia_assessments 
                    (assessment_id, project_name, organization, created_date, 
                     assessment_data, risk_score, risk_level, compliance_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (assessment_id) DO UPDATE SET
                        assessment_data = EXCLUDED.assessment_data,
                        risk_score = EXCLUDED.risk_score,
                        risk_level = EXCLUDED.risk_level,
                        compliance_status = EXCLUDED.compliance_status,
                        updated_date = CURRENT_TIMESTAMP
                """, (
                    assessment_data.get('assessment_id'),
                    assessment_data.get('project_name', 'Unknown'),
                    assessment_data.get('organization', 'Unknown'),
                    datetime.now(),
                    json.dumps(assessment_data),
                    assessment_data.get('risk_score', 0),
                    assessment_data.get('risk_level', 'Unknown'),
                    assessment_data.get('compliance_status', 'Pending')
                ))
                
                conn.commit()
                cursor.close()
                return True
                
        except Exception as e:
            st.error(f"Database save error: {str(e)}")
            return False
    
    def get_assessment(self, assessment_id):
        """Retrieve assessment by ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM simple_dpia_assessments 
                    WHERE assessment_id = %s
                """, (assessment_id,))
                
                result = cursor.fetchone()
                cursor.close()
                
                if result:
                    return {
                        'id': result[0],
                        'assessment_id': result[1],
                        'project_name': result[2],
                        'organization': result[3],
                        'created_date': result[4],
                        'assessment_data': result[5],
                        'risk_score': result[6],
                        'risk_level': result[7],
                        'compliance_status': result[8]
                    }
                return None
                
        except Exception as e:
            st.error(f"Database retrieval error: {str(e)}")
            return None
    
    def get_recent_assessments(self, limit=10):
        """Get recent assessments for history view"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT assessment_id, project_name, organization, 
                           created_date, risk_level, compliance_status
                    FROM simple_dpia_assessments 
                    ORDER BY created_date DESC 
                    LIMIT %s
                """, (limit,))
                
                results = cursor.fetchall()
                cursor.close()
                
                return [{
                    'assessment_id': row[0],
                    'project_name': row[1],
                    'organization': row[2],
                    'created_date': row[3],
                    'risk_level': row[4],
                    'compliance_status': row[5]
                } for row in results]
                
        except Exception as e:
            st.error(f"Database query error: {str(e)}")
            return []
    
    def execute_query(self, query: str, params: tuple = None) -> bool:
        """Execute a query (INSERT, UPDATE, DELETE) and return success status"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                conn.commit()
                cursor.close()
                return True
        except Exception as e:
            logger.error(f"Execute query error: {str(e)}")
            return False
    
    def fetch_query(self, query: str, params: tuple = None) -> list:
        """Execute a SELECT query and return results"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                results = cursor.fetchall()
                cursor.close()
                return results
        except Exception as e:
            logger.error(f"Fetch query error: {str(e)}")
            return []

# Singleton instance
db_manager = DatabaseManager()
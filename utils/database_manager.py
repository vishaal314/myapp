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
        """Initialize database connection pool"""
        try:
            DATABASE_URL = os.environ.get('DATABASE_URL')
            if not DATABASE_URL:
                st.error("Database URL not configured")
                return
            
            # Create connection pool with 2-10 connections
            self._connection_pool = psycopg2.pool.SimpleConnectionPool(
                2, 10, DATABASE_URL
            )
            
            # Create tables on initialization
            self._create_tables()
            
        except Exception as e:
            st.error(f"Failed to initialize database pool: {str(e)}")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            if self._connection_pool:
                conn = self._connection_pool.getconn()
                yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn and self._connection_pool:
                self._connection_pool.putconn(conn)
    
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

# Singleton instance
db_manager = DatabaseManager()
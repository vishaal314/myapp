"""
Base Repository Pattern Implementation

Provides a foundation for enterprise feature data persistence using the existing
database optimizer infrastructure. Includes encryption for sensitive fields
and comprehensive error handling.
"""

import logging
import uuid
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from contextlib import contextmanager

try:
    from utils.database_optimizer import get_optimized_db
    DB_AVAILABLE = True
except ImportError:
    get_optimized_db = None
    DB_AVAILABLE = False
from utils.centralized_logger import get_scanner_logger

logger = get_scanner_logger("base_repository")

class EncryptionHelper:
    """
    Helper class for field-level hashing of sensitive data
    
    NOTE: This is a demo implementation using secure hashing, not reversible encryption.
    In production, use proper symmetric encryption (AES-GCM, Fernet) with KMS.
    """
    
    @staticmethod
    def encrypt_field(value: str, field_name: str = "data") -> str:
        """
        Hash sensitive field data (DEMO - not reversible encryption)
        
        Args:
            value: The value to hash
            field_name: Field name for salt generation
            
        Returns:
            Hashed value with prefix
        """
        try:
            # Secure hash for demo - in production use reversible encryption with KMS
            salt = hashlib.sha256(field_name.encode()).hexdigest()[:16]
            combined = f"{salt}{value}"
            hashed = hashlib.sha256(combined.encode()).hexdigest()
            return f"hash:{hashed}"
        except Exception as e:
            logger.error(f"Field hashing failed for {field_name}: {e}")
            return f"hash:error_{field_name}"
    
    @staticmethod
    def decrypt_field(hashed_value: str, field_name: str = "data") -> str:
        """
        Return placeholder for hashed data (DEMO - cannot decrypt hashes)
        
        Args:
            hashed_value: The hashed value
            field_name: Field name for reference
            
        Returns:
            Placeholder indicating data is hashed
        """
        if not hashed_value.startswith("hash:"):
            return hashed_value
            
        # Demo mode - hashes cannot be reversed
        logger.debug(f"Hash reversal requested for {field_name} (not possible)")
        return f"[HASHED_{field_name.upper()}]"
    
    @staticmethod
    def hash_for_lookup(value: str) -> str:
        """Create searchable hash for encrypted fields"""
        return hashlib.sha256(value.encode()).hexdigest()[:32]

class BaseRepository:
    """
    Base repository providing common database operations with encryption support
    
    Leverages existing database optimizer infrastructure while adding
    enterprise-specific features like field encryption and audit trails.
    """
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.db = get_optimized_db() if DB_AVAILABLE else None
        self.encryption = EncryptionHelper()
        
        # Fields that should be encrypted
        self.sensitive_fields = set()
        
        # Fields that should have content hashes for integrity
        self.integrity_fields = set()
        
        logger.debug(f"Initialized {self.__class__.__name__} for table {table_name}")
    
    def add_sensitive_field(self, field_name: str) -> None:
        """Mark a field as sensitive (will be encrypted)"""
        self.sensitive_fields.add(field_name)
    
    def add_integrity_field(self, field_name: str) -> None:
        """Mark a field as requiring integrity checking (will be hashed)"""
        self.integrity_fields.add(field_name)
    
    def _prepare_data_for_storage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for storage by encrypting sensitive fields"""
        prepared = data.copy()
        
        # Encrypt sensitive fields
        for field in self.sensitive_fields:
            if field in prepared and prepared[field] is not None:
                original_value = str(prepared[field])
                prepared[field] = self.encryption.encrypt_field(original_value, field)
                logger.debug(f"Encrypted field: {field}")
        
        # Add integrity hashes
        for field in self.integrity_fields:
            if field in prepared and prepared[field] is not None:
                hash_field = f"{field}_hash"
                prepared[hash_field] = hashlib.sha256(str(prepared[field]).encode()).hexdigest()
        
        # Add metadata
        prepared['created_at'] = prepared.get('created_at', datetime.now().isoformat())
        prepared['updated_at'] = datetime.now().isoformat()
        
        return prepared
    
    def _prepare_data_from_storage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data from storage by decrypting sensitive fields"""
        if not data:
            return data
            
        prepared = data.copy()
        
        # Process hashed fields (demo mode - show placeholders)
        for field in self.sensitive_fields:
            if field in prepared and prepared[field] and str(prepared[field]).startswith("hash:"):
                prepared[field] = self.encryption.decrypt_field(prepared[field], field)
        
        return prepared
    
    @contextmanager
    def get_connection(self):
        """Get database connection from optimizer"""
        if not self.db:
            raise RuntimeError("Database not available - install psycopg2 and configure DATABASE_URL")
            
        conn = None
        try:
            conn = self.db.get_connection()
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            if conn:
                self.db.return_connection(conn)
    
    def create(self, data: Dict[str, Any]) -> str:
        """
        Create a new record
        
        Args:
            data: Record data
            
        Returns:
            Generated record ID
        """
        try:
            # Generate ID if not provided
            record_id = data.get('id', str(uuid.uuid4()))
            data['id'] = record_id
            
            # Prepare data for storage
            prepared_data = self._prepare_data_for_storage(data)
            
            # Build insert query
            fields = list(prepared_data.keys())
            placeholders = ', '.join(['%s'] * len(fields))
            field_names = ', '.join(fields)
            
            query = f"""
                INSERT INTO {self.table_name} ({field_names})
                VALUES ({placeholders})
            """
            
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, list(prepared_data.values()))
                    
            logger.info(f"Created record {record_id} in {self.table_name}")
            return record_id
            
        except Exception as e:
            logger.error(f"Failed to create record in {self.table_name}: {e}")
            raise
    
    def get_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        """
        Get record by ID
        
        Args:
            record_id: Record identifier
            
        Returns:
            Record data or None if not found
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE id = %s"
            
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (record_id,))
                    result = cursor.fetchone()
                    
                    if result:
                        # Convert to dict if using RealDictCursor
                        if hasattr(result, '_asdict'):
                            record = dict(result._asdict())
                        else:
                            # Get column names
                            columns = [desc[0] for desc in cursor.description]
                            record = dict(zip(columns, result))
                        
                        return self._prepare_data_from_storage(record)
                    
            return None
            
        except Exception as e:
            logger.error(f"Failed to get record {record_id} from {self.table_name}: {e}")
            raise
    
    def update(self, record_id: str, data: Dict[str, Any]) -> bool:
        """
        Update existing record
        
        Args:
            record_id: Record identifier
            data: Updated data
            
        Returns:
            True if updated successfully
        """
        try:
            # Prepare data for storage
            prepared_data = self._prepare_data_for_storage(data)
            
            # Remove ID from update data
            prepared_data.pop('id', None)
            
            if not prepared_data:
                return True
            
            # Build update query
            set_clauses = [f"{field} = %s" for field in prepared_data.keys()]
            set_clause = ', '.join(set_clauses)
            
            query = f"""
                UPDATE {self.table_name}
                SET {set_clause}
                WHERE id = %s
            """
            
            values = list(prepared_data.values()) + [record_id]
            
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, values)
                    updated = cursor.rowcount > 0
                    
            if updated:
                logger.info(f"Updated record {record_id} in {self.table_name}")
            else:
                logger.warning(f"No record found to update: {record_id}")
                
            return updated
            
        except Exception as e:
            logger.error(f"Failed to update record {record_id} in {self.table_name}: {e}")
            raise
    
    def delete(self, record_id: str) -> bool:
        """
        Delete record by ID
        
        Args:
            record_id: Record identifier
            
        Returns:
            True if deleted successfully
        """
        try:
            query = f"DELETE FROM {self.table_name} WHERE id = %s"
            
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (record_id,))
                    deleted = cursor.rowcount > 0
                    
            if deleted:
                logger.info(f"Deleted record {record_id} from {self.table_name}")
            else:
                logger.warning(f"No record found to delete: {record_id}")
                
            return deleted
            
        except Exception as e:
            logger.error(f"Failed to delete record {record_id} from {self.table_name}: {e}")
            raise
    
    def find_by_criteria(self, criteria: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """
        Find records matching criteria
        
        Args:
            criteria: Search criteria
            limit: Maximum records to return
            
        Returns:
            List of matching records
        """
        try:
            if not criteria:
                return []
            
            # Build where clause
            where_clauses = []
            values = []
            
            for field, value in criteria.items():
                if value is not None:
                    where_clauses.append(f"{field} = %s")
                    values.append(value)
            
            if not where_clauses:
                return []
            
            where_clause = ' AND '.join(where_clauses)
            query = f"""
                SELECT * FROM {self.table_name}
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT %s
            """
            values.append(limit)
            
            records = []
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, values)
                    results = cursor.fetchall()
                    
                    for result in results:
                        if hasattr(result, '_asdict'):
                            record = dict(result._asdict())
                        else:
                            columns = [desc[0] for desc in cursor.description]
                            record = dict(zip(columns, result))
                        
                        records.append(self._prepare_data_from_storage(record))
            
            return records
            
        except Exception as e:
            logger.error(f"Failed to find records in {self.table_name}: {e}")
            raise
    
    def count_by_criteria(self, criteria: Dict[str, Any]) -> int:
        """
        Count records matching criteria
        
        Args:
            criteria: Search criteria
            
        Returns:
            Number of matching records
        """
        try:
            if not criteria:
                return 0
            
            # Build where clause
            where_clauses = []
            values = []
            
            for field, value in criteria.items():
                if value is not None:
                    where_clauses.append(f"{field} = %s")
                    values.append(value)
            
            if not where_clauses:
                return 0
            
            where_clause = ' AND '.join(where_clauses)
            query = f"SELECT COUNT(*) FROM {self.table_name} WHERE {where_clause}"
            
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, values)
                    count = cursor.fetchone()[0]
                    return count
            
        except Exception as e:
            logger.error(f"Failed to count records in {self.table_name}: {e}")
            raise
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get repository health status"""
        try:
            count = self.count_by_criteria({})
            return {
                'table_name': self.table_name,
                'total_records': count,
                'status': 'healthy',
                'last_check': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'table_name': self.table_name,
                'status': 'error',
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
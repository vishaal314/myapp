import os
import json
import uuid
import psycopg2
from psycopg2.extras import Json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

class ResultsAggregator:
    """
    Aggregates and stores scan results in a PostgreSQL database.
    """
    
    def __init__(self, db_url: str = None):
        """
        Initialize the results aggregator.
        
        Args:
            db_url: PostgreSQL database URL. If None, uses DATABASE_URL environment variable.
        """
        self.db_url = db_url or os.environ.get('DATABASE_URL')
        self._init_db()
    
    def _get_connection(self):
        """Get a database connection."""
        return psycopg2.connect(self.db_url, sslmode='prefer')
    
    def _init_db(self):
        """Initialize the database with required tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Create scans table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            scan_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            scan_type TEXT NOT NULL,
            region TEXT NOT NULL,
            file_count INTEGER NOT NULL,
            total_pii_found INTEGER NOT NULL,
            high_risk_count INTEGER NOT NULL,
            result_json JSONB NOT NULL
        )
        ''')
        
        # Create audit log table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            log_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            action TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            details JSONB
        )
        ''')
        
        # Create PII types reference table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pii_types (
            type_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            risk_level TEXT NOT NULL,
            category TEXT,
            requires_consent BOOLEAN NOT NULL
        )
        ''')
        
        # Create data purpose table (for Purpose Limitation)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS data_purposes (
            purpose_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            created_by TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            active BOOLEAN NOT NULL DEFAULT TRUE
        )
        ''')
        
        # Create scan-purpose relation table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS scan_purposes (
            id SERIAL PRIMARY KEY,
            scan_id TEXT NOT NULL REFERENCES scans(scan_id) ON DELETE CASCADE,
            purpose_id TEXT NOT NULL REFERENCES data_purposes(purpose_id),
            assigned_at TIMESTAMP NOT NULL,
            assigned_by TEXT NOT NULL,
            UNIQUE(scan_id, purpose_id)
        )
        ''')
        
        # Create data minimization flags table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS data_minimization (
            id SERIAL PRIMARY KEY,
            scan_id TEXT NOT NULL REFERENCES scans(scan_id) ON DELETE CASCADE,
            pii_type TEXT NOT NULL,
            location TEXT NOT NULL,
            file_name TEXT NOT NULL,
            is_excessive BOOLEAN NOT NULL DEFAULT FALSE,
            is_unused BOOLEAN NOT NULL DEFAULT FALSE,
            reason TEXT,
            flagged_by TEXT NOT NULL,
            flagged_at TIMESTAMP NOT NULL
        )
        ''')
        
        # Create data accuracy verification table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS data_accuracy (
            id SERIAL PRIMARY KEY,
            scan_id TEXT NOT NULL REFERENCES scans(scan_id) ON DELETE CASCADE,
            pii_type TEXT NOT NULL,
            location TEXT NOT NULL,
            is_verified BOOLEAN NOT NULL DEFAULT FALSE,
            is_current BOOLEAN,
            verification_method TEXT,
            verified_by TEXT,
            verified_at TIMESTAMP,
            expires_at TIMESTAMP
        )
        ''')
        
        # Create storage limitation policies table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS storage_policies (
            policy_id TEXT PRIMARY KEY,
            pii_type TEXT NOT NULL,
            retention_period_days INTEGER NOT NULL,
            legal_basis TEXT NOT NULL,
            region TEXT NOT NULL,
            created_by TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            active BOOLEAN NOT NULL DEFAULT TRUE
        )
        ''')
        
        # Insert standard PII types if not exists
        cursor.execute("SELECT COUNT(*) FROM pii_types")
        if cursor.fetchone()[0] == 0:
            pii_types = [
                ('bsn', 'BSN', 'Dutch citizen service number', 'High', 'National ID', True),
                ('email', 'Email', 'Email address', 'Low', 'Contact', True),
                ('phone', 'Phone', 'Phone number', 'Medium', 'Contact', True),
                ('address', 'Address', 'Physical address', 'Medium', 'Contact', True),
                ('name', 'Name', 'Personal name', 'Low', 'Identity', True),
                ('credit_card', 'Credit Card', 'Credit card number', 'High', 'Financial', True),
                ('ip_address', 'IP Address', 'Internet Protocol address', 'Low', 'Technical', True),
                ('dob', 'Date of Birth', 'Date of birth', 'Medium', 'Identity', True),
                ('passport', 'Passport Number', 'Passport identification number', 'High', 'National ID', True),
                ('medical', 'Medical Data', 'Health-related information', 'High', 'Special Category', True),
                ('financial', 'Financial Data', 'Bank details, account numbers', 'High', 'Financial', True),
                ('username', 'Username', 'System username', 'Low', 'Technical', True),
                ('password', 'Password', 'System password', 'High', 'Technical', True)
            ]
            
            insert_query = '''
            INSERT INTO pii_types (type_id, name, description, risk_level, category, requires_consent)
            VALUES (%s, %s, %s, %s, %s, %s)
            '''
            cursor.executemany(insert_query, pii_types)
        
        # Create region-specific rules table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS region_rules (
            region_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            minor_age_limit INTEGER NOT NULL,
            breach_notification_hours INTEGER NOT NULL,
            special_requirements TEXT
        )
        ''')
        
        # Insert region data if not exists
        cursor.execute("SELECT COUNT(*) FROM region_rules")
        if cursor.fetchone()[0] == 0:
            regions = [
                ('NL', 'Netherlands', 16, 72, 'Special rules for BSN, medical data. Must follow UAVG.'),
                ('DE', 'Germany', 16, 72, 'Strict rules for data minimization. Must follow BDSG.'),
                ('FR', 'France', 15, 72, 'Special rules for minor data.'),
                ('BE', 'Belgium', 13, 72, 'Special rules for processing activities.')
            ]
            
            insert_query = '''
            INSERT INTO region_rules (region_id, name, minor_age_limit, breach_notification_hours, special_requirements)
            VALUES (%s, %s, %s, %s, %s)
            '''
            cursor.executemany(insert_query, regions)
        
        conn.commit()
        conn.close()
    
    def save_scan_result(self, result: Dict[str, Any]) -> bool:
        """
        Save a scan result to the database.
        
        Args:
            result: The scan result dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Extract required fields
            scan_id = result.get('scan_id')
            username = result.get('username')
            timestamp = result.get('timestamp', datetime.now().isoformat())
            scan_type = result.get('scan_type', 'Unknown')
            region = result.get('region', 'Unknown')
            file_count = result.get('file_count', 0)
            total_pii_found = result.get('total_pii_found', 0)
            high_risk_count = result.get('high_risk_count', 0)
            
            # Insert into database using jsonb for result_json
            cursor.execute('''
            INSERT INTO scans 
            (scan_id, username, timestamp, scan_type, region, file_count, total_pii_found, high_risk_count, result_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (scan_id) DO UPDATE 
            SET username = EXCLUDED.username,
                timestamp = EXCLUDED.timestamp,
                scan_type = EXCLUDED.scan_type,
                region = EXCLUDED.region,
                file_count = EXCLUDED.file_count,
                total_pii_found = EXCLUDED.total_pii_found,
                high_risk_count = EXCLUDED.high_risk_count,
                result_json = EXCLUDED.result_json
            ''', (scan_id, username, timestamp, scan_type, region, file_count, total_pii_found, high_risk_count, Json(result)))
            
            # Log scan action in audit log
            log_id = str(uuid.uuid4())
            cursor.execute('''
            INSERT INTO audit_log (log_id, username, action, timestamp, details)
            VALUES (%s, %s, %s, %s, %s)
            ''', (log_id, username, 'SCAN_SAVED', datetime.now().isoformat(), Json({
                'scan_id': scan_id,
                'scan_type': scan_type,
                'region': region,
                'file_count': file_count
            })))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error saving scan result: {str(e)}")
            return False
    
    def get_scan_by_id(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a scan result by ID.
        
        Args:
            scan_id: The ID of the scan to retrieve
            
        Returns:
            The scan result dictionary, or None if not found
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT result_json FROM scans WHERE scan_id = %s', (scan_id,))
            row = cursor.fetchone()
            
            conn.close()
            
            if row:
                return row[0]  # PostgreSQL jsonb is automatically converted to Python dict
            return None
            
        except Exception as e:
            print(f"Error retrieving scan result: {str(e)}")
            return None
    
    def get_all_scans(self, username: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve all scan results, optionally filtered by username.
        
        Args:
            username: Optional username to filter results
            
        Returns:
            List of scan result dictionaries
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if username:
                cursor.execute('SELECT result_json FROM scans WHERE username = %s ORDER BY timestamp DESC', (username,))
            else:
                cursor.execute('SELECT result_json FROM scans ORDER BY timestamp DESC')
            
            rows = cursor.fetchall()
            conn.close()
            
            return [row[0] for row in rows]  # PostgreSQL jsonb is automatically converted to Python dict
            
        except Exception as e:
            print(f"Error retrieving scan results: {str(e)}")
            return []
    
    def delete_scan(self, scan_id: str, username: str = None) -> bool:
        """
        Delete a scan result by ID.
        
        Args:
            scan_id: The ID of the scan to delete
            username: Username for audit logging
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get scan details before deletion for audit log
            cursor.execute('SELECT username, scan_type FROM scans WHERE scan_id = %s', (scan_id,))
            scan_details = cursor.fetchone()
            
            if not scan_details:
                return False
                
            scan_username, scan_type = scan_details
            
            # Delete the scan
            cursor.execute('DELETE FROM scans WHERE scan_id = %s', (scan_id,))
            
            # Log deletion in audit log
            log_id = str(uuid.uuid4())
            audit_username = username or scan_username or 'system'
            cursor.execute('''
            INSERT INTO audit_log (log_id, username, action, timestamp, details)
            VALUES (%s, %s, %s, %s, %s)
            ''', (log_id, audit_username, 'SCAN_DELETED', datetime.now().isoformat(), Json({
                'scan_id': scan_id,
                'scan_type': scan_type
            })))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error deleting scan result: {str(e)}")
            return False
    
    def get_recent_scans(self, days: int = 30, limit: int = 100, username: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get recent scan results within a specified time period.
        
        Args:
            days: Number of days to look back
            limit: Maximum number of scans to return
            username: Optional username to filter results
            
        Returns:
            List of recent scan result dictionaries
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Calculate cutoff date
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            if username:
                cursor.execute('''
                SELECT result_json FROM scans 
                WHERE username = %s AND timestamp > %s
                ORDER BY timestamp DESC LIMIT %s
                ''', (username, cutoff_date, limit))
            else:
                cursor.execute('''
                SELECT result_json FROM scans 
                WHERE timestamp > %s
                ORDER BY timestamp DESC LIMIT %s
                ''', (cutoff_date, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [row[0] for row in rows]
            
        except Exception as e:
            print(f"Error retrieving recent scan results: {str(e)}")
            return []
    
    def get_statistics(self, username: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics about scan results.
        
        Args:
            username: Optional username to filter results
            
        Returns:
            Dictionary with statistics
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            stats = {}
            
            # Base where clause and parameters
            where_clause = 'WHERE username = %s' if username else ''
            params = (username,) if username else ()
            
            # Get total scans
            cursor.execute(f'SELECT COUNT(*) FROM scans {where_clause}', params if username else None)
            stats['total_scans'] = cursor.fetchone()[0]
            
            # Get total PII found
            cursor.execute(f'SELECT SUM(total_pii_found) FROM scans {where_clause}', params if username else None)
            stats['total_pii_found'] = cursor.fetchone()[0] or 0
            
            # Get total high risk items
            cursor.execute(f'SELECT SUM(high_risk_count) FROM scans {where_clause}', params if username else None)
            stats['total_high_risk'] = cursor.fetchone()[0] or 0
            
            # Get scan types distribution
            if username:
                cursor.execute('SELECT scan_type, COUNT(*) FROM scans WHERE username = %s GROUP BY scan_type', (username,))
            else:
                cursor.execute('SELECT scan_type, COUNT(*) FROM scans GROUP BY scan_type')
            stats['scan_types'] = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Get regions distribution
            if username:
                cursor.execute('SELECT region, COUNT(*) FROM scans WHERE username = %s GROUP BY region', (username,))
            else:
                cursor.execute('SELECT region, COUNT(*) FROM scans GROUP BY region')
            stats['regions'] = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Add purpose limitation compliance stat
            cursor.execute('''
            SELECT COUNT(DISTINCT s.scan_id) 
            FROM scans s
            JOIN audit_log a ON a.details->>'scan_id' = s.scan_id
            WHERE a.action = 'PURPOSE_VALIDATED'
            ''' + (' AND s.username = %s' if username else ''), params if username else None)
            stats['purpose_validated_scans'] = cursor.fetchone()[0] or 0
            
            # Add data expiry information
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            cursor.execute(f'''
            SELECT COUNT(*) FROM scans
            WHERE timestamp < %s {' AND username = %s' if username else ''}
            ''', (thirty_days_ago,) + params if username else (thirty_days_ago,))
            stats['scans_older_than_30_days'] = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return stats
            
        except Exception as e:
            print(f"Error retrieving statistics: {str(e)}")
            return {'error': str(e)}
            
    def log_audit_event(self, username: str, action: str, details: Dict[str, Any] = None) -> bool:
        """
        Log an audit event.
        
        Args:
            username: Username performing the action
            action: Type of action (e.g., 'LOGIN', 'SCAN_STARTED', 'REPORT_GENERATED')
            details: Optional details about the action
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            log_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            cursor.execute('''
            INSERT INTO audit_log (log_id, username, action, timestamp, details)
            VALUES (%s, %s, %s, %s, %s)
            ''', (log_id, username, action, timestamp, Json(details) if details else None))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error logging audit event: {str(e)}")
            return False
    
    # ----- Purpose Limitation Implementation -----
    
    def create_data_purpose(self, name: str, description: str, created_by: str) -> Optional[str]:
        """
        Create a new data purpose for purpose limitation.
        
        Args:
            name: Purpose name
            description: Purpose description
            created_by: Username who created the purpose
            
        Returns:
            Purpose ID if successful, None otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            purpose_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            cursor.execute('''
            INSERT INTO data_purposes (purpose_id, name, description, created_by, created_at, active)
            VALUES (%s, %s, %s, %s, %s, %s)
            ''', (purpose_id, name, description, created_by, timestamp, True))
            
            conn.commit()
            conn.close()
            
            # Log the purpose creation
            self.log_audit_event(created_by, 'PURPOSE_CREATED', {
                'purpose_id': purpose_id,
                'name': name
            })
            
            return purpose_id
            
        except Exception as e:
            print(f"Error creating data purpose: {str(e)}")
            return None
    
    def assign_purpose_to_scan(self, scan_id: str, purpose_id: str, assigned_by: str) -> bool:
        """
        Assign a purpose to a scan (Purpose Limitation principle).
        
        Args:
            scan_id: The scan ID to assign a purpose to
            purpose_id: The purpose ID to assign
            assigned_by: Username who is assigning the purpose
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Verify that both scan and purpose exist
            cursor.execute('SELECT 1 FROM scans WHERE scan_id = %s', (scan_id,))
            scan_exists = cursor.fetchone() is not None
            
            cursor.execute('SELECT 1 FROM data_purposes WHERE purpose_id = %s AND active = TRUE', (purpose_id,))
            purpose_exists = cursor.fetchone() is not None
            
            if not scan_exists or not purpose_exists:
                conn.close()
                return False
            
            # Assign purpose to scan
            timestamp = datetime.now().isoformat()
            cursor.execute('''
            INSERT INTO scan_purposes (scan_id, purpose_id, assigned_at, assigned_by)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (scan_id, purpose_id) DO NOTHING
            ''', (scan_id, purpose_id, timestamp, assigned_by))
            
            # Log purpose assignment in audit log
            self.log_audit_event(assigned_by, 'PURPOSE_ASSIGNED', {
                'scan_id': scan_id,
                'purpose_id': purpose_id
            })
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error assigning purpose to scan: {str(e)}")
            return False
    
    def validate_purpose_for_scan(self, scan_id: str, purpose_id: str, validated_by: str) -> bool:
        """
        Validate that a scan's data use complies with its stated purpose (Purpose Limitation).
        
        Args:
            scan_id: The scan ID to validate
            purpose_id: The purpose ID to validate against
            validated_by: Username who is performing the validation
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Verify that the scan has been assigned this purpose
            cursor.execute('''
            SELECT 1 FROM scan_purposes 
            WHERE scan_id = %s AND purpose_id = %s
            ''', (scan_id, purpose_id))
            
            if cursor.fetchone() is None:
                conn.close()
                return False
            
            # Log the purpose validation in audit log
            self.log_audit_event(validated_by, 'PURPOSE_VALIDATED', {
                'scan_id': scan_id,
                'purpose_id': purpose_id,
                'validated_at': datetime.now().isoformat()
            })
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error validating purpose for scan: {str(e)}")
            return False
    
    def flag_purpose_violation(self, scan_id: str, purpose_id: str, reason: str, flagged_by: str) -> bool:
        """
        Flag a scan as violating its stated purpose (Purpose Limitation).
        
        Args:
            scan_id: The scan ID that violates the purpose
            purpose_id: The purpose ID that is violated
            reason: Reason for the violation
            flagged_by: Username who is flagging the violation
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Log the purpose violation in audit log
            return self.log_audit_event(flagged_by, 'PURPOSE_VIOLATION', {
                'scan_id': scan_id,
                'purpose_id': purpose_id,
                'reason': reason,
                'flagged_at': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Error flagging purpose violation: {str(e)}")
            return False
    
    # ----- Data Minimization Implementation -----
    
    def flag_excessive_data(self, scan_id: str, pii_type: str, location: str, file_name: str, 
                          reason: str, flagged_by: str) -> bool:
        """
        Flag excessive data (Data Minimization principle).
        
        Args:
            scan_id: The ID of the scan containing the data
            pii_type: Type of PII that is excessive
            location: Location of the PII (e.g., line number)
            file_name: Name of the file containing the PII
            reason: Reason why the data is considered excessive
            flagged_by: Username who is flagging the data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            
            cursor.execute('''
            INSERT INTO data_minimization (scan_id, pii_type, location, file_name, 
                                          is_excessive, is_unused, reason, flagged_by, flagged_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (scan_id, pii_type, location, file_name, True, False, reason, flagged_by, timestamp))
            
            # Log in audit trail
            self.log_audit_event(flagged_by, 'EXCESSIVE_DATA_FLAGGED', {
                'scan_id': scan_id,
                'pii_type': pii_type,
                'location': location,
                'file_name': file_name,
                'reason': reason
            })
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error flagging excessive data: {str(e)}")
            return False
    
    def flag_unused_data(self, scan_id: str, pii_type: str, location: str, file_name: str, 
                        reason: str, flagged_by: str) -> bool:
        """
        Flag unused data (Data Minimization principle).
        
        Args:
            scan_id: The ID of the scan containing the data
            pii_type: Type of PII that is unused
            location: Location of the PII (e.g., line number)
            file_name: Name of the file containing the PII
            reason: Reason why the data is considered unused
            flagged_by: Username who is flagging the data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            
            cursor.execute('''
            INSERT INTO data_minimization (scan_id, pii_type, location, file_name, 
                                          is_excessive, is_unused, reason, flagged_by, flagged_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (scan_id, pii_type, location, file_name, False, True, reason, flagged_by, timestamp))
            
            # Log in audit trail
            self.log_audit_event(flagged_by, 'UNUSED_DATA_FLAGGED', {
                'scan_id': scan_id,
                'pii_type': pii_type,
                'location': location,
                'file_name': file_name,
                'reason': reason
            })
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error flagging unused data: {str(e)}")
            return False
    
    def get_minimization_issues(self, scan_id: str) -> List[Dict[str, Any]]:
        """
        Get all data minimization issues for a scan.
        
        Args:
            scan_id: The ID of the scan to check
            
        Returns:
            List of data minimization issues
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT id, scan_id, pii_type, location, file_name, is_excessive, is_unused, reason, 
                   flagged_by, flagged_at
            FROM data_minimization
            WHERE scan_id = %s
            ORDER BY flagged_at DESC
            ''', (scan_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            issues = []
            for row in rows:
                issue = {
                    'id': row[0],
                    'scan_id': row[1],
                    'pii_type': row[2],
                    'location': row[3],
                    'file_name': row[4],
                    'is_excessive': row[5],
                    'is_unused': row[6],
                    'reason': row[7],
                    'flagged_by': row[8],
                    'flagged_at': row[9].isoformat() if hasattr(row[9], 'isoformat') else row[9]
                }
                issues.append(issue)
            
            return issues
            
        except Exception as e:
            print(f"Error getting minimization issues: {str(e)}")
            return []
    
    # ----- Accuracy Implementation -----
    
    def verify_data_accuracy(self, scan_id: str, pii_type: str, location: str, 
                           is_current: bool, verification_method: str, verified_by: str,
                           expires_at: Optional[datetime] = None) -> bool:
        """
        Verify the accuracy of detected PII (Accuracy principle).
        
        Args:
            scan_id: The ID of the scan containing the data
            pii_type: Type of PII to verify
            location: Location of the PII
            is_current: Whether the data is current/accurate
            verification_method: Method used for verification
            verified_by: Username who performed the verification
            expires_at: When this verification expires
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            verification_time = datetime.now().isoformat()
            expiry_time = expires_at.isoformat() if expires_at else None
            
            cursor.execute('''
            INSERT INTO data_accuracy 
            (scan_id, pii_type, location, is_verified, is_current, verification_method, verified_by, verified_at, expires_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (scan_id, pii_type, location, True, is_current, verification_method, verified_by, 
                  verification_time, expiry_time))
            
            # Log audit event
            self.log_audit_event(verified_by, 'DATA_VERIFIED', {
                'scan_id': scan_id,
                'pii_type': pii_type,
                'location': location,
                'is_current': is_current,
                'verification_method': verification_method,
                'expires_at': expiry_time
            })
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error verifying data accuracy: {str(e)}")
            return False
    
    def get_unverified_data(self, scan_id: str) -> List[Dict[str, Any]]:
        """
        Get all unverified PII data in a scan (Accuracy principle).
        
        Args:
            scan_id: The ID of the scan to check
            
        Returns:
            List of unverified PII items
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Query to find all PII in this scan that hasn't been verified
            cursor.execute('''
            WITH scan_pii AS (
                SELECT 
                    s.scan_id,
                    pii.pii_type,
                    pii.location
                FROM scans s
                CROSS JOIN LATERAL jsonb_to_recordset(s.result_json->'detailed_results') 
                    AS file(file_name text, pii_found jsonb)
                CROSS JOIN LATERAL jsonb_to_recordset(file.pii_found) 
                    AS pii(type text, value text, location text, risk_level text)
                WHERE s.scan_id = %s
            )
            SELECT 
                sp.scan_id, 
                sp.pii_type, 
                sp.location
            FROM scan_pii sp
            LEFT JOIN data_accuracy da 
                ON sp.scan_id = da.scan_id 
                AND sp.pii_type = da.pii_type 
                AND sp.location = da.location
            WHERE da.id IS NULL
            ''', (scan_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            unverified = []
            for row in rows:
                item = {
                    'scan_id': row[0],
                    'pii_type': row[1],
                    'location': row[2]
                }
                unverified.append(item)
            
            return unverified
            
        except Exception as e:
            print(f"Error getting unverified data: {str(e)}")
            return []
    
    def get_expired_verifications(self) -> List[Dict[str, Any]]:
        """
        Get all expired data accuracy verifications (Accuracy principle).
        
        Returns:
            List of expired verifications
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cursor.execute('''
            SELECT 
                id, scan_id, pii_type, location, is_current, verification_method, 
                verified_by, verified_at, expires_at
            FROM data_accuracy
            WHERE expires_at IS NOT NULL AND expires_at < %s
            ''', (now,))
            
            rows = cursor.fetchall()
            conn.close()
            
            expired = []
            for row in rows:
                item = {
                    'id': row[0],
                    'scan_id': row[1],
                    'pii_type': row[2],
                    'location': row[3],
                    'is_current': row[4],
                    'verification_method': row[5],
                    'verified_by': row[6],
                    'verified_at': row[7].isoformat() if hasattr(row[7], 'isoformat') else row[7],
                    'expires_at': row[8].isoformat() if hasattr(row[8], 'isoformat') else row[8]
                }
                expired.append(item)
            
            return expired
            
        except Exception as e:
            print(f"Error getting expired verifications: {str(e)}")
            return []
    
    # ----- Storage Limitation Implementation -----
    
    def create_storage_policy(self, pii_type: str, retention_period_days: int, 
                            legal_basis: str, region: str, created_by: str) -> Optional[str]:
        """
        Create a storage limitation policy (Storage Limitation principle).
        
        Args:
            pii_type: Type of PII this policy applies to
            retention_period_days: How long the data can be kept (in days)
            legal_basis: Legal basis for the retention period
            region: Region this policy applies to
            created_by: Username who created the policy
            
        Returns:
            Policy ID if successful, None otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            policy_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            cursor.execute('''
            INSERT INTO storage_policies 
            (policy_id, pii_type, retention_period_days, legal_basis, region, created_by, created_at, active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (policy_id, pii_type, retention_period_days, legal_basis, region, created_by, timestamp, True))
            
            # Log audit event
            self.log_audit_event(created_by, 'STORAGE_POLICY_CREATED', {
                'policy_id': policy_id,
                'pii_type': pii_type,
                'retention_period_days': retention_period_days,
                'region': region
            })
            
            conn.commit()
            conn.close()
            return policy_id
            
        except Exception as e:
            print(f"Error creating storage policy: {str(e)}")
            return None
    
    def get_data_past_retention(self) -> List[Dict[str, Any]]:
        """
        Find PII data past its retention period (Storage Limitation principle).
        
        Returns:
            List of PII data items past their retention period
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            WITH scan_pii AS (
                SELECT 
                    s.scan_id,
                    s.username,
                    s.timestamp,
                    s.region,
                    pii.pii_type AS type,
                    pii.location,
                    file.file_name
                FROM scans s
                CROSS JOIN LATERAL jsonb_to_recordset(s.result_json->'detailed_results') 
                    AS file(file_name text, pii_found jsonb)
                CROSS JOIN LATERAL jsonb_to_recordset(file.pii_found) 
                    AS pii(type text, value text, location text, risk_level text)
            )
            SELECT 
                sp.scan_id,
                sp.username,
                sp.timestamp,
                sp.region,
                sp.type,
                sp.location,
                sp.file_name,
                sp.policy_id,
                sp.retention_period_days,
                sp.legal_basis
            FROM (
                SELECT 
                    sp.*,
                    p.policy_id,
                    p.retention_period_days,
                    p.legal_basis,
                    sp.timestamp + (p.retention_period_days * INTERVAL '1 day') AS expiry_date
                FROM scan_pii sp
                JOIN storage_policies p 
                    ON sp.type = p.pii_type 
                    AND sp.region = p.region
                    AND p.active = TRUE
            ) sp
            WHERE sp.expiry_date < NOW()
            ORDER BY sp.timestamp
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            expired_data = []
            for row in rows:
                item = {
                    'scan_id': row[0],
                    'username': row[1],
                    'scan_timestamp': row[2].isoformat() if hasattr(row[2], 'isoformat') else row[2],
                    'region': row[3],
                    'pii_type': row[4],
                    'location': row[5],
                    'file_name': row[6],
                    'policy_id': row[7],
                    'retention_period_days': row[8],
                    'legal_basis': row[9],
                    'should_have_been_deleted_by': 
                        (row[2] + timedelta(days=row[8])).isoformat() 
                        if hasattr(row[2], 'isoformat') else row[2]
                }
                expired_data.append(item)
            
            return expired_data
            
        except Exception as e:
            print(f"Error finding data past retention: {str(e)}")
            return []
    
    def mark_data_for_deletion(self, scan_id: str, pii_type: str, location: str, 
                             marked_by: str, reason: str = "Retention period expired") -> bool:
        """
        Mark data for deletion due to storage limitation (Storage Limitation principle).
        
        Args:
            scan_id: The ID of the scan containing the data
            pii_type: Type of PII to mark for deletion
            location: Location of the PII
            marked_by: Username who marked the data
            reason: Reason for deletion
            
        Returns:
            True if successful, False otherwise
        """
        # This is primarily an audit log entry until actual deletion functionality is implemented
        return self.log_audit_event(marked_by, 'DATA_MARKED_FOR_DELETION', {
            'scan_id': scan_id,
            'pii_type': pii_type,
            'location': location,
            'reason': reason,
            'marked_at': datetime.now().isoformat()
        })

import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional

class ResultsAggregator:
    """
    Aggregates and stores scan results in a database.
    """
    
    def __init__(self, db_path: str = "gdpr_scan_results.db"):
        """
        Initialize the results aggregator.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the database with required tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create scans table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            scan_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            scan_type TEXT NOT NULL,
            region TEXT NOT NULL,
            file_count INTEGER NOT NULL,
            total_pii_found INTEGER NOT NULL,
            high_risk_count INTEGER NOT NULL,
            result_json TEXT NOT NULL
        )
        ''')
        
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
            conn = sqlite3.connect(self.db_path)
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
            
            # Convert result to JSON
            result_json = json.dumps(result)
            
            # Insert into database
            cursor.execute('''
            INSERT OR REPLACE INTO scans 
            (scan_id, username, timestamp, scan_type, region, file_count, total_pii_found, high_risk_count, result_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (scan_id, username, timestamp, scan_type, region, file_count, total_pii_found, high_risk_count, result_json))
            
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
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT result_json FROM scans WHERE scan_id = ?', (scan_id,))
            row = cursor.fetchone()
            
            conn.close()
            
            if row:
                return json.loads(row[0])
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
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if username:
                cursor.execute('SELECT result_json FROM scans WHERE username = ? ORDER BY timestamp DESC', (username,))
            else:
                cursor.execute('SELECT result_json FROM scans ORDER BY timestamp DESC')
            
            rows = cursor.fetchall()
            conn.close()
            
            return [json.loads(row[0]) for row in rows]
            
        except Exception as e:
            print(f"Error retrieving scan results: {str(e)}")
            return []
    
    def delete_scan(self, scan_id: str) -> bool:
        """
        Delete a scan result by ID.
        
        Args:
            scan_id: The ID of the scan to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM scans WHERE scan_id = ?', (scan_id,))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error deleting scan result: {str(e)}")
            return False
    
    def get_statistics(self, username: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics about scan results.
        
        Args:
            username: Optional username to filter results
            
        Returns:
            Dictionary with statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            stats = {}
            
            # Query parameters
            params = (username,) if username else ()
            where_clause = 'WHERE username = ?' if username else ''
            
            # Get total scans
            cursor.execute(f'SELECT COUNT(*) FROM scans {where_clause}', params)
            stats['total_scans'] = cursor.fetchone()[0]
            
            # Get total PII found
            cursor.execute(f'SELECT SUM(total_pii_found) FROM scans {where_clause}', params)
            stats['total_pii_found'] = cursor.fetchone()[0] or 0
            
            # Get total high risk items
            cursor.execute(f'SELECT SUM(high_risk_count) FROM scans {where_clause}', params)
            stats['total_high_risk'] = cursor.fetchone()[0] or 0
            
            # Get scan types distribution
            cursor.execute(f'SELECT scan_type, COUNT(*) FROM scans {where_clause} GROUP BY scan_type', params)
            stats['scan_types'] = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Get regions distribution
            cursor.execute(f'SELECT region, COUNT(*) FROM scans {where_clause} GROUP BY region', params)
            stats['regions'] = {row[0]: row[1] for row in cursor.fetchall()}
            
            conn.close()
            
            return stats
            
        except Exception as e:
            print(f"Error retrieving statistics: {str(e)}")
            return {'error': str(e)}

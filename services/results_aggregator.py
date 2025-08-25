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
    Falls back to file-based storage if database is unavailable.
    """
    
    def __init__(self, db_url: Optional[str] = None):
        """
        Initialize the results aggregator.
        
        Args:
            db_url: PostgreSQL database URL. If None, uses DATABASE_URL environment variable.
        """
        self.db_url = db_url or os.environ.get('DATABASE_URL')
        self.use_file_storage = False
        try:
            self._init_db()
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            self.use_file_storage = True
            self._init_file_storage()
    
    def _get_connection(self):
        """Get a database connection with error handling."""
        try:
            if self.db_url and not self.use_file_storage:
                return psycopg2.connect(self.db_url, sslmode='prefer')
            return None
        except Exception as e:
            print(f"Database connection error: {str(e)}")
            self.use_file_storage = True
            return None
    
    def _init_file_storage(self):
        """Initialize file-based storage for results."""
        # Create necessary directories
        os.makedirs('reports', exist_ok=True)
        os.makedirs('data', exist_ok=True)
        
        # Create initial empty files if they don't exist
        if not os.path.exists('data/scans.json'):
            with open('data/scans.json', 'w') as f:
                json.dump([], f)
                
        if not os.path.exists('data/audit_log.json'):
            with open('data/audit_log.json', 'w') as f:
                json.dump([], f)
    
    def _init_db(self):
        """Initialize the database with required tables if they don't exist."""
        conn = self._get_connection()
        if not conn:
            print("No database connection available. Using file-based storage.")
            self.use_file_storage = True
            self._init_file_storage()
            return
            
        try:
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
                gdpr_article TEXT
            )
            ''')
            
            # Create compliance scores table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS compliance_scores (
                score_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                repo_name TEXT NOT NULL,
                scan_id TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                overall_score INTEGER NOT NULL,
                principle_scores JSONB NOT NULL
            )
            ''')
            
            # Create GDPR principles reference table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS gdpr_principles (
                principle_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                article TEXT NOT NULL
            )
            ''')
            
            # Create user sessions table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                login_time TIMESTAMP NOT NULL,
                last_activity TIMESTAMP NOT NULL,
                ip_address TEXT,
                user_agent TEXT
            )
            ''')
            
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error creating database tables: {str(e)}")
            if conn:
                conn.close()
            self.use_file_storage = True
            self._init_file_storage()
    
    def save_scan_result(self, username: str, result: Dict[str, Any]) -> str:
        """
        Save scan result - alias for store_scan_result for backward compatibility.
        
        Args:
            username: Username who performed the scan
            result: Scan result dictionary
            
        Returns:
            str: Scan ID of the saved result
        """
        return self.store_scan_result(username, result)
    
    def store_scan_result(self, username: str, result: Dict[str, Any]) -> str:
        """
        Store a scan result in the database.
        
        Args:
            username: Username associated with the scan
            result: Scan result dictionary
        
        Returns:
            Scan ID
        """
        # Generate a scan ID if not present
        scan_id = result.get('scan_id', f"scan_{uuid.uuid4().hex}")
        result['scan_id'] = scan_id
        
        # Extract metadata
        scan_type = result.get('scan_type', 'unknown')
        region = result.get('region', 'Netherlands')  # Default to Netherlands for GDPR
        file_count = result.get('files_scanned', 0)
        total_pii = result.get('total_pii_found', 0)
        high_risk = result.get('high_risk_count', 0)
        
        if self.use_file_storage:
            return self._store_scan_result_file(username, scan_id, scan_type, 
                                              region, file_count, total_pii, 
                                              high_risk, result)
        
        try:
            conn = self._get_connection()
            if not conn:
                self.use_file_storage = True
                return self._store_scan_result_file(username, scan_id, scan_type, 
                                                 region, file_count, total_pii, 
                                                 high_risk, result)
            
            cursor = conn.cursor()
            
            # Insert into scans table
            cursor.execute("""
            INSERT INTO scans 
            (scan_id, username, timestamp, scan_type, region, file_count, total_pii_found, high_risk_count, result_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (scan_id) DO UPDATE SET
            timestamp = EXCLUDED.timestamp,
            result_json = EXCLUDED.result_json,
            file_count = EXCLUDED.file_count,
            total_pii_found = EXCLUDED.total_pii_found,
            high_risk_count = EXCLUDED.high_risk_count
            """, (
                scan_id,
                username,
                datetime.now(),
                scan_type,
                region,
                file_count,
                total_pii,
                high_risk,
                Json(result)
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return scan_id
        except Exception as e:
            print(f"Error storing scan result: {str(e)}")
            self.use_file_storage = True
            return self._store_scan_result_file(username, scan_id, scan_type, 
                                             region, file_count, total_pii, 
                                             high_risk, result)
    
    def _store_scan_result_file(self, username: str, scan_id: str, scan_type: str,
                              region: str, file_count: int, total_pii: int,
                              high_risk: int, result: Dict[str, Any]) -> str:
        """Store scan result in file system."""
        try:
            # Load existing scans
            scans = []
            if os.path.exists('data/scans.json'):
                with open('data/scans.json', 'r') as f:
                    scans = json.load(f)
            
            # Create scan entry
            scan_entry = {
                'scan_id': scan_id,
                'username': username,
                'timestamp': datetime.now().isoformat(),
                'scan_type': scan_type,
                'region': region,
                'file_count': file_count,
                'total_pii_found': total_pii,
                'high_risk_count': high_risk,
                'result': result
            }
            
            # Remove previous entry with same scan_id if exists
            scans = [s for s in scans if s.get('scan_id') != scan_id]
            
            # Add new entry
            scans.append(scan_entry)
            
            # Save to file
            with open('data/scans.json', 'w') as f:
                json.dump(scans, f, indent=2)
            
            # Save detailed result to separate file
            with open(f'reports/scan_{scan_id}.json', 'w') as f:
                json.dump(result, f, indent=2)
                
            return scan_id
        except Exception as e:
            print(f"Error storing scan result to file: {str(e)}")
            return scan_id
    
    def get_scan_result(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a scan result by ID.
        
        Args:
            scan_id: Scan ID
            
        Returns:
            Scan result dictionary or None if not found
        """
        if self.use_file_storage:
            return self._get_scan_result_file(scan_id)
        
        try:
            conn = self._get_connection()
            if not conn:
                self.use_file_storage = True
                return self._get_scan_result_file(scan_id)
            
            cursor = conn.cursor()
            
            # Query the scans table
            cursor.execute("SELECT result_json FROM scans WHERE scan_id = %s", (scan_id,))
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if result:
                return result[0]
            return None
        except Exception as e:
            print(f"Error retrieving scan result: {str(e)}")
            self.use_file_storage = True
            return self._get_scan_result_file(scan_id)
    
    def _get_scan_result_file(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """Get scan result from file system."""
        try:
            # Try to load from detailed file first
            if os.path.exists(f'reports/scan_{scan_id}.json'):
                with open(f'reports/scan_{scan_id}.json', 'r') as f:
                    return json.load(f)
            
            # Otherwise, look in the scans.json file
            if os.path.exists('data/scans.json'):
                with open('data/scans.json', 'r') as f:
                    scans = json.load(f)
                
                for scan in scans:
                    if scan.get('scan_id') == scan_id:
                        return scan.get('result')
            
            return None
        except Exception as e:
            print(f"Error retrieving scan result from file: {str(e)}")
            return None

    def get_user_scans(self, username: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent scans for a user.
        
        Args:
            username: Username to get scans for
            limit: Maximum number of scans to return
            
        Returns:
            List of scan metadata dictionaries
        """
        if self.use_file_storage:
            return self._get_user_scans_file(username, limit)
        
        try:
            conn = self._get_connection()
            if not conn:
                self.use_file_storage = True
                return self._get_user_scans_file(username, limit)
            
            cursor = conn.cursor()
            
            # Query the scans table for the most recent scans for this user
            cursor.execute("""
            SELECT scan_id, timestamp, scan_type, region, file_count, total_pii_found, high_risk_count
            FROM scans
            WHERE username = %s
            ORDER BY timestamp DESC
            LIMIT %s
            """, (username, limit))
            
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Format as dictionaries
            scans = []
            for row in results:
                scans.append({
                    'scan_id': row[0],
                    'timestamp': row[1].isoformat(),
                    'scan_type': row[2],
                    'region': row[3],
                    'file_count': row[4],
                    'total_pii_found': row[5],
                    'high_risk_count': row[6]
                })
            
            return scans
        except Exception as e:
            print(f"Error retrieving user scans: {str(e)}")
            self.use_file_storage = True
            return self._get_user_scans_file(username, limit)
    
    def _get_user_scans_file(self, username: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user scans from file system."""
        try:
            # Load existing scans
            if os.path.exists('data/scans.json'):
                with open('data/scans.json', 'r') as f:
                    all_scans = json.load(f)
                
                # Filter for this user and sort by timestamp (most recent first)
                user_scans = [s for s in all_scans if s.get('username') == username]
                user_scans.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                
                # Limit the number of results
                user_scans = user_scans[:limit]
                
                # Format for return
                return [
                    {
                        'scan_id': s.get('scan_id'),
                        'timestamp': s.get('timestamp'),
                        'scan_type': s.get('scan_type'),
                        'region': s.get('region'),
                        'file_count': s.get('file_count', 0),
                        'total_pii_found': s.get('total_pii_found', 0),
                        'high_risk_count': s.get('high_risk_count', 0)
                    }
                    for s in user_scans
                ]
            
            return []
        except Exception as e:
            print(f"Error retrieving user scans from file: {str(e)}")
            return []

    def get_recent_scans(self, days: int = 30, username: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get recent scans within the specified number of days.
        
        Args:
            days: Number of days to look back
            username: Optional username filter
            
        Returns:
            List of recent scan results
        """
        # Always try database first, even if use_file_storage is True
        db_scans = self._get_recent_scans_db(days, username)
        if db_scans is not None:
            return db_scans
            
        if self.use_file_storage:
            return self._get_recent_scans_file(days, username)
        
        return []
    
    def _get_recent_scans_db(self, days: int = 30, username: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """Get recent scans from database with enhanced error handling."""
        
        try:
            conn = self._get_connection()
            if not conn:
                print(f"No database connection for recent scans query")
                return None
            
            cursor = conn.cursor()
            
            # Calculate cutoff date - Use current timestamp for accurate filtering
            cutoff_date = datetime.now() - timedelta(days=days)
            print(f"Querying scans since: {cutoff_date} for user: {username}")
            
            # Build query with optional username filter  
            if username:
                cursor.execute("""
                    SELECT scan_id, username, timestamp, scan_type, region, 
                           file_count, total_pii_found, high_risk_count, result_json
                    FROM scans 
                    WHERE timestamp >= %s AND username = %s
                    ORDER BY timestamp DESC
                """, (cutoff_date, username))
            else:
                cursor.execute("""
                    SELECT scan_id, username, timestamp, scan_type, region, 
                           file_count, total_pii_found, high_risk_count, result_json
                    FROM scans 
                    WHERE timestamp >= %s
                    ORDER BY timestamp DESC
                """, (cutoff_date,))
            
            results = cursor.fetchall()
            print(f"Database returned {len(results)} scan records")
            
            cursor.close()
            conn.close()
            
            # Convert to list of dictionaries with enhanced logging
            scans = []
            for result in results:
                scan_data = {
                    'scan_id': result[0],
                    'username': result[1], 
                    'timestamp': result[2].isoformat() if result[2] else None,
                    'scan_type': result[3],
                    'region': result[4],
                    'file_count': result[5],
                    'total_pii_found': result[6],
                    'high_risk_count': result[7],
                    'result': result[8]
                }
                scans.append(scan_data)
            
            print(f"Formatted {len(scans)} scans for return")
            return scans
        except Exception as e:
            print(f"Error retrieving recent scans: {str(e)}")
            self.use_file_storage = True
            return self._get_recent_scans_file(days, username)
    
    def _get_recent_scans_file(self, days: int = 30, username: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent scans from file storage."""
        try:
            if not os.path.exists('data/scans.json'):
                return []
            
            with open('data/scans.json', 'r') as f:
                all_scans = json.load(f)
            
            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Filter scans
            recent_scans = []
            for scan in all_scans:
                try:
                    scan_date = datetime.fromisoformat(scan['timestamp'])
                    if scan_date >= cutoff_date:
                        if username is None or scan.get('username') == username:
                            recent_scans.append(scan)
                except (ValueError, KeyError):
                    continue
            
            # Sort by timestamp descending
            recent_scans.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return recent_scans
        except Exception as e:
            print(f"Error retrieving recent scans from file: {str(e)}")
            return []

    def log_audit_event(self, username: str, action: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an audit event for tracking user actions and system activities.
        
        Args:
            username: Username performing the action
            action: Type of action (e.g., 'login', 'scan', 'report_download')
            details: Dictionary of additional details
        """
        log_id = f"log_{uuid.uuid4().hex}"
        
        if self.use_file_storage:
            self._log_user_action_file(log_id, username, action, details)
            return
        
        try:
            conn = self._get_connection()
            if not conn:
                self.use_file_storage = True
                self._log_user_action_file(log_id, username, action, details)
                return
            
            cursor = conn.cursor()
            
            # Insert into audit_log table
            cursor.execute("""
            INSERT INTO audit_log (log_id, username, action, timestamp, details)
            VALUES (%s, %s, %s, %s, %s)
            """, (
                log_id,
                username,
                action,
                datetime.now(),
                Json(details) if details else None
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error logging audit event: {str(e)}")
            self.use_file_storage = True
            self._log_user_action_file(log_id, username, action, details)
    
    # For backward compatibility
    def log_user_action(self, username: str, action: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Legacy method for logging user actions, redirects to log_audit_event.
        
        Args:
            username: Username performing the action
            action: Type of action (e.g., 'login', 'scan', 'report_download')
            details: Dictionary of additional details
        """
        return self.log_audit_event(username, action, details)
    
    def _log_user_action_file(self, log_id: str, username: str, action: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log user action to file system."""
        try:
            # Load existing logs
            logs = []
            if os.path.exists('data/audit_log.json'):
                with open('data/audit_log.json', 'r') as f:
                    logs = json.load(f)
            
            # Create log entry
            log_entry = {
                'log_id': log_id,
                'username': username,
                'action': action,
                'timestamp': datetime.now().isoformat(),
                'details': details or {}
            }
            
            # Add new entry
            logs.append(log_entry)
            
            # Save to file (keep only last 1000 entries to prevent file growth)
            with open('data/audit_log.json', 'w') as f:
                json.dump(logs[-1000:], f, indent=2)
        except Exception as e:
            print(f"Error logging user action to file: {str(e)}")

    def store_scan_results(self, scan_id: str, username: str, scan_type: str, results: Dict[str, Any]) -> None:
        """
        Store scan results (alias for store_scan_result for compatibility).
        
        Args:
            scan_id: Unique scan identifier
            username: Username associated with the scan
            scan_type: Type of scan performed
            results: Scan result dictionary
        """
        # Ensure results has required fields
        results['scan_id'] = scan_id
        results['scan_type'] = scan_type
        self.store_scan_result(username, results)
    
    def get_scan_by_id(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a scan by its ID.
        
        Args:
            scan_id: Unique scan identifier
            
        Returns:
            Scan results dictionary or None if not found
        """
        if self.use_file_storage:
            return self._get_scan_by_id_file(scan_id)
        
        try:
            conn = self._get_connection()
            if not conn:
                self.use_file_storage = True
                return self._get_scan_by_id_file(scan_id)
            
            cursor = conn.cursor()
            cursor.execute("""
            SELECT scan_id, username, timestamp, scan_type, region, 
                   file_count, total_pii_found, high_risk_count, result_json
            FROM scans WHERE scan_id = %s
            """, (scan_id,))
            
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if row:
                return {
                    'scan_id': row[0],
                    'username': row[1],
                    'timestamp': row[2],
                    'scan_type': row[3],
                    'region': row[4],
                    'file_count': row[5],
                    'total_pii_found': row[6],
                    'high_risk_count': row[7],
                    'result_json': row[8]
                }
            return None
            
        except Exception as e:
            print(f"Error retrieving scan by ID: {str(e)}")
            self.use_file_storage = True
            return self._get_scan_by_id_file(scan_id)
    
    def _get_scan_by_id_file(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve scan by ID from file storage."""
        try:
            if os.path.exists('data/scans.json'):
                with open('data/scans.json', 'r') as f:
                    scans = json.load(f)
                    for scan in scans:
                        if scan.get('scan_id') == scan_id:
                            return scan
            return None
        except Exception as e:
            print(f"Error retrieving scan by ID from file: {str(e)}")
            return None

    def store_compliance_score(self, username: str, repo_name: str, scan_id: str, 
                             overall_score: int, principle_scores: Dict[str, int]) -> None:
        """
        Store a compliance score for a repository.
        
        Args:
            username: Username associated with the scan
            repo_name: Repository name or identifier
            scan_id: Associated scan ID
            overall_score: Overall compliance score (0-100)
            principle_scores: Dictionary mapping GDPR principles to scores (0-100)
        """
        score_id = f"score_{uuid.uuid4().hex}"
        
        if self.use_file_storage:
            self._store_compliance_score_file(score_id, username, repo_name, scan_id,
                                           overall_score, principle_scores)
            return
        
        try:
            conn = self._get_connection()
            if not conn:
                self.use_file_storage = True
                self._store_compliance_score_file(score_id, username, repo_name, scan_id,
                                              overall_score, principle_scores)
                return
            
            cursor = conn.cursor()
            
            # Insert into compliance_scores table
            cursor.execute("""
            INSERT INTO compliance_scores
            (score_id, username, repo_name, scan_id, timestamp, overall_score, principle_scores)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                score_id,
                username,
                repo_name,
                scan_id,
                datetime.now(),
                overall_score,
                Json(principle_scores)
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error storing compliance score: {str(e)}")
            self.use_file_storage = True
            self._store_compliance_score_file(score_id, username, repo_name, scan_id,
                                          overall_score, principle_scores)
    
    def _store_compliance_score_file(self, score_id: str, username: str, repo_name: str,
                                   scan_id: str, overall_score: int, 
                                   principle_scores: Dict[str, int]) -> None:
        """Store compliance score in file system."""
        try:
            # Create scores file if it doesn't exist
            scores = []
            if os.path.exists('data/compliance_scores.json'):
                with open('data/compliance_scores.json', 'r') as f:
                    scores = json.load(f)
            
            # Create score entry
            score_entry = {
                'score_id': score_id,
                'username': username,
                'repo_name': repo_name,
                'scan_id': scan_id,
                'timestamp': datetime.now().isoformat(),
                'overall_score': overall_score,
                'principle_scores': principle_scores
            }
            
            # Add new entry
            scores.append(score_entry)
            
            # Save to file
            with open('data/compliance_scores.json', 'w') as f:
                json.dump(scores, f, indent=2)
        except Exception as e:
            print(f"Error storing compliance score to file: {str(e)}")

    def get_user_compliance_history(self, username: str, repo_name: Optional[str] = None,
                                  days: int = 30) -> List[Dict[str, Any]]:
        """
        Get compliance score history for a user.
        
        Args:
            username: Username to get history for
            repo_name: Optional repository name to filter by
            days: Number of days of history to include
            
        Returns:
            List of compliance score data points
        """
        if self.use_file_storage:
            return self._get_user_compliance_history_file(username, repo_name, days)
        
        try:
            conn = self._get_connection()
            if not conn:
                self.use_file_storage = True
                return self._get_user_compliance_history_file(username, repo_name, days)
            
            cursor = conn.cursor()
            
            # Build query based on whether repo_name is provided
            if repo_name:
                query = """
                SELECT score_id, repo_name, scan_id, timestamp, overall_score, principle_scores
                FROM compliance_scores
                WHERE username = %s AND repo_name = %s AND timestamp > %s
                ORDER BY timestamp ASC
                """
                params = (username, repo_name, datetime.now() - timedelta(days=days))
            else:
                query = """
                SELECT score_id, repo_name, scan_id, timestamp, overall_score, principle_scores
                FROM compliance_scores
                WHERE username = %s AND timestamp > %s
                ORDER BY timestamp ASC
                """
                params = (username, datetime.now() - timedelta(days=days))
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Format as dictionaries
            history = []
            for row in results:
                history.append({
                    'score_id': row[0],
                    'repo_name': row[1],
                    'scan_id': row[2],
                    'timestamp': row[3].isoformat(),
                    'overall_score': row[4],
                    'principle_scores': row[5]
                })
            
            return history
        except Exception as e:
            print(f"Error retrieving compliance history: {str(e)}")
            self.use_file_storage = True
            return self._get_user_compliance_history_file(username, repo_name, days)
    
    def _get_user_compliance_history_file(self, username: str, repo_name: Optional[str] = None,
                                        days: int = 30) -> List[Dict[str, Any]]:
        """Get compliance history from file system."""
        try:
            if os.path.exists('data/compliance_scores.json'):
                with open('data/compliance_scores.json', 'r') as f:
                    all_scores = json.load(f)
                
                # Calculate cutoff date
                cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
                
                # Filter for this user and optional repo_name
                if repo_name:
                    filtered_scores = [
                        s for s in all_scores 
                        if s.get('username') == username 
                        and s.get('repo_name') == repo_name
                        and s.get('timestamp', '') > cutoff_date
                    ]
                else:
                    filtered_scores = [
                        s for s in all_scores 
                        if s.get('username') == username
                        and s.get('timestamp', '') > cutoff_date
                    ]
                
                # Sort by timestamp (oldest first for time series)
                filtered_scores.sort(key=lambda x: x.get('timestamp', ''))
                
                return filtered_scores
            
            return []
        except Exception as e:
            print(f"Error retrieving compliance history from file: {str(e)}")
            return []
    
    def get_all_scans(self, username: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get all scans for a user (alias for get_user_scans for backward compatibility).
        
        Args:
            username: Username to get scans for
            limit: Maximum number of scans to return
            
        Returns:
            List of scan metadata dictionaries
        """
        return self.get_user_scans(username, limit)
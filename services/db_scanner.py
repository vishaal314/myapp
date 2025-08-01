"""
Database Scanner module for detecting PII in database tables and columns.

This scanner connects to various database types (PostgreSQL, MySQL, SQLite, etc.) 
and analyzes schema, data sampling, and query results to identify potential 
PII data stored in the database.
"""

from typing import Dict, List, Any, Optional, Tuple, Union
import logging
import time
import os
import json
import re
from datetime import datetime
import random

try:
    import psycopg2
    import psycopg2.extras
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

try:
    import sqlite3
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DBScanner:
    """
    A scanner that detects PII in database tables, columns, and content.
    """
    
    def __init__(self, region: str = "Netherlands"):
        """
        Initialize the database scanner.
        
        Args:
            region: The region for which to apply GDPR rules
        """
        self.region = region
        self.connection = None
        self.db_type = None
        self.supported_db_types = []
        
        # Check available database drivers
        if POSTGRES_AVAILABLE:
            self.supported_db_types.append("postgres")
        if MYSQL_AVAILABLE:
            self.supported_db_types.append("mysql")
        if SQLITE_AVAILABLE:
            self.supported_db_types.append("sqlite")
            
        # PII detection patterns
        self.pii_patterns = self._get_pii_patterns()
        
        # Sampling settings
        self.max_sample_rows = 100
        self.max_columns_to_scan = 50
        self.max_table_count = 100
        
        # Timeout settings
        self.query_timeout_seconds = 30
        
        logger.info(f"Initialized DBScanner with region: {region}, supported DB types: {self.supported_db_types}")
    
    def _get_pii_patterns(self) -> Dict[str, Tuple[str, str]]:
        """
        Get patterns for detecting various types of PII in column names and data.
        
        Returns:
            Dictionary mapping PII type to (column pattern, data pattern) tuple
        """
        # Each pattern is a tuple of (column name regex, data content regex)
        patterns = {
            "EMAIL": (
                r"(?i)(^|_)e?mail(s|_address)?($|_)",
                r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
            ),
            "IP_ADDRESS": (
                r"(?i)(^|_)ip(_address|v4|v6)?($|_)",
                r"(?:\d{1,3}\.){3}\d{1,3}|([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}"
            ),
            "CREDIT_CARD": (
                r"(?i)(^|_)(cc|credit_?card|card_?num)($|_)",
                r"\b(?:\d{4}[- ]?){3}\d{4}\b"
            ),
            "PHONE": (
                r"(?i)(^|_)(phone|mobile|cell|tel|telephone|contact)(_num|_number)?($|_)",
                r"\b(?:\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b"
            ),
            "SSN": (
                r"(?i)(^|_)(ssn|social_security|social_security_number)($|_)",
                r"\b\d{3}[- ]?\d{2}[- ]?\d{4}\b"
            ),
            "NAME": (
                r"(?i)(^|_)(first|last|full|user|customer|client|person|employee)_?name($|_)",
                r"\b[A-Z][a-z]+(?: [A-Z][a-z]+)+\b"
            ),
            "USERNAME": (
                r"(?i)(^|_)(username|user_id|login|account)($|_)",
                r"\b[a-zA-Z0-9_]{3,20}\b"
            ),
            "PASSWORD": (
                r"(?i)(^|_)(password|passwd|pass|pwd|secure|credentials)($|_)",
                r".*"  # Any password data is sensitive
            ),
            "ADDRESS": (
                r"(?i)(^|_)(address|addr|street|city|state|province|country|zipcode|postal|zip)($|_)",
                r"\b\d+\s+[A-Za-z0-9\s\.,-]+\b"
            ),
            "DOB": (
                r"(?i)(^|_)(birth|dob|date_of_birth|birthdate)($|_)",
                r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"
            ),
            "AGE": (
                r"(?i)(^|_)age($|_)",
                r"\b\d{1,3}\b"
            ),
            "GENDER": (
                r"(?i)(^|_)(gender|sex)($|_)",
                r"\b(?:male|female|m|f|other|non-binary)\b"
            ),
            "ID_NUMBER": (
                r"(?i)(^|_)(id|identifier|national_id|passport|driver_license|license)(_num|_number)?($|_)",
                r"\b[A-Z0-9]{6,12}\b"
            ),
            "FINANCIAL": (
                r"(?i)(^|_)(account|acct|bank|routing|swift|iban)(_num|_number)?($|_)",
                r"\b[A-Z0-9]{8,34}\b"
            ),
            "MEDICAL": (
                r"(?i)(^|_)(health|medical|diagnosis|patient|treatment|prescription)($|_)",
                r".*"  # Any medical data is sensitive
            ),
            "BIOMETRIC": (
                r"(?i)(^|_)(biometric|fingerprint|retina|iris|face|voice)($|_)",
                r".*"  # Any biometric data is sensitive
            ),
            "LOCATION": (
                r"(?i)(^|_)(geo|lat|lon|longitude|latitude|coordinates|location)($|_)",
                r"\b-?\d{1,3}\.\d+\b"
            ),
            "RELIGION": (
                r"(?i)(^|_)(religion|faith|belief|church|temple|synagogue|mosque)($|_)",
                r"\b(?:christian|muslim|jewish|hindu|buddhist|sikh|atheist|agnostic)\b"
            ),
            "ETHNICITY": (
                r"(?i)(^|_)(ethnicity|race|origin|nationality)($|_)",
                r".*"  # Any ethnicity data is sensitive
            ),
            "POLITICAL": (
                r"(?i)(^|_)(political|politics|party|affiliation|vote)($|_)",
                r".*"  # Any political data is sensitive
            ),
            "UNION": (
                r"(?i)(^|_)(union|labor|trade_union|membership)($|_)",
                r".*"  # Any union membership data is sensitive
            ),
            "GENETIC": (
                r"(?i)(^|_)(genetic|dna|gene|genomic)($|_)",
                r".*"  # Any genetic data is sensitive
            ),
            "SEXUAL_ORIENTATION": (
                r"(?i)(^|_)(sexual|orientation|lgbtq|preference)($|_)",
                r".*"  # Any sexual orientation data is sensitive
            )
        }
        
        return patterns
    
    def connect_to_database(self, connection_params: Dict[str, Any]) -> bool:
        """
        Connect to a database.
        
        Args:
            connection_params: Parameters for database connection
                - db_type: Type of database (postgres, mysql, sqlite)
                - For Postgres: host, port, dbname, user, password
                - For MySQL: host, port, database, user, password
                - For SQLite: database (file path)
                
        Returns:
            True if connection is successful, False otherwise
        """
        db_type = connection_params.get('db_type', '').lower()
        
        if db_type not in self.supported_db_types:
            logger.error(f"Unsupported database type: {db_type}")
            return False
        
        try:
            if db_type == 'postgres':
                if not POSTGRES_AVAILABLE:
                    logger.error("PostgreSQL driver not available")
                    return False
                
                # Extract connection parameters
                host = connection_params.get('host', 'localhost')
                port = connection_params.get('port', 5432)
                dbname = connection_params.get('dbname', '')
                user = connection_params.get('user', '')
                password = connection_params.get('password', '')
                
                # Connect to database
                self.connection = psycopg2.connect(
                    host=host,
                    port=port,
                    dbname=dbname,
                    user=user,
                    password=password
                )
                
            elif db_type == 'mysql':
                if not MYSQL_AVAILABLE:
                    logger.error("MySQL driver not available")
                    return False
                
                # Extract connection parameters
                host = connection_params.get('host', 'localhost')
                port = connection_params.get('port', 3306)
                database = connection_params.get('database', '')
                user = connection_params.get('user', '')
                password = connection_params.get('password', '')
                
                # Connect to database
                self.connection = mysql.connector.connect(
                    host=host,
                    port=port,
                    database=database,
                    user=user,
                    password=password
                )
                
            elif db_type == 'sqlite':
                if not SQLITE_AVAILABLE:
                    logger.error("SQLite driver not available")
                    return False
                
                # Extract connection parameters
                database = connection_params.get('database', ':memory:')
                
                # Check if file exists for SQLite
                if database != ':memory:' and not os.path.exists(database):
                    logger.error(f"SQLite database file not found: {database}")
                    return False
                
                # Connect to database
                self.connection = sqlite3.connect(database)
            
            self.db_type = db_type
            logger.info(f"Successfully connected to {db_type} database")
            return True
            
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            self.connection = None
            return False
    
    def disconnect(self) -> None:
        """
        Disconnect from the database.
        """
        if self.connection:
            try:
                self.connection.close()
                logger.info("Disconnected from database")
            except Exception as e:
                logger.error(f"Error disconnecting from database: {str(e)}")
            finally:
                self.connection = None
                self.db_type = None
    
    def _get_tables(self) -> List[str]:
        """
        Get list of tables in the connected database.
        
        Returns:
            List of table names
        """
        if not self.connection:
            return []
        
        tables = []
        try:
            cursor = self.connection.cursor()
            
            if self.db_type == 'postgres':
                # Query to get all tables in PostgreSQL
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
                
            elif self.db_type == 'mysql':
                # Query to get all tables in MySQL
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = DATABASE()
                    ORDER BY table_name
                """)
                
            elif self.db_type == 'sqlite':
                # Query to get all tables in SQLite
                cursor.execute("""
                    SELECT name 
                    FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    ORDER BY name
                """)
            
            # Fetch all table names
            tables = [row[0] for row in cursor.fetchall()]
            
            # Limit the number of tables to scan
            if len(tables) > self.max_table_count:
                logger.warning(f"Too many tables ({len(tables)}), limiting to {self.max_table_count}")
                tables = tables[:self.max_table_count]
                
            cursor.close()
            
        except Exception as e:
            logger.error(f"Error getting tables: {str(e)}")
        
        return tables
    
    def _get_columns(self, table_name: str) -> List[str]:
        """
        Get list of columns for a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of column names
        """
        if not self.connection:
            return []
        
        columns = []
        try:
            cursor = self.connection.cursor()
            
            if self.db_type == 'postgres':
                # Query to get all columns for a table in PostgreSQL
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' AND table_name = %s
                    ORDER BY ordinal_position
                """, (table_name,))
                
            elif self.db_type == 'mysql':
                # Query to get all columns for a table in MySQL
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_schema = DATABASE() AND table_name = %s
                    ORDER BY ordinal_position
                """, (table_name,))
                
            elif self.db_type == 'sqlite':
                # Query to get all columns for a table in SQLite
                # Use escaped identifier to prevent SQL injection
                escaped_table = self._escape_identifier(table_name)
                cursor.execute(f"PRAGMA table_info({escaped_table})")
                columns = [row[1] for row in cursor.fetchall()]
                cursor.close()
                return columns
            
            # Fetch all column names (for PostgreSQL and MySQL)
            columns = [row[0] for row in cursor.fetchall()]
            
            # Limit the number of columns to scan
            if len(columns) > self.max_columns_to_scan:
                logger.warning(f"Too many columns ({len(columns)}), limiting to {self.max_columns_to_scan}")
                columns = columns[:self.max_columns_to_scan]
                
            cursor.close()
            
        except Exception as e:
            logger.error(f"Error getting columns for table {table_name}: {str(e)}")
        
        return columns
    
    def _escape_identifier(self, identifier: str) -> str:
        """
        Safely escape database identifiers (table/column names) to prevent SQL injection.
        
        Args:
            identifier: The database identifier to escape
            
        Returns:
            Safely escaped identifier
        """
        # Remove any existing quotes and escape internal quotes
        cleaned = identifier.replace('"', '""').replace('`', '``')
        
        # Apply appropriate quoting based on database type
        if self.db_type == 'mysql':
            return f'`{cleaned}`'
        else:  # postgres, sqlite
            return f'"{cleaned}"'
    
    def _get_sample_data(self, table_name: str, columns: List[str]) -> List[Dict[str, Any]]:
        """
        Get sample data from a table with proper SQL injection protection.
        
        Args:
            table_name: Name of the table
            columns: List of column names
            
        Returns:
            List of dictionaries, each representing a row of data
        """
        if not self.connection or not columns:
            return []
        
        sample_data = []
        try:
            cursor = self.connection.cursor()
            
            # Safely escape identifiers to prevent SQL injection
            escaped_columns = [self._escape_identifier(col) for col in columns]
            column_str = ", ".join(escaped_columns)
            escaped_table = self._escape_identifier(table_name)
            
            # Use parameterized query for LIMIT to prevent injection
            if self.db_type in ['postgres', 'sqlite']:
                if self.db_type == 'postgres':
                    query = f'SELECT {column_str} FROM {escaped_table} LIMIT %s'
                    cursor.execute(query, (self.max_sample_rows,))
                else:  # sqlite
                    query = f'SELECT {column_str} FROM {escaped_table} LIMIT ?'
                    cursor.execute(query, (self.max_sample_rows,))
            elif self.db_type == 'mysql':
                query = f'SELECT {column_str} FROM {escaped_table} LIMIT %s'
                cursor.execute(query, (self.max_sample_rows,))
            
            # Fetch all rows
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    row_dict[col] = row[i]
                sample_data.append(row_dict)
                
            cursor.close()
            
        except Exception as e:
            logger.error(f"Error getting sample data for table {table_name}: {str(e)}")
        
        return sample_data
    
    def _check_column_name_for_pii(self, column_name: str) -> List[Dict[str, Any]]:
        """
        Check if a column name suggests it may contain PII.
        
        Args:
            column_name: Name of the column
            
        Returns:
            List of PII findings based on column name
        """
        findings = []
        
        for pii_type, (column_pattern, _) in self.pii_patterns.items():
            if re.search(column_pattern, column_name):
                finding = {
                    "type": pii_type,
                    "column_name": column_name,
                    "source_type": "column_name",
                    "confidence": 0.7,  # Medium-high confidence based on naming
                    "context": f"Column name suggests {pii_type} data",
                    "detection_method": "column_name_analysis",
                    "risk_level": self._get_risk_level(pii_type),
                    "reason": self._get_reason(pii_type, "column_name")
                }
                findings.append(finding)
        
        return findings
    
    def _check_data_for_pii(self, column_name: str, data_values: List[Any]) -> List[Dict[str, Any]]:
        """
        Check if data in a column contains PII.
        
        Args:
            column_name: Name of the column
            data_values: List of values from the column
            
        Returns:
            List of PII findings based on data values
        """
        findings = []
        
        # Filter out None values and convert to strings
        data_values = [str(val) for val in data_values if val is not None]
        
        if not data_values:
            return []
        
        # Sample up to 10 values for checking
        sample_values = random.sample(data_values, min(10, len(data_values)))
        
        for pii_type, (_, data_pattern) in self.pii_patterns.items():
            # Skip password check for most columns unless they look like password columns
            if pii_type == "PASSWORD" and not re.search(self.pii_patterns["PASSWORD"][0], column_name):
                continue
                
            # Count matches
            matches = 0
            total_checked = len(sample_values)
            
            for value in sample_values:
                if re.search(data_pattern, value):
                    matches += 1
            
            # Calculate match percentage
            match_percentage = matches / total_checked if total_checked > 0 else 0
            
            # If more than 20% of values match the pattern, consider it a finding
            if match_percentage > 0.2:
                # Set confidence based on match percentage
                confidence = 0.5 + match_percentage / 2  # 0.6 to 1.0 based on matches
                
                finding = {
                    "type": pii_type,
                    "column_name": column_name,
                    "source_type": "data_content",
                    "confidence": confidence,
                    "context": f"Column data contains patterns consistent with {pii_type}",
                    "detection_method": "data_pattern_analysis",
                    "risk_level": self._get_risk_level(pii_type),
                    "match_percentage": match_percentage,
                    "reason": self._get_reason(pii_type, "data_content")
                }
                findings.append(finding)
        
        return findings
    
    def _get_risk_level(self, pii_type: str) -> str:
        """
        Get risk level for a specific PII type.
        
        Args:
            pii_type: The type of PII found
            
        Returns:
            Risk level (Critical, High, Medium, or Low)
        """
        critical_types = [
            "PASSWORD", "CREDIT_CARD", "SSN", "MEDICAL", 
            "BIOMETRIC", "GENETIC", "SEXUAL_ORIENTATION"
        ]
        
        high_types = [
            "EMAIL", "ID_NUMBER", "FINANCIAL", "DOB", "RELIGION",
            "ETHNICITY", "POLITICAL", "UNION"
        ]
        
        medium_types = [
            "NAME", "USERNAME", "ADDRESS", "PHONE", "LOCATION"
        ]
        
        if pii_type in critical_types:
            return "Critical"
        elif pii_type in high_types:
            return "High"
        elif pii_type in medium_types:
            return "Medium"
        else:
            return "Low"
    
    def _get_reason(self, pii_type: str, detection_type: str) -> str:
        """
        Get a reason explanation for the PII finding.
        
        Args:
            pii_type: The type of PII found
            detection_type: How the PII was detected (column_name or data_content)
            
        Returns:
            A string explaining why this PII is a concern
        """
        base_reasons = {
            "EMAIL": "Email addresses are direct contact information and online identifiers protected under GDPR.",
            "IP_ADDRESS": "IP addresses are considered personal data under GDPR as they can identify individuals' online activities.",
            "CREDIT_CARD": "Payment card information requires special protection under both GDPR and PCI DSS requirements.",
            "PHONE": "Phone numbers are direct contact information protected as personal data.",
            "SSN": "Social security numbers are highly sensitive personal identifiers with significant identity theft risk.",
            "NAME": "Names are basic personal identifiers protected under data protection regulations.",
            "USERNAME": "Usernames are online identifiers that can be linked to individuals.",
            "PASSWORD": "Password data is highly sensitive and requires encryption and strict security controls.",
            "ADDRESS": "Physical addresses are contact information that can reveal location and living circumstances.",
            "DOB": "Birth dates are personal identifiers that contribute to identity verification and age determination.",
            "AGE": "Age information is personal data that reveals demographic characteristics.",
            "GENDER": "Gender information is personal data that can be sensitive in certain contexts.",
            "ID_NUMBER": "Government-issued identification numbers are personal data that can uniquely identify individuals.",
            "FINANCIAL": "Financial account information is sensitive personal data requiring protection under GDPR.",
            "MEDICAL": "Health information is special category data under GDPR Article 9 requiring explicit consent.",
            "BIOMETRIC": "Biometric data is special category data under GDPR Article 9.",
            "LOCATION": "Location data can reveal personal habits, activities, and whereabouts of individuals.",
            "RELIGION": "Religious beliefs are special category data under GDPR Article 9.",
            "ETHNICITY": "Ethnic origin is special category data under GDPR Article 9.",
            "POLITICAL": "Political opinions are special category data under GDPR Article 9.",
            "UNION": "Trade union membership is special category data under GDPR Article 9.",
            "GENETIC": "Genetic data is special category data under GDPR Article 9.",
            "SEXUAL_ORIENTATION": "Sexual orientation is special category data under GDPR Article 9."
        }
        
        # Default reason if specific type not found
        default_reason = f"This type of personal information ({pii_type}) requires protection under applicable data protection regulations."
        
        # Get specific reason or default
        base_reason = base_reasons.get(pii_type, default_reason)
        
        # Add context based on how it was detected
        if detection_type == "column_name":
            context = "Column naming suggests PII data storage which requires appropriate security measures."
        else:  # data_content
            context = "Actual data content contains personal information requiring protection."
        
        # Add region-specific information for Netherlands
        if self.region == "Netherlands":
            region_context = " Under Dutch UAVG implementation of GDPR, this requires specific technical and organizational measures."
            return f"{base_reason} {context}{region_context}"
        
        return f"{base_reason} {context}"
    
    def scan_table(self, table_name: str) -> Dict[str, Any]:
        """
        Scan a single table for PII in both column names and data.
        
        Args:
            table_name: Name of the table to scan
            
        Returns:
            Dictionary containing scan results
        """
        if not self.connection:
            return {"error": "Not connected to database", "findings": []}
        
        logger.info(f"Scanning table: {table_name}")
        
        start_time = time.time()
        findings = []
        
        try:
            # Get columns
            columns = self._get_columns(table_name)
            
            if not columns:
                return {
                    "table": table_name,
                    "error": f"No columns found in table {table_name}",
                    "findings": [],
                    "scan_time_ms": int((time.time() - start_time) * 1000)
                }
            
            # Check column names for PII indicators
            for column in columns:
                column_findings = self._check_column_name_for_pii(column)
                for finding in column_findings:
                    finding["table"] = table_name
                findings.extend(column_findings)
            
            # Get sample data
            sample_data = self._get_sample_data(table_name, columns)
            
            if sample_data:
                # Convert sample data to column-based format for easier analysis
                column_data = {}
                for column in columns:
                    column_data[column] = [row.get(column) for row in sample_data]
                
                # Check data for PII
                for column, values in column_data.items():
                    data_findings = self._check_data_for_pii(column, values)
                    for finding in data_findings:
                        finding["table"] = table_name
                    findings.extend(data_findings)
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(findings)
            
            # Record scan metadata
            metadata = {
                "scan_time": datetime.now().isoformat(),
                "db_type": self.db_type,
                "table": table_name,
                "columns_scanned": len(columns),
                "rows_sampled": len(sample_data),
                "process_time_ms": int((time.time() - start_time) * 1000)
            }
            
            logger.info(f"Completed scan for table {table_name}. Found {len(findings)} PII instances.")
            
            return {
                "table": table_name,
                "metadata": metadata,
                "findings": findings,
                "risk_score": risk_score,
                "has_pii": len(findings) > 0
            }
            
        except Exception as e:
            logger.error(f"Error scanning table {table_name}: {str(e)}")
            return {
                "table": table_name,
                "error": str(e),
                "findings": [],
                "scan_time_ms": int((time.time() - start_time) * 1000)
            }
    
    def scan_database(self, callback_fn = None) -> Dict[str, Any]:
        """
        Scan all tables in the connected database for PII.
        
        Args:
            callback_fn: Callback function for progress updates
            
        Returns:
            Dictionary containing aggregated scan results
        """
        if not self.connection:
            return {"error": "Not connected to database", "findings": []}
        
        logger.info(f"Scanning entire database of type: {self.db_type}")
        
        start_time = time.time()
        all_findings = []
        tables_with_pii = 0
        tables_scanned = 0
        errors = []
        table_results = {}
        
        # Get all tables
        tables = self._get_tables()
        total_tables = len(tables)
        
        # Scan each table
        for i, table in enumerate(tables):
            # Update progress
            if callback_fn:
                callback_fn(i + 1, total_tables, table)
            
            # Scan table
            result = self.scan_table(table)
            tables_scanned += 1
            
            # Store result
            table_results[table] = result
            
            # Check for errors
            if "error" in result and result["error"]:
                errors.append({"table": table, "error": result["error"]})
            else:
                # Add findings
                table_findings = result.get("findings", [])
                all_findings.extend(table_findings)
                
                # Update count of tables with PII
                if result.get("has_pii", False):
                    tables_with_pii += 1
        
        # Calculate overall risk
        risk_summary = self._calculate_overall_risk(all_findings)
        
        # Record scan metadata
        metadata = {
            "scan_time": datetime.now().isoformat(),
            "db_type": self.db_type,
            "tables_scanned": tables_scanned,
            "tables_total": total_tables,
            "tables_with_pii": tables_with_pii,
            "total_findings": len(all_findings),
            "process_time_seconds": time.time() - start_time
        }
        
        logger.info(f"Completed database scan. Scanned {tables_scanned} tables, found {len(all_findings)} PII instances.")
        
        results = {
            "scan_type": "database",
            "metadata": metadata,
            "table_results": table_results,
            "findings": all_findings,
            "tables_with_pii": tables_with_pii,
            "errors": errors,
            "risk_summary": risk_summary
        }
        
        # Integrate cost savings analysis
        try:
            from services.cost_savings_calculator import integrate_cost_savings_into_report
            results = integrate_cost_savings_into_report(results, 'database', self.region)
        except Exception as e:
            logger.warning(f"Cost savings integration failed: {e}")
        
        return results
    
    def _calculate_risk_score(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate risk score for an individual table based on findings.
        
        Args:
            findings: List of PII findings
            
        Returns:
            Dictionary with risk score details
        """
        if not findings:
            return {
                "score": 0,
                "max_score": 100,
                "level": "Low",
                "factors": []
            }
        
        # Count findings by risk level
        risk_counts = {
            "Critical": 0,
            "High": 0,
            "Medium": 0,
            "Low": 0
        }
        
        for finding in findings:
            risk_level = finding.get("risk_level", "Medium")
            if risk_level in risk_counts:
                risk_counts[risk_level] += 1
        
        # Calculate score (weighted sum)
        weights = {
            "Critical": 25,
            "High": 15,
            "Medium": 7,
            "Low": 2
        }
        
        score = sum(risk_counts[level] * weights[level] for level in risk_counts)
        # Cap at 100
        score = min(score, 100)
        
        # Determine overall risk level
        level = "Low"
        if score >= 75:
            level = "Critical"
        elif score >= 50:
            level = "High"
        elif score >= 25:
            level = "Medium"
        
        # Risk factors explanation
        factors = []
        for risk_level, count in risk_counts.items():
            if count > 0:
                factors.append(f"{count} {risk_level} risk finding{'s' if count > 1 else ''}")
        
        return {
            "score": score,
            "max_score": 100,
            "level": level,
            "factors": factors
        }
    
    def _calculate_overall_risk(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate overall risk metrics from all findings across all tables.
        
        Args:
            findings: List of all PII findings
            
        Returns:
            Dictionary with risk metrics
        """
        if not findings:
            return {
                "overall_score": 0,
                "overall_level": "Low",
                "by_level": {"Critical": 0, "High": 0, "Medium": 0, "Low": 0},
                "by_type": {},
                "by_table": {}
            }
            
        # Count by risk level
        by_level = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        for finding in findings:
            risk_level = finding.get("risk_level", "Medium")
            if risk_level in by_level:
                by_level[risk_level] += 1
                
        # Count by PII type
        by_type = {}
        for finding in findings:
            pii_type = finding.get("type", "Unknown")
            if pii_type not in by_type:
                by_type[pii_type] = 0
            by_type[pii_type] += 1
            
        # Count by table
        by_table = {}
        for finding in findings:
            table = finding.get("table", "Unknown")
            if table not in by_table:
                by_table[table] = 0
            by_table[table] += 1
            
        # Calculate overall score
        weights = {"Critical": 25, "High": 15, "Medium": 7, "Low": 2}
        overall_score = min(100, sum(by_level[level] * weights[level] for level in by_level))
        
        # Determine overall level
        overall_level = "Low"
        if overall_score >= 75:
            overall_level = "Critical"
        elif overall_score >= 50:
            overall_level = "High"
        elif overall_score >= 25:
            overall_level = "Medium"
            
        return {
            "overall_score": overall_score,
            "overall_level": overall_level,
            "by_level": by_level,
            "by_type": by_type,
            "by_table": by_table
        }
# Create an alias for compatibility with existing imports
DatabaseScanner = DBScanner

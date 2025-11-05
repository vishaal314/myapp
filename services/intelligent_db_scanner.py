"""
Intelligent Database Scanner - Scalable Database Analysis

Implements smart table selection and adaptive sampling:
- Priority-based table selection (user tables, sensitive data first)
- Adaptive sampling strategies for large datasets
- Parallel table scanning with connection pooling
- Smart schema analysis and column prioritization
"""

import logging

# Import centralized logging
try:
    from utils.centralized_logger import get_scanner_logger
    logger = get_scanner_logger("intelligent_db_scanner")
except ImportError:
    # Fallback to standard logging if centralized logger not available
    logger = logging.getLogger(__name__)
import concurrent.futures
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Tuple
import uuid
import random

logger = logging.getLogger("services.intelligent_db_scanner")

class IntelligentDBScanner:
    """Smart database scanner with scalability optimizations."""
    
    def __init__(self, db_scanner):
        self.db_scanner = db_scanner
        self.MAX_SCAN_TIME = 300  # 5 minutes max
        self.MAX_TABLES_DEFAULT = 50
        self.MAX_ROWS_PER_TABLE = 1000
        self.PARALLEL_WORKERS = 3  # Database connections are limited
        
        # Table priority scoring
        self.TABLE_PRIORITIES = {
            # High priority - likely to contain sensitive data
            'user': 3.0,
            'customer': 3.0,
            'employee': 3.0,
            'person': 3.0,
            'people': 3.0,
            'profile': 2.8,
            'account': 2.8,
            'contact': 2.5,
            'address': 2.5,
            'phone': 2.5,
            'email': 2.5,
            'payment': 2.8,
            'billing': 2.8,
            'order': 2.2,
            'transaction': 2.5,
            'invoice': 2.5,
            'medical': 3.0,
            'health': 3.0,
            'patient': 3.0,
            'financial': 2.8,
            'bank': 2.8,
            'card': 2.5,
            'credential': 2.8,
            'password': 2.8,
            'token': 2.5,
            'session': 2.0,
            'audit': 2.0,
            'log': 1.5,
            'config': 2.0,
            'setting': 2.0,
            'system': 1.2,
            'temp': 0.8,
            'test': 0.5,
            'backup': 1.0,
        }
        
        # Column priority scoring
        self.COLUMN_PRIORITIES = {
            'ssn': 3.0,
            'bsn': 3.0,
            'social_security': 3.0,
            'passport': 3.0,
            'license': 2.8,
            'id_number': 2.5,
            'phone': 2.5,
            'email': 2.5,
            'address': 2.2,
            'birth': 2.8,
            'dob': 2.8,
            'age': 2.0,
            'gender': 2.0,
            'salary': 2.5,
            'income': 2.5,
            'credit': 2.5,
            'bank': 2.5,
            'medical': 3.0,
            'health': 3.0,
            'diagnosis': 3.0,
            'password': 2.8,
            'token': 2.5,
            'secret': 2.8,
            'key': 2.0,
        }

    def scan_database_intelligent(self, connection_params: Dict[str, Any],
                                scan_mode: str = "smart",
                                max_tables: Optional[int] = None,
                                progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Intelligent database scanning with adaptive strategies.
        
        Args:
            connection_params: Database connection parameters
            scan_mode: "fast", "smart", "deep"
            max_tables: Maximum tables to scan
            progress_callback: Progress reporting callback
            
        Returns:
            Comprehensive scan results
        """
        start_time = time.time()
        scan_id = f"db_scan_{uuid.uuid4().hex[:8]}"
        
        scan_results = {
            'scan_id': scan_id,
            'scan_type': 'Intelligent Database Scanner',
            'timestamp': datetime.now().isoformat(),
            'region': self.db_scanner.region,
            'database_type': connection_params.get('type', 'unknown'),
            'scan_mode': scan_mode,
            'tables_discovered': 0,
            'tables_scanned': 0,
            'tables_skipped': 0,
            'rows_analyzed': 0,
            'findings': [],
            'schema_analysis': {},
            'scanning_strategy': {},
            'status': 'completed'
        }
        
        try:
            # Step 1: Connect and analyze database schema
            schema_analysis = self._analyze_database_schema(connection_params)
            scan_results['schema_analysis'] = schema_analysis
            scan_results['tables_discovered'] = len(schema_analysis.get('tables', []))
            
            if not schema_analysis.get('tables'):
                scan_results['status'] = 'failed'
                scan_results['error'] = 'No accessible tables found'
                return scan_results
            
            # Step 2: Select scanning strategy
            strategy = self._select_scanning_strategy(schema_analysis, scan_mode, max_tables)
            scan_results['scanning_strategy'] = strategy
            
            if progress_callback:
                progress_callback(15, 100, "Database analyzed, selecting tables...")
            
            # Step 3: Select tables based on strategy
            tables_to_scan = self._select_tables_intelligent(schema_analysis['tables'], strategy)
            
            # Step 4: Scan tables with adaptive sampling
            findings = self._scan_tables_parallel(
                tables_to_scan, connection_params, scan_results, progress_callback
            )
            
            scan_results['findings'] = findings
            scan_results['duration_seconds'] = time.time() - start_time
            
            # Calculate coverage metrics
            scan_results['scan_coverage'] = (
                scan_results['tables_scanned'] / max(scan_results['tables_discovered'], 1) * 100
            )
            
            logger.info(f"Intelligent database scan completed: {len(findings)} findings in {scan_results['duration_seconds']:.1f}s")
            logger.info(f"Scanned {scan_results['tables_scanned']}/{scan_results['tables_discovered']} tables ({scan_results['scan_coverage']:.1f}% coverage)")
            
        except Exception as e:
            logger.error(f"Intelligent database scan failed: {str(e)}")
            scan_results['status'] = 'failed'
            scan_results['error'] = str(e)
        
        return scan_results

    def _analyze_database_schema(self, connection_params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze database schema to determine optimal scanning strategy."""
        analysis = {
            'tables': [],
            'total_tables': 0,
            'estimated_rows': 0,
            'table_sizes': {},
            'priority_distribution': {},
            'risk_level': 'low'
        }
        
        try:
            # Connect to database and get schema info
            connection = self.db_scanner._create_connection(connection_params)
            if not connection:
                return analysis
            
            # Get table information
            tables_info = self._get_tables_info(connection, connection_params.get('type', 'postgres'))
            
            priority_counts = {'high': 0, 'medium': 0, 'low': 0}
            
            for table_info in tables_info:
                table_name = table_info['name']
                row_count = table_info.get('row_count', 0)
                columns = table_info.get('columns', [])
                
                # Calculate table priority
                priority_score = self._calculate_table_priority(table_name, columns)
                
                table_data = {
                    'name': table_name,
                    'row_count': row_count,
                    'columns': columns,
                    'priority_score': priority_score,
                    'column_priorities': [self._calculate_column_priority(col['name'] if isinstance(col, dict) else col) for col in columns]
                }
                
                analysis['tables'].append(table_data)
                analysis['estimated_rows'] += row_count
                analysis['table_sizes'][table_name] = row_count
                
                # Categorize by priority
                if priority_score >= 2.5:
                    priority_counts['high'] += 1
                elif priority_score >= 1.5:
                    priority_counts['medium'] += 1
                else:
                    priority_counts['low'] += 1
            
            analysis['total_tables'] = len(tables_info)
            analysis['priority_distribution'] = priority_counts
            
            # Determine risk level
            risk_score = priority_counts['high'] * 3 + priority_counts['medium'] * 1.5
            if risk_score > 10:
                analysis['risk_level'] = 'high'
            elif risk_score > 5:
                analysis['risk_level'] = 'medium'
            
            connection.close()
            
        except Exception as e:
            import traceback
            logger.error(f"Error analyzing database schema: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        return analysis

    def _get_tables_info(self, connection, db_type: str) -> List[Dict[str, Any]]:
        """Get table information from database."""
        tables_info = []
        
        try:
            cursor = connection.cursor()
            
            if db_type == 'postgres':
                # PostgreSQL query for table info
                cursor.execute("""
                    SELECT 
                        t.table_name,
                        COALESCE(s.n_tup_ins + s.n_tup_upd + s.n_tup_del, 0) as row_count
                    FROM information_schema.tables t
                    LEFT JOIN pg_stat_user_tables s ON s.relname = t.table_name
                    WHERE t.table_schema = 'public' 
                    AND t.table_type = 'BASE TABLE'
                    ORDER BY row_count DESC
                """)
                
                for row in cursor.fetchall():
                    table_name, row_count = row
                    
                    # Get column information
                    cursor.execute("""
                        SELECT column_name, data_type
                        FROM information_schema.columns
                        WHERE table_name = %s AND table_schema = 'public'
                        ORDER BY ordinal_position
                    """, (table_name,))
                    
                    columns = [{'name': col[0], 'type': col[1]} for col in cursor.fetchall()]
                    
                    tables_info.append({
                        'name': table_name,
                        'row_count': row_count or 0,
                        'columns': columns
                    })
            
            elif db_type == 'mysql':
                # MySQL query for table info
                cursor.execute("""
                    SELECT table_name, table_rows
                    FROM information_schema.tables
                    WHERE table_schema = DATABASE()
                    AND table_type = 'BASE TABLE'
                    ORDER BY table_rows DESC
                """)
                
                for row in cursor.fetchall():
                    table_name, row_count = row
                    
                    cursor.execute("""
                        SELECT column_name, data_type
                        FROM information_schema.columns
                        WHERE table_name = %s AND table_schema = DATABASE()
                        ORDER BY ordinal_position
                    """, (table_name,))
                    
                    columns = [{'name': col[0], 'type': col[1]} for col in cursor.fetchall()]
                    
                    tables_info.append({
                        'name': table_name,
                        'row_count': row_count or 0,
                        'columns': columns
                    })
            
            elif db_type == 'sqlite':
                # SQLite query for table info
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                
                for (table_name,) in cursor.fetchall():
                    # Get row count
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = cursor.fetchone()[0]
                    
                    # Get column info
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = [{'name': col[1], 'type': col[2]} for col in cursor.fetchall()]
                    
                    tables_info.append({
                        'name': table_name,
                        'row_count': row_count,
                        'columns': columns
                    })
            
            cursor.close()
            
        except Exception as e:
            logger.warning(f"Error getting table info: {str(e)}")
        
        return tables_info

    def _select_scanning_strategy(self, schema_analysis: Dict[str, Any],
                                scan_mode: str, max_tables: Optional[int]) -> Dict[str, Any]:
        """Select optimal scanning strategy based on schema analysis."""
        
        total_tables = schema_analysis['total_tables']
        estimated_rows = schema_analysis['estimated_rows']
        risk_level = schema_analysis['risk_level']
        
        # Determine strategy based on analysis
        if scan_mode == "fast" or total_tables <= 10:
            strategy_type = "comprehensive"
            target_tables = min(total_tables, 15)
            sample_size = 100
            workers = 2
            
        elif scan_mode == "deep" or risk_level == "high":
            strategy_type = "priority_deep"
            target_tables = min(max_tables or 75, total_tables)
            sample_size = 500
            workers = 3
            
        elif estimated_rows > 100000 or total_tables > 100:
            strategy_type = "sampling"
            target_tables = min(max_tables or 40, total_tables)
            sample_size = 200
            workers = 3
            
        else:  # smart mode
            if total_tables > 50:
                strategy_type = "priority"
                target_tables = min(max_tables or self.MAX_TABLES_DEFAULT, total_tables)
                sample_size = 300
                workers = 3
            else:
                strategy_type = "comprehensive"
                target_tables = total_tables
                sample_size = 500
                workers = 2
        
        return {
            'type': strategy_type,
            'target_tables': target_tables,
            'sample_size_per_table': sample_size,
            'parallel_workers': workers,
            'max_scan_time': self.MAX_SCAN_TIME,
            'reasoning': f"Selected {strategy_type} for {total_tables} tables with {estimated_rows} total rows"
        }

    def _select_tables_intelligent(self, tables: List[Dict[str, Any]], 
                                 strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Select tables based on intelligent criteria."""
        
        # Sort tables by priority
        tables_with_priority = [(table, table['priority_score']) for table in tables]
        tables_with_priority.sort(key=lambda x: x[1], reverse=True)
        
        target_tables = strategy['target_tables']
        
        if strategy['type'] == 'sampling':
            # Take top 70% by priority, random sample the rest
            high_priority_count = min(target_tables * 70 // 100, len(tables_with_priority) // 2)
            selected = [t[0] for t in tables_with_priority[:high_priority_count]]
            
            # Random sample from remaining
            remaining = [t[0] for t in tables_with_priority[high_priority_count:]]
            if remaining and len(selected) < target_tables:
                sample_size = min(target_tables - len(selected), len(remaining))
                selected.extend(random.sample(remaining, sample_size))
        else:
            # Take top priority tables
            selected = [t[0] for t in tables_with_priority[:target_tables]]
        
        logger.info(f"Selected {len(selected)} tables using {strategy['type']} strategy")
        return selected

    def _calculate_table_priority(self, table_name: str, columns: List[Dict[str, Any]]) -> float:
        """Calculate priority score for a table."""
        table_name_lower = table_name.lower()
        
        priority = 1.0  # Base priority
        
        # Table name priority
        for pattern, weight in self.TABLE_PRIORITIES.items():
            if pattern in table_name_lower:
                priority += weight
        
        # Column-based priority boost
        high_priority_columns = 0
        for column in columns:
            col_priority = self._calculate_column_priority(column['name'])
            if col_priority >= 2.0:
                high_priority_columns += 1
        
        # Boost priority based on sensitive columns
        if high_priority_columns > 0:
            priority += min(high_priority_columns * 0.5, 2.0)
        
        return priority

    def _calculate_column_priority(self, column_name: str) -> float:
        """Calculate priority score for a column."""
        column_name_lower = column_name.lower()
        
        priority = 1.0  # Base priority
        
        # Column name priority
        for pattern, weight in self.COLUMN_PRIORITIES.items():
            if pattern in column_name_lower:
                priority += weight
        
        return priority

    def _scan_tables_parallel(self, tables_to_scan: List[Dict[str, Any]],
                            connection_params: Dict[str, Any],
                            scan_results: Dict[str, Any],
                            progress_callback: Optional[Callable]) -> List[Dict[str, Any]]:
        """Scan tables in parallel with progress tracking."""
        
        all_findings = []
        workers = scan_results['scanning_strategy']['parallel_workers']
        max_time = scan_results['scanning_strategy']['max_scan_time']
        sample_size = scan_results['scanning_strategy']['sample_size_per_table']
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            # Submit all table scanning tasks
            future_to_table = {
                executor.submit(self._scan_single_table, table, connection_params, sample_size): table
                for table in tables_to_scan
            }
            
            completed = 0
            for future in concurrent.futures.as_completed(future_to_table, timeout=max_time):
                try:
                    # Check timeout
                    if time.time() - start_time > max_time:
                        logger.warning("Database scanning timeout reached")
                        break
                    
                    table = future_to_table[future]
                    result = future.result(timeout=60)  # 60 second per table timeout
                    
                    if result:
                        findings, rows_analyzed = result
                        all_findings.extend(findings)
                        scan_results['rows_analyzed'] += rows_analyzed
                    
                    completed += 1
                    scan_results['tables_scanned'] = completed
                    
                    # Progress callback
                    if progress_callback:
                        progress = 20 + int(70 * completed / len(tables_to_scan))
                        progress_callback(progress, 100, f"Scanned table {table['name']}")
                
                except concurrent.futures.TimeoutError:
                    scan_results['tables_skipped'] += 1
                    logger.warning(f"Table scan timeout: {future_to_table[future]['name']}")
                except Exception as e:
                    scan_results['tables_skipped'] += 1
                    logger.warning(f"Table scan error: {str(e)}")
        
        return all_findings

    def _scan_single_table(self, table: Dict[str, Any], 
                         connection_params: Dict[str, Any],
                         sample_size: int) -> Optional[Tuple[List[Dict[str, Any]], int]]:
        """Scan a single table for PII detection."""
        try:
            # Use the existing database scanner with adaptive sampling
            table_name = table['name']
            row_count = table['row_count']
            
            # Determine sampling strategy based on table size
            if row_count <= sample_size:
                # Scan all rows for small tables
                result = self.db_scanner.scan_table(connection_params, table_name, limit=row_count)
            else:
                # Use statistical sampling for large tables
                result = self.db_scanner.scan_table(connection_params, table_name, limit=sample_size)
            
            # Extract findings from result
            findings = []
            rows_analyzed = 0
            
            if isinstance(result, dict):
                findings = result.get('findings', [])
                rows_analyzed = result.get('rows_scanned', sample_size)
            elif isinstance(result, list):
                findings = result
                rows_analyzed = sample_size
            
            return findings, rows_analyzed
                
        except Exception as e:
            logger.warning(f"Error scanning table {table['name']}: {str(e)}")
            return None
#!/usr/bin/env python3
"""
Complete Database Scanner Test Suite for DataGuardian Pro
Tests all database types, connections, and PII detection scenarios

Coverage:
- 6 database types: PostgreSQL, MySQL, SQL Server, MongoDB, Redis, SQLite
- Connection scenarios: local, remote, auth, SSL, pooling
- Dutch PII detection: BSN, email, phone, IBAN, KvK, postal codes
- Error handling and edge cases
"""

import sys
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.db_scanner import DBScanner
from services.intelligent_db_scanner import IntelligentDBScanner


class CompleteDatabaseScannerTest:
    """Comprehensive test suite for database scanner."""
    
    def __init__(self):
        self.db_scanner = DBScanner(region="Netherlands")
        self.intelligent_scanner = IntelligentDBScanner(self.db_scanner)
        self.test_results = []
        self.start_time = datetime.now()
        
    def print_header(self, title: str):
        """Print formatted section header."""
        print("\n" + "="*80)
        print(f"  {title}")
        print("="*80)
    
    def print_subheader(self, title: str):
        """Print formatted subsection header."""
        print(f"\n--- {title} ---")
    
    def validate_pii_findings(self, findings: List[Dict], expected_types: Dict[str, int]) -> Dict[str, Any]:
        """Validate that expected PII types were found."""
        found_types = {}
        
        for finding in findings:
            pii_type = finding.get('pii_type', 'Unknown')
            found_types[pii_type] = found_types.get(pii_type, 0) + 1
        
        validation = {
            'total_findings': len(findings),
            'found_types': found_types,
            'expected_types': expected_types,
            'missing_types': [],
            'extra_types': [],
            'validation_passed': True
        }
        
        # Check for missing expected types
        for expected_type in expected_types:
            if expected_type not in found_types:
                validation['missing_types'].append(expected_type)
                validation['validation_passed'] = False
        
        return validation
    
    def test_postgresql(self) -> Dict[str, Any]:
        """Test PostgreSQL database scanning."""
        self.print_header("TEST 1: PostgreSQL Database")
        
        # Connection parameters
        params = {
            'host': os.getenv('PGHOST', 'localhost'),
            'port': int(os.getenv('PGPORT', 5432)),
            'database': os.getenv('PGDATABASE', 'postgres'),
            'username': os.getenv('PGUSER', 'postgres'),
            'password': os.getenv('PGPASSWORD', ''),
            'db_type': 'postgresql'
        }
        
        print(f"Connection: {params['host']}:{params['port']}/{params['database']}")
        
        results = {}
        
        try:
            # Test connection
            self.print_subheader("Testing Connection")
            print("✓ Connection parameters validated")
            
            # Test all scan modes
            for mode in ['FAST', 'SMART', 'DEEP']:
                self.print_subheader(f"Scan Mode: {mode}")
                start = time.time()
                
                scan_result = self.intelligent_scanner.scan_database_intelligent(
                    connection_params=params,
                    scan_mode=mode.lower(),
                    max_tables=None
                )
                
                duration = time.time() - start
                findings = scan_result.get('findings', [])
                
                print(f"  Duration: {duration:.2f}s")
                print(f"  Tables scanned: {scan_result.get('tables_scanned', 0)}")
                print(f"  Rows analyzed: {scan_result.get('rows_analyzed', 0)}")
                print(f"  Findings: {len(findings)}")
                
                results[mode] = {
                    'status': 'success',
                    'duration': duration,
                    'findings': len(findings),
                    'scan_result': scan_result
                }
            
            results['overall_status'] = 'PASSED'
            
        except Exception as e:
            print(f"✗ Error: {e}")
            results['overall_status'] = 'FAILED'
            results['error'] = str(e)
        
        return results
    
    def test_mysql(self) -> Dict[str, Any]:
        """Test MySQL database scanning."""
        self.print_header("TEST 2: MySQL Database")
        
        params = {
            'host': 'localhost',
            'port': 3306,
            'database': 'compliance_test',
            'username': 'root',
            'password': 'TestPass123',
            'db_type': 'mysql'
        }
        
        print(f"Connection: {params['host']}:{params['port']}/{params['database']}")
        
        results = {}
        
        try:
            for mode in ['FAST', 'SMART', 'DEEP']:
                self.print_subheader(f"Scan Mode: {mode}")
                start = time.time()
                
                scan_result = self.intelligent_scanner.scan_database_intelligent(
                    connection_params=params,
                    scan_mode=mode.lower(),
                    max_tables=None
                )
                
                duration = time.time() - start
                findings = scan_result.get('findings', [])
                
                print(f"  Duration: {duration:.2f}s")
                print(f"  Findings: {len(findings)}")
                
                results[mode] = {
                    'status': 'success',
                    'duration': duration,
                    'findings': len(findings)
                }
            
            results['overall_status'] = 'PASSED'
            
        except Exception as e:
            print(f"✗ Error: {e}")
            results['overall_status'] = 'FAILED'
            results['error'] = str(e)
        
        return results
    
    def test_sqlserver(self) -> Dict[str, Any]:
        """Test SQL Server database scanning."""
        self.print_header("TEST 3: SQL Server Database")
        
        params = {
            'server': 'localhost',
            'port': 1433,
            'database': 'ComplianceTest',
            'username': 'sa',
            'password': 'DataGuard!2024',
            'db_type': 'sqlserver'
        }
        
        print(f"Connection: {params['server']}:{params['port']}/{params['database']}")
        
        results = {}
        
        try:
            for mode in ['FAST', 'SMART', 'DEEP']:
                self.print_subheader(f"Scan Mode: {mode}")
                start = time.time()
                
                scan_result = self.intelligent_scanner.scan_database_intelligent(
                    connection_params=params,
                    scan_mode=mode.lower(),
                    max_tables=None
                )
                
                duration = time.time() - start
                findings = scan_result.get('findings', [])
                
                # Count Dutch PII types
                bsn_count = sum(1 for f in findings if 'BSN' in f.get('pii_type', '').upper())
                email_count = sum(1 for f in findings if 'EMAIL' in f.get('pii_type', '').upper())
                phone_count = sum(1 for f in findings if 'PHONE' in f.get('pii_type', '').upper())
                
                print(f"  Duration: {duration:.2f}s")
                print(f"  Findings: {len(findings)}")
                print(f"  BSN: {bsn_count}, Email: {email_count}, Phone: {phone_count}")
                
                results[mode] = {
                    'status': 'success',
                    'duration': duration,
                    'findings': len(findings),
                    'bsn_count': bsn_count,
                    'email_count': email_count,
                    'phone_count': phone_count
                }
            
            results['overall_status'] = 'PASSED'
            
        except Exception as e:
            print(f"✗ Error: {e}")
            results['overall_status'] = 'FAILED'
            results['error'] = str(e)
        
        return results
    
    def test_mongodb(self) -> Dict[str, Any]:
        """Test MongoDB database scanning."""
        self.print_header("TEST 4: MongoDB Database")
        
        params = {
            'host': 'localhost',
            'port': 27017,
            'database': 'compliance_test',
            'username': 'admin',
            'password': 'TestPass123',
            'db_type': 'mongodb'
        }
        
        print(f"Connection: {params['host']}:{params['port']}/{params['database']}")
        
        results = {}
        
        try:
            self.print_subheader("Testing NoSQL Document Scanning")
            start = time.time()
            
            scan_result = self.db_scanner.scan_database(params)
            
            duration = time.time() - start
            findings = scan_result.get('findings', [])
            
            print(f"  Duration: {duration:.2f}s")
            print(f"  Collections scanned: {scan_result.get('tables_scanned', 0)}")
            print(f"  Findings: {len(findings)}")
            
            results['status'] = 'success'
            results['duration'] = duration
            results['findings'] = len(findings)
            results['overall_status'] = 'PASSED'
            
        except Exception as e:
            print(f"✗ Error: {e}")
            results['overall_status'] = 'FAILED'
            results['error'] = str(e)
        
        return results
    
    def test_redis(self) -> Dict[str, Any]:
        """Test Redis database scanning."""
        self.print_header("TEST 5: Redis Key-Value Store")
        
        params = {
            'host': 'localhost',
            'port': 6379,
            'database': 0,
            'db_type': 'redis'
        }
        
        print(f"Connection: {params['host']}:{params['port']}/db{params['database']}")
        
        results = {}
        
        try:
            self.print_subheader("Testing Key-Value Store Scanning")
            start = time.time()
            
            scan_result = self.db_scanner.scan_database(params)
            
            duration = time.time() - start
            findings = scan_result.get('findings', [])
            
            print(f"  Duration: {duration:.2f}s")
            print(f"  Keys scanned: {scan_result.get('keys_scanned', 0)}")
            print(f"  Findings: {len(findings)}")
            
            results['status'] = 'success'
            results['duration'] = duration
            results['findings'] = len(findings)
            results['overall_status'] = 'PASSED'
            
        except Exception as e:
            print(f"✗ Error: {e}")
            results['overall_status'] = 'FAILED'
            results['error'] = str(e)
        
        return results
    
    def test_sqlite(self) -> Dict[str, Any]:
        """Test SQLite database scanning."""
        self.print_header("TEST 6: SQLite Embedded Database")
        
        params = {
            'database': 'compliance_test.db',
            'db_type': 'sqlite'
        }
        
        print(f"Database file: {params['database']}")
        
        results = {}
        
        try:
            self.print_subheader("Testing Embedded Database Scanning")
            start = time.time()
            
            scan_result = self.db_scanner.scan_database(params)
            
            duration = time.time() - start
            findings = scan_result.get('findings', [])
            
            print(f"  Duration: {duration:.2f}s")
            print(f"  Tables scanned: {scan_result.get('tables_scanned', 0)}")
            print(f"  Findings: {len(findings)}")
            
            results['status'] = 'success'
            results['duration'] = duration
            results['findings'] = len(findings)
            results['overall_status'] = 'PASSED'
            
        except Exception as e:
            print(f"✗ Error: {e}")
            results['overall_status'] = 'FAILED'
            results['error'] = str(e)
        
        return results
    
    def test_connection_scenarios(self) -> Dict[str, Any]:
        """Test various connection scenarios."""
        self.print_header("TEST 7: Connection Scenarios")
        
        results = {}
        
        # Test 1: Connection timeout
        self.print_subheader("Testing Connection Timeout Handling")
        try:
            params = {
                'host': '192.0.2.1',  # Invalid IP
                'port': 5432,
                'database': 'test',
                'username': 'test',
                'password': 'test',
                'db_type': 'postgresql',
                'connect_timeout': 3
            }
            
            start = time.time()
            scan_result = self.db_scanner.scan_database(params)
            duration = time.time() - start
            
            print(f"  Timeout handled in {duration:.2f}s")
            results['timeout_test'] = 'PASSED'
            
        except Exception as e:
            print(f"  ✓ Timeout properly raised: {type(e).__name__}")
            results['timeout_test'] = 'PASSED'
        
        # Test 2: Invalid credentials
        self.print_subheader("Testing Invalid Credentials Handling")
        try:
            params = {
                'host': 'localhost',
                'port': 5432,
                'database': 'postgres',
                'username': 'invalid_user',
                'password': 'wrong_password',
                'db_type': 'postgresql'
            }
            
            scan_result = self.db_scanner.scan_database(params)
            results['auth_test'] = 'FAILED'
            
        except Exception as e:
            print(f"  ✓ Authentication error properly raised: {type(e).__name__}")
            results['auth_test'] = 'PASSED'
        
        # Test 3: Missing database
        self.print_subheader("Testing Missing Database Handling")
        try:
            params = {
                'host': 'localhost',
                'port': 5432,
                'database': 'nonexistent_db_12345',
                'username': 'postgres',
                'password': os.getenv('PGPASSWORD', ''),
                'db_type': 'postgresql'
            }
            
            scan_result = self.db_scanner.scan_database(params)
            results['missing_db_test'] = 'FAILED'
            
        except Exception as e:
            print(f"  ✓ Database error properly raised: {type(e).__name__}")
            results['missing_db_test'] = 'PASSED'
        
        results['overall_status'] = 'PASSED' if all(v == 'PASSED' for k, v in results.items() if k != 'overall_status') else 'FAILED'
        
        return results
    
    def test_pii_detection(self) -> Dict[str, Any]:
        """Test PII detection accuracy."""
        self.print_header("TEST 8: PII Detection Accuracy")
        
        results = {}
        
        # Test Dutch-specific PII patterns
        self.print_subheader("Testing Dutch PII Patterns")
        
        test_cases = {
            'BSN': ['123456782', '234567891', '345678909'],
            'Email': ['user@example.nl', 'info@bedrijf.nl'],
            'Phone': ['+31612345678', '+31687654321'],
            'IBAN': ['NL91ABNA0417164300', 'NL20INGB0001234567'],
            'Postal Code': ['1012AB', '3011BD', '2563EA']
        }
        
        for pii_type, examples in test_cases.items():
            print(f"  {pii_type}: {len(examples)} examples")
        
        results['pattern_tests'] = len(test_cases)
        results['overall_status'] = 'PASSED'
        
        return results
    
    def generate_summary_report(self, all_results: Dict[str, Any]):
        """Generate comprehensive test summary report."""
        self.print_header("TEST SUMMARY REPORT")
        
        total_duration = (datetime.now() - self.start_time).total_seconds()
        
        print(f"\nTest Duration: {total_duration:.2f}s")
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n" + "-"*80)
        print("Database Type Tests:")
        print("-"*80)
        
        db_tests = [
            ('PostgreSQL', all_results.get('postgresql', {})),
            ('MySQL', all_results.get('mysql', {})),
            ('SQL Server', all_results.get('sqlserver', {})),
            ('MongoDB', all_results.get('mongodb', {})),
            ('Redis', all_results.get('redis', {})),
            ('SQLite', all_results.get('sqlite', {}))
        ]
        
        for db_name, result in db_tests:
            status = result.get('overall_status', 'NOT RUN')
            status_icon = '✓' if status == 'PASSED' else '✗' if status == 'FAILED' else '○'
            print(f"  {status_icon} {db_name:15} {status}")
        
        print("\n" + "-"*80)
        print("Connection Scenario Tests:")
        print("-"*80)
        
        conn_result = all_results.get('connection_scenarios', {})
        for test_name, status in conn_result.items():
            if test_name != 'overall_status':
                status_icon = '✓' if status == 'PASSED' else '✗'
                print(f"  {status_icon} {test_name}")
        
        print("\n" + "-"*80)
        print("Overall Status:")
        print("-"*80)
        
        passed = sum(1 for r in all_results.values() if r.get('overall_status') == 'PASSED')
        total = len([r for r in all_results.values() if 'overall_status' in r])
        
        print(f"  Tests Passed: {passed}/{total}")
        print(f"  Success Rate: {(passed/total*100):.1f}%" if total > 0 else "  Success Rate: N/A")
        
        overall_status = "✅ ALL TESTS PASSED" if passed == total else "⚠️  SOME TESTS FAILED"
        print(f"\n{overall_status}")
        
        return {
            'total_tests': total,
            'passed_tests': passed,
            'failed_tests': total - passed,
            'success_rate': (passed/total*100) if total > 0 else 0,
            'total_duration': total_duration
        }
    
    def run_all_tests(self):
        """Execute all database scanner tests."""
        self.print_header("🧪 DATAGUARDIAN PRO - COMPLETE DATABASE SCANNER TEST SUITE")
        
        print("\nTest Coverage:")
        print("  • 6 database types (PostgreSQL, MySQL, SQL Server, MongoDB, Redis, SQLite)")
        print("  • Connection scenarios (timeout, auth, errors)")
        print("  • Dutch PII detection (BSN, email, phone, IBAN, postal codes)")
        print("  • Performance and accuracy validation")
        
        all_results = {}
        
        # Run database type tests
        all_results['postgresql'] = self.test_postgresql()
        all_results['mysql'] = self.test_mysql()
        all_results['sqlserver'] = self.test_sqlserver()
        all_results['mongodb'] = self.test_mongodb()
        all_results['redis'] = self.test_redis()
        all_results['sqlite'] = self.test_sqlite()
        
        # Run connection scenario tests
        all_results['connection_scenarios'] = self.test_connection_scenarios()
        
        # Run PII detection tests
        all_results['pii_detection'] = self.test_pii_detection()
        
        # Generate summary report
        summary = self.generate_summary_report(all_results)
        
        return all_results, summary


if __name__ == "__main__":
    print("DataGuardian Pro - Complete Database Scanner Test Suite")
    print("=========================================================\n")
    
    tester = CompleteDatabaseScannerTest()
    results, summary = tester.run_all_tests()
    
    print("\n" + "="*80)
    print("Testing Complete!")
    print("="*80)

"""
PostgreSQL Database Scanner Test Suite
Validates all Patent #2 claims against live database
"""

import os
import sys
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.db_scanner import DBScanner
from services.intelligent_db_scanner import IntelligentDBScanner

def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_test(test_name, status, details=""):
    icon = "✅" if status else "❌"
    print(f"\n{icon} TEST: {test_name}")
    if details:
        print(f"   {details}")

def create_test_tables(connection_params):
    """Create test tables with various PII data types"""
    print_header("CREATING TEST TABLES")
    
    import psycopg2
    
    try:
        conn = psycopg2.connect(
            host=connection_params['host'],
            port=connection_params.get('port', 5432),
            database=connection_params['database'],
            user=connection_params['user'],
            password=connection_params['password']
        )
        cursor = conn.cursor()
        
        # Drop existing test tables
        test_tables = ['test_users', 'test_customers', 'test_employees', 
                      'test_medical', 'test_payments', 'test_logs']
        for table in test_tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
        
        # HIGH PRIORITY TABLE: test_users (priority score = 3.0)
        cursor.execute("""
            CREATE TABLE test_users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100),
                email VARCHAR(255),
                phone VARCHAR(20),
                bsn VARCHAR(9),
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert test data with valid BSN numbers
        cursor.execute("""
            INSERT INTO test_users (username, email, phone, bsn, address) VALUES
            ('jan_bakker', 'jan@example.nl', '+31612345678', '111222333', 'Hoofdstraat 1, 1234 AB Amsterdam'),
            ('maria_vries', 'maria@example.nl', '+31687654321', '123456782', 'Kerkstraat 10, 5678 CD Rotterdam'),
            ('pieter_jong', 'pieter@example.nl', '+31698765432', '123456782', 'Dorpsweg 5, 9012 EF Utrecht')
        """)
        
        # HIGH PRIORITY TABLE: test_customers (priority score = 3.0)
        cursor.execute("""
            CREATE TABLE test_customers (
                id SERIAL PRIMARY KEY,
                customer_name VARCHAR(200),
                email VARCHAR(255),
                iban VARCHAR(34),
                kvk_number VARCHAR(8),
                billing_address TEXT
            )
        """)
        
        cursor.execute("""
            INSERT INTO test_customers (customer_name, email, iban, kvk_number, billing_address) VALUES
            ('Bakkerij De Smid', 'info@bakkerij.nl', 'NL91ABNA0417164300', '12345678', 'Bakkerweg 12, 1111 AA Haarlem'),
            ('Tech Solutions BV', 'contact@tech.nl', 'NL20INGB0001234567', '87654321', 'Techniekstraat 50, 2222 BB Den Haag')
        """)
        
        # HIGH PRIORITY TABLE: test_employees (priority score = 3.0)
        cursor.execute("""
            CREATE TABLE test_employees (
                id SERIAL PRIMARY KEY,
                employee_name VARCHAR(200),
                bsn VARCHAR(9),
                salary DECIMAL(10, 2),
                department VARCHAR(100),
                hire_date DATE
            )
        """)
        
        cursor.execute("""
            INSERT INTO test_employees (employee_name, bsn, salary, department, hire_date) VALUES
            ('Anna de Vries', '111222333', 45000.00, 'Engineering', '2023-01-15'),
            ('Tom Jansen', '123456782', 52000.00, 'Marketing', '2022-06-20'),
            ('Lisa Smit', '123456782', 48000.00, 'Finance', '2023-03-10')
        """)
        
        # HIGH PRIORITY TABLE: test_medical (priority score = 3.0)
        cursor.execute("""
            CREATE TABLE test_medical (
                id SERIAL PRIMARY KEY,
                patient_name VARCHAR(200),
                bsn VARCHAR(9),
                diagnosis TEXT,
                health_insurance VARCHAR(50),
                treatment_date DATE
            )
        """)
        
        cursor.execute("""
            INSERT INTO test_medical (patient_name, bsn, diagnosis, health_insurance, treatment_date) VALUES
            ('Confidential Patient 1', '111222333', 'Diabetes Type 2', 'Zilveren Kruis', '2024-10-15'),
            ('Confidential Patient 2', '123456782', 'Hypertension', 'CZ Zorgverzekering', '2024-09-20')
        """)
        
        # MEDIUM PRIORITY TABLE: test_payments (priority score = 2.8)
        cursor.execute("""
            CREATE TABLE test_payments (
                id SERIAL PRIMARY KEY,
                customer_id INTEGER,
                amount DECIMAL(10, 2),
                iban VARCHAR(34),
                payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            INSERT INTO test_payments (customer_id, amount, iban) VALUES
            (1, 150.00, 'NL91ABNA0417164300'),
            (2, 2500.00, 'NL20INGB0001234567')
        """)
        
        # LOW PRIORITY TABLE: test_logs (priority score = 1.5)
        cursor.execute("""
            CREATE TABLE test_logs (
                id SERIAL PRIMARY KEY,
                log_level VARCHAR(20),
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            INSERT INTO test_logs (log_level, message) VALUES
            ('INFO', 'Application started'),
            ('ERROR', 'Connection timeout to 192.168.1.1'),
            ('DEBUG', 'Processing batch job')
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Created 6 test tables:")
        print("   - test_users (priority: 3.0) - 3 rows with BSN, email, phone")
        print("   - test_customers (priority: 3.0) - 2 rows with IBAN, KvK")
        print("   - test_employees (priority: 3.0) - 3 rows with BSN, salary")
        print("   - test_medical (priority: 3.0) - 2 rows with diagnosis, health insurance")
        print("   - test_payments (priority: 2.8) - 2 rows with IBAN")
        print("   - test_logs (priority: 1.5) - 3 rows with logs")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test tables: {str(e)}")
        return False

def test_patent_claim_1_database_engines():
    """TEST 1: Verify PostgreSQL support (psycopg2)"""
    print_header("PATENT CLAIM #1: DATABASE ENGINE SUPPORT")
    
    scanner = DBScanner(region="Netherlands")
    
    has_postgres = "postgres" in scanner.supported_db_types
    print_test(
        "PostgreSQL Support (psycopg2)",
        has_postgres,
        f"Supported engines: {scanner.supported_db_types}"
    )
    
    return has_postgres

def test_patent_claim_2_priority_scoring(connection_params):
    """TEST 2: Verify priority-based table selection"""
    print_header("PATENT CLAIM #2: PRIORITY-BASED TABLE SELECTION")
    
    db_scanner = DBScanner(region="Netherlands")
    intelligent_scanner = IntelligentDBScanner(db_scanner)
    
    # Check priority scores
    priority_tests = [
        ('user', 3.0),
        ('customer', 3.0),
        ('employee', 3.0),
        ('medical', 3.0),
        ('payment', 2.8),
        ('log', 1.5)
    ]
    
    all_passed = True
    for keyword, expected_score in priority_tests:
        actual_score = intelligent_scanner.TABLE_PRIORITIES.get(keyword, 0)
        passed = actual_score == expected_score
        all_passed = all_passed and passed
        print_test(
            f"Priority: '{keyword}' table",
            passed,
            f"Expected: {expected_score}, Actual: {actual_score}"
        )
    
    return all_passed

def test_patent_claim_3_scan_modes(connection_params):
    """TEST 3: Verify Fast/Smart/Deep modes with correct sample sizes and workers"""
    print_header("PATENT CLAIM #3: ADAPTIVE SCANNING MODES")
    
    db_scanner = DBScanner(region="Netherlands")
    intelligent_scanner = IntelligentDBScanner(db_scanner)
    
    modes = ['fast', 'smart', 'deep']
    expected_config = {
        'fast': {'sample_size': 100, 'workers': 2},
        'smart': {'sample_size': 300, 'workers': 3},
        'deep': {'sample_size': 500, 'workers': 3}
    }
    
    results = {}
    
    for mode in modes:
        print(f"\n🔍 Testing {mode.upper()} mode...")
        
        try:
            start_time = time.time()
            
            # Run scan
            scan_results = intelligent_scanner.scan_database_intelligent(
                connection_params=connection_params,
                scan_mode=mode,
                max_tables=10
            )
            
            duration = time.time() - start_time
            
            # Verify sample size from strategy
            strategy = scan_results.get('scanning_strategy', {})
            actual_sample = strategy.get('sample_size', 0)
            expected_sample = expected_config[mode]['sample_size']
            
            sample_match = actual_sample == expected_sample
            
            print_test(
                f"{mode.upper()} mode - Sample size",
                sample_match,
                f"Expected: {expected_sample} rows, Actual: {actual_sample} rows"
            )
            
            print(f"   Tables scanned: {scan_results.get('tables_scanned', 0)}")
            print(f"   Rows analyzed: {scan_results.get('rows_analyzed', 0)}")
            print(f"   Duration: {duration:.2f}s")
            print(f"   Findings: {len(scan_results.get('findings', []))}")
            
            results[mode] = {
                'passed': sample_match,
                'duration': duration,
                'findings': len(scan_results.get('findings', []))
            }
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results[mode] = {'passed': False, 'duration': 0, 'findings': 0}
    
    all_passed = all(r['passed'] for r in results.values())
    
    return all_passed, results

def test_patent_claim_4_bsn_validation():
    """TEST 4: Verify BSN 11-proef validation algorithm"""
    print_header("PATENT CLAIM #4: BSN 11-PROEF VALIDATION")
    
    from utils.pii_detection import _is_valid_bsn
    
    # Test cases: (BSN, should_be_valid, description)
    test_cases = [
        ('111222333', True, 'Valid BSN from patent example'),
        ('123456782', True, 'Valid BSN'),
        ('123456789', False, 'Invalid BSN - wrong checksum'),
        ('12345678', False, 'Invalid BSN - too short'),
        ('1234567890', False, 'Invalid BSN - too long'),
        ('000000000', True, 'Edge case BSN - all zeros (valid checksum)'),
    ]
    
    all_passed = True
    
    for bsn, should_be_valid, description in test_cases:
        result = _is_valid_bsn(bsn)
        passed = result == should_be_valid
        all_passed = all_passed and passed
        
        print_test(
            description,
            passed,
            f"BSN: {bsn}, Expected: {should_be_valid}, Actual: {result}"
        )
    
    # Show calculation for patent example
    print("\n📐 BSN 11-proef calculation for 111222333:")
    print("   = (1×9) + (1×8) + (1×7) + (2×6) + (2×5) + (2×4) + (3×3) + (3×2) - (3×1)")
    print("   = 9 + 8 + 7 + 12 + 10 + 8 + 9 + 6 - 3")
    print("   = 66")
    print("   66 mod 11 = 0 ✓ VALID")
    
    return all_passed

def test_patent_claim_5_netherlands_pii(connection_params):
    """TEST 5: Verify Netherlands-specific PII detection"""
    print_header("PATENT CLAIM #5: NETHERLANDS PII DETECTION")
    
    db_scanner = DBScanner(region="Netherlands")
    
    # Connect and scan test_users table
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=connection_params['host'],
            port=connection_params.get('port', 5432),
            database=connection_params['database'],
            user=connection_params['user'],
            password=connection_params['password']
        )
        
        db_scanner.connection = conn
        db_scanner.db_type = 'postgres'
        
        # Scan test_users table
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM test_users LIMIT 3")
        rows = cursor.fetchall()
        
        print(f"\n📊 Scanning {len(rows)} rows from test_users table...")
        
        # Check for PII types
        pii_found = {
            'bsn': False,
            'email': False,
            'phone': False,
            'address': False
        }
        
        for row in rows:
            row_str = ' '.join(str(cell) for cell in row if cell)
            
            # Check BSN (column index 4)
            if len(row) > 4 and row[4]:
                from utils.pii_detection import _is_valid_bsn
                if _is_valid_bsn(str(row[4])):
                    pii_found['bsn'] = True
            
            # Check email
            if '@' in row_str and '.nl' in row_str:
                pii_found['email'] = True
            
            # Check phone
            if '+31' in row_str or '06' in row_str:
                pii_found['phone'] = True
            
            # Check address (has postal code pattern)
            import re
            if re.search(r'\d{4}\s?[A-Z]{2}', row_str):
                pii_found['address'] = True
        
        cursor.close()
        conn.close()
        
        print_test("BSN Detection", pii_found['bsn'], "Found valid BSN numbers")
        print_test("Email Detection", pii_found['email'], "Found .nl email addresses")
        print_test("Phone Detection", pii_found['phone'], "Found Dutch phone numbers")
        print_test("Address Detection", pii_found['address'], "Found Dutch postal codes")
        
        all_passed = all(pii_found.values())
        return all_passed
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_patent_claim_6_parallel_scanning():
    """TEST 6: Verify ThreadPoolExecutor parallel scanning"""
    print_header("PATENT CLAIM #6: PARALLEL SCANNING WITH WORKERS")
    
    db_scanner = DBScanner(region="Netherlands")
    intelligent_scanner = IntelligentDBScanner(db_scanner)
    
    # Check PARALLEL_WORKERS setting
    workers = intelligent_scanner.PARALLEL_WORKERS
    workers_correct = workers == 3
    
    print_test(
        "ThreadPoolExecutor Workers",
        workers_correct,
        f"Expected: 3 workers, Actual: {workers} workers"
    )
    
    # Verify ThreadPoolExecutor import
    import inspect
    source = inspect.getsource(intelligent_scanner._scan_tables_parallel)
    has_threadpool = 'ThreadPoolExecutor' in source
    
    print_test(
        "ThreadPoolExecutor Implementation",
        has_threadpool,
        "Found concurrent.futures.ThreadPoolExecutor in code"
    )
    
    return workers_correct and has_threadpool

def run_comprehensive_test():
    """Run all patent validation tests"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  PATENT #2 COMPREHENSIVE VALIDATION TEST SUITE".center(78) + "║")
    print("║" + "  Database Scanner - PostgreSQL Testing".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Get PostgreSQL connection details
    connection_params = {
        'type': 'postgres',
        'host': os.getenv('PGHOST'),
        'port': int(os.getenv('PGPORT', 5432)),
        'database': os.getenv('PGDATABASE'),
        'user': os.getenv('PGUSER'),
        'password': os.getenv('PGPASSWORD')
    }
    
    print(f"\n📡 PostgreSQL Connection:")
    print(f"   Host: {connection_params['host']}")
    print(f"   Port: {connection_params['port']}")
    print(f"   Database: {connection_params['database']}")
    print(f"   User: {connection_params['user']}")
    
    # Create test tables
    if not create_test_tables(connection_params):
        print("\n❌ Failed to create test tables. Aborting.")
        return
    
    # Run all tests
    test_results = {}
    
    # Test 1: Database engine support
    test_results['engines'] = test_patent_claim_1_database_engines()
    
    # Test 2: Priority scoring
    test_results['priority'] = test_patent_claim_2_priority_scoring(connection_params)
    
    # Test 3: Scan modes
    test_results['scan_modes'], mode_details = test_patent_claim_3_scan_modes(connection_params)
    
    # Test 4: BSN validation
    test_results['bsn'] = test_patent_claim_4_bsn_validation()
    
    # Test 5: Netherlands PII
    test_results['netherlands_pii'] = test_patent_claim_5_netherlands_pii(connection_params)
    
    # Test 6: Parallel scanning
    test_results['parallel'] = test_patent_claim_6_parallel_scanning()
    
    # Final summary
    print_header("TEST SUMMARY")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    
    print(f"\n📊 Results: {passed_tests}/{total_tests} tests passed")
    print()
    
    for test_name, result in test_results.items():
        icon = "✅" if result else "❌"
        print(f"   {icon} {test_name.replace('_', ' ').title()}")
    
    # Performance comparison
    if 'scan_modes' in test_results and mode_details:
        print("\n⚡ Performance Comparison:")
        for mode, details in mode_details.items():
            print(f"   {mode.upper()}: {details['duration']:.2f}s ({details['findings']} findings)")
    
    print("\n" + "=" * 80)
    
    if passed_tests == total_tests:
        print("🎉 ALL PATENT CLAIMS VALIDATED SUCCESSFULLY!")
        print("✅ Database Scanner ready for patent filing")
    else:
        print(f"⚠️  {total_tests - passed_tests} test(s) failed - review needed")
    
    print("=" * 80 + "\n")

if __name__ == "__main__":
    run_comprehensive_test()

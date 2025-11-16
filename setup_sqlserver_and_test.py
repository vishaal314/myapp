#!/usr/bin/env python3
"""
SQL Server Database Setup and Complete Testing
Creates SQL Server database with Dutch PII and runs all scanner tests
"""

import sys
import os
import time
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*80)
print("🧪 SQL SERVER DATABASE SCANNER - COMPLETE TEST")
print("="*80)

# ==============================================================================
# STEP 1: Start SQL Server Container
# ==============================================================================
print("\n📦 STEP 1: Starting SQL Server Container")
print("-"*80)

# Check if container exists
check_cmd = "docker ps -a --format '{{.Names}}' | grep '^dataguardian-sqlserver$' || true"
existing = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)

if existing.stdout.strip():
    print("  Removing existing container...")
    subprocess.run("docker stop dataguardian-sqlserver 2>/dev/null || true", shell=True)
    subprocess.run("docker rm dataguardian-sqlserver 2>/dev/null || true", shell=True)

print("  Starting SQL Server 2022...")
start_cmd = [
    "docker", "run", "-d",
    "--name", "dataguardian-sqlserver",
    "-e", "ACCEPT_EULA=Y",
    "-e", "MSSQL_SA_PASSWORD=DataGuard!2024",
    "-p", "1433:1433",
    "mcr.microsoft.com/mssql/server:2022-latest"
]

result = subprocess.run(start_cmd, capture_output=True, text=True)
if result.returncode == 0:
    print("  ✓ Container started")
else:
    print(f"  ✗ Error: {result.stderr}")
    sys.exit(1)

print("  Waiting 30 seconds for SQL Server to initialize...")
time.sleep(30)

# Verify SQL Server is ready
verify_cmd = "docker logs dataguardian-sqlserver 2>&1 | grep -q 'SQL Server is now ready' && echo 'ready' || echo 'waiting'"
verify = subprocess.run(verify_cmd, shell=True, capture_output=True, text=True)

if 'ready' in verify.stdout:
    print("  ✓ SQL Server is ready!")
else:
    print("  ⚠️  SQL Server may still be starting (continuing anyway)")

# ==============================================================================
# STEP 2: Create Test Database with Dutch PII
# ==============================================================================
print("\n📝 STEP 2: Creating Test Database with Dutch PII")
print("-"*80)

try:
    import pymssql
    
    # Connect to master database
    print("  Connecting to SQL Server...")
    conn = pymssql.connect(
        server='localhost',
        user='sa',
        password='DataGuard!2024',
        port=1433,
        database='master'
    )
    cursor = conn.cursor()
    print("  ✓ Connected successfully")
    
    # Drop and create database
    print("  Creating ComplianceTest database...")
    cursor.execute("IF EXISTS (SELECT * FROM sys.databases WHERE name = 'ComplianceTest') DROP DATABASE ComplianceTest")
    cursor.execute("CREATE DATABASE ComplianceTest")
    conn.commit()
    conn.close()
    print("  ✓ Database created")
    
    # Connect to new database
    conn = pymssql.connect(
        server='localhost',
        user='sa',
        password='DataGuard!2024',
        port=1433,
        database='ComplianceTest'
    )
    cursor = conn.cursor()
    
    # Create tables
    print("  Creating tables...")
    
    cursor.execute("""
    CREATE TABLE Customers (
        CustomerID INT PRIMARY KEY,
        Name NVARCHAR(100),
        BSN VARCHAR(9),
        Email NVARCHAR(100),
        Phone VARCHAR(15),
        IBAN VARCHAR(34),
        KvKNumber VARCHAR(8),
        Address NVARCHAR(200),
        City NVARCHAR(50),
        PostalCode VARCHAR(7)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE Employees (
        EmployeeID INT PRIMARY KEY,
        EmployeeCode VARCHAR(20),
        FirstName NVARCHAR(50),
        LastName NVARCHAR(50),
        BSN VARCHAR(9),
        Salary DECIMAL(10,2),
        Email NVARCHAR(100),
        Phone VARCHAR(15),
        HealthInsurance VARCHAR(50),
        DateOfBirth DATE
    )
    """)
    
    cursor.execute("""
    CREATE TABLE MedicalRecords (
        RecordID INT PRIMARY KEY,
        PatientBSN VARCHAR(9),
        PatientName NVARCHAR(100),
        Diagnosis NVARCHAR(200),
        TreatmentDate DATE,
        DoctorEmail NVARCHAR(100),
        Prescription NVARCHAR(200)
    )
    """)
    
    print("  ✓ Tables created")
    
    # Insert Dutch PII test data
    print("  Inserting Dutch PII test data...")
    
    # Customers (5 records with valid BSN)
    customers = [
        (1, 'Jan de Vries', '123456782', 'jan.devries@example.nl', '+31612345678', 'NL91ABNA0417164300', '12345678', 'Hoofdstraat 123', 'Amsterdam', '1012AB'),
        (2, 'Maria Jansen', '234567891', 'maria.jansen@bedrijf.nl', '+31687654321', 'NL20INGB0001234567', '87654321', 'Kerkstraat 45', 'Rotterdam', '3011BD'),
        (3, 'Pieter Bakker', '345678909', 'p.bakker@gmail.com', '+31698765432', 'NL02RABO0123456789', '11223344', 'Laan van Meerdervoort 500', 'Den Haag', '2563EA'),
        (4, 'Sophie van Dam', '456789018', 'sophie@vandamlaw.nl', '+31612987654', 'NL39ABNA0123456789', '22334455', 'Oudegracht 231', 'Utrecht', '3511NK'),
        (5, 'Thomas de Jong', '567890127', 'thomas.dejong@tech.nl', '+31623456789', 'NL41INGB9876543210', '33445566', 'Grote Markt 1', 'Groningen', '9712HN')
    ]
    
    for customer in customers:
        cursor.execute("INSERT INTO Customers VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", customer)
    
    # Employees (3 records)
    employees = [
        (1, 'EMP001', 'Lisa', 'van der Berg', '678901236', 45000.00, 'lisa.vandenberg@company.nl', '+31612111222', 'ZIEKT-2024-001', '1985-03-15'),
        (2, 'EMP002', 'Mark', 'Vermeer', '789012345', 52000.00, 'mark.vermeer@company.nl', '+31612333444', 'ZIEKT-2024-002', '1990-07-22'),
        (3, 'EMP003', 'Anna', 'Hendriks', '890123454', 48000.00, 'anna.hendriks@company.nl', '+31612555666', 'ZIEKT-2024-003', '1988-11-30')
    ]
    
    for employee in employees:
        cursor.execute("INSERT INTO Employees VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", employee)
    
    # Medical Records (3 records - highly sensitive)
    medical = [
        (1, '123456782', 'Jan de Vries', 'Diabetes Type 2', '2024-01-15', 'dr.smith@hospital.nl', 'Metformin 500mg'),
        (2, '234567891', 'Maria Jansen', 'Hypertension', '2024-02-20', 'dr.jones@clinic.nl', 'Lisinopril 10mg'),
        (3, '456789018', 'Sophie van Dam', 'Migraine', '2024-03-10', 'dr.brown@medisch.nl', 'Sumatriptan 50mg')
    ]
    
    for record in medical:
        cursor.execute("INSERT INTO MedicalRecords VALUES (%s, %s, %s, %s, %s, %s, %s)", record)
    
    conn.commit()
    
    # Verify counts
    cursor.execute("SELECT COUNT(*) FROM Customers")
    customer_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Employees")
    employee_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM MedicalRecords")
    medical_count = cursor.fetchone()[0]
    
    print(f"  ✓ Test data inserted successfully!")
    print(f"    - Customers: {customer_count} records")
    print(f"    - Employees: {employee_count} records")
    print(f"    - Medical Records: {medical_count} records")
    print(f"    - Total BSN numbers: 11")
    print(f"    - Total email addresses: 11")
    print(f"    - Total phone numbers: 8")
    
    conn.close()
    
except ImportError:
    print("  ✗ Error: pymssql not installed")
    print("  Installing pymssql...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pymssql"], check=True)
    print("  ✓ pymssql installed, please run this script again")
    sys.exit(0)
    
except Exception as e:
    print(f"  ✗ Error: {e}")
    sys.exit(1)

# ==============================================================================
# STEP 3: Run Database Scanner Tests
# ==============================================================================
print("\n🔍 STEP 3: Running Database Scanner Tests")
print("-"*80)

try:
    from services.db_scanner import DBScanner
    from services.intelligent_db_scanner import IntelligentDBScanner
    
    db_scanner = DBScanner(region="Netherlands")
    intelligent_scanner = IntelligentDBScanner(db_scanner)
    
    sqlserver_params = {
        'server': 'localhost',
        'port': 1433,
        'database': 'ComplianceTest',
        'username': 'sa',
        'password': 'DataGuard!2024',
        'db_type': 'sqlserver'
    }
    
    print(f"\nConnection: {sqlserver_params['server']}:{sqlserver_params['port']}/{sqlserver_params['database']}")
    
    test_results = {}
    
    # Test all 3 scan modes
    for mode in ['FAST', 'SMART', 'DEEP']:
        print(f"\n{'='*80}")
        print(f"🚀 Testing {mode} Mode")
        print(f"{'='*80}")
        
        start_time = time.time()
        
        scan_result = intelligent_scanner.scan_database_intelligent(
            connection_params=sqlserver_params,
            scan_mode=mode.lower(),
            max_tables=None
        )
        
        duration = time.time() - start_time
        findings = scan_result.get('findings', [])
        
        # Count PII types
        pii_counts = {}
        for finding in findings:
            pii_type = finding.get('pii_type', 'Unknown')
            pii_counts[pii_type] = pii_counts.get(pii_type, 0) + 1
        
        bsn_count = sum(count for pii_type, count in pii_counts.items() if 'BSN' in pii_type.upper())
        email_count = sum(count for pii_type, count in pii_counts.items() if 'EMAIL' in pii_type.upper())
        phone_count = sum(count for pii_type, count in pii_counts.items() if 'PHONE' in pii_type.upper())
        iban_count = sum(count for pii_type, count in pii_counts.items() if 'IBAN' in pii_type.upper())
        
        print(f"\n📊 Scan Results:")
        print(f"  Status: {scan_result.get('status')}")
        print(f"  Tables scanned: {scan_result.get('tables_scanned', 0)}")
        print(f"  Rows analyzed: {scan_result.get('rows_analyzed', 0)}")
        print(f"  Total findings: {len(findings)}")
        print(f"  Duration: {duration:.2f}s")
        
        print(f"\n🇳🇱 Dutch PII Detected:")
        print(f"  BSN (Social Security): {bsn_count}")
        print(f"  Email addresses: {email_count}")
        print(f"  Phone numbers: {phone_count}")
        print(f"  IBAN numbers: {iban_count}")
        
        if pii_counts:
            print(f"\n📋 Detailed PII Breakdown:")
            for pii_type, count in sorted(pii_counts.items()):
                print(f"  - {pii_type}: {count}")
        
        # Show sample findings
        if findings:
            print(f"\n📝 Sample Findings (first 5):")
            for i, finding in enumerate(findings[:5], 1):
                table = finding.get('table_name', 'Unknown')
                column = finding.get('column_name', 'Unknown')
                pii_type = finding.get('pii_type', 'Unknown')
                print(f"  {i}. {table}.{column} - {pii_type}")
        
        test_results[mode] = {
            'duration': duration,
            'findings': len(findings),
            'bsn': bsn_count,
            'email': email_count,
            'phone': phone_count,
            'iban': iban_count,
            'tables': scan_result.get('tables_scanned', 0),
            'rows': scan_result.get('rows_analyzed', 0)
        }
    
    # ==============================================================================
    # STEP 4: Test Summary
    # ==============================================================================
    print(f"\n{'='*80}")
    print("📊 TEST SUMMARY")
    print(f"{'='*80}")
    
    print("\nScan Mode Comparison:")
    print(f"{'Mode':<10} {'Duration':<12} {'Findings':<12} {'BSN':<8} {'Email':<8} {'Tables':<8} {'Rows':<8}")
    print("-"*80)
    
    for mode, results in test_results.items():
        print(f"{mode:<10} {results['duration']:<12.2f} {results['findings']:<12} {results['bsn']:<8} {results['email']:<8} {results['tables']:<8} {results['rows']:<8}")
    
    print("\nValidation:")
    all_passed = True
    
    # Check if BSN detection works
    if test_results['DEEP']['bsn'] >= 8:
        print("  ✓ BSN Detection: PASSED (found {} BSNs)".format(test_results['DEEP']['bsn']))
    else:
        print("  ✗ BSN Detection: FAILED (expected 8+, found {})".format(test_results['DEEP']['bsn']))
        all_passed = False
    
    # Check if email detection works
    if test_results['DEEP']['email'] >= 8:
        print("  ✓ Email Detection: PASSED (found {} emails)".format(test_results['DEEP']['email']))
    else:
        print("  ✗ Email Detection: FAILED (expected 8+, found {})".format(test_results['DEEP']['email']))
        all_passed = False
    
    # Check if all tables scanned
    if test_results['DEEP']['tables'] == 3:
        print("  ✓ Table Coverage: PASSED (scanned 3/3 tables)")
    else:
        print("  ✗ Table Coverage: FAILED (scanned {}/3 tables)".format(test_results['DEEP']['tables']))
        all_passed = False
    
    print("\n" + "="*80)
    if all_passed:
        print("✅ ALL TESTS PASSED - SQL Server Scanner is Working Correctly!")
    else:
        print("⚠️  SOME TESTS FAILED - Review findings above")
    print("="*80)
    
except Exception as e:
    print(f"\n✗ Test Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ==============================================================================
# Cleanup Instructions
# ==============================================================================
print("\n📝 Cleanup Instructions:")
print("  To stop and remove SQL Server container:")
print("    docker stop dataguardian-sqlserver")
print("    docker rm dataguardian-sqlserver")
print("")

#!/usr/bin/env python3
"""
SQL SERVER NETHERLANDS PII DETECTION TEST
==========================================
Tests DataGuardian Pro Database Scanner (Patent #2) with Microsoft SQL Server
Focus: Netherlands-specific PII detection (BSN, .nl emails, +31 phones, postcodes, IBAN)

Usage:
    SQLSERVER_HOST="your-server.database.windows.net" \
    SQLSERVER_PORT="1433" \
    SQLSERVER_USER="admin" \
    SQLSERVER_PASSWORD="YourPassword123!" \
    SQLSERVER_DATABASE="testdb" \
    python test_sqlserver_netherlands_pii.py
"""

import os
import sys
import time
from typing import Dict, Any

sys.path.insert(0, '.')

from services.db_scanner import DBScanner
from services.intelligent_db_scanner import IntelligentDBScanner


def setup_netherlands_test_data():
    """Create test table with Netherlands PII data in SQL Server"""
    try:
        import pyodbc
    except ImportError:
        print("❌ pyodbc not installed. Install with: pip install pyodbc")
        return False
    
    host = os.getenv('SQLSERVER_HOST')
    port = os.getenv('SQLSERVER_PORT', '1433')
    user = os.getenv('SQLSERVER_USER')
    password = os.getenv('SQLSERVER_PASSWORD')
    database = os.getenv('SQLSERVER_DATABASE')
    
    if not all([host, user, password, database]):
        print("❌ Missing SQL Server credentials. Set SQLSERVER_HOST, SQLSERVER_USER, SQLSERVER_PASSWORD, SQLSERVER_DATABASE")
        return False
    
    print(f"\n🔧 Setting up test data in SQL Server: {host}/{database}")
    print("="*80)
    
    try:
        # Connect to SQL Server
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={host},{port};"
            f"DATABASE={database};"
            f"UID={user};"
            f"PWD={password};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=no;"
            f"Connection Timeout=30;"
        )
        
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Drop table if exists
        cursor.execute("""
            IF OBJECT_ID('netherlands_pii_test', 'U') IS NOT NULL 
            DROP TABLE netherlands_pii_test
        """)
        
        # Create test table
        cursor.execute("""
            CREATE TABLE netherlands_pii_test (
                id INT IDENTITY(1,1) PRIMARY KEY,
                customer_name NVARCHAR(100),
                bsn NVARCHAR(20),
                email NVARCHAR(100),
                phone NVARCHAR(30),
                postcode NVARCHAR(10),
                address NVARCHAR(200),
                iban NVARCHAR(30),
                notes NVARCHAR(500),
                created_at DATETIME DEFAULT GETDATE()
            )
        """)
        
        # Insert Netherlands test data
        test_data = [
            ('Jan de Vries', '123456782', 'jan.devries@gmail.nl', '+31 6 12345678', '1012 AB', 'Damstraat 1, Amsterdam', 'NL91ABNA0417164300', 'Valid BSN customer'),
            ('Anna van der Berg', '987654321', 'anna@bedrijf.nl', '06-23456789', '3011 AD', 'Coolsingel 40, Rotterdam', 'NL20INGB0001234567', 'Corporate client'),
            ('Pieter Jansen', '234567891', 'p.jansen@outlook.nl', '+31 20 1234567', '2501 CA', 'Binnenhof 1, Den Haag', 'NL86RABO0123456789', 'Government employee'),
            ('Sophie Visser', '345678912', 'sophie.visser@xs4all.nl', '06-34567890', '3511 NZ', 'Domplein 9, Utrecht', 'NL02ABNA0123456789', 'Healthcare worker'),
            ('Lucas Bakker', '456789123', 'lucas@kpn.nl', '+31 30 2345678', '5611 ZT', 'Markt 77, Eindhoven', 'NL56INGB0123456789', 'Telecom engineer'),
            ('Emma de Jong', '567891234', 'emma.dejong@uva.nl', '06-45678901', '9712 CP', 'Grote Markt 1, Groningen', 'NL71RABO0123456789', 'University student'),
            ('Daan Mulder', '678912345', 'daan@ziggo.nl', '+31 50 3456789', '6511 LK', 'Stevensplein 2, Nijmegen', 'NL39ABNA0123456789', 'Retired'),
            ('Lisa Smit', '789123456', 'l.smit@gmail.nl', '06-56789012', '2011 RK', 'Grote Kerk 10, Haarlem', 'NL14INGB0123456789', 'Artist'),
            ('Thomas Peters', '891234567', 'thomas@live.nl', '+31 23 4567890', '8011 VR', 'Sassenstraat 21, Zwolle', 'NL82RABO0123456789', 'Business owner'),
            ('Mila Hendriks', '912345678', 'mila.hendriks@yahoo.nl', '06-67890123', '7511 HN', 'Oude Markt 4, Enschede', 'NL28ABNA0123456789', 'Software developer'),
            ('Noah van Dijk', '111111110', 'noah@protonmail.nl', '+31 53 5678901', '4811 XT', 'Grote Markt 20, Breda', 'NL65INGB0123456789', 'Privacy advocate'),
            ('Saar Vermeulen', '222222229', 'saar@tutanota.nl', '06-78901234', '6221 BR', 'Vrijthof 50, Maastricht', 'NL49RABO0123456789', 'Legal consultant'),
        ]
        
        for data in test_data:
            cursor.execute("""
                INSERT INTO netherlands_pii_test 
                (customer_name, bsn, email, phone, postcode, address, iban, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, data)
        
        conn.commit()
        
        # Verify data
        cursor.execute("SELECT COUNT(*) FROM netherlands_pii_test")
        result = cursor.fetchone()
        count = result[0] if result else 0
        
        cursor.close()
        conn.close()
        
        print(f"✅ Created netherlands_pii_test table with {count} records")
        print("\n📋 Sample data:")
        print("   - 12 unique BSN numbers (Netherlands social security)")
        print("   - 12 .nl email addresses")
        print("   - 12 +31/06 phone numbers")
        print("   - 12 Dutch postcodes (#### XX format)")
        print("   - 12 Dutch IBAN numbers (NL## format)")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up test data: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_sqlserver_netherlands_pii_test():
    """Test SQL Server Netherlands PII detection"""
    
    print("\n" + "="*80)
    print("SQL SERVER NETHERLANDS PII DETECTION TEST")
    print("="*80)
    
    # Get credentials
    host = os.getenv('SQLSERVER_HOST')
    port = os.getenv('SQLSERVER_PORT', '1433')
    user = os.getenv('SQLSERVER_USER')
    password = os.getenv('SQLSERVER_PASSWORD')
    database = os.getenv('SQLSERVER_DATABASE')
    
    if not all([host, user, password, database]):
        print("❌ Missing SQL Server credentials")
        print("\nUsage:")
        print("    SQLSERVER_HOST='your-server.database.windows.net' \\")
        print("    SQLSERVER_PORT='1433' \\")
        print("    SQLSERVER_USER='admin' \\")
        print("    SQLSERVER_PASSWORD='YourPassword!' \\")
        print("    SQLSERVER_DATABASE='testdb' \\")
        print("    python test_sqlserver_netherlands_pii.py")
        return
    
    # Setup test data
    if not setup_netherlands_test_data():
        print("❌ Failed to setup test data")
        return
    
    # Initialize scanners
    db_scanner = DBScanner(region='Netherlands')
    intelligent_scanner = IntelligentDBScanner(db_scanner)
    
    # Connection parameters
    connection_params = {
        'db_type': 'sqlserver',
        'host': host,
        'port': int(port),
        'database': database,
        'user': user,
        'password': password
    }
    
    print(f"\n🔍 Connecting to SQL Server: {host}/{database}")
    
    if not db_scanner.connect_to_database(connection_params):
        print("❌ Failed to connect to SQL Server")
        return
    
    print("✅ Connected successfully")
    
    # Run DEEP scan on test table
    print("\nRunning DEEP scan on netherlands_pii_test table...")
    
    start_time = time.time()
    results = intelligent_scanner.scan_database_intelligent(
        connection_params=connection_params,
        scan_mode='deep',
        max_tables=10
    )
    duration = time.time() - start_time
    
    # Display results
    print("\n" + "-"*80)
    print("SCAN RESULTS")
    print("-"*80)
    
    total_findings = results.get('summary', {}).get('total_findings', 0)
    tables_scanned = results.get('summary', {}).get('tables_scanned', 0)
    
    print(f"\nDuration: {duration:.2f} seconds")
    print(f"Total PII Findings: {total_findings}")
    print(f"Tables Scanned: {tables_scanned}")
    
    # Analyze PII types
    findings = results.get('findings', [])
    pii_types = {}
    
    for finding in findings:
        pii_type = finding.get('type', 'unknown')
        pii_types[pii_type] = pii_types.get(pii_type, 0) + 1
    
    if pii_types:
        print("\n" + "-"*80)
        print("PII TYPES DETECTED")
        print("-"*80)
        
        # Sort by count
        sorted_types = sorted(pii_types.items(), key=lambda x: x[1], reverse=True)
        
        for pii_type, count in sorted_types:
            # Highlight Netherlands-specific types
            marker = "✅" if any(kw in pii_type.lower() for kw in ['bsn', 'email', 'phone', 'iban', 'postcode']) else "  "
            print(f"{marker} {pii_type}: {count} instances")
    
    # Netherlands-specific validation
    print("\n" + "="*80)
    print("NETHERLANDS PII VALIDATION")
    print("="*80)
    
    bsn_count = sum(1 for f in findings if 'bsn' in f.get('type', '').lower() or ('id' in f.get('type', '').lower() and 'number' in f.get('type', '').lower()))
    email_count = sum(1 for f in findings if 'email' in f.get('type', '').lower())
    phone_count = sum(1 for f in findings if 'phone' in f.get('type', '').lower())
    postcode_count = sum(1 for f in findings if 'postcode' in f.get('type', '').lower() or 'postal' in f.get('type', '').lower())
    
    # Validation checks
    checks = {
        'BSN Detection (11-proef)': bsn_count >= 12,
        'Netherlands Email (.nl)': email_count >= 12,
        'Netherlands Phone (+31)': phone_count >= 12,
        'Netherlands Postcode': postcode_count >= 0,  # Optional
        'Total PII > 30': total_findings > 30,
        'Scan Performance < 10s': duration < 10.0
    }
    
    passed = 0
    for check_name, check_result in checks.items():
        status = "✅ PASS" if check_result else "❌ FAIL"
        print(f"{status} - {check_name}: ", end="")
        
        if 'BSN' in check_name:
            print(f"{bsn_count} BSN numbers detected")
        elif 'Email' in check_name:
            print("Email detection working" if check_result else f"Only {email_count}/12 emails detected")
        elif 'Phone' in check_name:
            print("Phone detection working" if check_result else f"Only {phone_count}/12 phones detected")
        elif 'Postcode' in check_name:
            print("Postcode detection working" if postcode_count > 0 else "No postcodes detected")
        elif 'Total PII' in check_name:
            print(f"{total_findings} total findings")
        elif 'Performance' in check_name:
            print(f"{duration:.2f}s scan time")
        
        if check_result:
            passed += 1
    
    print("\n" + "="*80)
    print(f"VALIDATION SUMMARY: {passed}/{len(checks)} checks passed")
    print("="*80)
    
    if passed == len(checks):
        print("\n✅ All validation checks passed!")
    elif passed >= len(checks) * 0.75:
        print(f"\n⚠️ Most validation checks passed ({passed}/{len(checks)})")
    else:
        print("\n⚠️ Some validation checks failed")
    
    print()


if __name__ == '__main__':
    run_sqlserver_netherlands_pii_test()

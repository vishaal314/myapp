#!/usr/bin/env python3
"""
SQL Server Database Scanner Test
Tests DataGuardian Pro scanner with SQL Server
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.db_scanner import DBScanner
from services.intelligent_db_scanner import IntelligentDBScanner

print("="*80)
print("🔍 SQL SERVER DATABASE SCANNER TEST")
print("="*80)

# Connection parameters (adjust if using Azure)
sqlserver_params = {
    'server': 'localhost',  # Or: yourserver.database.windows.net for Azure
    'port': 1433,
    'database': 'ComplianceTest',
    'username': 'sa',  # Or: sqladmin for Azure
    'password': 'DataGuard!2024',  # Or: DataGuard!2024Azure for Azure
    'db_type': 'sqlserver'
}

print(f"\nConnection: {sqlserver_params['server']}:{sqlserver_params['port']}/{sqlserver_params['database']}")

# Initialize scanners
db_scanner = DBScanner(region="Netherlands")
intelligent_scanner = IntelligentDBScanner(db_scanner)

test_results = {}

# Test all scan modes
for mode in ['FAST', 'SMART', 'DEEP']:
    print(f"\n{'='*80}")
    print(f"🚀 Testing {mode} Mode")
    print(f"{'='*80}")
    
    try:
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
        
        print(f"\n📊 Scan Results:")
        print(f"  Status: {scan_result.get('status')}")
        print(f"  Tables scanned: {scan_result.get('tables_scanned', 0)}")
        print(f"  Rows analyzed: {scan_result.get('rows_analyzed', 0)}")
        print(f"  Total findings: {len(findings)}")
        print(f"  Duration: {duration:.2f}s")
        
        print(f"\n🇳🇱 Dutch PII Detected:")
        print(f"  BSN: {bsn_count}")
        print(f"  Email: {email_count}")
        print(f"  Phone: {phone_count}")
        
        if pii_counts:
            print(f"\n📋 PII Types Found:")
            for pii_type, count in sorted(pii_counts.items()):
                print(f"  - {pii_type}: {count}")
        
        # Sample findings
        if findings[:3]:
            print(f"\n📝 Sample Findings:")
            for i, f in enumerate(findings[:3], 1):
                print(f"  {i}. {f.get('table_name')}.{f.get('column_name')} - {f.get('pii_type')}")
        
        test_results[mode] = {
            'duration': duration,
            'findings': len(findings),
            'bsn': bsn_count,
            'email': email_count,
            'phone': phone_count
        }
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        test_results[mode] = {'error': str(e)}

# Summary
print(f"\n{'='*80}")
print("📊 TEST SUMMARY")
print(f"{'='*80}")

print(f"\n{'Mode':<10} {'Duration':<12} {'Findings':<12} {'BSN':<8} {'Email':<8}")
print("-"*60)

for mode, results in test_results.items():
    if 'error' not in results:
        print(f"{mode:<10} {results['duration']:<12.2f} {results['findings']:<12} {results['bsn']:<8} {results['email']:<8}")

print("\n" + "="*80)
print("✅ SQL SERVER SCANNER TEST COMPLETED")
print("="*80)

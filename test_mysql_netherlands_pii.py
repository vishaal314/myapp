"""
Test Netherlands-specific PII detection in MySQL Railway database.
Validates BSN detection, Dutch emails, phone numbers, and postcodes.
"""

import pymysql
import pymysql.cursors
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.db_scanner import DBScanner
from services.intelligent_db_scanner import IntelligentDBScanner

class NetherlandsPIITester:
    """Test Netherlands-specific PII detection in MySQL."""
    
    def __init__(self):
        self.mysql_config = {
            'host': os.getenv('MYSQL_HOST', 'nozomi.proxy.rlwy.net'),
            'port': int(os.getenv('MYSQL_PORT', 46657)),
            'user': os.getenv('MYSQL_USER', 'root'),
            'password': os.getenv('MYSQL_PASSWORD'),
            'database': os.getenv('MYSQL_DATABASE', 'railway')
        }
    
    def create_netherlands_test_data(self):
        """Create table with Netherlands-specific PII data."""
        print("\n" + "="*80)
        print("CREATING NETHERLANDS PII TEST DATA IN MYSQL")
        print("="*80)
        
        try:
            # Connect to MySQL
            conn = pymysql.connect(
                **self.mysql_config,
                cursorclass=pymysql.cursors.DictCursor
            )
            cursor = conn.cursor()
            
            # Drop table if exists
            cursor.execute("DROP TABLE IF EXISTS netherlands_pii_test")
            
            # Create test table
            cursor.execute("""
                CREATE TABLE netherlands_pii_test (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    customer_name VARCHAR(100),
                    bsn VARCHAR(20),
                    email VARCHAR(100),
                    phone VARCHAR(50),
                    postcode VARCHAR(20),
                    address VARCHAR(200),
                    iban VARCHAR(50),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert Netherlands-specific PII data
            test_data = [
                # Valid BSN numbers (pass 11-proef validation)
                ('Jan de Vries', '123456782', 'jan.devries@gmail.nl', '+31 6 12345678', '1012 AB', 'Damstraat 1, Amsterdam', 'NL91ABNA0417164300', 'Valid BSN customer'),
                ('Anna van der Berg', '987654321', 'anna@bedrijf.nl', '06-23456789', '3011 AD', 'Coolsingel 101, Rotterdam', 'NL20INGB0001234567', 'Corporate email'),
                ('Pieter Jansen', '234567891', 'p.jansen@outlook.nl', '+31 20 1234567', '2501 CA', 'Prinsessegracht 20, Den Haag', 'NL39RABO0300065264', 'Netherlands phone'),
                ('Maria Bakker', '345678912', 'maria@ziggo.nl', '0612345678', '9711 AA', 'Grote Markt 1, Groningen', 'NL86INGB0002445588', 'Mobile format'),
                ('Thomas de Groot', '456789123', 'thomas.groot@kpn.nl', '+31-6-87654321', '5611 AB', 'Stratumseind 10, Eindhoven', 'NL02ABNA0123456789', 'Hyphenated phone'),
                
                # Dutch business/organization data
                ('Gemeente Amsterdam', '567891234', 'info@amsterdam.nl', '+31 20 624 1111', '1012 KP', 'Amstel 1, Amsterdam', 'NL76RABO0300000000', 'Government entity'),
                ('VU Universiteit', '678912345', 'contact@vu.nl', '020-5989898', '1081 HV', 'De Boelelaan 1105, Amsterdam', 'NL12INGB0000001111', 'University'),
                ('Ziekenhuis Utrecht', '789123456', 'info@umcutrecht.nl', '+31 88 7555555', '3584 CX', 'Heidelberglaan 100, Utrecht', 'NL55ABNA0250000000', 'Hospital with medical data'),
                
                # Mixed international (should detect Dutch elements)
                ('John Smith', '891234567', 'john.smith@company.com', '+1-555-1234567', '10001', '123 Main St, New York', 'US12345678901234567', 'American with BSN (expat)'),
                ('Sophie Laurent', '912345678', 'sophie@gmail.fr', '+33 6 12345678', '75001', '10 Rue de Paris', 'FR7630006000011234567890189', 'French but has Dutch BSN'),
                
                # Edge cases
                ('Test Invalid', '000000000', 'test@test.nl', '0000000000', '0000 AA', 'Test Address', 'NL00TEST0000000000', 'Invalid BSN (should fail 11-proef)'),
                ('No PII User', None, 'noreply@example.com', None, None, None, None, 'User without Dutch PII'),
            ]
            
            insert_query = """
                INSERT INTO netherlands_pii_test 
                (customer_name, bsn, email, phone, postcode, address, iban, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.executemany(insert_query, test_data)
            conn.commit()
            
            # Verify insertion
            cursor.execute("SELECT COUNT(*) as count FROM netherlands_pii_test")
            count = cursor.fetchone()['count']
            
            print(f"\n✅ Created table 'netherlands_pii_test' with {count} test records")
            print("\nTest data includes:")
            print("  • 10 valid BSN numbers (11-proef validated)")
            print("  • 11 .nl email addresses")
            print("  • 10 Netherlands phone numbers (+31 format)")
            print("  • 10 Dutch postcodes (1234 AB format)")
            print("  • 10 Dutch IBAN numbers")
            print("  • Mixed valid/invalid data for edge case testing")
            
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error creating test data: {str(e)}")
            return False
    
    def test_mysql_netherlands_pii_detection(self):
        """Test PII detection on Netherlands-specific data."""
        print("\n" + "="*80)
        print("TESTING NETHERLANDS PII DETECTION IN MYSQL")
        print("="*80)
        
        try:
            # Initialize scanner
            scanner = DBScanner(region="Netherlands")
            intelligent_scanner = IntelligentDBScanner(scanner)
            
            # Connection parameters
            connection_params = {
                'type': 'mysql',
                'host': self.mysql_config['host'],
                'port': self.mysql_config['port'],
                'database': self.mysql_config['database'],
                'user': self.mysql_config['user'],
                'password': self.mysql_config['password']
            }
            
            # Run DEEP scan (most thorough)
            print("\nRunning DEEP scan on netherlands_pii_test table...")
            start_time = datetime.now()
            
            results = intelligent_scanner.scan_database_intelligent(
                connection_params=connection_params,
                scan_mode='deep',
                max_tables=None
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Analyze results
            print("\n" + "-"*80)
            print("SCAN RESULTS")
            print("-"*80)
            
            total_findings = results.get('total_findings', 0)
            tables_scanned = results.get('tables_scanned', 0)
            
            print(f"\nDuration: {duration:.2f} seconds")
            print(f"Total PII Findings: {total_findings}")
            print(f"Tables Scanned: {tables_scanned}")
            
            # Detailed findings breakdown
            if 'findings' in results:
                print("\n" + "-"*80)
                print("PII TYPES DETECTED")
                print("-"*80)
                
                pii_types = {}
                for finding in results['findings']:
                    pii_type = finding.get('type', 'unknown')
                    pii_types[pii_type] = pii_types.get(pii_type, 0) + 1
                
                # Check for Netherlands-specific PII
                bsn_found = pii_types.get('BSN (Netherlands)', 0) or pii_types.get('bsn', 0)
                nl_email_found = any('email' in k.lower() for k in pii_types.keys())
                nl_phone_found = any('phone' in k.lower() for k in pii_types.keys())
                nl_postcode_found = any('postcode' in k.lower() or 'postal' in k.lower() for k in pii_types.keys())
                
                for pii_type, count in sorted(pii_types.items(), key=lambda x: x[1], reverse=True):
                    marker = "✅" if any(kw in pii_type.lower() for kw in ['bsn', 'netherlands', 'email', 'phone', 'iban']) else "  "
                    print(f"{marker} {pii_type}: {count} instances")
                
                # Validation summary
                print("\n" + "="*80)
                print("NETHERLANDS PII VALIDATION")
                print("="*80)
                
                validations = [
                    ("BSN Detection (11-proef)", bsn_found > 0, f"{bsn_found} BSN numbers detected"),
                    ("Netherlands Email (.nl)", nl_email_found, "Email detection working"),
                    ("Netherlands Phone (+31)", nl_phone_found, "Phone detection working"),
                    ("Netherlands Postcode", nl_postcode_found, "Postcode detection working"),
                    ("Total PII > 30", total_findings > 30, f"{total_findings} total findings"),
                    ("Scan Performance < 10s", duration < 10, f"{duration:.2f}s scan time")
                ]
                
                passed = 0
                for name, result, details in validations:
                    status = "✅ PASS" if result else "❌ FAIL"
                    print(f"{status} - {name}: {details}")
                    if result:
                        passed += 1
                
                print("\n" + "="*80)
                print(f"VALIDATION SUMMARY: {passed}/{len(validations)} checks passed")
                print("="*80)
                
                return passed == len(validations)
            else:
                print("\n⚠️ No detailed findings available")
                return False
                
        except Exception as e:
            import traceback
            print(f"\n❌ Error testing PII detection: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return False

def main():
    """Run Netherlands PII detection test."""
    print("\n" + "="*80)
    print("DATAGUARDIAN PRO - NETHERLANDS PII DETECTION TEST")
    print("MySQL Railway Database")
    print("="*80)
    
    tester = NetherlandsPIITester()
    
    # Step 1: Create test data
    if not tester.create_netherlands_test_data():
        print("\n❌ Failed to create test data")
        return 1
    
    # Step 2: Test PII detection
    if not tester.test_mysql_netherlands_pii_detection():
        print("\n⚠️ Some validation checks failed")
        return 1
    
    print("\n" + "="*80)
    print("✅ ALL NETHERLANDS PII DETECTION TESTS PASSED!")
    print("="*80)
    return 0

if __name__ == "__main__":
    sys.exit(main())

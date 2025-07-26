"""
Comprehensive Test Suite for Code Scanner
6 automated tests covering functional and performance validation.
"""

import unittest
import tempfile
import os
import sys
from typing import Dict, Any

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.code_scanner import CodeScanner
from tests.test_framework import ScannerTestSuite, BaseScanner

class TestCodeScanner(ScannerTestSuite):
    """Comprehensive test suite for Code Scanner functionality and performance"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.scanner = CodeScanner(region="Netherlands")
        cls.base_tester = BaseScanner("CodeScanner")
    
    def test_1_functional_pii_detection(self):
        """Test 1: Functional - PII Detection in Code Files"""
        # Create test file with PII patterns
        test_code = '''
# Test file with PII
email = "john.doe@company.com"
phone = "+31 6 12345678"  # Dutch mobile
bsn = "123456782"  # Netherlands BSN
api_key = "sk_live_abc123def456ghi789"  # Stripe key
password = "super_secret_password123"
'''
        
        temp_file = self.create_temp_file(test_code, '.py')
        
        try:
            # Execute scan
            performance_data = self.base_tester.measure_performance(
                self.scanner.scan_file, temp_file
            )
            result = performance_data['result']
            
            # Validate structure
            self.assert_scan_structure(result)
            
            # Validate PII detection
            self.assertGreater(len(result['findings']), 0, "Should detect PII patterns")
            
            # Check for Netherlands-specific BSN detection
            bsn_found = any('bsn' in str(finding).lower() or 'netherlands' in str(finding).lower() 
                           for finding in result['findings'])
            self.assertTrue(bsn_found, "Should detect Netherlands BSN pattern")
            
            # Validate performance
            self.assert_performance_within_limits(performance_data)
            
            print(f"✓ Test 1 PASSED: Detected {len(result['findings'])} PII patterns in {performance_data['execution_time']:.2f}s")
            
        finally:
            self.cleanup_temp_file(temp_file)
    
    def test_2_functional_secret_detection(self):
        """Test 2: Functional - Secret and API Key Detection"""
        test_code = '''
# Configuration with secrets
AWS_ACCESS_KEY = "AKIA1234567890123456"
AWS_SECRET_KEY = "abcdef1234567890abcdef1234567890abcdef12"
STRIPE_SECRET = "sk_live_1234567890abcdef1234567890abcdef12345678"
DATABASE_URL = "postgresql://user:password@localhost:5432/db"
API_TOKEN = "ghp_1234567890abcdef1234567890abcdef123456"
'''
        
        temp_file = self.create_temp_file(test_code, '.py')
        
        try:
            performance_data = self.base_tester.measure_performance(
                self.scanner.scan_file, temp_file
            )
            result = performance_data['result']
            
            # Validate structure
            self.assert_scan_structure(result)
            
            # Check for secret detection
            secret_findings = [f for f in result['findings'] 
                              if any(keyword in str(f).lower() for keyword in ['secret', 'key', 'token', 'password'])]
            self.assertGreater(len(secret_findings), 0, "Should detect secret patterns")
            
            # Validate performance
            self.assert_performance_within_limits(performance_data)
            
            print(f"✓ Test 2 PASSED: Detected {len(secret_findings)} secrets in {performance_data['execution_time']:.2f}s")
            
        finally:
            self.cleanup_temp_file(temp_file)
    
    def test_3_functional_gdpr_compliance(self):
        """Test 3: Functional - GDPR Compliance Analysis"""
        test_code = '''
# GDPR compliance issues
def collect_user_data(email, name, age, ssn):
    # No consent validation
    user_data = {
        "email": email,
        "personal_name": name,
        "age": age,
        "ssn": ssn  # Sensitive data without protection
    }
    # Store without encryption
    save_to_database(user_data)
    return user_data

def process_children_data(child_email, parent_consent=False):
    if not parent_consent:
        # Processing children data without consent - GDPR violation
        return process_data(child_email)
'''
        
        temp_file = self.create_temp_file(test_code, '.py')
        
        try:
            performance_data = self.base_tester.measure_performance(
                self.scanner.scan_file, temp_file
            )
            result = performance_data['result']
            
            # Validate structure
            self.assert_scan_structure(result)
            
            # Check GDPR-specific compliance
            if 'gdpr_compliance' in result:
                self.assertIn('compliance_score', result['gdpr_compliance'])
                score = result['gdpr_compliance']['compliance_score']
                self.assertGreaterEqual(score, 0)
                self.assertLessEqual(score, 100)
            
            # Validate performance
            self.assert_performance_within_limits(performance_data)
            
            print(f"✓ Test 3 PASSED: GDPR analysis completed in {performance_data['execution_time']:.2f}s")
            
        finally:
            self.cleanup_temp_file(temp_file)
    
    def test_4_performance_large_codebase(self):
        """Test 4: Performance - Large Codebase Scanning"""
        # Generate large test file (1000+ lines)
        large_code = '''
# Large codebase performance test
import os
import sys
from typing import Dict, List, Any

class DataProcessor:
    def __init__(self):
        self.api_key = "test_key_12345"
        self.email_patterns = []
    
    def process_emails(self, emails):
        """Process email data"""
        results = []
        for email in emails:
            if "@" in email:
                results.append(email)
        return results
''' * 50  # Repeat to create ~1000+ lines
        
        temp_file = self.create_temp_file(large_code, '.py')
        
        try:
            performance_data = self.base_tester.measure_performance(
                self.scanner.scan_file, temp_file
            )
            result = performance_data['result']
            
            # Validate structure
            self.assert_scan_structure(result)
            
            # Performance requirements for large files
            self.assertLess(performance_data['execution_time'], 15.0, 
                           "Large file scan should complete within 15 seconds")
            self.assertLess(performance_data['memory_used'], 150.0,
                           "Memory usage should stay under 150MB for large files")
            
            print(f"✓ Test 4 PASSED: Large codebase ({len(large_code.split())} lines) scanned in {performance_data['execution_time']:.2f}s")
            
        finally:
            self.cleanup_temp_file(temp_file)
    
    def test_5_performance_multiple_file_formats(self):
        """Test 5: Performance - Multiple Programming Languages"""
        test_files = {
            '.py': 'email = "test@example.com"\napi_key = "abc123"',
            '.js': 'const email = "test@example.com";\nconst apiKey = "abc123";',
            '.java': 'String email = "test@example.com";\nString apiKey = "abc123";',
            '.php': '<?php $email = "test@example.com"; $apiKey = "abc123"; ?>',
            '.rb': 'email = "test@example.com"\napi_key = "abc123"'
        }
        
        temp_files = []
        try:
            # Create test files
            for ext, content in test_files.items():
                temp_file = self.create_temp_file(content, ext)
                temp_files.append(temp_file)
            
            # Scan all files
            total_findings = 0
            total_time = 0
            
            for temp_file in temp_files:
                performance_data = self.base_tester.measure_performance(
                    self.scanner.scan_file, temp_file
                )
                result = performance_data['result']
                
                # Validate each result
                self.assert_scan_structure(result)
                total_findings += len(result['findings'])
                total_time += performance_data['execution_time']
            
            # Performance validation
            avg_time_per_file = total_time / len(temp_files)
            self.assertLess(avg_time_per_file, 3.0, 
                           "Average scan time per file should be under 3 seconds")
            
            print(f"✓ Test 5 PASSED: {len(temp_files)} file formats scanned with {total_findings} findings in {total_time:.2f}s")
            
        finally:
            for temp_file in temp_files:
                self.cleanup_temp_file(temp_file)
    
    def test_6_functional_netherlands_specific(self):
        """Test 6: Functional - Netherlands-Specific GDPR/UAVG Compliance"""
        test_code = '''
# Netherlands-specific data processing
def process_dutch_citizen_data():
    bsn = "123456782"  # Netherlands BSN
    postcode = "1234 AB"  # Dutch postal code
    kvk_number = "12345678"  # Chamber of Commerce
    
    # Process without UAVG compliance
    citizen_data = {
        "bsn": bsn,
        "postcode": postcode,
        "kvk": kvk_number,
        "medical_data": "sensitive health info"
    }
    
    # No DPA notification mechanism
    return store_citizen_data(citizen_data)

def handle_data_breach():
    # Missing 72-hour notification requirement
    pass
'''
        
        temp_file = self.create_temp_file(test_code, '.py')
        
        try:
            performance_data = self.base_tester.measure_performance(
                self.scanner.scan_file, temp_file
            )
            result = performance_data['result']
            
            # Validate structure
            self.assert_scan_structure(result)
            
            # Check Netherlands-specific detection
            nl_specific_findings = [f for f in result['findings'] 
                                   if any(keyword in str(f).lower() for keyword in 
                                         ['bsn', 'netherlands', 'dutch', 'uavg', 'postcode'])]
            self.assertGreater(len(nl_specific_findings), 0, 
                              "Should detect Netherlands-specific patterns")
            
            # Validate region setting
            self.assertEqual(result.get('region'), 'Netherlands')
            
            # Validate performance
            self.assert_performance_within_limits(performance_data)
            
            print(f"✓ Test 6 PASSED: Netherlands-specific analysis with {len(nl_specific_findings)} findings in {performance_data['execution_time']:.2f}s")
            
        finally:
            self.cleanup_temp_file(temp_file)

if __name__ == '__main__':
    unittest.main(verbosity=2)
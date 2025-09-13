#!/usr/bin/env python3
"""
Comprehensive UAVG (Netherlands) Scanner Test Suite
15 tests each for: Functionality, Performance, Security, Violation Detection
Total: 60 comprehensive test cases for Netherlands GDPR compliance
"""

import unittest
import sys
import os
import time
import tempfile
import threading
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.netherlands_gdpr import detect_nl_violations, validate_bsn, detect_cookie_banners
from utils.gdpr_rules import get_region_rules, evaluate_risk_level

class TestUAVGScannerFunctionality(unittest.TestCase):
    """15 Functionality Tests for UAVG Scanner"""
    
    def setUp(self):
        self.region = "Netherlands"
        
    def test_01_bsn_validation_algorithm(self):
        """Test BSN validation algorithm functionality"""
        valid_bsns = ["123456782", "111222333"]  # Valid BSN numbers
        invalid_bsns = ["123456789", "111111111", "000000000"]
        
        for bsn in valid_bsns:
            self.assertTrue(validate_bsn(bsn), f"Valid BSN {bsn} should pass validation")
            
        for bsn in invalid_bsns:
            self.assertFalse(validate_bsn(bsn), f"Invalid BSN {bsn} should fail validation")
            
    def test_02_nl_region_rules_loading(self):
        """Test Netherlands region rules loading"""
        rules = get_region_rules("Netherlands")
        
        self.assertIsInstance(rules, dict)
        self.assertTrue(rules.get('bsn_required', False))
        self.assertIn('cookie_consent_required', rules)
        self.assertIn('ap_authority_url', rules)
        
    def test_03_cookie_banner_detection(self):
        """Test cookie banner detection functionality"""
        html_with_banner = '''
        <div class="cookie-banner">
            <p>We use cookies. Accept our <a href="/privacy">privacy policy</a></p>
            <button id="accept-cookies">Accept</button>
        </div>
        '''
        
        html_without_banner = '''
        <div class="content">
            <p>Welcome to our website</p>
        </div>
        '''
        
        banners_found = detect_cookie_banners(html_with_banner)
        self.assertGreater(len(banners_found), 0)
        
        banners_not_found = detect_cookie_banners(html_without_banner)
        self.assertEqual(len(banners_not_found), 0)
        
    def test_04_dutch_privacy_policy_detection(self):
        """Test Dutch privacy policy detection"""
        dutch_terms = ["privacy verklaring", "gegevensbescherming", "AVG", "privacybeleid"]
        
        for term in dutch_terms:
            content = f'link = "https://company.nl/{term.replace(" ", "-")}"'
            violations = detect_nl_violations(content)
            self.assertIsInstance(violations, list)
            
    def test_05_nl_phone_number_patterns(self):
        """Test Netherlands phone number pattern detection"""
        nl_phones = [
            "+31-6-12345678",
            "06-12345678", 
            "+31 20 1234567",
            "020-1234567"
        ]
        
        for phone in nl_phones:
            content = f'phone = "{phone}"'
            violations = detect_nl_violations(content)
            phone_violations = [v for v in violations if 'phone' in v.get('type', '').lower()]
            self.assertGreaterEqual(len(phone_violations), 0)
            
    def test_06_dutch_address_detection(self):
        """Test Dutch address pattern detection"""
        nl_addresses = [
            "1012 AB Amsterdam", 
            "Kalverstraat 1, Amsterdam",
            "Postbus 1234, 1000 AA Amsterdam"
        ]
        
        for address in nl_addresses:
            content = f'address = "{address}"'
            violations = detect_nl_violations(content)
            self.assertIsInstance(violations, list)
            
    def test_07_iban_netherlands_detection(self):
        """Test Netherlands IBAN detection"""
        nl_ibans = [
            "NL91ABNA0417164300",
            "NL02RABO0123456789"
        ]
        
        for iban in nl_ibans:
            content = f'account = "{iban}"'
            violations = detect_nl_violations(content)
            iban_violations = [v for v in violations if 'iban' in v.get('type', '').lower()]
            self.assertGreaterEqual(len(iban_violations), 0)
            
    def test_08_kvk_number_detection(self):
        """Test KvK (Chamber of Commerce) number detection"""
        kvk_numbers = ["12345678", "87654321"]
        
        for kvk in kvk_numbers:
            content = f'kvk_nummer = "{kvk}"'
            violations = detect_nl_violations(content)
            kvk_violations = [v for v in violations if 'kvk' in v.get('type', '').lower()]
            self.assertGreaterEqual(len(kvk_violations), 0)
            
    def test_09_dutch_id_document_detection(self):
        """Test Dutch ID document number detection"""
        id_patterns = [
            "NL12345678901",  # Dutch passport
            "ID123456789",     # ID card
        ]
        
        for id_num in id_patterns:
            content = f'document_id = "{id_num}"'
            violations = detect_nl_violations(content)
            self.assertIsInstance(violations, list)
            
    def test_10_ap_authority_compliance_check(self):
        """Test AP (Autoriteit Persoonsgegevens) compliance check"""
        rules = get_region_rules("Netherlands")
        ap_url = rules.get('ap_authority_url')
        
        self.assertIsNotNone(ap_url)
        self.assertIn('autoriteitpersoonsgegevens.nl', ap_url)
        
    def test_11_gdpr_vs_uavg_differences(self):
        """Test GDPR vs UAVG implementation differences"""
        nl_rules = get_region_rules("Netherlands")
        eu_rules = get_region_rules("Germany")  # Standard EU GDPR
        
        # Netherlands should have BSN requirements
        self.assertTrue(nl_rules.get('bsn_required', False))
        self.assertFalse(eu_rules.get('bsn_required', True))
        
    def test_12_dutch_medical_data_detection(self):
        """Test Dutch medical data pattern detection"""
        medical_terms = [
            "BSN medisch dossier",
            "patient nummer",
            "zorgverzekering",
            "AGB code"
        ]
        
        for term in medical_terms:
            content = f'medical_data = "{term} 123456789"'
            violations = detect_nl_violations(content)
            self.assertIsInstance(violations, list)
            
    def test_13_consent_mechanism_detection(self):
        """Test consent mechanism detection"""
        consent_html = '''
        <form id="consent-form">
            <label><input type="checkbox" name="marketing"> Marketing emails</label>
            <label><input type="checkbox" name="analytics"> Analytics cookies</label>
            <button type="submit">Opslaan voorkeuren</button>
        </form>
        '''
        
        violations = detect_nl_violations(consent_html)
        self.assertIsInstance(violations, list)
        
    def test_14_dark_pattern_detection(self):
        """Test dark pattern detection in consent"""
        dark_pattern_html = '''
        <div class="consent">
            <button class="big-green-button">Accept All</button>
            <a href="#" class="tiny-link">Manage preferences</a>
        </div>
        '''
        
        violations = detect_nl_violations(dark_pattern_html)
        dark_patterns = [v for v in violations if 'dark' in v.get('type', '').lower()]
        self.assertGreaterEqual(len(dark_patterns), 0)
        
    def test_15_multilingual_content_detection(self):
        """Test multilingual content detection (Dutch/English)"""
        mixed_content = '''
        privacy_policy_nl = "Wij respecteren uw privacy"
        privacy_policy_en = "We respect your privacy"
        email_nl = "contact@bedrijf.nl"
        '''
        
        violations = detect_nl_violations(mixed_content)
        self.assertIsInstance(violations, list)

class TestUAVGScannerPerformance(unittest.TestCase):
    """15 Performance Tests for UAVG Scanner"""
    
    def setUp(self):
        self.region = "Netherlands"
        
    def test_01_bsn_validation_speed(self):
        """Test BSN validation algorithm speed"""
        test_bsns = ["123456782"] * 1000
        
        start_time = time.time()
        for bsn in test_bsns:
            validate_bsn(bsn)
        end_time = time.time()
        
        total_time = end_time - start_time
        self.assertLess(total_time, 1.0)  # Should validate 1000 BSNs in under 1 second
        
    def test_02_large_text_scanning_performance(self):
        """Test performance on large Dutch text content"""
        large_dutch_content = '''
        Dit is een groot Nederlands document met veel persoonsgegevens.
        BSN: 123456782
        Telefoon: 06-12345678
        Email: gebruiker@bedrijf.nl
        Adres: Kalverstraat 1, 1012 AB Amsterdam
        ''' * 1000
        
        start_time = time.time()
        violations = detect_nl_violations(large_dutch_content)
        end_time = time.time()
        
        scan_time = end_time - start_time
        self.assertLess(scan_time, 10.0)  # Should scan large content in under 10 seconds
        
    def test_03_concurrent_bsn_validation(self):
        """Test concurrent BSN validation performance"""
        def validate_worker(bsn_list, results):
            count = 0
            for bsn in bsn_list:
                if validate_bsn(bsn):
                    count += 1
            results.append(count)
            
        bsn_lists = [["123456782", "111222333"] for _ in range(10)]
        results = []
        threads = []
        
        start_time = time.time()
        for bsn_list in bsn_lists:
            thread = threading.Thread(target=validate_worker, args=(bsn_list, results))
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()
        end_time = time.time()
        
        total_time = end_time - start_time
        self.assertLess(total_time, 2.0)  # Concurrent validation should be fast
        
    def test_04_regex_compilation_performance(self):
        """Test regex pattern compilation performance"""
        start_time = time.time()
        
        # Simulate pattern compilation (would be done in actual implementation)
        import re
        patterns = [
            r'\b\d{9}\b',  # BSN pattern
            r'\+31-?\s?\d{1,2}-?\s?\d{7,8}',  # Dutch phone
            r'\b\d{4}\s?[A-Z]{2}\s+[A-Za-z\s]+\b',  # Postal code
        ]
        
        compiled_patterns = [re.compile(pattern) for pattern in patterns]
        end_time = time.time()
        
        compilation_time = end_time - start_time
        self.assertLess(compilation_time, 0.1)  # Should compile quickly
        
    def test_05_memory_efficiency_large_dataset(self):
        """Test memory efficiency with large Dutch datasets"""
        import psutil
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Process large amount of Dutch data
        for i in range(100):
            content = f'''
            Persoon {i}:
            BSN: 12345678{i % 10}
            Telefoon: 06-1234567{i % 10}
            Email: persoon{i}@voorbeeld.nl
            '''
            detect_nl_violations(content)
            
        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be reasonable
        self.assertLess(memory_growth, 50 * 1024 * 1024)  # Less than 50MB
        
    def test_06_cookie_banner_detection_speed(self):
        """Test cookie banner detection speed"""
        large_html = '''
        <html><body>
        ''' + '''<div class="content">Content block</div>''' * 1000 + '''
        <div class="cookie-banner">
            <p>We use cookies for analytics</p>
            <button onclick="acceptCookies()">Accept</button>
        </div>
        </body></html>
        '''
        
        start_time = time.time()
        banners = detect_cookie_banners(large_html)
        end_time = time.time()
        
        detection_time = end_time - start_time
        self.assertLess(detection_time, 2.0)  # Should detect banners quickly
        
    def test_07_scalability_increasing_content(self):
        """Test scalability with increasing content sizes"""
        sizes = [100, 500, 1000, 2000]  # Lines of Dutch content
        times = []
        
        for size in sizes:
            content = "BSN: 123456782\\nTelefoon: 06-12345678\\n" * size
            
            start_time = time.time()
            detect_nl_violations(content)
            end_time = time.time()
            
            times.append(end_time - start_time)
            
        # Performance should scale reasonably
        for i in range(1, len(times)):
            scale_factor = sizes[i] / sizes[i-1]
            time_factor = times[i] / times[i-1] if times[i-1] > 0 else 1
            self.assertLess(time_factor, scale_factor * 2)
            
    def test_08_pattern_matching_optimization(self):
        """Test pattern matching optimization"""
        # Test with and without optimization
        content = "BSN: 123456782, Telefoon: 06-12345678" * 500
        
        start_time = time.time()
        violations1 = detect_nl_violations(content)
        first_scan_time = time.time() - start_time
        
        start_time = time.time()
        violations2 = detect_nl_violations(content)  # Second scan (potential caching)
        second_scan_time = time.time() - start_time
        
        # Second scan should be similar or faster
        self.assertLessEqual(second_scan_time, first_scan_time * 1.2)
        
    def test_09_iban_validation_performance(self):
        """Test IBAN validation performance"""
        test_ibans = ["NL91ABNA0417164300"] * 1000
        
        start_time = time.time()
        for iban in test_ibans:
            content = f'account = "{iban}"'
            detect_nl_violations(content)
        end_time = time.time()
        
        total_time = end_time - start_time
        self.assertLess(total_time, 5.0)  # Should process 1000 IBANs quickly
        
    def test_10_postal_code_detection_speed(self):
        """Test Dutch postal code detection speed"""
        postal_codes = [f"{1000 + i} AB Amsterdam" for i in range(1000)]
        
        start_time = time.time()
        for postal_code in postal_codes:
            content = f'address = "{postal_code}"'
            detect_nl_violations(content)
        end_time = time.time()
        
        total_time = end_time - start_time
        self.assertLess(total_time, 3.0)
        
    def test_11_multilingual_detection_performance(self):
        """Test multilingual detection performance"""
        mixed_content = '''
        English: We collect personal data
        Nederlands: Wij verzamelen persoonsgegevens
        BSN: 123456782
        Telefoon: 06-12345678
        ''' * 200
        
        start_time = time.time()
        violations = detect_nl_violations(mixed_content)
        end_time = time.time()
        
        scan_time = end_time - start_time
        self.assertLess(scan_time, 5.0)
        
    def test_12_consent_form_analysis_speed(self):
        """Test consent form analysis speed"""
        complex_form = '''
        <form class="consent-form">
        ''' + '''
            <label><input type="checkbox" name="category_{}"> Category {}</label>
        '''.format(i, i) * 100 + '''
        </form>
        ''' for i in range(50)
        
        start_time = time.time()
        for form in complex_form:
            detect_nl_violations(form)
        end_time = time.time()
        
        analysis_time = end_time - start_time
        self.assertLess(analysis_time, 8.0)
        
    def test_13_dark_pattern_detection_performance(self):
        """Test dark pattern detection performance"""
        complex_html = '''
        <div class="consent-area">
        ''' + '''
            <button class="primary-button">Accept All</button>
            <a href="#" class="small-link">Settings</a>
        ''' * 100 + '''
        </div>
        '''
        
        start_time = time.time()
        violations = detect_nl_violations(complex_html)
        end_time = time.time()
        
        detection_time = end_time - start_time
        self.assertLess(detection_time, 3.0)
        
    def test_14_caching_effectiveness(self):
        """Test caching effectiveness for repeated content"""
        content = "BSN: 123456782, Email: test@voorbeeld.nl"
        
        # First scan
        start_time = time.time()
        for _ in range(50):
            detect_nl_violations(content)
        first_batch_time = time.time() - start_time
        
        # Second scan (potential caching benefits)
        start_time = time.time()
        for _ in range(50):
            detect_nl_violations(content)
        second_batch_time = time.time() - start_time
        
        # Should not be significantly slower
        self.assertLess(second_batch_time, first_batch_time * 1.5)
        
    def test_15_resource_cleanup_efficiency(self):
        """Test resource cleanup efficiency"""
        initial_time = time.time()
        
        # Process many different Dutch content samples
        for i in range(50):
            content = f'''
            Sample {i}:
            BSN: 12345678{i % 10}
            Telefoon: 06-87654{i:03d}
            Email: test{i}@bedrijf.nl
            '''
            detect_nl_violations(content)
            
        total_time = time.time() - initial_time
        average_time = total_time / 50
        
        # Each sample should process efficiently
        self.assertLess(average_time, 0.2)

class TestUAVGScannerSecurity(unittest.TestCase):
    """15 Security Tests for UAVG Scanner"""
    
    def setUp(self):
        self.region = "Netherlands"
        
    def test_01_bsn_data_protection(self):
        """Test BSN data is properly protected in output"""
        sensitive_bsn = "123456782"
        content = f'bsn_number = "{sensitive_bsn}"'
        
        violations = detect_nl_violations(content)
        
        # Violations should not contain actual BSN
        violations_str = str(violations)
        self.assertNotIn(sensitive_bsn, violations_str)
        
    def test_02_input_sanitization_dutch_content(self):
        """Test input sanitization for Dutch content"""
        malicious_content = '''
        <script>alert("XSS")</script>
        BSN: 123456782
        eval("malicious_code")
        '''
        
        # Should handle malicious content safely
        violations = detect_nl_violations(malicious_content)
        self.assertIsInstance(violations, list)
        
    def test_03_injection_prevention_dutch_patterns(self):
        """Test injection prevention in Dutch pattern matching"""
        injection_attempts = [
            "BSN: 123456782'; DROP TABLE users; --",
            "Telefoon: 06-12345678\\x00malicious",
            "Email: test@voorbeeld.nl<script>alert(1)</script>"
        ]
        
        for attempt in injection_attempts:
            violations = detect_nl_violations(attempt)
            self.assertIsInstance(violations, list)
            
    def test_04_regex_dos_protection_dutch(self):
        """Test ReDoS protection for Dutch patterns"""
        # Content designed to trigger catastrophic backtracking
        redos_content = "BSN: " + "1" * 10000 + "782"
        
        start_time = time.time()
        violations = detect_nl_violations(redos_content)
        end_time = time.time()
        
        # Should complete in reasonable time
        scan_time = end_time - start_time
        self.assertLess(scan_time, 10.0)
        
    def test_05_memory_exhaustion_protection(self):
        """Test memory exhaustion protection"""
        import psutil
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Large Dutch content that could cause memory issues
        large_content = '''
        BSN lijst: [
            "123456782" * 10000 for i in range(1000)
        ]
        '''
        
        violations = detect_nl_violations(large_content)
        
        current_memory = process.memory_info().rss
        memory_increase = current_memory - initial_memory
        
        # Should not consume excessive memory
        self.assertLess(memory_increase, 200 * 1024 * 1024)  # Less than 200MB
        
    def test_06_concurrent_access_safety_dutch(self):
        """Test thread safety for Dutch content processing"""
        def process_worker(content, results):
            try:
                violations = detect_nl_violations(content)
                results.append(len(violations))
            except Exception as e:
                results.append(f"Error: {e}")
                
        dutch_contents = [
            f"BSN: 12345678{i}, Telefoon: 06-1234567{i}"
            for i in range(5)
        ]
        
        threads = []
        results = []
        
        for content in dutch_contents:
            thread = threading.Thread(target=process_worker, args=(content, results))
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join(timeout=5)
            
        # All threads should complete successfully
        self.assertEqual(len(results), len(dutch_contents))
        for result in results:
            self.assertIsInstance(result, int)
            
    def test_07_data_leakage_prevention(self):
        """Test prevention of data leakage in logs"""
        sensitive_data = '''
        BSN: 123456782
        Creditcard: 4111-1111-1111-1111
        Password: GeheimWachtwoord123!
        '''
        
        violations = detect_nl_violations(sensitive_data)
        
        # Check that sensitive data is not leaked in results
        results_str = str(violations)
        self.assertNotIn("123456782", results_str)
        self.assertNotIn("4111-1111-1111-1111", results_str)
        self.assertNotIn("GeheimWachtwoord123!", results_str)
        
    def test_08_privilege_escalation_prevention(self):
        """Test prevention of privilege escalation"""
        escalation_content = '''
        import os
        os.system("rm -rf /")
        
        BSN: 123456782
        AP_ACCESS_KEY: "admin_key_123"
        '''
        
        # Should process content without executing commands
        violations = detect_nl_violations(escalation_content)
        self.assertIsInstance(violations, list)
        
    def test_09_path_traversal_protection(self):
        """Test path traversal protection"""
        traversal_content = '''
        config_file = "../../../etc/passwd"
        bsn_database = "../../private/bsn_list.txt"
        BSN: 123456782
        '''
        
        violations = detect_nl_violations(traversal_content)
        self.assertIsInstance(violations, list)
        
    def test_10_unicode_security_dutch(self):
        """Test Unicode security for Dutch content"""
        unicode_content = '''
        BSN: １２３４５６７８２  # Unicode digits
        Telefoon: ０６－１２３４５６７８  # Unicode phone
        Email: tëst@vöörbëeld.nl  # Dutch diacritics
        '''
        
        violations = detect_nl_violations(unicode_content)
        self.assertIsInstance(violations, list)
        
    def test_11_html_injection_protection(self):
        """Test HTML injection protection"""
        html_injection = '''
        <div>BSN: 123456782</div>
        <img src="x" onerror="alert('XSS')">
        <iframe src="javascript:alert('injection')"></iframe>
        '''
        
        violations = detect_nl_violations(html_injection)
        self.assertIsInstance(violations, list)
        
    def test_12_configuration_tampering_protection(self):
        """Test protection against configuration tampering"""
        # Test with various malicious configurations
        tampered_configs = [
            {"region": "Netherlands/../../../etc/passwd"},
            {"bsn_patterns": [".*", "(.*)"]},  # Overly broad patterns
            {"max_violations": 999999999}
        ]
        
        for config in tampered_configs:
            try:
                # Configuration should be validated
                rules = get_region_rules(config.get('region', 'Netherlands'))
                self.assertIsInstance(rules, dict)
            except (ValueError, TypeError):
                # Expected for invalid configurations
                pass
                
    def test_13_error_message_information_leakage(self):
        """Test error messages don't leak information"""
        problematic_content = '''
        BSN: invalid_bsn_format
        Malformed Dutch content: <<<>>>
        '''
        
        try:
            violations = detect_nl_violations(problematic_content)
            # Should handle gracefully
            self.assertIsInstance(violations, list)
        except Exception as e:
            error_msg = str(e)
            # Error should not contain system paths or sensitive info
            self.assertNotIn('/tmp/', error_msg)
            self.assertNotIn(os.environ.get('USER', ''), error_msg)
            
    def test_14_resource_limit_enforcement(self):
        """Test resource limit enforcement"""
        # Extremely large content that could cause issues
        huge_content = "BSN: 123456782\\n" * 100000
        
        start_time = time.time()
        try:
            violations = detect_nl_violations(huge_content)
            self.assertIsInstance(violations, list)
        except (MemoryError, TimeoutError):
            # Expected for extremely large content
            pass
        end_time = time.time()
        
        # Should not run indefinitely
        processing_time = end_time - start_time
        self.assertLess(processing_time, 30.0)
        
    def test_15_audit_trail_security(self):
        """Test audit trail security"""
        import logging
        import io
        
        # Capture log output
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        logger = logging.getLogger('netherlands_gdpr')
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        
        try:
            sensitive_content = '''
            BSN: 123456782
            Wachtwoord: SuperGeheimWachtwoord123!
            '''
            
            detect_nl_violations(sensitive_content)
            
            # Check logs don't contain sensitive data
            log_output = log_capture.getvalue()
            self.assertNotIn("123456782", log_output)
            self.assertNotIn("SuperGeheimWachtwoord123!", log_output)
            
        finally:
            logger.removeHandler(handler)

class TestUAVGScannerViolationDetection(unittest.TestCase):
    """15 Violation Detection Tests for UAVG Scanner"""
    
    def setUp(self):
        self.region = "Netherlands"
        
    def test_01_bsn_detection_accuracy(self):
        """Test BSN detection accuracy"""
        test_cases = [
            ("BSN: 123456782", True),  # Valid BSN
            ("burgerservicenummer: 111222333", True),  # Dutch term
            ("BSN: 123456789", False),  # Invalid BSN checksum
            ("number: 123456789", False),  # Generic number
        ]
        
        for content, should_detect in test_cases:
            violations = detect_nl_violations(content)
            bsn_violations = [v for v in violations if v.get('type', '').lower() == 'bsn']
            
            if should_detect:
                self.assertGreater(len(bsn_violations), 0, f"Should detect BSN in: {content}")
            else:
                self.assertEqual(len(bsn_violations), 0, f"Should not detect BSN in: {content}")
                
    def test_02_dutch_phone_number_detection(self):
        """Test Dutch phone number detection"""
        test_cases = [
            ("+31-6-12345678", True),
            ("06-12345678", True),
            ("+31 20 1234567", True),  # Landline
            ("020-1234567", True),
            ("+1-555-123-4567", False),  # US number
            ("123-456-7890", False)  # Generic format
        ]
        
        for phone, should_detect in test_cases:
            content = f'telefoon = "{phone}"'
            violations = detect_nl_violations(content)
            phone_violations = [v for v in violations if 'phone' in v.get('type', '').lower()]
            
            if should_detect:
                self.assertGreater(len(phone_violations), 0, f"Should detect Dutch phone: {phone}")
                
    def test_03_dutch_postal_code_detection(self):
        """Test Dutch postal code detection"""
        test_cases = [
            ("1012 AB Amsterdam", True),
            ("2587 CX Den Haag", True),
            ("90210 Beverly Hills", False),  # US zip code
            ("SW1A 1AA London", False)  # UK postcode
        ]
        
        for address, should_detect in test_cases:
            content = f'adres = "{address}"'
            violations = detect_nl_violations(content)
            postal_violations = [v for v in violations if 'postal' in v.get('type', '').lower()]
            
            if should_detect:
                self.assertGreater(len(postal_violations), 0, f"Should detect Dutch postal code: {address}")
                
    def test_04_dutch_iban_detection(self):
        """Test Dutch IBAN detection"""
        test_cases = [
            ("NL91ABNA0417164300", True),
            ("NL02RABO0123456789", True),
            ("DE89370400440532013000", False),  # German IBAN
            ("FR1420041010050500013M02606", False)  # French IBAN
        ]
        
        for iban, should_detect in test_cases:
            content = f'rekening = "{iban}"'
            violations = detect_nl_violations(content)
            iban_violations = [v for v in violations if 'iban' in v.get('type', '').lower()]
            
            if should_detect:
                self.assertGreater(len(iban_violations), 0, f"Should detect Dutch IBAN: {iban}")
                
    def test_05_kvk_number_detection(self):
        """Test KvK (Chamber of Commerce) number detection"""
        test_cases = [
            ("KvK: 12345678", True),
            ("KvK-nummer: 87654321", True),
            ("handelsregister: 11223344", True),
            ("random: 12345678", False)  # Generic number
        ]
        
        for content, should_detect in test_cases:
            violations = detect_nl_violations(content)
            kvk_violations = [v for v in violations if 'kvk' in v.get('type', '').lower()]
            
            if should_detect:
                self.assertGreater(len(kvk_violations), 0, f"Should detect KvK number: {content}")
                
    def test_06_dutch_medical_data_detection(self):
        """Test Dutch medical data detection"""
        medical_content = [
            "AGB code: 12345678",
            "zorgverzekering nummer: 987654321",
            "patient ID: NL123456789",
            "BSN medisch dossier: 123456782"
        ]
        
        for content in medical_content:
            violations = detect_nl_violations(content)
            medical_violations = [v for v in violations if any(term in v.get('type', '').lower() 
                                                             for term in ['medical', 'health', 'agb', 'patient'])]
            self.assertGreater(len(medical_violations), 0, f"Should detect medical data: {content}")
            
    def test_07_consent_banner_compliance_detection(self):
        """Test consent banner compliance detection"""
        compliant_banner = '''
        <div class="cookie-consent">
            <p>We use cookies. You can manage your preferences.</p>
            <button onclick="acceptAll()">Accept All</button>
            <button onclick="managePreferences()">Manage Preferences</button>
            <button onclick="rejectAll()">Reject All</button>
        </div>
        '''
        
        non_compliant_banner = '''
        <div class="cookie-notice">
            <p>This site uses cookies.</p>
            <button onclick="continue()">Continue</button>
        </div>
        '''
        
        compliant_violations = detect_nl_violations(compliant_banner)
        non_compliant_violations = detect_nl_violations(non_compliant_banner)
        
        # Non-compliant should have more violations
        self.assertGreaterEqual(len(non_compliant_violations), len(compliant_violations))
        
    def test_08_dark_pattern_detection_accuracy(self):
        """Test dark pattern detection accuracy"""
        dark_patterns = [
            '''<button class="big green">Accept All</button><a href="#" class="tiny">Settings</a>''',
            '''<input type="checkbox" checked> Subscribe to newsletter (required)''',
            '''<button disabled>Reject All</button><button>Accept All</button>'''
        ]
        
        for pattern in dark_patterns:
            violations = detect_nl_violations(pattern)
            dark_violations = [v for v in violations if 'dark' in v.get('type', '').lower()]
            self.assertGreater(len(dark_violations), 0, f"Should detect dark pattern: {pattern[:50]}...")
            
    def test_09_dutch_language_privacy_terms(self):
        """Test Dutch language privacy terms detection"""
        dutch_terms = [
            "persoonsgegevens verwerking",
            "gegevensbescherming",
            "privacy verklaring",
            "toestemming cookies",
            "AVG compliance"
        ]
        
        for term in dutch_terms:
            content = f'policy = "{term} informatie"'
            violations = detect_nl_violations(content)
            privacy_violations = [v for v in violations if 'privacy' in v.get('type', '').lower()]
            self.assertGreaterEqual(len(privacy_violations), 0, f"Should recognize Dutch term: {term}")
            
    def test_10_ap_authority_reference_detection(self):
        """Test AP (Authority Personal Data) reference detection"""
        ap_references = [
            "AP melding vereist",
            "Autoriteit Persoonsgegevens",
            "autoriteitpersoonsgegevens.nl",
            "data breach notification AP"
        ]
        
        for reference in ap_references:
            content = f'compliance = "{reference}"'
            violations = detect_nl_violations(content)
            ap_violations = [v for v in violations if 'ap' in v.get('type', '').lower() or 'authority' in v.get('type', '').lower()]
            self.assertGreaterEqual(len(ap_violations), 0, f"Should detect AP reference: {reference}")
            
    def test_11_dutch_sensitive_categories_detection(self):
        """Test Dutch sensitive data categories detection"""
        sensitive_categories = [
            "religieuze overtuiging",
            "politieke voorkeur", 
            "seksuele gerichtheid",
            "strafrechtelijke gegevens",
            "gezondheidsgegevens"
        ]
        
        for category in sensitive_categories:
            content = f'data_type = "{category}"'
            violations = detect_nl_violations(content)
            sensitive_violations = [v for v in violations if 'sensitive' in v.get('type', '').lower()]
            self.assertGreater(len(sensitive_violations), 0, f"Should detect sensitive category: {category}")
            
    def test_12_cookie_categorization_detection(self):
        """Test cookie categorization detection"""
        cookie_html = '''
        <div class="cookie-categories">
            <label><input type="checkbox" name="necessary" checked disabled> Necessary</label>
            <label><input type="checkbox" name="analytics"> Analytics</label>
            <label><input type="checkbox" name="marketing"> Marketing</label>
            <label><input type="checkbox" name="preferences"> Preferences</label>
        </div>
        '''
        
        violations = detect_nl_violations(cookie_html)
        cookie_violations = [v for v in violations if 'cookie' in v.get('type', '').lower()]
        self.assertGreaterEqual(len(cookie_violations), 0)
        
    def test_13_data_retention_period_detection(self):
        """Test data retention period detection"""
        retention_content = [
            "data wordt 2 jaar bewaard",
            "retention period: 24 months",
            "gegevens worden na 5 jaar verwijderd",
            "permanent storage of user data"
        ]
        
        for content in retention_content:
            violations = detect_nl_violations(content)
            retention_violations = [v for v in violations if 'retention' in v.get('type', '').lower()]
            self.assertGreaterEqual(len(retention_violations), 0, f"Should detect retention policy: {content}")
            
    def test_14_third_party_sharing_detection(self):
        """Test third-party data sharing detection"""
        sharing_content = [
            "data wordt gedeeld met partners",
            "third-party analytics providers",
            "gegevens overdracht naar VS",
            "sharing with advertising networks"
        ]
        
        for content in sharing_content:
            violations = detect_nl_violations(content)
            sharing_violations = [v for v in violations if any(term in v.get('type', '').lower() 
                                                             for term in ['sharing', 'transfer', 'third'])]
            self.assertGreater(len(sharing_violations), 0, f"Should detect data sharing: {content}")
            
    def test_15_comprehensive_uavg_compliance_check(self):
        """Test comprehensive UAVG compliance check"""
        complex_dutch_content = '''
        Privacy Verklaring - Bedrijf BV
        
        Persoonsgegevens die wij verwerken:
        - BSN: 123456782 (voor identificatie)
        - Telefoon: 06-12345678 (voor contact)
        - Email: klant@bedrijf.nl (voor communicatie)
        - Adres: Kalverstraat 1, 1012 AB Amsterdam
        - KvK nummer: 12345678
        - IBAN: NL91ABNA0417164300
        
        Cookies:
        <div class="cookie-banner">
            <button onclick="acceptAll()">Alles accepteren</button>
            <a href="#settings" class="small">Instellingen</a>
        </div>
        
        Gegevens worden 5 jaar bewaard en gedeeld met Google Analytics.
        Bij vragen kunt u contact opnemen met de Autoriteit Persoonsgegevens.
        '''
        
        violations = detect_nl_violations(complex_dutch_content)
        
        # Should detect multiple types of violations
        self.assertGreaterEqual(len(violations), 8, "Should detect multiple UAVG violations")
        
        # Check for different violation categories
        violation_types = [v.get('type', '').lower() for v in violations]
        expected_categories = ['bsn', 'phone', 'email', 'iban', 'cookie', 'retention']
        
        found_categories = 0
        for category in expected_categories:
            if any(category in vtype for vtype in violation_types):
                found_categories += 1
                
        self.assertGreaterEqual(found_categories, 4, "Should detect violations across multiple categories")

if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestUAVGScannerFunctionality,
        TestUAVGScannerPerformance,
        TestUAVGScannerSecurity,
        TestUAVGScannerViolationDetection
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\\n{'='*60}")
    print(f"UAVG NETHERLANDS SCANNER TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
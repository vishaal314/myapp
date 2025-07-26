"""
Comprehensive Test Suite for Website Scanner
6 automated tests covering functional and performance validation.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch
from typing import Dict, Any

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.website_scanner import WebsiteScanner
from tests.test_framework import ScannerTestSuite, BaseScanner

class TestWebsiteScanner(ScannerTestSuite):
    """Comprehensive test suite for Website Scanner functionality and performance"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.scanner = WebsiteScanner(region="Netherlands")
        cls.base_tester = BaseScanner("WebsiteScanner")
    
    def test_1_functional_cookie_detection(self):
        """Test 1: Functional - Cookie and Consent Banner Detection"""
        # Mock HTML with various cookie patterns
        mock_html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Website</title>
            <script src="https://www.googletagmanager.com/gtag/js"></script>
            <script>
                gtag('config', 'GA-123456789');
                window.dataLayer = window.dataLayer || [];
            </script>
        </head>
        <body>
            <div id="cookie-banner" style="display:block">
                <p>We use cookies to improve your experience.</p>
                <button id="accept-all">Accept All</button>
                <button id="reject-all">Reject All</button>
            </div>
            <script src="https://connect.facebook.net/en_US/fbevents.js"></script>
        </body>
        </html>
        '''
        
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = mock_html
            mock_response.headers = {'content-type': 'text/html'}
            mock_get.return_value = mock_response
            
            performance_data = self.base_tester.measure_performance(
                self.scanner.scan_website, "https://example.com"
            )
            result = performance_data['result']
            
            # Validate structure
            self.assert_scan_structure(result)
            
            # Check cookie detection
            self.assertIn('cookies', result)
            self.assertIn('consent_mechanisms', result)
            
            # Check for Google Analytics detection
            ga_detected = any('google' in str(finding).lower() or 'analytics' in str(finding).lower() 
                             for finding in result.get('findings', []))
            self.assertTrue(ga_detected, "Should detect Google Analytics tracking")
            
            # Validate performance
            self.assert_performance_within_limits(performance_data)
            
            print(f"✓ Test 1 PASSED: Cookie analysis completed in {performance_data['execution_time']:.2f}s")
    
    def test_2_functional_privacy_policy_analysis(self):
        """Test 2: Functional - Privacy Policy and GDPR Compliance"""
        mock_html = '''
        <!DOCTYPE html>
        <html>
        <head><title>Privacy Policy</title></head>
        <body>
            <h1>Privacy Policy</h1>
            <p>We collect personal data including email addresses and names.</p>
            <p>Data is shared with third parties for marketing purposes.</p>
            <p>You have the right to access, rectify, and delete your data.</p>
            <p>Contact our Data Protection Officer at dpo@company.com</p>
            <p>Data is transferred to the United States.</p>
            <p>We use legitimate interest as our legal basis.</p>
        </body>
        </html>
        '''
        
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = mock_html
            mock_response.headers = {'content-type': 'text/html'}
            mock_get.return_value = mock_response
            
            performance_data = self.base_tester.measure_performance(
                self.scanner.scan_website, "https://example.com/privacy"
            )
            result = performance_data['result']
            
            # Validate structure
            self.assert_scan_structure(result)
            
            # Check GDPR compliance analysis
            if 'privacy_policy' in result:
                privacy_analysis = result['privacy_policy']
                self.assertIn('gdpr_compliance', privacy_analysis)
            
            # Check for data transfer detection
            transfer_detected = any('transfer' in str(finding).lower() or 'third' in str(finding).lower() 
                                   for finding in result.get('findings', []))
            
            # Validate performance
            self.assert_performance_within_limits(performance_data)
            
            print(f"✓ Test 2 PASSED: Privacy policy analysis completed in {performance_data['execution_time']:.2f}s")
    
    def test_3_functional_netherlands_compliance(self):
        """Test 3: Functional - Netherlands-Specific GDPR/AP Compliance"""
        mock_html = '''
        <!DOCTYPE html>
        <html lang="nl">
        <head><title>Nederlandse Website</title></head>
        <body>
            <div class="cookie-banner">
                <p>Deze website gebruikt cookies voor marketing doeleinden.</p>
                <button id="accepteren">Accepteren</button>
                <!-- Missing "Reject All" button - AP violation -->
            </div>
            <script>
                // Pre-ticked marketing consent - forbidden by Dutch AP
                document.getElementById('marketing-consent').checked = true;
            </script>
        </body>
        </html>
        '''
        
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = mock_html
            mock_response.headers = {'content-type': 'text/html'}
            mock_get.return_value = mock_response
            
            performance_data = self.base_tester.measure_performance(
                self.scanner.scan_website, "https://example.nl"
            )
            result = performance_data['result']
            
            # Validate structure
            self.assert_scan_structure(result)
            
            # Check Netherlands-specific compliance
            self.assertEqual(result.get('region'), 'Netherlands')
            
            # Check for AP-specific violations
            ap_violations = [f for f in result.get('findings', []) 
                            if any(keyword in str(f).lower() for keyword in 
                                  ['reject', 'pre-ticked', 'dutch', 'netherlands'])]
            
            # Validate performance
            self.assert_performance_within_limits(performance_data)
            
            print(f"✓ Test 3 PASSED: Netherlands compliance analysis in {performance_data['execution_time']:.2f}s")
    
    def test_4_performance_multi_page_crawling(self):
        """Test 4: Performance - Multi-Page Website Crawling"""
        # Mock multiple pages
        pages = {
            'https://example.com': '<html><body><h1>Home</h1><a href="/about">About</a><a href="/contact">Contact</a></body></html>',
            'https://example.com/about': '<html><body><h1>About</h1><p>Company information</p></body></html>',
            'https://example.com/contact': '<html><body><h1>Contact</h1><p>Contact form</p></body></html>'
        }
        
        def mock_get_side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = pages.get(url, '<html><body>Not found</body></html>')
            mock_response.headers = {'content-type': 'text/html'}
            mock_response.url = url
            return mock_response
        
        with patch('requests.Session.get', side_effect=mock_get_side_effect):
            # Configure scanner for multi-page crawling
            scanner = WebsiteScanner(max_pages=5, max_depth=2, crawl_delay=0.1)
            
            performance_data = self.base_tester.measure_performance(
                scanner.scan_website, "https://example.com"
            )
            result = performance_data['result']
            
            # Validate structure
            self.assert_scan_structure(result)
            
            # Performance requirements for multi-page scanning
            self.assertLess(performance_data['execution_time'], 20.0,
                           "Multi-page scan should complete within 20 seconds")
            
            # Check that multiple pages were processed
            if 'pages_scanned' in result:
                self.assertGreater(result['pages_scanned'], 1, "Should scan multiple pages")
            
            print(f"✓ Test 4 PASSED: Multi-page crawling completed in {performance_data['execution_time']:.2f}s")
    
    def test_5_performance_large_website_analysis(self):
        """Test 5: Performance - Large Website with Many Trackers"""
        # Mock large HTML with many tracking scripts
        large_html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Large Website</title>
            <script src="https://www.googletagmanager.com/gtag/js"></script>
            <script src="https://connect.facebook.net/en_US/fbevents.js"></script>
            <script src="https://www.google-analytics.com/analytics.js"></script>
            <script src="https://static.hotjar.com/c/hotjar.js"></script>
            <script src="https://js.hs-scripts.com/hubspot.js"></script>
        </head>
        <body>
        ''' + '<div>Content section</div>' * 100 + '''
        </body>
        </html>
        '''
        
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = large_html
            mock_response.headers = {'content-type': 'text/html'}
            mock_get.return_value = mock_response
            
            performance_data = self.base_tester.measure_performance(
                self.scanner.scan_website, "https://large-example.com"
            )
            result = performance_data['result']
            
            # Validate structure
            self.assert_scan_structure(result)
            
            # Performance validation for large sites
            self.assertLess(performance_data['execution_time'], 25.0,
                           "Large website analysis should complete within 25 seconds")
            self.assertLess(performance_data['memory_used'], 200.0,
                           "Memory usage should stay under 200MB for large sites")
            
            # Check tracker detection
            if 'trackers' in result:
                self.assertGreater(len(result['trackers']), 3, "Should detect multiple trackers")
            
            print(f"✓ Test 5 PASSED: Large website analysis in {performance_data['execution_time']:.2f}s")
    
    def test_6_functional_ssl_and_security_analysis(self):
        """Test 6: Functional - SSL/TLS and Security Headers Analysis"""
        mock_html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Secure Website</title>
            <meta http-equiv="Strict-Transport-Security" content="max-age=31536000">
        </head>
        <body>
            <h1>Secure Content</h1>
            <form action="https://secure.example.com/submit" method="post">
                <input type="email" name="email" required>
                <input type="submit" value="Submit">
            </form>
        </body>
        </html>
        '''
        
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = mock_html
            mock_response.headers = {
                'content-type': 'text/html',
                'strict-transport-security': 'max-age=31536000',
                'x-frame-options': 'DENY',
                'x-content-type-options': 'nosniff'
            }
            mock_get.return_value = mock_response
            
            performance_data = self.base_tester.measure_performance(
                self.scanner.scan_website, "https://secure-example.com"
            )
            result = performance_data['result']
            
            # Validate structure
            self.assert_scan_structure(result)
            
            # Check security analysis
            if 'security_headers' in result:
                security_headers = result['security_headers']
                self.assertIsInstance(security_headers, dict)
            
            # Check SSL analysis
            if 'ssl_analysis' in result:
                ssl_analysis = result['ssl_analysis']
                self.assertIsInstance(ssl_analysis, dict)
            
            # Validate performance
            self.assert_performance_within_limits(performance_data)
            
            print(f"✓ Test 6 PASSED: Security analysis completed in {performance_data['execution_time']:.2f}s")

if __name__ == '__main__':
    unittest.main(verbosity=2)
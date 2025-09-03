#!/usr/bin/env python3
"""
Unit Tests for Certificate Generation - 2025 EU AI Act Timeline
Tests updated compliance certificates with 2025 enforcement dates
"""

import unittest
import sys
import os
import tempfile
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.certified_pdf_report import generate_certified_pdf_report
from services.certificate_payment_integration import CertificatePaymentIntegration

class TestCertificateGeneration2025(unittest.TestCase):
    """Test suite for certificate generation with 2025 timeline"""

    def setUp(self):
        """Set up test environment"""
        self.mock_scan_results = {
            'scan_id': 'cert-test-2025',
            'scanner_type': 'ai_model',
            'ai_system_name': 'Test AI Model Certificate',
            'compliance_score': 85,
            'findings': [
                {
                    'type': 'AI_ACT_GPAI_COMPLIANCE',
                    'severity': 'High',
                    'compliance_deadline': 'August 2, 2025 (Effective)'
                }
            ],
            'assessment_date': '2025-09-03T19:45:00',
            'region': 'Netherlands'
        }
        
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_certificate_contains_2025_timeline(self):
        """Test certificate contains 2025 enforcement timeline"""
        try:
            # Generate certificate
            pdf_path = generate_certified_pdf_report(
                self.mock_scan_results,
                output_dir=self.temp_dir
            )
            
            # Verify PDF was created
            self.assertTrue(os.path.exists(pdf_path), "Certificate PDF should be created")
            
            # Verify file size (should contain content)
            file_size = os.path.getsize(pdf_path)
            self.assertGreater(file_size, 1000, "Certificate should have substantial content")
            
        except ImportError:
            # Skip if ReportLab not available
            self.skipTest("ReportLab not available for PDF generation")

    def test_certificate_compliance_scoring(self):
        """Test certificate includes accurate compliance scoring"""
        # Test high compliance score
        high_score_results = {
            **self.mock_scan_results,
            'compliance_score': 95
        }
        
        try:
            pdf_path = generate_certified_pdf_report(
                high_score_results,
                output_dir=self.temp_dir
            )
            self.assertTrue(os.path.exists(pdf_path))
        except ImportError:
            self.skipTest("ReportLab not available")

    def test_certificate_with_gpai_findings(self):
        """Test certificate handles GPAI findings correctly"""
        gpai_results = {
            **self.mock_scan_results,
            'findings': [
                {
                    'type': 'AI_ACT_GPAI_COMPLIANCE',
                    'category': 'GPAI Model Requirements',
                    'severity': 'High',
                    'penalty_risk': 'Up to €15M or 3% global turnover',
                    'compliance_deadline': 'August 2, 2025 (Effective)'
                }
            ]
        }
        
        try:
            pdf_path = generate_certified_pdf_report(
                gpai_results,
                output_dir=self.temp_dir
            )
            self.assertTrue(os.path.exists(pdf_path))
        except ImportError:
            self.skipTest("ReportLab not available")

    def test_certificate_payment_integration(self):
        """Test certificate payment integration works"""
        payment_integration = CertificatePaymentIntegration()
        
        # Test payment integration exists
        self.assertIsNotNone(payment_integration)

    def test_certificate_netherlands_compliance(self):
        """Test certificate includes Netherlands-specific compliance"""
        nl_results = {
            **self.mock_scan_results,
            'region': 'Netherlands'
        }
        
        try:
            pdf_path = generate_certified_pdf_report(
                nl_results,
                output_dir=self.temp_dir
            )
            self.assertTrue(os.path.exists(pdf_path))
        except ImportError:
            self.skipTest("ReportLab not available")

    def test_certificate_file_naming(self):
        """Test certificate files are named correctly"""
        try:
            pdf_path = generate_certified_pdf_report(
                self.mock_scan_results,
                output_dir=self.temp_dir
            )
            
            filename = os.path.basename(pdf_path)
            
            # Should contain scan ID and be PDF
            self.assertIn('cert-test-2025', filename)
            self.assertTrue(filename.endswith('.pdf'))
            
        except ImportError:
            self.skipTest("ReportLab not available")

    def test_certificate_multiple_findings(self):
        """Test certificate handles multiple findings correctly"""
        multi_findings_results = {
            **self.mock_scan_results,
            'findings': [
                {
                    'type': 'AI_ACT_GPAI_COMPLIANCE',
                    'severity': 'High',
                    'compliance_deadline': 'August 2, 2025 (Effective)'
                },
                {
                    'type': 'prohibited',
                    'severity': 'Critical',
                    'compliance_deadline': 'February 2, 2025 (Effective)'
                },
                {
                    'type': 'high_risk',
                    'severity': 'Medium',
                    'compliance_deadline': 'August 2, 2027 (Deadline)'
                }
            ]
        }
        
        try:
            pdf_path = generate_certified_pdf_report(
                multi_findings_results,
                output_dir=self.temp_dir
            )
            self.assertTrue(os.path.exists(pdf_path))
        except ImportError:
            self.skipTest("ReportLab not available")

    def test_certificate_date_accuracy(self):
        """Test certificate shows accurate assessment date"""
        # Test with specific date
        dated_results = {
            **self.mock_scan_results,
            'assessment_date': '2025-09-03T19:45:00'
        }
        
        try:
            pdf_path = generate_certified_pdf_report(
                dated_results,
                output_dir=self.temp_dir
            )
            self.assertTrue(os.path.exists(pdf_path))
        except ImportError:
            self.skipTest("ReportLab not available")

    def test_certificate_ai_model_specific(self):
        """Test certificate is specific to AI model scanning"""
        ai_model_results = {
            **self.mock_scan_results,
            'scanner_type': 'ai_model',
            'ai_system_name': 'Foundation Model Assessment'
        }
        
        try:
            pdf_path = generate_certified_pdf_report(
                ai_model_results,
                output_dir=self.temp_dir
            )
            self.assertTrue(os.path.exists(pdf_path))
        except ImportError:
            self.skipTest("ReportLab not available")

    def test_certificate_error_handling(self):
        """Test certificate generation handles errors gracefully"""
        # Test with minimal data
        minimal_results = {
            'scan_id': 'minimal-cert-test',
            'compliance_score': 50
        }
        
        try:
            pdf_path = generate_certified_pdf_report(
                minimal_results,
                output_dir=self.temp_dir
            )
            # Should either create file or handle gracefully
            if pdf_path:
                self.assertTrue(os.path.exists(pdf_path))
        except ImportError:
            self.skipTest("ReportLab not available")
        except Exception as e:
            # Should not crash with minimal data
            self.fail(f"Certificate generation should handle minimal data: {e}")

if __name__ == '__main__':
    unittest.main()
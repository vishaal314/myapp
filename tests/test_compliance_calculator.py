"""
Unit Tests for Compliance Calculator - Verify accuracy across edge cases
and regional configurations for production deployment.
"""

import unittest
from unittest.mock import patch
from typing import List, Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.compliance_calculator import (
    ComplianceCalculator, 
    ComplianceConfig, 
    calculate_compliance_score,
    get_compliance_status,
    get_risk_level,
    REGIONAL_CONFIGS
)

class TestComplianceCalculator(unittest.TestCase):
    """Test suite for compliance score calculation accuracy."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = ComplianceCalculator()
        
    def test_perfect_score_no_findings(self):
        """Test perfect score with no findings."""
        findings = []
        result = self.calculator.calculate_compliance_score(findings)
        
        self.assertEqual(result.score, 100.0)
        self.assertEqual(result.total_findings, 0)
        self.assertEqual(result.critical_findings, 0)
        
    def test_critical_findings_penalty(self):
        """Test critical findings apply correct penalty."""
        findings = [
            {'severity': 'Critical', 'type': 'API Key Exposure'},
            {'severity': 'Critical', 'type': 'Database Credentials'}
        ]
        result = self.calculator.calculate_compliance_score(findings)
        
        # 2 critical findings × 25% penalty = 50% penalty
        expected_score = 100 - (2 * 25)
        self.assertEqual(result.score, expected_score)
        self.assertEqual(result.critical_findings, 2)
        
    def test_high_findings_penalty(self):
        """Test high findings apply correct penalty."""
        findings = [
            {'severity': 'High', 'type': 'PII Exposure'},
            {'privacy_risk': 'High', 'type': 'Cookie Tracking'}
        ]
        result = self.calculator.calculate_compliance_score(findings)
        
        # 2 high findings × 15% penalty = 30% penalty
        expected_score = 100 - (2 * 15)
        self.assertEqual(result.score, expected_score)
        self.assertEqual(result.high_findings, 2)
        
    def test_mixed_severity_calculation(self):
        """Test mixed severity findings calculation."""
        findings = [
            {'severity': 'Critical', 'type': 'Data Breach'},      # 25% penalty
            {'severity': 'High', 'type': 'PII Leak'},            # 15% penalty
            {'severity': 'High', 'type': 'Auth Bypass'},         # 15% penalty
            {'severity': 'Medium', 'type': 'XSS Vulnerability'}, # 5% penalty
            {'severity': 'Low', 'type': 'Missing Header'}        # 2% penalty
        ]
        result = self.calculator.calculate_compliance_score(findings)
        
        # Total penalty: 25 + 15 + 15 + 5 + 2 = 62%
        expected_score = 100 - 62
        self.assertEqual(result.score, expected_score)
        
    def test_privacy_risk_mapping(self):
        """Test privacy_risk High maps to high_findings for website scans."""
        findings = [
            {'privacy_risk': 'High', 'type': 'Cookie Consent'},
            {'privacy_risk': 'High', 'type': 'Tracker Detection'}
        ]
        result = self.calculator.calculate_compliance_score(findings)
        
        self.assertEqual(result.high_findings, 2)
        self.assertEqual(result.score, 100 - (2 * 15))  # 70%
        
    def test_uncategorized_findings_as_medium(self):
        """Test uncategorized findings treated as medium severity."""
        findings = [
            {'type': 'Unknown Issue 1'},  # No severity specified
            {'type': 'Unknown Issue 2'}   # No severity specified
        ]
        result = self.calculator.calculate_compliance_score(findings)
        
        # Should be treated as medium findings
        self.assertEqual(result.medium_findings, 2)
        self.assertEqual(result.score, 100 - (2 * 5))  # 90%
        
    def test_minimum_score_zero(self):
        """Test score never goes below 0%."""
        findings = []
        # Create enough critical findings to exceed 100% penalty
        for i in range(10):
            findings.append({'severity': 'Critical', 'type': f'Critical Issue {i}'})
            
        result = self.calculator.calculate_compliance_score(findings)
        
        # 10 critical × 25% = 250% penalty, but score should be 0% minimum
        self.assertEqual(result.score, 0.0)
        
    def test_compliance_status_mapping(self):
        """Test compliance status text mapping."""
        self.assertEqual(get_compliance_status(95), "Excellent")
        self.assertEqual(get_compliance_status(85), "Good")
        self.assertEqual(get_compliance_status(60), "Needs Improvement")
        self.assertEqual(get_compliance_status(30), "Critical")
        
    def test_risk_level_mapping(self):
        """Test risk level mapping."""
        self.assertEqual(get_risk_level(85), "Low")
        self.assertEqual(get_risk_level(60), "Medium")
        self.assertEqual(get_risk_level(30), "High")
        
    def test_regional_configuration(self):
        """Test different regional penalty configurations."""
        findings = [{'severity': 'Critical', 'type': 'Data Breach'}]
        
        # Test Netherlands config (default)
        netherlands_calc = ComplianceCalculator(REGIONAL_CONFIGS["Netherlands"])
        result_nl = netherlands_calc.calculate_compliance_score(findings)
        self.assertEqual(result_nl.score, 75.0)  # 100 - 25
        
        # Test Germany config (stricter)
        germany_calc = ComplianceCalculator(REGIONAL_CONFIGS["Germany"])
        result_de = germany_calc.calculate_compliance_score(findings)
        self.assertEqual(result_de.score, 70.0)  # 100 - 30
        
        # Test Enterprise config (strictest)
        enterprise_calc = ComplianceCalculator(REGIONAL_CONFIGS["Enterprise"])
        result_ent = enterprise_calc.calculate_compliance_score(findings)
        self.assertEqual(result_ent.score, 65.0)  # 100 - 35
        
    def test_caching_functionality(self):
        """Test compliance score caching works correctly."""
        findings = [
            {'severity': 'High', 'type': 'PII Exposure'},
            {'severity': 'Medium', 'type': 'Config Issue'}
        ]
        
        # First calculation
        result1 = self.calculator.calculate_compliance_score(findings, scan_id="test1")
        
        # Second calculation with same findings should use cache
        result2 = self.calculator.calculate_compliance_score(findings, scan_id="test2")
        
        self.assertEqual(result1.score, result2.score)
        self.assertEqual(result1.total_findings, result2.total_findings)
        
    def test_audit_trail_creation(self):
        """Test audit trail is properly maintained."""
        findings = [{'severity': 'High', 'type': 'Test Finding'}]
        
        initial_trail_length = len(self.calculator.get_audit_trail())
        
        result = self.calculator.calculate_compliance_score(
            findings, 
            scan_id="audit_test", 
            username="test_user"
        )
        
        trail = self.calculator.get_audit_trail()
        self.assertEqual(len(trail), initial_trail_length + 1)
        
        latest_entry = trail[-1]
        self.assertEqual(latest_entry.scan_id, "audit_test")
        self.assertEqual(latest_entry.username, "test_user")
        self.assertEqual(latest_entry.score, result.score)
        
    def test_edge_case_empty_severity(self):
        """Test handling of findings with empty/None severity."""
        findings = [
            {'severity': None, 'type': 'Null Severity'},
            {'severity': '', 'type': 'Empty Severity'},
            {'type': 'No Severity Field'}
        ]
        
        result = self.calculator.calculate_compliance_score(findings)
        
        # All should be treated as medium severity
        self.assertEqual(result.medium_findings, 3)
        self.assertEqual(result.score, 100 - (3 * 5))  # 85%
        
    def test_real_world_website_scan_scenario(self):
        """Test realistic website scan with mixed privacy risks."""
        findings = [
            {'privacy_risk': 'High', 'type': 'Cookie Banner Missing'},
            {'privacy_risk': 'High', 'type': 'Google Analytics Without Consent'},
            {'severity': 'High', 'type': 'Facebook Pixel Tracking'},
            {'severity': 'Medium', 'type': 'Missing Privacy Policy Link'},
            {'severity': 'Medium', 'type': 'Non-HTTPS Form'},
            {'severity': 'Low', 'type': 'Missing Alt Text'},
            {'type': 'Third-party Domain'}  # Uncategorized
        ]
        
        result = self.calculator.calculate_compliance_score(findings)
        
        # Expected: 3 high (45%) + 3 medium (15%) + 1 low (2%) = 62% penalty
        expected_score = 100 - 62
        self.assertEqual(result.score, expected_score)
        self.assertEqual(result.high_findings, 3)
        self.assertEqual(result.medium_findings, 3)
        self.assertEqual(result.low_findings, 1)

class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions for backward compatibility."""
    
    def test_calculate_compliance_score_function(self):
        """Test standalone calculate_compliance_score function."""
        findings = [{'severity': 'High', 'type': 'Test'}]
        
        score, result = calculate_compliance_score(findings, "test_scan", "test_user")
        
        self.assertEqual(score, 85.0)  # 100 - 15
        self.assertIsInstance(result.score, float)
        self.assertEqual(result.scan_id, "test_scan")
        self.assertEqual(result.username, "test_user")

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)